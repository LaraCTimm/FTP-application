import socket
import sys
import os
from datetime import datetime

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

    def getReply(self):
        echoSentence = self.clientSock.recv(1024)
        print 'Server Echo:', echoSentence
        print ("")

 # access control commands ---------------------------------------
    def USER(self, username):
        # USER <SP> <username> <CRLF>
        # username - string
        self.clientSock.send('USER '+username)
        self.getReply()

    def PASS(self, password):
        # PASS <SP> <password> <CRLF>
        # password - string
        self.clientSock.send('PASS '+password)
        self.getReply()

    def QUIT(self):
        # QUIT <CRLF>
        self.clientSock.send('QUIT \r\n')
        self.getReply()

    # transfer parameter commands -----------------------------------
    def PORT(self, ipAddr, port):

        IPChunks = ipAddr.split('.')
        byteU = int(port / 256)
        byteL = port % 256

        connectionString = '%s,%i,%i' % (','.join(IPChunks[:4]), byteU, byteL)
        self.passive = False

        print connectionString

        self.activeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.activeSocket.bind((ipAddr, port))
        self.activeSocket.listen(1)

        self.clientSock.send('PORT '+connectionString)
        self.getReply()

    def PASV(self):
        self.clientSock.send('PASV \r\n')
        reply = self.clientSock.recv(1024)
        openBracketIndex = reply.find('(')
        print openBracketIndex
        closeBracketIndex = reply.find(')')
        print closeBracketIndex

        connectionString = reply[openBracketIndex+1:-(len(reply) - closeBracketIndex)]
        print connectionString

        rec = connectionString.split(',')
        self.passiveServerIP = '.'.join(rec[:4])

        byteU = int(rec[4])
        byteL = int(rec[5])
        self.passiveServerPort = 256*byteU + byteL

        print 'connecting to passive:', self.passiveServerIP, self.passiveServerPort

        self.passive = True

    def TYPE(self, fileName):
        # TYPE <SP> <type-code> <CRLF>
        # specifies representation type (ascii[D], ebcdic, image, 
        #       local byte size)
        if fileName.find('.') != -1:
            if fileName.find('.txt') != -1 or \
                fileName.find('.html') != -1 or \
                fileName.find('.pl') != -1 or \
                fileName.find('.cgi') != -1:
                self.binaryFile = False
                self.clientSock.send('TYPE A')
            else:
                self.binaryFile = True
                self.clientSock.send('TYPE I')
        else:
            return
        
        self.getReply()

    def MODE(self, transferMode):
        # MODE <SP> <mode-code> <CRLF>
        # specify data transfer mode (stream[D], block, compressed)
        self.clientSock.send('MODE '+transferMode)
        self.getReply()

    def STRU(self, structureCode):
        # STRU <SP> <structure-code> <CRLF>
        # specifies file structure (file[D], record, page)
        self.clientSock.send('STRU '+structureCode)

    def LIST(self):
        self.clientSock.send('LIST \r\n')

        if self.passive:
            dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                dataStreamSocket.connect((self.passiveServerIP, self.passiveServerPort))
                print 'Data connection established'
            else:
                print 'Unable to open data connection'
                print reply
                return
        else:
            dataStreamSocket, addr = self.activeSocket.accept()
            print str(datetime.now())
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                print 'Data connection established'
            # reply = self.clientSock.recv(1024)
            else:
                print 'Unable to open data connection'
                print reply
                return

        directoryArray = [] 
        itemIndex = 0
        directoryItem = dataStreamSocket.recv(1024)

        while (directoryItem):
            if len(directoryItem) > 40:
                print directoryItem
                directoryArray.append(directoryItem)
                itemIndex += 1
            directoryItem = dataStreamSocket.recv(1024)
            
        print "Done Receiving"

        response = self.clientSock.recv(1024)
        print response

        if response[:3] == '226':
            dataStreamSocket.shutdown(socket.SHUT_WR)
            print 'SHUTDOWN'
        else:
            print 'Directory listing failed'

    # service commands -----------------------------------------------
    def RETR(self, fileName):
        # RETR <SP> <pathname> <CRLF>
        # transfer a copy file to client over data connection
        
        self.clientSock.send('RETR '+fileName)

        if self.passive:
            dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                dataStreamSocket.connect((self.passiveServerIP, self.passiveServerPort))
                print 'Data connection established'
            else:
                print 'Unable to open data connection'
                print reply
                return
        else:
            dataStreamSocket, addr = self.activeSocket.accept()
            print str(datetime.now())
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                print 'Data connection established'
            # reply = self.clientSock.recv(1024)
            else:
                print 'Unable to open data connection'
                print reply
                return

            # if reply[:3] != '200':
            #     print 'Data connection established'
            #     return

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
        print response

        if response[:3] == '226':
            dataStreamSocket.shutdown(socket.SHUT_WR)
            print 'SHUTDOWN'
        else:
            print 'File trainsfer failed'

            os.remove(filePath)

    def STOR(self, fileName):
        # STOR <SP> <pathname> <CRLF>
        # accept data from data connection and store as file on server
        filePath = os.path.join(self.baseDirectory, fileName)

        if os.path.exists(filePath):
            self.clientSock.send('STOR '+fileName)
        else:
            print 'File not found'
            return

        dataStreamSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.passive: 
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                dataStreamSocket.connect((self.passiveServerIP, self.passiveServerPort))
                print 'Data connection established'
            else:
                print 'Unable to open data connection'
                print reply
                return
        else:
            dataStreamSocket, addr = self.activeSocket.accept()
            print str(datetime.now())
            reply = self.clientSock.recv(1024)
            if reply[:3] == '150':
                print 'Data connection established'
            # reply = self.clientSock.recv(1024)
            else:
                print 'Unable to open data connection'
                print reply
                return
        
        if self.binaryFile:
            requestedFile = open(filePath,'rb')
        else :
            requestedFile = open(filePath,'r')
            
        fileChunk = requestedFile.read(1024)

        while fileChunk:
            print 'Sending...'
            dataStreamSocket.send(fileChunk)
            fileChunk = requestedFile.read(1024)

        requestedFile.close()
        dataStreamSocket.shutdown(socket.SHUT_WR)

        print "Done Sending"

        response = self.clientSock.recv(1024)
        print response

        if response[:3] == '226':
            print 'File sent successfully'
        else:
            print 'File trainsfer failed'
            os.remove(filePath)        

    def NOOP(self):
        # NOOP <CRLF>
        # server sends an okay reply
        self.clientSock.send('NOOP\r\n')
        self.getReply()

    def CWD(self, directory):
        self.clientSock.send('CWD  ' + directory)
        self.getReply()
        
    def CDUP(self):
        self.clientSock.send('CDUP\r\n')
        self.getReply()
        
    def PWD(self):
        self.clientSock.send('PWD \r\n')
        self.getReply()