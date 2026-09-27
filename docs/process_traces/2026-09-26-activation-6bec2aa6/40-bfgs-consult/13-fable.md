# BFG-S design consult — Fable seat (blind, one round)

Seat: Claude Fable 5.1 (`claude-fable-5-1`), single foreground session, worktree `JouleWise-wt-bfgsc-fable-6bec2aa6` at `64e39bb9` (verified `git rev-parse --short HEAD`). Session 2026-09-26 ≈08:52–09:10 PDT. No subagents, no background tasks, no `sudo`, `launchctl`, `powermetrics`, installer, inference or live `ioreg`. Only this file was written. No scratch files were needed.

**Read:** the scout packet (11), ex-01 (§5.3–§5.6, X2, A-R5b v1.1 text), ex-02 (§3.7, §4.1, §4.11), ex-03 (§8 F-1, E6, E19), ex-04 (§3.1, §3.10), and at `64e39bb9`: `joulewise/battery_float.py` (constants, `observe`, `validate_window`, `predates_battery_float`, `verdict_record`), `controller.py` (`:425-475` attachment guard, `:860-875` lifecycle, `:941-960`, `:1353-1400`, `:1445-1500` reduce and failure salvage, `:1564-1600`, `:2076-2236` metadata), `bundle_read.py` (`:240-300`, `:379-410`, `:824-840`, `FROZEN_LEGACY_BUNDLE_IDENTITIES`), `bundle.py` (`write_metadata` `:1032-1110`), `reduce.py` (`:2640-2675`), `calibration_bracketing.py` (`CalibrationCandidate` `:607-700`, loader `:1530-1660`, evaluator `:1965-2000`, caller `:2636-2760`, `discover_calibration_candidates` `:1811-1841`), `calibration_ledger.py` (`LedgerObservation` fields), `scored_reduce.py` (whole), `quiet_predicate_campaign.py` (`hard_exclusions` `:1059-1081`, `pilot_summary` `:1139-1280`, `execute` `:1488-1510`), `scripts/sample_quiet_predicate_evidence.py` (`collect` `:1028-1215`, `summarize` `:1462-1530`), `configs/campaigns/quiet_predicate_evidence_01/` (protocol v3, README), the nine d117 pack READMEs and receipt directories, the three `_v5` directories, `arm_readiness_evidence.py:3320-3350`, `scripts/generate_arm_readiness.py:30-60`, `docs/phase_2/window_runbook.md:284-323`, `tests/test_battery_float_sweep.py` (whole), `tests/test_battery_float_consumers.py` (allowlist lines). Not read: `RUN_STATE.md`, `TASK_QUEUE.md`, `CLAUDE*.md` beyond what the harness loaded, the decision log, any other process trace.

**Executed evidence (read-only, this session).** E1 `git rev-parse --short HEAD` = `64e39bb9`. E2 the scout's line pins reproduce: `_run_lifecycle` `:860`; `_stage_prepare()` / `_stage_idle_baseline()` `:869-870`; `_stage_idle_drift_sentinel()` / `_stage_cleanup()` `:873-874`; `_write_metadata` `:2076`, `extra: dict[str, Any] = {}` `:2079`, `self._writer.write_metadata(extra)` `:2235`; `BundleReader.metadata()` `:272-279`; F-1 arm `"battery_float" in evidence or any(` `:439-447`; `scored_reduce.reduce(registration, roster, predicted_decode_s, score_rows, capture_windows)` `:145`; collector `envelope_cpu_start = cpu_total()` `:1066`, `start = clock.stamp()` `:1067`, `session["end_stamp"] = asdict(clock.stamp())` `:1163`. E3 all nine d117 packs hold exactly one freeze receipt each (`freeze-0001` for `_v1`, `-0002` for `_v2`, `-0003` for `_v3`) and 11 source files; the three `_v5` directories hold only `generate_configs.py` (plus two registration JSONs in `d117_contrast_v5`). E4 `pilot_summary` already carries a summary-level refusal that is deliberately not an exclusion (`recorder_kind`, comment at `:1200-1216`: "a new reason would force a registration v3"). E5 `bundle.write_metadata` base keys are `platform, machine, python_version, joulewise_version, schema_version, config_sha256, run_id, git_commit, source_provenance, clock`; `battery_float` collides with none. E6 `BundleReader.raw_artifact_bytes` accepts basenames only, so `battery_float.pre.ioreg` under `raw/` is readable through the strict boundary. E7 the AST guard asserts `len(ALLOWLIST) == 6` (`tests/test_battery_float_consumers.py:186`) and guards `parse`. E8 the sweep's `OBSERVE_CALLERS` names five files (`:69-76`).

