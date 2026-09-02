WRITE_SCOPE: ["scripts/check_paper_round7_artifacts.py","tests/test_paper_round7_artifacts.py","docs/paper/results-fill-registry.md"]
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: implementation

# FIX ROUND 1 — dx-registry (branch feat/2026-09-02-dx-registry @ 2a6d3841)

Linked worktree; you cannot commit — the magistrate commits. Never run
`python -m unittest discover`; named modules only. `TMPDIR` is preset under
the scratchpad; every scratch file goes there. Touch nothing outside
WRITE_SCOPE (no draft files, no JSON artifacts, no SVG, no checklist).

A luna refuter (report excerpt below) ran six mutation probes against R7F
(`scripts/check_paper_round7_artifacts.py`). Three were killed; three PASSED
when they must have failed. Cure all three and the one should-fix, and add a
DEFECT-SHAPED REGRESSION for each: the test must reproduce the refuter's
exact mutation against a scratch copy and assert the checker refuses with a
message naming the row/field. A regression that only exercises today's
committed artifact kills nothing (mutation-cure counterfactual rule).

## Blockers (refuter's replacement code is the specification; adapt names to the file)

B1 `R7F-REFUSAL-BUCKET-001` (~:399-413, DX-021 renderer): only the
`anchor_unresolved` list length is checked; an extra refusal-token bucket in
`AQ#summary.v3_refusals_by_token` is ignored. Require: the bucket map's key
set == {"anchor_unresolved"}; `len(buckets["anchor_unresolved"]) ==
v3_refused_count`; `v3_derived_count + v3_refused_count == population_size`.
Regression = refuter mutation M5 (add an extra bucket to a scratch AQ copy,
update the scratch registry's DX-002 digest/size to match, run → must FAIL
naming DX-021).

B2 `R7F-EXACT-INTEGER-001` (~:388-418): integer/count rows use `int()`,
which truncates `15.9` to `15`. Add
```
def _exact_int(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"not an exact integer: {value!r}")
    return value
```
and use it for EVERY integer, count, flip, control, and derived/refused
branch. Regression = mutation M4 (`population_size: 15.9` in a scratch AQ
copy with updated digest/size → must FAIL naming the field).

B3 `R7F-F4-COMMAND-001` (~:222-230, DX-003): the full F4 replay command is
unstructured prose; removing `--svg` from the row still passes. In the
registry parser, after `row_id` is parsed, assert for DX-003 that the
supplier cell contains exactly
```
full replay is `python3 scripts/paper_excursion_decomposition.py --corpus-root /Users/edr/code/JouleWise --out docs/paper/round7/excursion-decomposition.json --svg docs/paper/figures/fig4_edge_excursions.svg`.
```
and raise a RegistryError naming DX-003 otherwise. Regression = mutation M6
(scratch registry with `--svg …` removed → must FAIL naming DX-003).

## Should-fix

S1 `DX-027-SIGNED-001`: DX-027 renders the SIGNED `median_pct` (0.607832;
8 positive / 4 negative) without the explicit `+` that DX-024 uses for the
signed absolute median. Replace the DX-027 row with (verbatim):
```
| DX-027 — successor-draft median relative delta | +0.61 % | `AQ#summary.delta_v3_vs_stored_relative.median_pct`, parent DX-002; the issued artifact names this field `median_pct` (not `median_abs_pct`); render an explicit sign and two decimals followed by ` %`; `R7F_RENDER=signed_2_percent` | 15 retained instrument_validation captures, v2 era | MEASURED | DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; SUCCESSOR_DRAFT_ONLY | AQ, AS, R7F |
```
and add the renderer branch `signed_2_percent` (explicit sign, two decimals,
` %`). If the draft skeleton or checklist prints `0.61 %` anywhere, REPORT it
(they are outside your scope) — do not edit them.

## Verify and report (verbatim tails)

- `python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness`
- the checker's digest half from this worktree (expect the comparison count
  to rise if you added comparisons — report the new `R7F COMPARED n /
  MISMATCHES 0` line) and its replay half (expect exit 3 here if the corpus is
  absent, or the full pass if present — report which)
- re-run all six refuter mutations M1–M6 yourself against scratch copies and
  report each result; all six must FAIL now.
- `git status --porcelain` — only the three scoped files dirty.

FINAL message = `claude-codex-report/v1` envelope (implementation) with a
`verification` entry per command and a "Change" section mapping B1/B2/B3/S1
→ file:line and the regression test name for each.
