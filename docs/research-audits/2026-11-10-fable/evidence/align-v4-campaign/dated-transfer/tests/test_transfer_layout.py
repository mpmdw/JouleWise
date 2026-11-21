"""Frozen RL-181 acceptance. Run with TMPDIR set to the private seat directory.

The Git inputs are public source and kit definitions. All changed inputs,
queue times and mock span outputs are synthetic. No date is assigned.
"""
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from importlib import import_module
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[5]
TRANSFER = HERE.relative_to(ROOT)
AUDIT = "eaaa1fd560cd457f4e4ccef316be62af920d08e1"
PIN = "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"
OLD = "71a83f666"
PLAYBACK = "4e5c2ad1d"
OLD_ROSTER = "173f75c45475ab2c2cd01402d570d5c8740cbf8c24fa85c5127b76b22dc4e01f"
OLD_FIRST_KIT = "a018bf05c67e0417cb2a3e5cf0f8a3073a7fac9502670f823b10d868539cefd3"
CELLS = [(2000, 4096), (10000, 4096), (19458, 4096), (19458, 4096)]
CYCLE = ((4096, 3724), (3151, 4096), (3724, 4096), (4096, 3151))
ROSTER = [f"L{i:03}" for i in range(1, 7)]
BUILDER = HERE / "build_kits.py"
NAMES = ["date-place-roster.json"] + [
    name for place in range(1, 21) for name in (
        f"kits/cl-transfer-{place:02}.v1.1.json",
        f"queues/cl-transfer-{place:02}.queue.json",
        f"ITEM-transfer-{place:02}.md",
    )
]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *map(str, args)])


def blob(revision, path):
    return git("cat-file", "blob", f"{revision}:{path}")


def read(path):
    return json.loads(path.read_bytes())


def inventory():
    # The same public families as 4e5c2ad1d, including the two qual-pin stability kits.
    sources = [
        (PIN, "docs/process/cadence/kits", r"cl-[^/]+\.json"),
        (AUDIT, str(TRANSFER.parent),
         r"item-drafts-(?:1118|rl172)/kits/cl-[^/]+\.json"
         r"|item-drafts-f2/f2-inst-01\.v1\.1\.json"
         r"|item-drafts-f2-0203/(?:f2-inst-0[23]/f2-inst-0[23]\.v1\.1\.json|hp-02/cl-hp-02\.json)"
         r"|f2-stab/(?:qual-pin/)?f2-stab-\d\d\.v1\.1\.json"),
    ]
    docs = []
    for revision, prefix, pattern in sources:
        names = git("ls-tree", "-r", "--name-only", revision, prefix).decode().splitlines()
        docs += [json.loads(blob(revision, path)) for path in names
                 if re.fullmatch(pattern, path.removeprefix(prefix + "/"))]
    return docs


def draw(kit_id, master, tag, i):
    return int.from_bytes(sha256(f"{kit_id}|{master}|{tag}|{i}".encode()).digest()[:8], "big")


class TransferContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        scratch = tempfile.TemporaryDirectory(prefix="transfer-contract-")
        cls.addClassCleanup(scratch.cleanup)
        cls.scratch = Path(scratch.name)
        cls.seat = cls.scratch / "seat"
        cls.seat.mkdir()
        cls.out = cls.seat / "first"
        cls.second = cls.seat / "second"
        cls.candidate = cls.out
        cls.builds = []
        if BUILDER.is_file():
            for out in (cls.out, cls.second):
                cls.builds.append(cls.run_builder("build", out))
        else:
            # Exercise the untouched baseline's committed outputs where possible.
            cls.candidate = ROOT
        cls.artifacts = cls.candidate / TRANSFER

    @classmethod
    def run_builder(cls, command, out):
        return subprocess.run(
            [sys.executable, "-B", str(BUILDER), command, "--seat-dir", str(cls.seat), "--output-dir", str(out)],
            cwd=ROOT, capture_output=True, text=True,
        )

    def require_builder(self):
        self.assertTrue(BUILDER.is_file(), "audit baseline has no executable transfer builder")

    def kits(self):
        return [read(self.artifacts / f"kits/cl-transfer-{place:02}.v1.1.json") for place in range(1, 21)]

    def test_historical_commitments(self):
        for name in NAMES:
            path = TRANSFER / name
            data = (ROOT / path).read_bytes()
            self.assertEqual(data, blob(OLD, path), name)
            self.assertEqual(data, blob(PLAYBACK, path), name)
        self.assertEqual(sha256((HERE / NAMES[0]).read_bytes()).hexdigest(), OLD_ROSTER)
        self.assertEqual(sha256((HERE / NAMES[1]).read_bytes()).hexdigest(), OLD_FIRST_KIT)

    def test_build_reproducible_and_confined(self):
        self.require_builder()
        for result in self.builds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({p.relative_to(self.artifacts).as_posix() for p in self.out.rglob("*") if p.is_file()},
                         set(NAMES))
        for name in NAMES:
            self.assertEqual((self.artifacts / name).read_bytes(),
                             (self.second / TRANSFER / name).read_bytes(), name)
        result = self.run_builder("build", self.out)
        self.assertNotEqual(result.returncode, 0, "existing output accepted")
        outside = self.scratch / "outside-seat"
        result = self.run_builder("build", outside)
        self.assertNotEqual(result.returncode, 0, "output outside seat accepted")
        self.assertFalse(outside.exists())

    def test_admitted_pin_and_all_frozen_paths(self):
        old = json.loads(blob(OLD, TRANSFER / NAMES[1]))["frozen"]["paths"]
        self.assertEqual(len(old), 38)
        hashes = {path: sha256(blob(PIN, path)).hexdigest() for path in old}
        self.assertEqual({p for p in old if hashes[p] != old[p]},
                         {"scripts/cadence_legs_runner.py", "scripts/launch_cadence_span.py"})
        for kit in self.kits():
            self.assertEqual(kit["frozen"], {"commit": PIN, "paths": hashes}, kit["campaign_id"])

    def test_rebind_preserves_nonseed_kit_fields(self):
        for kit in self.kits():
            kit_id = kit["campaign_id"]
            old = json.loads(blob(OLD, TRANSFER / "kits" / f"{kit_id}.v1.1.json"))
            changed = {key for key in old.keys() | kit.keys() if old.get(key) != kit.get(key)}
            self.assertLessEqual(changed, {"frozen", "seed_law", "legs"}, kit_id)

    def test_order_layout_and_fresh_first_unused_seeds(self):
        prior = inventory()
        self.assertEqual(len(prior), 38)
        masters = {kit["seed_law"]["master_seed"] for kit in prior}
        seeds = {leg["seed"] for kit in prior for leg in kit["legs"]}
        orders = set()
        for place, kit in enumerate(self.kits(), 1):
            with self.subTest(place=place):
                kit_id = f"cl-transfer-{place:02}"
                self.assertEqual(kit["campaign_id"], kit_id)
                law, legs = kit["seed_law"], kit["legs"]
                self.assertEqual((law["method"], law["spans"], law["n_legs"]), ("sha256-qual-v1", 1, 6))
                self.assertEqual([leg["leg_id"] for leg in legs], ROSTER)
                self.assertEqual([leg["start_band"] for leg in legs], ["q0"] * 6)
                self.assertEqual(legs[0]["leg_type"], "A")
                self.assertEqual([leg["g0_shape"] for leg in legs], ["own"] + ["span"] * 5)
                self.assertEqual(sorted((leg["prefill_tokens"], leg["decode_tokens"])
                                        for leg in legs if leg["leg_type"] == "A"), CELLS)
                pair = [i for i, leg in enumerate(legs) if leg["leg_type"] == "L"]
                self.assertEqual(pair, [pair[0], pair[0] + 1])
                self.assertEqual([(legs[i]["prefill_tokens"], legs[i]["pair"]) for i in pair], [(19458, "p1")] * 2)
                order = tuple(legs[i]["decode_tokens"] for i in pair)
                expected_order = CYCLE[(place - 1) % 4]
                self.assertEqual(order, expected_order)
                orders.add(order)
                for master in range(2026111800, law["master_seed"] + 1):
                    if master in masters:
                        continue
                    full_first = draw(kit_id, master, "qual-pair-first0", 0) % 2 == 1
                    ordered_seeds = [draw(kit_id, master, "seed", i) % (2 ** 32) for i in range(6)]
                    if full_first == (expected_order[0] == 4096) and len(set(ordered_seeds)) == 6 and seeds.isdisjoint(ordered_seeds):
                        break
                else:
                    self.fail("no eligible master seed through the one in the kit")
                self.assertEqual(law["master_seed"], master)
                self.assertEqual([leg["seed"] for leg in legs], ordered_seeds)
                masters.add(master)
                seeds.update(ordered_seeds)
        self.assertEqual(orders, set(CYCLE))

    def test_roster_halted_queues_and_unissued_items(self):
        roster = read(self.artifacts / NAMES[0])
        self.assertEqual((roster["status"], roster["max_dates"], roster["max_legs"]), ("draft", 20, 120))
        self.assertEqual(roster["runner_pin"], PIN)
        self.assertEqual([row["date_place"] for row in roster["places"]], list(range(1, 21)))
        for row in roster["places"]:
            place, kit_id = row["date_place"], row["kit_id"]
            self.assertEqual(kit_id, f"cl-transfer-{place:02}")
            self.assertEqual(row["span_id"], f"{kit_id}-s01")
            self.assertEqual(row["legs"], ROSTER)
            for key, relpath in (("kit", f"kits/{kit_id}.v1.1.json"), ("queue", f"queues/{kit_id}.queue.json")):
                ref = row[key]
                self.assertEqual(ref["path"], (TRANSFER / relpath).as_posix())
                self.assertEqual(ref["sha256"], sha256((self.candidate / ref["path"]).read_bytes()).hexdigest())
            queue = read(self.candidate / row["queue"]["path"])
            self.assertTrue(queue["halt"])
            self.assertLess(datetime.fromisoformat(queue["expires_at"]),
                            datetime.fromisoformat("2026-11-18T14:00:00-08:00"))
            self.assertEqual(queue["spans"], [{
                "seq": 1, "span_id": row["span_id"], "block_id": kit_id, "kit": row["kit"],
                "legs": ROSTER, "attempt": 1, "not_before": queue["expires_at"][:10],
            }])
            item = (self.artifacts / f"ITEM-transfer-{place:02}.md").read_text()
            for binding in ("**Unissued.", "has no assigned date", PIN, row["kit"]["sha256"], row["queue"]["sha256"]):
                self.assertIn(binding, item)
            self.assertGreater(row["expected_s"], 0)
            self.assertGreaterEqual(row["worst_case_s"], row["expected_s"])
            self.assertGreaterEqual(row["launch_minimum_s"], row["worst_case_s"])

    def test_shifted_ordinal_including_a_miss_seed_collision_and_split_l(self):
        self.require_builder()
        sys.path.insert(0, str(HERE))
        try:
            validate_layout = import_module("build_kits").validate_layout
        finally:
            sys.path.pop(0)
        kits = self.kits()
        validate_layout(kits)
        shifted = kits[1:] + kits[:1]  # Reuse place 2's kit in place 1 after a miss.
        with self.assertRaisesRegex(ValueError, "date place"):
            validate_layout(shifted)
        shifted = deepcopy(kits)
        # Re-labeling the shifted layouts still violates the frozen cycle.
        shifted[1]["legs"], shifted[2]["legs"] = shifted[2]["legs"], shifted[1]["legs"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate_layout(shifted)
        collision = deepcopy(kits)
        collision[-1]["legs"][0]["seed"] = collision[0]["legs"][0]["seed"]
        with self.assertRaisesRegex(ValueError, "fresh"):
            validate_layout(collision)
        split = deepcopy(kits)
        legs = split[0]["legs"]
        end = max(i for i, leg in enumerate(legs) if leg["leg_type"] == "L")
        gap = end + 1 if end < 5 else end - 2
        legs[end], legs[gap] = legs[gap], legs[end]
        with self.assertRaisesRegex(ValueError, "adjacent"):
            validate_layout(split)

    def test_stale_path_stale_digest_and_active_queue(self):
        self.require_builder()
        # Replace only invented fields in the seat-local candidate and restore after each probe.
        kit_path, queue_path = (self.artifacts / n for n in NAMES[1:3])
        cases = (("stale path", kit_path, r"cadence_legs_runner\.py.*sha256"),
                 ("stale digest", queue_path, r"sha256|digest"),
                 ("active queue", queue_path, r"halt"))
        for label, path, reason in cases:
            with self.subTest(label=label):
                original = path.read_bytes()
                doc = json.loads(original)
                if label == "stale path":
                    doc["frozen"]["paths"]["scripts/cadence_legs_runner.py"] = "0" * 64
                elif label == "stale digest":
                    doc["spans"][0]["kit"]["sha256"] = "0" * 64
                else:
                    doc["halt"] = None
                    doc["expires_at"] = "2026-11-19T00:00:00-08:00"
                try:
                    path.write_text(json.dumps(doc))
                    result = self.run_builder("validate-kit", self.out)
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertRegex(result.stdout + result.stderr, reason)
                finally:
                    path.write_bytes(original)

    def test_validates_and_runs_one_synthetic_full_span(self):
        self.require_builder()
        for command in ("validate-kit", "mock"):
            with self.subTest(command=command):
                result = self.run_builder(command, self.out)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("six legs, zero stops", result.stdout)


if __name__ == "__main__":
    unittest.main()
