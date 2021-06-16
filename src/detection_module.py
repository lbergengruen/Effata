# import the necessary modules
from utils import to_polar_coords, to_cartesian_coords, get_intersection_area, reduce_sources
from main import MIN_CONFIDENCE, CLASSES, camera_offset_cm, offset_adjust, MAX_DISTANCE_CM, H, W, category_index

# import the necessary packages
import math
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import visualization_utils as viz_utils
import warnings

warnings.filterwarnings('ignore')  # Suppress Matplotlib warnings


def detect_objects_tf(images, net, display):
    final_result = []
    list_detections = []

    for image in images:
        result = []
        image_np = np.array(image).astype(np.uint8)

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

    image_np_with_detections = image_np.copy()

    sources = stereo_match(final_result[0], final_result[1])
    # sources = reduce_sources(sources)  # Not being used at the moment

    if display:
        for source in sources:
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                np.array([source['box']]),
                np.array([CLASSES.index(source['class']) + 1]),
                np.array([source['confidence']]),
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=20,
                min_score_thresh=MIN_CONFIDENCE,
                agnostic_mode=False)
            print(f'Distance {source["class"]}: {source["distance"]}')

    return sources, image_np_with_detections


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

# TFLITE DETECTION MODULE
# def detect_objects_tflite(images, net, display):
#     final_result = []
#     list_detections = []
#
#     for image in images:
#         result = []
#
#         image_np = np.array(image)
#         input_tensor = tf.convert_to_tensor(image_np, dtype=tf.float32)
#
#         # TFLITE MODEL
#         input_details = net.get_input_details()
#         output_details = net.get_output_details()
#         net.set_tensor(input_details[0]['index'], [input_tensor])
#         net.invoke()
#         boxes = net.get_tensor(output_details[0]['index'])
#         classes = net.get_tensor(output_details[1]['index'])
#         scores = net.get_tensor(output_details[2]['index'])
#
#         # Detection_classes should be ints.
#         classes[0] = classes[0].astype(np.int64)
#         num_detections = len(classes[0])
#
#         for i in np.arange(0, num_detections):
#             if scores[0][i] > MIN_CONFIDENCE:
#                 result.append({"class": CLASSES[int(classes[0][i]) - 1],
#                                "confidence": scores[0][i],
#                                "coordinates": boxes[0][i].tolist()})
#         final_result.append(result)
#
#     image_np_with_detections = image_np.copy()
#
#     sources = stereo_match(final_result[0], final_result[1])
#     # sources = reduce_sources(sources)
#
#     if display:
#         for source in sources:
#             viz_utils.visualize_boxes_and_labels_on_image_array(
#                 image_np_with_detections,
#                 np.array([source['box']]),
#                 np.array([CLASSES.index(source['class']) + 1]),
#                 np.array([source['confidence']]),
#                 category_index,
#                 use_normalized_coordinates=True,
#                 max_boxes_to_draw=20,
#                 min_score_thresh=MIN_CONFIDENCE,
#                 agnostic_mode=False)
#
#     return sources, image_np_with_detections
