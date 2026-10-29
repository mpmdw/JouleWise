"""RC-CMP-6 G1-G6: the comparator's producer-derived input gate, with the round-3 witnesses as regression tests.

G1 reads a step-11 output only as the canonical serialisation of its strict parse (L9's writer
flags); G2 reads an identity field only on the object it names; G3 routes only by ids the sealed
campaign configs register, looked up literally. The witnesses are the round-3 reviews' (Opus F1-F5,
Q1-Q5; Sol 1-3, RC-CMP-OPUS-REV-3 and RC-CMP-SOL-REV-3) and the Fable consult's probes A1-A8,
B1-B7, C1-C4, D (RC-CMP-FABLE-CONSULT prototype_gate.py). At 7fede8c7 the comparator exits 0 on
B1, B2, B3, B5, B7, C1-C4, Q1b, Q1e, Q5a, Q5b and Sol's diagnostics subtree (counterfactuals in
.codex-report/RC-CMP-6.md); each test here also shows, where the check can be switched off in
place, the same bytes passing without it.
"""
import ast
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from . import test_comparator
from .test_comparator import BARS, DECODE, PREFILL, ROOT, SHA, cmp, written
from .test_review_fixes import DISCLOSURE, FILL, VERDICTS, Case, MeterCase
from .test_structural_rules import v3_floor

CODED = BARS["recompute_coded_7e322b76"]
EXTRACTION = f"mint/{SHA}-extraction-alpha.json"
# 7fede8c7's identity rule, at any depth (scripts/compare_b5_recompute.py:1297-1300 there).
OLD_IDENTITY = (r"(fill|disclosure):(.*/)?(cell_id|contrast_id|unit_id|plan_id|run_id|bundle_id|pack|harvest_pin|record_shape|"
                r"model|stage_ids/\*|stage_id|floor_cell_ids/\*|floor_row_ids/\*|source_cell_ids/\*|floor_source_cell_ids/\*|"
                r"omitted_block_id|transport_group_id|[a-z_]*sha256|[a-z_]*_id|claim_verdicts_id|manifest_id|artifact_id|"
                r"central_band/(pack|plan_id))")


class GateCase(Case):
    def raw_exit(self, name, before, after):
        """The CLI on the case's custody with one output's written bytes edited (its digest re-listed)."""
        root = self.custody()
        path = root / cmp.RESTRICTED / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(before, text)
        path.write_bytes(text.replace(before, after, 1).encode("utf-8"))
        return self.relisted(root)

    def raw_bytes_exit(self, name, raw):
        root = self.custody()
        (root / cmp.RESTRICTED / name).write_bytes(raw)
        return self.relisted(root)

    def relisted(self, root):
        record = json.loads((root / cmp.RECORD).read_text())
        for output in record["steps"][0]["outputs"]:
            output["sha256"] = hashlib.sha256((root / cmp.RESTRICTED / output["name"]).read_bytes()).hexdigest()
        (root / cmp.RECORD).write_text(json.dumps(record))
        ours = self.root / "ours-raw.json"
        ours.write_text(json.dumps(self.ours))
        out = self.root / ("restricted-raw-%d.json" % len(list(self.root.glob("restricted-raw-*.json"))))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = cmp.main(["--l9-custody", str(root), "--recompute", str(ours), "--bars", str(CODED),
                             "--restricted-out", str(out)])
        return code, err.getvalue(), json.loads(out.read_text())

    def refused(self, code):
        """The refusal the shipped CLI gives on this case."""
        result = self.exit_code(CODED)
        self.assertEqual(result[:2], (2, f"refused={code}\n"))
        self.assertEqual(result[2], {"schema": cmp.SCHEMA, "refused": code})

    def without_gate(self):
        """The 7fede8c7 composition: no gate (G2, G3), leaves() taking an identity field at any depth, and
        the identity rule at any depth (G5)."""
        return _patches(
            mock.patch.object(cmp, "gate", lambda *args, **kwargs: None),
            mock.patch.object(cmp, "owns", lambda label, key, star: key in cmp.IDENTITY_FIELDS),
            mock.patch.object(cmp, "COVERAGE", cmp.COVERAGE + ((OLD_IDENTITY, cmp.IDENTITY),)))


@contextlib.contextmanager
def _patches(*patches):
    with contextlib.ExitStack() as stack:
        for patch in patches:
            stack.enter_context(patch)
        yield


