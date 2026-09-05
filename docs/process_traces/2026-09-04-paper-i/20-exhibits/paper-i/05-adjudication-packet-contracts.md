```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Three seats converge on custody, fail-closed rendering, fixtures, and measurement deferral, with twelve R1-R3 choices left for the magistrate.",
  "workspace": {"base_requested":"3b2df563","base_mode":"exact","head_start":"3b2df563b096eed98c8045e961590e1d32abb5d2","head_end":"3b2df563b096eed98c8045e961590e1d32abb5d2","upstream_end":"3b2df563b096eed98c8045e961590e1d32abb5d2","branch":"feat/2026-09-04-paper-i-scout"},
  "pathspec": ["docs/process_traces/2026-09-04-paper-i/05-adjudication-packet-contracts.md"],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"R1","severity":"should_fix","title":"Five D-123 wire/reduction/refusal choices require rulings"},
      {"id":"R2","severity":"blocker","title":"Four gamma bound/version/token/prose choices require rulings"},
      {"id":"R3","severity":"blocker","title":"Three transfer projection/quantity/prose choices require rulings"}
    ]
  },
  "verification": [
    {"id":"V1","kind":"inspection","cmd":"git diff --no-index --check /dev/null docs/process_traces/2026-09-04-paper-i/05-adjudication-packet-contracts.md","cwd":".","observed":{"result":"pass","exit_code":1,"tail":[]},"expected":{"exit_code":1,"tail_regex":"^$"}},
    {"id":"V2","kind":"inspection","cmd":"test \"$(wc -c < docs/process_traces/2026-09-04-paper-i/05-adjudication-packet-contracts.md)\" -lt 30000","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
    {"id":"V3","kind":"test","cmd":"python3 -m unittest discover -s tests (prohibited by user preflight rule)","cwd":".","observed":{"result":"not_run","exit_code":0,"tail":["No tests run: explicit preflight rule."]},"expected":{"exit_code":0,"tail_regex":"No tests run"}}
  ],
  "flags": [
    {"id":"F1","kind":"lead_ruling","level":"blocking","text":"Twelve R1-R3 divergences remain.","needs":"Answer Q-R1-1 through Q-R3-3 before implementation."},
    {"id":"F2","kind":"verification_gap","level":"nonblocking","text":"Inspection only; tests prohibited.","needs":"Implementation seats own the tests below."},
    {"id":"F3","kind":"residual_risk","level":"nonblocking","text":"Transfer branch d67ee56c is unreviewed and outside this base.","needs":"Adjudicate it before binding a consumer."}
  ]
}
```

# Magistrate's adjudication packet — Paper I supplier contracts

## Findings

Baseline: `3b2df563`. Seats are **Sol** (`02-consult-sol-contracts.md`), **Fable** (`02-blind-fable-contract-seat.md`), and **Opus** (`03-consult-opus-contracts.md`). “AGREE” means the same field and semantics; “DIFFER” names the exact wire or rule split. The scout is context, not a fourth vote.

### R1 — `joulewise.reported_phase_energy.v1`

#### Field-by-field comparison

