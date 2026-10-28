# RC-CMP-OPUS-REV — executing review of RC-CMP-1 and RC-CMP-2

Seat RC-CMP-OPUS-REV (gate policy rule 3, Opus half). Reviewed: `lane/2026-10-27-recompute-comparator`
`9ca87bcee..3bf93b25e`. Branch `review/2026-10-28-rc-cmp-opus-rev`. Synthetic fixtures only. No block-5/6 or BYTES
data was opened or searched for. Interpreter `/usr/bin/python3.13` (3.13.17), `TMPDIR=/tmp/rcopusrev`.

**VERDICT: ACCEPT_WITH_FIXES.** The suite passes, the bars are not widened, the streams are blind and the scripts are
independent. The comparator can still report agreement while a printed step-11 value differs (F1, F2). The meter fit
is not bit-for-bit the parser definition (F3). Fix F1-F3 before the comparator binds block 5's release.

Suite: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/independent_recompute -t .`
gives `Ran 165 tests in 97.653s OK (skipped=18)`, exit 0 (`rc-cmp-opus-rev/suite.out`).

The probes are in `.codex-report/rc-cmp-opus-rev/`. Each has its captured `.out`. Run them from the repo root with
`TMPDIR=/tmp/rcopusrev PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/rc-cmp-opus-rev/<probe>.py`.

## Findings

### MAJOR

**F1. Step-11 coverage checks membership by value, not by key, so a wrong printed value passes**
(`scripts/compare_b5_recompute.py:689-718`, decision at `:714`). A mapped fill or disclosure leaf counts as covered
when its value equals any L9-side value that its family (or, for the `NUMBERS` rule `:664`, any of ten families)
compared, under any key. The fill input is never compared directly, only through this check. RC-CMP-1 decision 4
claims the check "catches an adapter that copies the wrong number". It does not catch swaps or cross-field copies,
and a small word or integer vocabulary makes coincidences near-certain. `probe_comparator.py`, shipped `COVERAGE`:

```
P1b fill swaps two contrasts' estimates, shipped COVERAGE rules: exit0=True fails={} unmapped=[]
P2  fill prints another field's value (s_d) as the estimate, COVERAGE: exit0=True fails={} unmapped=[]
P3  fill outcome words 'L1' and null (truth not_resolvable), COVERAGE: exit0=True fails={} unmapped=[]
```

In P3, `"L1"` passes because the ceiling `L1` is a compared outcome word. Null passes because `scalar_key(None)`
equals the compared direction `"none"` (`:682-683`). **Fix:** bind each mapped leaf to the comparison key it copies,
for example contrast id plus field from the sibling `contrast_id`, or a rule that names the key template. Require
`l9 == leaf` for that row, and also require the row to be AGREE.

**F2. Families are compared only over L9's items; an item on the recompute side only is never compared**
(`compare_runs :192`, `compare_floors :233`, `compare_contrasts :304`, `compare_sensitivity :423-435`,
`compare_machine :537-539`). When L9 omits an item, the family still shows `fail 0`:

```
P4 contrast present on the recompute side only: exit0=True fails={} unmapped=[]
P5 run present on the recompute side only (no L9 rereduced file): exit0=True fails={} unmapped=[]
P6 L9 extraction report with no cells (recompute has floors): exit0=True fails={} unmapped=[]
P7 meter line on recompute + harvest record, none in L9 disclosure, --harvest-meter given: exit0=True fails={} unmapped=[]
```

P4 to P6 would usually show up further downstream, through Holm-adjusted p and the floors. P7 would not:
`compare_machine` `continue`s before it looks at the harvest record (`:538-539`). A whole-machine line dropped by L9
therefore passes silently, even though the recompute and the withheld record both carry it. **Fix:** for each family,
take the union of L9 keys and recompute keys, and record a key missing on either side as `missing_or_null`. For the
meter line, require L9's members to cover the members of `whole_machine.windows[*]` and of the harvest record.

**F3. `meter_clock_fit` takes first-pass residuals in absolute host ns, not relative to the first point as
`km003c_parse.clock_fit` does** (`scripts/independent_recompute_b5.py:1509`, against the parser's
`xs/ys = p - used[0]`). Rounding at CLOCK_MONOTONIC_RAW magnitudes (about 0.1-0.5 ns at 1e15-4e15 ns, i.e. 12-46
days of uptime) can flip the bin minimum between two near-tied polls. The envelope then runs through a different
point, and the host times move by tens of µs. `probe_meter_fit.py`:

```
A offset=1e+15ns: max|host diff|=1 ns; seeds >1ns or refused: 0 []        (shipped 240-seed generator, shifted)
A offset=4e+15ns: max|host diff|=1 ns; seeds >1ns or refused: 0 []
B planted near-ties: 55 streams with |host diff| > 1 ns
  base=1e+15 seed=26 target=-0.3 parser_residual_gap_ns=-0.0602 max_host_diff_ns=71838
