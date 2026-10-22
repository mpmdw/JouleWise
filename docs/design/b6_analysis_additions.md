# Block-6 analysis additions: design and build brief (item B6-1)

**Status: design, written blind, 2026-10-21.** Author: Opus 5.5 (interactive session 2dc9c377, workflow item B6-1).
Claim-path. It designs the code that registration B6-REPL §13 requires
(`docs/registrations/block6_replication_DRAFT.md`, written "the registration" or "REG" below), maps every clause of
REG §9.5 to §11.4 and §13 to a function (§13 of this file), and ends with the Sol build brief (§17).

**Which text wins.** The registration, then the rulings it cites (cold gates of 2026-10-17, the threshold and silly-numbers
rulings, block 5's B5-REG and B5-PLAN where REG says "unchanged"), then this design. Where this file and the registration
differ, the registration governs and this file is wrong.

**Blind.** The author opened no block-5 or block-6 archive, export, withheld file, restricted custody or harvest
record. Read: the registration on main `ef520743c`; B5-PLAN §2.4, §3, §8.1, §8.2; B5-REG §0.12 and §9.2; the block-6
code at `lane/2026-10-17-b6-packs-registered` `1706257c4` (`joulewise/b6/acceptance.py`, `session.py`, `queue.py`,
`loop.py`, `export_runs.py`, `session_paths.py`, `survivor_screen.py`, `analysis_lane.py`, `lanes.py`, the pack files,
`configs/b6/registration/README.md`, `scripts/harvest_b6_session.py`); lane L9 at
`lane/2026-10-20-l9-ruling-build` `1ab888a68` (`joulewise/b5_analysis/*.py`, the step programs' window-index
bindings, `joulewise/external/km003c_parse.py`, `joulewise/analysis_engine/inputs.py`,
`joulewise/paper_reported_energy_issuer.py`); the independent recompute at
`lane/2026-10-14-independent-recompute` `76f45da3e` (its meter functions only); RUN_STATE items 53, 59 and 65, and
the record of activation c634f6f3 (item 53), which carry structure only (counting, rounds, flag codes).

---

## 0. What this file decides (summary)

1. **L9 cannot open a block-6 archive today**, for reasons that are about block 5's bindings, not about block 6's
   numbers. L9 hard-binds block 5's seal pins, pack ids, flag catalog, harvest pins and the rule "the analysed
   attempt is the first claim-usable one". Item 53 is one face of this: r2-gamma would be refused at four places
   (§4.4). The additions therefore start with a **binding seam**: one value, `AnalysisBlock`, collects every
   block-5 binding, with block 5's as the default, and block 6 supplies its own (§4).
2. **Counting comes from the loop and the session's acceptance, never from `claim_usable`** (§4.5, §12). The kept
   units are recomputed with the sealed exclusion function under the block-6 rule (no GAMMA midpoint reason,
   REG §8.2), then the desk graphics exclusion of REG §8.3 item 3 is applied; a session whose target stratum then
   falls below 5 kept units stops counting before pairing is computed.
3. **Units of analysis**: one *floor unit* per counting ALPHA or BETA session, and one *GAMMA unit* per counting GAMMA
   session, which is an L9 chain over (that GAMMA session, its paired ALPHA, its paired BETA) (§4.3, §5).
4. **Two dry-run phases**: per-session steps run blind now; the cross-block steps (REG §10, §11) read block 5's
   released outputs, so they run only after block 5's release event. The dry run that satisfies REG §12.3 item 3 is
   the one that includes them (§14).
5. **S-15 cannot be filled by pointing at a block-5 analysis commit**: L9 defines only the request-level
   whole-machine cross-check (B5-PLAN §8.2). The per-phase definition exists only in the independent recompute. §8
   gives the definition, and §15 says how the lead fills the slot.
6. **Battery assist** (the MagSafe question in RUN_STATE item 65): the problem was real and was ruled on
   2026-10-06. The rail numbers are unaffected. The whole-machine line was the remaining gap. §7 closes it.

---

## 1. Terms used below

- **Session**: one block-6 collection of one pack (REG §1.6), with a loop session id of the form `r<round>-<pack>`,
  sometimes with a suffix (`-a<n>`, `-n<m>`; `joulewise/b6/loop.py` `_layout`, `_fresh_id`).
- **Archive**: `/Users/edr/night-b6/sessions/<session id>/archive`, the harvest's output (REG §14 S-2). It holds the
  block-5 harvest's files (`harvest.json`, `derived/exclusions.json`, `derived/flags.jsonl`, `derived/roster.json`,
  `derived/window_flags.json`, `derived/neg8-allowance.json`, `withheld/…`, `sources/…`) plus the block-6 files
  `derived/b6-acceptance.json`, `derived/b6-flags.jsonl` and `withheld/b6-neg8.json`.
- **Loop record**: `/Users/edr/night-b6/loop/attempts.jsonl` (one line per attempt: `session_id`, `round`, `packs`,
  `t0`, `outcomes`, `line`) and `state.json` (its `reharvested` corrections). `joulewise.b6.queue.counting_ids`
  reads both.
- **Acceptance record**: `derived/b6-acceptance.json`, schema `joulewise.b6_acceptance.v1`, with `counting`,
  `verdict`, `excluding`, `cells` (kept units per cell), `calibration` (b_op), `neg8`.
- **Block-5 exclusions document**: `derived/exclusions.json`, written by the block-5 harvest code that the block-6
  harvest runs. Its `claim_usable` and `reasons` carry block 5's meaning (item 53).
- **Block-6 exclusions document**: the same function's output under the block-6 rule (§4.5), written by the
  analysis into restricted custody. It is never written into an archive.
- **Desk exclusion**: an exclusion the registration assigns to the desk instead of the harvest. There is one, the
  graphics and neural-engine line P* (REG §8.3 item 3, S-9).
- **Analysis counting**: the loop's counting, confirmed by the acceptance record and re-tested for REG §8.2 N3 after
  the desk exclusion (§4.6).
- **Floor unit, GAMMA unit**: §4.3.
- **Structure**: what REG §12.1 releases during the block (verdicts, counting, flag counts by code and family, kept
  unit counts, the drift screen's verdict word, hazard measurements, timing that is not a phase duration).

---

## 2. The forcing problem

REG §13 says the programs are L9 at its release tag "plus the block-6 additions (pairing, between-session summary,
side-by-side table, replication word, flagged-inclusive line)". Reading L9 against a block-6 archive shows more than
those five additions are needed:

| L9 place (at `1ab888a68`) | What it requires | What a block-6 archive has |
|---|---|---|
| `b5_analysis/windows.py` `SealPins.load()`, `governing_pin`, `sealed_pack_table` | block 5's harvest pins (pin1 to pin4), pack ids from `sizing_b5.json`, plan ids `v5-b5-<pack>-a<n>-…` | harvest from the measurement checkout at `f31aca19f`; session ids `r<k>-<pack>` |
| `windows.select_analysed_attempts` → `flags.exclusions.first_claim_usable` | the first claim-usable attempt per pack, all three packs | up to three counting sessions per pack; selection by counting and pairing |
| `archive.open_attempt_record`, `open_archive` | `claim_usable` true; block 5's catalog digest; block 5's record shapes | r2-gamma: `claim_usable` false (`neg8.midpoint_lost_primary`); block-6 catalog `b5bce6c6…` |
| `kept_units.load_kept_units` | `claim_usable` true, `reasons == []`, catalog = block 5's | as above |
| `analysis_engine/inputs.py` `require_contrast_attempt_keeps_midpoint` | GAMMA carries no `neg8.midpoint_lost` | REG §8.2: on GAMMA a lost midpoint is disclosed, not removing |
| `bracket.evaluate_window_bracket` | block 5's acceptance (s_bracket 14.531 ms) | block 6's acceptance (s_bracket 10.818 ms, REG §3.3) |
| `bracket.block_b_max_for_archives`, `dry_run` steps 4, 10, 11 | exactly one archive per pack | floor sessions that serve no GAMMA session (ALPHA r4) |
| `disclosures._machine_lines` | request-level ΔE and ρ only | REG §9.5 item 5 asks for per-phase energy (S-15) |
| `joulewise/b6/analysis_lane.py` | "No registered-estimator precision entry point exists in stage 1" | correct and stays so: REG §5.3 says no precision stopping applies to the replication packs |

So the additions are: the binding seam (§4.2); the block-6 binding (§4.4 to §4.8); the units and pairing (§4.3, §5);
the new labelled lines (§6); whole-machine per phase (§8); the cross-block outputs (§9, §10); the release comparison
(§11); the structure-only record (§14).

---

## 3. Module layout

New, in L9's package (the seam; §4.2):

