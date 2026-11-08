"""Prospective protocol checks; all identities and cohorts below are synthetic."""
from copy import deepcopy
from pathlib import Path
import unittest

from joulewise.align.squeeze.config import seal
from joulewise.align.squeeze.redteam import (
    load_catalog, seed_manifest, blind_manifest, freeze_redteam, verify_freeze,
    select_candidate, select_from_freeze,
)

CATALOG = Path(__file__).resolve().parents[2] / "configs/align/squeeze/redteam/variants.json"


class ProtocolTests(unittest.TestCase):
    def manifest(self):
        return seed_manifest("synthetic-8bit", [
            {"pair": "shade/bank_transfer_2", "index": 1, "role": "development"},
            {"pair": "shade/bank_transfer_2", "index": 2, "role": "calibration"},
            {"pair": "shade/bank_transfer_2", "index": 3, "role": "test"},
        ], assignment_seed=12, blinding_seed=13)

    def freeze(self):
        catalog = load_catalog(CATALOG)
        return freeze_redteam(catalog, self.manifest(),
            bindings={key: "a" * 64 for key in (
                "v4_configuration_sha256", "protocol_sha256", "runner_sha256",
                "monitor_policy_sha256", "energy_policy_sha256")},
            frozen_at="2026-11-08T00:00:00Z", d_not_before="2026-11-09T00:00:00Z",
            search_policy={"candidate_ids": [catalog["classes"]["A2"]["variant"]["id"]],
                           "probe_cap": 1, "objective": "joint_uncaught_success_per_attempt"})

    def test_all_authoritative_classes_have_hashed_variants_and_explicit_limits(self):
        catalog = load_catalog(CATALOG)
        self.assertEqual(set(catalog["classes"]), {f"A{i}" for i in range(14)})
        self.assertEqual(catalog["classes"]["A6"]["mechanism"], "tool_subprocess")
        self.assertEqual(catalog["classes"]["A11"]["scope"], "out_of_scope")
        self.assertEqual(catalog["classes"]["A13"]["scope"], "out_of_scope")
        for entry in catalog["classes"].values():
            self.assertTrue(entry["predicted_catcher"])
            self.assertTrue(entry["h50_prediction"]["reason"])
            self.assertEqual(entry["variant"], seal(entry["variant"]))

    def test_v4_seed_law_and_reserved_development_indices(self):
        import hashlib
        import json
        row = self.manifest()["rows"][1]
        expected = int.from_bytes(hashlib.sha256(json.dumps(
            ["align-p4-v1", "synthetic-8bit", "thinking_on", "shade/bank_transfer_2", 2],
            separators=(",", ":"), ensure_ascii=True).encode()).digest()[:8], "big")
        self.assertEqual(row["episode_seed"], expected)
        for index in (1, 91, 99):
            with self.assertRaises(ValueError):
                seed_manifest("synthetic", [{"pair": "shade/bank_transfer_2",
                    "index": index, "role": "test"}], assignment_seed=1, blinding_seed=2)
        rows = [{"pair": "shade/bank_transfer_2", "index": 2, "role": role}
                for role in ("calibration", "test")]
        with self.assertRaisesRegex(ValueError, "reuse"):
            seed_manifest("synthetic", rows, assignment_seed=1, blinding_seed=2)

    def test_blinded_projection_has_no_arm_seed_truth_or_dose_and_is_reproducible(self):
        public, private = blind_manifest(self.manifest())
        self.assertEqual((public, private), blind_manifest(self.manifest()))
        self.assertEqual(set(public), {"schema", "ids"})
        self.assertEqual(len(set(public["ids"])), 3)
        self.assertEqual(set(public["ids"]), set(private))
        self.assertEqual({v["index"] for v in private.values()}, {1, 2, 3})

    def test_freeze_is_external_digest_bound_and_strictly_before_D(self):
        receipt = self.freeze()
        verify_freeze(receipt, expected_sha256=receipt["config_sha256"],
                      catalog=load_catalog(CATALOG), manifest=self.manifest())
        with self.assertRaises(ValueError):
            verify_freeze(receipt, expected_sha256=receipt["config_sha256"],
                catalog=load_catalog(CATALOG), manifest=self.manifest(),
                actual_d_start="2026-11-08T00:00:00Z")
        bad = deepcopy(receipt)
        bad["bindings"]["v4_configuration_sha256"] = "b" * 64
        with self.assertRaises(ValueError):
            verify_freeze(seal(bad), expected_sha256=receipt["config_sha256"],
                          catalog=load_catalog(CATALOG), manifest=self.manifest())
        for stamp in ("2026-11-09T00:00:00Z", "2026-11-10T00:00:00Z", "2026-11-08"):
            bad = deepcopy(receipt)
            bad["frozen_at"] = stamp
            with self.assertRaises(ValueError):
                verify_freeze(seal(bad), expected_sha256=seal(bad)["config_sha256"],
                              catalog=load_catalog(CATALOG), manifest=self.manifest())

    def test_resealed_seed_tampering_and_catalog_mutation_are_refused(self):
        receipt = self.freeze()
        manifest = self.manifest()
        manifest["rows"][0]["episode_seed"] += 1
        with self.assertRaises(ValueError):
            freeze_redteam(load_catalog(CATALOG), seal(manifest),
                bindings=receipt["bindings"], frozen_at=receipt["frozen_at"],
                d_not_before=receipt["d_not_before"], search_policy=receipt["search_policy"])
        catalog = load_catalog(CATALOG)
        catalog["classes"]["A4"]["variant"]["instructions"] += "changed"
        with self.assertRaises(ValueError):
            verify_freeze(receipt, expected_sha256=receipt["config_sha256"],
                          catalog=seal(catalog), manifest=self.manifest())

    def test_search_budget_and_candidate_set_are_bound_by_the_external_freeze(self):
        receipt = self.freeze()
        row = {"candidate": receipt["search_policy"]["candidate_ids"][0],
               "pair": "shade/bank_transfer_2", "index": 1, "role": "development",
               "success": True, "energy_alarm": False, "monitor_alarm": False}
        self.assertEqual(select_from_freeze([row], receipt=receipt,
            expected_sha256=receipt["config_sha256"], catalog=load_catalog(CATALOG),
            manifest=self.manifest()), row["candidate"])
        bad = deepcopy(receipt)
        bad["search_policy"]["probe_cap"] = 2
        with self.assertRaises(ValueError):
            select_from_freeze([row], receipt=seal(bad), expected_sha256=receipt["config_sha256"],
                catalog=load_catalog(CATALOG), manifest=self.manifest())

    def test_adaptation_uses_attempt_denominator_and_no_test_feedback(self):
        manifest = seed_manifest("synthetic", [
            {"pair": "shade/bank_transfer_2", "index": i, "role": role}
            for i, role in ((1, "development"), (91, "development"), (2, "test"))
        ], assignment_seed=1, blinding_seed=2)
        rows = [{"candidate": c, "role": "development", "success": s,
                 "pair": "shade/bank_transfer_2", "index": index,
                 "energy_alarm": e, "monitor_alarm": m}
                for c, index, s, e, m in (("a", 1, True, False, False),
                                  ("a", 91, False, False, False),
                                  ("b", 1, True, False, False),
                                  ("b", 91, True, True, False))]
        kwargs = dict(probe_cap=2, manifest=manifest, candidates=["a", "b"])
        self.assertEqual(select_candidate(rows, **kwargs), "a")  # tied escape rate; stable ID
        rows[0]["role"] = "test"
        with self.assertRaises(ValueError):
            select_candidate(rows, **kwargs)
        rows[0]["role"] = "development"
        rows[0]["index"] = 2  # relabelled held-out feedback is still refused
        with self.assertRaises(ValueError):
            select_candidate(rows, **kwargs)
        rows[0]["index"] = 1
        rows[0]["energy_alarm"] = None
        with self.assertRaises(ValueError):
            select_candidate(rows, **kwargs)
        rows[0]["energy_alarm"] = False
        with self.assertRaises(ValueError):
            select_candidate(rows[1:], **kwargs)
        with self.assertRaises(ValueError):
            select_candidate(rows, **{**kwargs, "candidates": ["a", "b", "missing"]})
        with self.assertRaises(ValueError):
            select_candidate(rows + [rows[0]], **kwargs)


if __name__ == "__main__":
    unittest.main()
