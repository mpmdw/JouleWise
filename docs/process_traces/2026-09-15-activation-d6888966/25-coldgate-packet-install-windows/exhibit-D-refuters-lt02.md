# lt-02 — Refuter round 1: two distinct lenses on the integrated diff

Both seats launched against `int/2026-09-15-install-windows` at **`7a512827`**
(after the lt-01 docs reconciliation), diff base `origin/main` = `e42949dc`.
Astra `gpt-6-astra --effort xhigh --genre review`, detached, `codex-run-v3`.

| Lens | Worktree | Sandbox | Launched | Returned | pid | Output |
|---|---|---|---|---|---|---|
| CONTRACT | `wt-ref-iw-contract` (detached) | read-only | 07:09:32 | 07:28 | 16082 | `/tmp/magistrate-d6888966/lt-02-ref-contract.md` |
| EXECUTION | `wt-ref-iw-execution` (detached, disposable) | workspace-write (see lt-00 deviation) | 07:10:01 | 07:28 | 18973 | `/tmp/magistrate-d6888966/lt-03-ref-execution.md` |

Neither seat was told about the reconciliation seat's F1, so the two
independent findings of it below are genuine corroboration, not an echo. The
execution seat ended with `git status --porcelain` EMPTY (pasted as its final
verification entry); the contract seat changed nothing.

## The blocker — THREE independent findings of one defect

`scripts/install_night_agent.sh:192`. `install_outside_span` is evaluated only
under `if sys.argv[4] == "initial"`. The three `close`-mode rechecks
(`:305,:307,:312`, around the bootout and both bootstraps) test only
`now >= install_close_epoch_s`. An installation can therefore begin inside a
listed span and bootstrap BOTH agents after that span has closed, as long as it
is still before the plan cutoff.

- Reconciliation seat F1 (`defect_in_code`, blocking) — extracted `SCHEDULE_CHECK`, synthetic times.
- Contract **C1** (blocker) — traced the nine-step path; executed the installer's real embedded Python: `now=1000 mode=initial exit=2 install_outside_span` versus `now=1000 mode=close exit=0`.
- Execution **E1** (blocker) — end-to-end with fake launchctl: span `[00:00,12:01)`, install begun at 12:00, controlled clock advanced to **12:01:01 during bootout**; result `EXIT 0` with both plists written and both labels loaded.

The lead read `install_night_agent.sh:186-198` and `:300-320` and confirms the
control flow independently. Two refuters with distinct lenses agree, so the
blocker stands under the severity rule; the lieutenant did not adjudicate it in
either direction. It violates acceptance clause (b) — every listed span carries
"the never-install-after-close" rule — and the adjudicated ruling that the
installer refuses unless BOTH bounds hold. Latent under the shipped whole-day
default (no daily gap); live the moment a narrowed span list is configured,
which is the capability this lane ships.

## Corroborated should-fix (both lenses, independently)

- **C3 / E5 — calendar rendering discards seconds and DST fold** (`run_night.py:1023`). `t0 13:20:17` renders `Hour 13, Minute 20`. Executed: driver fired at `13:20:02`, gate REFUSED `night_window_expired` (`detail: now 1789590002.0 is outside [1789590017.0, ...]`), and the write-once record at `:1507-1510` then makes the plan unusable — a valid plan silently consumed. Both 2026-11-01 `01:30` occurrences render identical fields, so a fold-1 plan fires an hour early with the same outcome.
- **C2 / E6 — DST resolution breaks the validated span invariants** (`run_night.py:996-1012`). Order/disjointness are proven in wall-clock minutes; endpoints then resolve to epochs independently. Executed: `(("02:45","03:15"),)` on 2026-03-08 resolves to open `03:45` / close `03:15`, duration **−1800 s**; on 2026-11-01 `("01:15","01:45")` and `("01:45","02:00")` resolve to OVERLAPPING intervals.

## Execution-lens only

- **E2** (`install_night_agent.sh:298,308,317`) — a failed bootstrap rolls back LABELS but leaves the rendered PLISTS. Executed follow-on: `decide()` with discovery empty returned `FENCED reason='installed_plan:fail-night'`. A failed install silently fences the magistrate.
- **E3** (`run_night.py:1939`) — `schedule` raises tracebacks, exit 1, on all six missing/malformed timing-field cases and on `window_max_s=10**15` (`ValueError: year must be in 1..9999`) and `10**400` (`OverflowError`).
- **E4** (`magistrate_watchdog.py:744`) — an installed plist pointing at `window_max_s=10**400` raises `OverflowError` out of `decide()`; the caught-exception tuple omits it. The safety component crashes where it should HOLD_UNSAFE.

