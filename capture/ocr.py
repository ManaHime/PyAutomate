import easyocr
import numpy as np
import cv2

# Global variables
reader = None
last_screenshot_region = None

def initialize_ocr():
    """Initialize the EasyOCR reader if not already initialized."""
    global reader
    if reader is not None:
        print("EasyOCR already initialized")
        return True
        
    try:
        reader = easyocr.Reader(
            ['ja', 'en'],
            gpu=True, 
            model_storage_directory='./models',
            download_enabled=True,
            recog_network='japanese_g2'
        )
        print("EasyOCR initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        reader = None
        return False

def is_ocr_initialized():
    """Check if EasyOCR is initialized."""
    return reader is not None

def ocr(img: np.ndarray, region: dict = None):
    """Perform OCR on the given image."""
    if not is_ocr_initialized():
        print("EasyOCR not initialized. Call initialize_ocr() first.")
        return {'text':[],'left':[],'top':[],'width':[],'height':[],'conf':[]}
        
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

__all__ = ['ocr', 'initialize_ocr', 'is_ocr_initialized']