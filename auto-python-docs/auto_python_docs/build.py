from sphinx.cmd.build import main

# Build Documentation
status = main([
    '-M', 'html', 
    '.', '_build', 
    '-E', '-a'
])
if status != 0:
    raise RuntimeError(f'{status=}')

