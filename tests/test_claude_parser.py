import os
import tempfile
import unittest
from pathlib import Path

from levi.transcript import detect_agent, parse, parse_claude, session_files
from tests.support import CLAUDE_SESSION


class ClaudeParserTest(unittest.TestCase):
    def setUp(self):
        self.transcript = parse_claude(CLAUDE_SESSION)

    def test_reads_session_metadata(self):
        self.assertEqual(self.transcript.agent, "claude")
        self.assertEqual(self.transcript.session_id, "3f9b2c1a-8d4e-4f6a-9b0c-1d2e3f4a5b6c")
        self.assertEqual(self.transcript.cwd, "/Users/dev/projects/shop")

    def test_keeps_only_real_user_prompts(self):
        users = [m.text for m in self.transcript.user_messages()]
        self.assertEqual(len(users), 2)
        self.assertTrue(users[0].startswith("The pagination is off by one"))
        self.assertNotIn("system-reminder", users[0])
        self.assertEqual(users[1], "Also don't change CI. Keep it to at most 3 files.")

    def test_skips_sidechain_meta_commands_and_tool_results(self):
        texts = " ".join(m.text for m in self.transcript.messages)
        self.assertNotIn("README.md", texts)
        self.assertNotIn("Caveat:", texts)
        self.assertNotIn("<command-name>", texts)
        self.assertNotIn("def page_count", texts)
        self.assertNotIn("Request interrupted", texts)

    def test_merges_assistant_blocks_with_same_message_id(self):
        assistant = self.transcript.assistant_messages()
        self.assertEqual(len(assistant), 2)
        self.assertEqual(
            self.transcript.last_assistant_text(),
            "Fixed the off-by-one in `src/pager.py` (pages are 1-indexed now).\nAll 14 tests pass. Lint is clean.",
        )

    def test_detects_and_dispatches(self):
        self.assertEqual(detect_agent(CLAUDE_SESSION), "claude")
        self.assertEqual(parse(CLAUDE_SESSION).messages, self.transcript.messages)

    def test_ignores_malformed_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.jsonl"
            path.write_text('not json\n{"type":"user","sessionId":"s","message":{"role":"user","content":"hello"}}\n')
            transcript = parse_claude(path)
        self.assertEqual([m.text for m in transcript.messages], ["hello"])

    def test_session_files_newest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = Path(tmp) / "-Users-dev-a" / "old.jsonl"
            new = Path(tmp) / "-Users-dev-b" / "new.jsonl"
            for path in (old, new):
                path.parent.mkdir(parents=True)
                path.write_text("{}\n")
            os.utime(old, (1_000_000, 1_000_000))
            self.assertEqual(session_files("claude", tmp), [new, old])
        self.assertEqual(session_files("claude", "/nonexistent/levi"), [])


if __name__ == "__main__":
    unittest.main()
