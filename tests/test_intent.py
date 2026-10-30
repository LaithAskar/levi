import json
import tempfile
import unittest
from pathlib import Path

from levi.intent import extract_intent, find_paths, split_clauses
from levi.transcript import parse
from tests.support import CLAUDE_SESSION, CODEX_LEGACY_SESSION, CODEX_SESSION, chat


class FixtureIntentTest(unittest.TestCase):
    def test_claude_session(self):
        intent = extract_intent(parse(CLAUDE_SESSION))
        self.assertEqual(intent.allowed, ["src/pager.py", "tests/test_pager.py"])
        self.assertEqual(intent.forbidden, ["src/auth/", "src/db/lock.py"])
        self.assertTrue(intent.protect_ci)
        self.assertFalse(intent.protect_tests)
        self.assertEqual(intent.max_files, 3)
        self.assertEqual([(c.kind, c.final) for c in intent.claims], [("tests_pass", True), ("lint_pass", True)])

    def test_claude_session_ignores_code_fences_and_subagents(self):
        intent = extract_intent(parse(CLAUDE_SESSION))
        self.assertNotIn("src/billing.py", intent.forbidden)
        self.assertNotIn("README.md", intent.allowed)

    def test_codex_session(self):
        intent = extract_intent(parse(CODEX_SESSION))
        self.assertTrue(intent.protect_tests)
        self.assertFalse(intent.protect_ci)
        self.assertEqual(intent.allowed, ["cli/", "README.md"])
        self.assertEqual(intent.forbidden, [".github/workflows/release.yml"])
        self.assertEqual([(c.kind, c.final) for c in intent.claims], [("tests_pass", True), ("typecheck_pass", True)])

    def test_codex_legacy_session(self):
        intent = extract_intent(parse(CODEX_LEGACY_SESSION))
        self.assertEqual(intent.allowed, ["lib/parser.py"])
        self.assertTrue(intent.protect_ci)
        self.assertEqual([c.kind for c in intent.claims], ["tests_pass"])

    def test_writes_intent_json(self):
        intent = extract_intent(parse(CLAUDE_SESSION))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.json"
            intent.write(path)
            data = json.loads(path.read_text())
        self.assertEqual(data["forbidden"], ["src/auth/", "src/db/lock.py"])
        self.assertEqual(data["claims"][0]["kind"], "tests_pass")
        self.assertIn("protect_ci", {c["kind"] for c in data["constraints"]})


class PhraseIntentTest(unittest.TestCase):
    def test_leave_alone(self):
        self.assertEqual(extract_intent(chat(("user", "Please leave src/legacy alone."))).forbidden, ["src/legacy"])

    def test_anything_except_is_an_allowlist(self):
        intent = extract_intent(chat(("user", "Don't touch anything except src/api/ and docs/.")))
        self.assertEqual(intent.allowed, ["src/api/", "docs/"])
        self.assertEqual(intent.forbidden, [])

    def test_absolute_paths_are_relativized(self):
        intent = extract_intent(chat(("user", "Only edit /repo/app/models.py"), cwd="/repo"))
        self.assertEqual(intent.allowed, ["app/models.py"])

    def test_test_paths_do_not_protect_all_tests(self):
        intent = extract_intent(chat(("user", "Don't edit tests/fixtures/.")))
        self.assertEqual(intent.forbidden, ["tests/fixtures/"])
        self.assertFalse(intent.protect_tests)

    def test_max_files(self):
        self.assertEqual(extract_intent(chat(("user", "Change no more than two files."))).max_files, 2)
        self.assertEqual(extract_intent(chat(("user", "Use fewer than 3 files."))).max_files, 2)
        self.assertEqual(extract_intent(chat(("user", "Fix it in a single file."))).max_files, 1)

    def test_later_permission_lifts_test_protection(self):
        intent = extract_intent(chat(("user", "Don't touch the tests."), ("user", "OK, you can update the tests now.")))
        self.assertFalse(intent.protect_tests)

    def test_permission_without_scope_does_not_create_allowlist(self):
        self.assertEqual(extract_intent(chat(("user", "Feel free to edit docs/guide.md."))).allowed, [])

    def test_permission_removes_forbidden_path(self):
        intent = extract_intent(chat(("user", "Never touch config.yaml."), ("user", "Actually you may edit config.yaml.")))
        self.assertEqual(intent.forbidden, [])

    def test_unscoped_constraint_is_recorded(self):
        intent = extract_intent(chat(("user", "Don't change the lock ordering.")))
        self.assertEqual(intent.forbidden, [])
        self.assertEqual([(c.kind, c.paths) for c in intent.constraints], [("forbid", [])])

    def test_urls_and_slash_words_are_not_paths(self):
        found, _ = find_paths("see https://example.com/docs/api.md and/or the client in web/client.ts")
        self.assertEqual([p for p, _ in found], ["web/client.ts"])

    def test_clause_splitting(self):
        self.assertEqual(
            split_clauses("Fix the parser, but don't touch lexer.py and only edit parser.py"),
            ["Fix the parser", "don't touch lexer.py", "only edit parser.py"],
        )

    def test_negated_claims_are_ignored(self):
        intent = extract_intent(chat(("assistant", "I haven't checked whether tests pass."), ("assistant", "Build succeeded.")))
        self.assertEqual([c.kind for c in intent.claims], ["build_pass"])

    def test_user_text_is_not_a_claim(self):
        self.assertEqual(extract_intent(chat(("user", "All tests pass on main."))).claims, [])


if __name__ == "__main__":
    unittest.main()
