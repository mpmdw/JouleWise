# lt-12 — Opus pairing refuter (contract lens) on cold-gate packet 25, INSTALL-WINDOWS-MULTI-01

Rule 11 pairing seat. Packet sha256 `b204398d…a261a` and charter sha256 `099de884…c95d81` recomputed, both
match the convening pins; all nine exhibit digests match the packet manifest. Code read at `df86cee6` in
`/Users/edr/code/JouleWise-wt-coldgate-iw` (`git rev-parse HEAD` confirmed). Read-only seat: no file in any
worktree modified except this one; probes ran `python3 -B` from `/tmp/opus-refuter-25/`.

## Independent answers (written before reading the ruling) — 2026-09-15 08:59 PDT (clock read, `date`)

### Executed probe (mine)

`/tmp/opus-refuter-25/probe_deadman_crossing.py` subclasses the tracked `tests/test_install_night_agent.py`
harness (its zsh `launchctl-stub`, its `_controlled_python` clock seam; no real `launchctl`, no
`~/Library/LaunchAgents`) and advances the fake clock at the DEAD-MAN bootstrap only — after the last
`check_schedule close` (`install_night_agent.sh:343`), before the job is created (`:348`).

- **CASE 1** (exhibit B row 1: spans `(("00:00","12:01"),("12:01","24:00"))`, 12:00 → 12:01:01):
  `exit=0`, both labels loaded, stderr empty. F1 reproduced.
- **CASE 2 — new, and it refutes the packet:** shipped whole-day default `(("00:00","24:00"),)`,
  now = `install_close_epoch(plan) − 1`, advanced to `install_close_epoch + 1`: `exit=0`, BOTH loaded.

Bench-verified besides: `install_night_agent.sh:2` is `set -euo pipefail`; `/bin/zsh -c 'set -e; trap "print
trap-fired" EXIT; f(){ false; }; f'` exits 1 printing nothing (exhibit B F2 confirmed);
`preregistration_d079_epoch_25g83_rev1.md:143` is the "Sample. Three agent-free [QUIET-MAC] windows on
distinct calendar days" sentence; `decision_log.md:11873-11875` (D-181 cl.1) keeps "pre-registration before
data" among the fences that "stay exactly as they are".

### PACKET-HYGIENE DEFECT — BLOCKER for Q4, MATERIAL for Q1

Packet line 28 asserts "the blocker is latent under that default". True of the ORIGINAL defect
(`install_outside_span`, a span-list-only bound evaluated only in `initial` mode); FALSE of the residual F1
blocker at `:348`, because `check_schedule` tests `now >= schedule["install_close_epoch_s"]` in EVERY mode
(`:186-188`) and `install_close_epoch = t0 − PLAN_LEAD_S − INSTALL_CLOSE_MARGIN_S` exists under the whole-day
default. CASE 2 proves exit 0, both agents loaded, on the shipped default. Exhibit B's own rows 3–4 say it
too; the packet did not carry them into Q4's premise.

### Q1 — structure

**(c); a MECHANISM CHOICE inside the exhibit-E contract, not a contract change.** (a) adds an eleventh point
check to an open set. (b) alone also fails: a pre-sequence budget is a prediction, and a slow or hung
`bootstrap` overruns any budget, so (b) still needs a terminal check. The class closes by converting the
requirement from preconditions at call sites into a POSTCONDITION after the LAST mutation:

> The installer exits 0 only if a clock read strictly AFTER the final `bootstrap` and its verification
> satisfies `now < min(selected_span_close, install_close_epoch)`. On any other outcome — refusal, error,
> `errexit`, signal — it exits non-zero through ONE idempotent teardown.

That is exhibit E's adjudicated contract ("refuses unless BOTH hold") plus kernel clause (b), with no new
constant and no new refusal class. Existing point checks may stay as early exits; they stop being
load-bearing. Residual exposure is then bounded by teardown duration and points in the SAFE direction
(nothing loaded) — the asymmetry point checks never had.

### Q2 — the bound

**Yes, E's rejection extends to `MAX_INSTALL_DURATION_S`; nothing needs to carry the bound.** E rejected
`MAX_PLAN_SPAN_S` because "a new ceiling constant is a new rule; not this lane's to invent". A duration
ceiling is the same kind: nothing physical pins it, and it would refuse installs that WOULD have completed
in time — a new refusal the contract does not contain, i.e. a contract change. Under the Q1 postcondition no
bound is needed, and the margin is already pinned: `INSTALL_CLOSE_MARGIN_S = 3600` (`run_night.py:68`). Any
operator-facing duration figure stays a MEASURED install start/end pair in the arm record, diagnostic only.

### Q3 — cleanup shape

