"""kits for data analysis wrote for CCU, by Neuro sama :).

General tools in `general.py  will be imported when `import ccukit`.

User importing example:
>>> from ccukit import get_path

Other more specfic tasks are orginized in the submodules:
-- fittingtool: Fitting tools, include common fitting formulas.
-- labberreader: The labberreader packages. For tools to read labber measured data.
-- visadriver: The driver to control visa instruments.

Developer should write (in this __init__.py):
>>> from .general import new_func
"""

from .general import get_path, plot_trace, set_plot_style, save_to_csv, get_run_script_func