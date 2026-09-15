# Seat brief — register INSTALLER-BACKUP-WINDOW-01 (cold gate 28 Q4, F4)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at origin/main (cite `git rev-parse --short HEAD`). Do NOT commit. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. `RUN_STATE.md`/`TASK_QUEUE.md` change ONLY inside the generator-owned fences via `python3 scripts/gen_state.py`.

Register ONE task, rank 203, lane `agent`, status `queued`, priority `p4_polish`, in the shape of today's rows (`git show 3bcdfae8 -- docs/process/state_kernel.json tests/test_gen_state.py`). Row count 176 + 1 = 177 with the dated comment convention.
Goal: in `scripts/install_night_agent.sh` (integration branch `int/2026-09-15-install-windows`, round 2 head `9a7bacdf`; lines ~304–309) the prior-plist backup `cp` runs before `trap teardown EXIT` is installed, so a signal in that window leaves prior plists intact, no job loaded, and one leaked backup directory under `TMPDIR` — a conservative half-state (the fence still sees the prior plan) but a leak.
Acceptance summary: the trap block is installed before `mktemp`, with `plist_backup=""` initialised so `teardown`'s early return handles the no-backup case; a regression sends TERM during the backup `cp` (fake `cp` on the fixture PATH) and asserts no `/tmp/night-agent-install.*` survives, both priors byte-identical, no job loaded; lands after INSTALL-WINDOWS-MULTI-01 merges, in its own small PR; not night-critical.
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/28-coldgate-packet-install-windows-round-3/10-coldgate-fable-ruling.md` (Q4 F4); `12-opus-pairing-refuter-on-ruling-10.md` (Q4); `13-magistrate-synthesis-ruling-10-with-opus-amendments.md` (Q4); `lt-15-delta-re-audit-round-2.md` (F4).
Authority label: cold gate 28 ruling 10 Q4 + Opus pairing 12 + synthesis 13 (magistrate registration, not a ruling). Dependency: INSTALL-WINDOWS-MULTI-01 (hard start dependency, same shape as ARM-RETRY-CLASS-01 uses on its predecessor — copy that shape; if the schema rejects it, register without the dependency and say so).

Verification to paste: `python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?`; `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`; `git status --short`; `git diff --stat`. Report in the claude-codex-report/v1 envelope; NEEDS_RULING on any schema conflict.
