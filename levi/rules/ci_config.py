from levi.findings import BLOCK, WARN, Finding
from levi.paths import is_ci_file

NAME = "ci_config"


def check(files, intent):
    findings = []
    for diff in files:
        path = next((p for p in diff.paths() if is_ci_file(p)), None)
        if not path:
            continue
        if intent.protect_ci:
            findings.append(Finding(NAME, BLOCK, path, f"{diff.status} CI config {path}, but you were told not to change CI"))
        else:
            findings.append(Finding(NAME, WARN, path, f"{diff.status} CI config {path}"))
    return findings
