# Seat brief — register BRIDGE-BASELINE-COMPLIANCE-01 (process finding from the transactional-installer lane)

SESSION_MODE: delegated
WRITE_SCOPE: ["docs/process/state_kernel.json","tests/test_gen_state.py","TASK_QUEUE.md","RUN_STATE.md"]
BASE_HEAD: 22f70bf2c17f60d2a615e3dd9bb56207bf40cb70
BASELINE_MANIFEST: .codex-bridge/baselines/mag-lanes7-1604.json
BASELINE_DIGEST: sha256:701cf04c04817b0bf2f3fb1d98c5178efe8597fb85d3a1958e4f8e3a5b8bb22c
LEASE_ID: lease-38f5fbdc66d64863b2752e4ecd0080b5

Worktree `/Users/edr/code/JouleWise-wt-lanes-d6888966`, branch `chore/2026-09-15-lanes-d6888966` at `22f70bf2` (origin/main). Do NOT commit. Never touch `/Users/edr/code/JouleWise`, other worktrees, `/Users/edr/JouleWise-measurement-*`, `~/Library/LaunchAgents`, `/Users/edr/night-custody`. No network. `RUN_STATE.md`/`TASK_QUEUE.md` change ONLY inside the generator-owned fences via `python3 scripts/gen_state.py`.

Register ONE task, rank 205, lane `agent`, status `queued`, priority `p2_next_slice`, in the shape of today's rows (`git show 6684dc76 -- docs/process/state_kernel.json tests/test_gen_state.py`). Row count 178 + 1 = 179 with the dated comment convention.
Goal: `docs/contracts/bridge_protocol.md` §7 requires `scripts/bridge baseline` and `BASE_HEAD`/`BASELINE_MANIFEST`/`BASELINE_DIGEST` in the prompt before every workspace-write Codex session, and a governing lease for `scope-check`; on 2026-09-15 every seat launched by the magistrate (activation d6888966: four harvest seats, the GAMMA repair seat, six lanes seats) and by its Opus lieutenant until mid-afternoon ran through `~/.local/bin/codex-run-v3` without `--base`, so manifests record `scope_action: not_enforced` and `bridge lease-list` showed zero leases (`ATTRIBUTION_INDETERMINATE`); an xhigh seat read the contract and refused, earlier seats did not. Compensating controls were the lead's pathspec commits, independent refuters and delta re-audits, and bench re-runs; nothing was re-run.
Acceptance summary: the council or cold gate rules (rule 11: a process rule is not the magistrate's or lieutenant's to ratify) whether the detached launcher pattern used by the magistrate and lieutenant must carry `bridge baseline` + `lease-acquire` for every workspace-write seat, and whether `codex-run-v3` without `--base` may be used at all for editing seats; the ruling is recorded in the decision log by dated addendum and the launcher template in the codex-delegation skill / `docs/orchestration.md` updated accordingly; until then every new editing seat carries baseline + lease (the lieutenant already does).
Evidence: `docs/process_traces/2026-09-15-activation-d6888966/lt-24-T1-rulings-and-protocol-finding.md`, `lt-27-refuters-fixes-delta.md` (§protocol findings); `docs/contracts/bridge_protocol.md` §7 (cite the lines); manifests under `docs/process_traces/2026-09-15-activation-d6888966/manifests/` (`scope_action` field).
Authority label: 2026-09-15 activation d6888966 (magistrate registration of the lieutenant's protocol finding; the ruling itself is the council's/cold gate's).

Verification to paste: `python3 scripts/gen_state.py && python3 scripts/gen_state.py --check; echo rc=$?`; `python3 -m unittest tests.test_gen_state 2>&1 | tail -3`; `git status --short`; `git diff --stat`. Report in the claude-codex-report/v1 envelope; NEEDS_RULING on any schema conflict.
