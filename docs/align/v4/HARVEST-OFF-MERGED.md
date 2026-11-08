# Harvest off the MBP: merged build (R17, W1 integration item 7)

- **Branch:** `align/2026-11-08-harvest-off-merged`, started from `align/2026-11-08-harvest-off-opus` @ `19d8cfcee`.
- **Merged in (no rebase):** `origin/align/2026-11-08-v4-r11` @ `03253edca`, then `356c41c82` (delta5). That brings the arm's packet rebuild, the merged D/C/T series and the W1-blocker fixes.
- **Ruling:** RUN_STATE 228 R17. Agreement: `docs/align/v4/HARVEST-OFF-AGREEMENT.md` @ `ea5612686`.
- **Design and profile:** `docs/align/v4/HARVEST-OFF-opus.md`.
- **Builder:** Opus 5.5. A Sol review follows.
- **Data:** synthetic only.

## 1. What R17 adopts, and where it lives

| R17 item | Implementation |
|---|---|
| MBP does finalize, light triage and pack. The Air restores at the same path, then harvests, runs the full desk and reduces once. | `scripts/align_v4_harvest_off.py`: `finalize-manifest`, `pack`, `unpack`, `triage`, `desk`, `final`, `reduce`, `sweep`. Transport: `joulewise/align/apple/harvest_offload.py`. |
| **Provisional `member_eligibility` at the arm** | `scripts/align_v4_next_arm_packet.py`: a record committed before the Air desk finished carries a `light_triage` source and a `desk` placeholder (`status: running_off_mbp`). `WindowRecord.eligibility(allow_provisional=...)` derives the counts from the light triage's thermal section with no harvest exclusions, `status: provisional`. It is allowed only for the previous window, and only when the full desk is not due. |
| **Window k final before the arm of k+2, and before any arm the full desk gates** | Final sources come from record k itself (`pilot`, `desk`, `exclusions`) or from record k+1's `previous_final` = `{record_sha256, sources}`. That field must name record k by digest. Every older calibration record in the hash chain must be final, otherwise the refusal reads `R17: final eligibility of Ck must be recorded before the arm of the window after next`. A finally excluded member may not remain in `pool_members`. The last desk-passed state may point to the successor that carries the off-MBP desk (`last_passed_record.final_record`). |
| **Item 216's "from window 6" clause withdrawn** | `scripts/align_v4_series.py:bind_packet`: the C6 fence is gone; only the previous attempt may be provisional. The frozen series manifest's bytes are **unchanged**: they are seed-checked and pinned by `test_r11_delta5_sol2`. Its `fence_from: C6` field stays in those frozen bytes but is withdrawn by R17, and the binder no longer reads it. Refreeze the manifest only with the next paired seed check. The protocol B2 table, B3 §1, the frozen `member_eligibility` triage text and the series README are updated. |
| **Scoped in-run memo** keyed by content sha256; refusals never kept; dropped at run end | `joulewise/adapters/powermetrics.py:document_memo`, opened per member by `harvest.assess_member`. Unchanged from the Opus build. |
| **Workers auto-sized** to min(free cores, free memory ÷ measured peak per worker); sweep 2/4/6/8/10 | Runner `desk --workers auto [--sweep SWEEP.json]` (`auto_workers`, `free_cores`, `free_memory_bytes` from `vm_stat`). Without a sweep receipt, the peak is 8× the window's largest raw plist, the measured resident ratio. `sweep` harvests the restored window at each count into separate archives with `--profile`, recording wall time and the largest descendant RSS (the per-worker peak). |

**Ported from Sol** (as the agreement chose):
- **Threaded hashing:** `tree_inventory(workers)`, `Seams.io_workers`.
- **Step timing:** the stage observer, `joulewise/harvest_profile.py`, and `harvest_b6_session.py --profile/--io-workers`.
- **The record-bound transport manifest,** with one change. Sol's `harvest_transport` refuses symlinks, and every ALIGN session's measurement view is symlinks. So its finalized-manifest contract was folded into `harvest_offload` instead:
  - `finalized_manifest()` runs on the MBP at finalize, and its sha256 is committed with the record;
  - `pack(finalized=...)` and `unpack(finalized=..., finalized_sha256=...)` check the chain committed digest → finalized manifest → offload manifest → restored bytes.

  Sol's module is therefore not carried, since it would be a second, superseded transport.
- **Not taken:** Sol's one-entry parse cache, which R17 replaced with the memo.

## 2. Per-turn energy table: built and proven equal to PILOT.json

`joulewise/align/apple/turn_table.py`.
- **No new integral.** It runs the desk's own functions once on the Air:
  - `episode_summary` gives per-channel `per_turn_j` and segments;
  - `read_bundle_record` + `enrich_record` give `turn_owned_j`, half-widths, `gross_episode_j` and per-turn `owned_j`/decode clock.
- It digest-binds every input file.
- `reduce` writes `<run_id>/turns.json` next to the columnar `.npy` files, with digests in `MANIFEST.json`.
- **The gate is `equal_to_pilot`.** The table must equal what the full desk wrote into PILOT.json, compared after the same `finite_json` and JSON round trip the desk applies.
- **Proven** in `SyntheticV4SessionE2ETests`: every member of the synthetic session matches the PILOT.json written by the real v4 desk. A tampered PILOT.json per-turn value fails.

## 3. End to end on a synthetic v4 kit session (`SyntheticV4SessionE2ETests`)

