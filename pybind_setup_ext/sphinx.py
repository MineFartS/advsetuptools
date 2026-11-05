from sphinx.application import Sphinx as _Sphinx
from ghp_import import ghp_import
from datetime import datetime
from os.path import abspath
from pathlib import Path
import tomllib as toml
import sys

__all__ = [
    "shell", "Sphinx",
]

def shell(*args:str) -> None:
    from sphinx.cmd.quickstart import main
    result = main(args)
    if result != 0:
        raise RuntimeError(f'{result=}')

class Sphinx(_Sphinx):

    @staticmethod
    def init():

        #==============================================
        # Sphinx

        with open("pyproject.toml", "rb") as f:
            project = toml.load(f)['project']

        args = ['=q']

        args += '-p', project['name']
        args += '-v', project['version']

        args += "--no-sep", '.'

        shell(*args)

        #==============================================
        # Git Ignore

        with open(".gitignore", "a") as f:
            f.write(f"_build\n")
            f.write(f"_api\n")

        #==============================================

        return Sphinx(".")

    def __init__(self,
        srcdir: str,
        freshenv: bool = False,
    ): super().__init__(
        srcdir = srcdir,
        confdir = srcdir,
        outdir = "_build/html",
        doctreedir = "_build/doctrees",
        buildername = "html",
        freshenv = freshenv,
    )

    def build(s) -> None:

        # Safely modify the runtime sys.path
        sys.path.insert(0, abspath("."))

        # Mutate existing configuration variables from conf.py
        s.config.copyright = f'{datetime.now().year}, {s.config.author}'

        # Ensure lists are cleanly extended
        s.config.exclude_patterns += ['_build', 'Thumbs.db', '.DS_Store']
        s.config.extensions += ["autodoc2", "sphinx.ext.viewcode"]

        # Inject your dynamic autodoc2 configurations
        s.config.autodoc2_packages = [s.config.project]
        s.config.autodoc2_output_dir = "_api"
        s.config.autodoc2_render_plugin = "rst"

        s.config.autodoc_mock_imports = [
            ".".join(pyi_path.with_suffix("").parts)
            for pyi_path in Path(s.config.project).rglob("*.pyi") 
        ]

        super().build()

    def upload(self) -> None:
        ghp_import(
            srcdir = self.outdir,
            nojekyll = True,
            push = True,
            force = True
        )

#======================================================================

