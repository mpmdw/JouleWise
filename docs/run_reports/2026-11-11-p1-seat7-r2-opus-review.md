# Paper 1 seat 7, round 2: Opus cold review of the F2–F8 fixes (Block 6 option (c))

Date: 2026-11-11 01:32 PST. Reviewer: Opus 5.5 (cold, Block-5-naive).
Target: `analysis/2026-11-11-b6-path` @ `3daa274ebfcb722dc17b1afb0697e210b9029613`.
Round-2 diff reviewed: `git diff da0a03145..3daa274eb` (implementation `fa0373cc9`, author report `ae4c0b156`).
Author report: `docs/run_reports/2026-11-11-p1-seat7-r2.md`. Prior review: `docs/run_reports/2026-11-11-p1-seat7-opus-review.md`.

**Verdict: ADMIT-WITH-FIXES.** F2, F3, F5, F6, F7 and F8 are closed, and each fix has a test that fails on
the wrong code. All 11 of the prior review's mutants are killed, and so are 10 of my 13 new ones. F4 is only
half-closed. Its new witness perturbs a quantity that both the checker and the comparator see, so the checker
arm of the option-(c) hold is never exercised on its own. With that arm removed (mutant N8), a scratch probe
gets 1777 checker failures and still exits 0. The production code is correct today: the same probe exits 3
on unmutated code. Only the witness is missing. Add one test for it (R2-F1) before the S-14 pin. The other
findings are Low or Info. F1 (the timing of §17-R12) is still the lead's ruling and is outside this round.

## Blind status

Read: the prior Opus review (F1–F10 and its mutant table), the round-2 author report, the full code diff
`da0a03145..HEAD`, and the current `joulewise/b6_analysis_inputs.py` and `joulewise/b6_analysis_check.py`
(`check_block`). From `scripts/independent_recompute_b6.py` I read only the sections the round touches or
that my mutants target: loader, `MemberPool`, `Session.__init__`/`check_exclusions`, `session_quantities`,
`add_session_machine`, the option-(c) assembly in `recompute_block`, and `main`. In the pinned B5 script I
grepped only for the clock-journal path and the `b_op_s` uses. I also read the `seal`/`stream_file` support
code. The seat-1 author report was used only for its vendored-file list.

Not opened: `docs/analysis/b5/RESULTS.md`, `REDERIVATION.md`, `rederivation.tsv`, `hand_checks_phase2.tsv`,
any seat-4 report or its review, RL-38 to RL-42, `RUN_STATE.md`, anything under `docs/paper/paper1/`, and any
custody, night-*, archive, restricted or real-session path. No real Block 5 or Block 6 data was opened.
Every run built marked synthetic trees under my scratch `TMPDIR`
(`/private/tmp/claude-501/…/scratchpad/rev7`) or the default macOS `TMPDIR`. No study outcome was seen. The
structural diff of old against new dry-run output (check 5) compared two synthetic fixture outputs only.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | `test_b6_production` (15) under the **default macOS** `TMPDIR=/var/folders/…/T/` | PASS (22.1 s). F3's failure no longer reproduces. |
| 1b | Same module with `TMPDIR` unset (`/tmp`) | PASS (19.1 s) |
| 1c | `test_b6_production`, `test_block6`, `test_flags_exclusions`, `test_harvest_twin`, `test_engine_twin` under the scratch `TMPDIR` | 103 tests, PASS. No regression in the three named modules. |
| 2 | `shasum -a 256 scripts/independent_recompute_b5.py` | `d49103e884cc…a2e4e0`, the pin. No diff against `da0a03145` or `origin/main`. |
| 3 | Vendored files against `f31aca19f`: `flag_catalog_b6.json` (S-3), `registration/acceptance.json` (S-4), `registration/identity_pins.json` (S-18), `desk_compress.py`, `flags/exclusions.py` | All byte-identical |
| 4 | `b6_synthetic_dry_run.py --workers 1` and `--workers 2` | Both exit 0, comparator `True`, 0 flags. Numbers, public JSON, stdout and stderr are byte-identical. Restricted SHA-256 is `7eae099a05a38aa850ac980f3e5658e7805932f3b5f30db72068eb2b641bf590`, which equals the report. |
| 4b | Report's explanation of the SHA change | Consistent. At `da0a03145` the dry run reproduces `c6bae5e4…7fec809`. Every key that differs between old and new output is a meter-derived phase quantity (`energy_J`, `mean_W`, `gross_share`, `mean_j`/`lower_j`/`upper_j`, corner `change_j`, medians), a digest of a changed synthetic source (`sha256sums_sha256` ×10, `compression_sha256`, `run_inputs_sha256`), or `program_sha256`, which is recorded in the output. Nothing else changed. |
| 5 | F2 witness | The synthetic meter now runs 10 W baseline, 40 W prefill and 60 W decode. The 7b test asserts that for each non-p42 cell the printed line minus four label keys equals the oracle cell, including all four corners. It also asserts that every `lines/whole_machine/<model>/<phase>/mean_j` equals the oracle `mean_j`, and that decode ≠ p2048. |
| 6 | F3 boundary | A symlink at the root (`root_alias`), a file symlink below it and a directory symlink below it all refuse `input_symlink`. An ancestor alias is accepted, maps to the canonical root and reads identical bytes. Member components are checked from the resolved root, `..`/`.` are refused, and `read` opens `self.archive / name`. The relaxation therefore cannot be used to reach anything below or outside the root (mutants N1, N2, N6, N11). See R2-F3 for one cosmetic bypass. |
| 7 | Real data in tests | None. The only new `night-custody` string is a relative relocation key inside a synthetic archive. No absolute or home path appears. |
| 8 | Timings | No new test module. `test_b6_production` (20.055 s) and `test_block6` (10.372 s) are now in `seconds_by_module`, with a provenance note. The JSON parses. `tests.test_shard_split` (36) passes. |

