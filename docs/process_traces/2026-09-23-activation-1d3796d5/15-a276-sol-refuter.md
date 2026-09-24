```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The v3 notice matches the pinned rules, but two summary labels violate the brief or overstate their data; semantic text mutants also survive the focused tests.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "exact",
    "head_start": "c9e2bd14374fee3d62004dcf0d69eacc34043338",
    "head_end": "c9e2bd14374fee3d62004dcf0d69eacc34043338",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "blocker": 0,
      "should_fix": 3,
      "nit": 0,
      "mutants_killed": 20,
      "mutants_survived": 13
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "summary": "A v2 summary changes its SD label, contrary to the seat brief's unchanged v2 summary requirement."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "summary": "The new SD label says every captured envelope is included, but captured envelopes without readable energy are omitted."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "summary": "Focused tests pass with false threshold and observer wording in the generated texts."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 285 tests in 892.032s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 285 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/joulewise-a276-refuter.LNxqyu/run_mutants.py > /tmp/joulewise-a276-refuter.LNxqyu/mutant_results.jsonl",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

**F1 — should_fix.** I executed `pilot_summary` with the v2 registration on base and HEAD, using the same empty envelope fixture. Base writes `single-envelope SD None J`; HEAD writes `unfiltered single-envelope SD (every captured envelope, excluded ones included) None J`. The v2 busy-core sentence is unchanged, but the summary text as a whole is not. The seat brief explicitly requires unchanged v2 summary text. The lead should either restore that contract or rule that the SD correction also applies to v2.

**F2 — should_fix.** I executed a v3 summary with three captured session and round records whose energies were `[10, None, 14]`. `summary.json` reports an unfiltered SD of `2.8284271247461903`, calculated from the two readable values, while `summary.md` calls it “every captured envelope, excluded ones included.” The middle captured envelope is omitted. “Every captured envelope with readable energy” would describe the computation.

**F3 — should_fix.** In the temporary copy, changing `at or above 0.5 busy cores` to `above 0.5 busy cores` left `NoticeProtocolTextTests` green. Changing the summary’s “process outside the measurement apparatus” to “process inside the measurement apparatus” also left its named text test green. These are false readings of the enforced rules at the threshold and observer boundary. Assert the complete rule clauses, including direction and observer identity, and exercise a relative registration path.

### Mutation results

Mutations were applied one at a time to the `/tmp` copy and restored after each focused named test run. **N3** means `tests.test_evidence_night.NoticeProtocolTextTests.test_v3_notice_states_bound_schedule_and_all_refusal_rules`; **S** means `tests.test_quiet_predicate_campaign.CampaignTests.test_summary_text_follows_registration_exclusion_rule`.

| Mutant | Result |
|---|---|
| Disable sealed registration hash check | SURVIVED |
| Disable current digest check | SURVIVED |
| Disable armability check | SURVIVED |
| Accept any registration SHA in binding check | SURVIVED |
| Resolve relative registration against custody root | SURVIVED |
| Drop rule assignment | Killed by N3 |
| Swap pitch and envelope operands in span | Killed by N3 |
| Drop settle operand from span | Killed by N3 |
| Collapse span to settle | Killed by N3 |
| Collapse span to pitch | Killed by N3 |
| Collapse span to envelope | Killed by N3 |
| Make span/window comparison never true | SURVIVED |
| Make span/window comparison always true | Killed by N3 |
| Drop “sizes a later experiment” sentence | SURVIVED |
| Restore “first evidence night” claim | Killed by N3 |
| Drop cadence sentence | SURVIVED |
| Hard-code settling value in sentence | SURVIVED |
| Drop window-fit sentence | Killed by N3 |
| Change arm threshold from “at or above” to “above” | SURVIVED |
| Change arm threshold value | Killed by N3 |
| Drop arm-check location | Killed by N3 |
| Change envelope offender from outside to inside apparatus | SURVIVED |
| Change envelope core-second value | Killed by N3 |
| Drop consecutive-abort sentence | Killed by N3 |
| Hard-code consecutive-abort value | SURVIVED |
| Drop corecaptured sentence | Killed by N3 |
| Change corecaptured threshold | Killed by N3 |
| Restore “exactly one git show” claim | Killed by N3 |
| Flip summary `if rule` branch | Killed by S |
| Restore old v3 covariate-only sentence | Killed by S |
| Restore old SD label | Killed by S |
| Change summary offender from outside to inside apparatus | SURVIVED |
| Change summary core-second value | Killed by S |

### Full rendered v3 notice

This is a direct `render_notice` execution with a v3-bound state built in the style of `tests/test_evidence_night.py`. Fixture paths and identifiers are illustrative; no notice was sent.

```text
DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.
To: claude2.glaring610@passmail.net
Subject: NIGHT NOTICE — qpe01-pilot-n2-v3-fixture (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 2

Ed,
Launch needs no action from you unless you reply NO. Your NO overrides.
Arm attempt 2; prior candidates for this date: qpe01-pilot-n1-20260923-0700.
This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.
After 600 seconds settling, 12 600-second idle envelopes start 620 seconds apart and use 480-second interiors after 60-second offsets.
Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a busy-cores journal.
The 8,020-second program fits inside the 9,000-second window; no top-up or automatic repeat.
A process outside the measurement apparatus at or above 0.5 busy cores refuses the night at the arm check or at t0.
A process outside the measurement apparatus using 30 or more core-seconds inside an envelope excludes that envelope. 2 such exclusions in a row end the night.
the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes
Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.
The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.
After delivery the lead sizes block two or records 'no cutoff qualifies'.
plan_id: qpe01-pilot-n2-v3-fixture
repo_head = measurement_head = H: c9e2bd14374fee3d62004dcf0d69eacc34043338
clone: /fixture/clone
custody: /fixture/custody
runs: /fixture/custody/runs
staged plan: /tmp/tmpgchmgibg/plan.json
authored_epoch_s: 1
/Users/edr/code/wt-1d3796d5-ref-a276/configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json sha256 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
/fixture/chain sha256 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
No-objection opens only on mail service acceptance of the exact notice. Publication follows acceptance with no additional minimum waiting interval.
Every observed NO stops publication, including older threads. Reply NO on the thread or through an owner-authored directive; no reply is required.
The magistrate checks readable NO/directive/stop channels before publication and exits before REQUEST.
Keep agent applications closed and the machine untouched from REQUEST through completion, longer if the night remains active.
```

The cadence, 100 ms sampling, 9,000-second window, no top-up, and diagnostic purpose match `pilot_protocol_v3.json`; `window_budget_ok` uses the same span formula. `night_gate.non_observer_offender` enforces the inclusive 0.5-core arm/t0 bar. `non_observer_busy` enforces the inclusive 30 core-second envelope bar, and the executor aborts at two consecutive exclusions. The corecaptured t0 check uses more than two spawns in a 600-second window. The remaining address, veto, state metadata, supervision, and provisional-status sentences retain the existing notice policy. Removing the old single-`git show` claim is justified: `manifest_for` calls `tracked_bytes` for eight manifest paths.

The only production callers of `render_notice` are `prepare` and `notice` in `joulewise/evidence_night.py`. At this HEAD, `prepare` pins the v3 `PROTOCOL_PATH`; its bytes hash to the current `night_gate` digest, are armable, contain the rule, and yield `8020 <= 9000`. I also executed a relative-path binding successfully. A mismatched sealed SHA and a superseded v2 registration each raised the intended `Refused`. Thus the new refusal checks do not fire for the v3 plan this HEAD writes and seals.

## Residual risk

The 33 mutants used the focused named text cases; the complete 285-test command was run once on unmodified HEAD.