# Paper 1 seat 7: Opus cold review of the Block 6 analysis path, option (c)

Date: 2026-11-11 (PST). Reviewer: Opus 5.5 (cold, Block-5-naive under RL-43).
Target: `analysis/2026-11-11-b6-path` @ `5259dbd5f` (rebased on `origin/main`). Author report:
`docs/run_reports/2026-11-11-p1-seat7.md`.

**Verdict: ADMIT-WITH-FIXES.** The 7b structure holds: the per-phase arithmetic runs from the pinned B5 bytes.
Option (c) with C3 is wired as registered, and the `.zst` read path STOPs on a digest mismatch or a missing
binary. The synthetic dry run reproduces bit for bit. Before the S-14 pin, three test gaps must be closed (F2,
F4, F5) and the tests must pass under a default macOS `TMPDIR` (F3). Separately, the lead must rule on R12's
timing (F1).

## Blind status and what was read

Read: RL-6, RL-24 (seat 7 row), RL-25, RL-30 on `origin/audit/2026-11-10-fable`. Also the §17 draft on main,
§17-DLE2 to §17-R12. Also the branch diff (`git diff origin/main...HEAD`) and the pinned B5 functions it
calls (`add_machine`, `machine_member`, `MeterStream.offset`, `Reader`, `MemberPool`, `_member_worker`).
I did not open: `RESULTS.md`, `REDERIVATION.md`, `rederivation.tsv`, `hand_checks_phase2.tsv`, seat-4
reports, RL-38 to RL-42, `RUN_STATE.md`, any Paper 1 text, or any custody, night, archive or restricted path.
Every run used synthetic trees in my scratch directory. No Block 6 number was seen. RL-25's own text quotes two
calibration-acceptance allowances (14.531 / 10.818 ms). Those are registration parameters, not outcomes.

## Checks run

| Check | Result |
|---|---|
| `shasum -a 256 scripts/independent_recompute_b5.py` | `d49103e8…a2e4e0`, the pin. File not touched on the branch (no diff vs main). |
| Vendored S-3/S-4/S-18 + `desk_compress.py` vs `f31aca19f` | All four byte-identical. `joulewise/flags/exclusions.py` is identical to `f31aca19f` too. |
| `test_block6` (26), `test_flags_exclusions` (34), `test_harvest_twin` (16), `test_engine_twin` (12) | PASS |
| `test_b6_production` (9), default macOS `TMPDIR=/var/folders/…` | **FAIL: 2 failures, 3 errors, all `input_symlink`** (F3) |
| `test_b6_production` (9), `TMPDIR` under `/private/tmp/…` | PASS |
| `scripts/b6_synthetic_dry_run.py --workers 1` and `--workers 2` | Both exit 0, comparator `True`, 0 flags; restricted SHA-256 `c6bae5e4cb58…7fec809` both times. This equals the author's receipt. |
| Mutation testing, 11 mutants against both B6 modules (table below) | 6 killed, 5 survive |

### Mutation results (point 5: would the tests fail on wrong code?)

Every mutant was applied in the worktree, run against `test_b6_production` and `test_block6`, then reverted with
`git checkout`. The worktree was confirmed clean afterwards.

| Mutant | Killed by |
|---|---|
| M1: add 1 mJ to every pinned `add_machine` cell mean | `test_7b_…`, `test_blind_dry_run_…` |
| M2: printed per-phase line taken from the wrong cell | **survives** |
| M2b: printed decode per-phase line scaled by 1.001 | **survives** |
| M3: B5 digest check removed from `load_pinned_b5` | `test_loaded_b5_is_exactly_the_release_pin_…` |
| M4: decompressed-digest check removed from `AuthenticatedInputs.read` | `test_zst_bytes_checked_…`, `test_harvest_pin_…` |
| M5: missing `zstd` no longer refuses | `test_zst_bytes_checked_…` |
| M6: C3 called with `pack_scoped=True` | **survives** |
| M7: C3 comparison forced to "agrees" | `test_c3_disagreement_…` |
| M8: option-(c) checker failure no longer raises the STOP flag | **survives** |
| M9: `compression_record_missing` refusal removed | **survives** |
| M10: double b_op fed to the pinned `add_machine` | `test_7b_…` |

On the old code (the pre-seat lane `b324be1b4`), the new production module cannot import its support modules,
so it fails trivially. The mutants above are the meaningful form of point 5.

## Findings

