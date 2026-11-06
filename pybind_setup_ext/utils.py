from contextlib import contextmanager
from unittest.mock import patch
import sys

__all__ = [
    "patch_sys_path",
]

@contextmanager
def patch_sys_path(path:str):
    with patch.dict(sys.path):
        sys.path.insert(0, path)
        yield

