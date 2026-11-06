from setuptools.command.build import (build as _build)
from setuptools import (setup as _setup)
from .build_ext import build_ext
from .cpp_ext import cpp_ext
from .sphinx import Sphinx
from datetime import date

__all__ = [
    "setup",
]

class build(_build):
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
        version = 'v' + date.today().isoformat().replace('-', '.'),
    )

