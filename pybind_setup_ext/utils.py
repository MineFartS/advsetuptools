from contextlib import contextmanager
from os.path import abspath
import sys

__all__ = [
    "sys_path",
]

@contextmanager
def sys_path(path:str):
    path = abspath(path)
    try:
        sys.path.insert(0, path)
        yield
    finally:
        sys.path.remove(path)

