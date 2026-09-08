WRITE_SCOPE: ["scripts/gen_g2_phase_d.py","scripts/preflight.sh","scripts/prewindow_check.sh","docs/process_traces/2026-08-28-live-smoke/**","tests/test_gen_g2_phase_d.py","tests/test_prewindow_check.py","tests/test_preflight.py","docs/process/NIGHT_HANDBACK.md"]

# Seat brief — G2A-CHAIN-ROUTING-01: the generated G2-a chain and its preflight must take the measurement root, head and interpreter from the v2 night plan, never from literals (gpt-6-astra, high)

## Forcing problem (from the 2026-09-08 readiness scout, trace 27, verified file:line)
`scripts/gen_g2_phase_d.py:130` copies a fixed-variable block from
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:253` and substitutes only the G2-a date. That
block hard-codes the OLD measurement root `/Users/edr/JouleWise-measurement-20260813` (protected, pre-v2, at
eeb4e133; must stay untouched) and the development interpreter `/Users/edr/code/JouleWise/.venv/bin/python`.
`preflight.sh:40` independently requires those exact coordinates. Exporting replacement variables before invoking
the chain does not help: the chain overwrites them. Result: no trustworthy real G2-a v2 plan can be produced, which
blocks every downstream production pack and claim window.

## Ruling you implement (interactive magistrate, 2026-09-08, adopting the scout's option 3)
- The v2 night plan is the ONE source of `measurement_root`, `measurement_head` and the interpreter for a night.
  The emitted chain and the preflight READ them from the plan (or from variables the night driver derives from
  the plan and passes explicitly) and REFUSE if any is missing, relative, or if `git -C $MEASUREMENT_ROOT
  rev-parse HEAD != measurement_head`. No literal root or interpreter path may remain in the emitted chain or the
  preflight; a regression greps the emitted chain for `JouleWise-measurement-20260813` and `code/JouleWise/.venv`
  and fails if either appears.
- Interpreter: `$MEASUREMENT_ROOT/.venv/bin/python` by default (a venv created inside the measurement clone from
  the repository's locked requirements — find how the existing venv is built and document the exact creation
  command in the runsheet), overridable by an explicit plan field only if the plan schema already has one (do not
  add schema fields; if the schema lacks the interpreter, derive it from measurement_root and say so).
- Naming convention for future roots: `/Users/edr/JouleWise-measurement-v5-<YYYYMMDD>-<head7>`, an independent
  `git clone --no-hardlinks` of the canonical repo detached at the reviewed head (the scout's creation sequence in
  trace 27 §1). Document it where the chain's operator instructions live; do NOT create any checkout yourself.
- Keep the 2026-08-28 runsheet's historical block as history: add the parametrised block as the emitter's new
  source and mark the old block SUPERSEDED with a pointer, rather than rewriting history in place (the emitter's
  sidecar/source-block contract at `gen_g2_phase_d.py:116` and `:147` must keep verifying).

## Deliverables
1. Emitter + preflight changes with defect-shaped regressions (each named counterfactual: literal survives in the
   emitted chain; preflight passes with a mismatched head; missing measurement_root not refused).
2. `python3 -B scripts/gen_g2_phase_d.py --check` and `--emit-chain` to a scratch path + `zsh -n` on the result,
   tails recorded.
3. Acceptance = the scoped test modules you touched or added (name them), never the repository-wide suite.
4. Report body: every literal removed with file:line before/after, the plan fields consumed, the refusal texts,
   fail-before/pass-after tails, and any NEEDS_SCOPE / NEEDS_RULING (e.g. if the driver `scripts/run_night.py`
   must pass the variables and is outside scope, return NEEDS_SCOPE naming the exact function).
No `git commit`. Header < 8192 bytes; genre implementation verdict keys.
