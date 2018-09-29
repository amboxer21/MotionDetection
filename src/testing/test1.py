import cv2
import multiprocessing

class decorator(object):
    def __init__(self, func):
        self.func  = func
    def __call__(self,*args):
        queue = args[len(args) - 1]
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(3,320)
        self.video_capture.set(4,320)
        queue.put(self.video_capture)
        print('Called {func} with args: {args}'.format(func=self.func.func_name,args=args))
        return self.func(*args)

class New(object):
    @decorator
    def test_func_one(x,y,queue):
        if not queue.empty():
            print 'queue.get()',queue.get()
        return x,y

    @decorator
    def test_func_two(value,queue):
        if not queue.empty():
            print 'queue.get()',queue.get()
        return value

if __name__ == '__main__':
    new = New()
    multiprocessing_queue = multiprocessing.Queue()
    process_one = multiprocessing.Process(target=new.test_func_one, args=(1,2,multiprocessing_queue))
    process_two = multiprocessing.Process(target=new.test_func_two, args=(555,multiprocessing_queue))
    process_one.start()
    process_one.join()
    process_two.start()
    process_two.join()
