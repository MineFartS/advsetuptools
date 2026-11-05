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

    def get_members(self, obj: object) -> list[tuple[str, Any]]:
        obj_dict: Mapping[str, Any] = getattr(obj, "__dict__")  # noqa: B009
        results = []
        for name in obj_dict:
            if self.is_skipped_attribute(name):
                continue
            # Try to get the value via getattr
            try:
                if is_cached_property(obj_dict[name]):
                    value = obj_dict[name]
                else:
                    value = getattr(obj, name)
            except AttributeError:
                continue
            else:
                results.append((name, value))
        return results

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
        """Generate property stub using introspection of 'obj'.

        Try to infer type from docstring, append resulting lines to 'output'.

        raw_obj : object before evaluation of descriptor (if any)
        obj : object after evaluation of descriptor
        """

        is_cached_prop = is_cached_property(raw_obj)

        docstring = getattr(raw_obj, "__doc__", None)
        
        if is_cached_prop and not docstring:
            docstring = getattr(raw_obj.func, "__doc__", None)
        
        fget = getattr(raw_obj, "fget", None)
        if fget:
            alt_docstr = getattr(fget, "__doc__", None)
            if alt_docstr and docstring:
                docstring += "\n" + alt_docstr
            elif alt_docstr:
                docstring = alt_docstr

        ctx = FunctionContext(
            self.module_name, name, docstring=docstring, is_abstract=False, class_info=class_info
        )

        if self.is_private_name(name) or self.is_not_in_all(name):
            return

        self.record_name(ctx.name)
        static = self.is_static_property(raw_obj)
        readonly = self.is_property_readonly(raw_obj)
        if static:
            ret_type: str | None = self.strip_or_import(self.get_type_annotation(obj))
        else:
            default_sig = self.get_default_function_sig(raw_obj, ctx)
            ret_type = default_sig.ret_type

        inferred_type = self.get_property_type(ret_type, self.sig_generators, ctx)
        if inferred_type is not None:
            inferred_type = self.strip_or_import(inferred_type)

        if static:
            classvar = self.add_name("typing.ClassVar")
            trailing_comment = "  # read-only" if readonly else ""
            if inferred_type is None:
                inferred_type = self.add_name("_typeshed.Incomplete")

            static_properties.append(
                f"{self._indent}{name}: {classvar}[{inferred_type}] = ...{trailing_comment}"
            )
        else:  # regular property
            if readonly:
                docstring = self._indent_docstring(ctx.docstring) if ctx.docstring else None

                if is_cached_prop:
                    self.import_tracker.add_import_from("functools", [("cached_property", None)])
                    ro_properties.append(f"{self._indent}@cached_property")
                else:
                    ro_properties.append(f"{self._indent}@property")
                
                sig = FunctionSig(name, [ArgSig("self")], inferred_type, docstring=docstring)
                ro_properties.append(
                    sig.format_sig(
                        indent=self._indent, include_docstrings=self._include_docstrings
                    )
                )
            else:
                if inferred_type is None:
                    inferred_type = self.add_name("_typeshed.Incomplete")

                rw_properties.append(f"{self._indent}{name}: {inferred_type}")

