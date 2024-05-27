# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of goodies ((cool) scripts / utilities)


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
import pycfutils.system
from pycfutils.exceptions import NetworkException

print("Press a key in less than one second...")
print(pycfutils.io.read_key(timeout=1))
print(misc.timestamp_string(human_readable=True))
try:
    print(pycfutils.network.connect_to_server("127.0.0.1", 22))
except NetworkException as e:
    print(e)
pycfutils.system.cpu_stress(3)

# --- Windows only ---
import pycfutils.gui

print(pycfutils.gui.message_box("Title", "Text to display", x=320, y=200))

# --- Requires PyGObject (also might take some time to complete) ---
from pycfutils.gstreamer import RegistryAccess

ra = RegistryAccess()
print(ra.element_classes())
```

Also, there are some useful (CLI wrapper) scripts **in the *tools* folder**. 

- *Nix*:

    ```lang-bash
    for script in $(find "pycfutils/tools" -maxdepth 1 -type f); do python "${script}" -h; done
    ```

- *Win*:

    ```lang-bat
    for /f %g in ('dir /b /a-d /a-l "pycfutils\tools\*.py"') do (python "pycfutils\tools\%g" -h)
    ```
