#!/usr/bin/env python3
"""Census every hard-coded SHA-256 literal in tests/ and configs/.

Lane L7 (Ed's point c, 2026-10-05). Hard-coded digests are of two kinds:

- Kind P protects a number. It pins measured raw data, an issued artifact
  (acceptance file, floor, prompt pin), the estimator code an acceptance was
  issued against, a sealed registration, pack config bytes, or a production
  paper-supply role. It stays hard-coded, is checked in CI by
  ``scripts/repin.py --check``, and is never repinned automatically.
- Kind B is busywork. It pins something no number depends on: synthetic
  fixture envelopes, placeholders, digests of source code outside the
  measurement core, outputs of deterministic generators. It either cannot go
  stale (it hashes immutable synthetic bytes) or it should be computed at test
  time instead of written down.

The census finds every 64-hex literal, records where it sits (a JSON pointer
for JSON files, ``#L<line>`` otherwise), resolves it against the tree, sorts it
into a family, and writes ``configs/pins/registry.json``. A literal is
resolved against, in order:

1. ``file``: SHA-256 of a tracked file's bytes;
2. ``git_blob``: SHA-256 of a tracked file framed as a Git blob;
3. ``canonical_json``: SHA-256 of a tracked JSON file's canonical encoding
   (sorted keys, compact separators; with or without a final newline, with
   or without ASCII escaping);
4. ``py_def`` / ``py_segment``: SHA-256 of one Python definition's source,
   decorator-inclusive lines (``inspect.getsource`` form) or the bare
   ``ast.get_source_segment`` form.

Resolved Kind-P rows are what ``repin.py --check`` re-verifies: it recomputes
the target's digest by the recorded method and requires the pinning file to
still carry it. Unresolved literals (raw data never committed, historical
digests) are recorded but cannot be recomputed from the tree.

Era records (``ERA_RECORDS``) are documents that record bytes as they were at
a commit they declare. Literals in a record's declared scope resolve against
the files at that commit instead of today's tree; their target key carries
``@<commit>`` and ``repin.py --check`` re-reads the bytes with ``git show``.

Usage::

    python scripts/digest_pin_census.py            # print a summary
    python scripts/digest_pin_census.py --write    # rewrite configs/pins/registry.json
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_REL = "configs/pins/registry.json"
SCHEMA = "joulewise.pin_registry.v1"
SCOPE = ("tests/", "configs/")
HEX64 = re.compile(r"(?<![0-9A-Fa-f])[0-9a-f]{64}(?![0-9A-Fa-f])")

# The protected measurement core (gate-prune plan §5.1). A digest of any of
# these files, or of a definition in them, protects a number wherever it sits.
MEASUREMENT_CORE = frozenset({
    "joulewise/reduce.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/powermetrics_fiducial.py",
    "joulewise/adapters/powermetrics.py",
    "joulewise/controller.py",
    "joulewise/bundle.py",
    "joulewise/whole_window.py",
    "scripts/run_campaign.py",
    "scripts/validate_powermetrics_fiducial.py",
})
# Issued modules outside the core whose bytes a test freezes on purpose: the
# frozen v1 analysis-manifest issuer and the battery-float grammar (#421, a
# physics hazard check that L1's battery module reuses).
ISSUED_MODULES = frozenset({
    "joulewise/analysis_manifest.py",
    "joulewise/battery_float.py",
})
ISSUED_PREFIXES = ("scripts/floor_mint_pinsets/",)
FIXTURE_PREFIXES = ("tests/fixtures/", "tests/goldens/")
# Content too common to name one file: an empty file, an empty JSON value.
_TRIVIAL_TARGET_BYTES = 2
# Archived evidence trees: digests of these bytes are digests of recorded data.
EVIDENCE_PREFIXES = ("docs/process_traces/", "docs/legacy/", "analysis/", "figures/",
                     "docs/paper/figures/")
RAW_CAPTURE_SUFFIXES = (".ioreg", ".plist", ".b85", ".zlib", ".log", ".txt", ".csv", ".exited")

# Files another gate-prune lane owns exclusively; Kind-B literals there are
# listed as follow-ups for that lane and never edited by L7.
OTHER_LANE_FILES = {
    "L2": ("tests/test_run_night.py", "tests/test_night_gate.py", "tests/test_night_agent_install.py",
           "tests/test_magistrate_watchdog.py", "tests/test_magistrate_watchdog_span.py",
           "tests/test_magistrate_watchdog_cli.py", "tests/test_install_magistrate_watchdog.py",
           "tests/test_b5_", "tests/fixtures/b5_plan/"),
    "L1": ("tests/hazards/", "tests/fixtures/hazards/"),
    "L3": ("tests/test_window_lineage.py",),
    "L4": ("tests/flags/", "configs/flags/"),
    "L5": ("tests/test_check_window_provenance.py", "tests/test_harvest_b5_window.py",
           "tests/fixtures/b5_harvest/"),
    "L6": ("configs/campaigns/v5_claim_25g83/",),
    "L8": ("tests/test_g10_clock_step_control.py",),
    "L10": ("tests/test_d117_contrast_v5_pack.py", "tests/test_v5_pack_regen.py",
            "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/"),
}
# Kind-B pins outside the census scope that the plan names as follow-ups.
EXTRA_FOLLOWUPS = (
    {"path": "joulewise/night_gate.py", "symbol": "RULED_REGISTRATIONS", "lane": "L2",
     "note": "registration digests table keyed by literal; owned by L2 (plan §5 L7)"},
)

# Family table. kind: P or B. write: how ``repin.py --write <family>`` acts.
#   rewrite_tests rewrite stale literal copies held in tests/ files
#   reissue       configs-held issued artifact: re-issue it with its issuer;
#                 a pack's own pins are rewritten by the pack generator
#   review        frozen code: revert the edit or re-freeze through review
#   none          not recomputable from the tree; nothing to write
FAMILIES: dict[str, dict[str, str]] = {
    "estimator_code": {
        "kind": "P", "write": "review",
        "description": "digest of measurement-core source; an acceptance or floor was issued against it"},
    "issued_code": {
        "kind": "P", "write": "review",
        "description": "digest of a deliberately frozen issued module (v1 analysis manifest, battery-float "
                       "grammar, floor-mint pinsets); re-freeze from the reviewed base, never from a head"},
    "pack_config_bytes": {
        "kind": "P", "write": "reissue",
        "description": "pack config bytes, plan trees, order manifests and pack registrations"},
    "sealed_registration": {
        "kind": "P", "write": "reissue",
        "description": "sealed registration or preregistration bytes"},
    "calibration_issued": {
        "kind": "P", "write": "reissue",
        "description": "issued calibration acceptance, ledger pins, battery-float verdicts"},
    "floor_artifact": {
        "kind": "P", "write": "reissue",
        "description": "issued floor-mint extraction specs and floor artifacts"},
    "supply_map_production": {
        "kind": "P", "write": "reissue",
        "description": "production paper-supply roles; a validator change must re-issue paper values"},
    "issued_config": {
        "kind": "P", "write": "reissue",
        "description": "other committed config pins (policies, panels, suites, readiness pins)"},
    "pinned_config_copy": {
        "kind": "P", "write": "rewrite_tests",
        "description": "a test's copy of a committed config, registration or pack file digest"},
    "recorded_evidence": {
        "kind": "P", "write": "none",
        "description": "digest of measured raw data or archived evidence bytes"},
    "historical_pin": {
        "kind": "P", "write": "none",
        "description": "test-held digest of a registration, acceptance, ledger or capture that is no longer in the tree"},
    "fixture_content": {
        "kind": "B", "write": "none",
        "description": "content address inside committed fixture data; stale only if the fixture bytes change"},
    "synthetic_literal": {
        "kind": "B", "write": "none",
        "description": "digest of inline synthetic data or a test constant; no code edit can make it stale"},
    "placeholder": {
        "kind": "B", "write": "none",
        "description": "repeated-character placeholder digest"},
    "source_digest": {
        "kind": "B", "write": "none",
        "description": "digest of source outside the measurement core; should be computed at test time"},
}
_P_CONTEXT = re.compile(
    r"registration|acceptance|ledger|floor|calibration|prompt|raw|bundle|capture|evidence|"
    r"estimator|stream|plist|ioreg|syslog|fixture_sha|SOURCE|frozen|structural", re.IGNORECASE)


@dataclass(frozen=True)
class Literal:
    path: str
    pointer: str
    value: str
    line: int
    context: str


@dataclass(frozen=True)
class Target:
    path: str
    method: str
    # None: today's tree. A commit: the bytes at that commit (an era record).
    commit: str | None = None

    @property
    def key(self) -> str:
        method = self.method if self.commit is None else f"{self.method}@{self.commit}"
        return f"{method}:{self.path}"


def parse_target_key(key: str) -> Target:
    """Invert ``Target.key``: ``<method>[@<commit>]:<path>[::<definition>]``."""

    method, _, path = key.partition(":")
    method, _, commit = method.partition("@")
    return Target(path, method, commit or None)


# Era records (orchestrator ruling 2026-10-06; CLAUDE.local.md "Physics refuses;
# everything else is a flag", item 2: provenance digests are records). A
# document that records the bytes of its own era declares the commit it
# recorded them at. A literal inside its declared scope resolves against the
# tree at that commit (``git show``), not today's, so a later edit to the
# recorded file leaves the record true while a tampered literal or a moved
# declared commit still fails ``repin.py --check``.
#   commit_pointer / commit_line  where the document declares its commit: a
#                                 JSON pointer, or a regex whose group 1 is the
#                                 commit on exactly one line
#   scope_pointer / scope_line    which literals are era records: a regex on
#                                 the JSON pointer, or on the literal's line
ERA_RECORDS: dict[str, dict[str, str]] = {
    # Block 4's sizing source records the production code at sizing time; its
    # top-level "head" is the commit it sized from.
    "configs/campaigns/v5_qualification_25g83/sizing_sources/sizing_source_v2.json": {
        "commit_pointer": "/head",
        "scope_pointer": r"^/provenance/production/[0-9]+/source/sha256$",
    },
    # Revision 6's pins.validator_sha256 records the validator that produced
    # block 1's derivation captures, sealed at the commit its heading names.
    # Its estimator_code_sha256 pins stay live: acceptance re-derives them.
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md": {
        "commit_line": r"^# Revision 6 \(sealed [0-9]{4}-[0-9]{2}-[0-9]{2} at ([0-9a-f]{7,40})\)$",
        "scope_line": r'^\s*"validator_sha256": "[0-9a-f]{64}",?$',
    },
}


class EraRecordError(ValueError):
    """An era record's declared commit is missing, ambiguous or not in history."""


