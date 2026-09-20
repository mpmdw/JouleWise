SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# REFUTER (execution lens, read-only) — INSTALLER-RENDER-ONLY-EVIDENCE-01 at head `__HEAD__` on `fix/2026-09-19-installer-render-only-evidence`

Cwd is a detached read-only worktree at `__HEAD__`. Never touch /Users/edr/code/JouleWise (canonical root) or any other worktree. Interpreter /Users/edr/code/JouleWise/.venv/bin/python. Write only under /tmp. No launchctl, sudo, powermetrics, network. Do not end your turn before the report.

Your job is to BREAK the change, by execution, not by reading. Contract: ruling 04a `/Users/edr/code/JouleWise-wt-mag-a743be05/docs/process_traces/2026-09-19-activation-a743be05/04a-ruling-render-only-evidence.md` (R1–R5 + the addendum: Ed's directive #368 item 1, no mocked rehearsals). Diff under review: `git diff 0959e613..HEAD` (production: `joulewise/night_agent_install.py`, `joulewise/night_gate.py`; tests: `tests/test_night_agent_install.py`, `tests/test_gen_evidence_night.py`, `tests/test_install_night_agent.py`, `tests/test_night_gate.py`, `tests/test_evidence_arm_sequence.py`).

E1. Run the composed arm sequence YOURSELF on a fresh /tmp fixture (not the test): author a v2 evidence plan at a staging path → `scripts/gen_evidence_night.py --render-only` → the ACTUAL shell installer `scripts/install_night_agent.sh --plan STAGED --python PY --render-only DIR` (exit code, stdout JSON, the three plists) → `os.replace` publish → `scripts/install_night_agent.sh --render-only` again from the PUBLISHED path (byte-identical plists?) → `evidence_probe_bindings` → `run_night.probe_night` with the real supervisor (stub only what the repo's evidence probe tests stub) → `validate_probe_receipt` → `validate_install`. Report every exit code and the exact refusal text of anything that refuses.
E2. Mutants (each must be KILLED by a named test; name the test that fails, or report SURVIVED): (a) revert the dispatch so render-only executes the chain for evidence plans; (b) make the ambiguous-payload case fall back to the legacy branch; (c) drop the sealed-literal check (wrapper for another custody root accepted); (d) make `_check_registration` read the relative registration_path from cwd again; (e) skip the sidecar check in the evidence render branch; (f) change the calibration branch's stdout key order or execute the chain twice.
E3. Calibration path byte-identity: diff the calibration render-only branch's behaviour before/after (AST or golden stdout + a spy that the chain runs exactly once with `NIGHT_RESERVATION_ARGV_ONLY=1`); the `/bin/true` staged-stub fixtures in `tests/test_install_night_agent.py` still pass.
E4. Same-signature sweep: any other site in `night_agent_install.py`, `scripts/run_night.py`, `scripts/install_night_agent.sh` that decides behaviour from the EXISTENCE of a calibration artefact rather than the plan's payload kind and that an evidence plan reaches (install, probe, uninstall, night run, courier). Execute where possible.
E5. Run `python3 -m unittest tests.test_evidence_arm_sequence tests.test_night_agent_install tests.test_gen_evidence_night tests.test_night_gate tests.test_install_night_agent 2>&1 | tail -8` (the sandbox `/bin/ps`/sysmond census failure `test_cleanup_refusal_reports_the_failure_it_interrupted` is environmental — name it).

Report: claude-codex-report/v1 envelope for --genre review; findings ranked blocker/should_fix/nit with file:line, the executed command and its output tail for each; SURVIVED mutants are blockers. JSON header under 800 bytes; envelope under 8 KB.
