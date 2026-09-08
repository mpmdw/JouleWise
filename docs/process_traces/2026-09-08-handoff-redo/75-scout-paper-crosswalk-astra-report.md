```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Comparison acquisition and desk preparation can proceed as separate lanes, but production paper roles, several suppliers, and the successor placement/branch contract remain missing.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row":"S1 successor placement and registry specification","action":"start_now"},
      {"row":"S2 reported-energy supplier and synthetic tests","action":"start_now"},
      {"row":"S3 claim-side-bound semantics and source-cell join","action":"needs_ruling"},
      {"row":"S4 authenticated whole-window refusal supplier","action":"start_now"},
      {"row":"S5 floor acceptance and D-165 publication preparation","action":"start_now"},
      {"row":"S6 comparison renderer specification and non-issuing fixtures","action":"start_now"},
      {"row":"S7 fill-checklist and first-use migration inventory","action":"start_now"},
      {"row":"Characterization inclusion and custody family","action":"needs_ruling"},
      {"row":"G2-a diagnostic collection","action":"wait_for","wait_for":"Lead-controlled quiet window and current acquisition gates"},
      {"row":"Production pack generation","action":"wait_for","wait_for":"Authenticated G2-a selection and prompt pin"},
      {"row":"G2-b and ALPHA/BETA/GAMMA","action":"wait_for","wait_for":"Readiness gates, pack-bound launch implementation, reviewed estate and quiet windows"},
      {"row":"Production role pinning and empirical paper fill","action":"wait_for","wait_for":"Actual authenticated artifacts, adopted suppliers and successor placement contract"},
      {"row":"Execute stale paper-G selector instructions or fill retired rows","action":"do_not_start"},
      {"row":"Transfer/common-time replay redesign or external-meter collection","action":"do_not_start"}
    ],
    "inventory": {
      "protocol_image_references": 1,
      "protocol_markdown_table_rows": 0,
      "current_skeleton_outcome_groups": 0,
      "production_supply_roles": 0,
      "registered_issuance_gates": ["d165_closeout/d165-closeout.v1"]
    }
  },
  "verification": [
    {
      "id":"V1",
      "kind":"smoke",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/fill-rehearsal/select_outcome_branches.py --check-rendered docs/paper/draft-v2-skeleton.md",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250"]},
      "expected":{"exit_code":0,"tail_regex":"^METHODS_DIAGNOSTIC validated; abstract_words=246, limit=250$"}
    },
    {
      "id":"V2",
      "kind":"inspection",
      "cmd":"git status --short --branch; git rev-parse HEAD origin/main",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","1c83f2af48df5611c7bbf824bec818209c252d0d","1c83f2af48df5611c7bbf824bec818209c252d0d"]},
      "expected":{"exit_code":0,"tail_regex":"## HEAD \\(no branch\\)\\n1c83f2af48df5611c7bbf824bec818209c252d0d\\n1c83f2af48df5611c7bbf824bec818209c252d0d"}
    }
  ],
  "flags": [
    {
      "id":"F1","kind":"lead_ruling","level":"nonblocking",
      "text":"Claim-side-bound validation is explicitly a non-issuing candidate; the adopted producer contract and source-cell joins are missing.",
      "needs":"Rule the sidecar semantics before implementing or registering claim-evidence.v1."
    },
    {
      "id":"F2","kind":"lead_ruling","level":"nonblocking",
      "text":"The successor needs explicit placements and custody routes for floor tables, characterization and dependence results; retired registry rows confer no rendering authority.",
      "needs":"Adopt the successor placement/supplier contract; decide whether separate Window C characterization is included."
    },
    {
      "id":"F3","kind":"residual_risk","level":"nonblocking",
      "text":"branch-selection.md describes A/B/REFUSAL and transfer slots that the current selector rejects; parked round-7 sheets also contain superseded wording.",
      "needs":"Correct the active guidance and adjudicate successor text rather than mechanically applying the historical sheets."
    },
    {
      "id":"F4","kind":"verification_gap","level":"nonblocking",
      "text":"Read-only source inspection and the fallback validator were run. No suite, acquisition, out-of-repository corpus replay, production issuance or hardware validation was performed.",
      "needs":"Lead verifies actual acquisition and production artifacts at their respective gates."
    }
  ]
}
```

## Scheduling matrix

**The protocol contains one figure, P1, and no Markdown tables. The current skeleton has no paper-G outcome groups.** Former Tables 2/3 and A/B/REFUSAL placements survive as retired registry entries and historical instructions. The crosswalk below distinguishes those successor obligations from currently published material.

