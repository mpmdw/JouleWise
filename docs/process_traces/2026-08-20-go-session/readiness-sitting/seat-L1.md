```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "L1 is NOT-READY: Phase-2 is merged, but the ruled _v3 fuse lapse, dead baseline manifest, open stable ED replay, and missing coverage prevent clearance.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "exact",
    "head_start": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "head_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "upstream_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "component": "L1-AUTHORITY-PLANE",
    "result": "NOT-READY",
    "coverage": "40/42 independently enumerated authority checks completed; 2 production-Mac verify groups remain unexecuted",
    "ed_rows": {
      "ED-QUAL-L1-1": "UNVERIFIED",
      "ED-QUAL-L1-2": "CLOSED capability evidence, not current arm authority"
    },
    "findings": [
      {
        "id": "L1-F1",
        "severity": "blocker",
        "disposition": "STILL-OPEN",
        "text": "_v3 uses legacy 24-hour generic evidence; the final D-148.5 ruling requires LAPSE and a _v4 re-freeze with registry installation."
      },
      {
        "id": "L1-BASELINE",
        "severity": "blocker",
        "disposition": "STILL-OPEN",
        "text": "The sole baseline manifest remains at ac3fe1d and all three pinned _v1 pack digests now mismatch."
      },
      {
        "id": "L1-COVERAGE",
        "severity": "blocker",
        "disposition": "UNVERIFIED",
        "text": "No sealed independent L1 re-enumeration or adversarial coverage artifact exists at the current head."
      },
      {
        "id": "L1-ED1",
        "severity": "blocker",
        "disposition": "UNVERIFIED",
        "text": "The required production-Mac generate_arm_readiness verify and project_identity_pins verify positives were not located or executable here."
      },
      {
        "id": "L1-F4",
        "severity": "should_fix",
        "disposition": "STILL-OPEN",
        "text": "D-118 still asserts mechanical gate-ledger enforcement, but no checker exists in scripts or workflows."
      },
      {
        "id": "L1-F5",
        "severity": "should_fix",
        "disposition": "STILL-OPEN",
        "text": "The kernel remains dated 2026-08-19 at a 2026-08-20 head, and its validator accepts a stale date."
      },
      {
        "id": "L1-F6",
        "severity": "should_fix",
        "disposition": "STILL-OPEN",
        "text": "FREEZE-FCM01 still prohibits pack registration while the active _v3 calibration files register the estimator."
      },
      {
        "id": "L1-F8",
        "severity": "nit",
        "disposition": "STILL-OPEN",
        "text": "Invariant 8 still accepts a textual D-041 mention and still names retired P2-006."
      },
      {
        "id": "L1-NF1",
        "severity": "should_fix",
        "disposition": "STILL-OPEN",
        "text": "D-149 requires mechanical T-0 GO conditions, while WO-D149-GO-EVALUATOR remains hand-written and says the issuer follows the template manually."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD main origin/main && git log --oneline -3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5bd7acf Merge pull request #160 from mpmdw/integration/phase2-transaction",
          "bfc3236 Merge impl/r2-s0-mint-resolver: the executed D-146/D-147 transaction (S0-S5), gate-authorized"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5bd7acf.*Phase-2"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/gen_state.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..........................................................................................................................................."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check --preserve-current-frozen-bytes",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "verified d117_floor_qwen25_1p5b_v3 frozen by d134 receipt: 100 science configs; calibration_plan_sha256=9ab4776f3c416284d6d01a5a49587eedcdfbcb8ef61428cdc1046e9b9d74a072; plan_tree_sha256=2b3fefc8e04c32b29b26c720643c5b2b842f332ff3e2bfbeaf4aa7adf1b954a7"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "verified d117_floor_qwen25_1p5b_v3 frozen.*"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "generation failed: the current frozen identity requires preserve mode"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "generation failed: the current frozen identity requires preserve mode"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The manifest is not superseded and its three _v1 digests fail recomputation at merged main.",
      "needs": "Create the ruled SUPERSESSION, then conduct the focused re-audit against its fixed head."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "ED-QUAL-L1-1 requires real-model, production-Mac verify commands; no positive receipt was located.",
      "needs": "After the compelled _v4 mint, execute and custody both verify paths for every pack."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The final D-148.5 ruling orders the _v3 fuse to lapse; _v3 armability cannot support this sitting.",
      "needs": "Complete the ruled _v4 transaction and its required independent reviews."
    }
  ]
}
```

