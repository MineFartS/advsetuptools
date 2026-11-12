# advsetuptools

Wrapper for Python's `setuptools`

---
## Installation:

```
pip install "advsetuptools @ git+https://github.com/MineFartS/advsetuptools"
```

---
## Features:

- Advanced pybind11 behavior and syntax

- Automatic `.pyi` stub generation *([mypy](https://github.com/python/mypy))*

- Automatic documentation *([sphinx-autodoc2](https://github.com/sphinx-extensions2/sphinx-autodoc2))* with GitHub Pages deployment *([ghp-import](https://github.com/c-w/ghp-import))*

- Git submodule management

---

## Example:

```python
from advsetuptools import setup, cpp_ext, update_submodule

update_submodule(recurse=True) # Optional

ext_win_only = cpp_ext(
    "mypkg/win_native.cpp",
    platforms=["win32"],
    extra_objects=["libs/*.lib"],
)

ext_cross_platform = cpp_ext(
    "mypkg/fast_math.cpp",
    include_dirs=["external/include"],
)

setup(
    ext_win_only,
    ext_cross_platform,
)
```

