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

## §2 Replay (row 9) — full sharded replay at `0481bb0b` (round 1 + main) in the lifecycle worktree, untouched during the run (11:17–12:27 PDT; three audits ran their own tests in /tmp copies concurrently)
```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p …/.venv/bin/python -B scripts/shard_tests.py --workers 4 --split
SHARD SUMMARY index=1/4 modules=61 tests=1815 failures=0 errors=0 skipped=76 result=PASS
SHARD SUMMARY index=2/4 modules=62 tests=1658 failures=0 errors=0 skipped=5 result=PASS
SHARD SUMMARY index=3/4 modules=62 tests=1712 failures=0 errors=0 skipped=20 result=PASS
SHARD SUMMARY index=4/4 modules=63 tests=1491 failures=0 errors=0 skipped=2 result=PASS
WORKERS SUMMARY shards=4 modules=248 tests=6676 failures=0 errors=0 skipped=103 failed_shards=none result=PASS
```
Log: `/tmp/magistrate-21752427/replay-36/full-replay-0481bb0b.log`. Rounds 2 and 3 (`069f1e77`, `789542c6`) change only `joulewise/evidence_night.py`, its tests and the contract; their module was re-run alone at the bench under 3.13 (69 OK) and 3.11 (69 OK), and the modules the seats had seen fail under sandbox load (`test_run_night`, `test_sample_quiet_predicate_evidence`, `test_night_agent_install`, `test_axi_controller_events`) were re-run alone at the bench on the final tree (tail in the commit chain of 12:30 PDT).

## §3 Fix contract (row 3) and same-signature (row 5)
Fix contracts = brief 35 (twelve dictated closures from refuter 32 + Opus 34; counterfactual table: 17 tests FAIL→PASS against the `b678b1dc` module in memory) and brief 37 (three closures from fresh eyes 36); round 3 = the auditor's fail-closed prescription applied at the bench (record 38 §2). Same-signature: "the entry point silently diverges from the bench procedure" — closed at 38 §3 (bench step 0 gate in `check` and before publication; step-5 baseline declared deferred; root attempt records refuse); "an evidence-affecting side effect without a refusal path" — closed at 36 (atomic journals; recovery never uninstalls what it did not install; unpublish only on matching bytes); "stale-module evidence" — closed at 38 §1 (census, ancestry, installer and retry routing all execute in the clone).

## §4 Terminal review (row 12), 12:30 PDT 09-20
Final code head `789542c6` = `b678b1dc` (B1) + `472d12c5` (round 1, twelve closures) + `0481bb0b` (main merged: the py311 probe fix) + `069f1e77` (round 2) + `789542c6` (round 3, bench). Gauntlet: brief 30 → seat 30 (Astra xhigh; attempt 1 NEEDS_RULING → ruling 30a → attempt 2) → lead bench + diff read (33 §1) → refuter 32 (Astra xhigh, execution: BLOCKER F1 recovery destroys pre-existing jobs; F2/F3) + Opus 34 (contract: six should-fix) → brief 35 → seat 35 → fresh eyes 36 (PASS; F1 residual stale-module) → brief 37 → seat 37 → fresh eyes 38 §1 (PASS; one should-fix) → bench round 3 → fresh eyes 38 §3 (PASS, classes closed) → replay §2. Verdict: MERGE the records-only candidate (merge of main onto `789542c6`). Carried to slice B2: notice transport and reading/veto, courier execution, full `retry_allowed` clearance, the step-5 night-directory baseline, `ARG_MAX`-safe JSON via stdin, the runbook/handbook checklist replacing record 17's script set. A FIRST LIVE USE of `check`/`publish-install` must be watched step by step at the bench (fixtures prove composition only).

## §5 Hosted checks on the PR head (row 11), 13:08 PDT 09-20
PR #374 head `d2b9d7da` (records-only merge of main `9f70d0e7` onto `789542c6`): 15/15 checks pass — build: pass; calibration-exits-exclusive (3.13): pass; calibration-writer-crash-matrix-exclusive (3.13, 1): pass; calibration-writer-crash-matrix-exclusive (3.13, 2): pass; changes: pass; fences: pass; gate-ledger: pass; installed-wheel: pass; quick: pass; test (3.13, 1): pass; test (3.13, 2): pass; test (3.13, 3): pass; test (3.13, 4): pass; test (3.13, 5): pass; test (3.13, 6): pass. Merge proceeds; the post-merge matrix (incl. the 3.11 shards) is watched after the merge (fix forward if red).

Bench tail (12:30–12:42 PDT, final tree `789542c6`): `tests.test_run_night tests.test_sample_quiet_predicate_evidence tests.test_night_agent_install tests.test_axi_controller_events` → `Ran 370 tests in 752.845s OK`; `tests.test_evidence_night` under python3.11 → OK.

## §6 Post-merge matrix on main `e216ca00`, 13:32 PDT
Run 35534394828: conclusion SUCCESS — every job green, including all six 3.11 shards. Slice B1 is delivered end to end.
