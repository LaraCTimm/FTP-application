import socket
import sys
from FTPclient_logic import clientLogic

#servIP = socket.gethostbyname(sys.argv[1])
servIP = socket.gethostbyname(socket.gethostname())

logic = clientLogic(servIP)

if logic.clientSock.recv(256)[:3] == '220':       # wait for service ready response

    while 1:
        # generate message to be sent
        sentence = raw_input('Input message: ')

        try:
            functionName = sentence[:4].strip().upper()

            if functionName == 'USER':
                logic.USER(sentence[5:])

            elif functionName == 'PASS':
                logic.PASS(sentence[5:])

            elif functionName == 'CWD':
                logic.CWD(sentence[4:])

            elif functionName == 'CDUP':
                logic.CDUP()

            elif functionName == 'QUIT':
                logic.QUIT()
                break

            elif functionName == 'PORT':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', 0))
                logic.PORT(socket.gethostbyname(socket.gethostname()), sock.getsockname()[1])

            elif functionName == 'PASV':
                logic.PASV()

            elif functionName == 'TYPE':
                logic.TYPE(sentence[5:])

            elif functionName == 'STRU':
                logic.STRU(sentence[5:])

            elif functionName == 'MODE':
                logic.MODE(sentence[5:])

            elif functionName == 'RETR':
                logic.RETR(sentence[5:])

            elif functionName == 'STOR':
                logic.STOR(sentence[5:])

            elif functionName == 'DELE':
                logic.DELE(sentence[5:])

            elif functionName == 'PWD':
                logic.PWD()

            elif functionName == 'LIST':
                logic.LIST()

            elif functionName == 'MKD':
                logic.MKD(sentence[4:])

            elif functionName == 'RMD':
                logic.RMD(sentence[4:])

            elif functionName == 'NOOP':
                logic.NOOP()

            elif functionName == 'AUTH':
                logic.clientSock.send('AUTH TLS')
                #logic.getReply()
            
            else:
                raise Exception('Command not found')
        except Exception, err:
            print 'Error: ', err

    logic.clientSock.close()
#-------------------------------------------------------------------------------