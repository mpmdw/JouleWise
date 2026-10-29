GPT-6 (no more specific runtime model identifier is exposed)
VERDICT: REJECT

Reviewed `mpmdw/JouleWise` delta `5d80e12cd..e23cd1e7b`, PR #598. Authority: registration `docs/registrations/bytes_pack_v1.md` §21 item 3 and §7, with T1–T7. Python 3.13.5, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`. All execution used synthetic data; no hardware or real BYTES measurements. Production files were not edited.

1. **MAJOR — An existing output directory can route the transform's writes into the source export.** `scripts/bytes_thermal_lines.py:347`, `:349`, `:369`. Removal of the new-directory requirement permits `output/export` to be a directory symlink to the supplied source export. The top-level overlap check passes because the output root is separate. `mkdir(exist_ok=True)` follows the directory link; the leaf CSV itself is not a symlink. `write_copy` unlinks and replaces the source CSV. This is an executing source-protection failure, beyond the unchanged linked payload's acknowledged writability. Detach/check destination directory links before writing, including intermediate withheld directories.

   Repro from repository root:

   ```sh
   JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/by-therm-lines-rev-sol-2/delta_probes.py
   ```

   Output tail:

   ```text
   SOURCE_EXPORT_CHANGED True
   ```

   The repro creates an ordinary synthetic source export, sets `output/export -> source export`, and invokes `request-end-p1` with that source export. Its before/after source bytes differ. All changed files in this repro are temporary synthetic files.

2. **MAJOR — Reusing an output retains an obsolete export and certifies it as the current view.** `scripts/bytes_thermal_lines.py:333–357`. Files absent from the new output specification are never removed or replaced. First produce a request-end output with `--export`, removing member `a`'s OS code. Then change the archived pass to 2 and rerun request-end into the same output without `--export`. The new record correctly says pass mismatch and the new acceptance retains `a`'s original OS exclusion, but the previously copied export still restores `a`. The new manifest incorporates this stale CSV, so verification succeeds. The archive and blinded ingress now decide different membership. Existing-output support must not expose prior payload as part of a newly certified line.

   Repro: the same `delta_probes.py` command above. Output:

   ```text
   REUSE_ARCHIVE [('a', 'thermal.os_level_nonzero')]
   REUSE_CSV ['a,"",False', 'b,,False']
   REUSE_VERIFY []
   ```

3. **MAJOR — Deleting journal provenance enables a restoration that a mismatched seal forbids.** `scripts/bytes_thermal_lines.py:171–177`. `mismatch` starts false and is checked only if `derived/window_flags.json` exists. Thus a missing provenance file bypasses T3's comparison entirely; the archived journal is used to restore members without establishing that harvest read it. Treat unavailable provenance as a recorded undefined restoration, preserving the original codes and exit 0. Do not equate absence with a matching SHA-256.

   Repro: the same `delta_probes.py` command. It first supplies a mismatched sealed digest, then deletes only `window_flags.json` and repeats:

   ```text
   MISMATCH not defined (journal differs from the harvest's) changes 0
   MISSING_SEAL evaluated changes 1 codes []
   ```

   The positive mismatch case does preserve the member exactly as ruled. The defect is the missing-file bypass, not a demonstrated bad exclusion decision on a coherent complete archive.

4. **MINOR — A damaged manifest can crash `verify`, leaving the recorded change flag false.** `scripts/bytes_thermal_lines.py:402–408`. A syntactically valid damaged manifest containing `{"files":[{"path":7}]}` is accepted into `expected`. Sorting its integer path together with the real string paths raises outside the error handler, despite the already detected manifest hash mismatch. This violates T4's exit-0 recorded-flag behavior for manifest damage. Validate the manifest's entry types, and complete the flag write on malformed entries.

   Repro: the same `delta_probes.py` command. Output (the order of the type names can vary):

   ```text
   DAMAGED_MANIFEST exit 1 tail TypeError: '<' not supported between instances of 'int' and 'str'
   DAMAGED_MANIFEST_FLAG False
   ```

