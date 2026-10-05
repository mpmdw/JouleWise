#!/usr/bin/env python3
"""Ed-owned, pre-window physical RAW-anchor control; never execute sudo here.

The lead supplies a reviewed resync vector/deadline and real, un-authored T-0
inputs. Ed executes the printed commands in a second terminal. Synthetic
inputs are useful only in tests, never physical qualification evidence.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import os
from pathlib import Path
import shlex
import subprocess
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


def run_unprivileged(argv, *, timeout):
    # This runner has a single executable purpose: the real author CLI.
    return subprocess.run(argv, capture_output=True, timeout=timeout, check=False,
                          cwd=REPO_ROOT, stdin=subprocess.DEVNULL)


def owner_command(root, label, argv, timeout):
    """Ed's shell executes the privileged vector, capturing separate raw streams.

    Stamp subprocesses merely read clocks and boot identity. The helper never
    spawns the displayed privileged command, including the OFF command.
    """
    directory = root / "commands" / label
    directory.mkdir(parents=True)
    base = [sys.executable, str(Path(__file__).resolve()), "stamp", "--output"]
    print(f"In your second terminal, run this once (deadline {timeout} seconds; "
          "interrupt there if it hangs):", flush=True)
    print("\n".join([
        "umask 077",
        shlex.join([*base, str(directory / "started.json")]) + " && {",
        shlex.join(argv) + " > " + shlex.quote(str(directory / "stdout.txt"))
        + " 2> " + shlex.quote(str(directory / "stderr.txt")),
        "g10_command_rc=$?",
        "printf '%s\\n' \"$g10_command_rc\" > " + shlex.quote(str(directory / "exit_code.txt")),
        shlex.join([*base, str(directory / "finished.json")]),
        "}",
    ]), flush=True)
    if input("Type DONE here after that command finishes: ").strip() != "DONE":
        raise NotDischarged("owner_command_unconfirmed")
    started, finished = read_json(directory / "started.json"), read_json(directory / "finished.json")
    return {"argv": list(argv), "exit_code": int((directory / "exit_code.txt").read_text()),
            "stdout": (directory / "stdout.txt").read_text(),
            "stderr": (directory / "stderr.txt").read_text(),
            "started": started, "finished": finished}


def checked_command(root, label, argv, timeout, boot, owner):
    result = owner(root, label, argv, timeout)
    write_json(root / "commands" / f"{label}.json", result)
    start, end = result["started"], result["finished"]
    if (result["argv"] != list(argv) or type(result["exit_code"]) is not int
            or result["exit_code"] != 0
            or not isinstance(result["stdout"], str) or not isinstance(result["stderr"], str)
            or start["boot_id"] != boot or end["boot_id"] != boot
            or not 0 <= end["monotonic_ns"] - start["monotonic_ns"] <= timeout * 1e9):
        raise NotDischarged(f"{label}_command_not_admitted")
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


def run_control(*, pack_root, author_inputs, custody_root, resync_argv,
                resync_timeout_s, sample=stamp, runner=run_unprivileged,
                owner=owner_command):
    """Execute once, retaining failed evidence and always requesting OFF cleanup.

    Only the author runner executes a process; the owner callback mediates all
    privileged acts. There is deliberately no automatic retry or ON restore.
    """
    # The missing reviewed vector is a required lead input, not a default.
    if (list(resync_argv) not in (["/usr/bin/sudo", "/usr/bin/sntp", "-sS", "time.apple.com"],
                                 ["/usr/bin/sudo", "-n", "/usr/bin/sntp", "-sS", "time.apple.com"])
            or type(resync_timeout_s) is not int or not 1 <= resync_timeout_s <= 300):
        raise NotDischarged("reviewed_resync_recipe_required")
    root = Path(custody_root).absolute()
    source = Path(author_inputs).resolve(strict=True)
    if root.resolve().is_relative_to(source) or source.is_relative_to(root.resolve()):
        raise NotDischarged("control_custody_not_isolated")
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    pack = Path(pack_root).resolve(strict=True)
    inputs = root / "author-custody" / pack.name / author._INPUT_DIRECTORY
    outcome = {"status": "NOT-DISCHARGED", "reason": "control_incomplete"}
    on_attempted = False
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
        if abs(r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"] - anchor(before)) > 5_000_000:
            raise NotDischarged("author_sequence_already_above_anchor_bound")
        write_json(root / "author-input-lineage.json", {
            "input_source": str(Path(author_inputs).resolve()),
            "pack_root": str(pack), "r0_anchor_ns": r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"],
            "boot_id": boot,
            "author_code_sha256": {p: readiness.sha256_bytes((REPO_ROOT / p).read_bytes())
                for p in ("scripts/author_arm_evidence_t0.py", "joulewise/arm_readiness_evidence_t0.py")}})
        on_attempted = True
        on = checked_command(root, "on", ON_ARGV, 30, boot, owner)
        if " ".join(on["stdout"].split()).lower().rstrip(".") not in {
                "setusingnetworktime: on", "network time is already on"}:
            raise NotDischarged("network_time_on_not_observed")
        checked_command(root, "resync", resync_argv, resync_timeout_s, boot, owner)
        after = sample()
        write_json(root / "after.json", after)
        if after["boot_id"] != boot:
            raise NotDischarged("boot_changed")
        if max(before["read_skew_ns"], after["read_skew_ns"]) > 1_000_000:
            raise NotDischarged("anchor_read_skew")
        movement = abs(anchor(after) - anchor(before))
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
    except (OSError, ValueError, KeyError, TypeError, EOFError, KeyboardInterrupt, subprocess.SubprocessError) as exc:
        outcome["reason"] = str(exc) if isinstance(exc, NotDischarged) else "control_evidence_invalid"
    finally:
        if on_attempted:
            try:
                off = checked_command(root, "off", network_time_off.OFF_ARGV, 30, boot, owner)
                # Reuse the established receipt producer with Ed's retained result;
                # its injected runner returns bytes and never executes sudo.
                path = root / network_time_off.RECEIPT_BASENAME
                network_time_off.set_network_time_off(
                    path, root.name, root.name,
                    runner=lambda argv, timeout: subprocess.CompletedProcess(argv, off["exit_code"], off["stdout"], off["stderr"]),
                    clock=lambda: {"epoch_s": off["finished"]["realtime_ns"] / 1e9,
                                   "monotonic_s": off["finished"]["monotonic_ns"] / 1e9},
                    boot_probe=lambda: boot)
                network_time_off.read_receipt(path, plan_id=root.name, window_id=root.name)
            except (OSError, ValueError, KeyError, TypeError, EOFError, KeyboardInterrupt, subprocess.SubprocessError):
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    stamps = sub.add_parser("stamp")
    stamps.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--pack-root", type=Path, required=True)
    run.add_argument("--author-inputs", type=Path, required=True)
    run.add_argument("--custody-root", type=Path, required=True)
    run.add_argument("--reviewed-resync-argv", required=True, help="JSON argv from the lead's reviewed recipe; no default")
    run.add_argument("--resync-timeout-s", type=int, required=True)
    args = parser.parse_args(argv)
    if args.operation == "stamp":
        write_json(args.output, stamp())
        return 0
    if input("Ed: confirm no agent seat, armed window or capture is running; type OUTSIDE: ").strip() != "OUTSIDE":
        return 2
    try:
        result = run_control(pack_root=args.pack_root, author_inputs=args.author_inputs,
                             custody_root=args.custody_root,
                             resync_argv=readiness.parse_json_bytes(args.reviewed_resync_argv.encode()),
                             resync_timeout_s=args.resync_timeout_s)
    except (OSError, ValueError):
        result = {"status": "NOT-DISCHARGED", "reason": "control_setup_refused"}
    print(readiness.render_json(result).decode(), end="")
    return 0 if result["status"] == "DISCHARGED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
