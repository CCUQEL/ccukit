# ccukit

**Kits for data analysis and instrument control, developed by CCU-QEL members.**

## Using ccukit

It is recommended to clone the repository or download as zip onto local device for using it:

```sh
git clone https://github.com/CCUQEL/ccukit.git
```


## Importing Examples

```python
import sys
sys.path.insert(0, 'c:\\Users\\QEL\\Desktop\\py') # add path of where ccukit located
from ccukit import get_path
from ccukit.visadriver import YOKOGAWA
from ccukit.labberreader import VNAxDC
from ccukit.fittingtool import fit_and_plot
```
It is recommaned to have the workspace contains the folder of ccukit to see its docstring. For example,
the workspace we used is `c:\Users\QEL\Desktop\py`, we use VScode to open this folder and use it.


## sub-modules overview
- `visadriver`: Contains drivers to control visa instruments.
- `labberreader`: Contains tools to read Labber measured data.
- `fittingtool`: Contains formulas, plotting tools, fitting tools to help data analysis.

## License

This project is licensed under the [MIT License](LICENSE).


> [!NOTE]  
> The used packages like `numpy`, `scipy`, `maplotlib` etc... should be installed by user manually,
> ccukit doesn't provide the check of the installation and version for those packages.
