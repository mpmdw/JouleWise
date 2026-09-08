```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Six copy-ready desk implementation briefs, collision scheduling, and two ruling packets prepared; no files changed.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "71588d6ab4e99bae3057e59463c27d2fe471dac7",
    "head_end": "71588d6ab4e99bae3057e59463c27d2fe471dac7",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row":"S1","action":"start_now","wait_for":[]},
      {"row":"S2","action":"start_now","wait_for":[]},
      {"row":"S4","action":"start_now","wait_for":[]},
      {"row":"S5","action":"start_now","wait_for":[]},
      {"row":"S6","action":"start_now","wait_for":[]},
      {"row":"S7","action":"start_now","wait_for":[]},
      {"row":"S3","action":"needs_ruling","wait_for":["Adopt claim-side quantity, producer semantics, and explicit source-cell join"]},
      {"row":"Characterization inclusion","action":"needs_ruling","wait_for":["Choose inclusion and custody route"]},
      {"row":"Issuing successor renderer","action":"wait_for","wait_for":["Adopted S1 placements","S3 ruling and implementation","Verified S2/S4/S5 supplier contracts"]},
      {"row":"Production role pinning and empirical fill","action":"wait_for","wait_for":["Actual authenticated artifacts","Lead publication acceptance","Adopted placements and issuing renderer"]},
      {"row":"Measurement collection in these seats","action":"do_not_start","wait_for":[]}
    ]
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
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","71588d6ab4e99bae3057e59463c27d2fe471dac7","e9318fdf5900270b234f6db7316d03c5b40d97dc"]},
      "expected":{"exit_code":0,"tail_regex":"71588d6ab4e99bae3057e59463c27d2fe471dac7\\ne9318fdf5900270b234f6db7316d03c5b40d97dc$"}
    },
    {
      "id":"V3",
      "kind":"inspection",
      "cmd":"ls configs/paper_supply/supply_map.json docs/paper/results-fill-registry.md joulewise/paper_custody.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["configs/paper_supply/supply_map.json","docs/paper/results-fill-registry.md","joulewise/paper_custody.py"]},
      "expected":{"exit_code":0,"tail_regex":"joulewise/paper_custody.py$"}
    }
  ],
  "flags": [
    {
      "id":"F1","kind":"baseline_drift","level":"nonblocking",
      "text":"The crosswalk records 1c83f2af48df5611c7bbf824bec818209c252d0d; this checkout is 71588d6ab4e99bae3057e59463c27d2fe471dac7. Brief evidence was inspected at the current checkout.",
      "needs":"Rebase and refresh line references before dispatch; do not reuse historical verification as current evidence."
    },
    {
      "id":"F2","kind":"lead_ruling","level":"nonblocking",
      "text":"S3 and characterization remain ruling-gated. S1 proposes placements without activating them. S2's reported-mean basis and fully composed interval remain explicitly undefined in the current registry.",
      "needs":"Adopt the relevant contracts before production gate registration; use the ruling packets below for S3 and characterization."
    },
    {
      "id":"F3","kind":"verification_gap","level":"nonblocking",
      "text":"Read-only inspection, ls path checks, and the fallback smoke check were performed. Proposed acceptance modules were not created or run; no suite, production issuance, or hardware validation was performed.",
      "needs":"Dispatch the bounded seats and replay their named acceptance modules."
    }
  ]
}
```

## Scheduling matrix

