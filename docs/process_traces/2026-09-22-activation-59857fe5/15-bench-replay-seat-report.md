# BENCH-REPLAY-START-DRIFT-01 — implementation seat report

Worktree `/Users/edr/code/JouleWise-wt-replay`, branch `feat/2026-09-22-bench-replay-start-drift`,
base `56ea8ae0`, head `3e299b85`, tree CLEAN. Nine commits, one per item plus two fixes
found by running the smoke.

## Per item (file:line at head)

1. **Sampler seam.** `scripts/sample_quiet_predicate_evidence.py`: `REPLAY_ENV`/
   `REPLAY_LABEL_SHIFT_ENV`/`REPLAY_FEEDER`/`RECORDER_KIND_*` :105–112;
   `PowerRecorder.metadata["recorder_kind"] = "powermetrics"` :737; helpers
   `stream_sha256` :837, `replay_envelope_index` :846 (slot i ↔ archived envelope i, D5,
   read off the output name), `replay_source_dir` :861; `class ReplayRecorder(PowerRecorder)`
   :886 overriding `__init__` **alone**; `main()` selection :1631.
2. **Feeder.** `scripts/replay_powermetrics_frames.py` (new). 1 MiB streaming reads, NUL split,
   one frame per archived `elapsed_ns` paced from the first write, flush per frame,
   `--label-shift none|auto`, hold-until-SIGTERM, exit 0 on SIGTERM, sidecar carrying
   mode/K/both digests/frame count/cadence.
3. **Stub.** `scripts/bench_replay_systemsetup_stub.py` (new). Prints the *imported*
   `EXPECTED_NETWORK_TIME_OFF_STDOUT` only when `REPLAY_ENV` is set; otherwise empty stdout,
   exit 2. Argv shape checked.
4. **Driver.** `scripts/bench_replay_start_drift.py` (new): `require_clean_head` :121,
   `require_no_night_agent` :132, `stage_custody` :188 (renders a REAL sealed wrapper+manifest
   through `gen_evidence_night`, so the covariate recorder's `verify_environment` passes on
   production terms), `SMOKE_PROTOCOL` :100, `verdict` :291, `markdown` :325, `execute_bench` :387.
5. **Arm refusal.** `scripts/run_night.py`: `REPLAY_RECORDER_ENV` :72; `_chain_environment`
   **raises** :591–596 (never pops).
6. **Harvest refusal.** `joulewise/quiet_predicate_campaign.py`: `REPLAY_NEVER_EVIDENCE` /
   `REPLAY_REFUSAL_REASON` :60–61; per-session check :928; report override :1038 (`status`,
   `evidence_status`, `retained: []`, `s_upper: null`, `replay_recorder_envelopes`) and a
   replacement `summary.md`; `execute` refusal :1247; `evidence_outcome.json.recorder_kind` :1259;
   **new** `cleanup_wall_s` :1193/:1218 (D8 requires per-slot cleanup wall and nothing recorded it).
7. **Regressions.** `tests/test_sample_quiet_predicate_evidence.py:1593` (R1–R3, 6 tests);
   `tests/test_quiet_predicate_campaign.py:1887` (R5, R6, R7, R9, 8 tests);
   `tests/test_run_night.py:2989` (R4), `:3020` + `:4814` (R8).
   `tests/fixtures/replay/envelope-01/` = a 3-frame **synthetic** plist (5154 B) + session.json,
   built from the archived frame structure; no archived bytes copied.

## Regressions and their executed kills

- **R1** absent ⇒ `main` hands `collect` `PowerRecorder`; argv holds `sudo` + `POWER_METRICS`;
  `recorder_kind == "powermetrics"`; no `replay` key. **Kill:** the same selection with the
  variable present returns `ReplayRecorder` (a defaulted-on seam therefore fails R1).
- **R2** set ⇒ argv is `[python, -B, feeder, …]`, no `sudo`/`powermetrics` token anywhere; both
  source digests recorded. **Kill:** a slot whose archived envelope is absent refuses (D5).
- **R3** feeder as a REAL subprocess over the fixture: SIGTERM → exit 0; `none` → output bytes
  identical to the source and `written_stream_sha256 == source_sha256`; write deltas equal the
  archived `elapsed_ns` within 80 ms; `PowerRecorder`'s own `parse_frames` reads it back (3 frames,
  no dropped tail). `auto` → every label shifted by one integer K and, with the dates blanked,
  the streams are byte-identical. **Kill:** the unshifted first label is > 2 s from now, so the
  live bracket cannot contain it.
