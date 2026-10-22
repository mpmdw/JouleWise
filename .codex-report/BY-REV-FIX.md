## PROGRESS
- Done: FIX-1/FIX-2 generated and all twelve real acceptance probes pass; FIX-3 implementation and initial regression checks pass; intake; clean baseline bda481d5af510b29dde4976f172a20170a42c955; no active stop card. This delegated [AGENT] fix brief is the current authority; lead-owned state files remain untouched.
- Next: director expands scope for Mac-kit generated tree or rules on the required check; rerun the sandbox-limited dynamic import proof where host process-group census works. All independent authorized implementation and focused verification finished.
- Open: NEEDS_SCOPE for configs/campaigns/bytes_mac_check/plan_tree.json (generator drift); import-graph dynamic probe cannot census host process group under this sandbox. All required analysis classes passed. No hardware or protected operational roots accessed.

## SUMMARY
FIX-1, FIX-2 and FIX-3 are implemented within the exhaustive write scope.
All twelve roster censuses and real acceptance loss cases pass.
The manifest reproduces from committed records and validates with a sessions list supplied.
Twelve in-place session exports produce byte-identical model_estimates/H1/H2/MoE outputs.
A copied production-shaped export discloses missing stores and checked paths through the real CLI.
The twin and all requested analysis classes pass; refusal census arrays are empty.
Required Mac-kit regeneration needs an additional path; its check and module remain blocked.
Dynamic import proof is limited by sandbox host process census; static proofs pass.
No commits, collection, installation, protected roots or operational refs were touched.

## CHANGES
Generator preserves external input mapping and writes/pins all twelve extraction specs; frozen manifest regenerated from committed records; desk CLI accepts multiple in-place exports; missing records and pass rows disclose absolute checked store path; input validation requires config_key; regression tests and input contract updated.

## DECISIONS I MADE
- Family ID: `<module_id>-decode`, shared between absolute and comparative extraction cells.
- Pin extraction spec bytes under downstream_contract.extraction_spec, following replication floors; arm_attachments remains {}.

## EVIDENCE
Baseline: `git -C /Users/edr/code/JouleWise-by-rev log --oneline -6` exit 0, head bda481d5a; `git -C /Users/edr/code/JouleWise-by-rev status --short` exit 0, empty.

## OPEN ISSUES
Acceptance pending.

## NEEDS_RULING
none

Slice checkpoint: baseline pack regression exit 1 (12 AttributeError errors); corrected pack regression exit 0 (all role censuses and 24 loss verdicts). Initial input regression exit 1 (5 failures, 1 error); corrected input/manifest run exit 0 (19 tests). Full command/output ledger follows below before handoff.

## SLICE 1 VERIFIED CHANGES
- scripts/bytes_plan_trees.py: preserve mapping and reference/artifact entries; remove only BETA-owned entries; generate complete absolute/comparative specs and pin their bytes.
- configs/campaigns/bytes-s{1..6}-p{1,2}/plan_tree.json and extraction_spec.json: generated through the generator only. Arm attachments remain empty.
- scripts/bytes_manifest.py and configs/bytes/bytes_manifest.json: registered model/role/MoE/tier/native L4 IDs and public identity, byte-reproducible from committed records. Integer k/E cross-checked with §2's 8/128, 10/512, 8/256; fit and tier membership from §§2,9.
- scripts/bytes_analyze.py: multiple export roots passed directly to existing load_records duplicate guard.
- joulewise/bytes_analysis.py: non-empty public config_key validation and checked absolute withheld paths on census placeholders and missing pass rows.
- tests/b6/test_bytes_packs.py, tests/test_bytes_analysis.py, tests/test_bytes_manifest.py: real acceptance and CLI regression coverage; generator hash pin check updated.
- docs/contracts/bytes_tables.md: input generation, per-session exports, checked-path disclosure.

## SCOPE EXPANSION REQUIRED
NEEDS_SCOPE: requested_paths = ["configs/campaigns/bytes_mac_check/plan_tree.json"].
Reason: required `scripts/bytes_mac_kit.py --check` derives its tree from the repaired BYTES s1 pass tree. Read-only comparison of `bytes_mac_kit.build_files()` finds this sole generated file drifted. It is outside WRITE_SCOPE and remains untouched. Minimal change: regenerate that file through the existing Mac-kit generator after lead expands scope. Blocked: Mac-kit check and tests.test_bytes_mac_kit.

