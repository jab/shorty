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

py_pytest_main(
    name = "__test__",
    deps = ["@pip//pytest"],
)

py_test(
    name = "app_test",
    srcs = [
        "test_app.py",
        ":__test__",
    ],
    main = ":__test__.py",
    deps = [
        ":__test__",
        ":app_bin",
        "@pip//flask",
        "@pip//pytest",
    ],
)
