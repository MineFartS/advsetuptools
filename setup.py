from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

setup(
    install_requires = [
        "setuptools>=74.1",
        "mypy @ " + (cwd / "mypy").as_uri(),
        "auto-python-docs @ " + (cwd / "auto-python-docs").as_uri(),
    ]
)

