WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# DELTA RE-AUDIT — dx-registry fix round 1 (branch feat/2026-09-02-dx-registry, fix commit 3f1677b7 over 2a6d3841)

Read-only refuter: workspace-write sandbox, EMPTY write scope — write nothing
under the checkout; scratch under $TMPDIR (preset). Never run `python -m
unittest discover`; named modules only. Run everything from this worktree.
You are a DIFFERENT model from the seat that wrote the fix (Sol) and from the
refuter that found the defects (luna); do not trust either report — re-execute.

Fix rounds introduce defects. Your job: (1) confirm each cure actually kills
its mutation, (2) find what the fix broke or left open, (3) state the
same-signature verdict.

Diff to audit: `git show 3f1677b7` — three files: `scripts/check_paper_round7_artifacts.py`
(F4_REPLAY_COMMAND literal + DX-003 parser assertion :228; DX-027 renderer
guard; `_exact_int`/`_exact_int_field` :385-397 used in every integer branch;
`derived_refused_counts` now reads `AQ#summary.v3_refusals_by_token` directly
and requires key set == {"anchor_unresolved"} and derived+refused ==
population_size; new `signed_2_percent`), `docs/paper/results-fill-registry.md`
(DX-027 row → `+0.61 %`, `R7F_RENDER=signed_2_percent`),
`tests/test_paper_round7_artifacts.py` (+148: four regressions at ~:223,
:245, :266, :287).

The six mutations from the prior refuter (all must FAIL with a message naming
the row/field; copy registry/JSON/SVG to $TMPDIR, point the checker via its
`R7F_REGISTRY` and related env/args — read the script's CLI):
M1 change one digit of DX-014's value; M2 swap the sign of DX-011;
M3 alter one SVG mark coordinate in a copy of F4;
M4 `population_size: 15.9` in a scratch AQ copy (update digest/size in the
scratch registry to match); M5 add an extra refusal-token bucket to a scratch
AQ copy (digest/size updated); M6 remove `--svg …` from DX-003's full replay
command in a scratch registry.
Then at least THREE NEW mutations of your own aimed at the fix, e.g.:
M7 `population_size: True` (bool is not an exact int — the guard claims to
refuse it); M8 `v3_refusals_by_token: {"anchor_unresolved": [...]}` correct
key set but `v3_derived_count` off by one; M9 DX-027 value `0.61 %` left
unsigned with the signed renderer (must the checker refuse, or does it pass
because the rendered string is compared, not the literal? state which and
whether that is a defect); M10 the DX-003 command with an extra space or a
different `--out` path.

Also check: does the DX-027 parser guard (`render_matches != ["signed_2_percent"]`)
belong in a generic parser (a row-specific literal in the parser is a
maintainability smell — NIT or SHOULD-FIX, your call with reasoning); does
the `derived_refused_counts` branch still consume its third field_ref
(`_` discarded — is the registry's field list now partly dead, and does the
digest-half comparison count change as a result); do the skeleton or
checklist print `0.61 %` anywhere (`grep -rn '0\.61 %' docs/paper`).

Run: `python3 -m unittest tests.test_paper_round7_artifacts tests.test_paper_replay_fence tests.test_docs_freshness`;
the checker's digest half and replay half from this worktree (report the
`R7F COMPARED n / MISMATCHES 0` lines; expect exit 3 if the corpus is absent
— it is present at /Users/edr/code/JouleWise, read-only).

Severity: BLOCKER = a mutation that still passes, a wrong value, a fence that
can pass when it should refuse; SHOULD_FIX = consistency/maintainability
defect with a concrete replacement; NIT otherwise.

FINAL message = `claude-codex-report/v1` envelope, fenced ```json, fields
{"verdict":"CLEAN"|"NOT CLEAN","same_signature":"<yes/no + which class>",
"findings":[{id,severity,lens,file,line,summary,replacement_text}],
"mutations":[{id,what,result}],"tests":"<last line per module>"} followed by
prose evidence with file:line citations. Anything unverified is a finding.
