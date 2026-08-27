```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "blocked",
  "completion": "partial",
  "summary": "TERM A is exactly derivable and passes 4/4 emitted-diagnostic proofs; TERM B and the per-cell aggregation require magistrate rulings.",
  "workspace": {
    "base_requested": "/Users/edr/code/JouleWise-wt-r2",
    "base_mode": "exact",
    "head_start": "99b2bbca311490ae3665d4b4fa983fed5a4f9ac4",
    "head_end": "99b2bbca311490ae3665d4b4fa983fed5a4f9ac4",
    "upstream_end": "2bc5daabc347035208eaf0ac8204225ba69b89d0",
    "branch": "paper/t26-round2"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "No code or contract defines one scalar per-cell TERM A/B aggregation.",
        "evidence": "The code preserves absolute and comparative diagnostics separately; only the drift-widened publication gate has a max aggregation."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The actual dominance operand is not the emitted full corner-widened guarded floor.",
        "evidence": "The predicate compares a derived linear residual/contrast corner maximum with TERM A; all four available diagnostic cases show it differs from corner_widened_guarded_floor_j."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The required blind Fable verification cannot be run from this delegated session.",
        "evidence": "Bridge protocol section 8 makes delegated sessions ineligible for consult_fable."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/private/tmp/t26_term_a_self_consistency.py /Users/edr/code/JouleWise-wt-r2/df-ph-decode-floor-mint1.json /Users/edr/JouleWise-measurement-20260813/df-ph-decode-floor-mint1.json /Users/edr/JouleWise-measurement-20260818/df-ph-decode-floor-mint1.json /Users/edr/JouleWise-window-custody/shakedown-20260818/clone/df-ph-decode-floor-mint1.json /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SUMMARY\\tloaded_paths=5\\tunique_payloads=2\\tdiagnostics_checked=4\\tpass=4\\tfail=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SUMMARY.*diagnostics_checked=4.*pass=4.*fail=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "rg -l --hidden --glob '*.json' '\"point_floor_diagnostic(s)?\"' /Users/edr/JouleWise-measurement-20260813 /Users/edr/JouleWise-measurement-20260818 /Users/edr/JouleWise-window-custody /Users/edr/JouleWise-backup",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "/Users/edr/JouleWise-window-custody/shakedown-20260818/clone/df-ph-decode-floor-mint1.json",
          "/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "detection-floor-extraction\\.json$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Choose a per-cell TERM aggregation and cell-level truth rule.",
      "needs": "Rule between scalar max and componentwise comparison, and state whether cell success means all components or any component."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Ruling item 26(ii) conflates two different code quantities.",
      "needs": "Choose the exact predicate operand or the emitted full corner-widened guarded floor; if the latter, acknowledge that it defines a different dominance test."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Blind Fable check not executed because this WRITE_SCOPE session is delegated.",
      "needs": "Launch one blind read-only Fable seat from an eligible top-level session and adjudicate it against this Sol report."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Available proof payloads do not exercise a non-reference or null guard factor.",
      "needs": "Keep the replay fence exact and rerun it on every newly issued claim-bearing artifact."
    }
  ]
}
```
## Findings

### F1 — blocker — TERM A is exact componentwise, but no scalar cell aggregation exists

For a model × phase cell at index `c`, the exact point-only identities are:

```text
U_A_abs(c) = max(
    cells[c].absolute.max_abs_residual_j,
    cells[c].absolute.prediction_component_j
)

A_abs_guarded(c) =
    cells[c].absolute.guard_factor * U_A_abs(c)
    when cells[c].absolute.guard_factor is not null;
    otherwise the emitted guarded value is null and the predicate uses U_A_abs(c).

U_A_cmp(c) = max(
    cells[c].comparative.max_abs_delta_j,
    cells[c].comparative.prediction_component_j
)

A_cmp_guarded(c) =
    cells[c].comparative.guard_factor * U_A_cmp(c)
    when cells[c].comparative.guard_factor is not null;
    otherwise the emitted guarded value is null and the predicate uses U_A_cmp(c).
```

