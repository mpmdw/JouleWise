```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Closed X1–X7 in the five authorized paths; all 13 previously surviving mutants were killed and the named acceptance passed.",
  "workspace": {
    "base_requested": "313efcca",
    "base_mode": "descendant",
    "head_start": "c9e2bd14374fee3d62004dcf0d69eacc34043338",
    "head_end": "c9e2bd14374fee3d62004dcf0d69eacc34043338",
    "upstream_end": null,
    "branch": "feat/2026-09-23-a276-notice-v3"
  },
  "pathspec": [
    "joulewise/evidence_night.py",
    "joulewise/quiet_predicate_campaign.py",
    "tests/test_evidence_night.py",
    "tests/test_quiet_predicate_campaign.py",
    "docs/contracts/evidence_night_entry.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night.NoticeProtocolTextTests tests.test_evidence_night.PrepareTests.test_sealed_registration_decisions_use_candidate_interpreter tests.test_quiet_predicate_campaign.CampaignTests.test_summary_text_follows_registration_exclusion_rule",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 5 tests in 14.517s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 5 tests in .*s\\s+OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a276_mutants.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["{\"name\": \"hardcode_abort\", \"verdict\": \"KILLED\", \"test\": \"tests.test_evidence_night.NoticeProtocolTextTests.test_notice_window_and_registered_counts_refuse_or_render\", \"tail\": [\"FAIL: test_notice_window_and_registered_counts_refuse_or_render (tests.test_evidence_night.NoticeProtocolTextTests.test_notice_window_and_registered_counts_refuse_or_render)\", \"Ran 1 test in 0.003s\", \"FAILED (failures=1)\"]}"]},
      "expected": {"exit_code": 0, "tail_regex": "\"hardcode_abort\".*\"KILLED\""}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 287 tests in 546.222s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 287 tests in .*s\\s+OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A future v4 registration that removes t0_non_observer_share_max still needs handling in the registration-v4 lane, as assigned by the magistrate.",
      "needs": "Registration-v4 lane"
    }
  ]
}
```

## Change

| Item | Closure |
|---|---|
| X1 | [evidence_night.py:241](/Users/edr/code/wt-1d3796d5-a276/joulewise/evidence_night.py:241) resolves the registration and checks its ruled, current, and armable status in H’s interpreter, with a distinct refusal for each check. The notice keeps its sealed-binding hash refusal at [line 289](/Users/edr/code/wt-1d3796d5-a276/joulewise/evidence_night.py:289). [The candidate test](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:658) proves a wrong caller import cannot veto H and exercises the three H-side refusals. |
| X2 | Both notice fixtures use `night_gate.QPE01_PILOT_REGISTRATION_PATH`: [text test](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:67), [lifecycle test](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:2247). |
| X3 | [Notice rendering](/Users/edr/code/wt-1d3796d5-a276/joulewise/evidence_night.py:297) now glosses the four terms, uses “t0, the scheduled start,” spells out “twelve,” completes the corecaptured sentence, and states the git activity conditionally. Complete-sentence and production-call assertions are at [test lines 66–82](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:66), [368](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:368), and [2263](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:2263). |
| X4 | [The SD label](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1438) says “every envelope with a readable energy value, excluded envelopes included,” matching the unfiltered computation. [The text test](/Users/edr/code/wt-1d3796d5-a276/tests/test_quiet_predicate_campaign.py:109) pins the label. |
| X5 | The corrected SD label also applies to v2. [The v2 test](/Users/edr/code/wt-1d3796d5-a276/tests/test_quiet_predicate_campaign.py:116) asserts its entire empty-fixture summary, preserving every other sentence. |
| X6 | Binding, H-side refusal, relative-path, window, count, and complete-sentence tests are at [notice tests](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:66), [candidate test](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:658), and [summary test](/Users/edr/code/wt-1d3796d5-a276/tests/test_quiet_predicate_campaign.py:98). All 13 prior survivors failed focused tests in `/tmp` copies. |
| X7 | [The contract’s pre-output refusal list](/Users/edr/code/wt-1d3796d5-a276/docs/contracts/evidence_night_entry.md:431) now includes sealed-binding mismatch and H-side registration refusals. |

