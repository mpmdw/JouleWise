```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HOLD OPEN: marker-free manual claim-bearing collection bypasses H1; downstream consumers also lack an independent hold check, although the synthetic fresh-bracket probe refused on corpus doubling.",
  "workspace": {
    "base_requested": "325d9f77",
    "base_mode": "exact",
    "head_start": "325d9f77b3ffb73fd0dd0f876f3ce59d567a092b",
    "head_end": "325d9f77b3ffb73fd0dd0f876f3ce59d567a092b",
    "upstream_end": "9eab16f81783c9cf079474c38d10c4a5bdf0f118",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "hold": "OPEN",
    "open_route_count": 1,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Manual claim-bearing collection bypasses pack admission",
        "locations": [
          "scripts/run_campaign.py:1866",
          "scripts/run_campaign.py:8091",
          "scripts/run_campaign.py:8738",
          "joulewise/arm_readiness.py:11445"
        ]
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Claim consumers lack an independent H1 check; freshness refusal is not hold enforcement",
        "locations": [
          "joulewise/calibration_bracketing.py:1245",
          "joulewise/calibration_bracketing.py:2024",
          "joulewise/whole_window.py:693",
          "joulewise/analysis_engine/inputs.py:3123",
          "scripts/mint_floor_artifact_generalized.py:2219"
        ]
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t1_new_issuance_is_held_at_arm tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t2_r7_stays_admitted tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t3_registry_and_admission_sets_match",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.001s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-holdref-d528efb2/probe_entrypoints.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "claim_bearing_policy=true; marker_free_campaign_preflight=allowed_without_lineage",
          "held_level_screen_s=0.038078579302948",
          "held_allowance_s=0.013701",
          "admission_calls=0; hardware_calls=0; git_writes=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "admission_calls=0; hardware_calls=0; git_writes=0"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-holdref-d528efb2/probe_hold.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["fresh_pair_refused_by_corpus_doubling_not_H1"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "fresh_pair_refused_by_corpus_doubling_not_H1"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["325d9f77b3ffb73fd0dd0f876f3ce59d567a092b"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^325d9f77b3ffb73fd0dd0f876f3ce59d567a092b\\s*$"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Design ruling section 9 step 6 requires the issuing transaction to stop on the manual collection bypass.",
      "needs": "Close F1 and repeat the hold refutation before issuance."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No hardware collection or successful end-to-end held-calibration verdict, floor mint, or claim artifact was executed. Downstream conclusions distinguish static missing checks from demonstrated admission.",
      "needs": ""
    }
  ]
}
```

HOLD: OPEN — 1 route(s)

The count groups manual campaign, benchmark, and experiment entry points as one collection-admission bypass. It does **not** count downstream paths as independently demonstrated successful claims.

