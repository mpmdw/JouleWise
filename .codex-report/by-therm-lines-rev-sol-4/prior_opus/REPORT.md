claude-opus-5-5
VERDICT: ACCEPT_WITH_FIXES

# BY-THERM-LINES delta review (fix rounds 2 and 3), executing

Reviewed mpmdw/JouleWise `e23cd1e7b..574f13d2f` (PR #598 head, confirmed with `git ls-remote`: `refs/pull/598/head = 574f13d2f76c…`). Authority: registration §21 item 3 and §7, rulings T1–T7, U1–U4 and V1–V6. Python 3.13.17, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONDONTWRITEBYTECODE=1`, synthetic data only. I did not edit any production file. Line numbers refer to `scripts/bytes_thermal_lines.py` at `574f13d2f`.

Scripts and logs are in this directory: `probes_v.py` and `probes_v.log` (my probes); `adapted/` holds three earlier-review scripts, each adapted only for U1 or U2 as noted in the file, and `census_sealed.log`.

## Findings

1. **MAJOR: `request-end-p1` prints `equals registered line` (and `equals_registered_line: true`) for a member whose outcome depends on a journal that differs from the harvest's seal, or whose seal is absent.** Lines `243–250`. When the journal is mismatched or its provenance is unavailable, a member becomes `not defined` only if the unverified journal *changes* its code. Take a member that carries `thermal.os_level_nonzero`, where the unverified journal also shows the code. Its status is "equals registered line", but it was never determined. The sealed journal could remove the code; request-end can only remove. The journal-absent branch (`209–211`) already applies the right rule: every member that carries the code is not defined. The mismatch and provenance-unavailable branches do not. In the repro below, the harvest's sealed journal restores `a` (`evaluated`). The archived journal differs from that seal and keeps `a`. The tool then prints the whole line as equal to the registered line, with `a` still dropped. The only signal is the `records.thermal_journal_mismatch` notice. The same happens with `derived/window_flags.json` absent.
   Repro: `JW=/tmp/jw python3.13 by-therm-lines-delta-opus-2/probes_v.py` (seat env sourced). Output tail:
   ```
   PROBE V1 req mismatch sealed-journal-truth ((0, '}'), {'members': {'a': 'evaluated', 'b': 'equals registered line', ...}, 'eq': False, 'status': 'evaluated', 'dropped': [], ...})
   PROBE V1 req mismatch differing-journal-keeps-a ((0, '}'), {'members': {'a': 'equals registered line', 'b': 'equals registered line', ...}, 'eq': True, 'status': 'equals registered line', 'dropped': ['a'], 'notices': ['records.thermal_journal_mismatch', 'reference.unchanged']})
   PROBE V1 req provenance-absent differing-journal-keeps-a ((0, '}'), {... 'a': 'equals registered line' ..., 'eq': True, 'status': 'equals registered line', 'dropped': ['a'], 'notices': ['records.thermal_journal_provenance_unavailable', 'reference.unchanged']})
   ```
   This changes which members count: `a` is excluded while the line claims registered equality. U2 says "each member it would restore gets not defined", and its literal wording could be read to cover this, so the lead should decide whether U2 knowingly supersedes the finding. If it does not, the fix is determined by V1 and the existing journal-unavailable rule. Under a mismatch or an unavailable seal, every science member carrying the code gets `not defined (<reason>)` and keeps its codes. Members without the code keep V2's handling. No existing test covers the case where the unverified journal keeps the code (`tests/test_bytes_thermal_lines.py:892–1006` cover only would-remove and would-add).

2. **MINOR: five non-ruled faults still stop with no record.** Each one exits 1 with a traceback, or 2. They are: acceptance `excluding: null` (`153`, TypeError); an exclusion row without `code` (`155`, KeyError); a roster member without `run_id` (`152`, KeyError); a non-UTF-8 export CSV (`136` via `281`, where `UnicodeDecodeError` escapes the `except OSError`); and `--export` with no `session_id` in the acceptance (`259`). None of them writes an output, so none can miscount members. They are still outside V2's "only two stops".
   ```
   PROBE V1 hull acceptance-excluding-null ((1, "TypeError: 'NoneType' object is not iterable"), 'NO RECORD')
   PROBE STOP non-utf8-csv ((2, "'utf-8' codec can't decode byte 0xff in position 35: invalid start byte"), 'NO RECORD')
   PROBE STOP acceptance-missing-session_id ((2, 'missing structural field: session_id'), 'NO RECORD')
   PROBE STOP exclusion-row-missing-code ((1, "KeyError: 'code'"), 'NO RECORD')
   PROBE STOP roster-member-missing-run_id ((1, "KeyError: 'run_id'"), 'NO RECORD')
   ```

3. **MINOR: `verify` crashes (exit 1) on a `thermal_line.json` that parses but is structurally damaged, and when called through a symlinked output path.** The record check at `487–488` only tests for a dict with a `notices` list. Three damaged records still crash verify: non-dict notices, a notice without `code` (`516–517`), and `source_sha256` that is not an object (`507`). In each case the on-disk flag stays `False`. A symlinked output path is rejected by `guard_destination` inside verify's own write (`524` → `416`).
   ```
   PROBE VERIFY record-notices-not-dicts ((1, "TypeError: 'int' object is not subscriptable"), 'flag=False')
   PROBE VERIFY record-notice-without-code ((1, "KeyError: 'code'"), 'flag=False')
   PROBE VERIFY record-source_sha256-list ((1, "AttributeError: 'list' object has no attribute 'items'"), 'flag=False')
   PROBE VERIFY via-symlinked-output-path (1, 'ValueError: destination directory is a symlink: …/vl/link')
   ```

4. **MINOR: a missing pass identity is treated as a match.** Lines `144–151`: when there is no `sources/repo/plan_tree.json`, or the plan tree has no `bytes_pass` (`except ValueError: continue`), the tool raises no pass mismatch, and `hull-p2` adds codes as `evaluated`. The harvest's own rule (`harvest.py:3998–3999`) treats a missing `bytes_pass` as not pass two. On that reading, such an archive was harvested with the pass-1 window, so V1 would call it a pass mismatch. This only affects a damaged archive.
   ```
   PROBE V1 hull no-plan_tree ((0, '}'), {'members': {'a': 'equals registered line', 'b': 'evaluated', ...}, 'eq': False, 'status': 'evaluated', ...})
   PROBE V1 hull plan_tree-without-bytes_pass ((0, '}'), {... 'b': 'evaluated' ...})
   ```

5. **NIT: wrong reason on a changed member when the CSV is invalid.** With an empty or column-less CSV, the changed member's reason is overwritten by "changed member absent from export" instead of the CSV fault (`311–315` run after `295–298`). Representation only; the status is still `not defined`.

6. **NIT: `verify` on a path that does not exist creates the directory** and writes a flagged `thermal_line.json` into it (`524` → `425` `mkdir(parents=True)`). It exits 0 with the flag set.

7. **NIT: nothing binds `thermal_line.json` itself.** Editing `equals_registered_line` or `member_statuses` still gives `view verified`. This is inherent in T4's design, where the record is the root that binds the manifest. I note it and ask for no new process.

## Item results

1. **Earlier reviews, re-run at `574f13d2f`.**
   - **Sol delta findings 1–4:** all closed, checked with `adapted/delta_probes_u1.py`. That script adapts Sol's `delta_probes.py` for U1 only: the two steps that reused an existing output now expect the refusal. Results: `MISSING_SEAL not defined (journal provenance unavailable) changes 0`; `REUSE refused: output must be a new directory`; `DAMAGED_MANIFEST exit 0 … FLAG True`; `LINKED refused …`, `SOURCE_EXPORT_CHANGED False`. The unadapted script stops at the U1 refusal, which U1 knowingly supersedes.
   - **Sol's other scripts:**
     - `sol_probes.py`: fails its assertion that unsealed restorations happen, which U2 supersedes. With journals sealed (`adapted/sol_probes_sealed.py`) it prints `PROBES_PASS`.
     - `view_and_gap.py`: OK when run from the repository root (`REAL_GAPS_OS_PROJECTION_EXACT…`, `ADDED_DELETED exit 0 … flag True`).
     - `sol_campaign.py`, `campaign_delta.py` and `sol_chain.py`: complete with exit 0.
     - `opus_chain_analysis.py`: 27/30. The three failures are p1 "archive-stage transform changes exactly the target" on unsealed injected journals, superseded by U2. The module's sealed port of the same script passes 30/30 in the unit run.
     - `opus_chain_test.py`: 22/24. The two failures are "pass mismatch refused" and "linked view read-only", superseded by T2/V1 and T4 respectively.
   - **Opus delta findings 1–6** (`probes_delta.py`, run unmodified; the identity adaptation the builder claims is correct). Every probe line matches the builder's "After" block, apart from the dict ordering of `modes-of-copies`.
     - Opus 1: closed by V1, except finding 1 above.
     - Opus 2: closed for the named cases; the remainder is finding 2 above.
     - Opus 3: closed for missing or unparsable records; the remainder is finding 3 above.
     - Opus 4, 5 and 6: closed.
     - Opus 7 is out of scope.
   - **`census_t1.py`:** unmodified, it fails four p1 checks because the injected journals have no seal, which U2 supersedes. With the seal added (`adapted/census_t1_sealed.py`) it gives `SUMMARY fails []`.
2. **V1 direction.**
   - **`hull-p2`:** the assessment file absent or not JSON, a missing per-member field, `excluded: null`, a non-bool `excluded`, and `journal_available: false` all behave correctly. A member carrying the code is determined; a member without it is `not defined (hull assessment unavailable)`. `equals_registered_line` is true only when every member is determined (`absent-all-carry-code` gives `eq: True`).
   - **Pass mismatch:** every science member is `not defined (pass mismatch)` in both directions.
   - **`request-end-p1`:** an absent journal or spans file is correct, and so is the would-remove case under a mismatched or absent seal. The one failure is finding 1. A missing pass identity is finding 4.
3. **Stops.**
   - **Ruled stops:** source overlap (archive or export, either direction, and a parent symlink into the source) exits 2. A request-end would-add on a journal matching its seal exits 2 and creates no output. A mismatched would-add exits 0 with `not defined (journal differs from the harvest's)`.
   - **Faults that record and exit 0:** an empty CSV, a column-less CSV, a ragged row, and an absent withheld store. A run outside a git work tree (scripts and package copied to a non-git directory) writes `producing_commit: null` and `producing_tree_dirty: null`, exit 0.
   - **Remaining stops:** finding 2.
4. **`verify`.** All of these exit 0 with `flag=True`: a deleted or unparsable record, a record that is a list, a record missing its manifest binding, a damaged manifest (not JSON, deleted, entries that are ints or floats), added and deleted view files, and moved sources (acceptance, export, deleted linked source). Moved sources print `source changed since transform: <path>`. The crashes are finding 3.
5. **U1.**
   - **Refused before any write, sources byte-identical afterwards (`U1 sources-unchanged True`):** an existing directory, a dangling symlink, a symlink to an existing directory, an output inside the archive or export, an output whose parent symlinks into the source, and an archive inside the output.
   - **Two fresh outputs from the same inputs:** the manifest, the change list, the full `thermal_line.json` and the export CSV are each byte-identical.
6. **Census and blinding.**
   - **Census (sealed census):** public + withheld rows equal the source's on s2 (63+50) and s5 (13+50), both passes and both stages. The record census is source==output (s2: 50/100, s5: 0/50 before and after commit).
   - **Withheld copy:** it equals `csv.DictWriter(stream, fieldnames=columns)` output (the exporter's call, `export_runs.py:735,744`) for the post-change rows, byte for byte. That includes CRLF, a quoted multiline sentinel field, and a retained secondary code keeping `excluded=True` (`DW … True` ×3).
   - **Sentinels:** in `probes_delta.py`'s guarded run, energy, power, duration and rail sentinels are never decoded and never appear in stdout or the record (`[]`, `[]`). Payload bytes are hashed for the T4 manifest, as T4 rules, and never parsed.
7. **Numbers.**
   - **No float tolerance anywhere.** A grep for `isclose|1e-|abs(|tolerance|round(|assertAlmost` finds none in the script or tests. Comparisons are set or string equality on codes, `type(...) is int` on ns stamps, integer `==` on sizes and inode/mtime, and string equality on SHA-256. No agreement bar exists or is needed.
   - **Pinned files unchanged:** `joulewise/bytes_analysis.py` `18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71` and `joulewise/b5/harvest.py` `2aec65877b3a7e6da096171eb305833750932e2b5e0674eb835f408a0ad6c744` match. `git diff e23cd1e7b 574f13d2f -- joulewise/` is empty.
8. **CI: not read.** This session's GitHub access is scoped to mpmdw/JouleWise-data only, so PR #598's check runs on mpmdw/JouleWise were not readable here. I attribute no job and claim no state. The head is `574f13d2f`, and the delta touches only the script, its test module and the report. The lead should read the PR's checks.

## Executed

- `bash tools/cloud/seat_setup.sh /tmp/jw`. Detached `/tmp/jw` and worktree `/tmp/jwh` at `574f13d2f`. Read `.codex-report/BY-THERM-LINES.md` in full, the full script, the round-3 tests, both earlier delta reports, and the relevant exporter and harvest lines.
- `python3.13 -m unittest tests.test_bytes_thermal_lines -v` at `574f13d2f`: `Ran 33 tests in 1123.250s`, `OK (skipped=1)`. The skip is the compressed-journal test, because zstd is not installed here (it is optional in the harvest tests too). Log: `unit.log`. I did not re-run `tests.b6.test_bytes_p2_thermal_window` or `tests.test_harvest_b5_window`, since the delta does not touch them and the budget was spent.
- Opus `probes_delta.py` and `census_t1.py` (plus the sealed adaptation); Sol's nine scripts (two adapted, as described above); `probes_v.py` (65 probe lines, in `probes_v.log`).
- `git ls-remote` for the PR head; SHA-256 of the two pinned files.

## Decisions I made

- I rated finding 1 MAJOR because it changes which members count and prints a false `equals_registered_line`. The verdict is ACCEPT_WITH_FIXES rather than REJECT because the fix is local, and V1 plus the existing journal-unavailable branch already determine it. I flagged U2's literal wording so the lead can say whether it supersedes the finding.
- I treated the earlier scripts' failures on unsealed journals as superseded by U2, and confirmed this by re-running sealed adaptations rather than reading the failures as defects.
- I rated the remaining stops and verify crashes MINOR: neither can produce an output that miscounts.
- I did not read PR CI, because of the session's repository scope, rather than use a route outside it.
- I pushed the report to the session's designated branch `claude/by-therm-lines-delta-opus-2-bj9jkr` and also to `claude/by-therm-lines-delta-opus-2`, the branch the brief names.
