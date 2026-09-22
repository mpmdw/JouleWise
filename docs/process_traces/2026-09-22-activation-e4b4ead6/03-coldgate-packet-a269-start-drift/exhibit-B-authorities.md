# Exhibit B — controlling authorities (verbatim extracts at main `ecbc0fac`)

## B1 — `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json` (complete file; its sha256 is printed in exhibit C1; this is the byte-pinned registration that `night_gate.QPE01_PILOT_REGISTRATION_SHA256` checks — exhibit A, `frozen_protocol`)

```json
{
  "block_two": {
    "authored_after_pilot": true,
    "contrast": "idle-load-idle bracket",
    "levels": [
      0,
      0.05
    ],
    "one_profile": true,
    "one_qos": true,
    "smallest_holdable_share": 0.05,
    "upper_bound": "one-sided 95% paired-contrast upper bound"
  },
  "busy_cores_role": "covariate_only",
  "cadence_exclusion": "start_drift: absolute collector start drift greater than 10 s from the frozen schedule",
  "chain_source_sha256": "568a2771b28da9d805cd23ff4059bbbc27d6dfad1f8d9603331a412e3751b7ea",
  "envelope_s": 600,
  "envelopes": 12,
  "exclusions": [
    "census_not_clean_or_unknown",
    "ac_not_AC_Power_or_probe_error",
    "CPU_Speed_Limit_below_100_or_thermal_probe_error",
    "clock_anchor_unresolved",
    "incomplete_interior_support",
    "collect_error",
    "cleanup_unproven",
    "start_drift"
  ],
  "interior_offset_s": 60,
  "interior_s": 480,
  "load_generator": false,
  "minimum_adjacent_pairs": 4,
  "minimum_retained": 8,
  "pairing_rule": "disjoint_original_adjacent_pairs_both_retained_no_bridging",
  "power_interval_ms": 100,
  "receipt_class": "DIAGNOSTIC_NO_PACK",
  "recorder_journal": "evidence_busy_cores.jsonl",
  "ruling": "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b",
  "sample_interval_s": 30,
  "schema": "joulewise.quiet_predicate_pilot.v1",
  "settle_s": 600,
  "sizing": {
    "assumption": "independent normally distributed disjoint pair differences",
    "chi_square_lower_tail_probability": 0.1,
    "confidence": 0.9,
    "delta_j": 1,
    "formula": "max(3, ceil(8 * s_upper**2 / delta_j**2))",
    "maximum_pairs": 24,
    "minimum_pairs": 3,
    "multiplier": 8,
    "reference_factors": {
      "n_4": 2.266,
      "n_6": 1.762
    },
    "s_pair": "sample SD of retained disjoint differences, df = n - 1",
    "s_upper": "s_pair * sqrt((n - 1) / chi_square_quantile(0.10, n - 1))"
  },
  "start_drift_max_s": 10,
  "stop_branches": {
    "block_two_upper_bound_above_1_J": "no cutoff qualifies",
    "observer_floor_above_smallest_holdable_share": "no cutoff qualifies",
    "sized_pairs_above_24": "no cutoff qualifies"
  },
  "summary": [
    "interior rail-sum and combined joules",
    "retained disjoint pairs (e1,e2), (e3,e4), ..., (e11,e12); even minus odd interior joules; sample SD and upper 90% bound",
    "overlapping adjacent differences and SD, maximum absolute difference: diagnostics only, never sizing",
    "all single-envelope values and SD, first-to-last retained drift: diagnostics only, never sizing",
    "name every overlapping original adjacent pair with absolute difference above 3 * s_pair; diagnostic only; never exclude by magnitude",
    "whole-round observer cpu-s, self plus reaped children including recorder; never subtracted",
    "recorder journal joined by monotonic support: per-envelope busy-core median/max and clean-machine distribution; covariates only",
    "cadence and native sample counts",
    "boot_id, os_build, sw_vers, powermetrics identity",
    "all named exclusions; partial observations retained; PROVISIONAL, no cutoff authority"
  ],
  "top_up": false,
  "window_max_s": 9000
}
```

