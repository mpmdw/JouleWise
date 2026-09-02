# MAGISTRATE RULING — T0-UNATTENDED-01 synthesis (Fable, 2026-08-23 night)

Two blind design seats (Sol xhigh, session 01a0317c…; Opus, agent
a7f0ec45…), one debate round each way, magistrate bench verification of
every load-bearing measurement. The seats CONVERGED after debate; no
disputed verdict remains, so no cold gate is triggered. This document is
the ONE home for the ruled design; the seat files and both critiques sit
beside it in this directory.

## Bench-verified facts the ruling rests on (all re-measured by the magistrate at HEAD)

1. `prior_network_time` is written (`arm_readiness_evidence_t0.py:879`) and
   never read — dead field. `prior_systemsetup_state_captured` is
   hard-coded `True` by the producer (`:877`) and required to be exactly
   `True` by the predicate (`arm_readiness.py:805`) — a tautology. The
   operator's privileged `systemsetup -getusingnetworktime` read therefore
   contributes no checked signal. **r4-6's "needs a D-127 privileged-scope
   change" premise is dead; the amendment is a scope CLOSURE.**
2. `CLOCK_ATTESTATION` already admits `PROBE` (`arm_readiness.py:731`).
3. Python `time.monotonic_ns()` on Darwin is `CLOCK_UPTIME_RAW` (measured
   delta 0.75 µs) and is sleep-blind: this machine shows 812,998 s
   (9.41 d) of RAW−UPTIME divergence, and the T-0 census requires
   `caffeinate` ABSENT (`arm_readiness_evidence_t0.py:1387`), so dwell-time
   sleep is live.
4. The governed anchor ceiling is 5 ms and the 2026-07-26 incident slewed
   at +110/−158 ppm (`quiet_window_clock.sh:5-9`). Worked replay: a summed
   0.5 s bound PASSES the incident-rate continuity (66 ms over 600 s); a
   separate 5 ms gate REFUSES it.
5. E-10 remains "Ed's deliberate physical launch"
   (`docs/phase_2/window_runbook.md:1113`, `:786-787`) and no launchd
   relaunch artifact exists in the repo.

## RULED DESIGN (adopted)

**Skeleton (Opus): single row, in-place source discrimination.** The
existing `clock.correct_and_prior_state.v1` row gains a `PROBE` branch;
the value dict of that branch does NOT contain
`prior_systemsetup_state_captured` (no claim → no false evidence); the
`OPERATOR_ATTESTATION` branch is byte-identical to today, so historical
and attended receipts authenticate unchanged. No registry change, no
evidence-kind change, no profile mode in the 15-row census module during
`_v4`. Sol's legibility concern (the fact id names a retired thing) is
ADOPTED AS CONCERN, DEFERRED AS CURE: the rename and any horizon change
batch into one post-`_v4` registry row, T0-CLOCK-ROW-RENAME-01, and the
two decisions are ruled COUPLED (revisit both together, never one alone).

**Reference (merged):** fixed versioned roster `time.apple.com`,
`pool.ntp.org`, `time.nist.gov` under Sol's `sample_policy_id` scheme; one
governed `/usr/bin/sntp -t 2` invocation per hostname (Opus's measured
5×-internal-retry correction), one attempt each, no runtime substitution
or fallback; quorum ≥2 successful legs; ALL successful parseable legs
enter an agreement-interval intersection (Sol's honest demotion from
"Marzullo" — Darwin sntp's ± is an estimate, not a certified bound); no
best-result selection; resolved peer address and raw line are
evidence-bearing for every leg. Two references: **R0 pre-pin** (before
network-time disable) and **R1 live at authoring**, with R1 ordered
BEFORE the author's fresh maintenance and process censuses (cures Sol's
probe-traffic objection mechanically); bound `|offset| + uncertainty ≤
0.5 s` per `quiet_window_clock.sh:30`.

**Falsifier (Opus, subsuming Sol's continuity term at Sol's own
retraction):** one `CLOCK_REALTIME − CLOCK_MONOTONIC_RAW` anchor delta
across the T-0 sequence (600 s ≤ span ≤ 3600 s), gated SEPARATELY at the
governed 5 ms — never summed into the 0.5 s bound. Clock is
`CLOCK_MONOTONIC_RAW` explicitly (sleep-immune); both samples same boot;
read skew ≤1 ms. No wall-vs-ordinary-monotonic term anywhere. The anchor
endpoints (`anchor_realtime_ns`/`anchor_monotonic_raw_ns`) are PUBLISHED
in the T-0 receipt value, and an **arm-side predicate re-samples the
anchor and refuses if it moved >5 ms since T-0** — this closes the
unbounded-step gap and is what makes the ruled 6 h horizon safe (drift by
arithmetic: 3.68 ppm × 6 h = 79.5 ms ≪ 500 ms; steps by mechanism).

