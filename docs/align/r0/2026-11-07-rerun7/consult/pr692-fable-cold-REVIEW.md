VERDICT: ADMIT_WITH_FIXES

Cold executing review of `fix/2026-11-07-r0-smc-coverage-cell` (3c0b71b24 over e1a91226e), worktree
/Users/edr/code/jw-wt/r0-smc-cov. Scratch: /Users/edr/night-archive/r0-smc-cov/fable/ (scripts
`run_real.py`, `real_offsets.py`, `adversarial.py`, `advlib.py`, `adversarial2.py`, `host_receipt.py`;
output `rank_real_r0.json`). Read only the cold brief and my own directory.

Summary: the diff itself is correct. `Coverage` gains a validated `tolerance_ns` keyword whose default
is unchanged, `rank` counts one cell per reading at half a period, the real capture goes from 403
record-only keys to a resolved pair, and no capture the production sampler can produce passes the 99%
bar when it should not. The required fix is outside the diff but on the path the brief asks about: the
R0 host receipt (`joulewise/align/r0_host.py:484-496`, called by `r0_runner.py:230`) re-checks the
selected keys against the whole-capture `coverage` block that `scripts/align_smc_enumerate.py:130`
still writes at the 100 ms default. Executed on the real capture, that receipt stays `inconclusive`
("SMC selected-key coverage does not meet 1 Hz / <1% errors / 10 min") after this fix. Re-arming R0 on
this branch alone reproduces the refusal.

## 1. Tests (brief step 1)

The first run imported the wrong tree: the agent harness resets cwd between calls, so after the
standalone `cd` the `-m unittest` run put /Users/edr/code/JouleWise first on sys.path and
`joulewise.align.apple.thermal` resolved to the custody checkout
(/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/joulewise/...), which
has no `tolerance_ns` (`TypeError: Coverage.__init__() got an unexpected keyword argument
'tolerance_ns'`, 11 errors in test_thermal_coverage, 1 failure + 2 errors in test_smc_classifier_v4,
4 in test_thermal_gate, 2 in test_thermal_desk). Confirmed with:

    PYTHONPATH=<wt> <python> -B -c "import joulewise.align.apple.thermal as t; print(t.__file__)"
    -> .../night-custody/.../thermal.py           (without PYTHONSAFEPATH)
    -> /Users/edr/code/jw-wt/r0-smc-cov/joulewise/align/apple/thermal.py   (PYTHONSAFEPATH=1)

With `PYTHONSAFEPATH=1 PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov <python> -B -m unittest
tests.align.<module>`, each in its own process:

    test_smc_classifier_v4   Ran 6 tests   OK
    test_thermal_coverage    Ran 5 tests   OK
    test_smc_selection       Ran 9 tests   OK
    test_smc_quiet           Ran 19 tests  OK
    test_r0_host             Ran 44 tests  OK
    test_thermal_gate        Ran 31 tests  OK   (7.1 s)
    test_thermal_desk        Ran 21 tests  OK

Not a defect of the branch; recorded so the lead's own reproduction does not trip on it.

## 2. Real capture through the branch `rank` (brief step 2)

`run_real.py`: inventory/phases/started/finished from
/Users/edr/night-align/r0-v4-20261107T0810Z/smc/r0.json, 1,800 rows from samples.jsonl.

    n samples 1800 (idle 300, load 900, recovery 600); total read errors 0
    start-to-start ms: median 1002 min 850 max 1298
    read duration ms:  median 86   min 79  max 392
    r0: status pass  classes {record-only: 246, die: 16, heatsink: 141}
        selection {s_fast: Tg2I, s_slow: TaRT}   select_keys -> same
        phase_coverage: 1.0 in idle, load and recovery for all 403 keys
        reasons: 131 not in class, 115 constant/stale idle, 16 die, 141 heatsink
        Tg2I die: rise 88.60 degC, t63 2.88 s, t63_end 2.10 s, tau 1.68 s, noise 10.24
        TaRT heatsink: rise 4.10 degC, t63 50.9 s, t63_end 140.8 s, tau 123.1 s, noise 1.14
    r1: identical counts and selection

