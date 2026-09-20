SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Execution-lens refuter (read-only) — EVIDENCE-PLAN-PATH-BINDING-01, `a9e48ae9..9a0d8fa853cbdbad1177a0588891b23d4966d225` on `fix/2026-09-19-evidence-plan-path-binding`

Cwd is a detached read-only worktree at `9a0d8fa853cbdbad1177a0588891b23d4966d225` (`git log -1`). Never touch /Users/edr/code/JouleWise (canonical root) or any other worktree; write nothing but /tmp scratch; no sudo, no powermetrics, no `collect`/`load`, no LaunchAgent install or probe (fixture-only probe code paths are fine), no email. Interpreter /Users/edr/code/JouleWise/.venv/bin/python (read-only use). You have not seen this branch before. Do not end your turn before every item has an answer.

Read as files: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/87a-ruling-evidence-plan-path-binding.md` (the contract), `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/87-arm-scripts-qpe01-pilot-astra.md` and `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/87-arm-scripts-qpe01-pilot/README-sequence.md` §"NEEDS_RULING — blocking conflicts" (the fixture reproduction at main), the seat's report `/tmp/magistrate-d0b83820/88-evidence-plan-path-binding-astra.md`, and the runbook §1.1b (`docs/phase_2/derivation_night_runbook.md`) for the invariant.

E1. Execute the arm order end to end on a /tmp fixture with the REAL generator and REAL `evidence_probe_bindings` (no mocking of either): author at a staging path → render (`--render-only`) → `os.replace` into `<custody>/night_plan.json` → bindings PASS; then the negatives: probe with the staged path → the named refusal; a plan whose `custody_root` differs from the directory the plan sits in → refused; wrapper bytes from the staged copy == bytes from the published copy. Paste each outcome.
E2. Run-time consumer: at night time the driver passes the PUBLISHED plan as `--plan`; `joulewise/quiet_predicate_campaign.py` reads `EVIDENCE_PLAN_PATH` — show (by reading `scripts/run_night.py` / the chain template) that the executor and the driver now agree on one path, and that nothing else in the chain reads the staged path.
E3. Same-signature sweep: every `export` the generator writes — classify each as content-derived or argument-derived; any other argument-derived literal that a probe or the gate compares against a run-time path is a finding.
E4. Re-run seat 87's fixture dry-check (`/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/87-arm-scripts-qpe01-pilot/dry-check.py`, /tmp fixtures only) against this head; the "CONFIRMED BLOCKER" line must be gone; paste the tail.
E5. Run `tests.test_gen_evidence_night tests.test_night_agent_install tests.test_night_gate tests.test_run_night tests.test_quiet_predicate_campaign` and `scripts/quick_suite.py --tier quick --workers 4`; paste tails (a blocked `/bin/ps` census in your sandbox is environmental — say so and name the tests). Any test the seat weakened or deleted rather than repaired is a finding.

Report: claude-codex-report/v1 envelope for --genre review; verdict = {counts, findings}; JSON header under 8000 bytes; counterfactual + call site per finding.