| Field / rule | Sol | Fable | Opus | Mark and exact difference |
|---|---|---|---|---|
| Cardinality / `schema_version` | One per pack; exact v1 | One per role; exact v1 | Cardinality implicit via `pack_id`; exact v1 | AGREE on v1; DIFFER on explicit cardinality |
| Content / role identity | `artifact_id=rpe-<hash>`; role inferred | `artifact_sha256`; `campaign_role` | No ID; cell `arm_id/model_id`, provenance `pack_id` | DIFFER — prefixed ID vs hash vs none; role location differs |
| `producer` | Implementation, commit, source hash | Absent | Absent | DIFFER — Sol only |
| Extraction/floor parents | Spec+report schemas/hashes and floor projection hash | Extraction/frozen-semantics/plan hashes | Floor artifact, pack, config, byte-receipt hashes | DIFFER — distinct parent sets |
| Whole-window parent | Per-member evaluation-basis hash | Top-level verdict hash/status | Absent | DIFFER |
| G2-a / prompt-pin parents | Both top-level, schema/hash/length joined | G2-a external; pin hash in `per_token` | Not explicit | DIFFER |
| `cells[].cell_id` | Exact registered ID | Exact extraction ID | Exact ID plus `source_cell_id` | AGREE on selector; DIFFER on duplicate source ID |
| Phase/model fields | `metric` | `phase,metric` | `phase,model_id,arm_id` | DIFFER — only metric/phase semantics overlap |
| Cell status/refusal | `status=issued|refused`; cell reasons | No cell status; token status | Top-level refusal; token refusal | DIFFER |
| Member basis | Exact ordered generator list; all 50 or cell refusal | Sorted extraction-admitted IDs | Producer-issued independent-bundle IDs | DIFFER — fixed vs admitted vs abstract basis |
| Counts | `registered_member_count=50`, admitted count | `n_planned`, admitted count | Admitted count | DIFFER |
| Member inventory/custody | Full records: ordinal, IDs, five hashes, admission/reasons | IDs/excluded slots; no member hashes | IDs plus member/config hashes | DIFFER |
| Member values | Point, envelope, observed denominator per member | Not emitted | Not emitted | DIFFER — Sol only |
| `mean_j_per_request` | Mean of fixed 50 points | Mean of admitted values | Producer-issued; consumer cannot calculate | AGREE on field; DIFFER on basis/deriver |
| Interval wrapper/endpoints | `interval_j_per_request.{lower_j,upper_j}` | `interval.{lower_j,upper_j}` | Same as Fable | AGREE endpoints; DIFFER wrapper name |
| Interval composition/terms | Mean member-envelope endpoints; descriptive | t·s/√n + max anchor + one drift; emits all terms | Registered opaque rule plus `terms[]` | DIFFER — three rules |
| `per_token.value_j_per_token` | Issued | Issued | Value or null | AGREE |
| Numerator / aggregate | Stores summed energy and observed count | Stores denominator total/uniformity, no numerator | Stores observed count, no numerator | DIFFER |
| Denominator kind | `runtime_observed_{prompt,output}_tokens` | `observed_{prompt,output}_tokens` | `{prompt,output}_tokens` | DIFFER — literals |
| Denominator source | `runtime_observed` plus member evidence | Exact metadata/event expression | `runtime_observed|server_usage` | DIFFER |
| Aggregation | Ratio of sums, fixed members | Ratio of sums | Forbids mean/one-count division; no rule ID | AGREE in intent; DIFFER in wire |
| Cross-checks | Prefill four surfaces+G2-a/pin; decode positive | Same prefill; decode exactly 512 | Neither explicit | DIFFER |
| Refusal scope | Member defect refuses cell; denominator included | Shared/basis defect refuses artifact; denominator only token | Basis/provenance defect refuses artifact; bad source token-only | DIFFER |
| `rendered` | Absent; renderer formats | Supplier emits half-even strings | Absent | DIFFER — formatting owner |
| Floor noninterference | Projection hash + byte test | Digest equality + byte test | Receipt hash + byte test | AGREE on byte identity; DIFFER proof field |

#### Existing-contract conflicts verified

| ID | Seat-raised conflict | Verification |
|---|---|---|
| C-R1-1 | The registry/scout says the D-123 member basis is undefined, but both `_v5` floor generators already register three fixed 50-member reported cells. | **VERIFIED.** Registry says undefined at `docs/paper/results-fill-registry.md:331-336,340-359`; D-123 says same 50 at `docs/decision_log.md:7987-7993`; both generators emit `reducer="arithmetic_mean_over_fixed_member_universe.v1"`, `expected_n=50`, ordered members at `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2133-2180` and the 8B twin at the same lines. The registry is stale on basis, not on the missing result schema. |
| C-R1-2 | A whole-artifact member refusal would override the registered per-cell `missing_or_invalid_member` rule. | **VERIFIED.** Each registered cell owns `missing_or_invalid_member="refuse_reported_mean"` at both v5 generators `:2144-2180`; only a missing registered phase has the broader before-emission refusal at `:2206-2210`. |
| C-R1-3 | `floor.mean_j`, `floor.n`, or comparative `n_admitted` cannot substitute for the reader-facing mean or bundle count. | **VERIFIED.** Registry forbids the internal floor mean at `docs/paper/results-fill-registry.md:331-336` and floor-component count at `:344,349,354,359`; code emits floor `mean_j` at `joulewise/floor_extraction.py:1347-1358`, while comparative admission is block differences and block count at `:2653-2717,2799-2803`, not independent-bundle mean/count. |
| C-R1-4 | Configured or stream-chunk token counts are not authenticated denominators; `server_usage` is runtime evidence, not a config fallback. | **VERIFIED.** D-058 logic accepts observed total and rejects stream fallback at `joulewise/reduce.py:401-416`; output-token logic accepts `server_usage` or token events but returns no value for `stream_chunk_fallback`/`config_fallback` at `:3735-3756`; prefill realizes four agreeing surfaces at `joulewise/bundle_read.py:1015-1051`. |

