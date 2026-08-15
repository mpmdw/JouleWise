```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All four launch/consumption blockers survive; F1 needs a wording correction, and F3/F4 should be one census-semantics work order.",
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
        "title": "Prospective gamma manifest has no finalizer or claim-consumer wire",
        "detail": "analyze-claims rejects v3.prospective; the U7-required reusable builder and validator symbols, postcollection finalizer, and queue row are absent. A pack-local draft builder exists, so the broad phrase 'no prospective builder' should be narrowed.",
        "remedy": "Implement and validate the prospective-to-final attachment transition and wire the resulting schema into analyze-claims; a schema allowlist alone is insufficient."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Margin recorder rejects the governed estimator vocabulary",
        "detail": "The real alpha pack deterministically returns REFUSE/authoritative_input_invalid before bundle discovery or receipt publication.",
        "remedy": "Authorize only the pack-pinned extraction-spec path before its first authenticated read and add committed-spec end-to-end regressions."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Maintenance census treats resident services as forbidden activity",
        "detail": "Current launchd state has several regex-matching services running continuously, so the required exit-1/empty condition cannot hold.",
        "remedy": "Replace resident-process absence with an activity/busy-state predicate for perturbing maintenance work; do not merely delete names."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Browser and monitor census patterns match resident system agents",
        "detail": "Safari launch agents remain running with the Safari application closed, while unanchored 'watch' matches watchdogd and watchlistd.",
        "remedy": "Match actual browser applications and exact monitoring executables/argv shapes; remove unanchored substring classification."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --name-status ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b..8937dec9bd7be8f6d87694a739089ac8434b8bc9",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "M README.md",
          "M RUN_STATE.md",
          "A docs/process/audit-baseline-manifest.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "README.md.*RUN_STATE.md.*audit-baseline-manifest.json"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 -c 'import runpy,sys,tempfile; tempfile.tempdir=\"/private/tmp\"; sys.argv=[\"joulewise\",\"analyze-claims\",\"--analysis-manifest\",sys.argv[1],\"--runs-root\",sys.argv[2],\"--floor-artifact\",\"/private/tmp/nonexistent-floor.json\",\"--output\",\"/private/tmp/nonexistent-claim-verdicts.json\"]; runpy.run_module(\"joulewise\",run_name=\"__main__\")' \"$PWD/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json\" \"$PWD\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "error: unsupported analysis manifest schema_version: 'joulewise.analysis_manifest.v3.prospective'"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "unsupported analysis manifest schema_version.*v3\\.prospective"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'import runpy,sys,tempfile; tempfile.tempdir=\"/tmp\"; sys.argv=[\"scripts/record_window_duration_margins.py\",\"--repository-root\",sys.argv[1],\"--pack-root\",sys.argv[2],\"--runs-root\",\"/tmp\",\"--receipt-root\",\"/tmp\",\"--pack-identity\",\"plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v1\"]; runpy.run_path(\"scripts/record_window_duration_margins.py\",run_name=\"__main__\")' \"$PWD\" \"$PWD/configs/campaigns/d117_floor_qwen25_1p5b_v1\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "{\"detail\": \"v2_authentication_forbidden_json_key: forbidden key 'estimator_registration' at pack-pinned extraction spec.cells[1].estimator_registration\", \"reason\": \"authoritative_input_invalid\", \"status\": \"REFUSE\"}"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "authoritative_input_invalid.*estimator_registration"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "/usr/bin/pgrep -lf XProtect",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 3,
        "tail": [
          "sysmon request failed with error: sysmond service not found",
          "pgrep: Cannot get process list"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "[0-9]+.*XProtect"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/bin/launchctl print system/com.apple.watchdogd",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "state = running",
          "program = /usr/libexec/watchdogd",
          "pid = 552",
          "last exit code = (never exited)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "state = running.*watchdogd"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "/bin/launchctl print gui/$(id -u)/com.apple.SafariLaunchAgent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "state = running",
          "program = /System/Cryptexes/App/usr/libexec/SafariLaunchAgent",
          "pid = 1993",
          "last exit code = (never exited)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "state = running.*SafariLaunchAgent"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is a clean descendant of ac3fe1d; only README.md, RUN_STATE.md, and the baseline-manifest commit differ. Instrument code, configs, tests, and the runbook are byte-unchanged.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Managed-shell process enumeration is denied, so exact live pgrep output could not be captured. Current launchd running-state, executable paths, PIDs, and regex matching independently establish F3/F4.",
      "needs": "Re-run the exact pgrep commands once from an ordinary non-agent shell after repair."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "No arm receipt was authored: this session is agent load, WRITE_SCOPE is empty, and the sandbox is read-only. Authoring T-0 evidence here would violate the quiet-Mac gate.",
      "needs": ""
    }
  ]
}
```

## Findings

The checkout remained clean at `8937dec`; `git diff --quiet ac3fe1d..HEAD -- joulewise scripts tests configs docs/phase_2/window_runbook.md` exited 0.

### F1 — CONFIRMED · blocker

