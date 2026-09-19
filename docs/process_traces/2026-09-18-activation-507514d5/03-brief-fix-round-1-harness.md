SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["scripts/sample_quiet_predicate_evidence.py","tests/test_sample_quiet_predicate_evidence.py"]

# Fix round 1 — lane QUIET-PREDICATE-EVIDENCE-01 (kernel 232) sampling harness, head `d066d271`

Cwd is `/Users/edr/code/JouleWise-wt-harness-232` on branch `feat/2026-09-18-quiet-predicate-evidence-harness` at `d066d271`. Do NOT commit (the lead commits by pathspec). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree. Never run `sudo`, `powermetrics`, or a live `collect` with power. A measurement night is armed on this machine for 00:00 PDT: every process you start must end inside 60 s; keep load experiments to `--cores 0.1` and at most 10 s. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`; `pytest` is absent, use `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence`. Never run the canonical discovery suite. Finish inside 20 minutes: if an item will not fit, leave it untouched and say so in the report rather than half-do it.

## Why

Two read-only refuters reviewed `d066d271`. Read both reports first: `/tmp/mag-507514d5/01-refuter-contract-astra.md` (contract lens: F1, F2) and `/tmp/mag-507514d5/02-refuter-execution-astra.md` (execution lens: R1 blocker, R2–R7). The execution lens's mutation script is at `/tmp/mag-507514d5/mutations.py`; it must report failures for every mutation after your change. The contract lens confirmed (C5) that the production alignment path has no arrival-time fallback, so R1 is a coverage defect: the test suite passes when alignment is replaced by arrival time. The cure is a regression that fails under that mutation, built from a fixture where arrival time and anchored time differ by a known amount; a test that only checks the field exists kills nothing.

## Do, in this order

1. R1 (blocker): a regression whose expected aligned timestamps are computed from the anchor model on a fixture with a deliberate arrival-vs-anchored offset (state the offset in the test), asserting the aligned value and the bound; it must fail under `mutations.py alignment`.
2. R2: a regression that supplies a known reaped-child CPU delta and asserts the observer cost includes it; must fail under `mutations.py observer`.
3. R3: `load` honours `--cores`: a short real run (≤ 3 s, cores 0.1 and 0.2) asserting the log's achieved thread-CPU fraction tracks the setting within a stated tolerance; must fail under `mutations.py cores`. State the tolerance and why it is sized to a 3 s window.
4. R4: one real-subprocess integration test of `collect --no-power` with the smallest legal duration and interval into a temp dir, asserting rows exist with `status`/`error` explaining the missing power and that every worker PID recorded is gone afterwards.
5. R5: `summarize` over an empty directory produces a reasoned-null summary (exit 0, `status: "no_rounds"` or equivalent, reason string, PROVISIONAL label), with a test.
6. R6 + F2: the JSON summary carries `evidence_status: "PROVISIONAL"`, the alignment model label and the network-time provenance exactly as `session.json` does, with a test.
7. R7: temporary journals are created under the `--out` target (or a subdirectory of it), never under `TMPDIR`, with a test asserting nothing is written outside `--out`.
8. F1: every round row records the census results observed during that round (the smoke round's concurrent censuses, not only the sample observation's), a per-round `census_clean` boolean derived from them, and `null` with a reason when no census completed; `summarize` groups by `census_clean` and never pools clean with contaminated or unknown rounds. Update the module docstring's schema description accordingly. Keep the schema name `joulewise.quiet_predicate_evidence.v1` unless a field's meaning changed, in which case say so and stop with a NEEDS_RULING rather than bump it silently.

Run the 31 existing tests plus yours, then every mutation in `mutations.py`, and paste the tails. Do not weaken or delete any existing assertion.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; per item: DONE / NOT DONE with the test name and the mutation result. List every file written. Residual risk and anything you could not verify go in flags.