- **R4** `_chain_environment` raises, message names the variable. **Kill (executed):** popping
  instead returns a usable environment with no signal. Plus `run_night.REPLAY_RECORDER_ENV ==
  sampler.REPLAY_ENV` pinned (a drifted spelling would disarm the refusal).
- **R5** scaled end-to-end `execute`, stub collector writing `recorder_kind: "replay"` ⇒
  `REPLAY_NEVER_EVIDENCE` (status and evidence_status), `retained == []`, `s_upper is None`,
  twelve `replay_recorder_envelopes`, outcome `refused` / `replay_recorder`,
  `evidence_outcome.recorder_kind == "replay"`, rc 2, one refusal file, and all twelve
  `evidence_envelopes.jsonl` rows present with `start_drift_s`, `cleanup_wall_s`,
  `network_time_attestation_wall_s`. **Kills:** the same night under `"powermetrics"` → rc 0,
  `complete`, `SPREAD_RECORDED`, retained 12; a session with **no** `recorder_kind` also refuses.
- **R6** stub without the variable → rc 2, stdout `""`, and the production
  `establish_network_time_off` (both executable constants rebound, as the driver rebinds them)
  raises with `off.exit_code == 2`, `off.stdout == ""`. **Kill:** with the variable, the same
  argv prints the imported comparator's exact line and exits 0.
- **R7** `verdict` FAILs on one 0.6 s row (`slots_over_bar == [7]`). **Kill (executed):** the same
  journal against `bar_s=2` PASSes. Plus chain-pass/session-fail ⇒ `escalate…` true, and a
  journal short of the registered slot count never passes.
- **R8** the sealed wrapper's export set and each launchd template's environment set are pinned
  **by enumeration**; neither carries the key, and the tracked zsh chain does not either.
- **R9** all 13 child environments of an ordinary night lack the key.

## Smoke, executed for real (protocol copy per D7: envelope 60 s, pitch 80 s, settle 5 s, 3 slots)

Run `~/night-bench/bench-replay-20260922T191902Z`, `--label-shift none`, wall 227 s, machine
`pgrep claude` 0 at start and end, load averages ~3.7.

| slot | chain drift s | session drift s | exit | cleanup proven / wall s | attestation / wall s | anchor | tail s | frames |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.252 | 0.370 | 0 | True / 0.033 | authenticated / 0.716 | unknown (`clock_fit_span_insufficient`) | 0.795 | 257 |
| 2 | 0.059 | 0.173 | 0 | True / 0.016 | authenticated / 0.804 | unknown (same) | 0.714 | 258 |
| 3 | 0.091 | 0.204 | 0 | True / 0.015 | authenticated / 0.683 | unknown (same) | 0.758 | 257 |

**Verdict PASS** — `max(chain start_drift_s) = 0.252 s ≤ 0.5 s over 3/3 slots`;
`max(session) = 0.370 s ≤ 0.5 s`; no chain-pass/session-fail split.
`summary.status = summary.evidence_status = REPLAY_NEVER_EVIDENCE`, `retained: []`,
`s_upper: null`; outcome `refused`, **rc 2**, `evidence_outcome.recorder_kind = "replay"`,
`network_time_restored: true`. The control record's argv is
`[…/bench_replay_systemsetup_stub.py, -n, …/bench_replay_systemsetup_stub.py,
-setusingnetworktime, off]` — it names neither `/usr/bin/sudo` nor `/usr/sbin/systemsetup`,
so the receipt is self-identifying as a bench record.

Every anchor was unresolved, so per instruction the smoke was repeated under `--label-shift auto`
(`~/night-bench/bench-replay-20260922T192315Z`): chain 0.149 / 0.079 / 0.112 s,
session 0.275 / 0.196 / 0.230 s, attestation authenticated 0.694 / 0.911 / 0.799 s, PASS,
same REPLAY_NEVER_EVIDENCE / refused / rc 2 markers. K = 35779 / 35251 / 34730 s, three
**distinct** source plist digests (D5 confirmed live). **The anchor stayed `unknown` with detail
`clock_fit_span_insufficient` in all three slots under both modes** — at a 60 s envelope the
native support (~67 s) is too short for the rate fit, so the smoke cannot discriminate 11b's F1
either way. At the full 600 s envelope it will: `none` should give
`rate_aware_native_set_empty` (F1), `auto` should resolve `bounded`. **Recommendation to the
magistrate: run the full replay with `--label-shift auto`**, and expect `label_shift_s` ≈ the
age of the archive in whole seconds, recorded per slot.

