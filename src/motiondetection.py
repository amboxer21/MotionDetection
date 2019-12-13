#!/usr/bin/env python

import re
import os
import cv2
import sys
import time
import glob
import email
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
                    + " - ImageCapture - "
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

    __disabled__ = False

    @staticmethod
    def send(sender,to,password,port,subject,body):
        try:
            if not Mail.__disabled__:
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
                Logging.log("INFO", "(Mail.send) - Sent email successfully!")
            else:
                Logging.log("WARN", "(Mail.send) - Sending mail has been disabled!")
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
            Logging.log("ERROR",
                "(Mail.send) - Unexpected error in Mail.send() error e => "
                + str(e))
            pass

# Metaclass for locking video camera
class VideoFeed(type):

    def __new__(meta,name,bases,dct):
        if not hasattr(meta,'lock'):
            meta.lock = multiprocessing.Lock()
        return super(VideoFeed, meta).__new__(meta, name, bases, dct)

    def __init__(cls,name,bases,dct):
        if not hasattr(cls,'lock'):
            Logging.log("INFO", '(VideoFeed.__init__) - Passing "Lock" object to class "'
            + cls.__name__
            + '"')
            cls.lock = multiprocessing.Lock()
        if not hasattr(cls,'pid'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "pid" attribute to class "'
            + cls.__name__
            + '"')
            cls.pid = os.getpid()
        if not hasattr(cls,'main_pid'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "main_pid" attribute to class "'
            + cls.__name__
            + '"')
            cls.main_pid = os.getpid()
        if not hasattr(cls,'parent_pid'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "parent_pid" attribute to class "'
            + cls.__name__
            + '"')
            cls.parent_pid = os.getppid()
        if not hasattr(cls,'mac_addr_listed'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "mac_addr_listed" attribute to class "'
            + cls.__name__
            + '"')
            cls.mac_addr_listed = False
        if not hasattr(cls,'thread_locked'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "thread_locked" attribute to class "'
            + cls.__name__
            + '"')
            cls.thread_locked = False
        if not hasattr(cls,'timeout'):
            Logging.log("INFO", '(VideoFeed.__init__) - Adding "timeout" attribute to class "'
            + cls.__name__
            + '"')
            cls.timeout = 0
        super(VideoFeed,cls).__init__(name,bases,dct)

class MotionDetection(object):

    __metaclass__ = VideoFeed

    def __init__(self,options_dict={}):
        super(MotionDetection,self).__init__()

        self.tracker           = 0
        self.count             = 60

        self.ip                = options_dict['ip']
        self.fps               = options_dict['fps']
        self.email             = options_dict['email']
        self.netgear           = options_dict['netgear']
        self.password          = options_dict['password']
        self.email_port        = options_dict['email_port']
        self.accesslist        = options_dict['accesslist']
        self.server_port       = options_dict['server_port']
        self.cam_location      = options_dict['cam_location']
        self.disable_email     = options_dict['disable_email']

        self.delta_thresh_min  = options_dict['delta_thresh_min']
        self.delta_thresh_max  = options_dict['delta_thresh_max']
        self.motion_thresh_min = options_dict['motion_thresh_min']

        Mail.__disabled__   = self.disable_email

        self.accesslist_semaphore = threading.Semaphore(1)

        if not self.disable_email and (self.email is None or self.password is None):
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
            '/home/pi/.motiondetection/capture'
            + str(MotionDetection.img_num() + 1)
            + '.png'
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
                "Threading exception eStartThread => "
                + str(eStartThread))

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

            if not self.netgear is None:
                accesslist_thread = threading.Thread(
                    target=AccessList.mac_addr_presence,
                    args=(self.accesslist_semaphore,self.netgear,self.accesslist)
                )
                if not AccessList.thread_locked and AccessList.timedout(30):
                    AccessList.thread_locked = True
                    accesslist_thread.start()

            time.sleep(0.1)

            frame_delta = cv2.absdiff(previous_frame, current_frame)
            #(ret, frame_delta) = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY) # Original values
            (ret, frame_delta) = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
            frame_delta = cv2.dilate(frame_delta,np.ones((5,5), np.uint8),iterations=1)
            frame_delta = cv2.normalize(frame_delta, None, 0, 255, cv2.NORM_MINMAX)
            delta_count = cv2.countNonZero(frame_delta)

            if delta_count > self.delta_thresh_min and delta_count < self.delta_thresh_max:
                self.tracker += 1
                if self.tracker >= 60 or self.count >= 60:
                    self.count   = 0
                    self.tracker = 0
                    Logging.log("INFO",
                        "(MotionDetection.capture) - Motion detected with threshold levels at "
                        + str(delta_count)
                        + "!")
                    '''self.take_picture(colored_frame)
                    MotionDetection.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                        'Motion Detected','MotionDecetor.py detected movement!')'''
                    # Access list feature
                    if not AccessList.mac_addr_listed:
                        self.take_picture(colored_frame)
                        MotionDetection.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                            'Motion Detected','MotionDecetor.py detected movement!')
            elif delta_count < self.motion_thresh_min:
                self.count  += 1
                self.tracker = 0

            previous_frame = current_frame
            (ret, current_frame) = self.camera_motion.read()
            colored_frame  = current_frame 
            current_frame  = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)
            current_frame  = cv2.GaussianBlur(current_frame, (21, 21), 0)

