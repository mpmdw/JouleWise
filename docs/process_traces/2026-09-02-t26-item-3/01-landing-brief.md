WRITE_SCOPE: ["joulewise/arm_readiness.py","joulewise/arm_readiness_evidence_t0.py","tests/test_arm_readiness_evidence_t0.py","tests/test_arm_readiness.py","tests/test_t0_rehearsal.py","docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md","docs/contracts/arm_readiness.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# INSTALL T26 cold-gate verdict item 3 — the T-0 600 s liveness bound

Linked worktree `/Users/edr/code/JouleWise-wt-t26-b`, branch
`feat/2026-09-02-t26-liveness` @ 6075389a (main). You cannot commit; the
magistrate commits. Never run `python -m unittest discover`; named modules
only. `TMPDIR` is preset under the scratchpad. Never edit
`docs/process/state_kernel.json`, `docs/decision_log.md`, any `runs*/`, or any
file outside WRITE_SCOPE (`docs/contracts/arm_readiness.md` is in scope ONLY
if it documents the predicate's clock relations — check; if it does not, leave
it untouched and say so).

You are implementing a RULING verbatim. If a ruled clause cannot be
implemented as written (a cited site does not exist, a required input is
unreachable on the call path), STOP that clause and return a `NEEDS_RULING`
flag naming the clause, the obstacle, and two concrete options — do not
improvise a semantics. This is HARDWARE-ADJACENT night machinery: a wrong
bound refuses a healthy night; a missing bound lets a stalled T-0 issue.

## The ruling (read in full first)

`docs/process_traces/2026-08-27-t26/process-proposals/COLD-GATE-RULING.md`
item 3, `:162-253`. Operative text (`:196-215`, verbatim):

> `0 ≤ (valid_until_monotonic_ns − 21_600_000_000_000) − r1_batch_finished_monotonic_ns ≤ 600_000_000_000`
> with both endpoints from `context.clock.monotonic_ns()` (the clock every
> consumer tests `valid_until_monotonic_ns` against). Clock: ordinary
> monotonic (`time.monotonic_ns`, `CLOCK_UPTIME_RAW` on Darwin) — NOT
> `CLOCK_MONOTONIC_RAW`, which stays reserved for the anchor physics.
> Constant provenance: eleven `_fresh_probe` sites × `_PROBE_TIMEOUT_SECONDS
> = 45` = 495 s; 105 s allowed for the intervening derivers' ungoverned
> filesystem/git work; the sum equals the module's existing `_MIN_IDLE_NS =
> 600 s`. The bound is a liveness/hang detector and is labelled so in code;
> it is NOT a metrology bound.

The 5 s constant and the 35 s corollary are STRUCK. Enforcement (`:229-236`):
`arm_readiness.py` `_predicate_passes` clock branch gains the
`≤ 600_000_000_000` conjunct; issuance already runs the predicate
(`arm_readiness_evidence_t0.py:2342`, and `:2217`), so producer refusal is via
the registered `evidence_author_t0_predicate_refused` — NO new reason code, no
REASON_CODE_COVERAGE delta. Regressions: boundary controls 600 s + 1 ns
refuses, 600 s − 1 ns passes, at BOTH the issuance and the arm site. Update
the pre-ruling comment and the §6.3 "COLD-GATE-PENDING" disposition.

## Where the code is today (main 6075389a; re-locate with grep)

- `joulewise/arm_readiness.py:6413` `_clock_probe_predicate_passes`; the
  clock conjunct block `:6467-6483` currently reads
  `valid_until - value["r1_batch_finished_monotonic_ns"] >= 21_600_000_000_000`
  under the comment (`:6477-6479`) "The R1-completion-to-validity-origin <=5 s
  upper bound is an open magistrate item at HEAD's derivation order." That
  comment is now false; replace it with the liveness label and the D-170 /
  ruling pointer. Determine whether `valid_until` there is
  `valid_until_monotonic_ns` on the ordinary clock and whether
  `r1_batch_finished_monotonic_ns` (`:6370`, distinct from the `_raw_ns`
  sibling at `:6368`) is the ordinary-clock stamp the ruling names — cite
  the producer line in `arm_readiness_evidence_t0.py` that writes each. If
  the two stamps are NOT on the same clock, that is a NEEDS_RULING, not a
  guess.
- Constants: `arm_readiness_evidence_t0.py:51` `_MIN_IDLE_NS`, `:54`
  `_PROBE_TIMEOUT_SECONDS`. Re-do the §6.3 AST census of `_fresh_probe` sites
  yourself (count them; if the count is no longer eleven, report the new
  count and whether 495 + 105 still lands on `_MIN_IDLE_NS` — the ruled
  constant is 600 s regardless; the provenance note in code must be TRUE).
- `_predicate_passes` `:6510`; arm-site consumers `:6663`, `:9120`.
- `docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md`
  `:990` (§6.3 heading) and `:1132-1150` (the COLD-GATE-PENDING disposition):
  append a dated disposition line citing the ruling file and D-170; never
  rewrite the existing text.

## Regressions (defect-shaped; each its own test method, named for what it refuses)

At the ARM site (`tests/test_arm_readiness.py` or the module that already
exercises `_clock_probe_predicate_passes` — find the existing fixture that
builds a passing PROBE receipt and reuse it):
1. `test_t0_liveness_bound_refuses_at_600s_plus_1ns` — receipt otherwise
   valid, `valid_until − 6 h − r1_batch_finished = 600_000_000_001` → False.
2. `test_t0_liveness_bound_passes_at_600s_minus_1ns` → True.
3. `test_t0_liveness_bound_refuses_negative` — `valid_until − 6 h <
   r1_batch_finished` (the `0 ≤` half) → False; confirm whether the existing
   `>= 21_600_000_000_000` already covered this and say so.
At the ISSUANCE site (`tests/test_arm_readiness_evidence_t0.py` — find the
existing test that drives the author through `:2342` with a fake clock/context;
if the existing fixtures cannot make the author's derived
`r1_batch_finished_monotonic_ns` lag `validity_origin` by a controlled amount,
say exactly why and what seam would be needed → NEEDS_RULING for that half
only, with the arm-site half still landing):
4. `test_issuance_refuses_t0_when_r1_batch_is_stale_by_600s_plus_1ns` →
   `evidence_author_t0_predicate_refused` (assert the reason code string).
5. `test_issuance_passes_t0_when_r1_batch_is_600s_minus_1ns_old`.
`tests/test_t0_rehearsal.py`: only if the rehearsal evaluator re-derives this
relation (grep `r1_batch_finished`); if it does, mirror 1–2 there, else state
that it does not and leave the file untouched.

Mutation check you run and report: delete the new conjunct, re-run — tests 1
and 4 must FAIL; restore.

## Verify and report (verbatim tails)

- `python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_evidence_author tests.test_capture_t0_step`
- `python3 -m unittest tests.test_reason_code_coverage` (or whatever module
  pins REASON_CODE_COVERAGE — find it; it must be unchanged-green)
- the mutation check
- `git diff --stat`; `git status --porcelain` — only WRITE_SCOPE files dirty.

FINAL message = `claude-codex-report/v1` envelope (implementation) with a
`verification` entry per command, `flags` for any NEEDS_RULING, and a "Change"
section: each ruled sentence of item 3 → CONFIRMED (file:line) or NOT DONE
(why), plus the `_fresh_probe` census result and the clock-identity finding
for the two stamps.
