import ctypes
import enum
import sys
from typing import Any, Optional

try:
    _CLS_CDATA = ctypes.c_int.__mro__[-2]
except Exception:
    _CLS_CDATA = None


class Endian(enum.IntEnum):
    UNKNOWN = 0
    BIG = 1
    LITTLE = 2


def endianness() -> "Endian":

    class _U(ctypes.Union):
        _fields_ = (
            ("b4", ctypes.c_uint8 * 4),
            ("dw", ctypes.c_uint32),
        )

    u = _U()
    u.dw = 0x00010203
    if u.b4[0] == 0x00 and u.b4[1] == 0x01 and u.b4[2] == 0x02 and u.b4[3] == 0x03:
        return Endian.BIG
    elif u.b4[0] == 0x03 and u.b4[1] == 0x02 and u.b4[2] == 0x01 and u.b4[3] == 0x00:
        return Endian.LITTLE
    return Endian.UNKNOWN


def _to_string(
    c_object: Any,
    indent: int,
    prefix: Optional[str],
    suffix: Optional[str],
    indent_text: str,
    indent_first_line: bool,
) -> str:
    cls = c_object.__class__
    ret = [prefix] if prefix is not None else []
    ret.append(f"{(indent_text * indent) if indent_first_line else '':s}{c_object}")
    if _CLS_CDATA is None or not issubclass(cls, _CLS_CDATA):
        if suffix is not None:
            ret.append(suffix)
        return "\n".join(ret)
    if issubclass(cls, (ctypes.Structure, ctypes.Union)):
        for name, _ in c_object._fields_:
            ret.append(
                "{:s}{:s}: {:s}".format(
                    indent_text * (indent + 1),
                    name,
                    _to_string(
                        c_object=getattr(c_object, name),
                        indent=indent + 1,
                        prefix=None,
                        suffix=None,
                        indent_text=indent_text,
                        indent_first_line=False,
                    ),
                )
            )
    elif issubclass(cls, ctypes.Array):
        for e in c_object:
            ret.append(
                _to_string(
                    c_object=e,
                    indent=indent + 1,
                    prefix=None,
                    suffix=None,
                    indent_text=indent_text,
                    indent_first_line=True,
                )
            )
    elif issubclass(cls, ctypes._Pointer):
        if c_object:
            ret.append(
                _to_string(
                    c_object=c_object.contents,
                    indent=indent + 1,
                    prefix=prefix,
                    suffix=suffix,
                    indent_text=indent_text,
                    indent_first_line=True,
                )
            )
    if suffix is not None:
        ret.append(suffix)
    return "\n".join(ret)


def to_string(
    c_object: Any,
    indent: int = 0,
    prefix: Optional[str] = "",
    suffix: Optional[str] = "",
    indent_text: str = "  ",
) -> str:
    return _to_string(
        c_object=c_object,
        indent=indent,
        prefix=prefix,
        suffix=suffix,
        indent_text=indent_text,
        indent_first_line=True,
    )


if _CLS_CDATA:

    class Structure(ctypes.Structure):
        to_string = to_string

    class Union(ctypes.Union):
        to_string = to_string

    #    class Array(cts.Array):
    #        to_string = to_string

    class BigEndianStructure(ctypes.BigEndianStructure):
        to_string = to_string

    class LittleEndianStructure(ctypes.LittleEndianStructure):
        to_string = to_string

    __all__ = (
        # "Array",
        "BigEndianStructure",
        "LittleEndianStructure",
        "Structure",
        "Union",
    )
else:
    __all__ = ()

__all__ += ("to_string",)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
