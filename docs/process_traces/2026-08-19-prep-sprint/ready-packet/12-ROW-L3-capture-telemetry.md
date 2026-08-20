# ROW L3-CAPTURE-TELEMETRY-xhigh — capture + telemetry (GATING)

Original verdict: **NOT-READY (0 blockers / 3 should-fix / 2 nits / coverage 25/29)**
Falsifiers 3 · unexecuted obligations 7 · ED-QUALIFICATION rows 4.
(sitting-packet-FINAL.md §2 line 28; seat report §8 "Component verdict: **NOT-READY**".)

Seat report sha256-16 `2ee51138ea4dcf7f` — **VERIFIED** by `shasum -a 256` against
sitting-packet-FINAL.md:13. Baseline: manifest head `ac3fe1d`, worktree `8937dec`; the seat
verified the runbook sha against the manifest by direct shasum.

**No L3 finding was contested by any refuter.** The nine C-028 refuter runs covered clusters A
(arm/freeze expiry), B (T-0 producer gap), DG (kernel/ceremony), ECF (consumption/margin/census)
and the L2 falsely-clean attack; none took an L3 lens. So every L3 finding stands exactly as the
seat wrote it, unverified by a second lens in either direction.

**Structural fact the seat must weigh first: none of WO-L3-1..4 was ever registered anywhere
outside the council trace.** `grep -rn "WO-L3-1\|WO-L3-2\|WO-L3-3\|WO-L3-4"` over the whole repo
returns hits only in `docs/process_traces/2026-08-15-readiness-council/triage.json:283-286` and
the L3 seat report. They appear in **no** TASK_QUEUE row (generated or hand-authored), **no**
`docs/process/state_kernel.json` task, and **no** Completed-queue entry. council-verdict.md's
Phase-1 program (lines 80-87) names WO-KERNEL-RECONCILE, WO-T0-PRODUCER, WO-LAUNCH-BINDING,
WO-CONSUMPTION-EDGE, WO-MARGIN-RECORDER-AUTHZ, WO-CENSUS-SEMANTICS, WO-DETECT-PULSES-BUDGET,
WO-L2-REAUDIT and "should-fix batch incl. sweep verify-and-fix items … and L11's three paper
corrections" — **the L3 work orders are not enumerated in it**. They fell out of the program at
verdict-recording time.

Corroborating negative: `joulewise/adapters/powermetrics.py` was last touched on
`origin/main` by `fdb311f` (**2026-07-22**), three weeks before the council; the two branch-only
commits that do touch it (`4efea13`, `b7e5730`, clock-anchor v3 / D-146) add **no** census, no
`pgrep`, and no `samplers_available` change (`git diff origin/main HEAD -- joulewise/adapters/powermetrics.py
joulewise/controller.py | grep -i census` → empty). `docs/phase_2/ed-qualification-session.md`
has exactly one commit in its life (`95362e2`, pre-council).

---

## L3-1 — Measured-run (adapter/controller) path has no post-teardown sampler census

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [should_fix] [L3] Measured-run (adapter/controller) path has no post-teardown sampler census; kill-escalation orphan samples invisibly through the rest of a window

Seat-report §6 finding 1, full text:

> 1. **[should-fix] No post-teardown sampler census on the measured-run path** — powermetrics.py:1655-1663 vs validate_powermetrics_fiducial.py:562-578. Scenario: sampler hangs >10 s at member k's stop during the funded window; SIGKILL strands a root orphan (executed F-B); it samples through members k+1..N and their idle baselines; the only censuses are the fiducial script's (not this path) and the T0 arm probe (arm-time only) — contaminated bundles do **not** fail closed against consumption. Work order WO-L3-1.

Supporting executed falsifier, seat-report §4 F-B (VERBATIM):

