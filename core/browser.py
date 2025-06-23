import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)


_all_drivers = []
_default_driver = None  # Initialize the default driver variable

def init_driver(browser_name="chrome", headless=False, window_size=(1920,1080)):
    global _default_driver
    if browser_name.lower() == "chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        # Suppress Chrome DevTools logging
        # chrome_options.add_argument("--log-level=3")
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if headless:
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    _all_drivers.append(driver)
    if _default_driver is None:
        _default_driver = driver
    return driver

def get_driver():
    return _default_driver

def close_driver(driver):
    try:
        driver.quit()
        _all_drivers.remove(driver)
        if driver == _default_driver:
            _default_driver = None
    except:
        return False
    return True

def close_all_drivers():
    for d in _all_drivers:
        try:
            d.quit()
        except:
            return False
    return True

def get_selector_type(selector_type):
    if selector_type == "xpath":
        return By.XPATH
    elif selector_type == "css":
        return By.CSS_SELECTOR
    elif selector_type == "id":
        return By.ID
    elif selector_type == "class":
        return By.CLASS_NAME
    else:
        raise ValueError(f"Invalid selector type: {selector_type}")

# def wait_for_element(driver, wait_type, selector_type, selector, timeout=20):
#     wait = WebDriverWait(driver, timeout)
#     try:
#         if wait_type == "present":
#             print(f"Waiting for element to be present: {selector} with selector_type: {selector_type}")
#             try:
#                 element = wait.until(EC.presence_of_element_located((selector_type, selector)))
#                 print(f"✅ Element found: {selector}")
#                 return element
#             except Exception as e:
#                 print(f"❌ Element not found after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "all_present":
#             print("waiting all present")
#             try:
#                 # Try the wait condition with better error handling
#                 elements = wait.until(EC.presence_of_all_elements_located((selector_type, selector)))
#                 for el in elements:
#                     print("is visible: ", el.is_displayed())
#                     print("is enabled: ", el.is_enabled())
#                     print("is selected: ", el.is_selected())
#                     print("text: ", el.text)
#                     print("tag_name: ", el.tag_name)
#                     print("class: ", el.get_attribute("class"))
#                     print("id: ", el.get_attribute("id"))
#                     print("name: ", el.get_attribute("name"))
#                     print("placeholder: ", el.get_attribute("placeholder"))
#                 # Check if we got a boolean instead of elements (the bug)
                    
#                 print(f"✅ Elements found: {selector}")
#                 return elements
#             except Exception as e:
#                 print(f"❌ No elements found after timeout: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
                
#                 # Try direct find as fallback
#                 try:
#                     print(f"   Trying direct find_elements as fallback...")
#                     direct_elements = driver.find_elements(selector_type, selector)
#                     print(f"   Direct find returned: {len(direct_elements)} elements")
#                     return direct_elements
#                 except Exception as fallback_e:
#                     print(f"   Fallback also failed: {type(fallback_e).__name__}: {str(fallback_e)}")
#                     return []
#         elif wait_type == "clickable":
#             print(f"Waiting for element to be clickable: {selector}")
#             try:
#                 element = wait.until(EC.element_to_be_clickable((selector_type, selector)))
#                 print(f"✅ Element is clickable: {selector}")
#                 return element
#             except Exception as e:
#                 print(f"❌ Element not clickable after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "interactable":
#             print(f"Waiting for element to be interactable: {selector}")
#             try:
#                 # First wait for presence (loaded in DOM)
#                 test_val = wait.until(
#                     EC.presence_of_all_elements_located((selector_type, selector))
#                 )
#                 for el in test_val:
#                     print("is visible: ", el.is_displayed())
#                     print("is enabled: ", el.is_enabled())
#                     print("is selected: ", el.is_selected())
#                 # Then filter visible + enabled elements
#                 elements = driver.find_elements(selector_type, selector)
#                 for el in elements:
#                     if el.is_displayed() and el.is_enabled():
#                         print(f"✅ Interactable element found: {selector}")
#                         return el  # return first usable element

#                 print(f"❌ No interactable elements found: {selector}")
#                 return None  # if nothing usable
#             except Exception as e:
#                 print(f"❌ Error waiting for interactable element: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
                
