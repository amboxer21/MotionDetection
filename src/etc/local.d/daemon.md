Add both .start files to the /etc/local.d directory and it will bring up the webconfigurator and motiondetection at boot time.

Make the file executable by everyone!
```
localhost ~ # for n in motiondetectiond.start webconfigurator.start cam-symlink.start; do chmod +x /etc/local.d/$n ; done
```

Confirm that the file is executable by everyone.
```
localhost ~/MotionDetection # for n in motiondetectiond.start webconfigurator.start cam-symlink.start; do ls -al /etc/local.d/$n ; done
-rwxr-xr-x 1 root root 2882 Oct 25 11:16 /etc/local.d/motiondetectiond.start
-rwxr-xr-x 1 root root 1451 Dec 31  1969 /etc/local.d/webconfigurator.start
-rwxr-xr-x 1 root root 106 Oct 25 11:14 /etc/local.d/cam-symlink.start
localhost ~/MotionDetection #
```


[Gentoo local.d wiki](https://wiki.gentoo.org/wiki//etc/local.d)