Ed’s instruction establishes the comparison objective without the old deadline. It does not make retired slots fillable or missing measurements into empirical refusals.

**Path notation:** `<G2A>`, `<ALPHA>`, `<BETA>`, `<GAMMA>` and `<publication>` denote future lead-frozen custody roots, not issued locators. Where a producer accepts an output argument, the filename below is a registered convention or descriptive pattern; its actual path and digest must enter the supply map. `L` is the authenticated G2-a `collection_prefill_tokens`, never an assumed rung.

**Custody notation:** RE = `ReportedEnergyParentsRef`; DC = `D165CloseoutRef`; WW = `WholeWindowVerdictRef`; CE = `ClaimEvidenceRef`; TP = `TransferProjectionRef`. All empirical suppliers must call `open_paper_input(ref)`. Every production role needs the complete fixed/transitive source census, inventory, receipt, fresh validation and reopen checks. The clean anchor must be contained in local `origin/main`.

The implemented seam is in `joulewise/paper_custody.py`; its [contract](docs/contracts/paper_supply_custody.md) currently enumerates **zero custody-bound registry rows**. Only DC has a registered issuance gate; all five supply-map roles are non-issuing fixtures.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| X1 — P.1 model/workload identities and selected prefill length | wait_for | G2-a for selected length; desk specification now | Panel/workload files → `<G2A>/window-plan/d166-prefill-counts-receipt.json`, `d166-prefill-resolvability-summary.json` → selection JSON → prompt-pin v2. Producers exist: `summarize_g2a_prefill_probe.py`, `select_g2a_prefill_length.py`, `issue_g2a_prefill_prompt_pin.py`. Registry: V5-ID-001/002, V5-WL-001–005, V5-G2A-001. RE includes selection/prompt-pin parents, but no issuing role or dedicated selection-text grant exists. |
| X2 — P.1 twelve-ratio hypothesis; paper-G A/all-pass sentence and contingent headline | wait_for | Both floor windows, mint/replay, finalized manifest and publication acceptance | `<publication>/d165-closeout.json` from `scripts/build_d165_dominance_closeout.py`, consuming finalized manifest, aggregate floor and D-165 replay sidecar. Mint/sidecar producer exists: `scripts/mint_floor_artifact_generalized.py --d165-replay-out …`. Registry: all eight `R_*`, four comparative `R_cm_*`, four absolute N/A entries, contingent-title rule. DC gate exists; production role and complete prose renderer are missing. Raw inputs arise in ALPHA/BETA; issuance also waits for authenticated close-out parents. |
| X3 — Paper-G B/below-two sentence and failed-component list | wait_for | Same complete, authenticated and evaluable ratio census as X2 | Same close-out; enumerate every failed independent/comparative diagnostic record. Registry OB-01 and ratio rows. `render_d165` currently returns only the branch; the professor-facing list renderer is missing. B never means that a model contrast failed. |
| X4 — Former Table 2 floor columns; P.3 component composition and cell labels | wait_for | ALPHA and BETA floors | `<window-custody>/detection-floor-extraction.json` via `scripts/extract_detection_floors.py`; v2 floor output via generalized mint. Exact semantic IDs: `d117-qwen3-{1p7b,8b}-decode-floor-v5` and `d117-qwen3-{1p7b,8b}-prefill-pL-floor-v5`. Registry DS-01, DS-11/15/19/23 and all `F_*`/TERM rows. Extraction/mint arithmetic exists. Standalone floor-cell rendering has no adopted dedicated family/grant; DC authenticating a floor does not automatically license arbitrary floor-table output. |
| X5 — Former Table 2 means, intervals, per-token values and counts | wait_for | ALPHA supplies small-model cells; BETA supplies large-model cells | Generated `extraction_spec.json`, D-117 mint-consumption extraction report, whole-window basis, strict source members, selection and prompt pin. Registry DS-09/10/12, DS-13/14/16, DS-17/18/20, DS-21/22/24; corresponding twenty mean/interval/companion/count tokens. RE joins and actual reported-energy projection are missing. Existing extraction-report validation is not a producer of the renderer’s expected `reported_energy_cells`. |
| X6 — Former Table 3 decode row; P.3 magnitude, intervals, direction/Holm and signed clearance | wait_for | GAMMA after floors | Finalized manifest via `scripts/finalize_analysis_manifest.py`; `claim_verdicts.json` via `joulewise analyze-claims`; proposed `claim_side_bound.v1` sidecar; authenticated floor and floor acceptance. Registry DS-25–32. Analysis producer exists. CE candidate gate and sidecar validator exist, but sidecar contract/producer and registered issuance gate do not. Full table renderer is missing. |
| X7 — Former Table 3 prefill row and D-166 split refusal | wait_for | G2-a identity, ALPHA/BETA prefill floors, GAMMA | Same chain as X6 for `ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b`. Registry DS-33, PG-01/02/04–08. Missing guarded prefill token family, side-bound supplier, gate/verdict renderings and split-refusal integration. No PG-03 is implied: DS-33 owns that floor slot. |
| X8 — Repeated model-verdict sentences in paper-G A/B paragraphs | wait_for | Independently authenticated GAMMA verdicts | Repeat precisely the DS-32/PG-08 renderings in Abstract, Discussion and Conclusion. CE. No inference from DC branch A or B. On a ratio refusal, preserve independently valid model results in their table slots. Current skeleton/selector has no such placements. |
| X9 — P.4/P.9 empirical non-admission; paper-G “before comparison” refusal | wait_for | An actual affected production-window record | `<runs-root>/campaign_log.jsonl`, `whole-window-verdict.json`, prospective manifest and plan, with bracket/basis/member/model bindings. `scripts/run_campaign.py` and provenance validators exist. WW typed validation exists; F6 issuance and empirical non-admission renderer are missing. Registry OR-01; affected DS-32/PG-08 slots retain issued outcomes or the registered “not evaluated” wording. G2-a/G2-b diagnostic failures cannot stand in for a failed ALPHA/BETA/GAMMA comparison window. |
| X10 — Paper-G “at close-out” refusal, including zero denominator | wait_for | Authentic governing close-out evidence | DC source adapter/refusal vocabulary exists in `joulewise/dominance_closeout.py`, but the issuing gate explicitly does not license an empirical refusal for null branch. Registry OR-01. Need adopted refusal routing/renderer; an unreadable or missing source means unavailable evidence, not a fabricated issued reason. Two-stage precedence must remain explicit. |
| X11 — P.4 preservation, admission/accounting and P.8 archive statements | wait_for | Accumulates from G2-a through final close | Raw run bundles including telemetry, runtime/environment records and `instrument_calibration/`; campaign log, replacements/quarantine, frozen plan/receipt/policy, calibration acceptance, drift artifact, bracket binding, extraction specification, finalized manifest and claim verdicts. Existing collector/provenance/finalizer code supplies much of this chain. No single registry row covers a complete archive claim: add a successor archive census. WW/RE/CE/DC authenticate their own subsets, not the entire archive by implication. |
| X12 — Figure P1 and its four outcome descriptions | start_now | None for schematic; X6–X10 for empirical annotations | Existing `docs/paper/figures/fig3_decision_gates.svg`; no measured layout or numeric threshold. No standalone numbered P1 supplier row found; add an explicit schematic placement row. Refused / not resolvable / direction unresolved / directional claim remain four distinct meanings. A schematic is not evidence that any outcome occurred. |
| X13 — P.2 workload-response result or withdrawal | needs_ruling | Separate Window C selection and collection | `<runs_root>/characterization_result_report.json`, frozen `configs/campaigns/metrology_v1/characterization_result_schema_v1.json`, forty admitted bundles over five output lengths. Registry DS-02 and linearity tokens/outcome phrase. Specification exists; no `characterization_result` producer found in `scripts/` or `joulewise/`. None of the five closed custody families represents the complete characterization report. |
| X14 — P.2 identical-condition containment result; paper-G D prefix | needs_ruling | Separate, disjoint Window C blocks and earlier comparator floor | Same report, five disjoint A/B/B/A blocks per registered magnitude, each block interval, mean interval and maximum endpoint magnitude. Registry DS-03/null tokens. ALPHA/BETA floor-building nulls cannot double as this test. If uncollected, preserve the no-characterization prefix; D is not a fourth global outcome. Producer/custody route missing. |
| X15 — P.2 phase-accounting and drift/recovery results or withdrawals | needs_ruling | Separate Window C evidence | Same report: phase accounting needs 24 admitted bundles/two brackets; drift needs six designated references, three held-out probes and three sustained-work/cooldown pairs. Registry DS-05/06 and corresponding tokens. Ordinary window references may inform their owning window allowance but do not establish this separate report. Producer/custody route missing. |
| X16 — Optional characterization challenge and between-session statements | do_not_start | Explicit inclusion and respective design gates | DS-04 is the deliberate small-difference challenge; DS-07 is retired between-session stability. Neither may be silently restored through P.2 or reused historical Window C evidence. |
| X17 — P.5 measured dependence-sensitivity report | wait_for | Ten complete GAMMA blocks per contrast in collection order | `scripts/dependence_sensitivity.py` exists and emits JSON. Required inputs include authenticated deltas and metrology inputs; report independent, estimated-AR(1) and fixed effective-sample-size-halving calculations without changing membership. SYN-04 covers the illustration, not a measured sensitivity result. Add measured registry rows and an adopted custody route; the standalone calculator is not an issuing claim supplier. |
| X18 — P.6 reconstructed-versus-published floor statement | wait_for | Each actual submission floor and authenticated source corpus | `bind_v2_floor_artifact_evidence` exists in `joulewise/floor_mint_estimator.py`. Require source-member/width census, bracket/basis/estimator identity and pinned `joulewise.paper_floor_acceptance.v1` PASS. DC/CE require this acceptance. Publication writer/recording workflow and registry placement still need explicit ownership; binder existence is not evidence that the real recheck occurred. |
| X19 — P.2/P.3/P.5 synthetic illustrations and their pass/refusal sentences | start_now | None | P.2 null diagram and endpoint-weight illustration are inline synthetic data; P.3 floor composition uses SYN-02 and `worked-examples.json`; Student-t/Holm, 10-J geometry and P.5 illustration use SYN-04 and the dependence script. Retain separate illustrative datasets and synthetic labels. Add explicit rows for currently unnumbered P.2 illustrations if carried into the successor. No production capability or live window is needed. |
| X20 — P.7 transfer result/limitation | do_not_start | Separate prospectively fixed transfer design | Future transfer result, reviewed capture, plan, pre-data receipt, pulse-bound source and bundle inventory would require TP. Complete runnable protocol, acceptance and gate are absent. TR-01 is withdrawn as a result slot and now fixes the limitation sentence. Existing historical pulse bound is not transfer validation. |
| X21 — P.7 external-meter or replication result | do_not_start | Separate authorization, fixed load/synchronization/range and equipment | No issued meter result, registered paper result row or relevant custody family. The stated ratio design supplies no result. These studies are not dependencies of finishing the fixed-pair comparison. |
| X22 — P.10 availability and P.11 fresh-machine applicability | wait_for | Actual release checklist / actual machine admission | DS-34 remains stopped until repository revision, archive and fingerprint-manifest locators issue. Existing local custody paths are not public locators. P.11’s configured instrument/runtime/model/privilege/admission requirements must be demonstrated for collection; no result licenses another machine’s limits. |

