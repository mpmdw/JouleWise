```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Amend text 6: authenticate a failed provisional collector, then exclude that envelope without blanking other authenticated envelopes.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "a30385e8a2de978f274024efcbf3368217ad92e9",
    "head_end": "a30385e8a2de978f274024efcbf3368217ad92e9",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F-1",
        "severity": "blocker",
        "text": "Text 6 would blank a night for one failed provisional collector although excluding its envelope cannot make the remaining authenticated numbers wrong."
      },
      {
        "id": "F-2",
        "severity": "should_fix",
        "text": "The merged authenticator does not emit amendment 30's specified quiet span unavailable reason for a shape-(iii) session with a recorded pre read and no post."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -B /tmp/qpe_shape3_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["case finalio exit 2 stderr ", "case finalzero exit 0 stderr "]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "case finalio exit 2"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "a30385e8a2de978f274024efcbf3368217ad92e9"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "a30385e8a2de978f274024efcbf3368217ad92e9"
      }
    }
  ],
  "flags": [
    {
      "id": "G-1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "S2 is unwritten, so amendment 35's future pilot_summary and summarize behavior was not executed.",
      "needs": "Implement and run the T6 rows in S2."
    }
  ]
}
```

**Contamination disclosure:** I saw the repository instructions supplied in the prompt. I did not open the prohibited files or use another judge’s answer. All probe writes were under `/tmp`; the repository is clean.

## Findings

**F-1 — Questions 1–3.** **AMEND.** The executor books timeout as exit 124 and calls group cleanup ([quiet_predicate_campaign.py:1566](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/joulewise/quiet_predicate_campaign.py:1566)). Today `pilot_summary` adds `collect_error` for every nonzero exit ([quiet_predicate_campaign.py:1150](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/joulewise/quiet_predicate_campaign.py:1150)). The collector writes `session.json` before rounds and writes `end_stamp` only on finalization ([sample_quiet_predicate_evidence.py:1084](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1084), [sample_quiet_predicate_evidence.py:1163](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1163), [sample_quiet_predicate_evidence.py:1208](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1208)). Those parts of F1–F3 hold. A kill during the current non-atomic final write could instead leave unreadable JSON; amendment 34’s atomic write is needed to make the provisional shape reliable.

I drove real `collect` in subprocesses, adding the planned pre record at its first write because S2 has not added that code. Exit 17 left `session.json`, no `end_stamp`, no refusal class, and no journal. Authentication returned `battery_float_evidence_missing`, reason `post evidence missing: phase not recorded`; a charging pre returned `battery_float_confounded`, reasons `pre IsCharging is not No` and the missing post. Changing the recorded pre raw raised `CustodyFailure`. Current `pilot_summary` returned `INCONCLUSIVE`, exclusions `collect_error` and `incomplete_interior_support`, `joules: null`, and no `battery_float_envelopes`; current `summarize` returned `no_rounds`. These are current outputs, not an S2 test.

Exclude a nonzero-exit shape (iii) after authentication, even when its pre read is confounded. Its energy is never admitted; each other envelope has its own pair. Thus this choice cannot make a pooled published number wrong. Preserve that verdict in `battery_float_envelopes`. **Every** amendment-29/30 raise and raw-digest `CustodyFailure` must propagate before exclusion ([battery_float.py:955](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/joulewise/battery_float.py:955), [battery_float.py:912](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/joulewise/battery_float.py:912)).

**F-2 — F4.** F4’s proposed *status* follows text 6, but its exact reason is refuted by execution. The helper adds span unavailability only when it has two parsed stamps ([battery_float.py:934](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/joulewise/battery_float.py:934)); a missing post supplies one. Correct this amendment-30 reason mismatch. Text 6’s night blanking remains **NOT EXECUTED** because S2 has not implemented it ([addendum ruling:109](/Users/edr/code/JouleWise-wt-bk-e6f06c96/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:109)).

**Questions 4–5.** Normal `collect` cannot honestly return exit 0 with shape (iii): its successful return follows the final write ([sample_quiet_predicate_evidence.py:1208](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1208), [sample_quiet_predicate_evidence.py:1683](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1683)). An injected `os._exit(0)` proved the bytes are possible through abnormal termination; treat them as non-pass and blank/refuse. `summarize` has no exit entry, so authenticate shape (iii) and raise on non-pass; today it merely enumerates journals and missed the journal-free probe ([sample_quiet_predicate_evidence.py:1462](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1462)).

Nonzero exits honestly cover pre-write validation/crash (**no output**), network-time refusal (**refusal**, exit 3), a handled round or finalization error whose final write succeeds (**completed**, usually exit 1), and timeout, signal, crash, or failed final write after the first write (**other**, shape iii). The injected final-write `OSError` produced exit 2 and shape (iii) despite `end_stamp` having been set in memory. A failure after a successful final write remains **completed**. The main return mapping is at [sample_quiet_predicate_evidence.py:1686](/Users/edr/code/JouleWise-wt-qpe3sol-e6f06c96/scripts/sample_quiet_predicate_evidence.py:1686).

I searched `evidence_envelopes.jsonl` and `evidence/summary.json` beneath both `~/night-custody` and `~/night-archive`: three distinct 12-envelope nights, all **36/36 exits zero**. Archive and results-clone copies duplicate those nights. A fourth night’s summaries had zero envelope rows. This establishes observed frequency only, not a timeout rate.

**Question 6 — T6 rows.** At `pilot_summary → authenticate_quiet_session`: nonzero shape (iii) with passing pre, then with charging pre, must retain other passing envelopes and list respectively missing/confounded verdicts (**RED** against naive text-6 blanking). The same call with altered pre raw must raise (**RED** against exclusion before authentication). Exit-zero shape (iii) must blank; completed non-pass must blank. At `summarize → authenticate_quiet_session`, a session-only shape (iii) must be found and raise (**RED** against today’s journal-only enumeration).

**Amendment 35 replacement text:** In `pilot_summary`, apply amendment 32’s no-output carve-out. For every other listed envelope, call `authenticate_quiet_session` before reading its journal, excluding it, or using any energy; propagate all custody raises. A nonzero-`collector_exit` shape (iii) is excluded as `collect_error` regardless of its authenticated status, including a confounded pre; record its index, status, reasons, and raw digests in `battery_float_envelopes`, and admit none of its energy to any night statistic. Do not blank other authenticated envelopes for that case. For all other non-pass envelopes, apply text 6’s whole-night status and blanking, confounded first. An exit-zero shape (iii) receives that non-pass treatment. `summarize` enumerates the amendment-32 union, authenticates every session before its journal, and raises on any non-pass; it has no collector-exit exception. Custody is never an exclusion. The frozen exclusion vocabulary and digest remain unchanged.

## Residual risk

S2’s implementation and tests remain to be run. No production night in the searched custody data exercised a nonzero collector exit.

Five-line summary for Ed:  
One stalled collector can currently cost an entire night under the proposed rule.  
Its own measurement can be excluded while other independently checked measurements remain valid.  
A charging reading in that failed measurement does not invalidate the others.  
Missing or changed recorded files still stop publication as custody failures.  
The three archived 12-envelope nights had no failed collector exits.