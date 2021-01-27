# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2

# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")
webcam1 = cv2.VideoCapture(0)
webcam1.set(3,160)
webcam1.set(4,120)

webcam2 = cv2.VideoCapture(2)
webcam2.set(3,160)
webcam2.set(4,120)

names = ['Cam #1', 'Cam #2']
rotations = [cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE]
cameras = [webcam1, webcam2]

time.sleep(2.0)


while True:
    # initialize the list of frames that have been processed
    frames = []
    i = 0
    # loop over the frames and their respective motion detectors
    for idx in [0, 1]:
        stream = cameras[idx]
        resp, frame = stream.read()
        frames.append(cv2.rotate(frame, rotations[idx]))
    
        # increment the total number of frames read and grab the 
        # current timestamp
        
        timestamp = datetime.datetime.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        # loop over the frames a second time
        
        # draw the timestamp on the frame and display it
        cv2.putText(frame, ts, (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.imshow(names[i], frame)
        i=i+1
    # check to see if a key was pressed
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()