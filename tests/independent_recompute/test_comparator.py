"""RC-CMP-1 A1-A4: the recompute-versus-L9 comparator on small synthetic custody.

Each planted fault moves one value by twice its family bar (or changes one word),
and each test also shows the fault passing once the check that catches it is
disabled (counterfactual). Synthetic values only. RC-CMP-10: the words a producer prints that the base needs
(the p42 refusal code, the resolution's transport rule, the history lines) come from the producers themselves
(producer_fixtures, detection_floor); the comparator still imports no repository code.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest import mock

from joulewise.detection_floor import TRANSPORT_RULE_ID

from . import producer_fixtures

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("compare_b5_recompute_test_subject", ROOT / "scripts/compare_b5_recompute.py")
cmp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmp)
BARS = {name: ROOT / "tests/independent_recompute/bar_sets" / (name + ".json")
        for name in ("recompute_coded_7e322b76", "s13_block6")}
DECODE, PREFILL = "ctr-d117-decode-qwen3-1p7b-vs-qwen3-8b", "ctr-d117-prefill-p2048-qwen3-1p7b-vs-qwen3-8b"
SHA = "0" * 64
# FS4 (RC-CMP-10): the synthetic window index the fixture's L9 run read (the record carries its digest); the
# comparator's default --window-index is pointed at it, as the lead passes the full-size window's own index.
WINDOW_INDEX = ROOT / "tests/independent_recompute/window_index/synthetic.json"
cmp.WINDOW_INDEX = WINDOW_INDEX
INDEX_ATTEMPTS = json.loads(WINDOW_INDEX.read_text())["attempts"]
# The finalized manifest step 8 writes and the fill names (FABLE F4, RC-CMP-10): its lineage names the sealed manifest.
FINALIZED = "finalized/am-synthetic.finalized.json"


ALPHA_CELLS = {"absolute": "d117-df-ph-decode-qwen3-1p7b-absolute", "comparative": "d117-df-cmp-abba-ph-decode-qwen3-1p7b"}
# The aggregate floor cells of each contrast's arms A and B (the consumer declaration's registered ids).
FLOOR_CELLS = {DECODE: ("d117-qwen3-1p7b-decode-floor-v5", "d117-qwen3-8b-decode-floor-v5"),
               PREFILL: ("d117-qwen3-1p7b-prefill-p2048-floor-v5", "d117-qwen3-8b-prefill-p2048-floor-v5")}
CONDITIONS = {DECODE: ("sw-decode-a-qwen3-1p7b", "sw-decode-b-qwen3-8b"),
              PREFILL: ("sw-prefill-p2048-a-qwen3-1p7b", "sw-prefill-p2048-b-qwen3-8b")}


def extraction_cell_id(model, kind):
    """The registered spelling (extraction_spec.json): d117-df-ph-...-absolute, d117-df-cmp-abba-ph-..."""
    return f"d117-df-ph-decode-{model}-absolute" if kind == "absolute" else f"d117-df-cmp-abba-ph-decode-{model}"


# The registered block ids of each contrast (analysis_manifest_v3 contrasts[*].block_ids): the fixture keeps blocks
# 2-10 and leaves block 1 out, so each contrast's kept n is 9.
BLOCKS = {DECODE: tuple(f"d117-decode-contrast-b{i:02d}" for i in range(1, 11)),
          PREFILL: tuple(f"d117-prefill-p2048-contrast-b{i:02d}" for i in range(1, 11))}
KEPT = {cid: blocks[1:] for cid, blocks in BLOCKS.items()}
# Each arm's registered transport group (the manifest's floor_dependency.transport.transport_groups).
TRANSPORT_GROUPS = {DECODE: ("tg-d117-qwen3-1p7b-decode-v5", "tg-d117-qwen3-8b-decode-v5"),
                    PREFILL: ("tg-d117-qwen3-1p7b-prefill-p2048-v5", "tg-d117-qwen3-8b-prefill-p2048-v5")}
PACK_MODELS = {"alpha": ("qwen3-1p7b", "Qwen3-1.7B-4bit"), "beta": ("qwen3-8b", "Qwen3-8B-4bit")}


def loo_row(cid, block, p):
    """One engine leave-one-out row (analysis_engine _LOO_ROW_KEYS): the block left out moves nothing."""
    return {"omitted_block_id": block, "n_blocks": 8, "df": 7, "estimate": -1.25,
            "metrology_aware_ci95": {"lower": -14.0, "upper": 11.5}, "decision_interval": {"lower": -16.75, "upper": 14.25},
            "floor_status": "not_above_floor", "raw_p": p, "adjusted_p": 1.0, "outcome": "not_resolvable",
            "influence_triggers": []}


def recompute_loo_row(cid, block, p):
    """The recompute's row for the same block (finish_contrast: block_number is the block's registered position)."""
    return {"block_number": BLOCKS[cid].index(block) + 1, "dbar_j": -1.25, "p": p, "holm_p": 1.0, "holm_reject": False,
            "outcome": "not_resolvable", "metrology_interval_j": [-14.0, 11.5], "decision_interval_j": [-16.75, 14.25],
            "n": 8, "above_floor": False}


def verdict_row(cid, p):
    """A claim-verdict contrast in the producer's key set (analysis_engine _CONTRAST_KEYS, v3 floor)."""
    a, b = CONDITIONS[cid]
    phase = "decode" if cid == DECODE else "prefill"
    resolutions = [{"status": "exact", "source_cell_ids": [cell], "transport_group_id": group,
                    "transport_rule_id": TRANSPORT_RULE_ID, "floor_abs_j": 43.0, "floor_cmp_j": 103.5,
                    "floor_gate_j": 103.5, "reason_codes": []} for group, cell in zip(TRANSPORT_GROUPS[cid], FLOOR_CELLS[cid])]
    blocks = BLOCKS[cid]
    return {"contrast_id": cid, "plan_id": "plan-gamma", "family_instance_id": "fam-gamma-primary", "claim_role": "primary",
            "metric": {"name": f"phase_energy_j.{phase}", "metric_tag": "phase_decode_energy" if cid == DECODE
                       else "phase_prefill_p2048_energy", "window_class": "phase",
                       "unit": "J", "ratio_estimand": None},
            "conditions": {"condition_a_id": a, "condition_b_id": b, "cell_a_id": "cell-" + a, "cell_b_id": "cell-" + b,
                           "difference_orientation": "condition_b_minus_condition_a"},
            "hypothesized_direction": "positive", "equivalence": None, "mde": None,
            "bundle_blocks": {"planned_block_ids": list(blocks),
                              "included_bundle_ids": [f"q{i:02d}-{arm}" for i in range(2, 11) for arm in ("a1", "b1")],
                              "blocks": [{"block_id": bid, "bundle_a_id": f"q{i + 1:02d}-a1", "bundle_b_id": f"q{i + 1:02d}-b1",
                                          "included": bid in KEPT[cid],
                                          "reason_codes": [] if bid in KEPT[cid] else ["block_excluded"]}
                                         for i, bid in enumerate(blocks)]},
            "sampling": {"confirmatory_status": "confirmatory", "planned_n": 10, "observed_complete_n": 9,
                         "kept_n": 9, "removed_block_ids": [blocks[0]]},
            "estimator": {"name": "abba_block_arm_mean_difference_t_v1", "n": 9, "df": 8, "estimate": -1.25, "s_d": 16.0,
                          "SE_repeat": 5.0, "SE_metrology": 1.5, "SE_total": 5.25, "t_critical_95": 2.306,
                          "repeat_point_CI95": {"lower": -12.75, "upper": 10.25},
                          "metrology_aware_CI95": {"lower": -13.5, "upper": 11.0},
                          "variance_contributions": [{"name": "repeat", "summed_paired_variance": 2304.0,
                                                      "squared_standard_error": 25.0}],
                          "excluded_stochastic_terms": [], "raw_p": p},
            "deterministic_bounds": {"terms": [{"name": "edge", "bound": 2.75}], "total": 2.75,
                                     "decision_interval": {"lower": -16.25, "upper": 13.75}},
            "floor": {"status": "exact", "floor_row_ids": list(FLOOR_CELLS[cid]), "floor_abs_j": 43.0, "floor_cmp_j": 103.5,
                      "active_floor_j": 103.5, "transport_verdict": "exact_stack_only", "resolutions": resolutions,
                      "claim_floor_rule": "cross_stack_armwise_max.v1", "aggregation": "max_never_sum",
                      "arm_gates": [{"arm_id": arm, "condition_family_id": condition, "status": "exact", "floor_gate_j": 103.5}
                                    for arm, condition in zip("AB", CONDITIONS[cid])]},
            "multiplicity": {"raw_p": p, "adjusted_p": 1.0, "rejected": False},
            "randomization_check": {"status": "not_run", "reason": "fixture", "n_blocks": 9, "exact_two_sided_p": None,
                                    "rejects": None},
            # RC-CMP-9: block 5's kept quads make the contrast complete, so the engine prints a row per kept block.
            "loo": {"status": "complete", "rows": [loo_row(cid, block, p) for block in KEPT[cid]]},
            "sensitivity_status": "not_run",
            "claim_evaluation": {"outcome": "not_resolvable", "direction": None, "reason_codes": ["floor_not_cleared"],
                                 "claim_ready_for_l2_l3": False, "claim_level_ceiling": "L1"}}


