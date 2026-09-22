# BENCH-REPLAY-START-DRIFT-01 — EXECUTION LENS (Opus, worktree `JouleWise-wt-a267-review3` @ `3e299b85`)

Delta `56ea8ae0..3e299b85`. Everything below was executed this session on this machine (load 5–8, another suite running; drift figures are conservative per D8). Tree left clean; nothing committed or pushed.

## BLOCKER

**B1 — a chain-pass / session-fail split exits 0 and prints `PASS`.** `scripts/bench_replay_start_drift.py:311-312` sets `status = "PASS"` and then records `escalate` as a *separate boolean*; `:343` renders the headline `**PASS**`; `:510` returns `0` whenever `status == "PASS"`. Brief D8 is explicit: "a chain-pass/session-fail split is ESCALATED, never passed."
*This is not hypothetical — my live smoke hit it.* `max(session start_drift_s) = 0.734 s`, slots 1 and 3 over the 0.5 s session bar, `escalate_chain_pass_session_fail: true`, and the driver still printed `"status": "PASS"` and exited **0**. The full run is launched detached and unattended (D7); a magistrate reading exit code + headline proceeds to arm on a split.
Command: `python3 -B scripts/bench_replay_start_drift.py --archive /Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922 --smoke --label-shift auto` → see table below.
Fix shape: a third status value (`ESCALATE`) that is neither PASS nor FAIL, carried into `markdown()`'s headline and into `main()`'s return code (non-zero).

**B2 — `verdict()` admits slots whose finalisation tail never happened.** `verdict()` (`:302-322`) reads only `chain_start_drift_s` / `session_start_drift_s`. It never consults `collector_exit`, `cleanup_proven`, `anchor_status` or `interior_complete_support`, all of which `slot_rows()` already collects. Executed probe (`bench.verdict` on rows with `collector_exit=1` on slot 5, `cleanup_proven=False` on slot 6, `anchor_status="unknown"` and `interior_complete_support=False` on all twelve) → `status = PASS`, `escalate = False`.
Why blocker, not nit: in **all three slots of my live smoke** the anchor was `unknown` / `clock_fit_span_insufficient` and `interior_complete_support` was `False` — `align_frames` returned nothing, so the per-round integration and interior reduction, the expensive part of the tail the bench exists to time, **did not run**. The bench returned PASS anyway. Whether `auto` resolves the anchor at the full 600 s envelope is untested; if it does not, the full run yields a PASS that systematically under-measures the quantity the 0.5 s bar is about. The verdict must require every slot `collector_exit == 0`, `cleanup_proven`, `anchor_status == "bounded"` and `interior_complete_support`, else FAIL/ESCALATE.

## SHOULD-FIX

**S1 — the harvest fail-closed point fails OPEN when an envelope's journal is unreadable.** `joulewise/quiet_predicate_campaign.py:928` reads `recorder_kind` *after* the `try` at `:915-919`, which `continue`s on any `OSError`/`ValueError` from `session.json` **or `rounds.jsonl`**. Executed (`/tmp/replay-lens/probe_failopen.py`): twelve sessions each carrying `recorder_kind: "replay"`, `rounds.jsonl` absent ⇒ `status='INCONCLUSIVE'`, `evidence_status='PROVISIONAL'`, no `replay_recorder_envelopes`, so `execute` would **not** refuse (rc 0, outcome `complete`) and `summary.md` reads "QPE-01 pilot (PROVISIONAL, descriptive)". Control with `rounds.jsonl` present ⇒ `REPLAY_NEVER_EVIDENCE`. Bound honestly: it needs *every* envelope to fail the read, and then nothing is retained anyway — but the claimed ordering is not what the code does. Fix: read `power.recorder_kind` before the try, or append in the `except` branch too.