`start_now` means the bounded desk increment below. It does not authorize production issuance. All named existing repository paths were checked with `ls`; absent proposed paths are explicitly marked **NEW**. Test fixtures belong inline in the new test modules unless separately scoped.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| S1 | start_now | None for proposed placement specification; adoption before activation | Registry; custody contract |
| S2 | start_now | Contract adoption before an issuing energy gate | Supply map; registry; custody implementation/contract; rendering |
| S4 | start_now | Adopted fixed refusal rendering before issuance | Same shared files as S2 |
| S5 | start_now | S1 before floor-table grants; actual floors before publication acceptance | Same shared files as S2 |
| S6 | start_now | None for non-issuing contract increment; S1/S3 and suppliers before issuing follow-on | New contract and test only |
| S7 | start_now | S1/S6 before final migration reconciliation; live adjudication before substitution | Checklist, active guide, new inventory/test |
| S3 | needs_ruling | Quantity semantics and source-cell join | Future scope must be issued after ruling |
| Characterization | needs_ruling | Inclusion and custody-family decision | Future scope must be issued after ruling |

Collision matrix for the **exact scopes below**:

| Shared file | S1 | S2 | S4 | S5 | S6 | S7 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `configs/paper_supply/supply_map.json` | — | W | W | W | — | — |
| `docs/paper/results-fill-registry.md` | W | W | W | W | — | — |
| `joulewise/paper_custody.py` | — | W | W | W | — | — |
| `docs/contracts/paper_supply_custody.md` | W | W | W | W | — | — |
| `joulewise/paper_rendering.py` | — | W | W | W | — | — |

Serialize S1/S2/S4/S5 integration. In particular, **S2, S4, and S5 must not concurrently edit or repin the shared custody/map/rendering surfaces**. S6 and S7 can begin independent inventories, but must consume the adopted predecessor contracts before closure.

## Critical path

Recommended order: **S1 → S2 → S4 → S5 → reconcile S6 → reconcile S7**. Prepare the S3 and characterization rulings alongside S1.

Cross-row dependencies:

- S1 adoption fixes the placements and grants consumed by S2/S4/S5 and the issuing S6 follow-on.
- S3 ruling and implementation block claim-bearing S6 behavior, not S6’s non-issuing specification.
- S2/S4/S5 establish supplier outputs that S6 must compose without inventing evidence.
- S7’s final migration inventory consumes S1 placements and S6’s token/branch contract.
- Characterization adds a separate branch only if included; it must not silently become a comparison prerequisite.
- Actual authenticated evidence and lead publication acceptance precede production map pinning and empirical fill.

## BRIEF S1

**GENRE:** implementation  
**Mission:** Produce the proposed successor placement and custody specification for crosswalk obligations X1–X22, with executable table-agreement checks. Preserve current fallback behavior pending lead adoption.

