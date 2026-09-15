# lt-23 — Transactional installer: implementation lane launched

Written 11:59 PDT 2026-09-15 (clock read). Branch
`feat/2026-09-15-install-windows-transactional` from `073a9763`, worktree
`/Users/edr/code/JouleWise-wt-iw-txn`. `int/2026-09-15-install-windows` is
frozen at `073a9763` and I touch it no further.

## What the redesign consult settled

Adjudication `34-design-adjudication-transactional-installer.md` (magistrate,
11:56 PDT) on three blind seats — Astra xhigh (33a), Opus (33b), fresh Fable
(33c). **All three recommended (B), the rewrite.** D1–D10 are dictation.

The sentence that justifies the whole lane, and that I want on the record
because it is the honest verdict on my own four rounds:

> Four rounds did not fail on four bugs; they failed on one topology: invariants
> enforced by inspecting call sites, and the class reappearing one site further
> each time.

B replaces enumeration with three constructions: a **single mutation channel**
(three mutators, nothing else touches `launch_dir` or launchctl), a **commit
predicate that is the only road to exit 0**, and **deletion that requires an
absence proof** (`require_absent(label) → Absent`, a token that
`remove_plist`/`restore_prior` demand). The unsafe states become
unrepresentable rather than reviewed away.

The specific killer from delta 3 is answered by D2: the old code's
`print … >/dev/null 2>&1 &&` read **any** non-zero rc as "not loaded", so a
query that merely ERRORED (rc 9) was proof of absence and the plists were
deleted under a live job. D2 makes liveness three-valued — `LOADED` iff rc 0;
`ABSENT` iff rc 113 **and** stderr carries the exact
`Could not find service "<label>" in domain for user gui: <uid>` line; **everything
else is UNKNOWN, and unknown counts as loaded.** Both the bare `rc != 0 ⇒ absent`
and the bare `113 ⇒ absent` readings are explicitly rejected.

Two design consequences worth flagging forward: **there is no bootout on the
success path** (a prior LOADED job is a refusal, never something to unload and
"restore"), and **no TMPDIR directory exists anywhere in the design** — prior
bytes go to a `.prior` sidecar beside the plist, which deletes the F4 class and
the cold-gate-28-Q1b class by construction rather than by guard.

## Seats launched in parallel, both detached, 11:58:59

| Seat | Model | Sandbox | pid | WRITE_SCOPE |
|---|---|---|---|---|
| **T1** — engine, shell, tests | Astra **xhigh** | workspace-write | 89800 | `joulewise/night_agent_install.py`, `scripts/install_night_agent.sh`, `tests/test_night_agent_install.py`, `tests/test_install_night_agent.py` |
| **T2** — D9 operator docs | Astra high | workspace-write | 89801 | `docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`, `docs/process/NIGHT_COURIER_PROMPT.md` |

T1's brief (`/tmp/magistrate-d6888966/brief-15-T1.md`, 19 138 bytes) carries
**D1–D10 verbatim** — I extracted the adjudication's dictation section
programmatically rather than paraphrasing it, because paraphrase is how three of
my four dictation defects happened. On top of it: the three-valued stateful fake
launchctl with per-label fault directives that do not change loaded state and
mutators whose return code and effect are modelled INDEPENDENTLY; the PRODUCT
matrix with its 4-tuple assertion and the one shared fence assertion in every
cell; the FIX-1..10 / FIX-A mapping table; the `control_…` rename; the full
must-die set; and the lt-21 `reproduce.py` re-run expecting **class_1: NO** and
**class_2: NO** under D10's class-1 reading. T2's brief is D9 exactly, with §3
declared untouchable and the verbatim refusal-string list.

## The interpreter landmine I added to T1's brief

`/usr/bin/python3` on this machine is **3.9.6** (bench-verified 11:57); the
project's `python3` is 3.14.7. D7 requires `--uninstall` to run under the system
interpreter with no project imports beyond the module. **A rehearsal night was
already lost to exactly this on 2026-09-11** (`datetime.UTC` under launchd's
3.9). T1 is therefore told in terms that the module must be 3.9.6-compatible —
no `match`, no runtime PEP-604 unions, no `datetime.UTC`, no `slots=True`
dataclasses — and must add a test that EXECS the uninstall path under
`/usr/bin/python3`. This was not in the adjudication; it is a bench fact the
adjudication's D7 depends on.

## The bar, unchanged

The stop condition of synthesis 28/13 §Q3 applies to every delta in this lane,
with class 1 read as D10 states it: **a clock read after the last LAUNCHD
mutation; a sidecar or temp cleanup is not launchd state** — a recording of cold
gate 28 Q1, not a new rule. On YES: no further round, hand back.

## Plan after the seats

Lead-run of the new and ported modules → paired refuters (contract vs execution,
Astra xhigh, disposable detached worktrees) on `git diff 073a9763...HEAD` → fix
rounds with dictated closure shapes and defect-shaped regressions → delta
re-audit of every round with isolated reversions → on clean, a fresh **Opus**
counter-review (row 6, not me), replay (row 9 = sharded full suite **plus**
reproduce.py NO/NO), fresh-eyes (row 10), ledger and PR body. No PR, no merge;
rows 7 and 12 and the merge are the magistrate's. A204 — the watchdog
installer's uninstall, which has the same shape and no re-read at all — lands as
a SEPARATE PR after this one, which is why D8 parameterises the module by label
set from the first commit.
