from pynput.keyboard import Controller, Key, KeyCode
from selenium.webdriver.common.keys import Keys
from ..core.browser import get_driver, get_selector_type, wait_for_element
import time
keyboard = Controller()

def confirm_input(driver=None, selector=None, selector_type=None, timeout=10):
    if selector is not None:
        selector_type = get_selector_type(selector_type)
        if driver is None:
            driver = get_driver()
        if driver is None:
            raise ValueError("Driver is not initialized")
        element = wait_for_element(driver, "interactable", selector_type, selector, timeout)
        if element:
            element.send_keys(Keys.ENTER)
            return True
        else:
            print(f"No input element found for: {selector}")
            return False

def type(text: str, driver=None, selector=None, selector_type=None, timeout=10):
        if selector is not None:
            selector_type = get_selector_type(selector_type)
            if driver is None:
                driver = get_driver()
            if driver is None:
                raise ValueError("Driver is not initialized")
            element = wait_for_element(driver, "interactable", selector_type, selector, timeout)
            if element:
                try:
                    element.click()
                    time.sleep(0.1)
                    element.clear()
                    time.sleep(0.1)
                    element.send_keys(text)
                    time.sleep(0.1) 
                    return True
                except Exception as e:
                    print(f"Error while sending input: {e}")
                    return False
            else:
                print(f"No input element found for: {selector}")
                return False    
        else:
            try:
                keyboard.type(text)
                return True
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
        
        if "timeout" in error_msg.lower():
            print(f"⏰ Timeout while typing '{text}' into: {selector}")
        elif "no such element" in error_msg.lower():
            print(f"🔍 Element not found for typing '{text}': {selector}")
        elif "stale element" in error_msg.lower():
            print(f"🔄 Stale element reference while typing '{text}': {selector}")
        elif "invalid selector" in error_msg.lower():
            print(f"❌ Invalid selector for typing '{text}': {selector}")
        else:
            print(f"❌ Error typing '{text}' into {selector}: {error_type}: {error_msg}")
        
        return False

def clear(driver=None, selector=None, selector_type=None, timeout=10):
    if selector is not None:
        selector_type = get_selector_type(selector_type)
        if driver is None:
            driver = get_driver()
        if driver is None:
            raise ValueError("Driver is not initialized")
        element = wait_for_element(driver, "interactable", selector_type, selector, timeout)
        if element:
            try:
                element.click()
                time.sleep(0.1)

                # First attempt: normal clear()
                element.clear()
                time.sleep(0.1)

                # Fallback: CTRL+A then BACKSPACE
                element.send_keys(Keys.CONTROL, 'a')
                time.sleep(0.05)
                element.send_keys(Keys.BACKSPACE)

                return True
            except Exception as e:
                print(f"Error while clearing input: {e}")
                return False
        else:
            print(f"No input element found to clear for: {selector}")
            return False
    else:
        print(f"No selector provided for clear operation")
        return False

def is_modifier(k):
    return k.lower() in ['ctrl', 'alt', 'shift', 'cmd', 'win']

def get_key(k):
    k = k.lower()
    # Map win to cmd_l (left Windows key)
    if k == 'win':
        return Key.cmd_l
    try:
        return getattr(Key, k)
    except AttributeError:
        return k

def key(input_str: str, driver=None, selector=None, selector_type=None, timeout=10):
    if selector is not None:
        selector_type = get_selector_type(selector_type)
        if driver is None:
            driver = get_driver()
        if driver is None:
            raise ValueError("Driver is not initialized")
        element = wait_for_element(driver, "interactable", selector_type, selector, timeout)
        if element:
            element.send_keys(input_str)
            return True
        else:
            print(f"No element found to send key for: {selector}")
            return False
    elif input_str.startswith("[") and input_str.endswith("]"):
        keys = input_str[1:-1].split("][")
        modifiers, action_keys = [], []
        for k in keys:
            (modifiers if is_modifier(k) else action_keys).append(k)
        for mod in modifiers:
            keyboard.press(get_key(mod))
        for act in action_keys:
            k = get_key(act)
            keyboard.press(k); keyboard.release(k)
        for mod in reversed(modifiers):
            keyboard.release(get_key(mod))
    else:
        k = get_key(input_str)
        keyboard.press(k); keyboard.release(k)

def ime_on():
    keyboard.press(KeyCode.from_vk(243))
    keyboard.release(KeyCode.from_vk(244))

def ime_off():
    keyboard.press(KeyCode.from_vk(244))
    keyboard.release(KeyCode.from_vk(243))
