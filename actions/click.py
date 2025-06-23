from ..vision.template import get_img_center_coords, get_text_center_coords
from ..core.mouse import mouse, hover
from selenium.webdriver.common.action_chains import ActionChains
from pynput.mouse import Button
import time
from ..core.browser import get_driver, wait_for_element

def click(target, x_offset=0, y_offset=0, timeout=10, driver=None, selector_type=None ):
    if target is not None:
        if selector_type is not None:
            if driver is None:
                driver = get_driver()
            if driver is None:
                raise ValueError("Driver is not initialized")
            element = wait_for_element(driver, "interactable", selector_type, target, timeout)
            if element:
                element.click()
                return True
            else:
                print(f"No clickable element found for: {target}")
                return False
        else:
            print(f"Clicking image/text target: {target}")
            if hover(target, x_offset, y_offset, timeout):
                try:
                    mouse.press(Button.left); time.sleep(0.1)
                    mouse.release(Button.left)
                    print(f"✅ Successfully clicked image/text target")
                    return True
                except Exception as e:
                    print(f"❌ Click error on image/text target: {type(e).__name__}: {str(e)}")
            return False
        
    if hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.left); time.sleep(0.1)
            mouse.release(Button.left)
            print(f"✅ Successfully clicked target")
            return True
        except Exception as e:
            print(f"❌ Click error: {type(e).__name__}: {str(e)}")
    return False

def dbclick(target, x_offset=0, y_offset=0, timeout=10, driver=None, selector_type=None ):
    if selector_type is not None:
        if driver is None:
            driver = get_driver()
        if driver is None:
            raise ValueError("Driver is not initialized")
        element = wait_for_element(driver, "interactable", selector_type, target, timeout)
        if element:
            ActionChains(driver).double_click(element).perform()
            return True
        else:
            print(f"No double-clickable element found for: {target}")
            return False
        
    elif hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            time.sleep(0.1)
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            return True
        except Exception as e:
            print(f"Double-click error: {e}")
    return False

def rightclick(target, x_offset=0, y_offset=0, timeout=10):
    if hover(target, x_offset, y_offset, timeout):
        try:
            mouse.press(Button.right); time.sleep(0.1)
            mouse.release(Button.right)
            return True
        except Exception as e:
            print(f"Right-click error: {e}")
    return False