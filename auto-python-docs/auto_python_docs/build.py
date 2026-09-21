from sphinx.cmd.build import main
from ghp_import import ghp_import

# Build Documentation
status = main([
    '-M', 'html', 
    '.', '_build', 
    '-E', '-a'
])
if status != 0:
    raise RuntimeError(f'{status=}')

# Upload the Built Docs to GitHub Pages Branch
ghp_import(
    srcdir = "_build\\html",
    nojekyll = True,
    push = True,
    force = True
)

