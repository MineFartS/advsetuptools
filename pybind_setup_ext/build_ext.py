from __future__ import annotations

__all__ = [
    "build_ext",
    "InspectionStubGenerator",
]

from setuptools.command.build_ext import build_ext as __build_ext
from mypy.stubgen import (main as _generate_stubs)
from setuptools.extension import Extension
from mypy import stubgenc as _stubgenc
from mypy.stubdoc import FunctionSig
from contextlib import chdir
from os import environ

from mypy.stubutil import (
    ClassInfo,
    FunctionContext,
)

from mypy.stubgenc import (
    InspectionStubGenerator as _InspectionStubGenerator
)


class build_ext(__build_ext):

    extensions: list[Extension]
    build_lib: str

    def run(self) -> None:
        
        super().run()

        for ext in self.extensions:

            self.generate_stubs(self.build_lib, ext.name)

            self.generate_stubs('.', ext.name)

    @staticmethod
    def generate_stubs(
        output_dir: str, 
        module: str
    ) -> None:

        _stubgenc.InspectionStubGenerator = InspectionStubGenerator

        environ["STUBGEN"] = "1"
        try:
            with chdir(output_dir):
                _generate_stubs([
                    '--output', output_dir,
                    '--module', module,
                ])
        finally:
            environ.pop("STUBGEN", None)
            _stubgenc.InspectionStubGenerator = _InspectionStubGenerator


class InspectionStubGenerator(_InspectionStubGenerator):
    """Stub generator that does not parse code.

    Generation is performed by inspecting the module's contents, and thus works
    for highly dynamic modules, pyc files, and C modules (via the CStubGenerator
    subclass).
    """

    def get_default_function_sig(self, func: object, ctx: FunctionContext) -> FunctionSig:
        
        if self.is_cached_property(func):
            func = func.func

        return super().get_default_function_sig(func, ctx)

    def is_skipped_attribute(self, attr: str) -> bool:
        return (
            super().is_skipped_attribute(attr)
            or attr in (
                "_pybind11_conduit_v1_",
                "__pybind11_native_enum__",
            )
        )

    @staticmethod
    def is_cached_property(obj: object) -> bool:
        return type(obj).__name__ == "cached_property"

    @classmethod
    def is_property(cls, class_info: ClassInfo, name: str, obj: object) -> bool:
        return (
            super().is_property(class_info, name)
            or cls.is_cached_property(obj)
        )

    @classmethod
    def is_property_readonly(cls, prop: object) -> bool:
        return (
            super().is_property_readonly(prop)
            or cls.is_cached_property(prop)
        )

    def generate_property_stub(
        self,
        name: str,
        raw_obj: object,
        obj: object,
        static_properties: list[str],
        rw_properties: list[str],
        ro_properties: list[str],
        class_info: ClassInfo | None = None,
    ) -> None:

        initial_size = len(ro_properties)

        super().generate_property_stub(
            name, raw_obj, obj, 
            static_properties,
            rw_properties,
            ro_properties,
            class_info,
        )

        if (self.is_cached_property(raw_obj) 
            and len(ro_properties) > initial_size
            and "@property" in ro_properties[-1]
        ):
            self.import_tracker.add_import_from("functools", [("cached_property", None)])
            ro_properties[-1] = ro_properties[-1].replace("@property", "@cached_property")


