WRITE_SCOPE: ["joulewise/arm_readiness.py", "joulewise/arm_readiness_evidence_t0.py"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# REFUTE (execution lens) — T26 item 3: T-0 liveness bound, counterfactuals at the production site

Worktree `/Users/edr/code/JouleWise-wt-t26-b3` (DETACHED at the head of
branch `feat/2026-09-02-t26-liveness`; all files committed). The write scope
covers the two production files SOLELY so mutations can be applied and
reverted with `git checkout -- <file>` after EVERY mutation; the tree must
be byte-clean (`git status --short` empty) at exit. `TMPDIR` is preset under
the scratchpad. Named test modules only; never `discover`. No codex/claude
launches. Never run anything that arms, mints, or touches a night custody
root outside TMPDIR.

Ruling: `docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 3 (`:162-260`). Landed: `git diff 6075389a..HEAD`.

## Named counterfactuals — execute these FIRST, then add your own

Mandated suite for each: `python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas`
(record which test(s) fail; "KILLED by <test>" or "SURVIVED").

M1  constant 600_000_000_000 → 600_000_000_001 (must be killed by the +1 ns boundary tests at BOTH sites)
M2  constant → 599_999_999_999 (killed by the −1 ns passes tests)
M3  drop the lower `0 <=` half (keep only `<= 600 s`)
M4  drop the upper half (restore the pre-ruling `>= 6 h` only)
M5  read `r1_batch_finished_monotonic_raw_ns` instead of `r1_batch_finished_monotonic_ns` in the conjunct (wrong clock)
M6  in `arm_readiness_evidence_t0.py`, compute `valid_until` as `validity_origin + 6 h + 1 s` (issuance-side drift; must be caught by the issuance-site regression, not only the arm site)
M7  in `arm_readiness_evidence_t0.py`, stamp `validity_origin` BEFORE the fifteen-row loop instead of after (back-dating; report whether any test notices)
M8  replace the refusal path so the predicate failure raises a NEW reason code string (check the reason-code coverage test refuses the census change)

Then run the item's own claim: 600 s + 1 ns refuses / 600 s − 1 ns passes at
the issuance site by driving the AUTHORING entry point with a fake clock
(find how `tests/test_arm_readiness_evidence_t0.py:~831` does it and confirm
it exercises the real authoring function, not `_predicate_passes` directly).

## Also

- Confirm `_MIN_IDLE_NS` in `arm_readiness_evidence_t0.py` equals the new
  constant and say whether any test binds the equality.
- `python3 -m unittest tests.test_arm_readiness_evidence_author tests.test_capture_t0_step tests.test_arm_readiness_integration` — paste tails.
- Same-signature statement: none applicable (first round) — say so.

## Deliverable

FINAL message = `claude-codex-report/v1` review envelope: `mutations` (M1–M8
+ yours: mutation, KILLED/SURVIVED, killed_by), `verdict.findings` (each with
`file:line`, the counterfactual input, the observed outcome), `tests` tails,
and confirmation the tree is clean at exit. No fixes.
