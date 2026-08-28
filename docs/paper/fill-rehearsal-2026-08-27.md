# Round-7 results-fill rehearsal — 2026-08-27

This rehearsal asks the renderer to read synthetic files with the same schema names and the same role bindings it expects from the real alpha and beta campaigns: a whole-window verdict says whether the complete campaign passed its admission checks, a floor mint holds one prompt-processing cell and one token-generation cell, and an extraction report supplies each cell's absolute and comparative components. The larger component is that cell's operative floor. The role manifest connects those files without guessing their final identifiers. The renderer either writes one complete guarded prose choice to standard output and nothing to standard error, or writes no prose and prints one `STOP_FILL` record to standard error. The files here are conspicuously synthetic and are not measurement evidence.

## Exact round-7 command sequence with real artifacts

The named inputs force this sequence: the two whole-window verdicts license reading the two floor mints and two extraction reports; those six artifacts feed the renderer; a successful renderer output feeds the independent rendered-prose validator. The gamma claim verdict and characterization report are named because the registry needs them, but input schema `joulewise.results_fill_input.v1` has no usable gamma binding and no characterization-report binding. They therefore remain hand-fill inputs until that contract changes.

```text
alpha verdict + alpha floor mint + alpha extraction ─┐
                                                     ├─ role manifest ─ renderer ─┬─ stdout prose ─ validator
beta verdict  + beta floor mint  + beta extraction ─┘                            └─ stderr STOP_FILL
gamma claim verdict ──────────────────────────────── hand fill (not consumed by manifest v1)
characterization report ─────────────────────────── hand fill (manifest v1 accepts only its verdict)
```

Replace every `/ABSOLUTE/...` value and every `REPLACE-WITH-ISSUED-*` identifier with the issued round-7 path or identifier named by the variable. `REAL_FILL_DIR` is the evidence directory that retains the manifest, renderer output, error output, and validator output together. Do not substitute a historical artifact.

```sh
export JOULEWISE_REPO=/Users/edr/code/JouleWise
export REAL_FILL_DIR=/ABSOLUTE/round-7-fill-custody
export REAL_FILL_MANIFEST="$REAL_FILL_DIR/results-fill-input.json"

export ALPHA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/alpha/whole-window-verdict.json
export ALPHA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/alpha/aggregate-floor-artifact.json
export ALPHA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/alpha/detection-floor-extraction.json
export ALPHA_PROMPT_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-CELL-ID
export ALPHA_PROMPT_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-ABS-ID
export ALPHA_PROMPT_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-CMP-ID
export ALPHA_DECODE_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-CELL-ID
export ALPHA_DECODE_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-ABS-ID
export ALPHA_DECODE_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-CMP-ID

export BETA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/beta/whole-window-verdict.json
export BETA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/beta/aggregate-floor-artifact.json
export BETA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/beta/detection-floor-extraction.json
export BETA_PROMPT_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-CELL-ID
export BETA_PROMPT_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-ABS-ID
export BETA_PROMPT_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-CMP-ID
export BETA_DECODE_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-CELL-ID
export BETA_DECODE_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-ABS-ID
export BETA_DECODE_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-CMP-ID

export GAMMA_CLAIM_VERDICT=/ABSOLUTE/gamma/claim-verdicts.json
export CHARACTERIZATION_WHOLE_WINDOW_VERDICT=
export CHARACTERIZATION_RESULT_REPORT=
mkdir -p "$REAL_FILL_DIR"

PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

def campaign(prefix):
    return {
        "verdict": os.environ[f"{prefix}_WHOLE_WINDOW_VERDICT"],
        "floor_artifact": os.environ[f"{prefix}_AGGREGATE_FLOOR_MINT"],
        "extraction": os.environ[f"{prefix}_DETECTION_FLOOR_EXTRACTION"],
        "cells": {
            "prompt": {
                "floor_cell_id": os.environ[f"{prefix}_PROMPT_FLOOR_CELL_ID"],
                "absolute_extraction_cell_id": os.environ[f"{prefix}_PROMPT_ABSOLUTE_EXTRACTION_CELL_ID"],
                "comparative_extraction_cell_id": os.environ[f"{prefix}_PROMPT_COMPARATIVE_EXTRACTION_CELL_ID"],
            },
            "decode": {
                "floor_cell_id": os.environ[f"{prefix}_DECODE_FLOOR_CELL_ID"],
                "absolute_extraction_cell_id": os.environ[f"{prefix}_DECODE_ABSOLUTE_EXTRACTION_CELL_ID"],
                "comparative_extraction_cell_id": os.environ[f"{prefix}_DECODE_COMPARATIVE_EXTRACTION_CELL_ID"],
            },
        },
    }

characterization_verdict = os.environ["CHARACTERIZATION_WHOLE_WINDOW_VERDICT"] or None
manifest = {
    "schema_version": "joulewise.results_fill_input.v1",
    "campaigns": {"alpha": campaign("ALPHA"), "beta": campaign("BETA")},
    "gamma": None,
    "characterization": {
        "funded": characterization_verdict is not None,
        "run": characterization_verdict is not None,
        "verdict": characterization_verdict,
    },
}
Path(os.environ["REAL_FILL_MANIFEST"]).write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY

set +e
PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \
  "$JOULEWISE_REPO/scripts/render_results_fills.py" "$REAL_FILL_MANIFEST" \
  > "$REAL_FILL_DIR/rendered-results.md" \
  2> "$REAL_FILL_DIR/rendered-results.stderr.txt"
render_exit=$?
printf 'render exit=%s\n' "$render_exit"
if [ "$render_exit" -eq 0 ]; then
  PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python \
    "$JOULEWISE_REPO/scripts/render_results_fills.py" \
    --validate-rendered "$REAL_FILL_DIR/rendered-results.md" \
    > "$REAL_FILL_DIR/validate-results.stdout.txt" \
    2> "$REAL_FILL_DIR/validate-results.stderr.txt"
  validate_exit=$?
  printf 'validate exit=%s\n' "$validate_exit"
else
  sed -n '1p' "$REAL_FILL_DIR/rendered-results.stderr.txt"
fi
```

