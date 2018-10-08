import numpy as np
import cv2


class DuplicateHandler:
    entries = []

    def __init__(self, thresh):
        self.threshold = thresh

    def check(self, img, add=True):
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        for i in self.entries:
            if self.calcDiff(i, img) < self.threshold:
                return False

        if add:
            self.entries.append(img)

        return True

    def calcDiff(self, img1, img2):
        # bring the two images to the same size
        if img1.shape[0] > img2.shape[0] or img1.shape[1] > img2.shape[1]:
            img1 = img1[0: img2.shape[0], 0: img2.shape[1]]
        elif img2.shape[0] > img1.shape[0] or img2.shape[1] > img1.shape[1]:
            img2 = img2[0: img1.shape[0], 0: img1.shape[1]]

        diff = cv2.absdiff(img1, img2)
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        diff = diff.astype(np.uint8)
        # alternatively: (np.sum(diff) / (diff.size * 255)) * 100
        percent = (np.count_nonzero(diff) / diff.size) * 100

        return percent