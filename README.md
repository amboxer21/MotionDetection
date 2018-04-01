# MotionDetection

A system that monitors motion from a webcam and allows remote viewing of the webcam from an android app. The system takes pictures when it detects motion then emails those pictures. The android all allows you to remotely view the cam anytime.

#### **CMAKE BUILD OPTIONS FOR OpenCV:** 

```python
sudo cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_PYTHON_EXAMPLES=ON -DOPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib-3.1.0/modules -DBUILD_EXAMPLES=ON ..
```

#### **OpenCV VERSION**

```python
aguevara@anthony ~ $ opencv_version 
```

>2.4.13.6

#### **OpenCV DOWNLOAD LINK:**

Download [OpenCV 2.4.13.6](https://github.com/opencv/opencv/archive/2.4.13.6.zip)

#### ** BUILT WITH:**

>ffmpeg-3.0.11

>cmake version 3.5.1

>opencv-2.4.13.6

>opencv-3.1.0

>opencv_contrib-3.1.0

#### **DEPS:**

```python
sudo apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libatlas-base-dev gfortran python2.7-dev python3-dev 
```
