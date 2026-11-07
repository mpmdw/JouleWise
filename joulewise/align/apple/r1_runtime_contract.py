"""WP15 runtime contract for the ALIGN v4 R1 rehearsal driver.

``scripts/align_r1_rehearsal.py`` invokes one runtime argv per segment as

    <runtime...> --r1-kind KIND --output DIR [--duration-s N] [--soak-reference FILE]

and reads one JSON object from stdout. This module is the single declaration
of the fields each kind must return (``docs/align/r1_runtime_contract.md``
is its prose form) plus the host-side reference implementation of the two
fields every quiet segment needs: the per-second CPU load journal and the
process census (council ruling 8). The model, SMC and gate measurements stay
with the WP15 runtime; nothing here opens a model or a sensor.
"""
from __future__ import annotations

import subprocess
import time

# cpu_busy_t_s: one sample time (s, segment clock) per cpu_busy_cores value,
# so the driver can bound journal gaps (executing review MEDIUM-1).
QUIET_FIELDS = ("cpu_busy_cores", "cpu_busy_t_s", "census")
DEADMAN_PHASES = ("G0", "G1", "H", "decode", "prefill", "tool", "tail")
GATED_D_KINDS = ("d-spam-benign-s1-a", "d-spam-benign-s1-b", "d-bank-benign-s1")
PLANNING_KINDS = tuple(f"d-planning-turn-r-plus-{offset}c" for offset in (0, 2, 4))
HIGH_POWER_KINDS = ("high-power-aba-a1", "high-power-aba-b", "high-power-aba-a2")
# LEAD-RULINGS-2 R7-2: every G0 wait is recorded. Every kind that runs a G0
# reports the wait and the cap it ran under (the R1 timeout, g0_timeout_s, for
# step-d, the designed states, the gated runs and X-G; 600 s otherwise).
G0_WAIT_FIELDS = ("g0_wait_s", "g0_timeout_s")

# Fields per kind, in addition to QUIET_FIELDS for quiet segments. Dotted names
# are nested keys. ``soak_reference`` marks kinds that need --soak-reference.
KIND_FIELDS = {
    "calibration-pre": (),
    "calibration-post": (),
    "idle": (),
    # sensor_series_t_s: one read time per value, so the soak SD uses the last
    # 1,200 s and not the last 1,200 valid samples (cold pass round 4 LOW-2);
    # sensor_series_end_t_s: the soak's end on the same clock (the window's end).
    "idle_soak": ("sensor_series_c", "sensor_series_t_s", "sensor_series_end_t_s"),
    # Ruling 4(b): the battery drain rate (%/h) under the 30B and under D.
    # Protocol v4 :243-251 (LEAD-RULINGS-2 R5-5): the full-inventory R1
    # classification around both planning-turn steps (the 30B for the record).
    "step-30b": ("battery_drain_pct_per_h", "thermometry.status", "thermometry.classification_sha256",
                 *G0_WAIT_FIELDS),
    "step-d": ("slots", "e_D_j_per_token", "battery_drain_pct_per_h", "thermometry.status",
               "thermometry.classification_sha256", "thermometry.alias_groups", *G0_WAIT_FIELDS),
    # released: S_slow reached the G0 band of R (<= R + delta_slow) before the cap.
    "idle-until-soak": ("recovery_curve", "released"),
    # R5-1: X-G and the gated D runs gate against the soak R (reference_source
    # r1_soak_reference), never a self-captured warm reference. R6-1: each
    # follows a D turn with only W1's inter-member schedule (the member's own
    # configured idle, inter_member_idle_s); its G0 outcome decides whether
    # the run is judged or INCONCLUSIVE. R6-3: decode_tokens gives the run's
    # observed decode rate (with deadman.phases_s.decode) for ruling 1(f).
    # R7-2: their G0 wait (g0_wait_s) under the R1 timeout (g0_timeout_s).
    "x-g": ("reference_c", "reference_source", "g0_outcome", "inter_member_idle_s", *G0_WAIT_FIELDS),
    **{kind: ("energy_j", "admitted_turns", "x7", "deadman.T_dead_s", "deadman.phases_s",
              "battery_drain_pct_per_h", "reference_c", "reference_source", "gate_waits_s.G1",
              "gate_waits_s.H", "g0_outcome", "inter_member_idle_s", "decode_tokens", *G0_WAIT_FIELDS)
       for kind in GATED_D_KINDS},
    **{kind: ("reference_c", "g0_release_c", "delta_slow_c", "energy_j", *G0_WAIT_FIELDS)
       for kind in PLANNING_KINDS},
    "d-4bit": G0_WAIT_FIELDS,
    "g0-release-soak": ("released", *G0_WAIT_FIELDS),
    # R5-3: g0_released false = the leg's own G0 did not release (no turn, no
    # t_decline); the driver makes adoption INCONCLUSIVE and R1 continues.
    **{kind: ("t_decline_s", "g0_released", *G0_WAIT_FIELDS) for kind in HIGH_POWER_KINDS},
    # Ruling 4(b): the SoC at which charging resumed during R1 (null if never).
    "harvest": ("charge_resume_soc_pct",),
}
# LEAD-RULINGS-2 R6-2: step-d and the designed start states are calibration
# segments; a G0 that does not release there is INCONCLUSIVE for that segment
# (the driver precools and retries it once), not a refusal of the R1 night.
# Such a result carries segment_status "inconclusive" and g0_released false,
# and only these fields beside the quiet ones.
G0_INCONCLUSIVE_KINDS = ("step-d", *PLANNING_KINDS)
INCONCLUSIVE_FIELDS = ("segment_status", "g0_released", "g0_outcome", *G0_WAIT_FIELDS)
NEEDS_SOAK_REFERENCE = frozenset(("idle-until-soak", "g0-release-soak", "x-g", *GATED_D_KINDS, *PLANNING_KINDS,
                                  *HIGH_POWER_KINDS))


