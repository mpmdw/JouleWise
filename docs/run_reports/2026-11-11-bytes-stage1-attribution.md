# BYTES stage 1: attribution of the 390 above-bar fields (RL-80)

2026-11-11 07:05 PST. Opus attribution seat under research-lead ruling RL-80. This is not a repair seat.

**What was read.** On the stage-1 run line `lane/2026-11-07-bytes-stage1-run` @ `df4c73e55`:
- the estimator `joulewise/bytes_analysis.py` (sha256 `18582818…0a71`, the pin) and the reducer and harvest code
  it calls;
- the twin `scripts/bytes_twin.py`;
- the exporter `joulewise/b6/export_runs.py`;
- the comparer `tests/test_bytes_agreement.py`;
- the registration `docs/registrations/bytes_pack_v1.md` §6, §7, §11 to §16;
- the design ruling's Addenda 1 to 8 (`docs/design/bytes_pack_design.md`);
- block 5's plan §4 step 4 (`configs/campaigns/v5_claim_25g83/analysis_plan_block5.md`);
- the synthetic campaign fixture.

From RUN_STATE item 264 and the magistrate record I read field names, counts and paths only.

**Blind status.** Blind to every BYTES value, for the fit set and the held-out models alike. I opened no export,
predictions file, withheld store, key, stage-1 output, archive or custody path. I did not use SSH. Every
attribution below rests on code and text alone. I fixed it before any value was compared. This report does not say
which side's bound is larger, and the code reading here does not settle that.

**What the diagnostic is.** `scripts/bytes_stage1_attribution_probe.py`, with tests in
`tests/test_bytes_stage1_attribution_probe.py`. It is a probe the magistrate runs over the existing stage-1
outputs. It prints only these:
- names, built from a fixed vocabulary: fit models, boundaries, variants, comparer field names and catalogued flag
  codes;
- counts;
- each above-bar difference as an unsigned multiple of its bar;
- yes/no answers.

It is standard library only. The tests use synthetic inputs and plant energies, durations and bounds. They check:
- that none of those values reaches the output;
- that no signed number appears;
- that the bound and `w` lines do not change when a and t are swapped;
- that a held-out group is counted and never named;
- that withheld, key, custody and held-out paths are refused.

## Item 1. The clock-anchor timing term (`B_j`, `lower_j`, `upper_j`, the attribution floors, `B_kind:anchor`)

**Governing sentences.**
- Registration §7, the table of B's terms (`bytes_pack_v1.md:222`). For rails, phase-edge timing is "the run's rails
  anchor-shift bound (block-5 plan §4 step 4, its first kind, re-derived under the session's operative timing bound
  from `joulewise/b6/calibration.py`; Addendum 1 item 4)". For rest it is "rails anchor-shift bound + u + v".
  DC input carries no anchor term.
- Registration §16 (`bytes_pack_v1.md:428`): "The analysis also reads the harvest's operative timing bound
  (`calibration.operative_bound_s` in `derived/b6-acceptance.json`, evaluated by `joulewise/b6/calibration.py`;
  Addendum 1 item 4) and never recomputes a calibration bracket."
- Design Addendum 1 item 4 (`bytes_pack_design.md:172`): "The operative bound comes from the block-6 harvest's
  existing code path (`joulewise/b6/calibration.py`)."
- Block-5 plan §4 step 4 (`analysis_plan_block5.md:233-246`). The first kind is "the largest change in the energy
  assigned to the member's phase". "The result is the field `max_abs_delta_j` of the member's anchor-shift energy
  envelope for the phase". "The summary stored in the bundle was reduced under the pre capture's fiducial bound
  alone, so the bound is not read from it: it is read from the member's summary as reduced again, in memory,
  under b."

These sentences fix two properties of the term:
- **(P1)** It is the envelope of the **decode phase's** energy.
- **(P2)** It comes from a re-reduction under the **session's operative bound**, `calibration.operative_bound_s`,
  which `calibration.evaluate` computes as max(pre, post) + max(drift, screen) (`joulewise/b6/calibration.py:87-107`)
  and `joulewise/b6/acceptance.py:276-277` records.

