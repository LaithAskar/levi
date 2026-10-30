import re

COMMENT_RE = {"python": re.compile(r"^\s*#"), "js": re.compile(r"^\s*(?://|/\*|\*)")}

ASSERT_RES = {
    "python": re.compile(r"^\s*assert\b|\bself\.assert[A-Z]\w*\s*\(|\bself\.fail\s*\(|\bpytest\.raises\s*\(|\bassert_\w+\s*\("),
    "js": re.compile(r"\bexpect\s*\(|\bassert(?:\.\w+)?\s*\(|\.should\b"),
}

SKIP_RES = {
    "python": re.compile(
        r"@pytest\.mark\.(?:skip|skipif|xfail)\b|@(?:unittest\.)?(?:skip|skipIf|skipUnless|expectedFailure)\b"
        r"|\bpytest\.(?:skip|xfail)\s*\(|\bself\.skipTest\s*\(|\braise\s+(?:unittest\.)?SkipTest\b"
    ),
    "js": re.compile(
        r"\b(?:it|test|describe|context|suite)(?:\.each\([^)]*\))?\.(?:skip|todo|only|skipIf|fails)\b"
        r"|(?<![\w.])(?:xit|xtest|xdescribe|xcontext|fit|fdescribe|ftest)\s*\("
    ),
}

TEST_DEF_RES = {
    "python": re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)\s*\("),
    "js": re.compile(r"(?<![\w.])[xf]?(?:it|test)(?:\.\w+)?\s*\(\s*(['\"`])(.+?)\1"),
}

PY_TRIVIAL_RE = re.compile(r"^\s*assert\s+(?:True|1|not\s+(?:False|None|0))\s*(?:,|#|$)|\bself\.assertTrue\(\s*(?:True|1)\s*[,)]")
JS_TRIVIAL_RE = re.compile(
    r"\bexpect\(\s*(true|1|false|null)\s*\)\.(?:toBe|toEqual|toStrictEqual)\(\s*\1\s*\)"
    r"|\bexpect\(\s*(?:true|1)\s*\)\.toBeTruthy\(\s*\)|\bassert(?:\.ok)?\(\s*(?:true|1)\s*\)"
)
PY_EXACT = r"assert(?:Equal|Equals|ListEqual|DictEqual|TupleEqual|SetEqual|SequenceEqual|MultiLineEqual|CountEqual|Is|IsNone)"
PY_MEDIUM = r"assert(?:NotEqual|In|NotIn|Greater|GreaterEqual|Less|LessEqual|AlmostEqual|NotAlmostEqual|Regex|NotRegex|IsNot|NotIsInstance|Raises|RaisesRegex|Warns|Logs)"
PY_WEAK = r"assert(?:True|False|IsNotNone|IsInstance)"
BROAD_EXCEPTIONS = r"(?:Exception|BaseException|Error)"
JS_EXACT = (
    r"\.(?:toBe|toEqual|toStrictEqual|toBeNull|toBeUndefined|toBeNaN|toHaveBeenCalledWith|toHaveBeenLastCalledWith|"
    r"toHaveBeenNthCalledWith|toHaveBeenCalledTimes|toMatchSnapshot|toMatchInlineSnapshot|toHaveLength)\(|\.toThrow\(\s*[^)\s]"
)
JS_MEDIUM = (
    r"\.(?:toContain|toContainEqual|toMatch|toMatchObject|toBeGreaterThan|toBeGreaterThanOrEqual|toBeLessThan|"
    r"toBeLessThanOrEqual|toBeCloseTo|toHaveProperty|toBeInstanceOf|toThrowError|rejects|resolves)\b"
)
JS_WEAK = r"\.(?:toBeTruthy|toBeFalsy|toBeDefined)\(|\.toHaveBeenCalled\(\s*\)|\.toThrow\(\s*\)"
JS_ASSERT_EXACT = r"\bassert\.(?:equal|strictEqual|deepEqual|deepStrictEqual|throws|rejects)\("


def is_comment(line, lang):
    pattern = COMMENT_RE.get(lang)
    return bool(pattern and pattern.match(line))


def count_asserts(line, lang):
    pattern = ASSERT_RES.get(lang)
    if not pattern or is_comment(line, lang):
        return 0
    return len(pattern.findall(line))


def skip_marker(line, lang):
    pattern = SKIP_RES.get(lang)
    if not pattern or is_comment(line, lang):
        return None
    match = pattern.search(line)
    return match.group(0) if match else None


def test_names(line, lang):
    pattern = TEST_DEF_RES.get(lang)
    if not pattern or is_comment(line, lang):
        return []
    if lang == "python":
        return [m.group(1) for m in pattern.finditer(line)]
    return [m.group(2) for m in pattern.finditer(line)]


def _python_strength(line):
    if PY_TRIVIAL_RE.search(line):
        return 0
    if re.search(rf"\b(?:self\.assertRaises|pytest\.raises)\(\s*{BROAD_EXCEPTIONS}\s*[,)]", line):
        return 1
    if re.search(r"\b(?:self\.assertRaises|pytest\.raises)\(", line):
        return 3
    if re.search(rf"\bself\.{PY_EXACT}\(", line):
        return 3
    if re.search(rf"\bself\.{PY_MEDIUM}\(", line):
        return 2
    if re.search(rf"\bself\.{PY_WEAK}\(", line):
        return 1
    statement = re.match(r"^\s*assert\s+(.*)$", line)
    if statement:
        body = statement.group(1)
        if re.search(r"\bis\s+not\s+None\b", body) or re.match(r"\s*(?:not\s+|isinstance\(|bool\(|len\([^)]*\)\s*$)", body):
            return 1
        if re.search(r"==|\bis\b", body):
            return 3
        if re.search(r"!=|<|>|\bin\b", body):
            return 2
        return 1
    return 2


def _js_strength(line):
    if JS_TRIVIAL_RE.search(line):
        return 0
    negated = ".not." in line
    if re.search(r"\.not\.(?:toBeNull|toBeUndefined)\(", line):
        return 1
    if re.search(JS_WEAK, line):
        return 1
    if re.search(JS_EXACT, line) or re.search(JS_ASSERT_EXACT, line):
        return 2 if negated else 3
    if re.search(JS_MEDIUM, line):
        return 2
    if re.search(r"\bassert(?:\.ok)?\(", line):
        return 1
    return 2


def assert_strength(line, lang):
    if lang == "python":
        return _python_strength(line)
    if lang == "js":
        return _js_strength(line)
    return 2