**Session.** Three real native-endpoint bundles (fake MLX), gated by the registered synthetic gate policy so U1-U3 are evaluated. The v4 kit layout carries a synthetic U3 bar, WP19 receipt, R1 sensors and soak reference. The steps run through the runner CLI:
1. `triage --out light_triage.json`: the real `powermode_desk_check` without the harvest gives provisional eligibility and the record source the packet builder reads.
2. `desk --workers auto`: the real v4 desk with auto-sized workers. Only the harvest subprocess is replaced, by a synthetic archive writer that excludes one member; the harvest itself is proven separately (§4).
3. `final`: final eligibility.
   - It is a subset of the provisional set, and the excluded member is ineligible.
   - The captured count is equal.
   - `thermal_escalation` equals the light triage's, so U1-U3 ignore the harvest.
4. `reduce --workers 2`: columnar files bound to raw digests, and per-turn tables equal to PILOT.json.

## 4. MBP-versus-Air archive byte identity: re-run on the merged tree

`SamePathHarvestEqualityTests` re-runs on the merged tree. The merged harvest now includes the ported threaded hashing and stage observer:
- the MBP side uses 1 worker with dedupe off;
- the Air side restores the verified copy at the same path, with 3 workers and dedupe on;
- all 177 archive files are identical, and `harvest.json` is equal.

With real clocks and distinct boots, only the declared provenance fields differ. Sol's ported `test_complete_harvest_equal_on_verified_copy_in_canonical_namespace` (`tests/test_harvest_off_io.py`) now runs through `harvest_offload` with the record-bound manifest and 2 I/O threads, and is equal byte for byte.

## 5. Measurements (synthetic B5 window, 6 members, Air nearly idle, load 2-3)

| Harvest | wall s | peak worker RSS MB |
|---|---:|---:|
| 1 worker, no memo (today) | 14.88 | n/a |
| 1 worker, memo | 3.72-3.73 | n/a |
| 2 workers, memo | 2.74 | 155 |
| 4 workers, memo | 2.33 | 163 |
| 6 workers, no memo | 5.00 | 186 |
| 6 workers, memo | 2.17-2.31 | 183-197 |
| 8 workers, memo | 2.23 | 193 |
| 10 workers, memo | 2.24 | 197 |

Reading the table:
- On the unloaded Air the memo alone gives 4.0×, and the memo plus 6 workers gives **6.4× on the whole harvest**.
- The knee is at 4-6 workers for 6 members, since there are never more useful workers than members.
- Real members are about 1 GB. There the knee will be set by memory (about 8× the largest plist per worker), which is why `auto` sizing reads the measured peak.
- **Native N4/N5** is the Air `sweep` on the first real restored window.

## 6. Tests (one module per process)

All pass. The new and changed modules are these:
- `tests.align.test_harvest_off`: 30 OK;
- `tests.test_harvest_off_io`: 4 OK;
- `tests.align.test_v4_next_arm_packet`: 34 OK, including the 6 R17 tests;
- `tests.align.test_v4_series`: 16 OK;
- `tests.align.test_v4_series_e2e`: 9 OK.

Unchanged modules: `test_v4_cadence` 30, `test_v4_registration` 22, `test_v4_executed_closure` 4, `test_v4_kit` 116, `test_thermal_desk` 25, `test_v4_powermode_record` 9, `test_v4_w1_blockers` 16, `test_km003c` 23, `test_pilot3` 7 (1 skipped), `tests.test_powermetrics` 61, `tests.b6.test_session_wrapper` 6, `test_r11_delta_sol2` 6, `test_v4_dc_sealing` 2.

`tests.test_harvest_b5_window` was not re-run on this Air: its fixture follows a real iCloud custody locator (Opus doc, note under §9). It needs CI.

The full list of modules run:
- `tests.align.test_harvest_off` (new E2E, R17 sizing and record binding);
- `tests.test_harvest_off_io` (Sol, ported);
- `tests.align.test_v4_next_arm_packet` (+6 R17 tests);
- `tests.align.test_v4_series`, `tests.align.test_v4_series_e2e` (fence → R17);
- `tests.align.test_v4_cadence`, `test_v4_registration`, `test_v4_executed_closure`, `test_v4_kit`;
- `test_thermal_desk`, `test_v4_powermode_record`, `test_v4_w1_blockers`, `test_km003c`, `test_pilot3`;
- `tests.test_powermetrics`, `tests.b6.test_session_wrapper`, `test_r11_delta_sol2`, `test_v4_dc_sealing`.

## 7. Open items for the Sol review and the lead

1. **The light B bar.**
   - For a provisional record, `battery_window` reads `v4_B_bar` from the light triage. That is the desk's own check without harvest battery codes, using the desk's journal join.
   - A harvest-only `battery.member_span` (registered-threshold join) can turn it false later. The k+2 final then recounts the streak.
   - A first non-pass resumes automatically anyway (ruling 9), so the exposure is one window.
2. **Who commits what.**
   - The magistrate's record step must commit `light_triage.json` (from `triage --out`) and the finalize-manifest sha256 with record k.
   - Record k+1 must carry `previous_final` for k once the Air desk passes.
   - The series ledger's `last_passed_record` gets `final_record` when the desk passed off the MBP.
   - The runbook text for the magistrate is not written here.
3. **The sweep runs on the restored session** and writes separate archives under its `--out`. It needs the disk headroom (the Air now has 49 GB free; one real window is 18.6-26.4 GB).
4. **`gpu_active_mhz`** in the columnar file is still diagnostic, as in the Opus doc §10.
