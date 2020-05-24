import time
import cv2
camera = cv2.VideoCapture(0)

time.sleep(0.1)  # If you don't wait, the image will be dark
return_value1, image1 = camera1.read()
cv2.imwrite("one.png", image1)
del(camera1)  # so that others can use the camera as soon as possible
camera2 = cv2.VideoCapture(2)
time.sleep(0.1)  # If you don't wait, the image will be dark
return_value2, image2 = camera2.read()
cv2.imwrite("two.png", image2)
del(camera2)  # so that others can use the camera as soon as possible