| Route | Admission-list / H1 coverage | Finding or boundary |
|---|---|---|
| Pack evidence author → arm receipt → `run_night.py` transaction | **Yes.** `arm_readiness.py:6209`, `arm_readiness_evidence.py:2626`; required successor evidence refuses at `arm_readiness_evidence.py:979`. Night arm calls it at `run_night.py:1982`. | Protected for a pack naming the held ID. V1 passes all three H tests. |
| Manual `run_campaign.py` with production claim-bearing policy and unmarked configs | **No.** `run_campaign.py:1866` returns without launch authentication when no config has the marker; `arm_readiness.py:11445` determines that solely from tags. Collection reaches the child-launch call at `run_campaign.py:8738`. | **OPEN, F1.** V2 verifies the skipped admission boundary with a checked-in production config and `quiet_mac_p2_production.json`, whose `claim_bearing` is true at line 33. |
| Direct benchmark / experiment CLI | **No independent H1 check.** `cli.py:370` → `controller.py:238`; experiments reach the same runner at `controller.py:2916`. | Same F1 collection family. Supplying no instrument attachment returns normally at `controller.py:376`. |
| Ordinary calibration capture’s level-screen calculation | **No.** `validate_powermetrics_fiducial.py:372` authenticates bytes, epoch and estimator pins; the ordinary capture branch uses it at line 2134. | V2 derives **0.038078579302948** from the held default. Calibration evidence alone is not a claim, but this does not prevent F1’s claim collection. |
| Bracket evaluation using S, C and level screen | **No H1 check.** Default loads at `calibration_bracketing.py:2074`; arithmetic at line 2579; successful return at line 2679. | F2. **V3 refused**, independently, on corpus doubling. No successful bracket claimed here. |
| Whole-window verdict CLI | **No independent H1 check.** `run_campaign.py:6171` → bracket evaluation at line 5257 → verdict publication at line 6422. | Inherits bracket refusal. `core_passed` requires no conditions at line 6335; the observed freshness failure therefore cannot establish a positive verdict. |
| Whole-window authenticated consumption | **No independent H1 check.** Default loads at `whole_window.py:508`; bracket evaluation at line 693. | Current bracket route inherits V3’s barrier. The legacy minted-summary branch at line 680 can bypass bracket recomputation, but reading an old summary alone does not demonstrate use of the new numbers. |
| Floor extraction | **Conditional lineage authentication, no H1 check.** `floor_extraction.py:2829` creates a consumption session at line 2870 and requires whole-window evidence at line 3135. | Inherits whole-window checks; no successful held-calibration extraction demonstrated. |
| Original mint and generalized v1 mint | **No independent H1 check.** `mint_floor_artifact.py:2036` loads the default, authenticates components, rebinds, and writes at line 2108. Generalized entry is `mint_floor_artifact_generalized.py:1769`. | Depends on component/verdict authentication. Not an independently proven successful bypass. |
| Generalized v2 mint / allowance projection | **No H1 check.** Explicit acceptance authentication at `mint_floor_artifact_generalized.py:3596`; allowance projection at line 2219; estimator selection at `floor_mint_estimator.py:156`. | V2 accepts the held artifact and derives **S = 0.013701**. Full mint additionally requires authenticated components, bindings and reviewed pins; not executed. |
| Analysis loader → claim verdict artifact | **No independent H1 check.** `analysis_engine/inputs.py:3123` loads the default; consumption session at line 3274. `analysis_engine/__init__.py:1684` loads inputs and publishes at line 1887. | Inherits floor and whole-window checks. No successful held-calibration claim artifact demonstrated. |
| Claim validators, sidecar and paper renderer | **No H1 check.** `analysis_engine/artifact.py:981`, `claim_side_bound.py:158`, `paper_custody.py:597`, `paper_rendering.py:68`. | These validate or render upstream evidence; they do not independently withdraw held calibration authority. F2 downstream coverage. |
| Bracket binding / analysis finalization | **No H1 check, but no numerical claim itself.** `build_bracket_binding.py:494` authenticates ledger/session custody and publishes the binding at line 545. | Binding is an input to later verdict checks, not permission to claim. |
| Diagnostic no-pack / derivation nights | Admission list intentionally skipped: `night_gate.py:624`, `run_night.py:3057`. | **Non-claim lane.** The derivation chain explicitly excludes claim output at `night_chains/calibration_derivation_only.zsh:11`; derivation observations are excluded from claim endpoint discovery at `calibration_bracketing.py:1896`. |
| Rehearsal / mock | Separate restrictions: `night_gate.py:995`, `run_night.py:2142`; mock claim refusals at `analysis_engine/inputs.py:2842` and `floor_extraction.py:1985`. | **Non-claim by construction.** |
| HTML report / phase-share analysis | `report.py:431` labels every report diagnostic; `analyze_phase_share.py:164` emits `diagnostic_non_claim_bearing`. | **Non-claim by construction.** |
| Issuance, continuation, equivalence and probe-generation utilities | Acceptance readers include `issue_calibration_acceptance_generation.py:393`, `issue_epoch_continuation.py:75`, `epoch_equivalence_check.py:208`, `generate_g2a_probe_inputs.py:667`. | Calibration/governance or preparation outputs, not measurement claims. Generated collection still needs F1’s boundary closed. `sim_acc_25g83_rev5.py:227` explicitly reads retained R7. |

## Findings

**F1 — BLOCKER: manual claim-bearing collection bypasses H1.**

The guard protects packs that name the held calibration. A manual campaign can instead select the production claim-bearing policy and ordinary configs without `launch_lineage_required`. Its collection preflight returns `None`, and the campaign continues toward launching measurement children without consulting `_issued_d079`.

The issued file also passes the ordinary level-screen derivation at 25G83. V2 installs a tripwire on `_issued_d079`: campaign launch-authentication preflight, level-screen derivation, and mint allowance projection all complete without touching it.

This establishes the missing **claim-window admission gate**, which the charge explicitly includes. It does not establish successful measurement or publication: no child was launched, no hardware was accessed, and no battery was read.

**Required next step:** stop the issuing transaction and close the manual claim-collection boundary. Preserve an explicit non-claim path for diagnostic captures.

**F2 — SHOULD-FIX: downstream consumers have no independent H1 enforcement.**

The hold table is consumed only through arm-readiness applicability. Authenticating the issued bytes or obtaining registered operatives does not check it. Whole-window evaluation, minting, analysis and rendering therefore rely on upstream admission or unrelated validation failures.

A material counterexample to overstating the evidence: the authentic issued prefix contains **23 valid 25G83 observations**, although its derivation corpus is 12. V3 constructs that prefix and two synthetic ordinary endpoints without patching the acceptance loader, numeric rules or hold. Evaluation returns:

- Pack admission: `false`.
- Acceptance artifact `claim_eligible`: `true`.
- Bracket status: `failed`.
- Reason: `calibration_acceptance_bound_stale`.
- Trigger: `corpus_doubles_from_12_to_24`.
- Operative bound: `null`.

That is a real refusal, **not a successful claim bypass**. It is also not H1 enforcement. Add a purpose-aware hold check at claim consumption so safety does not depend on this separate freshness condition.

**NIT:** None.

## Residual risk

This was a read-only source census with bounded synthetic probes, not hardware validation or a complete synthetic campaign-to-publication replay. The full suite was not run; only the three relevant hold tests were executed.

Repository files remained unchanged and the tree remained clean. Replay scripts and the bracket result are under `/tmp/d138-holdref-d528efb2/`.