class CamHandler(BaseHTTPRequestHandler,object):

    __record__    = False

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
                if not self.server.queue.empty():
                    if self.server.queue.get() == 'kill_monitor':
                        Logging.log("INFO",
                            '(CamHandler.do_GET) - (Queue message) -> Killing Live Feed!')
                        del(self.server.video_capture)
                        self.server.queue.put('close_camview')
                        break
                    elif self.server.queue.get() == 'start_recording':
                        CamHandler.__record__ = True
                        Logging.log("INFO",
                            "(CamHandler.do_GET) - queue.get() == 'start_recording'")
                    elif self.server.queue.get() == 'stop_recording':
                        CamHandler.__record__ = False
                        Logging.log("INFO",
                            "(CamHandler.do_GET) - queue.get() == 'stop_recording'")
                (read_cam, image) = self.server.video_capture.read()
                if not read_cam:
                    continue
                try:
                    self.server.video_output.write(image)
                    '''if CamHandler.__record__:
                        self.server.video_output.write(image)'''
                except Exception as eWrite:
                    print("Exception eWrite => "+str(eWrite))
                    pass
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
            print("(CamHandler.do_GET) - Exception e => "+str(e))
        return CamHandler

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
    def __init__(self, server_address,RequestHandlerClass,queue,video_capture,video_output,bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.queue = queue
        self.video_ouput = video_output
        self.video_capture = video_capture
        HTTPServer.allow_reuse_address = True

class Stream(MotionDetection):

    __metaclass__ = VideoFeed

    def __init__(self):
        super(Stream, self).__init__(options_dict)
        self.fps          = options_dict['fps']
        self.camview_port = options_dict['camview_port']
        self.cam_location = options_dict['cam_location']

    def stream_main(self,queue=None):
        Stream.lock.acquire()
        Logging.log("INFO", "(Stream.stream_main) - Lock acquired!")
        try:
            video_capture = cv2.VideoCapture(self.cam_location)
            video_capture.set(3,320)
            video_capture.set(4,320)
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            video_output = cv2.VideoWriter(
                '/home/pi/.motiondetection/stream.avi',
                fourcc, self.fps, (
                    int(video_capture.get(3)),
                    int(video_capture.get(4))
                )
            )
            Stream.lock.release()
            Logging.log("INFO", "(Stream.stream_main) - Streaming HTTPServer started")
            server = ThreadedHTTPServer(
                ('0.0.0.0', self.camview_port), CamHandler, queue, video_capture, video_output
            )
            server.timeout = 1
            server.queue   = queue
            server.video_output  = video_output
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
        except Exception as eThreadedHTTPServer:
            Logging.log("ERROR",
                "(Stream.stream_main) - eThreadedHTTPServer => "
                + str(eThreadedHTTPServer))
            queue.close()

class FileOpts(object):
  
    @staticmethod
    def file_exists(file_name):
        return os.path.isfile(file_name)

    @staticmethod
    def create_file(file_name):
        if FileOpts.file_exists(file_name):
            Logging.log("INFO",
                "(FileOpts.compress_file) - File "
                + str(file_name)
                + " exists.")
            return
        Logging.log("INFO",
            "(FileOpts.compress_file) - Creating file "
            + str(file_name)
            + ".")
        open(file_name, 'w')

    @staticmethod
    def dir_exists(dir_path):
        return os.path.isdir(dir_path)

    @staticmethod
    def mkdir_p(dir_path):
        try:
            Logging.log("INFO", "Creating directory " + str(dir_path))
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and FileOpts.dir_exists(dir_path):
                pass
            else:
                Logging.log("ERROR", "mkdir error: " + str(e))
                raise


class AccessList(object):

    __metaclass__ = VideoFeed 

    @staticmethod
    def set_default_values(semaphore,listed=False,locked=False):
        AccessList.mac_addr_listed = listed
        semaphore.release()
        AccessList.thread_locked = locked

    @classmethod
    def timedout(cls,seconds=60):
        if AccessList.timeout == 0:
            AccessList.timeout += 1
        elif AccessList.timeout >= 10 * seconds:
            AccessList.timeout = 0
            return True
        else:
            AccessList.timeout += 1

    @classmethod
    def mac_addr_presence(cls,semaphore,netgear,accesslist):
        semaphore.acquire(blocking=True)
        try:
            if isinstance(netgear, Netgear):
                for device in netgear.get_attached_devices():
                    if not device.mac in open(accesslist,'r').read():
                        AccessList.set_default_values(semaphore,False,False)
                    else:
                        Logging.log("INFO","(AccessList.mac_addr_presence) - Device name: "+str(device.name))
                        Logging.log("INFO","(AccessList.mac_addr_presence) - Device IP address: "+str(device.ip))
                        Logging.log("INFO","(AccessList.mac_addr_presence) - Device MAC address: "+str(device.mac))
                        AccessList.set_default_values(semaphore,True,False)
                        break
            else:
                AccessList.set_default_values(semaphore,False,False)
        except:
            AccessList.set_default_values(semaphore,False,False)
            pass

class Server(MotionDetection):

    __metaclass__ = VideoFeed

    def __init__(self,queue):
        super(Server, self).__init__(options_dict)

        self.queue = queue
        self.camview_port = options_dict['camview_port']

        self.process = multiprocessing.Process(
            target=MotionDetection(options_dict).capture,name='capture',args=(queue,)
        )
        self.process.daemon = True
        self.process.start()

        Server.main_pid   = os.getpid()
        Server.parent_pid = os.getppid()
        Logging.log("INFO","(Server.__init__) - Server.main_pid: "+str(Server.main_pid))
        Logging.log("INFO","(Server.__init__) - Server.parent_pid: "+str(Server.parent_pid))

        MotionDetection.pid = self.process.pid
        Logging.log("INFO","(Server.__init__) - MotionDetection.pid: "+str(MotionDetection.pid))

        try:
            self.sock = socket.socket()
            self.sock.bind(('0.0.0.0', self.server_port))
        except Exception as eSock:
            if 'Address already in use' in eSock:
                Logging.log("ERROR",
                    "(Server.__init__) - eSock error e => "+str(eSock))
                os.system('/usr/bin/sudo /sbin/reboot')

    def handle_incoming_message(self,*data):
        for(sock,queue) in data:
            message = sock.recv(1024)
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
                MotionDetection.pid = self.proc.pid
                Logging.log("INFO","(Server.handle_incoming_message) - MotionDetection.pid: "+str(Stream.pid))
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
                MotionDetection.pid = self.process.pid
                Logging.log("INFO","(Server.handle_incoming_message) - MotionDetection.pid: "+str(MotionDetection.pid))
            elif(message == 'start_recording'):
                queue.put('start_recording')
            elif(message == 'stop_recording'):
                queue.put('stop_recording')
            elif(message == 'ping'):
                sock.send(str([Server.main_pid,MotionDetection.pid,Server.parent_pid]))
            else:
                pass
            sock.close()

    def server_main(self):

        Logging.log("INFO", "(Server.server_main) - Listening for connections.")

        while(True):
            time.sleep(0.05)
            try:
                self.sock.listen(10)
                (con, addr) = self.sock.accept()
                if not '127.0.0.1' in str(addr):
                    Logging.log("INFO",
                        "(Server.server_main) - Received connection from "
                        + str(addr))

                Server.handle_incoming_message(self,(con,self.queue))

            except KeyboardInterrupt:
                print('\n')
                Logging.log("INFO", "(Server.server_main) - Caught control + c, exiting now.\n")
                self.sock.close()
                sys.exit(0)
            except Exception as eAccept:
                Logging.log("ERROR", "(Server.server_main) - Socket accept error: "
                    + str(eAccept))

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
    parser.add_option('-c', '--camera-location',
        dest='cam_location', type='int', default=0,
        help='Camera index number that defaults to 0. This is the '
            + 'location of the camera - Which is usually /dev/video0.')
    parser.add_option('-f', '--fps',
        dest='fps', type='int', default='30',
        help='This sets the frames per second for the motion '
            + 'capture system. It defaults to 30 frames p/s.')
    parser.add_option('-w', '--white-list',
        dest='accesslist', default='/home/pi/.motiondetection/accesslist',
        help='This ensures that the MotionDetection system does not run '
            + 'if the mac is in the accesslist. This defaults to '
            + '/home/pi/.motiondetection/accesslist.')
    parser.add_option('-P', '--passive',
        dest='passive', action='store_true', default=False,
        help='This option allows you to circumvent the motiondetection system. '
            + 'This option must be used in conjunction with -r/--router-password.')
    parser.add_option('-e', '--email',
        dest='email',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail address is used to send the pictures taken as '
            + 'well as notify you of motion detected.')
    parser.add_option('-p', '--password',
        dest='password',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail password is used to send the pictures taken '
            + 'as well as notify you of motion detected.')
    parser.add_option('-r', '--router-password',
        dest='router_password', default='password',
        help='This option is your routers password. This is used to '
            + 'circumvent the motiondetection system. If your phone is '
            + 'connected to your router and in the access list. The '
            + 'MotionDetection system will not run.')
    parser.add_option('-C', '--camview-port',
        dest='camview_port', type='int', default=5000,
        help='CamView port defaults to port 5000'
            + 'This is the port the streaming feature runs on. '
            + 'The streaming feature is the ability to view the '
            + 'live feed from the camera via ANdroid app.')
    parser.add_option('-t', '--delta-threshold-min',
        dest='delta_thresh_min', type='int', default=1500,
        help='Sets the minimum movement threshold '
            + 'to trigger the programs image capturing/motion routines. If movement '
            + 'above this level is detected then this is when MotiondDetection '
            + 'goes to work. The default value is set at 1500.')
    parser.add_option('-T', '--delta-threshold-max',
        dest='delta_thresh_max', type='int', default=10000,
        help='Sets the maximum movement threshold when the '
            + 'programs image capturingi/motion routines stops working. '
            + 'If movement above this level is detected then this program '
            + ' will not perform any tasks and sit idle. The default value is set at 10000.')
    parser.add_option('-m', '--motion-threshold-min',
        dest='motion_thresh_min', type='int', default=500,
        help='Sets the minimum movement threshold to start the framework '
            + 'and trigger the programs main motion detection routine. '
            + 'This is used because even if there is no movement as all '
            + 'the program still receives false hits and the values can '
            + 'range from 1 to around 500 and is what the default is set to - 500.')
    parser.add_option('-S', '--server-port',
        dest='server_port', type='int', default=50050,
        help='Server port defaults to port 50050.'
            + 'This is the port the command server runs on. '
            + 'This server listens for specific commands from '
            + 'the Android app and controls the handling of the '
            + 'camera lock thats passed abck and forth between the '
            + 'streaming server and the motion detection system.')
    (options, args) = parser.parse_args()

    Logging.log("INFO", "(MotionDetection.__main__) - Initializing netgear object.")
    if options.passive:
        netgear = Netgear(password=options.router_password)
    else:
        netgear = None

    if not FileOpts.file_exists('/var/log/motiondetection.log'):
        FileOpts.create_file('/var/log/motiondetection.log')

    if not FileOpts.dir_exists('/home/pi/.motiondetection'):
        FileOpts.mkdir_p('/home/pi/.motiondetection')

    options_dict = {
        'logfile': options.logfile, 'fps': options.fps,
        'netgear': netgear, 'disable_email': options.disable_email,
        'server_port': options.server_port, 'email': options.email,
        'delta_thresh_max': options.delta_thresh_max, 'ip': options.ip, 
        'password': options.password, 'cam_location': options.cam_location,
        'email_port': options.email_port, 'camview_port': options.camview_port,
        'accesslist': options.accesslist, 'delta_thresh_min': options.delta_thresh_min,
        'router_password': options.router_password, 'motion_thresh_min': options.motion_thresh_min,
    }

    motion_detection = MotionDetection(options_dict)
    Server(multiprocessing.Queue()).server_main()
