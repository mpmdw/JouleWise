# RC-CMP-OPUS-REV-2: delta review of RC-CMP-3 (3bf93b25e..e5ccf720b)

Seat RC-CMP-OPUS-REV-2 (gate policy rule 3, Opus half). Branch `review/2026-10-28-rc-cmp-opus-rev-2` from
e5ccf720b. Synthetic fixtures only. No block-5/6 or BYTES data was opened or searched for. `/usr/bin/python3.13`
(3.13.17), `TMPDIR=/tmp/rcopusrev2`. L9's full-size `test_dry_run` was not run.

**VERDICT: ACCEPT_WITH_FIXES on e5ccf720b.** Every probe from both reviews now refuses or DISAGREEs. The meter fit
matches the parser exactly (0 ns, same envelope) on 580 new adversarial streams. The fix added three narrow
false-agreement paths (N1-N3, all MINOR). Each needs only a few lines. Fix them before the comparator binds block 5's
release. None of them blocks the A6 full-size rerun.

Suite: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 205 tests in 180.709s OK (skipped=18)`, exit 0 (`rc-cmp-opus-rev-2/suite.out`).

Probes are in `.codex-report/rc-cmp-opus-rev-2/`, each with its `.out`. Run them from the repo root with
`TMPDIR=/tmp/rcopusrev2 PYTHONPATH=.:tests PYTHONDONTWRITEBYTECODE=1 python3.13 <probe>`. To rerun the earlier
reviews' probes, first extract their directories (untracked) with
`git archive origin/review/2026-10-28-rc-cmp-{sol,opus}-rev .codex-report/rc-cmp-{sol,opus}-rev | tar x`.

## Findings (ranked)

**N1 (MINOR). A NaN or Infinity in a step-11 leaf passes when an `uncovered:` rule covers that leaf**
(`scripts/compare_b5_recompute.py:193` reads it as null; `:1154-1156` lets `uncovered:` rules take non-numbers; exit
code at `:1249-1253` ignores structure flags). X7 turns NaN into null, and X6 only sends *numbers* past an
`uncovered:` rule. So a nonfinite printed value now matches a word-only catch-all and exits 0. The flag shows only
as the count `structure_flags=1`. `probe_delta.out`:

```
N1a control: number under fill:campaigns catch-all: exit=2 stderr='refused=step11_unmapped_fill'
N1b NaN under fill:campaigns catch-all: exit=0 stderr='' fails={} unbound=[] flags=['nonfinite_value_read_as_null']
N1c Infinity printed as a J contrast's j_per_token: exit=0 stderr='' fails={} ... flags=['nonfinite_value_read_as_null']
N1d NaN under an uncovered-by-name rule: exit=0 ... uncovered_numeric lists it: False
```

In practice the exposure is narrow: a mapped leaf bound to a NaN row still refuses. **Fix:** refuse (exit 2) when a
`nonfinite_value_read_as_null` flag comes from a step-11 source. Or treat a leaf read from a nonfinite token as
numeric in `coverage()`.

**N2 (MINOR). Two comparison rows share one key, and coverage binds to the wrong one.** The floor cell
(`compare_floors :344`) and the dominance ratio whose `component` is `absolute`/`comparative`
(`compare_aggregate :385`) both emit `count:<model>/<phase>/<kind>/n`. `coverage()` keeps the first row
(`:1142` `setdefault`), so the rule `block_lines/dominance_ratio/n → {ratio_label}/n` binds to the floor cell's n.
`probe_delta.out` (ratio n = 7 on both sides, floor n = 9):

```
N2 duplicated row keys: [('count', 'Qwen3-1.7B-4bit/decode/absolute/n')]
N2a ratio line prints the floor cell's n=9 (ratio n is 7 on both sides): exit=0 fails={} unbound=[]
N2b ratio line prints the correct ratio n=7: exit=2 ... ('disclosure:block_lines/dominance_ratio/n', 'value_differs')
```

So the wrong value passes and the right value refuses. This only matters when a ratio's n differs from its floor
cell's n. **Fix:** give the ratio rows their own key prefix (for example `ratio/{label}/n`). Also make `coverage()`
refuse when two rows have the same (family, key); a duplicate key is a structure fault.

**N3 (MINOR). The central band's window is taken from L9 even when the recompute chose a different one, or none**
(`:833`). The recompute derives its own first clean window
(`scripts/independent_recompute_b5.py:2087-2097`). The comparator reads that window only when L9 prints no band. So
if L9 picks the wrong window, or prints a band where the recompute finds no clean window, the comparator agrees.
`probe_delta.out`:

```
N3a recompute sets no central band, L9 prints one: {} []
N3b recompute's band is BETA's, L9's is alpha's: {} []
```

The line is a diagnostic that never enters a claim number (PLAN §8.2 item 5). RC-CMP-3 decision 5 says the clean
window "is not re-derived", but the recompute does re-derive it. **Fix:** compare the band's window exactly: L9's
`central_band.pack` against the recompute's band pack, and DISAGREE when only one side sets a band.

## Answers

1. **Prior probes: all now fail.** `prior_probes_rerun.out`.
   - **Opus probes.** P1b, P2 and P3 refuse with `unmapped=[…estimate]` / `[…claim_evaluation/outcome]`.
     P4 gives `contrast_j: 8`, P5 `run_phase_energy_j: 3` and P6 `floor_j: 24, count: 4`. P7 refuses
     `bars_family_missing:rho` under the coded bars, and `test_meter_line_absent_from_l9_disclosure_p7` covers the
     release bars. P8 and P8b refuse `bars_invalid:contrast_j`. P9 gives `outcome_word: 2`. P12 refuses with all
     four leaves unmapped. `probe_meter_fit` gives `max|host diff|=0 ns` at 0, 1e15 and 4e15, and 0 near-tie hits.
     `probe_streams` gives `restricted written for NaN case: True`.
   - **Sol probes.** `wrong_fill_cli 2`, `wrong_machine_median {'rho': 1}` and `_cli 2`. Then `missing_l9_run_cli 1`,
     `extra_recompute_run {'run_phase_energy_j': 3}` and `missing_harvest_member_cli 2`. `missing_harvest_machine`
     gives `{…meter_j: 2…}` and `no_harvest_meter {'meter_j': 1, 'rho': 1}`. `infinite_override` refuses
     `bars_invalid:contrast_j`.
   - **How the Sol comparator probe was run.** The original stops at its `infinite_override` line with that
     traceback, so I ran a copy with only that call guarded (`sol_probe_comparator_guarded.py`).
   - **Sol meter probes.** `probe_meter_stream differences_ns= [0, 0, 0]`, `probe_meter_fit largest 0`, and
     `probe_meter_short` 0 at 1e15, 1e16 and 1e17.
   - **Still as designed.** `public_counts_before/after` still shows the pass/fail flip, which is the lead's ruling.
     The archive probe still stops with `trace_plist_missing`, as required.
2. **New false-agreement paths: N1-N3.** What I checked and found holding:
   - **Context inheritance.** On the fixture, every key-bound leaf takes its ids from its own line item. The only
     outer id it inherits is the line's `contrast_id`, read by `magnitude_per_token/{metrology,decision}`, which is
     correct.
   - **The arm-gate binding.** It reads only the model substring (`qwen3-1p7b`/`qwen3-8b`) of
     `condition_family_id`, and the phase from the contrast id. An id with neither tag gives `key_unresolved`, which
     refuses.
   - **Union.** Every family in `run()` takes the union of keys (P4-P7 and Sol's probes confirm it).
   - **Summary definitions.** These match L9's producer (`6af08b780:joulewise/b5_analysis/disclosures.py:663-679`):
     median, min and max over all finite ρ; q25/q75 by `percentile`; the spread and the band over plausible members,
     with the same plausibility rule.
   - **`uncovered-by-name:` subtrees.** I read the broad ones. `fill …/(conditions|metric|equivalence)` carries only
     registered definitions (for example the equivalence margin and method). `neg8_allowance/values_j/.*` carries
     internals besides the seven bound terms.
   - **One-sided null in a mapped row.** It still DISAGREEs (`nonfinite_or_null` all DISAGREE). A one-sided null
     passes only through N1.
3. **Meter fit: exact.** `probe_meter_adversarial.out` covers 12 families and 580 streams, comparing host times and
   the parser's second `_linear_fit` points. The families: origins at 9e18 ns and at 2^53+12345 ns, exact
   residual ties with no jitter at 1e16, RTTs straddling the 3 ms cap, n straddling 63, negative RTTs, shuffled rx
   order, duplicated polls, 40 s device gaps across the 65 536 ms wrap, 19-poll fallback, two-poll streams, and
   −80 ppm drift at 4e15. Every family gives `max_host_diff_ns=0` and `same_env` for every stream, with no
   non-comparison.
4. **Over-refusal on real shapes.** These risks are real, but each one fails closed:
   - **(a) RC-CMP-3 OPEN ISSUE 1, the step-11 map.** Any field L9 writes that the map does not name refuses.
     *Evidence that would settle it:* the A6 full-size comparison at e5ccf720b (or the N1-N3 fix head), with the
     public line showing `step11_unmapped=0`. Also `coverage.unbound` reasons from the restricted output, which give
     paths and reasons and no values.
   - **(b) OPEN ISSUE 2, the equal-member-set rule.** The recompute's `whole_machine` members are the collected
     roster. L9's members are `withheld/meter.json`'s `members` (L9 producer `:639`). These can differ by design
     when a collected member has no meter row. *Evidence:* from the A6 restricted output, the per-window counts of
     member ids on each of the three sides and the names of their set differences. That is structure only.
   - **(c) The N2 collision.** It refuses correct data whenever a ratio's n differs from its floor cell's n.
     *Evidence:* whether L9's ratio-table `n` is defined as the floor cell's n (`closeout.ratio-table` producer), or
     the A6 `unbound` list.
   - **(d) Strict type equality in `same()`.** An int printed where the compared row is a float refuses
     (`test_integer_printed_for_a_float_refuses`). The one rounded value I checked is fine: `rounded_t` is
     `_ci_t_critical(n-1)`, the same float as `t_critical_95` (`6af08b780:joulewise/analysis_engine/estimators.py:224`,
     `disclosures.py:540`), so it binds.
   - **(e) `machine_summary` model words.** Non-science members take `_meter_member_model`'s identifier in L9. If
     the recompute's member `model` uses another spelling, the union splits the group, and both sides DISAGREE.
     *Evidence:* the A6 `machine_summary/<pack>/<model>` row keys.

## Handoff

Files changed: this report and `.codex-report/rc-cmp-opus-rev-2/` (probes, outputs, suite log). No production file
was edited. Next step for the lead: fix N1-N3, then rerun A6 to settle answers 4(a)-(c).
