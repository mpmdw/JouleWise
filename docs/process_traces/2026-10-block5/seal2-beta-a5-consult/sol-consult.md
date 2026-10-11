```json
{
  "schema": "claude-codex-report/v1",
  "genre": "root_cause",
  "status": "findings",
  "completion": "complete",
  "summary": "Sequence 456 caused both stale-acceptance exclusions; same-epoch re-derivation is required by policy but unsupported by the existing bootstrap tooling.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "ee569cc7d921eb9c2a96e501ca21df5bc38e6bb1",
    "head_end": "e1a9c2a8b71c147477894d9d43eea84b9e2c5e62",
    "upstream_end": "e1a9c2a8b71c147477894d9d43eea84b9e2c5e62",
    "branch": "records/2026-10-block5"
  },
  "pathspec": [],
  "unowned_dirty": ["docs/process_traces/2026-10-block5/seal2-beta-a5-window.md"],
  "verdict": {
    "cause": "confirmed",
    "remediation": "proposed"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nimport json\nfrom pathlib import Path\nfrom decimal import Decimal\nr=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18')\na=json.loads((r/'configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json').read_text())\nrows=[json.loads(x) for x in (r/'runs/calibration_observation_ledger.jsonl').read_text().splitlines()]\nd=json.loads((r/'configs/calibration/observation_dispositions.json').read_text())\ndisposed={x['content_id'] for x in d if x['disposing_decision_id'] in a['prior_observation_set']['disposing_decision_ids']}\nprior={x['content_id'] for x in a['prior_observation_set']['observations']}\nobs={x['content_id']:x for x in rows if x.get('content_id')}\nnew=[x for k,x in obs.items() if k not in prior and x['identity_epoch']==a['identity_epoch']]\nv=[Decimal(x['b_fiducial_s']) for x in a['derivation_corpus']['members']]\nprint('ledger_rows',len(rows))\nprint('new_systematic_sequences',[x['sequence'] for x in new if x['disposition']=='systematic-invalid'])\nprint('new_valid_range_expansions',sum(x['disposition']=='valid' and not min(v)<=Decimal(x['exact_bound_lexeme_s'])<=max(v) for x in new))\nprint('doubling_count',sum(x['disposition']=='valid' and x['identity_epoch']==a['identity_epoch'] and k not in disposed for k,x in obs.items()))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ledger_rows 478",
          "new_systematic_sequences [456]",
          "new_valid_range_expansions 0",
          "doubling_count 41"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ledger_rows 478\\nnew_systematic_sequences \\[456\\]\\nnew_valid_range_expansions 0\\ndoubling_count 41"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Existing registration mandates prospective re-derivation, but writer and issuer reject same-epoch bootstrap. Neither a successor sampling plan nor retrospective rescue is authorized.",
      "needs": "Cold adjudication of a prospective desk-side trigger amendment versus a newly registered same-epoch derivation and block restart."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The records worktree advanced concurrently, changing seal2-beta-a5-window.md. This session changed nothing; code findings use the pinned harvest checkout and measurement clone.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only inspection and structure-only restricted-file projections were performed. No measurement, re-harvest, candidate generation, or test suite was run.",
      "needs": "Lead owns implementation verification and any subsequent quiet-Mac work."
    }
  ]
}
```

## Causal chain

Source notation below:

- **H** = `/Users/edr/night-custody/desk/b5-harvest`, inspected at `0699abbb0881ce64b39c46ba07de568cc3848260`.
- **M** = `/Users/edr/night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18`.
- **R** = `M/configs/campaigns/v5_claim_25g83/registration_block5.md`.
- **P** = `M/configs/calibration/preregistration_d079_epoch_25g83_rev1.md`.
- **B** = `/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-07-block5-seal/40-magistrate-brief.md`.

I read the consult brief in full, opened no other consult seat’s report, and changed no file. Restricted bracket evaluations were read only through a program printing status words and reason codes.

**1. The lead’s reading is correct for attempts 4 and 5 and future windows.** The deciding function is `evaluate_calibration_bracket`, invoked by the harvest through `calibration_bracket_for_bundles`. The harvest converts its failure into `calibration.bracket_acceptance_failed`. (`H/joulewise/calibration_bracketing.py:2103`, `H/joulewise/b5/harvest.py:4588`, `H/joulewise/b5/harvest.py:4595`.)

The evaluator considers distinct ledger observations outside the acceptance’s prior observation set—not merely the evaluated window’s two endpoints. One new `systematic-invalid` observation of a judged epoch makes freshness stale and returns before computing endpoint drift. (`H/joulewise/calibration_bracketing.py:2500`, `:2514`, `:2577`, `:2594`.)

