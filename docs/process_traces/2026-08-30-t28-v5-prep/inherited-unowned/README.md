# Inherited unowned files from the T27 stall (custodied 2026-08-30)

Four files the stalled 2026-08-28 session left untracked in the S15 worktree,
outside the continuation session's write scope. Moved here so the superseded
test cannot reach the shard runner; nothing deleted.

- `test_d117_contrast_v5_generator.py` — SUPERSEDED: written against the
  inherited defective generator (512-default prefill, mirror probes); fails
  8/12+12 against the finished generator, whose coverage now lives in
  `tests/test_d117_contrast_v5_pack.py`.
- `admit_model_panel_entry.py` + `test_admit_model_panel_entry.py` +
  `mirror_model_panel_entry.md` — an offline mirror-verification tool for
  model-panel entries (D-164 admission evidence). Potentially still useful for
  estate 12 / freeze, but its tests fail against the finished closed panel
  schema. Decide during the `_v5` refuter round: refresh it against the new
  schema, or record the admission evidence another way and retire it.
