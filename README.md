# MotionDetection

A system that monitors motion from a webcam and allows remote viewing of the webcam from an android app. The system takes pictures when it detects motion then emails those pictures. The android all allows you to remotely view the cam anytime.

#### **CMAKE BUILD OPTIONS FOR OpenCV:** 

```python
sudo cmake -DCAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local -DINSTALL_PYTHON_EXAMPLES=ON -DWITH_V4L=ON -DWITH_OPENGL=ON -DWITH_QT=OFF -DOPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib/modules -DBUILD_EXAMPLES=ON -DARCH=ARMV7 .. && sudo make -j3
```

> **NOTE** ^^ Above build depends on opencv_contrib being on build3.4 not master!!

#### **CMAKE BUILD OPTIONS for OpenCV on Gentoo**
```python
sudo cmake -DCAKE_BUILD_TYPE=RELEASE -DCMAKE_INSTALL_PREFIX=/usr/local/opencv-3.4.3 -DINSTALL_PYTHON_EXAMPLES=ON -DWITH_V4L=ON -DWITH_OPENGL=ON -DWITH_OPENCL=OFF -DWITH_VTK=OFF -DWITH_QT=OFF -DOPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib/modules -DBUILD_EXAMPLES=ON -DARCH=ARMV7 .. && sudo make -j3
```

#### **OpenCV VERSION**

```python
aguevara@anthony ~ $ opencv_version 
```

>2.4.13.6

#### **OpenCV DOWNLOAD LINK:**

Download [OpenCV 2.4.13.6](https://github.com/opencv/opencv/archive/2.4.13.6.zip)

### **FFMpeg confiure options**

>sudo ./configure --enable-libv4l2 --enable-opengl

#### ** BUILT WITH:**

>ffmpeg-3.3.6

>cmake version 3.5.1

>opencv-2.4.13.6

>opencv-3.1.0

>opencv_contrib-3.1.0

#### **DEPS:**

```python
sudo apt-get install build-essential pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python2.7-dev python3-dev 
```
