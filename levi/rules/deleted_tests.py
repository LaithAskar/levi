from levi.findings import BLOCK, Finding
from levi.paths import is_test_file, language
from levi.patterns import test_names

NAME = "deleted_tests"


def check(files, intent):
    findings = []
    for diff in files:
        if diff.old_path and is_test_file(diff.old_path) and not is_test_file(diff.new_path):
            if diff.status == "deleted":
                message = f"deleted test file {diff.old_path}"
            else:
                message = f"moved test file {diff.old_path} to non-test path {diff.new_path}"
            findings.append(Finding(NAME, BLOCK, diff.old_path, message))
            continue
        if not is_test_file(diff.path):
            continue
        lang = language(diff.path)
        added = {name for line in diff.added() for name in test_names(line.text, lang)}
        for line in diff.removed():
            for name in test_names(line.text, lang):
                if name not in added:
                    findings.append(Finding(NAME, BLOCK, diff.path, f"removed test '{name}' from {diff.path}", line.old_no))
    return findings
