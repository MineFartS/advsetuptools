from contextlib import contextmanager, chdir
from importlib import (metadata as md)
from subprocess import check_call
from unittest.mock import patch
from sys import executable
import sys

__all__ = [
    "at_path",
    "is_pkg_installed",
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

class shell:

    @staticmethod
    def pip(*args: str) -> None:
        check_call([executable, "-m", "pip", *args])

    @staticmethod
    def git(*args: str) -> None:
        check_call(['git', *args])

    @staticmethod
    def sphinx(*args:str) -> None:
        from sphinx.cmd.quickstart import main
        result = main(args)
        if result != 0:
            raise RuntimeError(f'{result=}')

