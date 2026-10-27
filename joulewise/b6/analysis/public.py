"""Restricted custody and the structure-only public record (registration §12.1).

Restricted until the release: energies, powers, phase durations, floors,
means, ratios, dbar, outcome words, signs and calibration values.  Released
as structure: verdicts, counting, flag counts by code and family (a restricted
code shown only as removed), kept-unit counts, the drift screen's verdict word
and timing that is not a phase duration.

Restricted outputs are canonical JSON stored by content address
(``restricted/objects/<sha256>.json``).  The public record names them by digest
and carries structure only; :func:`require_structure_only` refuses any float,
any decimal-looking token and any outcome or replication word before a public
byte is written.  The driver prints only that record's path and digest
(stdout) and one status line per node (stderr).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

PUBLIC_RECORD = "B6-BLIND-DRY-RUN-RECORD.json"     # design §14
# Outcome and replication words (B5-PLAN §7.2, registration §11.2) are restricted.
RESTRICTED_WORDS = ("direction_supported", "not_resolvable", "unresolved", "not_estimable", "replicated")
_DECIMAL = re.compile(r"(?<![A-Za-z0-9])[+-]?(?:\d+\.\d*|\.\d+|\d+[eE][+-]?\d+)(?![A-Za-z0-9])")


class CustodyRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def canonical(value) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                          allow_nan=False).encode("ascii") + b"\n"
    except ValueError:
        raise CustodyRefusal("restricted_value_not_finite") from None


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _text_is_structure(text: str) -> bool:
    lowered = text.lower()
    return _DECIMAL.search(text) is None and not any(word in lowered for word in RESTRICTED_WORDS)


def structure_problems(value, path: str = "$") -> list[str]:
    """Every place a public value could carry a restricted number or word."""
    problems = []
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not _text_is_structure(key):
                problems.append(path + ":key")
            problems.extend(structure_problems(item, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            problems.extend(structure_problems(item, f"{path}[{index}]"))
    elif isinstance(value, float):
        problems.append(path + ":float")
    elif isinstance(value, str):
        if not _text_is_structure(value):
            problems.append(path + ":text")
    elif value is not None and not isinstance(value, (bool, int)):
        problems.append(path + ":type")
    return problems


def require_structure_only(value) -> bytes:
    if structure_problems(value):
        raise CustodyRefusal("public_record_not_structure")
    raw = canonical(value)
    if not _text_is_structure(raw.decode("ascii")):
        raise CustodyRefusal("public_record_not_structure")
    return raw


def public_token(code: str | None) -> str | None:
    """A refusal token as it may appear publicly; others become a fixed word."""
    if code is None:
        return None
    return code if re.fullmatch(r"[a-z][a-z0-9_.]*", code) and _text_is_structure(code) else "restricted_token"


def preflight(custody: Path, run_directory: str, repo_root: Path) -> Path:
    """Refuse aliases, a custody root inside the repository and a used run directory."""
    if re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", run_directory) is None:
        raise CustodyRefusal("analysis_mode_invalid")
    root = Path(custody).absolute()
    if (any(char.isspace() for char in str(root)) or ".." in root.parts or root.resolve() != root
            or any(part.is_symlink() for part in (root, *root.parents))):
        raise CustodyRefusal("custody_path_invalid")
    if root.is_relative_to(Path(repo_root).resolve()):
        raise CustodyRefusal("custody_inside_repository")
    target = root / run_directory
    if target.exists():
        raise CustodyRefusal("custody_run_directory_exists")
    return target


class Custody:
    """One run directory: ``restricted/`` for automation, the record beside it."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.restricted = self.directory / "restricted"
        self.objects = self.restricted / "objects"
        self.objects.mkdir(parents=True)
        self.roles: dict[str, str] = {}

    def put(self, role: str, value) -> str:
        raw = canonical(value)
        digest = sha256(raw)
        path = self.objects / f"{digest}.json"
        if not path.exists():
            with path.open("xb") as stream:
                stream.write(raw)
        if role in self.roles and self.roles[role] != digest:
            raise CustodyRefusal("restricted_role_written_twice")
        self.roles[role] = digest
        return digest

    def get(self, digest: str):
        raw = (self.objects / f"{digest}.json").read_bytes()
        if sha256(raw) != digest:
            raise CustodyRefusal("restricted_object_digest_mismatch")
        return json.loads(raw)

    def write_public(self, record: dict) -> tuple[Path, str]:
        raw = require_structure_only(record)
        path = self.directory / PUBLIC_RECORD
        with path.open("xb") as stream:
            stream.write(raw)
        return path, sha256(raw)
