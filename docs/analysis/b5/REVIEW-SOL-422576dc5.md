Independent executing review of `git diff e5ddc5c57 HEAD`, at `422576dc5` (`lane/2026-11-06-b5-lean-release`), 2026-11-06.

Recommendation: hold this change for the MAJOR findings below. Four MAJOR and three MINOR findings reproduced. No tracked file was edited. All execution used synthetic fixtures in reviewer-created temporary directories; no prohibited data path, full-size recompute, or heavy L9 pipeline was accessed or run. Commands inherited the launcher's scheduling policy.

The executable probes remain in these reviewer-created temporary directories:

```sh
P=/var/folders/b6/ny6fn4ds5rzdpxxskt2dbxn00000gn/T/b5-sol-synthetic-1ljfpiic
R=/var/folders/b6/ny6fn4ds5rzdpxxskt2dbxn00000gn/T/b5-sol-release-u50lpc17
D=/var/folders/b6/ny6fn4ds5rzdpxxskt2dbxn00000gn/T/b5-sol-deadworker-t6zmrahw
```

Run probe scripts from this checkout. Give the pool/release scripts a fresh synthetic destination when repeating them:

```sh
PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B "$P/probe_pool.py" "$(mktemp -d /private/tmp/b5-sol-pool-XXXXXX)"
PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B "$R/probe_release.py" "$(mktemp -d /private/tmp/b5-sol-release-XXXXXX)"
PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B "$D/run_dead_worker.py"
```

The release probe uses the committed tests' matching recompute fixture for stage (b), exactly as `ReleaseTests.fake_recompute` does. Digest verification and the comparator execute for real. These agreement-path probes are not evidence of live agreement or of an all-real successful pipeline.

1. **MAJOR — A worker dying during a result transfer can hang the parent indefinitely.** `scripts/independent_recompute_b5.py:598`.

   **Evidence:** Run the dead-worker command above. It constructs a real `Member` from `support.bundle`, with 8 MB of unused synthetic metadata, using the real `_member_worker` and `MemberPool(3)`. After the result pipe becomes readable, it kills and joins the workers before calling `take`. Observed:

   ```text
   result header ready (real Member, 8 MB synthetic unused metadata)
   all worker exitcodes [-9, -9, -9]
   TIMEOUT: take failed to observe exited workers; process group killed
   ```

   The supervisor allowed 16 seconds, then killed its isolated process group. `Queue.get(timeout=1.0)` can enter a blocking message-body read after the initial readiness check; a partially written result never reaches the `queue.Empty` handler that checks worker exits. A worker crash during a sufficiently large result has the same failure mechanism.

   **Suggested fix:** Use a result transport whose partial reads can be interrupted or reach EOF when its worker dies, with explicit process supervision. Per-worker pipes require closing unused writer endpoints. Merely adding another liveness check before `Queue.get` does not close the race. Add a kill-during-large-result regression with a process-group timeout.

2. **MAJOR — An arbitrary `--bars` file can turn a release disagreement into agreement without changing the advertised release bar-set name.** `scripts/release_b5.py:303` and `scripts/release_b5.py:434`.

   **Evidence:** The release probe changes the synthetic decode contrast's `dbar_j` by 1. With the committed release bars it reports `exit 1`, `hold`, `comparator_disagreement`. Copying the release bar file, preserving its `bar_set`, and setting only `families.contrast_j.absolute = 1000` produces `exit 0`, `agree`, `reason None`, still identifying `b5_release_recompute_coded_7e322b76`. Custody and input digest verification pass in both runs; the comparator really runs in both.

   `--bars` is neither bound to the pinned commit nor checked for equality with the adopted release thresholds. The wrapper therefore certifies the DLE-1 release condition under caller-selected thresholds, although RS item 83 ruling 1 binds block 5 to a fixed set.

   **Suggested fix:** Bind release bars to the adopted content digest or verify their complete effective family/override definitions against the release set. If alternate bars are needed for audits, those runs must not produce a release-authorizing verdict or success exit.

3. **MAJOR — The final blinding guard can return a held verdict with success exit 0.** `scripts/release_b5.py:399` and `scripts/release_b5.py:405`.

   **Evidence:** In the release probe, retain every release threshold and change only the valid custom bars file's `bar_set` to `synthetic 12.5 J`. All comparison families agree. `finish` correctly replaces the verdict, but the caller still returns:

   ```text
   exit 0 verdict hold reason verdict_not_structure_only
   ```

   `main` prints that returned verdict and returns the unchanged code at lines 443–446. An exit-code consumer therefore receives success after the last guard has refused the release.

   **Suggested fix:** Finalize the verdict before deriving the exit status, or propagate a refusal from `finish`. Assert that every final `hold`, including this guard, has a nonzero exit code.

4. **MAJOR — Unvalidated bar-set metadata reaches the blinded verdict as an outcome word.** `scripts/release_b5.py:354`.

   **Evidence:** The release probe leaves the numeric bars unchanged and sets `bar_set` to the synthetic outcome word `not_resolvable`. Observed: `exit 0`, `verdict agree`, and `stages.comparator.bar_set == "not_resolvable"` in the saved verdict. `main` prints this same verdict object at line 445. The decimal-token guard does not reject an outcome word.

   This reproduction requires a caller-supplied bars file; it does not demonstrate a default-bar path leaking a live science value. It does disprove the unconditional promise that the public verdict cannot carry an outcome word.

   **Suggested fix:** Project only fixed, validated identifiers into public output. Keep arbitrary labels in restricted comparison output, and validate the final verdict against a structure-only schema rather than relying on a decimal regex.

