from setuptools.command.build_ext import build_ext as __build_ext
from setuptools.extension import Extension
from .mypy.stubgen import generate_stubs
from .utils import sys_path

class build_ext(__build_ext):

    extensions: list[Extension]
    build_lib: str

    def run(self) -> None:
        
        super().run()

        with sys_path(self.build_lib):

            for ext in self.extensions:

                generate_stubs(self.build_lib, [ext.name])

                generate_stubs('.', [ext.name])

