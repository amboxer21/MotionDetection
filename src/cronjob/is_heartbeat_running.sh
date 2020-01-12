#!/bin/bash

if [[ `/bin/ps aux | /usr/bin/awk '/^root.*:[0-9]{1,2}.*heart.py/{if($11 !~ /sudo|vim|awk/) print $2}' | wc -l` -eq 0 ]]; then 
    /usr/bin/sudo logger -i -t heartbeat "Heartbeat is not running, starting heartbeat." -f /var/log/motiondetection.log
    /usr/bin/sudo /usr/bin/python3 /usr/local/bin/heart.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /usr/bin/awk '/^root.*:[0-9]{1,2}.*heart.py/{if($11 !~ /sudo|vim|awk/) print $2}' | wc -l` -gt 1 ]]; then 
    /usr/bin/sudo logger -i -t heartbeat "Restarting heartbeat." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/heart.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/sudo /usr/bin/python3 /usr/local/bin/heart.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /usr/bin/awk '/^root.*:[0-9]{1,2}.*heart.py/{if($11 !~ /sudo|vim|awk/) print $2}' | wc -l` -eq 1 ]]; then 
    /usr/bin/sudo logger -i -t heartbeat "Heartbeat is running." -f /var/log/motiondetection.log
fi
