```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Six-file fact packet assembled; ten source citations spot-checked.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "687f022b044073587afd1546deecd8f21dde8432",
    "head_end": "687f022b044073587afd1546deecd8f21dde8432",
    "upstream_end": null,
    "branch": "docs/2026-09-24-278ebc9e-packets2"
  },
  "pathspec": [
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/00-question.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/01-cadence-facts.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/02-acceptance-rules.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/04-options.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/05-open-facts.md"
  ],
  "unowned_dirty": [],
  "verdict": {"rows": []},
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "wc -l docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/*.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["131 total"]},
      "expected": {"exit_code": 0, "tail_regex": "131 total"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## docs/2026-09-24-278ebc9e-packets2", "?? docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/"]},
      "expected": {"exit_code": 0, "tail_regex": "22-acceptance-council-packet/"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Archived native intervals establish the cadence change but do not isolate sampler-binary causation from OS scheduling or sampler work.",
      "needs": ""
    }
  ]
}
```

## Packet files

[00-question.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/00-question.md)

- States the council question without taking a position.
- Defines the acceptance and identity epoch.
- Defines the main lane and artifact IDs.
- Records r7’s 25F84 binding.
- Records Ed’s ruling that neither equivalence night counts.

[01-cadence-facts.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/01-cadence-facts.md)

- Gives r6 and 25G83 sampler hashes and the common 100 ms request.
- Lists raw interval medians and frame counts for all 24 September 19 slots.
- Inventories the September 20–23 pilot cadence evidence.
- Separates the anchor estimator change from the native interval change.
- Identifies what archived records can answer and what requires a quiet, sudo-enabled run.

[02-acceptance-rules.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/02-acceptance-rules.md)

- Defines the corpus inputs, timing bound, screens, and ceiling.
- Records the historical operative thresholds and their derivation.
- Identifies epoch, preflight, drift, and bracket refusals.
- Explains the new maximum, range, SD, and Q99 calculations.
- Quantifies why a doubled sample interval does not mechanically double the ~1 J or ~5 J figures.

[03-evidence-inventory.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md)

- Lists all 24 September 19 capture dispositions and reasons.
- Lists each September 20–23 pilot’s retained envelopes.
- Separates pilot envelopes from 59-pulse calibration captures.
- Records the 11/24 valid capture count as diagnostic evidence.
- States the prospective membership and already-seen-data boundary.

[04-options.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/04-options.md)

- Covers cadence restoration and observed-cadence characterization.
- Covers prospective rule amendment and an uncalibrated diagnostic night.
- Includes a combined path using the KM003C as a separately labelled reference.
- Separates quiet-window, calendar-day, and desk-work costs.
- States each path’s evidentiary limits and possible unblock.

[05-open-facts.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/05-open-facts.md)

- Lists the remaining causal and yield questions.
- Flags the need to reconcile ruled-out captures in the ledger prior set.
- Separates unknown successor thresholds from historical figures.
- Records the diagnostic night’s unfinished registration and payload.
- Contains ten `sed -n` citation spot-check commands and excerpts.

## Spot-check tails

All ten `sed -n` commands in [05-open-facts.md](/Users/edr/code/wt-278ebc9e-packets2/docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/05-open-facts.md) exited 0. Their checked excerpts were:

1. `“os_build”: “25F84”`; `“sampling_interval_ms”: 100`.
2. `Three agent-free [QUIET-MAC] windows on distinct calendar days`.
3. `Retained n >= 19 is REQUIRED`; `No top-ups, retries, early stops, or outcome-driven extra nights.`
4. `If two or more retained members exceed 0.032898493715362, the corpus is not issued and Ed rules in`.
5. `d01, d03, d05, d07, d09, d11, d12 valid`; five `ordinary-invalid`.
6. `neither night counts toward the three-night derivation`; `resolve the instrument`.
7. `d01|871|110.4/244.3/274.0/284.5`; `d05|855|113.4/247.7/274.2/299.1`.
8. `2,535 frames in 600 s`; `interval of ~237 ms`.
9. `identity_epoch not in judged_epochs`; `acceptance_artifact_epoch_mismatch`.
10. `allowance = max(drift_decimal, screen)`; `operative_bound = endpoint_max_decimal + allowance`.

The six files are uncommitted, all inside the specified write scope, and each is under 250 lines.