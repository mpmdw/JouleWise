```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"Regenerated the source-line-pinned sheet; relocation failures are stale v1 mint fixture hashes in an unlisted test file.","workspace":{"base_requested":"f5abdea0","base_mode":"exact","head_start":"f5abdea040166dabf1c25402a5b59841b787300e","head_end":"f5abdea040166dabf1c25402a5b59841b787300e","upstream_end":null,"branch":"feat/2026-09-04-fb-metadata"},"pathspec":["docs/paper/round7/dependence-sensitivity.md","docs/process_traces/2026-09-04-peer-audit/48-fb-v2-ci-fix-report.md"],"unowned_dirty":["docs/process_traces/2026-09-04-peer-audit/46-fb-v2-round-s-report.md"],"verdict":{"implementation":"partial","acceptance":"needs_ruling"},"verification":[{"id":"V1","kind":"test","cmd":"python3 -B -m unittest tests.test_dependence_sensitivity","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 29 tests in 5.286s","","FAILED (failures=3)"]},"expected":{"exit_code":0,"tail_regex":"Ran 29 tests in [0-9.]+s\\s+OK$"}},{"id":"V2","kind":"test","cmd":"python3 -B -m unittest tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 1 test in 5.340s","","FAILED (errors=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in [0-9.]+s\\s+OK$"}},{"id":"V3","kind":"test","cmd":"python3 -B -m unittest tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 1 test in 9.051s","","FAILED (errors=1)"]},"expected":{"exit_code":0,"tail_regex":"Ran 1 test in [0-9.]+s\\s+OK$"}},{"id":"V4","kind":"other","cmd":"python3 -B - <<'PY'\nimport unittest\nfrom joulewise import arm_readiness_evidence as evidence\nneedle = 'failed_ids = sorted('\nassert evidence._SUITE_SUBPROCESS.count(needle) == 1\nevidence._SUITE_SUBPROCESS = evidence._SUITE_SUBPROCESS.replace(\n    needle,\n    'if result.errors or result.failures:\\n'\n    '    raise RuntimeError(\"\\\\n\".join(detail for _, detail in (*result.errors, *result.failures)))\\n\\n'\n    + needle,\n)\nunittest.main(module=None, argv=['diagnose', 'tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation'])\nPY","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 1 test in 3.967s","","FAILED (errors=1)"]},"expected":{"exit_code":0,"tail_regex":""}},{"id":"V6","kind":"build","cmd":"python3 -B scripts/dependence_sensitivity.py --render-sheet > docs/paper/round7/dependence-sensitivity.md","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},{"id":"V7","kind":"test","cmd":"python3 -B -m unittest tests.test_dependence_sensitivity","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["----------------------------------------------------------------------","Ran 29 tests in 4.505s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 29 tests in [0-9.]+s\\s+OK$"}},{"id":"V8","kind":"other","cmd":"python3 -B - <<'PY'\nimport unittest\nfrom joulewise import arm_readiness_evidence as evidence\nprobe = '''\nfrom tests.test_mint_floor_artifact_generalized import generalized as gen\nfrom joulewise import detection_floor as df\nimport copy\nobservations = []\noriginal_build = gen._build_v2_artifacts\ndef observe_build(**kwargs):\n    artifact, components = original_build(**kwargs)\n    for index, (component, pin) in enumerate(zip(components, kwargs['pinset'].value['aggregate']['component_artifacts'])):\n        legacy = copy.deepcopy(component)\n        replacements = []\n        def visit(node):\n            if isinstance(node, dict):\n                for key, value in node.items():\n                    if key == 'single_count_discipline':\n                        assert value == df.attribution_single_count_discipline()\n                        node[key] = df.attribution_single_count_discipline(df.SINGLE_COUNT_DISCIPLINE_ID_V1)\n                        replacements.append(key)\n                    else:\n                        visit(value)\n            elif isinstance(node, list):\n                for value in node:\n                    visit(value)\n        visit(legacy)\n        digest = lambda value: hashlib.sha256((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\\\\n').encode()).hexdigest()\n        observations.append(f\"component {index}: v2={digest(component)}; v1-only={digest(legacy)}; pinned={pin['sha256']}; metadata_objects={len(replacements)}; v1_matches_pin={digest(legacy) == pin['sha256']}\")\n    return artifact, components\ngen._build_v2_artifacts = observe_build\n'''\nevidence._SUITE_SUBPROCESS = evidence._SUITE_SUBPROCESS.replace(\n    'result = unittest.TestResult()',\n    \"if any('test_v2_assurance_and_git_containment' in name for name in test_ids):\\n    exec(\" + repr(probe) + \")\\n\\nresult = unittest.TestResult()\",\n).replace(\n    'failed_ids = sorted(',\n    \"if result.errors and 'observations' in globals():\\n    raise RuntimeError('\\\\n'.join(observations))\\n\\nfailed_ids = sorted(\",\n)\nunittest.main(module=None, argv=['diagnose', 'tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation'])\nPY","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["----------------------------------------------------------------------","Ran 1 test in 3.936s","","FAILED (errors=1)"]},"expected":{"exit_code":0,"tail_regex":""}},{"id":"V9","kind":"other","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}},{"id":"V10","kind":"other","cmd":"python3 -B scripts/dependence_sensitivity.py --check-sheet","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":""}}],"flags":[{"id":"F1","kind":"scope_deviation","level":"blocking","text":"NEEDS_SCOPE before any unlisted edit: tests/test_mint_floor_artifact_generalized.py owns the stale golden hashes. No scope violation occurred.","needs":"Expand WRITE_SCOPE to that file and authorize its focused fixture checks; then rerun the two named relocation methods."}],"scope_expansion":{"requested_paths":["tests/test_mint_floor_artifact_generalized.py"],"reason":"Both relocation tests execute a mint-trust fixture whose frozen component hashes still bind canonical v1 discipline bytes; the lane now emits v2.","blocked_work":"Repair fixture hashes and add the regression, then establish passing relocation tests.","minimal_change":"Review and update current synthetic component hashes and dependent producer/self hashes with an independent fixture oracle; retain a v1 byte-preservation witness. Audit the same file's CLI component pins."}}
```

