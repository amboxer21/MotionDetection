#!/usr/bin/env python

import os,re

def video_id():
    _ids = []
    for _file in os.listdir('/dev/'):
        name = re.search("(\wideo)(\d)", _file, re.M | re.I)
        #name = re.search("(tty)(\d+)", _file, re.M | re.I)
        if name is not None:
            _ids.append(int(name.group(2)))
    return min(_ids)

if __name__ == '__main__':
    print video_id()
