#!/usr/bin/env python3
"""Pin and inspect only explicitly named, locally generated R12 fixture roots.

Never copies, completes or edits a generated session/archive. The run-input
document and observation receipts are generator-owned files beside the trees.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
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
os.environ["XDG_CONFIG_HOME"] = str(Path(tempfile.gettempdir()).resolve() / "r12-xdg-empty")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
LOADED_VERIFIER_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
PROGRAM_ARGV_SCHEMA = "r12.program_argv.v1"


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


def prediction_sources(commit, repo=REPO):
    """Recover declarations from the immutable commit bound before generation.

    Never use later working files to turn an observation into a prediction.
    The generated manifest already carries this commit; these explicit blob
    hashes and original docstrings make that binding directly auditable.
    """
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("invalid generator commit")
    sources = {}
    declarations = {}
    for name in ("tests/test_b6_r12_session_fixture.py", "docs/run_reports/2026-11-11-p1-b6-r12-r3.md"):
        data = subprocess.check_output(["git", "show", commit + ":" + name], cwd=repo)
        sources[name] = hashlib.sha256(data).hexdigest()
        if name.endswith(".py"):
            for node in ast.parse(data).body:
                if isinstance(node, ast.ClassDef) and node.name == "DeclaredShapeTests":
                    declarations = {method.name: ast.get_docstring(method) for method in node.body
                                    if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")}
    if not declarations or not all(declarations.values()):
        raise ValueError("bound generator commit lacks pre-run shape declarations")
    return {"schema": "r12.pre_run_predictions.v1", "generator_commit": commit,
            "source_sha256": sources, "test_docstrings": declarations}


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
    manifest["git_blob_input_receipts"] = {path.name: sha(path) for path in sorted(root.glob("git-blob-input-queries-*.jsonl"))}
    manifest["volume"] = "mixed; see predeclared per-session source policies"
    manifest["pre_run_prediction_sources"] = prediction_sources(manifest["generator_commit"])
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def rows(data):
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def session_facts(root, session_id):
    """Read actual archived writer outputs, never construct an expected result."""
    from joulewise.b6_analysis_inputs import AuthenticatedInputs
    metadata = json.loads((root / "sessions" / session_id / "session.json").read_bytes())
    actual_attempts = [row for row in rows((root / "loop/attempts.jsonl").read_bytes())
                       if row["session_id"] == session_id]
    if len(actual_attempts) != 1:
        raise ValueError("one original loop attempt required")
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
            "off_actions": off_actions, "real_loop_attempt": bool(actual_attempts)}


def meter_facts(data):
    """Bounded-memory wire census; original protocol decoder supplies sample layout."""
    from joulewise.external.km003c_parse import SAMPLE, STEP_MS, WRAP
    header = None
    polls = total = kept = duplicates = dropped = irregular = 0
    previous_seq = previous_rx = running_max = None
    current = first = last = 0
    for line in io.BytesIO(data):
        row = json.loads(line)
        if row.get("k") == "h":
            header = row
        if row.get("k") != "b":
            continue
        polls += 1
        for index, sample in enumerate(SAMPLE.iter_unpack(bytes.fromhex(row.get("p") or ""))):
            seq = sample[0]
            total += 1
            if previous_seq is None:
                current = 0
            else:
                delta = ((seq - previous_seq + WRAP // 2) % WRAP) - WRAP // 2
                if index == 0 and previous_rx is not None:
                    host_ms = (row["rx"] - previous_rx) / 1e6
                    if host_ms > WRAP // 2:
                        delta += round((host_ms - delta) / WRAP) * WRAP
                current += delta
            previous_seq = seq
            if running_max is not None and current <= running_max:
                duplicates += 1
                continue
            if kept:
                gap = current - last
                step = STEP_MS[header["rate_idx"]]
                dropped += max(0, gap // step - 1)
                irregular += bool(gap % step)
            else:
                first = current
            kept += 1
            last = running_max = current
        previous_rx = row["rx"]
    if header is None:
        raise ValueError("original meter header missing")
    return {"sps": header["sps"], "poll_s": header["poll_s"], "polls": polls,
            "wire_samples": total, "samples": kept, "duplicates": duplicates,
            "step_ms": STEP_MS[header["rate_idx"]], "span_s": (last - first) / 1000,
            "drops": {"kept": kept, "dropped": dropped, "irregular_gaps": irregular,
                      "drop_fraction": dropped / (kept + dropped) if kept + dropped else None}}


def primary_plist_names(names):
    """Primary capture layout, excluding calibration copies and validation runs."""
    return sorted(name for name in names if re.fullmatch(
        r"sources/(?:claim|bound)-runs/[^/]+/raw/powermetrics\.plist", name))


def volume_facts(root, session_id):
    """Count native frames/cadence and actual meter rows without refitting decisions.

    Each source plist document has elapsed_ns. Counting those wire fields is
    independent of the source-policy duration declaration. No bundle is edited.
    """
    from joulewise.b6_analysis_inputs import AuthenticatedInputs
    metadata = json.loads((root / "sessions" / session_id / "session.json").read_bytes())
    archive = child(root, metadata["paths"]["archive"])
    reader = AuthenticatedInputs(archive, archive_pin(root, archive, metadata))
    plist = []
    for name in primary_plist_names(reader.expected):
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
            meter.append({"path": name, **meter_facts(reader.read(archive / name))})
    monitor = {}
    for name in reader.expected:
        if name.startswith("sources/night-custody/hazards/monitor/") and name.endswith(".jsonl"):
            data = rows(reader.read(archive / name))
            by_kind = {}
            for row in data:
                stamp = row.get("started", {}).get("monotonic_ns")
                if isinstance(stamp, int):
                    kind = row.get("kind", "unknown")
                    source = (row.get("values") or {}).get("source")
                    key = kind + ":" + source if isinstance(source, str) else kind
                    by_kind.setdefault(key, []).append(stamp)
            monitor[name] = {"rows": len(data), "errors": sum(bool(row.get("error")) for row in data),
                            "kinds": {kind: {
                "rows": len(times), "span_s": (times[-1] - times[0]) / 1e9,
                "cadence_ns": sorted({b - a for a, b in zip(times, times[1:])})}
                for kind, times in by_kind.items()}}
    config_path = archive / "sources/night-custody/hazards/monitor/config.json"
    config = json.loads(reader.read(config_path))
    declaration = root / "fixture-manifests" / (session_id + ".json")
    compression_log = Path(str(archive) + ".desk/compression.jsonl")
    native_generation = None
    if declaration.is_file() and compression_log.is_file():
        start_ns = declaration.stat().st_mtime_ns
        end_ns = compression_log.stat().st_mtime_ns
        if end_ns < start_ns:
            raise ValueError("native generation timestamps are reversed")
        native_generation = {"method": "native filesystem mtimes: pre-run declaration through final desk compression log",
            "start_mtime_ns": start_ns, "end_mtime_ns": end_ns, "wall_s": (end_ns - start_ns) / 1e9,
            "declaration_sha256": sha(declaration), "compression_log_sha256": sha(compression_log),
            "primary_stream_duration_s": sum(item["duration_s"] for item in plist),
            "includes_validation_and_compression": True, "injected_clock": False}
    return {"session_id": session_id, "primary_plists": plist, "meter": meter, "monitor": monitor,
            "registered_monitor_cadence": config["cadence"],
            "native_generation": native_generation,
            "archive_pin_sha256": hashlib.sha256(json.dumps(reader.record, sort_keys=True).encode()).hexdigest()}


def run_option_c(root, workers=1, *, stem="option-c", session_id=None):
    verifier_sha256 = sha(Path(__file__))
    if verifier_sha256 != LOADED_VERIFIER_SHA256:
        raise RuntimeError("verifier changed after import; reload before producing evidence")
    verifier_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    # The serial/pool byte comparison must use the exact same input-document
    # path as well as the same bytes. Output destinations may differ.
    input_stem = stem.removesuffix("-pool") if workers > 1 else stem
    archives, attempts, document = prepare_run_inputs(root, counting_only=session_id is None,
                                                     session_id=session_id, stem=input_stem)
    numbers, public = root / (stem + "-numbers.json"), root / (stem + "-public.json")
    argv = [sys.executable, "-B", str(REPO / "scripts/independent_recompute_b6.py"), "block",
            *[value for archive in archives for value in ("--session", str(archive))],
            *(["--closed"] if session_id is None else []),
            "--loop-attempts", str(attempts), "--loop-state", str(root / "loop/state.json"),
            "--inputs", str(document), "--inputs-sha256", sha(document), "--workers", str(workers),
            "--restricted-out", str(numbers), "--public-out", str(public)]
    program_argv = root / (stem + "-program-argv.json")
    program_argv.write_text(json.dumps({"schema": PROGRAM_ARGV_SCHEMA,
        "verifier_sha256": LOADED_VERIFIER_SHA256, "argv": argv}, indent=2) + "\n")
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
               "archives": [str(archive) for archive in archives], "closed": session_id is None,
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
    document = json.loads(child(root, argv_file).read_text())
    if (not isinstance(document, dict) or document.get("schema") != PROGRAM_ARGV_SCHEMA
            or document.get("verifier_sha256") != LOADED_VERIFIER_SHA256):
        # An auxiliary watcher may outlive an implementation increment. It
        # must stop before scientific work, rather than attribute old loaded
        # functions to the new file hash. This is a harness cancellation,
        # never a production recomputation result.
        receipt = {"exit_code": 98, "harness_cancelled": True,
                   "reason": "stale or unversioned verifier invocation; reload required"}
        (root / (stem + "-process.json")).write_text(json.dumps(receipt, indent=2) + "\n")
        return 98
    argv = document["argv"]
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
        receipt_name = "option-c-skips-receipt.json" if label == "r12-skips" else "option-c-receipt.json"
        receipt = skipped_receipt if label == "r12-skips" else block_receipt
        if value["archive"] not in receipt["archives"]:
            receipt_name = "option-c-" + sid + "-receipt.json"
            receipt = json.loads((root / receipt_name).read_bytes())
        if value["archive"] not in receipt["archives"]:
            raise ValueError("shape archive not checked by its program receipt")
        value.update(production_exit=receipt["exit_code"],
                     comparator_agrees=bool(receipt.get("option_c", {}).get("comparator", {}).get("pass")),
                     program_receipt_sha256=sha(root / receipt_name))
        if label == "r12-gamma-cross":
            gamma = next(r for r in block["sessions"].values() if r["pack"] == "GAMMA" and r["round"] == 1)
            value["pairing"] = gamma["pairing"]
            value["kept_units"] = gamma["kept_units"]
            has_unit = any(units for strata in gamma["kept_units"].values() for units in strata.values())
            value["cross_session_gamma"] = has_unit and bool(gamma["pairing"]) and all(
                p.get("session_id") and p["session_id"] != gamma["session_id"]
                for p in gamma["pairing"].values())
        observed[label] = value
    value = session_facts(denied_root, "r1-alpha")
    if value["archive"] not in denied_receipt["archives"]:
        raise ValueError("denied-action archive not checked by its program receipt")
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