#### Magistrate decisions

1. **Q-R1-1 — Which member universe and cardinality?** Sol: one artifact per pack, exact ordered generator universe, 50/all-or-cell-refuse. Fable: one per role over extraction-admitted sorted members. Opus: producer-issued independent-bundle basis. **Recommendation:** Sol, amended to name `campaign_role`; D-123 and the v5 bytes already freeze the exact 50-member universe, so no post-data admission shrinkage is allowed.
2. **Q-R1-2 — What is the fully composed interval?** Sol: mean member-envelope endpoints only. Fable: symmetric t95 repeat half-width plus max anchor and one drift allowance. Opus: defer to a separately registered composition ID/terms. **Recommendation:** adopt a new pre-data rule combining the defensible parts: lower = mean(member lower endpoints) − t95·s(point)/√50 − one authenticated window allowance; upper = mean(member upper endpoints) + t95·s(point)/√50 + that allowance. This preserves asymmetric member envelopes, adds repeatability once, and avoids Fable's second anchor charge. Register the exact rule ID before collection.
3. **Q-R1-3 — Where does refusal bite?** Sol: any member defect refuses the owning cell's mean/interval/per-token/count. Fable: shared/basis failures refuse artifact; denominator defects refuse per-token only. Opus: whole artifact for basis/provenance/n, per-token null for bad source. **Recommendation:** three levels: shared identity/authentication failure refuses artifact; a registered-member energy/envelope failure refuses that cell; denominator-only failure refuses only its per-token companion. Sibling cells and the gross/count fields remain available when their own parents authenticate.
4. **Q-R1-4 — Which denominator and reduction?** Sol: strict runtime counts, ratio of sums, prompt four-surface equality. Fable: same plus decode=512 and uniformity. Opus: producer-issued runtime/server usage, never config fallback or mean/count division. **Recommendation:** ratio of sums over the same fixed members; accept only current reducer runtime sources (`runtime_observed` token events or `server_usage`), reject stream/config fallback; require prefill four-surface equality and decode output count 512 per D-166. Do not require denominator uniformity beyond those checks.
5. **Q-R1-5 — Which closed wire and formatting owner?** Sol: rich content-addressed artifact with member records; Fable: compact artifact plus producer-formatted strings; Opus: minimal issued values/provenance without ID. **Recommendation:** a content-addressed per-role artifact using Sol's custody/member detail, explicit `campaign_role`, and no `rendered` object; unrounded numeric relations validate first and the paper renderer owns registered formatting.

### R2 — gamma claim renderer, `claim_side_bound`, and prefill token family

#### Field-by-field comparison

