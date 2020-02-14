from distutils.cmd import Command
from setuptools import setup, find_packages
from distutils.errors import DistutilsError, DistutilsExecError

import sys

if sys.version_info.major < 3:
    sys.exit('Sorry, Python2 is not supported. Please use Python3!')

setup(
    name='MotionDetection',
    version='2.0.1',
    url='https://github.com/amboxer21/MotionDetection',
    license='GPL-3.0',
    author='Anthony Guevara',
    author_email='amboxer21@gmail.com',
    description="A DIY CCTV system that monitors motion from a USB camera on an Raspberry Pi. "
        + "It takes a burst of pictures then E-mails them to you. You can also view the live feed from your phohne.",
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
    data_files=[
        ('/usr/local/bin/', ['src/heart.py']),
        ('/usr/local/bin/', ['src/motiondetection.py']),
        ('/etc/motiondetection/', ['src/etc/motiondetection/motiondetection.cfg']),
        ('/home/pi/.motiondetection/scripts/', ['src/cronjob/is_heartbeat_running.sh']),
        ('/home/pi/.motiondetection/scripts/', ['src/cronjob/is_motiondetection_running.sh']),
        ('/home/pi/.motiondetection/scripts/', ['src/cronjob/manage_motiondetection_data.py'])
    ],
    zip_safe=True,
    setup_requires=['Pillow','opencv-python','flask'],
)
