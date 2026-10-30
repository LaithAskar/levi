import unittest

from levi.findings import BLOCK, WARN
from levi.intent import Intent
from levi.rules import ci_config
from tests.support import load_diff


class CiConfigTest(unittest.TestCase):
    def test_ci_edit_warns_by_default(self):
        findings = ci_config.check(load_diff("ci_config"), Intent())
        self.assertEqual([(f.path, f.severity) for f in findings], [(".github/workflows/ci.yml", WARN)])

    def test_ci_edit_blocks_when_protected(self):
        findings = ci_config.check(load_diff("ci_config"), Intent(protect_ci=True))
        self.assertEqual([(f.path, f.severity) for f in findings], [(".github/workflows/ci.yml", BLOCK)])
        self.assertIn("told not to change CI", findings[0].message)

    def test_non_ci_diff(self):
        self.assertEqual(ci_config.check(load_diff("scope"), Intent(protect_ci=True)), [])


if __name__ == "__main__":
    unittest.main()