| Field / rule | Sol | Fable | Opus | Mark and exact difference |
|---|---|---|---|---|
| Carrier/location | v2 sibling `contrasts[].claim_side_bound` | v1 nested field, or sidecar fallback | v1 sibling | DIFFER — version/location |
| `value_j` | Named clock-anchor term | Full decision-interval half-width | New registered sizing bound or null | DIFFER — incompatible quantities |
| Bound identity | `source_term_name=E_clock_anchor_shift_bound_j` | `definition=decision_interval_half_width`; t/SE/total terms | Opaque `bound_id` | DIFFER |
| Role/composition | Explicit measurement role, named-term and single-count IDs | Formula only | Reason codes only | DIFFER |
| Null/reasons | Required finite value in issued object | Not specified | `value_j|null`, `reason_codes[]` | DIFFER |
| Cross-check | Exactly one named term equals B, never total | B=(upper-lower)/2 | Bound ID registered; no alias | DIFFER |
| Existing estimate/endpoints | Read estimator estimate and decision interval | Same | Same | AGREE |
| Magnitude token | Preserve decode; add symmetric prefill `M_*` | Mirrors every decode token | Omits `M_*` from enumerated minimal family | DIFFER |
| Floor token/rule | Decode+prefill, two-arm max/cross-check | Same | Same | AGREE |
| `B_*_claim_J` | Decode + symmetric prefill from field | Decode + prefill from half-width | Decode + prefill from nullable field | AGREE on token role; DIFFER on source |
| Clearance/shortfall/ratio | Preserve decode and add all three prefill twins | Mirrors all decode names | Adds clearance/shortfall only | DIFFER |
| Joint sizing `S_*_joint_J` | Preserve decode/add prefill | Mirrors decode | Not enumerated | DIFFER |
| Signed sizing clearance | New `C_*_sizing_signed_clearance_J` for both | Not separately named | Not separately named | DIFFER |
| Gate/verdict outputs | `OUTCOME_*_{floor,direction}_gate`, `VERDICT_*` | `V_*_{floor,direction}_gate`, `V_*_verdict` | No tokens; row-bound text | DIFFER — names/presence |
| Gate rule | `|estimate|>F`; interval wholly registered side; claim/Holm consistent | Same | Same | AGREE |
| Equivalence | Invalid/`STOP_FILL` for these directional contrasts | `STOP_FILL` | Fixture excludes; artifact vocabulary acknowledged | AGREE in effect |
| D-166 3/4-count branch | Exact special rendering | Not stated | Not stated | DIFFER — Sol alone carries the existing rule |
| Refusal strings | Exact token-generation/prompt-processing/earlier-stop forms | Same | Same | AGREE |
| Verdict prose | Full outcome-specific `supported/not supported` phrases with ordered codes | `supported/direction observed/unresolved/not resolvable/not estimable` | One phrase per outcome, text not fixed | DIFFER |

#### Existing-contract conflicts verified

| ID | Seat-raised conflict | Verification |
|---|---|---|
| C-R2-1 | `B_decode_claim_J` must not alias `deterministic_bounds.total` or become a gate. | **VERIFIED.** `docs/paper/draft-v1.md:196-200,285`, registry `docs/paper/results-fill-registry.md:377,381`, artifact guide `docs/paper/artifact-guide.md:139-142`, and renderer guard `scripts/render_results_fills.py:574-578,975-978` all say so. |
| C-R2-2 | The seats disagree whether the separately registered B is the clock-anchor term, the complete interval half-width, or a future bound. Existing sources themselves split. | **VERIFIED.** D-078 calls the claim-side measurement uncertainty the member `E_clock_anchor_shift_bound_j` at `docs/decision_log.md:4791-4800`; D-083 repeats that design at `:5281-5306`; adapter contract and code name `claim_side_bound_source` as that term at `docs/contracts/adapter_contracts.md:621-643` and `joulewise/detection_floor.py:348-363`. But the newer artifact guide says even the named term “is likewise not the column” at `docs/paper/artifact-guide.md:139-142`, while the registry keeps the supplier unknown at `docs/paper/results-fill-registry.md:377`. Fable's full half-width additionally includes t·SE and every deterministic term (`joulewise/analysis_engine/estimators.py:465-485`), broader than the D-078 named source. A magistrate amendment is required. |
| C-R2-3 | Adding either proposed field to `claim_verdicts.v1` in place violates its closed schema. | **VERIFIED.** Current producer emits v1 at `joulewise/analysis_engine/__init__.py:1827-1834`; validator fixes exact contrast keys without `claim_side_bound` at `joulewise/analysis_engine/artifact.py:167-187` and rejects extras at `:1655-1663`. Sol's v2 or a separately versioned sidecar is required; Fable/Opus in-place v1 sketches are invalid. |
| C-R2-4 | DS-28's current floor-only binding contradicts its `F+B; signed clearance` column; PG-04 has the same unresolved shape. | **VERIFIED.** Draft specifies `C=F+B` and `|estimate|-C` at `docs/paper/draft-v1.md:285`; the registry defines `S_decode_joint_J=F+B` at `docs/paper/results-fill-registry.md:381` but DS-28 binds floor-only clearance/shortfall at `:881`; PG-04 remains unspecified at `:890`. |
| C-R2-5 | Prefill gate/verdict vocabulary cannot be guessed from decode or D-165. | **VERIFIED.** Registry explicitly leaves the prefill family missing at `docs/paper/results-fill-registry.md:363-368,886,888-894` and forbids D-165 inference in DS-32/PG-08 at `:885,894`. |
| C-R2-6 | D-166 requires distinct count<3 and count=3–4 refusal renderings. | **VERIFIED.** Binding decision `docs/decision_log.md:212`; registry repeats the exact split at `docs/paper/results-fill-registry.md:280-286`. |

