import unittest

from levi.diff import parse_diff
from levi.intent import Intent
from levi.rules import skipped_tests
from tests.support import load_diff

COMMENTED_SKIP = """diff --git a/tests/test_api.py b/tests/test_api.py
index 1111111..2222222 100644
--- a/tests/test_api.py
+++ b/tests/test_api.py
@@ -1,2 +1,3 @@
+# @pytest.mark.skip was removed here last week
 def test_ok():
     assert True is not False
"""


class SkippedTestsTest(unittest.TestCase):
    def test_python_and_js_skips(self):
        findings = skipped_tests.check(load_diff("skipped_tests"), Intent())
        self.assertEqual(
            [(f.path, f.line) for f in findings],
            [
                ("src/__tests__/format.test.ts", 13),
                ("src/__tests__/format.test.ts", 17),
                ("tests/cart.test.js", 4),
                ("tests/test_lock.py", 18),
                ("tests/test_pager.py", 20),
            ],
        )
        self.assertIn("focused", findings[2].message)
        self.assertIn("@pytest.mark.skip", findings[4].message)

    def test_comments_are_ignored(self):
        self.assertEqual(skipped_tests.check(parse_diff(COMMENTED_SKIP), Intent()), [])

    def test_clean_diff(self):
        self.assertEqual(skipped_tests.check(load_diff("clean"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
