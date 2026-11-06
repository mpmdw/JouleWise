"""Read-only R0 host probes. No model imports or downloads."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
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
from joulewise.align.r0_step import ProfileRefused, profile_config, rank_response, step_budget
from joulewise.align.apple.smc_enumeration import rank as classify_smc


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
    """

    def __init__(self, parents, *, run=subprocess.run, inspect_custody=census,
                 clock=time.monotonic):
        self.parents = [Path(p) for p in parents]
        self.run, self.inspect_custody, self.clock = run, inspect_custody, clock
        self.last = float("-inf")
        self.failure = None
        self.receipts = []

    def check(self, *, force=False):
        if self.failure:
            raise Refused(self.failure)
        if not force and self.clock() - self.last < 15:
            return
        receipt = {"monotonic_s": self.clock(), "resolved_custody_parents": []}
        self.receipts.append(receipt)
        try:
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
            busy = busy_contaminants(table.stdout)  # also validates every row
            chains = []
            pattern = re.compile(
                r"(?:^|[/\s])(?:run_campaign|run_night|window[-_]chain|"
                r"align_r1_rehearsal|align_r0_checks|run_b5_analysis|chain|powermetrics)"
                r"(?:\.py|\.sh|\.zsh)?(?:\s|$)", re.I)
            for line in table.stdout.splitlines():
                pid, _, argv = line.split(None, 2)
                if int(pid) != os.getpid() and pattern.search(argv):
                    chains.append(line)
            receipt.update(agent=asdict(agent), custody=asdict(custody), busy=busy, chains=chains)
            if refusal or not custody.clear or busy or chains:
                raise Refused(f"machine occupied or census indeterminate: {receipt}")
            self.last = self.clock()
        except Exception as exc:
            self.failure = str(exc)
            receipt["refusal"] = self.failure
            raise Refused(self.failure) from exc


def inventory(root, tick=lambda: None):
    """Hash regular files only; refuse symlinks and restricted subdirectories.

    Operators supply a materialized local model mirror, rather than an HF cache
    with links to another tree. This makes the hashed read boundary explicit.
    """
    root = Path(root)
    if "restricted" in root.parts or root.is_symlink() or not root.is_dir():
        raise ValueError(f"not a materialized unrestricted directory: {root}")
    rows = []
    def walk_error(exc):
        raise exc
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        for name in dirs:
            path = Path(directory) / name
            if name == "restricted" or path.is_symlink():
                raise ValueError(f"refusing directory: {path}")
        for name in sorted(files):
            tick()
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"not a regular materialized file: {path}")
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as handle:
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
    budget = step_budget(config.get("smc_step"))
    required = 80_000_000_000 + budget["journal_bytes_estimate"]
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
    offloads = []
    for item in config.get("offloads", []):
        # A source inventory saved BEFORE offload allows the local root to have
        # been removed. No copying or deletion is performed here.
        import json
        expected = json.loads(Path(item["inventory"]).read_text())
        actual = inventory(item["destination"], tick)
        ok = (isinstance(expected, list) and bool(expected) and expected == actual)
        offloads.append({"label": item["label"], "pass": ok,
                         "inventory": item["inventory"], "destination": item["destination"],
                         "observed": actual})
    covered = {row["label"] for row in offloads if row["pass"]}
    return {"status": "pass" if free >= required and {"pilot8", "pilot9"} <= covered else "fail",
            "free_bytes_after_present_weights": free, "required_free_bytes_after_weights": required,
            "required_free_bytes_after_r0": 80_000_000_000, "smc_step_budget": budget,
            "design": {"W1_bytes_per_copy": 18_710_000_000, "W1_two_copies_bytes": 37_400_000_000,
                       "D_two_copies_bytes": 52_900_000_000, "disk_figures_are_rounded_planning_estimates": True},
            "anchor": {"files": anchor_files, "bytes": sum(r["bytes"] for r in anchor_files),
                       "revision": "d388dead1515f5e085ef7a0431dd8fadf0886c57",
                       "identity_note": "Local hashes; remote revision not independently authenticated."},
            "models": models, "offloads": offloads,
            "note": "Download totals are diagnostics (mirror metadata can differ); free-space and offload hashes are gates."}


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
            "--idle-seconds", str(profile["idle_seconds"]), "--load-seconds", str(profile["load_seconds"]),
            "--recovery-seconds", str(profile["recovery_seconds"])]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=budget["timeout_seconds"])
    receipt = {"status": "fail" if result.returncode else "inconclusive",
               "argv": argv, "exit_code": result.returncode, "smc_step_budget": budget,
               "timeout_seconds": budget["timeout_seconds"],
               "stdout": result.stdout, "stderr": result.stderr,
               "smc_source_commit": "274fec2cb2fcc301798c91140e51c244c2469988",
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
        diagnostic = rank_response(payload, samples, profile)
        classification = classify_smc({**payload, "samples": samples}, stage="r0")
        selection = {name: classification[name] for name in ("s_fast", "s_slow")}
        resolved = all(isinstance(v, str) and re.fullmatch(r"T[!-~]{3}", v) for v in selection.values())
        resolved = resolved and selection["s_fast"] != selection["s_slow"]
        receipt.update(selection=selection, response=classification,
                       exponential_fit_diagnostic=diagnostic, source_response=payload["response"])
        coverage = payload["coverage"]
        readable = resolved and classification["readability_bar_met"] and coverage["period_ns"] == 1_000_000_000
        if readable:
            for key in selection.values():
                stats = coverage["per_key"][key]
                expected, valid = stats["expected_samples"], stats["valid_samples"]
                readable = readable and (type(expected) is int and type(valid) is int
                                        and expected >= 600 and 0 <= valid <= expected and valid / expected > .99)
        receipt["readability_bar_met"] = bool(readable)
        if not resolved:
            receipt["reason"] = "SMC die/heatsink selection unresolved"
        elif not readable:
            receipt["reason"] = "SMC selected-key coverage does not meet 1 Hz / <1% errors / 10 min"
        else:
            receipt["status"] = "pass"
            receipt["reason"] = "WP14(a) model-free classifier and readability bars met; picks PROVISIONAL"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        receipt["reason"] = f"SMC r0.json selection unavailable: {exc}"
    return receipt
