# Round-7 fill checklist (prepared while draft-v1.md is frozen)

This is the execution record for filling the round-7 working copy after the `_v4` artifacts are final. `docs/paper/draft-v1.md` remains frozen: do not edit it. Copy it into the new custody directory and apply every fill or omission sentence only to that working copy, following the rehearsal in `docs/paper/fill-rehearsal-2026-08-27.md:40-220`. The renderer is atomic: it either emits one complete §7 choice plus one complete §6 choice, or emits no prose, writes one `STOP_FILL` record to standard error, and exits non-zero (`scripts/render_results_fills.py:31-36`, `:945-999`, `:1137-1165`). On `STOP_FILL`, discard the run's empty/partial result, retain its stderr, and use only the registered omission sentences below.

## Glossary

- **Supplier:** the exact issued artifact field or frozen derivation that authorizes one fill; prose, a nearby field, and an old result are not suppliers.
- **Issued:** written by the authenticated producer and retained with its identity and provenance, rather than calculated informally at the desk.
- **Custody directory:** a new, non-overwritten directory containing the role manifest, working draft, renderer output, fill ledger, derived TERM record, and every check output.
- **Replay fence:** `scripts/check_paper_replay_fence.py`, which re-derives the Section 2 worked values from retained primary bytes and passes only at `COMPARED 43` and `MISMATCHES 0` (`scripts/check_paper_replay_fence.py:562-588`). It currently does not check the TERM derivations; Batch 2 therefore has an additional fail-closed derivation check.
- **STOP_FILL:** a refusal to insert an unauthenticated, malformed, missing, or unregistered value. The renderer prints the machine-readable refusal on stderr and no paper prose on stdout (`scripts/render_results_fills.py:138-169`, `:1157-1164`).
- **TERM A / TERM B:** for each absolute or comparative floor component, TERM A is the guarded point-only repeatability value and TERM B is the exact linear corner maximum used by the code's dominance predicate. The predicate passes only when `TERM B > TERM A`; equality fails (`docs/paper/results-fill-registry.md:197-242`; `joulewise/detection_floor.py:806-841`).
- **Corner-widened:** evaluated at the allowed endpoints of every member's energy interval. The published corner-widened component floor includes more of the full point-floor formula and is at least TERM B; it is not TERM B (`docs/paper/results-fill-registry.md:227-234`).
- **Operative floor:** the number that governs use at its level. An extraction row calls its drift-widened component value `operative_floor_j` (`joulewise/floor_extraction.py:1359-1384`); an aggregate mint calls the cell maximum `floor_gate_j` (`joulewise/detection_floor.py:1620-1645`). Do not exchange those field names.

## Preconditions (batch 0)

1. Start from the lead-named 40-hex round-7 commit, a clean tree, and a detached checkout. Create a fresh custody directory; never reuse one.

   ```sh
   set -euo pipefail
   set -o noclobber
   export JOULEWISE_REPO=/Users/edr/code/JouleWise
   export PINNED_ROUND7_COMMIT=REPLACE-WITH-ROUND7-COMMIT
   export PYTHON="$JOULEWISE_REPO/.venv/bin/python"
   export REAL_FILL_DIR=/ABSOLUTE/round-7-fill-custody
   export PAPER_REPLAY_CORPUS_ROOT=/ABSOLUTE/root-containing-runs_window_a_20260722
   test "$PINNED_ROUND7_COMMIT" != REPLACE-WITH-ROUND7-COMMIT
   test -z "$(git -C "$JOULEWISE_REPO" status --porcelain)"
   git -C "$JOULEWISE_REPO" switch --detach "$PINNED_ROUND7_COMMIT"
   test "$(git -C "$JOULEWISE_REPO" rev-parse HEAD)" = "$PINNED_ROUND7_COMMIT"
   test ! -e "$REAL_FILL_DIR"
   mkdir -m 700 "$REAL_FILL_DIR"
   cp "$JOULEWISE_REPO/docs/paper/draft-v1.md" "$REAL_FILL_DIR/draft-v1.round7-working.md"
   ```

2. Bind the seven required issued artifacts. The verdict producer emits `status`, `member_failures`, `idle_admission_core`, and its evaluation basis at `scripts/run_campaign.py:6310-6342` and publishes the exact row atomically at `:6364-6373`. The generalized mint constructs each issued cell at `scripts/mint_floor_artifact_generalized.py:2783-2827` and collects those cells into the artifact at `:3002-3024`. The extraction producer emits `cells[]` at `joulewise/floor_extraction.py:1359-1409`. The gamma producer emits each contrast at `joulewise/analysis_engine/__init__.py:1544-1622` and writes the validated artifact atomically at `joulewise/analysis_engine/artifact.py:3507-3530`.

   ```sh
   export ALPHA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/alpha/whole-window-verdict.json
   export ALPHA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/alpha/aggregate-floor-artifact.json
   export ALPHA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/alpha/detection-floor-extraction.json
   export BETA_WHOLE_WINDOW_VERDICT=/ABSOLUTE/beta/whole-window-verdict.json
   export BETA_AGGREGATE_FLOOR_MINT=/ABSOLUTE/beta/aggregate-floor-artifact.json
   export BETA_DETECTION_FLOOR_EXTRACTION=/ABSOLUTE/beta/detection-floor-extraction.json
   export GAMMA_CLAIM_VERDICT=/ABSOLUTE/gamma/claim-verdicts.json

   export ALPHA_PROMPT_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-CELL-ID
   export ALPHA_PROMPT_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-ABS-ID
   export ALPHA_PROMPT_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-PROMPT-CMP-ID
   export ALPHA_DECODE_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-CELL-ID
   export ALPHA_DECODE_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-ABS-ID
   export ALPHA_DECODE_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-ALPHA-DECODE-CMP-ID
   export BETA_PROMPT_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-CELL-ID
   export BETA_PROMPT_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-ABS-ID
   export BETA_PROMPT_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-PROMPT-CMP-ID
   export BETA_DECODE_FLOOR_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-CELL-ID
   export BETA_DECODE_ABSOLUTE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-ABS-ID
   export BETA_DECODE_COMPARATIVE_EXTRACTION_CELL_ID=REPLACE-WITH-ISSUED-BETA-DECODE-CMP-ID

   for required in \
     "$ALPHA_WHOLE_WINDOW_VERDICT" "$ALPHA_AGGREGATE_FLOOR_MINT" \
     "$ALPHA_DETECTION_FLOOR_EXTRACTION" "$BETA_WHOLE_WINDOW_VERDICT" \
     "$BETA_AGGREGATE_FLOOR_MINT" "$BETA_DETECTION_FLOOR_EXTRACTION" \
     "$GAMMA_CLAIM_VERDICT"; do
     test -f "$required"
   done
   ```

   Copy only issuer-written cell IDs. The renderer requires one floor ID plus distinct absolute and comparative extraction IDs for prompt and decode (`scripts/render_results_fills.py:756-804`).

