# Magistrate terminal review — G2A-CHAIN-ROUTING-01 (interactive magistrate, 2026-09-08 ~03:05 PDT)

Merge candidate: branch `feat/2026-09-08-g2a-chain-routing`, head named in the PR ledger row 12. Series on top of
main e4ce8b3b: f0fedc91 landing (Astra high, resumed once for driver scope) → 3e016b04 fix round 1 (Astra medium,
Opus B1-B3, N1-N3; resumed once for the generator test's fence range) → trace commit.

## Why this exists
The readiness scout (trace 27 §1) showed the generated G2-a chain and its preflight hard-coded the protected August
measurement checkout and the development interpreter, so no honest v2 night plan could pin its own measurement
root. After this series the v2 plan is the one source of `measurement_root`, `measurement_head` and the derived
interpreter; the driver's `_run_chain_once` exports them from the parsed plan (plain assignment, overriding any
inherited environment), the emitted chain's first block refuses on missing/relative root, head mismatch or a
missing venv interpreter, and the preflight re-derives the same three values from the plan file with `/usr/bin/jq`.

## Gauntlet record
| Layer | Seat | Report | Unique catches |
|---|---|---|---|
| Implementation | Astra high | 31 | — (NEEDS_SCOPE for the driver, approved) |
| Execution refuter | Astra medium | 35 | none; real-clone probes, head-mismatch and missing-interpreter refusals verified; literal mutation killed |
| Contract refuter | Opus | 33 | B1 BLOCKER: `tests/test_check_window_provenance.py` still pinned the retired preflight contract (suite red, invisible to the three-module acceptance); B2 desk path lost its exports; B3 sibling docs stale; N1-N3 |
| Fix round 1 | Astra medium | 37 | — (NEEDS_SCOPE for the moved fence range, approved) |
| Delta re-audit | Astra medium | 39 | R1 should-fix: the re-expressed B1 test is string-based; two hypothetical mutants (two-positional normalisation; NIGHT_PLAN env fallback) survive |

## Lead triage of R1 (findings are dispositioned, never silently applied)
ACCEPTED AS FOLLOW-UP, not fixed in this series. Reasons: (a) the finding is about the STRENGTH of a test, not a
behaviour of the code; the preflight at HEAD has exactly one positional argument and no env fallback, and N1's
subprocess tests exercise the real program for the no-argument and head-mismatch refusals; (b) a second fix round on
the same finding is a rule-11 cold-gate trigger, and spending a cold gate on a test-strength nit is not proportionate
to the cost of being wrong; (c) the follow-up (two executable refusal assertions: two positional arguments → refuse;
zero arguments with `NIGHT_PLAN` populated → refuse) is registered in the queue row for this lane and is bench-sized
for the next touch of `preflight.sh`.

## Apex code-reading gate (from `git diff e4ce8b3b <head> -- scripts/`)
1. `scripts/run_night.py` gains four lines in `_run_chain_once`: the child environment is a copy of `os.environ`
   with `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD`, `PY` (derived `$MEASUREMENT_ROOT/.venv/bin/python`) and the plan
   id assigned unconditionally from the parsed plan. Ordering relative to the zero-agent census is unchanged: the
   census runs inside `evaluate_night` before `_run_chain_once` is reached (Opus 33 Q3); `joulewise/` is untouched.
2. `scripts/gen_g2_phase_d.py`: the emitter now inventories the runsheet's `## Plan-derived measurement variables`
   block as the first (routing) block, pins its range, and `--check` renders the chain and prints a `FAIL` line
   (not a traceback) when the heading is missing. The historical block is byte-identical and marked superseded.
3. The refusals in the routing block and the preflight fire before any `mkdir`, custody write or interpreter
   execution (Opus 33 Q2 table).
4. Overbuild: none. Two behaviour changes ride along and are entailed by the clone recipe (detached-HEAD
   requirement replaces the branch-count census; `REVIEWED_HEAD` env requirement dropped); both tested.

## Live verification (lead-owned)
- The four touched modules run unpiped at the bench on f0fedc91 (74 OK) and 3e016b04 (OK, rc from the process).
- Full-suite replay on the merge candidate: ledger row 9 names the log and tail (queued behind the census replay).
- NOT exercised: a real G2-a night. The first real arm still needs the `_v5` measurement clone created by the
  documented recipe and a reviewed head; that is the next lane, not this PR.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded.
