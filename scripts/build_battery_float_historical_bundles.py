"""Rebuild and audit the closed, pre-battery-float bundle inventory at S1 base."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

BASE = "1417c0c4caf36f7ac132410b3cd3ebc7aefbd9e7"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise.detection_floor import complete_bundle_sha256  # noqa: E402
from joulewise.bundle_read import BundleReadError, BundleReader, _bundle_tree_sha256  # noqa: E402

OUTPUT = ROOT / "configs/battery_float/historical_bundles.json"
INCLUDED_SOURCES = frozenset({
    "df-ph-decode-floor-mint1.json",
    "analysis/rpt001-v2/input_manifest.json",
    "tracked_fixture_bundles",
})
HEX = re.compile(r"^[0-9a-f]{64}$")
HEX_ANY = re.compile(r"\b[0-9a-f]{64}\b")
HEX_ANY_BYTES = re.compile(rb"\b[0-9a-f]{64}\b")
KEY = re.compile(r"(?i)(?:bundle.*(?:sha256|digest|tree)|(?:sha256|digest|tree).*bundle)")
TEXT_TOKEN = re.compile(r"[A-Za-z0-9_]+")
# (key, producing schema) -> (class, producing code). Every observed pair is named.
CLASSIFICATION = {
    ("bundle_sha256", "joulewise.detection_floor_artifact.v2"):
        ("complete", "joulewise/detection_floor.py:558"),
    ("bundle_sha256s", "joulewise.detection_floor_artifact.v2"):
        ("complete", "joulewise/detection_floor.py:558"),
    ("bundle_tree_sha256", "joulewise.report_analysis_input.v1:rpt001-v2"):
        ("tree_nul_v1", "scripts/make_figures.py:184"),
    ("bundle_tree_sha256", "joulewise.report_artifact_manifest.v1:rpt001-v2"):
        ("tree_nul_v1", "scripts/make_figures.py:337"),
    ("bundle_tree_sha256", "joulewise.report_analysis_input.v1:rpt001-v1"):
        ("tree_legacy", "scripts/make_figures.py:138"),
    ("bundle_tree_sha256", "joulewise.report_artifact_manifest.v1:rpt001-v1"):
        ("tree_legacy", "scripts/make_figures.py:138"),
    ("validated_bundle_sha256", "joulewise.strict_validation_attempt_evidence.v1"):
        ("not_a_bundle", "scripts/run_campaign.py:7044"),
    ("/spec_on_bundle/requests_artifact_sha256", "tests/goldens/output_identity_*.patch.json"):
        ("file_digest", "joulewise/output_identity.py:102"),
    ("PINNED_BUNDLE_SHA256", "scripts/issue_dg071_dg075_statistics.py"):
        ("file_digest", "scripts/issue_dg071_dg075_statistics.py:537-539"),
}


def tracked_snapshot() -> tuple[Path, tempfile.TemporaryDirectory[str], list[str]]:
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    archive = subprocess.check_output(["git", "archive", BASE], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar:
            dest = root / member.name
            if member.isdir():
                dest.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                dest.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                assert source is not None
                dest.write_bytes(source.read())
            else:
                raise ValueError(f"non-regular tracked member: {member.name}")
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "-z", BASE], cwd=ROOT,
    ).decode().rstrip("\0").split("\0")
    return root, temp, names


def _schema(obj: object, name: str) -> str:
    if not isinstance(obj, dict):
        return name
    value = obj.get("schema") or obj.get("schema_version")
    if not isinstance(value, str):
        return name
    if name.startswith("analysis/rpt001-"):
        return f"{value}:{name.split('/')[1]}"
    return value


def _walk(obj: object, keys: tuple[str, ...] = (), identity: str | None = None):
    if isinstance(obj, dict):
        identity = next((obj[k] for k in ("bundle_id", "run_id")
                         if isinstance(obj.get(k), str)), identity)
        for key, value in obj.items():
            yield from _walk(value, keys + (key,), identity)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk(value, keys, identity)
    elif isinstance(obj, str) and HEX.fullmatch(obj):
        named = next((key for key in reversed(keys) if KEY.search(key)), None)
        if named:
            yield named, obj, identity or (keys[-1] if keys else "")


def _classified(name: str, key: str, schema: str) -> tuple[str, str]:
    lookup = (key, schema)
    if key == "/spec_on_bundle/requests_artifact_sha256":
        lookup = (key, "tests/goldens/output_identity_*.patch.json")
    if lookup not in CLASSIFICATION:
        if schema == name and name.endswith((".md", ".html", ".txt")):
            return "quoted", ""
        raise ValueError(f"unclassified candidate pair: key={key} schema={schema} file={name}")
    return CLASSIFICATION[lookup]


def _candidates(root: Path, names: list[str]):
    for name in names:
        path = root / name
        if not path.is_file():
            continue
        try:
            content = path.read_text()
        except UnicodeError:
            print(f"skipped non-utf8 {name}", file=sys.stderr)
            continue
        parsed = False
        if name.endswith((".json", ".jsonl")):
            try:
                objects = ([json.loads(line) for line in content.splitlines() if line.strip()]
                           if name.endswith(".jsonl") else [json.loads(content)])
            except ValueError as exc:
                print(f"unparseable {name}: {type(exc).__name__}", file=sys.stderr)
            else:
                parsed = True
                for obj in objects:
                    schema = _schema(obj, name)
                    for key, digest, run_id in _walk(obj):
                        yield name, key, schema, digest, run_id
        if not parsed:
            # Assignment and prose lines. Markdown tables are attributed to
            # their header column, rather than to nearby prose on the line.
            header: list[str] = []
            for line in content.splitlines():
                if line.lstrip().startswith("|"):
                    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                    if (len(cells) >= 2 and all(len(cell) < 80 for cell in cells)
                            and not any(HEX_ANY.search(cell) for cell in cells)
                            and any(KEY.search(cell) for cell in cells)):
                        header = cells
                        continue
                    for index, cell in enumerate(cells):
                        if index < len(header) and KEY.search(header[index]):
                            for digest in HEX_ANY.findall(cell):
                                yield name, header[index], name, digest, ""
                    continue
                if name == "scripts/issue_dg071_dg075_statistics.py" and "PINNED_BUNDLE_SHA256" in line:
                    continue
                keys = [(token.start(), token.group()) for token in TEXT_TOKEN.finditer(line)
                        if not HEX.fullmatch(token.group()) and KEY.fullmatch(token.group())]
                if keys:
                    for match in HEX_ANY.finditer(line):
                        before = [item for item in keys if item[0] < match.start()]
                        key = (before[-1] if before else keys[0])[1]
                        yield name, key, name, match.group(), ""
            if name == "scripts/issue_dg071_dg075_statistics.py":
                match = re.search(r"PINNED_BUNDLE_SHA256\s*=\s*\(\s*\"([0-9a-f]{64})\"", content)
                if match:
                    yield name, "PINNED_BUNDLE_SHA256", name, match.group(1), ""


def build(root: Path, names: list[str]):
    rows: dict[str, dict[str, str]] = {}
    pending: list[tuple[str, str, str, str]] = []
    tracked = set(names)
    for name in names:
        if not name.endswith("/metadata.json") or not name.startswith(("tests/fixtures/", "docs/process_traces/")):
            continue
        directory = Path(name).parent
        if (directory / "events.jsonl").as_posix() not in tracked:
            continue
        metadata = json.loads((root / name).read_text())
        digest = complete_bundle_sha256(root / directory)
        if digest in rows:
            raise ValueError(f"duplicate fixture digest: {digest}")
        rows[digest] = {"complete_bundle_sha256": digest,
                        "run_id": metadata.get("run_id") or directory.name,
                        "source": name}
    for name, key, schema, digest, run_id in _candidates(root, names):
        kind, producer = _classified(name, key, schema)
        if name in INCLUDED_SOURCES and name == "df-ph-decode-floor-mint1.json" and key == "bundle_sha256":
            if digest in rows:
                raise ValueError(f"duplicate included digest: {digest}")
            rows[digest] = {"complete_bundle_sha256": digest, "run_id": run_id,
                            "source": name}
        elif name in INCLUDED_SOURCES and name == "analysis/rpt001-v2/input_manifest.json":
            manifest = json.loads((root / name).read_text())
            if manifest.get("bundle_tree_identity") != {"algorithm": "sha256", "version": "joulewise.bundle-tree.nul-v1"}:
                raise ValueError("included tree manifest has wrong identity")
            if digest in rows:
                raise ValueError(f"duplicate included digest: {digest}")
            rows[digest] = {"bundle_tree_sha256": digest,
                            "tree_identity": "joulewise.bundle-tree.nul-v1",
                            "run_id": run_id, "source": name}
        else:
            pending.append((name, key, kind, digest))
    listed = []
    for name, key, kind, digest in pending:
        reason = ("duplicate of included citation" if digest in rows and name in (
                      "df-ph-decode-floor-mint1.json", "analysis/rpt001-v2/artifact_manifest.json")
                  else "source not named by amendment 40" if kind in ("complete", "tree_nul_v1")
                  else "quoted in text, not a citation source" if kind == "quoted"
                  else "file digest, not a bundle" if kind == "file_digest" else
                  "retired tree fold" if kind == "tree_legacy" else "not a bundle")
        listed.append((name, key, kind, digest, reason))
    ordered = sorted(rows.values(), key=lambda row: ("complete" if "complete_bundle_sha256" in row else "tree",
                                                   row.get("complete_bundle_sha256", row.get("bundle_tree_sha256"))))
    return ordered, listed


def witness(root: Path, names: list[str], roots: list[Path], rows: list[dict[str, str]]) -> None:
    citations: dict[str, set[str]] = defaultdict(set)
    for name in names:
        path = root / name
        if path.is_file():
            for digest in HEX_ANY_BYTES.findall(path.read_bytes()):
                citations[digest.decode()].add(name)
    included = {row.get("complete_bundle_sha256", row.get("bundle_tree_sha256")): row
                for row in rows}
    bundles: list[Path] = []
    for run_root in roots:
        if not run_root.is_dir():
            raise ValueError(f"witness root unavailable: {run_root}")
        bundles.extend(p.parent for p in run_root.rglob("metadata.json") if p.is_file())
    print(f"witness bundles={len(bundles)}")
    hit_count = Counter()
    matched: set[str] = set()
    named: set[str] = set()
    namesake_lines = 0
    namesake_bundles: set[Path] = set()
    for bundle in sorted(set(bundles)):
        complete = complete_bundle_sha256(bundle)
        tree = _bundle_tree_sha256(bundle)
        bundle_names = {bundle.name}
        try:
            metadata = BundleReader(bundle)._strict_json("metadata.json")
        except BundleReadError:
            metadata = None
        if isinstance(metadata, dict) and isinstance(metadata.get("run_id"), str):
            bundle_names.add(metadata["run_id"])
        else:
            print(f"witness metadata_unreadable {bundle}")
        observed = {"complete": complete, "tree": tree}
        for kind, digest in (("complete", complete), ("tree", tree)):
            for source in sorted(citations.get(digest, ())):
                status = "included" if digest in included and included[digest]["source"] == source else "listed"
                print(f"witness {status} {kind} {bundle} {digest} {source}")
                hit_count[(kind, source, status)] += 1
            if digest in included and included[digest]["run_id"] not in bundle_names:
                raise ValueError(f"included digest run_id mismatch: {bundle} {digest}")
            if digest in included and not citations.get(digest):
                raise ValueError(f"included digest has no tracked citation: {bundle} {digest}")
        for row in rows:
            kind = "complete" if "complete_bundle_sha256" in row else "tree"
            digest = row.get("complete_bundle_sha256", row.get("bundle_tree_sha256"))
            if observed[kind] == digest:
                matched.add(digest)
            elif row["run_id"] in bundle_names:
                named.add(digest)
                namesake_lines += 1
                namesake_bundles.add(bundle)
                print(f"witness namesake {kind} {bundle} {row['run_id']} "
                      f"expected={digest} observed={observed[kind]}")
    fails = False
    entry_counts = Counter()
    for row in rows:
        kind = "complete" if "complete_bundle_sha256" in row else "tree"
        digest = row.get("complete_bundle_sha256", row.get("bundle_tree_sha256"))
        state = "matched" if digest in matched else "named_only" if digest in named else "absent"
        entry_counts[state] += 1
        print(f"witness_entry {state} {kind} {row['run_id']} {digest} {row['source']}")
        if state == "named_only" and row["source"] in {
            "df-ph-decode-floor-mint1.json", "analysis/rpt001-v2/input_manifest.json"
        }:
            fails = True
    for state in ("matched", "named_only", "absent"):
        print(f"witness_entry_count {state} {entry_counts[state]}")
    print(f"witness_namesake_count lines={namesake_lines} bundles={len(namesake_bundles)}")
    for (kind, source, status), count in sorted(hit_count.items()):
        print(f"witness_count {status} {kind} {source} {count}")
    unexpected = [source for _, source, status in hit_count if status == "listed"
                  and not source.endswith((".md", ".html", ".txt"))
                  and source != "analysis/rpt001-v2/artifact_manifest.json"]
    if unexpected:
        raise ValueError(f"witness non-prose listed hits: {sorted(set(unexpected))}")
    if fails:
        raise ValueError("witness named_only included citation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--witness", nargs="+", type=Path)
    args = parser.parse_args()
    root, temp, names = tracked_snapshot()
    try:
        rows, listed = build(root, names)
        rendered = (json.dumps(rows, indent=2, sort_keys=True) + "\n").encode()
        if len(rows) != 69:
            raise ValueError(f"entry count {len(rows)} differs from 69")
        if args.check:
            if OUTPUT.read_bytes() != rendered:
                raise ValueError("forward check: committed bytes differ")
            print(f"forward check: byte-identical entries={len(rows)}")
        elif args.witness is None:
            OUTPUT.write_bytes(rendered)
            print(f"written entries={len(rows)} sha256={hashlib.sha256(rendered).hexdigest()}")
        counts = Counter((item[0], item[1]) for item in listed)
        for name, key, kind, digest, reason in sorted(listed):
            print(f"listed {name} {key} {kind} {digest}: {reason}", file=sys.stderr)
        for (name, key), count in sorted(counts.items()):
            print(f"listed_count {name} {key} {count}", file=sys.stderr)
        results = json.loads((root / "docs/process_traces/2026-08-09-prefill-phase-proof/results.json").read_text())
        def named_bundles(obj):
            if isinstance(obj, dict):
                if isinstance(obj.get("bundle"), str):
                    yield obj["bundle"], obj.get("corpus_root", "")
                for value in obj.values():
                    yield from named_bundles(value)
            elif isinstance(obj, list):
                for value in obj:
                    yield from named_bundles(value)
        paper = sorted(set(named_bundles(results)))
        print(f"listed_population paper_results_file_digest bundles={len(paper)}", file=sys.stderr)
        for run_id, corpus in paper:
            print(f"listed_population {run_id} {corpus} file_digest", file=sys.stderr)
        if args.witness is not None:
            witness(root, names, args.witness, rows)
        return 0
    finally:
        temp.cleanup()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"builder error: {exc}", file=sys.stderr)
        raise SystemExit(1)
