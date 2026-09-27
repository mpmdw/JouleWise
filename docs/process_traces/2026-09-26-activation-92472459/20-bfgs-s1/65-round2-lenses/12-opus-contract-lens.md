# BFG-S S1 round 2: Opus contract lens on `21213be7`

Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), contract lens. One foreground session, no subagents, no background tasks. Charge: `65-round2-lenses/00-lens-charge.md`. Authority: the round-2 brief `60-round2/10-seat-brief.txt` and the texts it names (FT v1.1 texts 9, 10, 12, §E, §F T9/T10/T12; AD2 amendments 24–27; ERR amendment 26; SCOPE amendments 36 (round-2 rule), 41 (round-2 note), 42).

**Where I worked.** Every probe ran in shared clones under `/tmp/opus_r2/` (`head` = `21213be7`, `r1` = `b859317c`, `base` = `1417c0c4`, `mut` = mutant copy of head, reset with `git checkout` after each mutant). No repository file was edited. One side effect in the read-only worktree `JouleWise-wt-s1cg-92472459`: my first sweep run there (before I set `PYTHONDONTWRITEBYTECODE`) may have created the git-ignored `tests/__pycache__/`. `git status --short` shows no tracked change.

**Terms used below.**
- **Gate**: `bundle_read.authenticate_window_members(members)`. It classifies every member bundle's battery evidence and either returns the verdicts or raises. It raises `WindowBatteryRefusal` (a subclass of `RuntimeError`) for a status refusal, and `battery_float.CustodyFailure` or `CustodyUnreadable` (also `RuntimeError` subclasses; MRO printed below) for custody.
- **Sweep**: `tests/test_bfgs_consumer_sweep.py`, the AST scan text 12 requires.
- **Singleton gate**: a gate call whose member set holds one bundle.

---

## 1. Clause table

Verdict key: **exact** = implemented and pinned as ruled; **partial** = implemented, but the pin is weak or a sub-clause is missing; **deviates** = the code contradicts the ruled text; **overreach** = behaviour that no ruled text asks for.

### Text 9 (scored reducer)

| Ruled sentence | Implementation | Pinning test | Verdict |
|---|---|---|---|
| Six-argument `reduce(..., battery_evidence)` | `scored_reduce.py:195` | `test_signature_six_positional` | exact |
| Key set = every placement whose status is not `not_started` | `_check_battery_evidence` `:95-111` | `test_complete_placement_universe_and_no_bundle_vocabulary`, `test_missing_extra_duplicate_and_marker_disagreement` | exact |
| Each entry is a bundle-kind `PairVerdict` whose `bundle_sha256`, **where a capture window exists**, equals the window's digest | `:133` requires a window for **every** `PairVerdict` (`digest is not None and ...`) | none for a windowless placement | **deviates** (B-2) |
| The `{"no_bundle": status}` marker is accepted only for a placement **the roster records as having finalized no bundle**, and only when it equals the roster's status | `:128` checks only "no window, and marker equals status". The vocabulary `{completed, cut_off, not_started}` (`scored_packer.py:237,402`) records nothing about bundle finalization. | the test pins `{completed, cut_off}` as admissible (`test_scored_reduce.py:206`), i.e. every started status | **deviates** (B-2) |
| Missing, extra, duplicate, unbound or non-pass entries raise before `_check_window`; `unobserved_historical` and `not_applicable` count as non-pass; `window_bundle_duplicate` | `:95-138`, called at `:204` before the window loop | `test_input_digest_binding_and_nonpass_statuses`, `test_duplicate_bundle_digest_and_precheck_order` (patches `_check_window` to assert it is not reached) | exact |
| Imports `battery_float` only because text 9 needs it (amendment 36 round-2 rule) | `from joulewise.battery_float import PairVerdict` (`:10`) | guard V2 green | exact |

### Text 10 (bracketing)

