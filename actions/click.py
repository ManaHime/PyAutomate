from ..vision.template import get_img_center_coords, get_text_center_coords
from ..core.mouse import mouse, hover
from pynput.mouse import Button
import time

def click(target, x_offset=0, y_offset=0, timeout=None):
    if hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.left); time.sleep(0.1)
            mouse.release(Button.left)
            return True
        except Exception as e:
            print(f"Click error: {e}")
    return False

def dbclick(target, x_offset=0, y_offset=0, timeout=None):
    if hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            time.sleep(0.1)
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            return True
        except Exception as e:
            print(f"Double-click error: {e}")
    return False

def rightclick(target, x_offset=0, y_offset=0, timeout=None):
    if hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.right); time.sleep(0.1)
            mouse.release(Button.right)
            return True
        except Exception as e:
            print(f"Right-click error: {e}")
    return False