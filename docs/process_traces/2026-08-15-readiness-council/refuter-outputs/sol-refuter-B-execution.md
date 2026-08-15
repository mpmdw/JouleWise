```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "F1/F2/F3/F5/F6 are confirmed launch blockers; F4's privilege gap survives but its claimed current timing premise is false.",
  "workspace": {
    "base_requested": "ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b",
    "base_mode": "descendant",
    "head_start": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "head_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "upstream_end": "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The T-0 consumer exists, but no shipped operational producer creates its nine private input files."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "Independent schema, script, runbook, packet, and custody searches found only test-fixture synthesis, not a production capture path; duplicates F1."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "A controlled clean-machine replay returned READY after 1 minute in 60.09 seconds, while the author requires at least 600 seconds."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "verdict": "PARTIAL",
        "summary": "The undocumented sudo dependency is real, but the claim that the current E-7b necessarily cools the timestamp is false because E-7b currently lasts only about one minute."
      },
      {
        "id": "F5",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The authoritative packet and its 49dcc49 measurement checkout predate the T-0 author and go directly from E-9 to ARM."
      },
      {
        "id": "F6",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The runbook example violates the author's raw env, key-name, plan-path, and exact repository-binding contracts."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --quiet ac3fe1d..HEAD -- joulewise/arm_readiness_evidence_t0.py scripts/author_arm_evidence_t0.py scripts/prewindow_check.sh docs/phase_2/window_runbook.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["audited_target_delta_exit=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "audited_target_delta_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -l -F 'joulewise.arm_readiness_t0_command_capture.v1' . | sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["./joulewise/arm_readiness_evidence_t0.py"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\./joulewise/arm_readiness_evidence_t0\\.py$"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "bash -c 'ps(){ :; }; uptime(){ echo \"11:00 up 1 day, 1 user, load averages: 0.10 0.20 0.30\"; }; pmset(){ echo \"Now drawing from AC Power\"; }; sudo(){ echo \"Network Time: Off\"; }; df(){ printf \"%s\\n\" \"Filesystem 1G-blocks Used Available Capacity Mounted\" \"probe 100 1 99 1% /\"; }; export -f ps uptime pmset sudo df; /usr/bin/time -p /bin/bash scripts/prewindow_check.sh --wait --timeout-min 2 --window alpha'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["clean check 3/3", "READY after 1 min.", "real 60.09"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "READY after 1 min\\."
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; from types import SimpleNamespace; import joulewise.arm_readiness_evidence_t0 as t; c=SimpleNamespace(values={},custody_pack_root=Path(\"/definitely-missing\"));\\ntry: t._clock_attestation(c,kind=\"CLOCK_ATTESTATION\")\\nexcept t.T0EvidenceAuthoringError as e: print(e.kind, e.reason_code, str(e), sep=\" | \")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["CLOCK_ATTESTATION | evidence_author_t0_clock_attestation_missing | independent-clock attestation is unreadable: /definitely-missing/arm_readiness.t0.inputs/clock-attestation.json"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "evidence_author_t0_clock_attestation_missing"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "/usr/bin/sudo -n /usr/sbin/systemsetup -getusingnetworktime",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 126,
        "tail": ["time: /usr/bin/sudo: Operation not permitted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Network Time: Off"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git cat-file -e 49dcc49a:scripts/author_arm_evidence_t0.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 128,
        "tail": []
      },
      "expected": {
        "exit_code": 128,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F-BD1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is a descendant of ac3fe1d; only README.md, RUN_STATE.md, and the audit manifest differ. All four audited code/runbook files are byte-identical to the pin.",
      "needs": ""
    },
    {
      "id": "F-ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The read-only sandbox denied temporary-file creation and all sudo execution, preventing a full synthetic GO receipt and direct inspection of the installed sudoers rule.",
      "needs": "Lead should replay the exact sudo probe and repaired end-to-end author→arm→verify→consume flow in the controlled writable bench environment."
    }
  ]
}
```

## Findings

