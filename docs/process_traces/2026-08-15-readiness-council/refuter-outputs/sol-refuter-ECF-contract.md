```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All four readiness blockers survive defensive refutation; F1's L1 rationale and F3/F4's CI-coverage narratives require qualification.",
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
        "title": "Prospective D-117 claim-consumption edge has no compatible validator, finalizer, or consumer"
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Collection-margin recorder rejects the governed estimator vocabulary now pinned by both floor packs"
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Maintenance census mistakes resident macOS services for active maintenance churn"
      },
      {
        "id": "F4",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "title": "Browser and monitor regexes match resident Safari, watchdog, and watchlist services"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git merge-base --is-ancestor ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "8937dec9bd7be8f6d87694a739089ac8434b8bc9",
          "ANCESTOR_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "8937dec.*ANCESTOR_EXIT=0"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"from pathlib import Path; from joulewise.analysis_engine.inputs import load_manifest; load_manifest(Path('configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json'))\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AnalysisInputError: unsupported analysis manifest schema_version: 'joulewise.analysis_manifest.v3.prospective'",
          "PROBE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "unsupported analysis manifest schema_version.*v3\\.prospective"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n 'build_prospective_analysis_manifest_v3|validate_prospective_analysis_manifest_v3' joulewise scripts tests; rg -n -i 'postcollection.*(finaliz|attach).*(analysis|manifest)|(analysis|manifest).*postcollection.*(finaliz|attach)' joulewise scripts --glob '*.py'; rg -n -i 'prospective.*analysis.*manifest|analysis.*manifest.*prospective|postcollection.*analysis.*manifest' TASK_QUEUE.md docs/process/state_kernel.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "FUNCTION_SEARCH_EXIT=1",
          "FINALIZER_SEARCH_EXIT=1",
          "QUEUE_SEARCH_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FUNCTION_SEARCH_EXIT=1.*FINALIZER_SEARCH_EXIT=1.*QUEUE_SEARCH_EXIT=1"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"from pathlib import Path; from joulewise.authentication_io import V2AuthenticationReadSession, read_authentication_input; s=V2AuthenticationReadSession(); s.__enter__(); read_authentication_input(Path('configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json'), grammar='json', label='pack-pinned extraction spec')\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "V2AuthenticationInputError: v2_authentication_forbidden_json_key: forbidden key 'estimator_registration' at pack-pinned extraction spec.cells[1].estimator_registration",
          "PROBE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "v2_authentication_forbidden_json_key.*cells\\[1\\]\\.estimator_registration"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/bin/launchctl print gui/$(/usr/bin/id -u) | rg -i 'Safari|watchdog|watchlist'; /bin/launchctl print system | rg -i 'XProtect|backupd|softwareupdated|watchdog'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "com.apple.SafariLaunchAgent",
          "com.apple.watchlistd",
          "com.apple.watchdogd",
          "com.apple.backupd",
          "com.apple.softwareupdated"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SafariLaunchAgent|watchlistd|watchdogd|backupd|softwareupdated"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "/usr/bin/pgrep -lf '<exact repository census patterns>'",
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
        "exit_code": 1,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_receipt_oracle_is_recomputed_from_the_production_model",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FileNotFoundError: No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "B1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is a descendant of ac3fe1d; intervening paths are README.md, RUN_STATE.md, and the audit-baseline manifest itself. Audited runbook and row-registry hashes equal the manifest pins.",
      "needs": ""
    },
    {
      "id": "E1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The review sandbox denies process-table access and all temporary-file creation. Exact pgrep replay returned exit 3 and the focused unittest could not import through tempfile; launchd and plist inspection supplied independent resident-service evidence.",
      "needs": "At the next lead-controlled, no-agent preflight, replay the four exact pgrep commands for a fresh PID-level capture."
    }
  ]
}
```

## Findings

### F1 — CONFIRMED (blocker)

The claim-consumption obligation is real. D-117 requires three prospective claim windows and explicitly includes a contrast manifest in the desk deliverables ([decision_log.md:7658](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/decision_log.md:7658)); D-122 requires the added prefill contrast to flow through fail-closed claim machinery ([decision_log.md:7874](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/decision_log.md:7874)); and the runbook requires exact-basis contrast extraction, analysis, and reporting ([three-night packet:470](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/strategy/2026-08-07-three-night-operator-packet.md:470)).

The pack uses `joulewise.analysis_manifest.v3.prospective` and retains empty postcollection slots ([analysis_manifest_v3.json:2](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:2), [line 1044](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/analysis_manifest_v3.json:1044)). Direct `load_manifest` replay refused it with the alleged unsupported-schema error. The only final-v3 validator requires the historical schema, Splitwise design, fixed `n=10`, and exactly two stages ([analysis_manifest_v3.py:603](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/analysis_manifest_v3.py:603)). Independent searches found neither specified prospective function, no postcollection finalizer, and no queue/kernel row for this successor edge.

Qualification: L1 does not categorically prohibit implementing code after collection; immutable evidence could be re-extracted and analyzed together later. But that does not make the instrument ready, and post-outcome implementation would require heightened proof that frozen estimands were not changed. The blocker severity is correct.

Remedy shape: sound. Land a governed prospective validator plus deterministic attachment/finalization path and either teach `analyze-claims` that finalized schema or convert it mechanically into a consumer-compatible final v3. Cover both D-122 contrasts, preserve frozen multiplicity semantics, and add a dedicated queue row.

### F2 — CONFIRMED (blocker)

