gpt-6.1-sol

Branch: `lane/2026-10-20-l9-ruling-build`; verified base `090a398bb55916850ad052c1127433a4f0f7b1c4`.
Work in progress; final assessed head and complete check/replay tables follow after all questions.

Authority: origin/main's L9-RULING-ADDENDUM.md (activation 6cff3515), then L9-RULING.md (4b350f47), both read in full. Read both council reports, both cold reports and the silly-number executing review; inspected the cold exact-stack and consumer probes. No real archive or key directory opened. All checks use Python 3.13 unittest (pytest absent), `JW_B5_SYNTHETIC_ONLY=1`, and fresh per-module TMPDIRs.

Number rule: every measured/derived tolerance carries its derivation between 1e6 times float noise and 1% of the smallest printed half-width; without a half-width use 1e-6 absolute in the column unit. Equality is reserved for integer/hash/identity/digest comparisons and identical code on identical inputs. §Z supplies the zero-point bar.

Q-LINEAGE: DONE. Aggregate producer inventory, ordered schema validation, per-producer reconstruction and digest checking, scoped absent/unauthenticated limitations, and verdict revalidation. Single-lineage provenance remains the original shape; per-producer split/mixed provenance still refuses. Focused detection-floor, claim-artifact, input and S10 defect tests pass; the full mint checks are in progress.
Q-EXACTSTACK, Q-CONSUMERID, Q-RENDERER, §C, §Z and seam deletion: NOT DONE yet, in the required order.

§I step 1: not run yet; no consumer-identity policy decision has been taken.

Decisions I made:
- Baseline runs use an immutable detached worktree at the exact base. This keeps baseline evidence separate from implementation.
- `/tmp` has a small independent capacity. Concurrent fixture restores exhausted it; those capacity-error runs are retained in scratch logs and repeated using fresh module directories under `/workspace/l9-tmp`. This does not change test code or evidence.
- Floor lineage limitations are compared by exact equality of the complete floor-lineage subsequence of `inputs.limitations`; other questions append their own scoped limitations to the same existing list.
- The synthetic mint helper updates its aggregate producer-set digest after re-pinning its generated component digests, eliminating a pre-existing helper-only stale binding in the new assertions.

Left for a later round: none decided yet. No NEEDS_RULING at this checkpoint.

Q-EXACTSTACK: DONE. `detection_floor.exact_stack_serving_cell` selects the unique claim-usable source using family admission, backend/metric/window class, stack digest, and authenticated family phase/token lengths. Finalizer, close-out, request construction and exact resolution use it. Group-served requests use empty stress, retain the actual source id, and check the singleton gate by operand identity. Verdicts carry the scoped no-envelope limitation. The 31-test S10 defect module (including nine refusal variants), 131 detection-floor tests, 20 input tests, 65 claim tests, 19 manifest tests, 59 close-out tests and 18 finalizer tests pass. Number coverage passes (6 tests, 1 skip), so `number_rows.json` is unchanged.

Q-LINEAGE full mint verification completed: generalized mint 84 tests (2 skips), kept-unit mint 85 tests (2 skips), all pass. The Git CLI has no working push credential; after checking explicit per-file/branch authorization, the connected GitHub API published the identical Git tree as commit `a8f3d5566c7e171293a4fd930b092bda94e2e21d`. Automatic review initially rejected one blob for purported incomplete authorization; the same upload succeeded after the scope and public-source checks. No approval remains blocked.


## Round 2 continuation (activation af419b16)

Verified continuation base/head: `00ccb8c7caf9474d17fb83e6e029c9cfe180c3bd` on the sole authorized branch `lane/2026-10-20-l9-ruling-build`. Both rulings re-read in full from origin/main (`bcd70a273`); existing Q-LINEAGE and Q-EXACTSTACK sections above are preserved. Supporting cold reports, council reports and consumer probes read. No real archive or key directory read.

