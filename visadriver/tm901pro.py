"""The high level control objects to use TM-901pro.






"""
from PIL import Image
import pytesseract
import pyautogui

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

__all__ = [
    'TM901pro'
]

import pygetwindow as gw
class TM901pro():
    """Need to open TM-901pro software first. Set to DC*10 mode.
    
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
        # screen shot the value region before and after decimal point
        screenshot_region((150, 310, 210, 120), 'beforedot.png')
        screenshot_region((385, 310, 150, 120), 'afterdot.png')

        # screen shot the N/S pixel
        screenshot_region((170, 265, 1, 1), 'NS_pixel.png')

        # extract the value
        beforedot_str = recognize_numerical_value('beforedot.png')
        afterdot_str = recognize_numerical_value('afterdot.png')
        value = float(beforedot_str + '.' + afterdot_str)

        # extract the N/S
        pixel_color = get_pixel_color('NS_pixel.png')
        if pixel_color == (255, 0, 0): # S
            pass
        else: # N
            value = -value

        return value


def recognize_numerical_value(image_path):
    """Read the numerical value from image"""
    # Use pytesseract to do OCR on the image
    img = Image.open(image_path)
    text = pytesseract.image_to_string(
        img, 
        config='--psm 7 -c tessedit_char_whitelist=0123456789 digits'
    )
    
    value_str = ''.join(filter(str.isdigit, text))
    
    return value_str

from PIL import Image, ImageEnhance




def screenshot_region(region, output_path):
    """Takes a screenshot of a specified region of the screen and saves it to a file.

    region has formate (left, top, width, height)
    """
    screenshot = pyautogui.screenshot(region=region)
    screenshot.save(output_path)

def get_pixel_color(image_path):
    # Open the image using Pillow
    img = Image.open(image_path)
    
    # Get the color of the single pixel
    pixel_color = img.getpixel((0, 0))

    return pixel_color