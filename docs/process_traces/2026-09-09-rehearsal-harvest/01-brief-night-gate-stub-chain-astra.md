WRITE_SCOPE: ["joulewise/night_gate.py","scripts/run_night.py","tests/test_night_gate.py","tests/test_run_night.py"]
SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Seat brief — NIGHT-GATE-STUB-CHAIN-01 (gpt-6-astra, medium, genre implementation)

## Forcing defect (live, 2026-09-09 02:56 PDT, plan rehearsal-20260909, class REHEARSAL_STUB)
The armed stub night produced result.json verdict REHEARSAL_ONLY / chain rc 0, but receipt.json verdict REFUSED with refusal
reason `night_probe_error`, detail `FileNotFoundError: [Errno 2] No such file or directory: '/Users/edr/night-custody/rehearsal-20260909/chain.zsh'`.
Cause (lead-verified on main 83ab38ed, read-only): `joulewise/night_gate.py::evaluate_night` reads `plan.chain_path` and
`plan.chain_sha256_path` through `probes.read_text` unconditionally (lines ~1046–1047) for every receipt class, while
`scripts/run_night.py` substitutes the built-in stub chain for REHEARSAL_STUB (lines ~1567–1570: chain_path=/dev/null,
command `sleep 2; echo REHEARSAL`) and the stub arm never writes `chain.zsh` or its sidecar. The driver then continued because
`rehearsal_effective` (line ~1540) is true, so the log line `night gate verdict=REFUSED` was silently overridden.
`tests/test_night_gate.py::test_a_fully_green_rehearsal_can_never_yield_go` (line ~414) did not catch it because
`FakeProbeSource.read_text` serves chain and sidecar text for every path.

## Cure contract (gate side keeps gate and driver in ONE truth)
F1 — In `evaluate_night`, for `plan.receipt_class == "REHEARSAL_STUB"` do NOT read the chain or sidecar. Record the substitution
inside the C5 row's `measured` dict only, e.g. `"chain_sha256": null, "expected_chain_sha256": null, "chain_stub": "built_in_stub_by_design"`
(exact key names are yours; they must be stable and tested). Do NOT change the class table (`class_table()`, the ruled
condition matrix pinned by `test_the_class_table_matches_the_ruled_condition_matrix`) and do NOT change any `basis` value or the
`validate_receipt` basis rules (lines ~1417–1425 require PASS/FAIL with null basis for non-NOT_APPLICABLE rows). If you conclude the
cure cannot be expressed without touching the class table or basis rules, STOP with NEEDS_RULING (question, options, recommendation,
blocked work) rather than change them. Every other class (DIAGNOSTIC_NO_PACK, TRANSACTION_PACK) keeps the unconditional chain +
sidecar read and all existing sidecar defect checks byte-for-byte.
F2 — Defect-shaped regression in `tests/test_night_gate.py`: a REHEARSAL_STUB plan evaluated with a probe source whose `read_text`
RAISES `FileNotFoundError` for `plan.chain_path` and `plan.chain_sha256_path` yields verdict REHEARSAL_ONLY, refusal None,
`validate_receipt` returns [], and `read_calls` contains neither chain path (counterfactual: on main 83ab38ed this test must FAIL
with the `night_probe_error` refusal — state the observed pre-cure failure in your report). Also pin that a DIAGNOSTIC_NO_PACK plan
with the same raising probe source is still refused `night_probe_error` (the unconditional read survives for real classes).
F3 — Driver log line in `scripts/run_night.py` (~line 1518): when `receipt.verdict == "REFUSED"` append the refusal reason and detail
to the same line, e.g. `night gate verdict=REFUSED reason=<reason> detail=<detail>` (one line, detail truncated to 200 chars); the
non-refused form stays exactly `night gate verdict=<verdict>`. Regression in `tests/test_run_night.py` through the existing
driver test seams (do not add new production seams). If the existing seams cannot reach that line without a new seam, implement F1+F2,
leave F3 undone, and say so in the report as blocked work.
No behaviour change to any other verdict path, exit code, file written, or courier behaviour.

## Acceptance and constraints
- Run to a log with rc: `python3 -m unittest tests.test_night_gate tests.test_run_night` (scoped modules, never the repo-wide suite).
- WRITE_SCOPE is exhaustive; do not edit docs, plans, RUN_STATE, TASK_QUEUE, or any other test module. No `git commit`, no push.
- Report: claude-codex-report/v1 envelope, genre implementation verdict keys, header < 8192 bytes; body = per-finding cure +
  counterfactual (pre-cure failure text) + the exact test tails with rc.
