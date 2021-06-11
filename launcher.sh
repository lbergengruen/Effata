#!/bin/sh
# launcher.sh

# GPS CONFIG
# echo GPS CONFIG
# sudo systemctl stop gpsd.socket
# sudo gpsd /dev/serial0 -F /var/run/gpsd.sock

# sudo systemctl stop serial-getty@serial0.service
# sudo systemctl disable serial-getty@ttyS0.service
# sudo systemctl stop serial-getty@ttyS0.service

# Prepare usb cameras
sudo rmmod uvcvideo
sudo modprobe uvcvideo nodrop=1 timeout=5000 quirks=0x80

# navigate to src directory, then execute python script, then back home
echo Running main
cd /home/pi/Desktop/Effata/src
sudo -u pi LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 main.py
cd /