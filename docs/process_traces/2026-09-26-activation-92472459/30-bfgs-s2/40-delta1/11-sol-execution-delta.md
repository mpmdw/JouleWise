```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F7 introduces an honest-write custody regression; F4 leaves an authentication binding gap and an unpinned journal guard.",
  "workspace": {
    "base_requested": "4ea4b26b",
    "base_mode": "exact",
    "head_start": "6c73caf42b4df2bf882c0fef84d56d27ffd325b3",
    "head_end": "6c73caf42b4df2bf882c0fef84d56d27ffd325b3",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "B1", "severity": "blocker", "summary": "F7 turns an honest refusal-session write failure from the no-record carve-out into whole-night custody failure."},
      {"id": "B2", "severity": "blocker", "summary": "F4's equal before/after snapshots do not prove that the authenticator checked those bytes; both summary call sites can publish a passing summary from non-passing session bytes."},
      {"id": "S1", "severity": "should_fix", "summary": "Removing both F4 journal-change guards leaves the relevant 36 tests green."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_quiet_predicate_campaign.BatteryFloatSummaryTests tests.test_quiet_predicate_campaign.BatteryFloatExecuteTests tests.test_quiet_predicate_campaign.BenchReplayFailClosedTests.test_L2_replay_collectors_crash_before_any_record_still_refuses tests.test_quiet_predicate_campaign.BenchReplayFailClosedTests.test_replay_with_battery_nonpass_refuses_at_harvest tests.test_sample_quiet_predicate_evidence.BatteryCollectorTests 2>&1 | tail -5",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["..............", "----------------------------------------------------------------------", "Ran 40 tests in 4.057s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 40 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "set -o pipefail; python3 -m unittest tests.test_quiet_predicate_campaign.BenchReplayFailClosedTests.test_R5_counterfactual_the_same_night_under_powermetrics_completes tests.test_quiet_predicate_campaign.TimedLogScannerTests.test_every_attestation_record_names_what_was_queried_even_when_nothing_was 2>&1 | tail -5",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["..", "----------------------------------------------------------------------", "Ran 2 tests in 0.110s", "", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests in .*\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "PYTHONPATH=\"$PWD\" python3 /tmp/bfgs_s2_f7_window.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["collect OSError injected refusal session write failure", "records session False journal b''", "pilot CustodyUnreadable session.json unreadable: missing summary False"]},
      "expected": {"exit_code": 0, "tail_regex": "pilot CustodyUnreadable .* summary False"}
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "PYTHONPATH=\"$PWD\" python3 /tmp/bfgs_s2_aba_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["pilot_direct_status battery_float_evidence_missing", "pilot_report SPREAD_RECORDED battery_rows 0 retained 12 summary True", "summarize_direct_status battery_float_evidence_missing", "summarize_report complete summary True source_status battery_float_evidence_missing"]},
      "expected": {"exit_code": 0, "tail_regex": "summarize_report complete summary True"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "set -o pipefail; python3 -m unittest tests.test_quiet_predicate_campaign.BatteryFloatSummaryTests tests.test_sample_quiet_predicate_evidence.BatteryCollectorTests 2>&1 | tail -5",
      "cwd": "/tmp/bfgs-s2-delta-d0rowj2b/mut_journal_compare",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["....................................", "----------------------------------------------------------------------", "Ran 36 tests in 3.777s", "", "OK"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "F7 follows the dictated write order, but a journal-only interruption is custody under the existing carve-out. Its stated honest-kill-window objective and that closure cannot both hold.",
      "needs": "Rule an atomic publication mechanism or revise F7's closure."
    },
    {
      "id": "V6",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full V1/V2 suites and live hardware were not rerun for this read-only delta lens; the focused call-site suite, constructed nights, and mutants were run.",
      "needs": ""
    }
  ]
}
```

## Findings

**B1 — BLOCKER; new in fix round 1.** The refusal path in [collect](/Users/edr/code/JouleWise-wt-s2lens-92472459/scripts/sample_quiet_predicate_evidence.py:1109) now publishes `rounds.jsonl` before `session.json`. If the session write fails, the surviving journal prevents [pilot_summary’s no-record carve-out](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1199). The real `collect` → `pilot_summary` probe, with a failed session write, produced:

```text
$ PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_f7_window.py
collect OSError injected refusal session write failure
records session False journal b''
pilot CustodyUnreadable session.json unreadable: missing summary False
```

