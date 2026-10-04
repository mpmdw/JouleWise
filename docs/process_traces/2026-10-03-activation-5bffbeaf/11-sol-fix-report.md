```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"blocked",
"completion":"partial",
"summary":"G2-a provenance fixed; w2 replay reaches the correct measurement refusal. Commit and one out-of-scope consumer remain blocked.",
"workspace":{"base_requested":"e256ac28","base_mode":"exact","head_start":"e256ac280d1d3b7461cfb6fa400fa76296d357bb","head_end":"e256ac280d1d3b7461cfb6fa400fa76296d357bb","upstream_end":"e256ac280d1d3b7461cfb6fa400fa76296d357bb","branch":"fix/2026-10-03-g2a-w2-summary-config-provenance"},
"pathspec":["scripts/summarize_g2a_prefill_probe.py","scripts/issue_g2a_prefill_prompt_pin.py","tests/test_summarize_g2a_prefill_probe.py","tests/test_issue_g2a_prefill_prompt_pin.py","tests/test_harvest_g2a_window.py"],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"needs_ruling"},
"verification":[
{"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_harvest_g2a_window tests.test_select_g2a_prefill_length","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 87 tests in 29.516s","OK"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 87 tests.*OK"}},
{"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_custody_mode_inventory","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 42.988s","OK"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 7 tests.*OK"}},
{"id":"V3","kind":"smoke","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -u - <<'PY'\nimport hashlib, json, shutil\nfrom pathlib import Path\nfrom scripts import summarize_g2a_prefill_probe as summary\nfrom scripts import select_g2a_prefill_length as selector\nbase = Path('/tmp/g2a-w2-replay-5bffbeaf')\ng2a = base / 'd117-g2a-prefill-probe-20261003T1748Z'\nsource = Path('/Users/edr/night-g2a') / g2a.name\nharvest_source = Path('/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z/harvest.json')\nharvest_copy = base / 'w2-harvest.original.json'\nshutil.copy2(harvest_source, harvest_copy)\nassert harvest_copy.read_bytes() == harvest_source.read_bytes()\nvalid = {row['run_id'] for row in json.loads(harvest_copy.read_bytes())['members'] if row['valid']}\nsummary.REPO_ROOT = base / 'repo-inputs'\noutput = base / 'final-replay'\noutput.mkdir()\nrc = summary.main(['--config-root', str(g2a / 'prefill-probe-configs'), '--input-inventory', str(g2a / 'window-plan/g2a-input-inventory.replay.json'), '--runs-root', str(g2a / 'runs'), '--counts-output', str(output / 'counts.json'), '--summary-output', str(output / 'summary.json')], valid_run_ids=valid)\nprint('VALID_MEMBERS', len(valid))\nprint('SUMMARY_EXIT', rc)\nif rc == 0:\n    print('SUMMARY_ROWS', json.dumps(json.loads((output / 'summary.json').read_bytes()), sort_keys=True))\n    rc = selector.main(['--summary', str(output / 'summary.json'), '--output', str(output / 'selection.json')])\n    print('SELECTION_EXIT', rc)\n    print('SELECTION_RESULT', json.dumps(json.loads((output / 'selection.json').read_bytes()), sort_keys=True))\nfiles = [p for p in source.rglob('*') if p.is_file()]\nassert all(hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256((g2a / p.relative_to(source)).read_bytes()).digest() for p in files)\nprint('SOURCE_COPY_VERIFIED', len(files), 'files; protected source unchanged')\nraise SystemExit(rc)\nPY","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["VALID_MEMBERS 12","SUMMARY_EXIT 0","SELECTION_EXIT 0","SELECTION_RESULT {\"collection_prefill_tokens\": 4096, \"qualifying_prefill_tokens\": [], \"refusal\": {\"code\": \"no_g2a_prefill_rung_qualifies\", \"fallback_action\": \"collect_at_4096\", \"fallback_label\": \"collect-at-4096\", \"result_reporting\": {\"count_below_pre_registered_floor\": {\"count_range\": \"3-4\", \"disclose_reducer_resolvable_result\": true, \"refusal\": \"below the pre-registered count floor of 5\"}, \"count_below_reducer_minimum\": {\"count_range\": \"<3\", \"refusal\": \"not_resolvable_sample_count\"}}}, \"rule\": {\"all_small_count_ge_5_required\": true, \"ladder_prefill_tokens\": [512, 1024, 2048, 4096], \"minimum_overlapping_power_interval_count\": 5, \"minimum_small_members_per_rung\": 5, \"reducer_min_phase_samples\": 3, \"selection\": \"shortest_qualifying_rung\"}, \"schema_version\": \"joulewise.g2a_prefill_selection.v1\", \"selected_prefill_tokens\": null, \"status\": \"refused\", \"summary_sha256\": \"5c7f185d6d841d044a389fa0ef01d770e575eace5dac6bd448daffcef28a02be\"}","SOURCE_COPY_VERIFIED 375 files; protected source unchanged"]},"expected":{"exit_code":0,"tail_regex":"(?s)SUMMARY_EXIT 0.*SELECTION_EXIT 0.*no_g2a_prefill_rung_qualifies.*SOURCE_COPY_VERIFIED 375"}},
{"id":"V4","kind":"inspection","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
{"id":"V5","kind":"suite","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests","cwd":".","observed":{"result":"fail","exit_code":130,"tail":["KeyboardInterrupt"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V6","kind":"other","cmd":"git add scripts/summarize_g2a_prefill_probe.py scripts/issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_issue_g2a_prefill_prompt_pin.py tests/test_harvest_g2a_window.py && git commit -m 'Bind G2-a run provenance to runner-normalized input configs'","cwd":".","observed":{"result":"fail","exit_code":128,"tail":["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-5bffbeaf-fix/index.lock': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"Bind G2-a run provenance"}}
],
"flags":[
{"id":"F1","kind":"scope_deviation","level":"blocking","text":"NEEDS_SCOPE: joulewise/window_duration_margins.py:553 compares run config bytes directly to source-config pins supplied by the campaign generator. Confirmed read-only refusal on the scratch run. No out-of-scope repository paths modified.","needs":"Grant the requested paths for the same provenance repair, or explicitly limit this task to G2-a."},
{"id":"F2","kind":"environment","level":"blocking","text":"No commit created: sandbox denied index.lock creation in the primary repository's Git metadata. No approval route is available; HEAD is unchanged.","needs":"Lead must stage and commit the five modified files from an authorized Git session."},
{"id":"F3","kind":"verification_gap","level":"nonblocking","text":"Canonical suite intentionally interrupted at the scope handback; no full-suite pass count. Requested focused tests and custody inventory passed. Replay used the original harvest's recorded valid-member set; optional fresh strict hardware-bundle revalidation was interrupted.","needs":"Run the canonical suite and final verification after scope disposition."}
],
"scope_expansion":{"requested_paths":["joulewise/window_duration_margins.py","tests/test_window_duration_margins.py"],"reason":"The wider consumer audit found the same source-byte versus runner-normalized-byte defect outside WRITE_SCOPE.","blocked_work":"Remediation and regression coverage for the window-duration consumer; the scoped G2-a fix and mandatory w2 summary/selection replay are complete.","minimal_change":"Authenticate the pack's source config bytes against its input pin, derive the run hash through the imported runner parser/hash helper, and bind run bytes and metadata to that hash; add real-writer fixture coverage."}
}
```

## Change

Imported the runner’s parser and deterministic config-hash helper. Summary and prompt-pin validation now bind inventory input bytes, normalized run bytes, and metadata hashes. Fixtures use the real bundle writer and reject non-default changes even when metadata is rebound.

Replay exposed and fixed the empty-rung minimum-count defect: it now emits `null`, allowing the correct measurement refusal.

Commit SHA: **none**. Git staging was denied by the sandbox. Nothing was pushed.

## Verification notes

Replay used the archived harvest’s 12 valid members and relocated inventory paths in scratch. Its next refusal is `no_g2a_prefill_rung_qualifies`, the expected measurement outcome.

The canonical suite remains incomplete. No custody replay-mode calls changed, so the allowlist required no update.

## Residual risk

[window_duration_margins.py](/Users/edr/code/JouleWise-wt-5bffbeaf-fix/joulewise/window_duration_margins.py:553) retains the same defect outside scope. The lead must grant the requested paths, complete verification, and commit the five-file diff.