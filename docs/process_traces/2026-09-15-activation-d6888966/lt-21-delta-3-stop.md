# lt-21 — Delta 3: BOTH predicates YES. Stop condition met; no round 4.

Written 11:42 PDT 2026-09-15 (clock read). Head audited: **`073a9763`**.
Auditor: fresh Astra xhigh, detached pid 9917, 11:16:48 → 11:40, worktree
`wt-ref-iw-contract`. Brief `/tmp/magistrate-d6888966/brief-14-delta3.md`;
output `/tmp/magistrate-d6888966/lt-14-delta3.md`.

## The answer to the only question that decides the lane

```
class_1: YES
class_2: YES
```

Both with executed reproductions against the **unchanged** installer bytes at
this head (the reproducer asserts the script bytes equal the worktree's).
Per the adopted, judgment-free stop condition: **no fix seat, no round 4.** I
have launched nothing since. Rows 6, 9 and 10 are not run — they are gated on a
clean delta.

Reproduction command for F1 and F2:
`PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 /tmp/iw-delta3-evidence/reproduce.py`

## F1 — class 1 YES. **Read this one carefully before acting on it.**

The success branch of `teardown` still removes the backup after the commit gate.
Reading the clock during that removal:

| Case | Selected close | Plan cutoff | Post-gate clock read | Exit | Loaded |
|---|---:|---:|---:|---:|---|
| Selected-close first | 1789498860 | 1789498920 | 1789498860 | **0** | both |
| Plan-cutoff first | 1789498920 | 1789498860 | 1789498860 | **0** | both |

Both satisfy the supplied predicate **exactly as written**: exit 0, a label
loaded, a post-gate clock read at or past `min(selected_span_close,
install_close_epoch)`.

**The tension I must flag and must not resolve.** Cold gate 28 Q1 ruled that the
class-1 invariant covers *the two loaded jobs and the two plist files*, that a
`TMPDIR` backup is not that state, and that rc 0 / both loaded / both plists is
the INTENDED installed state — it recorded exactly this result in its own probe
Q1a and called the clock-half definitional, not class 1. The adopted predicate
carries no such carve-out, so **any** work after the gate — including the
backup removal that the same ruling deliberately MOVED into `teardown` — can
cross the bound and fire it. On the ruling's own definition F1 is benign; on the
predicate's text it is YES. **The predicate is judgment-free by design and it
fired; whether it over-fires here is the magistrate's call, not mine.** I report
it as YES because that is what the instrument says.

## F2 — class 2 YES. This one is NOT definitional, and it is the real finding.

**A failed verification query is treated as proof that the label is unloaded.**

All three re-read sites use `print … >/dev/null 2>&1 &&` — lieutenant-verified
by reading at this head: `scripts/install_night_agent.sh:273` (uninstall) and
`:335`, `:338` (teardown). Any **non-zero** exit from `print` is taken as "not
loaded". But only a not-found code means that; an error code means **unknown**,
and the conservative treatment of unknown is "assume loaded, retain the plists".
The stub returned **9**; the code concluded "gone" and deleted.

| Path | Exit | Affected label still loaded | Its plist deleted |
|---|---:|---|---|
| `--uninstall` | **0** | yes | yes |
| `--uninstall` + render-only | **0** | yes | yes |
| failed-install teardown | 3 | yes | yes |

Each row executed separately for the night label and the dead-man label — **six
reproductions**. Uninstall satisfies BOTH alternatives of class 2 (ends with a
label loaded and its plist absent, AND exits 0 while a label it attempted to
bootout is still loaded); teardown satisfies the first.

This is the fence-blind state the whole lane exists to eliminate, reached
through the very mechanism built to prevent it. The verification re-read
verifies *that the query succeeded*, not *that the label is absent*.

## F3 — blocker: a binding must-die requirement FAILED

**Removing `trap - EXIT` SURVIVED** all 59 checked-in installer tests and the
auditor's independent teardown probes (retained labels, missing backups,
render-only, success, cleanup failures). It found no harmful counterexample —
but §Q5 makes that removal a mandatory kill for landing, and it is not killed.

The other five must-die items were RED: the `exit 4`, **each label's** re-read
(checked individually at both the uninstall and teardown sites), the backup copy,
both render-only guards, and the success guard. Two near-misses worth recording:
deleting only the `-p` from `cp -p` survived the 59 tests (an independent mtime
probe kills it — saved mtimes changed instead of preserving `946684800`), and
changing the success guard's `return 0` to `return 1` survived.

## Isolated reversions — three of four correct, one regression exposed as worthless

| Reversion | Result |
|---|---|
| edit 1 | **RED** — `test_backup_removal_failure_after_commit_gate_preserves_verified_arm` (0 != 1) |
| edit 2, uninstall | **RED** — all three subcases (4 != 0) |
| edit 2, occupancy | **RED** — `test_deadman_only_preloaded_refuses_install_without_bootstraps` (3 != 0) |
| edit 3 | **RED** — `test_term_during_first_restore_preserves_both_priors_and_original_status` (3 != 143) |

But: `test_clock_advancing_during_backup_removal_preserves_verified_arm`
**SURVIVED** edit 1's reversion — "worthless as a regression for edit 1", in the
auditor's words. That is the control I ruled in `lt-19`; a control is supposed to
pass before and after, so surviving a reversion is its correct behaviour. It
should be NAMED a control in the test, not counted as a regression. My ruling
was right; the naming invites exactly this misreading.

## Survivor lists

**List A (lt-04 §F4's 22): 7 RED, 15 SURVIVED.** All seven installer signal-exit
constants died. Eight of the survivors are behavioural with executed
counterexamples — resolved-duration `<=`→`<` (accepts a zero-length spring span),
resolved-overlap `<`→`<=` (refuses valid touching spans), both previous-offset
mutants, removal of discovery's deadline validation (`LAUNCHING` instead of
`HOLD_UNSAFE`), removal of `decide()`'s arithmetic guard (uncaught `ValueError`),
and backup-failure exit `1`→`0` (**false success**) and `1`→`2`. The remaining
seven change diagnostic text only and are text-only under §Q5. Note most of the
behavioural ones live in `run_night.py` / `magistrate_watchdog.py`, outside this
lane's WRITE_SCOPE.

**List B (lt-10's 8 + 3): all eleven survive the checked-in module.** The
auditor's independent cleanup-failure probes kill the three tail variants (head
rc 1; mutants 3 / 0 / 2); the eight function mutants still survive. It also
resolved the count discrepancy I flagged: the first historical row contained two
flag mutants, so all eight are accounted for and none was missing.

## What I did NOT do

No fix seat. No Opus counter-review (row 6), no replay (row 9), no fresh-eyes
(row 10) — all gated on a clean delta. No PR, no merge. The head stays
`073a9763`, pushed, green on all seven modules.
