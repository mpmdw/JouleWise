```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "PAPER-CUSTODY-AUDIT: printed-number coverage is the missing boundary; bind results before deleting custody machinery.",
  "workspace": {
    "base_requested": "32ff9013",
    "base_mode": "exact",
    "head_start": "32ff901374024defa97fc3d137c5a699423676e7",
    "head_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "upstream_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"should_fix","text":"Five sampled printed-number mutations escape main's draft-number checks; the branch inventory still accepts the mutated abstract count."},
      {"id":"F2","severity":"should_fix","text":"Custom capabilities and mirrored custody inventories guard an unconnected API rather than the current paper's printed values."},
      {"id":"F3","severity":"should_fix","text":"CI lacks an explicit always-on paper-number check; docs-only changes suppress ordinary test jobs."}
    ]
  },
  "verification": [
    {"id":"V1","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["COMPARED 43","MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"COMPARED 43\\nMISMATCHES 0"}},
    {"id":"V2","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_paper_round7_artifacts.py --corpus-root /Users/edr/code/JouleWise > /private/tmp/jw-paper-custody-audit-cg28dsf_/baseline-R7-full.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R7F PLACED 0/4","R7F COMPARED 415 / MISMATCHES 0"]},"expected":{"exit_code":0,"tail_regex":"R7F COMPARED 415 / MISMATCHES 0"}},
    {"id":"V3","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/jw-paper-custody-audit-cg28dsf_/audit_mutations.py > /private/tmp/jw-paper-custody-audit-cg28dsf_/mutations-summary.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["MUTATION AUDIT: 30 checker runs matched expected exits"]},"expected":{"exit_code":0,"tail_regex":"MUTATION AUDIT: 30 checker runs matched expected exits"}},
    {"id":"V4","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /private/tmp/jw-paper-custody-audit-cg28dsf_/replay_a38.py > /private/tmp/jw-paper-custody-audit-cg28dsf_/A38-raw.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["A38 RAW REPLAY 0.027365018417518542 EXPECTED 0.027365018417518542 MATCH True"]},"expected":{"exit_code":0,"tail_regex":"MATCH True"}},
    {"id":"V5","kind":"test","cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B docs/process_traces/2026-08-09-prefill-phase-proof/audit_prefill_phase.py --source-repo /private/tmp/jw-paper-custody-audit-cg28dsf_/historical-source --output-dir /private/tmp/jw-paper-custody-audit-cg28dsf_/prefill-replay-historical > /private/tmp/jw-paper-custody-audit-cg28dsf_/prefill-historical.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["bundles=100","results_sha256=3b55a60872da42353bcd668724128efda5230b8031efadbf54dd129500f840cf"]},"expected":{"exit_code":0,"tail_regex":"results_sha256=3b55a60872da42353bcd668724128efda5230b8031efadbf54dd129500f840cf"}}
  ],
  "flags": [
    {"id":"G1","kind":"baseline_drift","level":"nonblocking","text":"The prefill proof rejected today's parser identity. Replaying with a scratch checkout of producing commit e4b95f835 succeeded; all 100 original stream inventories, boundaries and overlap counts matched.","needs":""},
    {"id":"G2","kind":"verification_gap","level":"nonblocking","text":"Digit trials ran both main checkers in literals-only mode. Full baseline replays passed; all five mutations leave RF extraction and R7's complete paper-dependent comparisons unchanged.","needs":""},
    {"id":"G3","kind":"baseline_drift","level":"nonblocking","text":"Term lint against round7/retensing-plan.md reports the same 51 findings for baseline and every mutation.","needs":""}
  ]
}
```

PAPER-CUSTODY-AUDIT

## Findings

**F1 — The missing protection is comparison at the printed-number boundary.** A preserved, correctly hashed trace does not stop an agent copying a different number into prose. Five real digit mutations escaped both numerical paper checkers on main. This is a coverage finding, not evidence that the five original numbers are wrong: the inspected source trails support them.

**F2 — Much of the paper-custody stack protects a different boundary.** `configs/paper_supply/supply_map.json` contains five non-issuing fixture roles and two pending energy roles, with no production role. I found no external production importer of the paper modules in `joulewise/` or `scripts/`. The current Markdown draft does not pass through their capability boundary.

Counts below are physical file lines or inclusive function spans, including comments/blanks. Spans overlap; do not sum them.

