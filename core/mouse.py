from pynput.mouse import Controller as MouseController
import time
import ctypes
mouse = MouseController()
import cv2
from ..capture.screenshot import screenshot
from ..capture.ocr import ocr, is_ocr_initialized
from ..vision.template import get_text_center_coords, get_img_center_coords
from ..vision import is_visual_initialized
from ..debug import debug_print as _debug_print

def send_input_mouse_move(x: int, y: int):
    """Simulate real mouse move using Windows API (absolute coordinates)"""
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)

    # Convert to absolute (0–65535) scale
    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)

    # MOUSEINPUT structure
    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ('dx', ctypes.c_long),
            ('dy', ctypes.c_long),
            ('mouseData', ctypes.c_ulong),
            ('dwFlags', ctypes.c_ulong),
            ('time', ctypes.c_ulong),
            ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [('mi', MOUSEINPUT)]
        _anonymous_ = ('i',)
        _fields_ = [('type', ctypes.c_ulong), ('i', _I)]

    inp = INPUT(type=0)  # INPUT_MOUSE = 0
    inp.mi = MOUSEINPUT(dx=abs_x,
                        dy=abs_y,
                        mouseData=0,
                        dwFlags=0x8000 | 0x0001,  # MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
                        time=0,
                        dwExtraInfo=None)

    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
    _debug_print(f"Sent input move to ({x}, {y})")

def move_mouse(x: int, y: int, strategy="smooth"):
    """
    Move the mouse to the specified coordinates.
    
    Args:
        x: Target x coordinate
        y: Target y coordinate
        strategy: "smooth" for animated movement, "real" for direct Windows input
    """
    try:
        current_x, current_y = mouse.position
        _debug_print(f"Moving mouse from ({current_x}, {current_y}) to ({x}, {y})")
        
        if strategy == "real":
            # Use Windows API directly for real mouse events
            send_input_mouse_move(x, y)
            return
            
        # Smooth movement strategy
        distance = ((x - current_x)**2 + (y - current_y)**2)**0.5
        
        # For very short distances, move directly
        if distance < 10:
            mouse.position = (x, y)
            _debug_print(f"Short distance move: ({x}, {y})")
            # Send a real mouse event to ensure Windows UI elements respond
            send_input_mouse_move(x, y)
            return
            
        # Calculate steps based on distance
        # Use fewer steps for shorter distances
        steps = max(3, min(20, int(distance / 20)))
        
        # Calculate step size
        dx = (x - current_x) / steps
        dy = (y - current_y) / steps
        
        # Use shorter sleep time for shorter distances
        sleep_time = min(0.01, 0.005 * (distance / 100))
        
        # Move in steps
        for i in range(steps+1):
            new_x = int(current_x + dx*i)
            new_y = int(current_y + dy*i)
            mouse.position = (new_x, new_y)
            time.sleep(sleep_time)
            
        # Verify final position
        final_x, final_y = mouse.position
        if abs(final_x - x) > 5 or abs(final_y - y) > 5:
            print(f"Warning: Mouse position ({final_x}, {final_y}) differs from target ({x}, {y})")
            # Try one final direct move
            mouse.position = (x, y)
            
        # Send a real mouse event to ensure Windows UI elements respond
        send_input_mouse_move(x, y)
            
    except Exception as e:
        print(f"Error moving mouse: {e}")
        raise

def hover(target, x_offset=0, y_offset=0, timeout=None, strategy="smooth"):
    _debug_print(f"Hovering on {target}")
    
    # If target is already coordinates, just add offsets
    if isinstance(target, tuple) and len(target)==2:
        move_mouse(target[0]+x_offset, target[1]+y_offset, strategy)
        return True

    # If target is an image path
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
        
        # Take initial screenshot
        screen_img, _ = screenshot()
        coords = get_img_center_coords(bgr, mask, screen_img, x_offset, y_offset, timeout)
        if coords:
            _debug_print(f"Found coordinates: {coords}")
            move_mouse(coords[0], coords[1], strategy)
            return True
        return False

    # Otherwise treat as OCR-text
    if not is_ocr_initialized():
        print("OCR not initialized. Call initialize_ocr() first.")
        return False
        
    if not is_visual_initialized():
        print("Visual processing not initialized. Call initialize_visual() first.")
        return False
        
    scale_factor = 2
    img_arr, region = screenshot()
    scaled_img = cv2.resize(img_arr, None, fx=scale_factor, fy=scale_factor)
    ocr_res = ocr(scaled_img, region)
    coords = get_text_center_coords(ocr_res, target, scale_factor, x_offset, y_offset)
    if coords:
        _debug_print(f"Found coordinates: {coords}")
        move_mouse(coords[0], coords[1], strategy)
        return True
    return False