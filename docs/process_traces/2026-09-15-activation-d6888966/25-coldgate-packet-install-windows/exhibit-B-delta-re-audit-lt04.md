# lt-04 — Delta re-audit of the fix rounds

Fresh auditor, no part in writing the code. Astra `xhigh`, detached pid 88647,
launched 07:56:11, returned 08:24 (clock reads), worktree
`wt-ref-iw-contract` detached at `df86cee6`. Brief
`/tmp/magistrate-d6888966/brief-06-delta.md`; output
`/tmp/magistrate-d6888966/lt-06-delta.md`. Envelope `status: findings`,
`completion: complete`, `pathspec: []`.

The brief required, per fix item: reproduce the ORIGINAL defect against the
pre-fix head `7a512827`, confirm it is gone at `df86cee6`, and confirm the
claimed regression FAILS when only the production change is reverted — because
a regression that passes against unfixed code is the commonest way a fix round
lies. It also required a mutation sweep of the NEW code and an explicit
SAME-SIGNATURE statement.

## Verdicts

| Item | Verdict |
|---|---|
| FIX-1 (the blocker) | **NOT CLOSED** |
| FIX-2 | **CLOSED WITH NEW DEFECT** (two) |
| FIX-3, FIX-4, FIX-5, FIX-6, FIX-7, FIX-8, FIX-9, FIX-10 | closed, each with reversion evidence |

Isolated-reversion evidence confirms the FIX-1..FIX-6 regressions are real:
FIX-3's regression fails all eight original inputs when the production change is
removed; FIX-4's errors on both paths; FIX-6's fails both DST cases.

## F1 — blocker, NOT closed: the last bootstrap is still a missed call site

`scripts/install_night_agent.sh:348`. Fix round 1 carried the SELECTED span's
close into the `close`-mode checks, and the advances during bootout and during
the FIRST bootstrap now correctly refuse and clean up. But the final schedule
check precedes the DEAD-MAN bootstrap, and neither the subsequent verification
nor the successful exit reads the clock again. Executed with fake launchctl,
four cases, all **exit 0 with both jobs loaded**:

| Clock advance before the dead-man job is created | Result |
|---|---|
| 12:00 → 12:01:01, selected span closes 12:01 | exit 0, both loaded |
| 12:00 → 12:02:01, crossing TWO span boundaries | exit 0, both loaded |
| plan cutoff 12:01, selected close 12:03 | exit 0, both loaded |
| selected close 12:01, plan cutoff 12:03 | exit 0, both loaded |

This is the same defect the round was called to close, one call site further
along.

## F2 / F3 — should-fix, NEW defects introduced by FIX-2's exit trap

- **F2** (`:329`): on this machine's zsh 5.9, `set -e` exiting from inside the `render()` function SKIPS the top-level EXIT trap. Minimal proof the seat ran: `/bin/zsh -c 'set -e; trap "print trap-fired" EXIT; f() { false; }; f'` exits 1 and never prints. Real filesystem reproduction: a read-only pre-existing dead-man plist makes the second render raise `PermissionError`; the installer exits 1 with the night plist left OVERWRITTEN and its backup directory leaked. The runbook sentence "every unsuccessful exit after rendering" is therefore false as written.
- **F3** (`:310`): TERM/INT/HUP after the first bootstrap exit 143/130/129, remove BOTH rendered plists, and leave the fake night job LOADED, with no bootout attempted. At `7a512827` the same signal left the job loaded **and its plist references**; deleting the references while the job stays loaded is strictly new, and it is the condition the installed-plist fence relies on to see an armed plan. A forced rollback-bootout failure likewise exits 2 printing "rolled back" while the job remains loaded and its plists are deleted.

## F4 — should-fix: the new branches are under-pinned

Requested sweep, whole owning modules: **17/17 RED at `df86cee6`**, so FIX-7's
head claim is confirmed. Its claim that all 17 previously survived is NOT
correct — five were already RED against the full pre-fix modules (the earlier
figure came from a focused subset). Recorded as a correction, not a defect.

New-code sweep: **54 mutations, 32 RED, 22 SURVIVED.** Material survivors:
selected-close `>=`→`>` (exactly at 12:01 during bootout the mutant installs
both jobs, exit 0); resolved-duration `<=`→`<` (a zero-length spring span
passes); resolved-overlap `<`→`<=` (valid touching spans refused); the
previous-span offset; removal of discovery's `deadman_epoch(plan)` validation
(a future plan with `window_max_s=10**400` and `courier.sent` returns LAUNCHING
instead of HOLD_UNSAFE); removal of the `decide()` arithmetic guard (an embedded
NUL in an absolute measurement-root string raises `ValueError`); the six
INT/TERM/HUP exit constants; and the backup-failure exit `1→0`, where the mutant
falsely reports success. Seven further survivors are diagnostic-text only.

## Preservation — all clean (the part that had to hold)

Only THREE pre-existing test lines changed in the whole fix round, all from
FIX-5 rounding fractional-second `t0` fixtures to whole minutes
(`test_install_night_agent.py:101,287`, `test_run_night.py:1690`). The auditor
judged each a valid fixture adjustment: no assertion weakened, no case removed;
the only behaviour no longer exercised is incidental installation of a
fractional timestamp, which FIX-5 now deliberately refuses. Residues 0.001,
0.5, 17 and 59.999 s all refuse.

Protected material verified unchanged: night gate, plan writer, v2 key sets,
`PLAN_LEAD_S`, stand-down ladder, courier constants, window arithmetic, the
write-once record set, `dead_man()`, the relaunch prompt, the PR template,
`docs/decision_log.md`, `docs/process/state_kernel.json`, historical revision
notes and every Executed record, and §1.4's email-then-arm section.

**Runbook §3 is byte-identical**, SHA-256
`71337a836df21f1f3668bcb46e7ffe6e487a247f7ce51368b459b9516612072b`.

Useful negative result: `tests.test_docs_freshness` passes against BOTH the old
and the corrected documentation, so it does not establish the FIX-8/9/10
semantic corrections. The auditor's independent assertions do (they fail on the
old text, pass on the new).

Seven target modules, **411 tests, all OK**, no ERROR, WARNING or
ResourceWarning.

## Residual risk the auditor names

FIX-4's widened handlers classify an arbitrary `ValueError` — including an
injected programming error — as HOLD_UNSAFE; `RuntimeError`, `TypeError` and
`AttributeError` still propagate. It found no naturally occurring programming
defect that this would mask. The sandbox denied `ps`, so a host-wide leaked-
process census is unverified; no live launchd validation was performed by
anyone.

## SAME-SIGNATURE STATEMENT — the auditor answers YES

Two classes, each a repeat of the class the round was called to close:

1. **Missed boundary-check call site** — the final bootstrap can cross the close (F1), after seat A missed the `close`-mode checks entirely.
2. **Incomplete failure cleanup** — render-time `errexit` and the signal / failed-bootout exits (F2, F3), after FIX-2 was written to make failure cleanup complete.

Its own recommendation: "Lead should apply the same-class escalation rule before
another fix round." The lieutenant does so in `lt-05`.
