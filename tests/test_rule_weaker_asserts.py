import unittest

from levi.diff import parse_diff
from levi.intent import Intent
from levi.rules import weaker_asserts
from levi.patterns import assert_strength
from tests.support import load_diff

STRONGER = """diff --git a/tests/test_api.py b/tests/test_api.py
index 1111111..2222222 100644
--- a/tests/test_api.py
+++ b/tests/test_api.py
@@ -1,2 +1,2 @@
 def test_status():
-    self.assertTrue(resp.ok)
+    self.assertEqual(resp.status_code, 200)
"""


class WeakerAssertsTest(unittest.TestCase):
    def test_weakened_python_and_ts_asserts(self):
        findings = weaker_asserts.check(load_diff("weaker_asserts"), Intent())
        messages = [f.message for f in findings]
        self.assertEqual(
            messages,
            [
                'weakened assertion: expect(formatPrice(1999)).toEqual("$19.99"); -> expect(formatPrice(1999)).toBeDefined();',
                "weakened assertion: expect(() => formatPrice(NaN)).toThrow(RangeError); -> expect(() => formatPrice(NaN)).toThrow();",
                "weakened assertion: self.assertEqual(a.balance, 6) -> self.assertTrue(a.balance)",
                "weakened assertion: assert page_count(11, 5) == 3 -> assert page_count(11, 5)",
                "weakened assertion: with pytest.raises(ValueError): -> with pytest.raises(Exception):",
                "added an assertion that always passes: assert True",
            ],
        )

    def test_stronger_assert_is_fine(self):
        self.assertEqual(weaker_asserts.check(parse_diff(STRONGER), Intent()), [])

    def test_clean_diff(self):
        self.assertEqual(weaker_asserts.check(load_diff("clean"), Intent()), [])

    def test_strength_ordering(self):
        self.assertGreater(assert_strength("assert x == 1", "python"), assert_strength("assert x in y", "python"))
        self.assertGreater(assert_strength("assert x in y", "python"), assert_strength("assert x is not None", "python"))
        self.assertEqual(assert_strength("expect(true).toBe(true)", "js"), 0)
        self.assertLess(assert_strength("expect(x).not.toBeNull()", "js"), assert_strength("expect(x).toBeNull()", "js"))
        self.assertLess(assert_strength("expect(x).not.toBe(2)", "js"), assert_strength("expect(x).toBe(2)", "js"))


if __name__ == "__main__":
    unittest.main()