## First-round finding dispositions

| Earlier finding | Delta disposition |
|---|---|
| Sol 1 / Opus 1: grouped-blind withheld refusal and model loss | Closed on fresh coherent outputs by T1. Both original campaign scripts and the strengthened campaign replay pass. |
| Sol 2 / Opus 4: unhashed mutable linked view | Knowingly superseded by T4's manifest plus explicit verification, rather than immutable links. Ordinary linked reduction drift, additions/deletions and re-acceptance are detected. Findings 1, 2 and 4 above identify remaining output/verification defects. |
| Sol 3 / Opus 2: nonphysics refusals | Closed for the named journal-unavailable, CSV/archive disagreement, absent changed member, pass mismatch and missing-gap cases. CLI writes records with exit 0; independent evaluable members still change. Overlap and request-end-would-add remain stops. |
| Sol 4: uninterrupted counting acceptance chain | Knowingly superseded by T7. The real acceptance chain's non-counting fixture limitation remains visible, while the real cross-pass identity and separate counting campaign analysis are exercised. |
| Opus 3: journal provenance | Matching and mismatching digests work; missing provenance remains defective (finding 3). Hull does not consume journal readings for its decision. |
| Opus 5: inconsistent `excluded` CSV field | Closed by T5. Rewritten rows use the exporter's boolean rule, `bool(codes)`, including withheld rows. |
| Opus 6: commit without dirty indication | Closed by T6. Both producing commit and tracked-tree dirty boolean are recorded. |

## Executed

All commands below used Python 3.13 with the two environment variables stated above. Repro scripts are committed in `.codex-report/by-therm-lines-rev-sol-2/`. The six `sol_*` / `opus_*` scripts are byte copies from the two pinned earlier review commits, `977bfb37a` and `72e28c5c2`; `JW=/workspace/JouleWise` and `/tmp/jw` pointing to this checkout satisfy their original imports. No compound command uses `cd`.

- Read all of `.codex-report/BY-THERM-LINES.md`, including Fix round 1, both first-round reports, the delta, registration §21 item 3 and §7, and the exporter/analysis withheld-store paths.
- `sol_campaign.py`: completed. Native s2/s5 exports succeed on both passes; science censuses are 100/100 for s2 and 50/50 for s5. Its deliberate linked-reduction mutation still changes analysis while `source_sha256` matches; that old observation is superseded by manifest verification, not claimed cured by immutable links.
- `sol_probes.py`: `PROBES_PASS`. Exact boundary, duplicate-code, secondary-code, reference, missing-span, malformed-line and guarded JSON sentinel checks pass. Former refusal branches no longer print refusal; linked mutation remains possible as T4 permits.
- `sol_chain.py`: completed. Real harvest, real B6 acceptance, export and transform run without the old acceptance adapter. Archive/CSV changes agree; repeat transforms and source protection pass. Analysis remains explicitly unavailable for the fixture's independent non-counting and mock-predictor reasons, as T7 allows.
- `opus_chain_analysis.py`: `SUMMARY 30 / 30`. s5-p1 now produces its heldout line; source/output quads go 9→10 post-commit. s2-p2 goes 10→9. Archive-root ingress still reports the pre-existing export-locator unavailability; export ingress computes.
- `opus_probe_postcommit_heldout.py /tmp/btl-ana-skg3hi_y`: both source and line have 100 science records, both Qwen models survive. The changed fit model goes 9→10 quads; heldout remains at 10.
- `campaign_delta.py`: completed with assertions, extending the native s2/s5 campaign to both passes, both analysis stages, before/after commit. Public+withheld physical row totals (including 13 reference rows) are 113 for s2 and 63 for s5. Pre-commit public totals are 63 and 13. Every source row ID survives, every yielded model/status survives, and output codes equal output acceptance codes exactly. Archive and blinded change lists are checked by the earlier scripts and supplied tests. Copied stores are `SESSION.withheld.csv`; tracing `_export_rows` proves `_stage_export_rows` opens the copied store after commit and never before. Verification passes on these fresh outputs.
- `view_and_gap.py`: three real journal-gap variants, each tested at gap arguments 0, 6 and 1000. Full `thermal.os_level_nonzero` tuples compare exactly equal while `thermal.unmeasured` changes (`True, True, False`). In production `thermal_member_flags` (`harvest.py:3077–3086`), `_thermal_nonzero_samples` and the OS tuple are computed independently before `_uncovered` receives the gap argument. No path from that argument changes an OS decision. Added and deleted payload files give exit 0, both paths and the true recorded flag.
- `view_and_gap.py /tmp/btl-chain-lzxugb68`: after normalizing to the same acceptance invocation, real `accept_archive(..., replace_existing=True)` replaces byte-identical `derived/b6-flags.jsonl`. Its size and SHA-256 stay identical; changed integer inode/mtime metadata causes verification to report it. The initial invocation changed flag bytes, so that alone was not counted as proof of the byte-identical case.
- `delta_probes.py`: all four findings above reproduced, with no production changes.

