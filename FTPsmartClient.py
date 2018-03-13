import socket
import sys
from FTPclient_logic import clientLogic

#servIP = socket.gethostbyname(sys.argv[1])
servIP = socket.gethostbyname(socket.gethostname())

print servIP
servPort = 21

# clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# clientSock.connect((servIP, servPort))

logic = clientLogic()

if logic.clientSock.recv(256)[:3] == '220':       # wait for service ready response

# lab code for testing ------------------------------------------------------
    while 1:
        # generate message to be sent
        sentence = raw_input('Input message: ')

        try:
            functionName = sentence[:4].strip().upper()

            if functionName == 'USER':
                logic.USER(sentence[5:])

            elif functionName == 'PASS':
                logic.PASS(sentence[5:])

            elif functionName == 'QUIT':
                logic.QUIT()

            elif functionName == 'PORT':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', 0))
                logic.PORT(socket.gethostbyname(socket.gethostname()), sock.getsockname()[1])

            elif functionName == 'PASV':
                logic.PASV()

            elif functionName == 'TYPE':
                logic.TYPE(sentence[5:])

            elif functionName == 'MODE':
                logic.MODE(sentence[5:])

            elif functionName == 'STRU':
                logic.STRU(sentence[5:])

            elif functionName == 'RETR':
                logic.RETR(sentence[5:])

            elif functionName == 'STOR':
                logic.STOR(sentence[5:])

            elif functionName == 'NOOP':
                logic.NOOP()
            else:
                raise Exception('Command not found')
        except Exception, err:
            print 'Error: ', err
        # send message
        # clientSock.send(sentence)

        # recieve and print message received
        # echoSentence = logic.clientSock.recv(1024)
        # print 'Server Echo:', echoSentence
        # print ("")
        
        # if server wishes to close the connection, close the socket
        # if echoSentence == 'Connection closed...':
        #    break

    # close the socket
    logic.clientSock.close()
#-------------------------------------------------------------------------------