```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"CITRIM-VERIFY: FINDINGS — two deleted modules protect live code; all modified test modules pass.",
  "workspace":{"base_requested":"800f3f53","base_mode":"exact","head_start":"800f3f53d671e0cba6a1139ad0b846dc8a59880d","head_end":"800f3f53d671e0cba6a1139ad0b846dc8a59880d","upstream_end":"ad6800cb7354139711cdbfe3420be61f9cd1e5cb","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[{"id":"F1","severity":"should_fix","path":"tests/test_build_capstone.py","text":"Deleted two tests for the live VOIDED capstone producer and its legacy-label regression guard."},{"id":"F2","severity":"should_fix","path":"tests/test_preflight.py","text":"Deleted nine tests for live plan-derived preflight routing."}],"brief_items":{"1":"DONE","2":"PARTIAL","3":"PARTIAL","4":"DONE","5":"DONE","6":"DONE"},"reviewed_tree":{"head":"32ff901374024defa97fc3d137c5a699423676e7","dirty_files":26,"diff_unchanged":true}},
  "verification":[
    {"id":"V1","kind":"test","cmd":"python3 -B /tmp/citrimver/run_modules.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["COMPLETE"]},"expected":{"exit_code":0,"tail_regex":"COMPLETE$"}},
    {"id":"V2","kind":"inspection","cmd":"python3 -B /tmp/citrimver/audit.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["AUDIT_COMPLETE live_deleted_tests=2 main_clean=True trim_diff_unchanged=True"]},"expected":{"exit_code":0,"tail_regex":"AUDIT_COMPLETE live_deleted_tests=2 main_clean=True trim_diff_unchanged=True"}},
    {"id":"V3","kind":"inspection","cmd":"JOULEWISE_FULL_CORPUS=1 PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/citrimver/check_corpus.py","cwd":"/Users/edr/code/JouleWise-wt-citrim-ff50b201","observed":{"result":"pass","exit_code":0,"tail":["CORPUS_ENABLED tests=83 skip_marked=0 original_function_bodies_changed=0"]},"expected":{"exit_code":0,"tail_regex":"CORPUS_ENABLED tests=83 skip_marked=0 original_function_bodies_changed=0"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/citrimver python3 -B -m unittest -v tests.test_shard_tests tests.test_shard_split > /tmp/citrimver/shard-tooling.log 2>&1","cwd":"/Users/edr/code/JouleWise-wt-citrim-ff50b201","observed":{"result":"pass","exit_code":0,"tail":["Ran 37 tests in 3.310s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V5","kind":"inspection","cmd":"gh run list --repo mpmdw/JouleWise --workflow d117-production-proof.yml --limit 1 --json createdAt,databaseId,conclusion","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["error connecting to api.github.com","check your internet connection or https://githubstatus.com"]},"expected":{"exit_code":0,"tail_regex":".*"}}
  ],
  "flags":[
    {"id":"F3","kind":"baseline_drift","level":"nonblocking","text":"Requested main baseline contains 20 tests absent from the older trim base; origin/main also advanced during verification.","needs":"Reconcile the landing base before final verification."},
    {"id":"F4","kind":"verification_gap","level":"nonblocking","text":"Git history verifies workflow retirement/deferment, but GitHub API connectivity prevented checking the last hosted D117 execution.","needs":"Confirm hosted workflow history."},
    {"id":"F5","kind":"verification_gap","level":"nonblocking","text":"Every modified module passed freshly; no fresh whole-repository suite or separate full-corpus trim execution was performed.","needs":"Lead owns final suite verification after resolving findings."}
  ]
}
```

## Findings

**F1 — should fix:** Restore or explicitly adjudicate [test_build_capstone.py](/Users/edr/code/JouleWise-wt-citrimver-ff50b201/tests/test_build_capstone.py:49). Its two tests cover live `generate_results_page()`/`LEGACY_LABEL`, called by the CLI, `release_check.py`, and retained RPT tests. September 4 commits `a02e424e0` and `5f9f9e266` repaired this producer’s VOIDED fence; closing legacy claims did not retire that fence. Deleted hunk excerpt:

```diff
@@ -1,64 +0,0 @@
-    def test_pre_cure_label_kills_void_fence(self):
-        with mock.patch.object(build_capstone, "LEGACY_LABEL", PRE_CURE_LABEL):
-            counterfactual = build_capstone.generate_results_page()
-        with self.assertRaises(AssertionError):
-            self.assert_voided_results_page(counterfactual)
```

