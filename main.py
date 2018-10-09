import time
import datetime
import os
import argparse
import cv2
import imutils
import img2pdf
import changedetection
import duplicatehandler


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--video", dest="video", required=True,
                    help="the path to your video file to be analyzed")
parser.add_argument("-o", "--output", dest="output", default="slides.pdf",
                    help="the output pdf file where the extracted slides will be saved")
parser.add_argument("-s", "--step-size", dest="step-size", default=20,
                    help="the amount of frames skipped in every iteration")
parser.add_argument("-p", "--progress-interval", dest="progress-interval", default=1,
                    help="how many percent should be skipped between each progress output")
parser.add_argument("-d", "--debug", dest="debug", default=False, action="store_true",
                    help="the path to your video file to be analyzed")

args = vars(parser.parse_args())


class Main:
    slideCounter = 0

    def __init__(self, debug, vidpath, output, stepSize, progressInterval):
        self.vidpath = vidpath
        self.output = output
        self.detection = changedetection.ChangeDetection(
            stepSize, progressInterval, debug)
        self.dupeHandler = duplicatehandler.DuplicateHandler(1)

    def strfdelta(self, tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    # crop image to slide size
    def cropImage(self, frame):
        min_area = (frame.shape[0] * frame.shape[1]) * (2 / 3)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if imutils.is_cv2() else contours[1]

        for cnt in contours:
            if cv2.contourArea(cnt) > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                crop = frame[y:y+h, x:x+w]
                return crop

    def checkRatio(self, frame, min, max):
        ratio = frame.shape[1] / frame.shape[0]
        return ratio >= min and ratio <= max

    def onTrigger(self, frame):
        frame = self.cropImage(frame)
        if frame is not None and self.checkRatio(frame, 1.2, 1.5):
            if self.dupeHandler.check(frame):
                print("Found a new slide!")
            # self.saveSlide(frame)

    def saveSlide(self, slide):
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        print("Saving slide " + str(self.slideCounter) + "...")
        cv2.imwrite(os.path.join(
            self.output, str(self.slideCounter) + ".jpg"), slide)
        self.slideCounter += 1

    def onProgress(self, percent):
        elapsed = time.time() - self.startTime
        eta = (elapsed / percent) * (100 - percent)
        etaString = self.strfdelta(datetime.timedelta(seconds=eta),
                                   "{hours}h {minutes}min {seconds}s")
        print("progress: ~%d%% | about %s left" % (percent, etaString))

    def convertToPDF(self):
        imgs = []
        for i in self.dupeHandler.entries:
            imgs.append(cv2.imencode('.jpg', i)[1].tostring())

        with open(self.output, "wb") as f:
            f.write(img2pdf.convert(imgs))

    def start(self):
        self.detection.onTrigger += self.onTrigger
        self.detection.onProgress += self.onProgress

        self.startTime = time.time()

        self.detection.start(self.vidpath.strip())

        print("Saving PDF...")
        self.convertToPDF()

        print("All done!")


main = Main(args['debug'], args['video'], args['output'],
            args['step-size'], args['progress-interval'])
main.start()
