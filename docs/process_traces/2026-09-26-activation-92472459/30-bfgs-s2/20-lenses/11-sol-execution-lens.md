```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Execution probes found two custody-routing blockers and three mutation-coverage findings; the worktree was not edited.",
  "workspace": {
    "base_requested": "1417c0c4",
    "base_mode": "descendant",
    "head_start": "4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd",
    "head_end": "4ea4b26b18f0e6bb6e3463c194ba6e8dc482c5fd",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "B1", "severity": "blocker", "summary": "A completed envelope stripped of end_stamp, post, and journal_rows becomes an excused collect_error."},
      {"id": "B2", "severity": "blocker", "summary": "pilot_summary can route a session changed after successful authentication without a custody raise."},
      {"id": "S1", "severity": "should_fix", "summary": "Three routing operands survive the current summary tests."},
      {"id": "S2", "severity": "should_fix", "summary": "Tests do not detect removal of required fsync or custody-output flush."},
      {"id": "N1", "severity": "nit", "summary": "Two recorder-path mutations survive; one is redundant under the enforced session shape."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_sample_quiet_predicate_evidence tests.test_quiet_predicate_campaign tests.test_night_kinds tests.test_evidence_night tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["", "----------------------------------------------------------------------", "Ran 468 tests in 462.118s", "", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "E1",
      "kind": "other",
      "cmd": "PYTHONPATH=\"$PWD\" python3 /tmp/bfgs_s2_execution.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["tamper delete_end_post_journal status SPREAD_RECORDED disposition excluded_collect_error summary True", "tamper edit_raw raises CustodyFailure custody failure: session-1/pre expected b42eb919dad653bc42dffac24df0512a4f9b315edbc928f79a1d31bd5b0766b4 observed d121be3103007b41edf96f8262925f8c7d61894afe9a041843b631f69445bc57 summary False", "race authentic_pass_then_session_changed status SPREAD_RECORDED envelope_error collector refused before capture: network_time_provenance, collector_exit 124 summary True"]},
      "expected": {"exit_code": 0, "tail_regex": "race authentic_pass_then_session_changed"}
    },
    {
      "id": "M1",
      "kind": "other",
      "cmd": "python3 /tmp/bfgs_s2_mutation_summary.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["route_1243_1 SURVIVED tests 16 tail OK", "atomic_fsync SURVIVED tests 1 tail OK", "distinct 34 killed 28"]},
      "expected": {"exit_code": 0, "tail_regex": "distinct 34 killed 28"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "lead_ruling", "level": "blocking", "text": "The requested rule that a stripped completed envelope never becomes an exclusion conflicts with amendment 35's current first-write definition and its stated indistinguishability rationale.", "needs": "Rule an independent stage witness or a narrower first-write condition before accepting this case."},
    {"id": "F2", "kind": "environment", "level": "nonblocking", "text": "V1's sole failure was the real-collector subprocess test; its captured stderr was empty. The prior seat report attributes this row to sandbox denial of /bin/ps, which this run did not independently prove.", "needs": "Rerun that test where /bin/ps is permitted."}
  ]
}
```

## Findings

**B1 — BLOCKER.** At [pilot_summary](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1250), the first-write test accepts a completed fixture after only `end_stamp`, `post`, and `journal_rows` are deleted. The post raw file remains. The real `pilot_summary` writes a normal night summary and excludes that envelope. This contradicts the requested tamper outcome, although it follows amendment 35’s current first-write definition.

Executed evidence, `PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_three_delete.py`:

```text
post_raw_exists True
verdict battery_float_evidence_missing status SPREAD_RECORDED
disposition excluded_collect_error
excluded ['collect_error', 'incomplete_interior_support']
```

**Closure:** Rule a way to distinguish a genuine first write from a stripped completed record. Checking finalized-only fields and an unbound post raw file closes this exact case; a guarantee against fully erased completed output needs an independent authenticated stage witness. Add the three-deletion case at `pilot_summary` and require a battery-blanked night, with no excused disposition.

