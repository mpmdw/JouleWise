import json
import unittest

from build_qual_pin_kits import (
    AUDIT, BASE, IDS, OUTPUT, SECTION, SEED_START, STABILITY, digest, manifest_with_rows,
)
from validate_kit import validate_cells


class QualPinKitsTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads((OUTPUT / "VERIFICATION.json").read_bytes())
        self.base = json.loads(BASE.read_bytes())
        self.queue_template = json.loads((STABILITY / "queues" / "f2-stab-01.json").read_bytes())

    def test_generated_kits_match_cells_and_bind_all_one_leg_artifacts(self):
        self.assertEqual(tuple(row["kit"] for row in self.evidence["kits"]), IDS)
        for row in self.evidence["kits"]:
            name = row["kit"]
            with self.subTest(kit=name):
                kit_path = OUTPUT / f"{name}.v1.1.json"
                raw = kit_path.read_bytes()
                kit = json.loads(raw)
                self.assertEqual(row["sha256"], digest(raw))
                self.assertEqual(kit["frozen"]["commit"], self.evidence["pin"])
                self.assertEqual(kit["frozen"]["paths"].keys(), self.base["frozen"]["paths"].keys())
                validate_cells({**kit, "frozen": self.base["frozen"]}, self.base)
                self.assertEqual(kit["seed_law"]["master_seed"], row["master_seed"])
                self.assertEqual(row["candidates_tested"], row["master_seed"] - SEED_START + 1)
                self.assertEqual(row["validate_kit"]["kit_sha256"], row["sha256"])
                self.assertTrue(row["validate_kit"]["frozen_paths_verified"])

                queue_raw = (OUTPUT / "queues" / f"{name}.json").read_bytes()
                queue = json.loads(queue_raw)
                self.assertEqual(row["queue_sha256"], digest(queue_raw))
                self.assertEqual(queue["queue_id"], f"cq-{name}")
                self.assertEqual(queue["expires_at"], self.evidence["expires_at"])
                self.assertEqual(row["validate_queue"]["spans"], 12)
                self.assertEqual(len(queue["spans"]), 12)
                item = (OUTPUT / "items" / f"ITEM-{name}.md").read_text(encoding="utf-8")
                self.assertEqual(item.count("\n## "), 12)
                for original, span, leg, plan in zip(
                    self.queue_template["spans"], queue["spans"], kit["legs"], row["plans"], strict=True,
                ):
                    self.assertEqual(span["legs"], [leg["leg_id"]])
                    self.assertEqual(span["span_id"], f"{name}-{leg['leg_id'].lower()}")
                    self.assertEqual(span["block_id"], name)
                    self.assertEqual(span["kit"], {
                        "path": kit_path.relative_to(AUDIT).as_posix(), "sha256": row["sha256"],
                    })
                    for key in ("seq", "attempt", "not_before"):
                        self.assertEqual(span[key], original[key])
                    self.assertEqual(plan["span_id"], span["span_id"])
                    self.assertEqual(plan["legs"], span["legs"])
                    self.assertIn(f"\n## {span['span_id']}\n", item)
                    self.assertIn(f"Roster `{leg['leg_id']}`", item)
                self.assertEqual(item.count(row["sha256"]), 12)
                self.assertEqual(item.count(self.evidence["pin"]), 12)
                self.assertEqual(row["mock"], {"leg_id": "L001", "rc": 0, "legs": 1, "stops": []})

    def test_manifest_regeneration_preserves_existing_sections(self):
        existing = (STABILITY / "MANIFEST.md").read_text(encoding="utf-8")
        original, marker, _ = existing.partition(SECTION)
        self.assertEqual(marker, SECTION)
        self.assertEqual(manifest_with_rows(original, self.evidence["kits"], self.evidence["pin"]), existing)
        self.assertEqual(manifest_with_rows(existing, self.evidence["kits"], self.evidence["pin"]), existing)
        with self.assertRaisesRegex(ValueError, "must be last"):
            manifest_with_rows(existing + "\n## Another section\n", self.evidence["kits"], self.evidence["pin"])


if __name__ == "__main__":
    unittest.main()