Q-CONSUMERID: DONE. §I.1 pinning test was written and passed before the policy change. Each of `suite_manifest_sha256`, `output_tokens`, `measurement-arm`, `df-condition`, `decode-prompt` is excluded by the real `_read_bundle` as `config_hash_mismatch`; unchanged control is included. The test isolates unrelated hardware/provenance checks so they cannot mask the config guard. All five variants differ in both typed config and exact expected bundle bytes; no mutant supplies floor-request evidence. This selects the limitation branch under §I.2.

The hazard route reads the committed unprojected pack's unique identity unit and authenticates each inventory file. A distinct hazard failure carries `consumer_identity_set_unauthenticated:<family>`; multi-identity unauthenticated arms refuse `consumer_identity_undeclared` before transport. Only hardware_target.notes, run_metadata.project and run_metadata.operator are recording differences; tags and every other typed field bind. The ARM frozen/U8 path is unchanged. Limitations pass through contrast preparation into the existing verdict list.

Diff pointers: `joulewise/analysis_engine/inputs.py:4411` (hazard declaration and closed allowlist), `joulewise/analysis_engine/inputs.py:4678` (request policy), `joulewise/analysis_engine/__init__.py:375` and `:1881` (limitation carrier), `tests/test_analysis_inputs.py:1229` (step-1 and hazard regressions), `tests/b5_analysis/test_chain_fixture.py:542` (production declaration assertion), `docs/contracts/identity_pin_projection.md:646` (hazard contract).

Focused Q-CONSUMERID checks: inputs 27 tests (1 skip), claims 65, S10 defects 31, all pass. Imports/dependent checks are running; their final results will be added. Earlier probe runs exposed fixture-only errors (wrong prefill unit name and request window class); corrected and re-run green.

Done: Q-LINEAGE (inherited), Q-EXACTSTACK (inherited), Q-CONSUMERID. Not done: Q-RENDERER, common §C, §Z, conditional seam deletion, PROVENANCE, opted-in joined end-to-end and complete refusal replay tables, final after/registry checks. No NEEDS_RULING at this checkpoint.

Before table (verified continuation base; each completed focused module re-run once). Completed runs began in the unchanged checkout; remaining runs use detached worktree `/workspace/l9-before` at the identical base to prevent contamination. An unfinished launcher was moved to that immutable worktree; only incomplete modules were restarted. Every test run has JW_B5_SYNTHETIC_ONLY=1 and a fresh per-module TMPDIR under `/workspace/l9-tmp`.

| Module | Before |
|---|---|
| `tests.b5_analysis.test_chain_fixture` | Ran 0 tests in 0.000s; OK (skipped=1) |
| `tests.b5_analysis.test_claim_gate_kept_quads` | Ran 31 tests in 1.447s; FAILED (errors=11) |
| `tests.b5_analysis.test_dry_run` | Ran 55 tests in 189.763s; OK (skipped=3) |
| `tests.b5_analysis.test_fill_adapter` | Ran 11 tests in 0.496s; OK |
| `tests.b5_analysis.test_finalization_block5` | Ran 75 tests in 72.854s; OK |
| `tests.b5_analysis.test_launch_lineage` | Ran 4 tests in 49.272s; OK |
| `tests.b5_analysis.test_mint_kept_units` | Ran 85 tests in 65.238s; OK (skipped=2) |
| `tests.b5_analysis.test_release_equality` | Ran 10 tests in 1.278s; OK (skipped=1) |
| `tests.b5_analysis.test_reported_cell` | Ran 16 tests in 0.070s; OK |
| `tests.b5_analysis.test_runtime_identity_cells` | Ran 12 tests in 2.801s; OK |
| `tests.b5_analysis.test_s10_chain_defects` | Ran 31 tests in 2.613s; OK |
| `tests.test_analysis_claims` | Ran 65 tests in 3.122s; OK |
| `tests.test_analysis_finalizer` | Ran 18 tests in 35.694s; OK |
| `tests.test_analysis_inputs` | Ran 20 tests in 16.363s; OK (skipped=1) |
| `tests.test_analysis_manifest_v3` | Ran 19 tests in 0.588s; OK |
| `tests.test_d165_dominance_closeout` | Ran 59 tests in 16.395s; OK |
| `tests.test_detection_floor` | Ran 131 tests in 4.801s; OK |
| `tests.test_dominance_closeout` | Ran 3 tests in 2.211s; OK |
| `tests.test_floor_extraction` | Ran 145 tests in 15.819s; OK (skipped=2) |
| `tests.test_floor_mint_pinsets_schema` | Ran 1 test in 0.001s; OK |
| `tests.test_mint_floor_artifact_generalized` | Ran 84 tests in 97.866s; OK (skipped=2) |
| `tests.test_r4_acceptance_oracle` | Ran 9 tests in 3.040s; FAILED (failures=10) |
| `tests.test_results_fill_adapter` | Ran 4 tests in 0.153s; OK |

