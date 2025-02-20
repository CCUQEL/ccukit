"""The labberreader packages. For tools to read labber measured data.

Importing example:
>>> from ccukit.labberreader import VNAxDC

Expect `core.py`, other python file should be wrote to have one class only and it is with the same name as filename.
And those classes should be automatically imported when using `import ccukit.labberreader`. Developer should write
>>> from .filename import ClassName
where FileName is the same as ClassName and the capitcal letter convention is applyed on the class definition.



"""

from .vnaxdc import VNAxDC