#!/usr/bin/env python

import socket,sys
from optparse import OptionParser

class Client():

    def __init__(self,ip='127.0.0.1',port=5051,command='probe'):

        parser = OptionParser()
        parser.add_option("-c",
            "--command", dest='command', help='"Command to send server. Defaults to \"reload\""',default='reload')
        parser.add_option("-i",
            "--ip-addr", dest='ip', help='"The servers ip address. Defaults to 127.0.0.1."',default='127.0.0.1')
        parser.add_option("-p",
            "--port", dest='port', help='"Deafults to port 50050"', type="int", default=50050)
        (options, args) = parser.parse_args()

        self.ip = options.ip
        self.port = options.port
        self.command = options.command

    def main(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print('Failed to create socket. Error => ' + msg[1])
            sys.exit();

        print("Socket created.")

        try:
            s.connect((str(self.ip),int(self.port)))
        except Exception as e:
            print("Connect exception Error => " + str(e))

        s.send(str(self.command))
        print("Server: " + s.recv(1024))
        s.close()

if __name__ == '__main__':
    c = Client()
    c.main()
