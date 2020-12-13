import cv2
import time
import threading
from threading import Condition

from detection_module import *
from notification_module import *
from utils import *

#CONSTANTES
NTHREADS = 2
cam_ports = [0, 2]
total_time = 540
    

#def new_thread(i, sem):
#    if i == 1:
#        run_detection(sem)
#    else:
#        run_notification(sem)

def run_detection():
    i = 0
    images = []
            
    initial = time.time()
    for stream in cameras:       
        rval, frame = stream.read()
        images.append(frame)
            
    coordinates, imagen = detect_objects(images, net)
    cv2.imshow("Camera", imagen)
    
    sources = stereo_match(coordinates[0], coordinates[1])
    print("Original sources: {}".format(sources))
    #sources = reduce_sources(sources)
    #print("Reduced sources: {}".format(sources))
    #if (len(sources)>0):
    #    i=i+1
    #    print("Guardando Imagen")
    #    cv2.imwrite(f"./result/imagen_{i}.png",imagen)

    print(time.time()-initial)
    print("Detected")
            
def run_notification():
    print("Notify")
    for coords in sources:
        play_sound(coords[0],coords[1],coords[2])

v = (0,0,0)
listener = oalGetListener()
listener.set_position(v)

webcam1 = cv2.VideoCapture(cam_ports[0])
webcam1.set(3,160)
webcam1.set(4,120)

webcam2 = cv2.VideoCapture(cam_ports[1])
webcam2.set(3,160)
webcam2.set(4,120)

time.sleep(2.0)
cameras = [webcam1, webcam2]
names = ['Cam #1', 'Cam #2']

start_time = time.time()
sources = []

while ((time.time() - start_time)<total_time):
    run_detection()
    #run_notification()

print("[*] all threads finished")
