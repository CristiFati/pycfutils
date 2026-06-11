# PyCFUtils

[![PyPI version](https://img.shields.io/pypi/v/pycfutils)](https://pypi.org/project/pycfutils/)
[![Python versions](https://img.shields.io/pypi/pyversions/pycfutils)](https://pypi.org/project/pycfutils/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**PyCFUtils** (**C**risti **F**ati's **Utils** for **Py**thon (&& more)) is a cross-platform collection of utility modules covering IO, networking, system operations, ctypes helpers, GUI wrappers (Windows), and SetupTools extensions for building native libraries. It has no global dependencies outside the Python standard library.

## Install

```shell
python -m pip install --upgrade pycfutils
```

## Usage

### IO

```python
import pycfutils.io

print("Press a key in less than one second...")
print(pycfutils.io.read_key(timeout=1))
```

### CTypes

```python
import pycfutils.ctypes

print(pycfutils.ctypes.endianness())
```

### Miscellaneous utilities

```python
import pycfutils.miscellaneous as misc

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
            processor=lambda arg: __import__("os").stat(arg).st_size,
        )
    ),
    head="Path items:",
    tail="",
)
```

### Timed execution decorator

```python
import time

import pycfutils.miscellaneous as misc


@misc.timed_execution()
def func(arg0, kw0=1):
    time.sleep(0.2)
    return 5


func("123")
```

### Networking

```python
import pycfutils.network
from pycfutils.exceptions import NetworkException

try:
    print(pycfutils.network.connect_to_server("127.0.0.1", 22))
except NetworkException as e:
    print(e)
```

### System

```python
import pycfutils.system

pycfutils.system.cpu_stress(3)
```

### GUI (Windows only)

```python
import pycfutils.gui

print(pycfutils.gui.message_box("Title", "Text to display", x=320, y=200))
```

### Building a native library (.dll / .so) with SetupTools

Parts of `setup.py`:

```python
# Requires SetupTools (python -m pip install setuptools) for Python >= 3.12
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
            "dll_name.so": "pkg_name",  # dll_name.dll on Win
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

### CLI tools

The `tools` folder contains CLI wrapper scripts. To list them and view their help:

Unix:

```shell
ls "pycfutils/tools"
for script in $(find "pycfutils/tools" -maxdepth 1 -type f); do python "${script}" -h; done
```

Windows:

```batch
dir /b "pycfutils\tools"
for /f %g in ('dir /b /a-d /a-l "pycfutils\tools\*.py"') do (python "pycfutils\tools\%g" -h)
```

They can also be run as modules. For example, in two separate terminals:

Terminal 1:

```shell
python -m pycfutils.tools.connect_to_server -a 127.0.0.1 -p 16180

# Go to Terminal 2 and start the server, then come back and re-run:

python -m pycfutils.tools.connect_to_server -a 127.0.0.1 -p 16180
```

Terminal 2:

```shell
python -m pycfutils.tools.start_server -a 127.0.0.1 -p 16180
```

## Notes

- The package has no global dependencies outside the Python standard library.
  However, some subpackages have their own requirements:
    - **pycfutils.setup.command**: requires [SetupTools](https://pypi.org/project/setuptools/) (`python -m pip install setuptools`) for Python >= 3.12

## Changelog

See [CHANGELOG](CHANGELOG) for a full list of changes.

## Contributing

Contributions are welcome. Please open an issue or submit a pull request on [GitHub](https://github.com/CristiFati/pycfutils).

## License

This project is licensed under the [MIT License](LICENSE).
