# [Description]
This highly configurable framework monitors motion from a USB webcam on a Raspberry Pi using the OpenCV API. Once motion is detected by the system, it takes a picture of what set off the framework then E-mails the picture(s) to you. It also affords the ability to remotely view that webcam from an android app from anywhere in the world at anytime. So after you’re notified via E-mail, then you have the option of checking the camera’s live feed if you’d like. If you need an image made, I can make an sdcard for you and send it via USPS(mail). If you need an image or have any questions, send an E-mail to amboxer21@gmail.com.

### [Todo]
> Redisgn the Android app's UI. See GitHub issue [#50](https://github.com/amboxer21/MotionDetection/issues/50).
---

# MotionDetection(CCTV) with Python3 on the Raspberry Pi powered by Gentoo Linux

**Note:** You can send me an E-mail if you have any trouble and I will be happy to help you - `amboxer21@gmail.com`. 

### [Videos]

> **Demo from Aug 9, 2020**

Find a quick demo [HERE](https://youtu.be/_jswANI5GCg)

> **Booting**

Booting the system after installation [HERE](https://youtu.be/WJWTAXVIbQg)

> **Installing MotionDetection on an sdcard

POC of installation [HERE](https://youtu.be/L-uoW5sm6rA)

---

### [Credentials]
> For use with the installer script.

`Username`**:** pi

`Password`**:** RASPBERRY pi 3

---

### [Downloads]:

[ LATEST ] Download the Motiondetection system data tarball [HERE](https://drive.google.com/file/d/1w4ONR2b-pfmmrI5HVXqQJ0dEUTHzKViJ/view?usp=sharing).

**Notice:** ^^ This tarball is essential to buillding an sdcard! Without it the system won't work.

[ LATEST ] Download the stage3 tarball for the RPI3 and the RPI4 [HERE](http://gentoo.osuosl.org/releases/arm/autobuilds/current-stage3-armv7a_hardfp/stage3-armv7a_hardfp-20200509T210605Z.tar.xz).

**Notice:** ^^ This tarball is necessary if you want to roll your own image instead of using mine.

---

### [Installing MotionDetection on your PI]
> This is an installer script that needs to be run in the same directory as the pi tarball! The script works on both the Raspberry PI 3b and 4b!!
```javascript
#!/bin/bash

echo "[ INFO ] Checking for presence of pi.tar.gz tarball.";
if [[ -e $(ls pi.tar.gz 2> /dev/null) ]] ; then
    echo "[ INFO ] pi.tar.gz found.";
else
    echo "[ ERROR ] The pi.tar.gz tarball needs to be in the same directory as this script.";
    exit;
fi

echo "[ INFO ] Checking for presence of sdcard at /dev/mmcblk";
if (( var=$(sudo fdisk -l /dev/mmcblk0 1>& /dev/null) $? == 0 )) ; then
    echo "[ INFO ] Found sdcard.";
else
    echo "[ ERROR ] Cannot find sdcard.";
    exit;
fi

mountpoint=$(mount | awk '/mmcblk0p2/{print $3}');

if [[ $mountpoint ]] ; then
    sudo umount -R $mountpoint;
fi

echo "[ INFO ] Partitioning sdcard.";
for n in {1..4}; do parted -a optimal /dev/mmcblk0 rm $n 2> /dev/null; done
sudo parted -a optimal /dev/mmcblk0 mkpart primary fat32 0% 513MB
sudo parted -a optimal /dev/mmcblk0 mkpart primary ext4 513MB 100%

echo "[ INFO ] Creating FAT32 filesystem on /dev/mmcblk0p1.";
echo 'y' | sudo mkfs.vfat -F32 /dev/mmcblk0p1

echo "[ INFO ] Creating EXT4 filesystem on /dev/mmcblk0p2.";
echo 'y' | sudo mkfs.ext4 /dev/mmcblk0p2

echo "[ INFO ] Checking if mountpoint /mnt/pi exists.";
if [[ -e /mnt/pi ]] ; then
    echo "[ INFO ] Mountpoint /dev/pi exists.";
else
    sudo mkdir -p /mnt/pi;
    echo '[ WARNING ] /mnt/pi doesnt exist - creating it now.';
fi

echo "[ INFO ] Mounting /dev/mmcblk0p2 on /mnt/pi";
sudo mount /dev/mmcblk0p2 /mnt/pi;

echo "[ INFO ] Checking if mountpoint /mnt/pi/boot exists.";
if [[ -e /mnt/pi/boot ]] ; then
    echo "[ INFO ] Mountpoint /dev/pi/boot exists.";
else
    sudo mkdir -p /mnt/pi/boot;
    echo '[ WARNING ] /mnt/pi/boot doesnt exist - creating it now.';
fi

echo "[ INFO ] Mounting /dev/mmcblk0p1 on /mnt/pi/boot";
sudo mount /dev/mmcblk0p1 /mnt/pi/boot;

echo "[ INFO ] Unpacking tarball onto your sdcard.";
tar -xzf pi.tar.gz -C /mnt/pi/ ;

echo "[ INFO ] Unmounting your sdcard now.";
sudo umount -R /mnt/pi ;
```

Example script output:
```javascript
anthony@anthony ~ $ sudo bash make-sdcard.sh 
Password: 
[ INFO ] Checking for presence of pi.tar.gz tarball.
[INFO] pi.tar.gz found.
[ INFO ] Checking for presence of sdcard at /dev/mmcblk
[ INFO ] Found sdcard.
[ INFO ] Partitioning sdcard.
Information: You may need to update /etc/fstab.                           

Information: You may need to update /etc/fstab.                           

[ INFO ] Creating FAT32 filesystem on /dev/mmcblk0p1.                     
mkfs.fat 4.1 (2017-01-24)
[ INFO ] Creating EXT4 filesystem on /dev/mmcblk0p2.
mke2fs 1.45.5 (07-Jan-2020)
Discarding device blocks: done                            
Creating filesystem with 15511296 4k blocks and 3883008 inodes
Filesystem UUID: fb8a85ff-1c19-4e64-a0e4-80c1e49167f5
Superblock backups stored on blocks: 
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
	4096000, 7962624, 11239424

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (65536 blocks): done
Writing superblocks and filesystem accounting information: done   

[ INFO ] Checking if mountpoint /mnt/pi exists.
[ INFO ] Mountpoint /dev/pi exists.
[ INFO ] Mounting /dev/mmcblk0p2 on /mnt/pi
[ INFO ] Checking if mountpoint /mnt/pi/boot exists.
[ WARNING ] /mnt/pi/boot doesnt exist - creating it now.
[ INFO ] Mounting /dev/mmcblk0p1 on /mnt/pi/boot
[ INFO ] Unpacking tarball onto your sdcard.
[ INFO ] Unmounting your sdcard now.
anthony@anthony ~ $
```

---

### [Rolling a Raspberry Pi image]:

* Install base system

* Update your system

* Emerge rust-bin

* Emerge ffmpeg

* Emerge OpenCV

* Emerge mail utils
> emerge -av acct-group/mail acct-user/mail dev-perl/MailTools net-mail/mailbase

**NOTE:** It is important to emerge rust-bin because compiling the regular rust package takes up a lot of resources and is prone to breaking on the arm arch! You don't want to spend days hacking this install when you can just install the bin version!

### Installing base system
> Run the command below seperately from the rest of the script and wait for it to finish before continuing!
```javascript
umount -R /mnt/gentoo
parted /dev/mmcblk0 mklabel msdos
```

**Continue!**
```javascript
for n in {1..4}; do echo -e 'y' | parted /dev/mmcblk0 rm $n 2>/dev/null; done
parted /dev/mmcblk0 mkpart primary fat32 0% 513MB
parted /dev/mmcblk0 mkpart primary linux-swap 513MB 2561MB
parted /dev/mmcblk0 mkpart primary ext4 2561MB 100%
parted /dev/mmcblk0 p

mkfs.vfat -F32 /dev/mmcblk0p1
mkswap /dev/mmcblk0p2
echo 'y' | mkfs.ext4 /dev/mmcblk0p3

mount /dev/mmcblk0p3 /mnt/gentoo
mkdir /mnt/gentoo/boot
mount /dev/mmcblk0p1 /mnt/gentoo/boot

tar xzvf rpi4b.tar.gz
cd rpi4b
tar xzvf gentoo.tar.gz

time rsync -ra gentoo/* /mnt/gentoo/

wget http://gentoo.osuosl.org/releases/arm/autobuilds/current-stage3-armv7a_hardfp/stage3-armv7a_hardfp-20200509T210605Z.tar.xz
tar xvf stage3-armv7a_hardfp-20200509T210605Z.tar.xz -C /mnt/gentoo/

wget http://distfiles.gentoo.org/snapshots/portage-latest.tar.bz2
tar xjvf portage-latest.tar.bz2 -C /mnt/gentoo/usr

git clone --depth 1 git://github.com/raspberrypi/firmware/
cd firmware/boot
cp -r * /mnt/gentoo/boot/
cp -r ../modules /mnt/gentoo/lib/

echo -e "/dev/mmcblk0p1 /boot auto noauto,noatime 1 2\n/dev/mmcblk0p3 / ext4 noatime 0 1\n/dev/mmcblk0p2 none swap sw 0 0" >> /mnt/gentoo/etc/fstab

echo "dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty1 root=/dev/mmcblk0p3 rootfstype=ext4 elevator=deadline rootwait" > /mnt/gentoo/boot/cmdline.txt

cp /mnt/gentoo/usr/share/zoneinfo/America/New_York /mnt/gentoo/etc/localtime

echo "America/New_York" > /mnt/gentoo/etc/timezone

sed -i 's/^root:.*/root::::::::/' /mnt/gentoo/etc/shadow

cd

umount -R /mnt/gentoo
```

### Update your system
> I would suggest installing rust-bin before updating @world!
```
(1) emerge --sync
(2) emerge -av --deep --newuse --update @world
```

**Note:** Before updating your system, create this file and copy these contents into that file to circumvent the gpg syncing errors
```
anthony@anthony ~ $ cat /etc/portage/repos.conf/gentoo.conf 
[DEFAULT]
main-repo = gentoo

[gentoo]
location = /usr/portage
sync-type = rsync
auto-sync = yes
sync-uri = rsync://rsync.us.gentoo.org/gentoo-portage
sync-rsync-verify-metamanifest = no
anthony@anthony ~ $ 
```

### Emerge rust-bin
```
emerge -av rust-bin
```

### Compiling OpenCV
> Create these file and set the use flags before emerging OpenCV and ffmpeg!

**Note:** Install ffmpeg before installing OpenCV!

#### [Package USE Flags]
> /etc/portage/package.use/ffmpeg
```
virtual/ffmpeg encode mp3 threads mp3 threads x264 jack alsa blueray libv4l v4l lzma twolame opengl openssl oss pulseaudio sdl vorbis xvid gsm opus speex vaapi vdpau -theora -truetype -libav
media-video/ffmpeg alsa bzip2 encode gmp gpl hardcoded-tables iconv jack libv4l lzma mp3 network opengl openssl oss postproc pulseaudio sdl threads twolame v4l vorbis x264 x265 xvid zlib bluray cdio chromium cpudetection debug doc fontconfig gcrypt gnutls gsm libass libdrm openh264 opus speex svg vaapi wavpack vdpau -theora -truetype -static-libs -amrenc -amr
```

> /etc/portage/package.use/alsa-plugins
```
media-plugins/alsa-plugins pulseaudio
```

> /etc/portage/package.use/gst-plugins-base
```
media-libs/gst-plugins-base -opengl
```

> /etc/portage/package.use/libcrypt
```
virtual/libcrypt static-libs
```

> /etc/portage/package.use/libglvnd
```
media-libs/libglvnd X
```

> /etc/portage/package.use/libv4l
```
media-libs/libv4l jpeg
```

> /etc/portage/package.use/mesa
```
media-libs/mesa X
```

> /etc/portage/package.use/numpy
```
dev-python/numpy lapack
```

> /etc/portage/package.use/opencv
```
media-libs/opencv v4l png jpeg gstreamer python ffmpeg contrib lapack -opengl
```

> /etc/portage/package.use/openssl
```
dev-libs/openssl sslv3
```

> /etc/portage/package.use/zlib
```
sys-libs/zlib abi_x86_64 minizip
```

> /etc/portage/package.use/pulseaudio
```
media-sound/pulseaudio bluetooth jack dbus sox ofono-headset native-headset libsamplerate CPU_FLAGS_ARM: -neon
```

**NOTE:** For `pulseaudio`, the neon flags causes the compilation to crash when emerging if this flag is set.

> /etc/portage/package.use/gcc
```
sys-devel/gcc objc objc++ objc-gc
```

**NOTE:** For `GCC`, I ran into issues compiling cmake and the solution was to recompile gcc with these use flags. I had to recompile quite a few times. Compiling gcc with these USE flags in the beginning could save you the same trouble!

**`Error message:`**
```
-- Checking if compiler supports needed C++17 constructs - yes
-- Checking if compiler supports C++ make_unique
-- Checking if compiler supports C++ make_unique - no
-- Checking if compiler supports C++ unique_ptr
-- Checking if compiler supports C++ unique_ptr - no
CMake Error at CMakeLists.txt:107 (message):
  The C++ compiler does not support C++11 (e.g.  std::unique_ptr).


-- Configuring incomplete, errors occurred!
See also "/var/tmp/portage/dev-util/cmake-3.17.4-r1/work/cmake-3.17.4_build/CMakeFiles/CMakeOutput.log".
See also "/var/tmp/portage/dev-util/cmake-3.17.4-r1/work/cmake-3.17.4_build/CMakeFiles/CMakeError.log".
 * ERROR: dev-util/cmake-3.17.4-r1::gentoo failed (configure phase):
 *   cmake failed
```

#### [Masked packages]

> /etc/portage/package.mask/cmake
```
>=dev-util/cmake-3.17.4-r1
```

#### [Accept keywords]

> /etc/portage/package.accept_keywords/eigen
```
dev-cpp/eigen ~arm
```

> /etc/portage/package.accept_keywords/opencv
```
media-libs/opencv ~arm
```

#### [make.conf]

```javascript
# These settings were set by the catalyst build script that automatically
# built this stage.
# Please consult /usr/share/portage/config/make.conf.example for a more
# detailed example.
COMMON_FLAGS="-O2 -pipe -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=hard"
CFLAGS="${COMMON_FLAGS}"
CXXFLAGS="${COMMON_FLAGS}"
FCFLAGS="${COMMON_FLAGS}"
FFLAGS="${COMMON_FLAGS}"
FEATURES="ccache"
CCACHE_DIR="/var/cache/ccache
CPU_FLAGS_ARM="edsp neon thumb vfp vfpv3 vfpv4 vfp-d32 crc32 v4 v5 v6 v7 thumb2"

# WARNING: Changing your CHOST is not something that should be done lightly.
# Please consult https://wiki.gentoo.org/wiki/Changing_the_CHOST_variable before changing.
CHOST="armv7a-unknown-linux-gnueabihf"
USE="bluetooth ffmpeg jpeg png gif curl -X -pulseaudio -gtk -qt -qt5 -qt4 -consolekit -static-libs -cups -systemd"

# NOTE: This stage was built with the bindist Use flag enabled

# This sets the language of build output to English.
# Please keep this setting intact when reporting bugs.
LC_MESSAGES=C

```

---

### [Changing Motiondetection options using a GUI]:

You can change the options that the Motiondetection framework runs with by opening your favorite browser, entering your Rapsberry Pi's IP address - i.e., 192.168.1.232. Here you can change options like the E-mail that the pictures are sent to, burst mode count, etc. A short demonstration can be found [HERE](https://youtu.be/YYGSTYESsQk).

---

### [Resources]:
[stage3-armv7a_hardfp-20200509T210605Z.tar.xz](http://gentoo.osuosl.org/releases/arm/autobuilds/current-stage3-armv7a_hardfp/stage3-armv7a_hardfp-20200509T210605Z.tar.xz)

[Raspberry Pi Gentoo wiki](https://wiki.gentoo.org/wiki/Raspberry_Pi/Quick_Install_Guide)

[MotionDetection Framework rsync data](https://drive.google.com/file/d/1bJ7WJQeGAhr-r2pe-ITLRjM1wxJExrOK/view?usp=sharing)

[Android app to view camera's feed](https://github.com/amboxer21/MotionDetection/blob/master/src/SecureView-debug.apk)

---

# [Change Log]
>[ OLD ][**As of 2020-08-03**] Currently fixing up this repo's code and working on a new Gentoo based ISO image

>[ OLD ][**As of 2020-08-03**] You can now update the application's configuration options in the GUI using your favorite browser. Now all you have to do is power up the RPI/USB camera, open a browser, navigate to a specified URL, reload, then the program will use your updated options. Watch a short demo of the webconfigurator [HERE](https://youtu.be/YYGSTYESsQk).

>[ OLD ][**As of 2020-08-09**] The framework that runs on Raspbian has been deprecated in favor of Gentoo Linux. The Raspbian system will no longer be updated but will be left in tact. 

>[ OLD ][**As of 2020-08-09**] Daemon support was removed from the framework. You will either have to set it up yourself or roll an image. The image is plug-and-play, power up the RPI4b and it just works.

>[ OLD ][**As of 2020-08-09**] The gentoo install is complete and the system automaticcaly comes up on boot - The system is plug and play. 

>[ OLD ][**As of 2020-08-20**] The system would crash after being triggered. A new symlink feature caused the issue and I have since changed that symlink call to a copy(cp) call in the motiondetection.py file in this [commit](5117801ee95b0cc571626b4d704146f06c0ac3d8). New rsync data with the new changes has been uploaded this morning.

>[ OLD ][**As of 2020-10-28**] I have written an installer script named **make-sdcard.sh** that installs an image that works on my my Raspberry PI 3 and 4. The size of the card does not matter either. The idea of a DD'able system image has been put on the back burner for now. The installer script is super simple to use anyway!

>[ LATEST ][**As of 2020-11-20**] I have fixed the broken ANdroid app functionality. The remote veiwing of the live camera feed via android app is now working!

---

### [SCREEN SHOTS]

![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171140_scaled-250x500.png)
![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171159_scaled-250x500.png)
![alt text](https://github.com/amboxer21/MotionDetection/blob/master/src/screenshots/Screenshot_20181119-171209_scaled-250x500.png)
![alt_text](https://user-images.githubusercontent.com/2100258/89722342-98db3700-d9b6-11ea-8901-cb8b639b1248.png)

---

---

**Since `Nov 27, 2017`**
