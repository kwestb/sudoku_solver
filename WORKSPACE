workspace(name = "sudoku_solver")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "rules_python",
    sha256 = "cdf6b84084aad8f10bf20b46b77cb48d83c319ebe6458a18e9d2cebf57807cdd",
    strip_prefix = "rules_python-0.8.1",
    urls = ["https://github.com/bazelbuild/rules_python/archive/refs/tags/0.8.1.tar.gz"],
)

load("@rules_python//python:repositories.bzl", "python_register_toolchains")

python_register_toolchains(
    name = "python",
    python_version = "3.10",
)

load("@rules_python//python:pip.bzl", "pip_parse")

load("@python//:defs.bzl", "interpreter")

pip_parse(
    name = "requirements",
    python_interpreter_target = interpreter,
    requirements_lock = "//:requirements.txt",
)

load("@requirements//:requirements.bzl", "install_deps")

install_deps()
