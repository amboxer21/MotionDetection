#!/usr/bin/env python

import socket,sys
from optparse import OptionParser

class Client():

    def __init__(self,ip='127.0.0.1',port=5050,command='probe'):

        parser = OptionParser()
        parser.add_option("-c",
            "--command", dest='command', help='"Command to send server. Defaults to \"probe\""',default='probe')
        parser.add_option("-i",
            "--ip-addr", dest='ip', help='"The servers ip address. Defaults to 127.0.0.1."')
        parser.add_option("-p",
            "--port", dest='port', help='"Deafults to port 5050"', type="int", default=5050)
        (options, args) = parser.parse_args()

        self.ip = options.ip
        self.port = options.port
        self.command = options.command

    def main(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print('Failed to create socket. Error => ' + msg[1])
            sys.exit();

        print("Socket created.")

        try:
            #s.connect('174.57.49.30','5050')
            s.connect((socket.gethostbyaddr(self.ip),int(self.port)))
            s.send(str(self.command))
            print("Server: " + s.recv(1024))
            s.close()
        except Exception as e:
            print("Connect exception Error => " + str(e))

if __name__ == '__main__':
    c = Client()
    c.main()
