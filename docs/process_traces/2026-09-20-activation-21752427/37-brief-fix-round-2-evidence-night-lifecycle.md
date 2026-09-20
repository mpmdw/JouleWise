SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/evidence_night.py", "tests/test_evidence_night.py", "docs/contracts/evidence_night_entry.md"]

# EVIDENCE-NIGHT-ENTRY-01 slice B1 — fix round 2 (fresh eyes 36 F1/F2/F4)

Cwd is `/Users/edr/code/JouleWise-wt-lifecycle2-21752427` on branch `feat/2026-09-20-evidence-night-lifecycle-r2` at `0481bb0b` (= round 1 + main). Same rules as briefs 30/35 (no canonical/other worktrees; only WRITE_SCOPE; fake launchctl seam only; no mail/network/sudo; no commits). Interpreter `/Users/edr/code/JouleWise/.venv/bin/python`; also prove under `/opt/homebrew/bin/python3.11`. Do not end your turn before the report. Each closure needs a test that FAILS at `0481bb0b` and PASSES after.

C1 (F1 — retry routing with the caller's code): `retry_inventory` must call `arm_retry.classify_abort` INSIDE the clone's venv python (`P -B -c …`, JSON in/out, cwd = clone), exactly as B6 does for the census; no caller-side `arm_retry` import on the `check` path. Counterfactual test: a fixture clone whose `joulewise/arm_retry.py` is patched to route every cause to `retry` (or to `cold_gate`) while the caller's routes differently → `check`'s verdict must follow the CLONE.
C2 (F2 — inventory location): the attempt inventory and prior-attempt records are read ONLY from `<staging>/lifecycle/` (one home); root-level `attempts.json` / `arm-attempts/` are not read (and their presence at the candidate root is the existing "unknown or uncheckpointed staging output" refusal of `prepare`); update the test that hand-writes `attempts.json` to write it under `lifecycle/`.
C3 (F4 — contract): document the refusals "unresolved raw census row", "malformed attempt journal/inventory", "installer ownership/rollback unknown"; move the fake-launchctl "rehearsal, never armable" rule to sit beside the `armable` definition.

Verification: `tests.test_evidence_night` under 3.13 AND 3.11; `tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_arm_census`; counterfactual proof for C1/C2 (fail at 0481bb0b, pass after); `git diff --stat`.
Report: claude-codex-report/v1 envelope, --genre implementation; JSON header < 800 bytes; total < 8 KB.
