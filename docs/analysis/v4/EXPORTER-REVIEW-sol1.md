# Native exporter review — Sol seat 1 — 2026-11-08

**Verdict: HOLD** at `6d0f9c73145cc19eea6175d824f45d8e8b3b93a7`.
Branch: `align/2026-11-08-exporter-review-sol1`. Review changes are witnesses and this report only.
No exporter fixes, coordination-state edits, pushes, network requests, model downloads, live measurements,
or real custody reads were part of the review. Authority: origin/main RUN_STATE 235–247 and release runbook
§§6a–6a.2. The brief's prohibition on the full suite and coordination writes overrides the general checklist.
Build-side inspection used this branch's pins, engine `72410b0b4f725d770298a301a55802e70d466537` and
recompute `7b06c6058efa211fd14acb14838cc84c13694012`. It is not a certification of the newer r23m
build/comparator combination discussed in §6a.2.

F1 is a normal-producer functional blocker. F2 and F3 can hand both builds the same wrong input without
breaking any of the exported file digests. These are operator/functional failures, not adversarial races.
F4 is a missing required input binding. No methodology ruling is needed to establish these defects.

## Findings

### F1 — HIGH: the actual session producer's state is rejected

`scripts/align_v4_session.py:61–63` writes five `v4_series` keys, including `extra_sentinels` and
`admission_sha256`. `scripts/export_v4_series.py:73,675` allows only three keys and therefore refuses the
ordinary producer's C/T session with `unknown_contract_key: v4_series` (also series-selected W1).

Witness: `NativeCustodyWitnesses.test_actual_prepare_session_is_accepted_by_the_exporter`.
It calls the real `prepare()` state-writing code with synthetic files and stubs for host restoration,
kit generation/admission and the lower preparation layer. It inserts that actual produced object into an
isolated completed synthetic C1 restore, updates the committed finalized-manifest digests, and invokes the
exporter. The refusal is precisely the two producer keys, before member arithmetic.

The §6a.2 fixture-vs-producer sweep misses this: `tests/v4_release/native_series.py:202–209` handwrites
`session.json` with only the three exporter-accepted keys. Its sessions are production-layout, but its
session-state object is not the actual producer's complete object.

**Fix:** admit and validate the current producer fields; make the native fixture use the actual session-state
projection. Do not remove producer provenance to get an export through.

### F2 — HIGH: an all-null capture inventory hides existing captures from both builds

The exporter opens and checks the restore only inside `if captured` (`export_v4_series.py:668`).
`captured` comes entirely from the record's capture inventory. The later `capture_missing_from_record`
check consequently sees no session when *every* inventory entry is null. Neither the finalized manifest's
22 plists nor the supplied `session_root` is checked.

Witness: `test_all_null_capture_inventory_must_not_hide_finalized_plists` commits an all-null copy of C1's
inventory while retaining the original finalized manifest, raw digest inventory, completed final desk,
and restored bytes. The witness independently counts 22 plist entries in that bound manifest. Export
succeeds and **both layouts mark every member `captured: false` under `C1-z1`**. This is inconsistent
custody, not a genuine zero-capture attempt. A partially null inventory has a check; all-null bypasses it.

**Impact:** a dropped/defaulted capture map can erase a real window, create a spurious retry/refusal,
and change the structural replacement/calibration history. Comparing the two exports cannot recover the
omitted captures. The exporter-level wrong-input agreement is executed; a complete threshold-changing
dual-build release was not run for this mutation.

**Fix:** establish absence independently from the bound custody/manifest, including all-null attempts;
refuse if a purported absent member has a captured plist. Preserve the genuine no-restore zero-capture
case only where absence is actually established.

### F3 — HIGH: incremental export silently ignores a changed configured prior record

`_state_for()` (`export_v4_series.py:1032–1040`) matches only `attempt_id`. The prior-window checks and
index rebuild (`:999–1000,1016–1018`) trust that state without matching `record_commit`, `record_path`,
the finalized manifest, or a successor's `final_record` binding to the current config.

Witness: `test_incremental_export_must_not_reuse_a_different_configured_w1_record` first lands W1,
then commits a different, independently readable/final W1 record with a changed ordinal-5 exclusion.
It points the config at that new record and exports C1. Export succeeds while `state/W1.json` still
identifies the old commit. The same old W1 raw row/adjudication continues to feed both layouts.

**Impact:** resuming into a reused output directory after correcting a config or final adjudication can
produce a perfectly digest-consistent shared input from the wrong configured custody. A full dual-build
release for this mutation was not run; the ignored config and successful stale export are executed facts.