3. Create the role manifest. Input v1 accepts the gamma path but does not read it; characterization has no result-report binding, so it stays unfunded/unrun here (`scripts/render_results_fills.py:945-999`).

   ```sh
   export REAL_FILL_MANIFEST="$REAL_FILL_DIR/results-fill-input.json"
   PYTHONDONTWRITEBYTECODE=1 "$PYTHON" - <<'PY'
   import json, os
   from pathlib import Path

   def campaign(prefix):
       return {
           "verdict": os.environ[f"{prefix}_WHOLE_WINDOW_VERDICT"],
           "floor_artifact": os.environ[f"{prefix}_AGGREGATE_FLOOR_MINT"],
           "extraction": os.environ[f"{prefix}_DETECTION_FLOOR_EXTRACTION"],
           "cells": {
               phase: {
                   "floor_cell_id": os.environ[f"{prefix}_{phase.upper()}_FLOOR_CELL_ID"],
                   "absolute_extraction_cell_id": os.environ[f"{prefix}_{phase.upper()}_ABSOLUTE_EXTRACTION_CELL_ID"],
                   "comparative_extraction_cell_id": os.environ[f"{prefix}_{phase.upper()}_COMPARATIVE_EXTRACTION_CELL_ID"],
               }
               for phase in ("prompt", "decode")
           },
       }

   value = {
       "schema_version": "joulewise.results_fill_input.v1",
       "campaigns": {"alpha": campaign("ALPHA"), "beta": campaign("BETA")},
       "gamma": {"claim_verdicts": os.environ["GAMMA_CLAIM_VERDICT"]},
       "characterization": {"funded": False, "run": False, "verdict": None},
   }
   with Path(os.environ["REAL_FILL_MANIFEST"]).open("x", encoding="utf-8") as handle:
       json.dump(value, handle, indent=2, sort_keys=True)
       handle.write("\n")
   PY
   ```

4. Prove the frozen baseline before any replacement. These commands were run on the preparation tree and printed exactly:

   ```sh
   grep -oE '\[PENDING[^]]*\]' docs/paper/draft-v1.md \
     | awk '{ sites += 1; slots += (index($0, ",") ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
   # sites=34 slots=36

   grep -oE '\[(PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]' \
     docs/paper/draft-v1.md \
     | awk '{ sites += 1; slots += ($0 ~ /^\[PENDING,/ ? 2 : 1) } END { print "sites=" sites, "slots=" slots }'
   # sites=37 slots=39

   grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[(PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' \
     docs/paper/results-fill-registry.md
   # 38
   ```

5. Run the replay fence on the unfilled working draft. Corpus absence is failure, never a skip.

   ```sh
   PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/check_paper_replay_fence.py" \
     --repository-root "$JOULEWISE_REPO" \
     --corpus-root "$PAPER_REPLAY_CORPUS_ROOT" \
     --draft "$REAL_FILL_DIR/draft-v1.round7-working.md" \
     --json "$REAL_FILL_DIR/replay-fence-batch0.json" \
     | tee "$REAL_FILL_DIR/replay-fence-batch0.stdout.txt"
   ```

   Passing tail:

   ```text
   COMPARED 43
   MISMATCHES 0
   ```

## Batch 1 — renderer route (§7 variant + §6 variant)

Run the renderer once. Preserve stdout and stderr even on refusal.

```sh
set +e
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/render_results_fills.py" \
  "$REAL_FILL_MANIFEST" \
  > "$REAL_FILL_DIR/rendered-results.md" \
  2> "$REAL_FILL_DIR/rendered-results.stderr.txt"
render_exit=$?
set -e
if [ "$render_exit" -ne 0 ]; then
  test "$render_exit" -eq 2
  test ! -s "$REAL_FILL_DIR/rendered-results.md"
  grep -q '^STOP_FILL ' "$REAL_FILL_DIR/rendered-results.stderr.txt"
  sed -n '1p' "$REAL_FILL_DIR/rendered-results.stderr.txt"
else
  PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/render_results_fills.py" \
    --validate-rendered "$REAL_FILL_DIR/rendered-results.md" \
    | tee "$REAL_FILL_DIR/validate-results.stdout.txt"
fi
```

Today, only §7 D (both floor windows pass but a decode cell publishes no floor) and §7 C3 (both floor windows refused) can emit, each paired with §6 0 (no characterization run). Their validator lines are respectively:

