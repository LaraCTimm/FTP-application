import socket
import sys
from FTPclient_logic import clientLogic

if sys.argv[1] == 'local':
    servIP = socket.gethostbyname(socket.gethostname())
elif sys.argv[1].upper() == 'IP':
    servIP = sys.argv[2]
else:
    servIP = socket.gethostbyname(sys.argv[1])
    
print servIP
#servIP = '192.168.1.41'
#servIP = socket.gethostbyname(socket.gethostname())


logic = clientLogic(servIP)

reply = logic.clientSock.recv(256)
print 'Response:', reply
if reply[:3] == '220':       # wait for service ready response

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

                IPAddr = socket.gethostbyname(socket.gethostname())
                port = sock.getsockname()[1]

                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.close()
                
                logic.PORT(IPAddr, port)

                # # ubuntu hack
                # IPAdd = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] \
                #            if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], \
                #            s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
                # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # sock.bind((IPAdd, 0))
                # port = sock.getsockname()[1]
                # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # sock.close()
                # logic.PORT(IPAdd, port)
                
                
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

            # elif functionName == 'AUTH':
            #     logic.clientSock.send('AUTH TLS')
            #     #logic.getReply()
            
            else:
                raise Exception('Command not found')
        except Exception, err:
            print 'Error: ', err

    logic.clientSock.close()
#-------------------------------------------------------------------------------