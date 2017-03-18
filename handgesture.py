# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import sys
from datetime import datetime

from datetime import datetime

PY3 = sys.version_info[0] == 3
if PY3:
    xrange = range

drawing = False
points = []
flag = 0


def rest():
    global points
    points = []


def draw(img):
    global points
    for p in points:
        cv2.circle(img, (p[0], p[1]), 8, (255, 255, 255), -1)
		# cv2.circle(img,(p[0]+10,p[1]+30),8,(0,255,255),-1)

    return img


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (20, 100, 100)
greenUpper = (30, 255, 255)

#greenLower = (67, 68, 38)
#greenUpper = (100, 255, 255)
pts = deque(maxlen=64)

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(0)

# keep looping
count = 0
while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=5)
    mask = cv2.dilate(mask, None, iterations=13)
    cv2.imshow("b&w", mask)
    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    # print len(cnts)
    # only proceed if at least one contour was found
    if len(cnts) == 3:
        global points
        points = []
        global flag
        flag = 0
    elif len(cnts) == 2 and flag == 0:
        global count, flag
        frame_blk = np.zeros(frame.shape)
        frame_blk = draw(frame_blk)
        time_now = str(datetime.now().time())

        cv2.imwrite(".\scr_shot\screen_shot" + str(time_now[0:2]) + "_" + str(time_now[3:5]) + "_" + str(
            time_now[6:8]) + ".jpg", frame_blk)
        print("here ")
        count = count + 1
        flag = 1

    if len(cnts) == 1:
        global flag
        flag = 0

        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(c) >= 950:
            print(cv2.contourArea(c), "cnt area")
            # print c , type(c)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
            points.append(center)
        # update the points queue
        # pts.appendleft(center)
    frame = draw(frame)
    # loop over the set of tracked points
    # for i in xrange(1, len(pts)):
    # 	# if either of the tracked points are None, ignore
    # 	# them
    # 	#if pts[i - 1] is None or pts[i] is None:
    # 	#	continue
    #
    # 	# otherwise, compute the thickness of the line and
    # 	# draw the connecting lines
    # 	thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
    # 	cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
    elif key == ord("r"):
        global points
        points = []

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
