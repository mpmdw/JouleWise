```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "partial",
  "summary": "The issued r6/r7 calibration corpus resolves 17/17 anchors under v3; historical science bundles record bounded v2 anchors, while no _v5 claim bundles or D-165 floors have issued.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "bbe475e5c410d9177f41a47101029ff15109523f",
    "head_end": "bbe475e5c410d9177f41a47101029ff15109523f",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "r6/r7 calibration", "action": "start_now", "anchored": 17, "unanchored": 0},
      {"row": "historical July science numbers", "action": "do_not_start", "reason": "Do not promote bounded v2 records to current v3 claim evidence."},
      {"row": "_v5 and D-165 outcomes", "action": "wait_for", "reason": "No collected claim bundles or issued floors are linked yet."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -c 'import json; from pathlib import Path; r=json.load(open(\"configs/calibration/calibration_acceptance_d079_v2_n17_r7.json\"))[\"derivation_corpus\"][\"members\"]; d=json.load(open(\"docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json\")); m={x[\"member_id\"]:x for x in d}; p=json.load(open(\"docs/process_traces/2026-08-09-prefill-phase-proof/results.json\"))[\"bundles\"]; print(\"r7\",len(r),sum(m[x[\"member_id\"]][\"anchor_v3\"][\"status\"]==\"bounded\" for x in r)); print(\"paper-populations\",sum(x[\"stack\"]==\"1.5B\" for x in p),sum(x[\"stack\"]==\"7B\" for x in p))'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["r7 17 17", "paper-populations 50 50"]},
      "expected": {"exit_code": 0, "tail_regex": "r7 17 17\\npaper-populations 50 50"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)", "bbe475e5c410d9177f41a47101029ff15109523f"]},
      "expected": {"exit_code": 0, "tail_regex": "## HEAD \\(no branch\\)\\nbbe475e5c410d9177f41a47101029ff15109523f"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The cited 13-osctx-mvp-design-v2_3.md trace is absent from this worktree; sensitivity figures were taken from the task prompt.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Instrument-validation captures do not record a run_campaign-versus-plain-run invocation or post-window dwell. Three r7 member raw paths point outside the permitted read locations; their retained derivation records were inspected.",
      "needs": "Lead may check original launch records and the three raw captures if exact provenance is required."
    }
  ]
}
```

## Scheduling matrix

“Anchored” below means **bounded under the method recorded for that corpus**. The July science bundles record the older `powermetrics_native_second_censored_intersection_v1` method; their counts are not v3 acceptance counts. The exact fields are `instrument_evidence.json`’s `clock_anchor_resolved`, `clock_anchor.method/status/effective_clock_anchor_bound_s`, and run `metadata.json`’s `uncertainty_evidence.clock_anchor.*` and `trace_window_margins.requested_post_window_dwell_s`. Current unresolved captures may record `trace_fallback_method`; that fallback is explicitly barred from claim math in [powermetrics.py](/Users/edr/code/wt-278ebc9e-g2a/joulewise/adapters/powermetrics.py:574).

