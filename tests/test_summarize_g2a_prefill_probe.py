from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.select_g2a_prefill_length import main as select_main
from scripts.summarize_g2a_prefill_probe import main as summarize_main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/g2a/pin"


class SummarizeG2APrefillProbeTests(unittest.TestCase):
    maxDiff = None

    def copy_fixture(self, temporary: str) -> tuple[Path, Path, Path]:
        root = Path(temporary) / "fixture"
        shutil.copytree(FIXTURE, root)
        inventory_path = root / "g2a-input-inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["config_root"] = str(root / "config-root")
        ladder_path = root / "prefill-prompt-ladder.json"
        ladder = json.loads(ladder_path.read_text(encoding="utf-8"))
        ladder.update(
            rendering_mode="raw_prompt_text",
            chat_template_applied=False,
            thinking_policy="not_applicable_raw_prefill",
        )
        ladder_path.write_text(json.dumps(ladder) + "\n", encoding="utf-8")
        inventory.update(
            runtime_adapter={
                "path": "joulewise/adapters/mlx_runtime.py",
                "sha256": hashlib.sha256(
                    (ROOT / "joulewise/adapters/mlx_runtime.py").read_bytes()
                ).hexdigest(),
            },
            repo_head="a" * 40,
            rendering_mode="raw_prompt_text",
            chat_template_applied=False,
            thinking_policy="not_applicable_raw_prefill",
        )
        inventory["prompt_ladder"]["path"] = str(ladder_path)
        inventory["prompt_ladder"]["sha256"] = hashlib.sha256(
            ladder_path.read_bytes()
        ).hexdigest()
        by_length = {rung["prefill_tokens"]: rung for rung in ladder["rungs"]}
        for stage in inventory["stages"]:
            rung = by_length[stage["prefill_tokens"]]
            for member in stage["members"]:
                run_root = root / "summary-root" / member["run_id"]
                config_raw = (root / "config-root" / member["config_path"]).read_bytes()
                (run_root / "config.json").write_bytes(config_raw)
                summary_path = run_root / "summary_metrics.json"
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                summary.update(
                    run_id=member["run_id"],
                    workload_provenance={
                        "prompt": {
                            "realized_token_count": rung["prefill_tokens"],
                            "token_ids_sha256": rung["prompt_token_ids_sha256"],
                        }
                    },
                )
                summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
        inventory_path.write_text(
            json.dumps(inventory, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return root / "config-root", inventory_path, root / "summary-root"

    def run_summary(
        self,
        root: Path,
        config_root: Path,
        inventory: Path,
        runs_root: Path,
    ) -> tuple[int, Path, Path]:
        counts = root / "counts.jsonl"
        summary = root / "summary.json"
        code = summarize_main(
            [
                "--config-root",
                str(config_root),
                "--input-inventory",
                str(inventory),
                "--runs-root",
                str(runs_root),
                "--counts-output",
                str(counts),
                "--summary-output",
                str(summary),
            ]
        )
        return code, counts, summary

    def rewrite_count(self, runs_root: Path, run_id: str, count: int) -> None:
        path = runs_root / run_id / "summary_metrics.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["window_evidence_precheck"]["phase"]["prefill"]["windows"][0][
            "in_window_sample_count"
        ] = count
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def test_five_passing_small_members_qualify_and_large_below_five_does_not_gate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            self.rewrite_count(runs_root, "g2a-large-p0512-r01", 0)
            code, counts_path, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
            counts = json.loads(counts_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual(counts["schema_version"], "joulewise.g2a_probe_counts_receipt.v1")
        self.assertEqual(len(counts["runs"]), 24)
        self.assertEqual([row["length"] for row in rows], [512, 1024, 2048, 4096])
        self.assertTrue(rows[0]["all_small_count_ge_5"])
        self.assertEqual(rows[0]["small_minimum_count"], 6)
        self.assertEqual(rows[0]["large_members"], 1)
        large = next(
            row for row in counts["runs"] if row["run_id"] == "g2a-large-p0512-r01"
        )
        self.assertEqual(large["in_window_sample_count"], 0)

    def test_one_small_member_below_five_makes_only_that_rung_nonqualifying(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            self.rewrite_count(runs_root, "g2a-small-p1024-r03", 4)
            code, _counts, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        by_length = {row["length"]: row for row in rows}
        self.assertFalse(by_length[1024]["all_small_count_ge_5"])
        self.assertEqual(by_length[1024]["small_minimum_count"], 4)
        self.assertTrue(by_length[512]["all_small_count_ge_5"])

    def test_small_count_below_three_is_preserved_in_member_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p2048-r04"
            self.rewrite_count(runs_root, run_id, 2)
            code, counts_path, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            counts = json.loads(counts_path.read_text(encoding="utf-8"))["runs"]
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        member = next(row for row in counts if row["run_id"] == run_id)
        self.assertEqual(member["in_window_sample_count"], 2)
        rung = next(row for row in rows if row["length"] == 2048)
        self.assertEqual(rung["small_minimum_count"], 2)
        self.assertFalse(rung["all_small_count_ge_5"])

    def test_missing_small_run_remains_a_below_floor_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            (runs_root / "g2a-small-p0512-r05" / "summary_metrics.json").unlink()
            code, counts, summary = self.run_summary(
                root, config_root, inventory_path, runs_root
            )
            row = next(
                item for item in json.loads(summary.read_text()) if item["length"] == 512
            )
        self.assertEqual(code, 0)
        self.assertEqual(row["small_members"], 4)
        self.assertEqual(row["small_minimum_count"], 0)
        self.assertFalse(row["all_small_count_ge_5"])

    def test_missing_summary_emits_zero_below_floor_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            (runs_root / "g2a-small-p2048-r02" / "summary_metrics.json").unlink()
            code, _counts, summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
            row = next(
                item for item in json.loads(summary.read_text()) if item["length"] == 2048
            )
        self.assertEqual(code, 0)
        self.assertEqual(row["small_minimum_count"], 0)
        self.assertFalse(row["all_small_count_ge_5"])

    def test_wrong_run_id_refuses_even_when_the_mutated_config_hash_is_rebound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p0512-r01"
            summary_path = runs_root / run_id / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["run_id"] = "wrong-run-id"
            summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory_path, runs_root
            )
        self.assertEqual(code, 2)

    def test_altered_config_hash_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            path = config_root / "large-p4096/g2a-large-p4096-r01.json"
            path.write_bytes(path.read_bytes() + b" \n")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_recorded_run_config_hash_mismatch_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p0512-r01"
            path = runs_root / run_id / "config.json"
            path.write_bytes(path.read_bytes() + b" ")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_extra_config_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            (config_root / "small-p4096/extra.json").write_text("{}\n", encoding="utf-8")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_exact_four_row_output_is_accepted_by_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            code, _counts, summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
            selection = root / "selection.json"
            select_code = select_main(
                ["--summary", str(summary), "--output", str(selection)]
            )
            record = json.loads(selection.read_text(encoding="utf-8"))
        self.assertEqual((code, select_code), (0, 0))
        self.assertEqual(record["selected_prefill_tokens"], 512)


if __name__ == "__main__":
    unittest.main()
