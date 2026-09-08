# Validating the methods/diagnostic successor

The legacy filename `select_outcome_branches.py` now implements a single
methods/diagnostic validator/copier. `--outcome` accepts only
`METHODS_DIAGNOSTIC`. A, B and REFUSAL are retired and rejected; historical
branch sheets provide no selection authority today. The copier validates its
source and copies it unchanged, refusing the source path or an existing output.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  docs/paper/fill-rehearsal/select_outcome_branches.py \
  --source docs/paper/draft-v2-skeleton.md \
  --output /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md \
  --outcome METHODS_DIAGNOSTIC
```

The output parent must already exist. Keep frozen inputs read-only. The guard
rejects outcome-branch markers, reader-facing result fills, and retired
DS/PG/OB/OR/R_/V5 fill markers even in comments. It checks one prospective
protocol link, the historical Abstract and Conclusion headlines, the fixed
Discussion transfer limitation, the historical figure placement, separation of
prospective material and the editorial ledger, and the 250-word Abstract limit.
It does not authenticate evidence or certify all first uses.

TR-01 is a fixed limitation, not a result slot. `RETIRED_FALLBACK` rows have no
submission placement. DS-34 remains an unissued locator hold. Prospective
counts are design requirements, not observed counts. Preserve historical and
synthetic labels. No numeric substitution is authorized by successful copying.

Check a final methods/diagnostic working copy with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  docs/paper/fill-rehearsal/select_outcome_branches.py \
  --check-rendered /ABSOLUTE/FILL-CUSTODY/draft-v2-selected.md
```

Require validation and an Abstract of at most 250 words after any authorized
assembly changes. The assembled-paper first-use review is a separate gate.
Successor operations remain PENDING adopted S1/S6 contracts and live
campaign-fill adjudication. Follow the [batch gates](../round7/fill-checklist.md)
and [migration inventory](../round7/successor-migration-inventory.md) for the
fresh successor copy, complete supplier/placement checks, input/output hashes,
replacement ledger and preserved historical replay fences. Eventual empirical
suppliers must use D-173 `open_paper_input`. Migration preparation does not
constitute empirical fill.
