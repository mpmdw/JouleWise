```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All six blocker findings survive; F1/F2 are one producer defect, and F6 also contains an uncovered production-path join failure.",
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
        "summary": "The required private T-0 input namespace has no shipped producer or operator step."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "Independent filename, schema, field, and script-inventory searches found only test-fixture writers; consolidate with F1."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "A clean prewindow wait can finish after about 60 seconds, while the author requires a 600-second captured duration."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The author requires fresh passwordless systemsetup access after the idle, while the installed D-004 rule covers powermetrics only."
      },
      {
        "id": "F5",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The FINAL standalone packet goes directly from E-9 to arm and predates the current T-0 authoring step."
      },
      {
        "id": "F6",
        "severity": "blocker",
        "verdict": "CONFIRMED",
        "summary": "The runbook env/chain templates violate the author contract; a separate doubled production-plan path also guarantees refusal."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -l 'started_monotonic_ns|finished_monotonic_ns|clock-attestation\\.json|launch-manifest\\.json|arm_readiness\\.t0\\.inputs' scripts joulewise configs docs/phase_2 tests | sort",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/arm_readiness_evidence_t0.py",
          "tests/test_arm_readiness_evidence_t0.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_arm_readiness_evidence_t0.py"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -c 'from pathlib import Path; from types import SimpleNamespace; import joulewise.arm_readiness_evidence_t0 as m; c=SimpleNamespace(custody_pack_root=Path(\"/tmp/jw-refuter-absent/d117_floor_qwen25_1p5b_v1\"),values={});\\ntry: m._clock_attestation(c,kind=\"CLOCK_ATTESTATION\")\\nexcept m.T0EvidenceAuthoringError as e: print(e.kind,e.reason_code,str(e),sep=\" | \")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CLOCK_ATTESTATION | evidence_author_t0_clock_attestation_missing | independent-clock attestation is unreadable: /tmp/jw-refuter-absent/d117_floor_qwen25_1p5b_v1/arm_readiness.t0.inputs/clock-attestation.json: [Errno 2] No such file or directory"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "evidence_author_t0_clock_attestation_missing"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import re,pathlib; s=pathlib.Path(\"scripts/prewindow_check.sh\").read_text(); n=int(re.search(r\"^SETTLE_CHECKS=(\\\\d+)\",s,re.M).group(1)); d=int(re.search(r\"^INTERVAL_S=(\\\\d+)\",s,re.M).group(1)); import joulewise.arm_readiness_evidence_t0 as m; print({\"clean_exit_lower_bound_s\":(n-1)*d,\"author_min_idle_s\":m._MIN_IDLE_NS//1_000_000_000,\"gap_s\":m._MIN_IDLE_NS//1_000_000_000-(n-1)*d})'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{'clean_exit_lower_bound_s': 60, 'author_min_idle_s': 600, 'gap_s': 540}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "'gap_s': 540"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -c 'import pathlib; import joulewise.arm_readiness_evidence_t0 as m; p=pathlib.Path(\"docs/phase_2/window_runbook.md\"); lines=p.read_text().splitlines(); raw=(\"\\\\n\".join(lines[183:206])+\"\\\\n\").encode(); print(m._parse_shell_assignments(raw, kind=\"LAUNCH_RECIPE\"))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: window.env value for PACK_ROOT is ambiguous"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "PACK_ROOT is ambiguous"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; from joulewise import arm_readiness as r; root=Path(\"configs/campaigns/d117_floor_qwen25_1p5b_v1\").resolve(); tree,_=r._plan_tree(root); expected=root/str(tree[\"plan\"][\"path\"]); actual=root/Path(str(tree[\"plan\"][\"path\"])).name; print(\"author_expected=\",expected); print(\"actual_pack_plan=\",actual); print(\"author_expected_exists=\",expected.exists()); print(\"actual_exists=\",actual.exists())'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "author_expected_exists= False",
          "actual_exists= True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "author_expected_exists= False\\nactual_exists= True"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD is a descendant of the requested baseline; post-baseline paths are README.md, RUN_STATE.md, and the baseline manifest. The reviewed runbook hash still matches the manifest.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox denied temporary-directory creation and execution of sudo, so the full author CLI and live sudo capability could not be replayed; pure negative probes and source/contract inspection establish the reviewed defects.",
      "needs": "Lead may replay the full CLI and sudo -n capability check outside the sandbox before implementing."
    }
  ]
}
```