**Fix:** bind landed state to the full source selection, including final-adjudication/successor identity,
and compare it before using any prior state. Refuse drift and require a fresh export root. An immutable
landed window must not be silently substituted for the requested record.

### F4 — MEDIUM: series input digests are optional in the implementation

§6a.1 requires `u3_bar`, `r1_references`, and `registration_inputs` as `{path, sha256}`. `read_ref_file()`
(`export_v4_series.py:267–275`) verifies the SHA only *if the key exists*. All three files can be read
successfully without it, giving both builds an unpinned path-selected reference.

Witness: `test_series_reference_files_require_the_declared_digest` removes each SHA separately from the
otherwise valid synthetic input config. `series_inputs()` accepts all three cases (three failed subtests).
The frozen allocation is separately protected by the hard-coded `21313cc2…` check and is not this defect.

**Fix:** require the exact reference shape and a valid SHA-256 before opening the file, then compare it.
Reject a missing binding rather than treating it as an optional convenience.

## Coverage and limits

| Requested surface | Review / executed evidence |
|---|---|
| `identity_sha256` | Known canonical bytes, turn order and boundaries checked; missing IDs are covered by the existing units. Export derives from the verified `align_turns.jsonl`, with the same digest added to the recompute Episode. |
| WP22 `registered_span_ns` | First G0 in recorded interval order, otherwise episode start, through episode end. Existing and new controls pass. This is the explicit rule, not a minimum over all G0 starts. |
| Thermal projection | Native W1/C1 sidecar JSON array equals production rows; recompute JSONL is compared to `thermal_desk.normalize_journal()` for every captured member with a sidecar. Optional ungated-anchor sidecars remain optional. |
| Raw references / digest binding | Changed-byte `Session.read` and streaming `verify_file` controls pass for config, kit/plan/result-shaped files, KM003C, plist, thermal and battery journals. Native prefix controls rehash exported config, planned config, Episode and journal refs and check plan/result/raw-source census membership. Kit/plan/result have their additional binding paths by inspection; F4 is the reference-input exception. This is not a claim that every omission/mutation was run end to end. |
| Plan ownership | `plan_owner_check` checks W1/C/T headers, window, manifest and optional attempt. Existing unit controls pass. Per-ordinal kit digest and writer bytes are checked for captures. Both pinned loaders also validate ownership; no new owner-check defect found. |
| Seed index vs derived seed | All 40 captured native W1/C1 Episodes preserve the seed index, distinct from the roster's expected derived seed. Export roster is checked against frozen fields. Both pinned loaders' config/seed checks were inspected, including anchors; no seed recomputation was substituted in the exporter. |
| Production run IDs | C/T non-anchors checked against `align-v4-<slot>-eNN`; anchors get series-unique prefixes. W1/anchor local IDs remain plan-derived and the engine validates them. No invented rename was added. |
| Frozen R24 | Every successful export passed `frozen_allocation()` against the full 18-window `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c` manifest. Prefix output still carries the full allocation. |
| A27 | Inspected roster classification and pinned engine `_member_output`/aggregate sealing and recompute `is_c_sabotage`, `member_public`, aggregate/reduction public projections. Scored C sabotage receives the sabotage marker; 30B anchor sabotage remains anchor. The exporter emits raw analysis inputs, which contain outcomes and must stay inside the sealed analysis workflow; its CLI summary is structural. No new exporter-specific seal bypass established. **Full public-output noninterference is not certified:** the complete release module was interrupted and §6a.2 already records outstanding build/comparator gaps. |
| Zero captures / retries | Genuine C2 empty prefix control passes; a second empty C2 attempt has a separate record ID and the same slot. F2 is the all-null inconsistency. Captured-retry dual-build analysis was not completed in this run. |
| `kit_not_normalized` | Inspected the exact writer-byte equality guard in `planned_kit`; valid compact/non-normalized kits are refused, invalid kits remain the builds' `config_invalid` responsibility. Existing dedicated e2e witness was read, but the interrupted module did not execute it. |
| Incremental / determinism | Honest W1 → C1 → empty C2 and byte-identical re-export (excluding the append-only timing log) pass. F3 covers stale selection across invocations. No decision cache or throughput optimization was introduced. |
| Refusal / guessing | Normal units and raw mutation controls pass. F2/F3/F4 demonstrate silent acceptance instead of refusal; F1 demonstrates incorrect refusal of the normal producer. |

### Restored Air copy and JW-EXT

