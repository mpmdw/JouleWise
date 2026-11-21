import json
import re
import unittest

from build_qual_pin_kits import AUDIT, digest
from build_successor_kits import (
    EXPIRES, INDEX, NOT_BEFORE, ROSTERS, W2, W3, intake_blob, kit_seeds, reserved_seeds,
    single_position_queues,
)
from validate_kit import validate_cells


class SuccessorKitsTests(unittest.TestCase):
    def test_index_preserves_base_and_predecessors_and_binds_new_kit_bytes(self):
        original = json.loads(intake_blob(INDEX))
        index = json.loads((AUDIT / INDEX).read_bytes())
        self.assertEqual(index["base_kits"], original["base_kits"])
        self.assertEqual(index["rows"][:16], original["rows"])
        new_rows = index["rows"][16:]
        self.assertEqual([row["kit_id"] for row in new_rows], [f"f2-stab-{n:02d}" for n in range(17, 54)])
        references = {row["kit_id"]: row for row in original["rows"]}
        rows = {row["kit_id"]: row for row in new_rows}
        reserved = reserved_seeds()
        for predecessor, numbers in ROSTERS:
            reference = references[predecessor]
            base = json.loads(intake_blob(reference["path"]))
            for number in numbers:
                name = f"f2-stab-{number:02d}"
                with self.subTest(kit=name):
                    row = rows[name]
                    raw = (AUDIT / row["path"]).read_bytes()
                    self.assertEqual(row["runner_pin"], reference["runner_pin"])
                    self.assertEqual(row["sha256"], digest(raw))
                    kit = json.loads(raw)
                    self.assertEqual(kit["campaign_id"], name)
                    validate_cells(kit, base)
                    seeds = kit_seeds(kit)
                    self.assertEqual(len(seeds), 13)
                    self.assertFalse(seeds & reserved)
                    reserved.update(seeds)

    def test_single_position_queue_retains_w2_span_ordinal_and_plan_identity(self):
        template = json.loads(intake_blob(W2 / "queues-1leg/f2-stab-14.json"))
        row = {"kit_id": "f2-stab-17", "path": "kits/f2-stab-17.json", "sha256": "a" * 64}
        queues = list(single_position_queues(template, row, "2026-11-26"))
        self.assertEqual(len(queues), 12)
        for index, (path, raw) in enumerate(queues, 1):
            span_id = f"f2-stab-17-l{index:03d}"
            self.assertEqual(path.name, f"{span_id}.json")
            queue = json.loads(raw)
            self.assertEqual(queue["queue_id"], f"cq-{span_id}")
            self.assertEqual(queue["expires_at"], EXPIRES)
            self.assertEqual(queue["spans"], [{
                "seq": index, "span_id": span_id, "block_id": row["kit_id"],
                "kit": {key: row[key] for key in ("path", "sha256")},
                "legs": [f"L{index:03d}"], "attempt": 1, "not_before": "2026-11-26",
            }])

    def test_published_queues_match_index_and_readme_digests(self):
        root = AUDIT / W3
        readme = (root / "README.md").read_text(encoding="utf-8")
        declared = re.findall(r"^\| \[[^\]]+\]\((queues-1leg/[^)]+)\) \| `([a-f0-9]{64})` \|$",
                              readme, flags=re.MULTILINE)
        rows = json.loads((AUDIT / INDEX).read_bytes())["rows"][16:]
        verified = {}
        for row in rows:
            for position in range(1, 13):
                span_id = f"{row['kit_id']}-l{position:03d}"
                name = f"queues-1leg/{span_id}.json"
                with self.subTest(queue=name):
                    raw = (root / name).read_bytes()
                    verified[name] = digest(raw)
                    queue = json.loads(raw)
                    self.assertEqual(queue["queue_id"], f"cq-{span_id}")
                    self.assertEqual(queue["expires_at"], EXPIRES)
                    self.assertEqual(queue["spans"], [{
                        "seq": position, "span_id": span_id, "block_id": row["kit_id"],
                        "kit": {key: row[key] for key in ("path", "sha256")},
                        "legs": [f"L{position:03d}"], "attempt": 1, "not_before": NOT_BEFORE,
                    }])
        self.assertEqual(len(declared), 444)
        self.assertEqual(dict(declared), verified)
        self.assertEqual(set(verified), {path.relative_to(root).as_posix()
                                        for path in (root / "queues-1leg").glob("*.json")})


if __name__ == "__main__":
    unittest.main()
