# Selecting the outcome branches

The Abstract, Section 7 discussion, and Section 10 conclusion each contain one
`OUTCOME-BRANCHES` group with the same three alternatives and their governed
labels: `A` is **A — every required ratio passes:**, `B` is **B — an
authenticated, evaluable ratio is below 2:**, and `REFUSAL` is **Refusal — a
required ratio is missing, unauthenticated, or has a zero denominator:**.
Select one alternative only after the authenticated close-out has classified
every required independent-edge and comparative shared-error ratio. Use `A`
only when every required ratio passes, `B` only when every required ratio is
authenticated and evaluable and at least one is below the fixed cutoff, and
`REFUSAL` when a required ratio is absent, cannot be authenticated, or has a
zero denominator.

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
test "$(grep -c '^\*\*Refusal — a required ratio is missing, unauthenticated, or has a zero denominator:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 1
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
professor-facing renderings issue. Do not delete, guess, or replace either
slot while filling unrelated numeric markers.

Outcome D is not a fourth value for `--outcome`. The retensing plan places its
prefix only where the identical-workload characterization row is discussed,
in Sections 4 and 6. When that characterization was not collected, insert the
ruled D prefix at those two sites, omit their tokenized characterization lead,
and still select one of `A`, `B`, or `REFUSAL` here. None of the three groups
handled by this selector discusses that row, so adding a D prefix to one of
them is an error.

Finally, replace numeric `[FILL:...]` markers from the named registry rows and
replace the two expressly authorized semantic slots only after their registry
stops clear. Run the paper first-use and replay checks, and retain the selected
working copy and check outputs together in fill custody.