#                 # Try direct find as fallback
#                 try:
#                     print(f"   Trying direct find_elements as fallback...")
#                     direct_elements = driver.find_elements(selector_type, selector)
#                     for el in direct_elements:
#                         if el.is_displayed() and el.is_enabled():
#                             print(f"   Found interactable element via fallback: {selector}")
#                             return el
#                     print(f"   No interactable elements found via fallback: {selector}")
#                     return None
#                 except Exception as fallback_e:
#                     print(f"   Fallback also failed: {type(fallback_e).__name__}: {str(fallback_e)}")
#                     return None
#         elif wait_type == "selected":
#             try:
#                 element = wait.until(EC.element_to_be_selected((selector_type, selector)))
#                 return element
#             except Exception as e:
#                 print(f"❌ Element not selected after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "invisible":
#             try:
#                 # This returns boolean, but we need to return the element that became invisible
#                 # So we'll find the element first, then wait for it to be invisible
#                 element = driver.find_element(selector_type, selector)
#                 wait.until(EC.invisibility_of_element_located((selector_type, selector)))
#                 return element  # Return the element that became invisible
#             except Exception as e:
#                 print(f"❌ Element not invisible after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "visible":
#             print(f"Waiting for element to be visible: {selector}")
#             try:
#                 element = wait.until(EC.visibility_of_element_located((selector_type, selector)))
#                 print(f"✅ Element is visible: {selector}")
#                 return element
#             except Exception as e:
#                 print(f"❌ Element not visible after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "has_text":
#             try:
#                 # This returns boolean, but we need to return the element that has the text
#                 element = driver.find_element(selector_type, selector)
#                 wait.until(EC.text_to_be_present_in_element((selector_type, selector)))
#                 return element  # Return the element that has the text
#             except Exception as e:
#                 print(f"❌ Element doesn't have expected text after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "title_has":
#             try:
#                 # This returns boolean, but we need to return the page title
#                 wait.until(EC.title_contains(selector))
#                 return driver.title  # Return the page title
#             except Exception as e:
#                 print(f"❌ Title doesn't contain '{selector}' after {timeout}s")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "title_is":
#             try:
#                 # This returns boolean, but we need to return the page title
#                 wait.until(EC.title_is(selector))
#                 return driver.title  # Return the page title
#             except Exception as e:
#                 print(f"❌ Title is not '{selector}' after {timeout}s")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "url_has": 
#             try:
#                 # This returns boolean, but we need to return the current URL
#                 wait.until(EC.url_contains(selector))
#                 return driver.current_url  # Return the current URL
#             except Exception as e:
#                 print(f"❌ URL doesn't contain '{selector}' after {timeout}s")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "url_matches":
#             try:
#                 # This returns boolean, but we need to return the current URL
#                 wait.until(EC.url_matches(selector))
#                 return driver.current_url  # Return the current URL
#             except Exception as e:
#                 print(f"❌ URL doesn't match '{selector}' after {timeout}s")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         elif wait_type == "inputable":
#             print(f"Waiting for element to be inputable: {selector}")
#             try:
#                 element = wait.until(EC.element_to_be_clickable((selector_type, selector)))
#                 print(f"✅ Element is inputable: {selector}")
#                 return element
#             except Exception as e:
#                 print(f"❌ Element not inputable after {timeout}s: {selector}")
#                 print(f"   Error details: {type(e).__name__}: {str(e)}")
#                 return None
#         else:
#             raise ValueError(f"Invalid wait type: {wait_type}")
#     except Exception as e:
#         # Provide more detailed error information
#         error_type = type(e).__name__
#         error_msg = str(e)
        
#         if "timeout" in error_msg.lower():
#             print(f"⏰ Timeout after {timeout}s waiting for {wait_type}: {selector}")
#             print(f"   This usually means the element doesn't exist or hasn't loaded yet")
#         elif "no such element" in error_msg.lower():
#             print(f"🔍 Element not found: {selector}")
#             print(f"   The element may not exist in the current page")
#         elif "stale element" in error_msg.lower():
#             print(f"🔄 Stale element reference: {selector}")
#             print(f"   The element was found but is no longer attached to the DOM")
#         elif "invalid selector" in error_msg.lower():
#             print(f"❌ Invalid selector: {selector}")
#             print(f"   Check the XPath/CSS syntax")
#         else:
#             print(f"❌ Wait error for {wait_type}: {selector}")
#             print(f"   Error type: {error_type}")
#             print(f"   Error message: {error_msg}")
        
#         # Always return None or empty list, never boolean
#         return None