B hits by base: {'1e+15': 15, '4e+15': 40} of 200 streams per base   (0 of 200 at base 1e12)
B with relative coordinates in the recompute fit: 0 of 55 still differ by > 1 ns
```

The probe's stream has a latency trend, so the first-pass slope differs from the envelope slope. A near-tie inside
0.1 ns needs two in-bin floor polls whose residuals coincide. That is rare with ns-jittered stamps, but RC-CMP-2's
"within 1 ns" property is false in general, and the 240-seed test only uses base 1e12 ns. The effect is a false
DISAGREE or a `meter_request_mismatch`, not a false agreement. **Fix:** compute the residuals (and
`max_above_envelope_ns`) on `x - origin`, `y - pairs[0][1]`, exactly as the parser does. Re-run
`test_meter_fit` with a base of at least 1e15 and with a planted near-tie case.

### MINOR

**F4. Per-key overrides are not validated** (`compare_b5_recompute.py:90-92`; used by `family_spec :98`). A
family-level `Infinity` is refused, but the same value in `keys[]` is accepted, and so is a negative
`printed_decimals`:

```
P8  per-key override absolute=Infinity accepted by load_bars (planted D_j=1e9): exit0=True fails={} unmapped=[]
P8b per-key override printed_decimals=-9 accepted (planted D_j=1e8): exit0=True fails={} unmapped=[]
P8c control: family-level Infinity: REFUSED bars_invalid:contrast_j
```

No shipped bar file has overrides today (only the test S-13 file does), so this is a hole in a config guard, not a
live widening. **Fix:** apply the same finite, non-negative and int checks to every override.

**F5. Catch-all uncovered rules swallow numeric leaves** (`:626` `disclosure:window_lines/.*`, `:650`
`fill:campaigns/.*`, `:652` `fill:characterization/.*`). A new energy leaf in those subtrees is listed as
uncovered without anyone seeing it (P12: `meter_energy_j`, `values/rho`, `campaigns/gamma/gross_energy_j` and
`characterization/delta_j` were all reported "uncovered"). **Fix:** limit the catch-alls to non-numeric leaves, or
refuse a numeric leaf under them unless an explicit uncovered rule names it.

**F6. A NaN or Infinity anywhere in L9's restricted JSON aborts the comparator with no restricted output**
(`:765`, `allow_nan=False`): `comparator-l9-nan: exit=2 ... stderr: error=internal ValueError`, and the restricted
output was not written (`probe_streams.out`). It fails closed, but the reviewer gets no row explaining why. **Fix:**
sanitise non-finite values to null in the restricted copy, as the recompute does with its `nonfinite_value` flag.

**F7. Window edges are compared exactly under `count`** (`:572-573`). The coded 7e322b76 rule compares exactly only
for `window_basis == "controller_stamps"`, and allows 1e-6 s for a legacy wall placement. A legacy-basis archive will
DISAGREE spuriously. That is a readiness risk, not a false agreement.

### NIT

**F8.** `exact()` uses `==` (`:130`), so `True == 1 == 1.0` agrees (P9: `exit0=True`). Compare `(type, value)`.

**F9.** `MeterStream` does not check `header.status == "streaming"` (the parser treats any other status as absent),
and it drops a whole batch on a payload/count mismatch where the parser decodes it. Both cases are malformed or
absent streams, so they only turn a comparison into a non-comparison.

## Answers

1. **False agreement: yes.** F1 covers wrong printed fill or disclosure values that pass by key-free value
   membership (P1b, P2, P3). F2 covers values present on the recompute side only (P4-P7), including the meter line
   when `--harvest-meter` is passed but L9 omits the line. F4 covers per-key overrides that accept an infinite bar.
   F5 covers leaf classes that are silently uncovered. What holds: NaN, inf and None on either side give DISAGREE
   (P10). A numeric family absent from the bars refuses (P11: `bars_family_missing:count`), and so do the meter
   families once used (the test suite). Without `--harvest-meter`, a disclosed meter line gives DISAGREE
   (`test_missing_harvest_record_disagrees`).
2. **Meter clock fit: not exactly.** Eligibility (`n<63`, RTT `<3` ms, negative RTT eligible), the fallback below
   20, the rx-stable sort, the bin count, width and origin, first-on-tie, the envelope fallback, duplicates and
   samples-less polls all match `km003c_parse.clock_fit`/`parse`. The coordinates of the first-pass residuals do not
   match (F3). A stream with a per-sample difference above 1 ns exists: up to 71,838 ns (`probe_meter_fit.out`).
   Also, the recompute alone refuses `b<=0`, which only turns a comparison into a non-comparison.
3. **Blinding: no leak found.** Both CLIs ran under an audit hook on the synthetic machine archive and the comparator
   fixture (`probe_streams.out`). The only number-like tokens on the streams were in the sha256 hex and the bar-set
   name; the interpreter version is the only decimal. An exception carrying "energy 123.456 J p=0.0371" prints
   `error: internal ValueError`. Refusal strings are fixed codes. The public counts are counts of comparisons, runs
   and STRUCTURE flags. The recompute's stdout `sha256=` is a digest of the restricted output: a commitment, not a
   value.
4. **Independence: yes.** The audit hook logged imports, opens, exec and compile. Neither script touched
   `joulewise/b5_analysis` or `joulewise/external` (`l9_or_parser_touched=[]` for all four runs). The imports are
   stdlib only. The recompute reads `configs/campaigns/v5_claim_25g83/flag_catalog.json`, which is data, not L9 or
   parser source.
5. **Bars: equal, none widened.** Eleven families are equal to `bar_sets/recompute_coded_7e322b76.json`, and
   `meter_j`, `meter_w` and `machine_j` (1e-6 rel/abs) and `rho` (1e-6 abs) were added. Against the code at
   `7e322b76` (`agrees()`: `max(1e-6, 1e-6|x|)`, and 1e-6 absolute for rho): `count` (exact) and `b_op_s` (relative
   only) are narrower, not wider. The window edges are narrower too (F7).
6. **Real-data readiness.** Desk-compressed `.zst` plists raise `trace_plist_missing` (STOP), so the archives must
   go through `scripts/restore_run_to_scratch.py` first, and the comparator then shows DISAGREE, not agreement. A
   `.zst` meter stream gives `meter_absent`. Gaps over half a wrap use the same host-time wrap rule as the parser.
   Long uptime triggers F3. Legacy window bases trigger F7. NaN in L9 JSON triggers F6. More than one
   `disclosures/<sha>.json` in custody becomes a single DISAGREE (`:462-466`), and an extra sensitivity-labelled
   record is ignored (`:417`). BETA extra sessions (`--extra-beta`) are not compared by the comparator at all; they
   are disclosure-only. Missing optional records (an extraction, aggregate, projection or bracket file) give
   DISAGREE rows, except where F2 applies.
