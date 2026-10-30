from levi.findings import BLOCK, Finding
from levi.paths import is_test_file, language
from levi.patterns import assert_strength, count_asserts

NAME = "weaker_asserts"


def check(files, intent):
    findings = []
    for diff in files:
        if not diff.new_path or not is_test_file(diff.new_path):
            continue
        lang = language(diff.new_path)
        for hunk in diff.hunks:
            removed = [line for line in hunk.removed() if count_asserts(line.text, lang)]
            added = [line for line in hunk.added() if count_asserts(line.text, lang)]
            for index, new in enumerate(added):
                new_strength = assert_strength(new.text, lang)
                if new_strength == 0:
                    findings.append(Finding(NAME, BLOCK, diff.new_path, f"added an assertion that always passes: {new.text.strip()}", new.new_no))
                    continue
                if index < len(removed):
                    old = removed[index]
                    if new_strength < assert_strength(old.text, lang):
                        findings.append(Finding(NAME, BLOCK, diff.new_path, f"weakened assertion: {old.text.strip()} -> {new.text.strip()}", new.new_no))
    return findings
