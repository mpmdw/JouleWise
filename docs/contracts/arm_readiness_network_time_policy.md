# Arm-readiness network-time policy

Under D-186 (2026-09-29) and the orchestrator's 2026-10-04 prospective
replacement ruling, the live `d117_row_registry_v2.json` replaces
`clock.restore_recipe` with `clock.network_time_policy`. Registry v2 has no
retirement field: it requires exactly 35 sorted rows and every profile selects
every row. The replacement therefore has a new row ID and predicate ID
`clock.network_time_policy.v1`, with the same `FREEZE_AND_ARM` phase, `ALWAYS`
applicability, `DOCTRINE_PIN` evidence kind and re-derivable lifecycle policy.

The new predicate requires these facts from current runbook §5A:

- Network time stays OFF across windows, including completion, refusal,
  crash, verdict and both backups.
- Resync happens only in the arm step, before its OFF receipt and capture.
- Each window uses one OFF receipt from the arm step. `clock-disable` reuses
  the saved write-once receipt and does not toggle again.
- Close-out records the OFF receipt and its identity without restoring ON.

The deriver requires the governing stays-OFF, resync, saved-receipt and
close-out sentences and rejects contradictory restore instructions even when
the stays-OFF sentence remains. It emits the new fact, never
`clock.restore_recipe.v1`. This is procedural doctrine evidence;
`clock.network_time_off` and its live `CLOCK_PROBE` requirements are unchanged.
Missing live OFF evidence still refuses ARM.

The live registry has no separate whole-file digest literal or sidecar to
advance. Its consumer requires canonical bytes equal to committed HEAD and
computes the SHA-256 reference. New plan trees, freeze receipts and ARM
receipts record that committed digest. No frozen pack, historical receipt,
histsem pinset, historical digest, archival v1 registry or old predicate is
rewritten. Historical verification uses its authenticated receipt coordinates
and retains the restore predicate's original semantics.
