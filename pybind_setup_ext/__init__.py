
from .git import update_submodule
from .build.build_ext import build_ext
from .build.cpp_ext import cpp_ext
import setuptools as st

from .build.cpp_ext import (
    _extra_compile_args as extra_compile_args,
    _extra_objects as extra_objects,
    _include_dirs as include_dirs,
    _extra_link_args as extra_link_args,
)

__all__ = [
    "cpp_ext", "setup", "update_submodule", 
    "extra_compile_args", "extra_objects", "include_dirs",
    "extra_link_args"
]

def setup(*ext_modules:cpp_ext) -> None:
    st.setup(
        cmdclass = {'build_ext': build_ext},
        ext_modules = list(filter(None, ext_modules)),
    )
    from .build import sphinx # Run sphinx.py
    from .build import ghp_import # Run ghp_import.py

