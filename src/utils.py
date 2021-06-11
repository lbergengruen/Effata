# Import the necessary modules
from main import W, H, MAX_ANGLE_LENSE_X, MAX_ANGLE_LENSE_Y

# Import the necessary packages
import math

# CONSTANTS
e = 0.25  # All objects inside of a circle of radios 45 degrees will be considered as one.


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
    r1 = math.sqrt(o1[0] ** 2 + o1[1] ** 2 + o1[2] ** 2)
    t1 = math.atan2(o1[1], o1[0])
    f1 = math.acos(o1[2] / r1)

    r2 = math.sqrt(o2[0] ** 2 + o2[1] ** 2 + o2[2] ** 2)
    t2 = math.atan2(o2[1], o2[0])
    f2 = math.acos(o2[2] / r2)

    if abs(t2 - t1) < e and abs(f2 - f1) < e:
        r3 = min(r1, r2)
        t3 = (t1 + t2) / 2
        f3 = (f1 + f2) / 2
        o3 = [(r3 * math.sin(f3) * math.cos(t3)), (r3 * math.sin(f3) * math.sin(t3)), (r3 * math.cos(f3))]
        result = [o3]
    else:
        result = [o1, o2]
    return result


def keep_significant_sources(sources):
    # In case of having to reduce the number of sources to a minimum we keep the 3 closest objects in sight
    sources = sorted(sources, key=lambda k: (math.sqrt(k[0] ** 2 + k[1] ** 2 + k[2] ** 2)))
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