## Mutants

Each mutant was applied as an exact single-occurrence string replacement. It was run against
`tests.independent_recompute.test_b6_production` and then `tests.independent_recompute.test_block6`,
sequentially, with a scratch `TMPDIR` and `JW_B5_SYNTHETIC_ONLY=1`. It was then reverted with `git checkout`,
and the tree was confirmed clean before the next one. `test_block6` passes under every mutant, which is
expected because it does not exercise these seams. The pinned B5 file was never touched.

| Mutant | Target | Result | Killed by (`test_b6_production`) |
|---|---|---|---|
| M1 | +1 mJ on every pinned `add_machine` cell mean (adapter seam) | KILLED | 7b equality; blind dry run |
| M2 | Printed line taken from the next cell | KILLED | 7b equality; blind dry run |
| M2b | Printed decode mean ×1.001 | KILLED | 7b equality |
| M3 | B5 digest check removed | KILLED | B5 pin/tamper |
| M4 | Decompressed digest check removed | KILLED | harvest-pin/escape, clock journal, zst-before-parser |
| M5 | Missing `zstd` returns instead of refusing | KILLED | zst-before-parser |
| M6 | C3 with `pack_scoped=True` | KILLED | GAMMA window midpoint loss |
| M7 | C3 forced to agree | KILLED | C3/reducer stops; GAMMA midpoint |
| M8 | `option_c_disagrees` flag suppressed | KILLED | second-producer disagreement / exit 3 |
| M9 | `compression_record_missing` removed | KILLED | compression/digest refusals |
| M10 | Doubled b_op on the `add_machine` proxy | KILLED | 7b equality |
| N1 | F3 too permissive: member-component symlink check removed | KILLED | harvest-pin/escape (file and dir alias) |
| N2 | F3 root symlink check removed | KILLED | harvest-pin/escape (root alias) |
| N3 | F7 `input_outside_archive` removed from `PoolReader.raw` | KILLED | pool refuses outside contexts |
| N4 | F8 `clock_journal_required` removed | KILLED | listed clock journal |
| N5 | F8 weakened: any non-empty `clock_journal` accepted | KILLED | listed clock journal (wrong pin) |
| N6 | `local()` uses `resolve()`, following symlinks | KILLED | harvest-pin/escape |
| N7 | `read()` opens the supplied path, not the canonical one | survives | Equivalent except for an ancestor swap after init (TOCTOU). Info. |
| N8 | `checks["pass"] = comparator["pass"]`: checker failures ignored | **survives** | R2-F1 |
| N9 | `input_digest_conflict` removed | KILLED | compression/digest refusals |
| N10 | `session_quantities` swaps the decode and p2048 labels | KILLED | 7b equality; blind dry run |
| N11 | F3 too strict: ancestor alias refused | KILLED | harvest-pin/escape (ancestor accepted) |
| N12 | Printed **p42** whole-machine mean ×1.001 | **survives** | R2-F2 |

Score: 11/11 prior mutants killed, and 10/13 new ones (N7 is an equivalent mutant).

**Probe for N8 (scratch only, not committed).** The probe subclasses the production test and adds 0.01 J to
every `harvest.anchor_envelope().max_abs_delta_j` the checker computes. `harvest_bound` is a checker-only
family that the comparison table does not carry.

| Code | Exit | `option_c.pass` | `comparator.pass` | checker failures | flags |
|---|---|---|---|---|---|
| unmutated | 3 | False | True | 1777 | `option_c_disagrees` |
| N8 | **0** | **True** | True | 1777 | none |

## Disposition of prior findings

