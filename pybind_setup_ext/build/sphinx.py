from ..sphinx.application import Sphinx
from ghp_import import ghp_import

Sphinx(
    srcdir = ".",
    confdir = ".",
    outdir = "_build/html",
    doctreedir = "_build/doctrees",
    buildername = "html",
    freshenv = True,
).build()

# Upload the Built Docs to GitHub Pages Branch
ghp_import(
    srcdir = "_build\\html",
    nojekyll = True,
    push = True,
    force = True
)