## VERIFICATION NOTES
The initial export module fails because macOS resolves /tmp to /private/tmp but its assertion compares that resolved store to an unresolved /tmp fixture root. Rerunning with a separate TMPDIR under /private/tmp passes all 11 tests without edits.
Import-graph tests: 5 static tests pass; dynamic real fake-collector child returns NULL because its host pgrep process-group census is denied: `sysmon request failed with error: sysmond service not found; pgrep: Cannot get process list`. Canonical TMPDIR does not fix it. No bypass used. Diagnostic Rig.run was fixture-backed, not live hardware; all OS command seams other than the existing child process-group census are fakes.

## FINAL DECISIONS AND LIMITS
- No registered count, exclusion minimum, arithmetic or inference threshold changed. Counts, labels and bytes are compared exactly, as authorized. No numerical agreement bar added.
- All generated pass files were written only by the requested generator command. Frozen manifest was written only by merge from committed records. Shared harvest, flags and B6 implementation are unchanged. No tests in the whole repository suite were run.
- Mac-kit read-only diff shows only its pre-existing malformed external_inputs key list changes order (manifests/artifacts becomes artifacts/manifests) because the repaired seed now serializes a mapping with sorted keys. Regenerating the one out-of-scope tree would satisfy byte drift; the kit generator independently still iterates mapping keys. That existing kit defect is preserved and disclosed to the director rather than silently changing its scope.
- No scope expansion has been applied. No ruling changes which data count or any printed number. NEEDS_RULING: none. NEEDS_SCOPE remains blocking for the required Mac-kit check.

## EVIDENCE — REPLAY COMMANDS AND OBSERVED OUTPUTS
All commands below ran at `/Users/edr/code/JouleWise-by-rev`. Every repository-code command used the synthetic-only/no-bytecode environment. Every final module invocation has its own TMPDIR. Initial combined red input probes shared one TMPDIR; final manifest and analysis module invocations were separate.

```sh
git -C /Users/edr/code/JouleWise-by-rev log --oneline -6
```
Exit 0.
```text
bda481d5a BY-INT: lead verification and main refresh in the report
d401c6213 Merge current main (PR #538, Codex MCP server) into BYTES pass-1 integration
```