- `joulewise/b5_analysis/block.py`: `AnalysisBlock` (a frozen dataclass), `BLOCK5` (built from exactly the
  constants L9 uses today) and `block_for_index(path) -> AnalysisBlock` (reads the index file's `schema` field only).

New package `joulewise/b6_analysis/`:

| Module | Contents |
|---|---|
| `sessions.py` | read the loop record and each acceptance record; `counting_sessions()`; `desk_exclusions()` (P*); `analysis_counting()`; `pair()` (REG §6.2) |
| `binding.py` | `BLOCK6`: the session index writer, `configs/analysis/b6/seal_pins.json` reader, block-6 record shapes, the block-6 exclusions document (§4.5), the allowance (§4.7), the b_op check (§4.8), the usable predicate |
| `driver.py` | unit construction, the step lists of floor and GAMMA units, invocation of L9's programs, the structure-only record (§14) |
| `lines.py` | REG §9.5 items 3, 7, 8, the battery-assist value of the whole-machine line, the outside-processor labelled alternative (§8.5), the P* exclusion's record |
| `machine.py` | whole-machine energy per phase (REG §9.5 item 5, S-15; §8 here) |
| `crossblock.py` | between-session summary (§10), side-by-side table and Δ (§11.1), replication word (§11.2), sentence templates (§11.3), flagged-inclusive line (§11.4) |
| `compare.py` | REG §12.3 item 4: the analysis against the independent recompute |

New script `scripts/b6_analyze.py`: `--mode blind-dry-run|release --loop-root <dir> --sessions-root <dir>
--custody <dir> [--block5-release-record <file>]`. Exit 0, 3 (a registered outcome) or 2, as
`scripts/run_b5_analysis.py`.

New configuration under `configs/analysis/b6/`:

- `seal_pins.json`: the block-6 bindings by digest: the S-1 commit `f31aca19f` as the only harvest pin; the
  registration file, catalog (`b5bce6c6…`, S-3), acceptance (`ea130c87…`, S-4), identity pins (`513d7d4a…`, S-18)
  and the three pack files.
- `registered_constants.json`: F_min = 1.9 J (S-10), w = 5.432 J per CPU-s and c_q = 0.54 CPU-s per 10 s interval
  (S-8; 0.72 as measured, printed beside), d = +0.180 J (S-6), and T_phase per pack, model and phase (S-11, written by
  the lead from each pack's smoke, null until then). Each value carries its REG section.
- `dry_run_refusal_classes.json`: tooling and outcome classes for the block-6 steps (L9's file is the model).
- `printed_precision.json`: decimals per quantity kind (§11).

Untouched: `joulewise/b6/analysis_lane.py` (§2, last row); every `joulewise/b5/*.py` file in
`configs/campaigns/v5_claim_25g83/sealed_inventory.json`; `configs/b6/flag_catalog_b6.json` (pinned, S-3); the
measurement checkout.

---

## 4. How L9's steps run on block-6 sessions

### 4.1 One session's inputs (layout S-2)

For session `s`, the analysis reads, and only by automation into restricted custody:

| Input | Path | Used for |
|---|---|---|
| Plan | `sessions/s/custody/night_plan.json` | the session's runs, custody and archive roots |
| Archive | `sessions/s/archive/` | everything L9 reads, plus the block-6 records above |
| Claim runs | the plan's claim runs root under `sessions/s/runs-parent/` | strict validation and re-reduction of every kept bundle (L9 steps 1, 2) |
| Capture list | `<measurement checkout>/runs/calibration_observation_ledger.jsonl` (S-2) | L9's ledger-prefix check |
| Loop record | `/Users/edr/night-b6/loop/attempts.jsonl`, `state.json` | round, t0, counting |

Never read: the export directory (`sessions/s/export`). Its per-run table carries the hidden-offset factors
(`joulewise/b6/export_runs.py`, pack files `"blinding": {"hidden_offset": true}`), and the analysis computes from the
bundles. So REG §12.1's "divided out before any number is printed" is satisfied by never reading the export. A test
asserts that no `b6_analysis` module opens a path under `export`.

### 4.2 The binding seam

`AnalysisBlock` carries every value L9 now binds to block 5:

| Field | Block 5 (`BLOCK5`) | Block 6 (`BLOCK6`) |
|---|---|---|
| `index_schema` | `joulewise.b5_window_index.v1` | `joulewise.b6_session_index.v1` |
| `seal_pins` | `configs/analysis/b5/seal_pins.json` | `configs/analysis/b6/seal_pins.json` |
| `pack_table` | `sealed_pack_table` (sizing_b5, `v5-b5-<pack>-a<n>-`) | the three block-6 pack files, session id grammar `r<k>-<pack>[-a<n>][-n<m>]` |
| `governing_pin(entry)` | pin1 to pin4 by seal and t0 | `f31aca19f` for every session (S-1) |
| `record_shapes` | per pin, as L9 has them | the shapes the harvest at `f31aca19f` writes (taken from a fixture produced by that code, §16) |
| `catalog` | `configs/campaigns/v5_claim_25g83/flag_catalog.json` | `configs/b6/flag_catalog_b6.json` |
| `select(index, records)` | first claim-usable attempt per pack | the index names one session per pack in the unit; each must have analysis counting true |
| `usable(record)` | `claim_usable` true, `reasons == []` | analysis counting true (§4.6) |
| `kept_units(archive)` | `derived/exclusions.json` | the block-6 exclusions document from restricted custody, by digest (§4.5) |
| `allowance(archive, family)` | `whole_window.harvest_neg8_allowance_bracket` | REG §1.8 from `withheld/b6-neg8.json` (§4.7) |
| `window_bracket(archive)` | `bracket.evaluate_window_bracket` (block 5's acceptance) | block 6's acceptance, checked against the acceptance record (§4.8) |
| `gamma_midpoint_refuses` | true (B5-PLAN §2.4) | false (REG §8.2) |
| `verdict_row_answers` | as L9 (`dry_run._step_results`) | block 5's session-removing conditions and `neg8_bracket_*` answered as disclosed (§4.9) |
| `refusal_classes` | `configs/analysis/b5/dry_run_refusal_classes.json` | `configs/analysis/b6/dry_run_refusal_classes.json` |
| `custody_open` | true (D-173 opens in steps 9b and 10) | false (§18 D9) |
| `results_fill` | true | false (§18 D9) |

**Binding sites.** Every call that reads one of these values goes through the block of the index it was given. The
sites at L9 `1ab888a68` (a grep for `SealPins.load(`, `sealed_pack_table(`, `CATALOG_PATH`, `v5_claim_25g83`,
`configs/analysis/b5`, `first_claim_usable`, `select_analysed_attempts(`, `governing_pin(` outside `joulewise/b5/`,
plus the midpoint check and the bracket evaluator) are, with counts:

`joulewise/b5_analysis/windows.py` (14), `archive.py` (1), `kept_units.py` (2), `context.py` (2), `disclosures.py`
(3), `dry_run.py` (5), `bracket.py` (`evaluate_window_bracket`, `block_b_max_for_archives`),
`joulewise/analysis_engine/inputs.py` (2, and `require_contrast_attempt_keeps_midpoint`),
`joulewise/paper_reported_energy_issuer.py` (3), `scripts/extract_detection_floors.py` (3),
`scripts/mint_floor_artifact_generalized.py` (3), `scripts/build_results_fill_input.py` (2),
`scripts/produce_b5_disclosures.py` (2).

Not bound, because block 6 does not run them: `joulewise/paper_custody.py`, `scripts/run_b5_analysis.py`,
`scripts/rehearse_b5_real.py`, `scripts/size_b5_window.py`, `scripts/write_b5_identity_pins.py`,
`scripts/digest_pin_census.py`, `scripts/collect_window_flags.py`, `joulewise/flags/*`.

**Two checks keep the seam honest.**

1. *Binding census* (a test): after the seam, the grep above finds the block-5 constants only in `block.py`.
2. *Equivalence replay* (a test, exact): L9's own production-shaped synthetic block-5 chain (the S10 fixture,
   `tests/b5_analysis/fixtures_s10.py`) runs at L9's release tag and at the analysis commit. Every output digest
   in the two dry-run records is equal. Bit identity is the property here, because the inputs are identical and the
   seam only moves constants. This is what "L9 at its release tag" means once the seam exists.

Block 5's own dry run and release run from L9's release tag, never from the block-6 analysis commit (§18 D2). Its
`release_difference` check compares analysis commits, so mixing the two would refuse block 5's release.

### 4.3 Units

- **Floor unit**: one counting ALPHA or BETA session. Steps: L9 `0`, `1`, `2`, `3`, `3b`, `4` (that pack only),
  `10` (issue only, no custody open), then the block-6 floor lines (§6). L9's `RunState` assumes three packs in
  `prepare_brackets` (`block_b_max_for_archives`) and in steps 4, 10 and 11, so the floor unit uses a subclass in
  `driver.py` that overrides exactly those, with no change to L9's step functions.
- **GAMMA unit**: one counting GAMMA session `g` with its pairing (§5). It runs L9's step functions unchanged over the
  index {g, A(g), B(g)}: `0`, `1`, `2`, `3`, `3b`, `4`, `5`, `8`, `6`, `9`, `10` (issue only), `11` (disclosures only;
  no results-fill input). Steps 9b and the custody open of step 10 are not run (§18 D9).
- **Equalities between units (exact).** A floor session that appears in a GAMMA unit produces, in that unit, step-4
  and step-10 outputs byte-identical to its floor unit's. Each floor session's four dominance ratios R per model
  (REG §9.3) come from its floor unit, through `joulewise.dominance_closeout.dominance_ratio` on the extraction
  report's corner-widened and point unguarded floors; in each GAMMA unit, the close-out's R for that session equals
  them. Identical code on identical inputs, so bit identity is the property.

Order: floor units first, then GAMMA units, then the cross-block step (§14).

### 4.4 The session index (block 6)

`binding.write_index(unit)` writes one `joulewise.b6_session_index.v1` file per unit into restricted custody (not
into the repository). Its entries use L9's `IndexEntry` fields: `pack`, `pack_id`, `attempt` (1; see below),
`plan_id` (= session id), `t0_epoch_s` (from the loop record), `seal` (`"b6"`), `entry_kind`
`"harvested"`, `archive_root`, `harvest_record_sha256`, the four roots (from the plan), `harvest_pin` (`f31aca19f`),
`verdict` (from `harvest.json`), `claim_usable` (**analysis counting**, not the harvest's field), `cause_key` null.
L9's `_complete_history` requires attempts 1..n without gaps: the index lists only the unit's sessions, each as
attempt 1 of its pack, so the history check is trivially met, and the pack's full attempt history is printed from
the loop record (§6, B5-PLAN §8.1 history line).

Item 53 would have stopped r2-gamma at four places, all now behind the binding: `select_analysed_attempts`
(`first_claim_usable`), `open_archive` (`attempt_not_claim_usable`), `load_kept_units` (`exclusions_schema_invalid`)
and `require_contrast_attempt_keeps_midpoint` (`analysed_attempt_carries_midpoint_lost`).

### 4.5 Kept units: the block-6 exclusions document (the item-53 fix)

*Forcing problem.* The block-5 harvest code wrote `derived/exclusions.json` with GAMMA's pack-scoped midpoint reason
(B5-PLAN §2.4, Q11). REG §8.2 drops that reason on GAMMA. The acceptance applied the block-6 rule
(`compute(..., pack_scoped=False)` in `joulewise/b6/acceptance.py`), and the loop counted r2-gamma; the archive's
document still says `claim_usable: false`.

*Rule.* `binding.b6_exclusions(archive)`:

1. Build the acceptance's inputs exactly as `joulewise.b6.session.accept_archive` does
   (`acceptance.evidence_from_archive`, `archive.ordered_roster`, the internal flags and spans), and add the flags in
   `derived/b6-flags.jsonl`.
2. Call the sealed `joulewise.flags.exclusions.compute(flags, roster, spans, b6_catalog)` with the roster's
   `pack_id` key removed. With no pack id, `PACK_SCOPED_WINDOW_REASONS` adds nothing, which is REG §8.2's rule. This
   needs no keyword that the frozen file lacks, so the analysis runs whichever version of `exclusions.py` the base
   carries (§15 step 3).
3. Apply the desk exclusion (§4.6): each run it removes enters `compute` as one more member flag through an
   in-memory overlay of the catalog with one added entry, `desk.graphics_pstar` (effect EXCLUDE_MEMBER, family
   PHYSICS_IN_SPAN). So the whole unit containing the run is removed, as REG §8.3 requires. The overlay's bytes and
   digest are written beside the document; the pinned catalog file is not changed (REG §8.1: the graphics line has
   no catalog code).
4. Checks before step 3 (all exact: integers, run-id sets and code sets):
   - `members_excluded` (run id and codes) equals the acceptance record's member entries of `excluding`, and every
     cell's kept count equals the acceptance record's `cells`. A difference is a tooling refusal
     (`b6_kept_units_differ_from_acceptance`): the acceptance is the registered judge, so the analysis may not keep
     a different set;
   - for a counting session, the document's `claim_usable` is true. A false value means a window reason the
     acceptance did not apply: tooling refusal;
   - `members_excluded` and every cell's `kept_units` against `derived/exclusions.json`. The pack-scoped reason only
     adds a window reason, so they should agree; the acceptance's own emitted member flags (for example
     `member.bytes_ambiguous`) can legitimately add to them, so a difference is a structure word in the record
     (`b5_exclusions_member_sets_differ`), not a refusal.
5. Write the document (schema `joulewise.exclusions.v1`, the sealed function's own output) to
   `restricted/b6/kept/<session>.json`; the index entry's kept-units binding names its digest.

The analysis never reads `claim_usable` or `reasons` from `derived/exclusions.json` (§12).

### 4.6 Counting, the desk exclusion, and analysis counting

*Counting (REG §4).* `sessions.counting_sessions(pack)` returns `joulewise.b6.queue.counting_ids(state, pack)` over
the loop record (it applies `reharvested` corrections). For each, the acceptance record must say `counting: true`
and `joulewise.session_structure`'s `counting_source` must be `b6_acceptance`; a disagreement is a tooling refusal
(`b6_counting_records_disagree`).

*The desk exclusion (REG §8.3 item 3, §8.5 graphics row, S-9, S-11).* For each run of a counting session, P_x is the
time-weighted mean of GPU plus ANE rail power over the run's idle baseline (the baseline records of its measured
stream). E_add = P_x × T_phase, with T_phase from `registered_constants.json` for (pack, model, phase), the model being
the run's own (§18 D11). The run is excluded when E_add ≥ F_min / 4 = 0.475 J, that is, when P_x ≥ P* = 0.475 J /
T_phase. *Worked example (synthetic):* T_phase = 6.0 s, so P* = 0.0792 W. A run with P_x = 0.15 W has E_add = 0.90 J:
excluded. A run with P_x = 0.0002 W (the quiet rails read about 0.2 mW, REG §8.5) has E_add = 0.0012 J: kept. While
S-11 is null, this step records `pstar_unsized` in the structure record and the release-gating dry run cannot
complete (REG §14 S-9: due before the blind dry run).

*Analysis counting.* A counting session stays counting unless, after the desk exclusion, a target cell's stratum
keeps fewer than 5 units (REG §8.2 N3). Then it stops counting, its structure record says
`analysis_counting: false, cause: cell.below_minimum (desk)`, and pairing (§5) is computed on analysis counting.
Pairing then depends on an idle-baseline power, a hazard measurement, never on a science energy (REG §6.2). On the
77 rehearsal runs the line removes 0 runs (REG §8.3 item 3), so no change of counting is expected; the code path
still has a fixture (§16).

### 4.7 The drift allowance (REG §1.8)

*Forcing problem.* L9's consumers read the allowance through `whole_window.harvest_neg8_allowance_bracket`, from the
block-5 harvest's NEG-8 record. Block 6's registered allowance is REG §1.8 (clean corpus of 6 or more, survivors
under the block-6 catalog, the midpoint's two-value fallback). The b6 survivor screen
(`joulewise/b6/survivor_screen.py`) records its inputs in `withheld/b6-neg8.json`: per family, the start, midpoint
and end means and the bound terms, but not the allowance itself.

*Rule.* `binding.allowance(archive, family)` = max(spread, bound_j), where bound_j is the screen's recorded
`bound_terms.bound_j` for that family and spread is the largest minus the smallest of the start mean, the midpoint mean
and the end mean, or |end mean − start mean| when the midpoint is lost (REG §1.8). Each run carries half of it, as in
block 5. Consumers take the family they take for block 5 (the allowance wire is per family).

*Check.* When the block-5 harvest's NEG-8 record is defined and its corpus and reference run-id sets equal the b6
screen's (`corpus_run_ids`, `reference_run_ids`), both allowances come from the same functions on the same energies,
so they must be equal (exact, float hex). When the sets differ, the b6 value governs and the structure record says
`allowance_sources_differ` (a structure word, no number). An undefined b6 screen is REG §8.2 N2: the session does not
count, and the acceptance already says so.

### 4.9 The stored whole-window verdict row and the harvest commit

L9's consumers read the whole-window verdict row the harvest stored (`analysis_engine.inputs.archived_verdict_row`,
`whole_window.validate_whole_window_verdict_row`) and admit it only when every condition it carries is answered
(`dry_run._step_results`, `answered_by`). In block 6 the row's NEG-8 bracket decision and its `neg8_bracket_*`
conditions are disclosed only (REG §9.5 item 7: block 5's 0.05 J bar fails every session by construction), and block
5's other session-removing codes are flags (REG §8.2). So `BLOCK6` answers each such condition as `disclosed (REG
§8.2, §9.5 item 7)`, and the row is admitted on the block-6 conditions: the acceptance's verdict, the b6 screen and
the b_op check. The builder confirms on the fixtures which conditions the real harvest writes, and lists them.

The harvest commit each session's `harvest.json` names is the S-1 commit `f31aca19f` unless the session was
harvested again (REG §4: a harvest fault is fixed and re-run on the same bytes). A different commit is recorded in the
structure record with the loop's `reharvested` entry beside it; it is a flag, not a refusal (records are flags), and
the lead reads it.

### 4.8 The operative timing bound

b_op for a block-6 session is max(opening, closing) + max(|closing − opening|, 10.818 ms) (REG §1.7, §3.3), from the
session's own two captures. `binding.window_bracket(archive)` evaluates it with block 6's acceptance
(`configs/b6/registration/acceptance.json`) through the same function the acceptance used
(`joulewise.b6.calibration`). It must equal the acceptance record's `calibration` b_op (exact decimal string), and
L9's `require_member_bound_is_window_bracket` then requires each member's recorded operative bound to equal it, as
in block 5. A difference is a tooling refusal. *Worked example (synthetic, REG §1.7 with block 6's s_bracket):*
opening 40.0 ms, closing 30.0 ms: b_op = 40.0 + max(10.0, 10.818) = 50.818 ms.

---

## 5. GAMMA pairing (REG §6.2)

`sessions.pair(g, counting)` takes a counting GAMMA session `g` of round k and, for each floor pack P in (ALPHA, BETA),
the list of P's analysis-counting sessions with their rounds and t0. It returns (session, rule):

1. `same_round`: P's counting session of round k;
2. `later_round`: otherwise P's counting session of the smallest round greater than k;
3. `earlier_round`: otherwise P's counting session of the largest round smaller than k;
4. `block5`: otherwise block 5's analysed session of P, labelled "floor from block 5". This step reads block 5's
   floors, which exist only after block 5's release, so a pairing that needs it is computed in the cross-block phase
   (§14).

Ties (two counting sessions of P in one round, possible after a held pack is resumed): the earlier t0 (§18 D16).
Pairing reads only round, t0 and analysis counting. One floor session may serve several GAMMA sessions; every pairing
is printed with its rule. A GAMMA session's own counting does not depend on its pairing.

*Worked example 1 (structure as recorded, RUN_STATE item 59: counting only, no energy).* ALPHA counted in rounds 1, 3,
4; BETA in 1, 2, 3; GAMMA in 1, 2, 3. GAMMA r1 → ALPHA r1 (rule 1), BETA r1 (rule 1). GAMMA r2 → ALPHA r3 (rule 2: no
ALPHA counted in round 2; r2-alpha never ran, item 52), BETA r2 (rule 1). GAMMA r3 → ALPHA r3, BETA r3 (rule 1). ALPHA
r3 serves two GAMMA sessions. ALPHA r4 serves none: it is a floor unit only, and its cells, floors and R are printed.
So there are six floor units and three GAMMA units.

*Worked example 2 (synthetic, exercising rules 3 and 4).* As example 1, but BETA r3 does not count and BETA has no
later counting session: GAMMA r3 pairs with BETA r2 (rule 3), which then serves GAMMA r2 and r3. Had BETA no counting
block-6 session at all, every GAMMA session would pair with block 5's BETA session, and each contrast's outcome line
and the replication sentence would print "floor from block 5".

---

## 6. REG §9.5: disclosures and labelled lines

Each counting session prints B5-PLAN §8.1's disclosures with "session" for "window". L9's disclosure producer prints
them per unit. What changes for block 6, and the new lines:

| REG §9.5 | Where | Block-6 specifics |
|---|---|---|
| preamble: kept units and positions of removed units | L9 `disclosures._kept_lines` | from the block-6 exclusions document; desk-excluded units carry the label `desk.graphics_pstar` |
| preamble: attempt history | `lines.history()` | block 5's attempts (block 5's index, structure) and the pack's block-6 attempts from the loop record, with outcome status and cause |
| preamble: battery, thermal, contention, clock counts; reference drift with realised counts; monitor cost; fixed sentences | L9 `disclosures` | unchanged; the GAMMA midpoint sentence (L9 `MIDPOINT_SENTENCE`) is printed for a GAMMA session with `neg8.midpoint_lost` (REG §8.2), where block 5 refused |
| 1 load-correlated physics sensitivity | L9 `_energy_lines` | unchanged. `contention.request_overlap` removes nothing in block 6, so only the two thermal codes can trigger it |
| 2 battery-assist line | L9 `_energy_lines` (cells, contrasts) and `lines.machine_without_assist()` | unchanged for rail cells and contrasts; also applied to the whole-machine per-phase value (§7, §8) |
| 3 scaled drift allowance | `lines.scaled_allowance()` | new; below |
| 4 single-step reconstruction diagnostic | the independent recompute | not computed by the analysis (REG: "computed by the independent recompute"); `crossblock` places the recompute's value beside the cell, labelled |
| 5 whole-machine energy per phase | `machine.py` | new; §8; ALPHA and BETA only |
| 6 cross-session consistency | L9 `_energy_lines` (cross-window check) | runs per GAMMA unit, G against the paired floor session's F; the label "agree within the statistical half-widths; timing bounds B not included" |
| 7 block-5 codes carried | `lines.block5_codes()` | new; below |
| 8 waited runs | `lines.without_waited()` | new; below |
| REG §8.3 item 3, §8.5 "What is printed": outside-processor labelled alternative | `lines.outside_processor_alternative()` | new; below |

**Item 3, scaled drift allowance.** For a cell: factor = max(1, E / E_ref, T / T_ref). E is the cell's estimator-1
mean. T is the cell's mean phase length, by estimator 1's weights (0.2 × mean over kept repeats + 0.8 × mean over the
runs of kept quads). E_ref and T_ref are the plain means of the gross request energy and request length over the
surviving start, midpoint and end references that set the allowance (§18 D12). The line prints the allowance term
(half the allowance, as it enters B) times the factor, and B and the interval recomputed with it. For a contrast:
factor = max(1, E_a / E_ref, E_b / E_ref, T_a / T_ref, T_b / T_ref) on the allowance term of D, with E_a, E_b, T_a,
T_b the side means over kept quads. *Worked example (synthetic):* allowance term 0.40 J, E_ref = 37.2 J, T_ref =
4.1 s. A BETA prefill cell with E = 58.5 J, T = 0.95 s: factor max(1, 1.5726, 0.2317) = 1.5726, scaled term
0.629 J. A 1.7B decode cell with E = 25.5 J, T = 1.99 s: factor 1, unchanged. A contrast with E_a = 25.5 J, E_b =
85.0 J, T_a = 1.99 s, T_b = 6.6 s: factor max(1, 0.6855, 2.2849, 0.4854, 1.6098) = 2.2849, scaled term 0.914 J.
(REG §9.5 item 3's own example: 0.49 J × 8.108 = 3.97 J.)

**Item 7, block-5 codes carried.** For each block-6 session: the codes in its flags (`derived/flags.jsonl` and
`derived/b6-flags.jsonl`) whose effect in block 5's sealed catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`,
digest from `configs/analysis/b5/seal_pins.json`) is EXCLUDE_WINDOW, plus block 5's pack-scoped reasons
(`flags.exclusions.PACK_SCOPED_WINDOW_REASONS`: on GAMMA, `neg8.midpoint_lost` → `neg8.midpoint_lost_primary`),
minus the NEG-8 bracket decision and its `neg8_bracket_*` conditions (disclosed only, never listed as a carried
failure). Codes absent from block 5's catalog are listed separately as "not in block 5's catalog". Beside the list:
`harvest.json`'s `claim_usable` (structure; `session_structure` records it as `b5_harvest_claim_usable`). For
r2-gamma the line reads `neg8.midpoint_lost_primary` (the item-53 session, shown, not removed). A restricted code
(REG §12.1, D21) prints as "removed (restricted code)" in the blind record.

**Item 8, waited runs.** For each registered cell and contrast: the same estimator over the kept units with every unit
that contains an `idle.waited` run removed, printed as "without waited runs (n_r = …, n_b = …)" (contrast: "(n = …)"),
with the number of waited runs per stratum; below 5 units it carries "below the registered minimum of 5 units" and
decides nothing (the battery-assist line's form, B5-PLAN §8.1). d = +0.180 J (S-6) is below 0.475 J, so waited runs
stay in the registered value.

**Outside-processor labelled alternative (REG §8.3 item 3, §8.5).** For every cell and every contrast (a GAMMA
contrast is a cell of the exclusion function), and for every kept run: C = Σ of the monitor's
`outside_total` over the k accounting intervals that overlap its request (the quantity the harvest's contention join
reads, `joulewise.b5.harvest`), excess = C − k × 0.54, E_add = 5.432 × max(0, excess). The alternative removes each
run with E_add ≥ 0.475 J (and its unit), recomputes the estimator (for a contrast, REG §9.4 steps 1 to 3 only: dbar and its metrology interval, no Holm
test, no floor decision, no outcome, as the battery-assist contrast line), and prints "registered outside-processor rule (w =
5.432 J per CPU-s, c_q = 0.54 CPU-s; 0.72 as measured with Spotify and the orphaned test process)" with the count of
runs removed, and, for each removed or `contention.request_overlap`-flagged run, C, k, excess and E_add. It never
replaces the registered value. *Worked example (REG §8.5):* C = 1.54 CPU-s over k = 2 intervals: excess 0.46 CPU-s,
E_add = 2.499 J: removed by the alternative, kept and flagged in the registered value. C = 0.95 over k = 2: excess
below 0, E_add = 0. The background-priority line (w = 0.0862) is not printed (§18 D14).

---

## 7. Battery assist (the MagSafe question, RUN_STATE item 65)

*What happens.* Under heavy load the machine draws more than the 140 W adapter supplies and the battery makes up the
difference while the adapter stays connected. This was measured on 2026-10-06 (B5-REG §9.2): in a 170 s load of 8B
plus a CPU burner, the SMC battery current B0AC was nonzero in 126 of the run's 536 SMC publications, all of them
inside the load phase, about 63 s of the 170 s, lowest −5,331 mA.

*Was it a problem?* For the numbers the paper claims, no. They are processor-rail energies (CPU, GPU and ANE), and
the rails are regulated downstream of the supply, so the sampler reads the same rail energy whichever source delivers
it. Removing assisted runs would have been the real bias, because assist happens exactly when load is highest, so the
kept means would drop, most for 8B. The ruling of 2026-10-06 (two blind seats, then the orchestrator) therefore made
discharge a disclosure (`battery.assist`), kept charging and AC loss as exclusions, and printed every cell with and
without assisted runs. 8B decode ran at 69.1 to 72.6 tokens/s under up to −5.3 A of assist against 68.9 to 71.1
tokens/s without. Block 6 carries all of this (REG §8.3 item 1, §9.5 item 2).

*Where it was a problem: the whole-machine line.* The wall meter sits on the adapter's cable, so it cannot see energy
the battery supplies. Block 5's request-level cross-check adds the battery term (ΔE_machine = ΔE_meter + ΔE_battery,
B5-PLAN §8.2). Block 6's per-phase line (REG §9.5 item 5) is meter-only, because the battery current is read once a
second and no reading falls inside 38% of prefill phases. So in an assisted phase the per-phase whole-machine value
reads low by the battery's share. The registration flags such phases but defines no value free of the gap.

*What this design does.*

1. Assisted runs are those carrying `battery.assist` (the registered member rule: a negative SMC read held into the
   request, B5-PLAN §8.1). `meter.battery_activity` (a nonzero B0AC read in the meter stream inside the request) is
   counted beside it.
2. REG §9.5 item 2 applies to "each estimate", so the whole-machine per-phase value is printed twice, like every rail
   cell: over all kept units, and over the kept units with no assisted run, with the count of assisted runs per
   stratum (`lines.machine_without_assist()`). The second value is the one with no battery gap.
3. Each run's request-level ΔE_machine with the battery term (block 5's definition) is printed beside, with the
   count of runs whose battery term was unavailable.
