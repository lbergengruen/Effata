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


class MyThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        i = 0

        print("Starting " + self.name)
        while (time.time() - start_time) < total_time:
            if self.thread_id == 1:
                i = self.run_detection(i)
            elif self.thread_id == 2:
                self.run_notification()
            else:
                raise Exception(f"No thread has id: {i}")

            key = cv2.waitKey(1) & 0xFF

            # If the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        print("Exiting " + self.name)

    def run_notification(self):
        if not variable_lock.locked():
            variable_lock.acquire()

            print(f"{self.name}: List of Sources {sources}")

            for source in sources:
                play_sound(source[0], source[1], source[2])

            variable_lock.release()
        else:
            print("%s: %s" % (self.name, time.ctime(time.time())))

    def run_detection(self, i):

        if not variable_lock.locked():
            variable_lock.acquire()

            images = []

            for idx in [0, 1]:
                stream = cameras[idx]
                resp, frame = stream.read()
                images.append(cv2.rotate(frame, rotations[idx]))

            sources, image = detect_objects(images, net)

            variable_lock.release()
            cv2.imshow("Camera", image)

            if len(sources) > 0:
                i = i + 1
                print(f"{self.name}: Saving Image in ./result/imagen_{i}.png")
                cv2.imwrite(f"./result/imagen_{i}.png", image)

        print("%s: %s" % (self.name, time.ctime(time.time())))
        return i


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

    threads = []

    variable_lock = threading.Lock()
    detection_thread = MyThread(1, "Detection-Thread")
    notification_thread = MyThread(2, "Notification-Thread")

    detection_thread.start()
    notification_thread.start()

    # Add threads to thread list
    threads.append(detection_thread)
    threads.append(notification_thread)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print("[INFO] all threads finished")
