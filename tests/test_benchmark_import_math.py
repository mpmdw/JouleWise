"""MATH importer acceptance tests; real-file checks skip outside the bench."""
from __future__ import annotations

import hashlib
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from joulewise import benchmark_import_math as math
from joulewise.suite import SuiteManifest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/math"
REAL = Path("/Users/edr/jw_data/math-prm800k-7ecc7947")


def synthetic_receipt(payload: bytes) -> dict:
    sha = hashlib.sha256(payload).hexdigest()
    pointer = f"version https://git-lfs.github.com/spec/v1\noid sha256:{sha}\nsize {len(payload)}\n".encode()
    return {"sha256": sha, "bytes": len(payload), "git_blob_sha1": math.git_blob_sha1(payload), "lfs_pointer_blob_sha1": math.git_blob_sha1(pointer), "line_count": len(payload.splitlines()), "license_blob_sha1": math.LICENSE_BLOB_SHA1}


def synthetic_records():
    test = FIXTURE / "synthetic_test.jsonl"
    train = FIXTURE / "synthetic_train.jsonl"
    with mock.patch.object(math, "SOURCE_RECEIPTS", {"test.jsonl": synthetic_receipt(test.read_bytes()), "train.jsonl": synthetic_receipt(train.read_bytes())}):
        return math.load_math_test(test, train)


def selection_population():
    rows = []
    for level in range(1, 6):
        for subject in ("Algebra", "Geometry", "Number Theory"):
            for index in range(160):
                uid = f"test/{subject}/{level}_{index}.json"
                rows.append({"source_item_id": f"math_{level}_{subject}_{index}", "source_sha256": hashlib.sha256(uid.encode()).hexdigest(), "level": level, "subject": subject})
    return rows


