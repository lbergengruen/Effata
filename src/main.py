import numpy as np
import cv2
import argparse
import time
import PIL
from PIL import Image
import matplotlib.pyplot as plt
import math
import sys
from openal import *
import random
import threading
from threading import Condition
from random import randint

#CONSTANTES
WEIGHTS = '../YOLO v3/yolov3.weights'
CONFIG = '../YOLO v3/yolov3.cfg'
CLASES = '../YOLO TINY/yolov3-tiny.txt'
MAX_DISTANCE_CM = 500 #5 metros
MAX_ANGLE_LENSE = 85 #En grados
W = 768
H = 576
NTHREADS = 2
WAVE_FILE = WaveFile("agudo5s.wav")

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]
net = cv2.dnn.readNetFromCaffe("./MobileNetSSD_deploy.prototxt.txt", "./MobileNetSSD_deploy.caffemodel") 

def detect_objects(orig_image_paths, net):
    orig_images = [cv2.imread(i) for i in orig_image_paths]
    images = [cv2.resize(i, (W, H)) for i in orig_images]
    w = images[0].shape[1]
    h = images[0].shape[0]
    final_result = []
    
    for image in images:
        result = []
        COLORS = np.random.uniform(0, 255, 3)
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > 0.2:
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = box.astype("int")
                
                label = "{}: {:.2f}%".format(CLASSES[idx], confidence*100)
                
                cv2.rectangle(images[0], (start_x, start_y), (end_x, end_y), COLORS, 2)
                y = start_y - 15 if start_y - 15 > 15 else start_Y + 15
                cv2.putText(images[0], label, (start_x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS, 2)
                result.append({"class": CLASSES[idx], "confidence": confidence*100, "coordinates":box})
        final_result.append(result)
    return final_result, images[0]

def stereo_match(left_boxes, right_boxes):
    camera_offset_cm = 5
    offset_adjust = 4300 # offset_adjust: SSD uses around 4300 and YOLO v3 uses around 30
#     objects = []
    coords = []

    for box1 in left_boxes:
        for box2 in right_boxes:
            if box1['class']==box2['class']:
                c1 = [(box1['coordinates'][0]+box1['coordinates'][2]/2),(box1['coordinates'][1]+box1['coordinates'][3]/2)]
                c2 = [(box2['coordinates'][0]+box2['coordinates'][2]/2),(box2['coordinates'][1]+box2['coordinates'][3]/2)]
                sqr_diff=math.sqrt((c1[0]-c2[0])*(c1[0]-c2[0]) + (c1[1]-c2[1])*(c1[1]-c2[1]))
                x = (c1[0]+c2[0])/2
                y = (c1[1]+c2[1])/2
                distance = camera_offset_cm/sqr_diff*offset_adjust
                if distance <= MAX_DISTANCE_CM:
                    center = [x,y]
                    angles = to_polar_coords(center)
                    cartesian_coords = to_cartesian_coords(angles[0],angles[1], distance)
                    coords.append(cartesian_coords)
#                     objects.append({"class":box1["class"], "coords": cartesian_coords})
    return coords

def to_polar_coords(center):
    im_center = [W/2, H/2]
    angle_x = math.asin(((center[0]-im_center[0])*math.sin(MAX_ANGLE_LENSE))/im_center[0])
    angle_y = math.asin(((center[1]-im_center[1])*math.sin(MAX_ANGLE_LENSE))/im_center[1])
    return [angle_x, angle_y]

def to_cartesian_coords(angle_x,angle_y, distance):
    distance_x = round((distance*(math.cos(angle_y))*(math.sin(angle_x)))/100, 3)
    distance_y = round((distance*(math.cos(angle_y))*(math.cos(angle_x)))/100, 3)
    distance_z = round((distance*(math.sin(angle_y)))/100, 3)
    return [distance_x, distance_y, distance_z]

# class threadSound (threading.Thread):
#     def __init__(self, x, y, z):
#         threading.Thread.__init__(self)
#         self.x = x
#         self.y = y
#         self.z = z
#     def run(self):
#         playSound(self.x,self.y,self.z)
        
def beep_beep(source):
    source.play()
    time.sleep(0.1)
    source.stop()
    time.sleep(0.05)
    source.play()
    time.sleep(0.1)
    source.stop()
    
def gradual_beep(source):
    source.play()
    gain = 8.0
    
#     while gain > 0.02:
#         source.set_gain(gain)
#         gain = gain - (gain/1.6)
#         time.sleep(0.05)
    
#     source.set_gain(0.0)
    time.sleep(0.7)
    source.stop()

def piano_beep(source):
    source.play()
    gain = 15.0
    
    while gain > 0.02:
        source.set_gain(gain)
        gain = gain - (gain/17)
        time.sleep(0.05)
    
    source.set_gain(0.0)
    time.sleep(0.4)
    source.stop()    
    
def play_sound(x,y,z):
    buffer = Buffer(WAVE_FILE)
    source = Source(buffer)
    
    source.set_source_relative(True)
    v1 = (x,y,z)
    source.set_position(v1)
    pitch = 0.5 + 0.3
    source.set_pitch(pitch)
    beep_beep(source)
#    gradual_beep(source)
#     piano_beep(source)
#     oalQuit()

def new_thread(i, sem):
    if i==1:
        run_detection(sem)
    else:
        run_notification(sem)

def run_detection(sem):
    print("Running detection")
    global sources
    while ((time.time() - start_time)<10):         
        with sem:
            sem.notifyAll()
            sem.wait(2)
            initial = time.time()
            coordinates, imagen = detect_objects(["./left.jpeg", "./right.jpeg"], net)
            sources = stereo_match(coordinates[0], coordinates[1])
            t=time.time()- start_time -5
            sources=[[t,0.5,0]]
            print(time.time()-initial)
            print("Detected")
            
def run_notification(sem):
    print("Running notification")
    global sources
    while ((time.time() - start_time)<10):
        with sem:
            sem.notifyAll()
            sem.wait(2)
            print("Notify")
            print(sources)
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

print("[*] all threads finished")