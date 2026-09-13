# Exhibit B — where the census is evaluated

## scripts/run_night.py lines 1490–1515
```python
            plan,
            EXIT_REFUSED,
            resolved_courier,
            deadman_epoch_s=deadman_epoch_s,
            courier_bin_substitution=courier_substitution,
        )

    prepared = arm_state = None
    is_pack = plan.receipt_class == "TRANSACTION_PACK"
    if is_pack:
        try:
            if initial_refusal is not None or initial_probe.exit_code != 1 or initial_probe.stdout != "":
                error = PackNightRefusal("census: " + (initial_refusal.detail if initial_refusal else "stdout must be empty"))
                if initial_refusal is not None:
                    error.reason = initial_refusal.reason
                raise error
            if rehearsal:
                raise PackNightRefusal("receipt_class: rehearsal flag requires REHEARSAL_STUB")
            prepared = _prepare_pack_night(plan, plan_path, plan_raw)
            arm_state = _author_pack_arm(plan, prepared)
            receipt = evaluate_night(plan, probes, pack_arm_receipt=arm_state["path"])
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as error:
            receipt = _pack_refused_receipt(plan, error, probes)
    else:
        # Reuse the first census for the legacy evaluator's census slot; no
        # filesystem or command probe preceded the driver's initial census.
```

## scripts/author_arm_evidence_t0.py lines 1–60
```python
#!/usr/bin/env python3
"""Author the fifteen D-134 T-0 evidence receipts in window custody."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness  # noqa: E402
from joulewise.arm_readiness import ArmReadinessError, render_json  # noqa: E402
from joulewise.arm_readiness_evidence_t0 import (  # noqa: E402
    T0EvidenceAuthoringError,
    author_arm_readiness_evidence_t0,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack-root", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        root = args.pack_root.resolve(strict=True)
        custody = args.custody_root.resolve(strict=True)
        pack_repository = readiness._repo_for_pack(root).resolve(strict=True)
        cli_repository = REPO_ROOT.resolve(strict=True)
        if pack_repository != cli_repository:
            raise T0EvidenceAuthoringError(
                "AUTHORING_SET",
                "evidence_author_t0_repository_mismatch",
                "pack repository differs from the T-0 evidence-author CLI repository",
            )
        result = author_arm_readiness_evidence_t0(root, custody)
        result["next_step"] = {
            "command": (
                "python3 scripts/generate_arm_readiness.py arm "
                f"--pack-root {root} --arm-context '<canonical JSON object>' "
                f"--window-custody-root {custody}"
            ),
            "warning": (
                "Run immediately in the same boot session; any refusal ends this "
                "arm attempt and is not an operator override point."
            ),
        }
    except T0EvidenceAuthoringError as exc:
        result = {
            "status": "REFUSE",
            "kind": exc.kind,
            "reason_codes": [exc.reason_code],
            "detail": str(exc),
```

## joulewise/arm_readiness_evidence_t0.py lines 100–130 (row ids and kinds)
```python
    "clock.correct_and_prior_state",
    "clock.network_time_off",
    "desk.terminal_review",
    "t0.background_quiet",
    "t0.campaign_lock_absent",
    "t0.display_thermal_idle",
    "t0.fresh_roots_waivers",
    "t0.ledger_reservation",
    "t0.machine_readiness",
    "t0.no_stray_keepawake",
    "t0.offline_inputs",
    "t0.passwordless_powermetrics",
    "t0.power_path",
    "t0.single_launch_capability",
    "t0.storage_backup_capacity",
)
_ROW_KIND = {
    "clock.correct_and_prior_state": "CLOCK_ATTESTATION",
    "clock.network_time_off": "CLOCK_PROBE",
    "desk.terminal_review": "TERMINAL_REVIEW",
    "t0.background_quiet": "MAINTENANCE_CENSUS",
    "t0.campaign_lock_absent": "ROOT_PREFLIGHT",
    "t0.display_thermal_idle": "MACHINE_PREFLIGHT",
    "t0.fresh_roots_waivers": "ROOT_PREFLIGHT",
    "t0.ledger_reservation": "LEDGER_RESERVATION",
    "t0.machine_readiness": "MACHINE_PREFLIGHT",
    "t0.no_stray_keepawake": "PROCESS_CENSUS",
    "t0.offline_inputs": "OFFLINE_INPUT_INVENTORY",
    "t0.passwordless_powermetrics": "POWERMETRICS_PROBE",
    "t0.power_path": "POWER_PREFLIGHT",
    "t0.single_launch_capability": "LAUNCH_RECIPE",
```

## configs/arm_readiness/d117_row_registry_v2.json — the t0.no_stray_keepawake row and the profiles' required_row_ids that name it
```json
/freeze_evidence_lifecycle/row_policies/29
{
 "freshness_policy_id": "r1.time_bound.volatile_20m.v1",
 "row_id": "t0.no_stray_keepawake"
}
/rows/29
{
 "applicability_rule": "ALWAYS",
 "evaluation_phase": "ARM_ONLY",
 "predicate_id": "t0.no_stray_keepawake.v1",
 "required_evidence_kinds": [
  "PROCESS_CENSUS"
 ],
 "row_id": "t0.no_stray_keepawake"
}
required_row_ids mentions of the row: 6
```

## joulewise/arm_readiness.py lines 1105–1120 and 1170–1178 (schema for the row)
```python
        "current": True,
        "frozen_prewindow_check_wait_command": True,
        "same_plan": True,
        "same_roots": True,
        "status": "READY",
    },
    "t0.no_stray_keepawake.v1": {
        "absent_process_classes": ["agent", "browser", "keep_awake", "monitor"],
        "fresh_process_census": True,
    },
    "t0.offline_inputs.v1": {
        "file_inventory_matches_frozen_inputs": True,
        "no_network_fetch": True,
        "u11_live_derivation_matches_frozen_inputs": True,
    },
    "t0.passwordless_powermetrics.v1": {
# …
    "t0.display_thermal_idle.v1": "MACHINE_PREFLIGHT",
    "t0.fresh_roots_waivers.v1": "ROOT_PREFLIGHT",
    "t0.ledger_reservation.v1": "LEDGER_RESERVATION",
    "t0.machine_readiness.v1": "MACHINE_PREFLIGHT",
    "t0.no_stray_keepawake.v1": "PROCESS_CENSUS",
    "t0.offline_inputs.v1": "OFFLINE_INPUT_INVENTORY",
    "t0.passwordless_powermetrics.v1": "POWERMETRICS_PROBE",
    "t0.power_path.v1": "POWER_PREFLIGHT",
    "t0.single_launch_capability.v1": "LAUNCH_RECIPE",
```