def is_g0_inconclusive(kind, result):
    """R6-2: an INCONCLUSIVE step-d or designed start state (its G0 did not release)."""
    return (kind in G0_INCONCLUSIVE_KINDS and isinstance(result, dict)
            and result.get("segment_status") == "inconclusive")


def required_fields(kind, *, quiet, contract_key=None, inconclusive=False):
    """Return the field names the runtime must return for ``kind``."""
    key = contract_key or kind
    if key not in KIND_FIELDS:
        raise ValueError(f"r1 runtime contract has no kind {key!r}")
    if inconclusive:
        if key not in G0_INCONCLUSIVE_KINDS:
            raise ValueError(f"r1 runtime contract: {key!r} has no INCONCLUSIVE result")
        return tuple(QUIET_FIELDS) + INCONCLUSIVE_FIELDS
    fields = list(KIND_FIELDS[key])
    if quiet:
        fields = list(QUIET_FIELDS) + fields
    if key in GATED_D_KINDS:
        fields += [f"deadman.phases_s.{phase}" for phase in DEADMAN_PHASES]
    return tuple(fields)


def missing_fields(kind, result, *, quiet, contract_key=None):
    """Names from ``required_fields`` absent in ``result`` (presence only)."""
    missing = []
    inconclusive = is_g0_inconclusive(contract_key or kind, result)
    for name in required_fields(kind, quiet=quiet, contract_key=contract_key, inconclusive=inconclusive):
        value = result
        for part in name.split("."):
            if not isinstance(value, dict) or part not in value:
                missing.append(name)
                break
            value = value[part]
    return missing


# --- Reference implementation: per-second CPU load journal and census ------

PS_ARGV = ("/bin/ps", "-A", "-o", "pid=,ppid=,pcpu=,comm=")


def _run(argv):
    return subprocess.run(argv, text=True, capture_output=True, check=False, timeout=10)


def process_table(runner=None):
    """Return ``[{pid, ppid, pcpu, comm}]`` from one ``ps`` snapshot."""
    result = (runner or _run)(PS_ARGV)
    if result.returncode:
        raise ValueError(f"ps failed: exit {result.returncode}")
    rows = []
    for line in result.stdout.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 3:
            continue
        try:
            rows.append({"pid": int(parts[0]), "ppid": int(parts[1]), "pcpu": float(parts[2]),
                         "comm": parts[3] if len(parts) > 3 else ""})
        except ValueError:
            continue
    return rows


def descendants(rows, roots):
    """PIDs of ``roots`` and every descendant in ``rows``."""
    children = {}
    for row in rows:
        children.setdefault(row["ppid"], []).append(row["pid"])
    seen, stack = set(), list(roots)
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, ()))
    return seen


def busy_cores(rows, exclude_roots=()):
    """Background CPU load in cores: the summed %CPU / 100 outside the measured tree."""
    excluded = descendants(rows, exclude_roots)
    return sum(row["pcpu"] for row in rows if row["pid"] not in excluded) / 100.0


class LoadJournal:
    """Per-second background-load journal and census for one quiet segment.

    ``exclude_roots`` are the PIDs of the measured workload (the runtime and
    its children), whose own CPU is not background load. The census is the
    full process table at segment start and end.
    """

    def __init__(self, exclude_roots=(), *, runner=None, clock=time.monotonic):
        self.exclude_roots = tuple(exclude_roots)
        self.runner = runner
        self.clock = clock
        self.cpu_busy_cores = []
        self.cpu_busy_t_s = []
        self.census = []
        self.t0 = clock()

    def snapshot(self, label):
        rows = process_table(self.runner)
        self.census.append({"label": label, "t_s": self.clock(), "processes": rows})
        return rows

    def sample(self):
        value = busy_cores(process_table(self.runner), self.exclude_roots)
        self.cpu_busy_cores.append(value)
        self.cpu_busy_t_s.append(self.clock() - self.t0)
        return value

    def fields(self):
        return {"cpu_busy_cores": list(self.cpu_busy_cores), "cpu_busy_t_s": list(self.cpu_busy_t_s),
                "census": list(self.census)}
