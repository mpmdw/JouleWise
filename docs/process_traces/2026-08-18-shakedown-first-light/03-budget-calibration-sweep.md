```json
{"schema":"claude-codex-report/v1","genre":"scout","status":"findings","completion":"complete","summary":"Recommend a 165,000-cell detector budget: the complete retained unique v3 corpus has a 137,189-cell maximum across 34 full 59-pulse replays.","workspace":{"base_requested":null,"base_mode":null,"head_start":"a3c5c9c252b83f00c8ef2f14721c75820334e765","head_end":"a3c5c9c252b83f00c8ef2f14721c75820334e765","upstream_end":"62c6a0687c1bb1fe6183d70bb23dd6b1c095c27b","branch":"integration/phase2-transaction"},"pathspec":[],"unowned_dirty":[],"verdict":{"recommendation":{"budget_cells":165000,"margin_cells":27811,"margin_pct_of_observed_max":20.3},"census":{"unique_raw_v3_bundles":40,"raw_locations":56,"issued_n19_raw_retained":19,"full_convergences":34,"anchor_unresolved":6},"distribution":{"min":112205,"median":122044,"max":137189,"p95":135513},"rows":[{"action":"needs_ruling","subject":"detector budget","recommendation":"Adopt 165000 cells in the governed Phase-2 transaction; it exceeds the observed maximum by 27811 cells, more than the full observed min-to-max spread."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"enumerate /Users/edr/code/JouleWise/runs* plus /Users/edr/JouleWise-window-custody/*/runs and every D-079 ledger custody_locator","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["40 unique v3 bundles; 56 retained locations; 19/19 issued members retain raw artifacts"]},"expected":{"exit_code":0,"tail_regex":"40 unique v3 bundles"}},{"id":"V2","kind":"smoke","cmd":"in-memory lifted-budget rederive_detection_from_artifacts(raw/powermetrics.plist, events.jsonl, instrument_evidence.json[clock_anchor]) for every unique raw v3 identity","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["34 full 59-pulse convergences; min=112205 median=122044 max=137189","6 bundles refused before fitting: calibration trace anchor is unresolved"]},"expected":{"exit_code":0,"tail_regex":"34 full 59-pulse convergences"}},{"id":"V3","kind":"inspection","cmd":"compare checkout/archive SHA-256 values for raw/powermetrics.plist, events.jsonl, and instrument_evidence.json","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["16 shared raw bundles; 16 byte-identical artifact sets; mismatches=[]"]},"expected":{"exit_code":0,"tail_regex":"mismatches=\\[\\]"}}],"flags":[{"id":"F1","kind":"residual_risk","level":"nonblocking","text":"The 165000 recommendation is calibrated to all currently retained unique v3 traces, not an unobserved future trace class; six anchor-unresolved bundles cannot supply a 59-pulse work count.","needs":"Recalibrate on any new protocol/identity/cadence class."}]}
```

## Recommended parameter ruling

Adopt `DETECTION_PROJECTION_CELL_BUDGET = 165_000`.

The complete retained set reaches **137,189 cells**. A 165,000-cell limit adds **27,811 cells (20.3%)** of explicit headroom—more than the entire observed 24,984-cell min-to-max spread. `150,000` would leave only 12,811 cells / 9.3% above the observed maximum.

The converged distribution is **n=34**: min **112,205**, median **122,044**, p95 **135,513**, max **137,189**. Six additional raw bundles fail before fitting because their raw bytes cannot re-derive the recorded clock anchor, so they have no valid 59-pulse convergence count.

Census: 40 unique raw-bearing v3 identities across 56 retained locations. The referenced iCloud archive contains all **19/19** D-079 issued derivation-corpus members and all 38 ledger finalizations; checkout copies duplicate 16 of those identities, adds one unledgered Metrology-A trace, and custody adds the shakedown.

