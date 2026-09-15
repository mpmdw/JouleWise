# lt-12 — Opus pairing refuter (contract lens) on cold-gate packet 25, INSTALL-WINDOWS-MULTI-01

Rule 11 pairing seat. Packet sha256 `b204398d…a261a`, charter sha256 `099de884…c95d81` and all nine exhibit
digests recomputed; all match their pins. Code read at `df86cee6` in `JouleWise-wt-coldgate-iw`. Read-only:
no worktree file modified except this one; probes ran `python3 -B` from `/tmp/opus-refuter-25/`.

## Independent answers (written before reading the ruling) — 2026-09-15 08:59 PDT (clock read, `date`)

### Executed probe (mine)

`/tmp/opus-refuter-25/probe_deadman_crossing.py` subclasses the tracked `tests/test_install_night_agent.py`
harness (zsh `launchctl-stub` + `_controlled_python` clock seam; no real `launchctl`, no
`~/Library/LaunchAgents`), advancing the clock at the DEAD-MAN bootstrap only — after the last
`check_schedule close` (`install_night_agent.sh:343`), before the job is created (`:348`).

- **CASE 1** (exhibit B row 1: spans `(("00:00","12:01"),("12:01","24:00"))`, 12:00 → 12:01:01):
  `exit=0`, both loaded, stderr empty. F1 reproduced.
- **CASE 2 — new, and it refutes the packet:** shipped whole-day default `(("00:00","24:00"),)`,
  now = `install_close_epoch(plan) − 1`, advanced to `install_close_epoch + 1`: `exit=0`, BOTH loaded.

Also bench-verified: `install_night_agent.sh:2` is `set -euo pipefail`; `zsh -c 'set -e; trap "print x" EXIT;
f(){ false; }; f'` exits 1 printing nothing (exhibit B F2 confirmed); `…epoch_25g83_rev1.md:143` is the
"Sample. Three agent-free [QUIET-MAC] windows on distinct calendar days" sentence; `decision_log.md:11873-
11875` (D-181 cl.1) keeps "pre-registration before data" among the fences that "stay exactly as they are".

### PACKET-HYGIENE DEFECT — BLOCKER for Q4, MATERIAL for Q1

Packet line 28 asserts "the blocker is latent under that default". True of the ORIGINAL defect
(`install_outside_span`, a span-list-only bound evaluated only in `initial` mode); FALSE of the residual F1
blocker at `:348`, because `check_schedule` tests `now >= schedule["install_close_epoch_s"]` in EVERY mode
(`:186-188`) and `install_close_epoch = t0 − PLAN_LEAD_S − INSTALL_CLOSE_MARGIN_S` exists under the whole-day
default. CASE 2 proves exit 0, both agents loaded, on the shipped default; exhibit B's own rows 3–4 say it
too, and the packet did not carry them into Q4's premise.

### Q1 — structure

**(c); a MECHANISM CHOICE inside the exhibit-E contract, not a contract change.** (a) adds one more point
check to an open set. (b) alone also fails: a budget predicts rather than observes, so a hung `bootstrap`
overruns it and a terminal check is needed anyway. The class closes by converting the
requirement from preconditions at call sites into a POSTCONDITION after the LAST mutation:

> The installer exits 0 only if a clock read strictly AFTER the final `bootstrap` and its verification
> satisfies `now < min(selected_span_close, install_close_epoch)`. On any other outcome — refusal, error,
> `errexit`, signal — it exits non-zero through ONE idempotent teardown.

That is exhibit E's adjudicated contract ("refuses unless BOTH hold") plus kernel clause (b), with no new
constant and no new refusal class. Existing point checks may stay as early exits; residual
exposure is then teardown-bounded and points the SAFE way (nothing loaded).

### Q2 — the bound

**Yes, E's rejection extends to `MAX_INSTALL_DURATION_S`; nothing needs to carry the bound.** E rejected
`MAX_PLAN_SPAN_S` because "a new ceiling constant is a new rule; not this lane's to invent". A duration
ceiling is the same kind: nothing physical pins it, and it would refuse installs that WOULD have finished in
time — a new refusal the contract does not contain, i.e. a contract change. Under the Q1 postcondition no
bound is needed, and the margin is already pinned: `INSTALL_CLOSE_MARGIN_S = 3600` (`run_night.py:68`). Any operator-facing
duration figure stays a MEASURED start/end pair in the arm record, diagnostic only.

