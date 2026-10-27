# RC-B6-1: independent recompute extended to block 6

Seat RC-B6-1, 2026-10-27. Branch `lane/2026-10-27-recompute-b6`, based on
`lane/2026-10-14-independent-recompute` at `9ca87bce`. Synthetic data only.

## SUMMARY

- **What exists.** `scripts/independent_recompute_b6.py`, the second implementation the block-6 release compares
  against. It has three commands:
  - `block`: every block-6 session.
  - `single`: one newly harvested session, on the day it lands.
  - `compare`: the S-13 comparator.
- **What it is built on.** It reuses the independent block-5 script's raw-record arithmetic, loaded by file path. Its
  block-6 rules come from the registration text. Counting comes from the loop's acceptance records. GAMMA is paired
  by registered round.
- **Synthetic result.** On a nine-session synthetic block:
  - Clean data agrees within the S-13 bars, with 0 observed difference on a rerun.
  - A 1 ms edge shift is caught at about 10 mJ on its run, against the 1 mJ bar.
  - A dropped power record is caught.
  - Public outputs pass a structure-only guard.
- **Lead rulings applied (milestone 2).** The lead ruled on all six NEEDS_RULING items; see LEAD DECISIONS.
  - The comparison precision is ratified.
  - The key contract is published at `configs/b6/recompute/comparison_keys.json`.
  - The release comparison requires a closed block run (`compare --release`).

## Independence

- **No shared code.** Nothing is imported from `joulewise/`, lane L9 (`joulewise/b5_analysis/`), the block-6 analysis
  driver (`joulewise/b6/analysis/`), the reducer or the validator. The only code dependency is
  `scripts/independent_recompute_b5.py`, the existing independent lineage. Its SHA-256 is recorded in every output
  (`b5_program_sha256`).
- **Texts the arithmetic comes from.**
  - Registration `docs/registrations/block6_replication_DRAFT.md` at origin/main: §1.7, §1.8, §3.3, §4, §6.2, §8.2 to
    §8.3, §9, §10, §11 and §12.3.
  - B5-PLAN, through the block-5 script's existing implementation.
  - Ed's ruling and the cadence plan §4: per-session analysis as data lands.
- **Record formats read**, at the pin `f31aca19f`, for field names and file locations only:
  - `joulewise/b6/acceptance.py`: the `derived/b6-acceptance.json` writer and `evidence_from_archive`.
  - `joulewise/b6/loop.py`: the `attempts.jsonl` record.
  - `joulewise/b6/queue.py`: outcome statuses and `reharvested` corrections.
  - `joulewise/b6/calibration.py`: the keys of the calibration block.
- **Disclosure: harvest screen code.** To find the `withheld/b6-neg8.json` field names, I also saw the harvest's
  `joulewise/b6/survivor_screen.py`. That is harvest code, not the analysis driver, the reducer or the validator. The
  §1.8 screen here is written from the registration text, and it does not read that file.
- **Analysis-driver side.** I read only the interface paragraph of the driver seat's *report*
  (`.codex-report/B6-AN-1.md`, "Independent recompute, block-6 adaptation"), for the shape of the keys. None of the
  driver's code was read.

## What is built

### Per session (`Session`, `compute_session`)

- **Counting (§4)** comes from `derived/b6-acceptance.json`: `counting` true, `verdict` ACCEPT and no physics stop.
  - The loop's `attempts.jsonl` outcome for that session and pack must agree. Optionally, `state.json` supplies the
    `reharvested` corrections, as `queue.counting_ids` applies them.
  - A disagreement raises `counting_disagrees`, which stops the comparison.
  - No block-5 `exclusions.json` or `claim_usable` is read anywhere. This answers the scout's item-53 counting defect.
- **Kept units (§8.3)** are the roster units with no run in the acceptance record's member-scoped `excluding` rows. A
  removed quad run removes its quad.
  - The kept counts are checked against the record's `cells` (`acceptance_kept_count_mismatch`).
  - Each kept unit is then validated by the block-5 unit checks: shape, models, GAMMA tags, usability and 3 records.
  - A kept unit that fails validation raises `kept_unit_not_validated`.
- **b_op (§1.7, §3.3)** = max(pre, post) + max(|post − pre|, 10.818 ms).
  - The captures come from the archived capture records, as in block 5.
  - The result is checked against the acceptance record's `operative_bound_s` at 1e-6 relative.
- **Drift screen and allowance (§1.8)**, from the survivors:
  - The corpus is the first 12 clean corpus runs in committed order. At least 6 are needed, otherwise the screen is
    `undefined`.
  - At least 2 surviving start and end references are needed.
  - No spare references: a spare raises `neg8_spare_present`.
  - The screen is evaluated on the gross and the idle-subtracted families. The allowance is max(spread, bound) on
    gross energies. A lost midpoint narrows the spread and removes nothing.
  - The verdict, survivor counts and clean-corpus count are checked against the acceptance record.
