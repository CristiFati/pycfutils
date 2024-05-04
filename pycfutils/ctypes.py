
# CTypes utilities script by (pussious) cfati

import ctypes as cts
import sys

try:
    _CLS_CDATA = cts.c_int.__mro__[-2]
except:
    _CLS_CDATA = None


def _to_string(obj, indent, head, tail, indent_text, indent_first_line):
    cls = obj.__class__
    ret = [""] if head else []
    ret.append("{:s}{:s}".format((indent_text * indent) if indent_first_line else "", str(obj)))
    if _CLS_CDATA is None or not issubclass(cls, _CLS_CDATA):
        if tail:
            ret.append("")
        return "\n".join(ret)
    if issubclass(cls, (cts.Structure, cts.Union)):
        for name, _ in obj._fields_:
            ret.append("{:s}{:s}: {:s}".format(
                indent_text * (indent + 1), name,
                _to_string(
                    obj=getattr(obj, name), indent=indent + 1, head=False, tail=False, indent_text=indent_text,
                    indent_first_line=False)))
    elif issubclass(cls, cts.Array):
        for e in obj:
            ret.append(_to_string(obj=e, indent=indent + 1, head=False, tail=False,
                                  indent_text=indent_text, indent_first_line=True))
    elif issubclass(cls, cts._Pointer):
        if obj:
            ret.append(_to_string(obj=obj.contents, indent=indent + 1, head=head, tail=tail,
                                  indent_text=indent_text, indent_first_line=True))
    if tail:
        ret.append("")
    return "\n".join(ret)


def to_string(obj, indent=0, head=True, tail=True, indent_text="  "):
    return _to_string(obj=obj, indent=indent, head=head, tail=tail, indent_text=indent_text, indent_first_line=True)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

