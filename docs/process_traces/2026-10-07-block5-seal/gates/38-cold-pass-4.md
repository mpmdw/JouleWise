# Fable 5.1 cold delta pass (pass 4): int5 43ac12d0c..fe28e5a0c (census ancestors, NEG-8 delta fixes, sealed reference pin, T3 prune)

Reviewer: Fable 5.1, single foreground session, read-only in every repository. Worktree
`/Users/edr/code/JouleWise-wt-int5`, branch `integrate/2026-10-07-int5`, HEAD confirmed
`fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7` (`git rev-parse HEAD`; working tree clean). Diff reviewed:
`git diff 43ac12d0c fe28e5a0c -- joulewise scripts configs` (19 files, +1035/-137) plus the test diff (18 files,
+896/-72). Rule applied: `REVIEW_BRIEF_RULE.md` in both directions. Context: my pass-3 report
(`cold-pass-3/REPORT.md`, PASS WITH NOTES, notes N-A..N-C), the Sol delta audit (`delta-audit-sol/REPORT.md`, A1-A5),
dry-records F1, the NEG-8 ruling (`neg8-council/RULING.md`), `FROZEN_HEAD_4.md`, and the block-5 analysis plan at
`JouleWise-wt-ia-claim/configs/campaigns/v5_claim_25g83/analysis_plan_block5.md` (read-only, for item 1's consumer
question).

Interpreter `/opt/homebrew/bin/python3.13 -B` (non-venv), `TMPDIR=/private/tmp/coldpass4`, every run foreground.
Probes written to my scratchpad only, never into a repository.

## Overall verdict: PASS WITH NOTES

Every one of A1-A5 and F1 is fixed in the direction the audit asked, no fix adds a non-physics refusal or a path to a
wrong number, the sealed `neg8_reference` pin derives from the committed configs and the real rehearsal bundles and
equals the committed panel pins, the census now sees an agent ancestor and still never matches the window's own
processes, and the pinned estimators are byte-identical to a434e363d. One defect (D1) is a plumbing gap on the
claim-time floor path: the A1 consumer is reachable from `analyze-claims` but not from floor extraction, so on a
HAZARD runs root every block-5 floor cell refuses `whole_window_drift_allowance_unrecorded` until the archive can be
passed. It cannot produce a wrong number (the consumer refuses rather than reading the stored bracket), it touches no
collection or harvest code, and the analysis plan assigns analysis code to lane L9 (section 11, written blind), so it
does not block arming or the seal of the measurement code; it must land before section 4 step 4 runs. The notes are
dispositions for the orchestrator and the seal, not fix rounds.

## Per-item table

