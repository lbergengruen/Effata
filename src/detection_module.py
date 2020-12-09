# import the necessary packages
from __future__ import print_function
import datetime
import time
import cv2
import math
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings

#CONSTANTES
MAX_DISTANCE_CM = 800 #5 metros
MAX_ANGLE_LENSE_X = 160 #En grados
MAX_ANGLE_LENSE_Y = 120 #En grados
camera_offset_cm = 10
offset_adjust = 4300
W = 320
H = 240

CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person", "Sculpture", "Street light", "Table", "Traffic light", "Traffic sign", "Tree"]

PATH_TO_LABELS = "./models/ssd_trained/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "./models/ssd_trained/saved_model"

net = tf.saved_model.load(PATH_TO_SAVED_MODEL)

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

def detect_objects(images, net):
    w = images[0].shape[1]
    h = images[0].shape[0]
    final_result = []

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

        filtered_detections = {'detection_anchor_indices': [], 'detection_scores': [], 'detection_boxes': [],
                               'detection_classes': [], 'raw_detection_boxes': [], 'detection_multiclass_scores': [],
                               'raw_detection_scores': [], 'num_detections': 0}
        for i in np.arange(0, len(detections['detection_scores'])):
            if detections['detection_scores'][i] > 0.40:
                filtered_detections['detection_anchor_indices'].append(detections['detection_anchor_indices'][i])
                filtered_detections['detection_scores'].append(detections['detection_scores'][i])
                filtered_detections['detection_boxes'].append(detections['detection_boxes'][i])
                filtered_detections['detection_classes'].append(detections['detection_classes'][i])
                filtered_detections['raw_detection_boxes'].append(detections['raw_detection_boxes'][i])
                filtered_detections['detection_multiclass_scores'].append(detections['detection_multiclass_scores'][i])
                filtered_detections['raw_detection_scores'].append(detections['raw_detection_scores'][i])
                filtered_detections['num_detections'] = filtered_detections['num_detections'] + 1

                result.append({"class": CLASSES[detections['detection_classes'][i]],
                               "confidence": detections['detection_scores'][i] * 100,
                               "coordinates": detections['detection_boxes'][i]})
        final_result.append(result)

    image_np_with_detections = image_np.copy()

    for detection in filtered_detections:
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detection['detection_boxes'],
            detection['detection_classes'],
            detection['detection_scores'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=.40,
            agnostic_mode=False)

    # plt.figure(figsize=(12, 8))
    # plt.imshow(image_np_with_detections)
    # plt.show()
    # print(final_result)

    return final_result, image_np_with_detections

def stereo_match(left_boxes, right_boxes):
    coords = []

    for box1 in left_boxes:
        for box2 in right_boxes:
            if box1['class']==box2['class']:
                #print(box1['class'])
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
    angle_x = math.asin(((center[0]-im_center[0])/im_center[0])*math.sin(MAX_ANGLE_LENSE_X))
    angle_y = math.asin(((center[1]-im_center[1])/im_center[1])*math.sin(MAX_ANGLE_LENSE_Y))
    return [angle_x, angle_y]

def to_cartesian_coords(angle_x,angle_y, distance):
    distance_x = round((distance*(math.cos(angle_y))*(math.sin(angle_x)))/100, 3)
    distance_y = round((distance*(math.cos(angle_y))*(math.cos(angle_x)))/100, 3)
    distance_z = round((distance*(math.sin(angle_y)))/100, 3)
    return [distance_x, distance_y, distance_z]
