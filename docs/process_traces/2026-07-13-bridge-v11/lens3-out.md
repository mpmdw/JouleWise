```json
[
  {
    "title": "Write sessions can close as DISCUSSION without a rejecting test",
    "file": "tests/test_bridge.py",
    "line_hint": "527-566",
    "severity": "should-fix",
    "argument": "The ratified pin releases on DONE+SCOPE_OK; the contract permits DISCUSSION only for a read-only session that somehow holds a lease. session-open creates write sessions, yet scripts/bridge currently classifies DISCUSSION as a success status and releases their leases. Existing close tests exercise DONE and NEEDS_RULING only, so this semantic deviation passes unnoticed.",
    "suggested_fix": "Add a session-open followed by session-close --status DISCUSSION test that expects nonzero refusal, no complete thread event, and the write lease retained. Then restrict DISCUSSION completion to a demonstrably read-only receipt or remove it from write-session close statuses."
  },
  {
    "title": "Fail-closed session-open coverage stops at baseline failure",
    "file": "tests/test_bridge.py",
    "line_hint": "494-525",
    "severity": "should-fix",
    "argument": "The tests cover an existing receipt before acquisition and a baseline failure after acquisition, but not the two other pinned post-acquisition failures: thread-record and receipt creation. Deleting either cleanup path would leave an active lease while every current test remained green.",
    "suggested_fix": "Inject a thread-record failure, for example with an unusable mcp-thread-events.jsonl path, and a receipt-write failure, for example with receipts as a non-directory. For each, assert the reported stage, nonzero exit, an abandon event with the recorded reason, no active lease, and no receipt."
  },
  {
    "title": "Receipt tests never tamper the receipt and rely on self-referential expectations",
    "file": "tests/test_bridge.py",
    "line_hint": "460-492, 587-603",
    "severity": "should-fix",
    "argument": "The creation test derives header_fragment, scope digest, and persisted receipt expectations from the same returned object, while the later tampering test mutates only the baseline manifest. Consequently, receipt-field validation and the receipt's binding role as session-close's trust anchor can be weakened without these tests detecting it.",
    "suggested_fix": "Add table-driven receipt-tampering cases for invocation/lease identity, baseline pointer and digest, scope and scope digest, owner, and timestamps. Assert fail-closed close behavior, no release, and no terminal thread append. Also compare successful receipt fields to independently derived Git HEAD, baseline contents, requested scope, and lease events."
  },
  {
    "title": "Close-after-abandon recovery behavior is unguarded",
    "file": "tests/test_bridge.py",
    "line_hint": "527-603",
    "severity": "should-fix",
    "argument": "No test opens a session, explicitly abandons its lease, and then attempts session-close. This leaves the pinned no-auto-release boundary unprotected: a regression could scope-check an abandoned lease, append a contradictory completion, or convert abandonment into release.",
    "suggested_fix": "Open a session, abandon its lease, snapshot both event logs, then call session-close. Assert a nonzero error, the lease remains abandoned, no release event appears, and no new completion or waiting_lead thread event is appended."
  }
]
```

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Test-adequacy review found four should-fix gaps: an uncovered write-session DISCUSSION release defect, incomplete session-open failure injection, no direct receipt-tampering audit, and no close-after-abandon test.","pathspec":[],"verification":["Read git diff main...HEAD and all 12 touched files; inspected session wrapper and reverse-adapter implementation paths with numbered source output.","Confirmed HEAD bad3465ad4613ce120efd13d69eed5397b773985 matches BASE_HEAD; inspected the three branch commits and ran git diff --check main...HEAD successfully.","Ran python3 -m unittest tests.test_bridge tests.test_claude_bridge_mcp; execution was environment-blocked after discovery (57 tests, 60 setup/subtest errors) because the read-only sandbox exposed no writable temporary directory.","Rechecked git status --short --branch; no workspace changes were made."],"flags":[]}