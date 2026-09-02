# Seat: Fable (blind) — unattended quiet-machine windows (D-169)

Head verified: main `bdf557c9`; `impl/t0-unattended-01` content-identical to main (scout, confirmed by diff).
Where the packet and code disagree I say so inline; code wins.

## Q1. Minimum mechanism set for T1

**Code-wins correction that reshapes the packet.** G2-a's launch surface is NOT `launch_window.py`. The
G2-a evening is a generated zsh block (`scripts/gen_g2_phase_d.py` renders it into
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:269-439`) that calls
`validate_powermetrics_fiducial.py --allow-live --sleep-display-before-capture` for the pre/post slots and
`run_campaign.py --arm-quiet-mode --arm-countdown-s 20 --max-failures 1` over 8 probe configs; it carries
ledger readiness + bracket reservation but no prewindow_check, no quiet_mac_prep, no clock-disable, no
`launch_window.py`, no agent census. G2-a is pack-less (`state_kernel.json` row `V5-G2A-PREFILL-PROBE-01`:
deps none, `lead_only`), and `capture_t0_step.py` requires `--pack-root` (`:853`), `launch_window.py`
resolves its arm receipt under `custody/<pack>/arm_readiness.receipts` (`:179-184`). So the packet's
"GO-receipt consumer in `launch_window.py`" cannot gate T1 at all; nothing pack-shaped can. `run_campaign.py`'s
own preflight (`:973-1054`) checks AC/external/low-power/display/screensaver/thermal — no agent census.

Therefore the smallest T1 shape is **one new pre-exec supervisor** wrapped around the G2-a chain, and the
answer to the brief's "can the census producer be the launcher's own pre-exec step" is yes — but the
launcher is the supervisor, not `launch_window.py`.

Gap triage (scout G-1..G-9), T1-required vs deferred:
- REQUIRED: G-1 (scheduler: none exists; no joulewise LaunchAgents, `pmset sleep=0 displaysleep=0` so
  calendar jobs fire), G-2 (unattended supervisor/GO producer), G-4 (zero-agent census producer with the
  production exact-exit-1 predicate — `arm_readiness_evidence_t0.py:1312-1314` `_expect_absent`, `:1720-1736`
  census set), G-8 (email path: the launcher has no mail; Gmail works only from a Claude session), G-7 fix
  (`prewindow_check.sh --window` maps to `_v2` roots `:54-56`; G2-a writes elsewhere — run it without
  `--window` or add a roots arg; without the fix the "clean dwell" reads the wrong tree).
- DEFERRED to T2: G-3 (relaunch harness), G-5 (heartbeat/liveness), G-6 (E-10 runbook amendment is a
  G2-b/transaction concern: `window_runbook.md:813-816, 1243-1244` speak of the pack launch, not G2-a).
- DEFERRED to T3: G-9 (`launch_window.py` consumer + registered by-class refusal), the STEP6/hC digest
  supply line (`window_runbook.md:1246-1302`; open defect noted at `SHAKEDOWN-G2-RUNSHEET.md:781-788`).
- Fourth agent-check spelling NOT in the scout: `prewindow_check.sh:150` (`ps aux | grep -E
  "codex|claude|t3|mcp-server|run_campaign|window-chain"`, BLOCK if count>0). Keep it — it is stricter,
  and it means an idle T3 window already blocks a `--wait` loop rather than hanging it (it re-polls at 30 s
  until `--timeout-min`). The production spelling stays the custody predicate.

Staged plan: STAGE 1 = `scripts/unattended_night.py` + LaunchAgent plist + `gen_g2_phase_d.py --emit-chain`
(emit the block as an executable file instead of only Markdown) + morning `claude -p` mail session. Detail in
the table.

## Q2. GO receipt post-D-167

C1 (council verdict) is retired by D-167 for a diagnostic window; do not fake it. Replace with the
**pre-registration record (D-166)**: C1 := `{condition_id:"C1", status:"PASS", evidence:[<artifact
reference to the D-166 record, path + sha256>]}` when the record for `V5-G2A-PREFILL-PROBE-01` exists and
hashes; `NOT_APPLICABLE` is wrong because pre-registration is an UNCHANGED fence for G2-a (kernel row
fences: D-078/D-149(2)-(5)/D-167/D-166).

Schema: `joulewise.t0_unattended_d149_go_receipt.v1` (`t0_rehearsal.py:48`) does NOT fit unchanged.
Its G5 evaluator (`:710-738`) demands `set(value) == _D149_KEYS` exactly (`:719`) and each condition's
keys exactly `{condition_id,status,evidence}` (`:725`) with `evidence` a non-empty list of custody artifact
references (`:727-731`) — so a top-level `receipt_class` FAILS G5, and a status other than PASS fails
too (`:726`). Ruling-shaped fix: mint `joulewise.t0_unattended_go_receipt.v2` = v1 keys + required
`receipt_class` (rehearsal constant is `T0_UNATTENDED_SUPERVISED_REHEARSAL`, `:38`; new value
`T0_UNATTENDED_DIAGNOSTIC`) and extend `_D149_KEYS`/G5 to accept v2 by class. All five conditions stay
PASS-only; a pack-less C2 is a PASS with different evidence, never a `NOT_APPLICABLE` status.
C2 (arm receipt/pack readiness) for a pack-less window := PASS with `evidence.mode:"packless"` +
`ledger_readiness` + `bracket_reservation` outputs from the G2-a block; C3 clock-disable := exact stdout
`setUsingNetworkTime: Off\n` (`arm_readiness.py:94`; `capture_t0_step.py:639-644`); C4 quiet :=
`prewindow_check.sh` "READY after N min." (`capture_t0_step.py:656-665` shape) + the census set; C5 :=
process lineage (Q4).

Writer: `unattended_night.py`, as the last act before exec. Location: `custody/unattended/<night_id>/
go_receipt.json` + `night_record.json`, immutable after write (D-167: write-once, sha256 in the record).
Consumer for T1: the same module (producer and consumer are ONE module; the exec is refused unless the
receipt it just wrote re-reads as PASS — a self-check, not theatre, because the write is fsynced before
the exec and the record hash is what the morning session emails). Refusal for T1 lives in that module's
own vocabulary (see table). For T3, the `launch_window.py` consumer refuses by class with a NEW code
registered through the launch-lineage path: `LAUNCH_LINEAGE_REASON_CODES` frozenset
(`arm_readiness.py:215-225`; `LaunchLineageError` raises on unregistered codes `:1089-1096`), decision-log
additive amendment (precedent `launch_lineage_axi_unsupported`, `decision_log.md:9993`), mirror in
`validate_powermetrics_fiducial.py:158-167`, tests `test_arm_readiness.py:1043/1155`. Name:
`launch_go_receipt_missing` / `launch_go_receipt_invalid` (class-shaped; the packet's §6.2,
`reason-code-coverage-delta.md:947-988`, already reserves "refuse by class, code selected by
UNATTENDED-LAUNCH-01" — that ticket is T3, not T1).

## Q3. Scheduler and wake layers

**User LaunchAgent (`gui/501`), not LaunchDaemon.** Reasons verified: (a) both sudoers slices are
`edr`-scoped and `sudo -n -l` lists them headlessly — a daemon runs as root/other and would not exercise the
slice Ed ratified; (b) `quiet_mac_prep.sh:17-29` uses `osascript` to quit apps and
`run_campaign.py` calls `pmset displaysleepnow` — Aqua session; (c) `claude -p` needs the user keychain;
(d) `~/Library/LaunchAgents` is writable by `edr` with no sudo — zero Ed hands. powermetrics itself needs
only the sudoers slice (`quiet_mac_prep.sh:47-51` probes it with `sudo -n`), not the GUI. Note pmset has
`sleep=0`; that is what makes `StartCalendarInterval` reliable; add `pmset -g` to preflight and refuse if
sleep != 0.

Two independent wake layers (D-127 §4): **Layer A** = the night supervisor's completion path spawns the
headless agent (`claude -p ... --output-format stream-json`) once the chain exits and the completion record is
written. **Layer B** = a second LaunchAgent, `StartCalendarInterval` fixed clock time (e.g. 07:00), that runs
`claude -p` regardless of Layer A. Independence: different plists, different trigger kinds (event vs
calendar), no shared state except the night directory they both read. Layer B is also the T1 mail carrier.

"Stand down on liveness proof", concretely: the headless session's first scripted action writes
`custody/unattended/<night_id>/agent_heartbeat.json` = `{session_id, pid, monotonic_ns, wall_iso,
night_id}`. Layer A watches for that file; deadline 600 s from spawn; if absent, one more spawn after 120 s
backoff, then a third after 300 s — three total, then a `RELAUNCH_FAILED` record (never a re-run of the
measurement). **Code-wins correction:** the T26 600 s bound (`COLD-GATE-RULING.md:162-248, 308`) is
`0 ≤ (valid_until − 21_600 s) − r1_batch_finished ≤ 600 s` — a T-0 AUTHORING liveness bound, not a relaunch
heartbeat deadline. Reusing 600 s here is my choice by analogy; it is not "already ruled" and needs its own
line (Q6).

Failed night surfaces as: `night_record.json` with `status:"REFUSED"|"FAILED"`, `reason_codes[]`, the
raw stdout of the failing predicate, restore-clock stdout; Layer B's session reads the directory and emails
it. No retry: the supervisor execs the chain once (`os.execve` pattern of `launch_window.py:262-264`, "no
child process, wait path, or automatic retry"); the clock restore is an EXIT trap in the chain, precedent
`05-driver-as-run.sh` (networktime off / EXIT-trap on).

## Q4. Who observes the machine

Producer = `unattended_night.py`, which is not an agent (no `codex|claude|t3` in its argv or children —
verify by name at test time). Sequence:
1. The arming agent writes `night_plan.json` `{night_id, agent_pid: os.getpid(), chain_path, chain_sha256,
   armed_at}` as its LAST act and then exits the whole session (for the interactive magistrate this means
   the /loop ends the session, Q5). Its own exit is not self-proven; the supervisor proves it.
2. Supervisor at T-0 − 60 min: waits until `agent_pid` is gone AND the production census is absent
   (`pgrep -lf "codex|claude|t3"` exit exactly 1 empty stdout, `pgrep -x caffeinate` absent, browsers,
   monitors — the `:1720-1736` set), records `agent_exit_monotonic_ns` (first observation of pid absence),
   `pre_launch_census`. Bounded wait: 20 min, then REFUSE `agent_still_present` + record naming the pids.
3. The chain takes `capture_censuses` itself: the emitted chain file gains a background sampler (every
   60 s, same pgrep set, appending to `capture_censuses.jsonl`; precedent `shakedown-driver.sh` pgrep
   censuses to custody). Sampler pid is recorded so it is excluded from its own census.
4. The supervisor assembles `process_lineage` (`t0_rehearsal.py:96-104` keys) post-hoc into the night record.

Idle T3-Code window: verified today two interactive `claude` processes alive 3d8h each with `codex
mcp-server` children plus a `caffeinate -i -t 300` child. The census REFUSES (never hangs: bounded wait
step 2), record lists pids/argv, Layer B emails. **Yes — the headless loop replaces the interactive session
on window nights**; an interactive session cannot exit itself, `claude -p` can. This is the one behavioural
change Ed must accept: close T3 Code before an armed night, or the night refuses (it will not be hijacked,
D-127 §2).

## Q5. Interaction with the running /loop

Night protocol for the interactive magistrate: at block end, if `night_plan.json` is staged for tonight,
the loop (a) commits and pushes everything (rule 7), (b) writes `docs/process/loop_state/handoff.md` —
what was done, open background jobs (none allowed), next three actions, the night id — plus updates
`state_kernel.json`, (c) writes `night_plan.json` with its own pid, (d) ends the session (the /loop's stop
condition is "night armed"). The relaunched headless session reads FIRST
`custody/unattended/<night_id>/night_record.json`, then `handoff.md`, then the kernel. Its brief (a tracked
prompt file `docs/process/unattended/morning_brief.md`) says: email Ed the record (verbatim reason codes),
then delegate harvest + judgment to Sol xhigh / Opus with WRITE_SCOPE fenced to the night directory and
the G2-a producers' output; Fable reads only the two summaries + `git diff`. Tool allowlist is
`--allowedTools` on the plist argv (read-only git, `.venv/bin/python scripts/…`, Gmail send) — a fixed,
reviewed list; no `danger-full-access`, no bypass flag.

## Q6. Rulings needed before stage 1

1. Receipt schema v2 + class `T0_UNATTENDED_DIAGNOSTIC`, and C1 := D-166 record (D-167 retired C1;
   template `d149-go-receipt-template.md:63-66` licenses a mechanical evaluator for C2–C4 only, not C1/C5;
   G5's exact key set `t0_rehearsal.py:719` makes any new field a schema change, hence a ruling).
2. G7 consumer entry point for G2-a = the new supervisor, not `launch_window.py` (`t0_rehearsal.py:790-793`
   says UNRULED; packet §6.2 names `launch_window.py`).
3. The pack-less C2 shape (`evidence.mode:"packless"`), since D-149 (2) was written for pack readiness.
4. Relaunch deadline/backoff numbers (600 s / 3 attempts) — NOT covered by T26 item 3 (authoring bound).
5. Ed-ratified content of the plist argv allowlist (`--allowedTools`); agents must not self-grant
   permissions (D-148/D-150b spirit), so the reviewed list is Ed's one approval, not a sudo command.
6. Ed behavioural item: interactive T3 window closed on armed nights, or accept refusals.
7. `gen_g2_phase_d.py` gains `--emit-chain`; the runsheet stops being the launch surface for unattended
   runs (the Markdown block is what was reviewed — the file must be byte-derived from the same anchors,
   hashed into the night plan).
No E-10 amendment for T1 (`window_runbook.md:813-816` governs pack launches; amend at T3 with G-6).

## Q7. Risk register (stage 1)

1. **Clock re-enabled mid-capture** (EXIT trap fires early, or network time never went off): detector =
   C3 exact stdout at T-0 and a second `systemsetup -getusingnetworktime` sample in every census tick;
   any `On` during capture → night marked INVALID in the record (number never enters a claim).
2. **Agent sneaks back** (Layer B fires early, a cron/other launches claude): detector = capture
   censuses; any non-exit-1 tick → INVALID + email; Layer B plist has `StartCalendarInterval` after the
   chain's worst-case end plus 1 h and refuses to start if `night_record.json` lacks `completion`.
3. **Wrong runs root for the clean-dwell check** (G-7): detector = supervisor asserts the roots it
   passed match the chain's configured output roots (from the emitted chain header) and records both.
4. **Screensaver/HID-idle path**: `quiet_mac_prep.sh:78-79` FAILs when the screensaver delay is non-zero
   after long idle (currently `idleTime=0`, `:114` OK). Detector = preflight reads `idleTime` and refuses
   if != 0; a silent night here would otherwise pass preflight and fail 45 min later — still a refusal,
   not a wrong number, but it burns the night.
5. **Silent supervisor death** (LaunchAgent never fired, or died before the record): detector = Layer B
   is calendar-driven and independent; if the night directory has no `night_record.json` at 07:00 it
   emails `NO_RECORD` with `launchctl print gui/501/…` output. No number is produced, so no wrong number —
   but this is the case that would otherwise be invisible.

## Stage plan

| Stage | Files touched | New modules | Interfaces | Refusal codes | Tests | Ed-hands residue | Rulings | LOC |
|---|---|---|---|---|---|---|---|---|
| 1 (T1) | `scripts/gen_g2_phase_d.py` (`--emit-chain`, census sampler + EXIT-trap clock restore in the block), `scripts/prewindow_check.sh` (`--roots` arg), `joulewise/t0_rehearsal.py` (v2 schema id, `receipt_class`, G5 accepts v2 `:719-731`), kernel row, decision log | `scripts/unattended_night.py`; `launchd/com.joulewise.night.plist`, `launchd/com.joulewise.morning.plist`; `docs/process/unattended/morning_brief.md` | `night_plan.json`, `go_receipt.json` (v2), `night_record.json`, `capture_censuses.jsonl`, `agent_heartbeat.json` | new `UNATTENDED_REASON_CODES` frozenset: `preflight_failed`, `agent_still_present`, `census_not_clear`, `quiet_not_ready`, `clock_disable_failed`, `preregistration_missing`, `chain_hash_mismatch`, `receipt_invalid` (own vocabulary; not in launch-lineage set) | unit: each predicate with fake pgrep/sudo (exact exit-1, exact stdout); receipt round-trip through `t0_rehearsal` G5; plan/record schema; exec-once (assert no wait/retry path); dry-run LaunchAgent with `launchctl kickstart` and a stub chain | Close T3 Code the armed night; approve plist allowlist; read the email | Q6 1-7 | ~650 py + ~80 plist/sh + ~350 tests |
| 2 (T2) | `unattended_night.py` (completion → spawn), plists | `scripts/relaunch_agent.py` (spawn, heartbeat watch, 3 attempts, `RELAUNCH_FAILED` record) | `agent_heartbeat.json` deadline 600 s | `relaunch_no_heartbeat`, `relaunch_exhausted` | spawn stub; heartbeat timing; Layer A/B independence (each runs with the other disabled) | none | Q6 4 | ~250 + ~150 tests |
| 3 (T3) | `scripts/launch_window.py` (`--go-receipt` consumer), `joulewise/arm_readiness.py:215-225`, `validate_powermetrics_fiducial.py:158-167`, tests `:1043/:1155`, `window_runbook.md` E-10/STEP6 (hC digest from a mechanical step6 record), decision log | supervisor gains pack mode calling `capture_t0_step.py` steps | pack-mode `go_receipt.json` under `custody/<pack>/` | `launch_go_receipt_missing`, `launch_go_receipt_invalid` (registration path §4.5 seven steps) | lineage-code coverage; refuse-by-class; E-10 conformance | Ed's one-time email GO for the transaction (`V5-TRANSACTION-GO-01`) | E-10 amendment; G-6; hC supply line | ~300 + ~200 tests |

## Where I disagree with the packet or the rulings' ordering

- The packet centres `launch_window.py` as the GO consumer for T1; the code shows G2-a never touches
  `launch_window.py` and cannot (pack-less; `:179-184`, `capture_t0_step.py:853`). T1 must be a new
  supervisor; the lineage-code work is T3.
- The packet reads T26 item 3's 600 s as a relaunch liveness deadline; it is the T-0 authoring hang bound.
- The scout lists three agent-check spellings; there are four (`prewindow_check.sh:150`), and the fourth
  is the one that makes an idle T3 window a bounded block rather than a hang.
- Ordering: build the supervisor + email BEFORE the relaunch harness (D-127 §4 cl.4 lists the harness
  first). A night that runs and is reported beats a night that relaunches an agent into silence.
- The packet's Ed-hands residue includes a quiet-guard sudoers install; it is off the critical path for
  G2-a (the chain uses `sudo -n` only for networktime and powermetrics, both installed) — do not spend
  Ed's one command on it.

Confidence: high on the code-wins corrections, the v2 receipt id (G5 exact-key check read at `:719`), and
the LaunchAgent choice (verified live); medium on the 600 s / 3-attempt relaunch numbers, which are mine.
