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
    'set_plot_style',
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
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Magnitude")
    axes[1].set_title("Magnitude vs Frequency")
    axes[1].set_xlim([min(freq), max(freq)])
    axes[1].grid()
    
    # Plot Phase vs Frequency
    axes[2].plot(freq, np.angle(signal), '-')
    axes[2].set_xlabel("Frequency")
    axes[2].set_ylabel("Phase (radians)")
    axes[2].set_title("Phase vs Frequency")
    axes[2].set_xlim([min(freq), max(freq)])
    axes[2].grid()
    
    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()

def set_plot_style():
    """Modify the plot style of matplotlib. I don't like default one. 

    It also returns a dictionary to set marker as a hollow one.

    Example:
    >>> from matplotlib import pyplot as plt
    >>> hms = set_plot_style()
    >>> plt.plot([0], [0], 'o', **hms)
    >>> plt.show()
    """
    plt.rcParams.update({
        #### Font settings
        'font.family': 'Times New Roman',
        'mathtext.fontset': 'cm',
        'mathtext.rm': 'serif',
        'mathtext.it': 'serif:italic',
        'mathtext.bf': 'serif:bold',
        'axes.labelsize': 15,
        'axes.titlesize': 20,
        # pad
        'axes.titlepad': 10,  # Padding for title
        # for xy label pad, write labelpad=pad as parm.

        #### Ticks
        # general
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        # tick on/off
        'xtick.bottom': True,
        'xtick.top': False,
        'ytick.left': True,
        'ytick.right': False,
        # tick-label on/off
        'xtick.labelbottom': True,
        'xtick.labeltop': False,
        'ytick.labelleft': True,
        'ytick.labelright': False,
        # about major-ticks
        'xtick.major.size': 8,
        'ytick.major.size': 8,
        'xtick.labelsize': 14,  # fontsize
        'ytick.labelsize': 14,  # fontsize
        # about mirror-ticks (plt.minorticks_on())
        'xtick.minor.visible': True,
        'ytick.minor.visible': True,
        'xtick.minor.size': 3,
        'ytick.minor.size': 3,
        #'xtick.minor.ndivs': ['auto', 4][1],
        #'ytick.minor.ndivs': ['auto', 4][1],

        #### legend
        'legend.fontsize': 11,
        'legend.title_fontsize': 18, 
        'legend.labelspacing': 0.4,
        'legend.frameon': True,
        'legend.handletextpad': 0.2,
        'legend.loc': ['best', 0][0], # 0~10
        'legend.markerscale': 2.0,

        #### axes
        # general
        'axes.linewidth': 0.8,
        # spines
        'axes.spines.bottom': True,
        'axes.spines.left': True,
        'axes.spines.right': True,
        'axes.spines.top': True,
        # margin (xy lim, percentage)
        'axes.xmargin': 0.0,  
        'axes.ymargin': 0.05, 
        'axes.zmargin': 0.05, 

        # grid
        'axes.grid': False,
        'axes.grid.axis': ['both', 'x', 'y'][0],
        'axes.grid.which': ['major', 'minor', 'both'][0],
        'grid.alpha': 0.3, # transparency
        'grid.color': '#000000',
        'grid.linestyle': '-',
        'grid.linewidth': 0.8,
    })

    hollow_marker_setting = {
        'markerfacecolor': 'none',
        'markersize': 6, 
        'markeredgewidth': 1.5
    }

    return hollow_marker_setting