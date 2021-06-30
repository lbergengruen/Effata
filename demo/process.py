# Import modules
from utils import to_polar_coords, to_cartesian_coords, get_intersection_area, reduce_sources

# import the necessary packages
import cv2
import time
import os
import math
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import json

# CONSTANTS
total_time = 300
W = 320  # Width of the images taken by the camera
H = 240  # Height of the images taken by the camera
MIN_CONFIDENCE = 0.40
MAX_DISTANCE_CM = 500  # Value expressed in centimeters
camera_offset_cm = 10  # Value expressed in centimeters
offset_adjust = 300  # Constant Value that depends on the cameras used and lets us calculate distance
CLASSES = ["Barrel", "Bicycle", "Bus", "Car", "Chair", "Dog", "Fire hydrant", "Horse", "Palm tree", "Person",
           "Street light", "Table", "Traffic light", "Traffic sign", "Tree", "Pozo", "Baliza", "Cono"]

PATH_TO_LABELS = "../src/models/ssd_trained_model/label_map.pbtxt"
PATH_TO_SAVED_MODEL = "../src/models/ssd_trained_model/saved_model"

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


def detect_objects_tf(images, net):
    final_result = []
    list_detections = []
    images_np_with_detections = []

    for image in images:
        result = []
        image_np = np.array(image).astype(np.uint8)
        images_np_with_detections.append(image_np.copy())

        # TF MODEL
        input_tensor = tf.convert_to_tensor(image_np)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = net(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections

        # Detection_classes should be ints.
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
                               "confidence": detections['detection_scores'][i],
                               "coordinates": detections['detection_boxes'][i].tolist()})
        list_detections.append(filtered_detections)
        final_result.append(result)

    for idx in [0, 1]:
        for source in final_result[idx]:
            viz_utils.visualize_boxes_and_labels_on_image_array(
                images_np_with_detections[idx],
                np.array([source['coordinates']]),
                np.array([CLASSES.index(source['class']) + 1]),
                np.array([source['confidence']]),
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=20,
                min_score_thresh=MIN_CONFIDENCE,
                agnostic_mode=False)

    sources = stereo_match(final_result[0], final_result[1])
    final_image_np = image_np.copy()

    for source in sources:
        viz_utils.visualize_boxes_and_labels_on_image_array(
            final_image_np,
            np.array([source['box']]),
            np.array([CLASSES.index(source['class']) + 1]),
            np.array([source['confidence']]),
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=MIN_CONFIDENCE,
            agnostic_mode=False)
        print(f'Distance {source["class"]}: {source["distance"]}')

    return sources, images_np_with_detections, final_image_np


def stereo_match(left_boxes, right_boxes):
    sources = []

    for box1 in left_boxes:
        candidates = []
        distances = []

        for idx, box2 in enumerate(right_boxes):

            if box1['class'] == box2['class']:
                c1 = [(box1['coordinates'][0] + box1['coordinates'][2]) * H / 2,
                      (box1['coordinates'][1] + box1['coordinates'][3]) * W / 2]

                c2 = [(box2['coordinates'][0] + box2['coordinates'][2]) * H / 2,
                      (box2['coordinates'][1] + box2['coordinates'][3]) * W / 2]

                sqr_diff = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

                x = (c1[0] + c2[0]) / 2
                y = (c1[1] + c2[1]) / 2

                distance = camera_offset_cm / sqr_diff * offset_adjust

                if distance <= MAX_DISTANCE_CM:
                    candidates.append(idx)
                    distances.append(distance)

        if len(distances) > 0:
            np_distances = np.array(distances)
            index = np.argmin(np_distances)
            best_box2 = right_boxes.pop(candidates[index])
            best_distance = distances[index]

            c1 = [(box1['coordinates'][0] + box1['coordinates'][2]) * H / 2,
                  (box1['coordinates'][1] + box1['coordinates'][3]) * W / 2]

            c2 = [(best_box2['coordinates'][0] + best_box2['coordinates'][2]) * H / 2,
                  (best_box2['coordinates'][1] + best_box2['coordinates'][3]) * W / 2]

            sqr_diff = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)

            y = (c1[0] + c2[0]) / 2
            x = (c1[1] + c2[1]) / 2

            center = [x, y]
            angles = to_polar_coords(center)
            cartesian_coords = to_cartesian_coords(angles[0], angles[1], best_distance)

            source = {"class": box1['class'],
                      "confidence": max(box1['confidence'], best_box2['confidence']),
                      "box": best_box2['coordinates'],
                      "distance": best_distance,
                      "cartesian_coords": cartesian_coords}

            sources.append(source)

    return sources


if __name__ == "__main__":
    version = 4

    print("[INFO] Starting Job")

    images_list = os.listdir(f"./raw/v{version}/right/")
    if '.DS_Store' in images_list:
        images_list.remove('.DS_Store')
    images_list.sort()

    print("[INFO] Loading Model")
    net = tf.saved_model.load(PATH_TO_SAVED_MODEL)

    for image_file in images_list:
        print(image_file)
        left_im = cv2.imread(f"./raw/v{version}/left/{image_file}")
        right_im = cv2.imread(f"./raw/v{version}/right/{image_file}")

        id = (image_file.split('_')[1]).split(".")[0]

        sources, images, final_image = detect_objects_tf([left_im, right_im], net)
        print(sources)
        cv2.imwrite(f"./processed/v{version}/left/imagen_{id}.png", images[0])
        cv2.imwrite(f"./processed/v{version}/right/imagen_{id}.png", images[1])

        cv2.imwrite(f"./final/v{version}/imagen_{id}.png", final_image)
        if f"text_{id}.txt" in os.listdir(f"./final/v{version}/"):
            os.remove(f"./final/v{version}/text_{id}.txt")
        f = open(f"./final/v{version}/text_{id}.txt", "a")
        f.write(str(sources))
        f.close()

    print("[INFO] Job Finished")