Every input above is an unconditional aggregate-artifact field. The absolute builder writes `max_abs_residual_j`, `prediction_component_j`, and `guard_factor` into the component record before the conditional metadata call (`joulewise/detection_floor.py:1454-1470`). The comparative builder does the same for `max_abs_delta_j` (`joulewise/detection_floor.py:1494-1510`). `build_floor_cell` always copies the component records to `cells[].absolute` and `cells[].comparative` (`joulewise/detection_floor.py:1641-1642`). The diagnostic function performs exactly the two maxima and guard multiplications above (`joulewise/detection_floor.py:787-803`); the dominance predicate uses the guarded result and falls back to the unguarded result only when the guarded result is null (`joulewise/detection_floor.py:820-823`). The emitted `guard_factor` itself is sufficient input; its code-side derivation is frozen separately at `joulewise/detection_floor.py:664-672`.

The component diagnostic is conditional, not its parents. `_add_attribution_limit_metadata` adds `point_floor_diagnostic` only after the component predicate is true (`joulewise/detection_floor.py:844-855`), and the validator forbids that metadata when the predicate is false (`joulewise/detection_floor.py:3295-3313`). The desk identity therefore remains available in both positive and negative outcomes.

What the code does **not** write down is one arithmetic operator from `(A_abs_guarded, A_cmp_guarded)` to a scalar per-cell TERM A. It preserves a component-keyed map (`joulewise/detection_floor.py:1658-1667`) and runs the dominance predicate on one `FloorEstimate` at a time (`joulewise/detection_floor.py:806-841`). The evidence-backed candidates are:

1. `max(A_abs_guarded, A_cmp_guarded)`, by analogy to the only scalar component composition already defined for a cell: `floor_gate_j = max(floor_abs_j, floor_cmp_j)` (`joulewise/detection_floor.py:1630-1640`; `docs/paper/results-fill-registry.md:104-107`). The mint contract explicitly says component maximum, never sum (`docs/paper/results-fill-registry.md:118-119`). This is an analogy, not a TERM A rule.
2. Keep `(A_abs_guarded, A_cmp_guarded)` as an ordered component pair and evaluate two componentwise comparisons. This exactly preserves the predicate's code domain and the emitted diagnostic structure, but it does not produce the ruling's requested single term per cell.
3. For a cell-level Boolean only, the current label container is added when **any** component is attribution-limited (`joulewise/detection_floor.py:1647-1653`). That is not an energy aggregation and is not equivalent to either a scalar-max comparison or an all-components requirement.

A sum has contrary evidence and is not a candidate. Choosing among the three semantics above is NEEDS-RULING; the ruling's falsifier can change outcome under that choice.

### F2 — blocker — TERM B in the prose ruling is not the TERM B the predicate computes

The predicate's exact right-hand dominance operand is derived from fields the aggregate artifact emits unconditionally.

For the absolute component, with `n = cells[c].absolute.n`, `r_i = cells[c].absolute.residuals_j[i]`, `w_i = cells[c].absolute.admissible_half_widths_j[i]`, and `W = math.fsum(cells[c].absolute.admissible_half_widths_j)`:

```text
B_abs_predicate(c) = max_i(
    abs(r_i) + w_i * (n - 1) / n + (W - w_i) / n
)
```

That is the expression at `joulewise/detection_floor.py:824-834`. For the comparative component, with `d_i = cells[c].comparative.block_deltas_j[i]` and `w_i = cells[c].comparative.admissible_half_widths_j[i]`:

```text
B_cmp_predicate(c) = max_i(abs(d_i) + w_i)
```

`_linear_corner_widened_max` establishes that identity (`joulewise/detection_floor.py:735-745`), and the predicate calls it at `joulewise/detection_floor.py:835-838`. The actual test is strict `B_component_predicate > A_component` (`joulewise/detection_floor.py:811-841`). Neither predicate operand is emitted as a named aggregate-artifact scalar; both are desk-derivable from the exact paths above.

The quantities literally named “corner widened” in the artifact are instead already emitted unconditionally as:

- `cells[c].absolute.corner_widened_guarded_floor_j`
- `cells[c].comparative.corner_widened_guarded_floor_j`

