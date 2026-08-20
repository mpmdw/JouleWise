# D-144 PRE-MERGE SEAT PASS — Opus seat findings (contract lens)

Worktree `wtSEAT-O` at merge head `afb7d57`. Scope `git diff 7d4454e..afb7d57 -- joulewise/ scripts/ configs/ tests/`
(493 files; 46 code/test files, 2 875 insertions outside the emitted `_v3` trees).
All digests below were recomputed in the worktree, not read from prose.

---

## BLOCKERS

**None.**

---

## SHOULD-FIX (correct today, fragile)

### SF-1 — S5's superseded-era report is unreachable from any production caller in the mixed-era case
`joulewise/calibration_bracketing.py:2003` adds a `diagnostics: list[dict[str,str]] | None`
out-parameter, filled at `:2118-2126`. **No production caller passes it**: `joulewise/whole_window.py:649`,
`joulewise/whole_window.py:4086`, `scripts/run_campaign.py:4641` all omit it; the only callers that
supply it are `tests/test_calibration_bracketing.py:2183,:2228` and
`tests/test_calibration_live_three_window.py:1636`. The reason-code path is additionally gated at
`:2127` by `if not candidates:` — so when a ledger holds **both** a v3 candidate and a superseded
observation, `calibration_bracket_for_bundles` returns neither `capture_pipeline_superseded` in
`reasons` nor any diagnostic, and the superseded observations are silently dropped from the
candidate set.

Offends R1 ruling S5: *"rejection solely on `anchor_method_version` **reports**
`capture_pipeline_superseded` and is excluded from the `registered_valid` reconciliation, so era
eligibility never masquerades as `calibration_ledger_custody_invalid`."* The second half is
executed-correct (`:2081` excludes superseded from `registered_valid`, so the custody-invalid
early return at `:2092` can no longer fire on era grounds). The first half — *reports* — holds
only in the all-superseded case. Mixed-era era rejection no longer masquerades as custody-invalid;
it is now invisible. S5's closing sentence ("the retained mixed-era regression asserts the era
reason") is satisfied only through a test-only channel.

### SF-2 — two independent era predicates with two different constants
S3 ruled one closed predicate: `capture_pipeline_refusal` +
`CLAIM_BEARING_ANCHOR_METHODS` (`joulewise/uncertainty_evidence.py:1299,:1302`).
`joulewise/calibration_bracketing.py:1271-1280` `_capture_pipeline_refusal_for_observation`
re-implements the era test against a **different** constant,
`ACTIVE_CAPTURE_ANCHOR_METHOD` (`uncertainty_evidence.py:1298`). The two coincide today (both
`CLOCK_METHOD_V3`), so behaviour is correct. S1 keeps every era forever and the next flip is the
event that separates "the method we now capture with" from "the set of methods that may bear
claims"; on that day the calibration lane and the claim lane disagree and nothing tests the
equality. Second defect in the same function: it returns `capture_pipeline_superseded` when
`anchor_method_version` is **absent**, collapsing the absent/superseded taxonomy that r6 was
issued to establish (15-amendment-r6.md, "BLOCKER-2 predicate inversion; the S3 taxonomy split").
Executed check — this is latent, not live: `joulewise/calibration_ledger.py:2458-2460` refuses any
observation with an incomplete T1 binding and `anchor_method_version` is in `V2_BINDING_FIELDS`
(`joulewise/powermetrics_fiducial.py:110`), so a `valid` observation always carries a non-empty
method.

### SF-3 — the `schema_v2.json` acceptance-id conditional has no registry-sync test
`scripts/floor_mint_pinsets/schema_v2.json:180` (`n19AcceptanceIds`), `:186` (`n17AcceptanceIds`)
and the two `allOf` conditionals at `:713` and `:993` hardcode the generation→screen mapping.
Nothing under `tests/` references either `$defs` name (grep: zero hits), and nothing binds them to
`ISSUED_ACCEPTANCE_REGISTRY` / `_D102_GENERATION_DERIVATIONS`
(`joulewise/calibration_bracketing.py:141-176,:196-259`). A future `_r7` registered in Python but
not added to `n17AcceptanceIds` makes **both** `if` branches false, at which point the permissive
outer enums (`:204`, `:210`) accept *either* screen value — the exact crosswire the conditional
exists to forbid. Not live wrong behaviour: the Python gate
(`scripts/mint_floor_artifact_generalized.py:638-651`) still raises
`unregistered acceptance generation`. This is silent loss of a defence-in-depth layer, and R2 S4
ratified the conditional as the artifact-layer half of that defence.

