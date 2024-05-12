# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of (cool) scripts / utilities


## Install

Use *PIP*:

```shell
python -m pip install --upgrade pycfutils
```


## Usage example

```python
import pycfutils.miscellaneous as misc
import pycfutils.keyboard

print("Press a key in less than one second...")
print(pycfutils.keyboard.read_key(timeout=1))
print(misc.timestamp_string(human_readable=True))

# --- Windows only ---
import pycfutils.gui

print(pycfutils.gui.message_box("Title", "Text to display", x=320, y=200))

# --- Requires PyGObject (also might take some time to complete) ---
from pycfutils.gstreamer import RegistryAccess

ra = RegistryAccess()
print(ra.element_classes())
```