4. The boundary sentence is printed as registered, followed by one sentence: "DC input at the USB-C port; the
   adapter's AC-to-DC loss is not included. Battery energy is not included in the per-phase value; phases whose
   request shows battery assist are counted and the value is also printed without them."
5. The ruling's reopening conditions (B5-REG §9.2: lower rail power, frequency or tokens per second in assisted
   against matched unassisted seconds; power-mode transitions with assist; a battery-temperature rise concentrated in
   assisted stages) are visible after the release in the battery-assist line (energy) and in the existing
   battery-temperature diagnostic. The analysis adds no new test for them.

How many block-6 runs carry `battery.assist` is structure (flag counts by code, REG §12.1); the blind dry run writes
it per session and cell (§14), so the lead can say how often assist happened without opening an energy.

---

## 8. Whole-machine energy per phase (REG §9.5 item 5, S-15)

*Finding.* REG §9.5 item 5 says the definition is "the one committed for block 5". L9 at `1ab888a68` commits only the
request-level cross-check of B5-PLAN §8.2 (`disclosures._machine_lines`, `km003c_parse.delta_machine_energy`), and
B5-PLAN §8.2 says "the harvest computes no phase-level figures". The per-phase line exists in the independent recompute
(`scripts/independent_recompute_b5.py` at `76f45da3e`: `machine_member`, `phase_machine_mean`, the edge-shift
corners), labelled "gross meter energy per phase; battery assist flagged at request level", which is item 37's 03:26
amendment. The analysis must implement the same definition independently, or REG §12.3 item 4 cannot pass on these
values.

