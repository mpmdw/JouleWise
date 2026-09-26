# BFG-S design consult — Opus seat (Claude Opus 5.5, `claude-opus-5-5`)

Blind seat. One foreground session in worktree `JouleWise-wt-bfgsc-opus-6bec2aa6` at `64e39bb937e79c710886acf13fbfab295526aa18` (confirmed with `git rev-parse HEAD`). I opened no other seat's file. I read the scout packet, ex-01 (§5.1 to §5.8), ex-02 (§3 and §4), ex-03 §8 F-1 and E19, ex-04 §3.1 and §3.10, and the code listed below. I wrote nothing except this file.

**Contamination.** The harness loaded the global and project `CLAUDE.md` and the auto-memory index. I opened none of them beyond that.

## 0. Executed evidence (this session)

| # | What | Result |
|---|---|---|
| X1 | `/usr/bin/time -p /usr/sbin/ioreg -r -c AppleSmartBattery`, three runs | `real 0.01` each time. The nominal probe cost is about 10 ms, but the ruled timeout is 10 s (ex-01 §5.1), so worst-case cost is set by the timeout. |
| X2 | `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json` | `envelope_s` = 600, `slot_pitch_s` = 620, `start_drift_abort_s` = 2, `start_drift_max_s` = 10. The gap between envelopes is 20 s, and cleanup plus network-time attestation already use it (`quiet_predicate_campaign.cleanup_budget_s`, `:1465`). |
| X3 | Executor `quiet_predicate_campaign.py:1537-1562` | The collector is spawned **at** its scheduled instant, and the collector's `start_drift_s` is `start.monotonic_before_s − scheduled` (`sample_quiet_predicate_evidence.py:1067,1071`). Anything the collector does before `start` therefore adds to the recorded start drift. |
| X4 | `pilot_summary` `:1200-1220`, `:1390-1432` | There is already a precedent for a summary-level refusal that is **not** an exclusion reason. For the replay recorder, the code comment says the refusal "is the SUMMARY's, not an exclusion reason -- A269 byte-pins the registration's exclusion list". The summary is replaced by `REPLAY_NEVER_EVIDENCE` and every energy number is blanked. |
| X5 | `controller._handle_failure` `:1463-1496` | Salvage runs as independent steps (`stop_sampling`, custody, cleanup, env, outputs, trace, metadata) and then writes a failure summary. `reduce.reduce_bundle` turns `BundleReadError` into `FAILED/unknown_error` (scout; not re-read). |
| X6 | `controller._load_instrument_calibration_attachment` `:430-460` | The refusal arm `"battery_float" in evidence` exists. Nothing validates battery state on an attached capture. |
| X7 | `bundle.RunBundleWriter.write_metadata` `:1032` | No digest of `metadata.json` is recorded anywhere at write time. `complete_bundle_sha256` (`detection_floor.py:558`) is computed only later, by consumers (`floor_extraction:2135`, `analysis_engine/inputs:1911`, `mint_floor_artifact:399`). |
| X8 | `bundle_read.FROZEN_LEGACY_BUNDLE_IDENTITIES` `:144` | Keyed on `(run_id, config_sha256)`, which are metadata fields. This is **not** a byte authentication and must not be the model for Q6. |
| X9 | `whole_window.py:761,1021,2453,3639`, `floor_extraction.py:1853,1925`, `analysis_engine/inputs.py:845` | These read `metadata.json` directly, not through `BundleReader.metadata()`. |
| X10 | `night_kinds.NIGHT_KINDS` | Only two kinds are registered: `quiet_predicate_evidence` (payload) and `calibration`. |
| X11 | `battery_float.observe` `:287` | `phase` is accepted as free text; nothing checks it against the enumeration. |
| X12 | `CalibrationCandidate` `:607` | Already carries `relative_path`, `evidence_sha256` and `bracket_runs_root`, which is enough to re-read the capture from bytes at the evaluator. |
| X13 | `scored_reduce` | No `configs/` or `docs/paper` file references it, so its `REDUCTION_CODES` are not registered. No production caller exists. |
| X14 | `configs/campaigns/` | The `_v5` directories (`d117_contrast_v5`, `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5`) hold only generators. None of the three has a `_v4` sibling. The runbook (`:307-316`) says a `_v<N>` pack refuses to freeze without the `_v<N-1>` sibling as `--predecessor-pack-root`. |

NOT EXECUTED: no test was run; no freeze dry run; no measurement of a hung ioreg.

---

## Q1. Observation `phase` values

**Decision.** Add explicit phases and keep the schema id `joulewise.battery_float.v1`. The ruled enumeration becomes:

`arm_check | publish_install | t0 | validate_install | t0_power_row | slot_pre | slot_post | quiet_envelope_pre | quiet_envelope_post | bundle_pre | bundle_post`

