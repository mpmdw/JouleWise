# Magistrate terminal review — decode-identity merge candidate (gate ledger items 7, 8, 9, 10, 12)

Candidate: `fix/2026-09-02-decode-identity-set` at `f753daeb16459805084378daa1eed087aaca81cd` (main `8ed652f7` merged in at f753daeb; trace custody commits after). Session `joulewise-60` → "Paper experiment loop" (same context), 2026-09-03 23:50 PDT.

## Item 7 — apex code-reading diff gate (design-level)
Read at the bench, in full, the two rewritten contract sections (§Analysis-gate definitions :583–645, §Analysis consumption :646–737) at 3903696c and the eight counter-review hunks after it. Design questions answered: (a) does the paragraph state the mechanism a reader can rebuild — yes: the eight hops in execution order with the code each emits, tag gating, the completion policy, the direct-call label, and the pack-digest framing deferred to the one exact statement (step 2); (b) is any term used before it is built — no, after the alias declaration was moved to first use and 'runs root', 'pack digest', 'file modes/content digests' were glossed; (c) does the contract now name the modules it describes as authoritative — yes (status clause extended to `arm_readiness.py` and `analysis_engine/inputs.py`). Behavioural truth rests on execution: 28/28 probes (file 51), re-executed by the fresh pass (54: 23 hops on a real settled lineage) and the counter-review (57).

## Item 8 — overbuild / merge-ability prune
Counter-review (57) charge (4): 85 files vs merge-base, no strays; every path belongs to a scoped round (code: identity_pins.py, analysis_engine/, detection_floor.py; tests; the two trace dirs; four doc/contract files). The fresh-fable-audit files 01–05 (custody from the 2026-09-02 pause) land with this PR by design. Nothing to prune.

## Item 9 — full-suite replay on the integration tree
Unpiped `R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` at f753daeb (= 3903696c + origin/main 8ed652f7), log `<job>/tmp/decode-id-replay-f753daeb.log`:
```
Ran 4880 tests in 6837.779s
FAILED (failures=3, skipped=125)
```
The three failures, each re-run in isolation at the same head:
- `test_calibration_exits.PublicGovernedExitWitnessTests.test_logical_producer_delay_preserves_exact_evidence_bytes` (two artifact subtests) — PASS in isolation on the branch (`Ran 2 tests in 76.476s`, only the node test failed) and PASS on main in isolation (`Ran 1 test in 58.072s / OK`). The replay ran with four other full suites concurrently (114 min wall); CI runs this module as an exclusive job. Load flake, not a defect of this branch.
- `test_node_worker_subprocess.NodeWorkerSubprocessTests.test_real_client_worker_artifact_contract_over_localhost` — FAILS in isolation on the branch AND on main (0f80c98a) on this machine ("missing or malformed status.json"); pre-existing/environmental, not touched by this branch; queued for a main-side look.
The prose-only commits after f753daeb (58, 59) change no code; the contract-reading modules were re-run after 53 (`tests.test_analysis_inputs tests.test_arm_readiness_lifecycle` → 84 OK, skipped=4) and after 57 (`tests.test_analysis_inputs` → 18 OK).

## Item 10 — fresh-eyes after every post-review commit
Post-review commits: 53 (bench cures, checked by the delta 55), 56 (checked by the counter-review 57 charge 1), 58 (three one-line cures, each a verbatim closure of 57's SF1/N1/N3, re-read at the bench; no behavioural clause changed).

## Item 12 — magistrate terminal review of the exact merge candidate
Final head `f753daeb16459805084378daa1eed087aaca81cd`. Merge candidate reviewed in full session context: the gauntlet ran four fix rounds, one consult (files 38/40–42/44), one cold gate (45–48), formulation 4 (49–51), a fresh pass (54), a delta (55) and an Opus counter-review (57); every finding is closed or recorded as a kernel row (LINEAGE-RESOLVE-RACE-01, ONE-USE-CONSUMPTION-TEST-01 — registered on main 14f89811). Disposition: MERGE after CI green on this head.
