# ROW L3 — CAPTURE + TELEMETRY (gating, xhigh tier)

Assembled mechanically from the read-only worktree `…/scratchpad/wtS0`, branch
`impl/r2-s0-mint-resolver`. `origin/main == main == 0099382`. Every pointer below was
opened and verified; where evidence could not be located, the row says so and lists the search.
**Candidate dispositions are assembled, not adjudicated; the seat rules.**

> **ASSEMBLY-PIN ANOMALY — report it to the seat, do not paper over it.** The assembler was
> instructed to work at **`4597ad4`**. At the time of reading, branch HEAD was already
> **`b92b43d`** ("Shakedown-v3 first-light run card (prep item 6b)…", = `4597ad4` + 2 commits,
> via `79a4cd0`). By the time of final verification HEAD had advanced again to **`7305e0d`**
> ("Prep sprint: paper staging landed…"), through `45e0229` ("Fresh-pass gate CLEAN through
> `b92b43d`…"). **The tree moved twice underneath this assembly.** Re-checked: no L3-scope code
> surface changed between `b92b43d` and `7305e0d` (the diff touches `README.md`, `RUN_STATE.md`,
> `TASK_QUEUE.md`, `WINDOW_STATUS.md`, `docs/decision_log.md`, `docs/process/state_kernel.json`,
> `tests/test_gen_state.py`, and new `docs/process_traces/2026-08-19-prep-sprint/` files).
> `TASK_QUEUE.md` line numbers shifted by +7 during assembly, and a new hand-authored block
> **`## WO-D149-GO-EVALUATOR` (registered 2026-08-19 night)** appeared at `TASK_QUEUE.md:373`.
> Rows are cited by **ID** as well as line; the ID is authoritative.

---

## 0. Seat identity and 2026-08-15 result

- Seat: `L3-CAPTURE-TELEMETRY-xhigh`, **GATING**, xhigh tier.
- Seat report: `docs/process_traces/2026-08-15-readiness-council/seat-reports/L3-CAPTURE-TELEMETRY-xhigh-report.md`.
- **Verdict 2026-08-15: NOT-READY.** Coverage **25/29** (`evidence_universe_count=29`).
  **0 blockers / 3 should-fix / 2 nits / 3 executed falsifiers** (`raw/L3-triage.md`;
  `sitting-packet-FINAL.md:140-144`).
- Seat scope (`L3-…-report.md:5`): "sampler lifecycle + child supervision (#127 production path),
  cadence handling, powermetrics parse/integration, channel census currency (cpu+gpu+ane and
  NOTHING else enters the integral), boundary documentation coherence post-JW-MET-1."
- The seat's own closing sentence names the closure condition
  (`L3-…-report.md:58`): "on their completion plus **ED-L3-1..4 closure** this component's
  evidence base supports READY." All four ED rows are therefore load-bearing for this row.
- Declared at the sitting (`raw/L3-triage.md` §UNEXECUTED OBLIGATIONS, verbatim):
  "No live sudo powermetrics execution of any kind (environment: no sudo, no live measurement) —
  everything privileged is emitted as ED-QUALIFICATION rows, none silently skipped."

---

## 1. FINDINGS — original text verbatim, with citation

Source of verbatim text: `raw/L3-triage.md` (extracted from
`docs/process_traces/2026-08-15-readiness-council/triage.json`, seat entry
`L3-CAPTURE-TELEMETRY-xhigh`), cross-checked against `sitting-packet-FINAL.md:140-144` (§4
should-fix/nits; this seat filed no blockers so it has no §3 entries).

### F1 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `Measured-run (adapter/controller) path has no post-teardown sampler census; kill-escalation orphan samples invisibly through the rest of a window`
- **`file_line` (verbatim):** `joulewise/adapters/powermetrics.py:1655-1663 (_stop_process); contrast scripts/validate_powermetrics_fiducial.py:562-578 (_sampler_lifetime + census)`
- **failure_scenario (verbatim):**
  > "During a funded window, powermetrics hangs >10 s past SIGTERM at member k's stop; _stop_process SIGKILLs sudo, which cannot forward it; the root powermetrics survives (executed falsifier F-B), keeps sampling at 100 ms into an unlinked file, and loads the machine through members k+1..N and their idle baselines. Only the fiducial script has the #127 detect-and-report census; the controller path has none, and the arm-time T0 monitor census (arm_readiness_evidence_t0.py:1350) runs only at arm — nothing between members detects it, so contaminated bundles do NOT fail closed against consumption."
- **Citations:** seat report §6 finding 1 (`L3-…-report.md:42`); executed falsifier F-B
  (`L3-…-report.md:31`); `sitting-packet-FINAL.md:140`.

### F2 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `ED-qualification Step 2 points at a checklist home that does not contain the checklist`
- **`file_line` (verbatim):** `docs/phase_2/ed-qualification-session.md:18-19 vs scripts/validate_powermetrics_fiducial.py:1-27`
- **failure_scenario (verbatim):**
  > "The doc says the #127 reliance checklist 'items live in the sampler module docstring'; the current docstring carries only the UNSUPPORTED-scope statement (the round-2 rewrite dropped the round-1 checklist). The executable items actually live in scripts/ed_session/sampler-checklist.sh, and no staging step copying it to the referenced /tmp/ed-session/ path exists in the repo. At the single batched Ed session, the operator or the preparing loop follows the pointer, finds no items, and ED-QUALIFICATION rows get closed against an unenumerated or improvised checklist — corrupting the exact closure the council READY depends on."
- **Citations:** seat report §6 finding 2 (`L3-…-report.md:43`); `sitting-packet-FINAL.md:141`.

### F3 — should_fix

- **Severity:** `should_fix`
- **Title (verbatim):** `ED sampler checklist qualifies cadence at 1 Hz while every production surface runs 100 ms`
- **`file_line` (verbatim):** `scripts/ed_session/sampler-checklist.sh:59,106-110 (-i 1000 -n 5) vs packs power_hz=10.0, powermetrics_fiducial.py:63 (SAMPLING_INTERVAL_MS=100), window_runbook.md:638`
- **failure_scenario (verbatim):**
  > "Step 2's 'record cadence observations' captures five 1000 ms intervals; the cadence row closes on 1 Hz evidence. The window then runs at 100 ms, where powermetrics' realized-interval behavior on the current OS build was never observed live; a post-update realized-cadence anomaly at 100 ms (elapsed_ns integration stays correct, but rollover-gate timing, drain budgets, and window sample-count planning assume ~100 ms) surfaces only inside the funded window."
- **Citations:** seat report §6 finding 3 (`L3-…-report.md:44`); `sitting-packet-FINAL.md:142`.

### F4 — nit

- **Severity:** `nit`
- **Title (verbatim):** `Post-JW-MET-1 residual: retained related-work draft still describes JouleWise with system-on-chip boundary language`
- **`file_line` (verbatim):** `docs/paper/related_work_draft.md:19`
- **failure_scenario (verbatim):**
  > "JW-MET-1 narrowed all five draft-v1.md sites (31ccef5), but the retained draft's 'integrates named system-on-chip power channels' (subject: JouleWise) was not swept; a future paper train copying from the retained draft reintroduces the overbroad boundary claim. (Third-party descriptions of Silicon Showdown's whole-SoC boundary are correct and not affected.)"
- **Citations:** seat report §6 finding 4 (`L3-…-report.md:45`); `sitting-packet-FINAL.md:143`.

### F5 — nit

- **Severity:** `nit`
- **Title (verbatim):** `samplers_available metadata echoes the requested list rather than a probed census`
- **`file_line` (verbatim):** `joulewise/adapters/powermetrics.py:1175-1179`
- **failure_scenario (verbatim):**
  > "After any rc-0 one-sample probe, device metadata reports samplers_available=[cpu_power,gpu_power,ane_power,thermal] with method='requested_sampler_probe'. A bundle auditor reads it as a probed census; if the thermal sampler were silently absent (thermal_pressure is optional in the parser), the metadata would still claim it available. The label is honest but the field name invites over-reading."
- **Citations:** seat report §6 finding 5 (`L3-…-report.md:46`); `sitting-packet-FINAL.md:144`.

### Work orders (verbatim, `raw/L3-triage.md` §WORK ORDERS)

- **WO-L3-1:** "Add the detect-and-report post-teardown sampler census to the measured-run stop path (adapter stop_sampling_with_evidence/_take_measured_capture or controller finalization), mirroring scripts/validate_powermetrics_fiducial.py's _report_powermetrics_census, and record findings into bundle metadata so a mid-window orphan is at least detectable at reduce time. Keep detect-and-report-only semantics pending WO-SAMPLER-SUPERVISOR."
- **WO-L3-2:** "Fix docs/phase_2/ed-qualification-session.md Step 2 to name scripts/ed_session/sampler-checklist.sh as the checklist home (and either add the /tmp/ed-session staging step to the loop's prep or reference the repo path directly); align the module docstring pointer or restore an item list there."
- **WO-L3-3:** "Add a second short capture at -i 100 (production cadence) to scripts/ed_session/sampler-checklist.sh's cadence-record step, or explicitly annotate the row as supervision-only and move cadence currency to the T0 probes."
- **WO-L3-4 (nit-grade):** "sweep docs/paper/related_work_draft.md:19 boundary wording; rename or probe-derive samplers_available metadata."

### Unexecuted obligations declared at the sitting (verbatim)

- "tests/test_calibration_writer_crash_matrix.py NOT run at this seat (hosted-pathological per WO-CRASHMATRIX-RELIABILITY; a sibling seat was executing it live during my audit — concurrent duplicate execution would have contended; its writer-crash coverage is L2's scope)."
- "No live sudo powermetrics execution of any kind (environment: no sudo, no live measurement) — everything privileged is emitted as ED-QUALIFICATION rows, none silently skipped."
- "joulewise/adapters/mock_telemetry.py not audited (not on the funded-window path; pack member verified pinning telemetry_backend=powermetrics)."
- "scripts/ed_session/rail-probe.sh read for role, not line-audited (JW-MET-3 is documentation-grade)."
- "quiet_guard.py / quiet_guard_process.py header-ruled out of this seat's scope (agent-session custody guard — seats 1/9 territory)."
- "Rich-telemetry consumers (salvage_dangler.py, floors common-mode) and reducer integration internals corroborated only at the seam (reduce.py D-018 policy: only manifest rails summed, non-manifest rows ignored) — deep audit is L4's scope."
- "Long-stream soak of the admission stream cursor (_advance_stream_cursor over hours-scale files) not executed; covered by unit tests incl. the 64KiB-chunk large-stream test only."

---

## 2. WHAT CHANGED SINCE 2026-08-15

### 2.1 F1 / WO-L3-1 — measured-run post-teardown census: **NO REPAIR FOUND**

- `_stop_process` is byte-unchanged, now at `joulewise/adapters/powermetrics.py:1664-1671`
  (finding cited `:1655-1663`):
  ```python
  @staticmethod
  def _stop_process(process: subprocess.Popen[bytes]) -> None:
      if process.poll() is None:
          process.terminate()
      try:
          process.communicate(timeout=10.0)
      except subprocess.TimeoutExpired:
          process.kill()
          process.communicate()
  ```
- `grep -n "census\|pgrep\|orphan" joulewise/adapters/powermetrics.py` returns **zero hits**. The
  four `_stop_process` call sites (`:415`, `:422`, `:432`, `:861` — the last inside
  `_take_measured_capture`) are unchanged and none censuses afterwards.
- Two commits touched the adapter since the council, **both branch-only (not on `origin/main`)**:
  `4efea13` "Rate-aware clock anchor: exact set-membership estimator + method identity" and
  `b7e5730` "S1: anchor-v3 production flip + D-079 r5 (science-neutral, 19-member replay proven) +
  claim barrier (D-146)". Neither adds a census.
- The contrast path is unchanged and still detect-and-report only:
  `scripts/validate_powermetrics_fiducial.py:958-985` `_sampler_lifetime` → `finally:
  _terminate_powermetrics(process)` then `_report_powermetrics_census(event_reporter)` (def at
  `:926`).
- The arm-time T0 monitor census the finding names still exists, now at
  `joulewise/arm_readiness_evidence_t0.py:1390`, and still runs **only at arm**.
- **WO-L3-1 has no queue row, no kernel row, and no landing record.** Searched: `TASK_QUEUE.md`,
  `RUN_STATE.md`, `docs/process/state_kernel.json`, and a tree-wide grep for `WO-L3-1`…`WO-L3-4` —
  the only hits are `docs/process_traces/2026-08-15-readiness-council/triage.json` and the seat
  report itself.
- **WO-SAMPLER-SUPERVISOR** (which the work order names as the follow-on that would lift
  detect-and-report-only) remains **registered but unimplemented**: `TASK_QUEUE.md:293-316`,
  "Until landed, the production script's census is detect-and-report only and full ownership is
  documented UNSUPPORTED. **Not on any critical path.**" There is no kernel task row for it
  (`grep WO-SAMPLER-SUPERVISOR docs/process/state_kernel.json` → nothing). Its module docstring
  statement is likewise unchanged (`scripts/validate_powermetrics_fiducial.py:22-26`).

### 2.2 F2 / WO-L3-2 — checklist home pointer: **NO REPAIR FOUND**

- `docs/phase_2/ed-qualification-session.md` has **zero commits since 2026-08-15**
  (`git log --since=2026-08-15 -- docs/phase_2/ed-qualification-session.md` → empty). Step 2 at
  `:17-25` still reads, verbatim: "The #127 production sampler's reliance checklist (its items live
  in the sampler module docstring; the capture-lens audit enumerates them as rows): run the commands
  the loop has staged in `/tmp/ed-session/sampler-checklist.sh` when pinged".
