from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

setup(
    install_requires = [
        "setuptools>=74.1",
        "pybind11 @ " + (cwd / "pybind11").as_uri(),
        "mypy @ " + (cwd / "mypy").as_uri(),
    ]
)

