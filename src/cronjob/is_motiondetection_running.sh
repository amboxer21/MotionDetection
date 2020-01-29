#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/motiondetection.py" | wc -l` < 1 ]]; then 
    logger -i -t motiondetection "Motiondetection is not running, starting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo LD_PRELOAD=/usr/arm-linux-gnueabihf/lib/libatomic.so.1.2.0 /usr/bin/python3 /usr/local/bin/motiondetection.py --config-file=/etc/motiondetection/motiondetection.cfg &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/motiondetection.py" | wc -l` > 2 ]]; then 
    logger -i -t motiondetection "Restarting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/motiondetection.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/sudo LD_PRELOAD=/usr/arm-linux-gnueabihf/lib/libatomic.so.1.2.0 /usr/bin/python3 /usr/local/bin/motiondetection.py --config-file=/etc/motiondetection/motiondetection.cfg &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/motiondetection.py" | wc -l` < 2 ]]; then 
    logger -i -t motiondetection "Restarting motiondetection." -f /var/log/motiondetection.log
    /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python3 /usr/local/bin/motiondetection.py" | /usr/bin/awk '{print $2}'`;
    /usr/bin/sudo LD_PRELOAD=/usr/arm-linux-gnueabihf/lib/libatomic.so.1.2.0 /usr/bin/python3 /usr/local/bin/motiondetection.py --config-file=/etc/motiondetection/motiondetection.cfg &
else
    logger -i -t motiondetection "Motiondetection is running." -f /var/log/motiondetection.log
fi
