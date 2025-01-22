"""The driver to control visa instruments.

Importing example:
>>> from ccukit.visadriver import YOKOGAWA

Python file in this folder should be wrote to have one class only and it is with the same name as filename.
And those classes should be automatically imported when using `import ccukit.labberreader`. Developer should write
>>> from .filename import ClassName
where FileName is the same as ClassName and the capitcal letter convention is applyed on the class definition.


"""

from .yokogawa import YOKOGAWA
from .keysightexg import KeySightEXG