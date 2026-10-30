from dataclasses import asdict, dataclass

BLOCK = "block"
WARN = "warn"


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    message: str
    line: int = None

    def to_dict(self):
        return asdict(self)
