#!/usr/bin/env python3
"""S-16, Block 5's half, row E (RL-140): the P* desk exclusion replayed on Block 5's idle-baseline rails.

Calls the PINNED desk function, ``joulewise.b6_analysis_hazards.desk_hazards`` at ``b5ab6a71d`` (SHA-256
``9a907a36…``), imported from a ``git archive`` of that commit, with the pinned sizing
``configs/b6/recompute/hazard_sizing.json`` (``bf399bec…``). No Block 6 analysis code is written here: this file
only hands the pinned function Block 5's bytes through a read adapter.

What the function reads, and what the adapter lets through:

- each science run's ``raw/powermetrics_idle.plist`` (the idle-baseline rails): passed whole;
- each run's ``metadata.json``: only ``model.name``;
- each run's ``summary_metrics.json``: only ``status`` (no phase energy reaches the function);
- ``withheld/spans.json``: only each run's request span;
- the contention monitor journal: passed whole (outside CPU time; the function needs it to run, its processor
  result is not reported here);
- ``derived/roster.json``.

Every file under ``sources/`` is checked against that root's ``sources/SHA256SUMS``, which is pinned by the Block 5
dry run's input census; ``spans.json`` and the roster are pinned below. The output is the count of runs the rule
removes and, as §8.3 item 3 prints it for the rehearsals, the largest baseline mean beside the lowest line.

Exit 0 on success, 4 on a refusal (including any InputRefusal of the pinned function: that is a STOP for RL-140).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PINNED_COMMIT = "b5ab6a71d"
DESK_SHA256 = "9a907a3671dbe210df4d417428c9108f0fdee1c16531bd0bef2fd39b0f27bb2b"
SIZING_SHA256 = "bf399bec4195b9237f53c747c6fc9cd24066610eba933a0fad767534d970d29b"
CONTENTION_JOURNAL = "sources/night-custody/hazards/monitor/contention.jsonl"
PACKS = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
PACK_ORDER = ("alpha", "beta", "gamma")

# SHA256SUMS digests are in B5-BLIND-DRY-RUN-RECORD.json's input census; spans.json is pinned at first read
# (2026-11-13); the rosters equal the counts script's pins.
SESSION_PINS: dict[str, dict[str, str]] = {
    "v5-b5-alpha-a1-20261009T2312Z": {
        "sources/SHA256SUMS": "01bc8bc20762f1abe397c9eb1496e73bc8cb11631b49fdea5f13d04c3cb15098",
        "withheld/spans.json": "a0ba8fd12cb597f2aaf590e33897fe514bb455aeba9254bdf3dcebfe168e27c6",
        "derived/roster.json": "f8170bf46cf976b246dad299967e38e0c4279fff41e056364d0ede6e834a184c",
    },
    "v5-b5-beta-a6-20261011T2011Z": {
        "sources/SHA256SUMS": "e2be240b1bd6b96955cbb6f0d1b82ff8adfab1d610567f0322ba1ddddc187356",
        "withheld/spans.json": "4372f4dfe22b74a633258107da688b33706a74a65cf1bfdf555985495593c00c",
        "derived/roster.json": "e67c15600998b1672e31ddbe795560ae989b42cb68411e55e1f7141b7edf3577",
    },
    "v5-b5-gamma-a1-20261012T0420Z": {
        "sources/SHA256SUMS": "128b251c6b3129524b69d227670ad438e12920bea57b340eb6c9aa14521b322a",
        "withheld/spans.json": "f85cd157538b078c128106aac922c6a74ccb715d099ed9b2d027829054f49098",
        "derived/roster.json": "87961bc79d9d6c475ac6f4944047d27efddb88d5fbcdefad19bb69d985c502e2",
    },
}


class Refusal(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_pinned(repo: Path, dest: Path) -> Path:
    """git archive the pinned commit's joulewise package and sizing into dest/pinned; check both digests."""
    tar_path = dest / "pinned.tar"
    with tar_path.open("wb") as fh:
        subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", PINNED_COMMIT, "joulewise",
                        "configs/b6/recompute/hazard_sizing.json"], stdout=fh, check=True)
    root = dest / "pinned"
    with tarfile.open(tar_path) as tf:
        tf.extractall(root, filter="data")
    desk = root / "joulewise/b6_analysis_hazards.py"
    if sha256_bytes(desk.read_bytes()) != DESK_SHA256:
        raise Refusal("desk_function_digest_mismatch")
    sizing_bytes = (root / "configs/b6/recompute/hazard_sizing.json").read_bytes()
    if sha256_bytes(sizing_bytes) != SIZING_SHA256:
        raise Refusal("hazard_sizing_digest_mismatch")
    return root


_PINNED: dict[str, Any] = {}