### Rendered v3 notice

Fixture paths and identifiers are illustrative. No notice was sent.

```text
DRAFT — NOT SENT; prerequisites and veto observations are not yet recorded.
To: claude2.glaring610@passmail.net
Subject: NIGHT NOTICE — qpe01-pilot-n2-v3-fixture (EVIDENCE; DIAGNOSTIC_NO_PACK) — attempt 2

Ed,
Launch needs no action from you unless you reply NO. Your NO overrides.
Arm attempt 2; prior candidates for this date: qpe01-pilot-n1-20260923-0700.
This idle-variance evidence night sizes a later experiment; it activates no new quietness cutoff.
After 600 seconds settling, twelve 600-second idle envelopes start 620 seconds apart and use 480-second interiors after 60-second offsets.
Power sampling is every 100 ms, with census, AC-power, thermal, timing and cleanup observations and a journal of busy cores (the average number of CPU cores a process kept busy).
The 8,020-second program fits inside the 9,000-second window; no top-up or automatic repeat.
A process outside the measurement apparatus (the night's own measurement processes) at or above 0.5 busy cores refuses the night at the arm check (the checks run when the night is installed) or at t0, the scheduled start.
A process outside the measurement apparatus using 30 or more core-seconds (busy cores multiplied by seconds) inside an envelope excludes that envelope. Two such exclusions in a row end the night.
At t0, the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes.
During the night, read-only git show checks run in the measurement clone; successful results publication commits and pushes them from a separate results clone.
Partial observations and refusals are kept. No model, load generator, calibration-ledger session or measurement pack runs.
The scheduler supervises the program and the courier emails the result. Evidence remains PROVISIONAL.
After delivery the lead sizes block two or records 'no cutoff qualifies'.
plan_id: qpe01-pilot-n2-v3-fixture
repo_head = measurement_head = H: c9e2bd14374fee3d62004dcf0d69eacc34043338
clone: /fixture/clone
custody: /fixture/custody
runs: /fixture/custody/runs
staged plan: /tmp/a276-render-h9tl2n64/plan.json
authored_epoch_s: 1
/Users/edr/code/wt-1d3796d5-a276/configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json sha256 69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616
/fixture/chain sha256 bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
No-objection opens only on mail service acceptance of the exact notice. Publication follows acceptance with no additional minimum waiting interval.
Every observed NO stops publication, including older threads. Reply NO on the thread or through an owner-authored directive; no reply is required.
The magistrate checks readable NO/directive/stop channels before publication and exits before REQUEST.
Keep agent applications closed and the machine untouched from REQUEST through completion, longer if the night remains active.
```

The new numeric and operational claims were checked against these enforcing lines:

