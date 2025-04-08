import cv2
import numpy as np
print(cv2.__version__)

# Load and display an image
img = cv2.imread('Sample.jpg', -1)
if img is not None:
    cv2.imshow('Sample Image -1', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not read the image.")

img1 = cv2.imread('Sample.jpg', 0)
if img1 is not None:
    cv2.imshow('Sample Image 0', img1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not read the image.")


img2 = cv2.imread('Sample.jpg', 1)
if img2 is not None:
    cv2.imshow('Sample Image -1', img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not read the image.")



image_Data = [    
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]],
    [[0, 0, 0], [255, 255, 255]]
    ]

made_img = np.array(image_Data,  dtype=np.uint8)


cv2.imshow('made image', made_img)
cv2.waitKey(0)
cv2.destroyAllWindows()