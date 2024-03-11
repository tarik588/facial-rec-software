import cv2
import numpy as np

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Create background subtractor object
fgbg = cv2.createBackgroundSubtractorMOG2()

# Initialize variables
gesture_start = False
gesture_frames = 0

while True:
    ret, frame = cap.read()
    fgmask = fgbg.apply(frame)
    thresh = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY)[1]
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if w > 100 and h > 100:
            if not gesture_start:
                gesture_start = True
                gesture_frames = 0
            else:
                gesture_frames += 1
            
            # If a certain number of frames have passed, recognize as a wave gesture
            if gesture_frames > 30:
                print("Wave gesture detected!")

                
    # Display output
    cv2.imshow('Frame', frame)
    