def plain_loads(raw, label, tail):
    """A reader that keeps the last of two members and takes any spelling (the 7fede8c7 step-11 read)."""
    return json.loads(raw, parse_constant=lambda word: cmp.NONFINITE)


class ProducerShapeTests(GateCase):
    """G4 (consult D): the base fixture carries the producers' key sets."""
    ADAPTER_ROW = {"contrast_id", "metric", "conditions", "limitations", "floor_source_cell_ids", "estimate", "interval",
                   "decision_interval", "deterministic_widening_total", "j_per_token", "n", "floor", "multiplicity",
                   "claim_evaluation", "plan_id", "claim_role", "hypothesized_direction", "equivalence", "sampling",
                   "loo", "df", "t_critical_95", "kept_block_ids", "removed_block_ids"}

    def test_fill_rows_carry_the_24_adapter_keys(self):
        for row in self.files[FILL]["gamma"]["contrasts"]:
            self.assertEqual(set(row), self.ADAPTER_ROW)
        self.assertEqual(len(self.ADAPTER_ROW), 24)
        self.assertEqual(set(self.files[FILL]), {"schema_version", "campaigns", "gamma", "characterization"})
        self.assertEqual(set(self.files[FILL]["gamma"]), {"claim_verdicts_id", "claim_verdicts_sha256", "evidence_class",
                                                          "limitations", "contrasts", "finalized_manifest",
                                                          "floor_artifact", "exclusions_sha256"})
        self.assertEqual(set(self.files[FILL]["campaigns"]["alpha"]),
                         {"plan_id", "attempt", "claim_usable", "exclusions_sha256", "harvest_record_sha256"})

    def test_disclosure_record_carries_the_producer_sections_and_item_keys(self):
        record = self.files[DISCLOSURE]
        self.assertEqual(set(record), {"schema_version", "windows", "cells", "floors", "contrasts", "window_lines",
                                       "block_lines", "sensitivity", "fixed_sentences"})
        lines = (record["floors"] + record["contrasts"] + record["block_lines"] + record["fixed_sentences"]
                 + [line for lines in record["window_lines"].values() for line in lines])
        for line in lines:
            self.assertTrue({"line", "restricted", "label", "text"} <= set(line), line)
        kinds = {line["line"] for line in lines}
        self.assertTrue({"floor_composition", "primary_contrast", "decision_floor", "contrast_interval",
                         "dominance_ratio", "sensitivity_reported"} <= kinds)

    def test_producer_shape_is_covered_and_agrees(self):
        code, err, out = self.exit_code(CODED)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual((out["coverage"]["unmapped"], out["coverage"]["nonfinite"]), ([], []))
        leaves = out["coverage"]["leaves"]
        # A8: the registered comparative spelling binds (7fede8c7 refused it, key_unresolved).
        self.assertEqual(leaves["disclosure:floors/floor_composition/guarded_j"], "floor_j")
        self.assertEqual(leaves["disclosure:floors/floor_composition/cell_id"], "routing_id")
        self.assertEqual(leaves["disclosure:block_lines/dominance_ratio/ratio"], "dominance_ratio")
        self.assertEqual(leaves["fill:gamma/contrasts/*/floor/arm_gates/*/floor_gate_j"], "floor_gate_j")