Sequence **456** is that observation: BETA-3’s pre capture, bound **44.3768 ms**, disposition `systematic-invalid`, same six-field identity as the acceptance. It is above the operative **36.4629 ms** screen. (`M/runs/calibration_observation_ledger.jsonl:456`; `R:957`.) Classification distinguishes a physically valid capture above the systematic screen from an ordinary-invalid capture. (`H/joulewise/calibration_ledger.py:6190`.)

My census found:

- Exactly one new same-epoch systematic-invalid observation: sequence 456.
- No new valid same-epoch range expansion.
- **41** counted valid observations after the declared dispositions, below the doubling threshold **48**.
- All four measurement-clone estimator hashes match the artifact.

The restricted evaluations for both attempts independently list only `new_systematic_failure_challenges_preflight_screen`, with empty `stale_fields` and null drift. The other trigger checks are at `H/joulewise/calibration_bracketing.py:2494`, `:2539`, `:2553`, and `:2573`; the registered meanings are at `R:2482`.

Attempts 4 and 5 contribute valid observations to the doubling count, but **neither triggers this exclusion**. Their bounds lie inside the original corpus range: sequences 464/468 are 31.4087/31.8648 ms; 474/478 are 27.5505/29.4777 ms. (`M/runs/calibration_observation_ledger.jsonl:464`, `:468`, `:474`, `:478`; range at `R:2493`.)

A future GAMMA bracket using unchanged rules will encounter sequence 456 and fail likewise. This is explicitly registered: the trigger remains in the ledger and later brackets fail until issuance. (`R:2501`.)

**ALPHA re-harvest needs a qualification.** Evaluating ALPHA against a complete, current, otherwise admissible snapshot would encounter the same trigger. But the stock harvest against today’s live ledger first asks for ALPHA’s session-terminal pin. That function refuses when later non-control receipts exist, so the harvest emits `calibration.no_bracket` before freshness evaluation. (`H/joulewise/calibration_ledger.py:5275`, `:5314`; `H/joulewise/b5/harvest.py:4451`.) A replay using ALPHA’s preserved original ledger bytes does not contain sequence 456. Its original fresh judgment is not retroactively evidence of a stale instrument.

**4. Attempts 4 and 5 cannot be rescued merely by substituting a newly derived acceptance.** The registration requires judgment under the prior artifact, never an acceptance fitted to the observation, and permits no rule or threshold change for an armed or completed attempt. (`R:2484`, `R:5144`.) Its re-harvest provision permits a **repaired program on identical bytes**, not a later threshold applied retrospectively. (`R:4696`; `B:852`.)

A genuine implementation defect could therefore support lawful re-harvest under the original applicable rule. Here, the code faithfully implements the sealed trigger rule. Reclassifying that rule as excessive is a prospective science change, not an implementation repair.

Attempt 4 also retains the brief’s independently reported sleep objection. Attempt 5’s six lost members are not automatically another window exclusion: the driver’s minimum is 4/5 of a stage, whereas the registered claim minimum is **five surviving units out of ten per target-cell stratum**. (`H/joulewise/b5/driver.py:154`, `:1392`; `R:4166`.) LOW yield alone removes nothing. (`R:4743`.) Thus 14/20 is a warning, not proof that the registered cell minimum failed. Its present harvest names only the calibration exclusion; that does not establish every deferred downstream check would pass.

**6. This could have been detected before either arm.** The existing production function to exercise is **`joulewise.calibration_bracketing.evaluate_calibration_bracket`**, using an authenticated current ledger snapshot, the acceptance cutoff, complete discovered candidates, and the last completed bracket’s valid binding. Candidate discovery is `discover_calibration_candidates`. (`H/joulewise/calibration_bracketing.py:1944`, `:2103`, `:2355`.) An empty-candidate shortcut is invalid because the evaluator enforces complete enumeration before checking these triggers.

There is **no existing dedicated acceptance-freshness-only check**. The issuer’s `check` explicitly does not evaluate trigger observations; it watches identity and registration admissibility. (`H/scripts/issue_calibration_acceptance_generation.py:11`, `:405`.) The registration itself says nothing at the arm, plan writer, or watchdog checks the triggers. (`R:2509`.) A desk helper extracting the production trigger logic would close this gap without running a new measurement or exposing claim values.

## Remediation

**2. The current rule requires re-derivation, but does not supply an executable same-epoch successor procedure.** It sends the question to a cold gate before another arm. (`R:2509`.)

The existing pre-registration is an **epoch-bootstrap campaign**, not a reusable authorization to refresh this same epoch:

