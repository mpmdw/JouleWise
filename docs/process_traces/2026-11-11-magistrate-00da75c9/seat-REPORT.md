# RL-80 attribution seat (Opus 5.5): BYTES stage 1, analysis vs twin

Saved by the magistrate (activation 00da75c9) from the seat's hand-back; the harness refused
the subagent's own write of this file. Line numbers are at `df4c73e55`. "Estimator" =
`joulewise/bytes_analysis.py`; "twin" = `scripts/bytes_twin.py`; "comparer" =
`tests/test_bytes_agreement.py` `compare_campaign` (imported by `scripts/bytes_stage1.py`).
No repository file was edited; nothing under `night-archive/`, `night-b6/` or any pack or
withheld store was opened by the seat.

## Verdicts

- **Item A (anchor term):** the estimator at stage `fit` follows §7 as written; the twin departs at
  stage 1. The twin's export column is a different quantity (gross sampling-window envelope, not the
  decode phase), reduced under a different bound (the member's mint calibration, not the session's
  operative bound). The text supports one reading.
- **Item B (flags):** from code, most likely session-scoped flag codes. The estimator adds them to
  every record at `fit`; the export's `flag_codes` drops them, so the twin never sees them. The text
  supports both readings (RL-80 branch 3). The diagnostic lists the actual codes.
- **Shared cause:** none in code; shared root: both are archive information the estimator reads at
  `fit` that the export does not carry, and the synthetic fixtures zero or omit both.

## 1. Item A: the rails anchor-shift term

| Side, stage | Source |
|---|---|
| Estimator, `fit` | `operative_summary` (`bytes_analysis.py:587-617`, called `:999-1005`) re-reduces in memory with `reduce._rederive_summary_for_authenticated_fiducial_bound(plain, authenticated_fiducial_bound_s = b6-acceptance.calibration.operative_bound_s)`; takes `energy_anchor_shift_envelopes["/phase_energy_j/decode"].max_abs_delta_j` as `rails_anchor_j` (`:1013`); enters B on rails and rest (`:1275`). |
| Estimator, `blinded` | export column `bound_E_clock_anchor_shift_bound_j` (`:1146`). |
| Twin, every stage | export column `bound_E_clock_anchor_shift_bound_j`, unblinded with the released key (`bytes_twin.py:1324` `_member`; rails `:1328`, rest `:1345`). |

The operative bound is written by `joulewise/b6/calibration.py` `evaluate` (`:45-107`, called at
`acceptance.py:276`); the reducer applies it only through the override at `reduce.py:1838-1858`.

The export column is not §7's re-derivation:
- filled from `withheld/reductions/<run>.summary_metrics.rereduced.json`, field
  `energy_bound_terms_j.E_clock_anchor_shift_bound_j` (`export_runs.py:677`, `:701-702`);
- the harvest writes that file with `reduce_bundle(bundle, reducer_version=recorded)` and no override
  (`b5/harvest.py:2266-2279`), i.e. under the member's mint calibration bound (`reduce.py:1812-1836`);
- the reducer sets that field to the `/gross_energy_j` envelope's `max_abs_delta_j`, the whole
  sampling window (`reduce.py:3243-3250`; also `:3607-3613`); the decode-phase envelope is a separate
  entry (`:3225-3240`).

Governing sentences:
- `docs/registrations/bytes_pack_v1.md:222`: "the run's rails anchor-shift bound (block-5 plan §4 step
  4, its first kind, re-derived under the session's operative timing bound from
  `joulewise/b6/calibration.py`; Addendum 1 item 4)"; rest = "rails anchor-shift bound + u + v".
- `docs/design/bytes_pack_design.md:172` (Addendum 1 item 4): "The operative bound comes from the
  block-6 harvest's existing code path (`joulewise/b6/calibration.py`)."