class CanonicalLoadTests(GateCase):
    """G1: one reading of the bytes, L9's writer only."""
    def test_control_a1_l9_writer_bytes_are_read(self):
        root = self.custody()
        self.assertEqual((root / cmp.RESTRICTED / FILL).read_bytes(),
                         json.dumps(self.files[FILL], sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                    allow_nan=False).encode() + b"\n")
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_duplicate_member_wrong_value_first_refuses_b3_opus_f2_q4_sol2(self):
        code, err, out = self.raw_exit(FILL, '"estimate":-1.25', '"estimate":999.0,"estimate":-1.25')
        self.assertEqual((code, err), (2, "refused=l9_output_duplicate_key:fill\n"))
        # Counterfactual: the 7fede8c7 reader keeps the agreeing last member, and the run exits 0.
        with mock.patch.object(cmp, "strict_loads", plain_loads):
            self.assertEqual(self.raw_exit(FILL, '"estimate":-1.25', '"estimate":999.0,"estimate":-1.25')[0], 0)

    def test_duplicate_member_agreeing_value_first_refuses_b4(self):
        code, err, _ = self.raw_exit(FILL, '"estimate":-1.25', '"estimate":-1.25,"estimate":999.0')
        self.assertEqual((code, err), (2, "refused=l9_output_duplicate_key:fill\n"))

    def test_nan_erased_by_a_later_member_refuses_b5_sol2(self):
        code, err, _ = self.raw_exit(FILL, '"estimate":-1.25', '"estimate":NaN,"estimate":-1.25')
        self.assertEqual((code, err), (2, "refused=l9_output_nonfinite:fill\n"))
        with mock.patch.object(cmp, "strict_loads", plain_loads):
            self.assertEqual(self.raw_exit(FILL, '"estimate":-1.25', '"estimate":NaN,"estimate":-1.25')[0], 0)

    def test_lone_nan_refuses_at_the_load_b6(self):
        code, err, _ = self.raw_exit(FILL, '"estimate":-1.25', '"estimate":NaN')
        self.assertEqual((code, err), (2, "refused=l9_output_nonfinite:fill\n"))

    def test_duplicate_member_in_the_disclosure_refuses(self):
        code, err, _ = self.raw_exit(DISCLOSURE, '"ratio":0.99', '"ratio":0.5,"ratio":0.99')
        self.assertEqual((code, err), (2, "refused=l9_output_duplicate_key:disclosure\n"))

    def test_another_writer_refuses_c2_c3_c4(self):
        pretty = (json.dumps(self.files[FILL], indent=1, sort_keys=True) + "\n").encode()
        unsorted = (json.dumps(self.files[FILL], separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        no_newline = written(FILL, self.files[FILL])[:-1]
        escaped = written(DISCLOSURE, self.files[DISCLOSURE]).replace("1.7B".encode(), "1\\u002e7B".encode(), 1)
        cases = {"pretty-printed": (FILL, pretty), "unsorted keys": (FILL, unsorted), "no trailing newline": (FILL, no_newline),
                 "escaped character": (DISCLOSURE, escaped)}
        for label, (name, raw) in cases.items():
            with self.subTest(label):
                code, err, _ = self.raw_bytes_exit(name, raw)
                label_ = "fill" if name == FILL else "disclosure"
                self.assertEqual((code, err), (2, f"refused=l9_output_not_canonical:{label_}\n"))
                with mock.patch.object(cmp, "strict_loads", plain_loads):
                    self.assertEqual(self.raw_bytes_exit(name, raw)[0], 0, label)
        code, err, _ = self.raw_exit(FILL, '"estimate":-1.25', '"estimate":-1.25E0')
        self.assertEqual((code, err), (2, "refused=l9_output_not_canonical:fill\n"))
        with mock.patch.object(cmp, "strict_loads", plain_loads):
            self.assertEqual(self.raw_exit(FILL, '"estimate":-1.25', '"estimate":-1.25E0')[0], 0)

    def test_disclosure_with_the_fills_newline_refuses(self):
        raw = written(DISCLOSURE, self.files[DISCLOSURE]) + b"\n"
        self.assertEqual(self.raw_bytes_exit(DISCLOSURE, raw)[:2], (2, "refused=l9_output_not_canonical:disclosure\n"))

    def test_every_other_input_refuses_a_duplicate_member(self):
        # L9's other outputs, the recompute's output, the harvest meter record and the bar set.
        root = self.custody()
        path = root / cmp.RESTRICTED / f"brackets/{SHA}-block.json"
        path.write_text('{"T": 424, "T": 425, "attained_by_sequence": 396, "value_s": 0.0625}')
        self.relisted(root)
        ours = self.root / "ours-dup.json"
        ours.write_text(json.dumps(self.ours))
        with self.assertRaisesRegex(cmp.Refusal, "^l9_output_duplicate_key$"):
            cmp.run(root, ours, CODED)
        ours.write_text('{"program_sha256": "f", "program_sha256": "g"}')
        with self.assertRaisesRegex(cmp.Refusal, "^recompute_output_duplicate_key$"):
            cmp.run(self.custody(), ours, CODED)
        meter = self.root / "meter.json"
        meter.write_text('{"members": {}, "members": {}}')
        with self.assertRaisesRegex(cmp.Refusal, "^harvest_meter_duplicate_key$"):
            cmp.load_meter_records(["alpha=" + str(meter)])
        bars = self.root / "bars.json"
        bars.write_text(CODED.read_text().replace('"families"', '"families": {}, "families"', 1))
        with self.assertRaisesRegex(cmp.Refusal, "^bars_duplicate_key$"):
            cmp.load_bars(bars)


class OwnerIdentityTests(GateCase):
    """G2: an identity field is read only on the object it names."""
    def test_floors_swapped_each_naming_the_other_contrast_refuse_b1_opus_f1_q3c(self):
        v3_floor(self)
        decode = next(r for r in self.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == DECODE)
        prefill = next(r for r in self.files[FILL]["gamma"]["contrasts"] if r["contrast_id"] == PREFILL)
        decode["floor"] = {"contrast_id": PREFILL, "active_floor_j": 103.5}
        prefill["floor"] = {"contrast_id": DECODE, "active_floor_j": 120.0}
        self.refused("identity_field_misplaced:fill:gamma/contrasts/*/floor/contrast_id")
        # Counterfactual (Q3c at 7fede8c7): with the gate off and every enclosing scalar merged, exit 0.
        with self.without_gate():
            self.assertEqual(self.exit_code(CODED)[0], 0)
        # Control Q3b: the same swap without the nested ids is a value refusal.
        decode["floor"], prefill["floor"] = {"active_floor_j": 103.5}, {"active_floor_j": 120.0}
        self.assertEqual(self.exit_code(CODED)[:2], (2, "refused=step11_unmapped_fill\n"))

    def test_primary_contrast_rerouted_by_a_nested_contrast_id_refuses_b2_sol1(self):
        # Sol's shape: one primary_contrast line (DECODE's) whose estimator prints PREFILL's estimate. In the
        # full producer shape PREFILL's own line would also bind those rows (duplicate_binding).
        self.set_estimate(PREFILL, -2.5)
        self.ours["contrasts"][PREFILL]["dbar_j"] = -2.5
        self.files[DISCLOSURE]["contrasts"] = [line for line in self.files[DISCLOSURE]["contrasts"]
                                               if not (line["line"] == "primary_contrast" and line["contrast_id"] == PREFILL)]
        line = next(line for line in self.files[DISCLOSURE]["contrasts"]
                    if line["line"] == "primary_contrast" and line["contrast_id"] == DECODE)
        line["estimator"] = {"estimate": -2.5}
        # Control: the wrong decode estimate alone refuses (value_differs).
        code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 2)
        self.assertIn("disclosure:contrasts/primary_contrast/estimator/estimate", out["coverage"]["unmapped"])
        line["estimator"]["contrast_id"] = PREFILL
        self.refused("identity_field_misplaced:disclosure:contrasts/*/estimator/contrast_id")
        with self.without_gate():
            self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_nested_object_repeating_its_owners_id_refuses_c1(self):
        self.files[FILL]["gamma"]["contrasts"][0]["floor"]["contrast_id"] = DECODE
        self.refused("identity_field_misplaced:fill:gamma/contrasts/*/floor/contrast_id")

    def test_an_owner_cannot_shadow_its_enclosing_owner(self):
        # A sensitivity line that names a window and whose record names another one.
        line = next(line for line in self.files[DISCLOSURE]["block_lines"] if line["line"] == "sensitivity_reported")
        line["pack"] = "beta"
        self.refused("identity_field_misplaced:disclosure:block_lines/*/record/pack")

    def test_identity_field_in_any_other_position_refuses(self):
        for edit, where in (
                (lambda f: f[FILL]["gamma"].update(pack="alpha"), "fill:gamma/pack"),
                (lambda f: f[FILL]["gamma"]["contrasts"][0]["loo"].update(omitted_block_id="b01"),
                 "fill:gamma/contrasts/*/loo/omitted_block_id"),
                (lambda f: f[DISCLOSURE]["windows"]["alpha"].update(cell_id="d117-df-ph-decode-qwen3-1p7b-absolute"),
                 "disclosure:windows/alpha/cell_id"),
                (lambda f: f[DISCLOSURE]["contrasts"][0]["decision_interval"].update(text="x"),
                 "disclosure:contrasts/*/decision_interval/text"),
                (lambda f: f[DISCLOSURE]["contrasts"][0].update(contrast_id=None),
                 "disclosure:contrasts/*/contrast_id")):
            with self.subTest(where):
                self.setUp()
                edit(self.files)
                self.refused("identity_field_misplaced:" + where)

    def test_a_bands_pack_is_an_attribute_a6(self):
        record = {"window_lines": {"alpha": [{"line": "machine_summary", "model": "qwen3-1p7b",
                                              "central_band": {"pack": "beta", "lower": 0.9, "upper": 1.1}}]}}
        cmp.gate(record, "disclosure", cmp.load_registry())
        contexts = [context for path, _, context in cmp.leaves(record, "disclosure") if path.endswith("central_band/pack")]
        self.assertNotIn("pack", contexts[0])
        self.assertEqual(contexts[0]["model"][0], "qwen3-1p7b")

    def test_leaves_read_identity_only_from_its_owner(self):
        document = {"gamma": {"contrasts": [{"contrast_id": DECODE, "plan_id": "p",
                                             "floor": {"contrast_id": PREFILL, "active_floor_j": 1.0}}]}}
        context = next(context for path, _, context in cmp.leaves(document, "fill") if path.endswith("active_floor_j"))
        self.assertEqual(context["contrast_id"], (DECODE, "gamma/contrasts/*/contrast_id"))
        self.assertNotIn("plan_id", context)


class RegisteredIdTests(GateCase):
    """G3: routing ids are looked up literally in the sealed configs."""
    def floor_line(self, cell_id, pack="alpha"):
        line = next(line for line in self.files[DISCLOSURE]["floors"] if line["line"] == "floor_composition")
        line.update(pack=pack, cell_id=cell_id)
        return line

    def test_typo_cell_id_refuses_b7_sol3(self):
        self.floor_line("TYPO-d117-df-ph-decode-qwen3-1p7b-absolute")
        self.refused("routing_id_unregistered:disclosure:floors/*/cell_id")
        # Without the gate the literal lookup still finds no cell: the leaf is unbound, never routed by its parts.
        with mock.patch.object(cmp, "gate", lambda *args: None):
            code, _, out = self.exit_code(CODED)
        self.assertEqual(code, 2)
        self.assertIn(("disclosure:floors/floor_composition/guarded_j", "key_unresolved"),
                      {(u["path"], u["reason"]) for u in out["coverage"]["unbound"]})

    def test_suffixed_spellings_refuse(self):
        for cell_id in ("d117-df-ph-decode-qwen3-1p7b-absolute-TYPO", "d117-df-ph-decode-qwen3-1p7b-comparative",
                        "d117-reported-mean-ph-decode-qwen3-1p7b"):
            with self.subTest(cell_id):
                self.setUp()
                self.floor_line(cell_id)
                self.refused("routing_id_unregistered:disclosure:floors/*/cell_id")

    def test_both_registered_spellings_bind_a7_a8(self):
        result = self.shipped()
        bound = {row["key"] for row in result["comparisons"] if row["family"] == "floor_j"}
        for key in ("Qwen3-1.7B-4bit/decode/absolute/guarded_floor_j", "Qwen3-1.7B-4bit/decode/comparative/guarded_floor_j"):
            self.assertIn(key, bound)
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))

    def test_a_cell_registered_for_another_window_refuses(self):
        self.floor_line("d117-df-cmp-abba-ph-decode-qwen3-8b", pack="alpha")
        self.refused("routing_id_unregistered:disclosure:floors/*/cell_id")

    def test_unregistered_pack_refuses(self):
        self.files[DISCLOSURE]["window_lines"]["alpha"][0]["pack"] = "delta"
        self.refused("routing_id_unregistered:disclosure:window_lines/alpha/*/pack")

    def test_l9_family_inputs_route_by_registered_ids(self):
        # The extraction report's lane-fixture spelling of 7fede8c7 (consult side finding) is not registered.
        self.files[EXTRACTION]["cells"][1]["cell_id"] = "d117-df-ph-decode-qwen3-1p7b-comparative"
        self.refused("routing_id_unregistered:extraction_cell:alpha")
        self.setUp()
        self.files[EXTRACTION]["cells"][0]["cell_id"] = "d117-df-ph-decode-qwen3-8b-absolute"
        self.refused("routing_id_unregistered:extraction_cell:alpha")
        self.setUp()
        self.files[f"mint/{SHA}-aggregate-floor.json"]["cells"][0]["cell_id"] = "d117-qwen3-1p7b-decode-floor-v6"
        self.refused("routing_id_unregistered:aggregate_cell")

    def test_an_unregistered_source_cell_id_is_no_cell(self):
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["resolutions"][0]["source_cell_ids"] = ["d117-qwen3-1p7b-decode-floor-v5-TYPO"]
        result = self.shipped()
        self.assertEqual(self.fails(result), {"routing_id": 1})


