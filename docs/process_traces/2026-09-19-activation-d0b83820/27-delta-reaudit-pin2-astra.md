```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Found one weakened immutability oracle and one duplication nit; all five modules pass, both requested negative-oracle sets succeed, and quick-suite failure is environmental.",
  "workspace": {
    "base_requested": "d3c8b3559a3c635e43de46e98918e0e468201919",
    "base_mode": "exact",
    "head_start": "d6b99c71f47b6d1261ebbbee18a8722acd9d0435",
    "head_end": "d6b99c71f47b6d1261ebbbee18a8722acd9d0435",
    "upstream_end": "d6b99c71f47b6d1261ebbbee18a8722acd9d0435",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 1, "nit": 1},
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "title": "V3 source-immutability assertion hashes the unexecuted checkout",
        "call_site": "tests/test_d117_v3_family.py:183-191",
        "assertion_site": "tests/test_d117_v3_family.py:214-224",
        "counterfactual": "A production mutant appends a comment to its own cloned v2 source after --check. The final test passes; the d3c8b355 test, supplied historical head bytes in scratch, fails its source-hash assertion.",
        "recommendation": "Also snapshot and compare the generator files in generation_repository(), retaining the original-checkout safety assertion."
      },
      {
        "id": "R2",
        "severity": "nit",
        "title": "Disposable generation-repository helper is copied five times",
        "call_site": "tests/test_arm_readiness_registry.py:99; tests/test_d117_decode_contrast_plan.py:824; tests/test_d117_floor_qwen25_1p5b_plan.py:467; tests/test_d117_floor_qwen25_7b_plan.py:460; tests/test_d117_v3_family.py:141",
        "counterfactual": "A future cleanup or overlay correction applied to one helper leaves four independent implementations unchanged.",
        "recommendation": "Consider one shared helper. The bytes and digest already have one home; all five helper ASTs are currently identical after ROOT-name normalization."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_arm_readiness_registry",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 6 tests in 26.511s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 25 tests in 42.984s", "", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen25_1p5b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 22 tests in 14.233s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_floor_qwen25_7b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 20 tests in 16.583s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_d117_v3_family",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 17.133s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK$"}
    },
    {
      "id": "V6",
      "kind": "other",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-reaudit-d6b99c71/oracles.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["ORACLES: 10/10 head mutants and 6/6 production mutants killed"]},
      "expected": {"exit_code": 0, "tail_regex": "ORACLES: 10/10 head mutants and 6/6 production mutants killed"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-reaudit-d6b99c71/source_mutation.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 0, "tail": ["Ran 1 test in 13.669s", "", "OK", "", "EXIT 0"]},
      "expected": {"exit_code": 0, "tail_regex": "EXIT 1"}
    },
    {
      "id": "V8",
      "kind": "other",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-reaudit-d6b99c71/source_mutation.py --baseline",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 17.630s", "", "FAILED (failures=1)", "", "EXIT 1"]},
      "expected": {"exit_code": 0, "tail_regex": "EXIT 1"}
    },
    {
      "id": "V9",
      "kind": "other",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-reaudit-d6b99c71/cleanup.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["test_d117_v3_family clone-failure PASS; all fixture roots removed", "test_d117_v3_family assertion-failure PASS; all fixture roots removed"]},
      "expected": {"exit_code": 0, "tail_regex": "assertion-failure PASS; all fixture roots removed"}
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python scripts/quick_suite.py --tier quick --workers 4",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["QUICK SUMMARY tier=quick modules=153 excluded=85 failures=1 seconds=275.541 result=FAIL"]},
      "expected": {"exit_code": 0, "tail_regex": "failures=0 .*result=PASS"}
    },
    {
      "id": "V11",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/head-pin-reaudit-d6b99c71/assertion_audit.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Identical helper ASTs after ROOT-name normalization: True"]},
      "expected": {"exit_code": 0, "tail_regex": "normalization: True"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Quick suite completed with one failing module: tests.test_axi_controller_events, two failures reporting campaign start identity unavailable. Its identity observer invokes /bin/ps; a direct probe was denied with operation not permitted.",
      "needs": "Lead rerun the quick suite where process observation is permitted."
    }
  ]
}
```

## Findings

**R1 — should fix: the v3 immutability proof is weakened.** The test executes the fixture’s generator at [line 186](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_v3_family.py:186), but its before/after hashes still read `ROOT` at lines 175–179 and [214–224](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_v3_family.py:214).

