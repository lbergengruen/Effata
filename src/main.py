# import the necessary packages
from detection_module import *
from notification_module import *
from utils import *

import cv2
import time
import threading
from threading import Condition
import tensorflow as tf
from object_detection.utils import label_map_util
from openal import oalGetListener

# CONSTANTS
NTHREADS = 2  # Number of threads to be created
cam_ports = [0, 2]  # USB Ports at which the cameras are connected
total_time = 540  # Total time of execution
MAX_DISTANCE_CM = 800  # Value expressed in centimeters
MAX_ANGLE_LENSE_X = 160  # Value expressed in degrees
MAX_ANGLE_LENSE_Y = 120  # Value expressed in degrees
camera_offset_cm = 10  # Value expressed in centimeters
offset_adjust = 300  # Constant Value that depends on the cameras used and lets us calculate distance
W = 320  # Width of the images taken by the camera
H = 240  # Height of the images taken by the camera
MIN_CONFIDENCE = 0.50  # Minimum Confidence accepted from the Detection Model

# MODEL INITIALIZATION
CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person",
           "Sculpture", "Street light", "Table", "Traffic light", "Traffic sign", "Tree", "Pozo", "Baliza", "Cono"]

PATH_TO_LABELS = "./models/final_model/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "./models/final_model/saved_model"

net = tf.saved_model.load(PATH_TO_SAVED_MODEL)
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


# def new_thread(i, sem):
#    if i == 1:
#        run_detection(sem)
#    else:
#        run_notification(sem)

def run_detection():
    images = []
    i = 0

    initial = time.time()
    for idx in [0, 1]:
        stream = cameras[idx]
        rval, frame = stream.read()
        images.append(cv2.rotate(frame, rotations[idx]))

    sources, imagen = detect_objects(images, net)
    cv2.imshow("Camera", imagen)

    print("Original sources: {}".format(sources))
    sources = reduce_sources(sources)
    print("Reduced sources: {}".format(sources))
    if len(sources) > 0:
        i = i + 1
        print(f"[INFO] Saving Image in ./result/imagen_{i}.png")
        cv2.imwrite(f"./result/imagen_{i}.png", imagen)

    print(time.time() - initial)
    print("Detected")


def run_notification():
    print("Notify")
    for source in sources:
        play_sound(source[0], source[1], source[2])


if __name__ == "__main__":
    print("[INFO] Loaded Detection Model...")
    
    listener = oalGetListener()
    listener.set_position([0, 0, 0])

    cameras = []
    
    print("[INFO] Opening Cameras...")
    for port in cam_ports:
        webcam = cv2.VideoCapture(port)
        webcam.set(3, 120)
        webcam.set(4, 160)
        cameras.append(webcam)

    rotations = [cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE]

    start_time = time.time()
    sources = []
    
    print("[INFO] Starting Job")
    while (time.time() - start_time) < total_time:
        run_detection()
        # run_notification()key = cv2.waitKey(1) & 0xFF

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    print("[*] all threads finished")
