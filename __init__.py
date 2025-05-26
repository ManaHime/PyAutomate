from .core.keyboard import type, key
from .core.mouse import move_mouse, hover
from .capture.screenshot import screenshot
from .capture.ocr import ocr, initialize_ocr, is_ocr_initialized
from .vision.template import get_img_center_coords, get_text_center_coords, wait_for_screen_change
from .vision import initialize_visual, is_visual_initialized
from .actions.click import click, dbclick, rightclick
from .actions.wait_presence import wait_presence
from .actions.scroll import scroll_up, scroll_down
from .utils import clipboard

__all__ = [
    "type", "key",
    "move_mouse", "hover",
    "screenshot", "ocr",
    "wait_for_screen_change",
    "initialize_ocr", "is_ocr_initialized",
    "initialize_visual", "is_visual_initialized",
    "get_img_center_coords", "get_text_center_coords",
    "click", "dbclick", "rightclick",
    "scroll_up", "scroll_down",
    "clipboard",
    "wait_presence"
]

# Initialize OCR by default for backward compatibility
initialize_ocr()