# import the necessary modules
from detection_module import *
from notification_module import *
from utils import *

# import the necessary packages
import cv2
import queue
import time
import threading
import tensorflow as tf
from object_detection.utils import label_map_util
from openal import oalGetListener
import imutils

# CONSTANTS
total_time = -1 # Total time of execution. Can be set to a specific value for testing or to -1 to run indefinitely
MAX_DISTANCE_CM = 800  # Value expressed in centimeters
MAX_ANGLE_LENSE_X = 160  # Value expressed in degrees
MAX_ANGLE_LENSE_Y = 120  # Value expressed in degrees
camera_offset_cm = 10  # Value expressed in centimeters
offset_adjust = 300  # Constant Value that depends on the cameras used and lets us calculate distance
W = 320  # Width of the images taken by the camera
H = 240  # Height of the images taken by the camera
MIN_CONFIDENCE = 0.5  # Minimum Confidence accepted from the Detection Model

# MODEL INITIALIZATION
CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person",
           "Sculpture", "Street light", "Table", "Traffic light", "Traffic sign", "Tree", "Pozo", "Baliza", "Cono"]
PATH_TO_LABELS = "./models/ssd_trained_model/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "./models/ssd_trained_model/saved_model"

# TFLITE is not being used
# PATH_TO_TFLITE_MODEL = "./models/ssd_trained_model/model.tflite"

# Load label_map
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


# Bufferless VideoCapture
class VideoCapture:
    def __init__(self, name):
        webcam = cv2.VideoCapture(name)
        webcam.set(3, 120)
        webcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap = webcam
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            time.sleep(0.5)
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()


def run_notification(sources, debug):
    coords = [source["cartesian_coords"] for source in sources]

    if debug:
        print(f"Notification-Step: List of Sources {coords}")

    for source in sources:
        if source["class"] != "Pozo":
            play_sound(3 * source["cartesian_coords"][0], source["cartesian_coords"][1] / 2, 0)
        else:
            play_pozo_sound(3 * source["cartesian_coords"][0], source["cartesian_coords"][1] / 2, 0)


def run_detection(i, display, debug):
    images = []

    for idx in [0, 1]:
        stream = cameras[idx]
        frame = stream.read()
        frame = imutils.resize(frame, height=240, width=320)
        images.append(cv2.rotate(frame, rotations[idx]))

    sources, image = detect_objects_tf(images, interpreter, display)

    if display:
        cv2.imshow("Camera", image)

        if len(sources) > 0:
            if i == 99:
                i = 0   # Save a maximun of 100 images
            else:
                i = i + 1
            if debug:
                print(f"Detection-Step: Saving Image in ./result/imagen_{i}.png")
                cv2.imwrite(f"./result/imagen_{i}.png", image)  # Save image for debugging
        else:
            print(f"Detection-Step: No Objects Detected.")

    return sources, i


if __name__ == "__main__":
    listener = oalGetListener()
    listener.set_position([0, 0, 0])
    play_start_sound()  # Start Sound to Notify Initialization Started

    display = False
    debug = False

    print("[INFO] Loading Detection Model...")
    # Using TF MODEL
    interpreter = tf.saved_model.load(PATH_TO_SAVED_MODEL)

    # WHEN TFLITE MODEL
    # interpreter = tf.lite.Interpreter(model_path=PATH_TO_TFLITE_MODEL)
    # interpreter.allocate_tensors()

    # Cameras Initialization
    cameras = []
    print("[INFO] Opening Cameras...")
    for port in [0, 2]:
        webcam = VideoCapture(port)
        cameras.append(webcam)

    time.sleep(2)
    rotations = [cv2.ROTATE_180, cv2.ROTATE_180]    # Cameras are positioned up-side-down

    start_time = time.time()
    print("[INFO] Starting Job")
    play_start_sound()  # Start Sound to Notify Initialization Finished

    i = 0
    while (time.time() - start_time) < total_time or total_time == -1:
        start_det_time = time.time()
        sources, i = run_detection(i, display, debug)
        print(f"Detection took: {time.time() - start_det_time} s")
        start_not_time = time.time()
        run_notification(sources, debug)
        print(f"Notification took: {time.time() - start_not_time} s")

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            for cap in cameras:
                cap.release()
            break

    print("[INFO] Job Finished")
