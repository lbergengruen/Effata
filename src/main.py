import cv2
import time
import threading
from threading import Condition

from detection_module import *
from notification_module import *
from utils.py import *

#CONSTANTES
NTHREADS = 2
cam_ports = [0, 2]
total_time = 90
    

def new_thread(i, sem):
    if i==1:
        run_detection(sem)
    else:
        run_notification(sem)

def run_detection(sem):
    print("Running detection")
    global sources
    sources = []
    global cameras
    
    webcam1 = cv2.VideoCapture(cam_ports[0])
    webcam1.set(3,160)
    webcam1.set(4,120)

    webcam2 = cv2.VideoCapture(cam_ports[1])
    webcam2.set(3,160)
    webcam2.set(4,120)
    
    time.sleep(2.0)
    cameras = [webcam1, webcam2]
    names = ['Cam #1', 'Cam #2']
    i=0

    while ((time.time() - start_time)<total_time):
        with sem:
            sem.notifyAll()
            images = []
            
            initial = time.time()
            for stream in cameras:       
                rval, frame = stream.read()
                images.append(frame)
                #cv2.imshow(names[i], frame)
                #i=i+1
            sem.wait(2)
            
            coordinates, imagen = detect_objects(images, net)
            sources = stereo_match(coordinates[0], coordinates[1])
            print("Original sources: {}".format(sources))
            sources = reduce_sources(sources)
            print("Reduced sources: {}".format(sources))
            #if (len(sources)>0):
            #    i=i+1
            #    print("Guardando Imagen")
            #    cv2.imwrite(f"./result/imagen_{i}.png",imagen)
            #cv2.imshow("Camera", imagen)
            #t=time.time()- start_time -5
            #sources=[[t,0.5,0]]
            
            print(time.time()-initial)
            print("Detected")
            
def run_notification(sem):
    print("Running notification")
    global sources
    sources = []
    while ((time.time() - start_time)<total_time):
        with sem:
            sem.notifyAll()
            sem.wait(2)
            print("Notify")
            #print(sources)
            for coords in sources:
                play_sound(coords[0],coords[1],coords[2])

sem = Condition()
start_time = time.time()
simplethread = []

v = (0,0,0)
listener = oalGetListener()
listener.set_position(v)

for i in range(NTHREADS):
    # arranque y comienzo de hilo num i+1
    simplethread.append(threading.Thread(target=new_thread, args=[i+1, sem]))
    simplethread[-1].start()

for i in range(NTHREADS):
    # esperamos que acabe el hilo num i
    simplethread[i].join()
    #for cam in cameras:
    #    del(cam)

print("[*] all threads finished")