#### Magistrate decisions

1. **Q-R2-1 — What is B?** Sol: the exact `E_clock_anchor_shift_bound_j` contrast term. Fable: complete decision-interval half-width. Opus: a new registered sizing-bound ID, unissued until defined. **Recommendation:** Sol, by explicit amendment of the artifact guide/registry: B is the named clock-anchor contrast term projected into a separately typed field. This matches D-078/D-083 and the single-count contract; the full half-width would double-label stochastic and unrelated deterministic uncertainty as the clock-anchor claim-side quantity.
2. **Q-R2-2 — Where does B live?** Sol: required sibling in `claim_verdicts.v2`. Fable: nested v1 field or sidecar. Opus: sibling in v1. **Recommendation:** required sibling in `joulewise.claim_verdicts.v2`; preserve v1 unchanged. A sidecar adds a second identity join without benefit, and the v1 exact-key validator rules out in-place extension.
3. **Q-R2-3 — What exact token family closes both rows and sizing?** Sol: full symmetric numeric family plus `OUTCOME_*`, `VERDICT_*`, and signed-sizing-clearance tokens. Fable: mirror all decode tokens but call outcome/verdict tokens `V_*`. Opus: minimal prefill numeric mirror; gate/verdict rows have no named tokens. **Recommendation:** Sol's full family; retain every already registered decode name, mirror it for `prefill_p[PREFILL_LENGTH]`, and add explicit `C_*_sizing_signed_clearance_J`, `OUTCOME_*_{floor,direction}_gate`, and `VERDICT_*`. Bind DS-28/PG-04 to `S_*_joint_J` plus signed sizing clearance, never the floor-only clearance.
4. **Q-R2-4 — Which exact professor-facing phrases?** Sol: complete conservative phrases and ordered raw codes. Fable: shorter “cleared/not cleared” and outcome-specific phrases. Opus: requires one phrase per outcome but leaves bytes open. **Recommendation:** Sol's semantic branches with Fable's concise surface: `passes/does not pass/not evaluated` for each gate; `supported/not supported/not evaluated` for verdicts; name model, phase, registered direction, and exact interval/floor relation; append authenticated reason codes in artifact order only where no registered prose map exists. Preserve the two registry refusal sentences byte-exact and include D-166's 3/4-count sentence.

### R3 — `transfer_fiducial_result` and TR-01

#### Field-by-field comparison

| Field / rule | Sol | Fable | Opus | Mark and exact difference |
|---|---|---|---|---|
| Public carrier | New projection `joulewise.transfer_fiducial_result.v1` | Revised/consumed `joulewise.transfer_fiducial_capture.v1` | Consume candidate capture directly; no new fields | DIFFER |
| Content identity | `result_id=tfr-<sha256(empty-id canonical JSON)>` | `artifact_sha256` | Existing capture has no content ID | DIFFER |
| Protocol identity | Exact task ID | Protocol estimator ID + registration hash | Candidate protocol ID/revision | DIFFER |
| Diagnostic flags | `diagnostic=true`, `claim_bearing=false` | Same | Same candidate fields | AGREE |
| Source identity | Capture/schema/file/commit/plan/receipt/estimator/bundle hashes | Protocol/session/run hashes | Existing capture fields | DIFFER — wrapper and digest closure |
| Run census/identity | Exact census/two edges; bundle hashes + selected witness | Registered/observed counts; run/bundle hash | Planned/observed nested runs, IDs/config hashes | AGREE on validation; DIFFER on wire |
| Edge evidence | Selected `largest_inserted_gap_edge` with interval, anchor, composed bound | Per-run start/end interval/status | Existing target edges carry interval, anchor, `radius_s` | AGREE on evidence; DIFFER on public projection |
| Public residual field | `composed_absolute_residual_bound_s` in selected witness | `largest_edge_residual_s=max |interval endpoint|` | Candidate `residual_transfer_s=max(radius_s)` | DIFFER — Fable omits the added anchor from the named max; Sol/Opus include it |
| Anchor composition | Explicit `max(|lower|,|upper|)+effective_clock_anchor_bound_s` | Not included in declared `largest_edge_residual_s` formula | Already included in each `radius_s` | DIFFER |
| Pulse bound | `pulse_derived_timing_bound_s` | `session_bound.b_fiducial_s` with receipt | Candidate `b_pulse_s`, sourced from evidence `b_fiducial_s` | DIFFER — semantic public name vs ledger name vs candidate alias |
| Comparison/excess | Outcome derived from composed max <= bound; no excess field | `comparison.{residual_s,bound_s,excess_s,supported}` | Candidate `excess_s`, `verdict`; renderer should read/cross-check | DIFFER |
| Outcome vocabulary | `supported|not_supported|not_evaluated` | `supported|not_supported|inconclusive` | `supported|exceeds_bound|inconclusive` | DIFFER |
| Reasons | Closed ordered unique `reason_codes` | Registered `reasons[]` | Candidate sorted `reasons[]` | AGREE semantically; DIFFER in field/vocabulary |
| Producer-formatted strings | None; renderer formats seconds to six decimals | `rendered` milliseconds, one decimal | None | DIFFER |
| Public token | `[TRANSFER_FIDUCIAL_RESULT]` | Implicit TR-01 sentence | `TR_01_transfer_result` | DIFFER |
| Placement/branch/claim | Nine identical copies; never removed; no floor/claim | Same | Same | AGREE |
| Fixture not-supported value | 0.031 s | 0.041 s | Candidate `exceeds_bound`, unspecified here | DIFFER — any authenticated >bound fixture works; exact golden differs |

