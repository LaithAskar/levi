import unittest

from levi.intent import Intent, extract_intent
from levi.rules import RULES, run
from levi.transcript import parse
from tests.support import CLAUDE_SESSION, FIXTURES


class RunRulesTest(unittest.TestCase):
    def test_every_rule_is_registered(self):
        self.assertEqual(len({rule.NAME for rule in RULES}), 8)

    def test_clean_diff_has_no_findings(self):
        self.assertEqual(run((FIXTURES / "diffs" / "clean.diff").read_text(), Intent()), [])

    def test_transcript_intent_against_diff(self):
        intent = extract_intent(parse(CLAUDE_SESSION))
        findings = run((FIXTURES / "diffs" / "scope.diff").read_text(), intent)
        self.assertEqual(
            [(f.rule, f.path) for f in findings],
            [
                ("forbidden_files", "src/auth/session.py"),
                ("forbidden_files", "src/db/lock.py"),
                ("out_of_scope", "docs/pagination.md"),
                ("out_of_scope", "src/utils/strings.py"),
                ("out_of_scope", ""),
            ],
        )


if __name__ == "__main__":
    unittest.main()
