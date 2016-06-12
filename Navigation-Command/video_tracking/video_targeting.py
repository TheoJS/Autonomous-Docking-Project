# import the necessary packages
from collections import deque
import numpy as np
import imutils
import cv2
import math
 
# initialise camera link
camera_port = 0
camera = cv2.VideoCapture(camera_port)

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (26, 44, 47)
greenUpper = (72, 255, 255)
purpleLower = (129, 44, 77)
purpleUpper = (164, 255, 255)
tail_len=5
pts = deque(maxlen=tail_len)
 
# keep looping
while True:

  # capture frame
  (grabbed, frame)=camera.read()
  # resize the frame, and convert it to the HSV
  # color space
  frame = imutils.resize(frame, width=300)
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
  # construct a mask for the color "green", then perform
  # a series of dilations and erosions to remove any small
  # blobs left in the mask
  mask_purp = cv2.inRange(hsv, purpleLower, purpleUpper)
  mask_purp = cv2.erode(mask_purp, None, iterations=2)
  mask_purp = cv2.dilate(mask_purp, None, iterations=2)
  
  mask_gree = cv2.inRange(hsv, greenLower, greenUpper)
  mask_gree = cv2.erode(mask_gree, None, iterations=2)
  mask_gree = cv2.dilate(mask_gree, None, iterations=2)

  # find contours in the mask and initialize the current
  # (x, y) center of the ball
  cnts_purp = cv2.findContours(mask_purp.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)[-2]
  center = None
 
  # only proceed if at least one contour was found
  if len(cnts_purp) > 0:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    c1 = max(cnts_purp, key=cv2.contourArea)
    ((x1, y1), radius1) = cv2.minEnclosingCircle(c1)
    M1 = cv2.moments(c1)
    center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))
 
    # only proceed if the radius meets a minimum size
    if radius1 > 20:
      cnts_gree = cv2.findContours(mask_gree.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
      if len(cnts_gree) > 0:
        for c2 in cnts_gree:
          ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
          M2 = cv2.moments(c2)
          center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))
          if math.sqrt((center1[0]-center2[0])**2 + (center1[1]-center2[1])**2) < radius1:
            center = center2
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x2), int(y2)), int(radius2), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            print "target obtained"
  
  # update the points queue
  pts.appendleft(center)

  # loop over the set of tracked points
  for i in xrange(1, len(pts)):
    # if either of the tracked points are None, ignore
    # them
    if pts[i - 1] is None or pts[i] is None:
      continue
 
    # otherwise, compute the thickness of the line and
    # draw the connecting lines
    thickness = int(np.sqrt(tail_len / float(i + 1)) * 2.5)
    cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
  
  # show the frame to our screen
  cv2.imshow("Frame", frame)
  # cv2.imshow("Mask", mask_purp)
  # cv2.imshow("Mask", mask_gree)
  key = cv2.waitKey(1) & 0xFF
 
  # if the 'q' key is pressed, stop the loop
  if key == ord("q"):
    break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
