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
import csv
import os
import sys
from datetime import datetime
from os.path import isdir, isfile, join



__all__ = [
    'get_path',
    'get_folderpath',
    'plot_trace',
    'set_plot_style',
    'save_to_csv',
    'get_run_script_func'
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

def get_folderpath(title='Select a folder'):
    """Pop up a dialog to browse and select a folder.

    Example usage:
    >>> folder = get_folderpath('Select a data folder')
    
    Args:
        title (str): The title displayed on the dialog.

    Returns:
        str: The selected folder path. Empty string if canceled.
    """
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    folderpath = filedialog.askdirectory(title=title)
    return folderpath


def plot_trace(freq, signal):
    """Plot the trace of Imaginary vs Real, Magnitude vs Frequency, and Phase vs Frequency."""

    # Create figure and subplots
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    # Plot Imaginary vs Real part
    axes[0].plot(np.real(signal), np.imag(signal), 'y.')
    axes[0].set_xlabel("Real")
    axes[0].set_ylabel("Imaginary")
    axes[0].set_title("Imaginary vs Real", fontsize=17)
    axes[0].set_aspect('equal')
    axes[0].grid()
    
    # Plot Magnitude vs Frequency
    axes[1].plot(freq, np.abs(signal), '-')
    axes[1].set_xlabel("Frequency")
    axes[1].set_ylabel("Magnitude")
    axes[1].set_title("Magnitude vs Frequency", fontsize=17)
    axes[1].set_xlim([min(freq), max(freq)])
    #axes[1].tick_params(axis='both', which='major', labelsize=12)
    axes[1].grid()
    
    
    # Plot Phase vs Frequency
    axes[2].plot(freq, np.unwrap(np.angle(signal)), '-')
    axes[2].set_xlabel("Frequency")
    axes[2].set_ylabel("Phase")
    axes[2].set_title("Phase vs Frequency", fontsize=17)
    axes[2].set_xlim([min(freq), max(freq)])
    #axes[2].tick_params(axis='both', which='major', labelsize=12)
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

def save_to_csv(filename, title_array, data_array):
    """
    Saves the given title_array and data_array to a CSV file with two columns.
    
    Example:
    >>> data1 = [1, 2, 3, 4]
    >>> data2 = [5, 6, 7, 8]
    >>> title_array = ["Column 1", "Column 2"]
    >>> data_array = [data1, data2]
    >>> save_to_csv("data.csv", title_array, data_array)
    
    Parameters:
    filename (str): Name of the CSV file to save.
    title_array (list): List containing two column titles.
    data_array (list or numpy.ndarray): 2D list or numpy array where each sublist represents a column.
    """
    # Ensure data_array is a numpy array for easier column-wise processing
    data_array = np.array(data_array)
    
    # Transpose data to align with two-column format
    data_array = data_array.T.tolist()
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(title_array)  # Write the header row
        writer.writerows(data_array)  # Write the data as two columns

from Labber import ScriptTools
def get_run_script_func(
    template_path,
    data_save_folder=r'C:\Users\QEL\Labber\Data',
    labber_install_path=r'C:\Program Files\Keysight\Labber',
    ):
    """Return a function that can run the script, based on template provided.
    
    Example usage:
    >>> run_script = get_run_script_func(template_path=template_path)
    >>> override = {
    >>>     # VNA
    >>>     'VNA - Start frequency': {'single': 4e+9},
    >>>     'VNA - Stop frequency': {'single': 5e+9},
    >>>     'VNA - # of points': {'single': 401},
    >>>     # DC
    >>>     'DC supply - 1 - Current': {
    >>>         'start': 2.5e-3,
    >>>         'stop': 7.5e-3,
    >>>         'n_pts': 11,
    >>>     },
    >>>     'DC supply - 2 - Current': {'single': 4e-3}
    >>> }
    >>> save_path = run_script(save_name='save_name', override=override)
    """
    def get_datafolder_today(database_folder):
        """Get data folder for storing mearuement data of Labber, for today's date."""
        # check for the root folder exist
        if not isdir(database_folder):
            raise Exception(f'the labber database folder `{database_folder}` does not exist.')
        
        # check for today's folder exist, create it if not
        yy, mm, dd = datetime.today().strftime('%Y-%m-%d').split('-')
        data_folder_today = join(database_folder, f'{yy}\\{mm}\\Data_{mm}{dd}')
        if not isdir(data_folder_today):
            os.makedirs(data_folder_today)
        return data_folder_today
    
    # check if Labber install directory exist
    if not isdir(labber_install_path):
        raise ImportError('Labber is not installed in default directory')

    # create api and measurement client paths
    api_path = join(labber_install_path, 'Script')
    client_path = join(labber_install_path, 'Program', 'Measurement.exe')
    sys.path.append(api_path)
    ScriptTools.setExePath(client_path)
    save_folder = get_datafolder_today(data_save_folder)


    def run_script(save_name: str, override: dict = {}, show_result=False, print_info=True):
        """Run script based on template, override provided settings.

        override has format `{channel_name:{item_type: value}}`.
        The item type: single, start, stop, center, span, step, n_pts.
        See example usage.

        Example usage:
        >>> run_script = get_run_script_func(template_path=template_path)
        >>> override = {
        >>>     # VNA
        >>>     'VNA - Start frequency': {'single': 4e+9},
        >>>     'VNA - Stop frequency': {'single': 5e+9},
        >>>     'VNA - # of points': {'single': 401},
        >>>     # DC
        >>>     'DC supply - 1 - Current': {
        >>>         'start': 2.5e-3,
        >>>         'stop': 7.5e-3,
        >>>         'n_pts': 11,
        >>>     },
        >>>     'DC supply - 2 - Current': {'single': 4e-3}
        >>> }
        >>> save_path = run_script(save_name='save_name', override=override)
        """
        # delete existing file with the same name
        save_path = join(save_folder, save_name + '.hdf5')
        if isfile(save_path):
            os.remove(save_path)
        
        # create measurement object, override if provided
        MeasObj = ScriptTools.MeasurementObject(template_path, save_path)
        if override:
            for master_channel, variable in override.items():
                MeasObj.setMasterChannel(master_channel)
                for name, val in variable.items():
                    MeasObj.updateValue(master_channel, val, itemType=name)

        # start measurement
        if print_info:
            print('>>>', datetime.now().strftime("%Y-%m-%d %H:%M"), end='') 
            print(f', measurement `{save_name}` begins.')
        result = MeasObj.performMeasurement()
        if print_info:
            print('>>>', datetime.now().strftime("%Y-%m-%d %H:%M"), end='') 
            print(f', measurement `{save_name}` ends.')
        if show_result:
            print(result)
        return save_path
    
    return run_script