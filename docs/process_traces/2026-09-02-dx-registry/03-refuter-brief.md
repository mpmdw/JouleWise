WRITE_SCOPE: []
ORIGIN: claude-fable-5 magistrate (JouleWise loop session) | HOP: 1 | GENRE: review

# ADVERSARIAL REFUTATION — dx-registry (branch feat/2026-09-02-dx-registry @ 2a6d3841, one commit over main a63d45bd)

Read-only refuter: workspace-write sandbox, EMPTY write scope — write nothing
under the checkout; scratch under $TMPDIR (already set). Never run
`python -m unittest discover`; run only named modules. Do not touch
`/Users/edr/code/JouleWise` (the main checkout) except for READ-ONLY inspection
of the retained corpus if the replay half needs it; run every command from
this worktree.

Diff to audit: `git show 2a6d3841 --stat` and `git show 2a6d3841` — four files:
`docs/paper/results-fill-registry.md` (+56: new `#### Successor-draft desk
analyses (round 7) — DX rows` section, 19 rows DX-001..003/010..017/020..027),
`scripts/check_paper_round7_artifacts.py` (new fence "R7F"),
`tests/test_paper_round7_artifacts.py` (new), `docs/paper/round7/fill-checklist.md`.

The ruling it implements (consult 168, three seats): register the round-7 desk
analyses as registry rows in a NEW `DX-` namespace (not appended to the closed
DG census); values issued from the two gated JSON artifacts XD/AQ with their
own digests as parent rows; a SEPARATE fence (digest half in CI; replay half
corpus-gated, exit 3 when the corpus is absent — never a pass); truthful
freeze label that does NOT say `REPLAY_FENCED` (reserved for RF); figure F4
bound by SVG SHA + JSON SHA + full `--svg` command; prose-standing sentence
mandatory. Seat report claims: R7F digest half 181 comparisons/0 mismatches,
full replay 184/0, two registry mutations refused, legacy replay-fence suite
15 OK 1 skip.

Use TWO lenses and tag every finding with one:

- CONTRACT lens: does every row obey the registry's own column vocabulary
  (`Fill rule` closed to MEASURED/DERIVE/STOP_FILL, registry :30-38; freeze
  tokens :574 ff.; sources abbreviations :548-567), do the DG census greps at
  registry ~:854-892 and the `01-verify-registry-v5.py` row-set assertion
  (`docs/process_traces/2026-08-31-registry-v5/01-verify-registry-v5.py:172-179`)
  still hold, does the fill-checklist placement count (`53/53`) reconcile with
  the rows, does every value in the table equal the JSON field under the stated
  rounding (recompute each of the 16 value rows yourself from the JSON), is
  every abbreviation defined, and does each freeze label say what the fence
  actually does.
- EXECUTION lens: run `python3 -m unittest tests.test_paper_round7_artifacts
  tests.test_paper_replay_fence tests.test_docs_freshness`; run the checker
  directly from THIS worktree (find its CLI in the script) and confirm the
  replay half exits 3 (not 0, not a pass) when the retained corpus path is
  absent; confirm `SVG` mark inversion actually reads the 118 marks (not a
  count-only check); perform at least THREE mutation kills of your own (copy
  the registry/JSON to $TMPDIR and point the checker at the copy — the seat's
  `R7F_REGISTRY` env var suggests how): (i) change one digit of DX-014's value,
  (ii) swap the sign of DX-011, (iii) alter one SVG mark coordinate in a copy of
  F4 — each must FAIL with a message naming the row. Check that CI actually
  runs the new test module (look at `.github/workflows/*.yml` and any shard
  list / `shard_tests` mechanism; a test that CI never executes is a finding).

Two bench observations from the magistrate (verify, rule):
(a) DX-027 renders `0.61 %` from `AQ#summary.delta_v3_vs_stored_relative.median_pct`
= 0.607832, which is the SIGNED median (8 positive / 4 negative), while
DX-024 (the signed absolute-delta median) renders WITH an explicit `+` sign.
Inconsistent sign rendering between two signed medians of the same population
— is it a finding, and what is the replacement rendering rule?
(b) The seat's flag F1: the ruling text spelled the field `median_abs_pct`
which does not exist; the seat substituted `median_pct`. Does the row's
column text ("median relative delta") describe the signed statistic truthfully,
and does any prose sentence in `draft-v2-skeleton.md` or the checklist
describe it as a magnitude?

Severity: BLOCKER = wrong value, wrong field, a fence that can pass when it
should refuse, a census/assertion broken, CI not running the test; SHOULD_FIX =
label/rendering/consistency defect; NIT otherwise. Give VERBATIM replacement
text for every finding (paste-ready; registry rows as full table rows).

FINAL message = `claude-codex-report/v1` envelope, fenced ```json, fields
{"verdict":"CLEAN"|"NOT CLEAN","findings":[{id,severity,lens,file,line,summary,replacement_text}],
"mutations":[{id,what,result}],"tests":"<last line per module>"} followed by
prose evidence with file:line citations. Anything unverified is a finding.