| Bundle | Canonical root | Result | Cells | Peak pulse cells | Median SNR |
|---|---|---:|---:|---:|---:|
| 20260722T145535-e941c821 | archive/runs-20260727 | 59/59 | 117669 | 36:3515 | 42263 |
| 20260722T194118-9dc0749d | archive/runs-20260727 | 59/59 | 122431 | 9:5023 | 41591 |
| 20260722T213749-563b9849 | archive/runs-20260727 | anchor unresolved | — | — | — |
| 20260722T214220-1acdbbc0 | archive/runs-20260727 | 59/59 | 119273 | 17:3617 | 41788 |
| 20260722T215127-eeef661a | archive/runs-20260727 | 59/59 | 119631 | 46:3391 | 41485 |
| 20260722T222332-901c5c13 | archive/runs-20260727 | 59/59 | 123575 | 9:3399 | 41174 |
| 20260722T232509-82642517 | archive/runs-20260727 | 59/59 | 122023 | 16:4477 | 41605 |
| 20260723T023058-8732d1c9 | archive/runs-20260727 | 59/59 | 122313 | 22:5471 | 41486 |
| 20260723T052051-d9358c8a | archive/runs-20260727 | 59/59 | 121811 | 18:3375 | 41958 |
| 20260723T183306-4ce692b4 | archive/runs-20260727 | 59/59 | 116173 | 10:3431 | 41587 |
| 20260723T194632-d04e038e | archive/runs-20260727 | 59/59 | 128607 | 41:3725 | 41749 |
| 20260723T195730-bc4ba14a | archive/runs-20260727 | 59/59 | 121443 | 40:4047 | 41946 |
| 20260723T221449-e9ae755e | archive/runs-20260727 | 59/59 | 117043 | 2:5291 | 41305 |
| 20260723T223406-314f6d9e | archive/runs-20260727 | 59/59 | 124447 | 38:3573 | 41798 |
| 20260724T014109-57844352 | archive/runs-20260727 | 59/59 | **137189** | 45:4843 | 41656 |
| 20260725T005132-a64711b7 | archive/window-a9 | 59/59 | 119891 | 10:4863 | 40921 |
| 20260725T011533-0b5ec77c | archive/window-a9 | 59/59 | 119055 | 31:3875 | 41113 |
| 20260725T022712-0a9534f5 | archive/window-a9 | 59/59 | 119479 | 31:3323 | 41270 |
| 20260725T030533-d3f076e5 | archive/window-a10 | 59/59 | 122065 | 36:3975 | 41907 |
| 20260725T055825-b10cb348 | archive/window-a10 | anchor unresolved | — | — | — |
| 20260725T060617-97c5cba6 | archive/window-a10 | 59/59 | 117563 | 41:4423 | 41554 |
| 20260726T000039-491995f3 | archive/window-b | 59/59 | 123267 | 15:3627 | 41243 |
| 20260726T031222-e0ce33f5 | archive/window-b | 59/59 | 122947 | 24:3793 | 41087 |
| 20260726T225227-1f550773 | archive/window-c | anchor unresolved | — | — | — |
| 20260726T225920-ab4272f5 | archive/window-c | 59/59 | 115197 | 30:3161 | 41634 |
| 20260727T015824-45feb516 | archive/window-c | 59/59 | 133883 | 23:5277 | 42012 |
| 20260727T020611-4a409a30 | archive/window-d | 59/59 | 126103 | 7:3855 | 41757 |
| 20260727T050047-95e2f87e | archive/window-d | 59/59 | 120551 | 5:3613 | 41050 |
| 20260729T204105-39d25f8a | archive/7bfloor | 59/59 | 129965 | 27:5377 | 41540 |
| 20260730T014035-124df355 | archive/7bfloor | 59/59 | 135513 | 23:5811 | 41425 |
| 20260730T210703-f76b5771 | archive/contrast | 59/59 | **112205** | 46:3769 | 40856 |
| 20260731T012210-374020b6 | archive/contrast | 59/59 | 122117 | 44:3345 | 41075 |
| 20260731T161713-b8b08280 | archive/metrologyA | 59/59 | 131065 | 6:5437 | 41116 |
| 20260731T214355-126fc2ab | archive/metrologyA | anchor unresolved | — | — | — |
| 20260731T215120-fa1e9cda | checkout/metrologyA | 59/59 | 117057 | 29:3717 | 3376 |
| 20260801T010113-e859f3aa | archive/metrologyB | anchor unresolved | — | — | — |
| 20260801T010805-ff3fdc88 | archive/metrologyB | anchor unresolved | — | — | — |
| 20260801T014059-8c3bfe9e | archive/metrologyB | 59/59 | 132861 | 11:5835 | 41558 |
| 20260801T064830-c76f5d1c | archive/metrologyB | 59/59 | 119223 | 35:4201 | 41133 |
| 20260818T045736-4d9e9db9 | custody/shakedown | 59/59 | 124029 | 54:3489 | 43029 |

Count versus median-SNR has only a weak Pearson relationship (`r=0.18`; still `r=0.18` excluding the 3,376-SNR Metrology-A outlier). All evidence declares the same 100 ms configured sampling interval, so that field cannot explain variance. The likely source is trace-grid/edge alignment: per-pulse projection peaks range from 3,161 to 5,835 cells despite similar SNR.

## Constant and D-138 impact

The current 100,000 constant is code, not registry/config: [powermetrics_fiducial.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/powermetrics_fiducial.py:81). It is used as the detector default at [line 902](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/powermetrics_fiducial.py:902).

Changing it changes one of D-138’s four authenticated estimator inputs. The consequence is not a simple parameter edit:

- Reissue the active D-079 acceptance artifact, updating its `estimator_code_sha256` pin ([r2 artifact](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/configs/calibration/calibration_acceptance_d079_v2_r2.json:39)).
- Update the dual-generation registry, successor identity, byte pin, and active default in [calibration_bracketing.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/calibration_bracketing.py:67).
- Preserve predecessor bytes and routing; ARM must continue recognizing both issued generations ([arm_readiness.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/joulewise/arm_readiness.py:4125)).
- Regenerate the three successor campaign pin surfaces: each `_v2` generator, `plan_tree.json`, `arm_readiness.sources/acceptance-owner.json`, and its acceptance-dependent source records; plus the two `_v2` floor-mint extraction specs.
- Update the corresponding exact-pin and stale-pin regressions. Do not re-key production tests to fixtures.

D-138 requires this to land only inside the atomic successor-family re-freeze with the acceptance reissue; it deliberately makes the acceptance artifact stale and forbids a standalone merge ([decision log](/private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/wtTXN/docs/decision_log.md:9877)).

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Detection budget | needs_ruling | Lead’s 165,000-cell parameter ruling | D-138 atomic re-freeze, D-079 r2 artifact and successor pack pins |

## Critical path

Parameter ruling → governed `powermetrics_fiducial.py` change → D-079 reissue and dependent-pin migration in the same atomic re-freeze.