> **F-B — supervision orphan (demonstrated).** `scratchpad/probe_orphan_falsifier.py` replicates the `sudo -n` signal topology without privileges: relay parent forwards SIGTERM (as sudo does), sampler child ignores it (stands in for a hung root powermetrics). Running the adapter's verbatim `_stop_process` (powermetrics.py:1655): 10 s grace expires → SIGKILL to relay (rc −9, not forwardable) → **sampler grandchild survives reparented to PID 1**. Orphan verified alive, then killed and verified dead. Live-sudo reality is strictly worse (root-owned orphan the user cannot kill). This confirms the WO-SAMPLER-SUPERVISOR class is reachable on the **adapter/controller measured-run path**, which — unlike the fiducial script — has **no census at all** (finding 1).

The council's remedy text, `triage.json:283` (VERBATIM):

> "WO-L3-1: Add the detect-and-report post-teardown sampler census to the measured-run stop path (adapter stop_sampling_with_evidence/_take_measured_capture or controller finalization), mirroring scripts/validate_powermetrics_fiducial.py's _report_powermetrics_census, and record findings into bundle metadata so a mid-window orphan is at least detectable at reduce time. Keep detect-and-report-only semantics pending WO-SAMPLER-SUPERVISOR."

Citation: sitting-packet-FINAL.md §4 line 140; seat report
`docs/process_traces/2026-08-15-readiness-council/seat-reports/L3-CAPTURE-TELEMETRY-xhigh-report.md:42`
(+ F-B at :31); refuter verdict — **none; no refuter took an L3 lens**.
Post-verdict adjudication: none.

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND.** Verified at the current head:

- `grep -c "census" joulewise/adapters/powermetrics.py joulewise/controller.py` → **0 and 0**. The
  measured-run path still has no census of any kind.
- The census function the remedy says to mirror exists only on the fiducial path:
  `scripts/validate_powermetrics_fiducial.py:926` `def _report_powermetrics_census(...)`, called at
  `:985`.
- The escalation the falsifier exercised is byte-unchanged:
  `joulewise/adapters/powermetrics.py:1664` `def _stop_process(...)` → `terminate()` →
  `communicate(timeout=10.0)` → `TimeoutExpired` → `kill()`. (Line moved 1655→1664; the code did
  not change.)
- No WO-L3-1 row exists in TASK_QUEUE or the kernel (see the row header).
- **WHERE it lives: nowhere.** No commit, no branch, no queue row.

**Adjacent, non-substituting evidence:** `WO-SAMPLER-SUPERVISOR` — the *stronger* fix this
detect-and-report census was explicitly scoped as an interim to — is **still open** and registered
only as hand-authored prose at `TASK_QUEUE.md:293-316`, **outside** the generated region and
**absent** from `docs/process/state_kernel.json` (`grep SAMPLER-SUPERVISOR docs/process/state_kernel.json`
→ no match). Its own text confirms the interim state (VERBATIM):

> Until landed, the production script's census is detect-and-report only
> and full ownership is documented UNSUPPORTED. Not on any critical path.

Note the phrase "the **production script's** census" — i.e. the fiducial script's. The adapter
path L3 found has neither the supervisor nor a census. Its ADMISSION GATE ("lead-owed, live Mac":
real powermetrics must run with process creation denied) has no closure record; the section
records two already-failed formulations (group-kill r0, identity preamble r1).

Live evidence bearing on the orphan class, from the 2026-08-17 Ed session
(`docs/run_reports/2026-08-18-t10-session.md:104`): "Sampler lifecycle (ED-QUAL step 2) | PASS —
cadence mean **1.0128 s**, zero orphans". That is the **fiducial/checklist** path on the healthy
5-sample happy path at 1 Hz — it does not exercise a hung sampler, and it is not the adapter path.

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND.** The seat is adjudicating a should-fix backed by an executed falsifier
(orphan reproduced, reparented to PID 1) whose remedy the council itself specified in one
sentence, which was never registered as work, never implemented, and whose stronger successor
(WO-SAMPLER-SUPERVISOR) is also open and invisible to the kernel — on the path that runs every
funded-window member.

### (d) Skeptical probes

1. `grep -rn "census" joulewise/adapters/powermetrics.py joulewise/controller.py` — verify the zero
   for yourself, then ask what artifact would record a mid-window orphan if one occurred.
