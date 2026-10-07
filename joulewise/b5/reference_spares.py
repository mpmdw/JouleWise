"""Spare NEG-8 reference members for the spare-slot retry (NEG-8 ruling 2026-10-07, decision 5).

Block-5 registration 0.12, "One retry, by spare slot": each reference stage
(the start triplet, the midpoint reference, the end triplet) lists spare
members, copies of the stage's reference config under their own run ids (three
for each triplet, one for the midpoint). When the stage ends with fewer
succeeded members than it planned, the chain runs exactly (planned -
succeeded) of them, immediately, into the same runs root
(``joulewise.b5.chain``). The failed attempt's bundle is never touched; each
spare carries the slot's role, so the whole-window evaluators gather it by
role like any other reference.

The spares are committed under ``configs/campaigns/window_reference_spares_v5``
as one directory per spare count: ``<stage>_spares_<k>/`` holds spares 1..k and
an order manifest listing exactly them, so the chain launches a committed
directory and run_campaign never sees a config its manifest does not list.
Spare i is the stage's first reference config byte for byte except its
``run_id``; its order-manifest row is the stage's first row with its own
index, config, run id and rep (role and sentinel position unchanged).

``python -m joulewise.b5.reference_spares --check`` verifies the committed
bytes; ``--write`` writes them. The pack generators call
``attach_spare_retries`` so each reference stage's plan-tree row carries
``spare_retry``: the spare members (run id, config path, SHA-256) and each
spare set's order manifest (path, SHA-256), all pinned by the plan tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SPARE_RETRY_SCHEMA = "joulewise.b5_reference_spare_retry.v1"
SPARES_REL = "configs/campaigns/window_reference_spares_v5"
REFERENCES_REL = "configs/campaigns/window_references_v5"

# slot -> (the stage's config directory, its spare-directory stem, spare run-id stem, spare count)
SLOTS: dict[str, tuple[str, str, str, int]] = {
    "start": (f"{REFERENCES_REL}/start_triplet", "start_triplet_spares", "neg8-window-start-spare", 3),
    "midpoint": (f"{REFERENCES_REL}/midpoint", "midpoint_spares", "neg8-window-midpoint-spare", 1),
    "end": (f"{REFERENCES_REL}/end_triplet", "end_triplet_spares", "neg8-window-end-spare", 3),
}


class SpareError(ValueError):
    """The committed reference bytes cannot give the spares; nothing was written."""


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def render_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def spare_directory(slot: str, count: int) -> str:
    _source, stem, _run_stem, maximum = SLOTS[slot]
    if not 1 <= count <= maximum:
        raise SpareError(f"{slot}: spare count {count} is outside 1..{maximum}")
    return f"{SPARES_REL}/{stem}_{count}"


def spare_run_id(slot: str, index: int) -> str:
    return f"{SLOTS[slot][2]}-{index}"


def spare_files(repo_root: Path = REPO_ROOT) -> dict[str, bytes]:
    """Every committed spare file (repository-relative path -> bytes), derived from the stage's own bytes."""

    files: dict[str, bytes] = {}
    for slot, (source_dir, _stem, _run_stem, maximum) in SLOTS.items():
        source = Path(repo_root) / source_dir
        try:
            manifest = json.loads((source / "order_manifest.json").read_bytes())
            first = manifest["executed_order"][0]
            config_raw = (source / first["config"]).read_bytes()
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise SpareError(f"{slot}: {source_dir} cannot be read: {exc}") from exc
        needle = f'"run_id": "{first["run_id"]}"'.encode("utf-8")
        if config_raw.count(needle) != 1:
            raise SpareError(f"{slot}: {first['config']} does not name its run id exactly once")
        configs = {}
        rows = []
        for index in range(1, maximum + 1):
            run_id = spare_run_id(slot, index)
            name = f"{run_id}.json"
            configs[name] = config_raw.replace(needle, f'"run_id": "{run_id}"'.encode("utf-8"))
            rows.append({**first, "index": index, "config": name, "run_id": run_id, "rep": index,
                         "position_in_block": index})
        for count in range(1, maximum + 1):
            directory = spare_directory(slot, count)
            for row in rows[:count]:
                files[f"{directory}/{row['config']}"] = configs[row["config"]]
            files[f"{directory}/order_manifest.json"] = render_json({
                **manifest,
                "manifest_id": f"{manifest['manifest_id']}-spares-{count}",
                "ordering_note": (f"Spare-slot retry (NEG-8 ruling 2026-10-07, registration 0.12): the first "
                                  f"{count} spare(s) of {source_dir.rsplit('/', 1)[-1]}, run by the chain only when "
                                  f"the stage ends with {count} fewer succeeded member(s) than it planned."),
                "planned_n_bundles": count,
                "executed_order": rows[:count],
            })
    return files


