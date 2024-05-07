import ctypes as cts
import sys
from typing import Any, Optional

cts.c_bool = 1
try:
    _CLS_CDATA = cts.c_int.__mro__[-2]
except Exception:
    _CLS_CDATA = None


__all__ = ("to_string",)


def _to_string(
    obj: Any,
    indent: int,
    prefix: Optional[str],
    suffix: Optional[str],
    indent_text: str,
    indent_first_line: bool,
) -> str:
    cls = obj.__class__
    ret = [prefix] if prefix is not None else []
    ret.append(f"{(indent_text * indent) if indent_first_line else '':s}{obj}")
    if _CLS_CDATA is None or not issubclass(cls, _CLS_CDATA):
        if suffix is not None:
            ret.append(suffix)
        return "\n".join(ret)
    if issubclass(cls, (cts.Structure, cts.Union)):
        for name, _ in obj._fields_:
            ret.append(
                "{:s}{:s}: {:s}".format(
                    indent_text * (indent + 1),
                    name,
                    _to_string(
                        obj=getattr(obj, name),
                        indent=indent + 1,
                        prefix=None,
                        suffix=None,
                        indent_text=indent_text,
                        indent_first_line=False,
                    ),
                )
            )
    elif issubclass(cls, cts.Array):
        for e in obj:
            ret.append(
                _to_string(
                    obj=e,
                    indent=indent + 1,
                    prefix=None,
                    suffix=None,
                    indent_text=indent_text,
                    indent_first_line=True,
                )
            )
    elif issubclass(cls, cts._Pointer):
        if obj:
            ret.append(
                _to_string(
                    obj=obj.contents,
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
    obj: Any,
    indent: int = 0,
    prefix: Optional[str] = "",
    suffix: Optional[str] = "",
    indent_text: str = "  ",
) -> str:
    return _to_string(
        obj=obj,
        indent=indent,
        prefix=prefix,
        suffix=suffix,
        indent_text=indent_text,
        indent_first_line=True,
    )


if _CLS_CDATA:
    __all__ += (
        "Structure",
        "Union",
        # "Array",
        "BigEndianStructure",
        "LittleEndianStructure",
    )

    class Structure(cts.Structure):
        to_string = to_string

    class Union(cts.Union):
        to_string = to_string

    #    class Array(cts.Array):
    #        to_string = to_string

    class BigEndianStructure(cts.BigEndianStructure):
        to_string = to_string

    class LittleEndianStructure(cts.LittleEndianStructure):
        to_string = to_string


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
