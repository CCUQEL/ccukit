# ccukit

**Kits for data analysis developed by CCU-QEL members.**

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
```

## sub-modules
`visadriver`: Contains drivers to control visa instruments.
`labberreader`: The labberreader packages. For tools to read labber measured data.
`fittingtool`: Contains formulas, plotting tools, fitting tools to help analyze data.
