from contextlib import contextmanager, chdir
from unittest.mock import patch
import sys

__all__ = [
    "at_path",
]

@contextmanager
def at_path(path:str):
    with patch.object(sys, "path", sys.path.copy()):
        sys.path.insert(0, path)
        with chdir(path):
            yield