- `opus_chain_test.py`: `SUMMARY 22 / 24`, exit 1. The two failures are exactly the superseded pass-mismatch-refusal and linked-files-read-only expectations; all other checks pass. The current port in the supplied module passes 29/29.
- `python3.13 -m unittest tests.test_bytes_thermal_lines -q`: 19 tests, OK, 710.285 s, exit 0. This includes the former-refusal CLI records, partial disagreement preserving other evaluable members, compressed journal, modified-file modes, JSON/public/withheld sentinels, and both reviewer ports.
- `python3.13 -m unittest tests.b6.test_bytes_p2_thermal_window tests.test_harvest_b5_window -q`: 198 tests, OK (11 skipped), 806.735 s, exit 0. Pass-1, block-5 and alpha byte-identity replays pass.

Blinding: guarded JSON and CSV sentinel tests cover energy, power, duration and rail lexemes, including quoted multiline withheld fields and sidecars. Measurement fields remain opaque, byte-preserved, absent from records/stdout. T4 necessarily hashes payload bytes; this does not decode measurement values. No blinding defect was found on these production-shaped inputs.

Numbers: no float tolerance or agreement bar is introduced. Code sets, row counts/IDs, integer-ns stamps, SHA-256 strings and inode/mtime integers use exact equality. The helper's pre-existing float conversion of the discarded coverage threshold is not an agreement tolerance. No numerical bar was invented.

Bound analysis SHA-256 remains `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`; harvest remains `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744`. `git diff --check` passes.

PR #598 still has head `e23cd1e7bf7e78d79565ace77dbed72d02b70c95`. At 2026-10-29T05:41:11Z, [head CI run 40823112744](https://github.com/mpmdw/JouleWise/actions/runs/40823112744) has nine successful jobs: fences, build, changes, quick, both calibration-writer crash-matrix shards, calibration-exits, test shard 6, and installed-wheel. The other eleven test shards are in progress. There is no red job to attribute at this snapshot; the overall suite is not yet green. The separate gate-ledger run is skipped.

## Decisions I made

- Reject for source modification, a certified stale export and an unproven restoration; these bear on source custody or which members count. The fresh coherent grouped-export path is substantially repaired.
- Apply T7 as written; do not demand a counting real-acceptance fixture that the ruling explicitly waived, or disguise fixture rejection as a computed result.
- Accept T4's linked-view design and control-file hashing arrangement. Report concrete failures of the new mechanism, not the deliberately retained links themselves.
- Treat missing journal provenance as unavailable evidence, not permission to restore. This asks for no new scientific policy.
- Keep comparisons exact and leave analysis, harvest, estimator arithmetic and registration untouched. Write only this report and its repro directory; no project-state or implementation changes.
- Report the model identity actually exposed by this runtime; a more specific exact deployment identifier is unavailable and is not guessed.