- **Estimators 1 to 3 (§9.1 to §9.3)** for ALPHA and BETA use block 5's functions unchanged, per session:
  - reported cells, per-token values and attribution floors;
  - absolute and comparative floors, with corner widening and the guard;
  - the floor gate per model and phase;
  - the four R and R_cm per model.
- **Estimator 4 (§9.4)** for GAMMA, per session:
  - dbar, metrology and decision intervals, the t test, and Holm over the session's two contrasts;
  - the floor gate from the paired sessions, the outcome word, leave-one-out and the ceiling;
  - the descriptive energy ratio and per-token values.
- **Pairing (§6.2)** follows rules 1, 2 and 3 over counting floor sessions:
  - Without a block-5 input, a missing floor is labelled "floor unavailable"; with one, "floor from block 5".
  - Before `--closed`, rules 2 and 3 are marked provisional (`pairing_provisional`).
  - Non-counting GAMMA sessions are paired the same way, for §11.4.
  - The dominance branch sentence is printed once per GAMMA pairing (§9.3).
- **§9.5 lines.**
  - Item 1, load-correlated sensitivity: restores units removed only by thermal or contention codes.
  - Item 2, battery assist: removes units with a `battery.assist` run.
  - Item 3, scaled drift allowance: on cells, floors and contrasts.
  - Item 4, single-step reconstruction: on floor cells.
  - Item 6, cross-session consistency: GAMMA side means against the paired reported cell.
  - Item 8, waited runs: removes units with an `idle.waited` run.

### Block (`block_lines`)

- **§10 between-session summary:** n, mean and sample SD per quantity, over block 5's value (when `--block5` is
  given) and the counting block-6 sessions. Nothing else.
- **§11.1 side by side:** Δ = mean(block 6) − block 5, plus each session's own difference from block 5.
- **§11.2 replication word:**
  - "replicated" only if every counting GAMMA session has block 5's outcome word and sign.
  - No word if block 5 is absent or `not_estimable`.
  - A "short" sentence below 3 counting sessions.
  - The flagged-inclusive sessions' words are printed beside it.
- **§11.4 flagged-inclusive line:**
  - It adds non-counting sessions with no W1, W2, W3 or S1 condition, whose strata all reach 5 kept units and whose
    b_op and drift screen are defined.
  - Session-level exclusions are ignored for it; run exclusions are kept.

### Single-session mode (`single`)

- One archive, with the loop records when they already hold the session.
- It writes the same restricted per-session result and a structure-only public file.
- A GAMMA session run before its floor sessions exist has no floor gate. Its dbar, intervals and test are computed,
  and its outcome word waits for the block run (NEEDS_RULING 5).

### Comparator (`compare`)

- **Inputs:** this script's restricted output and the driver's comparison table. The table is
  `{sessions: {id: {quantities, run_phase_energy_j}}, block: {quantities}}`; any nested mapping is flattened to `/`
  keys.
- **The join** is key by key.
  - Run phase energies must agree within 1 mJ.
  - Every printed float must agree within 0.5 × 10^−d, where d is its printed decimal places.
  - Words, booleans and integers must be exactly equal.
  - A key on only one side fails its class (unmatched).
  - A key with no print precision fails.
- **The restricted output** keeps every row: both values, the observed difference and the bar. Each class's largest
  observed difference sits beside its bar; differences never set a bar.
- **The public output** has only pass/fail and counts per quantity class, plus whether the print table was ratified.

### Blinding

- **Synthetic-only guard.** Under `JW_B5_SYNTHETIC_ONLY=1` the script opens nothing unless the archive root carries
  the `SYNTHETIC_BLOCK6_FIXTURE` marker. Otherwise it exits 4 before any read.
- **Public files** pass `require_structure_only`, which refuses any float, any decimal- or exponent-looking token,
  and any outcome, direction or replication word.
  - Flag codes appear only when they are structure codes. All others are counted as `restricted_flag_count`.
  - Stdout carries counts, the stop state and the restricted digest.

## LEAD DECISIONS

Rulings from the lead session, 2026-10-27, made blind, on this seat's NEEDS_RULING 1 to 6. Each is applied in the
script, with the decision cited in a comment.

1. **Comparison precision is ratified.** The proposed table is ratified as the S-13 comparison precision and renamed
   `RATIFIED_COMPARISON_DECIMALS`.
   - It is at least as fine as anything the paper prints, so it only makes the half-unit bar stricter.
   - The paper may print fewer digits, which never loosens the comparison.
   - `compare` uses it by default and reports `print_spec_ratified: true`.
   - Ed may override it before the release.