**Estimator, stage `fit`. Follows the text.**
- It reads `acceptance.calibration.operative_bound_s` (`joulewise/bytes_analysis.py:595-599`).
- It passes that bound to `reduce._rederive_summary_for_authenticated_fiducial_bound` (`bytes_analysis.py:600-603`;
  `joulewise/reduce.py:2715-2746`). That function re-runs the reducer in memory with the member's fiducial bound
  replaced by the operative bound (`reduce.py:1839-1858`).
- It requires the decode envelope (`bytes_analysis.py:604, 614-617`) and takes
  `energy_anchor_shift_envelopes["/phase_energy_j/decode"].max_abs_delta_j` (`bytes_analysis.py:1004-1005`).
- That value enters B for rails and rest (`bytes_analysis.py:1275-1278`) and the rails attribution floor
  (`bytes_analysis.py:1329`).

So P1 and P2 both hold.

**Twin, every stage. Departs from the text.** `_member` takes the export column
`bound_E_clock_anchor_shift_bound_j` (`scripts/bytes_twin.py:1324`), for rails (`:1328`) and rest (`:1345`). The
attribution floors are built from that column (`:1463-1466`, `:1492`). The twin never refers to an operative bound.

**The export column is not the §7 re-derivation. It fails both properties.**
- The exporter fills `bound_E_clock_anchor_shift_bound_j` from `energy_bound_terms_j` of
  `withheld/reductions/<run>.summary_metrics.rereduced.json` (`joulewise/b6/export_runs.py:677-679, 701-702`).
- **P2 fails.** That file is written once, by the harvest's member assessment, through
  `reduce_bundle(bundle, reducer_version=…)` with no bound override (`joulewise/b5/harvest.py:2266-2279`). It is
  therefore reduced under the member's own mint calibration (`reduce.py:1820-1826`; the override branch at `:1839`
  is not taken). It is not reduced under the session's operative bound.
- **P1 fails.** In the reducer, `energy_bound_terms_j["E_clock_anchor_shift_bound_j"]` is the envelope of
  `"/gross_energy_j"`, the run's whole sampling window, not the decode phase (`reduce.py:3243-3250`; on the v0.6.0
  path, `:3607-3613`).
- For contrast, the exporter does re-derive under the operative bound for the reference request columns
  (`export_runs.py:442-445`). It does not do so for science members' bound columns.

**Why the agreement campaigns did not see it.**
- The fixture sets every anchor envelope and bound term to 0 (`tests/fixtures/bytes/campaign.py:235-238`).
- For a labelled synthetic fixture, the estimator returns the stored summary instead of re-reducing
  (`bytes_analysis.py:605-612`).
- So all nineteen campaigns had B_kind:anchor = 0 on both sides.
- On real data at the blinded stage, both sides read the export column. The estimator does so at
  `bytes_analysis.py:1146`, as §11's stage table requires ("from the blinded export's columns (no archive, key or
  meter reads)", `bytes_pack_v1.md:368`). So the clean blinded agreement could not see the term either.

**RL-80 branch: the twin departs from the text.** The twin is fixed; the estimator and its digest do not move. The
rerun must give a predictions file byte-identical to the uncommitted one (sha256 `a6cb172c…5f19`). Two points for
the fix seat:
- At stages 1 and 2, the twin must form the term as the decode-phase anchor-shift envelope under the session's
  operative bound, independently of the analysis (§12, R8 item 4).
- At the blinded stage, §11 still prescribes the export columns. Under the text, the twin's blinded path keeps
  reading them, as the estimator's does.

Addendum 8 item 4 says method differences must not hide under the bar. By that rule, the synthetic campaigns need
nonzero anchor envelopes for the fix's agreement, with the decode envelope distinct from the gross one and the
operative bound distinct from the mint bound. As things stand they test the term at zero.