Newly observed base failure: `tests.b5_analysis.test_claim_gate_kept_quads` has 11 errors, all inherited from Q-EXACTSTACK's limitation emission looking up stub-only source id `floor-a`. This is separate from the known §Z oracle failures and custody environment failures. Will repair the authorized synthetic fixture shape while preserving production source-cell validation. Other baseline modules still running are recorded in the final table.

Decisions I made in round 2:
- Use `_read_bundle`'s byte and typed-config pinning as the flag justification; do not claim scientific identity equality at the group-served source cell.
- Keep the recording allowlist hazard-specific. Compare every typed field and every tag outside its three named fields; preserve run_id's existing omission from scientific identity because it identifies physical repeats.
- Use the existing optional limitation list through request construction and contrast preparation; do not add a verdict schema, catalog or public record field.
- Seat setup's /opt/homebrew Python symlink was denied by filesystem ownership, although Python 3.13.5 and zsh 5.9 are available. This is an environment observation; no repository file was changed to hide it.

Q-CONSUMERID checkpoint pushed successfully by Git CLI as `994478b28` (no API fallback needed in this seat). The report's old statement about the prior seat's credential remains historical.

Q-RENDERER: DONE. `joulewise/b5_analysis/dry_run.py:203` registers `results_rendering_not_run_no_block5_template`; `:1034` ends step 11 after the fill builder, with no render invocation or rendered_fills role. `tests/b5_analysis/test_dry_run.py:636` (T20) checks fill input, the flag, no capture and no Markdown; its argv census expects 17 calls. `tests/b5_analysis/test_release_equality.py:113` (R3) now perturbs results-fill-input.json. `tests/b5_analysis/test_s10_chain_defects.py:537` checks the production stop and no renderer call. Only addendum §S's quoted text is appended to `docs/process_traces/2026-10-07-block5-seal/SEAL_RECORD.md`. Renderer script untouched.

Renderer focused checks: QRendererProductionTests 2 OK; T20 1 OK; release equality 10 OK (1 skip). Complete dry-run module is still running at this checkpoint and will appear in the final after table. The first mocked-state renderer test lacked its disclosure output registry; corrected and the focused test passed.

Done: inherited Q-LINEAGE and Q-EXACTSTACK; Q-CONSUMERID; Q-RENDERER. Not done: common §C, §Z, seam deletion/PROVENANCE, opted-in end-to-end, complete refusal replay/final after and registry checks. No NEEDS_RULING.

Dependent baseline observation: test_analysis_integration has 17 errors and test_sensitivity has 1 error from the same inherited source-id lookup on mathematical stubs (the tests are outside the edit scope). The appropriate authorized correction is to derive the source-cell limitation at actual resolution, alongside the new consumer limitations, instead of rediscovering source cells after a stubbed resolver. No out-of-scope test will be edited.

Q-RENDERER pushed by Git CLI as `b83eed5dc`.

Common §C: DONE. `joulewise/results_fill_adapter.py:49` copies the exact verdict limitation list to gamma and each contrast's scoped subsequence to the contrast; `floor_source_cell_ids` copies the issued real source ids. `validate_results_fill_projection` compares ordered lists and exact text/source strings through results_fill_contrast_census_mismatch and results_fill_floor_mismatch. `scripts/build_results_fill_input.py:85` runs that comparison at the builder boundary too. The floor projection itself is also compared unchanged. Tests in `tests/test_results_fill_adapter.py:180` exercise dropped, changed, reordered and unrelated-family limitations and changed source cells. No rounding or arithmetic is added.

