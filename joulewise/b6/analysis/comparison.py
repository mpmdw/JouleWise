"""The restricted comparison output the independent recompute joins key by key.

The independent recompute (separate seat RC-B6-1, ``lane/2026-10-27-recompute-b6``)
fails closed on any unmatched key, and its key pattern is the comparison
contract (lead decision 2, 2026-10-27; schema ``joulewise.b6_comparison_keys.v1``).
This module generates that key set from its rules (models, phases, forms and
fields).  A test asserts equality with the recompute's published file, vendored
with its source commit; nothing here reads that file or the recompute's code.

Output (restricted role ``comparison``), in the shape the recompute's
comparator reads, ``{sessions: {id: {quantities, run_phase_energy_j}}, block:
{quantities}}``, with nothing else in it (metadata goes to ``comparison_meta``):

* ``sessions/<id>/quantities``: exactly the session's pack keys (ALPHA, BETA,
  GAMMA), or, for a GAMMA session analysed alone (§12.2), the single-session
  keys, its six deferred groups waiting for the full run;
* ``sessions/<id>/run_phase_energy_j``: run phase energies keyed
  ``<run_id>/<phase>`` with phase ``decode``, ``prefill`` or ``request``;
* ``block/quantities`` (cross-block phase only): ``summary/``, ``inclusive/``
  and ``side_by_side/`` per pack and quantity, and ``replication/<contrast>/word``.

A value is a finite number, a word, a boolean or None (undefined in that
session).  A key the adapter does not supply is a tooling refusal
(``comparison_key_absent``), never a silent None.
"""
from __future__ import annotations

import fnmatch
import math
import re

KEYS_SCHEMA = "joulewise.b6_comparison_keys.v1"
VALUES_SCHEMA = "joulewise.b6_comparison_values.v1"
PACK_NAMES = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
MODELS = {"ALPHA": "qwen3-1p7b", "BETA": "qwen3-8b"}
MODEL_TAGS = ("qwen3-1p7b", "qwen3-8b")
PHASES = ("decode", "prefill-p2048")
CONTRASTS = PHASES
FORMS = ("absolute", "comparative")
RUN_PHASES = ("decode", "prefill", "request")

_FLOOR_FIELDS = ("corner_j", "floor_j", "guarded_j", "n", "operative_j", "point_j")
_REPORTED_FIELDS = ("B_j", "attribution_floor_j", "h_j", "lower_j", "mean_j", "n_b", "n_r", "per_token_j", "upper_j")
_CELL_LINE_FIELDS = ("lower_j", "mean_j", "n_b", "n_r", "upper_j")
_CONTRAST_FIELDS = ("D_j", "ceiling", "dbar_j", "decision_lower_j", "decision_upper_j", "direction", "energy_ratio",
                    "energy_ratio_lower", "energy_ratio_upper", "floor_gate_j", "holm_p", "metrology_lower_j",
                    "metrology_upper_j", "n", "outcome", "p", "per_token_j", "s_d_j", "t")
_CROSS_FIELDS = ("F_j", "G_j", "agree", "delta_j", "h_F_j", "h_G_j", "n")
_NEG8 = ("neg8/allowance_j", "neg8/bound_j", "neg8/verdict")
GAMMA_DEFERRED = ("contrast/*/outcome", "contrast/*/ceiling", "contrast/*/floor_gate_j", "dominance/branch",
                  "cross_session/*", "lines/scaled_allowance/*/outcome")


