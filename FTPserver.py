import socket
import threading
import os
import sys

locIP = socket.gethostbyname(socket.gethostname())
# print loc_ip
locPort = 10000

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

    def run(self):
        self.connSock.send('220 Service ready for new user.\r\n')
        while 1:
            command = self.connSock.recv(256)
            print command
            self.connSock.send(command)

            # if not command:
            #     break
            # else:
            #     print 'Recieved: ', command
            #     try:
            #         action = getattr(self, command[:4].strip().upper())
            #         action(command)
            #     except Exception, err:
            #         print 'Error: ', err
            #         self.connSock.send('500 Syntax error, command unrecognized.\r\n')

    # access control commands ---------------------------------------
    def USER(self):
        # USER <SP> <username> <CRLF>
        # username - string

    def PASS(self):
        # PASS <SP> <password> <CRLF>
        # password - string

    def QUIT(self):
        # QUIT <CRLF>

    # transfer parameter commands -----------------------------------
    def PORT(self):
        # PORT <SP> <host-port> <CRLF>
        # host-post spec for data port to be used in data connection
        # 32bit internet host address, 16bit port address
        # "PORT h1,h2,h3,h4,p1,p2"

    def TYPE(self):
        # TYPE <SP> <type-code> <CRLF>
        # specifies representation type (ascii[D], ebcdic, image, 
        #       local byte size)

    def MODE(self):
        # MODE <SP> <mode-code> <CRLF>
        # specify data transfer mode (stream[D], block, compressed)

    def STRU(self):
        # STRU <SP> <structure-code> <CRLF>
        # specifies file structure (file[D], record, page)

    # service commands -----------------------------------------------
    def RETR(self):
        # RETR <SP> <pathname> <CRLF>
        # transfer a copy file to client over data connection

    def STOR(self):
        # STOR <SP> <pathname> <CRLF>
        # accept data from data connection and store as file on server

    def NOOP(self):
        # NOOP <CRLF>
        # server sends an okay reply
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