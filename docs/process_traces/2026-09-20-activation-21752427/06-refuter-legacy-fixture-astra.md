```json
{"schema":"claude-codex-report/v1","genre":"review","status":"clean","completion":"complete","summary":"Fix confirmed; baseline neighbours fail.","workspace":{"base_requested":"d5f35ca1","base_mode":"exact","head_start":"d5f35ca1","head_end":"d5f35ca1","upstream_end":"d5f35ca1","branch":"fix/2026-09-20-legacy-fixture-linux"},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[]},"verification":[{"id":"V1","kind":"other","cmd":"/opt/homebrew/bin/python3.11 -B /tmp/fixture-linux-refute-9ekbshmi/check_evidence.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["REVIEW_EVIDENCE_OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}}],"flags":[{"id":"E1","kind":"verification_gap","level":"nonblocking","text":"Baseline census/timeouts fail.","needs":""}]}
```

## Findings

No blocker, should_fix, or nit attributable to `d5f35ca1`. Repository unchanged; final HEAD and upstream remain `d5f35ca1`.

Tests ran in `/tmp/fixture-linux-refute-9ekbshmi/checkout`, populated from `git archive d5f35ca1` with disposable Git metadata. [Replay driver](/tmp/fixture-linux-refute-9ekbshmi/run_modules.py), [recorded results](/tmp/fixture-linux-refute-9ekbshmi/results.jsonl).

| Execution | Result |
|---|---|
| `/usr/bin/true` counterfactual, Python 3.13 | 65 tests; **12 assertion failures** |
| Fixed fixture, Python 3.13 | **65/65 OK** |
| Fixed fixture, Python 3.11 | **65/65 OK** |
| Both grep-selected neighboring modules, Python 3.13 | 304 tests; 4 failures, 2 errors, 9 skips; qualifications below |

1. **Counterfactual confirmed.** All 12 failures contain exactly: `night wrapper is not valid UTF-8: 'utf-8' codec can't decode byte 0xca in position 0: invalid continuation byte`. This reproduces the refusal class using this Mac’s binary; it does not reproduce the Linux-specific byte offset. [Counterfactual log](/tmp/fixture-linux-refute-9ekbshmi/counterfactual.log).

2. **Guard confirmed.** Creating a non-UTF-8 file before `_write_plan` raises:

   > True is not false : Legacy fixture chain must be absent (2026-09-20 CI: night wrapper is not valid UTF-8): /private/tmp/tmp7207jyun/legacy-missing-chain.zsh

   Directories and symlinks to existing binaries also trigger it. Two executed `setUp` calls produced distinct roots; another 256 fresh temporary directories produced no sentinel collisions. `tests/test_install_night_agent.py:68–69` creates and resolves a fresh directory per test. Receipt preparation was executed: it changes the plan to `custody/probe-chain.zsh`, leaves the sentinel absent, and permits another `_write_plan`. No legitimate sentinel producer was found. [Guard/path probes](/tmp/fixture-linux-refute-9ekbshmi/probes.log), [fixture transition](/tmp/fixture-linux-refute-9ekbshmi/transition.log).

3. **Path behavior checked.** Missing chain paths through both `/tmp` and `/private/tmp` aliases rendered successfully. The observed canonical path was 49 bytes, below the host’s limits. A dangling symlink has `exists() == False`, passes the guard, and renders successfully because reading its target fails. Creating a binary target afterward causes installer exit 2 with the UTF-8 refusal. Under ordinary Linux/macOS filesystem semantics, a fresh directory does not acquire this child merely because of the platform; another writer is required. Actual Linux execution remains unverified.

4. **Remaining executable-path fixtures identified.**
   - `tests/test_magistrate_watchdog_cli.py:198` still sets `chain_path="/bin/true"`. Substituting `/usr/bin/true` at runtime exercised four plans across **three passing tests**. It did not reproduce the wrapper refusal. [Executed probe](/tmp/fixture-linux-refute-9ekbshmi/watchdog.log).
   - `tests/test_night_agent_install.py:547` and `:1306` contain `/bin/true` in courier arguments, rather than `chain_path`. Their module was included in the neighboring run.
   - The complete `/bin/` and `/usr/bin/` search is retained in [path census](/tmp/fixture-linux-bin-paths.txt).

5. **Neighbors executed.** The requested helper search selected `tests.test_night_agent_install` and `tests.test_run_night`. Both ran to completion on 3.13; they were **not wholly green**. See E1 below.

6. **Same-signature conclusion.** The exercised installer helper’s platform-existing binary defect is closed. Repository-wide elimination of host-file placeholders is **not** established: the watchdog fixture survives, although its executed binary substitution passes. No UTF-8 refusal appeared in the fixed module or neighboring failure diagnostics.

## Residual risk

**E1 — neighboring verification remains qualified.** [Full neighboring log](/tmp/fixture-linux-refute-9ekbshmi/neighbors313.log):

- `LaunchdAccessProbeTests.test_cleanup_refusal_reports_the_failure_it_interrupted` fails at `tests/test_night_agent_install.py:1866` because real `pgrep` reports `sysmond service not found` / `Cannot get process list`. It reproduces with the pre-fix helper and on 3.11. Injecting an explicit absent-census result makes this isolated test pass.
- Three `BindSupervisionProcessTests` fail with the eight-second external-watchdog signature: `test_blocked_journal_never_blocks_deadline_or_grants_go`, `test_blocking_join_startup_and_post_publication`, and `test_startup_hang_is_nonblocking`. All three reproduce with the pre-fix helper restored. Their underlying cause was not resolved. [Baseline replay](/tmp/fixture-linux-refute-9ekbshmi/supervision-baseline.log).
- Two errors were caused by my scratch repository lacking historical objects `3e4acc59` and `a90ab4e8`. After copying and byte-verifying the required commit/tree/blob objects into scratch, **both affected tests passed**. [Focused replay](/tmp/fixture-linux-refute-9ekbshmi/history-replay.log). The full neighboring suite was not repeated afterward.

Execution was on Darwin arm64, not hosted Linux; nine neighboring tests were skipped. Next exact step: lead reruns the affected Linux CI shard and separately adjudicates the four baseline neighboring failures.