## Change

Regenerated the tracked sheet with its own renderer. Only the two `evaluate_claim` citations moved from line 257 to line 258. Before writing, an in-memory comparison asserted that replacing source-line numbers in both documents made them byte-identical; formula values, mathematical text, and all other prose are unchanged. All 29 tests in the sheet module now pass, including the three reported failures.

The relocation repair is blocked by exhaustive WRITE_SCOPE. The nested mint-trust fixture in `tests/test_mint_floor_artifact_generalized.py:8141` consumes `freeze_synthetic_v2_pinset()`; its constants at lines 1282-1303 still pin v1 discipline bytes. Changing the production validator or downgrading current output to satisfy those fixture hashes would be the wrong fix. No production or test source was changed. The required regression remains part of the requested scope expansion.

## Verification notes

V1 reproduced exactly three failures: `test_rendered_sheet_is_byte_equal_to_the_tracked_document`, `test_renderer_refuses_registered_alpha_or_multiplicity_constant_drift`, and `test_tail_replay_formula_values_and_source_locations_are_current`.

V2 and V3 reproduced the two named relocation errors. Their original traceback tails follow.

```text
E
======================================================================
ERROR: test_production_minted_dry_run_survives_repository_relocation (tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_production_minted_dry_run_survives_repository_relocation)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fb-metadata/tests/test_arm_readiness_dry_run.py", line 516, in test_production_minted_dry_run_survives_repository_relocation
    authored = evidence.author_arm_readiness_evidence(pack)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 3380, in author_arm_readiness_evidence
    item = _DERIVERS[kind](context)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 2149, in _derive_mint_trust
    result = _run_suite(context, kind, test_ids)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 781, in _run_suite
    raise _underivable(
    ...<4 lines>...
    )
joulewise.arm_readiness_evidence.EvidenceAuthoringError: focused suite refused: failures=0, errors=1, unexpected_successes=0

----------------------------------------------------------------------
Ran 1 test in 5.340s

FAILED (errors=1)
```

```text
E/opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/lib/python3.14/tempfile.py:962: ResourceWarning: Implicitly cleaning up <TemporaryDirectory '/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpof9g2bw2'>
  _warnings.warn(warn_message, ResourceWarning)

======================================================================
ERROR: test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change (tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-fb-metadata/tests/test_launch_window.py", line 835, in test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change
    self._mint_v4_arm()
    ~~~~~~~~~~~~~~~~~^^
  File "/Users/edr/code/JouleWise-wt-fb-metadata/tests/test_launch_window.py", line 606, in _mint_v4_arm
    authored = generic_evidence.author_arm_readiness_evidence(pack)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 3380, in author_arm_readiness_evidence
    item = _DERIVERS[kind](context)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 2149, in _derive_mint_trust
    result = _run_suite(context, kind, test_ids)
  File "/Users/edr/code/JouleWise-wt-fb-metadata/joulewise/arm_readiness_evidence.py", line 781, in _run_suite
    raise _underivable(
    ...<4 lines>...
    )
joulewise.arm_readiness_evidence.EvidenceAuthoringError: focused suite refused: failures=0, errors=1, unexpected_successes=0

----------------------------------------------------------------------
Ran 1 test in 9.051s

FAILED (errors=1)
```

