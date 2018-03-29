#!/usr/bin/env python

import sys

class NameSpace():

    def count(self,option=None,variable=0):
        print("count ONE")
        print("option => " + option)

    def isSent(self,option=None,variable=False):
        print("option => " + option)
        print("isSent")

    def isMoving(self,option=None,variable=True):
        print("option => " + option)
        print("isMoving")

    def killCamera(self,option=None,variable=False):
        print("option => " + option)
        print("killCamera")

    def streamCamera(self,option=None,variable=None):
        print("option => " + option)
        print("streamCamera")

    def options(self,opt,var):
        option = {
            'count' : self.count,
            'isSent' : self.isSent,'isMoving' : self.isMoving,
            'killCamera' : self.killCamera,'streamCamera' : self.streamCamera,
        }
        option[opt](var)

if __name__ == '__main__':
    nameSpace = NameSpace()
    nameSpace.options(sys.argv[1],sys.argv[2])
