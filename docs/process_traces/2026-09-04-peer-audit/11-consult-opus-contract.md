# Three-seat consult — OPUS seat, CONTRACT lens (2026-09-04)

Worktree `JouleWise-wt-consult-opus`, detached at `5e416c47`, read-only apart from this file; every code fact was
executed or read this session. Lens: the contract, decision entry or registry row each remedy touches; **RELABEL**
(prose/metadata only) vs **SEMANTIC**; and the re-pin it forces.

## Q1 ESTIMAND — **PARTLY**: the witness is correct, but this is not a contract defect. Remedy (a), enclosure as a desk script.

**Evidence.** P1 reproduces exactly:

```text
interval_average_point_J=9.000 interpolation_bound_J=0.000 envelope_J=[8.800, 9.200]
two_gate outcome=direction_supported claim_ready=True
```

`reduce.py:167-180` integrates `power_w * overlap`; `:519-520,554-555` hard-return `0.0` for interval-supported
traces. Two 20 W/0 W half-record histories give identical record averages and admit [8, 10] J, which the
[8.8, 9.2] J envelope excludes. The counterexample holds.

**Where I part from the auditors.** This is not code-vs-contract. `run_bundle_layout.md:805` says verbatim:
*"overlap clipping is the point estimand, while clock/marker uncertainty remains separately bounded."* The frozen
contract declares the allocation estimand; the defect is the paper's promotion of it to physical phase energy
(`draft-v2-skeleton.md:1387`). Remedy (a) is **RELABEL**; nothing frozen changes value.

**Contract impact.** Edit the estimand sentences in `draft-v2-skeleton.md` (1387/1393/1399 + §2 methods), which is
unpinned. Do not touch `draft-v1.md`: pinned by SHA `939dfa23…` in the registry header, so any edit forces a
registry regeneration. `run_bundle_layout.md:805` needs no amendment. One decision-log **addendum**, not a new
decision.

**Enclosure: desk script, not `reduce.py`.** A new `summary_metrics.json` field crosses a version boundary —
`reduce.py:99-109` pins `0.5.0/0.5.1/0.6.0/0.6.2` and `run_bundle_layout.md` freezes the roster per version with a
legacy strict-comparison allowlist — forcing a reducer bump, contract amendment, allowlist entry and re-reduction:
SEMANTIC-shaped cost for a diagnostic. The enclosure needs only raw plist records and the frozen window bounds,
both retained. Desk script → appendix figure → one registry row ruled `DERIVE`. **Cost:** ~1 day; no
re-collection, no re-pin.

## Q2 D-165 — **AGREE** on both. The retained sweeps do **not** carry the coordinates. Relabel now; rebuild optional.

**Evidence, executed.**

```text
common_time_shift_ratio=2.250368 passes=True
shared_energy_sign_ratio=1.500000 passes=False
```

**Wrong substitute? Yes.** `dominance_closeout.py:278-333` reduces each block's sweeps to
`zero_centred_width = max(|lower|,|upper|)` — a per-block extremum over that block's own grid — then `:683-700`
applies one `shared_sign` to those heterogeneous widths. A common *time* shift gives
`dE_i/dt = P_i(end) − P_i(start)`, differing per block in magnitude **and sign**; sharing an energy sign moves
every block together and destroys the dispersion a real shift creates.

**Absolute cancellation wrong physics? Yes, as written.** `dominance_closeout.py:51-55` says a *"uniform shared
fiducial shift cancels exactly"* from deviations from the mean. A uniform additive **joule** offset does; a
uniform **fiducial time** shift induces per-run changes `dt·(P_i(end) − P_i(start))`, of which only the common
component cancels, leaving the run-to-run spread of edge powers. That residual is probably small, but the string
asserts exactness and is emitted into artifacts.

**Coordinates retained? No — worse than the audit says.** Grids are built per block from that block's own record
support edges (`floor_extraction.py:2495-2503`, `:2539-2540 onset_shifts_s=sorted(onset_candidates)`), so index
*k* of two blocks is not the same shift; and `_CommonModeBlockInputs` (`:245-253`) has **no shift-coordinate field
at all** — only sweep values, zero point, residual half-widths, window bounds and envelope sum. A shared-onset or
shared-offset replay is a re-extraction from raw bundles, not a sidecar re-analysis.

**Direction of the error — the audits omit this, and it sets the remedy.** `replay_common_mode_dominance` has no
consumer outside `dominance_closeout`; the operative gate `active_floor_j` comes from the mint
(`analysis_engine/__init__.py:273-283`). The defect touches the **methods headline R ≥ 2**, not claim
admissibility, and in P2 the issued formula returns the *lower* ratio. No claim can be admitted through it.

