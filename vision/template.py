import cv2, numpy as np
import mss
import time
from ..capture.ocr import last_screenshot_region, ocr
from ..capture.screenshot import screenshot
from ..debug import debug_print as _debug_print, set_debug_mode

__all__ = [
    'get_img_center_coords',
    'get_text_center_coords',
    'wait_for_text',
    'wait_for_screen_change',
    'set_debug_mode'
]

def get_text_center_coords(ocr_result, target_text: str, scale_factor: int = 2, x_offset: int = 0, y_offset: int = 0):
    full_text = ''.join([t for t in ocr_result['text'] if t.strip()])
    _debug_print(f"Looking for text: {target_text}\nFound text: {full_text}")
    
    # Print all detected text with their positions
    _debug_print("\nDetected text blocks:")
    for i,(text,conf) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip():
            _debug_print(f"'{text}': {conf}% at ({ocr_result['left'][i]}, {ocr_result['top'][i]}) size {ocr_result['width'][i]}x{ocr_result['height'][i]}")
    
    # Try exact match first
    for i,(text,_) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip() and text == target_text:
            if last_screenshot_region is not None:
                r = last_screenshot_region
                # Calculate center in original coordinates first
                center_x = ocr_result['left'][i] + ocr_result['width'][i] / 2
                center_y = ocr_result['top'][i] + ocr_result['height'][i] / 2
                
                # Then scale down and add offsets
                cx = r['left'] + int(center_x / scale_factor) + x_offset
                cy = r['top'] + int(center_y / scale_factor) + y_offset
            else:
                # Calculate center in original coordinates first
                center_x = ocr_result['left'][i] + ocr_result['width'][i] / 2
                center_y = ocr_result['top'][i] + ocr_result['height'][i] / 2
                
                # Then scale down and add offsets
                cx = int(center_x / scale_factor) + x_offset
                cy = int(center_y / scale_factor) + y_offset
            _debug_print(f"Found exact match. Original position: ({center_x}, {center_y}), Scaled: ({cx}, {cy})")
            return (cx, cy)
    
    # If exact match fails, try partial match
    for i,(text,conf) in enumerate(zip(ocr_result['text'], ocr_result['conf'])):
        if text.strip() and target_text in text and conf > 40:  # Only consider matches with confidence > 40%
            # Calculate the position of the target text within the detected text
            start_pos = text.find(target_text)
            text_width = ocr_result['width'][i]
            target_width = len(target_text) * (text_width / len(text))  # Estimate target width proportionally
            
            if last_screenshot_region is not None:
                r = last_screenshot_region
                # Calculate center in original coordinates first
                center_x = ocr_result['left'][i] + (start_pos * text_width / len(text) + target_width/2)
                center_y = ocr_result['top'][i] + ocr_result['height'][i]/2
                
                # Then scale down and add offsets
                cx = r['left'] + int(center_x / scale_factor) + x_offset
                cy = r['top'] + int(center_y / scale_factor) + y_offset
            else:
                # Calculate center in original coordinates first
                center_x = ocr_result['left'][i] + (start_pos * text_width / len(text) + target_width/2)
                center_y = ocr_result['top'][i] + ocr_result['height'][i]/2
                
                # Then scale down and add offsets
                cx = int(center_x / scale_factor) + x_offset
                cy = int(center_y / scale_factor) + y_offset
                
            _debug_print(f"Found partial match in '{text}'. Original position: ({center_x}, {center_y}), Scaled: ({cx}, {cy})")
            return (cx, cy)
    
    _debug_print("No match found for text:", target_text)
    return None

