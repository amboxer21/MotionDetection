#!/usr/bin/env python

import socket,sys

class Client():

    def main(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print('Failed to create socket. Error => ' + msg[1])
            sys.exit();

        print("Socket created.")

        try:
            #s.connect('174.57.49.30','5050')
            s.connect(('200.255.100.118',5051))
            s.send("mon")
            print("Server: " + s.recv(1024))
            s.close()
        except Exception as e:
            print("Connect exception Error => " + str(e))

if __name__ == '__main__':
    c = Client()
    c.main()
