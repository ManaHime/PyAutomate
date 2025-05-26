import mss
import numpy as np
import cv2

last_screenshot_region = None

def screenshot(x1=None, y1=None, x2=None, y2=None):
    with mss.mss() as sct:
        if None not in (x1,y1,x2,y2):
            region = {"left":x1,"top":y1,"width":x2-x1,"height":y2-y1}
        else:
            mon = sct.monitors[1]
            region = {"left":mon['left'],"top":mon['top'],
                      "width":mon['width'],"height":mon['height']}
        img = np.array(sct.grab(region))
        if img.shape[2]==4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img, region