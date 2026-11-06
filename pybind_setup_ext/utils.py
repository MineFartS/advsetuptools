from contextlib import contextmanager, chdir
from importlib import (metadata as md)
from unittest.mock import patch
import sys

__all__ = [
    "at_path",
    "is_pkg_installed",
    "shell",
]

@contextmanager
def at_path(path:str):
    with patch.object(sys, "path", sys.path.copy()):
        sys.path.insert(0, path)
        with chdir(path):
            yield

def is_pkg_installed(name:str) -> bool:
    try:
        md.version(name)
        return True
    except md.PackageNotFoundError:
        return False