**B2 — BLOCKER.** [pilot_summary](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1169) authenticates, then reads `session.json` again for routing. A deterministic swap immediately after the real authenticator returned `pass` changed a completed record into a refusal record. The changed, unauthenticated record was excluded and a summary was written.

Executed evidence, `PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_execution.py`, exact tail:

```text
race authentic_pass_then_session_changed status SPREAD_RECORDED envelope_error collector refused before capture: network_time_provenance, collector_exit 124 summary True
```

**Closure:** Route from a stable authenticated snapshot, or compare the session and journal bytes used by the summary with those authenticated. A change must raise `CustodyFailure` before routing and leave no new summary. Pin the swap immediately after authentication in a production-call-site test.

**S1 — SHOULD-FIX.** Collapsing each operand of the new `and` routes killed most mutants, but three survived the 16 `BatteryFloatSummaryTests`: the first and second no-record operands at [line 1164](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1164), and the completed/refusal discriminator at [line 1248](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1248). The mutation command was `PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_mutation.py`; `python3 /tmp/bfgs_s2_mutation_summary.py` reports:

```text
route_1164_0 SURVIVED tests 16 tail OK
route_1164_1 SURVIVED tests 16 tail OK
route_1248_1 SURVIVED tests 16 tail OK
```

**Closure:** Add nonzero-exit cases with (a) a session but no journal and (b) a journal but no session; both must raise custody. Add a completed, passing record carrying `error_class` with nonzero exit; it must remain on the completed-record and observer-floor route.

**S2 — SHOULD-FIX.** The production calls are present, but deleting `os.fsync` from [atomic_write_text](/Users/edr/code/JouleWise-wt-s2lens-92472459/scripts/sample_quiet_predicate_evidence.py:156) or `flush=True` from [execute](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1774) survives their focused tests. Executed mutation commands were `PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_mutation2.py` and `PYTHONPATH="$PWD" python3 /tmp/bfgs_s2_mutation_extra.py`; their exact result tails are:

```text
{"mutant": "atomic_fsync", "result": "SURVIVED", "tests_run": 1, "killers": [], "log_tail": ["Ran 1 test in 0.002s", "", "OK"]}
{"mutant": "x1_flush", "result": "SURVIVED", "killers": [], "tail": ["Ran 1 test in 0.053s", "", "OK"]}
```

**Closure:** Assert that both atomic target writes call `fsync` before replacement, and use a stdout spy that observes `flush()` on the custody line.

**N1 — NIT.** Collapsing the [replay guard](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1440) to `replay_recorders` survives without a mixed replay-and-battery case. Collapsing [line 1243](/Users/edr/code/JouleWise-wt-s2lens-92472459/joulewise/quiet_predicate_campaign.py:1243) to `power is not None` also survives; its removed `session is not None` operand is redundant after the required object check. `python3 /tmp/bfgs_s2_mutation_summary.py` reports:

```text
route_1440_0 SURVIVED tests 16 tail OK
route_1243_1 SURVIVED tests 16 tail OK
```

**Closure:** Pin the mixed replay-and-battery report shape; simplify the redundant session guard if that exact operand remains a mutation target.

Ruled-item results: **FT text 5 and AD2 amendment 20: no production findings** (both post paths, injected clock, digests, and a failing probe were exercised). **ERR amendment 32:** B2 and S1. **ERR amendment 33: no findings.** **ERR amendment 34:** S2 test coverage. **Q35 amendment 35:** B1, B2, and S1. **X-1:** no production finding; S2 covers its flush test. **FT text 15: no findings.**

The real-collector crash probes reached the ruled no-record, unfinished, and completed routes. The two historical pilot fixtures each re-summarized as `BATTERY_FLOAT_EVIDENCE_MISSING`, with 12 battery rows and all joules blank. Raw-file tampering raised `CustodyFailure` without writing a summary. Frozen paths were byte-identical to base, the registration digest remained `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`, and the detached worktree remained clean.

## Residual risk

V1 ran 468 tests in 462.118 seconds and failed only `test_real_collect_no_power_reaps_all_recorded_workers` at its subprocess return-code assertion (`1 != 0`, empty stderr). Its sandbox cause remains unverified in this run; the prior seat report identified `/bin/ps` access.