class RegistryTests(unittest.TestCase):
    """G3: the table is the sealed configs' own fields, pinned by digest."""
    def test_table_from_the_sealed_configs(self):
        registry = cmp.load_registry()
        self.assertEqual(set(registry.digests), set(cmp.REGISTRY_PINS))
        tables = registry.tables
        self.assertEqual(len(tables["extraction"]), 12)
        self.assertEqual(cmp.floor_key(tables["extraction"]["d117-df-cmp-abba-ph-decode-qwen3-1p7b"]),
                         "Qwen3-1.7B-4bit/decode/comparative")
        self.assertEqual(cmp.floor_key(tables["extraction"]["d117-df-ph-prefill-p2048-qwen3-8b-absolute"]),
                         "Qwen3-8B-4bit/prefill/absolute")
        self.assertEqual({cid for cid, e in tables["extraction"].items() if e["p42"]},
                         {f"d117-df-{k}ph-prefill-p42-{m}{s}" for m in ("qwen3-1p7b", "qwen3-8b")
                          for k, s in (("", "-absolute"), ("cmp-abba-", ""))})
        self.assertEqual({cid: e["family"] for cid, e in tables["reported"].items()},
                         {f"d117-reported-mean-ph-{p}-{m}": f"df-ph-{p}-{m}" for m in ("qwen3-1p7b", "qwen3-8b")
                          for p in ("decode", "prefill-p42", "prefill-p2048")})
        self.assertEqual(tables["contrast"][DECODE]["conditions"], ("sw-decode-a-qwen3-1p7b", "sw-decode-b-qwen3-8b"))
        self.assertEqual(tables["contrast"][PREFILL]["phase"], "prefill")
        self.assertEqual({cid: (e["pack"], e["phase"]) for cid, e in tables["floor"].items()},
                         {"d117-qwen3-1p7b-decode-floor-v5": ("alpha", "decode"),
                          "d117-qwen3-8b-decode-floor-v5": ("beta", "decode"),
                          "d117-qwen3-1p7b-prefill-p2048-floor-v5": ("alpha", "prefill"),
                          "d117-qwen3-8b-prefill-p2048-floor-v5": ("beta", "prefill")})
        self.assertEqual(registry.families("alpha", True), {"df-ph-prefill-p42-qwen3-1p7b"})

    def test_a_spec_edit_changes_the_table_and_the_pin_refuses_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "campaigns"
            for name in cmp.REGISTRY_PINS:
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(cmp.CAMPAIGNS / name, root / name)
            spec = root / cmp.EXTRACTION_SPECS["alpha"]
            spec.write_text(spec.read_text().replace("d117-df-cmp-abba-ph-decode-qwen3-1p7b", "d117-df-cmp-abba-ph-decode-renamed"))
            with self.assertRaisesRegex(cmp.Refusal, "routing_registry_digest_differs"):
                cmp.load_registry(root, dict(cmp.REGISTRY_PINS))
            pins = dict(cmp.REGISTRY_PINS, **{cmp.EXTRACTION_SPECS["alpha"]: hashlib.sha256(spec.read_bytes()).hexdigest()})
            edited = cmp.load_registry(root, pins)
            self.assertIn("d117-df-cmp-abba-ph-decode-renamed", edited.tables["extraction"])
            self.assertNotIn("d117-df-cmp-abba-ph-decode-qwen3-1p7b", edited.tables["extraction"])

    def test_no_id_is_parsed_for_its_parts(self):
        source = (ROOT / "scripts/compare_b5_recompute.py").read_text()
        tree = ast.parse(source)
        names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertFalse(names & {"cell_phase", "cell_model", "floor_kind", "floor_cell_key", "reported_key",
                                  "reported_cid", "pack_of_cell", "aggregate_key", "arm_condition", "tag"})
        for text in ('"p42" in', '"decode" in', 'endswith("-" +', '.replace("d117-reported-mean-ph-"', 'endswith("qwen3'):
            self.assertNotIn(text, source)


