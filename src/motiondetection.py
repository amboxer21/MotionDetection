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
        if not hasattr(meta,'video_capture'):
            meta.video_capture = cv2.VideoCapture(0)
            meta.video_capture.set(3,320)
            meta.video_capture.set(4,320)
        return super(VideoFeed, meta).__new__(meta, name, bases, dct)

    def __init__(cls,name,bases,dct):
        if not hasattr(cls,'video_capture'):
            Logging.log("INFO", 'Passing videocapture object to class "'+cls+'"')
            cls.video_capture = meta.video_capture
        super(VideoFeed,cls).__init__(name,bases,dct)

    def video_feed(cls):
        return VideoFeed.video_capture
 
    def release(cls):
        Logging.log("INFO", "(VideoFeed.release) - Releasing camera from "+cls.__name__+" class!")
        if hasattr(cls,'video_capture'):
            try:
                del(cls.video_capture)
                delattr(cls,'video_capture')
                Logging.log("INFO", "video_capture attribute deleted from class '"+cls.__name__+"'")
            except AttributeError:
                pass

class Queue(object):
    def queue_process(self,func,queue=None):
        try:
            process = multiprocessing.Process(target=func, args=(queue,))
            process.start()
        except Exception as eQueueProcess:
            Logging.log("ERROR",
                "(Queue.queue_process) - Queue exception eQueueProcess => " + str(eQueueProcess))

class CamHandler(BaseHTTPRequestHandler,object):

    __metaclass__ = VideoFeed

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.rfile._sock.settimeout(10)
            self.send_response(200)
            self.send_header('Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
        while True:
            try:
                (read_cam, image) = self.server.video_capture.read()
                if not read_cam:
                    continue
                if not self.server.queue.empty() and self.server.queue.get() == 'kill_monitor':
                    Logging.log("INFO",'(CamHandler.do_GET) - Killing CamView feed!')
                    CamHandler.release()
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
                CamHandler.release()
                break
            except Exception as e:
                if re.search('[Errno 32] Broken pipe',str(e), re.M | re.I):
                    Logging.log("WARN", "(CamHandler.do_GET) - [Errno 32] Broken pipe.")
                    break
                pass
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, queue, video_capture, bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.queue = queue
        self.video_capture = video_capture 

class Stream(object):

    #__metaclass__ = VideoFeed

    def stream_main(self,queue=None):
        try:
            Logging.log("INFO", "(Stream.stream_main) - Streaming HTTPServer started")
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler,queue)
            server.timeout = 2
            server.queue = queue
            server.video_capture = cv2.VideoCapture(0)
            server.video_capture.set(3,320)
            server.video_capture.set(4,320)
            server.serve_forever()
        except KeyboardInterrupt:
            Stream.release()
            server.server_close()
        except Exception as eThreadedHTTPServer:
            print("(Stream.stream_main) - Exception eThreadedHTTPServer => "
                + str(eThreadedHTTPServer))

