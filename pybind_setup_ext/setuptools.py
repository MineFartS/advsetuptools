from setuptools.command.build import (build as _build)
from .utils import is_pkg_installed, shell
from setuptools import (setup as _setup)
from .build_ext import build_ext
from .cpp_ext import cpp_ext
from subprocess import run
from .sphinx import Sphinx
from sys import executable
from shutil import rmtree

__all__ = [
    "setup",
]

class build(_build):

    @staticmethod
    def _pip(*args:str) -> None:
        run(
            [executable, "-m", "pip", *args],
            check = True,
        )

    def initialize_options(self) -> None:
        super().initialize_options()
        if FORCE:
            
            name = self.distribution.get_name()

            for d in ("build", "dist", "_build", "_api", f"{name}.egg-info"):
                rmtree(d, True)
            
            if is_pkg_installed(name):
                self._pip("uninstall", "-y", name)

            self._pip("cache", "purge")
    
    def run(self) -> None:
        super().run()
        Sphinx('.', True).build()

def setup(*ext_modules:cpp_ext):
    return _setup(
        cmdclass = {
            'build_ext': build_ext,
            'build': build,
        },
        ext_modules = list(filter(None, ext_modules)),
    )

