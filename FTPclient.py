import socket
import sys

#servIP = socket.gethostbyname(sys.argv[1])
servIP = socket.gethostbyname(socket.gethostname())

print servIP
servPort = 10000




clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect((servIP, servPort))

if clientSock.recv(256)[:3] == '220':       # wait for service ready response

# lab code for testing ------------------------------------------------------
    while 1:
        # generate message to be sent
        sentence = raw_input('Input message: ')
        # send message
        clientSock.send(sentence)

        # recieve and print message received
        echoSentence = clientSock.recv(1024)
        print 'Server Echo:', echoSentence
        print ("")
        
        # if server wishes to close the connection, close the socket
        if echoSentence == 'Connection closed...':
            break

    # close the socket
    clientSock.close()
#-------------------------------------------------------------------------------