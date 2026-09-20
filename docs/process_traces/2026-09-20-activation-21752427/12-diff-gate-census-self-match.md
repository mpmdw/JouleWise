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

## §4 Replay tail (row 9)
(pending)

## §5 Terminal review (row 12)
(pending)
