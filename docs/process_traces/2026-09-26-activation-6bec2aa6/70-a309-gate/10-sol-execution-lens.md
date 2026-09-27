```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The candidate passes focused verdict tests, but two merge commits can rewrite and restore the record while the loader accepts its history.",
  "workspace": {
    "base_requested": "64e39bb9",
    "base_mode": "exact",
    "head_start": "87aad39c7c8d543afc252395797a948e3b4373da",
    "head_end": "87aad39c7c8d543afc252395797a948e3b4373da",
    "upstream_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Merge rewrite followed by merge restore loads",
        "evidence": "The scratch history has harvest, merge rewrite, and merge restore in full path history. The candidate's no-merges query sees only harvest; load_committed_verdict returns LOAD with the harvest commit.",
        "fix": "Check each reachable merge's record tree entry against its parents and refuse a merge that synthesizes a different entry. Permit an honest merge that carries one parent's entry. Add a rewrite-then-restore regression. This extends the dictated closure and needs lead adjudication."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "other",
      "cmd": "PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 /tmp/bfgd_execution_matrix.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "merge rewrite restore: full path history included two rewriting merges; filtered history included only harvest; outcome LOAD"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "LOAD"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 225 tests in 289.543s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_battery_float.CommittedVerdictTests tests.test_battery_float_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 25 tests in 14.658s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "/usr/sbin/sysctl -n kern.osversion",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "sysctl: sysctl fmt -1 1024 1: Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".+"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sole failure in V2 is an unchanged live machine identity test: os_build is None because this sandbox denies kern.osversion sysctl. The isolated test fails the same way.",
      "needs": "Lead may rerun that live probe outside this sandbox."
    },
    {
      "id": "G2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "F1 concerns transient historical rewrites; final HEAD bytes equal the original adding commit, so this probe did not demonstrate an altered final verdict or false calibration.",
      "needs": "Decide whether the dictated closure must also reject transient merge rewrites."
    }
  ]
}
```

## Findings

**F1 — SHOULD-FIX.** The scratch command in V1 built a harvest commit, a merge that rewrote the verdict, and a second merge that restored its original bytes. Full path history listed all three commits; the candidate’s `--no-merges` history listed only harvest, and the loader returned `LOAD`. The adding-blob check proves the *final* bytes match harvest, but does not establish the comment’s broader claim that a merge rewrite is caught. The exact fix and its authority question are in F1 above.

The other probed histories behaved as expected: a single merge rewrite, merge replacement, rename round trip, CRLF edit, gitlink, and symlink refused; honest octopus and cherry-pick histories loaded. A side-branch alteration ignored by `-s ours` refused because that alteration remains in full history.

## Residual risk

The combined test run had one unrelated live `sysctl` failure. The focused verdict and consumer tests passed, and the repository remained clean.