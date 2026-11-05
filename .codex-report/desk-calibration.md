# ALIGN desk calibration

Branch: `lane/2026-11-04-align-desk-calibration`, based on the requested `cda28a5ef4144b4d0f441c112bc0aab97907bb81`. Early stub commit `5028b3a86` was pushed before implementation.

Implemented the labelled desk CLI in `scripts/align_pilot_calibration.py` and production-shaped synthetic coverage in `tests/align/test_align_pilot_calibration.py`. No real data or hardware measurement was used. The three frozen source files are unchanged. No registry, fixture, inventory, kernel, or other out-of-scope file was edited.

## Decisions I made

- Import `load_members` and the full frozen implementation pin from the existing desk script. Preserve its labels, input order, duplicate-label validation, and member-only loading.
- Run frozen analysis independently by session. Retain exact registered-scope, per-pair, counts-logged values for both designs; no recomputation of those values.
- Keep configuration cohorts separate, as the frozen analysis does. Within each cohort/design, deduplicate pooled benign scores on `(task_pair, condition, seed)` in session/member order. Frozen representative selection removes within-session replays first. Seed selection limits calibration, never the fitting population or sabotage reporting.
- Compute split ranks using integer arithmetic, `(19*(m+1)+19)//20`. This implements the stated formula exactly but conflicts with the supplied m=21 test expectation; see NEEDS_RULING below. Do not silently special-case that sample size or change its required test.
- Use finite benign LOO scores for m, preserving unavailable score witnesses and flagging nonfinite calibration scores, consistent with the frozen analysis. An unavailable pooled threshold is JSON null and stdout NA; its crossings are not evaluated.
- Reuse each sabotage trajectory's own-session full-fit score and curve. Compare strictly above threshold; an initial crossing at k=0 is `above_at_H0` and never a detection. Sabotage records retain every session's representatives, since cross-session deduplication is required only for calibration.
- Print clock diagnostics for each session/configuration/pair/design, beside that design's residual in joules. Pearson n counts finite residual/clock pairs; fewer than two pairs or constant data gives NA. Clock values never enter JSON results, fits, scores, thresholds, flags, or crossings; exact clock-independence is tested.
- For the +8 J test, truncate builder episodes to ten turns and add 0.8 J to every turn plus 8 J to measured episode totals. This makes both a constant per-turn intercept shift and an exact +8 J episode shift. Distinct seed indices in the second session let the single-fit contrast include both sessions rather than deduplicating them.
- Use only the stipulated 1e-6 relative offset-invariance tolerance: intercept absorption is exact algebraically, floating-point error is about 1e-12 relative, and 1e-6 is 1e6 times that noise while below 1% of the 1 J attribution limit on a 2000–4000 J episode. The cross-session contrast uses the same bar. Integers, selected scores, and identical-code/input values use exact equality. No other numeric tolerance was introduced.

## Verification

Python: `/usr/bin/python3.13`. Each run uses `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, and a newly created `TMPDIR`.

Command:

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d) python3.13 -m unittest tests.align.test_align_pilot_calibration tests.align.test_align_pilot_alt_desk tests.align.test_energy_residual
```

Initial run: 33 tests, 32 passed; the sole failure is the brief's m=21 contradiction (formula produces 21, supplied assertion requires 20). Offset invariance, single-fit contrast, identity, deduplication, strict/H0 crossings, clock independence, parser behavior, duplicate labels, and actual CLI subprocesses on three synthetic PILOT.json files passed. The CLI checks both default calibration and `17-26`; the third file has ten benign seeds 17–26 and sabotage only at seed 1.

Final run after simplifying parser assertions and adding configuration/registered-eligibility coverage: 34 tests in 39.566 s, 33 passed, the sole failure remains m=21 (21 versus the required 20). Full-suite execution is intentionally excluded by the explicit user instruction; CI owns it. `git diff --check` passed.

## NEEDS_RULING

Question: at m=21, should k be 21 from `ceil(0.95*(m+1)) = ceil(20.9)`, or the explicitly listed 20?

Options considered: follow the split-rule formula; introduce an m=21 exception to follow the supplied integer list.

Recommendation: follow the split-rule formula, k=21, and correct that one test expectation. This preserves the stated prospective calibration rule.

Blocked work: changing either the printed rank/threshold or the required test expectation to resolve their disagreement. The implementation and test deliberately expose the conflict; this branch is not ready to treat as a passing calibration deliverable until the ruling arrives. All independent scoped work is complete. No outside-scope change is needed.