| # | Sev | Point | Finding | Required action |
|---|---|---|---|---|
| F1 | **High (lead ruling)** | 2 | §17-R12 is titled **"Fixtures before S-14 is cut"**: real-chain fixtures at `f31aca19f` covering waited/attempt-N, wait-cap and budget skips, `anchor_not_bounded`, mixed campaign-log rows, compressed logs and plists, and a cross-session GAMMA unit. The seat's report (limitation 2) calls the real-chain replay a *release* gate, and its fixture is handmade. RL-24's acceptance also says "full-size synthetic"; the fixture has full member topology but 16 raw records per member. | The lead either runs the R12 real-chain fixture before cutting S-14, or logs the moved gate as a deviation. Not a code defect in this seat. |
| F2 | **Medium (fix before pin)** | 1 | The 7b witness (`test_7b_b6_phase_output_equals_b5_own_output_including_corners`) compares only the raw disclosure `result["whole_machine"]` with the oracle. The *printed* per-phase line (`result["lines"][cid]["whole_machine"]`, then `session_quantities` → `lines/whole_machine/<model>/<phase>/mean_j`) is checked only for not-None, 4 corners and the boundary label. M2 and M2b survive. The synthetic meter is a constant 50 W step (`support_b6_production.py:41`), so decode and p2048 both print exactly 50.0 J with zero spread. The one 50 J assertion therefore cannot tell those cells apart (it does guard against p42, which prints 1.5625 J). The key mapping already produced one bug this seat (p42 overwrote p2048). | In the 7b test, for every non-p42 cid, assert that the printed line minus the added label keys equals `oracle[…]["cells"][cid]`. Also assert that each `session_quantities` key equals the oracle cell's `mean_j`. Give decode and prefill different synthetic powers or durations so a swap shows. |
| F3 | **Medium (fix before pin)** | 4, 5 | `AuthenticatedInputs.__init__` rejects a symlink in **any ancestor** of the archive path. On macOS `/var` and `/tmp` are symlinks, so with the default `TMPDIR` 5 of the 9 production tests fail with `input_symlink`. A real run from a `/tmp/…` path would also refuse. That fails safe, but the test module is environment-dependent; it passed for the author only because of the shell's `TMPDIR`. | Either resolve the test temp roots (`Path(tmp).resolve()`), or resolve the archive root once and refuse symlinks only below it. Re-run the module under a default `TMPDIR`. |
| F4 | **Medium (fix before pin)** | 2, 5 | No test shows that a disagreement on the option-(c) second side (checker or comparator) holds the run. M8 survives. That disagreement → hold is DLE-2 item 4 / CARE §2.5 item 3, the core of option (c). | Add a negative witness: perturb one checker-compared quantity (for example, one member's stored energy inside the bar of the reducer check but outside the twin's), then assert `option_c_disagrees` and exit 3. |
| F5 | **Medium (fix before pin)** | 2, 5 | C3 passes `pack_scoped=False` as R6 registers ("no pack-scoped window reasons"), but no B6 test depends on it. M6 survives. | Add a GAMMA synthetic session with a window `neg8.midpoint_lost` flag and an acceptance record without `neg8.midpoint_lost_primary`. Assert C3 agrees, and that with `pack_scoped=True` it would disagree. |
| F6 | Low | 3, 5 | Untested refusal paths: `compression_record_missing` (M9 survives), absolute-path `relocations` and `compression_relocation_ambiguous`, `input_digest_conflict`, `request_comparison_record_missing` / `_member_missing`, and `disclosure_coverage_*`. Without the M9 refusal, a `.zst` file listed only in `SHA256SUMS` would still be hash-checked, but against SHA256SUMS rather than the desk record that R11 names. | Add one-line negative tests. Not blocking alone. |
| F7 | Low | 3 | `MemberPool.PoolReader.raw` (`independent_recompute_b6.py:166-168`) falls back to the unauthenticated B5 reader when a path lies under no context archive. In production every archive has a context, so this does not trigger today. It is still a fail-open seam. | When `contexts` is non-empty and none matches, raise `InputRefusal("input_outside_archive")`. |
| F8 | Low | 1 | `clock_journal` is optional in the pin. If it is omitted, the pinned `MeterStream.offset` loses its journal fallback. That shows as `meter_offset_unavailable` only when the stream's own header/trailer offset fails. | Require `clock_journal` whenever the archive's `SHA256SUMS` lists `…/monitor/clock.jsonl`. |
| F9 | Info | 3 | `desk_compress.read_bytes` streams from `zstd` stdout but holds each file's full decompressed bytes in memory, which the digest-before-parse rule requires. That is fine per file. Watch peak RSS on the largest meter or plist file on the Air. | None. |
| F10 | Info | 2 | Under option (c), the ALPHA/BETA floor estimators (B5 `make_reported`, `make_floors`) have no second producer. The checker covers counting, calibration, run phase energies, harvest bounds, NEG-8, GAMMA engine, pairing and §10-§11. That is the audit's design of (c) (twins + checker + reducer gate), not a seat defect. The lead should know it when citing the agreement. | None. |

