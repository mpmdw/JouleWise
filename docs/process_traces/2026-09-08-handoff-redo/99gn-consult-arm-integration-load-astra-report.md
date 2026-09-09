```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend deterministic probe-result seams; serialization cannot isolate unrelated processes, and the reported census cause remains unproven.",
  "workspace": {
    "base_requested": "9e1c7280",
    "base_mode": "exact",
    "head_start": "9e1c72803839ced9d975cc7b198d4a91d2d75e24",
    "head_end": "9e1c72803839ced9d975cc7b198d4a91d2d75e24",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "ARM-INTEGRATION-LOAD-01", "action": "start_now"},
      {"row": "quiet-machine live validation", "action": "wait_for"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["9e1c72803839ced9d975cc7b198d4a91d2d75e24"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^9e1c72803839ced9d975cc7b198d4a91d2d75e24$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Static inspection only; no tests run. Exact earlier census refusals were not supplied.",
      "needs": "Retain failing row IDs and reason details before attributing census failures to ambient processes."
    }
  ]
}
```

## Scheduling matrix

Row | action | wait_for | collision surface
---|---|---|---
ARM-INTEGRATION-LOAD-01 | start_now | Lead assignment and write scope | Test fixtures and subprocess fixture bootstrap
Quiet-machine live validation | wait_for | Agent-free, lead-controlled window | Whole machine

**Diagnosis.** The integration path is `test_arm_readiness_integration.py:326` → `generate_arm_receipt` → live sampling at `joulewise/arm_readiness.py:8690` → `_evaluate_rows` → `_predicate_passes` (`:6889`) → `_clock_probe_predicate_passes` (`:6739`).

`joulewise/clock_reference.py:110` reads RAW-before, REALTIME, RAW-after; the anchor uses the RAW midpoint and records the enclosing read interval. ARM requires read skew **≤1 ms** and change in REALTIME-minus-RAW from the authored anchor **≤5 ms** (`arm_readiness.py:6823–6835`). Authored inputs additionally enforce R0/R1 skew ≤1 ms, anchor change ≤5 ms, T0 span 600–3600 seconds, R1 duration ≤30 seconds, two reference servers, reference bound ≤0.5 seconds, and validity-origin lag ≤600 seconds (`:6767–6809`).

A scheduler interruption between reads can exceed 1 ms; longer delays also allow clock-discipline divergence against RAW. This is plausible, not a reproduced diagnosis. Freezing `time.monotonic_ns` in integration setup (`tests/test_arm_readiness_integration.py:295`) does **not** freeze these reads; fixture authoring itself samples live at `:176`.

Launch fixtures likewise sample live at `tests/test_launch_window.py:839`, author through `author_environment` at `:853`, then invoke the real ARM subprocess at `:866`.

**Census distinction.** Production census checks presence, not total process count or CPU utilization:

- Maintenance: XProtect, Spotlight/indexing, backup, photo/media analysis, software update patterns (`joulewise/arm_readiness_evidence_t0.py:1317`).
- Process classes: caffeinate; codex/claude/t3; browsers; powermetrics/window-chain/run_campaign/tail/watch (`:1720`). Absence requires exit 1 and empty stripped stdout (`:1312`).
- Machine readiness validates captured preparation/READY evidence and plan/root bindings (`:1684`). The captured prewindow script separately rejects contaminating daemons above 5% CPU and load average above 2 (`scripts/prewindow_check.sh:34`, `:72`).

Workers perturb load and timing; matching agents/processes perturb census. However, these integration fixtures already synthesize census evidence: `install_passing_evidence` (`tests/test_arm_readiness_integration.py:157`) and `passing_probe` returning pgrep absence (`tests/test_arm_readiness_evidence_t0.py:739`). A machine-preflight reason also covers campaign locks (`joulewise/arm_readiness.py:6938`). Therefore the earlier census failures cannot confidently be assigned the same cause.

**(a) Recommended: deterministic observations, real adjudication.** Supply coherent numeric fixture anchors through `_sample_live_clock_anchor`, keeping `_evaluate_rows` and all predicates real. Use `author_environment(probe=…, sample_anchor=…)`, which patches `_execute_probe` and `_production_clock` (`tests/test_arm_readiness_evidence_t0.py:768`). Carry matching anchors into the launch subprocess through the existing fixture bootstrap hook (`:295`). Preserve ordinary monotonic capability deadlines and their separation tests.

`patch_pack_night_dependencies` (`tests/test_arm_readiness.py:159`) currently patches GO T0 authentication and boot identity; it is **not** an existing preflight-result injector. Do not mistake its authentication bypass for the proposed fix.

This still proves receipt derivation, bindings, hashing, row propagation, ARM verification and launch consumption under specified observations. It does not prove live machine readiness. Preserve clock boundary tests (`tests/test_arm_readiness_schemas.py:1269`; `test_arm_readiness_evidence_t0.py:1593`, `:1767`), and require synthetic forbidden/error census cases plus an injected-bad-anchor integration refusal.

**(b) Serialize.** Partition exclusive modules out, await all ordinary workers, then run exclusives sequentially and aggregate every failure/count. Today packing is descending-duration greedy, followed by alphabetical execution within shards (`scripts/shard_tests.py:532`); all workers launch before waiting (`:808–830`). CI separately filters exclusives and runs dedicated jobs (`.github/workflows/ci.yml:64`, `:119`). Local serialization preserves probes but cannot exclude another replay or reviewer, so it is insufficient here.

**(c) Accept/document.** Retain standalone replay requirements temporarily. This preserves production soundness but leaves ambient nondeterminism and recurring verification cost.

**Reviewer refusal criteria:** relaxed thresholds, retries-until-PASS, skipped rows, PASS-returning predicate mocks, production test switches, or claiming synthetic evidence as hardware validation.

**Draft queue row:** `ARM-INTEGRATION-LOAD-01 | [AGENT] | Make ARM/launch integration fixtures deterministic through probe-result seams. | Acceptance: coherent parent/subprocess anchors; real predicates, bindings and deadlines retained; bad clock/census results refuse; focused and four-worker full-suite replays pass under controlled concurrent agent load; no test deletions or production-gate relaxation.`

## Critical path

Lead assigns implementation scope → fixture changes and refusal coverage → lead reviews and verifies. Live validation remains independently gated on machine quiet.