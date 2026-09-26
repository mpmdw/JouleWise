# Cold gate BFGS-DESIGN-01: paired Opus contract refuter

Refuter: Claude Opus 5.5 (`claude-opus-5-5`). One non-interactive foreground session, with no subagents and no background tasks. Worktree `JouleWise-wt-bfgs-cgref-6bec2aa6` at `55cd733d`. `git diff --stat 64e39bb9 HEAD -- joulewise scripts configs tests` is empty, so the code is the scout's code. Session 2026-09-26. This file is the only thing written.

## 0. Contamination disclosure

- **Loaded by the harness, not chosen by me:**
  - the global `~/.claude/CLAUDE.md`;
  - the project `CLAUDE.md`;
  - the auto-memory index `MEMORY.md`, which is one-line pointers, including loop-context titles such as "Verity-germane = mandatory (#421)" and "Checkpoint 2026-09-26 activation ed17a643";
  - a git-status reminder listing five commit subjects.

  I opened no memory file and none of `RUN_STATE.md`, `TASK_QUEUE.md`, `AGENTS.md` or the decision log. I cite none of that material as authority.
- **Read:**
  - both charges (`00-charge.md` and `01-refuter-charge.md` in `50-coldgate/`);
  - the synthesis `20-magistrate-synthesis.md`;
  - the consult charge `40-bfgs-consult/00-charge.md`;
  - the scout report;
  - ex-01 through ex-04 in full.
- **Not read:** the four seat reports (Sol, Astra, Opus, Fable), except as the synthesis quotes them.
- **Live commands:** five `ioreg -r -c AppleSmartBattery` reads, used only to time the probe (≈0.01 s each). No `sudo`, `launchctl`, `powermetrics`, installer or model inference.

## 1. Executed evidence (verbatim, condensed)

