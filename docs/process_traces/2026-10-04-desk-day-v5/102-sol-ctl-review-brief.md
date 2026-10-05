# Executing review (Sol 6.1 xhigh, non-author): PR #482, controller G2-b pre-slot attachment and per-bundle battery pairs (head 9b08ecf6)

Worktree: /Users/edr/code/JouleWise-wt-dd5-ctrev, detached at 9b08ecf6 (parent main b2ff2f36). Diff: `git diff b2ff2f36 9b08ecf6`. Findings it fixes: `/Users/edr/night-archive/ia-0a40/MEMO.md` §1.16 and §1.2(b) (repros `/Users/edr/night-archive/ia-0a40/premortem/scratch-*/`). Seat report `/Users/edr/night-archive/desk-day-v5/sol-ctl.md`.

Hunt by executing code: (1) can the new attachment route accept any calibration directory other than the authenticated launch lineage's finalized PRE slot of the same session (foreign session, post slot, unfinalized, symlinked or copied directory, stale lineage file, lineage without a consumption record)? Can G2-a's existing opt-in path or a plain non-G2 run now accept Revision-5 markers they refused before? (2) Are the battery observations really outside the sampler lifetime and the clock-anchor stamps (trace the call order in `run_member`/equivalent; a probe that runs while powermetrics samples would add CPU load to the measured stream)? Does a slow or hung ioreg delay a phase stamp? Is a failure recorded and never raised? (3) Do the readers that #421's harvest uses accept these pairs on a real bundle shape? (4) Mutate each guard and watch a test fail. Run `tests/test_controller*.py tests/test_battery_float*.py tests/test_revision_five*.py` (TMPDIR=/tmp/dd5-ctrev).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-ctrev/ only. No background processes. Finish in this turn.