## Marker-site outcomes

The renderer is atomic: a later stop discards all earlier authenticated fills, so the two complete-floor runs wrote zero bytes. `STOP-B` below is the exact line both runs printed:

```text
STOP_FILL {"label": "SUPPLIER_UNKNOWN", "reason": "the registry freezes this token but defines no producing artifact field", "registry_row": "[B_decode_claim_J]"}
```

`STOP-U(token)` is the same renderer rule with the named registry token—a bracketed key such as `[E_1p5B_prompt_J_per_request]`: `STOP_FILL {"label": "SUPPLIER_UNKNOWN", "reason": "the registry freezes this token but defines no producing artifact field", "registry_row": "token"}`. A supplier is the exact issued artifact field or frozen calculation that authorizes one fill. The claim-side bound is the separately registered non-floor quantity `B` in the disclosure `F+B`; it is not the complete deterministic-bound total. `NOT-EXERCISED-BY-RENDERER` means input schema v1 has no route from the named artifact field to that physical draft site; it is not a successful fill.

| Variant | Render exit | Rendered outputs | STOP_FILL outputs | Validate exit | Observed result |
|---|---:|---:|---:|---:|---|
| dominance reproduced | 2 | 0 | 1 | not run | `STOP-B`; stdout 0 bytes |
| dominance not reproduced | 2 | 0 | 1 | not run | `STOP-B`; stdout 0 bytes |
| both floor windows refused | 0 | 1 | 0 | 0 | §7 C3 + §6 0; validator PASS |
| characterization refused | 2 | 0 | 1 | not run | `VALUE_UNISSUED` at `[D_C_linearity_diagnostic_J_per_token]`; stdout 0 bytes |

The next table has one row per marker-bound registry row. PG-02 and PG-03 share one physical interval marker; DS-26 has one interval marker holding two semantic values. Actual lines were found by searching each row anchor in the frozen draft.

