from setuptools import (setup as _setup)
from .build_ext import build_ext
from .cpp_ext import cpp_ext
from .sphinx import Sphinx

__all__ = [
    "setup",
]

def setup(*ext_modules:cpp_ext):
    
    dist = _setup(
        cmdclass = {'build_ext': build_ext},
        ext_modules = list(filter(None, ext_modules)),
        script_args = [],
    )
    
    dist.run_command('build_ext')
    
    Sphinx('.', True).build()

    return dist