```text
results prose rendered lint: PASS (§7 7_D; §6 0; zero fill tokens)
results prose rendered lint: PASS (§7 7_C3; §6 0; zero fill tokens)
```

Complete-floor A/B1/B2 executions stop at `[B_decode_claim_J]` (`scripts/render_results_fills.py:963-978`). Contrary to the shorthand in the task brief, one-window-pass C1/C2 executions stop earlier at the first missing D-123 reported mean, not at `[B_decode_claim_J]` (`scripts/render_results_fills.py:979-989`). A supplied characterization verdict stops at the first unissued characterization result field (`scripts/render_results_fills.py:917-942`). Do not splice earlier authenticated values out of any stopped atomic output.

| Placement row | Draft site | Supplier and fill rule |
|---|---|---|
| DS-08a | line 274, complete marker bytes in registry `docs/paper/results-fill-registry.md:765` | Renderer route: replace the whole marker with the selected, validated §7/§6 guarded choice only after a zero exit. If the renderer stops, print exactly: “The prospective Results branch is omitted: the atomic registered renderer stopped before issuing one complete guarded Section 7 and Section 6 choice; the retained STOP_FILL record identifies the first unavailable supplier.” |

Batch-1 fence: the `--validate-rendered` command above must print one of the two exact PASS lines. If the renderer stopped, the fence is instead `render_exit=2`, zero-byte stdout, and exactly one `STOP_FILL` line; no renderer-supplied draft fill occurred.

## Batch 2 — desk derivations under the replay fence (TERM A / TERM B, 16 rows) and the dominance verdict; title choice

The eight component pairs below are the sixteen registry rows at `docs/paper/results-fill-registry.md:244-261`. Their source is `aggregate-floor-artifact.json` → `cells[<issued floor cell_id>].absolute` or `.comparative`. The absolute producer emits `n`, `residuals_j`, `max_abs_residual_j`, `prediction_component_j`, `guard_factor`, and `admissible_half_widths_j` at `joulewise/detection_floor.py:1440-1467`; the comparative producer emits `n_blocks`, `block_deltas_j`, `max_abs_delta_j`, `prediction_component_j`, `guard_factor`, and widths at `:1480-1507`. The conditional diagnostic object is emitted at `:787-803` and attached at `:844-855`.

| Registry row | Source artifact → exact field path | Frozen derivation |
|---|---|---|
| `TERM_A_1p5B_prompt_abs_J` (`docs/paper/results-fill-registry.md:246`) | Alpha mint → `cells[$ALPHA_PROMPT_FLOOR_CELL_ID].absolute.{guard_factor,max_abs_residual_j,prediction_component_j}` | `guard_factor * max(max_abs_residual_j, prediction_component_j)` |
| `TERM_B_1p5B_prompt_abs_J` (`docs/paper/results-fill-registry.md:247`) | Alpha mint → `cells[$ALPHA_PROMPT_FLOOR_CELL_ID].absolute.{n,residuals_j,admissible_half_widths_j}` | `max_i(abs(r_i)+w_i*(n-1)/n+(math.fsum(w)-w_i)/n)` |
| `TERM_A_1p5B_prompt_cmp_J` (`docs/paper/results-fill-registry.md:248`) | Alpha mint → `cells[$ALPHA_PROMPT_FLOOR_CELL_ID].comparative.{guard_factor,max_abs_delta_j,prediction_component_j}` | `guard_factor * max(max_abs_delta_j, prediction_component_j)` |
| `TERM_B_1p5B_prompt_cmp_J` (`docs/paper/results-fill-registry.md:249`) | Alpha mint → `cells[$ALPHA_PROMPT_FLOOR_CELL_ID].comparative.{block_deltas_j,admissible_half_widths_j}` | `max_i(abs(block_deltas_j[i])+admissible_half_widths_j[i])` |
| `TERM_A_1p5B_decode_abs_J` (`docs/paper/results-fill-registry.md:250`) | Alpha mint → `cells[$ALPHA_DECODE_FLOOR_CELL_ID].absolute.{guard_factor,max_abs_residual_j,prediction_component_j}` | Absolute TERM-A formula above. |
| `TERM_B_1p5B_decode_abs_J` (`docs/paper/results-fill-registry.md:251`) | Alpha mint → `cells[$ALPHA_DECODE_FLOOR_CELL_ID].absolute.{n,residuals_j,admissible_half_widths_j}` | Absolute TERM-B formula above. |
| `TERM_A_1p5B_decode_cmp_J` (`docs/paper/results-fill-registry.md:252`) | Alpha mint → `cells[$ALPHA_DECODE_FLOOR_CELL_ID].comparative.{guard_factor,max_abs_delta_j,prediction_component_j}` | Comparative TERM-A formula above. |
| `TERM_B_1p5B_decode_cmp_J` (`docs/paper/results-fill-registry.md:253`) | Alpha mint → `cells[$ALPHA_DECODE_FLOOR_CELL_ID].comparative.{block_deltas_j,admissible_half_widths_j}` | Comparative TERM-B formula above. |
| `TERM_A_7B_prompt_abs_J` (`docs/paper/results-fill-registry.md:254`) | Beta mint → `cells[$BETA_PROMPT_FLOOR_CELL_ID].absolute.{guard_factor,max_abs_residual_j,prediction_component_j}` | Absolute TERM-A formula above. |
| `TERM_B_7B_prompt_abs_J` (`docs/paper/results-fill-registry.md:255`) | Beta mint → `cells[$BETA_PROMPT_FLOOR_CELL_ID].absolute.{n,residuals_j,admissible_half_widths_j}` | Absolute TERM-B formula above. |
| `TERM_A_7B_prompt_cmp_J` (`docs/paper/results-fill-registry.md:256`) | Beta mint → `cells[$BETA_PROMPT_FLOOR_CELL_ID].comparative.{guard_factor,max_abs_delta_j,prediction_component_j}` | Comparative TERM-A formula above. |
| `TERM_B_7B_prompt_cmp_J` (`docs/paper/results-fill-registry.md:257`) | Beta mint → `cells[$BETA_PROMPT_FLOOR_CELL_ID].comparative.{block_deltas_j,admissible_half_widths_j}` | Comparative TERM-B formula above. |
| `TERM_A_7B_decode_abs_J` (`docs/paper/results-fill-registry.md:258`) | Beta mint → `cells[$BETA_DECODE_FLOOR_CELL_ID].absolute.{guard_factor,max_abs_residual_j,prediction_component_j}` | Absolute TERM-A formula above. |
| `TERM_B_7B_decode_abs_J` (`docs/paper/results-fill-registry.md:259`) | Beta mint → `cells[$BETA_DECODE_FLOOR_CELL_ID].absolute.{n,residuals_j,admissible_half_widths_j}` | Absolute TERM-B formula above. |
| `TERM_A_7B_decode_cmp_J` (`docs/paper/results-fill-registry.md:260`) | Beta mint → `cells[$BETA_DECODE_FLOOR_CELL_ID].comparative.{guard_factor,max_abs_delta_j,prediction_component_j}` | Comparative TERM-A formula above. |
| `TERM_B_7B_decode_cmp_J` (`docs/paper/results-fill-registry.md:261`) | Beta mint → `cells[$BETA_DECODE_FLOOR_CELL_ID].comparative.{block_deltas_j,admissible_half_widths_j}` | Comparative TERM-B formula above. |

