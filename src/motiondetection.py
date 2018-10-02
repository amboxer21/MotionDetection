#!/usr/bin/env python

import re
import os
import cv2
import sys
import cgi
import time
import glob
import socket
import smtplib
import logging
import StringIO
import subprocess
import multiprocessing
import logging.handlers

from PIL import Image
from optparse import OptionParser

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart

from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class Accepts(object):

    @classmethod
    def boolean(cls,func):
        arg_count = func.__code__.co_argcount
        def wrapper(*args):
            for arg in args:
                if re.search(r'<__main__',str(arg)) is not None:
                    pass
                elif not isinstance(arg, bool):
                    raise TypeError('"' + str(arg) + '" is not a bool type!')
            if int(arg_count) > 1:
                return func(cls,args)
            return func(args)
        return wrapper
    
    @classmethod
    def integer(cls,func):
        arg_count = func.__code__.co_argcount
        def wrapper(*args):
            for arg in args:
                if re.search(r'<__main__',str(arg)) is not None:
                    pass
                elif not isinstance(arg, int):
                    raise TypeError('"' + str(arg) + '" is not an integer!')
            if int(arg_count) > 1:
                return func(cls,args)
            return func(args)
        return wrapper
    
    @classmethod
    def string(cls,func):
        arg_count = func.__code__.co_argcount
        def wrapper(*args):
            for arg in args:
                if re.search(r'<__main__',str(arg)) is not None:
                    pass
                elif not isinstance(arg, str):
                    raise TypeError('"' + str(arg) + '" is not a string!')
            if int(arg_count) > 1:
                return func(cls,args)
            return func(args)
        return wrapper

    @classmethod
    def tuple(cls,func):
        arg_count = func.__code__.co_argcount
        def wrapper(*args):
            for arg in args:
                if re.search(r'<__main__',str(arg)) is not None:
                    pass
                elif not isinstance(args, tuple):
                    raise TypeError('"' + str(arg) + '" is not a tuple!')
                else:
                    if int(arg_count) > 1:
                        return func(cls,arg)
                    return func(arg)
        return wrapper

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

class User(object):
    @staticmethod
    def name():
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()

class Time(object):
    @staticmethod
    def now():
        return time.asctime(time.localtime(time.time()))

