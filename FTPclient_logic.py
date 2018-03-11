 
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