Run this fail-closed derivation. It preserves array order, uses `math.fsum`, requires every unconditional parent, and recreates the complete emitted `point_floor_diagnostic` object wherever present before it writes the sixteen terms.

```sh
export TERM_DERIVATION_OUT="$REAL_FILL_DIR/term-dominance.json"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" - <<'PY'
import json, math, os
from pathlib import Path

jobs = (
    ("1p5B_prompt", os.environ["ALPHA_AGGREGATE_FLOOR_MINT"], os.environ["ALPHA_PROMPT_FLOOR_CELL_ID"], "prompt"),
    ("1p5B_decode", os.environ["ALPHA_AGGREGATE_FLOOR_MINT"], os.environ["ALPHA_DECODE_FLOOR_CELL_ID"], "decode"),
    ("7B_prompt", os.environ["BETA_AGGREGATE_FLOOR_MINT"], os.environ["BETA_PROMPT_FLOOR_CELL_ID"], "prompt"),
    ("7B_decode", os.environ["BETA_AGGREGATE_FLOOR_MINT"], os.environ["BETA_DECODE_FLOOR_CELL_ID"], "decode"),
)

def number(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SystemExit(f"STOP_FILL invalid numeric parent: {where}")
    return float(value)

terms, checks, phase_passes = {}, 0, {"prompt": [], "decode": []}
for stem, artifact_path, cell_id, phase in jobs:
    artifact = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
    if artifact.get("schema_version") != "joulewise.detection_floor_artifact.v2":
        raise SystemExit(f"STOP_FILL wrong floor schema: {artifact_path}")
    matches = [cell for cell in artifact.get("cells", []) if cell.get("cell_id") == cell_id]
    if len(matches) != 1:
        raise SystemExit(f"STOP_FILL floor cell must occur exactly once: {cell_id}")
    cell = matches[0]
    for kind, suffix in (("absolute", "abs"), ("comparative", "cmp")):
        component = cell.get(kind)
        if not isinstance(component, dict):
            raise SystemExit(f"STOP_FILL missing component: {cell_id}.{kind}")
        guard = number(component.get("guard_factor"), f"{cell_id}.{kind}.guard_factor")
        prediction = number(component.get("prediction_component_j"), f"{cell_id}.{kind}.prediction_component_j")
        widths = [number(v, f"{cell_id}.{kind}.admissible_half_widths_j") for v in component.get("admissible_half_widths_j", [])]
        if kind == "absolute":
            points = [number(v, f"{cell_id}.absolute.residuals_j") for v in component.get("residuals_j", [])]
            maximum = number(component.get("max_abs_residual_j"), f"{cell_id}.absolute.max_abs_residual_j")
            n = component.get("n")
            if isinstance(n, bool) or not isinstance(n, int) or n <= 0 or n != len(points) or len(widths) != n:
                raise SystemExit(f"STOP_FILL invalid absolute array/count parents: {cell_id}")
            if maximum != max(abs(v) for v in points):
                raise SystemExit(f"STOP_FILL max_abs_residual_j disagrees: {cell_id}")
            width_sum = math.fsum(widths)
            term_b = max(abs(r) + w * (n - 1) / n + (width_sum - w) / n for r, w in zip(points, widths, strict=True))
        else:
            points = [number(v, f"{cell_id}.comparative.block_deltas_j") for v in component.get("block_deltas_j", [])]
            maximum = number(component.get("max_abs_delta_j"), f"{cell_id}.comparative.max_abs_delta_j")
            n = component.get("n_blocks")
            if isinstance(n, bool) or not isinstance(n, int) or n <= 0 or n != len(points) or len(widths) != n:
                raise SystemExit(f"STOP_FILL invalid comparative array/count parents: {cell_id}")
            if maximum != max(abs(v) for v in points):
                raise SystemExit(f"STOP_FILL max_abs_delta_j disagrees: {cell_id}")
            term_b = max(abs(d) + w for d, w in zip(points, widths, strict=True))
        unguarded = max(maximum, prediction)
        term_a = guard * unguarded
        expected_diagnostic = {
            "label": "repeatability_diagnostic",
            "published_claim_floor": False,
            "unguarded_floor_j": unguarded,
            "guard_factor": guard,
            "guarded_floor_j": term_a,
        }
        if "point_floor_diagnostic" in component:
            if component["point_floor_diagnostic"] != expected_diagnostic:
                raise SystemExit(f"STOP_FILL point diagnostic mismatch: {cell_id}.{kind}")
            checks += 1
        terms[f"TERM_A_{stem}_{suffix}_J"] = term_a
        terms[f"TERM_B_{stem}_{suffix}_J"] = term_b
        phase_passes[phase].append(term_b > term_a)

if len(terms) != 16 or any(len(values) != 4 for values in phase_passes.values()):
    raise SystemExit("STOP_FILL TERM census mismatch")
phase = {name: all(values) for name, values in phase_passes.items()}
outcome = "A" if all(phase.values()) else "B"
record = {"terms": terms, "diagnostic_objects_reproduced": checks, "phase_pass": phase, "outcome_if_admitted": outcome}
with Path(os.environ["TERM_DERIVATION_OUT"]).open("x", encoding="utf-8") as handle:
    json.dump(record, handle, indent=2, sort_keys=True, allow_nan=False)
    handle.write("\n")
print("TERM_ROWS 16")
print(f"DIAGNOSTIC_SELF_CONSISTENCY PASS checked={checks}")
print(f"DOMINANCE prompt={phase['prompt']} decode={phase['decode']} outcome={outcome}")
PY
```

