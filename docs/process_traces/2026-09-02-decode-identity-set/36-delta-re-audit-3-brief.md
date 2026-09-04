WRITE_SCOPE: []
ORIGIN: claude-magistrate  HOP: 1  GENRE: review  READ-ONLY (workspace-write with an empty write scope: write NOTHING under the checkout; use only $TMPDIR)

# Delta re-audit of decode-identity FIX ROUND 3 (`791a2522..<HEAD>`) — execution lens + pedagogy as its own dimension

Checkout: `/Users/edr/code/JouleWise-wt-decode-id3`, detached at the round-3 head (run `git rev-parse HEAD` and quote it). Under review: `git diff 791a2522 HEAD -- configs docs/contracts docs/decision_log.md tests` = Sol 266's landing + the magistrate's bench assertion block (`tests/test_d117_contrast_v5_pack.py` ~877–898). Authority: `docs/process_traces/2026-09-02-decode-identity-set/32-magistrate-synthesis-s1-s3.md` (what was ruled), `33-fix-round-3-brief.md` (what was ordered), `34-…` (the seat's report), `35-…` (bench ruling). The consult reports are files 30 (Sol) and 31 (blind Fable). This is the FIRST fix round on each of S1/S2/S3; if any cure does not bite, say so plainly — do not lower a severity.

Run every test with `TMPDIR` under your scratch dir; never `unittest discover`; mutations on in-memory copies only; write nothing under the checkout.

## A. Execution lens

A1. S2 (`generate_configs.py:1321` removed; pin at `tests/test_d117_contrast_v5_pack.py` ~864–898). (i) Counterfactual: re-add `"prompt_tokens": DECODE_PROMPT_TOKENS["A"]` to `workload_for`'s decode branch in memory and paste the failure. (ii) Own mutants: a plan workload missing `output_tokens`; a declared profile whose `suite_manifest_set` is absent; a declared profile with an extra NON-null key (e.g. `prompt_tokens: 42`) — which of these the assertion block kills, one line each KILLED/SURVIVES. (iii) Is the None-drop ruling (file 35) sound: enumerate the typed workload fields that can be None in `BenchmarkConfig`'s workload model (cite the dataclass/model lines) and say whether any None-valued field could legitimately be declared non-null for a decode unit in a way the assertion would wrongly pass or fail. (iv) `DECODE_PROMPT_TOKENS[arm]` still emitted at :1366/:1551 for the configs — confirm the per-config decode workload still carries per-arm `prompt_tokens`? (Fable's probe in file 31 says emitted decode configs carry NO `prompt_tokens`; Sol 266 says `DECODE_PROMPT_TOKENS[arm]` remains at :1551 — resolve the contradiction by executing: print an emitted decode config's `workload` for each arm.) (v) D-166 digest and `tests.test_d165_dominance_closeout` tail.

A2. S3 test `tests/test_analysis_inputs.py::FrozenConsumerIdentitySetTests::test_missing_pack_root_refuses_with_unauthenticated_label` (~:706). Counterfactual: drop `OSError` from the catch tuple at `inputs.py:4039–4048` in memory (paste the error tail). Second mutant: make `resolve(strict=True)` at :3897 non-strict — does the test still pass (it should: `committed_pack_tree_sha256` raises) — say what that means for what the test does and does not pin.

A3. Round-2 tests still bite: re-run the F-B test (`test_self_consistent_forged_pack_requires_launch_tree_digest_binding`) with `:3898` → `if False:` and the R2-B test with the gate body → `return frozenset()`; one line each KILLED/SURVIVES.

## B. Pedagogy + factual dimension on the three contract texts

B1. Freeze-procedure steps 1 and 3 (`docs/contracts/identity_pin_projection.md` ~451–473) and the paragraph ~491–501: grade EVERY clause PROVEN / OVERCLAIMED / UNDERCLAIMED with the proving line in `joulewise/identity_pins.py` (`_read_unit_configs` :1436–1457; `_derive_projection_units` :1588–1670; `_declared_manifest_path` :1541–1568; `_resolve_config_path` :1245–1259). Then EXECUTE the ordering probes from file 31 §Q3 (a generated pack with (1) manifest bytes tampered only, (2) config bytes AND manifest tampered, (3) config bytes only, (4) declaration drift AND manifest tampered, (5) declaration drift only) and paste which message each produces — the contract's claimed order (configs read in step 1, manifest authenticated in step 3 before declarations are compared, pair check in step 4) must be the executed order.

B2. The lineage-layer paragraph (~609–621): per clause, the proving line in `inputs.py:2768–2783` and `arm_readiness.py` (:9333–9352, :8960–8985, :10200–10205, :10222, :10233–10252). Execute at least the consumption-receipt hop (Fable's probe 3) and the `_replay_consumed_arm` hop with a non-existent `pack_root` — paste the reason codes. Is "the same label as any pack it cannot authenticate" true (list the gate's refusal exits that share it)?

B3. First-use table for all three texts — build your own, do not copy Sol 266's; report any term Sol's table missed or mis-cited. Cold read: from the contract alone, can a reader state WHY a bundle from a clone never sees `consumer_identity_set_unauthenticated`?

B4. `docs/decision_log.md:8464–8467` addendum: verify R-5 is the unit config-set digest ruling and R-1 is "exact identities stay exact" in `06-ruling-171a.md` (quote both lines).

## C. Same-signature statement (mandatory)

Did this round produce a defect of the SAME CLASS as a previous round — a closure without a biting test (F-B class), a first-use/ordering defect in contract prose (F-N/F2/S1 class), or an uninstalled ruling clause (S2 class)? YES/NO per class with evidence. A YES on the prose class would be the FOURTH consecutive; say so.

## D. Suite tails

`python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_docs_freshness` (expected 487 OK skipped=1). Paste exact tails.

## Report

`claude-codex-report/v1` envelope, genre review; `verdict` = `{counts, findings}` ONLY (JSON block under 8 KB). Markdown body: A1–A3 with pasted counterfactual tails (never a pin you did not execute), B1 clause table + executed ordering probe, B2 table + executed hops, B3 tables + cold read, B4, C, D, residual risk, "what this pass did NOT check". Do not end the turn mid-flight.
