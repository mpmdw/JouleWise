# ROW L9-environmental-controls-census — Environmental controls / census (GATING)
Original verdict: NOT-READY (2 blockers / 3 should-fix / 3 nits / coverage 14/16)
Falsifiers 4 · unexecuted obligations 6 · ED-QUAL rows 3
Citation: `docs/process_traces/2026-08-15-readiness-council/sitting-packet-FINAL.md` §2 seat-verdict table (line 32); seat report `docs/process_traces/2026-08-15-readiness-council/seat-reports/L9-environmental-controls-census-report.md` (sha16 `8ed06561c5301636`, packet §1).

**Assembly note on the reading head.** The assembler brief names the read-only worktree at
`impl/r2-s0-mint-resolver` @ `d10881b`. The worktree is actually two commits further on:
`impl/r2-s0-mint-resolver` @ **`79a4cd0`** ("D-149 GO-receipt template + evidence runbook"),
with `d10881b` as its parent-1 ancestor. `main` == `origin/main` == `0099382`. Everything below
was read at `79a4cd0` and its main-vs-branch location stated per pointer.

---

## L9-B1 — t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine

### (a) Original finding (VERBATIM)
> ### L9-environmental-controls-census B1: t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine — arm always refuses
> at: joulewise/arm_readiness_evidence_t0.py:963-980
> scenario: ALPHA arm night: agents closed, machine genuinely quiet. author_arm_evidence_t0.py runs _maintenance_probe; pgrep -lf matches permanently resident Spotlight.app, mds_stores, XProtect XPC services, mediaanalysisd, photoanalysisd, softwareupdated, backupd-helper (~20 matches observed live); _expect_absent raises underivable → no T-0 evidence → no arm receipt → NO-GO on every attempt. Fail-closed (no false data risk) but the window can never launch. CI never saw this: tests fake the probe executor with exit_code=1 (tests/test_arm_readiness_evidence_t0.py:561).
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: sitting-packet-FINAL.md §3 heading "L9-environmental-controls-census B1: t0.background_quiet (MAINTENANCE_CENSUS) is unpassable on the real machine — arm always refuses" (packet line 74); seat report §5 (F1); refuter verdicts — sitting-packet-FINAL.md §9 "ECF-contract" ("All four CONFIRMED (L10-B1 consumption edge, L4-B1 margin recorder, **L9-B1 maintenance census**, L9-B2 browser/monitor regexes)") and §9 "ECF-execution" ("F3/F4 census over-match confirmed on launchd running-state + regex analysis (live pgrep denied in sandbox — earlier live L9 observation stands)"). The `[PENDING]` slots in §3 were never back-filled in the sealed packet; the verdicts live only in §9.