```
P1  arm_readiness.py:79-85  _RULED_V5_PREDECESSOR_PACK_IDS = {
      "d117_floor_qwen3-1p7b_v5": "d117_floor_qwen25_1p5b_v3",
      "d117_floor_qwen3-8b_v5": "d117_floor_qwen25_7b_v3",
      "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5": "d117_contrast_qwen25_1p5b_vs_7b_v3" }
    arm_readiness.py:7856 freeze refuses a _v5 whose predecessor name differs; author script :76 consumes the map.
    ls configs/campaigns | grep d117 -> the contrast _v5 PACK dir does not exist yet; d117_contrast_v5/generate_configs.py:1095
      pack_id = f"d117_contrast_{MODEL_IDS['A']}_vs_{MODEL_IDS['B']}_v5"          => D9 code claim CONFIRMED
P2  controller.py:439-447: `if isinstance(evidence, dict) and ("battery_float" in evidence or any(... REVISION_FIVE_EPOCH ...))`
    => F-1 site CONFIRMED (key arm at :440)
P3  controller.py:869 _stage_prepare, :870 _stage_idle_baseline, :873 _stage_idle_drift_sentinel, :874 _stage_cleanup,
    :878 _capture_post_run_environment_observation, :879 _stage_reduce -> :1447 _write_metadata then :1453 reducer
    => D5 sites CONFIRMED; the post read precedes the metadata write and the in-process reduce
P4  scripts/sample_quiet_predicate_evidence.py:
    1066 envelope_cpu_start = cpu_total() | 1067 start = clock.stamp() | 1074 if provenance is None:
    1081 write_json(out / "session.json", session) | 1083 return session, [] | 1084 write_json(out / "session.json", session)
    1163 session["end_stamp"] = ... | 1164 whole_envelope_observer_cpu_s | 1208 final write_json
    => D3's ":1087" first write is WRONG (first writes are :1081 and :1084), and the :1074-1083 early return bypasses the finally
P5  quiet_predicate_campaign.py pilot_summary comment (read at ~:1203-1213): "`power: null` ... is an envelope that refused
    before any recorder existed -- the network-time provenance refusal path ... Refusing a whole REAL night ... because one
    envelope refused early is a false record, and it was reachable (lane contract lens 17a S1)."
P6  shasum pilot_protocol_v3.json = 69321c693b33...d2c813616 (matches the synthesis). Its exclusions include "collect_error"
    and "start_drift"; "start_drift_abort_s": 2, "start_drift_max_s": 10, "slot_pitch_s": 620, "envelope_s": 600.
    chain_source_sha256 568a2771... = shasum of scripts/night_chains/quiet_predicate_evidence.zsh (probed over every tracked file);
    night_gate.py:7-11 "A ruled registration ... pins no Python"  => S2 moves no registered digest (CONFIRMED)
P7  ioreg -r -c AppleSmartBattery, 5 timed runs: real 0.01 s each; battery_float.PROBE_TIMEOUT_S = 10
P8  quiet_predicate_campaign.py:1552 in-chain abort: `if index >= 2 and drift > protocol["start_drift_abort_s"]: ... raise
    ValueError("start_drift_abort: ...")` -- the executor ends the night REFUSED before a capture and books no exclusion
P9  metadata.json readers outside BundleReader.metadata(): analysis_engine/inputs.py:845, analysis_engine/registry.py:542,955,
    analysis_manifest_v3.py:3222,3351, arm_readiness.py:11472, controller.py:3126,3181,3276, floor_extraction.py:1853,1925,
    output_identity.py:157, publication_privacy.py:433,1080, salvage_dangler.py:706,853, bundle_read.py:411 (raw_metadata)
P10 BundleReader energy accessors that never call metadata(): summed_curve/source_curve/trace_rows/measured_window.
    window_duration_margins.py:607 `curve = reader.summed_curve()` (docstring: "Every numeric conclusion is re-derived from
    authenticated collection bytes; summary_metrics.json is used only to cross-check"); whole_window.py:4229 and
    floor_extraction.py:1870 `BundleReader(path).measured_window()`
P11 summary_metrics.json readers (run-time summaries, no metadata() call): aggregate.py, mint_floor_artifact.py,
    extract_detection_floors.py, run_campaign.py, make_figures.py, analyze_phase_share.py, check_window_provenance.py,
    summarize_g2a_prefill_probe.py, paper_prefill_resolvability_projection.py, ... (29 files)
    aggregate.py:122 "members_failed": count of failed; :188 `if record.get("status") != "succeeded"` -> dropped from points
P12 whole_window.py:3100 validated_attempt_selection: the attempt ledger selects which attempt of a block is consumed
P13 scored_reduce: `grep -rn scored_reduce joulewise scripts` (excluding itself) -> empty (no production caller).
    _classify :72-88 keys = roster placements, kind in {live, terminal, voided}; _check_window :109 refuses status "not_started";
    :296 `gross = window_by_key[key]["gross_j"] if t["type"] == "ceiling_violation" and key in window_by_key else None`
    -> a terminal refusal's window may be ABSENT from capture_windows
P14 calibration_bracketing.py:1811 discover_calibration_candidates: loops over EVERY valid, non-import, non-derivation ledger
    observation; :1853 `candidate = _candidate_from_observation(...)`; :1854 `if candidate is None: return ()`;
    comment :1840-1846 "must stay symmetric with the `registered_valid` universe ... anti-withholding equality";
    :2189-2220 `if supplied_valid != registered_valid or len(candidates) != len(supplied_valid)` -> refusal
P15 CalibrationCandidate :607-627 carries relative_path, manifest_sha256, evidence_sha256, content_id, optional bracket_runs_root;
    it carries no complete_bundle_sha256
P16 detection_floor.py:558 complete_bundle_sha256 hashes EVERY regular file under the bundle root (summary_metrics.json included)
P17 tests/test_battery_float_consumers.py:185 `def test_the_allowlist_has_exactly_six_rows: assertEqual(len(ALLOWLIST), 6)`;
    GUARDED includes `parse` (:25)
P18 evidence_night.py:1387-1404 reads `row.corecaptured_at_arm_and_t0` and `row.non_observer_at_arm_and_t0` by name;
    NIGHT_KINDS has exactly two rows (quiet_predicate_evidence :49, calibration :71); `row is None` for any other payload kind
P19 observe() phase values in live BFG-D callers: t0 (night_gate:1522), arm_check (evidence_night:1370), publish_install (:1793),
    validate_install (night_agent_install:1222), t0_power_row (arm_readiness_evidence_t0:1883), slot_pre/slot_post
    (validate_powermetrics_fiducial.py:2177 `phase=f"slot_{phase}"`)
P20 render_results_fills.py imports: argparse, decimal, fractions, importlib.util, json, re, sys, pathlib, typing -- no joulewise
P21 publication_privacy.py:99 _METADATA_KEYS frozenset; :434 _unknown_keys(set(value), _METADATA_KEYS, "metadata.json");
    :267-279 fixed raw-file allowlist (raw/powermetrics.plist, ... ) with no raw/battery_float.*
P22 Pins on proposed write scopes (count of arm_readiness.sources files naming the path):
    controller 18, bundle_read 42, calibration_bracketing 51, whole_window 24, floor_extraction 33, analysis_engine/inputs 24,
    publication_privacy 24, aggregate 24; battery_float, scored_reduce, quiet_predicate_campaign, sample_quiet_predicate_evidence,
    night_kinds, evidence_night, and every tests/ module R2 names: 0.
    Current-byte digests of all 13 scope files: `git grep` outside arm_readiness.sources and process_traces -> none.
    ESTIMATOR_CODE_PATHS (calibration_bracketing.py:206) = powermetrics_fiducial, uncertainty_evidence, adapters/powermetrics,
    reduce -- none in scope. Pinned tests: test_calibration_bracketing.py (9), test_mint_floor_artifact*.py, test_calibration_ledger.py ...
P23 docs/paper/results-fill-registry.md:366-367,774 cite whole_window.py:199/200, floor_extraction.py:190/191,
    calibration_bracketing.py:207 by LINE (not digest); no test checks those line numbers
```

