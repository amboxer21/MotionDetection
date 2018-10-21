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
import threading
import subprocess
import multiprocessing
import logging.handlers

import numpy as np

from PIL import Image
from pynetgear import Netgear
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
            print("(ERROR) MotionDetection - Exception in Logging class => " + str(eLogging))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection - Exception => " 
                + str(eLogging)))
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
                + ".png","rb").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            Logging.log("INFO", "(Mail.send) - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "(Mail.send) - Could not athenticate with password and username!")
        except TypeError as eTypeError:
            Logging.log("INFO", "(Mail.send) - Picture("
                + str(MotionDetection.img_num())
                + ".png) "
                + "TypeError => "
                + str(eTypeError))
            pass
        except Exception as e:
            Logging.log("ERROR", "(Mail.send) - Unexpected error in Mail.send() error e => " + str(e))
            pass

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
                    Logging.log("INFO",
                        '(CamHandler.do_GET) - (Queue message) -> Killing Live Feed!')
                    del(self.server.video_capture)
                    self.server.queue.put('close_camview')
                    self.server.sock.close()
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
                if not queue.empty() and queue.get() == 'close_camview':
                    CamHandler.lock.release()
                    queue.close()
                    break
                server.handle_request()
        except KeyboardInterrupt:
            CamHandler.lock.release()
            Stream.lock.release()
            queue.close()
            server.shutdown()
            server.server_close()
        except Exception as eThreadedHTTPServer:
            Logging.log("ERROR",
                "(Stream.stream_main) - eThreadedHTTPServer => "
                + str(eThreadedHTTPServer))
            queue.close()
            server.shutdown()
            server.server_close()

class MotionDetection(object):

    __metaclass__ = VideoFeed

    def __init__(self,options_dict={}):
        super(MotionDetection,self).__init__()

        self.tracker       = 0
        self.count         = 60

        self.ip              = options_dict['ip']
        self.fps             = options_dict['fps']
        self.email           = options_dict['email']
        self.netgear         = options_dict['netgear']
        self.password        = options_dict['password']
        self.email_port      = options_dict['email_port']
        self.access_list     = options_dict['access_list']
        self.server_port     = options_dict['server_port']
        self.cam_location    = options_dict['cam_location']

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
        if not FileOpts.file_exists('/home/pi/.motiondetection/capture1.png'):
            Logging.log("INFO", "(MotionDetection.img_num) - Creating capture1.png.")
            FileOpts.create_file('/home/pi/.motiondetection/capture1.png')
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            img_list.append(int(num.group(2)))
        return max(img_list)
    
    @staticmethod
    def take_picture(frame):
        picture_name = (
            '/home/pi/.motiondetection/capture' + str(MotionDetection.img_num() + 1) + '.png'
        )
        image = Image.fromarray(frame)
        image.save(picture_name)

    @staticmethod
    def start_thread(proc,*args):
        try:
            t = threading.Thread(target=proc,args=args)
            t.daemon = True
            t.start()
        except Exception as eStartThread:
            Logging.log("ERROR",
                "Threading exception eStartThread => " + str(eStartThread))

    def white_listed(self):
        if isinstance(self.netgear, Netgear):
            for device in self.netgear.get_attached_devices():
                if device.mac in open(self.access_list,'r').read():
                    return True
        return False

    def capture(self,queue=None):

        MotionDetection.lock.acquire()

        Logging.log("INFO", "(MotionDetection.capture) - Lock acquired!")
        Logging.log("INFO", "(MotionDetection.capture) - MotionDetection system initialized!")
    
        self.camera_motion = cv2.VideoCapture(self.cam_location)
        self.camera_motion.set(cv2.CAP_PROP_FPS, self.fps)

        (ret, previous_frame) = self.camera_motion.read()
        colored_frame  = previous_frame 
        previous_frame = cv2.cvtColor(previous_frame, cv2.COLOR_RGB2GRAY)
        previous_frame = cv2.GaussianBlur(previous_frame, (21, 21), 0)

        (ret, current_frame) = self.camera_motion.read()
        current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
        current_frame = cv2.GaussianBlur(current_frame, (21, 21), 0)

        while(True):

            if not queue.empty() and queue.get() == 'start_monitor':
                Logging.log("INFO",
                    "(MotionDetection.capture) - (Queue message) -> Killing camera.")
                del(self.camera_motion)
                queue.close()
                MotionDetection.lock.release()
                break

            time.sleep(0.1)

            frame_delta = cv2.absdiff(previous_frame, current_frame)
            #(ret, frame_delta) = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY) # Original values
            (ret, frame_delta) = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
            frame_delta = cv2.dilate(frame_delta,np.ones((5,5), np.uint8),iterations=1)
            frame_delta = cv2.normalize(frame_delta, None, 0, 255, cv2.NORM_MINMAX)
            delta_count = cv2.countNonZero(frame_delta)

            if delta_count > self.motion_thresh_min and delta_count < self.motion_thresh_max:
                self.tracker += 1
                if self.tracker >= 60 or self.count >= 60:
                    self.count = 0
                    self.tracker = 0
                    Logging.log("INFO",
                        "(MotionDetection.capture) - Motion detected with threshold levels at "+str(delta_count)+"!")
                    self.take_picture(colored_frame)
                    MotionDetection.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                        'Motion Detected','MotionDecetor.py detected movement!')
                    # Access list feature
                    '''if not self.white_listed(delta_count,colored_frame):
                        Logging.log("INFO",
                            "(MotionDetection.capture) - Motion detected with threshold levels at "+str(delta_count)+"!")
                        self.take_picture(colored_frame)
                        MotionDetection.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                            'Motion Detected','MotionDecetor.py detected movement!')'''
            elif delta_count < 500:
                self.count += 1
                self.tracker = 0

            previous_frame = current_frame
            (ret, current_frame) = self.camera_motion.read()
            colored_frame  = current_frame 
            current_frame  = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
            current_frame  = cv2.GaussianBlur(current_frame, (21, 21), 0)