- `configs/campaigns/v5_claim_25g83/analysis_plan_block5.md:234`: first kind = "the largest change in
  the energy assigned to the member's phase … b is the window's operative fiducial bound"; `:246`:
  "The result is the field `max_abs_delta_j` of the member's anchor-shift energy envelope for the phase
  … The summary stored in the bundle was reduced under the pre capture's fiducial bound alone, so the
  bound is not read from it: it is read from the member's summary as reduced again, in memory, under b".
- §6 `:179`: "no decode timing envelope" makes a run unusable.

Follows or departs: estimator at `fit` follows; twin at stage 1 departs (one reading). Blinded stage:
§11 (`:368`) limits `blinded` to the export's columns, so blinded agreement could never see item A.
Fixture gap: `tests/fixtures/bytes/campaign.py:235-238` writes both fields as 0, so the 19 agreement
campaigns could not separate the sources (contrary to §12 `:387`, Addendum 8 item 4). For the fix
round: the twin cannot import the reducer, so following §7 needs either an input carrying the operative
decode-phase envelope or a twin-side envelope computation; that choice follows from the text.

## 2. Item B: cell `flags`

- Estimator at `fit`: `_record_base` (`bytes_analysis.py:920-928`) unions run-scoped codes from
  `derived/flags.jsonl` and `b6-acceptance.emitted_flags` (`:947-951`); every session-scoped code (no
  `scope.run_id`) from both, added to every record (`:952-953`, `:927`); member exclusion codes
  (`:944-946`); meter-join flags (`:1053-1054`, `:1061-1063`, `:1076-1077`); `bytes.withheld_missing`
  (`:977-979`). Cell flags = union over kept records (`:1326`), or module when unavailable (`:1364`,
  `:1368`).
- Estimator at `blinded`: export `flag_codes` and `exclusion_codes`, no session codes (`:1137-1139`).
- Twin: export `flag_codes` plus `_meter_flags` (`bytes_twin.py:2108-2112`); cell union over kept rows
  (`:1470-1473`).
- Export `flag_codes` (`export_runs.py:581-585`, `:676`) keeps only rows with a `run_id`;
  `evidence.runtime._b6.flags` holds every `flags.jsonl` row (`acceptance.py:437-452`, `:570`);
  acceptance's session-level emissions carry no `run_id` (`acceptance.py:176-197`).

Candidates: (1) session-scoped codes (fits "every cell, DC input included, blinded clean");
(2) exclusion codes of runs restored in flagged-inclusive cells (unlikely; would show at blinded);
(3) per-run meter-join disagreements (implausible on every cell).

Registered rules: §6 `:177` "A **flag** is a recorded code on a run or session" … "each code has one
effect"; §15 `:423` cell contents include flags; meter-join §7 `:228`; `bytes.decode_battery_assist`
§6 `:190`; `bytes.withheld_missing` §11 item 4 `:358`. `docs/contracts/bytes_tables.md:91-92` supports
the estimator but is not registered text.

Both readings (branch 3): Reading 1 (estimator): a session code is a flag (§6); a pass's cell belongs
to one session, so §15 prints its codes in every cell. Reading 2 (twin): a cell's flags are the codes
on its runs (§6 "Units, not runs"; §15 lists flags beside removed units); the export carries only run
codes and the estimator's own blinded cells print without session codes. Effect: a printed label list
only, provided every differing code is DISCLOSE; the diagnostic prints each code's effect.

## 3. Shared cause

`operative_summary` adds no flag (a failed re-derivation makes the record unusable, `:1017`);
`member.anchor_not_bounded` is a validity code on both sides; DC-input cells have no anchor term yet
differ in flags. Planting exactly these two causes synthetically gives 390 above-bar fields with the
same field set as the real stage 1: consistent, not proof.

## 4. The diagnostic

Command (`--out` must not exist):

