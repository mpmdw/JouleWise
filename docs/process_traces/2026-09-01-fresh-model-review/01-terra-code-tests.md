```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Conditionally fit for the capstone: protect the raw-evidence/anchor path, fix the v5 corner-cap divergence, then stop changing campaign code.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "672b995fd258e0a87e7abd4f9b76f626598e6e39",
    "head_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "upstream_end": "3b3839c0636bfb5e6fe5537178b1929551dac139",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [
    "docs/process_traces/2026-09-01-fresh-model-review/"
  ],
  "verdict": {
    "overall": "Yes, conditionally: the physics/evidence path is unusually defensible, but the code is not readily navigable by a new maintainer and must now be treated as a frozen instrument. The scheduled v5 design has 10 blocks, so it is inside the registered 16-block exact-corner limit, but its separate common-mode replay accepts up to 20 blocks; that inconsistency should be corrected before the transaction. The largest thing to protect is strict re-derivation from raw bundle evidence through the clock-anchor and reducer path. Do not spend the remaining ten days on a broad refactor or another process framework.",
    "biggest_change": "Align the v5 common-mode replay cap with the canonical n=16 cap and add a direct 17-block refusal regression before the campaign.",
    "biggest_protect": "Keep strict raw-to-trace re-reduction and anchor-envelope claim gates intact (joulewise/cli.py:392-412, 542-574; joulewise/reduce.py:2388-2510).",
    "critical_path": [
      "pack source and prospective-manifest validation: configs/campaigns/d117_contrast_v5/generate_configs.py:3174-3263",
      "bundle strict validation and fresh reduction: joulewise/cli.py:392-412, 1819-1826, 1835-1872",
      "clock-anchor correction/envelopes inside reduction: joulewise/reduce.py:2920-2950, 3188-3293",
      "cell-floor extraction: joulewise/floor_extraction.py:2236-2353, 2577-2811",
      "floor mint re-validates bundles strictly: scripts/mint_floor_artifact_generalized.py:4067-4157",
      "outcome-blind finalization binds the verdict, bracket, ledger, and floor: scripts/finalize_analysis_manifest.py:23-83",
      "claim gate consumes strict validation and the floor: joulewise/cli.py:2003-2035; joulewise/analysis_engine/claims.py:257-414"
    ],
    "numeric_checks": [
      "F_cell is correct: max(0.81, 1.04)=1.04, matching max(floor_abs, floor_cmp) in joulewise/detection_floor.py:1620-1640 and the validator at 3862-3874.",
      "g(5)=sqrt(9/4)=1.5 and g(10)=1, matching joulewise/detection_floor.py:104-110, 664-672.",
      "The ratio rule is correct by inspection: 2/1=2 passes and a zero denominator refuses, matching configs/campaigns/d117_contrast_v5/generate_configs.py:591-612 and its regression at tests/test_d117_contrast_v5_pack.py:518-534.",
      "The canonical exact enumeration rejects n>16 (joulewise/detection_floor.py:859-914), but v5 allows n<=20 before enumerating 2*2^n shared/local sign cases (configs/campaigns/d117_contrast_v5/generate_configs.py:683-762)."
    ],
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "rank": 1,
        "when": "change now (pre-campaign)",
        "observation": "The canonical floor code caps exact corners at 16, and extraction applies that cap to common-mode comparative cells, but the v5 R_cm replay refuses only above 20. Evidence: joulewise/detection_floor.py:110, 887-900; joulewise/floor_extraction.py:2766-2797; configs/campaigns/d117_contrast_v5/generate_configs.py:683-762.",
        "why": "The current 10-block design is safe, but two nominally exact implementations disagree on their governed domain. A future or malformed 17-20 block input could produce a replay result where the canonical path refuses.",
        "first_step": "Import/use MAX_EXACT_ADMISSIBLE_CORNER_N in the v5 generator and add a 17-block test that asserts common_mode_replay_block_count_invalid before enumeration.",
        "cost_risk": "Small code/test change, but it changes a pack-generator source that is intended for the campaign; re-run the prescribed pre-freeze regeneration/authentication checks rather than silently patching it."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "rank": 2,
        "when": "change now (pre-campaign), documentation only",
        "observation": "The critical path is sound but spread across very large files: arm_readiness is 12,035 lines, run_campaign 8,921, whole_window 5,929, reduce 4,003, detection_floor 4,415, and the v5 generator 3,420. The actual path requires crossing the files listed above rather than following one operator-facing entry point.",
        "why": "This is an operator-error risk during the G2-a/transaction handoff, not a reason to redesign the instrument. The project has more test source than package source, so another general process document would not help unless it directly names the runnable path.",
        "first_step": "Add one short v5 run-sheet map: exact input artifact, command owner, emitted artifact, and next consumer for bundle validation, reduction, extraction, mint, finalization, and claims.",
        "cost_risk": "Less than a day; the risk is a stale duplicate map, so keep it to links/commands and do not restate policy."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "rank": 3,
        "when": "change after the campaign closes",
        "observation": "CI runs the normal suite across Python 3.11/3.14 and shards it, but its timing narrative is stale: it describes 138 modules and 3,804 tests as of 2026-08-23 (.github/workflows/ci.yml:264-276), while this review's AST inventory found 168 test files and 4,241 declared test methods; 28 current modules have no timing entry. The disabled D117 production-proof workflow also says current-main fixture drift prevents automatic triggering (.github/workflows/d117-production-proof.yml:3-13).",
        "why": "The full suite is still selected by discovery, so this is observability and CI-latency debt, not an omitted-test conclusion. It makes the test wall-clock and the special proof's meaning hard to assess quickly.",
        "first_step": "Capture one successful post-campaign CI timing run; update the timing map and explicitly either repair the legacy D117 proof for a still-live requirement or retire/archive it.",
        "cost_risk": "Do not touch this before collection: it has no bearing on the 10-block v5 design and creates needless churn."
      },
      {
        "id": "F4",
        "severity": "nit",
        "rank": 4,
        "when": "change after the campaign closes; never worth doing pre-campaign",
        "observation": "A name-based inventory finds 2,260 of 4,241 test names (53.3%) signal refusal/integrity checks. That is only a heuristic, but it agrees with the repository's own D-161 ruling that deliberate-operator-only guards should be removed while physics, pre-registration, and plausible operator mistakes remain fail-closed (docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:9-16, 24-35, 53-55).",
        "why": "Some process machinery is over-engineered for the stated threat model, but the rule correctly defers pruning so it cannot destabilize a measurement campaign.",
        "first_step": "After the paper data close, execute the already-registered D-161 prune in small waves and redirect the saved maintenance budget to untested ruled clauses.",
        "cost_risk": "High if attempted now; low-to-moderate afterward if each removal preserves a mistake-catching test."
      }
    ],
    "would_keep": [
      "Strict bundle validation re-reduces raw evidence instead of trusting stored summaries (joulewise/cli.py:392-412, 542-574).",
      "The componentwise floor gate is max, never a sum, and is checked again during artifact validation (joulewise/detection_floor.py:1620-1640, 3862-3874).",
      "G2-a selection is deterministic: exact four-rung ladder, count checks, shortest qualifying rung, and a recorded refusal fallback (scripts/select_g2a_prefill_length.py:16-24, 53-136).",
      "The CI fast tier is explicitly additive rather than a substitute for full testing (.github/workflows/ci.yml:241-276).",
      "D-161's distinction between physics/pre-registration/mistake safeguards and deliberate-only safeguards (docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:9-16)."
    ],
    "anomalies": [
      "Mission M0 still names a 2026-07-08 expectation of skipped=10 (docs/agent_playbook.md:66-70); it is stale as a current verification instruction.",
      "The D117 production-proof workflow is manual-only because of a documented fixture/API drift (.github/workflows/d117-production-proof.yml:3-13).",
      "No unambiguously dead package module was established: joulewise.__main__ is the CLI entry point, and the apparently unimported node_worker is copied and invoked by NodeWorkerClient (joulewise/adapters/node_client.py:1059-1063, 276-285)."
    ],
    "open_questions": [
      "Is n=16 intended to bind the v5 shared-sign R_cm replay as well as the canonical cell-floor path?",
      "Will the v5 generator's replay function be the authoritative paper-fill replayer after collection, or only a generation/test helper?",
      "Does the disabled D117 production-proof workflow cover any acceptance condition still needed for v5?",
      "Can a writable clean checkout or CI run the canonical suite before the transaction?",
      "Is there a post-submission maintenance horizon? If not, I would not recommend module splitting at all."
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2791 tests in 120.085s",
          "FAILED (errors=1787, skipped=112)",
          "FileNotFoundError: [Errno 2] No usable temporary directory found"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran [0-9]+ tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'from joulewise.detection_floor import small_sample_guard_factor; print(small_sample_guard_factor(5), small_sample_guard_factor(10), max(0.81,1.04))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "1.5 1.0 1.04"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1\\.5 1\\.0 1\\.04"
      }
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The read-only sandbox exposes no writable temporary directory, so the canonical suite's 1,787 errors are environment-caused and cannot establish repository test health.",
      "needs": "Run the canonical command in a normal writable clean checkout or inspect the current CI result."
    },
    {
      "id": "BASE1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "main advanced during review from 672b995f to 3b3839c0; the intervening commit changed only README.md and RUN_STATE.md, not the reviewed code/test/CI paths.",
      "needs": ""
    },
    {
      "id": "RISK1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The v5 replay's n=20 domain divergence remains until F1 is resolved.",
      "needs": "Adjudicate the intended cap and re-run focused checks."
    }
  ]
}
```

