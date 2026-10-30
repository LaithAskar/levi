import re

from levi.findings import WARN, Finding
from levi.paths import language
from levi.patterns import is_comment

NAME = "removed_error_handling"

HANDLER_RES = {
    "python": re.compile(r"^\s*except\b"),
    "js": re.compile(r"\bcatch\s*[({]|\.catch\s*\("),
}


def _handlers(lines, lang):
    pattern = HANDLER_RES[lang]
    return [line for line in lines if pattern.search(line.text) and not is_comment(line.text, lang)]


def check(files, intent):
    findings = []
    for diff in files:
        if not diff.old_path:
            continue
        lang = language(diff.old_path)
        if lang not in HANDLER_RES:
            continue
        removed = _handlers(diff.removed(), lang)
        added = _handlers(diff.added(), lang) if diff.new_path else []
        if len(removed) > len(added):
            count = len(removed) - len(added)
            kind = "except" if lang == "python" else "catch"
            findings.append(Finding(NAME, WARN, diff.path, f"removed {count} {kind} handler(s) in {diff.path}: {removed[0].text.strip()}", removed[0].old_no))
    return findings
