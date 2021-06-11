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

print("[INFO] starting cameras...")
webcam1 = cv2.VideoCapture(0)
webcam1.set(3,160)
webcam1.set(4,120)

webcam2 = cv2.VideoCapture(2)
webcam2.set(3,160)
webcam2.set(4,120)

while True:
    # initialize the list of frames that have been processed
    frames = []

    # loop over the frames and their respective motion detectors
    rval, frame1 = webcam1.read()
    rval, frame2 = webcam2.read()

    #frames.append(frame)

    res, frame = detect_objects([frame1, frame2], net)
                
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Cam", frame)
    print(res)
    
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()