| Mechanism and inspected location | What it prevents | Would it catch Ed’s bad-number threat? |
|---|---|---|
| `paper_custody.py`, **1,523 lines**; constructor/token/getattribute layer **134–317, 184 lines** | Ordinary construction or access to objects lacking the mint token; fixture/production type confusion | **No for today’s paper.** It rejects unverified API objects, but never reads the printed number. It is also explicitly not resistant to token discovery through attributes/closures. |
| Supply-map resolver **993–1109, 117 lines**; inventory **1155–1240, 86**; receipt **1243–1303, 61** | Wrong paths, hashes, roles, duplicated or omitted bindings, mismatched receipts | **Partly through that API.** Useful wrong-input checks; no current printed-text comparison. |
| Validator-source census **731–843, 113 lines**; ingress **1389–1498, 110** | Changed validator implementation, unexpected transitive reads, input changes between replay and reopen | **Partly.** Detects source/replay drift, not an independently copied or consistently wrong result. |
| Floor-acceptance gate **533–560, 28 lines** | Wrong floor bytes, source census, binder identity or acceptance ancestry | **Partly.** Preserves intended inputs; its receipt/hash checks do not establish the printed value. |
| D165 gate **563–594, 32 lines** | Invalid closeout sources and inconsistent derived branch/licensing | **Partly.** Recomputes branch semantics; it has no production supply role or current draft connection. |
| Claim gate **597–652, 56 lines** | Manifest/verdict/side-bound inconsistencies, floor mismatch, unsupported claim grants | **Partly.** Reevaluates claims using stored estimates and bounds; it does not rerun `analyze_claims` from raw data or compare prose. |
| `paper_rendering.py`, **88 lines** | Wrong issuing type, family, mode or subject grant before rendering | **Partly for API use; no current-paper coverage.** Its energy renderer prints the supplied projection mean. |
| `paper_reported_energy.py`, **431 lines**; `_project_cell` **339–402, 64** | Wrong 50-member ordering, phase/model/unit/token identities; incorrect aggregation relative to supplied rows | **Partly.** Numerical projection checks matter, but supplied energy rows still need raw provenance/replay; production dispatch is absent. |
| Registration-order checks **170–220, 51 lines including intervening lines** | Registration/spec ordering and digest disagreement | **No for a printed digit.** History ordering is not numerical validation. |
| `authentication_io.py`, **834 lines**; read session **322–540, 219**; Path wrapper **60–130, 71** | Ambiguous JSON, changed bytes across reads, missing read registration; pinned no-follow reads | **Partly.** Good shared input integrity; stable wrong arithmetic still passes. |
| Authentication AST/signature guards **659–754, 96**, **757–814, 58** | Direct reads outside the reader; public supplier signatures accepting arbitrary values | **No for prose.** These police implementation structure, not displayed quantities. |
| `AuthenticatedConsumptionSession`, actually in `whole_window.py` **465–966, 502 lines**, imported by `inputs.py` | Stale/incorrect calibration bindings; narrowed operative envelopes; re-reduces when the authenticated bound requires widening | **Partly.** Scientifically useful freshness and recomputation. It does not validate arbitrary paper literals. |
| `analysis_engine/inputs.py`, **4,629 lines**; floor authentication **881–955, 75**; evidence binder **1610–2029, 420**; input loading **3092–3344, 253** | Wrong floor/bundle/config/metric identities, invalid members, inconsistent lineage and whole-window eligibility | **Partly.** Preserve these numerical/input obligations when simplifying. `AuthenticatedFloorArtifact` is an ordinary frozen dataclass, not the paper token mint. |
| Analysis generation: `__init__.py` **1,909 lines**; artifact validation **3,651**; claim evaluation **431** | Computes estimates/intervals/multiplicity; rejects inconsistent serialized claim arithmetic and outcomes | **Partly.** Generates and validates claim artifacts; cannot protect separately typed paper/README numbers. Artifact consistency is not complete independent raw reanalysis. |
| `_private_factory_identity`, **93–98, 6 lines** | Records injected factory identity as `private_test_seam:…` | **No.** It is metadata; the inspected artifact policy check requires nonempty strings, not numerical replay. |
| Single-count metadata/accessors, `detection_floor.py` **364–554**; census test **1,190 lines** | Missing/mixed/corrupted explanatory rule metadata | **No for a copied digit.** Keep actual floor and decision-interval arithmetic tests. The current metadata explicitly says it is a sizing diagnostic, not another acceptance gate. |
| `check_paper_replay_fence.py`, **678 lines** | Wrong selected worked-example values through raw hash checks, rederivation and specified rounding; repeated operands/subtraction inconsistencies | **Partly overall; yes for its selected values.** Full replay compared **43 rows** successfully. My five chosen sites are outside its extraction. |
| `check_paper_round7_artifacts.py`, **1,377 lines** | Wrong DX source pins/fields/registry renderings, artifact gates and 118 SVG marks; producer replay disagreement | **Partly.** Full replay passed **415 comparisons**, but current placement is **0/4**. The unmarked selected prose values escape its draft scans. |
| Results-fill registry, **1,258 Markdown lines** | Documents supplying paths, fields, rounding and retirement | **No by itself.** A documented binding becomes protection only when executed against the display. |
| `render_results_fills.py`, **1,185 lines** | Malformed legacy result inputs, unsupported fills and inconsistent generated variants | **Partly on its legacy output.** It does not own the D174 methods/diagnostic skeleton. |
| Comparison/placement test modules, **357 + 396 lines** | Mirrored obligations, supplier labels and retirement/proposal agreement | **No general digit check.** Keep eligibility assertions; repeating identical proposal text adds no numerical comparison. |
| Term lint **656 lines**, claims lint **1,985**, Markdown structure checker **580** | Vocabulary/claim-index semantics or document structure | **No general numerical binding.** The forbidden-language scan’s inspected surface list excludes `docs/paper`; term and structure checks do not recompute results. |

