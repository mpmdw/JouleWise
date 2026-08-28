# Round-7 results-fill rehearsal — 2026-08-27

This rehearsal asks the renderer to read synthetic files with the same schema names and the same role bindings it expects from the real alpha and beta campaigns: a whole-window verdict says whether the complete campaign passed its admission checks, a floor mint holds one prompt-processing cell and one token-generation cell, and an extraction report supplies each cell's absolute and comparative components. The larger component is that cell's operative floor. The role manifest connects those files without guessing their final identifiers. The renderer either writes one complete guarded prose choice to standard output and nothing to standard error, or writes no prose and prints one `STOP_FILL` record to standard error. The files here are conspicuously synthetic and are not measurement evidence.

## (ii) Exact round-7 command sequence with real artifacts

Glossary for this procedure:

- **Alpha** is the 1.5B floor campaign; **beta** is the 7B floor campaign; **gamma** is the 1.5B-versus-7B contrast campaign. Alpha and beta each supply prompt-processing and token-generation floors; gamma supplies the two model contrasts.
- A **whole-window verdict** is the issued accept-or-refuse record for every declared member and environmental check in one complete window.
- An **aggregate floor mint** is the issued JSON artifact that joins the absolute and comparative floor components and publishes their larger value as each cell's operative floor.
- An **extraction** is the governed report that reads authenticated run bundles and derives the component floors used by the mint.
- An **issued cell ID** is the exact `cell_id` written by an issuer into a floor mint or extraction. It is copied into the role manifest; an operator never invents it from a model or phase name.
- A **custody directory** is a new, non-overwritten directory that keeps the manifest, renderer outputs, and check outputs together.
- The **registry** is `docs/paper/results-fill-registry.md`: the one table that binds every bracket marker in the frozen draft to the artifact field that may fill it and the rule for doing so. A marker absent from the registry cannot be filled.
- A **pinset** is the JSON file that pins, by path and SHA-256, every input a floor mint is allowed to read; the mint refuses inputs outside it, so the round-7 operator passes the pinset frozen for that campaign, never a reconstructed one.
- The **replay fence** is `scripts/check_paper_replay_fence.py`: it re-derives the two Section 2 worked examples from the retained capture's primary bytes and requires all 43 printed literals to match; `COMPARED 43 / MISMATCHES 0` is the only passing output.
- `STOP_FILL` is the renderer's refusal: it emits no prose, writes one machine-readable reason to standard error, and exits non-zero.

The named inputs force this sequence: the two whole-window verdicts license reading the two floor mints and two extraction reports; those six artifacts feed the renderer; a successful renderer output feeds the independent rendered-prose validator. The gamma claim verdict and characterization report are named because the registry needs them, but input schema `joulewise.results_fill_input.v1` has no usable gamma binding and no characterization-report binding. They therefore remain hand-fill inputs until that contract changes.

```text
alpha verdict + alpha floor mint + alpha extraction ─┐
                                                     ├─ role manifest ─ renderer ─┬─ stdout prose ─ validator
beta verdict  + beta floor mint  + beta extraction ─┘                            └─ stderr STOP_FILL
gamma claim verdict ──────────────────────────────── hand fill (present in the manifest; not read by input v1)
characterization report ─────────────────────────── hand fill (manifest v1 accepts only its verdict)
```

The rehearsal floors now show the six issuer fields omitted by the earlier reduced mocks (`calibration_scope`, `source_class`, `method`, `provenance`, `idle_drift_guard`, and `transport_groups`) and the six omitted per-cell fields (`key`, `absolute`, `comparative`, `source_regime`, `transport_group_id`, and `provenance`). Eligibility carries `use_role` and `minimum_claim_n`; dominance-labelled cells and extraction reports carry the fixed `single_count_discipline`. Each extraction carries every required report and cell field in the generalized mint's consumed shape. Values that would otherwise look like real hashes or issued identifiers are explicitly prefixed `SYNTHETIC-REHEARSAL-`.

Preparation and artifact origins:

