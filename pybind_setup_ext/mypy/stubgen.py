from __future__ import annotations

__all__ = [
    "generate_stubs"
]

import os

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

    os.environ["STUBGEN"] = "1"
    try:
        _generate_stubs(options)
    finally:
        os.environ.pop("STUBGEN", None)


