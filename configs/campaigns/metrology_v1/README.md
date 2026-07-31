# Metrology v1 campaign suite

This suite characterizes the measurement instrument for paper claims C1-C5. It
does not gate a scientific claim, introduce a model, or mint a detection floor.
The program reuses its two already-characterized stacks; the runnable metrology
members here use the frozen Qwen2.5-1.5B MLX stack and the existing window
reference/bound corpus uses that same reference stack.

The five draft plans are deterministic and must be magistrate-ratified before
measurement. `micro_delta/k0064` is only a DRAFT-PENDING-SLOPE placeholder.

## Evidence roots

Each campaign writes beneath its exact `--runs-dir` root:

| Campaign | Evidence root | Campaign log |
| --- | --- | --- |
| `linearity_ramp` | `runs/metrology_v1/linearity_ramp` | `runs/metrology_v1/linearity_ramp/campaign_log.jsonl` |
| `null_ladder` | `runs/metrology_v1/null_ladder` | `runs/metrology_v1/null_ladder/campaign_log.jsonl` |
| `additivity_shapes` | `runs/metrology_v1/additivity_shapes` | `runs/metrology_v1/additivity_shapes/campaign_log.jsonl` |
| `micro_delta` | `runs/metrology_v1/micro_delta` | `runs/metrology_v1/micro_delta/campaign_log.jsonl` |
| `long_holds` | `runs/metrology_v1/long_holds` | `runs/metrology_v1/long_holds/campaign_log.jsonl` |

The campaign READMEs give the exact command for every stage. Governed
extraction invocations must pass an ABSOLUTE `--runs-dir` and an explicit
`--evaluation-basis-sha256`; these are tool-contract requirements, not
optional conveniences.

The governed 3+1+3 window references and 12-member NEG-8 in-window bound corpus
are supplied by `configs/campaigns/window_references/` and
`configs/campaigns/neg8_reference_corpus/`. They are not science stages in
these campaign directories.

## Window packing

- Metrology window A (~2.8 h): `linearity_ramp` + `additivity_shapes` +
  `null_ladder` stage `02_null_o0512` + long-holds Part A =
  3727+2257+1842+319 = 8145 s = 2.26 h science, plus 3+1+3 window references
  (~11 min) and the 12-member NEG-8 in-window bound corpus (~19 min) =
  ~2.76 h. FITS one ~3 h window.
- Metrology window B (~3.1 h, TIGHT): `null_ladder` stages 01 + 03
  (1810+1964 = 3774 s) + `micro_delta` three k slots (~5535 s) = 9309 s =
  2.59 h + references/corpus 30 min = ~3.09 h. RECOMMEND moving one k slot
  to window C.
- Window C: long-holds Part B (25 min incl. the extended-idle members) + the
  third `micro_delta` k slot + stability repeat + spillover.

## OPEN QUESTIONS FOR RATIFICATION

- All characterization cells use `use_role: staleness_sentinel`, the spec's
  first-choice non-claim vocabulary. The calibration-plan document has no
  active schema validator for this literal, so ratification must confirm it.
- Non-micro plans use `freeze_status:
  draft_pending_magistrate_ratification`; `micro_delta` uses
  `draft_pending_slope`. These are deliberate draft literals, not frozen-plan
  claims.
- Cell kinds and modular family IDs follow the campaign READMEs. The plan-level
  multi-family `stack_scope.condition_families` list is a descriptive extension
  of the single-family 7B shape and needs ratification before consumption by a
  future plan validator.
