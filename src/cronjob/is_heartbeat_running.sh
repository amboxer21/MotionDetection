#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/heart.py" | wc -l` < 1 ]]; then 
    logger -i -t heartbeat "Heartbeat is not running, starting heartbeat." -f /var/log/motiondetection.log
    /usr/bin/python /usr/local/bin/heart.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/heart.py" | wc -l` > 2 ]]; then 
    logger -i -t heartbeat "Restarting heartbeat." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/heart.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/python /usr/local/bin/heart.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/heart.py" | wc -l` < 2 ]]; then 
    logger -i -t heartbeat "Restarting heartbeat." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/heart.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/python /usr/local/bin/heart.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
else
    logger -i -t heatbeat "Heartbeat is running." -f /var/log/motiondetection.log
fi