`joulewise/analysis_engine/__init__.py:490` now derives floor-pack notes at the actual resolution site and merges them via the same per-contrast limitation carrier. This fixes the 11 inherited kept-quad errors without weakening floor validation or editing mathematical stub fixtures. Authorized checks: results adapter 6 OK, block-5 fill adapter 11 OK, kept quads 31 OK, claims 65 OK, inputs 27 OK (1 skip). Out-of-scope integration/sensitivity dependency reruns are pending.

Done: Q-LINEAGE, Q-EXACTSTACK, Q-CONSUMERID, Q-RENDERER, common §C. Not done: §Z, seam deletion/PROVENANCE, opted-in joined end-to-end, final refusal-replay/after/registry tables. No NEEDS_RULING.

Common §C pushed by Git CLI as `4da5e65a2`. Its out-of-scope dependency reruns are green: tests.test_analysis_integration 116 OK and tests.b5_analysis.test_sensitivity 36 OK. Q-RENDERER full tests.b5_analysis.test_dry_run: 55 OK (3 skips).

Addendum §Z: DONE. `joulewise/detection_floor.py:1218` uses rel_tol=0.0 and abs_tol=max(1e-6,1e6*2**-53*S), with the complete ruled derivation. The same shared predicate remains at all three production call sites. `scripts/floor_mint_pinsets/schema_v2.json:35` loses only the retired literal exclusion after schema-structure checks. `tests/test_r4_acceptance_oracle.py:213` puts all ten refused boundary cases just past the current bar and separately refuses a 1e-3 J divergence at production scales; admitted randomized/mismatch-grid samples now use the new bar while exact Fraction enclosure checks stay independent. `tests/test_detection_floor.py:916` tests the new scale band and its old adversarial generator now samples that band too. N5 derivation comments are beside all 18 actual places=9 mint-kept assertions, the reported t comparison, both p-value comparisons, five custody-driver comparisons (comments only), and three NEG8 absolute comparisons.

§Z focused outcomes: detection floor 131 OK; floor extraction 145 OK (2 skips); dominance 3 OK; D165 dominance 59 OK; oracle 10 OK (the base's 10 failed subtests are fixed); schema 2 OK; mint kept units 85 OK (2 skips); reported cell 16 OK; kept quads 31 OK. NEG8/custody reruns are still finishing; the final table will record them. One oracle boundary generator run was interrupted after cancellation landed exactly at zero and nextafter walked subnormals; stepping the tolerance radius first fixes it, with a bounded guard. Final oracle is green.

N2/N3/N4: no production change. S remains the validated member-envelope upper bound; earlier validation/refusal order remains; allowance mismatch is re-derived and recorded at mint as ruled.

Done: Q-LINEAGE, Q-EXACTSTACK, Q-CONSUMERID, Q-RENDERER, common §C, §Z. Not done: seam deletion/PROVENANCE, opted-in joined end-to-end, complete refusal-replay/final after and registry tables. No NEEDS_RULING.

§Z pushed by Git CLI as `5ca9202c9`.

Conditional seam deletion and PROVENANCE: DONE. `tests/b5_analysis/fixtures_s10.py:52` now goes directly from the disclosed hardware/Git seams to commit_checkout; all four conditional patches and CONDITIONAL_SEAMS are deleted. `tests/b5_analysis/joined_s10.py:28` and its Git context no longer import/install them. The four former conditional rows in `tests/fixtures/b5_analysis/s10/PROVENANCE.md` are replaced by a production-ruling account. `tests/b5_analysis/test_dry_run.py:67` adds joined assertions for the two-producer inventory, real single-source GAMMA floors, scoped limitations in fill, and the validated-fill/FLAGS endpoint. Focused seam-free checks: S10 defects 31 OK and release equality 10 OK (1 skip); inputs rerun is finishing.

Done: all implementation questions, common §C, §Z, seam deletion and PROVENANCE. Not done: opted-in end-to-end joined run, complete refusal-replay/final after and registry tables. No NEEDS_RULING. The next command opts in to the real-stage chain over the committed synthetic archives; it does not collect hardware data or read real archives.
