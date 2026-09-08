WRITE_SCOPE: []

# Refuter brief — G2A-CHAIN-ROUTING-01 landing, EXECUTION lens (gpt-6-astra, read-only)

HEAD of this detached worktree = the seat landing (one commit on main e4ce8b3b). Packet: `git diff HEAD~1 HEAD`
(7 files: scripts/gen_g2_phase_d.py, scripts/run_night.py, docs/process_traces/2026-08-28-live-smoke/{preflight.sh,
SHAKEDOWN-G2-RUNSHEET.md, 2026-09-08-g2a-chain-routing-report.md}, docs/process/NIGHT_HANDBACK.md, three test
modules). Seat claims: the emitted G2-a chain, the preflight and the night driver's `_run_chain_once` now take
`measurement_root`, `measurement_head` and the interpreter (`$MEASUREMENT_ROOT/.venv/bin/python`, derived since
the v2 schema has no interpreter field) from the parsed night plan, overriding inherited environment; refusals when
missing/relative/head-mismatch; no literal `JouleWise-measurement-20260813` or `code/JouleWise/.venv` survives in
the emitted chain; historical runbook block byte-identical and marked superseded; 74 tests across three modules.

Break it, on THIS machine: (1) emit the chain (`python3 -B scripts/gen_g2_phase_d.py --emit-chain $TMPDIR/chain
--night-date 20260910`), `zsh -n` it, grep it for BOTH retired literals and for any other absolute `/Users/edr`
path; (2) construct a v2 plan JSON (use `joulewise.night_plan_writer.write_night_plan` or the schema in
`joulewise/night_gate.py`) whose measurement_root is a scratch `git clone --no-hardlinks` of this worktree detached
at HEAD, and drive `_run_chain_once` (or the smallest driver entry that reaches it) with a stub chain that only
prints its environment: confirm MEASUREMENT_ROOT/HEAD/interpreter arrive from the plan and that a poisoned
inherited environment (export the OLD literals first) is overridden; (3) head mismatch: move the scratch clone one
commit and confirm the preflight/driver refuse with the named text BEFORE any measurement step; (4) relative or
missing root → refusal; (5) the interpreter derivation: what happens when `$MEASUREMENT_ROOT/.venv/bin/python` does
not exist — is that refused early with a clear text or does it fail deep inside the chain? (6) mutation: in a
$TMPDIR copy, re-insert one literal in the emitter's source block and confirm the retired-literal regression fails;
(7) anything the chain's remaining steps still assume about the OLD root (grep the whole emitted chain and
preflight for `20260813`, `.venv`, `code/JouleWise`). Run only the three touched test modules. Report (genre
review): `verdict` = {counts, findings} ONLY; header < 8192 bytes; each finding with file:line, severity, exact
demonstrating command.
