# Import the necessary packages
from __future__ import print_function
import datetime
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import warnings

warnings.filterwarnings('ignore')   # Suppressing Matplotlib warnings

print("[INFO] starting cameras...")
webcam1 = cv2.VideoCapture(0)
webcam1.set(3,120)
webcam1.set(4,160)
webcam2 = cv2.VideoCapture(2)
webcam2.set(3,120)
webcam2.set(4,160)

print("[INFO] Loading Detection Model...")
CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person", "Sculpture", "Street light", "Table", "Traffic light", "Traffic sign", "Tree", "Pozo", "Baliza", "Cono"]

PATH_TO_LABELS = "../models/final_model/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "../models/final_model/saved_model"

net = tf.saved_model.load(PATH_TO_SAVED_MODEL)

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

def detect_objects(images, net):
    final_result = []
    image_np_with_detections = np.array(images[1]).copy()
    
    for image in images:
        result = []
        image_np = np.array(image)
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = net(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # Detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        filtered_detections={'detection_anchor_indices': [], 'detection_scores': [],
                             'detection_boxes': [],
                             'detection_classes': [], 'raw_detection_boxes': [],
                             'detection_multiclass_scores': [],
                             'raw_detection_scores': [], 'num_detections': 0}

        for i in np.arange(0, detections['num_detections']):
            if detections['detection_scores'][i] > 0.40:
                filtered_detections['detection_anchor_indices'].append(detections['detection_anchor_indices'][i])
                filtered_detections['detection_scores'].append(detections['detection_scores'][i])
                filtered_detections['detection_boxes'].append(detections['detection_boxes'][i].tolist())
                filtered_detections['detection_classes'].append(detections['detection_classes'][i])
                filtered_detections['raw_detection_boxes'].append(detections['raw_detection_boxes'][i].tolist())
                filtered_detections['detection_multiclass_scores'].append(detections['detection_multiclass_scores'][i].tolist())
                filtered_detections['raw_detection_scores'].append(detections['raw_detection_scores'][i].tolist())
                filtered_detections['num_detections'] = filtered_detections['num_detections'] + 1

                result.append({"class": CLASSES[detections['detection_classes'][i]-1],
                               "confidence": detections['detection_scores'][i]*100,
                               "coordinates": detections['detection_boxes'][i]})
        final_result.append(result)

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            np.array(filtered_detections['detection_boxes']),
            filtered_detections['detection_classes'],
            filtered_detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=.40,
            agnostic_mode=False)

    print(final_result)

    return final_result, image_np_with_detections

print("[INFO] Beggining...")
while True:
    # Initialize the list of frames that have been processed
    frames = []
    cams = [webcam1, webcam2]
    rotations = [cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_90_CLOCKWISE]
    
    # Loop over the frames and their respective motion detectors
    for index in [0,1]:
        rval, frame = cams[index].read()

        frames.append(cv2.rotate(frame,rotations[index]))

    res, frame = detect_objects([frames[0],frames[1]], net)
                
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Cam", frame)
    key = cv2.waitKey(1) & 0xFF

    # If the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# Do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
