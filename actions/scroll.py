from ..core.mouse import mouse
import time

def scroll_up(n=1):
    for _ in range(n):
        mouse.scroll(0, 1)
        time.sleep(0.02)

def scroll_down(n=1):
    for _ in range(n):
        mouse.scroll(0, -1)
        time.sleep(0.02)