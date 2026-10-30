import unittest

from levi.findings import BLOCK
from levi.intent import Intent
from levi.rules import out_of_scope
from tests.support import load_diff


class OutOfScopeTest(unittest.TestCase):
    def test_flags_files_outside_allowlist(self):
        intent = Intent(allowed=["src/pager.py", "tests/test_pager.py"], forbidden=["src/auth/", "src/db/lock.py"])
        findings = out_of_scope.check(load_diff("scope"), intent)
        self.assertEqual([f.path for f in findings], ["docs/pagination.md", "src/utils/strings.py"])
        self.assertTrue(all(f.severity == BLOCK for f in findings))

    def test_file_budget(self):
        findings = out_of_scope.check(load_diff("scope"), Intent(max_files=3))
        self.assertEqual(len(findings), 1)
        self.assertIn("changed 5 files, but the limit was 3", findings[0].message)

    def test_globs_and_dirs_in_scope(self):
        self.assertEqual(out_of_scope.check(load_diff("scope"), Intent(allowed=["src/*", "docs/"])), [])

    def test_no_allowlist_no_findings(self):
        self.assertEqual(out_of_scope.check(load_diff("scope"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