Post-verdict adjudication: **CONFIRMED by both lenses**, consolidated with B2 into ONE work order —
council-verdict.md "WORK-ORDER PROGRAM … WO-CENSUS-SEMANTICS (gated on ED-Q-L9-3)"; cold-fable-ruling.md
line 93 ("L9-B1+B2 consolidated — activity-based re-shape of MAINTENANCE_CENSUS and the browser/monitor
patterns; gated on ED-Q-L9-3's quiet-state baseline fixture"). Opus refuter S8 additionally marked the
empirical basis SINGLE-SOURCE (see the SINGLE-SOURCE sub-row below).

### (b) What changed since 2026-08-15
- **The defect code is BYTE-IDENTICAL to the audit baseline.** Verified by direct comparison:
  `git show ac3fe1d:joulewise/arm_readiness_evidence_t0.py` line 976 and head `79a4cd0`
  `joulewise/arm_readiness_evidence_t0.py:989` both carry the same pattern
  `"XProtect|mds_stores|mdworker|mdbulkimport|backupd|photoanalysisd|softwareupdated|Spotlight|mediaanalysisd"`.
  `_maintenance_probe` is at `:981-994`, `_expect_absent` at `:976-979`, `_derive_background_quiet`
  at `:996`. Only line numbers moved (963-980 → 981-995); the semantics did not.
  WHERE it lives: **merged to main** — `joulewise/arm_readiness_evidence_t0.py` at HEAD is
  byte-identical to `main:joulewise/arm_readiness_evidence_t0.py` (last touched on main by `65cc0f3`,
  "T-0 F4 honest contract", which did not touch the census).
- **The CI-masking mechanism is also unchanged.** `tests/test_arm_readiness_evidence_t0.py:583-584`
  still reads `if "/usr/bin/pgrep" in command: return _probe_result(command, cwd, exit_code=1)` —
  every pgrep probe is faked absent with empty stdout. WHERE: merged to main.
- **Two Darwin-gated "real pgrep" tests exist but do NOT close the gap.**
  `tests/test_arm_readiness_evidence_t0.py:1089-1102` (`test_real_maintenance_census_executes_pgrep_and_binds_output`)
  and `:1104-1123` (process census) execute the real argv, but per `_real_probe_source` they assert the
  probe *argv/source binding only* — not that `_expect_absent` passes. Both predate the council:
  `git log -S` attributes them to `ac3fe1d` (#149), the audit baseline itself. No repair.
- **The gating work order is still BLOCKED, on both main and the branch.**
  `docs/process/state_kernel.json` `/tasks/WO-CENSUS-SEMANTICS`: `"status": "blocked"`, `"rank": 4`,
  `status_note` = "Council Phase 1 parallel code work, deliberately held until Ed supplies ED-Q-L9-3
  early in the batched qualification session." Verified identical on `main` (kernel line 3083) and at
  HEAD (line 3122) — the kernel file differs between branch and main elsewhere, but **this row does not**.
- **ED-Q-L9-3 WAS CAPTURED — but not as a committed fixture.** See the dedicated sub-row below.
- No commit anywhere on `impl/r2-s0-mint-resolver` (49 commits ahead of `origin/main`) touches the
  census semantics. `git log -- joulewise/arm_readiness_evidence_t0.py` since the council returns exactly
  one commit, `65cc0f3` (T-0 F4 honest contract), whose subject and diff concern the D-134 cl.6 overclaim
  and the injection seam, not the censuses.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating whether a launch-blocking, unrepaired, correctly-diagnosed
census defect whose work order is deliberately `blocked` in the authoritative kernel can coexist with
any READY grade on a gating seat — and, separately, whether the ED-Q-L9-3 precondition is now satisfied
(next sub-row) or merely captured.

### (d) Skeptical probes
1. `grep -n "XProtect|mds_stores" joulewise/arm_readiness_evidence_t0.py` at whatever head the sitting
   adopts — is the pattern still the 2026-08-15 string, or did a late commit change it without a WO?
2. `sed -n '576,590p' tests/test_arm_readiness_evidence_t0.py` — does the pgrep executor still fake
   `exit_code=1`? If any assembler claims CI now covers this, that line refutes it.
3. Read `_real_probe_source` in `tests/test_arm_readiness_evidence_t0.py` in full: do the Darwin tests
   assert a PASS/absence outcome, or only argv binding? (Assembler read: only binding.)
4. `python3 -c "import json;print(json.load(open('docs/process/state_kernel.json'))['tasks']['WO-CENSUS-SEMANTICS']['status'])"`
   on BOTH `main` and the sitting head — a divergence would mean the queue and the kernel disagree.
5. Ask whether "activity-based re-shape" (cold ruling line 93) is a *probe weakening* requiring its own
   ruling. The L9 seat's own WO-L9-1 text says so: "probe weakening ⇒ needs a ruling". Has that ruling
   been entered anywhere in `docs/decision_log.md` D-138..D-149?

---

## L9-B2 — t0.no_stray_keepawake (PROCESS_CENSUS) is unpassable: browser/monitor patterns match permanent system daemons

### (a) Original finding (VERBATIM)
> ### L9-environmental-controls-census B2: t0.no_stray_keepawake (PROCESS_CENSUS) is unpassable — browser/monitor patterns match permanent system daemons
> at: joulewise/arm_readiness_evidence_t0.py:1344-1360
> scenario: Same arm night: 'Safari|...' matches 9 always-resident Safari LaunchAgents with Safari closed; 'watch' substring in the monitor pattern matches watchdogd (permanent) and watchlistd. _expect_absent refuses → arm NO-GO forever. The keep-awake (pgrep -x caffeinate) and agent (codex|claude|t3) probes are correct and verified effective live; only the browser and monitor patterns over-match.
> REFUTER-CONTRACT: [PENDING]  REFUTER-EXECUTION: [PENDING]  MAGISTRATE-SYNTHESIS: [PENDING]

Citation: sitting-packet-FINAL.md §3 heading at packet line 79; seat report §5 (F2); refuter verdicts —
§9 "ECF-contract" ("All four CONFIRMED … L9-B2 browser/monitor regexes") and §9 "ECF-execution"
("Consolidation: F3+F4 = ONE census-semantics work order").

Post-verdict adjudication: **CONFIRMED by both lenses**; consolidated with B1 into WO-CENSUS-SEMANTICS
(cold-fable-ruling.md line 93). Cold ruling seat table line 27: "B1, B2 confirmed (consolidated to one
census-semantics defect); the hazard-register should-fix stands."

### (b) What changed since 2026-08-15
- **Both regexes are BYTE-IDENTICAL to the audit baseline.** At head `79a4cd0`,
  `joulewise/arm_readiness_evidence_t0.py:1389` is
  `_fresh_probe(context, kind, "browser", ("/usr/bin/pgrep", "-lf", "Safari|Google Chrome|Chromium|Firefox|browser automation"))`
  and `:1390` is
  `_fresh_probe(context, kind, "monitor", ("/usr/bin/pgrep", "-lf", "powermetrics|window-chain|run_campaign|tail -f|watch"))`.
  At `ac3fe1d` the same two lines are at `:1349` and `:1350` with identical strings. Line drift only.
- `_derive_process_census` is at `:1384-1400`; the `for label, probe in zip(("keep-awake", "agent",
  "browser", "monitor"), probes, strict=True)` loop at `:1392` still calls `_expect_absent` on all four.
  The row is wired at `:1618` (`"t0.no_stray_keepawake": _derive_process_census`).
  WHERE it lives: **merged to main** (file identical between HEAD and `main`).
- **The over-match is now empirically confirmed on the real machine** — but as ground truth for the
  fixture, not as a fix. See the ED-Q-L9-3 sub-row: `census-browser.txt` records 7 always-resident
  Safari agents with Safari closed; `census-monitor.txt` records `watchdogd` + `watchlistd`.
  This *strengthens* the finding; it does not repair it.
- No repair commit found. Same search as B1.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating an unrepaired launch-blocking defect that the intervening
live capture has now independently corroborated — the evidence moved from single-source *analysis*
toward observed ground truth, while the code moved not at all.

### (d) Skeptical probes
1. `grep -n "Safari|Google Chrome\|powermetrics|window-chain" joulewise/arm_readiness_evidence_t0.py` —
   confirm both regexes at the sitting head.
2. `cat ~/JouleWise-window-custody/ed-qual-20260817/quiet-census/census-browser.txt` — count the resident
   Safari lines yourself. Does the file show 7, and is Safari genuinely closed per `CAPTURE-NOTE.txt`?
3. Does any test assert the *fixed* semantics (e.g. that `watchdogd` is admitted)? `grep -rn "watchdogd\|watchlistd" tests/`
   — assembler found zero repo hits outside the council trace.
4. B2's own text asserts the agent probe `codex|claude|t3` "is correct and verified effective live".
   Cross-check against L8's nit and L9's SF1: the *prewindow* agent census is a different, still-broken
   pattern. Do not let the correct T-0 probe launder the broken shell probe.
5. Was the B1+B2 consolidation into one WO ever recorded in the decision log as a formal ruling, or does
   it exist only in `cold-fable-ruling.md` line 93 and the verdict's Phase-1 list?

---

## L9-SF1 — prewindow_check.sh agent census misses claude / codex mcp-server / t3

### (a) Original finding (VERBATIM)
> - [should_fix] [L9] prewindow_check.sh agent census misses claude / codex mcp-server / t3 — printed OK while three agent processes were live

Citation: sitting-packet-FINAL.md §4 (packet line 155). Seat report §5 F3: "prewindow_check.sh:155 agent
census misses claude/codex mcp/t3 (observed lying OK, live). E-7b READY can certify the ≥10-min idle with
agents running; only T-0 catches it later." Seat WO-L9-3: "align prewindow #8 with the T-0 agent pattern."
No refuter verdict slot (should-fix tier; §9 refuters covered blockers only).

### (b) What changed since 2026-08-15
- **NOT repaired.** `scripts/prewindow_check.sh:148-156` at head `79a4cd0`:
  ```
  # 8. No agent or measurement process already running.
  local procs
  procs="$(ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain" | grep -vc grep)"
  ```
  The pattern is still `codex exec|codex-run|run_campaign|window-chain`. It contains no `claude`,
  no `t3`, and `codex exec` does not match `codex mcp-server`.
  WHERE it lives: **merged to main** (file identical between HEAD and `main`).
- `scripts/prewindow_check.sh` HAS changed twice since the audit baseline, both times for other reasons:
  `a61ac92` (WO-T0-PRODUCER, PR #152) and `b6553fd` ("WO-FREEZE-NUMBERING delta-8", whose F3 flipped the
  `--window` prefixes to the `_v2` family — `git show b6553fd -- scripts/prewindow_check.sh` is 6 insertions
  / 3 deletions and does not touch check 8). So the file was in scope for two work orders and the census
  was not fixed in either.
- Adjacent repair that is NOT this one: the `--wait` path now enforces a continuous clean dwell
  (`MIN_CLEAN_DWELL_S`, `clean_since` reset on any failed sample, `scripts/prewindow_check.sh:181-210`)
  — that closes L8-B2's 61-second-READY defect, not L9's pattern gap. A seat should not credit it here.
- The ED-Q-L9-3 capture makes the gap concrete: `CAPTURE-NOTE.txt` records that at capture time
  `census-agent` matched "this session (claude) + resident codex MCP servers from the tracked `.mcp.json`
  bridge (idle, no active runs) + t3 substring matches from the T3 harness" — i.e. exactly the three
  classes prewindow check 8 cannot see.

### (c) Candidate disposition for the seat
**STILL-OPEN (NO-REPAIR-FOUND).** The seat is adjudicating a two-line shell fix that survived two
work orders touching the same file, and whose failure mode — E-7b printing READY with agents live —
is now corroborated by the ED-Q-L9-3 capture.

### (d) Skeptical probes
1. `sed -n '148,156p' scripts/prewindow_check.sh` at the sitting head — read the literal pattern.
2. `pgrep -lf 'codex|claude|t3'` vs `ps aux | grep -E "codex exec|codex-run|run_campaign|window-chain"`
   run side by side during any agent session: does check 8 print OK while the T-0 pattern matches?
3. Is WO-L9-3 registered anywhere as a task? `grep -rn "WO-L9-3\|WO-L9-1\|WO-L9-2\|WO-L9-4"
   docs/process/state_kernel.json TASK_QUEUE.md RUN_STATE.md` — assembler found **zero hits**; only
   the consolidated `WO-CENSUS-SEMANTICS` exists, and its acceptance evidence (kernel `:3124-3128`)
   names the MAINTENANCE and browser/monitor repairs only, **not** the prewindow alignment.
4. If the seat is told this rides inside WO-CENSUS-SEMANTICS, make it point at the acceptance clause
   that covers `scripts/prewindow_check.sh`. There is none.

---

## L9-SF2 — No single-home hazard register; consult-mandated hazards entirely absent

### (a) Original finding (VERBATIM)
> - [should_fix] [L9] No single-home hazard register; consult-mandated hazards entirely absent: radios, notifications, peripherals, remote sessions, third-party LaunchAgents

Citation: sitting-packet-FINAL.md §4 (packet line 156). Seat report §5 F4: "no one-home hazard register;
consult-mandated hazards absent entirely (radios, notifications, peripherals, remote sessions — live:
3 sessions; third-party LaunchAgents — live: 14 incl. periodic us.zoom.updater). A mid-member
Zoom-updater burst is invisible to every member-level gate and today not even documented as
uncontrolled." Seat WO-L9-4: "author the one-home hazard register with the missing rows, each
dispositioned; wire the mid-workload residual into the paper limitation text."

Post-verdict adjudication: expressly preserved — cold-fable-ruling.md line 27: "the hazard-register
should-fix **stands**."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `grep -rln "hazard register\|hazard_register\|HAZARD REGISTER" docs/ scripts/ joulewise/`
  at head `79a4cd0` returns six files, **all of them council-era artifacts describing the absence**:
  `docs/process_traces/2026-08-15-readiness-council/{magistrate-dispositions-for-sitting.md, triage.json,
  sitting-packet-FINAL.md, seat-reports/L9-environmental-controls-census-report.md}`,
  `docs/process_traces/2026-08-14-readiness-charter-consult/consult.md`, and
  `docs/process/instrument-readiness-audit-charter.md`. No register document was authored.
- Targeted re-check of the operative surfaces: `grep -rn "hazard register\|hazard-register"
  docs/phase_2/window_runbook.md docs/paper/ RUN_STATE.md TASK_QUEUE.md` → **zero hits**.
- No task row exists: `grep -rn "WO-L9-4" docs/process/state_kernel.json TASK_QUEUE.md RUN_STATE.md`
  → zero hits. The consolidated WO-CENSUS-SEMANTICS acceptance (kernel `:3124-3128`) covers only the
  two census repairs and the ED-Q-L9-3 precondition; the hazard register is in no work order.
- Spot-checks of the named missing hazards at the sitting head:
  `grep -niw "lid" docs/phase_2/window_runbook.md` → two hits, both operator-discipline prose
  (`:42` "Do not touch the keyboard, trackpad, lid, display controls, power settings…" and `:1620`
  the deviation table). `grep -niw "battery|charger|charging"` → `:41`, `:43`, `:391`, all
  operator-discipline. No radios, notifications, peripherals, or remote-session rows anywhere.
  WHERE: **merged to main**.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** Searched: all of `docs/`, `scripts/`, `joulewise/` for register wording; the
runbook, paper, RUN_STATE and TASK_QUEUE for the specific hazard classes; the kernel and queue for a
WO-L9-4-shaped row. The seat is adjudicating a should-fix the cold adjudicator explicitly preserved,
which has no owner, no work order, and no home document four days later.

### (d) Skeptical probes
1. `grep -rln "hazard" docs/ | grep -v 2026-08-15-readiness-council` — is there a register under a
   different name (e.g. "uncontrolled variables", "environmental controls table")?
2. Ask for the *one home*. If the answer is "the runbook §1 discipline checklist", read
   `docs/phase_2/window_runbook.md:40-46` and judge whether five prose bullets constitute a
   dispositioned register.
3. `grep -rn "zoom.updater\|LaunchAgent" docs/` — the seat observed 14 third-party periodic LaunchAgents
   live, including `us.zoom.updater`. Is any of that recorded anywhere outside the seat report?
4. Does the paper carry the DOCUMENTED-UNCONTROLLED wording WO-L9-4 asked for? Cross-check
   `docs/paper/draft-v1.md` §7 limitations — assembler found the attribution-limit, one-stack, and
   load-regime limitations, but no mid-workload-contamination limitation.

---

## L9-SF3 — Mid-workload background contamination has no member-level detector and no documented disposition

### (a) Original finding (VERBATIM)
> - [should_fix] [L9] Mid-workload background contamination has no member-level detector and no documented disposition

Citation: sitting-packet-FINAL.md §4 (packet line 157). Seat report §5 F5: "mid-workload contamination
has no member-level detector (idle_admission.py:392-467 gates pre-run baseline only); needs a
DOCUMENTED-UNCONTROLLED row + paper limitation wording, not silence." Seat report §2 completeness
disposition: "The per-member CPU admission gate is pre-run idle-baseline only; the workload phase is
bounded solely at window scale by the NEG-8 reference triplet/midpoint and drift allowance. That is a
defensible design under the D-078 attribution limit — but it is currently undocumented."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `joulewise/idle_admission.py` still exposes `evaluate_cpu_idle_admission`
  at `:392` (pre-run baseline), `evaluate_adapter_wattage_continuity` at `:516`, and
  `evaluate_neg8_bracket` at `:631` — i.e. the same pre-run + window-scale shape the seat described.
  No mid-workload / per-member detector function was added.
  WHERE: **merged to main**.
- No documented disposition found: no hazard register (SF2), and no mid-workload limitation in the
  paper. Searched `docs/paper/draft-v1.md` §7 "Discussion and limitations" — the limitation entries
  present at head are attribution-limited resolution, one-unit/one-stack/one-boundary, load-regime
  transfer, and the trusted-operator family; none names mid-workload background contamination.
- Note for the seat: this finding is a **documentation** obligation as much as a code one. Neither half
  landed.

### (c) Candidate disposition for the seat
**NO-REPAIR-FOUND.** Searched `joulewise/idle_admission.py` for a member-level detector, and the paper
+ runbook + hazard-register search space for the DOCUMENTED-UNCONTROLLED disposition. The seat is
adjudicating whether an admittedly defensible-but-undocumented residual can stay silent through a
READY-candidate sitting when the design's own reviewer asked for it to be written down.

### (d) Skeptical probes
1. `grep -n "def evaluate" joulewise/idle_admission.py` — is every gate still pre-run or window-scale?
2. `grep -rn "mid-workload\|mid-member\|during the workload" docs/paper/draft-v1.md docs/phase_2/window_runbook.md`
   — any disposition text at all?
3. If someone claims the NEG-8 bracket + drift allowance already covers it, ask at what time resolution:
   a single one-shot daemon burst inside one ~50 J member is the scenario, and window-scale drift
   screens integrate it away.
4. Does D-078's attribution-limit ratification actually license the silence, or only the residual?
   Read the D-078 body, not the summary.

---

## L9-N1 — JW-MET-2's four census literals have no named custody destination in the §12 close-out list

### (a) Original finding (VERBATIM)
> - [nit] [L9] JW-MET-2's four census literals have no named custody destination in the §12 close-out list

Citation: sitting-packet-FINAL.md §4 (packet line 158). Seat report §5 F6: "JW-MET-2's four census
literals lack a named custody slot in §12 (runbook:1509-1544)." Seat report §2 hazard table:
"Nit: literals lack a §12 custody slot."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `docs/phase_2/window_runbook.md:472-491` still prescribes the four literals
  (`keyboard_backlight.level=0`, `.automatic_adjust=false`, `.inactivity=never`,
  `.verification=operator_visual`, at `:481-484`) with the instruction "Record these four literals
  exactly" and no destination. `grep -n "keyboard_backlight" docs/phase_2/window_runbook.md` returns
  exactly those four lines — the strings appear nowhere in a §12 close-out slot.
  WHERE: **merged to main**.
- The literals WERE captured once, off-repo, during the Ed session: `docs/run_reports/2026-08-18-t10-session.md:107`
  records "**Backlight rows** | level 0 / auto-adjust off / inactivity never, `operator_visual` |
  `keyboard-backlight.txt` (18:00:42)" under custody root `~/JouleWise-window-custody/ed-qual-20260817/`.
  That closes ED-Q-L9-1, not this nit — the nit is that the *runbook* names no destination for a
  future window's literals.

### (c) Candidate disposition for the seat
**STILL-OPEN (nit).** The seat is adjudicating a one-line runbook addition; note that ED-Q-L9-1's
one-off capture is not the same thing as a §12 custody slot.

### (d) Skeptical probes
1. `sed -n '1500,1560p' docs/phase_2/window_runbook.md` — read §12's close-out enumeration and look
   for a keyboard-backlight row.
2. `grep -rn "keyboard_backlight" docs/ scripts/ joulewise/` — where would a window's literals land?

---

## L9-N2 — Battery charge state is censused but has no gate or disposition

### (a) Original finding (VERBATIM)
> - [nit] [L9] Battery charge state is censused but has no gate or disposition

Citation: sitting-packet-FINAL.md §4 (packet line 159). Seat report §5 F7: "charge state censused,
not gated/dispositioned (arm_readiness_evidence_t0.py:1457-1498)."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `_derive_power` at `joulewise/arm_readiness_evidence_t0.py:1495-1530` runs
  `("/usr/bin/pmset", "-g", "batt")` at `:1498` and gates on exactly one substring:
  `if batt.exit_code != 0 or "AC Power" not in batt.stdout: raise _underivable(kind, "fresh power probe
  does not report AC power")` (`:1506-1507`). The remaining `pmset -g batt` content — charge percentage
  and charging/charged status — is captured into the receipt but never evaluated. The other two gates
  in the row are low-power-mode-off (`:1508-1509`) and a connected known-wattage adapter (`:1519-1521`).
  WHERE: **merged to main**.
- Relevant corroboration that charge state matters: the T10 rail probe was degraded partly by a
  "charge-termination step" — `docs/run_reports/2026-08-18-t10-session.md:106` records "cpu delta
  **−5.7 J** attributed to concurrent replay load + charge-termination step". That is the exact class
  of unmodelled state this nit names, observed on the real machine after the council.

### (c) Candidate disposition for the seat
**STILL-OPEN (nit), with new corroborating evidence.** The seat is adjudicating whether a nit whose
failure mode was subsequently observed to perturb a real measurement (T10 rail probe) should stay a nit.

### (d) Skeptical probes
1. `sed -n '1495,1525p' joulewise/arm_readiness_evidence_t0.py` — count the gates; confirm charge
   percentage is unread.
2. `pmset -g batt` on the arming machine mid-charge vs at 100% — does the receipt distinguish them?
3. Read `docs/run_reports/2026-08-18-t10-session.md:106` and ask whether the rail-probe caveat should
   promote this row.

---

## L9-N3 — Lid state is operator-discipline only, never probed

### (a) Original finding (VERBATIM)
> - [nit] [L9] Lid state is operator-discipline only, never probed

Citation: sitting-packet-FINAL.md §4 (packet line 160). Seat report §5 F8: "lid state discipline-only,
no probe (runbook:42)."

### (b) What changed since 2026-08-15
- **NO-REPAIR-FOUND.** `grep -niw "lid" docs/phase_2/window_runbook.md` at head `79a4cd0` returns two
  hits, both prose: `:42` "Do not touch the keyboard, trackpad, lid, display controls, power settings,
  charger, or cable during the chain." and `:1620` the deviation table row "Operator touches display,
  input, lid, or power". `grep -rn "lid state\|lid open\|lid closed" docs/phase_2/ docs/process/`
  → zero hits. No `ioreg`/`pmset` lid probe exists in `joulewise/arm_readiness_evidence_t0.py`.
  WHERE: **merged to main**.
- One off-repo observation of lid state exists: `CAPTURE-NOTE.txt` in the ED-Q-L9-3 custody records
  `machine_state=AC full, lid open, …`. That is a hand-written note, not a probe.

### (c) Candidate disposition for the seat
**STILL-OPEN (nit).** The seat is adjudicating whether lid state stays discipline-only for the funded
windows.

### (d) Skeptical probes
1. `grep -niw "lid" docs/phase_2/window_runbook.md` and `grep -rn "AppleClamshellState" joulewise/ scripts/`.
2. Is there a cheap probe (`ioreg -r -k AppleClamshellState`) that the T-0 author could add, and would
   adding one require a contract amendment (new receipt row) rather than a nit fix?

---

## L9-SINGLE-SOURCE — the council's own qualification on this seat's live evidence (recorded for the sitting)

### (a) Original text (VERBATIM)
From `council-verdict.md`, "ADJUDICATED DISPOSITIONS" item 5:
> 5. **SINGLE-LENS labels** (Opus S7): L2-1, L2-COV-1, L2-EDQ-1 (one falsely-clean run) and the
>    terminal-review-trailer producer gap (B-execution only) are recorded SINGLE-LENS; a second
>    distinct-lens refuter is ORDERED before their work orders implement (launched by the
>    magistrate at verdict recording). L9's live census observation is single-source; ED-Q-L9-3's
>    quiet-state fixture is a HARD precondition to WO-CENSUS-SEMANTICS (Opus S8/W9).

From `opus-contract-refuter-findings.md` line 43:
> **S8 — L9-B1/B2's empirical basis is single-source and unreplayed.** Both refuters confirmed by regex/launchd static analysis because the sandbox denied live `pgrep`; the "~20 matches observed live" claim exists only in the L9 seat's own run. Two lenses agree on the analysis, not the observation. The remedy redefines what "quiet" means, which is claim-bearing — a loosened census admits contaminated windows. Bind ED-Q-L9-3's fixture as a hard precondition to WO-L9-1/2.

And line 73: > **W9.** L9 census re-shape gated on ED-Q-L9-3's real quiet-state fixture (see S8).

Citations: `docs/process_traces/2026-08-15-readiness-council/council-verdict.md` lines 45-50;
`.../opus-contract-refuter-findings.md` lines 43, 73; cold-fable-ruling.md line 93. WHERE: **merged to main**.

### (b) What changed since 2026-08-15 — ED-Q-L9-3 WAS EXECUTED
- **Captured 2026-08-17 23:51 PT, by the lead, not by Ed.**
  `docs/run_reports/2026-08-18-t10-session.md:109`: "**ED-Q-L9-3 quiet census** | **Captured 23:51**
  by the lead with all agent runs quiesced; 7 resident Safari agents, `watchdogd`+`watchlistd`,
  19 maintenance daemons — the L8/L9 **over-match findings confirmed as fixture ground truth**;
  lead-session lines labeled | `quiet-census/` (6 files + `CAPTURE-NOTE.txt`)".
  WHERE the record lives: **merged to main** (`docs/run_reports/2026-08-18-t10-session.md` is
  byte-identical between HEAD and `main`; last touched on main by `786183a`).
- Corroborating working note (branch-only): `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:276-280`
  — "ED-Q-L9-3 census CAPTURED (23:51): browser 7 resident Safari agents, monitor watchdogd+watchlistd,
  maintenance 19 daemons — L8/L9 over-match findings CONFIRMED as fixture ground truth; lead-session
  lines labeled in CAPTURE-NOTE.txt." WHERE: **branch-only** — this file does not exist on `main`.
- Also recorded to Ed: `docs/process/ed-morning-packet-2026-08-18.md:123-124` (merged to main).
- **THE ARTIFACTS ARE OFF-REPO AND UNCOMMITTED.** They live at
  `~/JouleWise-window-custody/ed-qual-20260817/quiet-census/` — 7 files, all timestamped
  `Aug 17 23:51`: `CAPTURE-NOTE.txt`, `captured-at.txt`, `census-agent.txt`, `census-browser.txt`,
  `census-keepawake.txt`, `census-maintenance.txt`, `census-monitor.txt`.
  `git ls-files | grep -i "quiet-census"` at head `79a4cd0` returns **nothing**; a repo-wide
  `find` for `*quiet*census*` returns nothing. **Not committed to main, not committed to the branch.**
- The `CAPTURE-NOTE.txt` is explicit about what the fixture does and does not prove:
  > captured_by=lead (Fable magistrate session), all delegated agent RUNS quiesced
  > machine_state=AC full, lid open, decisive replay COMPLETE, no measurement in flight
  > known lead-session-owned lines (ABSENT on a real ARM night when all sessions close):
  > - census-keepawake: the single caffeinate pid = T3 Code harness 5-min lease (caffeinate -i -t 300), parented by the claude process
  > - census-agent: all lines = this session (claude) + resident codex MCP servers from the tracked .mcp.json bridge (idle, no active runs) + t3 substring matches from the T3 harness
  > fixture value (the three patterns WO-L9-1/2 must fix, UNAFFECTED by the session):
  > - census-browser: 7 always-resident Safari LaunchAgents/XPC with Safari closed → confirms the L8/L9 over-match finding
  > - census-monitor: watchdogd + watchlistd via the 'watch' substring → confirms over-match
  > - census-maintenance: 19 resident Apple daemons (Spotlight/mds/XProtect/mediaanalysisd/photoanalysisd/softwareupdated etc.) → the _expect_absent underivability ground truth
- **The kernel's acceptance clause is not satisfied.** `docs/process/state_kernel.json`
  `/tasks/WO-CENSUS-SEMANTICS/acceptance/evidence[0]` reads "ED-Q-L9-3 real quiet-state fixture **is
  committed** before implementation" (kernel `:3125` at HEAD, `:3086` on main). The capture exists;
  the commit does not. `/tasks/WO-CENSUS-SEMANTICS/constraints` (`:3158`) adds: "Do not weaken either
  census from synthetic or self-nominated evidence; ED-Q-L9-3 is a hard precondition."
- **RUN_STATE and the queue are stale against the capture.** `RUN_STATE.md:519` still reads
  "WO-CENSUS-SEMANTICS (HARD-gated on ED-Q-L9-3 — **needs Ed**)" and `:426` "WO-CENSUS-SEMANTICS stays
  HARD-gated on ED-Q-L9-3", both written as if the row were unexecuted. `ed-morning-packet-2026-08-18.md:125`
  contradicts them ("OPEN: the dress rehearsal (item 4) only").

### (c) Candidate disposition for the seat
**ED-ROW — PARTIALLY DISCHARGED, PRECONDITION NOT MET AS SPECIFIED.** The seat is adjudicating three
distinct questions the record collapses: (i) does a lead-captured census satisfy an ED-QUAL row whose
text reads "with all fleets/agents closed on the real machine" when the CAPTURE-NOTE concedes the
capturing session's own `claude` / `codex mcp-server` / `t3` / `caffeinate` lines are present and were
merely *labelled* as removable; (ii) does an off-repo, uncommitted custody directory satisfy an
acceptance clause that says "**is committed**"; (iii) may WO-CENSUS-SEMANTICS unblock on that basis.

### (d) Skeptical probes
1. `git ls-files | grep -i quiet-census` at the sitting head — is the fixture committed *yet*?
   (Assembler: no, at `79a4cd0`.)
2. `cat ~/JouleWise-window-custody/ed-qual-20260817/quiet-census/CAPTURE-NOTE.txt` and
   `census-agent.txt` — the ED-QUAL text demands "all fleets/agents closed". Count the agent lines that
   belong to the capturing session. Is a *labelled* contaminated capture a valid regression fixture, or
   does it require a genuinely-closed re-capture?
3. `census-keepawake.txt` is 13 bytes — the caffeinate pid. On a real arm night `pgrep -x caffeinate`
   must return empty. This fixture therefore cannot be used to prove the keep-awake probe passes.
   Does WO-CENSUS-SEMANTICS need a *second* capture with the harness lease released?
4. Diff the fixture's `census-*.txt` against the exact argv in `arm_readiness_evidence_t0.py:989`,
   `:1387-1390` — were the captures taken with the *identical* patterns, or approximations?
   (`docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:25-27` shows the shakedown
   driver using the identical patterns; verify the 08-17 capture did too.)
5. The custody directory is outside the repo and outside any backup manifest the audit covers. Ask what
   guarantees it against loss before it is committed.
6. Reconcile `RUN_STATE.md:519` ("needs Ed") against `ed-morning-packet-2026-08-18.md:125`
   ("OPEN: the dress rehearsal only"). Which is authoritative for the sitting?

---

## L9-COVERAGE — coverage 14/16 (narrowest denominator in the fleet, flagged for priority attack)

### (a) Original record (VERBATIM)
Packet §2 seat-verdict table row:
> | L9-environmental-controls-census | GATING | NOT_READY | 14/16 | 2 | 3 | 3 | 4 | 6 | 3 |

Packet §6 (unexecuted obligations — coverage adjudication input), all six L9 rows verbatim:
> - [L9] quiet_mac_prep.sh full execution (quits user apps and sleeps the display — not sandbox-safe from an agent session; step-7 probes replicated read-only instead)
> - [L9] --arm-quiet-mode live re-probe path inside run_campaign (requires display sleep + live campaign; code path read, not run)
> - [L9] sudo-gated probes: systemsetup -getusingnetworktime read, sudo -n powermetrics (no sudo in sandbox; covered by capture lens + ED rows)
> - [L9] quiet_guard engine internals (Commit-1 is contractually inactive and non-armable; contract read, engine not audited)
> - [L9] whole_window.py adapter-wattage-continuity and controller.py enforcement wiring examined at grep/inventory level only
> - [L9] full audit of tests/test_arm_readiness_evidence_t0.py fixtures beyond confirming the probe executor is faked with empty-pgrep results

Cold ruling, coverage section (line 75):
> Seats with the narrowest denominators (L9 at 14/16, L11 at 14/16) are flagged for priority coverage attack at the re-audit; no present re-run is ordered since their verdicts are already adverse.

Council verdict, work-order certification paragraph:
> **The work-order program is NOT CERTIFIED COMPLETE** (Opus B4 cure, cold §E concurring): every seat's evidence universe was self-nominated, and the one denominator adversarially tested fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must re-enumerate every universe independently and run the adversarial coverage attack as a standing packet element.

Citations: sitting-packet-FINAL.md §2 line 32, §6 lines 245-250; cold-fable-ruling.md line 75;
council-verdict.md "VERDICT" §. WHERE: **merged to main**.

### (b) What changed since 2026-08-15
- The cold ruling's own condition — "no present re-run is ordered **since their verdicts are already
  adverse**" — is spent the moment a seat is asked to consider anything other than NOT-READY. L9's
  verdict is still adverse on the evidence above, so the deferral arguably still holds; that is the
  seat's call, not the assembler's.
- **No L9 coverage re-enumeration has been performed.** There is no L9 analogue of
  `docs/process_traces/2026-08-15-l2-reaudit/` (WO-L2-REAUDIT, `0f886d3`). `ls docs/process_traces/`
  since the council shows no L9 re-audit directory.
- Two of the six unexecuted obligations are now *partly* addressable off the back of ED-Q-L9-3
  (the pgrep-family probes were run live on 08-17), but the fixture-audit obligation
  ("full audit of tests/…fixtures beyond confirming the probe executor is faked") is untouched, and
  the assembler's own read of `tests/test_arm_readiness_evidence_t0.py:583-584` confirms the fake is
  still there.

### (c) Candidate disposition for the seat
**STILL-OPEN.** The seat is adjudicating a denominator the cold adjudicator singled out as one of the
two narrowest in the fleet, under a verdict that says closing work orders does not entitle READY and
that every universe must be independently re-enumerated at the READY-candidate sitting.

### (d) Skeptical probes
1. Who re-enumerated L9's universe? Name the artifact. (Assembler found none.)
2. `ls docs/process_traces/` for any post-council L9 audit; compare against the L2 precedent
   (`2026-08-15-l2-reaudit`, `0f886d3`), which is the only seat re-audit that exists.
3. The seat self-nominated 16 items. Run the adversarial coverage attack the verdict makes standing:
   what environmental control surface is in neither the 14 nor the 6?
4. Does the shakedown of 2026-08-18 (`docs/process_traces/2026-08-18-shakedown-first-light/`) close any
   of the six? Its driver `05-driver-as-run.sh:24-27,69-71` does run pre/post censuses with the
   production patterns — but it is labelled diagnostic/non-claim and did not run `quiet_mac_prep.sh`
   in full or the `--arm-quiet-mode` re-probe.

---

## ROW-LEVEL OPEN ITEMS
- **L9-B1 and L9-B2: no repair of any kind.** The three defect regexes at
  `joulewise/arm_readiness_evidence_t0.py:989`, `:1389`, `:1390` are byte-identical to the audit
  baseline `ac3fe1d`. The gating work order `WO-CENSUS-SEMANTICS` is `"status": "blocked"` in
  `docs/process/state_kernel.json` on **both** main and the branch.
- **The CI mask that hid B1 is still in place**: `tests/test_arm_readiness_evidence_t0.py:583-584`
  fakes every `/usr/bin/pgrep` with `exit_code=1` and empty stdout. The two Darwin "real pgrep" tests
  (`:1092`, `:1107`) predate the council (`ac3fe1d`) and assert argv binding only, not census PASS.
- **ED-Q-L9-3 is captured but NOT committed.** Artifacts are off-repo at
  `~/JouleWise-window-custody/ed-qual-20260817/quiet-census/` (7 files, 2026-08-17 23:51). The kernel
  acceptance clause requires the fixture "**is committed** before implementation" (`state_kernel.json`
  `/tasks/WO-CENSUS-SEMANTICS/acceptance/evidence[0]`). It is in no git tree at `79a4cd0`.
- **ED-Q-L9-3 was captured by the LEAD, not by Ed, and with the capturing session live.** The ED-QUAL
  text says "with all fleets/agents closed"; `CAPTURE-NOTE.txt` concedes the `claude` session, resident
  codex MCP servers, t3 matches, and a T3-harness `caffeinate` lease were all present and merely
  labelled. Whether a labelled-contaminated capture discharges a HARD precondition is unadjudicated.
- **The keep-awake leg of the fixture is unusable as-is**: `census-keepawake.txt` contains the harness's
  own caffeinate pid, so it cannot demonstrate the keep-awake probe passing on a real arm night.
- **SF1 (prewindow agent census) has no owner.** `scripts/prewindow_check.sh:150` is unchanged and the
  seat's WO-L9-3 ("align prewindow #8 with the T-0 agent pattern") appears in no queue, kernel row, or
  work order — WO-CENSUS-SEMANTICS's acceptance clauses do not cover the shell script.
- **SF2 (hazard register) and its WO-L9-4 do not exist anywhere.** Zero hits for a register document in
  `docs/`, zero hits for WO-L9-4 in kernel/TASK_QUEUE/RUN_STATE. The cold adjudicator expressly said
  this should-fix "stands".
- **SF3 (mid-workload contamination) landed neither half** — no member-level detector in
  `joulewise/idle_admission.py`, and no DOCUMENTED-UNCONTROLLED row or paper limitation.
- **All three nits unrepaired**: JW-MET-2 literals still have no §12 destination
  (`docs/phase_2/window_runbook.md:481-484`); charge state is captured but only `"AC Power"` is gated
  (`arm_readiness_evidence_t0.py:1506-1507`) — and a charge-termination step measurably perturbed the
  T10 rail probe; lid state remains prose-only (`window_runbook.md:42`) with no probe.
- **No L9 coverage re-enumeration exists.** The cold ruling flagged L9 (14/16) for priority coverage
  attack at the re-audit; the only post-council seat re-audit in the repo is L2's.
- **Stale process text the seat may trip over**: `RUN_STATE.md:426` and `:519` still describe
  ED-Q-L9-3 as owed by Ed, contradicting `docs/run_reports/2026-08-18-t10-session.md:109` and
  `docs/process/ed-morning-packet-2026-08-18.md:123-125`. Both files are on main; the contradiction is
  live on main.
- **Assembler could not verify** the exact argv used for the 2026-08-17 quiet-census captures against
  the production patterns; only `CAPTURE-NOTE.txt` and the file names were read, plus the shakedown
  driver's (different, later) invocation.
