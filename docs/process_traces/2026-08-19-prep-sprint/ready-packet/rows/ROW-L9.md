# ROW L9 — ENVIRONMENTAL CONTROLS CENSUS (gating, high tier)

Assembled mechanically from the read-only worktree `…/scratchpad/wtS0`, branch
`impl/r2-s0-mint-resolver`. `origin/main == main == 0099382`. Every pointer below
was opened and verified; where evidence could not be located, the row says so and lists the search.
**Candidate dispositions are assembled, not adjudicated; the seat rules.**

> **ASSEMBLY-PIN ANOMALY — report it to the seat, do not paper over it.** The assembler was
> instructed to work at **`4597ad4`**. At the time of reading, branch HEAD was already
> **`b92b43d`** ("Shakedown-v3 first-light run card (prep item 6b)…", = `4597ad4` + 2 commits,
> via `79a4cd0`). By the time of final verification HEAD had advanced again to **`7305e0d`**
> ("Prep sprint: paper staging landed…"), through `45e0229` ("Fresh-pass gate CLEAN through
> `b92b43d`…"). **The tree moved twice underneath this assembly.** Re-checked: no L9-scope code or
> doc surface changed between `b92b43d` and `7305e0d` — the diff touches `README.md`,
> `RUN_STATE.md`, `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `docs/decision_log.md`,
> `docs/process/state_kernel.json`, `tests/test_gen_state.py`, and new
> `docs/process_traces/2026-08-19-prep-sprint/` files. Two consequences the seat should note:
> (1) **TASK_QUEUE.md line numbers below shifted by +7** during assembly (the A4 row moved from
> `:538` to `:545`, duplicate view `:632`→`:639`) — rows are cited by **ID** as well as line, and
> the ID is authoritative; (2) a new hand-authored queue block **`## WO-D149-GO-EVALUATOR`
> (registered 2026-08-19 night)** appeared at `TASK_QUEUE.md:373`. Findings, code line numbers,
> and all ED-row evidence in this document were verified at `b92b43d` and re-confirmed unchanged
> at `7305e0d`.

---

## 0. Seat identity and 2026-08-15 result

- Seat: `L9-environmental-controls-census`, charter §9 ENVIRONMENTAL CONTROLS CENSUS (high),
  **GATING** (`docs/process/instrument-readiness-audit-charter.md:48`).
- Seat report: `docs/process_traces/2026-08-15-readiness-council/seat-reports/L9-environmental-controls-census-report.md`
  (packet digest `8ed06561c5301636`, `sitting-packet-FINAL.md:19`).
- **Verdict 2026-08-15: NOT-READY.** Coverage **14/16** (`evidence_universe_count=16`;
  items 11 `whole_window.py` and 12 `controller.py` partial). **2 blockers / 3 should-fix /
  3 nits / 4 executed falsifiers** (`sitting-packet-FINAL.md:32`).
- This seat's two blockers rest on **live unprivileged probes executed on the actual measurement
  machine** (Mac15,9 / 25F84 — "Probes executed live on the actual measurement machine (Mac15,9 /
  25F84, per the census itself)", `L9-…-report.md:3`; see report §3–§4). Council **Disposition 5**
  records that this makes the observation **SINGLE-SOURCE**:
  > "L9's live census observation is single-source; ED-Q-L9-3's quiet-state fixture is a HARD
  > precondition to WO-CENSUS-SEMANTICS (Opus S8/W9)."
  (`council-verdict.md:49-50`.) Opus S8 states the underlying reason:
  > "Both refuters confirmed by regex/launchd static analysis because the sandbox denied live
  > `pgrep`; the '~20 matches observed live' claim exists only in the L9 seat's own run. Two
  > lenses agree on the analysis, not the observation."
  (`opus-contract-refuter-findings.md:43`.)
- Both blockers were CONFIRMED by both refuter lenses and **consolidated into ONE work order**:
  `sitting-packet-FINAL.md:455-467` ("F3/F4 census over-match confirmed on launchd running-state +
  regex analysis (live pgrep denied in sandbox — earlier live L9 observation stands).
  Consolidation: F3+F4 = ONE census-semantics work order."); cold ruling §6
  (`cold-fable-ruling.md:93`).

---

## 1. FINDINGS — original text verbatim, with citation

Source of verbatim text: `raw/L9-triage.md` (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L9-environmental-controls-census`), cross-checked against
`sitting-packet-FINAL.md` §3 (blockers, lines 74-84) and §4 (should-fix/nits, lines 155-160).

### F1 — blocker

- **Severity:** `blocker`
- **Title (verbatim):** `t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine — arm always refuses`
- **`file_line` (verbatim):** `joulewise/arm_readiness_evidence_t0.py:963-980`
- **failure_scenario (verbatim):**
  > "ALPHA arm night: agents closed, machine genuinely quiet. author_arm_evidence_t0.py runs _maintenance_probe; pgrep -lf matches permanently resident Spotlight.app, mds_stores, XProtect XPC services, mediaanalysisd, photoanalysisd, softwareupdated, backupd-helper (~20 matches observed live); _expect_absent raises underivable → no T-0 evidence → no arm receipt → NO-GO on every attempt. Fail-closed (no false data risk) but the window can never launch. CI never saw this: tests fake the probe executor with exit_code=1 (tests/test_arm_readiness_evidence_t0.py:561)."
- **Citations:** seat report §5 BLOCKER F1 (`L9-…-report.md:66`); §4 falsifier 1
  (`L9-…-report.md:59`); sitting packet §3 `sitting-packet-FINAL.md:74-77`;
  refuter confirmations `sitting-packet-FINAL.md:455`, `:467`; cold §6 `cold-fable-ruling.md:93`.
- **Post-verdict adjudication:** consolidated with F2 into **WO-CENSUS-SEMANTICS**, HARD-gated on
  ED-Q-L9-3 (Disposition 5; Opus W9 `opus-contract-refuter-findings.md:73`).

### F2 — blocker

- **Severity:** `blocker`
- **Title (verbatim):** `t0.no_stray_keepawake (PROCESS_CENSUS) is unpassable — browser/monitor patterns match permanent system daemons`
- **`file_line` (verbatim):** `joulewise/arm_readiness_evidence_t0.py:1344-1360`
- **failure_scenario (verbatim):**
  > "Same arm night: 'Safari|...' matches 9 always-resident Safari LaunchAgents with Safari closed; 'watch' substring in the monitor pattern matches watchdogd (permanent) and watchlistd. _expect_absent refuses → arm NO-GO forever. The keep-awake (pgrep -x caffeinate) and agent (codex|claude|t3) probes are correct and verified effective live; only the browser and monitor patterns over-match."
- **Citations:** seat report §5 BLOCKER F2 (`L9-…-report.md:67`); §4 falsifier 2
  (`L9-…-report.md:60`); sitting packet §3 `sitting-packet-FINAL.md:79-82`.
- **Post-verdict adjudication:** same consolidation as F1.

### F3 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `prewindow_check.sh agent census misses claude / codex mcp-server / t3 — printed OK while three agent processes were live`
- **`file_line` (verbatim):** `scripts/prewindow_check.sh:155`
- **failure_scenario (verbatim):**
  > "E-7b: operator runs the frozen prewindow_check --wait believing it certifies the agent-free ≥10-minute idle; pattern 'codex exec|codex-run|run_campaign|window-chain' matches none of the actual agent processes (observed live: OK printed with a claude session, codex mcp-server, and caffeinate running), so READY can be granted on an agent-contaminated machine; the only enforcing catch is PROCESS_CENSUS minutes later at T-0 authoring."
- **Citations:** seat report §5 SHOULD-FIX F3 (`L9-…-report.md:68`); §4 falsifier 4
  (`L9-…-report.md:62`); `sitting-packet-FINAL.md:155`.

### F4 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `No single-home hazard register; consult-mandated hazards entirely absent: radios, notifications, peripherals, remote sessions, third-party LaunchAgents`
- **`file_line` (verbatim):** `docs/phase_2/window_runbook.md:1160 (§7, nearest anchor — the register is distributed)`
- **failure_scenario (verbatim):**
  > "Charter amendment 8 (from the consult's minimum list) requires rows for network/Bluetooth radios, notifications/media devices, external peripherals, concurrent users/remote sessions. None exists anywhere: live machine shows 3 login sessions (who), 14 third-party launchd jobs including the periodic us.zoom.updater, and active radios — a Zoom updater firing mid-member during the workload phase is invisible to every gate (CPU admission is pre-run idle-baseline only) and is bounded only at window scale by NEG-8 references; today that residual is not even documented as uncontrolled."
- **Citations:** seat report §2 hazard table + §5 SHOULD-FIX F4 (`L9-…-report.md:41-46,69`);
  `sitting-packet-FINAL.md:156`; charter amendment source
  `docs/process_traces/2026-08-14-readiness-charter-consult/consult.md:239,293`.

### F5 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `Mid-workload background contamination has no member-level detector and no documented disposition`
- **`file_line` (verbatim):** `joulewise/idle_admission.py:392-467`
- **failure_scenario (verbatim):**
  > "evaluate_cpu_idle_admission gates the PRE-RUN idle baseline (p95 combined power ≤ 1.0 W); environment re-probes bracket but do not cover the workload phase. A one-shot daemon burst inside a member's measurement phase silently inflates that member's energy; only window-scale drift (NEG-8 triplet/midpoint) can catch a sustained version. This is a legitimate design tradeoff under the D-078 attribution limit — but it must be a DOCUMENTED-UNCONTROLLED register row and a paper limitation, not silence."
- **Citations:** seat report §5 SHOULD-FIX F5 (`L9-…-report.md:70`); completeness disposition
  (`L9-…-report.md:46`); `sitting-packet-FINAL.md:157`.

### F6 — nit

- **Severity:** `nit`
- **Title (verbatim):** `JW-MET-2's four census literals have no named custody destination in the §12 close-out list`
- **`file_line` (verbatim):** `docs/phase_2/window_runbook.md:1509-1544`
- **failure_scenario (verbatim):**
  > "Operator records keyboard_backlight.level=0 etc. per §5A but §12 never enumerates where they land; a close-out can be 'complete' without them, weakening the JW-MET-2 audit trail."
- **Citations:** seat report §5 NIT F6 (`L9-…-report.md:71`); `sitting-packet-FINAL.md:158`.

### F7 — nit

- **Severity:** `nit`
- **Title (verbatim):** `Battery charge state is censused but has no gate or disposition`
- **`file_line` (verbatim):** `joulewise/arm_readiness_evidence_t0.py:1457-1498`
- **failure_scenario (verbatim):**
  > "POWER_PREFLIGHT passes with is_charging=true; charging mid-window adds SMC/charger thermal load that differs from the not-charging state a bound corpus may have been minted under — an uncontrolled, undocumented within-window state change."
- **Citations:** seat report §5 NIT F7 (`L9-…-report.md:72`); `sitting-packet-FINAL.md:159`.

### F8 — nit

- **Severity:** `nit`
- **Title (verbatim):** `Lid state is operator-discipline only, never probed`
- **`file_line` (verbatim):** `docs/phase_2/window_runbook.md:42`
- **failure_scenario (verbatim):**
  > "A lid change alters the thermal envelope mid-window; only the downstream thermal-pressure gate would notice, and only if pressure leaves Nominal."
- **Citations:** seat report §5 NIT F8 (`L9-…-report.md:73`); `sitting-packet-FINAL.md:160`.

### Work orders (verbatim, `raw/L9-triage.md` §WORK ORDERS)

- **WO-L9-1:** "Re-shape t0.background_quiet's MAINTENANCE_CENSUS from absence-required pgrep to an activity-based census (CPU-threshold like prewindow_check's, or a curated transient-only process list). This weakens a probe, so it needs a magistrate/cold ruling; include a regression fixture built from the real resident-process table (ED-Q-L9-3) so CI can no longer pass on faked-empty pgrep output."
- **WO-L9-2:** "Fix PROCESS_CENSUS browser and monitor patterns (anchor tokens; exclude permanent daemons watchdogd/watchlistd/Safari support agents, or move to activity-based). Keep the keep-awake and agent probes byte-identical — both verified effective live."
- **WO-L9-3:** "Align prewindow_check.sh check #8 with the T-0 agent census (add claude|codex mcp|t3), so E-7b READY cannot be granted with agents running."
- **WO-L9-4:** "Author the one-home hazard register with per-hazard disposition (controlled / censused / DOCUMENTED-UNCONTROLLED), adding the absent rows: Wi-Fi/Bluetooth radios, notifications/media devices, external peripherals, concurrent users/remote sessions, third-party LaunchAgents, ambient temperature, battery charge state, lid state, and the mid-workload contamination residual; wire that residual into the paper's limitation text."

### Unexecuted obligations declared at the sitting (verbatim)

- "quiet_mac_prep.sh full execution (quits user apps and sleeps the display — not sandbox-safe from an agent session; step-7 probes replicated read-only instead)"
- "--arm-quiet-mode live re-probe path inside run_campaign (requires display sleep + live campaign; code path read, not run)"
- "sudo-gated probes: systemsetup -getusingnetworktime read, sudo -n powermetrics (no sudo in sandbox; covered by capture lens + ED rows)"
- "quiet_guard engine internals (Commit-1 is contractually inactive and non-armable; contract read, engine not audited)"
- "whole_window.py adapter-wattage-continuity and controller.py enforcement wiring examined at grep/inventory level only"
- "full audit of tests/test_arm_readiness_evidence_t0.py fixtures beyond confirming the probe executor is faked with empty-pgrep results"

---

## 2. WHAT CHANGED SINCE 2026-08-15

### 2.1 WO-CENSUS-SEMANTICS (A4) — kernel/queue rows exist; **implementation NOT started; the ED-Q-L9-3 precondition is NOT met as the acceptance defines it**

- Kernel entry: `docs/process/state_kernel.json:3122-3168`, `"id": "WO-CENSUS-SEMANTICS"`.
  Acceptance evidence item 1 (verbatim, `:3125`):
  > "ED-Q-L9-3 real quiet-state fixture is **committed** before implementation"

  Fence (verbatim, `:3158`):
  > "Do not weaken either census from synthetic or self-nominated evidence; ED-Q-L9-3 is a hard precondition"

  Blocker target (`:3148`): `"target": "ED-Q-L9-3"`. Status note (`:3168`):
  > "Council Phase 1 parallel code work, deliberately held until Ed supplies ED-Q-L9-3 early in the batched qualification session."
- Generated queue row at the current head: **row `A4`**, `TASK_QUEUE.md:545` (duplicate view
  `:639`; these were `:538`/`:632` at `b92b43d` — see the assembly-pin anomaly above) —
  **`A4 | WO-CENSUS-SEMANTICS | P1 Phase Gate | BLOCKED — ED-Q-L9-3 (real quiet-state
  resident-process baseline fixture is captured with all fleets and agents closed) [AGENT]`**.
  Still BLOCKED two days after the quiet census was captured. Kernel dependency record
  (`state_kernel.json:3140-3150`): `{"kind":"external","target":"ED-Q-L9-3","strength":"hard",
  "scope":"start","state":"pending", … ,"evidence": null}` — **`state: pending`, `evidence: null`**
  at the current head.
- `RUN_STATE.md:426`: "**Phase-1 residue:** WO-CENSUS-SEMANTICS stays HARD-gated on ED-Q-L9-3."
  `RUN_STATE.md:519` repeats "(HARD-gated on ED-Q-L9-3 — needs Ed)".
- **Code state verified at 4597ad4 — both blockers are byte-unrepaired**, only shifted by line
  number:
  - `_maintenance_probe` is still the absence-required pgrep, now at
    `joulewise/arm_readiness_evidence_t0.py:981-993` (pattern
    `XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd`,
    then `_expect_absent(probe, kind=kind, label="maintenance")`), consumed by
    `_derive_background_quiet` at `:996-1006`.
  - `_derive_process_census` is still at `:1384-1396` with the identical over-matching patterns:
    browser `Safari|Google Chrome|Chromium|Firefox|browser automation` (`:1389`) and monitor
    `powermetrics|window-chain|run_campaign|tail -f|watch` (`:1390`), all four run through
    `_expect_absent` at `:1393`.
  - `_expect_absent` unchanged at `:976-978`
    (`if result.exit_code != 1 or result.stdout.strip(): raise _underivable(...)`).
  - The only commit touching this module since the council is **`65cc0f3`** "T-0 F4 honest
    contract: D-134 cl.6 overclaim superseded … public execute/monotonic_ns/utc_now injection
    seam removed from capture_t0_step (module-private test hook), runbook + docstrings corrected"
    — **ON `origin/main`**; it does not touch either census.
  - CI still cannot see the defect: `tests/test_arm_readiness_evidence_t0.py:1092-1122` runs the
    real pgrep argvs but only *binds output* (`test_real_maintenance_census_executes_pgrep_and_binds_output`,
    `test_real_process_census_executes_pgrep_and_binds_output`); no committed
    quiet-state resident-process fixture asserts PASS/FAIL against them.
- **Precondition state (Disposition 5's hard gate):** a quiet-state census WAS captured on
  2026-08-17 — see §3 ED-Q-L9-3 — but it lives **only** in out-of-repo custody
  `~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`. **It is NOT committed to the
  repository** and is therefore not the "committed" fixture the kernel acceptance names.
  Searched for it in-repo: `find . -type d -name "quiet-census*"`, `find . -name "*quiet*census*"`,
  `ls tests/fixtures/`, `grep -rln "watchdogd\|mds_stores" tests/ configs/` — the only hits are
  the argv strings inside `tests/test_arm_readiness_evidence_t0.py`, not a fixture.

### 2.2 WO-L9-3 (prewindow census alignment) — **NO REPAIR FOUND**

`scripts/prewindow_check.sh` check #8 is unchanged; the pattern is now at **line 150** (was 155):

```
procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"
```

The only commit touching the file since the council is `b6553fd` "WO-FREEZE-NUMBERING delta-8:
replay reauthenticates the successor; v2 freeze sequences carry the predecessor" (ON `origin/main`),
which does not touch check #8. `claude`, `codex mcp`, and `t3` are still absent from the pattern.

### 2.3 WO-L9-4 (one-home hazard register) — **NO REPAIR FOUND**

Searched: `grep -rn "hazard register|hazard-register|DOCUMENTED-UNCONTROLLED|DOCUMENTED_UNCONTROLLED|hazard_register" docs joulewise scripts`.
Every hit is a *pre-existing* reference to the finding itself (the council triage.json, the seat
report, the cold ruling, the charter §9 line, and the 2026-08-14 charter consult). **No register
document exists anywhere in the tree.** No rows for radios, notifications, peripherals, remote
sessions, or third-party LaunchAgents were authored.

### 2.4 F5 mid-workload residual + paper limitation — **NO REPAIR FOUND**

- `joulewise/idle_admission.py` has **zero commits since 2026-08-15**
  (`git log --since=2026-08-15 -- joulewise/idle_admission.py` empty);
  `evaluate_cpu_idle_admission` still begins at `:392`.
- Paper limitation text: `grep -rn "mid-workload|mid-member" docs/paper docs/report_src docs/contracts`
  returns **nothing**. `grep -rn "zoom" docs/phase_2 docs/paper` returns nothing.

### 2.5 F6 / F7 / F8 nits — **NO REPAIR FOUND**

- **F6:** `docs/phase_2/window_runbook.md` §12 "Close-out record" begins at `:1790`; the enumerated
  list (`:1792-1831`) still contains **no** keyboard-backlight / JW-MET-2 census-literal slot
  (`awk 'NR>=1790' … | grep backlight` → empty). The four literals remain declared only at
  `window_runbook.md:481-484`.
- **F7:** `_derive_power` (POWER_PREFLIGHT) is now at `arm_readiness_evidence_t0.py:1495-1535`.
  It asserts AC power, low-power-mode off, and a connected known-wattage adapter, and records
  `observed_adapter_wattage` / `low_power_mode`. There is still **no charge-state gate or
  disposition** — `grep -n is_charging joulewise/arm_readiness_evidence_t0.py` returns nothing at
  all, i.e. charge state is not even recorded as a named field on the row.
  *(Material for the seat: the 2026-08-17 rail probe was run while the machine reached full charge
  mid-sequence — see §3 ED-Q-L9-2 — which is a live instance of exactly this uncontrolled state
  change.)*
- **F8:** `window_runbook.md:42-43` is unchanged operator discipline
  ("Do not touch the keyboard, trackpad, lid, display controls, power settings, charger, or cable
  during the chain."); no lid probe exists.

### 2.6 Changes that touched this seat's surface indirectly

- **WO-T0-PRODUCER — merged, PR #152 (`a61ac92`) at head `9e8936a`** (`TASK_QUEUE.md` Completed
  table): "`scripts/capture_t0_step.py`, the strict R2 plan resolver, the D-127 privileged clock
  route, and dwell/env hardening landed". This produces the nine T-0 input files the author
  consumes — i.e. it makes the arm sequence *runnable up to* the census probes; it does **not**
  change the two census probes that make it refuse. Follow-up lane commit `65cc0f3` (ON main) added
  the TRUSTED-OPERATOR limitation v1 and removed the public injection seam.
- **WO-KERNEL-RECONCILE — PR #150 (`47d2645`)**: `WINDOW-COUNCIL-GATE` is live in
  `docs/process/state_kernel.json:10-16` (scope `lanes:[quiet_mac]`, `operation:select`); all three
  `_v3` pack rows carry status notes that they remain behind it
  (`state_kernel.json:898,949,1000`). No quiet-mac task can be selected before a READY-candidate
  verdict — so the L9 blockers are currently *masked by the gate*, not cured.
- **WO-MARGIN-RECORDER-AUTHZ — PR #151 (`00ec3b7`)**; **WO-L2-REAUDIT** custody
  `docs/process_traces/2026-08-15-l2-reaudit/` (`0f886d3`) — neither touches L9 scope.
- **WO-DETECT-PULSES-BUDGET**: implementation commit `ceda7a6` "WO-DETECT-PULSES-BUDGET:
  deterministic projection budget + anchor-unresolved bypass + governed nonconvergent abort" is
  **on `origin/main`**, yet the generated queue still shows `A5 | WO-DETECT-PULSES-BUDGET | …
  PARTIAL; READY [AGENT]` (`TASK_QUEUE.md`), and `RUN_STATE.md` records the remaining branch
  `impl/wo-detect-pulses-budget @ 5449e58` as merging "inside the atomic re-freeze". Out of L9
  scope; recorded because the seat is entitled to know the queue's status strings and the commit
  graph disagree.
- **WO-SAMPLER-SUPERVISOR**: registered only, `TASK_QUEUE.md:293-316`; explicitly "Not on any
  critical path"; no implementation. It bounds F1-class remedies on L3's side, not L9's.
- **Operator-facing documents authored since the council** (all ON `origin/main` unless noted):
  `aa90dc3` `docs/process/ed-evening-checklist.md`; `b352cff` `docs/process/ed-morning-packet-2026-08-18.md`;
  `80155db` `docs/process/ed-batch-packet.md`; `ad14ac4` `docs/process/rehearsal-operator-card.md`
  + `scripts/ed_session/build_rehearsal_env.sh`; `79a4cd0`
  `docs/process/d149-go-receipt-template.md` (**branch-only**); `cbcb5ea`
  `docs/process_traces/2026-08-18-t10-t11-working-notes/` (**branch-only**); `4db15bd`
  `docs/process_traces/2026-08-18-shakedown-first-light/` (ON main).
- **`scripts/ed_session/*` fixes** from the live operator evening (both ON `origin/main`):
  `d873f77` "ed_session: guard empty-args re-exec against macOS bash 3.2 set -u (unbound
  ORIGINAL_ARGS[@])" and `e5dc38a` "ed_session: probe command-scoped sudo authorization, not
  blanket sudo -n true". Neither changes census semantics.
- **A file inside this seat's evidence universe CHANGED after the audit, unre-audited:**
  universe item 10, `joulewise/environment_admission.py` (seat report `:18`, "function-inventory
  survey"), was modified by **`b7e5730`** "S1: anchor-v3 production flip + D-079 r5
  (science-neutral, 19-member replay proven) + claim barrier (D-146)" — **branch-only, not on
  `origin/main`** (`git show b7e5730 --stat` → `joulewise/environment_admission.py | 4 +-`).
  `_window_thermal_pressure_refusals` now resolves the anchor reconstructor by era instead of
  calling the v2 deriver directly. A sibling commit `d279bd2` "S1 fix 3" explicitly repairs a
  "**missed census site**" in the calibration live-three-window scenario. This is anchor-era
  dispatch *inside environment admission* — **not** the MAINTENANCE_CENSUS/PROCESS_CENSUS process
  censuses (those remain WO-CENSUS-SEMANTICS, blocked) — but it is a post-audit change to a file
  this seat enumerated, landed on the branch, and reviewed by no seat.
- **`docs/phase_2/ed-qualification-session.md` — ZERO commits since 2026-08-15.**
  `git log --since=2026-08-15 -- docs/phase_2/ed-qualification-session.md` is empty. Steps 3 and 4
  (the homes ED-Q-L9-2 and ED-Q-L9-1 cite) are byte-identical to the audited text.

### 2.7 D-149 no-hands window automation — scope note

`0e96dbb` "D-149: standing conditional T-0 GO — full no-hands window automation (Ed); kernel fences
updated (regen + pins green)" is **branch-only (not on `origin/main`)**, as is its receipt template
`docs/process/d149-go-receipt-template.md` (`79a4cd0`) and the run card `b92b43d`
"Shakedown-v3 first-light run card (prep item 6b): turnkey window lane — GO receipt, in-band check
against the r6 band, D-078 refusal handling".

**What D-149 says.** Decision-log index row `docs/decision_log.md:172`; body
`docs/decision_log.md:8865-8870` ("## D-149: Standing conditional T-0 GO (no-hands window
automation)"). T-0 GO is (verbatim) "AUTO-ISSUED when ALL of the following hold, evaluated
mechanically at T-0 and written into the window's custody record as a GO receipt" — conditions
C1–C5, including C3 machine quiet ("census clean, fleet quiesced, no interactive use, single
writer"). Purpose clause (verbatim): "the paper pipeline … runs end-to-end lead-driven; **Ed
confirms bytes at the end, not launches at the start**." Retained (verbatim): "**REMAINS ED'S:
anything needing hands (cables, backlight, reboots, new sudo), claim publication, exact-byte
confirmation.**" Restated `RUN_STATE.md:80-83`.

**It DOES re-scope an operator clause — in the kernel, not in the phase-2 docs.**
`git show 0e96dbb -- docs/process/state_kernel.json` replaces the fence rule on **all three**
window tasks (D117-W-ALPHA / BETA / GAMMA):
- **removed:** `"…and the separate perishable T-0 GO; Ed remains the physical launch authority"`
- **added:** `"…and the separate perishable T-0 GO; T-0 GO auto-issues per D-149 when its five
  recorded conditions pass (no-hands windows); hands-required work remains Ed's"`

and the fence authority label flipped from `2026-08-15 council NOT-READY verdict` to
`D-149 standing conditional T-0 GO (2026-08-19)`. The same replaced text is rendered into the
generated queue rows Q2/Q3/Q4 of `TASK_QUEUE.md`. **"Ed remains the physical launch authority" is
gone from the kernel** while `docs/phase_2/window_runbook.md` still asserts the opposite in prose
that is unmodified at HEAD — e.g. `:464` "§5A. Pre-window clock stabilization (administrator step;
**Ed performs it**)", `:1055` "E-10 — **Ed's deliberate physical launch**", `:886` "The real binding
to a real quiet window is **Ed's human §5A tap** …", and the mandatory handback attestation at
`:976-981`. `docs/phase_2/*.md` contain **zero** occurrences of `D-149`, `no-hands`, or
`unattended`.

**Effect on L9's rows.** D-149 does **not moot** any L9 row and does not re-scope ED-Q-L9-1 or
ED-Q-L9-2 — both are System-Settings / sudo-probe rows with no automated substitute, their home
document (`ed-qualification-session.md` steps 3–4) is unchanged, and D-149 explicitly keeps
"backlight" on Ed's side of the line. Four facts the seat should weigh:

1. **D-149's C1 presupposes exactly these rows.** C1 requires "ED-QUALIFICATION rows closed"
   (`decision_log.md:172`; charter `docs/process/instrument-readiness-audit-charter.md:83`). Those
   rows close only through a physical visit. So auto-GO cannot legitimately fire until the ED
   rows this packet is adjudicating are closed — **this sitting's verdict is an input to D-149's
   own gate.**
2. **The "evaluated mechanically" wording is not yet implemented.**
   `docs/process/d149-go-receipt-template.md:63-66` (verbatim): "Tooling: a mechanical evaluator
   script MAY be built to fill C2–C4, but it goes through the ordinary gauntlet first; **until then
   the issuer fills the receipt by running the runbook commands and attaching outputs.**" A queue
   block `## WO-D149-GO-EVALUATOR (registered 2026-08-19 night)` was added at `TASK_QUEUE.md:373`
   *during this assembly*. So at HEAD, "mechanical" evaluation is a lead agent by hand.
3. **C3's "census clean" is a point-in-time T-0 check performed by the two censuses this seat
   ruled UNPASSABLE (F1/F2) and unrepaired.** There is no continuous supervisor: `QUIET-GUARD-01`
   is queued and descoped to "commit 1 only, installed-INACTIVE" (`TASK_QUEUE.md` A9);
   WO-SAMPLER-SUPERVISOR is unlanded; WO-CENSUS-SEMANTICS is blocked. With no operator present,
   mid-window contamination (F5) is observable only post hoc.
4. **The operator-presence assumption underneath F4/F5/F8 loses its enforcer.** Note that the
   window was *already* unattended after launch (`window_runbook.md:1070-1072`: "Ed steps away
   immediately after invoking E-10 and does not touch or monitor the machine") — D-149's delta is
   the **launch and the GO decision**, not the capture. But lid state (F8) and charger/lid
   non-interference (`window_runbook.md:42-46`) are dispositioned as *operator discipline*, which
   assumes an operator who was present to start it.
5. **`WINDOW_STATUS.md` was not reconciled.** grep for `D-149|no-hands|unattended` → NOT FOUND;
   it is still dated "2026-08-17" and still says "Do not launch a measurement window before a
   READY-candidate council issues a qualifying verdict" (`:36-38`).

**No seat has audited D-149's automation**, and it post-dates every seat report by four days.
Registered as an assembled fact, not a graded disposition — see probe §5.7.

---

## 3. ED-QUALIFICATION ROWS

Charter classification, as the sitting recorded it: **ED-QUALIFICATION rows are stable
capabilities** ("everything above stays valid (stable capabilities; only T0 rows are perishable)",
`docs/phase_2/ed-qualification-session.md:53-54`). Under the **charter amendment adopted at this
sitting** (Opus S12, `council-verdict.md:54-57`), a **READY-CANDIDATE sitting binds charter:77-78 —
only T0 rows may remain open.** All three L9 rows are ED-QUALIFICATION, none are T0; on the
amendment's terms each must be closed before this sitting can grade READY.

---

### ED-Q-L9-1 — JW-MET-2 keyboard-backlight census

**Row text (VERBATIM,** `sitting-packet-FINAL.md:192` **/** `raw/L9-triage.md` **):**
> "ED-Q-L9-1 (staged): JW-MET-2 System Settings keyboard-backlight census — level 0, auto-adjust off, inactivity Never, verification=operator_visual (ed-qualification-session.md step 4; no CLI exists for the level, operator visual is the only probe)"

**Charter classification as declared in the row:** `(staged)` — a stable capability staged in the
one batched Ed session; not T0, not perishable.

**LOCATED CLOSURE EVIDENCE — EXECUTED LIVE, durable receipt (out-of-repo custody):**

- Path: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/keyboard-backlight.txt`
  (122 bytes, file mtime 2026-08-17 18:00). Full contents:
  ```
  backlight_level=0
  auto_adjust=false
  inactivity_dim=never
  verification=operator_visual
  checked_at=2026-08-17T18:00:42-0700
  ```
- **Machine:** Ed's measurement Mac (the qualification-evening custody root).
  **Date:** 2026-08-17 18:00:42 -0700. **Live sudo:** not applicable — the row is
  `verification=operator_visual` by construction (no CLI exists for the level).
  **Durably recorded:** yes, as a file under the custody root.
- Corroborating narrative: `docs/run_reports/2026-08-18-t10-session.md:113`
  ("**Backlight rows** | level 0 / auto-adjust off / inactivity never, `operator_visual` |
  `keyboard-backlight.txt` (18:00:42)"); `docs/process/ed-morning-packet-2026-08-18.md:118`
  ("Keyboard-backlight rows (level 0 / auto-adjust off / inactivity never).").
- **Weaknesses the seat should weigh, stated plainly:** (a) the receipt is **outside the
  repository** — nothing in the tree commits or hashes it, so it is not reachable from any
  manifest, and F6 (no §12 custody slot for these literals) is precisely the defect that leaves it
  homeless; (b) the four literals are a *self-report typed by the operator*, with no independent
  probe — which the row itself concedes; (c) it records a **one-time settings state**, and nothing
  re-verifies it at arm time.

---

### ED-Q-L9-2 — JW-MET-3 rail-inclusion differential probe

**Row text (VERBATIM,** `sitting-packet-FINAL.md:193` **):**
> "ED-Q-L9-2 (staged): JW-MET-3 keyboard-backlight rail-inclusion differential probe — sudo powermetrics ABBA max/off arms (ed-qualification-session.md step 3; documentation-grade, boundary verdict already stands on code evidence)"

**Charter classification as declared in the row:** `(staged)`, documentation-grade.

**LOCATED CLOSURE EVIDENCE — EXECUTED LIVE with real sudo powermetrics, durable receipts
(out-of-repo custody):**

- Path: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/rail-probe-20260818T011943Z/`
  containing `max-1.plist`, `off-1.plist`, `off-2.plist`, `max-2.plist` (~1.59 MB each),
  `rail-probe-results.json`, `rail-probe.log`.
- **Live sudo ran:** yes. `rail-probe.log` records each arm's literal command, e.g.
  `command=/usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 30 --samplers battery,cpu_power,gpu_power,ane_power,thermal --format plist -o /tmp/ed-session/rail-probe-20260818T011943Z/off-1.plist`,
  each followed by `PASS: arm <name> captured and sampler exited.` and a `PASS: no powermetrics
  process found.` orphan census. Final line:
  `PASS: ABBA rail probe complete; preserve /tmp/ed-session/rail-probe-20260818T011943Z.`
- **Machine/date:** measurement Mac, arms captured 2026-08-18T01:19:43Z (= 2026-08-17 evening PT);
  4 × 30 s, 30 records each.
- **Result (verbatim from `rail-probe-results.json`):**
  `aggregate_max_minus_off_consumed_rail_energy_delta_j` = `cpu_power: -5.704900831585405`,
  `gpu_power: 0.13299985399425585`, `ane_power: 0.0`.
- **Recorded caveats — the operator's own load note**
  (`~/JouleWise-window-custody/ed-qual-20260817/rail-probe-load-note.txt`, verbatim excerpts):
  > "concurrent_load=decisive_replay_unittest"
  > "power_state=operator_reported: charging during probe, reached full charge ~3/4 through the four-arm sequence (charge-termination step change spans the off-2/max-2 boundary region)"
  > "note=ABBA design, documentation-grade row; negative aggregate cpu delta (-5.7 J) attributed to concurrent-load drift + charge-state step, not backlight; ANE delta exactly 0.000000000 J across both pairs; boundary verdict (LED outside cpu+gpu+ane consumed rails) stands on code evidence independent of this probe"
  > "recorded_by=lead (dictated from operator report, 2026-08-17 evening PT; operator's own load-note paste superseded by this fuller record same evening)"
- **Weaknesses the seat should weigh:** (a) the probe ran on a **contaminated machine** — a
  concurrent decisive-replay unit test held CPU at ~13.7–14.0 W mean across all four arms, and the
  battery reached full charge mid-sequence, i.e. **two of L9's own uncontrolled hazards (F5
  mid-workload contamination, F7 charge-state transition) actually fired inside the qualification
  probe**; (b) the differential is **negative** (-5.7 J for a load that can only add energy),
  which the note attributes to drift rather than to the backlight; (c) the load note is
  **lead-authored, dictated from the operator's report**, after "the operator's own load-note paste"
  was overwritten; (d) receipts are out-of-repo and uncommitted. The row is documentation-grade by
  construction, so none of this is claim-bearing — but "executed" is not the same as "informative".

---

### ED-Q-L9-3 — quiet-state resident-process baseline (the HARD precondition)

**Row text (VERBATIM,** `sitting-packet-FINAL.md:194` **):**
> "ED-Q-L9-3 (new, stable capability, no sudo): quiet-state resident-process baseline — with all fleets/agents closed on the real machine, capture the four PROCESS_CENSUS and one MAINTENANCE_CENSUS pgrep outputs and commit them as the regression fixture that the WO-L9-1/2 pattern fixes must pass against; this is the only way to prove the fixed censuses PASS in the state they will actually run in"

**Charter classification as declared in the row:** `(new, stable capability, no sudo)` —
ED-QUALIFICATION, not T0. Additionally a **HARD PRECONDITION** to WO-CENSUS-SEMANTICS
(`council-verdict.md:49-50`; Opus S8/W9; kernel fence `state_kernel.json:3158`).

**LOCATED EVIDENCE — CAPTURED LIVE, but with two material qualifications against the row text:**

- Path: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/quiet-census/` — 7 files:
  `CAPTURE-NOTE.txt`, `captured-at.txt`, `census-agent.txt`, `census-browser.txt`,
  `census-keepawake.txt`, `census-maintenance.txt`, `census-monitor.txt`.
  `captured-at.txt` = `2026-08-17T23:51:29-0700`.
- **All five required censuses are present** (4 PROCESS_CENSUS + 1 MAINTENANCE_CENSUS), each with
  its `exit=` line. Contents that constitute the fixture value:
  - `census-browser.txt` — **7** always-resident Safari agents with Safari closed
    (`SafariBookmarksSyncAgent`, `SafariLaunchAgent`, `CredentialProviderExtensionHelper`,
    `com.apple.Safari.SafeBrowsing.Service`, `com.apple.Safari.History`, `SafariNotificationAgent`,
    `SafariConfigurationSubscriber`), `exit=0`.
  - `census-monitor.txt` — `552 /usr/libexec/watchdogd` and
    `1999 …/WatchListKit.framework/Support/watchlistd`, `exit=0`.
  - `census-maintenance.txt` — **20 process lines** (file is 21 lines incl. `exit=0`):
    `softwareupdated` ×2, `backupd`, `backupd-helper`, `mds_stores`, `mdworker`, `mdbulkimport`,
    `mediaanalysisd`, … `exit=0`.
  - `census-keepawake.txt` — one pid (`95305`), `exit=0`.
  - `census-agent.txt` — many lines, `exit=0`.
- **QUALIFICATION 1 — captured by the LEAD (an agent session), not by Ed, and NOT with all
  agents closed.** `CAPTURE-NOTE.txt` says so in its own words (verbatim):
  > "captured_by=lead (Fable magistrate session), all delegated agent RUNS quiesced"
  > "known lead-session-owned lines (ABSENT on a real ARM night when all sessions close):"
  > "- census-keepawake: the single caffeinate pid = T3 Code harness 5-min lease (caffeinate -i -t 300), parented by the claude process"
  > "- census-agent: all lines = this session (claude) + resident codex MCP servers from the tracked .mcp.json bridge (idle, no active runs) + t3 substring matches from the T3 harness"
  > "fixture value (the three patterns WO-L9-1/2 must fix, UNAFFECTED by the session):"

  The row demands "with all fleets/agents closed on the real machine". The capture instead has a
  live `claude` session, several resident `codex mcp-server` processes, T3 harness processes, and
  a live `caffeinate` lease — i.e. **two of the five censuses (`keepawake`, `agent`) are
  contaminated by the capturing agent itself**, and the note asks the reader to accept a
  self-declared partition into "session-owned" vs "fixture value" lines. The three patterns the
  work order must fix (browser/monitor/maintenance) are argued to be unaffected — but that argument
  is **the capturing party's own**, which is precisely the "self-nominated evidence" the kernel
  fence forbids (`state_kernel.json:3158`).
- **QUALIFICATION 2 — the fixture was never COMMITTED.** The acceptance text requires the fixture
  be "**committed** before implementation" (`state_kernel.json:3125`) and the row itself says
  "capture … **and commit them as the regression fixture**". Searched the whole tree for it:
  `find . -type d -name "quiet-census*"` (nothing), `find . -name "*quiet*census*"` (nothing),
  `ls tests/fixtures/` (only `fake_powermetrics_process.py`),
  `grep -rln "watchdogd\|mds_stores" tests/ configs/` (only argv strings in
  `tests/test_arm_readiness_evidence_t0.py`). **NO COMMITTED FIXTURE LOCATED.**
- **Corroborating narrative (agrees with both qualifications):**
  - `docs/run_reports/2026-08-18-t10-session.md:109` — "**ED-Q-L9-3 quiet census** | **Captured
    23:51** by the lead with all agent runs quiesced; 7 resident Safari agents, `watchdogd`+`watchlistd`,
    19 maintenance daemons — the L8/L9 **over-match findings confirmed as fixture ground truth**;
    lead-session lines labeled | `quiet-census/` (6 files + `CAPTURE-NOTE.txt`)".
    *(Note the arithmetic drift: the run report says "19 maintenance daemons" and the CAPTURE-NOTE
    says "19 resident Apple daemons"; the file itself carries **20** process lines.)*
  - `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:276` — "ED-Q-L9-3 census
    CAPTURED (23:51): browser 7 resident Safari agents, …" (**branch-only**, `cbcb5ea`).
  - `docs/process/ed-morning-packet-2026-08-18.md:123` — "ED-Q-L9-3 quiet census (lead-captured
    23:51 with fleets quiesced; browser/monitor/maintenance over-match ground truth confirmed;
    labeled)."
  - `docs/process/ed-evening-checklist.md:13-16` had assigned it to Ed: "**Quiet-state baseline
    (ED-Q-L9-3) — do this EARLY** while the machine settles: the ~10-minute quiet-machine baseline
    per the qualification script. Evidence: the baseline capture. (This also unblocks the census
    work order.)" — the ~10-minute quiet dwell the checklist specifies is **not recorded anywhere
    in the capture**; `captured-at.txt` is a single instant.
- **Net state for the seat:** the observation exists and is durable; it is *not* the artifact the
  row and the kernel acceptance define, and it does not discharge Disposition 5's hard
  precondition as written. WO-CENSUS-SEMANTICS' own queue row still says BLOCKED on it
  (`TASK_QUEUE.md:538`), which is the repo's own agreement with that reading.
- **Second-source status (Disposition 5):** the 2026-08-17 capture is the **first independent
  re-observation** of the L9 live census claim — a different session, a different day, on the same
  machine. It reproduces the browser (7 vs the seat's 9), monitor (`watchdogd`+`watchlistd`), and
  maintenance (20 vs the seat's ~20) over-matches. Whether "a later capture by the same
  organisation on the same machine" counts as a **second source** for Opus S8's purposes is
  exactly the question the seat must rule on; it is not the same as a second *lens*.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Severity | Candidate disposition | What is attached / what remains |
|---|---|---|---|
| F1 `t0.background_quiet` unpassable | blocker | **STILL-OPEN** | Code byte-unrepaired at `arm_readiness_evidence_t0.py:981-1006`; WO-CENSUS-SEMANTICS never started; queue row still BLOCKED (`TASK_QUEUE.md:538`). Remaining: the activity-based re-shape + its magistrate/cold ruling (probe-weakening) + a committed fixture. |
| F2 `t0.no_stray_keepawake` unpassable | blocker | **STILL-OPEN** | Patterns byte-identical at `:1389-1390`; `_expect_absent` unchanged at `:1393`. Same work order, same block. |
| F3 prewindow agent census misses agents | should_fix | **STILL-OPEN — NO REPAIR FOUND** | `scripts/prewindow_check.sh:150` unchanged; `claude|codex mcp|t3` still absent. Searched the file's full git log since 2026-08-15 (one commit, `b6553fd`, unrelated). |
| F4 no one-home hazard register | should_fix | **STILL-OPEN — NO REPAIR FOUND** | No register document exists; search listed in §2.3. |
| F5 mid-workload contamination undocumented | should_fix | **STILL-OPEN — NO REPAIR FOUND** | `idle_admission.py` has zero commits since the council; no paper/limitation text (§2.4). *Aggravating fact: the hazard fired inside ED-Q-L9-2's own probe.* |
| F6 JW-MET-2 literals lack a §12 custody slot | nit | **STILL-OPEN — NO REPAIR FOUND** | §12 list at `window_runbook.md:1792-1831` has no backlight row; and the actual 2026-08-17 literals landed out-of-repo, illustrating the gap. |
| F7 charge state censused, ungated | nit | **STILL-OPEN — NO REPAIR FOUND** | `_derive_power` at `:1495-1535` has no charge-state field or gate; `is_charging` appears nowhere in the module. |
| F8 lid state discipline-only | nit | **STILL-OPEN — NO REPAIR FOUND** | `window_runbook.md:42-46` unchanged; no probe. *Interacts with D-149 no-hands operation (§2.7).* |
| **ED-Q-L9-1** backlight census | ED-QUALIFICATION (stable) | **ED-ROW — closed-with-evidence, evidence OUT-OF-REPO** | Live operator-visual receipt `…/ed-qual-20260817/keyboard-backlight.txt`, 2026-08-17 18:00:42 -0700. Seat must rule whether an uncommitted, unhashed self-report closes a gating row. |
| **ED-Q-L9-2** rail probe | ED-QUALIFICATION (stable, documentation-grade) | **ED-ROW — closed-with-evidence, evidence OUT-OF-REPO and CONTAMINATED** | Four live `sudo -n powermetrics` ABBA arms + results JSON + log, 2026-08-18T01:19Z; ANE delta exactly 0; **cpu delta negative** under concurrent replay load and a mid-sequence charge-to-full. Seat must rule whether a documentation-grade row closes on a contaminated differential. |
| **ED-Q-L9-3** quiet-state fixture | ED-QUALIFICATION (stable) **+ HARD PRECONDITION** | **ED-ROW — OPEN as the row defines it** (a live capture exists) | Capture exists at `…/ed-qual-20260817/quiet-census/` (5 censuses, 2026-08-17T23:51:29-0700) but (a) **captured by the lead agent, not Ed, with claude/codex-mcp/t3/caffeinate live**, contaminating 2 of the 5 censuses, and (b) **never committed** as the fixture the kernel acceptance names. The repo's own queue agrees: `A4 … BLOCKED — ED-Q-L9-3`. |
| WO-CENSUS-SEMANTICS (A4) | work order | **STILL-OPEN, BLOCKED** | Kernel row + acceptance + fence exist (`state_kernel.json:3122-3168`); zero implementation. |
| WO-L9-3 / WO-L9-4 | work orders | **NO-REPAIR-FOUND** | Neither registered as its own kernel row that this assembler could locate, nor implemented. |
| D-149 no-hands automation | new since the sitting | **NEW, UNAUDITED — for the seat to scope** | `0e96dbb` + `79a4cd0` + `b92b43d`, all **branch-only**. Does not moot any L9 row; removes the human enforcer that F5/F8's "operator discipline" disposition assumes. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

Each probe names its falsifier — the observation that would overturn the candidate disposition.

1. **(a) Staged-vs-live, ED-Q-L9-1.** Ask whether an operator-typed four-line text file with no
   independent probe and no commit is a *receipt* or a *claim*.
   Run: `cat ~/JouleWise-window-custody/ed-qual-20260817/keyboard-backlight.txt`; then
   `git -C <repo> log --all --oneline -S"operator_visual" -- docs/ configs/ tests/`.
   **Falsifier of the assembled disposition:** a committed, hashed record of the same literals
   inside the repo, or a re-verification at arm time. **Falsifier of closure:** the settings were
   changed after 2026-08-17 (nothing re-checks them) — ask Ed to re-open System Settings once.

2. **(a) Staged-vs-live, ED-Q-L9-2.** Verify the arms were live and not replayed:
   `grep -c "sudo -n /usr/bin/powermetrics" ~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/rail-probe-20260818T011943Z/rail-probe.log`
   (expect 4); check the plists carry distinct `kern_boottime`/`timestamp` and 30 records each.
   **Falsifier:** identical byte content across arms, or timestamps outside 2026-08-18T01:19–01:24Z.
   Then ask the harder question: **does a documentation-grade row close on a differential whose
   sign is wrong?** `aggregate … cpu_power: -5.7049 J` for a load that can only add power.

3. **(a) Staged-vs-live, ED-Q-L9-3 — the decisive probe of this row.** Read
   `CAPTURE-NOTE.txt` line "captured_by=lead (Fable magistrate session)" and
   `census-agent.txt` (11+ live `claude`/`codex mcp-server`/`codex-code-mode-host` lines) and
   `census-keepawake.txt` (a live caffeinate pid). Compare against the row's requirement
   "with all fleets/agents closed on the real machine".
   **Falsifier of the assembled "OPEN" disposition:** a second capture, taken by Ed with every
   agent process actually terminated, whose `census-agent` and `census-keepawake` are **empty**.
   That capture does not exist — searched `~/JouleWise-window-custody/` (22 dirs; only
   `ed-qual-20260817/quiet-census/`).

4. **(a) Committed-fixture existence.** The acceptance says "committed". Run in the worktree:
   `git log --all --oneline --diff-filter=A -- '*quiet-census*' '*quiet_state*'` and
   `git grep -l "SafariBookmarksSyncAgent\|watchlistd" -- tests configs`.
   **Falsifier:** any committed fixture file. Assembler found none.

5. **(b) Is the live census observation still SINGLE-SOURCE?** Disposition 5 labels it
   single-source because "the '~20 matches observed live' claim exists only in the L9 seat's own
   run" (Opus S8). There is now a **second capture** (2026-08-17, lead) that reproduces the
   browser/monitor/maintenance over-matches — but on the **same machine**, by the **same
   organisation**, with no independent lens. Probe: does the seat count same-machine
   re-observation as a second source, or does S8's concern (a *claim-bearing* remedy that
   redefines "quiet") require an independent observer or a committed artifact CI can re-derive?
   **Falsifier of "still single-source":** the seat rules the 2026-08-17 capture is an adequate
   second source. **Falsifier of "now two-source":** note that the 7-vs-9 Safari-agent count and
   the 20-vs-"~20" maintenance count differ between the two observations, and neither observation
   is machine-checkable today.

6. **(c) Does the census match the CURRENT OS build, not the audited one?** Both observations bind
   to macOS **25F84** / **Mac15,9** (the 2026-08-17 sampler plist records
   `hw_model=Mac15,9`, `kern_osversion=25F84`). Probe now, at the machine:
   `sw_vers -buildVersion; sysctl -n hw.model` and re-run the exact five argvs from
   `arm_readiness_evidence_t0.py:987-991` and `:1387-1390`.
   **Falsifier:** a build other than 25F84, or a resident-process table that differs from
   `quiet-census/` — either voids the fixture and reopens the row. Note the standing rule that this
   class of row "REOPENS on any OS update before the window".

7. **(d) D-149 unattended failure modes — no seat has audited this.** Run
   `git show 0e96dbb -- docs/process/state_kernel.json` and read the fence replacement on all
   three window tasks: `"Ed remains the physical launch authority"` is **deleted**. Then read
   `docs/decision_log.md:172` (C1–C5), `docs/process/d149-go-receipt-template.md` (`79a4cd0`), and
   the run card `b92b43d`. Ask specifically:
   (i) **C3 "census clean" is evaluated by the two censuses this seat ruled UNPASSABLE and which
   are still unrepaired** — how does an auto-GO evaluate C3 at all? Either it uses the broken
   probes (and never fires), or it uses something else (and the seat should ask what).
   (ii) **C1 requires "ED-QUALIFICATION rows closed"** — so D-149 depends on *this sitting's*
   verdict on ED-Q-L9-1/2/3. Is that circularity recorded anywhere?
   (iii) "evaluated mechanically at T-0" vs `d149-go-receipt-template.md:63-66` ("until then the
   issuer fills the receipt by running the runbook commands and attaching outputs") and the
   brand-new `## WO-D149-GO-EVALUATOR` block at `TASK_QUEUE.md:373` — **the evaluator does not
   exist.**
   (iv) with no human at the machine, who observes a lid change (F8) or a mid-member daemon burst
   (F5)? (v) does the automation retry after a refusal — D-078 no-retry says it must not
   ("a refused capture ends that lane with diagnosis, never re-arm-and-hope", `decision_log.md:172`)
   — is that mechanically enforced or documentary? (vi) does it re-assert `prewindow_check.sh`,
   the check **F3 proves lies about agent presence**? (vii) E-4 expects an interactive sudo
   password prompt (`window_runbook.md:896`) and D-149 keeps "new sudo" as Ed's — how does a
   no-hands T-0 obtain privilege? NOT ADDRESSED in any document located.
   **Falsifier:** an explicit automation-side environmental gate or continuous supervisor that
   supersedes operator discipline. **Aggravators:** all three D-149 artifacts are **branch-only**,
   absent from `origin/main` and from every seat's evidence universe; `WINDOW_STATUS.md` still
   carries the pre-D-149 rule and is dated 2026-08-17; and the kernel and
   `docs/phase_2/window_runbook.md` now contradict each other on who launches.

8. **Gate-masking check.** `WINDOW-COUNCIL-GATE` (`state_kernel.json:10-16`) currently blocks every
   quiet-mac selection, so F1/F2's "arm always refuses" is untestable in production today. Probe:
   does a READY verdict from this sitting *lift* the very gate that is masking two unrepaired
   arm-blocking defects? **Falsifier:** the census repairs land and pass against a committed
   fixture first.

9. **Self-nomination check (the council's standing caution).** The verdict warns that "every seat's
   evidence universe was self-nominated, and the one denominator adversarially tested fell"
   (`council-verdict.md:18-22`). L9's coverage was **14/16** with items 11 and 12
   (`whole_window.py` adapter-wattage continuity, `controller.py` enforcement wiring) examined at
   grep level only, and the t0 test-fixture audit incomplete. Probe: independently re-enumerate
   L9's universe before accepting 14/16.
   **Falsifier:** an independent enumeration reproducing 16 items exactly.

10. **Charter-amendment applicability.** Opus S12's amendment (`council-verdict.md:54-57`) says a
    READY-CANDIDATE sitting binds charter:77-78 — "only T0 rows may remain open." All three L9 rows
    are declared stable/staged capabilities, not T0. Probe: on that text, can this sitting grade
    READY with ED-Q-L9-3 in its current state? **Falsifier:** a ruling that the 2026-08-17 capture
    closes the row despite the "all fleets/agents closed" and "commit them" clauses.

---

## 6. OPEN ITEMS FROM THIS ROW

- **F1 (blocker) — no repair.** `t0.background_quiet` MAINTENANCE_CENSUS is byte-unchanged at
  `joulewise/arm_readiness_evidence_t0.py:981-1006`; arm still refuses on every attempt on a
  genuinely quiet machine.
- **F2 (blocker) — no repair.** `t0.no_stray_keepawake` browser/monitor patterns byte-unchanged at
  `:1389-1390`.
- **WO-CENSUS-SEMANTICS has zero implementation** and is still `BLOCKED — ED-Q-L9-3` in the
  generated queue at the current head (`TASK_QUEUE.md:538`, duplicated `:632`).
- **ED-Q-L9-3 is NOT closed as the row defines it.** A live capture exists
  (`~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`, 2026-08-17T23:51:29-0700) but was
  taken **by the lead agent with agent processes live** (contaminating the keepawake and agent
  censuses) and was **never committed** as the regression fixture the kernel acceptance requires.
  **NO COMMITTED FIXTURE LOCATED** — searched `find . -type d -name "quiet-census*"`,
  `find . -name "*quiet*census*"`, `ls tests/fixtures/`,
  `grep -rln "watchdogd\|mds_stores" tests/ configs/`, and `git log --since=2026-08-15` on
  `tests/test_arm_readiness_evidence_t0.py`.
- **Disposition 5's SINGLE-SOURCE label is not cleanly discharged.** The only re-observation is
  same-machine, same-organisation, and self-partitioned by its own capture note; its counts differ
  from the seat's (7 vs 9 Safari agents; 20 vs "~20" maintenance daemons).
- **WO-L9-3 — no repair.** `scripts/prewindow_check.sh:150` still uses
  `codex exec|codex-run|run_campaign|window-chain`; E-7b can still print OK with agents live.
- **WO-L9-4 — no repair, nothing authored.** No hazard register exists anywhere in the tree; the
  consult-mandated rows (radios, notifications, peripherals, remote sessions, third-party
  LaunchAgents, ambient temperature, charge state, lid state, mid-workload residual) are all still
  absent.
- **F5's paper limitation text does not exist** — `grep -rn "mid-workload|mid-member"` over
  `docs/paper docs/report_src docs/contracts` returns nothing.
- **F6/F7/F8 nits all unrepaired**, verified line by line at 4597ad4.
- **The two hazards L9 flagged as uncontrolled actually fired inside this seat's own qualification
  probe**: ED-Q-L9-2's rail probe ran under `concurrent_load=decisive_replay_unittest` (F5) while
  the battery reached full charge mid-sequence (F7). No seat has assessed what that does to the
  probe's admissibility.
- **All ED-row closure evidence for this seat lives OUTSIDE the repository**
  (`~/JouleWise-window-custody/ed-qual-20260817/`), uncommitted and unhashed by any manifest. F6 is
  the registered version of exactly this gap.
- **The dress rehearsal — the operator ceremony that would exercise the arm sequence end to end —
  is OPEN**, per `docs/process/ed-morning-packet-2026-08-18.md:126` ("OPEN: the dress rehearsal
  (item 4) only.") and `docs/run_reports/2026-08-18-t10-session.md:110`.
- **D-149's no-hands window automation is unaudited by any seat** and is **branch-only**
  (`0e96dbb`, `79a4cd0`, `b92b43d`, none on `origin/main`). It removes the operator presence that
  F5's and F8's "operator discipline" dispositions silently assume.
- **D-149 DELETED the kernel clause "Ed remains the physical launch authority"** from all three
  window tasks while `docs/phase_2/window_runbook.md` still asserts Ed's §5A tap, E-10 physical
  launch, and handback attestation verbatim at HEAD. **The kernel and the runbook now contradict
  each other on who launches**, and no cold gate or seat has reconciled them.
- **D-149's C1 ("ED-QUALIFICATION rows closed") makes its auto-GO depend on the very rows this
  sitting is adjudicating** — a circularity recorded nowhere in D-149's own text.
- **D-149's "evaluated mechanically at T-0" is not implemented.** The receipt template defers the
  evaluator (`d149-go-receipt-template.md:63-66`) and a queue block `## WO-D149-GO-EVALUATOR`
  appeared at `TASK_QUEUE.md:373` *during this assembly*.
- **`WINDOW_STATUS.md` was never reconciled with D-149** — no mention of it, still dated
  2026-08-17.
- **A file in this seat's evidence universe changed after the audit and was re-audited by nobody:**
  `joulewise/environment_admission.py` (universe item 10) via **`b7e5730`** (branch-only), with a
  "missed census site" repair in `d279bd2`.
- **The branch HEAD moved twice during this assembly** (`4597ad4` → `b92b43d` → `7305e0d`),
  shifting `TASK_QUEUE.md` line numbers by +7 and adding a new queue block. A packet assembled
  against a moving tree is itself a finding for the sitting.
- **`docs/phase_2/ed-qualification-session.md` has not been touched since the council**
  (zero commits since 2026-08-15), so ED-Q-L9-1 and ED-Q-L9-2's documented homes (steps 4 and 3)
  are byte-identical to what the seat audited.