**F2 — should fix:** Restore [test_preflight.py](/Users/edr/code/JouleWise-wt-citrimver-ff50b201/tests/test_preflight.py:16). Its nine tests cover live `preflight.sh`, still invoked by `SHAKEDOWN-G2-RUNSHEET.md:746`. September 8 commits `f0fedc91a` and `3e016b042` added/repaired measurement-root, head, interpreter, and retired-plan protections. Deleted hunk excerpt:

```diff
@@ -1,138 +0,0 @@
-    def test_retired_plan_refused(self) -> None:
-        self.plan["schema"] = "joulewise.night_plan.v1"
-        result = self.run_routing()
-        self.assertEqual(result.returncode, 1)
-        self.assertIn("FAIL night plan must use joulewise.night_plan.v2 with schema_version 2", result.stdout)
```

Brief checks, based on executed discovery, source/diff inspection, git history, and foreground system-Python runs:

1. **DONE — timings:** Main: **269 modules, 39 missing timing entries**. Trim: **261 modules, zero missing**. All 261 values match preserved scheduling observations, including the 0.001-second floor.
2. **PARTIAL — workflows:** Main pushes and PRs select **3.13 only**; other matrix dimensions and gate-ledger bytes are unchanged. `site.yml` history confirms D-136 retirement (`f4aa13843`, August 11). D117’s last file edit is `01af200b4`, August 16, deferring automatic execution and retaining dispatch-only operation. Git cannot establish its last hosted execution; API inspection failed.
3. **PARTIAL — six deletions:** `test_pack_capsule` (43 tests) and `test_build_site_parsers` (30) belong to D-136’s retired automatic lane. `test_axi_sb_spike` (18; `7c90093b4`, July 16) and `test_axi_sc_spike` (20; `646fc91af`, July 17) target completed spike harnesses, with no core production imports. **Capstone (2) and preflight (9) target live code**, as F1/F2 show.
4. **DONE — duplicate execution:** Main **7,560 IDs**, trim **7,241**, using `python3 -B -c` discovery. Literal duplicate extras: **137 → 0**; normalizing `tests.test_*` versus `test_*` reveals **178 → 0** redundant executions: `LaunchConsumptionV2Tests` **160**, `PairAuthenticationTests` **18**. The 319-count decrease comprises 178 duplicates, 122 deletions, 20 baseline-only additions, offset by one new stress test.
5. **DONE — scored gating:** All four changed scored modules were timed whole, with default corpus settings:

| Module (`tests.` prefix) | Main wall seconds | Trim wall seconds |
|---|---:|---:|
| `test_scored_packer_stress` | 944.726 | 15.105 |
| `test_scored_packer_fuzz` | 51.751 | 0.235 |
| `test_scored_ownership_forgery` | 581.538 | 3.309 |
| `test_scored_reduce` | 1166.355 | 69.172 |

`JOULEWISE_FULL_CORPUS=1` enables all **83 tests**, with zero skip markers; original function bodies are unchanged. Default named regressions, seal regressions, checker-exception/entry witnesses, 63 fast reduce cases, and new `test_first_two_registration_sequences` all passed.

6. **DONE — synchronization:** `ArmReadinessEvidenceAuthorTests.test_suite_completion_kills_delayed_grandchild_process_group` and `.test_suite_timeout_kills_delayed_grandchild_process_group` now use readiness/FIFO handshakes and EOF. `CalibrationExitReliabilityTests.test_torn_event_line_keeps_its_acknowledgement` polls sampler-confirmed drained bytes. Existing assertions remain intact; all three passed.

Every **14 modified test modules** passed whole: **1,119 tests, 16 skips, zero failures**, including zero sandbox-only failures. The additional shard-tooling suite passed **37 tests**. No weakened assertion appeared in retained hunks; the deleted protections above are the coverage findings.

KEEP-list touches: source files `test_calibration_exits.py`, `test_detection_floor.py`, `test_floor_extraction.py`, and `test_whole_window.py`; plus **62 timing weights**. Calibration synchronization strengthened; the other three source edits replace imported test-class aliases. No KEEP source was deleted.

Evidence: [module results](/tmp/citrimver/module-results.json), [audit results](/tmp/citrimver/audit-result.json), [reviewed diff](/tmp/citrimver/trim.patch). Both repositories remained unchanged by this seat.

## Residual risk

The full opt-in trim corpus was enabled and source-compared, but not separately executed; main’s original corpus executed successfully. No fresh whole-repository suite was run. Preserved prior-seat suites show **15 failures before versus 15 failures plus one error after**; the added RPT error is now fixed and its whole module passed freshly. Those existing failures were not independently classified as sandbox-only.

The fixed requested baseline includes 20 tests and two modules absent from trim’s older base; upstream advanced to `ad6800cb` during verification. Resolve F1/F2, reconcile the landing base, confirm hosted D117 history, then perform lead-owned final suite verification.