| # | Item | Verdict | Where (fe28e5a0c) | Evidence |
|---|---|---|---|---|
| 1 | A1: the harvest records which bracket carries the allowance | SOUND | `harvest.py:4562-4669` (`neg8_screen` returns `stored_verdict` / `survivor_rescreen` / `screen_failed`), `4671-4706` (`neg8_allowance` writes `derived/neg8-allowance.json`), `4961-4996` (`neg8_rescreen_binding`: survivor bracket digest from `write_json_once`, `bound_used`, clean bound), `5086-5090` (clean bound digest + corpus manifest), `5103-5108` (`neg8_deferred_screen` chains screen then allowance) | Step order `model_identity` (7562), `neg8_corpus_physics` (7570), `neg8_screen` (7571), `finish` writes `harvest.json` with `outputs` (7361). Record is structure only: paths, SHA-256s, canonical row digest, basis digest; the energies stay in `withheld/neg8-rescreen-bracket.json` and `withheld/neg8-clean-bound.json`. `neg8_screen` is called from one site only. Tests `HarvestSurvivorTests::test_the_survivor_rescreen_is_the_bracket_the_allowance_consumer_reads` (real harness, (3,1,2), asserts no `_j"` key in the record and that a replaced withheld bracket is `survivor_bracket_unauthenticated`), `..._a_clean_window_names_the_stored_bracket`, `..._a_failed_screen_supplies_no_allowance`, `..._a_clean_corpus_bound_is_authenticated_for_the_allowance` (bound(10 clean) = 0.7 J; a byte appended to the clean bound is `clean_bound_unauthenticated`). |
| 1 | A1: the consumer `harvest_neg8_allowance_bracket` | SOUND | `whole_window.py:7195-7395` | Chain: `harvest.json` (governed reader), `outputs["derived/neg8-allowance.json"]` digest, record bytes hash-checked, schema, `row_sha256` and `evaluation_basis_sha256` must equal the row handed in, then `source`. `stored_verdict` returns the row's own bracket (the harvest names it only when no new loss, no clean bound, no `neg8_*` reason). `survivor_rescreen` authenticates the withheld wrapper at the recorded digest, requires `decision == "passed"` and `conditions == []`, the bound artifact's canonical digest and `validate_neg8_drift_bound_artifact`, the clean bound bytes + clean corpus bytes with `require_corpus_identity=True` when a clean bound was used, `drift_bound_artifact == stored` when the stored bound was used, both families present, and recomputes `drift_allowance_j`, `trajectory_excursion_max_j`, `derived_repeatability_bound_j` through `_family_drift_record`. Any other source is `screen_not_passed`. No path falls back to the stored bracket after a recorded re-screen (`SurvivorAllowanceConsumerTests::test_a_recorded_rescreen_that_does_not_authenticate_refuses`: withheld bytes replaced, record text flipped to `stored_verdict`, `harvest.json` removed, all `absent`; `..._whose_allowance_does_not_recompute_refuses`: consistent hashes over 0.5933 gives `survivor_arithmetic_differs`). |
| 1 | A1: `whole_window_drift_allowances(neg8_harvest_archive)` and the bbdae1e86 governed-reader change | SOUND | `whole_window.py:7402-7580`, `7210-7230` (`_archive_bytes` through `read_authentication_input`) | The record is consulted when the archive is given or the root is a HAZARD root (`_is_hazard_runs_root` = `window_lineage.is_hazard_locator(root / ".joulewise-launch-lineage.json")`); `(None, problem)` gives `absent`; the row still passes `_validate_row` first. `absent` without the archive on a HAZARD root is NUMBER_INTEGRITY: only the harvest sees the monitor journals, so a stored bracket read without its screen record may hold a contaminated energy (the Sol A1 trigger: 0.5933 J for 0.6383 J). `analyze_claims`, `load_analysis_inputs`, `whole_window_drift_allowances` carry the argument; `cli.py` adds `--neg8-harvest-archive`. `test_a_hazard_window_without_its_harvest_archive_refuses`, `test_a_survivor_rescreen_supplies_the_survivor_allowance` (0.6383 gross and idle-subtracted, basis sha carried). |
| 1 | A1: consumer plumbing on the floor path | **DEFECT D1** | `floor_extraction.py:2949-2957`, `2977-2993`; `scripts/mint_floor_artifact.py:1102`; `scripts/extract_detection_floors.py` (no allowance or archive argument) | `extract_cells` calls `whole_window_drift_allowances(runs_root, referenced_bundle_ids, evaluation_basis_sha256, consumption_session, consumption_semantics_id)` with no archive and has no parameter to take one; `mint_floor_artifact.py` calls its `allowance_deriver` the same way. On a HAZARD runs root the result is `absent`, and 2977-2993 then gives every cell report `whole_window_drift_allowance_unrecorded`, `floor=None`, `n_admitted=0`. Analysis plan section 4 step 4 runs ALPHA and BETA floor extraction through `scripts/extract_detection_floors.py`, and line 785 says the issuer reads the re-screen bracket after a harvest re-screen; on this path there is no code behind that clause. Direction is safe (refuse, never the stored bracket). See D1 below. |
| 1 | Blinding | SOUND | `derived/neg8-allowance.json`, `derived/neg8-screen.json` (`survivor_bracket`, `clean_bound` digests), `derived/neg8-corpus-physics.json` (`clean_bound` digest) | Digests and paths only; every energy-bearing record is under `withheld/` (`neg8-rescreen-bracket.json`, `neg8-clean-bound.json`). The harness test asserts no `_j"` key in the allowance record. |
| 2 | A2: reference identity in the harvest | SOUND WITH NOTE (N-1) | `harvest.py:5703-5705` (every `neg8_slot`/`spare_slot` member goes to unit `neg8_reference`), `5716-5719`, `5729`, `5737-5776` (`_reference_model_identity`) | Expected identity: the sealed pin under `units.neg8_reference` of `sources/inputs/identity_pins.json` (the arm collector's copy; `override` at 5666-5669), else the strict majority of the measured references and spares; a member that differs is member-level `model.identity_mismatch` with `pin_source`; no strict majority and no pin makes every reference `model.identity_underivable`. Both codes are in `NEG8_REFERENCE_LOSS_CODES`, so the screen drops that reference. No energy read. `ReferenceModelIdentityTests` (real ALPHA roster, sealed pins): a wrong-model spare is a member-specific loss; the audit's exact trigger; any slot; no majority; a sealed pin outvotes a majority; the committed pin with `pin_source == "sealed_pin"`. |
| 2 | A2: pin derivation (`write_b5_identity_pins.py`, 754c8c093) | SOUND | `scripts/write_b5_identity_pins.py:126-140`, `415-446`, `472-485`, `513-518` | Unit from all 20 committed configs (7 references + 13 spares; `find` here: 20 non-order-manifest JSON files); one model, quantization, target and output policy required; runtime stack from the six `neg8-window-*` bundles of `rehearsal-real/{alpha-1,gamma-2}/archive/sources/claim-runs` (all six present here; each `metadata.json` carries `fea4cb94...` and `Qwen2.5-1.5B-Instruct-4bit`), which must pass `check_runtime_environment` against the measurement interpreter; the bundles' digest must equal every frozen pin of that source+revision in `d117_floor_qwen25_1p5b_v1` and `d117_contrast_qwen25_1p5b_vs_7b_v1` (`panel_model_pins`; both trees carry `fea4cb94...`, 2 occurrences each). `write_b5_identity_pins.py --check` here: OK, `identity_pins.json` sha256 `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` (matches `shasum`). Pack units keep their own block-3 references (`work` list, 472-485). `test_write_b5_identity_pins` 28 rows updated, OK. |
| 3 | A3: known losses survive missing manifests | SOUND WITH NOTE (N-2) | `harvest.py:4618-4626`, `4752-4759` | The sealed roster's `neg8_slot` and `spare_slot` members are always named (an unrun spare carries no flag, so it adds no loss); the stored bracket's loss list is trusted only when `neg8_reference_source == verdict_sources` (set in `_neg8_reference_losses` before the read), otherwise every known loss is new and goes to the re-screen, which cannot run on unauthenticated sources, so `neg8.screen_failed`. `RosterNamedReferenceLossTests` (the audit's probe objects: no manifest reads, `contention.request_overlap` on the known end reference, loss mapped, screen failed; a measured spare named; an unauthenticated stored loss list never leaves the stored screen standing). The clean unauthenticated case still leaves the stored screen (pass-3 N-B, unchanged). |
| 3 | A5: a strict-invalid reference is lost in writer, replay and harvest | SOUND WITH NOTE (N-3) | `run_campaign.py:7187-7199`; `whole_window.py:4973-4996`, `5010`, `6824-6845`; `harvest.py:4924-4945`, `4956` | Writer: a succeeded reference with `strict_valid == False` is lost as `strict_invalid` instead of being handed to the evaluator as `None`. On HAZARD `strict_valid` is the structural `validate_bundle(strict=False)` plus the custody triangle plus `_bundle_config_binding_problem` (2873-2918). Replay (row validator): `stored_strict_losses` = the bracket's `strict_invalid` list; each is verified by the triangle or `strict_validate_bundles([path], workers=1)[0]` (a list of problems; `bool` means invalid, correct sense); a listed reference that verifies valid is read, so the replay differs and the row is `whole_window_verdict_provenance_invalid`; an unlisted triangle-invalid reference is `bundle_strict_invalid` as before (`unlisted_strict_invalid="refuse"`); the frozen arm is untouched (`not survivors and ...` at 5010; the frozen `continue` precedes). Harvest: the authenticity pass replays the stored selection (`"read"` mode, `stored_strict`), the exclusion pass now always runs (`exclude is not None`, 4956) with `members[id]["strict_valid"] is False` (full strict), so a structurally valid but strict-invalid reference is dropped before aggregation and the survivors decide. Tests: writer `test_a_strict_invalid_reference_is_lost_not_invalid`; replay `test_a_strict_invalid_reference_is_lost_before_aggregation`, `..._only_as_the_stored_bracket_listed_it`; harvest `test_a_strict_invalid_reference_is_lost_and_the_survivors_pass`, `test_the_audit_strict_trigger_rescreens_the_survivors`. |
| 4 | Census: `pgrep -a`, own tree downward only | SOUND | `night_gate.py:208-219`, `hazards/arm.py:63-68`, `319-351`; `agent_identity.py:394-415` (`in_tree`), `418-470` (`filter_census`) | `in_tree` walks the listed pid's parent chain to the root, or the chain of its process-group leader; an ancestor never descends from the root and a group led by an ancestor is not in the root's tree, so an agent ancestor is kept and the window's descendants are ignored whatever they run. Live test `test_an_agent_ancestor_is_a_hit_and_the_window_is_not` (claude-named zsh, then chain.zsh under `.claude/.../attempt3`, then the census python, then a codex-named sleep, plus a foreign `run_campaign` under `.claude`): for both the gate and the hazard census the ancestor is a hit, the own descendant is `own_tree`, the chain shell and the foreign runner are `not_agent_executable`; ran OK here. `arm_census` discovery deliberately keeps no `-a` (diagnostic; it reads its own ancestors from the kernel table). `quiet_admission.sample_interval` (267-273) and t0 `_agent_lines_decided` (1843-1860) decide the `-a` list with `own_tree_root=os.getpid()`; the sampler's ancestors (chain zsh, `run_campaign` python, driver) are decided by executable, so a `.claude` custody path never makes them hits. `t0_rehearsal` keeps the two former argvs so recorded journals resolve (669-683). |
| 4 | Census: interpreter parsing (A4), legacy filtering, T3 removal | SOUND | `agent_identity.py:133-301`; `arm_census.py:130-134`; `t0_rehearsal.py:69-70`; `prewindow.py:102`; `gen_derivation_night.py:70`; `gen_g2_phase_d.py:342-348`; `physics_rows.json` texts | Probe of `identify` here (18 argvs): native binary `~/.local/share/claude/versions/2.1.289` is agent; `node --require /tmp/preload.cjs .../@anthropic-ai/claude-code/cli.js` and the `--require=` form are agent (the A4 trigger); `node /opt/homebrew/bin/codex exec` is agent; `node -- .../claude-code/cli.js`, `node .../.bin/claude`, `bun run .../@openai/codex/...` are agent; `Claude.app/.../Claude`, ChatGPT's bundled `codex` are agent; `zsh /Users/edr/.claude/custody/chain.zsh`, `.venv python run_campaign.py --root /Users/edr/.claude/x`, `bun -c /x/claude.toml app.js`, `node --max-old-space-size 4096 /y/claude-thing/app.js`, the census pgrep itself are not_agent; `node --unknown-opt value ...`, `node -e "console.log('claude')"`, `node -` are undecided (kept as a hit, the pre-existing policy; the window's own tree is checked before identity, so its own interpreter launches cannot refuse). T3: dropped from `AGENT_PREFIXES`, the arm-census interactive roots, the t0 token regex, the prewindow comm list and the generators; `scripts/prewindow_check.sh` keeps its sealed bytes (`t3` still in its comm list: an over-refusal at the legacy check only, needs an erratum to change; `test_revision6_seal`, `test_prewindow_check` OK). |
| 5 | Pinned estimators byte-identical to a434e363d | SOUND | `joulewise/reduce.py`, `uncertainty_evidence.py`, `powermetrics_fiducial.py`, `adapters/powermetrics.py` | `git diff a434e363d fe28e5a0c --stat` on the four paths is empty. |
| - | Rule check by hand (shapes the test cannot see) | SOUND | `whole_window.py:4990-4996` (`return None, "bundle_strict_invalid"`: the existing refusal, now narrowed to an unlisted triangle-invalid reference in `refuse` mode), `5006` (`continue` on a loss: the ruling's rule), `harvest.py:4668` (`return "screen_failed"` after the existing emit), `_reference_model_identity` (emits flags only), `agent_identity.identify` (`undecided` kept: existing policy) | No new raise, no new call to a raising function in an admission or selection path, no new flag code. `test_refusal_allowlist` 23 OK; `refusal_census` clean (unlisted, stale, miscounted, guard_changed, scope_gaps all empty). Conditions that stopped refusing: a strict-invalid reference no longer fails the whole writer bracket or the whole re-derivation. Conditions that started refusing: an agent that is the census's ancestor (F1: a live agent, the hazard the census exists for); N-2's widening (NUMBER_INTEGRITY, below). The opposite failure (a physics or number hazard turned into a flag): none found; `_agent_lines_decided` returns the raw probe when nothing was ignored and flips exit 0 to 1 only when the kept text is empty. |

## Tests executed here

| Module | Result |
|---|---|
| `tests.test_agent_identity`, `test_night_gate`, `test_arm_census`, `hazards.test_arm`, `test_quiet_admission`, `test_arm_readiness_evidence_t0`, `test_agent_census_concurrency` | 259 OK, 580 s (includes the live ancestor census test) |
| `tests.test_write_b5_identity_pins`, `hazards.test_refusal_allowlist`, `flags.test_flags_exclusions`, `test_whole_window_selection` | 128 OK |
| `python -m tests.hazards.refusal_census` | clean |
| `scripts/write_b5_identity_pins.py --check` | OK, sha256 a0865895... |
| `tests.test_neg8_survivors` | 79 OK, 39 s |
| `tests.test_run_campaign.IdleAdmissionCoreVerdictTests`, `test_hazard_whole_window_verdict`, `test_hazard_neg8_mint_verdicts`, `test_t0_rehearsal`, `test_prewindow_check`, `test_revision6_seal` | 162 OK, 158 s |
| `tests.test_analysis_claims`, `test_floor_extraction`, `test_mint_floor_artifact` | 242 OK (these patch `whole_window_drift_allowances`; none runs the floor path on a HAZARD root, which is why D1 is not caught) |
| `tests.test_harvest_b5_window` | 176 OK, 527 s |

About 1,050 tests plus the census and the pins check, plus one `identify` probe of my own (18 argvs, results in
the table). No process I started is alive (the one live `unittest` process, pid 16683, is another session's shard
runner, started with a different module list; not touched). `/private/tmp/coldpass4` was removed at the end (it held
only the harvest suite's 68 MB template cache).

## DEFECT

**D1 (item 1, floor-path plumbing for the A1 consumer).** *Trigger:* run `scripts/extract_detection_floors.py` (or
`scripts/mint_floor_artifact.py`) on any block-5 floor window's runs root (ALPHA or BETA; the root carries
`.joulewise-launch-lineage.json`, so `_is_hazard_runs_root` is true). *Observed:* `floor_extraction.extract_cells`
calls `whole_window_drift_allowances` with no `neg8_harvest_archive` and has no parameter to take one;
`harvest_neg8_allowance_bracket(None, row)` returns `harvest_archive_required`; the result is `absent`; every cell
report gets `whole_window_drift_allowance_unrecorded`, `floor=None`, `n_admitted=0`. The same window's contrast path
(`python -m joulewise analyze-claims --neg8-harvest-archive ...`) works. *Why it is not a wrong number:* the consumer
refuses; it never reads the stored bracket on a HAZARD root (the Sol A1 trigger would otherwise print 0.5933 J for
0.6383 J). *Why it is not an arming blocker:* no collection, chain, driver, hazard or harvest code is involved; the
analysis plan puts the analysis programs in lane L9 (section 11, written blind, pinned by an addendum to the seal
record), and its section 4 step 4 / line 785 already states the rule the code must implement. *Fix:* add
`neg8_harvest_archive` to `floor_extraction.extract_cells` and pass it to `whole_window_drift_allowances`; add
`--neg8-harvest-archive` to `scripts/extract_detection_floors.py` and to `scripts/mint_floor_artifact.py` /
`mint_floor_artifact_generalized.py` (or supply a partial `allowance_deriver`); one test that runs `extract_cells` on
a root with a HAZARD locator and a harvest archive and gets the survivor allowance, and one that gets
`whole_window_drift_allowance_unrecorded` without the archive. *Disposition:* L9, before section 4 step 4; record in
the lane list. Not a fix round on this head.

## Notes (dispositions for the orchestrator and the seal; no fix round)

**N-1 (item 2, one identity unit for all references; extends pass-3 N-A).** Because every reference and spare now
shares the unit `neg8_reference`, a wrong-model spare emits two flags: member-level `model.identity_mismatch` (its
loss, as the ruling wants) and window-level `model.identity_inconsistent_in_window` (the unit saw two identities;
`test_a_spare_of_another_model_is_a_member_specific_loss` asserts it is emitted). Under the draft catalog
`model.identity_mismatch` is EXCLUDE_WINDOW at any scope (pass-3 N-A) and `model.identity_inconsistent_in_window`
is absent from `DRAFT_CODES` (UNCLASSIFIED, so release-blocked). So the ruling's outcome (drop the reference,
survivors decide) is pre-empted twice for a reference of another model. Direction is conservative; the
classification question is the seal's (the L6 catalog): either give both codes a member-scoped effect for
`neg8_reference` members, or reword the ruling to say a reference of another model excludes the window. Not a
defect of this delta.

**N-2 (item 3, A3's widening).** Before A3 the stored bracket's loss list was trusted whatever the sources said; a
window whose verdict sources do not authenticate and whose writer-dropped reference carries a loss flag kept its
stored screen. Now the same window re-screens, the re-screen cannot run, and `neg8.screen_failed` is emitted
(`observed.reference_source` records the unauthenticated source). This is the one condition in the delta that moved
from "stands" to "excludes". It is NUMBER_INTEGRITY by the rule's text: the bracket's provenance cannot be checked,
so whose energy it holds cannot be known, and the allowlist's `neg8.screen_failed` entry already names "when that
re-screen cannot run". The asymmetry remains that the clean unauthenticated case (no loss flag) still leaves the
stored screen standing (pass-3 N-B); the seal's classification of `whole_window.verdict_unauthenticated` decides it.

**N-3 (item 3, three definitions of "strict-invalid").** The writer's HAZARD predicate is structural validation +
custody triangle + `_bundle_config_binding_problem` (run_campaign-local: `config.json` run id and content against the
registered config); the harvest's is `validate_bundle(strict=True)` (`strict_problems`) plus the triangle in the
exclusion pass; the replay's is `strict_validate_bundles` (strict) plus the triangle. `cli.validate_bundle` has no
config-binding check. Consequence: a reference whose `config.json` disagrees with its registered config is listed
`strict_invalid` by the writer, verifies valid in the replay and the harvest, is read, the replay differs, and the row
is `whole_window_verdict_provenance_invalid` (analysis path) or the screen is `neg8.screen_failed`
(`rederivation_differs_from_stored_bracket`). Reachable only through a bundle whose config the runner did not write
(a corrupted or edited bundle); the outcome is an exclusion, the same as before A5 (then
`neg8_bracket_reference_invalid`), never a pass. Disposition: the consolidation lane below; no change on this head.

**N-4 (item 1, the collected-subset bound in the consumer).** When `bound_used == "collected_subset"`, the consumer
checks the bound artifact's canonical digest against the record and `validate_neg8_drift_bound_artifact(artifact)`
without corpus bytes; the harvest validated that bound against its collected-manifest bytes
(`neg8_collected_bound`). The record's digest rests on `harvest.json`, read through the governed reader, as the
stored-verdict path rests on the verdict row. Acceptable under the project's threat model (hallucination, not
forgery); if the seal wants byte-level parity with the clean-bound path, the harvest can record the collected
manifest's digest beside the bound as it does for the clean corpus. Not a defect.

## The NEG-8 survivor logic in three places: seal now, consolidate the predicate after

The logic lives in (1) the writer, `run_campaign._idle_admission_core_evaluation` (losses it can see: status,
unreadable summary, its own strict predicate); (2) the replay, `whole_window._derived_neg8_decision`, one function
shared by the row validator and the harvest, parameterised by `exclude_bundle_ids`, `strict_invalid`,
`stored_strict_losses`, `unlisted_strict_invalid`; (3) the harvest, `neg8_screen` / `_neg8_rescreen` /
`_neg8_reference_losses` (losses only it can see: the 6.4 physics codes, timeout, abort, identity, its own strict
check, the roster's absent members). The evaluator (`evaluate_neg8_point_drift`), the count-adjusted bound
(`neg8_count_adjusted_bound`) and the re-derivation are already single implementations; what differs between the
sites is the loss vocabulary each can observe and the strict predicate (N-3). Every disagreement between the sites
ends in an exclusion (`rederivation_differs_from_stored_bracket` then `neg8.screen_failed`;
`whole_window_verdict_provenance_invalid`), never in a passing screen or a read of a dropped energy, and the tests
exercise each site for the status, unreadable, strict, physics, identity and absent cases, with the real harness for
the harvest. That is consistent enough to seal. Consolidation should be a named post-seal lane: one strict-invalid
predicate (structural + triangle + config binding + strict) used by the harvest's `assess_member` and the row
validator, so the harvest and replay drop exactly what the writer drops. It should leave the writer's bytes alone
(`run_campaign.py` runs inside the window) and move the harvest and replay toward the writer's predicate, so no
erratum is needed. Do it with D1 in the same lane: both are claim-time and harvest-side, and both touch only what
a cell or claim reads, never what a window collects.

## Refusals and exclusions checked against the rule in this delta

- New refusals: none. New flag codes: none. `hazard_refusals.json` unchanged on the measurement paths; census clean.
- Narrowed refusals: `bundle_strict_invalid` in `_derived_neg8_decision` (an unlisted triangle-invalid reference in
  `refuse` mode, or the no-survivors arm); the writer's `neg8_bracket_reference_invalid` no longer fires for a
  strict-invalid reference.
- Widened exclusions: N-2 (unauthenticated sources plus a loss-flagged, writer-dropped reference; the re-screen
  cannot run; `neg8.screen_failed`); NUMBER_INTEGRITY.
- Widened physics refusal: an agent that is the census's ancestor (F1); the window's own processes and
  argv-substring-only processes stay ignored (live test).
- Claim-time refusal with no route to the record: D1 (`whole_window_drift_allowance_unrecorded` on every block-5
  floor cell until L9 threads the archive). Safe direction; must land before section 4 step 4.
