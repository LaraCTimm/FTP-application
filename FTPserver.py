import socket
import threading
import os
import sys
from pathlib2 import Path
import time
from stat import * 
import stat
import shutil
#from filemode_class import FileMode

from datetime import datetime

locIP = socket.gethostbyname(socket.gethostname())
locPort = 21
serverDirectory = os.path.abspath('./serverDirectory')
#---------------------------------------------------------------------------

class serverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.bind((locIP, locPort))

    def run(self):
        self.servSock.listen(5)
        while 1:
            clientTh = clientThread(self.servSock.accept())
            clientTh.setDaemon(1)
            clientTh.start()

    def closeSocket(self):
        self.servSock.close()

#---------------------------------------------------------------------------

class clientThread(threading.Thread):
    def __init__(self, (conn, addr)):
        threading.Thread.__init__(self)
        print 'Client connected...'
        self.connSock = conn            # socket for command messages
        self.connAddr = addr            # IP address of connected client
        self.baseDirectory = serverDirectory
        self.workingDirectory = '' #
        self.loggedIn = False
        self.username = ''
        self.passive = False #
        self.binaryFile = False #
        self.dataConnOpen = False

        self.dataPort = -1  # set in port and pasv
        self.dataAddress = '' #

        # file containing usernames and passwords of people registered on server 
        passwordFile = open("userdata.txt", 'r')
        self.userData = passwordFile.readlines()
        passwordFile.close()

    def run(self):
        self.connSock.send('220 Service ready for new user.\r\n')
        while 1:
            command = self.connSock.recv(256)
            if not command: 
                break
            else:
                print 'Request:', command
                try:
                    action = getattr(self, command[:4].strip().upper())
                    action(command)
                except Exception, err:
                    print 'Error:', err
                    if err[0][:3] == '500':
                        self.connSock.send('500 Syntax error, command unrecognized.\r\n')
                    elif err[0][:3] == '530':
                         self.connSock.send('530 Not logged in.\r\n')
                    elif err[0][:3] == '221':
                        self.connSock.send('221 Service closing control connection.\r\n')
                        self.connSock.close()
                        print 'Client disconnected...'
                        break
                    else:
                        do = 'stuff'


    # access control commands ---------------------------------------------------------------------------

    def USER(self, command):

        # check if user is already registered
        self.username = command[5:-2]
        print self.username
        self.userRow = -1

        if self.username != '':
            for i in range(0, len(self.userData)):
                index = self.userData[i].find(self.username)
                
                if index != -1:
                    self.userRow = i
                    break
                    
            if self.userRow > -1:
                self.baseDirectory = os.path.join(serverDirectory, self.username) 
                user_dir = Path(self.baseDirectory)     # base directory for specific client

                if user_dir.is_dir() == True:
                    self.connSock.send('331 User name okay, need password.\r\n')
                    return
                else:
                    self.username = ''
                    self.connSock.send('332 Need account for login. <directory not found>\r\n')
                    return
            else:
                self.connSock.send('332 Need account for login. <username not registered>\r\n')
                return
        else:
            self.connSock.send('332 Need account for login. <invalid username>\r\n')
            return

    def PASS(self, command):

        password = command[5:-2]
        if password != '' and password != ' ':
            if self.username != '':                  # must have entered username to enter password

                if self.userRow > -1:
                    storedPassword = self.userData[self.userRow][-(len(password)+1):-1] 

                    if storedPassword == password:
                        self.loggedIn = True
                        self.workingDirectory = self.baseDirectory
                        self.connSock.send('230 User logged in, proceed.\r\n')
                        return
                    else:
                        self.connSock.send('530 Not logged in. <password incorrect>\r\n')
                        return
                else:
                    self.connSock.send('332 Need account for login. <username not registered>\r\n')
                    return
            else:
                self.connSock.send('332 Need account for login. <username not registered>\r\n')
                return
        else:
            self.connSock.send('332 Need account for login. <invalid password>\r\n')

    def CWD(self, command):
        self.checkLoggedIn()

        newDirectory = os.path.join(self.workingDirectory, command[4:-2])

        if os.path.exists(newDirectory):
            self.workingDirectory = newDirectory
            self.connSock.send('250 Requested action okay. Working directory changed.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Directory does not exist.\r\n')     
    
    def CDUP(self, command):
        self.checkLoggedIn()

        highestDirectory = os.path.join(serverDirectory, self.username)
        if self.workingDirectory != highestDirectory:
            self.workingDirectory = os.path.dirname(self.workingDirectory)
            self.connSock.send('250 Requested action okay. Working directory changed.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Permission denied.\r\n')    
    
    def QUIT(self, command):
        # QUIT <CRLF>
        raise Exception('221 Service closing control connection.')

    def checkLoggedIn(self):
        if not self.loggedIn: 
            raise Exception('530 Not logged in.')

    # transfer parameter commands ----------------------------------------------------------------------

    def PORT(self, command): # ACTIVE MODE ###############
        self.checkLoggedIn()

        if self.passive:
            self.passive = False
            self.passiveSocket.close()

        rec = command[5:-2].split(',')
        self.dataAddress = '.'.join(rec[:4])
        byteU = int(rec[4])
        byteL = int(rec[5])
        self.dataPort = 256*byteU + byteL

        self.connSock.send('200 Port command successful.\r\n')

    def PASV(self, command): # PASSIVE MODE ##############
        
        self.passive = True

        self.passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passiveSocket.bind((locIP, 0))     # binds to local IP and available port
        ip, port = self.passiveSocket.getsockname()
        self.passiveSocket.listen(1)
        print 'Connection opened',ip,':',port

        byteU = int(port / 256)
        byteL = int(port % 256)
        
        connectionString = '(%s,%i,%i)' % (','.join(locIP.split('.')), byteU, byteL)
        self.connSock.send('227 Entering passive mode '+ connectionString +'.\r\n')

    def TYPE(self, command):

        fileType = command[5:-2]

        if fileType == 'I':
            self.binaryFile = True
            self.connSock.send('200 Switching to Binary mode.\r\n')
        elif fileType == 'A':
            self.binaryFile = False
            self.connSock.send('200 Switching to ASCII mode.\r\n')
        else:
            raise Exception('500 Syntax error, command unrecognized.')

    def STRU(self, command):
        # specifies file structure (file[D], record, page)
        structure = command[5:-2]

        if structure == 'F':
            self.connSock.send('200 Switching to File structure mode.\r\n')
        else:
            raise Exception('500 Syntax error, command unrecognized.')

    def MODE(self, command):
        # specify data transfer mode (stream[D], block, compressed)
        mode = command[5:-2]

        if mode == 'S':
            self.connSock.send('200 Switching to Stream transfer mode.\r\n')
        else:
            raise Exception('500 Syntax error, command unrecognized.')

    # service commands ---------------------------------------------------------------------------------

    def RETR(self, command):
        # transfer a copy file to client 
        self.checkLoggedIn()

        if self.dataConnOpen: 
            fileName = command[5:-2]
            filePath = os.path.join(self.workingDirectory, fileName)
            
            if os.path.isfile(filePath):
                requestedFile = None
                if self.binaryFile:
                    requestedFile = open(filePath,'rb')
                else:
                    requestedFile = open(filePath,'r')

                self.connSock.send('150 Opening data connection.\r\n')
                try:
                    self.open_dataSocket()

                    fileChunk = requestedFile.read(1024)

                    while fileChunk:
                        print 'Sending...'
                        self.dataSocket.send(fileChunk)
                        fileChunk = requestedFile.read(1024)
                
                except Exception, err:
                    self.connSock.send('451 Requested action aborted: local error in processing.\r\n')

                requestedFile.close()
                self.close_dataSocket()

                self.connSock.send('226 Closing data connection. Requested file action successful.\r\n')
            else:
                self.connSock.send('550 Requested action not taken. File unavailable.\r\n')
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def STOR(self, command):
        # accept data from data connection and store as file on server
        self.checkLoggedIn()
    
        if self.dataConnOpen:
            fileName = command[5:-2]
            filePath = os.path.join(self.workingDirectory, fileName)

            requestedFile = None
            if self.binaryFile:
                requestedFile = open(filePath, 'wb')
            else:
                requestedFile = open(filePath, 'w')
            
            self.connSock.send('150 File status okay; about to open data connection.\r\n')

            try:
                self.open_dataSocket()

                fileChunk = self.dataSocket.recv(1024)
                while (fileChunk):
                    print "Receiving..."
                    requestedFile.write(fileChunk)
                    fileChunk = self.dataSocket.recv(1024)

                requestedFile.close()
                self.close_dataSocket
                print "Done Receiving"
                self.connSock.send('226 Closing data connection. Requested file action successful.\r\n')
            
            except Exception, err:
                self.connSock.send('550 Requested action not taken. File transfer unsuccessful.\r\n')
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def open_dataSocket(self):
        self.dataConnOpen = True
        #----PASSIVE-------------------------------------------------------
        if self.passive:
            self.dataSocket, addr = self.passiveSocket.accept()
            print 'Data stream opened at address:', addr
        #----ACTIVE--------------------------------------------------------
        else:
            self.dataSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.dataSocket.connect((self.dataAddress,self.dataPort))   # params retreived from PORT command
            print 'Data stream opened at address: (\'%s\', %u)' % (self.dataAddress, self.dataPort)

    def close_dataSocket(self):
        self.dataConnOpen = False
        if self.passive:
            self.passiveSocket.close()
        self.dataSocket.close()
    
    def DELE(self, command):
        self.checkLoggedIn()

        filePath = os.path.join(self.workingDirectory, command[5:-2])
        if os.path.isfile(filePath):
            os.remove(filePath)
            self.connSock.send('250 Requested file action okay, file deleted.\r\n')
        elif os.path.isdir(filePath):
            self.connSock.send('550 Requested action not taken. To delete directory use RMD.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. File does not exist.\r\n')

    def PWD(self, command):
        self.checkLoggedIn()
        self.connSock.send('257 \"%s\" is the working directory.\r\n' % (self.workingDirectory[len(serverDirectory):]))

    def LIST(self, command):
        self.checkLoggedIn()

        if self.dataConnOpen:
            self.connSock.send('150 Opening data connection. Sending directory list.\r\n')    
            self.open_dataSocket()

            # print self.workingDirectory
            itemString = ''

            for item in os.listdir(self.workingDirectory):
                itemString += self.createItemString(os.path.join(self.workingDirectory,item))

            self.dataSocket.send(itemString)
            
            self.connSock.send('226 Closing data connection. Directory list sent.\r\n')
            self.close_dataSocket()
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def createItemString(self, itemPath):
        itemStat = os.stat(itemPath)
        permissionString = 'rwxrwxrwx'
        itemPermissions = ''
        directoryChar = ''

        for i in range(9):
            if (itemStat.st_mode>>(8-i)) & 1:
                itemPermissions += permissionString[i]
            else:
                itemPermissions += '-'

        if os.path.isdir(itemPath):
            directoryChar = 'd'
        else:
            directoryChar = '-'

        timestamp = time.strftime("%d %b %Y %H:%M" , time.localtime(itemStat[ST_MTIME]))

        itemString = directoryChar + itemPermissions + ' ' + str(itemStat[ST_INO]) + ' ' + \
                     str(itemStat[ST_UID]) + ' ' + str(itemStat[ST_GID]) + ' ' + \
                     str(itemStat[ST_SIZE]) + ' ' + timestamp + ' ' + os.path.basename(itemPath) + ' \r\n'
                     
    
        return itemString

    def MKD(self, command):
        self.checkLoggedIn()

        dirPath = os.path.join(self.workingDirectory, command[4:-2])
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            self.connSock.send('257 \"%s\\%s\" created.\r\n'\
                    % (self.workingDirectory[len(serverDirectory):],command[5:]))
        else:
            self.connSock.send('550 Requested action not taken. \"%s\\%s\" already exists.\r\n'\
                    % (self.workingDirectory[len(serverDirectory):],command[5:]) )
            
    def RMD(self, command):
        self.checkLoggedIn()
        if command[5:] != '':
            dirPath = os.path.join(self.workingDirectory, command[4:-2])
            if os.path.isdir(dirPath):
                shutil.rmtree(dirPath)
                self.connSock.send('250 Requested file action okay, directory deleted.\r\n')
            elif os.path.isfile(dirPath):
                self.connSock.send('550 Requested action not taken. To delete file use DELE\r\n')
            else:
                self.connSock.send('550 Requested action not taken. Directory does not exist.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Permission denied.\r\n')

    def NOOP(self, command):
        self.checkLoggedIn()
        self.connSock.send('200 Command okay.\r\n')

    def AUTH(self, command):
        self.connSock.send('530 Please log in with USER and PASS.\r\n')