| Ruled sentence | Implementation | Pinning test | Verdict |
|---|---|---|---|
| Predicate resolves `custody_locator` and checks the on-disk evidence digest; a mismatch or an unreadable file raises `CustodyFailure`; `authenticate_capture` runs from bytes with amendment 27's `expected` | `calibration_bracketing.py:1814-1859` | `test_digest_bound_pass_confounded_and_identity`, `test_deleted_raw_is_custody_and_removed_key_breaks_digest` | exact |
| Applied at both sites: discovery `continue` right after the pipeline-refusal skip and before `_candidate_from_observation`; the `registered_valid` comprehension | `:1909`; `registered_valid` `:2289`; also `calibration_bracket_for_bundles` `:2833` | `test_confounded_ordinary_row_does_not_empty_discovery`, `test_confounded_row_is_excluded_from_evaluator_universe` (mutant T10-M4 is killed) | exact |
| Excluded endpoints are listed under `battery_excluded_endpoints` and their `b_fiducial_s` is never read | `:2060`, `:2254-2269` | same test (asserts `["charging"]`) | exact |
| Historical boundary: no key and `sequence <= 176` gives `unobserved_historical`, otherwise `evidence_missing`. 176 = the committed head pin at `1417c0c4`; cutoff = that commit's committer time | `:53-54`, `:1850-1853`. I checked the values: `configs/calibration/calibration_ledger_head.json` `"sequence": 176`; `git log -1 --format=%ct 1417c0c4` = `1790462247` | `test_historical_boundary_and_prospective_missing` pins 176; the cutoff is pinned only as `> 0` | partial (N-2) |
| Use rule: a historical endpoint brackets only a window that ends before the cutoff | `:2600` (`>=` refuses) | `test_late_window_cannot_use_historical_endpoint` | exact for row (d); boundary unpinned (N-2) |
| The evaluator re-runs the predicate from bytes and refuses `calibration_battery_float_disagreement` on any difference from discovery | `:2330-2346` | `test_evaluator_reauthenticates_and_refuses_disagreement` runs with `_allow_unissued_fixture=True`, and that flag disables the equality clause (`:2340`). Mutant T10-M1 (clause deleted) survives. | partial (S-4) |
| No production caller passes `_allow_unissued_fixture` | — | `test_fixture_flag_has_no_production_true_caller` | exact |
| Loader polarity unchanged; no carried proof field; no `historical_captures.json` | no diff to `_load_calibration_candidate_unbounded`; `git ls-tree` shows 0 `historical_captures.json` | — | exact |

### Text 12 as amended by 26/42 (consumers), amendment 36's round-2 rule, amendment 41's round-2 note

| Ruled sentence | Implementation | Pinning test | Verdict |
|---|---|---|---|
| Each of the eight consumers calls `bundle_read.authenticate_window_members` before reading energy | whole_window `:679, :3486, :3635, :3907`; inputs `:1864, :2788, :3140`; floor_extraction `:2879`; aggregate `:104, :155`; window_duration_margins `:948`; mint_floor_artifact `:378, :456, :1018`; extract_detection_floors `:142`; run_campaign `:2802, :5331, :6214, :8928` | behavioural: aggregate (2 tests) and the run_campaign helper only; the other six are covered only by the structural test "the module contains ≥1 call" | partial (S-3). The run_campaign collection-time gate is overreach (S-2). |
| `members` = every finalized bundle, `FAILED` included, plus every attempt the ledger records, selected or superseded | run_campaign helper `:6197-6216` (tested); inputs and whole_window enumerate AXI siblings with `rglob`; mint_floor_artifact, window_duration_margins and aggregate use spec, cell or manifest members only | `test_campaign_helper_includes_superseded_ordinary_and_axi_attempts` (mutant M5f is killed) | partial (S-3) |
| Consumers do not import `battery_float` | none of the eight import it (checked with `git grep` at head) | `test_eight_consumer_modules_call_reader_gate_without_battery_import`, which does not see `from joulewise import battery_float` (mutant M7 survives) | partial (S-3) |
| Consumers do not catch `CustodyFailure`, by name or through a broad handler | `inputs.py:1751` `except (OSError, RuntimeError, TypeError, ValueError)` wraps a path that reaches the gate | none; mutants M4b and M4c survive | **deviates** (S-1) |
| Custody and status are never turned into a per-bundle reason or exclusion | same site: both become the string `whole_window_verdict_provenance_invalid` | none | **deviates** (S-1) |
| `unobserved_historical` and `not_applicable` are visible in every window-level output | `battery_float_members` in aggregate, floor-extraction report, `LoadedAnalysisInputs`, window-duration-margins receipt, whole-window verdict row, campaign verdict row | aggregate only (`test_aggregate_exposes_historical_battery_state`) | partial (S-3) |
| Sweep flags every tolerant accessor and **any direct read** of `summary_metrics.json`, `metadata.json` or `power_trace.csv` in an ungated function | `test_bfgs_consumer_sweep.py:118-150` | the sweep's own tests | **deviates** (B-1) |
| Every exemption is a named row with class `non_claim`, `historical` or `strict_validation` | 65 rows; the classes are asserted | `test_all_ungated_reads_have_named_reason` | exact for the rows present. No row covers S1-new code: the head sweep run over base sources reports all 65 rows at `1417c0c4`. |
| Self-test: the sweep reports `joulewise/cli.py:423` at the pre-S1 head | uses `git show b859317c:` (the S1 fix-round head) where the ruled revision is `1417c0c4`; `cli.py` is unchanged in S1, so line 423 is the same | `test_cli_raw_metadata_self_test` | exact in effect (N-4) |
| Amendment 41: the sweep must report `issue_dg071_dg075_statistics.py`'s direct `power_trace.csv` read; the row, if granted, is class `historical` | reported **only** through a clause hard-coded to that site (`:139-146`, keyed on the variable name `actual_path` and a string in the file) | the class is asserted as `historical`; the reason does not cite amendment 41 (N-3) | **deviates** (B-1) |