**Horizon (ruled DISSOLVED, no number moves):** the two T-0 kinds keep
their D-150 item-2 code-stamped 6 h horizon exactly (Sol retracted its
1200 s proposal). SNTP recency is enforced at EVIDENCE ISSUANCE as
numeric predicate relations recomputed by `_predicate_passes` — never
another hard-coded boolean: R0→authoring span within [600 s, 3600 s] on
RAW anchors; R1 batch duration ≤30 s; R1-completion→validity-origin ≤5 s
(oldest participating R1 result ≤35 s old at issuance); receipt deadline
= validity origin + exactly 21_600_000_000_000 ns. **Standing fence:** any
consumption-time SNTP recency tighter than 6 h is a de-facto horizon
change and requires an Ed ruling — it must not travel as "predicate
recency."

**Horizon — AMENDED by cold gate 2026-08-28 (T26 item 3):** the 5 s issuance bound and the 35 s corollary are STRUCK; the retained relation is `0 ≤ (valid_until_monotonic_ns − 21_600_000_000_000) − r1_batch_finished_monotonic_ns ≤ 600_000_000_000` on the ordinary monotonic clock, a liveness bound, not a metrology bound — see `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md` item 3 and D-170.

**Enforcement postcondition (Sol):** double active
`systemsetup -setusingnetworktime off` with exit 0 AND exact-stdout-line
match — ADOPTED, GATED on Ed bench-verifying the exact
`setUsingNetworkTime: Off` string under sudo BEFORE it gates (a wrong
byte refuses every window forever).

**Rehearsal (merged 10-gate table, Sol's draft ruled in):**
noninteractive stdin (`/dev/null` everywhere, surviving prompt → loud
refusal); receipt/source census (zero OPERATOR_ATTESTATION, zero
operator-interactive argv, clock fact PROBE); local-input witness
(`HIDIdleTime` ≥ T-0 span, strict parse, absent output fails); clock
mechanics gates; D-149 C1–C5 mechanically green; rehearsal separation
(receipt class `T0_UNATTENDED_SUPERVISED_REHEARSAL`, `claim_eligible:
false`, rehearsal-prefixed window id, custody outside production);
production-side mechanical REJECTION of the valid rehearsal receipt as
part of acceptance; zero-agent capture; full lifecycle incl. backups and
restore; falsifier boundary controls (5 ms+1 ns refuses, 5 ms−1 ns
passes, plus the privileged positive control below). Any intervention
fails the rehearsal, even one that would have made it succeed. The
positive control runs OUTSIDE the T-0 sequence, at the bench adjacent to
the rehearsal window — explicitly not an intervention.

**Refusal vocabulary:** pre-implementation deliverable = an enumerated
delta against the closed refusal list (codes added; `clock_prior_state_
capture` retired; rehearsal coverage evidence per code) satisfying the
live `REASON_CODE_COVERAGE` gate (registry v1:240-242). New codes
register under the R1 family tables; nothing ships unregistered.

**Scope fence (both seats co-signed):** this row removes the T-0
*evidence* blocker only. The *launch* blocker — E-10's physical launch,
D-127 clause 4's relaunch harness and launchd fallback, none of which
exist in the repo — is a SEPARATE row, UNATTENDED-LAUNCH-01, registered
now, and production windows depend on BOTH rows. This row must not
silently absorb it.

## Ed-hands items (flagged, not blocking implementation start)

1. **D-127 sudoers install/exercise** — pre-existing, blocks every window
   regardless of this design (BLOCKING for windows, not for build).
2. **~2 min privileged anchor positive control** during the supervised
   rehearsal sitting (closes the detector-inertness risk; would have
   caught the sleep-blind clock in one wake cycle).
3. **Ratification:** D-127.1 (scope closure — retire the operator
   `-getusingnetworktime` read; NO new privileged command) and the ruled
   6 h retention.
4. **Exact-Off string bench verification** under sudo before the
   strengthened postcondition gates.

## Dissents recorded

None surviving. Sol retracted its continuity term and horizon proposal
with grounds; Opus conceded R1 ordering and reversed its own anchor-
publication deferral. The seats' residual stylistic differences (e.g.
±395 ns described as an observed five-sample range, never a "noise
floor") are carried into the implementation brief as accuracy notes.

## Work orders emitted

- T0-UNATTENDED-01 (existing row): implement per this ruling (Sol,
  enforced WRITE_SCOPE, full gauntlet; REASON_CODE delta is the first
  deliverable of the round, before code).
- UNATTENDED-LAUNCH-01 (new row): launch/relaunch harness per D-127
  clause 4 + E-10 runbook amendment; design round required; windows
  depend on it.
- T0-CLOCK-ROW-RENAME-01 (new row, post-`_v4` gated): the coupled
  rename + any horizon successor, one registry churn.
