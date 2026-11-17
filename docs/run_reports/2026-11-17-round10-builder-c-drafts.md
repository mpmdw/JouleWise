# Builder C draft repairs, 2026-11-17

The user selected this off-host draft repair on `audit/2026-11-10-fable`.
M0 found no active stop card on the task worktree at `16d02b846`. The Astra
window-schedule findings 2, 3, 4, 5 and 8, QUEUE-SPEC D8–D10 and RL-165,
RL-172, RL-173 and RL-174 govern the work. No phase exit-checklist row is
being closed.

The six qualification Start blocks now complete native preflight and the
kit checklist before setting `CHECKLIST_OK`. Run refreshes both. Rule 7
backs out s01's work, retry and cleanup budget plus its close interval from
s02's earliest legal cutoff. The D8 s01 ceiling is 16:32:00 PST. The full
27,260 s first-span budget and 300 s close floor yield 16:20:39 PST when
s02 can start as late as 23:59:59. An earlier expiry moves that cutoff
earlier. Actual fence, Check, copy and hand-read evidence still govern.

The launch drafts carry the authorized date and exclusive cutoff. Both
entry scripts are on the qualification kits' frozen path list. The
candidate guard is a separate patch against that source and needs a lead
ruling and exact successor-pin admission before qualification issue.

F0 uses item 377's recorded verified R0 location and treats the check
as fatal. The renewal can be issued ahead and opens at item 346's expiry.
Early issue shortens its effective interval under RL-165's seven days
from actual issue. It uses RL-174's priority order and removes the closed
restart gate. The renewal and twelve F2 drafts use the qualification
maintenance predicate. Dev-05 variant B was already issued on main in
items 393–394. Earlier checks without the cloud-job predicate leave those
jobs unobserved.

## Verification

The audit regressions reproduced failures on `16d02b846`. The child CLI
also reproduced the missing handoff arguments against the unmodified
qualification pin. The verification commands were the three draft
folders' `tests/run_all_gates.sh` under bash and zsh, with their matching
local pins and disposable synthetic fixtures. The changes affect draft
tooling and a candidate patch. The repository-wide suite and cases that
signal fixture processes were outside the verification scope.

- Qualification passed 1,154 gate checks, 246 close/copy cases, 91 pinned
  checks, 21 standing-F0 checks, nine Round 10 scenarios and seven
  regeneration checks. The gate tests execute the embedded bash and zsh
  blocks, including full Start with the flag unset and a failed checklist
  with a previously supplied flag.
- F2 inst-01 passed 872 gate checks, 144 close/copy cases, eight mock
  spans, the q600 synthetic runtime and 22 local staging cases in each
  wrapper run.
- F2 inst-02/03 passed 944 gate checks and 144 close/copy cases per kit,
  plus 30 pinned kit and mock checks, 396 hp-02 gate checks and 50 local
  staging cases in each wrapper run.

The audit branch carries no PR. Its CI workflow is configured for PR
events and pushes to main.

## Handoff

[Qualification status and recovery instructions](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118/STATUS.md)
records the recovery instructions and the open t0 guard admission.
The audit branch advanced to `b26c0d0e7` with RL-175 during this run. Its
C.3 resolves the original half-run NEEDS_RULING. Preserve the first
span's actual date. Use a lead-issued s02 on the next unused date with
the same legs and seeds pending the Friday span-keyed regeneration.
RL-175 C.4's batch arm enforcement is also due before qualification
issue. The next lead step is to decide successor-pin admission of the
candidate guard and obtain the two exact-pin admission lines for each
kit. The F0 renewal is a draft for lead issue. RUN_STATE was not edited.
