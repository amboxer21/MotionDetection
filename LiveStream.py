#!/usr/bin/env python

import Image,time,cv2,sys
import StringIO,threading

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn

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

    def main():
        global img
        global capture
        capture = cv2.VideoCapture(int(sys.argv[1]))
        capture.set(3,320)
        capture.set(4,320)
        try:
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            print("server started")
            server.serve_forever()
            except KeyboardInterrupt:
            del(capture)
            server.socket.close()

if __name__ == '__main__':
  main()

