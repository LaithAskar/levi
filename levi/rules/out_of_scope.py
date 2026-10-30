from levi.findings import BLOCK, Finding
from levi.paths import matches

NAME = "out_of_scope"


def check(files, intent):
    findings = []
    if intent.allowed:
        for diff in files:
            if any(matches(path, p) for path in diff.paths() for p in intent.forbidden):
                continue
            outside = [path for path in diff.paths() if not any(matches(path, p) for p in intent.allowed)]
            if outside:
                scope = ", ".join(intent.allowed)
                findings.append(Finding(NAME, BLOCK, outside[0], f"{diff.status} {outside[0]}, which is outside the agreed scope ({scope})"))
    if intent.max_files is not None and len(files) > intent.max_files:
        findings.append(Finding(NAME, BLOCK, "", f"changed {len(files)} files, but the limit was {intent.max_files}"))
    return findings