### SF-4 — unruled controller stage reorder inside the ruled transaction
`joulewise/controller.py:858-865` moves `_capture_post_run_environment_observation()` out of
`_stage_cleanup` (its old site was inside `_stage_cleanup`, immediately before
`self._complete_stage("cleanup", metadata)`) into `_run_lifecycle`, between `_stage_cleanup()` and
`_stage_reduce()`. R1 S7's site census lists only `controller.py:1355-1362` (the S8 seed envelope)
for this file; there is no recorded amendment, and the execution custody
(`docs/process_traces/2026-08-19-refreeze-execution/reports/*.md`) has zero hits for
`post_run_observation` / `_stage_cleanup`. Behaviourally the reorder is safe — `_stage_cleanup()`
has exactly one call site (`:860`) and is followed unconditionally by the new call, so no path
loses the capture — but it changes the instant at which `collect_environment_guard_observation`
samples adapter power (now after cleanup teardown rather than during it), and that observation
feeds `adapter_wattage_continuity`, which claim gates read
(`scripts/run_campaign.py:6094`). A behaviour change to claim-adjacent evidence timing landed
without a ruled clause or an amendment.

### SF-5 — the no-copied-scalar guard is an allowlist, not a derived set
`tests/test_mint_policy_resolver_guard.py:12-16` checks exactly three files
(`joulewise/floor_mint_estimator.py`, `joulewise/detection_floor.py`,
`scripts/mint_floor_artifact_generalized.py`). R2 S1(i) is broader — *"no literal screen scalar or
screen-substituted rule string anywhere in the mint lane"* — and a new mint-lane module, or a
literal reintroduced in `joulewise/whole_window.py` / `joulewise/floor_extraction.py`, is outside
the guard. Executed: the invariant holds at head — the only occurrences of `0.010818` / `0.009724`
under `joulewise/` and `scripts/` are the registry's own values at
`joulewise/calibration_bracketing.py:199` and `:211`.

---

## NITS

- **N-1** `joulewise/powermetrics_fiducial.py:37` still imports `CLOCK_METHOD_V2`; its only
  consumer was the `or CLOCK_METHOD_V2` silent default that S7 ruled must die (`:1466-1471`, now
  `raise ValueError("detection anchor method is missing")`). Dead import.
- **N-2** `joulewise/uncertainty_evidence.py:29` `SCHEMA_FOR_ANCHOR_METHOD` is a mutable `dict`
  while its era siblings `NATIVE_ANCHOR_METHODS` (`:24`) and `CLAIM_BEARING_ANCHOR_METHODS`
  (`:1299`) are frozensets. S1 makes it the single canonical era mapping and
  `joulewise/cli.py:1237` derives strict's accepted schema set from its `.values()`.
- **N-3** `tests/test_gen_state.py:285` — the running-count audit comment now ends
  `73 - 1 = 73 exact live records` while the assertion at `:287` moved `72`→`73`. The number is
  right (`REFREEZE-D147-CLOSE` was added at `:24`); the arithmetic chain that justifies it is
  broken and drops the addition. The comment is the only audit trail for that count.
- **N-4** `tests/test_gen_state.py:636-641` — the synthetic-gate oracle helper now rewrites
  `REFREEZE-D147-CLOSE`'s status from `active` to `queued` before validating. It is scoped to one
  task id and honestly commented, but it means a real regression that leaves that row `active`
  under a select-scoped gate is no longer observable by this suite.
- **N-5** Test isolation, unreproduced: my ad-hoc invocation
  `python3 -m unittest tests.test_p2038_production_path tests.test_powermetrics tests.test_reduce
  tests.test_run_campaign tests.test_mint_floor_artifact_generalized tests.test_detection_floor
  tests.test_authentication_io tests.test_arm_readiness_evidence_author tests.test_calibration_exits
  tests.test_gen_state` gave `Ran 805, FAILED (failures=1)` with a 7.4 MB diff, while **all ten pass
  standalone** and all ten pass under canonical discovery. That signature is a module-level cache
  poisoned by a cross-module import order, and this transaction reshaped exactly such a cache —
  `tests/test_reduce.py:62` `_SELF_CONSISTENT_CALIBRATION` → `_SELF_CONSISTENT_CALIBRATIONS`
  (dict keyed by anchor method), imported by `test_calibration_exits`, `test_powermetrics_fiducial`,
  `test_p2038_production_path`, `test_whole_window_selection`. I did not identify the failing test
  and it does not appear under the gate's own invocation; recorded so the magistrate can decide
  whether to spend a run on it.
