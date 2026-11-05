from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

setup(
    install_requires = [
        "setuptools>=74.1",
        "sphinx",
        "ghp-import",
        "mypy @ " + (cwd / "mypy").as_uri(),
        "sphinx-autodoc2 @ " + (cwd / "autodoc2").as_uri(),
    ]
)