**S2 — the feeder's sidecar `source_sha256` is a partial digest under its normal exit path.** `scripts/replay_powermetrics_frames.py:133` folds chunks into `source_digest` only as they are read; on SIGTERM (the normal stop) the generator is abandoned mid-file, and `:225` writes that partial digest under the name `source_sha256`. Live proof, envelope-01 of the seat's own `auto` smoke: sidecar `source_sha256 = ee01f351…` vs the true full-file digest in `session.json` `power.replay.source_plist_sha256 = ef4429b4…`. A provenance field that names a file but digests a prefix will be read as the file's digest. Rename it (`source_bytes_read_sha256`) or record `bytes_read` beside it.

**S3 — network time is never actually off, so the bench attests a different log.** The stub toggles nothing, so `timed` keeps applying corrections; my slot 2 came back `slew_attested` — a real, live slew, not reproducible in a night. The artifact quotes these attestation walls as the first measurement of the A267 B1 residual; it must say they are live-log-with-slews costs and that `slew_attested` slots in the full run are expected, not a defect.

**S4 — `test_R9…` (tests/test_quiet_predicate_campaign.py:1962) is green only because the ambient shell is clean.** Run from a shell carrying the switch the whole module goes red: `env EVIDENCE_POWER_RECORDER_REPLAY=… python3 -B -m unittest …test_R9_no_child_of_an_ordinary_night_ever_sees_the_replay_switch` → `FAIL … 'EVIDENCE_POWER_RECORDER_REPLAY' unexpectedly found`. The setup never creates the condition it asserts against, so it can only fail for the wrong reason. Pop the key under `patch.dict` and assert the real property (`execute` propagates it; `_chain_environment` is the gate).

## NIT

- `evidence_outcome.json.recorder_kind` (`campaign.py:1257`) is derived from the *executor's* `os.environ`, not from the sessions it just read; the two can disagree (the summary still refuses, so it is not load-bearing).
- `tests/test_sample_quiet_predicate_evidence.py:1682,1721`: `feed(seconds=2.6)` + `assertAlmostEqual(delta, …, delta=0.08)` are wall-clock races; under today's load they are one scheduler hiccup from red.

## Kill ledger (mutate → red tail → `git checkout --` → restore verified byte-identical)

| id | mutation | tail | red |
| --- | --- | --- | --- |
| R1 | `os.environ.get(REPLAY_ENV)` → `…get(REPLAY_ENV, "/tmp/x")` (seam defaulted on) | `…SeamTests` | FAIL `test_R1_without_the_variable…` |
| R2 | `ReplayRecorder.argv` prefixed with `"sudo"` | `…SeamTests` | FAIL `test_R2_…names_no_privilege` |
| R3a | feeder `since_first_ns += elapsed_ns` → `… // 2` | `…SeamTests` | FAIL `test_R3_…archived_cadence` |
| R3b | feeder `shift_s = int(math.ceil(…))` → `shift_s = 0` | `…SeamTests` | FAIL `test_R3_auto_shifts…` |
| R4 | `if REPLAY_RECORDER_ENV in os.environ:` → `if False and …` | `test_run_night.NightProbeTests` | FAIL `test_R4_an_inherited…` |
| R5 | `!= RECORDER_KIND_PRODUCTION` → `not in (PRODUCTION, REPLAY)` | `…FailClosedTests` | FAIL `test_R5_a_replay_recorder_refuses…` |
| R6 | stub `if not os.environ.get(REPLAY_ENV):` → `if False:` | `…FailClosedTests` | FAIL `test_R6_…refuses_without_the_variable` |
| R7 | `START_DRIFT_BAR_S = 0.5` → `2.0` | `…FailClosedTests` | FAIL `test_R7_…single_slot_over_the_bar` |

Green tail after restore, all three classes → **Ran 30 tests in 35.9 s, OK**; `git status --short` empty.

## Smoke, executed for real (mine, not the seat's)

`launchctl list | grep joulewise.night` empty before start. `~/night-bench/bench-replay-20260922T193512Z`, `--label-shift auto`, wall **227.7 s**, protocol 60/80/5/3, cleanup budget 15 s, attestation timeout 5 s. Machine: start `load 5.46 4.84 3.86`, `pgrep claude` 1; end `load 8.64 6.65 4.84`, `pgrep claude` 0.