## Findings

Verdict: **NOT-READY**.

Evidence universe: **40/42**. I independently enumerated head/merge state (3), `_v3` receipt/freeze/projection/generator controls (12), lifecycle registry and final rulings (5), gate/queue controls (6), F4–F8 controls (6), baseline controls (5), and ED/re-audit/form controls (5). The two unexecuted items are the production-Mac positive `generate_arm_readiness.py verify` and `project_identity_pins.py verify` groups.

- **F1 / B1 — STILL-OPEN, blocker.** The `_v3` receipt groups are present and structurally valid, but all are legacy generic v1 evidence with the unchanged 24-hour horizon ([arm_readiness_evidence.py:42](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/joulewise/arm_readiness_evidence.py:42), [arm_readiness.py:6240](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/joulewise/arm_readiness.py:6240)). The final ruling expressly orders the fuse to lapse and compels `_v4` with registry installation ([MAGISTRATE-RULING.md:23](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING.md:23), [MAGISTRATE-RULING-r2.md:74](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/docs/process_traces/2026-08-20-go-session/MAGISTRATE-RULING-r2.md:74)). The sandbox monotonic comparison was not a production-Mac observation and cannot countermand that ruling.

- **F2 / B2 — READY.** `WINDOW-COUNCIL-GATE` is on merged main, allows no quiet-Mac task IDs, and requires this exact council form ([state_kernel.json:2](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/docs/process/state_kernel.json:2)). `gen_state --check` passed and the selector returned no quiet-Mac task.

- **F3 / B3 — READY for the original finding.** The named historical WOs are explicitly completed records rather than selectable work; the originally false kernel rows are gone. I adopt the sibling assembly’s narrow disposition. The newer D-149 manual evaluator is a separate current authority-plane should-fix, not a resurrection of B3.

- **F4 / S1 — STILL-OPEN.** No ledger enforcement appeared in `.github/` or `scripts/`, while D-118 still promises mechanical enforcement.

- **F5 / S2 — STILL-OPEN.** The kernel says `updated: 2026-08-19` at a 2026-08-20 head ([state_kernel.json:3425](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/docs/process/state_kernel.json:3425)). An in-memory stale-date falsifier passed validation; the validator checks only format ([gen_state.py:216](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/scripts/gen_state.py:216)).

- **F6 / S3 — STILL-OPEN.** `FREEZE-FCM01.md` still forbids registering in any pack ([FREEZE-FCM01.md:5](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/FREEZE-FCM01.md:5)); the active `_v3` pack registers that estimator.

- **F7 / N1 — READY for successor scope.** `_v3` uses `as_generated_pre_d134_freeze`, and D-140 supplies the successor semantic authority. The preserved `_v1` descriptive bytes do not govern the successor family.

- **F8 / N2 — STILL-OPEN, nit.** The falsifier with a non-authoritative label containing “D-041” passed, matching the substring implementation ([gen_state.py:368](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/scripts/gen_state.py:368)).

- **Baseline / coverage — blockers.** The sole manifest remains at `ac3fe1d` with `_v1` digests ([audit-baseline-manifest.json:20](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtRC1/docs/process/audit-baseline-manifest.json:20)); all three recomputed mismatched. No current sealed L1 re-enumeration or adversarial coverage artifact was found.

ED status: **ED-QUAL-L1-1 = UNVERIFIED**; the required production positive replays have no located receipt. **ED-QUAL-L1-2 = CLOSED as a historical capability demonstration**: its production evidence and mints are now on main, but that does not make the lapsed `_v3` family armable.

Sibling adjudication: both assemblies’ “branch-only / P-13 open” claims are cured by `5bd7acf` and its parent `bfc3236`. Their `_v3` headroom claim is superseded by the final LAPSE ruling. I adopt the sibling’s F3 and F7 conclusions, but retain F5 open because the merged 2026-08-20 head has already made its freshness metadata stale.

Single strongest reason: the final D-148.5 ruling requires `_v3` to lapse and a fresh `_v4` re-freeze; no READY verdict may treat a deliberately retired armability window as live.

## Residual risk

The production-Mac model bytes and off-repo custody were unavailable here. Even a later positive replay must be against the future `_v4` family, not `_v3`.