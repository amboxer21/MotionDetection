#!/usr/bin/env python

import os
import time
import socket
import signal

class Ping(object):

    __pid__ = 1025

    @classmethod
    def alive(cls):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(('127.0.0.1',50050))
            sock.sendall(b'ping')
            Ping.__pid__ = sock.recv(1024)
            return True
        except Exception as e:
            return False

if __name__ == '__main__':
    while(True):
        try:
            time.sleep(10)
            if Ping.alive():
                pass
            else:
                os.kill(int(Ping.__pid__), signal.SIGTERM)
        except OSError:
            pass
