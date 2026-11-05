from ghp_import import ghp_import

# Upload the Built Docs to GitHub Pages Branch
ghp_import(
    srcdir = "_build\\html",
    nojekyll = True,
    push = True,
    force = True
)