| Registry row | Draft line and marker | Supplier | Dominance reproduced | Dominance not reproduced |
|---|---|---|---|---|
| DS-01 | 189, `[RESULT PENDING ISSUED ARTIFACTS]` | alpha/beta floor mints and extractions | STOP-B | STOP-B |
| DG-071 | 256, first diagnostic `[PENDING]` | declared interval-width statistic in an issued diagnostic artifact | NOT-EXERCISED-BY-RENDERER: manual diagnostic row | same |
| DG-075 | 256, second diagnostic `[PENDING]` | declared median-spacing statistic in an issued diagnostic artifact | NOT-EXERCISED-BY-RENDERER: manual diagnostic row | same |
| DS-08a | 274, `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]` | one complete guarded template choice | STOP-B | STOP-B |
| DS-09 | 280, prompt/1.5B gross `[PENDING]` | alpha prompt mean + interval | STOP-U(`[E_1p5B_prompt_J_per_request]`) | same |
| DS-10 | 280, prompt/1.5B per-token `[PENDING]` | alpha prompt reported-mean companion | STOP-U(`[E_1p5B_prompt_J_per_token]`) | same |
| DS-11 | 280, prompt/1.5B floor `[PENDING]` | alpha prompt operative floor | STOP-B | STOP-B |
| DS-12 | 280, prompt/1.5B count `[PENDING]` | alpha prompt admitted-bundle count | STOP-U(`[N_bundles_1p5B_prompt]`) | same |
| DS-13 | 281, prompt/7B gross `[PENDING]` | beta prompt mean + interval | STOP-U(`[E_7B_prompt_J_per_request]`) | same |
| DS-14 | 281, prompt/7B per-token `[PENDING]` | beta prompt reported-mean companion | STOP-U(`[E_7B_prompt_J_per_token]`) | same |
| DS-15 | 281, prompt/7B floor `[PENDING]` | beta prompt operative floor | STOP-B | STOP-B |
| DS-16 | 281, prompt/7B count `[PENDING]` | beta prompt admitted-bundle count | STOP-U(`[N_bundles_7B_prompt]`) | same |
| DS-17 | 282, decode/1.5B gross `[PENDING]` | alpha decode mean + interval | STOP-U(`[E_1p5B_decode_J_per_request]`) | same |
| DS-18 | 282, decode/1.5B per-token `[PENDING]` | alpha decode reported-mean companion | STOP-U(`[E_1p5B_decode_J_per_token]`) | same |
| DS-19 | 282, decode/1.5B floor `[PENDING]` | alpha decode operative floor | STOP-B | STOP-B |
| DS-20 | 282, decode/1.5B count `[PENDING]` | alpha decode admitted-bundle count | STOP-U(`[N_bundles_1p5B_decode]`) | same |
| DS-21 | 283, decode/7B gross `[PENDING]` | beta decode mean + interval | STOP-U(`[E_7B_decode_J_per_request]`) | same |
| DS-22 | 283, decode/7B per-token `[PENDING]` | beta decode reported-mean companion | STOP-U(`[E_7B_decode_J_per_token]`) | same |
| DS-23 | 283, decode/7B floor `[PENDING]` | beta decode operative floor | STOP-B | STOP-B |
| DS-24 | 283, decode/7B count `[PENDING]` | beta decode admitted-bundle count | STOP-U(`[N_bundles_7B_decode]`) | same |
| DS-25 | 289, decode point `[PENDING]` | gamma decode estimate | STOP-B | STOP-B |
| DS-26 | 289, decode interval `[PENDING, PENDING]` | gamma decode decision-interval endpoints | STOP-B | STOP-B |
| DS-27 | 289, decode floor `[PENDING]` | maximum of alpha/beta decode floors | STOP-B | STOP-B |
| DS-28 | 289, decode sizing sum/clearance `[PENDING]` | gamma magnitude, floor, and claim-side bound | NOT-EXERCISED-BY-RENDERER: draft/template shape mismatch | same |
| DS-29 | 289, decode claim-side bound `[PENDING]` | no producing field | STOP-B | STOP-B |
| DS-30 | 289, decode floor outcome `[PENDING]` | missing conservative-render token | NOT-EXERCISED-BY-RENDERER: token missing | same |
| DS-31 | 289, decode direction outcome `[PENDING]` | missing conservative-render token | NOT-EXERCISED-BY-RENDERER: token missing | same |
| DS-32 | 289, decode verdict `[PENDING]` | missing professor-facing verdict token | NOT-EXERCISED-BY-RENDERER: token missing | same |
| DS-33 | 290, prompt floor `[PENDING]` | missing prompt claim-floor token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| DS-34 | 348, `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | release-manifest repository/archive locators | NOT-EXERCISED-BY-RENDERER: release checklist is outside input v1 | same |
| PG-01 | 290, prompt point `[PENDING]` | missing gamma prompt estimate token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| PG-02 | 290, prompt interval `[PENDING, PENDING]`, lower | missing gamma prompt lower-endpoint token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| PG-03 | 290, same interval marker, upper | missing gamma prompt upper-endpoint token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| PG-04 | 290, prompt sizing sum/clearance `[PENDING]` | missing prompt branch and claim-bound fields | NOT-EXERCISED-BY-RENDERER: token family and shape contract missing | same |
| PG-05 | 290, prompt claim-side bound `[PENDING]` | no named claim-side-bound field | NOT-EXERCISED-BY-RENDERER: supplier and token missing | same |
| PG-06 | 290, prompt floor outcome `[PENDING]` | missing conservative-render token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| PG-07 | 290, prompt direction outcome `[PENDING]` | missing conservative-render token | NOT-EXERCISED-BY-RENDERER: token family missing | same |
| PG-08 | 290, prompt verdict `[PENDING]` | missing authenticated verdict token | NOT-EXERCISED-BY-RENDERER: token family missing | same |

Per complete-floor variant, the 38 registry rows therefore contain **0 RENDERED, 22 STOP_FILL, and 16 NOT-EXERCISED-BY-RENDERER** outcomes. This count is by registry row, not physical marker: PG-02 and PG-03 share one marker.

## Sites with no renderer supplier

- DG-071 and DG-075 need a declared statistic and an issued diagnostic artifact. The desk values in the registry are not issuances and cannot be copied.
- DS-09, DS-10, DS-12 through DS-14, DS-16 through DS-18, DS-20 through DS-22, and DS-24 need the D-123 reported-mean artifact: point estimate, composed endpoints, authenticated per-token companion, and admitted independent-bundle count for each alpha/beta phase cell.
- DS-29 needs the decode claim-side bound. DS-28 then needs one explicit rendering that contains both `F+B` and signed clearance; neither the complete deterministic-bound total nor floor-only clearance may be substituted.
- DS-30 through DS-32 need bound tokens for the decode floor outcome, direction outcome, and conservative verdict.
- DS-33 and PG-01 through PG-08 need the complete gamma prompt token family: estimate, interval endpoints, claim floor, sizing sum and signed clearance, claim-side bound, both gate outcomes, and verdict.
- DS-34 must be supplied by the release checklist's repository commit, archive locator, and published fingerprint manifest.
- The held paper title and the sixteen TERM A/TERM B dominance rows are manual round-7 derivations. They are not physical bracket markers and input v1 never evaluates them; the item-34 replay fence must derive them before the title is chosen.

## Defects and agreement findings

1. Input v1 is a guarded-template renderer, not an in-place draft renderer. Even a successful run emits only one §7 template choice followed by one §6 template choice. A human or a future program still has to map that output into the frozen draft's Section 6 sites.
2. Both complete-floor variants reach the deliberate `[B_decode_claim_J]` guard and stop. This agrees with the registry; it is not a renderer defect. It proves that all four alpha/beta cell bindings loaded and passed before the first unresolved claim-bound field stopped the atomic render.
3. `gamma` is accepted but ignored, and the manifest examples set it to `null`. The renderer cannot read the real gamma claim verdict, so decode contrast cells and the entire live prompt arm cannot be filled end to end.
4. Characterization input carries only a whole-window verdict path. It has no path for the issued characterization result report whose row fields the registry names. The refusal rehearsal stops at `[D_C_linearity_diagnostic_J_per_token]` exactly as coded.
5. DS-28 and PG-04 now point mechanically to the current `Sizing sum F+B; signed clearance` header, but their bindings still describe clearance or shortfall alone. One placeholder must encode two disclosed quantities; that semantic shape mismatch remains unfixed.
6. The registry's current-draft note says 533 lines; `wc -l` measured 672. Marker row lines 189, 256, 274, 280–283, 289–290, and 348 are current despite that stale narrative count.
7. Mechanical locator repairs made here: DG-071 `no line → 256`; DG-075 `no line → 256`; DS-02 `\| Workload response \| → **Workload response:**`; DS-03 internal `line 125 → 95`; DS-05 `\| Phase accounting \| → **Phase accounting:**`; DS-06 `\| Drift and recovery \| → **Drift and recovery:**`; DS-29 `no line → 289`; PG-05 `no line → 290`; DS-28 and PG-04 headings changed from the absent clearance heading to the current sizing-sum heading. No marker bytes or supplier rules changed.
8. The exact-token tables contain 109 rows: all 91 template tokens, sixteen dominance-term rows that have no template counterpart, and two swap-block-only rows. The census prose's “91 exact template-token rows plus 42 draft-site rows” does not state the sixteen extra dominance rows.

No blocking renderer defect was found, so `scripts/render_results_fills.py` and its tests were not changed.

## Census recount

This is the registry's recorded literal-`PENDING` recount, including its rule that a comma means two semantic slots:

```sh
grep -oE '\[PENDING[^]]*\]' docs/paper/draft-v1.md \
  | awk '{ sites += 1; slots += (index($0, ",") ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
```

Observed: `sites=34 slots=36`. The registry's recorded marker-row command printed `35`:

```sh
grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[PENDING' docs/paper/results-fill-registry.md
```

That command excludes the three other registered pending-family markers at DS-01, DS-08a, and DS-34. Recounting all three allowed prefixes printed `sites=37 slots=39`, and the parallel all-prefix registry-row command printed `38` because PG-02 and PG-03 share one marker:

```sh
grep -oE '\[(PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]' docs/paper/draft-v1.md \
  | awk '{ sites += 1; slots += ($0 ~ /^\[PENDING,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[(PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' docs/paper/results-fill-registry.md
```

The registry's **34 sites / 36 slots** is correct only for markers whose bytes begin with `[PENDING`; it is not the count of every pending-family marker the registry itself defines.
