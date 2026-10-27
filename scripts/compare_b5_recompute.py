#!/usr/bin/env python3
"""Compare L9's block-5 dry-run restricted outputs with the independent recompute.

Standard library only; imports no repository code (never joulewise.b5_analysis).
Inputs: L9's dry-run custody root (its record and restricted folder), the
recompute's --member-detail output, and a bar-set config. No bar is coded here:
every numeric family's bar comes from the config, and a family the config does
not name refuses the run.

Rules (RC-CMP-1 A1-A4):
- numeric families pass when both sides are finite numbers within the family bar;
- categorical families (outcome words, dominance branch, p42 status, Holm order,
  the recompute's exclusion re-derivation) pass only on exact equality;
- a value missing or null on either side is DISAGREE;
- every leaf of the step-11 outputs (fill input and disclosure record) must match
  a coverage rule, either a comparison family or a listed uncovered reason; an
  unmapped leaf refuses the run;
- stdout carries per-family pass/fail counts and structure codes only; values and
  observed differences go only to the restricted output file.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

SCHEMA = "joulewise.b5_recompute_comparison.v1"
BARS_SCHEMA = "joulewise.b5_comparator_bars.v1"
RECORD = "dry-run/B5-BLIND-DRY-RUN-RECORD.json"
RESTRICTED = "dry-run/restricted"
PACKS = {"alpha": "ALPHA", "beta": "BETA", "gamma": "GAMMA"}
MODELS = {"alpha": "Qwen3-1.7B-4bit", "beta": "Qwen3-8B-4bit"}
NUMERIC = ("run_phase_energy_j", "floor_j", "floor_gate_j", "dominance_ratio", "reported_cell_j",
           "contrast_j", "contrast_p", "b_op_s", "count")
CATEGORICAL = ("outcome_word", "dominance_branch", "p42_status", "holm_order", "exclusions_rederivation")


class Refusal(Exception):
    """A structure-only reason the comparison cannot be evaluated."""


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def get(obj, *keys, default=None):
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and isinstance(key, int) and -len(obj) <= key < len(obj):
            obj = obj[key]
        else:
            return default
    return obj


def load_bars(path):
    try:
        bars = json.loads(Path(path).read_bytes())
    except (OSError, ValueError):
        raise Refusal("bars_unreadable") from None
    if not isinstance(bars, dict) or bars.get("schema") != BARS_SCHEMA or not isinstance(bars.get("families"), dict):
        raise Refusal("bars_invalid")
    for family in NUMERIC:
        spec = bars["families"].get(family)
        if not isinstance(spec, dict):
            raise Refusal("bars_family_missing:" + family)
        for key in ("absolute", "relative"):
            if key in spec and (not finite(spec[key]) or spec[key] < 0):
                raise Refusal("bars_invalid:" + family)
        if "printed_decimals" in spec and (type(spec["printed_decimals"]) is not int or spec["printed_decimals"] < 0):
            raise Refusal("bars_invalid:" + family)
        if not {"absolute", "relative", "printed_decimals"} & set(spec):
            raise Refusal("bars_invalid:" + family)
    return bars


def bar_for(spec, reference):
    parts = [spec.get("absolute", 0.0), spec.get("relative", 0.0) * abs(reference)]
    if "printed_decimals" in spec:
        parts.append(0.5 * 10.0 ** -spec["printed_decimals"])
    return max(parts)


class Comparison:
    def __init__(self, bars):
        self.bars, self.rows = bars, []

    def numeric(self, family, key, l9, ours):
        assert family in NUMERIC, family
        row = {"family": family, "key": key, "l9": l9, "recompute": ours}
        if finite(l9) and finite(ours):
            row["difference"] = ours - l9
            row["bar"] = bar_for(self.bars["families"][family], l9)
            row["verdict"] = "AGREE" if abs(ours - l9) <= row["bar"] else "DISAGREE"
        else:
            row["verdict"], row["reason"] = "DISAGREE", "missing_or_null"
        self.rows.append(row)
        return row

    def exact(self, family, key, l9, ours):
        assert family in CATEGORICAL, family
        missing = l9 is None or ours is None
        row = {"family": family, "key": key, "l9": l9, "recompute": ours,
               "verdict": "AGREE" if not missing and l9 == ours else "DISAGREE"}
        if missing:
            row["reason"] = "missing_or_null"
        self.rows.append(row)
        return row

    def keys(self):
        return {(row["family"], row["key"]) for row in self.rows}

    def counts(self):
        counts = {family: {"pass": 0, "fail": 0} for family in NUMERIC + CATEGORICAL}
        for row in self.rows:
            counts[row["family"]]["pass" if row["verdict"] == "AGREE" else "fail"] += 1
        return counts


class Custody:
    """L9's dry-run custody: every file used must be listed in the record with its digest."""
    def __init__(self, root):
        self.root = Path(root)
        self.restricted = self.root / RESTRICTED
        try:
            self.record = json.loads((self.root / RECORD).read_bytes())
        except (OSError, ValueError):
            raise Refusal("l9_record_unreadable") from None
        self.listed, self.status = {}, {}
        for row in self.record.get("steps", []):
            key = (row.get("step"), row.get("window"))
            self.status[key] = row.get("status")
            for output in row.get("outputs", []):
                self.listed[output["name"]] = output["sha256"]

    def step_ok(self, step, window=None):
        return self.status.get((step, window)) == "ok"

    def names(self, pattern):
        return sorted(name for name in self.listed if re.fullmatch(pattern, name))

    def read(self, name):
        if name not in self.listed:
            raise Refusal("l9_output_unlisted")
        try:
            raw = (self.restricted / name).read_bytes()
        except OSError:
            raise Refusal("l9_output_unreadable") from None
        if hashlib.sha256(raw).hexdigest() != self.listed[name]:
            raise Refusal("l9_output_digest_differs")
        return json.loads(raw)

    def one(self, pattern):
        names = self.names(pattern)
        if len(names) > 1:
            raise Refusal("l9_output_ambiguous")
        return self.read(names[0]) if names else None
