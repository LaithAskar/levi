import json
import re
from dataclasses import asdict, dataclass, field

from levi.paths import normalize

VERB = (
    r"(?:touch(?:es|ing)?|modify(?:ing)?|modifies|chang(?:e|es|ing)|edit(?:s|ing)?|alter(?:s|ing)?|"
    r"rewrit(?:e|es|ing)|refactor(?:s|ing)?|updat(?:e|es|ing)|mess(?:ing)?\s+with|renam(?:e|es|ing)|mov(?:e|es|ing))"
)
NEG = (
    r"(?:don'?t|do\s+not|never|avoid|without|must\s+not|mustn'?t|shouldn'?t|should\s+not|"
    r"can'?t|cannot|not\s+allowed\s+to|no\s+need\s+to)"
)
TRIGGER = r"(?:don'?t|do\s+not|never|only|just|leave|keep|avoid|please|stay|limit|restrict|you\s+can|you\s+may|feel\s+free)"
SPLIT_RE = re.compile(
    rf"(?<=[.!?])\s+|[;\n]+|,\s*(?:and\s+|but\s+|then\s+)?(?={TRIGGER}\b)|\s+(?:and|but|then)\s+(?={TRIGGER}\b)",
    re.I,
)
FENCE_RE = re.compile(r"```.*?```", re.S)

PERMIT_RE = re.compile(
    rf"\b(?:you\s+(?:can|may)(?:\s+also)?|feel\s+free\s+to|go\s+ahead\s+and|(?:it'?s\s+)?(?:ok|okay|fine)\s+to|allowed\s+to)\s+(?:\w+\s+){{0,2}}?{VERB}\b",
    re.I,
)
EXCEPT_RE = re.compile(
    rf"\b(?:{NEG}\b.*?\b{VERB}\b.*?\b(?:anything|any\s+(?:other\s+)?files?|other\s+files?|files?)|nothing)\s+"
    r"(?:except(?:\s+for)?|other\s+than|besides|outside(?:\s+of)?|but|apart\s+from|beyond)\b",
    re.I,
)
FORBID_RES = [
    re.compile(rf"\b{NEG}\b.*?\b{VERB}\b", re.I),
    re.compile(r"\bleave\b.*?\b(?:alone|as[\s-]is|untouched|unchanged|intact|be)\b", re.I),
    re.compile(r"\bkeep\b.*?\b(?:unchanged|untouched|intact|as[\s-]is)\b", re.I),
    re.compile(r"\b(?:off[\s-]limits|read[\s-]only|hands\s+off|frozen)\b", re.I),
]
ALLOW_RES = [
    re.compile(rf"\b(?:only|just|solely|exclusively)\b.*?\b(?:{VERB}|fix(?:es|ing)?|work(?:ing)?|implement(?:ing)?|patch(?:ing)?|stay)\b", re.I),
    re.compile(rf"\b{VERB}\b.*?\bonly\b", re.I),
    re.compile(r"\b(?:limit|restrict|confine|scope|keep)\b.*?\b(?:changes?|edits?|diff|work|yourself)\b.*?\b(?:to|in|within|inside)\b", re.I),
    re.compile(r"\bstay\s+(?:with)?in\b", re.I),
]
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
MAX_FILES_RE = re.compile(
    r"\b(at\s+most|no\s+more\s+than|max(?:imum)?(?:\s+of)?|up\s+to|fewer\s+than|less\s+than|under)\s+"
    r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+files?\b",
    re.I,
)
SINGLE_FILE_RE = re.compile(r"\b(?:a\s+single|only\s+one|just\s+one|one)\s+file\s+only\b|\b(?:a\s+single|only\s+one|just\s+one)\s+file\b", re.I)
TESTS_RE = re.compile(r"\b(?:tests?|test\s+(?:files?|suites?|cases?)|specs?|assert(?:ion)?s?)\b", re.I)
CI_RE = re.compile(r"\b(?:ci|ci/cd|github\s+actions|workflows?|pipelines?)\b", re.I)

CODE_EXT = (
    r"py|pyi|js|jsx|ts|tsx|mjs|cjs|mts|cts|json|ya?ml|toml|ini|cfg|md|txt|lock|sh|go|rs|java|kt|rb|php|"
    r"c|h|cc|cpp|hpp|cs|swift|css|scss|html|sql|graphql|proto|xml|gradle|vue|svelte"
)
FILENAME_RE = re.compile(rf"[\w.*-]*\.(?:{CODE_EXT})", re.I)
BARE_FILENAMES = {"Makefile", "Dockerfile", "Jenkinsfile", "Procfile", "Gemfile", "Rakefile"}
PATH_TOKEN_RE = re.compile(r"`([^`\s]+)`|(?<![\w@:/.\-`])((?:\.{1,2}/|/|~/)?[\w.*\-]+(?:/[\w.*\-]+)*/?)")
SLASH_WORDS = {"and/or", "either/or", "input/output", "read/write", "true/false", "yes/no", "on/off", "n/a", "w/", "w/o", "i/o", "client/server", "ci/cd"}

