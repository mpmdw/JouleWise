# BENCH-REPLAY-START-DRIFT-01 — contract lens (Fable, read-only at 3e299b85)

Scope: `git diff 56ea8ae0..3e299b85` (11 paths), brief 10 (D1–D8, items 1–7), memos 11a/11b, seat report, cold gate #3 Q7 / A269 Q3 replacement-R6 text. Nothing executed; every line cited was read at 3e299b85.

## Verdict: 0 BLOCKER / 2 SHOULD-FIX / 5 NIT. Items 1–7 CONFORM. Deviations 1–5 HOLD.

## Q1 — production identity with the variable absent

New production branches, each with its absent-variable pin:

- `sample_quiet_predicate_evidence.py:1631` `factory = ReplayRecorder if os.environ.get(REPLAY_ENV) else PowerRecorder`; `:1633` passes it to the pre-existing `recorder_factory=` kwarg (`collect` already had it at 56ea8ae0:852, so `collect` itself is unchanged). Pinned: R1 (`main_recorder_factory({})` is `PowerRecorder`, argv has `sudo` + `POWER_METRICS`). Byte-identical otherwise.
- `PowerRecorder.__init__ :735–737` adds `metadata["recorder_kind"]="powermetrics"` — additive key in every production `session.json`. Pinned by R1.
- `execute` `:1191–1193, :1218` `cleanup_wall_s` (additive row key); `:1239–1247` reads the summary status; `:1259–1260` `evidence_outcome.recorder_kind` from `os.environ` (absent ⇒ `"powermetrics"`). Pinned by R5-counterfactual (12 × `powermetrics` ⇒ rc 0 / `complete` / `SPREAD_RECORDED`) and R9 (13 child envs lack the key).
- `pilot_summary :928–930` — **behaviour changes for a real night** (S1 below). Not pinned for the reachable case.
- `run_night._chain_environment :591–596` — raise only when present; absent path unchanged (R4 second half).
- `ReplayRecorder`, `stream_sha256`, `replay_*` helpers (`:837–928`) are dead code when absent.

## Q2 — fail-closed set

ARM: `_chain_environment` raises `:591`; called at arm via `night_agent_install.reservation_input_digests :711` → `reservation_input_paths :626`, and at run `:847`. R4 pins raise + spelling equality; R8 pins the launchd templates' environment key sets BY ENUMERATION (`test_run_night :3020`) and the wrapper's export set (`:4814`) plus the tracked chain text — no free-form slot exists. Real, reachable, pinned.
RUN: `session.power.recorder_kind` (pinned R2/R5), `evidence_outcome.recorder_kind :1259` (R5), plan-id prefix and `~/night-bench/` root (`bench_replay_start_drift.py :389–394`) — these two are driver constants with no regression (N3). The `:393` `CUSTODY_ROOT_FORBIDDEN` guard is tautological (the root is always built under `BENCH_ROOT`).
HARVEST: `pilot_summary :928–1057` + `execute :1243–1247` refusal, rc 2 via `:1278`. Pinned R5 (three variants), rows preserved.
Courier / `night-results`: the driver calls `campaign.execute` directly (`:416`); it never enters `run_night`, never installs a label, never writes under `~/night-custody/`. `_push_results` (`run_night :1082`) is reachable only from `run_night`'s own session, which cannot be launched under the variable. No path found. (Deliberate manual `run_night courier` against a `~/night-bench` plan is the only route, and it would push a `refused` outcome under a `bench-replay-` id — not evidence.)

## Q3 — the ruled text

REAL `execute` (`:416`, the production function, schedule/abort/attestation intact), REAL collector (`main()` → `collect` unchanged), injected recorder: `ReplayRecorder` overrides `__init__` only (`:886–928`); `start/request_stop/finish` are inherited. Archived plist read in place, digested by streaming (`:837`), never copied. NO SUDO: every `sudo` in the reachable tree is (a) `power_argv :199–203` — bypassed because `ReplayRecorder` replaces `self.argv`; (b) `campaign.network_time_argv :311–313` — both `SUDO` and `SYSTEMSETUP` rebound to the stub (`:415`), so argv is `(stub, "-n", stub, -setusingnetworktime, off|on)`; the stub is mode 100755 and refuses without the variable (R6, executed as a subprocess). `request_stop` uses `os.kill` (`:786/:802`); `cleanup_groups` uses `killpg`; `attest_network_time` runs `/usr/bin/log` (`LOG :34`, not rebound) — so D3 holds: the real `log show` runs in the gap at `:1207–1210` with `timeout=attestation_timeout_s(protocol)` and its wall cost is journaled. No measurement: frames are archived bytes. Never labelled evidence: three markers + summary override + refusal. The restore in `execute`'s `finally` runs while the variable is still set (the driver restores `os.environ` only after `execute` returns, `:417–423`), so the ON stub answers.

## Q4 — label shift (D4, Deviation 5)

`shift_frame :95–102` rewrites ONLY the `<key>timestamp</key><date>…</date>` group; K is computed once at frame 1 (`:192`, `int(math.ceil(...))`) and applied to every frame; `--label-shift none` returns the frame untouched (`:97`). R3-auto pins: K integer, every label = archived + K, date-blanked streams byte-identical. Per slot: `source_plist_sha256`/`source_session_sha256` in `session.power.replay` (`:915–920`), `written_stream_sha256`, `label_shift_s`, `label_shift_basis` in the sidecar (`:223–237`), quoted per slot in the artifact (`:340–344`). Mistaken for evidence? Only out-of-band marks distinguish an `auto` plist (N1), but no reader of `envelope-NN/session.json` exists outside `pilot_summary` (grep: none in `joulewise/` or `scripts/`), and that reader refuses.

## Q5 — `cleanup_wall_s`

