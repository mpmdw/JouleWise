# Bench verification of fix round 1 (lead, 2026-09-18 22:30–22:32 PDT)

Worktree `/Users/edr/code/JouleWise-wt-harness-232`, branch `feat/2026-09-18-quiet-predicate-evidence-harness`, seat diff over `d066d271` (two in-scope files only; +332/−19), committed by pathspec as `05e90616` and pushed.

Executed evidence (this session):

```
python3 -B -m unittest tests.test_sample_quiet_predicate_evidence
Ran 41 tests in 5.147s
OK
python3 -B /tmp/mag-507514d5/mutations.py alignment   -> MUTATION alignment run 41 failures 6 errors 4
python3 -B /tmp/mag-507514d5/mutations.py observer    -> MUTATION observer run 41 failures 5 errors 4
python3 -B /tmp/mag-507514d5/mutations.py cores       -> MUTATION cores run 41 failures 4 errors 4
pgrep -fl sample_quiet_predicate_evidence | wc -l      -> 0
```

At `d066d271` the same three mutations survived all 31 tests (record 02, V2–V4). The bench counts differ from the seat's (2/1/1 failures, 0 errors): the seat applied the mutations through an in-memory loader (its flag F2), the bench ran the refuter's runner with its sibling mutation files (`02a-*.py`) so the real-subprocess tests also see the mutated module and error out. Either way every mutation is killed; the delta re-audit (record 04) is asked to confirm and to explain the error rows.

Ruling on the seat's blocking flag F1 (lead, not a process rule): the brief's 0.1-core cap stands while a night is armed; 0.1-core coverage is accepted for this round and the 0.2-core case is a deferral for the successor to run on an unarmed machine (or to drop, if the 0.1 case with the 500 ms period is judged sufficient by the memo's reviewers). Seat flag F3 (achieved 0.058 cores for a 0.1 request at 100 ms period; regression uses 500 ms periods, tolerance 0.04 absolute) is a limitation carried into the evidence memo's observer/load section.

Diff read at the bench (production file): per-round `censuses`/`census_errors` gathered from the smoke round's concurrent census tasks; `census_condition` maps hit → False, no census → None, malformed/incomplete → None, all-absent → True; `summarize` groups by `(state, repeat, census_clean)` and keeps references per condition; JSON summary carries `evidence_status`, `alignment_model`, network-time provenance and `status: no_rounds` for the empty case; journals confined under `--out` via a scoped `tempfile.TemporaryDirectory` replacement. Open question passed to the re-audit: the census exit-code semantics (0+stdout = hit, 1+empty = absent) must match the production census.
