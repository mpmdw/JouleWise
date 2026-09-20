# Record 33 — magistrate diff gate: EVIDENCE-NIGHT-ENTRY-01 slice B1 (`feat/2026-09-20-evidence-night-lifecycle`, head `b678b1dc`), 2026-09-20 10:12 PDT

## §1 Diff gate (rows 7 and 8) — the production delta skimmed by function and refusal (full read deferred to the refuters' line citations; the lead reads every hunk the refuters name)
Seat 30 (Astra xhigh; attempt 1 NEEDS_RULING → ruling 30a → attempt 2): +1,120/−13, one module (`joulewise/evidence_night.py` gains `candidate_state`, `candidate_lock`, `sealed_state`, `clone_schedule`, `canonical_check`, `supervisor_check`, `retained_roots`, `census_check`, `retry_inventory`, `check`, `installer_call`, `verify_state`/`verify`, `publish_install`, `uninstall`, and the CLI actions with `--launchctl-bin`), its tests (`LifecycleTests`, `LifecycleCompositionTests`: fixture repo, injected census, fake launchctl, synthetic probe receipt), the contract. Bench: `tests.test_evidence_night` + `tests.test_evidence_arm_sequence` → `Ran 45 tests in 122.475s OK`; the seat's five-module run → 162 OK.
Design-level reading:
- **Every check is a refusal with a named cause** (canonical ancestry/cleanliness; census-fix containment by literal `CENSUS_FIX`; supervisor freshness by the reflog walk of record 21; courier on PATH; retained-root discovery; census + ancestry; attempt inventory) and `check` writes only `check.json`.
- **Publication** is `os.replace` on one filesystem after `check.json` (armable, bound to `prepare.json`, newer than every sealed artefact) and a notice acceptance id; failure after publication → uninstall-first → unpublish only if the published bytes still equal the staged snapshot, else stop with the retained state named. This is the bench step-4 recovery, in code.
- **verify** (ruling 30a): both labels LOADED via the installer's typed liveness; installed plists compared field by field to the plan-derived schedule and byte-equal to the render; no `launchctl print` calendar parsing.
- **Overbuild / prune:** none seen — the façade delegates to the installer for probe/install/uninstall/liveness; no second installer, no scheduler, no transport (slice B2).
- **Open to the refuters:** fidelity to step 0/4/5 line by line; the freshness rule's basis (mtime vs digest); the literal fix SHA as a constant; the live (a)/(b) verdicts on this machine; recovery under a crash between publication and the installer call.
Verdict of the diff gate: MERGE-able pending refuter 32 (execution) and the Opus contract lens (record 34), then the fix round and delta audits, then the replay.

## §2 Replay (row 9) — (pending)
## §3 Fix contract / same-signature — (pending)
## §4 Terminal review — (pending)
