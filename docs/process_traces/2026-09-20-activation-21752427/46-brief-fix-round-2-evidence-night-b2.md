SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/evidence_night.py", "tests/test_evidence_night.py", "docs/contracts/evidence_night_entry.md", "docs/process/NIGHT_HANDBACK.md"]

# EVIDENCE-NIGHT-ENTRY-01 slice B2 — fix round 2 (fresh eyes 45 findings 1–3, nits 5)

Cwd is `/Users/edr/code/JouleWise-wt-b2r2-21752427` on branch `feat/2026-09-20-evidence-night-b2-r2` at `67a147c4` (= B2 round 1). Same rules as briefs 40/43 (no canonical/other worktrees; only WRITE_SCOPE; injected `gh` and launchctl seams; no mail/network/sudo; no commits). Interpreter `/Users/edr/code/JouleWise/.venv/bin/python`; prove under `/opt/homebrew/bin/python3.11` too. Known sandbox artefact: the 8 s supervision-watchdog test in `tests.test_run_night` — ignore. Each closure needs a test that FAILS at `67a147c4` and PASSES after.

E1 (finding 1 — surviving mutant): a test that exercises the boundary production gate: a `veto.json` with `production: true` but a `veto-at-publication` observation produced with the fixture magistrate/injected runner while `launchctl_bin` is the literal `launchctl` → `publish-install` refuses "rehearsal veto evidence cannot authorize a real arm" AT THE BOUNDARY (use a seam that lets the boundary observation be non-production while the earlier record was production). Prove: deleting the boundary gate makes the test fail.
E2 (finding 2 — phase ordering + timeout): the boundary veto observation runs BEFORE `record["phase"] = "publishing"`, under its own phase `observing-veto`; `probe_command`/the gh runner call gets a `timeout` (60 s) and a timeout refuses "cannot read directives: timeout" (record written with `clear: false`); the contract's phase table updated. Tests: phase sequence asserted from the attempt record; a runner that sleeps past the timeout → refusal, and `phase` never reached `publishing`.
E3 (finding 3 — doc contradiction): handbook clause (the +9 paragraph's last sentence) becomes exactly: "`publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change." The contract's corresponding sentence says the same. Protected regions untouched (md5s: Executed→EOF `4c71305c…`; ARM-RETRY-POLICY lines 68–144 `fc6e3a97…`).
E4 (nits): a blank line between the provenance line and "Ed,"; the test that prints a full notice body captures stdout; document in the contract that a successful real-`launchctl` publication is exercised only at the bench's first live use (no fixture can prove `outcome: installed` with a real launchctl).

Verification: `tests.test_evidence_night` under 3.13 AND 3.11; `tests.test_evidence_arm_sequence tests.test_arm_retry tests.test_night_gate`; counterfactual proof for E1/E2 (fail at 67a147c4 → pass); protected-region md5s; `git diff --stat`.
Report: claude-codex-report/v1 envelope, --genre implementation; JSON header < 800 bytes; total < 8 KB.
