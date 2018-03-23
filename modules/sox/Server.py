#!/usr/bin/env python

import socket,sys

class Server():

    def __init__(self,ip='0.0.0.0',port=5050):
        self.ip = ip
        self.port = port

    def main(self):

        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((self.ip, int(self.port)))

        s.listen(5)
        print("Listening for connections.")
        while(True):
            c, addr = s.accept()
            print("Received connection from " + str(addr))
            mes = c.recv(1024)
            if(mes == 'smon'):
                print("Starting camera!")
                c.send("Starting camera!")
            elif(mes == 'kmon'):
                print("Killing camera!")
                c.send("Killing camera!")
            elif(mes == 'smot'):
                print("Starting motion sensor!")
                c.send("Starting motion sensor!")
            elif(mes == 'kmot'):
                print("Killing motion sensor!")
                c.send("Killing motion sensor!")
            elif(mes == 'probe'):
                print("Server is alive.")
                c.send("Server is alive.")
            else:
                print(mes + " is not a known command.")
                c.send(mes + " is not a konwn command!")
        c.close()

if __name__ == '__main__':
    s = Server()
    s.main()