class FileOpts(object):
  
    @staticmethod
    def file_exists(file_name):
        return os.path.isfile(file_name)

    @staticmethod
    def create_file(file_name):
        if FileOpts.file_exists(file_name):
            Logging.log("INFO", "(FileOpts.compress_file) - File " + str(file_name) + " exists.")
            return
        Logging.log("INFO", "(FileOpts.compress_file) - Creating file " + str(file_name) + ".")
        open(file_name, 'w')

class Server(MotionDetection):

    __metaclass__ = VideoFeed

    def __init__(self,queue):
        super(Server, self).__init__(options_dict)

        self.queue = queue

        self.process = multiprocessing.Process(
            target=MotionDetection(options_dict).capture,name='capture',args=(queue,)
        )
        self.process.daemon = True
        self.process.start()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.server_port))
        except Exception as eSock:
            Logging.log("ERROR", "(Server.__init__) - eSock error e => " + str(eSock))

    def handle_incoming_message(self,*messages):
        for(message,queue) in messages:
            if(message == 'start_monitor'):
                Logging.log("INFO",
                    "(Server.handle_incoming_message) - Starting camera! -> (start_monitor)")
                queue.put('start_monitor')
                Server.lock.acquire()
                if self.process.name == 'capture':
                    Logging.log("INFO",
                        "(Server.handle_incoming_message) - Terminating "
                        + str(self.process.name)
                        + " process")
                    self.process.terminate()
                Server.lock.release()
                self.proc = multiprocessing.Process(
                    target=Stream().stream_main,name='stream_main',args=(queue,)
                )
                self.proc.daemon = True
                self.proc.start()
            elif(message == 'kill_monitor'):
                Logging.log("INFO",
                    "(Server.handle_incoming_message) - Killing camera! -> (kill_monitor)")
                queue.put('kill_monitor')
                Server.lock.acquire()
                if self.process.name == 'stream_main':
                    Logging.log("INFO",
                        "(Server.handle_incoming_message) - Terminating "
                        + str(self.process.name)
                        + " process")
                    self.process.terminate()
                Server.lock.release()
                self.process = multiprocessing.Process(
                    target=MotionDetection(options_dict).capture,name='capture',args=(queue,)
                )
                self.process.daemon = True
                self.process.start()
            else:
                pass
                #con.send(message + " is not a known command!")

    def server_main(self):

        Logging.log("INFO", "(Server.server_main) - Listening for connections.")

        while(True):
            time.sleep(0.05)
            try:
                self.sock.listen(10)
                (con, addr) = self.sock.accept()
                Logging.log("INFO",
                    "(Server.server_main) - Received connection from " + str(addr))

                Server.handle_incoming_message(self,(con.recv(1024),self.queue))

            except KeyboardInterrupt:
                print("\n")
                Logging.log("INFO", "(Server.server_main) - Caught control + c, exiting now.")
                print("\n")
                sys.exit(0)
            except Exception as eAccept:
                Logging.log("ERROR", "(Server.server_main) - Socket accept error: " + str(eAccept))

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
        dest='email', type="str",
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
    parser.add_option("-l", "--log-file",
        dest='logfile', default='/var/log/motiondetection.log',
        help="Tail log defaults to /var/log/motiondetection.log.")
    parser.add_option("-f", "--fps",
        dest='fps', type="int", default='30',
        help='"This sets the frames per second for the motion '
            + 'capture system. It defaults to 30 frames p/s."')
    parser.add_option("-w", "--white-list",
        dest='access_list', default='/home/pi/.motiondetection/access_list',
        help='"This ensures that the MotionDetection system does not run '
            + 'if the mac is in the access_list. This defaults to '
            + '/home/pi/.motiondetection/access_list"')
    parser.add_option("-m", "--motion-threshold-min",
        dest='motion_thresh_min', type="int", default=1500,
        help='"Sets the minimum movement threshold '
            +'to trigger the programs image capturing routine.'
            +' The default value is set at 1500."')
    parser.add_option("-M", "--motion-threshold-max",
        dest='motion_thresh_max', type="int", default=10000,
        help='"Sets the maximum movement threshold when the '
            +'programs image capturing routine stops working.'
            +' The default value is set at 10000."')
    parser.add_option("-r", "--router-password",
        dest='router_password', default='password',
        help='"This option is your routers password. This is used to '
            + 'circumvent the motiondetection system. If your phone is '
            + 'connected to your router and in the access list. The '
            + 'MotionDetection system will not run."')
    (options, args) = parser.parse_args()

    netgear = 'netgear'
    #netgear = Netgear(password=options.router_password)

    if not FileOpts.file_exists('/var/log/motiondetection.log'):
        FileOpts.create_file('/var/log/motiondetection.log')

    options_dict = {
        'netgear': netgear,
        'logfile': options.logfile, 'fps': options.fps,
        'server_port': options.server_port, 'email': options.email,
        'motion_thresh_max': options.motion_thresh_max, 'ip': options.ip, 
        'password': options.password, 'cam_location': options.cam_location,
        'email_port': options.email_port, 'camview_port': options.camview_port,
        'access_list': options.access_list, 'motion_thresh_min': options.motion_thresh_min
    }

    motion_detection = MotionDetection(options_dict)
    Server(multiprocessing.Queue()).server_main()
