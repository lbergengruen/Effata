# import the necessary packages
from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2
import threading
from threading import Condition

from detection_module import *

cam_ports= [0,2]
names = ['Cam #1', 'Cam #2']

def new_thread(i,sem,frames):
    if i<2:
        webcam = cv2.VideoCapture(cam_ports[i])
        webcam.set(3,160)
        webcam.set(4,120)
        time.sleep(2.0)
        run_cam(i, webcam,sem,frames)
    else:
        run_display(i, sem,frames)
        
def run_display(i, sem,frames):
    print(f"Starting thread Display")
    while True:        
        
        cv2.imshow(names[0], frames[0])
        cv2.imshow(names[1], frames[1])
        
        sem.notifyAll()
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

def run_cam(i, webcam,sem, frames):
    print(f"Starting thread {names[i]}")
    while True:
        rval, frame = webcam.read()
        frames.append(frame)
        #final_result, frame = detect_objects([frame], net)
        #cv2.imshow(names[i], frame)
        sem.wait(i)
        key = cv2.waitKey(1) & 0xFF
        #if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

global frames
frames=[]
simplethread = []
sem = Condition()

for i in range(3):
    # arranque y comienzo de hilo num i+1
    simplethread.append(threading.Thread(target=new_thread, args=[i,sem,frames]))
    simplethread[-1].start()

for i in range(3):
    # esperamos que acabe el hilo num i
    simplethread[i].join()

cv2.destroyAllWindows()