class ExemptionTests(GateCase):
    """G5: named exemptions are enumerated leaf names, and the restricted output lists them."""
    def test_no_rule_takes_a_field_at_any_depth(self):
        for rule in cmp.COVERAGE:
            self.assertNotIn("(.*/)?", rule[0])
            if len(rule) == 2 and rule[1] in (cmp.IDENTITY, cmp.IDENTITY_NUMBER, cmp.TEXT):
                self.assertNotIn(".*", rule[0], rule)
        broad = [rule[0] for rule in cmp.COVERAGE if len(rule) == 2
                 and rule[1].startswith((cmp.NAMED, cmp.NULL_NAMED)) and ".*" in rule[0]]
        # The one numeric subtree no review named (load-correlated values) stays for the full-size census
        # (report, open issues); RC-CMP-7 F2 enumerated the hazard measurements (HAZARD).
        self.assertEqual(len(broad), 1, broad)

    def test_attempt_anywhere_refuses_q5a(self):
        self.files[FILL]["gamma"]["contrasts"][0]["floor_attempt"] = {"attempt": 87.25}
        self.assertIn("fill:gamma/contrasts/*/floor_attempt/attempt", self.shipped()["coverage"]["unmapped"])

    def test_numbers_under_equivalence_refuse_q5b(self):
        self.files[FILL]["gamma"]["contrasts"][0]["equivalence"] = {"margin_j": 87.25, "anything": {"x": 1.5}}
        unmapped = self.shipped()["coverage"]["unmapped"]
        self.assertTrue({"fill:gamma/contrasts/*/equivalence/margin_j", "fill:gamma/contrasts/*/equivalence/anything/x"}
                        <= set(unmapped))

    def test_numbers_under_floor_diagnostics_refuse_sol(self):
        for field, value in (("point_floor_diagnostics", {"active_floor_j": 999999.0}),
                             ("single_count_discipline", {"estimate": 999999.0})):
            with self.subTest(field):
                self.setUp()
                self.files[FILL]["gamma"]["contrasts"][0]["floor"][field] = value
                self.assertEqual(len(self.shipped()["coverage"]["unmapped"]), 1)
        self.setUp()
        self.files[FILL]["gamma"]["contrasts"][0]["floor"]["point_floor_diagnostics"] = {
            "label": "diagnostic", "published_claim_floor": False, "unguarded_floor_j": 1.0, "guard_factor": 1.0,
            "guarded_floor_j": 1.0}
        result = self.shipped()
        self.assertEqual(result["coverage"]["unmapped"], [])
        self.assertIn("fill:gamma/contrasts/*/floor/point_floor_diagnostics/guarded_floor_j",
                      result["coverage"]["uncovered_numeric"])

    def test_named_exemptions_are_listed_by_rule(self):
        out = self.exit_code(CODED)[2]["coverage"]
        listed = {path for paths in out["named_exemptions"].values() for path in paths}
        self.assertEqual(listed, set(out["uncovered_numeric"]))
        self.assertIn("fill:gamma/contrasts/*/sampling/planned_n", listed)
        self.assertIn("fill:characterization/verdict", listed)
        self.assertIn("fill:campaigns/alpha/attempt", listed)

    def test_producer_fields_that_7fede8c7_refused_are_named(self):
        # build_results_fill_input writes an integer attempt per campaign; the adapter's default
        # characterization verdict is null. 7fede8c7 refused both (strings-only subtree rules).
        leaves = self.shipped()["coverage"]["leaves"]
        self.assertTrue(leaves["fill:campaigns/alpha/attempt"].startswith(cmp.NAMED))
        self.assertTrue(leaves["fill:characterization/verdict"].startswith(cmp.NULL_NAMED))


