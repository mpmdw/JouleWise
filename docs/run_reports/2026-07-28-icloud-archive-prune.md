# 2026-07-28 — iCloud archive + verified selective prune of runs corpora

**Operator:** Fable (lead), Ed-authorized 2026-07-27 ("get as much off disk
to iCloud as possible, verify on iCloud before deleting") — resolving the
two open disk questions from the 2026-07-27 ruled plan: iCloud-only is
acceptable for bulk traces, and delete-after-verified-upload stands.

## What was done

1. **Audit.** Existing iCloud backups (`runs/` 07-17 snapshot; a9, a10,
   +bounds 07-25) checked by file-count/byte parity. a9/a10 complete;
   local `runs/` had diverged from its 07-17 snapshot (reorganized), so a
   fresh `runs-20260727` snapshot was taken.
2. **Archive.** All 22 not-yet-backed-up corpora hash-manifested
   (`MANIFEST.sha256`, sha256 of every file) and APFS-cloned (`cp -Rpc`,
   zero disk cost) into
   `~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/`.
   Name-set + byte parity verified per dir, 22/22 OK.
3. **Upload verification.** `brctl evict` attempted on 100% of the 23,162
   archived files — evict success is the upload-completeness detector
   (per the ruled standard; a local hash proves nothing about cloud
   durability). Sole refusal: a Finder-created `.DS_Store` (macOS refuses
   evicting those categorically; removed).
4. **Durability verification.** Per corpus (all 27, incl. the four
   pre-existing a9/a10 backups against locally derived manifests):
   rematerialized 100% of small files (<1 MB) plus the 3 largest + every
   20th large trace, rehashed against the manifest. **20,028 files
   rehashed from iCloud, 0 mismatches.**
5. **Prune.** Only after a per-dir VERIFY-OK marker: deleted local
   `powermetrics*.plist` traces >10 MB (verified to be the only >10 MB
   file class) — **1,848 traces ≈ 61 GB**. Every small evidence file
   stays resident; each pruned dir carries `PRUNED.md` + its
   `MANIFEST.sha256`.

## Keep list (no deletion)

- `runs_window_a10_20260725(+_bound)`, `runs_window_c_20260726(+_bound)` —
  mint #1 inputs, fully resident (and archived).
- `runs_window_a5_quarantine` — quarantine is evidence (archived, untouched).
- `runs/example-mac-mlx-*` (six frozen acceptance-gate bundles, incl.
  their >10 MB idle plists) and `runs/experiments/` custody.

## Post-conditions and verification

- Disk: 33 GB → **86 GB free**.
- `tests.test_corpus_strict_validation` re-run post-prune: 3/3 OK,
  including the six-bundle strict read-only gate (lead-run).
- Keep-list file counts verified unchanged (1196/302/966/302/22).
- Full canonical suite re-run post-prune: `Ran 2194 tests`, `FAILED
  (errors=2, skipped=12)` — both errors are `test_build_site_parsers`
  Lakebed-budget tests, **pre-existing at HEAD and independent of the
  prune** (the `32e510a` Session History rewrite uses
  `docs/process_traces/` pointers the site-builder parser rejects;
  reproduced by running `parse_session_history` on the pristine HEAD
  file). Ruling needed on parser-vs-doc; recorded in RUN_STATE
  "Current Verification".
- Restore path for any trace: `brctl download` under the archive dir;
  manifests authenticate any restore.
- The traces are now **iCloud-only** (single durable copy). If a second
  physical copy is wanted, say so and it becomes a queue item.
- Upload churn is finished (all files evicted server-side-complete), so
  the next quiet measurement window is not competing with a background
  upload.