- **N-6** Each `_v3` pack ships a self-check command that no longer runs. The generator writes
  `python3 configs/campaigns/<pack>_v3/generate_configs.py --check` into its own artifacts
  (`configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py:1899,:1927`). Executed at the
  merge head, all three exit non-zero with
  `generation failed: the current frozen identity requires preserve mode`;
  `--check --preserve-current-frozen-bytes` passes on all three. This is the same post-freeze shape
  the `_v2` packs already carry (inherited, not a regression), but the ruled S4 acceptance step
  ("`--check` per `_v3` root") is no longer replayable as written.

---

## KNOWN RESIDUE — root confirmed, NOT deeper than the classified seam

`tests/test_d117_v3_family.py::test_unedited_v2_generators_emit_v3_successors` ×3. Executed root
cause, not inferred:

- `generation_arm_readiness_attachment()`
  (`configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:431`) resolves the freeze
  attachment from `REPO_ROOT / identity.pack_rel` — the **real repo's `_v3` pack** — irrespective of
  `--output-root`.
- `check_current()` (`:2569-2580`) then reads the receipt named by the generated tree from
  `check_root` — the temp root.

Before S5 committed `freeze-0003.json`, the real `_v3` pack had no committed receipt, the
attachment's `freeze_receipt` was `None`, the read was skipped, and the test passed. After the
mint it resolves to `freeze-0003.json` and fails with
`FileNotFoundError: …/d117-v2-to-v3-*/configs/campaigns/d117_floor_qwen25_1p5b_v3/arm_readiness.freeze.receipts/freeze-0003.json`.

This is a `REPO_ROOT`-vs-`check_root` asymmetry confined to **re-emitting a successor that already
has a committed freeze receipt**. A genuine fresh successor emission (target pack not yet frozen)
still works, and in-tree `--check` has `check_root == REPO_ROOT` so both sides agree. The packet's
"post-mint fixture/check-mode seam" classification is correct; I found no deeper root and no
production-route consequence.

---

## POSITIVE VERIFICATIONS (executed, this seat)

**Frozen surfaces — all recomputed:**
- `committed_pack_tree_sha256` on the three `_v2` roots at head = `95f7c51c…`, `e5ec0f74…`,
  `2fe51b03…`; `freeze-0002` receipt shas = `1277103b…`, `decd8cdc…`, `18855647…`. All six
  digits-for-digits identical to the T10 table
  (`docs/run_reports/2026-08-18-t10-session.md:1027-1029`). No `_v1`/`_v2` pack path appears in the
  scope diff.
- All `freeze-0002`/`freeze-0003` receipts match their `.sha256` sidecars; every evidence file
  matches its sidecar and its in-receipt pin (0 mismatches across all six packs);
  every `plan_tree.sha256` / `calibration_plan.sha256` sidecar matches; each freeze receipt's
  `pack_identity.plan_sha256` matches the committed plan bytes.
- `freeze-0003` predecessor blocks bind each pack's own `_v2` root and its `freeze-0002` (recomputed
  `pack_sha256` matches), ordinal = predecessor+1, `pack_root` path-bound to
  `/Users/edr/JouleWise-measurement-20260818/…` — R2 S3 as amended, satisfied.
- Git history check: `plan_tree.json` / `producer_contract.json` / `calibration_plan.json` in each
  `_v3` pack last changed **in the same commit as its freeze-0003 mint** (`5e38f1e`, `eb7f6c6`,
  `94dc3b3`). Nothing mutated a frozen pack afterwards; S8's "freeze-0003 last" invariant holds.

**The r5→r6 drift class does NOT recur — the check this pass most owed.** All four D-079-pinned
estimator sources match head bytes exactly against the r6 record
(`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`
`prospective_rederivation.estimator_code_sha256`): `powermetrics_fiducial.py 386e8254…`,
`uncertainty_evidence.py 257cda08…`, `adapters/powermetrics.py 70f47086…`, `reduce.py 7b9c0d28…`.
`git log 3038eeb..afb7d57 -- <those four>` is **empty**. No `_r7` is owed; bind-at-birth holds at the
merge head. Every `_v3` pack's `arm_readiness.sources/*.json` `primary_artifacts` code pin
(`joulewise/**`, `scripts/**`) also matches head bytes — 0 code mismatches per `_v3` pack.
(The `_v2` packs show 18-19 mismatches including code — correct and intended: they are frozen
against pre-flip code and are retired history.)