## B2 — sealed cold-gate rebuttal ruling 14 (A267, sha256 507c33cb… per its SEALED-SHA256SUMS), sections R4 and R6 verbatim (`git show ecbc0fac:docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/14-coldgate-fable-rebuttal-ruling.md | sed -n '121,123p;129,131p'`)

```
```

## B3 — sealed A267 refuter 11 (sha256 85f0437d…), every line mentioning start_drift (`git show ecbc0fac:docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/11-opus-contract-refuter.md | grep -n start_drift`)

```
172:protocol's own `start_drift_max_s: 10` (A20) removes 06 (10.18 s) and 09 (10.06 s)
206:  but the prose names only envelopes 03 and 06 as `start_drift` while C1's own
226:against 8 and 4**, because `start_drift` independently removes envelopes 03, 06 and
```

## B4 — kernel entry for A269 at ecbc0fac (first object in `docs/process/state_kernel.json` whose string values mention A269 / ENVELOPE-START-DRIFT, `json.dumps`)

```json
{
 "label": "T38t \u2014 2026-09-22: pilot night qpe01-pilot-n1-20260922-0217 harvested (GO, INCONCLUSIVE 2/12; seven clock-anchor refusals traced to timed slews against the v3 anchor's 5 ms absolute caps); agents uninstalled; A267\u2013A269 registered",
 "path": "docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md"
}
```

## B5 — the previous magistrate activation's A269 diagnosis record 02 (LABELED ARGUMENT, not evidence; its table is reproduced independently in exhibit C2; `git show ecbc0fac:docs/process_traces/2026-09-22-activation-d9990b3c/02-a269-start-drift-diagnosis.md`, complete file)