- Ordinary bracket captures and the controller's pre-calibration captures come from the same writer as derivation slots. They keep `slot_pre`/`slot_post` and are not renamed.
- Identity fields:
  - Quiet envelope: `session_id` = the collector's `session`, `slot` = `"envelope-NN"`, `plan_id` = the evidence plan id.
  - Bundle: `session_id` = `run_id`, `slot` = null, `attempt_id` = null, `plan_id` = the campaign plan id where one exists.
- `raw_path` is relative to the container: `raw/battery_float.<pre|post>.ioreg` in both kinds.
- `observe` gains a check that `phase ∈ PHASES`, raising `ValueError` at the call site (X11). This is a programming error, not a probe error.
- Every consumer requires the exact phase pair for its kind. A bundle reader refuses `slot_pre`, and a quiet reader refuses `bundle_pre`.

**Reason.** A null-slot `slot_pre` would read as "a derivation slot with a missing identity". Any reader that keys on phase to decide which custody rules apply would then apply derivation rules (ledger row, `instrument_evidence.json`) to a bundle, or bundle rules to a derivation slot. Adding values to an enumeration leaves every existing v1 record valid, so no schema bump and no rewrite of any committed verdict record is needed. `validate_window` checks `raw_path`, not `phase`, so derivation behaviour is untouched.

**Failure prevented.** A record copied from one kind into another's container passes a reader that does not check which kind it belongs to. Explicit phases plus exact-pair checks catch honest mix-ups, such as a raw file copied across directories by a recovery script.

## Q2. Non-derivation verdict and custody

**Decision.** Add new functions only in `joulewise/battery_float.py`. Do **not** alter `parse`, `validate_window`, `load_committed_verdict` or `compare_verdict` before the Revision 5 epoch issues or stops (see Q12-3).

```python
@dataclass(frozen=True, slots=True)
class PairVerdict:
    kind: str                     # "bundle" | "quiet_envelope" | "capture"
    container_sha256: str         # sha256 of the container bytes judged (metadata.json | session.json | instrument_evidence.json)
    status: str                   # "pass" | "battery_float_confounded" | "battery_float_evidence_missing" | "not_applicable" | "unobserved_historical"
    pre_raw_sha256: str | None
    post_raw_sha256: str | None
    pre_update_age_s: float | None
    post_update_age_s: float | None
    delta_q_mah: int | None       # diagnostic only, never affects status (ex-01 F-5 cure (a))
    reasons: tuple[str, ...]

def _judge_pair(root: Path, battery: object, *, phases: tuple[str, str], identity: Mapping[str, object]) -> PairVerdict  # private core
def authenticate_bundle(bundle_path: Path) -> PairVerdict          # container metadata.json
def authenticate_quiet_session(envelope_dir: Path) -> PairVerdict  # container session.json
def authenticate_capture(capture_dir: Path, *, manifest_sha256: str | None = None) -> PairVerdict  # container instrument_evidence.json, anchored by manifest.json.artifacts
```

`_judge_pair` applies ex-02 §4.1 steps E2 to E6 to each phase:

- The phase is absent, is not a dict, has the wrong `phase` value, the wrong `raw_path`, a malformed digest or a non-numeric `wall_time_s` → `evidence_missing`.
- Raw bytes are unreadable, or their digest differs from the recorded one → **`CustodyFailure`** (raised).
- `exit_code ≠ 0` or `timed_out` → `evidence_missing`.
- `parse` raises (stale, malformed, object count) → `evidence_missing`.
- The parse succeeds but `passed` is false → `confounded`.

Confounded takes precedence over missing. Custody failure precedes everything. The helper calls the **existing** `parse` unchanged; a stored `passed` is never trusted.

**Refusal reasons** (strings in `reasons`, plus the one exception):

