# Cold reviews: RL-86 registry seat (`ops/2026-11-11-w1-p2c`) and RL-87 test seat (`ops/2026-11-11-w1-p3c`)

Independent Opus subagents, read-only, 2026-11-11. Both **ADMIT**.

## `w1-p2c` (RL-86), ADMIT

- C01 INTERNAL with RL-86's protects text verbatim (substring-checked); the handler at `driver.py:2783-2787` does what it says.
- C02-C07 field-identical to the proposal; C04 `5f7ff180602a7c30`, C05 `da64569332d2625b`; C06 NUMBER_INTEGRITY, C07 INTERNAL,
  both out of BASELINE; no frozen file touched (`test_the_baseline_is_frozen` passes).
- Five modules scanned; `timing_receipts.py span / raise / <reraise>` count 1 guard `420f332386437c13` INTERNAL, text verbatim;
  `align_r0_checks.py` not scanned as `desk`.
- C09 refused: `v4_desk` reason verbatim, `align_v4_session.py` under it; the new test was mutation-tested by the reviewer (a raise in
  the probe, a second imported name, a function-level import from another module: each fails it).
- `alignment_workload` reason verbatim for `workload.py` and `registry_select.py`.
- The 41 keys (17 `watchdog_status.py`, 24 `launch_align_r0.py`) all read at the presign tree: none stops a measurement chain or
  excludes a member or window; INTERNAL is honest for all 41. Commits confirmed (`21029737a` and others).
- `tests.hazards.test_refusal_allowlist`: 24 OK, 1 skipped.
- Nit: the three `read_fence` protects texts name only the `_decide` and `_launch_fence` holds; the same errors also suppress the
  remote-stop probe and status transport through `_remote_probe_allowed` (watchdog-only; conclusion unchanged).

## `w1-p3c` (RL-87), ADMIT

- `t0_rehearsal.py` hashes to its sealed-inventory entry, read from the file (833b19ad...1ef1).
- The unregistered calls equal exactly the literal three (getter `19a862dc8`; `git init --bare` and the courier prefix `c80d4d638`,
  the prefix marked a partial vector); extra, missing or duplicate entries fail; no other allowlist widened.
- The two courier inventory rows are a literal tied to `c80d4d638`, present only while the list is non-empty.
- `run_night.py` differs from its sealed digest (d2a2c335... vs b3c58c91...); with equal digests the list must be empty.
- Fixture untouched. Mutants real, each `assertRaisesRegex` on the RL-87 message. `tests.test_v5_block4_x12b`: 18 OK.
- Note for the research lead's record: RL-87 item 4 asked for a fixture refresh; the seat instead carries the two courier rows in
  the test under the seal condition (stricter, same effect). The `_run_night` refresh (`826f90e04`) was already in the fixture.
