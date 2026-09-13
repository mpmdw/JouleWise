```json
[
  {
    "title": "Snapshot-read DISCUSSION success is unreachable",
    "file": "scripts/bridge",
    "line_hint": "1198, 1696-1728, 2137",
    "severity": "blocker",
    "argument": "F4 requires DISCUSSION to complete on a snapshot_read lease, but session-open accepts only --access write. Even with a pre-existing or manually constructed snapshot receipt, scope-check calls governing_writer_lease, which rejects every non-write lease; this produces no_governing_lease and ATTRIBUTION_INDETERMINATE, so close retains rather than completes. An in-memory probe confirmed the parser choices are ['write'] and a selected snapshot_read lease returns no governing lease. The new tests cover only write-lease rejection, not the required success path.",
    "suggested_fix": "Allow snapshot_read in session-open and add an explicit scope-check mode that validates a selected receipt-bound snapshot lease without granting write authority. Add end-to-end clean-snapshot DISCUSSION success and persistent-delta rejection tests."
  },
  {
    "title": "Concurrent lease expansion can enlarge the lease after close audits its scope",
    "file": "scripts/bridge",
    "line_hint": "611-659, 1557-1609, 1701-1802",
    "severity": "blocker",
    "argument": "session-close holds session.lock, but lease-expand uses only bridge.lock. Close can read scope S, release bridge.lock, and run scope-check on S; lease-expand can then append S2 before the closing thread event or release. Close records digest S while lease-release reads and releases canonical scope S2. The added paths were never audited, violating F2 and whole-close serialization.",
    "suggested_fix": "Make lease expansion participate in session.lock with session.lock -> bridge.lock ordering, or atomically version/revalidate the lease scope before recording and releasing. Add a controlled real-process race test for expand during close."
  },
  {
    "title": "Waiting-state dedupe suppresses the expanded-scope digest",
    "file": "scripts/bridge",
    "line_hint": "1744-1766",
    "severity": "should-fix",
    "argument": "After a waiting_lead close records digest D1, the retained lease may be expanded to D2. Repeating the same status with the same verdict satisfies the no-op condition because it compares only state, status, verdict, and active disposition. It therefore leaves D1 as the latest thread digest even though close recomputed D2. The tests cover expansion before the first close and dedupe without an intervening expansion, so this combination is missed.",
    "suggested_fix": "Require latest_thread.write_scope_digest to equal current_scope_digest before deduping; otherwise append a new closing event carrying D2. Add an expand-between-waiting-closes regression test."
  },
  {
    "title": "Invocation-ID checking is not atomic with reservation",
    "file": "scripts/bridge",
    "line_hint": "1343-1403",
    "severity": "blocker",
    "argument": "invocation_usage_sources releases bridge.lock before session-open invokes lease-acquire. session.lock excludes another wrapper, but standalone baseline, lease-acquire, and thread-record commands do not acquire it. One can claim the ID in this gap; a disjoint direct lease-acquire can create a second lease under the same invocation ID and session-open can still succeed, corrupting the invocation-keyed joins. All new F3 tests are sequential and cannot detect this race.",
    "suggested_fix": "Introduce an atomic owner-tokenized invocation reservation, or refactor ID-producing primitives so public commands and wrappers share session.lock -> bridge.lock ordering without recursively reacquiring session.lock. Add a synchronized primitive-versus-session-open race test."
  },
  {
    "title": "Close errors can still report a stale or unknown lease disposition",
    "file": "scripts/bridge",
    "line_hint": "1664-1673, 1778-1787, 1816-1827",
    "severity": "should-fix",
    "argument": "A --lease-id mismatch or malformed --expect-digest raises before observed_lease_state is populated, returning unknown despite a valid receipt-bound lease. More seriously, standalone lease-abandon can run after close observes active but before lease-release; release then fails as already abandoned while the exception handler still maps the stale active observation to retained. This contradicts F7's actual-state error reporting.",
    "suggested_fix": "Observe the receipt-bound lease immediately after loading a valid receipt, and on later failures perform a best-effort locked state refresh before emitting the error. Add tests for early option-validation errors and abandon racing the release step."
  },
  {
    "title": "The new session-lock assertion does not exercise locking",
    "file": "tests/test_bridge.py",
    "line_hint": "628-630",
    "severity": "should-fix",
    "argument": "The only new session-lock assertion checks that session.lock exists after a sequential open. Deleting both flock operations while retaining lock_path.open would leave this assertion green, so the F1 serialization behavior is unguarded.",
    "suggested_fix": "Hold session.lock with a real parent-process flock, launch a wrapper subprocess, verify it remains blocked, then unlock and verify completion. Also assert concurrent closes cannot duplicate terminal or release events."
  }
]
```

BRIDGE_REPORT_V1
{"status":"DISCUSSION","summary":"Delta audit found three blocker and three should-fix defects in the fix-round paths; no files were changed.","pathspec":[],"verification":["Read git diff bad3465..22de70b for docs/contracts/bridge_protocol.md, scripts/bridge, and tests/test_bridge.py; traced all session_lock and bridge_lock acquisitions and wrapper primitive calls.","git diff --check bad3465..22de70b for the three scoped files completed with exit 0.","Read-only in-memory probe parsed scripts/bridge successfully, found session-open access choices ['write'], and confirmed governing_writer_lease returns None for a selected snapshot_read lease.","Focused unittest was attempted with PYTHONDONTWRITEBYTECODE=1 but could not enter setUp because the read-only sandbox provides no usable temporary directory; /tmp reproduction was therefore unavailable.","Final git status remained clean on impl/bridge-v1.1."],"flags":["no_edits","verification_incomplete"]}