Outcome A means all four prompt pairs and all four decode pairs pass. Outcome B means admitted evidence produces at least one failing pair; a phase passes only when all four of its pairs pass. Outcome C takes precedence when alpha, beta, or a required gamma contrast is refused before the predicate can be evaluated (`docs/paper/round7/retensing-plan.md:3-29`). A selects the PRIMARY title at frozen draft lines 3 and 7. B selects the NULL-OUTCOME title at lines 4 and 7 under registry item 28 (`docs/paper/results-fill-registry.md:263-272`). Outcome C's title is not explicitly bound; stop before changing line 7 and request the ruling recorded under Open gaps.

Batch-2 fence: rerun the Batch-0 replay command with `--json "$REAL_FILL_DIR/replay-fence-batch2.json"`; require `COMPARED 43` and `MISMATCHES 0`. Also require the derivation output lines `TERM_ROWS 16` and `DIAGNOSTIC_SELF_CONSISTENCY PASS ...`. The official replay program does not consume `term-dominance.json`; the inline fail-closed check above is the current TERM fence.

## Batch 3 — hand fills, Section 4 and Section 6 (in draft line order)

Use issued cell IDs and issued `contrast_id` values, never array positions. The aggregate cell fields are emitted at `joulewise/detection_floor.py:1635-1645`; gamma's `estimator`, `deterministic_bounds`, `floor`, and `claim_evaluation` objects are emitted at `joulewise/analysis_engine/__init__.py:1544-1622`. Record each replacement, old marker bytes, source SHA-256, field path, and new bytes in `$REAL_FILL_DIR/fill-ledger.jsonl` before editing the working copy.

| Placement row | Draft line | Marker bytes | Supplier: artifact → field | Fill rule | Fence after fill |
|---|---:|---|---|---|---|
| DS-01 | 189 | `[RESULT PENDING ISSUED ARTIFACTS]` | Alpha and beta `aggregate-floor-artifact.json` → `cells[<issued prompt/decode cell_id>].floor_abs_j`, `.floor_cmp_j`, `.floor_gate_j` (`docs/paper/results-fill-registry.md:744`; producer `joulewise/detection_floor.py:1620-1645`) | Copy both components; independently derive `max(floor_abs_j, floor_cmp_j)` and require exact equality with `floor_gate_j`. Replace the complete marker as one unit using the registry's four-cell decomposition shape. If any parent is unavailable, print exactly: “The four prospective phase-cell decompositions are omitted: at least one authenticated aggregate floor artifact or issued cell is unavailable, so no cell value is reported.” | Replay fence; ledger old bytes must occur once before and zero times after. |
| DS-11 | 280 | `[PENDING]` in 1.5B prompt floor cell | Alpha aggregate mint → `cells[$ALPHA_PROMPT_FLOOR_CELL_ID].floor_gate_j` | HAND-FILL the operative floor and the cell's authenticated label branch; derive max of component fields and require exact equality. Registry `docs/paper/results-fill-registry.md:784`. | Same. |
| DS-15 | 281 | `[PENDING]` in 7B prompt floor cell | Beta aggregate mint → `cells[$BETA_PROMPT_FLOOR_CELL_ID].floor_gate_j` | Same rule. Registry `docs/paper/results-fill-registry.md:788`. | Same. |
| DS-19 | 282 | `[PENDING]` in 1.5B decode floor cell | Alpha aggregate mint → `cells[$ALPHA_DECODE_FLOOR_CELL_ID].floor_gate_j` | Same rule. Registry `docs/paper/results-fill-registry.md:792`. | Same. |
| DS-23 | 283 | `[PENDING]` in 7B decode floor cell | Beta aggregate mint → `cells[$BETA_DECODE_FLOOR_CELL_ID].floor_gate_j` | Same rule. Registry `docs/paper/results-fill-registry.md:796`. | Same. |
| DS-25 | 289 | decode point `[PENDING]` | `claim-verdicts.json` → `contrasts[<issued decode contrast_id>].estimator.estimate` | HAND-FILL signed B-minus-A estimate; verify `conditions.difference_orientation == "condition_b_minus_condition_a"`. Registry `docs/paper/results-fill-registry.md:798`; producer `joulewise/analysis_engine/__init__.py:1575-1607`. | Replay fence; unique contrast ID and ledger entry required. |
| DS-26 | 289 | decode interval `[PENDING, PENDING]` | Same contrast → `deterministic_bounds.decision_interval.lower`, `.upper` | HAND-FILL both endpoints in their stored order; one physical marker supplies two slots. Registry `docs/paper/results-fill-registry.md:799`; producer `joulewise/analysis_engine/__init__.py:1566-1574`. | Same. |
| DS-27 | 289 | decode floor `[PENDING]` | Alpha/beta aggregate mints → decode `cells[<issued id>].floor_gate_j`; gamma contrast → `floor.active_floor_j` | DERIVE max of the two issued arm gates and require exact equality with gamma `floor.active_floor_j`. Registry `docs/paper/results-fill-registry.md:800`; consumer max `joulewise/analysis_engine/__init__.py:225-285`. | Same. |