## Point-by-point

1. **7b condition: holds structurally; the witness needs F2.**
   - `load_pinned_b5` hashes and `exec`s the *same* bytes. A mismatch raises `b5_script_digest_mismatch`, and the
     test covers it.
   - `add_session_machine` calls `B5.add_machine` directly. The four edge-shift corners, `machine_member`
     (→ `sampled_gross`) and `phase_machine_mean` all run inside the pinned file. A test asserts that the
     `co_filename` of the six named functions is the pinned path.
   - The seat's only interventions are I/O and labels:
     - it stages authenticated meter, clock and `withheld/meter.json` bytes in a temp dir, as RL-30 allows;
     - members and b_op are supplied from outside (B6 acceptance, 10.818 ms, per R5);
     - the boundary sentence and the single-implementation label are added;
     - the battery count is taken from harvest `battery.assist`, as RL-30/S17-02 rules.
   - No module global of B5 is reassigned except `B5.Reader` during the pool fork, which is reverted in
     `finally`. No arithmetic is copied.
   - Block 5's side is read from the released output's `disclosures.whole_machine…cells[*].mean_j`, never
     recomputed.
   - The oracle in the equality test calls the same `B5.add_machine` on the same members, without the staging
     dir. That fits RL-30's "on the same input", but it covers only the raw disclosure (F2).
2. **Option (c) + C3: implemented as registered, apart from the test gaps F4 and F5 and the R12 timing (F1).**
   - C3 uses the sealed `compute` with the B6 catalog at its pinned digest, `pack_scoped=False`, and never reads
     `claim_usable`.
   - Member codes, window reasons and kept units are checked against acceptance, and a disagreement is a STOP.
   - Counting comes from acceptance and the loop, and they must agree.
   - The second side is twins + `b6_analysis_check` + the reducer gate (`stored_energy_mismatch` is a STOP). The
     comparator receives only checker-produced rows, and the per-phase line is excluded as R3/S17-03 requires.
   - The L9 audit state is recorded before the run (`l9_audit: not_run|completed`; pending refuses), per RL-25
     flag 6.
3. **`.zst` read: compliant.**
   - Each read decompresses through the `zstd` binary on stdout and checks SHA-256 before any parser sees a
     byte. A test patches the parser and asserts it is never reached.
   - A compressed file needs a desk-record row, and a record row may not conflict with `SHA256SUMS`.
   - A missing binary raises `zstd_unavailable`, a mismatch raises `input_digest_mismatch`, and `main` turns both
     into exit 4.
   - The binary's path and version go into the census.
   - The final census re-reads every named input with no cache.
4. **Synthetic blind dry run: reproduced.** Exit 0, comparator pass, digest identical to the receipt, and serial
   and 2-worker runs byte-identical. One caveat: it passes only with a non-symlinked temp root (F3).
5. **Tests fail on wrong code: partly.** The digest, read-path, C3 and reducer refusals are guarded. The printed
   7b line, the option-(c) hold and `pack_scoped` are not (F2, F4, F5).
6. **Real Block 6 data in tests: none found.**
   - Every test and the dry run build marked synthetic trees under a temp root. The `sources/night-custody/…`
     strings are relative paths *inside* those synthetic archives.
   - `Session` refuses an archive that has neither authenticated inputs nor the synthetic marker.
   - Under `JW_B5_SYNTHETIC_ONLY=1`, an unmarked archive refuses (exit 4).
   - The fixture sealer refuses unmarked trees.
   - No absolute or home path appears in the tests.

## For the S-14 pin

7b can be declared shown once F2's strengthened witness passes. Pin only after F2 to F5 land and the
production module passes under a default `TMPDIR`, and after the lead's F1 ruling on R12. F6 and F7 are
cheap and worth folding into the same fix commit.