V4 replayed only the named dry-run test with an in-memory modification to the nested unittest command string, exposing the failure details that the production author reports only as counts. It did not change files or admission behavior. The actual nested traceback was:

```text
RuntimeError: Traceback (most recent call last):
  File "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpya_s3k9f/repo/tests/test_mint_floor_artifact_generalized.py", line 8146, in test_v2_assurance_and_git_containment_are_required_provenance
    artifact = generalized.mint_multi_cell_authenticated_artifact(
        pinset_path=path,
    ...<4 lines>...
        project_tree_state="clean",
    )
  File "/private/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/tmpya_s3k9f/repo/scripts/mint_floor_artifact_generalized.py", line 3375, in mint_multi_cell_authenticated_artifact
    raise MintError(
    ...<2 lines>...
    )
scripts.mint_floor_artifact_generalized.MintError: aggregate/component hash mismatch: component artifact 0 expected 8ac980a543bfa7d61d4f1e8e849ba6ca12d6ac16320592ae081da2a2bca70495, observed dae1d43209662a471c1ff1d283f151c4296da58a6456177a9543e6b6061391e7
```

V8 replayed that same named test with a read-only diagnostic wrapper around component construction. The original artifacts were returned unchanged. Only detached copies had their six canonical discipline objects replaced by canonical v1 objects for independent `hashlib.sha256(json.dumps(..., indent=2, sort_keys=True, allow_nan=False) + newline)` comparison. Both old pinned hashes were recovered exactly:

```text
component 0: v2=dae1d43209662a471c1ff1d283f151c4296da58a6456177a9543e6b6061391e7; v1-only=8ac980a543bfa7d61d4f1e8e849ba6ca12d6ac16320592ae081da2a2bca70495; pinned=8ac980a543bfa7d61d4f1e8e849ba6ca12d6ac16320592ae081da2a2bca70495; metadata_objects=6; v1_matches_pin=True
component 1: v2=c12749ccf1691860c5635c08de5cafce9edf57f1f81604bead7951bc80925b9c; v1-only=a8c195553895a7a3d178336e0a1b133f84488ed68c6726c394966e7be61a0d70; pinned=a8c195553895a7a3d178336e0a1b133f84488ed68c6726c394966e7be61a0d70; metadata_objects=6; v1_matches_pin=True
```

This establishes metadata-byte drift, with no arithmetic or provenance-byte change in those components. Neither observed relocation traceback is a missing optional discipline refusal. There is no evidence here supporting a change to optional-absence admission. V4/V8 intentionally surface diagnostics by raising inside the subprocess, so their exit-1 tails are diagnostic evidence, not passing acceptance tests.

The pre-write source-line-only inspection (omitted from the envelope to keep its JSON below 8192 bytes) is replayable against the starting sheet using `git show f5abdea0:docs/paper/round7/dependence-sensitivity.md` in place of the first read. Its exact original command and tail were:

```sh
python3 -B - <<'PY'
import difflib
import re
from scripts import dependence_sensitivity as ds
old = ds.SHEET_OUTPUT_PATH.read_text(encoding='utf-8')
new = ds.render_sheet()
normalize = lambda value: re.sub(r'line [0-9]+', 'line <SOURCE>', value)
assert normalize(old) == normalize(new), 'STOP: renderer changes more than source line numbers'
print(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='tracked', tofile='renderer')), end='')
print('PASS: only source line numbers differ; formula values and prose are byte-identical')
PY
```

```text
PASS: only source line numbers differ; formula values and prose are byte-identical
```

Only the three authorized top-level unittest selections were run; the two additional diagnostic runs selected the same named dry-run method. Their own production author invokes nested evidence checks in temporary synthetic repositories. No discovery suite, additional launcher method, child Claude/Codex session, or real measurement checkout was used. No project commit was made; HEAD and branch stayed exact. The pre-existing untracked round-S report was preserved. The branch has no configured upstream, hence `upstream_end: null`.

## Residual risk

The two relocation tests remain failing until the lead expands scope, reviews and repairs the independently pinned current-v2 fixture hashes and their dependent self-hashes, and reruns the named methods. Preserve historical v1 byte evidence and current validation; add a regression at the fixture owner. The same file's separate CLI golden hashes need inspection during that repair; they were not exercised directly here. Lead-owned final review and PR CI remain pending.