2. Re-run the seat's F-B falsifier shape against `_stop_process` at the current head
   (`powermetrics.py:1664`). Does the grandchild still survive SIGKILL-to-relay?
3. Ask where a contaminated bundle would be caught downstream. The seat says the reducer sums only
   manifest rails (D-018) — so an orphan sampler's contamination arrives as *elevated real power in
   the same rails*, not as an extra channel. Is there any consumer that fails closed on it?
4. `grep -rn "WO-SAMPLER-SUPERVISOR" docs/process/state_kernel.json` → empty. Ask whether a work
   order outside the declared sole work-selection authority can gate anything.
5. The supervisor's ADMISSION GATE is lead-owed on a live Mac and has failed twice. Ask whether the
   council is prepared to accept detect-and-report-only permanently — and if so, whether the
   *adapter* path getting a census becomes mandatory rather than interim.

---

## L3-2 — ED-qualification Step 2 points at a checklist home that does not contain the checklist

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [should_fix] [L3] ED-qualification Step 2 points at a checklist home that does not contain the checklist

Seat-report §6 finding 2, full text:

> 2. **[should-fix] ED-qualification Step 2 points at an empty checklist home** — ed-qualification-session.md:18-19 says the items “live in the sampler module docstring”; the docstring (validate_powermetrics_fiducial.py:1-27) carries only the UNSUPPORTED-scope prose (round-2 rewrite dropped round-1's docstring checklist); the real items live in `scripts/ed_session/sampler-checklist.sh`, and no staging step to the referenced `/tmp/ed-session/` exists. Scenario: the single batched Ed session closes ED rows against an unenumerated checklist — the tired-operator hazard on exactly the closure council READY requires. WO-L3-2.

Council remedy text, `triage.json:284` (VERBATIM):

> "WO-L3-2: Fix docs/phase_2/ed-qualification-session.md Step 2 to name scripts/ed_session/sampler-checklist.sh as the checklist home (and either add the /tmp/ed-session staging step to the loop's prep or reference the repo path directly); align the module docstring pointer or restore an item list there."

Citation: sitting-packet-FINAL.md §4 line 141; seat report :43; refuter verdict — none.
Post-verdict adjudication: none. **Named as a hard precondition** for closing ED-L3-1 —
sitting-packet §5 line 183: "Close only after WO-L3-2/WO-L3-3 fix the checklist's documented home
and add the 100 ms leg."

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND — and the row it gates was closed anyway.**

- `docs/phase_2/ed-qualification-session.md:17-24` at the current head is unchanged (VERBATIM):

  > ## Step 2 — production sampler live checklist (~5 min)
  > The #127 production sampler's reliance checklist (its items live in the
  > sampler module docstring; the capture-lens audit enumerates them as rows):
  > run the commands the loop has staged in
  > `/tmp/ed-session/sampler-checklist.sh` when pinged …

  Still "live in the sampler module docstring"; still the staged `/tmp/ed-session/` path; still no
  reference to `scripts/ed_session/sampler-checklist.sh`.
- `git log --oneline origin/main -- docs/phase_2/ed-qualification-session.md` → **one commit ever**:
  `95362e2` "ED-QUALIFICATION session script: one ~20-min visit closes all stable hardware/sudo
  rows…" (pre-council). Nothing since.
- The docstring is still the UNSUPPORTED-scope prose:
  `scripts/validate_powermetrics_fiducial.py:1-27` opens "Lead-owned [QUIET-MAC] pulse-fiducial
  calibration run (D-078)" and lists protocol facts — no checklist items.
- **WHERE it lives: nowhere.**

**But the gated ED row was executed regardless, on 2026-08-17.** `docs/run_reports/2026-08-18-t10-session.md:104`:

> | **Sampler lifecycle (ED-QUAL step 2)** | PASS — cadence mean **1.0128 s**, zero orphans | `ed-session-evidence/sampler-checklist-*.log` (3 runs + plist) |

