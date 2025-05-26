import cv2
import numpy as np

# Global variables
_visual_initialized = False

def initialize_visual():
    """Initialize the visual processing capabilities."""
    global _visual_initialized
    if _visual_initialized:
        print("Visual processing already initialized")
        return True
        
    try:
        # Test basic CV2 functionality
        test_img = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        _visual_initialized = True
        print("Visual processing initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing visual processing: {e}")
        _visual_initialized = False
        return False

def is_visual_initialized():
    """Check if visual processing is initialized."""
    return _visual_initialized

__all__ = ['initialize_visual', 'is_visual_initialized']
