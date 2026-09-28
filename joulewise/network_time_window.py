"""Write-once H5/H6 receipts and fail-closed per-capture network-time verdicts.

No project imports: consumers can use this module without importing a driver.
The command runner, clock and boot probe are replaceable at the OS boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


OFF_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off")
ON_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "on")
BOOT_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")
LOG_PREFIX = ("/usr/bin/log", "show", "--info", "--debug", "--style", "syslog",
              "--predicate", 'process == "timed"')
HEADER = "Timestamp                       (process)[PID]"
MARKERS = ("cmd,apply,src,", "ntp_adjtime", "settimeofday")
NETWORK_TIME_ENFORCED_KINDS = frozenset()
RESTORE_PENDING_PATH = (Path.home() / "Library/Application Support/JouleWise"
                        / "network-time-restore-pending.json")
OLD_BUILDS = frozenset({"25F84"})
OLD_SESSIONS = frozenset({
    "d079-epoch-25g83-derivation-w1-20260927",
    "d079-epoch-25g83-derivation-w2-20260927",
})
# Populated with sealed historic idle plan IDs when that consumer lands.
OLD_IDLE_PLANS = frozenset()
_STAMP = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+)([+-]\d\d:?\d\d)\b")
_TIMESTAMP_LIKE = re.compile(r"^\d{4}-\d\d-\d\d(?:[ T]|$)")
_DATA_CATEGORY = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+[+-]\d\d:?\d\d\s+(?:\S+\s+)?timed\[\d+\]:?\s+\[com\.apple\.timed:data\](?:\s|$)")


def _run(argv, timeout=30):
    return subprocess.run(argv, capture_output=True, timeout=timeout, check=False)


def _bytes(value):
    return value if isinstance(value, bytes) else str(value).encode("utf-8")


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _write_once(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _boot(runner):
    try:
        result = runner(BOOT_ARGV, timeout=10)
        if result.returncode == 0:
            return _bytes(result.stdout).decode("utf-8", "strict").strip() or None
    except (OSError, ValueError, subprocess.TimeoutExpired, UnicodeError):
        pass
    return None


def _clock():
    # The same Python clocks used by the capture writer; stamp after the call.
    return {"epoch_s": time.time(), "monotonic_s": time.monotonic()}


def _command_receipt(argv, plan_id, *, runner=_run, boot_probe=None, clock=_clock):
    error = None
    try:
        result = runner(argv, timeout=30)
        exit_code = result.returncode
        stdout = _bytes(result.stdout).decode("utf-8", "surrogateescape")
        stderr = _bytes(result.stderr).decode("utf-8", "surrogateescape")
    except (OSError, subprocess.TimeoutExpired) as exc:
        exit_code, stdout, stderr = None, "", ""
        error = f"{type(exc).__name__}: {exc}"
    stamp = clock()
    return {"argv": list(argv), "exit_code": exit_code, "stdout": stdout,
            "stderr": stderr, "error": error, **stamp,
            "boot_id": boot_probe() if boot_probe is not None else _boot(runner),
            "plan_id": plan_id}


def create_restore_marker(custody_root, plan_id, *, measurement_root=None,
                          chain_path=None, marker_path=RESTORE_PENDING_PATH):
    marker = {"custody_root": str(Path(custody_root).resolve()), "plan_id": plan_id}
    if measurement_root is not None and chain_path is not None:
        for name, path in (("measurement_root", measurement_root),
                           ("custody_root", custody_root), ("chain_path", chain_path)):
            if name == "custody_root":
                marker[name + "_written"] = str(path)
            else:
                marker[name] = str(path)
            marker[name + "_resolved"] = str(Path(path).resolve())
    _write_once(marker_path, _json_bytes(marker))


def set_network_time_off(custody_root, plan_id, *, runner=_run, boot_probe=None,
                         clock=_clock, marker_path=RESTORE_PENDING_PATH,
                         measurement_root=None, chain_path=None):
    """Create the recovery marker before touching the setting; save even failure."""
    create_restore_marker(custody_root, plan_id, measurement_root=measurement_root,
                          chain_path=chain_path, marker_path=marker_path)
    receipt = _command_receipt(OFF_ARGV, plan_id, runner=runner,
                               boot_probe=boot_probe, clock=clock)
    _write_once(Path(custody_root) / "night/network_time/h5-off.json", _json_bytes(receipt))
    return receipt


def set_network_time_on(custody_root, plan_id, *, runner=_run, boot_probe=None,
                        clock=_clock, marker_path=RESTORE_PENDING_PATH):
    """Attempt ON; preserve every receipt and retry after a failed restore."""
    window_dir = Path(custody_root) / "night/network_time"
    target = window_dir / "h5-on.json"
    if target.exists():
        index = 1
        while (window_dir / f"h5-on-recovery-{index}.json").exists():
            index += 1
        target = window_dir / f"h5-on-recovery-{index}.json"
    receipt = _command_receipt(ON_ARGV, plan_id, runner=runner,
                               boot_probe=boot_probe, clock=clock)
    _write_once(target, _json_bytes(receipt))
    if receipt["exit_code"] == 0:
        Path(marker_path).unlink(missing_ok=True)
    return receipt


def _format_epoch(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")


def query_argv(off_epoch, now_epoch):
    start = math.floor(off_epoch - 3600)
    end = math.ceil(now_epoch)
    return (*LOG_PREFIX, "--start", _format_epoch(start), "--end", _format_epoch(end))


def _query_records(window_dir):
    return sorted(Path(window_dir).glob("h6-window-*.json"),
                  key=lambda p: int(p.stem.rsplit("-", 1)[1]) if p.stem.rsplit("-", 1)[1].isdigit() else -1)


def run_window_query(night_dir, *, who="driver", runner=_run, boot_probe=None,
                     clock=_clock):
    """Query only after the caller proves its capturing children ended."""
    if who not in {"driver", "chain", "recovery"}:
        raise ValueError("unknown query actor")
    window_dir = Path(night_dir) / "network_time"
    off_raw = (window_dir / "h5-off.json").read_bytes()
    off = json.loads(off_raw)
    # Raw output is published before its record. A crash in between leaves an
    # orphaned raw file, which must remain immutable and cannot own the retry.
    index = 1
    while ((window_dir / f"h6-query-{index}.txt").exists()
           or (window_dir / f"h6-window-{index}.json").exists()):
        index += 1
    begun = clock()
    argv = query_argv(float(off["epoch_s"]), begun["epoch_s"])
    raw = None
    error = None
    try:
        result = runner(argv, timeout=120)
        exit_code = result.returncode
        raw = _bytes(result.stdout)
        stderr = _bytes(result.stderr).decode("utf-8", "surrogateescape")
    except (OSError, subprocess.TimeoutExpired) as exc:
        exit_code, stderr = None, ""
        error = f"{type(exc).__name__}: {exc}"
    ended = clock()
    if raw is not None:
        _write_once(window_dir / f"h6-query-{index}.txt", raw)
    record = {"argv": list(argv), "exit_code": exit_code, "stderr": stderr,
              "error": error, "raw_sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None,
              "start_epoch_s": float(datetime.strptime(argv[-3], "%Y-%m-%d %H:%M:%S%z").timestamp()),
              "end_epoch_s": float(datetime.strptime(argv[-1], "%Y-%m-%d %H:%M:%S%z").timestamp()),
              "start_arg": argv[-3], "end_arg": argv[-1],
              "started": begun, "ended": ended,
              "boot_id": boot_probe() if boot_probe is not None else _boot(runner),
              "off_sha256": hashlib.sha256(off_raw).hexdigest(), "who": who}
    _write_once(window_dir / f"h6-window-{index}.json", _json_bytes(record))
    return record


def _placed_lines(raw):
    """Return placed syslog lines and whether every line has a valid parent."""
    try:
        lines = raw.decode("utf-8", "strict").splitlines()
    except UnicodeError:
        return [], False, False
    header = bool(lines) and lines[0].rstrip() == HEADER
    placed, valid, parent = [], header, None
    for line in lines[1:] if header else lines:
        match = _STAMP.match(line)
        if match:
            try:
                parent = datetime.strptime(match.group(1) + match.group(2).replace(":", ""),
                                           "%Y-%m-%d %H:%M:%S.%f%z").timestamp()
            except ValueError:
                parent, valid = None, False
        elif parent is not None and not _TIMESTAMP_LIKE.match(line):
            pass
        else:
            parent, valid = None, False
        if parent is not None:
            placed.append((parent, line))
    return placed, header, valid


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("invalid clock reading")
    return float(value)


def _stamp(value):
    if isinstance(value, dict):
        return (_number(value["epoch_s"]),
                _number(value.get("monotonic_before_s", value.get("monotonic_s"))))
    return (_number(value.epoch_s),
            _number(getattr(value, "monotonic_before_s", getattr(value, "monotonic_s", None))))


def _interval(first, last):
    fw, fm = _stamp(first)
    lw, lm = _stamp(last)
    span = lm - fm
    if span < 0:
        raise ValueError("reversed monotonic capture")
    return fw, fm, lw, lm, min(fw, lw - span) - 180, max(lw, fw + span) + 1


def _read_off(window_dir):
    raw = (window_dir / "h5-off.json").read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _is_data_line(line):
    # The category must be the syslog category field, not quoted text in a
    # payload or on a continuation line.
    return bool(_DATA_CATEGORY.match(line))


def _has_valid_run(window_dir):
    try:
        off, off_digest = _read_off(window_dir)
        for path in _query_records(window_dir):
            try:
                record = json.loads(path.read_bytes())
                raw_path = window_dir / path.name.replace("h6-window-", "h6-query-").replace(".json", ".txt")
                raw = raw_path.read_bytes()
                lines, header, parsed = _placed_lines(raw)
                argv = tuple(record["argv"])
                start = datetime.strptime(record["start_arg"], "%Y-%m-%d %H:%M:%S%z").timestamp()
                end = datetime.strptime(record["end_arg"], "%Y-%m-%d %H:%M:%S%z").timestamp()
                if (isinstance(off, dict) and isinstance(record, dict)
                        and hashlib.sha256(raw).hexdigest() == record["raw_sha256"]
                        and record["off_sha256"] == off_digest and record["exit_code"] == 0
                        and header and parsed and argv == (*LOG_PREFIX, "--start", record["start_arg"],
                                                            "--end", record["end_arg"])
                        and start == record["start_epoch_s"] and end == record["end_epoch_s"]
                        and start <= off["epoch_s"] - 3600
                        and end >= record["started"]["epoch_s"]
                        and record["boot_id"] == off["boot_id"] and off["boot_id"]
                        and any(_is_data_line(line) and epoch < off["epoch_s"]
                                for epoch, line in lines)):
                    return True
            except (OSError, ValueError, TypeError, KeyError, OverflowError):
                continue
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return False


def capture_verdict(window_dir, first, last):
    """Compute one verdict from authenticated saved bytes; never trust a cached verdict."""
    window_dir = Path(window_dir)
    try:
        fw, fm, lw, lm, lower, upper = _interval(first, last)
    except (KeyError, TypeError, ValueError, AttributeError):
        return "network_time_unattested", "invalid_capture_clock"
    try:
        off_raw = (window_dir / "h5-off.json").read_bytes()
        off_digest = hashlib.sha256(off_raw).hexdigest()
        try:
            off = json.loads(off_raw)
        except (ValueError, UnicodeError):
            off = None
    except OSError:
        return "network_time_unattested", "off_not_proved"
    valid_cover = False
    for path in _query_records(window_dir):
        try:
            record = json.loads(path.read_bytes())
            raw = (window_dir / path.name.replace("h6-window-", "h6-query-").replace(".json", ".txt")).read_bytes()
            if (not isinstance(record, dict)
                    or hashlib.sha256(raw).hexdigest() != record["raw_sha256"]
                    or record["off_sha256"] != off_digest):
                continue
            placed, header, parsed = _placed_lines(raw)
            for epoch, line in placed:
                if lower <= epoch <= upper and any(marker in line for marker in MARKERS):
                    return "network_time_slew_attested", {"query": path.name, "epoch_s": epoch}
            argv = tuple(record["argv"])
            if (record["exit_code"] != 0 or not header or not parsed
                    or argv[:len(LOG_PREFIX)] != LOG_PREFIX
                    or argv[len(LOG_PREFIX):] != ("--start", record["start_arg"], "--end", record["end_arg"])):
                continue
            start = datetime.strptime(record["start_arg"], "%Y-%m-%d %H:%M:%S%z").timestamp()
            end = datetime.strptime(record["end_arg"], "%Y-%m-%d %H:%M:%S%z").timestamp()
            if (not isinstance(off, dict)
                    or start != record["start_epoch_s"] or end != record["end_epoch_s"]
                    or start > float(off["epoch_s"]) - 3600
                    or end < float(record["started"]["epoch_s"])
                    or record["boot_id"] != off["boot_id"] or not off["boot_id"]
                    or not any(_is_data_line(line) and epoch < off["epoch_s"]
                               for epoch, line in placed)):
                continue
            if (record["started"]["epoch_s"] >= lw + 1
                    and record["started"]["monotonic_s"] >= lm + 1):
                valid_cover = True
        except (OSError, ValueError, TypeError, KeyError, OverflowError):
            continue
    if (not isinstance(off, dict) or off.get("argv") != list(OFF_ARGV) or off.get("exit_code") != 0
            or off.get("stdout") != "setUsingNetworkTime: Off\n"):
        return "network_time_unattested", "off_not_proved"
    try:
        if fw - _number(off["epoch_s"]) < 600 or fm - _number(off["monotonic_s"]) < 600:
            return "network_time_unattested", "off_lead_short"
    except (KeyError, TypeError, ValueError):
        return "network_time_unattested", "off_not_proved"
    return ("clean", "valid_query") if valid_cover else ("network_time_unattested", "no_valid_query")


def attestation_required(os_build, session_id):
    if not isinstance(os_build, str) or not isinstance(session_id, str):
        return True
    return os_build not in OLD_BUILDS and session_id not in OLD_SESSIONS | OLD_IDLE_PLANS


def recover_network_time(*, marker_path=RESTORE_PENDING_PATH, runner=_run,
                         boot_probe=None, clock=_clock, process_group_absent=None,
                         capture_proof=None):
    """Finish an interrupted night only after the chain is proved gone."""
    try:
        marker_path = Path(marker_path)
        if not marker_path.exists():
            return "nothing_pending"
        marker = json.loads(marker_path.read_bytes())
        if not isinstance(marker, dict) or not isinstance(marker.get("custody_root"), str) or not isinstance(marker.get("plan_id"), str):
            return "marker_invalid"
    except (OSError, ValueError, TypeError, UnicodeError):
        return "marker_invalid"
    try:
        root = Path(marker["custody_root"])
        night_dir = root / "night"
        started_path = night_dir / "chain.started"
        exited_path = night_dir / "chain.exited"
        if started_path.exists():
            try:
                started = json.loads(started_path.read_bytes())
            except (OSError, ValueError, TypeError, UnicodeError):
                return "chain_unproved"
            pgid = started.get("pgid") if isinstance(started, dict) else None
            if isinstance(pgid, bool) or not isinstance(pgid, int) or pgid <= 0:
                # The one safe exception is a documented failed Popen: no
                # process was created, and the exit record says so.
                try:
                    exited = json.loads(exited_path.read_bytes()) if exited_path.exists() else None
                except (OSError, ValueError, TypeError, UnicodeError):
                    exited = None
                never_launched = (isinstance(started, dict)
                    and started.get("pid") is None and started.get("pgid") is None
                    and (started.get("popen_attempted") is False
                         or isinstance(started.get("launch_error"), str) and bool(started["launch_error"]))
                    and isinstance(exited, dict) and exited.get("launch_failed") is True)
                if not never_launched:
                    return "chain_unproved"
            else:
                if capture_proof is None:
                    return "chain_unproved"
                try:
                    proved, _evidence = capture_proof(marker, pgid)
                except Exception:
                    return "chain_unproved"
                if not proved:
                    return "chain_unproved"
        else:
            # The driver claims chain.started before OFF. A missing claim
            # cannot prove launch never happened.
            return "chain_unproved"
        window_dir = night_dir / "network_time"
        if (window_dir / "h5-off.json").exists() and not _has_valid_run(window_dir):
            try:
                run_window_query(night_dir, who="recovery", runner=runner,
                                 boot_probe=boot_probe, clock=clock)
            except (OSError, ValueError, TypeError, KeyError, OverflowError, UnicodeError):
                pass
        if isinstance(pgid, int) and pgid > 0:
            try:
                proved, _evidence = capture_proof(marker, pgid)
            except Exception:
                return "chain_unproved"
            if not proved:
                return "chain_unproved"
        on_records = [window_dir / "h5-on.json", *sorted(window_dir.glob("h5-on-recovery-*.json"))]
        def restored(path):
            try:
                value = json.loads(path.read_bytes())
                return isinstance(value, dict) and value.get("exit_code") == 0
            except (OSError, ValueError, TypeError):
                return False
        if any(restored(path) for path in on_records):
            marker_path.unlink(missing_ok=True)
            return "restored"
        receipt = set_network_time_on(root, marker["plan_id"], runner=runner,
                                      boot_probe=boot_probe, clock=clock, marker_path=marker_path)
        if receipt["exit_code"] != 0:
            # The retry receipt is saved. The next night proves its own OFF
            # state; a failed ON is diagnostic, not a new admission veto.
            marker_path.unlink(missing_ok=True)
            return "restore_failed"
        return "restored"
    except Exception:
        return "chain_unproved"


def _evidence_stamps(path):
    evidence = json.loads(Path(path).read_bytes())
    for location in (evidence.get("clock_stamps"),
                     evidence.get("clock_anchor", {}).get("clock_stamps"),
                     evidence.get("power", {}).get("anchor", {}).get("clock_stamps"),
                     evidence.get("stamps")):
        if isinstance(location, dict):
            return location
    raise ValueError("capture has no paired readings")


def _estimator_offset_span(stamps):
    """Mirror uncertainty_evidence._offset_envelope_s's unpadded span."""
    order = ("pre_spawn", "first_parse", "sampling_started",
             "sampling_stopped", "post_parse")
    readings = [stamps[name] for name in order]
    raw_lowers = [_number(s["epoch_s"]) - _number(s["monotonic_after_s"])
                  for s in readings]
    raw_uppers = [_number(s["epoch_s"]) - _number(s["monotonic_before_s"])
                  for s in readings]
    return max(raw_uppers) - min(raw_lowers)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("report",))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--h6", action="store_true")
    mode.add_argument("--h7", action="store_true")
    parser.add_argument("--window-dir", type=Path, required=True)
    parser.add_argument("--capture", type=Path, action="append", required=True)
    args = parser.parse_args(argv)
    rows = []
    for path in args.capture:
        stamps = _evidence_stamps(path)
        first = stamps.get("pre_spawn", stamps.get("sampling_started"))
        last = stamps.get("post_parse", stamps.get("sampling_stopped"))
        verdict, detail = capture_verdict(args.window_dir, first, last)
        row = {"capture": str(path), "verdict": verdict, "detail": detail}
        if args.h6:
            row["flagged"] = verdict == "network_time_slew_attested"
        if args.h7:
            evidence = json.loads(path.read_bytes())
            span = _estimator_offset_span(stamps)
            baseline = _number(evidence["clock_anchor"]["rate_fit_baseline_s"])
            if baseline <= 0:
                raise ValueError("invalid rate-fit baseline")
            try:
                off, off_digest = _read_off(args.window_dir)
                state = ("off" if isinstance(off, dict) and off.get("argv") == list(OFF_ARGV)
                         and off.get("exit_code") == 0
                         and off.get("stdout") == "setUsingNetworkTime: Off\n"
                         else "unknown")
            except (OSError, ValueError, TypeError):
                state, off_digest = "unknown", None
            row.update(state=state, h5_off_sha256=off_digest,
                       standing_rate_ppm=span / baseline * 1e6,
                       drift_term_s=span)
        rows.append(row)
    rows.sort(key=lambda row: (row["verdict"] != "network_time_slew_attested", row["capture"]))
    for row in rows:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
