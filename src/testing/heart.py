#!/usr/bin/env python

import os
import re
import time
import socket
import signal

class Heart(object):

    __pids__ = []

    @classmethod
    def format_data(cls,data):
        data = re.match('(\[)(.*)(, )(.*)(, )(.*)(\])', data, re.M | re.I)
        if data is not None:
            return [data.group(2),data.group(4),data.group(6)]

    @classmethod
    def beat(cls):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect(('127.0.0.1',50050))
            sock.send('ping')
            data = sock.recv(1024)
            if data is not None:
                Heart.__pids__ = Heart.format_data(data)
            sock.close()
            return True
        except Exception as e:
            print("Exception e: "+str(e))
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
                [os.kill(int(pid), signal.SIGTERM) for pid in Heart.__pids__]
                pass
        except OSError:
            pass
