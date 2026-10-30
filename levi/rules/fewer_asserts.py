from levi.findings import BLOCK, Finding
from levi.paths import is_test_file, language
from levi.patterns import count_asserts

NAME = "fewer_asserts"


def check(files, intent):
    findings = []
    for diff in files:
        if diff.status == "deleted" or not is_test_file(diff.path):
            continue
        lang = language(diff.path)
        removed = sum(count_asserts(line.text, lang) for line in diff.removed())
        added = sum(count_asserts(line.text, lang) for line in diff.added())
        if removed > added:
            first = next((line.old_no for line in diff.removed() if count_asserts(line.text, lang)), None)
            findings.append(Finding(NAME, BLOCK, diff.path, f"assertion count in {diff.path} dropped by {removed - added} (removed {removed}, added {added})", first))
    return findings
