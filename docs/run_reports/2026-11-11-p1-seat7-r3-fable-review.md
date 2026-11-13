# Paper 1 seat 7, round 3: Fable cold review of R2-F1 to R2-F3

Date: 2026-11-11 02:44 PST. Reviewer: Fable 5.2 (cold).
Target: `analysis/2026-11-11-b6-path` @ `6fd6c455fab9bec0113b188a75f6ccdbed2b45d8`
(fix `9fdec5aed`). Diff reviewed: `git diff 920fc77c3..HEAD`.

**Verdict: ADMIT.** R2-F1, R2-F2 and R2-F3 are closed, each with a witness that fails on the wrong code.
I applied N8, N12 and a guard deletion myself and all die. The five modules pass under the native macOS
temp directory, which the author could not test. No fix is required. The lead's F1/R12 ruling is
untouched by this round and still gates the S-14 pin.

## Read and not read

Read: the round-2 Opus review, the round-3 author report, the full round-3 diff, all of
`joulewise/b6_analysis_inputs.py` up to `read`, and in `scripts/independent_recompute_b6.py` only the
option-(c) assembly in `recompute_block` and the printed-line assembly after `B5.add_machine`. In the test
module I read the 7b test and the new cases.

Not opened: `docs/analysis/b5/RESULTS.md`, `REDERIVATION.md`, `rederivation.tsv`,
`hand_checks_phase2.tsv`, any seat-4 report, RL-38 to RL-42, `RUN_STATE.md`, anything under
`docs/paper/paper1/`, and any custody, night-*, archive, restricted or real-session path. No real Block 5
or Block 6 data was opened. Every run built marked synthetic fixtures; the only numbers I saw are
synthetic fixture values in assertion messages. The pinned B5 script was hashed, never opened or edited.

## Checks

Environment: MacBook Air, Python 3.13.18, `JW_B5_SYNTHETIC_ONLY=1`, modules run one at a time.
`TMPDIR=/var/folders/b6/.../T/`, equal to `getconf DARWIN_USER_TEMP_DIR`. Note that `env -u TMPDIR` does
not give `/var/folders` here: Python then falls back to `/tmp`. I used the native value, which is what
the check intends; the author already covered `/tmp`.

| # | Check | Result |
|---|---|---|
| 1 | `tests.independent_recompute.test_b6_production`, native temp dir | 16 tests, OK (50.3 s, machine loaded) |
| 1b | `tests.independent_recompute.test_block6` | 26 tests, OK |
| 1c | `tests.flags.test_flags_exclusions` | 34 tests, OK |
| 1d | `tests.twins.test_harvest_twin` | 16 tests, OK |
| 1e | `tests.twins.test_engine_twin` | 12 tests, OK |
| 2 | `shasum -a 256 scripts/independent_recompute_b5.py` | `d49103e884ccae47242b8efb91ea1f5764e4505a4ad5e54558cc42a399a2e4e0`. No diff against `origin/main` or `920fc77c3`; still the pin after my mutant runs. |
| 3 | `b6_synthetic_dry_run.py --workers 1` and `--workers 2` | Both exit 0, `comparator=True`, 0 flags, `comparison_stopped=false`. `synthetic-numbers.json` (`7eae099a...bf590`, as in the report), `public.json`, the archives tree, stdout and stderr are byte-identical. `receipt.json` differs in its `seconds` field only. |
| 4 | R2-F1 witness | Perturbs one `anchor_envelope().max_abs_delta_j` by 0.01 J. Asserts comparator pass, exactly one `harvest_bound` failure, option (c) fail, `option_c_disagrees`, `comparison_stopped` and exit 3. So it holds on the checker arm alone. |
| 5 | R2-F2 witness | The p42 `continue` is gone. Printed-line equality, the four corners and the boundary sentence now cover p42; only the quantities-key assertion is skipped for it. |
| 6 | R2-F3 guard | `".." in Path(archive).absolute().parts` refuses before the symlink check and before `resolve()`. See the probe below. |
| 7 | Tree hygiene | Clean after every mutant and after the dry runs. |

## Mutants (applied by me, exact single-occurrence replacement, full `test_b6_production` each)

| Mutant | Result | Killed by |
|---|---|---|
| N8: `checks["pass"] = comparator["pass"]` | KILLED | new checker-only test, `True is not false` |
| N8b (mine): the flag loop tests `comparator["pass"]` instead of `checks["pass"]` | KILLED | new checker-only test, `'option_c_disagrees' not found in set()` |
| N12: printed p42 whole-machine `mean_j` x1.001 | KILLED | 7b equality, subtest `df-ph-prefill-p42-qwen3-1p7b` |
| G: the two R2-F3 guard lines deleted | KILLED | harvest-pin/escape test, `InputRefusal not raised` |

Each kill is exactly one assertion failure, with no import or collection error.

## R2-F3 bypass probe (synthetic directories only)

| Supplied path | Outcome |
|---|---|
| `link/derived/..` as `Path` and as `str`, with trailing `/` or `/.` | `input_path_invalid` |
| `arch/derived/..` (no symlink) | `input_path_invalid` |
| `sub/../link` | `input_path_invalid` |
| relative `..` | `input_path_invalid` |
| `link/.`, `link/`, `link//` | `input_symlink` (pathlib drops `.` and trailing slashes, so the last component is the link) |
| a link whose own target contains `..` | `input_symlink` |
| `os.path.normpath("link/derived/..")` | `input_symlink` |
| relative `.` with the shell inside `link` | accepted as the physical archive: `os.getcwd()` is already physical, so no alias is involved |

I found no bypass. `Path.absolute()` keeps `..` verbatim, so no spelling of a parent hop reaches
`resolve()`. What remains accepted is an ancestor symlink with no `..`, which is the documented design
(`/var`, `/tmp`), and every byte read is still authenticated against the custody digests.

## Findings

| # | Sev | Finding | Required action |
|---|---|---|---|
| R3-F1 | Info | `scripts/test_timings.json` still records about 20 s for `test_b6_production`. With the sixteenth test, which runs a full synthetic recompute, the author measured 26 s. | None now. Refresh the entry at the next timings update. |
| R3-F2 | Info | The brief's `env -u TMPDIR` does not select `/var/folders` on this machine; it selects `/tmp`. | None. Use the inherited `TMPDIR` or `getconf DARWIN_USER_TEMP_DIR` in future briefs. |
| R3-F3 | Info | The checker-only witness patches `harvest.anchor_envelope` module-wide and perturbs only the first call. It is sound today because the comparator-pass and single-`harvest_bound` assertions would fail if the primary producer ever consumed that call instead. | None. |

Carried forward, unchanged by this round: R2-F4 to R2-F6 (Info) and the lead-owned F1/R12 ruling.
