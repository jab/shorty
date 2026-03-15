load("@rules_mypy//mypy:mypy.bzl", "mypy")

mypy_aspect = mypy(
    mypy_ini = "@@//:pyproject.toml",
)
