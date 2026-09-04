WRITE_SCOPE: []
ORIGIN: claude-magistrate  HOP: 1  GENRE: review  READ-ONLY (workspace-write with an empty write scope: write NOTHING under the checkout; use only $TMPDIR)

# Delta re-audit of decode-identity FIX ROUND 2 (`7cfd0b59..629a333e`) — execution lens + pedagogy as its own dimension

Checkout: `/Users/edr/code/JouleWise-wt-decode-id3`, detached at `629a333e`. Under review: `git diff 7cfd0b59 629a333e` = Sol 262's landing `bd2cae3e` (its report is custodied at `docs/process_traces/2026-09-02-decode-identity-set/24-sol-262-fix-round-2-report.md`) + the magistrate's bench corrections `9c1dc717` (contract gloss + rewrap, R2-D docstring) + docs-only custody `629a333e`. The brief the seat executed is file 23 in that directory; the cold-gate synthesis that ruled the round's shape is file 22. You originated F-B (file 17); this round is fix round 2 on F-B under rule 11 — if the F-B test does not bite, say so plainly: that is the standing escalation signature and the next spend is a consult, not round 3. Do not lower a severity to avoid that.

Run every test with `TMPDIR` under your scratch dir. Do NOT run `python3 -m unittest discover`. Mutations are made on in-memory copies or by re-`exec` of function source — write nothing under the checkout.

## A. Execution lens — does each cure kill its named counterfactual, and only for the right reason?

A1. R2-A `tests/test_analysis_inputs.py::FrozenConsumerIdentitySetTests::test_self_consistent_forged_pack_requires_launch_tree_digest_binding`. (i) Read the fixture against the custodied forgery script `20a-coldF-forgery_probe.py.txt`: does it forge `A/decode` to declare a DRIFTED identity, re-render the projection receipt + sidecar, the U8 freeze receipt + sidecar, both plan-tree bindings, COMMIT the pack, and keep the lineage's HONEST `pack_sha256`? Is the drift applied exactly once (the seat trap: `_generated_exact_case` re-reads the forged inventory)? (ii) Counterfactual: replace `inputs.py:3898` (`if committed_pack_tree_sha256(pack_root) != next(iter(pack_hashes)):`) by `if False:` in memory and paste the failure tail. (iii) The CONTROL assertion (same forged pack, lineage RE-STAMPED to the forged committed tree digest → accepted): verify it is present and that it would FAIL if the gate refused for any reason other than the tree comparison — e.g. mutate the control's re-stamped digest to a wrong 64-hex and show the control assertion trips. (iv) Does the test assert on the PRODUCTION seam (`_production_floor_resolution` / `_resolve_contrast_floor` with `request_factory=None`) for the exact-cell case, and `floor_request_for_evidence(...) is None` for the transport case? (v) Own mutants: at least two more (e.g. compare against the wrong lineage field; skip `resolve(strict=True)`).

A2. R2-B `…::test_generated_multi_identity_transport_uses_real_frozen_gate_and_skips_exact_cell`: confirm no `patch` of `_frozen_consumer_identity_set`; counterfactual = gate body replaced by `return frozenset()` (paste); confirm the assertions match the mocked sibling at ~`:799` (transport route taken, exact-cell route skipped) and name any assertion the mocked test makes that this one does not.

A3. R2-C `tests/test_analysis_integration.py::…::test_identity_gate_refusals_map_to_transport_inapplicable`: mutant mapping either label to `floor_row_missing` must fail (paste). Is the pinned mapping the one R-M3 (file 15) ruled? Quote R-M3.

