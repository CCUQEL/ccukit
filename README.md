# ccukit

**Kits for data analysis and instrument control, developed by CCU-QEL members.**

## Using ccukit

It is recommended to clone the repository onto local device for using it:

```sh
git clone https://github.com/CCUQEL/ccukit.git
```

## Importing Examples

```python
from ccukit import get_path
from ccukit.visadriver import YOKOGAWA
from ccukit.labberreader import VNAXDC
from ccukit.fittingtool import fit_and_plot
```

## sub-modules overview
- `visadriver`: Contains drivers to control visa instruments.
- `labberreader`: Contains tools to read labber measured data.
- `fittingtool`: Contains formulas, plotting tools, fitting tools to help data analysis.

## License

This project is licensed under the [MIT License](LICENSE).


> [!NOTE]  
> The used packages like `numpy`, `scipy`, `maplotlib` etc... should be installed by user manually,
> ccukit doesn't provide the check of the installation and version for those packages.
