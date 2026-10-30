import unittest

from levi.findings import BLOCK
from levi.intent import Intent
from levi.rules import forbidden_files
from tests.support import load_diff


class ForbiddenFilesTest(unittest.TestCase):
    def test_flags_forbidden_paths(self):
        findings = forbidden_files.check(load_diff("scope"), Intent(forbidden=["src/auth/", "src/db/lock.py"]))
        self.assertEqual([f.path for f in findings], ["src/auth/session.py", "src/db/lock.py"])
        self.assertTrue(all(f.severity == BLOCK for f in findings))
        self.assertIn("src/auth/", findings[0].message)

    def test_protect_tests_blocks_any_test_edit(self):
        findings = forbidden_files.check(load_diff("deleted_tests"), Intent(protect_tests=True))
        self.assertEqual([f.path for f in findings], ["src/__tests__/format.test.ts", "tests/test_lock.py", "tests/test_pager.py"])

    def test_no_constraints_no_findings(self):
        self.assertEqual(forbidden_files.check(load_diff("scope"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