Batch-3 fence: rerun the replay fence and require `COMPARED 43` / `MISMATCHES 0`; then run the final-census command from Post-fill closure and reconcile every changed marker/slot against these eight ledger rows. The replay fence protects its 43 existing literals, not these hand-filled fields, so source hashes and exact old/new bytes in the ledger are mandatory.

## Batch 4 — hand fills, diagnostics and locators (DG-071, DG-075, DS-34, the two [[NEEDS-VALUE]] sites at lines 272 and 276)

These five sites have no fillable producer in this checkout; replace each site only with its exact omission sentence and ledger the replacement.

| Placement row | Draft line and bytes | Supplier status | Exact sentence |
|---|---|---|---|
| DG-071 | line 256, first diagnostic `[PENDING]` | `power_trace.csv` has `interval_start_s` and `interval_end_s`, but the registry declares neither a representative statistic nor an issued diagnostic artifact (`docs/paper/results-fill-registry.md:627`; interval fields validated at `joulewise/bundle_read.py:2604-2636`). | “The sampling-record interval width is omitted: no representative statistic and no issued diagnostic artifact are registered for this bundle (registry row DG-071).” |
| DG-075 | line 256, second diagnostic `[PENDING]` | The raw `timestamp_s` values exist, but the desk median is not an issuance and no producing artifact field is registered (`docs/paper/results-fill-registry.md:631`; timestamp input validated at `joulewise/bundle_read.py:2604-2610`). | “The median record spacing is omitted: the desk calculation is not an issued artifact field and no supplier is registered for this bundle (registry row DG-075).” |
| DS-34 | line 348, `[REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST]` | No release-manifest schema or fields exist for repository commit, archive locator, and digest manifest (`docs/paper/results-fill-registry.md:807`). | “Repository and archive locators are omitted: the release checklist has not issued a repository commit, archive locator, and published fingerprint manifest (registry row DS-34).” |

The two non-registry generic sites are placed as follows:

| Draft line and exact site | Supplier status | Exact sentence |
|---|---|---|
| 272, `[[NEEDS-VALUE: exact cell-floor F, claim-side bound B ...]]` | D-122 retains only an approximate 5 J bar (`docs/paper/results-fill-registry.md:641-651`); exact B has no supplier (`:367`). | “The exact planning components F and B and any fixed margin are omitted: D-122 retains only the approximate 5 J bar, and no exact claim-side-bound supplier is built.” |
| 276, `[[NEEDS-VALUE: D-123 producing schema ...]]` | The reported-mean schema, admitted-member basis, interval fields, and runtime-observed per-token companions are undefined (`docs/paper/results-fill-registry.md:321-351`). | “The D-123 per-token numerator, denominator, and point-or-interval rendering are omitted because the producing schema is not built.” |

Batch-4 fence: rerun the replay fence and require `COMPARED 43` / `MISMATCHES 0`; rerun the all-family census and reconcile the five changed sites against exactly five new ledger entries.

## STOP_FILL rows

The following rows have no supplier or no registered rendering token. These sentences are the complete replacement text; do not insert the tempting internal floor-component mean, deterministic total, unregistered outcome wording, or inferred prompt analogue.

