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
import re
import subprocess
import sys
import tempfile

os.environ.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_ATTR_NOSYSTEM="1",
                  PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
                  PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin")

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


def prepare_run_inputs(root, *, counting_only=True, session_id=None, stem="run"):
    attempts_path = root / "loop/attempts.jsonl"
    attempts = [json.loads(line) for line in attempts_path.read_text().splitlines() if line]
    archives, pins = [], {}
    for attempt in attempts:
        if session_id is not None and attempt["session_id"] != session_id:
            continue
        if counting_only and not any(row.get("status") == "counting" for row in attempt.get("outcomes", {}).values()):
            continue
        metadata_path = root / "sessions" / attempt["session_id"] / "session.json"
        metadata = json.loads(metadata_path.read_text())
        archive = child(root, metadata["paths"]["archive"])
        archives.append(archive)
        pins[archive.name if archive.name != "archive" else str(archive)] = archive_pin(root, archive, metadata)
    # The production program selects pins by archive.name or full archive
    # spelling; repeated basename "archive" therefore needs explicit paths.
    if not archives:
        raise ValueError("no actual completed loop attempt selected")
    document = root / (stem + "-inputs.json")
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


def rows(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def session_facts(root, session_id):
    """Read actual archived writer outputs, never construct an expected result."""
    from joulewise.b6_analysis_inputs import AuthenticatedInputs
    metadata = json.loads((root / "sessions" / session_id / "session.json").read_bytes())
    archive = child(root, metadata["paths"]["archive"])
    pin = archive_pin(root, archive, metadata)
    reader = AuthenticatedInputs(archive, pin)
    acceptance = json.loads(reader.read(archive / "derived/b6-acceptance.json"))
    roster = json.loads(reader.read(archive / "derived/roster.json"))
    flags = []
    for name in ("derived/flags.jsonl", "derived/b6-flags.jsonl"):
        if name in reader.expected:
            flags += rows(reader.read(archive / name))
    campaign = rows(reader.read(archive / "sources/claim-runs/campaign_log.jsonl"))
    kinds = set()
    for row in campaign:
        if row.get("record_type") == "idle_admission_whole_window_verdict":
            kinds.add("evaluation")
        elif row.get("config") and row.get("members"):
            kinds.add("member")
    attempts = [(int(match[1]), name) for name in reader.expected
                if (match := re.search(r"rich_telemetry_idle_attempt_(\d+)\.jsonl$", name))]
    log = Path(str(archive) + ".desk/compression.jsonl")
    compressed = [row for row in rows(log.read_bytes()) if row.get("event") == "compress"] if log.exists() else []
    arm = json.loads(reader.read(archive / "sources/night-custody/hazards/arm.json"))
    # Keep the original record rather than assuming which nested action key
    # a pinned arm version uses. The caller can inspect the whole raw action.
    off_actions = []
    def visit(value):
        if isinstance(value, dict):
            argv = value.get("argv", value.get("command", []))
            if isinstance(argv, list) and "-setusingnetworktime" in argv and "off" in argv:
                off_actions.append(value)
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
    visit(arm)
    return {"session_id": session_id, "archive": str(archive), "acceptance": acceptance,
            "roster_members": len(roster["members"]),
            "flags": sorted({row["code"] for row in flags}),
            "max_idle_attempt": max((number for number, _ in attempts), default=0),
            "attempt_telemetry": [name for _, name in sorted(attempts)],
            "campaign_row_kinds": sorted(kinds), "campaign_rows": len(campaign),
            "compressed_campaign_logs": sum(row["path"].endswith("campaign_log.jsonl") for row in compressed),
            "compressed_plists": sum(row["path"].endswith(".plist") for row in compressed),
            "off_actions": off_actions, "real_loop_attempt": True}


def volume_facts(root, session_id):
    """Count native frames/cadence and actual meter rows without refitting decisions.

    Each source plist document has elapsed_ns. Counting those wire fields is
    independent of the source-policy duration declaration. No bundle is edited.
    """
    from joulewise.b6_analysis_inputs import AuthenticatedInputs
    from joulewise.external.km003c_parse import samples, drops
    metadata = json.loads((root / "sessions" / session_id / "session.json").read_bytes())
    archive = child(root, metadata["paths"]["archive"])
    reader = AuthenticatedInputs(archive, archive_pin(root, archive, metadata))
    plist = []
    for name in sorted(reader.expected):
        if not (name.startswith(("sources/claim-runs/", "sources/bound-runs/"))
                and name.endswith("/raw/powermetrics.plist") and "instrument_validation/" not in name):
            continue
        data = reader.read(archive / name)
        elapsed = [int(value) for value in re.findall(rb"<key>elapsed_ns</key>\s*<integer>(\d+)</integer>", data)]
        frames = data.count(b"</plist>")
        plist.append({"path": name, "bytes": len(data), "frames": frames,
                      "elapsed_fields": len(elapsed), "duration_s": sum(elapsed) / 1e9,
                      "cadence_ns": sorted(set(elapsed)),
                      "cpu_fields": data.count(b"<key>cpu</key>")})
    meter = []
    for name in reader.expected:
        if name.startswith("sources/night-custody/hazards/meter/stream-") and name.endswith(".jsonl"):
            data = rows(reader.read(archive / name))
            header = next(row for row in data if row.get("k") == "h")
            batch = [row for row in data if row.get("k") == "b"]
            parsed = samples(header, batch)
            meter.append({"path": name, "sps": header["sps"], "poll_s": header["poll_s"],
                          "polls": len(batch), "samples": len(parsed.dev_ms), "step_ms": parsed.step_ms,
                          "span_s": (parsed.dev_ms[-1] - parsed.dev_ms[0]) / 1000 if parsed.dev_ms else 0,
                          "drops": drops(parsed)})
    monitor = {}
    for name in reader.expected:
        if name.startswith("sources/night-custody/hazards/monitor/") and name.endswith(".jsonl"):
            data = rows(reader.read(archive / name))
            monitor[name] = {"rows": len(data)}
    return {"session_id": session_id, "primary_plists": plist, "meter": meter, "monitor": monitor,
            "archive_pin_sha256": hashlib.sha256(json.dumps(reader.record, sort_keys=True).encode()).hexdigest()}


def run_option_c(root, workers=1, *, stem="option-c", session_id=None):
    verifier_sha256 = sha(Path(__file__))
    verifier_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    archives, attempts, document = prepare_run_inputs(root, counting_only=session_id is None,
                                                     session_id=session_id, stem=stem)
    numbers, public = root / (stem + "-numbers.json"), root / (stem + "-public.json")
    argv = [sys.executable, "-B", str(REPO / "scripts/independent_recompute_b6.py"), "block",
            *[value for archive in archives for value in ("--session", str(archive))],
            *(["--closed"] if session_id is None else []),
            "--loop-attempts", str(attempts), "--loop-state", str(root / "loop/state.json"),
            "--inputs", str(document), "--inputs-sha256", sha(document), "--workers", str(workers),
            "--restricted-out", str(numbers), "--public-out", str(public)]
    program_argv = root / (stem + "-program-argv.json")
    program_argv.write_text(json.dumps(argv, indent=2) + "\n")
    timed = ["/usr/bin/time", "-l", sys.executable, "-B", str(Path(__file__).resolve()),
             "--root", str(root), "--exec-argv", str(program_argv), "--stem", stem]
    (root / (stem + "-argv.json")).write_text(json.dumps(timed, indent=2) + "\n")
    with (root / (stem + ".stdout")).open("wb") as out, (root / (stem + ".time")).open("wb") as err:
        result = subprocess.run(timed, cwd=REPO, stdout=out, stderr=err, check=False,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"})
    child_receipt = json.loads((root / (stem + "-process.json")).read_text())
    receipt = {"exit_code": child_receipt["exit_code"], "time_wrapper_exit": result.returncode,
               "verifier_sha256": verifier_sha256, "verifier_commit": verifier_commit,
               "process_measurement": child_receipt, "sessions": len(archives), "workers": workers,
               "program_sha256": sha(REPO / "scripts/independent_recompute_b6.py"),
               "inputs_sha256": sha(document), "session_id": session_id}
    if numbers.exists():
        value = json.loads(numbers.read_bytes())
        receipt["option_c"] = value.get("block", {}).get("option_c")
        receipt["numbers_sha256"] = sha(numbers)
    (root / (stem + "-receipt.json")).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return child_receipt["exit_code"]


def execute_argv(root, argv_file, stem):
    """Retain the program exit even if macOS time -l's sysctl is denied."""
    import resource
    import time
    argv = json.loads(child(root, argv_file).read_text())
    if not (len(argv) > 2 and argv[:2] == [sys.executable, "-B"]
            and Path(argv[2]) == REPO / "scripts/independent_recompute_b6.py"):
        raise ValueError("only the declared local B6 program may be measured")
    started = time.monotonic()
    temporary = root / "analysis-tmp"
    temporary.mkdir(exist_ok=True)
    result = subprocess.run(argv, cwd=REPO, check=False, env={**os.environ, "TMPDIR": str(temporary)})
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = {"exit_code": result.returncode, "wall_s": time.monotonic() - started,
               "peak_rss": usage.ru_maxrss, "peak_rss_units": "bytes" if sys.platform == "darwin" else "KiB",
               "peak_rss_method": "getrusage(RUSAGE_CHILDREN).ru_maxrss; fallback, not time -l",
               "user_s": usage.ru_utime, "system_s": usage.ru_stime}
    (root / (stem + "-process.json")).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return result.returncode


def write_observations(root, denied_root):
    """Join verified program receipts and raw collection facts, never predictions."""
    block_receipt = json.loads((root / "option-c-receipt.json").read_bytes())
    block = json.loads((root / "option-c-numbers.json").read_bytes())
    skipped_receipt = json.loads((root / "option-c-skips-receipt.json").read_bytes())
    denied_receipt = json.loads((denied_root / "option-c-denied-receipt.json").read_bytes())
    observed = {}
    for label, sid in {"r12-waited": "r2-alpha", "r12-skips": "r1-alpha",
                       "r12-anchor": "r2-beta", "r12-mixed": "r1-beta",
                       "r12-compressed": "r1-beta", "r12-gamma-cross": "r1-gamma"}.items():
        value = session_facts(root, sid)
        receipt = skipped_receipt if label == "r12-skips" else block_receipt
        value.update(production_exit=receipt["exit_code"],
                     comparator_agrees=bool(receipt.get("option_c", {}).get("comparator", {}).get("pass")),
                     program_receipt_sha256=sha(root / ("option-c-skips-receipt.json" if label == "r12-skips"
                                                       else "option-c-receipt.json")))
        if label == "r12-gamma-cross":
            gamma = next(r for r in block["sessions"].values() if r["pack"] == "GAMMA" and r["round"] == 1)
            value["pairing"] = gamma["pairing"]
            value["cross_session_gamma"] = all(p.get("session_id") and p["session_id"] != gamma["session_id"]
                                                for p in gamma["pairing"].values())
        observed[label] = value
    value = session_facts(denied_root, "r1-alpha")
    value.update(production_exit=denied_receipt["exit_code"],
                 comparator_agrees=bool(denied_receipt.get("option_c", {}).get("comparator", {}).get("pass")))
    value["off_action_returncode"] = next((action.get("returncode") for action in value["off_actions"]), None)
    observed["r12-denied-action"] = value
    (root / "observations.json").write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n")
    full = {sid: volume_facts(root, sid) for sid in ("r3-alpha", "r1-beta", "r1-gamma")}
    (root / "full-volume-observations.json").write_text(json.dumps(full, indent=2, sort_keys=True) + "\n")
    return observed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--run-option-c", action="store_true")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=1)
    parser.add_argument("--exec-argv")
    parser.add_argument("--stem", default="option-c")
    parser.add_argument("--session-id", help="one actual loop attempt, including a non-counting shape")
    parser.add_argument("--observe-denied-root", help="join final facts after both roots' option-(c) runs")
    args = parser.parse_args(argv)
    root = safe_root(args.root)
    if args.exec_argv:
        return execute_argv(root, args.exec_argv, args.stem)
    finalize_manifest(root)
    if args.observe_denied_root:
        write_observations(root, safe_root(args.observe_denied_root))
        return 0
    if args.run_option_c:
        return run_option_c(root, args.workers, session_id=args.session_id,
                            stem=args.stem if args.workers == 1 else args.stem + "-pool")
    archives, _, document = prepare_run_inputs(root)
    print(json.dumps({"sessions": len(archives), "input_document": str(document)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