### Q3 — cleanup shape

**Mechanism choice; bootout-before-remove IMPLEMENTS the exhibit-E plist fence rather than changing it.** E
adopted "watchdog reads the INSTALLED plists … unreadable → `HOLD_UNSAFE`", so the fence assumes a plist
exists whenever a job is loaded; F3's "both plists deleted, job loaded" is the one state that blinds it.
REQUIRED shape:

1. ONE idempotent `teardown_install()`, single entry, the SOLE cleanup path.
2. It bootouts BOTH labels (ignoring "not loaded"), then RE-READS with `launchctl print`. If either is still
   loaded it touches NO plist — prints the loaded labels, exits non-zero. Never delete a plist under a
   loaded job. Only when both report not-loaded does it restore/remove plists, then the backup directory.
3. `trap teardown_install EXIT` is INSUFFICIENT: `:2` sets `-e` and zsh 5.9 skips the EXIT trap on `errexit`
   inside a function (bench-proved). Each mutation and each `render` takes `… || { teardown_install; exit
   N; }`; INT/TERM/HUP traps call it before exiting 130/143/129.

Proving regression (must FAIL when only the production teardown call is reverted): a fake-launchctl matrix
over {render failure via read-only prior plist; both bootstrap failures; close crossed during the dead-man
bootstrap; TERM/INT/HUP; bootout ITSELF failing} asserting per cell exit non-zero, no marker for either
label, prior plist bytes intact, no leaked backup dir — and for the bootout cell the inverse: plists PRESENT.

### Q4 — landing

**(i): close the blocker before the lane lands.** Primary reason is CASE 2, not judgment: the blocker is NOT
latent under the shipped default, so (ii)'s bargain does not exist — pinning a refusal of non-default span
lists leaves the same exit-0-both-loaded path reachable on the default. Secondary: under the Q1
postcondition the cure is one clock read plus the Q3 teardown, inside one bounded seat. Sub-question: (ii)
is not strictly a "reinterpretation" of D-181 cl.1 (whose text says decided ≠ done, and that a mechanism
limit is a fact not a rule) — but TEST-PINNING the refusal converts that limit into a code-enforced
constraint against the capability D-180/D-181 promote to rank 0, which is Ed's or the magistrate's call.

### Q5 — FIX-5 narrowing of acceptance clause (c)

**AFFIRM, with the kernel acceptance text amended to match.** `StartCalendarInterval` has no seconds field,
so a `t0` with non-zero seconds fires EARLY, the gate refuses `night_window_expired`, and the write-once
record at `run_night.py:1507-1510` consumes a pre-registered plan — evidence-bearing loss, exactly where
D-161 leaves fail-closed intact. Same for a folded local minute: both occurrences render identical fields
and real launchd dispatch on a repeated minute is unestablished, so the AMEND alternative (deterministic
fold 0) rests on unverified behaviour. Cost: one local hour a year, reversible. Clause (c) narrows to whole,
locally-unambiguous minutes, two refusal literals.

### Q6 — runbook §3 vs D-181

**(i) No conflict.** D-181 cl.1 (`decision_log.md:11873-11875`) keeps "pre-registration before data" as an
unchanged fence and removes only cadence RULES. The distinct-calendar-days requirement
(`preregistration_d079_epoch_25g83_rev1.md:143`) is not a cadence rule but part of the registered SAMPLE for
the d079 epoch-25G83 campaign. The runbook's install-span text must say that spans may recur several times a
day under D-181 cl.1, governing only when the machinery may install and arm and never the registered sample;
that the FAIL route's three [QUIET-MAC] windows stay on three DISTINCT CALENDAR DAYS per that line; and that
moving two onto one day amends a registration made before data, which only Ed may do. Severity MATERIAL; the defect is
silence at that text, not any change to §3 (byte-identical, `71337a83…072b`).

## Pairing refutation of ruling 10 — 2026-09-15 09:04 PDT (clock read)