**S3 per-lane mutation-kill — executed, the S1 contract lens's BLOCKER-1 is genuinely cured.**
Flipping `capture_pipeline_refusal` to fail-open in **one lane at a time** kills ≥1 test in each
lane independently, and 0 tests at baseline:

| lane (patched module) | baseline | mutated | tests killed |
|---|---|---|---|
| `analysis_engine.inputs` | 23 run, 0 fail | 2 fail | `test_analysis_engine.MixedWireAnchorTermIntersectionTests.test_window_precheck_refuses_capture_pipeline_presentation` (superseded, absent) |
| `floor_extraction` | 172 run, 0 fail | 2 fail | `test_floor_extraction.TelemetryIdentityGateTests.test_absent_anchor_member_refuses_capture_pipeline_absent`, `…test_v2_anchor_member_refuses_capture_pipeline_superseded` |
| `whole_window` | 123 run, 0 fail | 2 fail | `test_whole_window_selection.MaxBracketConsumptionTests.test_d079_measurement_shape_refuses_capture_pipeline_presentation` (superseded, absent) |

**Ruled-clause conformance, spot-verified:**
- S1: `SCHEMA_FOR_ANCHOR_METHOD` is the single mapping; **method is the sole dispatch key** — no
  `schema_version`-based era dispatch remains anywhere in `joulewise/`/`scripts/` (all surviving
  `p2-038.x` occurrences are comments/docstrings). Crossed pairs refuse:
  `cli.py:1252-1257` emits `clock_anchor_era_inconsistent` and, with an unregistered method,
  `resolve_clock_evidence_deriver` (`uncertainty_evidence.py:1342`) raises before re-derivation.
- S2: era-faithful strict verify per method; the `cli.py:1575` rich-telemetry fail-open is dispatched
  on method (`cli.py:1585-1589`), and `test_capture_pipeline_era.test_v3_corrupt_rich_telemetry_is_not_fail_open`
  covers the .3 corruption case. Residual early-returns in that function are backstopped by
  `_strict_uncertainty_evidence_problems`; both feed the same problem list (`cli.py:545,:547`).
- S6 (R1): the campaign gate is **equality against the active constant** —
  `scripts/run_campaign.py:1639-1649` compares both `schema_version` and `method` to
  `SCHEMA_FOR_ANCHOR_METHOD[ACTIVE_CAPTURE_ANCHOR_METHOD]` / `ACTIVE_CAPTURE_ANCHOR_METHOD`, no
  set-membership.
- S7: `powermetrics_fiducial.py:1466-1471` raises on an absent method (silent `or CLOCK_METHOD_V2`
  killed); `environment_admission.py:307,:351` dispatch through `resolve_anchor_reconstructor`;
  `analysis_engine/inputs.py:190` dead-status fix `"unresolved"`→`"unknown"` matches the statuses
  the derivers actually emit (`uncertainty_evidence.py:125,:264,:300,:710`);
  `arm_readiness.py:4149-4150` `_issued_d079` gains r5 **and** r6.
- S8: executed — the controller seed envelope carries **no** `schema_version` and **no**
  `clock_anchor` (`controller.py:1360-1363`); `capture_pipeline_refusal` returns
  `capture_pipeline_absent`; strict fails the bundle closed
  (`['…unsupported or missing schema_version', '…clock_anchor and sample_phase must be objects']`).
- R2 S2/S4: the `_v2`→`_v3` generator delta is **exactly** the three ruled edit sites plus the
  tool-emitted `_v2`→`_v3` renames — verified by full `diff -u` on all three pairs. Nothing else
  moved. `CURRENT_FROZEN_RECEIPT_SHA256` in each `_v3` generator equals **that pack's own** `_v2`
  freeze-0002 sha (the ruled hygiene fix), verified for all three.
- R2 S4 regression assertion: `--check --preserve-current-frozen-bytes` **passes on all three `_v2`
  roots** at the merge head, and the worktree stayed clean (`git status --porcelain` empty).
- R2 S6: `DEFAULT_ACCEPTANCE_BOUND_SHA256` → `GENESIS_FIXTURE_ACCEPTANCE_SHA256`, value `9a264c57…`
  unchanged, both call sites renamed (`calibration_bracketing.py:735,:828`), comment present
  (`:174-176`), and the executed-proven silent-coverage gap is closed by
  `tests/test_calibration_bracketing.py:625-640`. Verified the constant is genuinely **not** the
  digest of `DEFAULT_ACCEPTANCE_BOUND_PATH`.
- R2 S2 crosswire guard: implemented at `calibration_bracketing.py:262-297` and **tested**
  (`tests/test_calibration_bracketing.py:685-736`, both poisoning directions).
