from sphinx.application import Sphinx
from sphinx.config import Config
from datetime import datetime
from os.path import abspath
from pathlib import Path
import sys

def _read(confdir, overrides=None):

    # Properly invoke the parent classmethod to load conf.py
    config = _orig_read(confdir, overrides)
    
    # Safely modify the runtime sys.path
    sys.path.insert(0, abspath("."))
    
    # Mutate existing configuration variables from conf.py
    config.copyright = f'{datetime.now().year}, {config.author}'
    
    # Ensure lists are cleanly extended
    config.exclude_patterns += ['_build', 'Thumbs.db', '.DS_Store']
    config.extensions += ["autodoc2", "sphinx.ext.viewcode"]
    
    # Inject your dynamic autodoc2 configurations
    config.autodoc2_packages = [config.project]
    config.autodoc2_output_dir = "_api"
    config.autodoc2_render_plugin = "rst"
    
    config.autodoc_mock_imports = [
        ".".join(pyi_path.with_suffix("").parts)
        for pyi_path in Path(config.project).rglob("*.pyi") 
    ]
    
    return config

_orig_read = Config.read
Config.read = _read

Sphinx(
    srcdir = ".",
    confdir = ".",
    outdir = "_build/html",
    doctreedir = "_build/doctrees",
    buildername = "html",
    freshenv = True,
    force_all = True,
).build()

