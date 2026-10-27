"""Scoring and CLI checks against synthetic MATH generations."""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise.packs.difficulty.config import load_config
from joulewise.packs.difficulty.score import BENCH_COLUMNS, score_generations, repetition_loop

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/difficulty/pack_config.json"
MANIFEST = {"items": [{"item_id": "item", "level": 2, "expected_answer": "3"}]}


def generation(**changes):
    return {"model": "qwen3-1.7b", "mode": "off", "item_id": "item",
            "response_text": "\\boxed{3}", "finish_reason": "stop",
            "prompt_tokens": 10, "generated_tokens": 20, "generated_token_ids": [], **changes}


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(FIXTURE)

    def score(self, *rows):
        return score_generations(MANIFEST, self.config, rows)

    def test_correct_capped_and_runtime_failed(self):
        for finish, expected in (("stop", "correct"), ("length", "truncated"), ("error", "malformed")):
            with self.subTest(finish=finish):
                row = self.score(generation(finish_reason=finish))[0]
                self.assertEqual(row["outcome"], expected)
                self.assertEqual(row["correct"], int(finish == "stop"))
                self.assertEqual(row["cap_hit"], int(finish == "length"))
                self.assertEqual(row["flags"], "runtime_failed" if finish == "error" else "")

    def test_thinking_close_and_last_box(self):
        self.assertEqual(self.score(generation(mode="on"))[0]["outcome"], "malformed")
        text = "<think>\\boxed{0}</think>final \\boxed{3}"
        self.assertEqual(self.score(generation(mode="on", response_text=text))[0]["outcome"], "correct")
        self.assertEqual(self.score(generation(response_text="\\boxed{3} then \\boxed{4}"))[0]["outcome"], "incorrect")

    def test_unknown_item_config_and_automatic_attempts(self):
        rows = self.score(generation(), generation(), generation(item_id="absent"), generation(model="unknown"))
        self.assertEqual(len(rows), 4)
        self.assertNotIn("duplicate", rows[1]["flags"])
        self.assertEqual([row["attempt"] for row in rows], [1, 2, 1, 1])
        self.assertIn("unknown_item", rows[2]["flags"])
        self.assertIsNone(rows[2]["level"])
        self.assertIn("unknown_config", rows[3]["flags"])

    def test_bad_token_numbers_and_missing_text(self):
        for value in (-1, 1.0, True, None, "2", [], float("nan")):
            with self.subTest(value=value):
                row = self.score(generation(prompt_tokens=value))[0]
                self.assertIn("bad_number", row["flags"])
                self.assertIsNone(row["prompt_tokens"])
                self.assertEqual(row["generated_tokens"], 20)
        for text in (None, "", 17):
            row = self.score(generation(response_text=text))[0]
            self.assertIn("missing_text", row["flags"])
            self.assertEqual(row["outcome"], "malformed")

    def test_unknown_finish_reason_keeps_scored_row(self):
        row = self.score(generation(finish_reason="other"))[0]
        self.assertEqual(row["flags"], "unknown_finish_reason")
        self.assertEqual(row["outcome"], "malformed")
        self.assertEqual(row["correct"], 0)

    def test_R_flags_and_tail_loops(self):
        block = list(range(1000, 1020))
        cases = [(list(range(180)) + block*3, True),
                 (list(range(300)) + block*2, False),
                 (block*3 + list(range(300)), False), ([7]*80, False), ([7]*240, True)]
        for units, expected in cases:
            with self.subTest(length=len(units)):
                row = self.score(generation(generated_token_ids=units))[0]
                self.assertEqual("repetition_loop" in row["flags"], expected)
                self.assertNotIn("loop_check_words", row["flags"])
                self.assertEqual(row["correct"], 1)
        text = " ".join(map(str, cases[0][0])) + " \\boxed{3}"
        row = self.score(generation(response_text=text, generated_token_ids=None))[0]
        self.assertEqual(row["flags"], "loop_check_words;repetition_loop")
        row = self.score(generation(flags="repetition_loop"))[0]
        self.assertEqual((row["correct"], row["flags"]), (1, "repetition_loop"))
        row = self.score(generation(flags=["sleep", "Bad Flag", "repetition_loop", "sleep"]))[0]
        self.assertEqual(row["flags"], "bad_flag;repetition_loop;sleep")
        for invalid in ([True], [-1], [1.0], "ids", None):
            self.assertIn("loop_check_words", self.score(generation(generated_token_ids=invalid))[0]["flags"])
        self.assertFalse(repetition_loop([], self.config["loop_detector"]))

    def test_attempt_validation_and_file_order(self):
        rows = self.score(generation(attempt=10), generation(), generation(attempt=2), generation())
        self.assertEqual([row["attempt"] for row in rows], [10, 2, 2, 4])
        for invalid in (0, -1, True, "2", 2.0, None):
            row = self.score(generation(attempt=invalid))[0]
            self.assertIsNone(row["attempt"])
            self.assertIn("bad_number", row["flags"])

    def test_cli_every_line_including_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
            (path / "gen.jsonl").write_text(json.dumps(generation()) + "\nnot JSON\n[]\n", encoding="utf-8")
            command = [sys.executable, str(ROOT / "scripts/difficulty_score.py"),
                       "--manifest", str(path / "manifest.json"), "--config", str(FIXTURE),
                       "--generations", str(path / "gen.jsonl"), "--out", str(path / "bench.csv")]
            result = subprocess.run(command, capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stderr)
            with (path / "bench.csv").open(newline="") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(reader.fieldnames, list(BENCH_COLUMNS))
                rows = list(reader)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["correct"], "1")
            self.assertIn("unknown_item", rows[1]["flags"])

    def test_manifest_cli_repository_output_usage_error(self):
        command = [sys.executable, str(ROOT / "scripts/difficulty_manifest.py"),
                   "--config", str(FIXTURE), "--out", str(ROOT / "forbidden.json")]
        result = subprocess.run(command, capture_output=True, text=True, env=os.environ.copy())
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the repository", result.stderr)
        self.assertFalse((ROOT / "forbidden.json").exists())


if __name__ == "__main__":
    unittest.main()