- Acceptance registry integrity: all six `ISSUED_ACCEPTANCE_REGISTRY` `file_sha256` pins match the
  committed bytes, each file's own `acceptance_id` matches its key and `artifact_role` is `issued`;
  `ACTIVE_ACCEPTANCE_ID` = r6; r6's `derivation_sha256` `18d09aa9…` matches the pin in both `_v3`
  floor generators.
- Reason-code plumbing: `capture_pipeline_absent`/`capture_pipeline_superseded` in
  `ENGINE_REASON_CODES` + `_NOT_RESOLVABLE` + `floor_extraction.CELL_REFUSAL_CODES` +
  `whole_window._REDERIVATION_LEAF_REASONS`; `instrument_calibration_capture_time_mismatch` in
  `REDUCER_REASON_CODES` + `_NOT_RESOLVABLE` + the whole-window leaf set and both `reduce.py`
  mappings (`:1833,:2410`). `ordered_reason_codes` accepts all three without raising.

**Canonical suite — run independently by this seat at `afb7d57`.**
`python3 -m unittest discover -s tests` → **Ran 3759 tests in 2718.8 s, FAILED
(failures=3, errors=1, skipped=95)**.
- The 3 failures are exactly the classified residue
  (`test_d117_v3_family.test_unedited_v2_generators_emit_v3_successors` ×3).
- **The 1 error was self-inflicted by this review and is not an artifact defect.**
  `ERROR: test_committed_v2_pack_tree_digests_are_unchanged_at_head (pack='d117_floor_qwen25_1p5b_v2')`
  → `ArmReadinessError: untracked pack directory: b'__pycache__'`
  (`joulewise/arm_readiness.py:2638`). My `importlib` load of the `_v2` generator, taken to get the
  residue traceback, wrote `configs/campaigns/d117_floor_qwen25_1p5b_v2/__pycache__/`. Removing it
  restores `tests.test_d117_v3_family` to **exactly the 3 known-residue failures**, and the three
  `_v2` digests recompute to `95f7c51c…`/`e5ec0f74…`/`2fe51b03…`. Read the other way this is a
  positive: the pack-tree guard detected a stray untracked byte inside a frozen pack within one
  review session. Worktree left clean (`git status --porcelain` empty, no `__pycache__` under
  `configs/`).

**So the packet's "exactly one known residue" claim is independently confirmed.**

Other suites, all green at head: `test_calibration_bracketing`, `test_mint_policy_resolver_guard`,
`test_floor_mint_estimator`, `test_environment_admission`, `test_powermetrics_fiducial`,
`test_controller`, `test_d078_reason_registry`, `test_analysis_engine` (Ran 259, OK, 1 skip);
`test_analysis_claims`, `test_analysis_integration` (Ran 160, OK);
`test_analysis_finalizer`, `test_whole_window`, `test_calibration_writer_crash_matrix` (Ran 81, OK);
and standalone `test_mint_floor_artifact_generalized`, `test_arm_readiness_evidence_author`,
`test_p2038_production_path`, `test_detection_floor`, `test_authentication_io`,
`test_calibration_exits`, `test_gen_state`, `test_powermetrics`, `test_run_campaign`,
`test_reduce` — all OK (see N-5 for the one ad-hoc multi-module invocation that did not reproduce).

---

## RECOMMENDATION

**GO** for the merge wave.

Canonical discovery at the merge head carries exactly the one classified residue; the fourth result
in my run was my own contamination, cured and re-verified.

Single strongest reason: the drift class this pass was convened to hunt — a fix round silently
falsifying a design-time verification, the r5→r6 signature — **does not recur at the merge head**,
and I proved it by recomputation rather than by reading the custody: all four D-079-pinned estimator
sources hash exactly to the r6 record's `estimator_code_sha256`, no commit after the r6 issuance
touches any of them, every `_v3` pack's evidence pins the code that head actually runs, the three
`_v2` pack digests are digits-for-digits the T10 table, and the S3 claim barrier kills a test in
each of the three claim lanes independently under a fail-open mutation. Nothing I found is
wrong behaviour or a broken frozen surface; the five should-fix items are all latent-divergence or
missing-guard defects that a follow-on transaction can absorb without touching a frozen artifact.

SF-1 is the one I would ask the magistrate to route into the same wave rather than defer, because it
is a one-line change (drop the `if not candidates:` guard at `calibration_bracketing.py:2127`, or
pass `diagnostics` at the three production call sites) and because it is the only finding that
leaves a claim-adjacent lane silent where a ruled clause says it must report.
