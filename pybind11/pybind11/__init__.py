from __future__ import annotations

from os.path import abspath, dirname, join, exists

from ._version import __version__, version_info

DIR = abspath(dirname(__file__))

def get_include() -> str:
    """Return the path to the pybind11 include directory."""
    installed_path = join(DIR, "include")
    source_path = join(dirname(DIR), "include")
    return installed_path if exists(installed_path) else source_path

__all__ = (
    "__version__",
    "get_include",
    "version_info",
    "DIR"
)

