```json
[
  {
    "title": "Reap the handshake child when sentinel assertions fail",
    "file": "tests/test_bridge.py",
    "line_hint": "264-278",
    "severity": "should-fix",
    "argument": "The helper starts a subprocess and then performs readiness and sentinel assertions without cleanup. If either assertion fails while the child remains alive, the Popen handle is lost and the child may remain blocked or contaminate later tests. Fault injection reproduced this path: a live child received no terminate, kill, or communicate call after the missing-sentinel assertion.",
    "suggested_fix": "Wrap the handshake assertions in try/except BaseException; on failure terminate and communicate with a timeout, escalate to kill if necessary, then re-raise. Also reap an already-exited child to close its pipes."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"One round-3 test-harness defect found: handshake assertion failures can leave an unreaped child. No production defect found in command naming, structured-error cardinality, handler exception boundaries, env-flag primitive behavior, sentinel placement, import side effects, or read-only commands.","pathspec":[],"verification":["Read exact git diff 63dd5f1..d0424ce for scripts/bridge and tests/test_bridge.py plus surrounding decorator, lock, primitive-wrapper, parser, and test-helper code.","Fault injection passed for all 8 mutating command names, single structured lock/repository errors, handler-boundary no-double-output behavior, env-flag lock bypass, and all 3 read-only command schemas.","Reproduced missing-sentinel cleanup defect with a mocked live Popen; terminate/kill/communicate were not called.","git diff --check passed; both files parsed successfully with ast.parse; worktree remained clean.","python3 -m unittest tests.test_bridge was attempted but all 57 tests failed during setup because the read-only environment exposed no writable temporary directory."],"flags":["no_edits","verification_incomplete"]}