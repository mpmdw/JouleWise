SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Fresh-eyes review (read-only) — EVIDENCE-PLAN-PATH-BINDING-01 final head `9f452559`: the lead's bench commit `9a0d8fa8..9f452559541dc6ea1113a0c8d7ab0ceef3208917`

Cwd is a detached read-only worktree at `9f452559541dc6ea1113a0c8d7ab0ceef3208917` (`git log -1`). Never touch /Users/edr/code/JouleWise (canonical root) or any other worktree; write nothing but /tmp scratch; no sudo, no powermetrics, no `collect`/`load`, no LaunchAgent install/probe, no email. Interpreter /Users/edr/code/JouleWise/.venv/bin/python (read-only use). You have not seen this branch before. Do not end your turn before every item has an answer.

Read as files: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/90a-ruling-plan-path-reviews.md` (what the bench commit must be), `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/89-refuter-plan-path-binding-astra.md` (R1) and `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/90-opus-counter-review-plan-path.md` (S1/S2/N1–N3, with the /tmp probes), `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/87a-ruling-evidence-plan-path-binding.md` (the original contract).

F1. `git diff 9a0d8fa8 9f452559541dc6ea1113a0c8d7ab0ceef3208917`: exactly the 90a closure and nothing else? Does resolving BOTH sides of the identity comparison keep the sealed literal unresolved (the generator must not resolve)? Execute: the Opus probe 2 shape (custody root reached through a symlink; `--plan` given resolved AND literal — both must now pass bindings), the refuter's `/tmp` vs `/private/tmp` case, and the Opus probe 1 shape (relative custody root → the generator's `GenerationRefusal` before any artefact is written).
F2. Mutants in /tmp: (a) revert `.resolve()` to `.absolute()` on the plan side only → which test fails; (b) drop `_require_absolute` → which test fails; (c) resolve the literal in the generator → which test fails (the byte-identity or literal tests must catch a resolved literal on a symlinked/aliased root — if none does, that is a finding).
F3. Run `tests.test_gen_evidence_night tests.test_night_agent_install tests.test_night_gate tests.test_run_night tests.test_quiet_predicate_campaign` and `scripts/quick_suite.py --tier quick --workers 4`; paste tails (a blocked `/bin/ps` census in your sandbox is environmental — say so and name the tests; the BindSupervision 8 s watchdog failures are sandbox-only — the lead's unsandboxed runs pass them).
F4. Same-signature: any other place in the installer or gate that compares a plan-content path with a runtime path using a different normalisation than its sibling check (grep `.absolute()` / `.resolve()` / `os.path.realpath` in joulewise/night_agent_install.py, joulewise/night_gate.py, scripts/run_night.py) — a mismatched pair that can be mutually unsatisfiable on the same inode is a finding.

Report: claude-codex-report/v1 envelope for --genre review; verdict = {counts, findings}; JSON header under 8000 bytes; counterfactual + call site per finding.
