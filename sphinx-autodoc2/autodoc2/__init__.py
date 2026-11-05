"""Analyse a python project and create documentation for it."""

def setup(app):  # type: ignore
    """Entrypoint for sphinx."""
    from .sphinx.extension import setup as _setup

    return _setup(app)
