```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FAIL: four acceptance-blocking implementation/test-hygiene defects, one blocking FIX-9 contract conflict, and one should-fix sweep defect were reproduced.",
  "workspace": {
    "base_requested": "3df8777",
    "base_mode": "exact",
    "head_start": "468e0a68ffb6af56d548f82bb012a5a6cff22160",
    "head_end": "468e0a68ffb6af56d548f82bb012a5a6cff22160",
    "upstream_end": "468e0a68ffb6af56d548f82bb012a5a6cff22160",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "FAIL",
    "classes": {
      "unexecuted-proof": "ALIVE — same-signature COUNT 2",
      "inspect-as-permission": "DEAD"
    },
    "findings": [
      {
        "id": "P1-1",
        "severity": "blocker",
        "title": "Hard-linked ledger aliases acquire simultaneous writer leases",
        "site": "joulewise/calibration_ledger.py:2571,2630",
        "scenario": "A ledger and os.link hard link shared st_dev/st_ino but selected different lock paths and both leases acquired concurrently."
      },
      {
        "id": "P1-2",
        "severity": "blocker",
        "title": "Unexecuted-proof recurs: same-signature COUNT 2",
        "site": "tests/test_calibration_exits.py:2423",
        "scenario": "A temporary-copy mutation made the corrected --allow-live writer always refuse; the QUIET_MAC_AUTH_REQUIRED terminal witness still passed."
      },
      {
        "id": "P1-3",
        "severity": "blocker",
        "title": "Finalization-conflict preservation witness fingerprints too late",
        "site": "tests/test_calibration_exits.py:1843,2127",
        "scenario": "A temporary-copy mutation corrupted manifest.json inside the initial refusal handler; the FINALIZATION_BINDING_CONFLICT witness still passed."
      },
      {
        "id": "P1-4",
        "severity": "blocker",
        "title": "Crash harness leaks sampler descendants after SIGKILL",
        "site": "tests/test_calibration_writer_crash_matrix.py:351; scripts/validate_powermetrics_fiducial.py:164,945",
        "scenario": "Crashing the real writer after sampler readiness left sampler PID 60012 alive; both focused and full-suite containment groups retained descendants after unittest exited."
      },
      {
        "id": "P1-5",
        "severity": "blocker",
        "title": "FIX-9 crash environment variable is live in production code, contrary to this re-audit's inertness requirement",
        "site": "scripts/validate_powermetrics_fiducial.py:163",
        "scenario": "Setting JOULEWISE_TEST_WRITER_CRASH_STAGE on the ordinary writer CLI caused real process SIGKILL (-9). The binding FIX-9 contract explicitly authorized env/config crash points at production write sites, so the two requirements conflict."
      },
      {
        "id": "P2-1",
        "severity": "should_fix",
        "title": "Standing positional-receipt lint misses actual positional receipt fixtures",
        "site": "tests/test_calibration_exits.py:593; tests/test_calibration_live_three_window.py:1020,1126",
        "scenario": "The lint passed while business_rows[1:] and marker_removed[1] continued to address receipt collections positionally."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_diagnostic_routes_never_emit_ready_to_arm_under_live_lease tests.test_calibration_ledger.CalibrationLedgerTests.test_enforcing_post_readiness_refuses_deleted_finalized_pre_custody tests.test_calibration_ledger.CalibrationLedgerTests.test_sessionless_pin_advancement_refuses_pending_business_head tests.test_calibration_ledger.CalibrationLedgerTests.test_symlink_alias_cannot_acquire_a_second_writer_lease tests.test_calibration_exits.RefusalInventoryTests.test_calibration_tests_have_no_literal_positional_receipt_indexing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.697s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits tests.test_calibration_writer_crash_matrix",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["Ran 16 tests in 162.913s", "OK", "POST_SUITE_PROCESS_GROUP_SURVIVORS=True"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK.*POST_SUITE_PROCESS_GROUP_SURVIVORS=False"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_ledger tests.test_powermetrics_fiducial tests.test_calibration_live_three_window tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 171 tests in 44.346s", "OK (skipped=3)", "POST_SUITE_PROCESS_GROUP_SURVIVORS=False"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["Ran 2770 tests in 843.148s", "OK (skipped=90)", "POST_SUITE_PROCESS_GROUP_SURVIVORS=True"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2770 tests .*\\n\\nOK \\(skipped=90\\).*POST_SUITE_PROCESS_GROUP_SURVIVORS=False"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "temporary-copy hard-link lease, unexecuted-proof mutation, preservation mutation, and crash-child probes under $TMPDIR",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": ["hardlink_second_acquired=true", "MUTATION_SURVIVED: QUIET_MAC_AUTH_REQUIRED", "MUTATION_SURVIVED: FINALIZATION_BINDING_CONFLICT", "sampler_alive_after_writer_sigkill=true"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "hardlink_second_acquired=false.*MUTATION_KILLED.*sampler_alive_after_writer_sigkill=false"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "FIX-9 authorizes env/config crash points at real production write sites, while this re-audit requires proof that production cannot trigger them.",
      "needs": "Magistrate must rule which requirement controls."
    },
    {
      "id": "R2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied host-wide ps/pgrep inspection; owned-process-group containment nevertheless reproduced and reaped the leaked descendants.",
      "needs": ""
    },
    {
      "id": "R3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The fix report claims 12 files and 1631 insertions; git diff 3df8777..468e0a6 contains 15 files and 1927 insertions because the three gauntlet records are included. git diff --check also reports trailing whitespace in Lens B.",
      "needs": "Reconcile the fix report's stated diff scope with the committed comparison."
    }
  ]
}
```

