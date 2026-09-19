# Record 13 — Opus counter-review (gate-ledger row 6), lane QUIET-PREDICATE-EVIDENCE-01 harness PR

Read-only, worktree `JouleWise-wt-reaudit3-d0b83820` @ `d74b1be5` (branch head, rebased on main `2f79e633`).
Diff under review: `git diff 2f79e633 d74b1be5` = `scripts/sample_quiet_predicate_evidence.py` (new, 1152 lines) +
`tests/test_sample_quiet_predicate_evidence.py` (new, 845 lines, 45 tests). Module run once: **45 tests, OK, 5.028 s**.

## Verdict: MERGE-WITH-FIXES

**0 blockers, 7 should_fix, 3 nits.** No finding overstates a *measured quantity* in a published row: PROVISIONAL is
hard-coded, reasoned nulls hold everywhere `assert_null_reasons` reaches, and the census grouping keeps true/false/unknown
apart. The defects are (a) refusals that never reach a caller-visible channel, (b) one surviving starvation-fragile
assertion of exactly the signature the cold gate deleted once, (c) a summary that pools across boots, and (d) dead code.
All ten are in-file and small; one fix round, then a delta re-audit of the round, then merge.

## Findings

### S1 (should_fix) — `load()` swallows every cleanup escalation; exit 0 after a force-killed or surviving worker
`scripts/…:928-943`. The `finally` ladder joins .5 s → `terminate()` → `kill()` and records
`{"pid","exitcode","alive"}` in `report["cleanup"]`, but **nothing folds that into `report["error"]`**, and
`main` returns `int(load(args)["error"] is not None)` (`:1143`). A worker that had to be SIGTERMed, SIGKILLed, or that is
still `alive` after both joins yields `error: null` and process exit 0. `production_round` does the opposite for the same
hazard (`:433-436`, residue ⇒ status error), so this is an inconsistency inside one file.
*Counterfactual (executed, probe_c.py):* child delivers its result then takes 1 s to exit ⇒
`cleanup row: {'exitcode': -15, 'alive': False}`, `report["error"]` untouched.
*Fix:* `if any(c["alive"] or c["exitcode"] not in (0,) for c in report["cleanup"]): report["error"] = (…)`.

### S2 (should_fix) — the real-load test still has one assertion a correct worker can fail under starvation (Q3, part 1)
`tests/…:676` `self.assertEqual(child["exitcode"], 0)`, keyed to the 0.5 s first join at `scripts/…:932`. After the parent
has received the result, a correct worker is in `connection.close()` + interpreter shutdown; on a loaded machine that can
exceed 0.5 s, at which point `load()` SIGTERMs it and the exitcode becomes `-15`.
*Counterfactual (executed, probe_c.py):* the identical join/terminate/kill ladder against a child that finishes its work
and then needs 1.0 s to exit → `tests:676 assertEqual(exitcode, 0) would: FAIL`. Nothing the worker did was wrong.
This is the same signature ("assertion keyed to a quantity starvation destroys") that ruling 10 removed for the delivery
floor; it survived because the round-3 brief touched only the floor line.
*Fix:* raise the first join grace to the file's own 5 s convention (`stop_process` `grace_s=5` `:448`;
`production_round` `cleanup_deadline = +5` `:424`), and let S1's `report["error"]` carry the escalation so the test's
existing `assertIsNone(report["error"])` (`:652`) does the work.
Everything else in that test is starvation-safe: `fraction <= .14` (`:661`), the per-period ceiling (`:663`) and
`charged_s >= claimed_s - .01` (`:669`) all relax as the scheduler hands out less.

### S3 (should_fix) — `collect` returns exit 0 when every round errored
`scripts/…:654-700`, `:1140-1141`. `production_round` catches its own exceptions and returns `status:"error"` (`:396`);
`collect` copies that into the row but never into `session["error"]`, and `:697` breaks only on `partial` or a session
error — so an error round neither stops the loop nor fails the process.
*Counterfactual (executed, probe_a.py part B):* a round runner returning `status:"error"` five times →
`statuses: ['error']×5`, `session error: None`, `exit code would be: 0`. A `collect && summarize` chain proceeds on
zero usable rounds. (The rows themselves stay honest, which is why this is not a blocker.)