**Questions the diagnostic answers.** Each one is counted over the fit cells.
- `B_other_keys`: is every above-bar fit field one of the seven named?
- `B_other_kinds`: are the interpolation, drift and meter-edge kinds within bar?
- `B_is_anchor`: does the B difference equal the anchor-kind difference, within bar?
- `B_centre_h`: are mean, h and duration within bar?
- `B_ends`: does each interval end move by exactly the B difference?
- `B_twin_is_export`: does the twin's anchor term equal the stratified average of the export column? The probe
  scales by the twin's own decode mean over the export's `phase_decode_j` average, so the blinding factor cancels
  and no key is read.
- `B_estimator_is_export`: does the estimator's anchor term equal that same average?
- `B_operative_one`: is every operative record `rereduced`, with one bound equal to the sidecar's
  `operative_bound_s`?
- `MULT` lines give each difference as a multiple of its bar, only where the bar is 1% of the cell's (h + B) or of w; a field with an absolute bar (1 ms, 0.0005 J, ...) gets a `NOMULT` line, since its multiple times the public bar would be the difference in seconds or joules.

**What the output settles.** The attribution stands as written if all of these hold:
- `B_twin_is_export` is yes in every rails cell;
- `B_estimator_is_export` is no wherever the anchor is above bar;
- `B_is_anchor`, `B_ends`, `B_other_kinds`, `B_centre_h` and `B_operative_one` are all yes;
- `B_other_keys` is yes.

If `B_twin_is_export` is no anywhere, the twin has a second difference, such as how it unblinds the column, and the
item comes back before any fix. The probe does not separate P1 from P2. That would need archive reads, and the
attribution does not need it: both are code facts, and both sit on the twin's side.

## Item 2. The flags

**Sources, from code.**
- **Estimator at `fit`.**
  - Each run's flags are its run-scoped codes from `derived/flags.jsonl` and `acceptance.emitted_flags`, plus every
    **session-scoped** code from those two sources (scope without `run_id`, `bytes_analysis.py:943-953`), plus its
    member exclusion codes (`:920-928`).
  - Meter flags are then added (`:1054, 1061-1063, 1077`).
  - A cell's flags are the union over its kept runs (`:1326`).
- **Estimator at `blinded`.** The export's `flag_codes` and exclusion codes only. Session flags are an empty set
  (`bytes_analysis.py:1135-1139`).
- **Export.** `flag_codes` carries run-scoped codes only (`export_runs.py:580-585`). Session-scoped codes appear
  only as names in the sidecar's `flag_counts` (`export_runs.py:756`; `acceptance.py:364-365, 385`).
- **Twin.** The export's `flag_codes` plus its own meter flags (`bytes_twin.py:1471-1473, 2109-2112`). It never
  includes session-level codes or exclusion codes.

**Candidate set, until the probe has run.**
- **C1, session-scoped codes.** These would appear on the estimator side only, in every fit cell, on all three
  boundaries. They match the reported pattern: every cell, `dc_input` included.
  - One such code is certain in every session: `power.pstar_unsized`. Acceptance emits it with no member
    (`acceptance.py:280-285`). It is DISCLOSE in the catalog.
  - Others are possible: the `calibration.*` flags from `calibration.evaluate`, emitted without a member
    (`acceptance.py:278-279`), and `catalog.digest_mismatch`, `registration.default_used`,
    `plan.spare_retry_present` and evidence window flags (`acceptance.py:183-190`).
- **C2, meter-derived flags.** `bytes.meter_decode_unavailable` and `bytes.meter_gap` (§7, meter edge term) and
  `bytes.decode_battery_assist` (§6). Both sides compute these, by different code paths. They could differ only
  run by run.
- **C3, exclusion codes of restored runs in flagged-inclusive cells.** These would appear on the estimator side
  only, if acceptance excluded a run for a code that is not also in its `flag_codes`.

**Governing text.**
- §6 (`bytes_pack_v1.md:177`): "A **flag** is a recorded code on a run or session."
- §15 (`bytes_pack_v1.md:423`): each pass's cell prints its "flags".

Neither sentence says whether a session-scoped code belongs in a cell's flag list. The estimator's own contract
(`docs/contracts/bytes_tables.md:91-92`) keeps the session codes as labels. That contract is implementation text,
not registration.

