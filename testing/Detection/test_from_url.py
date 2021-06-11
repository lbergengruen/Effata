# import the necessary packages
from __future__ import print_function
import datetime
import time
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import warnings
from PIL import Image
import requests
from io import BytesIO

warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

MIN_CONFIDENCE = 0.40
CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person", "Sculpture", "Street light", "Table", "Traffic light", "Traffic sign", "Tree", "Pozo", "Baliza", "Cono"]

PATH_TO_LABELS = "../models/final_model/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "../models/final_model/saved_model"

net = tf.saved_model.load(PATH_TO_SAVED_MODEL)

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

def detect_objects(images, net):
    final_result = []
    list_detections = []

    for image in images:
        result = []
        image_np = np.array(image)
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = net(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # detection_classes should be ints.
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        filtered_detections = {'detection_anchor_indices': [], 'detection_scores': [],
                               'detection_boxes': [],
                               'detection_classes': [], 'raw_detection_boxes': [],
                               'detection_multiclass_scores': [],
                               'raw_detection_scores': [], 'num_detections': 0}

        for i in np.arange(0, detections['num_detections']):
            if detections['detection_scores'][i] > MIN_CONFIDENCE:
                filtered_detections['detection_anchor_indices'].append(detections['detection_anchor_indices'][i])
                filtered_detections['detection_scores'].append(detections['detection_scores'][i])
                filtered_detections['detection_boxes'].append(detections['detection_boxes'][i].tolist())
                filtered_detections['detection_classes'].append(detections['detection_classes'][i])
                filtered_detections['raw_detection_boxes'].append(detections['raw_detection_boxes'][i].tolist())
                filtered_detections['detection_multiclass_scores'].append(
                    detections['detection_multiclass_scores'][i].tolist())
                filtered_detections['raw_detection_scores'].append(detections['raw_detection_scores'][i].tolist())
                filtered_detections['num_detections'] = filtered_detections['num_detections'] + 1

                result.append({"class": CLASSES[detections['detection_classes'][i] - 1],
                               "confidence": detections['detection_scores'][i] * 100,
                               "coordinates": detections['detection_boxes'][i].tolist()})
        list_detections.append(filtered_detections)
        final_result.append(result)

    image_np_with_detections = image_np.copy()

    for filtered_detections in list_detections:
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            np.array(filtered_detections['detection_boxes']),
            filtered_detections['detection_classes'],
            filtered_detections['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=MIN_CONFIDENCE,
            agnostic_mode=False)

    return final_result, image_np_with_detections




while True:
    url = input("Insert URL:")
    response = requests.get(url)
    frame = np.array((Image.open(BytesIO(response.content))))

    file = open("sample_image.jpg", "wb")
    file.write(frame)
    file.close()

    res, frame = detect_objects([frame], net)
                
    timestamp = datetime.datetime.now()
    ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

    cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("Cam", frame)
    cv2.waitKey()

