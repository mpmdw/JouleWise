# What ordinal-1 `--check` proves

This document distinguishes the current-tree generator CLI from the historical
PACK_AUTHENTICATION evidence already frozen into ordinal-1 packs.

## The two requested modes are the same current-tree derivation

For each ordinal-1 pack, the compiled receipt constant equals the plan-pinned
current freeze receipt. Therefore `PRESERVE_CURRENT_FROZEN_BYTES` is true
(`generate_configs.py:220-224`). A bare `--check` uses that default, and an
explicit `--preserve-current-frozen-bytes` selects the same branch. `_generate`
reads each declared output from `REPO_ROOT` and returns early. `check_current`
then compares those copied bytes to `check_root`, which is also `REPO_ROOT`
under the bare CLI. The modes differ only in whether the same boolean was
implicit or explicit.

## Bare `--check` on an ordinal-1 current tree

It **proves**:

1. The current generator can start under the selected Python environment and
   its argument/identity setup accepts the current target.
2. Every path in the generator's declared output inventory exists and can be
   read. A missing science-row file failed with `ENOENT`.
3. The actual pack inventory has no file outside the generator's licensed
   generated inventory plus the freeze/evidence/source/projection additions
   admitted by `check_current`. An extra `UNLICENSED-EXTRA.txt` failed with
   `pack inventory differs: extras=UNLICENSED-EXTRA.txt`.
4. The current freeze receipt bytes and regenerated sidecar still equal the
   plan-tree freeze reference. A canonical receipt mutation plus regenerated
   sidecar failed with `committed freeze receipt is not the receipt the plan
   pins`.
5. Echoed declared bytes compare equal to the identical current-tree bytes
   from which they were read. This is an integrity-of-read/control-flow check,
   not a derivation claim.

It **does not prove**:

1. That a science-row configuration is the output of the generator's science
   logic. Appending a newline to a committed row returned 0.
2. That `calibration_plan.json` is re-derived. Appending a newline returned 0;
   the changed digest was merely printed.
3. That the semantic content of `plan_tree.json` is re-derived. Adding a
   canonical unknown member and regenerating `plan_tree.sha256` returned 0.
   This mutation intentionally left the freeze reference intact; changing that
   reference is covered by the separate freeze-binding check above.
4. That pinned external inputs are current. Appending a newline to
   `configs/calibration/calibration_acceptance_d079_v2.json` returned 0 because
   the pinned-input comparisons after the preserve return were never reached.
5. That the current generator source matches the plan's generator SHA for
   ordinal 1. All three current ordinal-1 sources fail that equality, yet bare
   `--check` returns 0.
6. That any generator output is independent of the committed pack under test,
   or that a second implementation agrees.

## Explicit preserve-mode `--check`

It proves and does not prove exactly the same six groups above. Every mutation
had the same return-code class as bare mode:

| Fresh `/tmp` mutation of `d117_floor_qwen25_1p5b_v1` | Bare | Preserve | Meaning |
|---|---:|---:|---|
| Science row: append newline | 0 | 0 | committed science bytes are echoed, not derived |
| `calibration_plan.json`: append newline | 0 | 0 | committed plan bytes are echoed |
| `plan_tree.json`: add canonical field, regenerate sidecar | 0 | 0 | plan semantics are not re-derived |
| Pinned acceptance JSON: append newline | 0 | 0 | external pin checks are unreachable |
| Add `UNLICENSED-EXTRA.txt` | 1 | 1 | closed inventory catches an extra |
| Delete one science row | 1 | 1 | declared-path read catches a missing file |
| Canonically mutate freeze receipt, regenerate sidecar | 1 | 1 | plan-tree-to-receipt digest binding catches the change |

Replay all cases with:

```sh
sh docs/process_traces/2026-08-26-t26-s3/replay-mutations.sh
```

Each case has its mutation diff, commit, exact command, stdout, stderr, return
code, and final line under `raw/mutations/`.

## What the already-consumed ordinal-1 PACK_AUTHENTICATION receipts prove

The tautology applies to a **fresh current-tree** CLI/re-derivation. It does not
describe how the three frozen ordinal-1 evidence receipts were originally
authored. Their authenticated PACK_AUTH sources record these `head_commit`s:

| Pack | Recorded derivation commit | Generator at commit | Freeze reference at commit | Replayed check | Recomputed historical pack digest |
|---|---|---|---|---:|---|
| 1.5B v1 | `3c8677d982cfdf2651fca6809cae5b8ee0c0d9f1` | no preserve mode; no receipt constant | none | rc=0 | matches source `pack_sha256` |
| 7B v1 | `6193379490de0733f142d5ff6248389d99d224a9` | no preserve mode; no receipt constant | none | rc=0 | matches source `pack_sha256` |
| contrast v1 | `c3d805ee94629a0588f44b0ccb8430fd52ec07b3` | no preserve mode; no receipt constant | none | rc=0 | matches source `pack_sha256` |

`replay-historical-anchor.sh` materializes each exact commit from local Git,
runs its generator, and recomputes the committed pack digest. All three checks
returned 0 and all three digests matched. This is genuine pre-freeze
regeneration: there was no echo branch to take. The present
`legacy_receipt_histsem_pinset_v1.json` then authenticates the historical
coordinate, current coordinate, receipt/source/freeze/plan bindings, and a
closed post-authoring delta (`docs/contracts/receipt_histsem_verifier.md:
64-78`).

The honest claim is therefore:

> Existing ordinal-1 PACK_AUTHENTICATION is evidence of generator regeneration
> at its authenticated pre-freeze derivation commit, composed with a governed
> historical-to-current custody delta. A current-tree preserve `--check` is
> only echo-integrity and cannot independently renew that derivation claim.

The implementation cure should enforce that distinction mechanically rather
than weakening the already-supported historical claim.

