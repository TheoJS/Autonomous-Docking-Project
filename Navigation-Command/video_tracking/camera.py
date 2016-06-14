# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import imutils
import cv2
import math
import time


class Camera():

    def __init__(self):
      # initialise camera link
      print "Initializing camera..."
      self.pi_camera = PiCamera()
      self.resolution = (320, 240)
      self.framerate = 20
      self.rawCapture = PiRGBArray(self.pi_camera, self.resolution)
      # define the lower and upper boundaries of the "green"
      # ball in the HSV color space, then initialize the
      # list of tracked points
      self.greenLower = (26, 20, 20) #(26, 44, 47)
      self.greenUpper = (72, 255, 255)
      self.purpleLower = (129, 20, 20) #(129, 44, 77)
      self.purpleUpper = (164, 255, 255)
      print "Initialisation OK"
      

    def seek_target(self)

      # grab frame
      frame = self.pi_camera.capture(self.rawCapture, format='bgr'):

      # grab array
      frame = frame.array

      # resize image
      # frame = imutils.resize(frame, width=300)

      # color space
      hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

      # construct a mask for the colors "green" and "purpl", then perform
      # a series of dilations and erosions to remove any small
      # blobs left in the mask
      mask_purp = cv2.inRange(hsv, self.purpleLower, self.purpleUpper)
      mask_purp = cv2.erode(mask_purp, None, iterations=2)
      mask_purp = cv2.dilate(mask_purp, None, iterations=2)

      mask_gree = cv2.inRange(hsv, self.greenLower, self.greenUpper)
      mask_gree = cv2.erode(mask_gree, None, iterations=2)
      mask_gree = cv2.dilate(mask_gree, None, iterations=2)

      # find contours in the mask and initialize the current
      # (x, y) center of the ball
      cnts_purp = cv2.findContours(mask_purp.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
      center = None
      X = None
      Y = None

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
        if radius1 > 10:
          cnts_gree = cv2.findContours(mask_gree.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
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

                # get center coordinates
                (X, Y) = center;
                print "X = %d  ;  Y = %d" % (X, Y)


      # clear stream for next frame
      self.rawCapture.truncate(0)

      # return coordinates of the center, width and height
      return (X, Y, self.resolution[0], self.resolution[1])