CLAIM_PATTERNS = [
    ("tests_pass", re.compile(
        r"\b(?:all\s+)?(?:\d+\s+)?(?:the\s+)?(?:unit\s+|integration\s+)?tests?\s+(?:now\s+|all\s+|still\s+)?"
        r"(?:pass(?:es|ed|ing)?|are\s+(?:all\s+)?(?:passing|green)|succeed(?:s|ed)?|green)\b"
        r"|\btest\s+suite\s+(?:now\s+)?(?:passes|passed|is\s+green)\b|\b\d+\s+passed\b",
        re.I,
    )),
    ("build_pass", re.compile(r"\bbuild\s+(?:now\s+)?(?:passes|passed|succeeds|succeeded|is\s+green)\b", re.I)),
    ("lint_pass", re.compile(r"\blint(?:er|ing)?\s+(?:now\s+)?(?:passes|passed|is\s+clean|clean)\b", re.I)),
    ("typecheck_pass", re.compile(r"\btype[\s-]?check(?:s|ing|er)?\s+(?:now\s+)?(?:passes|passed|is\s+clean|clean)\b", re.I)),
]
CLAIM_NEGATION_RE = re.compile(r"\b(?:not|never|unsure|whether|if|until|unless|no\s+longer)\b|n't\b", re.I)
SENTENCE_RE = re.compile(r"[^.!?\n]+[.!?]?")


@dataclass
class Constraint:
    kind: str
    text: str
    paths: list = field(default_factory=list)


@dataclass
class Claim:
    kind: str
    text: str
    message_index: int
    final: bool


@dataclass
class Intent:
    allowed: list = field(default_factory=list)
    forbidden: list = field(default_factory=list)
    protect_tests: bool = False
    protect_ci: bool = False
    max_files: int = None
    constraints: list = field(default_factory=list)
    claims: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def write(self, path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.to_json() + "\n")


def _clean_path(token, cwd):
    token = token.strip().strip("\"'(").rstrip(".,:;!?)\"'")
    if not token or "://" in token or token.lower() in SLASH_WORDS:
        return None
    name = token.rstrip("/").rsplit("/", 1)[-1]
    if "/" in token:
        if not re.search(r"[A-Za-z]", token):
            return None
    elif name not in BARE_FILENAMES and not FILENAME_RE.fullmatch(name):
        return None
    return normalize(token, cwd) or None


def find_paths(text, cwd=""):
    found = []
    masked = []
    last = 0
    for match in PATH_TOKEN_RE.finditer(text):
        path = _clean_path(match.group(1) or match.group(2), cwd)
        if not path:
            continue
        found.append((path, match.start()))
        masked.append(text[last:match.start()])
        masked.append(" PATH ")
        last = match.end()
    masked.append(text[last:])
    return found, "".join(masked)


def split_clauses(text):
    text = FENCE_RE.sub(" ", text.replace("’", "'"))
    return [part.strip() for part in SPLIT_RE.split(text) if part and part.strip()]


def _max_files(clause):
    match = MAX_FILES_RE.search(clause)
    if match:
        raw = match.group(2).lower()
        value = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
        if match.group(1).lower().startswith(("fewer", "less", "under")):
            value -= 1
        return max(value, 0)
    if SINGLE_FILE_RE.search(clause):
        return 1
    return None


def _add(items, values):
    for value in values:
        if value not in items:
            items.append(value)


def _extract_claims(transcript):
    claims = []
    assistant = transcript.assistant_messages()
    for index, message in enumerate(assistant):
        for sentence in SENTENCE_RE.findall(message.text):
            for kind, pattern in CLAIM_PATTERNS:
                match = pattern.search(sentence)
                if match and not CLAIM_NEGATION_RE.search(sentence[:match.start()]):
                    claims.append(Claim(kind, sentence.strip(), index, index == len(assistant) - 1))
    return claims


def extract_intent(transcript):
    intent = Intent()
    permitted = []
    cwd = transcript.cwd
    for message in transcript.user_messages():
        for clause in split_clauses(message.text):
            found, masked = find_paths(clause, cwd)
            paths = [path for path, _ in found]
            limit = _max_files(masked)
            if limit is not None:
                intent.max_files = limit if intent.max_files is None else min(intent.max_files, limit)
                intent.constraints.append(Constraint("max_files", clause))
            if PERMIT_RE.search(masked) and not re.search(rf"\b{NEG}\b", masked, re.I):
                _add(permitted, paths)
                intent.forbidden = [p for p in intent.forbidden if p not in paths]
                if TESTS_RE.search(masked):
                    intent.protect_tests = False
                if CI_RE.search(masked):
                    intent.protect_ci = False
                intent.constraints.append(Constraint("permit", clause, paths))
                continue
            exception = EXCEPT_RE.search(clause)
            if exception:
                _add(intent.allowed, [p for p, start in found if start >= exception.end()])
                _add(intent.forbidden, [p for p, start in found if start < exception.start()])
                intent.constraints.append(Constraint("allow", clause, paths))
                continue
            if any(pattern.search(masked) for pattern in FORBID_RES):
                _add(intent.forbidden, paths)
                if TESTS_RE.search(masked):
                    intent.protect_tests = True
                    intent.constraints.append(Constraint("protect_tests", clause))
                if CI_RE.search(masked):
                    intent.protect_ci = True
                    intent.constraints.append(Constraint("protect_ci", clause))
                if paths or not (TESTS_RE.search(masked) or CI_RE.search(masked)):
                    intent.constraints.append(Constraint("forbid", clause, paths))
                continue
            if paths and any(pattern.search(masked) for pattern in ALLOW_RES):
                _add(intent.allowed, paths)
                intent.constraints.append(Constraint("allow", clause, paths))
    if intent.allowed:
        _add(intent.allowed, permitted)
    intent.claims = _extract_claims(transcript)
    return intent
