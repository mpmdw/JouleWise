WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (contract lens) — T26 item 3 install: the T-0 liveness bound

Worktree `/Users/edr/code/JouleWise-wt-t26-b2` (detached at the head of branch
`feat/2026-09-02-t26-liveness`, two commits over main 6075389a: Sol 194's
landing `73fe1459` and one magistrate fixture commit). Read-only: write
NOTHING in the tree; `TMPDIR` is preset under the scratchpad for scratch
files. Never run `unittest discover`; named modules only. Do not launch
codex/claude processes.

## Your lens: RULED TEXT vs LANDED TEXT — with the S2 ordering rule

Ruling: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 3 (`:162-260`; the operative "Ruled relation" block and the
"Enforcement" paragraph). D-170 in `docs/decision_log.md` records the same
verdicts.

S2 ORDERING (mandatory, cold gate 2026-09-02): BEFORE reading the seat's
report or diff, read the ruling and write your OWN clause list — one row per
proposition a single production-site edit could falsify (the relation's two
inequalities, both endpoints on the ordinary monotonic clock, the constant
600_000_000_000, the "labelled liveness not metrology" code comment, refusal
via the existing `evidence_author_t0_predicate_refused` with no new reason
code, boundary regressions 600 s+1 ns refuses / 600 s−1 ns passes at BOTH
the issuance site and the arm site, the `:6336-6338` comment update, the
§6.3 COLD-GATE-PENDING disposition update citing the ruling file, and the
struck 5 s / 35 s text appearing nowhere as a live bound). Record that list
in your report FIRST under `## Independent clause list`. Only then open
`git diff 6075389a..HEAD` and the seat's clause map below.

Then, per clause, cite `file:line` for the landed text and give
CONFIRMED / DIVERGES / MISSING. Specific checks:
1. The conjunct at `joulewise/arm_readiness.py` (~:6478-6485): is it exactly
   `0 ≤ (valid_until − 21_600_000_000_000) − r1_batch_finished_monotonic_ns ≤ 600_000_000_000`
   with the constant named and the comment stating liveness provenance
   (11 × 45 s + 105 s = `_MIN_IDLE_NS`)? Is `_MIN_IDLE_NS` in
   `arm_readiness_evidence_t0.py` actually 600 s, and is the equality
   asserted anywhere by test (or only by comment)?
2. Both endpoints on the ordinary clock: trace `valid_until_monotonic_ns`
   at issuance (`arm_readiness_evidence_t0.py` validity_origin, ~:2313-2339)
   and `r1_batch_finished_monotonic_ns` (~:1120, :1199) — same clock object?
   Cite.
3. Issuance-site regression AND arm-site regression both present
   (`tests/test_arm_readiness_evidence_t0.py:~831`,
   `tests/test_t0_rehearsal.py:~562`, `tests/test_arm_readiness.py:~21`):
   does each hit the production conjunct through its own site (the
   authoring path vs the arm predicate), or do all three call the same
   helper? A test that reaches the predicate only through
   `_predicate_passes` directly is NOT the issuance-site regression.
4. No new reason code: grep for reason-code registries / coverage tests;
   confirm the REASON_CODE_COVERAGE census is unchanged.
5. Struck text: grep the repo (docs + code) for the 5 s / 35 s bound still
   stated as live (e.g. "≤5 s", "35 s old at issuance"); anything not marked
   STRUCK/superseded is a finding.
6. The magistrate's fixture commit changed `tests/test_arm_readiness_schemas.py`
   (sample EVIDENCE horizon 10**30 → R1 + 6 h + 1 s; sample ARM stays 10**30).
   Judge: is that the right fixture (does 6 h + 1 s sit strictly inside the
   ruled window), and does any schema test now lose coverage it had at
   10**30?

## Seat's clause map (from Sol 194's report — open only after your own list)

Production: `joulewise/arm_readiness.py:6349` constant, `:6478-6485`
conjunct. Tests: `tests/test_arm_readiness.py:59` ClockProbePredicateLivenessTests,
`tests/test_arm_readiness_evidence_t0.py:831`, `tests/test_t0_rehearsal.py:562`.
Disposition: `docs/.../reason-code-coverage-delta.md:1150` §6.3.

## Deliverable

FINAL message = `claude-codex-report/v1` review envelope with
`verdict.findings` (id, severity blocker/should_fix/nit, `file:line`,
`ruled_text`, `landed_text`, `why_they_differ`) and `verdict.clause_table`
(your independent list with CONFIRMED/DIVERGES/MISSING and the seat-map row
it corresponds to, or "not in seat map"). No fixes; no writes.
