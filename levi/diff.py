import re
from dataclasses import dataclass, field

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
GIT_HEADER_RE = re.compile(r"^diff --git a/(.*) b/(.*)$")


@dataclass
class Line:
    tag: str
    text: str
    old_no: int = None
    new_no: int = None


@dataclass
class Hunk:
    old_start: int
    new_start: int
    lines: list = field(default_factory=list)

    def removed(self):
        return [line for line in self.lines if line.tag == "-"]

    def added(self):
        return [line for line in self.lines if line.tag == "+"]


@dataclass
class FileDiff:
    old_path: str = None
    new_path: str = None
    hunks: list = field(default_factory=list)
    binary: bool = False
    new_file: bool = False
    deleted_file: bool = False

    @property
    def status(self):
        if self.old_path is None:
            return "added"
        if self.new_path is None:
            return "deleted"
        if self.old_path != self.new_path:
            return "renamed"
        return "modified"

    @property
    def path(self):
        return self.new_path or self.old_path

    def paths(self):
        return [p for p in dict.fromkeys((self.old_path, self.new_path)) if p]

    def removed(self):
        return [line for hunk in self.hunks for line in hunk.removed()]

    def added(self):
        return [line for hunk in self.hunks for line in hunk.added()]


def _header_path(raw):
    raw = raw.split("\t")[0].strip()
    if raw == "/dev/null":
        return None
    if raw.startswith(("a/", "b/")):
        return raw[2:]
    return raw


def _finish(current):
    if current is None:
        return
    if current.new_file:
        current.old_path = None
    if current.deleted_file:
        current.new_path = None


def parse_diff(text):
    files = []
    current = None
    hunk = None
    old_left = new_left = 0
    old_no = new_no = 0
    for line in text.splitlines():
        if hunk is not None and (old_left > 0 or new_left > 0):
            tag = line[:1] or " "
            if tag == "\\":
                continue
            body = line[1:]
            if tag == "+":
                hunk.lines.append(Line("+", body, None, new_no))
                new_no += 1
                new_left -= 1
            elif tag == "-":
                hunk.lines.append(Line("-", body, old_no, None))
                old_no += 1
                old_left -= 1
            else:
                hunk.lines.append(Line(" ", body, old_no, new_no))
                old_no += 1
                new_no += 1
                old_left -= 1
                new_left -= 1
            continue
        hunk = None
        if line.startswith("diff --git "):
            _finish(current)
            current = FileDiff()
            files.append(current)
            match = GIT_HEADER_RE.match(line)
            if match:
                current.old_path, current.new_path = match.group(1), match.group(2)
        elif line.startswith("--- "):
            if current is None or current.hunks:
                _finish(current)
                current = FileDiff()
                files.append(current)
            current.old_path = _header_path(line[4:])
            if current.old_path is None:
                current.new_file = True
        elif line.startswith("+++ ") and current is not None:
            current.new_path = _header_path(line[4:])
            if current.new_path is None:
                current.deleted_file = True
        elif current is None:
            continue
        elif line.startswith("new file mode"):
            current.new_file = True
        elif line.startswith("deleted file mode"):
            current.deleted_file = True
        elif line.startswith("rename from "):
            current.old_path = line[len("rename from "):]
        elif line.startswith("rename to "):
            current.new_path = line[len("rename to "):]
        elif line.startswith("Binary files ") or line.startswith("GIT binary patch"):
            current.binary = True
        elif line.startswith("@@"):
            match = HUNK_RE.match(line)
            if match:
                old_no, new_no = int(match.group(1)), int(match.group(3))
                old_left = int(match.group(2)) if match.group(2) is not None else 1
                new_left = int(match.group(4)) if match.group(4) is not None else 1
                hunk = Hunk(old_no, new_no)
                current.hunks.append(hunk)
    _finish(current)
    return files
