# WO-MINT-ESTIMATOR-VOCAB implementation — three-site spec-authoritative estimator dispatch (CONSULT DESIGN ADOPTED)

WRITE_SCOPE: ["joulewise/floor_mint_estimator.py", "scripts/mint_floor_artifact_generalized.py", "tests/test_floor_mint_estimator.py", "tests/test_mint_floor_artifact_generalized.py", "docs/decision_log.md"]

Branch impl/floor-commonmode-01 at HEAD (this worktree; stacked on the
landed FCM rounds). Implement the adopted consult design EXACTLY (the
full consult text is appended below the divider — it is the contract;
NEEDS_RULING for anything it does not settle).

Non-negotiables restated:
1. NEW shared module joulewise/floor_mint_estimator.py: per-cell
   estimator dispatch whose SOLE authority is the committed pre-registered
   extraction spec (never report/artifact data — ALT-D120 invariant);
   selects between the worst-case default core computation and the
   governed two-shared-edge extraction-path computation.
2. The generalized mint consumes the dispatch at ALL THREE sites:
   postcollection equality (steps 8-9), artifact construction, and final
   evidence binding. NO site may retain an unconditional default-core
   recomputation. The consult's named failure mode (steps 8-9-only patch)
   is the thing your tests must prove absent.
3. The mint still RECOMPUTES the floor itself from authenticated members
   under the dispatched estimator and refuses on any mismatch with the
   report's cached value — never trust the report's number.
4. UNCHANGED: scripts/mint_floor_artifact.py (pinned core),
   scripts/floor_mint_pinsets/schema_v2.json, report/artifact schemas,
   production extraction specs (the pack re-spec is a separate D-133
   consumption step).
5. Committed regressions for every consult attack class: spec-swap,
   estimator-mismatch between spec and report, default/registered
   cross-wiring at EACH of the three sites (three distinct regressions —
   one per site, each demonstrated failing against a deliberately
   site-limited implementation variant or the pre-WO code), equality-check
   bypass, and a full mint run on a synthetic common-mode cell producing
   a bound artifact whose floor equals the extraction path's exact value.
6. Proofs: focused matrices (test_floor_mint_estimator,
   test_mint_floor_artifact_generalized, test_floor_extraction,
   test_detection_floor) AND the full canonical suite
   (python3 -m unittest discover -s tests) on python3 AND python3.11,
   exact counts pasted. Append the WO note to docs/decision_log.md's
   D-124/D-133 chain. Leave uncommitted; claude-codex-report/v1, genre
   implementation.

