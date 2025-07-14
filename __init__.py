from .core.keyboard import type, key, clear, ime_on, ime_off, confirm_input
from .core.mouse import move_mouse, hover
from .capture.screenshot import screenshot
from .capture.ocr import ocr, initialize_ocr, is_ocr_initialized
from .vision.template import get_img_center_coords, get_text_center_coords, wait_for_screen_change
from .vision import initialize_visual, is_visual_initialized
from .actions.click import click, dbclick, rightclick
from .actions.wait_presence import wait_presence
from .actions.scroll import scroll_up, scroll_down
from .actions.goto import goto
from .core.browser import init_driver, get_driver, close_driver, close_all_drivers, read, select_by_value, wait_element_hidden, get_elements
from .utils import clipboard, clipboard_copy

__all__ = [
    "type", "key", "clear", "ime_on", "ime_off", "confirm_input",
    "move_mouse", "hover",
    "init_driver", "get_driver", "close_driver", "close_all_drivers", "read", "select_by_value", "wait_element_hidden", "get_elements",
    "goto",
    "screenshot", "ocr",
    "wait_for_screen_change",
    "initialize_ocr", "is_ocr_initialized",
    "initialize_visual", "is_visual_initialized",
    "get_img_center_coords", "get_text_center_coords",
    "click", "dbclick", "rightclick",
    "scroll_up", "scroll_down",
    "clipboard", "clipboard_copy",
    "wait_presence",
]

# Initialize OCR by default for backward compatibility
initialize_ocr()