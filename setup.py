from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

def embed(name:str) -> str:
    return name + " @ " + (cwd / name).as_uri()

setup(
    install_requires = [
        "setuptools==84.2.1",
        "ghp-import==2.1.0",
        "mypy==2.4.1",
        "sphinx==9.1.1",
        embed("sphinx-autodoc2"),
    ]
)

