# Magistrate note — CLONE-READINESS-01 plan (2026-09-08 ~13:35 PDT), from scout 99cn

Finding: the v5 measurement clone `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a` (HEAD 1c83f2af) is NOT
arm-ready for G2-a: (1) no `runs/` → the physical calibration ledger and its custody are absent (loader reports
calibration_ledger_missing + rollback against the committed pin sequence 76); (2) untracked `joulewise.egg-info/` trips
the clean-tree preflight gate (P:71–76); (3) with the preflight's PYTHONPATH the lock comparison reports the editable
`joulewise==0.1.0` from the duplicate source metadata; (4) the clone predates today's driver changes (liveness census in
run_night.py, plan-derived routing already in, D-176 producer pending).

Plan (bench-owned; the clone is outside any seat's sandbox):
1. Re-cut the clone at the post-merge main head after today's lanes land (recipe: trace 67 / runbook 27), with the
   new `*.egg-info/` ignore rule (main, today) so the tree is clean after an editable install; verify the lock diff is
   empty under the preflight's PYTHONPATH.
2. Restore the ledger byte-exact: `rsync -a --checksum` of `/Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl`
   and every custody directory the ledger's observations reference (enumerate from the ledger; never initialize an
   empty ledger, never reset the pin) into `<clone>/runs/`, then authenticate in the clone with custody replay
   enabled (`load_calibration_ledger_snapshot(verify_custody=True)` must report the pinned sequence, no rollback).
3. Ed items (batched, one session): `sudo -n -l /usr/bin/powermetrics` passwordless authorization; quiet-hardware
   checks; night-agent install from the clone (`scripts/install_night_agent.sh --plan ... --hour --minute`).
4. Magistrate inputs for the plan (after rehearsal acceptance): PLAN_ID, NIGHT_ROOT (fresh non-symlink dir under
   ~/night-custody), T0 (window + 300 s courier must end before 07:00), WINDOW_MAX_S, reviewed head.
5. Email-then-arm per D-175 line 19 / README in trace 99cd.
Registered as CLONE-READINESS-01 (kernel/queue rows in the T38c bookkeeping seat).

## Follow-ups accumulated 2026-09-08 afternoon (fold into the T38c bookkeeping seat: kernel + TASK_QUEUE rows)
- CLONE-READINESS-01 (this note, steps 1–5).
- BRIDGE-BASELINE-ANCHORS-01 (S2 synthesis ruling 8; TASK_QUEUE row exists above the generated region — kernel fold pending).
- WINDOW-LIVENESS-DOCS-01 — DONE on PR #305 (TASK_QUEUE row marked; kernel fold pending).
- UNIT-VOCAB-SHARED-01 (S3 contract follow-ups list; wire the shared metric-unit validator into manifest and verdict validation).
- REGISTRY-ROW-PIN-DRIFT (D-165 allowlist keyed by line; ordinal keying like the custody census) — nit from the S7 cure.
- D-176 seat 4 (rehearsal purpose / G7) after seat 2's fix round lands; second cold gate on the integrated head before the first pack-bound night.
- Paper integration tree: S2 (e5eb5b8d + nits) + S3 (6c34cfe6, LAND) + S7 reconciliation (1f7cb8e0) → one PR after a single supply-map repin and integration review.

## Amendment (2026-09-08 ~17:05, second D-176 gate 99ey): the REHEARSAL clone is separate from the production v5 clone.
- The production v5 clone (`JouleWise-measurement-v5-…`) stays an inventoried production deployment; it is never used for a rehearsal.
- The rehearsal night runs from a fresh `JouleWise-rehearsal-<date>-<sha>` clone cut AFTER the census cure + seat 4 land on main, at a head carrying `configs/production_custody_inventory.json`; NOT inventoried; the plan pins `measurement_head` = that head and `repo_head` = the driver checkout's head; the inventory bytes must equal `git show <repo_head>:configs/production_custody_inventory.json`.
- Steps 2–5 of the plan (ledger restore, Ed sudo items, plan inputs, email-then-arm) apply to the production clone for G2-a; the rehearsal clone needs no ledger restore (its runs/ is its own).
