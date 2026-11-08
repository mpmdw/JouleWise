# Sol delta-3 review of PR #704 — seat sol2

Date: 2026-11-08. Branch: `b5rel/2026-11-08-sol-delta3-704-sol2`.
Reviewed: `131369801..c41ee4b09984c49a1e4f929ca00b6bd17f8a8a21`.
The branch was already provisioned at the requested head and clean on intake.
Both delta-2 reports were read from their named local `origin/b5rel/...`
refs through Git objects; no fetch or network access was used.

## Verdict: ADMIT

The four lead dispositions are implemented. No new false agreement, new
false refusal on correct output beyond the explicitly accepted conservative
holds, or broken exit contract was demonstrated in the reviewed delta.
There are no blocking findings or requested production fixes.

This admits the code delta under the brief's dispositions. It does not
authorize unsealing, publication, merging, or running a real-data release.
Block 5 remains sealed until Ed's unseal OK.

## Dispositions and executing evidence

1. **Inside the bar is always undetermined; outside uses strict `>`.**
   `limited_forms` no longer accepts identity of the three printed numbers
   as identity of the unprinted bound. For an eligible computed form with
   nonzero widths inside or exactly on the `floor_j` bar, it returns `None`
   and its decision scope records `within_bar_undetermined`. Aggregate and
   per-resolution callers supply those scopes, and both comparator and
   release hold automatically. The two delta-2 modules pass, including the
   real producer's one-ulp unprinted-bound counterexample. The new module
   checks adjacent representable inside/outside values at both edges, with
   the absolute and relative bars, both forms, and diagnostics present or
   absent. It also checks exact equality and an exact positive bar-edge
   distance. The CLI witness pins all twelve expected aggregate, claim and
   resolution keys for both exact and transported diagnostic layouts:
   numerically agreeing rows still exit 1. Zero-width and noncomputed forms
   retain their existing exclusions; this delta does not broaden those gates.

2. **Exit precedence is refusal (2), then hold (1), then agreement (0).**
   The comparator checks coverage refusal before semantic disagreement or
   undetermined holds. `stage_compare` now rejects process statuses outside
   `(0, 1)` before either hold branch. The touched release module executes
   the actual comparator for normal agreement, disagreement, undetermined
   output, and mixed refusal cases. In particular, exit 2 with family failures
   becomes release exit 2 / `comparator_refused`, with its family counts still
   reported. The new CLI witness combines failed families, coverage refusal
   and undetermined rows. A separate 20-case process/output matrix checks
   exits 0, 1, 2, 3 and -9 against failures and undetermined rows. That matrix
   mocks only stage-(c) process output; it is not a custody or independent
   recomputation validation.

3. **Transport usability remains a disclosed inherited limit.** DLE-5 now
   explicitly distinguishes finite source-floor arithmetic from engine
   transport usability. The real synthetic resolver controls in both
   delta-2 modules still show an in-envelope transported consumer and an
   out-of-envelope refused consumer with a finite source floor. The latter
   correctly remains held by the proxy, rather than becoming agreement.
   This inherited conservative mismatch is accepted by the brief; it is not
   repaired or claimed equivalent to general transport validation. The
   registered Block-5 floor route is `exact_stack_only.v1` (analysis plan
   section 5). No printed refusal is trusted to disable a due comparison.

4. **Legitimate permanent holds are disclosed.** DLE-5 expressly says that
   correct nonlimited output can hold indefinitely and an unchanged rerun
   cannot clear it. It names structural equality with positive widths on
   other members and makes no liveness guarantee. The prior witnesses for
   producer equality, below-equality and the ten-member structural plateau
   all pass. No empirical likelihood or statement about actual Block-5
   values follows from these synthetic cases. Disclosure does not itself
   supply an override or release authority.

## Independence and scope limits

`scripts/independent_recompute_b5.py` is unchanged across the reviewed range.
Its SHA-256, independently checked with `shasum` and the witness module, is
`d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`.
AST inspection finds stdlib imports only, no relative imports, and no direct
`exec`, `eval` or `__import__` calls. The comparator delta adds no estimator
import. The existing copy-only checks for derivation-exempt words and
discipline objects remain copy checks; this review does not close other
LEAN-COVERAGE-AUDIT exemptions or certify sealed scientific outcomes.

All input data used here was synthetic. Temporary directories named
`restricted` were created only by the repository test harness. External
archive paths in tracked configuration were treated as text. No real
measurement data or real restricted directory was accessed. No model weights
were downloaded, no Block-5 analysis pipeline was run, and the running analysis
job was not inspected or altered. No new agent or cross-model consult was launched.

## Verification

Each test module ran in its own process, sequentially, using:

```text
JW_B5_SYNTHETIC_ONLY=1 nice -n 10 python3.13 -B -m unittest tests.independent_recompute.<module>
```

| Module | Tests | Result | Seconds |
| --- | ---: | --- | ---: |
| `test_sol_delta2_review_704_sol1` | 7 | pass | 3.921 |
| `test_sol_delta2_review_704_sol2` | 10 | pass | 0.923 |
| `test_floor_limit` | 37 | pass | 15.861 |
| `test_release_b5` | 31 | pass | 8.832 |
| `test_sol_delta_review_704` | 21 | pass | 165.331 |
| `test_sol_delta3_review_704_sol2` | 6 | pass | 1.194 |

All 112 tests passed, with no skips or expected failures, in 196.062 seconds
of reported test time. The new module also set `GIT_CONFIG_GLOBAL=/dev/null`
and `GIT_CONFIG_NOSYSTEM=1` to keep fixture Git independent of personal config.

`nice` reported `setpriority: Operation not permitted`; Python proceeded, so
the requested lower scheduling priority could not be enforced. The full suite
was not run, per the binding concurrent-job constraint. Focused
`python3.13 -B -m compileall -q` on the two production scripts, unchanged
recompute and all six review/touched test modules passed. `git diff --check`
passed, and the final staged diff was read before committing.

`python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` exited 2:
`PermissionError: [Errno 1] Operation not permitted: 'ps'`. Thus process
observation was unavailable; no clean-census or zero-orphan claim is made.
No permission bypass or retry outside the sandbox was attempted. This is an
environmental verification limit, not a comparator finding.

No MLX or native runtime code changed; there is no additional native/Metal
test requirement for this delta. Real custody and hardware checks were not
run and remain lead-owned.

## Handoff

Changed files: this review, its dated pointer under `docs/run_reports/`, and
`tests/independent_recompute/test_sol_delta3_review_704_sol2.py`. Production
code, `RUN_STATE.md`, `TASK_QUEUE.md`, state kernel and `tests/test_gen_state.py`
are unchanged; no task was registered. The review and witnesses are committed
together locally on the named branch; nothing is pushed.

Open questions: none blocking. Remaining uncertainty is the documented
general-transport proxy limit and the unknown frequency of permanent holds
on sealed inputs; neither was inferred from real data.

Next exact step: the lead audits these witnesses, combines the two independent
seat dispositions, and performs its final diff gate. Keep any real-data
comparator/release execution and Ed's unseal authorization outside this seat.