| Placement row | Exact sentence that prints in place of the marker |
|---|---|
| DS-09 | “The 1.5B prompt-processing gross phase-energy estimate and composed interval are omitted: the D-123 reported-mean schema and admitted-member basis have no built supplier in this checkout (registry row DS-09).” |
| DS-10 | “The 1.5B prompt-processing per-token value is omitted: no D-123 runtime-observed numerator and denominator field is registered in this checkout (registry row DS-10).” |
| DS-12 | “The 1.5B prompt-processing bundle count is omitted: the admitted independent-bundle basis for the D-123 mean is not defined (registry row DS-12).” |
| DS-13 | “The 7B prompt-processing gross phase-energy estimate and composed interval are omitted: the D-123 reported-mean schema and admitted-member basis have no built supplier in this checkout (registry row DS-13).” |
| DS-14 | “The 7B prompt-processing per-token value is omitted: no D-123 runtime-observed numerator and denominator field is registered in this checkout (registry row DS-14).” |
| DS-16 | “The 7B prompt-processing bundle count is omitted: the admitted independent-bundle basis for the D-123 mean is not defined (registry row DS-16).” |
| DS-17 | “The 1.5B token-generation gross phase-energy estimate and composed interval are omitted: the D-123 reported-mean schema and admitted-member basis have no built supplier in this checkout (registry row DS-17).” |
| DS-18 | “The 1.5B token-generation per-token value is omitted: no D-123 runtime-observed numerator and denominator field is registered in this checkout (registry row DS-18).” |
| DS-20 | “The 1.5B token-generation bundle count is omitted: the admitted independent-bundle basis for the D-123 mean is not defined (registry row DS-20).” |
| DS-21 | “The 7B token-generation gross phase-energy estimate and composed interval are omitted: the D-123 reported-mean schema and admitted-member basis have no built supplier in this checkout (registry row DS-21).” |
| DS-22 | “The 7B token-generation per-token value is omitted: no D-123 runtime-observed numerator and denominator field is registered in this checkout (registry row DS-22).” |
| DS-24 | “The 7B token-generation bundle count is omitted: the admitted independent-bundle basis for the D-123 mean is not defined (registry row DS-24).” |
| DS-28 | “The sizing sum C = F + B and its signed clearance are omitted: the claim-side bound B has no built supplier in this checkout (registry row DS-29), and the one-cell/two-quantity rendering contract for registry row DS-28 is unresolved; only the floor gate \|estimate\| > F is reported.” |
| DS-29 | “The decode claim-side bound B is omitted: no producing artifact field is registered in this checkout (registry row DS-29), and deterministic_bounds.total is not a substitute.” |
| DS-30 | “The decode floor-gate outcome is omitted: no exact conservative rendering token is registered for this table cell (registry row DS-30).” |
| DS-31 | “The decode direction-gate outcome is omitted: no exact conservative rendering token is registered for this table cell (registry row DS-31).” |
| DS-32 | “The decode verdict is omitted: claim-verdicts.json issues an internal outcome, but no professor-facing conservative rendering token is registered for this table cell (registry row DS-32).” |
| DS-33 | “The prompt-processing claim floor is omitted: the guarded prompt token family is not registered in this checkout (registry row DS-33).” |
| PG-01 | “The prompt-processing contrast estimate is omitted: no authenticated prompt estimate token is registered in this checkout (registry row PG-01).” |
| PG-02 | “The prompt-processing interval lower endpoint is omitted: no authenticated prompt lower-endpoint token is registered in this checkout (registry row PG-02).” |
| PG-03 | “The prompt-processing interval upper endpoint is omitted: no authenticated prompt upper-endpoint token is registered in this checkout (registry row PG-03).” |
| PG-04 | “The prompt-processing sizing sum C = F + B and its signed clearance are omitted: the prompt claim-bound token family and the one-cell/two-quantity rendering contract are not registered in this checkout (registry row PG-04).” |
| PG-05 | “The prompt-processing claim-side bound B is omitted: no named producing artifact field or prompt rendering token is registered in this checkout (registry row PG-05).” |
| PG-06 | “The prompt-processing floor-gate outcome is omitted: no conservative prompt rendering token is registered in this checkout (registry row PG-06).” |
| PG-07 | “The prompt-processing direction-gate outcome is omitted: no conservative prompt rendering token is registered in this checkout (registry row PG-07).” |
| PG-08 | “The prompt-processing verdict is omitted: no authenticated professor-facing prompt verdict token is registered in this checkout (registry row PG-08).” |

For DS-29, the renderer's exact machine refusal remains:

```text
STOP_FILL {"label": "SUPPLIER_UNKNOWN", "reason": "the registry freezes this token but defines no producing artifact field", "registry_row": "[B_decode_claim_J]"}
```

## Post-fill closure

1. Revalidate the renderer output if Batch 1 succeeded:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/render_results_fills.py" \
     --validate-rendered "$REAL_FILL_DIR/rendered-results.md"
   ```

   Passing line is one exact `results prose rendered lint: PASS (...)` line recorded in Batch 1.

2. Run the replay fence on the final working draft and require the exact tail:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 "$PYTHON" "$JOULEWISE_REPO/scripts/check_paper_replay_fence.py" \
     --repository-root "$JOULEWISE_REPO" \
     --corpus-root "$PAPER_REPLAY_CORPUS_ROOT" \
     --draft "$REAL_FILL_DIR/draft-v1.round7-working.md" \
     --json "$REAL_FILL_DIR/replay-fence-final.json" \
     | tee "$REAL_FILL_DIR/replay-fence-final.stdout.txt"
   ```

   ```text
   COMPARED 43
   MISMATCHES 0
   ```

3. Write the final marker census and reconcile it with the fill ledger. Starting counts are literal `34/36` and all-family `37/39`. For each ledger entry, decrement one site and one slot, except DS-26 and the shared PG-02/PG-03 interval site decrement one site and two slots. A changed count with no matching ledger entry is `STOP_FILL`.

   ```sh
   ROUND7_WORKING_DRAFT="$REAL_FILL_DIR/draft-v1.round7-working.md" "$PYTHON" - <<'PY'
   import os, re
   from pathlib import Path
   text = Path(os.environ["ROUND7_WORKING_DRAFT"]).read_text(encoding="utf-8")
   literal = re.findall(r"\[PENDING[^]]*\]", text)
   family = re.findall(r"\[(?:PENDING[^]]*|RESULT PENDING ISSUED ARTIFACTS[^]]*|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)\]", text)
   print(f"literal_pending sites={len(literal)} slots={sum(2 if ',' in x else 1 for x in literal)}")
   print(f"all_marker_family sites={len(family)} slots={sum(2 if x.startswith('[PENDING,') else 1 for x in family)}")
   print(f"needs_value sites={len(re.findall(r'\[\[NEEDS-VALUE:', text))}")
   PY
   ```