### S4 (should_fix) — `summary.json` emits reason strings that contradict their non-null siblings
`scripts/…:1032-1033` and `:1039-1040` put `reference_reason` and `alignment_model_reason` in the dict unconditionally.
The file's own contract is `reasons()`'s docstring (`:83`): a `<field>_reason` exists because the field is null — and
`collect` honours it by popping the reason when the value resolves (`:737-738`).
*Counterfactual (executed, probe_a.py part A):* a single-session, single-census-condition directory gives
`reference is None? False` beside `reference_reason: "reference absent or spans census conditions…"`, and a resolved
`alignment_model` beside `alignment_model_reason: "models differ across sessions…"`. A downstream reader that trusts the
reason field discards good evidence.
*Fix:* mirror `:737-738` — pop both reasons when the sibling is not None.

### S5 (should_fix) — `summarize` pools rows across boots/OS builds into one mean and one Δ
Group key is `(state, repeat, census_clean)` only (`scripts/…:1006-1008`); `boot_id` is written into every row
(`:673`) but is neither a key nor an emitted group field, and `session_provenance` carries only the four keys at
`:1026-1028`. Given D-078 / the 25G83 acceptance-epoch invalidation, silently averaging across a reboot or an OS update
is the project's own known-bad pattern.
*Counterfactual (executed, probe_d.py):* two `idle` rows, same repeat and census condition, `boot-A-macOS-25G80` at 1 W and
`boot-B-macOS-25G83` at 9 W → `1 group`, `pooled cpu_w 5.0`, `group keys mentioning boot: []`. Nothing in `summary.json`
tells the reader the mean straddles two boots.
*Fix:* add `boot_id` to the group key, or emit `boot_ids: sorted({r["boot_id"] …})` per group (minimum) .

### S6 (should_fix) — the QoS class is unverified; a constant swap survives all 45 tests (Q3, part 2)
`scripts/…:855` `code = 0x09 if qos == "background" else 0x19`. No test observes the applied class: the only fake-clock
worker test stubs the function out (`tests/…:619`), and the real-load test passes `--qos user-initiated` but never reads
the class back. A `0x09 ↔ 0x19` swap therefore kills no assertion and is outside the seven-mutation set (cores,
alignment, observer, clock, catchup-capped, burn-noop, window-skip), while `report["qos"]` (`:891`) labels every load
evidence file with a QoS the workers did not run at — the one thing the `load` subcommand exists to control.
*Executed:* readback is available and works —
`pthread_get_qos_class_np(pthread_self(), …)` from `/usr/lib/libSystem.B.dylib` returned class `0x11`, then `0x9` after
`pthread_set_qos_class_self_np(0x09, 0)`. (`pthread_get_qos_class_self_np` is not an exported symbol; use the `_np`
variant taking `pthread_self()`.)
*Fix:* one darwin-only test asserting `set_qos("background")` ⇒ `0x09` and `set_qos("user-initiated")` ⇒ `0x19`.

### S7 (should_fix) — `stop_process` is dead code, and its docstring misattributes the recorder's termination
`scripts/…:448-460` has **no production call site** (grep: only `tests/…:513` and `:522`). Its docstring — "TERM the sudo
supervisor (which forwards it), then KILL after grace" — describes work `PowerRecorder` actually does itself in
`request_stop`/`force_stop`/`finish` (`:508-552`), deliberately without `wait()` inside the observer bracket. Two of the
45 tests exist only to exercise the orphan, inflating the count the gate reads.
*Fix:* delete the function and `tests/…:509-523` (43 tests), or call it from `PowerRecorder.finish` — not both states.

### N1 (nit) — stale comment: there is no floor any more
`tests/…:19`: "…the floor is sized to the instrument, not to delivery." Round 3 deleted the delivery floor;
`STARTUP_CPU_S` is now used at exactly one site, `:671`, as headroom on a *ceiling*. Reword to say so.