- The referenced docstring is still checklist-free:
  `scripts/validate_powermetrics_fiducial.py:1-27` carries the protocol description and the
  UNSUPPORTED-scope paragraph, no item list.
- **Partial mitigation not in the repo docs:** an out-of-band ordered checklist was authored for
  the operator evening — `docs/process/ed-evening-checklist.md` (`aa90dc3`, **ON `origin/main`**),
  item 4: "**Sampler checklist + rail probe + keyboard-backlight rows** — per the qualification
  script items". It points back at the same unchanged qualification script. The script itself
  self-stages (`scripts/ed_session/sampler-checklist.sh:23-27` creates `SESSION_ROOT=/tmp/ed-session`
  and its own log/capture paths), so the "no staging step exists" half of the finding is
  operationally moot even though the doc was never corrected.
- Two `scripts/ed_session/*` commits landed, both **ON `origin/main`**, both from defects the live
  operator run flushed — neither is WO-L3-2: `d873f77` "ed_session: guard empty-args re-exec against
  macOS bash 3.2 set -u (unbound ORIGINAL_ARGS[@])" and `e5dc38a` "ed_session: probe command-scoped
  sudo authorization, not blanket sudo -n true".

### 2.3 F3 / WO-L3-3 — 100 ms cadence leg: **NOT ADDED to the checklist; but the 100 ms cadence WAS observed live on 2026-08-18, and it is ~13 % long**

- **The script is unchanged.** `scripts/ed_session/sampler-checklist.sh:59` and `:106-111` still
  build exactly one command, at 1 Hz: `-b 0 -i 1000 -n 5`. No `-i 100` leg, no annotation
  demoting the row to supervision-only. WO-L3-3 is **NOT DONE**.
