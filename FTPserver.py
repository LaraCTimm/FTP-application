import socket
import threading
import os
import sys
from pathlib2 import Path
import time
from stat import * # ST_SIZE etc
import stat
#from utils import fileProperty
from filemode_class import FileMode
#from contextlib import closing


import hashlib
# mystring = input('Enter String to hash: ')
# # Assumes the default UTF-8
# hash_object = hashlib.md5(mystring.encode())
# print(hash_object.hexdigest())

locIP = socket.gethostbyname(socket.gethostname())
# print loc_ip
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
        self.connSock = conn            # socket for command messages
        self.connAddr = addr            # IP address of connected client
        self.baseDirectory = ''
        self.workingDirectory = '' #
        self.loggedIn = False
        self.username = ''

        self.dataPort = -1  # set in port and pasv
        self.dataAddr = '' #

        # file containing usernames and passwords of people registered on server 
        passwordFile = open("userdata.txt", 'r')
        self.userData = passwordFile.readlines()
        passwordFile.close()



        self.statClass = FileMode() #
        # self.userRow = -1   #
        self.passive = True #
        self.passivePort = None #
        self.binaryFile = False #

    def run(self):
        self.connSock.send('220 Service ready for new user.\r\n')
        while 1:
            command = self.connSock.recv(256)
            if not command: 
                break
            else:
                print 'Recieved: ', command
                try:
                    action = getattr(self, command[:4].strip().upper())
                    action(command)
                except Exception, err:
                    print 'Error: ', err
                    self.connSock.send('500 Syntax error, command unrecognized.\r\n')


    # access control commands ---------------------------------------
    def USER(self, command):
        # USER <SP> <username> <CRLF>
        
        # check if user is already registered
        self.username = command[5:]
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
        # PASS <SP> <password> <CRLF>

        password = command[5:]
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
        
    # def QUIT(self, command):
    #     # QUIT <CRLF>

    # # transfer parameter commands -----------------------------------
    def PORT(self, command): # ACTIVE MODE ###############

        if self.passive:
            self.passive = False
            ##### dataSock.close()

        rec = command[5:].split(',')
        self.dataAddr = '.'.join(rec[:4])
        upperByte = int(rec[4])
        lowerByte = int(rec[5])
        self.dataPort = 256*upperByte + lowerByte

        self.connSock.send('200 Command okay.\r\n')

        # import socket
        # s = socket.socket()
        # s.bind(("127.0.0.1", 20))              # server details (locIP, locDataPort)
        # s.connect(("321.12.131.432", 80))     # client details received from port

    def PASV(self, command): # PASSIVE MODE ###############
        # This command requests the server-DTP to "listen" on a data
        # port (which is not its default data port) and to wait for a
        # connection rather than initiate one upon receipt of a
        # transfer command.  The response to this command includes the
        # host and port address this server is listening on.
        self.passive = True

        

        self.passivePort = self.find_free_port()
        
        print 'Available port:', self.passivePort
        locIpChunks = locIP.split('.')
        portChunk1 = int(self.passivePort / 256)
        portChunk2 = self.passivePort % 256
        connectionString = '(%s,%s,%s,%s,%i,%i)' % (locIpChunks[0], locIpChunks[1], \
                locIpChunks[2], locIpChunks[3], portChunk1, portChunk2)
        self.connSock.send('227 Entering passive mode '+ connectionString + '.\r\n')

    def find_free_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        return sock.getsockname()[1]
        

    def TYPE(self, command):
    #     # TYPE <SP> <type-code> <CRLF>
    #     # specifies representation type (ascii[D], ebcdic, image, 
    #     #       local byte size)
        fileType = command[5:]

        if fileType == 'I':
            self.binaryFile = True
        elif fileType == 'A':
            self.binaryFile = False
        else:
            self.connSock.send('500 Syntax error, command unrecognized.\r\n')

    # def MODE(self, command):
    #     # MODE <SP> <mode-code> <CRLF>
    #     # specify data transfer mode (stream[D], block, compressed)

    # def STRU(self, command):
    #     # STRU <SP> <structure-code> <CRLF>
    #     # specifies file structure (file[D], record, page)

    # # service commands -----------------------------------------------

    def LIST(self, command):
    #if self.loggedIn:
        pathname = command[5:]
        fileList = os.listdir(pathname)
        #print fileList

        for i in range(0,len(fileList)):
            st = os.stat(fileList[i])
            print "mode:", self.statClass.filemode(st.st_mode)                  #rights
            print "file ID:", st[ST_INO]                                        #file number
            print "user ID:", st[ST_UID]                                        #userID
            print "group ID:", st[ST_GID]                                       #groupID
            print "file size:", st[ST_SIZE]                                     #file size
            print "file modified:",time.strftime("%d %b %Y %H:%M" , time.localtime(st[ST_MTIME]))   #date
            filename = fileList[i]+'\r\n'
            print "file name:", filename                                        #file name
            print ''
    

    # else:
    #     self.connSock.send('530 Not logged in.')

    def RETR(self, command):
    #     # RETR <SP> <pathname> <CRLF>
    #     # transfer a copy file to client over data connection

        fileName = command[5:]
        filePath = os.path.join(self.workingDirectory, fileName)
        # file_dir = Path(filePath)
        
        if filePath.is_fil():
            dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.passive:
                dataStreamSocket.bind(locIP, self.passivePort)
                dataStreamSocket.listen(1)
                dataStreamSocket, addr = dataStreamSocket.accept()
                self.connSock.send('150 File status okay; about to open data connection.\r\n')

            else:
                dataStreamSocket.connect((self.internetAddr, self.port))

            # if(fileName.find('.txt') or 
            #    fileName.find('.html') or 
            #    fileName.find('.pl') or 
            #    fileName.find('.cgi'))
            requestedFile = None

            if self.binaryFile:
                requestedFile = open(filePath,'rb')
            else :
                requestedFile = open(filePath,'r')

            fileChunk = requestedFile.read(1024)

            fileStat = os.stat(filePath)
            fileSizeTotal = fileStat[ST_SIZE]
            print 'Total file size:', fileSizeTotal

            fileSizeSent = 0

            while fileSizeSent < fileSizeTotal:
                print 'Sending...'
                dataStreamSocket.send(fileChunk)
                fileSizeSent += len(fileChunk)
                print 'File size sent:', fileSizeSent
                fileChunk = requestedFile.read(1024)

            requestedFile.close()

            if fileSizeSent == fileSizeTotal:
                self.connSock.send('226 Closing data connection. Requested file action successful.\r\n')
            else:
                self.connSock.send('451 Requested action aborted: local error in processing.\r\n') 

            dataStreamSocket.shutdown(socket.SHUT_WR)

    # def STOR(self, command):
    #     # STOR <SP> <pathname> <CRLF>
    #     # accept data from data connection and store as file on server

    def NOOP(self, command):
    #     # NOOP <CRLF>
    #     # server sends an okay reply
        self.connSock.send('200 Command okay.\r\n')

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