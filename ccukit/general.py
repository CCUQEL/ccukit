"""General tools in `general.py  will be imported when `import ccukit`.
"""

from tkinter import Tk, filedialog
import ctypes

__all__ = [
    'get_path'
]

def get_path(ext: str, title = 'Select a file path', save_file = False):
    """Pop up a dialog to browse a file path then return it.

    Example usage:
    >>> from ccukit import get_path
    >>> filepath = get_path('.hdf5', title = 'MEASURMENT data')
    
    Argumenumt
    ----------
    -- ext: The filename extestion.
    -- title: The title displayed on the dialog.
    -- save_file: For it's True, it ask a path to save a file.
    
    Return
    ----------
    -- filepath: the selected filepath, empty string when canceled.
    """
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    if save_file:
        dialog = filedialog.asksaveasfilename
    else:
        dialog = filedialog.askopenfilename
    filepath = dialog(filetypes = [(ext.upper() + ' Files', ext)],
                      title = title)
    return filepath