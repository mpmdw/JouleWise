# Opus counter-review (file 19, PR #272 @ 73f7fcc2) — magistrate disposition 2026-09-02

Opus report verdict: `SHOULD-FIX 2`, `NIT 4`; "What I would not merge as-is:
nothing". Nothing is applied silently.

| Finding | Disposition | Where |
|---|---|---|
| SF1 — the R7F tail pinned as a constant (`fill-checklist.md:24-28` "exact successful full-replay tail `R7F COMPARED 184 / MISMATCHES 0`"; tests `:797-801`, `:850`, `:861`, `:263-269`) is placement-dependent: a correct 16-marker fill batch yields `COMPARED 200` (Opus probe P-C: `R7F PLACED 16/16, LITERALS-ONLY COMPARED 197 / MISMATCHES 0`) | ACCEPTED IN TWO HALVES. Checklist half: bench edit on this branch stating the tail as `181 + one comparison per placed DX literal (+3 in full replay)`, with the rule that the batch PR restates the exact tail before and after. Test half: DEFERRED to the DX fill-batch PR, which must rewrite the zero-placement census pins in the same commit that places the markers (the pins are the "before" tail that the batch's brief cites; deriving the count in the tests would weaken the fixed-point pin the fence exists to hold). Opus's own placement: "cured before the DX fill batch is executed, not before merge". | bench commit (checklist); fill-batch brief |
| SF2(a) — fence contract (`:13-15,20`) says `<path>` without saying the path is RESOLVED; a consumer written from `--help` asserts the as-given root and fails across a macOS symlink (the c8ea9e95 defect at a new site) | ACCEPTED: `<resolved path>` + one sentence at `:20`. | luna fix round |
| SF2(b) — producer-exit-3 branches (`:888`, `:915`) put an un-flattened producer message after `R7F CORPUS UNAVAILABLE: `; single-line only by the producers' manners; no test asserts the resulting line | ACCEPTED: flatten with the `_producer_failure` idiom via one helper at both sites; regression with a two-line stub producer; counterfactual executed. | luna fix round |
| NIT1 — identity rows' declared supplier fields navigable-only (`XD.replay_command = 12345` → `rc=0, 181/0`) | RECORDED, no change: provenance strings, not paper numbers; inside the D-161 prune. The registry wording "bound to" is accurate for the pin (the digest binds the bytes), not for the type. | this file |
| NIT2 — refusal-bucket list elements counted, not typed; DX-021's third declared ref discarded (`:456`) and `AQ#summary.population_size` read undeclared (`:466`) | RECORDED, no code change: the key-set check at `:459-462` carries the claim; the registry is bench-only and a fourth declared ref would change the `len(values) == 3` rule. The docstring is corrected (NIT4) so the fence's reading is stated, not hidden. | this file; luna fix round (NIT4) |
| NIT3 — `CORPUS_ROOT` hardcoded machine path, no env escape (`R7F_REGISTRY` convention exists two lines above); replay costs ~8 min in every local full-suite run; module absent from `scripts/test_timings.json` | ACCEPTED for the env override (`R7F_CORPUS_ROOT`) + docstring sentence; the timing map is CI-measured (its provenance header) and the replay skips on CI, so it is NOT hand-edited. | luna fix round |
| NIT4 — docstring `:3-5` overclaims the registry as the single field-path source | ACCEPTED: one parenthetical naming the `derived_refused_counts` read. | luna fix round |

Rule-11 check: SF2(b) is the first edit to the producer-exit-3 branches on
this lane; SF2(a)/NIT3/NIT4 are doc/env edits. The c8ea9e95 bench commit
touched the TEST side of the resolved-path contract; SF2(a) states the
contract on the FENCE side — same subject, but a documentation clause, not a
second cure of the same defect (the defect was a test symlink hazard, cured
once). No same-signature trigger. Fix round: luna high; delta re-audit by a
different model.

Executed at the bench this session: `git status --porcelain` on
`JouleWise-wt-dx` empty before the fix round; `R7F-DX-PROSE-SCAN-01` absent
from the kernel (120 tasks) — that row is applied in the post-merge kernel
batch. SF1's test-half home is the checklist sentence itself (the fill-batch
operator reads the checklist; a kernel row for the batch does not exist yet
and is registered when the batch is briefed).
