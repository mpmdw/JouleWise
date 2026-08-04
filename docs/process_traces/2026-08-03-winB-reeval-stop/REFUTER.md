# CONTRACT-LENS REFUTER REPORT — window B re-evaluation STOP
(Opus contract refuter, fresh context; delivered 2026-08-03 night.
Verbatim findings; sanity check: reproduced the operator's exact
refusal string from primary code and bytes, then falsified by removal.)

## F1 — Sole cause proven: mtadd-p2048o0128-r06. Classification (i). [BLOCKER-grade certainty]
Real policy, real 70-bundle set, salvage semantics: ready=False,
refusal_reasons=('clock_anchor_unresolved','environment_admission_missing'),
bracket b_fiducial_s 0.0350400833260715. Falsification — identical run
with r06 removed: 69 bundles, ready=True, zero refusals, 69/69
provenance. r06's own bytes carry clock_anchor_bound_s null and both
reasons at every window class. A stored-summary scan across all 70
found the two reasons in EXACTLY one bundle. Mechanism
(whole_window.py:594-599): reasons come from
_classify_precheck_refusals(operative_summary), promoted global because
neither is in _METRIC_LOCAL_PRECHECK_REASONS (whole_window.py:141-157).
r06's third reason clock_bound_unrecorded IS allowlisted and stays
local — why exactly two surfaced. Machinery behaving as designed.

## F2 — Not corpus drift, not tightened policy [HIGH]
The producing bytes are byte-identical to the original evaluation
inputs (210 files + 4 bracket files, mismatch 0). The reasons were
minted 2026-08-01 and simply never LOOKED AT: the original row ran
under d078_minted_envelopes_v1 and run_campaign.py:5175-5182 constructs
a consumption session only for max-bracket/salvage — no session
existed, _prepare never ran. Cleanly discriminates window B from the
same-night a10/window_c tightened-policy observations.

## F3 — Hypothesis (ii) refuted; its stated mechanism factually wrong [HIGH]
(1) The contract defines this: D-100 addendum (decision_log.md:6267-
6269) — salvage semantic = COMPOUND authenticated max-bracket survivor
consumption + exactly one exclusion. (2) The consumer demands it:
whole_window.py:3630-3637 rejects rows not stamped max-bracket; the
_prepare stamp (whole_window.py:645-648) is required, not a leak.
(3) The named mechanism did not fire: calibration_bracket_for_bundles
returned ZERO reasons, b_fiducial_s bit-identical to the recorded post
bracket. Packet also mis-identifies the bundle class (posits nulls; the
driver is an additivity bundle with status succeeded).

## F4 — Material omission: the NEG-8 bound expired 2026-08-02 [HIGH]
derived_at_s=1785576128.913 + max_age_s=86400 -> expired
2026-08-02T09:22:08Z. Probe: decision stale, triggers
[validity_horizon_expired]; AS-OF 2026-08-01T14:20Z -> fresh. Horizon
compared against live wall clock (whole_window.py:983-992, 1073-1077,
1604-1608). Consequence: even with consumption repaired, the commanded
run would have re-emitted neg8_drift_bound_stale and FAILED. The packet
marks conditions 1-7 done and presents consumption as the sole blocker
without noting the license had become unable to PASS a day before
D-108 unblocked it. Partially answers the packet's question (iii); the
packet had the artifact path in hand.

## F5 — No licensed path to remove r06: refusal is TERMINAL [HIGH]
Salvage exclusion applies only to terminal_absent bundles
(run_campaign.py:4799,4818); r06 present, succeeded. D-100 §2(d) caps
exclusions at ONE; D-108 cl.2 fixes the target as r08. --waivers is
FORBIDDEN under salvage (run_campaign.py:788-789). Combined with F4:
no executable path to a PASS under the current license.

## F6 — D-100's "pure cascade" falsified for one condition [HIGH]
Probe over the core-verdict site (current_environment_refusals, the
producer of the original row's condition, whole_window.py:3317-3330):
exactly one bundle with core-verdict environment refusals — r06,
['environment_admission_missing']. The original FAILED row's condition
traces to r06 alone — never a cascade condition; a standing per-bundle
defect no exclusion or membership repair can cure. (r06 metadata:
decision admitted on attempt 2 after attempt 1 failed
cpu_busy_ratio_p95_exceeded at 0.6136 > 0.5.) The packet's neutral
checkbox framing is the selective framing this gate was warned about.

## F7 — The real contract question: scope, not dispatch [MEDIUM-HIGH]
_fail_global (whole_window.py:404-416) voids the entire window's
consumption on one bundle's global refusal. r06 belongs to the
p2048-o0128 shape D-100 §3 already ruled barred regardless (frozen
min_n 8, 7 present). A member of an independently-barred cell is
voiding the six additivity cells and both null rungs D-100 §3 called
the real stake. Whether D-100 licensed window-scope voiding by an
out-of-stake member is a genuine open question — a SCOPE question in
the membership->consumption handoff. The global/local split is
deliberate; the question is whether that design was ratified for THIS
use.

## Packet accuracy audit
Verified true: 120 log lines; tail row timestamp/status; no row
appended; five original conditions verbatim; refusal site; clause-(d)
re-record byte-identical to the banked copy (both 4eb06ee9...f5); 3
subjects licensed true, 22 files each; frozen corpus 210+4/0; operator
flags valid; waivers correctly absent; naive-probe disclosure honest.
Wrong or selectively framed: the cascade bullet (F6); the omitted
expired bound (F4); hypothesis (ii)'s mechanism and bundle class (F3).

## Lean and strongest counter
Lean (i) with the amendment that the condition is TERMINAL. Strongest
counter: D-100 §3 carved p2048-o0128 out of the stake; admitting a
barred-cell member as gating survivor is arguably a (ii)-class defect
in the membership->consumption handoff. Rebuttal: _prepare
authenticates the INCLUDED set; cell-level bars apply downstream; no
code path or clause removes barred-cell members from membership. Absent
a ruling, (i) is correct — but the gate should rule F7 explicitly.

## What the gate must NOT conclude
1. Not that repairing consumption unblocks a PASS (F4 independent).
2. Not tightened-policy by analogy (F2).
3. Not a repair row (a "fix" = weakening the allowlist = doctrine
   change).
4. Not that r06 can be excluded (F5).
5. Not any reinterpretation of the original FAILED verdict.
6. Not that the machinery is defective because a barred-cell bundle
   drives the void (F7 needs a ruling, not an inference).
7. The 70-bundle included-set identity is inferred (from the runs root
   + the original row's bundle_ids/empty exclusions), not independently
   resolved — the one gap a follow-up should close. [CLOSED by the cold
   adjudicator's faithful probe: membership resolved 70 sources with
   empty selection conditions — magistrate note.]
