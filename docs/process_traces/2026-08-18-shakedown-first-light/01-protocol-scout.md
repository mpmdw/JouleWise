```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The v3 calibration route and diagnostic idle sampler command are identified, but current quiet-window clearance and ledger custody block safe execution.",
  "workspace": {
    "base_requested": "/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtS-scout",
    "base_mode": "exact",
    "head_start": "62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b",
    "head_end": "62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "id": "R1",
        "action": "do_not_start",
        "what": "Any QUIET-MAC capture",
        "wait_for": "A current READY-candidate council clearance",
        "collision_surface": "RUN_STATE WINDOW-COUNCIL-GATE"
      },
      {
        "id": "R2",
        "action": "needs_ruling",
        "what": "Three calibration bundles",
        "wait_for": "A lead-approved isolated calibration ledger/custody route",
        "collision_surface": "The production validator mutates the canonical calibration ledger"
      },
      {
        "id": "R3",
        "action": "wait_for",
        "what": "The 600-second diagnostic baseline",
        "wait_for": "The same quiet-machine clearance and lead classification as nonclaim evidence",
        "collision_surface": "Direct powermetrics output is not a governed production run bundle"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD\ngit status --short --branch\ngit diff --name-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b",
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b\\n## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The production v3 validator always performs calibration-ledger reservation/finalization; no supported no-ledger shakedown mode exists.",
      "needs": "Approve a separate committed shakedown ledger checkout or provide a new nonclaim route."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "RUN_STATE currently prohibits quiet-machine work after the 2026-08-15 NOT-READY verdict.",
      "needs": "Confirm current READY-candidate clearance before any lead execution."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The standalone 600-second baseline command produces raw powermetrics only, without governed run-bundle metadata or production idle-admission evidence.",
      "needs": "Preserve raw output, command, fence logs, and post-capture census; label it diagnostic/nonclaim."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| 1 | `do_not_start` current quiet-window work | READY-candidate clearance | `RUN_STATE.md:3667-3683` |
| 2 | Prepare AC, displays asleep, screensaver disengaged, no agents | Lead-owned QUIET-MAC session | `docs/contracts/measurement_methodology.md:38-70` |
| 3 | Capture 600-second idle baseline | Fence completion | Approximately 10 minutes |
| 4 | Run three v3 calibration bundles | Isolated ledger ruling | Approximately 4 minutes each; `docs/phase_2/window_runbook.md:129-148` |
| 5 | Re-derive each `b_fiducial` | Raw artifacts complete | Seconds to minutes; read-only |

## Critical path

D-139 A3 requires quiet-state baseline first, then calibration-only instrument verification before any claim window: `docs/decision_log.md:9720-9728`.

### Calibration bundle

The route is `scripts/validate_powermetrics_fiducial.py`, using frozen protocol v3: 4096² FP16 MLX matmul, three warmups, 59 one-second pulses, 100 ms sampling, and GPU-power detection: `scripts/validate_powermetrics_fiducial.py:1-26`; `configs/calibration/powermetrics_fiducial/protocol_v3.json:1-39`.

The production invocation, repeated exactly three times, is:

```sh
/Users/edr/code/JouleWise/.venv/bin/python /Users/edr/code/JouleWise/scripts/validate_powermetrics_fiducial.py --allow-live --power-policy ac_high_power --output-root /Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation
```

This command requires noninteractive `sudo -n` authorization for `/usr/bin/powermetrics`: `joulewise/adapters/powermetrics.py:126-128,1464-1489`; the validator’s CLI and output-root behavior are defined at `scripts/validate_powermetrics_fiducial.py:1040-1115,1219-1248`.

Do not run that command as-is tonight: its default ledger is the canonical production ledger, and the validator acquires a lease, repairs/reserves, and finalizes ledger state: `scripts/validate_powermetrics_fiducial.py:832-860,924-965,1607-1627`. The ledger contract requires exactly reservation plus finalization for live captures: `docs/contracts/calibration_ledger.md:9-13`.

The D-079 comparison corpus is 19 derivation members, with decimal minimum `0.022741007370546462`, maximum `0.03355875667989999`, and `n=19`: `configs/calibration/calibration_acceptance_d079_v2.json:46-179,449-466`. Existing corpus artifacts are protocol-v3 manifests: `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/manifest.json:1-11`.

### Quiet-state baseline

There is no standalone governed ten-minute idle-baseline CLI. Production campaign runs measure and store an idle baseline inside each bundle: `docs/contracts/measurement_methodology.md:118-149`. The ED-QUAL checklist is only a five-sample sampler check and uses a different battery-inclusive sampler list: `scripts/ed_session/sampler-checklist.sh:54-60`.

The closest literal diagnostic command using production sampler settings is:

```sh
mkdir -p /Users/edr/JouleWise-window-custody/shakedown-20260818/quiet-state-baseline
/usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 600 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o /Users/edr/JouleWise-window-custody/shakedown-20260818/quiet-state-baseline/powermetrics_idle_baseline.plist
```

Expected result: exit 0, a 600-sample plist, approximately ten minutes. This is diagnostic raw sampler evidence, not a claim-bearing governed bundle.

### Reduction

The old `scripts/validate_powermetrics_fiducial.py --rederive-artifact` path refuses non-v1/v2 40-pulse evidence: `scripts/validate_powermetrics_fiducial.py:628-646`. For v3, use the shared authenticated estimator, which re-derives the clock anchor, pulse schedule, raw trace, and effective bound: `joulewise/powermetrics_fiducial.py:931-944,951-1085,1088-1164`.

After artifacts exist, this read-only command prints declared, fresh, and effective `b_fiducial` values for every bundle:

```sh
env PYTHONPATH=/Users/edr/code/JouleWise /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'
import json
from pathlib import Path
from joulewise.powermetrics_fiducial import rederive_detection_from_artifacts

