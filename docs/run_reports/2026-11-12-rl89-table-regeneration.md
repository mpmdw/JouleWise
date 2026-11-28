# RL-89: Part B table regenerated from the saved fifth smoke (no re-measurement)

2026-11-12, lead (Air). Authority: RL-89 item 3 ("regenerated, not re-measured"), RL-94.
Blind: temperature, classifier and coverage fields only; no v4 outcome, no energy value.

## Inputs

- **Segment:** the fifth smoke's step-D segment (RUN_STATE 282), MBP
  `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261112T103324Z/part-b/step_D_prefill_10k_decode_4096`.
  It was copied read-only to the Air with rsync. The large raw, power-trace and rich-telemetry files were left out,
  because `smoke_table` does not read them. The files it does read are byte-identical to the MBP copies (sha256
  compared on both hosts): `runtime_result.json`, `inventory/*`, `runs/align-v4-r1-step-d/events.jsonl` and
  `runs/align-v4-r1-step-d/outputs/align_thermal.jsonl`.
- **Saved table:** `part-b/smoke_part_b.json`, sha256
  `6b05379df65a34e6503a29ce5813d8934ee9d923b9fe3c83c04301070d1ff373` (matches RUN_STATE 282). The receipt
  `runner_receipt.json` sha256 `f69e56499d85de47eb676eac4923c0ac7154ae992af1169674026ff150e5aaa1` also matches.
- **Code and config:** branch `fix/2026-11-12-rl89-sensor-config` at the RL-89 config commit. Only
  `configs/align/v4/r1_runtime.json` differs from presign `22f438fd3` among the files `smoke_table` reads. The kit,
  runtime and classifier are unchanged.

## Command

```sh
export TMPDIR=/Volumes/JW-EXT/scratch/rl89/tmp
cd /Volumes/JW-EXT/jw-wt/rl89     # the branch head with the RL-89 config
nice -n 10 python3.13 -B -c "
import json,sys
sys.path.insert(0,'.')
from scripts import align_r1_followup_kit as kit
t=kit.smoke_table('/Volumes/JW-EXT/scratch/rl89/smoke5/part-b/step_D_prefill_10k_decode_4096')
open('/Volumes/JW-EXT/scratch/rl89/regen/smoke_part_b.json','x').write(json.dumps(t, indent=2, sort_keys=True) + '\n')
"
```

The serialization is the kit's own (`smoke()` writes `json.dumps(part_b, indent=2, sort_keys=True) + "\n"`).

## Hashes

| Table | Path | sha256 |
|---|---|---|
| Saved (fifth smoke, six-key list) | `docs/run_reports/2026-11-12-rl89/smoke_part_b.fifth_smoke.json` | `6b05379df65a34e6503a29ce5813d8934ee9d923b9fe3c83c04301070d1ff373` |
| Regenerated (RL-89 config) | `docs/run_reports/2026-11-12-rl89/smoke_part_b.rl89.json` | `1fdd980c91ceca6ee3907191b499f0108ca84b8709648a638bd49808a298eba3` |

## Acceptance (RL-89 item 3): ACCEPTED

1. `classification_sha256` is unchanged in both tables:
   `0b9cdb9e136eee48c742a6bdfef3313373f795949027779353c31f717630e0a6`.
2. `coverage` is identical (deep equality of the whole object).
3. `selection` is `ok` true, `fallback` false, `s_fast` TV0h, `s_slow` Th0C, with `reasons` [].
4. The top-level fields that differ are `r0_classified_keys` (6 keys to 60), `selection` and `status`.
   - In `selection`, only `ok` (false to true) and `reasons` (the R0-membership reason is removed) change. That
     is identity 3 itself.
   - `status` follows from `selection.ok` in the kit's code (`SELECTION_FAILED` to `FOR_RESEARCH_LEAD_RULING`).
   - `rejected_keys` (3 rows, all TVH3 in load) is identical, `r0_class` labels included. TVH3 is record-only in
     R0, so it reads `unclassified` under both lists.
   - `classification_table`, `candidate_replays`, `class_edge_margins`, `schema` and `note` are byte-equal as
     objects.

`validate_sensor_ruling` passes on the regenerated table with
`docs/run_reports/2026-11-12-rl89/sensor_ruling_rl89.json` and the branch config. On the saved table it refuses
("RL-78: smoke R0 key set changed"), as it should.

## Not changed

- The `candidate_replays` rows are still all `unobserved`. RL-89 calls this "one defect, not gating", and the lead
  diagnoses it after the night.
