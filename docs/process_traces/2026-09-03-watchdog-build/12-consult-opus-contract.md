# Consult — Opus seat, contract lens — magistrate relaunch watchdog (2026-09-04)

Seat: Opus, contract lens, read-only except this file. Worktree
`/Users/edr/code/JouleWise-wt-watchdog-build`, branch
`feat/2026-09-03-magistrate-watchdog`, head `1e324e3d`, base for the round-4 diff
`4a23c119`.

Read this session: `10-delta-reaudit-round-4.md` (full);
`origin/main:docs/process_traces/2026-09-02-hands-free-week/19-coldgate-fable-ruling-packet-17.md`;
`…/20-magistrate-synthesis-gate-17.md`; `scripts/magistrate_watchdog.py`
(:20–120, :161–191, :204–300, :334–350, :399–470, :480–560, :646–760, :887–960,
:1528–1623); `joulewise/night_gate.py` (:1–40, :140–280, :418, :612–645);
`scripts/run_night.py` (:265–300, :840–900); `tests/test_magistrate_watchdog.py`
(:1–205, :659–690, :760–800); `tests/test_install_night_agent.py` (:55–150);
`scripts/install_night_agent.sh` (:51–95); `docs/process/MAGISTRATE_WATCHDOG.md`
(:110–180); `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` (all 23 lines);
`git diff 4a23c119..HEAD`.

Standing license: I disagree with the magistrate where marked. The two
disagreements that matter are in Q3 (round 4's ignore-everything rule is the
wrong shape, not merely mis-scoped) and Q4 (ancestry is not the missing
provenance; an artifact only this magistrate could have written is).

---

## Q1 — The structural cause of unit-green / production-broken

The suite is green because it tests the decision logic and never tests the
wiring, and because the fixtures, the code, and the oracle were written by one
author with one belief about the schema. Four facts, each checked this session.

**(a) The production wiring layer is executed by zero tests.** `Harness`
(`tests/test_magistrate_watchdog.py:53-85`) builds `wd.Dependencies` from fakes
for the four surfaces where production differs — `census`, `git_probe`,
`processes`, `spawn`. Grepping the test module for the production constructors
returns matches only for `version_probe` as a lambda keyword (`tests:82`) and
`remote_stop_probe` under a mocked `subprocess.run` (`tests:276-280`).
`production_census` (`scripts/magistrate_watchdog.py:334`), `real_dependencies`
(`:430`), `real_spawn` (`:399`), `version_probe` (`:417`), `build_parser`
(`:1569`) and `main` (`:1587`) are named in no test. The asymmetry is the
finding: the single production probe that *is* exercised is the single one that
did not break in the merge.

**(b) There are two literal constructions of the same frozen contract object,
and the merge updated one.** `Probes` gained a required `measurement_head` field
(`joulewise/night_gate.py:163-169`). The canonical production bundle is
`scripts.run_night.make_probes` (`scripts/run_night.py:267-290`), which supplies
it (`:276-290`). The watchdog hand-rolls a second bundle at
`scripts/magistrate_watchdog.py:334-342` and does not — even though that module
*already imports from `scripts.run_night`* at `:44-48`
(`COURIER_DEADLINE_S`, `COURIER_LOCK_FRESH_S`, `_next_deadman_epoch`). F1 is not
a missing keyword argument; it is a duplicated constructor. The tell that the
duplicate was never meant to be a peer is the placeholder value on the line
above: `checkout_head=lambda: "unused-by-agent-census"` (`:339`).

**(c) Fixtures are hand-authored duplicates of the plan schema, edited by the
same seat, in the same commit as the code.** `make_plan`
(`tests/test_magistrate_watchdog.py:99-118`) writes a literal dict. The v1→v2
migration was a manual edit to that literal — the round-4 diff shows
`"schema"` flipped and `measurement_root` / `measurement_head` typed in by hand
at `tests:102-110`, inside commit `e09ed7ce`, the same commit as the code. A
fixture authored this way cannot disagree with its author's belief about the
schema; it can only disagree with the schema, which is a different and much
rarer event. The same commit also had to hand-edit two doc examples, policed by
a string-count assertion (`tests:769-778`) — three hand-updated sites, and a
fourth (`:334-342`) missed.

