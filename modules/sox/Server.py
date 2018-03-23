#!/usr/bin/env python

import socket,sys

class Server():

    def main(self):

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((socket.gethostname(), 5051))

        s.listen(5)
        print("Listening for connections.")
        while(True):
            c, addr = s.accept()
            print("Received connection from " + str(addr))
            mes = c.recv(1024)
            if(mes == 'mon'):
                print("Starting camera!")
                c.send("Starting camera!")
            else:
                print(mes + " is not a known command.")
                c.send(mes + " is not a konwn command!")
        c.close()

if __name__ == '__main__':
    s = Server()
    s.main()
