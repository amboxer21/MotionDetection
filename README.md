# MotionDetection
>
**Description:** A system that monitors motion from a webcam and allows remote viewing of the webcam from an android app. The system takes pictures when it detects motion then emails those pictures. The android app allows you to remotely view the cam anytime. The motion detection system can be controlled with a white list so you're not spammed while your home.

### [Build Options]

#### **CMAKE BUILD OPTIONS FOR OpenCV:** 

```python
sudo cmake -DCAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DINSTALL_PYTHON_EXAMPLES=ON -DWITH_V4L=ON -DWITH_OPENGL=ON -DWITH_QT=OFF -DOPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib/modules -DBUILD_EXAMPLES=ON -DARCH=ARMV7 .. && sudo make -j3
```

#### **CMAKE BUILD OPTIONS for OpenCV on my Gentoo box**
```python
sudo cmake -DCAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local/opencv-3.4.3 -DINSTALL_PYTHON_EXAMPLES=ON -DWITH_V4L=ON -DWITH_OPENGL=ON -DWITH_OPENCL=OFF -DWITH_VTK=OFF -DWITH_QT=OFF -DOPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib/modules -DBUILD_EXAMPLES=ON -DARCH=ARMV7 .. && sudo make -j3
```

#### **FFMpeg configure options**

>sudo ./configure --enable-libv4l2 --enable-opengl --enable-libmp3lame


> **NOTE** ^^ Above build depends on opencv_contrib being on build3.4 not master!!

### [System Component Versions]

#### **GCC VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ dpkg -s gcc | grep ^Version
```

>Version: 4:4.9.2-2

#### **CMAKE VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ cmake --version
```

>cmake version 3.5.1

#### **OpenCV VERSION**

```python
aguevara@anthony ~ $ opencv_version 
```

>2.4.13.6

#### **FFMPEG VERSION**

```python
pi@raspberrypi:~/Documents/Python/MotionDetection $ ffmpeg -version
```

```python
ffmpeg version 3.4.5 Copyright (c) 2000-2018 the FFmpeg developers
built with gcc 4.9.2 (Raspbian 4.9.2-10+deb8u1)
configuration: --enable-libmp3lame --enable-libv4l2 --enable-opengl
libavutil      55. 78.100 / 55. 78.100
libavcodec     57.107.100 / 57.107.100
libavformat    57. 83.100 / 57. 83.100
libavdevice    57. 10.100 / 57. 10.100
libavfilter     6.107.100 /  6.107.100
libswscale      4.  8.100 /  4.  8.100
libswresample   2.  9.100 /  2.  9.100
```

#### ** BUILT WITH:**

>ffmpeg-3.4.5

>cmake version 3.5.1

>opencv-2.4.13.6

>opencv-3.1.0

>opencv_contrib-3.1.0

### [Download Links]

[OpenCV 2.4.13.6](https://github.com/opencv/opencv/archive/2.4.13.6.zip)

[OpenCV open_contrib](https://github.com/opencv/opencv_contrib/tree/3.4)

#### **DEPS:**

```python
sudo apt-get install build-essential pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python2.7-dev python3-dev 
```

here is a video demonstrating the program https://youtu.be/ZDyZsqIcBnk
