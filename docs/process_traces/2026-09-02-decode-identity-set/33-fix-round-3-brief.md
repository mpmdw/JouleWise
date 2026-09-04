WRITE_SCOPE: ["docs/contracts/identity_pin_projection.md", "configs/campaigns/d117_contrast_v5/generate_configs.py", "tests/test_d117_contrast_v5_pack.py", "tests/test_analysis_inputs.py", "docs/decision_log.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# FIX round 3 — decode-identity set (branch fix/2026-09-02-decode-identity-set @ e3f52884+; first round on each of S1, S2, S3)

Authority: `docs/process_traces/2026-09-02-decode-identity-set/32-magistrate-synthesis-s1-s3.md` (read it first; the consult reports are files 30 and 31, the originating counter-review file 28, the packet file 29). No production module under `joulewise/` is in scope — if you believe one must change, stop and return NEEDS_RULING with the evidence.

Checkout: `/Users/edr/code/JouleWise-wt-decode-id` (branch worktree; you cannot commit — the magistrate commits). Set `TMPDIR` to a subdirectory of your scratch dir for every test run. Do NOT run `python3 -m unittest discover`. Hard invariant: `tests.test_d165_dominance_closeout` passes with digest `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`; `git diff -- docs/paper/draft-v1.md` empty.

## R3-A (S2). Install ruling R-2's removal clause in `generate_configs.py`

In `workload_for` (:1313–1323) delete the line `"prompt_tokens": DECODE_PROMPT_TOKENS["A"],` from the decode branch and nothing else. `DECODE_PROMPT_TOKENS` itself stays (it is per-arm; the prefill branch at :1367 and the decode emission at :1552 keep using `DECODE_PROMPT_TOKENS[arm]`). The plan's shared `stack_scope.measurement_arms.decode.workload` (written by `build_plan`, :1758, into `calibration_plan.json`) then carries the common profile alone: `{"name": …, "repetitions": 1, "warmup_runs": 1, "output_tokens": 512}`. Do NOT add `suite_manifest_set` or any pointer key to it (synthesis §S2).

Pin it in `tests/test_d117_contrast_v5_pack.py` next to the existing plan read (~:863): assert the decode workload in `calibration_plan.json` equals exactly that four-key common profile, has no `prompt_tokens` key, and equals the declared common profile of BOTH identity units' `declared_identity.workload_profile` with `suite_manifest_set` removed. Counterfactual (paste): restore the deleted line in memory (monkeypatch `workload_for` or re-exec the function source) and show the new assertion fails.

## R3-B (S1). Contract: the freeze-procedure list and the paragraph at :481–486 — DICTATED, verify each clause against the code

Every clause below was bench-verified by the magistrate against `joulewise/identity_pins.py` (`_read_unit_configs` :1436–1457; `_derive_projection_units` :1588–1640; `_declared_manifest_path` :1541–1568; `_resolve_config_path` :1245–1259). You VERIFY each clause and paste the proving line in your report; you may correct a factual error ONLY by quoting the contradicting code line; you may not add, remove or rename any term. Wrap at 79 columns.

(1) Replace step 1 (:451–452) with:

> 1. It reads every inventoried configuration's raw bytes, requires their
>    SHA-256 to equal that inventory row's digest, and parses each as a JSON
>    object. Typing through `BenchmarkConfig` happens later, per
>    configuration, inside the comparison of steps 2–3.

(2) In step 3 (:456–462), after the clause "removes only `suite_manifest_set` from the stored workload to obtain the declared common workload profile," insert, as its own sentences before "and removes only `suite_manifest_ref` …" (rephrase the join so the step reads as prose; keep every existing clause):

> It then resolves each declared member's `suite_manifest_ref` — a
> repository-relative path, of which only the part after the pack directory's
> name is kept — as a regular, non-symlink file whose resolved path stays
> below the pack root, reads it, and requires its SHA-256 to equal the
> member's declared `suite_manifest_sha256`. A reference that cannot be
> resolved that way, a file that cannot be read, or a digest that differs
> refuses with reason code `readiness_identity_environment_dirty` ("declared
> suite manifest is unauthenticated") before any configuration's declaration
> is compared.

(3) Replace the paragraph at :481–486 ("The identity projection authenticates the inventoried configuration bytes. … refuses in step 4.") with:

> The identity projection therefore authenticates two kinds of bytes inside
> the campaign-pack directory (the pack root) before it compares any
> declaration: every inventoried configuration's raw bytes against its
> inventory digest (step 1) and, when a suite-manifest set is declared, every
> declared manifest member's file against its declared digest (step 3).
> Within this contract, an unauthenticated manifest binding means either a
> declared manifest member whose reference cannot be resolved below the pack
> root, whose file cannot be read, or whose file bytes do not hash to its
> declared `suite_manifest_sha256` — each refuses in step 3 with
> `readiness_identity_environment_dirty` — or a configuration whose manifest
> digest and reference are not present as the exact declared pair, which
> refuses in step 4.

Then check every other sentence of the contract and every executable-evidence row that quotes the replaced text (the round-2 brief found one near :968) and report each hit with what you did. First-use table for the new text in your report (term → first-use line → definition line); `declared manifest member` is the contract's defined term (:90–98) — confirm.

## R3-C (S3). Contract limitation at the lineage layer — DICTATED — plus the direct-seam test

(1) In `docs/contracts/identity_pin_projection.md` §Analysis consumption, after the sentence ending "The analysis input gate follows that already-authenticated root to the plan-pinned U8 readiness freeze receipt, …" paragraph (:583–591 — insert as a NEW paragraph after that one), insert:

> That root is the machine-absolute pack path recorded when the arm was
> consumed. Bundle loading authenticates the launch lineage before any
> evidence row exists: it replays the consumed arm and resolves the recorded
> pack root strictly, as it resolves the consumption receipt, the launch
> manifest, the window root and the lifecycle receipts, so a bundle whose
> arming-time paths no longer exist is refused at input loading
> (`launch_binding_mismatch`, or `launch_consumption_missing` when the
> consumption receipt itself is gone) and never reaches this gate. Analysis
> of successor-lineage bundles therefore runs on the filesystem that armed
> them; making the lineage relocatable is a separate design lane, not a
> property of this gate. Called directly with a lineage whose pack root does
> not resolve, the gate refuses with `consumer_identity_set_unauthenticated`,
> the same label as any pack it cannot authenticate.

Verify each clause against `joulewise/analysis_engine/inputs.py:2770–2783` (`_read_bundle` → `authenticate_bundle_launch_lineage`), `joulewise/arm_readiness.py:9330–9352` (`_replay_consumed_arm` strict resolve), and the consumption/manifest/window/lifecycle resolves Fable cites in file 31 (`arm_readiness.py` `_read_v2_consumption` ~:8960–8985; `:10200–10205`, `:10222`, `:10233–10252`) — paste the lines. Correct only by quoting the contradicting line.

(2) In `tests/test_analysis_inputs.py` (class `FrozenConsumerIdentitySetTests`), add `test_missing_pack_root_refuses_with_unauthenticated_label`: generated frozen pack; rewrite the exact-cell case's lineage `pack_root` to a non-existent absolute path (keep the honest `pack_sha256`); assert `_frozen_consumer_identity_set` returns `frozenset()` and the production seam (`_production_floor_resolution`) returns `status == "refused"`, `reason_codes == ("consumer_identity_set_unauthenticated",)`. Counterfactual (paste): remove `OSError` from the catch-all at `inputs.py:4039–4048` in memory (re-exec the function source) — the test must fail with a propagated `FileNotFoundError` instead of the refusal.

## R3-D (Opus nit 2). Decision-log dated addendum — DICTATED

`docs/decision_log.md:8462` reads "several members use the R-1 domain-separated set digest". Do NOT edit that line. Append immediately after that paragraph (before the next `###` heading) the addendum:

> *Addendum 2026-09-02 (Opus counter-review nit 2, trace
> `2026-09-02-decode-identity-set/28`): the set digest above is ruling 171a
> R-5 (unit config-set digest), not R-1; R-1 is "exact identities stay
> exact". The original line stands as written.*

## Verification (paste tails)

`python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_docs_freshness` (report the count; 446 skipped=1 was the seven-module figure before `tests.test_d117_contrast_v5_pack` was added to the list). `git diff --check`. `git diff -- docs/paper/draft-v1.md` empty. `shasum -a 256 configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` = `1c0a4a11…`.

## Report

`claude-codex-report/v1` envelope, genre implementation; JSON block under 8 KB. Markdown body: per clause R3-A..R3-D the biting test `file:line`, the counterfactual, and the pasted RED tail (or `NOT PINNED: <reason>` — never a pin you did not execute); the R3-B and R3-C clause-verification tables (clause → proving line); the first-use table; suite tails. Do not end the turn mid-flight; complete the brief or return NEEDS_RULING/NEEDS_SCOPE.