**Forcing problem:** `docs/contracts/paper_supply_custody.md:101` requires every claim-bearing placement to have an explicit family/role binding, while its current table grants no comparison placements. `docs/paper/results-fill-registry.md:970` retains retired successor outcome slots. Their existence does not authorize reactivation.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_comparison_placements.md",
  "docs/contracts/paper_supply_custody.md",
  "docs/paper/results-fill-registry.md",
  "tests/test_paper_comparison_placements.py"
]
```

**NEW:** `docs/contracts/paper_comparison_placements.md`; `tests/test_paper_comparison_placements.py`.

**Deliverables and regressions:**

- A proposed placement table covering every X1–X22 obligation: semantic location, exact token/site identity, artifact field, family/role, required grant, applicability, missing-evidence behavior, and adoption status. Distinguish synthetic/schematic material from empirical placements.
- Explicitly mark floor-cell, measured-dependence, and characterization routes unresolved where no adopted family/grant exists. Do not invent a sixth family or infer grants from a related authenticated artifact.
- Add proposed successor rows alongside preserved dated retirement history. Keep proposals non-fillable until adoption; separate proposal tables from the live custody-bound census.
- Agreement regressions reject a missing obligation, duplicate placement, mismatched family/role, retired row treated as active, or empirical row with only a synthetic supplier. **Counterfactual:** deleting one obligation or changing one supplier in only one table must fail; the current retired rows must remain non-fillable.
- Include explicit schematic and synthetic dispositions for P1 and the P.2 illustrations, plus archive and availability obligations that cannot be licensed by a partial family census.

**Acceptance — named modules only:** `tests.test_paper_comparison_placements`.

**Constraints:** D-173: every empirical supplier obtains evidence through `open_paper_input`; this seat grants no production authority. Do not modify frozen measurement inputs or current paper text. No measurement collection, repository-wide suite, or git commit. Do not expand scope for bookkeeping. Return `NEEDS_RULING` for unresolved authority and `NEEDS_SCOPE` for necessary unlisted writes.

**Return contract:** First fenced JSON object: `schema="claude-codex-report/v1"`, `genre="implementation"`, UTF-8 size **<8192 bytes**. Use `verdict.implementation=implemented|partial|no_change` and `verdict.acceptance=ready|pending_verification|needs_ruling`; report actual changed paths, verification, and flags. Contract preparation can be complete while adoption remains pending.

## BRIEF S2

**GENRE:** implementation  
**Mission:** Build the reported-energy supplier’s bounded schema/projection increment and adversarial synthetic tests; make unresolved statistical choices explicit before registering an issuing gate.

**Forcing problem:** `joulewise/paper_rendering.py:41` expects `extraction_report.reported_energy_cells`, but `docs/paper/results-fill-registry.md:368` explicitly says the reported-mean schema, admitted member basis, composed intervals, and per-token fields remain undefined. `docs/contracts/paper_supply_custody.md:283` requires exact ordered members and all strict-bundle inputs.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_reported_energy.md",
  "docs/contracts/paper_supply_custody.md",
  "docs/paper/results-fill-registry.md",
  "configs/paper_supply/supply_map.json",
  "joulewise/paper_reported_energy.py",
  "joulewise/paper_custody.py",
  "joulewise/paper_rendering.py",
  "tests/test_paper_reported_energy.py"
]
```

**NEW:** `docs/contracts/paper_reported_energy.md`; `joulewise/paper_reported_energy.py`; `tests/test_paper_reported_energy.py`.

**Deliverables and regressions:**

- A proposed closed projection contract for the four model/phase cells and their twenty mean/endpoint/per-token/count outputs. Identify exact ordered membership, energy boundary, interval construction, and observed-token denominator.
- Implement independently settled identity, census, shape, and provenance checks now. If the owning contracts do not uniquely determine the mean basis, interval composition, or per-token aggregation, return a bounded `NEEDS_RULING` with alternatives; do not choose these by convenience.
- Keep the existing closed mint-consumption report schema intact. Use a distinct projection rather than inserting an invented field into an authenticated report.
- Authenticate selection/prompt pin, model, phase, frozen extraction specification, whole-window basis, and every strict member through the existing custody flow. Include new validators in the transitive source census.
- Mutation regressions: omitted/duplicated/reordered member, swapped model/phase, stale prompt pin, incorrect interval endpoint, fabricated token denominator, and count copied from a floor component. **Counterfactual:** each individually corrupted input must refuse even when its mean looks plausible; a complete synthetic control must produce the independently calculated projection.
- Preserve fixture roles as non-issuing. Map edits may document pending roles; do not add invented production digests or register the production energy gate before contract adoption.

**Acceptance — named modules only:** `tests.test_paper_reported_energy`.

**Constraints:** All paper evidence enters through `open_paper_input`; callers supply no evidence dict/path/digest bypass. No frozen measurement-input changes, collection, repository-wide suite, or git commit. Synthetic tests confer no production acceptance. No out-of-scope bookkeeping; use scope/ruling early returns when needed.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; `verdict.implementation=implemented|partial|no_change`, `verdict.acceptance=ready|pending_verification|needs_ruling`. Enumerate unresolved semantic fields rather than claiming an issuing supplier is complete.

## BRIEF S4

**GENRE:** implementation  
**Mission:** Implement the authenticated whole-window non-admission supplier increment, preserving authenticity separately from admission and binding any empirical refusal to the affected production window.

