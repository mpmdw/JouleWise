WRITE_SCOPE: ["tests/test_check_window_provenance.py","tests/test_preflight.py","docs/process_traces/2026-08-28-live-smoke/**","scripts/gen_g2_phase_d.py"]

# Fix-round brief — G2A-CHAIN-ROUTING-01, Opus contract-refuter findings (gpt-6-astra, medium)

HEAD = f0fedc91 on feat/2026-09-08-g2a-chain-routing (the routing landing). An Astra execution refuter was clean;
the Opus contract refuter (trace 33) returned LAND-WITH-FIXES. Cure B1 (blocker), B2, B3 (should-fix); N1, N2
optional if cheap; N3 = add one sentence. Findings verbatim:

B1 blocker — `tests/test_check_window_provenance.py:641-650`
`test_preflight_requires_documented_measurement_checkout_argument` pins the RETIRED preflight contract: it asserts
`/Users/edr/JouleWise-measurement-20260813` and `SMOKE_CHECKOUT="$1"` are still in `preflight.sh`. The diff
removed both, so the suite is red at HEAD. Re-express its intent ("the preflight pins one documented argument")
against the NEW contract (`preflight.sh <night_plan.json>` deriving root/head/interpreter from the plan) rather
than deleting it. Demonstrate: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -k
test_preflight_requires_documented_measurement_checkout_argument tests.test_check_window_provenance` fails before,
passes after.

B2 should-fix — `SHAKEDOWN-G2-RUNSHEET.md:730-731`, `:705-707` vs `:251`: the desk (human) path lost its routing
recipe. Phase A invokes `preflight.sh "$NIGHT_PLAN"` and asserts `"$MEASUREMENT_HEAD"`, but the only block that
exported those coordinates is now SUPERSEDED, and the operative block (L1516-1580) CONSUMES `MEASUREMENT_ROOT` /
`MEASUREMENT_HEAD` from the environment. Add an operator step in Phase A that sets `NIGHT_PLAN` to the plan file
and derives `MEASUREMENT_ROOT` / `MEASUREMENT_HEAD` from it with `/usr/bin/jq` (verbatim commands), before any
desk block that consumes them.

B3 should-fix — `RUNSHEET.md:265-266` and `00-verification-notes.md:18-19` still specify the retired contract
(`FAIL REVIEWED_HEAD is required`; A2 row requiring `REVIEWED_HEAD`, `SMOKE_CHECKOUT`, the source interpreter).
Reconcile both to the new contract by dated addendum lines (do not rewrite historical verification records; add
"superseded 2026-09-08 by …" pointers next to the stale rows).

N1 nit — `tests/test_preflight.py:47-58`: the preflight is never executed as a program; add one subprocess test
that runs `preflight.sh` with no argument (expect exit 2 + usage) and with a plan whose head mismatches (expect the
named refusal), and drop the vestigial `REVIEWED_HEAD` env at `:53`.
N2 nit — `scripts/gen_g2_phase_d.py:411`: a missing `## Plan-derived measurement variables` heading escapes as an
uncaught ValueError from `_section_bounds`; make `--check` print a `FAIL …` line and exit non-zero instead.
N3 nit — `SHAKEDOWN-G2-RUNSHEET.md:1490`: say in one sentence that the clone-prep fence is ```bash on purpose so
the emitter's `^```(?:sh|zsh)` regex excludes it from the night chain.

Constraints: WRITE_SCOPE exhaustive; acceptance = `python3 -m unittest tests.test_check_window_provenance
tests.test_preflight tests.test_gen_g2_phase_d tests.test_run_night` to a log with rc, plus `python3 -B
scripts/gen_g2_phase_d.py --check`; never the repository-wide suite; no `git commit`; header < 8192 bytes; genre
implementation verdict keys; body = per-finding cure with fail-before/pass-after tails.
