"""D-176 plan-root regressions; all records and checkouts are fixtures."""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.night_gate import NightPlan, PlanError
from joulewise.night_plan_writer import (
    night_plan_json_bytes, night_plan_mapping, write_night_plan,
)
from scripts import magistrate_watchdog


class NightPlanWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.plan = NightPlan(
            plan_id="pack-night-test", receipt_class="TRANSACTION_PACK",
            t0_epoch_s=1000.0, window_max_s=60, authored_epoch_s=900.0,
            repo_head="a" * 40, measurement_root=str(self.root / "measurement"),
            measurement_head="b" * 40, chain_path=str(self.custody / "chain.zsh"),
            chain_sha256_path=str(self.custody / "chain.sha256"),
            custody_root=str(self.custody), registration_path=None,
            pack_night={
                "pack_id": "pack-test", "pack_sha256": "c" * 64,
                "attempt_ordinal": 7,
                "authorization_record": {
                    "path": str(self.custody / "authorization.json"), "sha256": "d" * 64,
                },
                "confirmation_record": {
                    "path": str(self.custody / "step6_confirmation_record.json"), "sha256": "e" * 64,
                },
            },
        )

    def test_pack_v3_exact_keys_and_persisted_attempt_round_trip(self) -> None:
        mapping = night_plan_mapping(self.plan)
        self.assertEqual({
            "schema", "schema_version", "plan_id", "receipt_class", "t0_epoch_s",
            "window_max_s", "authored_epoch_s", "repo_head", "measurement_root",
            "measurement_head", "chain_path", "chain_sha256_path", "custody_root",
            "registration_path", "pack_night",
        }, set(mapping))
        self.assertEqual("joulewise.night_plan.v3", mapping["schema"])
        self.assertIs(type(mapping["schema_version"]), int)
        self.assertEqual(3, mapping["schema_version"])
        self.assertEqual({
            "pack_id", "pack_sha256", "attempt_ordinal",
            "authorization_record", "confirmation_record",
        }, set(mapping["pack_night"]))
        path = write_night_plan(self.custody / "night_plan.json", self.plan)
        raw = path.read_bytes()
        self.assertEqual(0o600, path.stat().st_mode & 0o777)
        self.assertEqual(night_plan_json_bytes(self.plan), raw)
        self.assertTrue(raw.endswith(b"\n"))
        loaded = NightPlan.from_mapping(json.loads(raw))
        self.assertEqual(self.plan, loaded)
        self.assertEqual(7, loaded.pack_night["attempt_ordinal"])
        self.assertEqual(raw, night_plan_json_bytes(loaded))
        changed = dataclasses.replace(loaded, pack_night={**loaded.pack_night, "attempt_ordinal": 8})
        self.assertNotEqual(hashlib.sha256(raw).digest(), hashlib.sha256(night_plan_json_bytes(changed)).digest())

    def test_pack_binding_required_iff_pack_and_v2_stays_exact(self) -> None:
        for receipt_class in ("DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"):
            plan = dataclasses.replace(self.plan, receipt_class=receipt_class,
                                       pack_night=None, registration_path="registration.json")
            mapping = night_plan_mapping(plan)
            self.assertEqual("joulewise.night_plan.v2", mapping["schema"])
            self.assertEqual(2, mapping["schema_version"])
            self.assertNotIn("pack_night", mapping)
            self.assertEqual(plan, NightPlan.from_mapping(mapping))
            for binding in (None, self.plan.pack_night):
                with self.subTest(receipt_class=receipt_class, binding=binding):
                    with self.assertRaises(PlanError):
                        NightPlan.from_mapping({**mapping, "pack_night": binding})
            with self.assertRaises(PlanError):
                night_plan_mapping(dataclasses.replace(plan, pack_night=self.plan.pack_night))
        mapping = night_plan_mapping(self.plan)
        for changes in (
            {"schema": "joulewise.night_plan.v2", "schema_version": 2},
            {"schema_version": True}, {"schema_version": 3.0},
            {"pack_night": None}, {"pack_night": {}}, {"unexpected": 1},
        ):
            with self.subTest(changes=changes), self.assertRaises(PlanError):
                NightPlan.from_mapping({**mapping, **changes})
        del mapping["pack_night"]
        with self.assertRaises(PlanError):
            NightPlan.from_mapping(mapping)

    def test_pack_nested_keys_types_and_digests_fail_closed(self) -> None:
        baseline = night_plan_mapping(self.plan)
        mutations = [
            ("pack_id", value) for value in ("", None, 3, True)
        ] + [
            ("pack_sha256", value) for value in ("F" * 64, "0" * 63, "a" * 64 + "\n", None)
        ] + [
            ("attempt_ordinal", value) for value in (True, False, 0, -1, 1.0, "1", None)
        ]
        for key, value in mutations:
            mapping = copy.deepcopy(baseline)
            mapping["pack_night"][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(PlanError):
                NightPlan.from_mapping(mapping)
        for key in baseline["pack_night"]:
            mapping = copy.deepcopy(baseline)
            del mapping["pack_night"][key]
            with self.subTest(missing=key), self.assertRaises(PlanError):
                NightPlan.from_mapping(mapping)
        mapping = copy.deepcopy(baseline)
        mapping["pack_night"]["extra"] = 1
        with self.assertRaises(PlanError):
            NightPlan.from_mapping(mapping)
        for name in ("authorization_record", "confirmation_record"):
            good = baseline["pack_night"][name]
            for record in (None, {}, {"path": good["path"]}, {"sha256": good["sha256"]},
                           {**good, "extra": 1}, {**good, "sha256": "X" * 64},
                           {**good, "sha256": True}, {**good, "path": 1}):
                mapping = copy.deepcopy(baseline)
                mapping["pack_night"][name] = record
                with self.subTest(name=name, record=record), self.assertRaises(PlanError):
                    NightPlan.from_mapping(mapping)

    def test_both_record_locators_must_resolve_inside_custody(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (self.custody / "escape").symlink_to(outside, target_is_directory=True)
        for name in ("authorization_record", "confirmation_record"):
            for path in ("relative.json", str(self.custody), str(outside / "record.json"),
                         str(self.custody / ".." / "record.json"),
                         str(self.custody / "escape" / "record.json")):
                mapping = night_plan_mapping(self.plan)
                mapping["pack_night"][name]["path"] = path
                with self.subTest(name=name, path=path), self.assertRaises(PlanError):
                    NightPlan.from_mapping(mapping)
        with self.assertRaises(PlanError):
            night_plan_mapping(dataclasses.replace(self.plan, custody_root="relative"))

    def test_validated_mapping_does_not_alias_caller_record_bindings(self) -> None:
        mapping = night_plan_mapping(self.plan)
        parsed = NightPlan.from_mapping(mapping)
        mapping["pack_night"]["authorization_record"]["sha256"] = "f" * 64
        self.assertEqual("d" * 64, parsed.pack_night["authorization_record"]["sha256"])
        self.assertEqual("d" * 64, self.plan.pack_night["authorization_record"]["sha256"])

    def test_invalid_plan_does_not_replace_existing_armed_bytes(self) -> None:
        path = write_night_plan(self.custody / "night_plan.json", self.plan)
        original = path.read_bytes()
        invalid = dataclasses.replace(self.plan, pack_night={**self.plan.pack_night, "attempt_ordinal": 0})
        with self.assertRaises(PlanError):
            write_night_plan(path, invalid)
        self.assertEqual(original, path.read_bytes())
        self.assertEqual([path], list(self.custody.iterdir()))

    def test_watchdog_reads_real_v3_plan_without_mutation(self) -> None:
        path = write_night_plan(self.custody / "night_plan.json", self.plan)
        original = path.read_bytes()
        storage = mock.Mock(spec=magistrate_watchdog.Storage)
        storage.glob_plans.return_value = [path]
        storage.read_text.side_effect = lambda candidate: candidate.read_text(encoding="utf-8")
        snapshot = magistrate_watchdog.load_plans(storage, now_epoch_s=1000.0)
        self.assertEqual((self.plan,), snapshot.plans)
        self.assertEqual((), snapshot.errors)
        self.assertEqual((), snapshot.diagnostics)
        self.assertEqual(original, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