class NumericWordTests(GateCase):
    """Opus round-3 F3: a string spelling a number is numeric-class outside the text and identity rules."""
    def test_numeric_string_under_a_word_rule_refuses_q1b_q1e(self):
        self.files[FILL]["campaigns"]["gamma"] = {"gross_energy_j": "123.4"}
        self.assertIn("fill:campaigns/gamma/gross_energy_j", self.shipped()["coverage"]["unmapped"])
        self.setUp()
        self.files[DISCLOSURE]["window_lines"]["alpha"].append(
            {"line": "host_cpu", "restricted": False, "label": "host_cpu", "text": "x", "value_s": 1.5,
             "value_text_s": "0.93"})
        # RC-CMP-7 F2: the producer writes no value_text_s on a host_cpu line, so the line gate refuses first;
        # the coverage layer behind it (the gate switched off) still refuses the numeric spelling.
        with self.assertRaisesRegex(cmp.Refusal, "line_key_unregistered:disclosure:window_lines/host_cpu/value_text_s"):
            self.shipped()
        self.enterContext(mock.patch.object(cmp, "gate_lines", lambda record: None))
        self.assertEqual(self.shipped()["coverage"]["unmapped"], ["disclosure:window_lines/alpha/host_cpu/value_text_s"])
        # RC-CMP-7 F2: no rule names value_text_s now (the window_lines/.* subtree is enumerated), so even read as
        # a word it stays unmapped. A numeric spelling at an enumerated word leaf still refuses as a number:
        with mock.patch.object(cmp, "numeric_word", lambda value: False):
            self.assertEqual(self.shipped()["coverage"]["unmapped"], ["disclosure:window_lines/alpha/host_cpu/value_text_s"])
        self.setUp()
        next(r for r in self.files[DISCLOSURE]["window_lines"]["alpha"] if r["line"] == "stored_status")["status"] = "0.93"
        self.assertEqual(self.shipped()["coverage"]["unmapped"], ["disclosure:window_lines/alpha/stored_status/status"])
        # Counterfactual: by JSON type only (7fede8c7), the string passes as a word.
        with mock.patch.object(cmp, "numeric_word", lambda value: False):
            self.assertEqual(self.shipped()["coverage"]["unmapped"], [])

    def test_numeric_string_under_a_named_rule_is_listed_q1d(self):
        self.files[DISCLOSURE]["window_lines"]["alpha"].append(
            {"line": "battery_discharged", "restricted": True, "label": "battery_discharged", "text": "x", "value_j": "41.7"})
        result = self.shipped()
        self.assertEqual(result["coverage"]["unmapped"], [])
        self.assertIn("disclosure:window_lines/alpha/battery_discharged/value_j", result["coverage"]["uncovered_numeric"])

    def test_text_and_identity_keep_numeric_spellings(self):
        line = next(line for line in self.files[DISCLOSURE]["contrasts"] if line["line"] == "loo_counts")
        line.update(text="3", exclusive_block_numbers=["3", "10"])
        self.files[DISCLOSURE]["windows"]["alpha"]["harvest_pin"] = "1234567"
        self.assertEqual(self.shipped()["coverage"]["unmapped"], [])

    def test_spellings(self):
        for word in ("1", "-1.25", "1E0", "1e-3", ".5", "NaN", "Infinity", " 2 ", "+3"):
            self.assertTrue(cmp.numeric_word(word), word)
        for word in ("b03", "0" * 64, "a1b2c3d", "", "1.2.3", "qwen3-8b", "-"):
            self.assertFalse(cmp.numeric_word(word), word)