2. **The key pattern is the contract.** It is published, as key names only, at
   `configs/b6/recompute/comparison_keys.json`, written by the new `keys` command from a block run. The file holds:
   - the per-pack session keys (ALPHA 100, BETA 100, GAMMA 89);
   - the 52 same-day GAMMA keys;
   - the 310 block keys;
   - the run-energy key form, `<run_id>/<phase>`.
   
   B6-AN-1 is to emit exactly these keys. Two changes follow:
   - Run energies are compared for a defined set: every run of a kept unit, the surviving screen references and the
     clean corpus.
   - The load-correlated line is always printed, restoring nothing when no unit was triggered, so every session's key
     set is fixed. A test checks that each synthetic session's keys equal the published set.
3. **The idle-subtracted screen family** uses the block-5 recompute's REG 5.8 idle source: `rail_idle_power`,
   elapsed_ns-weighted rich idle telemetry.
4. **The release comparison requires `--closed`.** `compare --release` fails unless its recompute input is a
   `BLOCK` run with `closed: true` (`release_inputs_valid`). Provisional pairings are for same-day checks only.
5. **Same-day GAMMA in single mode** compares run energies and floor-free statistics only. These keys are dropped
   from the single-session table and listed under `deferred_to_block_run`; the closed block run decides them:
   - `contrast/*/outcome`, `ceiling` and `floor_gate_j`;
   - `dominance/branch`;
   - `cross_session/*`;
   - the scaled line's outcome.
6. **"Floor from block 5":** the registered block-5 floor stands in for the scaled-allowance line, labelled
   "registered block-5 floor stands in (lead decision 6)".

## Coverage against §9 to §11

