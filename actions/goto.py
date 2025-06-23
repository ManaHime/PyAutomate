from ..core.browser import init_driver, get_driver

def goto(url, driver=None):
    try:
        if driver is None:
            if get_driver() is None:
                driver = init_driver()
            else:
                driver = get_driver()
        
        driver.get(url)
        return driver
    except Exception as e:
        print(f"Error opening URL: {e}")
        return None