| Corpus → bundles | Anchored / unanchored | Launch, dwell, and claim dependency |
|---|---:|---|
| **r6/r7 calibration acceptance:** the same 17 `derivation_corpus.members[]` instrument-validation captures | **17 / 0 under rederived v3**; bound **0.538–3.026 ms** | Supplies the paper’s 17-capture table, **9.724 ms** screen and **10.164835 ms** drift limit. The worked capture supplies the **59/49** pulse observation, **1.135 ms** anchor and **30.068 ms** capture bound. Its stored file says bounded *v2*; the retained rederivation says bounded *v3*. These capture directories have no run metadata, recorded dwell, or executable launch context, so `run_campaign` versus direct validation cannot be established per capture. [r7 member list](/Users/edr/code/wt-278ebc9e-g2a/configs/calibration/calibration_acceptance_d079_v2_n17_r7.json:46), [v3 derivations](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/r4-derivation.json:1), [paper arithmetic](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/draft-v2-skeleton.md:157). |
| **a10:** 30 floor-cell science bundles plus 7 references | **37 / 0 stored v2**; 26/30 science captures have controller coverage under 60 s | Campaign log and metadata show campaign collection and **1.0 s** requested dwell. Supplies draft-v1’s three point/corner floor pairs, **10.92/5.92/7.02** ratios and **25.6–31.1 ms** timing range; these placements are retired diagnostics. Two valid calibration captures are bounded; a third invalid, unresolved attempt is excluded. [draft values](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/draft-v1.md:103), [registry membership](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/results-fill-registry.md:667), [example bundle metadata](/Users/edr/code/JouleWise/runs_window_a10_20260725/p2015-df-ph-decode-abs-r03/metadata.json), [excluded capture](/Users/edr/code/JouleWise/runs_window_a10_20260725/instrument_validation/20260725T055825-b10cb348/instrument_evidence.json). |
| **1.5B record-support population:** 10 a10 decode bundles + 40 Window C bundles | **50 / 0 stored v2**; 47/50 have controller coverage under 60 s | Campaign metadata records **1.0 s** dwell. Supplies **37/50** two-record refusals, **13/50** passes, the r03 **0.121034145 s** example, and the current methods paper’s **0.1365 s** median. Window C’s extra invalid calibration attempt is excluded. [issued 100-bundle enumeration](/Users/edr/code/wt-278ebc9e-g2a/docs/process_traces/2026-08-09-prefill-phase-proof/results.json:1), [paper membership and counts](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/draft-v2-skeleton.md:642), [registry r03 source](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/results-fill-registry.md:690), [excluded C capture](/Users/edr/code/JouleWise/runs_window_c_20260726/instrument_validation/20260726T225227-1f550773/instrument_evidence.json). |
| **7B record-support population:** 50 floor-window science bundles | **50 / 0 stored v2**; 46/50 have controller coverage under 60 s | Campaign metadata records **1.0 s** dwell. Supplies **50/50** identifiable, **33** three-record and **17** four-record phases, and the **0.2815 s** median. Its two window calibrations are bounded v2. [paper counts](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/draft-v2-skeleton.md:652), [registry and membership](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/results-fill-registry.md:1045), [example bundle metadata](/Users/edr/code/JouleWise/runs_window_7bfloor_20260729/sw7bfloor-df-ph-decode-abs-r05/metadata.json). |
| **Historical contrast:** 40 A/B/B/A science bundles plus 7 references | **47 / 0 stored v2**; all 40 science captures have controller coverage under 60 s | Campaign metadata records **1.0 s** dwell. Supplies draft-v1’s retired sizing input **5.809930 J** and its **11.619860 J** extrapolation, **not** an issued comparison. Both window calibrations are bounded v2. [draft sizing](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/draft-v1.md:268), [exact bundle pattern](/Users/edr/code/wt-278ebc9e-g2a/docs/paper/results-fill-registry.md:613), [example bundle metadata](/Users/edr/code/JouleWise/runs_window_contrast_20260730/swdec-contrast-b01-a1/metadata.json). |
| **Window D / README historical pass:** 30 science bundles plus 7 references | **37 / 0 stored v2**; 29/30 science captures have controller coverage under 60 s | Campaign metadata records **1.0 s** dwell; both calibrations are bounded v2. README calls D and the other four July windows historical passes, while explicitly denying them live claim authority. [README qualification](/Users/edr/code/wt-278ebc9e-g2a/README.md:84), [example D metadata](/Users/edr/code/JouleWise/runs_window_d_20260726/p2015-df-rq-mid-abs-r01/metadata.json). |
| **D-117 `_v5` / D-165 floor and contrast registrations** | **0 / 0 collected claim bundles** | These are rules and prospective cells, not measured floor values. The pack says its floor gate and linked bundle hashes are pending; the registered D-165 ratio threshold is **2.0**. [pack status](/Users/edr/code/wt-278ebc9e-g2a/docs/campaign_packs/d117_contrast_v5.md:15), [D-165 registration](/Users/edr/code/wt-278ebc9e-g2a/configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json:1). |
| **README idle-variance pilot:** 12 archived envelopes, each with 19 custom collector rounds | **5 / 7 envelopes** have respectively all bounded / all unknown round anchors; **2/12** were retained by the overall pilot | This used `sample_quiet_predicate_evidence.py collect`, neither `run_campaign` nor plain `joulewise run`; sessions record no post-window dwell. The README’s “only two of twelve passed the timing check” conflates retention with anchor status: five envelopes have bounded round anchors, while only two satisfy the overall retention outcome. This is provisional operational evidence, not a paper energy corpus. [README claim](/Users/edr/code/wt-278ebc9e-g2a/README.md:15), [archived summary](/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/summary.json), [per-round anchor records](/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/evidence/envelope-01/rounds.jsonl). |

The five July window groups above have **1.0 s recorded dwell** and campaign provenance; [run_campaign.py](/Users/edr/code/wt-278ebc9e-g2a/scripts/run_campaign.py:1552) passes the policy dwell to its run command. A bounded v2 record remains a bounded **v2** record. The current v3 estimator requires at least **60 s** of native fit span and sufficient controller coverage, and only v3 is in the claim-bearing method set: [uncertainty_evidence.py](/Users/edr/code/wt-278ebc9e-g2a/joulewise/uncertainty_evidence.py:1065), [method gate](/Users/edr/code/wt-278ebc9e-g2a/joulewise/uncertainty_evidence.py:1457). Thus the short July bundles cannot be counted as v3-resolved without a different capture; their historical status does not imply that they used the fallback.

## Critical path

**No currently issued `_v5` or D-165 claim-bearing energy number rests on an observed unresolved clock anchor:** those results have not issued. The issued r6/r7 calibration constants and worked capture are supported by **17/17 bounded v3 rederivations**. The printed July inference numbers are explicitly historical diagnostics or retired sizing inputs and have bounded **v2** anchors; promoting them to current v3 claim evidence would fail the method/version gate for many short captures.

I found **no recorded fallback marker in the included measured paper bundles**, so there is no defensible bundle-specific energy correction to calculate. For a *future* unresolved capture using the sudo-spawn midpoint fallback, the supplied sensitivity is **±1.8% per ±0.1 s**, or **−9.6%/+7.4% at ±0.55 s**. Those percentages should not be applied to the July v2 bundles or to the idle pilot’s different collector.

The audit remains partial on exact launch provenance for the 17 standalone calibration captures and on three r7 raw captures whose derivation records point outside the permitted read locations. No files were changed and no measurement process was started.