- **However — and this is new evidence no seat has seen — live 100 ms captures on the current OS
  build now exist.** On 2026-08-18 the lead ran the v3 fiducial validator live under Ed's D-127
  sudo grant, 10 times, at `SAMPLING_INTERVAL_MS = 100`
  (`joulewise/powermetrics_fiducial.py:65`; the live command is assembled at
  `scripts/validate_powermetrics_fiducial.py:1765-1777` with `-b 0 -i <SAMPLING_INTERVAL_MS>` and
  **no** `-n <count>`).
  - Custody: `/Users/edr/JouleWise-window-custody/shakedown-20260818/runs/instrument_validation/`
    (4 bundles: `20260818T045736-4d9e9db9`, `20260818T163440-8eab7b5a`, `20260818T165057-81acfefe`,
    `20260818T165459-f22b25aa`) and `.../runs/spacing_probe/` (6 bundles,
    `20260818T173136-bc9bff8e` … `20260818T182149-a7e8b412`).
  - Each raw `powermetrics.plist` (~91 MB, root-owned, retained) carries
    `hw_model = Mac15,9` and `kern_osversion = 25F84`; each `instrument_evidence.json` carries
    `"hardware_model": "Mac15,9"`, `"os_build": "25F84"`, `"sampling_interval_ms": 100`.
  - **Realized cadence: ≈ 113 ms at a configured 100 ms** — ~1745 records over a ~196.8 s capture;
    per-record `elapsed_ns` second-record values 112.09–114.20 ms across all ten bundles.
    Compare the 1 Hz leg, where realized was 1.0114–1.0136 s (≈1.1–1.4 % long). **The 100 ms
    overshoot is ~13 %** — an order of magnitude worse in relative terms, and precisely the
    "realized-interval behavior on the current OS build was never observed live" that F3 warned
    about. Energy integration is unaffected (per-record `elapsed_ns` is used), but F3's named
    consumers — "rollover-gate timing, drain budgets, and window sample-count planning assume
    ~100 ms" — have not been re-derived against 113 ms by anyone.
  - Driver of record: `docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:56-61`
    (`--allow-live --power-policy ac_high_power`); custody trace
    `docs/process_traces/2026-08-18-shakedown-first-light/` (`4db15bd`, ON `origin/main`) and
    `docs/process_traces/2026-08-18-t10-t11-working-notes/` (`cbcb5ea`, **branch-only**).
  - **Executed by the lead/agent bench session, not by Ed** (`docs/run_reports/2026-08-18-t10-session.md:1056`
    "Bench work by the lead this stretch (rule-9 threshold): the shakedown driver and its hardening…").
    Ed licensed the window (`…/2026-08-18-t10-t11-working-notes/trace-notes.md:315-317`:
    "Ed pinged ~01:15 … shakedown-window license requested; explicitly NOT inferring measurement
    consent from 'I guess'.").
- **Nothing at 100 ms since 2026-08-18.** The 2026-08-19 profiler pilot was a dry run:
  `/Users/edr/JouleWise-window-custody/profiler-pilot-20260818/dryrun/wrapper-20260818T223746.log`
  — "== dry run: no fences, no sudo, no capture, no generation".

### 2.4 F4 / F5 nits — **NO REPAIR FOUND**

- **F4:** `docs/paper/related_work_draft.md` has **zero commits since 2026-08-15**; line 19 still
  reads "JouleWise applies this lineage to `powermetrics` on Apple silicon. It **integrates named
  system-on-chip power channels** only inside runtime-emitted phase boundaries…".
- **F5:** `samplers_available` is unchanged, now at `joulewise/adapters/powermetrics.py:1183-1187`
  (finding cited `:1175-1179`):
  ```python
  self._device_metadata["powermetrics"]["samplers_available"] = SAMPLERS.split(",")
  self._device_metadata["powermetrics"]["samplers_probe"] = {"ok": True, "method": "requested_sampler_probe"}
  ```
  The unprobed default (`"probe-unavailable"`) at `:1449` and `:1457` is also unchanged. No rename,
  no probe derivation.

### 2.5 WO-T0-PRODUCER (PR #152 / `a61ac92`) — merged; relevant to this seat only at the seam

- `TASK_QUEUE.md` Completed table: "**WO-T0-PRODUCER** | P1 Phase Gate | 2026-08-15 | Implement the
  integrated nine-input T-0 producer, dwell enforcement, D-127 clock route, and chain/manifest
  fixes | … Merged via **#152 (`a61ac92`)** at D-121-verified head **`9e8936a`**:
  `scripts/capture_t0_step.py`, the strict R2 plan resolver, the D-127 privileged clock route, and
  dwell/env hardening landed; the F4 honest-contract deltas ride the follow-up t0-producer lane per
  the 2026-08-15 provenance ruling." `a61ac92` is **ON `origin/main`**; the merge head `9e8936a`
  is branch-only.
- Follow-up lane commit **`65cc0f3`** (ON `origin/main`): "T-0 F4 honest contract: D-134 cl.6
  overclaim superseded (production-interface/ceremony rule, no operator-fabrication-resistance
  claim), TRUSTED-OPERATOR limitation v1 registered, public execute/monotonic_ns/utc_now injection
  seam removed from capture_t0_step (module-private test hook), runbook + docstrings corrected".
- **For L3 specifically:** WO-T0-PRODUCER supplies the nine T-0 input files and the ≥10-min dwell;
  it does **not** touch `_stop_process`, the sampler census, the cadence surfaces, or
  `samplers_available`. The D-127 privileged clock route it landed is, however, the grant that made
  the 2026-08-17 and 2026-08-18 live sudo captures possible at all (sudoers digest `7dfe980b…`,
  `docs/run_reports/2026-08-18-t10-session.md:104`).

### 2.6 Other work orders named in the assembler brief

- **WO-CENSUS-SEMANTICS (A4):** kernel row exists (`docs/process/state_kernel.json:3122-3168`) with
  acceptance "ED-Q-L9-3 real quiet-state fixture is committed before implementation" (`:3125`) and
  fence "…ED-Q-L9-3 is a hard precondition" (`:3158`). Generated queue at the current head:
  row **`A4`** at `TASK_QUEUE.md:545` (was `:538` pre-drift) — **`BLOCKED — ED-Q-L9-3`**; kernel dependency `state: pending`, `evidence: null` (`state_kernel.json:3140-3150`). **Zero implementation**; both L9 census probes
  are byte-unchanged. Its ED-Q-L9-3 precondition is **not met as the acceptance defines it**: the
  2026-08-17 quiet census exists only in out-of-repo custody
  (`~/JouleWise-window-custody/ed-qual-20260817/quiet-census/`) and was **never committed** — see
  `rows/ROW-L9.md` §3 for the full evidence and its two qualifications.
- **WO-SAMPLER-SUPERVISOR:** see §2.1 — registered only, `TASK_QUEUE.md:293-316`, "Not on any
  critical path". This bounds what WO-L3-1 can ever achieve (detect-and-report is the ceiling).
- **WO-DETECT-PULSES-BUDGET (A5):** implementation commit **`ceda7a6`** "WO-DETECT-PULSES-BUDGET:
  deterministic projection budget + anchor-unresolved bypass + governed nonconvergent abort" is
  **ON `origin/main`**, and its effect is visible in the live shakedown output
  (`driver-20260818T045235.log` → `"status": "invalid" … "invalid_evidence_disposition":
  "detection_nonconvergent", "cell_budget": 100000, "trigger": "evaluated_cell_budget"` — the
  governed abort fired on real data). Yet the generated queue still shows
  `A5 | WO-DETECT-PULSES-BUDGET | P1 Phase Gate | PARTIAL; READY [AGENT]`, and `RUN_STATE.md` keeps
  branch `impl/wo-detect-pulses-budget @ 5449e58` pending "inside the atomic re-freeze" (the branch
  edits D-079-pinned estimator inputs). **The queue status string and the commit graph disagree** —
  flagged for the seat, not adjudicated.
- **Capture-era system (landed 2026-08-19) and D-149 no-hands automation:** see §2.7.

### 2.7 The capture-era system landed 2026-08-19 — **a PRODUCTION CAPTURE FLIP inside this seat's audited module, unre-audited by any seat**

This is the most consequential change to L3's scope since the sitting, and it is **branch-only**.

- **Landing commit `b7e5730`** "S1: anchor-v3 production flip + D-079 r5 (science-neutral,
  19-member replay proven) + claim barrier (D-146)" — 29 files, +1245/−112. Its own message
  (verbatim): "(2) **adapter flip**, strict verify era dispatch incl. the :1575 fail-open fix,
  campaign-gate equality, environment-admission stored-method dispatch, fiducial fail-closed,
  controller incomplete-evidence, r5 issuance + rebind rows; (3) capture_pipeline_superseded
  barrier via one shared predicate + calibration era diagnostics; (4) A1-A8 attack tests + contract
  era sections + **748-bundle census**."
  Fix rounds on the same branch: `1ec5dc4`, `3038eeb`, `d279bd2` ("missed census site"), `6f00d05`,
  and `d8f1202` (S2 r6 golden re-derivation). **None is on `origin/main`.**
- **What it did to `joulewise/adapters/powermetrics.py`** — the file this seat read in full
  (universe item 1, "2251 lines, read in full", `L3-…-report.md:10`). Verified by
  `git show b7e5730 -- joulewise/adapters/powermetrics.py` (+28/−… over 4 call sites):
  - the import changed from `derive_powermetrics_clock_evidence_v2` to
    `resolve_clock_evidence_deriver` + `ACTIVE_CAPTURE_ANCHOR_METHOD`;
  - **all four live clock-evidence sites** now call
    `resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)(...)` instead of the v2 deriver;
  - the `TIMESTAMP_DERIVATION` metadata string — which every bundle carries — was rewritten from
    "the admissible interval formed by **intersecting the censored native whole-second
    constraints** … (**p2-038.2**)" to "the admissible **rate-aware set-membership** interval
    formed from native whole-second constraints and paired clock stamps under the affine wall rate
    model (**p2-038.3**)";
  - a docstring changed from "Project parsed records onto the **v2** anchor estimator's native
    evidence" to "…onto the **p2-038.3** anchor's native evidence".
  A second branch-only commit `4efea13` "Rate-aware clock anchor: exact set-membership estimator +
  method identity" is the estimator itself.
