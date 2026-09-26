```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "MERGE: the seal matches the prescribed substitutions and local template hashes; one test nit and two verification limits remain.",
  "workspace": {
    "base_requested": "c6814dd8",
    "base_mode": "exact",
    "head_start": "23dd9909e1f34610681b8616f573dee1a944cc3a",
    "head_end": "23dd9909e1f34610681b8616f573dee1a944cc3a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGE",
    "s1": "Both digests match their correctly ordered templates. Local Git identifies 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87 as the GitHub-authored merge of PR #412; gh API confirmation was unavailable.",
    "s2": "The candidate changes exactly the prescribed header and three literal tokens, without backticks. Placeholder count is zero.",
    "s3": "The issuer's placeholder pattern has zero matches and its commit and digest patterns each have one match. The fast suite passes. The longer suite has one unrelated live-machine probe failure. No fixed digest of this file was found in the inspected consumers; the issuer requires the arm-supplied digest of the current bytes.",
    "s4": "Both pinned templates contain ProcessType=Interactive and are unchanged through the candidate. The installer checks rendered ProcessType and per-window rendered digests, but does not compare current template source bytes with the historical digests in this registration.",
    "findings": [
      {
        "id": "F1",
        "severity": "nit",
        "text": "tests/test_acc_25g83_rev5.py:95-98 replaces the former pending header string. That replacement is now a no-op, so this test no longer exercises the header transition. Its placeholder and issuer checks still run; this does not change the scientific rule."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git show --no-patch --format=fuller 9b750bf3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87",
          "Merge: 4e48c159 dc210094",
          "    Merge pull request #412 from mpmdw/feat/2026-09-25-acc-launch-context"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Merge pull request #412"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "gh pr view 412 --json mergeCommit",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "check your internet connection or https://githubstatus.com"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git show 9b750bf3:configs/launchd/com.joulewise.night.plist.template | shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8  -"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8  -$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git show 9b750bf3:configs/launchd/com.joulewise.night-probe.plist.template | shasum -a 256",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd  -"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd  -$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --numstat c6814dd8 23dd9909 && git diff --check c6814dd8 23dd9909",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2\t2\tconfigs/calibration/preregistration_d079_epoch_25g83_rev1.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^2\\t2\\tconfigs/calibration/preregistration_d079_epoch_25g83_rev1.md$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "grep -c -E '<PR-L-MERGE[-]SHA>|<TEMPLATE[-]SHA256:' configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["0"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "^0$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nfrom pathlib import Path\nimport re\ns=Path('configs/calibration/preregistration_d079_epoch_25g83_rev1.md').read_text()\nfor name, pat in [('placeholder',r'<PR-L-MERGE-SHA>|<TEMPLATE-SHA256:[^>]+>'),('commit',r'template at commit [0-9a-f]{40}\\b'),('digests',r'template digests [0-9a-f]{64} and [0-9a-f]{64}\\b')]:\n m=list(re.finditer(pat,s))\n print(name,len(m),[x.group() for x in m])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "placeholder 0 []",
          "commit 1 ['template at commit 9b750bf3cb0abc4c0a4474a2b5bb1e1e4ec52c87']",
          "digests 1 ['template digests e62a461b9f739be6aa57588219674cbb27f574dc40930ee1ee706f230442e5c8 and 1570b74587075445ee64fff9b14b718a4b753ec3432db9363455636a2d2fc1fd']"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "placeholder 0.*commit 1.*digests 1"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_acc_25g83_rev5 tests.test_preregistration_chain_digest",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 17 tests in 11.386s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 17 tests.*OK"
      }
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_issue_calibration_acceptance_generation tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAIL: test_live_probes_report_this_machine_against_the_active_epoch (tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch)",
          "AssertionError: None is not an instance of <class 'str'>",
          "Ran 217 tests in 79.186s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 217 tests.*OK"
      }
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --exit-code 9b750bf3 23dd9909 -- configs/launchd/com.joulewise.night.plist.template configs/launchd/com.joulewise.night-probe.plist.template",
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
      "id": "V11",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1 --untracked-files=all",
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
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "GitHub API was unreachable, so gh could not independently confirm the mergeCommit field. The local GitHub-authored merge commit names PR #412.",
      "needs": "Re-run gh pr view 412 --json mergeCommit when API access returns."
    },
    {
      "id": "G2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The live-machine test fails because observe_machine reports os_build=None and hardware_model=None in this session; the failure does not read the changed registration file.",
      "needs": "Run the live identity probe on the intended macOS host."
    },
    {
      "id": "G3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A future arm checkout could contain changed, still-Interactive templates: installer validation checks rendered ProcessType and rendered digests but does not compare source template hashes to this registration's historical pins.",
      "needs": "At W1 arm, compare the arm checkout's two template hashes with the registered values and retain the rendered-plist evidence."
    }
  ]
}
```

## Findings

- **F1 — NIT.** The old-header replacement in [test_acc_25g83_rev5.py](/Users/edr/code/JouleWise-wt-817355d2-solens/tests/test_acc_25g83_rev5.py:95) is now a no-op. The test still exercises the issuer’s seal checks, so this does not affect the science; it leaves the header wording without that test’s coverage.

## Residual risk

The seal records template bytes at PR #412’s merge commit. The installer later renders templates from the arm checkout and checks `ProcessType=Interactive` and the rendered digests. Those checks do not themselves prove that the arm checkout’s template source bytes equal the two historical hashes. The templates are equal in this candidate; their equality needs checking again at W1 arm. No W1 capture or live launch was performed in this review.