and `docs/process/ed-morning-packet-2026-08-18.md:114` "Sampler lifecycle (cadence 1.0128 s, zero
orphans)", under "## 5. Qualification ledger … **CLOSED** with custody evidence in
`~/JouleWise-window-custody/ed-qual-20260817/`". Custody is **off-repo, Ed-held** — not verifiable
from this worktree.

The instructing document for that evening was `docs/process/ed-evening-checklist.md:21-24`
(VERBATIM): "4. **Sampler checklist + rail probe + keyboard-backlight rows** — per the
qualification script items (backlight: level zero, auto-adjust false, inactivity never; record
`verification=operator_visual`)." — i.e. it routed the operator back to the same
"qualification script items" whose home L3 found empty. Neither WO-L3-2 nor WO-L3-3 had landed.

Two `ed_session` script fixes *were* made that evening, both live-found defects, both unrelated to
this finding — and both **merged to main**:
- `d873f77` (2026-08-17 18:06) "ed_session: guard empty-args re-exec against macOS bash 3.2 set -u
  (unbound ORIGINAL_ARGS[@])".
- `e5dc38a` (2026-08-17 18:18) "ed_session: probe command-scoped sudo authorization, not blanket
  `sudo -n true`" — 2 files, 3 insertions/3 deletions (`rail-probe.sh` 1 line, `sampler-checklist.sh`
  2 lines). Verified `git merge-base --is-ancestor e5dc38a origin/main` → true.
  `git show --stat e5dc38a` confirms it touches only the sudo probe; it does not touch the
  checklist home, the cadence, or the docstring pointer.

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND, and the precondition was overridden in practice.** The seat is adjudicating
whether ED-L3-1 can count as closed when the council's own closure condition ("close only after
WO-L3-2/WO-L3-3") was unmet at execution time, the checklist home the operator was pointed at is
still empty, and the resulting evidence lives off-repo where no seat can inspect it.

### (d) Skeptical probes

1. Open `docs/phase_2/ed-qualification-session.md:18` and `scripts/validate_powermetrics_fiducial.py:1-27`
   side by side. Are the checklist items anywhere in the docstring?
2. `git log --oneline origin/main -- docs/phase_2/ed-qualification-session.md` — one commit,
   pre-council. Confirm nothing was fixed.
3. Ask for the three `sampler-checklist-*.log` files from `~/JouleWise-window-custody/ed-qual-20260817/`.
   Do they enumerate the checklist rows the seat said were unenumerated — pre-census, supervised
   capture, **post-teardown census**, cadence record, pinned-parser parse — or only the script's
   own output?
4. `/tmp/ed-session/` is a staged path with no producer step. Ask which file the operator actually
   executed on 2026-08-17: the repo script or a staged copy, and whether the two were byte-identical.
5. Ask whether closing an ED row against an unmet, council-stated precondition sets a precedent for
   the other ED rows in this packet.

---

## L3-3 — ED sampler checklist qualifies cadence at 1 Hz while every production surface runs 100 ms

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [should_fix] [L3] ED sampler checklist qualifies cadence at 1 Hz while every production surface runs 100 ms

Seat-report §6 finding 3, full text:

> 3. **[should-fix] ED checklist qualifies cadence at 1 Hz, production is 100 ms** — sampler-checklist.sh runs `-i 1000 -n 5` while packs/fiducial/runbook all bind 100 ms. Scenario: the cadence row closes on 1 Hz evidence; a post-OS-update realized-interval anomaly at 100 ms surfaces only inside the funded window. WO-L3-3.

Council remedy text, `triage.json:285` (VERBATIM):

> "WO-L3-3: Add a second short capture at -i 100 (production cadence) to scripts/ed_session/sampler-checklist.sh's cadence-record step, or explicitly annotate the row as supervision-only and move cadence currency to the T0 probes."

Citation: sitting-packet-FINAL.md §4 line 142; seat report :44; refuter verdict — none.
Post-verdict adjudication: none. Also a stated precondition for ED-L3-1 (sitting-packet §5 line 183).

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND — and the row closed on exactly the 1 Hz evidence the seat predicted.**