| slot | chain drift s | session drift s | exit | cleanup proven / wall s | attestation / wall s | anchor | tail s | frames | K s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **0.479** | **0.734** | 0 | True / 0.023 | authenticated / 0.846 | unknown (`clock_fit_span_insufficient`) | 0.920 | 253 | 36497 |
| 2 | 0.005 | 0.379 | 0 | True / 0.018 | **slew_attested** / 1.009 | unknown (same) | 1.439 | 254 | 35969 |
| 3 | 0.131 | **0.547** | 0 | True / 0.025 | authenticated / 0.772 | unknown (same) | 1.158 | 253 | 35448 |

`verdict.status = PASS` (chain max 0.479 s — 0.021 s under the bar) but `escalate_chain_pass_session_fail = **true**`, `session_slots_over_bar = [1, 3]`, `max_session = 0.734 s`; process exit **0** (B1). Far worse than the seat's smoke (chain 0.149/0.079/0.112): same code, heavier machine. The full run's margin is thin.

Markers: `summary.status = evidence_status = REPLAY_NEVER_EVIDENCE`, `retained: []`, `s_upper: null`; outcome `refused` / `replay_recorder`, rc **2**; `evidence_outcome.recorder_kind = "replay"`; every slot `recorder_kind = "replay"`, `recorder_argv_0 = …/python3.14`; `network_time_restored: true`. Control argv = `[…/bench_replay_systemsetup_stub.py, -n, …/bench_replay_systemsetup_stub.py, -setusingnetworktime, off]` — **names neither `/usr/bin/sudo` nor `/usr/sbin/systemsetup`**. Confirmed.

**Bench root inspection.** `~/night-bench/` = 137 MB, four bench-replay dirs. **No `courier.sent`, no `result.json`, no `night-results`** anywhere; `~/night-results` does not exist; nothing written under `~/night-custody/`. Each run carries `night/evidence/summary.{json,md}`, `evidence_outcome.json`, `refusal.json` — structurally a night — but all four self-label: `summary.md` opens `# QPE-01 REPLAY_NEVER_EVIDENCE`, `refusal.json` says `evidence chain refused: replay_recorder`. No tool globs `~/night-*`; the only roots in the tree are `~/night-custody` literals. Clean.

## Fail-closed probes (my own fakes)

`/tmp/replay-lens/probe_failclosed.py`. `_chain_environment` on a fake ORDINARY-night plan: variable absent → normal env (`NIGHT_PLAN_ID` set, key absent); set → `ValueError: EVIDENCE_POWER_RECORDER_REPLAY is set in this environment…` — raises, never pops. `pilot_summary` on my own two-envelope fakes: `recorder_kind` **absent** → `REPLAY_NEVER_EVIDENCE` / `retained: []` / `s_upper: None` / `summary.md` = `# QPE-01 REPLAY_NEVER_EVIDENCE`; `"replay"` → identical refusal; `"powermetrics"` control → `INCONCLUSIVE` / `PROVISIONAL`. Both refuse.

## Production identity (variable absent)

`git archive 56ea8ae0 | tar -x -C /tmp/base56ea8ae0`; `FrozenExecutorTests().exercise()` run end to end in each tree, artifacts diffed key-by-key. Both: rc 0, outcome `complete`, `SPREAD_RECORDED`, 0 refusals. Differing paths, **all** of them:

| artifact | key | base → head |
| --- | --- | --- |
| `evidence_outcome.json` | `recorder_kind` | absent → `"powermetrics"` |
| `evidence_envelopes.jsonl` (×12) | `cleanup_wall_s` | absent → `0.0` |
| `summary.json` envelopes (×12) | `cleanup_wall_s` | absent → `0.0` |
| `summary.json` | `whole_campaign_observer_cpu_s` | 0.014775 → 0.015144 (real CPU, nondeterministic) |
| twelve `session.json` | `power.recorder_kind` | absent → `"powermetrics"` |
| twelve `session.json` | `network_time_provenance.attestation.session_sha256_before` | changed — *consequence* of the new key being in the pre-attestation bytes, not an independent change |

Exactly the two expected keys, plus one nondeterministic CPU measurement and one derived digest. **Production identity holds.**
