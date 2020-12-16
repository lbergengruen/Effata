# import the necessary packages
from __future__ import print_function
import cv2
import time
import threading
from threading import Condition
import datetime
from detection_module import *
from notification_module import *
from utils import *

print("Sound Playing")
while True:
    play_sound(0.002, 0.556, 0.084)