"""Small, replayable idle-wait ledger and pure admission choices."""
from __future__ import annotations

import json
import math
from pathlib import Path
from joulewise.b6.sleep_guard import append_record

# Collection design 6.2 and threshold note 3.1; sidecars may override after M2.
WAIT_CAP_S = 1500
SESSION_WAIT_BUDGET_S = 7200


class WaitLedger:
    def __init__(self, path: Path):
        self.path = Path(path)

    def remaining(self, budget_s: float) -> float:
        self.exhausted_recorded = False
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return float(budget_s)
        total = 0.0
        for line in lines:
            row = json.loads(line)
            self.exhausted_recorded |= row.get("budget_exhausted") is True
            wait = row["wait_s"]
            if isinstance(wait, bool) or not isinstance(wait, (int, float)) or not math.isfinite(wait) or wait < 0:
                raise ValueError("invalid idle wait ledger duration")
            total += wait
        return float(budget_s) - total

    def append(self, *, run_id: str, wait_s: float, outcome: str, **fields) -> None:
        append_record(self.path, {"run_id": run_id, "wait_s": wait_s, "outcome": outcome, **fields})


def next_step(*, attempt_start_s, now_s, last_attempt_s, cap_s, remaining_s) -> str:
    if remaining_s <= 0:
        return "skip_budget"
    if now_s - attempt_start_s + last_attempt_s > min(cap_s, remaining_s):
        return "skip_budget" if remaining_s < cap_s else "skip_cap"
    return "retry"


def abandon_admission_sampling(adapter, context=None) -> None:
    """End a failed powermetrics stream, preserving its persisted idle attempts.

    Keep this lifecycle operation outside the pinned estimator adapter. Its
    existing native stop/release/reset members own the actual cleanup.
    """
    from joulewise.adapters.powermetrics import RAW_SAMPLES_NAME

    process = adapter._process
    if process is not None:
        adapter._stop_process(process)
    adapter._process = None
    adapter._release_capture(RAW_SAMPLES_NAME)
    adapter._reset_admission_sampling_state()


def busy_fraction_only(cpu_admission: dict, *, evidence_conditions=()) -> bool:
    # Q3 is a disclosure; A18 evidence conditions do not turn it into a wait.
    conditions = cpu_admission.get("conditions")
    return (isinstance(conditions, list)
            and "cpu_busy_ratio_p95_exceeded" in conditions
            and set(conditions) <= set(evidence_conditions) | {"cpu_busy_ratio_p95_exceeded"}
            and cpu_admission.get("gpu_admitted") is not False)