def era_commit(root: Path, path: str, text: str) -> str:
    """The full commit an era record declares, verified to exist in history."""

    spec = ERA_RECORDS[path]
    if "commit_pointer" in spec:
        try:
            declared = _pointer(json.loads(text), spec["commit_pointer"])
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise EraRecordError(f"{path}: no declared commit at {spec['commit_pointer']}") from error
    else:
        found = re.findall(spec["commit_line"], text, flags=re.MULTILINE)
        if len(found) != 1:
            raise EraRecordError(f"{path}: {len(found)} commit declarations, expected 1")
        declared = found[0]
    if not isinstance(declared, str) or not re.fullmatch(r"[0-9a-f]{7,40}", declared):
        raise EraRecordError(f"{path}: declared commit {declared!r} is not a hex commit id")
    out = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet", f"{declared}^{{commit}}"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    if out.returncode != 0:
        raise EraRecordError(f"{path}: declared commit {declared} is not in this repository's history")
    return out.stdout.strip()


def in_era_scope(path: str, literal: "Literal", text: str) -> bool:
    spec = ERA_RECORDS.get(path)
    if spec is None:
        return False
    if "scope_pointer" in spec:
        return re.search(spec["scope_pointer"], literal.pointer) is not None
    lines = text.splitlines()
    line = lines[literal.line - 1] if 0 < literal.line <= len(lines) else ""
    return re.search(spec["scope_line"], line) is not None


