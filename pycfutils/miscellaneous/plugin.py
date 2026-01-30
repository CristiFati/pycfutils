import inspect
import pathlib
import sys
from importlib.util import module_from_spec, spec_from_file_location
from typing import Tuple

from pycfutils import common, miscellaneous

_self_path = pathlib.Path(__file__).parent.absolute()


class BasePlugin:
    @classmethod
    def id(cls) -> str:
        return "".join((__name__, cls.__name__))

    @classmethod
    def type(cls) -> str:
        return cls.__name__

    @classmethod
    def _filter_plugin(cls, item) -> bool:
        return (
            item is not cls
            and issubclass(item.__class__, type)
            and issubclass(item, cls)
        )

    @classmethod
    def _load_file(
        cls,
        entry: common.PathLike,
        name_filter_function: common.StringFilter,
        item_filter_function: common.GenericFilter,
    ) -> common.GenericTuple:
        spec = spec_from_file_location(entry.stem, entry)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)

        return miscellaneous.object_items(
            mod,
            name_filter_function=name_filter_function,
            item_filter_function=lambda arg: mod.__name__
            == getattr(arg, "__module__", None)
            and cls._filter_plugin(arg)
            and not inspect.isabstract(arg)
            and item_filter_function(arg),
            modules_only=True,
        )

    @classmethod
    def load(
        cls,
        location: common.PathLike,
        recursive: bool = False,
        filesystem_filter_function: common.PathFilter = lambda arg: True,
        name_filter_function: common.StringFilter = lambda arg: True,
        item_filter_function: common.GenericFilter = lambda arg: True,
    ) -> Tuple["BasePlugin", ...]:
        ret = []
        path = pathlib.Path(location)
        if path.is_file():
            if path.absolute() == _self_path:
                return ()
            try:
                return tuple(
                    cls._load_file(path, name_filter_function, item_filter_function)
                )
            except:
                return ()
        glob_func = path.rglob if recursive else path.glob
        for entry in glob_func("*"):
            if not filesystem_filter_function(entry) or entry.absolute() == _self_path:
                continue
            try:
                ret.extend(
                    cls._load_file(entry, name_filter_function, item_filter_function)
                )
            except:
                pass
        return tuple(ret)


__all__ = ("BasePlugin",)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)
