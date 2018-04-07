#!/usr/bin/env python

from PIL import Image
from __init__ import *
from optparse import OptionParser

from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart

from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

import modules.datetime.datetime as datetime
import cv2,sys,time,smtplib,threading,glob,re
#import StringIO,Image,socket,threading,os,subprocess
import StringIO,socket,threading,os,subprocess

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        global streamCamera

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
        while True:
            try:
                read, image = streamCamera.read()
                #if not read:
                    #continue
                if killCamera is True:
                    print("[CamHandler] Killing cam.")
                    del(streamCamera)
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
                del(streamCamera)
                break
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Stream():
    def __init__(self,cam_location):
        self.cam_location = cam_location

    def main(self):

        global killCamera
        global streamCamera

        streamCamera = cv2.VideoCapture(self.cam_location)
        streamCamera.set(3,320)
        streamCamera.set(4,320)
        try:
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            print("Streaming HTTPServer started")
            server.serve_forever()
        except KeyboardInterrupt:
            del(streamCamera)
            server.socket.close()
        except Exception as eThreadedHTTPServer:
            pass

class MotionDetection():

    def __init__(self,ip,server_port,email,password,email_port,cam_location):

        self.ip = ip
        self.email = email
        self.password = password
        self.email_port = email_port
        self.server_port = server_port
        self.cam_location = cam_location

    def user_name(self):
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()
    
    def now(self):
        return time.asctime(time.localtime(time.time()))
    
    def img_num(self):
        _list = []
        os.chdir("/home/" + self.user_name() + "/.motiondetection/")
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(int(num.group(2)))
        return max(_list)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            message.attach(MIMEImage(file("/home/" + self.user_name() + "/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            print("MotionDetection.py Security ALERT: - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            print("MotionDetection.py - Could not athenticate with password and username!")
        except Exception as e:
            print( "Error: %s " % str(e) )
            print("MotionDetection.py - Unexpected error in sendMail():")
    
    def notify(self):
        global is_sent
        if is_sent is not True:
            self.sendMail(self.email,self.email,self.password,self.email_port,'Motion Detected','MotionDecetor.py detected movement!')
            is_sent = True
    
    def takePicture(self):
        camera = cv2.VideoCapture(self.cam_location)
        if not camera.isOpened():
            return
        ret, frame = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.1)
        picture_name = "/home/" + self.user_name() + "/.motiondetection/capture" + str(self.img_num() + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        del(camera)

    def kill_cam(self):
        global kill
        print("def kill_cam(self):")
        killCamera = True

    def capture(self):
        print("Motion Detection system initialed.")
    
        global cam
        global cam_deleted
   
        is_moving   = True
        cam_deleted = False
    
        cam = cv2.VideoCapture(self.cam_location)

        frame_now = cam.read()[1]
        frame_now = cam.read()[1]

        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)
        frame_prior = frame_now
    
        while(True):

            if killCamera is True:
                print("Killing cam.")
                del(cam)
                break
      
            global count
            global is_sent

            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
             
            if(delta_count > 1500 and delta_count < 10000 and is_moving is True):
                count = 0
                is_moving = False
                print("MOVEMENT: " + self.now() + ", Delta: " + str(delta_count))
                del(cam)
                cam_deleted = True
                #self.takePicture()
                #self.notify()
            elif delta_count < 100:
                count += 1
                time.sleep(0.1)
                is_moving = True
                #print("count: " + str(count))
                if count == 5000:
                    print("Resetting counter.")
                    count = 0
                    is_sent = False
    
            if cam_deleted:
                cam = cv2.VideoCapture(self.cam_location)
    
                cam_deleted = False
    
            # keep the frames moving.
            frame_prior = frame_now
            frame_now = cam.read()[1]
            frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
            frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)

class Server():

    def __init__(self):
        parser = OptionParser()
        parser.add_option("-i",
            "--ip", dest='ip', help='"This is the IP address of the server."',default='0.0.0.0')
        parser.add_option("-S",
            "--server-port", dest='server_port', help='"Server port defaults to port 50050"', type="int", default=50050)
        parser.add_option("-e",
            "--email", dest='email', help='"This argument is required!"')
        parser.add_option("-p",
            "--password", dest='password', help='"This argument is required!"')
        parser.add_option("-c",
            "--camera-location", dest='cam_location', help='"Camera index number."', type="int", default=0)
        parser.add_option("-E",
            "--email-port", dest='email_port', help='"E-mail port defaults to port 587"', type="int", default=587)
        (options, args) = parser.parse_args()

        self.ip = options.ip
        self.email = options.email
        self.password = options.password
        self.email_port = options.email_port
        self.server_port = options.server_port
        self.cam_location = options.cam_location

        if self.email is None or self.password is None:
            print("\nERROR: Both E-mail and password are required!\n")
            parser.print_help()
            sys.exit(0)

    def start_thread(self,proc):
        try:
            t = threading.Thread(target=proc)
            t.daemon = True
            t.start()
        except Exception as eStartThread:
            print("Threading exception eStartThread => " + str(eStartThread))

    def main(self):

        global sock
        global killCamera

        stream = Stream(self.cam_location)
        motionDetection = MotionDetection(self.ip,self.server_port,self.email,self.password,self.email_port,self.cam_location)

        try:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.server_port))
            sock.listen(5)
            time.sleep(1)
            self.start_thread(motionDetection.capture)
            time.sleep(1)
        except Exception as eSock:
            print("Sock exception eSock => " + str(eSock))

        print("Listening for connections.")
        while(True):
            time.sleep(0.05)
            try:
                con, addr = sock.accept()
                print("Received connection from " + str(addr))
                message = con.recv(1024)

                if(message == 'start_monitor'):
                    print("Starting camera!")
                    #con.send("Starting camera!")
                    killCamera = True
                    time.sleep(1)
                    killCamera = False
                    self.start_thread(stream.main)
                elif(message == 'kill_monitor'):
                    print("Killing camera!")
                    #con.send("Killing camera!")
                    killCamera = True
                    time.sleep(1)
                    killCamera = False
                    self.start_thread(motionDetection.capture)
                elif(message == 'start_motion'):
                    print("Starting motion sensor!")
                    #con.send("Starting motion sensor!")
                elif(message == 'kill_motion'):
                    print("Killing motion sensor!")
                    #con.send("Killing motion sensor!")
                elif(message == 'probe'):
                    print("Server is alive.")
                    #con.send("Server is alive.")
                else:
                    print(message + " is not a known command.")
                    #con.send(message + " is not a konwn command!")
            except Exception as eAccept:
                print("Socket accept error: " + str(eAccept))
        con.close()

if __name__ == '__main__':
    server = Server()
    server.main()
