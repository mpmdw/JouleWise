SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/quiet_predicate_campaign.py", "scripts/night_chains/quiet_predicate_evidence.zsh", "scripts/run_night.py", "scripts/gen_evidence_night.py", "scripts/sample_quiet_predicate_evidence.py", "joulewise/night_gate.py", "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json", "configs/campaigns/quiet_predicate_evidence_01/README.md", "tests/test_quiet_predicate_campaign.py", "tests/test_run_night.py", "tests/test_night_gate.py", "tests/test_gen_evidence_night.py", "tests/test_sample_quiet_predicate_evidence.py", "docs/process/NIGHT_HANDBACK.md"]

# STAGE-A-EVIDENCE-EXECUTOR-01 fix round 1 — Opus counter-review 61 (B1, B2, S1–S4) and the refuters 56c/56x, as ruled in triage 61a (+ addendum)

Cwd is the linked worktree of branch `feat/2026-09-19-stage-a-evidence-executor` at `__HEAD__` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp`; no `sudo`, no `powermetrics`, no live `collect`, no LaunchAgent install. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

Read as files: `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/61a-triage-opus-counter-review-stage-a.md` (the ruled fix shape per finding — implement each disposition exactly), `61-opus-counter-review-stage-a.md` (findings with file:line), and the two refuter reports `56c-refuter-contract-stage-a-astra.md` / `56x-refuter-execution-stage-a-astra.md` (their findings are dispositioned in 61a's addendum; implement those marked ACCEPT).

## Deliver, each with a defect-shaped regression named in 61a

B1 continue-on-envelope-failure (named mechanisms `collect_error`, `cleanup_unproven`; abort only on the chain's own refusal class or ≥ 2 consecutive `cleanup_unproven`; refusal document on abort) · B2 pre-execute refusal → typed refusal document + missing process journal = nothing to clean → the courier always runs · S1 all five sizing/protocol constants (δ, multiplier, floor, stop, block-two share) frozen in `pilot_protocol_v1.json`, required by `validate_protocol`, read by code, README lists them with the file as the source; re-pin the digest in the gate table and its test · S2 cleanup proven by process absence after a bounded wait, never by `killpg` success; EPERM on a foreign group logged, not fatal; the recorder keeps its supervised stop path · S3 the reducer joins `evidence_busy_cores.jsonl` to envelopes by monotonic support and reports per-envelope `busy_cores` covariates and the clean-machine distribution (never retention inputs) · S4 a test pins the serialized ruled-registration table (dated-comment discipline) and checks each entry's `ruling` names an existing record path · nits from 61 that touch files already in scope · cross-unit review 62 N1: in `tests/test_sample_quiet_predicate_evidence.py` move the platform-independent "Process.start() must close both Pipe ends" block out of the darwin-only ladder test back into the cross-platform fake-clock test (it needs no spawn).

## Bench acceptance (execute; paste tails)

Changed modules individually; the seven-module set from record 55/59; quick tier; negative oracles for B1/B2/S1/S2/S3 (each: the counterfactual input from 61 fails the new regression on a `/tmp` copy with the fix reverted); `git diff --stat` within scope; no LaunchAgent installed.

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; clause map (finding → site → biting test → counterfactual); NEEDS_RULING if a disposition cannot be implemented as written.
