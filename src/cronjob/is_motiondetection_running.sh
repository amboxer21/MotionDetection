#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/motiondetection.py" | wc -l` < 1 ]]; then 
    logger -i -t motiondetection "Motiondetection is not running, starting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo /usr/bin/python /usr/local/bin/motiondetection.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/motiondetection.py" | wc -l` > 2 ]]; then 
    logger -i -t motiondetection "Restarting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/motiondetection.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/sudo /usr/bin/python /usr/local/bin/motiondetection.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/motiondetection.py" | wc -l` < 2 ]]; then 
    logger -i -t motiondetection "Restarting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/motiondetection.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/sudo /usr/bin/python /usr/local/bin/motiondetection.py -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
else
    logger -i -t motiondetection "Motiondetection is running." -f /var/log/motiondetection.log
fi
