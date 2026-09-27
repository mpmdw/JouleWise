# S0 NEEDS_RULING F1: which fields give the bundle's measured span (magistrate gap-fill, activation 6bec2aa6)

**Question (S0 seat, report 10 F1).** Final texts v1.1 text 2(f) compares `pre.monotonic_after_ns` and `post.monotonic_before_ns` against a span given in the probe's monotonic-nanosecond domain. Bundle stage events in `events.jsonl` record only wall-time `timestamp_s`. The ruled texts name no field for the bundle span and no conversion.

**Decision: option (a), the seat's recommendation.** The span comes from monotonic bounds that the controller records in `events.jsonl`. There is no wall-to-monotonic conversion.

1. **S1 (controller) must write** `metadata.monotonic_ns = time.monotonic_ns()` on two events:
   - the `idle_baseline` stage-**start** event;
   - the `idle_drift_sentinel` stage-**end** event.

   `time.monotonic_ns()` is the clock that `battery_float.observe` stamps. S1 edits no other event.
2. **`authenticate_bundle(bundle_path)`** (S0) derives `span = (start, end)`:
   - `start` is the `metadata.monotonic_ns` of the FIRST `idle_baseline` stage-start event;
   - `end` is that of the LAST `idle_drift_sentinel` stage-end event.

   It passes `span` to `authenticate_pair`. If either event, or either field, is absent or not a non-negative int, or if end < start, the verdict is `battery_float_evidence_missing` with reason `bundle span unavailable`. This applies at the span rung only, after every earlier rung (text 2 order).
3. **Pair ownership follows text 7.** A bundle whose `events.jsonl` has no `idle_baseline` start owes no pair. That case is `not_reached`, which the reader handles under text 8. `authenticate_bundle` is then not asked to judge a span.
4. **Why not a conversion.** Converting wall time to monotonic reintroduces the clock-anchoring hazard that the monotonic check exists to avoid: the wall clock can step during a run. Event metadata is written by the same process as the probe records, so it adds no new trust assumption.
5. **Authority.** This fills a gap and does not amend the ruled text. It is flagged explicitly to the S0 and S1 cold Fable final passes, and any disagreement goes to a cold gate.
