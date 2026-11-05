from setuptools.command.build_ext import build_ext as __build_ext
from ..mypy.stubgen import generate_stubs
from os.path import abspath
import sys

class build_ext(__build_ext):
    def run(self) -> None:
        
        super().run()

        sys.path.insert(0, abspath(self.build_lib))

        for ext in self.extensions:

            generate_stubs(self.build_lib, [ext.name])

            generate_stubs('.', [ext.name])

