#!/bin/bash

if [[ `ps aux | egrep -i "[0-9]*:[0-9]* python motiondetection.py -[pe] .* -[pe] .*$" | wc -l` < 1 ]]; then 
	/usr/bin/python /home/pi/Documents/Python/MotionDetection/MotionDetection.py -e 'example@gmail.com' -p 'password';
fi

if [[ `ps aux | egrep -i "[0-9]*:[0-9]* python motiondetection.py -[pe] .* -[pe] .*$" | wc -l` > 1 ]]; then 
	kill -9 `ps aux | egrep -i "motiondetection.py" | awk '{print $2}'`;
fi
