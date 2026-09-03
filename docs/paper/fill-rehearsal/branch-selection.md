# Selecting the outcome branches

The Abstract, Section 7 discussion, and Section 10 conclusion each contain one
`OUTCOME-BRANCHES` group with the same three alternatives: `A`, `B`, and
`REFUSAL`. Select one alternative only after the authenticated close-out has
classified every required independent-edge and comparative shared-error
ratio. Use `A` only when every required ratio passes, `B` only when every
required ratio is evaluable and at least one is below the fixed cutoff, and
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
test "$(grep -c '^\*\*A:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 0
test "$(grep -c '^\*\*B:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 0
test "$(grep -c '^\*\*Refusal:\*\*$' /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md)" -eq 0
```

Outcome D is not a fourth value for `--outcome`. The retensing plan places its
prefix only where the identical-workload characterization row is discussed,
in Sections 4 and 6. When that characterization was not collected, insert the
ruled D prefix at those two sites, omit their tokenized characterization lead,
and still select one of `A`, `B`, or `REFUSAL` here. None of the three groups
handled by this selector discusses that row, so adding a D prefix to one of
them is an error.

Finally, replace only numeric `[FILL:...]` markers from the named registry rows,
run the paper first-use and replay checks, and retain the selected working copy
and check outputs together in fill custody.
