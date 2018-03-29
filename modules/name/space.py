#!/usr/bin/env python

import sys

class NameSpace():

    def count(variable=0,option=None):
        print("option => " + option)

    def isSent(variable=False,option=None):
        print("option => " + option)

    def isMoving(variable=True,option=None):
        print("option => " + option)

    def killCamera(variable=False,option=None:
        print("option => " + option)

    def streamCamera(variable=None,option=None):
        print("option => " + option)

    options = {
        0 : count,
        1 : isSent,
        2 : isMoving,
        3 : killCamera,
        4 : streamCamera,
    }

if __name__ == '__main__':
    nameSpace = NameSpace()
    nameSpace.options[int(sys.argv[1])](sys.argv[2])