The builders place them in every component record (`joulewise/detection_floor.py:1465-1467`, `joulewise/detection_floor.py:1505-1507`). They are the guarded maximum of the **complete** floor over every admissible-set corner, including the Student-t prediction component, not merely the linear maximum used in the predicate. The full-corner enumerator is `joulewise/detection_floor.py:859-914`; the absolute and comparative estimators apply it at `joulewise/detection_floor.py:943-947` and `joulewise/detection_floor.py:966-970`; validation recomputes it at `joulewise/detection_floor.py:3132-3155`. The guarded/unguarded identity is enforced at `joulewise/detection_floor.py:1428-1435`.

Therefore ruling item 26(ii), which says the corner-widened floor is “the quantity the code's own dominance predicate compares” (`docs/process_traces/2026-08-27-t26/paper-goal-consult/03-MAGISTRATE-RULING.md:223-226`), joins two nonidentical quantities. The executed table below confirms they differ in every available diagnostic case. The code settles what the predicate does; it does not settle which half of the prose ruling the magistrate intends to preserve.

`floor_gate_j` is different again. The component builders add the whole-window drift allowance to the corner-widened guarded value (`joulewise/detection_floor.py:1298-1340`, with the corner values passed at `joulewise/detection_floor.py:1471-1477` and `joulewise/detection_floor.py:1511-1517`). `build_floor_cell` then takes the maximum of those two drift-widened components (`joulewise/detection_floor.py:1620-1640`). Comparing `floor_gate_j` with TERM A would test timing plus drift versus repeatability, not the ruled predicate.

Recommendation for ruling: if the intended claim is “the code's attribution-dominance condition holds,” use the exact derived predicate operands above and report the full corner-widened guarded floor plus `floor_gate_j` separately. If the intended TERM B is the emitted full corner-widened guarded floor, amend the claim to say it is a new desk comparison rather than the code's predicate.

### F3 — blocker — blind Fable verification is still owed

This prompt carries `WRITE_SCOPE`, so the repository classifies this as a delegated session. Contract §8 states that only an actually top-level Codex lead may invoke `consult_fable` and that a delegated session is ineligible (`docs/contracts/bridge_protocol.md:642-653`); the transitional language repeats that a visibly delegated caller must not invoke it (`docs/contracts/bridge_protocol.md:655-673`). I therefore did not create a non-authority-bearing pseudo-check. This report supplies the Sol half only. A separate top-level blind Fable seat must check both the TERM A identity and the TERM B conflict before item 26's two-family verification requirement is satisfied.

### Executed self-consistency proof

**Diagnostic-era instrument evidence only. None of the values in this subsection is a paper-facing result or a current instrument property.**

Repository and named corpus discovery found five real physical artifact paths but only two unique byte payloads. Four paths are byte-identical copies of `df-ph-decode-floor-mint1.json`; the other payload is the retained 7B extraction artifact. Synthetic test fixtures were not treated as real evidence. The two unique payloads contain four emitted diagnostic instances total.

The proof recomputes the entire diagnostic object from unconditional fields, checks exact IEEE-754 binary64 identity for `guarded_floor_j`, and compares canonical UTF-8 JSON bytes for the complete emitted-versus-derived diagnostic object. It uses no tolerance. The retained extraction artifact uses its own emitted unconditional paths `cells[].floor.max_abs_deviation_j`, `cells[].floor.prediction_component_j`, and `cells[].floor.guard_factor`; those are written at `joulewise/floor_extraction.py:1319-1340`, and its diagnostic identity is independently implemented at `joulewise/floor_extraction.py:1675-1696` and emitted at `joulewise/floor_extraction.py:1391-1403`.

Script, verbatim (`/private/tmp/t26_term_a_self_consistency.py`):