**Forcing problem:** `joulewise/whole_window.py:85` exposes distinct `authentic` and `admitted` fields. `joulewise/paper_custody.py:499` permits only the positive whole-window grant; F6 is absent. `joulewise/paper_rendering.py:54` renders only “admitted.” `docs/paper/results-fill-registry.md:984` requires model/window-specific two-stage refusal handling.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_whole_window_refusal.md",
  "docs/contracts/paper_supply_custody.md",
  "docs/paper/results-fill-registry.md",
  "configs/paper_supply/supply_map.json",
  "joulewise/paper_whole_window_refusal.py",
  "joulewise/paper_custody.py",
  "joulewise/paper_rendering.py",
  "tests/test_paper_whole_window_refusal.py"
]
```

**NEW:** `docs/contracts/paper_whole_window_refusal.md`; `joulewise/paper_whole_window_refusal.py`; `tests/test_paper_whole_window_refusal.py`.

**Deliverables and regressions:**

- Preserve the typed whole-window validation result through custody replay. An authentic rejection can support non-admission; unauthentic evidence supports only unavailable/invalid evidence handling.
- Bind campaign/plan, production-window identity, affected model, ordered membership, bracket, and basis before issuing any refusal grant. G2-a/G2-b diagnostic failures cannot substitute for ALPHA/BETA/GAMMA failures.
- Specify a closed mapping from supported governing reasons to exact reader-facing text and the `before comparison` stage. Reuse adopted wording where available; submit missing wording/grant choices for adoption before enabling F6.
- Keep `at close-out` routing with the D-165 owner. Do not turn a custody exception into an empirical reason or introduce a stop-receipt family.
- Regressions cover authentic rejection, authentic admission, unauthentic rejection-looking bytes, wrong-window/model substitution, missing member/basis binding, unsupported reason, and competing stages. **Counterfactual:** collapsing validation to an empty diagnostic list, accepting a diagnostic window, or bypassing reason membership must make a test fail.
- Use non-issuing synthetic controls now; production map entries and F6 activation wait for adopted contract and real evidence.

**Acceptance — named modules only:** `tests.test_paper_whole_window_refusal`.

**Constraints:** D-173 `open_paper_input` is the only paper evidence entry; maintain source census, replay, and reopen protections. No frozen measurement-input changes, collection, repository-wide suite, or git commit. No unlisted bookkeeping. Missing authority or scope requires the corresponding early return.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; implementation verdict `implemented|partial|no_change`, acceptance verdict `ready|pending_verification|needs_ruling`. Distinguish implemented validation from enabled production issuance.

## BRIEF S5

**GENRE:** implementation  
**Mission:** Prepare reproducible floor-acceptance recording and the D-165 paper projection, including exhaustive failed-component output, without issuing acceptance for uncollected floors.

**Forcing problem:** `docs/contracts/paper_supply_custody.md:319` requires a pinned PASS record tied to actual floor/source/binder/anchor identities. The existing binder begins at `joulewise/floor_mint_estimator.py:598`. `joulewise/paper_rendering.py:50` returns only the branch, while `docs/paper/results-fill-registry.md:982` requires the complete OB-01 failed-component list.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_supply_custody.md",
  "docs/contracts/d165_dominance_closeout.md",
  "docs/paper/results-fill-registry.md",
  "configs/paper_supply/supply_map.json",
  "joulewise/paper_floor_publication.py",
  "scripts/record_paper_floor_acceptance.py",
  "joulewise/paper_custody.py",
  "joulewise/paper_rendering.py",
  "tests/test_paper_floor_publication.py"
]
```

**NEW:** `joulewise/paper_floor_publication.py`; `scripts/record_paper_floor_acceptance.py`; `tests/test_paper_floor_publication.py`.

**Deliverables and regressions:**

