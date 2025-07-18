"""Targets in the repository root"""

# We prefer BUILD instead of BUILD.bazel
# gazelle:build_file_name BUILD

load("@pip//:requirements.bzl", "all_whl_requirements")
load("@rules_python_gazelle_plugin//manifest:defs.bzl", "gazelle_python_manifest")
load("@rules_python_gazelle_plugin//modules_mapping:def.bzl", "modules_mapping")

alias(
    name = "format",
    actual = "//tools/format",
)

exports_files(
    [".shellcheckrc"],
    visibility = ["//:__subpackages__"],
)

exports_files(
    ["pyproject.toml"],
    visibility = ["//:__subpackages__"],
)

# Set `aspect configure` to produce aspect_rules_py targets rather than rules_python
# aspect:map_kind py_binary py_binary @aspect_rules_py//py:defs.bzl
# aspect:map_kind py_library py_library @aspect_rules_py//py:defs.bzl
# aspect:map_kind py_test py_test @aspect_rules_py//py:defs.bzl
#
# Don't walk into virtualenvs when looking for python sources.
# We don't intend to plant BUILD files there.
# aspect:exclude **/*.venv
#
# Fetches metadata for python packages we depend on.
modules_mapping(
    name = "modules_map",
    wheels = all_whl_requirements,
)

# Provide a mapping from an import to the installed package that provides it.
# Needed to generate BUILD files for .py files.
# This macro produces two targets:
# - //:gazelle_python_manifest.update can be used with `bazel run`
#   to recalculate the manifest
# - //:gazelle_python_manifest.test is a test target ensuring that
#   the manifest doesn't need to be updated
gazelle_python_manifest(
    name = "gazelle_python_manifest",
    modules_mapping = ":modules_map",
    pip_repository_name = "pip",
)