```python
#!/usr/bin/env python3
"""Exact self-consistency proof for emitted point-floor diagnostics."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any, Iterable


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def binary64(value: float | None) -> str:
    if value is None:
        return "null"
    return struct.pack(">d", value).hex()


def derived_diagnostic(record: dict[str, Any], max_key: str) -> dict[str, Any]:
    point_unguarded = max(record[max_key], record["prediction_component_j"])
    guard_factor = record["guard_factor"]
    point_guarded = (
        guard_factor * point_unguarded if guard_factor is not None else None
    )
    return {
        "label": "repeatability_diagnostic",
        "published_claim_floor": False,
        "unguarded_floor_j": point_unguarded,
        "guard_factor": guard_factor,
        "guarded_floor_j": point_guarded,
    }


def aggregate_cases(
    document: dict[str, Any],
) -> Iterable[tuple[str, str, dict, str, dict]]:
    for cell_index, cell in enumerate(document.get("cells", [])):
        diagnostics = cell.get("point_floor_diagnostics")
        if not isinstance(diagnostics, dict):
            continue
        for component, max_key in (
            ("absolute", "max_abs_residual_j"),
            ("comparative", "max_abs_delta_j"),
        ):
            emitted = diagnostics.get(component)
            record = cell.get(component)
            if isinstance(emitted, dict) and isinstance(record, dict):
                location = f"cells[{cell_index}].point_floor_diagnostics.{component}"
                yield location, component, record, max_key, emitted


def extraction_cases(
    document: dict[str, Any],
) -> Iterable[tuple[str, str, dict, str, dict]]:
    for cell_index, cell in enumerate(document.get("cells", [])):
        emitted = cell.get("point_floor_diagnostic")
        record = cell.get("floor")
        kind = cell.get("kind")
        if (
            isinstance(emitted, dict)
            and isinstance(record, dict)
            and kind in {"absolute", "comparative"}
        ):
            location = f"cells[{cell_index}].point_floor_diagnostic"
            yield location, kind, record, "max_abs_deviation_j", emitted


def predicate_operand(record: dict[str, Any], kind: str) -> float:
    widths = record["admissible_half_widths_j"]
    values = record.get("residuals_j")
    if values is None:
        values = record.get("block_deltas_j")
    if values is None:
        values = record["deviations_j"]
    if kind == "absolute":
        n = record["n"]
        width_sum = math.fsum(widths)
        return max(
            abs(residual)
            + width * (n - 1) / n
            + (width_sum - width) / n
            for residual, width in zip(values, widths, strict=True)
        )
    return max(
        abs(delta) + width
        for delta, width in zip(values, widths, strict=True)
    )


def main(arguments: list[str]) -> int:
    if not arguments:
        print("usage: t26_term_a_self_consistency.py ARTIFACT.json [...]", file=sys.stderr)
        return 2

    payloads: dict[str, tuple[dict[str, Any], list[Path]]] = {}
    for raw_path in arguments:
        path = Path(raw_path).resolve()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        document = json.loads(raw)
        if digest in payloads:
            payloads[digest][1].append(path)
        else:
            payloads[digest] = (document, [path])
        print(f"LOADED\t{path}\tsha256={digest}")

    print("TERM_A_SELF_CONSISTENCY_TABLE")
    print(
        "sha256_12\tlocation\tguard_factor\tmax_abs\tprediction_component_j"
        "\temitted_guarded_floor_j\tderived_guarded_floor_j"
        "\tbinary64_exact\tcanonical_diagnostic_bytes_exact\tresult"
    )
    checked = 0
    failures = 0
    all_cases: list[tuple[str, str, dict, str, dict, str]] = []
    for digest, (document, aliases) in payloads.items():
        cases = [*aggregate_cases(document), *extraction_cases(document)]
        print(f"PAYLOAD\t{digest}\taliases={len(aliases)}\tdiagnostics={len(cases)}")
        for alias in aliases:
            print(f"ALIAS\t{digest[:12]}\t{alias}")
        for location, kind, record, max_key, emitted in cases:
            all_cases.append((location, kind, record, max_key, emitted, digest))
            derived = derived_diagnostic(record, max_key)
            emitted_guarded = emitted["guarded_floor_j"]
            derived_guarded = derived["guarded_floor_j"]
            bits_exact = binary64(emitted_guarded) == binary64(derived_guarded)
            object_exact = canonical_json_bytes(emitted) == canonical_json_bytes(derived)
            ok = bits_exact and object_exact
            checked += 1
            failures += int(not ok)
            print(
                "\t".join(
                    [
                        digest[:12],
                        location,
                        repr(record["guard_factor"]),
                        repr(record[max_key]),
                        repr(record["prediction_component_j"]),
                        repr(emitted_guarded),
                        repr(derived_guarded),
                        "yes" if bits_exact else "no",
                        "yes" if object_exact else "no",
                        "PASS" if ok else "FAIL",
                    ]
                )
            )

    print("TERM_B_CODE_OPERAND_VS_EMITTED_CORNER_TABLE")
    print(
        "sha256_12\tlocation\tkind\tpredicate_uncertainty_max"
        "\tcorner_widened_guarded_floor_j\tbinary64_exact_same"
    )
    for location, kind, record, _max_key, _emitted, digest in all_cases:
        operand = predicate_operand(record, kind)
        corner = record["corner_widened_guarded_floor_j"]
        print(
            "\t".join(
                [
                    digest[:12],
                    location,
                    kind,
                    repr(operand),
                    repr(corner),
                    "yes" if binary64(operand) == binary64(corner) else "no",
                ]
            )
        )

    print(
        f"SUMMARY\tloaded_paths={len(arguments)}\tunique_payloads={len(payloads)}"
        f"\tdiagnostics_checked={checked}\tpass={checked - failures}\tfail={failures}"
    )
    return 0 if checked and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

Replay command:

```sh
set -o pipefail
/private/tmp/t26_term_a_self_consistency.py \
  /Users/edr/code/JouleWise-wt-r2/df-ph-decode-floor-mint1.json \
  /Users/edr/JouleWise-measurement-20260813/df-ph-decode-floor-mint1.json \
  /Users/edr/JouleWise-measurement-20260818/df-ph-decode-floor-mint1.json \
  /Users/edr/JouleWise-window-custody/shakedown-20260818/clone/df-ph-decode-floor-mint1.json \
  /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json