#### Existing-contract conflicts verified

| ID | Seat-raised conflict | Verification |
|---|---|---|
| C-R3-1 | Candidate `residual_transfer_s` is not a raw fitted residual; it is the maximum composed radius after adding anchor uncertainty, making TR-01's current wording ambiguous. | **VERIFIED.** Candidate code computes `radius=max(abs(lower),abs(upper))+run_bound` at `d67ee56c:joulewise/transfer_fiducial.py:317-348`, then sets `residual_transfer_s=max(radii)` at `:856-866,1367-1388`; worked example pins 0.020+0.002=0.022 at `d67ee56c:docs/process_traces/2026-09-04-fanout/transfer-fiducial/worked-example.json:9-19`. TR-01 says “largest fitted ... residual” at `docs/paper/results-fill-registry.md:920`. |
| C-R3-2 | Candidate `exceeds_bound` conflicts with a registered literal `not_supported`. | **NOT FOUND.** TR-01 and kernel acceptance require recording whether the residual supports applying the bound, but close no verdict enum: `docs/paper/results-fill-registry.md:920`; `docs/process/state_kernel.json:5332-5345`. `not_supported` is a reasonable public projection, not an existing registry literal that overrides the capture. |
| C-R3-3 | Candidate `b_pulse_s` diverges from the ledger/evidence name `b_fiducial_s`. | **VERIFIED** as a naming projection, **not** as a forbidden alias. Candidate reads evidence `b_fiducial_s` then emits `b_pulse_s` at `d67ee56c:joulewise/transfer_fiducial.py:870-909,1437-1476`; historical registry names `b_fiducial_v3_s` at `docs/paper/results-fill-registry.md:602-605`. A result schema should preserve the source field/hash while using an unambiguous public semantic name. |
| C-R3-4 | A direct renderer would bind to an unaccepted schema even though TR-01 says no issued schema field/token exists. | **VERIFIED.** TR-01 says supplier named but schema field/token absent at `docs/paper/results-fill-registry.md:920`; the candidate branch is `d67ee56c`, explicitly unreviewed and not in baseline `3b2df563`. Its capture currently emits the fields at `d67ee56c:joulewise/transfer_fiducial.py:1449-1501`. |
| C-R3-5 | Any branch suppression or claim/floor minting would violate existing contracts. | **VERIFIED.** TR-01 makes placement branch-independent at `docs/paper/results-fill-registry.md:920`; task acceptance requires diagnostic/non-claim-bearing and no floor/claim at `docs/process/state_kernel.json:5332-5345`, with existing-estimator fence at `:5407-5412`. |

#### Magistrate decisions

