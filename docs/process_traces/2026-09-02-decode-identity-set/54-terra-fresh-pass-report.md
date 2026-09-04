# §5 fresh pass + delta re-audit at 28060067 (terra xhigh + wrapper adjudication), verbatim

Adjudication complete. Seat report consumed into the manifest (`accepted`, lead re-verification `match`).

## Verdict: NOT LANDABLE at 28060067 — two one-line bench cures away from LANDABLE

Seat: gpt-5.6-terra xhigh, read-only (workspace-write, `WRITE_SCOPE: []`), run `20260904T025359Z-8613-terra-report`, envelope valid/final. Report: `<tmp>`. My replay probe: `.../decode-id-fresh-pass/probes/real_hops.py`.

### Findings (lead-adjudicated; seat concurrence noted)

| id | sev | line | evidence |
|---|---|---|---|
| L1 | SHOULD-FIX | :573 | Bench edit S4 restored a STALE citation. `identity_pins.py:2100-2234` was `verify_frozen_projection` at merge-base (line 2100 = its `def`); the branch added 299 lines above it. At HEAD 2100-2234 = `_receipt` (2098), `_load_frozen_receipt` (2132), `_frozen_pack_matches_receipt` (2179), `_frozen_pack_identity_matches_receipt` (2201), `_atomic_write_set` (2216). `verify_frozen_projection` is now 2379-2513 (load call :2403, `try:` :2411). Cure: cite `joulewise/identity_pins.py:2379-2513`. `arm_readiness.py:5681-5729` = `_run_identity_arm_reverification`, valid at HEAD and origin/main. Seat F2 concurs. |
| L2 | SHOULD-FIX | :621 | "runs root" — sole occurrence in the contract, never built or glossed (lineage-locator bullet). The file-52 extractor MISSED it (not among the 39 rows), so its "every noun phrase of two or more words" claim is incomplete. Cure: "in a runs root (the directory under which that launch's collected bundles are written)". Lead-added; seat did not flag. |
| L3 | NIT | :589 | Pack-digest gloss "SHA-256 of the committed campaign-pack tree". Producer `committed_pack_tree_sha256` (`arm_readiness.py` ~2750-2874): `git ls-tree -rz --full-tree HEAD -- <pack>`, verifies each disk file's bytes+mode equal the committed blob, then SHA-256 over domain `joulewise.committed_pack_tree_sha256.v1\n` + sorted path/mode/content framing. Not a git tree-object id. Contract :704-706 already says "computed by `committed_pack_tree_sha256` … from its committed bytes", so the gloss is consistent, not false — under-specified. Seat F1 rated SHOULD-FIX ("not literally the Git tree digest"); lead downgrades with dissent recorded. Suggested: "(a SHA-256 over the committed campaign-pack files — paths, modes, bytes)". |
| L4 | NIT | :589 | "consumed arm authorization" used one bullet before "single launch authorization" (:591) and "Consuming" (:615) are built — intra-block forward reference. |
| L5 | NIT | :629/:644/:683 | "analysis gate" / "analysis input gate" / "the gate": three spellings, alias undeclared (S1's class). Cure at :644: "The analysis input gate (the analysis gate)". |
| L6 | NIT | :682 | "[S3 ruling (d)]" is internal process shorthand as link text on a contract page. |
| L7 | NIT | :643 | "successor packs" first use unglossed; legacy/successor split only arrives :691/:728 (pre-existing text). |
| L8 | NIT | :13 | Status clause uses "launch-lineage" before its :588 build (mitigated: names the section). |

### Charge 1 — the seven bench edits

| edit | closes? | new claim true? | evidence |
|---|---|---|---|
| :468 "below the campaign-pack directory" | S4b yes | yes | `_declared_manifest_path` docstring "regular file below its pack" (`identity_pins.py:1541-42`); "campaign pack" built :38 |
| :572-573 citations | S4a in form | PARTLY FALSE | L1 (pins range stale); readiness range valid |
| :589 pack digest gloss | S2 yes | true, imprecise | L3 |
| :629-630 "consumer's distinct member identity set, built above" | S3 yes | yes | built :109; `_frozen_consumer_identity_set` re-derives the unit's identities, checks `identity_unit_config_set_sha256` vs `config_set_sha256` (`inputs.py` ~4030-38); empty → code at 4082-87 |
| :657-659 bundle/input loading alias | S1 yes | yes | `_read_bundle` → `authenticate_bundle_launch_lineage(..., require_completion=False)`; `LaunchLineageError` → `AnalysisInputError` (`inputs.py:2773-2782`) |
| :675-676 sidecar gloss | N4 yes | yes | sidecar built :176; writers `namespace / f"{receipt_name}.sha256"` (`arm_readiness.py:7682, 7975, 8446`; consumption 9770) |
| :733 "ordinary launch step" demoted | S2 yes | n/a | ordinary phrase; no symbol bears the name (`launch_window.py:239-267`) |

### Charge 2 — 39-row triage (lead re-derived; * = extractor stem/hyphen artifact)
- Built: campaign pack directory (:38); arm ceremony* (:152 "Arm is the readiness ceremony"); one use record (:599-600); pack root recorded (:592); consumption receipt recorded (:599); `.sha256` (:176); bundle loading use* (:657); analysi gate definition* (:582 heading); committed campaign pack tree (:535 "committed checkout", :704-706) — DIVERGES from seat, which called this row the DEFECT behind F1.
- Glossed at first use: launch lineage refusal code used (:624); consumer identity set unauthenticated (:629); launch lineage required + tag (:654); untagged bundle, lineage checked bundle (:654-655, by the tag sentence); bundle loading, bundle to analysi admission step*, input loading (:657-659); execution order (:662); digest file (:675).
- Ordinary: analysi consumption* (:13), launch lineage sentence, arm decision, layer map*, readiness refusal (:572), absolute path (:593), reviewed command (:597; "reviewed" :43), launched window (:614), launch lineage record (:620), absolute artifact path (:622), order bundle loading* (:662), later artifact, listed code, receipt itself, separate design decision.
- NIT: consumed arm authorization (L4), analysi gate (L5), s3 ruling (L6).
- DEFECT: `joulewise/identity pins.py 2100 2234` (:573, L1).
- Missed by the extractor: runs root (:621, L2).

### Charge 3 — my executed hops on a REAL settled lineage (`LaunchConsumptionV2Tests` fixture → `_settle()` → delete one artifact → `authenticate_campaign_launch_lineage`)
Control: NO ERROR. Single hops: locator → `launch_consumption_missing`; consumption → `launch_consumption_missing`; arm → `launch_consumption_invalid`; pack_root → `launch_binding_mismatch`; manifest → `launch_consumption_invalid`; window plan root → `launch_binding_mismatch`; window.env / window-chain.zsh → `launch_consumption_invalid`; start / settle → `launch_lifecycle_incomplete`. Cascade k=0..6: missing / invalid / binding_mismatch / invalid / binding_mismatch / lifecycle_incomplete / lifecycle_incomplete. Sidecars: consumption `.sha256` → `launch_consumption_missing`; start `.sha256` → `launch_lifecycle_incomplete`; locator `.sha256` → `launch_consumption_missing`. C18: completion absent + `require_completion=False` → NO ERROR; `=True` → `launch_lifecycle_incomplete`. Sibling custody dirs confirmed (`arm_readiness.consumptions` / `arm_readiness.receipts`, same parent); `window.env.resolve().parent == window_plan_root.resolve()` (the `/var`→`/private/var` symlink is the only reason a naive compare fails). All 23 rows match the contract and file 51; the seat independently executed 8 rows, all PASS. Note: the cold-gate `46a-coldF-cascade.py` disagrees at S4/S6/S7, but that script leaves a `b"{}"` manifest on disk with a mismatched digest and stubs argv binding — an artifact of its mocks, not evidence. No exhaustiveness claim (:661-662). Status clause names `arm_readiness.py` + `analysis_engine/inputs.py`; the behaviour lives in `inputs._read_bundle` (2735-2782) and `arm_readiness.authenticate_launch_lineage` / `authenticate_campaign_launch_lineage` — confirmed by execution.

### Charge 4
`git status --short`: clean (0 lines). Tests: `tests.test_analysis_inputs tests.test_arm_readiness_lifecycle` → 84 OK, skipped=4 (lead replay). Paths outside the union of briefs 07/13/15/23/33/49 and the trace dir: `docs/process_traces/2026-09-02-fresh-fable-audit/01-05` (commit fc52bda6, magistrate custody, not a seat commit; absent on origin/main so they land with this PR — `05-ed-email-batch2-UNSENT.md` included). Everything else is in-scope.

### Process observation (for the magistrate, not a ruling)
A bench cure re-asserted a line-range citation that the branch's own +299-line growth had already invalidated — the "citation as verified prose" signature again. Function-name citations (or ranges re-checked at every bench edit) would close this class.