## Findings

### F1 — CONFIRMED (blocker)

The obligation is real, although the nine private filenames are implementation preconditions rather than names prescribed by D-134. D-134 requires missing live evidence to REFUSE, requires verdicts and bindings to be derived, and allows operators to provide only paths and irreducible attestations (`docs/decision_log.md:8603-8636`). The runbook then makes the T-0 author mandatory immediately after E-9 (`docs/phase_2/window_runbook.md:802-838`).

The author requires `arm_readiness.t0.inputs` plus six captures, a clock attestation, arm context, and launch manifest (`joulewise/arm_readiness_evidence_t0.py:38-50,132-202,448-520,550-620`). Its public CLI accepts only pack and custody roots (`scripts/author_arm_evidence_t0.py:23-27`), so it cannot create those prerequisites.

Independent searches:

- `rg -l 'started_monotonic_ns|finished_monotonic_ns|clock-attestation\.json|launch-manifest\.json|arm_readiness\.t0\.inputs' scripts joulewise configs docs/phase_2 tests | sort` returned only the author and its test.
- `rg -n 'arm_readiness\.t0\.inputs' docs/phase_2/window_runbook.md` returned no match.
- The direct missing-input probe produced `evidence_author_t0_clock_attestation_missing`.

Severity is correctly blocker. The sound remedy is a shipped acquisition tool that executes/captures E-4…E-9, derives boot and monotonic values, builds context/launch inputs from frozen bytes, and accepts only the irreducible clock observation from Ed. Document its exact invocation before the author step.

### F2 — CONFIRMED (blocker; duplicate of F1)

A filename-oriented search found writers for all nine inputs only in `tests/test_arm_readiness_evidence_t0.py:356-545`. Production code only reads them (`joulewise/arm_readiness_evidence_t0.py:448-620`). Exact searches for all three private schemas found them only in the author itself.

The test fixture demonstrates what the absent producer must do: create the input namespace, construct canonical context and launch objects, and wrap every command with boot-bound start/finish monotonic timestamps. That fixture is not shipped operator machinery.

Severity is correct, but this should not generate a second work order. Merge F2 into F1. Merely documenting hand-authored JSON would violate D-134’s derive-never-enter intent and would leave the fabricated-duration problem intact.

### F3 — CONFIRMED (blocker)

The runbook requires at least ten untouched minutes and says the frozen `prewindow_check.sh --wait` invocation fulfills it (`docs/phase_2/window_runbook.md:366-373,780-789`). The author independently enforces a 600-second command-capture duration (`joulewise/arm_readiness_evidence_t0.py:49,946-959`).

But the script uses three clean checks separated by 30 seconds (`scripts/prewindow_check.sh:29-37,177-198`). On a clean machine, checks occur near 0, 30, and 60 seconds, then return READY. The arithmetic probe reported:

`{'clean_exit_lower_bound_s': 60, 'author_min_idle_s': 600, 'gap_s': 540}`

Thus the runbook’s assertion that the command fulfills the idle is false, and the author correctly refuses the short capture. Severity is blocker. The remedy should make the wait enforce a minimum ten-minute dwell while continuing its checks; lowering the author threshold would defeat the contamination control.

### F4 — CONFIRMED (blocker)

D-004’s accepted and installed privilege is exactly `/usr/bin/powermetrics` (`docs/decision_log.md:297-329`; `docs/phase_1/phase_1_exit_checklist.md:285-291`). The runbook acknowledges that `systemsetup` needs administrator rights (`docs/phase_2/window_runbook.md:509-540`).

The author nevertheless performs a fresh:

`/usr/bin/sudo -n /usr/sbin/systemsetup -getusingnetworktime`