4. Recount the ruling-item-45 marker rows and the all-family successor count:

   ```sh
   grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[PENDING' docs/paper/results-fill-registry.md
   # 35
   grep -cE '^\| (DS|PG|DG)-[0-9]+[a-z]? — .*\[(PENDING|RESULT PENDING ISSUED ARTIFACTS|REPOSITORY AND ARCHIVE LOCATORS PENDING RELEASE CHECKLIST)' docs/paper/results-fill-registry.md
   # 38
   ```

5. Prove that every marker-bound row is placed exactly once in this checklist:

   ```sh
   "$PYTHON" - <<'PY'
   import re
   from collections import Counter
   from pathlib import Path
   text = Path("docs/paper/round7/fill-checklist.md").read_text(encoding="utf-8")
   placed = re.findall(r"^\| ((?:DS|PG|DG)-[0-9]+[a-z]?) \|", text, re.M)
   expected = ["DS-01", "DS-08a", *[f"DS-{n:02d}" for n in range(9, 35)], *[f"PG-{n:02d}" for n in range(1, 9)], "DG-071", "DG-075"]
   counts = Counter(placed)
   assert set(counts) == set(expected), (sorted(set(expected)-set(counts)), sorted(set(counts)-set(expected)))
   assert all(counts[row] == 1 for row in expected), counts
   print("ROWS 38/38 PLACED")
   PY
   ```

6. Run the existing regressions and paper build. On this preparation tree, with `TMPDIR` under the worktree, the command printed the exact passing tail shown below:

   ```sh
   mkdir -p .tmp-r7
   TMPDIR="$PWD/.tmp-r7" PYTHONDONTWRITEBYTECODE=1 \
     /Users/edr/code/JouleWise/.venv/bin/python -m pytest -p no:cacheprovider \
     tests/test_render_results_fills.py tests/test_paper_build.py -q
   ```

   ```text
   ................................                                       [100%]
   32 passed, 2 subtests passed in 1.32s
   ```

   The replay-fence regression was also run separately on this tree:

   ```sh
   TMPDIR="$PWD/.tmp-r7" PYTHONDONTWRITEBYTECODE=1 \
     /Users/edr/code/JouleWise/.venv/bin/python -m pytest -p no:cacheprovider \
     tests/test_paper_replay_fence.py -q
   ```

   ```text
   ........s                                                                [100%]
   8 passed, 1 skipped in 0.47s
   ```

   Remove `.tmp-r7/` after the run; it is disposable test scratch, not custody evidence.

## Open gaps (NEEDS-RULING candidates)

1. **DS-28 / PG-04 shape:** each draft cell promises both `F+B` and signed clearance, but the registry binds only clearance/shortfall and supplies no two-quantity rendering contract (`docs/paper/results-fill-registry.md:801`, `:811`; rehearsal finding 5 at `docs/paper/fill-rehearsal-2026-08-27.md:300-301`). Rule the exact cell syntax before those STOP sentences may be retired.
2. **Claim-side bound:** DS-29 and PG-05 have no supplier. `deterministic_bounds.total` is expressly forbidden as a substitute (`docs/paper/results-fill-registry.md:367`; renderer guard `scripts/render_results_fills.py:975-978`). Build and register the field before either sizing sum renders.
3. **Gamma ignored by input v1:** the manifest accepts `gamma`, but `render_from_manifest` never reads it (`scripts/render_results_fills.py:945-999`). Decode hand fills therefore require the explicit `contrast_id` route above; the entire prompt token family and generic outcome tokens remain missing (`docs/paper/results-fill-registry.md:803-826`).
4. **C1/C2 stop-site discrepancy:** code stops a one-window-pass route at the first D-123 reported mean (`scripts/render_results_fills.py:979-989`), not at `[B_decode_claim_J]` as the task shorthand states. The registry and rehearsal agree with code; rule whether the brief should be corrected.
5. **D-123 reported means:** no schema fixes the point estimate, composed endpoints, authenticated per-token companion, or admitted-bundle count (`docs/paper/results-fill-registry.md:321-351`). Until one lands, DS-09/10/12-14/16-18/20-22/24 and line 276 stay omitted.
6. **Characterization writer absent:** the frozen schema names report fields, but this checkout has no authenticated command that writes `characterization_result_report.json`; input v1 also has no report path. Do not hand-build it (`docs/paper/fill-rehearsal-2026-08-27.md:34-39`, `:296-304`).
7. **TERM fence coverage:** the official replay fence compares 43 Section 2 literals but does not consume the prospective floor artifacts or `term-dominance.json` (`docs/paper/results-fill-registry.md:668-676`; `scripts/check_paper_replay_fence.py:562-588`). The inline Batch-2 check closes the arithmetic locally, but a durable item-26/item-34 replay-fence supplier is still absent.
8. **Outcome-C title:** registry item 28 binds PRIMARY when dominance reproduces and NULL-OUTCOME when it does not, but it does not say which title applies when evidence is refused and dominance is unevaluated (`docs/paper/results-fill-registry.md:263-272`). Keep the placeholder title for C until ruled.
9. **Aggregate/extraction field-name mismatch:** the task example names `aggregate-floor-artifact.json → cells[].operative_floor_j`, but that field exists on extraction rows (`joulewise/floor_extraction.py:1377-1384`), while aggregate cells publish `floor_gate_j` (`joulewise/detection_floor.py:1635-1642`). This checklist follows producing code and the registry.
10. **Release and diagnostic writers:** DG-071, DG-075, and DS-34 have no declared issued statistic/locator schema. Their raw or conceptual values are not fill authority (`docs/paper/results-fill-registry.md:627`, `:631`, `:807`).

There are no unverified-field markers in this checklist: every named field is anchored to producing code or a registry row; missing contracts are stated as missing rather than guessed.