**Remedy: RELABEL.** Rewrite `ABSOLUTE_COMMON_MODE_REASON` and its mirror at
`d117_contrast_v5/generate_configs.py:514-519` to "a uniform additive energy offset cancels from absolute
residuals; no absolute common-time replay is implemented". The string is emitted, so bump
`COMMON_MODE_REPLAY_RULE_ID` (`dominance_closeout.py:50`, `…replay.v1`) to `.v2` and file a **D-165 addendum**
withdrawing the physical common-mode interpretation — pre-collection, so nothing issued is invalidated. In the
paper, `draft-v2-skeleton.md:29,1145` "the same timing error moved together" becomes "a second calculation
retaining a shared sign for block-level energy allowances." The rebuild (persist grids, replay one shared onset
and one shared offset) is a bounded day and cheaper now than ever — fund it only if the comparative R ≥ 2 arm
stays load-bearing. **Cost:** relabel 2–3 h; rebuild ~1 day, no re-pin (nothing issued).

## Q3 F+B METADATA — **PARTLY**: right direction, but not metadata-only — it has an exact-equality blast radius.

**Evidence.** `detection_floor.py:348-362` emits `effective_clearable_effect_formula="floor_j + claim_side_bound_j"`
with `both_terms_required: True`, while `claims.py`/`estimators.py` implement two independent gates; P1's example
(estimate 6, floor 5, deterministic 4) reproduces `direction_supported / claim_ready True` at 6 < 9. F+B is a
sizing quantity, not the implemented threshold — I side with the auditor against D-083
(`decision_log.md:5315-5327`), which preserved the phrase with Sol's dissent recorded.

**Why not metadata-only.** The object is compared for **exact equality** at seven sites —
`detection_floor.py:3346, 3835, 4105`; `floor_extraction.py:1433, 3121`; `analysis_engine/artifact.py:491`;
`analysis_engine/__init__.py:258, 295` — each raising *"must preserve the clause-11 composition rule"*. Its bytes
are frozen in **`adapter_contracts.md:618-637`**, mirrored in two `docs/phase_2/` contracts, and baked into 14
`docs/paper/fill-rehearsal/dominance-reproduced-*.json`. Any change invalidates every artifact carrying the old
object.

**Accepted shape.** Keep the two-gate rule unchanged; rename the key → `planning_sizing_expression`, set
`both_terms_required: False`, add `role: "prospective_sizing_diagnostic"` and `not_an_acceptance_gate: True`,
bump `SINGLE_COUNT_DISCIPLINE_ID` (`detection_floor.py:113`) to `.v2`. Requires a **D-078 clause-11 amendment**
(`decision_log.md:5282`) and a **D-083 addendum** recording that enforcement is unchanged and only the description
corrected — Sol's dissent partly vindicated on the mathematics, still overruled on the gate.
`adapter_contracts.md` moves in the same commit (frozen contract → cold-gate item); the 14 rehearsal JSONs
regenerate. Effect **RELABEL**, mechanism a schema bump. **Cost:** half a day plus one cold-gate ratification.

## Q4 FLOOR vs CONTRAST PROMPTS — **PARTLY DISAGREE** with 03-F3. Mirror the rotation into the floor packs.

**Evidence the audit missed — the eight prompts are shape-identical, enforced in code.**

- `configs/model_panels/qwen3_4bit.json`, pinset `qwen3-real-prompts-v1-thinking-off`: executed — all eight
  prompts render to **42 prompt tokens** (`[42] 8`), one tokenizer.
- `d117_contrast_v5/generate_configs.py:975-981` **refuses** `decode_prompt_shape_mismatch` unless every
  rendering in an arm shares one `prompt_tokens` value.
- `:1539` `greedy_forced_512_suppress_eos` — decode forced to exactly 512 tokens, EOS suppressed.
- `:1693` rotation applies **only** to the decode arm; prefill uses the pinned `prefill_prompt_pin`.

So the transfer is across prompt **content** at fixed shape, not across workloads. Ruling 171a R-7
(`decision_log.md:8478`) authorises the split: *"Floor producer and consumer units bind through condition-family
transport; their config-set digests are not required to be equal."*

**Where I agree, sharpened.** `configs/floor_mint/condition_family_df_ph_decode.json` defines a family by
`workload_profile{prompt_tokens, output_tokens, repetitions, warmup_runs}` — **no prompt identity** — so the
difference is invisible to `transport_verdict`, which returns `exact` (`analysis_engine/__init__.py:280-283`).
And the floor is a between-block scatter bound: the demonstration varies prompt between blocks, so prompt-content
variance sits in its scatter but not in a prompt-0 floor. That is floor **understatement** — the dangerous
direction, and prose cannot cure it.

**Choice: regenerate the floor packs to mirror the contrast rotation exactly.** Both have ten decode ABBA blocks
(floor `:586-593`; contrast `:1487`), so the identical rule `prompt_index = (block_number − 1) mod 8`, prompt
constant within a block (as `decode_prompt_index(block)` already does, `:1734`), gives the same 10-over-8
weighting — doubling of prompts 1 and 2 included — in floor and demonstration alike. The imbalance then
**cancels** rather than needing disclosure, and the floor absorbs prompt-content scatter. Contrast-on-prompt-0 is
the weaker paper; disclosure-only leaves an understated floor.