root = Path("/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation")
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    evidence = json.loads((d / "instrument_evidence.json").read_text())
    fresh = rederive_detection_from_artifacts(
        (d / "raw/powermetrics.plist").read_bytes(),
        (d / "events.jsonl").read_bytes(),
        evidence["clock_anchor"],
        protocol_id=evidence["protocol_id"],
    )
    declared = float(evidence["b_fiducial_s"])
    print(json.dumps({
        "dir": str(d),
        "declared_b_fiducial_s": declared,
        "fresh_b_fiducial_s": fresh.b_fiducial_s,
        "effective_b_fiducial_s": max(declared, float(fresh.b_fiducial_s)),
        "status": evidence["status"],
        "pulse_count": len(fresh.fits),
        "all_pulses_detected": fresh.all_pulses_detected,
        "reasons": fresh.reasons,
    }, sort_keys=True))
PY
```

No current `scripts/reissue_calibration_acceptance.py` exists in the inspected tree. The stored scalar alone is insufficient for fresh authentication; the production reducer re-derives from raw artifacts: `joulewise/reduce.py:1524-1579`.

### Fence checklist

- No other agent session, terminal workload, or monitoring process may run during QUIET-MAC capture: `scripts/validate_powermetrics_fiducial.py:19-26`; `docs/phase_2/window_runbook.md:22-24,400-402`.
- AC power, approved charger/cable, low-power mode off, thermal state nominal: `scripts/quiet_mac_prep.sh:12-15`; `configs/campaign_policies/quiet_mac_p2_production.json:15-27`.
- Displays asleep and screensaver disengaged; use transient display sleep only: `scripts/quiet_mac_prep.sh:85-126`; `docs/phase_2/window_runbook.md:41-48`.
- Allow at least ten untouched idle minutes before calibration: `docs/phase_2/window_runbook.md:387-394`.
- The prior contamination history makes screensaver/display state material: `docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:96-97`; the runbook records display wake/screensaver contamination: `docs/phase_2/window_runbook.md:353-361`.
- The 5 ms clock-anchor ceiling remains authoritative: `docs/phase_2/window_runbook.md:453-491`. Network-time disable is required by the armed quiet-window runbook, but the stabilization script itself says it is operational hygiene, not proof of the clock predicate: `docs/phase_2/window_runbook.md:568-611`; `scripts/quiet_window_clock.sh:1-27,95-127`. For this nonclaim shakedown it is optional only if the lead explicitly classifies the run outside the armed runbook; it remains recommended.
- Do not supply `--session-id`, `--slot`, or `--attempt-id`; do not reserve a D-117 bracket or write claim-run roots. A single calibration is explicitly usable only for nonclaim probe/exploratory reduction: `docs/contracts/powermetrics_fiducial.md:109-121`.

Skipping agent quiesce, display/saver controls, AC/thermal checks, raw artifact preservation, or clock-anchor validation would make the data unsuitable for the paper’s “instrument verified” narrative. Even clean shakedown values remain nonclaim evidence and must not be imported into the issued D-079 corpus; the ledger currently records the issued D-079 state and 19-member derivation corpus: `docs/contracts/calibration_ledger.md:227-234`.

### Risk list

1. Current `RUN_STATE.md:3667-3683` blocks any quiet-machine task after the NOT-READY council verdict; the user’s license does not supersede that repository gate without current clearance.

2. The canonical validator mutates calibration-ledger state. Pointing `--ledger` at a new file is not sufficient by itself because ordinary receipt append requires a committed matching head pin: `joulewise/calibration_ledger.py:5276-5313`. A separate committed shakedown ledger checkout or an explicit new nonclaim route is required.

3. An out-of-family calibration may return nonzero or systematic-invalid while still leaving useful diagnostic artifacts; do not rerun merely to obtain a passing value. The production gates and dispositions are defined at `scripts/validate_powermetrics_fiducial.py:1569-1638`.

4. The reported D-079 range is a comparison band, not a universal instrument guarantee. The estimator contract limits conclusions to the tested protocol and trace-anchor assumptions: `docs/contracts/powermetrics_fiducial.md:58-91`.