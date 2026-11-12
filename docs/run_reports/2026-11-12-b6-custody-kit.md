# Block 6 custody kit (BRIEF-B), 2026-11-12

Opus 5.5 build seat, on the Air, 12:45-13:05 PST. Branch `analysis/2026-11-12-b6-custody-kit`, worktree
`/Volumes/JW-EXT/jw-wt/b6-custody-kit`, base `b4e4df8ed` (R12, fetched read-only from
`/Volumes/JW-EXT/jw-wt/sol-p1-b6-r12c` into `snap/b6-r12-b4e4df8ed`; the short sha was not fetchable by name, so
the branch was fetched and the full sha `b4e4df8ed7df6bd3b85bcf3bcf2eae7fa07c4e71` pinned). The branch is pushed to
origin as a backup; it carries the R12 snapshot it is based on (no rebase onto R12 until R12's review, RL-100). Synthetic archives only; no real session, custody, `night-*` or archive path was opened, listed or stat'ed.

## What was built

`scripts/b6_custody_kit.py`, stdlib only, three subcommands. It hashes bytes and reads file names. The only session
content it parses is the path column of `sources/SHA256SUMS`, and only after that file's digest matches the source
manifest. Exit 0 ok, 4 refusal (`refused: <code>` on stderr; for an unexpected exception only its type name), 2 usage.

- `manifest` (source): per `--session`, the SHA-256 of `sources/SHA256SUMS`, `harvest.json`,
  `derived/b6-acceptance.json` and the desk compression log (inside: `<archive>/compression.jsonl`; adjacent:
  `<archive>.desk/compression.jsonl`; both present is refused), every file outside `sources/` by name and digest,
  every file of the adjacent `.desk` folder, the archive's file count and total bytes, the SHA-256 of
  `--loop-attempts` and optional `--loop-state`, and a `copy_path`. Refuses symlinks, FIFOs, a missing pinned file
  and an existing `--out`. Prints the manifest's own SHA-256.
- `verify` (copy): checks `--manifest-sha256`, then per session rehashes every `SHA256SUMS` row (a row whose plain
  file is absent is read as `<name>.zst`, decompressed by `zstd -d -c` into a pipe and hashed; nothing is written),
  every manifest-digested file outside `sources/`, and the `.desk` folder. Refuses a missing file, an unlisted extra
  file, a digest mismatch, a `SHA256SUMS` digest unlike the manifest's, a changed file count or total bytes, a
  symlink and a non-regular file. The receipt holds counts and bytes only, plus the manifest digest, the copy root
  and the zstd path and version.
- `inputs` (Air): the run-input document, `host: "Air"`, `l9_audit` from `--l9-audit`. Every digest comes from the
  SOURCE manifest; the copy is never rehashed for a pin (test `test_inputs_digests_come_from_source_manifest`
  changes the copy's `harvest.json` after verify and shows the pin still carries the source digest). Sessions are
  keyed by absolute copy path (the exact pin form, so the repeated production basename `archive` is safe).
  `--list-names <copy_path>` prints that session's authenticated names for the person writing `mapping.json`.

## Schema targeted

`joulewise/b6_analysis_inputs.py` and `session_input_pin` / `main` in `scripts/independent_recompute_b6.py` as of
`b4e4df8ed` (sha256 `f46367d5…` and `ee00548d…`). Emitted per session: `harvest_sha256`, `acceptance_sha256`,
`sha256sums_sha256`, `files` (source digests of every `derived/` and `withheld/` file), `meter_streams`,
`contention_journal`, optional `clock_journal`, `copied_records` (eight families), and `compression` as
`{"path", "sha256"}` (inside) or `{"external_path", "sha256", "relocations"}` (adjacent). Root `external` carries
`loop_attempts` and optional `loop_state`. Neither pinned file nor `independent_recompute_b5.py`
(`d49103e8…`, re-checked) was edited.

## Interpretations a reviewer should check

1. **Citable mapped paths (ruled, RL-100 item 1).** `SHA256SUMS` lists `sources/` only, but both the seat-7
   fixture pins and R12's real-shaped pins map copied families to `derived/flags.jsonl`,
   `derived/b6-acceptance.json` and `withheld/b6-neg8.json`. RL-100 rules that a mapped path must be a `SHA256SUMS`
   row (as `sources/<row>`), a key of the pin's emitted `files` (`derived/`, `withheld/`), or one of the three pinned
   files (`harvest.json`, `derived/b6-acceptance.json`, `sources/SHA256SUMS`). Any other manifest-hashed file (the
   inside desk log, a marker file) is refused; `--list-names` prints exactly this set. Witness
   `test_mapping_path_hashed_but_not_emitted`; mutant RL-100 below.
2. **The manifest digests every file outside `sources/` and the `.desk` folder.** The brief lists four digests plus
   count and bytes. R12 shows flags and spans may be absent from `harvest.outputs`, and `AuthenticatedInputs` takes
   them through `files`; those digests must come from the source, so the manifest records them. These files are small
   (JSON records), so the source-side cost is negligible; the large `sources/` tree is not rehashed at the source.
3. **"Byte-identical public output."** Not literally possible without editing the recompute: the restricted output
   records `inputs.run_inputs_sha256` (two different documents by construction) and the public output carries
   `restricted_sha256`. The test proves the restricted outputs differ in that one field only, and the public files are
   byte-identical once the `restricted_sha256` value is removed.
4. **Relocations.** For an adjacent desk log the kit adds `{<source archive path>: "."}`. The other prefixes (custody
   root, run roots; R12 takes them from `session.json`) the person supplies as `relocations` in `mapping.json`. The
   kit does not parse the desk log, so an incomplete set is refused by the recompute (`compression_relocation_
   ambiguous`), not by the kit.
5. **A compressed row's `.zst` bytes are not digest-pinned**; its decompressed stream is checked against
   `SHA256SUMS`, and a recompressed `.zst` is refused through total bytes. A row present both plain and as `.zst` is
   refused as an unlisted extra file.
6. `block5` external digest is not emitted (no released Block 5 input is used; L9 is not planned).
7. `copy_path` is the shortest unique trailing suffix of at most three names: production `sessions/<id>/archive`
   gives `<id>/archive`; the `.desk` folder must sit beside it in the copy.

## Commands and exact tails

```
$ export TMPDIR=/Volumes/JW-EXT/tmp/b6-custody-kit JW_B5_SYNTHETIC_ONLY=1
$ python3.13 -B scripts/b6_synthetic_dry_run.py --out-dir $TMPDIR/probe1 --workers 1     # baseline probe
recompute sessions=10 flags=0 comparison_stopped=false restricted_sha256=8c17d392cdc1a588a573ba27949d2d2c2cd640e90ef810bbfd4d4e5080b71722
synthetic_dry_run exit=0 comparator=True                                                  # 16.7 s wall
$ python3.13 -B -m unittest tests.test_b6_custody_kit.Mini tests.test_b6_custody_kit.NoContentLeak
Ran 60 tests in 3.151s
OK
$ python3.13 -B -m unittest -v tests.test_b6_custody_kit.EndToEnd
test_kit_steps_exit_zero ... ok
test_public_output_identical_up_to_run_input_digest ... ok
test_recompute_on_kit_inputs_agrees ... ok
Ran 3 tests in 32.402s
OK
$ python3.13 -B -m unittest tests.test_b6_custody_kit
Ran 63 tests in 42.585s
OK
$ python3.13 -B -m unittest tests.test_b6_custody_kit     # after RL-100 (two tests added)
Ran 65 tests in 32.764s
OK
$ python3.13 -B -m unittest tests.test_shard_split      # the one timing line
Ran 36 tests in 2.027s
OK
$ python3.13 -B $TMPDIR/mutants/run_mutants.py           # 3 min 07 s
mutants 50 survived 0                                     # after RL-100
```

The end-to-end test runs `production_block` (ten archives, the first with two compressed rows and an inside log),
recomputes with the fixture's own sealed inputs, then runs manifest, a `copytree` copy, verify, a mapping built from
the fixture pins' names, inputs, and the recompute on the copy (`--workers 1`). Both runs exit 0 with
`option_c.pass` true and `comparison_stopped` false.

The leak test plants a marker in a plain meter stream, a compressed meter stream, `harvest.json` and
`derived/flags.jsonl`, runs all four commands and a refusal on the flipped marker file, and finds the marker in no
stdout, stderr or written file.

## Mutant kill table

The runner (in `$TMPDIR/mutants/`, not committed) replaces one `refuse(...)` call with `pass` per mutant and runs the
`Mini` and `NoContentLeak` classes. No mutant kills, signals or reaps a process. 50 mutants (49 refusal deletions plus the RL-100 mutant, which
makes every manifest-hashed file citable again), 50 killed. Line numbers are at the RL-100 head.

| Line | Refusal | Killed by |
|---|---|---|
| 56 | symlink (path component) | test_manifest_refuses_symlinked_session_root, test_symlinked_copy_root |
| 67 | not_regular_file (open) | test_manifest_refuses_fifo_loop_file |
| 83 | decompression_failed | test_corrupt_zst |
| 93 | symlink (in tree) | test_manifest_refuses_symlink_inside_source, test_symlink_in_copy |
| 97 | not_regular_file (in tree) | test_fifo_in_copy |
| 106, 109 | path_invalid | test_mapping_path_not_string; test_mapping_path_escapes, test_sums_path_escapes |
| 119 | out_exists (exclusive create) | test_write_refuses_out_created_after_check |
| 137 | copy_path_ambiguous | test_copy_path_ambiguous |
| 146, 149 | sums_line_invalid | test_sums_line_invalid; test_sums_duplicate_row |
| 160 | required_file_missing | test_manifest_refuses_missing_pinned_file |
| 164 | symlink (desk folder) | test_manifest_refuses_symlinked_desk |
| 169 | compression_log_ambiguous | test_manifest_refuses_two_compression_logs |
| 185, 267, 373 | out_exists (early) | test_manifest_refuses_existing_out_before_reading; test_verify_out_exists_before_any_read; test_inputs_out_exists_before_mapping_read |
| 188, 190 | session_missing, session_repeated (manifest) | test_manifest_refuses_missing_session; test_manifest_refuses_repeated_session |
| 209, 212 | zstd_unavailable | test_zstd_unavailable; test_zstd_version_fails |
| 219 | session_missing (copy) | test_session_missing_on_copy |
| 222, 229, 246 | listed_file_missing | test_missing_sha256sums; test_missing_derived_file; test_missing_listed_source_file |
| 224 | sums_digest_mismatch (verify) | test_edited_sha256sums |
| 231, 248, 260 | digest_mismatch | test_flipped_byte_in_derived_file; test_flipped_byte_in_listed_source_file (+ leak test, test_zst_whose_stream_differs); test_flipped_byte_in_desk_log |
| 250 | unlisted_extra_file | test_extra_file_in_sources, test_extra_file_in_derived |
| 252 | tree_size_mismatch | test_recompressed_zst_changes_bytes |
| 257 | desk_file_set_mismatch | test_desk_file_set |
| 270, 272 | manifest_digest_mismatch, manifest_schema_invalid | test_wrong_manifest_sha256; test_manifest_schema |
| 292, 294, 296 | receipt_not_verified, receipt_manifest_mismatch ×2 | test_receipt_not_verified; test_receipt_for_other_manifest; test_receipt_session_set_differs |
| 311 | sums_digest_mismatch (inputs) | test_sha256sums_changed_after_verify |
| 319 | mapping_path_unlisted | test_mapping_path_not_in_sha256sums |
| 323, 326, 328 | mapping_key_unknown, meter_streams_empty, contention_journal_missing | the same-named tests |
| 331, 333 | family_set_invalid, family_empty | test_missing_required_family; test_empty_required_family |
| 345, 354 | relocations_without_log, relocation_conflict | the same-named tests |
| 366, 371, 376 | session_unknown, inputs_arguments_missing, mapping_session_mismatch | test_list_names_unknown_session; test_inputs_arguments_missing; test_mapping_session_mismatch |
| RL-100 | citable names (all manifest-hashed files made citable) | test_mapping_path_hashed_but_not_emitted, test_list_names |

## Operator runbook (placeholders in angle brackets)

```
# CUSTODY: the manifest and run-input document hold digests of withheld/ files. They stay in the mode-700 custody directory and are never committed, mailed or pasted into RUN_STATE; only their own SHA-256 values travel.
# SOURCE (MBP desk gap, nothing armed): manifest, then note the printed sha256 OUT OF BAND (its digest only).
python3.13 -B scripts/b6_custody_kit.py manifest --session <sessions>/<id>/archive [...x each session] \
  --loop-attempts <loop>/attempts.jsonl --loop-state <loop>/state.json --out <desk>/b6-custody-manifest.json
# COPY: keep <copy_path> (printed in the manifest) and the sibling .desk folder; never --copy-links.
mkdir -m 700 /Volumes/JW-EXT/b6-custody && for id in <ids>; do rsync -aR <sessions>/./$id/archive <sessions>/./$id/archive.desk \
  <air>:/Volumes/JW-EXT/b6-custody/; done; rsync -a <loop>/attempts.jsonl <loop>/state.json <desk>/b6-custody-manifest.json <air>:/Volumes/JW-EXT/b6-custody/
# AIR: verify, write mapping.json from --list-names, emit inputs, run the recompute on the copy.
python3.13 -B scripts/b6_custody_kit.py verify --manifest /Volumes/JW-EXT/b6-custody/b6-custody-manifest.json --manifest-sha256 <sha from SOURCE> --root /Volumes/JW-EXT/b6-custody --out <run>/verify-receipt.json
python3.13 -B scripts/b6_custody_kit.py inputs --manifest <...> --verify-receipt <run>/verify-receipt.json --list-names <id>/archive
python3.13 -B scripts/b6_custody_kit.py inputs --manifest <...> --verify-receipt <...> --mapping <run>/mapping.json --l9-audit not_run --out <run>/run-inputs.json
python3.13 -B scripts/independent_recompute_b6.py block --session /Volumes/JW-EXT/b6-custody/<id>/archive [...] --closed --loop-attempts /Volumes/JW-EXT/b6-custody/attempts.jsonl --loop-state /Volumes/JW-EXT/b6-custody/state.json --inputs <run>/run-inputs.json --inputs-sha256 <printed> --workers <n> --restricted-out <...> --public-out <...>
```

## What the operator supplies by hand

- The manifest SHA-256, carried from the source to the Air by a channel other than the copy itself.
- `mapping.json`: `{"sessions": {"<copy_path>": {"meter_streams": [...], "contention_journal": "...",
  "clock_journal": "...", "copied_records": {<eight families>: [...]}, "relocations": {...}}}}`. Names come from
  `--list-names`. R12's `archive_pin` is a worked template for the families. The kit checks names and coverage only;
  the lead's hand check that each copied-record file holds its disclosure (status table §17-R3) stays owed.
- `relocations` for every absolute prefix in the desk log other than the archive itself (custody root and run roots,
  from each session's `session.json`).
- `--l9-audit` (`not_run` unless the audit completed) and the session list; disk for the copy (§17-R11's 32.75-38.82
  GiB per session is the decompressed size; the copy stays compressed).

## STOP findings

None. The schema at `b4e4df8ed` expresses everything the kit needs; the synthetic generator produced every case
(the adjacent `.desk` log and repeated basename `archive` were built in the kit's own mini fixtures because
`production_block` uses an inside log and unique names); no step needed a real path. Note for the lead: `verify`
reads every byte of every archive (decompressing `.zst` rows), so on real sessions it costs roughly one full
decompressed read per session.

## Read and not read

Read: `/Volumes/JW-EXT/scratch/b6-release-path.md` §0-§1 and BRIEF-B; `docs/run_reports/2026-11-11-p1-seat7.md`
(production input contract and its example command); `joulewise/b6_analysis_inputs.py`;
`scripts/b6_synthetic_dry_run.py`; `tests/independent_recompute/support_b6_production.py`; the head of
`tests/independent_recompute/test_b6_production.py` and of `support_b6.py`; §17-R11 of
`docs/registrations/block6_s17_entries_DRAFT_2026-11-10.md` (and, scanning to it, its decision table row 9 and
§17-DLE2); in `scripts/independent_recompute_b6.py`, `session_input_pin`, the meter/copied-record input use,
`write_outputs`, `finish_recompute` and `main`; `scripts/b6_r12_verify.py` lines 1-130 (pin construction); grep hits
in `tests/test_b6_r12_session_fixture.py`; `scripts/test_timings.json` structure. Synthetic archives under
`$TMPDIR` only.

Not read: anything under `/Users/edr/night-*`, `/Volumes/JW-EXT/air-home/night-*` or any custody, archive,
restricted or real-session path; `docs/analysis/b5/RESULTS.md`, `REDERIVATION.md`, `rederivation.tsv`,
`hand_checks_phase2.tsv`, `RUN_STATE.md`, `docs/paper/paper1/`, RL-38 to RL-42; §2-§5 of the release-path file.
Nothing was written to or run in `/Volumes/JW-EXT/jw-wt/sol-p1-b6-r12c` (one read-only `git fetch` from it). The
nine-session R12 fixtures were not run. No SSH.
