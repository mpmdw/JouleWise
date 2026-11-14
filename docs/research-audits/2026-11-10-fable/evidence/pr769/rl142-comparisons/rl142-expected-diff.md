# RL-142 §2 item 5: expected difference for comparisons (a) and (b), written BEFORE the r2 gate and dry runs

Revised per fable-rl142-j-rulings.md (C1-C3), 2026-11-13 15:22 PST.

Written 2026-11-13 ~15:10 PST (`date` 15:06), before any r2 run. Builder seat (Claude Opus 5.5) for the lead.
**Blind.** It is designed from code only. Code read: RC-B6-1 at `aaa2f3086` (`/Volumes/JW-EXT/jw-wt/b6-s14-r2`),
lines 986-1137, 1290-1482 and 1558-1800; `joulewise/b6_analysis_check.py` (`check_block`); and the tools at
`f19f36081` (`/Volumes/JW-EXT/jw-wt/b6-real-run/scripts/`): `b6_real_run.py` (all of it), `b6_structure_probe.py`
(`extract`, checks, `probe`) and `b6_release_record.py` (header). Under `/Volumes/JW-EXT/b6-custody-run` I listed file
names only. I opened, hashed and parsed no run output. The tests use synthetic directories only.

- Old program, RC-B6-1 `90e22603…5fb85759` (`b6/analysis`, `3551e1a7d`). Old dirs: `$RUN/gate-2` for (a), `$RUN/dry` for (b).
- New program, RC-B6-1 `4a9f5944…5211ea` (`b6/analysis-r2`). New dirs: `$RUN/gate-r2` and `$RUN/dry-r2`, as in
  `rl142-r2-records.md` §F.
- Comparer: `/Volumes/JW-EXT/scratch/compare_rl142.py`. It prints its SHA-256 and writes it into `result.json`.
  Usage: `compare_rl142.py --mode a|b --old DIR --new DIR --out result.json [--inputs-rerun]`.
  Exit 0: no UNOWNED path. Exit 3: HOLD. Exit 2: usage or parse error.

Path notation: JSON-pointer style, with `/` inside a key written `~1`. For example the key
`lines/whole_machine/qwen3-1p7b/decode/mean_j` is `lines~1whole_machine~1qwen3-1p7b~1decode~1mean_j`. Lists are
compared by index, except `flags` (J12).

## 1. The ten files

| File | Writer (code) | Class | How compared |
|---|---|---|---|
| `restricted.json` | RC-B6-1 `finish_recompute` + `write_outputs` | **A** | JSON, key path by key path |
| `public.json` | RC-B6-1 `finish_recompute` + `write_outputs` | **A** | JSON, key path by key path |
| `structure.json` | `b6_structure_probe.py --out` (derived from restricted + public; names, counts, digests) | **A** (derived analysis record) | JSON, key path by key path |
| `record.json` | `b6_real_run.py launch()` | **C**: mixed. It holds the program-hash fields (`commit`, `closure_*`), the output digests, the verdict fields (`exit_code`, `status`, `code`) and the process fields | JSON, key path by key path. Its process fields are allowed as B fields (R-B-*), not as owned by the spec |
| `child-argv.json` | `b6_real_run.py launch()` (`{schema, checkout, argv}`) | **C**: the program's arguments ("same arguments", RL-142 §2 item 5) | JSON, by index. An element may differ only by the out-dir or checkout spelling (R-B-4) |
| `stdout` | RC-B6-1 `main` (one line: `sessions`, `flags`, `comparison_stopped`, `restricted_sha256`) | **C**: analysis summary line | parsed into the four named tokens and compared token by token. An unparsable line that differs is UNOWNED (J9) |
| `process.json` | `b6_real_run.py exec_child` (exit, rusage) | **B** | SHA-256 only |
| `samples.jsonl` | `b6_real_run.py Sampler` | **B** | SHA-256 only |
| `stderr` | the program's stderr | **B** | SHA-256 only (its digest in `record.json` is bound, R-B-2) |
| `time` | `/usr/bin/time -l` report | **B** (RL-132 §1) | SHA-256 only |

The B files are expected to differ in both comparisons. They are reported `B-FILE` and never hold. A file of
the ten that is missing on either side, or any file outside the ten, is UNOWNED.

## 2. Allowed differences, comparison (a): gate r2 against gate attempt 2

RL-142: "no difference except the program hash". The gate run passes no `--block5`, so `pack_block5_keys` returns
`{}` under both programs (ruling §2 item 5). Everything below follows from the hash, or is a process record.