- `scripts/ed_session/sampler-checklist.sh` at the current head still runs 1 Hz:
  - `:59` echoes `/usr/bin/sudo -n /usr/bin/powermetrics -b 0 **-i 1000** -n 5 --samplers battery,cpu_power,gpu_power,ane_power,thermal --format plist -o $CAPTURE`
  - `:108` the executed argv: `"-b", "0", **"-i", "1000"**, "-n", "5",`
  - No 100 ms leg anywhere in the file; no supervision-only annotation.
- `git log --oneline origin/main -- scripts/ed_session/sampler-checklist.sh` → three commits total:
  `ac3fe1d` (the baseline itself), `d873f77` (bash 3.2 guard), `e5dc38a` (sudo probe). **Neither
  post-council commit touches the interval.**
- **WHERE it lives: nowhere.**

**The predicted outcome occurred.** The 2026-08-17 closure recorded **cadence mean 1.0128 s**
(`docs/run_reports/2026-08-18-t10-session.md:104`) — a 1 Hz measurement standing in for a 100 ms
production cadence. The seat's scenario ("the cadence row closes on 1 Hz evidence") is now the
record.

**Partial, incidental 100 ms evidence exists from a different route — the shakedown, not the
checklist:**
- `docs/process_traces/2026-08-18-shakedown-first-light/02-root-cause-diagnosis.md:109-110`:
  "No interval gaps over 1 ms. / Shakedown cadence was **113.3 ms median**, within the same general
  range as corpus members at about **120.2 ms**."
- `docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md:58`: "All
  evidence declares the same **100 ms configured sampling interval**".
- **WHERE it lives: merged to main** — the shakedown custody dir is present at `origin/main`; the
  D-143 ruling it grounds is at `docs/decision_log.md:166` / `:8821`.

Read carefully, that is a *realized-interval* observation at production cadence on the current OS
build (113.3 ms median vs 100 ms nominal, a ~13% overshoot) obtained as a by-product of a detector
diagnostic — not a supervised checklist run, not a teardown-census run, and not recorded against
ED-L3-1 or ED-L3-4. It is also evidence that the realized interval is **not** 100 ms, which is
precisely the class of anomaly the seat wanted qualified before the window rather than inside it.

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND (with partial off-row evidence).** The seat is adjudicating whether the cadence
row is qualified when the checklist still measures 1 Hz, the closure record shows 1.0128 s, and the
only production-cadence observation (113.3 ms median against a 100 ms nominal) came from an
unrelated diagnostic that was never attributed to this row.

### (d) Skeptical probes

