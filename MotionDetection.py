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
import StringIO,socket,threading,os,subprocess,sqlite3

class SQLDB(object):

    def __init__(self,db):
        super(SQLDB, self).__init__()
        self.db = db 
   
    # Used to re-initialize the database when exiting the program. It will set all columns to False
    def init_db(self):
        print("(SQLDB)[init_db] def init_db()")
        self.select_all()
        with self.db:
            self.db.row_factory = sqlite3.Row
            cursor = self.db.cursor()
            try:
                print("(SQLDB)[init_db] self.update('is_sent','False')")
                self.update('is_sent','False')
                print("(SQLDB)[init_db] self.update('cam_deleted','False')")
                self.update('cam_deleted','False')
                print("(SQLDB)[init_db] self.update('kill_camera','False')")
                self.update('kill_camera','False')
                print("(SQLDB)[init_db] self.update('stop_motion','False')")
                self.update('stop_motion','False')
            except Exception as e:
                print("(SQLDB)[init_db] Exception e => " + str(e))
            self.db.commit()

    # Used to initialize the database. It will create the
    # database, columns and tables if they do not exist and then return. 
    def select_all(self):
        print("(SQLDB)[select_all] def select_all()")
        while(True):
            with self.db:
                self.db.row_factory = sqlite3.Row
                cursor = self.db.cursor()
                try:
                    cursor.execute('select * from motion')
                    data = cursor.fetchall()
                    return data
                except sqlite3.OperationalError as e:
                    print("(SQLDB)[select_all] Exception sqlite3.OperationalError e => " + str(e))
                    if re.search('no such table:', str(e), re.I | re.M):
                        print("(SQLDB)[select_all] Exception sqlite3.OperationalError 'no such table'")
                        cursor.execute('Create table motion(id INTEGER PRIMARY KEY NOT NULL, name TEXT, state TEXT)')
                        cursor.execute("Insert into motion (name, state) values('is_sent','False')")
                        cursor.execute("Insert into motion (name, state) values('cam_deleted','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('stop_motion','False')")
                    elif re.search('no such column:', str(e), re.I | re.M):
                        print("(SQLDB)[select_all] Exception sqlite3.OperationalError 'no such column'")
                        cursor.execute("Insert into motion (name, state) values('is_sent','False')")
                        cursor.execute("Insert into motion (name, state) values('cam_deleted','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('stop_motion','False')")
                    self.db.commit()

    def insert(self,column,value):
        print("(SQLDB)[insert] def insert()")
        with self.db:
            cursor = self.db.cursor()
            try:
                cursor.execute("insert into motion (name,state) values('" + column + "','" + values + "');")
            except Exception as e:
                print("(SQLDB)[insert] Exception e => " + str(e))
                pass
            self.db.commit()

    def update(self,column,value):
        print("(SQLDB)[update] def update()")
        with self.db:
            cursor = self.db.cursor()
            try:
                cursor.execute("update motion set state = '" + value + "' where name = '" + column + "';")
            except Exception as e:
                print("(SQLDB)[update] Exception e => " + str(e))
                pass
            self.db.commit()

    # Used to grab the state of which ever column you pass as a parameter.
    # Every column has a state field which either returns true or false.
    def select_state_from(self,column):
        # Using below function prints too many times and makes it so you can't read the other output.
        #print("(SQLDB)[select_state_from] def select_state_from()")
        with self.db:
            cursor = self.db.cursor()
            try:
                data = cursor.execute("select state from motion where name = '" + column + "';")
            except Exception as e:
                print("(SQLDB)[select_state_from] Exception e => " + str(e))
                pass
        for d in data:
            return d[0]

# This class is instantiated to create the DB when the program is started for the
# first time. It's useless after the first call but but necessary to call for that first time.
if __name__ == '__main__':
    sqldb = SQLDB(sqlite3.connect('motiondetection.db'))
    sqldb.select_all()

