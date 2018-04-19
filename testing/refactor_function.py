#!/usr/bin/env python

import time

def func(list,time):
    for dict in list:
        for d in dict:
            print("self.start_thread(self.update('" + d + "','" + dict[d] + "'))")
            print("time.sleep(" + str(time) + ")")

def sock_opts(list,time):
    for dict in list:
        for d in dict:
            #self.start_thread(self.update(d,dict[d]))
            time.sleep(int(time))
        

if __name__ == '__main__':
    func([{'kill_camera':'True'},{'stop_motion':'False'},{'kill_camera':'False'}],1)

"""
print("Starting motion sensor!")
killCamera = True
self.start_thread(self.update('kill_camera','True'))
time.sleep(1)
stopMotion = False
self.start_thread(self.update('stop_motion','False'))
time.sleep(1)
killCamera = False
self.start_thread(self.update('kill_camera','False'))
time.sleep(1)
self.start_thread(Server().capture)
time.sleep(1)
"""
