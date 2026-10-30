import unittest

from levi.paths import is_ci_file, is_test_file, language, matches


class PathsTest(unittest.TestCase):
    def test_test_files(self):
        for path in ("tests/test_api.py", "pkg/api_test.py", "conftest.py", "src/__tests__/a.ts", "web/button.spec.tsx", "lib/x.test.mjs"):
            self.assertTrue(is_test_file(path), path)
        for path in ("src/api.py", "src/testing_utils.ts", "tests/README.md", "docs/test_plan.txt"):
            self.assertFalse(is_test_file(path), path)

    def test_ci_files(self):
        for path in (".github/workflows/ci.yml", ".gitlab-ci.yml", ".circleci/config.yml", "Jenkinsfile", "azure-pipelines.yml"):
            self.assertTrue(is_ci_file(path), path)
        self.assertFalse(is_ci_file(".github/CODEOWNERS"))

    def test_language(self):
        self.assertEqual(language("a/b.py"), "python")
        self.assertEqual(language("a/b.tsx"), "js")
        self.assertIsNone(language("a/b.go"))

    def test_matches(self):
        self.assertTrue(matches("src/auth/session.py", "src/auth/"))
        self.assertTrue(matches("src/auth/session.py", "src/auth"))
        self.assertTrue(matches("src/auth/session.py", "auth/"))
        self.assertTrue(matches("src/pager.py", "pager.py"))
        self.assertTrue(matches("src/pager.py", "./src/pager.py"))
        self.assertTrue(matches("src/api/v1/users.ts", "src/api/*.ts"))
        self.assertFalse(matches("src/authz/rules.py", "src/auth/"))
        self.assertFalse(matches("src/pager.py", "tests/test_pager.py"))


if __name__ == "__main__":
    unittest.main()
