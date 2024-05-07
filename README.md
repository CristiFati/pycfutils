# *PyCFUtils*

*PyCFUtils* (**C**risti **F**ati's ***Utils*** for ***Py**thon* (&& more)) - a collection of (cool) scripts / utilities


## Install

Use *PIP*:

```shell
python -m pip install --upgrade pycfutils
```


## Usage example

```python
import pycfutils.common
import pycfutils.keyboard

print("Press a key...")
print(pycfutils.keyboard.read_key())
print(pycfutils.common.timestamp_string(human_readable=True))

# --- Windows only ---
import pycfutils.gui

pycfutils.gui.message_box("Title", "Text to display", 200, 200)
```

