```json
[]
```

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Clean review: cleanup escalation, reaping, original assertion re-raise, success path, caller interaction, and commit isolation are correct.","pathspec":[],"verification":["Read git show 8b96bd4 and surrounding helper/callers in tests/test_bridge.py","git diff-tree: only tests/test_bridge.py modified","git diff --check 8b96bd4^ 8b96bd4: PASS","Real subprocess probes: already-exited communicate/reap, repeated communicate/close, TERM-timeout-KILL-reap, terminate-after-exit, and exception identity all PASS","Exact helper mock probes: unchanged success path and timeout escalation/assertion path PASS","python3 -m unittest tests.test_bridge attempted: sandbox-blocked; all 57 setups failed because no writable temporary directory was available"],"flags":["no_edits","verification_incomplete","read_only_sandbox"]}