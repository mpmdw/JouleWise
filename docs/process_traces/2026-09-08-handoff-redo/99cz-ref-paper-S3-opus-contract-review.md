**Contract-lens refutation — S3 claim-side bound, worktree `/Users/edr/code/JouleWise-wt-paper-S3`, branch `feat/2026-09-08-paper-S3`, HEAD `ed44276a` (`git diff ac092ccd HEAD`).** Read-only; nothing written.

Executed this session: `python3 -m unittest tests.test_claim_side_bound tests.test_paper_custody` → 51 tests OK; `python3 tests/fixtures/paper_custody/run_kills.py --s3` → **20/20 KILLED**.

---

### 1. BLOCKER — `ratio_estimand` is typed as a string; the real schema makes it an object
`joulewise/analysis_engine/claim_side_bound.py:117-119` requires `metric.ratio_estimand ∈ {"mean_of_request_ratios","ratio_of_totals"}` (bare strings). The authoritative verdict schema is `joulewise/analysis_engine/artifact.py:190` (`_METRIC_KEYS`) → `:1823-1827`, which routes a non-null `ratio_estimand` through `joulewise/analysis_engine/ratio.py:267-284`: it must be an **exact six-key B8 mapping** (`RATIO_ESTIMAND_KEYS`, `ratio.py:34-43`) whose `form` field carries those two strings (`ratio.py:44`). A production ratio contrast therefore presents a `dict`, never a string, and `_project` raises `paper_claim_side_bound_unit_mismatch` for **every** per-token contrast. The contract row rule (`docs/contracts/paper_claim_side_bound.md:56`, "`mean_of_request_ratios` or `ratio_of_totals` with J/token") and the registry binding (`docs/paper/results-fill-registry.md:1138-1141`) restate the invented type as normative.

### 2. BLOCKER — `"J/token"` is not a unit that exists in this repo
Same line, `claim_side_bound.py:118`. The real per-token metric units are `J/committed_output_token` and `J/accepted_draft_token` (`configs/analysis_registry/ap_spec_draft_front.v2.json:115,128`; identically in `ap_spec_native_mtp_front.v2.json`). `grep -rn '"J/token"'` over the repo hits **only** the S3 code, contract and tests. Consequence for the ruling: synthesis item 2's whole point — "a per-token quantity under a `_j` suffix is a BLOCKER" — is installed as a guard keyed on a unit token that can never appear, so it is inert against real verdicts; and `tests/test_claim_side_bound.py:153-166` (`test_ratio_in_j_cell`) manufactures the schema it tests. This is the same defect class the cold gate named and item 7 ordered eliminated (`joining a key the v3 schema does not have`) — the manifest key was cured, the metric vocabulary reintroduces it. Cure: bind `unit` to the registry vocabulary (or accept any nonempty unit and key the `_j` refusal on "unit ≠ `J`"), and read `ratio_estimand["form"]` when the value is a mapping, copying the object verbatim.

### 3. SHOULD-FIX — join injectivity can refuse legitimate co-registered contrasts
`claim_side_bound.py:112-114`. Two contrasts over the same two arms (e.g. an absolute-J contrast and its per-token companion, `ap_spec_draft_front.v2.json:111-128` shows companion/mechanism-diagnostic estimands on the same arms) resolve from the same floor cells in the same order and would refuse `join_not_injective`. Faithful to synthesis 3/Opus 3, but the contract (`paper_claim_side_bound.md:98-99`) records no exemption and no evidence was offered that the production manifest cannot produce this. Recommend an explicit ruling note or keying injectivity on `(contrast_id-independent estimand, cells)`.

### 4. NIT — advertised kill independence is overstated
`tests/fixtures/paper_custody/run_kills.py:104-107`: 11 of the 20 S3 mutations disable the *same* single line, `if row != source:`. Real distinct guards ≈ 9. The 20/20 result is honest as data coverage, not as guard coverage; the contract's clause-to-test table (`paper_claim_side_bound.md:135-160`) reads as if 20 boundaries exist.

### 5. NIT — key overload
Sidecar row key `deterministic_bounds` (`claim_side_bound.py:135`) holds only the verdict's `terms` list, while the verdict's `deterministic_bounds` is the `{terms,total,decision_interval}` object (`artifact.py:225`). Documented, but a reader will misjoin it.

