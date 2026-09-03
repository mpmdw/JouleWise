WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (physics / causality lens) — T26 item 3: the T-0 liveness bound on the arm clock

Worktree `/Users/edr/code/JouleWise-wt-t26-b` (branch
`feat/2026-09-02-t26-liveness`, head = Sol 194 landing + one magistrate
fixture commit over main 6075389a). Read-only: write NOTHING in the tree;
`TMPDIR` preset under the scratchpad. Named test modules only; never
`discover`. No codex/claude launches. Never arm, mint, or touch any night
custody root.

Ruling: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 3 (`:162-260`) — read the refuter's objection, the six verified facts,
the ruled relation, and the two recorded limitations L1/L2. Landed:
`git diff 6075389a..HEAD`.

## Your lens: does the landed bound do what the physics says, on a real night?

You are NOT re-checking clause fidelity (another seat does that) nor
mutating code (a third seat does). You reason about clocks and time on
Ed's machine — Darwin, `time.monotonic_ns()` = `CLOCK_UPTIME_RAW`
(sleep-blind), `CLOCK_MONOTONIC_RAW` sleep-inclusive — and the actual
T-0 authoring path (`joulewise/arm_readiness_evidence_t0.py`: the R1
reference batch, the fifteen-row derivation loop, `validity_origin`,
`valid_until = validity_origin + 6 h`) and the arm/consumption path
(`joulewise/arm_readiness.py`: the clock-probe predicate, the live 5 ms
anchor re-sample, consumer expiry tests against `time.monotonic_ns()`).

Answer with file:line evidence and real numbers:
1. FALSE-REFUSE risk. Enumerate every governed and ungoverned wait between
   `r1_batch_finished_monotonic_ns` being stamped and `validity_origin` being
   read on the SUCCESSFUL path (list the `_fresh_probe` sites after R1 with
   their timeouts, plus filesystem/git work). Give the worst-case successful
   duration you can derive from code, and say whether 600 s covers it with
   what margin. Is the "eleven sites × 45 s + 105 s" census correct at
   HEAD — count the post-R1 `_fresh_probe` call sites yourself.
2. SLEEP. If the machine naps between R1 and the stamp (L1), both endpoints
   are on the sleep-blind clock: show with numbers what the bound sees and
   what the 5 ms RAW-vs-ordinary anchor gates (`arm_readiness.py` ~:6329,
   ~:6342-6366) see. Is there a nap scenario that passes the liveness bound
   AND both anchor gates but yields a reference that is stale in wall time?
   If so, is it already excluded by D-150's horizon or by something else —
   cite — or is it a real gap the ruling's L1 understates?
3. ARM vs ISSUANCE. The predicate runs at issuance and again at arm on the
   same receipt values. Is there any way the arm-time evaluation can differ
   from the issuance-time evaluation (different clock reads, re-derived
   fields, mutable inputs)? If both are pure functions of the receipt, say
   so and cite; if not, name the input that differs.
4. CONSUMER SEMANTICS. Consumers test `time.monotonic_ns() < valid_until`.
   With the new bound, what is the tightest and loosest possible age of the
   R1 reference at the LAST admissible consumption instant? State the
   interval in seconds and whether the paper's/contract's stated horizon
   text (grep docs/contracts for the 6 h horizon) matches.
5. The struck 5 s: is there any physical argument the ruling missed for a
   tighter bound (e.g. an interaction with `r1_batch_duration_ns ≤ 30 s`
   or the 3.68 ppm drift budget)? Give the arithmetic; if none, say the
   600 s is physically inert as a metrology bound, as the ruling claims.

## Deliverable

FINAL message = `claude-codex-report/v1` review envelope: `verdict.findings`
(id, severity, `file:line`, the scenario with numbers, what the code does,
what physics says should happen) and `verdict.answers` keyed 1–5. Findings
that merely restate L1/L2 are nits unless you show a concrete scenario the
ruling's text does not already exclude. No fixes; no writes.
