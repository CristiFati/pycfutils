# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of goodies ((cool) scripts / utilities)


## Install

Use *PIP*:

```shell
python -m pip install --upgrade pycfutils
```


## Usage example

```python
import time

import pycfutils.io
import pycfutils.miscellaneous as misc
import pycfutils.network
import pycfutils.system
from pycfutils.exceptions import ModuleException, NetworkException

print("Press a key in less than one second...")
print(pycfutils.io.read_key(timeout=1))

print(misc.timestamp_string(human_readable=True))
print(tuple(misc.progression(ratio=2)))

@misc.timed_execution()
def func(arg0, kw0=1):
    time.sleep(0.2)
    return 5

func("123")

try:
    print(pycfutils.network.connect_to_server("127.0.0.1", 22))
except NetworkException as e:
    print(e)

pycfutils.system.cpu_stress(3)

# --- Requires PyGObject (also might take some time to complete) ---
try:
    from pycfutils.gstreamer import RegistryAccess
except ModuleException as e:
    print(e)
else:
    ra = RegistryAccess()
    print(ra.element_classes())

# --- Windows only ---
import pycfutils.gui

print(pycfutils.gui.message_box("Title", "Text to display", x=320, y=200))
```

#### Functionality to build a *\*.dll* (*\*.so*) with *SetupTools*. Parts of *setup.py*:

```python
from setuptools import setup

from pycfutils.setup.command.build_clibdll import build_clibdll
from pycfutils.setup.command.install_platlib import install_platlib  # Optional

dll = (
    "dll_name",
    {
        "sources": ["src0.c", "src1.c", ],
        # ...
        "dll": True,  # False (or nothing) for regular (static) library
        "copy_files": {  # Optional (copy artifacts)
            "dll_name.so": "pkg_name",  #  dll_name.dll on Win
        }
        # ...
    },
)


setup(
    name="pkg_name",
    # ...
    cmdclass={
        "build_clib": build_clibdll,
        "install": install_platlib,
    },
    libraries=[dll],
    # ...
)
```

#### There are also some useful (*CLI* wrapper) scripts in the *tools* folder. Example:

- *Nix*:

    ```shell
    ls "pycfutils/tools"
    for script in $(find "pycfutils/tools" -maxdepth 1 -type f); do python "${script}" -h; done
    ```

- *Win*:

    ```batchfile
    dir /b "pycfutils\tools"
    for /f %g in ('dir /b /a-d /a-l "pycfutils\tools\*.py"') do (python "pycfutils\tools\%g" -h)
    ```

Or run them as modules (e.g. in 2 separate terminals). Example (*Shell* snippets that also work in *Batch*):

- Terminal 1:

    ```shell
    python -m pycfutils.tools.connect_to_server -a 127.0.0.1 -p 16180

    # Go to the other terminal and run the other command (start the server), then come back and re-run the previous command

    python -m pycfutils.tools.connect_to_server -a 127.0.0.1 -p 16180
    ```

- Terminal 2:

    ```shell
    python -m pycfutils.tools.start_server -a 127.0.0.1 -p 16180
    ```
