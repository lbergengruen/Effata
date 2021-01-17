# import the necessary packages
from utils import to_polar_coords, to_cartesian_coords, get_intersection_area
from main import MIN_CONFIDENCE, CLASSES, camera_offset_cm, offset_adjust, MAX_DISTANCE_CM, H, W, category_index

import math
import numpy as np
import tensorflow as tf
from object_detection.utils import visualization_utils as viz_utils
import warnings

warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings


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
                               "confidence": detections['detection_scores'][i] * 100,
                               "coordinates": detections['detection_boxes'][i].tolist()})
        list_detections.append(filtered_detections)
        final_result.append(result)

    image_np_with_detections = image_np.copy()

    sources = stereo_match(final_result[0], final_result[1])

    for source in sources:
        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            np.array([source['box']]),
            f"{source['class']}_{source['distance']}_cm",
            source['confidence'],
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=20,
            min_score_thresh=MIN_CONFIDENCE,
            agnostic_mode=False)

    # for filtered_detections in list_detections:
    #     viz_utils.visualize_boxes_and_labels_on_image_array(
    #         image_np_with_detections,
    #         np.array(filtered_detections['detection_boxes']),
    #         filtered_detections['detection_classes'],
    #         filtered_detections['detection_scores'],
    #         category_index,
    #         use_normalized_coordinates=True,
    #         max_boxes_to_draw=20,
    #         min_score_thresh=MIN_CONFIDENCE,
    #         agnostic_mode=False)

    return sources["cartesian_coords"], image_np_with_detections


def stereo_match(left_boxes, right_boxes):
    sources = []

    for box1 in left_boxes:
        for box2 in right_boxes:

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
                    center = [x, y]
                    angles = to_polar_coords(center)
                    cartesian_coords = to_cartesian_coords(angles[0], angles[1], distance)

                    source = {"class": box1['class'],
                              "confidence": max(box1['confidence'], box2['confidence']),
                              "box": get_intersection_area(box1['coordinates'], box2['coordinates']),
                              "distance": distance,
                              "cartesian_coords": cartesian_coords}

                    sources.append(source)

    return sources