def read(driver, selector_type, selector, content_type="text", timeout=20, stable_time=1.0):
    """
    Read content from elements matching the selector, with special stable-list waiting
    for table rows when you ask for table_data, table_rows or table_dict.
    """
    # 1) Convert the selector_type string to Selenium By enum
    by = get_selector_type(selector_type)

    # 2) Handle table-based types up front with a stable-list wait on rows
    if content_type in ("table_rows", "table_data", "table_dict"):
        # wait for <tr> under your selector to stabilize
        rows = wait_for_element(
            driver,
            "stable_list",
            by,
            f"{selector}//tr",
            timeout=timeout,
            # our stable-list helper uses this extra param:
            # so we overload expected_count to pass stable_time
            expected_count=stable_time
        )
        if not rows:
            print(f"No rows found under {selector}")
            return []

        # table_rows: just return the WebElement rows
        if content_type == "table_rows":
            return rows

        # build a list-of-lists for table_data
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
            texts = [c.text.strip() for c in cells]
            if texts:
                data.append(texts)
        if content_type == "table_data":
            return data

        # table_dict: first row = headers (if th), else auto Column_1…
        headers = []
        header_cells = rows[0].find_elements(By.TAG_NAME, "th")
        if header_cells:
            headers = [c.text.strip() for c in header_cells]
            data_rows = rows[1:]
        else:
            # auto-generate header names
            sample_cells = rows[0].find_elements(By.TAG_NAME, "td")
            headers = [f"Column_{i+1}" for i in range(len(sample_cells))]
            data_rows = rows

        dict_list = []
        for row in data_rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            texts = [c.text.strip() for c in cells]
            if len(texts) == len(headers):
                dict_list.append(dict(zip(headers, texts)))
            else:
                # fallback: Column_1, Column_2…
                dict_list.append({f"Column_{i+1}": t for i, t in enumerate(texts)})
        return dict_list

    # 3) For everything else, fall back to a simple all-present wait
    elements = wait_for_element(driver, "all_present", by, selector, timeout=timeout)
    if not elements:
        elements = driver.find_elements(by, selector)
    if not elements:
        print(f"No elements found for selector: {selector}")
        return []

    # 4) Non-table content types
    if content_type == "elements":
        return elements
    if content_type == "text":
        return elements[0].text if len(elements) == 1 else [el.text for el in elements]
    if content_type in ("html", "inner_html"):
        return (elements[0].get_attribute("innerHTML")
                if len(elements) == 1
                else [el.get_attribute("innerHTML") for el in elements])
    if content_type == "outer_html":
        return (elements[0].get_attribute("outerHTML")
                if len(elements) == 1
                else [el.get_attribute("outerHTML") for el in elements])
    if content_type == "attribute":
        def attrs(el):
            return {
                "text": el.text,
                "innerHTML": el.get_attribute("innerHTML"),
                "outerHTML": el.get_attribute("outerHTML"),
                "tag_name": el.tag_name,
                "class": el.get_attribute("class"),
                "id": el.get_attribute("id")
            }
        return attrs(elements[0]) if len(elements) == 1 else [attrs(el) for el in elements]

    raise ValueError(
        f"Invalid content_type: {content_type!r}. "
        "Use 'text', 'html', 'inner_html', 'outer_html', 'attribute', "
        "'table_rows', 'table_data', 'table_dict' or 'elements'."
    )


def select_by_value(driver, selector_type, selector, value, timeout=10):
    element = wait_for_element(driver, "clickable", selector_type, selector, timeout)
    if element:
        select = Select(element)
        select.select_by_value(value)
        return True
    else:
        print(f"No visible select element found for: {selector}")
        return False








def wait_for_stable_elements(driver, by, locator, stable_time=2.0, timeout=30):
    """
    Poll `find_elements` until the number of matching elements
    stays constant for `stable_time` seconds (or timeout).
    """
    end_time     = time.time() + timeout
    last_count   = -1
    stable_start = time.time()

    while time.time() < end_time:
        elements     = driver.find_elements(by, locator)
        current_count = len(elements)

        if current_count != last_count:
            last_count   = current_count
            stable_start = time.time()
        elif time.time() - stable_start >= stable_time:
            return elements

        time.sleep(0.2)

    raise TimeoutException(f"Elements for {locator!r} never stabilized in {timeout}s")