def check(repo_root: Path = REPO_ROOT) -> list[str]:
    """Paths whose committed bytes differ from what ``spare_files`` derives (empty: verified)."""

    root = Path(repo_root)
    expected = spare_files(root)
    problems = []
    for relative, raw in sorted(expected.items()):
        path = root / relative
        if not path.is_file() or path.read_bytes() != raw:
            problems.append(relative)
    present = {path.relative_to(root).as_posix() for path in (root / SPARES_REL).rglob("*.json")} \
        if (root / SPARES_REL).is_dir() else set()
    problems.extend(sorted(present - set(expected)))
    return problems


def write(repo_root: Path = REPO_ROOT) -> list[str]:
    root = Path(repo_root)
    written = []
    for relative, raw in sorted(spare_files(root).items()):
        path = root / relative
        if path.is_file() and path.read_bytes() == raw:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        written.append(relative)
    return written


def spare_retry_record(slot: str, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """The plan-tree ``spare_retry`` of one reference stage; refuses committed bytes that do not verify."""

    root = Path(repo_root)
    files = spare_files(root)
    _source, _stem, _run_stem, maximum = SLOTS[slot]
    for relative, raw in files.items():
        if relative.startswith(f"{SPARES_REL}/{SLOTS[slot][1]}_") and (
                not (root / relative).is_file() or (root / relative).read_bytes() != raw):
            raise SpareError(f"committed spare bytes drifted: {relative}")
    largest = spare_directory(slot, maximum)
    members = [{"run_id": spare_run_id(slot, index),
                "path": f"{largest}/{spare_run_id(slot, index)}.json",
                "sha256": sha256_bytes(files[f"{largest}/{spare_run_id(slot, index)}.json"])}
               for index in range(1, maximum + 1)]
    return {
        "schema_version": SPARE_RETRY_SCHEMA,
        "slot": slot,
        "max_spares": maximum,
        "rule": ("NEG-8 ruling 2026-10-07, registration 0.12: after the stage, when fewer members succeeded than "
                 "planned, the chain runs the spare set of size (planned - succeeded), once, into the same runs "
                 "root, under the collection deadline; each spare measured is flagged member.retried"),
        "members": members,
        "spare_sets": [{"count": count,
                        "order_manifest": {"path": f"{spare_directory(slot, count)}/order_manifest.json",
                                           "sha256": sha256_bytes(
                                               files[f"{spare_directory(slot, count)}/order_manifest.json"])}}
                       for count in range(1, maximum + 1)],
    }


def stage_slot(stage: Mapping[str, Any]) -> str | None:
    """The NEG-8 slot of a plan-tree collection stage that launches a window reference directory."""

    if not isinstance(stage, Mapping) or stage.get("kind") != "campaign_collection":
        return None
    try:
        first = stage["launch"]["commands"][0]["argv_template"]["arguments"][0]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(first, Mapping) or first.get("kind") != "repo_path":
        return None
    for slot, (source_dir, *_rest) in SLOTS.items():
        if first.get("value") == source_dir:
            return slot
    return None


def attach_spare_retries(stages: Sequence[dict[str, Any]], repo_root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Add ``spare_retry`` to each window reference stage of a plan-tree stage graph (in place, returned)."""

    for stage in stages:
        slot = stage_slot(stage)
        if slot is not None:
            stage["spare_retry"] = spare_retry_record(slot, repo_root)
    return list(stages)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="verify the committed spare bytes")
    mode.add_argument("--write", action="store_true", help="write the spare bytes")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    try:
        if args.write:
            for relative in write(args.repo):
                print(f"wrote {relative}")
            return 0
        problems = check(args.repo)
    except SpareError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    for relative in problems:
        print(f"DIFFERS: {relative}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
