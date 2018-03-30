# MotionDetection

A system that monitors motion from a webcam and allows remote viewing of the webcam from an android app. The system takes pictures when it detects motion then emails those pictures. The android all allows you to remotely view the cam anytime.

#### **CMAKE BUILD OPTIONS FOR OpenCV:** 

```python
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local -DWITH_V4L=ON -DWITH_OPENGL=ON -DWITH_QT=ON -DOPENCV_EXTRA_MODULES_PATH=modules -DBUILD_EXAMPLES=OFF
```

#### **OpenCV VERSION**

```python
aguevara@anthony ~ $ opencv_version 
```

>2.4.13.6

#### **OpenCV DOWNLOAD LINK:**

Download [OpenCV 2.4.13.6](https://github.com/opencv/opencv/archive/2.4.13.6.zip)