- [Registration lines 17–18, 32–33, 53, 59, 76, 96–98](/Users/edr/code/wt-1d3796d5-a276/configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:17) specify `600`-second envelopes, `12` envelopes, `60`/`480`-second interiors, `100` ms power sampling, `600` seconds settling, `620`-second pitch, the `0.5` share, `top_up: false`, and the `9000`-second window. [The schedule check](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1480) computes `settle_s + (envelopes - 1) * slot_pitch_s + envelope_s`, yielding 8,020 seconds.
- [The arm/t0 predicate](/Users/edr/code/wt-1d3796d5-a276/joulewise/night_gate.py:850) uses `busy_cores >= T0_NON_OBSERVER_SHARE_MAX`; [the dynamic arm check](/Users/edr/code/wt-1d3796d5-a276/joulewise/night_gate.py:1727) and [night evaluation](/Users/edr/code/wt-1d3796d5-a276/joulewise/night_gate.py:1772) call the machine check. [The envelope predicate](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1019) sums `busy_cores * interval_s` and at [line 1024](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1024) uses `total >= rule["bar_core_seconds"]`. [The registration](/Users/edr/code/wt-1d3796d5-a276/configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:37) sets that bar to `30` and consecutive abort to `2`; [the executor](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1643) enforces the latter.
- [The shared corecaptured constants](/Users/edr/code/wt-1d3796d5-a276/joulewise/corecaptured_loop.py:12) are `WINDOW_S = 600` and `SPAWNS_MAX = 2`; [the t0 check](/Users/edr/code/wt-1d3796d5-a276/joulewise/night_gate.py:1526) refuses when `spawns.count > SPAWNS_MAX`.
- [The measurement read](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:96) runs `git -C root show` for tracked bytes; [the manifest](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:83) names eight paths, and [the recorder launch](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1528) runs its own environment verification. [The results publisher](/Users/edr/code/wt-1d3796d5-a276/scripts/run_night.py:1056) is best effort: it creates `results-clone` at [line 1073](/Users/edr/code/wt-1d3796d5-a276/scripts/run_night.py:1073), then commits and pushes from that clone at [lines 1111 and 1118](/Users/edr/code/wt-1d3796d5-a276/scripts/run_night.py:1111). The notice says **successful** publication because this step can fail.

### Mutant table

`N` = complete notice test; `B` = binding/relative-path test; `W` = window/count test; `H` = candidate-interpreter test; `S` = summary text test. **†** marks the 20 mutants killed in Sol’s supplied refuter run; the 13 unmarked former survivors were rerun in `/tmp` and killed here.

| Mutant | Result | Test |
|---|---|---|
| Disable sealed-binding hash | Killed | B |
| Disable current digest | Killed | H |
| Disable armability | Killed | H |
| Accept any registration SHA | Killed | H |
| Resolve relative registration against wrong root | Killed | B |
| Drop rule assignment | Killed† | N |
| Swap pitch and envelope operands | Killed† | N |
| Drop settle operand | Killed† | N |
| Collapse span to settle | Killed† | N |
| Collapse span to pitch | Killed† | N |
| Collapse span to envelope | Killed† | N |
| Make span/window comparison never true | Killed | W |
| Make span/window comparison always true | Killed† | N |
| Drop “sizes a later experiment” sentence | Killed | N |
| Restore “first evidence night” claim | Killed† | N |
| Drop cadence sentence | Killed | N |
| Hard-code settling value | Killed | W |
| Drop window-fit sentence | Killed† | N |
| Change “at or above” to “above” | Killed | N |
| Change arm threshold value | Killed† | N |
| Drop arm-check location | Killed† | N |
| Change notice offender from outside to inside | Killed | N |
| Change envelope core-second value | Killed† | N |
| Drop consecutive-abort sentence | Killed† | N |
| Hard-code consecutive-abort value | Killed | W |
| Drop corecaptured sentence | Killed† | N |
| Change corecaptured threshold | Killed† | N |
| Restore “exactly one git show” claim | Killed† | N |
| Flip summary `if rule` branch | Killed† | S |
| Restore old v3 covariate-only sentence | Killed† | S |
| Restore old SD label | Killed† | S |
| Change summary offender from outside to inside | Killed | S |
| Change summary core-second value | Killed† | S |

## Verification notes

The first acceptance invocation was interrupted after a final scan found the second hard-coded v3 fixture path. It reported no failure before interruption. The path was corrected, and the **final** named acceptance passed: `Ran 287 tests in 546.222s`, `OK`. No other test module imports a changed function; `tests/test_run_night.py` imports `CHAIN_PATH` only. No quiet-machine measurement or forbidden command was run. No commit was made.

## Residual risk

The magistrate should double-check the H-interpreter decision with an actual future v4 candidate and route the already-recorded `t0_non_observer_share_max` removal case to the registration-v4 lane. The best-effort results wording and the five-path diff are ready for final review.