```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "BFG-S insertion sites and pin collisions are mapped at 64e39bb9; implementation needs rulings on non-derivation evidence semantics and immutable pack re-freeze.",
  "workspace": {
    "base_requested": "64e39bb937e79c710886acf13fbfab295526aa18",
    "base_mode": "exact",
    "head_start": "64e39bb937e79c710886acf13fbfab295526aa18",
    "head_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "upstream_end": "64e39bb937e79c710886acf13fbfab295526aa18",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"row": "BFG-S production and defect-shaped tests", "action": "start_now"},
      {"row": "Non-derivation record, verdict, and historical replay contracts", "action": "needs_ruling"},
      {"row": "Transaction-pack successor generation and readiness re-freeze", "action": "needs_ruling"},
      {"row": "Revision 5 predicate and registration amendment", "action": "wait_for", "event": "Revision 5 epoch issued or stopped"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD origin/main",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["64e39bb937e79c710886acf13fbfab295526aa18", "64e39bb937e79c710886acf13fbfab295526aa18"]},
      "expected": {"exit_code": 0, "tail_regex": "64e39bb937e79c710886acf13fbfab295526aa18"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --exit-code",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The ruled BFG-S row does not define non-derivation phase names, authenticated verdict format, historical-bundle compatibility, or scored-reducer evidence binding.",
      "needs": "Lead to settle the contracts before implementation."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Nine existing d117 packs have immutable readiness sources and freeze receipts; the authoring command will authenticate those sources, not replace them.",
      "needs": "Lead to name successor packs and approve their authoring sequence."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The QPE-01 frozen protocol has no battery-float exclusion reason; a new exclusion would move its ruled digest.",
      "needs": "Choose a fail-closed summary outcome or obtain a new protocol ruling."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| BFG-S code and tests | start_now | Ruled evidence semantics below before finalizing consumer behavior | `controller.py`, `bundle_read.py`, `calibration_bracketing.py`, battery consumer guards |
| Transaction-pack readiness | needs_ruling | Successor pack names and authority to mint new freeze receipts | Nine immutable d117 pack trees; 51 distinct pinned source files |
| Revision 5 text and predicate amendment | wait_for | Revision 5 epoch **issued or stopped** | Registered text digest and `battery_float.py` verdict replay |
| Non-derivation arm | wait_for | BFG-S code, review, and applicable pack re-freeze complete | All non-derivation window kinds |

## Insertion packet at `64e39bb9`

The BFG-D seam is [`battery_float.observe/require_pass`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/battery_float.py:287) for live probes. Its [`authenticate_committed_verdict`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/battery_float.py:691) is specific to terminal derivation sessions and committed harvest verdicts. The latter cannot directly authenticate a quiet envelope or run bundle.

| BFG-S item and insertion site | Current code at the site; required connection |
|---|---|
| Quiet collector **pre**: [`scripts/sample_quiet_predicate_evidence.py:1065`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1065), after `session` construction and **before** observer accounting and the first envelope stamp. | `envelope_cpu_start = cpu_total()` / `start = clock.stamp()` (:1066–1067). Use `observe` with a bytes runner; retain `raw/battery_float.pre.ioreg` and its record. |
| Quiet collector **post**: same file [:1164](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1164), after `session["end_stamp"] = asdict(clock.stamp())` (:1163) and `whole_envelope_observer_cpu_s` (:1164), before reduction (:1166). | `session["end_stamp"] = asdict(clock.stamp())` / `session["whole_envelope_observer_cpu_s"] = cpu_total() - envelope_cpu_start` (:1163–1164). Retain the post raw bytes and record in `session.json`; the collector currently writes that file at :1208. The ruling does not say whether an unsuccessful pre probe stops collection or produces a retained non-pass envelope. |
| Quiet `summarize`: same file [:1468–1473](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1468), authenticate each session’s two observations before `aggregate` at :1516–1518. | `session_path = path.parent / "session.json"` / `session = json.loads(session_path.read_text()) if session_path.exists() else None` (:1468–1469). It currently trusts the journal and has no battery read. |
| `quiet_predicate_campaign.pilot_summary`: [`joulewise/quiet_predicate_campaign.py:1194–1199`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/quiet_predicate_campaign.py:1194), authenticate the session/raw pair before `all_rows.extend(rows)`, `hard_exclusions`, and energy retention at :1225–1274. | `session = json.loads((out / "session.json").read_text())` / `rows = [json.loads(line) for line in (out / "rounds.jsonl").read_text().splitlines() if line]` (:1196–1197). It currently has no battery check. Reuse one new `battery_float` authentication helper; do not call guarded `parse` from this module. |
| Controller **pre**: [`joulewise/controller.py:870`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:870), after `_stage_prepare()` and before `_stage_idle_baseline()`. | `self._stage_prepare()` / `self._stage_idle_baseline()` (:869–870). Use `observe`; store record and raw bytes on `_Execution`. |
| Controller **post**: [`joulewise/controller.py:873–874`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:873), after `_stage_idle_drift_sentinel()` and before cleanup. | `self._stage_idle_drift_sentinel()` / `self._stage_cleanup()` (:873–874). This is after the measured sampler and the post-idle sentinel. Failure-path handling needs a ruling so a missing post cannot leave a successful bundle. |
| Bundle raw files and `metadata.json.battery_float`: controller [`_write_metadata:2079`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:2079) and [:2235](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:2235). | `extra: dict[str, Any] = {}` (:2079); `self._writer.write_metadata(extra)` (:2235). Put `battery_float` in **top-level** `extra`, with `pre` and `post`, not in caller-supplied `metadata.extra`. Existing [`RunBundleWriter.write_raw`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/bundle.py:1150) writes the two bytes files; `bundle.py` need not change. |
| `BundleReader.metadata()` and `reduce_bundle`: [`joulewise/bundle_read.py:272–279`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/bundle_read.py:272). | `raw = self._strict_json("metadata.json")` / `self._cache["metadata"] = raw` (:275–278). Validate record shape, paths, raw digests, reparse, and both predicates **before caching**. [`reduce_bundle:2652–2667`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/reduce.py:2652) already turns `BundleReadError` into `FAILED/unknown_error`; `reduce.py` need not change. |
| `scored_reduce.reduce`: [`joulewise/scored_reduce.py:145–158`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/scored_reduce.py:145). | `def reduce(registration, roster, predicted_decode_s, score_rows, capture_windows):` / `verify_executed_roster(registration, roster, predicted_decode_s)` (:145–146). It currently accepts only caller-supplied window dictionaries and has no production caller in `joulewise/` or `scripts/`. Require authenticated battery evidence bound to **every** capture window before `_check_window` and before scores can contribute. The argument and binding format are unruled. |
| Calibration candidate consumer 1: [`joulewise/calibration_bracketing.py:1629–1634`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/calibration_bracketing.py:1629), within `_load_calibration_candidate_unbounded` (:1542). | `authenticated_capture = capture_wall_time_from_events(events_raw)` / `effective_bound = verify_stored_evidence_physics(evidence, powermetrics_raw, events_raw)` (:1631–1634). Authenticate battery raw files **before** `verify_stored_evidence_physics` reads the bound. Merely checking for the `battery_float` key is insufficient. |
| Calibration bracket consumer 2: [`joulewise/calibration_bracketing.py:1982–1984`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/calibration_bracketing.py:1982), entry to `evaluate_calibration_bracket` (:1965). | `"""Select a causal bracket and apply the provenance-bound D-079 budget."""` / `result: dict[str, Any] = {` (:1982–1984). Directly supplied candidates must be covered before their bounds are selected. A `CalibrationCandidate` already contains `b_fiducial_s`, so this second check cannot substitute for the loader’s earlier check. |
| Readiness source re-freeze: authoring entry [`arm_readiness_evidence.py:3332–3347`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/arm_readiness_evidence.py:3332), then [`generate_arm_readiness.py:36–57`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/generate_arm_readiness.py:36). | `if source_dir.exists() or evidence_dir.exists():` / `return _authenticate_existing(...)` (:3334–3347). Existing frozen sources are authenticated, not overwritten. New pack generations must be authored, committed, then frozen with the CLI. |

**Stamp fence.** The quiet pair must lie outside the collector’s `start` [:1067](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1067) through `end_stamp` [:1163](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1163). Inside that span are each round’s start [:1096](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:1096) and support end [:658](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:658), plus the power recorder’s `pre_spawn` [:740](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:740), `first_parse`/`sampling_started` [:758–759](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:758), `sampling_stopped` [:778](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:778), and `post_parse` [:830](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/sample_quiet_predicate_evidence.py:830). These feed the recorded round alignment or power anchor.

The controller pair must enclose baseline, measurement, and sentinel: baseline time [:945](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:945), idle-admission attempt times [:1124–1126](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:1124), sampler `sampling_started`/`sampling_stopped` [:1262, :1294](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:1262), and the adapter’s estimator stamps `pre_spawn`, `first_parse`, `post_parse` at [`powermetrics.py:398, :1553, :532`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/adapters/powermetrics.py:398). The sentinel’s parse anchor is [`powermetrics.py:1040`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/adapters/powermetrics.py:1040). The failure-path stop stamp at [`controller.py:1591`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:1591) also precedes any attempted post observation.

## Frozen-source and registry pins

Exactly **nine** campaigns have `arm_readiness.sources` pinning a BFG-S production file. They are the floor 1.5B, floor 7B, and Qwen2.5 contrast families at each of `_v1`, `_v2`, `_v3`:

| Campaign directories under `configs/campaigns/` | `controller.py` pin | `calibration_bracketing.py` pin | BFG-D writer pin |
|---|---|---|---|
| `d117_floor_qwen25_1p5b_v1`, `d117_floor_qwen25_7b_v1`, `d117_contrast_qwen25_1p5b_vs_7b_v1` | `b0b84b1086b53ab13e2bc38592daf494afb61fbf531c68c015cea723367a26a4` | `f020bda2bc93c93d54557b2a5244a2ca23939939f0c291fd9a6fd6f3af212a7d` | `7b197a559e3a24865acad881113f5334780481caf3192a6c40055f5342ecf8e8` |
| Corresponding three `_v2` directories | `b0b84b1086b53ab13e2bc38592daf494afb61fbf531c68c015cea723367a26a4` | `62111af1903ea6f2cce89fc734d97305df48dffbc9aab6de5e140ffb5ccd2b42` | `9ca2a026d18b7b74da2bb1803c60799f453b406dded40d007d361a60020ab844` |
| Corresponding three `_v3` directories | `96c96286c69279ac3a595f2e8843b5b0e57a94c59b6c1510789ab90a06f4d423` | `53addd143817f7476324381ef34524b7233d14bfe0b6ab806b8ba94389581` | `5b3e729d588ecad03d8ece85cc72e4ec03adc66427e893af0b1208c03d3ba020` |

All nine pin `joulewise/bundle_read.py` at `82d4ef714147cf7c1cd43298f598e6c149bc8ca7a69c2b7038d47cf018f0803c`. Across the nine packs, the proposed edits hit **51 distinct source files**: 51 pin `calibration_bracketing.py`, 42 pin `bundle_read.py`, and 18 pin `controller.py`. Eighteen additionally pin BFG-D’s already changed `scripts/validate_powermetrics_fiducial.py`; this is the prerequisite stated in ex-01 §5.3 item 8. The current source hashes are different from those historical pins, as expected for frozen historical packs.

The mechanism is [`scripts/author_arm_readiness_evidence.py --pack-root … --measurement-checkout …`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/scripts/author_arm_readiness_evidence.py:33), commit its emitted `arm_readiness.sources` and `arm_readiness.evidence`, then [`scripts/generate_arm_readiness.py freeze --pack-root … --measurement-checkout … --predecessor-pack-root …`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/docs/phase_2/window_runbook.md:297). Receipts and plan-tree pins are **no-clobber** [`window_runbook.md:284–323`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/docs/phase_2/window_runbook.md:284). Consequently, “re-freeze” must mean authoring successor pack generations; patching the nine committed source JSON files would move their committed pack digests and contradict that custody rule. The three `_v5` campaign directories have no `arm_readiness.sources` yet and must receive their first applicable authoring/freeze before a transaction window uses them.

No registered experimental digest should be rewritten by this code PR. A new successor pack gets a **new** committed pack digest and reviewed freeze receipt. Editing the frozen [`QPE-01 pilot_protocol_v3.json:19–30`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json:19) to add a battery exclusion *would* move its `69321c…` registration digest; [`night_gate.RULED_REGISTRATIONS`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/night_gate.py:108) and the [README:8–17](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/configs/campaigns/quiet_predicate_evidence_01/README.md:8) say that change needs a cold-gate ruling.

Other pin collisions to preserve:

- `joulewise/reduce.py` is one of the four [`ESTIMATOR_CODE_PATHS`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/calibration_bracketing.py:206) and is pinned in 24 readiness source files. Implement the reducer refusal through `BundleReader.metadata()`; leave `reduce.py` byte-identical.
- `joulewise/bundle.py` is pinned in 42 readiness sources. Its existing `write_raw` and metadata merge suffice.
- `tests/test_calibration_bracketing.py` is pinned in nine sources. Put BFG-S bracket regressions in a new test module to avoid moving this test pin.
- [`docs/paper/results-fill-registry.md:791`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/docs/paper/results-fill-registry.md:791) pins `scripts/paper_anchor_correction_quantified.py`, **not** a proposed BFG-S edit. BFG-D kept that paper script byte-identical (ex-03 §2 E2 and §3 item 6); BFG-S should do the same.
- BFG-D retained `SAMPLERS`, `protocol_v3.json`, all four estimator digests, chain digest, and the manifest/evidence artifact key sets (ex-03 §2 E2, E7). The BFG-S pin test should assert the same invariants where its path overlaps.

## F-1 and §4.11 disposition

**F-1 is in BFG-S now.** At [`controller.py:439–447`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/controller.py:439), the refusal begins `"battery_float" in evidence or any(`. BFG-D writes that key on ordinary pre-calibration captures too. Delete only the key arm; keep the `REVISION_FIVE_EPOCH` identity arm. Change [`tests/test_revision_five_b_readers.py::test_controller_attachment_refuses_before_physics_or_bound`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/tests/test_revision_five_b_readers.py:64) so a **non-Revision-5** file with `battery_float` attaches and Revision 5 evidence still refuses before physics or B access. This moves the controller readiness pin and belongs in the same BFG-S code PR.

**The future-time predicate, registration text, and module pin are gated.** Current [`battery_float.parse:249–253`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/joulewise/battery_float.py:249) rejects `age > 180` and permits a large negative age. The later amendment changes that to `abs(update_age_s) <= 180`; it also carries the digest-recorded custody clause into the registered [“Window verdict” text:658](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:658) and adds `joulewise/battery_float.py` to that registration’s code pins. Ex-02 §4.11 states the gate exactly:

> “The BFG-S predicate change (`|update_age_s| ≤ 180`), the carrying of the custody clause into ‘Window verdict’, and the addition of `joulewise/battery_float.py` to the registration's code pins are one text-and-code amendment that lands only after the Revision 5 epoch has issued or stopped; if it lands earlier, issuance refuses on disagreement by design and the epoch waits.”

Thus BFG-S may use the present shared predicate now; this three-part amendment is a **later PR**, not part of the before-non-derivation-arm code PR. BFG-D records the module digest in each harvest verdict but does not refuse on module drift alone (ex-02 §3.7).

## Defect-shaped test packet

The literal demand that **every** ex-01 §5.6 test be RED at this head conflicts with the merged BFG-D state: its parser, arm, issuer, writer, harvest, and recovery tests already pass. The table gives a new **BFG-S-specific** test for each obligation; each proposed test is RED at `64e39bb9` for the stated production reason. Existing BFG-D assertions remain controls.

| Ex-01 §5.6 | Proposed test and production call site | Why RED now |
|---|---|---|
| 1, 3, 4 | `test_bfgs_quiet_collect_charging_pre_refuses_before_recorder_start` → `sample_quiet_predicate_evidence.collect`; `test_bfgs_controller_charging_pre_never_starts_idle_baseline` → `_run_lifecycle` | Neither call site invokes `battery_float.observe`; existing night gate and zero-capture tests already cover their BFG-D paths. |
| 2, 10 | `test_bfgs_bundle_reader_reparses_raw_instead_of_trusting_passed_and_rejects_stale` → `BundleReader.metadata()` | It presently accepts arbitrary metadata JSON; no battery raw file is opened. Parser boundary cases themselves already pass in BFG-D. |
| 3 | `test_bfgs_pilot_summary_refuses_charging_session_even_with_clean_rows` → `pilot_summary` | It can retain the envelope using only rows and existing exclusions. |
| 5 | `test_bfgs_controller_bundle_has_two_raw_files_and_top_level_records_without_moving_estimator_pins` → `_run_lifecycle`, `_write_metadata` | No controller brackets or metadata key exist. Assert BFG-D’s sampler/protocol/estimator/chain/key-set invariants separately. |
| 6 | `test_bfgs_bracket_loader_rejects_charging_capture_before_physics` and `test_bfgs_bracket_evaluator_rejects_unauthenticated_direct_candidate` → the two `calibration_bracketing.py` sites | Both currently accept their battery-free candidate inputs. Issuer replacement and A-7 tests are already BFG-D controls. |
| 7 | `test_bfgs_pilot_passes_two_float_points_with_delta_q_75_diagnostic` → `collect` then `pilot_summary` | Neither records or reports battery ΔQ. The BFG-D slot ΔQ test is already green. |
| 8 | `test_bfgs_failed_controller_run_missing_post_cannot_reduce_successfully` → controller finalization and `BundleReader.metadata()` | Failure metadata has no mandatory post observation; reader does not check it. |
| 9 | `test_bfgs_quiet_and_controller_probe_spans_miss_all_anchor_stamps_at_zero_and_two_seconds` → collector/controller logical clocks | No probe spans exist; the current serialized stamps cannot prove non-overlap. |
| 10 | `test_bfgs_quiet_and_bundle_stale_raw_fail_closed` → `summarize`, `pilot_summary`, `BundleReader.metadata()` | Neither consumer reparses `UpdateTime`. BFG-D’s 179/181-second tests remain controls. |
| 11 | `test_bfgs_aborted_quiet_envelope_with_no_post_is_not_retained` → `pilot_summary` | It has no required post record or equivalent of a finalized-slot check. |
| New scored obligation | `test_bfgs_scored_reduce_requires_authenticated_battery_for_every_live_window` → `scored_reduce.reduce` | The function has no authenticated-evidence argument and can score caller-supplied window dictionaries alone. |
| F-1 | `test_controller_attachment_allows_non_rev5_battery_capture_but_refuses_rev5_before_physics` → `_load_instrument_calibration_attachment` | The `"battery_float" in evidence` arm refuses both. |

Update [`tests/test_battery_float_sweep.py:69–97`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/tests/test_battery_float_sweep.py:69) when adding the two production `observe` callers: its exact caller inventory must name each bytes runner. The [`tests/test_battery_float_consumers.py`](/Users/edr/code/JouleWise-wt-bfgs-scout-8e43cfa7/tests/test_battery_float_consumers.py:24) AST guard from ex-04 §3.10 must remain authoritative: production code cannot call `parse`, `validate_window`, `load_committed_verdict`, `compare_verdict`, or `verdict_record` directly. A new in-module non-derivation authentication helper would require a **narrow, named allowlist addition and guard self-test**; its public consumer call must be tested through the real production sites.

## Rulings needed before final implementation

| Ambiguity left by the ruled BFG-S row | Options | Recommendation |
|---|---|---|
| The v1 observation `phase` enumeration in ex-01 §5.4 names slot and arm phases, not quiet-envelope or controller phases. | Reuse `slot_pre/post` with null slot identity; or add explicit `quiet_pre/post` and `bundle_pre/post`. | Add explicit phases and test strict identity/path bindings. Do not imply these are derivation slots. |
| Non-derivation verdict and custody semantics are unspecified. | Reuse committed derivation verdict files; or define a `battery_float` helper for a raw pre/post pair tied to its session/bundle metadata. | Use a new helper in the existing module. The derivation seam needs a terminal ledger session and a committed harvest file that these windows do not have. Apply the ex-02 digest-recorded custody distinction. |
| Quiet collector’s “brackets” could mean each 30-second round or the 600-second envelope. | Round pairs; envelope pair; both. | Envelope pair outside :1067–1163; that is the unit `pilot_summary` retains and scores. Specify behavior when pre fails and when the collector exits before post. |
| Frozen QPE-01 exclusions do not include battery failure. | Add an exclusion and register v4; refuse the pilot’s claim on a non-pass envelope; or report diagnostic only. | Fail closed without silently changing the frozen list. A replacement/exclusion route needs a new cold registration. |
| Controller failure after pre, before post, and non-Mac/mock runs are unspecified. | Require a post on every finalized bundle; or only when a measured window exists; define an unsupported target outcome. | Require an authenticated pair for any claimed measured window, and make incomplete/failing pairs structured non-success. Preserve failure-bundle finalization; do not treat a missing post as pass. |
| `BundleReader.metadata()` must fail closed for new bundles but historical bundles have no key. | Reject every historical re-reduction; exempt a fixed authenticated historical set; or version the contract by trusted provenance. | Set an explicit prospective version boundary and a narrowly authenticated historical rule. Do not infer it from a freely writable `passed` flag. |
| `scored_reduce.reduce` currently receives `bundle_sha256`, not a bundle path or authenticated battery object. | Accept a mapping of verified bundle results; authenticate each bundle inside the reducer; or extend each capture-window record. | Pass a frozen authenticated evidence object keyed to capture identity and bundle digest; refuse missing, duplicate, or mismatched entries before scoring. Name its producer. |
| Bracket evaluator receives `CalibrationCandidate` after its B field was loaded. Historical/genesis candidates also exist. | Gate all candidates unconditionally; prospective-only gate; or add custody proof to candidate type. | Authenticate at loader before physics and carry a verified proof into evaluator; define an explicit historical compatibility boundary. |
| “Re-freeze every transaction-pack campaign” conflicts with no-clobber committed receipts. | Edit nine frozen packs; author successor generations; or permanently retire those packs. | Author successor generations and new receipts. Lead must name the generations and identify which of the nine are still armable; existing pack bytes stay intact. |
| Wall-meter windows share the battery screen but need an energy rule. | Treat float as sufficient; or retain the separate wall-meter bar. | Retain the A-R5b wall-meter bar: float only screens thermal state; WALL-METER-GAIN-01 still controls claim bearing. |

## Critical path

1. Settle the non-derivation evidence contract and the QPE-01 fail-closed outcome.
2. Land BFG-S production code, F-1 closure, AST/sweep updates, and the RED-to-GREEN tests. Keep `reduce.py`, `bundle.py`, the four estimator paths, and paper-pinned scripts byte-identical.
3. Name and author successor transaction packs from that reviewed main head. Commit new sources/evidence, mint no-clobber freeze receipts, and verify the plan-tree pins before any transaction-pack arm.
4. After the Revision 5 epoch issues or stops, land the single ex-02 §4.11 predicate/text/code-pin amendment.

## Delegation contracts

**Proposed BFG-S code-seat `WRITE_SCOPE`** (exact paths; no pack writes):

```text
joulewise/battery_float.py
joulewise/controller.py
joulewise/bundle_read.py
joulewise/calibration_bracketing.py
joulewise/quiet_predicate_campaign.py
joulewise/scored_reduce.py
scripts/sample_quiet_predicate_evidence.py
tests/test_battery_float.py
tests/test_battery_float_consumers.py
tests/test_battery_float_sweep.py
tests/test_revision_five_b_readers.py
tests/test_controller.py
tests/test_bundle_read.py
tests/test_reduce.py
tests/test_sample_quiet_predicate_evidence.py
tests/test_quiet_predicate_campaign.py
tests/test_scored_reduce.py
tests/test_bfgs_calibration_bracketing.py
```

**Proposed pack-seat scope:** only the exact, lead-named *new successor* `configs/campaigns/<pack-id>/**` trees, plus their reviewed generator paths if generation requires changes. Do not grant the nine existing frozen pack trees by inference. The seat runs `author_arm_readiness_evidence.py`, commits its outputs, then runs `generate_arm_readiness.py freeze` in the ruled order.

**Split:** use **two PRs now**: BFG-S code/tests/F-1 first; successor pack authoring and freeze second, based on the merged code head. A **third, later PR** carries the indivisible ex-02 §4.11 Revision 5 amendment. BFG-S is complete only after the second PR and the applicable transaction-pack freeze checks pass.