### Amendment 36 guard row 14

| Ruled sentence | Evidence | Verdict |
|---|---|---|
| The exposed pre-S1 `replace` call gets its exact row, with the replaced type proven by file:line, the count updated and the row reported | Row present and count 14. `CalibrationCandidate` is a frozen dataclass at `:609-610`; `load_calibration_candidate` returns it (the annotation is at `:1522`; the comment cites `:1521`); assignment at `:1686`. The provenance test ran (`1417c0c4` is present). Mutant G-M1 (row text copied into a new function) and G-M2 (a forged `replace(v, status='pass')` in `scored_reduce.py`) are both flagged. | exact (one-line NIT N-1) |

### Protected paths (FT §E, brief)

`git diff --quiet 1417c0c4 21213be7` holds for `joulewise/reduce.py`, `joulewise/bundle.py`, `joulewise/battery_float.py`, the four `ESTIMATOR_CODE_PATHS`, the three paper scripts, `tests/test_calibration_bracketing.py`, `tests/test_calibration_ledger.py`, `tests/test_mint_floor_artifact*.py`, `tests/receipt_corpus.py`, `configs/campaigns/d117_*`, `configs/calibration/`, and `pilot_protocol_v3.json`; no `historical_captures.json` exists. **All byte-identical.** S1's pin test (`test_bundle_read.py:280-304`) does not assert all of them (S-5).

---

## 2. Findings

### BLOCKER

**B-1. The consumer sweep cannot see the usual form of a direct read, and it meets amendment 41's witness only through a site-specific special case.**

The detector (`test_bfgs_consumer_sweep.py:132-146`) flags a read only when the filename literal sits inside the read call's own syntax tree, and only for seven function names. So it misses:

- a path held in a variable;
- a path held in a module constant;
- `open_authentication_input`;
- a function "gated" by any unrelated `.metadata()` call.

Amendment 41's site uses a path variable, so the generic detector cannot see it. The test reports it only through a clause matching `qualname == "build_payload"`, `call.func.value.id == "actual_path"` and a string in the file.

Executed evidence. `M*` mutants go in a new tracked module `joulewise/zz_mutant_claim.py`; each result is the tail of `python3 -m unittest tests.test_bfgs_consumer_sweep`.