This obligation is explicit, not inferred. D-133 authorized the tighter-estimator re-spec ([decision_log.md:8785](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/decision_log.md:8785)) and separately ruled that collection close-out gates on the margin receipt ([decision_log.md:8817](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/decision_log.md:8817)). Runbook §11 mandates recorder → backup → extraction and says `REFUSE` stops close-out without a receipt ([window_runbook.md:1449](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/phase_2/window_runbook.md:1449)).

Both pack-pinned specs contain `estimator_registration` in all three comparative cells; the first is visible at [d117_qwen25_1p5b_extraction_spec.json:202](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/configs/floor_mint/d117_qwen25_1p5b_extraction_spec.json:202). The recorder opens `V2AuthenticationReadSession` ([window_duration_margins.py:897](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/window_duration_margins.py:897)) and reads the spec without authorization; the common reader forbids that key by default ([authentication_io.py:175](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/authentication_io.py:175)). The direct critical-path read reproduced `v2_authentication_forbidden_json_key`. The recorder maps it to `authoritative_input_invalid` and derives before any write ([window_duration_margins.py:967](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/window_duration_margins.py:967), [line 1189](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/window_duration_margins.py:1189)). Only the mint authorizes the governed spec before reading it ([mint_floor_artifact_generalized.py:1255](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/scripts/mint_floor_artifact_generalized.py:1255)). The recorder tests’ “real pack” fixture omits the vocabulary entirely ([test_window_duration_margins.py:213](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/tests/test_window_duration_margins.py:213)).

Remedy shape: sound and small. Authorize only the authenticated plan-tree-pinned extraction-spec path, before its first authentication read. Add regressions using both actual governed specs plus a negative case proving unpinned or report-side estimator vocabulary still refuses.

### F3 — CONFIRMED (blocker)

The row is contractually mandatory: the sole registry marks `t0.background_quiet` `ALWAYS`, `ARM_ONLY`, requiring `MAINTENANCE_CENSUS` ([d117_row_registry_v1.json:336](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/configs/arm_readiness/d117_row_registry_v1.json:336)). D-134 prohibits UNKNOWN and makes missing live evidence refuse ([decision_log.md:8609](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/decision_log.md:8609)).

The contract requires maintenance to be “finished or paused,” not every resident service binary to disappear ([beta_arm_readiness.md:55](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/phase_2/beta_arm_readiness.md:55)). Implementation instead requires `pgrep` exit exactly 1 and empty stdout, over names including XProtect, backupd, and softwareupdated ([arm_readiness_evidence_t0.py:963](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/arm_readiness_evidence_t0.py:963)). Current `launchctl` evidence independently showed active PIDs for XProtect, `backupd`, and `softwareupdated`; their system plists resolve to executables bearing those exact names.

The CI narrative needs narrowing: Darwin tests do execute real `pgrep`, but merely serialize its exit/output ([test_arm_readiness_evidence_t0.py:915](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/tests/test_arm_readiness_evidence_t0.py:915)). They never call `_expect_absent`; the actual authoring success fixture still forces every `pgrep` to exit 1 ([line 553](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/tests/test_arm_readiness_evidence_t0.py:553)).

Remedy shape: do not merely delete names. Replace process-existence testing with resident-aware activity checks for indexing, backup, updates, and malware scanning, or an explicit resident-service classification plus activity-specific probes. Add a real-host quiescent baseline and fixtures for genuinely active maintenance.

### F4 — CONFIRMED (blocker)

`no_stray_keepawake` is likewise an `ALWAYS`, `ARM_ONLY` row ([d117_row_registry_v1.json:390](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/configs/arm_readiness/d117_row_registry_v1.json:390)). Its checked contract view says no *unrelated* browser, monitor, watcher, tail, or campaign process—not no service whose name contains those substrings ([beta_arm_readiness.md:61](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/docs/phase_2/beta_arm_readiness.md:61)).

The implementation uses broad full-command regexes for `Safari|...` and `...|watch` ([arm_readiness_evidence_t0.py:1344](/private/tmp/claude-501/-Users-edr-code-JouleWise/e972460c-5f2e-4c7b-bac5-1583f5517547/scratchpad/refuter-tree-econ/joulewise/arm_readiness_evidence_t0.py:1344)). Current GUI launchd state contained active `SafariLaunchAgent`, Safari SafeBrowsing/history/bookmark services, and `watchlistd`; system state contained active `watchdogd`. Plist inspection confirmed executable paths ending in `SafariLaunchAgent`, `watchlistd`, and `watchdogd`, all matching the repository regexes.

Severity is correctly blocker. Remedy shape: retain the exact `caffeinate` check, but classify browser UI/automation by anchored executable identity and monitor processes by exact reviewed command/argv. Explicitly exclude unrelated Apple services such as `watchdogd`, `watchlistd`, and Safari background agents when no browser UI or automation process is running. Add passability tests that actually invoke `_derive_process_census`, not only probe serialization.

Synthesis: F1–F4 all survive; none is a phantom defect. The minimal true work-order set is three bounded units: (1) complete and queue the prospective D-117 manifest finalization/claim-consumer edge; (2) authorize the pack-pinned governed extraction spec in the collection-margin recorder and add production-shape regressions; and (3) repair both T-0 censuses together with resident-aware semantics and real passability tests. No new acceptance threshold, manifest redesign, or weakening of fail-closed readiness is warranted.

## Residual risk

The sandbox denied direct process enumeration (`pgrep` exit 3) and temporary-file creation, so the exact PID-level commands and focused unittest could not complete here. Current launchd PID records plus executable plist identities independently establish the overmatching mechanisms, but the lead should retain a fresh exact-`pgrep` capture after all agents close and before accepting the T-0 repair. The repository remained clean and unchanged.