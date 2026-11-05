from setuptools.command.build_ext import build_ext as __build_ext
from setuptools.extension import Extension
from .stubgen import generate_stubs

class build_ext(__build_ext):

    extensions: list[Extension]
    build_lib: str

    def run(self) -> None:
        
        super().run()

        for ext in self.extensions:

            generate_stubs(self.build_lib, [ext.name])

            generate_stubs('.', [ext.name])