class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("(CamHandler)[do_GET] def do_GET()")

        #global streamCamera
        time.sleep(1)
        streamCamera = cv2.VideoCapture(Server().cam_location)
        streamCamera.set(3,160) # Set width
        streamCamera.set(4,120) # Set height

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

        while True:

            read,image = streamCamera.read()

            try:

                # if kill_camera:
                if re.search('True',Server().select_state_from('kill_camera'), re.M | re.I):
                    print("(CamHandler)[do_GET] Killing cam.")
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
            except Exception as e:
                #print("(CamHandler)[do_GET] Exception e => " + str(e))
                break
            except KeyboardInterrupt:
                print("(CamHandler)[do_GET] KeyboardInterrupt.")
                del(streamCamera)
                break
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Stream(object):
    def __init__(self,opts,*args):
        super(Stream, self).__init__(*args)
        self.cam_location = opts[0] # cam_location

    def stream_main(self):
        print("(Stream)[stream_main] def stream_main()")

        '''
        global streamCamera

        time.sleep(1)
        streamCamera = cv2.VideoCapture(self.cam_location)
        streamCamera.set(3,160) # Set width
        streamCamera.set(4,120) # Set height
        '''

        Server().sock_opts([{'kill_camera':'False'}],0)

        try:
            print("(Stream)[stream_main] Streaming HTTPServer started")
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            print("(Stream)[stream_main] KeyboardInterrupt")
            del(streamCamera)
            Server().socket.close()
        except Exception as e:
            if re.search('Address already in use', str(e)).group():
                print("(Server)[server_main] Exception e - re.search('Address already in use') ")
            print("(Stream)[stream_main] Exception e => " + str(e))
            pass

