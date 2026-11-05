from __future__ import annotations

__all__ = [
    "InspectionStubGenerator",
    "is_cached_property",
    "MonkeyPatch",
]

from collections.abc import Mapping
from typing import Any

from mypy.stubdoc import ArgSig, FunctionSig
from mypy import stubgenc as _stubgenc

from mypy.stubutil import (
    ClassInfo,
    FunctionContext,
    SignatureGenerator,
)

from mypy.stubgenc import (
    InspectionStubGenerator as _InspectionStubGenerator,
    ExternalSignatureGenerator,
    DocstringSignatureGenerator,
)

class MonkeyPatch:

    def inject() -> None:
        _stubgenc.InspectionStubGenerator = InspectionStubGenerator

    def eject() -> None:
        _stubgenc.InspectionStubGenerator = _InspectionStubGenerator

def is_cached_property(obj: Any) -> bool:
    return type(obj).__name__ == "cached_property"

class InspectionStubGenerator(_InspectionStubGenerator):
    """Stub generator that does not parse code.

    Generation is performed by inspecting the module's contents, and thus works
    for highly dynamic modules, pyc files, and C modules (via the CStubGenerator
    subclass).
    """

    def get_default_function_sig(self, func: object, ctx: FunctionContext) -> FunctionSig:
        
        if is_cached_property(func):
            func = func.func

        return super().get_default_function_sig(func, ctx)

    def get_sig_generators(self) -> list[SignatureGenerator]:
        if not self.is_c_module:
            return []
        else:
            sig_generators: list[SignatureGenerator] = [DocstringSignatureGenerator()]
            if self.doc_dir:
                # Collect info from docs (if given). Always check these first.
                sig_generators.insert(0, ExternalSignatureGenerator.from_doc_dir(self.doc_dir))
            return sig_generators

    def is_skipped_attribute(self, attr: str) -> bool:
        return (
            super().is_skipped_attribute(attr)
            or attr in (
                "_pybind11_conduit_v1_",
                "__pybind11_native_enum__",
            )
        )

    @staticmethod
    def is_property(class_info: ClassInfo, name: str, obj: object) -> bool:
        return (
            super().is_property(class_info, name)
            or is_cached_property(obj)
        )

    @staticmethod
    def is_property_readonly(prop: Any) -> bool:
        return (
            super().is_property_readonly(prop)
            or is_cached_property(prop) 
        )

    def generate_function_stub(
        self, name: str, obj: object, *, output: list[str], class_info: ClassInfo | None = None
    ) -> None:
        """Generate stub for a single function or method.

        The result (always a single line) will be appended to 'output'.
        If necessary, any required names will be added to 'imports'.
        The 'class_name' is used to find signature of __init__ or __new__ in
        'class_sigs'.
        """
        docstring: Any = getattr(obj, "__doc__", None)
        if not isinstance(docstring, str):
            docstring = None

        ctx = FunctionContext(
            self.module_name,
            name,
            docstring=docstring,
            is_abstract=self.is_abstract_method(obj),
            class_info=class_info,
        )
        if self.is_private_name(name) or self.is_not_in_all(name):
            return

        self.record_name(ctx.name)
        default_sig = self.get_default_function_sig(obj, ctx)
        inferred = self.get_signatures(default_sig, self.sig_generators, ctx)
        self.process_inferred_sigs(inferred)

        decorators = []
        if len(inferred) > 1:
            decorators.append("@{}".format(self.add_name("typing.overload")))

        if ctx.is_abstract:
            decorators.append("@{}".format(self.add_name("abc.abstractmethod")))

        if class_info is not None:
            if self.is_staticmethod(class_info, name, obj):
                decorators.append("@staticmethod")
            else:
                for sig in inferred:
                    if not sig.args or sig.args[0].name not in ("self", "cls"):
                        sig.args.insert(0, ArgSig(name=class_info.self_var))
                # a sig generator indicates @classmethod by specifying the cls arg.
                if inferred[0].args and inferred[0].args[0].name == "cls":
                    decorators.append("@classmethod")

        docstring = self._indent_docstring(ctx.docstring) if ctx.docstring else None
        output.extend(self.format_func_def(inferred, decorators=decorators, docstring=docstring))
        self._fix_iter(ctx, inferred, output)

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

        if (is_cached_property(raw_obj) 
            and len(ro_properties) > initial_size
            and "@property" in ro_properties[-1]
        ):
            self.import_tracker.add_import_from("functools", [("cached_property", None)])
            ro_properties[-1] = ro_properties[-1].replace("@property", "@cached_property")


