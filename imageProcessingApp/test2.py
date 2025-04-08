import cv2
import numpy as np

# 0 is usually the built-in webcam
cap = cv2.VideoCapture(0)


# Check if camera opened successfully
if not cap.isOpened():
    print("Error opening camera")
    exit()


# we do this in a while so that we can continuously display images from our webcam
while True:
    # Capture frame-by-frame
    # read() returns 2 values: ret -> tells us if the capture is working (if the webcam is not used by smth else)
    #                        frame -> one actual frame (image as numpy array type) from our webcam
    ret, frame = cap.read()
    
    if not ret:
        print("Error capturing frame")
        break
    
    # we get the width and height of the camera feed by selecting properties of the cap object (3 is width,  4 is height)
    width = int(cap.get(3))
    height = int(cap.get(4))


    image = np.zeros(frame.shape, np.uint8)
    smaller_frame = cv2.resize(frame, (0, 0), fx= 0.5, fy= 0.5)

    image[:height//2, :width//2] = cv2.rotate(smaller_frame, cv2.ROTATE_180)
    image[height//2:, width//2:] = cv2.rotate(smaller_frame, cv2.ROTATE_180)
    image[:height//2, width//2:] = smaller_frame
    image[height//2:, :width//2] = smaller_frame

    # Display the frame
    cv2.imshow('Camera Feed', image)
    
    # Press 'q' to exit
    # for each frame wait 1ms for a key press and move on to the next frame if 'q' key is not pressed
    if cv2.waitKey(1) == ord('q'):
        break

# Release webcam resources and close webcam feed window
cap.release()
cv2.destroyAllWindows()