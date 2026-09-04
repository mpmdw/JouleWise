# Selecting the outcome branches

The Abstract, Section 7 discussion, and Section 10 conclusion each contain one
`OUTCOME-BRANCHES` group with the same three alternatives and their governed
labels: `A` is **A — every required ratio passes:**, `B` is **B — an
authenticated, evaluable ratio is below 2:**, and `REFUSAL` is **Refusal —
stopped before comparison or at close-out:**. Select one alternative after the
evidence either stops before comparison or reaches close-out. Before
comparison, select `REFUSAL` when a model-specific measurement window was
excluded or an authenticated token-generation or prompt-processing verdict is
absent. If the evidence reaches close-out, select `REFUSAL` when a required
ratio is missing, unauthenticated, or has a zero denominator. Otherwise, use
`A` only when every required independent-edge and comparative shared-error
ratio passes, and use `B` only when every required ratio is authenticated and
evaluable and at least one is below the fixed cutoff.

Run the selector against a copy of the skeleton, never the skeleton itself:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  docs/paper/fill-rehearsal/select_outcome_branches.py \
  --source docs/paper/draft-v2-skeleton.md \
  --output /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md \
  --outcome A
```

`--outcome` accepts exactly `A`, `B`, or `REFUSAL`. The selector requires one
complete group in each of the three sections, verifies that each group contains
the three alternatives in that order, deletes both unselected alternatives and
all selection markers, removes the selected bold label and quote prefix, and
refuses to overwrite its input or an existing output. After it succeeds,
require all of the following before numeric filling:

```sh
test "$(grep -c '<!-- OUTCOME-BRANCH' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 0
test "$(grep -c '^\*\*A — every required ratio passes:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 1
test "$(grep -c '^\*\*B — an authenticated, evaluable ratio is below 2:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 1
test "$(grep -c '^\*\*Refusal — stopped before comparison or at close-out:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 1
test "$(grep -c '\[FILL:TR-01\]' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 3
```

The one surviving copy of each bold form is the governing reference in Section
4, not a removable branch label. The skeleton contains four copies of each
form—one reference plus three branch labels—so exactly one after selection means
that zero branch labels remain.

The selector also prints the retained slot counts. Every selected draft must
carry three `[FILL:TR-01]` placements, one in each selected paragraph, because
the post-campaign inserted-gap result is independent of the A/B/Refusal ratio
outcome. A B selection must additionally carry three `[FILL:OB-01]`
placements naming the below-two components; A and REFUSAL must carry none.
Both rows are `STOP_FILL` in the registry until their named suppliers and
professor-facing renderings issue. Each A or B selection must also carry three
`[FILL:DS-32]` token-generation-verdict placements and three `[FILL:PG-08]`
prompt-processing-verdict placements, one of each in every selected paragraph.
Those verdicts come only from their authenticated claim-evaluation rows and are
never inferred from the ratio outcome. A REFUSAL selection carries neither
verdict slot in its three selected paragraphs; it carries three
`[FILL:OR-01]` placements that each name whether the stop occurred before
comparison or at close-out and print the issued reason. The governed Section-4
Refusal form contributes one additional `[FILL:OR-01]` until final filling
selects one Section-4 form, so the whole selected draft contains four such
markers for REFUSAL and one for A or B. `OR-01` prints a Qwen-pair verdict only
when the absence of that verdict is the issued stop reason. Do not delete,
guess, or replace any of these slots while filling unrelated numeric markers.

Outcome D is not a fourth value for `--outcome`. The retensing plan places its
prefix only where the identical-workload characterization row is discussed,
in Sections 4 and 6. When that characterization was not collected, insert the
ruled D prefix at those two sites, omit their tokenized characterization lead,
and still select one of `A`, `B`, or `REFUSAL` here. None of the three groups
handled by this selector discusses that row, so adding a D prefix to one of
them is an error.

Finally, replace numeric `[FILL:...]` markers from the named registry rows and
replace semantic slots only after their registry stops clear. Run the paper
first-use and replay checks, and retain the selected working copy and check
outputs together in fill custody.