class Mail(object):
    @staticmethod
    def send(sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            message.attach(MIMEImage(file("/home/pi/.motiondetection/capture"
                + str(MotionDetection.img_num())
                + ".png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            Logging.log("INFO", "(Mail.send) - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "(Mail.send) - Could not athenticate with password and username!")
        except Exception as e:
            Logging.log("ERROR", "(Mail.send) - Unexpected error in Mail.send() error e => " + str(e))

# Metaclass for locking video camera
class VideoFeed(type):

    __classes__ = []

    def __new__(meta,name,bases,dct):
        VideoFeed.__classes__.append(name)
        if not hasattr(meta,'lock'):
            meta.lock = multiprocessing.Lock()
        return super(VideoFeed, meta).__new__(meta, name, bases, dct)

    def __init__(cls,name,bases,dct):
        if not hasattr(cls,'lock'):
            Logging.log("INFO", 'Passing "Lock" object to class "'+cls.__name__+'"')
            cls.lock = multiprocessing.Lock()
        super(VideoFeed,cls).__init__(name,bases,dct)

class CamHandler(BaseHTTPRequestHandler,object):

    __metaclass__ = VideoFeed

    def do_GET(self):
        try:
            CamHandler.lock.acquire()
            Logging.log("INFO", "(CamHandler.do_GET) - Lock acquired!")
            if self.path.endswith('.mjpg'):
                self.rfile._sock.settimeout(1)
                self.send_response(200)
                self.send_header('Content-type',
                    'multipart/x-mixed-replace; boundary=--jpgboundary')
                self.end_headers()
            while True:
                if not self.server.queue.empty() and self.server.queue.get() == 'kill_monitor':
                    Logging.log("INFO",'(CamHandler.do_GET) - (Queue message) -> Killing Live Feed!')
                    del(self.server.video_capture)
                    self.server.queue.put('close_camview')
                    CamHandler.lock.release()
                    break
                (read_cam, image) = self.server.video_capture.read()
                if not read_cam:
                    continue
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
            del(self.server.video_capture)
            CamHandler.lock.release()
        except Exception as e:
            if re.search('[Errno 32] Broken pipe',str(e), re.M | re.I):
                Logging.log("WARN", "(CamHandler.do_GET) - [Errno 32] Broken pipe.")
        return CamHandler

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, queue, video_capture, bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.queue = queue
        self.video_capture = video_capture
        HTTPServer.allow_reuse_address = True

class Stream(object):

    __metaclass__ = VideoFeed

    def stream_main(self,queue=None):
        Stream.lock.acquire()
        Logging.log("INFO", "(Stream.stream_main) - Lock acquired!")
        try:
            video_capture = cv2.VideoCapture(0)
            video_capture.set(3,320)
            video_capture.set(4,320)
            Stream.lock.release()
            Logging.log("INFO", "(Stream.stream_main) - Streaming HTTPServer started")
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler,queue,video_capture)
            server.timeout = 1
            server.queue = queue
            server.video_capture = video_capture
            del(video_capture)
            while(True):
                server.handle_request()
                if not queue.empty() and queue.get() == 'close_camview':
                    queue.close()
                    break
        except KeyboardInterrupt:
            Stream.lock.release()
            server.shutdown()
            server.server_close()
        except Exception as eThreadedHTTPServer:
            pass

class MotionDetection(object):

    __metaclass__ = VideoFeed

    def __init__(self,options_dict={}):
        super(MotionDetection,self).__init__()

        self.count         = 120
        self.tracker       = 120
        self.stop_motion   = False 
        self.kill_camera   = False 
        self.stream_camera = False 

        self.ip            = options_dict['ip']
        self.email         = options_dict['email']
        self.password      = options_dict['password']
        self.email_port    = options_dict['email_port']
        self.server_port   = options_dict['server_port']
        self.cam_location  = options_dict['cam_location']

        self.motion_thresh_min = options_dict['motion_thresh_min']
        self.motion_thresh_max = options_dict['motion_thresh_max']

        if self.email is None or self.password is None:
            Logging.log("ERROR",
                "(MotionDetection.__init__) - Both E-mail and password are required!")
            parser.print_help()
            sys.exit(0)

    @staticmethod
    def img_num():
        img_list = []
        os.chdir("/home/pi/.motiondetection/")
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            img_list.append(int(num.group(2)))
        return max(img_list)
    
    def take_picture(self):
        camera = cv2.VideoCapture(self.cam_location)
        if not camera.isOpened():
            return
        (ret, frame) = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.5)
        picture_name = "/home/pi/.motiondetection/capture" + str(MotionDetection.img_num() + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        del(camera)

    def capture(self,queue=None):

        MotionDetection.lock.acquire()

        Logging.log("INFO", "(MotionDetection.capture) - Lock acquired!")
        Logging.log("INFO", "(MotionDetection.capture) - MotionDetection system initialized!")
    
        self.camera_motion = cv2.VideoCapture(self.cam_location)

        frame_now = self.camera_motion.read()[1]
        frame_now = self.camera_motion.read()[1]

        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)
        frame_prior = frame_now

        while(True):

            if not queue.empty() and queue.get() == 'start_monitor':
                Logging.log("INFO",
                    "(MotionDetection.capture) - (Queue message) -> Killing camera.")
                del(self.camera_motion)
                queue.close()
                MotionDetection.lock.release()
                break
      
            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
             
            if delta_count > self.motion_thresh_min and delta_count < self.motion_thresh_max:
                self.tracker += 1
                if self.count >= 60:
                    # Reset counter
                    self.count = 0
                    # Reset tracker
                    self.tracker = 0
                    del(self.camera_motion)
                    self.take_picture()
                    self.camera_motion = cv2.VideoCapture(self.cam_location)
                    Mail.send(self.email,self.email,self.password,self.email_port,
                        'Motion Detected','MotionDecetor.py detected movement!')
                elif self.tracker >= 60:
                    # Reset tracker
                    self.tracker = 0
                    del(self.camera_motion)
                    self.take_picture()
                    self.camera_motion = cv2.VideoCapture(self.cam_location)
                    Mail.send(self.email,self.email,self.password,self.email_port,
                        'Motion Detected','MotionDecetor.py detected movement!')
            elif delta_count < 100:
                self.count += 1
                # Reset tracker
                self.tracker = 0
                time.sleep(0.1)

            # keep the frames moving.
            frame_prior = frame_now
            frame_now = self.camera_motion.read()[1]
            frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
            frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)

