import os

from setuptools.command.install import install


# @TODO - cfati: Use platlib path instead of purelib
class InstallPlatLib(install):
    def finalize_options(self):
        super().finalize_options()
        self.install_libbase = self.install_platlib
        self.install_lib = os.path.join(self.install_libbase, self.extra_dirs)


install_platlib = InstallPlatLib