Old tolerance replicated through the real `rank` (mock `Coverage` to NS // 10, `real_offsets.py`):
status inconclusive, 403 record-only, phase_coverage idle 0.120 / load 0.289 / recovery 0.220, which
is the brief's 12-29%.

Why the real data fails at 100 ms and passes at 500 ms (`real_offsets.py`, stamp = read midpoint,
offset to the nearest tick of the phase's own grid):

    idle     offset ms: min 44 p5 85 median 173 p95 219 max 222; distinct cells 300; stamps sharing a cell 0
    load     offset ms: min 41 p5 49 median 153 p95 191 max 196; distinct cells 900; sharing 0
    recovery offset ms: min 51 p5 73 median 142 p95 216 max 222; distinct cells 600; sharing 0
    stamp-to-stamp gaps > 1.5 s: 0 in every phase

Every reading sits in its own cell with 278 ms of margin (500 - 222) to the cell boundary. Each phase's
grid is its first reading, which `collect()` starts at the phase origin (first start - span_start = 0 ms
in all three phases), so the arithmetic edges are exact: first=0, last=300/900/600.

## 3. Findings, ranked

### F1 (high; fix before re-arming): the host receipt still refuses the real capture

`r0_runner.py:230` runs the SMC step through `r0_host.smc_enumeration`. After `rank` passes, that
function requires, for each selected key, `payload["coverage"]["per_key"][key]` to have
`valid / expected > .99` (r0_host.py:484-491). `payload["coverage"]` is written by
`scripts/align_smc_enumerate.py:130` as `temperature.coverage(samples, started, finished, selected)`,
which constructs `Coverage(start_ns, selected)` with the default 100 ms over the whole 1,800 s
capture. The diff does not touch it. Executed on the real payload (`host_receipt.py`):

    rank selection {s_fast: Tg2I, s_slow: TaRT}  readability_bar_met True  resolved True
    stored r0.json coverage block tolerance_ns = 100000000
      per_key[Tg2I] expected 1800 valid 36 fraction 0.0200 -> FAILS > .99
      per_key[TaRT] expected 1800 valid 36 fraction 0.0200 -> FAILS > .99
    r0_host.smc_enumeration receipt would be: inconclusive:
      'SMC selected-key coverage does not meet 1 Hz / <1% errors / 10 min'

So the concrete real capture r0-v4-20261107T0810Z gives a wrong fail at the receipt that the runner
records, with this branch merged. The branch's own `Coverage` at NS // 10 reproduces the stored block
exactly (36/1800), confirming other callers are unchanged.

Switching the script's whole-capture block to NS // 2 is not the fix. The three phases start at
0.117 s, 300.443 s and 1200.614 s after the capture origin, so against a single capture-wide grid the
stamps straddle the half-period boundary:

    whole-capture coverage at 500 ms: expected 1801 valid 1631 fraction 0.9056 (Tg2I and TaRT 1631/1801)
      idle     stamp offset to whole-capture grid ms: min   44 median  173 max 222
      load     stamp offset ms:                       min -499 median  381 max 500
      recovery stamp offset ms:                       min -452 median -360 max -280

The per-phase computation `rank` already does is the consistent quantity (per-phase `Coverage` on each
phase's own grid, which is what `classification["ranking"][i]["phase_coverage"]` holds). The receipt
should take its readability from that, or from a per-phase `Coverage` built the same way, instead of
the capture-wide block; the 99% bar itself is pre-existing and I am not proposing a different one.
`markdown()` in the script also prints "Complete-sensor sample fraction: 0.02" into summary.md beside a
passing response; whatever the receipt reads, the summary line should print the same quantity.

Why the suite did not catch it: `tests/align/test_r0_host.py:test_smc_missing_and_present_hook` feeds
`write_capture(...)`, a synthetic payload whose coverage block is already full; it only checks that
zeroing one key's `valid_samples` flips the receipt. A test that runs production-shaped jitter (the
0-150 ms lateness, 50-400 ms reads of `jittered_capture`) through `temperature.coverage()` plus the
receipt would have failed on this branch.

### F2 (medium, flag not refuse): what the half-period bar does and does not catch

`adversarial.py` and `adversarial2.py` build captures in the branch's own two-sensor world and run the
real `rank` at both tolerances ("NEW" = branch, "OLD" = NS // 10 via mock). Load-phase coverage of
TDIE shown; other phases 1.0 unless stated.

    #  scenario                                                     NEW cov   NEW status     OLD cov  OLD status
    1  regular 1 Hz, 100 ms late                                    1.0000    pass           1.0000   pass
    2a 9 isolated 2 s gaps (drop 9 of 900)                          0.9900    pass           0.9900   pass
    2b 10 isolated 2 s gaps                                         0.9889    inconclusive   0.9889   inconclusive
    3  reader stalled 30 s                                          0.9667    inconclusive   0.9667   inconclusive
    4  bursts of 3 reads in 300 ms then 2 s holes, every 10 s       0.8000    inconclusive   0.8000   inconclusive
    5a 4 reads of 1.2 s                                 cov .9956 err .0044   pass           same     pass
    5b 9 reads of 1.2 s                                 cov .9900 err .0100   inconclusive   same     inconclusive
    8  due-grid sampler, measured jitter, one 1.3 s stalled read   0.9978 err .0011 pass    0.4472   inconclusive
    9  due-grid sampler, reads 700-950 ms                           0.7922    inconclusive   0.0000   inconclusive
    10 due-grid sampler, lateness 80-480 ms                         1.0000    pass           0.4672   inconclusive
    11 due-grid sampler, lateness 80-600 ms                         0.8156    inconclusive   0.0567   inconclusive
    16a due-grid, 8 reads of 1.05 s (each skips a tick)   cov .9822 err .0090  inconclusive  0.3437   inconclusive
    16b due-grid, 10 reads of 1.05 s                      cov .9778 err .0112  inconclusive  0.3437   inconclusive
    14a branch jittered_capture                                     1.0000    pass           0.2422   inconclusive
    14b jittered_capture minus 9 of 900 load ticks                  0.9900    pass           0.2389   inconclusive

Every genuinely missing reading costs exactly one cell at 500 ms, the same as at 100 ms on aligned
data (2a/2b, 3, 4, 5a/5b identical at both tolerances). The 99% bar admits up to 9 missing load cells,
3 idle, 6 recovery; that is the pre-existing bar, not this change. Reads over one second are dropped
by `observe` and counted as read errors by `rank` (5a/5b), and a `collect()` read that finishes past
the next due skips a tick, which shows up as one empty cell plus one error (16a/16b). A reading more
than 500 ms late lands in the next cell and doubles there, leaving its own cell empty (11): the bar
degrades one cell per late reading, never silently.

The definitional limit, executed (`adversarial2.py`):

    6b +400 ms slip of every stamp from t=700 (one 1.40 s gap, then 1 Hz)     NEW 1.0000 pass   OLD 0.4444
    6c +456 ms slip (stamp offset 499 ms; one 1.456 s gap)                     NEW 1.0000 pass   OLD 0.4444
    6d +457 ms slip (stamp offset 500 ms, tie rounds forward)                  NEW 0.9989 pass   OLD 0.4444
    7b two readings 2 ms apart straddling each cell boundary, every 2 s        NEW 0.9989 pass   OLD 0.0011
       (899 readings, max start-to-start gap 1.998 s)
    7c two serialised 86 ms reads straddling each boundary, every 2 s          NEW 0.9989 pass   OLD 0.0011

A cell bar is phase-agnostic inside the cell: a one-off slip of up to 456 ms on the stamp (a single
gap of up to 1.456 s) keeps every cell filled, and a pathological reader that fires two readings
either side of each boundary every two seconds reports 899/900 while leaving 1.998 s between data.
Neither can come out of `collect()`: `due` advances by whole seconds from the phase origin, a read is
never started before the next whole second (min start-to-start on the real data 850 ms), and a read
that finishes past the next due skips that tick (16a). So on the sampler this bar is attached to, the
old 100 ms tolerance was protecting against nothing these captures show, and the new one loses no
real catch. I record it because `Coverage(tolerance_ns=NS // 2)` is now a general facility: any future
caller feeding it a free-running or bursty reader inherits this property. `report()` still computes
`gaps_ns` (now only intervals over 1.5 s) and `max_interval_ns`, and `rank` ignores both; they are the
existing quantities that would see 7b/7c if a caller ever needed them. No new bar proposed.

### F3 (low): edge cells and boundary snapping at 500 ms behave, and are stricter than before

At NS // 2, `boundary()` snaps every edge (no stamp is ever more than half a period from a grid
point; a tie at exactly NS/2 rounds forward via `nearest()`), so an edge cell of at least half a period
is counted as an expected cell and one shorter than half is dropped. Executed:

    12 first load reading 0.6 s after span start, then 1 Hz (899 readings)   NEW 0.9989 (cell -1 expected, empty)   OLD 1.0000
    12 first load reading 1.6 s after span start (898 readings)              NEW 0.9978                               OLD 0.9989
    13 every load reading at +600 ms (grid shifts; last stamp at 1199.643)   NEW 0.9989 (cell 900 excluded)          OLD 1.0000
    15 load span_end 1200.0 / 1200.49 / 1200.5 / 1200.51 with grid 300.1     load 1.0000 in all four; the moved
       recovery start cost its first cell (0.9983) identically at .49/.50/.51, so the tie is deterministic

A late first reading is now counted as a missing second (the old rule dropped that partial cell and
reported 1.0); that is the right direction. The real capture has first start - span_start = 0 ms and
last stamp 904-950 ms before span_end in every phase, so none of this moves the real number. Nit: the
`Coverage` docstring still says "Partial edge cells are excluded"; at the 500 ms setting that is true
only for cells shorter than half a period, and a half-period-or-longer partial cell is expected and
empty. One clause in the docstring.

### F4 (number rule, separate dimension)

Derived, and I checked the arithmetic:
- `NS // 2` in `rank`: half a period is the unique tolerance at which each stamp belongs to exactly
  one 1 s cell; the comment says so. The validation bound `(0, NS // 2]` follows (above half a period a
  stamp is within tolerance of two ticks). The `ValueError` text states the bound without the reason;
  one clause would make it self-carrying.
- Test world: 0-150 ms lateness and 50-400 ms reads are the measured shape (real: start lateness up
  to 150 ms against the phase grid, reads 79-392 ms). t63 delta 1 s = one sample period. t63_end
  delta 3 s: 1 s + 0.1 / (8 / (50 e)) = 1 + 1.70 s. tau delta 6 s: 1 s + 0.1 / (8 / (120 e)) = 1 +
  4.08 s. 882/900 = 98% for the 2% removal test. All stated beside the number and correct.

Not derived:
- `self.assertGreaterEqual(sensors["THEA"]["observed_rise"], 4)` with the comment "the synthetic 8 degC
  rise exceeds the brief's 4 degC floor". The code's heatsink floor is `rise >= 3.0` (RULE: "ΔT >=3
  degC"). The 4 cites a brief that is not in the tree and does not match the code. Tie it to the 3.0
  the classifier applies, or state where 4 comes from.
- The retained default `tolerance_ns = NS // 10` for `Sidecar`, `coverage()`, `thermal_gates.py:206`
  and `thermal_desk.py:130` has no derivation, and the new comment in `rank` says as much ("The old
  100 ms had no derivation"). Pre-existing, deliberately left by the brief, but it now sits beside a
  derived sibling and it is exactly the number that still gates the host receipt (F1).
- `docs/align/smc_temperature.md:140` ("Coverage uses the sampling grid with 100 ms tolerance") is now
  wrong for the classifier path. Doc tier.

### F5 (verified unchanged): other callers

`Sidecar.__init__` (thermal.py:128), `thermal.coverage()` (261), `thermal_gates.py:206`,
`thermal_desk.py:130` and the two `tests/hazards/test_temperature.py` uses all construct `Coverage`
without the keyword; the default binds the class attribute `NS // 10` at definition time. The branch
`Coverage` at NS // 10 reproduces the stored r0.json block bit for bit (36/1800), and
test_thermal_gate and test_thermal_desk pass. The sampler (`collect`) is untouched. The script's report
is unchanged in code and therefore still prints the 2% whole-capture line (F1).

## 4. What I would hand the builder

1. Make the R0 host receipt's readability check read the per-phase coverage that `rank` already
   computes (or a per-phase `Coverage` on each phase's grid), not the capture-wide 100 ms block; keep
   the existing 99% bar. Add a receipt test that pushes `jittered_capture`-shaped rows through the real
   `temperature.coverage()` + `smc_enumeration` receipt path. Re-run `host_receipt.py` on the real
   payload and require "pass".
2. Make `scripts/align_smc_enumerate.py` write and print the same quantity the receipt reads, so
   summary.md cannot show 0.02 beside a pass.
3. Nits: THEA floor comment (4 vs 3.0); `Coverage` docstring edge clause; `ValueError` reason;
   docs/align/smc_temperature.md:140.

With (1) and (2) done, ADMIT. Without them the re-arm fails for the same reason as re-run 7.
