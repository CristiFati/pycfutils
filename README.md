# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of (cool) scripts / utilities


## Install

Use *PIP*:

```shell
python -m pip install --upgrade pycfutils
```


## Usage example

```python
import pycfutils.io
import pycfutils.miscellaneous as misc
import pycfutils.network
from pycfutils.exceptions import NetworkException

print("Press a key in less than one second...")
print(pycfutils.io.read_key(timeout=1))
print(misc.timestamp_string(human_readable=True))
try:
    print(pycfutils.network.connect_to_server("127.0.0.1", 22))
except NetworkException as e:
    print(e)

# --- Windows only ---
import pycfutils.gui

print(pycfutils.gui.message_box("Title", "Text to display", x=320, y=200))

# --- Requires PyGObject (also might take some time to complete) ---
from pycfutils.gstreamer import RegistryAccess

ra = RegistryAccess()
print(ra.element_classes())
```