def fill_row(row):
    """results_fill_adapter.adapt_claim_verdicts' row for one verdict contrast (extended: all 24 keys)."""
    estimator = row["estimator"]
    included = {b["block_id"] for b in row["bundle_blocks"]["blocks"] if b["included"] is True}
    planned = row["bundle_blocks"]["planned_block_ids"]
    return copy.deepcopy({
        "contrast_id": row["contrast_id"], "metric": row["metric"], "conditions": row["conditions"],
        "limitations": ["synthetic limitation note"], "floor_source_cell_ids": row["floor"]["floor_row_ids"],
        "estimate": estimator["estimate"], "interval": estimator["metrology_aware_CI95"],
        "decision_interval": row["deterministic_bounds"]["decision_interval"],
        "deterministic_widening_total": row["deterministic_bounds"]["total"],
        "j_per_token": estimator["estimate"] if row["metric"]["unit"] == "J/token" else None,
        "n": estimator["n"], "floor": row["floor"], "multiplicity": row["multiplicity"],
        "claim_evaluation": row["claim_evaluation"],
        **{key: row[key] for key in ("plan_id", "claim_role", "hypothesized_direction", "equivalence", "sampling", "loo")},
        **{key: estimator[key] for key in ("df", "t_critical_95")},
        "kept_block_ids": [bid for bid in planned if bid in included],
        "removed_block_ids": [bid for bid in planned if bid not in included]})


def item(line, restricted, text, **values):
    """disclosures._item: every disclosure line carries line, restricted, label and text."""
    return {"line": line, "restricted": restricted, "label": line, "text": text, **values}


def kept_units_record(pack, runs, cell_id=None):
    """kept_units.KeptUnits.to_record: the kept and dropped units of each cell, by run id."""
    cell_id = cell_id or ALPHA_CELLS["absolute"]
    units = [{"cell_id": cell_id, "stratum": "repeat", "unit_id": f"{cell_id}-r{i + 1:02d}", "run_ids": [run],
              "positions": [i + 1], "stage_ids": ["01_phase_decode_absolute"]} for i, run in enumerate(runs)]
    cells = {cell_id: {"target": True, "planned": {"repeat": len(runs)}, "minimum": {"repeat": 0}, "n_r": len(runs),
                       "n_b": 0, "kept": {"repeat": units}, "dropped": []}} if runs else {}
    return {"schema_version": "joulewise.b5_kept_units.v1", "pack": pack, "plan_id": "plan-" + pack, "attempt": 1,
            "harvest_pin": "a1b2c3d" + pack, "exclusions_sha256": "e" * 64, "roster_sha256": "d" * 64,
            "catalog_sha256": "c" * 64, "sensitivity_label": None, "cells": cells}


NEG8_BASE = "bracket.claim_families.gross_energy."
NEG8_VALUES = {"bound_envelope_j": 2.0, "bound_prediction_j": 1.5, "start.mean_j": 10.0, "midpoint.mean_j": 10.5,
               "end.mean_j": 11.0, "trajectory_excursion_max_j": 1.0, "drift_allowance_j": 1.0}
NEG8_WORDS = ("neg8_screen", "neg8_allowance", "reference_counts", "corpus_counts")


def neg8_lines(pack, start=2, deciding=12):
    """disclosures._reference_lines: every window's NEG-8 screen and reference lines (RC-CMP-8 F3: the producer
    prints them for each registered window, so the base fixture carries them)."""
    return [item("neg8_screen", True, f"{pack}: NEG-8 screen passed", decision="passed"),
            item("neg8_allowance", True, f"{pack}: NEG-8 allowance", source="survivor_rescreen",
                 values_j={NEG8_BASE + k: v for k, v in NEG8_VALUES.items()}),
            item("reference_counts", False, f"{pack}: reference counts", counts={"start": start, "midpoint": 1, "end": 3},
                 planned={"start": 3, "midpoint": 1, "end": 3}),
            item("corpus_counts", False, f"{pack}: corpus counts", collected=12, in_window=12, deciding=deciding,
                 desk_cap=[], drop_counts={"status": 0, "desk_cap": 0})]


def neg8_recompute():
    """The recompute's NEG-8 terms of a window (windows.<PACK>.neg8), matching neg8_lines."""
    return {"source": "survivor_rescreen", "screen_decision": "passed", "bound_envelope_j": 2.0,
            "bound_prediction_j": 1.5, "start_mean_j": 10.0, "midpoint_j": 10.5, "end_mean_j": 11.0, "spread_j": 1.0,
            "allowance_j": 1.0, "n_start": 2, "n_mid": 1, "n_end": 3, "corpus_n": 12}


