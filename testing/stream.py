#!/usr/bin/env python

from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

import cv2,sys,time,smtplib,threading,glob,re
import StringIO,Image,socket,threading,os,subprocess

capture=None

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
        while True:
            try:
                rc, img = capture.read()
                if not rc:
                    continue
                imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                jpg = Image.fromarray(imgRGB)
                tmpFile = StringIO.StringIO()
                jpg.save(tmpFile,'JPEG')
                self.wfile.write("--jpgboundary")
                self.send_header('Content-type','image/jpeg')
                self.send_header('Content-length',str(tmpFile.len))
                self.end_headers()
                jpg.save(self.wfile,'JPEG')
                time.sleep(0.05)
            except KeyboardInterrupt:
                break
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Stream():
    def __init__(self,cam_location):
        self.cam_location = cam_location

    def main(self):
        global img
        global capture
        capture = cv2.VideoCapture(self.cam_location)
        capture.set(3,320)
        capture.set(4,320)
        try:
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            print("Streaming HTTPServer started")
            server.serve_forever()
        except KeyboardInterrupt:
            del(capture)
            server.socket.close()

if __name__ == '__main__':
    stream = Stream(0)
    stream.main()
