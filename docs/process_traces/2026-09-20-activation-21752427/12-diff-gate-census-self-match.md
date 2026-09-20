# Record 12 — magistrate diff gate and bench verification: CENSUS-SELF-MATCH-01 (`fix/2026-09-20-census-self-match`, head `7472a7c7`)

## §1 Diff gate (rows 7 and 8; every production hunk read, 04:25 PDT 09-20)

Head `7472a7c7` = one commit over main `e1e7d6a7`; 13 files, +106/−18 plus the new 198-line `tests/test_agent_census_concurrency.py`. Production delta is three hunks:
1. `joulewise/night_gate.py:88-90`: `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")` with a two-line comment naming the 09-20 self-match. `agent_census`, `_check_census`, refusal reasons, ancestor handling: unchanged.
2. `joulewise/arm_readiness_evidence_t0.py::_derive_process_census`: the duplicated literal becomes the shared constant, imported inside the function (the module's public namespace is closed; the same in-function import pattern `arm_readiness.py:10024` already uses).
3. `scripts/gen_derivation_night.py:66`: comment only; `CENSUS_SUBSTRINGS = ("codex","claude","t3")` and its refusal are untouched — correct, because the bracketed regex still matches a plan id or root carrying the words.
`docs/process/NIGHT_HANDBACK.md`: the current-pattern sentence plus a four-line rollout note (all producers at or after the fix; fresh artefacts because `MANIFEST_PATHS` hashes `night_gate.py`); history blocks untouched by the diff (refuters 10/11 confirm byte-identity).

Design-level answers:
- **Does the cure change the census population?** No. `[c]odex` is the one-character class `c` followed by `odex`, identical to the literal for every command line except one that contains the bracketed text itself — i.e. a peer census. Bench proof at 03:50 PDT: 300 overlapped runs, old pattern 300 peer hits, bracketed 0; the bracketed pattern still listed this session's `codex mcp-server` and the `~/.claude/shell-snapshots` shells (legitimately forbidden during acquisition).
- **Is post-filtering avoided?** Yes — no hit is discarded; the evidence recorded in receipts is the raw pgrep output as before. This was the deciding property against option B (consult 03).
- **Every producer covered?** Driver, `_binding_census`, quiet-admission per-round census, arm discovery and the watchdog all derive from the constant by import (seat 05 report; refuter 10 Q2 re-verifies by executed import). The t0 author was the one duplicate and is now centralised. `night_agent_install.py:983` is a label/plan pattern — out of scope, correct.
- **Overbuild / prune:** none. The native module (three tests, skip when pgrep is sandboxed) is proportionate: it is the only executable proof of the concurrent form, and it carries an old-pattern control that refuses to pass vacuously.
- **Open question deferred to refuters:** `tests/test_night_gate.py:1224` aligns the differential "baseline" engine's constant to the production one; whether that masks a receipt-semantics difference is refuter 10 Q4 / Opus R3.

Verdict of the diff gate: MERGE-able pending refuters 10 (execution) and 11 (contract) and replay 09.

## §2 Bench verification (rule 1: the lead's own runs, unpiped tails)

Native module at the bench (real pgrep), cure worktree at `7472a7c7`:
```
PYTHONDONTWRITEBYTECODE=1 …/.venv/bin/python -B -m unittest tests.test_agent_census_concurrency -v
test_owned_agent_markers_are_still_listed … ok
test_stopped_peer_is_excluded_after_exec … ok
test_synchronized_peer_censuses_do_not_match … ok
Ran 3 tests in 47.890s
OK
```
Seat 05's two focused-run failures (`BindSupervisionProcessTests` journal_block / startup_hang, 8 s supervision watchdog) re-run alone in the cure tree: `Ran 22 tests in 31.203s OK` — load-induced timing inside the seat's serial 800 s run, not the cure. The quick-tier module it named (`tests.test_axi_controller_events`) at the bench: main tree `Ran 7 tests OK`, cure tree `Ran 7 tests OK` — sandbox-environmental in the seat, not present at the bench.
Seat 05's counterfactual (V2): with the old constant patched in, `test_census_does_not_match_peer_argv` and `test_peer_census_reaches_and_completes_chain` both FAIL; with the production constant both pass — the regressions are defect-shaped.

Full sharded replay (row 9): record 09 (`replay-09/full-replay-7472a7c7.log`), running at the time of writing; tail appended below when done.

## §3 Fix contract (row 3) and same-signature statement (row 5)
Fix contract = brief 05 (dictated closure shape from consult 03: one constant, no filtering, t0 author centralised, regressions that fail at the old constant, native tests with an old-pattern control). Seat 05 implemented it in one round; no fix round so far. Same-signature statement: the class "two owned censuses match each other" is closed for every producer that imports the constant; the residual, legitimately-forbidden matches (courier binary path, agent shell snapshots) are real agents during acquisition and are not false positives (refuter 10 Q8 rules on any remaining owned-process false positive).

## §4 Replay tail (row 9) — full sharded replay at `7472a7c7` in the branch worktree, untouched during the run (04:15–05:01 PDT)
```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p …/.venv/bin/python -B scripts/shard_tests.py --workers 4 --split
SHARD SUMMARY index=1/4 modules=61 tests=1373 failures=0 errors=0 skipped=3 result=PASS
SHARD SUMMARY index=2/4 modules=61 tests=1857 failures=0 errors=1 skipped=12 result=FAIL
SHARD SUMMARY index=3/4 modules=62 tests=1836 failures=0 errors=0 skipped=6 result=PASS
SHARD SUMMARY index=4/4 modules=63 tests=1548 failures=0 errors=0 skipped=82 result=PASS
WORKERS SUMMARY shards=4 modules=247 tests=6614 failures=0 errors=1 skipped=103 failed_shards=2 result=FAIL
real 2761.28
```
The one error: `tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect` (pattern `powermetrics|window-chain|run_campaign|tail -f|(^|/)watch( |$)`) — `ValueError: invalid literal for int() … 'SESSION_MODE:'` at `tests/test_arm_readiness_evidence_t0.py:2750`: the test parses every real `pgrep -lf` output line as `<pid> <command>`, and a concurrently running Codex seat (refuter 10, launched by this activation with the whole brief as one process argument) had a MULTI-LINE command line containing the word "watch"; its continuation lines have no pid. Environmental pollution by the lead's own seat launches, not the cure: re-run alone after the seats exited → `Ran 1 test in 1.469s OK`. (Finding for the successor: launch seats so the brief is not a process argument, or never run real-pgrep replays while a seat with a multi-line argv is alive.) Full log: `/tmp/magistrate-21752427/replay-09/full-replay-7472a7c7.log` (9,953 lines). The production delta between `7472a7c7` and the final head `0b3d69b8` is empty (rounds 1–3 touched tests and the handbook only); the touched test modules were re-run alone at `80e715ba` (78 + 228 OK) and `70637c31` (78 OK), and the native module at `0b3d69b8` by the auditor (3 OK).

## §5 Terminal review (row 12), 05:05 PDT 09-20
Final code head `0b3d69b8` = `7472a7c7` (cure) + `80e715ba` (round 1: pgrep-naming foreign-agent control that kills the post-filter mutant; handbook; native rounds 300; test name) + `70637c31` (round 2: performable pre-arm check; nits) + `81824ea7` (round 3, consult-derived: watchdog mechanism corrected — a 300 s launchd interval job whose ticks re-import from the canonical checkout; only a resident supervisor is stale; pid from `state.json`) + `0b3d69b8` (the auditor's two precision nits applied verbatim). Gauntlet: consult 03 (Astra xhigh) → seat 05 (Astra xhigh) → bench native proof → refuter 10 (Astra xhigh, execution: no blocker; mutant table; F1 coverage gap → closed in round 1; F2 pre-existing watchdog false hold on the driver's `--courier-bin` path → separate lane) + Opus 11 (contract: FIX-FIRST on the rollout note → rounds 1–3) → fresh eyes 13 (round 1: mutant killed) → fresh eyes 14 §1 (round 2: FIX-NEEDED, same signature → consult) → consult + bench → round 3 → fresh eyes 14 §5 PASS, same-signature class CLOSED → replay §4.
Verdict: MERGE the records-only candidate (merge of main onto `0b3d69b8`). Residuals carried, not blockers: (i) OPERATIONAL PRECONDITION for the next arm — the canonical checkout `/Users/edr/code/JouleWise` (fenced for this activation; the watchdog ticks import from it) must contain the merged fix, and no resident supervisor older than that move may be alive at arm time — Ed's action or an unfenced activation, verified per the handbook's check (a)/(b); (ii) refuter 10 F2 (driver's courier path matches the census from an independent producer → false `HOLD_CENSUS`, never fatal) → successor lane; (iii) Opus 11 R6 (`arm_readiness.py:10149` on a pre-fix `TRANSACTION_PACK` GO census) → nit for that lane; (iv) arm scripts re-authored with the bracketed pattern single-quoted; (v) `envelopes_attempted: 0` bookkeeping after a first-envelope interruption (seat 05 residual) → nit.

## §6 Hosted checks on the PR head (row 11)
First head (candidate `a64cf4af`, 05:03–05:20 PDT): build / changes / fences / gate-ledger / installed-wheel / quick / both calibration-writer-crash shards PASS; `test (3.13, 5)` FAIL; shards 1/2/3/6 cancelled by fail-fast; shard 4 pass. The failure (job 106075250385, log `/tmp/magistrate-21752427/pr371-shard5.clean.log` lines 860–927) is confined to `tests/test_agent_census_concurrency.py::test_synchronized_peer_censuses_do_not_match`: both `multiprocessing` "spawn" workers died at startup with `FileNotFoundError: … '/home/runner/work/JouleWise/JouleWise/<stdin>'` from `multiprocessing.spawn._fixup_main_from_path` — the hosted shard runner feeds the test program to Python on stdin, so spawn cannot re-import `__main__`. The module's other two tests behaved as designed on Linux (`test_owned_agent_markers_are_still_listed` ok — real pgrep works there; the Darwin-only stopped-peer test skipped). Not the cure: a portability defect of the new native test's process-start method.

## §7 Fix round 4 = `d11ab811` (test only, one hunk): workers use `multiprocessing.get_context("fork")` where "fork" is available (Linux and macOS), else "spawn"; the workers only exec pgrep, so a forked child is safe. Bench (05:22 PDT): module `Ran 3 tests in 13.719s OK`; the CI shape reproduced with the program on stdin (`python -B - <<EOF`) → the single test `Ran 1 test in 13.607s OK` (it had no way to fail this way before the fix on macOS because the bench ran unittest from a file, which is why the replay and three fresh-eyes passes did not see it). Fresh-eyes 15 audits the round; the PR head is now `d11ab811` (row 12 updated in the PR body; `check_gate_ledger` 12/12). Second hosted pass is recorded here before merge.
