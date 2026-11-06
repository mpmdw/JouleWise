# Step-11 ordered sensitivity pass concurrency

Branch: `sol/u90-item3`, starting at `76f3386ec`.
Authority: the 2026-11-06 item-3 brief and its standing rules; D-188.
Status: implemented; runtime verification blocked by the execution sandbox.

## Change

`dry_run._sensitivity` dispatches the primary-bound equality pass and the
registered-bound pass through `pack_parallel.pack_map`, then consumes them in
their original order. The module-level `sensitivity_pass_pack` returns the
record, every sources-replay archive census (including GAMMA), and the explicit
GAMMA handle's census. Consumption merges those rows before advancing. Only the
second record is written; sensitivity and step-results publication remain in
their original order.

Failed computations are recomputed through the same wrapper at their serial
position by `consume`. Thus a primary-pass refusal leaves its serial partial
archive state and prevents consumption of pass 2. Reads, deadlines, physics,
store entries, and failure handling use the existing pack transport. Its
`member_worker_shares` assigns each pass a share, which its nested derivation
pool subdivides again. No pool or estimator policy changed. The existing
`JOULEWISE_B5_PACK_PARALLEL` switch applies to `sensitivity_pass_pack`; `off`,
insufficient workers, or failed input transport retain serial execution.

No custody read-replay call moved. `derive_pack` remains in `sensitivity.py`, so
the custody allowlist is unchanged. No pin, cache key, estimator, or record
schema changed. The standing-rule protected state files were not edited.

## Synthetic regression coverage added

`tests/b5_analysis/test_sensitivity_passes_parallel.py` contains six tests:

- Identical records (including their JSON serialization), publication order,
  archive censuses and authentication read records for serial and spawned
  execution, with both shared and distinct GAMMA handles.
- A late primary-pass refusal wins over an early secondary-pass refusal or a
  successful secondary pass; its partial state matches serial and the later
  worker's synthetic deadline firing is not accounted.
- A secondary-pass refusal preserves the consumed primary-pass state.
- Failed worker result transport recomputes serially at the pass position;
  failed input serialization retains the serial path.
- The operator switch retains the same records and censuses.
- Nested derivations receive `[1, 2]` and `[2, 2]` from passes assigned `[3, 4]`
  under a seven-worker budget (an inline executor inspects actual task shares).

Arithmetic consumers are explicit synthetic seams. These are not live-data or
hardware checks, and the tests have not executed in this session.

## Executed evidence

- `git status --short --branch`, branch and HEAD inspection: clean starting
  tree on the requested branch and base commit.
- `git diff --check`: passed.
- Python 3.13 AST parsing of the two changed production modules and the new
  test module: passed. This was syntax validation only.
- Attempted baseline command:

  ```sh
  nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.b5_analysis.test_sensitivity_parallel
  ```

  Exit 70, before unittest started:

  ```text
  nice: setpriority: Operation not permitted
  taskpolicy: setpriority(): Operation not permitted
  ```

The sandbox does not permit the required priority controls. No unprefixed test
command was substituted. No unittest ran; the remaining modules below were not
attempted after this shared launch prerequisite failed. The full suite and
full-size synthetic pipeline were not run, as directed. No network or real
measurement input was used. No agent or cross-model delegation was used.

## Remaining verification and expected saving

Run these modules one at a time in an environment that permits the mandated
priority controls, retaining the supplied TMPDIR and the same command prefix:

```sh
nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.b5_analysis.test_sensitivity_passes_parallel
nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.b5_analysis.test_sensitivity_parallel
nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.b5_analysis.test_sensitivity.PassTests
nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.b5_analysis.test_step11_null_outcomes
nice -n 19 taskpolicy -b env TMPDIR="$TMPDIR" python3.13 -B -m unittest tests.test_custody_mode_inventory
```

The ideal pass time changes from `P1(W) + P2(W)` to
`max(P1(share1), P2(share2))`, plus dispatch/transport overhead, where shares sum
to W. With sufficient spare workers and balanced passes the ceiling is about
50% less time for the sensitivity portion. There is no measured saving from
this session. Reduced per-pass member parallelism, CPU/memory contention,
serialization and additional process startup can erase the saving or cause a
slowdown. Other step-11 work is unchanged. The lead's cloud benchmark and
D-188 equivalence gate remain necessary before claiming performance or result
equivalence on the complete analysis.

Next exact step: run the six commands above, then perform the lead-controlled
cloud benchmark and equivalence comparison. This local commit is unverified at
runtime and is not a merge-readiness claim.
