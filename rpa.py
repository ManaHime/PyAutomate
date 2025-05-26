import mss
import numpy as np
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import time
import cv2
import easyocr
import torch

# Check if CUDA is available
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Using GPU: {torch.cuda.get_device_name(0)}")

# Initialize EasyOCR reader with error handling
try:
    reader = easyocr.Reader(
        ['ja', 'en'],
        gpu=True, 
        model_storage_directory='./models',
        download_enabled=True,
        recog_network='japanese_g2'
    )
    print("EasyOCR initialized successfully")
except Exception as e:
    print(f"Error initializing EasyOCR: {e}")
    raise

keyboard = KeyboardController()
mouse = MouseController()

def type(text: str):
    keyboard.type(text)

def is_modifier(k):
    return k.lower() in ['ctrl', 'alt', 'shift', 'cmd', 'win']

def get_key(k):
    try:
        return getattr(Key, k.lower())
    except AttributeError:
        return k.lower()

def key(input_str: str):
    if input_str.startswith("[") and input_str.endswith("]"):
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

def move_mouse(x: int, y: int):
    current_x, current_y = mouse.position
    distance = ((x - current_x)**2 + (y - current_y)**2)**0.5
    reference = (1920**2 + 1080**2)**0.5
    steps = max(5, int(150 * (distance / reference)))
    dx = (x - current_x) / steps
    dy = (y - current_y) / steps
    for i in range(steps+1):
        mouse.position = (int(current_x + dx*i), int(current_y + dy*i))
        time.sleep(0.01)

