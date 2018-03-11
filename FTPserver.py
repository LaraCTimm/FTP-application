import socket
import threading
import os
import sys

loc_ip = socket.gethostbyname(socket.gethostname())
# print loc_ip
loc_port = 10000

#---------------------------------------------------------------------------

class serverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.servSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servSock.bind((loc_ip, loc_port))

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



#---------------------------------------------------------------------------
# MAIN

if __name__ == '__main__':
    FTPconnection = serverThread()
    FTPconnection.setDaemon(1)
    FTPconnection.start()
    print 'Listening on', loc_ip, ':', loc_port
    raw_input('Press Enter to end...\n')
    FTPconnection.closeSocket()