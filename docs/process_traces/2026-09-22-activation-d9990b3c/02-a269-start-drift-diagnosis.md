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


## Addendum (dated; the text above is unchanged)

Addendum 2026-09-22 (A269 cold gate 10, packet b7c37d6d…): on night qpe01-pilot-n1-20260922-0217 the `start_drift` exclusion (envelopes 03/06/09, chain-level 10.11/10.06/9.95 s, session-level 10.23/10.18/10.06 s) removed no envelope not already excluded for `incomplete_interior_support` (03, 06, 09) and `clock_anchor_unresolved` (03, 09); envelopes excluded for `start_drift` alone: none (evidence/summary.json sha256 9121f080…3d04). The as-observed claim that `start_drift` removed 03/06/09 is withdrawn. A269's p1 standing rests on the forward argument: with A267's two exclusion classes cured, `start_drift` alone would leave 9 retained envelopes and 3 disjoint pairs against `minimum_adjacent_pairs: 4`.

Correction 2026-09-22 07:50 PDT (activation e4b4ead6, executed at the bench on the A267 seat head 447fd6bf, file 16b): the forward figure "9 retained / 3 pairs" above assumed A267 cures EVERY clock_anchor_unresolved exclusion. It does not, and must not: replaying the twelve 09-22 fixtures through derive_powermetrics_anchor_v3 under CLOCK_METHOD_V3_1 bounds envelopes 02, 05, 06, 08, 09, 11, 12 (seven) and still refuses 01, 03, 04, 10 (affine_clock_fit_empty: an adjtime slew inside the capture) and 07 (wall_minus_monotonic_span_exceeded: 22.36 ms against the 15 ms backstop). On the 09-22 data the post-A267 set is therefore 7 retained / 3 disjoint pairs ((5,6), (8,9), (11,12)), which start_drift (03, 06, 09) cuts to 5 retained / 1 pair — the figure ruling 14 R6's parenthetical "(5 retained / 1 pair against 8 / 4)" carried, which is thus CORRECT as a forward projection on this night's data and is NOT withdrawn. The "9 retained / 3 pairs" figure is the forward projection for a RE-RUN under the A267 chain (network time OFF, no slews, exact tiling), where start_drift alone would cut 12 to 9 and pairs to 3. Both projections sustain the p1 standing (start_drift costs 2 envelopes and 2 pairs on the observed data; 3 envelopes and 3 pairs on a clean re-run). The withdrawn claim remains only the AS-OBSERVED one: no envelope on 09-22 was excluded for start_drift alone.
