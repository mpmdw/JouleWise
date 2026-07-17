# Stream ledger — Window A advisor brief (2026-07-17)

Scope: build the meeting deliverable at
`docs/advisor_briefs/2026-07-17-window-a-brief.html` from the pinned skeleton,
verified floor extraction, current decision/state records, and AXI feasibility
verdicts. No campaign, hardware, site deployment, or claim adjudication work.

## ABRIEF-1 — Preserve the verified bundle-accounting correction

Decision: the requested shorthand “248 strict-valid floor bundles” is not used
as a factual headline because the independent NEG-8 verification in
`docs/process_traces/2026-07-17-floor-extraction/extraction-verified.json`
establishes 248 campaign-log lines, 222 distinct bundle directories, 17 resumed
skip rows, and 9 campaign-verdict rows. The brief leads with “222 distinct
strict-valid floor bundles” and explains the correction in the hero and footer.

Evidence: extraction `result.extractions[3].notes` and
`result.verifications[3].details`; `runs/p2_015_floors_window_a/campaign_log.jsonl`.

## ABRIEF-2 — Treat floors as calibrated refusal thresholds, not claims

Decision: floor values are shown exactly from the verified extraction (rounded
only for display), while the following remain visually prominent caveats:

- all 222 distinct bundles are strict-valid and collection-usable but also
  claim-evidence-flagged;
- request-window L2/L3 precheck awaits P2-037/P2-039 adjudication;
- optional block 08 has zero rows, so no long-request floor exists;
- request and phase ABBA tails show drift/ordering structure;
- suite b01/b02 has a six-member low-energy regime that drives comparative
  floors to roughly 15× absolute;
- short prefill is `not_resolvable_sample_count` and smoke-only;
- NEG-8 is an n=2 drift diagnostic, not a campaign floor;
- the four independent verification families are `confirmed`, with no numeric
  discrepancies and only minor prose-precision findings.

Evidence: every extraction family’s `notes` plus every verification family’s
`details` in the verified JSON.

## ABRIEF-3 — Use a fixed, validated chart grammar

Decision: charts use the reference palette’s first two categorical slots in
their fixed order (absolute = slot 1 blue; comparative = slot 2 green), with
the documented light/dark steps. The project timeline uses one blue sequential
ramp; mechanism state uses the fixed status palette with icon + text labels.
Every plot has one quantitative axis, thin marks, two-pixel series separation,
selective direct labels, a legend for multi-series plots, and bundle citations
in hover tooltips plus visible evidence footnotes. The floor overview uses a
log-J axis to retain the 0.026694–24.618735 J range without dropping the small
request cells.

Evidence: reference palette at
`/private/tmp/claude-501/bundled-skills/2.1.212/c6ab550d45b012db9fda86f2d6b8796b/dataviz/references/palette.md`;
validator commands are recorded in the implementation return.

## ABRIEF-4 — Keep mechanism verdicts at their evidence ceiling

Decision: AXI-SB is presented as live runtime-feasibility support, not energy
evidence. AXI-SC is an honest `unsupported_for_joulewise` result on pinned
mlx-lm: external draft lacks complete event observability and native MTP lacks
an execution surface, so no Mac energy leg is minted. DSpark/DFlash are a
separate planned mechanism path with C5-2.5a–d draft rows and a dedicated
environment requirement. Native MTP remains gated.

Evidence:
`docs/specs/axi/sb_static_batch_verdict.md`,
`docs/specs/axi/sc_spec_decode_verdict.md`, and
`docs/process_traces/2026-07-17-extension-axes/axes-evaluations.json`.

## Verification record

- HTML parser / structural inspection: section order 1–7, sections 4/5 native
  collapsibles, section 7 checklist, one inline style block, one inline script,
  no external resource URL or network API.
- JavaScript syntax: inline script extracted to a temporary file and checked
  with `node --check`.
- Palette: light and dark categorical steps checked with the required
  `validate_palette.js` commands.
- Rendered browser inspection was attempted, but the in-app browser runtime
  reported no available browser backend; this is a nonblocking visual-QA gap,
  not a structural or runtime-script failure.
- Repository diff: only the HTML deliverable and this ledger are authorized.
- No git commit requested or created.