1. Obtain the lead-named round-7 40-hex commit, require a clean checkout, detach at that exact commit, and create the checkout-local virtual environment. Do not run this procedure from a moving branch.
2. For alpha and beta, `scripts/run_campaign.py --whole-window-verdict --whole-window-verdict-output <window-custody>/whole-window-verdict.json` issues the copied verdict beside the authoritative `campaign_log.jsonl`; `scripts/extract_detection_floors.py --out <window-custody>/detection-floor-extraction.json` issues the extraction in the same window custody directory.
3. `scripts/mint_floor_artifact_generalized.py --pinset <pinset.json> --pinset-sha256 <sha256 of that file> --v2-input-manifest <frozen v2 input manifest> --out <campaign-custody>/aggregate-floor-artifact.json --single-count-out <campaign-custody>/single-count-statement.json --project-commit <commit SHA of the pinned checkout> --project-tree-state clean` issues each aggregate floor mint in campaign custody. Use the exact pinset and input-manifest arguments frozen for that producer; do not reconstruct them here.
4. After the gamma prospective manifest is finalized, `python -m joulewise.cli analyze-claims --analysis-manifest <gamma analysis manifest> --runs-root <RUNS_ROOT> --evidence-root <evidence_root_id>=<path, one flag per declared evidence root> --floor-artifact <the aggregate floor mint that governs the contrast> --output <gamma-analysis-custody>/claim-verdicts.json` issues `joulewise.claim_verdicts.v1` in gamma analysis custody.
5. The characterization contract fixes the destination `<characterization-runs-root>/characterization_result_report.json`, but this checkout has no report-writer command. That is a production stop, not permission to hand-build an artifact: if the round-7 checkout still lacks the sole authenticated writer, record `STOP_FILL` and do not fill characterization prose.

Replace every `/ABSOLUTE/...` value and every `REPLACE-WITH-ISSUED-*` identifier below with the issued round-7 path or identifier named by the variable. `REAL_FILL_DIR` is the custody directory that retains the manifest, renderer output, error output, and validator output together. `PAPER_REPLAY_CORPUS_ROOT` is the retained corpus root that contains `runs_window_a_20260722/`. Do not substitute a historical artifact for a round-7 role.