- **Core of the era system:** `joulewise/uncertainty_evidence.py` —
  `ACTIVE_CAPTURE_ANCHOR_METHOD = CLOCK_METHOD_V3` (`:1298`),
  `CLAIM_BEARING_ANCHOR_METHODS = frozenset({CLOCK_METHOD_V3})` (`:1299`),
  `capture_pipeline_refusal()` (`:1302-1325`) returning `None` / `capture_pipeline_absent` /
  `capture_pipeline_superseded`; consumed at the three claim-admission sites
  (`analysis_engine/claims.py:135,173`, `floor_extraction.py:190`, `whole_window.py:199`) plus
  `reduce.py`, `controller.py:1362`, `calibration_bracketing.py:1274`, `cli.py:1527,1549,1569`,
  `arm_readiness.py`, `environment_admission.py`, `powermetrics_fiducial.py`.
  Tests: `tests/test_capture_pipeline_era.py`.
- **Authority:** D-146 (`docs/decision_log.md:169` index, `:8844` body), ONE home
  `docs/process_traces/2026-08-19-r1-r2-codesign/13-r1-ruling.md`. D-148 clause (7)
  (`docs/decision_log.md:171`) registers the consequence: "the stored anchor-v2 population
  (**748 repo-tree bundles**) gets a REGISTERED LIMITATION paragraph: permanently non-claim-bearing
  on estimator grounds, mechanically enforced by the D-146 barrier."
- **Why the seat must weigh this.** L3's charter is "powermetrics parse/integration" and
  "cadence handling". The seat audited the **v2** capture path at `ac3fe1d`/`8937dec`; the
  production capture path is now **v3**, changed four days later, on a branch, and **no seat has
  re-audited it**. The council's Phase-3 program calls for "focused re-audit of pack/custody-bearing
  seats (L1, L5, L7 minimum)" (`council-verdict.md:102-104`) — **L3 is not on that list**, yet
  L3's central module was flipped. Separately: the ten live 100 ms captures of 2026-08-18 (§2.3)
  predate or straddle this flip and were produced by a *clone* under
  `~/JouleWise-window-custody/shakedown-20260818/clone/`, so the code that produced them is not
  necessarily the code at HEAD.
- **Sampler lifecycle is NOT touched by the era work** — spawn/signal/reap is unchanged; ownership
  remains WO-SAMPLER-SUPERVISOR, unlanded. F1 stands exactly as filed.

### 2.8 D-149 no-hands window automation — scope note

- **Branch-only, not on `origin/main`:** `0e96dbb` "D-149: standing conditional T-0 GO — full
  no-hands window automation (Ed); kernel fences updated (regen + pins green)"; `79a4cd0` "D-149
  GO-receipt template + evidence runbook (prep item 6; evaluator script deferred to gauntlet)"
  (`docs/process/d149-go-receipt-template.md`); `b92b43d` "Shakedown-v3 first-light run card (prep
  item 6b): turnkey window lane — GO receipt, in-band check against the r6 band, D-078 refusal
  handling". Decision-log index `docs/decision_log.md:172`, body `:8865-8870`.
- **It re-scopes an operator clause in the kernel:** `git show 0e96dbb -- docs/process/state_kernel.json`
  deletes `"Ed remains the physical launch authority"` from the D117-W-ALPHA/BETA/GAMMA fences and
  substitutes `"T-0 GO auto-issues per D-149 when its five recorded conditions pass (no-hands
  windows); hands-required work remains Ed's"`. `docs/phase_2/*.md` contain **zero** occurrences of
  `D-149`/`no-hands`/`unattended`, so `window_runbook.md` still asserts Ed's §5A tap and E-10
  physical launch verbatim at HEAD — **kernel and runbook now disagree on who launches.**