*Definition* (`machine.py`; the proposed S-15 fill, §15):

1. **Timeline.** Meter samples (Vbus × Ibus, 50 per second) are placed on CLOCK_MONOTONIC_RAW by the stream's clock
   fit (`km003c_parse.clock_fit`, the lower-envelope line). A run's phase edges, stamped on its wall clock, are mapped
   to the same clock by the run's clock anchor (the midpoint of its wall-minus-monotonic bounds) plus the stream's
   raw-minus-monotonic offset (`km003c_parse.raw_offset_ns`; failing that, the hazard monitor's journal line nearest
   the phase, recorded as `meter_offset_from_journal`).
2. **Per-run value.** E_meter(phase) = mean power of the samples whose host time lies in [start, end) × (end −
   start), gross (`km003c_parse.integrate`). No sample in the phase, or no stream covering it: the run's value is
   absent and counted.
3. **Per cell.** Estimator 1's arithmetic over the kept units (REG §9.1 steps 1 to 3: m, V, h), per model and phase,
   ALPHA and BETA only. The rails' share is printed beside: the median over kept runs of gross rail energy ÷ gross
   meter energy for the same phase.
4. **Uncertainty from the timeline.** δ = b_op + r_max, where r_max is the largest height of any fit point above the
   fitted envelope (the meter's clock-fit residual). The cell mean is recomputed with every run's start edge moved by
   ±δ and end edge by ±δ, four corners, the same sign for all runs in a corner; the largest |change| of m is printed as
   "edge-shift sensitivity (b_op + clock-fit residual)". It is a sensitivity printed beside m ± h, not a term added to
   the interval.
5. **Battery.** §7 items 1 to 4.

*Worked example (synthetic).* A prefill phase of 0.620 s holds 31 meter samples with mean 68.0 W: E_meter = 42.16 J.
Its request holds an SMC read of B0AC = −1,200 mA at B0AV = 12,600 mV, 15.12 W supplied by the battery, so the run
carries `battery.assist`; its unit is left out of the "without assisted runs" value. With b_op = 45 ms and r_max =
6 ms, δ = 51 ms; if the four corners move m by +0.41, −0.38, +0.05 and −0.02 J, the line prints 0.41 J.

*Block 5's value for REG §10.* The between-session summary needs block 5's per-phase value too. `machine.py` computes
it from block 5's archives in the cross-block phase, after block 5's release, with the same function (§18 D13); the
recompute's block-5 value is its comparison partner.

---

## 9. Estimators 1 to 4 (REG §9.1 to §9.4): unchanged, run by L9 per unit (§4.3)

Estimators 1 to 4 are block 5's, one counting session at a time; no run, unit or cell is pooled across sessions
(REG §9). The kept-unit issuer must equal `paper_reported_energy._project_cell` exactly on a complete cell (REG §9): a
test runs both on a complete synthetic cell and compares float hex.

---

## 10. The between-session summary (REG §10)

`crossblock.summary(Q, pack)`: for each printed quantity Q and pack, the values Q_j of block 5's analysed session and
of every counting block-6 session (each computed by §9 within its session), n = 1 + (counting block-6 sessions),

    Q̄ = (1/n) Σ_j Q_j,        s_Q = √( Σ_j (Q_j − Q̄)² / (n − 1) ).

Printed as "between-session summary (n sessions): mean, standard deviation". Nothing else: no ratio to a half-width,
no pooled interval, no test, no claim. The quantities (REG §10): each reported mean and per-token value, attribution
floor, operative floor, dominance ratio, dbar and energy ratio, and each whole-machine per-phase value. A per-token
value is computed per session and then summarized. For R the "session" is the floor session; for dbar and the energy
ratio, the GAMMA session.

*Edge cases.* n = 1 (no counting block-6 session of the pack): Q̄ = Q_1 and s_Q prints "not defined (n = 1)". A
session whose Q is not computable (for example a refused cell): left out, n reduced, and the line names it. A block-5
value that its analysis did not compute: n counts block-6 sessions only and the line says "block 5: not computed".

*Worked example (synthetic).* BETA's prefill-p2048 reported mean: block 5 58.40 J; three counting block-6 sessions
58.71, 57.96 and 58.83 J. n = 4, Q̄ = 58.475 J, s_Q = 0.388 J. The per-token values (÷ 2,048) are 0.02851563,
0.02866699, 0.02830078 and 0.02872559 J; their summary is 0.02855225 J, standard deviation 0.00018955 J. GAMMA decode
dbar: block 5 +3.00 J; block 6 +2.84, +3.21, +2.95 J: n = 4, Q̄ = 3.000 J, s_Q = 0.155 J. A dominance ratio: 3.84, 3.51,
4.02, 3.77: Q̄ = 3.785, s_Q = 0.211.

---

## 11. Reporting rules (REG §11.1 to §11.4), written exactly

### 11.1 Side by side (`crossblock.side_by_side`)

For every quantity of REG §9 and each pack, one row per session: block 5's value, then each counting block-6
session's value, each with its interval (where the estimator has one), its kept units (n_r, n_b, or n) and its flags
(the session's flag codes with counts; restricted codes as such until the release). Then:

- Δ = (mean of the counting block-6 sessions' values) − (block 5's value);
- each block-6 session's own difference, Q_j − Q_block5;
- the between-session summary (§10);
- two fixed facts, printed with every table: "Block 6 makes record conditions flags; the rules for which runs and
  sessions enter differ between the blocks (REG §8)." and "Each block's own calibration acceptance sets its b_op:
  s_bracket 14.531 ms in block 5, 10.818 ms in block 6.";
- for each block-6 session, the item-7 line (§6).

*Same worked example:* block-6 mean 58.50 J, Δ = +0.10 J; own differences +0.31, −0.44, +0.43 J.

No Δ is printed when block 5's value is absent ("block 5: not computed") or no block-6 session counts ("no counting
block-6 session").

### 11.2 The replication word (`crossblock.replication_word`), per GAMMA contrast

Inputs: block 5's outcome word w5 and dbar5; for each counting block-6 GAMMA session j, w_j and dbar_j.

1. If w5 is `not_estimable` (no dbar): the word "replicated" is not used; print the sessions' words and signs.
2. Otherwise "replicated" when, for every counting block-6 GAMMA session j, w_j = w5 **and** sign(dbar_j) =
   sign(dbar5); else "not replicated", followed by each session's word and signed dbar.
3. A block-6 session whose contrast is `not_estimable` has no sign: it differs from any w5 other than `not_estimable`,
   so the contrast is "not replicated".
4. If GAMMA closed with fewer than 3 counting sessions, the sentence adds "short: k counting block-6 sessions of the
   3 targeted" (and, below 2, "below the commitment of 2"). With k = 0 there is no replication sentence, only that
   line.
5. A pairing with rule 4 (§5) adds "floor from block 5" to that session's outcome line and to the sentence.
6. The flagged-inclusive sessions' words and signs are printed beside, labelled, and never enter the word.

*Worked example (synthetic).* Block 5 `direction_supported`, +3.00 J. Block 6 `direction_supported` +2.84,
`direction_supported` +3.21, `direction_supported` +2.95: **replicated**. Had the third been `unresolved` with +0.95:
**not replicated** (sessions: supported +2.84, supported +3.21, unresolved +0.95), although every sign agrees.

### 11.3 What may be said (`crossblock.SENTENCES`)

Every printed sentence about block 6 comes from one closed table of templates:

- a reported cell is an L1 instrument result; its interval is printed and not tested;
- a contrast reaches L2 only by REG §9.4 within its own session (its own outcome and leave-one-out), never from the
  replication word or the summary;
- "replicated" and "not replicated" describe agreement of outcome words and signs, and no template places an
  interval, p-value, "significant" or "confirmed" next to them;
- every between-session statement uses the §10 summary and states n ("(n sessions)").

A test asserts that every string the analysis prints for block 6 matches a template, and that no template breaks the
four rules.

### 11.4 The flagged-inclusive line (`crossblock.flagged_inclusive`)

Added back: each non-counting block-6 session that (i) ran the registered experiment, meaning none of
`model.files_differ_from_registered`, `model.stack_differs_from_registered`, `code.number_bearing_unreviewed`,
`structure.*` (REG §8.2 W1, W2, W3, S1), and (ii) can be computed: every target stratum keeps at least 5 units under
the run exclusions, b_op is defined (no N1), and the drift screen is defined (no N2). The session-level conditions P1 to
P4 and D1 are ignored for it; run exclusions, including the desk exclusion, still apply. A non-counting GAMMA session
pairs by §5 with analysis-counting floor sessions only (§18 D17).

Printed beside every registered result (each §10 summary, each replication sentence) as "including sessions that did
not count (n = …)", listing each added session with its session-level codes. It never replaces the registered value.
With no session added it prints "including sessions that did not count: none". *Worked example (synthetic):* the BETA
example of §10 plus a session removed by its drift screen that read 59.10 J: n = 5, mean 58.600 J, standard deviation
0.437 J, labelled as such.

**Printed precision** (`configs/analysis/b6/printed_precision.json`; §18 D15): energies in joules to 5 decimals, as
L9's disclosure lines print cells; ratios (R, ρ, the energy ratio, the scaling factor) to 4 decimals; per-token
energies to 8 decimals (÷ 512 or ÷ 2,048 moves a value down about three decimal places); counts as integers. This fixes
REG §12.3 item 4's "half a unit of its last printed digit": 5 × 10⁻⁶ J, 5 × 10⁻⁵ and 5 × 10⁻⁹ J. *Derivation:* each
lies above 10⁶ times float noise (2.2 × 10⁻⁷ J at 1,000 J) and below 1% of the smallest printed half-width (about
10⁻⁴ J and up for these cells), the window the project's agreement rule sets. Block 5's renderer prints floors as exact
decimals; in the block-6 tables they print to 5 decimals, so the half-unit bar is not float noise.

---

## 12. `claim_usable`: every reader, and what it does on the block-6 line

Two different fields share the name. *Window-level*: a session (attempt) is usable for claims. *Cell-level*: a floor
cell of the aggregate floor artifact is claim-ready (`eligibility.claim_usable`). Item 53 concerns only the first.

| Reader | Which field | Block-6 behaviour |
|---|---|---|
| `joulewise/flags/exclusions.py` | window: `compute` writes `claim_usable = not window_reasons`; with the default `pack_scoped=True` a GAMMA `neg8.midpoint_lost` adds `neg8.midpoint_lost_primary`. `first_claim_usable` picks the first usable attempt | The harvest at `f31aca19f` writes `derived/exclusions.json` with block 5's meaning (item 53). The acceptance calls `compute(..., pack_scoped=False)`. The analysis calls `compute` with no pack id (same result, §4.5), never reads the file's `claim_usable` or `reasons`, never calls `first_claim_usable`. Not edited |
| `joulewise/session_structure.py` (block-6 line only) | window: reads `harvest.json` `claim_usable` only when `derived/b6-acceptance.json` is absent; otherwise counting comes from the acceptance; records `b5_harvest_claim_usable` | All nine counting sessions have an acceptance record, so `counting_source` is `b6_acceptance`. The analysis requires that (§4.6) and prints `b5_harvest_claim_usable` in item 7 (§6). Not edited |
| `joulewise/analysis_manifest_v3.py` (block-6 line, line 3498) | cell: finalization selects aggregate-floor cells whose `eligibility.claim_usable` is true | Unchanged meaning, per GAMMA unit, on the aggregate floor minted from the paired floor sessions. Not touched by item 53 |
| `joulewise/detection_floor.py` | cell: the validator requires `eligibility.claim_usable` boolean and equal to `status == claim_ready` | Unchanged, per floor cell |
| `joulewise/dominance_closeout.py` (block-6 line, line 1909) | cell: a floor cell resolves only if `eligibility.claim_usable` is true | Unchanged, per GAMMA unit |
| `scripts/harvest_b5_window.py` | window: prints `claim_usable` from the harvest record | Not on the block-6 path: block 6 harvests through `scripts/harvest_b6_session.py`, which prints `counting`. The analysis never runs it |
| `scripts/mint_floor_artifact.py` | cell: writes `claim_usable: true` (v1 mint) | Not used: L9 mints with the generalized mint |
| `scripts/mint_floor_artifact_generalized.py` | cell: writes `claim_usable: true` on claim-ready cells | Used per GAMMA unit (L9 step 5); cell-level |
| `scripts/render_results_fills.py` | cell: requires the mint cell `claim_ready` and `claim_usable` | Not run by the block-6 analysis (§18 D9); when block-6 tables are rendered later, cell-level only |
| L9 `windows.select_analysed_attempts`, `archive.open_attempt_record` and `open_archive`, `kept_units.load_kept_units`, `analysis_engine/inputs.require_contrast_attempt_keeps_midpoint` (not in the item's list, but where item 53 bites) | window | Behind the binding: selection by analysis counting, usable = analysis counting, kept units from §4.5, midpoint check off (§4.2, §4.4) |

On L9's branch, `analysis_manifest_v3.py` and `dominance_closeout.py` no longer carry the cell-level check at the lines
above (it moved with L9's changes); the base of §15 step 3 decides which version runs, and the meaning stays cell-level
either way.

**The r2-gamma check.** The task asked for a test on r2-gamma's real `exclusions.json`. That file names each excluded
run's codes, which REG §12.1 restricts, so no test file may hold it. Instead: (a) a synthetic fixture shaped like
r2-gamma (§16, session G2), and (b) in the blind dry run on the real sessions, r2-gamma's structure record must read
`b5_exclusions_claim_usable: false`, `b5_reasons: ["neg8.midpoint_lost_primary"]`, `b6_exclusions_claim_usable: true`,
`acceptance_counting: true`, `analysis_counting: true` and `analysed: true` (structure only). The lead reads those
six fields.

---

## 13. Clause map (REG §9.5 to §11.4, and §13)

| REG clause | Function | Test |
|---|---|---|
| §9 "per counting session", no pooling | `driver.units()` (§4.3) | e2e: each unit's index lists one session per pack |
| §9 kept-unit issuer equals `_project_cell` on a complete cell | L9 issuer, through `driver` | `test_issuer_equals_project_cell` (exact) |
| §9 GAMMA pack file's estimator-1 entry | corrected by the lead at the S-14 pin (§15 step 6) | — |
| §9.5 preamble (B5-PLAN §8.1 disclosures, "session" for "window") | L9 `disclosures` per unit; `lines.history()` | e2e: every unit has a disclosure record |
| §9.5 item 1 | L9 `_energy_lines` | fixture: a thermal-removed unit (§16) |
| §9.5 item 2 | L9 `_energy_lines`; `lines.machine_without_assist()` | fixture: assisted 8B prefill runs |
| §9.5 item 3 | `lines.scaled_allowance()` | worked example (§6) and fixture |
| §9.5 item 4 | the recompute; `crossblock` places it | `test_single_step_is_read_not_computed` |
| §9.5 item 5 | `machine.phase_energy()`, `machine.cell()` | worked example (§8), fixture meter streams |
| §9.5 item 6 | L9 cross-window check per GAMMA unit | fixture: one pairing that agrees, one that does not |
| §9.5 item 7 | `lines.block5_codes()` | fixture G2 lists `neg8.midpoint_lost_primary` |
| §9.5 item 8 | `lines.without_waited()` | fixture: waited runs |
| §8.2 GAMMA midpoint disclosed, fixed sentence | `BLOCK6.gamma_midpoint_refuses = False`; L9 `MIDPOINT_SENTENCE` | fixture G2 |
| §8.3 item 3 outside-processor alternative | `lines.outside_processor_alternative()` | worked example (§6), fixture |
| §8.3 item 3 graphics exclusion P* | `sessions.desk_exclusions()`, `binding.b6_exclusions()` step 3 | fixture: one excluded run; unit test: a stratum driven below 5 |
| §8.5 "What is printed" (C, k, excess, E_add) | `lines.outside_processor_alternative()` | as above |
| §4 counting; §8.2 N3 after desk exclusion | `sessions.analysis_counting()` | fixtures; unit test |
| §6.2 pairing, rules 1 to 3, ties, several GAMMA per floor session | `sessions.pair()` | worked examples 1 and 2 (§5) as unit tests |
| §6.2 step 3b "floor from block 5" | `sessions.pair()` rule 4, cross-block phase | unit test with block-5 stub |
| §10 definition and quantities | `crossblock.summary()` | worked example (§10), half-unit bars |
| §11.1 values, intervals, kept units, flags; Δ; own differences; summary; two facts; item 7 | `crossblock.side_by_side()` | worked example (§11.1) |
| §11.2 replicated / not replicated; not_estimable; short; flagged words beside | `crossblock.replication_word()` | both worked examples; each branch |
| §11.3 ceilings, wording | `crossblock.SENTENCES` | template test |
| §11.4 composition (i), (ii); ignored P1 to P4, D1; run exclusions apply; label; never replaces | `crossblock.flagged_inclusive()` | fixtures N1 and N2 (§16) |
| §12.1 structure only before release | `driver.record()` (§14) | no float token in the record; restricted codes masked |
| §12.3 item 3 blind dry run, no tooling refusal | `scripts/b6_analyze.py --mode blind-dry-run` | e2e |
| §12.3 item 4 recompute agreement (S-13) | `compare.py` | unit test with a synthetic recompute file |
| §13 steps 1 to 11 per counting session | L9 steps per unit (§4.3) | e2e |
| §13 per GAMMA pairing: aggregate floor and dominance close-out | GAMMA unit steps 5, 6 | e2e |
| §13 per GAMMA session: finalization and claim gate with paired floors | GAMMA unit steps 8, 9 | e2e |
| §13 L9 at its release tag plus additions | binding seam with census and equivalence replay (§4.2) | `test_binding_census`, `test_block5_equivalence` |
| §13 synthetic and full-size production-shaped archives through the real stage chain | §16 fixtures, CLI in separate processes | e2e |
| §13 content-addressed outputs; release re-run equal to the dry run | L9 `RunState.register`, `release_difference`; `driver` for the block-6 outputs | `test_release_equals_dry_run` |
| §13 executing review, two cold passes, S-14 pinned before the dry run | process (§15 steps 5, 6) | — |

---

## 14. Blind output layout (structure only)

```
<custody>/
  b6-dry-run/  (or b6-release/)
    B6-BLIND-DRY-RUN-RECORD.json    public: structure only
    restricted/
      logs/
      b6/sessions/<session>.json    counting, desk exclusions, allowance check, b_op check (restricted copy)
      b6/kept/<session>.json        block-6 exclusions documents and the catalog overlay
      units/<unit id>/              one L9 RunState custody per unit (index, outputs, disclosures)
      b6/lines/, b6/machine/        §6 to §8 outputs
      b6/crossblock/                §10, §11 outputs (cross-block phase only)
```

The record (`joulewise.b6_blind_dry_run.v1`) holds: mode; analysis commit; digests of the loop record, of every
session's `harvest.json` and acceptance record, of `registered_constants.json`, the catalog and the acceptance file;
per session: id, pack, round, t0 (integer epoch seconds), loop status, acceptance counting, analysis counting and its
cause, `b5_exclusions_claim_usable`, `b5_reasons`, `b6_exclusions_claim_usable`, kept units per cell and stratum
(integers), desk-excluded run count, `battery.assist` run count per cell, allowance check word, b_op check word; the
pairing table (session ids and rule words); per unit, L9's step records (step, status, exit status, refusal token,
output names and digests); the block-6 step records; `cross_block` status (`ok`, or `not_run` with
`block5_not_released`); `completed_without_tooling_refusal`.

Before writing, the record passes L9's structure test: no float token (`dry_run._FLOAT_TOKEN`) anywhere, codes
derived from a science energy or phase duration (REG §12.1, D21) masked as "removed (restricted code)", and an
outcome-class refusal shown only as "outcome-class refusal at step N".

**Two phases.** *Per-session phase* (any time, block 5 need not be released): floor units, GAMMA units, §6 to §8.
`cross_block` reads `not_run`. *Cross-block phase* (after block 5's release event): `crossblock` reads block 5's
release record (`B5-RELEASE-RECORD.json`), authenticates every output it uses by the digests in that record, and runs
§10 and §11. **The dry run that satisfies REG §12.3 item 3 is a full run that includes the cross-block phase**, so its
output digests are the ones the release re-run must reproduce (§18 D18).

---

## 15. Plan: S-14 and S-15 (the lead runs this after merging L9)

1. **Merge L9 into main** at its release tag (outside this item).
2. **Fill S-11 and S-9.** From each pack's first block-6 smoke archive (non-claim), T_phase per pack, model and phase
   (the longest smoke run); write them into `configs/analysis/b6/registered_constants.json` with the smoke archive's
   path and digest; P* = 0.475 J / T_phase; a dated REG §17 entry.
3. **Base branch.** `lane/<date>-b6-analysis-build` = main (with L9) merged with the block-6 line
   (`lane/2026-10-17-b6-packs-registered`, `1706257c4`, or its successor). A trial merge on 2026-10-21 (main
   `ef520743c` + L9 `1ab888a68`, then + `1706257c4`) conflicts in exactly three files: `joulewise/whole_window.py`
   (take L9's version and re-apply the block-6 line's whole delta to it, `git diff 3c05b8076 1706257c4 --
   joulewise/whole_window.py`: 31 changed lines from `495569dfc`, `a1b2b59c3`, `6ae3965bf` and `0276a3327`, among
   them the busy-only admission in the shared environment validator and the whole-window core check); `configs/gates/hazard_refusals.json` and
   `configs/pins/registry.json` (regenerate with their census tools). L9's `tests/b5_analysis/test_frozen_files.py`
   will then report three files that the block-6 line changed after L9 froze them: `joulewise/flags/exclusions.py`
   (the `pack_scoped` keyword), `joulewise/flags/catalog.py` (the DRAFT_CODES block) and `joulewise/b5/harvest.py`
   (code-table entries, two arm-flag pass-throughs and the NEG-8 comparison tolerance). The merged `harvest.py`
   digest is `1b08dfe4…` against pin4's `68d21947…`. The guard on the analysis line is amended to accept exactly
   these merged digests, each with its source commit range. Whether the deltas change anything on block 5's inputs is
   tested, not assumed: the equivalence replay (§4.2) must show block-5 bytes unchanged. The merge brings these deltas in; nobody writes a new line in a `joulewise/b5/*.py` file. This is
   stage B0 of the build (§17) unless the lead does it; if git cannot merge any other file cleanly, stop.
4. **Build** by the brief (§17), stages B0 to B5.
5. **Executing review** (a non-author model that runs the fixtures and the CLI), then **two blind executing cold
   passes**, Fable 5.1 and Opus 5.5 (REG §13).
6. **S-14 pin.** The merged commit is the analysis commit; a dated REG §17 entry names it. In the same entry, GAMMA's
   pack file estimator list is corrected (REG §9: GAMMA does not print estimator 1, so its `reported_phase_energy`
   entry is removed from `configs/b6/packs/gamma/registration.json` on the analysis line; no program reads the field).
7. **S-15** (whole-machine per phase): the lead checks L9's release tag for a per-phase definition. If one exists, S-15
   is that definition and commit, and `machine.py` calls it. If not (the state at `1ab888a68`), S-15 is filled by a
   dated REG §17 entry adopting §8 of this file, citing the recompute commit that implements it for block 5
   (`76f45da3e` or its successor), with one executing refuter (REG §12.4). The §7 additions (the without-assist value
   and the boundary's second sentence) are part of that fill; the recompute lane adds the without-assist value so that
   REG §12.3 item 4 covers it.
8. **Per-session blind dry run** on the Mac (blinded data never goes to a cloud seat): `scripts/b6_analyze.py --mode
   blind-dry-run` over the nine sessions. Each tooling refusal is cured blind (R3) and the run repeats until none
   remains. The lead reads only the structure record, including r2-gamma's six fields (§12).
9. **After block 5's release event:** the full dry run including the cross-block phase; this is REG §12.3 item 3.
10. **Recompute agreement** (`compare.py`, REG §12.3 item 4, S-13) for block 6's printed quantities. The independent
    recompute needs a block-6 mode (nine sessions, the pairing, the §10 and §11 quantities, §8's without-assist
    value); that is a recompute-lane item, named here because the release needs it.
11. **Release** (REG §12.3): the dated record; then `--mode release` reproduces every dry-run digest.

---

## 16. Fixture specification

*Rule.* Every fixture is generated by code, never copied from a real archive. The archives must have the shape that
the real ones have, so the generator runs the **measurement code at the S-1 commit** (`f31aca19f`): a `git archive`
export of that commit, the real block-6 loop composition (`joulewise/b6/compose.py`), the real chain and driver and
the real harvest (`scripts/harvest_b6_session.py`), with only the hardware replaced (the seams of L9's S10 producer,
`tests/b5_analysis/fixtures_s10.py`, and of `tests/b6/round_support.py`: mock model runtime, synthetic powermetrics
XML, synthetic battery, meter and monitor journals, no launchd). The analysis under test runs from the build branch,
in separate processes through `scripts/b6_analyze.py`. Archives are cached under `tests/fixtures/b6_analysis/` with a
`PROVENANCE.md` that names the export commit and every seam.

*Size.* Full size: ALPHA and BETA sessions 125 runs, GAMMA 107 (REG §3.1), 10 planned units per stratum, corpus 18,
start, midpoint and end references.

*The sessions* (eleven): three counting sessions per pack in the round structure of §5 example 1 (A1, A3, A4; B1,
B2, B3; G1, G2, G3), plus two that do not count:

| Session | Shape |
|---|---|
| G2 | **r2-gamma's shape**: the midpoint reference lost (fails admission), no other window reason. The harvest's `exclusions.json` must read `claim_usable: false`, `reasons: ["neg8.midpoint_lost_primary"]`, and the acceptance `counting: true` |
| A1 | one repeat removed by `thermal.os_level_nonzero` (item 1) and one quad removed by `member.anchor_not_bounded` |
| B2 | four 8B prefill-p2048 runs carry `battery.assist` (two repeats, two in different quads), with meter streams whose B0AC is negative inside their requests and a run whose request has no SMC read (`meter_battery_unavailable`) |
| B3 | two runs admitted after waiting (`idle.waited`) |
| A4 | one run whose idle baseline holds GPU power above P* (the desk exclusion removes its unit); A4 still counts |
| G1 | one quad with an outside-processor excess (C = 1.54, k = 2: E_add 2.50 J) and one flagged run below the line |
| G3 | a contrast whose outcome word differs from G1's and G2's (exercises "not replicated"), and an 8B side mean shifted from its paired BETA r3 cell by more than the two statistical half-widths (the cross-session line says the sessions differ; in G1 they agree) |
| N1 (ALPHA, round 2) | does not count: drift screen failed (D1); computable, so it enters the flagged-inclusive line |
| N2 (BETA, round 4) | does not count: model files differ (W1); not added to the flagged-inclusive line |

Plus a block-5 stub for the cross-block phase: a synthetic `B5-RELEASE-RECORD.json` with the output files it names,
built by L9's own S10 chain (block-5 binding), so the cross-block phase reads real block-5-shaped outputs.

*Synthetic worlds.* The generator sets each effect so that the rule it tests acts above the bar that judges it (the
project's rule: a method difference is caught by making the synthetic world exercise it, never by tightening the bar):
the assisted runs differ from their siblings by at least 10 times the agreement bar of their cell, so "with" and
"without" differ visibly; the same for waited runs, the desk-excluded run, the outside-processor run and the thermal
unit; the GAMMA midpoint excursion in G2 is planted so that the two-value spread differs from the three-value one; the
between-session spread of each quantity is planted at a known value; reference energies about 37 J over about 4 s and
8B cells large enough that the §6 scaling factor exceeds 1 for 8B prefill and for the contrasts. The generator writes,
beside each archive, its own expected values computed by a separate small oracle in the test (not by the analysis).

*Unit-level fixtures* (no archive needed): pairing examples 1 and 2; a desk exclusion that drops a stratum below 5;
`not_estimable` in block 5; n = 1; a short GAMMA; a synthetic recompute file for `compare.py`.

---

## 17. Sol build brief (B6-1 build)

You are a Codex seat (gpt-6.1-sol, effort xhigh). This is claim-path code written blind: open no real archive, no
path under `/Users/edr/night-b6/`, `/Users/edr/night-custody/`, `/Users/edr/night-archive/b5-*` or any block-5
restricted path. Read this file in full first.

**Authority, in order:** (1) the registration, `docs/registrations/block6_replication_DRAFT.md` on main; (2) the
rulings it cites, and B5-PLAN and B5-REG where the registration says "unchanged"; (3) this design. Where they disagree,
the higher one wins; report the disagreement under "decisions I made". Decide anything these texts determine.
NEEDS_RULING only for a choice that changes which data count or a printed number; record it with its evidence and
continue with the rest.

**Base.** Branch `lane/<date>-b6-analysis-build`, created by the lead per §15 step 3. If the launch message says the
base does not exist yet, build it in stage B0. Check `git rev-parse HEAD` against the commit the lead gives; stop if it
differs.

**Seat setup.** Fresh TMPDIR; `JW_B5_SYNTHETIC_ONLY=1` in every test and CLI process (the project's safety switch for
synthetic-only runs; never point a test or the CLI at a real archive or key directory); `/opt/homebrew/bin/python3.13` (in a cloud seat, the seat setup's
python3.13). No `cd` in any shell command; use absolute paths and `git -C`. Do not run the whole suite: CI runs it on
the draft PR; run only the modules you touched plus the registry tests below.

**No silly numbers (binding).** Every tolerance, threshold or assertion on a measured or derived quantity carries its
derivation in a comment beside it. You do not choose a bar; use these:

| Bar | Value | Derivation |
|---|---|---|
| B1 exact | equality (`==`, float hex for floats) | where bit identity is the property: integers, run-id and code sets, digests, words; the equivalence replay (identical inputs, the seam only moves constants); one floor session's outputs in two units; per-session R against the close-out's R; the issuer against `_project_cell` on a complete cell; the two allowances when the survivor sets are equal; b_op against the acceptance record |
| B2 worked examples | half a unit of the last digit printed in this file's or the registration's example | the expected value is known only to that precision |
| B3 analysis against the test oracle on synthetic archives | 1% of the cell's smallest printed half-width h for an energy with a half-width; otherwise 10⁻⁶ relative | the project's agreement rule: between 10⁶ × float noise (2.2 × 10⁻⁷ J at 1,000 J) and 1% of the smallest printed uncertainty |
| B4 release comparison (`compare.py`) | each run's phase energy within 1 mJ; every printed quantity, unrounded, within half a unit of its last printed digit (§11: 5 × 10⁻⁶ J, 5 × 10⁻⁵, 5 × 10⁻⁹ J) | REG §12.3 item 4, S-13 (registered); the observed agreement is printed beside and never used as the bar |
| B5 synthetic effects | each planted effect at least 10 × the B3 bar of its cell | so that a method difference cannot hide under the bar |

**Stages** (one branch, commit and push after each; push a first commit early):

- **B0, base** (only if the lead has not done it): the merge of §15 step 3, resolved by exactly the rules there. Any
  other conflict: stop and report.
- **B1, binding seam.** `joulewise/b5_analysis/block.py`; every binding site of §4.2 reads through
  `block_for_index`; `tests/b6_analysis/test_binding_census.py`; `tests/b6_analysis/test_block5_equivalence.py` (L9's
  S10 chain at L9's release tag and at your head: equal digests, bar B1). Done when both pass and L9's own tests in
  `tests/b5_analysis/` pass unchanged.
- **B2, fixtures.** The generator of §16 and the eleven archives plus the block-5 stub, cached; `PROVENANCE.md`.
  Report the wall time of a cold build.
- **B3, sessions and binding.** `sessions.py`, `binding.py` (§4.4 to §4.8), floor units in `driver.py`;
  `configs/analysis/b6/*.json`. Done when the six floor units run on the fixtures with no tooling refusal and every
  §4.5 and §4.8 check holds.
- **B4, GAMMA units and lines.** GAMMA units (§4.3), `lines.py`, `machine.py`. Done when the three GAMMA units run,
  G2 is analysed with the midpoint sentence, and every §6 to §8 line matches the oracle (bars B2, B3).
- **B5, cross-block, comparison, CLI.** `crossblock.py`, `compare.py`, `scripts/b6_analyze.py`, the record of §14;
  the end-to-end test runs the CLI in separate processes over the eleven sessions in both phases, then `--mode
  release`, and asserts equal digests.

**WRITE_SCOPE (exhaustive).**

- New modules: `joulewise/b5_analysis/block.py`; `joulewise/b6_analysis/__init__.py`, `sessions.py`, `binding.py`,
  `driver.py`, `lines.py`, `machine.py`, `crossblock.py`, `compare.py`; `scripts/b6_analyze.py`.
- New configuration: `configs/analysis/b6/seal_pins.json`, `registered_constants.json` (T_phase null unless the lead
  has filled S-11), `dry_run_refusal_classes.json`, `printed_precision.json`.
- Binding sites (edits that route a block-5 constant through `block_for_index`, and nothing else):
  `joulewise/b5_analysis/windows.py`, `archive.py`, `kept_units.py`, `context.py`, `disclosures.py`, `dry_run.py`,
  `bracket.py`; `joulewise/analysis_engine/inputs.py`; `joulewise/paper_reported_energy_issuer.py`;
  `scripts/extract_detection_floors.py`, `scripts/mint_floor_artifact_generalized.py`,
  `scripts/build_results_fill_input.py`, `scripts/produce_b5_disclosures.py`.
- Tests: `tests/b6_analysis/**` (new); `tests/fixtures/b6_analysis/**` (new, generated); `tests/b5_analysis/test_frozen_files.py`
  only for the §15 step 3 amendment and only in stage B0.
- Registries, each only to add the rows its test names for the new modules or sites:
  `tests/test_battery_float_sweep.py` (`READERS`: a row for each new file that reads `b_fiducial_s`, classification
  "bracket rows", gate "outside the derivation scope: block-6 analysis reads its session's own b_op");
  `configs/gates/hazard_refusals.json` (run `python3.13 -m tests.hazards.refusal_census`; a new module that a scanned
  module imports goes into `scan.modules` or into `scan.not_scanned` with reason `analysis`; never BASELINE);
  `tests/hazards/test_import_graph.py`; `tests/flags/test_flags_import_graph.py`; `tests/b6/test_catalog.py` (expect no
  change: the catalog file is pinned); `tests/test_fixture_orphan_census.py`; `tests/test_digest_pin_census.py`;
  `tests/test_schemas.py` (with `schemas/` entries for the two new record schemas if that test requires them).
- In stage B0 only: `joulewise/whole_window.py`, `configs/gates/hazard_refusals.json`, `configs/pins/registry.json`,
  for the merge resolution of §15 step 3.

**Never edit:** any `joulewise/b5/*.py` listed in `configs/campaigns/v5_claim_25g83/sealed_inventory.json`;
`configs/b6/flag_catalog_b6.json`; `configs/b6/registration/*`; `configs/b6/packs/*` (the lead corrects GAMMA's
estimator entry at the pin); `joulewise/b6/*.py` (the analysis imports them; a defect there is reported, not fixed);
any path in `joulewise/b6/registration.py` `NUMBER_BEARING_PATHS`; `joulewise/flags/*`; `joulewise/paper_custody.py`.
If a file outside this scope is needed, name it in the report and continue with the rest.

**Always run:** the modules you touched, `tests/b5_analysis/`, `tests/b6/test_catalog.py`,
`tests/hazards/test_refusal_allowlist.py`, `tests/hazards/test_import_graph.py`,
`tests/flags/test_flags_import_graph.py`, `tests/test_battery_float_sweep.py`, `tests/test_fixture_orphan_census.py`,
`tests/test_digest_pin_census.py`, `tests/test_schemas.py`. Environmental failures (`/private/tmp`, launchd,
powermetrics, fixture `git commit` exit 128) are listed, not chased.

**Report** (first line your model id): commits; tests run with counts; the cold-build wall time of the fixtures;
decisions I made; NEEDS_RULING (or "none"); every L9 or block-6 defect found, with the fixture that shows it.

---

## 18. Decisions made by the author

- **D1.** One seam (`AnalysisBlock`) instead of a block-6 copy of L9's driver: two copies would drift, the defect the
  project removed from `flags/exclusions.py` on 2026-10-06. The equivalence replay is the price.
- **D2.** Block 5's dry run and release run from L9's release tag; block 6's from the S-14 commit. L9's
  `release_difference` compares analysis commits, so the two blocks cannot share a run.
- **D3.** Units: a floor unit per counting ALPHA or BETA session, a GAMMA unit per counting GAMMA session (§4.3). A
  floor session serving no GAMMA session (ALPHA r4) still gets its cells, floors and R.
- **D4.** Kept units from the sealed `compute` with no pack id (§4.5). It reproduces REG §8.2 without the `pack_scoped`
  keyword, so the result does not depend on which `exclusions.py` the base carries.
- **D5.** Counting is the loop's, confirmed by the acceptance, re-tested for N3 after the desk exclusion (§4.6).
- **D6.** The allowance is REG §1.8's from the b6 screen record; the block-5 harvest's allowance is a cross-check
  (§4.7).
- **D7.** b_op from block 6's acceptance, checked against the acceptance record (§4.8).
- **D8.** The GAMMA midpoint refusal is off for block 6 and the fixed sentence printed (REG §8.2).
- **D9.** The paper-custody opens (L9 step 9b, the open half of step 10) and the results-fill input are not run for
  block 6. They admit paper inputs for block 5's placements; block 6's tables have no placement yet (placement is the
  orchestrator's call), and its numbers are protected by content addressing, the release re-run and the recompute.
  A later placement lane adds them with block-6 roles.
- **D10.** L9's J6 sensitivity (b_max) runs per GAMMA unit over its three sessions, labelled "per pairing".
- **D11.** T_phase is keyed by (pack, model, phase): for GAMMA, each side's own model ("the run's own target phase",
  REG §8.5). Keyed by (pack, phase) only, GAMMA's 1.7B runs would get the 8B's longer phase and a lower line; at the
  quiet rails (about 0.2 mW against lines of tens of mW and above) neither removes a run on the rehearsals.
- **D12.** E_ref and T_ref of the scaled allowance: plain means of gross request energy and request length over the
  start, midpoint and end survivors; T of a cell by estimator 1's weights.
- **D13.** The per-phase whole-machine value is computed for block 5 too, after its release, by the same function, so
  REG §10 has its n.
- **D14.** The background-priority outside-processor line (w = 0.0862) is not printed: REG says "may", and the table
  already carries the registered alternative.
- **D15.** Printed precision as in §11; it is a printing choice, and it is what makes S-13's half-unit bar a real
  number instead of float noise.
- **D16.** Pairing ties go to the earlier t0.
- **D17.** A non-counting GAMMA session in the flagged-inclusive line pairs only with analysis-counting floor
  sessions.
- **D18.** The release-gating dry run includes the cross-block phase and so runs after block 5's release.

**For the lead.** S-15 (§15 step 7) changes no registered number, but it fills a slot by adopting a definition that no
block-5 analysis commit holds, so it is the lead's call with a REG §17 entry. Nothing else here needs a ruling.
