# T0-UNATTENDED-01 debate round — Opus seat critique of the Sol design

Delivered 2026-08-23 night by the Opus design-seat agent (a7f0ec45a7fdb4f7f)
after reading seat-sol-design.md; blind phase over. Recorded verbatim from
the agent's report by the magistrate (transport: task notification; the
agent produced no separate file).

## 1. Agreements co-signed (12)

1. No new privileged command — the D-127 amendment is a closure, not an
   addition; `-getusingnetworktime` stays unadopted. Both seats reached this
   independently.
2. The PROBE hook at `arm_readiness.py:731` pre-exists; no SOURCE_KINDS or
   evidence-kind change.
3. The prior-state read is retired, not automated (bench note confirms the
   tautology; neither seat re-litigates).
4. `/usr/bin/sntp` is the right reference tool — platform-native, already
   used at `quiet_window_clock.sh:42`, reports its own uncertainty.
5. The 0.5 s ceiling is reused from `quiet_window_clock.sh:30`, not invented.
6. Quorum >= 2, every valid sample participates, no best-result selection —
   Sol's phrasing, adopted verbatim.
7. The reference batch is one attempt, not three retries; a refusal ends the
   lane under D-078/D-149 c.5.
8. Fail-closed everywhere; no partial evidence namespace is ever published.
9. Sol's `sample_policy_id` — the server set as a versioned policy id rather
   than a runtime choice. Adopted.
10. Sol's exact-Off-output strengthening of clock-disable (exit 0 AND the
    exact stdout line) — strictly better than HEAD's exit-code-only check.
    Adopted, with the SS2(b) caveat.
11. Sol's rehearsal receipt class — `claim_eligible: false`, window-ID
    prefix, custody root outside production, and the production-side
    mechanical-rejection negative check as part of acceptance. Adopted.
12. Sol's rule that any intervention fails the rehearsal, even one that
    would have made it succeed. Adopted.

## 2. Disagreements with grounds

### (a) Three legs against time.apple.com vs three distinct providers

Held for multi-server. Three legs against one host reduce variance, not
bias; a systematically wrong server produces three agreeing legs and a
silent-wrong-answer pin — strictly worse than refusal, and a misconfigured
time server is a bug inside D-139-A1's model. Sol's own risk register
concedes the shared-server dependency, admitting a regression against the
operator-yes on the source-diversity axis. The reachability argument
inverts: Sol's three legs share one DNS name and one anycast target, so the
most likely failure takes out all three; 2-of-3 across Apple/NIST/pool
survives it. pool.ntp.org is the weak member (stratum 2, measured root
dispersion 10.16 ms) and the intersection rule absorbs it correctly.
Measured correction: `sntp` retries five times internally, so `-t 5`
implies ~25 s/leg against Sol's 10 s subprocess kill — use `-t 2` with one
`_fresh_probe` per server.

### (b) Continuity term vs anchor falsifier — same mechanism, Sol's instantiation defective

Algebraically the same quantity (ANCHOR = wall − mono). Sol loses on clock
choice and gate placement:

- Defect 1, measured on this machine: Python `time.monotonic_ns()` on
  Darwin IS `CLOCK_UPTIME_RAW` (identical to ±1 us) — sleep-blind.
  MONOTONIC_RAW − UPTIME_RAW = 812,998 s (9.41 days asleep). T-0 runs
  uncaffeinated (census requires caffeinate ABSENT), so a nap during the
  >=600 s dwell blows the bound. Closed-direction failure: an availability
  defect — a night lost to a phantom clock fault. Fix is one token:
  CLOCK_MONOTONIC_RAW.
- Defect 2: summing continuity into the 0.5 s bound silently relaxes the
  governed 5 ms anchor ceiling ~90x. Worked incident replay: 110 ppm x
  600 s = 66 ms; Sol's summed bound PASSES (114 ms <= 500 ms) where a
  separate 5 ms gate REFUSES. The summed design would have passed the
  incident it exists to catch. Summing also destroys refusal attribution.
