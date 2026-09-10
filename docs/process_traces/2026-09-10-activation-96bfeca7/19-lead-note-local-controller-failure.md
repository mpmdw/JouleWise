# Lead note — `test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce` fails locally at main, CI green (2026-09-10 ~05:40 PDT)

Observed: `python3 -m unittest tests.test_controller` on a clean worktree at main `078a13a4` on this Mac → 73 tests,
1 failure (strict reasons `idle_drift does not match pre/post raw sentinel derivation`, `idle_drift_bound_w does not
match effective drift derivation`). GitHub CI at `078a13a4` (run 2026-09-10T11:14Z): success. Independent of the
GATE-SENSIBILITY-SWEEP-01 diff (seat 08 reproduced it with the four modules restored to HEAD bytes).

Root cause (report 19, Astra high, `verdict.cause: probable`): the controller fixture still sleeps through its post-idle
capture against a real deadline (the sleeping-sentinel timeout class cured for the campaign-test helper in PR #310, consult
87), so on a loaded or slow host the capture times out, the drift is unknown, salvaged raw samples remain, and strict
validation derives a bounded drift the producer did not record. Bench-timing dependent; CI runners are not loaded the same
way. F2: a REAL timed-out capture with enough salvaged samples can reach the same producer/validator disagreement, which is
a timeout outcome, not a false refusal of a healthy complete bundle; no existing member is invalidated by this.

Disposition (magistrate): not on the G2-a path; CI is the gate of record for the sweep PR; the local full replay at
8da99190 is read with this ONE known local-only failure allowed and named in the evidence. Signature note: this is the third
instance of the host-timing-dependent fixture class (87, 99, 19). Rule 11's standing escalation trigger concerns fix rounds
on the same defect; this is a pre-existing flaky fixture, registered as a follow-up lane for a Sol/Astra fixture cure
(pace the fixture like the campaign-test helper; add the deterministic timeout counterfactual) — FIXTURE-SENTINEL-CONTROLLER-01,
to be added to the kernel by the next bookkeeping seat, not fixed inside this activation.