def structure_lines(pack):
    """RC-CMP-9: the window lines the producer prints for every registered window whatever its data, beyond the
    NEG-8 and screen lines (disclosures._monitor_lines, _reference_lines, _structure_lines, _ruling_lines,
    _machine_lines); none of their values is compared."""
    return [item("monitor_cost", False, f"{pack}: monitor cost", cpu_s=1.5, reader_cpu_s=None, probes_inside_target_phases=0),
            item("monitor_sentence", False, "The hazard monitor ran on efficiency cores."),
            item("physics_counts", False, f"{pack}: physics-in-span counts: ", counts={}),
            item("anchor_counts", False, f"{pack}: members with anchor status bounded: 9", count=9),
            item("anchor_bound", True, f"{pack}: largest effective anchor bound", value_s=0.001),
            item("host_cpu", False, f"{pack}: host's total busy CPU during requests: not recorded", value_s=None),
            item("battery_counts", False, f"{pack}: battery observations", counts=dict.fromkeys(cmp.BATTERY_CODES, 0)),
            item("bound_formula", False, f"{pack}: bound formula", formula="max(envelope, prediction)"),
            item("erratum3_triggers", False, f"{pack}: triggers", values={"observed_triggers": [], "recorded_only_triggers": [],
                                                                       "doubling_count": 0, "systematic_sequences": []}),
            item("adapter_continuity", False, f"{pack}: adapter-continuity decision: stable", decision="stable"),
            item("stored_verdict_boundary", False, "The stored verdict's status and NEG-8 bracket decided nothing."),
            item("tripwire", False, f"{pack}: tripwire excluded_reference_in_screen: passed",
                 tripwire="excluded_reference_in_screen", result="passed"),
            item("tripwire", False, f"{pack}: tripwire kept_member_outside_verdict_membership: passed",
                 tripwire="kept_member_outside_verdict_membership", result="passed"),
            item("deciding_membership", False, f"{pack}: deciding screen", writer_excluded_by_family={},
                 writer_excluded_all_removed=True, deciding_references=7, deciding_spares=0, writer_excluded_count=0),
            item("reference_parity", False, f"{pack}: reference parity: passed", result="passed", harvest_pin="a1b2c3d" + pack),
            item("ledger_binding", False, f"{pack}: SHA256SUMS digest", sha256sums_sha256="5" * 64,
                 ledger_copy_sha256="6" * 64, terminal_sequence=424, prefix_result="passed"),
            item("machine_absent", False, "whole-machine meter: absent"),
            item("machine_boundary", False, "whole-machine DC input plus the battery term")]


# The reported cells of each floor window (extraction_spec reported_energy_cells): each phase's id and the
# recompute's cell id (the condition family of its extraction cells); p42 is the registered refused exit.
def reported_cells(pack):
    short = PACK_MODELS[pack][0]
    return {phase: (f"d117-reported-mean-ph-{phase}-{short}", f"df-ph-{phase}-{short}")
            for phase in ("decode", "prefill-p2048", "prefill-p42")}


def extraction_cells(pack):
    """Each floor window's registered extraction cells, in the fixture's order (decode, p42 absolute first)."""
    short = PACK_MODELS[pack][0]
    return [(f"d117-df-ph-decode-{short}-absolute", "decode", "absolute"),
            (f"d117-df-cmp-abba-ph-decode-{short}", "decode", "comparative"),
            (f"d117-df-ph-prefill-p42-{short}-absolute", "p42", "absolute"),
            (f"d117-df-ph-prefill-p2048-{short}-absolute", "prefill", "absolute"),
            (f"d117-df-cmp-abba-ph-prefill-p2048-{short}", "prefill", "comparative"),
            (f"d117-df-cmp-abba-ph-prefill-p42-{short}", "p42", "comparative")]


REPORTED_PROJECTION = {"mean_j": 50.0, "lower_j": 47.0, "upper_j": 53.0,
                       "interval": {"h_j": 2.0, "B_j": 1.0, "s_r": 1.5, "s_b": 1.25, "variance": 0.5, "n_r": 9, "n_b": 9,
                                    "df": 8, "kind_averages_j": dict.fromkeys(cmp.KIND_ORDER, 0.25)},
                       "attribution_floor": {"value_j": 3.0, "minimum_j": 1.0, "attained_by": "E_clock_anchor_shift_bound_j"},
                       "per_token": {"j_per_token": 0.1}, "n_bundles": 18, "kept_units": [{"stratum": "repeat", "unit_id": "u1"}]}
REPORTED_RECOMPUTE = {"status": "computed", "mean_j": 50.0, "lower_j": 47.0, "upper_j": 53.0, "n_r": 9, "n_b": 9,
                      "n_bundles": 18, "interval": {"h_j": 2.0, "B_j": 1.0, "s_r": 1.5, "s_b": 1.25, "variance": 0.5, "df": 8,
                                                    "kind_averages_j": [0.25] * 3},
                      "attribution_floor": {"value_j": 3.0, "minimum_j": 1.0}, "per_token": {"j_per_token": 0.1},
                      "kept_units": {"repeat": ["u1"]}}
