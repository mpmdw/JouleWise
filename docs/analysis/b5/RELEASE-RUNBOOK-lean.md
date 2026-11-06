# Block-5 lean release runbook (DLE-1)

**Authority.**
- The release procedure is DLE-1 of `docs/analysis/b5/DEVIATION-LOG.md`, adopted 2026-11-06. It replaces PLAN §3.2
  item 2.
- The program is `scripts/release_b5.py`.
- Its tests are in `tests/independent_recompute/test_release_b5.py` and `test_member_pool.py`.

**What it does.** It runs three checks on the blind dry run's custody, BEFORE anything is unsealed, and prints a
blinded verdict:
- **(a)** It re-verifies every digest the dry-run record holds, against the custody, the indexed inputs and the
  pinned commit.
- **(b)** It runs the independent recompute with a 10-process member pool.
- **(c)** It runs the comparator with the release bar set.

The verdict carries only:
- agree or hold, per comparator family, with pass and fail counts;
- structure codes and counts.

It never carries an energy, a difference or an outcome word. The values stay in the restricted folder you name.

**Unsealing is a separate step and needs Ed's OK.** Nothing in this runbook unseals or displays an outcome value.

## 0. Before you start

- Run it on the Air, or on any host that holds the dry-run custody and the three windows' archives and run roots.
  It needs no measurement hardware.
- You need a **clean** checkout of this branch, or of `main` once it has merged. `release_b5.py` refuses
  `release_checkout_not_clean` if `git status --porcelain --untracked-files=all` shows anything. This guarantees
  that the programs which run are the committed ones.
- You need the following facts. They are structure only; none of them is a value.

  | Name | What it is |
  |---|---|
  | `CUSTODY` | The dry run's custody root: the folder that holds `dry-run/B5-BLIND-DRY-RUN-RECORD.json`. Use the dry run being released (dry-j or dry-k). |
  | `PINNED` | The dry run's analysis commit, 40 hex digits. It is the record's `analysis_commit`. |
  | `INDEX` | The window index the dry run read. Its SHA-256 must equal the record's `window_index_sha256`. If `configs/analysis/b5/analysed_windows.json` has not changed since `PINNED`, use the tracked file. Otherwise extract it: `git show $PINNED:configs/analysis/b5/analysed_windows.json > $OUT_PARENT/analysed_windows.json`. |
  | `OUT` | A **new** folder in restricted custody, for example a sibling of the custody root. It must be outside this checkout and outside `$CUSTODY/dry-run/restricted`. The program creates it with mode 0700 and refuses if it already exists. |

## 1. The command

```bash
cd <clean checkout of lane/2026-11-06-b5-lean-release, or main after merge>
test -z "$(git status --porcelain --untracked-files=all)" || echo "checkout not clean"

CUSTODY=<dry-run custody root>
PINNED=<record analysis_commit>
INDEX=configs/analysis/b5/analysed_windows.json        # or the copy extracted from $PINNED
OUT=<new restricted folder, e.g. $(dirname "$CUSTODY")/release-check-$(date -u +%Y%m%dT%H%MZ)>

nice -n 19 taskpolicy -b python3.13 -B scripts/release_b5.py \
    --custody "$CUSTODY" --window-index "$INDEX" --pinned-commit "$PINNED" \
    --restricted-out "$OUT" --workers 10
echo "exit=$?"
```

- **Interpreter.** Use `python3.13`, the one the heavy runs and CI use. The recompute records its interpreter in
  its restricted output.
- **Priority.** Drop `nice -n 19 taskpolicy -b` only when no measurement or heavy run shares the host.
  Background QoS keeps the job on the efficiency cores and makes it several times slower (section 3).

## 2. Reading the result

`stdout` is one JSON verdict. The same bytes are in `$OUT/verdict.json`.

| Exit | `verdict` | `reason` | Meaning | Next step |
|---|---|---|---|---|
| 0 | `agree` | null | (a) verified; the recompute is clean (exit 0, `comparison_stopped` false); the comparator exits 0 (every family passes, 0 unmapped, no absent or non-finite step-11 output). **The DLE-1 release condition holds.** | Ask Ed for the unseal OK. |
| 1 | `hold` | `comparator_disagreement` | At least one family has `fail` > 0. The verdict shows which, with counts only. | DLE-2 disagreement rule: the release is held. A blind seat traces the disagreement structure-only from `$OUT/comparison.json`. Which side prints is decided by the defect found, never by the value. |
| 2 | `hold` | `release_digest_differs_from_dry_run` | Stage (a) found a changed or missing output, a changed input, another commit, other sealed digests or another index. The location (a path, never a value) is in `$OUT/refusal-location.txt`. | R3, as a custody or determinism defect. Do not unseal. |
| 2 | `hold` | `dry_run_record_missing_or_incomplete`, `dry_run_record_invalid`, `dry_run_not_completed` | The record is absent, malformed, a release-mode record, or has a tooling refusal. | Fix the input. A dry run with a tooling refusal must first complete (PLAN §3.2 item 1). |
| 2 | `hold` | `release_checkout_not_clean`, `release_checkout_unavailable`, `pinned_commit_invalid`, `pinned_commit_unavailable`, `window_index_unreadable`, `window_index_invalid` | Environment or binding problem. | Fix and re-run into a new `$OUT`. |
| 2 | `hold` | `recompute_failed`, `recompute_output_unreadable`, `recompute_comparison_stopped` | The recompute exited non-zero, or raised a STOP flag. Its structure-only `stdout` is in `$OUT/recompute.stdout`; for example, `exclusions_rederivation_mismatch` or `trace_plist_missing`. | Tooling defect: R3, blind. |
| 2 | `hold` | `comparator_refused`, `comparison_output_unreadable` | The comparator refused. Its code is `stages.comparator.refused`, and the step-11 coverage counts are in `stages.comparator.step11`. | Tooling defect: R3, blind. |

