# Import the necessary packages
import math
import json

# CONSTANTS
W = 320
H = 240
MAX_ANGLE_LENSE_X = 160  # Value expressed in degrees
MAX_ANGLE_LENSE_Y = 120  # Value expressed in degrees
e = 30  # All objects inside of a circle of radios 45 degrees will be considered as one.


def to_polar_coords(center):
    # Translate image coordinates into polar coordinates inside of the image.
    im_center = [W / 2, H / 2]
    angle_x = math.asin(((center[0] - im_center[0]) / im_center[0]) * math.sin(MAX_ANGLE_LENSE_X))
    angle_y = math.asin(((center[1] - im_center[1]) / im_center[1]) * math.sin(MAX_ANGLE_LENSE_Y))
    return [angle_x, angle_y]


def to_cartesian_coords(angle_x, angle_y, distance):
    # Translate the vision angles into global cartesian coordinates.
    distance_x = round((distance * (math.cos(angle_y)) * (math.sin(angle_x))) / 100, 3)
    distance_y = round((distance * (math.cos(angle_y)) * (math.cos(angle_x))) / 100, 3)
    distance_z = round((distance * (math.sin(angle_y))) / 100, 3)
    return [distance_x, distance_y, distance_z]


def reduce_sources(sources):
    # If two objects are very close to each other, a single sound may be enough to alert the user, so the objects are
    # merged as one. We will only accept a maximum of 3 objects per time.

    for i in range(2):
        for o1 in sources:
            for o2 in sources:
                if o1 != o2:
                    result = check_and_merge_objects(o1, o2)
                    if len(result) == 1:
                        sources.remove(o1)
                        sources.remove(o2)
                        sources.append(result[0])
                        break

    if len(sources) > 3:
        sources = keep_significant_sources(sources)
    return sources


def check_and_merge_objects(o1, o2):
    # Check if these two objects are so close to each other that can be notified as a single obstacle.
    o1 = json.loads(o1)
    o2 = json.loads(o2)

    c1 = [(o1['box'][1] + o1['box'][3]) * W / 2, (o1['box'][0] + o1['box'][2]) * H / 2]
    c2 = [(o2['box'][1] + o2['box'][3]) * W / 2, (o2['box'][0] + o2['box'][2]) * H / 2]

    if abs(c1[0] - c2[0]) < e and abs(c1[1] - c2[1]) < e:
        cart_coords = [(o1["cartesian_coords"][0]+o2["cartesian_coords"][0])/2,
                                     (o1["cartesian_coords"][1]+o2["cartesian_coords"][1])/2,
                                     (o1["cartesian_coords"][2]+o2["cartesian_coords"][2])/2]

        o3 = {"class": o1['class'],
                 "confidence": max(o1['confidence'], o2['confidence']),
                 "box": [min(o1['box'][0], o2['box'][0]), min(o1['box'][1], o2['box'][1]),
                                 max(o1['box'][2], o2['box'][2]), max(o1['box'][3], o2['box'][3])],
                "distance": math.sqrt(cart_coords[0]**2 + cart_coords[1]**2 + cart_coords[2]**2),
                "cartesian_coords": cart_coords, "merged": True
              }
        result = [json.dumps(o3)]
    else:
        result = [json.dumps(o1), json.dumps(o2)]
    return result


def keep_significant_sources(sources):
    # In case of having to reduce the number of sources to a minimum we keep the 3 closest objects in sight
    sources = sorted(sources, key=lambda k: json.loads(k)['distance'])
    return sources[:3]


def get_intersection_area(box_a, box_b):
    # Get intersection box
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    return [x_a, y_a, x_b, y_b]


def get_union_area(box_a, box_b):
    # Get intersection box
    x_a = min(box_a[0], box_b[0])
    y_a = min(box_a[1], box_b[1])
    x_b = max(box_a[2], box_b[2])
    y_b = max(box_a[3], box_b[3])

    return [x_a, y_a, x_b, y_b]