def hover_on_text_center(ocr_result, target_text: str, scale_factor: int = 2, x_offset: int = 0, y_offset: int = 0):
    full_text = ''.join([t for t in ocr_result['text'] if t.strip()])
    print(f"Looking for text: {target_text}\nFound text: {full_text}")
    for i,(text,conf) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip():
            print(f"'{text}': {conf}%")
    
    # Try exact match first
    for i,(text,_) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip() and text == target_text:
            if 'last_screenshot_region' in globals():
                r = last_screenshot_region
                cx = r['left'] + int((ocr_result['left'][i] + ocr_result['width'][i] / 2) / scale_factor) + x_offset
                cy = r['top']  + int((ocr_result['top'][i]  + ocr_result['height'][i] / 2) / scale_factor) + y_offset
            else:
                cx = int((ocr_result['left'][i] + ocr_result['width'][i] / 2) / scale_factor) + x_offset
                cy = int((ocr_result['top'][i]  + ocr_result['height'][i] / 2) / scale_factor) + y_offset
            print(f"Moving to: ({cx},{cy})")
            hover((cx, cy))
            return True
    
    # If exact match fails, try partial match
    for i,(text,conf) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip() and target_text in text and conf > 40:  # Only consider matches with confidence > 40%
            # Calculate the position of the target text within the detected text
            start_pos = text.find(target_text)
            text_width = ocr_result['width'][i]
            target_width = len(target_text) * (text_width / len(text))  # Estimate target width proportionally
            
            if 'last_screenshot_region' in globals():
                r = last_screenshot_region
                # Adjust the x position based on where the target text appears in the detected text
                cx = r['left'] + (ocr_result['left'][i] + (start_pos * text_width / len(text) + target_width/2))//2 + x_offset
                cy = r['top']  + (ocr_result['top'][i]  + ocr_result['height'][i]//2)//2 + y_offset
            else:
                cx = (ocr_result['left'][i] + (start_pos * text_width / len(text) + target_width/2))//2 + x_offset
                cy = (ocr_result['top'][i]  + ocr_result['height'][i]//2)//2 + y_offset
            print(f"Partial match found. Moving to: ({cx},{cy})")
            hover((cx, cy))
            return True
    
    return False

def hover_on_img_center(template_bgr: np.ndarray,
                        mask:         np.ndarray,
                        screen_img:   np.ndarray = None,
                        x_offset:     int = 0,
                        y_offset:     int = 0):
    """
    Handles both masked and unmasked template matching with enhanced validation and fallback for low-edge templates.
    """
    if screen_img is None:
        screen_img, _ = screenshot()
    screen_gray  = cv2.cvtColor(screen_img,  cv2.COLOR_BGR2GRAY)
    templ_gray   = cv2.cvtColor(template_bgr,cv2.COLOR_BGR2GRAY)

    # Check if template is larger than screen
    if templ_gray.shape[0] > screen_gray.shape[0] or templ_gray.shape[1] > screen_gray.shape[1]:
        print("Template image is larger than screen")
        return False

    # Validate mask if provided
    has_valid_mask = False
    if mask is not None:
        if mask.shape != templ_gray.shape[:2]:
            print("Mask shape doesn't match template shape")
            return False
        if not np.any(mask):  # Check if mask is empty
            print("Empty mask")
            return False
        has_valid_mask = True

    # Apply edge detection to both template and screen
    template_edges = cv2.Canny(templ_gray, 100, 200)
    screen_edges = cv2.Canny(screen_gray, 100, 200)

    # Count edge pixels in template
    edge_pixel_count = np.count_nonzero(template_edges)
    edge_ratio = edge_pixel_count / template_edges.size
    print(f"Template edge pixel count: {edge_pixel_count}, ratio: {edge_ratio:.3f}")

    # Adjust thresholds based on image dimensions
    h, w = templ_gray.shape
    is_text_like = w > h * 3  # If width is more than 3x height, consider it text-like
    print(f"Image is {'text-like' if is_text_like else 'icon-like'}")
    
    # Adjust thresholds for text-like images
    edge_threshold = 0.3 if is_text_like else 0.5  # Lower edge threshold for text
    distance_threshold = 20 if is_text_like else 10  # More lenient distance for text
    fallback_edge_ratio = 0.1 if is_text_like else 0.05  # More lenient edge ratio for text

    # Try different template matching methods
    methods = [
        ('TM_SQDIFF_NORMED', cv2.TM_SQDIFF_NORMED),
        ('TM_CCOEFF_NORMED', cv2.TM_CCOEFF_NORMED),
        ('TM_CCORR_NORMED', cv2.TM_CCORR_NORMED)
    ]

    best_val = -1
    best_loc = None
    best_method = None
    valid_matches = []
    fallback_matches = []

    for method_name, method in methods:
        try:
            # Match on both original and edge-detected images
            result = cv2.matchTemplate(screen_gray, templ_gray, method, mask=mask if has_valid_mask else None)
            edge_result = cv2.matchTemplate(screen_edges, template_edges, method, mask=mask if has_valid_mask else None)
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            edge_min_val, edge_max_val, edge_min_loc, edge_max_loc = cv2.minMaxLoc(edge_result)
            
            # For TM_SQDIFF_NORMED, the best match is the minimum value
            if method == cv2.TM_SQDIFF_NORMED:
                val = 1 - min_val  # Convert to similarity score
                edge_val = 1 - edge_min_val
                loc = min_loc
            else:
                val = max_val
                edge_val = edge_max_val
                loc = max_loc

            print(f"{method_name}: val={val:.2f}, edge_val={edge_val:.2f}, loc={loc}, edge_loc={edge_min_loc if method == cv2.TM_SQDIFF_NORMED else edge_max_loc}")

            # Skip invalid values
            if not np.isfinite(val) or not np.isfinite(edge_val):
                print(f"Skipping {method_name} due to invalid confidence value")
                continue

            # Only consider matches with high confidence in both original and edge detection
            if val > 0.8 and edge_val > edge_threshold:
                # Calculate the distance between the two match locations
                loc_distance = ((loc[0] - edge_min_loc[0])**2 + (loc[1] - edge_min_loc[1])**2)**0.5
                if loc_distance < distance_threshold:
                    valid_matches.append((val, loc, method_name, edge_val))

            # Fallback: if template has very little edge content, allow strong original match
            elif val > 0.9 and edge_ratio < fallback_edge_ratio:
                fallback_matches.append((val, loc, method_name, edge_val))



        except Exception as e:
            print(f"Error with {method_name}: {e}")
            continue

    if not valid_matches:
        if fallback_matches:
            print("Using fallback match due to low edge content.")
            valid_matches = fallback_matches
        else:
            print("No valid matches found with confidence > 0.8")
            return False

    # Sort matches by confidence
    valid_matches.sort(reverse=True)
    best_val, best_loc, best_method, best_edge_val = valid_matches[0]

    # Additional validation: Check if there are multiple high-confidence matches
    if len(valid_matches) > 1:
        second_best_val = valid_matches[1][0]
        if abs(best_val - second_best_val) < 0.1:  # If multiple matches are very close
            print("Multiple high-confidence matches found, rejecting to avoid ambiguity")
            print(f"Best match: {best_val:.2f} (edge: {best_edge_val:.2f}) at {best_loc}")
            print(f"Second best: {second_best_val:.2f} (edge: {valid_matches[1][3]:.2f}) at {valid_matches[1][1]}")
            return False

    h, w = templ_gray.shape
    cx = best_loc[0] + w//2 + x_offset
    cy = best_loc[1] + h//2 + y_offset
    # account for monitor offset
    mon = mss.mss().monitors[1]
    cx += mon['left']; cy += mon['top']
    print(f"Found! Method: {best_method}, Confidence: {best_val:.2f} (edge: {best_edge_val:.2f}), Moving to: ({cx},{cy})")
    move_mouse(cx, cy)
    return True

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

def ocr(img: np.ndarray, region: dict = None):
    try:
        if img.ndim==2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        results = reader.readtext(img)
        data = {'text':[],'left':[],'top':[],'width':[],'height':[],'conf':[]}
        for bbox, text, prob in results:
            x1,y1 = bbox[0]; x2,y2 = bbox[2]
            data['text'].append(text)
            data['left'].append(int(x1))
            data['top'].append(int(y1))
            data['width'].append(int(x2-x1))
            data['height'].append(int(y2-y1))
            data['conf'].append(int(prob*100))
        if region:
            global last_screenshot_region
            last_screenshot_region = region
        return data
    except Exception as e:
        print(f"OCR error: {e}")
        return {'text':[],'left':[],'top':[],'width':[],'height':[],'conf':[]}

def hover(target, x_offset=0, y_offset=0):
    print(f"Hovering on {target}")
    if isinstance(target, tuple) and len(target)==2:
        move_mouse(target[0]+x_offset, target[1]+y_offset)
        return True

    if isinstance(target, str) and (target.startswith('img/') or target.startswith('/img/')):
        img_path = target.lstrip('/')
        print(f"Looking for image {img_path}")
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print("Failed to load image")
            return False
        bgr   = img[...,:3]
        alpha = img[..., 3]
        _, mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
        screen_img, _ = screenshot()
        return hover_on_img_center(bgr, mask, screen_img, x_offset, y_offset)

    # otherwise treat as OCR-text
    scale_factor = 2
    img_arr, region = screenshot()
    scaled_img = cv2.resize(img_arr, None, fx=scale_factor, fy=scale_factor)
    ocr_res = ocr(scaled_img, region)
    return hover_on_text_center(ocr_res, target, scale_factor, x_offset, y_offset)

def click(target, x_offset=0, y_offset=0):
    if hover(target, x_offset, y_offset):
        try:
            mouse.press(Button.left); time.sleep(0.1)
            mouse.release(Button.left)
            return True
        except Exception as e:
            print(f"Click error: {e}")
    return False

def dbclick(target, x_offset=0, y_offset=0):
    if hover(target, x_offset, y_offset):
        try:
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            time.sleep(0.1)
            mouse.press(Button.left); time.sleep(0.1); mouse.release(Button.left)
            return True
        except Exception as e:
            print(f"Double-click error: {e}")
    return False

def rightclick(target, x_offset=0, y_offset=0):
    if hover(target, x_offset, y_offset):
        try:
            mouse.press(Button.right)
            time.sleep(0.1)
            mouse.release(Button.right)
            return True
        except Exception as e:
            print(f"Right-click error: {e}")
    return False

def scrollUp(n=1):
    for _ in range(n):
        mouse.scroll(0, 1)
        time.sleep(0.02)

def scrollDown(n=1):
    for _ in range(n):
        mouse.scroll(0, -1)
        time.sleep(0.02)
