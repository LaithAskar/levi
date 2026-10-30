import json
import re
from dataclasses import dataclass, field
from pathlib import Path

CLAUDE_ROOT = Path.home() / ".claude" / "projects"
CODEX_ROOT = Path.home() / ".codex" / "sessions"

INJECTED_PREFIXES = (
    "<command-name>",
    "<command-message>",
    "<command-args>",
    "<local-command-stdout>",
    "<local-command-stderr>",
    "<bash-input>",
    "<bash-stdout>",
    "<bash-stderr>",
    "<environment_context>",
    "<user_instructions>",
    "<user_shell_command>",
    "<turn_aborted>",
    "# AGENTS.md instructions",
    "Caveat: The messages below were generated",
    "[Request interrupted by user",
)
REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
CODEX_RECORD_TYPES = {"session_meta", "response_item", "event_msg", "turn_context", "compacted"}


@dataclass
class Message:
    role: str
    text: str
    timestamp: str = ""


@dataclass
class Transcript:
    agent: str
    path: str
    session_id: str = ""
    cwd: str = ""
    messages: list = field(default_factory=list)

    def user_messages(self):
        return [m for m in self.messages if m.role == "user"]

    def assistant_messages(self):
        return [m for m in self.messages if m.role == "assistant"]

    def last_assistant_text(self):
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message.text
        return ""


def _read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def _clean_user_text(text):
    text = REMINDER_RE.sub("", text).strip()
    if not text or text.startswith(INJECTED_PREFIXES):
        return ""
    return text


def _block_text(content, block_types):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") in block_types:
            parts.append(block.get("text") or "")
    return "\n".join(parts)


def parse_claude(path):
    transcript = Transcript(agent="claude", path=str(path))
    last_message_id = None
    for record in _read_jsonl(path):
        if not transcript.session_id and record.get("sessionId"):
            transcript.session_id = record["sessionId"]
        if not transcript.cwd and record.get("cwd"):
            transcript.cwd = record["cwd"]
        kind = record.get("type")
        if kind not in ("user", "assistant"):
            continue
        if record.get("isSidechain") or record.get("isMeta") or record.get("isCompactSummary"):
            continue
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        text = _block_text(message.get("content"), {"text"})
        timestamp = record.get("timestamp", "")
        if kind == "user":
            last_message_id = None
            text = _clean_user_text(text)
            if text:
                transcript.messages.append(Message("user", text, timestamp))
            continue
        message_id = message.get("id")
        text = text.strip()
        if text:
            previous = transcript.messages[-1] if transcript.messages else None
            if message_id and message_id == last_message_id and previous and previous.role == "assistant":
                previous.text = previous.text + "\n" + text
            else:
                transcript.messages.append(Message("assistant", text, timestamp))
        last_message_id = message_id
    return transcript


def parse_codex(path):
    transcript = Transcript(agent="codex", path=str(path))
    items = []
    events = []
    for record in _read_jsonl(path):
        kind = record.get("type")
        payload = record.get("payload") if isinstance(record.get("payload"), dict) else None
        timestamp = record.get("timestamp", "")
        if kind == "session_meta" and payload:
            transcript.session_id = transcript.session_id or payload.get("id", "")
            transcript.cwd = transcript.cwd or payload.get("cwd", "")
        elif kind == "turn_context" and payload:
            transcript.cwd = transcript.cwd or payload.get("cwd", "")
        elif kind == "response_item" and payload:
            items.append((payload, timestamp))
        elif kind == "event_msg" and payload:
            events.append((payload, timestamp))
        elif kind == "message":
            items.append((record, timestamp))
        elif kind is None and "id" in record and "instructions" in record:
            transcript.session_id = transcript.session_id or record.get("id", "")
    for payload, timestamp in items:
        if payload.get("type") != "message" or payload.get("role") not in ("user", "assistant"):
            continue
        role = payload["role"]
        text = _block_text(payload.get("content"), {"input_text", "output_text", "text"})
        text = _clean_user_text(text) if role == "user" else text.strip()
        if text:
            transcript.messages.append(Message(role, text, timestamp))
    if not transcript.messages:
        for payload, timestamp in events:
            role = {"user_message": "user", "agent_message": "assistant"}.get(payload.get("type"))
            if not role:
                continue
            text = payload.get("message") or ""
            text = _clean_user_text(text) if role == "user" else text.strip()
            if text:
                transcript.messages.append(Message(role, text, timestamp))
    return transcript


def detect_agent(path):
    for index, record in enumerate(_read_jsonl(path)):
        if record.get("type") in CODEX_RECORD_TYPES or "payload" in record or "record_type" in record:
            return "codex"
        if "instructions" in record and "id" in record:
            return "codex"
        if "sessionId" in record or "uuid" in record or "leafUuid" in record:
            return "claude"
        if index >= 20:
            break
    return "claude"


def parse(path):
    if detect_agent(path) == "codex":
        return parse_codex(path)
    return parse_claude(path)


def session_files(agent, root=None):
    if root is None:
        root = CODEX_ROOT if agent == "codex" else CLAUDE_ROOT
    root = Path(root)
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
