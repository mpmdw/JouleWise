# BENCH-REPLAY-START-DRIFT-01 fix round 1 — delta re-audit, CONTRACT LENS (Fable, read-only)

Read at `9e7061be` in `/Users/edr/code/JouleWise-wt-a267-review2` (diff `3e299b85..9e7061be`, 7 paths, 21 commits). Authorities: brief 16 + both addenda, ruling 18 §2, addendum 19, lenses 17a/17b, seat report 18. No test executed; every claim below is by reading.

## Tier summary: BLOCKER 0 / SHOULD-FIX 0 / NIT 5

### NITs (file:line at 9e7061be; scenario)

N1. `joulewise/quiet_predicate_campaign.py:1345-1346` (L2). `outcome, error = "refused", REPLAY_REFUSAL_REASON` overwrites whatever `error` already held. Scenario: a bench night aborts at envelope 02 (`start_drift_abort: envelope 2 …`) or `pilot_summary` raises; `evidence_outcome.error` and the refusal record then read `replay_recorder` only, and the bench report's `outcome_error` loses the abort text (the journal row's `abort` key survives, so the verdict still FAILs via the missing `collector_exit`). Same overwrite pre-existed at :1338 for the readable-session case, so not a regression in effect; `error = f"{error}; {REPLAY_REFUSAL_REASON}" if error else REPLAY_REFUSAL_REASON` would keep both. Real nights unaffected (variable absent).

N2. `scripts/sample_quiet_predicate_evidence.py:889` — class docstring "Only ``__init__`` is overridden" is now false (`finish` at :929). Stale-doc only.

N3. `quiet_predicate_campaign.py:1327-1328, 1356-1358` (X7). `replay_sessions` is true only for `recorder_kind == "replay"`. Scenario: a real night whose one session carries a power dict lacking the key → summary `REPLAY_NEVER_EVIDENCE`, night refused rc 2, yet `evidence_outcome.recorder_kind` says `powermetrics`. Fail-closed on outcome; the two fields of one document disagree. Matches the dictated shape ("any `replay` → `replay`"); noting only.

N4. `scripts/replay_powermetrics_frames.py:194`. The whole-file pass (≈130 MB) runs after the handlers and before frame 1, and its wall cost is not in the sidecar. Under `auto` it is absorbed by the sleep to `endpoint + K`; under `none` frame 1 is later by the digest wall. Add `source_sha256_wall_s` so the execution lens can bound it. Not a correctness defect.

N5. `quiet_predicate_campaign.py:975-976` (L1). `session.get("power") is None` also exempts a record with NO `power` key. Unreachable from the collector (`"power": None` is initialised at sampler:1048); a hand-made record only — D-161 class, noting.

## (a) C1 text and C2 pin
C1 `campaign.py:775-808`: `except (OSError, ValueError) as exc:` (the C8 widening, itself ruled) → `state = "asserted"` :798 → `reason = f"session rewrite failed: …"` :799 → `try: temporary.unlink(missing_ok=True) except OSError as unlink_exc: reason += f"; stale {temporary.name} not removed: …"` :803-807 → `return False` :808. Verbatim modulo the ruled C8 widening and comment text. R-C1 (`tests/test_quiet_predicate_campaign.py:1928-1956`) patches `campaign.os.replace`→OSError and `Path.unlink`→PermissionError and asserts False / asserted / both fragments / bytes unchanged — the ruled regression. C2 (`test:1441-1452`): under `patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10)`, `attestation_timeout_s(PROTOCOL) == 10` AND `({**PROTOCOL, 'slot_pitch_s': 603}) == 5` — exactly the ruled pair; `attestation_timeout_s`'s body is untouched by the delta (docstring only).

## (b) Production identity for a real night (variable absent)
New branches, each with its variable-absent behaviour:
- `pilot_summary` :953-983: session read before the `rounds.jsonl` read inside one `try`; the `incomplete_interior_support` `continue` moved AFTER the recorder check (:980-983). Real night: sessions say `powermetrics` → nothing appended; order change only. Pinned by X3 (:2158, variable NOT set, refusal from reading alone) and the untouched `UnreadableSessionRecordTests` (session gone → no check).
- L1 :975-979: `power is None` skips; `isinstance(power, dict)` else `recorder_kind = None` → refused. A malformed non-dict, non-None `power` (string, list, `{}`, `0`, `False`) therefore ALWAYS lands in `replay_recorders` → `REPLAY_NEVER_EVIDENCE` → rc 2. No admitting path. Only JSON `null`/absent key is exempt (N5). Pinned: `test_L1_…` :2216 (variable absent via the harness scrub at :521-530; rc 0, `recorder_kind: powermetrics`, refusals 0, envelope 07 excluded alone, retained 11) and the R5 no-key variant now asserting a power DICT (:2146-2152).
- L3 :1098-1112: only under `replay_recorders`; unreachable on a clean real night. Blanks `joules`, `combined_joules`, `interior` per envelope and every report energy key I could enumerate (`sizing_pairs`, `retained_pairs`, `adjacent_pairs`, `adjacent_pair_sd_j`, `pair_sd_j`, `pair_df`, `s_upper_factor`, both `single_envelope_sd_j`, `first_to_last_retained_drift_j`, `pairs_above_3_pair_sd`, `max_abs_delta_j`, `block_two_*`); the two `_role` strings that remain are not numbers.
- `execute` C7 :1299: a new key on EVERY real night's `evidence_envelopes.jsonl` row (`attestation.get("reason")`, never raises). Dictated; pinned :1975-1977. No digest pins that journal.
- `execute` X7 :1322-1328, L2 :1345-1346, X7 :1356-1358: with the variable absent and no `replay_recorder_envelopes`, all three are no-ops; pinned by L1's `outcome == "complete"` / `powermetrics` and R9(b) (:2270-2280, scrubbed copy, 13 children lack the key).
- `record_attestation` :775-808: reachable on a real night only on a failed rewrite; C8's `ValueError` catch pinned by `test_C8_…` (:1897) with a real NaN record.
- Sampler: the delta is ONE hunk (:924-957), all inside `ReplayRecorder`; `PowerRecorder` bytes unchanged; the factory at :1664 picks `PowerRecorder` when the variable is absent.

