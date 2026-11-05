from sphinx.application import Sphinx

Sphinx(
    srcdir = ".",
    confdir = ".",
    outdir = "_build/html",
    doctreedir = "_build/doctrees",
    buildername = "html",
    freshenv = True,
).build()