| Rule | File: path | Implements | Check made (no value printed) |
|---|---|---|---|
| R-PH-1 | restricted `/program_sha256`; structure `/digests/program_sha256`; record `/closure_before/scripts~1independent_recompute_b6.py`, `/closure_after/…` | "the program hash" | old = `90e22603…`, new = `4a9f5944…`, else UNOWNED |
| R-PH-2 | record `/commit` | "the program hash" (**J1**) | none |
| R-DG-1 | public `/restricted_sha256`; stdout token `restricted_sha256`; record `/outputs_sha256/{restricted,public,stdout}`; structure `/digests/{restricted_file,public_file,public_restricted_sha256}` | digests of a compared file that holds the hash (**J2**) | new value = SHA-256 of the new file, else UNOWNED |
| R-B-1 | record `/stem`, `/start_time_ns`, `/end_time_ns`, `/wall_s`, `/peak_rss`, `/time_wrapper_exit` | process record (RL-132 §1). B, not owned by RL-142 | none |
| R-B-2 | record `/outputs_sha256/stderr` | process record. B | = SHA-256 of the new `stderr` |
| R-B-3 | record `/argv_sha256` | process record. B | = SHA-256 of the new record's `argv` |
| R-B-4 | record `/argv/<i>`, `/timed_argv/<i>`, `/record_path`, `/checkout`; child-argv `/argv/<i>`, `/checkout` | process record: out-dir (and checkout, **J11**) spelling. B | new string = old with the out-dir and checkout substituted, else UNOWNED |
| R-IN-1 | restricted `/inputs/run_inputs_sha256`; structure `/digests/{run_inputs_sha256,inputs_file}`; argv value after `--inputs` or `--inputs-sha256` | only with `--inputs-rerun` (**J3**) | none |
| B-FILE | the four B files | process records | SHA-256, equal or differing |

Predicted equal in (a), and UNOWNED if they move: every other path of restricted, public and structure. In
record: `exit_code`, `status`, `class`, `code`, `frames`, `limit_s`, `python`, `peak_rss_units`,
`closure_unchanged` and the 23 other closure rows. The stdout `sessions`, `flags` and `comparison_stopped` tokens.

## 3. Allowed differences, comparison (b): dry run r2 against the held dry run

Every rule of §2 applies, plus the following, one per phrase of RL-142 §2 item 5. Here K is one of the four keys
`lines/whole_machine/{qwen3-1p7b,qwen3-8b}/{decode,prefill-p2048}/mean_j`, and P is its own pack (qwen3-1p7b is
ALPHA and qwen3-8b is BETA, from `MODEL_TAG`). A K under the other pack, or under GAMMA, is not allowed.

| Rule | File: path | RL-142 phrase |
|---|---|---|
| R-B1-SUM | restricted `/block/between_session/P/values/K/{n,mean,sd,block5_included}` | "the fields of item 1 for the four keys": summary n, mean, sd, `block5_included` |
| R-B1-INC | restricted `/block/flagged_inclusive/P/values/K/{n,mean,sd,block5_included}` | item 1: flagged-inclusive n, mean, sd, `block5_included` |
| R-B1-SBS | restricted `/block/side_by_side/P/K/{block5,block5_label,delta,session_deltas[/<sid>]}` | item 1: side-by-side Block 5 value, label, delta, session deltas |
| R-BQ | restricted `/comparison_table/block/quantities/{summary,inclusive}~1P~1K~1{n,mean,sd}` and `…/side_by_side~1P~1K~1delta` | "their block quantities" |
| R-CT-1 | restricted `/block/option_c/comparator/classes/side_by_side/{passed,failed}`; structure `/option_c/comparator/classes/side_by_side/{passed,failed}` (C3: only the `side_by_side` class, only these two tallies) | "comparator tallies" (the `side_by_side` class of their block quantities, `quantity_class`) |
| R-CT-2 | restricted `/block/option_c/comparator/pass` and `…/classes/side_by_side/pass`; structure the same, and `/checks/compared_classes_clean/{result,names_of_classes[/i]}` | verdicts formed from those tallies (**J4**, C3) |
| R-CT-3 | structure `/term7/per_class/side_by_side/passed` (C2) | new − old equals new − old of structure `/option_c/comparator/classes/side_by_side/passed`, both integers, else UNOWNED |
| R-FL | restricted `/block/option_c/failures[/i]`; structure `/names/failures[/i]`, `/option_c/failure_count`, `/checks/failures_empty/{result,count}` | "`failures`" |
| R-OCP | restricted `/block/option_c/pass`; structure `/option_c/pass`, `/checks/option_c_pass/{result,observed}` | "`option_c.pass`" |
| R-CS | restricted `/comparison_stopped`; public `/comparison_stopped`; stdout `comparison_stopped`; structure `/identity/comparison_stopped`, `/public/comparison_stopped`, `/checks/comparison_stopped/{result,observed}` | "`comparison_stopped`" |
| R-CS-X | record `/exit_code` (3 to 0), `/status` (hold to complete), `/code` (`comparison_stopped` to null) | the launcher's record of `comparison_stopped` (**J5**) |
| R-OCD | restricted `/flags/option_c_disagrees[/…]`; structure `/flags/option_c_disagrees[/…]` | "the `option_c_disagrees` flags" |
| R-OCD-N | public `/flag_count`, `/sessions/<sid>/restricted_flag_count`; stdout `flags` | counts of those flags (**J6**). Checked: each change equals the change in the number of `option_c_disagrees` rows (total or per session), else UNOWNED |
| R-B5N | structure `/block5_included/{ALPHA,BETA}`, `/checks/block5_included/{observed,expected,by_pack/{ALPHA,BETA},expected_by_pack/{ALPHA,BETA}}` | the probe's tally of item 1's `block5_included`, and item 4's predeclared count 44 to 48 (**J7**) |

