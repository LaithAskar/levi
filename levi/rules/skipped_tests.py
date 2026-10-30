from levi.findings import BLOCK, Finding
from levi.paths import is_test_file, language
from levi.patterns import skip_marker

NAME = "skipped_tests"


def check(files, intent):
    findings = []
    for diff in files:
        if not diff.new_path or not is_test_file(diff.new_path):
            continue
        lang = language(diff.new_path)
        removed = [line.text.strip() for line in diff.removed()]
        for line in diff.added():
            marker = skip_marker(line.text, lang)
            if not marker:
                continue
            if line.text.strip() in removed:
                removed.remove(line.text.strip())
                continue
            kind = "focused (other tests stop running)" if "only" in marker or marker.lstrip("(").startswith("f") else "skipped or disabled"
            findings.append(Finding(NAME, BLOCK, diff.new_path, f"test {kind} with {marker.strip()} in {diff.new_path}", line.new_no))
    return findings
