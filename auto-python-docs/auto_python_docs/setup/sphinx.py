from sphinx.cmd.quickstart import main
from tomllib import load

with open("pyproject.toml", "rb") as f:
    project = load(f)['project']

args = ['=q']

args += '-p', project['name']
args += '-v', project['version']

args += "--no-sep", '.'

result = main(args)

if result != 0:
    raise RuntimeError(f'{result=}')