def get_img_center_coords(template_bgr: np.ndarray,
                        mask:         np.ndarray,
                        screen_img:   np.ndarray = None,
                        x_offset:     int = 0,
                        y_offset:     int = 0,
                        timeout:      float = None):
    """
    Handles both masked and unmasked template matching with enhanced validation and fallback for low-edge templates.
    Returns coordinates if found, None if not found.
    
    Args:
        template_bgr: The template image to search for
        mask: Optional mask for the template
        screen_img: Optional screenshot to search in (will take new screenshot if None)
        x_offset: X offset to add to found coordinates
        y_offset: Y offset to add to found coordinates
        timeout: Optional timeout in seconds. If provided, will keep trying until timeout is reached.
    """
    if screen_img is None:
        screen_img, region = screenshot()
    else:
        region = None
    screen_gray  = cv2.cvtColor(screen_img,  cv2.COLOR_BGR2GRAY)
    templ_gray   = cv2.cvtColor(template_bgr,cv2.COLOR_BGR2GRAY)

    # Check if template is larger than screen
    if templ_gray.shape[0] > screen_gray.shape[0] or templ_gray.shape[1] > screen_gray.shape[1]:
        _debug_print("Template image is larger than screen")
        return None

    # Validate mask if provided
    has_valid_mask = False
    if mask is not None:
        if mask.shape != templ_gray.shape[:2]:
            _debug_print("Mask shape doesn't match template shape")
            return None
        if not np.any(mask):  # Check if mask is empty
            _debug_print("Empty mask")
            return None
        has_valid_mask = True

    # Apply edge detection to both template and screen
    template_edges = cv2.Canny(templ_gray, 100, 200)
    screen_edges = cv2.Canny(screen_gray, 100, 200)

    # Count edge pixels in template
    edge_pixel_count = np.count_nonzero(template_edges)
    edge_ratio = edge_pixel_count / template_edges.size
    _debug_print(f"Template edge pixel count: {edge_pixel_count}, ratio: {edge_ratio:.3f}")

    # Adjust thresholds based on image dimensions
    h, w = templ_gray.shape
    is_text_like = w > h * 3  # If width is more than 3x height, consider it text-like
    _debug_print(f"Image is {'text-like' if is_text_like else 'icon-like'}")
    
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

    def try_match():
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

                _debug_print(f"{method_name}: val={val:.2f}, edge_val={edge_val:.2f}, loc={loc}, edge_loc={edge_min_loc if method == cv2.TM_SQDIFF_NORMED else edge_max_loc}")

                # Skip invalid values
                if not np.isfinite(val) or not np.isfinite(edge_val):
                    _debug_print(f"Skipping {method_name} due to invalid confidence value")
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
                _debug_print(f"Error with {method_name}: {e}")
                continue

        if not valid_matches:
            if fallback_matches:
                _debug_print("Using fallback match due to low edge content.")
                valid_matches = fallback_matches
            else:
                _debug_print("No valid matches found with confidence > 0.8")
                return None

        # Sort matches by confidence
        valid_matches.sort(reverse=True)
        best_val, best_loc, best_method, best_edge_val = valid_matches[0]

        # Additional validation: Check if there are multiple high-confidence matches
        if len(valid_matches) > 1:
            second_best_val = valid_matches[1][0]
            if abs(best_val - second_best_val) < 0.1:  # If multiple matches are very close
                _debug_print("Multiple high-confidence matches found, rejecting to avoid ambiguity")
                _debug_print(f"Best match: {best_val:.2f} (edge: {best_edge_val:.2f}) at {best_loc}")
                _debug_print(f"Second best: {second_best_val:.2f} (edge: {valid_matches[1][3]:.2f}) at {valid_matches[1][1]}")
                return None

        h, w = templ_gray.shape
        cx = best_loc[0] + w//2 + x_offset
        cy = best_loc[1] + h//2 + y_offset
        
        # If we have a region from screenshot, use its offset
        if region is not None:
            cx += region['left']
            cy += region['top']
            
        _debug_print(f"Found! Method: {best_method}, Confidence: {best_val:.2f} (edge: {best_edge_val:.2f}), Coordinates: ({cx},{cy})")
        return (cx, cy)

    # If no timeout, just try once
    if timeout is None:
        return try_match()

    # Otherwise, keep trying until timeout
    start_time = time.time()
    last_match = None
    stable_count = 0
    required_stable_matches = 2  # Number of consecutive matches needed to consider it stable
    check_interval = 0.05  # Check every 50ms instead of 100ms
    
    while True:
        result = try_match()
        if result is not None:
            if last_match is None:
                last_match = result
                stable_count = 1
            else:
                # Check if this match is close to the last one
                dx = abs(result[0] - last_match[0])
                dy = abs(result[1] - last_match[1])
                if dx < 5 and dy < 5:  # If within 5 pixels
                    stable_count += 1
                    if stable_count >= required_stable_matches:
                        elapsed = time.time() - start_time
                        _debug_print(f"Found stable match after {elapsed:.2f} seconds")
                        return result
                else:
                    stable_count = 1
                last_match = result
            
        # Check if we've exceeded the timeout
        if time.time() - start_time > timeout:
            _debug_print(f"Timeout reached ({timeout}s) while searching for template")
            return None
            
        # Take a new screenshot for the next attempt
        screen_img, region = screenshot()
        screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
        screen_edges = cv2.Canny(screen_gray, 100, 200)
        
        # Wait a bit before trying again
        time.sleep(check_interval)

def wait_for_text(target_text: str, timeout: float = 5.0, check_interval: float = 0.1):
    """
    Wait for text to appear on screen with timeout.
    Returns True if text was found, False if timeout occurred.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Take screenshot and do OCR
        screen_img, region = screenshot()
        ocr_result = ocr.ocr(screen_img)
        
        # Check if text exists
        full_text = ''.join([t for t in ocr_result['text'] if t.strip()])
        if target_text in full_text:
            return True
            
        time.sleep(check_interval)
    
    return False

def wait_for_screen_change(timeout: float = 5.0, check_interval: float = 0.1):
    """
    Wait for screen to change with timeout.
    Returns True if screen changed, False if timeout occurred.
    """
    start_time = time.time()
    current_screen, _ = screenshot()
    while time.time() - start_time < timeout:
        new_screen, _ = screenshot()
        # Check if arrays are different using numpy's array comparison
        if not np.array_equal(new_screen, current_screen):
            return True
        time.sleep(check_interval)
    return False