```text
M1  path held in a variable: trace = bundle / "power_trace.csv"; trace.read_bytes()      -> OK   (missed)
M1b literal: (bundle / "power_trace.csv").read_bytes()                                    -> FAILED (failures=1)
M1c module constant: TRACE = "power_trace.csv"; (bundle / TRACE).read_bytes()            -> OK   (missed)
M1d open_authentication_input(bundle / "power_trace.csv", ...) + csv.DictReader power_w  -> OK   (missed)
M1e event.metadata(); (bundle / "power_trace.csv").read_bytes()                          -> OK   (missed)
S-M1 new _read_json_object(... "power_trace.csv") inside allowlisted whole_window_refusal_reasons -> OK (row covers path+function+op, not the site)
amendment-41 site with the special case disabled: sweep_source(...) == []   (with it: [('scripts/issue_dg071_dg075_statistics.py','build_payload','direct:read_bytes',537)])
```

The widened detector `/tmp/opus_sweep2.py` flags functions that mention a watched filename and call a read. It finds 23 functions that are neither gated nor listed. Among them:

- `joulewise/floor_extraction.py:1727 _read_summary`, a read of `summary_metrics.json` through a variable, inside a text-12 consumer;
- `joulewise/salvage_dangler.py:634 _telemetry_timestamp_bounds`, which parses `power_w` through `open_authentication_input`;
- `scripts/run_campaign.py:2929 summary_status`;
- `joulewise/cli.py _cmd_reduce`;
- digest reads in `whole_window._validated_evaluation_basis` and `validate_occurrence_supersession_entry`, and in `run_campaign._basis_member_occurrences` and `_run_record_supersession_locked`.

I found no site where one of these releases a claim number ahead of a gate. The sites I traced are behind a gate at their call site, or read only status, time or digests. The finding is therefore that text 12's instrument does not verify the property S1 exists to guarantee. The seat report states the opposite ("adding an ungated direct read makes the sweep fail").

Why BLOCKER: text 12's ruled mechanism does not work, and a ruled acceptance witness (amendment 41: "must report it") is met by hard-coding the witness. Every later PR will rely on this sweep.

Closure:
- Detect path values: any name bound in the function from an expression containing a watched filename or a module constant, and any function whose name starts with `read`, `open` or `load`, or ends with `_json_object`.
- Match `metadata()` only on a receiver that is a `BundleReader` construction or a name bound to one.
- Delete the site-specific clause.
- Key each allowlist row on `(path, function, operation, filename)`.
- Classify every newly reported site, gated or with a row. The refuter checks each row.
- Keep M1, M1c, M1d and M1e as self-tests that must be reported.

**B-2. Text 9 is inverted for placements without a capture window. A genuine `PairVerdict` is refused as `unbound`, and the `no_bundle` marker is accepted for every started status. A confounded voided placement therefore cannot refuse the reduction.**

Text 9 has the key set span voided and terminal placements "whether or not a capture window exists". It binds the digest to a window only "where a capture window exists", and restricts the marker to placements "the roster records as having finalized no bundle". The code does three things instead:

- `:133` demands a window for every `PairVerdict`;
- `:128` accepts the marker whenever there is no window and the marker equals the status;
- the test pins `{completed, cut_off}` as the admissible marker values. That is every started status, and both describe a block that ran.

Executed probe. Fixture `_terminal_night(width=2, kind="ceiling_violation")`, placement `('large:decode:1:0', 0)`, which is voided with status `cut_off`:

```text
passing PairVerdict for no-window placement voided/cut_off: refused battery_evidence_unbound
confounded PairVerdict for no-window placement voided/cut_off: refused battery_evidence_unbound
marker for no-window placement voided/cut_off: REDUCTION PRODUCED (dict)
```

The fixture producer itself emits `{"no_bundle": "completed"}` for four voided or terminal placements whose status is `completed`. The charge asks whether the scored reducer can produce a number from a window with a non-pass member. It can: a started, windowless placement with a confounded bundle is excused by the only input the reducer accepts for it.

Mitigation: `reduce` has no production caller (text 9). Why BLOCKER anyway: this is the contract the harvest producer will be written against, and it contradicts the ruled sentence.

