# import the necessary packages
import cv2
from matplotlib import pyplot as plt
from matplotlib.pyplot import draw, pause
import os
import numpy as np
import json
import time

# from openal import WaveFile, Buffer, Source
#
# # CONSTANTS
# WAVE_FILE = WaveFile("./openal/agudo5s.wav")
#
#
# def play_sound(x, y, z):
#     buffer = Buffer(WAVE_FILE)
#     source = Source(buffer)
#
#     source.set_source_relative(True)
#     v1 = (x, y, z)
#     source.set_position(v1)
#     pitch = 0.12
#     source.set_pitch(pitch)
#     gradual_beep_long(source)
#
#
# def gradual_beep_long(source):
#     source.play()
#     time.sleep(0.4)
#     source.stop()


if __name__ == "__main__":
    print("[INFO] Starting Job")

    version = 4

    images_list = os.listdir(f"./raw/v{version}/right/")
    if '.DS_Store' in images_list:
        images_list.remove('.DS_Store')
    images_list.sort()

    images_list = images_list[200:600]

    f, axarr = plt.subplots(1, 2, figsize=(15, 8))
    axarr[0].set_title("Left Camera")
    axarr[0].axis('off')
    axarr[1].set_title("Right Camera")
    axarr[1].axis('off')

    left_im = cv2.imread(f"./raw/v{version}/left/{images_list[0]}")[:, :, ::-1]
    right_im = cv2.imread(f"./raw/v{version}/right/{images_list[0]}")[:, :, ::-1]
    a = axarr[0].imshow(left_im)
    b = axarr[1].imshow(right_im)

    for image_file in images_list:
        print(image_file)
        left_im = cv2.imread(f"./processed/v{version}/left/{image_file}")[:, :, ::-1]
        right_im = cv2.imread(f"./processed/v{version}/right/{image_file}")[:, :, ::-1]
        a.set_data(left_im)
        b.set_data(right_im)
        draw()
        pause(1e-5)

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    f2, axarr2 = plt.subplots(1, 1, figsize=(15, 8))
    axarr2.set_title("Result Camera")
    axarr2.axis('off')

    im = cv2.imread(f"./final/v{version}/{images_list[0]}")[:, :, ::-1]
    a2 = axarr2.imshow(im)

    for image_file in images_list:
        print(image_file)
        im = cv2.imread(f"./final/v{version}/{image_file}")[:, :, ::-1]
        a2.set_data(im)
        draw()
        pause(1e-5)

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    f3, axarr3 = plt.subplots(1, 2, figsize=(15, 8))
    axarr3[0].set_title("Feedback")
    axarr3[0].axis('off')
    axarr3[1].set_title("Coordinates")
    axarr3[1].axis('off')

    left_im = cv2.imread(f"./feedback/v{version}/{images_list[0]}")[:, :, ::-1]
    right_im = cv2.imread(f"./feedback/coordinates_image.png")[:, :, ::-1]
    a3 = axarr3[0].imshow(left_im)
    b3 = axarr3[1].imshow(right_im)

    for image_file in images_list:
        print(image_file)
        im = cv2.imread(f"./feedback/v{version}/{image_file}")[:, :, ::-1]
        im2 = cv2.imread(f"./feedback/coordinates_image.png")[:, :, ::-1]

        im2 = cv2.line(np.float32(im2), (int(im2.shape[0]/2), int(im2.shape[1]*11/12)), (0,100), (0,0,0), 5)
        im2 = cv2.line(im2, (int(im2.shape[0]/2), int(im2.shape[1]*11/12)), (int(im2.shape[0]),100), (0,0,0), 5)
        im2 = cv2.circle(im2, (int(im2.shape[0]/2), int(im2.shape[1]*11/12)), 40, (255/255, 179/255, 186/255), -1)

        center = [int(im2.shape[0]/2), int(im2.shape[1]*5/6)]

        text_file = image_file.replace('imagen', 'text').replace('png', 'txt')
        if text_file in os.listdir(f"./feedback/v{version}/"):
            txt = open(f"./feedback/v{version}/{text_file}", "r").read()
            txt_array = txt.replace('[\'{', '{').replace('}\']', '}').replace('}\', \'{', '}/{').replace("'", "\"").split('/')
        else:
            txt_array = ["[]"]

        if txt_array[0] != "[]":
            for obj in txt_array:
                obj = json.loads(obj)
                x = obj['cartesian_coords'][0]
                y = obj['cartesian_coords'][1]

                if "merged" in obj and obj["merged"]:
                    color = (0, 255, 0)
                else:
                    color = (255, 0, 0)

                im2 = cv2.circle(im2, (np.float32(im2.shape[0]/2+600*x), np.float32(im2.shape[1]*5/6-125*y)), 20, color, -1)

        a3.set_data(im)
        b3.set_data(im2)
        draw()


        pause(1e-6)

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