| Section | Covered | Not covered |
|---|---|---|
| §9.1 estimator 1 | mean, V, h, B (three kinds), interval, per token, attribution floor | |
| §9.2 estimator 2 | point, corner-widened, operative, guarded and drift-widened floors; gate | |
| §9.3 estimator 3 | 4 R and R_cm per floor session; branch per GAMMA pairing | |
| §9.4 estimator 4 | all of items 1 to 8 | |
| §9.5 item 1 | load-correlated restore line | |
| §9.5 item 2 | battery-assist line (from harvest flag rows) | |
| §9.5 item 3 | scaled allowance on cells, floors and contrasts | |
| §9.5 item 4 | single-step reconstruction (floor cells) | GAMMA (not printed by block 5's line) |
| §9.5 item 5 | | whole-machine per phase: S-15 is open, so it is recorded as not computed |
| §9.5 item 6 | cross-session consistency per GAMMA session and pairing | |
| §9.5 item 7 | | block-5 codes carried: needs block 5's code list beside block 6's catalog (structure only) |
| §9.5 item 8 | waited-runs line | |
| §8.3 item 3 alternatives | | contention E_add and P* lines (owed with S-14 / S-9 by the driver; no registered E_add code here) |
| §10 | n, mean, SD; with and without block 5; flagged-inclusive version | whole-machine quantities (S-15) |
| §11.1 | Δ and per-session differences | |
| §11.2 | replication word, short sentence, inclusive words beside | |
| §11.3 | (claim ceilings come from §9.4) | |
| §11.4 | eligibility (i)/(ii), added sessions listed, summary with them | |
| §12.3 item 4 | comparator under S-13; ratified precision; release mode requires a closed block run | |

## Tests

Command (Python 3.13 linked at `/opt/homebrew/bin/python3.13`; zsh not needed):

```
JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp /opt/homebrew/bin/python3.13 -m unittest \
  tests.independent_recompute tests.test_shard_tests tests.test_battery_float_sweep
```

| Run | Result |
|---|---|
| `tests.independent_recompute.test_block6` (new, 26 tests after the lead decisions) | OK, 23.9 s |
| `tests.independent_recompute` + `tests.test_shard_tests` (all 140) | OK (skipped=18), 110.9 s |
| `tests.test_battery_float_sweep` | OK after classifying the new reader of `b_fiducial_s` (one row) |
| `tests.test_docs_freshness`, `tests.test_custody_mode_inventory`, `tests.test_battery_float_consumers` | OK (56 tests, skipped=1) |

**The synthetic block** (`tests/independent_recompute/support_b6.py`) has nine sessions in the rotation of §6.1:
A1 B1 G1, B2 G2 A2, G3 A3 B3.

- A2 fails its drift screen (D1), so it does not count and enters the flagged-inclusive line.
- A1 has the following exclusions and flags:
  - a thermal-excluded repeat, which the load line restores;
  - a removed quad;
  - a battery-assisted repeat;
  - a waited repeat.
- G1 has a thermal-excluded quad run.
- Every session's powers differ.
- Each trace is idle around a constant-power request, so every phase energy is closed-form.

**What the tests show:**

- Counting comes from the acceptance and loop records. A disagreement stops the comparison, and a `reharvested`
  correction in the loop state is honoured.
- The pairings are G1 → A1/B1, G2 → A3 (rule 2)/B2 and G3 → A3/B3, and the floor gate is the paired maximum.
- Pairing rules 1, 2 and 3 and the block-5 fallback hold.
- b_op uses 10.818 ms.
- Kept units come from the acceptance exclusions, and the load, battery and waited lines move the expected units.
- Every run phase energy of all nine sessions (more than 2,700 rows) matches the closed form within 1 mJ. A reported
  mean and a dbar match their closed forms within half a unit at 4 decimals.
- A clean rerun compares with 0 observed difference in every class.
- **Bar semantics:** moving every value by 0.9 of its bar passes, and by 1.2 of its bar fails the run-energy and
  reported classes.
- These comparator cases fail:
  - an outcome-word change;
  - a missing key (unmatched);
  - a key with no print precision.
- `single` on A1 equals the block run's A1 in every key. `single` on G2 computes dbar without a floor gate.
- **A 1 ms decode-onset shift** fails exactly that run's decode energy, at more than 10 mJ, and raises
  `stored_energy_mismatch`.
- **A dropped plist record** fails the run-energy class and raises `trace_csv_plist_mismatch`.
- Public outputs pass the structure guard, and the guard refuses a float, an outcome word and a decimal token.
- **Lead decisions:**
  - Release mode fails on an unclosed run and passes on a closed one, with G2's rule-2 pairing final.
  - The idle-subtracted family is gross minus the telemetry idle power times the request span.
  - The key contract equals the published file, and each session's keys equal its pack's set.
  - Same-day single GAMMA equals the block run on its non-deferred keys.
- The synthetic-only guard exits 4 and writes nothing.
- With fewer than 6 clean corpus runs the screen is `undefined` and the session cannot be computed. A lost midpoint
  leaves the screen defined, with no midpoint.

## OPEN ISSUES

1. **Not yet run on archives written by the real harvest and acceptance code.** The fixtures are built by hand in the
   record format read at `f31aca19f`. The first contact with production-shaped archives should be the blind dry run's
   automation, or a full-size synthetic chain if one is built for §13. A field-name drift shows up as structure flags
   (`acceptance_*`, `archive_file_missing`), never as silently wrong numbers.
2. **Capture values are the stored `b_fiducial_s`, not a refit.** This is the same input judgment as the block-5
   script. b_op is cross-checked against the acceptance record's `operative_bound_s`.
3. **Not computed:**
   - §9.5 item 5, whole machine (S-15 open);
   - §9.5 item 7, block-5 codes carried;
   - the §8.3 item 3 contention and P* alternatives (S-14 and S-9 obligations).
4. **Single-step reconstruction** needs five idle records before onset. The fixtures do not have them, so it is
   exercised as not computed only. The block-5 tests cover its arithmetic.
5. **The repeated timing-bound sensitivity line** of the block-5 script (`--sensitivity`, ledger B_max) is not
   carried to block 6. Block 6's registration does not list it among §9.5's lines.
6. **One file outside the recompute directories** was edited: `tests/test_battery_float_sweep.py` gains one
   classification row for the new reader of `b_fiducial_s`. That sweep fails on any unclassified reader.
7. **Block-5 values enter only through `--block5`** (a block-5 recompute output). Until block 5's release, §10's n
   excludes block 5 and §11.2 prints no word ("block5_absent").

## NEEDS_RULING

None open. Items 1 to 6 of milestone 1 are decided; see LEAD DECISIONS. Ed may override decision 1 before the
release.

## SUMMARY

- **What exists.** `scripts/independent_recompute_b6.py`, the independent block-6 recompute (`block`, `single`), the
  S-13 comparator (`compare`, with `--release`) and the key-contract writer (`keys`).
- **Basis and sources.**
  - Arithmetic: the existing independent block-5 script's raw-record arithmetic and estimators, applied per counting
    session, with block 6's rules from the registration text.
  - Counting: the loop's acceptance and attempt records.
  - Pairing: §6.2, by registered round.
- **Coverage.** §9.1 to §9.4 in full, five of §9.5's lines, §10, §11.1, §11.2 and §11.4.
- **Lead decisions.** All six are applied:
  - the comparison precision is ratified;
  - the key contract is published at `configs/b6/recompute/comparison_keys.json`;
  - the idle family uses block 5's source;
  - the release comparison needs a closed block run;
  - same-day GAMMA defers its floor-dependent keys;
  - a block-5 floor stands in for the scaled line, labelled.
- **Synthetic result.** 26 tests on a nine-session synthetic block pass:
  - clean data agrees within the bars;
  - a 1 ms edge shift and a dropped record are each caught;
  - public outputs carry structure only.
- **Not built:** whole-machine (S-15) and the block-5-codes line.
- **Next:** the driver emits the published keys; the first contact with real archives is through blind automation.