class ComparisonRefusal(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _dominance(model):
    return [f"dominance/{model}/{phase}/{form}" for phase in PHASES
            for form in ("absolute/R", "comparative/R", "comparative/R_cm")]


def _floors(model):
    keys = []
    for phase in PHASES:
        keys += [f"floor/{model}/{phase}/{form}/{field}" for form in FORMS for field in _FLOOR_FIELDS]
        keys.append(f"floor/{model}/{phase}/gate_j")
    return keys


def floor_session_keys(pack: str) -> list[str]:
    model = MODELS[pack]
    keys = ["calibration/b_op_s", *_dominance(model), *_floors(model), *_NEG8]
    for phase in PHASES:
        for line in ("battery_assist", "load_sensitivity", "waited_runs"):
            keys += [f"lines/{line}/{model}/{phase}/{field}" for field in _CELL_LINE_FIELDS]
        keys += [f"lines/scaled_allowance/{model}/{phase}/{field}" for field in ("factor", "gate_j", "lower_j", "upper_j")]
        keys += [f"lines/single_step_reconstruction/{model}/{phase}/{field}" for field in ("h_j", "mean_j", "n_b", "n_r")]
        keys += [f"reported/{model}/{phase}/{field}" for field in _REPORTED_FIELDS]
    return sorted(keys)


def gamma_session_keys() -> list[str]:
    keys = ["calibration/b_op_s", "dominance/branch", *_NEG8]
    for contrast in CONTRASTS:
        keys += [f"contrast/{contrast}/{field}" for field in _CONTRAST_FIELDS]
        for line in ("battery_assist", "load_sensitivity", "waited_runs"):
            keys += [f"lines/{line}/{contrast}/{field}" for field in ("dbar_j", "n")]
        keys += [f"lines/scaled_allowance/{contrast}/{field}" for field in ("D_j", "factor", "outcome")]
    keys += [f"cross_session/{model}/{phase}/{field}" for model in MODEL_TAGS for phase in PHASES
             for field in _CROSS_FIELDS]
    return sorted(keys)


def single_session_gamma_keys() -> list[str]:
    return [k for k in gamma_session_keys() if not any(fnmatch.fnmatchcase(k, p) for p in GAMMA_DEFERRED)]


def session_keys(pack: str, *, single_session: bool = False) -> list[str]:
    name = PACK_NAMES.get(pack, pack)
    if name == "GAMMA":
        return single_session_gamma_keys() if single_session else gamma_session_keys()
    return floor_session_keys(name)


def summarised_quantities(pack: str) -> list[str]:
    """The quantities §10, §11.1 and §11.4 print per pack, as the contract names them."""
    name = PACK_NAMES.get(pack, pack)
    if name == "GAMMA":
        return sorted(f"contrast/{c}/{f}" for c in CONTRASTS for f in ("dbar_j", "energy_ratio"))
    model = MODELS[name]
    keys = _dominance(model)
    keys += [f"floor/{model}/{phase}/{form}/{field}" for phase in PHASES for form in FORMS
             for field in ("floor_j", "operative_j")]
    keys += [f"reported/{model}/{phase}/{field}" for phase in PHASES
             for field in ("attribution_floor_j", "mean_j", "per_token_j")]
    return sorted(keys)


def block_keys() -> list[str]:
    keys = [f"replication/{c}/word" for c in CONTRASTS]
    for name in ("ALPHA", "BETA", "GAMMA"):
        for quantity in summarised_quantities(name):
            keys += [f"{line}/{name}/{quantity}/{stat}" for line in ("summary", "inclusive")
                     for stat in ("mean", "n", "sd")]
            keys.append(f"side_by_side/{name}/{quantity}/delta")
    return sorted(keys)


def contract() -> dict:
    """The key set this driver emits, in the contract file's own shape."""
    return {"schema": KEYS_SCHEMA, "model_tags": list(MODEL_TAGS), "phases": list(PHASES),
            "session_quantity_keys": {name: session_keys(name) for name in ("ALPHA", "BETA", "GAMMA")},
            "single_session_gamma_keys": single_session_gamma_keys(),
            "single_session_gamma_deferred": list(GAMMA_DEFERRED),
            "block_quantity_keys": block_keys(), "run_phase_energy_phases": list(RUN_PHASES)}


def _value(value):
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int) or (isinstance(value, float) and math.isfinite(value)):
        return value
    raise ComparisonRefusal("comparison_value_invalid")


def session_values(analysis, *, single_session: bool = False) -> dict:
    """Exactly the contract's keys for one session, from the adapter's values."""
    values = dict(analysis.quantities)
    for contrast, row in analysis.contrasts.items():
        values.setdefault(f"contrast/{contrast}/dbar_j", row.get("dbar"))
        values.setdefault(f"contrast/{contrast}/outcome", row.get("outcome"))
    out = {}
    for key in session_keys(analysis.pack, single_session=single_session):
        if key not in values:
            raise ComparisonRefusal("comparison_key_absent")
        out[key] = _value(values[key])
    return out


_RUN_KEY = re.compile(r"[^/\s]+/(decode|prefill|request)")


def run_values(analysis) -> dict:
    runs = {}
    for key, value in sorted(analysis.run_energies.items()):
        if not _RUN_KEY.fullmatch(key):
            raise ComparisonRefusal("run_energy_key_invalid")
        runs[key] = _value(value)
    return runs


def block_values(lines: dict, packs) -> dict:
    """The block keys from the cross-block lines.  A refused line refuses."""
    out = {}
    for pack in packs:
        name = PACK_NAMES[pack]
        summary, side, flagged = lines["summary"][pack], lines["side_by_side"][pack], lines["flagged_inclusive"][pack]
        if any("refused" in part for part in (summary, side, flagged)):
            raise ComparisonRefusal("comparison_line_refused")
        inclusive = flagged["summary"]
        for quantity in summarised_quantities(pack):
            for line, source in (("summary", summary), ("inclusive", inclusive)):
                row = source["quantities"].get(quantity)
                if row is None:
                    raise ComparisonRefusal("comparison_key_absent")
                for stat in ("mean", "n", "sd"):
                    out[f"{line}/{name}/{quantity}/{stat}"] = _value(row[stat])
            row = side["quantities"].get(quantity)
            if row is None:
                raise ComparisonRefusal("comparison_key_absent")
            out[f"side_by_side/{name}/{quantity}/delta"] = _value(row["delta"])
    for contrast in CONTRASTS:
        row = lines["replication"].get(contrast, {})
        if "refused" in row:
            raise ComparisonRefusal("comparison_line_refused")
        out[f"replication/{contrast}/word"] = _value(row.get("word"))
    return dict(sorted(out.items()))