| Prior | Status | Evidence |
|---|---|---|
| F1 (R12 timing) | Open, lead ruling | Not in scope. The author report says so too. |
| F2 | **Closed** | Check 5. M2, M2b and N10 are killed. The p42 line is still unguarded (R2-F2, Low). |
| F3 | **Closed** | Checks 1 and 6. N1, N2, N6 and N11 are killed. |
| F4 | **Partly closed** | The hold is witnessed, and M8 is killed. But the witness's disagreement also reaches the comparator, so the checker arm is untested (R2-F1). |
| F5 | **Closed** | M6 is killed. The GAMMA fixture shows that C3 agrees with `pack_scoped=False` and disagrees with `pack_scoped=True` (`neg8.midpoint_lost_primary`). |
| F6 | **Closed** | M9 and N9 are killed. `compression_record_missing`, absolute relocation, ambiguous relocation, digest conflict, both request-comparison cases and all four disclosure-coverage cases have exact-match refusals. |
| F7 | **Closed** | N3 is killed. Under that mutant the test fails because the unauthenticated fallback is reached. |
| F8 | **Closed** | N4 and N5 are killed. A missing or wrong pin refuses, the listed journal reads authenticated bytes, and later corruption refuses. |

## Findings

| # | Sev | Finding | Required action |
|---|---|---|---|
| R2-F1 | **Medium (fix before pin)** | The F4 witness (`test_option_c_second_producer_disagreement_stops_with_exit_three`) perturbs `harvest.overlap_energy`. That value appears both as a `harvest_energy` checker failure and in the comparison table's `run_phase_energy_j`, so the comparator alone is enough to hold. The `checks["pass"] and` term in `recompute_block` is the only thing that holds on checker-only families: `harvest_bound`, `counting`, `engine`/`engine_word`/`engine_refusal`, `pairing`, `section11_*`. That term has no witness, and N8 survives. The probe above shows that without the term, a run with 1777 checker failures exits 0 with no flag. That is DLE-2 item 4 / CARE §2.5 item 3, the core of option (c). | Add a test that perturbs a checker-only quantity, for example `harvest.anchor_envelope` as in the probe. Assert `comparator.pass is True`, `option_c.pass is False`, `option_c_disagrees` raised, `comparison_stopped` and exit 3. Re-run N8: it must die. |
| R2-F2 | Low | The 7b loop `continue`s on p42, so the printed p42 whole-machine line is compared with nothing, and N12 survives. Its `session_quantities` key is skipped by design, but the printed line still goes into the restricted output. | In the 7b loop, apply the printed-line-equals-oracle assertion to p42 too. Skip only the quantities-key assertion for it. |
| R2-F3 | Low | The root symlink check `supplied_archive.is_symlink()` tests only the last lexical component, and `Path.absolute()` keeps `..`. So `…/link/derived/..`, where `link` is a symlink to an archive, passes the check and resolves to the target. I confirmed the `is_symlink`/`resolve` behaviour in scratch. In `main` this cannot be exploited, because the pin is looked up by `Path(archive).name == ".."` and refuses `session_input_pin_missing`. Even if it got through, every byte is still authenticated against the custody digests. Direct API callers have no such guard. | Refuse a supplied archive path that has any `..` component (or normalise it before the check), and add a one-line test. |
| R2-F4 | Info | F8 accepts any listed `…/monitor/clock.jsonl`. B6 stages whichever journal is pinned at the one path the pinned B5 reads (`sources/night-custody/hazards/monitor/clock.jsonl`). If `SHA256SUMS` ever lists two clock journals, the pin can name the wrong one and still pass. | None now. If multi-journal archives appear, require the pin to equal the `night-custody` journal when it is listed. |
| R2-F5 | Info | N7 is equivalent apart from an ancestor swap after init. The current `path = self.archive / name` is the right choice, but no test can distinguish it. | None. |
| R2-F6 | Info | `PoolReader.raw` still falls through to the unauthenticated B5 reader when `contexts` is empty. That only happens without `--inputs`, where `Session` refuses an unmarked archive. This is unchanged from round 1 and fails closed in production. | None. |

## For the S-14 pin

With R2-F1's witness in place, 7b is shown and option (c)'s hold is witnessed on both arms. Folding in R2-F2
and R2-F3 is cheap and worth doing in the same commit. The lead's F1/R12 ruling is still required before the
pin.

Scratch receipts (ephemeral, synthetic only): the mutant harness `mutants.py`, `mutants-main.json`,
`mutants-n12.json`, per-mutant logs in `logs/`, `probe_checker_only.py`, and dry-run outputs
`dry1/`, `dry2/` and `dryold/`, all under
`/private/tmp/claude-501/-Users-edr-code-CapstoneProject-JouleWise/41120c85-9f5f-48c9-aa4d-c3d83d4df41c/scratchpad/rev7/`.