```sh
git -C /Users/edr/code/JouleWise-by-rev status --short
```
Exit 0.
```text
(empty at intake)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests
```
Exit 1.
```text
EEEEEEEEEEEE
======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s1-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s1-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s2-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s2-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s3-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s3-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s4-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s4-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s5-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s5-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s6-p1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

======================================================================
ERROR: test_all_pass_rosters_and_registered_stratum_minimum (tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests.test_all_pass_rosters_and_registered_stratum_minimum) (pack='bytes-s6-p2')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_bytes_packs.py", line 255, in test_all_pass_rosters_and_registered_stratum_minimum
    roster = build_roster(pack, ROOT)
  File "/Users/edr/code/JouleWise-by-rev/joulewise/b5/harvest.py", line 1694, in build_roster
    input_id = manifest.get("external_input_id") or manifest.get("input_id")
               ^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

----------------------------------------------------------------------
Ran 1 test in 0.438s

FAILED (errors=12)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.ReviewInputTests tests.test_bytes_manifest.FrozenManifestTests
```
Exit 1.
```text
FFFFEF
======================================================================
ERROR: test_missing_store_records_and_pass_rows_disclose_checked_path (tests.test_bytes_analysis.ReviewInputTests.test_missing_store_records_and_pass_rows_disclose_checked_path)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_analysis.py", line 2118, in test_missing_store_records_and_pass_rows_disclose_checked_path
    self.assertEqual({r['withheld_path_checked'] for r in rows}, {expected})
                      ~^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'withheld_path_checked'

======================================================================
FAIL: test_manifest_requires_public_config_key (tests.test_bytes_analysis.ReviewInputTests.test_manifest_requires_public_config_key) (value=None)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_analysis.py", line 2103, in test_manifest_requires_public_config_key
    with self.subTest(value=value), self.assertRaisesRegex(ba.AnalysisError, 'config_key'):
                                    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: AnalysisError not raised

======================================================================
FAIL: test_manifest_requires_public_config_key (tests.test_bytes_analysis.ReviewInputTests.test_manifest_requires_public_config_key) (value='')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_analysis.py", line 2103, in test_manifest_requires_public_config_key
    with self.subTest(value=value), self.assertRaisesRegex(ba.AnalysisError, 'config_key'):
                                    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: AnalysisError not raised

======================================================================
FAIL: test_manifest_requires_public_config_key (tests.test_bytes_analysis.ReviewInputTests.test_manifest_requires_public_config_key) (value='  ')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_analysis.py", line 2103, in test_manifest_requires_public_config_key
    with self.subTest(value=value), self.assertRaisesRegex(ba.AnalysisError, 'config_key'):
                                    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: AnalysisError not raised

======================================================================
FAIL: test_manifest_requires_public_config_key (tests.test_bytes_analysis.ReviewInputTests.test_manifest_requires_public_config_key) (value=7)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_analysis.py", line 2103, in test_manifest_requires_public_config_key
    with self.subTest(value=value), self.assertRaisesRegex(ba.AnalysisError, 'config_key'):
                                    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: AnalysisError not raised

======================================================================
FAIL: test_frozen_manifest_reproduces_and_validates_analysis_models (tests.test_bytes_manifest.FrozenManifestTests.test_frozen_manifest_reproduces_and_validates_analysis_models)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_manifest.py", line 346, in test_frozen_manifest_reproduces_and_validates_analysis_models
    self.assertEqual((root / 'configs/bytes/bytes_manifest.json').read_bytes(), raw)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: b'{\n[488 chars]nfig_sha256": "3027455f6ce315c983f1955f20d3961[3807180 chars]n}\n' != b'{\n[488 chars]nfig_key": "Llama-3.3-70B-Instruct-4bit|bytes_[3807971 chars]n}\n'

----------------------------------------------------------------------
Ran 3 tests in 0.186s

FAILED (failures=5, errors=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py
```
Exit 0.
```text
generated 12 BYTES draft registrations and 12 fixed pass trees
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs.BytesHarvestAcceptanceTests
```
Exit 0.
```text
.
----------------------------------------------------------------------
Ran 1 test in 0.652s

OK
bytes-s1-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-1p7b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-4b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s1-p1 lost members 1 ACCEPT True ()
bytes-s1-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s1-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-1p7b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-4b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s1-p2 lost members 1 ACCEPT True ()
bytes-s1-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s2-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-30b-a3b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s2-p1 lost members 1 ACCEPT True ()
bytes-s2-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s2-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-30b-a3b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s2-p2 lost members 1 ACCEPT True ()
bytes-s2-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s3-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-14b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-next-80b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s3-p1 lost members 1 ACCEPT True ()
bytes-s3-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s3-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-14b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-next-80b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s3-p2 lost members 1 ACCEPT True ()
bytes-s3-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s4-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-32b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-8bit-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s4-p1 lost members 1 ACCEPT True ()
bytes-s4-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s4-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-32b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-8bit-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s4-p2 lost members 1 ACCEPT True ()
bytes-s4-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s5-p1 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-llama-70b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s5-p1 lost members 1 ACCEPT True ()
bytes-s5-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s5-p2 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-llama-70b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s5-p2 lost members 1 ACCEPT True ()
bytes-s5-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s6-p1 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen35-122b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s6-p1 lost members 1 ACCEPT True ()
bytes-s6-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s6-p2 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen35-122b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s6-p2 lost members 1 ACCEPT True ()
bytes-s6-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
```