## Findings

Verdict: **FAIL**.

### P1-1 — Hard-linked ledgers bypass the identity-keyed lease

[`calibration_ledger.py:2571`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:2571>) and [`calibration_ledger.py:2630`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/joulewise/calibration_ledger.py:2630>) key locks and in-process leases by resolved pathname, not `(st_dev, st_ino)`.

In a temporary copy, I created `ledger.jsonl`, made `hardlink.jsonl` with `os.link`, verified that both names had the same device and inode, and acquired both leases simultaneously:

```text
same_inode=true
hardlink_second_acquired=true
lock_paths=["ledger.jsonl.lock","hardlink.jsonl.lock"]
```

Two genuinely different ledgers acquired concurrently, and a valid acquire-release-reacquire succeeded. Thus the problem is specifically same-inode aliases. FIX-2’s symlink regression passes, but it does not discriminate the incomplete realpath-only implementation.

### P1-2 — Unexecuted-proof is ALIVE, same-signature COUNT 2

At [`test_calibration_exits.py:2423`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:2423>), the three corrected writer cases do not execute the writer after correcting its arguments/authorization. They call ledger readiness directly and use its terminal projection.

In the temporary copy, I mutated the real writer’s `--allow-live` check so it always refused. The targeted `QUIET_MAC_AUTH_REQUIRED` witness still passed:

```text
MUTATION_SURVIVED ['calibration_quiet_mac_auth_required']
```

That is the admitted broken implementation: the mapped public writer remains unusable after correction while the witness claims success. By the standing rule, this is explicitly **same-signature COUNT 2**. No fix is proposed here.

### P1-3 — FIX-5 does not prove pre-refusal preservation for finalization conflict

[`test_calibration_exits.py:1843`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:1843>) deliberately excludes `FINALIZATION_BINDING_CONFLICT` from the pre-refusal fingerprint. Its fingerprint is instead taken at [`test_calibration_exits.py:2127`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:2127>), after the first writer refusal has already run.

I mutated that refusal handler to overwrite `manifest.json` with malformed bytes before emitting the refusal. The witness passed because it established its baseline only after the corruption and permitted the resumed command to report either finalization conflict or custody unreadable:

```text
MUTATION_SURVIVED ['calibration_finalization_binding_conflict']
```

FIX-5 therefore does not kill the named “refusal handler corrupts custody” implementation for every hard stop.

### P1-4 — Crash matrices leak real sampler children

The harness starts the writer with plain `subprocess.run` at [`test_calibration_writer_crash_matrix.py:351`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_writer_crash_matrix.py:351>). It uses no `start_new_session`, process-group kill, or `addCleanup`. The writer starts its sampler at [`validate_powermetrics_fiducial.py:945`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:945>) and then self-SIGKILLs at [`validate_powermetrics_fiducial.py:163`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:163>), leaving the sampler outside any cleanup path.

A controlled real-writer probe produced:

```text
writer_returncode=-9
sampler_pid=60012
sampler_alive_after_writer_sigkill=true
```

The focused 16-test witness/crash run and the full 2,770-test run were each placed in a fresh external process group. Both still had descendants after `unittest` exited:

```text
Ran 16 tests in 162.913s
OK
POST_SUITE_PROCESS_GROUP_SURVIVORS=True
```

```text
Ran 2770 tests in 843.148s
OK (skipped=90)
POST_SUITE_PROCESS_GROUP_SURVIVORS=True
```

The audit wrapper killed those groups afterward. The sandbox denied host-wide `ps`/`pgrep`, but the owned-process-group checks conclusively detected live descendants.

Timing distortion is concrete. Touched suites contain 1-second sampler-readiness/rollover deadlines, a 50ms rollover configuration, 5-second synchronization waits, and 10-second event/thread waits. Spinning descendants can consume CPU throughout later tests, inflate wall time, and cause deadline-sensitive failures. The reported fix-round run could therefore have been distorted by its own crash-matrix orphans.

### P1-5 — FIX-9 production inertness is false, but the requested standard conflicts with its contract

[`validate_powermetrics_fiducial.py:163`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/scripts/validate_powermetrics_fiducial.py:163>) reads the ambient `JOULEWISE_TEST_WRITER_CRASH_STAGE` variable without a test-mode guard. Running the ordinary writer command with that variable caused a genuine `SIGKILL` at a production write boundary.