**Five source-to-print traces and executed mutations.** There is no headline J/request result in this skeleton; the abstract’s record-support count is its available headline numerical result.

| Printed site; changed digit | Trace from preserved inputs to display | Checks touching it; mutation result |
|---|---|---|
| Abstract line 24: **37 → 38** failures | a10’s 10 + Window C’s 40 named bundles → event boundaries and raw-to-CSV validation → positive-overlap counts → `2026-08-09-prefill-phase-proof/results.json`, `stack_summaries[1.5B].resolvability…` → abstract | Historical-parser replay reproduced 37/50; all 100 original stream inventories/boundaries/counts matched. **Main misses edit; branch inventory also passes.** |
| Section 2 line 157: **9.724 → 9.725 ms** | Hash-pinned capture manifests/evidence and primary pulse bytes → current-anchor per-capture bounds → S17’s 17 decimal lexemes → max minus min = **0.00972358928879385 s** → nearest microsecond, HALF_EVEN → **9.724 ms** | I recomputed the range/rounding. **Main misses edit.** Branch fails only because stale unresolved contexts increase unaccounted count to 855 above 853; this is **not source-value validation**. |
| DX prose line 573: **+13.0 → +13.1 ms** | `20260722T145535-e941c821` raw plist + events, verified against evidence hashes → current anchor/pulse fits → XD `summary.onset_best_fit_lag.median_ms` → explicit sign, one decimal | Fresh XD JSON and SVG were byte-identical to committed parents. R7 verifies parents/registry/figure, but **misses this prose edit**. Branch rejects `dx.medians.onset_median`. |
| S4 table line 731: **0.0533655 → 0.0533656 s** | r03 raw power → preserved CSV; pinned events give phase [0.267684, 0.3887181] relative seconds → record 365 [0.1945653, 0.3210495] → clipped overlap → WEX `historical.geometry[0].records[1]` → table | I checked event/CSV hashes and recomputed **0.0533655** using Decimal. **Main misses edit.** Branch rejects its endpoint-derived overlap slot. |
| A.3.8 line 1263: **0.027365018417518542 → …543 s** | `20260722T194118-9dc0749d` manifest/evidence hashes → pinned raw plist/events → current-anchor pulse rederivation → R4 record / S17 `derivation_corpus.members[1].b_fiducial_s` → exact decimal string | Fresh raw replay reproduced **…542**. **Main misses edit.** Branch rejects `a38.table.v1`. Importantly, the stored older-method bound is **0.026300679324099796**: blindly reading that field would use the wrong method. |

For baseline and each mutation I executed both main checkers with `--literals-only`, the branch inventory with `--check`, Markdown checking and term lint: **30 runs**. Main numerical/Markdown checks returned 0 throughout; term lint retained its baseline 51 findings. Full baseline RF/R7 replays also passed. All five edits leave RF’s extracted inputs and R7’s entire paper-dependent comparison list identical; R7’s producer replay does not consume draft text. A separate positive-control edit to RF’s capture-bound literal correctly returned 2.

The inventory at `aeaf2556` is a useful first landing, not complete protection: inspection found **111 bound slots + one tied + six classed = 118 total slots**, across only DX, S4-overlap and A.3.8 groups. Its numerical census reports **155 unresolved results literals and 853 unaccounted literals**; 302 spelled-out numbers remain uninventoried. “STALE” unresolved contexts are informational unless count growth occurs. The historical “241” count should therefore not be used as today’s acceptance census.

