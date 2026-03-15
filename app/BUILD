load("@aspect_rules_py//py:defs.bzl", "py_binary", "py_pytest_main", "py_test")

py_binary(
    name = "app_bin",
    srcs = ["__main__.py"],
    data = [":templates"],  # keep
    main = "__main__.py",
    visibility = ["//:__subpackages__"],
    deps = [
        "@pip//flask",
        "@pip//hypercorn",
    ],
)

filegroup(
    name = "templates",
    srcs = glob(["templates/*.j2"]),
)

py_test(
    name = "app_test",
    srcs = [
        "test_app.py",
    ],
    pytest_main = True,
    deps = [
        ":app_bin",
        "@pip//flask",
        "@pip//pytest",
    ],
)