**NOT EXECUTED:** no unit test was run; no freeze, authoring or dry-run command was run; the `evaluate_calibration_bracket` no-snapshot branch was not traced past `:2031`; the `BenchmarkConfig` telemetry field name was not confirmed (the controller records `adapters["telemetry"]["name"]` at `:2162`). Everything below marked "obligation" is a design answer, not a bench result.

---

## Q1 — Observation `phase` values for non-derivation windows

**Decision: add explicit phases. Enumeration (v1 record, additive):** `arm_check | publish_install | t0 | validate_install | t0_power_row | slot_pre | slot_post | quiet_pre | quiet_post | bundle_pre | bundle_post`. The field set of §5.4 is unchanged; identity fields are bound as follows. `quiet_*`: `session_id` = the collector's own `session` uuid (`collect`, `session_id = str(uuid.uuid4())`), `plan_id` = the night plan id when the executor passes one, `slot` = `null`, `attempt_id` = `null`, `raw_path` = `raw/battery_float.<pre|post>.ioreg` relative to the envelope directory. `bundle_*`: `session_id` = the bundle `run_id` (the same string `metadata.json.run_id` carries), `plan_id` = the campaign plan id when known, `slot`/`attempt_id` = `null`, `raw_path` = `raw/battery_float.<pre|post>.ioreg` relative to the bundle root.

**Reason.** `slot_pre/post` with a null slot would make every consumer that reads `phase` unable to tell a derivation slot from a quiet envelope from a run bundle without consulting the container, and `validate_window` (the derivation consumer) currently accepts any phase string it finds under `battery_float.pre`; a bundle record accidentally fed to it would pass the phase check. Explicit phases let the non-derivation helper (Q2) refuse `identity_mismatch` when the phase does not name its container type, and let the derivation validator gain a one-line `phase == slot_<p>` check in a later PR without touching the schema. The schema id stays `joulewise.battery_float.v1` because no field is added or retyped; the enumeration is a documented domain widening, which the parser never gates on.

**Failure mode prevented.** A derivation-window consumer accepting a record that was taken around a run bundle (or vice versa), which would let a float observation from one container vouch for another.

## Q2 — Non-derivation verdict and custody

**Decision: one new helper in `joulewise/battery_float.py`, no committed verdict file for these windows.**

```
authenticate_pair(record: Mapping[str, Any], custody_root: Path, *,
                  phases: tuple[str, str],            # ("quiet_pre","quiet_post") | ("bundle_pre","bundle_post")
                  identity: Mapping[str, Any])        # {"session_id": <collector uuid | bundle run_id>}
    -> PairVerdict   # frozen: status, reasons, pre_raw_sha256, post_raw_sha256,
                     #         pre_update_age_s, post_update_age_s, delta_q_mah
```

`record` is the container's stored `battery_float` mapping (`session.json.battery_float` or `metadata.json.battery_float`), `custody_root` the envelope or bundle directory. Order per phase, mirroring §4.1 E2–E6 with the derivation-only E0/E1 removed: (a) phase absent, not a dict, `phase` field ≠ expected, `session_id` ≠ `identity["session_id"]`, `raw_path` ≠ `raw/battery_float.<p>.ioreg`, `raw_stdout_sha256` not 64-hex, `wall_time_s` not numeric → `battery_float_evidence_missing` with reason `<p> evidence missing: <fault>` (`identity_mismatch` is its own reason string); (b) raw file unreadable or sha256 ≠ recorded → **`CustodyFailure`** raised (the existing class); (c) `exit_code ≠ 0` or `timed_out` → evidence missing `probe failed`; (d) `parse(raw, wall_time_s)` raises `ProbeError` (stale, malformed, object count) → evidence missing; (e) `passed` false → `battery_float_confounded`. Status precedence: custody raises before any status; else confounded > evidence_missing > pass. `delta_q_mah` is reported, never gates. The helper never reads a stored `passed`.

