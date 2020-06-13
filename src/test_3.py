import cv2
import time
import threading
from threading import Condition

from detection_module import *
from notification_module import *

#CONSTANTES
WAVE_FILE = WaveFile("agudo5s.wav")
NTHREADS = 2
cam_ports = [0, 2]


def playSound(x,y,z,tipo):
    alDistanceModel(AL_EXPONENT_DISTANCE)
    buffer = Buffer(WAVE_FILE)
    source = Source(buffer)
    
    source.set_source_relative(True)
    v1 = (x,y,z)
    source.set_position(v1)
    source.set_reference_distance(0.5)
    source.set_rolloff_factor(0.5)
    pitch = 0.3
    source.set_pitch(pitch)
    
    if tipo==1:
        beep_beep(source)
    if tipo==2:
        gradual_beep_short(source)
    if tipo==3:
        gradual_beep_long(source)
    if tipo==4:
        sin_beep(source)
    if tipo==5:
        gradual_beep_beep(source)

        
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

    while ((time.time() - start_time)<10):
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
            if (len(sources)>0):
                i=i+1
                print("Guardando Imagen")
                cv2.imwrite(f"./result/imagen_{i}.png",imagen)
            cv2.imshow("Camera", imagen)
            #t=time.time()- start_time -5
            #sources=[[t,0.5,0]]
            
            print(time.time()-initial)
            print("Detected")
            
def run_notification(sem):
    print("Running notification")
    global sources
    sources = []
    while ((time.time() - start_time)<10):
        with sem:
            sem.notifyAll()
            sem.wait(2)
            print("Notify")
            print(sources)
            for coords in sources:
                play_sound(coords[0],coords[1],coords[2],sys.argv[1])

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
