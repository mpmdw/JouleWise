# R1 to W1: after R1 closes

Operator note for the magistrate and laptop lead. It turns the R1 lane's record into
what the W1 kit accepts. Nothing here edits the R1 lane; the steps run on the v4
branch (`align/2026-11-08-v4-r11`). Why the steps exist: the R1 lane driver
(`e901eb2a4`) writes no X-G evidence (`admitted_turns`, `x7`, `phases_s`; R10-4) and
no per-turn counts on the gated D rows (R11/R16), and the kit refuses a record
without them (`R11 contrast ...` / `turn opportunity ... inconclusive`).

## Where each step runs

| Step | Host | Why |
|---|---|---|
| R1 closes; finalize, hash and push the record (RUN_STATE 213) | MBP | the only MBP work; then it stays idle for the next window |
| Everything below | laptop | reads copies; no desk, hashing or evidence traffic on the MBP while it measures |

Copy the pushed R1 output directory (`RUN`: it holds `r1_result.json` and one
directory per phase) and the driver's `registration/r1_slots.json` to the laptop.
Use a checkout of the v4 branch; set `WORK` to a new empty directory.

## Command sequence (laptop, repository root)

```sh
RUN=/path/to/R1/output            # contains r1_result.json and D_*_gated_held*/
SLOTS=/path/to/R1/registration/r1_slots.json
WORK=/path/to/new/empty/dir

# 1. per-turn counts (reads only <phase>/<bundle>/outputs/align_turns.jsonl per gated D run)
python3 scripts/align_r1_turn_counts_export.py --run-dir $RUN --out $WORK/turn_counts_export.json

# 2. X-G evidence into the record (R10-4)
python3 scripts/align_w1_budget_procedure.py backfill-x-g \
    --r1-slots $SLOTS --r1-result $RUN/r1_result.json --out $WORK/r1_slots.xg.json

# 3. per-turn counts into the gated rows (R11/R16; records the export's sha256)
python3 scripts/align_w1_budget_procedure.py backfill-turn-counts \
    --r1-slots $WORK/r1_slots.xg.json --counts-export $WORK/turn_counts_export.json --out $WORK/r1_slots.json

# 4. install the record, then re-derive the contrast cap/fit from it
cp $WORK/r1_slots.json configs/campaigns/align_v4/registration/r1_slots.json
python3 scripts/align_w1_budget_procedure.py derive-contrast     # paste both fields into
                                                                 # registration/inputs.json R1.thermal_policy

# 5. R10-2 budget procedure (writes a receipt draft when branch (a)/(b); the lead signs)
python3 scripts/align_w1_budget_procedure.py decide --draft-out $WORK/ruling_1f_draft.json

# 6. readiness (this is kit.require_ready plus the other gates; it must pass before W1 registration)
python3.13 -B scripts/align_v4_kit.py --check
```

`--check` also needs the other pending registration inputs (U3, WP19, receipt, gates);
it fails closed until they are supplied. Steps 1-4 are mechanical; step 5 and the
signatures are lead-owned.

## What the exporter does and refuses

It reads `r1_result.json` and, for each of the three gated D runs, one file:
`RUN/<run name>/<result.bundle>/outputs/align_turns.jsonl` (or its `.zst`). From each
turn row it takes only the turn index, the `turn_token_budget_reached` flag, the
LENGTH of `generation.output_token_ids` and `generation.finish_reason`; no energy,
power, thermal or score file is opened and no token content is kept. A turn is
`completed` if it has a non-empty finish reason that is not a token-budget cut;
unknown reason is not completed (fails closed). The output carries per-run counts and
the sha256 of `r1_result.json` and of each turn file (stored and decompressed). It
refuses when the turn totals disagree with the driver's `decode_tokens` and
`admitted_turns`, when a turn file is missing or out of order, when a bundle path is
absolute or escapes `RUN`, and when `--out` exists. A gated run that admitted no turn
(for example a G0 timeout) exports empty counts and `backfill-turn-counts` refuses it:
R16 treats that as unresolved or an R1 re-run, which is the magistrate's call.

## Expected runtime

Seconds on the laptop: the export parses three JSONL files of at most a few thousand
rows each (plus `zstd -d` if compressed), and each backfill, `derive-contrast` and
`decide` is under a second; `--check` takes a few seconds (the kit regeneration).
No MBP time beyond the existing R1 close.

## Checked on synthetic data

`tests/align/test_r1_turn_counts_export.py` runs the chain on a lane-shaped record and
synthetic bundles: export, `backfill-x-g`, `backfill-turn-counts`, contrast
re-derivation and `kit.require_ready` bind. It is not evidence about real bundles; the
first real run should compare the export's totals with the driver record (the exporter
already refuses a mismatch).
