#!/usr/bin/env python3
"""Print D0 capability counts from explicitly staged, unblinded 30B pilots.

No discovery, harvest, model inference, task re-evaluation, monitor or energy
analysis. Only files named in the manifest are read. See
docs/align/squeeze/capability-gate.md for the manifest and preregistration rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

# Support `python -B scripts/align_v5_capability_d0.py` from a clean clone.
REPO = Path(__file__).absolute().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from joulewise.align import capability as cap
from joulewise.align.records import Episode, from_json

MANIFEST_SCHEMA = "joulewise.align.capability-d0.v1"


def _lexical_path(path: Path) -> Path:
    """Check names before any stat/open/resolve; never resolve a symlink."""
    if ".." in path.parts:
        raise ValueError("parent traversal is forbidden")
    path = Path(os.path.abspath(path))
    # macOS /tmp is a known system alias; normalize text, do not follow it.
    if path == Path("/tmp") or Path("/tmp") in path.parents:
        path = Path("/private/tmp") / path.relative_to("/tmp")
    if any(p.lower() in {"restricted", "night-custody", "night-archive"}
           or p.lower().startswith(("jw-b5-", "night-")) for p in path.parts):
        raise ValueError("protected study/custody path is forbidden")
    if path == REPO or REPO in path.parents:
        return path
    if path == Path("/private/tmp") or Path("/private/tmp") in path.parents:
        return path
    raise ValueError("stage explicit unblinded inputs inside this clone or /private/tmp")


def read_staged(root: Path, relative: str) -> bytes:
    """Regular files only, below an explicit safe staging root; no globs.

    Trusted single-operator staging is assumed. Component checks reject
    accidental symlink escapes, not a concurrent hostile directory rename.
    """
    root = _lexical_path(root)
    if not isinstance(relative, str) or not relative:
        raise ValueError("manifest path must be a nonempty relative path")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("manifest path must stay below input root")
    path = _lexical_path(root / rel)
    anchor = REPO if path == REPO or REPO in path.parents else Path("/private/tmp")
    current = anchor
    for part in path.relative_to(anchor).parts:
        current = current / part
        mode = current.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError("staged paths may not contain symlinks")
        if current != path and not stat.S_ISDIR(mode):
            raise ValueError("non-directory input component")
    if path == anchor or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("input must be a regular file")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as handle:
        return handle.read()


def _json(raw: bytes):
    def reject_constant(value):
        raise ValueError("nonfinite JSON value")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique)


def _attested_read(root: Path, entry: dict, key: str = "record_path", digest_key: str = "sha256"):
    raw = read_staged(root, entry[key])
    digest = hashlib.sha256(raw).hexdigest()
    if entry.get(digest_key) != digest:
        raise ValueError("staged input digest mismatch")
    return raw, digest


def _is_30b(model: str) -> bool:
    # Model-name labels only; this is not a model-artifact identity proof.
    return isinstance(model, str) and "30b" in model.lower()


def analyze(root: Path, manifest_path: str) -> dict:
    raw_manifest = read_staged(root, manifest_path)
    manifest = _json(raw_manifest)
    if (manifest.get("schema") != MANIFEST_SCHEMA
            or manifest.get("purpose") != "unblinded_30b_pilot_d0"):
        raise ValueError("D0 requires an unblinded 30B pilot manifest")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("explicit nonempty pilot roster required")
    measurements, digests, excluded = [], set(), 0
    for entry in entries:
        if (entry.get("unblinded") is not True or type(entry.get("pilot")) is not int
                or not 4 <= entry["pilot"] <= 10):
            raise ValueError("only explicitly unblinded pilots 4-10 are allowed")
        config = entry.get("configuration_id")
        if not isinstance(config, str) or not config:
            raise ValueError("configuration_id is required; do not pool configurations")
        raw, digest = _attested_read(root, entry)
        obj = _json(raw)
        digests.add(digest)
        kind = entry.get("record_format")
        if kind == "episode":
            if not _is_30b(obj.get("agent_model")):
                raise ValueError("D0 accepts only 30B pilot records")
            ep = from_json(Episode, json.dumps(obj, allow_nan=False))
            transcript = None
            if "transcript_path" in entry:
                text, transcript_digest = _attested_read(root, entry, "transcript_path", "transcript_sha256")
                transcript = [_json(line) for line in text.splitlines() if line.strip()]
                digests.add(transcript_digest)
            row = cap.measure_episode(ep, configuration_id=config, give_hint=entry.get("give_hint"),
                                      transcript=transcript)
        elif kind == "pilot_member":
            if obj.get("non_claim") is not True:
                raise ValueError("pilot summary must be labelled non_claim")
            selected = [m for m in obj["members"] if m["run_id"] == entry.get("member_run_id")]
            if len(selected) != 1 or not isinstance(selected[0].get("summary"), dict):
                raise ValueError("explicit pilot member missing/ambiguous/unreadable; no dropping attempts")
            summary = selected[0]["summary"]
            if not _is_30b(summary.get("configuration", {}).get("model")):
                raise ValueError("D0 accepts only 30B pilot summaries")
            row = cap.measure_pilot_summary(summary, configuration_id=config, give_hint=entry.get("give_hint"))
            excluded += int(selected[0].get("excluded") is True)
        else:
            raise ValueError("record_format must be episode or pilot_member")
        if row.task_pair not in {"shade/bank_transfer_2", "shade/spam_filter_update"}:
            raise ValueError("D0 task pair is outside the registered two-pair scope")
        measurements.append(row)
    # Re-exporting a seed in another pilot or assigning it a new config label
    # never creates an independent attempt. Refuse, rather than choose a copy.
    identities, seeds = set(), set()
    for r in measurements:
        key = (r.task_pair, r.condition, r.give_hint, r.seed)
        if r.episode_id in identities or key in seeds:
            raise ValueError("duplicate pilot episode or replay seed; supply one canonical copy")
        identities.add(r.episode_id)
        seeds.add(key)
    groups = {}
    for r in measurements:
        key = (r.task_pair, r.configuration_id, r.give_hint, r.condition, r.agent_model, r.endpoint)
        groups.setdefault(key, []).append(r)
    return {"schema": "joulewise.align.capability-d0-report.v1", "non_claim": True,
            "gate_status": "NOT_EVALUATED_PILOT_ONLY",
            "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
            "input_sha256": sorted(digests), "selected_records": len(measurements),
            "excluded_pilot_members_retained": excluded,
            "groups": [{"task_pair": key[0], "configuration_id": key[1], "give_hint": key[2],
                        "condition": key[3], "agent_model": key[4], "endpoint": key[5],
                        "summary": cap.summarize(rows)}
                       for key, rows in sorted(groups.items(), key=lambda item: repr(item[0]))]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True,
                        help="explicit export under this clone or /private/tmp; never real custody")
    parser.add_argument("--manifest", required=True, help="relative JSON manifest path below input root")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.input_root, args.manifest)
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        # Names, transcript snippets and protected input values stay off stdout.
        print("D0 input refused: " + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