class MotionDetection(object):

    #__metaclass__ = VideoFeed

    def __init__(self,options_dict={},global_vars_dict={}):
        super(MotionDetection,self).__init__()
        self.ip            = options_dict['ip']
        self.email         = options_dict['email']
        self.password      = options_dict['password']
        self.email_port    = options_dict['email_port']
        self.server_port   = options_dict['server_port']
        self.cam_location  = options_dict['cam_location']

        self.count         = global_vars_dict['count']
        self.is_sent       = global_vars_dict['is_sent']
        self.is_moving     = global_vars_dict['is_moving']
        self.cam_deleted   = global_vars_dict['cam_deleted'] 
        self.stop_motion   = global_vars_dict['stop_motion'] 
        self.kill_camera   = global_vars_dict['kill_camera'] 
        self.stream_camera = global_vars_dict['stream_camera']

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
        camera = MotionDetection.video_capture
        if not camera.isOpened():
            return
        (ret, frame) = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.5)
        picture_name = "/home/pi/.motiondetection/capture" + str(MotionDetection.img_num() + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        MotionDetection.release()

    @Accepts.boolean
    def stream_camera(self,value):
        Logging.log("INFO", "(MotionDetection.stream_camera) - " + value + "):")
        self.stream_camera = value

    @Accepts.boolean
    def stop_motion(self,value):
        Logging.log("INFO", "(MotionDetection.stop_motion) - " + value + "):")
        self.stop_motion = value

    @Accepts.boolean
    def kill_camera(self,value):
        Logging.log("INFO", "(MotionDetection.kill_camera) - " + value + "):")
        self.kill_camera = value

    def capture(self,queue=None):

        Logging.log("INFO", "(MotionDetection.capture) - Motion Detection system initialed!")
    
        #self.camera_motion = MotionDetection.video_capture
        self.camera_motion = cv2.VideoCapture(0)
        self.camera_motion.set(3,320)
        self.camera_motion.set(4,320)
        time.sleep(1)

        frame_now = self.camera_motion.read()[1]
        frame_now = self.camera_motion.read()[1]

        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)
        frame_prior = frame_now

        while(True):

            if not queue.empty() and queue.get() == 'start_monitor':
                Logging.log("INFO", "(MotionDetection.capture) - (Queue message) -> Killing camera.")
                MotionDetection.release()
                break
      
            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
             
            if(self.is_moving is True
                and delta_count > self.motion_thresh_min
                and delta_count < self.motion_thresh_max):
                    count = 0
                    self.is_moving = False
                    Logging.log("INFO", "(MotionDetection.capture) - MOVEMENT: "
                        + Time.now()
                        + ", Delta: "
                        + str(delta_count))
                    MotionDetection.release()
                    self.take_picture()
                    self.camera_motion = MotionDetection.video_capture
                    if not self.is_sent:
                        Mail.send(self.email,self.email,self.password,
                            self.email_port,'Motion Detected','MotionDecetor.py detected movement!')
                        self.is_sent = True
            elif delta_count < 100:
                self.count += 1
                time.sleep(0.1)
                self.is_moving = True
                #Reset counter
                if self.count == 120:
                    print('Resetting counter!')
                    self.count = 0
                    self.is_sent = False
    
            # keep the frames moving.
            frame_prior = frame_now
            frame_now = self.camera_motion.read()[1]
            frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
            frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)

class Server(MotionDetection):

    __metaclass__ = VideoFeed

    def __init__(self):
        super(Server, self).__init__(options_dict,global_vars_dict)

        try:
            self.sock = socket.socket()
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.server_port))
        except Exception as eSock:
            print("eSock error e => " + str(eSock))

    @Accepts.tuple
    def handle_incoming_message(*messages):
        for(ret, (message,queue)) in enumerate(messages):
            if(message == 'start_monitor'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Starting camera! -> (start_monitor)")
                queue.put('start_monitor')
                Queue().queue_process(Stream().stream_main,queue)
            elif(message == 'kill_monitor'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Killing camera! -> (kill_monitor)")
                queue.put('kill_monitor')
                CamHandler.release()
                Queue().queue_process(MotionDetection(options_dict,global_vars_dict).capture,queue)
            elif(message == 'start_motion'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Starting motion sensor! -> (start_motion)")
                queue.put('start_motion')
            elif(message == 'kill_motion'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Killing motion sensor! -> (kill_motion)")
                queue.put('kill_motion')
            elif(message == 'probe'):
                Logging.log("INFO", "(Server.handle_incoming_message) - Server is alive -> (probe).")
                queue.put('probe')
            else:
                pass
                #con.send(message + " is not a konwn command!")

    def server_main(self,queue=None):

        Logging.log("INFO", "(Server.server_main) - Listening for connections.")

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
        'ip': options.ip, 'server_port': options.server_port,
        'email': options.email, 'password': options.password,
        'cam_location': options.cam_location, 'email_port': options.email_port,
        'motion_thresh_min': options.motion_thresh_min, 
        'motion_thresh_max': options.motion_thresh_max
    }

    global_vars_dict = {
        'count': 0, 'is_sent': False, 'is_moving': True, 'cam_deleted': False,
        'stop_motion': False, 'kill_camera': False, 'stream_camera': False,
    }

    queue  = Queue()
    server = Server()
    stream = Stream()
    motion_detection = MotionDetection(options_dict,global_vars_dict)

    multiprocessing_queue = multiprocessing.Queue()
    queue.queue_process(server.server_main,multiprocessing_queue)
    #queue.queue_process(motion_detection.capture,multiprocessing_queue)
    #queue.queue_process(stream.stream_main,multiprocessing_queue)