**F3 — Put numerical checking in the always-on CI lane.** `.github/workflows/ci.yml` suppresses ordinary/quick tests for docs-only changes. Its explicit fences do not invoke either paper-number checker; `test_docs_freshness.py` contains no paper-check wiring. A paper-only digit edit needs its own mandatory check.

**Replacement design and safe order of work:**

1. Land the inventory checker first, explicitly invoking **`--check`** in CI for paper-only changes. Retain both existing checkers and their protections during migration.
2. Make one canonical machine-readable display manifest. Each result occurrence binds **slot → dataset/roster identity → named artifact + field or recomputation → unit → rounding**. Include abstract repetitions, tables, SVG labels/marks, README claims and claim-renderer output.
3. Bind headline/record-support and calibration values next, then eliminate every unresolved **results** literal. Explicitly classify references, dates and fixed method constants; count ceilings alone cannot establish coverage.
4. Keep derived sources hash-pinned, with provenance naming preserved primary hashes, complete selected/excluded membership, model/phase/epoch, and algorithm version. A hash of the wrong selected dataset is insufficient.
5. Provide one replay command that regenerates derived artifacts from those preserved inputs. Select the required historical parser/method explicitly. CI checks displays against pinned outputs; changes to scientific inputs or algorithms also require the corresponding raw replay. Missing inputs must report incomplete validation.
6. Prefer generated slot expansion for prose, tables and figure labels. The checker independently compares the final displayed strings/geometry and rejects missing, duplicated or mismatched slots. It must not merely compare an inventory with itself.
7. Establish an old-check → replacement-check coverage ledger. Keep numerical positive controls and scientific/eligibility tests; delete an old guard only after its relevant obligation is covered.

| Conditional deletion after coverage replacement | Estimated removable lines |
|---|---:|
| `paper_custody.py` and `paper_rendering.py`; move necessary source/eligibility validators behind an ordinary shared reader | **1,611 existing lines**, before accounting for relocated code |
| Thin `paper_reported_energy.py`: remove custom ingress coupling, fixture dispatch and Git-order ceremony; retain estimand, member/token semantics and projection arithmetic | **~150–250 net** |
| Retire `scripts/render_results_fills.py` from the current submission path | **1,185** |
| Replace duplicated RF/R7 text extraction, registry parsing, placement and reporting with the unified slots/checker; retain raw replay and SVG comparisons | **~400–700**, conservative estimate |
| Remove duplicate comparison/proposal/retirement mirror tests; retain actual applicability/eligibility tests | **~400–600 test lines**, from 753 existing |
| Remove AST supplier-signature/read policing where replacement boundary tests cover the obligation | **154 helper lines**, plus unestimated test/inventory reductions |

These estimates are not additive guarantees. Do **not** delete the shared authentication reader, analysis engine, calibration science or raw-input validators wholesale on this audit’s evidence.

Keep preserved traces and second-copy/hash custody; parsers and historical method selection; anchor/pulse fitting; calibration range/SD/quantile/bracket arithmetic; integration, estimator and denominator math; registered membership/exclusions; scientific admission/eligibility; and rounding/units. Replay can reproduce a deterministic implementation bug, so retain independent arithmetic witnesses and relevant science review.

One **cold Fable check** should cover the proposed changes to `_claim_issuance_gate`, `_d165_issuance_gate`, floor acceptance, reported-energy projection/eligibility, and removal of their capability/grant boundary. Further cuts to `AuthenticatedConsumptionSession`, floor binding, registered policy or calibration lineage belong in that same claim-path review. M14’s historical source-coordinate machinery was not comprehensively re-audited here; the successful historical-parser retry demonstrates an interpretation obligation that must survive simplification.

## Residual risk

I replayed the selected A.3.8 member, not all 17 calibration fits; calibration range/rounding was recomputed from their pinned lexemes. Mutation trials covered five sites, not every display surface. No full unittest suite was run because this was a read-only audit. Main remained clean and unchanged at `32ff9013`; all scratch writes were outside the repository.

Ed, the real gap is numbers copied into prose without source comparisons.
All five tested edits escaped main’s draft-number checks.
The new inventory catches three by value and one indirectly; the abstract count still escapes.
Bind every displayed result and run that checker for paper-only changes.
Keep the preserved traces, hashes, replay math and scientific eligibility.
Delete custody ceremony after coverage replacement; cold-check the claim-path cuts.