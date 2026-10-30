import unittest

from levi.diff import parse_diff
from levi.findings import WARN
from levi.intent import Intent
from levi.rules import removed_error_handling
from tests.support import load_diff

REWRAPPED = """diff --git a/app/io.py b/app/io.py
index 1111111..2222222 100644
--- a/app/io.py
+++ b/app/io.py
@@ -1,4 +1,4 @@
 try:
-    data = read()
-except OSError:
+    data = read(retries=3)
+except OSError:
     data = None
"""


class RemovedErrorHandlingTest(unittest.TestCase):
    def test_removed_catch_and_except(self):
        findings = removed_error_handling.check(load_diff("removed_error_handling"), Intent())
        self.assertEqual(
            [(f.path, f.severity, f.line) for f in findings],
            [("src/api/client.ts", WARN, 8), ("src/config/loader.py", WARN, 11)],
        )
        self.assertIn("removed 2 catch handler(s)", findings[0].message)
        self.assertIn("removed 2 except handler(s)", findings[1].message)

    def test_rewritten_handler_is_not_removed(self):
        self.assertEqual(removed_error_handling.check(parse_diff(REWRAPPED), Intent()), [])

    def test_clean_diff(self):
        self.assertEqual(removed_error_handling.check(load_diff("clean"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
