# import the necessary packages
import cv2
import time
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure, draw, pause
import os
from PIL import Image

if __name__ == "__main__":
    print("[INFO] Starting Job")

    version = 3

    images_list = os.listdir(f"./raw/v{version}/right/")
    if '.DS_Store' in images_list:
        images_list.remove('.DS_Store')
    images_list.sort()

    # number_images = int((images_list[-1].split('_')[1]).split(".")[0])

    # f, axarr = plt.subplots(1, 2, figsize=(15, 8))
    # axarr[0].set_title("Left Camera")
    # axarr[0].axis('off')
    # axarr[1].set_title("Right Camera")
    # axarr[1].axis('off')
    #
    # left_im = cv2.imread(f"./raw/v{version}/left/{images_list[0]}")[:, :, ::-1]
    # right_im = cv2.imread(f"./raw/v{version}/right/{images_list[0]}")[:, :, ::-1]
    # a = axarr[0].imshow(left_im)
    # b = axarr[1].imshow(right_im)

    # for image_file in images_list:
    #     print(image_file)
    #     left_im = cv2.imread(f"./raw/v{version}/left/{image_file}")[:, :, ::-1]
    #     right_im = cv2.imread(f"./raw/v{version}/right/{image_file}")[:, :, ::-1]
    #     a.set_data(left_im)
    #     b.set_data(right_im)
    #     draw()
    #     pause(1e-5)
    #
    #     key = cv2.waitKey(1) & 0xFF
    #     # If the `q` key was pressed, break from the loop
    #     if key == ord("q"):
    #         break

    # for image_file in images_list:
    #     print(image_file)
    #     left_im = cv2.imread(f"./processed/v{version}/left/{image_file}")[:, :, ::-1]
    #     right_im = cv2.imread(f"./processed/v{version}/right/{image_file}")[:, :, ::-1]
    #     a.set_data(left_im)
    #     b.set_data(right_im)
    #     draw()
    #     pause(1e-5)
    #
    #     key = cv2.waitKey(1) & 0xFF
    #     # If the `q` key was pressed, break from the loop
    #     if key == ord("q"):
    #         break

    f, axarr = plt.subplots(1, 1, figsize=(15, 8))
    axarr.set_title("Result Camera")
    axarr.axis('off')

    im = cv2.imread(f"./final/v{version}/{images_list[0]}")[:, :, ::-1]
    a = axarr.imshow(im)

    # for image_file in images_list:
    #     print(image_file)
    #     im = cv2.imread(f"./final/v{version}/{image_file}")[:, :, ::-1]
    #     a.set_data(im)
    #     draw()
    #     pause(1e-5)
    #
    #     key = cv2.waitKey(1) & 0xFF
    #     # If the `q` key was pressed, break from the loop
    #     if key == ord("q"):
    #         break

    for image_file in images_list:
        print(image_file)
        im = cv2.imread(f"./feedback/v{version}/{image_file}")[:, :, ::-1]
        a.set_data(im)
        draw()
        pause(1e-5)

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break