def import_pinned(root: Path):
    """Import the pinned desk function from an extracted archive; return (desk_hazards, InputRefusal, sizing)."""
    key = str(root)
    if key in _PINNED:
        return _PINNED[key]
    desk = root / "joulewise/b6_analysis_hazards.py"
    if sha256_bytes(desk.read_bytes()) != DESK_SHA256:
        raise Refusal("desk_function_digest_mismatch")
    sizing_bytes = (root / "configs/b6/recompute/hazard_sizing.json").read_bytes()
    if sha256_bytes(sizing_bytes) != SIZING_SHA256:
        raise Refusal("hazard_sizing_digest_mismatch")
    for name in list(sys.modules):
        if name == "joulewise" or name.startswith("joulewise."):
            raise Refusal(f"joulewise_already_imported: {name}")
    sys.path.insert(0, str(root))
    mod = importlib.import_module("joulewise.b6_analysis_hazards")
    if Path(mod.__file__).resolve() != desk.resolve():
        raise Refusal(f"desk_function_imported_from_elsewhere: {mod.__file__}")
    inputs = importlib.import_module("joulewise.b6_analysis_inputs")
    _PINNED[key] = (mod.desk_hazards, inputs.InputRefusal, json.loads(sizing_bytes))
    return _PINNED[key]


def evaluate(session: SimpleNamespace, desk_hazards, input_refusal, sizing,
             run_ids: list[str] | None = None) -> dict[str, Any]:
    """Run the pinned function on one session, or on a subset of its science runs (each run is independent)."""
    if run_ids is not None:
        keep = set(run_ids)
        session.roster = dict(session.roster, members=[m for m in session.roster["members"]
                                                       if m.get("run_id") in keep])
    try:
        result = desk_hazards(session, sizing)
    except input_refusal as exc:   # the pinned function cannot read this baseline: STOP (RL-140)
        raise Refusal(f"STOP: pinned desk function refused {session.plan_id}: {exc}") from exc
    return {"records": {rid: {k: rec[k] for k in ("P_x_w", "P_star_w", "per_model_would_remove")}
                        for rid, rec in result["records"].items()},
            "removed": list(result["power_removed"]), "files_read": len(session.reader.files_read)}


def _worker(job: tuple[str, str, list[str], bool]) -> tuple[str, dict[str, Any]]:
    pinned_root, harvest_root, run_ids, pinned = job
    desk_hazards, input_refusal, sizing = import_pinned(Path(pinned_root))
    session = session_for(Path(harvest_root), pinned=pinned)
    return harvest_root, evaluate(session, desk_hazards, input_refusal, sizing, run_ids)


class Block5Reader:
    """The read interface the pinned function calls (json, lines, raw), over one Block 5 harvest root.

    It verifies each ``sources/`` file against ``sources/SHA256SUMS`` and passes only the fields named in the
    module docstring.
    """

    def __init__(self, root: Path, sums: dict[str, str]) -> None:
        self.root = root
        self.sums = sums
        self.files_read: list[str] = []

    def _bytes(self, path: Path) -> bytes:
        data = path.read_bytes()
        rel = path.relative_to(self.root).as_posix()
        if rel.startswith("sources/"):
            want = self.sums.get(rel[len("sources/"):])
            if want is None:
                raise Refusal(f"source_not_in_sha256sums: {rel}")
            if sha256_bytes(data) != want:
                raise Refusal(f"source_digest_mismatch: {rel}")
        self.files_read.append(rel)
        return data

    def json(self, path: Path, scope: str, required: bool = True) -> Any:
        value = json.loads(self._bytes(Path(path)))
        name = Path(path).name
        if name == "summary_metrics.json":
            return {"status": value.get("status")}
        if name == "metadata.json":
            return {"model": {"name": (value.get("model") or {}).get("name")}}
        if name == "spans.json":
            return {"spans": {rid: {"request": v.get("request")} for rid, v in (value.get("spans") or {}).items()}}
        if name == "roster.json":
            return value
        raise Refusal(f"unexpected_json_read: {path}")

    def lines(self, path: Path, scope: str, required: bool = True) -> list[dict[str, Any]]:
        if Path(path).name != "contention.jsonl":
            raise Refusal(f"unexpected_lines_read: {path}")
        return [json.loads(line) for line in self._bytes(Path(path)).splitlines() if line.strip()]

    def raw(self, path: Path, scope: str, required: bool = True) -> bytes:
        if Path(path).name != "powermetrics_idle.plist":
            raise Refusal(f"unexpected_raw_read: {path}")
        return self._bytes(Path(path))


def session_for(root: Path, *, pinned: bool) -> SimpleNamespace:
    roster_bytes = (root / "derived/roster.json").read_bytes()
    roster = json.loads(roster_bytes)
    plan_id = roster["plan_id"]
    pack = plan_id.split("-")[2]
    if pack not in PACKS:
        raise Refusal(f"pack_unparsed: {plan_id}")
    if pinned:
        pins = SESSION_PINS.get(plan_id)
        if pins is None:
            raise Refusal(f"session_not_released_three: {plan_id}")
        for rel, want in pins.items():
            if sha256_bytes((root / rel).read_bytes()) != want:
                raise Refusal(f"session_input_digest_mismatch: {plan_id}: {rel}")
    sums = {}
    for line in (root / "sources/SHA256SUMS").read_text().splitlines():
        if line.strip():
            digest, rel = line.split(None, 1)
            sums[rel.strip()] = digest
    return SimpleNamespace(reader=Block5Reader(root, sums), archive=root, plan_id=plan_id, pack_key=pack,
                           pack=PACKS[pack], roster=roster, claim_root=root / "sources/claim-runs",
                           input_pin={"contention_journal": CONTENTION_JOURNAL})