The first post-generator acceptance test used empty capture rows and a deliberately mismatched test runtime and returned EXCLUDE (calibration.bracket_incomplete, model.stack_differs_from_registered). The corrected test supplies registered capture-corpus values and runtime versions as synthetic evidence; it still uses real prepare, synthetic_session and evaluate. No acceptance implementation was patched.

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/bytes_manifest.py merge --headers configs/bytes/records/*.headers.json --kv configs/bytes/records/*.kv.json
```
Exit 0.
```text
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "llama-3.3-70b-instruct-4bit", "pilot_read_meas_GB": 39.0973568}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-1.7b-4bit", "pilot_read_meas_GB": 0.968002688}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-14b-4bit", "pilot_read_meas_GB": 7.87021088}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-30b-a3b-4bit", "pilot_read_meas_GB": 1.711355008}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-32b-4bit", "pilot_read_meas_GB": 17.992094528}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-4b-4bit", "pilot_read_meas_GB": 2.262921632}
{"W_minus_pilot_bytes": 4.76837158203125e-07, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-8b-4bit", "pilot_read_meas_GB": 4.257673472}
{"W_minus_pilot_bytes": null, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-8b-8bit", "pilot_read_meas_GB": null}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3-next-80b-a3b-instruct-4bit", "pilot_read_meas_GB": 2.031833728}
{"W_minus_pilot_bytes": 0.0, "comparison": "W versus pilot read_meas_GB (pilot column excludes KV)", "model": "qwen3.5-122b-a10b-4bit", "pilot_read_meas_GB": 5.070253248}
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check
```
Exit 0.
```text
verified 12 BYTES draft registrations and 12 fixed pass trees
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/build_b6_flag_catalog.py --check
```
Exit 0.
```text
(no output)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check
```
Exit 1.
```text
ValueError: generated kit drifted: configs/campaigns/bytes_mac_check/plan_tree.json
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_bytes_packs
```
Exit 0.
```text
..........
----------------------------------------------------------------------
Ran 10 tests in 1.753s

OK
bytes-s1-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-1p7b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-4b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s1-p1 lost members 1 ACCEPT True ()
bytes-s1-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s1-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-1p7b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-4b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s1-p2 lost members 1 ACCEPT True ()
bytes-s1-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s2-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-30b-a3b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s2-p1 lost members 1 ACCEPT True ()
bytes-s2-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s2-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-30b-a3b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s2-p2 lost members 1 ACCEPT True ()
bytes-s2-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s3-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-14b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-next-80b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s3-p1 lost members 1 ACCEPT True ()
bytes-s3-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s3-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-14b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-next-80b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s3-p2 lost members 1 ACCEPT True ()
bytes-s3-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s4-p1 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-32b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-8bit-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s4-p1 lost members 1 ACCEPT True ()
bytes-s4-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s4-p2 {'absolute_repeat': 20, 'comparative_abba_member': 80, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen3-32b-decode', 'target': True, 'strata': ['quad', 'repeat']}, {'cell_id': 'bytes-qwen3-8b-8bit-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s4-p2 lost members 1 ACCEPT True ()
bytes-s4-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s5-p1 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-llama-70b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s5-p1 lost members 1 ACCEPT True ()
bytes-s5-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s5-p2 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-llama-70b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s5-p2 lost members 1 ACCEPT True ()
bytes-s5-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s6-p1 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen35-122b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s6-p1 lost members 1 ACCEPT True ()
bytes-s6-p1 lost members 24 EXCLUDE False ('cell.below_minimum',)
bytes-s6-p2 {'absolute_repeat': 10, 'comparative_abba_member': 40, 'neg8_bound': 18, 'end_reference': 3, 'midpoint_reference': 1, 'start_reference': 3} [{'cell_id': 'bytes-qwen35-122b-decode', 'target': True, 'strata': ['quad', 'repeat']}] 10 repeat + 10 quad units per model
bytes-s6-p2 lost members 1 ACCEPT True ()
bytes-s6-p2 lost members 24 EXCLUDE False ('cell.below_minimum',)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_blinding
```
Exit 0.
```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.075s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_export_runs
```
Exit 1.
```text
....F......
======================================================================
FAIL: test_group_withholds_offset_rows_and_only_publishes_counts_and_key_digests (tests.b6.test_export_runs.ExportTests.test_group_withholds_offset_rows_and_only_publishes_counts_and_key_digests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/b6/test_export_runs.py", line 127, in test_group_withholds_offset_rows_and_only_publishes_counts_and_key_digests
    self.assertTrue(store.is_relative_to(self.root / "packs/bytes"))
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true

----------------------------------------------------------------------
Ran 11 tests in 0.339s

FAILED (failures=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_release_subset
```
Exit 0.
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.064s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_catalog
```
Exit 0.
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.250s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_manifest
```
Exit 0.
```text
.................
----------------------------------------------------------------------
Ran 17 tests in 0.750s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_twin
```
Exit 0.
```text
.........................................................
----------------------------------------------------------------------
Ran 57 tests in 10.138s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_mac_kit
```
Exit 1.
```text
E...
======================================================================
ERROR: test_generated_tree_and_configs_validate_without_a_pack_registration (tests.test_bytes_mac_kit.MacKitTests.test_generated_tree_and_configs_validate_without_a_pack_registration)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/test_bytes_mac_kit.py", line 24, in test_generated_tree_and_configs_validate_without_a_pack_registration
    files = kit.generate(check=True)
  File "/Users/edr/code/JouleWise-by-rev/scripts/bytes_mac_kit.py", line 157, in generate
    raise ValueError("generated kit drifted: " + str(path))
ValueError: generated kit drifted: configs/campaigns/bytes_mac_check/plan_tree.json

----------------------------------------------------------------------
Ran 4 tests in 0.243s

FAILED (errors=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_gates
```
Exit 0.
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.710s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph
```
Exit 1.
```text
F.....
======================================================================
FAIL: test_a_complete_arm_and_monitor_run_load_no_retired_module (tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module)
Run the real arm (fakes at the hardware seams; the cadence probe's real
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/hazards/test_import_graph.py", line 217, in test_a_complete_arm_and_monitor_run_load_no_retired_module
    self.assertEqual(report["decision"], "GO")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'NULL' != 'GO'
- NULL
+ GO


----------------------------------------------------------------------
Ran 6 tests in 3.482s

FAILED (failures=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist
```
Exit 0.
```text
................s......
----------------------------------------------------------------------
Ran 23 tests in 12.823s

OK (skipped=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q1WithheldCensusTests
```
Exit 0.
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.003s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q1MissingFilesCLIChainTests
```
Exit 0.
```text
BYTES_Q1_CHAIN={"case": "both", "evidence": [{"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "blinded-before-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit-keys", "stdout": "{\"keys\": [\"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmpz9ofdcj8/fit-keys\", \"stage\": \"fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit", "stdout": "{\"stage\": \"fit\", \"predictions_sha256\": \"8de5a55d4d6c06e9b03adeb4db44bb7bcf829dabbb1e4d67517fa41d7467595c\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmpz9ofdcj8/fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "stage1-git-commit", "stdout": "03becd51c81f15b9000574087cb72c93ca693ba2"}, {"exit": 0, "h1": [{"flags": ["bytes.withheld_missing"], "pass_id": "mean", "status": "missing"}], "h2": [{"analysis": "primary", "k": 9, "n": 9}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 9}], "moe": [{"answer": "missing", "flags": ["bytes.withheld_missing"], "status": "missing"}], "passes": [{"flags": ["bytes.withheld_missing"], "pass_id": 1, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}, {"flags": ["bytes.withheld_missing"], "pass_id": 2, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}], "point": [{"flags": ["bytes.withheld_missing"], "n_passes": 0, "pass_status": "no_pass", "status": "missing"}], "stage": "blinded-post-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "heldout-keys", "stdout": "{\"keys\": [\"Llama-3.3-70B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-14B-4bit|bytes-synthetic|512\", \"Qwen3-30B-A3B-4bit|bytes-synthetic|512\", \"Qwen3-32B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"Qwen3-8B-8bit|bytes-synthetic|512\", \"Qwen3-Next-80B-A3B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3.5-122B-A10B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmpz9ofdcj8/heldout-keys\", \"stage\": \"heldout\"}"}, {"exit": 0, "h1": [{"flags": ["bytes.withheld_missing"], "pass_id": "mean", "status": "missing"}], "h2": [{"analysis": "primary", "k": 9, "n": 9}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 9}], "moe": [{"answer": "missing", "flags": ["bytes.withheld_missing"], "status": "missing"}], "passes": [{"flags": ["bytes.withheld_missing"], "pass_id": 1, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}, {"flags": ["bytes.withheld_missing"], "pass_id": 2, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}], "point": [{"flags": ["bytes.withheld_missing"], "n_passes": 0, "pass_status": "no_pass", "status": "missing"}], "stage": "heldout", "stdout": "{\"stage\": \"heldout\", \"predictions_sha256\": \"8de5a55d4d6c06e9b03adeb4db44bb7bcf829dabbb1e4d67517fa41d7467595c\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmpz9ofdcj8/heldout\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "unblind", "stdout": "{\"export\": \"/tmp/jwtmp-byrev.89okO0/tmpz9ofdcj8/unblinded.csv\", \"flags\": [\"bytes.withheld_missing\"], \"rows\": 63, \"unblinded\": true}"}], "sessions": 12}
.BYTES_Q1_CHAIN={"case": "optional", "evidence": [{"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "blinded-before-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit-keys", "stdout": "{\"keys\": [\"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmpp_v9297q/fit-keys\", \"stage\": \"fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit", "stdout": "{\"stage\": \"fit\", \"predictions_sha256\": \"3839c8dd83c35c00365d2307f4309c176f04dbf437c75b2fef65aa08e7511347\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmpp_v9297q/fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "stage1-git-commit", "stdout": "68c4b9b3f182cf01f54f38cf75807718619d9d20"}, {"exit": 0, "h1": [{"pass_id": "mean", "word": "neither"}, {"pass_id": 1, "word": "neither"}], "h2": [{"analysis": "primary", "k": 9, "n": 10}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 8}], "moe": [{"answer": "active"}], "passes": [{"flags": [], "pass_id": 1, "status": "computed"}], "point": [{"n_passes": 1, "pass_status": "one_pass", "status": "computed"}], "stage": "blinded-post-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "heldout-keys", "stdout": "{\"keys\": [\"Llama-3.3-70B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-14B-4bit|bytes-synthetic|512\", \"Qwen3-30B-A3B-4bit|bytes-synthetic|512\", \"Qwen3-32B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"Qwen3-8B-8bit|bytes-synthetic|512\", \"Qwen3-Next-80B-A3B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3.5-122B-A10B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmpp_v9297q/heldout-keys\", \"stage\": \"heldout\"}"}, {"exit": 0, "h1": [{"pass_id": "mean", "word": "bytes"}, {"pass_id": 1, "word": "bytes"}], "h2": [{"analysis": "primary", "k": 9, "n": 10}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 8}], "moe": [{"answer": "active"}], "passes": [{"flags": [], "pass_id": 1, "status": "computed"}], "point": [{"n_passes": 1, "pass_status": "one_pass", "status": "computed"}], "stage": "heldout", "stdout": "{\"stage\": \"heldout\", \"predictions_sha256\": \"3839c8dd83c35c00365d2307f4309c176f04dbf437c75b2fef65aa08e7511347\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmpp_v9297q/heldout\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "unblind", "stdout": "{\"export\": \"/tmp/jwtmp-byrev.89okO0/tmpp_v9297q/unblinded.csv\", \"rows\": 113, \"unblinded\": true}"}], "sessions": 11}
.BYTES_Q1_CHAIN={"case": "one", "evidence": [{"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "blinded-before-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit-keys", "stdout": "{\"keys\": [\"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmp42liv_dl/fit-keys\", \"stage\": \"fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "fit", "stdout": "{\"stage\": \"fit\", \"predictions_sha256\": \"f6c0626e63496d175e24958de3496b0ff33911a4f1899b423b9e21c9bad60413\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmp42liv_dl/fit\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "stage1-git-commit", "stdout": "c5af6b3749547853d65867a0f6cc91d49718d501"}, {"exit": 0, "h1": [{"flags": ["bytes.withheld_missing"], "pass_id": "mean", "word": "neither"}, {"flags": ["bytes.withheld_missing"], "pass_id": 1, "word": "neither"}], "h2": [{"analysis": "primary", "k": 9, "n": 10}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 9}], "moe": [{"answer": "active"}], "passes": [{"flags": [], "pass_id": 1, "status": "computed"}, {"flags": ["bytes.withheld_missing"], "pass_id": 2, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}], "point": [{"flags": ["bytes.withheld_missing"], "n_passes": 1, "pass_status": "one_pass", "status": "computed"}], "stage": "blinded-post-commit", "stdout": ""}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "heldout-keys", "stdout": "{\"keys\": [\"Llama-3.3-70B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3-1.7B-4bit|bytes-synthetic|512\", \"Qwen3-14B-4bit|bytes-synthetic|512\", \"Qwen3-30B-A3B-4bit|bytes-synthetic|512\", \"Qwen3-32B-4bit|bytes-synthetic|512\", \"Qwen3-4B-4bit|bytes-synthetic|512\", \"Qwen3-8B-4bit|bytes-synthetic|512\", \"Qwen3-8B-8bit|bytes-synthetic|512\", \"Qwen3-Next-80B-A3B-Instruct-4bit|bytes-synthetic|512\", \"Qwen3.5-122B-A10B-4bit|bytes-synthetic|512\", \"neg8_reference\"], \"release\": \"/tmp/jwtmp-byrev.89okO0/tmp42liv_dl/heldout-keys\", \"stage\": \"heldout\"}"}, {"exit": 0, "h1": [{"flags": ["bytes.withheld_missing"], "pass_id": "mean", "word": "bytes"}, {"flags": ["bytes.withheld_missing"], "pass_id": 1, "word": "bytes"}], "h2": [{"analysis": "primary", "k": 9, "n": 10}, {"analysis": "two_pass_sensitivity", "k": 9, "n": 9}], "moe": [{"answer": "active"}], "passes": [{"flags": [], "pass_id": 1, "status": "computed"}, {"flags": ["bytes.withheld_missing"], "pass_id": 2, "status": "missing", "withheld_config_row_count": 50, "withheld_row_count": 50}], "point": [{"flags": ["bytes.withheld_missing"], "n_passes": 1, "pass_status": "one_pass", "status": "computed"}], "stage": "heldout", "stdout": "{\"stage\": \"heldout\", \"predictions_sha256\": \"f6c0626e63496d175e24958de3496b0ff33911a4f1899b423b9e21c9bad60413\", \"out\": \"/tmp/jwtmp-byrev.89okO0/tmp42liv_dl/heldout\"}"}, {"exit": 0, "h1": [], "h2": [], "moe": [], "passes": [], "point": [], "stage": "unblind", "stdout": "{\"export\": \"/tmp/jwtmp-byrev.89okO0/tmp42liv_dl/unblinded.csv\", \"flags\": [\"bytes.withheld_missing\"], \"rows\": 63, \"unblinded\": true}"}], "sessions": 12}
.
----------------------------------------------------------------------
Ran 3 tests in 28.618s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.Q2CommitmentCLIChainTests
```
Exit 0.
```text
BYTES_Q2_CHAIN={"case": "comment", "fields_not_rebuilt": [], "flags": ["bytes.module_changed_after_commitment"], "module_digests": {"committed": "679b6fcc5f683254de30792c0ce30f5a6b6bb0f8bff8d0a54c3dd9faa5c53221", "evaluating": "361cff00ebf5b100c4158289a64a45eb3adbf589fab9af91428b7ff72b8f9a6f"}, "predictions_sha256": "4efe7530b03e80e0b5e73de5922513d93042f779bc9db1a084ba51939fa94d6d"}
BYTES_Q2_CHAIN={"case": "fit-line", "fields_not_rebuilt": ["rival_lines"], "flags": ["bytes.module_changed_after_commitment", "bytes.commitment_not_rebuilt"], "module_digests": {"committed": "3c33ae22167a33f9fad5b27d0e1c4a3c3cfdad00b028b3da42c700c43d61ceba", "evaluating": "361cff00ebf5b100c4158289a64a45eb3adbf589fab9af91428b7ff72b8f9a6f"}, "predictions_sha256": "95624b189f2589591b464de578a97bf94ea9cf7a97a39a4f77b606f587547802"}
.
----------------------------------------------------------------------
Ran 1 test in 15.174s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.SubsetReleaseChainTests
```
Exit 0.
```text
..
----------------------------------------------------------------------
Ran 2 tests in 43.769s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.BoundaryAndStagingTests
```
Exit 0.
```text
..........
----------------------------------------------------------------------
Ran 10 tests in 34.756s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_export_runs
```
Exit 0.
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.314s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph
```
Exit 1.
```text
F.....
======================================================================
FAIL: test_a_complete_arm_and_monitor_run_load_no_retired_module (tests.hazards.test_import_graph.ImportGraphTests.test_a_complete_arm_and_monitor_run_load_no_retired_module)
Run the real arm (fakes at the hardware seams; the cadence probe's real
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-by-rev/tests/hazards/test_import_graph.py", line 217, in test_a_complete_arm_and_monitor_run_load_no_retired_module
    self.assertEqual(report["decision"], "GO")
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'NULL' != 'GO'
- NULL
+ GO


----------------------------------------------------------------------
Ran 6 tests in 3.154s

FAILED (failures=1)
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_analysis.ReviewInputTests
```
Exit 0.
```text
...
----------------------------------------------------------------------
Ran 3 tests in 9.537s

OK
```

```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census
```
Exit 0.
```text
{
 "unlisted": [],
 "stale": [],
 "miscounted": [],
 "guard_changed": [],
 "scope_gaps": []
}
```

```sh
git -C /Users/edr/code/JouleWise-by-rev diff --exit-code bda481d5a -- configs/b6/packs/alpha/registration.json configs/b6/packs/beta/registration.json configs/b6/packs/gamma/registration.json configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json
```
Exit 0.
```text
(empty: replication registrations and plan trees byte-identical)
```

```sh
git -C /Users/edr/code/JouleWise-by-rev diff --check
```
Exit 0.
```text
(empty)
```

Final state: implementation complete within authorized files; acceptance partial due to NEEDS_SCOPE and sandbox dynamic-proof limitation. This slice does not claim BY-REV-FIX COMPLETE.

### Baseline multiple-export CLI regression (isolated baseline parser)
This replay uses bda481d5a's CLI source with the corrected library and current production-shaped fixture. It isolates the baseline CLI's one-directory parser; the initial red input tests above separately cover baseline library and manifest defects.
```sh
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byrev.XXXXXX) /opt/homebrew/bin/python3.13 -B - <<'PYREPLAY'
from pathlib import Path
import os, subprocess, tempfile, unittest
from unittest.mock import patch
from tests.test_bytes_analysis import ReviewInputTests, ROOT
with tempfile.TemporaryDirectory() as temp:
 script=Path(temp)/'bytes_analyze_baseline.py'
 script.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show','bda481d5a:scripts/bytes_analyze.py']))
 original=subprocess.run
 def baseline_cli(args, **kwargs):
  if isinstance(args,list) and 'scripts/bytes_analyze.py' in args:
   args=[str(script) if v=='scripts/bytes_analyze.py' else v for v in args]
   kwargs['env']={**os.environ,'PYTHONPATH':str(ROOT)}
  return original(args,**kwargs)
 with patch('subprocess.run',side_effect=baseline_cli):
  result=unittest.TextTestRunner().run(unittest.TestSuite([ReviewInputTests('test_twelve_in_place_session_exports_match_single_directory_cli')]))
 raise SystemExit(not result.wasSuccessful())
PYREPLAY
```
Exit 1. Baseline subprocess exits 2: `bytes_analyze_baseline.py: error: unrecognized arguments:` followed by the eleven additional per-session export directories. `Ran 1 test in 6.792s; FAILED (failures=1)`. Corrected CLI's three ReviewInputTests pass, including the final production copied-export extension (9.537s).

### Independent code inspection
`git diff --check`: exit 0, empty. Modified paths inspected against exhaustive WRITE_SCOPE; all repository writes are authorized. No generator drift or unrelated dirty paths were present at intake. No .git writes attempted. The initial minimal copied-sidecar test passes; the final production-shaped copied session additionally checks the real CLI's missing pass rows, exact sidecar row count and absolute checked store path.

## OPEN ISSUES — FINAL
1. NEEDS_SCOPE: configs/campaigns/bytes_mac_check/plan_tree.json. The required generator/check and its test remain red until the director permits the generated update or rules on this acceptance dependency. Existing key-only kit external_inputs defect is disclosed above.
2. Dynamic import graph proof cannot obtain host process-group census in this sandbox; five static checks pass. Lead must rerun the dynamic proof in a permitted environment; no approval bypass requested or attempted.
3. Deferred topics in the brief remain deferred: sessions producer, commitment manifest digest semantics, two-commitment table, stage-1 commit verification, registration slots/text.

## NEEDS_RULING — FINAL
none (scope expansion is required, not a data-count or printed-number ruling).
