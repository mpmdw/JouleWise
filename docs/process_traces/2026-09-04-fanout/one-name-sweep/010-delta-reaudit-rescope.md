```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "CLEAN: retired scanner gone; ruled regression and evidence refusals pass; scope is exact.",
  "verdict": {
    "findings": [],
    "new_defects": "none",
    "same_signature": "No same-signature repeat occurred; a repeat now would be a third occurrence.",
    "retired_mechanism": "gone; grep, unchanged linter surfaces, and path inventory exclude a renamed replacement",
    "acceptance": "the single named change-then-exact-restore test fails with the retired current-last-touch equality rule and passes on real code",
    "evidence_fence": "stored-commit resolution, historical script SHA-256, input SHA-256, regenerated JSON, and regenerated Markdown all refuse under mutation",
    "landing_scope": "only mission paths plus traces; state docs untouched"
  },
  "workspace": {
    "base_requested": "4b9e029071a88e99dc31dc5c8216d7df6a9c1624",
    "base_mode": "exact",
    "head_start": "4b9e029071a88e99dc31dc5c8216d7df6a9c1624",
    "head_end": "4b9e029071a88e99dc31dc5c8216d7df6a9c1624",
    "upstream_end": "a1184ccae2f62535b53c8c6e09c1bac37ff7f795",
    "branch": "feat/2026-09-04-fan-one-name-sweep"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/one-name-sweep/010-delta-reaudit-rescope.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "test \"$(git rev-parse HEAD)\" = 4b9e029071a88e99dc31dc5c8216d7df6a9c1624; git show --no-ext-diff --name-status --format=%H HEAD | sed '/^$/d'",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["4b9e029071a88e99dc31dc5c8216d7df6a9c1624","A\tdocs/process_traces/2026-09-04-fanout/one-name-sweep/09-sol-rescope-report.md","M\ttests/test_issue_dg071_dg075_statistics.py"]},
      "expected": {"exit_code":0,"tail_regex":"^4b9e0290[0-9a-f]{32}\\nA\\tdocs/process_traces/.*/09-sol-rescope-report\\.md\\nM\\ttests/test_issue_dg071_dg075_statistics\\.py$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); test -z \"$(rg -n 'ONE_NAME_RULES|ONE_NAME_TEXT_SUFFIXES|find_one_name_violations|run_one_name|one-name finding|enforce one name per paper object' scripts/paper_terms_lint.py tests/test_paper_terms_lint.py)\"; git diff --quiet \"$base\"..HEAD -- scripts/paper_terms_lint.py tests/test_paper_terms_lint.py; test -z \"$(git diff --name-only \"$base\"..HEAD -- 'scripts/**' 'joulewise/**' 'configs/**')\"; test \"$(rg -c '^    def test_change_then_exact_restore_replays_with_divergence_warning' tests/test_issue_dg071_dg075_statistics.py)\" = 1; echo RETIRED_MECHANISM_GONE",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["RETIRED_MECHANISM_GONE"]},
      "expected": {"exit_code":0,"tail_regex":"^RETIRED_MECHANISM_GONE$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "d=$(mktemp -d); git clone -q . \"$d/r\"; f=\"$d/r/tests/test_issue_dg071_dg075_statistics.py\"; perl -0pi -e 's/if current_last_touch != stored_commit:\\n        warnings\\.warn\\(/if current_last_touch != stored_commit:\\n        raise AssertionError(\"current_last_touch_equality_block\")\\n        warnings.warn(/' \"$f\"; cd \"$d/r\"; if PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics.Dg071Dg075StatisticsTests.test_change_then_exact_restore_replays_with_divergence_warning >\"$d/out\" 2>&1; then exit 1; fi; rg -q current_last_touch_equality_block \"$d/out\"; echo COUNTERFACTUAL_RED",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["COUNTERFACTUAL_RED"]},
      "expected": {"exit_code":0,"tail_regex":"^COUNTERFACTUAL_RED$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics.Dg071Dg075StatisticsTests.test_change_then_exact_restore_replays_with_divergence_warning && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_dg071_dg075_statistics",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 1 test in 0.293s","OK","Ran 28 tests in 1.295s","OK"]},
      "expected": {"exit_code":0,"tail_regex":"(?s)Ran 1 test in .*\\n\\nOK.*Ran 28 tests in .*\\n\\nOK"}
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport copy,json,subprocess,tempfile\nfrom pathlib import Path\nfrom tests.test_issue_dg071_dg075_statistics import ROOT,ISSUER,_verify_asymmetric_replay\nsrc=ROOT/'docs/paper/round7/dg071-dg075-statistics.json'; base=json.loads(src.read_text()); bundle=Path('/Users/edr/code/JouleWise')/base['input_bundle']['path']\ncases=(('stored_commit_unresolvable',lambda p:p['producer'].__setitem__('git_commit','0'*40)),('historical_script_sha256_mismatch',lambda p:p['producer'].__setitem__('git_commit','375656a384e5583317d1f33878bd559605eaed02')),('bundle_sha256_mismatch',lambda p:p['input_bundle'].__setitem__('sha256','0'*64)),('semantic_json_replay_mismatch',lambda p:p['statistics']['DG-071'].__setitem__('median_ms','counterfactual')),('semantic_markdown_replay_mismatch',lambda p:None))\nwith tempfile.TemporaryDirectory() as d:\n for name,mutate in cases:\n  payload=copy.deepcopy(base); mutate(payload); issued=Path(d)/(name+'.json'); issued.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\\n')\n  if name.endswith('markdown_replay_mismatch'): issued.with_suffix('.md').write_bytes(src.with_suffix('.md').read_bytes()+b'tamper\\n')\n  try: _verify_asymmetric_replay(checkout=ROOT,bundle=bundle,issued_json=issued,replay_json=Path(d)/(name+'-replay.json'))\n  except Exception as exc:\n   ok=(name=='stored_commit_unresolvable' and isinstance(exc,subprocess.CalledProcessError)) or (name=='bundle_sha256_mismatch' and isinstance(exc,ISSUER.IssuanceRefused) and exc.reason==name) or (name not in ('stored_commit_unresolvable','bundle_sha256_mismatch') and isinstance(exc,AssertionError) and name in str(exc)); assert ok,(name,repr(exc)); print('EVIDENCE_FENCE_REFUSED',name)\n  else: raise AssertionError(name+' did not refuse')\nPY",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["EVIDENCE_FENCE_REFUSED stored_commit_unresolvable","EVIDENCE_FENCE_REFUSED historical_script_sha256_mismatch","EVIDENCE_FENCE_REFUSED bundle_sha256_mismatch","EVIDENCE_FENCE_REFUSED semantic_json_replay_mismatch","EVIDENCE_FENCE_REFUSED semantic_markdown_replay_mismatch"]},
      "expected": {"exit_code":0,"tail_regex":"^EVIDENCE_FENCE_REFUSED .+(\\nEVIDENCE_FENCE_REFUSED .+){4}$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); allowed='^(docs/paper/(draft-v1\\.md|results-fill-registry\\.md|round7/(built-terms-lexicon\\.md|survival-map\\.md))|tests/test_issue_dg071_dg075_statistics\\.py|docs/process_traces/2026-09-04-fanout/one-name-sweep/[0-9]+[-a-z0-9]*\\.md)$'; test -z \"$(git diff --name-only \"$base\"..HEAD | rg -v \"$allowed\" || true)\"; test -z \"$(git diff --name-only \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md AGENT_PLAN.md docs/process/state_kernel.json)\"; echo LANDING_SCOPE_OK",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["LANDING_SCOPE_OK"]},
      "expected": {"exit_code":0,"tail_regex":"^LANDING_SCOPE_OK$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "set -e; report=docs/process_traces/2026-09-04-fanout/one-name-sweep/010-delta-reaudit-rescope.md; sed -n '2,/^```$/p' \"$report\" | sed '$d' | python3 -m json.tool >/dev/null; test \"$(sed -n '2,/^```$/p' \"$report\" | sed '$d' | wc -c | tr -d ' ')\" -le 8192; git diff --no-index --check /dev/null \"$report\" >/dev/null || test $? -eq 1; echo REPORT_VALID",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["REPORT_VALID"]},
      "expected": {"exit_code":0,"tail_regex":"^REPORT_VALID$"}
    }
  ],
  "flags": []
}
```

## Findings

None. The re-scope is clean. No same-signature repeat occurred; a repeat now would be a third occurrence.

## Residual risk

None within the requested delta. Only the touched test module ran, per preflight.
