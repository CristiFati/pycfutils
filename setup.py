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
from setuptools.command.sdist import sdist as sdist_orig
from wheel.bdist_wheel import bdist_wheel as bdist_wheel_orig

from pycfutils.setup.command.build_clibdll import build_clibdll
from pycfutils.setup.command.install_platlib import install_platlib

plat = sys.platform.lower()
_IS_WIN = plat == "win32"

_NAME = "pycfutils"
_CINTERFACE = "cinterface"

if _IS_WIN:
    _EXT = ".dll"
    _SUF = "win"
    _CINTERFACE_OUT_DLL_FILE_STEM = "hopa"
else:
    _EXT = ".so"
    _SUF = "nix"
    _CINTERFACE_OUT_DLL_FILE_STEM = f"lib{_CINTERFACE}"

_INCLUDE_DIR = f"include/{_NAME}"
_INCLUDE_FILES = (f"{_INCLUDE_DIR}/{_CINTERFACE}.h",)
_SOURCE_FILES = [
    e.replace("\\", "/")
    for e in glob.glob(os.path.join(_NAME, "src", f"{_CINTERFACE}*.cpp"))
]
_CINTERFACE_DLL_FILE_BASE = f"{_CINTERFACE_OUT_DLL_FILE_STEM}{_EXT}"
_CINTERFACE_DLL_FILE = _CINTERFACE_DLL_FILE_BASE
_CINTERFACE_OUT_LIB_FILE_STEM = f"lib{_CINTERFACE}"
_CINTERFACE_LIB_FILE_BASE = f"{_CINTERFACE_OUT_LIB_FILE_STEM}.lib"
_LIBS_DIR = "libs"
_CINTERFACE_LIB_FILE = f"{_LIBS_DIR}/{_CINTERFACE_LIB_FILE_BASE}"
_VS_FILES = tuple(
    f"vs/{e}"
    for e in (
        "vs.vcxproj",
        "vs.vcxproj.filters",
        "vs.sln",
    )
)
_TOOL_FILES = tuple(f"_utils/{e}" for e in ("nix.sh", "win.bat"))
_OTHER_FILES = ("release_branch.sh",)


def version():
    spec = importlib.util.spec_from_file_location("version", f"{_NAME}/version.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.__version__


# @TODO - cfati (gainarie): Create generic .whl as the .dll doesn't depend on Python
class BDistWheelDll(bdist_wheel_orig):
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
class SDist(sdist_orig):
    @staticmethod
    def _extra_files():
        ret = ["CHANGELOG"]
        ret.extend(f"{_NAME}/{e}" for e in _INCLUDE_FILES)
        ret.extend(_SOURCE_FILES)
        ret.extend(_VS_FILES)
        ret.extend(_TOOL_FILES)
        ret.extend(_OTHER_FILES)
        return ret

    def _adjust_sources(self, extra_files):
        ei_cmd = super().get_finalized_command("egg_info")
        manifest = os.path.join(ei_cmd.egg_info, "SOURCES.txt")
        existing = [e.rstrip() for e in open(manifest).readlines()]
        modified = False
        for file in extra_files:
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
            self._adjust_sources(extra)
        return cmd


bdist_wheel_dll = BDistWheelDll
sdist = SDist


c_interface_dll = (
    _CINTERFACE_OUT_DLL_FILE_STEM,
    {
        "dll": True,
        "copy_files": (
            {
                _CINTERFACE_DLL_FILE_BASE: _NAME,
                _CINTERFACE_LIB_FILE_BASE: f"{_NAME}/{_LIBS_DIR}",
            }
            if _IS_WIN
            else {
                _CINTERFACE_DLL_FILE_BASE: _NAME,
            }
        ),
        "sources": _SOURCE_FILES,
        "include_dirs": (f"{_NAME}/include",),
        "define_macros": (
            ("UNICODE", None),
            ("_UNICODE", None),
            ("WIN32", None),
            ("_WINDLL", None),
        ),
        "libraries": ("user32",),
        "extra_link_args": (f"/IMPLIB:{_CINTERFACE_LIB_FILE_BASE}",),
    },
)


setup_args = dict(
    name=_NAME,
    version=version(),
    description="PyCFUtils (Cristi Fati's Utils for Python (&& more)) - "
    "a collection of goodies ((cool) scripts / utilities)",
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
        "Topic :: Utilities",
    ],
    platforms=[
        "All",
    ],
    license="MIT",
    url=f"https://github.com/CristiFati/{_NAME}",
    download_url=f"https://pypi.org/project/{_NAME}",
    packages=find_packages(
        include=(
            _NAME,
            f"{_NAME}.gstreamer",
            f"{_NAME}.gui",
            f"{_NAME}.gui._win",
            f"{_NAME}.gui.effects",
            f"{_NAME}.setup",
            f"{_NAME}.setup.command",
            f"{_NAME}.tests",
            f"{_NAME}.tools",
        ),
        exclude=("src", "__pycache__"),
    ),
    package_data={_NAME: _INCLUDE_FILES} if _IS_WIN else {},
    cmdclass=(
        {
            "build_clib": build_clibdll,
            "install": install_platlib,
            "bdist_wheel": bdist_wheel_dll,
            "sdist": sdist,
        }
        if _IS_WIN
        else {
            "sdist": sdist,
        }
    ),
    libraries=[c_interface_dll] if _IS_WIN else [],
)

setup(**setup_args)