NOT EXECUTED:
- any unit test;
- any authoring or freeze of the `_v5` packs;
- a count of the valid non-derivation rows in the live calibration ledger (P14's consequence is argued from the code, not counted);
- whether S3's authored `arm_readiness.sources` will pin `joulewise/battery_float.py` (see M11).

## 2. Findings

Each finding gives its tier, the evidence, and the exact text change that closes it. There are no BLOCKERs against the principle. Two findings (M1 and M2) are BLOCKERs against the synthesis text as a seat brief, because as written the text either books a false record or cannot be implemented without a choice that changes numbers.

### M1: BLOCKER (text). D3/D4: the QPE provenance-refusal return books a battery "evidence_missing" that refuses the whole pilot on a non-battery reason

**Evidence (P4, P5).**
- At :1074–1083, `collect` returns early on network-time refusal. That return comes after the proposed pre read and before the `try`/`finally` that holds the post read.
- Such an envelope carries `pre` only. `authenticate_quiet_session` therefore yields `evidence_missing`, and D4 then refuses the whole pilot.
- This is exactly the false record the code already forbids in `pilot_summary` for this path (lens 17a S1), and it is the same kind of false record D3a uses to argue against a new collector exit.
- D3's citation of the "first `session.json` write (:1087)" is also wrong: the first writes are at :1081 and :1084.

**Closing text (replaces D3's second and third bullets).**

> The **pre** read sits in `collect` after `session` is built (`:1065`) and before `envelope_cpu_start = cpu_total()` (`:1066`). It is stored in `session["battery_float"]["pre"]` before either `session.json` write (`:1081` on the network-time refusal path, `:1084` otherwise). Every return from `collect` after the pre read attempts a post read before its last `session.json` write:
> - on the network-time refusal path, after `session["error_class"] = NETWORK_TIME_REFUSAL` and before `:1081`;
> - on the capture path, in the existing `finally`, after `:1163–1164` and before `:1208`.
>
> Test: an envelope refused for network time carries both reads, and a clean pair on it does not refuse the pilot.

### M2: BLOCKER (text). D8 cannot be implemented without a choice that either bricks every future bracket or withholds endpoints

**Evidence (P14, P15).**
- `discover_calibration_candidates` loads **every** valid ordinary ledger observation, and the evaluator refuses unless the supplied set equals the `registered_valid` universe (anti-withholding).
- D8 says the loader authenticates battery evidence "before physics", but does not say what a non-pass capture does. That leaves three options, and all three are wrong:
  1. **Raise.** One confounded ordinary capture anywhere in the ledger then refuses discovery for every future claim window, permanently.
  2. **Return `None`.** `:1854` then empties the whole enumeration, with the same effect.
  3. **Skip.** This breaks the equality, or, if the equality is edited to match, becomes an endpoint exclusion. An endpoint exclusion changes which bracket (and so which b bound) a window gets, and D8 never stated that it is decided from instrument state alone.
- D8's historical boundary ("the same content-pinned set as D6") is keyed by `complete_bundle_sha256`. That is a bundle digest; a `CalibrationCandidate` has no such field (P15). As written, the set cannot exempt one capture.

**Closing text (replaces D8).**

> **D8.** In `discover_calibration_candidates`, before `_candidate_from_observation`, each valid ordinary observation is classified by `battery_float.authenticate_capture(observation)`. The classification is computed from ledger-authenticated `instrument_evidence.json` (its digest is in the ledger row) and from the raw bytes whose digests that evidence records.
> - **`custody_failure`:** raises, which refuses the claim window.
> - **`pass`:** the observation is loaded as today.
> - **`confounded` or `evidence_missing`:** the observation is excluded from **both** the candidate list and the `registered_valid` universe (`:2189`) by the same predicate. It is excluded before its `b_fiducial_s` is read, and is listed in the bracket result under `battery_excluded_endpoints` with its verdict and raw digests.
> - **`predates_battery_float` (historical):** the observation's evidence authenticates against its ledger row and lacks the `battery_float` key, and its ledger sequence is at or below the committed head-pin sequence at the BFG-S merge commit (a constant). It is loaded, and marked `battery=unobserved_historical`. No bundle digest set is used for captures.
>
> `evaluate_calibration_bracket` re-runs the same classification from bytes for every supplied candidate (resolved through `bracket_runs_root`; a candidate without a resolvable root refuses). It refuses on any disagreement with the loader's classification.
>
> Tests:
> - (a) a confounded ordinary capture in the ledger leaves discovery for other windows unchanged, and the equality holds;
> - (b) a raw file deleted after finalization refuses;
> - (c) a post-BFG-D capture with the key removed from its evidence fails ledger authentication (custody), never "historical".

**Why the exclusion is admissible.** It is the ex-01 A-R5b reasoning: a verdict decided from instrument state alone, before any B is read, cannot select on outcome.

### M3: MATERIAL. D5 and D6 contradict each other on MOCK, and D6 has no `not_applicable`

D5 makes MOCK `not_applicable`. D6 says "every other bundle must carry an authenticated `pass` pair, or `BundleReader.metadata()` raises". Taken literally, every MOCK bundle then reduces `FAILED/unknown_error` (P3: the controller's success path reduces through `metadata()`), and hermetic controller tests break wholesale.

**Closing text (appended to D6).**

> `BundleReader.metadata()` admits exactly three states:
> - an authenticated `pass` pair;
> - a bundle in the historical set;
> - `not_applicable`, decided only from the `config.json` whose digest `metadata.config_sha256` binds, and only when `hardware_target.telemetry_backend == "mock"`.
>
> A `not_applicable` bundle is never claim-bearing. Every claim-set builder (obligation 2) refuses it.
>
> Applicability for a real backend is keyed on the hardware target, not the telemetry adapter. A Mac target (including `wall_meter` on a Mac) is bracketed. Any other target is `evidence_missing` until a platform predicate is registered. This blocks NVIDIA and Jetson claim work until then, which is recorded as a known consequence.

### M4: MATERIAL. D6's historical set has no enumeration rule, and obligation 8's visibility claim is false for the paper path

**Evidence.**
- "Closed at the BFG-S merge" does not say **which** bundles enter the set.
- Hashing whatever bundle directories exist on disk at merge would admit every bundle captured, battery unobserved, between now and the merge. That is the population obligation 8 says is untrustworthy.
- Obligation 8 says "D6 makes `unobserved_historical` visible in every window-level output". It does not: the paper renderer imports nothing from `joulewise` (P20), and the claim artifacts it renders are committed files that never pass through `metadata()`.

**Closing text.**

> **D6 set enumeration.** The set is exactly the `complete_bundle_sha256` values already present in committed claim artifacts at the BFG-S merge base: detection-floor artifacts, analysis manifests, and window receipts. The set is extracted by a committed script whose output file and digest land in S1. A bundle that is not cited by a committed artifact at the merge base is not historical.
>
> **Obligation 8, last bullet, replaced by:** HISTORICAL-BATTERY-STATE-01 adds a `battery_state` column (`unobserved (pre-directive)` | `evidence of charging` | `evidence of float`) to every claim row of `docs/paper/results-fill-registry.md` and to its renderer's input. The renderer refuses to render a claim row whose column is empty. D6 does not provide this disclosure.

### M5: MATERIAL. Obligations 2 and 3 name too few consumers, and name them by the wrong key

**Evidence (P9–P12).**

(a) **Bundles dropped from the claim set.** For new bundles, the gate sits at the producer: the charging bundle's run-time `summary_metrics.json` is `FAILED`. The danger is therefore not a bypass but a silent drop:
- `aggregate.py` counts failed members and aggregates the succeeded ones (P11);
- `mint_floor_artifact.py`, `extract_detection_floors.py` and `run_campaign.py` read summaries in the same way;
- `validated_attempt_selection` (P12) consumes a selected attempt, so a superseded attempt that was charging is never looked at.

(b) **Energy accessors that bypass the gate.** `window_duration_margins.py:607` re-derives energy with `reader.summed_curve()`, and never calls `metadata()` (P10). The same risk applies to any consumer using `measured_window()`, `source_curve()` or `trace_rows()`.

A sweep keyed on "direct `metadata.json` readers" misses both routes.

**Closing text (replaces obligations 2 and 3).**

> **2.** Every consumer that builds a set of bundles whose numbers are claimed calls `battery_float.authenticate_window_members(members)` before reading any energy, and refuses the whole set on any non-pass, `not_applicable` or custody failure. This covers:
> - `whole_window`;
> - `analysis_engine.inputs`;
> - `floor_extraction`;
> - `aggregate.aggregate`;
> - `scripts/mint_floor_artifact.py`;
> - `scripts/extract_detection_floors.py`;
> - `window_duration_margins`;
> - `run_campaign`'s final analysis.
>
> Here `members` = every finalized bundle of the window, including `FAILED` bundles **and every attempt the attempt ledger records, selected or superseded**.
>
> **3.** An AST sweep (the CONSUMER-DRIFT seam, ex-04) walks `joulewise/` and `scripts/`. It flags any production use of:
> - `BundleReader.summed_curve`, `source_curve`, `trace_rows`, `measured_window`, `raw_artifact_bytes` or `raw_metadata`;
> - any read of `summary_metrics.json`, `metadata.json` or `power_trace.csv`;
>
> in a function that does not first call the seam. Each exemption goes in a named allowlist with a reason (for example, `publication_privacy`, `salvage_dangler`, `cli` strict-validation and report paths that emit no claim). Its self-test reports `window_duration_margins.py:607` at `55cd733d`.

Pin consequence: `aggregate.py` (24 pins) and `window_duration_margins.py` (0) join S1's scope. Both move only retired-pack readiness pins.

### M6: MATERIAL. D7's coverage set is keyed on the wrong universe; fixing it removes obligation 5's truth content

**Evidence (P13).** The reducer's keys are roster placements, of kind `live`, `terminal` or `voided`. A terminal ceiling refusal's window can be absent from `capture_windows` (`:296`), so "bound to every capture window" does not reach the one window obligation 5 worries about.

**Closing text (D7, replacing the coverage sentence).**

> The evidence's key set must equal `{key for key, (_, _, status) in _classify(roster).items() if status != "not_started"}`, which spans live, terminal and voided placements, whether or not a capture window is supplied. Missing, extra, duplicate, unbound (`complete_bundle_sha256` ≠ the window's `bundle_sha256` where a window exists) or non-pass entries raise `ReductionRefusal` before `_check_window`.

**R3 consequence.** With this text, a ceiling decision taken from a confounded window makes the whole reduction refuse, so no number is untrue. Obligation 5 becomes a campaign-cost question only. It is correctly a separate lane, and it blocks nothing about truth. Also change "see D12.4" to "see obligation 4".

### M7: MATERIAL. D2's helper needs a seventh guard-allowlist row, which amends ruled text (ex-04 §3.10)

`authenticate_pair` must call the guarded `parse`. ex-04 §3.10 fixes the allowlist at "exactly six" rows, and a test asserts it (P17). The synthesis is silent, so an implementer either breaks the test or re-implements `parse`, which ex-01 §5.1 forbids ("nothing re-implements them").

**Closing text (added to D2).**

> This amends ex-04 §3.10. It adds exactly one allowlist row, `joulewise/battery_float.py::authenticate_pair → parse`, and changes the six-row assertion to seven. It adds a guard self-test that a `parse` call from any other new function in `battery_float.py` is flagged. The three wrappers call `authenticate_pair` only.

### M8: MATERIAL. The D11 arm fence cannot be built within the proposed scope, and its polarity is unstated

**Evidence (P18).** `evidence_night.check` reads NightKind flags by name. A new `battery_brackets` field does nothing until `evidence_night.py` reads it, and R2 does not list `evidence_night.py`. For a payload kind absent from `NIGHT_KINDS`, `row is None`, and the synthesis does not say whether the fence then passes or fails.

**Closing text (D11 fence).**

> S0/S1 scope adds `joulewise/evidence_night.py` (0 pins) and `tests/test_evidence_night.py`. In `check`, after `inspect("battery_float", …)`, the new check is `inspect("battery_brackets", …)`. It fails unless `row is not None and row.battery_brackets is True`. It has no `skipped` state and is not added to the `("machine_quiet", "corecaptured")` exemption. Values: `calibration=True`, `quiet_predicate_evidence=False` until S2 flips it. Tests: a QPE candidate is not armable; the derivation kind is unchanged; an unknown payload kind is not armable.

### M9: MATERIAL. D2 freezes derivation functions but leaves `observe`, which D1 edits and which the derivation writer runs mid-epoch

**Evidence (P19).** The writer calls `battery_float.observe` on every W2/W3 slot. D1 adds phase validation inside `observe`, and D2's byte/AST pin omits `observe` and `require_pass`. A validation defect would turn clean derivation slots into `evidence_missing` inside the Revision 5 epoch. That is D2's own stranding risk, reached through a different function.

**Closing text (D1/D2).**

> `observe` and `require_pass` join D2's byte-pinned set. The four new phases are validated in the new wrappers, which pass `phase` through to an unchanged `observe`. A test calls `observe` with each of the seven existing phases and asserts byte-identical records against a pre-S1 golden.

D1 also extends the enumeration of the ruled v1 schema (ex-01 §5.4) without a version bump. Record that extension in the D1 text as an amendment of ex-01 §5.4.

### M10: MATERIAL (plausible, needs one check at S3). S3 before S4 may strand the `_v5` freeze

The d117 readiness sources pin about 180 distinct paths per pack, including controller-adjacent modules (P22). After S1, `controller.py` and `bundle_read.py` import `battery_float`. If S3's authored `_v5` sources pin `joulewise/battery_float.py`, then S4 (the ex-02 §4.11 predicate change to `battery_float.parse`) moves a `_v5` frozen pin. That would force a `_v6` generation, which `_RULED_V5_PREDECESSOR_PACK_IDS` does not map.

**Closing text (D11, S3 bullet).**

> Before committing `_v5` sources, the S3 seat greps them for `joulewise/battery_float.py` and `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. If either is pinned, S3 stops and the magistrate chooses one of two ruled paths:
> - (a) freeze `_v5` after S4;
> - (b) accept a `_v6` generation after S4, with its predecessor map ruled then.

### M11: MATERIAL (scope completeness; fail-closed, not a truth hole). Publication privacy rejects every new bundle

`publication_privacy.py` has a fixed metadata-key allowlist and a fixed raw-file allowlist (P21). Neither admits `battery_float` or `raw/battery_float.{pre,post}.ioreg`, so every BFG-S bundle fails its publication audit.

**Closing text.** S1 scope adds `joulewise/publication_privacy.py` (24 retired-pack pins). It adds `battery_float` to `_METADATA_KEYS`, with the record's fields classified, and adds the two raw paths to the raw allowlist, each with its privacy class. Alternatively, the gate rules the breakage deliberate until a later PR.

### NITs

- **N1 (D3a reasoning).**
  - ex-01 §5.3 item 6 is scoped to the derivation writer, and its reason is writer-specific ("rc ≥ 2 would leave the session OPEN for desk recovery"). Applying it to the collector is an analogy, not a ruled rule.
  - The "a new exit is booked under `collect_error`" argument ignores the executor precedent (P8): `start_drift_abort` ends the night REFUSED before capture and books no exclusion.
  - Both D3a options are truth-safe because D4 refuses the pilot. I do not contest record-and-continue.

  Replace "states the ruled writer rule" with "is the ruled rule for the derivation writer; the collector follows it by analogy", and delete the `collect_error` sentence.
- **N2 (timing).** The pre read runs between the scheduled instant and `start` (`:1067`), so its latency counts toward `session.start_drift_s`, which feeds the frozen `start_drift` exclusion (10 s bar). A post read that hits the 10 s timeout also consumes half of the 20 s slot gap, which feeds the next envelope's 2 s `start_drift_abort`. Typical cost is 0.01 s (P7). A timeout implies `evidence_missing`, and the pilot refuses anyway, so there is no truth effect. Test obligation: record `monotonic_before_ns`/`after_ns` of both reads, and assert that a 0 s and a 2 s injected probe leave `interior` identical.
- **N3 (obligation 4).** "Before any energy is read" cannot be true: the controller writes energy into `summary_metrics.json` at finalization, and `complete_bundle_sha256` hashes it (P16). Replace with "before any claim-set consumer (obligation 2) runs".
- **N4.** Historical QPE sessions have no exemption, so re-summarizing the two pilot nights after S2 refuses. State this in D4 as intended.
- **N5.** Moving code in S1 invalidates the line citations at `results-fill-registry.md:366–367, 774` (P23). The S1 PR body should list them for refresh. No test is affected.

## 3. Write scopes versus frozen and registered digests (charge item 3)

- **No proposed write scope moves a registered digest.**
  - No current-byte digest of any scope file appears in a tracked file outside `arm_readiness.sources` and the process traces.
  - The QPE registration pins only the zsh chain, which no scope includes.
  - The Revision 5 estimator-code pins are the four `ESTIMATOR_CODE_PATHS`, none of which is in scope.
  - `reduce.py` and `bundle.py` are correctly excluded.

  (P6, P22)
- **S1 moves frozen readiness *source* pins** only in the nine Qwen2.5 packs: `controller` 18, `bundle_read` 42, `calibration_bracketing` 51, `whole_window` 24, `floor_extraction` 33, `analysis_engine/inputs` 24, plus `aggregate` 24 and `publication_privacy` 24 if M5 and M11 are adopted. Those packs' bytes are untouched and they are retired by D9. This is the movement ex-01 X2 already accepted.
- **Pinned tests.** New tests must not edit `tests/test_calibration_bracketing.py` (9 pins), `tests/test_calibration_ledger.py`, `tests/test_mint_floor_artifact*.py` or `tests/receipt_corpus.py`. Every test module R2 names is unpinned (P22).
- **R2 additions required by this report:**
  - `joulewise/evidence_night.py` and `tests/test_evidence_night.py` (M8);
  - `joulewise/aggregate.py`, `joulewise/window_duration_margins.py`, `scripts/mint_floor_artifact.py` and `scripts/extract_detection_floors.py`, each only if not paper-pinned. Check `results-fill-registry` before granting (M5);
  - `joulewise/publication_privacy.py` (M11);
  - a new `tests/test_bfgs_*.py` module per obligation.

## 4. Confirmed, no finding

- D9's code claim (P1).
- The F-1 site (P2).
- D5's line numbers (P3).
- D4's digest (P6).
- `scored_reduce` has no production caller (P13).
- `reduce_bundle` calls `metadata()` inside its `try` before any energy (`reduce.py:2649–2667`).
- `_resolve_reducer_version` uses only the tolerant summary.
- Controller failure summaries are built directly, not through the reducer, so D6 cannot rewrite a real failure reason.
- D10's arithmetic (200 mA × 12.9 V × 480 s ≈ 1.24 kJ).

## 5. Disposition table

| # | Finding | Tier | Closes by |
|---|---|---|---|
| M1 | QPE early return: pre-only envelope refuses the pilot on a non-battery reason; `:1087` wrong | BLOCKER (text) | D3 text in M1 |
| M2 | D8 loader outcome unspecified (poison or withholding); bundle-keyed historical set cannot exempt a capture | BLOCKER (text) | D8 text in M2 |
| M3 | D5 vs D6 on MOCK; no `not_applicable` | MATERIAL | D6 addition |
| M4 | D6 set enumeration; obligation 8's visibility claim false for the paper | MATERIAL | D6 and obligation 8 text |
| M5 | Claim-set builders and energy accessors unnamed; superseded attempts | MATERIAL | Obligations 2 and 3 replaced |
| M6 | D7 key universe; obligation 5 then has no truth content | MATERIAL | D7 sentence; R3 |
| M7 | Seventh allowlist row amends ex-04 | MATERIAL | D2 addition |
| M8 | Fence needs `evidence_night.py`; polarity | MATERIAL | D11 fence text |
| M9 | `observe` unpinned but edited mid-epoch | MATERIAL | D1/D2 text |
| M10 | S3 before S4 may strand `_v5` | MATERIAL (plausible) | S3 check |
| M11 | Publication privacy rejects new bundles | MATERIAL (operational) | Scope or ruling |
| N1–N5 | Reasoning, timing, wording, historical QPE, line cites | NIT | As stated |

**On R3.**
- Obligation 5 is not a BFG-S blocker once M6 is adopted, because the reduction then refuses and no number can be untrue.
- Obligation 8 is a separate lane, but it must block mechanically at the renderer (M4 text). Under #421, a "blocking" that exists only by record does not satisfy "germane → mandatory".