- A recording workflow wrapping the existing authenticated binder and preserving its result. Record the exact acceptance schema, floor digest, sorted unique source census, binder-source digest, valid preceding anchor, and PASS only after successful reproduction.
- Preserve the distinction between acceptance preparation and paper consumption: acceptance is a prerequisite established by the lead’s binder workflow; paper projection subsequently calls `open_paper_input`. Do not create a circular “open DC to manufacture its own acceptance” path or an acceptance callback that grants issuance.
- D-165 projection emits A/B disposition and every failed independent/comparative component for OB-01. Preserve eight independent ratios, four comparative ratios, four absolute `not_applicable` dispositions, and equality-at-two passage.
- Ratios use complete unguarded bounds before multiplier/allowance. Preserve v1 history and v2 shared-energy-sign/local-corner meaning; do not claim common-time robustness.
- Mutate missing/duplicate ratios, equality versus just-below-two, zero denominator, omitted failed component, stale acceptance, missing source, wrong binder digest, and v1 relabeled as v2. **Counterfactual:** accepting incomplete census, granting dominance from B, or printing only the first failure must fail a regression.
- Branch-null refusal remains non-issuing until its route is adopted. Standalone floor-table output remains blocked on S1’s explicit grant. Map preparation must contain no fabricated production digest.

**Acceptance — named modules only:** `tests.test_paper_floor_publication`.

**Constraints:** Every claim-bearing paper projection uses D-173 `open_paper_input`; retain existing binder authentication. No frozen-input edits or real acceptance issuance in this seat. No collection, repository-wide suite, or git commit. Return scope/ruling early requests for anything outside the allowlist or adopted semantics.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; `verdict.implementation=implemented|partial|no_change`, `verdict.acceptance=ready|pending_verification|needs_ruling`. Report synthetic verification separately from the pending actual-floor gate.

## BRIEF S6

**GENRE:** implementation  
**Mission:** Implement the first S6 increment: a typed successor rendering contract and executable non-issuing scenario fixtures. The issuing renderer is a separately scoped follow-on after S1/S3 and supplier adoption.

**Forcing problem:** `docs/paper/fill-rehearsal/select_outcome_branches.py:14` accepts only `METHODS_DIAGNOSTIC`, while `docs/paper/fill-rehearsal/branch-selection.md:3` describes nonexistent active A/B/REFUSAL groups. `joulewise/paper_rendering.py:41` and `:60` expose only partial cell/verdict projections.

**WRITE_SCOPE:**
```json
[
  "docs/contracts/paper_comparison_rendering.md",
  "tests/test_paper_comparison_contract.py"
]
```

**NEW:** Both paths.

**Deliverables and regressions:**

- Specify typed inputs and placement/token contracts for floor cells, decode and prefill comparisons, repeated model verdicts, ratio A/B disposition, D-166 split refusal, characterization prefix, and two-stage OR-01 precedence.
- Mark S1 placement decisions and S3 quantity semantics as dependencies; unresolved fields remain explicitly unbound. Never infer model verdicts from ratio A/B.
- Encode a scenario matrix with non-issuing expected outputs: A and B crossed with independently valid model outcomes; production-window non-admission; close-out refusal; unavailable evidence; prefill-only refusal; unaffected decode survival; conflicting stages.
- Specify transactional behavior: validate all required inputs before writing output; unexpected failure emits no partial paper prose. A licensed result surviving an unrelated refusal must be distinguished from an incomplete write.
- Include strict magnitude equality, sign disagreement, Holm failure, exact repeated-verdict consistency, and Abstract ≤250-word cases.
- **Counterfactuals:** ratio A forcing a directional model claim, missing evidence becoming an issued refusal, loss of unaffected decode results, conflicting repeated verdicts, a 251-word Abstract, or partial emission after a late failure must each invalidate a fixture.
- Fixtures remain synthetic and cannot obtain production capabilities. Leave the current selector and skeleton unchanged; supply an explicit list of requirements for the later issuing implementation.

**Acceptance — named modules only:** `tests.test_paper_comparison_contract`.