class MotionDetection(object):

    def __init__(self,opts,*args):
        super(MotionDetection, self).__init__(*args)
        self.ip = opts[0] # ip
        self.email = opts[2] # email
        self.password = opts[3] # password
        self.email_port = opts[4] # email_port
        self.server_port = opts[1] # server_port
        self.cam_location = opts[5] # cam_location

    def user_name(self):
        print("(MotionDetection)[user_name] def user_name()")
        comm = subprocess.Popen(["users"], shell=True, stdout=subprocess.PIPE)
        return re.search("(\w+)", str(comm.stdout.read())).group()
    
    def time_now(self):
        print("(MotionDetection)[time_now] def time_now()")
        return time.asctime(time.localtime(time.time()))
    
    # This program takes pictures when movement is detected. It saves the picture with the name
    # captureX.png X being a number. This method finds the capture with the highest number and 
    # returns that number. So if capture66.png was the picture with the higest number this
    # method will return that number.
    def img_num(self):
        print("(MotionDetection)[img_num] def img_num()")
        _list = []
        os.chdir("/home/" + self.user_name() + "/.motiondetection/")
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(int(num.group(2)))
        return max(_list)
    
    def send_mail(self,sender,to,password,port,subject,body):
        print("(MotionDetection)[send_mail] def send_mail()")
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            message.attach(MIMEImage(file("/home/" + self.user_name() + "/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            #message.attach(MIMEImage(file("/home/pi/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            print("(MotionDetection)[send_mail] Security ALERT: - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            print("(MotionDetection)[send_mail] Could not athenticate with password and username!")
        except Exception as e:
            print("(MotionDetection)[send_mail] Exception e => " + str(e))
    
    def notify(self):
        print("(MotionDetection)[notify] def notify()")
        global is_sent
        if is_sent is not True:
            self.send_mail(self.email,self.email,self.password,self.email_port,'Motion Detected','MotionDecetor.py detected movement!')
            is_sent = True
    
    def takePicture(self):
        print("(MotionDetection)[take_picture] def take_picture()")
        camera = cv2.VideoCapture(self.cam_location)
        if not camera.isOpened():
            return
        ret, frame = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.1)
        #picture_name = "/home/pi/.motiondetection/capture" + str(self.img_num() + 1) + ".png"
        picture_name = "/home/" + self.user_name() + "/.motiondetection/capture" + str(self.img_num() + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        del(camera)

    def capture(self):
        print("Motion Detection system initialed.\n")
        print("(MotionDetection)[capture] def capture()")
        time.sleep(3)
    
        global cam
        global cam_deleted
   
        is_moving   = True
        cam_deleted = False
    
        cam = cv2.VideoCapture(self.cam_location)

        read,frame_now = cam.read()

        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.GaussianBlur(frame_now, (15, 15), 0)
        frame_prior = frame_now
    
        while(True):

            # if kill_camera and stop_motion:
            if (re.search('True',Server().select_state_from('kill_camera'), re.M | re.I) or
                re.search('True',Server().select_state_from('stop_motion'), re.M | re.I)):
                    print("(MotionDetection)[capture] Killing cam.")
                    Server().sock_opts([{'kill_camera':'False'}],1)
                    del(cam)
                    break
      
            global count
            global is_sent

            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, 5, 100, cv2.THRESH_BINARY)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
             
            # Movement is measure here and then represented by the delta_count variable.
            # If the measured movement is above and below a specific threshold then we 
            # take a picture and notify the user of the program. If the threshold stays
            # below 100 for 1 minute, we allow the system to work again; that means emails and pics.
            if(delta_count > 1300 and delta_count < 10000 and is_moving is True):
                count = 0
                is_moving = False
                print("(MotionDetection)[capture] MOVEMENT: " + self.time_now() + ", Delta: " + str(delta_count))
                del(cam)
                cam_deleted = True
                self.takePicture()
                if self.email is not None:
                    self.notify()
            elif delta_count < 100:
                count += 1
                time.sleep(0.1)
                is_moving = True
                if count == 120:
                    print("(MotionDetection)[capture] Resetting counter.")
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

# Parent class inherits multiple child classes to circumvent the use of global variables.
# This is a neater and cleaner way to pass variables between the classes. This also allows
# me to call a method in from one class in multiple classes without ever having to instantiate
# that class multiple times.
class Server(Stream,MotionDetection,SQLDB):

    def __init__(self):
        parser = OptionParser()
        parser.add_option("-e",
            "--email",dest='email',help='"This argument is required!"')
        parser.add_option("-p",
            "--password",dest='password',help='"This argument is required!"')
        parser.add_option("-c",
            "--camera-location",dest='cam_location',help='"Camera index number."',type="int")
        parser.add_option("-i",
            "--ip", dest='ip',help='"This is the IP address of the server."',default='0.0.0.0')
        parser.add_option("-E",
            "--email-port",dest='email_port',help='"E-mail port defaults to port 587"',type="int",default=587)
        parser.add_option("-S",
            "--server-port",dest='server_port',help='"Server port defaults to port 50050"',type="int",default=50050)
        parser.add_option("-D",
            "--disable-email",dest='disable_email',help='"Disable E-mail notifications"',default=False,action="store_true")
        (options, args) = parser.parse_args()

        self.ip = options.ip
        self.email = options.email
        self.password = options.password
        self.email_port = options.email_port
        self.server_port = options.server_port
        self.disable_email = options.disable_email

        # If cam location is not passed as an option on the command line
        # then we will attempt to automatically try to find the camera. If
        # we are unable to find a camera automatically, then we will exit
        # after telling the user that they need to manually specify the cam
        # location.
        if options.cam_location is None:
            self.cam_location = self.video_id()
        else:
            self.cam_location = options.cam_location

        if not self.disable_email and (self.email is None or self.password is None):
            print("\nERROR: Both E-mail and password are required!\n")
            parser.print_help()
            sys.exit(0)

        streamList = [self.cam_location]
        motionList = [self.ip,self.server_port,
            self.email,self.password,self.email_port,self.cam_location]

        # Instantiating all child classes with the necessary variables passed as lists
        super(Server, self).__init__(streamList,motionList,sqlite3.connect('motiondetection.db'))

    # A method to automatically find the lowest cam index if it's present and named videoX
    def video_id(self):
        # Using below function prints too many times and makes it so you can't read the other output.
        #print("(Server)[video_id] def video_id()") 
        _ids = []
        for _file in os.listdir('/dev/'):
            name = re.search("(\wideo)(\d)", _file, re.M | re.I)
            if name is not None:
                _ids.append(int(name.group(2)))
        if not _ids:
            print("\n -> Cannot find a camera. Please use the -c option" + 
                "\n    and specifiy the cameras location manually.\n")
            sys.exit(0)
        else:
            return min(_ids)

    # Takes a list of dicts as its first param then an int as an arg to sleep.
    # sock_opts calls an sqlite3 update function via thread method and calls a sleep
    # function directoly after. This function was created to compress 3-6 lines in the 
    # server classes socket flow control below into 1 line per section.
    def sock_opts(self,list,seconds):
        print("(Server)[sock_opts] def sock_opts()")
        for dict in list:
            for d in dict:
                self.start_thread(self.update(d,dict[d]))
                time.sleep(int(seconds))

    def start_thread(self,proc):
        print("(Server)[server_main] def start_thread()")
        try:
            t = threading.Thread(target=proc)
            t.daemon = True
            t.start()
        except Exception as e:
            print("(Server)[start_thread] Exception e => " + str(e))

    def server_main(self):
        print("(Server)[server_main] def server_main()")

        global sock

        try:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.server_port))
            sock.listen(5)
            time.sleep(1)
            self.start_thread(Server().capture)
            time.sleep(1)
        except Exception as e:
            print("(Server)[server_main] Exception e => " + str(e))

        print("(Server)[server_main] Listening for connections.")
        while(True):
            time.sleep(0.05)
            try:
                con, addr = sock.accept()
                print("(Server)[server_main] Received connection from " + str(addr))
                message = con.recv(1024)

                # Start Live Stream feature.
                if(message == 'start_monitor'):
                    print("(Server)[server_main] start_monitor!")
                    # First example and use of the method to comress the sqlite3 update
                    # calls passed via list of dicts.
                    #self.sock_opts([{'kill_camera':'True'},{'kill_camera':'False'}],1)
                    self.sock_opts([{'kill_camera':'True'}],0)
                    self.start_thread(Server().stream_main)
                # Stop Live Stream feature.
                elif(message == 'kill_monitor'):
                    print("(Server)[server_main] kill_monitor!")
                    self.sock_opts([{'kill_camera':'True'},{'kill_camera':'False'}],1)
                    (self.start_thread(Server().capture) and time.sleep(1))
                # Start Motion Detection feature.
                elif(message == 'start_motion'):
                    print("(Server)[server_main] start_motion!")
                    self.sock_opts([{'kill_camera':'True'},{'stop_motion':'False'},{'kill_camera':'False'}],1)
                    (self.start_thread(Server().capture) and time.sleep(1))
                # Stop Motion Detection feature.
                elif(message == 'kill_motion'):
                    print("(Server)[server_main] kill_motion!")
                    self.sock_opts([{'kill_camera':'True'}],1)
                elif(message == 'probe'):
                    print("(Server)[server_main] probe!")
                    print("Server is alive.")
                else:
                    print(message + " is not a known command.")
            except KeyboardInterrupt:
                print("\n\nControl + c was pressed. Re-initializing database then closing program out.\n")
                print("(Server)[server_main] KeyboardInterrupt")
                Server().init_db()
                sys.exit(0)
            except Exception as e:
                print("(Server)[server_main] Exception e => " + str(e))
            con.close()

if __name__ == '__main__':
    server = Server()
    server.server_main()
