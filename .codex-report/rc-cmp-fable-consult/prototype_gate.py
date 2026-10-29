#!/usr/bin/env python3.13
"""RC-CMP-FABLE-CONSULT prototype: a producer-derived input gate in front of the comparator.

Nothing in production is edited. The gate wraps scripts/compare_b5_recompute.py in memory and
runs on the lane's own synthetic fixtures (tests/independent_recompute). Three gates:

  G1  strict + canonical load. L9 writes both step-11 outputs with one writer shape
      (fill: joulewise/results_fill_adapter.py render_results_fill_input; disclosure record:
      joulewise/calibration_ledger.py canonical_json_bytes, via b5_analysis/disclosures.py):
      json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False),
      the fill with one trailing newline. L9's own readers (kept_units._strict_json,
      results_fill_adapter._object) refuse a repeated member. So: refuse a duplicate key,
      refuse a nonfinite token, and refuse any byte string that is not the canonical
      serialisation of its own parse. The parse is then the unique reading of the bytes.
  G2  owner-only identity. An identity field (contrast_id, cell_id, pack, model, run_id, ...)
      may appear only on the object it names: a list item of a declared collection. The
      declared attribute positions (a band's pack) are the only exceptions. Anything else
      refuses before any binding is built. Closes the nested-identity re-route (Opus F1,
      Sol 1) at the shape, not at binding().
  G3  literal routing ids. Every id that routes a binding must be, byte for byte, one of the
      registered ids (configs/campaigns/*_v5/extraction_spec.json, analysis_manifest_v3.json
      on origin/main). No substring parsing decides where a number goes. Closes Sol 3.

Run from the repo root:
  TMPDIR=/tmp/jwfc-tmp PYTHONPATH=.:tests JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 \
    python3.13 .codex-report/rc-cmp-fable-consult/prototype_gate.py
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
os.environ.setdefault("JW_B5_SYNTHETIC_ONLY", "1")
from tests.independent_recompute import test_review_fixes as t  # noqa: E402
from tests.independent_recompute import test_structural_rules as s  # noqa: E402

cmp, FILL, DISC, VERD = t.cmp, t.FILL, t.DISCLOSURE, t.VERDICTS
DECODE, PREFILL = s.DECODE, s.PREFILL
CODED = t.BARS["recompute_coded_7e322b76"]


class Gate(Exception):
    """A step-11 output refused before comparison; the code names the shape."""


# ---------------------------------------------------------------- G1: strict + canonical load
# (kind, name pattern, trailing bytes) from L9's two writers.
WRITERS = (("fill", r"outputs/[0-9a-f]{64}-results-fill-input\.json", b"\n"),
           ("disclosure", r"disclosures/[0-9a-f]{64}\.json", b""))


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise Gate("l9_output_duplicate_key:" + key)
        result[key] = value
    return result


def _nonfinite(word):
    raise Gate("l9_output_nonfinite:" + word)


def canonical(value, tail=b""):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8") + tail


def strict_load(raw, tail):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    if canonical(value, tail) != raw:
        raise Gate("l9_output_not_canonical")
    return value


# ---------------------------------------------------------------- G2: owner-only identity
IDENTITY = set(cmp.IDENTITY_FIELDS)
# Objects that an identity field names, from the producers: the fill's contrast rows and their
# leave-one-out rows (results_fill_adapter.adapt_claim_verdicts); the disclosure record's _item()
# lines in cells, floors, contrasts, window_lines/<pack> and block_lines, the loo_magnitude rows,
# and the sensitivity record's cell and contrast entries (b5_analysis/disclosures.py).
OWNERS = (r"gamma/contrasts/\*", r"gamma/contrasts/\*/loo/rows/\*",
          r"(cells|floors|contrasts|block_lines)/\*", r"contrasts/\*/rows/\*", r"window_lines/[a-z]+/\*",
          r"sensitivity/(reported_cells|floor_cells|contrasts)/\*")
# Identity-named fields that are attributes of another object, never the object's own name.
ATTRIBUTES = (r"window_lines/[a-z]+/\*/central_band/pack",)


def owner_check(value, path=""):
    if isinstance(value, dict):
        for key, item in value.items():
            here = path + "/" + key if path else key
            if key in IDENTITY and not isinstance(item, (dict, list)):
                if not any(re.fullmatch(p, path) for p in OWNERS) and not any(re.fullmatch(p, here) for p in ATTRIBUTES):
                    raise Gate("identity_field_misplaced:" + here)
            owner_check(item, here)
    elif isinstance(value, list):
        for item in value:
            owner_check(item, path + "/*")


# ---------------------------------------------------------------- G3: literal routing ids
# Registered ids, byte for byte (origin/main, 2026-10-29). In production these are read from the
# sealed configs, never typed here.
REGISTERED = {
    "cell_id": {f"d117-df-{kind}ph-{phase}-{model}{suffix}"
                for model in ("qwen3-1p7b", "qwen3-8b") for phase in ("decode", "prefill-p42", "prefill-p2048")
                for kind, suffix in (("", "-absolute"), ("cmp-abba-", ""))}
               | {f"d117-reported-mean-ph-{phase}-{model}"
                  for model in ("qwen3-1p7b", "qwen3-8b") for phase in ("decode", "prefill-p42", "prefill-p2048")},
    "contrast_id": {DECODE, PREFILL},
}
ROUTED = ((r"gamma/contrasts/\*/contrast_id", "contrast_id"), (r"contrasts/\*/contrast_id", "contrast_id"),
          (r"(cells|floors)/\*/cell_id", "cell_id"), (r"sensitivity/[a-z_]+/\*/cell_id", "cell_id"))


def id_check(value, path=""):
    if isinstance(value, dict):
        for key, item in value.items():
            here = path + "/" + key if path else key
            for pattern, kind in ROUTED:
                if re.fullmatch(pattern, here) and item not in REGISTERED[kind]:
                    raise Gate(f"routing_id_unregistered:{here}:{item}")
            id_check(item, here)
    elif isinstance(value, list):
        for item in value:
            id_check(item, path + "/*")


# ---------------------------------------------------------------- harness
def fresh():
    case = t.Case()
    case.setUp()
    return case


def write_custody(case, raw_overrides=()):
    """The fixture's custody written the way L9 writes it (canonical bytes), with raw overrides."""
    root = case.root / ("custody-%d" % len(list(case.root.glob("custody-*"))))
    outputs = []
    for name, value in case.files.items():
        tail = next((tail for _, pattern, tail in WRITERS if re.fullmatch(pattern, name)), b"")
        raw = dict(raw_overrides).get(name) or canonical(value, tail)
        path = root / cmp.RESTRICTED / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
    (root / cmp.RECORD).write_text(json.dumps({"steps": [{"step": "11", "window": None, "status": "ok",
                                                           "outputs": outputs}]}))
    return root