def _pointer(document: object, pointer: str) -> object:
    value = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


# --------------------------------------------------------------------------
# Locating literals


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def _walk_json(value: object, pointer: str) -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{_escape(str(key))}"
            if HEX64.search(str(key)):
                yield f"{child_pointer}#key", str(key)
            yield from _walk_json(child, child_pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_json(child, f"{pointer}/{index}")
    elif isinstance(value, str) and HEX64.search(value):
        yield pointer, value


def _line_of(text: str, value: str) -> int:
    offset = text.find(value)
    return text.count("\n", 0, offset) + 1 if offset >= 0 else 0


def _python_contexts(text: str) -> dict[int, str]:
    """Map each line of a Python file to its innermost enclosing binding name."""

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    spans: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        name = None
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [target.id for target in targets if isinstance(target, ast.Name)]
            name = names[0] if names else None
        if name is not None and getattr(node, "end_lineno", None):
            spans.append((node.lineno, node.end_lineno, name))
    contexts: dict[int, str] = {}
    for start, end, name in sorted(spans, key=lambda span: span[0] - span[1]):
        for line in range(start, end + 1):
            contexts[line] = name  # innermost (shortest) span written last wins
    return contexts


def literals_in(path: str, raw: bytes) -> list[Literal]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return []
    if not HEX64.search(text):
        return []
    found: list[Literal] = []
    if path.endswith(".json"):
        try:
            value = json.loads(text)
        except ValueError:
            value = None
        if value is not None:
            for pointer, string in _walk_json(value, ""):
                key = pointer.endswith("#key")
                field = pointer[:-4].rsplit("/", 1)[-1] if key else pointer.rsplit("/", 1)[-1]
                for match in HEX64.finditer(string):
                    found.append(Literal(path, pointer, match.group(0), _line_of(text, match.group(0)), field))
            return found
    contexts = _python_contexts(text) if path.endswith(".py") else {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not HEX64.search(line):
            continue
        sub_pointer = ""
        if path.endswith(".jsonl"):
            try:
                pairs = list(_walk_json(json.loads(line), ""))
            except ValueError:
                pairs = []
            for pointer, string in pairs:
                for match in HEX64.finditer(string):
                    found.append(Literal(path, f"#L{number}{pointer}", match.group(0), number,
                                         pointer.rsplit("/", 1)[-1]))
            if pairs:
                continue
        for match in HEX64.finditer(line):
            context = contexts.get(number) or line.strip()[:80]
            found.append(Literal(path, f"#L{number}{sub_pointer}", match.group(0), number, context))
    return found


# --------------------------------------------------------------------------
# Resolving literals


def tracked_files(root: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], check=True,
                         stdout=subprocess.PIPE).stdout
    return sorted(item.decode("utf-8") for item in out.split(b"\0") if item)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def json_variants(raw: bytes) -> dict[str, bytes]:
    value = json.loads(raw)
    compact = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ascii_compact = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"canonical_json": compact, "canonical_json_nl": compact + b"\n",
            "canonical_json_ascii": ascii_compact, "canonical_json_ascii_nl": ascii_compact + b"\n"}


