#!/usr/bin/env python

import cv2
import time
import Image
import StringIO
import threading

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn

capture=None

class CamHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path.endswith('.mjpg'):
      self.send_response(200)
      self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
      self.end_headers()
      while True:
        try:
          rc,img = capture.read()
          if not rc:
            continue
          imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
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
    if self.path.endswith('.html'):
      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write('<html><head></head><body>')
      self.wfile.write('<img src="http://0.0.0.0:8080/cam.mjpg"/>')
      self.wfile.write('</body></html>')
      return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

def main():
  global capture
  capture = cv2.VideoCapture(1)
  capture.set(3,320)
  capture.set(4,320)
  global img
  try:
    server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
    print "server started"
    server.serve_forever()
  except KeyboardInterrupt:
    capture.release()
    server.socket.close()

if __name__ == '__main__':
  main()

