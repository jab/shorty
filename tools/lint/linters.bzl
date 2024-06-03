load("@aspect_rules_lint//lint:ruff.bzl", "lint_ruff_aspect")
load("@aspect_rules_lint//lint:lint_test.bzl", "lint_test")


ruff = lint_ruff_aspect(
    binary = "@@//tools/lint:ruff",
    configs = "@@//:.ruff.toml",
)

ruff_test = lint_test(aspect = ruff)
