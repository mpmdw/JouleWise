"""Step 3's statistic (iii) on the development legs, by the committed step 3 code (RL-151 §1.3 item 2; RL-166 Q6).

The adapter re-implements nothing. For each prompt-size cell it:
1. loads ``joulewise/cadence_looks/step3_energy_ratios.py`` afresh, refusing any sha256 other than
   ``84a1a553...eb173``;
2. rebinds the module's ``LEGS`` and ``ORIGINAL_EIGHT`` to the cell's roster;
3. calls the module's own ``analyse`` and ``custody_check``.

It contains no arithmetic on energy. It only selects fields from the module's output and takes the
largest drift fraction over cells for the tripwire.

* **One call per prompt-size cell.** The block fixed effect means something only at one prompt size; step
  3's legs were all 10k. The 10k cell prints first, as the like-for-like value.
* **Roster.** Stage 1's included development legs of type A (role ``fit``). Each leg is the tuple
  ``(key, day, key, "Automatic", bundle)``, step 3's ``(leg_id, night, leg, class, bundle)``. Every
  development leg is Automatic. ``ORIGINAL_EIGHT`` is the whole cell, so step 3's two drift variants read the
  same legs.
* **A leg on which ``analyse_leg`` raises** is named with the exception's type (never its message, which
  could carry a value), left out of that cell and counted. The cell is then run again on the remaining legs
  with a fresh module. The leg is found by walking the traceback to the module's own ``analyse_leg`` frame
  and reading its ``leg`` argument.
* **More than two such legs in a cell:** the cell prints ``not_run`` and comes to the research lead.
* **An exception outside ``analyse_leg``** (in the cell-level arithmetic or in ``custody_check``) also
  prints ``not_run``, with ``key`` "(cell)".
* **Kept from each call:** (ii) gamma without its per-leg leave-one-out values; gamma's estimability; (iii)
  as one number in each form; (iv)'s median, minimum and maximum; (vi) without its per-leg values.
  Per-leg lists and (v) are dropped.
* **Tripwire.** The largest ``drift_fraction_linear`` over cells whose gamma is estimable, against 0.08.
  The threshold is 0.04 if the cold seat's RL-166 Q11 check fails; the caller passes it.

This runs in stage 2: the module opens energy files, and only through its own loaders.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import uuid

STEP3_PATH = Path(__file__).resolve().with_name("step3_energy_ratios.py")
STEP3_SHA256 = "84a1a5530ab06e688b000c84f248b2c4e561e8330f37d3132ec47aa2572eb173"
LIKE_FOR_LIKE_CELL = 10000
DRIFT_THRESHOLD = 0.08
DRIFT_FALLBACK = 0.04
MAX_FAILED_LEGS = 2


class Step3Refused(RuntimeError):
    pass


def load_step3(path=STEP3_PATH, sha256=STEP3_SHA256):
    """A fresh module object from the committed bytes; refuses a file whose sha256 is not the pin."""
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha256:
        raise Step3Refused(f"{path}: sha256 is not the pinned step 3 code (RL-166 Q6: any edit needs a ruling)")
    spec = importlib.util.spec_from_file_location(f"_step3_{uuid.uuid4().hex}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _failing_leg(exc, module):
    """The leg key whose ``analyse_leg`` frame raised, or None if the exception came from elsewhere."""
    tb = exc.__traceback__
    found = None
    while tb is not None:
        frame = tb.tb_frame
        if frame.f_code.co_name == "analyse_leg" and frame.f_globals is module.__dict__:
            leg = frame.f_locals.get("leg")
            if isinstance(leg, tuple) and leg:
                found = leg[0]
        tb = tb.tb_next
    return found


def _strip_per_leg(d, leg_keys):
    if not isinstance(d, dict):
        return d
    return {k: v for k, v in d.items() if k not in leg_keys and k not in ("leave_one_leg_out",
                                                                           "all_blocks_leave_one_leg_out")}


def _one(values):
    vals = [v for v in (values or {}).values() if isinstance(v, (int, float))]
    return max(vals) if vals else None


def _project(out, keys_in_cell):
    iii = out.get("iii_precut_drift") or {}
    iv = out.get("iv_jpt_after_over_before") or {}
    return {
        "ii_gamma": _strip_per_leg(out.get("ii_gamma_per_degC"), keys_in_cell),
        "gamma_estimable": (out.get("gamma_estimability") or {}).get("estimable"),
        # with ORIGINAL_EIGHT = the whole cell, step 3's two variants read the same legs; take the larger
        "iii_drift_fraction_linear": _one(iii.get("drift_fraction_linear")),
        "iii_drift_fraction_exp_form": _one(iii.get("drift_fraction_exp_form")),
        "iv_after_over_before": {"median": iv.get("automatic_median"), "min": iv.get("automatic_min"),
                                 "max": iv.get("automatic_max")},
        "vi_slope_lnE_on_lnclock": _strip_per_leg(out.get("vi_slope_lnE_on_lnclock"), keys_in_cell),
    }


def run_cell(prompt_tokens, legs, loader=load_step3):
    """One cell. ``legs`` = [{"key", "day", "bundle"}]. Returns the output schema's ``step3_cell``."""
    tuples = [(leg["key"], leg["day"], leg["key"], "Automatic", leg["bundle"]) for leg in legs]
    failed = []
    cell = {"prompt_tokens": prompt_tokens, "status": "not_run", "n_legs": 0, "failed_legs": failed,
            "ii_gamma": None, "gamma_estimable": None, "iii_drift_fraction_linear": None,
            "iii_drift_fraction_exp_form": None, "iv_after_over_before": None, "vi_slope_lnE_on_lnclock": None}
    while tuples:
        module = loader()
        module.LEGS = list(tuples)
        module.ORIGINAL_EIGHT = [t[0] for t in tuples]
        try:
            out = module.analyse({t[0]: t[4] for t in tuples})
            module.custody_check(out)
        except Exception as exc:                  # never the message: it could carry a value
            key = _failing_leg(exc, module)
            failed.append({"key": key or "(cell)", "exception_type": type(exc).__name__})
            if key is None or len(failed) > MAX_FAILED_LEGS:
                return cell
            tuples = [t for t in tuples if t[0] != key]
            continue
        cell.update(status="ok", n_legs=len(tuples), **_project(out, {t[0] for t in tuples}))
        return cell
    return cell


