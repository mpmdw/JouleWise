```json
{
"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Implemented ruling 79a within scope; both delivery counterexamples are killed; remaining suite failures reproduce baseline/environment limitations.",
"workspace":{"base_requested":"df5c483e","base_mode":"exact","head_start":"df5c483e01f85a8f4e35a0c3d076551300616d4b","head_end":"df5c483e01f85a8f4e35a0c3d076551300616d4b","upstream_end":"6032b9e93220f9c9b9a04ca6d1dc75aa4aa92942","branch":null},
"pathspec":["scripts/run_night.py","tests/test_run_night.py"],"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"pending_verification"},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-round4-final-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night > /tmp/stagea-round4-run-night-final.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 224 tests in 146.462s","FAILED (failures=1, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 JOULEWISE_CUSTODY_PARENT=/tmp/stagea-round4-related-custody JOULEWISE_ADDITIONAL_CUSTODY_PARENTS='[]' /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_night_gate tests.test_gen_evidence_night tests.test_quiet_predicate_campaign tests.test_night_agent_install > /tmp/stagea-round4-related.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 163 tests in 921.132s","FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"suite","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B scripts/quick_suite.py --tier quick --workers 4 > /tmp/stagea-round4-quick.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["QUICK SUMMARY tier=quick modules=153 excluded=89 failures=1 seconds=104.114 result=FAIL"]},"expected":{"exit_code":0,"tail_regex":"result=PASS"}},
{"id":"V4","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest -v tests.test_run_night.CourierDeliveryBoundaryTests > /tmp/stagea-round4-boundary-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 16 tests in 5.093s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V5","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nfrom pathlib import Path\npath = Path('/tmp/stagea-round3-audit/evidence-inventory.py')\n# The publisher's new contract returns None, not an arbitrary Mock object.\nsource = path.read_text().replace(\"mock.patch.object(d,'_durable_record')\", \"mock.patch.object(d,'_durable_record',return_value=None)\")\nexec(compile(source, str(path), 'exec'))\nPY","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["{\"payload\": \"quiet_predicate_evidence\", \"unreadable_outcome\": true, \"exception\": null, \"rc\": 0, \"courier_calls\": 1, \"launches\": 1, \"directory_writable\": true, \"courier_outcome\": {\"attempted\": 1, \"heartbeat_seen\": true, \"last_error\": null, \"sent\": true}}","AssertionError"]},"expected":{"exit_code":1,"tail_regex":"AssertionError"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp TEMP=/tmp TMP=/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nfrom pathlib import Path\npath = Path('/tmp/stagea-round3-audit/concurrent-refusal.py')\nsource = path.read_text()\na = source.index('    barrier=')\nb = source.index('    def wait(', a)\nsource = source[:a] + '''    entered, release = threading.Event(), threading.Event()\n    original = driver._evidence_cleanup_error\n    repairs = []\n    heartbeat = night/'courier.heartbeat'\n    heartbeat.write_bytes(b'previous heartbeat')\n    def repair(*args):\n        repairs.append(True)\n        entered.set()\n        if not release.wait(5):\n            raise RuntimeError('owner not released')\n        return original(*args)\n''' + source[b:]\nsource = source.replace(\"mock.patch.object(campaign,'write_refusal',side_effect=write_refusal)\", \"mock.patch.object(driver,'_evidence_cleanup_error',side_effect=repair)\")\na = source.index('            futures=')\nb = source.index('    paths=', a)\nsource = source[:a] + '''            winner = pool.submit(call)\n            try:\n                assert entered.wait(5)\n                loser = pool.submit(call).result(timeout=5)\n                assert loser['attempted'] == 0 and loser['sent'] is False\n                assert heartbeat.read_bytes() == b'previous heartbeat'\n                assert len(repairs) == 1\n            finally:\n                release.set()\n            results = [winner.result(timeout=5), loser]\n''' + source[b:]\nsource = source.replace('    assert len(paths)==2,paths', \"    print(json.dumps({'results':results,'refusal_documents':len(paths),'launches':launch.call_count,'repair_calls':len(repairs)}),flush=True)\\n    assert len(paths)==2,paths\")\nimport sys\nsys.path.insert(0, str(path.parent))\nexec(compile(source, str(path), 'exec'))\nPY","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["{\"results\": [{\"attempted\": 1, \"sent\": true, \"heartbeat_seen\": true, \"last_error\": null}, {\"attempted\": 0, \"sent\": false, \"heartbeat_seen\": false, \"last_error\": \"courier lock belongs to a live process\"}], \"refusal_documents\": 1, \"launches\": 1, \"repair_calls\": 1}"]},"expected":{"exit_code":1,"tail_regex":"\"refusal_documents\": 1, \"launches\": 1"}}
],
"flags":[
{"id":"F1","kind":"environment","level":"nonblocking","text":"Sandbox denies /bin/ps; pgrep cannot obtain the process list. Related cleanup test and two quick-tier AXI identity tests fail; named in notes.","needs":"Lead reruns host-dependent checks outside this sandbox."},
{"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Blocked-journal supervision test hits its 8 s watchdog; reproduced with unchanged df5c483e driver.","needs":"Lead adjudicates the pre-existing watchdog failure before accepting the suite gate."},
{"id":"F3","kind":"residual_risk","level":"nonblocking","text":"Pre-existing lock metadata interleave, dead-man reporting block, pre-boundary chain-exit persistence and Popen failures remain deferred by 79a.","needs":""}
]
}
```