def fmt_mw(watts: float) -> str:
    return f"{watts * 1000:.2f}"


def run_parallel(roots: list[Path], pinned_root: Path, jobs: int, pinned: bool) -> dict[str, dict[str, Any]]:
    from concurrent.futures import ProcessPoolExecutor
    tasks = []
    for root in roots:
        roster = json.loads((root / "derived/roster.json").read_text())
        science = [m["run_id"] for m in roster["members"] if m.get("kind", "science") == "science"]
        n = max(1, -(-len(science) // max(1, jobs)))
        tasks += [(str(pinned_root), str(root), science[i:i + n], pinned) for i in range(0, len(science), n)]
    merged: dict[str, dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        for root, part in pool.map(_worker, tasks):
            m = merged.setdefault(root, {"records": {}, "removed": [], "files_read": 0})
            m["records"].update(part["records"])
            m["removed"] += part["removed"]
            m["files_read"] += part["files_read"]
    return merged


def replay(roots: list[Path], desk_hazards, input_refusal, sizing, *, pinned: bool,
           precomputed: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    sessions = sorted((session_for(r, pinned=pinned) for r in roots), key=lambda s: PACK_ORDER.index(s.pack_key))
    if pinned and sorted(s.plan_id for s in sessions) != sorted(SESSION_PINS):
        raise Refusal("session_set_differs_from_released_three")
    out: dict[str, Any] = {"sessions": [], "removed_by_pack": {}, "per_model_removed_by_pack": {}}
    max_px, lowest_line = None, None
    for s in sessions:
        science = [m for m in s.roster["members"] if m.get("kind", "science") == "science"]
        if precomputed is not None:
            result = precomputed[str(s.archive)]
        else:
            result = evaluate(s, desk_hazards, input_refusal, sizing)
        records = result["records"]
        pxs = [rec["P_x_w"] for rec in records.values()]
        lines = [rec["P_star_w"] for rec in records.values()]
        removed = sorted(result["removed"])
        out["removed_by_pack"][s.pack_key] = len(removed)
        out["per_model_removed_by_pack"][s.pack_key] = sum(1 for rec in records.values()
                                                          if rec["per_model_would_remove"])
        out["sessions"].append({
            "plan_id": s.plan_id, "pack": s.pack, "runs": len(s.roster["members"]), "science_runs": len(science),
            "science_runs_examined": len(records), "science_runs_not_examined": len(science) - len(records),
            "removed": len(removed), "removed_run_ids": removed,
            "max_baseline_mean_w": max(pxs) if pxs else None,
            "lowest_line_w": min(lines) if lines else None,
            "files_read": result["files_read"],
        })
        if pxs:
            max_px = max(pxs) if max_px is None else max(max_px, max(pxs))
            lowest_line = min(lines) if lowest_line is None else min(lowest_line, min(lines))
    total_runs = sum(s["runs"] for s in out["sessions"])
    examined = sum(s["science_runs_examined"] for s in out["sessions"])
    removed = sum(out["removed_by_pack"].values())
    by_pack = ", ".join(str(out["removed_by_pack"][p]) for p in PACK_ORDER if p in out["removed_by_pack"])
    out.update(
        schema="joulewise.b6_s16_block5_pstar.v1", pinned_commit=PINNED_COMMIT, desk_sha256=DESK_SHA256,
        sizing_sha256=SIZING_SHA256, runs=total_runs, science_runs_examined=examined, removed=removed,
        max_baseline_mean_w=max_px, lowest_line_w=lowest_line,
        max_baseline_mean_mw_text=fmt_mw(max_px) if max_px is not None else None,
        lowest_line_w_text=f"{lowest_line:.3g}" if lowest_line is not None else None,
        sentence=(f"removes {removed} of {total_runs} runs ({by_pack}); largest baseline mean "
                  f"{fmt_mw(max_px)} mW against the lowest line {lowest_line:.3g} W") if max_px is not None else None,
    )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1],
                    help="a git repository holding the pinned commit")
    ap.add_argument("--session", type=Path, action="append", required=True, help="a Block 5 harvest root")
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--unpinned", action="store_true", help="skip the session pins (synthetic fixtures)")
    ap.add_argument("--jobs", type=int, default=1, help="worker processes (each runs the pinned function on a "
                                                        "subset of one session's science runs)")
    args = ap.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            pinned_root = extract_pinned(args.repo, Path(tmp))
            if args.jobs > 1:
                pre = run_parallel(args.session, pinned_root, args.jobs, not args.unpinned)
                result = replay(args.session, None, None, None, pinned=not args.unpinned, precomputed=pre)
            else:
                desk_hazards, input_refusal, sizing = import_pinned(pinned_root)
                result = replay(args.session, desk_hazards, input_refusal, sizing, pinned=not args.unpinned)
    except Refusal as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 4
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 4
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.write_text(text)
    print(result["sentence"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
