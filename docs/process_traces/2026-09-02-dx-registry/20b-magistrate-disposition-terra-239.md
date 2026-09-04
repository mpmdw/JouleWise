# Delta re-audit 3 (terra xhigh, 239, file 20) — magistrate disposition 2026-09-02

`VERDICT: SHOULD-FIX 1`. Contract arithmetic (181 + one per placed literal + 3
replay identities; 184/181 at zero placement, 200/197 at 16) confirmed by an
independent synthetic placement; AS-branch flattening confirmed by an
independent probe; `R7F_CORPUS_ROOT` isolation confirmed; scope clean.

| Finding | Disposition | Where |
|---|---|---|
| SF2-CONTRACT — the round-3 docstring promises `R7F CORPUS UNAVAILABLE: <resolved path>` but both producer-exit-3 branches (`:900-902`, `:929-930`) emit the flattened producer message through `_producer_unavailable_message` (`:837-841`); the grammar is false for that branch | ACCEPTED, bench (doc-only, two sentences): `<detail>` is the missing resolved path from this script's own preflight, or the producer's flattened stdout+stderr when a producer exits 3. No code change; the executed-path regressions (`tests/test_paper_round7_artifacts.py:619`, `:859`) already pin both forms. | bench commit on this branch |

Rule-11 check: this is a defect INTRODUCED by fix round 3 (the round-3
sentence over-specified what the round-2 sentence under-specified), cured
once; it is not a second fix of the Opus SF2(a) finding (the resolved-path
sentence stands and is true for the preflight branch). No same-signature
trigger across rounds: Opus SF2(a) = "does not say resolved"; terra = "says
path where a message can appear". The fresh pass on the final head (a
different model) reads this sentence again.

Executed at the bench this session, after the edit: the four non-replay
classes `Ran 44 tests`, `OK`; `python3 scripts/check_paper_round7_artifacts.py
--literals-only` → `R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0`.
