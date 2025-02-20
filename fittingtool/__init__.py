"""Contains formulas, plotting tools, fitting tools to help analyze data.

General tools in `tools.py  will be imported when `import ccukit.fittingtool`.

User importing example:
>>> from ccukit import get_path

Other more specfic tasks are orginized in the submodules:
-- fittingtool: Some of the common fitting formulaes that we use frequently.

Developer should write (in this __init__.py):
>>> from .tools import new_func
"""

from .tools import fit_and_plot, circle_fit, r2_score