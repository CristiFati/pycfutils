import os
import shutil
import sys

try:
    from distutils import log
    from distutils.errors import DistutilsSetupError
except ImportError:  # v3.12+
    import setuptools

    log = setuptools.distutils._log
    DistutilsSetupError = setuptools.distutils.errors.DistutilsSetupError

from setuptools.command.build_clib import build_clib

try:
    from setuptools.dep_util import newer_pairwise_group
except ImportError:
    from setuptools.modified import newer_pairwise_group

_IS_WIN = sys.platform[:3].lower() == "win"


class BuildCLibDll(build_clib):

    description = "build C/C++ libraries (static or dynamic) used by other commands"

    dll_ext = ".dll" if _IS_WIN else ".so"

    # @TODO - cfati: Override method from distutils.command.build_clib.build_clib
    # It's actually copy / paste, the differences are:
    #   - `if build_info.get("dll"):` ...
    #   - `for src_base, dst_path in build_info.get("copy_files", {}).items():` ...
    # Would be nicer to refactor directly in distutils / setuptools
    def build_libraries(self, libraries):
        for lib_name, build_info in libraries:
            sources = build_info.get("sources")
            if sources is None or not isinstance(sources, (list, tuple)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'sources' must be present and must be "
                    "a list of source filenames" % lib_name
                )
            sources = sorted(list(sources))

            log.info("building '%s' library", lib_name)

            # Make sure everything is the correct type.
            # obj_deps should be a dictionary of keys as sources
            # and a list/tuple of files that are its dependencies.
            obj_deps = build_info.get("obj_deps", dict())
            if not isinstance(obj_deps, dict):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'obj_deps' must be a dictionary of "
                    "type 'source: list'" % lib_name
                )
            dependencies = []

            # Get the global dependencies that are specified by the '' key.
            # These will go into every source's dependency list.
            global_deps = obj_deps.get("", list())
            if not isinstance(global_deps, (list, tuple)):
                raise DistutilsSetupError(
                    "in 'libraries' option (library '%s'), "
                    "'obj_deps' must be a dictionary of "
                    "type 'source: list'" % lib_name
                )

            # Build the list to be used by newer_pairwise_group
            # each source will be auto-added to its dependencies.
            for source in sources:
                src_deps = [source]
                src_deps.extend(global_deps)
                extra_deps = obj_deps.get(source, list())
                if not isinstance(extra_deps, (list, tuple)):
                    raise DistutilsSetupError(
                        "in 'libraries' option (library '%s'), "
                        "'obj_deps' must be a dictionary of "
                        "type 'source: list'" % lib_name
                    )
                src_deps.extend(extra_deps)
                dependencies.append(src_deps)

            expected_objects = self.compiler.object_filenames(
                sources,
                output_dir=self.build_temp,
            )

            if newer_pairwise_group(dependencies, expected_objects) != ([], []):
                # First, compile the source code to object files in the library
                # directory.  (This should probably change to putting object
                # files in a temporary build directory.)
                macros = build_info.get("macros")
                include_dirs = build_info.get("include_dirs")
                cflags = build_info.get("cflags")
                self.compiler.compile(
                    sources,
                    output_dir=self.build_temp,
                    macros=macros,
                    include_dirs=include_dirs,
                    extra_postargs=cflags,
                    debug=self.debug,
                )
            if build_info.get("dll"):
                lib_full_name = lib_name + self.dll_ext

                self.compiler.link_shared_object(
                    expected_objects,
                    lib_full_name,
                    libraries=build_info.get("libraries"),
                    library_dirs=build_info.get("library_dirs"),
                    runtime_library_dirs=build_info.get("runtime_library_dirs"),
                    extra_postargs=build_info.get("extra_link_args"),
                    export_symbols=build_info.get("export_symbols"),
                    debug=self.debug,
                    build_temp=self.build_temp,
                    target_lang=self.compiler.detect_language(expected_objects),
                    output_dir=self.build_clib,
                )

            else:
                # Now "link" the object files together into a static library.
                # (On Unix at least, this isn't really linking -- it just
                # builds an archive.  Whatever.)
                self.compiler.create_static_lib(
                    expected_objects,
                    lib_name,
                    output_dir=self.build_clib,
                    debug=self.debug,
                )
            build_py_cmd = self.get_finalized_command("build_py", create=False)
            path_prefix = build_py_cmd.build_lib if build_py_cmd else ""
            for src_base, dst_path in build_info.get("copy_files", {}).items():
                src_file = os.path.join(self.build_clib, src_base)
                src = (
                    src_file
                    if os.path.isfile(src_file)
                    else src_base if os.path.isfile(src_base) else ""
                )
                if src:
                    if path_prefix:
                        dst_path = os.path.join(path_prefix, dst_path)
                    os.makedirs(dst_path, exist_ok=True)
                    shutil.copyfile(src, os.path.join(dst_path, os.path.basename(src)))
                else:
                    log.warn(f"{src_base} specified but not found. Skipping")


build_clibdll = BuildCLibDll
