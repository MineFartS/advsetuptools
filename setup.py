from setuptools import setup
from pathlib import Path

cwd = Path(__file__).resolve().parent

def embed(name:str) -> str:
    return name + " @ " + (cwd / name).as_uri()

setup(
    install_requires = [
        "setuptools>=74.1",
        "ghp-import",
        "typing_extensions>=4.6.0; python_version<'3.15'",
        "typing_extensions>=4.14.0; python_version>='3.15'",
        "mypy_extensions>=1.0.0",
        "pathspec>=1.0.0",
        "tomli>=1.1.0; python_version<'3.11'",
        "librt>=0.16.0; platform_python_implementation != 'PyPy'",
        "ast-serialize>=0.12.1,<1.0.0",
        "mypy>=2.4.1",
        embed("sphinx"),
        embed("sphinx-autodoc2"),
    ]
)

