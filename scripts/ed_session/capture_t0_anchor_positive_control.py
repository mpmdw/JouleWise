#!/usr/bin/env python3
"""Ed-owned, pre-window physical RAW-anchor control using the reviewed ON/OFF vector.

Ed runs this helper himself against real, un-authored T-0 inputs. Network time
is enabled once, the RAW anchor is polled to a bounded deadline, and OFF is
always attempted in finally. Synthetic inputs are only test evidence.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import signal
import threading
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from joulewise import arm_readiness as readiness
from joulewise import arm_readiness_evidence_t0 as author
from joulewise import clock_reference, network_time_off, t0_rehearsal

ON_ARGV = (*network_time_off.OFF_ARGV[:-1], "on")
REFUSAL = "evidence_author_t0_clock_attestation_underivable"
ANCHOR_DETAIL = "R0-to-author RAW anchor delta exceeds 5000000 ns"


class NotDischarged(ValueError):
    pass


def write_bytes(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def write_json(path, value):
    write_bytes(path, readiness.render_json(value))


def read_json(path):
    if path.is_symlink():
        raise NotDischarged("symlink_in_custody")
    return readiness.parse_json_bytes(path.read_bytes(), require_canonical=True)


def stamp():
    return {**asdict(clock_reference.sample_anchor()),
            "monotonic_ns": time.monotonic_ns(),
            "boot_id": network_time_off.boot_id()}


def anchor(value):
    return value["realtime_ns"] - value["monotonic_raw_ns"]


def run_command(argv, *, timeout):
    return subprocess.run(argv, capture_output=True, timeout=timeout, check=False,
                          cwd=REPO_ROOT, stdin=subprocess.DEVNULL)


def execute_command(root, label, argv, timeout, sample, runner):
    """Retain exact argv, actual exit and separated streams for the ON command."""
    started = sample()
    completed = runner(argv, timeout=timeout)
    finished = sample()
    directory = root / "commands" / label
    for name, value in (("stdout.txt", completed.stdout), ("stderr.txt", completed.stderr)):
        write_bytes(directory / name, value if isinstance(value, bytes) else value.encode())
    write_json(directory / "started.json", started)
    write_json(directory / "finished.json", finished)
    result = {"argv": list(argv), "exit_code": completed.returncode,
              "stdout": network_time_off._text(completed.stdout),
              "stderr": network_time_off._text(completed.stderr),
              "started": started, "finished": finished}
    write_json(root / "commands" / f"{label}.json", result)
    return result


def snapshot_inputs(source, target):
    if source.is_symlink() or not source.is_dir():
        raise NotDischarged("author_inputs_not_regular")
    # Copy bytes, never rewrite captures or their absolute replay locators.
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise NotDischarged("author_input_symlink")
        if path.is_file():
            write_bytes(target / path.relative_to(source), path.read_bytes())
    for filename in author._CAPTURE_FILES.values():
        if not (target / filename).is_file():
            raise NotDischarged("author_capture_missing")


@contextmanager
def _uninterrupted_off():
    saved = {}
    if threading.current_thread() is threading.main_thread():
        for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            saved[number] = signal.signal(number, signal.SIG_IGN)
    try:
        yield
    finally:
        for number, handler in saved.items():
            signal.signal(number, handler)


def run_control(*, pack_root, author_inputs, custody_root, resync_timeout_s=120,
                sample=stamp, runner=run_command, monotonic_ns=time.monotonic_ns,
                sleep=time.sleep):
    """Ed's single attempt: reviewed ON, bounded anchor polling, author, then OFF."""
    if type(resync_timeout_s) is not int or not 1 <= resync_timeout_s <= 300:
        raise NotDischarged("resync_timeout_out_of_range")
    root = Path(custody_root).absolute()
    source = Path(author_inputs).resolve(strict=True)
    if root.resolve().is_relative_to(source) or source.is_relative_to(root.resolve()):
        raise NotDischarged("control_custody_not_isolated")
    pack = Path(pack_root).resolve(strict=True)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    inputs = root / "author-custody" / pack.name / author._INPUT_DIRECTORY
    outcome = {"status": "NOT-DISCHARGED", "reason": "control_incomplete"}
    boot = None
    positive = None
    try:
        snapshot_inputs(source, inputs)
        before = sample()
        write_json(root / "before.json", before)
        boot = before["boot_id"]
        reference_capture = read_json(inputs / "clock-reference.json")
        r0 = readiness.parse_json_bytes(reference_capture["stdout"].encode())
        # Bind the observed step to the unchanged real author's R0 sequence.
        # The real author owns span/quorum/order admission and its exact refusal.
        if r0["boot_session_id"].lower() != boot:
            raise NotDischarged("r0_boot_mismatch")
        span = before["monotonic_raw_ns"] - r0["anchor_monotonic_raw_ns"]
        if not 600_000_000_000 <= span <= (3600 - resync_timeout_s - 120) * 1_000_000_000:
            raise NotDischarged("pre_on_author_span_out_of_range")
        if abs(r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"] - anchor(before)) > 5_000_000:
            raise NotDischarged("author_sequence_already_above_anchor_bound")
        write_json(root / "author-input-lineage.json", {
            "input_source": str(Path(author_inputs).resolve()),
            "pack_root": str(pack), "r0_anchor_ns": r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"],
            "boot_id": boot,
            "author_code_sha256": {p: readiness.sha256_bytes((REPO_ROOT / p).read_bytes())
                for p in ("scripts/author_arm_evidence_t0.py", "joulewise/arm_readiness_evidence_t0.py")}})
        if before["read_skew_ns"] > 1_000_000:
            raise NotDischarged("anchor_read_skew")
        deadline = monotonic_ns() + resync_timeout_s * 1_000_000_000
        print(f"Enabling network time once; polling RAW anchor for at most {resync_timeout_s} s.", flush=True)
        on = execute_command(root, "on", ON_ARGV, min(30, resync_timeout_s), sample, runner)
        if (on["exit_code"] != 0
                or on["started"]["boot_id"] != boot or on["finished"]["boot_id"] != boot):
            raise NotDischarged("on_command_not_admitted")
        if " ".join(on["stdout"].split()).lower().rstrip(".") not in {
                "setusingnetworktime: on", "network time is already on"}:
            raise NotDischarged("network_time_on_not_observed")
        after = before
        movement = 0
        poll = 0
        while monotonic_ns() < deadline:
            after = sample()
            poll += 1
            write_json(root / "polls" / f"{poll:03d}.json", after)
            if after["boot_id"] != boot:
                raise NotDischarged("boot_changed")
            if after["read_skew_ns"] > 1_000_000:
                raise NotDischarged("anchor_read_skew")
            movement = abs(anchor(after) - anchor(before))
            # A slow sample may finish beyond the deadline; never admit it.
            if monotonic_ns() > deadline:
                raise NotDischarged("resync_deadline_exceeded")
            print(f"RAW anchor movement: {movement} ns (must exceed 5000000 ns).", flush=True)
            if movement > 5_000_000:
                break
            sleep(min(5, max(0, (deadline - monotonic_ns()) / 1e9)))
        write_json(root / "after.json", after)
        write_json(root / "anchor-movement.json", {"absolute_movement_ns": movement})
        if movement <= 5_000_000:
            raise NotDischarged("anchor_movement_at_or_below_5ms")
        if abs(anchor(after) - (r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"])) <= 5_000_000:
            raise NotDischarged("changed_author_sequence_not_above_bound")
        argv = [sys.executable, str(REPO_ROOT / "scripts/author_arm_evidence_t0.py"),
                "--pack-root", str(pack), "--custody-root", str(root / "author-custody")]
        started = sample()
        completed = runner(argv, timeout=120)
        finished = sample()
        raw = completed.stdout if isinstance(completed.stdout, bytes) else completed.stdout.encode()
        err = completed.stderr if isinstance(completed.stderr, bytes) else completed.stderr.encode()
        write_bytes(root / "author.stdout.json", raw)
        write_bytes(root / "author.stderr.txt", err)
        namespace = inputs.parent
        present = [name for name in (author._SOURCE_DIRECTORY, author._EVIDENCE_DIRECTORY)
                   if (namespace / name).exists() or (namespace / name).is_symlink()]
        write_json(root / "author-execution.json", {
            "argv": argv, "exit_code": completed.returncode, "started": started,
            "finished": finished, "present_namespaces": present})
        response = readiness.parse_json_bytes(raw, require_canonical=True)
        if present:
            raise NotDischarged("author_pass_namespace_present")
        if (not isinstance(response, dict) or completed.returncode != 2 or response.get("status") != "REFUSE"
                or response.get("reason_codes") != [REFUSAL]
                or response.get("kind") != "CLOCK_ATTESTATION"
                or response.get("detail") != ANCHOR_DETAIL):
            raise NotDischarged("author_exact_anchor_refusal_missing")
        if started["boot_id"] != boot or finished["boot_id"] != boot:
            raise NotDischarged("author_boot_changed")
        positive = {"schema_version": t0_rehearsal.POSITIVE_CONTROL_SCHEMA,
                    "performed_by": "Ed", "outside_t0_sequence": True,
                    "network_time_reenabled": True, "forced_resync": True,
                    "anchor_before_ns": anchor(before), "anchor_after_ns": anchor(after),
                    "author_refusal_reason_code": REFUSAL}
    except (Exception, KeyboardInterrupt) as exc:
        positive = None
        outcome["reason"] = str(exc) if isinstance(exc, NotDischarged) else "control_evidence_invalid"
    finally:
        try:
            path = root / network_time_off.RECEIPT_BASENAME
            # OFF execution must not depend on the anchor sampler: a probe
            # exception (including an interrupt) still reaches the real setter.
            try:
                print("Finishing with network time OFF.", flush=True)
            finally:
                with _uninterrupted_off():
                    off = network_time_off.set_network_time_off(
                        path, root.name, root.name, runner=runner,
                        clock=lambda: {"epoch_s": time.time(), "monotonic_s": monotonic_ns() / 1e9},
                        boot_probe=lambda: network_time_off.boot_id(runner))
            network_time_off.read_receipt(path, plan_id=root.name, window_id=root.name)
            write_json(root / "commands" / "off.json", off)
            write_bytes(root / "commands" / "off" / "stdout.txt", off["stdout"].encode())
            write_bytes(root / "commands" / "off" / "stderr.txt", off["stderr"].encode())
        except (Exception, KeyboardInterrupt):
            positive = None
            outcome["reason"] = "off_receipt_missing_or_invalid"
        if positive is not None:
            write_json(root / "positive-control.json", positive)
            outcome = {"status": "DISCHARGED", "positive_control_path": str(root / "positive-control.json")}
        write_json(root / "outcome.json", outcome)
        # All raw command streams, clock stamps, inputs, and refusal bytes bind.
        hashes = {str(p.relative_to(root)): readiness.sha256_bytes(p.read_bytes())
                  for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}
        write_json(root / "custody-manifest.json", {"files": hashes})
    return outcome


def verify_g10_custody(positive_path, manifest_path, *, code_root, head,
                       before_monotonic_ns, boot_id):
    """Replay the physical control's complete support census, never a locator alone."""
    positive_path, manifest_path = Path(positive_path), Path(manifest_path)
    root = manifest_path.parent
    if (manifest_path.name != "custody-manifest.json" or positive_path != root / "positive-control.json"
            or not root.is_absolute() or any(p.is_symlink() for p in (root, *root.parents))):
        raise NotDischarged("g10_custody_locator")
    manifest = read_json(manifest_path)
    if set(manifest) != {"files"} or not isinstance(manifest["files"], dict):
        raise NotDischarged("g10_manifest_schema")
    observed = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise NotDischarged("g10_custody_symlink")
        if path.is_file() and path != manifest_path:
            observed[path.relative_to(root).as_posix()] = readiness.sha256_bytes(path.read_bytes())
    if manifest["files"] != observed:
        raise NotDischarged("g10_custody_hash_or_census")
    before, after = read_json(root / "before.json"), read_json(root / "after.json")
    positive = read_json(positive_path)
    if (set(positive) != t0_rehearsal._POSITIVE_CONTROL_KEYS
            or positive["schema_version"] != t0_rehearsal.POSITIVE_CONTROL_SCHEMA
            or positive["performed_by"] != "Ed"
            or any(positive[key] is not True for key in
                   ("outside_t0_sequence", "network_time_reenabled", "forced_resync"))
            or positive["anchor_before_ns"] != anchor(before)
            or positive["anchor_after_ns"] != anchor(after)
            or abs(anchor(after) - anchor(before)) <= 5_000_000
            or positive["author_refusal_reason_code"] != REFUSAL
            or read_json(root / "anchor-movement.json") !=
               {"absolute_movement_ns": abs(anchor(after) - anchor(before))}):
        raise NotDischarged("g10_anchor_or_record")
    on, execution = read_json(root / "commands/on.json"), read_json(root / "author-execution.json")
    response = read_json(root / "author.stdout.json")
    lineage = read_json(root / "author-input-lineage.json")
    r0_capture = read_json(root / "author-custody" / Path(lineage["pack_root"]).name /
                           author._INPUT_DIRECTORY / "clock-reference.json")
    r0 = readiness.parse_json_bytes(r0_capture["stdout"].encode())
    r0_anchor = r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"]
    if (lineage["r0_anchor_ns"] != r0_anchor or r0["boot_session_id"].lower() != boot_id
            or abs(r0_anchor - anchor(before)) > 5_000_000
            or abs(r0_anchor - anchor(after)) <= 5_000_000):
        raise NotDischarged("g10_r0_binding")
    if (on["argv"] != list(ON_ARGV) or on["exit_code"] != 0
            or " ".join(on["stdout"].split()).lower().rstrip(".") not in
               {"setusingnetworktime: on", "network time is already on"}
            or execution["exit_code"] != 2 or execution["present_namespaces"] != []
            or response.get("status") != "REFUSE" or response.get("kind") != "CLOCK_ATTESTATION"
            or response.get("reason_codes") != [REFUSAL] or response.get("detail") != ANCHOR_DETAIL
            or Path(execution["argv"][1]) != Path(code_root) / "scripts/author_arm_evidence_t0.py"
            or execution["argv"][2:] != ["--pack-root", lineage["pack_root"],
                "--custody-root", str(root / "author-custody")]):
        raise NotDischarged("g10_on_or_author_refusal")
    for label, command in (("on", on),):
        directory = root / "commands" / label
        if (read_json(directory / "started.json") != command["started"]
                or read_json(directory / "finished.json") != command["finished"]
                or (directory / "stdout.txt").read_bytes() != command["stdout"].encode()
                or (directory / "stderr.txt").read_bytes() != command["stderr"].encode()):
            raise NotDischarged("g10_command_support")
    off = network_time_off.read_receipt(root / network_time_off.RECEIPT_BASENAME,
                                       plan_id=root.name, window_id=root.name)
    stamps = [before, on["started"], on["finished"], after, execution["started"], execution["finished"]]
    times = [value["monotonic_ns"] for value in stamps]
    if (any(value["boot_id"] != boot_id or value["read_skew_ns"] > 1_000_000 for value in stamps)
            or times != sorted(times) or off["boot_id"] != boot_id
            or not times[-1] <= round(off["monotonic_s"] * 1e9) < before_monotonic_ns
            or lineage["boot_id"] != boot_id):
        raise NotDischarged("g10_boot_or_order")
    expected_codes = {"scripts/author_arm_evidence_t0.py", "joulewise/arm_readiness_evidence_t0.py"}
    if set(lineage["author_code_sha256"]) != expected_codes:
        raise NotDischarged("g10_code_inventory")
    for relative, digest in lineage["author_code_sha256"].items():
        raw = subprocess.check_output(["git", "-C", str(code_root), "show", f"{head}:{relative}"])
        if readiness.sha256_bytes(raw) != digest:
            raise NotDischarged("g10_code_pin")
    if read_json(root / "commands/off.json") != off:
        raise NotDischarged("g10_off_support")
    if ((root / "commands/off/stdout.txt").read_bytes() != off["stdout"].encode()
            or (root / "commands/off/stderr.txt").read_bytes() != off["stderr"].encode()):
        raise NotDischarged("g10_off_streams")
    outcome = read_json(root / "outcome.json")
    if outcome != {"status": "DISCHARGED", "positive_control_path": str(positive_path)}:
        raise NotDischarged("g10_outcome")
    return positive


_run_control = run_control


def run_control(**kwargs):
    """Translate termination signals into an unwind that still enforces OFF."""
    previous = {}
    def interrupted(signum, frame):
        for number in previous:
            signal.signal(number, signal.SIG_IGN)
        raise KeyboardInterrupt
    if threading.current_thread() is threading.main_thread():
        for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            previous[number] = signal.signal(number, interrupted)
    try:
        return _run_control(**kwargs)
    finally:
        for number, handler in previous.items():
            signal.signal(number, handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    stamps = sub.add_parser("stamp")
    stamps.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--pack-root", type=Path, required=True)
    run.add_argument("--author-inputs", type=Path, required=True)
    run.add_argument("--custody-root", type=Path, required=True)
    run.add_argument("--resync-timeout-s", type=int, default=120, choices=range(1, 301),
                     metavar="1..300", help="ON plus polling deadline in seconds (default: 120)")
    args = parser.parse_args(argv)
    if args.operation == "stamp":
        write_json(args.output, stamp())
        return 0
    try:
        print("Ed: confirm no agent seat, armed window or capture is running; type OUTSIDE: ",
              end="", file=sys.stderr, flush=True)
        confirmed = input().strip()
    except EOFError:
        print(readiness.render_json({"status": "NOT-DISCHARGED", "reason": "outside_confirmation_missing"}).decode(), end="")
        return 2
    if confirmed != "OUTSIDE":
        return 2
    try:
        result = run_control(pack_root=args.pack_root, author_inputs=args.author_inputs,
                             custody_root=args.custody_root,
                             resync_timeout_s=args.resync_timeout_s)
    except (OSError, ValueError):
        result = {"status": "NOT-DISCHARGED", "reason": "control_setup_refused"}
    print(readiness.render_json(result).decode(), end="")
    return 0 if result["status"] == "DISCHARGED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