CELL_VALUES = {"status": "computed", "mean_j": 50.0, "h_j": 2.0, "B_j": 1.0, "lower_j": 47.0, "upper_j": 53.0}
REPORTED_VALUES = {"mean_j": 50.0, "h_j": 2.0, "B_j": 1.0, "lower_j": 47.0, "upper_j": 53.0, "attribution_floor_j": 3.0}
CROSS_WINDOW = {"G_j": 50.5, "h_G_j": 3.0, "F_j": 50.0, "h_F_j": 2.0, "delta_j": 0.5, "agree": True}
FLOOR_VALUES = {"floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}
CONTRAST_VALUES = dict(FLOOR_VALUES, D_j=2.75, outcome="not_resolvable")
AGGREGATE_CELLS = [f"d117-{model}-{phase}-floor-v5" for model in ("qwen3-1p7b", "qwen3-8b") for phase in ("decode", "prefill-p2048")]


def aggregate_key(cid):
    model = "Qwen3-1.7B-4bit" if "-qwen3-1p7b-" in cid else "Qwen3-8B-4bit"
    return model + ("/decode" if "-decode-" in cid else "/prefill")


def sensitivity_rows():
    """sensitivity.build: every registered reported cell (p42 refused), every aggregate floor cell, every contrast;
    the base's sensitivity values equal its primary values."""
    reported = []
    for pack in ("alpha", "beta"):
        for phase, (cid, _) in reported_cells(pack).items():
            if phase == "prefill-p42":
                reported.append({"pack": pack, "cell_id": cid, "status": "refused",
                                 "code": producer_fixtures.p42_refusal_code()})
            else:
                reported.append({"pack": pack, "cell_id": cid, "status": "computed", "primary": dict(REPORTED_VALUES),
                                 "sensitivity": dict(REPORTED_VALUES), "mean_and_half_width_equal_primary": True,
                                 "equals_primary": True, "not_below_primary": True})
    floors = [{"pack": "alpha" if "-qwen3-1p7b-" in cid else "beta", "cell_id": cid,
               "primary": dict(FLOOR_VALUES, allowance_j=1.0), "sensitivity": dict(FLOOR_VALUES, allowance_j=1.0),
               "equals_primary": True, "not_below_primary": True} for cid in AGGREGATE_CELLS]
    contrasts = [{"contrast_id": cid, "floor_cell_ids": list(FLOOR_CELLS[cid]), "primary": dict(CONTRAST_VALUES),
                  "sensitivity": dict(CONTRAST_VALUES, D_j=3.0), "bound_independent_values_equal_primary": True,
                  "outcome_equals_primary": True, "not_below_primary": True} for cid in (DECODE, PREFILL)]
    return reported, floors, contrasts


def ratio_rows():
    """D-165's ratio table: each aggregate floor cell's absolute and comparative ratio and its common-mode ratio."""
    rows = []
    for cid in AGGREGATE_CELLS:
        for component, field in (("absolute", "corner_widened_unguarded_floor_j"),
                                 ("comparative", "corner_widened_unguarded_floor_j"),
                                 ("comparative", "common_mode_corner_widened_unguarded_floor_j")):
            rows.append({"cell_id": cid, "component": component, "numerator_field": field, "numerator_j": 39.5,
                         "denominator_j": 38.0, "n": 9, "ratio": 39.5 / 38.0, "status": "complete"})
    return rows


def l9_files():
    """L9 restricted outputs in the producers' shapes (RC-CMP-6 G4), with the registered ids.

    RC-CMP-9: producer-complete over the registry: every registered reported cell (p42 refused), extraction cell,
    aggregate floor cell, ratio, contrast and kept block (leave-one-out row), and every line the producer prints
    unconditionally, so the registry-driven expected-check table finds each of its items on both sides.
    """
    files = {"rereduced/alpha/run-a.rereduced.json": {"phase_energy_j": {"prefill": 2.5, "decode": 97.25},
                                                       "gross_energy_j": 120.0}}
    for pack in ("alpha", "beta"):
        cells = []
        for cid, phase, kind in extraction_cells(pack):
            if phase == "p42":
                cells.append({"cell_id": cid, "kind": kind, "extractable": False})
                continue
            cells.append({"cell_id": cid, "kind": kind, "extractable": True,
                          "operative_floor_j": 43.0, "n_admitted": 9,
                          "floor": {"corner_widened_unguarded_floor_j": 39.5, "unguarded_floor_j": 39.5,
                                    "guarded_floor_j": 42.0, "drift_widened_guarded_floor_j": 43.0,
                                    "prediction_component_j": 38.0, "max_abs_deviation_j": 29.5,
                                    "sample_stddev_j": 15.5, "whole_window_drift_allowance_j": 1.0,
                                    "guard_factor": 1.0, "corner_widened_guarded_floor_j": 39.5,
                                    "drift_widened_unguarded_floor_j": 40.5, "n": 9}})
        files[f"mint/{SHA}-extraction-{pack}.json"] = {"cells": cells}
        files[f"brackets/{SHA}-{pack}.json"] = {"b_sens": 0.0625, "evaluation": {"acceptance": {"allowance": {
            "operative_b_fiducial_binary64_s": 0.0375}}}}
    files[f"brackets/{SHA}-gamma.json"] = copy.deepcopy(files[f"brackets/{SHA}-alpha.json"])
    # L9's step-2 selection (RC-CMP-7 G7): each window's kept-units record (kept_units.KeptUnits.to_record).
    for pack in ("alpha", "beta", "gamma"):
        files[f"kept-units/{SHA}-{pack}.json"] = kept_units_record(pack, ["run-a"] if pack == "alpha" else [])
    files[f"brackets/{SHA}-block.json"] = {"T": 424, "attained_by_sequence": 396, "value_s": 0.0625}
    files[f"mint/{SHA}-aggregate-floor.json"] = {"cells": [
        {"cell_id": f"d117-{model}-{phase}-floor-v5", "floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}
        for model in ("qwen3-1p7b", "qwen3-8b") for phase in ("decode", "prefill-p2048")]}
    files["finalized/outputs/closeout.json"] = {"branch": "B", "dominance_sentence_licensed": False}
    files["finalized/outputs/closeout.ratio-table.json"] = {"ratios": ratio_rows()}
    rows = [verdict_row(DECODE, 0.84), verdict_row(PREFILL, 0.68)]
    files[f"outputs/{SHA}-claim-verdicts.json"] = {"contrasts": rows}
    files[FINALIZED] = {"schema_version": "joulewise.analysis_manifest.v3.finalized", "manifest_id": "am-synthetic",
                        "freeze_status": "finalized",
                        "lineage": {"prospective_manifest_sha256": cmp.REGISTRY_PINS[cmp.MANIFEST]}}
    windows = {p: {"plan_id": "plan-" + p, "attempt": 1, "harvest_pin": "a1b2c3d" + p, "record_shape": "second_seal"}
               for p in ("alpha", "beta", "gamma")}
    files[f"outputs/{SHA}-results-fill-input.json"] = {
        "schema_version": "joulewise.results_fill_input.v1",
        "campaigns": {p: {"plan_id": "plan-" + p, "attempt": 1, "claim_usable": True, "exclusions_sha256": "e" * 64,
                          "harvest_record_sha256": "f" * 64} for p in ("alpha", "beta")},
        "gamma": {"claim_verdicts_id": "cv-synthetic", "claim_verdicts_sha256": "c" * 64, "evidence_class": "synthetic",
                  "limitations": ["synthetic limitation note"], "contrasts": [fill_row(row) for row in rows],
                  "finalized_manifest": {"manifest_id": "am-synthetic", "file_sha256": hashlib.sha256(written(
                      FINALIZED, files[FINALIZED])).hexdigest()},
                  "floor_artifact": {"artifact_id": "floor-synthetic", "file_sha256": "b" * 64}, "exclusions_sha256": "e" * 64},
        "characterization": {"funded": False, "run": False, "verdict": None}}
    cells_lines, kept_cells = [], []
    for pack in ("alpha", "beta"):
        computed, refused = [], []
        for phase, (cid, _) in reported_cells(pack).items():
            if phase == "prefill-p42":
                refused.append({"cell_id": cid, "code": producer_fixtures.p42_refusal_code()})
                continue
            computed.append(dict(copy.deepcopy(REPORTED_PROJECTION), cell_id=cid))
            cells_lines += [
                item("reported_cell", True, f"{pack} {cid}: 50 J", pack=pack, cell_id=cid, **CELL_VALUES),
                item("battery_assist_cell", True, f"{pack} {cid}: no assisted member", pack=pack, cell_id=cid,
                     primary=dict(CELL_VALUES), without=dict(CELL_VALUES), n_r=9, n_b=9, assist_members={},
                     removed_unit_ids=[]),
                item("attribution_floor", True, "attribution floor 3 J", pack=pack, cell_id=cid, value_j=3.0,
                     attained_by="E_clock_anchor_shift_bound_j", minimum_j=1.0),
                item("cross_window", True, "GAMMA's and the floor window's estimates agree", pack=pack, cell_id=cid,
                     **CROSS_WINDOW)]
            kept_cells.append(item("kept_units", False, f"{pack} {cid}: kept units", pack=pack, cell_id=cid, n_r=9, n_b=9))
        files[f"outputs/{SHA}-projection-{pack}.json"] = {"cells": computed, "refused_cells": refused}
    reported, floor_rows, contrast_rows = sensitivity_rows()
    sensitivity = {
        "schema_version": "joulewise.b5_bracket_sensitivity.v1",
        "label": "sensitivity", "b_max": {"value_s": 0.0625, "T": 424, "attained_by_sequence": 396},
        "windows": {p: {"plan_id": "plan-" + p, "b_op_s": 0.0375, "b_sens_s": 0.0625, "widened": True}
                    for p in ("alpha", "beta", "gamma")},
        # The registered p42 exit: L9's sensitivity record lists each p42 cell as refused (RC-CMP-5 S3 union).
        "reported_cells": reported, "floor_cells": floor_rows, "contrasts": contrast_rows}
    files["outputs/" + "1" * 64 + ".json"] = sensitivity
    floors = [item("floor_composition", True, f"{pack} {cid}: guarded operative floor",
                   pack=pack, cell_id=cid, guarded_j=42.0, allowance_j=1.0,
                   source="survivor_rescreen", drift_widened_j=43.0, minted_j=43.0 if kind == "absolute" else 103.5)
              for pack in ("alpha", "beta") for cid, phase, kind in extraction_cells(pack) if phase != "p42"]
    floors.append(item("kept_units", False, "alpha kept units", pack="alpha", cell_id=ALPHA_CELLS["absolute"], n_r=9, n_b=9))
    floors += [item("kept_units", False, f"{pack} {cid}: kept units", pack=pack, cell_id=cid, n_r=9, n_b=9)
               for pack in ("alpha", "beta") for cid, _, _ in extraction_cells(pack) if cid != ALPHA_CELLS["absolute"]]
    contrasts = []
    for row in rows:
        cid, est = row["contrast_id"], row["estimator"]
        denominator = 512 if cid == DECODE else 2048
        contrasts += [item("primary_contrast", True, cid + ": primary", contrast_id=cid, estimator=copy.deepcopy(est),
                           decision_interval=copy.deepcopy(row["deterministic_bounds"]["decision_interval"])),
                      item("battery_assist_contrast", True, cid + ": without assisted quads", contrast_id=cid,
                           status="computed", n=9, mean_j=-1.25, s_d=16.0, se=5.25, t_star=2.306, lower_j=-13.5,
                           upper_j=11.0, assist_quads=0, assist_members={}),
                      item("magnitude_ratio", True, cid + ": ratio", contrast_id=cid, log_mean=-0.01, log_sd=0.2,
                           ratio=0.99, lower=0.875, upper=1.125),
                      item("magnitude_per_token", True, cid + ": per token", contrast_id=cid, value_j=-0.002,
                           denominator=denominator, metrology={"lower": -0.025, "upper": 0.02},
                           decision={"lower": -0.03, "upper": 0.025}),
                      item("contrast_interval", True, cid + ": rounded t*", contrast_id=cid, n=9, rounded_t=2.306,
                           exact_t=2.306004135033371),
                      item("decision_floor", True, cid + ": decision interval near end", contrast_id=cid,
                           decision_interval=copy.deepcopy(row["deterministic_bounds"]["decision_interval"]),
                           floor_j=103.5, estimate_j=-1.25),
                      item("loo_counts", False, cid + ": leave-one-out rows 9", contrast_id=cid, count=9,
                           exclusive_block_numbers=[]),
                      # L9 prints a loo_magnitude line for every contrast; no leave-one-out row here raises the trigger.
                      item("loo_magnitude", True, cid + ": no leave-one-out row raised the magnitude trigger",
                           contrast_id=cid, rows=[])]
    contrasts += [item("kept_units", False, f"gamma {cid}: kept quads 9", pack="gamma", cell_id=cid, n_r=0, n_b=9)
                  for cid in (DECODE, PREFILL)]
    block_lines = [item("sensitivity_bmax", True, "sensitivity: B_max", **sensitivity["b_max"])]
    block_lines += [item("sensitivity_window", True, "sensitivity: " + p, pack=p, **sensitivity["windows"][p])
                    for p in ("alpha", "beta", "gamma")]
    block_lines += [item("sensitivity_reported", True, "sensitivity: " + row["cell_id"], record=copy.deepcopy(row))
                    for row in sensitivity["reported_cells"]]
    block_lines += [item("sensitivity_floor", True, "sensitivity: floor", record=copy.deepcopy(row))
                    for row in sensitivity["floor_cells"]]
    block_lines += [item("sensitivity_contrast", True, "sensitivity: contrast", record=copy.deepcopy(row))
                    for row in sensitivity["contrasts"]]
    block_lines += [item("sensitivity_boundary", True, "Sensitivity values are never composed into a primary number."),
                    item("harvest_once", False, "no analysed window was harvested twice", no_analysed_window_harvested_twice=True)]
    # FS4 (RC-CMP-10): the history lines, printed by the producer from the window index's attempts.
    block_lines += producer_fixtures.history_lines(INDEX_ATTEMPTS)
    for ratio in files["finalized/outputs/closeout.ratio-table.json"]["ratios"]:
        label = "R_cm" if ratio["numerator_field"].startswith("common_mode") else "R"
        block_lines.append(item("dominance_ratio", True,
                                f"{ratio['cell_id']} {ratio['component']}: {label} 1.0395; point diagnostic; no interval",
                                cell_id=ratio["cell_id"], component=ratio["component"], n=9, status="complete",
                                ratio=ratio["ratio"], numerator_j=39.5, denominator_j=38.0))
    block_lines.append(item("dominance_branch", True, "D-165 branch B", branch="B", dominance_sentence_licensed=False))
    window_lines = {p: [item("stored_status", False, p + ": stored verdict status: passed", status="passed"),
                        item("flag_count", False, p + ": flag x: 0", count=0, family="PHYSICS_IN_SPAN", code="x",
                             blinding="OPEN"),
                        item("below_screen_bound", True, p + ": operative bound below 36.46 ms: no", b_op_s=0.0375,
                             below=False)] + neg8_lines(p) + structure_lines(p)
                    for p in ("alpha", "beta", "gamma")}
    fixed = [item(word, False, "fixed sentence " + word) for word in cmp.FIXED_SENTENCE_WORDS if word != "order"]
    fixed += [item("floor_drift_ownership", False, "Each contrast's floor carries the floor window's drift allowance."),
              item("gross_energy", False, "Phase energy is gross.")]
    files[f"disclosures/{SHA}.json"] = {
        "schema_version": "joulewise.b5_disclosures.v1", "windows": windows, "cells": cells_lines + kept_cells,
        "floors": floors, "contrasts": contrasts, "window_lines": window_lines, "block_lines": block_lines,
        "sensitivity": copy.deepcopy(sensitivity),
        "fixed_sentences": [item("order", False, "Every quad ran 1.7B, 8B, 8B, 1.7B in that fixed order.")] + fixed}
    return files


def recompute_output():
    floors, ratios, common = {}, {}, {}
    for model in ("Qwen3-1.7B-4bit", "Qwen3-8B-4bit"):
        for phase in ("decode", "prefill"):
            for kind in ("absolute", "comparative"):
                floors[f"{model}/{phase}/{kind}"] = {
                    "corner_widened_unguarded_floor_j": 39.5, "operative_unguarded_floor_j": 39.5, "guarded_floor_j": 42.0,
                    "drift_widened_guarded_floor_j": 43.0, "prediction_j": 38.0, "max_abs_deviation_j": 29.5, "s_j": 15.5,
                    "allowance_j": 1.0, "guard": 1.0, "n": 9}
                ratios[f"{model}/{phase}/{kind}"] = {"R": 39.5 / 38.0, "numerator_j": 39.5, "denominator_j": 38.0, "n": 9}
            common[f"{model}/{phase}"] = {"R_cm": 39.5 / 38.0, "numerator_j": 39.5, "denominator_j": 38.0, "n": 9}
    contrast = {"n": 9, "dbar_j": -1.25, "s_d_j": 16.0, "se_j": 5.25, "t_star": 2.306,
                "metrology_interval_j": [-13.5, 11.0], "D_j": 2.75, "decision_interval_j": [-16.25, 13.75],
                "floor_gate_j": 103.5, "holm_p": 1.0, "holm_reject": False, "outcome": "not_resolvable",
                "direction": "negative", "ceiling": "L1"}
    families = [family for pack in ("alpha", "beta") for phase, (_, family) in reported_cells(pack).items()
                if phase != "prefill-p42"]
    assist = {family: {"mean_j": 50.0, "lower_j": 47.0, "upper_j": 53.0, "n_r": 9, "n_b": 9, "interval": {"h_j": 2.0, "B_j": 1.0},
                       "assist_members_by_stratum": {}} for family in families}
    assist.update({cid: {"n": 9, "dbar_j": -1.25, "s_d_j": 16.0, "se_j": 5.25, "t_star": 2.306,
                         "metrology_interval_j": [-13.5, 11.0], "status": "computed", "assist_quads": 0,
                         "assist_members_by_stratum": {}} for cid in (DECODE, PREFILL)})
    descriptive = {"ratio": 0.99, "ratio_interval": [0.875, 1.125], "per_token_difference_j": -0.002,
                   "per_token_metrology_interval_j": [-0.025, 0.02], "per_token_decision_interval_j": [-0.03, 0.025]}
    return {"program_sha256": "f" * 64,
            "members": {"ALPHA": {"run-a": {"E_j": {"prefill": 2.5, "decode": 97.25, "request": 120.0}, "selected": True},
                                  "corpus-r1": {"E_j": {"prefill": 1.0, "decode": 1.0, "request": 1.0}, "selected": False}}},
            "inputs": {p: {"exclusions_sha256": "e" * 64, "claim_usable": True} for p in ("ALPHA", "BETA", "GAMMA")},
            "windows": {p: {"b_op_s": 0.0375, "neg8": neg8_recompute()} for p in ("ALPHA", "BETA", "GAMMA")},
            "disclosures": {"sensitivity_bound": {
                "B_max_s": 0.0625, "T": 424, "attaining_sequence": 396,
                "windows": {p: {"b_sens_s": 0.0625} for p in ("ALPHA", "BETA", "GAMMA")},
                "reported_cells": {family: {"status": "computed", "mean_j": 50.0, "lower_j": 47.0, "upper_j": 53.0,
                                            "interval": {"h_j": 2.0, "B_j": 1.0}, "attribution_floor": {"value_j": 3.0}}
                                   for family in families},
                "floor_cells": {aggregate_key(cid): dict(FLOOR_VALUES) for cid in AGGREGATE_CELLS},
                "floors": {aggregate_key(cid) + "/absolute": {"allowance_j": 1.0} for cid in AGGREGATE_CELLS},
                "contrasts": {cid: {"floor_gate_j": 103.5, "D_j": 3.0, "outcome": "not_resolvable",
                                    "outcome_equals_primary": True} for cid in (DECODE, PREFILL)}},
                "battery_assist": assist,
                "cross_window": {f"{model}/{phase}": dict(CROSS_WINDOW) for _, model in PACK_MODELS.values()
                                 for phase in ("decode", "prefill")}},
            "p42": {"df-ph-prefill-p42-qwen3-1p7b": {"status": "expected_unresolvable"},
                    "df-ph-prefill-p42-qwen3-8b": {"status": "expected_unresolvable"}},
            "floors": floors,
            "floor_cells": {model + "/" + phase: {"floor_abs_j": 43.0, "floor_cmp_j": 103.5, "floor_gate_j": 103.5}
                            for model in ("Qwen3-1.7B-4bit", "Qwen3-8B-4bit") for phase in ("decode", "prefill")},
            "dominance": {"branch": "B", "ratios": ratios, "common_mode": common},
            "contrasts": {cid: {**contrast, "p": p, "kept_quads": list(KEPT[cid]),
                                "loo": [recompute_loo_row(cid, block, p) for block in KEPT[cid]]}
                          for cid, p in ((DECODE, 0.84), (PREFILL, 0.68))},
            "reported_cells": {family: copy.deepcopy(REPORTED_RECOMPUTE) for family in families},
            "descriptive": {cid: dict(descriptive) for cid in (DECODE, PREFILL)},
            "exclusions_rederivation": {p: {"status": "agrees"} for p in ("ALPHA", "BETA", "GAMMA")}}


def no_table(c, custody, ours):
    """The comparator before RC-CMP-9, for counterfactuals: no expected-check table, so no check of what the
    outputs omit and every step-11 leaf counts as inside the table."""
    c.claimed.update({"fill": {()}, "disclosure": {()}})
    return []


# Key-bound rules (RC-CMP-3 X1): each mapped leaf names the comparison row it copies. The fixture is
# producer-shaped (RC-CMP-6 G4), so the rules are the shipped map.
RULES = cmp.COVERAGE


def written(name, value):
    """The bytes L9 writes: a step-11 output in its writer's canonical form (G1), other outputs as JSON.

    A planted NaN or Infinity cannot be written canonically; it is written the way json.dumps spells it.
    """
    tail = next((cmp.STEP11_TAILS[label] for label, pattern in cmp.STEP11_SOURCES if re.fullmatch(pattern, name)), None)
    if tail is None:
        return json.dumps(value).encode()
    try:
        return cmp.canonical(value) + tail
    except ValueError:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + tail


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.files, self.ours = l9_files(), recompute_output()

    def custody(self):
        root = self.root / ("custody-" + hashlib.sha256(json.dumps(self.files, sort_keys=True).encode()).hexdigest()[:8])
        outputs = []
        for name, value in self.files.items():
            path = root / cmp.RESTRICTED / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = written(name, value)
            path.write_bytes(raw)
            outputs.append({"name": name, "sha256": hashlib.sha256(raw).hexdigest()})
        (root / cmp.RECORD).write_text(json.dumps({
            "window_index_sha256": hashlib.sha256(Path(cmp.WINDOW_INDEX).read_bytes()).hexdigest(),
            "steps": [{"step": "11", "window": None, "status": "ok", "outputs": outputs}]}))
        return root

    def run_compare(self, bars="recompute_coded_7e322b76", rules=RULES):
        ours = self.root / "ours.json"
        ours.write_text(json.dumps(self.ours))
        return cmp.run(self.custody(), ours, BARS[bars], rules)

    def fails(self, result):
        return {family: n["fail"] for family, n in result["counts"].items() if n["fail"]}

    def test_baseline_agrees_under_both_bar_sets(self):
        for bars in BARS:
            with self.subTest(bars=bars):
                result = self.run_compare(bars)
                self.assertEqual(self.fails(result), {})
                self.assertEqual(result["coverage"]["unmapped"], [])
                self.assertTrue(all(result["counts"][f]["pass"] for f in cmp.NUMERIC + cmp.CATEGORICAL
                                    if f not in ("reported_cell_j", "battery_term")), result["counts"])
                # This fixture has no meter stream; the meter line is in test_comparator_meter.
                self.assertFalse(set(cmp.METER) & set(result["counts"]))

    def planted(self, family, edit, check, rows=1):
        """The fault fails its family; with the check disabled it passes (counterfactual)."""
        edit(self)
        self.assertEqual(self.fails(self.run_compare()), {family: rows})
        with check():
            self.assertEqual(self.fails(self.run_compare()), {})

    def numeric_fault(self, family, edit, rows=1):
        self.planted(family, edit, lambda: mock.patch.object(cmp, "bar_for", return_value=float("inf")), rows)

    def test_planted_run_phase_energy(self):
        self.numeric_fault("run_phase_energy_j", lambda t: t.ours["members"]["ALPHA"]["run-a"]["E_j"].update(decode=97.25 + 2e-4))

    def test_planted_floor(self):
        self.numeric_fault("floor_j", lambda t: t.ours["floors"]["Qwen3-8B-4bit/decode/absolute"].update(prediction_j=38.0 * (1 + 2e-6)))

    def test_planted_floor_gate(self):
        # L9's aggregate cell (the recompute's cell also feeds the producer-shaped verdict's arm resolution).
        self.numeric_fault("floor_gate_j", lambda t: t.files[f"mint/{SHA}-aggregate-floor.json"]["cells"][0].update(
            floor_cmp_j=103.5 * (1 - 2e-6)))

    def test_planted_dominance_ratio(self):
        self.numeric_fault("dominance_ratio", lambda t: t.ours["dominance"]["ratios"]["Qwen3-1.7B-4bit/decode/absolute"].update(R=39.5 / 38.0 * (1 + 2e-6)))

    def test_planted_contrast(self):
        # RC-CMP-9: the sensitivity record's own primary D (read directly) and the sum of the verdict's printed
        # deterministic terms see the moved D too. RC-CMP-11 F1: the record's not_below_primary word reads D's
        # sensitivity - primary difference, identical on both sides, so the word is decided and agrees; the moved D
        # is caught by the three contrast_j rows.
        self.ours["contrasts"][DECODE].update(D_j=2.75 * (1 + 2e-6))
        self.assertEqual(self.fails(self.run_compare()), {"contrast_j": 3})
        with mock.patch.object(cmp, "bar_for", return_value=float("inf")):
            self.assertEqual(self.fails(self.run_compare()), {})

    def test_planted_contrast_p(self):
        self.numeric_fault("contrast_p", lambda t: t.ours["contrasts"][PREFILL].update(p=0.68 + 2e-6))

    def test_planted_descriptive_ratio(self):
        self.numeric_fault("descriptive_ratio", lambda t: t.ours["descriptive"][DECODE].update(ratio=0.99 * (1 + 2e-6)))

    def test_planted_per_token(self):
        self.numeric_fault("per_token_j", lambda t: t.ours["descriptive"][DECODE].update(per_token_difference_j=-0.002 + 2e-6))

    def test_planted_kept_units(self):
        # RC-CMP-9: the recompute's kept set also fixes which leave-one-out rows are expected and the fill's
        # kept and removed block ids by position, so those rows (routing_id) DISAGREE beside the kept_units row.
        self.ours["contrasts"][DECODE].update(kept_quads=["b01"])
        fails = self.fails(self.run_compare())
        self.assertEqual(set(fails), {"kept_units", "routing_id"})
        # RC-CMP-10 FABLE F2: each registered block's included word is bound to the recompute's kept set too (nine
        # kept blocks the recompute now leaves out).
        self.assertEqual(fails["kept_units"], 1 + 9)
        original = cmp.Comparison.exact

        def lenient(c, fam, key, l9, ours, **raw):
            return original(c, fam, key, l9, l9 if fam == "kept_units" or "sampling_removed_block_ids" in key else ours,
                            **raw)
        # Counterfactual: the kept_units rows lenient, and neither the table nor the block-id positions (RC-CMP-10:
        # nor the verdict's own sampling copy).
        with mock.patch.object(cmp.Comparison, "exact", lenient), mock.patch.object(cmp, "compare_expected", no_table), \
                mock.patch.object(cmp, "verdict_block_ids", lambda row: ([], [])), \
                mock.patch.object(cmp, "registered_block_ids", lambda registry, cid, mine: ([], [])):
            self.assertEqual(self.fails(self.run_compare()), {})

    def test_mapped_leaf_whose_value_was_not_compared_refuses(self):
        # The fill copies an estimate no comparison saw (a copy error in the adapter).
        self.files[f"outputs/{SHA}-results-fill-input.json"]["gamma"]["contrasts"][1]["estimate"] = 1.25
        result = self.run_compare()
        self.assertEqual(result["coverage"]["uncompared"], ["fill:gamma/contrasts/*/estimate"])
        self.assertEqual(self.fails(result), {})
        # Counterfactual: path-only coverage (no value check) passes it.
        with mock.patch.object(cmp, "same", lambda a, b: True):
            self.assertEqual(self.run_compare()["coverage"]["unmapped"], [])

    def test_shipped_coverage_map_is_the_default(self):
        self.assertIs(cmp.coverage.__defaults__[0], None)
        self.assertTrue(cmp.COVERAGE)

    def test_planted_b_op(self):
        # The bracket row and the sensitivity record's window row both see the moved b_op.
        self.ours["windows"]["BETA"].update(b_op_s=0.0375 * (1 + 2e-6))
        self.assertEqual(self.fails(self.run_compare()), {"b_op_s": 2})
        with mock.patch.object(cmp, "bar_for", return_value=float("inf")):
            self.assertEqual(self.fails(self.run_compare()), {})

    def test_planted_count(self):
        self.numeric_fault("count", lambda t: t.files[f"brackets/{SHA}-block.json"].update(T=425))

    def exact_fault(self, family, edit, rows=1):
        original = cmp.Comparison.exact

        def lenient(c, fam, key, l9, ours, **raw):
            return original(c, fam, key, l9, l9 if fam == family else ours, **raw)
        self.planted(family, edit, lambda: mock.patch.object(cmp.Comparison, "exact", lenient), rows)

    def test_planted_outcome_word(self):
        # RC-CMP-9: the producer-complete fixture derives nine leave-one-out trigger lists from the full outcome, so
        # the planted outcome word is the recompute's sensitivity outcome (one row).
        self.exact_fault("outcome_word", lambda t: t.ours["disclosures"]["sensitivity_bound"]["contrasts"][DECODE].update(
            outcome="unresolved"))

    def test_planted_dominance_branch(self):
        # The branch and, since RC-CMP-7 F2, the licensed word that follows it (licensed iff branch A).
        self.exact_fault("dominance_branch", lambda t: t.ours["dominance"].update(branch="A"), rows=2)

    def test_planted_p42_status(self):
        # The extraction report and the sensitivity record's refused p42 cell both see the moved status.
        # Since RC-CMP-7 F2 the sensitivity line's printed status and code words are compared too (outcome_word);
        # since RC-CMP-9 F4 the projection's refused p42 cell too (the base fixture lists it).
        # RC-CMP-10 FS2: the projection's refused code is compared too (a third outcome_word row).
        self.ours["p42"]["df-ph-prefill-p42-qwen3-8b"].update(status="computed")
        self.assertEqual(self.fails(self.run_compare()), {"p42_status": 3, "outcome_word": 3})
        original = cmp.Comparison.exact

        def lenient(c, fam, key, l9, ours, **raw):
            return original(c, fam, key, l9, l9 if fam == "p42_status" or "p42" in key else ours, **raw)
        with mock.patch.object(cmp.Comparison, "exact", lenient):
            self.assertEqual(self.fails(self.run_compare()), {})

    def test_planted_holm_order(self):
        # Swapping which contrast has the smaller p changes only the Holm order.
        def swap(t):
            rows = t.files[f"outputs/{SHA}-claim-verdicts.json"]["contrasts"]
            rows[0]["multiplicity"]["raw_p"], rows[1]["multiplicity"]["raw_p"] = 0.68, 0.68 + 5e-7
            t.ours["contrasts"][DECODE]["p"], t.ours["contrasts"][PREFILL]["p"] = 0.68 + 6e-7, 0.68 + 5e-7
        self.exact_fault("holm_order", swap)

    def test_planted_exclusions_rederivation(self):
        self.exact_fault("exclusions_rederivation", lambda t: t.ours["exclusions_rederivation"]["GAMMA"].update(status="disagrees"))

    def test_missing_or_null_on_either_side_disagrees(self):
        for side in ("l9", "recompute"):
            with self.subTest(side=side):
                self.setUp()
                if side == "l9":
                    self.files[f"mint/{SHA}-extraction-alpha.json"]["cells"][0]["floor"]["guarded_floor_j"] = None
                else:
                    del self.ours["floors"]["Qwen3-8B-4bit/decode/comparative"]["guarded_floor_j"]
                result = self.run_compare()
                # RC-CMP-9: the expected-check table requires the recompute's floor terms of a computed cell (its
                # extraction floor and floor-composition line): the missing key DISAGREEs there too.
                self.assertEqual(self.fails(result), {"floor_j": 1} if side == "l9" else {"floor_j": 1, "routing_id": 2})
                row = next(r for r in result["comparisons"] if r["verdict"] == "DISAGREE" and r["family"] == "floor_j")
                self.assertEqual(row["reason"], "missing_or_null")
                # Counterfactual: skipping a missing value (recording it as agreement) hides it.
                original = cmp.Comparison.numeric

                def skipping(c, family, key, l9, ours):
                    if not (cmp.finite(l9) and cmp.finite(ours)):
                        c.rows.append({"family": family, "key": key, "verdict": "AGREE"})
                        return
                    return original(c, family, key, l9, ours)
                with mock.patch.object(cmp.Comparison, "numeric", skipping), \
                        mock.patch.object(cmp, "compare_expected", no_table):
                    self.assertEqual(self.fails(self.run_compare()), {})

    def test_unmapped_step11_fill_refuses(self):
        self.files[f"outputs/{SHA}-results-fill-input.json"]["gamma"]["contrasts"][0]["decision_word"] = "x"
        result = self.run_compare()
        self.assertEqual(result["coverage"]["unmapped"], ["fill:gamma/contrasts/*/decision_word"])
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        out = io.StringIO()
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(io.StringIO()):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["s13_block6"]), "--restricted-out", str(self.root / "r.json")])
        self.assertEqual(code, 2)
        # Counterfactual: a catch-all rule (no exhaustiveness) maps it silently.
        result = self.run_compare(rules=RULES + ((r".*", "uncovered:catch-all"),))
        self.assertEqual(result["coverage"]["unmapped"], [])

    def test_absent_step11_output_refuses(self):
        del self.files[f"outputs/{SHA}-results-fill-input.json"]
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        err = io.StringIO()
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(err):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["s13_block6"]), "--restricted-out", str(self.root / "r.json")])
        self.assertEqual((code, err.getvalue()), (2, "refused=step11_outputs_absent\n"))

    def test_mapping_to_a_family_with_no_comparison_is_not_coverage(self):
        rules = ((r"fill:gamma/contrasts/\*/estimate", "reported_cell_j", "{cid}/dbar_j"),) + RULES
        self.assertEqual(self.run_compare(rules=rules)["coverage"]["unmapped"], ["fill:gamma/contrasts/*/estimate"])

    def test_public_stdout_carries_counts_only(self):
        # A run's phase energy is not printed in step 11, so the disagreement is a family failure, not a coverage refusal.
        self.ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] = 97.2512345678
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        out = io.StringIO()
        restricted = self.root / "restricted.json"
        with mock.patch.object(cmp, "COVERAGE", RULES), contextlib.redirect_stdout(out):
            code = cmp.main(["--l9-custody", str(self.custody()), "--recompute", str(ours),
                             "--bars", str(BARS["recompute_coded_7e322b76"]), "--restricted-out", str(restricted)])
        self.assertEqual(code, 1)
        text = out.getvalue()
        self.assertNotIn("97.251", text)
        self.assertNotIn("97.25", text)
        self.assertNotRegex(text, r"\d\.\d")
        self.assertIn('"run_phase_energy_j":{"fail":1', text)
        detail = json.loads(restricted.read_text())
        row = next(r for r in detail["comparisons"] if r["verdict"] == "DISAGREE")
        self.assertAlmostEqual(row["difference"], 97.2512345678 - 97.25)

    def test_bars_come_from_the_config(self):
        bars = json.loads(BARS["s13_block6"].read_text())
        del bars["families"]["floor_j"]
        path = self.root / "bars.json"
        path.write_text(json.dumps(bars))
        with self.assertRaisesRegex(cmp.Refusal, "bars_family_missing:floor_j"):
            cmp.load_bars(path)
        # S-13's 1 mJ run bar admits a 0.2 mJ difference the coded 1e-6 relative bar refuses.
        self.ours["members"]["ALPHA"]["run-a"]["E_j"]["decode"] = 97.25 + 2e-4
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {})
        self.assertEqual(self.fails(self.run_compare("recompute_coded_7e322b76")), {"run_phase_energy_j": 1})

    def test_per_key_override_sets_its_own_printed_precision(self):
        # S-13 placeholder: se prints at 6 decimals inside a 5-decimal family, so 2e-6 J passes for D but not for se.
        self.ours["contrasts"][DECODE]["D_j"] = 2.75 + 2e-6
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {})
        self.ours["contrasts"][DECODE]["se_j"] = 5.25 + 2e-6
        self.assertEqual(self.fails(self.run_compare("s13_block6")), {"contrast_j": 1})
        with mock.patch.object(cmp, "family_spec", lambda spec, key: spec):
            self.assertEqual(self.fails(self.run_compare("s13_block6")), {})

    def test_l9_output_digest_is_checked(self):
        root = self.custody()
        path = root / cmp.RESTRICTED / f"brackets/{SHA}-block.json"
        path.write_text(json.dumps({"T": 999, "attained_by_sequence": 396, "value_s": 0.0625}))
        ours = self.root / "o.json"
        ours.write_text(json.dumps(self.ours))
        with self.assertRaisesRegex(cmp.Refusal, "l9_output_digest_differs"):
            cmp.run(root, ours, BARS["s13_block6"], RULES)

    def test_no_l9_import(self):
        text = (ROOT / "scripts/compare_b5_recompute.py").read_text()
        self.assertNotRegex(text, r"(?m)^\s*(from|import)\s+(joulewise|scripts)\b")
        imports = {line.split()[1].split(".")[0] for line in text.splitlines()
                   if line.startswith(("import ", "from "))}
        self.assertTrue(imports <= {"argparse", "hashlib", "itertools", "json", "math", "pathlib", "re", "statistics", "sys"},
                        imports)


if __name__ == "__main__":
    unittest.main()
