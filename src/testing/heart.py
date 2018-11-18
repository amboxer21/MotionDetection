#!/usr/bin/env python

import os
import re
import time
import socket
import signal
import logging
import logging.handlers

from optparse import OptionParser

class Logging(object):

    @staticmethod
    def log(level,message,verbose=True):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/var/log/motiondetection.log")
            )
            formatter = logging.Formatter(logging.BASIC_FORMAT)
            handler.setFormatter(formatter)
            root = logging.getLogger()
            root.setLevel(os.environ.get("LOGLEVEL", str(level)))
            root.addHandler(handler)
            # Log all calls to this class in the logfile no matter what.
            if comm is None:
                print(str(level) + " is not a level. Use: WARN, ERROR, or INFO!")
                return
            elif comm.group() == 'ERROR':
                logging.error(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection - "
                    + str(message)))
            elif comm.group() == 'INFO':
                logging.info(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection - "
                    + str(message)))
            elif comm.group() == 'WARN':
                logging.warn(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection - "
                    + str(message)))
            if verbose or str(level) == 'ERROR':
                print("(" + str(level) + ") "
                    + str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection - "
                    + str(message)))
        except IOError as eIOError:
            if re.search('\[Errno 13\] Permission denied:', str(eIOError), re.M | re.I):
                print("(ERROR) MotionDetection - Must be sudo to run MotionDetection!")
                sys.exit(0)
            print("(ERROR) MotionDetection - IOError in Logging class => "
                + str(eIOError))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection - IOError => "
                + str(eIOError)))
        except Exception as eLogging:
            print("(ERROR) MotionDetection - Exception in Logging class => "
                + str(eLogging))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection - Exception => " 
                + str(eLogging)))
            pass
        return

class Heart(object):

    __pids__ = []

    def __init__(self,options_dict={}):
        self.ip   = options_dict['ip']
        self.port = options_dict['port']

    @staticmethod
    def format_data(data):
        data = re.match('(\[)(.*)(, )(.*)(, )(.*)(\])', data, re.M | re.I)
        if data is not None:
            return [data.group(2),data.group(4),data.group(6)]

    def beat(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self.ip,self.port))
            sock.send('ping')
            data = sock.recv(1024)
            if data is not None:
                Heart.__pids__ = Heart.format_data(data)
            sock.close()
            return True
        except Exception as e:
            return False

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', '--ip',
        dest='ip', default='0.0.0.0',
        help='This is the IP address of the server.')
    parser.add_option('-l', '--log-file',
        dest='logfile', default='/var/log/motiondetection.log',
        help='Log file defaults to /var/log/motiondetection.log.')
    parser.add_option('-S', '--server-port',
        dest='port', type='int', default=50050,
        help='Heartbeat port defaults to port 50050.'
            + 'This is the port the heartbeat server runs on. '
            + 'This server takes in pid\'s from the motiondetection '
            + 'server and stores them in a list. If the heartbeat server '
            + 'loses connection with the motiondetection server then this '
            + 'heartbeat server will kill all pids in the list.')
    (options, args) = parser.parse_args()

    heart = Heart({'ip': options.ip, 'port': options.port})

    while(True):
        try:
            time.sleep(10)
            if heart.beat():
                pass
            elif Heart.__pids__:
                [os.kill(int(pid), signal.SIGTERM) for pid in Heart.__pids__]
                Logging.log('INFO',
                    'Lost connection to the MotionDetection framework. Killing system now!')
        except OSError:
            pass