1. **Q-R3-1 — What does the paper consume?** Sol: a small content-addressed result projection. Fable: a revised capture schema with rendered fields. Opus: the candidate capture directly. **Recommendation:** Sol's `joulewise.transfer_fiducial_result.v1` projection, derived and hash-bound to the reviewed capture. It isolates the public contract from the candidate's verbose/unreviewed schema and makes the largest-edge witness auditable.
2. **Q-R3-2 — What exact quantity and bound names issue?** Sol: `largest_inserted_gap_edge.composed_absolute_residual_bound_s` against `pulse_derived_timing_bound_s`. Fable: raw endpoint maximum against `session_bound.b_fiducial_s`. Opus: candidate `residual_transfer_s` against `b_pulse_s`. **Recommendation:** public names `largest_composed_edge_residual_bound_s` and `pulse_derived_timing_bound_s`, with a witness carrying the raw interval and anchor addend and a source-capture binding to `b_fiducial_s`; this matches the implemented arithmetic without calling a composed bound a raw fitted residual.
3. **Q-R3-3 — Which outcome enum, token, and sentence?** Sol: `supported|not_supported|not_evaluated`, `[TRANSFER_FIDUCIAL_RESULT]`, six-decimal seconds. Fable: `supported|not_supported|inconclusive`, millisecond prose. Opus: candidate `supported|exceeds_bound|inconclusive`, `TR_01_transfer_result`. **Recommendation:** projection enum `supported|not_supported|not_evaluated` and token `[TRANSFER_FIDUCIAL_RESULT]`; fixed six-decimal seconds; each sentence begins `Diagnostic only:` and states both magnitudes when comparable, whether the bound is supported for the studied inference boundary, and that no floor or claim is minted. `not_evaluated` prints authenticated ordered reasons and says transfer remains unestablished.

### Agreed parts — ruling-ready once the questions above are answered

**R1 contract, fixture, test.** Adopt closed authenticated `joulewise.reported_phase_energy.v1`. Exact `cell_id` selection issues gross J/request mean and composed endpoints, runtime-observed J/token, admitted independent-bundle `n`, and replayable parent/member digests. Never use floor-internal mean/count, shrink silently, use fallback counts, render absence as zero, or change floor bytes; `[PREFILL_LENGTH]` comes only from authenticated G2-a+pin. Fixture: alpha/beta prefill+decode 50-member cells with varied points/envelopes/counts, refusal mutations, and a floor-fixture byte copy. One table test asserts all 20 values/relations, refusal scope, exact selection, denominator provenance, and unchanged floor bytes.

**R2 contract, fixture, test.** Decode and selected-prefill families each bind estimate, endpoints, magnitude, armwise-max floor, B, floor clearance/shortfall/ratio, joint sizing, gate outcomes, and verdict; exact names await Q-R2-3. Select exact IDs; keep `F+B` disclosure-only; gate floor by `|estimate|>F` and direction by the full interval plus consistent claim/Holm state; never use D-165. Invalid inputs refuse. Preserve exactly `not evaluated — required token-generation verdict absent`, its `prompt-processing` twin, and `not evaluated — stopped before comparison: <issued reason>`; apply D-166's count split. Fixture: content-addressed decode+prefill (2048), four floors, and supported/failure/count/absence/bad-ID variants. One table test covers DS-29..33, PG-01..08, repeated placements, unrounded cross-checks, `STOP_FILL`, and pseudotoken elimination.

**R3 contract, fixture, test.** TR-01 authenticates the existing estimator revision, exact run/edge census, pulse bound, `diagnostic=true`, and `claim_bearing=false`. One token supplies nine byte-identical, branch-independent sentences; it cannot mint a floor, alter gamma/D-165, or license a claim. Fixture: non-measurement 0.022 s ≤ 0.030067931757111657 s, one >bound case, and one refusal. One test replays all outcomes/copies, mutates every digest, census, maximum, outcome, flag, and equality boundary, and requires all invalid inputs to `STOP_FILL` all nine sites.

**Measurement wait.** This packet issues no live value or claim. R1/R2 wait on G2-a and alpha/beta/gamma `_v5`; R3 waits on final G3 and the lead-controlled zero-agent transfer-fiducial window. Fixtures are non-measurement and non-claim-bearing.

## Residual risk

R1's recommended interval is a new synthesis and needs explicit text before pack regeneration. R2 waits on reconciliation of D-078/D-083 with the artifact guide. R3 must bind a reviewed capture revision, not the unreviewed commit by implication.
