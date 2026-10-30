from levi.findings import BLOCK, Finding
from levi.paths import is_test_file, matches

NAME = "forbidden_files"


def check(files, intent):
    findings = []
    for diff in files:
        for path in diff.paths():
            pattern = next((p for p in intent.forbidden if matches(path, p)), None)
            if pattern:
                findings.append(Finding(NAME, BLOCK, path, f"{diff.status} {path}, which you were told not to touch ({pattern})"))
                break
            if intent.protect_tests and is_test_file(path):
                findings.append(Finding(NAME, BLOCK, path, f"{diff.status} test file {path}, but you were told not to touch tests"))
                break
    return findings