**Constraints:** The contract requires all eventual empirical suppliers to call D-173 `open_paper_input`. No production gate registration, frozen measurement-input changes, paper fill, collection, repository-wide suite, or git commit. No extra writes for bookkeeping. Escalate authority/scope gaps rather than encoding guesses.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; implementation `implemented|partial|no_change`, acceptance `ready|pending_verification|needs_ruling`. “Implemented” here refers only to this contract/fixture increment.

## BRIEF S7

**GENRE:** implementation  
**Mission:** Prepare the successor fill/migration inventory and current operating guidance, with first-use regression checks, without applying parked substitutions.

**Forcing problem:** `docs/paper/round7/fill-checklist.md:3` requires a fresh working copy and hash-bearing ledger. `docs/paper/round7/structural-edits.md:3` parks substitutions until live campaign-fill adjudication. `docs/paper/fill-rehearsal/branch-selection.md:29` advertises outcomes rejected by the current selector.

**WRITE_SCOPE:**
```json
[
  "docs/paper/round7/fill-checklist.md",
  "docs/paper/fill-rehearsal/branch-selection.md",
  "docs/paper/round7/successor-migration-inventory.md",
  "tests/test_paper_successor_migration.py"
]
```

**NEW:** `docs/paper/round7/successor-migration-inventory.md`; `tests/test_paper_successor_migration.py`.

**Deliverables and regressions:**

- Correct active instructions to describe the current methods/diagnostic selector. Label successor operations as pending adopted S1/S6 contracts.
- Inventory stale anchors, retired rows, transfer slots, prompt-ensemble assumptions, and common-time wording in the parked sheets. Record current semantic targets and required adjudications; do not edit or mechanically apply those sheets.
- Define future batch gates: fresh successor copy, complete supplier/placement checks, input/output hashes and replacement ledger, preserved historical replay fences, then assembled-paper first-use and Abstract checks.
- Use `docs/paper/round7/built-terms-lexicon.md` and `docs/paper/protocol/first-use-audit-ledger.md` as read-only sources for relocated first uses. Inventory operands, units, signs, sampling units, thresholds, figure encodings, and synthetic labels.
- Regressions reject active instructions to select A/B/REFUSAL today, fill retired rows, edit the frozen draft, bypass the ledger, or treat prospective counts as observed.
- A small synthetic relocation case must put a technical term before its construction and fail; its corrected control must pass. **Counterfactual:** checking only the old paragraph location or mechanically approving the parked sheet must not satisfy the migration check.
- Reconcile the inventory with adopted S1/S6 outputs before final closure; keep real text substitution explicitly pending live fill adjudication.

**Acceptance — named modules only:** `tests.test_paper_successor_migration`.

**Constraints:** D-173 `open_paper_input` remains mandatory for eventual empirical suppliers. No frozen-input or paper-text edits, measurement collection, repository-wide suite, or git commit. Preserve historical evidence and replay requirements; do not run external-corpus replay as this desk acceptance. Use scope/ruling early returns for unresolved work.

**Return contract:** First fenced `claude-codex-report/v1` JSON, `genre="implementation"`, **<8192 UTF-8 bytes**; `verdict.implementation=implemented|partial|no_change`, `verdict.acceptance=ready|pending_verification|needs_ruling`. State that migration preparation does not constitute empirical fill.

## Ruling packet — S3

**Question:** What exact paper quantity does `claim_side_bound_j` denote, how is it derived from the estimator’s deterministic terms, and which prospectively registered source-cell join licenses each contrast?

**Evidence:**

- `joulewise/analysis_engine/claim_side_bound.py:1`: the wire is expressly a non-issuing scaffold.
- `joulewise/analysis_engine/claim_side_bound.py:48`: source cells must equal explicit manifest registration; missing registration refuses.
- `joulewise/analysis_engine/claim_side_bound.py:57`: candidate arithmetic symmetrically expands the metrology-aware interval.
- `joulewise/analysis_engine/estimators.py:141`: paired estimates distinguish stochastic/deterministic layers and expose deterministic total plus decision interval.
- `docs/contracts/paper_supply_custody.md:302`: candidate validation is not an adopted producer contract; the CE gate remains unregistered.

