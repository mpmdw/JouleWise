# 21i — HARVEST RECORD: rehearsal-20260909 (headless activation 628c2eed; NIGHT-REHEARSAL-01 evidence)

Written 1788950400 2026-09-09 ~03:40 PDT by activation `628c2eed-acf6-483d-998e-31c91f36e6d4` (pid 82637, watchdog attempt 5,
spawned 03:33:01 PDT, events.jsonl seq 22–23; every events.jsonl sequence cited in this record is in the read-only excerpt
`night-harvest/watchdog-events-excerpt.txt`, Opus review 06 S4). Every fact below is read from a captured artifact under
`21b-rehearsal-20260909-bench/night-harvest/` (byte copies of the custody root, `SHA256SUMS` alongside; the three `*.log` copies are force-added past the `docs/process_traces/**/*.log` ignore rule — fidelity refuter 05 F1); nothing is restated from memory.

## What fired
- Plan `rehearsal-20260909` (v2, `REHEARSAL_STUB`, t0 1788947760 = 02:56:00 PDT, window 900 s, root
  `/private/tmp/joulewise-rehearsal-20260909-checkout` @ `ae8f074f`): byte copy `night_plan.json`.
- `night.log`: driver started 02:56:00.988; `night gate verdict=REFUSED` 02:56:01; `night result verdict=REHEARSAL_ONLY` 02:56:03;
  durable record pushed `night-results/20260909` 02:56:10; courier attempt 1 heartbeat+sent 02:57:33; second push 02:57:35.
  No 07:00 dead-man line (agents were installed 01:57 on 09-09, so the R-7 case did not apply — see NIGHT_HANDBACK §Purpose).
- `refusal.json` is ABSENT BY DESIGN: the driver writes it only for a non-rehearsal refused gate (06 N5). `night.log`'s harvest digest
  `28ee7ad6…` differs from the `f894b3a4…` recorded inside `night-result.json`: the result digest covers the FIRST TWO lines of
  `night.log`; four lines were appended after the result was sealed, at `2026-09-09T02:56:03.367167-07:00`,
  `2026-09-09T02:56:10.980604-07:00`, `2026-09-09T02:57:33.117809-07:00`, and `2026-09-09T02:57:35.070205-07:00` (06 N4).
- `night-result.json`: verdict `REHEARSAL_ONLY`, `chain_exit_code` 0, `census_count` 1, `census_hits` [], `receipt_class`
  `REHEARSAL_STUB`, `aborted_reason` null. `night-chain.started` pid/pgid 82053; `night-chain.exited` rc 0; `night-chain.stdout.log`
  `REHEARSAL`; `night-censuses.jsonl` one clean census (pgrep exit 1, empty stdout).
- launchd-started, not shell-started: `night-launchd.night.out` is the courier's transcript written by the `com.joulewise.night` agent.
- Results branch: `night-results/20260909` on origin at `a84e0f7f` (parent `d4d494ec`, both "record night 20260909" on top of main
  `83ab38ed`); verified by `git ls-remote` at harvest (`pre-uninstall-observations.txt`) and equal to the results-clone HEAD with a
  clean tree (`removal-output.txt`).
- Courier: `night-courier.sent` message id `1a08599a4ff4d005`, thread `1a08599a4ff4d005`, sent epoch 1788947852, to Ed's address,
  courier pid 82210; `night-courier.json` attempted 1 / heartbeat_seen true / sent true. The courier also wrote
  `night-courier.finding.md` (root cause + cure options, read-only analysis of the stub checkout).
- Watchdog side: the courier process was counted by the production census inside the plan span → transition seq 20
  FENCED→HOLD_CENSUS (1788947872) → seq 21 back to FENCED (1788948174) once it exited; relayed to Ed as the launch notice
  (`notice_pending` id `transition-20-hold_census`; launch email `1a085bc57dbfabbe` on thread `1a0800cdb282c3f1`; `notice.ack` written).

## The finding (NOT the acceptable stub refusal)
`night-receipt.json`: verdict `REFUSED`, refusal reason `night_probe_error`, detail
`FileNotFoundError: [Errno 2] No such file or directory: '/Users/edr/night-custody/rehearsal-20260909/chain.zsh'`; C1/C4 "not evaluated
after refusal", C2 `NOT_APPLICABLE` (`no_pack_by_design`), C3 census clean but FAIL-marked by the refusal, C5 measured heads all
`ae8f074f` (plan/driver/measurement equal). Cause (lead-verified on main at `83ab38ed`, read-only): `joulewise/night_gate.py`
`evaluate_night` reads `plan.chain_path` and `plan.chain_sha256_path` unconditionally (lines 1046–1047) for every receipt class, while
`scripts/run_night.py` substitutes the built-in stub chain for `REHEARSAL_STUB` (lines 1567–1570) and never writes `chain.zsh`; the
driver then proceeds because `rehearsal_effective` (line 1540) is true. The existing test
`tests/test_night_gate.py::test_a_fully_green_rehearsal_can_never_yield_go` (line 414) passes because `FakeProbeSource.read_text`
serves chain text. Per NIGHT_HANDBACK §Next lane only `night_refused_agent_present` is acceptable; this is a finding to CURE before
any plan is armed, and this plan is never re-armed on this signature. Cure lane registered below as NIGHT-GATE-STUB-CHAIN-01.