1. `grep -n "\-i" scripts/ed_session/sampler-checklist.sh` — the interval is still 1000.
2. Ask what 113.3 ms median means for the instrument: is the reducer's per-record `elapsed_ns`
   integration immune to a 13% overshoot (the seat says "integration uses per-record `elapsed_ns`,
   not the nominal interval" — verify at `reduce.py`), and does any pack/protocol field assert 100 ms
   in a way that a 113 ms realized cadence would falsify?
3. Was the 113.3 ms capture taken under the production supervisor (`_sampler_lifetime`) or as a raw
   `powermetrics` invocation? Only the former exercises what ED-L3-1 covers.
4. Ask whether `-i 1000` in the checklist was a deliberate cost choice; if so, the alternative
   remedy the council offered ("explicitly annotate the row as supervision-only and move cadence
   currency to the T0 probes") is a one-line doc edit that also has not happened.
5. ED-L3-4 requires `hw_model`/`kern_osversion` recorded and matched to the runbook's Mac15,9 /
   macOS 25F84 bindings. `grep -rln "kern_osversion" docs/run_reports docs/process docs/process_traces`
   returns nothing outside the council trace — ask where that match is recorded.

---

## L3-N1 (nit) — Post-JW-MET-1 residual: retained related-work draft still describes JouleWise with system-on-chip boundary language

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [nit] [L3] Post-JW-MET-1 residual: retained related-work draft still describes JouleWise with system-on-chip boundary language

Seat-report §6 finding 4:

> 4. **[nit] JW-MET-1 residual** — related_work_draft.md:19 still says JouleWise “integrates named system-on-chip power channels”; the five draft-v1 sites are fixed, the retained draft was not swept. Scenario: a later paper train copies the stale sentence back.

Council remedy text, `triage.json:286` (VERBATIM):

> "WO-L3-4 (nit-grade): sweep docs/paper/related_work_draft.md:19 boundary wording; rename or probe-derive samplers_available metadata."

Citation: sitting-packet-FINAL.md §4 line 143; seat report :45; refuter verdict — none.

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND. The sentence is byte-identical to the baseline.**

- Current `docs/paper/related_work_draft.md:19`: "JouleWise applies this lineage to `powermetrics`
  on Apple silicon. It integrates named **system-on-chip** power channels only inside
  runtime-emitted phase boundaries, …"
- `git show ac3fe1d:docs/paper/related_work_draft.md | sed -n '19p'` — **identical**.
- `git log --oneline origin/main -- docs/paper/related_work_draft.md` → newest commit `ff5fa76`
  (**2026-08-10**), i.e. five days *before* the council. The file has not been touched since.
- The JW-MET-1 fix that *did* land covers only `draft-v1.md`: `31ccef5` (2026-08-14) "Paper:
  boundary wording narrowed to the implemented CPU+GPU+ANE processor-package boundary at all five
  sites (JW-MET-1 …); **flagged for next review train**" — the flag was never actioned for the
  retained draft.
- Note `related_work_draft.md:13` also carries "whole-system-on-chip software-counter boundary" —
  but that phrase describes *Silicon Showdown's* boundary, not JouleWise's, so it is correct as
  written; only :19 is the residual.
- **WHERE it lives: nowhere.**

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND.** A nit-grade, one-sentence, claim-adjacent paper edit on a P1 deliverable,
unregistered and unmade; the seat is adjudicating whether nit-grade paper residues carry into a
READY-candidate verdict or are dispositioned out.

### (d) Skeptical probes

1. `git show ac3fe1d:docs/paper/related_work_draft.md | sed -n '19p'` vs current — confirm byte-identity.
2. `grep -rn "system-on-chip" docs/paper docs/report_src docs/contracts` — is :19 the last
   JouleWise-describing instance, or are there others the seat's grep missed?
3. `31ccef5` says "flagged for next review train". Which train, and what tracked it? If nothing,
   the flag mechanism itself is the finding.
4. Is the related-work draft in the P1 paper's build path, or retained-only? The answer changes
   whether "a later paper train copies the stale sentence back" is live.

---

## L3-N2 (nit) — samplers_available metadata echoes the requested list rather than a probed census

### (a) Original finding (VERBATIM)

Sitting-packet §4 title:

> - [nit] [L3] samplers_available metadata echoes the requested list rather than a probed census

Seat-report §6 finding 5:

> 5. **[nit] `samplers_available` echoes the requested list** — powermetrics.py:1175-1179 fills it from `SAMPLERS.split(\",\")` after any rc-0 probe (label `requested_sampler_probe` is honest); a bundle auditor could over-read it as a probed census; thermal has no parse-side existence check (thermal_pressure optional).

Remedy folded into WO-L3-4 (`triage.json:286`, quoted above).

Citation: sitting-packet-FINAL.md §4 line 144; seat report :46; refuter verdict — none.

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND.**

- `joulewise/adapters/powermetrics.py:1183`:
  `self._device_metadata["powermetrics"]["samplers_available"] = SAMPLERS.split(",")` — unchanged
  (line moved 1175→1183). The honest sibling label survives at `:1184`
  (`"samplers_probe": {"ok": True, …}`), and the unavailable branches at `:1449`/`:1457` set
  `"probe-unavailable"`.
- The adapter has no post-council commit on `origin/main` (`fdb311f`, 2026-07-22 is the newest);
  the branch-only commits add nothing here (diff grep for `samplers_available` → empty).
- **WHERE it lives: nowhere.**

### (c) Candidate disposition for the seat

**NO-REPAIR-FOUND.** A metadata-honesty nit on bundle provenance — the seat is adjudicating
whether "a bundle auditor could over-read it as a probed census" matters for the retained corpus's
defensibility, or is dispositioned as accepted-and-labelled.

### (d) Skeptical probes

1. Read `powermetrics.py:1183-1188`. Is any consumer reading `samplers_available` as a census
   (`grep -rn "samplers_available" joulewise/ scripts/ tests/`)?
2. The seat noted "thermal has no parse-side existence check (thermal_pressure optional)". Confirm
   the parser's behaviour if `thermal` is silently unavailable — does the bundle still claim it?
3. This is the one L3 finding touching **bundle metadata**, i.e. retained-corpus provenance. Ask
   whether the a9/a10 retained bundles carry the same over-readable field.

---

## L3-COV — coverage 25/29

### (a) Original finding (VERBATIM)

Sitting-packet §2 line 28 records coverage **25/29** with 7 unexecuted obligations.
Seat-report §2 (VERBATIM):

> **25 / 29 examined** at seat-relevant depth. Unexecuted obligations, plainly: crash-matrix module not run (hosted-pathological; concurrently held by a sibling seat; L2 scope); no live sudo/powermetrics of any kind (emitted as ED rows, none skipped silently); mock_telemetry unexamined (pack member verified pinning `telemetry_backend=powermetrics`); rail-probe.sh not line-audited; quiet-guard pair ruled to seats 1/9; rich-telemetry consumers and reducer internals corroborated at the seam only (L4); no hours-scale stream-cursor soak.

The seat's 29-item universe is enumerated at seat-report §1 (:10-12) before findings — production
code (1)-(11), tests/fixtures (12)-(20), docs/config (21)-(29).

Citation: sitting-packet-FINAL.md §2 line 28 and §6 lines 221-227 (the seven unexecuted
obligations verbatim); seat report §1-§2.

### (b) What changed since 2026-08-15

**NO-REPAIR-FOUND for the denominator itself.** The council's generalisation applies here with
full force — council-verdict.md:18-22 (VERBATIM):

> every seat's evidence universe was self-nominated, and the one denominator adversarially tested
> fell. Closing all listed work orders does not entitle READY; the READY-candidate re-audit must
> re-enumerate every universe independently and run the adversarial coverage attack as a standing
> packet element.

L3's universe was **never adversarially tested** — no refuter took an L3 lens — and Phase 3's
re-enumeration of "all universes" has been executed for exactly one seat (L2, custody
`docs/process_traces/2026-08-15-l2-reaudit/`, commit `0f886d3`, merged to main). There is no
L3 equivalent: `ls docs/process_traces/ | grep -i l3` → nothing.

Movement on individual unexecuted obligations since the sitting:
- **Crash matrix** (obligation 1, ruled L2 scope): now completes — the WO-DETECT-PULSES-BUDGET cure
  is merged to main via PR #159 (`04e34ee`); see the L2 row file. Does not change L3's denominator.
- **Live sudo/powermetrics** (obligation 2): partially discharged off-row by the 2026-08-17 Ed
  evening and the 2026-08-18 shakedown — see the L3-3 sub-row. Custody is off-repo.
- **rail-probe.sh not line-audited** (obligation 4): still not audited; the script was touched once
  by `e5dc38a` (sudo probe, 1 line).
- Obligations 3, 5, 6, 7 (mock_telemetry, quiet-guard pair, reducer/rich-telemetry internals,
  stream-cursor soak): **no change found**.

The seat's own note that 25/29 was measured "at seat-relevant depth" with an inconsistently
atomized unit (files, modules, doc sections and a PR commit all counted as one item each) is the
same structural weakness that killed L2's 15/16 — item (29) is "PR #127 squash commit `5060189`",
item (23) is "docs/paper/draft-v1.md JW-MET-1 sites + commit `31ccef5`".

### (c) Candidate disposition for the seat

**STILL-OPEN.** The seat is adjudicating a self-nominated, never-attacked denominator built on a
mixed unit of counting, at a sitting whose own verdict ordered independent re-enumeration of every
universe — with that order discharged for one seat out of eleven.

### (d) Skeptical probes

1. Apply the L2 re-audit's procedure to L3: derive the universe from charter nouns (sampler
   lifecycle, cadence, parse/integration, channel census, boundary coherence) and count with one
   stable unit. Does 29 survive, or does it move the way 16 → 251 did?
2. Items (17) `test_calibration_writer_crash_matrix` and (29) "PR #127 squash commit" are counted
   as single universe members alongside 2,251-line source files. Ask what the denominator means.
3. The seat executed 139 tests (63 adapter/parser + 46 fiducial + 30 calexits). Re-run them at
   `origin/main`, where `adapters/powermetrics.py` is unchanged but `powermetrics_fiducial.py` has
   the D-143 budget. Do all 139 still pass?
4. Ask whether any L3-scoped artifact changed between `8937dec` and `0099382`. The adapter did not;
   the fiducial module did (budget). Does that void or preserve this seat's results under charter
   amendment 12's final-head invalidation rule?

---

## ROW-LEVEL OPEN ITEMS

- **All three should-fix findings (L3-1, L3-2, L3-3) and both nits are UNREPAIRED at the current
  head, and none of WO-L3-1..4 was ever registered.** They exist only in
  `docs/process_traces/2026-08-15-readiness-council/triage.json:283-286` and the seat report;
  they appear in no TASK_QUEUE row, no `state_kernel.json` task, and are absent from
  council-verdict.md's own Phase-1 enumeration (lines 80-87). This is the row's single largest
  finding: the work orders were dropped between the seat report and the ratified program.
- **ED-L3-1 was closed on 2026-08-17 with both of its council-stated preconditions unmet**
  (WO-L3-2 checklist home, WO-L3-3 100 ms leg). Recorded PASS at cadence **1.0128 s** — the 1 Hz
  evidence the seat named as the defect. Evidence lives off-repo at
  `~/JouleWise-window-custody/ed-qual-20260817/ed-session-evidence/sampler-checklist-*.log`,
  unverifiable from this worktree. Belongs to the ED row file for disposition; flagged here because
  the closure contradicts this row's findings.
- **ED-L3-2 (live SIGTERM-relay termination) has NO closure evidence anywhere.**
  `grep -rn "ED-L3-2"` returns hits only in the council trace. The 2026-08-17 qualification ledger
  (`docs/run_reports/2026-08-18-t10-session.md:98-112`) does not list it. "Zero orphans" on a
  5-sample happy-path run is not a SIGTERM-grace observation.
- **ED-L3-4 (channel-census currency: `hw_model`/`kern_osversion` matched to Mac15,9 / macOS 25F84)
  has no recorded match.** `grep -rln "kern_osversion"` over `docs/run_reports`, `docs/process`,
  `docs/process_traces` finds nothing outside the 2026-08-15 council trace. The row also REOPENS on
  any OS update before the window.
- **Realized cadence is ~113.3 ms against a 100 ms nominal** (`2026-08-18-shakedown-first-light/02-root-cause-diagnosis.md:109-110`),
  observed as a by-product of detector diagnostics and never attributed to ED-L3-1/L3-4 or to the
  cadence row. No seat has dispositioned it.
- **WO-SAMPLER-SUPERVISOR is open, outside the generated kernel region, absent from
  `state_kernel.json`, and its lead-owed live-Mac ADMISSION GATE is unexecuted** after two failed
  formulations (`TASK_QUEUE.md:293-316`). The detect-and-report census WO-L3-1 specified was the
  interim mitigation for exactly this; neither exists on the measured-run path.
- **L3's 25/29 denominator has never been adversarially tested and never re-enumerated.** No
  refuter took an L3 lens; Phase 3's "adversarial coverage re-enumeration of all universes" is
  discharged for L2 only.
- **Cross-row note (verify with the L2 file):** the L3 seat deferred the crash matrix to L2 and L2
  could not complete it; the budget cure that unblocks it is merged to main (PR #159 / `04e34ee`),
  while the kernel still renders WO-DETECT-PULSES-BUDGET as "PARTIAL; READY [AGENT]".
