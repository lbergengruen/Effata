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

    notification_cooldown = 10
    notification_duration = 20

    files_list = os.listdir(f"./final/v{version}/")
    if '.DS_Store' in files_list:
        files_list.remove('.DS_Store')
    files_list.sort()

    images_list = [i for i in files_list if 'imagen' in i]
    text_list = [i for i in files_list if 'text' in i]

    cooldown_countdown = 0
    duration_countdown = 0

    for id in range(len(images_list)):
        print(id)
        im = (cv2.imread(f"./raw/v{version}/right/{images_list[id]}")) // 6
        txt = open(f"./final/v{version}/{text_list[id]}", "r").read()
        txt_array = txt.replace('[{', '{').replace("'", "\"").replace('}]', '}').replace('}, {', '}/{').split('/')

        if txt_array[0] != "[]":

            txt_array = reduce_sources(txt_array)

            if duration_countdown > 0:
                for obj in temp_obj:
                    obj = json.loads(obj)
                    radius = int(7 * 500 / obj['distance'])

                    if radius > 30:
                        radius = 30

                    if "merged" in obj and obj["merged"]:
                        color = (0, 255 * (0.8 * duration_countdown/notification_duration + 0.2), 0)
                    else:
                        color = (0, 0, 255 * (0.8 * duration_countdown/notification_duration + 0.2))

                    cv2.circle(im, (
                        int((obj['box'][1] + obj['box'][3]) * W / 2), int((obj['box'][0] + obj['box'][2]) * H / 2)),
                                   radius, color, 4)
                duration_countdown = duration_countdown - 1

                if text_list[id] in os.listdir(f"./feedback/v{version}/"):
                    os.remove(f"./feedback/v{version}/{text_list[id]}")
                f = open(f"./feedback/v{version}/{text_list[id]}", "a")
                f.write(str(temp_obj))
                f.close()
            elif cooldown_countdown == 0:
                for obj in txt_array:
                    obj = json.loads(obj)
                    radius = int(7 * 500/obj['distance'])

                    if radius > 30:
                        radius = 30

                    if "merged" in obj and obj["merged"]:
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    cv2.circle(im, (int((obj['box'][1]+obj['box'][3])*W/2), int((obj['box'][0]+obj['box'][2])*H/2)), radius, color, 4)
                cooldown_countdown = notification_cooldown
                duration_countdown = notification_duration
                temp_obj = txt_array

                if text_list[id] in os.listdir(f"./feedback/v{version}/"):
                    os.remove(f"./feedback/v{version}/{text_list[id]}")
                f = open(f"./feedback/v{version}/{text_list[id]}", "a")
                f.write(str(temp_obj))
                f.close()
            else:
                cooldown_countdown = cooldown_countdown - 1
                if text_list[id] in os.listdir(f"./feedback/v{version}/"):
                    os.remove(f"./feedback/v{version}/{text_list[id]}")
                f = open(f"./feedback/v{version}/{text_list[id]}", "a")
                f.write("[]")
                f.close()

        cv2.imwrite(f"./feedback/v{version}/{images_list[id]}", im)


    print("[INFO] Job Finished")
