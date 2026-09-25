"""A292 HEADLINE-REDUCER-SEALED-01 acceptance harness (E2 v1.1).

The reducer import is deliberately inside ``_reducer`` so each witness is RED
individually until the implementation seat adds joulewise.scored_reduce.

Implementation gate ledger, M8 (run by the magistrate after implementation):
operand-collapse, > versus >= boundary, and guard-deletion sweeps over the
reducer must leave zero survivors. Required killed mutants: >= to > in
``capped``; > to >= in ``cap_bound``; ``sr.CAP_BOUND_FRACTION`` to a literal;
drop K24 pairing; sum window energy per item; drop missing_live_window,
row_tokens_over_cap, anchor, or internal_disagreement guards.
"""
from __future__ import annotations

import ast
from contextlib import ExitStack
from copy import deepcopy
import hashlib
import importlib
import inspect
import json
import math
from pathlib import Path
import random
import re
import unittest
from unittest.mock import patch

import joulewise.scored_packer as sp
import joulewise.scored_registration as sr
from tests.scored_case_generator import generate_case, pending
from tests.scored_reduce_checker import check_reduction, OUTPUT_KEYS, WINDOW_KEYS
from tests.scored_roster_checker import check_executed, check_roster, digest
from tests.test_scored_registration import fixture


def _reducer():
    return importlib.import_module("joulewise.scored_reduce")


def _night(n=5, width=1, mode="registered", policy=None, budget_j=None):
    cap = 6.0
    g, predictions = fixture(n=n, block_size=width, mode=mode, pred=.9, worst=1.0, cap=cap)
    g["cap_tokens"] = {g["arm"]: 5}
    g["s_per_token_upper"] = {model: {g["arm"]: .2} for model in g["role_to_model_id"].values()}
    if budget_j is not None:
        g["budget_j"] = budget_j
    reg = sr.Registration.from_mapping(g)
    roster = sp.pack(reg, predictions)
    while pending(roster) is not None:
        env = pending(roster)
        blocks = {b["block_id"]: b for b in roster["blocks"]}
        observations = []
        phase = False
        for bid in env["blocks"]:
            b = blocks[bid]
            status, elapsed = policy(roster, env, b) if policy is not None else ("completed", .1)
            if phase:
                status, elapsed = "not_started", None
            if status != "completed":
                phase = True
            observations.append(dict(block_id=bid, status=status, elapsed_s=elapsed))
        roster = sp.requeue_overrun(reg, roster, env["index"], observations)
    sp.verify_executed_roster(reg, roster, predictions)
    assert check_roster(g, roster, predictions) == []
    return g, reg, roster, predictions


def _in_force(roster, envelope_index):
    digest = roster["registered_sha256"]
    for event in roster["events"]:
        if event["envelope_index"] < envelope_index:
            digest = event["sha256"]
    return digest


def _inputs(g, reg, roster, *, optional=False, seed=0):
    blocks = {b["block_id"]: b for b in roster["blocks"]}
    rows, windows = [], []
    rng = random.Random(seed)
    for position, p in enumerate(roster["placements"]):
        env = roster["envelopes"][p["envelope_index"]]
        live = p["block_id"] in env["blocks"]
        observation = next(o for o in env["observations"] if o["block_id"] == p["block_id"])
        if not live and (not optional or observation["status"] == "not_started" or rng.random() >= .5):
            continue
        window = dict(schema="joulewise.scored_window.v1", registration_sha256=reg.digest,
                      roster_sha256=_in_force(roster, p["envelope_index"]),
                      block_id=p["block_id"], attempt=p["attempt"],
                      envelope_index=p["envelope_index"], gross_j=float(position + 1),
                      bundle_sha256="b" * 64,
                      energy_bound_terms_j={"E_clock_anchor_shift_bound_j": .125 if live else None})
        windows.append(window)
        for item_id in blocks[p["block_id"]]["items"]:
            rows.append(dict(schema="joulewise.scored_row.v1", registration_sha256=reg.digest,
                             roster_sha256=roster["sha256"], scorer_id=g["scorer_id"],
                             block_id=p["block_id"], attempt=p["attempt"], item_id=item_id,
                             prompt_tokens=3, generated_tokens=min(1, g["cap_tokens"][g["arm"]] - 1), stop_reason="stop",
                             extracted_answer="answer", scorer_match=True))
    return rows, windows


def _first_live(roster):
    return next(p for p in roster["placements"]
                if p["block_id"] in roster["envelopes"][p["envelope_index"]]["blocks"])


def _first_nonlive(roster, status=None):
    for p in roster["placements"]:
        env = roster["envelopes"][p["envelope_index"]]
        if p["block_id"] in env["blocks"]:
            continue
        obs = next(o for o in env["observations"] if o["block_id"] == p["block_id"])
        if status is None or obs["status"] == status:
            return p
    raise AssertionError("fixture lacks requested non-live placement")


def _add_window(g, reg, roster, p, gross=7.0, anchor=None):
    return dict(schema="joulewise.scored_window.v1", registration_sha256=reg.digest,
                roster_sha256=_in_force(roster, p["envelope_index"]),
                block_id=p["block_id"], attempt=p["attempt"],
                envelope_index=p["envelope_index"], gross_j=gross,
                bundle_sha256="c" * 64,
                energy_bound_terms_j={"E_clock_anchor_shift_bound_j": anchor})


