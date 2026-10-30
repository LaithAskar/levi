from levi.diff import parse_diff
from levi.intent import Intent
from levi.rules import (
    ci_config,
    deleted_tests,
    fewer_asserts,
    forbidden_files,
    out_of_scope,
    removed_error_handling,
    skipped_tests,
    weaker_asserts,
)

RULES = [
    forbidden_files,
    out_of_scope,
    deleted_tests,
    skipped_tests,
    fewer_asserts,
    weaker_asserts,
    removed_error_handling,
    ci_config,
]


def run(diff, intent=None):
    files = parse_diff(diff) if isinstance(diff, str) else diff
    intent = intent or Intent()
    return [finding for rule in RULES for finding in rule.check(files, intent)]
