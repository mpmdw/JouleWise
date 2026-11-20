# W1 step-5 contrast writer preservation, 2026-11-19

Tier 2 · Sol 6.2 build · [AGENT] · invented fixtures

The cycle's 19:59 Opus decision requires a controlled step-5 refusal when the optional writer sees a null policy or an existing contrast value that differs from derivation. The guard checks every derived field before any write. It emits the step and field on stderr, returns 1, and leaves the input file and the earlier step-4 install in place. Matching values replay without a write. A present policy can receive missing values from the same child output. Full nested JSON comparison ignores object key order and preserves value types and numeric spelling, consistent with the replay's retained-decision comparator. [RL-189 §2.5, lines 22186–22191](https://github.com/mpmdw/JouleWise/blob/00a28dcf2d0dc424bd3438678913d4f393d3ed3a/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22186-L22191)

## Commit and freeze

| Item | Commit | Tree |
| --- | --- | --- |
| Rehearsal B, PR #856 | `199b39b0cfa778e4efd240540674724d76fd3520` | `3652381ee416a621ac76388bc54d48abb11efc4e` |
| Executable acceptance freeze, committed before source edits | `e9607d3dcc55bb8a0fdcbe0896905707823690ae` | `525541dca2dc852bb191069d9d09e00125eea6a4` |
| Assessed implementation and frozen tests | `60bd505a7e1a38867074342736c28b609362e5f4` | `ef965ae354afcc980a65557ed72e6e8ef36b1d8d` |
| Assessed implementation and audit regression | `4b898ded5a393bcde8f1e180a0b614b58a7a20ff` | `4521636a4834306f499ed845bc4fee370bb4a38b` |

Pre-edit `git ls-tree` at rehearsal B and `b2e01464d6d4fbf2901ff4d4154df9455104a12a` matched for the wrapper, its chain test, and seven public producer and fixture-support files. The wrapper blob was `693028869d989f46a4ff73d224667ba9b874c737` and the chain test blob was `431c2471cfb481160ed648f1a8b65bec775c4e89`. The condition-13 comparison used only `git ls-tree` entries for the ten paths in `R1_EXECUTED_SOURCES`. All ten matched at base and implementation. The freeze-to-implementation diff of the test file was empty.

## Baseline and regression evidence

The focused module ran 12 tests at the freeze with only the two expected reds. Null policy raised `AttributeError` under normal `chain.main`. The conflicting-cap test failed byte preservation after 239 became 238. The original isolated Astra CLI replay matched all 39 baseline expectations. Its two proposed assertions both failed. The null case reached 5 and emitted a traceback. The cap case reached 8 and returned 1 after a downstream placeholder refusal, having already overwritten the input.

| Builder finding | Disposition and commit | Frozen test | Baseline → implementation |
| --- | --- | --- | --- |
| VERIFIED MED · `impl-bug` · null policy crashes | Step-5 refusal, `60bd505a7` | `ContrastWriterTests.test_null_policy_is_a_controlled_refusal` | ERROR → PASS |
| VERIFIED HIGH · `impl-bug` · conflicting cap overwritten | Step-5 refusal, `60bd505a7` | `ContrastWriterTests.test_conflicting_existing_value_is_preserved` | FAIL → PASS |
| Astra round 1 · VERIFIED LOW · `test-gap` · canonical formatting could hide an unnecessary rewrite | Compact JSON regression, `4b898ded5` | `ContrastWriterTests.test_matching_values_preserve_noncanonical_formatting` | FAIL on rehearsal B → PASS |

The final toy replay ran 41 invocations through the public CLIs, including both backfill refusals and downstream placeholder controls. The proposed Astra assertions passed 2/2. Each step-5 wrapper case kept the installed toy record equal to the step-4 output (SHA-256 `81f84fa915927c90242ad11fda0a30f4523c9802312fafd2e35ed748925fa534`). The separate prefilled print path kept its native counted record and all five retained values across regeneration and the expected readiness hold.

| Starting policy and action | Baseline exit / last step | Implementation exit / last step | SHA-256 of implementation inputs before → after, shown as prefixes |
| --- | --- | --- | --- |
| Null, write | 1 / 5, traceback | 1 / 5, controlled | `42480d860c4a` → `42480d860c4a` |
| Cap 239 vs 238, write | 1 / 8 | 1 / 5, controlled | `13e2f01ed279` → `13e2f01ed279` |
| Both fields absent in present policy, write | 1 / 8 | 1 / 8, expected placeholder hold | `b74ea05ac2a5` → `cf38cf4126a8` |
| Both fields match, write | 1 / 8 | 1 / 8, expected placeholder hold | `cf38cf4126a8` → `cf38cf4126a8` |
| Null, print through 5 | 0 / 5 | 0 / 5 | `42480d860c4a` → `42480d860c4a` |
| Cap 239, print through 5 | — | 0 / 5 | `13e2f01ed279` → `13e2f01ed279` |
| Nested fit differs, write | — | 1 / 5, controlled | `1b7cca815cd1` → `1b7cca815cd1` |
| Integer as float, write | — | 1 / 5, controlled | `5fe28694d31c` → `5fe28694d31c` |
| Nested false as zero, write | — | 1 / 5, controlled | `faac33c4dc22` → `faac33c4dc22` |

Pure derivation returned 0 and left exact input bytes in each of the nine final cases. The focused module also passed exact replay, absent-value insertion, null print-only, dry-run, and the unchanged exit 23 from an already failed derive child.

## Commands and results

The isolated seat scratch root is `report/w1-contrast-writer.jJ9J2q`. It contains the copied public fixture, SHA-256 ledger, invocations and stderr in the two observed JSON files, and the final replay driver. The fixture hash check passed 127/127 before the wrapper was replaced in the scratch copy.

```sh
git status --short --branch
gh pr view 856 --repo mpmdw/JouleWise --json number,headRefName,headRefOid,baseRefName,state,isDraft,url
git ls-remote origin refs/heads/integ/2026-11-18-w1-candidate-rehearsal-b
git diff --exit-code b2e01464d 199b39b0c -- scripts/align_r1_to_w1_chain.py tests/align/test_r1_to_w1_chain.py
git diff --exit-code e9607d3dc 60bd505a7 -- tests/align/test_r1_to_w1_chain.py
git diff --check 199b39b0c
```

With the scratch root as cwd and `TMPDIR` set to its `tmp` directory, these were the replay commands.

```sh
(cd fixture && shasum -a 256 -c PUBLIC-SHA256SUMS)
python3.13 -B fixture/replay.py --keep-root ./base-toy-root --report ./base-observed.json
python3.13 -B fixture/tier2_spec.py ./base-observed.json
PYTHONPATH=fixture python3.13 -B final_replay.py
python3.13 -B fixture/tier2_spec.py ./final-observed.json
```

The focused module ran from `focused-toy-root` with the same `TMPDIR` and `JOULEWISE_HOST_STATE_DIR` directed to scratch. The existing rehearsal fixture used its fake command runner, the public chain doc, and an invented runtime config, schedule and prior S6 record. That isolated Git root had only invented tree data. The required chain command passed 13/13, and the focused budget and exporter contracts passed 7/7. An exploratory wider run passed 16/20, with four setup errors from omitted kit and identity artifacts in the toy root. The canonical hosted sharded workflow supplies the full-suite result.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_r1_to_w1_chain
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_w1_kit_r10.ProcedureTests align.test_r1_turn_counts_export.ExportTests.test_export_matches_the_driver_and_binds_every_input_file
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_r1_to_w1_chain.ContrastWriterTests.test_matching_values_preserve_noncanonical_formatting
```

## Review and handoff

| Independent Astra audit | Assessed commit | VERIFIED HIGH | MED | LOW | Root cause and disposition |
| --- | --- | --- | --- | --- | --- |
| 1 | `60bd505a7` | 0 | 0 | 1 | `test-gap` · canonical formatting could hide a rewrite. Six tests and a compact-input probe passed. |
| 2 | `4b898ded5` | 0 | 0 | 0 | All seven writer tests passed. The delta remedied the test gap and preserved all six frozen cases verbatim. |

Round 2 meets the §3 decay rule with zero VERIFIED HIGH plus MED in both rounds and no new HIGH root cause. No return to spec was triggered. [Tier 2 pipeline](https://github.com/mpmdw/JouleWise/blob/1a060309679be06db4831009749f83e269bc7f61/docs/process/PIPELINE.md#L36-L62)

```sh
TMPDIR="$(mktemp -d "$PWD/report/astra-round1.XXXXXXXX")" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.align.test_r1_to_w1_chain.ContrastWriterTests
TMPDIR="$(mktemp -d "$PWD/report/astra-r2.XXXXXX")" python3.13 -B -m unittest -v tests.align.test_r1_to_w1_chain.ContrastWriterTests
```

The integration owner and Opus own acceptance of the final tree. Carry the draft onto the candidate after those acceptances and verify the candidate head. The working print-only W1 route can proceed independently. PR #886 and its operational inputs remain lead-owned. Fable owns any change in scientific meaning or protected rules. The draft evidence ledger and the seat's `FINAL-MESSAGE.md` record the published head, tree and checks.

NEEDS_SPEC: none from the builder.

## Lead pipeline audit 1 repair, 2026-11-20

Opus assessed the previous draft head `de432544203a9b64e0c6f4e43ad735c39b4b5b45`. The audit verified HIGH 1, MED 1 and LOW 0. Both findings were implementation bugs in the insertion path and were also present on rehearsal B. Exact-match replay bypassed the path. When a field was absent, whole-document JSON serialization could change independently authored values.

The new executable witnesses were frozen at `426da3e89fd63b5fd4916e3145b0cece12638d25` before implementation. At the assessed source, 13 of 15 chain tests passed and the two new audit witnesses failed. The repair at `66a8302477f876f7fd8e9078b07c75edee4fcd74`, tree `e5413081c118ee1cbfacfa4f37771a2687eb2ebf`, inserts only missing contrast members. It uses the already-derived value text and preserves every pre-existing input byte, including the encoding and numeric tokens. It refuses duplicate keys before insertion, including equivalent escaped spellings. All previously frozen cases remain verbatim.

| Audit finding | Commit | Regression | Result |
| --- | --- | --- | --- |
| VERIFIED HIGH · `impl-bug` · partial insertion rounded `R1.T_dead` and converted the independent comparator's HOLD to MATCH | `66a830247` | `test_insertion_preserves_authored_deadline_spelling` | FAIL → PASS |
| VERIFIED MED · `impl-bug` · partial insertion silently discarded cap 239 when a second key held 238 | `66a830247` | `test_duplicate_cap_with_missing_fit_is_refused` | FAIL → PASS |

The real CLI replay on fresh invented fixtures reproduced the auditor's before/after digests. With the repair, the number case inserts the missing fit and the comparator still reports HOLD on the unchanged authored deadline. Removing the inserted bytes recovers the exact original file. The duplicate case returns 1 at step 5, preserves the whole input, and keeps the step-4 install.

| Case | Assessed head result | Repair result | Repair SHA-256 of inputs, before → after |
| --- | --- | --- | --- |
| Deadline `1277.03797646727251`, cap 238 and missing fit | Exit 0 through 5, HOLD → MATCH | Exit 0 through 5, HOLD → HOLD | `c8eda7906f95` → `4dc6445ffaaa` |
| Duplicate cap 239 then 238 and missing fit | Exit 0 through 5, HOLD → MATCH | Controlled exit 1 at 5, HOLD → HOLD | `70de5fa12c2e` → `70de5fa12c2e` |
| Escaped duplicate cap | — | Controlled exit 1 at 5 | `5c58414b742e` → `5c58414b742e` |

The supplementary replay also checked insertion into an empty object and byte-for-byte retention of original UTF-16BE and UTF-32LE inputs with BOMs, non-ASCII strings, escaped member names and distracting nested JSON punctuation. The required chain module passed 15/15. Focused budget/export contracts passed 7/7. The full toy replay exercised 41 invocations and both original Astra assertions passed. All ten condition-13 identities still match `b2e01464d` by metadata.

The repair scratch root is `report/w1-contrast-round1.LSEYn8`. The focused commands ran in its `focused-toy-root`, with `TMPDIR` and `JOULEWISE_HOST_STATE_DIR` directed to that scratch root. For the CLI commands, the working directory was the scratch root and the copied wrapper was set to the assessed or repaired public source as appropriate.

```sh
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_r1_to_w1_chain
PYTHONPATH=tests:. python3.13 -B -m unittest align.test_w1_kit_r10.ProcedureTests align.test_r1_turn_counts_export.ExportTests.test_export_matches_the_driver_and_binds_every_input_file
PYTHONPATH=fixture python3.13 -B audit_replay.py old
PYTHONPATH=fixture python3.13 -B audit_replay.py new
PYTHONPATH=fixture python3.13 -B final_replay.py
python3.13 -B fixture/tier2_spec.py ./final-observed.json
python3.13 -B report/w1-contrast-writer.jJ9J2q/check_condition_13.py HEAD
git diff --exit-code 426da3e89 HEAD -- tests/align/test_r1_to_w1_chain.py
```

The lead's next audit and the integration-owner and Opus acceptances remain open. The PR ledger and the new seat handoff record the published repair head and canonical CI.
