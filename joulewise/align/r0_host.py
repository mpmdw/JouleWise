"""Read-only R0 host probes. No model imports or downloads."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from types import SimpleNamespace

from joulewise.measurement_liveness import census, custody_parent, ADDITIONAL_PARENTS_ENV
from joulewise.night_gate import ProbeResult, agent_census
from joulewise.prewindow import PS_ARGV, busy_contaminants
from joulewise import prewindow
from joulewise.hazards import contention
from joulewise.hazards.base import Stamp
from joulewise.align.r0_step import (ProfileRefused, profile_config as fixed_profile,
                                     rank_response, step_budget as fixed_budget)
from joulewise.align.apple.smc_enumeration import rank as classify_smc


def profile_config(value=None):
    """D3 adaptive profile; keep the retired fixed-profile fit diagnostic intact."""
    if value is not None and not isinstance(value, dict):
        return fixed_profile(value)  # existing typed refusal
    supplied = dict(value or {})
    # D3: measured post-step settle median ~930 s, maximum 1,038 s => 1,200 s cap.
    maximum = supplied.pop("idle_max_seconds", 1200)
    profile = fixed_profile(supplied)
    if type(maximum) is not int or maximum < profile["idle_seconds"]:
        raise ProfileRefused("smc_step.invalid_duration", "idle_max_seconds must be an integer >= idle_seconds")
    return {**profile, "idle_max_seconds": maximum}


def step_budget(value=None):
    profile = profile_config(value)
    # Budget the maximum capture; fixed_budget retains the existing +600 s
    # execution margin. Erratum 2: measured journal 95,467,641 bytes /1,800
    # one-Hz slots =53,037.58 bytes/slot; ceil to a whole byte for planning.
    maximum = {k: v for k, v in profile.items() if k != "idle_max_seconds"}
    maximum["idle_seconds"] = profile["idle_max_seconds"]
    budget = fixed_budget(maximum)
    per_slot = math.ceil(95_467_641 / 1800)
    return {**budget, "profile": profile, "journal_bytes_per_slot_estimate": per_slot,
            "journal_bytes_estimate": budget["capture_seconds"] * per_slot,
            "journal_estimate_note": "Measured 95,467,641 bytes /1,800 slots, rounded up; verify after enumeration."}


class Refused(RuntimeError):
    """A failed or indeterminate safety census; never continue this run."""


def command(argv):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                            env={**os.environ, "LC_ALL": "C"})
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exit {result.returncode}: {result.stderr.strip()}")
    return result.stdout


class QuietGuard:
    """Reuse the agent identity and custody census, with no ancestor exemption.

    Additional argv matching covers hand-run measurement chains. Custody parents
    include shared defaults and configured extras; missing roots fail closed.
    A refusal is latched even if an endpoint catches the raised exception.
    Contaminant CPU uses cumulative TIME over at least prewindow.INTERVAL_S;
    the first clean admission waits for that baseline before returning.
    """

    def __init__(self, parents, *, run=subprocess.run, inspect_custody=census,
                 clock=time.monotonic, sleep=time.sleep):
        self.parents = [Path(p) for p in parents]
        self.run, self.inspect_custody, self.clock = run, inspect_custody, clock
        self.sleep = sleep
        self.last = float("-inf")
        self._clock_last = float("-inf")
        self._snapshots = []
        self._previous_over = {}
        self.failure = None
        self.receipts = []

    def _now(self):
        now = self.clock()
        if not math.isfinite(now) or now < self._clock_last:
            raise Refused("census indeterminate: monotonic clock went backwards or is invalid")
        self._clock_last = now
        return now

    def _cpu_snapshot(self, receipt):
        started = self._now()
        wall = time.time_ns()
        try:
            result = self.run(contention.PS_ARGV, capture_output=True, text=True,
                              timeout=contention.PROBE_TIMEOUT_S,
                              env={**os.environ, "LC_ALL": "C"})
            table = self.run(PS_ARGV, capture_output=True, text=True,
                             timeout=contention.PROBE_TIMEOUT_S,
                             env={**os.environ, "LC_ALL": "C"})
        except Exception as exc:
            raise Refused(f"census indeterminate: cumulative CPU snapshot: {exc}") from exc
        finished = self._now()
        if result.returncode:
            raise Refused(f"census indeterminate: cumulative CPU snapshot exit {result.returncode}")
        if table.returncode:
            raise Refused("census indeterminate: process args table unavailable")
        busy_contaminants(table.stdout)  # validate the args table at each snapshot
        try:
            rows = contention.parse(result.stdout.encode("utf-8"))
        except (ValueError, OverflowError) as exc:
            raise Refused(f"census indeterminate: cumulative CPU snapshot: {exc}") from exc
        args = {int(line.split(None, 2)[0]): line.split(None, 2)[2]
                for line in table.stdout.splitlines() if line.strip()}
        for row in rows.values():
            row["contaminant_matches"] = [
                source for source, value in (("ucomm", row["command"]),
                                              ("args", args.get(row["pid"], "")))
                if re.search(prewindow.CONTAMINANTS, value, re.I)]
            row["contaminant"] = bool(row["contaminant_matches"])
        snapshot = contention.Snapshot(
            Stamp(wall, int(started * 1e9), int(started * 1e9)),
            Stamp(time.time_ns(), int(finished * 1e9), int(finished * 1e9)), rows, None)
        if snapshot.finished.wall_ns < wall:
            receipt["wall_clock_backwards"] = True
        if self._snapshots:
            previous = self._snapshots[-1]
            if snapshot.started.wall_ns < previous.finished.wall_ns:
                receipt["wall_clock_backwards"] = True
            for identity in previous.rows.keys() & rows.keys():
                if rows[identity]["cumulative_cpu_seconds"] < previous.rows[identity]["cumulative_cpu_seconds"]:
                    regressed = {
                        "pid": identity[0], "start": identity[1],
                        "command": rows[identity]["command"], "reason": "counter regressed",
                        "contaminant": rows[identity]["contaminant"] or previous.rows[identity]["contaminant"]}
                    receipt["cpu_interval"]["regressed_counters"].append(regressed)
                    if not regressed["contaminant"]:
                        receipt["cpu_interval"]["regressed_noncontaminant"].append(regressed)
        self._snapshots.append(snapshot)
        return snapshot

    def _cpu_interval(self, receipt):
        details = receipt["cpu_interval"] = {"regressed_counters": [], "regressed_noncontaminant": []}
        current = self._cpu_snapshot(receipt)
        dwell_ns = prewindow.INTERVAL_S * 1_000_000_000
        # Only first admission can lack a 30 s opening. Later calls, including
        # those after a gap, judge retained data without stalling decoding.
        baseline = self._snapshots[0]
        while current.midpoint_ns - baseline.midpoint_ns < dwell_ns:
            remaining = (dwell_ns - (current.midpoint_ns - baseline.midpoint_ns)) / 1e9
            self.sleep(remaining)
            current = self._cpu_snapshot(receipt)
        opening_index = max(i for i, snapshot in enumerate(self._snapshots)
                            if current.midpoint_ns - snapshot.midpoint_ns >= dwell_ns)
        opening = self._snapshots[opening_index]
        # Retain the newest eligible opening and every more recent snapshot.
        del self._snapshots[:opening_index]
        busy = self._judge_cpu_interval(opening, current, details)
        if details["long_interval"]:
            receipt["long_interval"] = True
        return busy

    def _judge_cpu_interval(self, opening, current, details):
        limit = prewindow.CPU_LIMIT_PERCENT / 100
        measured = contention.interval(opening, current, tree_roots=(),
                                       include_kernel_task=True, limit=limit,
                                       previous_over=self._previous_over)
        details.update({
            "start_monotonic_s": opening.midpoint_ns / 1e9,
            "end_monotonic_s": current.midpoint_ns / 1e9,
            "elapsed_s": measured["elapsed_s"], "contaminants": [],
            "unaccounted": measured["unaccounted"],
            "long_interval": measured["elapsed_s"] > 2 * prewindow.INTERVAL_S})
        matches = {}
        for snapshot in (opening, current):
            for identity, row in snapshot.rows.items():
                if row["contaminant"]:
                    matches.setdefault(identity, set()).update(row["contaminant_matches"])
        def contaminant(row):
            return (row["pid"], row["start"]) in matches
        regressions = [row for row in measured["unaccounted"] if row["reason"] == "counter regressed"]
        for row in regressions:
            entry = {**row, "contaminant": contaminant(row)}
            for key in ("regressed_counters", "regressed_noncontaminant"):
                if key == "regressed_noncontaminant" and entry["contaminant"]:
                    continue
                recorded = details[key]
                recorded[:] = [entry for entry in recorded
                               if (entry["pid"], entry["start"]) != (row["pid"], row["start"])]
                recorded.append(entry)
        # The module carries prior over-limit evidence into outside_over_limit
        # via exited_over_limit. An unproven regression alone is disclosure.
        if measured["error"] and measured["error"] != contention.REGRESSED_COUNTER_ERROR:
            raise Refused(f"census indeterminate: {measured['error']}")
        busy = [row for row in measured["outside_over_limit"] if contaminant(row)]
        self._previous_over = {identity: rate for identity, rate in contention.over_limit(measured).items()
                               if identity in matches}
        for row in measured["outside_listed"]:
            if contaminant(row) and row["cpu_s_per_s"] > contention.REPORT_FLOOR_CPU_S_PER_S:
                details["contaminants"].append({
                    "pid": row["pid"], "lstart": row["start"], "name": row["command"],
                    "matched_on": sorted(matches[(row["pid"], row["start"])]),
                    "cpu_s": row["cpu_s_per_s"] * measured["elapsed_s"],
                    "cpu_s_per_s": row["cpu_s_per_s"]})
        details["exited_over_limit"] = [
            row for row in measured["exited_over_limit"] if contaminant(row)]
        return busy

    def check(self, *, force=False):
        if self.failure:
            raise Refused(self.failure)
        receipt = {"resolved_custody_parents": []}
        try:
            now = self._now()
            if not force and now - self.last < 15:
                return
            receipt["monotonic_s"] = now
            self.receipts.append(receipt)
            extra = json.loads(os.environ.get(ADDITIONAL_PARENTS_ENV, "[]"))
            if not isinstance(extra, list) or any(not isinstance(p, str) or not p for p in extra):
                raise Refused("additional custody parents must be a JSON array of paths")
            parents = [custody_parent(), *(Path(p).expanduser() for p in extra), *self.parents]
            for parent in parents:
                if not parent.is_absolute() or "restricted" in parent.parts or ".." in parent.parts:
                    raise Refused(f"invalid custody parent: {parent}")
            parents = list(dict.fromkeys(p.resolve() for p in parents))
            receipt["resolved_custody_parents"] = [str(p) for p in parents]
            for parent in parents:
                if "restricted" in parent.parts or not parent.is_dir():
                    raise Refused(f"custody parent missing or not a directory: {parent}")
            installed = sorted(str(p) for p in (Path.home() / "Library/LaunchAgents").glob("com.joulewise.night*.plist"))
            receipt["installed_night_agents"] = installed
            if installed:
                raise Refused(f"measurement window armed: {installed}")
            launched = self.run(("/bin/launchctl", "print", f"gui/{os.getuid()}/com.joulewise.night"),
                                capture_output=True, text=True, timeout=15)
            receipt["launchctl"] = {"exit_code": launched.returncode, "stdout": launched.stdout,
                                    "stderr": launched.stderr}
            if launched.returncode == 0:
                raise Refused("measurement night LaunchAgent is loaded")
            if launched.returncode != 113 or "could not find service" not in launched.stderr.lower():
                raise Refused("LaunchAgent census indeterminate")
            def probe(argv):
                r = self.run(argv, capture_output=True, text=True, timeout=15)
                return ProbeResult(argv, r.returncode, r.stdout, r.stderr, time.monotonic_ns())
            agent, refusal = agent_census(SimpleNamespace(run=probe, monotonic_ns=time.monotonic_ns))
            custody = self.inspect_custody(parents=parents)
            table = probe(PS_ARGV)
            if table.exit_code != 0:
                raise Refused("process table unavailable")
            diagnostic = busy_contaminants(table.stdout)  # also validates every row
            chains = []
            pattern = re.compile(
                r"(?:^|[/\s])(?:run_campaign|run_night|window[-_]chain|"
                r"align_r1_rehearsal|align_r0_checks|run_b5_analysis|chain|powermetrics)"
                r"(?:\.py|\.sh|\.zsh)?(?:\s|$)", re.I)
            for line in table.stdout.splitlines():
                pid, _, argv = line.split(None, 2)
                if int(pid) != os.getpid() and pattern.search(argv):
                    chains.append(line)
            receipt.update(agent=asdict(agent), custody=asdict(custody),
                           pcpu_diagnostic=diagnostic, chains=chains)
            if refusal or not custody.clear or chains:
                raise Refused(f"machine occupied or census indeterminate: {receipt}")
            busy = self._cpu_interval(receipt)
            receipt["busy"] = busy
            if busy:
                names = ", ".join(f"{row['pid']} {row['command']} {row['cpu_s_per_s']:.6g} CPU-s/s"
                                  for row in busy)
                raise Refused(f"contaminating CPU contention: {names}")
            self.last = self._now()
        except Exception as exc:
            if not any(item is receipt for item in self.receipts):
                self.receipts.append(receipt)
            self.failure = str(exc)
            receipt["refusal"] = self.failure
            raise Refused(self.failure) from exc


def _hub_blob(path, hub_root):
    """Resolve each link inside the hub before inspecting its target."""
    pending = list(path.relative_to(hub_root).parts)
    resolved, links = hub_root, 0
    while pending:
        part, *pending = pending
        if part == "restricted":
            raise ValueError(f"refusing restricted target: {path}")
        if part == "..":
            if resolved == hub_root:
                raise ValueError(f"symlink escapes hub root: {path}")
            resolved = resolved.parent
            continue
        candidate = resolved / part
        if candidate.is_symlink():
            links += 1
            if links > 40:
                raise ValueError(f"symlink loop: {path}")
            target = Path(os.readlink(candidate))
            if target.is_absolute():
                if not target.is_relative_to(hub_root):
                    raise ValueError(f"symlink escapes hub root: {path}")
                resolved = hub_root
                target = target.relative_to(hub_root)
            pending = list(target.parts) + pending
        else:
            resolved = candidate
    relative = resolved.relative_to(hub_root)
    if (len(relative.parts) != 3 or not relative.parts[0].startswith("models--")
            or relative.parts[1] != "blobs" or not resolved.is_file()):
        raise ValueError(f"not a regular HF hub blob: {path}")
    return resolved


def inventory(root, tick=lambda: None):
    """Hash local files, including confined HF snapshot-to-blob links.

    Only a models--*/snapshots/<revision> root enables file links. Each must
    resolve to a regular models--*/blobs/<file> within that same hub directory.
    Directory links, escaping links and restricted components always refuse.
    """
    root = Path(root)
    if "restricted" in root.parts or root.is_symlink() or not root.is_dir():
        raise ValueError(f"not a materialized unrestricted directory: {root}")
    root = root.resolve()
    if "restricted" in root.parts:
        raise ValueError(f"refusing restricted directory: {root}")
    hub_root = (root.parent.parent.parent if root.parent.name == "snapshots"
                and root.parent.parent.name.startswith("models--") else None)
    rows = []
    def walk(directory):
        # os.walk classifies links with a target stat before yielding them.
        # Inspect links first so escapes refuse before any target access.
        with os.scandir(directory) as stream:
            entries = sorted(stream, key=lambda entry: entry.name)
        for entry in entries:
            tick()
            path = Path(entry.path)
            if entry.name == "restricted":
                raise ValueError(f"refusing restricted path: {path}")
            if entry.is_symlink():
                if hub_root is None:
                    raise ValueError(f"not an HF snapshot link: {path}")
                yield path, _hub_blob(path, hub_root)
            elif entry.is_dir(follow_symlinks=False):
                yield from walk(path)
            elif entry.is_file(follow_symlinks=False):
                yield path, path
            else:
                raise ValueError(f"not a regular materialized file: {path}")
    for path, target in walk(root):
        digest = hashlib.sha256()
        size = 0
        with target.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                tick()
                digest.update(chunk)
                size += len(chunk)
        rows.append({"path": path.relative_to(root).as_posix(),
                     "bytes": size, "sha256": digest.hexdigest()})
    if not rows:
        raise ValueError(f"empty inventory: {root}")
    return sorted(rows, key=lambda row: row["path"])


def disk_census(config, pins, tick=lambda: None):
    """Report R0 storage and local model hashes; no W1 arm gates or offloads."""
    budget = step_budget(config.get("smc_step"))
    free = shutil.disk_usage(config["disk_path"]).free
    anchor_files = inventory(config["anchor_source"], tick)
    models = {}
    for tag, entry in config["models"].items():
        rows = inventory(entry["source"], tick)
        total = sum(row["bytes"] for row in rows)
        models[tag] = {"files": rows, "bytes": total,
                       "design_download_bytes": pins[tag]["bytes"],
                       "difference_bytes": total - pins[tag]["bytes"],
                       "revision": pins[tag]["revision"],
                       "identity_note": "Local hashes; revision is configured, not independently authenticated."}
    return {"status": "diagnostic", "purpose": "r0_report_only",
            "free_bytes_after_present_weights": free, "smc_step_budget": budget,
            "w1_required_free_bytes_after_r0": 80_000_000_000,
            "design": {"W1_bytes_per_copy": 18_710_000_000, "W1_two_copies_bytes": 37_400_000_000,
                       "D_two_copies_bytes": 52_900_000_000, "disk_figures_are_rounded_planning_estimates": True},
            "anchor": {"files": anchor_files, "bytes": sum(r["bytes"] for r in anchor_files),
                       "revision": "d388dead1515f5e085ef7a0431dd8fadf0886c57",
                       "identity_note": "Local hashes; remote revision not independently authenticated."},
            "models": models, "offloads": [],
            "configured_w1_offload_labels": [item["label"] for item in config.get("offloads", [])],
            "note": "R0 disk check is report-only. Free space and configured offload hashes gate W1 via w1_disk_gate."}


def w1_disk_gate(config, tick=lambda: None):
    """Require 80 decimal GB after R0 and verify every configured offload.

    Call at W1 arm time, after R0's journal has been written. This read-only
    check neither performs offloads nor grants an arm authorization.
    """
    free = shutil.disk_usage(config["disk_path"]).free
    offloads = []
    for item in config.get("offloads", []):
        tick()
        row = {"label": item["label"], "pass": False,
               "inventory": item["inventory"], "destination": item["destination"]}
        offloads.append(row)
        try:
            # Saved BEFORE offload; the source need not remain on local disk.
            expected = json.loads(Path(item["inventory"]).read_text())
            actual = inventory(item["destination"], tick)
            row.update(observed=actual, **{"pass": isinstance(expected, list) and bool(expected) and expected == actual})
        except (OSError, ValueError) as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
    return {"status": "pass" if free >= 80_000_000_000 and all(row["pass"] for row in offloads) else "fail",
            "purpose": "w1_arm_gate", "free_bytes_after_present_weights": free,
            "required_free_bytes_after_r0": 80_000_000_000, "offloads": offloads,
            "required_offload_labels": [row["label"] for row in offloads]}


def swap_bytes(run=command):
    text = run(("/usr/sbin/sysctl", "-n", "vm.swapusage"))
    match = re.search(r"used\s*=\s*([0-9.]+)([KMG])", text)
    if not match:
        raise ValueError("vm.swapusage used value unavailable")
    return int(float(match[1]) * {"K": 1024, "M": 1024**2, "G": 1024**3}[match[2]])


def host_identity(expected_model, run=command):
    """Always gate native model work, including CLI subsets, on host capacity."""
    try:
        memory = int(run(("/usr/sbin/sysctl", "-n", "hw.memsize")).strip())
        model = run(("/usr/sbin/sysctl", "-n", "hw.model")).strip()
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}
    return {"status": "pass" if memory >= 128 * 1024**3 and model == expected_model else "fail",
            "hw_memsize": memory, "hw_model": model, "expected_hw_model": expected_model,
            "minimum_memory_bytes": 128 * 1024**3}


def host_snapshot(run=command):
    probes = {"pmset_custom": ("/usr/bin/pmset", "-g", "custom"),
              "pmset_battery": ("/usr/bin/pmset", "-g", "batt"),
              "pmset_thermal": ("/usr/bin/pmset", "-g", "therm"),
              "wired_limit": ("/usr/sbin/sysctl", "iogpu.wired_limit_mb"),
              "physical_memory": ("/usr/sbin/sysctl", "-n", "hw.memsize")}
    out = {}
    for name, argv in probes.items():
        try:
            out[name] = {"status": "pass", "stdout": run(argv)}
        except Exception as exc:
            out[name] = {"status": "fail", "error": str(exc)}
    batt = out["pmset_battery"].get("stdout", "")
    custom = out["pmset_custom"].get("stdout", "")
    settings = custom.split("AC Power:")[-1] if "AC Power:" in custom else ""
    mode = re.search(r"(?m)^\s*powermode\s+(\d+)\s*$", settings)
    low = re.search(r"(?m)^\s*lowpowermode\s+(\d+)\s*$", settings)
    powered = "AC Power" in batt
    # macOS 26 spells this powermode, older versions lowpowermode. Both
    # Automatic (0) and explicitly observed High Power (2) are recorded.
    power_ok = bool((mode and mode[1] in {"0", "2"}) or (not mode and low and low[1] == "0"))
    readiness = {"on_ac": powered, "power_mode_ok": power_ok,
                 "observed_power_mode": mode[1] if mode else None,
                 "observed_lowpowermode": low[1] if low else None}
    return {"status": "pass" if powered and power_ok and all(r["status"] == "pass" for r in out.values()) else "fail",
            "probes": out, "readiness": readiness,
            "note": "Read-only desk readiness; R1 lever adoption and arm readiness require their own gates."}


def smc_enumeration(repo, output, step=None):
    try:
        profile = profile_config(step)
    except ProfileRefused as exc:
        return {"status": "refused", "refusal_code": exc.code, "reason": str(exc)}
    budget = step_budget(profile)
    script = Path(repo) / "scripts/align_smc_enumerate.py"
    if not script.is_file():
        return {"status": "unavailable", "reason": "SMC lane not integrated"}
    import sys
    argv = [sys.executable, "-B", str(script), "--output", str(output), "--gpu-step",
            "--idle-seconds", str(profile["idle_seconds"]), "--idle-max-seconds", str(profile["idle_max_seconds"]),
            "--load-seconds", str(profile["load_seconds"]),
            "--recovery-seconds", str(profile["recovery_seconds"])]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=budget["timeout_seconds"])
    receipt = {"status": "fail" if result.returncode else "inconclusive",
               "argv": argv, "exit_code": result.returncode, "smc_step_budget": budget,
               "timeout_seconds": budget["timeout_seconds"],
               "stdout": result.stdout, "stderr": result.stderr,
               "smc_source_commit": "58525031a",
               "selection_status": "PROVISIONAL",
               "step_ruling": "docs/align/r0_step_test_ruling.md",
               "note": "Idle plus load-step selection; R1 still owns thermal-control qualification."}
    if result.returncode:
        return receipt
    try:
        payload = json.loads((Path(output) / "r0.json").read_text())
        if payload["schema"] != "joulewise.align_smc_r0.v1" or payload["gpu_step"] is not True:
            raise ValueError("not a #658 GPU-step receipt")
        if payload["samples_journal"] != "samples.jsonl":
            raise ValueError("unexpected SMC journal name")
        raw = (Path(output) / "samples.jsonl").read_bytes()
        if hashlib.sha256(raw).hexdigest() != payload["samples_sha256"]:
            raise ValueError("SMC journal SHA-256 mismatch")
        samples = [json.loads(line) for line in raw.splitlines() if line.strip()]
        # Authenticate observed adaptive phase lengths before either analysis.
        phases = payload["phases"]
        if [p["phase"] for p in phases] != ["idle", "load", "recovery"]:
            raise ValueError("SMC step phases must be idle, load, recovery")
        previous = 0
        duration_flags = []
        for phase in phases:
            begin, end = phase["start_s"], phase["end_s"]
            if (type(begin) not in (int, float) or type(end) not in (int, float)
                    or not math.isfinite(begin) or not math.isfinite(end) or begin < previous or end <= begin):
                raise ValueError("invalid SMC phase bounds")
            duration = end-begin
            # Erratum 2: deviation >one 1 Hz period is a bookkeeping flag,
            # never a refusal; quiet probes can overrun a phase deadline.
            # Adaptive idle is compared to its configured [minimum, cap].
            if phase["phase"] == "idle":
                deviation = duration - min(max(duration, profile["idle_seconds"]), profile["idle_max_seconds"])
            else:
                deviation = duration-profile[phase["phase"]+"_seconds"]
            if abs(deviation) > 1:
                duration_flags.append({"phase": phase["phase"], "actual_seconds": duration,
                                       "deviation_seconds": deviation})
            previous = end
        receipt["phase_duration_flags"] = duration_flags
        # The old load-fit block is diagnostic only. It expects exact fixed
        # lengths; use this capture's actual phase lengths, never the idle cap.
        diagnostic_profile = {p["phase"]+"_seconds": p["end_s"]-p["start_s"] for p in phases}
        try:
            diagnostic = rank_response(payload, samples, {
                k: round(v) for k, v in diagnostic_profile.items()})
        except ValueError as exc:
            diagnostic = {"status": "unavailable", "reason": str(exc)}
        # Erratum 4: a legacy journal has only actual ends. Reconstruct fixed
        # deadlines from the invoked profile, and adaptive idle from its
        # deciding evaluation (recorded by new collectors), bounded by its cap.
        grid_phases = []
        for phase in phases:
            name, begin = phase["phase"], phase["start_s"]
            deadline = (min(phase.get("deadline_s", phase["end_s"]), begin+profile["idle_max_seconds"])
                        if name == "idle" else begin+profile[name+"_seconds"])
            grid_phases.append({**phase, "deadline_s": deadline})
        classification = classify_smc({**payload, "phases": grid_phases, "samples": samples}, stage="r0")
        selection = {name: classification[name] for name in ("s_fast", "s_slow")}
        resolved = all(isinstance(v, str) and re.fullmatch(r"T[!-~]{3}", v) for v in selection.values())
        resolved = resolved and selection["s_fast"] != selection["s_slow"]
        receipt.update(selection=selection, response=classification,
                       **{field: classification[field] for field in (
                           "heat_ordering_reference", "heat_ordering_reference_rise", "heat_ordering_excluded")},
                       selected_key_aliases=classification["selected_key_aliases"],
                       exponential_fit_diagnostic=diagnostic, source_response=payload["response"])
        receipt["capture_coverage_diagnostic"] = payload["coverage"]
        by_key = {row["key"]: row for row in classification["ranking"]}
        selected_rows = {key: by_key[key] for key in selection.values() if key in by_key}
        receipt["selected_key_readability"] = {key: {field: row[field] for field in (
            "phase_coverage", "phase_read_error_fraction", "phase_seconds", "phase_valid_samples",
            "phase_max_empty_cells", "period_ns", "max_interval_ns", "baseline_unsettled", "baseline_slope_c_min")}
            for key, row in selected_rows.items()}
        # Keep the capture's nominal one-Hz period assertion; the capture-wide
        # occupancy fraction itself is diagnostic and never refuses a pick.
        readable = (resolved and classification["readability_bar_met"]
                    and payload["coverage"]["period_ns"] == 1_000_000_000)
        for row in selected_rows.values():
            # Erratum 2 D6: per-phase one-second-cell occupancy >=99%, <1%
            # read errors, no two adjacent empty cells (U1(c)'s 2 s window).
            # The old total >=600 s bar was vacuous under this step profile.
            readable = (readable and row["period_ns"] == 1_000_000_000
                        and all(v >= .99 for v in row["phase_coverage"].values())
                        and all(v < .01 for v in row["phase_read_error_fraction"].values())
                        and all(v < 2 for v in row["phase_max_empty_cells"].values()))
        receipt["readability_bar_met"] = bool(readable)
        if not resolved:
            receipt["reason"] = "SMC die/heatsink selection unresolved"
        elif not readable:
            receipt["reason"] = "SMC selected-key coverage does not meet 1 Hz / >=99% per phase / <1% errors / no consecutive empty cells"
        else:
            receipt["status"] = "pass"
            receipt["reason"] = "WP14(a) model-free classifier and readability bars met; picks PROVISIONAL"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        receipt["reason"] = f"SMC r0.json selection unavailable: {exc}"
    return receipt
