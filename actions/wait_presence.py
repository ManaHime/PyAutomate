import cv2
from ..capture.screenshot import screenshot
from ..vision.template import get_img_center_coords, _debug_print
from .. import is_visual_initialized
from ..core.browser import get_driver, get_selector_type, wait_for_element

def wait_presence(target, selector_type=None, driver=None, timeout=None, screen_img=None):
    if selector_type is not None or driver is not None:
        if selector_type is None:
            return False
        if driver is None:
            driver = get_driver()
        wait_for_element(driver, "present", selector_type, target)
        return True
    if isinstance(target, str) and (target.startswith('img/') or target.startswith('/img/')):
        if not is_visual_initialized():
            print("Visual processing not initialized. Call initialize_visual() first.")
            return False
            
        img_path = target.lstrip('/')
        _debug_print(f"Looking for image {img_path}")
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print("Failed to load image")
            return False
        bgr   = img[...,:3]
        alpha = img[..., 3]
        _, mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
        
        if screen_img is None:
            screen_img, _ = screenshot()
        coords = get_img_center_coords(bgr, mask, screen_img, 0, 0, timeout)
        if coords:
            return True
        return False