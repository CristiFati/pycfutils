import sys
import threading
import time

from pynput.mouse import Button, Controller

from pycfutils import gui as pg
from pycfutils import io as pio
from pycfutils.gui import effects as pge
from pycfutils.setup.command import build_clibdll as pscbcd


def click(x, y, delay=2):
    time.sleep(delay)
    ctrl = Controller()
    pos = ctrl.position
    ctrl.position = x + 360, y + 120
    ctrl.click(Button.left, 1)
    ctrl.position = pos


if __name__ == "__main__":
    print("Press a key: ", pio.read_key(timeout=1))
    x = 320
    y = 200
    threading.Thread(target=click, args=(x, y)).start()
    print(pg.message_box(f"Message Box ({x}, {y})", sys.version, x=x, y=y))
