# Overclocking your Pi

https://wiki.archlinux.org/title/CPU_frequency_scaling?fbclid=IwAR3iuO9hOSRrgXWf3QmQq-dj5Bly71AgFpAYOQxKQCzf2CzFlvKepzBLsxI#Scaling_governors

![187305133_176992287556441_4271946398981680622_n_gimped](https://user-images.githubusercontent.com/2100258/118826518-8d903280-b889-11eb-88b6-48e2384d4ff2.jpg)


![2021-05-19-09:51:42_scrot](https://user-images.githubusercontent.com/2100258/118825254-8583c300-b888-11eb-85d2-4408aa29b104.png)


![2021-05-19-09:51:39_scrot](https://user-images.githubusercontent.com/2100258/118825295-8fa5c180-b888-11eb-8eef-96d5d6f3d039.png)


![2021-05-19-10:58:38_scrot](https://user-images.githubusercontent.com/2100258/118835746-473ed180-b891-11eb-802b-dbb8b316d64d.png)

## /boot/config.txt
```
kernel=kernel7l-custom.img
dtparam=i2c1=on

[all]
over_voltage=6
arm_freq=2000
arm_freq_min=1950
gpu_freq=750
```


sudo emerge -av media-libs/raspberrypi-userland stress-ng

sudo watch -n 1 vcgencmd measure_clock arm

sudo stress-ng --cpu 4 --io 4 --vm 2 --vm-bytes 128M --fork 4 --timeout 60s