**Options and failures avoided:**

| Option | Decision required | Failure avoided |
|---|---|---|
| A — Adopt the candidate scalar wire | Prove the scalar equals the relevant existing deterministic total, with exact units, composition, and ordered cell join | A sidecar whose arithmetic passes but whose quantity is unrelated to the actual claim decision |
| B — Adopt a richer component/endpoints wire | Specify named contributions or endpoint treatment and derive displayed totals from them | Loss of necessary provenance or unjustified symmetric widening |
| C — Defer the side-bound display | Keep affected claim placements stopped pending a complete contract | Shipping plausible but unlicensed numbers |

**Recommendation:** Gate A on an explicit estimator-to-sidecar derivation. If equality and provenance cannot be demonstrated, choose B. C is the safe interim disposition; candidate validation alone cannot decide between A and B.

**Cold-gate decision fields:**

- Adopted quantity/formula and authoritative producer:
- Relationship to stochastic interval and already-applied deterministic widening:
- Exact contrast → ordered source-cell registration authority:
- Serialization/version and arithmetic tolerances:
- Required floor/reader/manifest/acceptance bindings:
- Mutation cases proving no omitted term, double widening, or guessed join:
- Approved implementation scope and clause-to-test map:

**Blocked work:** S3 producer, CE gate registration, and claim-bearing S6 output. No frozen manifest/schema is modified by this packet.

## Ruling packet — Characterization inclusion

**Question:** Does the successor include empirical Window C characterization, and, if so, what closed custody route authenticates its complete report and prospectively selected comparator mode?

**Evidence:**

- `docs/paper/protocol/prospective-comparison-protocol.md:56`: characterization is a separate instrument question.
- `docs/paper/protocol/prospective-comparison-protocol.md:77`: floor-building blocks cannot double as disjoint characterization evidence.
- `docs/paper/protocol/prospective-comparison-protocol.md:176`: registered member/block counts are design requirements, not collected counts.
- `configs/campaigns/metrology_v1/characterization_result_schema_v1.json:2`: predecessor-linked reports and anti-selection requirements.
- `configs/campaigns/metrology_v1/characterization_result_schema_v1.json:6`: comparator choice is fixed at freeze; issued-floor mode and held-out train/test mode have different evidence requirements.
- `docs/contracts/paper_supply_custody.md:66`: the closed public family set has no complete characterization-report family.
- `docs/paper/results-fill-registry.md:883`: DS-02/03 are retired; `:893` likewise retires DS-05/06.

**Options and failures avoided:**

| Option | Decision required | Failure avoided |
|---|---|---|
| A — Omit empirical characterization | Retain prospective methods and explicit uncollected disposition | An optional separate campaign becoming an implicit comparison dependency |
| B — Include through a dedicated closed family | Adopt producer, report census, comparator registration, grants, and successor placements | Treating partial floor/claim custody as authentication of a complete characterization report |
| C — Include through an explicitly extended existing family | Demonstrate complete semantic fit and add all parents/replay/grants prospectively | Family proliferation, while requiring proof against incomplete custody |

**Recommendation:** A unless the lead explicitly wants the separate empirical campaign. If included, prefer B unless C can demonstrate complete report coverage. Preserve the frozen comparator-mode predicate; do not silently require only an earlier issued floor or silently select held-out mode after outcomes.

**Cold-gate decision fields:**

- Included characterization questions and explicit exclusions:
- Selected custody family and producer owner:
- Prospectively frozen comparator mode and disjointness proof:
- Member census, predecessor/report publication, and anti-selection obligations:
- Withdrawal and no-characterization wording:
- Adopted placements/grants and implementation scope:
- Separate acquisition gate and clause-to-test map:

**Blocked work:** Characterization producer/custody implementation and empirical placements. The six desk briefs remain independently actionable within their stated boundaries.