import time
import numpy as np
import cv2
import imutils
import eventhook
import filevideostream


class ChangeDetection:
    # minimum contour area (1000)
    minArea = 1000
    # maximum frames before firstFrame reset (3)
    maxIdle = 3
    # frame step size
    stepSize = 20
    # amount of percent between each progress event
    progressInterval = 1
    # event that fires when motion is confirmed
    onTrigger = eventhook.EventHook()
    # event that gives feedback of how far the detection is
    onProgress = eventhook.EventHook()

    def __init__(self, stepSize, progressInterval, showDebug=False):
        self.stepSize = stepSize
        self.progressInterval = progressInterval
        self.showDebug = showDebug

    def start(self, source):
        firstFrame = None
        prevFrame = None
        # amount of contours
        contAmount = 0

        # amount of idle frames that were the same
        # used to determine if that frame should become the new firstFrame
        idleCount = 0

        # current pos in vid
        currentPosition = 0
        lastProgress = 0

        startTime = time.time()

        print('change detection initiated')

        self.videoStream = filevideostream.FileVideoStream(
            source, skipSize=self.stepSize)

        totalFrames = self.videoStream.totalFrames

        self.videoStream.start()

        # sleep to allow the thread to start
        time.sleep(1)

        while self.videoStream.more():
            frame = self.videoStream.read()
            if frame is None:
                break

            original = frame.copy()

            # convert grabbed frame to gray and blur
            gray = self.transform(frame)

            if firstFrame is None:
                firstFrame = np.zeros(gray.shape, np.uint8)
            if prevFrame is None:
                prevFrame = np.zeros(gray.shape, np.uint8)

            frameDelta = cv2.absdiff(firstFrame, gray)
            thresh = self.calcThresh(frameDelta)
            cnts = self.detectContours(thresh)

            # we have motion, possible new firstFrame?
            if len(cnts) > 0:
                prevDelta = cv2.absdiff(prevFrame, gray)
                prevThresh = self.calcThresh(prevDelta)
                # we have no changes from the previous frame
                if cv2.countNonZero(prevThresh) == 0:
                    idleCount += 1
                else:
                    idleCount = 0

            # we have now seen the same image for too long, reset firstImage
            if idleCount > self.maxIdle:
                firstFrame = prevFrame
                self.onTrigger.fire(original)
                idleCount = 0

            prevFrame = gray
            progress = (currentPosition / totalFrames) * 100

            if progress - lastProgress >= self.progressInterval:
                lastProgress = progress
                self.onProgress.fire(progress)

            currentPosition = self.videoStream.currentPosition

            if self.showDebug:
                # loop over the contours
                for c in cnts:
                    # compute the bounding box for the contour, draw it on the frame
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 255, 0), 2)

                cv2.putText(frame, "contours: " + str(contAmount),
                            (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "idle: " + str(idleCount), (140, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, "frame: " + str(currentPosition), (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                cv2.imshow("Frame", frame)
                cv2.imshow("Delta", frameDelta)
                cv2.imshow("Threshold", thresh)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        self.videoStream.stop()
        cv2.destroyAllWindows()

    def transform(self, img):
        img = imutils.resize(img, width=500)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (21, 21), 0)
        return img

    def calcThresh(self, frame):
        thresh = cv2.threshold(frame, 25, 255, cv2.THRESH_BINARY)[1]
        return cv2.dilate(thresh, None, iterations=2)

    def detectContours(self, thresh):
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        validCnts = []

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.minArea:
                continue

            validCnts.append(c)

        return validCnts