---

### Items 1–7: installation audit
All seven installed and faithful **except** as marked in §1–2 (which sit inside item 2's typing clause).
1. ✔ `claim_side_bound.py:129-136` copies `total` and `terms`; no arithmetic in production paths.
2. ✔ name/`unit`/`estimator_id`/`ratio_estimand` present; **✘ types** (§1–2). S6's `claim_side_bound_j` untouched — 27 hits across `docs/contracts/paper_comparison_rendering.md:106`, `adapter_contracts.md:636-666`, `phase_2/*`, fill-rehearsal JSON, all unchanged.
3. ✔ join re-pointed to `floor.resolutions[].source_cell_ids` — key verified real (`artifact.py:248-256`, `:2272-2313`), statuses `{exact,transported}` and exact→1 cell mirror the owner (`artifact.py:2299-2314`); no manifest schema change (`test_copy_only_control` asserts `source_cell_ids ∉ manifest`).
4. ✔ exact numeral bytes via `_JsonNumber`/`_encode` (`:39-55`); `isclose` confined to `claim_side_bound_diagnostics` (`:190-205`), never consulted by `validate_*`; bool rejected (`_number`, `:58-61`); `_SCHEMA = v2`, v1 refuses (`test_shape_digest_lineage_and_identity`).
5. ✔ `decision_interval` and `metrology_aware_CI95` both copied; contract formulas `d_ik`, `B_k`, `B`, `D=[L−B,U+B]` match `estimators.py:414-419,422-447,478-487` exactly; anchor required (`:127`).
6. ✔ union set present, all 20 killed.
7. ✔ `("claim_evidence","claim-evidence.v1")` registered (`paper_custody.py:651`); grants re-derived from verdict `contrasts` only — the sidecar dict lookup and its three field comparisons are deleted (`paper_custody.py:619-624` removed); invented-manifest-key fixture replaced (`tests/test_paper_custody.py:894-895`); X6/X7 remain `PROPOSED_STOP_FILL` in both `results-fill-registry.md:1204-1205` and `paper_comparison_placements.md:75-76`; D-178 present (`decision_log.md:222, 11161-11213`) and faithful to the synthesis including the recorded dissent.

### Contract quality (item 2 of brief)
`paper_claim_side_bound.md` is closed and replicable: symbols defined before use, formulas verified against `estimators.py`, all nine refusal codes enumerated and each actually raised/returned in code, custody roles delegated to `paper_supply_custody.md`. One stale cross-reference: `docs/contracts/paper_comparison_placements.md:75-76` still says `claim_side_bound.v1 and source-cell join` while the registry twin was updated to v2 — **should-fix**, the two tables are meant to be identical.

### Custody seam (D-173)
Clean. `_claim_issuance_gate` reads the sidecar as raw bytes from `ctx.raws[InputRole.CLAIM_SIDE_BOUND]` and hands the producer only `ctx.raws`-derived objects; the producer opens no paths and accepts no parsed verdict mapping (`_parse` rejects non-`bytes`). No sidecar value reaches `evaluate_claim` — `test_gate_reevaluates_verdicts_with_real_copy_validator` asserts `evaluate.assert_not_called()` on a 1e-13 sidecar drift. The module (parser, serializer, constants) is pinned by `_validator_source_census`'s module sweep (`paper_custody.py:804`) plus `_SCHEMA`/`_ROW_KEYS` in the policy digest (`:810-813`).

### Supply-map repin
Confirmed mechanically: `git diff ac092ccd HEAD -- configs/paper_supply/supply_map.json | grep -v expected_sha256` yields **0** changed lines. Ten digest fields only; no role, mode, gate id or census change.

---

**VERDICT: LAND-WITH-FIXES** — findings 1 and 2 must be cured before any renderer seat binds DS-29 (they make the ratio arm of the adopted contract unreachable and its `_j` guard inert on real data); finding 3 and the `paper_comparison_placements.md:75-76` v1/v2 drift are should-fix in the same round. The copy-only core, exact-numeral custody, re-pointed join, gate registration and hash-only repin are sound as landed.