**(d) No test runs the CLI as a process.** `subprocess` appears in the watchdog
test module only as `mock.patch.object(wd.subprocess, "run", …)`
(`tests:270-280`). The entry point `main()` (`:1587-1618`), the argparse surface
(`:1569-1584`), and the new `handoff-inventory` command (`:1589-1595`) are never
executed. The repo already owns the correct pattern one module over:
`tests/test_install_night_agent.py:97-118` runs `/bin/zsh
scripts/install_night_agent.sh` as a real subprocess against a stub `PATH` and a
real temp git repo — which is exactly why the installer's plan-pin defects (the
Q1 cure) were caught and the watchdog's were not.

**(e) Worse than a gap: the round-4 suite ratifies the defect.**
`test_other_unparsable_plan_is_ignored_once_without_holding`
(`tests:189-205`) asserts `decide(...).state == "LAUNCHING"` with a corrupt plan
file present. The suite is not silent about F2; it states F2 as the intended
behaviour. And `test_retired_v1_is_ignored_once_and_only_v2_plan_sets_span`
asserts `errors == []` (`tests:177`) against a `load_plans` that can no longer
populate `errors` at all.

Structural cause, one sentence: **the tests are a restatement of the
implementation rather than an independent statement of the contract**, and the
artifacts that *do* state the contract independently — the cold ruling, the
plan schema in `night_gate.py`, the installer's own gate at
`install_night_agent.sh:51-72` — are never executed against the watchdog. One
author held all three roles (code, fixture, oracle) in one commit, so the round
could not fail.

---

## Q2 — One production-shaped integration test, plus the fixture clause

### The test

New module `tests/test_magistrate_watchdog_cli.py`, modelled on
`tests/test_install_night_agent.py:97-118` (the pattern already in the repo).

**Fixture construction.** A temp `custody_parent/` with four sibling roots, so
the watchdog's own glob (`scripts/magistrate_watchdog.py:223`,
`self.root.parent.glob("*/night_plan.json")`) sees all of them beside the
custody root `custody_parent/magistrate/`:

| root | contents | produced by |
|---|---|---|
| `valid-v2/` | active v2 plan, `t0 = now + 60`, `window_max_s = 600`, `measurement_root` = a real temp git repo, `measurement_head` = its real `rev-parse HEAD` | the production writer (see clause) |
| `retired-v1/` | a v1 mapping | the frozen golden `tests/fixtures/night_plan_v1_retired.json` — never typed into a test body |
| `torn/` | the valid plan's bytes truncated to 40 % | `_truncate(path, 0.4)` applied to a written valid plan |
| `missing-field/` | the valid plan minus `measurement_head` | `_mutate(path, drop="measurement_head")` applied to a written valid plan |

**Invocation.** A real subprocess of the real script:

```
subprocess.run([sys.executable, str(REPO / "scripts/magistrate_watchdog.py"),
                "tick", "--custody-root", str(custody_parent / "magistrate")],
               env=env, capture_output=True, text=True, check=False)
```

with `env` supplying `MAGISTRATE_SESSION_BIN` → a stub binary and a `PATH` whose
`git` stub answers `ls-remote` deterministically (no `ops/stop*` ref, positive
control present) so the remote probe cannot mask later limbs — the round-4
audit's own V5 reached only `NETWORK_UNCERTAIN` under a network-denied sandbox,
which hides everything downstream of `:911-917`.

**Run the hold cases WITHOUT `--dry-run`.** Dry-run suppresses exactly the
writes (`Storage:227-292`) whose absence was F1's signature, and a hold never
forks (`tick` returns at `:1541-1542` before `os.fork()` at `:1543` when neither
`launch` nor `adopt` is set). So the hold cases exercise the real filesystem
path safely; only the launch-shaped positive control needs `--dry-run`.

**Assertions.**