- Its registered members are valid, resolved, in-frame captures belonging to its counting derivation windows; it prohibits B-based exclusions, top-ups, and retries. (`P:1484`.)
- It requires at least **24 counted captures** and **12 members**, ordinarily two twelve-slot sessions; a third counting session is allowed for count shortfall, plus one adverse-window replacement. (`P:1164`, `P:1197`.)
- Each session has a 600-second settle, twelve slots at 600-second pitch, and a final 480-second capture budget: **7,680 seconds, or 2 h 8 min**. There is no six-hour inter-session requirement in Revision 6. (`P:1027`, `P:1038`, `P:1045`.)
- Recording is roughly 197 seconds per capture; slot cadence and estimator budget, rather than recording alone, determine campaign time. (`P:1111`, `P:1031`.)
- Its predecessor and opening ledger pin are fixed; issuance cannot reopen the campaign after its `CLOSE_AND_DERIVE` decision. (`P:1443`, `P:1454`, `P:1467`, `P:1472`.)

Most decisively, the live writer rejects derivation-only capture in any already judged epoch, and the candidate issuer rejects a target epoch equal to its predecessor’s. (`H/scripts/validate_powermetrics_fiducial.py:2357`; `H/scripts/issue_calibration_acceptance_generation.py:2835`.) Therefore **“collect another 24 with the existing command” is not presently lawful or executable**.

Nor does the rule say to incorporate all later bracket captures automatically. Existing bootstrap tooling refuses undisposed valid same-epoch observations outside its registration. (`H/scripts/issue_calibration_acceptance_generation.py:63`, `:2760`.) Sequence 456 must remain in the prior history with its original disposition; any eligibility as a future successor’s derivation input needs an explicit cold ruling. It cannot be silently relabelled to make a threshold pass.

**Programs and changed surfaces.** `issue_calibration_acceptance_generation.py prepare-candidate` derives statistics and operatives but emits an unissued candidate; issuance is a reviewed atomic transaction. `promote_calibration_candidate.py` promotes only its specifically pinned historical candidates. `reissue_calibration_acceptance.py` authenticates and reconstructs the predecessor corpus, not a new sampling campaign. (`H/scripts/issue_calibration_acceptance_generation.py:24`, `:36`; `H/scripts/promote_calibration_candidate.py:57`; `H/scripts/reissue_calibration_acceptance.py:135`.)

A literal successor route needs a ruled identifier and sampling/membership procedure, then changes these surfaces:

| Surface | Where it must take effect |
|---|---|
| New calibration registration; same-epoch writer/input support | Desk development, then a separate reviewed calibration checkout for captures |
| Candidate issuer and promotion support; science evidence and ruling records | Desk |
| New issued acceptance file and `calibration_bracketing.py` generation/default/byte-pin registrations | New measurement clone; also harvest checkout |
| All three packs’ acceptance pins and regenerated dependent manifests | New measurement clone |
| Block registration, sealed inventory and seal record | New seal and new measurement clone; records maintained at desk |
| Ledger observations and head pin | Append-only capture ledger and reviewed pin advances |

The acceptance is pinned in both floor plan trees and GAMMA’s tree, and registered centrally in code. (`M/configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json:31`; corresponding 8B file `:31`; `M/configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json:36`; `H/joulewise/calibration_bracketing.py:155`, `:219`, `:231`.) Exact successor filenames and the regenerated changed set must be established by that ruling and generation, not invented here.

**Consequences:** literal re-derivation is **not desk work alone**. It needs a **prospective cold registration**, issuance gates, **a new seal and measurement clone**, and a **restart at ALPHA**: the block requires one acceptance across all three packs, and the acceptance/pins already read by completed windows would change. (`R:4775`, `R:4801`; `B:931`.) It does not leave a presently authorized route directly to same-block BETA-6 while retaining the old ALPHA floor.

If the gate adopts the existing Revision-6 acquisition shape for a new registration, budget **4.27 hours** of calibration window time normally, up to **8.53 hours** for three counting windows plus a replacement. Those are conditional planning estimates, not a registered new-capture requirement. Replacing ALPHA adds the registration’s projected **5.1–5.9-hour** chain before BETA can arm. (`R:383`.) Allow roughly **24–48 wall-clock hours** for development, reviews, calibration, issuance, sealing and replacement ALPHA; gate delays can extend that substantially.

**3. The permanent trigger is disproportionate to the evidence shown.** “Above the previous sample maximum” does not, by itself, establish a changed physical process. Under continuous exchangeable draws, a new observation exceeds the maximum of 24 with probability **1/25 averaged over calibration corpora**. That is a rank calculation, not a measured per-capture failure rate for this particular Mac or a proof of independence. The registration confirms the screen is the sample maximum. (`R:957`; `P:1518`.)

One exceedance among fourteen bracket observations is therefore compatible with ordinary variation. The implementation nevertheless excludes windows before examining their own in-range endpoints and drift. (`H/joulewise/calibration_bracketing.py:2594`, `:2664`.) A changed regime remains possible; this evidence does not prove one.

