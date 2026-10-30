import json
import tempfile
import unittest
from pathlib import Path

from levi.transcript import detect_agent, parse, parse_codex
from tests.support import CODEX_LEGACY_SESSION, CODEX_SESSION

PROMPT = (
    "Add a `--dry-run` flag to the export command in cli/export.ts. Don't modify the tests and don't touch "
    "anything outside cli/. Never edit .github/workflows/release.yml. You can also update README.md if needed."
)


class CodexParserTest(unittest.TestCase):
    def test_rollout_metadata(self):
        transcript = parse_codex(CODEX_SESSION)
        self.assertEqual(transcript.agent, "codex")
        self.assertEqual(transcript.session_id, "0199f3a2-7c41-7e10-9a2b-3c4d5e6f7a8b")
        self.assertEqual(transcript.cwd, "/Users/dev/projects/exporter")

    def test_rollout_skips_injected_context_and_event_duplicates(self):
        transcript = parse_codex(CODEX_SESSION)
        self.assertEqual([m.text for m in transcript.user_messages()], [PROMPT])
        self.assertEqual(len(transcript.assistant_messages()), 2)
        self.assertEqual(
            transcript.last_assistant_text(),
            "Added `--dry-run` to cli/export.ts. The test suite passes and the typecheck is clean.",
        )

    def test_legacy_rollout(self):
        transcript = parse_codex(CODEX_LEGACY_SESSION)
        self.assertEqual(transcript.session_id, "5b1c2d3e-4f5a-6b7c-8d9e-0f1a2b3c4d5e")
        self.assertEqual(
            [m.text for m in transcript.user_messages()],
            ["The tokenizer chokes on escaped quotes. Only change lib/parser.py. Leave the CI pipeline alone."],
        )
        self.assertEqual(transcript.last_assistant_text(), "Fixed escaped-quote handling in lib/parser.py. All tests are green.")

    def test_falls_back_to_event_messages(self):
        records = [
            {"timestamp": "t0", "type": "session_meta", "payload": {"id": "abc", "cwd": "/w"}},
            {"timestamp": "t1", "type": "event_msg", "payload": {"type": "user_message", "message": "only edit app.py"}},
            {"timestamp": "t2", "type": "event_msg", "payload": {"type": "agent_message", "message": "done"}},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout.jsonl"
            path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
            transcript = parse(path)
        self.assertEqual(transcript.agent, "codex")
        self.assertEqual([(m.role, m.text) for m in transcript.messages], [("user", "only edit app.py"), ("assistant", "done")])

    def test_detects_codex(self):
        self.assertEqual(detect_agent(CODEX_SESSION), "codex")
        self.assertEqual(detect_agent(CODEX_LEGACY_SESSION), "codex")
        self.assertEqual(parse(CODEX_LEGACY_SESSION).agent, "codex")


if __name__ == "__main__":
    unittest.main()