### N2 (nit) — inconsistent robustness in `aggregate`
`scripts/…:978` indexes `r["observation"]["metrics"]["busy_cores"]` directly while `:967-968` uses `.get` chains for the
same data. A hand-edited or foreign `rounds.jsonl` gives an uncaught `KeyError` traceback instead of the `ValueError`
refusal path `main` handles (`:1146`).

### N3 (nit) — pipe fd leak if `Process.start()` raises
`scripts/…:896-904`: `children.append`/`connections.append` happen *after* `start()`, so a failed launch leaves both ends
of that `Pipe()` unregistered and unclosed by the `finally` (`:939-940`). No worker outlives `load()` on this path.

## Answers to the five questions

1. **Overstatement / swallowed refusals:** none in a published measured field. `census_clean` is sound — `True` requires
   every completed census clean *and* no census errors (`:564-573`), and the "sampler census alone infers clean" hazard the
   `summarize` comment warns about (`:993-994`) is unreachable, because `smoke_observation_round` starts `census-1` on its
   first loop iteration (`scripts/run_night.py:2637-2640`), long before any observation exists, so every round contributes
   either a census result or a `census_errors` entry. PROVISIONAL is hard-coded conservatively (`:1038`); the empty-directory
   summary is reasoned-null (`status:"no_rounds"`, test `:772`). The real defects are refusals that never reach the exit
   code (**S1**, **S3**) and reason strings that lie in the *understating* direction (**S4**), plus comparability pooling (**S5**).
2. **`load` cleanup/reaping:** the pre-launch share guard is sound — `count = max(1, ceil(cores))`,
   `share = cores/count ≤ 1` per worker, host-logical-CPU refusal before any spawn (`:885-887`), and the log-exists
   refusal before that (`:882`). Every started child is appended immediately and the `finally` ladder reaches all of them
   on every error path, including an exception mid-`send(start)` or mid-`recv` and KeyboardInterrupt (caught at `:928`).
   A worker can outlive `load()` only if `kill()` + `join(1)` both time out — possible, and **silently recorded** (S1). N3
   is the one unclean error path.
3. **Tests:** yes, one starvation-fragile assertion remains — **S2**, executed. Under-asserted and outside the mutation
   set: **S6** (QoS constants). Also unasserted but lower value: `report["stationarity"]` from the real `load` run (`:927`)
   is never checked by the real-load test, though `stationarity` itself has three direct tests.
4. **Prune:** **S7** (dead `stop_process` + its two tests), **N1** (comment lies), **N2**, **S4**. All 20 imports are
   used; the docstring's line citations resolve (`run_night.py:2603-2712` ✓, `quiet_admission.py:231-278` ✓,
   `powermetrics.py:1775-1785` / `2009-2025` ✓). Nothing else reads as overbuilt.
5. **Verdict:** MERGE-WITH-FIXES, above.

## Commands run

```
git log/status/diff --stat 2f79e633 d74b1be5
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp .venv/bin/python -B -m unittest tests.test_sample_quiet_predicate_evidence   # 45 OK, 5.028 s
python -B /tmp/magistrate-d0b83820/opus-counter-232/probe_a.py   # S4 (part A), S3 (part B)
python -B /tmp/magistrate-d0b83820/opus-counter-232/probe_c.py   # S1, S2 (slow-exit child through load()'s ladder)
python -B /tmp/magistrate-d0b83820/opus-counter-232/probe_d.py   # S5 (cross-boot pooling)
python -B -c "<ctypes pthread_get_qos_class_np readback>"        # S6 feasibility
grep/sed over scripts/sample_quiet_predicate_evidence.py, tests/…, scripts/run_night.py, joulewise/quiet_admission.py
```

Probe sources are under `/tmp/magistrate-d0b83820/opus-counter-232/`. No repository file was modified; no sudo,
no powermetrics, no `collect --power`, nothing armed.
