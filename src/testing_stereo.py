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

coordinates = [
	[
		{'class': 'Person', 'confidence': 47.45822846889496, 'coordinates': [0.15356755256652832, 0.11219483613967896, 0.9860690832138062, 0.916467010974884]}
	],
	[
		{'class': 'Person', 'confidence': 56.92932605743408, 'coordinates': [0.14653617143630981, 0.40028589963912964, 1.0, 0.9658510088920593]}
	]
]


coords = stereo_match(coordinates[0], coordinates[1])
print("Original sources: {}".format(coords))