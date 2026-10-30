import unittest

from levi.findings import BLOCK
from levi.intent import Intent
from levi.rules import fewer_asserts
from tests.support import load_diff


class FewerAssertsTest(unittest.TestCase):
    def test_dropped_asserts_in_python_and_js(self):
        findings = fewer_asserts.check(load_diff("fewer_asserts"), Intent())
        self.assertEqual(
            [f.message for f in findings],
            [
                "assertion count in tests/cart.test.js dropped by 1 (removed 1, added 0)",
                "assertion count in tests/test_pager.py dropped by 2 (removed 2, added 0)",
            ],
        )
        self.assertTrue(all(f.severity == BLOCK for f in findings))

    def test_same_count_is_not_fewer(self):
        self.assertEqual(fewer_asserts.check(load_diff("weaker_asserts"), Intent()), [])

    def test_added_asserts(self):
        self.assertEqual(fewer_asserts.check(load_diff("clean"), Intent()), [])


if __name__ == "__main__":
    unittest.main()
