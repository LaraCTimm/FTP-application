import socket
import threading
import os
import sys
import time
from stat import *  # library used in LIST
import shutil       # library used in RMD

locIP = socket.gethostbyname(socket.gethostname())  # get local IP of server PC
locPort = 21                                        # default port for FTP command connection

# this directory must exist and should contain a directory for each registered user
serverDirectory = os.path.abspath('./serverDirectory')

#---------------------------------------------------------------------------

class serverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.bind((locIP, locPort))

    def run(self):
        # up to 5 clients may be connected at a time
        self.servSock.listen(5)
        while 1:
            # for each new client that connects, assign it a new thread
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
        self.connSock = conn            # socket for command messages with connected client
        self.connAddr = addr            # IP address of connected client
        self.baseDirectory = ''         # serverDirectory\username
        self.workingDirectory = ''      # current cleint working directory

        self.loggedIn = False
        self.username = ''
        self.passive = False 
        self.binaryFile = False 
        self.setPortPasv = False

        self.dataAddress = ''   # IP address for data connection
        self.dataPort = -1      # port for data connection
        
        # file containing usernames and passwords of registered clients
        passwordFile = open("userdata.txt", 'r')
        self.userData = passwordFile.readlines()
        passwordFile.close()

    def run(self):
        self.connSock.send('220 Service ready for new user.\r\n')
        while 1:
            command = self.connSock.recv(256)       # all client commands handled here
            if not command: 
                break
            else:
                print 'Request:', command
                try:
                    # convert received command into a function call and try to call that function
                    action = getattr(self, command[:4].strip().upper())
                    action(command)
                except Exception, err:
                    print 'Error:', err
                    if err[0][:3] == '500':
                        self.connSock.send('500 Syntax error, command unrecognized.\r\n')
                    elif err[0][:3] == '221':
                        self.connSock.send('221 Service closing control connection.\r\n')
                        self.connSock.close()
                        print 'Client disconnected...'
                        break
                    else:
                        self.connSock.send('500 Command not supported.\r\n')


    # ACCESS CONTROL COMMANDS ---------------------------------------------------------------------------

    def USER(self, command):
        
        self.username = command[5:-2]
        # print self.username
        self.userRow = -1

        if self.username != '':
            # check if user is already registered
            for i in range(0, len(self.userData)):
                index = self.userData[i].find(self.username)    
                
                if index != -1:
                    self.userRow = i    # identify which user is connecting to server
                    break               # stop looking
            
            storedUsername = (self.userData[self.userRow].split(' '))[0]

            if storedUsername == self.username:       # if username matches that found in user data file

                self.baseDirectory = os.path.join(serverDirectory, self.username) 

                if os.path.isdir(self.baseDirectory):
                    self.connSock.send('331 User name okay, need password.\r\n')
                    return
                else: 
                    # if directory doesn't exist, make one at base directory for specific client
                    os.makedirs(self.baseDirectory)
                    self.connSock.send('331 User name okay, need password.\r\n')
                    return
            else:
                self.username = ''
                self.connSock.send('332 Need account for login.\r\n')
                return
        else:
            self.connSock.send('332 Need account for login.\r\n')
            return

    def PASS(self, command):
        password = command[5:-2]

        if password != '' and password != ' ':      # must have entered a valid password
            if self.username != '':                 # must have entered a registered username 

                if self.userRow > -1:               # if the username was found in the userData file
                    # retrieve stored password (minus end of line character)
                    storedPassword = (self.userData[self.userRow].split(' '))[1][:-1]

                    if storedPassword == password:
                        self.loggedIn = True
                        self.workingDirectory = self.baseDirectory
                        self.connSock.send('230 User logged in, proceed.\r\n')
                        return
                    else:
                        password = ''
                        self.connSock.send('530 Not logged in.\r\n')
                        return
                else:
                    self.connSock.send('332 Need account for login.\r\n')
                    return
            else:
                self.connSock.send('332 Need account for login.\r\n')
                return
        else:
            self.connSock.send('332 Need account for login.\r\n')

    def CWD(self, command):
        if self.loggedIn == False: 
            return

        directoryString = command[4:-2]

        if directoryString == self.workingDirectory.split('\\')[-2]:
            self.CDUP('dummy string')
            return

        # check for variations in commands made by different clients
        index = directoryString.find('\\')
        if index != -1:
            directoryString = directoryString.split('\\')[-1]   # isolate directory name
        
        # make a path of the directory to be changed to
        newDirectory = os.path.join(self.workingDirectory, directoryString)

        if os.path.exists(newDirectory):
            self.workingDirectory = newDirectory
            self.connSock.send('250 Requested action okay. Working directory changed.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Directory does not exist.\r\n')     
    
    def CDUP(self, command):
        if self.loggedIn == False: 
            return

        # check that the client isnt going above their base directory
        highestDirectory = os.path.join(serverDirectory, self.username)
        if self.workingDirectory != highestDirectory:
            self.workingDirectory = os.path.dirname(self.workingDirectory)
            self.connSock.send('250 Requested action okay. Working directory changed.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Permission denied.\r\n')    
    
    def QUIT(self, command):
        # if the client quits the application the client thread can be closed
        raise Exception('221 Service closing control connection.')

    def checkLoggedIn(self):
        if self.loggedIn == False: 
            self.connSock.send('530 Not logged in.\r\n')
            return False
        else: 
            return True

    # TRANSFER PARAMETER COMMANDS ----------------------------------------------------------------------

    def PORT(self, command): # ACTIVE MODE ###############
        if self.checkLoggedIn() == False:
            return

        # if in passive mode, close the socket accepting new passive data connections
        if self.passive:
            self.passive = False
            self.passiveSocket.close()

        # set data IP and port from recieved client active port details
        rec = command[5:-2].split(',')
        self.dataAddress = '.'.join(rec[:4])
        byteU = int(rec[4])
        byteL = int(rec[5])
        self.dataPort = 256*byteU + byteL

        self.connSock.send('200 Port command successful.\r\n')

        # if port or pasv have not been called, dont allow list, retr or stor.
        self.setPortPasv = True

    def PASV(self, command): # PASSIVE MODE ##############
        if self.checkLoggedIn() == False:
            return

        self.passive = True

        # set up a new passive socket on which to listen for a new data connection
        self.passiveSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.passiveSocket.bind((locIP, 0))     # binds to local IP and available port
        ip, port = self.passiveSocket.getsockname()
        self.passiveSocket.listen(1)            # listen for a new connection on specified port
        print 'Listening on',ip,':',port

        # convert details to connection string to be sent to client
        byteU = int(port / 256)
        byteL = int(port % 256)
        
        connectionString = '(%s,%i,%i)' % (','.join(locIP.split('.')), byteU, byteL)
        self.connSock.send('227 Entering passive mode '+ connectionString +'.\r\n')
        self.setPortPasv = True

    def TYPE(self, command):
        if self.checkLoggedIn() == False:
            return

        fileType = command[5:-2]

        # set file type to be sent on data connection 
        if fileType == 'I':
            self.binaryFile = True
            self.connSock.send('200 Switching to Binary mode.\r\n')
        elif fileType == 'A':
            self.binaryFile = False
            self.connSock.send('200 Switching to ASCII mode.\r\n')
        else:
            self.connSock.send('504 Command not implemented for that parameter.\r\n')

    def STRU(self, command):
        # specifies file structure. Only default, File, is implemented
        if self.checkLoggedIn() == False:
            return

        structure = command[5:-2]

        if structure == 'F':
            self.connSock.send('200 Switching to File structure mode.\r\n')
        else:
            self.connSock.send('504 Command not implemented for that parameter.\r\n')

    def MODE(self, command):
        # specify data transfer mode. Only default, Stream, is implemented
        if self.checkLoggedIn() == False:
            return

        mode = command[5:-2]

        if mode == 'S':
            self.connSock.send('200 Switching to Stream transfer mode.\r\n')
        else:
            self.connSock.send('504 Command not implemented for that parameter.\r\n')

    # SERVICE COMMANDS ---------------------------------------------------------------------------------

    def RETR(self, command):    # transfer a copy file to client 

        if self.checkLoggedIn() == False:
            return

        # only continue if a data socket can be opened
        if self.setPortPasv: 
            fileName = command[5:-2]

            # check for variations in commands made by different clients
            index = fileName.find('\\')     
            if index != -1:
                fileName = fileName.split('\\')[-1]
                
            filePath = os.path.join(self.workingDirectory, fileName)
            
            if os.path.isfile(filePath):    # if file exists on server
                requestedFile = None

                # open the file to read, open mode depends on the file type set by TYPE command 
                if self.binaryFile:
                    requestedFile = open(filePath,'rb')
                else:
                    requestedFile = open(filePath,'r')

                self.connSock.send('150 Opening data connection.\r\n')
                try:
                    self.open_dataSocket()

                    fileChunk = requestedFile.read(1024)        # read from the file

                    while fileChunk:                            # while there is still more file to read
                        print 'Sending...'
                        self.dataSocket.send(fileChunk)         # send on dataSocket
                        fileChunk = requestedFile.read(1024)    # read some more
                
                except Exception, err:
                    self.connSock.send('451 Requested action aborted: local error in processing.\r\n')

                requestedFile.close()       # close the file read from
                self.close_dataSocket()     # close the data socket

                self.connSock.send('226 Closing data connection. Requested file action successful.\r\n')
            else:
                self.connSock.send('550 Requested action not taken. File unavailable.\r\n')
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def STOR(self, command):    # accept data from data connection and store as file on server
        
        if self.checkLoggedIn() == False:
            return

        # only continue if a data socket can be opened
        if self.setPortPasv:
            fileName = command[5:-2]

            # check for variations in commands made by different clients
            index = fileName.find('\\')
            if index != -1:
                fileName = fileName.split('\\')[-1]

            filePath = os.path.join(self.workingDirectory, fileName)
            requestedFile = None

            # open the file to write to, open mode depends on the file type set by TYPE command
            if self.binaryFile:
                requestedFile = open(filePath, 'wb')
            else:
                requestedFile = open(filePath, 'w')
            
            self.connSock.send('150 File status okay; about to open data connection.\r\n')

            try:
                self.open_dataSocket()

                fileChunk = self.dataSocket.recv(1024)      # recieve from data socket
                while (fileChunk):                          # while the data recieved exists
                    print "Receiving..."
                    requestedFile.write(fileChunk)          # write what is recieved to file
                    fileChunk = self.dataSocket.recv(1024)  # continue to recieve from data socket

                print "Done Receiving"
                requestedFile.close()           # close the file read from
                self.close_dataSocket()         # close the data socket

                self.connSock.send('226 Closing data connection. Requested file action successful.\r\n')
            
            except Exception, err:
                self.connSock.send('550 Requested action not taken. File transfer unsuccessful.\r\n')
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def open_dataSocket(self):
        #----PASSIVE-------------------------------------------------------
        if self.passive:
            self.dataSocket, addr = self.passiveSocket.accept()     # accept a connection from client
            print 'Data stream opened at address:', addr           
        #----ACTIVE--------------------------------------------------------
        else:
            self.dataSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # make a new TCP socket
            self.dataSocket.connect((self.dataAddress,self.dataPort))   # bind to address/port recieved from PORT command
            print 'Data stream opened at address: (\'%s\', %u)' % (self.dataAddress, self.dataPort)

    def close_dataSocket(self):
        self.setPortPasv = False        # require a new PORT/PASV command to be made before more data can be sent
        if self.passive:                # close passive socket (if passive)
            self.passiveSocket.close()
        self.dataSocket.close()         # close the data socket
    
    def DELE(self, command):
        if self.checkLoggedIn() == False:
            return

        fileString = command[5:-2]

        # check for variations in commands made by different clients
        index = fileString.find('\\')
        if index != -1:
            fileString = fileString.split('\\')[-1]

        filePath = os.path.join(self.workingDirectory, fileString)

        if os.path.isfile(filePath):    # if the file exists, delete it
            os.remove(filePath)
            self.connSock.send('250 Requested file action okay, file deleted.\r\n')

        elif os.path.isdir(filePath):   # to remove directory use a different command
            self.connSock.send('550 Requested action not taken. To delete directory use RMD.\r\n')
        
        else:
            self.connSock.send('550 Requested action not taken. File does not exist.\r\n')

    def PWD(self, command):
        if self.checkLoggedIn() == False:
            return

        # only send the part of the directory path from the client base directory onwards
        self.connSock.send('257 \"%s\" is the working directory.\r\n' % (self.workingDirectory[len(serverDirectory):]))

    def LIST(self, command):
        if self.checkLoggedIn() == False:
            return
        
        # ensure that the list is sent in ASCII mode
        self.binaryFile = False

        if self.setPortPasv:    # check data stream ready for opening

            self.connSock.send('150 Opening data connection. Sending directory list.\r\n')    
            self.open_dataSocket()      # open data socket

            itemString = ''

            # for all items in the working directory, get their file info (createItemString) and append it to the item string
            for item in os.listdir(self.workingDirectory):
                itemString += self.createItemString(os.path.join(self.workingDirectory,item))

            self.dataSocket.send(itemString)    # send the directory list in the data socket 
            
            self.connSock.send('226 Closing data connection. Directory list sent.\r\n')
            self.close_dataSocket()     # close data socket
        else:
            self.connSock.send('425 Use PORT or PASV first.\r\n')

    def createItemString(self, itemPath):
        itemStat = os.stat(itemPath)        # using stat module, get file info
        permissionString = 'rwxrwxrwx'      # set maximum permission string
        itemPermissions = ''                # clear item permissions
        directoryChar = ''                  # clear directory flag

        # for each char in permissionString, check and set permission based on result from 
        #       the logical AND of that bit (of the file mode) and 1
        for i in range(9):
            if (itemStat.st_mode>>(8-i)) & 1:
                itemPermissions += permissionString[i]
            else:
                itemPermissions += '-'

        # if the item is a directory, set the directory flag
        if os.path.isdir(itemPath):
            directoryChar = 'd'
        else:
            directoryChar = '-'

        # extract the date and time values 
        timestamp = time.strftime("%b %d %H:%M" , time.localtime(itemStat[ST_MTIME]))

        # assemble the itemString for that item
        # permissionString itemNumber userID groupID fileSize timeStamp filePath
        itemString = directoryChar + itemPermissions + ' ' + str(itemStat[ST_INO]) + ' ' + \
                     str(itemStat[ST_UID]) + ' ' + str(itemStat[ST_GID]) + ' ' + \
                     str(itemStat[ST_SIZE]) + ' ' + timestamp + ' ' + os.path.basename(itemPath) + '\r\n'
                     
        return itemString

    def MKD(self, command):
        if self.checkLoggedIn() == False:
            return

        directoryString = command[4:-2]

        # check for variations in commands made by different clients
        index = directoryString.find('\\')
        if index != -1:
            directoryString = directoryString.split('\\')[-1]

        dirPath = os.path.join(self.workingDirectory, directoryString)

        if not os.path.exists(dirPath):     # if the directory doesn't already exist, make it
            os.makedirs(dirPath)
            # send the part of the path higher that the users base directory
            self.connSock.send('257 \"%s\\%s\" created.\r\n'\
                    % (self.workingDirectory[len(serverDirectory):], command[4:-2]))
        else:
            self.connSock.send('550 Requested action not taken. \"%s\\%s\" already exists.\r\n'\
                    % (self.workingDirectory[len(serverDirectory):], command[4:-2]) )
            
    def RMD(self, command):
        if self.checkLoggedIn() == False:
            return

        if command[5:] != '':
            directoryString = command[4:-2]

            # check for variations in commands made by different clients
            index = directoryString.find('\\')
            if index != -1:
                directoryString = directoryString.split('\\')[-1]

            dirPath = os.path.join(self.workingDirectory, directoryString)

            if os.path.isdir(dirPath):      # if the directory exists, delete it
                shutil.rmtree(dirPath)
                self.connSock.send('250 Requested file action okay, directory deleted.\r\n')

            elif os.path.isfile(dirPath):   # if the requested item is a file, use a dirrerent command
                self.connSock.send('550 Requested action not taken. To delete file use DELE\r\n')

            else:
                self.connSock.send('550 Requested action not taken. Directory does not exist.\r\n')
        else:
            self.connSock.send('550 Requested action not taken. Permission denied.\r\n')

    def NOOP(self, command):
        if self.checkLoggedIn() == False:
            return
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