```sh
set -euo pipefail
set -o noclobber

export JOULEWISE_REPO=/Users/edr/code/JouleWise
export PINNED_ROUND7_COMMIT=REPLACE-WITH-ROUND7-COMMIT
export PYTHON="$JOULEWISE_REPO/.venv/bin/python"
test "$PINNED_ROUND7_COMMIT" != REPLACE-WITH-ROUND7-COMMIT
test -z "$(git -C "$JOULEWISE_REPO" status --porcelain)"
git -C "$JOULEWISE_REPO" switch --detach "$PINNED_ROUND7_COMMIT"
test "$(git -C "$JOULEWISE_REPO" rev-parse HEAD)" = "$PINNED_ROUND7_COMMIT"
test -d "$JOULEWISE_REPO/.venv" || python3 -m venv "$JOULEWISE_REPO/.venv"
"$PYTHON" -m pip install -e "$JOULEWISE_REPO"

export REAL_FILL_DIR=/ABSOLUTE/round-7-fill-custody
export REAL_FILL_MANIFEST="$REAL_FILL_DIR/results-fill-input.json"
export PAPER_REPLAY_CORPUS_ROOT=/ABSOLUTE/root-containing-runs_window_a_20260722
test ! -e "$REAL_FILL_DIR"
mkdir -m 700 "$REAL_FILL_DIR"

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

for required in \
  "$ALPHA_WHOLE_WINDOW_VERDICT" \
  "$ALPHA_AGGREGATE_FLOOR_MINT" \
  "$ALPHA_DETECTION_FLOOR_EXTRACTION" \
  "$BETA_WHOLE_WINDOW_VERDICT" \
  "$BETA_AGGREGATE_FLOOR_MINT" \
  "$BETA_DETECTION_FLOOR_EXTRACTION" \
  "$GAMMA_CLAIM_VERDICT"; do
  test -f "$required"
done
if [ -n "$CHARACTERIZATION_WHOLE_WINDOW_VERDICT" ] || [ -n "$CHARACTERIZATION_RESULT_REPORT" ]; then
  test -f "$CHARACTERIZATION_WHOLE_WINDOW_VERDICT"
  test -f "$CHARACTERIZATION_RESULT_REPORT"
fi

PYTHONDONTWRITEBYTECODE=1 "$PYTHON" - <<'PY'
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
    "gamma": {"claim_verdicts": os.environ["GAMMA_CLAIM_VERDICT"]},
    "characterization": {
        "funded": characterization_verdict is not None,
        "run": characterization_verdict is not None,
        "verdict": characterization_verdict,
    },
}
with Path(os.environ["REAL_FILL_MANIFEST"]).open("x", encoding="utf-8") as handle:
    json.dump(manifest, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY

if PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
    "$JOULEWISE_REPO/scripts/render_results_fills.py" "$REAL_FILL_MANIFEST" \
    > "$REAL_FILL_DIR/rendered-results.md" \
    2> "$REAL_FILL_DIR/rendered-results.stderr.txt"; then
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
    "$JOULEWISE_REPO/scripts/render_results_fills.py" \
    --validate-rendered "$REAL_FILL_DIR/rendered-results.md" \
    > "$REAL_FILL_DIR/validate-results.stdout.txt" \
    2> "$REAL_FILL_DIR/validate-results.stderr.txt"
else
  render_exit=$?
  /bin/cat "$REAL_FILL_DIR/rendered-results.stderr.txt" >&2 || true
  exit "$render_exit"
fi

test ! -e "$REAL_FILL_DIR/draft-v1.round7-working.md"
cp "$JOULEWISE_REPO/docs/paper/draft-v1.md" "$REAL_FILL_DIR/draft-v1.round7-working.md"

baseline_pending_census=$(grep -oE '\[PENDING[^]]*\]' "$REAL_FILL_DIR/draft-v1.round7-working.md" \
  | awk '{ sites += 1; slots += (index($0, ",") ? 2 : 1) } END { print "sites=" sites, "slots=" slots }')
test "$baseline_pending_census" = 'sites=34 slots=36'

baseline_all_marker_census=$(grep -oE '\[(PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]' \
  "$REAL_FILL_DIR/draft-v1.round7-working.md" \
  | awk '{ sites += 1; slots += ($0 ~ /^\[PENDING,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }')
test "$baseline_all_marker_census" = 'sites=37 slots=39'
test "$(grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[(PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' \
  "$JOULEWISE_REPO/docs/paper/results-fill-registry.md")" = 38
```

The shell block stops on any renderer refusal and therefore cannot silently continue into a paper edit. Before hand-fill, it also proves that the copied frozen baseline has 34 literal `[PENDING...]` sites / 36 slots, 37 all-family marker sites / 39 slots, and 38 registry rows. On a successful render, perform these hand-fill steps on `draft-v1.round7-working.md`, never on the frozen source file:

1. Map the emitted §7 choice and §6 choice to the exact current-draft anchors recorded by the corresponding DS rows in `docs/paper/results-fill-registry.md`. Replace each complete guarded passage as one unit; do not paste a value into a neighbouring marker merely because the prose looks similar.
2. For gamma, select the registered decode and prompt contrasts by their issued `contrast_id`. Copy only the producing fields named by the registry—estimate, decision-interval endpoints, floor resolution, outcomes, and reason codes. Input v1 ignores gamma: the manifest entry is present so the round-7 operator sees the shape; it is not read by input v1. A missing claim-side-bound supplier remains `STOP_FILL`; neither `deterministic_bounds.total` nor one clock term substitutes for it.
3. For characterization, require both the issued whole-window verdict and the authenticated `joulewise.characterization_result.v1` report. Follow the report's `render_map` field bindings row by row. If the report, writer, fingerprint, row, or required field is absent, leave every affected site unfilled and record `STOP_FILL`.

