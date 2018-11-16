#!/usr/bin/env python

import os
import time
import socket
import signal

class Heart(object):

    @classmethod
    def beat(cls):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(('127.0.0.1',50050))
            sock.send('ping')
            sock.close()
            return True
        except Exception as e:
            #print("Exception e => "+str(e))
            return False

if __name__ == '__main__':
    while(True):
        try:
            time.sleep(10)
            if Heart.beat():
                print('Alive!')
                pass
            else:
                print('Dead!')
                pass
        except OSError:
            pass
