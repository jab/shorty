load("@aspect_rules_py//py:defs.bzl", "py_binary")

py_binary(
    name = "app_bin",
    srcs = ["__main__.py"],
    main = "__main__.py",
    visibility = ["//:__subpackages__"],
    deps = [
        "@pip//flask",
        "@pip//hypercorn",
    ],
)
