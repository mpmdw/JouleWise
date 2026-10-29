"""Deterministic block-5 disclosures, retained in restricted custody.

The producer never decides release state. Each renderable item explicitly
labels its blinding; the renderer alone redacts values and restricted codes.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
import statistics
from functools import wraps

from joulewise.calibration_ledger import canonical_json_bytes
from joulewise.flags.catalog import catalog_from_bytes
from joulewise.paper_reported_energy import PaperReportedEnergyRefusal, T975
from joulewise.analysis_engine.estimators import (
    PairedObservation, _ci_t_critical, estimate_paired_blocks,
)
from joulewise.external.km003c_parse import percentile
from .kept_units import CATALOG_PATH, _strict_json
from .steps import classify_step4_exit
from .windows import AnalysisRefusal, SealPins
from .context import rebuilt_roster
from joulewise.analysis_engine.inputs import AnalysisInputError, archived_verdict_row

SCHEMA = "joulewise.b5_disclosures.v1"
PACK_ORDER = ("alpha", "beta", "gamma")
LOAD_CODES = frozenset(("thermal.os_level_nonzero",
                        "thermal.powermetrics_pressure_elevated", "contention.request_overlap"))
SCREEN_BOUND_S = 0.03646286164497997

# analysis_plan_block5.md 257 (X is substituted twice).
ATTRIBUTION_SENTENCE = ("Phase-edge timing alone could move the energy assigned to this phase of a single request "
    "by up to X J. The average of that bound over the kept members is already inside the interval, as part of B; "
    "X itself is not added. The bound says how far the assigned energy moves when power is taken as constant "
    "within each sampler record; it is not a bound on the physical energy of the phase.")
# analysis_plan_block5.md 489–490.
GROSS_SENTENCE = ("Phase energy is gross: it includes the machine's baseline power over the phase, and the "
    "8B phase lasts longer, so part of the difference is baseline power times the extra duration.")
# analysis_plan_block5.md 575–578 (Δ is substituted).
AGREE_SENTENCE = "GAMMA's and the floor window's estimates agree within their within-window intervals (difference Δ J)."
DIFFER_SENTENCE = ("GAMMA's and the floor window's estimates differ by Δ J, more than their within-window "
    "intervals cover; the reported intervals understate between-window variation, which includes different "
    "interleaving and thermal history.")
# analysis_plan_block5.md 581–584 (k and X are substituted).
DECISION_SENTENCE = "The estimate exceeds the floor, but its decision interval reaches below the floor."
LOO_SENTENCE = ("Leaving out quad k moves the estimate by X J, more than a quarter of the floor; the "
    "direction, the floor status and the multiplicity decision are unchanged.")
# analysis_plan_block5.md 692–693.
MACHINE_BOUNDARY = ("whole-machine DC input plus the battery term, measured at the USB-C input; "
                    "the adapter's AC-to-DC loss is not included.")
# analysis_plan_block5.md 506–508.
CONDITIONALITY = ("These numbers are conditional on a window that passed the registered physical-hazard checks "
    "at arm and kept at least 5 of 10 units per stratum after the registered exclusions; the kept units of each "
    "cell are printed beside it.")
# analysis_plan_block5.md 520–522, substitute the module list.
ARM_SENTENCE = ("At this window's arm the [clock, battery, thermal, contention, disk] check returned no reading "
               "and did not refuse; the monitor measured it during the window.")
# analysis_plan_block5.md 567–569.
MONITOR_SENTENCE = ("The hazard monitor ran on efficiency cores at background priority during collection, and "
    "the whole-machine meter's reader at ordinary priority; their CPU share is disclosed and was not subtracted.")
# analysis_plan_block5.md 619–621.
MIDPOINT_SENTENCE = ("The midpoint reference was lost, so drift inside this window that reverted by its end "
                    "was not measured; the drift allowance uses the start and end references only")
# analysis_plan_block5.md 632–633, substitute S, X and the screen word.
TEMPERATURE_SENTENCE = ("Stage S warmed by X K without levelling off; the window's NEG-8 screen [passed/failed], "
                       "and the reported numbers rest on that screen, not on this reading.")
FIXED_SENTENCES = {
    # analysis_plan_block5.md 570–572.
    "single_window": ("The units of this cell were measured in one window; the interval covers variation within "
        "that window, not between days or windows. The repeats and quads are modelled as independent units; "
        "that is an assumption (D-179 dependence caveat)."),
    # analysis_plan_block5.md 334–338 (§5, referenced at 579).
    "floor_transfer_assumption": ("the shared onset and offset edge treatment calibrated on floor blocks "
        "transfers unchanged to the consuming contrast at the same block timescale"),
    "floor_transfer_limit": "the historical corpus records bounds, not realized member-level boundary errors",
    # analysis_plan_block5.md 585–586.
    "order": ("Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order; the order was not randomized, and the "
              "p-value assumes the quad differences are independent."),
    # analysis_plan_block5.md 637–638.
    "p42": ("The 42-token prefill of the decode workload is shorter than one power record and could not be "
            "resolved; as registered, no p42 value is reported."),
    # analysis_plan_block5.md 640–641 (the plan uses unquoted prose here).
    "separate_windows": ("the 1.7B and 8B reported cells were collected in separate windows in a fixed order; "
        "their difference is not a comparison (claims ladder: forced order stays below L2)."),
    # analysis_plan_block5.md 642.
    "dominance": "R is a point diagnostic with no interval; 'independent' names the independent-corner component.",
    # analysis_plan_block5.md 643.
    "d177": "phase attribution is reported without a measured instrument phase-accounting check.",
    # analysis_plan_block5.md 644.
    "fixed_prompt": "the decode contrast uses one fixed prompt; no prompt-population generality is claimed.",
}


def _plain(value):
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _item(line, restricted, text, **values):
    return {"line": line, "restricted": restricted, "label": line,
            "text": text, **_plain(values)}


def _validate_sensitivity(value):
    """Validate the fixed S9 wire shape without importing the sensitivity seat."""
    try:
        if (set(value) != {"schema_version","label","b_max","windows","reported_cells","floor_cells","contrasts"}
                or value["schema_version"] != "joulewise.b5_bracket_sensitivity.v1"
                or value["label"] != "sensitivity"):
            raise ValueError()
        bmax = value["b_max"]
        sequence = bmax["attained_by_sequence"]
        if (set(bmax) != {"value_s","attained_by_sequence","T"}
                or not _finite(bmax["value_s"]) or bmax["value_s"] < 0
                or type(bmax["T"]) is not int or bmax["T"] < 0
                or sequence is not None and (type(sequence) is not int or not 1 <= sequence <= bmax["T"])):
            raise ValueError()
        if set(value["windows"]) != set(PACK_ORDER):
            raise ValueError()
        for row in value["windows"].values():
            if (set(row) != {"plan_id","b_op_s","b_sens_s","widened"}
                    or not isinstance(row["plan_id"], str) or not row["plan_id"]
                    or any(not _finite(row[k]) or row[k] < 0 for k in ("b_op_s", "b_sens_s"))
                    or type(row["widened"]) is not bool):
                raise ValueError()
        shapes = {
            "reported_cells": ("mean_j", "h_j", "B_j", "lower_j", "upper_j", "attribution_floor_j"),
            "floor_cells": ("floor_abs_j", "floor_cmp_j", "floor_gate_j", "allowance_j"),
            "contrasts": ("floor_abs_j", "floor_cmp_j", "floor_gate_j", "D_j", "outcome"),
        }
        booleans = {"reported_cells": ("mean_and_half_width_equal_primary", "equals_primary", "not_below_primary"),
                    "floor_cells": ("equals_primary", "not_below_primary"),
                    "contrasts": ("bound_independent_values_equal_primary", "outcome_equals_primary", "not_below_primary")}
        for name, keys in shapes.items():
            if not isinstance(value[name], list):
                raise ValueError()
            for row in value[name]:
                identity = "contrast_id" if name == "contrasts" else "cell_id"
                if not isinstance(row[identity], str) or not row[identity]:
                    raise ValueError()
                if name != "contrasts" and row["pack"] not in PACK_ORDER[:2]:
                    raise ValueError()
                if name == "contrasts" and (not isinstance(row["floor_cell_ids"], list)
                        or any(not isinstance(cid, str) for cid in row["floor_cell_ids"])):
                    raise ValueError()
                if name == "reported_cells":
                    if row["status"] == "refused":
                        if set(row) != {"pack","cell_id","status","code"} or not isinstance(row["code"], str):
                            raise ValueError()
                        continue
                    if row["status"] != "computed":
                        raise ValueError()
                for side in ("primary", "sensitivity"):
                    if set(row[side]) != set(keys):
                        raise ValueError()
                    for key in keys:
                        if key == "outcome":
                            if not isinstance(row[side][key], str):
                                raise ValueError()
                        elif not _finite(row[side][key]):
                            raise ValueError()
                if any(type(row[k]) is not bool for k in booleans[name]):
                    raise ValueError()
                expected={identity,"primary","sensitivity",*booleans[name]}
                expected.update({"floor_cell_ids"} if name=="contrasts" else {"pack"})
                if name=="reported_cells":expected.add("status")
                if set(row)!=expected:raise ValueError()
        canonical_json_bytes(value)
    except (KeyError, TypeError, ValueError, OverflowError):
        raise AnalysisRefusal("sensitivity_record_invalid") from None


def engine_contrast_observations(prepared_by_id):
    """Copy engine side means and its paired B−A values, in engine block order."""
    result = {}
    for cid, prepared in prepared_by_id.items():
        estimate = prepared.get("estimate")
        paired = dict(zip(estimate.block_ids, estimate.paired_values)) if estimate is not None else {}
        rows = []
        for observation in prepared["observations"]:
            if isinstance(observation, Mapping):
                bid = observation["block_id"]
                a, b = observation.get("a_mean_j", observation.get("value_a")), observation.get(
                    "b_mean_j", observation.get("value_b"))
                delta = observation.get("d_j", paired.get(bid, b - a))
            else:
                bid, a, b = observation.block_id, observation.value_a, observation.value_b
                delta = paired.get(bid, b - a)
            rows.append({"block_id": bid, "a_mean_j": a, "b_mean_j": b, "d_j": delta})
        result[cid] = rows
    return result


def _catalog():
    raw = CATALOG_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SealPins.load().sealed["catalog_sha256"]:
        raise AnalysisRefusal("exclusions_catalog_mismatch")
    return catalog_from_bytes(raw)


def _blinding_admitted(word, entry):
    """A flag may tighten its code's catalog blinding, never loosen it.

    The sealed catalog sets blinding per flag where it says so (for example
    diagnostic.s1_structural: precheck_counts is always written RESTRICTED over
    the STRUCTURE default); a STRUCTURE word on a RESTRICTED code still refuses.
    """
    return word == entry["blinding"] or (word == "RESTRICTED" and entry["blinding"] == "STRUCTURE")


def _flags(archive, catalog):
    rows = []
    for raw in archive.output_bytes("derived/flags.jsonl").splitlines():
        if not raw.strip():
            continue
        row = _strict_json(raw, "disclosure_input_invalid")
        entry = catalog.codes.get(row.get("code"))
        if entry is None or not _blinding_admitted(row.get("blinding"), entry):
            raise AnalysisRefusal("flag_blinding_differs_from_catalog")
        if row.get("family")!=entry["family"]:
            raise AnalysisRefusal("disclosure_input_invalid")
        rows.append(row)
    return rows


def _projection_cell(view, projection):
    """Bind issuer members to one exclusions cell, including non-target p42."""
    ids = {m["bundle_id"] for m in projection["members"]}
    candidates = []
    for cell in view.cells.values():
        units = [u for us in cell.kept.values() for u in us] + list(cell.dropped)
        if {run for u in units for run in u.run_ids} == ids:
            if cell.target == ("p42" not in projection["cell_id"].split("-")):
                candidates.append(cell)
    if len(candidates) != 1:
        raise AnalysisRefusal("exclusions_plan_mismatch")
    return candidates[0]


def _assist_units(cell, flags):
    assists = {row["scope"]["run_id"] for row in flags
               if row["code"] == "battery.assist" and row["scope"]["level"] == "member"}
    units, counts = [], {s: 0 for s in cell.kept}
    for stratum, rows in cell.kept.items():
        for unit in rows:
            count = len(set(unit.run_ids) & assists)
            counts[stratum] += count
            if count:
                units.append(unit.unit_id)
    return units, counts


def _load_units(cell):
    trigger = any(set(u.codes) & LOAD_CODES for u in cell.dropped)
    restored = [u for u in cell.dropped if u.codes and set(u.codes) <= LOAD_CODES]
    return trigger, restored


def _cell_values(row):
    return {"status": "computed", "mean_j": row["mean_j"], "h_j": row["interval"]["h_j"],
            "B_j": row["interval"]["B_j"], "lower_j": row["lower_j"], "upper_j": row["upper_j"]}


def _one_unit_mean(rows, n_r):
    """O3 only; all interval estimates remain owned by the registered kernel."""
    repeats = [row["energy_j"] for row in rows[:n_r]]
    quads = [statistics.fmean(row["energy_j"] for row in rows[i:i+4])
             for i in range(n_r, len(rows), 4)]
    return 0.2 * statistics.fmean(repeats) + 0.8 * statistics.fmean(quads)


def _descriptive_cell(pack, view, cid, cell_id, estimate, minimum):
    cell = view.cell(cid)
    if min(cell.n_r, cell.n_b) == 0:
        return {"status": "not_computable"}
    # A production issuer returns refusals as rows; a callable may raise the
    # kernel's typed refusal. Catch only its below-minimum code at this call.
    try:
        result = estimate(pack, view, minimum)
    except PaperReportedEnergyRefusal as exc:
        if exc.code != "paper_reported_energy_kept_units_below_minimum":
            raise
        # Raising callables must carry their normalized rows on the exception.
        result = {"cells": [], "refused_cells": [{"cell_id": cell_id, "code": exc.code}],
                  "normalized_rows": getattr(exc, "normalized_rows", {})}
    for row in result["cells"]:
        if row["cell_id"] == cell_id:
            return _cell_values(row)
    row = next((r for r in result["refused_cells"] if r["cell_id"] == cell_id), None)
    if row is None:
        raise AnalysisRefusal("disclosure_input_missing:cell_estimates")
    if row["code"] != "paper_reported_energy_kept_units_below_minimum":
        raise PaperReportedEnergyRefusal(row["code"])
    if minimum is not None or min(cell.n_r, cell.n_b) != 1:
        raise PaperReportedEnergyRefusal(row["code"])
    rows = result.get("normalized_rows", {}).get(cell_id)
    if rows is None:
        raise AnalysisRefusal("disclosure_input_missing:normalized_rows")
    return {"status": "one_unit", "mean_j": _one_unit_mean(rows, cell.n_r)}


# Plan 8.1: the load-correlated line never replaces the primary value and never
# gates anything. A typed refusal met while computing it (for example the
# kept-member stop firing on a restored member) is that line's text, not a
# refusal of the disclosure record (early cold passes F1, S10).
_LINE_REFUSALS = (AnalysisRefusal, PaperReportedEnergyRefusal, AnalysisInputError)


def _line_refusal(exc):
    code = getattr(exc, "code", None)
    code = (code if isinstance(code, str) else str(exc)).split(":", 1)[0]
    token = code.replace("_", "").replace(".", "")
    return code if code and code[0].isalpha() and token.isalnum() and token.isascii() else "refused"


def _cell_text(value):
    if value["status"] == "refused":
        return f"not computable: {value['code']}"
    if value["status"] == "not_computable":
        return "not computable (no unit left in a stratum)"
    if value["status"] == "one_unit":
        return (f"{value['mean_j']:.5f} J; no interval (one unit); "
                "below the registered minimum of 5 units")
    return (f"{value['mean_j']:.5f} J; h = {value['h_j']:.5f} J; "
            f"interval [{value['lower_j']:.5f}, {value['upper_j']:.5f}] J")


def _paired_values(rows):
    if not rows:
        return {"status": "not_computable", "n": 0}
    if len(rows) == 1:
        return {"status": "one_quad", "n": 1, "mean_j": rows[0]["d_j"]}
    # The engine owns steps 1–4 and its rounded quantile. No Holm/floor/outcome
    # is emitted by this descriptive line.
    observations = tuple(PairedObservation(r["block_id"], 0.0, r["d_j"]) for r in rows)
    estimate = estimate_paired_blocks(observations)
    return {"status": "computed", "n": estimate.n, "mean_j": estimate.estimate,
            "s_d": estimate.sample_stddev, "se": estimate.se_repeat,
            "t_star": estimate.t_critical_95, "lower_j": estimate.metrology_aware_ci95.lower,
            "upper_j": estimate.metrology_aware_ci95.upper}


def _paired_text(value):
    if value["status"] == "refused":
        return f"not computable: {value['code']}"
    if value["status"] == "not_computable":
        return "not computable (no quad left)"
    if value["status"] == "one_quad":
        return (f"{value['mean_j']:.5f} J; no interval (one quad); "
                "below the registered minimum of 5 quads")
    return (f"{value['mean_j']:.5f} J; s_d = {value['s_d']:.5f} J; se = {value['se']:.6f} J; "
            f"t* = {value['t_star']:.3f}; interval [{value['lower_j']:.5f}, {value['upper_j']:.5f}] J")


def _phase(cid):
    return "decode" if "decode" in cid.split("-") else "prefill"


def _energy_lines(result, windows, archives, kept, projections, extraction_reports,
                  artifact, verdicts, observe, estimate, flags):
    primary_observations = observe(kept["gamma"])
    verdict_by_id = {r["contrast_id"]: r for r in verdicts["contrasts"]}
    # All descriptive contrast lines, including cross-window lines, must use
    # the same primary observations as the verdict before any line is built.
    for cid, rows in primary_observations.items():
        est = verdict_by_id[cid]["estimator"]
        value = _paired_values(rows)
        if (len(rows) != est["n"]
                or float(value["mean_j"]).hex() != float(est["estimate"]).hex()
                or float(value["s_d"]).hex() != float(est["s_d"]).hex()):
            raise AnalysisRefusal("contrast_observations_differ_from_verdict")
    for pack in PACK_ORDER[:2]:
        view = kept[pack]
        for row in projections[pack]["cells"]:
            cid = row["cell_id"]
            cell = _projection_cell(view, row)
            primary = _cell_values(row)
            result["cells"].append(_item("reported_cell", True,
                f"{pack} {cid}: " + _cell_text(primary), pack=pack, cell_id=cid, **primary))
            units, counts = _assist_units(cell, flags[pack])
            without = view.without_units(cell.cell_id, units, label="battery-assist") if units else view
            c2 = without.cell(cell.cell_id)
            second = _descriptive_cell(pack, without, cell.cell_id, cid, estimate, None) if units else dict(primary)
            text = (f"{pack} {cid}: with assisted members: {_cell_text(primary)}; "
                    f"without assisted members (n_r = {c2.n_r}, n_b = {c2.n_b}): {_cell_text(second)}; "
                    f"assist members: repeat {counts.get('repeat', 0)}, quad {counts.get('quad', 0)}")
            if not units:
                text += "; no assisted member; without equals with"
            if min(c2.n_r, c2.n_b) < 5 and second["status"] == "computed":
                text += "; below the registered minimum of 5 units"
            result["cells"].append(_item("battery_assist_cell", True, text, pack=pack, cell_id=cid,
                primary=primary, without=second, n_r=c2.n_r, n_b=c2.n_b, assist_members=counts,
                removed_unit_ids=units))
            trigger, restored = _load_units(cell)
            if trigger:
                counts_r = Counter(u.stratum for u in restored)
                families = sorted({f for u in cell.dropped if set(u.codes) & LOAD_CODES for f in u.families})
                text = (f"{pack} {cid}: sensitivity: load-correlated physics exclusions "
                        "(thermal pressure, contention) not applied")
                values = {}
                if restored:
                    try:
                        changed = view.with_units_restored(cell.cell_id, [u.unit_id for u in restored], label="load-correlated")
                        c2 = changed.cell(cell.cell_id)
                        values = _descriptive_cell(pack, changed, cell.cell_id, cid, estimate, 5)
                        text += f" (n_r = {c2.n_r}, n_b = {c2.n_b}): " + _cell_text(values)
                    except _LINE_REFUSALS as exc:
                        values = {"status": "refused", "code": _line_refusal(exc)}
                        text += ": " + _cell_text(values)
                else:
                    text += ": no unit restored"
                text += (f"; restored repeat {counts_r['repeat']}, quad {counts_r['quad']}; "
                         f"code families: {', '.join(families)}")
                result["cells"].append(_item("load_correlated_cell", True, text, pack=pack, cell_id=cid,
                    restored_counts=dict(counts_r), families=families, values=values))
            floor = row["attribution_floor"]["value_j"]
            result["cells"].append(_item("attribution_floor", True,
                ATTRIBUTION_SENTENCE.replace("X", f"{floor:.5f}"), pack=pack, cell_id=cid, value_j=floor,
                attained_by=row["attribution_floor"]["attained_by"], minimum_j=row["attribution_floor"]["minimum_j"]))
            if not cell.target:
                continue
            matches = [obs for contrast_id, obs in primary_observations.items() if _phase(contrast_id) == row["phase"]]
            if len(matches) == 1 and len(matches[0]) >= 2:
                sides = [r["a_mean_j" if pack == "alpha" else "b_mean_j"] for r in matches[0]]
                G = statistics.fmean(sides)
                h_G = T975[len(sides)-1] * statistics.stdev(sides) / math.sqrt(len(sides))
                delta = G - primary["mean_j"]
                agree = abs(delta) <= math.hypot(h_G, primary["h_j"])
                text = (AGREE_SENTENCE if agree else DIFFER_SENTENCE).replace("Δ", f"{delta:.5f}")
                result["cells"].append(_item("cross_window", True, text, pack=pack, cell_id=cid,
                    G_j=G, h_G_j=h_G, F_j=primary["mean_j"], h_F_j=primary["h_j"], delta_j=delta, agree=agree))
        for row in extraction_reports[pack]["cells"]:
            floor = row.get("floor")
            if floor is None:
                continue
            cid = row["cell_id"]
            guarded = floor["guarded_floor_j"]
            allowance = floor["whole_window_drift_allowance_j"]
            widened = floor["drift_widened_guarded_floor_j"]
            if guarded is None:
                continue
            if guarded + allowance != widened:
                raise AnalysisRefusal("floor_report_composition_inconsistent")
            source = _strict_json(archives[pack].output_bytes("derived/neg8-allowance.json"),
                                  "disclosure_input_invalid")["source"]
            form = "absolute" if row["kind"] == "absolute" else "comparative"
            minted = []
            for mint in artifact["cells"]:
                if mint.get("provenance", {}).get(form, {}).get("calibration_cell_id") == cid:
                    minted.append(mint["floor_abs_j" if form == "absolute" else "floor_cmp_j"])
            if len(minted) != 1:
                raise AnalysisRefusal("disclosure_input_missing:minted_floor")
            result["floors"].append(_item("floor_composition", True,
                f"{pack} {cid}: guarded operative floor {guarded:.5f} J; allowance added {allowance:.5f} J "
                f"from {source}; drift-widened {widened:.5f} J; minted floor {minted[0]:.5f} J", pack=pack,
                cell_id=cid, guarded_j=guarded, allowance_j=allowance, source=source,
                drift_widened_j=widened, minted_j=minted[0]))
    if result["floors"]:
        result["fixed_sentences"].append(_item("floor_drift_ownership", False,
            "Each contrast's floor carries the floor window's drift allowance; the contrast's decision interval carries GAMMA's."))
    kept_ids = {cid: {r["block_id"] for r in rows} for cid, rows in primary_observations.items()}
    for cid, rows in primary_observations.items():
        cell = kept["gamma"].for_contrast(cid)
        verdict = verdict_by_id[cid]
        est = verdict["estimator"]
        primary = {"status": "computed", "n": est["n"], "mean_j": est["estimate"],
                   "s_d": est["s_d"], "se": est["SE_total"], "t_star": est["t_critical_95"],
                   "lower_j": est["metrology_aware_CI95"]["lower"],
                   "upper_j": est["metrology_aware_CI95"]["upper"]}
        result["contrasts"].append(_item("primary_contrast", True,
            f"{cid}: {_paired_text(primary)}", contrast_id=cid,
            estimator=_plain(verdict["estimator"]), decision_interval=_plain(verdict["deterministic_bounds"]["decision_interval"])))
        units, counts = _assist_units(cell, flags["gamma"])
        changed = kept["gamma"].without_units(cid, units, label="battery-assist") if units else kept["gamma"]
        without = [r for r in rows if r["block_id"] not in units]
        value = _paired_values(without)
        text = f"{cid}: without quads holding assisted members (n = {value['n']}): {_paired_text(value)}; assist quads {len(units)}"
        if 1 < value["n"] < 5:
            text += "; below the registered minimum of 5 quads"
        result["contrasts"].append(_item("battery_assist_contrast", True, text, contrast_id=cid,
            **value, assist_quads=len(units), assist_members=counts))
        trigger, restored = _load_units(cell)
        if trigger:
            families = sorted({f for u in cell.dropped if set(u.codes) & LOAD_CODES for f in u.families})
            text = f"{cid}: sensitivity: load-correlated physics exclusions (thermal pressure, contention) not applied"
            value = {}
            if restored:
                try:
                    changed = kept["gamma"].with_units_restored(cid, [u.unit_id for u in restored], label="load-correlated")
                    value = _paired_values(observe(changed)[cid])
                    text += f" (n = {value['n']}): {_paired_text(value)}"
                except _LINE_REFUSALS as exc:
                    value = {"status": "refused", "code": _line_refusal(exc)}
                    text += ": " + _paired_text(value)
            else:
                text += ": no unit restored"
            text += f"; restored quads {len(restored)}; code families: {', '.join(families)}"
            result["contrasts"].append(_item("load_correlated_contrast", True, text,
                contrast_id=cid, restored_count=len(restored), families=families, values=value))
        if len(rows) >= 2 and all(r["a_mean_j"] > 0 and r["b_mean_j"] > 0 for r in rows):
            logs = [math.log(r["b_mean_j"] / r["a_mean_j"]) for r in rows]
            rho, sd = statistics.fmean(logs), statistics.stdev(logs)
            half = T975[len(rows)-1] * sd / math.sqrt(len(rows))
            ratio, lo, hi = math.exp(rho), math.exp(rho-half), math.exp(rho+half)
            result["contrasts"].append(_item("magnitude_ratio", True,
                f"{cid}: registered descriptive estimates: ratio of phase energies, 8B to 1.7B: "
                f"{ratio:.4f} [{lo:.4f}, {hi:.4f}]. Recorded timing bounds are not propagated into it",
                contrast_id=cid, log_mean=rho, log_sd=sd, ratio=ratio, lower=lo, upper=hi))
        else:
            result["contrasts"].append(_item("magnitude_ratio", True,
                f"{cid}: registered descriptive estimates: ratio not computable", contrast_id=cid))
        denom = 512 if _phase(cid) == "decode" else 2048
        est = verdict["estimator"]
        decision = verdict["deterministic_bounds"]["decision_interval"]
        metrology = est["metrology_aware_CI95"]
        value = est["estimate"] / denom
        result["contrasts"].append(_item("magnitude_per_token", True,
            f"{cid}: registered descriptive estimates: {value:.6f} J per "
            f"{'output' if denom == 512 else 'prompt'} token; metrology interval "
            f"[{metrology['lower']/denom:.6f}, {metrology['upper']/denom:.6f}]; decision interval "
            f"[{decision['lower']/denom:.6f}, {decision['upper']/denom:.6f}]", contrast_id=cid,
            value_j=value, denominator=denom, metrology={k:v/denom for k,v in metrology.items()},
            decision={k:v/denom for k,v in decision.items()}))
        n = est["n"]
        result["contrasts"].append(_item("contrast_interval", True,
            f"{cid}: the rounded t* ({_ci_t_critical(n-1):.3f} for {T975[n-1]:.6f}); "
            "no metrology term is added for the phase metrics, and errors common to all members are carried by D "
            "and the attribution floor.", contrast_id=cid, n=n, rounded_t=_ci_t_critical(n-1), exact_t=T975[n-1]))
        floor = verdict["floor"]["active_floor_j"]
        near = decision["lower"] if est["estimate"] >= 0 else -decision["upper"]
        text = f"{cid}: decision interval near end {near:.5f} J; floor {floor:.5f} J"
        if abs(est["estimate"]) > floor and near <= floor:
            text += "; " + DECISION_SENTENCE
        result["contrasts"].append(_item("decision_floor", True, text, contrast_id=cid,
            decision_interval=decision, floor_j=floor, estimate_j=est["estimate"]))
        loo = verdict["loo"]["rows"]
        own_numbers={_block_number(bid) for bid in kept_ids[cid]}
        other_numbers=set().union(*({_block_number(bid) for bid in ids} for other,ids in kept_ids.items() if other != cid))
        exclusive=sorted(own_numbers-other_numbers,key=lambda n:(not n.isdigit(),int(n) if n.isdigit() else n)) if len(kept_ids)>1 else []
        result["contrasts"].append(_item("loo_counts", False,
            f"{cid}: leave-one-out rows {len(loo)}; block numbers only this contrast kept: " +
            (", ".join(exclusive) or "none"), contrast_id=cid,
            count=len(loo), exclusive_block_numbers=exclusive))
        magnitude_rows = []
        for row in loo:
            if "estimate_magnitude" in row["influence_triggers"]:
                k = _block_number(row["omitted_block_id"])
                movement = abs(row["estimate"] - est["estimate"])
                magnitude_rows.append({"block_number": k, "movement_j": movement})
        magnitude_rows.sort(key=lambda r: (not r["block_number"].isdigit(),
            int(r["block_number"]) if r["block_number"].isdigit() else r["block_number"]))
        text = f"{cid}: " + (" ".join(LOO_SENTENCE.replace("quad k", "quad " + r["block_number"])
            .replace("X", f"{r['movement_j']:.5f}") for r in magnitude_rows) if magnitude_rows else
            "no leave-one-out row raised the magnitude trigger")
        result["contrasts"].append(_item("loo_magnitude", True, text, contrast_id=cid, rows=magnitude_rows))
    if primary_observations:
        result["fixed_sentences"].append(_item("gross_energy", False, GROSS_SENTENCE))
    _machine_lines(result, windows, archives, kept, projections, flags)


def _block_number(bid):
    import re
    match = re.search(r"(?:b|block-?)(\d+)$", bid)
    return str(int(match[1])) if match else bid


def _meter_member_model(archive, window, member):
    """Resolve an archived member's config with the harvest's path rule."""
    config_path = member.get("config_path")
    if not isinstance(config_path, str):
        raise AnalysisRefusal("disclosure_input_missing:meter_member_model")
    relative = ("sources/repo/" + config_path if config_path.startswith("configs/") else
                f"sources/repo/configs/campaigns/{window.pack_id}/" + config_path)
    config = _strict_json(archive.source_bytes(relative), "disclosure_input_invalid")
    identifier = config["model"]["name"]
    return {"Qwen3-1.7B-4bit": "qwen3-1p7b", "Qwen3-8B-4bit": "qwen3-8b"}.get(identifier, identifier)


def _machine_lines(result, windows, archives, kept, projections, flags):
    bands = {}
    for pack in sorted(PACK_ORDER, key=lambda p: windows[p].record.entry.t0_epoch_s):
        archive = archives[pack]
        # Meter absent is a recorded descriptive state; never open bundles.
        try:
            meter_raw=archive.withheld_bytes("withheld/meter.json")
        except AnalysisRefusal as exc:
            if exc.code!="archive_withheld_unreadable" or not any(r["code"]=="meter.absent" for r in flags[pack]):raise
            result["window_lines"][pack].append(_item("machine_absent", False, "whole-machine meter: absent"))
            result["window_lines"][pack].append(_item("machine_boundary", False, MACHINE_BOUNDARY))
            continue
        meter = _strict_json(meter_raw, "disclosure_input_invalid")
        roster = _strict_json(archive.output_bytes("derived/roster.json"), "disclosure_input_invalid")
        models = {r["run_id"]: r.get("model") for r in roster["members"] if r.get("model")}
        if pack != "gamma":
            model = "qwen3-1p7b" if pack == "alpha" else "qwen3-8b"
            full_roster = rebuilt_roster(archive, archived_verdict_row(archive))
            by_run = {member["run_id"]: member for member in full_roster["members"]}
            models = {}
            for run in meter["members"]:
                member = by_run.get(run)
                if member is None:
                    raise AnalysisRefusal("disclosure_input_missing:meter_member_model")
                if member.get("kind") == "science":
                    models[run] = model
                else:
                    try:
                        identifier = _meter_member_model(archive, windows[pack], member)
                        if not isinstance(identifier, str) or not identifier:
                            raise ValueError()
                    except (AnalysisRefusal, KeyError, TypeError, ValueError):
                        raise AnalysisRefusal("disclosure_input_missing:meter_member_model") from None
                    models[run] = identifier
        else:
            for cell in kept[pack].cells.values():
                for unit in (*cell.kept["quad"], *cell.dropped):
                    models.update({run: "qwen3-1p7b" if i in (0,3) else "qwen3-8b"
                                   for i,run in enumerate(unit.run_ids)})
            missing=set(meter["members"])-models.keys()
            if missing:
                full_roster=rebuilt_roster(archive,archived_verdict_row(archive))
                for member in full_roster["members"]:
                    if member["run_id"] not in missing:continue
                    models[member["run_id"]] = _meter_member_model(archive, windows[pack], member)
        window_flags = sorted({r["code"] for r in flags[pack] if r["code"].startswith("meter.")
                               and r["scope"]["level"] == "window"})
        grouped = {}
        for run, row in sorted(meter["members"].items()):
            model = models.get(run)
            if model is None:
                raise AnalysisRefusal("disclosure_input_missing:meter_member_model")
            rho, rail = row["rho"], row["rail_delta_J"]
            machine = (row.get("machine") or {}).get("delta_J")
            removed = run in kept[pack].removed_run_ids()
            own_flags = sorted({r["code"] for r in flags[pack] if r["code"].startswith("meter.")
                                and r["scope"].get("run_id") == run})
            suffix = "; removed by the exclusion function" if removed else ""
            if not _finite(rho):
                text = f"{run}: not computable" + suffix
                plausible = False
            else:
                plausible = 0 < rho <= 1 and _finite(rail) and _finite(machine) and machine-rail >= 0
                text = f"{run}: ΔE_rail {rail:.5f} J; ΔE_machine {machine:.5f} J; ρ {rho:.4f}" + suffix
                if not plausible:
                    text += "; outside the hard band; meter flags: " + ", ".join(sorted(set(own_flags+window_flags)))
            result["window_lines"][pack].append(_item("machine_member", True, text, model=model,
                run_id=run, rho=rho, rail_j=rail, machine_j=machine, removed=removed,
                plausible=plausible, meter_flags=sorted(set(own_flags+window_flags)),
                battery_term_available=(row.get("machine") or {}).get("battery_available")))
            grouped.setdefault(model, []).append((rho, plausible, own_flags))
        for model, rows in sorted(grouped.items()):
            all_rhos = [r for r,_,_ in rows if _finite(r)]
            plausible = [r for r,p,_ in rows if p]
            values = {}
            text = f"{pack} {model}: whole-machine cross-check"
            if all_rhos:
                lo, hi = min(all_rhos), max(all_rhos)
                med = statistics.median(all_rhos)
                q1, q3 = percentile(all_rhos,25), percentile(all_rhos,75)
                values.update(median=med,minimum=lo,maximum=hi,q25=q1,q75=q3)
                text += f"; median {med:.4f}; range {lo:.4f} to {hi:.4f}; IQR {q1:.4f} to {q3:.4f}"
            if plausible:
                spread = (max(plausible)-min(plausible))/statistics.median(plausible)
                values["spread"] = spread
                text += f"; plausible spread {spread:.4f}; " + ("consistent" if spread<=.2 else "not consistent")
            clean = not window_flags and not any(r["code"]=="meter.battery_activity" for r in flags[pack])
            if model not in bands and clean and plausible:
                bands[model] = (pack, windows[pack].plan_id, windows[pack].attempt, min(plausible), max(plausible))
            if model in bands:
                bp, plan, attempt, low, high = bands[model]
                text += f"; first clean window for {model}: {bp} {plan} attempt {attempt}; central band {low:.4f} to {high:.4f}"
                if bp != pack:
                    count = sum(low<=r<=high for r in all_rhos)
                    text += f"; {count} of {len(all_rhos)} member windows inside the first clean window's band"
                values["central_band"]={"pack":bp,"plan_id":plan,"attempt":attempt,"lower":low,"upper":high}
            else:
                text += "; no clean window; no central band"
            result["window_lines"][pack].append(_item("machine_summary", True,text,model=model,**values))
        result["window_lines"][pack].append(_item("machine_boundary", False, MACHINE_BOUNDARY))


def _code(code, catalog, flags):
    # The flag's own word was checked in _flags; preserve it beside the code.
    words = {r["blinding"] for r in flags if r["code"] == code}
    entry = catalog.codes.get(code)
    if entry is None or any(not _blinding_admitted(word, entry) for word in words):
        raise AnalysisRefusal("flag_blinding_differs_from_catalog")
    if not words:
        raise AnalysisRefusal("disclosure_input_missing:flag_blinding")
    # Where flags of one code carry two words, the code is shown as the stricter.
    return {"code": code, "blinding": "RESTRICTED" if "RESTRICTED" in words else entry["blinding"]}


def _kept_lines(result, kept, projections, reports, catalog, flags, archives):
    for pack in PACK_ORDER:
        groups = []
        if pack == "gamma":
            groups = [(cid,cell,"contrasts") for cid,cell in kept[pack].cells.items()]
        else:
            groups = [(r["cell_id"],_projection_cell(kept[pack],r),"cells") for r in projections[pack]["cells"]]
            if reports[pack]["cells"]:
                prefix = f"sources/repo/configs/campaigns/{kept[pack].window.pack_id}/"
                spec = _strict_json(archives[pack].source_bytes(prefix+"extraction_spec.json"),"disclosure_input_invalid")
                specs = {r["cell_id"]:r for r in spec["cells"]}
                groups += [(r["cell_id"],kept[pack].for_floor_cell(specs[r["cell_id"]])[0],"floors")
                           for r in reports[pack]["cells"]]
        for cid,cell,section in groups:
            text = (f"{pack} {cid}: kept quads {cell.n_b}" if pack=="gamma" else
                    f"{pack} {cid}: kept units n_r = {cell.n_r}, n_b = {cell.n_b}")
            result[section].append(_item("kept_units",False,text,pack=pack,cell_id=cid,n_r=cell.n_r,n_b=cell.n_b))
            for unit in cell.dropped:
                result[section].append({"line":"removed_unit","restricted":False,"label":"removed unit",
                    "pack":pack,"cell_id":cid,"unit_id":unit.unit_id,"stratum":unit.stratum,
                    "families":list(unit.families),"codes":[_code(c,catalog,flags[pack]) for c in unit.codes],
                    "positions":list(unit.positions),"stage_ids":list(unit.stage_ids)})


def _trigger_values(record):
    bracket = record.calibration_bracket
    if bracket is None:
        return None
    result={"observed_triggers":list(bracket.get("observed_triggers",())),
            "recorded_only_triggers":list(bracket.get("recorded_only_triggers",())),
            "doubling_count":(bracket.get("corpus_doubling") or {}).get("count"),
            "systematic_sequences":list(bracket.get("other_session_systematic_sequences",()))}
    if (any(type(t) is not str for k in ("observed_triggers","recorded_only_triggers") for t in result[k])
            or result["doubling_count"] is not None and (type(result["doubling_count"]) is not int or result["doubling_count"]<0)
            or any(type(n) is not int or n<0 for n in result["systematic_sequences"])):
        raise AnalysisRefusal("disclosure_input_invalid")
    return result


def _trigger_text(values):
    if values is None:
        return "not recorded by this harvest's program"
    return ("triggers on record: " + (", ".join(values["observed_triggers"]) or "none") +
            "; recorded-only triggers: " + (", ".join(values["recorded_only_triggers"]) or "none") +
            f"; corpus doubling count: {values['doubling_count'] if values['doubling_count'] is not None else 'not recorded'}; "
            "other-session systematic sequences: " + (", ".join(str(n) for n in values["systematic_sequences"]) or "none"))


def _history_lines(result,index,records):
    for superseded in (False,True):
        entries = [r for r in records if (r.entry.seal != "second") == superseded]
        if superseded and entries:
            result["block_lines"].append(_item("superseded_history",False,"Superseded first-seal attempts:"))
        for pack in PACK_ORDER:
            history = sorted((r for r in entries if r.entry.pack==pack),key=lambda r:r.entry.attempt)
            if not history:
                continue
            causes = ", ".join(r.entry.cause_key or "none" for r in history)
            result["block_lines"].append(_item("attempt_count",False,
                f"{pack}: attempts of this pack: {len(history)} (causes {causes})",pack=pack,
                superseded=superseded,count=len(history),causes=[r.entry.cause_key for r in history]))
            for record in history:
                e=record.entry
                text=f"{pack} {e.plan_id} attempt {e.attempt}: {record.verdict}; cause key {e.cause_key or 'none'}"
                values={"pack":pack,"plan_id":e.plan_id,"attempt":e.attempt,"verdict":record.verdict,
                        "cause_key":e.cause_key,"superseded":superseded}
                if record.kind=="no_archive":
                    text += "; not harvested"
                else:
                    yield_counts=record.yield_counts or {}
                    # The pinned yield document has counts under window.
                    counts=yield_counts.get("window",yield_counts)
                    collected=counts.get("succeeded")
                    planned=counts.get("planned")
                    if any(v is not None and (type(v) is not int or v<0) for v in (collected,planned)):
                        raise AnalysisRefusal("disclosure_input_invalid")
                    text += f"; collected {collected if collected is not None else 'not recorded'} of {planned if planned is not None else 'not recorded'} planned members"
                    text += "; flag counts by family: " + ", ".join(f"{f} {n}" for f,n in sorted(record.flags_by_family.items()))
                    if record.reference_source=="claim_campaign_manifests_authenticated":
                        text += "; catalog-path screen: claim_campaign_manifests_authenticated"
                    text += "; " + _trigger_text(_trigger_values(record))
                    values.update(flags_by_family=dict(record.flags_by_family),collected=collected,planned=planned,
                        catalog_path=record.reference_source=="claim_campaign_manifests_authenticated",
                        triggers=_trigger_values(record))
                result["block_lines"].append(_item("attempt_history",False,text,**values))
                if record.g10_codes or e.g10_requested:
                    cycles=(str(e.g10_redraw_cycles) if e.g10_redraw_cycles is not None else
                            "not recorded in the block's records")
                    text=f"{pack} {e.plan_id}: G10: "+(", ".join(f"{c} {n}" for c,n in sorted(record.g10_codes.items())) or "no code recorded")
                    result["block_lines"].append(_item("g10",False,text+"; redraw cycles: "+cycles,
                        pack=pack,plan_id=e.plan_id,codes=dict(record.g10_codes),redraw_cycles=e.g10_redraw_cycles))


def _source_json(archive,name):
    return _strict_json(archive.source_bytes("sources/"+name),"disclosure_input_invalid")


def _journal(archive,name):
    return [_strict_json(line,"disclosure_input_invalid") for line in archive.source_bytes("sources/"+name).splitlines() if line.strip()]


def _reading_text(values):
    return ", ".join(f"{k} " + (f"{v:.6f}" if type(v) is float else str(v)) for k,v in sorted(values.items()))


def _hazard_values(value):
    """Keep measurements, never raw bytes, locators, identity or clock stamps."""
    allowed={"current_ma","instant_amperage_ma","amperage_ma","temperature_centi_c","temperature_k",
        "os_level","pressure","thermal_pressure","thermal_level","frequency_ppm","frequency_word",
        "free_bytes","available_bytes","cpu_self_s","cpu_children_s","host_busy_cpu_s_per_s",
        "tree_cpu_s_per_s","outside_tree_cpu_s_per_s","unattributed_cpu_s_per_s","smc_min_ma",
        "smc_reads_negative","smc_reads_below","smc_reads_in_force","smc_duration_below_s",
        "registry_publications_negative","registry_min_ma","accumulator_intervals_over_limit",
        "ACAttached","IsCharging","InstantAmperage","Amperage","Voltage","Temperature",
        "freq","offset","jitter","precision","status","decision","cpu_s_per_s","worst_cpu_s_per_s"}
    out={}
    def visit(node):
        if isinstance(node,Mapping):
            for key,child in node.items():
                if key in allowed and (child is None or type(child) in (bool,int,float)
                        or isinstance(child,str) and child in ("ok","error","passed","failed","bounded","UNMEASURED")):
                    out[key]=child
                elif isinstance(child,(Mapping,list,tuple)):visit(child)
        elif isinstance(node,(list,tuple)):
            for child in node:visit(child)
    visit(value)
    return out


def _monitor_lines(result,pack,archive,kept,flags,wf):
    names=archive.source_names()
    monitor_cost=0.; reader_cost=0.; monitor_found=False; reader_found=False
    journals=[]
    for name in names:
        if "/monitor/" in name and name.endswith(".jsonl"):
            rows=_journal(archive,name); journals.extend(rows)
            if name.endswith("/monitor.jsonl"):
                # Each supervised process writes cumulative cost, with a
                # fresh session_start after a restart. Sum the final costs.
                current=0.
                for row in rows:
                    if row.get("kind")=="session_start":
                        monitor_cost+=current; current=0.
                    if row.get("kind")=="cost":
                        v=row["values"]
                        current=v["cpu_self_s"]+v["cpu_children_s"]; monitor_found=True
                monitor_cost+=current
        if "/meter/" in name and name.endswith(".jsonl"):
            for row in _journal(archive,name):
                if row.get("k")=="t":
                    if _finite(row.get("utime_s")) and _finite(row.get("stime_s")):
                        reader_cost+=row["utime_s"]+row["stime_s"]; reader_found=True
    target_spans=[]; request_spans=[]; anchors=[]; clock_pairs={}
    all_runs={run for c in kept.cells.values() for units in c.kept.values() for u in units for run in u.run_ids}
    for name in names:
        if name.endswith("/metadata.json") and name.split("/")[-2] in all_runs:
            meta=_source_json(archive,name)
            anchor=(meta.get("uncertainty_evidence") or {}).get("clock_anchor") or {}
            anchors.append(anchor)
            stamps=anchor.get("clock_stamps") or {}
            first=(stamps.get("sampling_started") or {}).get("monotonic_before_s")
            last=(stamps.get("sampling_stopped") or {}).get("monotonic_after_s")
            epoch=(stamps.get("sampling_started") or {}).get("epoch_s")
            if _finite(first) and _finite(epoch):clock_pairs[name.split("/")[-2]]=(first,epoch)
            if _finite(first) and _finite(last):request_spans.append((first*1e9,last*1e9))
    for name in names:
        if name.endswith("/events.jsonl") and name.split("/")[-2] in all_runs:
            starts={}
            for row in _journal(archive,name):
                phase=row.get("phase"); meta=row.get("metadata") or {}; stamp=meta.get("monotonic_ns")
                if type(stamp) is not int and name.split("/")[-2] in clock_pairs and _finite(row.get("timestamp_s")):
                    mono,epoch=clock_pairs[name.split("/")[-2]]
                    stamp=math.floor((mono+row["timestamp_s"]-epoch)*1e9)
                if phase not in ("decode","prefill") or type(stamp) is not int:continue
                if row.get("event_type")=="phase_start":starts[phase]=stamp
                if row.get("event_type")=="phase_end" and phase in starts:target_spans.append((starts[phase],stamp))
    probes=0; host_busy=0.; host_found=False
    for row in journals:
        if row.get("kind") not in ("reading","interval"):continue
        lo=(row.get("started") or {}).get("monotonic_ns")
        hi=(row.get("finished") or {}).get("monotonic_ns")
        if type(lo) is not int or type(hi) is not int:continue
        if any(lo<b and hi>=a for a,b in target_spans):probes+=1
        busy=(row.get("values") or {}).get("host_busy_cpu_s_per_s")
        if row.get("module")=="contention" and _finite(busy):
            overlap=math.fsum(max(0,min(hi,b)-max(lo,a)) for a,b in request_spans)/1e9
            host_busy+=busy*overlap; host_found=True
    text=(f"{pack}: monitor cost: hazard CPU {monitor_cost:.6f} s" if monitor_found else
          f"{pack}: monitor cost: hazard CPU not recorded")
    text+=f"; probes inside target phases {probes}; meter reader CPU "+(f"{reader_cost:.6f} s" if reader_found else "not recorded")
    result["window_lines"][pack].append(_item("monitor_cost",False,text,
        cpu_s=monitor_cost if monitor_found else None,reader_cpu_s=reader_cost if reader_found else None,
        probes_inside_target_phases=probes))
    result["window_lines"][pack].append(_item("monitor_sentence",False,MONITOR_SENTENCE))
    for module,entries in sorted(wf.get("hazards",{}).items()):
        for entry in entries.get("arm",[]):
            values=_hazard_values(entry.get("measurement"))
            result["window_lines"][pack].append(_item("arm_hazards",False,
                f"{pack}: {module} at arm ({entry.get('phase')}): {entry.get('verdict')}; "+_reading_text(values),
                module=module,phase=entry.get("phase"),verdict=entry.get("verdict"),measurements=values))
    counts=Counter(r["code"] for r in flags if r.get("family")=="PHYSICS_IN_SPAN")
    restricted_physics=any(r.get("family")=="PHYSICS_IN_SPAN" and r["blinding"]=="RESTRICTED" for r in flags)
    result["window_lines"][pack].append(_item("physics_counts",restricted_physics,
        f"{pack}: physics-in-span counts: "+", ".join(f"{c} {n}" for c,n in sorted(counts.items())),counts=dict(counts)))
    bounded=sum(a.get("status")=="bounded" for a in anchors)
    bounds=[a["effective_clock_anchor_bound_s"] for a in anchors if _finite(a.get("effective_clock_anchor_bound_s"))]
    result["window_lines"][pack].append(_item("anchor_counts",False,f"{pack}: members with anchor status bounded: {bounded}",count=bounded))
    result["window_lines"][pack].append(_item("anchor_bound",True,
        f"{pack}: largest effective anchor bound: "+(f"{max(bounds):.6f} s" if bounds else "not recorded"),
        value_s=max(bounds) if bounds else None))
    result["window_lines"][pack].append(_item("host_cpu",False,
        f"{pack}: host's total busy CPU during requests: "+(f"{host_busy:.6f} s" if host_found else "not recorded"),
        value_s=host_busy if host_found else None))
    counts=Counter(r["code"] for r in flags)
    battery_codes=("battery.assist","battery.assist_outside_request","calibration.capture_battery_assist",
                   "battery.smc_unavailable","battery.capture_pair_assist","calibration.capture_battery_pair_assist")
    subjects={c:{r["scope"].get("run_id") or (r.get("observed") or {}).get("capture") or
                 (r.get("observed") or {}).get("attempt") or r.get("flag_id") or i
                 for i,r in enumerate(flags) if r["code"]==c} for c in battery_codes}
    member_counts={c:len(subjects[c]) for c in battery_codes}
    result["window_lines"][pack].append(_item("battery_counts",False,
        f"{pack}: battery observations: "+", ".join(f"{c} {member_counts[c]}" for c in battery_codes),
        counts=member_counts))
    for flag in flags:
        if flag["code"] not in ("battery.assist","battery.assist_outside_request","calibration.capture_battery_assist"):continue
        observed=flag.get("observed") or {}
        for phase,values in sorted(observed.get("phases",{}).items()):
            readings=_hazard_values(values)
            result["window_lines"][pack].append(_item("battery_phase",False,
                f"{pack} {flag['scope'].get('run_id') or 'calibration'} {phase}: "+_reading_text(readings),
                phase=phase,measurements=readings))
    if any(counts[c] for c in battery_codes[:3]):
        battery=_strict_json(archive.withheld_bytes("withheld/battery-assist.json"),"disclosure_input_invalid")
        for group in ("members","captures"):
            for identity,row in sorted(battery.get(group,{}).items()):
                for phase,values in sorted(row.get("phases",{}).items()):
                    joules=values["discharged_energy_j"]
                    result["window_lines"][pack].append(_item("battery_discharged",True,
                        f"{pack} {identity} {phase}: discharged energy {joules:.5f} J",value_j=joules))


def _reference_lines(result,pack,archive,record,flags):
    screen=_strict_json(archive.output_bytes("derived/neg8-screen.json"),"disclosure_input_invalid")
    bound=_strict_json(archive.output_bytes("derived/neg8-bound.json"),"disclosure_input_invalid")
    physics=_strict_json(archive.output_bytes("derived/neg8-corpus-physics.json"),"disclosure_input_invalid")
    rescreen=screen["rescreen"]; survivors=rescreen["survivors"]
    decision=rescreen["decision"]
    result["window_lines"][pack].append(_item("neg8_screen",True,
        f"{pack}: NEG-8 screen {decision}; the bound was validated against the collected members; "
        "the harvest's re-screen against the clean bound, not the stored verdict, decided the screen.",decision=decision))
    row=archived_verdict_row(archive)
    roster=rebuilt_roster(archive,row)
    refs={m["run_id"]:m.get("neg8_slot") or m.get("spare_slot") for m in roster["members"]
          if m.get("neg8_slot") or m.get("spare_slot")}
    lost={item["bundle_id"]:{"slot":item.get("slot") or refs.get(item["bundle_id"]),
                           "reason":item.get("reason")} for item in survivors.get("reference_losses",[])}
    for run,reason in screen.get("harvest_reference_losses",{}).items():
        lost.setdefault(run,{"slot":refs.get(run),"reason":reason})
    for excluded in row.get("excluded_bundles",[]):
        run=excluded["bundle_id"]
        if run in refs and run not in lost:lost[run]={"slot":refs[run],"reason":"writer_excluded"}
    # The engine preserves historical full-roster bytes: absent counts mean
    # (3, 1, 3), exactly as context.survivor_set reads that shape.
    reference_counts=survivors.get("reference_counts",{"start":3,"midpoint":1,"end":3})
    planned={"start":3,"midpoint":1,"end":3}
    result["window_lines"][pack].append(_item("reference_counts",False,
        f"{pack}: realised references (start, midpoint, end): "+
        ", ".join(str(reference_counts[k]) for k in planned)+" against planned (3, 1, 3)",
        counts=reference_counts,planned=planned))
    for run,values in sorted(lost.items()):
        reason_spec=_catalog().codes.get(values["reason"])
        result["window_lines"][pack].append(_item("reference_lost",bool(reason_spec and reason_spec["blinding"]=="RESTRICTED"),
            f"{pack}: lost reference {run}; slot {values['slot']}; reason {values['reason']}",run_id=run,**values))
    for member in roster["members"]:
        if not member.get("spare_slot"):continue
        run=member["run_id"]
        retried=[r for r in flags if r["code"]=="member.retried" and r["scope"].get("run_id")==run]
        if not retried:continue
        succeeded=(retried[0].get("observed") or {}).get("status")=="succeeded"
        result["window_lines"][pack].append(_item("reference_spare",False,
            f"{pack}: spare {run}; slot {member['spare_slot']}; succeeded {'yes' if succeeded else 'no'}",
            run_id=run,slot=member["spare_slot"],succeeded=succeeded))
    if survivors.get("midpoint_lost") or any(v["slot"]=="midpoint" for v in lost.values()):
        result["window_lines"][pack].append(_item("lost_midpoint",False,MIDPOINT_SENTENCE))
    dropped_counts=Counter()
    mint_drops=set()
    for flag in flags:
        if flag["code"]=="neg8.corpus_member_dropped":
            observed=flag.get("observed") or {}
            mint_drops.add(flag["scope"].get("run_id"))
            for reason in observed.get("reasons") or [observed.get("reason")]:
                if reason:dropped_counts[reason]+=1
    dropped_counts["status"]=len(set(bound.get("dropped_bundle_ids") or [])-mint_drops)
    cap=physics.get("beyond_cap") or []; dropped_counts["desk_cap"]=len(cap)
    corpus={"collected":bound.get("members_committed"),"in_window":physics.get("members_bound"),
            "deciding":physics.get("members_kept"),"desk_cap":cap,"drop_counts":dict(dropped_counts)}
    result["window_lines"][pack].append(_item("corpus_counts",False,
        f"{pack}: corpus collected {corpus['collected']}; in-window bound {corpus['in_window']}; "
        f"deciding clean corpus {corpus['deciding']}; desk cap left out: "+(", ".join(cap) or "none")+
        "; dropped by reason: "+", ".join(f"{r} {n}" for r,n in sorted(dropped_counts.items())),**corpus))
    for member in physics.get("dropped",[]):
        result["window_lines"][pack].append(_item("corpus_physics_drop",False,
            f"{pack}: corpus member {member['bundle_id']} dropped for physics: "+", ".join(member["reasons"]),
            run_id=member["bundle_id"],codes=member["reasons"]))
    result["window_lines"][pack].append(_item("bound_formula",False,
        f"{pack}: bound formula at realised counts: {screen['bound_formula']}",formula=screen["bound_formula"]))
    allowance=_strict_json(archive.output_bytes("derived/neg8-allowance.json"),"disclosure_input_invalid")
    bracket=(_strict_json(archive.withheld_bytes("withheld/neg8-rescreen-bracket.json"),"disclosure_input_invalid")
             if allowance["source"]=="survivor_rescreen" else row["idle_admission_core"]["neg8_bracket"])
    # Extract the registered energetic fields without copying provenance paths.
    numeric={}
    def collect(node,prefix=""):
        if isinstance(node,Mapping):
            for key,value in node.items():
                if key.endswith("_j") and _finite(value):numeric[prefix+key]=value
                elif isinstance(value,Mapping):collect(value,prefix+key+".")
    collect(bracket)
    result["window_lines"][pack].append(_item("neg8_allowance",True,
        f"{pack}: NEG-8 allowance source {allowance['source']}; "+
        ", ".join(f"{key} {value:.5f} J" for key,value in sorted(numeric.items())),
        source=allowance["source"],values_j=numeric))
    if record.reference_source=="claim_campaign_manifests_authenticated":
        result["window_lines"][pack].append(_item("catalog_path",False,
            f"{pack}: catalog-path screen: claim_campaign_manifests_authenticated"))
    return decision,roster


def _temperature_lines(result,pack,archive,flags,decision,roster):
    for name in archive.source_names():
        if "/campaign_manifests/" not in name or not name.endswith(".json"):continue
        manifest=_source_json(archive,name)
        if not isinstance(manifest.get("members"),list):continue
        config_dir=Path(str(manifest.get("config_dir") or "")).name
        runs={r.get("run_id") for r in manifest["members"] if isinstance(r,Mapping)}
        stages={r.get("stage_id") for r in roster["members"] if r["run_id"] in runs and r.get("stage_id")}
        stage=manifest.get("stage_id") or (next(iter(stages)) if len(stages)==1 else config_dir or Path(name).stem)
        valid=[r.get("temperature_centi_c") for r in manifest.get("battery_temperature_readings",[])
               if isinstance(r,Mapping) and type(r.get("temperature_centi_c")) is int]
        rise=(valid[-1]-valid[0])/100 if len(valid)>=2 else None
        plateau=len(valid)>=3 and (max(valid[-3:])-min(valid[-3:]))/100<=.5
        def stage_flag(code):
            return any(r["code"]==code and (
                r["scope"].get("stage_id")==stage or (r.get("observed") or {}).get("config_dir") in (stage,config_dir) or
                (r.get("observed") or {}).get("manifest")==Path(name).name) for r in flags)
        flagged=stage_flag("thermal.stage_battery_rise")
        unmeasured=stage_flag("thermal.battery_temperature_unmeasured")
        own_flag=rise is not None and rise>3 and not plateau
        values={"stage_id":stage,"readings_centi_c":valid,"rise_k":rise,"plateau":plateau,
                "harvest_flag":flagged,"producer_flag":own_flag,"temperature_unmeasured":unmeasured,
                "differs_from_harvest_flag":flagged!=own_flag}
        text=(f"{pack} stage {stage}: battery temperature readings: "+", ".join(f"{v/100:.2f} C" for v in valid)+
              f"; rise {rise:.2f} K" if rise is not None else
              f"{pack} stage {stage}: battery temperature readings: "+(", ".join(f"{v/100:.2f} C" for v in valid) if valid else "battery temperature not recorded for this stage"))
        text+=f"; plateau {'yes' if plateau else 'no'}; harvest flag {'yes' if flagged else 'no'}; producer flag {'yes' if own_flag else 'no'}"
        if unmeasured:text+="; thermal.battery_temperature_unmeasured"
        result["window_lines"][pack].append(_item("battery_temperature",False,text,**values))
        if flagged!=own_flag:
            result["window_lines"][pack].append(_item("temperature_disagreement",False,
                f"{pack} stage {stage}: producer rise rule differs from harvest flag",stage_id=stage))
        if flagged and rise is not None:
            text=TEMPERATURE_SENTENCE.replace("Stage S",f"Stage {stage}").replace("X",f"{rise:.2f}").replace("[passed/failed]",decision)
            # Its hazard measurements are structure, but the NEG-8 word is
            # selected by a science-energy screen, so this sentence is withheld.
            result["window_lines"][pack].append(_item("battery_temperature_sentence",True,text,stage_id=stage,rise_k=rise,neg8=decision))


def _structure_lines(result,index,records,windows,archives,kept,brackets,projections,reports,catalog,flags):
    _kept_lines(result,kept,projections,reports,catalog,flags,archives)
    _history_lines(result,index,records)
    result["fixed_sentences"].append(_item("conditionality",False,CONDITIONALITY))
    for key,text in FIXED_SENTENCES.items():result["fixed_sentences"].append(_item(key,False,text))
    for pack in PACK_ORDER:
        archive=archives[pack]; record=windows[pack].record
        counts = Counter(r["code"] for r in flags[pack])
        restricted_codes = {code for code, spec in catalog.codes.items() if spec["blinding"] == "RESTRICTED"}
        for code in sorted(counts.keys() | restricted_codes):
            count = counts[code]
            metadata = (_code(code,catalog,flags[pack]) if count else
                        {"code":code,"blinding":catalog.codes[code]["blinding"]})
            result["window_lines"][pack].append(_item("flag_count",metadata["blinding"]=="RESTRICTED",
                f"{pack}: flag {code}: {count}; family {catalog.codes[code]['family']}",
                count=count,family=catalog.codes[code]["family"],**metadata))
        modules=sorted({r["code"].split(".")[0] for r in flags[pack] if r["code"].endswith(".arm_unmeasured")})
        if modules:
            result["window_lines"][pack].append(_item("arm_unmeasured",False,
                ARM_SENTENCE.replace("[clock, battery, thermal, contention, disk]",", ".join(modules)),modules=modules))
        wf=_strict_json(archive.output_bytes("derived/window_flags.json"),"disclosure_input_invalid")
        _monitor_lines(result,pack,archive,kept[pack],flags[pack],wf)
        decision,roster=_reference_lines(result,pack,archive,record,flags[pack])
        _temperature_lines(result,pack,archive,flags[pack],decision,roster)
        values=_trigger_values(record)
        text=(_trigger_text(values) if values is not None else
            "sealed rule: the bracket read fresh, so no trigger was observed; doubling count and sequences not recorded by this harvest's program")
        result["window_lines"][pack].append(_item("erratum3_triggers",False,f"{pack}: "+text,values=values))
        below = brackets[pack].b_fiducial_s < SCREEN_BOUND_S
        result["window_lines"][pack].append(_item("below_screen_bound",True,
            f"{pack}: operative bound below 36.46 ms: {'yes' if below else 'no'} ({brackets[pack].b_fiducial_s:.6f} s)",
            b_op_s=brackets[pack].b_fiducial_s, below=below))


def _required(value,key,path=""):
    if not isinstance(value,Mapping) or key not in value:
        raise AnalysisRefusal("disclosure_input_missing:"+path+key)
    return value[key]


def _step_word(value):
    if value not in ("passed","failed","not_run","not_applicable","clear","triggered","not_triggered","pending"):
        raise AnalysisRefusal("disclosure_input_invalid")
    return value


# The writer's own adapter wattage continuity decisions
# (idle_admission.adapter_wattage_continuity), which the driver copies.
_CONTINUITY_WORDS = ("stable", "flagged", "failed", "not_applicable")


def _continuity_word(value):
    if value not in _CONTINUITY_WORDS:
        raise AnalysisRefusal("disclosure_input_invalid")
    return value


def _step_count(value):
    if type(value) is not int or value<0:raise AnalysisRefusal("disclosure_input_invalid")
    return value


def _logical_word(value):
    if not isinstance(value,str) or not value or any(c in value for c in ("/","\\","\x00","\n")):
        raise AnalysisRefusal("disclosure_input_invalid")
    return value


def _closeout_lines(result,closeout,artifact):
    floors={r["cell_id"]:r for r in artifact["cells"] if "cell_id" in r}
    for group in ("independent_ratios","comparative_common_mode_ratios"):
        for row in closeout.get(group,[]):
            cid=row["cell_id"];component=row["component"]
            floor=floors[cid][component]
            n=floor["n"] if component=="absolute" else floor["n_blocks"]
            values={"cell_id":cid,"component":component,"n":n,"status":row["status"]}
            label="R" if group=="independent_ratios" else "R_cm"
            if row["status"]=="complete":
                denominator=row["point_unguarded_floor_j"]
                numerator=row["corner_widened_unguarded_floor_j" if label=="R" else "common_mode_corner_widened_unguarded_floor_j"]
                ratio=row["ratio"]
                text=(f"{cid} {component}: {label} {ratio:.4f}; numerator {numerator:.5f} J; "
                      f"denominator {denominator:.5f} J; n = {n}; point diagnostic; no interval")
                values.update(ratio=ratio,numerator_j=numerator,denominator_j=denominator)
            else:
                text=f"{cid} {component}: {label} {row['status']}; point diagnostic; no interval"
            result["block_lines"].append(_item("dominance_ratio",True,text,**values))
    if "branch" in closeout:
        result["block_lines"].append(_item("dominance_branch",True,
            f"D-165 branch {closeout['branch']}; dominance sentence licensed: "+
            ("yes" if closeout["dominance_sentence_licensed"] else "no"),branch=closeout["branch"],
            dominance_sentence_licensed=closeout["dominance_sentence_licensed"]))


def _ruling_lines(result,windows,brackets,sensitivity,steps,catalog,flags):
    rows=_required(steps,"windows")
    for pack in PACK_ORDER:
        row=_required(rows,pack,"windows.")
        path=f"windows.{pack}."
        stored=_required(row,"stored_verdict",path)
        status=_step_word(_required(stored,"status",path+"stored_verdict."))
        result["window_lines"][pack].append(_item("stored_status",False,
            f"{pack}: stored verdict status: {status}",status=status))
        conditions=_required(stored,"conditions",path+"stored_verdict.")
        for condition in conditions:
            name=_logical_word(_required(condition,"condition",path+"stored_verdict.conditions."))
            answer=_logical_word(_required(condition,"answered_by",path+"stored_verdict.conditions."))
            result["window_lines"][pack].append(_item("stored_condition",name.startswith("neg8_"),
                f"{pack}: stored condition {name}; answered by {answer}",condition=name,answered_by=answer))
        for reason in _required(row,"member_reasons",path):
            values={key:_required(reason,key,path+"member_reasons.") for key in
                    ("reason","count","all_removed","families","codes")}
            _logical_word(values["reason"]);_step_count(values["count"])
            if type(values["all_removed"]) is not bool:raise AnalysisRefusal("disclosure_input_invalid")
            codes=[_code(c,catalog,flags[pack]) for c in values.pop("codes")]
            result["window_lines"][pack].append({"line":"stored_member_reason","restricted":False,
                "label":"stored member reason","pack":pack,"codes":codes,**_plain(values)})
        continuity=_continuity_word(_required(row,"adapter_continuity",path))
        result["window_lines"][pack].append(_item("adapter_continuity",False,
            f"{pack}: adapter-continuity decision: {continuity}",decision=continuity))
        result["window_lines"][pack].append(_item("stored_verdict_boundary",False,
            "The stored verdict's status and NEG-8 bracket decided nothing; its membership, basis, provenance "
            "and physics checks were applied."))
        tripwires=_required(row,"tripwires",path)
        for key in ("excluded_reference_in_screen","kept_member_outside_verdict_membership"):
            word=_step_word(_required(tripwires,key,path+"tripwires."))
            result["window_lines"][pack].append(_item("tripwire",False,
                f"{pack}: tripwire {key}: {word}",tripwire=key,result=word))
        counts={key:_step_count(_required(row,key,path)) for key in ("deciding_references","deciding_spares","writer_excluded_count")}
        families=_required(row,"writer_excluded_by_family",path)
        removed=_required(row,"writer_excluded_all_removed",path)
        if type(removed) is not bool:raise AnalysisRefusal("disclosure_input_invalid")
        for family,count in families.items():_logical_word(family);_step_count(count)
        result["window_lines"][pack].append(_item("deciding_membership",False,
            f"{pack}: deciding screen used {counts['deciding_references']} references and "
            f"{counts['deciding_spares']} spares; writer left out {counts['writer_excluded_count']} members; "
            f"every one removed: {'yes' if removed else 'no'}; removing families: "+
            ", ".join(f"{family} {count}" for family,count in sorted(families.items())),
            writer_excluded_by_family=families,writer_excluded_all_removed=removed,**counts))
        parity=_step_word(_required(row,"reference_parity",path))
        result["window_lines"][pack].append(_item("reference_parity",False,
            f"{pack}: reference parity: {parity}; deciding archive pin {windows[pack].harvest_pin}",
            result=parity,harvest_pin=windows[pack].harvest_pin))
        prefix=_step_word(_required(row,"ledger_prefix_test",path))
        bracket=brackets[pack]
        result["window_lines"][pack].append(_item("ledger_binding",False,
            f"{pack}: SHA256SUMS digest {bracket.sources_sha256sums_sha256}; ledger copy digest "
            f"{bracket.ledger_copy_sha256}; terminal sequence {bracket.terminal_sequence}; prefix test {prefix}",
            sha256sums_sha256=bracket.sources_sha256sums_sha256,ledger_copy_sha256=bracket.ledger_copy_sha256,
            terminal_sequence=bracket.terminal_sequence,prefix_result=prefix))
    twice=_required(steps,"no_analysed_window_harvested_twice")
    if type(twice) is not bool:raise AnalysisRefusal("disclosure_input_invalid")
    result["block_lines"].append(_item("harvest_once",False,
        "no analysed window was harvested twice" if twice is True else "analysed-window harvest parity requires review",
        no_analysed_window_harvested_twice=twice))
    if not twice:
        accounts=_required(steps,"reharvests")
        if not isinstance(accounts,list) or not accounts:raise AnalysisRefusal("disclosure_input_invalid")
        for row in accounts:
            fields={key:_required(row,key,"reharvests.") for key in
                    ("pack","original_pin","deciding_pin","original_harvest_sha256","deciding_harvest_sha256",
                     "reason","survivors_before","survivors_after")}
            for key in ("pack","original_pin","deciding_pin","reason"):_logical_word(fields[key])
            for key in ("survivors_before","survivors_after"):_step_count(fields[key])
            result["block_lines"].append(_item("reharvest_account",False,
                f"{fields['pack']}: re-harvest from pin {fields['original_pin']} to pin {fields['deciding_pin']}; "
                f"original archive digest {fields['original_harvest_sha256']}; deciding archive digest {fields['deciding_harvest_sha256']}; "
                f"reason {fields['reason']}; survivors {fields['survivors_before']} to {fields['survivors_after']}",**fields))
    result["fixed_sentences"].append(_item("config_binding",False,
        "The writer applied no config binding and the pinned harvest's loss list lacked the code; the analysis "
        "checked by structure that no reference the screen used carried it."))
    bmax=sensitivity["b_max"]
    attainment = (f"attained at ledger sequence {bmax['attained_by_sequence']}" if bmax["attained_by_sequence"] is not None else
                  "attained by a member of the acceptance (no ledger sequence)")
    result["block_lines"].append(_item("sensitivity_bmax",True,
        f"sensitivity: B_max {bmax['value_s']:.6f} s {attainment}; T = {bmax['T']}",**bmax))
    for pack in PACK_ORDER:
        row=sensitivity["windows"][pack]
        phrase="values differ from primary" if row["widened"] else "sensitivity values equal primary values"
        result["block_lines"].append(_item("sensitivity_window",True,
            f"sensitivity: {pack} {row['plan_id']}: b_op {row['b_op_s']:.6f} s; b_sens {row['b_sens_s']:.6f} s; {phrase}",pack=pack,**row))
    for name,line in (("reported_cells","sensitivity_reported"),("floor_cells","sensitivity_floor"),("contrasts","sensitivity_contrast")):
        for row in sensitivity[name]:
            identity=row["contrast_id"] if name=="contrasts" else row["pack"]+" "+row["cell_id"]
            text=f"sensitivity: {identity}"
            if row.get("status")=="refused":
                text+=f": refused ({row['code']})"
            else:
                for side in ("primary","sensitivity"):
                    text+=f"; {side}: "+", ".join(
                        f"{key} "+(value if isinstance(value,str) else f"{value:.5f} J")
                        for key,value in sorted(row[side].items()))
                if name=="contrasts":
                    text+="; sensitivity outcome equals primary: "+("yes" if row["outcome_equals_primary"] else "no")
                text+="; not below primary: "+("yes" if row["not_below_primary"] else "no")
            result["block_lines"].append(_item(line,True,text,record=row))
    result["block_lines"].append(_item("sensitivity_boundary",True,
        "Sensitivity values are never composed into a primary number."))


def _input_refusals(function):
    @wraps(function)
    def checked(*args,**kwargs):
        try:return function(*args,**kwargs)
        except (AnalysisRefusal,PaperReportedEnergyRefusal):raise
        except (KeyError,TypeError,AttributeError,ValueError,OverflowError):
            raise AnalysisRefusal("disclosure_input_invalid") from None
    return checked


@_input_refusals
def produce_disclosures(index, windows, archives, kept_units, brackets, projections,
                        extraction_reports, floor_artifact, closeout, claim_verdicts,
                        contrast_observations, sensitivity, *, records, cell_estimates,
                        step_results) -> dict:
    _validate_sensitivity(sensitivity)
    if len(records) != len(index.entries) or any(r.entry != e for r, e in zip(records, index.entries)):
        raise AnalysisRefusal("disclosure_input_missing:records")
    catalog = _catalog()
    flags = {pack: _flags(archives[pack], catalog) for pack in PACK_ORDER}
    for pack in PACK_ORDER[:2]:
        projection=projections[pack]
        if projection.get("mode")=="production":
            expected={key:getattr(windows[pack],key) for key in ("pack","plan_id","attempt","harvest_pin")}
            if projection.get("window")!=expected or projection.get("exclusions_sha256")!=kept_units[pack].exclusions_sha256:
                raise AnalysisRefusal("disclosure_input_invalid")
    result = {"schema_version": SCHEMA,
              "windows": {pack: {"plan_id": windows[pack].plan_id, "attempt": windows[pack].attempt,
                         "harvest_pin": windows[pack].harvest_pin,
                         "record_shape": windows[pack].record.record_shape} for pack in PACK_ORDER},
              "cells": [], "floors": [], "contrasts": [],
              "window_lines": {pack: [] for pack in PACK_ORDER}, "block_lines": [],
              "sensitivity": _plain(sensitivity), "fixed_sentences": []}
    _energy_lines(result, windows, archives, kept_units, projections, extraction_reports,
                  floor_artifact, claim_verdicts, contrast_observations, cell_estimates, flags)
    _structure_lines(result,index,records,windows,archives,kept_units,brackets,projections,
                     extraction_reports,catalog,flags)
    _ruling_lines(result,windows,brackets,sensitivity,step_results,catalog,flags)
    _closeout_lines(result,closeout,floor_artifact)
    canonical_json_bytes(result)
    return result


def _render_item(item, released):
    if item["restricted"] and not released:
        return item["label"] + ": withheld until the release event"
    if item["line"] == "removed_unit":
        restricted_code = any(c["blinding"] == "RESTRICTED" for c in item["codes"])
        word = "removed (restricted code)" if restricted_code and not released else "removed"
        codes = [c["code"] for c in item["codes"] if released or c["blinding"] == "STRUCTURE"]
        return (f"{item['unit_id']}: {word}; families: {', '.join(item['families'])}; "
                f"codes: {', '.join(codes)}; stage and ordinal: " + ", ".join(
                    f"{stage or 'unrecorded'} {position}" for stage, position in zip(
                        item["stage_ids"], item["positions"])))
    if item["line"] == "stored_member_reason":
        codes=[c["code"] if released or c["blinding"]=="STRUCTURE" else "restricted code" for c in item["codes"]]
        return (f"{item['pack']}: stored member reason {item['reason']}: {item['count']} members; "
                f"every one removed: {'yes' if item['all_removed'] else 'no'}; "
                f"families: {', '.join(item['families'])}; codes: {', '.join(codes)}")
    return item["text"]


def render_disclosures(record, *, released: bool) -> str:
    """Render a copy-free view; the custody record is independent of release."""
    lines = []
    for name in ("cells", "floors", "contrasts"):
        lines.extend(_render_item(item, released) for item in record[name])
    for pack in PACK_ORDER:
        lines.extend(_render_item(item, released) for item in record["window_lines"][pack])
    for name in ("block_lines", "fixed_sentences"):
        lines.extend(_render_item(item, released) for item in record[name])
    return "\n".join(lines) + "\n"
