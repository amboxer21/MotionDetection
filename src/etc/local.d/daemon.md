Add both .start files to the /etc/local.d directory and it will bring up the webconfigurator and motiondetection at boot time.

Make the file executable by everyone!
```
localhost ~ # chmod +x /etc/local.d/{motiondetectiond.start, webconfigurator.start}
```

Confirm that the file is executable by everyone.
```
localhost ~ # ls -al /etc/local.d/{motiondetectiond.start, webconfigurator.start}
-rwxr-xr-x 1 root root 2865 Oct 25  2020 /etc/local.d/motiondetectiond.start
-rwxr-xr-x 1 root root 1429 Oct 25  2020 /etc/local.d/webconfigurator.start
localhost ~ #
```


(Gentoo local.d wiki)[https://wiki.gentoo.org/wiki//etc/local.d]
