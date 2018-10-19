#!/usr/bin/env python

import os
import time
import socket
import signal

class Heart(object):

    __motion_pid__ = None
    __stream_pid__ = None

    @classmethod
    def beat(cls):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(('127.0.0.1',50050))
            sock.sendall(b'ping')
            Heart.__motion_pid__ = sock.recv(1024)
            return True
        except Exception as e:
            return False

if __name__ == '__main__':
    while(True):
        try:
            time.sleep(10)
            if Heart.beat():
                pass
            else:
                os.kill(int(Heart.__motion_pid__), signal.SIGTERM)
        except OSError:
            pass
