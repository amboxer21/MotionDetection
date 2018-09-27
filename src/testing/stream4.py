#!/usrlocal/env python

import cv2
import time
import StringIO
import multiprocessing

from PIL import Image
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class Global(type):
    def __call__(cls, *args, **kwds):
        if not hasattr(cls, 'stream_camera'):
            cls.stream_camera = args[0]
        return type.__call__(cls, *args, **kwds)

class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print "(CamHandler.do_GET) - Streaming HTTPServer started"
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
        while True:
            try:
                (read_cam, image) = Stream.stream_camera.read()
                if not read_cam:
                    continue
                '''if self.kill_camera is True:
                    print "(CamHandler.do_GET) - Killing cam."
                    self.streamCamera.release()
                    break'''
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
                Stream.stream_camera.release()
                break
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    print("ThreadedHTTPServer started!")
    pass

class Stream(object):

    __metaclass__ = Global

    def __init__(self,stream_camera):
        self.stream_camera = stream_camera

    def stream_main(self,queue):
        print "(Stream.stream_main) - Streaming server initialized!"
        try:
            #stream_camera = cv2.VideoCapture(self.cam_location)
            #self.stream_camera.set(3,320)
            #self.stream_camera.set(4,320)
            server = ThreadedHTTPServer(('0.0.0.0', 5000), CamHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            self.stream_camera.release()
            server.socket.close()
        except Exception as eThreadedHTTPServer:
            print 'eThreadedHTTPServer',eThreadedHTTPServer
            pass

class Queue(object):

    def queue_process(self,func,queue):
        try:
            process = multiprocessing.Process(target=func, args=(queue,))
            process.start()
        except Exception as eQueueProcess:
            print "(Queue.queue_process) - Queue exception eQueueProcess => " + str(eQueueProcess)

if __name__ == '__main__':

    queue  = Queue()
    stream_camera = cv2.VideoCapture(0)
    stream_camera.set(3,320)
    stream_camera.set(4,320) 
    stream = Stream(stream_camera)
    multiprocessing_queue = multiprocessing.Queue()
    queue.queue_process(stream.stream_main,multiprocessing_queue)
