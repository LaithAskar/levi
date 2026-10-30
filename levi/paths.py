import re
from fnmatch import fnmatchcase
from pathlib import PurePosixPath

PYTHON_EXTS = {".py", ".pyi"}
JS_EXTS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"}
TEST_DIRS = {"tests", "test", "__tests__", "spec", "specs"}
JS_TEST_NAME_RE = re.compile(r"\.(?:test|spec)\.[cm]?[jt]sx?$")
CI_DIRS = (".github/workflows/", ".github/actions/", ".gitlab/ci/", ".circleci/", ".buildkite/", ".woodpecker/", "azure-pipelines/")
CI_NAMES = {
    ".gitlab-ci.yml",
    ".travis.yml",
    "azure-pipelines.yml",
    "Jenkinsfile",
    "bitbucket-pipelines.yml",
    ".drone.yml",
    "appveyor.yml",
    ".woodpecker.yml",
}


def normalize(path, cwd=""):
    path = path.replace("\\", "/").strip()
    if cwd:
        root = cwd.replace("\\", "/").rstrip("/") + "/"
        if path.startswith(root):
            path = path[len(root):]
    while path.startswith("./"):
        path = path[2:]
    return path


def language(path):
    suffix = PurePosixPath(path).suffix.lower()
    if suffix in PYTHON_EXTS:
        return "python"
    if suffix in JS_EXTS:
        return "js"
    return None


def is_test_file(path):
    if not path:
        return False
    pure = PurePosixPath(normalize(path))
    name = pure.name
    in_test_dir = any(part in TEST_DIRS for part in pure.parts[:-1])
    lang = language(name)
    if lang == "python":
        return name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py" or in_test_dir
    if lang == "js":
        return bool(JS_TEST_NAME_RE.search(name)) or in_test_dir
    return False


def is_ci_file(path):
    if not path:
        return False
    path = normalize(path)
    if any(path.startswith(prefix) or ("/" + prefix) in path for prefix in CI_DIRS):
        return True
    return PurePosixPath(path).name in CI_NAMES


def matches(path, pattern):
    path = normalize(path)
    pattern = normalize(pattern)
    if not path or not pattern:
        return False
    if any(char in pattern for char in "*?["):
        trimmed = pattern.rstrip("/")
        return any(fnmatchcase(path, candidate) for candidate in (trimmed, trimmed + "/*", "*/" + trimmed, "*/" + trimmed + "/*"))
    return ("/" + pattern.strip("/") + "/") in ("/" + path + "/")
