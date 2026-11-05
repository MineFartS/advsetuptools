from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

def embed(name:str) -> str:
    return name + " @ " + (cwd / name).as_uri()

setup(
    install_requires = [
        "setuptools>=74.1",
        "ghp-import",
        "mypy==2.4.1",
        embed("sphinx"),
        embed("sphinx-autodoc2"),
    ]
)