def gate(root):
    """Every step-11 output through G1, G2, G3; the first refusal names the shape."""
    for kind, pattern, tail in WRITERS:
        for path in sorted((root / cmp.RESTRICTED).rglob("*")):
            name = path.relative_to(root / cmp.RESTRICTED).as_posix()
            if re.fullmatch(pattern, name):
                value = strict_load(path.read_bytes(), tail)
                owner_check(value)
                id_check(value)
    return "accepted"


def compare(case, root):
    ours = case.root / ("ours-%d.json" % len(list(case.root.glob("ours-*.json"))))
    ours.write_text(json.dumps(case.ours))
    out = case.root / ("restricted-%d.json" % len(list(case.root.glob("restricted-*.json"))))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
        code = cmp.main(["--l9-custody", str(root), "--recompute", str(ours), "--bars", str(CODED),
                         "--restricted-out", str(out)])
    result = json.loads(out.read_text())
    cover = result.get("coverage", {})
    return code, err.getvalue().strip(), (case.fails(result) if "counts" in result else result.get("refused")), \
        [(u["path"], u["reason"]) for u in cover.get("unbound", [])]


def show(label, case, raw_overrides=(), expect=None):
    root = write_custody(case, raw_overrides)
    try:
        verdict = gate(root)
    except Gate as exc:
        verdict = "REFUSED " + str(exc)
    code, err, fails, unbound = compare(case, root)
    print(f"{label}\n    gate={verdict}\n    comparator alone: exit={code} stderr={err!r} fails={fails} unbound={unbound}")
    if expect is not None:
        ok = (verdict.startswith("REFUSED") if expect == "refuse" else verdict == "accepted")
        print("    expected gate " + expect + ": " + ("OK" if ok else "MISMATCH"))
    return verdict, code