**What the verdict shows.**
- `stages.digests`: how many outputs and input-census rows were re-hashed. `input_census_binding_rows` counts the
  `binding/plan_tree` rows, which are L9's own binding and are not files.
- `stages.recompute`: exit status, worker count and wall time.
- `stages.comparator`: per family, `verdict` (agree or hold) with `pass` and `fail`; the bar-set name; step-11
  coverage counts; the structure-flag count.
- `release_checkout.commit`: the commit whose programs ran.

As a last guard, `release_b5.py` replaces any verdict whose bytes read as a decimal number with
`verdict_not_structure_only`.

**What stays restricted, in `$OUT`.**
- `recompute.json`: every value.
- `comparison.json`: values, differences and bars.
- `recompute.stdout` / `.stderr` and `comparator.stdout` / `.stderr`.
- `refusal-location.txt`.

Do not open these before the unseal OK, except to trace a hold blind, structure-only.

## 3. Expected wall time

**Measured** on the full-size SYNTHETIC window. This is the committed S10 fixture, extracted by
`tests/independent_recompute/fullsize_window.py`: 316 compared runs, about 1.1 GB on disk. It ran on this Air at
`nice -n 19 taskpolicy -b`, beside the live real-data run. Measurements are below.

TIMING-TABLE

**Projected on real block-5 data.** These are estimates. The care audit's section 2.3 explains them:
- The cost is dominated by one plistlib parse of each member's raw trace. That is about 316 traces of about 130 MB
  each, or about 41 GB.
- **Stage (a).** It re-hashes the input census, the same files the dry run's step-0 census hashed, which took 85 s on
  dry-j. It also re-hashes the restricted outputs (MB). Expect **about 1.5-3 min** (8 hashing threads, I/O bound).
- **Stage (b).** With 10 workers on a free host: **about 5-8 min**. The member parse spreads across the cores. What
  remains serial is the sensitivity re-envelopes, the reconstruction diagnostic and the statistics, each of which
  costs a fraction of one parse per member.
  - At background QoS beside another heavy job, expect several times longer.
  - With `--workers 1`, about 25-65 min.
- **Stage (c).** Unmeasured at full size. The comparator reads only the restricted step outputs and the recompute's
  output (MB, not GB). Expect **under 2 min**.
- **End to end: about 8-13 min on a free host.** That compares with one heavy release re-run of 136-152 min.

## 4. Before running on the real custody: the synthetic rehearsal

To check the installation, run the tests:

```bash
nice -n 19 taskpolicy -b python3.13 -B -m unittest \
    tests.independent_recompute.test_release_b5 tests.independent_recompute.test_member_pool
# Full-size worker-count determinism (extracts about 1.2 GB; minutes at background QoS):
JW_B5_FULLSIZE_RECOMPUTE=1 JW_B5_FULLSIZE_DIR=<scratch folder outside the checkout> \
    nice -n 19 taskpolicy -b python3.13 -B -m unittest tests.independent_recompute.test_member_pool
```

`test_release_b5` runs stages (a)-(c) end to end on synthetic custody. It covers agreement, a disagreement, tampered
outputs, inputs, commits, seal pins and index, a symbolic link, an incomplete record, a dirty checkout and a
recompute STOP flag. It also runs the real recompute on synthetic archives.

## 5. What the lean recompute does not cover

The recompute and the comparator do not re-derive every quantity the plan prints. The list is in
`docs/analysis/b5/LEAN-COVERAGE-AUDIT.md` §2, mostly §8 disclosure lines:
- monitor cost;
- the arm and host summaries;
- the battery phase, subject and temperature lines;
- the full reference, attempt and G10 history.

Those lines print from the L9 dry-run outputs, which stage (a) verifies byte for byte. They have no independent
recomputation. RS item 83, ruling 3 applies: any uncovered leaf the paper prints is checked by hand by the
post-release reader before it enters the paper, against a source the audit names.
