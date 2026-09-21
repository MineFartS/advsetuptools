from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('setup', action='store_true')
parser.add_argument('build', action='store_true')
args = parser.parse_args()

if args.install:
    from .install import gitignore
    from .install import sphinx
elif args.build:
    from .build import sphinx
    from .build import ghp_import

