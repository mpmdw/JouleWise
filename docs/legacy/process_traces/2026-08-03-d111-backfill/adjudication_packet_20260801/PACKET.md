# Machinery adjudication packet — metrology windows A + B (assembled 2026-08-01)

Mechanically assembled by the magistrate for an INDEPENDENT READ-ONLY
audit. The two whole-window verdicts below FAILED and **stand as
issued** — this audit does NOT re-run, override, or reinterpret either
verdict. Its question is whether the whole-window verdict machinery
correctly implements its contract when evaluating SALVAGE-SHAPED
windows, and if not, what the minimal contract-true repair is.

## The two verdicts (as issued)

- **Window A** `runs_window_metrologyA_20260731` — verdict row = LAST
  line of `runs_window_metrologyA_20260731/campaign_log.jsonl`
  (status "failed", completed 2026-08-01T07:52Z). Conditions:
  `whole_window_bundle_invalid`, `environment_admission_failed`
  (excluded_bundles carries the quarantined-never-replaced
  `mtadd-p0512o0512-r08` with `path does not exist`),
  `instrument_calibration_bracket_missing`
  (`calibration_bracket_set` pre AND post null — the selector refused
  the recorded-deviation retry post-cal `20260731T215120-fa1e9cda`;
  the §8 budgetable case was never evaluated). `source_campaign_manifests`
  resolved 6 manifests. neg8_bracket PASSED. 1 supersession consumed
  (mtadd-p0512o0512-r06) + bound-root supersession.
- **Window B** `runs_window_metrologyB_20260801` — verdict row = LAST
  line of `runs_window_metrologyB_20260801/campaign_log.jsonl`
  (status "failed", completed 2026-08-01T14:19Z). The §8 calibration
  bracket FORMED and PASSED (pre 20260801T014059-8c3bfe9e / post
  20260801T064830-c76f5d1c, drift 2.25 ms vs 10 ms policy). Conditions:
  `whole_window_campaign_membership_unresolved`
  (`source_campaign_manifests` EMPTY despite a populated
  `campaign_manifests/` dir that the supersession recorder consumed an
  hour earlier), `environment_admission_missing` (the dangling
  quarantined-never-replaced `mtadd-p2048o0128-r08` was NOT excluded),
  `neg8_bracket_missing` + `neg8_bracket_reference_invalid` +
  `neg8_drift_bound_stale` (evaluated against the bound minted
  IN-WINDOW at `runs_window_metrologyB_20260801_bound/neg8-drift-bound.json`);
  the recorded supersession (mtnull-o0512-b04-b2, entry 3896c5ed…) was
  NOT consumed (`occurrence_supersessions` empty).

## The three question groups (the audit's scope)

(a) **Dangling quarantined-without-replacement occurrences.** A window
that salvage-closes leaves a quarantined slot with no replacement run.
Window A's verdict EXCLUDED the dangler and still failed the window on
it; window B's verdict did not exclude its dangler at all
(`excluded_bundles` empty) and raised `environment_admission_missing`.
Which behavior (if either) is the contract's? Is there a defined
semantic for a §10-quarantined, never-replaced occurrence at
whole-window verdict time, or is this an unhandled case?

(b) **Deviation-retry post-cal selection.** Window A's post-cal
attempt 1 FAILED (preserved 20260731T214355-126fc2ab) and ONE settled
retry ran under an a10-precedent RECORDED DEVIATION
(20260731T215120-fa1e9cda, valid). The bracket selector returned
pre=null AND post=null — it refused to form a bracket rather than
consuming the valid retry (and note pre-cal 20260731T161713-b8b08280
exists and passed §5B, so even pre=null needs explaining). Window B's
selector consumed its single-attempt pair fine. What selection rule is
implemented, why did it null BOTH sides for A, and what is the
contract-true rule for failed-then-retried calibration attempts?

(c) **Window B's membership resolution.** Why did
`source_campaign_manifests` resolve EMPTY over a four-chain-segment
window with a populated `campaign_manifests/` dir? Trace the actual
resolution path (glob/pattern/schema filter/chain-segment naming).
Downstream: with membership unresolved, the recorded supersession was
not consumed and NEG-8 evaluated missing/invalid/stale — are those
independent defects or pure cascade? Also rule on
`neg8_drift_bound_stale`: the bound was minted IN-WINDOW (fresher than
any 24 h requirement) — is "stale" a mis-evaluation, a clock/anchor
comparison bug, or correct-per-contract-but-misnamed?

## Evidence pointers (all inside this repo checkout)

- Verdict rows: last line of each `campaign_log.jsonl` (paths above);
  earlier lines are member/supersession records.
- Close-out narratives: `.desk/adjudication_packet_20260801/close-out-windowA.md`
  and `close-out-windowB.md` (copies of the custody originals).
- Machinery: `joulewise/whole_window.py`, `scripts/run_campaign.py`
  (`--whole-window-verdict` path), `joulewise/analysis_engine/inputs.py`
  (cooldown join / supersession reader), calibration-bracket selection
  code (search for `calibration_bracket`), NEG-8 bracket evaluation
  (search `neg8`).
- Policy: `configs/campaign_policies/quiet_mac_p2_production.json`.
- Bound roots: `runs_window_metrologyA_20260731_bound/`,
  `runs_window_metrologyB_20260801_bound/`.
- Contract/doctrine: `docs/decision_log.md` D-088/D-093/D-094/D-097;
  `docs/run_reports/2026-08-01-metrology-window-b.md`.

## Deliverable

Per question group: (1) the machinery's ACTUAL behavior, traced to
specific code paths (file:line); (2) whether that behavior implements
the written contract, with the contract source cited; (3) verdict-shaped
classification — MACHINERY DEFECT (mis-rules salvage windows) /
CONTRACT GAP (case genuinely undefined) / CORRECT (verdict right,
expectations wrong); (4) if defect or gap: the minimal contract-true
repair, sized (bench-scale vs delegated commit), and whether a re-run
verdict after repair could change either window's outcome. Flag
anything that would ALSO mis-rule non-salvage windows (severity
escalator). Do not propose any override of the as-issued verdicts —
that path is cold-gate-only.
