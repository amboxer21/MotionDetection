#!/usr/bin/env python

import os
import re
import sys
import time
import email
import socket
import signal
import smtplib
import logging
import threading
import logging.handlers

from optparse import OptionParser

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

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
                logging.warning(str(time.asctime(time.localtime(time.time()))
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

class Mail(object):

    __disabled__ = False

    @staticmethod
    def send(sender,to,password,port,subject,body):
        try:
            if not Mail.__disabled__:
                message = MIMEMultipart()
                message['Body'] = body
                message['Subject'] = subject
                mail = smtplib.SMTP('smtp.gmail.com',port)
                mail.starttls()
                mail.login(sender,password)
                mail.sendmail(sender, to, message.as_string())
                Logging.log("INFO", "(Mail.send) - Sent email successfully!")
            else:
                Logging.log("WARN", "(Mail.send) - Sending mail has been disabled!")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "(Mail.send) - Could not athenticate with password and username!")
        except Exception as e:
            Logging.log("ERROR",
                "(Mail.send) - Unexpected error in Mail.send() error e => "
                + str(e))
            pass

class Heart(object):

    __pids__ = []
    __timeout__ = 10

    def __init__(self,options_dict={}):
        self.ip            = options_dict['ip']
        self.port          = options_dict['port']
        self.email         = options_dict['email']
        self.password      = options_dict['password']
        self.email_port    = options_dict['email_port']
        self.disable_email = options_dict['disable_email']

        self.min_thresh_interval = options_dict['min_thresh_interval']
        self.max_thresh_interval = options_dict['max_thresh_interval']

        if not self.disable_email and (self.email is None or self.password is None):
            Logging.log("ERROR",
                "(MotionDetection.__init__) - Both E-mail and password are required!")
            sys.exit(0)

    @staticmethod
    def start_thread(proc,*args):
        try:
            t = threading.Thread(target=proc,args=args)
            t.daemon = True
            t.start()
        except Exception as eStartThread:
            Logging.log("ERROR",
                "Threading exception eStartThread => "
                + str(eStartThread))

    @staticmethod
    def format_data(data):
        data = re.match('(\[)(.*)(, )(.*)(, )(.*)(\])', data, re.M | re.I)
        if data is not None:
            return [data.group(2),data.group(4),data.group(6)]

    def beat(self):
        while(True):
            try:
                time.sleep(Heart.__timeout__)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.ip,self.port))
                sock.send('ping')
                data = sock.recv(1024)
                print('data => '+str(data))
                print('type(data) => '+str(type(data)))
                if not data or data is not None:
                    Heart.__pids__ = Heart.format_data(data)
                sock.close()
                Heart.__timeout__ = self.min_thresh_interval
            except Exception as e:
                print('Heart.__pids__ => '+str(Heart.__pids__))
                if Heart.__pids__:
                    Logging.log('INFO',
                        'Lost connection to the MotionDetection framework. Killing system now!')
                    [os.kill(int(pid), signal.SIGTERM) for pid in Heart.__pids__]
                    Heart.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                        'HeartBeat','HeartBeat reset program!')
                    Heart.__timeout__ = self.max_thresh_interval
                print('(Heart.beat) exception e => '+str(e))
                pass
            except OSError:
                print('(Heart.beat) exception OSError => '+str(OSError))
                pass

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', '--ip',
        dest='ip', default='0.0.0.0',
        help='This is the IP address of the server.')
    parser.add_option('-E', '--email-port',
        dest='email_port', type='int', default=587,
        help='E-mail port defaults to port 587')
    parser.add_option('-l', '--log-file',
        dest='logfile', default='/var/log/motiondetection.log',
        help='Log file defaults to /var/log/motiondetection.log.')
    parser.add_option('-D', '--disable-email',
        dest='disable_email', action='store_true', default=False,
        help='This option allows you to disable the sending of E-mails.')
    parser.add_option('-m', '--min-thresh-interval',
        dest='min_thresh_interval', type='int', default=10,
        help='This option sets the interval at which this heartbeat monitor '
            + 'checks the state of the motiondetection servers. This option '
            + 'defaults to 10 seconds. This variable is used if heartbeat is '
            + ' still has a connection to the motiondetection servers.')
    parser.add_option('-M', '--max-thresh-interval',
        dest='max_thresh_interval', type='int', default=120,
        help='This option sets the interval at which this heartbeat monitor '
            + 'checks the state of the motiondetection servers. This option '
            + 'defaults to 120 seconds. This variable is used if one of both '
            + ' of the servers are down and prevents a boot loop.')
    parser.add_option('-p', '--password',
        dest='password',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail password is used to send the pictures taken '
            + 'as well as notify you of motion detected.')
    parser.add_option('-e', '--email',
        dest='email',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail address is used to send the pictures taken as '
            + 'well as notify you of motion detected.')
    parser.add_option('-S', '--server-port',
        dest='port', type='int', default=50050,
        help='Heartbeat port defaults to port 50050.'
            + 'This is the port the heartbeat server runs on. '
            + 'This server takes in pid\'s from the motiondetection '
            + 'server and stores them in a list. If the heartbeat server '
            + 'loses connection with the motiondetection server then this '
            + 'heartbeat server will kill all pids in the list.')
    (options, args) = parser.parse_args()

    Mail.disabled = options.disable_email

    options_dict = {
        'email_port': options.email_port,
        'disable_email': options.disable_email,
        'ip': options.ip, 'port': options.port, 
        'max_thresh_interval': options.max_thresh_interval,
        'min_thresh_interval': options.min_thresh_interval,
        'email': options.email,'password':options.password
    }

    #time.sleep(210)
    time.sleep(10)
    heart = Heart(options_dict).beat() 
