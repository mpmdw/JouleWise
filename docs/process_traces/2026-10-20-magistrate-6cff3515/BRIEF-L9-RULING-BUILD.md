# Sol build brief: L9 ruling build (cloud seat, activation 6cff3515, 2026-10-20)

You are a Codex Cloud seat (gpt-6.1-sol, xhigh). Repository: JouleWise, public clone.
Seat setup: clone mpmdw/JouleWise-data and run `bash tools/cloud/seat_setup.sh /tmp/jw && source /tmp/jw-seat.env`.
Base: `git fetch origin lane/2026-10-20-l9-silly-numbers && git checkout -b lane/2026-10-20-l9-ruling-build 090a398bb`
(verify `git rev-parse HEAD` starts with 090a398bb; stop if missing). Push ONLY to `lane/2026-10-20-l9-ruling-build`.
Commit and push after each question. Never push to main, `integration/*` or any other lane.

Safety: `JW_B5_SYNTHETIC_ONLY=1` on every test run (it is in `/tmp/jw-seat.env`); a fresh TMPDIR per module. Never read a
real archive or key directory. Run only the modules in WRITE_SCOPE plus the dependent modules named below, not the whole
suite (CI runs it from a draft PR). If pytest is absent use `python3.13 -m unittest <module>`.

## Governing texts, in authority order (earlier wins)

1. `docs/process_traces/2026-10-20-magistrate-6cff3515/L9-RULING-ADDENDUM.md` on origin/main (read it in full).
2. `docs/process_traces/2026-10-20-magistrate-4b350f47/L9-RULING.md` on origin/main (read it in full).
3. This brief.
4. The code at the base commit. Where a line number or name in 1-3 is off, the code is the fact; follow the intent and
   record it under "decisions I made".
Supporting evidence (read for the probes, do not treat as rulings): JouleWise-data branches
`claude/l9-ruling-cold-fable` (`reports/l9-ruling-cold/fable.md`), `claude/l9-ruling-cold-opus-p52emy`
(`reports/l9-ruling-cold/opus.md`, `opus-probes/*.py`), `claude/l9-silly-review-wcjrz5` (`reports/l9-silly-review/`),
`claude/l9-council-opus-tzdg1f`, `codex/l9-council-sol`.

## Order of work

Q-LINEAGE, then Q-EXACTSTACK (one shared predicate, three sites), then Q-CONSUMERID (addendum §I step 1 test first; its
result decides flag or refusal), then Q-RENDERER, then common §C (limitations to the fill), then addendum §Z (silly-number
follow-ups), then delete the four `CONDITIONAL_SEAMS` in `tests/b5_analysis/fixtures_s10.py` and update
`tests/fixtures/b5_analysis/s10/PROVENANCE.md` 159-162.

## Number rule (state it, apply it)

Every tolerance on a measured or derived quantity carries its derivation in a comment: between 1e6 times float noise and
1% of the smallest printed half-width; with no half-width, 1e-6 absolute in the column's unit. Exact equality only for
integers, hashes, identity/digest comparisons and identical code on identical inputs. You never choose a bar the texts
do not give; the addendum §Z sets the zero-point bar.

## WRITE_SCOPE (exhaustive; ask for any other file by name in your report instead of editing it)

Code:
- joulewise/detection_floor.py
- joulewise/floor_extraction.py
- joulewise/dominance_closeout.py
- joulewise/analysis_manifest_v3.py
- joulewise/analysis_engine/__init__.py
- joulewise/analysis_engine/inputs.py
- joulewise/analysis_engine/artifact.py
- joulewise/results_fill_adapter.py
- joulewise/b5_analysis/dry_run.py
- scripts/mint_floor_artifact_generalized.py
- scripts/build_results_fill_input.py
- scripts/floor_mint_pinsets/schema_v2.json
- configs/flags/number_rows.json (only if `tests/flags/test_number_coverage.py` fails; update the `checks` text of the
  exact_stack_only and `_contrast_floor_binding_error` rows)
