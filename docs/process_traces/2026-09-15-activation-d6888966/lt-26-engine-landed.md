# lt-26 — The transactional engine landed `490be1a3`; refuters running

Written 13:52 PDT 2026-09-15 (clock read).

## What is on `feat/2026-09-15-install-windows-transactional`

| Sha | What |
|---|---|
| `8f334b8f` | T2: D9 operator docs |
| `e867dee9` | the three-valued stateful fake launchctl (the instrument) |
| `6dc86461` | the system-interpreter import guard (R5) |
| `490be1a3` | **the engine**: D1–D8/D10 |

Diff against `073a9763`: 7 files, +1795 / −749. The shell goes **387 → 81
lines** — argv parsing, the MIN_PYTHON check, and `exec`. The engine is 662
lines of stdlib-only Python that must stay 3.9-compatible.

## The acceptance numbers

- **MUST-DIE campaign: 31/31 RED, 0 survived.**
- **`class_1: NO`, `class_2: NO`** from the lt-21 audit script, adapted per R6 to read the clock after the last LAUNCHD mutation.
- `tests.test_night_agent_install` **31 OK**, `test_install_night_agent` **46 OK**, `test_magistrate_watchdog` 93 OK, `test_night_gate` 59 OK, `test_docs_freshness` 31 OK, `test_gen_state` 44 OK — all lead-re-run at the bench, not taken from the seat.
- The uninstall path executes under `/usr/bin/python3` **3.9.6** in a stripped environment, with invalid pins and a missing venv, twice.

## Three more rulings (R8, R9, R10) — the seat stopped three more times and was right three more times

**R8 — bind the module's working directory to the SCRIPT's repo.** `-m` prepends
the INVOCATION cwd to `sys.path`, which shadows `PYTHONPATH="$repo"`, so running
the installer from another checkout imported THAT checkout's `joulewise`; the
copied-driver preflight tests failed with a repo_head mismatch. Ruled: absolutise
`--plan` and `--render-only` first, then `cd "$repo"` before the exec. `-P` /
`PYTHONSAFEPATH` is not available — the uninstall path runs under 3.9.6, which
predates it. Both tests green after.

**R9 — `tests/test_run_night.py` is out of scope; its four failures stand.**
Three installer tests encode absence as **rc 1** — the exact pre-D2 reading this
redesign exists to abolish — and one asserts a shell `KeepAlive` grep the
reduction removed. The seat was forbidden to touch the file or to weaken D2 to
satisfy it. **This is the one open ask for the magistrate.**

**R10 — a closed stdout must not turn a committed install into a failure.** The
seat found that closing the real stdout reader after the final bootstrap reaches
SUCCESS internally — both labels loaded, both plists present — and then Python's
shutdown flush fails and sets the process status to **120**, while D6 requires 0.
D6 already puts `BrokenPipeError` in the success branch, so this was the
implementation failing to deliver the design, not a conflict with it. Ruled:
neutralise the shutdown flush (redirect fd 1 to `os.devnull` once a
`BrokenPipeError` is seen) so a committed install reports exit 0. Pinned:
rc 0, both labels LOADED, both plists present, sidecars removed.

The reasoning I want on the record, because it is the lane's whole disease in
miniature: the install genuinely committed, so **exit 0 is the TRUE report and
120 is a false failure signal.** Every defect in this lane's history has been a
false signal — a query error read as proof of absence, a "rolled back" message
printed over a job that was still loaded. Reporting failure for a success the
machine actually performed is the same illness pointing the other way. **Flagged
for the magistrate:** cold gate 28 recorded a SIGPIPE residual as a NIT against
the OLD shell, where the observable was rc 141; under the new engine that case
now exits 0. That is a deliberate behaviour change relative to the NIT.

## Scorecard for the seat's early returns

Eight `NEEDS_RULING` / `NEEDS_SCOPE` returns across T1a–T1h, **eight of them
correct**: three contradictions inside the adjudication (R1, R2, R4), two
unsatisfiable-as-written clauses (R5, R6), one real semantic defect the design
did not anticipate (R8), one scope boundary (R9), and one implementation gap
against the design (R10). Two of the eight were the SAME question asked twice
because I rebuilt the brief from the original instead of accumulating my own
rulings — my error, named in lt-25 and cured by the cumulative R1..R10 block.

**Not one guess.** On a lane where four previous rounds each shipped a plausible
wrong answer, a seat that refuses to proceed on an ambiguity is worth more than
a seat that is usually right.

## Refuters running

Contract (pid 45351) and execution (pid 45352), Astra xhigh, disposable detached
worktrees at `490be1a3`, baselines captured. Both briefs carry the two
acceptance predicates as the thing to break, the D2/D3/D5/D6 constructions as
the authority, and the four known `test_run_night` failures as excluded noise.
Both are told in terms that a clean verdict from a real attack is as valuable as
a finding.