--- ADOPTED CONSULT (verbatim) ---
```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "The mint needs one spec-authoritative per-cell estimator dispatch shared by postcollection equality, construction, and final evidence binding; fixing steps 8-9 alone leaves a second default-core recomputation and a default-only binder.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "f0e7cf6084ce997bded95845d0df8a98d534cf2d",
    "head_end": "f0e7cf6084ce997bded95845d0df8a98d534cf2d",
    "upstream_end": "f0e7cf6084ce997bded95845d0df8a98d534cf2d",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {
        "row": "FCM-01 ALT-D120",
        "action": "wait_for",
        "wait_for": "ALT-D120 plus the full fresh arithmetic delta to land clean",
        "collision_surface": "floor_extraction and common-mode arithmetic"
      },
      {
        "row": "WO-MINT-ESTIMATOR-VOCAB implementation",
        "action": "wait_for",
        "wait_for": "FCM-01 prerequisite above",
        "collision_surface": "generalized mint, v2 binding, and U10 tests"
      },
      {
        "row": "D-118/D-121 merge gate",
        "action": "wait_for",
        "wait_for": "exact implementation head and committed attack regressions",
        "collision_surface": "all fixes retrigger delta and terminal final-head review"
      },
      {
        "row": "Pack re-spec to common mode",
        "action": "wait_for",
        "wait_for": "FCM-01, mint vocabulary, and their complete gates",
        "collision_surface": "D-117 pack freeze and U10 postcollection literals"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code && test -z \"$(git status --porcelain=v1)\" && git rev-parse HEAD && git rev-parse origin/main && git rev-parse impl/floor-commonmode-01 && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "f0e7cf6084ce997bded95845d0df8a98d534cf2d",
          "f0e7cf6084ce997bded95845d0df8a98d534cf2d",
          "4f041008297b62596e726e14e614a105837df5ca",
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
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 0,
        "tail": [
          "Not run: read-only scout with no repository changes."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The final evidence binder independently hard-codes default comparative widths, creating a third common-mode choke point after the two visible recomputations.",
      "needs": "Implement and regress an estimator-aware v2 binder; do not bypass binding."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No tests were run because this session was explicitly read-only design work.",
      "needs": "Run focused tests and the canonical suite on the authorized implementation head."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| FCM-01 ALT-D120 | wait_for | Full fresh delta clean and merge | `floor_extraction` arithmetic/API |
| Mint estimator adapter | wait_for | FCM-01 | Generalized mint steps 8–11 |
| D-118/D-121 gate | wait_for | Exact implementation head | Fix/delta/final-head sequencing |
| Pack re-spec | wait_for | Both gated units | D-117 freeze and U10 literals |

## Critical path

FCM-01 ALT-D120 + clean full delta → estimator-aware generalized mint → D-118 items 1–11 and D-121 terminal review → pack re-spec/common-mode U10 closure. Ed’s D-133 schedule ruling determines whether that chain blocks the freeze wave.

## 1. MAP — current recomputation and pinning path

### Authentication and spec binding

1. `scripts/mint_floor_artifact_generalized.py:1289-1326` authenticates the exact pinset bytes against the supplied SHA-256, rejects duplicate/nonfinite JSON, and selects the closed v2 schema.

2. The v2 schema pins the producer extraction-spec SHA/member count at `:731-740`. Each component repeats those pins, and `:842-852` requires exact agreement with its producer. There is currently no estimator field in the pinset schema.

3. `_authenticate_v2_inputs` loads each input spec and invokes the configured pinned core at `:3438-3476`.

4. The pinned core loads report and spec bytes independently at `scripts/mint_floor_artifact.py:1078-1080`, validates the spec and selects the corresponding spec/report cells at `:1096-1105`, authenticates report membership against the spec, verifies bundles at `:1139-1158`, and rederives the whole-window allowance at `:1164-1252`.

5. The resulting `AuthenticatedComponent` records the exact report and spec byte hashes at `:1255-1275`. The v2 component gate then checks the spec SHA, order-manifest SHA, counts, semantics, and exact member/config sequence at `scripts/mint_floor_artifact_generalized.py:1810-1862`.

Current ordering is slightly wrong for the new authority boundary: `_build_v2_artifacts` calls postcollection recomputation before `_v2_gate_component` at `:2717-2742`. The estimator design should reverse that order so no estimator executes before its spec and member pins pass.

### Every default comparative computation

There are three separate default-only surfaces:

- The pinned core’s normal construction computes ABBA blocks and calls `comparative_false_effect_floor` at `scripts/mint_floor_artifact.py:1474-1513` and `:1575-1585`.

- V2 steps 8–9 independently repeat that default computation at `scripts/mint_floor_artifact_generalized.py:2282-2307`.

- V2 construction repeats it again at `:2569-2579`.

There is also a fourth default assumption during evidence binding: `scripts/mint_floor_artifact.py:1917-1940` reconstructs comparative widths exclusively as `(wA1+wB1+wB2+wA2)/2`. The generalized mint invokes that binder at `scripts/mint_floor_artifact_generalized.py:3672-3684`. A common-mode artifact would therefore remain unmintable even after fixing steps 8–9 and construction.

### Equality and U10

The report-cache equality is exact in decimal text space:

- Recomputed absolute/comparative values are obtained at `scripts/mint_floor_artifact_generalized.py:2308-2318`.
- Both `cell.floor.drift_widened_guarded_floor_j` and `cell.operative_floor_j` must exactly equal the recomputation at `:2319-2344`.

The domain-owned U10 projection is built at `:2346-2396`. Its exact comparison covers:

- pre/post receipt and content digests;
- bracket-binding and terminal-ledger-head hashes;
- observed drift, allowance rule/screen/value, and embedding count;
- absolute/comparative evaluation-basis SHA/count;
- extraction-report SHA;
- absolute, comparative, and operative full-precision values;
- all three six-decimal renderings.

Every field is compared at `:2398-2431`; there is no fill/default route.

`extraction_report_sha256` is the SHA of the exact report bytes captured by the core. Both components must identify one report at `:2276-2280`, and that hash enters the U10 projection at `:2374`. It pins the whole closed-profile report byte stream, including members and cached numbers. It does not make the report an arithmetic authority: steps 8–9 still have to reproduce the numbers from authenticated evidence.

The extraction spec is separately authenticated by `spec_sha256`; that is the existing commitment capable of governing estimator selection.

### FCM branch arithmetic and vocabulary boundary

At `impl/floor-commonmode-01@4f04100`:

- `joulewise/floor_extraction.py:1093-1173` validates the spec-only estimator declaration, registration, and calibration basis.
- `extract_cells` passes those spec fields to `extract_comparative_cell` at `:2696-2717`.
- `extract_comparative_cell` chooses default versus common mode at `:2391-2442`, derives common-mode block inputs from bundle evidence at `:2540-2558`, and never falls back after a registered-path refusal.
- Raw trace curves, windows, residuals, and sweep candidates are independently derived by `_common_mode_block_inputs_from_evidence` at `:2152-2344`.
- `_common_mode_floor_from_extracted_inputs` owns the registered arithmetic at `:485-623`.
- `CellReport.as_row` emits no estimator identity at `:1291-1396`.
- The admitted report profile contains no estimator vocabulary at `:1410-1476` and recursively refuses `estimator_registration` at `:1539-1552`.
- `joulewise/detection_floor.py:4088-4115` similarly refuses registration vocabulary anywhere in an artifact.

## 2. DESIGN — minimal governed extension

### Authority rule

Do not add estimator fields to the v2 pinset, extraction report, floor artifact, or artifact provenance.

The selector is exactly `AuthenticatedComponent.spec_cell["estimator"]`, whose enclosing spec bytes already have:

- exact input authentication;
- component and producer SHA pins;
- membership/config/order pins;
- U10-era source ownership.

The extraction-spec SHA carried through component provenance is the durable indirect commitment. The declared registration authorizes a code path; it is never copied out as claimed provenance.

Selection must be per comparative cell:

- absent or `d054_false_effect_guard.v1` → pinned default core;
- `d124_two_shared_edge_common_mode.v1` → common-mode path only;
- anything else → refusal;
- pending candidate registration → refusal at mint time;
- malformed full registration or calibration basis → refusal, never default fallback.

For common mode, require the spec registration to equal the canonical branch registration exactly, including parameter SHA. Its `calibration_basis` must match the authenticated producer acceptance identity, artifact SHA, derivation SHA/schema, `max(observed_drift_s,0.010818)`, embedding count `1`, and componentwise-max rule. Numeric provenance is rederived from the acceptance, ledger, bracket binding, members, and traces.

### Implementation shape

Add a narrow shared adapter, proposed as `joulewise/floor_mint_estimator.py`. Do not move or copy the FCM arithmetic.

Its public surface should be limited to:

- `selection_from_authenticated_spec(...)`
- `recompute_comparative_estimate(...)`
- `bind_v2_floor_artifact_evidence(...)`

The adapter should call the FCM branch’s existing block-input builder and `_common_mode_floor_from_block_inputs`; it should assert their signatures and the canonical parameter SHA before use.

In `scripts/mint_floor_artifact_generalized.py`:

1. Run both `_v2_gate_component` checks and `_v2_gate_producer_inventory` before estimator selection.

2. For a common-mode cell, build a fresh `AuthenticatedConsumptionSession` from the authenticated evidence root, full spec membership, evaluation-basis SHA, pinned consumption semantics, authenticated ledger snapshot, and bracket binding. Require it to be ready and take its rederived full calibration bracket. Never use report-carried provenance as the bracket.

3. Build ABBA deltas from `AuthenticatedComponent.members` plus `spec_cell["blocks"]`. The spec must flatten to exactly the authenticated member sequence.

4. Under the active `V2AuthenticationReadSession`, re-read raw trace/window/clock evidence through the FCM block-input builder. Repeated authentication reads must resolve to the same first-seen file digests.

5. Dispatch:

   - default: use the existing core call unchanged;
   - common mode: use the FCM internal arithmetic with the authenticated bracket and once-widened operative bound.

6. Build one frozen in-memory `V2CellRecomputation` containing the estimator path, comparative blocks, estimate, exact widths, and comparative record. The estimator path is internal metadata and must never serialize.

7. Steps 8–10 compare the report and U10 values against this recomputation. `_v2_gate_postcollection` should return the frozen object.

8. `_mint_v2_cell_artifact` must consume that same object instead of recomputing with the default core. This removes gate/construction cross-wiring.

9. Replace the v2 call to the pinned binder with the estimator-aware shared binder. It must preserve every current check—plan, campaign log, bundle hashes, config hashes, stack identity, semantics, and member ordering—but derive comparative widths per the authenticated spec selector. For common mode, re-run the raw-evidence derivation and compare each stored width exactly via `Decimal(str(...))`; tolerance-based comparison is inappropriate after FCM’s sub-nanojoule findings.

10. Only after all cells bind, component/aggregate hashes match, and final artifact validation returns no findings may `write_outputs_exclusive` run.

The pinned `scripts/mint_floor_artifact.py` remains byte-unchanged. V1 behavior and its interface pins remain untouched.

### D-118 gauntlet invariants

The implementation ledger must prove:

1. Estimator authority comes only from the authenticated target comparative spec cell.
2. Spec SHA, membership, config, order, and producer inventory pass before dispatch.
3. No estimator/registration identity appears anywhere in admitted report or artifact JSON.
4. Pending or malformed common-mode registration refuses; no registered-path failure falls back.
5. Spec acceptance declarations match the authenticated acceptance domain owner exactly.
6. Calibration bracket and once-widened bound are rederived from ledger/binding/acceptance evidence.
7. Raw sweeps, residuals, windows, and widths come from authenticated member bytes.
8. Dispatch is cell-local; mixed default/common cells cannot inherit a producer-global choice.
9. One gated recomputation object feeds construction.
10. Report and all U10 numbers remain exact comparisons.
11. Final evidence binding independently uses the same spec selector and exact common-mode widths.
12. Default-only fixtures remain byte-identical to the current v2 output.
13. Common-mode refusal produces no output files.
14. Final-head tests include a one-ULP downward-width attack and the FCM exact-understatement oracle.
15. Any exact common-mode understatement invokes D-133’s permanent fallback, not another repair round.

## 3. Attack classes and committed regressions

| Attack | Required committed regression |
|---|---|
| Spec swap | Swap a valid same-membership default and common-mode spec path. Without pin repair, require refusal before estimator execution on extraction-spec SHA mismatch. Then repair report/U10 self-hashes but retain the frozen producer spec pin; refusal must remain. Assert no output. |
| Estimator mismatch between spec and report | Because the report has no identity vocabulary, test both manifestations: inject `estimator`/`estimator_registration` anywhere and repair report/U10 hashes—closed-profile refusal; separately place the opposite estimator’s cached floor in a vocabulary-clean report and repair all report/U10 literals—independent spec-selected recomputation must refuse. |
| Default/registered cross-wiring | Mint a four-cell fixture containing both selector types under one producer report. Assert default cells are byte-identical to baseline, registered cells use common-mode widths, and swapping cell order does not swap dispatch. Spy that registered refusal never calls the default floor function. |
| Equality-check bypass | Change report floor, operative floor, all U10 full/six-decimal values, extraction-report SHA, producer/component self-hashes, and external pinset SHA while leaving authenticated members unchanged. The raw-evidence recomputation must refuse before construction/write. Add a second case mutating one stored common-mode width by one ULP; the estimator-aware final binder must refuse even when artifact-local arithmetic is internally repaired. |

Also retain branch regressions covering recursive registration-key refusal, Unicode-escaped key injection, invalid registration without fallback, and default-path preservation.

## 4. COST

Expected product diff:

| File | Estimated change |
|---|---:|
| `joulewise/floor_mint_estimator.py` (new) | 220–320 LOC |
| `scripts/mint_floor_artifact_generalized.py` | 140–220 LOC |
| `tests/test_floor_mint_estimator.py` (new) | 250–400 LOC |
| `tests/test_mint_floor_artifact_generalized.py` | 300–450 LOC |

Expected total: roughly 360–540 production LOC and 550–850 test LOC. No changes should be needed in:

- `scripts/mint_floor_artifact.py`;
- `scripts/floor_mint_pinsets/schema_v2.json`;
- report or artifact schemas;
- production extraction specs during this WO.

The later pack re-spec is a separate D-133 consumption step.

Focused verification:

`python3 -m unittest tests.test_floor_mint_estimator tests.test_mint_floor_artifact_generalized tests.test_floor_extraction tests.test_detection_floor`

Then the required unpiped canonical suite:

`python3 -m unittest discover -s tests`

Expected gate cost: three audit waves—initial paired contract/execution/physics review, up to two fix-plus-delta rounds, Opus counter-review and prune, integration suite/CI, then D-121 terminal review. A same-signature recurrence escalates; an exact understatement terminates common-mode adoption.

## 5. RISKS

The single most likely failure mode is implementing estimator dispatch only in steps 8–9. That patch would appear correct in report/U10 tests but either:

- construct the artifact with the default estimator at `scripts/mint_floor_artifact_generalized.py:2569-2579`; or
- fail later when the pinned binder reconstructs default widths at `scripts/mint_floor_artifact.py:1917-1940`.

Other risks are private FCM helper drift, expensive repeated raw-trace authentication, and mistakenly treating the spec registration’s prose/evidence fields as runtime provenance. Signature/parameter pins, one shared adapter, and explicit “declaration only; provenance rederived” tests contain those risks.

The worktree ended clean at `f0e7cf6084ce997bded95845d0df8a98d534cf2d`; no files were modified.