**Re-pins.** `ruling-171a-floor-index-zero.v1` (floor `:1031-1034`, `prompt_count: 1`) is superseded → new rule
id under a **ruling 171a amendment**; the rendering selection at `:895-926` (pins `sky_color`, refuses
`decode_index_zero_rendering_mismatch`) must accept the full pinset; `"block_id": "single_prompt"` (`:1000`)
renamed; then per pack: scientific-config identities → unit `config_set_sha256` → frozen projection → **custody
reissue with a `supersedes` record** (ruling 171a clause 4). Record the rotation rule in the condition-family JSON
so transport is verifiably exact. **SEMANTIC for the packs, zero issued results affected. Cost:** one Sol seat
day for both packs plus census check and amendment; run counts unchanged.

## Q5 TRANSFER — **AGREE**. Withdraw the TR-01 dependency now; the protocol is not a one-week item.

`draft-v2-skeleton.md:1298-1301` says the protocol is not runnable (sleep actuation, command-stamp method,
fitted-edge selection unfixed); `:1324-1326` says there is no acceptance threshold; the registry row
(`results-fill-registry.md:920`) is `STOP_FILL / SUPPLIER_NAMED / VALUE_UNISSUED; TOKEN_MISSING`. A runnable
protocol *with a contemporaneous acceptance predicate* needs a sign-and-baseline redefinition of a detector built
for positive ~1 s rectangular pulses, a pre-registered predicate (one chosen after seeing residuals is not a
predicate), and a quiet window — three gated items in a week that already owes a campaign. Do not fund it.

**Contract cost of withdrawal.** The row carries *"no branch selection may remove this placement"*, so this is a
**registry amendment**, not an editorial cut. `[FILL:TR-01]` occupies nine sentences
(`draft-v2-skeleton.md:29,35,41,1145,1153,1161,1387,1393,1399`) plus the selector census
(`select_outcome_branches.py:21,176`) and its test. Replace the marker with fixed prose — "Transfer of the
pulse-derived timing allowance to inference was not tested" — keeping the placement so the census stays at three,
and retire the row to a `LIMITATION` entry. **RELABEL**, plus a registry regeneration and a withdrawal addendum;
strip the conditional-on-transfer phrasing at `:1145` in the same pass as Q1. **Cost:** 2–3 hours.

## Q6 SCOPE FREEZE — **AGREE** with 01-F4/01-F10

| Lane | Verdict | Paper object / reason |
|---|---|---|
| Whole-window stop receipt | **KEEP** | The Refusal branch's evidence (`draft-v2-skeleton.md:41,1161,1399`, `[FILL:OR-01]`); without it the likeliest outcome cannot render. |
| Claim non-issuance receipt | **KEEP, minimal** | Same branch; makes "no claim was issued" a *result*. Cap at the receipt the renderer reads. |
| AUTH allowlist guard | **PARK** | Defends against the trusted operator the draft declares out of scope (`:1283`). |
| Paper-supply custody seam (D-173, `decision_log.md:10903`) | **KEEP, five typed refs only** | Three lanes failed three rounds each on one defect class; every remaining supplier crosses it. Land the seam, not a governance subsystem. |
| Kernel rows | **PARK** unless a row supplies a named FILL | Bookkeeping. |
| Skill-distill packet | **PARK** post-submission | No paper dependency. |
| LINEAGE | **PARK** | A §Availability provenance paragraph substitutes at ~1% of the cost. |
| MODULARITY | **PARK** | P3 by the project stack. |

Rule to ratify with the freeze: **every remaining task names the figure, table or refusal sentence it enables, or
it does not run** — a process rule, so a cold-gate item under rule 11.

## Q7 LEGACY L1 — **AGREE**. Accept only the **retire-from-publication-routes** shape.

`scripts/build_capstone.py:34` still owns `LEGACY_LABEL = "legacy L1 (manual review; pre-2M)"`; the generated
page publishes the 47.2 J / 304.0 J gross means and calls idle-subtracted energy primary; `--check` returns
`build_capstone: check OK (no drift)`, a hash certifying faithful reproduction of voided numbers, while
`README.md:59` voids the corpus and `:71` makes gross energy the policy.

The "voided historical demonstration" shape is acceptable **only** if the numbers leave the generated artifact:
a page that keeps the table and adds a banner is one screenshot from being cited. Remove the table from the
**producer** (Markdown edits are undone by regeneration), keep the pipeline demonstration, and keep one
regression asserting the void disposition.

**Contract impact.** No frozen result changes — already void — so this is a **RELABEL** aligning a route with an
existing ruling. No new decision needed (D-161 evidence-fence enforcement), but file a one-line addendum naming
the route closed so regeneration cannot reopen it; raw bundles and past snapshots untouched. **Cost:** hours;
best return per hour in the set.

---