## Change

- **W1:** `run_night` guards post-chain result preparation and exclusive fallback creation. `_write_result` returns its inventory for inline diagnostics; `_finish_reporting` threads the report into `run_courier`. `_courier_optional` and `_courier_prelaunch` provide guarded preparation and filesystem-independent fallback argv.
- **W2:** `run_courier` repairs evidence only after acquiring ownership. A refused caller returns without repair or heartbeat inspection/mutation. Lock implementation unchanged.
- **W3:** `_artifact_entry` records unreadable artifacts; `_artifact_list` marks incomplete discovery; `_durable_record` skips error entries and returns diagnostics safely.
- **W4:** Courier attempt records, logs, sent-marker fsync, lock release, outcome writing, and subsequent publication cross the guard. The safety-suppressed path remains separate.
- **W5:** Added 16 regressions, including injected read denial, real chmod denial, and event-controlled concurrent callers. The eleven protected outcome tests and their delivery/repair helpers remain byte-identical and green.
- **W6:** Same-signature review found **no surviving optional-operation exception site within 79a’s accepted boundary**. After chain facts and successful courier-lock acquisition, optional preparation exceptions cannot prevent reaching `Popen`.

No commits. `git diff --check` passed.

## Verification notes

V5/V6 intentionally exit 1: their old defect assertions now fail. Reproduction sources were adapted in memory only: the publisher mock now returns `None`, and concurrency uses ownership events instead of the refusal barrier.

Remaining failures:

- `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`: identical eight-second timeout reproduced with the base driver.
- `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted`: process census unavailable.
- `AxiControllerEventTests.test_campaign_prebundle_process_failure_retains_identity_receipt_and_row`
- `AxiControllerEventTests.test_campaign_zero_exit_without_finalized_bundle_is_dispatch_failure`

The latter two fail because process identity is unavailable in this sandbox. Verification used the requested matrix; unrestricted discovery includes canonical-checkout dependencies excluded by A211 and this worktree-only brief.

## Residual risk

The deferred lock race and dead-man reporting block remain unchanged. Exception containment provides no wall-clock bound. Transport was mocked; no live email or hardware validation is claimed.

Next: lead delta re-audit, host-dependent verification, and adjudication of the baseline watchdog failure before acceptance.