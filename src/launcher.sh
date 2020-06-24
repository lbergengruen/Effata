#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /
cd /home/pi/Desktop/Effata/src
sudo LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3 main.py
cd /