**Mechanism choice; no adjudication needed — bootout-before-remove IMPLEMENTS the exhibit-E plist fence
rather than changing it.** E adopted "watchdog reads the INSTALLED plists … unreadable → `HOLD_UNSAFE`", so
the fence assumes a plist exists whenever a job is loaded; F3's "both plists deleted, job loaded" is the one
state that blinds it. REQUIRED shape:

1. ONE `teardown_install()`, idempotent, single entry, safe to call twice.
2. Bootout BOTH labels unconditionally (ignore "not loaded"), then RE-READ with `launchctl print`.
3. If either is still loaded: touch NO plist — print the labels still loaded, exit non-zero. Never delete a
   plist under a loaded job.
4. Only when both print not-loaded: restore backed-up bytes / remove plists this run created, then the
   backup directory.
5. Every non-success path routes through it. `trap teardown_install EXIT` is INSUFFICIENT: `:2` sets `-e`
   and zsh 5.9 skips the EXIT trap on `errexit` from inside a function (bench-proved). So each mutation and
   each `render` takes an explicit `… || { teardown_install; exit N; }`, and INT/TERM/HUP traps call
   `teardown_install` before exiting 130/143/129 instead of bare `exit`.

Proving regression (must FAIL when only the production teardown call is reverted): a fake-launchctl matrix
over {render failure via read-only prior plist; night bootstrap failure; close crossed during the dead-man
bootstrap; TERM/INT/HUP after the first bootstrap; bootout ITSELF failing in teardown}, asserting per cell —
exit non-zero, no `launch_log.<label>` marker for either label, prior plist bytes byte-identical, no plist
created that did not exist before, no leaked `night-agent-install.*` backup dir; and for the bootout-failure
cell the inverse — exit non-zero AND both plists still present.

### Q4 — landing

**(i): close the blocker before the lane lands.** Primary reason is CASE 2, not judgment: the blocker is NOT
latent under the shipped default, so (ii)'s bargain does not exist — pinning a refusal of non-default span
lists leaves the same exit-0-both-loaded path reachable on the default. Secondary: under the Q1
postcondition the cure is one clock read plus the Q3 teardown, inside one bounded seat. Sub-question: (ii)
would not be a strict "reinterpretation" of D-181 cl.1 (its own text says decided ≠ done, and a mechanism
limit is a fact not a rule) — but TEST-PINNING the refusal converts that limit into a code-enforced
constraint against the capability D-180/D-181 promote to rank 0, which is Ed's or the magistrate's call,
never the lieutenant's. Moot under CASE 2.

### Q5 — FIX-5 narrowing of acceptance clause (c)

**AFFIRM, with the kernel acceptance text amended to match.** `StartCalendarInterval` has no seconds field,
so a `t0` with non-zero seconds fires EARLY, the gate refuses `night_window_expired`, and the write-once
record at `run_night.py:1507-1510` consumes a pre-registered plan — evidence-bearing loss, exactly where
D-161 leaves fail-closed intact. Same for a folded local minute: both occurrences render identical fields
and real launchd dispatch on a repeated minute is unestablished, so the AMEND alternative (deterministic
fold 0) would rest on unverified behaviour. Cost: one local hour a year, one literal, reversible. Text for
the magistrate to RECORD (recording, not amending):
> acceptance clause (c): the plan's `t0` may be any clock time launchd can express exactly — any whole
> minute (seconds = 0) occurring exactly once in local time; a fractional-second `t0` is refused
> `plan_t0_not_minute_aligned`, a DST-repeated local minute `plan_t0_ambiguous_local_time`, both
> fail-closed under D-161 because a mis-dispatch consumes a pre-registered plan.

### Q6 — runbook §3 vs D-181

**(i) No conflict.** D-181 cl.1 (`decision_log.md:11873-11875`) keeps "pre-registration before data" as an
unchanged fence and removes only cadence RULES. The distinct-calendar-days requirement
(`preregistration_d079_epoch_25g83_rev1.md:143`) is not a cadence rule but part of the registered SAMPLE for
the d079 epoch-25G83 campaign. Sentence for the runbook at the install-span text:
> Install spans may recur several times a day (D-181 cl.1); this governs only when the machinery may be
> installed and armed, never the registered sample. The FAIL route's three [QUIET-MAC] capture windows
> remain on three DISTINCT CALENDAR DAYS per
> `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143`; putting two of those three on one
> calendar day amends a registration made before data, and only Ed may do that.

Severity MATERIAL: §3 is byte-identical (SHA-256 `71337a83…072b`), so nothing was changed under the
registration; the defect is silence at the install-span text.

## Pairing refutation of ruling 10 — 2026-09-15 09:04 PDT (clock read)

