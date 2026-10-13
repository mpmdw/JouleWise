# Floor mint pin authoring

`emit_floor_mint_pinset.py` authors a final `joulewise.floor_mint_pinset.v2`
and a `joulewise.floor_mint_inputs.v2` manifest. It reads identities from each
pack's producer contract and plan, and postcollection pins from the extraction
report, bundles, bracket binding and terminal ledger. It authenticates those
inputs through the generalized mint before deriving component artifact hashes.
It does not issue a floor or substitute missing postcollection evidence.

Supply exactly two occurrences of each producer argument, ALPHA then BETA.
The default `--prefill-role prefill_p2048` selects the claim-bearing `_v5`
prefill role; the other prefill role remains in the shared extraction spec's
physical member inventory. Consumer allowlists come from the consumer pack's
prospective analysis manifest and condition-family files. All output parents
must exist; outputs are exclusive and a failed second write removes the first.

```sh
"$PY" -B scripts/emit_floor_mint_pinset.py \
  --producer-pack "$ALPHA_PACK" --producer-pack "$BETA_PACK" \
  --runs-root "$ALPHA_RUNS" --runs-root "$BETA_RUNS" \
  --extraction-report "$ALPHA_REPORT" --extraction-report "$BETA_REPORT" \
  --bracket-binding "$ALPHA_BRACKET" --bracket-binding "$BETA_BRACKET" \
  --plan-relative-path "alpha/calibration_plan.json" \
  --plan-relative-path "beta/calibration_plan.json" \
  --consumer-pack "$GAMMA_PACK" \
  --calibration-acceptance "$CALIBRATION_ACCEPTANCE" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --calibration-ledger-head-pin "$CALIBRATION_LEDGER_HEAD_PIN" \
  --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" \
  --project-commit "$MINT_COMMIT" \
  --pinset-out "$FINAL_PINSET" --input-manifest-out "$V2_INPUT_MANIFEST"
```

Retain the printed `pinset_sha256` as `FINAL_PINSET_SHA256`. Plan relative paths
describe copies of the exact producer plan bytes relative to the aggregate
floor artifact directory. The mint commit is part of each component byte hash:
mint at that same clean HEAD before changing the checkout. Registration of the
emitted pinset under this directory makes its family discoverable by the claim
reader. Keep one pinset per family identity; multiple matches refuse.

The existing mint CLI already accepts and requires the D-165 output flag when
the supplied spec registers a common-mode comparative estimator:

```sh
"$PY" -B scripts/mint_floor_artifact_generalized.py \
  --pinset "$FINAL_PINSET" --pinset-sha256 "$FINAL_PINSET_SHA256" \
  --v2-input-manifest "$V2_INPUT_MANIFEST" \
  --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" \
  --out "$AGGREGATE_FLOOR_ARTIFACT" --single-count-out "$SINGLE_COUNT_STATEMENT" \
  --d165-replay-out "$DOMINANCE_REPLAY_SIDECAR" \
  --project-commit "$MINT_COMMIT" --project-tree-state clean \
  --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID"

"$PY" -B scripts/finalize_analysis_manifest.py \
  --prospective-manifest "$PACK_ROOT/analysis_manifest_v3.json" \
  --plan-tree "$PACK_ROOT/plan_tree.json" \
  --custody-root "$ANALYSIS_CUSTODY_ROOT" --runs-root "$RUNS_ROOT" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --aggregate-floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" \
  --dominance-replay-sidecar "$DOMINANCE_REPLAY_SIDECAR" \
  --output-dir "$ANALYSIS_CUSTODY_ROOT"
```

Finalization stages an external sidecar's exact bytes as
`dominance-replay-<sha256>.json` under finalize custody. Identical restaging is
idempotent; differing occupied bytes refuse. A sidecar already inside custody
retains its path. Omitting it preserves the dominance attachment refusal.

## Per-cell scientific config binding

The 2026-10-05 lead ruling permits a producer's decode and p2048 workloads to
have different scientific configs. Newly emitted v2 cells carry
`scientific_config_identity_sha256`; both absolute and comparative components
must equal their own cell's pin. The production emitter derives each workload
pin from every selected member's registered config in the frozen plan tree,
checking the pack's exact config-byte commitments before authoring. Collected
config-byte hashes remain separately bound by the existing member pins.

The producer's `model_runtime_config.config_set_sha256` is SHA-256 of the
canonical JSON array of sorted distinct per-cell scientific config hashes,
using UTF-8 and compact separators with no trailing newline. The minted
artifact records each producer's digest and cell bindings in
`provenance.producer_config_sets`. Claim discovery checks those records against
the registered pinset. Swapping the two workloads between cells remains a
refusal even when the producer's set is unchanged. Model-artifact and runtime
identity equality checks are unchanged.