Additive only: one new key on the row dict (`:1218`) and the journal line; no consumer enumerates row keys (grep: `run_night :1025` only lists the file as an artifact; no test pins the key set). Mirrors `network_time_attestation_wall_s`. Additive.

## Q6 — registration and chain

The 11-path delta touches neither `scripts/night_chains/**`, the registration JSON, `night_gate.py`, nor `gen_evidence_night.py`; `QPE01_PILOT_REGISTRATION_SHA256` is untouched and quoted into the artifact (`:438`). The driver loads via `campaign.validate_protocol(campaign.frozen_protocol(), chain_digest)` (`:231–232`); the smoke re-runs `cadence_fields` on the scaled copy (`:238`). No new exclusion reason (`REPLAY_NEVER_EVIDENCE` is a status; `:56–61`).

## Findings

**S1 (SHOULD-FIX) — a REAL night with one `power: null` session is refused as a "replay".** `collect` initialises `"power": None` (`sampler :1015`) and only sets `session["power"] = recorder.metadata` when a recorder was constructed (`:1107`); the provenance-refusal path writes `session.json` at `:1031` with `power: null` and returns. At `pilot_summary :928`, `(None or {}).get("recorder_kind")` is `None ≠ "powermetrics"`, so `replay_recorders` is non-empty and the WHOLE night becomes `REPLAY_NEVER_EVIDENCE`, `retained: []`, `refused`/`replay_recorder`, rc 2 — with `evidence_outcome.recorder_kind: "powermetrics"` on the same document. Scenario: envelope 07's collector finds the control record unreadable (`network_time_provenance :275–283`); at 56ea8ae0 that envelope was `collect_error`-excluded and the other eleven reached a spread verdict (`partial`, rc 0); at 3e299b85 the night is discarded under a false reason. Fail-closed direction, narrow trigger, but an unpinned production behaviour change with a false record. Cure: refuse only when `power` is a dict lacking/contradicting the key (`power is None` ⇒ no recorder ran ⇒ fall through to the existing exclusions); regression: one `power: null` session among twelve ⇒ status not `REPLAY_NEVER_EVIDENCE`. Note the brief's D6 wording and R5's "no key ⇒ refuse" are what the seat implemented; this needs a magistrate call, not a seat fault.

**S2 (SHOULD-FIX) — the harvest refusal keys on readable sessions only.** `:917–919` `continue`s before the `:928` check, so a replay night whose every `session.json` is missing/unparseable yields `replay_recorders == []`, an ordinary INCONCLUSIVE summary, outcome `partial`, rc 0 — with `evidence_outcome.recorder_kind: "replay"` as the only tell. Scenario: feeder crashes on a malformed archive so every collector is killed at `envelope_s + 30` before writing its session. Cure: in `execute :1243`, also refuse when `os.environ.get(harness.REPLAY_ENV)` (the RUN marker becomes a refusal point, independent of session readability); regression: replay env set + zero readable sessions ⇒ rc 2.

**N1** — under `auto`, the written plist carries live-looking dates and no in-band marker; provenance is entirely out-of-band (sidecar/session/root). Accept (D4 forbids other byte changes); say so in the artifact.
**N2** — `:1004–1005` `envelopes[*].joules` and `sizing_pairs` survive the `:1032` override; "no reader can lift a number" (`:1033–1036`) overstates. Reword or blank `sizing_pairs`.
**N3** — driver guards (`require_clean_head`, `require_no_night_agent :132`, plan-id prefix, bench root, `--smoke` name refusal) have no regressions; R7 covers `verdict` only.
**N4** — under `auto`, `session.power.replay.label_shift_s` is `null` (`:920–926`); K lives only in the sidecar. Fine for the artifact; a session-only reader lacks K.
**N5** — the run-side raise at `run_night :847` sits inside `with stdout_path.open("xb")` and `_run_chain_once` catches only `OSError` on Popen (`:859`); a desk `run_night run` under the variable tracebacks with `chain.stdout.log` already created. Unreachable from an armed night (R8), so cosmetic.

## Items 1–7

1 CONFORMS (seam is argv-only; `__init__` alone). 2 CONFORMS (streaming, NUL split, per-`elapsed_ns` pacing, flush, hold-until-TERM, exit 0, `none|auto`). 3 CONFORMS (variable-gated, empty stdout + exit 2, argv shape checked). 4 CONFORMS (clean-head + sha, label guard, `NightPlan` DIAGNOSTIC_NO_PACK under `~/night-bench/`, `frozen_protocol`+`validate_protocol`, rebind, real `execute`, json + markdown, 0.5 s + session figure + escalation, `--smoke`). 5 CONFORMS (raise, never pop; both pins by enumeration). 6 CONFORMS (status override, `retained: []`, `s_upper: null`, rc 2 `replay_recorder`, rows kept, no new exclusion reason) — subject to S1/S2. 7 CONFORMS (R1–R9 present with executed counterfactuals; R3 runs the feeder as a real subprocess).

## Deviations 1–5

1 HOLD — rebinding `SYSTEMSETUP` alone would exec `/usr/bin/sudo` (`:313`); both rebound is the only reading of D2 consistent with "no sudo". 2 HOLD — additive, D8-required. 3 HOLD — fix commits are in-lane and the `pgrep` cure is correct (exit 1 ⇒ 0, other ⇒ null). 4 HOLD — `docs/` outside WRITE_SCOPE; ruled name refused for smokes. 5 HOLD — the mode must cross the executor→collector boundary; one additional variable, validated to `none|auto` (`:891–893`), recorded per slot.

Seat recommendation to run the full replay under `--label-shift auto` is consistent with D4's rule (smoke anchors unresolved under both modes at 60 s; discrimination only at 600 s) — the artifact must state the mode and K per slot, which `:340–344` does.
