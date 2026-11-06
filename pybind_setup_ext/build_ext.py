from setuptools.command.build_ext import (build_ext as __build_ext)
from mypy.stubgen import (generate_stubs as _generate_stubs)
from mypy.stubgenc import (InspectionStubGenerator as _ISG)
from mypy.stubutil import ClassInfo, FunctionContext
from setuptools.extension import Extension
from mypy import (stubgenc as _stubgenc)
from mypy.stubgen import parse_options
from mypy.stubdoc import FunctionSig
from .utils import patch_sys_path
from os import environ

__all__ = [
    "build_ext",
]

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

        _stubgenc.InspectionStubGenerator = ISG

        environ["STUBGEN"] = "1"
        try:
            with patch_sys_path(output_dir):
                _generate_stubs(parse_options([
                    '--output', output_dir,
                    '--module', module,
                    '--inspect-mode',
                    '--include-private',
                ]))
        finally:
            environ.pop("STUBGEN", None)
            _stubgenc.InspectionStubGenerator = _ISG

class ISG(_ISG):

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

