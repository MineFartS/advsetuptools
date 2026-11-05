from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

setup(
    install_requires = [
        "sphinx",
        "ghp-import",
        "sphinx-autodoc2 @ " + (cwd / "autodoc2").as_uri(),
    ]
)

