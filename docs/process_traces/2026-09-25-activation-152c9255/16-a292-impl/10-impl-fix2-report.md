**Result: GREEN.** `tests.test_scored_reduce` passes: 63/63 non-differential tests, and all 200 differential nights (every seed and index, each run exactly once). Nothing contradicted the ruling, so there is no NEEDS_RULING. Not committed, as instructed. HEAD is still `a7d88826a026caa5d0cdce1ccc874da945cc940b`.

## What changed
I made exactly the Round I changes from the A292-ESC-01 ruling (Z3, which applies the Z2 amendment), and nothing else.

```
 joulewise/scored_reduce.py | 6 ++++--
 1 file changed, 4 insertions(+), 2 deletions(-)

@@ -17,6 +17,8 @@
 ANCHOR_KEY = "E_clock_anchor_shift_bound_j"
+ENERGY_MAX_J = 10**12
+INT_MAX = 2**53
@@ -49,11 +51,11 @@
 def _int(v):
-    return type(v) is int and v >= 0
+    return type(v) is int and 0 <= v <= INT_MAX
 def _num(v):
-    return type(v) is int or (type(v) is float and math.isfinite(v))
+    return (type(v) is int or (type(v) is float and math.isfinite(v))) and v <= ENERGY_MAX_J
```

- **Check order:** unchanged. `_int` and `_num` are only used inside the single `window_domain` / `row_domain` check. That check already runs before `window_unknown`, `row_unknown` and `row_tokens_over_cap`, which is where Z2 places it.
- **Existing positivity rules still hold:** `gross_j > 0` and anchor `>= 0` or null are still separate operands at the call site, so the new upper bound does not loosen either one.
- **Scope:** `git status` shows only ` M joulewise/scored_reduce.py`. I did not read `tests/scored_reduce_checker.py` or `tests/scored_reduce_witnesses.py`, and I did not touch `/Users/edr/code/JouleWise`.

## Run 1: all tests except the differential
One foreground command ran 63 tests in 12 parallel chunks. All chunks returned 0.
```
chunk 0: rc=0 Ran 6 tests in 3.673s | OK
...
chunk 5: rc=0 Ran 5 tests in 14.931s | OK
...
chunk 11: rc=0 Ran 5 tests in 9.518s | OK
TOTAL ran 63 failing chunks 0
python3 -B - <<<''  77.97s user 0.30s system 517% cpu 15.120 total
```
This includes the three new tests: `test_generated_one_fault_domain_witnesses`, `test_domain_boundaries_accept` and `test_extreme_values_refuse_not_crash`.

## Run 2: `test_differential_oracle_200_nights`, split into 12 parallel parts
One foreground command split the 4 seeds × 50 nights into 12 parts (each seed cut into index ranges 0–16, 17–33 and 34–49). Each worker ran the test method's own source code. I changed only three literal strings, and each was checked to appear exactly once before replacing it:
- the seed tuple, so each worker gets its own seed;
- `range(50)`, so each worker gets its own index range;
- the final `assertGreaterEqual(nights, 200)`, which became a report of that worker's night count and the (seed, index) pairs it ran.

The parent process then checked that the parts together ran every one of the 200 pairs exactly once.
```
seed=[17] idx=0..16 rc=0 ok=True nights=[17] | Ran 1 test in 116.607s | OK
seed=[17] idx=17..33 rc=0 ok=True nights=[17] | Ran 1 test in 171.871s | OK
seed=[17] idx=34..49 rc=0 ok=True nights=[16] | Ran 1 test in 100.681s | OK
seed=[29] idx=0..16 rc=0 ok=True nights=[17] | Ran 1 test in 119.877s | OK
seed=[29] idx=17..33 rc=0 ok=True nights=[17] | Ran 1 test in 170.664s | OK
seed=[29] idx=34..49 rc=0 ok=True nights=[16] | Ran 1 test in 103.705s | OK
seed=[43] idx=0..16 rc=0 ok=True nights=[17] | Ran 1 test in 128.240s | OK
seed=[43] idx=17..33 rc=0 ok=True nights=[17] | Ran 1 test in 100.201s | OK
seed=[43] idx=34..49 rc=0 ok=True nights=[16] | Ran 1 test in 138.077s | OK
seed=[71] idx=0..16 rc=0 ok=True nights=[17] | Ran 1 test in 104.614s | OK
seed=[71] idx=17..33 rc=0 ok=True nights=[17] | Ran 1 test in 114.011s | OK
seed=[71] idx=34..49 rc=0 ok=True nights=[16] | Ran 1 test in 102.717s | OK
partitions 12 failing 0 | nights total 200 | covered exactly once: True
python3 -B - <<<''  1466.65s user 1.95s system 853% cpu 2:52.00 total
```
Both of each night's checks passed:
- **Variant A:** the reducer's result matches the independent oracle.
- **Variant B:** with one live window dropped, the reducer refuses with `missing_live_window` and the oracle agrees.

## Still to do
- **Commit:** the ruled message is `A292 reducer fix-2 (A292-ESC-01 input bounds)`.
- **Magistrate's next step (G6 ii–iv):** re-enumerate the mutation sweep with the differential against this reducer. This includes the four bound mutants: `ENERGY_MAX_J` set to `10**11` and to `10**13`, and `INT_MAX` set to `2**52` and to `2**54`.