```
TMPDIR=/private/tmp/jwrl80-tmp /opt/homebrew/bin/python3.13 -B /Users/edr/night-custody/magistrate/rl80-attrib/seat/diag.py --repo /Users/edr/code/jw-wt/bytes-stage1 --manifest /Users/edr/night-archive/bytes-stage1-20261111/manifest.json --export /Users/edr/night-archive/bytes-stage1-20261111/export --run /Users/edr/night-archive/bytes-stage1-20261111/run --out /Users/edr/night-custody/magistrate/rl80-attrib/diag-out
```

Reads (audit-hook fence): repo; manifest; export (never `withheld`); from `--run` the agreement files,
summary, `out/a-fit/fit_pass_estimates.json`, `out/a-fit/predictions.json`, `out/t-1.json`; in
`released-keys/` only `pack.json`, `release.json` and the 3 fit keys + `neg8_reference`; per archive
`derived/b6-acceptance.json`, `derived/flags.jsonl` (session rows and fit-run rows, codes only),
`sources/{claim,bound}-runs/<run>` for fit-released runs, `ARCHIVE.desk/`. Never: any `withheld`
path, the loop packs, roster, meter stream, other `/Users/edr/night-*`. Writes only under `--out`.
Refuses before reading any value if the release is not exactly the fit set + `neg8_reference`, a key
file outside it is present, or a held-out row is visible in the export.

Bars: the comparer's own `bar_energy(h + B)` of the estimator's cell; per-run tests use the smallest
such bar among cells keeping the run; A12 uses the commit row's bar; sets compared exactly.

Questions: A1 twin anchor = stratified export column; A2 estimator anchor = stratified own
re-derivation; A3 estimator anchor = stratified export column; A4 export column = gross envelope, mint
bound; A5 gross = decode envelope (mint); A6 decode envelope mint = operative; A7 gross operative =
export column; A8 same kept runs; A9 dB = d(anchor); A10 d(lower), d(upper) are dB alone; A11 each
side's `rails_attribution_floor_j` = max of its own source; A12 commit dw = mean over passes of
d(h+B)/512; per-run A4-A7; B1-B3 (every estimator-only code session-scoped; no twin-only code; no
estimator-only code in kept runs' export `flag_codes`); census of above-bar rows with ratio min/median/max.

Prints only labels, fit model names, pass numbers, boundaries, variants, comparer field names, flag
codes (pattern-filtered), catalog effects, counts, yes/no, |diff|/bar to 3 s.f. Never a value, bar,
sign, run/session identity, clock or exception message.

Synthetic proof (`synthetic-demo/`): R6 twelve-sub-pack fixture; planted a nonzero decode envelope in
300 fit runs (export column 0) and one session-scoped DISCLOSE code in all 12 archives. Real
`run_stage1`: exit 7, blinded 0 above bar, stage 1 390 above bar. diag: exit 0; A1 48/0, A2 48/0,
A3 0/48, A7-A11 48/0, A12 yes 9/9; A4-A6 not evaluable on mock bundles (no clock anchor). Item B: 72
cells, B1-B3 72/0. Value scan of all outputs clean. Refusal probes (held-out key, held-out row) exit 2
before reading; 15 fence probes as expected.

## 5. Decisions the seat made

1. Item A has one reading (`:222` parenthesis + "first kind").
2. Blinded use of the export column is not a departure (§11), though it is not §7's B.
3. Item B is branch 3 (`bytes_tables.md` is not registered text).
4. Bars: only the comparer's `bar_energy` or the commit row's bar; sets exact; no seat-chosen tolerance.
5. Stratified average per §7 item 4: 0.2 × mean of kept repeats + 0.8 × mean of kept quad members.
6. Real runs do not read archive `withheld/reductions`; the mint summary is recomputed in memory with
   `reduce_bundle` and no override, as the harvest did.
7. `flags.jsonl` read in full as the estimator does at `fit`; non-fit rows dropped after scope is read.
8. Out of scope: per-run attribution of meter-join flags.
9. No test run; the tests module is imported only for bars and mappings.