Read only after the section above was written. Its probes DID run: `/tmp/coldgate-iw/test_probe.py` (08:58)
and `test_probe2.py` (08:59) exist. Citations spot-checked and correct: `magistrate_watchdog.py:712`
`installed_agent_fence`, `run_night.py:68`, `launchd.plist.5:468` "The minute (0-59)", runbook `:1297`,
runbook `:2085-2086` = §3 item 3. Verdicts converge on all six; two amendments, one material.

- **Q1 — AFFIRM.** Same postcondition I reached independently; its single commit gate before the success
  `print` at `:360` is strictly stronger than "after the last mutation" (it also covers the verification
  `print` calls). Its exactly-at-close regression additionally kills exhibit B F4's `>=`→`>` survivor.
  Agreed it is a mechanism choice, not a contract change.
- **Q2 — AFFIRM, NIT amendment.** "No measured duration and no derived margin are to be added" over-reaches
  by a word: an install start/end pair recorded in the arm record is diagnostic, not a bound. Read the
  sentence as forbidding any duration that FEEDS A REFUSAL.
- **Q3 — AMEND (BLOCKER).** Its teardown is `bootout … || true` then restore/remove files UNCONDITIONALLY.
  If the bootout itself fails, that produces precisely the state class 2 is about. Executed
  (`/tmp/opus-refuter-25/probe_bootout_failure.py`, stub `bootout` exits 1 leaving the label loaded,
  dead-man bootstrap fails, shipped default span): `exit=3`, `loaded=['com.joulewise.night']`, `plists=[]`,
  stderr `"rolled back com.joulewise.night"` — a loaded job, no plist, the fence blind, and a success-shaped
  rollback message. Exhibit B named this case ("A forced rollback-bootout failure likewise exits 2 printing
  'rolled back' while the job remains loaded and its plists are deleted"); the ruling's step-1 shape and its
  six-cell step-4 matrix both omit it. Exact replacement — insert into step 1 between the bootouts and the
  restore, and extend step 4:
  > After both bootouts, re-read `launchctl print gui/$uid/<label>` for each label. If either still reports
  > loaded, restore NOTHING and remove NOTHING (including `$plist_backup`): print both labels still loaded
  > and the plist paths retained, and return a distinct non-zero status. Only when both report not-loaded may
  > the restore / `rm -f` / `rm -rf "$plist_backup"` run. Step 4 gains a `bootout` rc=1 injection whose
  > expectation is the INVERSE of the other cells: exit non-zero AND both plists still present AND
  > `installed_agent_fence()` still sees the plan.
- **Q4 — AFFIRM, strengthened.** It falsified (ii)'s premise through class 2 under the default span; I
  falsified it independently through class 1 — my CASE 2 shows the `:348` crossing exits 0 with BOTH agents
  loaded under the shipped whole-day default, because `install_close_epoch` is tested in every mode
  (`:186-188`) and is a per-plan bound. Its P-F1a/b used narrowed spans only, so this is additional
  evidence, not an echo. Its D-181 reading (a test-pinned refusal would be a mechanism limit, not Ed-only)
  is correct on the text and does not disturb (i).
- **Q5 — AFFIRM.** Its kernel text is more exact than mine (`t0_epoch_s % 60 == 0`); I withdraw my wording
  in favour of it.
- **Q6 — AFFIRM the verdict; AMEND the second insertion (MATERIAL).** Q6(i) asked for the sentence at the
  install-span text; its `:1297` sentence answers that and I affirm it. Its SECOND insertion rewrites runbook
  §3 item 3 (`:2085-2086`) — byte-identical text declared untouchable in every brief of this lane and the
  carrier of the pre-registration constraint. The wording preserves the constraint and adds only a
  cross-reference, so it is not an amendment to the registration; but it should be recorded as a SEPARATE,
  Ed-visible docs item rather than folded into INSTALL-WINDOWS-MULTI-01's diff.
- **Answered but not asked:** (1) it authorises fix round 2 and prescribes the post-round sequence (delta
  re-audit, twelve-row gate). Charter §9 requires explicit justification before another same-shape round, so
  the authorisation is in remit and justified ("the structure changed, not the call site"), and the
  sequencing restates existing mechanism. (2) the §3 item-3 edit above.
- **Rule or doctrine amendments attempted: NONE FOUND.** Every text change is framed as text for the
  magistrate to record, and the ruling says so explicitly.
- **Coldness observation (process, not a defect in the ruling):** the judge discloses that the harness
  auto-loaded `~/.claude/CLAUDE.md` and this worktree's `CLAUDE.md` before it read anything — both doctrine.
  Cold seats should be convened from a doctrine-free worktree with no user-level `CLAUDE.md` on the path, or
  the coldness premise is weakened. Recorded for the magistrate; it changes no verdict here.