### F1 — CONFIRMED (blocker)

Independent searches for `arm_readiness.t0.inputs`, the command/attestation/launch schema literals, all nine filenames, and plausible capture/clock/ledger scripts found no operational producer. Each schema literal and the private-directory name occurs only in [arm_readiness_evidence_t0.py](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:38>); filename searches add only the test fixture. `find ~/JouleWise-window-custody` found no input, source, or evidence namespace.

The consumer directly reads the six captures at [lines 448–497](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:448>), clock attestation at [500–547](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:500), arm context at [550–568](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:550), and launch manifest at [595–620](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:595). The direct missing-file probe reproduced `evidence_author_t0_clock_attestation_missing`.

The current runbook names the final author command at [802–809](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/docs/phase_2/window_runbook.md:802), but no preceding step creates its inputs. Severity is correctly blocker. The remedy should be a shipped capture/orchestration tool that atomically records boot ID, monotonic bounds, argv/cwd/exit/output, attestation, context, and launch manifest—not relaxed validation or operator-authored JSON.

The phrase “no human can hand-produce” is literally overstated: a human can fabricate these plain JSON objects. That worsens, rather than refutes, the authenticity defect.

### F2 — CONFIRMED (blocker; duplicate of F1)

The only producer-like code is test setup: [test_arm_readiness_evidence_t0.py:468](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/tests/test_arm_readiness_evidence_t0.py:468) synthesizes all six captures, including a manufactured 600-second interval, and writes them at [line 544](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/tests/test_arm_readiness_evidence_t0.py:544). That is fixture construction, not shipped tooling.

The author verifies canonical bytes, self-reported boot identity, freshness, and ordering at [467–494](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:467) and [1587–1597](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:1587), but there is no trusted capture-origin marker. Hashing hand-authored bytes cannot distinguish them from wrapper-produced bytes. Some current-state claims are re-probed, but historical command timing—notably the ten-minute wait—remains forgeable.

Severity is blocker, but F1 and F2 should produce one work order, not two.

### F3 — CONFIRMED (blocker)

I replayed the unchanged wait loop with only machine-state commands stubbed to deterministic clean results. It completed:

- `clean check 3/3`
- `READY after 1 min.`
- `real 60.09`

The script hard-codes three checks and 30-second intervals at [lines 36–37](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/scripts/prewindow_check.sh:36); it checks immediately, sleeps after checks one and two, then exits at [177–193](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/scripts/prewindow_check.sh:177). The author independently requires 600 seconds at [946–959](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:946).

Severity is correctly blocker. Preserve the author’s ten-minute check; repair the wait to require ten continuous clean minutes—preferably a `clean_since` monotonic interval—then capture it through the producer from F1/F2.

### F4 — PARTIAL (blocker survives)

The author unconditionally runs `/usr/bin/sudo -n /usr/sbin/systemsetup -getusingnetworktime` and refuses nonzero output at [884–903](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:884). D-004 grants NOPASSWD only to `/usr/bin/powermetrics` at [decision_log.md:316](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/docs/decision_log.md:316), confirmed again by the installed-workflow record at [phase_1_exit_checklist.md:288](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/docs/phase_1/phase_1_exit_checklist.md:288). The runbook itself says `systemsetup` reads require administrator rights at [509–514](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/docs/phase_2/window_runbook.md:509).

What does not survive is the stated current timeline: F3 proves E-7b presently lasts about one minute, not ten, so an interactive timestamp might still be warm. Once F3 is correctly repaired, however, relying on an undocumented cached credential becomes unsound and the privilege gap becomes deterministic under the documented policy.

The exact live probe was attempted, but sandbox policy blocked `sudo` itself with exit 126. The remedy should be either an exact-argv, read-only NOPASSWD allowance for `systemsetup -getusingnetworktime`, verified during desk qualification, or a narrowly privileged attestation helper. Do not grant unrestricted `systemsetup`.

### F5 — CONFIRMED (blocker)

