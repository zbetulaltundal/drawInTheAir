import cv2 as cv
import numpy as np
import os
import sys

#this line provides the camera to close after code is terminated

os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = "0"

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open webcam")
    sys.exit()

cap.set(cv.CAP_PROP_FRAME_WIDTH, 480)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
kernel = np.ones((5, 5), np.uint8)
x, y = 0, 0
canvas = None
drawings = None

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        
        frame = cv.flip(frame, 1)
        
        l_h, l_s, l_v = 42, 59, 60
        u_h, u_s, u_v = 80, 177, 255
        lower_green = np.array([l_h, l_s, l_v], np.uint8)
        upper_green = np.array([u_h, u_s, u_v], np.uint8)
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        hsv_blur = cv.GaussianBlur(hsv, (5, 5), 0)
        mask = cv.inRange(hsv_blur, lower_green, upper_green)
        mask = cv.erode(mask, kernel, iterations=1)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        mask = cv.dilate(mask, kernel, iterations=1)
        result = cv.bitwise_and(frame, frame, mask=mask)

        contours, hieararchy = cv.findContours(
                mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if canvas is None:
            canvas = np.zeros(frame.shape,dtype=np.uint8)
            canvas.fill(255)
            cv.putText(canvas, "PRESS C TO CLEAR ALL", (15, 33), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv.LINE_AA)
            cv.putText(canvas, "PRESS Q TO EXIT", (15, 66), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv.LINE_AA)
            cv.putText(canvas, "HOLD S TO STOP DRAWING", (15, 99), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv.LINE_AA)

        if len(contours) > 0:
            if drawings is None:
                drawings = np.zeros_like(frame)
            
            if x == 0 and y == 0:
                c = max(contours, key=cv.contourArea)
                ((x, y), radius) = cv.minEnclosingCircle(c)
            else:
                c = max(contours, key=cv.contourArea)
                ((newX, newY), radius) = cv.minEnclosingCircle(c)
                cv.line(drawings, (int(x), int(y)), (int(newX), int(newY)), (0, 255, 0), 3)
                cv.line(canvas, (int(x), int(y)), (int(newX), int(newY)), (0, 255, 0), 3)
                x, y = newX, newY

        else:
            x, y = 0, 0
        
        if not drawings is None:
            frame = cv.add(frame, drawings)
        
        cv.imshow("Canvas", canvas)
        cv.imshow("Frame", frame)
        #If user press q for 10 ms close the vid
        k = cv.waitKey(10) & 0xff
        if k == ord("q"):
            break
        if k == ord('c') and not drawings is None:
            drawings = None
            canvas = None
        if k == ord('s'):
            x, y = 0, 0
            while cv.waitKey(10) & 0xff == ord('s'):
                x, y = 0, 0

    else:
        break

cap.release()
cv.destroyAllWindows()

