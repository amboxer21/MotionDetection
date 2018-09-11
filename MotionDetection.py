#!/usr/bin/env python

import re
import os
import cv2
import sys
import time
import glob
import socket
import smtplib
import logging
import StringIO
import threading
import subprocess
import logging.handlers

import modules.datetime.datetime as datetime

from PIL import Image
from __init__ import *
from optparse import OptionParser

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart

from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

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
                print(level + " is not a level. Use: WARN, ERROR, or INFO!")
                return
            elif comm.group() == 'ERROR':
                logging.error("(" + str(level) + ") " + "ImageCapture - " + str(message))
            elif comm.group() == 'INFO':
                logging.info("(" + str(level) + ") " + "ImageCapture - " + str(message))
            elif comm.group() == 'WARN':
                logging.warn("(" + str(level) + ") " + "ImageCapture - " + str(message))
            # Print to stdout only if the verbose option is passed or log level = ERROR.
            if verbose or str(level) == 'ERROR':
                print("(" + str(level) + ") " + "ImageCapture - " + str(message))
        except IOError as e:
            if re.search('\[Errno 13\] Permission denied:', str(e), re.M | re.I):
                print("(ERROR) ImageCapture - Must be sudo to run ImageCapture!")
                sys.exit(0)
            print("(ERROR) ImageCapture - IOError in Logging class => " + str(e))
            logging.error("(ERROR) ImageCapture - IOError => " + str(e))
        except Exception as e:
            print("(ERROR) ImageCapture - Exception in Logging class => " + str(e))
            logging.error("(ERROR) ImageCapture - Exception => " + str(e))
            pass
        return

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
        while True:
            try:
                (read, image) = self.streamCamera.read()
                #if not read:
                    #continue
                if self.killCamera is True:
                    Logging.log("INFO","Killing cam.")
                    del(self.streamCamera)
                    break
                rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(rgb)
                jpg_file = StringIO.StringIO()
                jpg.save(jpg_file,'JPEG')
                self.wfile.write("--jpgboundary")
                self.send_header('Content-type','image/jpeg')
                self.send_header('Content-length',str(jpg_file.len))
                self.end_headers()
                jpg.save(self.wfile,'JPEG')
                time.sleep(0.05)
            except KeyboardInterrupt:
                del(self.streamCamera)
                break
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Stream(object):
    def __init__(self):
        self.streamCamera = cv2.VideoCapture(self.cam_location)
        self.streamCamera.set(3,320)
        self.streamCamera.set(4,320)
        try:
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            Logging.log("INFO", "Streaming HTTPServer started")
            server.serve_forever()
        except KeyboardInterrupt:
            del(self.streamCamera)
            server.socket.close()
        except Exception as eThreadedHTTPServer:
            pass

class MotionDetection(object):

    def __init__(self):
        self.cam = None
        self.stopMotion = False
        self.is_sent = False
        self.cam_deleted = False
        pass

    def user_name(self):
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()
    
    def now(self):
        return time.asctime(time.localtime(time.time()))
    
    def img_num(self):
        _list = []
        os.chdir("/home/pi/.motiondetection/")
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(int(num.group(2)))
        return max(_list)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            #message.attach(MIMEImage(file("/home/" + self.user_name() + "/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            message.attach(MIMEImage(file("/home/pi/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            Logging.log("INFO", "Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "Could not athenticate with password and username!")
        except Exception as e:
            Logging.log("ERROR", "Unexpected error in sendMail() error e => " + str(e))
    
    def notify(self):
        if self.is_sent is not True:
            self.sendMail(self.email,self.email,self.password,self.email_port,'Motion Detected','MotionDecetor.py detected movement!')
            self.is_sent = True
    
    def takePicture(self):
        camera = cv2.VideoCapture(self.cam_location)
        if not camera.isOpened():
            return
        (ret, frame) = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.1)
        picture_name = "/home/pi/.motiondetection/capture" + str(self.img_num() + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        del(camera)

    def kill_cam(self):
        Logging.log("INFO", "def kill_cam(self):")
        self.killCamera = True

    def capture(self):
        Logging.log("INFO", "Motion Detection system initialed!")
    
        count     = 0
        is_moving = True
    
        self.cam  = cv2.VideoCapture(self.cam_location)

        frame_now = self.cam.read()[1]
        frame_now = self.cam.read()[1]

        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)
        frame_prior = frame_now
    
        while(True):

            if self.killCamera is True or self.stopMotion:
                Logging.log("INFO", "Killing cam.")
                del(self.cam)
                break
      
            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
             
            if(delta_count > 1300 and delta_count < 10000 and is_moving is True):
                count = 0
                is_moving = False
                Logging.log("INFO", "MOVEMENT: " + self.now() + ", Delta: " + str(delta_count))
                del(self.cam)
                self.cam_deleted = True
                self.takePicture()
                self.notify()
            elif delta_count < 100:
                count += 1
                time.sleep(0.1)
                is_moving = True
                #Logging.log("INFO", "count: " + str(count))
                if count == 120:
                    Logging.log("INFO", "Resetting counter.")
                    count = 0
                    self.is_sent = False
    
            if self.cam_deleted:
                self.cam = cv2.VideoCapture(self.cam_location)
    
                self.cam_deleted = False
    
            # keep the frames moving.
            frame_prior = frame_now
            frame_now = self.cam.read()[1]
            frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
            frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)

