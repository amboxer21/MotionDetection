from distutils.cmd import Command
from setuptools import setup, find_packages
from distutils.errors import DistutilsError, DistutilsExecError

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
        ('/usr/local/bin/webconfigurator/', ['src/webconfigurator/configure.py']),
        ('/etc/motiondetection/', ['src/etc/motiondetection/motiondetection.cfg.backup']),
        ('/usr/local/bin/webconfigurator/templates/', ['src/webconfigurator/templates/index.html']),
        ('/usr/local/bin/webconfigurator/templates/', ['src/webconfigurator/templates/invalid_credential_format.html'])
    ],
    zip_safe=True,
    install_requires=['Pillow','opencv-python','flask','click','itsdangerous','Werkzeug','jinja2','wtforms','email-validator','tensorflow','cvlib'],
)