#---------------------------------------------------------------------------
# MAIN

if __name__ == '__main__':
    FTPconnection = serverThread()
    FTPconnection.setDaemon(1)
    FTPconnection.start()
    print 'Listening on', locIP, ':', locPort
    raw_input('Press Enter to end...\n')
    FTPconnection.closeSocket()

# The following are the FTP commands:

# USER <SP> <username> <CRLF>
# PASS <SP> <password> <CRLF>
# ACCT <SP> <account-information> <CRLF>
# CWD  <SP> <pathname> <CRLF>
# CDUP <CRLF>
# SMNT <SP> <pathname> <CRLF>
# QUIT <CRLF>
# REIN <CRLF>
# PORT <SP> <host-port> <CRLF>
# PASV <CRLF>
# TYPE <SP> <type-code> <CRLF>
# STRU <SP> <structure-code> <CRLF>
# MODE <SP> <mode-code> <CRLF>
# RETR <SP> <pathname> <CRLF>
# STOR <SP> <pathname> <CRLF>
# STOU <CRLF>
# APPE <SP> <pathname> <CRLF>
# ALLO <SP> <decimal-integer>
#     [<SP> R <SP> <decimal-integer>] <CRLF>
# REST <SP> <marker> <CRLF>
# RNFR <SP> <pathname> <CRLF>
# RNTO <SP> <pathname> <CRLF>
# ABOR <CRLF>
# DELE <SP> <pathname> <CRLF>
# RMD  <SP> <pathname> <CRLF>
# MKD  <SP> <pathname> <CRLF>
# PWD  <CRLF>
# LIST [<SP> <pathname>] <CRLF>
# NLST [<SP> <pathname>] <CRLF>
# SITE <SP> <string> <CRLF>
# SYST <CRLF>
# STAT [<SP> <pathname>] <CRLF>
# HELP [<SP> <string>] <CRLF>
# NOOP <CRLF>

# <username> ::= <string>
# <password> ::= <string>
# <account-information> ::= <string>
# <string> ::= <char> | <char><string>
# <char> ::= any of the 128 ASCII characters except <CR> and
# <LF>
# <marker> ::= <pr-string>
# <pr-string> ::= <pr-char> | <pr-char><pr-string>
# <pr-char> ::= printable characters, any
#                 ASCII code 33 through 126
# <byte-size> ::= <number>
# <host-port> ::= <host-number>,<port-number>
# <host-number> ::= <number>,<number>,<number>,<number>
# <port-number> ::= <number>,<number>
# <number> ::= any decimal integer 1 through 255
# <form-code> ::= N | T | C
# <type-code> ::= A [<sp> <form-code>]
#                 | E [<sp> <form-code>]
#                 | I
#                 | L <sp> <byte-size>
# <structure-code> ::= F | R | P
# <mode-code> ::= S | B | C
# <pathname> ::= <string>
# <decimal-integer> ::= any decimal integer

# CDUP - Change to Parent Directory
# RMD - Remove Directory
# MKD - Make Directory
# PWD - Print Directory
#  LIST (LIST)
# NAME LIST (NLST) ######