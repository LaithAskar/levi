import unittest

from levi.diff import parse_diff
from tests.support import load_diff


class DiffParserTest(unittest.TestCase):
    def test_statuses_and_paths(self):
        files = load_diff("scope")
        self.assertEqual(
            [(f.path, f.status) for f in files],
            [
                ("docs/pagination.md", "added"),
                ("src/auth/session.py", "modified"),
                ("src/db/lock.py", "modified"),
                ("src/pager.py", "modified"),
                ("src/utils/strings.py", "modified"),
            ],
        )

    def test_line_numbers(self):
        lock = load_diff("scope")[2]
        self.assertEqual([(l.old_no, l.text) for l in lock.removed()], [(8, "    with _accounts:"), (9, "        with _ledger:")])
        self.assertEqual([l.new_no for l in lock.added()], [8, 9])

    def test_deleted_file(self):
        deleted = [f for f in load_diff("deleted_tests") if f.status == "deleted"]
        self.assertEqual([f.old_path for f in deleted], ["tests/test_lock.py"])
        self.assertEqual(len(deleted[0].removed()), 19)
        self.assertEqual(deleted[0].added(), [])

    def test_rename_without_hunks(self):
        files = parse_diff(
            "diff --git a/tests/test_old.py b/lib/old_helpers.py\n"
            "similarity index 100%\n"
            "rename from tests/test_old.py\n"
            "rename to lib/old_helpers.py\n"
        )
        self.assertEqual((files[0].old_path, files[0].new_path, files[0].status), ("tests/test_old.py", "lib/old_helpers.py", "renamed"))

    def test_removed_line_that_looks_like_a_header(self):
        files = parse_diff(
            "diff --git a/db/schema.sql b/db/schema.sql\n"
            "index 1111111..2222222 100644\n"
            "--- a/db/schema.sql\n"
            "+++ b/db/schema.sql\n"
            "@@ -1,2 +1,1 @@\n"
            "--- legacy table\n"
            " CREATE TABLE users (id int);\n"
            "\\ No newline at end of file\n"
        )
        self.assertEqual(len(files), 1)
        self.assertEqual([l.text for l in files[0].removed()], ["-- legacy table"])

    def test_binary_and_plain_unified_diff(self):
        binary = parse_diff("diff --git a/logo.png b/logo.png\nindex 1..2 100644\nBinary files a/logo.png and b/logo.png differ\n")
        self.assertTrue(binary[0].binary)
        plain = parse_diff("--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a = 1\n+a = 2\n--- a/y.py\n+++ b/y.py\n@@ -1 +1 @@\n-b = 1\n+b = 2\n")
        self.assertEqual([f.path for f in plain], ["x.py", "y.py"])
        self.assertEqual(plain[1].added()[0].text, "b = 2")


if __name__ == "__main__":
    unittest.main()
