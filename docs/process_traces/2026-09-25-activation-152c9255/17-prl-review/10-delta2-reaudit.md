# PR-L fix round 2: delta re-audit (Opus 5.5)

**Delta:** `9500545f..1bdbca1d`. **Verdict: SF1 and N-a through N-d are all closed. There is no new BLOCKER.** I found one new SHOULD-FIX. It is a coverage loss caused by the N-a change, not a change in behaviour. There are also two NITs.

## How each item closed

| Item | Result | Evidence |
|---|---|---|
| **SF1(1)** | CLOSED | `test_night_gate.py:922`: the exempt branch now also asserts `assertNotEqual("GO", receipt.verdict)`. |
| **SF1(2)** | CLOSED | The new `test_pack_rehearsal_exemption_requires_real_authorization_digest` writes a real authorization file under `Path(tmp).resolve()`. Only `MEASUREMENT_ROOT_CUSTODY_ROOT` is patched. With the correct sha, R16 is skipped and the plan refuses later with `night_probe_error`. With `"0"*64`, it refuses `measurement_root_outside_custody`, and neither case returns GO. Because the two sub-cases get different reasons, the test proves the exemption is reached only with the authentic digest. |
| **SF1(3)** | CLOSED, and it goes through the exemption branch | `test_run_night.py` `test_post_cutoff_t0_inside_measurement_custody_refuses_disjointness_end_to_end`. I added print statements in my `/tmp` clone to trace the path: `EXEMPT_BRANCH rehearsal=True`, then `DISJOINT_RAISE from _evaluate_pack_conditions ← evaluate_night`. The test checks that the driver exits REFUSED, that there are no launch calls, that no `go_receipt` is written, and that the refusal is `launch_go_receipt_invalid` with detail `rehearsal_roots_not_disjoint: measurement_root`. |
| **N-a** | CLOSED | The `_probe_cadence` suffix is gone, and the worker's prefix (`run_night.py:3902`) still carries `elapsed_s` and `bound_s`. `_probe_cadence` has one caller (`:3898`). |
| **N-b** | CLOSED | The supervisor-timeout detail now ends with `custody_elapsed_s=… timeout_s=…`. There are two tests: a real subprocess one (`timeout_s=3`) and a mocked Popen one (`timeout_s=0.25`). |
| **N-c** | CLOSED | `arm_retry.py:77` registers the string with the `<label>` placeholder, the same convention as the existing `<path>` entries. The two doc tables and the test set match, and `gen_state --check` returns rc 0. |
| **N-d** | CLOSED | The refusal is now `…differs from install: <label>`, and the tests check it for each label. |

**Mutation probes** (run on the clone, then reverted):
- **M1.** The exemption reads the authorization without checking its digest. **Killed** by the new unmocked test (the `"0"*64` subtest) and by the existing mocked test.
- **M2.** `_pack_rehearsal_roots` returns early for T0 plans authored after the cutoff (the "skip every root rule for T0" refactor). **Killed** by the new end-to-end test.

## SHOULD-FIX

**S-1. The requirement that the refusal text carries timing (Astra F2) no longer has any regression test.**
- The only test that checked `elapsed_s=` and `bound_s=55` in refusal text was `test_run_night_probe_cadence.py:90`. Round 2 changed it to check the structured `result["bound_s"]` and `result["elapsed_s"]` fields instead. Given N-a, that change is correct.
- But the text that now carries the timing, the worker's prefix at `run_night.py:3902`, is not asserted by any test. No test mentions `probe_cadence_failed` or `probe cadence elapsed_s`.
- **Mutation proof:** I deleted `elapsed_s` and `bound_s` from the worker's format string. `tests.test_run_night` (235 tests), `test_run_night_probe_cadence` and `test_evidence_arm_sequence` all still pass. The install tests contain no assertion on this text either.
- **Fix:** add one worker-level test where the cadence fails, and assert `receipt["refusal_code"] == "probe_cadence_failed"` and that the detail contains `elapsed_s=` and `bound_s=55`. Either stub `_probe_cadence` or reuse the 220-frame fake.

## NIT

- **N-1.** If the receipt's `launch_context` is missing or not a dict, `_validate_install_launch_context` reports `: <LABELS[0]>` (the night label). In that case no label actually differs; the whole context is absent. In practice `validate_probe_receipt:869` refuses first, so this is cosmetic. A clearer text would be `…: launch_context missing`.
- **N-2.** The end-to-end SF1(3) test builds a second `PackNightProducerTests()` inside the running test and calls its `setUp`/`doCleanups` by hand. The outer `self.setUp` fixture is built and never used. It works (it passed, and cleanup runs in `finally`), but it is unusual. A `subTest` or a helper that takes a `_rehearsal_layout` flag would be cleaner.

## Other checks: no new defects
- No behaviour changed outside the NITs. The installer check changed from "any label differs" to a loop over the labels. It refuses the same inputs, and only the refusal text changed.
- No test assertion was weakened. The only assertion changes are the one described under S-1 and a stricter `…: <label>` regex.

## Test runs

Clone `/tmp/152c9255/prl-reaudit2-opus` at `1bdbca1d`; no sudo, launchctl or real powermetrics; no background tasks.

| Run | Result |
|---|---|
| `tests.test_night_gate`, `tests.test_arm_retry`, `tests.test_run_night_probe_cadence`, `tests.test_evidence_arm_sequence` | `Ran 145 tests in 6.513s` — `OK` |
| `tests.test_run_night` | `Ran 235 tests in 111.426s` — `OK` |
| `tests.test_night_agent_install`, run in 4 parts to stay under the 10-minute limit | 43 + 12 + 13 + 13 = 81 tests — all `OK` (115 s, 43 s, 446 s, 11 s) |
| `gen_state.py --check` | rc 0 |

The worktree is unmodified (`git status` is clean, HEAD is `1bdbca1d`), and the clone was reverted after each mutation.

The claude.ai Anthropic Economic Index connector needs authorization in its claude.ai connector settings. It was not needed for this audit.
