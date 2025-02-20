"""General tools in `general.py  will be imported when `import ccukit`.

functions:
-- get_path: Pop up a dialog to browse a file path then return it.
-- plot_trace: Plot the trace of Im vs Re, Mag vs Freq, and Phase vs Freq.

Developer should add new function/class/object name in the `__all__` list.
"""

from tkinter import Tk, filedialog
import ctypes
from matplotlib import pyplot as plt
import numpy as np

__all__ = [
    'get_path',
    'plot_trace',
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

def plot_trace(freq, signal):
    """Plot the trace of Imaginary vs Real, Magnitude vs Frequency, and Phase vs Frequency."""

    # Create figure and subplots
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
    
    # Plot Imaginary vs Real part
    axes[0].plot(np.real(signal), np.imag(signal), 'y.')
    axes[0].set_xlabel("Real")
    axes[0].set_ylabel("Imaginary")
    axes[0].set_title("Imaginary vs Real")
    axes[0].grid()
    
    # Plot Magnitude vs Frequency
    axes[1].plot(freq, np.abs(signal), '-')
    axes[1].set_xlabel("Frequency Index")
    axes[1].set_ylabel("Magnitude")
    axes[1].set_title("Magnitude vs Frequency")
    axes[1].set_xlim([min(freq), max(freq)])
    axes[1].grid()
    
    # Plot Phase vs Frequency
    axes[2].plot(freq, np.angle(signal), '-')
    axes[2].set_xlabel("Frequency Index")
    axes[2].set_ylabel("Phase (radians)")
    axes[2].set_title("Phase vs Frequency")
    axes[2].set_xlim([min(freq), max(freq)])
    axes[2].grid()
    
    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()