at authoring time and refuses nonzero output (`joulewise/arm_readiness_evidence_t0.py:884-903`). Because E-7b must itself span ten minutes, a normal cached interactive timestamp is not a governed capability. `prewindow_check.sh:98-109` has the same problem but merely warns when it cannot read the state.

D-127 already defines the sound remedy: an exact-path, exact-argv sudoers authorization for the two network-time commands (`docs/decision_log.md:8154-8178`). It is chartered but not implemented or installed in this baseline. Severity is therefore blocker. Land and deliberately install that narrow route; do not depend on cached sudo state or weaken the fresh probe.

### F5 — CONFIRMED (blocker)

The packet explicitly says it is executable without the runbook (`arm-packet-alpha-FINAL-20260813.md:439-444`). Its night sequence runs E-9 and then E-9a `generate_arm_readiness.py arm` (`:463-482`), with no T-0 authoring command. It still says “no shipped authoring route” (`:151-193,529-532`).

The packet binds tree `49dcc49a` from 2026-08-13; the author landed in `ac3fe1d` on 2026-08-14. Current runbook lines 802-838 now require author → arm → verify → consume. D-134 clause 9 expressly required the operator packet’s ARM sequence to be amended (`docs/decision_log.md:8624-8628`).

Severity is blocker. Issue a reviewed successor packet from the corrected current sequence; preserve this packet as historical custody rather than silently editing it.

### F6 — CONFIRMED (blocker)

All four stated mismatches reproduce:

- The runbook example contains `$` expansions (`docs/phase_2/window_runbook.md:181-206`); the author rejects any parsed value containing `$` (`joulewise/arm_readiness_evidence_t0.py:571-592`). Direct parsing refused `PACK_ROOT is ambiguous`.
- The example omits `CUSTODY_ROOT`, `CLAIM_BACKUP_DEST`, and `BOUND_BACKUP_DEST`, using `WINDOW_CUSTODY_ROOT` and one `BACKUP_DEST` instead. The author requires the former exact bindings (`:652-666`).
- The runbook’s external `FROZEN_PLAN` and E-8 template (`docs/phase_2/window_runbook.md:917-950`) conflict with the author’s exact diagnostic plan-path check (`joulewise/arm_readiness_evidence_t0.py:1121-1155`).
- The chain template uses `REPO="${MEASUREMENT_REPO:-…}"` (`docs/phase_2/window_runbook.md:964-973`), while the author requires one literal resolved repository binding (`joulewise/arm_readiness_evidence_t0.py:668-676`).

There is also an additional production-only failure: `plan_tree.json` stores `configs/campaigns/.../calibration_plan.json`, but author line 1149 joins that repository-relative path to `pack_root`, yielding `pack_root/configs/campaigns/.../calibration_plan.json`. The probe showed that doubled path does not exist while `pack_root/calibration_plan.json` does. The synthetic test uses only `"calibration_plan.json"` (`tests/test_arm_readiness_evidence_t0.py:151`), so it misses this defect.

Severity is blocker. The remedy should establish one generated freeze artifact contract for `window.env`, launch manifest, chain, and plan path, then exercise it against a real production pack. The intended meaning of `FROZEN_PLAN` must be ruled before blindly changing either prose or parser.

All six findings survive; none is refuted. F1/F2 collapse to one defect. The minimal true work-order set is: (1) ship the T-0 acquisition/capture producer and exact operator step; (2) repair the ten-minute wait and land/install D-127’s narrow `systemsetup` privilege route; (3) reconcile/generated-test the env, chain, manifest, and frozen-plan contract—including the doubled production path; and (4) issue a successor FINAL packet only after those mechanics pass end-to-end.

## Residual risk

The sandbox prohibited temporary-directory creation, so the full author CLI stopped at its internal boot-probe staging before reaching the missing input; the lower-level production function reproduced the exact missing-attestation refusal. It also prohibited executing `sudo`, so installed host capability was established from the accepted decision/checklist and shipped sudoers artifacts, not a live `sudo -n` probe. I did not run the real ten-minute quiet gate because this agent session itself violates its no-agent operating condition; its clean-path timing follows directly from the loop’s three checks and two 30-second sleeps.