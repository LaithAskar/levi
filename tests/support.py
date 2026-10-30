from pathlib import Path

from levi.diff import parse_diff
from levi.transcript import Message, Transcript

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLAUDE_SESSION = FIXTURES / "claude" / "pager_session.jsonl"
CODEX_SESSION = FIXTURES / "codex" / "rollout-2026-10-21T09-14-03-dry-run.jsonl"
CODEX_LEGACY_SESSION = FIXTURES / "codex" / "rollout-2025-08-02T17-40-11-legacy.jsonl"


def load_diff(name):
    return parse_diff((FIXTURES / "diffs" / f"{name}.diff").read_text())


def chat(*turns, cwd=""):
    messages = [Message(role, text) for role, text in turns]
    return Transcript(agent="claude", path="", cwd=cwd, messages=messages)