Legacy v2 pinsets without per-cell scientific config pins keep their original
single-config check and artifact bytes. New singleton sets use the canonical
array hash; v1 behavior is unchanged. A producer may not mix legacy and new
cell bindings.

The fixture regression exercises the real pin author, mint, artifact validator
and claim loader without mocking those seams. It uses explicitly synthetic
authenticated producer objects. Full file-custody CLI verification also needs
the archived D117 calibration custody fixture, which is absent in this checkout.

## Block 5: floors over kept units, from the window index

Everything above describes the mint as it ran before block 5. A block-5 floor
window cannot be minted that way, for four reasons, and the block-5 mode below
exists to remove them. It changes no arithmetic.

Terms, each used with this meaning from here on:

- A **floor window** is one measurement session of a floor pack (ALPHA, the
  1.7B model; BETA, the 8B model). Each of its cells is measured ten times
  alone (ten **repeats**) and ten times in **quads**: four runs in the order
  A1, B1, B2, A2, from which one difference (B1 + B2 − A1 − A2)/2 is taken.
  A repeat or a quad is a **unit**.
- A cell's **detection floor** is the smallest energy difference the
  instrument can tell from no difference. It is computed twice: from the
  repeats (the **absolute form**) and from the quads' differences (the
  **comparative form**); the cell's floor is the larger of the two. Each
  unit enters with a **timing half-width**: the energy by which its value
  could change if its time stamps were wrong by the operative bound defined
  below.
- The **small-sample guard** widens a floor computed from fewer than ten
  units: the floor is multiplied by g(n) = sqrt(9 / (n − 1)), which is 1 at
  n = 10, 1.1339 at n = 8 and 1.5 at n = 5.
- The **claim gate** is the program (`python -m joulewise analyze-claims`)
  that compares each measured contrast between the two models with these
  floors. A **target cell** is a cell whose floor a claim reads.
- The **harvest archive** is the directory the harvest wrote for one session:
  a copy of the session's bytes under `sources/`, and the harvest's own
  records under `derived/`. The **window index** is the one JSON file that
  lists every session of the block with the path of its archive.
- The sealed exclusion function decided, per unit, whether a fault recorded
  during the session removes it. A **kept unit** is one it did not remove.
  The decision is in the archive (`derived/exclusions.json`).
- The **extraction report** is the output of `scripts/extract_detection_floors.py`
  for one floor window. For each cell and form it holds the floor computed
  over the kept units, one row per planned member (a removed unit's rows carry
  `excluded: true` and no value), and a `kept_units_binding` that names, per
  cell, the kept and the removed unit ids and the SHA-256 of the exclusions
  file they came from.
- The **calibration bracket** of a window is the pair of timing calibrations
  that opened and closed it. Its **operative bound** is the largest distance,
  in seconds, by which a power sample's time stamp may differ from true time
  in that window. The **calibration ledger** is the append-only file that
  records every calibration in order.

The four reasons, and what the block-5 mode does about each:

1. **Removed units.** The older mint refuses a cell in which any member is
   excluded, and sets the cell's smallest admissible n to the absolute form's
   n. A block-5 cell may keep, say, ten repeats and eight quads. In block-5
   mode the mint accepts an excluded row exactly when its unit is a removed
   unit of the archive's exclusions file, computes each form over its kept
   units, and takes the smallest admissible n (`minimum_claim_n`) from the
   exclusions file's own per-cell minimum.
2. **Where the drift allowance comes from.** A floor carries the window's
   drift allowance: the energy by which the machine's idle draw may have
   moved between the start and the end of the session. On a block-5 window
   the allowance that stands is the one in the harvest archive, not the one
   in the row stored at the end of the session. The mint therefore needs each
   window's archive, and it opens no member of a removed unit.
3. **One ledger for two windows.** The older emitter and mint take one ledger
   file for both floor windows. ALPHA and BETA closed at different ledger
   positions. In block-5 mode each window is checked against its own archived
   copy of the ledger, cut at the entry that closed that window.
4. **A pinset that holds an energy.** The pinset records the drift allowance
   and the floor values. The block's energies are blinded: no person or
   committed file may hold them until a recorded release event. It therefore cannot be a file of this directory. In
   block-5 mode it is written beside the floor artifact, in analysis custody,
   and the claim gate looks for it only there.

### Worked example (made-up numbers)

One cell. All ten repeats are kept; quads 5 and 9 were removed, so eight quads
are kept. The eight quad differences are 0.10, −0.05, 0.20, 0.00, 0.05, 0.15,
−0.05 and 0.00 J, each with a timing half-width of 0.30 J. The window's drift
allowance is 0.80 J.

| Step | Absolute form (n = 10) | Comparative form (n = 8) |
|---|---|---|
| Floor before the small-sample guard | 0.5730 J | 1.0896 J |
| Guard factor g(n) | 1.0000 | 1.1339 |
| Guarded floor (floor × g) | 0.5730 J | 1.2354 J |
| Plus the drift allowance, 0.80 J | 1.3730 J | 2.0354 J |