Predicted equal in (b), and UNOWNED if they move. Everything else, in particular:

- `block6_only`, `noncomputable_sessions`, `sd_label` (**J8**), `n_counting`, `short` and `replication`;
- every session quantity, `families` and `first_program_only`;
- the comparator's `recompute_stopped`, `release`, `release_inputs_valid` and `print_spec_ratified`;
- every flag group other than `option_c_disagrees`;
- public `flag_counts`;
- structure `accounting` and `term7`, except `/term7/per_class/side_by_side/passed` (R-CT-3, C2). The summary and
  inclusive class tallies, and `compared`, `unmatched`, `both_null` and `first_program_only` in every class, are
  predicted equal (C3);
- record `class`, `frames`, `limit_s` and `python`.

GAMMA's `block5_included` is predicted unchanged (4).

## 4. JUDGMENT items for the research lead

- **J1.** record `/commit` is the launcher's `--expect-commit`. I classed it under "the program hash", because r2's
  commit is the hash change. `child-argv.json` does not carry it. No record field carries the `--block5-expected`
  file's SHA-256. Only structure `/checks/block5_included/expected` carries its count (J7).
- **J2.** Digests of a compared file that contains the program hash are allowed as consequences of the hash, as in
  the RL-129 precedent §A item 2. Each one is checked to bind the new file's bytes, so a digest cannot hide a
  difference that the file comparison does not also see.
- **J3.** If `run-inputs-*.json` is re-made (rl142-r2-records.md E4), its digest and path change in restricted
  `inputs`, structure `digests` and argv. I put this under "program hash" only when the lead passes
  `--inputs-rerun`. Without that flag these paths HOLD. E4 predicts reuse, so the flag is not expected to be needed.
- **J4.** (Ruled with change C3.) RL-142 lists "comparator tallies". The comparator `pass`, the `side_by_side`
  class `pass` and the probe's `compared_classes_clean` row are verdicts of the tallies and are allowed
  (`compare()`: pass ⇔ failed = 0 and unmatched = 0). Summary and inclusive tallies are not allowed: by the code only
  the `side_by_side` class changes, and only in `passed`, `failed` and `pass`.
- **J5.** record `exit_code`, `status` and `code` are the launcher's record of `comparison_stopped`
  (`main` returns 3 only when it is true). This widens the list. In (a) all three must be equal.
- **J6.** public `flag_count`, the per-session `restricted_flag_count` and the stdout `flags` token count the
  `option_c_disagrees` rows, which are not a public code. I allow them only when the change equals the change in
  those rows. This widens the list.
- **J7.** structure `block5_included` per pack and the `block5_included` check row are a count of item 1's
  `block5_included` field. Its `expected` comes from the item 4 predeclaration (44 to 48, read from `b5-probe-r2.json`).
- **J8.** `sd_label` (`"not defined"` iff n = 1) is a function of the summary n but is not in item 1's text. I left it
  **not allowed**. It can move only if a K's counting-session n is 0. If it fires, that is a HOLD to the research lead.
- **J9.** The brief listed stdout among the B records. I compare it token by token instead, which is stricter.
  `restricted_sha256` is R-DG-1, `comparison_stopped` is R-CS (b only), `flags` is R-OCD-N (b only), and
  `sessions` must be equal. This follows `compare_rl133b.py`.
- **J10.** record `python`, `limit_s` and `peak_rss_units` are process fields, but I predict them **equal** ("same
  arguments", same interpreter). A change HOLDs.
- **J11.** A changed run-checkout path is allowed as a B substitution, as in the RL-129 precedent §B "reader
  checkout". rl142-r2-records.md §F keeps the same path `$W`, so this is not expected to fire.
- **J12.** `flags` is a list sorted by (code, session, pack, scope, detail) in `finish_recompute`. It is keyed by
  code. The comparer groups it by code and compares by index within a group, so removing the `option_c_disagrees`
  rows does not shift every later flag. In printed paths a restricted flag code appears as
  `<restricted-code-n>`. Only public codes and `option_c_disagrees` are shown by name.
- **J13.** `structure.json` is classed A. The old file is the probe at `5c53850f6`, and the new one is the probe at
  `f19f36081`. Those differ only in `EXPECT_PROGRAM_SHA256`, so the check rows are predicted equal
  (`program_sha256` is "ok" on both sides). The dry-r2 probe is invoked with the same options as the probe that wrote
  the held `dry/structure.json`, `--term7` included, with `--block5-expected $RUN/b5-probe-r2.json`. A `/term7` key
  on one side only is UNOWNED.

## Rule

Any path that differs and has no rule above for that mode holds the release, and the comparison comes to the
research lead (RL-142 §2 item 5; RL-123 §2 item 4). The same applies to any failed binding check above. The
allowance is not widened after observation. The comparer prints and writes only key paths, file names, kinds,
rule ids, counts and the verdict. No value from a compared file leaves it.