def _add_row(g, reg, roster, p):
    block = next(b for b in roster["blocks"] if b["block_id"] == p["block_id"])
    return dict(schema="joulewise.scored_row.v1", registration_sha256=reg.digest,
                roster_sha256=roster["sha256"], scorer_id=g["scorer_id"],
                block_id=p["block_id"], attempt=p["attempt"], item_id=block["items"][0],
                prompt_tokens=3, generated_tokens=1, stop_reason="stop",
                extracted_answer="answer", scorer_match=True)


def _terminal_night(width=1, kind="unattributed_overrun"):
    target = None
    def policy(roster, env, block):
        nonlocal target
        if target is None:
            target = block["block_id"]
        if block["block_id"] == target:
            stage = block["retry_stage"]
            if kind == "unattributed_overrun":
                return ("cut_off", .1) if stage == "initial" else ("completed", .1)
            if stage in ("initial", "whole_block", "single_problem", "single_retry"):
                return "cut_off" if stage in ("initial", "whole_block") else "completed", 1.1 if stage.startswith("single") else 1.9 if width == 2 else 1.1
        if block["parent_block_id"] == target and kind == "ceiling_violation":
            return "completed", 1.1
        return "completed", .1
    return _night(n=10 if width == 2 else 5, width=width, policy=policy)