```

Actual output:

```text
LOADED	/Users/edr/code/JouleWise-wt-r2/df-ph-decode-floor-mint1.json	sha256=559ab5ede19e5aba4110fca2177773458ac93d3248d3f7d143cc86d2071188a8
LOADED	/Users/edr/JouleWise-measurement-20260813/df-ph-decode-floor-mint1.json	sha256=559ab5ede19e5aba4110fca2177773458ac93d3248d3f7d143cc86d2071188a8
LOADED	/Users/edr/JouleWise-measurement-20260818/df-ph-decode-floor-mint1.json	sha256=559ab5ede19e5aba4110fca2177773458ac93d3248d3f7d143cc86d2071188a8
LOADED	/Users/edr/JouleWise-window-custody/shakedown-20260818/clone/df-ph-decode-floor-mint1.json	sha256=559ab5ede19e5aba4110fca2177773458ac93d3248d3f7d143cc86d2071188a8
LOADED	/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json	sha256=bd87d5c4a70405daa222e696ab16b61883299bddd55982c0b5efb9ae6719309a
TERM_A_SELF_CONSISTENCY_TABLE
sha256_12	location	guard_factor	max_abs	prediction_component_j	emitted_guarded_floor_j	derived_guarded_floor_j	binary64_exact	canonical_diagnostic_bytes_exact	result
PAYLOAD	559ab5ede19e5aba4110fca2177773458ac93d3248d3f7d143cc86d2071188a8	aliases=4	diagnostics=2
ALIAS	559ab5ede19e	/Users/edr/code/JouleWise-wt-r2/df-ph-decode-floor-mint1.json
ALIAS	559ab5ede19e	/Users/edr/JouleWise-measurement-20260813/df-ph-decode-floor-mint1.json
ALIAS	559ab5ede19e	/Users/edr/JouleWise-measurement-20260818/df-ph-decode-floor-mint1.json
ALIAS	559ab5ede19e	/Users/edr/JouleWise-window-custody/shakedown-20260818/clone/df-ph-decode-floor-mint1.json
559ab5ede19e	cells[0].point_floor_diagnostics.absolute	1.0	0.30838469309418315	0.49344826888709603	0.49344826888709603	0.49344826888709603	yes	yes	PASS
559ab5ede19e	cells[0].point_floor_diagnostics.comparative	1.0	0.4656968055385384	0.6303242282254147	0.6303242282254147	0.6303242282254147	yes	yes	PASS
PAYLOAD	bd87d5c4a70405daa222e696ab16b61883299bddd55982c0b5efb9ae6719309a	aliases=1	diagnostics=2
ALIAS	bd87d5c4a704	/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/detection-floor-extraction.json
bd87d5c4a704	cells[0].point_floor_diagnostic	1.0	2.8040148280468884	2.4355438977235115	2.8040148280468884	2.8040148280468884	yes	yes	PASS
bd87d5c4a704	cells[1].point_floor_diagnostic	1.0	5.588784748106221	6.272522068625748	6.272522068625748	6.272522068625748	yes	yes	PASS
TERM_B_CODE_OPERAND_VS_EMITTED_CORNER_TABLE
sha256_12	location	kind	predicate_uncertainty_max	corner_widened_guarded_floor_j	binary64_exact_same
559ab5ede19e	cells[0].point_floor_diagnostics.absolute	absolute	2.1546708898450326	2.9398659385551955	no
559ab5ede19e	cells[0].point_floor_diagnostics.comparative	comparative	2.779249999417285	6.795813690761627	no
bd87d5c4a704	cells[0].point_floor_diagnostic	absolute	5.702572579475676	5.739261320079253	no
bd87d5c4a704	cells[1].point_floor_diagnostic	comparative	8.967896541590406	13.442917900148409	no
SUMMARY	loaded_paths=5	unique_payloads=2	diagnostics_checked=4	pass=4	fail=0
```

The TERM A result is clean: every available emitted diagnostic reproduced exactly. The TERM B comparison table is intentionally not a pass/fail test; its `no` entries prove that the predicate operand and the emitted full corner-widened guarded floor are different quantities in the available evidence.

### Replay-fence specification (not implemented)

The TERM A/B fence should follow the existing fence's fail-closed shape: unique anchored extraction (`scripts/check_paper_replay_fence.py:103-120`), authenticated input bytes (`scripts/check_paper_replay_fence.py:303-328`), re-derivation from parents rather than copying the quoted result (`scripts/check_paper_replay_fence.py:331-380`), exact-double comparison (`scripts/check_paper_replay_fence.py:22-29`, `scripts/check_paper_replay_fence.py:466-482`), and distinct mismatch-versus-artifact-unavailable exits (`scripts/check_paper_replay_fence.py:41-54`).

It should:

1. Accept the issued aggregate artifact and its frozen pinset/receipt as inputs; authenticate their exact SHA-256 bytes. Do not hard-code an unissued artifact path.
2. Run `joulewise.detection_floor.validate_floor_artifact` with the authenticated pinset and require an empty error list. That validator re-derives component statistics and authenticates exact pinset bytes (`joulewise/detection_floor.py:4146-4162`). Because the validator's numeric checks use a tolerance (`joulewise/detection_floor.py:2040-2047`), the TERM fence must add its own exact comparisons.
3. Bind exactly one cell for each registry role: alpha prompt, alpha decode, beta prompt, and beta decode. The exact `cell_id` literals must come from the issued frozen packs/pinsets; missing, duplicate, null-component, or wrong-role selections fail closed.
4. Bind these artifact literals: `schema_version`; `method.method_id`; `method.absolute_formula`; `method.comparative_formula`; `method.small_sample_guard.rule_id`; `method.small_sample_guard.formula`; `method.small_sample_guard.minimum_n`; `method.small_sample_guard.reference_n`; the selected cell's exact key coordinates; and every exact field path used in the identities above. The accepted values must come from the frozen pack/pinset authority, not this historical proof.
5. Recompute `U_A_abs`, `A_abs_guarded`, `U_A_cmp`, and `A_cmp_guarded` from the unconditional fields. Where a diagnostic exists, require exact complete-object agreement. Where it does not exist, derive TERM A without treating absence as a negative value. A null guard follows the code's unguarded fallback for predicate replay, but an artifact without an operative claim-bearing floor remains `STOP_FILL` under the existing branch rules.
6. After the magistrate resolves F2, bind TERM B to exactly one algorithm: either the linear predicate identities or the complete-corner identities. If the complete-corner interpretation is chosen, independently enumerate the full corners with the code's algorithm and compare exactly with each emitted `corner_widened_guarded_floor_j`; do not substitute `floor_gate_j`.
7. After F1 is resolved, bind the chosen component-to-cell operator and Boolean truth rule as literals. Recompute the cell result; never infer the operator from the data.
8. Read back the registry/rendered result literals from unique anchored rows, apply only a registry-authorized formatting rule, and require exact agreement with the derived values. An absent formatting rule is `STOP_FILL`, not permission to invent one.
9. Exit success only when all four cells pass. Use distinct nonzero exits for extraction/schema mismatch, arithmetic/value mismatch, and unavailable or unauthenticated artifact bytes so missing evidence cannot pass.

### Proposed results-fill-registry rows

The registry columns below exactly match `docs/paper/results-fill-registry.md:150-151`, and `STOP_FILL` is used because it explicitly covers an unissued governing verdict (`docs/paper/results-fill-registry.md:60-68`). The bracketed strings are proposed registry tokens, not emitted artifact field names. They are not frozen by this report.

| Exact token | Producing artifact and output field | Campaign / cell role | Fill rule | Freeze status and resolution | Sources |
|---|---|---|---|---|---|
| `[TERM_A_1p5B_prompt_J]` | Prospective aggregate floor artifact, alpha prompt cell; candidate `max(cells[].absolute.guard_factor * max(cells[].absolute.max_abs_residual_j, cells[].absolute.prediction_component_j), cells[].comparative.guard_factor * max(cells[].comparative.max_abs_delta_j, cells[].comparative.prediction_component_j))` | alpha / prompt dominance TERM A | STOP_FILL | Proposed key / VALUE_UNISSUED; aggregation NEEDS-RULING; reject null or missing required parents | DF, MINT, PLAN |
| `[TERM_B_1p5B_prompt_J]` | Same cell; NEEDS-RULING between `max(cells[].absolute.corner_widened_guarded_floor_j, cells[].comparative.corner_widened_guarded_floor_j)` and an aggregation of the exact derived predicate operands | alpha / prompt dominance TERM B | STOP_FILL | Proposed key / VALUE_UNISSUED; TERM B semantics and aggregation NEEDS-RULING | DF, MINT, PLAN |
| `[TERM_A_1p5B_decode_J]` | Prospective aggregate floor artifact, alpha decode cell; same exact TERM A candidate identity | alpha / decode dominance TERM A | STOP_FILL | Proposed key / VALUE_UNISSUED; aggregation NEEDS-RULING; reject null or missing required parents | DF, MINT, PLAN |
| `[TERM_B_1p5B_decode_J]` | Same cell; same exact TERM B alternatives | alpha / decode dominance TERM B | STOP_FILL | Proposed key / VALUE_UNISSUED; TERM B semantics and aggregation NEEDS-RULING | DF, MINT, PLAN |
| `[TERM_A_7B_prompt_J]` | Prospective aggregate floor artifact, beta prompt cell; same exact TERM A candidate identity | beta / prompt dominance TERM A | STOP_FILL | Proposed key / VALUE_UNISSUED; aggregation NEEDS-RULING; reject null or missing required parents | DF, MINT, PLAN |
| `[TERM_B_7B_prompt_J]` | Same cell; same exact TERM B alternatives | beta / prompt dominance TERM B | STOP_FILL | Proposed key / VALUE_UNISSUED; TERM B semantics and aggregation NEEDS-RULING | DF, MINT, PLAN |
| `[TERM_A_7B_decode_J]` | Prospective aggregate floor artifact, beta decode cell; same exact TERM A candidate identity | beta / decode dominance TERM A | STOP_FILL | Proposed key / VALUE_UNISSUED; aggregation NEEDS-RULING; reject null or missing required parents | DF, MINT, PLAN |
| `[TERM_B_7B_decode_J]` | Same cell; same exact TERM B alternatives | beta / decode dominance TERM B | STOP_FILL | Proposed key / VALUE_UNISSUED; TERM B semantics and aggregation NEEDS-RULING | DF, MINT, PLAN |

If the magistrate chooses componentwise dominance instead of scalar aggregation, these eight rows are the wrong shape: TERM A and TERM B need absolute/comparative component rows, plus a separately ruled cell-level Boolean. I have not silently expanded the token set.

### NEEDS-RULING items

1. **Question:** What maps the absolute and comparative TERM A/B components to the ruling's one scalar per cell, and what makes a cell pass? **Options considered:** scalar maximum; exact componentwise pair with all-components success; existing any-component label semantics. **Recommendation:** preserve the componentwise predicate as the scientific primitive, then explicitly define any scalar summary as presentation-only. **Blocked work:** freezing the eight proposed registry derivations and the replay-fence operator.
2. **Question:** Does TERM B mean the exact linear operand used by `admissible_set_uncertainty_dominates_point_floor`, or the emitted complete `corner_widened_guarded_floor_j`? **Options considered:** exact predicate operand; full emitted corner-widened guarded floor; `floor_gate_j` (rejected because it includes drift). **Recommendation:** use the exact predicate operand for the registered dominance claim, report the other two quantities separately, and correct item 26(ii)'s gloss. **Blocked work:** final TERM B identities, dominance verdicts, and registry rows.
3. **Question:** Are the proposed `[TERM_A_*]` and `[TERM_B_*]` token names accepted? **Options considered:** the neutral TERM labels above; semantic names after F1/F2 are ruled. **Recommendation:** defer naming until F1/F2 are resolved, then use semantic names that state the chosen quantity. **Blocked work:** key freeze only; the field-level derivation is complete.

### Places the derivation could be wrong, and what settles each

| Possible failure | Why it matters | What settles it |
|---|---|---|
| The component-to-cell operator is not `max`. | A scalar dominance verdict can reverse relative to componentwise comparisons. | Magistrate ruling F1, then a literal-bound fence test. |
| TERM B is interpreted as the full emitted corner floor although the code predicate uses the linear operand. | It changes the proposition under test. | Magistrate ruling F2 and corresponding paper wording. |
| A future artifact changes the method or schema while retaining familiar field names. | The desk formula could replay the wrong method. | Bind artifact hash, pinset, `schema_version`, method literals, and commit authority in the fence. |
| A claim-bearing component is null, missing, refused, or smoke-only. | The guarded identity or scalar aggregation is not available. | Existing artifact validation plus `STOP_FILL`; never substitute zero or another cell. |
| Absolute TERM B is recomputed with ordinary `sum` instead of `math.fsum`, or with a different member order. | Exact binary64 output can change. | Use the exact emitted array order and `math.fsum`, then exact-double tests. |
| A desk implementation recomputes `guard_factor` instead of consuming the emitted field. | A method mismatch could be hidden. | Consume the exact emitted `guard_factor`; separately check it against the bound method literal. |
| The historical extraction schema's generic `max_abs_deviation_j` is mistaken for the aggregate schema's component-specific field. | A script could read the wrong parent or invent a path. | Schema-specific adapters as in the executed proof; the prospective fence targets only the aggregate schema. |
| Validator success is treated as byte-for-value proof. | `validate_floor_artifact` permits a bounded numeric tolerance. | The additional exact binary64 and canonical-object comparisons specified above. |
| Conditional diagnostic absence is interpreted as a false or zero TERM A. | It makes the falsifier circular or biased positive. | Always derive from unconditional parents; presence is used only for self-consistency. |
| The available proof is assumed to cover non-reference or null guards. | It does not exercise those arithmetic branches empirically. | New emitted cases or focused generated fixtures for branch mechanics, followed by real `_v4` replay. |
| The Sol result is treated as satisfying the blind Fable requirement. | It violates item 26's independent-check order. | Eligible top-level blind Fable review and lead adjudication. |

## Residual risk

The artifact census covered the current repository and the named measurement/custody roots available to this session. It found two unique real payloads; all observed diagnostics use the reference guard branch, and all are positive-emission cases because the code forbids the diagnostic on the negative branch. Thus the arithmetic identity is source-proven and exactly self-consistent where observable, but empirical coverage does not include a non-reference guard or a negative emitted diagnostic. Prospective `_v4` artifacts are not yet issued, so this report contains no paper-facing measurement result.

Authorized output file byte size (post-write): `00035720` bytes.
