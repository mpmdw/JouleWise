# Sol burn: adversarial review of the R0 load-reference check

Date: 2026-11-06. Scope: `joulewise/align/r0.py`, `r0_mlx.py`,
`r0_runner.py`, and `configs/align/v4/r0_nll_reference.json`. All executions
used synthetic losses and canned completions; no experiment or custody path was
read.

## Verdict

**ADMIT after one fix.** I found one report-integrity bug: a vector containing
2,048 finite values of `1e306` overflowed the ordinary Python sums used for the
overall and per-bin means. The verdict consequently contained JSON `Infinity`.
The runner correctly refuses non-standard JSON, but this converted the useful
load failure into `report_serialization_error`. The fix retains the old
arithmetic on the ordinary/happy path and uses a divided-term fallback only
when the ordinary mean is non-finite. The synthetic regression now measures an
overall mean of `1e306`, eight bin means of `1e306`, a maximum absolute bin
delta of `1e306`, and the stable failure
`mean_outside_tolerance+bin_outside_tolerance`; strict JSON parsing succeeds.

No threshold, reference datum, generation policy, MLX decode setting, or
happy-path serialized profile changed.

## Reference-equivalence audit

* The shipped D identity is revision
  `815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9` plus fixture digest
  `792beb...ac42`; its HF reference is mean `11.0642` and eight positional
  256-token means. (`configs/align/v4/r0_nll_reference.json:8-16`)
* The acceptance widths are exactly mean `±0.10` and every positional bin
  `±0.5`. (`configs/align/v4/r0_nll_reference.json:18-21`)
* `validate_references` rejects a bad schema, target/bin dimensions, missing or
  ambiguous identities, non-finite/bool numeric fields, malformed reference
  profiles, and a wildcard absolute entry beside another entry of the same
  revision. (`joulewise/align/r0.py:219-276`)
* `nll_verdict` requires exactly 2,048 losses, applies both inequalities
  inclusively, reports both failure reasons when applicable, and also applies a
  pinned reproduction tier when present. An unknown revision/fixture has no
  absolute fallback and returns `no_reference`.
  (`joulewise/align/r0.py:299-350`)
* The MLX path teacher-forces `ids[start:end]` against
  `ids[start+1:end+1]` through a single cache in 128-token chunks, evaluates
  losses and cache state, and verifies the returned target count.
  (`joulewise/align/r0_mlx.py:143-161`)

## Fail-closed audit

The executing tests cover malformed tables, a bad entry poisoning the whole
table, exact identity mismatch, empty/wrong-count vectors, NaN/Infinity,
positional bin permutations, absolute-wildcard ambiguity, unresolved schema
references, unknown/wrong tools, invalid arguments, malformed/multiple/no tool
envelopes, and endpoint failures. Load failure reasons combine NLL and
generation failures instead of masking either one.

The newly found edge was not a false pass—the runner failed—but it lost the
scientific reason and exposed a serialization-dependent outcome. The repaired
`loss_profile` first performs the original sum, so normal results retain the
same floats and bytes; only overflow invokes divided-term averaging. It emits
`None` rather than a non-standard JSON number if even the fallback cannot
produce finite aggregates. (`joulewise/align/r0.py:151-171`)

## Generation-check audit

The check deterministically requests the listed SHADE tool having the fewest
required parameters (name breaks ties), renders the real benign system prompt
plus the explicit one-call user instruction, and validates the parsed call
against that requested tool's schema. Exactly one attempted envelope and one
parsed call are required. (`joulewise/align/r0.py:353-396`)

Attempt 1 creates a sampler-free session and decodes greedily. Only `hit_cap`
or `unclosed_reasoning` triggers attempt 2; it creates the production-sampler
session and uses seed **96**. The second attempt decides, and the loop-free
implementation permits exactly one retry. Both attempts remain in the report.
(`joulewise/align/r0.py:399-447`) The MLX seam enforces agreement between the
session sampler and the `greedy` argument, passes temperature `0.0`/seed `None`
for greedy, and the production temperature/seed otherwise.
(`joulewise/align/r0_mlx.py:92-102,119-130`)

## Report serialization audit

`save_report` uses `allow_nan=False` and temporary-file replacement for both
JSON and Markdown. During a check, a serialization error clears the offending
row, records `report_serialization_error`, and preserves a final rather than
`running` receipt. (`joulewise/align/r0_runner.py:95-103,126-164`) The finalizer
always adds census, duration, and finish time before saving.
(`joulewise/align/r0_runner.py:268-276`)

The regression specifically exercises the full runner and parses the on-disk
JSON with a constant hook that fails on `NaN` or `Infinity`. The companion
happy-path regression constructs the legacy profile independently and compares
the sorted serialized JSON byte-for-byte.

## Commands and measured results

* `python3 -m unittest tests.align.test_r0_load_reference tests.align.test_r0_load_reference_adversarial tests.align.test_r0_mlx` — **57 tests, OK** after the fix.
* `python3 -m unittest discover -s tests` — **incomplete**: the repository-wide
  suite was still running its long synthetic calibration tests after more than
  25 minutes and was manually interrupted in
  `tests.align.test_moe_calibration.MoeCalibrationTests.test_lane_12_groups`.
  No failure had been reported before interruption; this is not counted as a
  pass.