- `CustodyFailure`: `custody failure: <kind>/<phase> expected <sha> observed <sha|absent>`.
- `<phase> evidence missing: phase not recorded | raw path mismatch | digest malformed | wall time invalid | probe failed | <ProbeError text>`.
- `<phase>: ExternalConnected is not Yes | IsCharging is not No | InstantAmperage exceeds 200 mA`.
- `phase identity mismatch: <field>` (session id or run id differs from the container's own). This one is `evidence_missing`.
- `battery_float key absent` → `evidence_missing`, unless Q6's historical rule or Q5's `not_applicable` rule applies.

**Custody anchor per kind** (the "digest recorded before finalization" in the sense of ex-02 §3.2):

| Kind | Container | Who recorded the raw digests, and when | External anchor of the container |
|---|---|---|---|
| Capture (bracket endpoint, pre-calibration attachment) | `instrument_evidence.json` | The writer, before `manifest.json` is sealed | `manifest.json.artifacts` digest (checked, E1). Also the ledger row when the capture is ledger-backed. |
| Bundle | `metadata.json` | The controller, at `_write_metadata`, before the reducer runs | **None at write time** (X7). The anchor is the `complete_bundle_sha256` pinned by the window's harvest record (Q12-8). |
| Quiet envelope | `session.json` | The collector, before `rounds.jsonl` is finalized | The raw files sit in `raw/` at `parent == raw`, so their digests are **also** written into every row's `raw.sha256` map (`sample_quiet_predicate_evidence.py:1196-1199`). `authenticate_quiet_session` requires both records to agree. A mismatch between them is a `CustodyFailure`. |

**How ex-02's distinction applies.** Any bytes whose digest the container recorded, and which are now absent or different, are a `CustodyFailure`. That is a refusal of the *consumer's whole computation* (reduction, pilot summary, bracket evaluation, scored reduction), never a per-bundle or per-envelope exclusion.

This matters more here than for derivation. A non-pass bundle becomes `FAILED` and drops out of aggregates. Without the distinction, deleting one raw file would turn an inconvenient but valid rep into an excluded one: an outcome-selected exclusion. Under the rule, the only cure is restoring the bytes.

There is no committed verdict file for these kinds. Every consumer recomputes from bytes each time. That is sound because no replacement or top-up rule exists for them: a non-pass verdict can only remove claim eligibility, never license a new window. So the ex-02 check-4 machinery, whose job is to stop a verdict being re-recorded, has nothing to protect.

**AST guard (ex-04 §3.10).** Add exactly three allowlist rows, `battery_float.py::_judge_pair → parse` plus the three public wrappers → `_judge_pair`, with a self-test. Add `PairVerdict` construction to the guard: a `Call` whose target resolves to `battery_float.PairVerdict` outside `battery_float.py` is flagged. This is the same property the existing `AuthenticatedVerdict` seam relies on.

**Failure prevented.** A charging bundle or envelope accepted because a stored `passed: true` was trusted. A clean window turned into an excluded one by deleting a raw file. A derivation verdict changed as a side effect of BFG-S refactoring `validate_window`.

## Q3. Quiet-predicate collector bracket unit

**Decision: the 600 s envelope only; never per 30 s round.**

- **Pre site.** In `collect`, after `session` is constructed and before `envelope_cpu_start = cpu_total()` (`:1065`). The pre record is stored in `session["battery_float"]["pre"]` **before** the first `write_json(out / "session.json", session)` (`:1087`), so it survives a later kill.
- **Post site.** In the `finally` block, after `session["end_stamp"]` and `whole_envelope_observer_cpu_s` (`:1163-1164`), so it also runs when a round raises. The record goes into `session["battery_float"]["post"]` before the final `write_json` (`:1208`).
- Both raw files are written as `raw/battery_float.{pre,post}.ioreg`.

**Why not per round.** A round-level probe would sit inside the power recorder's life and inside the 480 s interior whose energy is the pilot's number. That violates the stamp rule of ex-01 §5.3 item 6, and the probe's own CPU would enter the measured interior. The retained and scored unit is the envelope.

**Pre fails** (predicate failure or probe error). The collector:

1. writes the record and the raw file;
2. sets `session["error_class"] = "battery_float"` and `session["error"] = "battery float refused before capture: <reasons>"`;
3. writes `session.json` and an empty `rounds.jsonl`;
4. **does not start the recorder**;
5. exits 3, mirroring the network-time refusal path at `:1075-1085`.

When the executor sees exit 3 with `error_class == "battery_float"`, it ends the night in-chain with `write_refusal(..., reason="night_refused_battery_float")` for a predicate failure, or `"night_probe_error"` for a probe error. Both codes are already registered by BFG-D, so no new code is needed.

The night ends because, under directive #421 and A-R5b, one non-float slot confounds the whole window. Every later envelope of that night is dead weight. A pre failure on envelope 01 is a zero-capture refusal and gets the D-182 successor route. Any later one is not zero-capture.

**Collector exits before the post read** (SIGKILL, executor timeout 124, power loss). `session.json` holds `pre` but not `post`. `authenticate_quiet_session` returns `evidence_missing`, and the whole night's summary refuses (Q4). The executor should also check the post record on every collector exit: a non-pass or absent post ends the night in-chain with the same codes, which saves up to about 2 h of machine time.

**Budget warning (bears on truth only through aborts).**

- The pre probe runs after the scheduled instant, so its duration lands in the recorded `start_drift_s` (X3). That is about 10 ms nominally (X1) and up to 10 s on timeout, where 10 s is exactly `start_drift_max_s`.
- The post probe extends the collector's life into the 20 s gap (X2). A hung ioreg can push the next envelope past the 2 s `start_drift_abort_s`.
- Both outcomes fail closed (exclusion or night abort), so neither can make a number false. The probe's wall cost must be journaled per envelope (`monotonic_after_ns − monotonic_before_ns` is already in the record) so a budget overrun is diagnosable.

**Failure prevented.** A charging envelope retained because the collector never looked. A killed collector read as clean. Probe CPU inside the measured interior.

## Q4. QPE-01's frozen exclusions

**Decision: (b) fail closed at the summary level, with the frozen exclusion list unchanged.** It follows the in-code replay-recorder precedent exactly (X4).

`pilot_summary` calls `authenticate_quiet_session` for every envelope that exists, readable or not, **before** `all_rows.extend(rows)`.

- If any envelope is non-pass, the report's `status` and `evidence_status` become `BATTERY_FLOAT_CONFOUNDED` or `BATTERY_FLOAT_EVIDENCE_MISSING` (confounded first).
- `retained`, `s_upper`, the sizing and adjacent pairs, every spread and drift statistic, and every per-envelope `joules`/`combined_joules`/`interior` are blanked, exactly as the replay override does.
- A `battery_float_envelopes` list names each envelope, its status, reasons and raw digests.
- `summary.md` says so in one paragraph.
- A `CustodyFailure` makes `pilot_summary` raise; no summary is written.
- `summarize` (the script's multi-session aggregator) applies the same rule per session. It refuses to aggregate any session whose pair is non-pass or missing, and raises on custody failure.

**Why this is not a silent change to a frozen protocol.**

1. **No registered byte moves.** `pilot_protocol_v3.json` and its `69321c…` digest are untouched, and so is every exclusion string. `ac_not_AC_Power_or_probe_error` is explicitly **not** reinterpreted to cover battery state; that would be the silent change.
2. **The exclusion list governs something else.** It decides *which envelopes of a claim-eligible night are retained*. (b) adds no envelope-level rule and changes no retained set of any night the protocol would call claim-eligible. It adds a night-level precondition on claim eligibility, imposed by a binding directive that outranks the protocol, and the codebase already carries one such precondition (replay).
3. **It is monotone.** It can only move a night from "claim" to "no claim", never the reverse, and it is decided from instrument state alone, before any energy is read. So it cannot select on outcome.
4. **It is ruled, not assumed.** This consult and the cold gate are the ruling, and the decision-log entry names it.

If QPE ever registers a v4 for other reasons, it should carry this precondition into the text, as ex-02 does with the custody clause. (c) is refused because a diagnostic-only battery result on a confounded night would let a number that #421 says is not true reach the paper. (a) is unnecessary; its cost is a fresh registration cycle for no gain in truth.

**Failure prevented.** A charging night produces a published spread bound or sizing.

## Q5. Controller outcomes

**Decision.**

**Obligation.** A new bundle owes a battery pair once its lifecycle has **begun `_stage_idle_baseline`**, the first stage that samples power. The authority for this is the event log (a `stage_started` event for `idle_baseline` in `events.jsonl`), not a metadata flag. A bundle that failed in `validate`/`prepare` has no measured window and owes nothing, like `window_exhausted` in A-R5b. The controller still writes `battery_float: {"pre": null, "post": null}` so absence of the key is never the new-bundle state.

**Sites.**

- **Pre:** in `_run_lifecycle`, between `_stage_prepare()` and `_stage_idle_baseline()`, before `_settle_before_idle`. The record is stored on `_Execution` and the raw file written with `RunBundleWriter.write_raw`.
- **Post, success path:** between `_stage_idle_drift_sentinel()` and `_stage_cleanup()`.
- **Post, failure path:** a new independent salvage step `battery_float_post` in `_handle_failure`. It runs **after** `stop_sampling` and **before** `metadata`, only if a pre was taken and no post was.
- **Post, interrupt path:** `_finalize_interrupted_run` gets the same best-effort step.
- **Recording:** both records go in top-level `extra["battery_float"]` at `_write_metadata`.

**Outcome for failure between pre and post.** The bundle finalizes as it does today, with the failure status its stage failure earned. The salvage post is attempted.

- If it cannot be taken (the process died), metadata holds `pre` only. `authenticate_bundle` → `evidence_missing`.
- A failed rep with a charging post is `confounded`.

In both cases the verdict matters **at window level**: every finalized bundle of the window that owes a pair is judged, *whatever its status*, mirroring validate_window's rule "every slot with a finalized ledger row, valid or ordinary-invalid". One non-pass confounds the window (Q12-2). A predicate failure at the pre read does **not** abort the run. The run continues and is recorded confounded, like the derivation writer ("no new exit path", ex-01 §5.3 item 6). The arm and t0 gates are the place that postpones.

**Non-Mac and mock targets.**

- `hardware_target.telemetry_backend == MOCK`: no probe. Record `battery_float = {"not_applicable": "mock_telemetry"}`. `authenticate_bundle` returns `not_applicable` only when the **re-validated `config.json`** says MOCK. Mock numbers are never claim-bearing by construction. `FakeClock` with real telemetry is test-only and follows the MOCK rule only in tests.
- Any real non-Mac target: the probe runs, ioreg is absent, and the result is a probe error → `evidence_missing` → never claim-bearing. This holds until a platform-specific float predicate is **registered** (the NVIDIA horizon leg needs one; a battery-less desktop is not "float" by assumption).

**Every finalized bundle, or only claimed ones?** Every finalized bundle that owes a pair must carry a post *attempt*. A bundle cannot know at write time whether it will be claimed, and "claimed" decided later is exactly the outcome-dependent choice to avoid.

**Failure prevented.** A crash between the reads that leaves a "successful-looking" bundle. A charging failed rep silently dropped while its clean neighbours keep the claim. A mock or non-Mac run that passes by default.

## Q6. `BundleReader.metadata()` and historical bundles

**Decision: exempt a fixed, byte-authenticated historical set. Its membership is the sha256 of `metadata.json` bytes.**

- `bundle_read.py` gains `BATTERY_FLOAT_HISTORICAL_METADATA_SHA256 = "<sha of the set file>"`. The committed file `configs/battery_float/historical_bundle_metadata.json` is a sorted list of `{metadata_sha256, run_id, source_root}`. This is the digest-pinned-registry pattern of ex-02 §4.6.
- `metadata()` reads the bytes it already reads, then:
  - **Key present:** it validates via `authenticate_bundle`. A `CustodyFailure` or non-pass raises `BundleReadError("battery_float_<status>: …")` before caching. This covers Q5's null/null form (valid only when no `idle_baseline` stage started) and `not_applicable` (valid only for a MOCK config).
  - **Key absent:** it passes only if `sha256(bytes)` is in the set, and records `battery_float_status = "unobserved_historical"` on the reader so window consumers can disclose it. Otherwise it raises `BundleReadError("battery_float_evidence_missing: key absent and bundle not in the historical set")`.
- The set is closed once. A reviewed script, committed with the set, enumerates the `metadata.json` of every bundle present in the measurement run roots at the BFG-S merge head. The set file's digest is pinned in the same PR. Bundles not on disk then can never be exempted later.

**Prospective boundary, exactly.** A bundle is prospective if and only if its `metadata.json` bytes are not in the pinned set. That is a content test, not a flag. A new bundle with its key stripped refuses, because its bytes are new. A writable field such as `schema_version`, `git_commit` or `passed` plays no part.

**Why not the alternatives.**

- Rejecting every historical re-reduction would break paper-reproduction paths (`whole_window`, `floor_extraction` and `analysis_engine` all go through readers) with no gain in truth. Those numbers already exist, and their disclosure is a separate question (Q12-6).
- "Trusted provenance" versioning has no trusted field to key on (X7, X8).
- `FROZEN_LEGACY_BUNDLE_IDENTITIES` is **not** reused, because it keys on writable fields (X8).

**Failure prevented.** A new charging bundle made to reduce by deleting `battery_float` from its metadata. Historical bundles bricked by a prospective rule.

## Q7. `scored_reduce.reduce` evidence

**Decision.**

- New signature: `reduce(registration, roster, predicted_decode_s, score_rows, capture_windows, battery_evidence)`, where `battery_evidence: tuple[PairVerdict, ...]`.
- Each `PairVerdict` is produced by `battery_float.authenticate_bundle(bundle_path)` with `kind == "bundle"`, plus a `bundle_sha256` field set to `detection_floor.complete_bundle_sha256(bundle_path)`, the existing helper (X7).
- The same helper is **declared** to be the definition of `capture_windows[*].bundle_sha256` in the window-record producer, which does not exist yet (X13), so the two sides cannot drift.
- The producer is whatever harvest code builds `capture_windows`. It must call `authenticate_bundle` on the same path it hashes.

**Checks.** They run after the `_check_window` loop (so `bundle_sha256` is validated hex) and before any score row is read. New `REDUCTION_CODES`, which are not registered anywhere (X13):

- `window_bundle_duplicate`: two capture windows name the same `bundle_sha256`. Today nothing checks this.
- `battery_evidence_input`: not a tuple, or an element not a `PairVerdict` of kind `bundle`.
- `battery_evidence_duplicate`: two entries with the same `bundle_sha256`.
- `battery_evidence_unbound`: an entry whose `bundle_sha256` matches no capture window.
- `battery_evidence_missing`: a capture window, **live or superseded**, with no entry.
- `battery_float_confounded` / `battery_float_evidence_missing`: any entry non-pass. Confounded is checked first. `unobserved_historical` counts as missing, because scored reduction has no historical corpus. `not_applicable` also counts as missing.

Any of these refuses the **whole reduction**. Superseded windows are included because they are slots of the same night: a charging superseded attempt confounds its neighbours thermally, just as it would in a derivation window. `CustodyFailure` is raised by the producer, before `reduce` is ever called.

**Failure prevented.** Scores and energies reduced from caller-supplied window dictionaries with no battery evidence. A charging retry hidden because only live windows were checked. Two windows sharing one bundle's evidence.

## Q8. `calibration_bracketing`

**Decision: gate at both sites. The evaluator re-verifies from bytes and does not trust a proof carried in the candidate.**

**Loader.** In `_load_calibration_candidate_unbounded`, immediately after the `artifact_hashes` check (`:1622-1628`) and **before** `capture_wall_time_from_events`/`verify_stored_evidence_physics` (`:1631-1634`), call `battery_float.authenticate_capture(directory, manifest_sha256=…)`.

- Non-pass → `return None`, the loader's existing refusal idiom, but with the reason logged.
- `CustodyFailure` → propagates. It is deliberately not caught by the `(KeyError, TypeError, ValueError)` arm, because it subclasses `RuntimeError`.

**Evaluator.** At the top of `evaluate_calibration_bracket`, for every candidate before bracket selection, the evaluator:

1. re-resolves `bracket_runs_root / relative_path`;
2. requires the on-disk `instrument_evidence.json` sha256 to equal `candidate.evidence_sha256`;
3. calls `authenticate_capture`.

- A candidate that cannot be re-resolved (no runs root) refuses with a named blocker, unless `_allow_unissued_fixture` is set.
- A guard test asserts that no production call site passes that flag. E7 shows the only callers are `:2642-2742`.
- A proof field on the dataclass is **not** added. `CalibrationCandidate` is a plain frozen dataclass that any caller can build, so a carried proof would be exactly the "trust a stored `passed`" defect.

**Historical/genesis boundary.** It is content-pinned, like Q6. A committed set `configs/battery_float/historical_capture_evidence.json` lists the `instrument_evidence.json` sha256 of every capture that lacks the key at the BFG-S merge head, including `GENESIS_FIXTURE_ACCEPTANCE_SHA256`'s capture set. Its digest is pinned in `calibration_bracketing.py`.

- Key present: the capture must pass.
- Key absent and in the set: `unobserved_historical`.
- Key absent and not in the set: `evidence_missing`.

**Use rule.**

- A bracket may include an `unobserved_historical` endpoint only when re-evaluating a window whose `window_end_s` precedes the set's recorded closing wall time. The evaluator reports it as `battery_float: unobserved_historical`.
- A window ending after that time requires **both** endpoints `pass`. That includes the "before" endpoint, which could otherwise be an old pre-boundary capture.

**Failure prevented.** Physics fitted, and a B bound selected, from a capture taken while charging. A synthetic candidate bypassing the loader. A prospective window bracketed by an unobserved old capture.

## Q9. Transaction packs

**Decision: yes, "re-freeze" means successor generations. Author them lazily, and only for packs that will actually arm.**

**Naming is forced by the tool.** The runbook (`:307-316`) makes a `_v<N>` successor refuse to freeze without its `_v<N-1>` sibling as predecessor. So the successors are:

- `d117_floor_qwen25_1p5b_v4` (predecessor `_v3`)
- `d117_floor_qwen25_7b_v4` (predecessor `_v3`)
- `d117_contrast_qwen25_1p5b_vs_7b_v4` (predecessor `_v3`)

**Retire.** All three `_v1` packs (their own README says "not armable", unfrozen drafts) and all three `_v2` packs (superseded by `_v3`). Retirement is a decision-log entry plus a runbook line. **No pack byte is edited.** In particular, `d117_floor_qwen25_1p5b_v3` stays byte-identical: W1's `calibration_plan.json` (sha `9ab4776f…`) is byte-pinned inside it. The `_v3` packs are retired *for transaction windows* only by being superseded by `_v4`.

**Authoring order.**

1. BFG-S code merges.
2. On the merged head, author **only** the `_v4` of a family the research plan will arm next: `author_arm_readiness_evidence.py`, then commit sources and evidence, then `generate_arm_readiness.py freeze --predecessor-pack-root …_v3`, then verify the plan-tree pins, then commit the receipt.
3. Author the next family only when it is scheduled.

**Why lazy.** Readiness sources pin 51 files, including `calibration_bracketing.py` and `bundle_read.py`. Any later edit to those files stales every `_v4` already frozen and forces a `_v5` of the same family. Freezing all three families now just to satisfy "re-freeze every pack" buys nothing and costs ordinals.

**The `_v5` packs.** Their first authoring comes after BFG-S. They have no `_v4` sibling (X14). Unless the tool derives the generation from something other than the directory suffix, they **cannot freeze as named**. Verify with a pre-write refusal run before the lead relies on them (NOT EXECUTED). If they refuse, they need a family-opening rename, which is a lead decision outside BFG-S.

**Failure prevented.** A transaction window armed against readiness sources that do not describe the code that measures it. A frozen receipt clobbered. W1's pinned plan bytes moved.

## Q10. Wall-meter windows

**Decision: float is necessary but not sufficient. WALL-METER-GAIN-01 remains a separate bar.**

A-R5b's registered Disclosure already says so. The 200 mA screen bounds instantaneous current at two instants, not the battery's net energy over the capture. ex-01 F-5 showed the gauge's mAh register can hide about 45 mAh of inflow and then step by 75 mAh.

- A wall meter measures wall-side energy. Any battery charge or discharge in between moves energy between the wall and the rails, and the meter cannot tell it from load.
- At about 12.9 V (ex-01 E1), 45 mAh is about 2.1 kJ, which is orders of magnitude above the ≈5 J claim bar.
- So a float screen at the endpoints cannot bound a wall-meter number. Wall-meter windows get the full BFG-S brackets *and* stay non-claim-bearing until WALL-METER-GAIN-01 registers a battery-energy bound, or a design that excludes the battery path.

**Failure prevented.** A wall-meter energy claim carrying an undetected battery exchange of kilojoules.

## Q11. The PR split

**Decision: agree in shape, with two amendments.**

1. **PR-S1, transaction and bracket code:**
   - `battery_float` additions (Q1, Q2) and their guard/sweep updates;
   - controller (Q5, and F-1 **plus** its missing counterpart, Q12-1);
   - `bundle_read` (Q6), `scored_reduce` (Q7), `calibration_bracketing` (Q8);
   - the two committed historical sets with their generator.
2. **PR-S2, QPE code:** collector, `summarize`, `pilot_summary` and the executor's in-chain abort (Q3, Q4). It is separable because it touches a different window kind with its own frozen protocol and budget arithmetic. If the lead prefers one code PR, S1 and S2 can merge together, but review lenses should treat them separately.
3. **PR-S3, pack successors:** one `_v4` per family, when scheduled (Q9).
4. **PR-S4 (later), the ex-02 §4.11 amendment:** the `|update_age_s| ≤ 180` predicate, the custody clause in "Window verdict", and the `battery_float.py` code pin. It lands after the Revision 5 epoch issues or stops. This is also the right PR to refactor `validate_window` onto `_judge_pair`, because it is the first point at which changing the derivation path can no longer cause an issuance disagreement.

**Amendment on the arm fence.** Each kind's arm must be **mechanically** blocked until its PR merges (Q12-5), not just procedurally.

**Failure prevented.** One oversized PR whose QPE budget questions stall the transaction path. A refactor that changes a derivation verdict before issuance.

## Q12. What the scout missed that bears on whether a number is true

1. **F-1's closure removes a refusal but adds no check (MATERIAL).** The attached pre-calibration capture's B bound feeds every transaction bundle's energy bound. After deleting the `"battery_float" in evidence` arm, a capture taken while charging attaches silently (X6). In the same PR, `_load_instrument_calibration_attachment` must call `authenticate_capture` on the attached directory before physics or B, with no historical exemption: attachments are always fresh at run time.
2. **Window-level verdict for transaction windows (MATERIAL).** Directive #421: "a window with a non-float slot is confounded". The transaction window is the night, and each rep bundle is a slot. `reduce_bundle` turns every `BundleReadError` into `FAILED/unknown_error`, which is indistinguishable from a crash. Downstream window consumers would therefore drop the charging rep and keep its neighbours, which is the per-slot exclusion A-R5b rejected. The window-level consumer (whichever of `whole_window` or `analysis_engine.inputs` builds the claim set) must call `authenticate_bundle` on **every finalized member, including FAILED ones**, and refuse the window on any non-pass.
3. **Do not touch the derivation path before Revision 5 issues (MATERIAL, sequencing).** Under ex-02 §3.7 and §4.11, the issuer recomputes with the code on `main` and refuses on disagreement. Any BFG-S change to `parse`, `_structure`, `validate_window`, `predates_battery_float` or `authenticate_committed_verdict` could flip a recomputation and strand the epoch. BFG-S should add new functions only. The test should pin the four functions' bytes, or their AST, as a regression guard until PR-S4.
4. **QPE time budget.** See Q3. The probes land in `start_drift_s` and in the 20 s gap. They fail closed but can abort nights. Journal each probe's wall cost, and add a test that a 2 s injected probe moves no interior energy and only shifts `start_drift_s` by the injected amount (the analogue of ex-01 test 9).
5. **No mechanical fence before BFG-S (MATERIAL, procedural gap).** `quiet_predicate_evidence` is a registered, armable kind today (X10). It has the BFG-D arm and t0 gates but no in-window brackets. Only procedure stops a QPE night arming before PR-S2.
   - Cheapest fence: a NightKind field `battery_brackets: bool`. It is `True` for `calibration`, and `False` for QPE until PR-S2 flips it. `evidence_night.check` fails the arm when it is `False`.
   - The analogue for transaction packs already exists, because readiness sources must re-freeze.
6. **Historical claim numbers (scoping question for the lead, not BFG-S code).** Every number already in the paper, and the QPE pilot nights 20260922-0217 and -2100 (observer floor, spread), were measured with battery state unobserved. Q6 and Q8 preserve them as `unobserved_historical`, but #421 makes their truth question mandatory. The lead should rule whether they:
   - are disclosed as pre-directive with battery state unobserved;
   - are audited from retained OS power logs, where they exist (`pmset -g log` history; NOT EXECUTED);
   - or are re-measured.

   BFG-S should at least make `unobserved_historical` visible in every window-level output.
7. **Direct `metadata.json` readers (X9).** `whole_window`, `floor_extraction` and `analysis_engine.inputs` read `metadata.json` without `BundleReader.metadata()`. Before BFG-S merges, a sweep test should prove that each path that can emit a claim-bearing number also goes through the gate: either `BundleReader.metadata()`, a status the gated reducer produced, or a direct `authenticate_bundle`.
8. **Bundles have no write-time custody anchor (X7).** A rewrite of both raw file and `metadata.json` together is undetectable until some consumer pins `complete_bundle_sha256`. The transaction harvest should pin every member's `complete_bundle_sha256` in a commit before any energy is read, the non-derivation analogue of the ex-02 head-pin commit. Without that, the custody rule in Q2 is only as strong as the first later pin.
9. **The `_v5` packs may be unfreezable as named** (Q9, X14). Verify before the lead plans the Qwen3 contrast on them.
10. **`observe` accepts any `phase`** (X11). Add the enumeration check (Q1). It is cheap and catches mislabelled records at the source.
11. **Quiet raw digests are double-recorded for free.** The collector already hashes every file directly under `raw/` into every row's `raw.sha256` map (`:1196-1199`). The battery raw files will therefore appear there automatically. Make it a required cross-check (Q2) rather than an accident, and add a test that the post file's digest appears in the final `rounds.jsonl` rows.

## Summary table

| Q | Decision | Confidence |
|---|---|---|
| Q1 | Explicit phases `quiet_envelope_pre/post`, `bundle_pre/post`; schema stays v1; `observe` validates `phase`; each reader requires its exact pair | high |
| Q2 | New `battery_float` helpers (`_judge_pair`, `authenticate_bundle`, `authenticate_quiet_session`, `authenticate_capture` → `PairVerdict`); ex-02 E2–E6 per phase; recorded-digest mismatch = `CustodyFailure`, which refuses the consumer and never excludes; per-kind anchors as tabled; no derivation function changed | high |
| Q3 | Envelope pair only (pre before `envelope_cpu_start` and in the first `session.json`; post in `finally` after `end_stamp`); pre fail → no recorder, exit 3, in-chain night refusal with existing codes; missing post → `evidence_missing` → night refused | high |
| Q4 | (b) summary-level fail-closed with energy blanked, following the replay precedent; exclusion list and digest unchanged; monotone, instrument-state-only, ruled | high |
| Q5 | Obligation begins at `idle_baseline` start (event log decides); pre before baseline, post after sentinel plus a failure/interrupt salvage step; failures finalize with a non-pass pair; every owing bundle carries a post attempt; MOCK = `not_applicable` from the re-validated config; non-Mac = `evidence_missing` until a platform predicate is registered | med |
| Q6 | Exempt a content-pinned historical set (sha256 of `metadata.json` bytes; digest-pinned set file, closed at the BFG-S merge); everything else must carry a pass | high |
| Q7 | `battery_evidence: tuple[PairVerdict]` from `authenticate_bundle`, keyed by `complete_bundle_sha256`; checks for missing, duplicate, unbound and non-pass over live and superseded windows; refuse the whole reduction | med |
| Q8 | Loader gate before physics, and the evaluator re-authenticates from bytes (no carried proof); content-pinned historical capture set; a prospective window needs both endpoints `pass` | med |
| Q9 | Successors `…_v4` for the three qwen25 families, authored lazily when scheduled; retire `_v1`/`_v2` by record only; `_v3` bytes untouched (W1 pin); `_v5` freezability to be verified | med |
| Q10 | Float necessary, not sufficient; WALL-METER-GAIN-01 stays | high |
| Q11 | Agree in shape: S1 transaction/bracket code, S2 QPE code, S3 lazy successor packs, S4 the §4.11 amendment plus the `validate_window` refactor; mechanical arm fence per kind | med |
| Q12 | Attachment must add a battery check (F-1 half-closure); window-level verdict over FAILED members; derivation path frozen until Revision 5 issues; QPE budget; interim arm fence; historical-number scoping; direct metadata readers; bundle custody anchor at harvest; `_v5` freezability | high on items 1–3; med on the rest |
