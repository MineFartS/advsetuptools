from __future__ import annotations

from typing import Callable

from mypy_stubgen.plugin import AttributeContext, Plugin
from mypy_stubgen.types import Instance, Type


class AttrPlugin(Plugin):
    def get_attribute_hook(self, fullname: str) -> Callable[[AttributeContext], Type] | None:
        if fullname == "m.Signal.__call__":
            return signal_call_callback
        return None


def signal_call_callback(ctx: AttributeContext) -> Type:
    if isinstance(ctx.type, Instance):
        return ctx.type.args[0]
    return ctx.default_attr_type


def plugin(version: str) -> type[AttrPlugin]:
    return AttrPlugin