**What authenticates the pair to its container.** The container's own record: the `raw_stdout_sha256` recorded by `observe` at write time, plus the identity binding (`session_id` = container id, `phase` = container type). There is no terminal ledger session and no committed harvest file, so there is nothing above the container to vouch for `metadata.json`/`session.json` themselves; that is the same trust level every other field in those files has today (a bundle's `measured_window`, an envelope's `interior`). Where a registry later pins the container (floor artefact members via `complete_bundle_sha256` in `mint_floor_artifact.py:399-404`, paper members by digest), the whole container including its battery record and raw files becomes byte-pinned, which is the only place non-derivation containers are ever authenticated today.

**How ex-02's digest-recorded custody distinction applies.** Exactly as ruled: bytes whose digest was recorded at write time (the two raw files, by the record) and are now absent or different are a **custody failure**, which raises and makes every consumer refuse ("restore the bytes"), never a verdict; every other fault is instrument state and yields `evidence_missing` or `confounded`. Without a ledger there is no E1 analogue for the record file itself, so I do not invent one: a rewritten `metadata.json` is outside this helper's reach and is disclosed as such (D-161 operator-only adversary; the registry pin is the durable answer).

**Guard.** `authenticate_pair` calls `parse`, a guarded name; it needs one allowlist row (`battery_float.py::authenticate_pair → parse`) and the guard's `len(ALLOWLIST) == 6` assertion becomes 7 with a self-test that an un-allowlisted `parse` call in the same module is still flagged. Production consumers (`summarize`, `pilot_summary`, `BundleReader.metadata`, the bracketing loader, `scored_reduce`) call only `authenticate_pair`; the helper's public call is tested through those sites (scout's requirement holds).

**Failure mode prevented.** A consumer trusting a stored `passed`, or a pair from one container vouching for another; and a deleted raw file quietly becoming "evidence missing → excluded" rather than a stop-and-restore.

## Q3 — Quiet-predicate collector bracket unit

**Decision: the 600 s envelope pair only; no per-round observations.** Pre at `:1065`, after `session` construction and before `envelope_cpu_start = cpu_total()` (`:1066`) and `start = clock.stamp()` (`:1067`). Post inside the existing `finally` block, immediately after `session["whole_envelope_observer_cpu_s"] = ...` (`:1164`) and before the block ends, so it runs on `KeyboardInterrupt` and on any round exception as well as on the normal path. Both raw files land directly under `raw/` (`raw/battery_float.pre.ioreg`, `raw/battery_float.post.ioreg`); `session["battery_float"] = {"pre": record, "post": record}` is written into `session.json` at `:1208`. Pass the collector's `clock` monotonic source into `observe(monotonic_ns=...)` so the anchor non-overlap test (§5.6 test 9 shape) is meaningful under the logical clock.

**Reason.** The unit `pilot_summary` retains, pairs and scores is the envelope (`values`, `retained`, `by_index` pairing at `:1274-1280`), so the verdict must attach to the envelope. Per-round observations would put 20 `ioreg` runs inside `[start, end_stamp]`, the span every round's alignment and the power anchor are computed from (scout's stamp fence), for no additional decision: the AC-power per-round probe (`hard_exclusions`, `PMSET_BATT_ARGV`) already exists and stays. Note a deliberate side effect: the rows' `raw.paths`/`raw.sha256` list (`:1199-1203`) collects every file whose parent is `raw/`, so both battery raw files will be digested into **every** round row of the envelope. That is a second, per-row custody record for the same bytes and I recommend keeping it, asserted by test, rather than moving the files to a subdirectory.

**Pre read fails (probe error or predicate fail).** Record it and continue collecting; do not add an exit path. Two reasons. First, the frozen v3 protocol's only collector-exit outcome is `collect_error`, a frozen exclusion reason (`collector_exit != 0` at `pilot_summary:1150`); exiting on a battery failure would record a battery confound under the wrong frozen reason, a false record. Second, the writer rule in §5.3 item 6 is the same ("a failing or erroring pre- or post-observation is recorded and the writer continues; the window verdict decides"). The consumer refuses (Q4). The executor may print a diagnostic line; it decides nothing.