def wait_for_element(
    driver,
    wait_type,     # e.g. "visible", "interactable", "stable_list", etc.
    by,            # e.g. By.XPATH, By.CSS_SELECTOR
    locator,       # the selector string
    timeout=20,
    expected_count=None,  # only used for "all_exact"
    stable_time=2.0       # only used for "stable_list"
):
    wait = WebDriverWait(driver, timeout)

    def _first_interactable(d):
        for el in d.find_elements(by, locator):
            if el.is_displayed() and el.is_enabled():
                return el
        return False

    # dispatch table
    wait_map = {
        "present":     lambda: wait.until(EC.presence_of_element_located((by, locator))),
        "all_present": lambda: wait.until(EC.presence_of_all_elements_located((by, locator))),
        "visible":     lambda: wait.until(EC.visibility_of_element_located((by, locator))),
        "clickable":   lambda: wait.until(EC.element_to_be_clickable((by, locator))),
        "selected":    lambda: wait.until(EC.element_to_be_selected((by, locator))),
        "inputable":   lambda: wait.until(EC.element_to_be_clickable((by, locator))),
        "interactable":lambda: wait.until(_first_interactable),
        "stable_list": lambda: wait_for_stable_elements(driver, by, locator, stable_time, timeout),
        # exact count if you really know how many you expect:
        "all_exact":   lambda: wait.until(
                            lambda d: (els := d.find_elements(by, locator)) and
                                      len(els) == expected_count and
                                      els
                        ) if expected_count is not None else None,
    }

    try:
        if wait_type not in wait_map:
            raise ValueError(f"Invalid wait_type: {wait_type!r}")
        return wait_map[wait_type]()
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
        print(f"[WAIT-ERROR] '{wait_type}' failed after {timeout}s on {locator!r}")
        print(f"   {type(e).__name__}: {e}")
        return None


def read(
    driver,
    selector_type,      # "xpath", "css", "id", "class", etc.
    selector,
    content_type="text",
    timeout=20,
    stable_time=1.0     # how long table rows must be stable
):
    by = get_selector_type(selector_type)

    # —— TABLE HANDLING ——  
    if content_type in ("table_rows", "table_data", "table_dict"):
        # **bypass** wait_for_element for stable_list — call the helper directly
        try:
            rows = wait_for_stable_elements(
                driver,               # your real WebDriver
                by,
                f"{selector}//tr",
                stable_time=stable_time,
                timeout=timeout
            )
        except TimeoutException:
            print(f"[READ-ERROR] Table rows under {selector!r} never stabilized in {timeout}s")
            return []

        if content_type == "table_rows":
            return rows

        # build list-of-lists
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
            texts = [c.text.strip() for c in cells]
            if texts:
                data.append(texts)

        if content_type == "table_data":
            return data

        # table_dict
        # first row headers if any <th>
        if rows and rows[0].find_elements(By.TAG_NAME, "th"):
            headers = [c.text.strip() for c in rows[0].find_elements(By.TAG_NAME, "th")]
            data_rows = data[1:]
        else:
            headers = [f"Column_{i+1}" for i in range(len(data[0]) if data else 0)]
            data_rows = data

        dicts = []
        for row_vals in data_rows:
            if len(row_vals) == len(headers):
                dicts.append(dict(zip(headers, row_vals)))
            else:
                # fallback: Column_1, Column_2…
                dicts.append({f"Column_{i+1}": v for i, v in enumerate(row_vals)})
        return dicts

    # —— GENERIC ELEMENT HANDLING ——  
    elements = wait_for_element(driver, "all_present", by, selector, timeout=timeout) or []
    if not elements:
        print(f"No elements found for selector: {selector}")
        return []

    if content_type == "elements":
        return elements
    if content_type == "text":
        return elements[0].text if len(elements) == 1 else [el.text for el in elements]
    if content_type in ("html", "inner_html"):
        return (elements[0].get_attribute("innerHTML")
                if len(elements) == 1
                else [el.get_attribute("innerHTML") for el in elements])
    if content_type == "outer_html":
        return (elements[0].get_attribute("outerHTML")
                if len(elements) == 1
                else [el.get_attribute("outerHTML") for el in elements])
    if content_type == "attribute":
        def attrs(el):
            return {
                "text": el.text,
                "innerHTML": el.get_attribute("innerHTML"),
                "outerHTML": el.get_attribute("outerHTML"),
                "tag_name": el.tag_name,
                "class": el.get_attribute("class"),
                "id": el.get_attribute("id")
            }
        return attrs(elements[0]) if len(elements) == 1 else [attrs(el) for el in elements]

    raise ValueError(
        f"Invalid content_type: {content_type!r}. "
        "Use 'text', 'html', 'inner_html', 'outer_html', 'attribute', "
        "'table_rows', 'table_data', 'table_dict' or 'elements'."
    )