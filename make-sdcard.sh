#!/bin/bash

mountpoint=$(mount | awk '/mmcblk0p2/{print $3}');

if [[ $mountpoint ]] ; then
    sudo umount -R $mountpoint;
fi

echo "=> Partitioning sdcard.";
for n in {1..4}; do parted -a optimal /dev/mmcblk0 rm $n 2> /dev/null; done
sudo parted -a optimal /dev/mmcblk0 mkpart primary fat32 0% 513MB
sudo parted -a optimal /dev/mmcblk0 mkpart primary ext4 513MB 100%

echo "=> Creating FAT32 filesystem on /dev/mmcblk0p1.";
echo 'y' | sudo mkfs.vfat -F32 /dev/mmcblk0p1

echo "=> Creating EXT4 filesystem on /dev/mmcblk0p2.";
echo 'y' | sudo mkfs.ext4 /dev/mmcblk0p2

echo "=> Checking if mountpoint /mnt/pi exists.";
if [[ -e /mnt/pi ]] ; then
    echo "[ INFO ] Mountpoint /dev/pi exists.";
else
    sudo mkdir -p /mnt/pi;
    echo '[ WARNING ] /mnt/pi doesnt exist - creating it now.';
fi

echo "=> Mounting /dev/mmcblk0p2 on /mnt/pi";
sudo mount /dev/mmcblk0p2 /mnt/pi;

echo "=> Checking if mountpoint /mnt/pi/boot exists.";
if [[ -e /mnt/pi/boot ]] ; then
    echo "[ INFO ] Mountpoint /dev/pi/boot exists.";
else
    sudo mkdir -p /mnt/pi/boot;
    echo '[ WARNING ] /mnt/pi/boot doesnt exist - creating it now.';
fi

echo "=> Mounting /dev/mmcblk0p1 on /mnt/pi/boot";
sudo mount /dev/mmcblk0p1 /mnt/pi/boot;

echo "=> Unpacking tarball onto your sdcard.";
tar -xzvf pi.tar.gz -C /mnt/pi/ ;

echo "=> Unmounting your sdcard now.";
sudo umount -R /mnt/pi ;
