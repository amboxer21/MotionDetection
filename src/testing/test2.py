import cv2
import multiprocessing

class VideoFeed(type):
    def __new__(meta,name,bases,dct):
        return super(VideoFeed, meta).__new__(meta, name, bases, dct)
    def __init__(cls,name,bases,dct):
        if not hasattr(cls,'video_capture'):
            cls.video_capture = None
        super(VideoFeed,cls).__init__(name,bases,dct)

    def capture(cls):
        cls.video_capture = cv2.VideoCapture(0)
        cls.video_capture.set(3,320)
        cls.video_capture.set(4,320)
        print cls.video_capture
        return cls.video_capture

    def release(cls):
        print('Deleting cam')
        del(cls.video_capture) 

class New(object):

    __metaclass__ = VideoFeed

    def test_func_one(self,one):
        New.capture()
        New.release()
        pass

    def test_func_two(self,two):
        pass

class Old(object):

    __metaclass__ = VideoFeed

    def test_func_one(self,one):
        Old.capture()
        Old.release()
        pass

    def test_func_two(self,two):
        pass


if __name__ == '__main__':
    new = New()
    old = Old()
    new.test_func_one('new')
    old.test_func_one('old')
    #multiprocessing_queue = multiprocessing.Queue()
    #process_two   = multiprocessing.Process(target=new.test_func_one, args=(multiprocessing_queue,))
    #process_three = multiprocessing.Process(target=new.test_func_two, args=(multiprocessing_queue,))
    #process_two.start()
    #process_three.start()