**Collector exits before the post read.** If the process dies so hard that `finally` does not run (SIGKILL, power loss), `session.json` is never written and the envelope is already `incomplete_interior_support` (unreadable, `:1226-1229`). If `finally` runs, the post is taken. Either way a `session.json` lacking an authenticated `post` is `battery_float_evidence_missing` at `summarize` and `pilot_summary`, never a pass, and it is never retained (this is the scout's test 11 shape).

**Failure mode prevented.** Battery probes perturbing round alignment; a charging envelope being misfiled under `collect_error`; an interrupted envelope counting because only its pre read existed.

## Q4 — QPE-01's frozen exclusions

**Decision: (b), fail closed at the summary, list unchanged; queue (a) as a separate cold-gate registration (v4) for the next QPE night, since a per-envelope battery exclusion is the scientifically better rule.**

**Mechanics of (b).** `pilot_summary` authenticates each readable envelope's pair (Q2) before `all_rows.extend(rows)` (`:1223`). Any readable envelope whose status is not `pass` puts the whole summary into the existing **refused** outcome with reason `battery_float_confounded` or `battery_float_evidence_missing`, listing envelope indices, slot reasons and raw digests; no retained set, no pairs, no energy number is emitted; per-envelope `delta_q_mah` is reported as a diagnostic. `CustodyFailure` propagates as a refusal with the restore text. Unreadable envelopes (no `session.json`) are already excluded and carry no battery obligation, because they yield no number. `summarize` (the harness-side reducer) applies the same helper per session and raises on non-pass.

**Why this is not a silent change to a frozen protocol.** The registration's `exclusions` list governs which envelopes leave the retained set while the pilot's numbers are still produced; it is byte-pinned by `RULED_REGISTRATIONS` and the README says so. A summary-level refusal produces **no** pilot number at all; it does not touch the list, the retained set, the pairing rule or the digest. The code already draws this exact line for `recorder_kind` (E4: "the refusal is the SUMMARY's, not an exclusion reason; a new reason would force a registration v3"), so (b) reuses an existing, reviewed pattern rather than inventing one. The cost is honest: one confounded envelope refuses the night's claim, and the cure is another night, which is what the frozen text ("nothing is compressed, retried or topped up") already demands for any defect it does not enumerate. Option (c) fails directive #421 outright (a confounded number would be reported). Option (a) is right long-term but cannot land in this PR without a cold registration and a `RULED_REGISTRATIONS` change.

**Failure mode prevented.** A charging envelope's joules entering `retained`/`pairs` because the frozen list has no battery reason; or a battery reason being smuggled into a frozen list without a ruling.

## Q5 — Controller outcomes

**Sites.** Pre: `_run_lifecycle` between `self._stage_prepare()` and `self._stage_idle_baseline()` (`:869-870`). Post: between `self._stage_idle_drift_sentinel()` and `self._stage_cleanup()` (`:873-874`). Both through `battery_float.observe(phase=..., runner=self._battery_runner, session_id=self._writer.run_id, raw_path=...)`; the raw bytes go through `RunBundleWriter.write_raw` (bundle.py unchanged); records are held on the execution object and emitted as top-level `extra["battery_float"] = {"pre": ..., "post": ...}` in `_write_metadata` (`:2079`), never under `extra["extra"]`. `_battery_runner` is an injectable attribute defaulting to the real bounded probe (the same shape as `night_agent_install.BATTERY_PROBE_RUNNER`), so tests and battery-less CI hosts inject a fixture (BFG-D round-8 pattern).

**Failure after pre and before post.** In `_handle_failure`, after `_stop_sampling_best_effort` and before the `metadata` salvage step (`:1486`), take the post observation as its own salvage step (`_attempt_salvage_step("battery_post", ...)`), so a failed run that reached the pre also carries a post (possibly `probe_error`). Failure before the pre (validate/prepare): metadata carries `battery_float = {"pre": null, "post": null, "not_reached": "<stage>"}`. The failure summary written by `_failure_summary` keeps its real `status`/`failure_reason`; nothing about the battery changes the failure path's exit or return code.

**Non-Mac and mock targets.** Applicability is decided from the typed config, never from a metadata flag: the telemetry adapter the re-validated `BenchmarkConfig` names (`BundleReader.config()` re-validates it; its digest is `config_sha256`, part of run identity). `powermetrics` adapter → both phases mandatory and must pass. A non-Apple adapter (`nvidia_smi`) → the controller records `battery_float = {"applicability": "no_apple_smart_battery", "adapter": "<name>"}` and takes no observation; the reader accepts that form only when the config's adapter agrees. Mock adapters → same path as powermetrics (observe through the injectable runner); a mock bundle is never claim-bearing, and one code path is cheaper to prove than two.

**Must every finalized bundle carry a post read?** Every bundle that took a pre must carry a post record (above). Whether a bundle **reduces successfully** is decided by the reader (Q6): a claimed measured window needs an authenticated passing pair; a failed run reduces `FAILED` either way. I reject "post only when the window is claimed": whether a window is claimed is decided later and elsewhere, and the record must exist before that decision.

**Failure mode prevented.** A run that lost external power mid-measurement finalizing a bundle with a pre-pass only and later reducing clean; a Linux CI mock run being mistaken for an applicable Mac run or vice versa via a writable flag.

## Q6 — `BundleReader.metadata()` and historical bundles

**Decision: exempt a fixed historical set authenticated by whole-bundle digest; everything else is prospective.** Concretely, in `metadata()` before caching (`:275-278`): if `battery_float` is present, authenticate it via Q2 (`identity = {"session_id": raw["run_id"]}`, `phases = ("bundle_pre","bundle_post")`, custody root = the bundle path, reading raw files through `raw_artifact_bytes`); non-pass → `BundleReadError("battery_float <status>: <reasons>")`, `CustodyFailure` → `BundleReadError("battery_float custody failure: ...; restore the bundle bytes")`; the `no_apple_smart_battery` form is accepted only if `config()`'s adapter agrees. If `battery_float` is absent: compute `detection_floor.complete_bundle_sha256(path)` (cached per reader) and accept only if it is in a module constant `HISTORICAL_BUNDLE_SHA256: frozenset[str]` committed in `bundle_read.py`; otherwise `BundleReadError("battery_float missing: prospective bundle")`. `reduce_bundle` turns either into `FAILED/unknown_error` (`reduce.py:2652-2667`, byte-identical).

**The prospective boundary, exactly.** A bundle is historical iff its complete digest is a member of `HISTORICAL_BUNDLE_SHA256`. The set is populated in the code PR from the containers already pinned by committed registries (paper `results-fill-registry.md` members, floor-artefact source rows, the DG-071/075 `PINNED_BUNDLE_SHA256`), each entry carrying a comment naming its pin. It is authenticated by the same identity `mint_floor_artifact.py:399-404` already uses to bind a report row to its bundle bytes. Adding to the set is a reviewed code change, the same pattern as `DISPOSITION_REGISTRY_SHA256` (ex-02 §4.6). `FROZEN_LEGACY_BUNDLE_IDENTITIES` (a `(run_id, config_sha256)` pair) must **not** be reused as the boundary: both values are plain metadata fields, i.e. freely writable. `joulewise_version`, `git_commit` and `schema_version` are likewise writable and are not the boundary.

**Why not reject every historical re-reduction.** The paper's replay fences (`check_paper_replay_fence.py`, `paper_excursion_decomposition.py`) re-reduce pinned historical members; rejecting them breaks reproducibility of already-published numbers that were true when produced and gain nothing from a gate that did not exist then. Why not "version by provenance": every provenance field in the bundle is self-asserted; the only trusted provenance a bundle has is a digest pin outside it, which is exactly what the set encodes.

**Failure mode prevented.** A new bundle written by an old or patched controller (no key) reducing clean; a historical bundle being re-reduced with a fabricated `battery_float` block (it would then have to pass the pair authentication, and its complete digest would no longer match its pin).

## Q7 — `scored_reduce.reduce` evidence object

**Decision: a frozen, authenticated `battery_evidence` argument keyed by capture identity and bound to `bundle_sha256`, produced by one new producer.**

Producer: `scripts/scored_capture_evidence.py build --bundle <path> ...` (or a function `scored_capture_evidence.build(bundle_paths)`), which for each bundle computes `complete_bundle_sha256`, runs `BundleReader.metadata()` (which performs Q6's authentication), and emits `joulewise.scored_battery_evidence.v1`: `{"schema", "entries": [{"block_id", "attempt", "bundle_sha256", "status", "pre_raw_sha256", "post_raw_sha256", "delta_q_mah", "reasons"}], "sha256"}`. `block_id`/`attempt` come from the bundle's own metadata (the AXI `extra`/batch identity the scored packer already writes), never from the caller.

`reduce(registration, roster, predicted_decode_s, score_rows, capture_windows, battery_evidence)`: before `_check_window` runs on any window, validate the object's schema and self-digest, then build `by_key = {(block_id, attempt): entry}` refusing `battery_duplicate` on a repeated key. Then for every capture window: `battery_missing` if its key has no entry; `battery_binding` if `entry.bundle_sha256 != w["bundle_sha256"]`; for a **live** window, `battery_confounded` / `battery_evidence_missing` if `entry.status != "pass"`. Non-live windows (voided, terminal) keep their entry recorded under `uncounted_windows` with the status; they never contribute energy to a cell. Add the five codes to `REDUCTION_CODES`. Entries without a matching window are `battery_unbound` (refuse: evidence for a window that was not supplied).

**Reason.** The reducer is sealed and pure over caller-supplied dictionaries; it has no bundle path and must not grow one (it would then read files and stop being a pure function of its arguments). The only thing it can authenticate is agreement between two independently produced records on a shared digest, so the evidence object carries `bundle_sha256` and the reducer binds on it. Duplicate and missing refusals mirror the existing `window_duplicate`/`missing_live_window` shape.

**Failure mode prevented.** Scores contributing from a live window whose bundle was charging; evidence for bundle A being presented for window B.

## Q8 — `calibration_bracketing` gate placement

**Decision: gate at the loader before physics, and carry a proof into the evaluator, which refuses unproven prospective candidates.**

Loader (`_load_calibration_candidate_unbounded`), immediately after the `artifact_sha256` events/plist checks and before `verify_stored_evidence_physics` (`:1631-1634`): if `evidence` has `battery_float`, run `authenticate_pair(evidence["battery_float"], directory, phases=("slot_pre","slot_post"), identity={"attempt_id": ...})` (the writer's records; identity binds `attempt_id`/`session_id` as the writer stored them); non-pass → return `None` (the loader's uniform refusal), and record a diagnostics row where the caller plumbs one. Put the result on a new `CalibrationCandidate` field `battery_float_proof: PairVerdict | None = None` that is **excluded from `descriptor()`** so no recorded reducer boundary moves.

**Historical/genesis boundary.** Decided by the ledger, not by key presence: a constant `BATTERY_FLOAT_LEDGER_BOUNDARY = {"sequence": S0, "head_digest": "<64 hex>"}` in `calibration_bracketing.py`, where `S0` is the ledger head sequence at the BFG-D merge (`64e39bb9`). A candidate whose `LedgerObservation.sequence ≤ S0` (genesis imports and every historical ordinary capture, including `is_historical_import` rows) is exempt; `sequence > S0` requires a `pass` proof. The chain digest at `S0` is authenticated by the ledger's existing head-pin check, so the boundary cannot be moved by editing a capture.

Evaluator (`evaluate_calibration_bracket`, at entry `:1982`): with a `ledger_snapshot`, look up each candidate's observation by `attempt_id`; if `sequence > S0` and `battery_float_proof` is `None` or not `pass`, the candidate is unselectable and the result gains reason `calibration_candidate_battery_unauthenticated`. Without a snapshot (synthetic callers) no candidate is claim-bearing today; refuse any candidate lacking a `pass` proof unless `_allow_unissued_fixture` (fixtures only). NOT EXECUTED: I did not trace the no-snapshot branch past `:2031`.

**Reason.** The loader is where `b_fiducial_s` first becomes a number the physics fit reads; refusing there keeps the B lexeme unread for a confounded capture (the same "before physics" rule as the controller attachment). The evaluator check is the belt for directly supplied candidates, which already carry `b_fiducial_s`, so it cannot substitute for the loader.

**Failure mode prevented.** A charging bracket endpoint bounding a transaction window; a genesis or historical endpoint being refused for lacking a record that could not have existed.

## Q9 — Transaction packs

**Decision: "re-freeze" means successor generations; never edit the nine.**

- **Retire without successor:** the six `_v1` and `_v2` packs. Each is already superseded by its `_v3` sibling in the same freeze chain (`freeze-0001` → `-0002` → `-0003`, E3); their pinned sources no longer match main, so arm readiness refuses them by construction. Their bytes and receipts stay as history.
- **Successor:** the three `_v3` packs → `d117_floor_qwen25_1p5b_v4`, `d117_floor_qwen25_7b_v4`, `d117_contrast_qwen25_1p5b_vs_7b_v4`, each with `--predecessor-pack-root` = its `_v3` sibling, minting `freeze-0004.json`.
- **Authoring order** (each: regenerate from the merged BFG-S code head → commit the pack tree → `author_arm_readiness_evidence.py` → commit sources/evidence → `generate_arm_readiness.py freeze` → verify plan-tree pins): (1) `d117_floor_qwen25_1p5b_v4` (W1's family; its `calibration_plan.json` must be **byte-identical** to `_v3`'s `9ab4776f…` because the W1 notice pins that plan, so the derivation epoch and the transaction pack must agree on one plan; assert it in the pack PR), (2) `d117_floor_qwen25_7b_v4`, (3) the contrast `_v4`.
- **The three `_v5` packs** (`d117_contrast_v5`, `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`) need their first authoring, but the runbook's successor rule (`_v<N>` must pass the `_v<N-1>` sibling beside it, `window_runbook.md:302-311`) has no `_v4` sibling for any of them. Either they are first-generation packs under a different name or the rule needs a ruling; I flag it, I do not resolve it here (NOT EXECUTED).

**Reason.** Receipts and plan-tree pins are no-clobber; editing committed source JSON moves the pack digest and contradicts the custody rule the runbook states. Authoring a `_v4` gets a new pack digest and a reviewed receipt, exactly the D-139 predecessor chain.

**Failure mode prevented.** A frozen receipt vouching for source bytes that were replaced underneath it.

## Q10 — Wall-meter windows

**Decision: the separate wall-meter bar (WALL-METER-GAIN-01) remains; float is necessary, not sufficient.**

**Reason, with the number.** The predicate admits |InstantAmperage| ≤ 200 mA at ≈12.9 V (E1 of ex-01: `Voltage = 12912`), i.e. up to ≈2.6 W flowing into or out of the pack while passing. Over a 480 s interior that is ≈1.2 kJ; over a 600 s envelope ≈1.5 kJ, against a ≈5 J claim bar. For powermetrics windows this is irrelevant (the rails are measured on the SoC side of the pack). For a wall meter, wall = SoC + charger losses ± battery, so the gate bounds nothing the wall number depends on. A-R5b v1.1's Disclosure already says this and makes it registered text; BFG-S changes nothing there. ΔQ is recorded per window as a diagnostic only, for the F-5 reason (the gauge re-syncs in steps).

**Failure mode prevented.** A wall-meter number being called claim-bearing because the battery gate passed.

## Q11 — PR split

**Decision: the scout's three-stage split is right, with one refinement: split the code PR in two along the pack-pin boundary.**

- **PR-A (no frozen pin moves):** `scripts/sample_quiet_predicate_evidence.py` brackets and `summarize`; `quiet_predicate_campaign.pilot_summary` refusal; the `authenticate_pair` helper; sweep and guard updates; `scored_reduce` (no production caller, no pin). After PR-A, QPE-01 nights (`DIAGNOSTIC_NO_PACK`, no `arm_readiness`) may arm again.
- **PR-B (moves `controller.py`, `bundle_read.py`, `calibration_bracketing.py` pins):** controller brackets and metadata, `BundleReader.metadata()` with the historical digest set, bracketing loader/evaluator with the ledger boundary, F-1 closure and its test change, new `tests/test_bfgs_calibration_bracketing.py` (never `tests/test_calibration_bracketing.py`, pinned). `reduce.py`, `bundle.py`, the four estimator paths and paper scripts byte-identical, asserted by the pin-regression test.
- **PR-C:** successor packs (Q9), authored from PR-B's merge head.
- **PR-D (later):** the indivisible ex-02 §4.11 amendment after the Revision 5 epoch issues or stops.

**Reason.** PR-A unblocks quiet-predicate windows weeks before the pack chain is done, at no cost in review coverage; PR-B is the one that forces PR-C. Merging A and B together buys nothing and delays QPE. No transaction-pack window arms between PR-B and PR-C (PR-B's body must say so, as BFG-D's did).

**Failure mode prevented.** Quiet windows held hostage to pack authoring; a transaction window arming against packs whose pins name pre-BFG-S bytes.

## Q12 — What the scout missed that bears on whether a number is true

1. **The 200 mA × 12.9 V ≈ 2.6 W arithmetic** (Q10) belongs in the BFG-S packet as the stated reason the wall-meter bar survives; the scout recorded the conclusion without the number.
2. **`_v4` plan byte-identity.** The W1 notice pins `d117_floor_qwen25_1p5b_v3/calibration_plan.json` (`9ab4776f…`). If the `_v4` generator emits a different plan, the derivation epoch's plan and the transaction pack's plan diverge silently. Assert byte-identity in PR-C.
3. **`_v5` predecessor rule** (Q9): the three `_v5` packs cannot freeze under the current rule without a ruling or a rename.
4. **Collector rows re-digest the battery raw files** (Q3): an unplanned but beneficial side effect of `p.parent == raw`; make it intentional and tested, or it will surprise a reviewer as a row-schema drift.
5. **Controller self-reduction.** `_stage_reduce` reduces the bundle it just wrote through `BundleReader`; with Q6 a run whose post read fails reduces `FAILED/unknown_error` with the battery reason in `failure_message`. That is correct, but every existing controller test that runs to `reduce` on a battery-less host now needs the injected runner (the BFG-D round-8 hermeticity work, again, larger this time). Budget it.
6. **Staleness sign.** Until PR-D, a future `UpdateTime` passes at every non-derivation site too (`update_age_s > 180` one-sided, `battery_float.py:249-253`). `observe` stamps wall time before the probe runs, so a negative age is clock skew, not a real reading; it is the ruled sequencing and I do not reopen it, but PR-A/B's tests should pin the current one-sided behaviour so PR-D's change is visibly RED.
7. **Scored roster decisions made before reduction.** `_classify` reads `terminal_refusals` (e.g. `ceiling_violation`) that the packer decided from a window's `gross_j` at execution time; a confounded window could have produced a ceiling violation that voided a block before any battery check. The reducer cannot undo that. The packer's ceiling decision should consult the same pair verdict, or the registration should say a ceiling violation on a confounded window is `voided`, not `terminal`. Out of this PR's scope; needs a ruling before the scored campaign arms.
8. **Identity of the bundle record.** `battery_float.session_id` = `run_id` (Q1) is a plain string in the same file; the binding is against `metadata.json.run_id`, which is what `reduce` already trusts for identity. The only stronger binding available is the registry digest pin (Q6), which is why the historical set is keyed by whole-bundle digest and not by identity fields.

---

## Decision table

| Q | Decision | Confidence |
|---|---|---|
| Q1 | Explicit phases `quiet_pre/post`, `bundle_pre/post`; v1 field set unchanged; `session_id` = collector uuid / bundle `run_id` | high |
| Q2 | `battery_float.authenticate_pair(record, custody_root, phases, identity)`; raw-digest mismatch = `CustodyFailure`; no committed verdict file; one allowlist row | high |
| Q3 | Envelope pair only (pre before `:1066`, post in `finally` after `:1164`); failing pre recorded and collection continues; missing post = evidence missing, never retained | high |
| Q4 | (b) summary-level refusal on any readable non-pass envelope, list unchanged; queue (a) v4 via cold gate | high on (b); med on timing of (a) |
| Q5 | Pre `:869/870`, post `:873/874`; post taken as a failure-path salvage step; applicability from the typed config's telemetry adapter; every pre-bearing bundle carries a post | high |
| Q6 | Fixed historical set keyed by `complete_bundle_sha256` in a committed constant; all else prospective and fail-closed | med (set population is work; the boundary itself is sound) |
| Q7 | Frozen `joulewise.scored_battery_evidence.v1` keyed `(block_id, attempt)` and bound to `bundle_sha256`; five new refusal codes | med (no production caller exists to test against) |
| Q8 | Loader before physics + proof field outside `descriptor()`; evaluator refuses unproven candidates with ledger `sequence > S0` | med (no-snapshot branch not traced) |
| Q9 | `_v1/_v2` retired, `_v3` → `_v4` successors, order 1p5b → 7b → contrast; `_v5` naming needs a ruling | high on the nine; low on `_v5` |
| Q10 | Wall-meter bar remains; float bounds ≈2.6 W, ≈1.2 kJ per interior | high |
| Q11 | Four PRs: A (quiet path, no pins) → B (bundle path, moves pins) → C (packs) → D (§4.11) | med |
| Q12 | Eight items above; items 2, 3, 7 need decisions before the affected windows arm | — |