class MathImportTests(unittest.TestCase):
    def test_synthetic_fixture_loader_and_eligibility(self):
        rows, receipts = synthetic_records()
        self.assertEqual((len(rows), len(receipts)), (7, 2))
        eligible, stats = math.eligible_records(rows)
        self.assertEqual(stats["excluded"], {"duplicate_unique_id": 2, "gold_not_rational": 1, "plain_comma_gold": 1})
        self.assertEqual([row["unique_id"] for row in eligible], ["test/algebra/1.json", "test/algebra/2.json", "test/prealgebra/7.json"])
        self.assertEqual(stats["reference_self_check"], "3/3")

    def test_receipts_refuse_one_byte_mutation_and_each_receipt(self):
        source = FIXTURE / "synthetic_test.jsonl"
        payload = source.read_bytes()
        expected = synthetic_receipt(payload)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.jsonl"
            path.write_bytes(payload)
            rows, receipt = math.authenticate_file(path, "test.jsonl", expected=expected)
            self.assertEqual(len(rows), 5)
            self.assertEqual(receipt, expected)
            path.write_bytes(payload.replace(b"Compute 1+1", b"Compute 1+2", 1))
            with self.assertRaisesRegex(ValueError, "sha256 receipt mismatch"):
                math.authenticate_file(path, "test.jsonl", expected=expected)
            path.write_bytes(payload)
            for key in ("sha256", "bytes", "git_blob_sha1", "lfs_pointer_blob_sha1", "line_count", "license_blob_sha1"):
                bad = dict(expected)
                bad[key] = "0" if isinstance(bad[key], str) else 0
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, key + " receipt mismatch"):
                    math.authenticate_file(path, "test.jsonl", expected=bad)
            pointer = Path(tmp) / "ptr"
            pointer.write_text("wrong")
            with self.assertRaisesRegex(ValueError, "pointer bytes mismatch"):
                math.authenticate_file(path, "test.jsonl", expected=expected, pointer_path=pointer)
            license = Path(tmp) / "LICENSE"
            license.write_text("wrong")
            with self.assertRaisesRegex(ValueError, "license_blob_sha1 receipt mismatch"):
                math.authenticate_file(path, "test.jsonl", expected=expected, license_path=license)

    def test_pilot_selection_determinism_prefix_disjointness(self):
        rows = selection_population()
        pilot = math.select_pilot(rows)
        self.assertEqual(len(pilot), 80)
        self.assertEqual({level: sum(row["level"] == level for row in pilot) for level in range(1, 6)}, {level: 16 for level in range(1, 6)})
        small = math.select_items(rows, pilot, 64)
        large = math.select_items(rows, pilot, 128)
        self.assertEqual(len(small), 320)
        self.assertEqual(len(large), 640)
        self.assertTrue({r["source_item_id"] for r in pilot}.isdisjoint({r["source_item_id"] for r in large}))
        for level in range(1, 6):
            self.assertEqual([r["source_item_id"] for r in small if r["level"] == level], [r["source_item_id"] for r in large if r["level"] == level][:64])
        self.assertEqual([r["source_item_id"] for r in pilot], [r["source_item_id"] for r in math.select_pilot(list(reversed(rows)))])
        self.assertEqual([r["source_item_id"] for r in small], [r["source_item_id"] for r in math.select_items(list(reversed(rows)), pilot, 64)])
        with self.assertRaisesRegex(ValueError, "short level"):
            math.select_items(rows[:160], [], 64)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            math.select_pilot(rows + [rows[0]])

    def test_short_subject_fills_from_other_subjects(self):
        rows = [row for row in selection_population() if row["subject"] != "Number Theory" or row["source_item_id"].endswith("_0")]
        pilot = math.select_pilot(rows)
        selected = math.select_items(rows, pilot, 64)
        self.assertEqual(len(selected), 320)
        self.assertTrue(all(sum(row["level"] == level for row in selected) == 64 for level in range(1, 6)))

    def test_render_both_thinking_arms_with_two_mirrors(self):
        class Tokenizer:
            def apply_chat_template(self, messages, *, tokenize, add_generation_prompt, enable_thinking):
                text = "<|im_start|>user\n" + messages[0]["content"] + "<|im_end|>\n<|im_start|>assistant\n"
                if not enable_thinking:
                    text += math.EMPTY_THINK_PREFIX
                return self.encode(text, add_special_tokens=True) if tokenize else text

            def encode(self, text, *, add_special_tokens):
                return list(text.encode())

        transformer_stub = types.ModuleType("transformers")
        transformer_stub.__version__ = "test"
        transformer_stub.AutoTokenizer = types.SimpleNamespace(from_pretrained=lambda *args, **kwargs: Tokenizer())
        with tempfile.TemporaryDirectory() as tmp:
            directories = [Path(tmp) / "one", Path(tmp) / "two"]
            for directory in directories:
                directory.mkdir()
                (directory / "tokenizer_config.json").write_text(json.dumps({"chat_template": "template"}))
                (directory / "tokenizer.json").write_text("tokenizer")
            original_sha256 = hashlib.sha256
            with mock.patch.dict("sys.modules", {"transformers": transformer_stub}), mock.patch.object(math, "_tokenizer_manifest", return_value={}), mock.patch.object(math, "tokenizer_id_for", return_value=math.PINNED_QWEN3_TOKENIZER_ID), mock.patch.object(math, "REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256", original_sha256(b"template").hexdigest()), mock.patch.object(math, "REVIEWED_QWEN3_TOKENIZER_JSON_SHA256", original_sha256(b"tokenizer").hexdigest()):
                for thinking in (False, True):
                    rendered = math.render_prompts([{"source_item_id": "x", "problem": "1+1?"}], directories, enable_thinking=thinking)
                    text = rendered["items"][0]["rendered_prompt_text"]
                    self.assertIn("1+1?", text)
                    self.assertEqual(text.endswith(math.EMPTY_THINK_PREFIX), not thinking)
                    self.assertEqual(text.endswith("<|im_start|>assistant\n"), thinking)

    def test_golden_pairs(self):
        correct = [(r"\dfrac{3}{4}", r"\frac34"), ("0.75", r"\frac34"), ("3/4", r"\frac34"), (r"\frac{6}{8}", r"\frac34"), (r"\boxed{\frac{3}{4}}", r"\frac34"), (r"-\frac12", r"-\frac{1}{2}"), ("x=5", "5"), ("10,080", r"10,\!080"), (r"90^\circ", "90"), (r"5\text{ cm}", "5"), (r"\$4", "4"), (".5", r"\frac12")]
        incorrect = [(r"\sqrt{2}", r"\frac32"), (r"\frac{1}{0}", "0"), ("1,2", "12"), (r"2\frac12", r"\frac52"), ("0.333", r"\frac13")]
        for response, reference in correct:
            with self.subTest(response=response, reference=reference):
                self.assertEqual(math.score_response(r"\boxed{" + response + "}", reference)["outcome"], "correct")
        for response, reference in incorrect:
            with self.subTest(response=response, reference=reference):
                self.assertEqual(math.score_response(r"\boxed{" + response + "}", reference)["outcome"], "incorrect")
        self.assertEqual(math.score_response(r"\boxed{1}\boxed{2}", "1")["outcome"], "incorrect")
        self.assertEqual(math.score_response(r"<think>\boxed{1}", "1", enable_thinking=True)["outcome"], "malformed")
        self.assertEqual(math.score_response("no box", "1")["outcome"], "malformed")
        capped = math.score_response(r"\boxed{1}", "1", runtime_status="capped")
        self.assertEqual((capped["outcome"], capped["parsed_answer"]), ("truncated", "1"))
        self.assertEqual(math.score_response("", "1", runtime_status="capped")["outcome"], "truncated")
        self.assertEqual(math.score_response(r"<think>\boxed{1}</think>\boxed{2}", "2", enable_thinking=True)["outcome"], "correct")

    def test_prompt_template_and_exact_set(self):
        self.assertEqual(math.PROMPT_TEMPLATE.count("{problem}"), 1)
        self.assertEqual(hashlib.sha256(math.PROMPT_TEMPLATE.encode()).hexdigest(), math.PROMPT_TEMPLATE_SHA256)
        manifest = {"items": [{"item_id": "a", "level": 1, "expected_answer": "1"}], "selected_item_ids_sha256": math.canonical_json_sha256(["a"]), "enable_thinking": False}
        row = {"item_id": "a", "response_text": r"\boxed{1}", "status": "succeeded"}
        self.assertEqual(math.score_math_outcome_table([row], manifest)["correct_count"], 1)
        with self.assertRaisesRegex(ValueError, "exact-set/order"):
            math.score_math_outcome_table([{**row, "item_id": "foreign"}], manifest)
        with self.assertRaisesRegex(ValueError, "id-list hash"):
            math.score_math_outcome_table([row], {**manifest, "selected_item_ids_sha256": "bad"})

    def test_native_suite_manifest_annotations_and_scoring(self):
        rows = []
        for level in range(1, 6):
            for subject in ("Algebra", "Geometry", "Number Theory"):
                for index in range(60):
                    source_index = len(rows)
                    rows.append({"problem": f"Compute {level}+{index}.", "solution": r"\boxed{1}", "answer": "1", "level": level, "subject": subject, "unique_id": f"test/{subject}/{level}_{index}.json", "source_file": "test.jsonl" if source_index < 500 else "train.jsonl", "line_index": source_index if source_index < 500 else source_index - 500})
        eligible, _ = math.eligible_records(rows)
        pilot = math.select_pilot(eligible)
        rendered = {"chat_template_sha256": math.REVIEWED_QWEN3_CHAT_TEMPLATE_SHA256, "tokenizer_json_sha256": math.REVIEWED_QWEN3_TOKENIZER_JSON_SHA256, "tokenizer_id": math.PINNED_QWEN3_TOKENIZER_ID, "rendered_with": {"library": "test", "version": "1"}, "items": [{"source_item_id": row["source_item_id"], "rendered_prompt_text": "<|im_start|>user\n" + math.PROMPT_TEMPLATE.replace("{problem}", row["problem"]) + "<|im_end|>\n<|im_start|>assistant\n", "prompt_token_ids": [1, 2]} for row in pilot]}
        manifest = math.build_math_suite_manifest(rows, math.SOURCE_RECEIPTS, set_name="pilot", n=None, enable_thinking=True, rendered=rendered, output_cap=384)
        self.assertEqual(SuiteManifest.from_mapping(manifest).to_dict(), manifest)
        self.assertEqual(len(manifest["benchmark_import"]["source_files"]), 2)
        sidecar = math.build_math_annotations(manifest, pilot)
        responses = [{"item_id": row["source_item_id"], "response_text": r"<think>work</think>\boxed{1}", "status": "succeeded"} for row in pilot]
        self.assertEqual(math.score_math_outcome_table(responses, manifest, sidecar)["correct_count"], 80)
        responses[0]["status"] = "capped"
        result = math.score_math_outcome_table(responses, manifest, sidecar)
        self.assertEqual((result["correct_count"], result["items"][0]["parsed_answer"]), (79, "1"))
        corrupt = json.loads(json.dumps(sidecar))
        corrupt["annotations"][0]["subject"] = "Precalculus"
        with self.assertRaisesRegex(ValueError, "source hash mismatch"):
            math.validate_math_annotations(manifest, corrupt)

    @unittest.skipUnless((REAL / "prm_test.jsonl").is_file() and (REAL / "prm_train.jsonl").is_file(), "pinned MATH source absent")
    def test_real_population_receipts_hashes_and_reference_self_check(self):
        rows, receipts = math.load_math_test(REAL / "prm_test.jsonl", REAL / "prm_train.jsonl", pointer_test=REAL / "ptr_test.txt", pointer_train=REAL / "ptr_train.txt", license_path=REAL / "prm_LICENSE")
        eligible, stats = math.eligible_records(rows)
        self.assertEqual((stats["rows"], stats["raw_distinct_ids"], stats["unique_ids"], stats["eligible"]), (5001, 5000, 4999, 4040))
        self.assertEqual(stats["reference_self_check"], "4040/4040")
        self.assertEqual([stats["levels"][str(level)]["eligible"] for level in range(1, 6)], [381, 733, 924, 967, 1035])
        self.assertEqual(receipts, math.SOURCE_RECEIPTS)
        pilot = math.select_pilot(eligible)
        hashes = {"pilot": math.canonical_json_sha256([r["source_item_id"] for r in pilot])}
        for n in (64, 128):
            hashes[f"n{n}"] = math.canonical_json_sha256([r["source_item_id"] for r in math.select_items(eligible, pilot, n)])
        fixture = json.loads((FIXTURE / "hash_only_manifest.json").read_text())
        self.assertEqual(hashes, fixture["set_hashes"])
        self.assertEqual(hashes, {"pilot": "d6a1671839efd2b99a3146f6f67be50d9b2cb57bff89704b630d17f7bd91d17c", "n64": "face9ab2eae3d9b0abf2d87ae83f4d1264d6951a8d9706ebc6ff7f147de81430", "n128": "1caaf115ac3e775d905be197bbdf63fb2f2b28b92cb7bac5cd46d044dc65aefa"})
        self.assertNotIn("problem", json.dumps(fixture))


if __name__ == "__main__":
    unittest.main()
