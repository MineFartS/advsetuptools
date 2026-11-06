from contextlib import contextmanager
from unittest.mock import patch
import sys

__all__ = [
    "at_path",
]

@contextmanager
def at_path(path:str):
    with patch.dict(sys.path):
        sys.path.insert(0, path)
        yield

