# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of goodies ((cool) scripts / utilities)


## Install

Use *PIP*:

```shell
python -m pip install --upgrade pycfutils
```


## Usage example

```python
import os
import time

import pycfutils.ctypes
import pycfutils.io
import pycfutils.miscellaneous as misc
import pycfutils.network
import pycfutils.system
from pycfutils.exceptions import ModuleException, NetworkException

print("Press a key in less than one second...")
print(pycfutils.io.read_key(timeout=1))

print(pycfutils.ctypes.endianness())

print(misc.timestamp_string(human_readable=True, separator="T", microseconds=True))
print(tuple(misc.progression(ratio=2, count=20)))
print(
    misc.merge_dicts({1: 2}, misc.nest_object((1,), 3)),
    misc.nested_dict_item({1: {2: 3}}, (1, 2)),
)
print(misc.randomize(180, round_result=True))
print(misc.call_stack())
misc.pretty_print(
    tuple(
        misc.process_path_items(
            path="${a_directory_with_few_child_items}",
            processor=lambda arg: os.stat(arg).st_size,
        )
    ),
    head="Path items:",
    tail="",
)


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

# --- REQUIRES PyGObject (python -m pip install PyGObject) ---
# --- Also, might take some time to complete ---
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

#### Functionality to build a *\*.dll* (*\*.so*) with *SetupTools*.

Parts of *setup.py*:

```python
# --- REQUIRES SetupTools (python -m pip install setuptools) for Python >= v3.12 ---
from setuptools import setup

from pycfutils.setup.command.build_clibdll import build_clibdll
from pycfutils.setup.command.install_platlib import install_platlib  # Optional

dll = (
    "dll_name",
    {
        "sources": [
            "src0.c",
            "src1.c",
        ],
        # ...
        "dll": True,  # False (or nothing) for regular (static) library
        "copy_files": {  # Optional (copy artifacts)
            "dll_name.so": "pkg_name",  #  dll_name.dll on Win
        },
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

#### Some useful (*CLI* wrapper) scripts (in the *tools* folder)

Example:

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

    # Go to the other terminal and run the other command (start the server),
    #   then come back and re-run the previous command

    python -m pycfutils.tools.connect_to_server -a 127.0.0.1 -p 16180
    ```

- Terminal 2:

    ```shell
    python -m pycfutils.tools.start_server -a 127.0.0.1 -p 16180
    ```

## Notes

- Package has no (global) dependencies (from outside *Python* standard library).<br>
  However, some of its (niche - more or less) subpackages have their requirements:
    - ***pycfutils.gstreamer***:
        - ***PyGObject*** (`python -m pip install PyGObject`)
    - ***pycfutils.setup.command***:
        - ***SetupTools*** (`python -m pip install setuptools`) for *Python* >= *v3.12*