Thus no proof of production inertness is possible for the landed implementation. However, FIX-9’s binding contract explicitly permits env/config-controlled crash points at real production sites. The re-audit expectation and binding contract conflict; the magistrate must rule rather than treating either interpretation as silently authoritative.

### P2-1 — FIX-12’s standing lint misses positional receipt fixtures

[`test_calibration_exits.py:593`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_exits.py:593>) checks a subscript only when the immediate variable name contains `receipt`.

The lint passes while receipt collections are indexed positionally at:

- [`test_calibration_live_three_window.py:1020`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_live_three_window.py:1020>): `business_rows[1:]`
- [`test_calibration_live_three_window.py:1126`](</private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/recovery/tests/test_calibration_live_three_window.py:1126>): `marker_removed = copy.deepcopy(self.receipts)` followed by `marker_removed[1]`

The repo-wide prohibited positional shape therefore remains detectable only by semantic context, not the landed lint.

## Per-fix closure

| Fix | Dictated closure | Regression discrimination |
|---|---|---|
| FIX-1 | Implemented | Yes. Diagnostic routes do not emit `ready_to_arm`; enforcing emitters require a lease. |
| FIX-2 | **Incomplete** | Symlink test kills the prior lexical implementation, but hard-link same-inode aliases still acquire concurrently (P1-1). |
| FIX-3 | Implemented | Yes for deleted finalized PRE custody. Enforcing readiness now verifies historical custody. |
| FIX-4 | Implemented | Yes. Pending business heads refuse; a legitimate recovery-control-tail sessionless advancement succeeded in the positive probe. |
| FIX-5 | **Incomplete** | No. The finalization-conflict corruption mutation survives (P1-3). |
| FIX-6 | **Incomplete** | No. The corrected-writer refusal mutation survives (P1-2). |
| FIX-7 | Implemented | Yes. The real writer commands now produce the mapped refusals and automatic abort/status consequences. |
| FIX-8 | Implemented | Yes. Abandon-then-repair and finalized terminal-pin paths are executed, though the shared crash harness leaks. |
| FIX-9 | Real boundaries implemented | The real SIGKILL boundaries discriminate the prior manual-hook matrix, but the harness leaks and production inertness is false (P1-4/P1-5). |
| FIX-10 | Implemented | Registry census and hostile claim/finalization scenarios pass; FIX-5’s independent preservation gap remains. |
| FIX-11 | Implemented | Yes. Contract projection and malformed-target quarantine witness pass. |
| FIX-12 | **Incomplete** | No. The standing lint passes over actual positional receipt collections (P2-1). |
| FIX-13 | Implemented | Yes. Half-written manifest custody is parsed/refused at the real boundary, subject to the shared orphan leak. |

FIX-3’s verification is linear in total historical custody bytes. A cached probe measured approximately 1.8ms for 4MiB, 6.2ms for 16MiB, and 25.4ms for 64MiB. I reproduced no binding-contract violation or legitimate morning-path refusal, but the integration fixture bypasses custody verification and no large real-ledger benchmark exists.

## Prohibited-shape sweep

- **unexecuted-proof: ALIVE — same-signature COUNT 2.** Reproduced at P1-2. Per standing rule, the class stops here without fix design.
- **inspect-as-permission: DEAD.** The tree-wide sweep found the sole production `ready_to_arm` projection in `CalibrationReadiness.as_dict`, gated by `enforcing_under_lease`. Writer and reservation consumers invoke it inside `CalibrationWriterLease`; recovery/audit routes request non-enforcing diagnostic readiness and do not feed an arming route.

## Full-suite comparison

The unpiped canonical run from a fresh containment process reported:

```text
----------------------------------------------------------------------
Ran 2770 tests in 843.148s

OK (skipped=90)
POST_SUITE_PROCESS_GROUP_SURVIVORS=True
```

The count and skips match the fix report’s `2770 OK (skipped=90)`. Wall time was 843.148 seconds versus 840.318 seconds, 2.830 seconds slower. Both runs remain timing-exposed because the suite itself creates spinning descendants.

The fix report’s stated diff also conflicts with the requested comparison: it reports 12 files and 1,631 insertions, while `git diff 3df8777..468e0a6` contains 15 files and 1,927 insertions. The three gauntlet records account for the additional paths. `git diff --check` exits 2 on trailing whitespace in Lens B.

## Residual risk

Host-wide before/after process census was unavailable because the sandbox rejects `ps` and `pgrep`; all descendants owned by the audit’s isolated process groups were nevertheless detected and reaped. FIX-3’s uncached large-ledger I/O cost and a real morning-path custody run remain unbenchmarked.

Checks performed: full unpiped 2,770-test suite; 5 targeted regressions; 3 registry/census tests; 16 witness/crash tests; 171 touched-suite tests; hard-link, legitimate-reacquire, terminal-pin, custody-performance, crash-child, and two mutation probes; tree-wide prohibited-shape searches; clean-tree, revision, diff-stat, and diff-integrity checks.