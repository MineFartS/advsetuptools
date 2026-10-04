from __future__ import annotations

from typing import Callable

from mypy_stubgen.plugin import AttributeContext, Plugin
from mypy_stubgen.types import Type as MypyType


class ClassAttrPlugin(Plugin):
    def get_class_attribute_hook(
        self, fullname: str
    ) -> Callable[[AttributeContext], MypyType] | None:
        if fullname == "__main__.Cls.attr":
            return my_hook
        return None


def my_hook(ctx: AttributeContext) -> MypyType:
    return ctx.api.named_generic_type("builtins.int", [])


def plugin(_version: str) -> type[ClassAttrPlugin]:
    return ClassAttrPlugin
