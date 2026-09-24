```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Updated the v3 notice and summary text from bound registration data; 285 named-module tests pass.",
  "workspace": {
    "base_requested": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "base_mode": "exact",
    "head_start": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "head_end": "313efcca236a8c914e4956fc7d686a810060e5ea",
    "upstream_end": null,
    "branch": "feat/2026-09-23-a276-notice-v3"
  },
  "pathspec": [
    "joulewise/evidence_night.py",
    "joulewise/quiet_predicate_campaign.py",
    "tests/test_evidence_night.py",
    "tests/test_quiet_predicate_campaign.py"
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
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 285 tests in 296.541s", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign > /tmp/a276-after.log 2>&1; result=$?; tail -n 24 /tmp/a276-after.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 285 tests in 251.811s", "FAILED (errors=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign > /tmp/a276-final.log 2>&1; result=$?; tail -n 5 /tmp/a276-final.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 285 tests in 272.189s", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night tests.test_quiet_predicate_campaign > /tmp/a276-acceptance.log 2>&1; result=$?; tail -n 5 /tmp/a276-acceptance.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 285 tests in 262.466s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": []
}
```

## Change

Changed files: [evidence_night.py](/Users/edr/code/wt-1d3796d5-a276/joulewise/evidence_night.py:276), [quiet_predicate_campaign.py](/Users/edr/code/wt-1d3796d5-a276/joulewise/quiet_predicate_campaign.py:1136), [test_evidence_night.py](/Users/edr/code/wt-1d3796d5-a276/tests/test_evidence_night.py:45), and [test_quiet_predicate_campaign.py](/Users/edr/code/wt-1d3796d5-a276/tests/test_quiet_predicate_campaign.py:98).

The changed v3 notice lines read:

> **Before:** “This first idle-variance evidence night…”; “Busy cores remain a descriptive covariate. The 7,800-second program fits inside 9,000 seconds…”; “During the night exactly one read-only git show…”
>
> **After:** “This idle-variance evidence night…”; “After 600 seconds settling, 12 600-second idle envelopes start 620 seconds apart…”; “The 8,020-second program fits inside the 9,000-second window…”; “A process outside the measurement apparatus at or above 0.5 busy cores refuses the night at the arm check or at t0.”; “A process outside the measurement apparatus using 30 or more core-seconds inside an envelope excludes that envelope. 2 such exclusions in a row end the night.”; “the night is refused at its start if launchd spawned the Wi-Fi log-capture helper corecaptured more than twice in the previous ten minutes”.

The v3 summary sentence changed from “Busy cores are recorded covariates and never an exclusion input.” to “Busy cores are recorded covariates. A process outside the measurement apparatus using 30 or more core-seconds inside an envelope excludes that envelope.” V2 summary wording remains unchanged; a superseded v2 notice is refused.

I dropped the single-`git show` claim. The t0 chain check performs one `git show`, while manifest verification calls `tracked_bytes` for eight tracked files, each of which performs another.

## Verification notes

The baseline’s three failures were the new defect tests. The first two post-change runs exposed incomplete older test fixtures; those fixtures were corrected within scope. The final named-module run passed all 285 tests. No other Python module imports `render_notice` or `pilot_summary` directly. `git diff --check` passed.

The magistrate should double-check the rendered notice against the next sealed plan, the v2 refusal choice, and the claim-bearing full-suite gate during replay. No commit was made.