Read only after the section above was sealed. Its probes DID run (`/tmp/coldgate-iw/test_probe.py` 08:58,
`test_probe2.py` 08:59). Citations spot-checked, all correct: `magistrate_watchdog.py:712`
`installed_agent_fence`, `run_night.py:68`, `launchd.plist.5:468`, runbook `:1297` and `:2085-2086`.
Verdicts converge on all six; two amendments, one material.

- **Q1 — AFFIRM.** Same postcondition I reached independently; its single commit gate before the success
  `print` at `:360` is strictly stronger than "after the last mutation" (it covers the verification `print`s
  too), and its exactly-at-close regression additionally kills exhibit B F4's `>=`→`>` survivor.
- **Q2 — AFFIRM, NIT amendment.** "No measured duration and no derived margin are to be added" over-reaches:
  an install start/end pair recorded in the arm record is diagnostic, not a bound. Read it as forbidding any
  duration FEEDING A REFUSAL.
- **Q3 — AMEND (BLOCKER).** Its teardown is `bootout … || true` then restore/remove files UNCONDITIONALLY,
  so if the bootout itself fails it produces precisely the state class 2 is about. Executed
  (`/tmp/opus-refuter-25/probe_bootout_failure.py`, stub `bootout` exits 1 leaving the label loaded,
  dead-man bootstrap fails, shipped default span): `exit=3`, `loaded=['com.joulewise.night']`, `plists=[]`,
  stderr `"rolled back com.joulewise.night"` — loaded job, no plist, fence blind, under a success-shaped
  rollback message. Exhibit B named this case ("A forced rollback-bootout failure likewise
  exits 2 printing 'rolled back' while the job remains loaded and its plists are deleted"); the ruling's
  step-1 shape and its six-cell step-4 matrix both omit it. Exact replacement — insert into step 1 between
  the bootouts and the restore, and extend step 4:
  > After both bootouts, re-read `launchctl print gui/$uid/<label>` for each label. If either still reports
  > loaded, restore NOTHING and remove NOTHING (including `$plist_backup`): print both labels still loaded
  > and the plist paths retained, and return a distinct non-zero status. Only when both report not-loaded may
  > the restore / `rm -f` / `rm -rf "$plist_backup"` run. Step 4 gains a `bootout` rc=1 injection whose
  > expectation is the INVERSE of the other cells: exit non-zero AND both plists still present AND
  > `installed_agent_fence()` still sees the plan.
- **Q4 — AFFIRM, strengthened.** It falsified (ii)'s premise through class 2 under the default span; I
  falsified it independently through class 1 — CASE 2 shows the `:348` crossing exits 0 with BOTH agents
  loaded under the shipped whole-day default, since `install_close_epoch` is tested in every mode
  (`:186-188`). Its P-F1a/b used narrowed spans only, so this is additional evidence, not an echo. Its D-181
  reading (a test-pinned refusal is a mechanism limit, not Ed-only) is correct and does not disturb (i).
- **Q5 — AFFIRM.** Its kernel text is more exact than mine (`t0_epoch_s % 60 == 0`); I adopt it.
- **Q6 — AFFIRM the verdict; AMEND the second insertion (MATERIAL).** Q6(i) asked for the sentence at the
  install-span text; its `:1297` sentence answers that and I affirm it. Its SECOND insertion rewrites runbook
  §3 item 3 (`:2085-2086`) — byte-identical text declared untouchable in every brief of this lane and the
  carrier of the pre-registration constraint. The wording preserves the constraint and only cross-references,
  so it does not amend the registration; but record it as a SEPARATE, Ed-visible docs item rather than
  folding it into INSTALL-WINDOWS-MULTI-01's diff.
- **Answered but not asked:** (1) it authorises fix round 2 and prescribes the post-round sequence (delta
  re-audit, twelve-row gate); charter §9 requires explicit justification before another same-shape round, so
  this is in remit and justified ("the structure changed, not the call site"). (2) the §3 item-3 edit.
- **Rule or doctrine amendments attempted: NONE FOUND.** Every text change is framed as text for the
  magistrate to record, and it says so.
- **Coldness observation (process, not a defect in the ruling):** the judge discloses that the harness
  auto-loaded `~/.claude/CLAUDE.md` and this worktree's `CLAUDE.md` — both doctrine. Convene cold seats in a
  doctrine-free worktree, no user-level `CLAUDE.md` on the path. No verdict here changes.