5. **MINOR — Closing a pool with queued work leaks parent feeder threads and their pipe resources.** `scripts/independent_recompute_b5.py:618`.

   **Evidence:** The pool probe performs three cycles of `MemberPool(3)`, 1,500 prefetched missing synthetic members, and `close()`. After each close, `multiprocessing.active_children()` is zero, but the number of live `QueueFeederThread` threads increases: `1`, `2`, `3`. The feeder is left trying to flush queued tasks after its consumers have been terminated. `cancel_join_thread()` prevents waiting for it; it does not stop it.

   This affects repeated in-process use, which the new tests explicitly support. It also means later pool startups can fork while earlier queue threads are still alive, despite the startup rationale.

   **Suggested fix:** Give shutdown a protocol that stops or drains the task feeder before removing its consumers, and verify that threads and descriptors return to baseline after early exits with a backlog. Avoid an unbounded drain in the error path.

6. **MINOR — The output no-follow check omits the restricted directory itself.** `scripts/release_b5.py:262` and `scripts/release_b5.py:96`.

   **Evidence:** In the release probe, move the newly created synthetic `custody/dry-run/restricted` directory to a synthetic sibling and replace it with a directory symlink. Without changing any output bytes or recorded hashes, the full digest/comparator path reports `exit 0`, `agree`, `outputs_verified: 20`.

   `read_nofollow` checks components below its `base`; the caller supplies the unchecked restricted directory as that base. Thus the DLE-1 promise to read these outputs without following a symbolic link is not enforced at this boundary. Content digests still match in this reproduction; this is a custody-path guarantee failure, not a demonstrated arithmetic change.

   **Suggested fix:** Resolve output names through the trusted custody root and include `dry-run/restricted` in the no-follow walk, preferably using directory descriptors. Add a symlinked-output-root case alongside the existing symlinked-file test.

7. **MINOR — The runbook claims measured timings but contains no measurements.** `docs/analysis/b5/RELEASE-RUNBOOK-lean.md:101`.

   **Evidence:** `nl -ba docs/analysis/b5/RELEASE-RUNBOOK-lean.md | sed -n '95,113p'` shows “Measured”, “Measurements are below”, then the literal `TIMING-TABLE` placeholder. The subsequent numbers are explicitly real-data projections; they do not supply the claimed synthetic measurements or worker-count speedups.

   **Suggested fix:** Insert the actual synthetic commands, worker counts, elapsed times and evidence reference, or remove the measurement claim and label the timing section as unmeasured projections. No heavy/full-size timing was run in this review.

**Verification and negative results**

The requested focused command was run with bytecode disabled for child imports and the synthetic-only fence enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.independent_recompute.test_member_pool tests.independent_recompute.test_release_b5
```

Result: `Ran 26 tests in 227.058s`, `OK (skipped=1)`. The full-size opt-in test was skipped; its opt-in environment variable was never set. No full repository suite was run under this bounded review.

Additional pool executions compared the entire tuple `(exit, output bytes, stdout, stderr)` for workers 1, 3 and 10:

| Synthetic case | Result |
| --- | --- |
| Baseline `full_pack(ALPHA, n=3)` | Identical; 102,294-byte output |
| Science member also named in a reference slot, duplicated roster ID, missing member directory, corrupt plist | Identical; 103,889-byte output |
| Same mutations plus `--diagnostic-ignore-exclusions` | Identical; 104,669-byte output |
| Repeated `--extra-beta` arguments naming the same archive | Identical |
| Primary BETA plus two extra-BETA arguments naming that exact BETA archive | Identical; 133,033-byte output |
| Unused metadata containing 600 nested lists | Identical |

A separate in-process test requested a spare as `science` after it had been prefetched as `start`: member details, flags and files-read sets were identical for 1/3/10 workers. Injecting `ZeroDivisionError` into a consumed member produced exactly `(2, empty stdout, "error: internal ZeroDivisionError\n", no output file)` for all three counts. No remaining worker children were observed after these normal/error closures. The dead-worker probe was explicitly killed and reaped by its supervisor. No macOS fork crash was reproduced in these executions; arbitrary pre-existing threaded/native-library hosts were not validated.

Release tests and probes confirmed the ordinary tampered/missing output, symlinked output file, changed input, wrong requested commit, changed seal pins/index, incomplete record and recompute-stop holds. No release invocation unsealed anything. The only reproduced public outcome-word path is finding 4; no default-bar science-value leak was observed.

`census_path` matches L9's `_released_input_difference` for well-formed ordinary archive rows, `original/claim-runs`, the live calibration ledger, and `sources/attempts/<plan>/...`. It also copies L9's deliberate `binding/plan_tree` exception: those rows are counted, not rehashed as files. Changing a synthetic binding-row digest was consequently ignored; I am not reporting that as a mapping discrepancy. The lean implementation is stricter on malformed/missing entry shapes.

The estimator arithmetic is unchanged in the reviewed diff; the added execution and release mechanisms are where the findings lie. The coverage audit explicitly pins its line citations to `e5ddc5c57`. A mechanical check of all 470 alias/range citations found no out-of-bounds references. Targeted source checks support its key omissions and named comparator exemptions, and the cited PLAN step-12/replay clauses, D-188 equivalence clauses and RS release/tie rulings are present. Signing assertions and historical/live timing claims were not independently verifiable without crossing this review's data boundary. “No estimand changes” is consistent with the arithmetic diff; it does not cure the release-gate and execution defects above.

Next exact step: fix findings 1–4, add their focused regressions, and rerun the two requested modules plus the bounded synthetic probes before considering release authorization.
