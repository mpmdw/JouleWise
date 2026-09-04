# D165-OUTCOME-RENDERER-01 seat landing report

Date: 2026-09-04  
Seat: Sol xhigh implementation  
Base/head at intake: `9cab7f6eee5c13d50846b1af04c197ad39fb0789`  
Branch: `feat/2026-09-04-d165-outcome-renderer`

## Outcome

Implemented the pure OB-01 / OR-01 supplier in
`joulewise/results_fill_outcome.py`. The module performs no file I/O. It
reauthenticates a D-165 close-out against the exact finalized-manifest, floor,
and replay-sidecar byte strings through the landed
`validate_d165_closeout` validator. All malformed, incomplete,
unauthenticated, stage-conflicting, or precedence-less inputs return
`{"OB-01": "STOP_FILL", "OR-01": "STOP_FILL"}`.

The fixture family copies the existing D-165 test builders at runtime and
mutates only fresh copies. No original D-165 fixture or builder was edited.

## Field to string mapping

| Fill | Governed fields | Exact rendering rule |
|---|---|---|
| OB-01 ordinary | `independent_ratios[].{cell_id,component,passes}` | For every `passes == false` record, in artifact order: `<cell_id> <component>`. |
| OB-01 shared error | `comparative_common_mode_ratios[].{cell_id,component,passes}` | For every `passes == false` record, after the ordinary records and in artifact order: `<cell_id> comparative common-mode`. |
| OB-01 list | all false records above | One item verbatim; two joined by `and`; three or more comma-separated with Oxford `and`. A, Refusal, or an empty B failure set is `STOP_FILL`. |
| OR-01 before / window | normalized authenticated `whole_window_admission.{model,outcome,reason}` | `before comparison: <model> measurement window — <reason>`; `model` is closed to the fixed Qwen3 pair and `outcome` must be `excluded`. |
| OR-01 before / verdict | normalized authenticated `claim_evaluation.{verdict,outcome,reason}` | `before comparison: <verdict> verdict for the fixed Qwen3-8B-versus-Qwen3-1.7B pair — <reason>`; the pair appears only for an absent token-generation or prompt-processing verdict. |
| OR-01 close-out | close-out `.refusal_reason`; refused ratio record `.cell_id/.component`; authenticated manifest arm `floor_cell_id -> realized_stack_identity.model.name` | `at close-out: <model> (<cell_id> <component>) — <refusal_reason>`. No affected-record/model binding means `STOP_FILL`; the renderer does not invent one. |

Fixture-exact positive examples:

- OB-01: `synthetic-floor-0-0 absolute, synthetic-floor-0-0 comparative common-mode, synthetic-floor-0-1 comparative common-mode, synthetic-floor-1-0 comparative common-mode, and synthetic-floor-1-1 comparative common-mode`
- OR-01 window: `before comparison: Qwen3-1.7B measurement window — synthetic_window_excluded`
- OR-01 absent verdict: `before comparison: token-generation verdict for the fixed Qwen3-8B-versus-Qwen3-1.7B pair — required token-generation verdict absent`
- OR-01 close-out: `at close-out: Qwen2.5-1.5B-Instruct-4bit (synthetic-floor-0-0 absolute) — dominance_ratio_zero_denominator`

The Qwen2.5 name in the last line is fixture provenance copied from the landed
synthetic D-165 builder. Production names come from the authenticated
finalized-manifest arm; no model name is guessed from a cell id.

## Refusal and precedence behavior

- A complete 8+4 census is authenticated before either fill is considered.
- A supplied close-out with any changed source bytes stops both fills.
- Each normalized before-comparison record must carry an upstream
  `authenticated: true` attestation and a closed kind/outcome shape.
- A refusal requires the matching explicit precedence value: `before
  comparison` or `at close-out`.
- Inputs from both stages conflict and stop both fills even if one precedence
  value is supplied.
- Issued reasons are copied; ratio values never generate a reason or a public
  number.

## Successor import seam

`RENDERER-V5-SUCCESSOR-01` should import
`joulewise.results_fill_outcome.render_outcome_fills`, pass the parsed
close-out together with the exact three source byte strings, and adapt already
authenticated whole-window / missing-verdict evidence into the module's
closed normalized before-comparison records. The successor owns placement of
the returned `OB-01` / `OR-01` values and handling of `STOP_FILL`.

No seam was wired here. The frozen `scripts/render_results_fills.py` remains
untouched.

## Acceptance test and RED/GREEN

The single table-driven acceptance test covers A, B (one ordinary and four
common-mode failures), an excluded model window, an absent Qwen-pair verdict,
a zero-denominator close-out refusal, all named fail-closed cases, and the
required mutation that removes one A-fixture census record.

RED, before the production module existed:

```text
ModuleNotFoundError: No module named 'joulewise.results_fill_outcome'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN, final permitted suite:

```text
................................................
----------------------------------------------------------------------
Ran 48 tests in 9.880s

OK
```

Replay command:

```text
python3 -m unittest tests.test_results_fill_outcome tests.test_d165_dominance_closeout
```

The repository-wide suite was intentionally not run: the prompt's preflight
rule limited tests to the new acceptance module and the existing D-165
close-out module found by grep.
