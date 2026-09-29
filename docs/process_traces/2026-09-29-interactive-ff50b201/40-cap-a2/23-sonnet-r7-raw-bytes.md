# Where are the raw bytes of R7's three members with empty `raw/` directories? (refuter B3)

Sonnet 5.5 subagent of session ff50b201, read-only, 2026-09-29; filed by the orchestrator (condensed wording, facts unchanged).

**All three FOUND, hash-verified, in the iCloud archive; iCloud is the only copy.**

| Bundle (`runs_window_a9_20260724/instrument_validation/<id>`) | Expected sha256 of `raw/powermetrics.plist` (manifest = `instrument_evidence.artifact_sha256`) | Found |
|---|---|---|
| 20260725T005132-a64711b7 | `a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e` | 86,371,900 bytes, sha256 matches |
| 20260725T011533-0b5ec77c | `9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d` | 87,027,099 bytes, sha256 matches |
| 20260725T022712-0a9534f5 | `bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf` | 87,293,622 bytes, sha256 matches |

- Location: `/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/window_a9_20260724/runs/instrument_validation/<id>/raw/powermetrics.plist`; downloaded (not dataless placeholders). The other four artifacts of each iCloud bundle are byte-identical (`cmp`) to the repo copies. The digests also appear in `runs_window_a9_20260724/MANIFEST.sha256` lines 13, 18, 23. No second copy in any `JouleWise-*` worktree, night-archive, night-custody or mounted volume.
- Never committed: `.gitignore:34` ignores `/runs_window_*/`; no LFS.
- **The other 14 members:** all 17 manifests and evidence files hash to R7's pins; the 14 others' raw plists are present locally and hash to their manifests (12 in windows a–a8, restored locally around Aug 18 per the directory mtimes, no restore record found; 2 in a10, never pruned).
- **Why empty:** `runs_window_a9_20260724/PRUNED.md:1-9` ("PRUNED 2026-07-28T12:29:25Z. 28 powermetrics*.plist trace files … deleted locally after verified iCloud archival (Ed-authorized, 2026-07-27: iCloud-only acceptable, delete after verified upload)"); operator report `docs/run_reports/2026-07-28-icloud-archive-prune.md:1-63` (1,848 traces, ≈61 GB; rehash of 20,028 files from iCloud, 0 mismatches; restore by `brctl download` authenticated by the MANIFEST, line 57; "iCloud-only (single durable copy)", line 59). Not the D-078 time-anchor gate.
- **Did R7's numbers come from these bytes?** Yes, upstream. R7 `selection` (line 47): b_fiducial "re-derived from primary bytes"; `derivation_method.raw_custody` (line 523): bytes "taken from the operator backup archive and admitted only because they hash to the value bound inside each member's hash-authenticated instrument_evidence.json". The r5/r6 neutrality replays (`scripts/paper_anchor_correction_quantified.py:108`; `docs/process_traces/2026-08-19-refreeze-execution/r5-issuance/prove_r5_neutrality.py:31-54`) search the iCloud `JouleWise-backup` directory by hash; their member JSONs give the three members' `b_fiducial_s` = 0.02366861961761718, 0.029273357215668885, 0.028733193582380412, equal to R7's values. No R7-era replay record for the three was seen; R7 carries r5/r6 values forward (its `science_neutrality_evidence`, line 634, says the 38-member corpus replayed exactly).
- The checked-in verifier `tests/verify_calibration_acceptance_corpus.py` never reads raw plists (lines 75-127).
