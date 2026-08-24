# T0-UNATTENDED-01 adjudication prep (magistrate bench notes)

## Opus seat delivered (t0-unattended-opus.md); Sol seat in flight (t0-unattended-sol.md)

## Bench verifications of Opus seat's load-bearing claims (2026-08-23 night, HEAD 75e5ae4)

1. VERIFIED: `prior_network_time` — single occurrence repo-wide, the WRITE at
   `joulewise/arm_readiness_evidence_t0.py:879`; zero readers. Dead field.
2. VERIFIED: `prior_systemsetup_state_captured` tautology — producer hard-codes
   `True` (`arm_readiness_evidence_t0.py:877`); the predicate content requirement
   for `clock.correct_and_prior_state.v1` demands exactly `True`
   (`arm_readiness.py:805`). The operator's pasted `systemsetup` output gates
   nothing beyond its own performance.
3. VERIFIED: `CLOCK_ATTESTATION` already admits `PROBE`
   (`arm_readiness.py:731`) — option-(b) hook pre-exists; no registry change.

Consequence if unrebutted by the Sol seat: r4-6's "privileged-scope (D-127)
change AND code change" premise is half-dead — the scope change is a CLOSURE
(retire the read), not an addition. Ed-hands items shrink to: sudoers
install/exercise (pre-existing D-127), one supervised rehearsal positive
control, ratification.

## Debate round — Opus critique received; bench verifications (2026-08-23 night)

4. VERIFIED: `time.monotonic_ns()` == CLOCK_UPTIME_RAW on this machine
   (0.75 µs delta); CLOCK_MONOTONIC_RAW − UPTIME_RAW = 812,998 s ≈ 9.41 d
   asleep since boot. Sol's continuity clock (monotonic_ns) is SLEEP-BLIND;
   Opus's defect-1 claim CONFIRMED.
5. VERIFIED: governed 5 ms anchor ceiling + the 2026-07-26 incident rates
   (+110 ppm / −158 ppm, adjtime) documented at quiet_window_clock.sh:5-9.
   Opus's worked replay (Sol summed 0.5 s bound PASSES 66 ms incident-rate
   continuity; separate 5 ms gate REFUSES) is arithmetically right.
6. VERIFIED: T-0 process census requires caffeinate ABSENT
   (arm_readiness_evidence_t0.py:1387 keep-awake probe -> _expect_absent
   :1393) — machine may sleep during the >=600 s dwell. Availability defect
   in any UPTIME_RAW-based span measurement stands.

Opus critique headline dispositions (tentative, pre-Sol-counter):
- 12 co-signed agreements incl. adopting Sol's sample_policy_id,
  no-best-result, exact-Off strengthening (with new Ed-hands bench check),
  rehearsal receipt class + any-intervention-fails.
- Multi-server (apple/NIST/pool, 2-of-3, interval intersection) over
  apple-only x3: Opus holds; Sol's shape correlated on BOTH axes (DNS/anycast
  single point). sntp -t retries x5 internally => -t 2 not -t 5.
- Continuity vs anchor: same quantity; carry ONE mechanism = separate 5 ms
  gate on CLOCK_MONOTONIC_RAW; R0 pre-pin + R1 live reference, R1 reordered
  BEFORE author censuses (concedes Sol's traffic objection).
- Successor-predicate rename + horizon change: defer both to one post-_v4
  registry row (T0-CLOCK-ROW-RENAME-01); PROBE branch omits the
  prior-state key entirely (no false evidence, no new profile mode in the
  15-row census module during _v4).
- Horizon: keep ruled 6h; recency in predicate content; PLUS publish anchor
  pair in T-0 receipt value + arm-side re-sample refusing >5 ms step
  (closes the step gap; Opus reversed its own deferral).
- REASON_CODE_COVERAGE: pre-implementation deliverable = enumerated delta
  against the closed refusal list (adds + retirements + rehearsal coverage).
- Ed-hands (4): D-127 sudoers install/exercise (blocking); ~2 min anchor
  positive control at bench adjacent to rehearsal (outside T-0 sequence);
  D-127.1 + 6h-retention ratification; exact "setUsingNetworkTime: Off"
  string bench-verification BEFORE it gates.

## Open items for the debate round
- Sol seat's independent shape (pending; codex task bmskne0gl).
- Cross-examine: Opus's SNTP-quorum + wall-vs-raw anchor falsifier —
  numbers to check: 8.3 ppm threshold vs 3.68 ppm benign drift vs 110/158 ppm
  incident slews; the ±395 ns anchor noise floor claim; Marzullo intersection
  admissibility (no invented agreement threshold — verify constants reused:
  0.5 s quiet_window_clock.sh:30, 5 ms anchor ceiling, _MIN_IDLE_NS).
- Opus scope flag: evidence blocker vs LAUNCH blocker (E-10 physical launch,
  D-127 clause 4 relaunch harness absent) — likely separate kernel row.