```
# 02 — ENVELOPE-START-DRIFT-01 (A269): the cause of the 7.6–10.2 s collector start drift, from primary evidence

Magistrate (activation d9990b3c), 2026-09-22 ~06:05 PDT, read-only over the harvest archive `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922` (byte-exact copy of the night root; SHA256SUMS 15801 OK) and the code at main `9b6b3f0e`. Executed at the bench; no seat. Promoted to the critical path by the A267 cold gate's refuter (record 01, file 11, BLOCKER 3): the pilot protocol's own `start_drift_max_s: 10` exclusion removed envelopes 03, 06 and 09 (drifts 10.23, 10.18, 10.06 s), so no re-run can reach the eight-envelope floor while the drift sits at 78–102 % of its budget.

## Mechanism (code)

`quiet_predicate_campaign.execute` (`joulewise/quiet_predicate_campaign.py:477–500`) schedules envelope *i* at `first + (i−1) × envelope_s`, sleeps until that instant, spawns the collector, **waits for the collector to exit**, runs `cleanup_groups` (30 s budget), and only then loops to the next slot. The collector (`scripts/sample_quiet_predicate_evidence.py collect`) anchors its sampling to `--envelope-start-mono-s` and stops at `scheduled + 600` regardless of its own spawn time (`deadline_mono_s = scheduled + envelope_s`; every envelope's `sampling_stopped − scheduled` = 600.08–600.15 s). Everything the collector does after `sampling_stopped` is therefore on the critical path of the NEXT slot: `PowerRecorder.finish` (`:640–668`) waits for the recorder to exit, reads and parses the ~130 MB plist (`parse_frames`), stamps `post_parse`, derives the anchor (`align_frames` → `derive_powermetrics_anchor_v3`, an exact-rational LP), integrates every round and the interior, hashes every raw file, writes `rounds.jsonl` and `session.json`; then the chain's `cleanup_groups` reaps the collector's groups and the next `Popen` starts. The drift does not accumulate because sampling ends at the scheduled instant; it is a per-slot constant equal to the serial finalisation time.

## Measured decomposition (monotonic clock stamps in each `session.json`; `evidence_envelopes.jsonl` for `scheduled_mono_s`)

| envelope | start drift s | sampling_stopped − scheduled | post_parse − sampling_stopped (recorder exit wait + plist parse) | end_stamp − post_parse (derive + integrate + hash + write) | next pre_spawn − end_stamp (exit + chain cleanup + spawn) | anchor |
|---|---|---|---|---|---|---|
| 01 | 0.16 | 600.15 | 4.98 | 0.01 | — | unresolved |
| 02 | 7.89 | 600.15 | 4.94 | 2.12 | 2.87 | bounded |
| 03 | 10.11 | 600.08 | 4.88 | 0.07 | 3.02 | unresolved |
| 04 | 7.70 | 600.15 | 4.85 | 0.11 | 2.78 | unresolved |
| 05 | 7.78 | 600.14 | 4.97 | 2.13 | 2.79 | bounded |
| 06 | 10.06 | 600.15 | 4.89 | 1.55 | 2.93 | bounded |
| 07 | 9.42 | 600.15 | 4.91 | 0.01 | 2.94 | unresolved |
| 08 | 7.63 | 600.15 | 5.01 | 2.29 | 2.67 | unresolved (post-fit) |
| 09 | 9.95 | 600.15 | 5.07 | 1.34 | 2.61 | unresolved (post-fit) |
| 10 | 9.12 | 600.15 | 4.90 | 0.01 | 2.68 | unresolved |
| 11 | 7.73 | 600.15 | 4.90 | 1.70 | 2.79 | bounded |
| 12 | 9.49 | 600.15 | 5.02 | 1.70 | 2.85 | bounded |

Envelope 1's 0.16 s is the settle path (no predecessor). Reading: drift ≈ 0.15 (stop lag) + ~4.9 (recorder exit wait + 130 MB parse; the bench probe in record 01 file 12 measured `parse_frames` + derive at 5.3–7.8 s per plist, so parse dominates) + 0–2.3 (anchor derivation and integration, present only when the fit runs to completion — this is the bimodality) + ~2.8 (collector exit, `cleanup_groups` census loop over the process journal, `Popen`). The recorder itself exited cleanly on TERM in every envelope (`power.cleanup.returncode 0`, `kill false`), so the 5 s kill timer is not the cost.

A single 600 s envelope therefore costs about 608–610 s of serial wall time against a 600 s slot pitch, and the protocol's 10 s drift exclusion sits inside the noise of that overrun. The 60 s interior offset absorbs the drift for the measurement itself (the interior is placed from the frozen schedule, `interior_epoch = start.epoch_s − start_drift_s + interior_offset_s`), so the excluded envelopes were not mis-measured; they were excluded by a cadence rule whose budget the harness cannot meet.

## Candidate cures (for the implementation brief; none chosen here)

1. **Capture-only collector, batch finalisation after the last envelope.** The collector exits right after `sampling_stopped` with the raw plist, stamps and rounds journal on disk; parse, anchor derivation, integration and hashing run once, after envelope 12, by the chain (or by `pilot_summary`). Removes ~7 s per slot; keeps every envelope's window free of the observer's parse CPU; the derivation is deterministic from the raw bytes and stamps already recorded. Changes the collector's output contract (session.json written in two stages) and the summary's inputs.
2. **Slot pitch larger than the capture** (`slot_pitch_s` = 615–620 s with `envelope_s` 600): a change to the pre-registered protocol (`pilot_protocol_v1.json` pins `envelope_s` as both), so it needs a protocol re-registration ruling; window budget allows it (600 + 12 × 620 = 8040 s < 9000 s).
3. **Re-size the drift budget** (`start_drift_max_s` 10 → 20): also a protocol re-registration, and it leaves the harness overrunning its own schedule.

Cure 1 is a harness change under the twelve-row gate; cures 2 and 3 are registration changes. Under the sensible-gates rule the exclusion should be sized to what it protects (interior placement, absorbed by the 60 s offset), which argues for cure 1 with the exclusion left as is.
```