def python_definitions(text: str) -> Iterator[tuple[str, str, str]]:
    """Yield (qualified name, method, source) for each definition in a module."""

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    lines = text.splitlines(keepends=True)

    def visit(node: ast.AST, prefix: str, module_level: bool) -> Iterator[tuple[str, str, str]]:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                first = min([child.lineno, *(item.lineno for item in child.decorator_list)])
                yield name, "py_def", "".join(lines[first - 1:child.end_lineno])
                segment = ast.get_source_segment(text, child)
                if segment is not None:
                    yield name, "py_segment", segment
                yield from visit(child, f"{name}.", False)
            elif module_level and isinstance(child, (ast.Assign, ast.AnnAssign)):
                targets = child.targets if isinstance(child, ast.Assign) else [child.target]
                segment = ast.get_source_segment(text, child)
                for target in targets:
                    if isinstance(target, ast.Name) and segment is not None:
                        yield f"{prefix}{target.id}", "py_segment", segment

    yield from visit(tree, "", True)


def _read_at(root: Path, path: str, commit: str | None) -> bytes | None:
    """A file's bytes in today's tree, or at ``commit``; None when absent."""

    if commit is None:
        try:
            return (root / path).read_bytes()
        except OSError:
            return None
    out = subprocess.run(["git", "-C", str(root), "show", f"{commit}:{path}"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return out.stdout if out.returncode == 0 else None


def files_at(root: Path, commit: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "-z", "--name-only", commit],
                         check=True, stdout=subprocess.PIPE).stdout
    return sorted(item.decode("utf-8") for item in out.split(b"\0") if item)


def era_index(root: Path, commit: str, document_text: str) -> dict[str, list[Target]]:
    """Digests of the files an era record names, as they were at its commit.

    An era record names each file it records by path, so only files at the
    commit whose path appears in the record's text are candidates.
    """

    named = [path for path in files_at(root, commit) if path in document_text]
    return build_index(root, named, commit)


def build_index(root: Path, files: Iterable[str], commit: str | None = None) -> dict[str, list[Target]]:
    index: dict[str, list[Target]] = {}

    def add(digest: str, path: str, method: str) -> None:
        index.setdefault(digest, []).append(Target(path, method, commit))

    for path in files:
        raw = _read_at(root, path, commit)
        if raw is None:
            continue
        if len(raw) <= _TRIVIAL_TARGET_BYTES:
            continue
        add(_sha(raw), path, "file")
        add(_sha(b"blob %d\0" % len(raw) + raw), path, "git_blob")
        if path.endswith(".json"):
            try:
                for method, encoded in json_variants(raw).items():
                    add(_sha(encoded), path, method)
            except (ValueError, UnicodeDecodeError):
                pass
        if path.endswith(".py") and path.startswith(("joulewise/", "scripts/")):
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                continue
            for name, method, source in python_definitions(text):
                if len(source.strip()) > _TRIVIAL_TARGET_BYTES:
                    add(_sha(source.encode("utf-8")), f"{path}::{name}", method)
    return index


def target_digest(root: Path, target: Target) -> str | None:
    """Recompute a target's digest by its method; None when the target is gone."""

    path, _, name = target.path.partition("::")
    raw = _read_at(root, path, target.commit)
    if raw is None:
        return None
    if target.method == "file":
        return _sha(raw)
    if target.method == "git_blob":
        return _sha(b"blob %d\0" % len(raw) + raw)
    if target.method.startswith("canonical_json"):
        try:
            return _sha(json_variants(raw)[target.method])
        except (ValueError, KeyError, UnicodeDecodeError):
            return None
    if target.method in {"py_def", "py_segment"}:
        for qualified, method, source in python_definitions(raw.decode("utf-8")):
            if qualified == name and method == target.method:
                return _sha(source.encode("utf-8"))
        return None
    raise ValueError(f"unknown digest method: {target.method}")


_METHOD_PREFERENCE = ("file", "canonical_json_nl", "canonical_json", "canonical_json_ascii_nl",
                      "canonical_json_ascii", "git_blob", "py_def", "py_segment")


def _shared_prefix(left: str, right: str) -> int:
    count = 0
    for a, b in zip(left.split("/"), right.split("/")):
        if a != b:
            break
        count += 1
    return count


def _best_target(targets: list[Target], pinning_path: str) -> Target | None:
    """Pick one target: preferred method, then the nearest path, then the name."""

    candidates = [target for target in targets if target.path.partition("::")[0] != pinning_path]
    if not candidates:
        return None
    return sorted(candidates, key=lambda target: (
        _METHOD_PREFERENCE.index(target.method),
        -_shared_prefix(target.path.partition("::")[0], pinning_path), target.path))[0]


# --------------------------------------------------------------------------
# Classification


def pack_dir(path: str) -> str | None:
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "configs" and parts[1] == "campaigns":
        return f"configs/campaigns/{parts[2]}"
    return None


def owner_lane(path: str) -> str | None:
    for lane, prefixes in OTHER_LANE_FILES.items():
        if any(path == prefix or path.startswith(prefix) for prefix in prefixes):
            return lane
    return None


def _is_placeholder(value: str) -> bool:
    return len(set(value)) == 1 or value in {"0123456789abcdef" * 4, "abcdef0123456789" * 4}


def _target_family(target: Target) -> str:
    path = target.path.partition("::")[0]
    if path in MEASUREMENT_CORE:
        return "estimator_code"
    if path in ISSUED_MODULES or path.startswith(ISSUED_PREFIXES):
        return "issued_code"
    if path.startswith("configs/") or path.endswith(".md") and "registration" in path:
        return "pinned_config_copy"
    if path.startswith(EVIDENCE_PREFIXES) or path.endswith(RAW_CAPTURE_SUFFIXES):
        return "recorded_evidence"
    if path.startswith(("joulewise/", "scripts/")) or path.endswith(".py"):
        return "source_digest"
    if path.startswith(("tests/fixtures/", "tests/goldens/")):
        return "fixture_content"
    return "recorded_evidence"


def classify(literal: Literal, target: Target | None) -> str:
    path = literal.path
    if _is_placeholder(literal.value):
        return "placeholder"
    if target is not None and target.path.partition("::")[0] in MEASUREMENT_CORE:
        return "estimator_code"
    if "estimator_code" in literal.context:
        return "estimator_code"
    if path.startswith("configs/"):
        if path == "configs/paper_supply/supply_map.json":
            return "supply_map_production"
        if "registration" in path.rsplit("/", 1)[-1]:
            return "sealed_registration"
        if path.startswith("configs/campaigns/"):
            return "pack_config_bytes"
        if path.startswith("configs/calibration/"):
            return "calibration_issued"
        if path.startswith("configs/floor_mint/"):
            return "floor_artifact"
        return "issued_config"
    # tests/
    if path.startswith(FIXTURE_PREFIXES):
        # Recorded fixture bytes name the digests of their era; they are
        # content addresses, never checked against today's tree.
        if target is not None and _target_family(target) == "recorded_evidence":
            return "recorded_evidence"
        return "fixture_content"
    if target is not None:
        return _target_family(target)
    if _P_CONTEXT.search(literal.context):
        return "historical_pin"
    return "synthetic_literal"


def is_checked(path: str, family: str, target_path: str | None) -> bool:
    """Whether ``repin.py --check`` re-verifies a row against today's tree.

    Checked: a resolved Kind-P row held in a test (the test asserts it anyway;
    the check adds the repin command), or a config's pin of another config's
    bytes or of measurement-core code. Not checked: fixture bytes, and a
    config's record of non-core code or archived documents as they were when
    it was issued. Those are provenance records of their era, and checking
    them against today's tree would fail every ordinary edit.
    """

    if target_path is None or FAMILIES[family]["kind"] != "P" or path.startswith(FIXTURE_PREFIXES):
        return False
    if path.startswith("configs/"):
        file_path = target_path.partition("::")[0]
        return file_path.startswith("configs/") or file_path in MEASUREMENT_CORE
    return True


def regenerator(family: str, path: str, root: Path = REPO_ROOT) -> str | None:
    pack = pack_dir(path)
    if pack and (root / pack / "generate_configs.py").is_file():
        return f"pack:{pack.rsplit('/', 1)[-1]}"
    write = FAMILIES[family]["write"]
    return None if write == "none" else family


# --------------------------------------------------------------------------
# Registry


def census(root: Path = REPO_ROOT) -> dict[str, object]:
    files = tracked_files(root)
    index = build_index(root, files)
    rows: dict[str, list[list[object]]] = {}
    target_ids: dict[str, int] = {}
    target_keys: list[str] = []
    checked = 0
    summary: Counter[tuple[str, str]] = Counter()
    followups: Counter[tuple[str, str, str]] = Counter()
    for path in files:
        if not path.startswith(SCOPE) or path == REGISTRY_REL:
            continue
        try:
            raw = (root / path).read_bytes()
        except OSError:
            continue
        era: dict[str, list[Target]] | None = None
        if path in ERA_RECORDS:
            text = raw.decode("utf-8")
            era = era_index(root, era_commit(root, path, text), text)
        for literal in literals_in(path, raw):
            in_scope = era is not None and in_era_scope(path, literal, text)
            target = _best_target((era if in_scope else index).get(literal.value, []), path)
            family = classify(literal, target)
            kind = FAMILIES[family]["kind"]
            summary[(kind, family)] += 1
            lane = owner_lane(path)
            if lane and kind == "B" and family not in {"placeholder", "fixture_content"}:
                followups[(lane, path, family)] += 1
            index_id = None
            if target is not None:
                key = target.key
                if key not in target_ids:
                    target_ids[key] = len(target_keys)
                    target_keys.append(key)
                index_id = target_ids[key]
                checked += is_checked(path, family, target.path)
            rows.setdefault(path, []).append([literal.pointer, family, index_id])
    by_family: dict[str, dict[str, object]] = {}
    for (kind, family), count in sorted(summary.items()):
        by_family[family] = {"kind": kind, "count": count}
    # Renumber targets in sorted order so the registry is deterministic.
    order = sorted(range(len(target_keys)), key=lambda i: target_keys[i])
    renumber = {old: new for new, old in enumerate(order)}
    for path_rows in rows.values():
        for row in path_rows:
            if row[2] is not None:
                row[2] = renumber[row[2]]
    files_out = []
    for path in sorted(rows):
        lane = owner_lane(path)
        entry: dict[str, object] = {"path": path, "rows": sorted(rows[path], key=lambda row: str(row[0]))}
        families = sorted({row[1] for row in rows[path]})
        regenerators = sorted({gen for family in families if (gen := regenerator(family, path, root))})
        if regenerators:
            entry["regenerators"] = regenerators
        if lane:
            entry["owner_lane"] = lane
        files_out.append(entry)
    return {
        "schema": SCHEMA,
        "generated_by": "python scripts/digest_pin_census.py --write",
        "scope": list(SCOPE),
        "row_format": ["json_pointer", "family", "target"],
        "target_format": "<method>[@<commit>]:<path>[::<definition>], indexed by a row's target; "
                         "@<commit> marks an era record, verified at that commit",
        "kinds": {
            "P": "protects a number: kept hard-coded, checked by scripts/repin.py --check, never auto-repinned",
            "B": "busywork: cannot go stale from a code edit, or is computed at test time",
        },
        "families": {name: dict(spec) for name, spec in sorted(FAMILIES.items())},
        "summary": {
            "literals": sum(summary.values()),
            "files": len(rows),
            "by_kind": {kind: sum(count for (k, _), count in summary.items() if k == kind) for kind in ("P", "B")},
            "by_family": by_family,
            "resolved_checked": checked,
        },
        "followups": [
            *({"lane": lane, "path": path, "family": family, "count": count}
              for (lane, path, family), count in sorted(followups.items())),
            *EXTRA_FOLLOWUPS,
        ],
        "targets": [target_keys[i] for i in order],
        "files": files_out,
    }


def render(registry: dict[str, object]) -> str:
    """One row per line, so a regenerated registry diffs line by line."""

    head = {key: value for key, value in registry.items() if key not in {"files", "targets"}}
    text = json.dumps(head, indent=2, sort_keys=True)
    lines = [text[:-2] + ',\n  "targets": [']
    targets = registry["targets"]
    for position, key in enumerate(targets):
        lines.append("    " + json.dumps(key) + ("," if position + 1 < len(targets) else ""))
    lines.append('  ],\n  "files": [')
    entries = registry["files"]
    for position, entry in enumerate(entries):
        meta = {key: value for key, value in entry.items() if key != "rows"}
        lines.append("    {" + json.dumps(meta, sort_keys=True)[1:-1] + ', "rows": [')
        rows = entry["rows"]
        for row_index, row in enumerate(rows):
            lines.append("      " + json.dumps(row) + ("," if row_index + 1 < len(rows) else ""))
        lines.append("    ]}" + ("," if position + 1 < len(entries) else ""))
    lines.append("  ]\n}\n")
    return "\n".join(lines)


def load_registry(root: Path = REPO_ROOT) -> dict[str, object]:
    return json.loads((root / REGISTRY_REL).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true", help=f"rewrite {REGISTRY_REL}")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    registry = census(args.root)
    if args.write:
        out = args.root / REGISTRY_REL
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(registry), encoding="utf-8")
        print(f"wrote {REGISTRY_REL}")
    summary = registry["summary"]
    print(f"{summary['literals']} literals in {summary['files']} files: "
          f"P {summary['by_kind']['P']}, B {summary['by_kind']['B']}; "
          f"{summary['resolved_checked']} Kind-P rows resolve to tracked bytes and are checked")
    for family, entry in summary["by_family"].items():
        print(f"  {entry['kind']} {family}: {entry['count']}")
    for item in registry["followups"]:
        print(f"  follow-up {item['lane']}: {item['path']} ({item.get('family', item.get('symbol'))})")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
