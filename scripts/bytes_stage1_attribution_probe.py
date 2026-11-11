#!/usr/bin/env python3
"""BYTES stage-1 attribution probe (research-lead ruling RL-80).

Run by the magistrate on the measurement Mac over the stage-1 outputs that already exist
(``bytes_stage1.py run --out $S1/run``) and the stage-1 export (``$S1/export``). It answers
stated questions about the 390 above-bar fields without showing any value.

What it prints, and nothing else:
- names: comparer group paths built only from a fixed vocabulary (the three registered fit
  models, boundaries, variants, passes), comparer field names, and flag codes that are in the
  registered block-6 flag catalog;
- counts (non-negative integers);
- each above-bar difference as a multiple of its own bar (|a - t| / bar, two significant
  figures, never signed);
- yes / no / not_evaluable answers to the questions in ``QUESTIONS``.

It never prints an energy, power, duration or bound value, the sign or direction of any
difference, or which side's value is larger. A name outside the vocabulary is counted, never
printed. It reads only: ``agreement-stage1.json``, ``agreement-blinded.json`` and
``out/a-fit/fit_pass_estimates.json`` under the run root; the ``.runs.csv`` and
``.session.json`` of the fit sessions under the export root; and the registered flag catalog
and bytes manifest in the repository. It refuses any path through a withheld store, a key
directory, custody, a held-out output or a stage-2 output. Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BMAP = {"rails": "rails", "DC input": "dc_input", "rest": "rest"}
VMAP = {("gross primary", "primary"): "gross", ("idle-subtracted secondary", "primary"): "idle_subtracted",
        ("gross primary", "flagged-inclusive"): "flagged_inclusive",
        ("idle-subtracted secondary", "flagged-inclusive"): "idle_flagged_inclusive"}
BOUNDARIES = tuple(BMAP.values())
VARIANTS = tuple(VMAP.values())
STRUCTURE_WORDS = frozenset({"cell", "commit", "fit_point", "tier_input", "without_assisted", "pass1", "pass2"})
SIDES = ("estimator_only", "twin_only")
METER_FLAGS = frozenset({"bytes.meter_decode_unavailable", "bytes.meter_gap", "bytes.decode_battery_assist"})
ANCHOR_COLUMN = "bound_E_clock_anchor_shift_bound_j"
DECODE_COLUMN = "phase_decode_j"
KEY_RE = re.compile(r"^[A-Za-z_]+(?::[A-Za-z_]+)?$")
REFUSED_PARTS = frozenset({"withheld", "released-keys", "no-keys", "custody", "night-custody", "a-held",
                           "post", "release-heldout", "keys"})
REFUSED_NAMES = frozenset({"t-2.json", "heldout_pass_estimates.json", "pack.json", "release.json"})

# Question texts are constants; they carry no digits so that every numeral in the output is a
# count or a multiple of a bar.
QUESTIONS = {
    "B_other_keys": "Is every above-bar field at stage fit one of flags, B_j, lower_j, upper_j, "
                    "attribution_floor_j, rails_attribution_floor_j, B_kind:anchor?",
    "B_other_kinds": "In this fit cell, are B_kind:interp, B_kind:drift and B_kind:meter_edge all within bar?",
    "B_is_anchor": "In this fit cell, does the B_j difference equal the B_kind:anchor difference within bar?",
    "B_centre_h": "In this fit cell, are mean_j, h_j and duration_s all within bar?",
    "B_ends": "In this fit cell, does each interval end move by exactly the B_j difference, within bar?",
    "B_twin_is_export": "Rails gross and flagged-inclusive cells: does the twin's anchor term equal the "
                        "stratified average of the export column bound_E_clock_anchor_shift_bound_j over its "
                        "kept runs, scaled by its own decode mean over the export phase_decode_j average "
                        "(blinding factor cancels), within bar?",
    "B_estimator_is_export": "Same cells: does the estimator's anchor term equal that same export-column "
                             "average, within bar?",
    "B_operative_one": "In this fit cell, is every operative record of status rereduced, with one operative "
                       "bound, equal to the export sidecar's operative_bound_s?",
    "W_follows_B": "Fit-commit w: does the w difference equal the mean over passes of the gross cell's "
                   "B_j difference, within the w bar?",
    "W_with_B": "Fit-commit w: is w above bar exactly when a gross cell B_j of that model and boundary is?",
    "F_row_flag_codes": "Is the code in the export flag_codes column of any row of the session?",
    "F_kept_flag_codes": "Is the code in the export flag_codes column of a kept run of the cell?",
    "F_exclusion_codes": "Is the code in the export exclusion_codes column of any row of the session?",
    "F_sidecar_counts": "Is the code in the session sidecar's flag_counts?",
    "F_every_cell": "Is the code in the estimator's flags of every fit cell of the session?",
    "F_meter_flag": "Is the code one of the meter-derived BYTES flags (meter_decode_unavailable, meter_gap, "
                    "decode_battery_assist)?",
    "F_blinded_estimator": "Is the code in the estimator's flags of the same rails cell at the blinded stage?",
}


class ProbeRefused(Exception):
    pass


def canon(name) -> str:
    text = str(name or "").strip().split("/")[-1].lower().replace("_", "-")
    return re.sub(r"-pinned$|\s+\(.*\)$", "", text)


def guard(path: Path) -> Path:
    path = Path(path)
    parts = set(path.resolve().parts) | set(path.parts)
    if parts & REFUSED_PARTS or path.name in REFUSED_NAMES or path.name.endswith(".withheld.csv"):
        raise ProbeRefused("refused: path outside the probe's permitted inputs")
    return path


def read_json(path: Path):
    return json.loads(guard(path).read_text(encoding="utf-8"))


def is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


# ---------------------------------------------------------------------------------------------
# The only way anything reaches stdout.

class Token(str):
    """A validated output token. Plain strings never reach stdout."""


class Name(Token):
    pass


PAIR_KEYS = frozenset({"yes", "no", "not_evaluable", "above_bar", "compared_fit", "cells", "unprintable_rows"})


class Out:
    """Typed, validated output. Every token is a Name, a count, a multiple or an answer."""

    def __init__(self, fit_models, catalog):
        self.fit_models = frozenset(fit_models)
        self.catalog = frozenset(catalog)
        self.lines = []
        self.unprintable = 0

    def group(self, text):
        parts = str(text).split("/")
        vocabulary = STRUCTURE_WORDS | set(BOUNDARIES) | set(VARIANTS) | self.fit_models
        if not parts or any(p not in vocabulary for p in parts):
            return None
        return Name(text)

    def key(self, text):
        return Name(text) if isinstance(text, str) and KEY_RE.match(text) else None

    def code(self, text):
        return Name(text) if text in self.catalog else None

    def effect(self, text):
        return Name("effect=" + text) if text in ("DISCLOSE", "EXCLUDE_MEMBER", "EXCLUDE_WINDOW") else None

    def word(self, text):
        allowed = set(BOUNDARIES) | set(SIDES) | {"fit", "fit-commit", "commit"} | set(QUESTIONS)
        if text not in allowed:
            raise ProbeRefused("refused: word outside the vocabulary")
        return Name(text)

    @staticmethod
    def count(value):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ProbeRefused("refused: a count must be a non-negative integer")
        return Token(str(value))

    @staticmethod
    def multiple(value):
        if not is_num(value) or value < 0:
            raise ProbeRefused("refused: a multiple of a bar must be finite and non-negative")
        return Token(format(float(f"{value:.2g}"), "g"))

    def pair(self, key, value):
        if key not in PAIR_KEYS:
            raise ProbeRefused("refused: pair outside the vocabulary")
        return Token(f"{key}={self.count(value)}")

    def emit(self, tag, *tokens):
        if tag not in ("TOTAL", "ABOVE", "MULT", "EXACT", "A", "FLAG", "FLAG_UNCATALOGUED", "FLAGQ"):
            raise ProbeRefused("refused: line tag outside the vocabulary")
        if not all(isinstance(token, Token) for token in tokens):
            raise ProbeRefused("refused: untyped output token")
        self.lines.append(" ".join((tag,) + tokens))

    def answer(self, qid, tally):
        self.emit("A", self.word(qid), *(self.pair(k, tally.get(k, 0)) for k in ("yes", "no", "not_evaluable")))

    def text(self):
        head = ["# BYTES stage-1 attribution probe (RL-80): names, counts, multiples of bar and yes/no only"]
        head += [f"Q {qid} {QUESTIONS[qid]}" for qid in QUESTIONS]
        tail = ["WITHHELD " + self.pair("unprintable_rows", self.unprintable)]
        return "\n".join(head + self.lines + tail) + "\n"


def tally_add(tally, verdict):
    tally[verdict] = tally.get(verdict, 0) + 1


# ---------------------------------------------------------------------------------------------
# Inputs.

def parse_group(group):
    parts = str(group).split("/")
    if parts[0] == "cell" and len(parts) >= 5:
        return {"kind": "cell", "model": parts[1], "pass": parts[2], "boundary": parts[3],
                "variant": parts[4], "sub": tuple(parts[5:])}
    if parts[0] == "commit" and len(parts) == 4:
        return {"kind": "commit", "what": parts[1], "boundary": parts[2], "model": parts[3]}
    return {"kind": "other"}


def index_rows(rows, stages):
    out = {}
    for row in rows:
        if row.get("stage") in stages:
            out.setdefault(row["group"], {})[row["key"]] = row
    return out


def numbers(row):
    if row is None:
        return None
    a, t, bar = row.get("a"), row.get("t"), row.get("bar")
    if not (is_num(a) and is_num(t) and is_num(bar)):
        return None
    return float(a), float(t), float(bar)


def read_export(export_root: Path, session_ids):
    """Fit sessions only. Rows keep code columns, identities and the two blinded columns needed for
    factor-free ratio checks; nothing else is retained."""
    guard(export_root)
    sessions = {}
    for sid in sorted(session_ids):
        tables = [guard(p) for p in export_root.glob(f"*/{sid}.runs.csv")]
        sidecars = [guard(p) for p in export_root.glob(f"*/{sid}.session.json")]
        if len(tables) != 1 or len(sidecars) != 1:
            sessions[sid] = None
            continue
        rows = []
        with tables[0].open(newline="", encoding="utf-8") as stream:
            for raw in csv.DictReader(stream):
                strata = (raw.get("strata") or "").split(";")
                stratum = next((s for s in strata if s in ("repeat", "quad")), None)
                def value(column):
                    try:
                        number = float(raw.get(column) or "nan")
                    except ValueError:
                        return None
                    return number if math.isfinite(number) else None
                rows.append({"run_id": raw.get("run_id"), "model": canon(raw.get("model_name")),
                             "pass_id": raw.get("pass_id"), "role": raw.get("role"), "stratum": stratum,
                             "flag_codes": set(filter(None, (raw.get("flag_codes") or "").split(";"))),
                             "exclusion_codes": set(filter(None, (raw.get("exclusion_codes") or "").split(";"))),
                             "anchor": value(ANCHOR_COLUMN), "decode": value(DECODE_COLUMN)})
        sidecar = read_json(sidecars[0])
        bound = sidecar.get("operative_bound_s")
        try:
            bound = float(bound) if bound is not None else None
        except (TypeError, ValueError):
            bound = None
        sessions[sid] = {"rows": rows, "flag_counts": set((sidecar.get("flag_counts") or {}).keys()),
                         "operative_bound_s": bound}
    return sessions


def stratified(rows, field):
    rep = [r[field] for r in rows if r["stratum"] == "repeat"]
    quad = [r[field] for r in rows if r["stratum"] == "quad"]
    if not rep or not quad or any(v is None for v in rep + quad):
        return None
    return 0.2 * statistics.fmean(rep) + 0.8 * statistics.fmean(quad)


# ---------------------------------------------------------------------------------------------
# The probe.

def probe(run_root: Path, export_root: Path, repo: Path) -> str:
    run_root, export_root = guard(Path(run_root)), guard(Path(export_root))
    catalog = read_json(Path(repo) / "configs/b6/flag_catalog_b6.json")["codes"]
    manifest = read_json(Path(repo) / "configs/bytes/bytes_manifest.json")
    fit_models = {canon(m["model"]) for m in manifest["models"] if m.get("role") == "fit"}
    out = Out(fit_models, catalog.keys() if isinstance(catalog, dict) else [c["code"] for c in catalog])

    stage1 = read_json(run_root / "agreement-stage1.json")
    blinded_path = run_root / "agreement-blinded.json"
    blinded = index_rows(read_json(blinded_path), {"blinded"}) if blinded_path.is_file() else {}
    fit_rows = read_json(run_root / "out/a-fit/fit_pass_estimates.json")
    fit_rows = [r for r in fit_rows if r.get("role") == "fit" and canon(r.get("model")) in fit_models]
    session_of = {(canon(r["model"]), f"pass{r['pass_id']}"): r["session_id"] for r in fit_rows}
    export = read_export(export_root, set(session_of.values()))

    above = [r for r in stage1 if r.get("status") == "above_bar"]
    compared = [r for r in stage1 if r.get("stage") in ("fit", "fit-commit")]
    out.emit("TOTAL", out.pair("above_bar", len(above)), out.pair("compared_fit", len(compared)))
    by_group = index_rows(stage1, {"fit", "fit-commit"})

    # Headline: above-bar names and counts, then each one as a multiple of its bar.
    headline, other_keys = {}, 0
    allowed_keys = {"flags", "B_j", "lower_j", "upper_j", "attribution_floor_j", "rails_attribution_floor_j",
                    "B_kind:anchor"}
    for row in above:
        info, group, key = parse_group(row.get("group")), out.group(row.get("group")), out.key(row.get("key"))
        if row.get("stage") not in ("fit", "fit-commit") or group is None or key is None:
            out.unprintable += 1
            continue
        where = "commit" if info["kind"] == "commit" else info["boundary"]
        headline[(row["stage"], where, key)] = headline.get((row["stage"], where, key), 0) + 1
        if row["stage"] == "fit" and key not in allowed_keys:
            other_keys += 1
    for (stage, where, key), n in sorted(headline.items()):
        out.emit("ABOVE", out.word(stage), out.word(where), key, out.count(n))
    out.answer("B_other_keys", {"yes": int(other_keys == 0), "no": int(other_keys > 0)})
    for row in above:
        group, key = out.group(row.get("group")), out.key(row.get("key"))
        if row.get("stage") not in ("fit", "fit-commit") or group is None or key is None:
            continue
        if row.get("bar") == "exact":
            out.emit("EXACT", group, key)
            continue
        nums = numbers(row)
        if nums is None or nums[2] <= 0:
            out.emit("EXACT", group, key)
            continue
        out.emit("MULT", group, key, out.multiple(abs(nums[0] - nums[1]) / nums[2]))

    # Item 1: the bound.
    tallies = {q: {} for q in ("B_other_kinds", "B_is_anchor", "B_centre_h", "B_ends", "B_twin_is_export",
                               "B_estimator_is_export", "B_operative_one", "W_follows_B", "W_with_B")}
    for group, keys in sorted(by_group.items()):
        info = parse_group(group)
        if info["kind"] != "cell" or info["sub"] or out.group(group) is None or "B_j" not in keys:
            continue
        others = [keys.get(k) for k in ("B_kind:interp", "B_kind:drift", "B_kind:meter_edge") if k in keys]
        tally_add(tallies["B_other_kinds"], "no" if any(r["status"] == "above_bar" for r in others) else "yes")
        B, A = numbers(keys.get("B_j")), numbers(keys.get("B_kind:anchor"))
        if B and A:
            tally_add(tallies["B_is_anchor"], "yes" if abs((B[0] - B[1]) - (A[0] - A[1])) <= B[2] else "no")
        else:
            tally_add(tallies["B_is_anchor"], "not_evaluable")
        centre = [keys.get(k) for k in ("mean_j", "h_j", "duration_s")]
        tally_add(tallies["B_centre_h"], "not_evaluable" if None in centre else
                  "no" if any(r["status"] == "above_bar" for r in centre) else "yes")
        L, U = numbers(keys.get("lower_j")), numbers(keys.get("upper_j"))
        if B and L and U:
            dB = B[0] - B[1]
            ok = abs((L[0] - L[1]) + dB) <= L[2] and abs((U[0] - U[1]) - dB) <= U[2]
            tally_add(tallies["B_ends"], "yes" if ok else "no")
        else:
            tally_add(tallies["B_ends"], "not_evaluable")
        if info["boundary"] == "rails" and info["variant"] in ("gross", "flagged_inclusive"):
            session = export.get(session_of.get((info["model"], info["pass"])))
            kept = keys.get("kept_runs")
            M = numbers(keys.get("mean_j"))
            for qid, side in (("B_twin_is_export", "t"), ("B_estimator_is_export", "a")):
                if session is None or kept is None or not isinstance(kept.get(side), list) or not (A and M):
                    tally_add(tallies[qid], "not_evaluable")
                    continue
                ids = set(kept[side])
                pass_number = info["pass"][4:]
                # The session is already the model's pass; run ids are unique within it.
                members = [r for r in session["rows"] if r["run_id"] in ids and str(r["pass_id"]) == pass_number]
                ratio_anchor, ratio_decode = stratified(members, "anchor"), stratified(members, "decode")
                if len(members) != len(ids) or ratio_anchor is None or not ratio_decode:
                    tally_add(tallies[qid], "not_evaluable")
                    continue
                anchor, mean = (A[1], M[1]) if side == "t" else (A[0], M[0])
                predicted = mean * ratio_anchor / ratio_decode
                tally_add(tallies[qid], "yes" if abs(anchor - predicted) <= A[2] else "no")
    by_cell = {}
    for r in fit_rows:
        variant = VMAP.get((r.get("basis"), r.get("selection")))
        if r.get("status") != "computed" or variant is None:
            continue
        session = export.get(r["session_id"])
        ops = r.get("operative") or []
        bounds = {op.get("operative_bound_s") for op in ops}
        ok = (session is not None and session["operative_bound_s"] is not None and ops
              and all(op.get("status") == "rereduced" for op in ops) and len(bounds) == 1
              and all(is_num(b) and float(b) == session["operative_bound_s"] for b in bounds))
        tally_add(tallies["B_operative_one"], "yes" if ok else "no")
        by_cell[(canon(r["model"]), f"pass{r['pass_id']}", BMAP.get(r["boundary"]), variant)] = r

    # Item 3: w at fit-commit.
    for group, keys in sorted(by_group.items()):
        info = parse_group(group)
        if info["kind"] != "commit" or info["what"] != "fit_point" or "w" not in keys or out.group(group) is None:
            continue
        W = numbers(keys["w"])
        cells = [by_group.get(f"cell/{info['model']}/{p}/{info['boundary']}/gross", {}) for p in ("pass1", "pass2")]
        deltas = [numbers(c.get("B_j")) for c in cells if c.get("B_j") is not None]
        deltas = [d for d in deltas if d is not None]
        if W is None or not deltas:
            tally_add(tallies["W_follows_B"], "not_evaluable")
        else:
            mean_dB = statistics.fmean(d[0] - d[1] for d in deltas)
            tally_add(tallies["W_follows_B"], "yes" if abs((W[0] - W[1]) - mean_dB) <= W[2] else "no")
        b_above = any(c.get("B_j", {}).get("status") == "above_bar" for c in cells)
        tally_add(tallies["W_with_B"], "yes" if (keys["w"].get("status") == "above_bar") == b_above else "no")
    for qid, tally in tallies.items():
        out.answer(qid, tally)

    # Item 2: the flags.
    flag_cells, flag_sessions, uncatalogued = {}, {}, 0
    fit_cell_flags = {}
    for r in fit_rows:
        fit_cell_flags.setdefault(r["session_id"], []).append(set(r.get("flags") or []))
    for row in above:
        if row.get("stage") != "fit" or row.get("key") != "flags":
            continue
        info = parse_group(row.get("group"))
        if info["kind"] != "cell" or out.group(row.get("group")) is None:
            continue
        a, t = set(row.get("a") or []), set(row.get("t") or [])
        sid = session_of.get((info["model"], info["pass"]))
        for side, codes in (("estimator_only", a - t), ("twin_only", t - a)):
            for code in sorted(codes):
                name = out.code(code)
                if name is None:
                    uncatalogued += 1
                    continue
                flag_cells[(info["boundary"], side, name)] = flag_cells.get((info["boundary"], side, name), 0) + 1
                flag_sessions.setdefault(name, {}).setdefault(sid, set()).add(
                    (info["model"], info["pass"], info["boundary"], info["variant"], info["sub"]))
    effects = catalog if isinstance(catalog, dict) else {c["code"]: c for c in catalog}
    for (boundary, side, name), n in sorted(flag_cells.items()):
        effect = out.effect(str((effects.get(name) or {}).get("effect", "")))
        out.emit("FLAG", out.word(boundary), out.word(side), name, out.pair("cells", n), *([effect] if effect else []))
    if uncatalogued:
        out.emit("FLAG_UNCATALOGUED", out.pair("cells", uncatalogued))
    for name, per_session in sorted(flag_sessions.items()):
        answers = {q: {} for q in ("F_row_flag_codes", "F_kept_flag_codes", "F_exclusion_codes", "F_sidecar_counts",
                                   "F_every_cell", "F_meter_flag", "F_blinded_estimator")}
        for sid, cells in sorted(per_session.items(), key=lambda item: str(item[0])):
            session = export.get(sid)
            if session is None:
                for q in answers:
                    tally_add(answers[q], "not_evaluable")
                continue
            tally_add(answers["F_row_flag_codes"], "yes" if any(name in r["flag_codes"] for r in session["rows"]) else "no")
            tally_add(answers["F_exclusion_codes"],
                      "yes" if any(name in r["exclusion_codes"] for r in session["rows"]) else "no")
            tally_add(answers["F_sidecar_counts"], "yes" if name in session["flag_counts"] else "no")
            flags = fit_cell_flags.get(sid, [])
            tally_add(answers["F_every_cell"], "yes" if flags and all(name in f for f in flags) else "no")
            tally_add(answers["F_meter_flag"], "yes" if name in METER_FLAGS else "no")
            kept_hit, blinded_hit, blinded_seen = False, False, False
            for model, pass_, boundary, variant, sub in cells:
                kept = by_group.get("/".join(("cell", model, pass_, boundary, variant) + sub), {}).get("kept_runs")
                ids = set((kept or {}).get("a") or [])
                pass_number = pass_[4:]
                kept_hit |= any(name in r["flag_codes"] for r in session["rows"] if r["run_id"] in ids
                                and str(r["pass_id"]) == pass_number)
                # The blinded stage computes rails only: the same model, pass and variant on rails.
                b = blinded.get("/".join(("cell", model, pass_, "rails", variant) + sub), {}).get("flags")
                if b is not None:
                    blinded_seen = True
                    blinded_hit |= name in set(b.get("a") or [])
            tally_add(answers["F_kept_flag_codes"], "yes" if kept_hit else "no")
            tally_add(answers["F_blinded_estimator"], "not_evaluable" if not blinded_seen else
                      "yes" if blinded_hit else "no")
        for q, tally in answers.items():
            out.emit("FLAGQ", name, out.word(q), *(out.pair(k, tally.get(k, 0)) for k in ("yes", "no", "not_evaluable")))
    return out.text()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-root", required=True, type=Path, help="the stage-1 --out directory ($S1/run)")
    parser.add_argument("--export", required=True, type=Path, help="the stage-1 export root ($S1/export)")
    parser.add_argument("--repo", type=Path, default=ROOT, help="checkout holding the registered catalog and manifest")
    args = parser.parse_args(argv)
    try:
        text = probe(args.run_root, args.export, args.repo)
    except ProbeRefused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - the class only: a message or traceback could quote a value
        print(f"probe failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