Executed counterfactual: append a comment to the invoked generator’s own source after its successful `--check`. The final test reports **OK**, despite the cloned source changing. The baseline test detects the same mutation and fails its hash comparison. [Reproducer](/tmp/head-pin-reaudit-d6b99c71/source_mutation.py), [final-test output](/tmp/head-pin-reaudit-d6b99c71/self-write.log), [baseline output](/tmp/head-pin-reaudit-d6b99c71/self-write-baseline.log).

The next fix should retain the original-checkout assertion and additionally compare the executed clone’s generator bytes before and after execution.

**R2 — nit: five helper implementations.** The head bytes and digest have one home in [test_campaign_generator_core.py:25](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_campaign_generator_core.py:25). Repository construction is copied into all five modules at the envelope’s call sites. The copies are currently identical after normalizing `ROOT` versus `REPO_ROOT`; no divergent behavior was found.

**E1 — final-text assertion audit.** The diff is exactly the five scoped modules: **259 insertions, 68 deletions**. All **852 original assertion calls remain**, with six additions. Retained assertion text does not preserve the source-immutability proof identified in R1.

The table describes each test’s intended proof before the change, then its final behavior. File labels link to the relevant modules; line numbers are final-head locations.

| ID | Changed test | Before → now |
|---|---|---|
| T1 | [Registry](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_arm_readiness_registry.py:300): `test_generators_check_both_without_and_with_committed_freeze_receipts` | Frozen/generated inventory and byte parity, receipt bindings, draft checks, committed-freeze refusal and preserve stability → same checks against historical-head fixtures. Assertions: 363–448, 466–482, 509–513, 568 onward. |
| T2 | [Contrast](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_decode_contrast_plan.py:1319): `test_dual_generation_transaction_and_generational_induction` | Exact 334-file v2 and v3 transactions, unchanged predecessor bytes, emitted-generator induction and preserve stability → same proof through fixtured inputs. Assertions: 1376, 1405–1411, 1439, 1455–1479. |
| T3 | Contrast: `test_emitted_successor_generator_refuses_downgrade_targets` | Three families × three modes refuse downgrade before writes; forward generation succeeds → same proof. Specific refusal and unchanged-state assertions: 1977–1993; forward acceptance: 2019–2020. |
| T4 | Contrast: `test_emitted_successor_pack_bytes_carry_no_freeze_variant_wording` | Nonempty successor output has no prohibited wording, with scanner self-check and classified prompt exemption → same proof. Assertions: 2062–2112. |
| T5 | [1.5B](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_floor_qwen25_1p5b_plan.py:720): `test_successor_generation_threads_plan_identity_and_lineage` | Exact successor inventory, predecessor/spec preservation, identity and lineage threading, embedded self-check and preserve stability → same proof. Assertions: 760–817, 850–957, 975–1018. |
| T6 | [7B](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_floor_qwen25_7b_plan.py:613): `test_target_status_inventory_and_invalid_modes_are_fail_closed` | Identity/status classification, exact artifact inventory, invalid-mode refusal without writes → same proof, strengthened with specific refusal messages. Assertions: 626–647, 665–671. |
| T7 | 7B: `test_generation_refuses_symlinked_write_inventory_before_any_write` | Four symlink configurations refuse with source/destination diagnostics and no writes → same proof after passing the head check. Assertions: 724–729. |
| T8 | 7B: `test_successor_generation_threads_plan_identity_and_lineage` | Same inventory, preservation, identity, lineage and embedded-generator properties as T5 → same proof with fixture inputs. Assertions: 771–828, 861–968, 986 onward. |
| T9 | [V3](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_v3_family.py:227): `test_check_still_refuses_missing_generator_owned_output` | Successful generation followed by specific refusal for deleted `order_manifest.json` → same proof. Assertions: 244, 256–257. |
| T10 | V3: `test_unedited_v2_generators_emit_v3_successors` | Three-family v3 emission, custody exclusion, successful checking and unchanged executed v2 sources → emission/custody/checking retained; executed-source immutability lost. Assertions: 196–224; **R1**. |

No changed refusal assertion became satisfied by the head-pin refusal.

**E2 — corrupted-head oracle.** Only the fixture’s `write_bytes` argument was corrupted; its constant-digest assertion remained intact. Every test exited **1**, with the head-file refusal visible:

| Test | Exact outcome | Head-refusal diagnostic |
|---|---|---|
| T1 | `FAILED (failures=1)` | `pinned input drifted` |
| T2 | `FAILED (failures=1)` | `pinned input drifted` |
| T3 | `FAILED (failures=1)` | `pinned input drifted` |
| T4 | `FAILED (failures=1)` | `pinned input drifted` |
| T5 | `FAILED (failures=1)` | `pinned input drifted` |
| T6 | `FAILED (errors=1)` | `external input drift` during artifact construction |
| T7 | `FAILED (failures=4)` | `external input drift`; all four symlink cases |
| T8 | `FAILED (failures=1)` | `external input drift` |
| T9 | `FAILED (failures=1)` | `pinned input drifted` |
| T10 | `FAILED (failures=2)` | Both floor families reject the head bytes |

Each diagnostic names `configs/calibration/calibration_ledger_head.json`. [Per-test results](/tmp/head-pin-reaudit-d6b99c71/oracles.json).

**E3 — production-condition oracle.** Tests and assertions were unchanged. Production sources were mutated only inside disposable `/tmp` clones. Every mutant was detected without a head-pin refusal:

| Test / mutation | Outcome |
|---|---|
| T7: bypass write-boundary validation | `FAILED (failures=4)`; pack directory, pack file, extraction spec and sidecar each fail with `AssertionError: 0 == 0`. |
| T6: disable positive-ordinal guard | `FAILED (failures=1)`; expected positive-ordinal message is absent, despite a different downgrade refusal. |
| T6: disable preserve-target guard | `FAILED (failures=1)`; `AssertionError: 0 == 0`. |
| T3: disable downgrade guard in all three predecessor generators, propagating into emitted successors | `FAILED (failures=10)`; all nine family/mode cases fail, plus the final predecessor-hash check. Preserve cases reject the wrong refusal message. |
| T9: ignore missing inventory entries and omit the deleted manifest’s byte comparison | `FAILED (failures=1)`; `AssertionError: 0 == 0`. |
| T4: emit `unfrozen draft` in successor READMEs | `FAILED (failures=3)`; wording scan catches all three families. |

[Replay script](/tmp/head-pin-reaudit-d6b99c71/oracles.py) and [results](/tmp/head-pin-reaudit-d6b99c71/oracles.json); production mutation diffs are alongside them.

**E4 — fixture hygiene.**

- All five helpers register cleanup before cloning. Injected clone failures and post-construction assertion failures removed every fixture root: **10/10 cleanup probes passed**.
- `git status --short --untracked-files=all` was empty after **each** module and at completion.
- No branch-name or historical-commit lookup is required. The audited checkout was detached throughout.
- The overlay copies every `d117_*/generate_configs.py`. Emitted successors derive from those sources and obtain inputs through the fixture-specific links; T2, T5 and T8 execute those successor paths.
- New fixture code uses standard Python, Git and POSIX paths/symlinks; no macOS-only calls were added. Linux execution was not performed.

**E5 — executions.** V1–V5 contain the requested module tails: **78 tests ran, one existing skip, all modules OK**. The quick suite completed:

```text
QUICK SUMMARY tier=quick modules=153 excluded=85 failures=1 seconds=275.541 result=FAIL
```

The failing module was `tests.test_axi_controller_events`: two tests received `campaign start identity unavailable`. The observer calls `/bin/ps`, and a direct probe returned `operation not permitted`. This is the anticipated sandbox limitation. [Full quick log](/tmp/head-pin-reaudit-d6b99c71/quick.log).

**E6 — same-signature census.** No active head-byte-dependent regeneration site remains in these five modules, and no fixture was found hiding a refusal the changed test exists to detect. There is a **dormant survivor**: the already-skipped authenticated-freeze test invokes live-checkout floor generators at [contrast lines 1533–1545](/Users/edr/code/JouleWise-wt-reaudit-pin2-d0b83820/tests/test_d117_decode_contrast_plan.py:1533). Its skip starts at line 1481. It needs fixturing when re-enabled.

**E7 — duplication.** One constants home, five identical repository helpers; R2 is a nit only.

## Residual risk

The quick suite needs a rerun with process observation permitted. The authenticated-freeze scenario remains structurally skipped, and Linux compatibility was inspected rather than executed.

No repository files were written. The permanent frozen-generator fixture ruling is preserved; the later production fix for the two live floor-v5 generators remains separate.