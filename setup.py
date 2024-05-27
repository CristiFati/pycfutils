#!/usr/bin/env python

"""
Still using setup.py, as I didn't get up to speed with pyproject.toml,
especially due to the workarounds (some quite lame) done to build the .dll.
"""

import glob
import importlib.util
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist
from setuptools.extension import Library
from wheel.bdist_wheel import bdist_wheel

_IS_WIN = sys.platform[:3].lower() == "win"

_NAME = "pycfutils"

if _IS_WIN:
    _EXT = ".dll"
    _SUF = "win"
else:
    _EXT = ".so"
    _SUF = "nix"

_INCLUDE_DIR = f"include/{_NAME}"
_INCLUDE_FILES = (f"{_INCLUDE_DIR}/cinterface.h",)
_SOURCE_FILES = [
    e.replace("\\", "/")
    for e in glob.glob(os.path.join(_NAME, "src", f"cinterface_*.cpp"))
]
_VS_FILES = tuple(
    f"vs/{e}"
    for e in (
        "vs.vcxproj",
        "vs.vcxproj.filters",
        "vs.sln",
    )
)


def version():
    spec = importlib.util.spec_from_file_location("version", f"{_NAME}/version.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.__version__


# @TODO - cfati (gainarie): Get rid of sysconfig's EXT_SUFFIX (e.g.: .cp310-win_amd64)
class BuildDll(build_ext):
    def get_ext_filename(self, ext_name):
        return os.path.join(*ext_name.split(".")) + _EXT


# @TODO - cfati (gainarie): Create generic .whl as the .dll doesn't depend on Python
class BDistWheelDll(bdist_wheel):
    def get_tag(self):
        if _IS_WIN:
            plat = self.plat_name.replace("-", "_").replace(".", "_").replace(" ", "_")
        else:
            plat = "any"
        return (
            "py3",
            "none",
            plat,
        )


# @TODO - cfati (gainarie): Manually add files in the source distribution (built on Nix)
class SDist(sdist):
    @staticmethod
    def _extra_files():
        ret = ["CHANGELOG"]
        ret.extend(_VS_FILES)
        ret.extend((os.path.join("_utils", e) for e in ("nix.sh", "win.bat")))
        if _IS_WIN:
            return ret
        ret.extend((os.path.join(_NAME, e) for e in _INCLUDE_FILES))
        ret.extend(_SOURCE_FILES)
        return ret

    def _adjust_sources(self):
        ei_cmd = super().get_finalized_command("egg_info")
        manifest = os.path.join(ei_cmd.egg_info, "SOURCES.txt")
        existing = [e.rstrip() for e in open(manifest).readlines()]
        modified = False
        for file in self._extra_files():
            if file not in existing:
                modified = True
                existing.append(file)
        if modified:
            with open(manifest, mode="w") as f:
                f.writelines((f"{e}\n" for e in existing))

    def get_finalized_command(self, command, create=1):
        cmd = super().get_finalized_command(command, create=create)
        extra = self._extra_files()
        if extra:
            cmd.filelist.files.extend(extra)
            self._adjust_sources()
        return cmd


c_interface_dll = Library(
    (_NAME + ".libcinterface"),
    sources=_SOURCE_FILES,
    include_dirs=[f"{_NAME}/include"],
    define_macros=[
        ("UNICODE", None),
        ("_UNICODE", None),
        ("WIN32", None),
        ("_WINDLL", None),
    ],
    extra_link_args=[
        "/DLL",
    ],
    libraries=[
        "user32",
        "kernel32",
    ],
)

setup_args = dict(
    name=_NAME,
    version=version(),
    description="PyCFUtils (Cristi Fati's Utils for Python (&& more)) - "
    "a collection of (cool) scripts / utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Cristi Fati",
    author_email="fati_utcluj@yahoo.com",
    maintainer="Cristi Fati",
    maintainer_email="fati_utcluj@yahoo.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
    ],
    platforms=[
        "All",
    ],
    license="MIT",
    url=f"https://github.com/CristiFati/{_NAME}",
    download_url=f"https://pypi.org/project/{_NAME}",
    packages=find_packages(
        include=(
            f"{_NAME}",
            f"{_NAME}.gstreamer",
            f"{_NAME}.gui",
            f"{_NAME}.tests",
            f"{_NAME}.tools",
        ),
        exclude=("src", "__pycache__"),
    ),
    package_data={
        f"{_NAME}": _INCLUDE_FILES if _IS_WIN else (),
    },
    cmdclass={
        "build_ext": BuildDll,
        "bdist_wheel": BDistWheelDll,
        "sdist": SDist,
    },
    ext_modules=[c_interface_dll] if _IS_WIN else [],
)

setup(**setup_args)