Attestation cost — the B1 residual's first measurement — is 0.68–0.91 s against its 5 s timeout;
teardown is 0.015–0.033 s against a 15 s budget.

## Exit contract

- `python3 -B -m unittest tests.test_uncertainty_evidence tests.test_sample_quiet_predicate_evidence
  tests.test_quiet_predicate_campaign tests.test_run_night` → `Ran 479 tests in 246.386s` / **OK**.
- `python3 -B scripts/quick_suite.py --tier quick --workers 4` →
  `QUICK SUMMARY tier=quick modules=153 excluded=92 failures=3 seconds=85.958 result=FAIL`,
  failing `tests.test_calibration_ledger` (1), `tests.test_calibration_live_three_window` (13),
  `tests.test_write_derivation_night_inputs` (8). **These are PRE-EXISTING and not this lane's.**
  Verified by extracting `56ea8ae0` with `git archive` into `/tmp` and running those three
  modules: identical failing tests, identical counts (1 / 13 / 8), identical signature
  `acceptance_artifact_stale` on `calibration_acceptance_d079_v2_n17_r6.json` — the unlanded r7
  re-issue (D-138). Delta from base: zero. (A whole-suite base run is not comparable: an
  extracted tree is not a git checkout, so 13 further modules fail there for that reason alone.)

## Deviations

1. **Both `SUDO` and `SYSTEMSETUP` are rebound, not `SYSTEMSETUP` alone (D2).** `network_time_argv`
   returns `(SUDO, "-n", SYSTEMSETUP, …)`, so rebinding only `SYSTEMSETUP` would execute the real
   `/usr/bin/sudo` — forbidden by this lane's hard limits and outside the NOPASSWD slice, which
   would refuse the night. Binding both also leaves a control record whose argv names neither
   privileged path. No production branch added; the module's documented rebinding seam is used.
2. **`cleanup_wall_s` added to each envelope row** in `execute` (not in the item list). D8 requires
   per-slot cleanup wall and nothing recorded it; it mirrors the existing
   `network_time_attestation_wall_s` precedent.
3. **Two follow-up fix commits** (`4c1479b5`, `3e299b85`) rather than amendments, per the no-amend
   limit: macOS `pgrep` has no `-c` (the census silently reported 0 for every reading), and the
   bench environment must carry `NIGHT_DIR` or the covariate recorder refuses and `execute` ends
   the night after slot 01 — found by running the smoke, which is why the smoke ran three times
   (first attempt: 1 slot, chain 0.212 s / session 0.331 s, then the two reported above).
4. **Artifact path.** `docs/` is outside WRITE_SCOPE, so the driver defaults its outputs into the
   bench custody root and takes `--artifact` / `--raw`; `--smoke` refuses any name ending
   `-bench-replay-start-drift.md` (D7). The magistrate supplies the ruled path for the full run.
5. **`--label-shift` is a driver flag defaulting to `none`**, passed to the collector through
   `EVIDENCE_POWER_RECORDER_REPLAY_LABEL_SHIFT`; D1 named only the one variable, but the mode has
   to cross the same executor→collector boundary and K must be recorded per slot.

## NEEDS_RULING

None.

## Unfinished / notes for the magistrate

- The FULL replay was not run (correct: it runs at the PR's merge sha, P7.1). Command shape:
  `python3 -B scripts/bench_replay_start_drift.py --archive /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922
  --label-shift auto --expect-sha <merge> --transaction-merge <D-138 merge>
  --artifact docs/process_traces/2026-09-22-activation-59857fe5/<nn>-bench-replay-start-drift.md
  --raw <…>/bench-replay.json` (≈ 2 h 14 m, ~1.6 GB of replayed plists under `~/night-bench/`,
  deletable after the artifact lands).
- Unrelated flake: `LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child`
  failed once under module contention (`-9 != -15`); passes alone and in the exit-contract run.
- Corpus replay 38/38 at the PR head (brief's exit contract) was **not** run by this seat — it
  belongs at the PR head after the rebase onto the transaction merge.
