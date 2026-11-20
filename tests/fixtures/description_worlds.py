"""Synthetic operational fixtures for builder tests under RL-192b."""

from scripts import run_state_items
from tests import test_desc_looks_acceptance as frozen


class DescriptionWorld(frozen.World):
    loaded_keys = frozenset()

    def named(self, name, rel, doc):
        if name == "host_chain":
            self.project_drops()
        super().named(name, rel, doc)

    def project_drops(self):
        drops = [row for row in self.rows if "drop" in row]
        if not drops:
            return
        witness_path = "ops/drop-evidence/retired-queue.json"
        witness = frozen.wire({"queue_id": "invented-queue", "final": True,
                               "unrun": [row["key"] for row in drops]})
        frozen.put(self.repo / witness_path, witness)
        item = {
            "schema": "joulewise.run_state_item.v1", "number": 900002, "owner": "lead",
            "status": "ISSUED", "issued_epoch_s": 1800000000, "expires_epoch_s": None,
            "sets": [], "supersedes": [],
        }
        statements = []
        for row in drops:
            key = row["key"]
            frozen.put(self.repo / row["drop"], {
                "key": key, "status": "dropped", "authority": "lead", "reason": "queue_retired",
                "queue": witness_path, "typed_item_ref": {"path": "RUN_STATE.md", "number": 900002},
            })
            statements.append(f"The lead declares {key} dropped:queue_retired. No member exists or will exist. "
                              f"Evidence {witness_path} sha256={frozen.sha(witness)}.")
        text = ("<!-- RUN_STATE TYPED ITEMS: invented queue retirement -->\n\n"
                "900002. **Invented queue retirement.**\n\n"
                f"```item\n{run_state_items.canonical(item)}\n```\n\n"
                + "\n\n".join(statements)
                + "\n\n<!-- RUN_STATE LEGACY ITEMS below: prose, not typed; cutover 900002 -->\n")
        frozen.put(self.repo / "RUN_STATE.md", text.encode())

    def commit_stage1(self, test):
        rc, stdout, stderr, events = frozen.invoke(self, "stage1")
        test.assertEqual((rc, stdout, stderr), (0, b"", b""))
        test.assertFalse([path for event, path in events if event == "open"])
        document = frozen.read(self.stage)
        test.assertEqual(document["counts"]["n_legs"], len(self.good))
        if not self.inst:
            test.assertEqual(document["counts"]["n_local_dates"], len(self.qualified_dates()))
        self.bind()

    def leg(self, kit, pos, v, day, ordinal, status):
        refs = super().leg(kit, pos, v, day, ordinal, status)
        key = refs["key"]
        record, receipt, plan, _ = self.records[key]
        loaded = key in self.loaded_keys
        budget = frozen.read(self.repo / "kits" / (key.split("/")[0] + ".json"))["span_template"]["leg_budget_s"]
        record.update(wall_s=budget, leg_budget_s=budget, over_time_budget=False)
        if record["loaded_flag"] is not loaded:
            record["loaded_flag"] = loaded
            self.records[key] = (record, receipt, plan, "not_qualified:loaded" if loaded else status)
            if status == "qualified":
                if loaded:
                    self.good.pop(key)
                else:
                    self.good[key] = (v, ordinal)
        frozen.put(self.repo / refs["leg_record"], record)
        return refs
