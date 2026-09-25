**Result: GREEN on everything I ran, and no test needs a ruling.** One caveat: I did not run `python3 -m unittest tests.test_scored_reduce` as a single command. That takes about 35 minutes, a single foreground command stops at 10, and background tasks were ruled out. Instead I ran the full module in one foreground command with the differential test split into 8 parallel parts, described below. Nothing was committed.

## Diff (`joulewise/scored_reduce.py` only; 2 lines changed)
```diff
 def _num(v):
-    return type(v) in (int, float) and math.isfinite(v)
+    return type(v) is int or (type(v) is float and math.isfinite(v))
@@ _check_window
-          and w["roster_sha256"] == _in_force(roster, placement["envelope_index"]), "window_binding", repr(key))
+          and w["roster_sha256"] == _in_force(roster, w["envelope_index"]), "window_binding", repr(key))
```
- **(a) Binding index.** The in-force digest is now computed from the window's own declared `envelope_index`, as E2 requires. The check order is unchanged: binding, then duplicate, then envelope. The later `window_envelope` check still compares the window's index against the placement's.
- **(b) Number range.** Integers skip `math.isfinite`, so any integer is accepted before the sign checks run. `10**1000` is now accepted and `-10**1000` refuses with `window_domain`. Floats must still be finite. Booleans are still excluded because `type(True) is bool`. There are no input-specific cases.

## Test tails
**Fast subset** (61 tests, everything except `test_differential_oracle_200_nights`, run in-process):
```
Ran 61 tests in 58.430s

OK
```
**Full module.** Script: `/tmp/152c9255/a292-fix2/partitioned_full.py`, run with `PYTHONPATH=<worktree>`, 3 min 15 s wall. It:
- runs the 61 fast tests in one worker;
- runs the unmodified differential test in 8 more workers, one per (seed, half of the 50 night indices), for seeds 17, 29, 43 and 71;
- makes each part by editing only the loop header in the test's own source, and asserts each of those edits happened exactly once;
- requires `nights == 25` in each part instead of `nights >= 200`.
```
fast: ran=61 failures=0 errors=0 ok=True 72.6s
diff seed=17 idx=[0,25): ... ok=True 195.3s     diff seed=17 idx=[25,50): ... ok=True 145.9s
diff seed=29 idx=[0,25): ... ok=True 179.0s     diff seed=29 idx=[25,50): ... ok=True 167.1s
diff seed=43 idx=[0,25): ... ok=True 163.3s     diff seed=43 idx=[25,50): ... ok=True 156.2s
diff seed=71 idx=[0,25): ... ok=True 132.5s     diff seed=71 idx=[25,50): ... ok=True 138.7s
DIFFERENTIAL_NIGHTS_OK=200/200
FULL_MODULE_PARTITIONED=PASS
```
If the gate needs the literal single `python3 -m unittest tests.test_scored_reduce` run, you'll have to run it with a timeout over 35 minutes.

## NEEDS_RULING
**None from the tests.** No harness test sends a very large *positive* energy (`gross_j`) through a live window. For your ruling lane (A292-AGGREGATE-OVERFLOW-01), I confirmed the gap with a probe outside the tests. Setting `gross_j = 10**1000` on window 0 of the fixture from `_night()` gets past `window_domain`, then:
```
  File ".../joulewise/scored_reduce.py", line 245, in reduce
    g_j=math.fsum(window_by_key[k]["gross_j"] for k in window_keys), k=len(window_keys),
OverflowError: int too large to convert to float
```
Following the brief, I added no new refusal code. A large anchor value (`E_clock_anchor_shift_bound_j = 10**1000`) is safe, because it is only checked for null and never added up. `test_positive_zero_and_large_integer_anchor` passes.

## Scope
- Only `joulewise/scored_reduce.py` is modified in the worktree. I did not open `tests/scored_reduce_checker.py` or edit any test file.
- Two files outside the repo came from this session: the run script above, in a new directory `/tmp/152c9255/a292-fix2/`, and nothing else. The overflow probe was run inline and saved nothing.
