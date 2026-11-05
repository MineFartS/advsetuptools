from __future__ import annotations

__all__ = [
    "generate_stubs"
]

import os, sys

from mypy.stubgen import (
    parse_options,
    generate_stubs as _generate_stubs,
)


def generate_stubs(
    output_dir: str, 
    modules: list[str]
) -> None:
    """Main entry point for the program."""

    # Make sure that the current directory is in sys.path so that
    # stubgen can be run on packages in the current directory.
    if not ("" in sys.path or "." in sys.path):
        sys.path.insert(0, "")

    options = parse_options([
        '--output', output_dir,
    ])
    options.modules = modules

    os.environ["STUBGEN"] = "1"
    try:
        _generate_stubs(options)
    finally:
        os.environ.pop("STUBGEN", None)


