#!/bin/sh
# launcher.sh

# xhost +
# xhost local:root

# GPS CONFIG
echo GPS CONFIG
sudo systemctl stop gpsd.socket
sudo gpsd /dev/serial0 -F /var/run/gpsd.sock

# sudo systemctl stop serial-getty@serial0.service
# sudo systemctl disable serial-getty@ttyS0.service
# sudo systemctl stop serial-getty@ttyS0.service

# navigate to home directory, then to this directory, then execute python script, then back home

# cd /
echo Running main
cd /home/pi/Desktop/Effata/src
sudo -u pi LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 main.py
# cd /
