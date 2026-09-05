# PAPER-CUSTODY-SEAM-01 — Sol fix round 1

Date: 2026-09-04. Base and ending commit: `0ce790f7c92214f37222e5deb3f94a753cb80d61` on `feat/2026-09-04-paper-custody-seam`. The worktree began clean. No commit was made. This delegated round modified only allowlisted paths.

Status: **PARTIAL — authorized cures implemented and focused tests green; three mandatory changes need write-scope expansion.** No production or quiet-machine evidence was run.

## Finding → cure → evidence

| Refuter finding | Cure in this round | File:line |
|---|---|---|
| Execution F1; contract F1–F2 — caller-selected repository, paths, digests, inventory, and receipt | Replaced all five public refs with exactly `role` + `runs_root`; made bindings/receipts private; added the tracked-map candidate with role/family/validator/path/digest rows; role resolution calls the consumed `_mint_git_anchor`, reads `<head>:configs/paper_supply/supply_map.json` through the active V2 session, and never accepts an anchor or locator from the caller. | `configs/paper_supply/supply_map.json:1`; `joulewise/paper_custody.py:92-119,596-680,1064-1088`; `tests/test_authentication_io.py:416-465`; `tests/test_paper_custody.py:435-456` |
| Execution F2; contract F3 — both lower bypasses | Removed `raw_bytes` from the campaign-log loader and added the signature guard. The floor-loader cure is blocked because its actual path and test are absent from `WRITE_SCOPE`. | `joulewise/campaign_provenance.py:453-468`; `tests/test_authentication_io.py:467-473`; blocked: `joulewise/analysis_engine/inputs.py:945-955` |
| Execution F3 — incomplete validator-source digest | Added a closed per-family census containing `_replay_family`, both dispatch layers, and every current owning validator; the digest hashes every member id and source. The test mutation-probes every census member. | `joulewise/paper_custody.py:367-451`; `tests/test_paper_custody.py:410-434` |
| Execution F4 — empty public `Verified*` construction | All five constructors now refuse; the private factory remains the only creation path. | `joulewise/paper_custody.py:151-192,1022-1030`; `tests/test_paper_custody.py:395-409` |
| Execution F5; contract F4 — duplicated D-165 ownership and one-way map check | Moved the paper adapter, adapter codes, closed refusal enumeration, and OR-01 sentence map into the real producer module. Added exact equality plus mutation probes on additions to either side. Deleting the old shim and writing the actual Markdown registry row remain scope-blocked. | `joulewise/dominance_closeout.py:175-328`; `tests/test_d165_dominance_closeout.py:2070-2095`; blocked: `joulewise/d165_dominance_closeout.py`, `docs/paper/results-fill-registry.md` |
| Contract F5 — D-173 deletion | Base `0ce790f7` already contains both the D-173 table row and full decision. They were preserved; the decision log was outside scope and untouched. | `docs/decision_log.md:219,10903-10923` |
| Contract F6 — raw exceptions | Validates digest type before regex use; the single public boundary preserves existing custody refusals and converts every other `Exception`, including active-session `RuntimeError`, to a closed refusal. | `joulewise/paper_custody.py:454-480,1053-1061`; `tests/test_paper_custody.py:457-470` |
| Contract F7 — non-rebuildable normative text | Rewrote the contract with first-use definitions/links for D-173, D-123, D-165, D-117, G2-a, TR-01, supply map, role, anchor, receipt, and family; fixed the exact map location/schema, lookup, clean-tree anchor, receipt wire, validator digest, replay, and reopen algorithms. | `docs/contracts/paper_supply_custody.md:3-259` |

## Red → green record

- RED `python3 -m unittest tests.test_paper_custody`: `Ran 8 tests`; `FAILED (failures=5, errors=6)` — missing census and five forgeable constructors; nested session also escaped.
- RED `python3 -m unittest tests.test_authentication_io`: `Ran 21 tests`; `FAILED (failures=2)` — caller-authored ref graph and `raw_bytes` channel.
- RED `python3 -m unittest tests.test_d165_dominance_closeout`: `Ran 50 tests`; `FAILED (errors=1)` — real-module enumeration absent.
- GREEN `python3 -m unittest tests.test_paper_custody`: `Ran 10 tests in 16.086s`; `OK`.
- GREEN `python3 -m unittest tests.test_authentication_io`: `Ran 21 tests in 0.753s`; `OK`.
- GREEN `python3 -m unittest tests.test_d165_dominance_closeout`: `Ran 50 tests in 10.027s`; `OK`.
- GREEN `python3 -m unittest tests.test_run_campaign`: `Ran 270 tests in 199.259s`; `OK`.
- GREEN `python3 -m json.tool configs/paper_supply/supply_map.json` and `python3 -m py_compile ...`: `SUPPLY_MAP_JSON_OK`; `PY_COMPILE_OK`.

The repository-wide suite was not run because the prompt expressly forbids it.

## Required scope expansion

1. `joulewise/analysis_engine/inputs.py` and `tests/test_analysis_inputs.py`: change `load_floor_artifact` to return `AuthenticatedFloorArtifact` without a mapping/digest downgrade and add its producer regression.
2. `joulewise/d165_dominance_closeout.py`: delete the superseded duplicate shim.
3. `docs/paper/results-fill-registry.md`: install the OR-01 reason sentences so the existing bidirectional test can parse and cross-check the actual registry rather than only the real-module map.

Smallest resume: grant exactly those four paths, apply the three changes, rerun `tests.test_analysis_inputs`, `tests.test_d165_dominance_closeout`, `tests.test_paper_custody`, and `tests.test_authentication_io` one module at a time, then update this report.