My preferred prospective amendment is:

- Keep a capture/bracket failure local to the affected window.
- Treat a single later empirical-range or sample-maximum exceedance as a disclosed calibration-review signal, rather than permanent exclusion of every subsequent bracket.
- Retain identity/protocol changes as hard provenance barriers.
- Require an explicitly calibrated change-detection or physical-validity criterion for global invalidation.
- Preserve the measured bracket allowance and its single embedding in uncertainty. (`H/joulewise/calibration_bracketing.py:2730`, `:2749`.)

The science gate must settle the statistical criterion and any replacement level threshold. I do not propose an unsupported numerical ceiling.

**Shortest proposed route to BETA-6:** a prospective **desk-side rule amendment**, keeping the issued acceptance bytes and measurement clone intact.

1. Finish the two blind science seats; cold judge/refuter decide the local-versus-global trigger rule.
2. Seal an explicit prospective override for future windows, including empirical-range triggers and the unchanged acceptance’s role.
3. Implement that policy in the desk harvest evaluation, add the freshness pre-arm helper, and verify the composed path including the sealed verdict writer.
4. Complete R3 review/testing/cold calibration pass, merge, and publish the harvest pin addendum.
5. Check current ledger freshness and forecast the next bracket’s count, retain keep-awake protection, check the LOW-yield process rule, then perform the normal notice and arm sequence.

Desk-only fixes do not move the measurement clone; the harvest reaches them through a new desk pin/addendum. (`R:4777`, `R:4804`; `B:917`.) Rule changes still require the prospective cold erratum. (`R:5144`.) Estimate **4–12 hours of desk/gate work**, **zero calibration measurement hours before arming**, with review latency uncertain. BETA’s ensuing chain remains roughly 5.1–5.9 hours. This route is a proposal requiring adjudication, not permission already supplied by the existing registration.

**NEEDS_RULING:** choose (A) that prospective desk-side amendment, or (B) a newly registered same-epoch successor and ALPHA restart. I recommend A. Unchanged BETA-6 and GAMMA arms are blocked meanwhile.

**5. Recurrence must be addressed before the next arm.** A fresh corpus maximum alone recreates the same tail problem. Fix both the global poisoning rule and the distinction between an empirical screen exceedance and demonstrated instrument failure through the science consult/cold erratum—not repeated threshold expansion after each failed window.

The current doubling count is 41: **seven further valid captures reach 48**. Even without sequence 456, four more ordinary two-capture windows would cross that threshold. The pre-arm desk check must forecast the complete next bracket, not merely report freshness at the current tip. (`H/joulewise/calibration_bracketing.py:2544`; `P:886`.) Revising the doubling rule itself requires the same prospective science gate.

For BETA-5’s LOW yield, inspect only the released terminal record for `stage.members_refused_pre_bundle_identical`. LOW with that shared pre-bundle cause requires a cure before unchanged re-arm; LOW alone does not. (`R:4725`.) Keep-awake protection addresses the separate sleep mechanism; it cannot remove the acceptance trigger.

## Disproved alternatives

- **Sleep caused the recorded exclusions in both attempts:** disproved. Both evaluations stop on ledger freshness before drift; the awake attempt reproduces the same trigger. Sleep remains a separate objection to attempt 4.
- **Attempts 4/5 challenged the screen themselves:** disproved by their valid, in-range ledger rows and the sole sequence-456 trigger.
- **Corpus doubling already fired:** disproved by the authenticated-policy census, 41 versus 48.
- **A candidate-generation or identity-watch command alone cures this:** disproved by same-epoch refusals, candidate-only outputs, and `check`’s explicit omission of trigger evaluation.
- **Re-harvest authority permits retrospective threshold replacement:** disproved by the prior-artifact rule and prospective-only threshold changes.

## Residual risk

This establishes the exclusion’s cause, not that attempts 4/5 would satisfy every downstream claim check if it were removed. Their harvest counts report deferred strict assessments; claim values and prohibited member-level exclusion files remained unopened.

No numerical replacement screen or demonstrated regime-change rate has been established. A same-epoch re-derivation procedure, if selected, still needs its own prospective membership, stopping, issuance and block-continuity rulings.

RECOMMENDATION: sequence 456 permanently poisoned the old acceptance under the sealed global trigger ; before the next arm adopt a prospective local-failure/global-review amendment and add live-ledger freshness plus count forecasting, or register a same-epoch successor and restart at ALPHA ; two blind science seats, cold judge/refuter erratum, R3 verification and harvest-pin addendum for the desk route, issuance plus new seal/clone for a successor ; attempts 4 and 5 remain non-claim-usable, with sleep separately adverse to 4 and LOW yield alone insufficient to exclude 5.