After the hand fill, close the custody record with these checks. The replay fence must report `COMPARED 43` and `MISMATCHES 0`; any corpus-unavailable exit is a failure, not a skip. The final census is a new custody artifact: reconcile its post-fill counts against the proved baseline and the DS/PG/DG rows actually filled. A changed count with no matching hand-fill entry is `STOP_FILL`.

```sh
set -euo pipefail
set -o noclobber

PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
  "$JOULEWISE_REPO/scripts/render_results_fills.py" \
  --validate-rendered "$REAL_FILL_DIR/rendered-results.md" \
  > "$REAL_FILL_DIR/validate-results-final.stdout.txt" \
  2> "$REAL_FILL_DIR/validate-results-final.stderr.txt"

PYTHONDONTWRITEBYTECODE=1 "$PYTHON" \
  "$JOULEWISE_REPO/scripts/check_paper_replay_fence.py" \
  --repository-root "$JOULEWISE_REPO" \
  --corpus-root "$PAPER_REPLAY_CORPUS_ROOT" \
  --draft "$REAL_FILL_DIR/draft-v1.round7-working.md" \
  --json "$REAL_FILL_DIR/replay-fence.json" \
  > "$REAL_FILL_DIR/replay-fence.stdout.txt" \
  2> "$REAL_FILL_DIR/replay-fence.stderr.txt"
grep -qx 'COMPARED 43' "$REAL_FILL_DIR/replay-fence.stdout.txt"
grep -qx 'MISMATCHES 0' "$REAL_FILL_DIR/replay-fence.stdout.txt"

test ! -e "$REAL_FILL_DIR/final-marker-census.txt"
ROUND7_WORKING_DRAFT="$REAL_FILL_DIR/draft-v1.round7-working.md" \
  "$PYTHON" - <<'PY' > "$REAL_FILL_DIR/final-marker-census.txt"
import os
import re
from pathlib import Path

text = Path(os.environ["ROUND7_WORKING_DRAFT"]).read_text(encoding="utf-8")
literal = re.findall(r"\[PENDING[^]]*\]", text)
all_family = re.findall(
    r"\[(?:PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|"
    r"REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]",
    text,
)
literal_slots = sum(2 if "," in marker else 1 for marker in literal)
all_family_slots = sum(2 if marker.startswith("[PENDING,") else 1 for marker in all_family)
print(f"literal_pending sites={len(literal)} slots={literal_slots}")
print(f"all_marker_family sites={len(all_family)} slots={all_family_slots}")
PY
test -s "$REAL_FILL_DIR/final-marker-census.txt"
```

## Marker-site outcomes

The renderer is atomic: a later stop discards all earlier authenticated fills, so the two complete-floor runs wrote zero bytes. `STOP-B` below is the exact line both runs printed:

```text
STOP_FILL {"label": "SUPPLIER_UNKNOWN", "reason": "the registry freezes this token but defines no producing artifact field", "registry_row": "[B_decode_claim_J]"}
```

The detailed table below separates runtime observation from static projection. `RULE-B` means: every A/B branch calls `_supplier_unknown("[B_decode_claim_J]")` before emitting prose, producing `SUPPLIER_UNKNOWN` because the registry freezes that token but defines no producing artifact field. `RULE-U(token)` means: if execution reached the named token, `_supplier_unknown(token)` would produce that same `SUPPLIER_UNKNOWN` rule. Thus `PROJECTED STOP — rule: RULE-B` and `PROJECTED STOP — rule: RULE-U(token)` are conclusions from reading the renderer; they were not observed at those rows. A supplier is the exact issued artifact field or frozen calculation that authorizes one fill. The claim-side bound is the separately registered non-floor quantity `B` in the disclosure `F+B`; it is not the complete deterministic-bound total. `STATIC NO ROUTE` means input schema v1 has no route from the named artifact field to that physical draft site; it is not a runtime result and not a successful fill.

