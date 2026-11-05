"""Command-line interface for the apidoc extension."""

from __future__ import annotations

import sys

from ._cli import main

raise SystemExit(main(sys.argv[1:]))