Closure:
- Accept a bundle-kind `PairVerdict` for a windowless placement, binding its digest to the harvest's pinned member digest, not to a window.
- Return NEEDS_RULING on the marker vocabulary. No roster field records "finalized no bundle", so the ruling must name the fact that does (for example, the attempt ledger's finalization record).
- Until then, admit the marker for no status.
- Tests: a confounded `PairVerdict` on a voided `cut_off` placement refuses `battery_float_confounded`; the marker on a `completed` placement refuses.

### SHOULD-FIX

**S-1. `inputs.py:1751` catches the gate's custody and status refusals through `RuntimeError` and turns them into a generic string.**

In `bind_floor_artifact_evidence`, the salvage-component revalidation runs before the function's own gate (`:1864`). Its call chain is:

`whole_window_refusal_reasons` → `_validate_row` → `_validate_row_uncached` (`whole_window.py:5438`) → `_current_core_rederivation_reasons` → `consumption_session._prepare` (`:4347`) → gate (`:679`).

That chain sits inside `except (OSError, RuntimeError, TypeError, ValueError): reasons = ("whole_window_verdict_provenance_invalid",)`. Both gate exceptions subclass `RuntimeError`:

```text
CustodyFailure ['CustodyFailure','RuntimeError','Exception',...]; WindowBatteryRefusal ['WindowBatteryRefusal','RuntimeError',...]
P2 inputs.py:1751 tuple caught WindowBatteryRefusal -> ('whole_window_verdict_provenance_invalid',)
P2 inputs.py:1751 tuple caught CustodyFailure -> ('whole_window_verdict_provenance_invalid',)
```

The handler predates round 2; round 2 made the gate reachable through it. The outcome is still fail-closed: the string enters `global_problems`, and every cell refuses. But the custody class and the member label are lost, which is what amendment 42 (SF-4) and amendment 36's round-2 rule forbid.

Closure: drop `RuntimeError` from that tuple, or re-raise `WindowBatteryRefusal` and `CustodyFailure` first (without importing `battery_float`, e.g. `except WindowBatteryRefusal: raise`, with custody propagated by narrowing). Add a test in which a salvage component with a deleted post raw raises `CustodyFailure` naming the member.

Not in S1's scope, for the record: `analysis_manifest_v3.py:3712` (`RuntimeError`) and `:4499` (`Exception`) turn the same exceptions into `ManifestRefusal`. That is fail-closed, and the class name is kept in the message.

**S-2. `run_campaign.evaluate_member` gets a singleton gate (`:2802`). Text 12 scopes run_campaign to "its final analysis and whole-window verdict".** `evaluate_member` runs at collection time: `run_axi_spec_campaign` `:7445, :7687, :7717, :7948`, and `run_campaign` `:8495, :8617, :8788`. It also runs before `record_campaign_member_provenance` (`:7696, :7724`). This has three consequences:

- A single confounded or evidence-missing member aborts the campaign mid-collection, and its provenance row is never written.
- A MOCK member is `not_applicable`, so every MOCK campaign through `run_campaign` aborts at member 1.
- The final-analysis gate (`:8928`), which lists every refused member, becomes unreachable whenever any member is non-pass. The refusal names only the first bad member, which is the SF-3 shape amendment 42 removed.

Probe:

```text
P1 evaluate_member (collection-time) raised WindowBatteryRefusal: [('m3', 'battery_float_confounded')]
```

Mutant M5 (final-analysis gate deleted) survives every test. Nothing is released (fail-closed), but this is unruled production-night behaviour, the same class as SF-5.

Closure: remove the collection-time singleton, keep `:8928` as the gate ahead of `classify_campaign_members`, and cover `evaluate_member` with a named sweep row. Or bring the magistrate a ruling that collection-time abort is intended, with the provenance-order consequence stated.

**S-3. T12 is pinned structurally, not behaviourally, and the structural test has a blind spot.**

- "`authenticate_window_members` in each of the eight consumers": only aggregate and the run_campaign helper have behavioural tests. Mutants M5 (run_campaign final gate) and M5d (the `load_analysis_inputs` gate) survive.
- The import check misses `from joulewise import battery_float`, the form `calibration_bracketing.py` itself uses. Mutant M7 survives.
- No test pins "does not catch `CustodyFailure`": M4b (mint `_strict_bundle` gate wrapped as `MintError`) and M4c (extract_cells `except RuntimeError`) survive. M4a is masked, because aggregate's `_read_member` singleton re-raises.
- The member-set rule (superseded and `FAILED` included) is tested only for the run_campaign helper. mint_floor_artifact, window_duration_margins and aggregate gate spec, cell or manifest members only.
- Window-level output visibility is tested only for aggregate.

Closure:
- One behavioural test per consumer at its production call site: a two-member window with one confounded superseded or `FAILED` member refuses, naming it; a historical member's status appears in the output.
- Fix the import matcher to cover `ImportFrom(module="joulewise", names∋battery_float)`.
- Add an AST check that no handler in the eight modules whose type includes `Exception`, `BaseException` or `RuntimeError` (or a bare `except`) swallows the gate unless it re-raises.
- For the spec-only member sets, either widen them or obtain a ruling that the verdict-time gate suffices.

**S-4. Text 10's "any difference from discovery" clause is not pinned.** `test_evaluator_reauthenticates_and_refuses_disagreement` passes `_allow_unissued_fixture=True`, and that flag skips the equality check at `:2340`; the test goes green through the separate "non-pass candidate" branch.

```text
T10-M1 drop discovery-equality clause -> OK (survives)
```

Closure: a test without the flag, in which discovery classifies an endpoint `pass` and re-authentication sees `unobserved_historical`, for example because the candidate path resolves to a key-less copy. It must refuse `calibration_battery_float_disagreement`.

**S-5. S1's pin test does not assert the whole FT §E excluded list.** `test_historical_set_bytes_and_protected_base_paths_are_pinned` omits:

- `tests/test_calibration_bracketing.py`
- `tests/test_calibration_ledger.py`
- `tests/test_mint_floor_artifact*.py`
- `tests/receipt_corpus.py`
- `joulewise/battery_float.py` (required byte-identical by the brief)
- the absence of `configs/battery_float/historical_captures.json`

All are byte-identical today; I checked with `git diff --quiet`. Closure: add them to the `protected` list and assert the file's absence.

### NIT

- **N-1.** The guard-row comment cites `calibration_bracketing.py:1521` for the loader's return type; the annotation is on `:1522`.
- **N-2.** The historical cutoff is pinned only as `> 0`, and the `>=` boundary is not pinned. Both mutants survive: `T10-M2 >= -> >` and `T10-M3 cutoff +86400`. Assert `BFGS_HISTORICAL_CUTOFF_WALL_S == int(git log -1 --format=%ct 1417c0c4)` and `BFGS_HISTORICAL_LEDGER_SEQUENCE == calibration_ledger_head.json["sequence"]`, plus the `window_end_s == cutoff` case. Also re-derive both constants if S1 is rebased before merge, since the ruled anchor is the S1 merge base.
- **N-3.** The amendment-41 row's reason ("Pinned pre-directive a10 trace…") does not cite amendment 41, as the note asks.
- **N-4.** The sweep self-test reads `git show b859317c:joulewise/cli.py`. The ruled anchor is the pre-S1 head `1417c0c4`, and the test has no `skipTest` when the commit is absent. `cli.py` is identical in both today.
- **N-5.** Unforced exception narrowing. Several `except Exception` handlers whose try-body cannot reach the gate were narrowed to `(OSError, TypeError, ValueError, KeyError)`. Examples: `mint_floor_artifact._exclusive_write`, `write_outputs_exclusive`, run_campaign `_normalized_benchmark_config`, `read_config_infos`, the two environment-preflight handlers, `campaign_cooldown_before_member`, `main`, `floor_extraction._common_mode_block_input_from_contrast`, and `inputs.declared_evidence_roots`. Exception classes outside the tuple (for example `BundleReadError`, `AttributeError`, `IndexError`) now crash instead of producing the prior structured refusal or cleanup. The outcome stays fail-closed. Either revert the handlers that cannot reach the gate, or list them in the PR body as intended.
- **N-6.** Result-shape additions have no schema bump or tolerance:
  - `battery_excluded_endpoints` is added to every `evaluate_calibration_bracket` result, `not_required` included.
  - `battery_float_status` is added inside the pre and post descriptors, and so enters `_calibration_bracket_basis`.
  - `battery_float_members` becomes a required key under window-duration-margins' exact-key receipt validator.

  Any stored pre-S1 whole-window verdict would now fail `dict(stored) != calibration_bracket` (`whole_window.py:4378`) with `whole_window_verdict_conflict`, and any pre-S1 receipt would fail validation. Probe: `grep -rl instrument_calibration_bracket` over `runs/` and `~/night-archive` campaign logs finds 0, and no committed receipt exists, so nothing breaks today. Record it in the PR body.
- **N-7.** Singleton gates in helpers (`aggregate._read_member`, `inputs._read_bundle`, `mint._strict_bundle`, `run_campaign._whole_window_member`, `whole_window._reference_energy_evidence`) re-hash each bundle that the window gate already classified. They appear to exist to satisfy the function-level sweep. Once B-1 is closed, prefer named sweep rows ("called only behind the window gate at X") to per-member gates.
- **N-8.** Coverage that became invisible. `test_controller` now patches `aggregate_experiment` out; the ruled consequence, that a MOCK `run_experiment` raises at aggregation, is not pinned. `test_mismatch_reaches_floor_but_analysis_window_refuses_not_applicable` drops the analysis-admission `prompt_realization_mismatch` assertion. Pin the MOCK behaviour directly and restore the prompt-realization check on a non-MOCK fixture in round F.
- **N-9.** Differential on local historical bundles (for the lead's information, environmental):
  - The 50 floor-set p2015 bundles under `runs/p2_015_floors_window_a` all refuse `prospective bundle` at head. Their local complete digests differ from the pinned ones (for example `p2015-df-ph-decode-abs-r03`: local `d15fa682…`, pinned `c2851728…`), consistent with `runs/PRUNED.md` (plist traces pruned to iCloud 2026-07-28). At base, `aggregate_experiment` over them returns numbers.
  - On the 13 tracked historical fixture bundles (copied byte-for-byte to `/tmp/opus_r2/fxroot`), `aggregate_experiment` output at base and at head is **identical** apart from the new `battery_float_members` key (all `unobserved_historical`; `members_read 4, members_succeeded 3`).

  No number changed where the bytes are the pinned bytes. Any historical replay on this machine needs the archived traces rematerialized.

---

## 3. Executed evidence (tails)

```text
head: tests.test_bfgs_calibration_bracketing tests.test_scored_reduce.BatteryEvidenceReduceTests tests.test_bfgs_window_consumers tests.test_bfgs_consumer_sweep tests.test_battery_float_consumers
  Ran 51 tests in 43.882s / OK
head: tests.test_bundle_read                          Ran 99 tests in 91.685s / OK (skipped=1)
head: tests.test_whole_window                          FAILED (errors=14)   [r1 b859317c: OK] — all 14 are gate refusals of synthetic fixtures (prospective/config unreadable/missing metadata), round-F debt
head: tests.test_calibration_bracketing (protected)    Ran 93 / FAILED (errors=6, skipped=1) — CustodyFailure on synthetic observations with no instrument_evidence.json, round-F debt
mutants (window-consumer + sweep + guard trio; tails):
  M4a aggregate gate in except Exception      OK (masked by _read_member singleton)
  M4b mint _strict_bundle gate -> MintError   OK (survives)
  M4c extract_cells except RuntimeError       OK (survives)
  M5  run_campaign final gate removed         OK (survives)
  M5b evaluate_member gate removed            FAIL sweep (killed)
  M5c whole_window _prepare gate removed      FAIL sweep (killed)
  M5d load_analysis_inputs gate removed       OK (survives)
  M5e window_duration_margins gate removed    FAIL structural (killed)
  M5f superseded omitted in helper            FAIL helper test (killed)
  M7  `from joulewise import battery_float` in aggregate   OK (survives)
  S-M2 extra allowlist row                    FAILED (killed)
  G-M1 / G-M2 guard forgeries                 FAILED (failures=2) each (killed)
  T10-M4 registered_valid predicate removed   FAIL (killed)
constants: calibration_ledger_head.json sequence 176; git log -1 --format='%ct' 1417c0c4 -> 1790462247
imports of battery_float: base 8 modules; r1 +bundle_read,+controller; head +calibration_bracketing,+scored_reduce (exactly the two amendment 36 permits)
```

Not run: the full V1 (the seat reports 416 OK in 1557 s) and V3. I relied on the module subsets above and on the seat's V2.
