#!/usr/bin/env python3
"""Pin and inspect only explicitly named, locally generated R12 fixture roots.

Never copies, completes or edits a generated session/archive. The run-input
document and observation receipts are generator-owned files beside the trees.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_root(value):
    path = Path(value).absolute()
    if path.is_relative_to("/Users/edr") or "restricted" in path.parts:
        raise ValueError("forbidden R12 root")
    if path != path.resolve() or not path.is_relative_to(Path(tempfile.gettempdir()).resolve()):
        raise ValueError("R12 root must be resolved, non-symlinked, and below resolved TMPDIR")
    return path


def child(root, value):
    path = Path(value)
    if not path.is_absolute() or not path.is_relative_to(root):
        raise ValueError("fixture input escapes root")
    if path != path.resolve():
        raise ValueError("fixture input uses symlink")
    return path


def archive_pin(root, archive, metadata):
    """Hash actual writer outputs; do not infer custody from sidecar contents."""
    harvest = json.loads((archive / "harvest.json").read_bytes())
    if harvest.get("verdict") == "HARVEST_FAULT":
        raise ValueError("harvest fault is not a completed fixture")
    sums = archive / "sources/SHA256SUMS"
    files = {}
    for folder in ("derived", "withheld"):
        for path in sorted((archive / folder).rglob("*")):
            if path.is_file():
                name = str(path.relative_to(archive))
                digest = sha(path)
                if name in harvest["outputs"] and harvest["outputs"][name] != digest:
                    raise ValueError("writer output changed: " + name)
                files[name] = digest
    streams = sorted((archive / "sources/night-custody/hazards/meter").glob("stream-*.jsonl*"))
    names = sorted({str(path.relative_to(archive)).removesuffix(".zst") for path in streams})
    pin = {"harvest_sha256": sha(archive / "harvest.json"),
           "acceptance_sha256": sha(archive / "derived/b6-acceptance.json"),
           "sha256sums_sha256": sha(sums), "files": files, "meter_streams": names,
           "clock_journal": "sources/night-custody/hazards/monitor/clock.jsonl",
           "contention_journal": "sources/night-custody/hazards/monitor/contention.jsonl"}
    if not names:
        raise ValueError("actual meter writer stream absent")
    monitor = "sources/night-custody/hazards/monitor/"
    night = "sources/night-custody/night/"
    pin["copied_records"] = {
        "monitor_cost": [monitor + "monitor.jsonl"],
        "arm_host": ["sources/night-custody/hazards/arm.json", night + "arm_collectors.json"],
        "battery_phase": [monitor + "battery.jsonl"],
        "subject_temperature": [monitor + "thermal.jsonl"],
        "reference_history": ["derived/flags.jsonl", "withheld/b6-neg8.json"],
        "attempt_history": ["sources/night-custody/collection/idle_wait.jsonl", night + "chain-stages.jsonl"],
        "g10_history": [night + "hazard_result.json"],
        "block5_codes_carried": ["derived/flags.jsonl"]}
    log = Path(str(archive) + ".desk") / "compression.jsonl"
    if log.exists():
        paths = metadata["paths"]
        mappings = {str(archive): ".", paths["custody"]: "sources/night-custody"}
        for name in metadata["runs_roots"]:
            mappings[name] = "sources/bound-runs" if Path(name).name.endswith("_bound") else "sources/claim-runs"
        pin["compression"] = {"external_path": str(log), "sha256": sha(log), "relocations": mappings}
    return pin


def prepare_run_inputs(root):
    attempts_path = root / "loop/attempts.jsonl"
    attempts = [json.loads(line) for line in attempts_path.read_text().splitlines() if line]
    archives, pins = [], {}
    for attempt in attempts:
        metadata_path = root / "sessions" / attempt["session_id"] / "session.json"
        metadata = json.loads(metadata_path.read_text())
        archive = child(root, metadata["paths"]["archive"])
        archives.append(archive)
        pins[archive.name if archive.name != "archive" else str(archive)] = archive_pin(root, archive, metadata)
    # The production program selects pins by archive.name or full archive
    # spelling; repeated basename "archive" therefore needs explicit paths.
    document = root / "run-inputs.json"
    document.write_text(json.dumps({"host": "Air", "l9_audit": "not_run", "sessions": pins,
        "external": {"loop_attempts": sha(attempts_path), "loop_state": sha(root / "loop/state.json")}},
        indent=2, sort_keys=True) + "\n")
    return archives, attempts_path, document


def finalize_manifest(root):
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    reads = set()
    for receipt in root.glob("source-reads-*.jsonl"):
        reads.update(json.loads(line)["path"] for line in receipt.read_text().splitlines() if line)
    ran = {}
    generated = {}
    for name in sorted(reads):
        path = child(root, name)
        if not path.is_file():
            continue
        parts = path.parts
        relative = None
        for directory in ("joulewise", "scripts"):
            if directory in parts:
                relative = "/".join(parts[parts.index(directory):])
                break
        digest = sha(path)
        if relative in manifest["source_sha256"]:
            if digest != manifest["source_sha256"][relative]:
                raise ValueError("pinned chain code changed: " + name)
            ran[relative] = digest
        else:
            generated[str(path.relative_to(root))] = digest
    manifest["loaded_pinned_source_sha256"] = ran
    manifest["generated_program_sha256"] = generated
    manifest["source_call_receipts"] = {path.name: sha(path) for path in sorted(root.glob("source-calls-*.jsonl"))}
    manifest["volume"] = "mixed; see predeclared per-session source policies"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def run_option_c(root, workers=1, *, stem="option-c"):
    archives, attempts, document = prepare_run_inputs(root)
    numbers, public = root / (stem + "-numbers.json"), root / (stem + "-public.json")
    argv = [sys.executable, "-B", str(REPO / "scripts/independent_recompute_b6.py"), "block",
            *[value for archive in archives for value in ("--session", str(archive))],
            "--closed", "--loop-attempts", str(attempts), "--loop-state", str(root / "loop/state.json"),
            "--inputs", str(document), "--inputs-sha256", sha(document), "--workers", str(workers),
            "--restricted-out", str(numbers), "--public-out", str(public)]
    timed = ["/usr/bin/time", "-l", *argv]
    (root / (stem + "-argv.json")).write_text(json.dumps(timed, indent=2) + "\n")
    with (root / (stem + ".stdout")).open("wb") as out, (root / (stem + ".time")).open("wb") as err:
        result = subprocess.run(timed, cwd=REPO, stdout=out, stderr=err, check=False,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"})
    receipt = {"exit_code": result.returncode, "sessions": len(archives), "workers": workers,
               "program_sha256": sha(REPO / "scripts/independent_recompute_b6.py"),
               "inputs_sha256": sha(document)}
    if numbers.exists():
        value = json.loads(numbers.read_bytes())
        receipt["option_c"] = value.get("block", {}).get("option_c")
        receipt["numbers_sha256"] = sha(numbers)
    (root / (stem + "-receipt.json")).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--run-option-c", action="store_true")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    args = parser.parse_args(argv)
    root = safe_root(args.root)
    finalize_manifest(root)
    if args.run_option_c:
        return run_option_c(root, args.workers, stem="option-c" if args.workers == 1 else "option-c-pool")
    archives, _, document = prepare_run_inputs(root)
    print(json.dumps({"sessions": len(archives), "input_document": str(document)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
