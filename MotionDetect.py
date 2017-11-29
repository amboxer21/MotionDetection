#!/usr/bin/env python

'''This is a video motion detector.

This uses about 5% CPU running with continuous motion detection on
a i5-3320M 2.6GHz with 16 GB RAM under no other load.

AUTHOR

    Noah Spurrier <noah@noah.org>

LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2014, Noah Spurrier
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

VERSION

    Version 2
'''

import cv2,sys,time,smtplib,threading
import modules.datetime.datetime as datetime

from __init__ import *
from time import sleep
from threading import Timer,Thread

from multiprocessing import Process
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart

def now():
    return time.asctime(time.localtime(time.time()))

def sendMail(sender,to,password,port,subject):
    try:
        message = MIMEMultipart()
        message['Subject'] = subject
        mail = smtplib.SMTP('smtp.gmail.com',port)
        mail.starttls()
        mail.login(sender,password)
        mail.sendmail(sender, to, message.as_string())
        sys.stdout.write("MotionDetection.py Security ALERT: - Sent email successfully!\n")
        sys.stdout.flush()
    except smtplib.SMTPAuthenticationError:
        sys.stdout.write("MotionDetection.py - Could not athenticate with password and username!\n")
        sys.stdout.flush()
    except:
        sys.stdout.write("MotionDetection.py - Unexpected error in sendMail().\n")
        sys.stdout.flush()

def notify():
    global is_sent
    print("is_sent = " + str(is_sent))
    if is_sent is not True:
        sendMail('from@gmail.com','tn@vtext.com','app password',587,'Motion Detected')
        is_sent = True

def main():

    BLUR_SIZE = 3
    NOISE_CUTOFF = 12

    cam = cv2.VideoCapture(0)
    cam.set(3,640)
    cam.set(4,480)

    # Stabilize the detector by letting the camera warm up and
    # seeding the first frames.
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

        # Visual detection statistics output.
        # Normalize improves brightness and contrast.
        # Mirror view makes self display more intuitive.
        cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
        frame_delta = cv2.flip(frame_delta, 1)

        if(delta_count > 1000 and is_moving is True):
            count = 0
            is_moving = False
            print("MOVEMENT: " + now() + ", Delta: " + str(delta_count))
            notify()
        elif delta_count < 100:
            count += 1
            is_moving = True
            print("count: " + str(count))
            if count == 60:
                print("Count == 60")
                is_sent = False

        # Advance the frames.
        frame_prior = frame_now
        frame_now = cam.read()[1]
        frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
        frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))

main()
