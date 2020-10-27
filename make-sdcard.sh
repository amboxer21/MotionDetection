#!/bin/bash

if [[ ! -e $(ls pi.tar.gz 2> /dev/null) ]] ; then
    echo "[ ERROR ] The pi.tar.gz tarball needs to be in the same directory as this script.";
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