For X4, the former Table 2 companion cells that are inapplicable should retain an explicit applicability disposition; they are not missing measurements to fill opportunistically.

**Desk seats.** Sizes below are bounded implementation increments, not acquisition estimates. `start_now` means a future scoped seat can begin; this read-only scout authorizes no writes.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| S1 — Successor placement/registry specification, medium | start_now | Lead adoption before active placement changes | Map X1–X22 to semantic locations; explicitly restore or replace retired rows; resolve floor-table, characterization and sensitivity custody routes. Own registry plus contract table and a table-agreement test. Preserve dated retirement history. |
| S2 — Reported-energy supplier, medium–large | start_now | Issuing values wait for ALPHA/BETA | Implement registered mean/interval/per-token/count projection from exact ordered members, strict bundles and frozen spec; authenticate all RE parents. Fixtures cover missing/duplicate members, wrong model/phase/prompt pin and interval/count mismatch. Do not weaken the closed extraction-report schema merely to satisfy the current renderer. |
| S3 — Claim-side-bound contract and producer, large; split at ruling | needs_ruling | Lead decides adopted bound semantics and explicit source-cell join | Candidate is `joulewise/analysis_engine/claim_side_bound.py`. Specify the paper quantity, provenance and relationship to deterministic interval widening; then implement producer, CE gate and mutations for reader digest, floor identity, cell join and arithmetic. Candidate validation alone cannot settle the contract. |
| S4 — WW/F6 empirical-refusal supplier, medium | start_now | Actual production evidence for issuance | Bind `authentic` separately from `admitted`, affected model/window, membership, basis and governing row. Emit only the fixed allowed non-admission sentence. Test authentic rejection versus unauthentic evidence, wrong-window substitution and unsupported reasons. Coordinate with OR-01 owner; no new stop-receipt family is implied. |
| S5 — Floor acceptance and D-165 projection, medium | start_now | S1 grant/placement choice; actual floor sources later | Prepare reproducible binder acceptance recording, source/width census, DC role templates and OB-01 projection. Test exact eight-plus-four ratio census, equality at two, zero denominator, missing ratio, stale acceptance and v1/v2 relabel separation. No production digest can be pinned before actual evidence exists. |
| S6 — Successor renderer and outcome selector, large; two increments | start_now | S1/S3 before issuing behavior | First specify typed token/placement contracts and non-issuing fixtures. Then implement two-phase comparison tables, repeated verdicts, D-166 split refusal and two-stage OR-01 precedence. Atomic failure must emit no partial paper prose. Test A/B/refusal combinations, unaffected verdict survival, floor equality, sign/Holm failures and Abstract ≤250 words. |
| S7 — Checklist and first-use migration, medium | start_now | Actual text substitution waits for live fill adjudication | Inventory stale anchors, rows and examples now; prepare current batch gates and first-use tests. Final substitution must cure the parked worklist, use a fresh successor copy and hash-bearing fill ledger, and retain historical replay fences. Do not mechanically run the parked retensing plan before data. |

