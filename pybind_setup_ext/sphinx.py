from sphinx.application import Sphinx
from ghp_import import ghp_import
from datetime import datetime
from os.path import abspath
from pathlib import Path
import sys

#======================================================================
# Sphinx - Build Documentation

s = Sphinx(
    srcdir = ".",
    confdir = ".",
    outdir = "_build/html",
    doctreedir = "_build/doctrees",
    buildername = "html",
    freshenv = True,
)

# Safely modify the runtime sys.path
sys.path.insert(0, abspath("."))

# Mutate existing configuration variables from conf.py
s.config.copyright = f'{datetime.now().year}, {s.config.author}'

# Ensure lists are cleanly extended
s.config.exclude_patterns += ['_build', 'Thumbs.db', '.DS_Store']
s.config.extensions += ["autodoc2", "sphinx.ext.viewcode"]

# Inject your dynamic autodoc2 configurations
s.config.autodoc2_packages = [s.config.project]
s.config.autodoc2_output_dir = "_api"
s.config.autodoc2_render_plugin = "rst"

s.config.autodoc_mock_imports = [
    ".".join(pyi_path.with_suffix("").parts)
    for pyi_path in Path(s.config.project).rglob("*.pyi") 
]

s.build()

#======================================================================
# GHP_IMPORT - Upload Documentation

ghp_import(
    srcdir = "_build\\html",
    nojekyll = True,
    push = True,
    force = True
)

#======================================================================

