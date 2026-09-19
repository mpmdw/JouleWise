SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (read-only, EXECUTION lens) — lane QUIET-PREDICATE-EVIDENCE-01 (kernel 232) sampling harness, head `d066d271` vs base `7faaf2d0`

Cwd is a detached read-only worktree at `d066d271`. Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch. No network, no `sudo`, no `powermetrics`, no live `collect` with power capture. A measurement night is armed on this machine for 00:00 PDT: every process you start must end inside 60 s, keep any load experiment to `--cores 0.1` and `--duration-s 20` at most, and verify with `ps` that nothing you started survives. Set `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp` and `-B`; `pytest` is absent on the canonical 3.14 interpreter, use `python3 -B -m unittest tests.test_sample_quiet_predicate_evidence`. Never run the canonical `python3 -m unittest discover`.

## What you are refuting

`git diff 7faaf2d0 d066d271` adds `scripts/sample_quiet_predicate_evidence.py` (desk harness: `collect` / `load` / `summarize` / `_sample`) and `tests/test_sample_quiet_predicate_evidence.py` (31 tests). The contract lens is a separate seat; you are the execution lens: does the code do what it says when run, and do the tests prove it rather than pass blind.

## Execution lens — answer each with evidence (commands, outputs, file:line)

E1. Run the 31 tests. Then for each of the three subcommands, name the test that exercises the real code path end to end (real subprocess, real pipe, real file) versus tests that only exercise a mock. A subcommand whose only coverage is mock-level is should_fix.
E2. Blind-pass check: pick the three assertions that carry the most weight (alignment bound, observer cost accounting, load generator core fraction) and, in `/tmp` copies only, break the production behaviour they guard (e.g. return arrival time instead of the anchored time; drop the reaped-children CPU from the observer sum; ignore `--cores`). Report which tests fail for each break. A break that no test catches is should_fix; the alignment one is blocker.
E3. `load`: run `python3 -B scripts/sample_quiet_predicate_evidence.py load --cores 0.1 --duration-s 15 --period-ms 100 --qos background --profile scalar --seed 1 --log /tmp/load.json` and measure the achieved CPU share with `ps -o %cpu` or the log's own accounting; state the requested vs achieved fraction, whether the requested QoS is applied (`taskpolicy`/`ps -o` where observable), and that all load processes are gone afterwards (`pgrep -f sample_quiet_predicate_evidence` empty).
E4. `collect` without root: run it with `--no-power --duration-s 5 --sample-interval-s 1` (or the smallest legal values) to a `/tmp` out dir. It must either produce rows with `status`/`error` explaining what could not be captured, or refuse with a clear reason. A traceback is should_fix; a row that looks complete while power was not captured is blocker.
E5. `summarize`: run it over the E4 output and over an empty directory. Confirm the empty case is a reasoned null, not a crash, and that the summary carries the PROVISIONAL label and the reference-state name.
E6. Cleanup and residue: after E3–E5, list any file the harness wrote outside its `--out`/`--log` targets and any process left alive. Either is should_fix.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; `verdict` = `{counts, findings}` only; JSON header under 8000 bytes; all evidence in the markdown body. Severity vocabulary: blocker / should_fix / nit. For every finding give the counterfactual input and the production call site or CLI invocation that shows it. If you find nothing, say so with the commands that would have found it.
