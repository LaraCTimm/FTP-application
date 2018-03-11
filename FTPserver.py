import socket
import threading
import os
import sys
from pathlib2 import Path

import hashlib
# mystring = input('Enter String to hash: ')
# # Assumes the default UTF-8
# hash_object = hashlib.md5(mystring.encode())
# print(hash_object.hexdigest())

locIP = socket.gethostbyname(socket.gethostname())
# print loc_ip
locPort = 10000
currentDirectory = os.path.abspath('.')
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
        self.connSock = conn
        self.connAddr = addr
        self.baseDirectory = ''
        self.workingDirectory = ''
        self.loggedIn = False
        self.username = ''

        passwordFile = open("userdata.txt", 'r')
        self.userData = passwordFile.readlines()
        passwordFile.close()

        self.userRow = -1

    def run(self):
        self.connSock.send('220 Service ready for new user.\r\n')
        while 1:
            command = self.connSock.recv(256)
            # print command
            # self.connSock.send(command)

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
        # username - string
        
        # check if user is already registered
        self.username = command[5:]
        self.userRow = -1
        if self.username != '':
            for i in range(0, len(self.userData)):
                print 'checking line: ', i
                index = self.userData[i].find(self.username)
                print index
                if index != -1:
                    self.userRow = i
            if self.userRow > -1:
                print self.username
                self.baseDirectory = os.path.join(currentDirectory, "serverDirectory" )
                self.baseDirectory = os.path.join(self.baseDirectory, self.username)
                print currentDirectory
                print self.baseDirectory
                user_dir = Path(self.baseDirectory)
                print user_dir
                if user_dir.is_dir():
                    self.connSock.send('331 User name okay, need password.\r\n')
                    return
                else:
                    self.user = ''
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
        # password - string

        password = command[5:]
        if password != '' and password != ' ':
            if self.username != '':

                if self.userRow > -1:
                    storedPassword = self.userData[self.userRow][-(len(password)+1):-1] #32 later if cd5 hash
                    if storedPassword == password:
                        self.loggedIn = True
                        self.connSock.send('230 User logged in, proceed.\r\n')
                        return
                    else:
                        self.connSock.send('530 Not logged in. <password incorrect>\r\n')
                        return
                else:
                    self.connSock.send('332 Need account for login. <username not registered>\r\n')
                    return
            else:
                self.connSock.send('332 Need account for login. <invalid username>\r\n')
                return
        else:
            self.connSock.send('332 Need account for login. <invalid password>\r\n')
            return
        
    # def QUIT(self, command):
    #     # QUIT <CRLF>

    # # transfer parameter commands -----------------------------------
    # def PORT(self, command):
    #     # PORT <SP> <host-port> <CRLF>
    #     # host-post spec for data port to be used in data connection
    #     # 32bit internet host address, 16bit port address
    #     # "PORT h1,h2,h3,h4,p1,p2"

    # def TYPE(self, command):
    #     # TYPE <SP> <type-code> <CRLF>
    #     # specifies representation type (ascii[D], ebcdic, image, 
    #     #       local byte size)

    # def MODE(self, command):
    #     # MODE <SP> <mode-code> <CRLF>
    #     # specify data transfer mode (stream[D], block, compressed)

    # def STRU(self, command):
    #     # STRU <SP> <structure-code> <CRLF>
    #     # specifies file structure (file[D], record, page)

    # # service commands -----------------------------------------------
    # def RETR(self, command):
    #     # RETR <SP> <pathname> <CRLF>
    #     # transfer a copy file to client over data connection

    # def STOR(self, command):
    #     # STOR <SP> <pathname> <CRLF>
    #     # accept data from data connection and store as file on server

    # def NOOP(self, command):
    #     # NOOP <CRLF>
    #     # server sends an okay reply
    #     self.connSock.send('200 Command okay.\r\n')





#---------------------------------------------------------------------------
# MAIN

if __name__ == '__main__':
    FTPconnection = serverThread()
    FTPconnection.setDaemon(1)
    FTPconnection.start()
    print 'Listening on', locIP, ':', locPort
    raw_input('Press Enter to end...\n')
    FTPconnection.closeSocket()


    
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