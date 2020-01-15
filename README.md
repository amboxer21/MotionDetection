# MotionDetection for Python3 on the Raspberry Pi 4 B

**Disclaimer:** The current code base does not work with anything other than a Raspberry Pi 4 B. The E-mails are sent to sshmonitorapp@gmail.com by default. Please change this address!

**Notice:** I am currently in need of a new RPI3 B+ and until I get one, everything has been moved to an RPI4 B. I will leave the RPI3 B+ image link up and available. Though the image for the RPI3 needs a bit of tweaking on the command line once it is installed. Things like the static route in place, the entry in wpa_suuplicant.conf to connect to an AP, etc. - small tweaks. On the other hand, the RPI4 image is complete and will just boot up if you use a wired connection.

**Description:**  This system is called MotionDetection and it monitors motion from a USB webcam on a Raspberry Pi using the OpenCV API. Once motion is detected by the system, it takes a picture of what set the motion detection software off and E-mails that picture to you. It also affords the ability to remotely view that webcam from an android app from anywhere in the world at anytime. So after you’re notified via E-mail, then you have the option of checking the camera’s live feed if you’d like. This system is highly configurable and stable! Donate [here](https://paypal.me/motiondetection) if you'd like. You can contact me via E-mail if you have any questions at amboxer21@gmail.com.

A video demo can be found [HERE](https://www.youtube.com/watch?v=ZDyZsqIcBnk).

A `Raspberry Pi 3 B+` **image** can be found [HERE](https://drive.google.com/file/d/11fAc2o3DcJfO78mSmx6JLptXjQdwnBMb).

A `Raspberry Pi 4 B`  **image** can be found [COMING SOON]().

---

### [Login Credentials]
#### <**Raspberry Pi**>

**Username:** `pi`

**Password:** `raspberry`

#### <**Wi-Fi**> (NOT yet working)

**Username:** `Guest`

**Password:** `ping*omit`

---

### [Remote Access]
> The IP address used for remote access depends on the type of router that you are using. I have included network routes for both 192. and 10. IP ranges. You should just be able to power the device up, plug in an ethernet cable and access the Pi remotely with either of these addresses.

**IP Address:** `192.168.1.235` or `10.0.0.235`

**Port Number:** `1194`

**Command to remotely access Pi:** `ssh -p1194 pi@192.168.1.235` or `ssh -p1194 pi@10.0.0.235`

---

### [System Component Versions]

#### **SYSTEM OS VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ readarray -t a < <(lsb_release -irs); echo "${a[@]}"
```

>Raspbian 10

#### **GCC VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ dpkg -s gcc | grep ^Version
```

>Version: 4:8.3.0-1+rpi2

#### **CMAKE VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ cmake --version
```

>cmake version 3.13.4

#### **OpenCV Python VERSION**

```javascript
pi@raspberrypi:~ $ python -c 'import cv2; print(str(cv2.__version__))'
```
>4.1.1

#### **FFMPEG VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ ffmpeg -version
```

```python
ffmpeg version 4.1.4-1+rpt6~deb10u1 Copyright (c) 2000-2019 the FFmpeg developers
built with gcc 8 (Raspbian 8.3.0-6+rpi1)
configuration: --prefix=/usr --extra-version='1+rpt6~deb10u1' --toolchain=hardened --incdir=/usr/include/arm-linux-gnueabihf --enable-gpl --disable-stripping --enable-avresample --disable-filter=resample --enable-avisynth --enable-gnutls --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libcodec2 --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm --enable-libjack --enable-libmp3lame --enable-libmysofa --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librsvg --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzmq --enable-libzvbi --enable-lv2 --enable-omx --enable-openal --enable-opengl --enable-sdl2 --enable-omx-rpi --enable-mmal --enable-neon --disable-vaapi --disable-vdpau --enable-rpi --enable-libdc1394 --enable-libdrm --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libx264 --enable-shared --libdir=/usr/lib/arm-linux-gnueabihf --cpu=arm1176jzf-s --arch=arm
libavutil      56. 22.100 / 56. 22.100
libavcodec     58. 35.100 / 58. 35.100
libavformat    58. 20.100 / 58. 20.100
libavdevice    58.  5.100 / 58.  5.100
libavfilter     7. 40.101 /  7. 40.101
libavresample   4.  0.  0 /  4.  0.  0
libswscale      5.  3.100 /  5.  3.100
libswresample   3.  3.100 /  3.  3.100
libpostproc    55.  3.100 / 55.  3.100

```

---

### [DEPS]

**Debian:**
> Needs to be fixed to make more accurate!
```python
sudo apt-get install build-essential pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python2.7-dev python3-dev 
```

---

### [DEMO]

Here is an older(but still relevant) [video](https://www.youtube.com/watch?v=ZDyZsqIcBnk) demonstrating the program. Which can also be found at the top of this page.

---

### [SCREEN SHOTS]

> **MotionDetection System**

![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171140_scaled-250x500.png)
![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171159_scaled-250x500.png)
![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171209_scaled-250x500.png)