## Findings

1. **F1 — change now.** The v5 common-mode replay checks every allowed combination of shared and local error signs, but it accepts up to 20 blocks; the canonical exact calculation and extraction gate refuse above 16. The scheduled design has 10 blocks, so this is not evidence of a current wrong result, but two implementations should not disagree about their valid domain. Align the v5 check with the canonical constant and add a direct 17-block refusal test. Sources: `joulewise/detection_floor.py:110,887-900`; `joulewise/floor_extraction.py:2766-2797`; `configs/campaigns/d117_contrast_v5/generate_configs.py:683-762`.

2. **F2 — change now, but only as a concise run map.** The measurement path is defensible but not easy to follow end to end: pack → bundle/strict validation → anchor-aware reduction → floor extraction → mint → outcome-blind finalization → claim gate. It crosses several multi-thousand-line modules, notably `scripts/run_campaign.py`, `joulewise/reduce.py`, and `joulewise/whole_window.py`; a short command-and-artifact map would reduce transaction-night error without adding policy prose. Sources: `joulewise/cli.py:392-412,1819-1872,2003-2035`; `scripts/extract_detection_floors.py:1-16`; `scripts/finalize_analysis_manifest.py:23-83`.

3. **F3 — after collection.** The normal CI design is good—two Python versions, sharded full suite, and an explicitly non-gating fast tier—but its timing data and prose lag the present suite, and the special D117 production-proof workflow is manually triggered because it is known broken. This is worth repairing or retiring after the campaign, not before it. Sources: `.github/workflows/ci.yml:9-104,241-276`; `.github/workflows/d117-production-proof.yml:3-13`.

4. **F4 — after collection only.** The repository really has accumulated more custody/process checks than this threat model needs. The project has already reached the right conclusion: retain checks that catch physics, evidence, pre-registration, or plausible mistakes; prune deliberate-operator-only checks after the campaign. Sources: `docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:9-16,24-35,53-55`.

Keep the strict raw-evidence re-reduction, the componentwise maximum floor, deterministic G2-a selection, and outcome-blind finalization. They are the parts that make a negative or null paper result credible rather than merely well documented.

By hand, the specified numerical points check out: `max(0.81, 1.04) = 1.04`; `g(5)=√(9/4)=1.5` and `g(10)=1`; and `R=2/1=2` passes while a zero denominator refuses. Sources: `joulewise/detection_floor.py:664-672,1620-1640`; `configs/campaigns/d117_contrast_v5/generate_configs.py:591-612`.

## Residual risk

I could not obtain a clean full-suite result because this read-only environment has no usable temporary directory. I did not run hardware, collection, or quiet-Mac commands.