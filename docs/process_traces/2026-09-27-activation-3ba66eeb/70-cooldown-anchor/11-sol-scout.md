```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Stored cooldown anchors and full cooldown notes can carry an unchecked baseline across campaigns; the real-window pre-check refused four stored anchors.",
  "workspace": {
    "base_requested": "315364b2",
    "base_mode": "exact",
    "head_start": "315364b2087ce413cc6c36347970838398796157",
    "head_end": "315364b2087ce413cc6c36347970838398796157",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "BFGS-COOLDOWN-ANCHOR-01",
        "action": "needs_ruling",
        "wait_for": "Cold gate decides freezing-refusal behavior, source-location field, and anchor format version before implementation.",
        "collision_surface": "scripts/run_campaign.py, joulewise/cooldown_anchor.py, and possibly joulewise/controller.py"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cg_samesig_err/f1_probe.py /Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb /tmp/anchor-scout-3ba66eeb/f1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "[4] prior_campaign_cooldown_anchor -> ('C', 9.99)",
          "[5/charging_anchor] cooldown note: result=recovered reference_selection=frozen_clean_anchor reference_power_w=9.99 effective_upper_w=10.989 waited_s=30.0",
          "[6/charging_anchor] cooldown reasons in _member_readiness_reasons: []"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "prior_campaign_cooldown_anchor -> \\('C', 9\\.99\\)"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/anchor-scout-3ba66eeb/trace_candidates.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "anchor mismatched: None",
          "anchor None id: C",
          "command child anchor: C 9.99",
          "note id probe-manifest-1 : [('C', 'first_run_exempt', 9.99, 'C')]",
          "note id other-manifest : []",
          "note id None : [('C', 'first_run_exempt', 9.99, 'C')]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "note id None : \\[\\('C', 'first_run_exempt', 9\\.99, 'C'\\)\\]"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/cg_samesig_err/anchor_precheck.py /Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb /Users/edr/code/JouleWise/runs_window_a10_20260725",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "campaign-20260725T105217765514Z-p90436.json: anchor neg8-window-start-r1: WindowBatteryRefusal: window battery refusal: neg8-window-start-r1: battery_float_evidence_missing (prospective bundle): REFUSE",
          "campaign-20260725T110644340763Z-p90873.json: anchor neg8-window-start-r1: WindowBatteryRefusal: window battery refusal: neg8-window-start-r1: battery_float_evidence_missing (prospective bundle): REFUSE",
          "campaign-20260725T124126327980Z-p94224.json: anchor neg8-window-start-r1: WindowBatteryRefusal: window battery refusal: neg8-window-start-r1: battery_float_evidence_missing (prospective bundle): REFUSE",
          "campaign-20260725T124638394354Z-p94367.json: anchor neg8-window-start-r1: WindowBatteryRefusal: window battery refusal: neg8-window-start-r1: battery_float_evidence_missing (prospective bundle): REFUSE",
          "manifests: 4 anchors refused: 4"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "manifests: 4 anchors refused: 4"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "315364b2087ce413cc6c36347970838398796157"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "315364b2087ce413cc6c36347970838398796157"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The ruling leaves three implementation choices to this lane's cold gate: action on refusal at freezing, source-bundle location, and anchor format version.",
      "needs": "Adjudicate the recommendations below before code is written."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The exact interim pre-check exited 1 on a real historical window: four anchors had battery_float_evidence_missing.",
      "needs": "Do not treat that runs directory as passing the pre-check for a scored campaign."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The two-campaign command-line route and RCA-4 through RCA-6 remain unexecuted; the scout used production functions with scratch bundles and did not change production code.",
      "needs": "Exercise those rows during implementation."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| BFGS-COOLDOWN-ANCHOR-01 | needs_ruling | Cold gate resolves the three choices below; implement and run RCA-1 through RCA-6; merge before the next scored campaign | Campaign anchor and note paths in `scripts/run_campaign.py`, shared anchor validation, and the child experiment path |

## Reader inventory

The line references below are on detached head `315364b2`. A *stored note* means a `preceding_campaign_cooldown` record in campaign provenance. Campaign provenance authentication checks the recorded file bytes; it does not battery-gate the bundle named inside an anchor.

| Reader and site | Energy-class value that passes | Gate today? |
|---|---|---|
| [`prior_campaign_cooldown_anchor`, scripts/run_campaign.py:4048](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:4048), reading `cooldown_anchor` at `:4065`; called at `:7408` and `:8350` | Entire anchor, including `baseline.power_w_mean` | **No.** It checks anchor shape and policy digest. With a supplied manifest ID it filters mismatches; with `None` it skips that filter. The scratch probe returned `C` at 9.99 W for both a matching ID and `None`, and returned `None` for a different ID. |
| `run_axi_spec_campaign` at `:7411`, `:7612`, `:7817`; `run_campaign` at `:8430`, `:8798`, `:8900` | Copies the stored anchor into new provenance or passes it to cooldown measurement | **No source-bundle gate before reuse.** The final window gates at `:7848` and `:9032` cover that campaign’s members, which need not include the earlier anchor bundle. |
| [`command_for`, scripts/run_campaign.py:1543](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:1543), called with the anchor at `:8569` for configurations with multiple repetitions | JSON command argument contains the full anchor and 9.99 W baseline | **No.** Executed probe decoded the child argument as `C`, 9.99 W. |
| [`joulewise/cli.py:306–338`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/joulewise/cli.py:306) and [`joulewise/controller.py:2928–2957`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/joulewise/controller.py:2928) | Child accepts and stores the forwarded anchor; `_cooldown_between_reps` at `controller.py:3100–3107` can use its baseline | **Semantic eligibility only; no gate on the anchor’s source bundle.** |
| [`campaign_cooldown_before_member`, scripts/run_campaign.py:4126–4146](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:4126) | Places the full anchor in `anchor_provenance` and, when the preceding baseline is ineligible, converts its baseline into the cooldown reference | **No.** The executed charging-bundle probe yielded `recovered` at a 9.99 W reference. |
| [`prior_campaign_cooldown_evidence`, scripts/run_campaign.py:3725](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:3725), reading physical notes at `:3762` and top-level notes at `:3789`; called at `:7898`, `:8021`, `:8345` | Returns the **whole note**, so `reference_power_w` and nested `anchor_provenance.baseline` survive. It validates first-run exemption identity, but does not strip energy fields or gate their source. The scratch note probe returned both 9.99 W and `C`; a mismatched manifest ID returned no note, while `None` accepted it. The probe’s added first-run note was synthetic; the full-note pass-through is the demonstrated property. |
| `run_campaign.py:7917–7926` | Reads a recovered note’s `result` and raw-trace verification for AXI continuity; no reference-power field is used there | **Raw cooldown trace checked; anchor source not gated.** |
| `run_campaign.py:2924–2928`, `:8034–8038`, `:8587`, `:8713`, `:8880` | Passes prior notes into `evaluate_member`; `:2908` stores the whole note on the evaluation | **No gate at attachment.** `_member_readiness_reasons` at `:6649–6664` uses result and raw-trace verification, while `MemberEvaluation.to_log()` at `:522–523` copies the whole note into logs and the member verdict row (`:6987`). |
| `run_campaign.py:3856–3899` | Reads child experiment cooldown rows, copies their full notes, and carries them into campaign provenance | **No anchor-source gate in this conversion.** |
| [`joulewise/analysis_engine/inputs.py:2367,2393`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/joulewise/analysis_engine/inputs.py:2367) | Reads stored notes, but `normalize_cooldown` at `:2293–2330` emits only result, verification, session, manifest, and raw-artifact identity | **No energy-class value passes to this join’s output.** Its callers include the analysis engine at `:3331`, [`floor_extraction.py:2873`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/joulewise/floor_extraction.py:2873), and [`check_window_provenance.py:703,768,802`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/check_window_provenance.py:703). Floor extraction gates its selected window at `:2883`, but that is not an anchor-source check. |

The `joulewise/`, `scripts/`, and `configs/` search found no other semantic campaign-provenance anchor reader. `cooldown_gates` is written to provenance but has no production reader in those roots. The generic campaign-provenance catalog loader transports records to the readers above; it does not inspect their anchor energy.

## Writers into campaign provenance

- [`new_campaign_provenance`, scripts/run_campaign.py:3505](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:3505) initializes `cooldown_anchor` to `None`.
- AXI copies a prior anchor at `:7411–7416` and freezes a new one at `:7817–7827`. Ordinary campaign flow copies at `:8430–8437` and freezes at `:8900–8911`. `_anchor_from_evaluation` at `:3980–4009` supplies the baseline; `_first_eligible_cooldown_anchor` at `:4012–4034` chooses it. Neither gates before eligibility.
- [`record_campaign_member_provenance`, scripts/run_campaign.py:4270](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/scripts/run_campaign.py:4270) writes notes to member rows at `:4319`, physical-member rows at `:4333–4339`, and `cooldown_gates` at `:4341–4351`. AXI call sites are `:7641`, `:7768`, `:7796`; ordinary flow uses `:8830` and `:8979`. Existing-member calls at `:8670` and `:8743` deliberately write no originating note.
- Note producers are `campaign_cooldown_before_member` (`:4105–4225`), first-run exemption and unknown-note branches (`:7590–7636`, `:8783–8814`), and `_physical_cooldown_evidence_for_config` (`:3841–3900`) for child repetitions. Each ultimately reaches the provenance writer above.

## Minimal design for §4.7 requirements 1–5

1. **Freezing:** In `_first_eligible_cooldown_anchor`, gate each candidate’s `evaluation.bundle_path` with the already imported `authenticate_window_members` **before** `_anchor_from_evaluation` calls `cooldown_reference_eligibility`. Use this at both `:7817` and `:8900`; ensure the child’s `_experiment_cooldown_anchor` path (`controller.py:3020`) gets the same ordering before it stores or uses a local anchor.
2. **Reuse:** Make `prior_campaign_cooldown_anchor` resolve the source bundle, gate it in this process, then compare the stored `baseline` with that bundle’s `summary_metrics.json["idle_baseline"]` before returning it. Both parent callers (`:7408`, `:8350`) then receive only verified anchors. This must happen before the copies at `:7411`/`:8430`, the child handoff at `:8569`, or cooldown calls at `:7612`/`:8798`.
3. **Refusal:** Return no anchor for a missing, ambiguous, battery-refused, or baseline-mismatched source, and record a structured refusal with status and reasons in the new campaign’s provenance. The parent then follows its current `None` path and can freeze its own first eligible, gated member. `WindowBatteryRefusal.members` provides the battery status and reasons.
4. **Custody:** Catch `WindowBatteryRefusal` specifically. Let `CustodyFailure` and its unreadable subclass propagate as exceptions.
5. **Boundary:** Use `joulewise.bundle_read.authenticate_window_members`; add no `battery_float` import to consumers and edit no frozen file. The existing child semantic checks remain useful after parent source authentication, but cannot substitute for it.

**Cold-gate recommendations:** Continue collection after a battery refusal *at freezing*, record it, and let the final whole-window gate refuse that campaign; this keeps the observed window evidence. Store a normalized, runs-root-relative `bundle_relpath` in each new anchor, requiring containment and a matching `bundle_id`; for old anchors, permit only a unique source-bundle lookup before gating. Bump the anchor format to `v2` for the new location field, while accepting old `v1` only through that gated, baseline-equal legacy lookup. These are recommendations for the lane’s ruling, not decisions made by this scout.

## RCA rows and available fixtures

| Row | Test placement and fixture |
|---|---|
| RCA-1 | Add a focused test beside [`test_run_campaign.py:2786`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/tests/test_run_campaign.py:2786), exercising both freeze call sites with charging bundle `C`. |
| RCA-2 | Add a provenance round-trip test in `tests/test_run_campaign.py`, using the production lock and writer as the executed `f1_probe.py` does. |
| RCA-3 | Extend the cooldown test at `tests/test_run_campaign.py:2200–2324` through `_member_readiness_reasons` and the member verdict row. |
| RCA-4 | Repeat RCA-2 and RCA-3 with passing bundle `P` and assert its baseline is actually used. |
| RCA-5 | Mutate one byte of `P/raw/battery_float.pre.ioreg` after creating the stored anchor; assert `CustodyFailure` escapes `prior_campaign_cooldown_anchor`. The authentication helper pattern exists in [`test_battery_float.py:203–305`](/Users/edr/code/JouleWise-wt-anchor-scout-3ba66eeb/tests/test_battery_float.py:203). |
| RCA-6 | Rewrite `P/summary_metrics.json` with a different idle baseline and assert refusal despite a passing battery gate. |

Committed raw fixtures **exist** at `tests/fixtures/battery_float/float.ioreg` and `charging-synthetic-from-real.ioreg`; stale and malformed variants also exist there. `C` and `P` as complete bundles are **not** committed fixtures: [`/tmp/cg_samesig_err/f1_probe.py`](/tmp/cg_samesig_err/f1_probe.py) builds `C` from those bytes, following `BundleAuthenticationTests.bundle`. The campaign test file already has anchor handoff, cooldown, and provenance helpers. `tests/fixtures/cooldown_join/real_7b_v1_existing_manifest.json` exists for the separate cooldown join.

## Real-runs pre-check and critical path

A read-only search found 33 `campaign_manifests` directories under `/Users/edr/code/JouleWise/runs_*`; it found none under the specified worktree-style `JouleWise*/runs` locations or `/Users/edr/night-custody`. On the real `runs_window_a10_20260725` directory, the judge’s exact §4.6 pre-check returned **exit 1: four manifests, four refused anchors**. Each named `neg8-window-start-r1` and reported `battery_float_evidence_missing (prospective bundle)`. Thus at least one real stored anchor cannot pass the current battery gate; this output does **not** establish that it was a charging bundle.

The lane can start its cold gate now. Its fix and RCA rows must land before the next scored campaign. Until then, §4.6 requires a **passing pre-check on that campaign’s actual runs directory** before it starts. No repository file was changed; scratch work is under `/tmp/anchor-scout-3ba66eeb/`.