A4. R2-D `tests/test_identity_pins.py::…::test_distinct_manifest_bindings_produce_distinct_scientific_identities` + the rewritten docstring on `test_declared_manifest_identity_cardinality_refuses_synthetic_mismatch`. Is the dominance argument SOUND against the code at `identity_pins.py:1676–1710` and `scientific_config_identity` (:218–237)? Specifically: is there ANY path to the call at :1701 on which `len(scientific_hashes) != len(declared_by_manifest)` — e.g. `suite_declaration is None` (the `if` at :1676): does the guard's call sit inside or outside that branch, and if outside, what does the census look like without a suite declaration? If you find a reachable path, that is a BLOCKER-class finding (`F-G: REACHABLE`) — the ruling in file 22 §Q3 was made from a bench read and a reachable path overturns it. Do NOT propose weakening any preceding check.

A5. Round-1/1b tests still bite: re-run the four round-1b label tests and the F-D tampered-pack test with their original counterfactuals (files 16 and 18 name them) — one line each, KILLED/SURVIVES.

## B. Pedagogy dimension (Ed's writing standard: a reader replicates the mechanism from the text; every term built or glossed at first use or deleted)

B1. The rewritten paragraph at `docs/contracts/identity_pin_projection.md` ~602–640 (dictated by the magistrate, verified by the seat, glossed at the bench). Grade EACH numbered step (1)–(8) against `inputs.py:3870–4048`: PROVEN / OVERCLAIMED / UNDERCLAIMED, with the proving line. Check the magistrate's bench gloss in step (2) against `joulewise/arm_readiness.py::committed_pack_tree_sha256` (:2750–2874): is it true that the function itself fails on an untracked, missing, or modified file (and therefore that the gate refuses)? Is "each path, Git mode, byte length and content digest in path order" the framing the code folds? Is "the same digest the launch lineage recorded at arm time" accurate — where is `pack_sha256` stamped into the lineage (Opus P5 chain: `bundle.py:87–147` → `authenticate_campaign_launch_lineage`; caller-supplied lineage rejected at `:1056–1062`)? Verify that chain ONCE and report it — this was owed by file 22.

B2. First-use table: the seat reported four `FIRST-USE-GAP` rows (file 24): "committed file tree" (now glossed at the bench — grade the gloss), "plan tree" (first use line 34 as the filename `plan_tree.json`, defined §3 ~178), "`projection_receipt` binding" (key list at 181 before definition at 192), "consumer binding" (`consumer_bindings` key at 200 before its rows are defined at 203). The magistrate's proposed ruling: a key name inside an exhaustive key list, or a filename, is a VALUE the reader copies (the same reasoning file 22 §Q2 applied to `U11` inside `D117-U11-IDPIN-PROJECTION`), and a definition that follows within the same section is not a gap. Refute or confirm, row by row. Then build your OWN first-use table for the two new paragraphs — do not copy the seat's — and report any term the seat's table missed.

B3. Read the two paragraphs cold, as a reader who has the contract but no code: can you state, from the text alone, which label a forged-but-self-consistent pack produces and WHY? If any sentence needs "the sequence above" or knowledge of the code, name it.

## C. Same-signature statement (mandatory)

Did this round produce a defect of the SAME CLASS as round 1 or 1b — a closure without a biting test (F-B class), or a first-use defect in the contract prose (F-N/F2 class)? Answer YES/NO per class with the evidence. A YES on either is the standing escalation signature; say so.

## D. Suite tails

`python3 -m unittest tests.test_detection_floor tests.test_analysis_inputs tests.test_analysis_claims tests.test_identity_pins tests.test_analysis_integration tests.test_d165_dominance_closeout tests.test_docs_freshness` (expected 446 OK skipped=1) and the D-165 digest test (expected `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`). Paste exact tails.

## Report

`claude-codex-report/v1` envelope, genre review; `verdict` = `{counts, findings}` ONLY (ids, severity, title — JSON block under 8 KB). Markdown body: A1–A5 with pasted counterfactual tails (never a pin you did not execute), B1 step table, B2 row-by-row ruling + your own first-use table, B3 cold read, C statement, D tails, residual risk, "what this pass did NOT check". Do not end the turn mid-flight.
