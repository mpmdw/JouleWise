# 69a — Opus 5 contract-lens refuter over V5-PREFILL-REALIZED-IDS-CHECK-01 (`0d14893e`) — CLEAN, three nits

Seat: Opus 5 (Agent, read-only) checking ruling 44c + 49b clause by clause
against the 14-file diff. Suites `Ran 458 … OK (skipped=1)`; hash `1c0a4a11`;
`gen_state.py --check` rc 0. Every clause SATISFIED (clause table in the
agent's report; summarized here): closed omission-serialized carrier
(`schemas.py:842-895`, `:1137`), one comparison home `BundleReader.problems()`
(`bundle_read.py:803-810`, `:918-1063`), three reader names with mismatch text
naming count/hash/domain, unwaivable incl. scope `any`
(`run_campaign.py:224-226`, `:452-455` above the `any` early-return at `:465`;
test `test_prompt_realization_reader_codes_are_unwaivable_including_any`),
frozen registration untouched, 49b call sites only, legacy `to_dict()` golden
(`test_schemas.py:417`), no `ConfigKeyWarning` (`:337`), first-mismatch stops
before child two (`test_run_campaign.py:5959`).

## Nits (recorded; no change)
1. `build_plan` (`generate_configs.py:1844`) hardcodes arm A for the plan's
   single workload slot — structurally forced; per-arm configs are correct.
2. Marker-surface ABSENCE yields unwaivable `evidence_missing` rather than
   `evidence_inconsistent` — consistent with 44c "absence is never a pass";
   `mlx_runtime.py:706/731` emit both markers on the single-prompt path.
3. Privacy allowlist admits the container key only; inner-key closure comes
   from `_require_exact_keys` + `additionalProperties:false` — same precedent
   as `prompt_token_evidence_policy`.

Execution/mutation lens: luna (trace 69), pending at the time of this record.