class Server(MotionDetection):

    __metaclass__ = VideoFeed

    def __init__(self):
        super(Server, self).__init__(options_dict)

        try:
            self.sock = socket.socket()
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.server_port))
        except Exception as eSock:
            Logging.log("ERROR", "(Server.__init__) - eSock error e => " + str(eSock))

    @Accepts.tuple
    def handle_incoming_message(*messages):
        process = None
        for(ret, (message,queue)) in enumerate(messages):
            if(message == 'start_monitor'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Starting camera! -> (start_monitor)")
                if process is not None:
                    if process.name() == 'capture':
                        process.close()
                queue.put('start_monitor')
                process = multiprocessing.Process(target=Stream().stream_main, name='stream_main', args=(queue,))
                process.daemon = True
                process.start()
            elif(message == 'kill_monitor'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Killing camera! -> (kill_monitor)")
                if process is not None:
                    if process.name() == 'stream_main':
                        process.close()
                queue.put('kill_monitor')
                process = multiprocessing.Process(target=MotionDetection(options_dict).capture, name='capture',args=(queue,))
                process.daemon = True
                process.start()
            else:
                pass
                #con.send(message + " is not a known command!")

    def server_main(self,queue=None):

        Logging.log("INFO", "(Server.server_main) - Listening for connections.")

        process = multiprocessing.Process(target=MotionDetection(options_dict).capture, name='init',args=(queue,))
        process.daemon = True
        process.start()

        while(True):
            time.sleep(0.05)
            try:
                self.sock.listen(5)
                (con, addr) = self.sock.accept()
                Logging.log("INFO", "(Server.server_main) - Received connection from " + str(addr))

                self.handle_incoming_message((con.recv(1024),queue))

            except KeyboardInterrupt:
                print("\n")
                Logging.log("INFO", "(Server.server_main) - Caught control + c, exiting now.")
                print("\n")
                sys.exit(0)
            except Exception as eAccept:
                Logging.log("ERROR", "(Server.server_main) - Socket accept error: " + str(eAccept))
        con.close()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-i", "--ip",
        dest='ip', default='0.0.0.0',
        help='"This is the IP address of the server."')
    parser.add_option("-S", "--server-port",
        dest='server_port', type="int", default=50050,
        help='"Server port defaults to port 50050"')
    parser.add_option("-C", "--camview-port",
        dest='camview_port', type="int", default=5000,
        help='"CamView port defaults to port 5000"')
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
    parser.add_option("-m", "--motion-threshold-min",
        dest='motion_thresh_min', type="int", default=1300,
        help='"Sets the minimum movement threshold '
            +'to trigger the programs image capturing routine.'
            +' The default value is set at 1300."')
    parser.add_option("-M", "--motion-threshold-max",
        dest='motion_thresh_max', type="int", default=10000,
        help='"Sets the maximum movement threshold when the '
            +'programs image capturing routine stops working.'
            +' The default value is set at 10000."')
    (options, args) = parser.parse_args()

    options_dict = {
        'motion_thresh_min': options.motion_thresh_min, 'motion_thresh_max': options.motion_thresh_max,
        'ip': options.ip, 'server_port': options.server_port, 'email': options.email, 'password': options.password,
        'cam_location': options.cam_location, 'email_port': options.email_port, 'camview_port': options.camview_port
    }

    motion_detection = MotionDetection(options_dict)
    Server().server_main(multiprocessing.Queue())