1. *(kills F1, and every future required-field addition to `Probes`)*
   `returncode == 0`, `"Traceback" not in stderr`, and
   `custody_parent/magistrate/state.json` exists and parses. Today this fails
   exactly as the audit's V2 observed: `TypeError: Probes.__init__() missing 1
   required positional argument: 'measurement_head'`, `state.json` absent.
2. *(kills B-1)* With `retired-v1/` present, `events.jsonl` contains exactly one
   `plan_retired_v1` event naming that root, and the decision is **not**
   `HOLD_UNSAFE` for a v1 parse reason — the retired residue does not hold the
   tick.
3. *(kills F2)* With `torn/` and `missing-field/` present and no active plan,
   the decision is `HOLD_UNSAFE`, its reason names **both** plan paths,
   `launch` is false, and no `attempts/` directory is created.
4. *(positive control, so the test cannot pass by holding for the wrong reason)*
   With only `valid-v2/` present and its span active, the decision is in
   `{FENCED, HOLD_CENSUS}` — never `LAUNCHING`, never `HOLD_UNSAFE` — and
   stderr carries no traceback.

Note on assertion 4: the census argv is the absolute
`/usr/bin/pgrep -lf codex|claude|t3` (`joulewise/night_gate.py:34`), so a `PATH`
stub cannot intercept it and a test run from inside a Claude session will
legitimately observe a non-empty census. Admitting `HOLD_CENSUS` alongside
`FENCED` is what keeps the test honest rather than flaky; the discrimination
that matters (it is not `LAUNCHING` and not `HOLD_UNSAFE`) survives either way.

Why one test covers all three defects: B-1, F1 and F2 are the same question —
*what does the real process do when it reads a real custody directory* — and
all three were invisible for the same reason, that every existing test calls
`decide`/`tick` in-process with `Harness.deps`. The test's job is precisely to
execute `real_dependencies()` (`:430-440`).

### Contract clauses

> **C-A (fixture provenance).** No test may construct a night-plan mapping
> literally. Every plan a test writes to disk is produced by the single
> production writer, `joulewise.night_gate.write_night_plan()` — which does not
> exist yet and must be added; the repo today has only a reader,
> `NightPlan.from_mapping` (`joulewise/night_gate.py:186-280`), which is why the
> schema exists as four hand-maintained copies. A test needing an invalid plan
> writes a valid one and names its mutation (`_mutate(drop=…)`,
> `_truncate(…)`), so invalidity is defined as a delta from the production
> shape. The one exception is a *foreign* schema (retired v1), which lives as a
> frozen golden file under `tests/fixtures/`, never as schema text in a test
> body.

> **C-B (single production constructor).** Each production dependency bundle has
> exactly one constructor. `scripts.run_night.make_probes` (`:267-290`) is the
> only `Probes` construction in the repo; `production_census` imports it rather
> than re-declaring one (`scripts/magistrate_watchdog.py:334-342` is deleted).
> Structurally better still: `agent_census` (`joulewise/night_gate.py:418`)
> consumes only `probes.run`, so it should accept a narrow `CensusProbes`
> protocol — a census caller must not be broken by a field added for the plan
> pin. That narrowing is the cure for the *class*; importing `make_probes` is
> the cure for this instance.

> **C-C (wiring coverage).** Every production constructor —
> `real_dependencies`, `production_census`, `real_spawn`, `version_probe`,
> `remote_stop_probe` — is executed by at least one test, with the
> machine-touching leaves stubbed at the process boundary (`PATH`, env, argv),
> never by substituting the constructor itself. This is mechanically checkable
> and it is the clause that makes F1 unrepeatable.

---

## Q3 — D-161 classification of the four plan conditions

First, what a night plan **is**, because the classification follows entirely
from it. A night plan is the pre-registered statement, authored and frozen
*before* a measurement window, of what will be measured, with which code
(`repo_head`, `measurement_root` + `measurement_head`), when (`t0_epoch_s`,
`window_max_s`), and under what receipt class. Two different consumers read it:
`run_night`/`night_gate` treat it as the evidence anchor; the **watchdog** reads
it only as a *fence* — "a window is armed in this span, so no interactive agent
may be alive." The watchdog's two failure directions are asymmetric:

- fail **open** → an agent runs inside a real measurement window → the window's
  physics is contaminated and the evidence is irrecoverable;
- fail **closed** → `HOLD_UNSAFE` → the magistrate does not relaunch, the loop
  stalls, and with Ed away it stalls for a week. Costly, announced, and fully
  recoverable by one operator action.

D-161 removes fail-closed refusals whose only trigger is a hostile operator, and
keeps them for physics, evidence, and pre-registration. A plan we cannot read is
not an adversary scenario at all — it is a torn write or a corrupt byte — and
what it endangers is precisely physics/evidence. So the D-161 question is
narrow: **can this condition possibly designate an active window?**

| condition | verdict | reasoning |
|---|---|---|
| retired v1 plan | **IGNORE** (log once, proceed) | The identification is *affirmative*: the mapping decodes and says `schema == "joulewise.night_plan.v1"` (`scripts/magistrate_watchdog.py:541-543`). By ruling, no v1 plan can arm anything — the installer refuses it before rendering any plist (`scripts/install_night_agent.sh:51-72`, exercised end-to-end at `tests/test_install_night_agent.py:192-201`). A v1 file is therefore residue, not pre-registration: it designates no window that any component will honour. Refusing to launch over it is an operator-hygiene refusal of exactly the kind D-161 prunes. **Condition:** the ignore is transitional. Synthesis Q4 already requires the two real v1 roots to be moved to `~/night-custody/retired-v1/` before install, which takes them out of the glob (`:223`) entirely. So a `plan_retired_v1` event appearing *after* handoff is itself an anomaly and should raise a notice, not be silently absorbed. |
| unreadable JSON (I/O error, truncated, `{not-json`) | **HOLD** | The schema is unknown, so the file *cannot be identified as retired*. The unknown set includes "a v2 plan for a window that starts in ten minutes, caught mid-write." Choosing IGNORE here is choosing to launch into a window we declined to read. Not adversarial, not operator-only: torn writes and corruption are ordinary. Recovery is one file. **Refinement that keeps the hands-free property:** hold and re-read on the next tick rather than latching. A torn write resolves within a tick; genuine corruption persists and the hold escalates with a notice. Never auto-ignore. |
| v2 missing required fields | **HOLD** — the strongest case of the four | The file *declares itself a current plan*. That is positive evidence that an author intended to arm a window; only the bounds are unreadable. Treating a self-declared current plan as absent is the fail-open in its purest form (the audit's executed counterfactual: `{"schema":"joulewise.night_plan.v2","plan_id":"armed-v2","t0_epoch_s":0}` → `decision=LAUNCHING, launch=true`). Second reason: the installer already refuses this shape (`install_night_agent.sh:51-72` → exit 3 `night_plan_malformed`), so an invalid v2 sitting in custody means either a half-completed arm or a **mutation after install** — and the latter is an evidence-integrity event, squarely inside D-161's fail-closed fence. |
| v2 with future authorship | **HOLD**, reason `night_plan_malformed` | Future `authored_epoch_s` means two clocks disagree: the author's or this machine's. A window's `t0` and duration *are* its time anchor, and the project has already paid for a time-anchor defect once (D-078 voided whole corpora). The watchdog owns a clock-uncertainty state for exactly this class (`clock_uncertain`, `decide:889-891`); future authorship belongs to it, not to the launch path. Note the current live behaviour: future authorship is checked by the gate and the installer, **not** by `from_mapping`, so such a plan parses and the watchdog fences on its span. The direction is safe today by accident; the reason is never reported, and it inverts the moment anyone adds "ignore stale plans." |

> **C-D (the ignore rule).** Only a mapping *positively identified* as
> `joulewise.night_plan.v1` may be ignored. Every other read, decode, or
> validation failure at a plan path is `HOLD_UNSAFE`, named per path, re-read
> every tick, never latched. An ignore must be derived from a positive
> identification, never from the absence of a successful parse.

**Disagreement with the magistrate, stated plainly.** The synthesis cure for
B-1 reads "retired-v1 plans are recorded once as `plan_retired_v1` and IGNORED
by the fence (never a hold)." Round 4 implemented that faithfully — and then
generalised it to every parse failure, because the implementation's natural
shape is `try/except Exception` (`:534-552`). The generalisation is where the
blocker came from. The cure text should have been written as a *positive
identification* rule from the start; "ignore v1" and "ignore what fails to
parse" are one keystroke apart in code and opposite in contract. I would amend
the cure table entry rather than only patching `load_plans`.

---

## Q4 — Handoff kill-list provenance and the race-safe protocol

**Is ancestry from the recorded interactive-twin pid sufficient? No — it is
necessary but structurally incapable of covering the case the kill list exists
for.** The whole reason for a handoff kill list is the orphans: the cold ruling
observed `4394 claude --bg-pty-host` at ppid 1 and five `codex-run-v3` trees at
ppid 1 (file 19, E10; M-2/M-3). Once a process is reparented to init, the
ancestry evidence has been *destroyed by the operating system*. So ancestry
under-covers by construction.

Round 4 responded by over-covering: it unions in every ppid-1 lookalike on the
machine (`scripts/magistrate_watchdog.py:711-722` — `_is_bg_pty_host` or a
`/.claude/shell-snapshots/` substring), which is provenance-free. That is F3,
and it violates the ruling's condition literally, independent of how unlikely a
second concurrent session is. **Neither ancestry alone nor ancestry ∪ lookalikes
is the answer.**

**The right shape: provenance from an artifact only this magistrate could have
written, never inferred from the process table.** Ranked:

1. **Socket/argv identity.** The bg-pty-host and bg-spare commands carry socket
   paths in argv (visible in the round-4 fixture at
   `tests/test_magistrate_watchdog.py:665-671`: `/tmp/spare.pty.sock`,
   `/tmp/orphan.sock`). If the real argv's socket path lies under a directory
   this session owns, that is genuine provenance. I have **not** verified the
   real argv shape this session — the magistrate must confirm it with one `ps`
   line at the bench before this is relied on.
2. **Open-file / cwd ownership.** `lsof -p <pid>` showing a file under this
   session's own transcript directory, or the session id present in argv.
3. **Explicit operator adjudication** — the clause I recommend adopting now,
   with 1 and 2 as later upgrades:

> **C-E (kill-list provenance).** `handoff-inventory` emits **two** lists:
> `owned` — the ancestry-closed descendants of the interactive root, provenance
> = ancestry — and `unclassified_candidates` — ppid-1 lookalikes, provenance =
> none. The reaper signals `owned` only. A candidate is promoted to `owned`
> exclusively by an explicit second invocation naming it and its start-time
> (`--adopt-pid 4394 --start "<lstart>" --reason "…"`), recorded verbatim in the
> handoff file. Automatic promotion is permitted only on verified socket/argv
> or open-file provenance (1 or 2 above), never on a name pattern.

This satisfies the ruling's "never lists a pid it did not classify as
magistrate-tree" literally, keeps the hands-free path safe, and puts a human or
the cold gate on the one irreversible act in the whole procedure.

**Minimal race-safe protocol.** The current documented reaper
(`docs/process/MAGISTRATE_WATCHDOG.md:145-172`) is close but wrong in three
places.

1. **Identity is the pair `(pid, start_time)`, never the pid.** `start_time` is
   the `ps -axo lstart` token already captured by `RealProcessTable`
   (`scripts/magistrate_watchdog.py:161-190`). Stated limit: `lstart` has
   one-second granularity, so two processes sharing a pid within the same second
   are indistinguishable. Accept and record that; it is far below the risk being
   removed.
2. **Freeze the list at inventory time; write it to the handoff file with
   `(pid, ppid, start_time, command)` plus wall and monotonic timestamps.** Never
   re-derive the target set later — the frozen list bounds what may be killed;
   the census bounds what may exist. Those are different guarantees and both are
   needed.
3. **Re-validate immediately before *each* signal, not once for the batch.**
   Today the reaper snapshots once and then TERMs the whole list
   (`MAGISTRATE_WATCHDOG.md:145-157`), leaving a reuse window per pid. For each
   pid, re-snapshot and signal only if `observed[pid].start_time ==
   recorded[pid].start_time`.
4. **Distinguish absent from changed.** A recorded pid that is *gone* is a
   success (`already_gone`); a recorded pid whose start-time *changed* is pid
   reuse — skip it, record `reused_skipped`, continue. The current doc collapses
   both into `raise SystemExit(f"handoff PID/start mismatch before TERM: …")`
   (`:149`), so one background process exiting normally between inventory and
   reaper aborts the entire handoff, and no retry path is documented. See AD-8.
5. **Order: every non-root pid first, the interactive root last** — the doc
   already does this (`:154`) and it is correct, since killing the root first
   orphans the remainder out of reach.
6. **Re-snapshot after TERM, KILL only matching survivors, then re-snapshot
   again.** *Any recorded `(pid, start_time)` still present after KILL is a
   FAILURE*, whatever the census says. Today the exit status keys on the census
   alone (`:172`, `SystemExit(0 if census.empty else 4)`), and the census is a
   `pgrep` pattern (`joulewise/night_gate.py:34`) that a recorded non-agent
   descendant will not match. Survivor check AND census — never census instead.
7. **One verification receipt**: recorded list, per-pid outcome
   (`already_gone` / `termed` / `killed` / `reused_skipped` / `survivor`), final
   census, verdict. The doc's log currently ends with a `CensusObservation`
   repr, which cannot express per-pid outcomes.

---

## Q5 — Rendering the checkout fence from the armed plan

**Yes, generate it at spawn time.** The prompt is already a template the
watchdog renders per launch: `@@LAUNCH_ISO@@`, `@@ACTIVATION_ID@@`,
`@@CUSTODY_ROOT@@`, `@@NOTICE_PENDING@@`
(`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:1-6`). The mechanism exists at zero
marginal cost. Meanwhile schema v2 explicitly accepts *any* absolute
`measurement_root` (`joulewise/night_gate.py:238-245`) while line 10 of the
prompt names one literal path. A literal path in a rendered template is a **pin
with no pinner**: nothing verifies it still matches the armed plan, and a reader
— including the relaunched session itself, which has no other source for this —
will treat the sentence as complete. Static text that claims to fence a dynamic
value is worse than no text.

**The rule.** Render `@@FENCED_CHECKOUTS@@` as the sorted union of
`{CANONICAL_REPO}` (`scripts/magistrate_watchdog.py:52`) and
`{plan.measurement_root}` over every plan the glob returned that is **armed** —
authored and not yet completed — not merely those whose span is *active*. The
distinction is load-bearing and the current code does not draw it: `decide`
computes `active_plans` (`:908`) for the fence, but the prompt's own rule at
line 10 forbids moving the checkout after *arming*, and a plan armed for tonight
is not in span at 14:00. Fencing only active plans would leave the armed
checkout unfenced for the hours when it is most likely to be moved. If the armed
set is empty, render the canonical repo alone plus an explicit "no measurement
checkout is armed" line — never a leftover literal.

**If two armed plans disagree.** Fence **both** — prohibitions compose safely,
so the union is always the right *fence*. But disagreement is itself a
launch-blocking signal, and the fence must not be used to paper over it:

- overlapping spans with different `measurement_root` → `HOLD_UNSAFE`
  (`plan_conflict`) + notice. Two windows pre-registered against different code
  for the same time is a pre-registration integrity fault: no single night can
  satisfy both, and nothing records which was intended. D-161 fail-closed.
- same `measurement_root`, different `measurement_head`, any spans →
  `HOLD_UNSAFE`. One checkout cannot be at two heads; moving it to satisfy one
  plan voids the other by the gate's own head check
  (`joulewise/night_gate.py:633-645`). At most one is satisfiable and we cannot
  tell which.
- non-overlapping spans, different roots → not a conflict. Fence both, launch
  permitted, the prompt lists both.

The watchdog performs **none** of these checks today: `active_plans` is used
only to pick `min(..., key=t0_epoch_s)` for the stand-down phase (`:919-921`), so
a second, contradictory plan is silently discarded. See AD-11.

---

## Additional defects

Defects in `4a23c119..HEAD` (or exposed by it) that the round-4 delta re-audit
did not name. AD-1, AD-2, AD-3, AD-7, AD-9 and AD-12 I would treat as
should-fix-before-packet-21; the rest as recorded nits.

**AD-1 — duplicated production `Probes` constructor is the root cause of the F1
*class*, and "add the missing kwarg" does not fix it.**
`scripts/magistrate_watchdog.py:334-342` re-declares a bundle that
`scripts/run_night.py:267-290` already builds, in a module that already imports
from `scripts.run_night` (`:44-48`). The placeholder
`checkout_head=lambda: "unused-by-agent-census"` (`:339`) shows the aggregate is
wrong for this caller: `agent_census` (`joulewise/night_gate.py:418`) needs only
`probes.run`. Cure: import `make_probes`, and narrow the census dependency to a
`CensusProbes` protocol so a field added for the plan pin cannot break a
census-only caller. (Clause C-B.)

**AD-2 — a fail-closed limb that can no longer fire.** `load_plans` still
returns `errors` (`:530-552`) but nothing appends to it after round 4, so the
hold at `decide:892-894` (`if plan_errors: return Decision("HOLD_UNSAFE", …)`)
is dead code, and `tests:177` asserts `errors == []`, pinning the deadness. A
dead fail-closed limb is worse than an absent one: a reviewer reads it as
protection. Either repopulate it (per clause C-D) or delete it — never leave it.

**AD-3 — the ignore-suppression key is the plan's parent directory, forever.**
`record_ignored_plan` keys on `str(path.parent.resolve())` (`:512-514`) and
`recorded_ignored_plan_roots` replays `events.jsonl` treating `plan_retired_v1`
and `plan_unparsable` as interchangeable suppressors (`:480-508`). So (i) a root
first recorded for one reason never emits an event for a *different, later*
failure — a v1 root re-authored as a broken v2 is silently absorbed, and the
operator sees only the stale first classification; (ii) suppression is permanent
across restarts and across nights, with no re-notification ever. Key on
`(root, kind, digest(detail))` and re-emit at least once per activation.

**AD-4 — field-name collision in the event stream.** The ignored-plan event's
`custody_root` (`:517`) is the *directory containing the plan file*, while
`custody_root` everywhere else is the plan's own declared field
(`joulewise/night_gate.py:256`, `NightPlan.custody_root`). Two meanings, one key,
one journal. Rename to `plan_dir`, or emit both.

**AD-5 — `decide` now writes to the durable journal as a side effect of
reading.** `load_plans` → `record_ignored_plan` → `append_jsonl`
(`:516-528`) executes inside a function whose other limbs are pure. Under
`--dry-run` the write is suppressed by `Storage` (`:238`) but
`storage.ignored_plan_roots_seen` is still mutated (`:527`), so a dry-run and a
real tick in the same process disagree. Harmless today (one tick per `main`);
a hazard as soon as the run loop ticks twice in-process.

**AD-6 — three different notions of "a usable plan."** The watchdog applies only
`NightPlan.from_mapping` (`:534-535`); the installer additionally applies the
36-hour age limb and the future-authorship limb
(`scripts/install_night_agent.sh:51-72`); the gate applies its own
(`joulewise/night_gate.py:612-617`). The watchdog therefore *accepts plans the
gate refuses*. The divergence errs safe today (it fences on plans nobody will
run) but it is unaudited, undocumented, and inverts the moment anyone adds
"ignore stale plans." State the intended relation — watchdog ⊇ gate — and test
it.

**AD-7 — the "Terminal-hosted interactive magistrate" guard checks nothing of
the kind.** `_is_interactive_claude` (`:654-663`) classifies by command string,
excluding only `{daemon, bg-pty-host, --bg-pty-host, bg-spare, --bg-spare}`. A
headless `claude -p` session — which is exactly what this watchdog spawns
(`SESSION_ARGV_AFTER_PROMPT`, `:78-84`) — classifies as **interactive**. So
`handoff-inventory` invoked from inside a watchdog-spawned magistrate would
accept that session as the twin and nominate its own tree for the kill list. The
error string at `:707-709` asserts an invariant nothing tests: there is no tty
check, no session-leader check. Add a positive check (isatty on the ancestor, or
the absence of `-p`/`--print` in its argv), or require the operator to pass the
expected pid explicitly.

**AD-8 — the reaper's pre-TERM check aborts on benign exits.**
`changed = {pid: (start, observed.get(pid)) for … if observed.get(pid) != start}`
then `raise SystemExit(…)` (`docs/process/MAGISTRATE_WATCHDOG.md:146-149`) treats
*absent* and *start-time-changed* identically. With ~10 recorded processes, one
of them exiting normally between inventory and reaper aborts the whole handoff,
and the doc provides no retry path — leaving the magistrate having already
stopped its background tasks (step 1) with no completed install. Absent =
success; changed = reuse, skip. (Q4 item 4.)

**AD-9 — the handoff kills the twin 15 seconds after TERM, against the
contract's own 9-minute drain.** `time.sleep(15)`
(`docs/process/MAGISTRATE_WATCHDOG.md:157`) applies to the interactive root as
well, while the same system's cooperative ladder is `STOP_COOPERATIVE_S = 9*60`
(`scripts/magistrate_watchdog.py:71`) and the relaunch prompt *promises* the
session it may "exit within nine minutes of the request"
(`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:17`), a window whose stated purpose
is committing and pushing work (`:16`). The handoff therefore kills a magistrate
that is, by its own contract, still allowed to be making work durable. Either
issue a cooperative `standdown.request` first and wait the contracted grace, or
state in the doc why the twin is exempt (e.g. step 1 already drained it) — the
current silence reads as an oversight, and on the evidence it is one.

**AD-10 — the reaper imports `production_census` from whatever checkout happens
to be cwd.** The heredoc runs `/usr/bin/python3 - "$handoff_file"`
(`docs/process/MAGISTRATE_WATCHDOG.md:141`) and does
`from scripts.magistrate_watchdog import production_census` (`:150`), so
resolution is via `sys.path[0] == ''`, i.e. the cwd, which the procedure never
pins — in a step sequence that explicitly directs installation *from the
measurement checkout*, making cwd ambiguous between two checkouts at different
revisions. The census that certifies the handoff could be a different revision
from the watchdog that was installed. Pin an absolute path or `PYTHONPATH`.
(`night_gate` is stdlib-only — `joulewise/night_gate.py:8-17` — so system
`python3` is otherwise fine.)

**AD-11 — no conflict detection across armed plans.** `active_plans`
(`:908`) feeds only `min(…, key=t0_epoch_s)` for the stand-down phase
(`:919-921`). Two plans with overlapping spans, or one `measurement_root` at two
`measurement_head`s, coexist silently and one is arbitrarily chosen. (Q5.)

**AD-12 — the new tests encode two defects as intended behaviour.**
`test_other_unparsable_plan_is_ignored_once_without_holding` (`tests:189-205`)
asserts `LAUNCHING` with a corrupt plan present; `tests:177` asserts the dead
`errors == []`. Any F2 regression must **replace** these assertions, not sit
beside them — otherwise the next round produces a suite that is green in both
directions at once.

**AD-13 (nit) — doc tests assert string counts.**
`test_documented_example_plans_are_v2` (`tests:769-778`) asserts
`text.count('"measurement_head"') == 2`. It fails when someone adds a third
correct example and passes for a doc that is wrong in every other respect. Parse
the fenced JSON blocks and validate them through `NightPlan.from_mapping`
instead — which also brings the doc examples under clause C-A.