## Documented post-completion uninstall (this session; allowed by the relaunch prompt)
Authority relied on: relaunch-prompt line 19 clause (b) ("the documented uninstall after a plan's completion") together with
NIGHT_HANDBACK §Next lane (uninstall FROM the stub checkout, remove the stub checkout and the plan root before any real plan). D-175
condition 8's arm-shaped steps (2)–(5) (arm email naming pins, census re-run immediately before) were NOT re-run, because the plan had
completed and nothing was being armed; whether condition 8 also governs post-completion removal is a scope question referred to the
cold gate (Opus review 06 S2), not decided here. Harvest-before-uninstall ordering evidence (06 N7): the copies' order relative to the uninstall is
INFERRED — no transcript of the copy command was captured. The harvest copies exist and hash 17/17 against `SHA256SUMS`, while
`removal-output.txt` records source-root removal at epoch `1788950258` (`plan root removed rc=0`).
`pre-uninstall-observations.txt` embeds a `state.json` whose `last_clock.epoch_s` is `1788950204.064847`, preceding the uninstall epoch
`1788950218` in `uninstall-output.txt` by exactly `13.935153` seconds; this dates the watchdog clock sample, not the copy.
- `uninstall-output.txt`: `scripts/install_night_agent.sh --plan … --hour 2 --minute 56 --uninstall` run FROM the stub checkout at
  `ae8f074f`, rc 0; afterwards `launchctl list` shows only `com.joulewise.magistrate`; only `com.joulewise.magistrate.plist` remains;
  custody root untouched by the uninstall (custody-root count output was 17, with the counting command not captured; the harvest includes 14 `night/` records plus `night.log` and `night_plan.json`, and the
  uninstall branch of `install_night_agent.sh` touches only launchd and the two plists — 06 N2: no pre-count was captured).
  `launchctl list` before the uninstall showed `com.joulewise.night` last exit status 3 = `EXIT_REFUSED` (`scripts/run_night.py`),
  consistent with the refused receipt (06 N3).
- `removal-output.txt`: results-clone HEAD == origin `a84e0f7f`, tree clean → `git worktree remove --force` of the stub checkout rc 0,
  `worktree prune`; plan root `/Users/edr/night-custody/rehearsal-20260909` removed after the byte harvest. `/Users/edr/night-custody`
  now holds `active-campaigns`, `magistrate`, `magistrate-bench`, `retired-v1` only. Nothing is armed.

## NIGHT-REHEARSAL-01 acceptance, item by item (kernel `/tasks/NIGHT-REHEARSAL-01/acceptance`)
1. cold_start.json / COURIER_DEADLINE_S — NOT re-verified here; predates this night (out of this record's evidence).
2. REHEARSAL_STUB result on a night-results branch from a launchd-started driver, verdict REHEARSAL_ONLY — MET (`a84e0f7f`; above).
3. Courier email in Ed's inbox with message id recorded — PARTIAL: the send is recorded (`1a08599a4ff4d005`, `night-courier.sent`); inbox receipt is not verifiable from a headless session (fidelity refuter 05 F4).
4. Stage-1 plan email before any DIAGNOSTIC_NO_PACK arm — NOT YET (no plan authored; owed before G2-a).
5. Agents installed the morning before with the 07:00 dead-man observed standing down — NOT EXERCISED by this night (installed 01:57
   same night; NIGHT_HANDBACK records that this night does not repeat that case). Still open.
6. One fresh post-watchdog REHEARSAL_STUB night through the driver's own courier before any real plan — MET, WITH A FINDING: the
   receipt refused for `night_probe_error`, not the acceptable `night_refused_agent_present`. Acceptance of item 6 is therefore
   CONDITIONAL on NIGHT-GATE-STUB-CHAIN-01 landing; whether a second stub night is required after the cure is a ruling for the cold
   gate or Ed, not this activation (rule 11).

## Next exact actions (this activation, in order)
1. NIGHT-GATE-STUB-CHAIN-01: seat in a linked worktree off main — gate-side cure (skip the chain/sidecar read for `REHEARSAL_STUB`,
   record `chain_sha256: null` and `chain_stub: built_in_stub_by_design` in C5 measured) plus the defect-shaped test (probe source raising on `chain_path`
   for a REHEARSAL_STUB plan → REHEARSAL_ONLY, no refusal); review lenses; PR under the normal gates.
2. Complete PR #308's twelve-row gate ledger (CI `gate-ledger` currently fails for the missing section, by design) and merge.
3. CLONE-READINESS-01 preparation (agent-side only), then G2-a inputs; the `claude remote-control` test between windows.

## Record note (Opus contract review 10, S4 — recorded here, not as a decision-log amendment; rule 11)
Once NIGHT-GATE-STUB-CHAIN-01 lands (branch `fix/2026-09-09-night-gate-stub-chain`, fix head `5db38b58`, PR #309), the night gate
performs NO chain-identity check for `REHEARSAL_STUB` plans, because the driver substitutes the built-in stub
(`sleep 2; echo REHEARSAL`) and never executes the plan's declared chain; consequently the `night_chain_digest_mismatch` refusal
will cover `DIAGNOSTIC_NO_PACK` and `TRANSACTION_PACK` only; on main at `83ab38ed` the gate still reads the chain unconditionally
(the forcing defect above). Authorized by the magistrate's cure brief (trace
`2026-09-09-rehearsal-harvest/01`); whether this belongs in a standing document is for the cold gate or Ed.