The same probe against `4ea4b26b` produced `records session False journal None` and `pilot SPREAD_RECORDED`. Feeding the journal-only shape through `execute` raised `CustodyUnreadable` before an rc was returned. A successfully written refusal record **does** authenticate as `pass`; the regression is the interrupted write. The new [F7 test](/Users/edr/code/JouleWise-wt-s2lens-92472459/tests/test_sample_quiet_predicate_evidence.py:390) pins the journal-only state without running it through the reader.

**Closure:** Resolve the conflict between F7’s dictated order and the journal-only custody rule. Publish the two refusal records under a ruled atomic mechanism, or revise the F7 closure; add the failed `collect` write → `pilot_summary` → `execute` regression.

**B2 — BLOCKER; inherited B2 class remains open.** Both [pilot_summary](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1205) and [summarize](/Users/edr/code/JouleWise-wt-s2lens-92472459/scripts/sample_quiet_predicate_evidence.py:1507) implement F4’s specified `b0`/`b1` comparison. Equality does not bind `b0` to the bytes the authenticator read. In a deterministic transition to passing bytes during authentication and back to the original non-passing bytes before return, both call sites wrote passing summaries:

```text
$ PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_aba_probe.py
pilot_direct_status battery_float_evidence_missing
pilot_report SPREAD_RECORDED battery_rows 0 retained 12 summary True
summarize_direct_status battery_float_evidence_missing
summarize_report complete summary True source_status battery_float_evidence_missing
```

The same probe also succeeds at `4ea4b26b`: F4 closes its named one-way swap counterfactual, but not the underlying authentication-to-routing binding. **Closure:** make the authenticator return or consume the exact immutable session and journal bytes used for summary decisions, and pin this transition through both call sites. This needs a ruling because `battery_float.py` is frozen by the S2 constraints.

**S1 — SHOULD-FIX.** The journal-change comparisons at [pilot_summary](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1216) and [summarize](/Users/edr/code/JouleWise-wt-s2lens-92472459/scripts/sample_quiet_predicate_evidence.py:1520) are not pinned. A `/tmp` mutant disabling both passed all 36 relevant tests:

```text
$ set -o pipefail; python3 -m unittest tests.test_quiet_predicate_campaign.BatteryFloatSummaryTests tests.test_sample_quiet_predicate_evidence.BatteryCollectorTests 2>&1 | tail -5
....................................
----------------------------------------------------------------------
Ran 36 tests in 3.777s

OK
```

A post-authentication journal append raises `CustodyUnreadable` at both current call sites, while that mutant writes both summaries. **Closure:** add a journal-swap row for each call site, asserting custody and no new summary, then require this mutant to fail.

### F1–F8 disposition

| Item | Delta re-audit |
|---|---|
| F1 | Closed as dictated. The mixed replay/battery `execute` row passes; reverting only the new execute guard makes it fail with `'complete' != 'refused'`. A normal powermetrics night completes. |
| F2 | Closed as dictated. Seven authenticated envelope classes retained their baseline booking fields. A busy-process probe gave the authenticated and carve-out rows the same busy-core sample, observer CPU, and named 60 core-second offender; the carve-out also kept `cleanup_unproven`. An unmarked recorder row now raises on the carve-out. |
| F3 | Closed as dictated. Mutants ignoring the journal, ignoring `raw/round-*`, replacing `lstat` with `exists`, and dropping the completed/refusal discriminator each failed their respective production-call-site row. |
| F4 | Literal byte-comparison and session-swap rows pass; **B2 and S1** remain. Normal `record_attestation` followed by non-replay `execute` passed. |
| F5 | Closed. Removing `fsync` or custody-line `flush=True` killed the respective test. |
| F6 | Closed for its listed notes and coverage rows. The behavior pins that were already correct at the base remain baseline-green. |
| F7 | Dictated order and its test pass, and a complete refusal authenticates; **B1** shows the intended interruption closure fails. |
| F8 | Closed. The missing historical journal still raises custody with the corrected wording; its row is baseline-red and current-green. |

**Same-signature statement:** custody converted to exclusion — **no** (B1 is the reverse boundary error); unpinned routing or authentication operand — **yes** (B2 and S1); replay record dropped under a battery status — **no**.

The worktree remains clean at `6c73caf4`. Frozen paths are byte-identical to `1417c0c4`, and the registration digest remains `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`.

## Residual risk

The ABA probe supplies a controlled second writer; it establishes the byte-binding gap, not its frequency during a live night. The full V1/V2 suites were not rerun in this read-only lens.