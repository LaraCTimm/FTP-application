import socket
import sys
import os

class clientLogic():
    def __init__(self):
        
        #servIP = socket.gethostbyname(sys.argv[1])
        self.locIP = socket.gethostbyname(socket.gethostname())
        self.servIP = self.locIP
        self.servPort = 21
        self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSock.connect((self.servIP, self.servPort))
        self.binaryFile = False
        self.passive = True
        self.passiveServerPort = self.servPort
        self.passiveServerIP = self.servIP
        self.baseDirectory = os.path.abspath('./clientDirectory')
        self.activePort = None
        self.activeIP = None

 # access control commands ---------------------------------------
    def USER(self, username):
        # USER <SP> <username> <CRLF>
        # username - string
        self.clientSock.send('USER '+username)

    def PASS(self, password):
        # PASS <SP> <password> <CRLF>
        # password - string
        self.clientSock.send('PASS '+password)

    def QUIT(self):
        # QUIT <CRLF>
        self.clientSock.send('QUIT \r\n')

    # transfer parameter commands -----------------------------------
    def PORT(self, ipAddr, port):
        # PORT <SP> <host-port> <CRLF>
        # host-post spec for data port to be used in data connection
        # 32bit internet host address, 16bit port address
        # "PORT h1,h2,h3,h4,p1,p2"
        IPChunks = ipAddr.split('.')
        portChunk1 = int(port / 256)
        portChunk2 = port % 256
        connectionString = '%i,%i,%i,%i,%i,%i' % (IPChunks[0], IPChunks[1], IPChunks[2], IPChunks[3], portChunk1, portChunk2)
        self.passive = False
        self.activeIP = ipAddr
        self.activePort = port

        self.clientSock.send('PORT '+connectionString)

    def PASV(self):
        self.clientSock.send('PASV \r\n')
        reply = self.clientSock.recv(1024)
        openBracketIndex = reply.find('(')
        closeBracketIndex = reply.find(')')
        connectionString = reply[openBracketIndex+1:-(len(reply) - closeBracketIndex + 1)]
        print connectionString

        rec = connectionString.split(',')
        self.passiveServerIP = rec[0]+'.'+rec[1]+'.'+rec[2]+'.'+rec[3]

        print 'test'

        upperByte = int(rec[4])
        lowerByte = int(rec[5])
        self.passiveServerPort = 256*upperByte + lowerByte

        print 'test2'

        self.passive = True

    def TYPE(self, fileName):
        # TYPE <SP> <type-code> <CRLF>
        # specifies representation type (ascii[D], ebcdic, image, 
        #       local byte size)
        if fileName.find('.'):
            if fileName.find('.txt') or \
                fileName.find('.html') or \
                fileName.find('.pl') or \
                fileName.find('.cgi'):
                self.binaryFile = False
                self.clientSock.send('TYPE A')
            else:
                self.binaryFile = True
                self.clientSock.send('TYPE I')
        else:
            return

    def MODE(self, transferMode):
        # MODE <SP> <mode-code> <CRLF>
        # specify data transfer mode (stream[D], block, compressed)
        self.clientSock.send('MODE '+transferMode)

    def STRU(self, structureCode):
        # STRU <SP> <structure-code> <CRLF>
        # specifies file structure (file[D], record, page)
        self.clientSock.send('STRU '+structureCode)

    # service commands -----------------------------------------------
    def RETR(self, fileName):
        # RETR <SP> <pathname> <CRLF>
        # transfer a copy file to client over data connection
        self.clientSock.send('RETR '+fileName)
        
        dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.passive:
            dataStreamSocket.connect((self.passiveServerIP, self.passiveServerPort))
            reply = self.clientSock.recv(1024)

            if reply[:3] != '150':
                print 'Unable to open data connection'
                return
        else:
            dataStreamSocket.bind(self.activeIP, self.activePort)
            reply = self.clientSock.recv(1024)

            if reply[:3] != '200':
                print 'Unable to open data connection'
                return

        filePath = os.path.join(self.baseDirectory, fileName)
        
        if self.binaryFile:
            requestedFile = open(filePath,'wb')
        else :
            requestedFile = open(filePath,'w')

        dataChunk = dataStreamSocket.recv(1024)

        while (dataChunk):
            print "Receiving..."
            requestedFile.write(dataChunk)
            dataChunk = dataStreamSocket.recv(1024)

        requestedFile.close()
        print "Done Receiving"

        response = self.clientSock.recv(1024)

        if response[:3] == '226':
            dataStreamSocket.shutdown(socket.SHUT_WR)
        else:
            print 'File trainsfer failed'
            os.remove(filePath)

    def STOR(self, fileName):
        # STOR <SP> <pathname> <CRLF>
        # accept data from data connection and store as file on server
        self.clientSock.send('STOR '+fileName)

    def NOOP(self):
        # NOOP <CRLF>
        # server sends an okay reply
        self.clientSock.send('NOOP \r\n')