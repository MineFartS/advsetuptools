from __future__ import annotations

__all__ = [
    "generate_stubs",
    "InspectionStubGenerator",
    "MonkeyPatch",
]

from mypy.stubdoc import FunctionSig
from mypy import stubgenc as _stubgenc
from os import environ

from mypy.stubutil import (
    ClassInfo,
    FunctionContext,
)

from mypy.stubgenc import (
    InspectionStubGenerator as _InspectionStubGenerator
)

from mypy.stubgen import (
    parse_options,
    generate_stubs as _generate_stubs,
)

def generate_stubs(
    output_dir: str, 
    modules: list[str]
) -> None:
    """Main entry point for the program."""

    options = parse_options([
        '--output', output_dir,
    ])
    options.modules = modules

    environ["STUBGEN"] = "1"
    try:
        _generate_stubs(options)
    finally:
        environ.pop("STUBGEN", None)

class MonkeyPatch:

    def inject() -> None:
        _stubgenc.InspectionStubGenerator = InspectionStubGenerator

    def eject() -> None:
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


