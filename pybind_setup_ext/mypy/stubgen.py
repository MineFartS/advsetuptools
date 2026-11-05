from __future__ import annotations

__all__ = [
    "generate_stub_for_py_module",
    "generate_stubs"
]

import os, sys

from .stubgenc import (
    generate_stub_for_c_module,
    InspectionStubGenerator,
)

from mypy.stubutil import (
    common_dir_prefix,
    generate_guarded,
)

from mypy.stubgen import (
    generate_asts_for_modules,
    collect_build_targets,
    parse_options,
    mypy_options,
    StubSource,
)

def generate_stub_for_py_module(
    mod: StubSource,
    target: str,
    *,
    export_less: bool = False,
    include_docstrings: bool = False,
    doc_dir: str = "",
    all_modules: list[str],
) -> None:
    """Use analysed (or just parsed) AST to generate type stub for single file.

    If directory for target doesn't exist it will created. Existing stub
    will be overwritten.
    """

    ngen = InspectionStubGenerator(
        module_name=mod.module,
        known_modules=all_modules,
        _all_=mod.runtime_all,
        doc_dir=doc_dir,
        export_less=export_less,
        include_docstrings=include_docstrings,
    )
    ngen.generate_module()
    output = ngen.output()

    # Write output to file.
    subdir = os.path.dirname(target)
    if subdir and not os.path.isdir(subdir):
        os.makedirs(subdir)
    with open(target, "w", encoding="utf-8") as file:
        file.write(output)


def generate_stubs(
    output_dir: str, 
    modules: list[str]
) -> None:
    """Main entry point for the program."""

    # Make sure that the current directory is in sys.path so that
    # stubgen can be run on packages in the current directory.
    if not ("" in sys.path or "." in sys.path):
        sys.path.insert(0, "")

    options = parse_options([
        '--output', output_dir,
    ])
    options.modules = modules

    os.environ["STUBGEN"] = "1"
    try:
        mypy_opts = mypy_options(options)
        py_modules, pyc_modules, c_modules = collect_build_targets(options, mypy_opts)
        all_modules = py_modules + pyc_modules + c_modules
        all_module_names = sorted(m.module for m in all_modules)
        # Use parsed sources to generate stubs for Python modules.
        generate_asts_for_modules(py_modules, mypy_opts, options.verbose)
        files = []
        for mod in py_modules + pyc_modules:
            assert mod.path is not None, "Not found module was not skipped"
            target = mod.module.replace(".", "/")
            if os.path.basename(mod.path) in ["__init__.py", "__init__.pyc"]:
                target += "/__init__.pyi"
            else:
                target += ".pyi"
            target = os.path.join(options.output_dir, target)
            files.append(target)
            with generate_guarded(mod.module, target, options.ignore_errors, options.verbose):
                generate_stub_for_py_module(
                    mod,
                    target,
                    export_less=options.export_less,
                    include_docstrings=options.include_docstrings,
                    doc_dir=options.doc_dir,
                    all_modules=all_module_names,
                )

        # Separately analyse C modules using different logic.
        for mod in c_modules:
            if any(py_mod.module.startswith(mod.module + ".") for py_mod in all_modules):
                target = mod.module.replace(".", "/") + "/__init__.pyi"
            else:
                target = mod.module.replace(".", "/") + ".pyi"
            target = os.path.join(options.output_dir, target)
            files.append(target)
            with generate_guarded(mod.module, target, options.ignore_errors, options.verbose):
                generate_stub_for_c_module(
                    mod.module,
                    target,
                    known_modules=all_module_names,
                    doc_dir=options.doc_dir,
                    export_less=options.export_less,
                    include_docstrings=options.include_docstrings,
                )
        num_modules = len(all_modules)
        if not options.quiet and num_modules > 0:
            print("Processed %d modules" % num_modules)
            if len(files) == 1:
                print(f"Generated {files[0]}")
            else:
                print(f"Generated files under {common_dir_prefix(files)}" + os.sep)

    finally:
        os.environ.pop("STUBGEN", None)


