"""The high level control objects to use TM-901pro.



See TM901pro class for docstring.
"""
from PIL import Image
import pyautogui
import cv2
import os
import numpy as np
import pygetwindow as gw

# Load digit templates into a dictionary.
script_directory = os.path.dirname(os.path.abspath(__file__))
template_directory = os.path.join(script_directory, "number_template")
templates = {}
for digit in range(10):
    template_path = os.path.join(template_directory, f"{digit}.png") 
    template = cv2.imread(template_path, 0)  # Load in grayscale
    templates[digit] = template
    
__all__ = [
    'TM901pro'
]

class TM901pro():
    """Need to open TM-901pro software first. Set to DC*10 mode.

    When using it, user need to make sure the window is visible.
    
    methods:
    -- movewindow_and_showontop: Move the window and make it show on the top.
    -- read_mag_field_mT: Read the mearued magnetic field (mT).

    Usage:
    >>> from ccukit.visadriver import TM901pro
    >>> tm901pro = TM901pro()
    >>> mag_field_mT = tm901pro.read_mag_field_mT()
    
    
    """
    def __init__(self):
        """Connect to TM-901pro software and move it to the place we want."""

        # use pygetwindow to capture the window
        windows = gw.getWindowsWithTitle("TM-901pro")
        if windows:
            self.window = windows[0]  # Get the first matching window
        else: 
            raise Exception("TM-901pro software not opened.")
        self.movewindow_and_showontop()

    def movewindow_and_showontop(self, x=100, y=100):
        """Move the window and make it show on the top."""
        # Move the window 
        self.window.moveTo(x, y)

        # move to the top 
        self.window.minimize()   
        self.window.restore() 

    def read_mag_field_mT(self):
        """Read the mearued magnetic field (mT). N is negative, S is positive."""
        # screen shot the measured value
        value_img = screenshot_region((150, 310, 380, 120))

        # screen shot the N/S pixel
        ns_pixel_img = screenshot_region((170, 265, 1, 1))

        # cut the value into four each digits, e+2~e-2, then convert to string then float
        ep2_str = recognize_numerical_value( value_img.crop((  0, 0,  70, 120)) )
        ep1_str = recognize_numerical_value( value_img.crop(( 70, 0, 140, 120)) )
        ep0_str = recognize_numerical_value( value_img.crop((140, 0, 210, 120)) )
        em1_str = recognize_numerical_value( value_img.crop((237, 0, 307, 120)) )
        em2_str = recognize_numerical_value( value_img.crop((307, 0, 377, 120)) )
        value = float(ep2_str + ep1_str + ep0_str + '.' + em1_str + em2_str)

        # extract the N/S
        pixel_color = get_pixel_color(ns_pixel_img)
        if pixel_color == (255, 0, 0): # S
            pass
        else: # N
            value = -value

        return value

def recognize_numerical_value(img):
    """Recognize digit using template matching."""
    img = img.convert("L")  # Convert to grayscale (if not already)
    img = np.array(img)  # Convert PIL image to NumPy arra

    best_match = None
    max_val = 0
    for digit, template in templates.items():
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > 0.8:  # Threshold for match confidence
            best_match = digit
            break
    if best_match is None:
        best_match = '0'
    return str(best_match)


def screenshot_region(region, output_path='') -> Image:
    """Takes a screenshot of a specified region of the screen and saves it to a file.

    region has format (left, top, width, height)
    """
    screenshot = pyautogui.screenshot(region=region)
    if output_path != '':
        screenshot.save(output_path)
    return screenshot

def get_pixel_color(img):
    # Open the image using Pillow
    pixel_color = img.getpixel((0, 0))
    return pixel_color