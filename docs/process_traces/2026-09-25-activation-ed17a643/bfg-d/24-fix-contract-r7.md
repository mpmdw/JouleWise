# BFG-D round 7: consumer-drift cure (lead contract)

**The one source.** `23-consumer-drift-final-texts-v1.1-source.md` §3 ("Consumer-drift final texts v1.1", §3.1–§3.13) is the cold Fable addendum to CONSUMER-DRIFT-ESC-01. It supersedes the original ruling where the two differ. Implement §3 exactly. Wherever §3 gives a name (function, class, code, message, flag, docstring text, runbook text), use it verbatim. Every §3.12 test must be RED at `3e984ecc` where the text marks it so, then GREEN. Paste both results.

**Also close these open items from the round-2 delta:**
- Sol F3 / Astra F2: the sweep inventory in `tests/test_battery_float_sweep.py` still labels controller, backfill and paper_anchor as `UNGATED`. Update each label to its refusal and to the test that proves the refusal.

**Rules.**
- WRITE_SCOPE is given in the prompt.
- Never weaken an existing assertion. List every expected-value edit with its before and after.
- **Run every test module that imports a changed production file or a changed fixture builder.** Find them with `git diff --name-only 3e984ecc HEAD` plus grep. Paste each module's tail. The last two rounds missed regressions because they skipped this step.
- The pin proof must be empty: `git diff --stat c6814dd8 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs`.
- Do not touch the frozen battery grammar. The pin test in `battery_float.py` must stay green.
- No full test discovery.
- One foreground session. No subagents or background jobs.
