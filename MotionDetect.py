#!/usr/bin/env python
#coding: interpy
    
import modules.datetime.datetime as datetime
import cv2,sys,time,smtplib,threading,glob,re,os
    
from __init__ import *
from time import sleep
   
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
   
class MotionDetection():
    
    def now(self):
        return time.asctime(time.localtime(time.time()))
    
    def img_num(self):
        _list = []
        os.chdir("/home/aguevara/.motiondetection/")
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            _list.append(num.group(2))
        return max(_list)
    
    def sendMail(self,sender,to,password,port,subject,body):
        try:
            message = MIMEMultipart()
            message['Body'] = body
            message['Subject'] = subject
            message.attach(MIMEImage(file("/home/aguevara/.motiondetection/capture" + str(self.img_num()) + ".png").read()))
            mail = smtplib.SMTP('smtp.gmail.com',port)
            mail.starttls()
            mail.login(sender,password)
            mail.sendmail(sender, to, message.as_string())
            print("MotionDetection.py Security ALERT: - Sent email successfully!\n")
        except smtplib.SMTPAuthenticationError:
            print("MotionDetection.py - Could not athenticate with password and username!")
        except  Exception as e:
            print( "Error: %s " % str(e) )
            print("MotionDetection.py - Unexpected error in sendMail():")
    
    def notify(self):
        global is_sent
        print("is_sent = " + str(is_sent))
        if is_sent is not True:
            self.sendMail('from@gmail.com','to@gmail.com','email_password',587,'Motion Detected','MotionDecetor.py detected movement!')
            is_sent = True
    
    def takePicture(self):
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return
        ret, frame = camera.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
        time.sleep(0.1)
        picture_name = "/home/aguevara/.motiondetection/capture" + str(int(self.img_num()) + 1) + ".png"
        cv2.imwrite(picture_name, frame)
        del(camera)
    
    def main(self):
    
        global cam_deleted
    
        cam_deleted = False
    
        BLUR_SIZE = 3
        NOISE_CUTOFF = 12
    
        cam = cv2.VideoCapture(0)
        cam.set(3,640)
        cam.set(4,480)
    
        frame_now = cam.read()[1]
        frame_now = cam.read()[1]
        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
        frame_prior = frame_now
    
        while True:
      
            global count
            global is_sent
    
            frame_delta = cv2.absdiff(frame_prior, frame_now)
            frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)[1]
            delta_count = cv2.countNonZero(frame_delta)
    
            cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
            frame_delta = cv2.flip(frame_delta, 1)
    
            if(delta_count > 1000 and is_moving is True):
                count = 0
                is_moving = False
                print("MOVEMENT: " + now() + ", Delta: " + str(delta_count))
                del(cam)
                cam_deleted = True
                self.takePicture()
                self.notify()
            elif delta_count < 100:
                count += 1
                is_moving = True
                print("count: " + str(count))
                if count == 60:
                    print("Count == 60")
                    is_sent = False
    
            if cam_deleted:
                BLUR_SIZE = 3
                NOISE_CUTOFF = 12
    
                cam = cv2.VideoCapture(0)
                cam.set(3,640)
                cam.set(4,480)
    
                cam_deleted = False
    
            # keep the frames moving.
            frame_prior = frame_now
            frame_now = cam.read()[1]
            frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
            frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
    
if __name__ == '__main__':
    motiond = MotionDetection()
    motiond.main()
