# Design consult: SMC sensor classification for ALIGN R0/R1 on the measurement Mac (Mac15,9)

You are one of two blind seats. Propose an amendment to the SMC temperature-sensor classifier, from real
data. Your proposal is an input. The lead and the owner decide; you do not.

## Where things are (read-only for you)
- Code: worktree /Users/edr/code/jw-wt/r0-smc-cov (branch fix/2026-11-07-r0-smc-coverage-cell = lane tip
  e1a91226e + a coverage fix). Classifier: `joulewise/align/apple/smc_enumeration.py` (`rank`, `select_keys`,
  `collect`). Receipt: `joulewise/align/r0_host.py` (around line 470-500). Window-time use of the picks:
  `joulewise/align/apple/thermal_gates.py`, `thermal.py`, `thermal_desk.py`. Design authority:
  `git -C /Users/edr/code/jw-wt/r0-smc-cov show origin/lane/2026-11-05-align-window-council:docs/align/council-2026-11-05/FINAL-DESIGN.md`
  (sections 2.1, 2.2, 2.6, 2.8 and V8), and `.../FINAL-DESIGN-AMENDMENT-1.md` on the same branch;
  `docs/align/r0_step_test_ruling.md` and `docs/align/smc_temperature.md` in the worktree.
- Real capture (R0 re-run 7, 2026-11-07): /Users/edr/night-align/r0-v4-20261107T0810Z/smc/r0.json
  (inventory, phases, started, finished, quiet_observations) and samples.jsonl (1,800 rows, 403 keys,
  1 Hz; `values.sensors[key]`). Profile: 300 s idle, 900 s GPU load (MLX float32 2048x2048 matmul),
  600 s recovery. The idle phase began right after R0's memory check, which loaded the machine with
  a 30B model for about 12 minutes.
- Python: /Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python,
  run with `-B -P` and PYTHONPATH=/Users/edr/code/jw-wt/r0-smc-cov. Check `module.__file__` points into
  the worktree. Never `cd` inside a compound command.

## What is known (verify it yourself before relying on it)
With per-phase coverage counted at one reading per 1 s cell, `rank` gives 16 die keys, 141 heatsink keys
and 246 record-only keys, and picks s_fast=Tg2I and s_slow=TaRT. Reviewers found that these picks are
artifacts:
- All 16 die keys are `Tg*` GPU keys. They read a fixed sub-zero value (e.g. -2.75 degC) on about 95% of
  idle samples and drop back to it within two samples of recovery. This looks like a power-gated
  placeholder.
- The heatsink keys were still cooling through idle. TaRT's rise at 50-60 s is 0.06 degC against a noise
  floor of 1.14 degC.
- The CPU-cluster keys TCMb, TCDX and TCMz respond cleanly (t63 18-26 s, tau 16-27 s) but fall between
  the die class (t63 <= 5 s) and the heatsink class (30 s < tau <= 300 s), so they are record-only.

## Questions
1. What do s_fast and s_slow have to do at window time? Answer from the code and design text. That
   need, not the current class thresholds, should drive the amendment.
2. Rejecting placeholders: what observable rule (from the data) separates a power-gated placeholder
   series from a temperature? Replay it over all 403 keys and list what it removes.
3. Idle baseline: what settle criterion, or pre-idle dwell, makes the baseline valid? Derive it from
   this capture's cooling curves. State the cost in seconds of R0 time.
4. Classes: given this Mac's measured responses, what class boundaries (or what different load step)
   yield picks that serve question 1? Run your proposed rule through the real `rank` path (a patched
   copy in your scratch dir is fine) and report the counts and picks.
5. The receipt: `r0_host` re-checks picks against a capture-wide coverage block at a 100 ms tolerance.
   Say what it should read instead.

## Rules
- Every threshold you propose carries its derivation: from the physics (sensor quantum, sample period,
  measured tau and noise) or from the printed precision. No number without a derivation. A number you
  cannot derive: say "measure first" and name the measurement.
- Execute: every claim about the data comes with the command you ran and its output.
- Decide what the code and design text determine, and list those as "decisions I made". NEEDS_RULING
  only for choices that change which sensors count.
- Write only in your scratch directory (given in your launch line). Do not edit the worktree, push,
  comment on GitHub, or start any measurement.

## Output
A proposal: a short rule text the code could implement, its derivations, its replay results on the real
capture (counts, picks, what each new rule removes), and what to verify in the next R0 run.