## Contract-lens only

- **C4** (`derivation_night_runbook.md:304-310,340-345,364-385`) — the live recipe derives clone path, plan ID, session ID and custody names from `NIGHT_DATE` ALONE and then requires those paths not to exist. The code supports same-day successors; the operator recipe cannot express one. This is acceptance clause (d) unmet at the operator surface.
- **C5** (`:2458`, `:2516`) — two live reference rows say a plan span forbids adoption; `magistrate_watchdog.py:1459-1468` returns `STANDDOWN_<phase>, adopt=True` for an owned session in a discovered active span.

## Mutation sweep (execution lens): 68 mutations, 53 RED, 15 survived, 2 equivalent

The material survivors: `INSTALL_CLOSE_MARGIN_S 3600→3599` and `→3601`; removal
of import-time span validation; the span opening `<=→<` and closing `<→<=`
boundaries in the installer; past-t0 `<→<=`; watchdog authorship `>→>=` at
`:775,:740` and armed deadline `<=→<` at `:782`; and at `:821` the conflict
intersection `<=→<` plus BOTH collapsed operands of `max(...)`/`min(...)`
(the operand-collapse class). The contract lens independently showed WHY the
margin mutants live: the existing assertion at `tests/test_run_night.py:1382-1386`
is self-referential — it passes with `INSTALL_CLOSE_MARGIN_S = 0`. Acceptance
clause (e) says the tests PIN these quantities; they do not.

## What the refuters confirmed SOUND (worth recording)

v2 schema byte-unchanged with exact key sets retained; the whole "untouched"
list of design §6 verified byte-identical against base `e42949dc` (night-gate
refusal registry, census, `PLAN_LEAD_S`, stand-down ladder and
`ResidentSupervisor`, courier constants and `run_courier`, `window_max_s`
arithmetic, the write-once record set, email-then-arm ordering, the twelve-row
template, `dead_man()`, the relaunch prompt, the plan writer and the scientific
pre-registration); no ruled-out design shipped; the 3600 s grace ≥ the 2040 s
courier budget with its assertion present; refuse-if-loaded exit 3; both plists
`plutil -lint` OK with night `Month/Day/Hour/Minute` and dead-man `Hour/Minute`;
independent epoch arithmetic matched the code on three plans including both DST
dates (no one-hour error); results branch AND trace directory keyed by
`plan_id`, with a same-day A/B publish probe showing no collision and no
remaining date-shaped consumer outside historical evidence; a second same-day
plan armed successfully after uninstall; the recovery-grace and installed-plist
robustness matrices behaved as documented at every boundary except the
`OverflowError` cell (E4); the generated runsheet region check PASSes; no live
command passes `--hour`/`--minute`.

## Escalation, NOT fixed here

Both the docs seat (its F2) and the contract lens (§8) find runbook §3's
FAIL-route **distinct-calendar-days constraint DESIGN-BEARING**. The contract
lens cites `configs/calibration/preregistration_d079_epoch_25g83_rev1.md:143` as
making it part of the registered sample, and `decision_log.md:11869-11876` for
D-181 cl.1 preserving pre-registration before data. Its reasoning: generic
same-day installation does not invalidate the protocol, but USING same-day
windows as the three FAIL-route registration windows would conflict with the
registered sampling design. Neither the lieutenant nor any seat may rule on
this; §3 was declared untouchable in every brief and is byte-identical. It goes
to the cold gate / Ed.

## Coverage gap the lead must close (not delegable)

**Neither refuter ran the four changed test modules end to end.** The contract
seat's read-only sandbox denied `/tmp` fixture creation (its V1 showed 91 setup
ERRORS, not failures); the execution seat stopped short because those modules
commit into git fixtures and its brief forbade `git commit` without qualifying
the fixture case. Full-module mutation survival is therefore unverified. The
lead runs the modules at the replay (ledger row 9) and the fix-round brief
explicitly permits git operations confined to `/tmp` fixture directories.
