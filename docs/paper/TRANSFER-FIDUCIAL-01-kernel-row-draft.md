# Draft kernel row — `TRANSFER-FIDUCIAL-01`

**Status: a DRAFT FOR THE MAGISTRATE TO REGISTER. It is not the kernel.**
The paper director does not edit `docs/process/state_kernel.json`; this file carries
the proposed row in that file's own shape, ready to paste under `tasks/`.

Authority: `docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md`
item 16 (with item 5, which item 16 supersedes on the SHAPE of the measurement).

## Why this row exists

Ruling item 5 registers the pulse-to-inference **load-regime transfer assumption** as
limitation #1: the phase-edge timing bound is characterized under the calibration
regime — commanded GPU pulses under light CPU load — and then transported to sustained
mixed inference load. Nothing in the frozen `_v4` pack tests that transport.

Ruling item 16 rules that the **inserted-gap fiducial arm** is the cheapest closure and
is better-shaped than item 5's generic "workload-shaped calibration", because it places
a fiducial edge *inside a real workload* rather than reproducing a synthetic one:

> a commanded ~500 ms sleep between prefill end and decode start on ~10 real-workload
> runs, edges fitted with the existing pulse estimator, residual compared to the
> pulse-derived bound

It does **NOT** enter `_v4`: the pack is frozen and any non-config change is a new
family generation. It is Future Work #1 in the paper and a queued row here, for the
first post-campaign diagnostic window.

## Proposed row (paste under `tasks/`)

```json
"TRANSFER-FIDUCIAL-01": {
  "acceptance": {
    "evidence": [
      "A diagnostic capture exists in which a commanded gap of approximately 500 ms separates prefill end from decode start on approximately 10 real-workload runs",
      "Both gap edges are fitted with the EXISTING pulse estimator, unmodified, and the estimator revision in force is named in the capture record",
      "The fitted-edge residual is compared against the pulse-derived timing bound in force for that session, and the comparison is recorded with both magnitudes",
      "The capture is labelled diagnostic and non-claim-bearing: it tests the transfer assumption and mints no floor and no claim"
    ],
    "pointer": {
      "json_pointer": "/tasks/TRANSFER-FIDUCIAL-01/acceptance",
      "label": "TRANSFER-FIDUCIAL-01 acceptance",
      "path": "docs/process/state_kernel.json"
    },
    "summary": "An inserted-gap fiducial arm measures phase-edge displacement inside a real inference workload and compares it with the pulse-derived bound."
  },
  "authority": {
    "label": "T26 paper-goal magistrate ruling, item 16 (with item 5)",
    "path": "docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md"
  },
  "dependencies": [
    {
      "evidence": null,
      "kind": "task",
      "required": "the frozen _v4 campaign completes; this row runs in the FIRST POST-CAMPAIGN diagnostic window and must not enter or perturb _v4",
      "scope": "start",
      "state": "pending",
      "strength": "hard",
      "target": "V4-TRANSACTION-01"
    }
  ],
  "fallback": null,
  "fences": [
    {
      "authority": {
        "anchor": "rulings",
        "label": "T26 paper-goal ruling item 16 (does not enter _v4; the pack is frozen)",
        "path": "docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md"
      },
      "rule": "Must not enter or perturb the _v4 pack. The pack is frozen and any non-config change is a new family generation; this row runs only in a post-campaign diagnostic window."
    },
    {
      "authority": {
        "anchor": "rulings",
        "label": "T26 paper-goal ruling item 16 (transfer is left untested by _v4; this arm tests it diagnostically)",
        "path": "docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md"
      },
      "rule": "Diagnostic and non-claim-bearing. Mints no floor, licenses no claim, and does not re-scope any issued floor or any published label."
    },
    {
      "authority": {
        "anchor": "rulings",
        "label": "T26 paper-goal ruling item 16 (edges fitted with the existing pulse estimator)",
        "path": "docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md"
      },
      "rule": "Uses the EXISTING pulse estimator unmodified, and the estimator revision in force is recorded with the capture. A changed estimator makes this a different measurement and voids the comparison."
    }
  ],
  "flags": [],
  "goal": "Close the pulse-to-inference load-regime transfer assumption (paper limitation #1) by fitting a commanded ~500 ms inter-phase gap on ~10 real-workload runs with the existing pulse estimator and comparing the residual with the pulse-derived bound.",
  "id": "TRANSFER-FIDUCIAL-01",
  "lane": "quiet_mac",
  "priority": "p2_next_slice",
  "rank": 0,
  "status": "queued",
  "status_note": "Ruled Future Work #1 by the T26 paper-goal ruling item 16; queued for the first post-campaign diagnostic window. Ed-hands (hardware window).",
  "stop_card": null
}
```

## Fields the magistrate must set, which the director deliberately did not

- **`rank`** — set to `0` ONLY as a schema-valid placeholder: `docs/process/state_kernel.schema.json`
  requires `rank` to be an integer, so `null` would not validate. Ranking against the other
  live rows is a queue-ordering judgment the director does not own — **replace `0` before
  registering.**
- **`priority`** — set to `"p2_next_slice"`. The director enumerated the kernel's live
  priority values (`p1_phase_gate`, `p2_next_slice`, `p3_hardening_candidates`,
  `p3_research_expansion`, `p3_tooling`, `p4_polish`) and picked the only one that fits a
  queued post-campaign measurement; `p3_research_expansion` is the defensible alternative
  if the magistrate reads this as expansion rather than next slice. No new literal was minted.
- **`lane`** — set to `"quiet_mac"`, not `"agent"`: this row is a measurement on Ed's
  machine under quiet-state conditions, so it belongs in the hardware-window lane
  (`quiet_mac`, 11 live rows) rather than the agent lane.
- **`dependencies[0].target`** — `V4-TRANSACTION-01` is named because ruling item 16
  sequences this row behind the campaign. Confirm that is the row that closes the
  campaign, rather than a successor row.

## What the paper says about this row

Per item 16, the paper WILL say plainly that `_v4` leaves transfer untested, and WILL name this
arm — in concrete form, not as a generic "future calibration work" — as Future Work #1.
That sentence is a round-2 edit under order (2) of the ruling's director orders, which
opens §7 with the load-regime transfer limitation.
