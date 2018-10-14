#!/usr/bin/env python

import os
import re
import sys
import gzip
import time
import glob
import shutil
import smtplib
import logging
import tarfile
import logging.handlers

from optparse import OptionParser

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.mime.application import MIMEApplication

class Logging(object):

    @staticmethod
    def log(level,message,verbose=True):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/var/log/motiondetection.log"))
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
                    + " - ImageCapture - "
                    + str(message)))
        except IOError as eIOError:
            if re.search('\[Errno 13\] Permission denied:', str(eIOError), re.M | re.I):
                print("(ERROR) MotionDetection - Must be sudo to run MotionDetection!")
                sys.exit(0)
            print("(ERROR) MotionDetection - IOError in Logging class => " + str(eIOError))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection - IOError => "
                + str(eIOError)))
        except Exception as eLogging:
            print("(ERROR) MotionDetection Data Manager - Exception in Logging class => " + str(eLogging))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection - Exception => "
                + str(eLogging)))
            pass
        return

class Mail(object):
    @staticmethod
    def send(sender,to,password,port,subject,body,file_name=None):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            if file_name is not None:
                #message.attach(MIMEImage(file(file_name).read()))
                message.attach(MIMEApplication(file(file_name).read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            Logging.log("INFO", "(Mail.send) - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "(Mail.send) - Could not athenticate with password and username!")
        except Exception as e:
            Logging.log("ERROR", "(Mail.send) - Unexpected error in Mail.send() error e => " + str(e))
            pass

class FileOpts(object):

    def __init__(self,options_dict={}):
        self.email      = options_dict['email'] #'sshmonitorapp@gmail.com'
        self.password   = options_dict['password'] #'hkeyscwhgxjzafvj'
        self.log_file   = options_dict['log_file']
        self.log_size   = options_dict['log_size'] # 11
        self.file_count = options_dict['file_count'] # 50
        self.email_port = options_dict['email_port'] # 587

    def tar(self,file_name,*files):
        try:
            if self.file_size(self.log_file) >= self.log_size:
                with tarfile.open(file_name+'.tar', 'w') as tar:
                    for f in files:
                        if self.file_exists(f):
                            tar.add(f)
        except IOError as eIOError:
            if '[Errno 13] Permission denied' in str(eIOError):
                Logging.log('INFO', '(FileOpts.delete_file) - Must be root to delete this log!')
 
    def compress_file(self,file_name):
        if self.file_exists(self.log_file):
            try:
                if self.file_size(self.log_file) >= self.log_size:
                    with open(file_name,'rb') as in_file, gzip.open(file_name+'.gz','wb') as out_file:
                        shutil.copyfileobj(in_file,out_file)
            except OSError as eOSError:
                if '[Errno 13] Permission denied' in str(eOSError):
                    Logging.log('INFO', '(FileOpts.compress_file) - Must be root to compress this file!')
        else:
            Logging.log("INFO",
                "(FileOpts.compress_file) - Cannot compress file because it does not exist.")

    def file_size(self,file_name):
        if self.file_exists(file_name):
            return os.stat(file_name).st_size / 1024
        Logging.log("WARN",
            "(FileOpts.file_size) - Cannot get file size because file does not exist.")

    def delete_file(self,file_name):
        if self.file_exists(file_name):
            try:
                if '.tar.gz' in file_name:
                    Mail.send(self.email,self.email,self.password,self.email_port,'Motion Detected',
                        'MotionDecetor.py logfile compressed, E-mailed and deleted!', str(file_name))
                    os.remove(file_name)
                else:
                    os.remove(file_name)
            except OSError as eOSError:
                if '[Errno 13] Permission denied' in str(eOSError):
                    Logging.log('INFO', '(FileOpts.delete_file) - Must be root to delete this log!')
        else:
            Logging.log("INFO",
                "(FileOpts.delete_log) - Cannot delete file because it does not exist.")

    def file_exists(self,file_name):
        return os.path.isfile(file_name)

    def create_file(self,file_name):
        if self.file_exists(file_name):
            Logging.log("INFO", "(FileOpts.compress_file) - File " + str(file_name) + " exists.")
            return
        Logging.log("INFO", "(FileOpts.compress_file) - Creating file " + str(file_name) + ".")
        open(file_name, 'w')

    @staticmethod
    def picture_count():
        return len(glob.glob("/home/pi/.motiondetection/*.png"))

    @staticmethod
    def pictures():
        return glob.glob("/home/pi/.motiondetection/*.png")

    def main(self):
        self.tar(self.log_file,self.log_file)
        self.compress_file(self.log_file+'.tar')
        for f in ('motiondetection.log','motiondetection.log.tar','motiondetection.log.tar.gz'):
            self.delete_file('/var/log/'+str(f))


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-l", "--log-file",
        dest='log_file', default='/var/log/motiondetection.log',
        help="Log file to monitor. This defaults to /var/log/motiondetection.log.") 
    parser.add_option("-e", "--email",
        dest='email', type="str", default='sshmonitorapp@gmail.com',
        help="E-mail address to send notifications to. "
            + "This defaults to sshmonitorapp@gmail.com.") 
    parser.add_option("-p", "--password",
        dest='password', type="str", default='hkeyscwhgxjzafvj',
        help="Password used to authenticate with E-mail. This "
            + "is used to send notification E-mails to you.") 
    parser.add_option("-L", "--log-size",
        dest='log_size', type="int", default=1024,
        help="The log is deleted when it reaches the specified size. "
            + "This size is specified in Kb and defaults to 1Mb.") 
    parser.add_option("-c", "--file-count",
        dest='file_count', type="int", default=50,
        help="Compresses, E-mails, and deletes all motiondetection pictures "
            + " when their count reaches the specified file_count option.") 
    parser.add_option("-P", "--email-port",
        dest='email_port', type="int", default=587,
        help="The port for the E-mails to go out.") 
    (options, args) = parser.parse_args()

    options_dict = {
        'log_file': options.log_file, 'email': options.email,
        'password': options.password, 'log_size': options.log_size,
        'file_count': options.file_count, 'email_port': options.email_port 
    }

    FileOpts(options_dict).main()