The cell's floor is the larger of the two last values, 2.0354 J. The pinset
records `expected_n` 10 with ten member pins for the absolute form, and
`expected_n` 8 with thirty-two member pins (eight quads of four) for the
comparative form. `minimum_claim_n` is 5, the exclusions file's minimum, not
10 and not 8. The eight members of quads 5 and 9 are in the report as
excluded rows and are never opened by the mint.

### The two commands

Both take the window index and take no path to a runs root, a ledger, an
acceptance file or a bracket binding: each of those is read from the window's
archive, and each sealed pack file (calibration plan, its digest file,
extraction spec, order manifest) is read from this checkout and must be
byte-identical to the archive's copy of it.

```sh
"$PY" -B scripts/emit_floor_mint_pinset.py \
  --window-index "$WINDOW_INDEX" \
  --alpha-report "$ALPHA_REPORT" --beta-report "$BETA_REPORT" \
  --out-dir "$FLOOR_DIR" --project-commit "$MINT_COMMIT"

"$PY" -B scripts/mint_floor_artifact_generalized.py \
  --window-index "$WINDOW_INDEX" \
  --pinset "$FLOOR_DIR/floor-mint-pinset.json" --pinset-sha256 "$FINAL_PINSET_SHA256" \
  --v2-input-manifest "$FLOOR_DIR/floor-mint-inputs.json" \
  --out "$FLOOR_DIR/$AGGREGATE_FLOOR_NAME" \
  --single-count-out "$FLOOR_DIR/single-count.txt" \
  --d165-replay-out "$FLOOR_DIR/dominance-replay.json" \
  --project-commit "$MINT_COMMIT" --project-tree-state clean
```

`$ALPHA_REPORT` and `$BETA_REPORT` are the two extraction reports.
`$FINAL_PINSET_SHA256` is the `pinset_sha256` the first command prints. With
`--window-index`, every flag of the older command lines is refused.

After both commands the floor directory holds the files below; every name but
the aggregate floor's is fixed by the programs.

```
$FLOOR_DIR/
  floor-mint-pinset.json        written by the emitter: the identities, hashes and
                                post-collection values the mint must reproduce
  floor-mint-inputs.json        written by the emitter: per floor pack, its plan id,
                                the SHA-256 of its exclusions file and the path of
                                its extraction report
  alpha/calibration_plan.json   written by the emitter: a copy of ALPHA's sealed plan
  beta/calibration_plan.json    written by the emitter: a copy of BETA's sealed plan
  $AGGREGATE_FLOOR_NAME         written by the mint: the four floor cells
  single-count.txt              written by the mint: the single-count statement
  dominance-replay.json         written by the mint: per kept quad, the inputs the
                                dominance close-out replays
```

The mint refuses an `--out` outside the pinset's directory, and a pinset
inside `scripts/floor_mint_pinsets/`. The two plan copies are there because
the claim gate reads each producer's plan beside the floor artifact.

### What the pinset does and does not carry

The pinset's keys are the same as before block 5: the artifact validator
accepts a pinset only with exactly those keys. The planned n, the removed unit
ids and the digest of the exclusions file are not new pinset keys. They are
bound through a key the pinset already has: `extraction_report_sha256` is the
SHA-256 of the extraction report, and the report's `kept_units_binding` states
all three. The mint loads the kept units from the archive itself and refuses
when the report's binding differs from them.

### Refusals of the block-5 mode

Each stops the program before any output is written.

| Message begins | Meaning |
|---|---|
| `window_index_required` | a block-5 window was given without the index |
| `window_index_conflicting_arguments` | the index was given with a flag or a manifest of the older mode |
| `floor_mint_kept_unit_mismatch` | the report, the pinset, the replay file or the archive disagree about which units are kept |
| `floor_mint_cell_not_a_target` | a cell that the exclusions file does not mark as a target cell was pinned (in the sealed packs: the 42-token prefill cells, which no claim reads) |
| `operative_bound_not_the_window_bracket` | a kept member's timing bound was reduced under a bound other than its own window's operative bound |
| `archive_input_changed_after_authentication` | an archive file read by path no longer has the bytes the archive's inventory lists |
| `floor_pinset_not_beside_floor` | the pinset and the floor artifact are not in one directory, or the pinset is in this directory |
| `producer_plan_identity_mismatch` | a pack's calibration plan, plan tree and producer contract do not name one plan id |

### JSON Schema

The bracket screen is the smallest timing allowance, in seconds, that a
window's calibration pair is given whatever drift it shows; block 5's is
0.014531 s. `schema_v2.json` now lists that value (`0.014531`) among the
values a final pinset may carry; before, its two lists allowed only the two
older screens, so no block-5 pinset could have satisfied the schema. The
programs do not read the schema; it is checked by a test when the optional
`jsonschema` package is installed.
