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
  The threshold is 0.04 if RL-166 Q11's condition fails. The custody entry point reads it from the committed
  manifest's drift_tripwire decision (Mythos cold seat 11), so it is a frozen value, not a run-time choice.

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
    # Sol round-4 NEW-2: run the bytes just hashed, never a cached compilation of the file
    spec = importlib.util.spec_from_loader(f"_step3_{uuid.uuid4().hex}", loader=None, origin=str(path))
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
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
        cell.update(status="ok", n_legs=len(tuples), details=out, **_project(out, {t[0] for t in tuples}))
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


def entries_from_stage1(stage1, sdir_of):
    import json
    from joulewise.cadence_looks import manifest as lm

    out = []
    for leg in stage1["legs"]:
        if not (leg.get("included") is True and leg.get("role") == "fit" and leg.get("leg_type") == "A"):
            continue
        span_id, leg_id = leg["leg_key"].split("/", 1)
        sdir = Path(sdir_of(span_id))
        record = json.loads((sdir / "legs" / leg_id / "leg_record.json").read_text(encoding="utf-8"))
        bundle = lm.runtime_bundle(sdir, leg_id, record)
        if bundle is None:
            raise ValueError("an included Step 3 leg has no bundle")
        out.append({"key": leg["leg_key"], "day": leg["day"], "bundle": str(bundle),
                    "role": "fit", "leg_type": "A", "included": True, "prompt_tokens_nominal": leg["cell_prompt_tokens"]})
    return out


def custody_problems(stage1, sdir_of):
    """Bind operational sources and every selected trace's time projection before any value reader runs.

    Step 3 includes legs with missing start readings, which are outside the energy fit. Their trace timing
    still must be the timing stage 1 judged. Synthetic level-R fixtures without custody retain their test path.
    """
    from joulewise.cadence_looks import manifest as lm
    from joulewise.cadence_looks import time_fields as tf
    ids = [leg["span_id"] for leg in stage1["legs"]
           if leg.get("included") is True and leg.get("role") == "fit" and leg.get("leg_type") == "A"]
    problems = lm.nonenergy_problems(stage1, sdir_of, ids)
    if problems:
        return problems
    spans = {sp["span_id"]: sp for sp in stage1["roster"]["spans"]}
    for leg in stage1["legs"]:
        if not (leg.get("included") is True and leg.get("role") == "fit" and leg.get("leg_type") == "A"):
            continue
        if stage1.get("synthetic") is True and (spans.get(leg["span_id"]) or {}).get("custody") is None:
            continue
        expected = ((leg.get("trace_holes") or {}).get("gpu_rail") or {}).get("rows_sha256")
        try:
            # Operational hashes above authenticate this bundle locator before it is used.
            import json
            sdir = Path(sdir_of(leg["span_id"]))
            leg_id = leg["leg_key"].split("/", 1)[1]
            record = json.loads((sdir / "legs" / leg_id / "leg_record.json").read_text(encoding="utf-8"))
            bundle = lm.runtime_bundle(sdir, leg_id, record)
            if bundle is None:
                raise ValueError("an included Step 3 leg has no bundle")
            rows = tf.gpu_rows(bundle)
            if expected is None or tf.rows_digest(rows) != expected:
                problems.append(f"custody: {leg['leg_key']}'s power_trace.csv is not the one stage 1 read (row stamps)")
        except (OSError, ValueError, TypeError, KeyError, tf.TimeFieldError):
            problems.append(f"custody: {leg['leg_key']}'s power_trace.csv: time projection unreadable")
    return problems


def custody_record(custody, overrides, entries, sdir_of, stage1=None):
    """What step 3 read, by path and sha256 (a hash of bytes, not a value): assemble requires the fit's GPU traces to
    be these (Mythos round-5 N6)."""
    from joulewise.cadence_looks import manifest as lm
    # A synthetic level-R fixture may carry no custody map or runner roster. Record operational
    # sources only where D bound them; real stage-1 files are required to carry that map.
    bound = {sp["span_id"] for sp in ((stage1 or {}).get("roster") or {}).get("spans") or []
             if sp.get("custody") is not None}
    files = [{"path": f"{sid}/{rel}", "sha256": sha}
             for sid in sorted({e["key"].split("/", 1)[0] for e in entries} & bound)
             for rel, sha in lm.nonenergy_files(sdir_of(sid)).items()]
    for e in entries:
        span_id = e["key"].split("/", 1)[0]
        b = Path(e["bundle"])
        rel = b.relative_to(Path(sdir_of(span_id))).as_posix()
        for name in ("power_trace.csv", "rich_telemetry.jsonl", "raw/powermetrics.plist"):
            if (b / name).is_file():
                files.append({"path": f"{span_id}/{rel}/{name}",
                              "sha256": hashlib.sha256((b / name).read_bytes()).hexdigest()})
    return {"root": str(Path(custody).resolve()),
            "span_dirs": [{"span_id": k, "path": str(Path(v).resolve())}
                          for k, v in sorted(dict(o.split("=", 1) for o in overrides).items())],
            "files": sorted(files, key=lambda f: f["path"])}