| Variant | Render exit | Rendered outputs | STOP_FILL outputs | Validate exit | Observed result |
|---|---:|---:|---:|---:|---|
| dominance reproduced | 2 | 0 | 1 | not run | `STOP-B`; stdout 0 bytes |
| dominance not reproduced | 2 | 0 | 1 | not run | `STOP-B`; stdout 0 bytes |
| both floor windows refused | 0 | 1 | 0 | 0 | §7 C3 + §6 0; validator PASS |
| characterization refused | 2 | 0 | 1 | not run | `VALUE_UNISSUED` at `[D_C_linearity_diagnostic_J_per_token]`; stdout 0 bytes |

The next table has one row per marker-bound registry row. PG-02 and PG-03 share one physical interval marker; DS-26 has one interval marker holding two semantic values. Actual lines were found by searching each row anchor in the frozen draft. The observed column applies to both complete-floor variants because both stopped at the same first field.

| Registry row | Draft line and marker | Supplier | Observed in each complete-floor run | Static projection: dominance reproduced | Static projection: dominance not reproduced |
|---|---|---|---|---|---|
| DS-01 | 189, `[RESULT PENDING ISSUED ARTIFACTS]` | alpha/beta floor mints and extractions | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DG-071 | 256, first diagnostic `[PENDING]` | declared interval-width statistic in an issued diagnostic artifact | not reached; atomic stop occurred first | STATIC NO ROUTE: manual diagnostic row | same |
| DG-075 | 256, second diagnostic `[PENDING]` | declared median-spacing statistic in an issued diagnostic artifact | not reached; atomic stop occurred first | STATIC NO ROUTE: manual diagnostic row | same |
| DS-08a | 274, `[RESULT PENDING ISSUED ARTIFACTS — tables below are structural placeholders; no energy value from superseded artifacts is carried into these tables, and none appears anywhere in this paper except the explicitly labeled instrument diagnostics of Sections 3, 6, and 7.]` | one complete guarded template choice | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-09 | 280, prompt/1.5B gross `[PENDING]` | alpha prompt mean + interval | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_1p5B_prompt_J_per_request]`); not observed | same |
| DS-10 | 280, prompt/1.5B per-token `[PENDING]` | alpha prompt reported-mean companion | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_1p5B_prompt_J_per_token]`); not observed | same |
| DS-11 | 280, prompt/1.5B floor `[PENDING]` | alpha prompt operative floor | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-12 | 280, prompt/1.5B count `[PENDING]` | alpha prompt admitted-bundle count | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[N_bundles_1p5B_prompt]`); not observed | same |
| DS-13 | 281, prompt/7B gross `[PENDING]` | beta prompt mean + interval | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_7B_prompt_J_per_request]`); not observed | same |
| DS-14 | 281, prompt/7B per-token `[PENDING]` | beta prompt reported-mean companion | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_7B_prompt_J_per_token]`); not observed | same |
| DS-15 | 281, prompt/7B floor `[PENDING]` | beta prompt operative floor | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-16 | 281, prompt/7B count `[PENDING]` | beta prompt admitted-bundle count | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[N_bundles_7B_prompt]`); not observed | same |
| DS-17 | 282, decode/1.5B gross `[PENDING]` | alpha decode mean + interval | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_1p5B_decode_J_per_request]`); not observed | same |
| DS-18 | 282, decode/1.5B per-token `[PENDING]` | alpha decode reported-mean companion | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_1p5B_decode_J_per_token]`); not observed | same |
| DS-19 | 282, decode/1.5B floor `[PENDING]` | alpha decode operative floor | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-20 | 282, decode/1.5B count `[PENDING]` | alpha decode admitted-bundle count | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[N_bundles_1p5B_decode]`); not observed | same |
| DS-21 | 283, decode/7B gross `[PENDING]` | beta decode mean + interval | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_7B_decode_J_per_request]`); not observed | same |
| DS-22 | 283, decode/7B per-token `[PENDING]` | beta decode reported-mean companion | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[E_7B_decode_J_per_token]`); not observed | same |
| DS-23 | 283, decode/7B floor `[PENDING]` | beta decode operative floor | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-24 | 283, decode/7B count `[PENDING]` | beta decode admitted-bundle count | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-U(`[N_bundles_7B_decode]`); not observed | same |
| DS-25 | 289, decode point `[PENDING]` | gamma decode estimate | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-26 | 289, decode interval `[PENDING, PENDING]` | gamma decode decision-interval endpoints | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-27 | 289, decode floor `[PENDING]` | maximum of alpha/beta decode floors | not reached; atomic stop occurred first | PROJECTED STOP — rule: RULE-B; not observed | same |
| DS-28 | 289, decode sizing sum/clearance `[PENDING]` | gamma magnitude, floor, and claim-side bound | not reached; atomic stop occurred first | STATIC NO ROUTE: draft/template shape mismatch | same |
| DS-29 | 289, decode claim-side bound `[PENDING]` | no producing field | **OBSERVED STOP_FILL at `[B_decode_claim_J]`; nothing rendered** | STOP_FILL — rule: RULE-B; observed | same |
| DS-30 | 289, decode floor outcome `[PENDING]` | missing conservative-render token | not reached; atomic stop occurred first | STATIC NO ROUTE: token missing | same |
| DS-31 | 289, decode direction outcome `[PENDING]` | missing conservative-render token | not reached; atomic stop occurred first | STATIC NO ROUTE: token missing | same |
| DS-32 | 289, decode verdict `[PENDING]` | missing professor-facing verdict token | not reached; atomic stop occurred first | STATIC NO ROUTE: token missing | same |
| DS-33 | 290, prompt floor `[PENDING]` | missing prompt claim-floor token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| DS-34 | 348, `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | release-manifest repository/archive locators | not reached; atomic stop occurred first | STATIC NO ROUTE: release checklist is outside input v1 | same |
| PG-01 | 290, prompt point `[PENDING]` | missing gamma prompt estimate token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| PG-02 | 290, prompt interval `[PENDING, PENDING]`, lower | missing gamma prompt lower-endpoint token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| PG-03 | 290, same interval marker, upper | missing gamma prompt upper-endpoint token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| PG-04 | 290, prompt sizing sum/clearance `[PENDING]` | missing prompt branch and claim-bound fields | not reached; atomic stop occurred first | STATIC NO ROUTE: token family and shape contract missing | same |
| PG-05 | 290, prompt claim-side bound `[PENDING]` | no named claim-side-bound field | not reached; atomic stop occurred first | STATIC NO ROUTE: supplier and token missing | same |
| PG-06 | 290, prompt floor outcome `[PENDING]` | missing conservative-render token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| PG-07 | 290, prompt direction outcome `[PENDING]` | missing conservative-render token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |
| PG-08 | 290, prompt verdict `[PENDING]` | missing authenticated verdict token | not reached; atomic stop occurred first | STATIC NO ROUTE: token family missing | same |

**Observed totals per complete-floor variant:** 0 rendered outputs; 1 `STOP_FILL`, at `[B_decode_claim_J]`; 37 registry rows not reached; stdout 0 bytes.

**Projected registry-row classification per complete-floor variant:** 0 RENDERED; 22 `STOP_FILL` rules (the one observed rule plus 21 projected-but-not-observed rows); 16 `STATIC NO ROUTE` rows. This projected count is by registry row, not physical marker: PG-02 and PG-03 share one marker.

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
3. `gamma` is accepted but ignored. Each dominance manifest now references an issuer-shaped synthetic `joulewise.claim_verdicts.v1` artifact containing its `claim_verdicts_id`, engine and input bindings, supersession/bundle/sampling audits, family, and contrast. It is **present so the round-7 operator sees the shape; not read by input v1**. The renderer therefore still cannot read the real gamma claim verdict, so decode contrast cells and the entire live prompt arm cannot be filled end to end.
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
