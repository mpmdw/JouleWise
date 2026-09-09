WRITE_SCOPE: ["tests/test_check_window_provenance.py","tests/test_preflight.py","docs/process_traces/2026-08-28-live-smoke/preflight.sh"]

# Seat brief — G2A-PREFLIGHT-ARGV-ASSERT-01 (gpt-6-astra, medium)
Delta re-audit trace docs/process_traces/2026-09-08-handoff-redo/39-ref-routing-delta-astra-report.md R1: the
re-expressed provenance test in tests/test_check_window_provenance.py checks preflight SOURCE STRINGS, so two mutants
survive: (1) a preflight that normalises two positional arguments to one before the arity guard; (2) a preflight
that supplies the missing argument from `NIGHT_PLAN` in the environment. Add EXECUTABLE refusal assertions (run
docs/process_traces/2026-08-28-live-smoke/preflight.sh as a program, the way tests/test_preflight.py's subprocess
tests do): two positional arguments → exit 2 + usage; zero arguments with `NIGHT_PLAN` exported → exit 2 + usage
(no env fallback). If preflight.sh currently accepts either, fix preflight.sh so it refuses (that is a behaviour fix
inside the routing contract: exactly one positional argument, the absolute v2 plan path). Prove each assertion
fails against the corresponding mutant in a $TMPDIR copy. Acceptance = tests.test_check_window_provenance
tests.test_preflight tests.test_gen_g2_phase_d to a log with rc; `bash -n` on the preflight. Never the
repository-wide suite; no `git commit`; header < 8192 bytes; genre implementation verdict keys.