`analyze-claims` exited 2 with the reported unsupported-schema error and created no output. Its loader admits only v1 and historical v3 at [inputs.py:554](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/analysis_engine/inputs.py:554).

Independent searches found:

- Exact U7 symbols: `git grep ... build_prospective_analysis_manifest_v3|validate_prospective_analysis_manifest_v3 ac3fe1d` → exit 1.
- Postcollection attachment usage exists only in the generated JSON, pack generator, and tests—no finalizer.
- Tool inventory contains historical manifest builders and `claims_lint.py`, but no prospective analysis producer/finalizer.
- The targeted queue/kernel search exited 1.

The historical v3 validator is genuinely frozen to Splitwise semantics at [analysis_manifest_v3.py:603](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/analysis_manifest_v3.py:603). The U7 contract explicitly required the missing APIs at [DRAFT-U5U7.md:23555](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/docs/process_traces/2026-08-07-plan-factory/DRAFT-U5U7.md:23555).

Correction: the pack generator does contain `build_analysis_manifest` and emits the draft schema and empty postcollection slots at [generate_configs.py:1085](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:1085). Thus “no prospective builder whatsoever” is too broad; the missing components are the reusable U7 API, validator, finalizer, and consumer.

Severity is correctly blocker. The remedy must implement the authenticated prospective-to-final transition and consumer integration before collection; merely accepting the schema string would create an unsafe half-fix. This also avoids colliding with the extraction-to-analysis same-session requirement at [window_runbook.md:61](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/docs/phase_2/window_runbook.md:61).

### F2 — CONFIRMED · blocker

The exact recorder path against the real alpha pack returned:

```text
status=REFUSE
reason=authoritative_input_invalid
detail=v2_authentication_forbidden_json_key ... cells[1].estimator_registration
exit=2
```

No receipt namespace was created. The recorder opens the V2 session at [window_duration_margins.py:897](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/window_duration_margins.py:897) and reads the spec at [window_duration_margins.py:394](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/window_duration_margins.py:394). Authentication rejects that reserved key unless authorized at [authentication_io.py:175](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/authentication_io.py:175).

Independent search found the authorization only in the authentication API and generalized mint; the recorder has no mirror. The recorder tests contain no `estimator_registration`, while their “real floor pack shapes” start at [test_window_duration_margins.py:213](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/tests/test_window_duration_margins.py:213).

Severity is correctly blocker. The proposed narrow remedy is sound: authorize the exact pack-pinned spec before its first read, then add alpha and beta tests using the committed re-specced files. Do not globally relax the reserved-key rule.

### F3 — CONFIRMED · blocker

The exact `pgrep` replay was sandbox-blocked, but launchd independently reports these matching processes currently running:

- `softwareupdated` PID 703
- `backupd-helper` PID 620
- `mediaanalysisd` PID 1276
- `photoanalysisd` PID 1425

Their executable paths all match the production regex. Several report one run and “never exited.” Production requires exit 1 plus empty stdout at [arm_readiness_evidence_t0.py:963](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/arm_readiness_evidence_t0.py:963), so one resident match makes `t0.background_quiet` underivable.

Test characterization needs a small correction: the main fixture does fake every `pgrep` as exit 1 at [test_arm_readiness_evidence_t0.py:553](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/tests/test_arm_readiness_evidence_t0.py:553). There are Darwin capture-only tests at line 973, but they merely serialize whatever exit/output occurs; they never invoke `_expect_absent` or require a successful census. Thus CI coverage remains non-discriminating.

Severity is blocker. The sound remedy is activity-based maintenance detection, not absence of resident service processes.

### F4 — CONFIRMED · blocker

With Safari’s application service absent, launchd still reports:

- `SafariLaunchAgent` PID 1993, running, never exited
- `Safari.SafeBrowsing.Service` PID 2716, running, never exited
- `watchdogd` PID 552, running, never exited
- `watchlistd` PID 1999, running, never exited

Regex replay over their executable paths matched every one. The production patterns are unanchored at [arm_readiness_evidence_t0.py:1344](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-eexe/joulewise/arm_readiness_evidence_t0.py:1344); `Safari` therefore detects background agents, and `watch` detects both system daemons.

Severity is blocker. Repair browser detection around actual application executables and monitor detection around exact executable/argv identities. Preserve the separate `pgrep -x caffeinate` and agent checks.

## Residual risk

The managed shell denied process-table enumeration, and Computer Use was not permitted to access Terminal or Activity Monitor. Therefore the exact `pgrep` stdout must be replayed in an ordinary shell during the repair gate. Launchd’s current running-state and program paths make the blocker verdict robust, but post-fix validation still needs one real quiet-machine pass plus a negative control that launches each genuinely forbidden process.

All four findings survive. The minimal true program is three work orders: (1) prospective gamma manifest validation/finalization/claim consumption; (2) the recorder’s narrow governed-spec authorization plus real-spec regressions; and (3) one combined T-0 census-semantics repair covering maintenance activity, actual browser applications, and exact monitor identities.