class ScoredReduceTests(unittest.TestCase):
    def setUp(self):
        self.g, self.reg, self.roster, self.predictions = _night()
        self.rows, self.windows = _inputs(self.g, self.reg, self.roster)

    def _invoke(self, rows=None, windows=None, roster=None, reg=None, predictions=None):
        reducer = _reducer()
        return reducer.reduce(reg or self.reg, roster or self.roster,
                              predictions or self.predictions,
                              self.rows if rows is None else rows,
                              self.windows if windows is None else windows)

    def _refuses(self, code, rows=None, windows=None, roster=None, reg=None, predictions=None,
                 detail_contains=None):
        reducer = _reducer()
        r = roster or self.roster
        g = (reg or self.reg).to_mapping()
        p = predictions or self.predictions
        score_rows = self.rows if rows is None else rows
        capture_windows = self.windows if windows is None else windows
        with self.assertRaises(reducer.ReductionRefusal) as caught:
            reducer.reduce(reg or self.reg, r, p, score_rows, capture_windows)
        self.assertEqual(caught.exception.code, code)
        self.assertTrue(hasattr(caught.exception, "detail"))
        if detail_contains is not None:
            self.assertIn(detail_contains, str(caught.exception.detail))
        self.assertEqual(check_reduction(g, r, p, score_rows, capture_windows,
                         {"refusal_code": caught.exception.code, "detail": caught.exception.detail}), [])

    def _accepted(self, rows=None, windows=None, roster=None, reg=None, predictions=None):
        r = roster or self.roster
        registration = reg or self.reg
        p = predictions or self.predictions
        score_rows = self.rows if rows is None else rows
        capture_windows = self.windows if windows is None else windows
        candidate = self._invoke(score_rows, capture_windows, r, registration, p)
        self.assertEqual(check_reduction(registration.to_mapping(), r, p,
                                         score_rows, capture_windows, candidate), [])
        return candidate

    def test_ast_first_statement_is_verifier(self):
        module = _reducer()
        tree = ast.parse(inspect.getsource(module.reduce))
        node = next(x for x in ast.walk(tree) if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)))
        first = node.body[0]
        self.assertIsInstance(first, ast.Expr)
        self.assertIsInstance(first.value, ast.Call)
        self.assertEqual(ast.unparse(first.value),
                         "verify_executed_roster(registration, roster, predicted_decode_s)")

    def test_signature_five_positional(self):
        signature = inspect.signature(_reducer().reduce)
        self.assertEqual(list(signature.parameters),
                         ["registration", "roster", "predicted_decode_s", "score_rows", "capture_windows"])
        self.assertTrue(all(p.default is inspect.Parameter.empty and
                            p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
                            for p in signature.parameters.values()))

    def test_packing_refusal_passes_through(self):
        reducer = _reducer()
        cases = []
        gp, regp, rp, pp = _night(mode="pilot")
        wrong_predictions = deepcopy(pp)
        wrong_predictions["large"][gp["item_ids_by_level"]["1"][0]] = .8
        cases.append((regp, rp, wrong_predictions, "inv_39"))
        wrong_digest = deepcopy(self.roster)
        wrong_digest["registration_sha256"] = "0" * 64
        cases.append((self.reg, wrong_digest, self.predictions, "inv_01"))
        unreported = sp.pack(self.reg, self.predictions)
        cases.append((self.reg, unreported, self.predictions, "unreported_envelope"))
        g2, reg2, roster2, p2 = _night(policy=lambda r,e,b: ("cut_off", 1.1) if not r["events"] else ("completed", .1))
        tampered = deepcopy(roster2)
        tampered["events"][0]["sha256"] = "0" * 64
        cases.append((reg2, tampered, p2, "inv_38"))
        for reg, roster, p, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(sp.PackingRefusal) as caught:
                    reducer.reduce(reg, roster, p, [], [])
                self.assertEqual(caught.exception.code, code)

    def test_reduce_input_not_list(self):
        self._refuses("reduce_input", rows={})
        self._refuses("reduce_input", windows={})

    def test_window_keys(self):
        self.assertEqual(WINDOW_KEYS, frozenset({
            "schema", "registration_sha256", "roster_sha256", "block_id", "attempt",
            "envelope_index", "gross_j", "bundle_sha256", "energy_bound_terms_j",
        }))
        self.assertEqual(set(self.windows[0]), WINDOW_KEYS)
        w = deepcopy(self.windows); w[0]["extra"] = 1
        self._refuses("window_keys", windows=w)
        w = deepcopy(self.windows); w[0].pop("energy_bound_terms_j")
        self._refuses("window_keys", windows=w)

    def test_window_domain_zero_negative_nonfinite_bool_anchor(self):
        for field, values in (("gross_j", [0, -1, float("nan"), float("inf"), True]),
                              ("attempt", [-1, True]), ("bundle_sha256", ["bad"])):
            for value in values:
                with self.subTest(field=field, value=value):
                    w = deepcopy(self.windows); w[0][field] = value
                    self._refuses("window_domain", windows=w)
        for anchor in [-1, float("nan"), float("inf"), True, "1"]:
            w = deepcopy(self.windows)
            w[0]["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"] = anchor
            self._refuses("window_domain", windows=w)
        w = deepcopy(self.windows); w[0]["energy_bound_terms_j"]["extra"] = 1
        self._refuses("window_domain", windows=w)

    def test_window_unknown_and_idle_slot(self):
        w = deepcopy(self.windows); w[0]["block_id"] = "foreign"
        self._refuses("window_unknown", windows=w)
        idle = next((e for e in self.roster["envelopes"] if e["kind"] == "idle_slot"), None)
        if idle is not None:
            w = deepcopy(self.windows)
            ghost = deepcopy(w[0]); ghost["block_id"] = "idle-ghost"; ghost["envelope_index"] = idle["index"]
            w.append(ghost)
            self._refuses("window_unknown", windows=w)

    def test_window_binding_in_force_stale_and_final_stamp_refused(self):
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        target = next(i for i,w in enumerate(windows) if w["roster_sha256"] != roster["sha256"])
        for stamp in ("0" * 64, roster["sha256"]):
            bad = deepcopy(windows); bad[target]["roster_sha256"] = stamp
            self._refuses("window_binding", rows=rows, windows=bad, roster=roster, reg=reg, predictions=p)
        bad = deepcopy(windows); bad[0]["registration_sha256"] = "0" * 64
        self._refuses("window_binding", rows=rows, windows=bad, roster=roster, reg=reg, predictions=p)

    def test_window_duplicate(self):
        self._refuses("window_duplicate", windows=self.windows + [deepcopy(self.windows[0])])

    def test_window_envelope_mismatch(self):
        w = deepcopy(self.windows); w[0]["envelope_index"] += 1
        self._refuses("window_envelope", windows=w)

    def test_window_unstarted_only_on_nonlive_keys(self):
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        nonlive = _first_nonlive(roster, "not_started")
        windows.append(_add_window(g, reg, roster, nonlive))
        self._refuses("window_unstarted", rows=rows, windows=windows, roster=roster, reg=reg, predictions=p)

    def test_anchor_unrecorded_live_refuses_nonlive_null_ok(self):
        w = deepcopy(self.windows); w[0]["energy_bound_terms_j"]["E_clock_anchor_shift_bound_j"] = None
        self._refuses("anchor_energy_envelope_unrecorded", windows=w)
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        nonlive = _first_nonlive(roster, "cut_off")
        windows.append(_add_window(g, reg, roster, nonlive, anchor=None))
        self._accepted(rows, windows, roster, reg, p)

    def test_missing_live_window_names_key(self):
        removed = self.windows[0]
        key = (removed["block_id"], removed["attempt"])
        self._refuses("missing_live_window", windows=self.windows[1:], detail_contains=repr(key))

    def test_a291_partial_keys_refuse_at_reduce(self):
        for width in (1, 2):
            with self.subTest(width=width):
                g, reg, roster, p = _terminal_night(width=width)
                rows, windows = _inputs(g, reg, roster)
                lost = windows[0]
                self._refuses("missing_live_window", rows=rows, windows=windows[1:],
                              roster=roster, reg=reg, predictions=p,
                              detail_contains=repr((lost["block_id"], lost["attempt"])))

    def test_row_keys(self):
        rows = deepcopy(self.rows); rows[0].pop("prompt_tokens")
        self._refuses("row_keys", rows=rows)

    def test_row_domain_and_coherence(self):
        for field, value in (("prompt_tokens", True), ("generated_tokens", -1),
                             ("scorer_match", 1), ("extracted_answer", ""), ("schema", "bad")):
            rows = deepcopy(self.rows); rows[0][field] = value
            self._refuses("row_domain", rows=rows)
        rows = deepcopy(self.rows); rows[0]["extracted_answer"] = None
        self._refuses("row_domain", rows=rows)

    def test_row_stop_reason_unknown_incl_runtime_failed(self):
        for reason in ("runtime_failed", "malformed", "stream_exhausted"):
            rows = deepcopy(self.rows); rows[0]["stop_reason"] = reason
            self._refuses("row_stop_reason_unknown", rows=rows)

    def test_row_scorer_id(self):
        rows = deepcopy(self.rows); rows[0]["scorer_id"] = "other"
        self._refuses("row_scorer", rows=rows)

    def test_row_unknown_item_not_in_block(self):
        rows = deepcopy(self.rows); rows[0]["item_id"] = "foreign"
        self._refuses("row_unknown", rows=rows)
        rows = deepcopy(self.rows); rows[0]["block_id"] = "foreign"
        self._refuses("row_unknown", rows=rows)

    def test_row_binding_final_digest(self):
        rows = deepcopy(self.rows); rows[0]["roster_sha256"] = self.roster["registered_sha256"]
        self._refuses("row_binding", rows=rows)

    def test_row_duplicate(self):
        self._refuses("row_duplicate", rows=self.rows + [deepcopy(self.rows[0])])

    def test_row_unstarted(self):
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        rows.append(_add_row(g, reg, roster, _first_nonlive(roster, "not_started")))
        self._refuses("row_unstarted", rows=rows, windows=windows, roster=roster, reg=reg, predictions=p)

    def test_row_missing(self):
        self._refuses("row_missing", rows=self.rows[1:])

    def test_row_tokens_over_cap(self):
        rows = deepcopy(self.rows); rows[0]["generated_tokens"] = 6
        self._refuses("row_tokens_over_cap", rows=rows)

    def test_row_cap_disagreement_both_directions(self):
        rows = deepcopy(self.rows); rows[0]["stop_reason"] = "length"; rows[0]["generated_tokens"] = 4
        self._refuses("row_cap_disagreement", rows=rows)
        rows = deepcopy(self.rows); rows[0]["stop_reason"] = "stop"; rows[0]["generated_tokens"] = 5
        self._refuses("row_cap_disagreement", rows=rows)

    def test_cap_boundary_cap_minus_one_and_cap(self):
        for tokens, reason, capped in ((4, "stop", False), (5, "length", True)):
            rows = deepcopy(self.rows); rows[0]["generated_tokens"] = tokens; rows[0]["stop_reason"] = reason
            candidate = self._accepted(rows)
            item = next(i for i in candidate["items"] if i["item_id"] == rows[0]["item_id"] and i["model"] == "large")
            self.assertIs(item["capped"], capped)

    def test_capped_never_correct(self):
        rows = deepcopy(self.rows); rows[0]["generated_tokens"] = 5; rows[0]["stop_reason"] = "length"
        candidate = self._accepted(rows)
        item = next(i for i in candidate["items"] if i["model"] == "large" and i["item_id"] == rows[0]["item_id"])
        self.assertFalse(item["correct"])

    def test_cap_bound_boundaries_1_5_2_10_3_15_and_null(self):
        for n, count, expected in ((5,1,False),(5,2,True),(10,2,False),(10,3,True),
                                    (15,3,False),(15,4,True)):
            g, reg, roster, p = _night(n=n)
            rows, windows = _inputs(g, reg, roster)
            chosen = [r for r in rows if r["block_id"].startswith("large:") and r["item_id"] in g["item_ids_by_level"]["1"]][:count]
            for row in chosen:
                row["generated_tokens"] = 5; row["stop_reason"] = "length"
            candidate = self._accepted(rows, windows, roster, reg, p)
            self.assertIs(candidate["cells"]["large:1"]["cap_bound"], expected)
        def all_large_terminal(roster, env, block):
            return ("cut_off", .1) if block["model"] == "large" else ("completed", .1)
        g, reg, roster, p = _night(policy=all_large_terminal)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertIsNone(candidate["cells"]["large:1"]["cap_bound"])

    def test_no_cap_literal_and_no_from_import(self):
        tree = ast.parse(inspect.getsource(_reducer()))
        self.assertFalse(any(isinstance(n, ast.Constant) and type(n.value) is float and n.value == .2
                             for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n, ast.ImportFrom) and any(a.name == "CAP_BOUND_FRACTION" for a in n.names)
                             for n in ast.walk(tree)))
        self.assertTrue(any(isinstance(n, ast.Import) and any(a.name == "joulewise.scored_registration" and a.asname == "sr" for a in n.names)
                            for n in ast.walk(tree)))

    def test_codes_disjoint_from_packer_and_registration(self):
        reducer = _reducer()
        other = set()
        for module in (sp, sr):
            tree = ast.parse(inspect.getsource(module))
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_need" and len(n.args) >= 2:
                    if isinstance(n.args[1], ast.Constant) and type(n.args[1].value) is str:
                        other.add(n.args[1].value)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("PackingRefusal", "RegistrationRefusal") and n.args:
                    if isinstance(n.args[0], ast.Constant) and type(n.args[0].value) is str:
                        other.add(n.args[0].value)
        self.assertFalse(set(reducer.REDUCTION_CODES) & other)

    def test_oracle_imports_no_joulewise(self):
        _reducer()
        import tests.scored_reduce_checker as oracle
        tree = ast.parse(inspect.getsource(oracle))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(not a.name.startswith("joulewise") for a in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or "").startswith("joulewise"))

    def test_output_exact_keys_and_sha256(self):
        before = deepcopy((self.roster, self.predictions, self.rows, self.windows))
        candidate = self._accepted()
        self.assertEqual((self.roster, self.predictions, self.rows, self.windows), before)
        self.assertEqual(set(candidate), OUTPUT_KEYS)
        preimage = {k:v for k,v in candidate.items() if k != "sha256"}
        digest = hashlib.sha256(json.dumps(preimage, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        self.assertEqual(candidate["sha256"], digest)

    def test_pilot_max_gap_null(self):
        g, reg, roster, p = _night(mode="pilot")
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertTrue(all(v["max_gap"] is None and not v["drift_exceeded"] for v in candidate["levels"].values()))

    def test_internal_disagreement_exit_injection(self):
        reducer = _reducer()
        original = sp.executed_status
        def flipped(*args, **kwargs):
            value = deepcopy(original(*args, **kwargs))
            key = next(iter(value["spread_exceeded"]))
            value["spread_exceeded"][key] = not value["spread_exceeded"][key]
            return value
        with ExitStack() as stack:
            stack.enter_context(patch.object(sp, "executed_status", flipped))
            if hasattr(reducer, "executed_status"):
                stack.enter_context(patch.object(reducer, "executed_status", flipped))
            with self.assertRaises(reducer.ReductionRefusal) as caught:
                reducer.reduce(self.reg, self.roster, self.predictions, self.rows, self.windows)
        self.assertEqual(caught.exception.code, "internal_disagreement")

    def test_forged_single_prediction_refused_record_code(self):
        reducer = _reducer()
        g, reg, roster, p = _terminal_night(width=2, kind="ceiling_violation")
        forged = deepcopy(roster)
        single = next(b for b in forged["blocks"] if b["parent_block_id"] is not None)
        single["predicted_item_s"][0] += .01
        with self.assertRaises(sp.PackingRefusal) as caught:
            reducer.reduce(reg, forged, p, [], [])
        self.assertIs(type(caught.exception.code), str)
        self.assertTrue(caught.exception.code)

    def test_voided_window_ledgered_not_summed(self):
        g, reg, roster, p = _terminal_night(width=2, kind="ceiling_violation")
        rows, windows = _inputs(g, reg, roster)
        voided = _first_nonlive(roster, "completed")
        windows.append(_add_window(g, reg, roster, voided, gross=997))
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual([x["reason"] for x in candidate["uncounted_windows"] if x["block_id"] == voided["block_id"]], ["voided"])
        self.assertNotIn(997, [x["gross_j"] for x in candidate["counted_windows"]])

    def test_ceiling_terminal_gross_j_on_record_or_null(self):
        g, reg, roster, p = _terminal_night(width=2, kind="ceiling_violation")
        rows, windows = _inputs(g, reg, roster)
        terminal = next(t for t in roster["terminal_refusals"] if t["type"] == "ceiling_violation")
        key = (terminal["block_id"], terminal["attempt"])
        pterm = next(x for x in roster["placements"] if (x["block_id"], x["attempt"]) == key)
        without = self._accepted(rows, windows, roster, reg, p)
        self.assertTrue(all(t["gross_j"] is None for t in without["terminal_refusals"] if (t["block_id"],t["attempt"]) == key))
        windows.append(_add_window(g, reg, roster, pterm, gross=123))
        with_window = self._accepted(rows, windows, roster, reg, p)
        self.assertTrue(all(t["gross_j"] == 123 for t in with_window["terminal_refusals"] if (t["block_id"],t["attempt"]) == key))

    def test_unattributed_multi_item_energy_once_gross_j_null(self):
        g, reg, roster, p = _terminal_night(width=2)
        rows, windows = _inputs(g, reg, roster)
        terminal = next(t for t in roster["terminal_refusals"] if t["type"] == "unattributed_overrun" and len(next(b for b in roster["blocks"] if b["block_id"] == t["block_id"])["items"]) == 2)
        key = (terminal["block_id"], terminal["attempt"])
        placement = next(x for x in roster["placements"] if (x["block_id"],x["attempt"]) == key)
        windows.append(_add_window(g, reg, roster, placement, gross=211))
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual(sum(w["gross_j"] == 211 for w in candidate["uncounted_windows"]), 1)
        records = [x for x in candidate["terminal_refusals"] if (x["block_id"],x["attempt"]) == key]
        self.assertEqual(len(records), 2)
        self.assertTrue(all(x["gross_j"] is None for x in records))

    def test_superseded_rows_checked_and_passed_through(self):
        g, reg, roster, p = _terminal_night(width=2, kind="ceiling_violation")
        rows, windows = _inputs(g, reg, roster)
        voided = _first_nonlive(roster, "completed")
        old = _add_row(g, reg, roster, voided)
        rows.append(old)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertIn(old, candidate["superseded_rows"])
        bad = deepcopy(rows); bad[-1]["roster_sha256"] = "0" * 64
        self._refuses("row_binding", rows=bad, windows=windows, roster=roster, reg=reg, predictions=p)

    def test_attempt_divergence(self):
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            if block["block_id"] == target and block["retry_stage"] == "initial":
                return "cut_off", 1.9
            if block["block_id"] == target and block["retry_stage"] == "whole_block":
                return "cut_off", .1
            if block["parent_block_id"] == target and block["retry_stage"] == "single_problem":
                return "completed", 1.1
            return "completed", .1
        g, reg, roster, p = _night(n=10, width=2, policy=policy)
        rows, windows = _inputs(g, reg, roster)
        voided = _first_nonlive(roster, "completed")
        old = _add_row(g, reg, roster, voided)
        old["scorer_match"] = False
        rows.append(old)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertTrue(any(i["attempt_divergence"] for i in candidate["items"] if i["outcome"] == "counted"))

    def test_whole_block_retry_window_counts_all_items(self):
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            if block["block_id"] == target and block["retry_stage"] == "initial":
                return "cut_off", 1.9
            return "completed", .1
        g, reg, roster, p = _night(n=10, width=2, policy=policy)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        whole = next(x for x in roster["placements"] if x["block_id"] == target and x["stage"] == "whole_block")
        entries = [i for i in candidate["items"] if i["block_id"] == target]
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(i["attempt"] == whole["attempt"] and i["retry_stage"] == "whole_block" for i in entries))
        self.assertEqual(sum(w["block_id"] == target for w in candidate["counted_windows"]), 1)

    def test_block_energy_summed_once_per_window(self):
        g, reg, roster, p = _night(n=10, width=2)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        for cell, value in candidate["cells"].items():
            expected = math.fsum(w["gross_j"] for w in candidate["counted_windows"]
                                 if next(b for b in roster["blocks"] if b["block_id"] == w["block_id"])["model"] == value["model"]
                                 and next(b for b in roster["blocks"] if b["block_id"] == w["block_id"])["level"] == value["level"])
            self.assertEqual(value["gross_j"], expected, cell)

    def test_retry_stage_on_items_and_cells(self):
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            return ("cut_off", 1.9) if block["block_id"] == target and block["retry_stage"] == "initial" else ("completed", .1)
        g, reg, roster, p = _night(n=10, width=2, policy=policy)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual(sum(i["retry_stage"] == "whole_block" for i in candidate["items"]), 2)
        self.assertEqual(candidate["cells"]["large:1"]["retry_stage_counts"].get("whole_block"), 2)

    def test_late_disclosed(self):
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            return ("completed", 1.1) if block["block_id"] == target else ("completed", .1)
        g, reg, roster, p = _night(policy=policy)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertTrue(next(i for i in candidate["items"] if i["block_id"] == target)["late"])

    def test_spread_four_vs_five_parents_by_terminal_degradation(self):
        full = self._accepted()
        self.assertFalse(full["cells"]["large:1"]["spread_exceeded"])
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        self.assertTrue(roster["planned_spread_shortfall"]["large:1"])
        degraded = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual(degraded["cells"]["large:1"]["fully_counted_parents"], 4)
        self.assertTrue(degraded["cells"]["large:1"]["spread_exceeded"])

    def test_spread_four_vs_five_envelopes(self):
        full = self._accepted()
        self.assertEqual(full["cells"]["large:1"]["distinct_envelopes"], 5)
        g, reg, roster, p = _terminal_night()
        rows, windows = _inputs(g, reg, roster)
        degraded = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual(degraded["cells"]["large:1"]["distinct_envelopes"], 4)
        self.assertTrue(degraded["cells"]["large:1"]["spread_exceeded"])

    def test_partial_parent_position_and_null_lever(self):
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            if block["block_id"] == target and block["retry_stage"] == "initial":
                return "cut_off", 1.9
            if block["block_id"] == target and block["retry_stage"] == "whole_block":
                return "cut_off", .1
            if block["parent_block_id"] == target and block["items"][0].endswith("I1"):
                return "cut_off", .1
            return "completed", .1
        g, reg, roster, p = _night(n=10, width=2, policy=policy)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        parent = next(x for x in candidate["parents"] if x["parent_block_id"] == target)
        self.assertEqual(len(parent["counted_item_ids"]), 1)
        self.assertFalse(parent["fully_counted"])
        self.assertIsNotNone(parent["position"])
        def all_large_terminal(roster, env, block):
            return ("cut_off", .1) if block["model"] == "large" else ("completed", .1)
        g, reg, roster, p = _night(policy=all_large_terminal)
        rows, windows = _inputs(g, reg, roster)
        null_case = self._accepted(rows, windows, roster, reg, p)
        self.assertIsNone(null_case["levels"]["1"]["executed_drift_lever_slots"])

    def test_drift_equal_vs_above_max_gap(self):
        baseline = self._accepted()
        lever = baseline["levels"]["1"]["executed_drift_lever_slots"]
        self.assertIsNotNone(lever)
        g, reg, roster, p = _night(budget_j=lever * 5)
        rows, windows = _inputs(g, reg, roster)
        equal = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual(equal["levels"]["1"]["executed_drift_lever_slots"], equal["levels"]["1"]["max_gap"])
        self.assertFalse(equal["levels"]["1"]["drift_exceeded"])
        target = None
        def policy(roster, env, block):
            nonlocal target
            if target is None:
                target = block["block_id"]
            return ("cut_off", 1.1) if block["block_id"] == target and block["retry_stage"] == "initial" else ("completed", .1)
        g, reg, roster, p = _night(policy=policy, budget_j=lever * 5)
        rows, windows = _inputs(g, reg, roster)
        above = self._accepted(rows, windows, roster, reg, p)
        self.assertGreater(above["levels"]["1"]["executed_drift_lever_slots"], above["levels"]["1"]["max_gap"])
        self.assertTrue(above["levels"]["1"]["drift_exceeded"])

    def test_unattributed_count_per_cell_in_items(self):
        g, reg, roster, p = _terminal_night(width=2)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        for cell in candidate["cells"].values():
            count = sum(i["outcome"] == "unattributed_overrun" for i in candidate["items"]
                        if i["model"] == cell["model"] and i["level"] == cell["level"])
            self.assertEqual(cell["uncounted"]["unattributed_overrun"], count)

    def test_cap_bound_k24_pairing_flip_2_10_to_2_9(self):
        g, reg, roster, p = _night(n=10)
        rows, windows = _inputs(g, reg, roster)
        for row in [r for r in rows if r["block_id"].startswith("large:") and r["item_id"] in g["item_ids_by_level"]["1"]][:2]:
            row["generated_tokens"] = 5; row["stop_reason"] = "length"
        baseline = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual((baseline["cells"]["large:1"]["n_capped"], baseline["cells"]["large:1"]["n"]), (2,10))
        self.assertFalse(baseline["cells"]["large:1"]["cap_bound"])
        victim = g["item_ids_by_level"]["1"][-1]
        def policy(roster, env, block):
            return ("cut_off", .1) if block["model"] == "small" and victim in block["items"] else ("completed", .1)
        g, reg, roster, p = _night(n=10, policy=policy)
        rows, windows = _inputs(g, reg, roster)
        for row in [r for r in rows if r["block_id"].startswith("large:") and r["item_id"] in g["item_ids_by_level"]["1"]][:2]:
            row["generated_tokens"] = 5; row["stop_reason"] = "length"
        dropped = self._accepted(rows, windows, roster, reg, p)
        self.assertEqual((dropped["cells"]["large:1"]["n_capped"], dropped["cells"]["large:1"]["n"]), (2,9))
        self.assertTrue(dropped["cells"]["large:1"]["cap_bound"])

    def test_k24_dropped_listed_and_parents_unpaired_ids(self):
        victim = self.g["item_ids_by_level"]["1"][0]
        def policy(roster, env, block):
            return ("cut_off", .1) if block["model"] == "small" and victim in block["items"] else ("completed", .1)
        g, reg, roster, p = _night(policy=policy)
        rows, windows = _inputs(g, reg, roster)
        candidate = self._accepted(rows, windows, roster, reg, p)
        self.assertIn(dict(item_id=victim, partner_outcome="unattributed_overrun"), candidate["cells"]["large:1"]["k24_dropped"])
        self.assertTrue(any(victim in parent["unpaired_item_ids"] for parent in candidate["parents"] if parent["model"] == "large"))

    def test_cap_bound_fraction_consumed_by_patch_on_sr(self):
        g, reg, roster, p = _night(n=10)
        rows, windows = _inputs(g, reg, roster)
        for row in [r for r in rows if r["block_id"].startswith("large:") and r["item_id"] in g["item_ids_by_level"]["1"]][:3]:
            row["generated_tokens"] = 5; row["stop_reason"] = "length"
        self.assertTrue(self._accepted(rows, windows, roster, reg, p)["cells"]["large:1"]["cap_bound"])
        with patch.object(sr, "CAP_BOUND_FRACTION", .30):
            candidate = self._invoke(rows, windows, roster, reg, p)
        self.assertFalse(candidate["cells"]["large:1"]["cap_bound"])

    def test_every_a291_provisional_R_witness_at_real_reduce(self):
        reducer = _reducer()
        # Each mutation is a violating A291 §5.3 row presented at the real R
        # entry.  Resealing preserves the input digest so the seal can reach
        # the invariant itself; replay then guards against a forged history.
        mutations = {
            "INV-01": lambda r: r.update(registration_sha256="0" * 64),
            "INV-02": lambda r: r.update(sha256="0" * 64),
            "INV-03": lambda r: r.update(models=[]),
            "INV-04": lambda r: r.update(n_per_level=6),
            "INV-05": lambda r: r.update(claim_ready=False),
            "INV-07": lambda r: r["blocks"][0]["predicted_item_s"].__setitem__(0, 31.0),
            "INV-08": lambda r: r["blocks"][0]["predicted_item_s"].__setitem__(0, .8),
            "INV-10": lambda r: r["blocks"][0].update(block_id="foreign"),
            "INV-11": lambda r: r["envelopes"][0]["blocks"].clear(),
            "INV-12": lambda r: r["blocks"][0].update(superseded=True),
            "INV-14": lambda r: r["envelopes"][0].update(model="small"),
            "INV-15": lambda r: r["envelopes"][0]["blocks"].clear(),
            "INV-16": lambda r: r["envelopes"][-1].update(observations=[]),
            "INV-17": lambda r: r["envelopes"][0].update(index=1),
            "INV-18": lambda r: r["events"][0]["placements"].append(0),
            "INV-20": lambda r: r["placements"][0].update(reserved_s=101.0),
            "INV-21": lambda r: r["placements"][0].update(reserved_s=5.0),
            "INV-24": lambda r: (r["envelopes"][0]["blocks"].append(r["envelopes"][2]["blocks"].pop(0)),
                                next(p for p in r["placements"] if p["block_id"] == "large:decode:1:1").update(envelope_index=0)),
            "INV-27": lambda r: r["drift_lever_slots"].__setitem__("1", 999.0),
            "INV-29": lambda r: r["events"][0]["block_ids"].clear(),
            "INV-30": lambda r: r["events"][0]["observations"][0].update(decision="advance"),
            "INV-35": lambda r: r["events"][0]["observations"][0].update(decision="reschedule"),
            "INV-36": lambda r: r["placements"][0].update(attempt=99),
            "INV-37": lambda r: r["terminal_refusals"].append(dict(
                type="ceiling_violation", block_id=r["blocks"][0]["block_id"], attempt=0,
                parent_block_id=None, item_id=r["blocks"][0]["items"][0], model="large", level=1)),
            "INV-38": lambda r: r["events"][0].update(sha256="f" * 64),
            "INV-41": lambda r: r["envelopes"][-1].update(kind="loaded"),
            "INV-47": lambda r: r["events"][0]["observations"][0].update(status="not_started", elapsed_s=None),
            "INV-48": lambda r: r["events"][0]["observations"][0].update(elapsed_s=101.0),
            "INV-49": lambda r: r["planned_spread_shortfall"].__setitem__("large:1", True),
            "INV-50": lambda r: r["blocks"].__setitem__(slice(0, 6, 5), [r["blocks"][5], r["blocks"][0]]),
            "INV-52": lambda r: r["blocks"][0].update(late=1),
        }
        for row, mutate in mutations.items():
            with self.subTest(row=row):
                roster = deepcopy(self.roster)
                mutate(roster)
                if row not in {"INV-01", "INV-02", "INV-03", "INV-04", "INV-05", "INV-38"}:
                    roster["sha256"] = digest(roster)
                    roster["events"][-1]["sha256"] = roster["sha256"]
                self.assertIn(row, {v.inv_id for v in check_roster(self.g, roster, self.predictions)})
                with self.assertRaises(sp.PackingRefusal) as caught:
                    reducer.reduce(self.reg, roster, self.predictions, [], [])
                self.assertIsInstance(caught.exception.code, str)
        g_retry, reg_retry, retry, p_retry = _terminal_night(width=2, kind="ceiling_violation")
        retry_mutations = {
            "INV-19": lambda r: next(p for p in r["placements"] if p["stage"] == "single_problem").update(
                envelope_index=next(e["envelope_index"] for e in r["events"] if any(o["decision"] == "split" for o in e["observations"]))),
            "INV-22": lambda r: next(p for p in r["placements"] if p["stage"] == "whole_block").update(reserved_s=29.0),
            "INV-23": lambda r: r["blocks"][-1].update(predicted_s=29.0),
            "INV-34": lambda r: r["placements"][-1].update(envelope_index=21),
            "INV-32": lambda r: next(o for e in r["events"] for o in e["observations"] if o["decision"] == "split").update(decision="keep"),
            "INV-33/43": lambda r: next(b for b in r["blocks"] if b["retry_stage"] == "ceiling_violation").update(late=False),
        }
        for row, mutate in retry_mutations.items():
            with self.subTest(row=row):
                roster = deepcopy(retry)
                mutate(roster)
                roster["sha256"] = digest(roster)
                roster["events"][-1]["sha256"] = roster["sha256"]
                self.assertIn(row, {v.inv_id for v in check_roster(g_retry, roster, p_retry)})
                with self.assertRaises(sp.PackingRefusal) as caught:
                    reducer.reduce(reg_retry, roster, p_retry, [], [])
                self.assertIsInstance(caught.exception.code, str)
        def initial_culprit(roster, env, block):
            return (("cut_off", 1.1) if block["block_id"] == "large:decode:1:0"
                    and block["retry_stage"] == "initial" else ("completed", .1))
        g_res, reg_res, rescheduled, p_res = _night(policy=initial_culprit)
        wrong_reschedule = deepcopy(rescheduled)
        next(p for p in wrong_reschedule["placements"] if p["stage"] == "initial" and p["attempt"] > 0)["envelope_index"] = 2
        wrong_reschedule["sha256"] = digest(wrong_reschedule)
        wrong_reschedule["events"][-1]["sha256"] = wrong_reschedule["sha256"]
        self.assertIn("INV-31", {v.inv_id for v in check_roster(g_res, wrong_reschedule, p_res)})
        with self.subTest(row="INV-31"), self.assertRaises(sp.PackingRefusal):
            reducer.reduce(reg_res, wrong_reschedule, p_res, [], [])
        with self.subTest(row="INV-51"), self.assertRaises(sp.PackingRefusal) as caught:
            reducer.reduce(None, self.roster, self.predictions, [], [])
        self.assertEqual(caught.exception.code, "inv_51")
        gp, regp, rp, pp = _night(mode="pilot")
        wrong = deepcopy(pp); wrong["large"][gp["item_ids_by_level"]["1"][0]] = .8
        for row, reg, roster, predictions, code in (
            ("INV-39", regp, rp, wrong, "inv_39"),
            ("INV-46", self.reg, sp.pack(self.reg, self.predictions), self.predictions, "unreported_envelope"),
        ):
            with self.subTest(row=row):
                with self.assertRaises(sp.PackingRefusal) as caught:
                    reducer.reduce(reg, roster, predictions, [], [])
                self.assertEqual(caught.exception.code, code)

    def test_differential_oracle_200_nights(self):
        reducer = _reducer()
        nights = 0
        for seed in (17, 29, 43, 71):
            for index in range(50):
                case = generate_case(seed, index)
                g, reg, roster, p = case.g, case.reg, case.rosters[-1], case.p
                sp.verify_executed_roster(reg, roster, p)
                rows, windows = _inputs(g, reg, roster, optional=True, seed=seed * 1000 + index)
                with self.subTest(seed=seed, index=index, variant="A"):
                    candidate = reducer.reduce(reg, roster, p, rows, windows)
                    self.assertEqual(check_reduction(g, roster, p, rows, windows, candidate), [])
                live = [w for w in windows if w["block_id"] in roster["envelopes"][w["envelope_index"]]["blocks"]]
                self.assertTrue(live)
                dropped = next(w for w in windows if w is live[(seed + index) % len(live)])
                variant_b = [w for w in windows if w is not dropped]
                with self.subTest(seed=seed, index=index, variant="B"):
                    with self.assertRaises(reducer.ReductionRefusal) as caught:
                        reducer.reduce(reg, roster, p, rows, variant_b)
                    self.assertEqual(caught.exception.code, "missing_live_window")
                    self.assertEqual(check_reduction(g, roster, p, rows, variant_b,
                                      {"refusal_code": caught.exception.code, "detail": caught.exception.detail}), [])
                nights += 1
        self.assertGreaterEqual(nights, 200)