def raw(case, name, before, after):
    text = canonical(case.files[name], b"\n" if name == FILL else b"").decode()
    assert before in text, before
    return {name: text.replace(before, after, 1).encode()}


def main():
    print("# RC-CMP-FABLE-CONSULT prototype gate on the lane fixtures (synthetic only)\n")
    print("## A. Controls (the gate must accept what L9 writes)")
    show("A1 baseline fixture, canonical bytes", fresh(), expect="accept")
    case = fresh()
    case.files[FILL]["gamma"]["contrasts"][0]["j_per_token"] = None
    show("A2 registered null (j_per_token) on a J contrast", case, expect="accept")
    case = fresh()
    case.files[FILL]["gamma"]["contrasts"].reverse()
    case.files[DISC]["contrasts"].reverse()
    show("A3 keyed lists in the other order (list order is content, still canonical)", case, expect="accept")
    case = fresh()
    s.v3_floor(case)
    show("A4 v3 floor with arm gates and resolutions (attributes, not identities)", case, expect="accept")
    case = fresh()
    verdict_floor, fill_floor = s.v3_floor(case)
    for floor in (verdict_floor, fill_floor):
        floor["arm_gates"][1].update(status="refused", floor_gate_j=None)
    case.ours["floor_cells"]["Qwen3-8B-4bit/decode"]["floor_gate_j"] = None
    show("A5 refused arm gate printed null on both sides (Opus Q6; the comparator's refusal is a ruling, not the gate's)",
         case, expect="accept")
    case = fresh()
    case.files[DISC]["window_lines"] = {"alpha": [{"line": "machine_summary", "model": "qwen3-1p7b",
                                                  "central_band": {"pack": "alpha", "lower": 0.9, "upper": 1.1}}]}
    show("A6 a band's pack is a declared attribute (ATTRIBUTES), accepted by G2; no meter in this fixture so the comparator refuses",
         case, expect="accept")
    case = fresh()
    case.files[DISC]["floors"] = [{"line": "floor_composition", "pack": "alpha",
                                   "cell_id": "d117-df-ph-decode-qwen3-1p7b-absolute", "guarded_j": 42.0}]
    show("A7 floor_composition line with the registered absolute cell id", case, expect="accept")
    case = fresh()
    case.files[DISC]["floors"] = [{"line": "floor_composition", "pack": "alpha",
                                   "cell_id": "d117-df-cmp-abba-ph-decode-qwen3-1p7b", "guarded_j": 42.0}]
    show("A8 floor_composition line with the REGISTERED comparative spelling (extraction_spec.json): the gate accepts; "
         "the comparator's suffix parser (floor_kind) cannot resolve it", case, expect="accept")

    print("\n## B. Round-3 witnesses (a wrong printed number passed the comparator with exit 0)")
    case = fresh()
    s.v3_floor(case)
    decode = next(r for r in case.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == DECODE)
    prefill = next(r for r in case.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == PREFILL)
    decode["floor"] = {"contrast_id": PREFILL, "active_floor_j": 103.5}
    prefill["floor"] = {"contrast_id": DECODE, "active_floor_j": 120.0}
    show("B1 Opus F1 / Q3c: floors swapped, each floor object naming the other contrast", case, expect="refuse")
    case = fresh()
    next(r for r in case.files[VERD]["contrasts"] if r["contrast_id"] == PREFILL)["estimator"]["estimate"] = -2.5
    case.ours["contrasts"][PREFILL]["dbar_j"] = -2.5
    case.files[FILL]["gamma"]["contrasts"][1]["estimate"] = -2.5
    case.files[DISC]["contrasts"].append({"line": "primary_contrast", "contrast_id": DECODE,
                                          "estimator": {"estimate": -2.5, "contrast_id": PREFILL}})
    show("B2 Sol 1: a decode primary_contrast line printing prefill's estimate, re-routed by a nested contrast_id",
         case, expect="refuse")
    case = fresh()
    show("B3 Opus F2 / Sol 2: duplicate member, wrong value first, agreeing value last", case,
         raw(case, FILL, '"estimate":-1.25', '"estimate":999.0,"estimate":-1.25'), expect="refuse")
    case = fresh()
    show("B4 Sol 2: duplicate member, agreeing value first, wrong value last (the comparator already refuses this one)",
         case, raw(case, FILL, '"estimate":-1.25', '"estimate":-1.25,"estimate":999.0'), expect="refuse")
    case = fresh()
    show("B5 Sol 2: NaN erased by a later duplicate member", case,
         raw(case, FILL, '"estimate":-1.25', '"estimate":NaN,"estimate":-1.25'), expect="refuse")
    case = fresh()
    show("B6 a lone NaN (today read as null and flagged; the gate refuses at load)", case,
         raw(case, FILL, '"estimate":-1.25', '"estimate":NaN'), expect="refuse")
    case = fresh()
    case.files[DISC]["floors"] = [{"line": "floor_composition", "pack": "alpha",
                                   "cell_id": "TYPO-d117-df-ph-decode-qwen3-1p7b-absolute", "guarded_j": 42.0}]
    show("B7 Sol 3: a typo'd cell_id that substring parsing still routes", case, expect="refuse")

    print("\n## C. Shapes no producer emits, refused at the shape")
    case = fresh()
    case.files[FILL]["gamma"]["contrasts"][0]["floor"] = {"contrast_id": DECODE, "active_floor_j": 103.5}
    show("C1 a nested object repeating its owner's own contrast_id (harmless today, refused by G2)", case, expect="refuse")
    case = fresh()
    pretty = (json.dumps(case.files[FILL], indent=1) + "\n").encode()
    show("C2 the same fill pretty-printed by another writer", case, {FILL: pretty}, expect="refuse")
    case = fresh()
    unsorted = (json.dumps(case.files[FILL], separators=(",", ":")) + "\n").encode()
    unsorted = unsorted.replace(b'{"contrast_id":"' + DECODE.encode() + b'","estimate":-1.25,"n":9}',
                                b'{"estimate":-1.25,"contrast_id":"' + DECODE.encode() + b'","n":9}')
    show("C3 keys out of sorted order", case, {FILL: unsorted}, expect="refuse")
    case = fresh()
    show("C4 a number spelled 1E0 (L9's writer spells 1.0)", case,
         raw(case, FILL, '"estimate":-1.25', '"estimate":-1.25E0'), expect="refuse")

    print("\n## D. The fill's exact field set, from the producer (results_fill_adapter.adapt_claim_verdicts)")
    adapter_row = {"contrast_id", "metric", "conditions", "limitations", "floor_source_cell_ids", "estimate", "interval",
                   "decision_interval", "deterministic_widening_total", "j_per_token", "n", "floor", "multiplicity",
                   "claim_evaluation", "plan_id", "claim_role", "hypothesized_direction", "equivalence", "sampling",
                   "loo", "df", "t_critical_95", "kept_block_ids", "removed_block_ids"}
    fixture_row = set(fresh().files[FILL]["gamma"]["contrasts"][0])
    print(f"    adapter row keys: {len(adapter_row)}; fixture row keys: {sorted(fixture_row)}")
    print(f"    an exact-key schema refuses the lane's own fixture: missing {len(adapter_row - fixture_row)} keys "
          f"(the only real-shaped data is the full-size synthetic dry run, RC-CMP-4)")


if __name__ == "__main__":
    main()
