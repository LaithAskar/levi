import unittest

from levi.diff import parse_diff
from levi.intent import Intent
from levi.rules import deleted_tests
from tests.support import load_diff

MOVED_TEST = """diff --git a/tests/test_math.py b/tests/test_math.py
index 1111111..2222222 100644
--- a/tests/test_math.py
+++ b/tests/test_math.py
@@ -1,6 +1,6 @@
-def test_add():
-    assert 1 + 1 == 2
-
-
 def test_sub():
     assert 2 - 1 == 1
+
+
+def test_add():
+    assert 1 + 1 == 2
"""

RENAMED_AWAY = """diff --git a/tests/test_legacy.py b/scripts/legacy_check.py
similarity index 100%
rename from tests/test_legacy.py
rename to scripts/legacy_check.py
"""


class DeletedTestsTest(unittest.TestCase):
    def test_python_and_ts_deletions(self):
        findings = deleted_tests.check(load_diff("deleted_tests"), Intent())
        self.assertEqual(
            [(f.path, f.message) for f in findings],
            [
                ("src/__tests__/format.test.ts", "removed test 'rejects NaN' from src/__tests__/format.test.ts"),
                ("tests/test_lock.py", "deleted test file tests/test_lock.py"),
                ("tests/test_pager.py", "removed test 'test_page_slice_last_page' from tests/test_pager.py"),
            ],
        )
        self.assertEqual(findings[2].line, 20)

    def test_renamed_out_of_test_tree(self):
        findings = deleted_tests.check(parse_diff(RENAMED_AWAY), Intent())
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].message, "moved test file tests/test_legacy.py to non-test path scripts/legacy_check.py")

    def test_moved_test_is_not_deleted(self):
        self.assertEqual(deleted_tests.check(parse_diff(MOVED_TEST), Intent()), [])

    def test_clean_diff(self):
        self.assertEqual(deleted_tests.check(load_diff("clean"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
