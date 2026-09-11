```json
[
  {
    "title": "Concurrent session-close calls can append contradictory terminal events",
    "file": "scripts/bridge",
    "line_hint": "1524-1601",
    "severity": "blocker",
    "argument": "Receipt loading, terminal-event inspection, scope-check, thread recording, and lease release occur as separate unlocked reads or separately locked subprocesses. Two closes can therefore both observe no terminal event, both pass scope-check, and append different complete events before racing to release. An in-memory reproduction against command_session_close appended both DONE and DISCUSSION; one returned success and the other failed during its second release attempt. An override or abandonment can similarly land between scope-check and release, invalidating the checked outcome. This violates idempotency and the prohibition on contradictory terminal events.",
    "suggested_fix": "Make close a single transaction under bridge.lock covering receipt/lease/thread validation, the lease-log snapshot used by scope-check, terminal thread append, and lease terminal event. Refactor the primitives into lock-aware in-process helpers so session-close does not recursively invoke subprocesses that reacquire the lock."
  },
  {
    "title": "session-close discards prospectively expanded lease scope",
    "file": "scripts/bridge",
    "line_hint": "1510-1515, 1562-1575",
    "severity": "blocker",
    "argument": "lease-expand updates the lease's canonical paths, but session-close always supplies receipt['write_scope'] and its original digest to scope-check and thread-record. Because the receipt is immutable, an authorized edit in a newly added path is consequently reported as SCOPE_VIOLATION. The reproduced scope-check invocation contained only tracked.txt after the mocked lease had expanded to tracked.txt plus other.txt. This makes the ratified prospective scope-expansion continuation path unable to complete through the preferred wrappers.",
    "suggested_fix": "Bind each approved expansion through an immutable append-only expansion receipt/event, then have session-close validate that chain and use the resulting canonical scope and digest for scope-check and the closing thread event."
  },
  {
    "title": "session-open does not refuse every previously used invocation id",
    "file": "scripts/bridge",
    "line_hint": "511-584, 1329-1335",
    "severity": "should-fix",
    "argument": "The wrapper checks only for an existing receipt. An invocation id present solely in the lease log or thread log remains reusable; for example, after abandoning a crash-left lease before baseline creation, session-open with the same id can acquire a new lease and succeed. Existing baselines happen to fail later, after a new lease is acquired. This deviates from the pinned requirement to refuse an existing invocation id and permits multiple lifecycle records to share one identity.",
    "suggested_fix": "Reserve and validate invocation-id uniqueness atomically under bridge.lock across receipts, baselines, lease events, and thread events before appending the acquisition. Treat any prior occurrence as requiring a fresh id."
  },
  {
    "title": "DISCUSSION closes and releases a write session",
    "file": "scripts/bridge",
    "line_hint": "24-25, 1581-1597, 1919-1943",
    "severity": "should-fix",
    "argument": "DISCUSSION is grouped with DONE without checking lease access or whether writes occurred. session-open only creates write leases, so DISCUSSION plus SCOPE_OK—including an in-scope persistent edit—records complete and releases that write lease. The branch contract permits DISCUSSION release only for a read-only session that somehow held a lease. The behavior was reproduced against command_session_close.",
    "suggested_fix": "Remove DISCUSSION from releasable wrapper statuses until read-only receipts are supported, or require a receipt-bound snapshot_read lease and prove there are no workspace deltas before allowing DISCUSSION to complete and release."
  },
  {
    "title": "Abandon-then-close falsely reports the lease as retained",
    "file": "scripts/bridge",
    "line_hint": "1535-1560, 1623-1631",
    "severity": "nit",
    "argument": "If a lead explicitly abandons a retained lease and session-close is subsequently retried, line 1558 raises because the state is abandoned, but the generic error response hardcodes lease_disposition to retained. That machine-readable result is the opposite of the recorded lease state and can misdirect recovery automation.",
    "suggested_fix": "Carry the observed lease state into the error response and report already_abandoned/abandoned accurately; optionally make this recovery case an explicit idempotent notice."
  }
]
```

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Execution-correctness review found five session-wrapper defects: two blockers, two should-fix findings, and one disposition-reporting nit; no adapter defect met the reporting threshold.","pathspec":[],"verification":["Read git diff main...HEAD and the touched bridge scripts, focused tests, and ratified v1.1 contract sections.","Traced session-open/session-close, lease expansion, receipt anchoring, outcome matrix, override health, scope-check lease selection, HEAD movement, and internal-path exemption code paths.","Ran Python AST parsing for scripts/bridge and node --check for scripts/claude-bridge-mcp.mjs: OK.","Ran 6 no-temp adapter guard/header/effort tests: OK.","Ran an in-memory harness against command_session_close: reproduced dropped expanded scope, DISCUSSION release of a write lease, and concurrent contradictory terminal statuses.","Attempted the two focused test modules; the read-only sandbox provided no writable temporary directory, so temp-backed cases could not execute.","Ran git diff --check main...HEAD: OK; confirmed HEAD bad3465ad4613ce120efd13d69eed5397b773985 and a clean branch worktree."],"flags":[]}