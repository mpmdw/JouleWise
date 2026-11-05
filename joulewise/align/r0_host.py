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
    free = shutil.disk_usage(config["disk_path"]).free
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
    return {"status": "pass" if free >= 80_000_000_000 and {"pilot8", "pilot9"} <= covered else "fail",
            "free_bytes_after_present_weights": free, "required_free_bytes_after_weights": 80_000_000_000,
            "design": {"W1_bytes_per_copy": 18_600_000_000, "W1_two_copies_bytes": 37_200_000_000,
                       "D_two_copies_bytes": 52_900_000_000, "N_download_bytes": 44_860_367_003},
            "models": models, "offloads": offloads,
            "note": "Download totals are diagnostics (mirror metadata can differ); free-space and offload hashes are gates."}


def swap_bytes(run=command):
    text = run(("/usr/sbin/sysctl", "-n", "vm.swapusage"))
    match = re.search(r"used\s*=\s*([0-9.]+)([KMG])", text)
    if not match:
        raise ValueError("vm.swapusage used value unavailable")
    return int(float(match[1]) * {"K": 1024, "M": 1024**2, "G": 1024**3}[match[2]])


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


def smc_enumeration(repo, output):
    script = Path(repo) / "scripts/align_smc_enumerate.py"
    if not script.is_file():
        return {"status": "unavailable", "reason": "SMC lane not integrated"}
    import sys
    result = subprocess.run([sys.executable, "-B", str(script), "--output", str(output)],
                            capture_output=True, text=True, timeout=180)
    return {"status": "pass" if result.returncode == 0 else "fail",
            "argv": [str(script), "--output", str(output)], "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "note": "Enumeration only; R1 must qualify fast/slow sensor classes."}