def _cell_order(sizes):
    return sorted(sizes, key=lambda s: (s != LIKE_FOR_LIKE_CELL, s))


def run_roster(entries, *, threshold=DRIFT_THRESHOLD, loader=load_step3):
    """All cells and the tripwire. ``entries`` = stage 1's legs: {"key", "day", "bundle", "role", "leg_type",
    "included", "prompt_tokens_nominal"}. Only included type-A fit legs enter. Returns the output schema's
    ``step3`` object."""
    if threshold not in (DRIFT_THRESHOLD, DRIFT_FALLBACK):
        raise Step3Refused(f"threshold {threshold}: RL-166 Q11 allows {DRIFT_THRESHOLD} or {DRIFT_FALLBACK}")
    cells = {}
    for e in entries:
        if e.get("included") is True and e.get("role") == "fit" and e.get("leg_type") == "A":
            cells.setdefault(e["prompt_tokens_nominal"], []).append(
                {"key": e["key"], "day": e["day"], "bundle": e["bundle"]})
    results = [run_cell(size, cells[size], loader) for size in _cell_order(cells)]
    eligible = [c for c in results if c["status"] == "ok" and c["gamma_estimable"] is True
                and isinstance(c["iii_drift_fraction_linear"], (int, float))]
    if eligible:
        top = max(eligible, key=lambda c: c["iii_drift_fraction_linear"])
        value, trips = top["iii_drift_fraction_linear"], top["iii_drift_fraction_linear"] > threshold
        tripwire = {"value": value, "cell": top["prompt_tokens"], "threshold": DRIFT_THRESHOLD,
                    "fallback_threshold": DRIFT_FALLBACK, "trips": trips,
                    "decision": "to the research lead" if trips else "within"}
    else:
        tripwire = {"value": None, "cell": None, "threshold": DRIFT_THRESHOLD, "fallback_threshold": DRIFT_FALLBACK,
                    "trips": None, "decision": "not_evaluable"}
    tripwire["threshold_applied"] = threshold
    return {"cells": results, "tripwire": tripwire}