- **Effect on this seat's rows:** none of D-149 repairs F1–F5, and none moots ED-L3-1..4 — the
  sampler-lifecycle, cadence, and channel-census rows are properties of the machine and the OS
  build, not of who presses Return. D-149 does, however, keep "backlight" and "new sudo" explicitly
  on Ed's side (`decision_log.md:172`, verbatim: "REMAINS ED'S: anything needing hands (cables,
  backlight, reboots, new sudo), claim publication, exact-byte confirmation"), which is why
  ED-L3-1/-3 are not automatable. Two facts sharpen F1 under automation: (i) the window was
  *already* unattended after launch (`window_runbook.md:1070-1072`, "Ed steps away immediately
  after invoking E-10 and does not touch or monitor the machine"), so D-149's delta is the launch
  and the GO decision; but (ii) with nobody starting it either, the F1 orphan scenario ("keeps
  sampling at 100 ms into an unlinked file, and loads the machine through members k+1..N") has
  **no human observer at any point** — and, verified above, **no measured-run census exists, and
  the shakedown's own post-teardown censuses were never durably written** (§3, ED-L3-2).
  D-149's C1 also requires "ED-QUALIFICATION rows closed", making its auto-GO depend on this
  sitting's verdict on ED-L3-1..4. **No seat has audited D-149.** See probe §5.8.

---

## 3. ED-QUALIFICATION ROWS

Charter classification as the rows declare it: **all four L3 rows are `(stable)` capabilities**, not
T0. Under the charter amendment adopted at this sitting (Opus S12, `council-verdict.md:54-57`), a
**READY-CANDIDATE sitting binds charter:77-78 — "only T0 rows may remain open."** ED-L3-4 carries
its own reopening trigger: "REOPENS on any OS update before the window."

**All located closure evidence for this seat lives OUTSIDE the repository**, under
`/Users/edr/JouleWise-window-custody/`. Nothing in the tree commits, hashes, or manifest-binds it.

---

### ED-L3-1 — Live sudo/powermetrics checklist

**Row text (VERBATIM,** `sitting-packet-FINAL.md:183` **/** `raw/L3-triage.md` **):**
> "ED-L3-1 (stable): Live sudo/powermetrics checklist — run scripts/ed_session/sampler-checklist.sh (sudo -n grant, empty pre-census, supervised 5-sample capture under _sampler_lifetime, empty post-teardown census, cadence record, parse by the pinned parser). This is the long-owed row gating reliance on #127's production sampler commit (RUN_STATE 'ED-OWED' item 3). Close only after WO-L3-2/WO-L3-3 fix the checklist's documented home and add the 100 ms leg."

**Charter classification as declared in the row:** `(stable)`.

**LOCATED CLOSURE EVIDENCE — EXECUTED LIVE ON THE MEASUREMENT MACHINE, BY ED, with a durable
recorded receipt (out-of-repo custody). The row's own closing PRECONDITION is UNMET.**

- Path: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/` —
  `sampler-checklist-20260818T011840Z.log` (1015 B), its capture
  `sampler-checklist-20260818T011840Z.plist` (264,911 B), plus two earlier attempts
  (`…010430Z.log` 0 B; `…011634Z.log` 640 B).
- **Live sudo ran:** yes. The successful log records every step verbatim:
  ```
  1. Confirm the intended command and evidence directory.
  /usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 5 --samplers battery,cpu_power,gpu_power,ane_power,thermal --format plist -o /tmp/ed-session/sampler-checklist-20260818T011840Z.plist
  2. Confirm non-interactive sudo before any live sampler starts.
  PASS: sudo -n authorization is available.
  3. Census pre-existing sampler processes.
  PASS: no powermetrics process found.
  4. Run a five-sample capture under the production sampler-lifetime supervisor.
  Press Return to start the supervised five-sample check: records=5
  cadence_s=1.011352,1.013561,1.013068,1.013052,1.013095
  cadence_mean_s=1.012826
  5. Verify teardown left no orphaned sampler process.
  PASS: no powermetrics process found.
  6. Record the result.
  PASS: supervised sampler lifecycle, orphan census, and cadence record completed.
  ```
- **Ed at the keyboard:** the `Press Return to start the supervised five-sample check:` prompt
  (`sampler-checklist.sh:94-95`) was answered interactively — this is a real operator run, not a
  scripted or `--dry-run` invocation. The earlier `…011634Z.log` is the genuine refusal
  (`sudo: a password is required` → `REFUSE: sudo -n is unavailable`) that produced the fix
  `e5dc38a`; the 0-byte `…010430Z.log` is the bash-3.2 crash that produced `d873f77`.
- **Machine / date:** measurement Mac; capture timestamp inside the plist
  `2026-08-18T01:18:48Z` (= 2026-08-17 18:18 PT). **Durably recorded:** yes — log + full plist.
- **Each element of the row, checked:** sudo -n grant ✅ (step 2 PASS); empty pre-census ✅
  (step 3); supervised 5-sample capture under `_sampler_lifetime` ✅ (the inline Python at
  `sampler-checklist.sh:97-126` imports `_sampler_lifetime` from
  `scripts.validate_powermetrics_fiducial` and `parse_powermetrics_records` from the adapter);
  empty post-teardown census ✅ (step 5); cadence record ✅ (five intervals + mean); parse by the
  pinned parser ✅ (`records=5` came from `parse_powermetrics_records`).
- **THE ROW'S CLOSING CONDITION IS NOT SATISFIED.** The row says "Close **only after** WO-L3-2/WO-L3-3
  fix the checklist's documented home and add the 100 ms leg." Verified at 4597ad4:
  **WO-L3-2 is NOT DONE** (`ed-qualification-session.md` has zero commits since the council; the
  docstring still has no items) and **WO-L3-3 is NOT DONE** (`sampler-checklist.sh` still runs
  `-i 1000 -n 5` only). The run therefore closed the row **against exactly the checklist the seat
  said must be fixed first** — the "tired-operator hazard" F2 named, realised.
- **Corroborating narrative:** `docs/run_reports/2026-08-18-t10-session.md:105` —
  "**Sampler lifecycle (ED-QUAL step 2)** | PASS — cadence mean **1.0128 s**, zero orphans |
  `ed-session-evidence/sampler-checklist-*.log` (3 runs + plist)";
  `docs/process/ed-morning-packet-2026-08-18.md:114` — "Sampler lifecycle (cadence 1.0128 s, zero
  orphans)."
- **The string `ED-L3-1` appears nowhere outside the 2026-08-15 council packet** — no run report,
  decision-log entry, queue row, or receipt names this row as closed. The closure is inferred from
  the artifact, not asserted anywhere.

---

### ED-L3-2 — Live SIGTERM-relay termination

**Row text (VERBATIM,** `sitting-packet-FINAL.md:184` **):**
> "ED-L3-2 (stable): Live SIGTERM-relay termination — confirm on the current OS build that `sudo -n powermetrics` exits within the 10 s grace on SIGTERM to sudo (normal path) ; the executed falsifier F-B shows that if it ever does not, the SIGKILL escalation strands a root orphan no software census on the measured-run path detects. One observation, any tap block."

**Charter classification as declared in the row:** `(stable)`; "One observation, any tap block."

**LOCATED EVIDENCE — the physical observation EXISTS (ten times over), but it was produced by an
AGENT session on the fiducial path, was never labelled as this row, and its post-teardown orphan
censuses were NOT durably recorded. The ED-QUAL checklist run did NOT exercise SIGTERM at all.**

**(a) What the ED-QUAL run did NOT show.** The checklist command carries `-n 5`, so powermetrics
self-exits after five samples; `process.wait(timeout=20)` returns first and
`_terminate_powermetrics`'s `poll() is not None` early-return means **no SIGTERM was ever sent**.
The step-5 `PASS: no powermetrics process found.` is a *self-exit* census, not a relay observation.
The same is true of all four rail-probe arms (`-n 30`, each logging
`PASS: arm <name> captured and sampler exited.`). **The t10 report's "zero orphans" line
(`:105`) is therefore 1 Hz self-exit evidence, not ED-L3-2 evidence.**

**(b) What did show it — 10 live relays, all far inside the grace.** The v3 fiducial live path
builds its command with **no `-n <count>`** (`scripts/validate_powermetrics_fiducial.py:1765-1777`),
so the sampler runs unbounded and MUST be signalled. `_sampler_lifetime` calls
`_terminate_powermetrics(process)` on the `sudo -n` parent
(`scripts/validate_powermetrics_fiducial.py:883-895`, `SAMPLER_TERMINATE_TIMEOUT_S = 10.0` at
`:131`) — **exactly the ED-L3-2 topology.** From the ten bundles' `instrument_evidence.json`
`clock_stamps` (`post_parse − sampling_stopped`, an upper bound on terminate+reap):

| bundle | teardown_s |
|---|---|
| `instrument_validation/20260818T045736-4d9e9db9` | 0.0228 |
| `instrument_validation/20260818T163440-8eab7b5a` | 0.0228 |
| `instrument_validation/20260818T165057-81acfefe` | 0.0047 |
| `instrument_validation/20260818T165459-f22b25aa` | 0.0107 |
| `spacing_probe/20260818T173136-bc9bff8e` | 0.0047 |
| `spacing_probe/20260818T173559-b192892b` | 0.0047 |
| `spacing_probe/20260818T175421-912e9ed4` | 0.0047 |
| `spacing_probe/20260818T175854-918be2ce` | 0.0048 |
| `spacing_probe/20260818T181717-4bae4cd2` | 0.0192 |
| `spacing_probe/20260818T182149-a7e8b412` | 0.0228 |

Max 22.8 ms against a 10 s grace; no `TimeoutExpired` (which would have cost ≥10 s), and every
plist parsed cleanly with 1744–1749 complete records — i.e. **sudo relayed SIGTERM and root
powermetrics flushed and exited on the current OS build (Mac15,9 / 25F84)**, ten times.
Custody: `/Users/edr/JouleWise-window-custody/shakedown-20260818/`. **Executed by:** the lead/agent
bench session, not Ed.

**(c) Why the seat cannot simply mark this closed.**
1. **Wrong actor and wrong labelling.** The row is an ED-QUALIFICATION row; this was an agent run.
   The string `ED-L3-2` appears **nowhere** outside the 2026-08-15 council packet.
2. **The post-teardown orphan census was NOT durably recorded.** The driver intended to write it
   (`docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:70-71` writes
   `census-monitor-post.txt` and `census-orphan-post.txt` into `$CUST/fences/`), but every
   `driver-*.log` terminates inside step 4, and
   `/Users/edr/JouleWise-window-custody/shakedown-20260818/fences/` contains **no**
   `census-monitor-post.txt` and **no** `census-orphan-post.txt` — only the `-pre` censuses,
   clock/power/thermal state files. The in-process diagnostic
   (`SAMPLER_CENSUS_DIAGNOSTIC = "powermetrics_post_teardown_census"`,
   `scripts/validate_powermetrics_fiducial.py:132`) emits **only when there are findings**, and no
   such event appears in any of the ten `events.jsonl`. The narrative claim
   `docs/process_traces/2026-08-18-t10-t11-working-notes/trace-notes.md:339` — "Machine clean
   (clock On via trap, no orphans)" — has **no durable artifact behind it**.
   So: SIGTERM relay is observed; *the absence of an orphan after it* is asserted, not recorded.
3. **The row's own hazard is the SIGKILL branch, which was never reached.** Ten fast, clean
   teardowns do not falsify "if it ever does not"; they raise the prior. F-B remains the only
   evidence about the failure branch, and F-B was a **simulation without privileges**
   (`L3-…-report.md:31`: "replicates the `sudo -n` signal topology without privileges").

---

### ED-L3-3 — JW-MET-3 rail probe

**Row text (VERBATIM,** `sitting-packet-FINAL.md:185` **):**
> "ED-L3-3 (stable): JW-MET-3 rail probe — scripts/ed_session/rail-probe.sh ABBA keyboard-backlight arms with --samplers battery,cpu_power,gpu_power,ane_power,thermal; documentation-grade rail-inclusion differential (the LED-outside-boundary verdict already stands on code evidence)."

**Charter classification as declared in the row:** `(stable)`, documentation-grade.
*(This row is the L3 twin of L9's ED-Q-L9-2 — one execution serves both; see `rows/ROW-L9.md` §3.)*

**LOCATED CLOSURE EVIDENCE — EXECUTED LIVE, BY ED, four real sudo arms, durable receipts
(out-of-repo custody). Contaminated conditions, recorded.**

- Path: `/Users/edr/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/rail-probe-20260818T011943Z/`
  — `max-1.plist`, `off-1.plist`, `off-2.plist`, `max-2.plist` (~1.59 MB each, 30 records each),
  `rail-probe-results.json`, `rail-probe.log`.
- **Live sudo ran:** yes; each arm's literal command is logged, e.g.
  `command=/usr/bin/sudo -n /usr/bin/powermetrics -b 0 -i 1000 -n 30 --samplers battery,cpu_power,gpu_power,ane_power,thermal --format plist -o /tmp/ed-session/rail-probe-20260818T011943Z/off-1.plist`,
  and the operator was prompted between arms ("Press Return only after the requested backlight level
  is visually stable:"). Final log line:
  `PASS: ABBA rail probe complete; preserve /tmp/ed-session/rail-probe-20260818T011943Z.`
- **Sampler set matches the row exactly**: `battery,cpu_power,gpu_power,ane_power,thermal`.
- **Result** (`rail-probe-results.json`, schema
  `joulewise.ed_qualification_keyboard_backlight_rail_probe.v1`):
  `aggregate_max_minus_off_consumed_rail_energy_delta_j` = `cpu_power: -5.704900831585405`,
  `gpu_power: 0.13299985399425585`, **`ane_power: 0.0`** (exactly zero across both ABBA pairs).
- **Recorded contamination** (`~/JouleWise-window-custody/ed-qual-20260817/rail-probe-load-note.txt`,
  verbatim): `concurrent_load=decisive_replay_unittest`;
  "power_state=operator_reported: charging during probe, reached full charge ~3/4 through the
  four-arm sequence"; "negative aggregate cpu delta (-5.7 J) attributed to concurrent-load drift +
  charge-state step, not backlight … boundary verdict (LED outside cpu+gpu+ane consumed rails)
  stands on code evidence independent of this probe";
  "recorded_by=lead (dictated from operator report … operator's own load-note paste superseded by
  this fuller record same evening)".
- **What the seat should weigh:** the probe *executed* as specified, and its documentation-grade
  status means the negative CPU differential does not damage any claim. But the differential is
  uninformative (wrong sign), the arms ran at ~13.7–14.0 W mean CPU under a concurrent unit test,
  and the load note is lead-authored after the operator's own note was overwritten. The row demands
  execution, not a usable number — the seat rules whether that is enough.

---

### ED-L3-4 — Channel-census currency on the arm build

**Row text (VERBATIM,** `sitting-packet-FINAL.md:186` **):**
> "ED-L3-4 (stable, largely co-closed by ED-L3-1): Channel-census currency on the arm build — one live capture parsed by the pinned parser with hw_model/kern_osversion recorded and matched against the runbook's Mac15,9 / macOS 25F84 bindings; REOPENS on any OS update before the window (the parser is pinned to the Slice-2H fixture format; a format/unit change fails closed on rails but silently on units only if Apple kept mW fields parseable — currency is an empirical row, not a test-provable one)."

**Charter classification as declared in the row:** `(stable, largely co-closed by ED-L3-1)`, with a
standing **REOPEN-on-OS-update** trigger.

**LOCATED CLOSURE EVIDENCE — EXECUTED LIVE, twice over, at both cadences; both bindings recorded.**

- **Ed's 2026-08-17 capture (1 Hz):**
  `~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/sampler-checklist-20260818T011840Z.plist`
  — first record carries `<key>hw_model</key><string>Mac15,9</string>` and
  `<key>kern_osversion</key><string>25F84</string>`, alongside `elapsed_ns 1011352000` and
  `timestamp 2026-08-18T01:18:48Z`. **Parsed by the pinned parser** — the checklist's inline Python
  ran `parse_powermetrics_records(capture.read_bytes())` and reported `records=5`, i.e. the
  Slice-2H-pinned parser accepted the live bytes with the three manifest rails present.
- **The lead's 2026-08-18 captures (100 ms, the production cadence — the stronger currency
  evidence):** all ten bundles under `~/JouleWise-window-custody/shakedown-20260818/` carry
  `hw_model = Mac15,9` / `kern_osversion = 25F84` in the raw plist **and**
  `"hardware_model": "Mac15,9"`, `"os_build": "25F84"`, `"sampling_interval_ms": 100` in
  `instrument_evidence.json`; each parsed to 1744–1749 complete records.
- **Match against the runbook bindings:** the row names "Mac15,9 / macOS 25F84"; both captures
  report exactly those values. The seat report's cadence-coherence chain (`L3-…-report.md:24`)
  binds the runbook's D-079 "100 ms cadence" to Mac15,9/macOS 25F84.
- **Not recorded as closing this row anywhere.** `ED-L3-4` appears nowhere outside the 2026-08-15
  council packet; no run report, decision entry, or receipt claims it.
- **The REOPEN trigger is live and unverified today.** Nothing in the tree or custody re-checks the
  build after 2026-08-18. The currency claim is 1–2 days old as of 2026-08-19 and reopens silently
  on any macOS update between now and the window. See probe §5.6.

---

## 4. CANDIDATE DISPOSITIONS FOR THE SEAT TO ADJUDICATE

**Candidate dispositions are assembled, not adjudicated; the seat rules.**

| Item | Severity | Candidate disposition | What is attached / what remains |
|---|---|---|---|
| F1 no measured-run post-teardown census | should_fix | **STILL-OPEN — NO REPAIR FOUND** | `_stop_process` byte-unchanged at `powermetrics.py:1664-1671`; zero `census/pgrep/orphan` in the adapter; WO-L3-1 has no queue/kernel row anywhere; WO-SAMPLER-SUPERVISOR still "Not on any critical path". **Aggravated:** the 2026-08-18 live runs also failed to durably record their post-teardown censuses (§3 ED-L3-2). |
| F2 ED-qual Step 2 points at an empty checklist home | should_fix | **STILL-OPEN — NO REPAIR FOUND** | `ed-qualification-session.md` zero commits since 2026-08-15; docstring still item-free. **Aggravated:** the batched Ed session went ahead and closed ED-L3-1 against the un-fixed checklist — the finding's own failure scenario. Partial mitigation: `ed-evening-checklist.md` (`aa90dc3`) gave the operator an ordered list, and the script self-stages `/tmp/ed-session`. |
| F3 checklist qualifies cadence at 1 Hz | should_fix | **STILL-OPEN (script), PARTIALLY OVERTAKEN BY NEW LIVE EVIDENCE** | WO-L3-3 not done — `sampler-checklist.sh` still `-i 1000 -n 5`. But 10 live 100 ms captures now exist (2026-08-18, lead-run) and show **realized ≈113 ms at configured 100 ms (~13 % long)** vs ~1.2 % at 1 Hz. The seat must decide whether that discharges the row's cadence-currency intent or **substantiates a new concern** about rollover-gate timing, drain budgets, and sample-count planning. |
| F4 related-work SoC boundary residual | nit | **STILL-OPEN — NO REPAIR FOUND** | `docs/paper/related_work_draft.md` zero commits since 2026-08-15; line 19 verbatim unchanged. |
| F5 `samplers_available` echoes the request | nit | **STILL-OPEN — NO REPAIR FOUND** | `powermetrics.py:1183-1187` unchanged; no rename, no probe derivation. |
| **ED-L3-1** live sampler checklist | ED-QUALIFICATION (stable) | **ED-ROW — EXECUTED LIVE BY ED with a durable receipt, BUT the row's stated PRECONDITION is UNMET** | `…/ed-qual-20260817/ed-session-evidence/sampler-checklist-20260818T011840Z.{log,plist}`, 2026-08-18T01:18:48Z, live `sudo -n`, all six steps PASS. Remaining: the row says "Close only after WO-L3-2/WO-L3-3" — **neither is done**, so the qualification ran against the defective checklist. Evidence is uncommitted/out-of-repo. |
| **ED-L3-2** live SIGTERM relay | ED-QUALIFICATION (stable) | **ED-ROW — OPEN as an ED row; the PHYSICAL OBSERVATION EXISTS (agent-run, unlabelled, uncensused)** | Ten live relays through `sudo -n`, max 22.8 ms of a 10 s grace, 2026-08-18, `…/shakedown-20260818/`. But: not an Ed run, `ED-L3-2` named nowhere, **post-teardown orphan censuses were never written** (`fences/census-orphan-post.txt` absent), and the SIGKILL branch — the row's actual hazard — was never reached. |
| **ED-L3-3** JW-MET-3 rail probe | ED-QUALIFICATION (stable, doc-grade) | **ED-ROW — EXECUTED LIVE BY ED with durable receipts; conditions CONTAMINATED and recorded** | Four `sudo -n powermetrics` ABBA arms + results JSON + log, 2026-08-18T01:19Z; ANE delta exactly 0. Differential negative (−5.70 J) under `concurrent_load=decisive_replay_unittest` and a mid-sequence charge-to-full. Out-of-repo. |
| **ED-L3-4** channel-census currency | ED-QUALIFICATION (stable, REOPENS on OS update) | **ED-ROW — EXECUTED LIVE, evidence attached at BOTH cadences; never recorded as closing the row; reopen trigger live** | `hw_model=Mac15,9` / `kern_osversion=25F84` in Ed's 1 Hz plist (parsed, `records=5`) and in all ten 100 ms shakedown bundles (`sampling_interval_ms: 100`, 1744–1749 records). Remaining: nobody has asserted closure, and nothing re-checks the build before the window. |
| WO-L3-1 / WO-L3-2 / WO-L3-3 / WO-L3-4 | work orders | **NO-REPAIR-FOUND; not even registered** | Searched `TASK_QUEUE.md`, `RUN_STATE.md`, `docs/process/state_kernel.json`, tree-wide grep — `WO-L3-1..4` appear only in `triage.json` and the seat report. |
| WO-T0-PRODUCER | Phase-1 WO | **MERGED, out of this seat's finding set** | PR **#152** (`a61ac92`, ON main) at head `9e8936a`; follow-up `65cc0f3` (ON main). Enables the live sudo captures via the D-127 route; repairs none of F1–F5. |
| WO-CENSUS-SEMANTICS | Phase-1 WO | **STILL-OPEN, BLOCKED on ED-Q-L9-3** | Kernel row `state_kernel.json:3122-3168` (`"status": "blocked"`); queue row `A4`, `TASK_QUEUE.md:545`. Precondition capture exists but is uncommitted and lead-captured — see `rows/ROW-L9.md` §3. |
| WO-SAMPLER-SUPERVISOR | registered WO | **STILL-OPEN, unregistered in the kernel** | `TASK_QUEUE.md:293-316`; "Not on any critical path". Caps WO-L3-1 at detect-and-report. |
| WO-DETECT-PULSES-BUDGET | Phase-1 WO | **LANDED ON MAIN (`ceda7a6`), queue string says PARTIAL; READY** | Governed abort observed firing on live data (`driver-20260818T045235.log`, `detection_nonconvergent`, `cell_budget: 100000`). Queue/graph disagreement flagged. |
| **Capture-era v3 production flip** | **new since the sitting, IN THIS SEAT'S CORE MODULE** | **NEW, UNAUDITED BY ANY SEAT — for the seat to scope** | `b7e5730` (+ `4efea13`, `1ec5dc4`, `3038eeb`, `d279bd2`, `6f00d05`, `d8f1202`), **all branch-only**. Flipped all four live clock-evidence sites in `joulewise/adapters/powermetrics.py` from the v2 deriver to `resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)` and rewrote the `TIMESTAMP_DERIVATION` string p2-038.2→p2-038.3. Authority D-146. L3 audited the v2 path; **L3 is not on the council's Phase-3 focused-re-audit list** (`council-verdict.md:102-104` names L1/L5/L7 minimum). |
| D-149 no-hands automation | new since the sitting | **NEW, UNAUDITED — for the seat to scope** | `0e96dbb`, `79a4cd0`, `b92b43d`, all **branch-only**. Deletes `"Ed remains the physical launch authority"` from the three window-task kernel fences while `window_runbook.md` still asserts it. Moots no L3 row; keeps backlight/new-sudo with Ed; removes the human observer the F1 orphan scenario implicitly relies on; its C1 depends on ED-L3-1..4 closure. |

---

## 5. WHAT A SKEPTICAL SEAT SHOULD PROBE

Each probe names its falsifier.

1. **(a) Staged-vs-live, ED-L3-1 — was this really a live operator run?**
   `cat ~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/sampler-checklist-20260818T011840Z.log`
   and confirm it contains `PASS: sudo -n authorization is available.` and the
   `Press Return to start the supervised five-sample check:` prompt (a `--dry-run` invocation
   prints `DRY-RUN: production supervisor import and live capture skipped.` instead —
   `sampler-checklist.sh:91-92`). Then `plutil -p …011840Z.plist | head` for real per-record data.
   **Falsifier of "live":** any `DRY-RUN` string, or a plist with fewer than 5 records.
   **Falsifier of "closed":** the row's text — WO-L3-2 and WO-L3-3 are demonstrably not done, so
   the row's own precondition bars closure regardless of how good the run was.

2. **(a) Staged-vs-live, ED-L3-2 — did anything actually SIGTERM a live sudo powermetrics?**
   Check the two candidate paths separately. ED-QUAL: `grep -n '\-n 5' scripts/ed_session/sampler-checklist.sh`
   → `-n 5` means self-exit, so `_terminate_powermetrics` early-returns on `poll() is not None` and
   **no signal is sent**. Shakedown: `grep -n 'SAMPLING_INTERVAL_MS' -A6 scripts/validate_powermetrics_fiducial.py`
   around `:1765-1777` → no `-n <count>` ⇒ the sampler must be signalled.
   **Falsifier of the assembled reading:** a `-n <count>` in the live fiducial command, or a
   teardown_s ≥ 10 s in any bundle (which would prove the SIGKILL branch, not the clean relay).

3. **(a) The missing orphan census after those SIGTERMs — the sharpest probe on this row.**
   `ls /Users/edr/JouleWise-window-custody/shakedown-20260818/fences/` and look for
   `census-orphan-post.txt` / `census-monitor-post.txt` (the driver writes them at
   `docs/process_traces/2026-08-18-shakedown-first-light/05-driver-as-run.sh:70-71`). They are
   **absent**. Then `grep -l powermetrics_post_teardown_census <each bundle>/events.jsonl` —
   **no hits** (the diagnostic emits only on findings). So the ten teardowns have **no recorded
   proof that no orphan survived**; `trace-notes.md:339` ("Machine clean … no orphans") is
   narrative. **Falsifier:** either fence file existing, or a census event in any `events.jsonl`.

4. **(a) Staged-vs-live, ED-L3-3.**
   `grep -c "sudo -n /usr/bin/powermetrics" ~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/rail-probe-20260818T011943Z/rail-probe.log`
   (expect 4) and confirm four distinct plists of ~1.59 MB with 30 records each.
   **Falsifier:** byte-identical arms, or fewer than four commands. Then the substantive question:
   does a documentation-grade row close on a differential with the **wrong sign** (−5.70 J for a
   load that can only add power), measured under a concurrent unit test and a charge-to-full step?

5. **(b) Is the live census/cadence observation still SINGLE-SOURCE?** Disposition 5's single-source
   label is L9's, but the same question binds L3: the only 100 ms realized-cadence observation is
   the lead's own 2026-08-18 shakedown, and the only 1 Hz observation is Ed's own 2026-08-17 run.
   Both are same-machine, same-organisation, no independent lens.
   **Falsifier of "still single-source":** an independent re-capture, or a committed artifact CI can
   re-derive. Neither exists — searched `~/JouleWise-window-custody/` (22 dirs) and the repo tree.

6. **(c) Does the channel/parser census match the CURRENT OS build, not the audited one?**
   At the machine: `sw_vers -buildVersion; sysctl -n hw.model`, then one short live capture and
   `parse_powermetrics_records` over it.
   **Falsifier of ED-L3-4's currency:** any build other than **25F84**, or a hardware model other
   than **Mac15,9** — the row REOPENS by its own terms on any OS update before the window, and the
   attached evidence is from 2026-08-17/18. Also probe the row's stated silent-failure mode: a unit
   change that keeps mW fields parseable would pass the parser and change every number; nothing
   in the attached evidence rules that out.

7. **(c) The 113 ms question — new, and no seat has ruled on it.**
   Recompute from primary bytes: for each shakedown bundle, count records and read the second
   record's `elapsed_ns`. Ten bundles give 112.09–114.20 ms at a configured 100 ms.
   Then ask what depends on ~100 ms: the D-078 rollover gate, the drain budgets
   (`_wait_for_native_rollover` / drain deadline logic in `joulewise/adapters/powermetrics.py`),
   and window sample-count planning.
   **Falsifier of "this is fine":** any budget or planning constant derived from 100 ms with less
   than 13 % headroom. **Falsifier of "this is new":** a prior record showing realized 100 ms
   cadence was already characterised — the assembler found none (`grep` over run reports, traces,
   and `docs/contracts/` for realized-cadence characterisation returned nothing).

8. **(d) D-149 automation — unattended failure modes no seat has audited.**
   Run `git show 0e96dbb -- docs/process/state_kernel.json` and see the fence replacement deleting
   `"Ed remains the physical launch authority"` on all three window tasks. Then read
   `docs/decision_log.md:172` (C1–C5), `docs/process/d149-go-receipt-template.md` (`79a4cd0`), and
   the run card `b92b43d`. Ask:
   (i) with no operator present, what detects the F1 mid-window root orphan — given that the
   measured-run path has **no census** and the shakedown's own post-teardown censuses were never
   written (§3, ED-L3-2 probe 3)? (ii) does the automation retry an arm or a member after a sampler
   failure, and could a retry spawn a second sampler while the first is stranded? D-078 no-retry
   says it must not ("a refused capture ends that lane with diagnosis, never re-arm-and-hope") —
   is that mechanically enforced or documentary? (iii) does it re-assert `prewindow_check.sh`,
   whose agent census L9-F3 proves lies? (iv) "evaluated mechanically at T-0" vs
   `d149-go-receipt-template.md:63-66` ("until then the issuer fills the receipt by running the
   runbook commands and attaching outputs") and the brand-new `## WO-D149-GO-EVALUATOR` block at
   `TASK_QUEUE.md:373` — **the evaluator does not exist**. (v) E-4 expects an interactive sudo
   password prompt (`window_runbook.md:896`) and D-149 keeps "new sudo" as Ed's — how does a
   no-hands T-0 obtain privilege?
   **Falsifier:** an automation-side sampler census or supervisor. **Aggravators:** all three D-149
   artifacts are **branch-only**, absent from `origin/main` and from every seat's evidence universe;
   the kernel and `docs/phase_2/window_runbook.md` now contradict each other on who launches; and
   `WINDOW_STATUS.md` was never reconciled (no `D-149` string; still dated 2026-08-17).

9. **Coverage self-nomination (the council's standing caution,** `council-verdict.md:18-22`**).**
   L3's 25/29 was self-enumerated; four items were explicitly not examined
   (`mock_telemetry.py`, the crash-matrix module, rail-probe line audit, deep reducer internals).
   Probe: independently re-enumerate the capture/telemetry universe before accepting 25/29.
   **Falsifier:** an independent enumeration reproducing 29 items exactly.

10. **Charter-amendment applicability.** Opus S12 (`council-verdict.md:54-57`): a READY-CANDIDATE
    sitting binds charter:77-78 — "only T0 rows may remain open." All four L3 rows are `(stable)`,
    none is T0. Probe: on that text, can this sitting grade READY while ED-L3-1's stated
    precondition is unmet and ED-L3-2 has no labelled closure? **Falsifier:** a ruling that live
    artifacts close the rows regardless of the "Close only after WO-L3-2/WO-L3-3" clause.

11. **Where the evidence lives.** Every ED-row artifact for this seat is under
    `/Users/edr/JouleWise-window-custody/`, **uncommitted and unhashed by any manifest**. Probe:
    `git -C <repo> log --all --oneline -- '*sampler-checklist*' '*rail-probe*'` → nothing but the
    scripts themselves. **Falsifier:** any committed receipt or digest binding these artifacts.
    Consequence if not cured: a future re-audit cannot re-derive this seat's closure from the repo.

12. **(new) The capture-era v3 flip — re-audit trigger for THIS seat.**
    `git show b7e5730 -- joulewise/adapters/powermetrics.py` and confirm the four
    `resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)` sites and the
    `TIMESTAMP_DERIVATION` p2-038.2→p2-038.3 rewrite. Then ask: this seat's positive probes —
    the ten-attempt parser falsification matrix, the phantom-channel exclusion proof, the cadence
    coherence chain — were all executed against the **v2** capture path at `8937dec`. Do they
    still hold at v3? **Falsifier of "unchanged":** any of `parse_powermetrics_records`,
    the rail set, or the integration boundary differing at HEAD. **Falsifier of "this is covered":**
    `council-verdict.md:102-104` names L1/L5/L7 as the Phase-3 focused re-audit minimum — L3 is
    absent, yet L3's core module changed. Also check whether the ten 100 ms shakedown captures
    (§2.3) were produced by the pre-flip or post-flip code: they ran from the clone at
    `~/JouleWise-window-custody/shakedown-20260818/clone/`, not from HEAD.

---

## 6. OPEN ITEMS FROM THIS ROW

- **F1 (should_fix) — no repair, and not even queued.** `joulewise/adapters/powermetrics.py:1664-1671`
  is byte-unchanged; the adapter contains no census of any kind; `WO-L3-1` exists only in the
  council packet. Searched `TASK_QUEUE.md`, `RUN_STATE.md`, `docs/process/state_kernel.json`, and
  tree-wide for `WO-L3-1`.
- **WO-SAMPLER-SUPERVISOR remains unimplemented and unregistered in the kernel** —
  `TASK_QUEUE.md:293-316`, "Not on any critical path" — so detect-and-report is the architectural
  ceiling for any F1 remedy, on a path that today has no detection at all.
- **F2 (should_fix) — no repair, and the failure scenario ACTUALLY OCCURRED.**
  `docs/phase_2/ed-qualification-session.md` has zero commits since 2026-08-15, the sampler-module
  docstring still carries no checklist items, and the batched Ed session nonetheless ran and closed
  the sampler row on 2026-08-17.
- **F3 (should_fix) — WO-L3-3 not done**, and the live 100 ms data that now exists shows
  **realized ≈113 ms at configured 100 ms (~13 % long)** across all ten 2026-08-18 bundles. No
  seat, ruling, or document has assessed what a 13 % cadence overshoot does to the rollover gate,
  the drain budgets, or window sample-count planning. **This is a NEW open item, not a repair.**
- **F4 and F5 nits — no repair.** `docs/paper/related_work_draft.md:19` and
  `joulewise/adapters/powermetrics.py:1183-1187` are verbatim unchanged.
- **ED-L3-1 was closed against the very checklist the row forbids closing against.** The row says
  "Close only after WO-L3-2/WO-L3-3"; neither is done. The seat must decide whether a good live run
  against a defective checklist closes a gating row.
- **ED-L3-2 has NO LABELLED CLOSURE.** The string `ED-L3-2` appears nowhere outside the 2026-08-15
  council packet; the ten live SIGTERM relays that would satisfy it were an **agent-run** by-product
  of the shakedown, on the fiducial path, and **their post-teardown orphan censuses were never
  durably recorded** — `~/JouleWise-window-custody/shakedown-20260818/fences/` has no
  `census-orphan-post.txt` and no `census-monitor-post.txt`, and no
  `powermetrics_post_teardown_census` event exists in any live `events.jsonl`. The SIGKILL branch —
  the row's actual hazard — has still only ever been observed in an **unprivileged simulation**
  (falsifier F-B).
- **ED-L3-3's differential is uninformative and was taken on a contaminated machine** — a
  concurrent decisive-replay unit test plus a mid-sequence charge-to-full, both recorded in
  `rail-probe-load-note.txt`, which is itself lead-dictated after the operator's own note was
  overwritten.
- **ED-L3-4 has never been asserted closed anywhere**, and its REOPEN-on-OS-update trigger is live
  and unchecked since 2026-08-18. The row's silent-failure mode (a unit change that keeps mW fields
  parseable) is not excluded by any attached evidence.
- **ALL ED-row closure evidence for this seat is OUT-OF-REPO and UNCOMMITTED**
  (`/Users/edr/JouleWise-window-custody/ed-qual-20260817/` and `.../shakedown-20260818/`), bound to
  no manifest and hashed by nothing. A future re-audit cannot re-derive this seat's closure from the
  repository.
- **`WO-L3-1..4` were never registered as work items anywhere outside the council packet** — unlike
  the L9 work orders, which at least reached the kernel as WO-CENSUS-SEMANTICS. Nothing in the
  queue would ever surface them for selection.
- **THE PRODUCTION CAPTURE PATH IN THIS SEAT'S CORE MODULE WAS FLIPPED AFTER THE AUDIT AND NO SEAT
  HAS RE-AUDITED IT.** `b7e5730` (branch-only, D-146 authority) replaced all four live
  clock-evidence sites in `joulewise/adapters/powermetrics.py` with
  `resolve_clock_evidence_deriver(ACTIVE_CAPTURE_ANCHOR_METHOD)` and rewrote the per-bundle
  `TIMESTAMP_DERIVATION` string from p2-038.2 to p2-038.3, with six follow-on fix commits
  (`1ec5dc4`, `3038eeb`, `d279bd2`, `6f00d05`, `d8f1202`, plus estimator `4efea13`). **L3 is not on
  the council's Phase-3 focused-re-audit list** (`council-verdict.md:102-104`: "L1, L5, L7
  minimum"). This seat's parser-falsification and cadence-coherence probes were all executed
  against the v2 path.
- **D-149's no-hands window automation is unaudited by any seat and is branch-only**
  (`0e96dbb`, `79a4cd0`, `b92b43d`, none on `origin/main`). It removes the human presence that the
  F1 orphan scenario tacitly relies on, on a path that has no software census; it **deletes the
  kernel clause "Ed remains the physical launch authority"** while `window_runbook.md` still
  asserts it; its "evaluated mechanically at T-0" evaluator **does not exist**
  (`d149-go-receipt-template.md:63-66`; `## WO-D149-GO-EVALUATOR` registered at
  `TASK_QUEUE.md:373` during this assembly); and its C1 ("ED-QUALIFICATION rows closed") makes the
  auto-GO depend on this sitting's verdict on ED-L3-1..4.
- **The branch HEAD moved twice during this assembly** (`4597ad4` → `b92b43d` → `7305e0d`).
  No L3 code surface changed across the drift, but `TASK_QUEUE.md` line numbers shifted +7 and a
  new queue block appeared. A packet assembled against a moving tree is itself a finding.
- **The queue's WO-DETECT-PULSES-BUDGET status string (`PARTIAL; READY`) disagrees with the commit
  graph** (`ceda7a6` is on `origin/main` and its governed abort was observed firing live). Not L3's
  finding, but it is a fact about the evidence base this seat is being asked to trust.
