# Block-5 comparator-bar audit

Date: 2026-11-06. Scope: `scripts/compare_b5_recompute.py`, the shipped block-5
bar set, and synthetic tests only. No experiment-data path was read.

## Verdict

The bars are **fixed blind as a release policy, not fitted tolerances**. The
shipped config identifies commit `7e322b767`, says it was fixed before any real
block-5 value was seen, and says it was not widened
(`configs/analysis/b5/recompute_bars.json:3-5`). The executable does not contain
a hidden `1e-6`: it requires every non-meter numeric family in the config
(`scripts/compare_b5_recompute.py:158-181`) and evaluates
`max(absolute, relative * abs(L9), half-print-unit)`
(`scripts/compare_b5_recompute.py:189-200`). This audit can verify those tracked
facts and behavior; it cannot independently reconstruct the historical time at
which the policy was chosen.

The release bars are appropriate for their stated purpose:

* Unrounded J, W, ratios, and positive duration use 1 ppm, generally with a
  `1e-6` absolute floor (`configs/analysis/b5/recompute_bars.json:7-35,42-75`).
  At a synthetic reference of 100 J, the computed bar is
  `9.999999999999999e-5 J`. The next binary64 value is only
  `1.4210854715202004e-14 J` away: the bar is about 7.0 billion ULPs. Thus normal
  last-bit evaluation-order noise passes, while the planted 2 ppm discrepancy
  (`0.00019999999999242846 J`) fails. The regression pins both outcomes
  (`tests/independent_recompute/test_comparator_bars_audit.py:20-34`).
* `contrast_p`, `rho`, and legacy wall-window edges use absolute `1e-6`, not a
  scale-dependent relative allowance (`configs/analysis/b5/recompute_bars.json:37-40,77-85`).
  `rho` therefore allows 1% of its documented four-decimal display quantum,
  while the p-value rule detects changes above one millionth.
* Counts and controller-stamp integer edges are exact, with zero absolute and
  relative allowance (`configs/analysis/b5/recompute_bars.json:57-60`). The
  synthetic test demonstrates that one representable step above 10 fails
  (`tests/independent_recompute/test_comparator_bars_audit.py:36-41`).
* Near zero, the `1e-6` absolute floor deliberately cannot detect a discrepancy
  below `1e-6` in the affected continuous families. That is the explicit blind
  policy, not floating-point necessity. There is no honest universal claim that
  every “real” physical discrepancy is caught; the precise claim is that a
  discrepancy greater than the configured ppm/absolute policy is caught.

## Key mapping and silent-pass audit

Numeric family keys are not an allowlist. A key receives the family default,
unless the first anchored (`re.fullmatch`) per-key override matches
(`scripts/compare_b5_recompute.py:184-186`). That fallback is intentional for
the release set, which has no key overrides. Configured overrides are validated
as regexes (`scripts/compare_b5_recompute.py:171-180`).

For item keys, all comparison sides are unioned. A key present on only one side
gets a `routing_id` disagreement with `missing_or_null`; duplicate comparison
rows refuse (`scripts/compare_b5_recompute.py:209-217,307-323`). Therefore an
unmapped item key does not disappear merely because the opposite side lacks it.

For step-11 leaf paths, an unmatched coverage rule is accumulated in
`coverage.unmapped`; a nominal mapping also fails coverage for unresolved/no
row, unequal copied value, disagreeing value or route, duplicate binding, or an
item outside the expected table (`scripts/compare_b5_recompute.py:3938-3978`).
Shortened copied lists are separately detected (`scripts/compare_b5_recompute.py:3982-3987`).
The existing synthetic suite proves the CLI refuses an unknown leaf and that a
catch-all would be unsafe (`tests/independent_recompute/test_comparator.py:724-738`).

The audited `continue`/filter paths are bounded rather than silent successes:

* A false registered condition omits its conditional expected item; when the
  condition holds, missing L9 or recompute keys become routing disagreements
  (`scripts/compare_b5_recompute.py:1428-1459`). Unclaimed items in closed
  collections become `unexpected/` disagreements
  (`scripts/compare_b5_recompute.py:1460-1464`).
* Recompute dictionaries deliberately select `status == computed`; the
  registry-driven expected table runs first and owns whether a non-computed item
  is expected (`scripts/compare_b5_recompute.py:1416-1480,1774-1782`).
* Missing/null numeric operands disagree rather than skip
  (`scripts/compare_b5_recompute.py:219-235`). Missing categorical operands do
  the same (`scripts/compare_b5_recompute.py:237-247`).
* Threshold-derived words may be `within_bar_undetermined`, but only agree when
  every numeric atom agrees and the word is in its producer vocabulary
  (`scripts/compare_b5_recompute.py:254-285`). This avoids turning a bar-straddled
  threshold into an unsupported categorical mismatch or silent pass.

## Hole found and fixed

Two finite-number overflow cases were not covered:

1. A syntactically valid finite relative coefficient multiplied by a very large
   finite reference could become infinity. The old `<= inf` check could then
   agree with any finite discrepancy. `bar_for` now refuses
   `bar_nonfinite_at_runtime` (`scripts/compare_b5_recompute.py:189-200`).
2. Opposite-sign finite extrema can subtract to infinity. The old row then held
   an infinite `difference`, so strict restricted-output JSON failed after the
   comparison. The row now disagrees, records `difference: null`, and names
   `difference_nonfinite` (`scripts/compare_b5_recompute.py:219-235`).

Synthetic regressions reproduce both cases and confirm the latter remains
serializable with `allow_nan=False`
(`tests/independent_recompute/test_comparator_bars_audit.py:42-56`). These paths
do not affect ordinary finite differences, so the happy-path comparison rows
and serialized analysis output are byte-identical. A pinned ordinary-row JSON
regression proves the byte shape (`tests/independent_recompute/test_comparator_bars_audit.py:43-49`),
and the full pre-existing comparator fixture remains green.

## Checks run

* `python3 -m unittest tests.independent_recompute.test_comparator_bars_audit tests.independent_recompute.test_comparator tests.independent_recompute.test_structural_rules`
* `python3 -m unittest discover -s tests` (started, then stopped: this checkout's
  canonical suite entered unrelated, exceptionally long B5 analysis work; the
  focused comparator suite above is the completed acceptance check)