The estimator is also inconsistent with itself: it prints different flags for the same rails cell at `blinded` and
at `fit`.

**RL-80 branch.**
- **For C1: the text supports both readings.** It goes to the research lead as an interpretation:
  - (a) a cell lists every code recorded on its session as well as on its runs (the estimator at `fit`);
  - (b) a cell lists its runs' codes, and session codes are printed at session level (the twin, and the estimator
    at `blinded`).
  - Under (b) the estimator changes. Its digest moves, which is §11's fix path and a dated addendum. Under (a) the
    twin changes, and the estimator's blinded path differs from the reading.
- **For C2, if it appears.** §7 and §6 define each code. The side that departs is the one whose condition differs
  from the sentence for that code. That needs a second, code-level attribution of the named code.
- **For C3, if it appears.** §6's flagged-inclusive line restores the run. It does not say whether its exclusion
  code is listed. This is an interpretation, like C1.

**Questions the diagnostic answers.**
- `FLAG` lines give each differing code, by boundary and side, with cell counts and catalog effect.
- For each code, per session:
  - `F_row_flag_codes`: is it in `flag_codes` on any row?
  - `F_kept_flag_codes`: is it in `flag_codes` on a kept run of the cell?
  - `F_exclusion_codes`: is it in any row's exclusion codes?
  - `F_sidecar_counts`: is it in the sidecar's `flag_counts`?
  - `F_every_cell`: is it in every fit cell of the estimator?
  - `F_meter_flag`: is it a meter flag?
  - `F_blinded_estimator`: is it in the estimator's blinded flags for that cell?

**What the output settles.** It sorts each code into C1, C2 or C3:
- **C1:** estimator only; `F_row_flag_codes` no, `F_exclusion_codes` no, `F_sidecar_counts` yes, `F_every_cell` yes,
  `F_blinded_estimator` no.
- **C2:** `F_meter_flag` yes.
- **C3:** `F_exclusion_codes` yes.

A code that fits none of these comes back to the attribution seat.

## Item 3. `w` at fit-commit

**What it is.** The comparer reads `w = (upper − lower) / 2` of the gross primary fit point
(`tests/test_bytes_agreement.py:1070-1072`). For two passes, the registered half-width is the mean of the passes'
(h + B) (§7, "Per model, combining passes", `bytes_pack_v1.md:280`).

**Whether it follows.** With h within bar, the difference in `w` is the mean over passes of the difference in B.
So it follows from item 1 alone. Flags carry no number, so item 2 does not enter. `w` is above bar on rails and
rest, not DC input, which matches the §7 table: DC input carries no anchor term.

**Branch.** The same as item 1: the twin departs. No separate fix.

**Questions the diagnostic answers.**
- `W_follows_B`: does Δw equal the mean over passes of the gross cell's ΔB, within the w bar?
- `W_with_B`: is `w` above bar exactly where that model's and boundary's B is?

## Running the diagnostic (magistrate, measurement Mac)

The stage-1 `--out` directory is `$S1/run` (`docs/run_reports/2026-11-07-bytes-stage1-plan.md` §3.8). The probe
reads `$S1/run/agreement-stage1.json`, `$S1/run/agreement-blinded.json` and
`$S1/run/out/a-fit/fit_pass_estimates.json`, and the fit sessions' `.runs.csv` and `.session.json` under
`$S1/export`. `$W` is not moved: `git fetch` changes refs only.

```zsh
git -C $W fetch -q origin analysis/2026-11-11-bytes-stage1-attribution
git -C $W show origin/analysis/2026-11-11-bytes-stage1-attribution:scripts/bytes_stage1_attribution_probe.py > $S1/attribution-probe.py
$PY -I $S1/attribution-probe.py --repo $W --run-root $S1/run --export $S1/export > $S1/attribution-probe.txt; echo rc=$?
```

- rc 0: the output is in the file and can be committed to the record as it stands. It holds names, counts,
  multiples of bar and yes/no only.
- rc 2: a path was refused.
- rc 1: the probe failed. It prints the exception class only.

Under RL-80, the seat that builds any fix sees only what this report states, plus the yes/no and count lines the
lead relays.
