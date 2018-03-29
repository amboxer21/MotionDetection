#!/usr/bin/env python

import sys

class Space():

    def __init__(self,opt,var=None):
        option = {
            'count' : self.count, 
            'isSent' : self.isSent,
            'isMoving' : self.isMoving,
            'killCamera' : self.killCamera,
            'streamCamera' : self.streamCamera,
        }; option[opt](var)

    def count(self,option=None,variable=0):
        print("def count()")
        if option is not None:
            self.variable = option
            print("option => " + option)
            print("self.variable => " + self.variable)
        else:
            return variable

    def isSent(self,option=None,variable=False):
        if option is not None:
            self.variable = option
        else:
            return variable

    def isMoving(self,option=None,variable=True):
        print("option => " + option)
        print("isMoving")

    def killCamera(self,option=None,variable=False):
        print("option => " + option)
        print("killCamera")

    def streamCamera(self,option=None,variable=None):
        print("option => " + option)
        print("streamCamera")

if __name__ == '__main__':
    space = Space(sys.argv[1],sys.argv[2])