The documented JW-EXT inbox is a **compressed offload store**. Harvest-off `unpack` restores its verified
copy at the finalized manifest's original `source_root` (harvest-off runbook §2a; `docs/ops/AIR-OFFLOAD.md`
§1a). Export config `session_root` points to that restored tree, not to the inbox/payload directory;
`records_repo` and `kit_root` are separate configured roots. The exporter checks `source_root` equality
and reads explicit session paths, without discovering a home-directory custody tree or model location.

The completed synthetic W1 and C1 used here went through the real finalize/pack/unpack helper before
their records were committed; it removes the original MBP-side copy. Normal configured restores export.
F1 shows why the actual production state still fails. The test's alternative synthetic path is rebound
before finalization; it does **not** assert that an already finalized offload can be relocated.
No real JW-EXT inbox, Air custody, SSH route, or cross-host hardware gate was inspected or validated.

## Verification

Every unittest invocation used one module per process, sequentially, under Python 3.13. No full suite.
Common environment:

```sh
env PATH=/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin TMPDIR=/private/tmp \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 JW_B5_SYNTHETIC_ONLY=1 JW_WP22_FULL=1 \
  JOULEWISE_BACKUP_ROOTS= GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 \
  python3.13 -B -m unittest -v MODULE
```

- `tests.v4_release.test_exporter_units`: **16 pass**, 1.027 s.
- `tests.v4_release.test_exporter_e2e`: **interrupted in setUpClass**, exit 130, before any test result;
  roughly seven minutes of synthetic setup. It reached completed W1, C1 and an empty C2, then was
  stopped during C2's captured retry to protect the brief's test budget. This is not a passing baseline.
- Initial `tests.v4_export.test_review_sol1`: 7 tests, 55.664 s; 3 pass, four methods fail (six failure
  records because F4 has three subtests). Required-property assertions are intentionally red.
- Final `tests.v4_export.test_review_sol1`: **8 tests in 208.708 s; 4 pass, four methods fail**
  (six failure records: F1, F2, F3 and F4's three subtests), exit 1, no errors or skips. The honest empty
  retry control passes. The synthetic fence reports **0 forbidden custody accesses** and 0 redirected
  home custody probes. These remain ordinary required-property failures, not expected failures.
- Total test time, including the interrupted setup and both witness runs, was approximately 12 minutes,
  below the brief's roughly 20-minute ceiling.
- `PYTHONPYCACHEPREFIX=/private/tmp/exporter-sol1-pycache python3.13 -m compileall -q joulewise tests`:
  exit 0; caches are outside the checkout. Explicit compilation of the two new Python sources also passes.
- `git diff --check`: exit 0.
- `shasum -a 256 configs/campaigns/align_v4/series/series_manifest.json`: exactly the frozen
  `21313cc2791865e01f322c24606db62ba2ac6a65adda6d737e5b7432bef2ad5c`.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`: exit 2,
  `PermissionError: [Errno 1] Operation not permitted: 'ps'`. No rows/count could be observed; this is
  **not** a clean fixture census. The census signalled no process; only this review's broad test was
  interrupted, and its own exec session exited 130. The blinded analysis job was left alone.

For the focused run, `JW_V4_SOL1_SYNTHETIC_CONFIG=/private/tmp/exporter-sol1-recovered-config.json` selected
only the completed synthetic W1/C1/empty-C2 prefix from the interrupted setup. The config was built from
its committed records and digest-bound inputs, with synthetic R1 reference numbers in the same shape
as `native_series.build`. Tests copy its records before mutations and use the **same production battery
join serially** to limit CPU. They never mutate shared raw fixture bytes. Without that optional explicit
fixture config, the witness builds this three-attempt prefix itself through `native_series.build`.
It may take several minutes. Temporary logs are `/private/tmp/exporter-sol1-{baseline,witnesses,witnesses-final}.log`.

## Handoff

Touched: `tests/v4_export/__init__.py`, `tests/v4_export/test_review_sol1.py`, this report.
No changes to `RUN_STATE.md`, `TASK_QUEUE.md`, the state kernel, or `tests/test_gen_state.py`.
No peer delegation or external consult was used; the seat remains independent.

Next exact step: lead adjudicates F1–F4, fixes the producer-state schema and the three binding/refusal
gaps, then reruns this witness module without weakening its assertions. Follow with the entire intended
native exporter e2e against the chosen final build pins and an authorized real-Air restore/export gate.
No MLX implementation changed; the controller's native MLX path here is synthetic. Native hardware
claims remain outside this review. The complete A27 release output and captured-retry build comparison
remain explicit verification limits, not assumed passes.