## (c) Fail-closed verdict
X1: `verdict` :318-385 sets `FAIL` if defects/incomplete/over, else `ESCALATE` if `session_over`, else `PASS`; `markdown` prints `**{status}**` :405; `main` :607 returns `{PASS:0, ESCALATE:3}.get(…, 1)`. X2: `ADMISSIBLE_SLOT` :300-301 = exit 0 / cleanup_proven True / anchor `bounded` / interior True; `SMOKE_EXEMPT_FIELDS` :306 = the anchor pair only, applied only when `smoke` is True; the sole caller passes `smoke=args.smoke` :561, and `kind == "smoke"` ⇔ the same flag :526, so a FULL run's `required` always contains `anchor_status == "bounded"`. A FULL run cannot print PASS with an unresolved anchor: an `unknown`/None anchor is a defect → FAIL before ESCALATE/PASS is considered; a short journal fails `complete`; an abort row lacks `collector_exit` → defect. X5: `BENCH_ATTESTATION_STATES` :315; anything else (`asserted`, None, `unknown`) is a named defect, smoke included (:349-352); artifact text :441-452. Tests X1/X2/X5 (:2496-2665) execute all of it, including rc 3/0/1 through `main`.

## (d) X4
`source_sha256()` :128-145 is its own streaming pass; taken at :194 after the handlers (which only set a flag, so a TERM during the pass cannot interrupt it) and before `source_frames` is consumed; the sidecar at :245-260 is written on both `Stopped` and source-exhausted paths with the same value and `source_sha256_scope` :248. Paths that write no sidecar at all (SIGKILL, a non-`Stopped` exception in the loop) are pre-existing and are what L2 covers. `test_X4_…` builds a >1 MiB source, TERMs mid-file, and checks sidecar == `shasum` == `stream_sha256` == the session's `source_plist_sha256`.

## (e) Forbidden surfaces
The seven paths contain none of: the registration `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v2.json`, the chain `scripts/night_chains/quiet_predicate_evidence.zsh`, or the D-138 four (`powermetrics_fiducial.py`, `uncertainty_evidence.py`, `adapters/powermetrics.py`, `reduce.py`). The sampler is in `HARNESS_PATHS` so each generated night's manifest digest moves — per-run, not a pinned constant; the bench records `manifest_sha256` per run. Clean.

## (f) `ReplayRecorder.finish`
Not a `PowerRecorder` behaviour change: `PowerRecorder.finish` :809 is byte-identical; the override exists only on the replay subclass, is `try: return super().finish() finally: …`, preserves the inherited return and any exception, and fences the sidecar read with `(OSError, ValueError, KeyError, TypeError)`. The collector's `session["power"] = recorder.metadata` :1140 lands after `finish`, so K reaches `session.json`.

## Item verdicts
1 CONFORMS · 2 CONFORMS · 3(i) CONFORMS; 3(ii) DEVIATES from ruling 18's sentence, CONFORMS to addendum 19 (docstring :638-657 states per-slot `6 − gap`, non-compounding, envelope-02 detection, else `start_drift_max_s`; both gaps pinned :1467-1517) · 4 DEVIATES from the ruled assertion, CONFORMS to addendum 19 (:1654-1656 specific list + `joules is None`, `asserted` ×12 on the row) · 5 CONFORMS (:484-489) · 6 CONFORMS (digests `dba7fb7c…eb63` / `da1b28ef…718b` match ruling 18 §1; 191/1 lines; window; zero-match minute; argv shape; provenance 07c) · 7 CONFORMS · 8 CONFORMS.
L1 CONFORMS · L2 CONFORMS (N1) · L3 CONFORMS · L4 CONFORMS (:2366-2470, all four guards + custody-root refusal, real `execute_bench` stopped at `build_plan`) · L5 CONFORMS (via the deviation).
X1 CONFORMS · X2 CONFORMS · X3 CONFORMS · X4 CONFORMS · X5 CONFORMS · X6 CONFORMS (R9 :2233-2280 both halves from copies; harness scrub :521-530) · X7 CONFORMS (recorder_kind from both; `feed` 2.6→3.5 s and delta 0.08→0.25 s with load comments).

## Deviation and NEEDS_RULING
- Deviation (`ReplayRecorder.finish`): HOLDS. L5's dictated shape (K into `session.power.replay` from the sidecar) is unsatisfiable from `__init__` because the sidecar exists only after the feeder exits, which only `finish` observes; confined to the replay class, real-night path untouched (f). The brief's "tests-facing seams only" phrase for the sampler is what the magistrate should amend in the record; fix N2's docstring with it.
- NEEDS_RULING 1 (C3(ii) wording): HOLDS — addendum 19 §1 already adopts the executed text; the docstring and the two-gap regression match it exactly.
- NEEDS_RULING 2 (C4 form): HOLDS — addendum 19 §2 accepted the specific-list form; the committed-red-then-corrected sequence (`1f64e223` → `2b1be7da`) is in the log.

Nothing in this delta blocks; the five NITs are optional polish for a later round, N1 being the only one with a diagnostic cost, and only on the bench.
