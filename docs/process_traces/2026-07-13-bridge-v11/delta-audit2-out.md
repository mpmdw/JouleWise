```json
[
  {
    "title": "The serialization decorator turns structured command failures into tracebacks",
    "file": "scripts/bridge",
    "line_hint": "181-185",
    "severity": "should-fix",
    "argument": "serialized_state_mutation resolves repository_root and enters state_mutation_lock outside the decorated command's existing exception boundary. For baseline, thread-record, lease-release, and lease-abandon, invocation outside a repository previously returned command-schema JSON with EXIT_ERROR=5; this round now emits a traceback and exits 1. Failure to create or open session.lock similarly escapes every decorated handler. This breaks JSON-consuming standalone tooling on newly introduced lock/repository failure paths. Reproduced against current and 22de70b behavior.",
    "suggested_fix": "Put repository resolution and session-lock acquisition inside a structured error boundary. Either move the lock into each command's existing try block or make the decorator accept a command-specific error emitter/schema and return EXIT_ERROR for BridgeError/OSError."
  },
  {
    "title": "The new lock-blocking tests can pass without session.lock serialization",
    "file": "tests/test_bridge.py",
    "line_hint": "436-443 and 663-665",
    "severity": "should-fix",
    "argument": "Both tests infer lock blocking solely from a 0.2-second process-launch timeout. The child performs interpreter startup and repository_root's git rev-parse before attempting session.lock. If that pre-lock work exceeds 200 ms, deleting the session-lock acquisition still produces TimeoutExpired with no appended event; the child then completes successfully after the test releases the unrelated held lock, satisfying every remaining assertion. Thus the D6 regression guard is timing-dependent and can false-green on a slow host.",
    "suggested_fix": "Add a deterministic child-to-parent handshake immediately before the real flock attempt, then start the blocked-state assertion only after that handshake. A multiprocessing child can import the module, wrap session_lock to signal before delegating to the real context manager, and invoke the public handler."
  }
]
```
BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Delta audit found two should-fix regressions: standalone mutator failures can escape as tracebacks, and the new lock-blocking tests are timing-dependent and can false-green. No edits made.","pathspec":[],"verification":["Read git diff 22de70b..63dd5f1 for docs/contracts/bridge_protocol.md, scripts/bridge, and tests/test_bridge.py; traced all state_mutation_lock and run_bridge_primitive call sites.","Reproduced current baseline/thread-record/lease-release outside a repository: traceback with exit 1; ran 22de70b versions via stdin and observed structured JSON with exit 5.","git diff --check 22de70b..63dd5f1 -- docs/contracts/bridge_protocol.md scripts/bridge tests/test_bridge.py: OK.","AST parsed scripts/bridge and tests/test_bridge.py: OK.","python3 -m unittest tests.test_bridge: attempted, but all 55 tests failed in setUp because the read-only sandbox provides no usable temporary directory; runtime lock/close tests were therefore not executable here.","Traced legacy events missing write_scope_digest: get() avoids KeyError; a waiting close appends one digest-bearing event and subsequent matching closes dedupe normally."],"flags":["no_edits","verification_incomplete"]}