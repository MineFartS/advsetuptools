from .utils import shell

__all__ = [
    "update_submodule",
]

def update_submodule(
    name: str|None = None,
    *,
    force: bool = False, 
    remote: bool = False,
    recurse: bool = True,
) -> None:
    
    args: list[str] = []
    if recurse: args += ['--recursive']
    if remote: args += ['--remote']
    if force:  args += ['--force']
    if name:   args += [name]

    shell.git('submodule', 'update', '--init', *args)