- configs/gates/hazard_refusals.json (only for entries `python3.13 -m tests.hazards.refusal_census` prints)
Docs:
- docs/specs/c027/p2-039_floor_artifact.md
- docs/contracts/identity_pin_projection.md
- docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md (append addendum §S's quoted text verbatim, nothing else)
- tests/fixtures/b5_analysis/s10/PROVENANCE.md
Tests:
- tests/test_detection_floor.py, tests/test_floor_extraction.py, tests/test_dominance_closeout.py,
  tests/test_d165_dominance_closeout.py
- tests/test_mint_floor_artifact_generalized.py, tests/b5_analysis/test_mint_kept_units.py
- tests/test_analysis_inputs.py, tests/test_analysis_claims.py, tests/test_analysis_finalizer.py,
  tests/test_analysis_manifest_v3*.py (existing files only)
- tests/test_results_fill_adapter.py, tests/b5_analysis/test_fill_adapter.py
- tests/b5_analysis/test_dry_run.py, tests/b5_analysis/test_release_equality.py, tests/b5_analysis/joined_s10.py,
  tests/b5_analysis/test_s10_chain_defects.py, tests/b5_analysis/fixtures_s10.py
- tests/b5_analysis/test_launch_lineage.py, tests/b5_analysis/test_chain_fixture.py,
  tests/b5_analysis/test_finalization_block5.py, tests/b5_analysis/test_runtime_identity_cells.py,
  tests/b5_analysis/test_claim_gate_kept_quads.py, tests/b5_analysis/test_reported_cell.py
- tests/test_r4_acceptance_oracle.py, tests/test_floor_mint_pinsets_schema.py, tests/test_neg8_survivors.py,
  tests/test_run_d165_closeout_from_custody.py (N5 comments only)
Report: `.codex-report/l9-ruling-build.md`.

Not in scope: `docs/decision_log.md` (the lead records decisions), `scripts/render_results_fills.py`, any path in
`joulewise/b6/registration.py` `NUMBER_BEARING_PATHS` (stop and report NEEDS_RULING if one seems needed).

## Checks you run

- Every WRITE_SCOPE test module before (record failures already on the base) and after. Known on the base:
  `tests/test_run_d165_closeout_from_custody.py` has 29 environmental errors in the cloud (`/Users/edr/...` custody
  locators); `tests/test_r4_acceptance_oracle.py` has 10 subtest failures that §Z fixes.
- Any other module importing a function you changed (grep); run it, do not edit it, report failures.
- Registries: `tests/hazards/test_refusal_allowlist.py`, `tests/hazards/test_import_graph.py`, `tests/test_schemas.py`,
  `tests/test_digest_pin_census.py`, `tests/flags/test_number_coverage.py`, and `python3.13 -m tests.hazards.refusal_census`.
- End to end on production-shaped synthetic data through the real stage chain: the joined S10 synthetic chain
  (`tests/b5_analysis/joined_s10.py`, `test_s10_chain_defects.py`, `test_dry_run.py`) with no conditional seam left,
  showing (a) a GAMMA-shaped arm resolves its floor through the group's single source cell, (b) a two-window aggregate
  mints with a producer-lineage inventory, (c) every new limitation string appears in the fill input, (d) step 11 ends at
  the validated fill input with the FLAGS string.
- Replay every refusal the ruling keeps (other stack, group not admitting the family, two sources, split producer,
  mixed provenance within a producer, undeclared identity, multi-identity unauthenticated arm) and every refusal it turns
  into a limitation, each on production-shaped synthetic data, and list the outcomes.

## Report (`.codex-report/l9-ruling-build.md`, committed and pushed, and as your final message)

First line: your model id. Branch head sha; per question: done / not done, diff summary with file:line; the §I step-1
result per variant; the refusal replay table; tests before and after (counts and failing names); "decisions I made";
"left for a later round"; NEEDS_RULING only for a choice that changes which data count or a printed number. Decide
everything the governing texts determine.