class Server(MotionDetection, Stream):

    def __init__(self, options_dict={}):
        super(Server, self).__init__()

        self.killCamera = False
        self.streamCamera = False
        self.sock = socket.socket()

        self.ip = options_dict['ip']
        self.email = options_dict['email']
        self.password = options_dict['password']
        self.email_port = options_dict['email_port']
        self.server_port = options_dict['server_port']
        self.cam_location = options_dict['cam_location']

        if self.email is None or self.password is None:
            Logging.log("ERROR", "Both E-mail and password are required!")
            parser.print_help()
            sys.exit(0)

    def start_thread(self, proc):
        try:
            t = threading.Thread(target=proc)
            t.daemon = True
            t.start()
        except Exception as eStartThread:
            Logging.log("ERROR", "Threading exception eStartThread => " + str(eStartThread))

    def main(self):

        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', self.server_port))
            self.sock.listen(5)
            time.sleep(1)
            self.start_thread(self.capture)
            time.sleep(1)
        except Exception as eSock:
            Logging.log("ERROR", "Sock exception eSock => " + str(eSock))

        Logging.log("INFO", "Listening for connections.")
        while(True):
            time.sleep(0.05)
            try:
                (con, addr) = self.sock.accept()
                Logging.log("INFO", "Received connection from " + str(addr))
                message = con.recv(1024)

                if(message == 'start_monitor'):
                    Logging.log("INFO", "Starting camera!")
                    #con.send("Starting camera!")
                    self.killCamera = True
                    time.sleep(1)
                    self.killCamera = False
                    self.start_thread(stream.main)
                elif(message == 'kill_monitor'):
                    Logging.log("INFO", "Killing camera!")
                    #con.send("Killing camera!")
                    self.killCamera = True
                    time.sleep(1)
                    self.killCamera = False
                    self.start_thread(self.capture)
                elif(message == 'start_motion'):
                    Logging.log("INFO", "Starting motion sensor!")
                    self.killCamera = True
                    time.sleep(1)
                    self.stopMotion = False
                    self.killCamera = False
                    self.start_thread(self.capture)
                    #con.send("Starting motion sensor!")
                elif(message == 'kill_motion'):
                    Logging.log("INFO", "Killing motion sensor!")
                    self.stopMotion = True
                    self.killCamera = True
                    time.sleep(1)
                    #con.send("Killing motion sensor!")
                elif(message == 'probe'):
                    Logging.log("INFO", "Server is alive.")
                    #con.send("Server is alive.")
                else:
                    Logging.log("ERROR", message + " is not a known command.")
                    #con.send(message + " is not a konwn command!")
            except KeyboardInterrupt:
                print("\n")
                Logging.log("INFO", "Caught control + c, exiting now.")
                print("\n")
                sys.exit(0)
            except Exception as eAccept:
                Logging.log("ERROR", "Socket accept error: " + str(eAccept))
        con.close()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-i", "--ip",
        dest='ip', default='0.0.0.0',
        help='"This is the IP address of the server."')
    parser.add_option("-S", "--server-port",
        dest='server_port', type="int", default=50050,
        help='"Server port defaults to port 50050"')
    parser.add_option("-e", "--email",
        dest='email',
        help='"This argument is required!"')
    parser.add_option("-p", "--password",
        dest='password',
        help='"This argument is required!"')
    parser.add_option("-c", "--camera-location",
        dest='cam_location', type="int", default=0,
        help='"Camera index number."')
    parser.add_option("-E", "--email-port",
        dest='email_port', type="int", default=587,
        help='"E-mail port defaults to port 587"')
    (options, args) = parser.parse_args()

    options_dict = {
        'ip': options.ip, 'server_port': options.server_port,
        'email': options.email, 'password': options.password,
        'cam_location': options.cam_location, 'email_port': options.email_port
    }

    server = Server(options_dict)
    server.main()
