# import the necessary packages
import cv2
import time
import imutils

# CONSTANTS
total_time = 300
W = 320  # Width of the images taken by the camera
H = 240  # Height of the images taken by the camera

if __name__ == "__main__":
    # Cameras Initialization
    cameras = []
    print("[INFO] Opening Cameras...")
    for port in [0, 2]:
        webcam = cv2.VideoCapture(port)
        webcam.set(3, 120)
        webcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cameras.append(webcam)

    rotations = [cv2.ROTATE_180, cv2.ROTATE_180]    # Cameras are positioned up-side-down

    print("[INFO] Starting Job")

    i = 0
    start_time = time.time()
    while (time.time() - start_time) < total_time or total_time == -1:

        images = []

        for idx in [0, 1]:
            stream = cameras[idx]
            ret, frame = stream.read()
            frame = cv2.rotate(imutils.resize(frame, height=240, width=320), rotations[idx])
            images.append(frame)

            cv2.imshow(f"Camera {idx}", frame)

        i = i + 1
        if i < 10:
            s = f"000{i}"
        elif i < 100:
            s = f"00{i}"
        elif i < 1000:
            s = f"0{i}"
        else:
            s = f"{i}"
        print(f"Saving Raw Images #{s}")
        cv2.imwrite(f"./raw/right/imagen_{s}.png", images[0])
        cv2.imwrite(f"./raw/left/imagen_{s}.png", images[1])

        # time.sleep(0.2)

        key = cv2.waitKey(1) & 0xFF
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            for cap in cameras:
                cap.release()
            break

    print("[INFO] Job Finished")