class ConsultControlTests(GateCase):
    """The consult's controls A1-A8: what L9 writes is accepted."""
    def test_registered_null_j_per_token_a2(self):
        self.assertIsNone(self.files[FILL]["gamma"]["contrasts"][0]["j_per_token"])
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_keyed_lists_in_another_order_a3(self):
        self.files[FILL]["gamma"]["contrasts"].reverse()
        self.files[VERDICTS]["contrasts"].reverse()
        self.files[DISCLOSURE]["contrasts"].reverse()
        self.files[DISCLOSURE]["floors"].reverse()
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_v3_arm_gates_and_resolutions_a4(self):
        v3_floor(self)
        self.assertEqual(self.exit_code(CODED)[0], 0)

    def test_refused_arm_gate_printed_null_a5_opus_q6(self):
        # The gate accepts the shape; the comparison of a null gate is the ruling Opus named (open issue).
        verdict, fill = v3_floor(self)
        for floor in (verdict, fill):
            floor["arm_gates"][1].update(status="refused", floor_gate_j=None)
        self.ours["floor_cells"]["Qwen3-8B-4bit/decode"]["floor_gate_j"] = None
        cmp.gate(self.files[FILL], "fill", cmp.load_registry())
        code, err, _ = self.exit_code(CODED)
        self.assertEqual((code, err), (2, "refused=step11_unmapped_fill\n"))


class MeterGateTests(MeterCase):
    """The producer-shaped machine lines pass the gate; a member line's nested run_id refuses."""
    def test_machine_lines_pass_the_gate(self):
        result = self.compare()
        self.assertEqual((self.fails(result), result["coverage"]["unmapped"]), ({}, []))

    def test_nested_run_id_refuses(self):
        self.lines()[0]["machine"] = {"run_id": "other", "delta_J": 1.0}
        with self.assertRaisesRegex(cmp.Refusal, "identity_field_misplaced:disclosure:window_lines/alpha/\\*/machine/run_id"):
            self.compare()


if __name__ == "__main__":
    unittest.main()