## Critical path

The acquisition dependency remains:

**G2-a → authenticated selection/prompt pin → generated/reviewed v5 estate → G2-b + its readiness proof → ALPHA → BETA → real floor mint/reproduction gate → GAMMA → finalization and claim publication.**

The readiness scout’s historical checkout-routing finding must not be presented as an unchanged current defect: this head includes subsequent routing work. Pack-bound unattended readiness, actual machine state and quiet-window acceptance still belong to the acquisition lead. Nothing in this scout starts a measurement.

The publication dependency runs alongside acquisition:

**S1 placement/custody decisions + S2/S3/S4/S5 suppliers → S6 issuing renderer → actual production supply-map roles → real replay/acceptance → filled comparison paper.**

G2-a does not wait for the comparison renderer. Production rendering does wait for the actual artifacts. Window C characterization is a separate optional branch requiring a lead inclusion decision; it is not supplied by the ALPHA/BETA floor-building blocks.

Once comparison evidence exists, these fallback surfaces require coordinated changes:

- **Title, Abstract, Introduction and Conclusion:** replace the single historical-diagnostic headline with the licensed comparison result; keep historical observations labelled as historical. Outcome A/B describes the ratio hypothesis, while DS-32/PG-08 describe the model comparisons.
- **Methods and Results:** integrate the selected P.1/P.3/P.4 methods and new floor/comparison tables; keep P.2 prospective unless its separate evidence exists. Preserve Section 4’s historical diagnostic results as supporting evidence, not v5 parents.
- **Discussion and availability:** replace claims of an unperformed comparison only where authenticated results justify it. Update P.5/P.6 width-reproduction disclosures and P.8 archive inventory to state exactly what was checked. Preserve transfer, trusted-operator, dependence, fixed-prompt and counter-boundary limitations.
- **Selector and guides:** the current selector explicitly rejects A/B/REFUSAL and comparison material. `fill-rehearsal/branch-selection.md` still instructs those selections and requires withdrawn transfer slots. Replace that active guidance with the adopted successor contract; do not execute it as written.
- **Round-7 pedagogy:** rederive first-use locations across the assembled paper, using `round7/built-terms-lexicon.md`, `protocol/first-use-audit-ledger.md` and `tests/test_paper_first_use_ledger.py`. Build quantities before naming them; define operands, units, signs, sampling units and thresholds; explain every figure’s encodings and label synthetic examples. Moving prose changes first use, even when every paragraph was previously acceptable.
- **Parked sheets:** `retensing-plan.md` and `structural-edits.md` explicitly require campaign-fill adjudication of the parked worklist. They contain stale prompt-ensemble, transfer and physical-common-time wording. The current fixed-prompt-0 and D-165 addenda control.

**D-165 must retain its relabel boundary:** eight independent ratios plus four comparative diagnostics; equality at two passes; a required comparative ratio below two withdraws the dominance sentence. Compute ratios from complete **unguarded** bounds, before the sample multiplier and window allowance. Active replay is `d165_shared_sign_local_corner_replay.v2`: shared additive energy sign with independent local corners, **not proven robustness to common-time movement**. Absolute `R_cm` remains `not_applicable` because the replay is comparative-only. Preserve historical v1 bytes and meanings. Neither TERM A/B nor the planning sum F+B replaces these rules or the separate magnitude and direction gates.

No files changed. The fallback validator passed with a 246-word Abstract; HEAD and the clean worktree remained unchanged. The next exact lead step is to adopt S1’s successor placement/custody specification and rule S3’s sidecar semantics, while acquisition proceeds through its independently controlled G2-a gate.