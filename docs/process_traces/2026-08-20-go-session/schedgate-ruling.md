# Scheduler mechanical gates — D-144 co-design ruling (2026-08-20)

Seats: terra (xhigh) + Opus 5, independent designs + one debate
response each (custody: schedgate-*-design.md, schedgate-*-debate.md).
Authority chain: r5 consolidation V-3/V-6/S-2 over r3 B-3. Pending one
cold delta pass (contract change on the window path), then the
implementation stages open.

## R-1 (fuse semantics — and a first-use failure in governing prose)

G1's predicate is: `min(TIME_BOUND evidence deadlines) − now ≥
arm_to_consume_budget_ns` (registry-sourced; refuses
`_budget_unresolved` while the value is ED_RESERVED). The "projected
span + margin" framing — invented by the magistrate's own brief and
faithfully reproduced by one seat — is STRUCK: `arm_to_consume_budget_ns`
is the minimum remaining T-0 evidence life required AT ARM, exactly as
the R1 registry ruling's V5 RECORDED WARNING states; a span-based gate is structurally
unsatisfiable (multi-hour spans vs 20-minute volatile horizons) and
would refuse every window. G1 RECOMPUTES DEADLINES FROM THE
AUTHENTICATED FROZEN EVIDENCE BYTES (all TIME_BOUND receipts) and
never treats an arm PASS as freshness proof (converged: terra F2,
Opus acceptance) — the load-bearing half of the gate while
FREEZE-REPLAY-EXPIRY-01 is open. RECORDED LESSON: the warning (the
R1 REGISTRY RULING's V5 — custody MAGISTRATE-RULING.md, "RECORDED
WARNING"; correctly homed per the cold pass) predicted two seats
misreading the name, and a third reader (the magistrate) then
repeated it in a brief — a first-use-test failure in governing
prose. Every future document glosses the name at first use; the V-4
Ed disclosure carries the gloss.

## R-2..R-8 (the debate's decisive rulings)

R-2: the arm-receipt schema amendment (recording
`armed_at_monotonic_ns` for the timing ledger) is a `_v4` VERSION
BUMP — ARM_RECEIPT_KEYS is exact-key enforced; no in-place key add.
The timing ledger records the arm instant from the gate's own clock
at authorization (terra's catch: it is NOT derivable from
valid_until, whose min may come from an expiry).
R-3: the `launch_window.py` seam is ENFORCED IN CODE — consume
refuses without a valid gate receipt (documentary binding is the
eaten-stop-signal failure V-5 exists to prevent).
R-4: p99 = nearest-rank; at n=1 that is the value itself (identical
to the max below n=100, so both seats' proposals coincide; the
statistic line records n).
R-5: the campaign-span CREATE-ONLY boot pin is ratified (Opus): a
per-window three-point check is internally consistent by
construction after a reboot; only a span pin makes V-7.5 mechanical.
R-6: G6-C1 encodes BOTH branches pending Ed's S-1 ruling —
shakedown-scoped reduced ED set for SHAKEDOWN, full set for CLAIM;
neither an amnesty nor the deadlock.
R-7: the evaluator's agent-ancestry self-refusal STANDS (fail-closed
under the tightened B-16 pattern); the D-149 no-hands path therefore
requires an AGENT-FREE DRIVER (launchd/cron outside agent ancestry) —
a topology commitment recorded on Ed's visibility list and a named
input to the GO-evaluator work order. NO DRIVER IS INSTALLED OR
BUILT except under Ed's B-δ option (b) gauntleted work order; if Ed
chooses attended-T-0, the no-hands path and its driver stay unbuilt.
(Cold-attached clause.)
R-8: the B-22 cure is a parallel gauntleted track landing before G3
activation (both seats agree it goes first; the row lives in
READY-WO-BATCH-01's B-22 clause).

## Ratified design (converged)

Placement: `joulewise/scheduler_gates.py` + thin
`scripts/evaluate_window_gates.py` (greenfield — verified NO existing
fuse check in run_campaign.py; the earlier contrary assertion is
corrected for the record). Separate `SCHEDULER_GATE_REASON_CODES`
vocabulary, NOT unioned into READINESS_REASON_CODES — ground per
terra F3's corrected causal chain (the cold pass struck the
"corruption" wording): unioned codes become ADMISSIBLE inside arm
receipts and can later fail the arm's derivation/replay equality —
a fail-closed replay mismatch, avoided by keeping the vocabularies
disjoint; mirrored codes carry `mirrored_from`. Gate receipt
`joulewise.window_scheduler_gate_receipt.v1`, custody-written before
first capture, bound into the GO receipt by sha. All six gates always
evaluate (no short-circuit); *(AMENDED 2026-08-22 by the marker
co-design ruling,
`docs/process_traces/2026-08-22-t20/marker-codesign/MAGISTRATE-RULING-MARKER.md`:
the enumeration becomes SEVEN gates — G7 = family-publication — and
the receipt bumps to `…gate_receipt.v2` with an exact-key
`family_publication` block; the all-gates-always-evaluate and
G5-first rules extend to G7 unchanged)* G5 boot pin evaluates FIRST with
NOT_EVALUATED (never PASS) semantics for monotonic gates across a
boot mismatch. G1 additionally REFUSES when the :6151 lifecycle check
is inert (dormant-R1 refusal — the scheduler never trusts a dormant
gate). G2 sticky halt never self-clears (rule 11). G3 cure detection
is BY EXECUTION (the L4 truncation fixture must be refused;
`_cure_ineffective` otherwise); shakedown records stamped
`claim_admissible: false` (no retrospective promotion — the cold
sentence flows through). G4 reviewed_main exact-match fail-early is
the mechanical detector of a V-3(c) freeze breach. No bypass flag
(grep-testable); no waiver of any arm gate; no pack writes.

## Implementation stages (open after the cold pass)

Opus's 0-7 with terra's amendments; every stage lands BEFORE the
V-3(c) freeze opens or rides the transaction's enumerated step list.
Stage order: vocabulary+schema → G4+G5 (inputs exist at head) → G1
(sequenced with/after FREEZE-REPLAY-EXPIRY-01, delta re-audit
against it) → G2 + timing ledger (with the R-2 version bump priced
into the `_v4` family, not `_v3`) → G3 (blocked on the B-22 track) →
G6 + CLI + wiring (incl. the R-3 launch_window enforcement) → the
kernel row closing WO-D149-GO-EVALUATOR. R12 binds: no review credit
until the specified test pins RUN in a writable worktree — neither
seat executed one.