- If only one survives: the separate 5 ms RAW-anchor gate. They compose
  fully if un-summed.
- Concession owed: Sol's probe-traffic objection to the R1 authoring-time
  query is correct; cure adopted — R1 executes BEFORE the author's fresh
  maintenance and process censuses, which then observe the machine after
  the network activity. The frozen 180 s settle sits between authoring and
  measurement regardless.

### (c) Sol's successor predicate `clock.correct_and_pinned_state.v1`

Sol's stated harm (false `prior_systemsetup_state_captured` evidence) does
not apply: the Opus design moves that key into an OPERATOR_ATTESTATION-only
branch — the PROBE value dict does not contain it; no claim, no false
evidence. The unstated ground that DOES land: the fact id names a thing the
PROBE path no longer does — a real legibility defect. But Sol's cure
(profile-aware `_required_rows`/`_DERIVERS`/`_ROW_KIND`/census in the most
safety-critical module, during `_v4`, with a never-both selection invariant
whose mis-selection arms a pack against the wrong clock row) is
disproportionate; the Opus shape cannot have that failure mode. Disposition:
rebut the mechanism, adopt the concern, defer the cure — batch rename +
horizon into one post-`_v4` registry row (T0-CLOCK-ROW-RENAME-01), noting
the coupling.

## 3. The two adjudication notes

- Horizon: the 1200 s proposal is a ruled-number reversal traveling as an
  implementation detail — rule-11 territory; flagging was right regardless
  of merits. The magistrate's dissolution survives with arithmetic: 6 h
  covers drift (3.68 ppm x 6 h = 79.5 ms; +40.8 ms authoring bound = 120 ms
  vs 500 ms — 4.2x margin) but NOT a step, which is unbounded — and Sol's
  20 min doesn't bound a step either. Amendment recommended (reversing the
  Opus seat's own S10 item-8 deferral): publish anchor_realtime_ns /
  anchor_monotonic_raw_ns in the T-0 receipt value and add an ARM-SIDE
  predicate that re-samples the anchor and refuses on >5 ms movement since
  T-0 — drift covered by arithmetic, steps by mechanism, no ruled number
  moves.
- REASON_CODE_COVERAGE: concede ("convention answer to a gate question").
  There is a live gate (`desk.reason_code_plumbing`, registry v1:240-242;
  alpha_arm_readiness.md:109). Pre-implementation deliverable required: an
  enumerated delta against the closed refusal list — codes added, codes
  retired (`clock_prior_state_capture` dies in both designs), rehearsal
  coverage evidence for each.

## 4. R2 positive control — stands

Sol's rehearsal receipt class is an unattendedness proof, not a detector
proof: every pass criterion is green-path; a rehearsal with a silently
inert clock detector passes all of them — exactly the 2026-07-26 shape.
The ~2 min privileged anchor positive control at Ed's hands remains
required; it runs OUTSIDE the T-0 sequence at the bench adjacent to the
rehearsal window, so Sol's any-intervention-fails rule is not violated
(make that explicit or the rules read as contradictory). It would also have
caught Sol's sleep-blind clock in one wake cycle. New fourth Ed-hands item
created by Sol's shape: bench-verify the exact `setUsingNetworkTime: Off`
string under sudo BEFORE it becomes a gate.

## Recommended synthesis (Opus seat's closing position)

Opus skeleton — single row, in-place source discrimination, two references
(R0 pre-pin + R1 live), separate 5 ms anchor gate on CLOCK_MONOTONIC_RAW —
with Sol's sample_policy_id, no-best-result rule, exact-Off strengthening,
and rehearsal receipt class folded in; R1 reordered before the author
censuses; the anchor published for an arm-side step check; rename + horizon
batched post-`_v4`. Ed-hands (4): D-127 install/exercise (blocking); ~2 min
anchor positive control; D-127.1 + 6 h-retention ratification; exact-Off
string bench verification.