The packet SHA-256 is `5c05f6fe99b547467372b90a61957163c47c891f6ff0c6414a4d3a7c40e47a96`. It binds `49dcc49a` and the older `6246b618…` pack at [lines 39–40](</Users/edr/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:39). The actual measurement checkout is still clean at `49dcc49a`, and `scripts/author_arm_evidence_t0.py` is absent there: `git cat-file -e 49dcc49a:scripts/author_arm_evidence_t0.py` exited 128. The historical runbook at that commit also contains no T-0 author step; the baseline `ac3fe1d` does.

The packet declares itself executable without the runbook at [line 441](</Users/edr/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:441) and goes from E-9 directly to E-9a ARM at [470–480](</Users/edr/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:470). Its §0.6 accurately describes the old tree’s missing author at [151–183](</Users/edr/JouleWise-window-custody/t4-session-20260810/arm-packet-alpha-FINAL-20260813.md:151), but is stale against the audit baseline.

Severity is blocker. After the integrated repair, re-freeze the reviewed measurement checkout and issue a new packet containing the capture steps, author step, 20-minute horizon, and re-author procedure. Merely editing the old packet would leave its frozen-head claims false.

### F6 — CONFIRMED (blocker)

The executable contract probe against the runbook’s example produced:

- `window.env value for PACK_ROOT is ambiguous`
- Missing required keys: `CUSTODY_ROOT`, `CLAIM_BACKUP_DEST`, `BOUND_BACKUP_DEST`
- Dollar-bearing assignments: `PACK_ROOT`, `RUNS_ROOT`, `BOUND_RUNS_ROOT`, `LEDGER_HEAD_PIN`
- Chain repository value: `${MEASUREMENT_REPO:-/Users/edr/JouleWise-measurement-20260813}`, not the exact reviewed repository

Those failures follow directly from the example at [window_runbook.md:181](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/docs/phase_2/window_runbook.md:181), the raw parser at [571–592](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:571), required names at [652–666](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:652), and chain regex at [671–674](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:671).

The plan mismatch is worse than reported. Production `plan_tree.json` stores a repository-relative path at [line 973](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/configs/campaigns/d117_floor_qwen25_1p5b_v1/plan_tree.json:973), but the author joins that to `pack_root` at [line 1149](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:1149), producing a doubled, nonexistent path. The synthetic test fixture instead uses `pack / "calibration_plan.json"` at [test line 361](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/tests/test_arm_readiness_evidence_t0.py:361), masking the production-pack shape.

Severity is blocker. The sound remedy is to generate `window.env` and `launch-manifest.json` from one typed context, emit fully expanded exact literals, align key names, resolve plan-tree paths relative to the repository, and add an end-to-end test using the real production pack layout.

One further end-to-end obstacle surfaced: baseline commit `ac3fe1d` lacks the three `JouleWise-Terminal-Review*` commit trailers demanded at [918–930](</private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-bexe/joulewise/arm_readiness_evidence_t0.py:918). The integrated repair must establish an operational producer for that terminal-review evidence too.

Five findings therefore survive outright; F4’s specific timing rationale dies, but its privilege-contract defect survives. The minimal true program is two work orders: first, one integrated T-0 acquisition/contract repair covering the nine-input producer, continuous ten-minute wait, exact privileged clock-read route, env/manifest/plan/chain alignment, terminal-review evidence, and a real-pack author→ARM→verify→consume rehearsal; second, a dependent re-freeze and packet reissue at the exact reviewed head. F1 and F2 are one defect, while F3/F4/F6 must be repaired and tested together because their contracts interact.

## Residual risk

The read-only sandbox denied all temporary-file creation, so the full author could not reach a valid synthetic GO receipt; its top-level attempt refused earlier because `TemporaryFile` had no usable directory. The same sandbox blocked direct `sudo` execution and protected reading of the 47-byte root-owned sudoers file. The clean-machine E-7b replay stubbed only observable machine state and was not quiet-Mac validation; it conclusively exercised the shipped wait control flow without claiming hardware readiness. No repository files changed.