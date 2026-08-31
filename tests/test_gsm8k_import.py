from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from joulewise import benchmark_import as gsm8k_import
from joulewise.benchmark_import import (
    ANSWER_HASH_DOMAIN,
    EMPTY_THINK_PREFIX,
    OUTCOME_CLASSES,
    OUTCOME_CORRECT,
    OUTCOME_INCORRECT,
    OUTCOME_MALFORMED,
    OUTCOME_TRUNCATED,
    PINNED_QWEN3_TOKENIZER_ID,
    PROMPT_TEMPLATE,
    PROMPT_TEMPLATE_SHA256,
    SCORER_ID,
    build_gsm8k_scored_annotations,
    build_gsm8k_scored_manifest,
    canonical_subset_json_sha256,
    expected_answer_sha256,
    gold_answer,
    load_gsm8k_test,
    parse_response_answer,
    score_gsm8k_outcome_table,
    score_gsm8k_response,
    select_items,
    selected_item_ids_sha256,
    validate_gsm8k_annotations,
)
from joulewise.gensuite import tokenizer_id_for
from joulewise.suite import SuiteManifest, suite_manifest_sha256


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT / "configs" / "suite_manifests" / "gsm8k_scored_v6_qwen3.json"
)
ANNOTATIONS_PATH = (
    ROOT
    / "configs"
    / "suite_manifests"
    / "gsm8k_scored_v6_qwen3_annotations.json"
)
MIRROR_DIRS = (
    Path("/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit"),
    Path("/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit"),
)
PINNED_MANIFEST_SHA256 = (
    "1ad902f8ec64c737ee80f76b9b2dc6989b9e2d49ca267d5cb685b6f4c645c7f5"
)
PINNED_ANNOTATIONS_FILE_SHA256 = (
    "9123780834539c9bf9bf3c1a7581034018fea5a9f5e4a26a65ed30c9ed36c7e2"
)


def _record(index: int, source_sha256: str | None = None) -> dict:
    question = f"question {index}"
    answer = f"work\n#### {index + 1}"
    return {
        "line_index": index,
        "question": question,
        "answer": answer,
        "source_item_id": f"gsm8k_test_{index:04d}",
        "source_sha256": source_sha256
        or hashlib.sha256(
            json.dumps(
                {"question": question, "answer": answer},
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
    }


def _annotation(item_id: str = "gsm8k_test_0001", answer: str = "3/4") -> dict:
    return {
        "item_id": item_id,
        "expected_answer": answer,
        "expected_answer_sha256": expected_answer_sha256(item_id, answer),
        "scorer_id": SCORER_ID,
    }


@contextmanager
def _loaded_synthetic_records(count: int = 12):
    payload = "".join(
        json.dumps(
            {
                "question": f"question {index}",
                "answer": f"work\n#### {index + 1}",
            },
            separators=(",", ":"),
        )
        + "\n"
        for index in range(count)
    ).encode("utf-8")
    blob_sha1 = hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "test.jsonl"
        source.write_bytes(payload)
        with mock.patch.multiple(
            gsm8k_import,
            GSM8K_TEST_SHA256=hashlib.sha256(payload).hexdigest(),
            GSM8K_TEST_GIT_BLOB_SHA1=blob_sha1,
            GSM8K_TEST_BYTES=len(payload),
            GSM8K_TEST_LINE_COUNT=count,
        ):
            yield load_gsm8k_test(source)


def _rendered_records(records) -> dict:
    selected = select_items(records, 8)
    panel = json.loads(
        (ROOT / "configs/model_panels/qwen3_4bit.json").read_text(encoding="utf-8")
    )
    pinset = panel["rendering_pinsets"][0]
    rendered = {
        "items": [
            {
                "source_item_id": record["source_item_id"],
                "prompt_token_ids": [100 + index, 200 + index],
                "rendered_prompt_text": (
                    "<|im_start|>user\n"
                    + PROMPT_TEMPLATE.format(question=record["question"])
                    + "<|im_end|>\n<|im_start|>assistant\n"
                    + EMPTY_THINK_PREFIX
                ),
                "rendered_prompt_sha256": hashlib.sha256(
                    (
                        "<|im_start|>user\n"
                        + PROMPT_TEMPLATE.format(question=record["question"])
                        + "<|im_end|>\n<|im_start|>assistant\n"
                        + EMPTY_THINK_PREFIX
                    ).encode()
                ).hexdigest(),
            }
            for index, record in enumerate(selected)
        ],
        "chat_template_sha256": pinset["chat_template_sha256"],
        "tokenizer_json_sha256": pinset["tokenizer_json_sha256"],
        "tokenizer_id": PINNED_QWEN3_TOKENIZER_ID,
        "rendered_with": {"library": "test", "version": "1"},
    }
    return rendered


def _synthetic_product() -> tuple[dict, dict]:
    with _loaded_synthetic_records() as records:
        manifest = build_gsm8k_scored_manifest(records, _rendered_records(records))
        return manifest, build_gsm8k_scored_annotations(manifest, records)


class GSM8KImportTests(unittest.TestCase):
    def test_prompt_template_and_answer_hash_domains_are_pinned(self) -> None:
        self.assertEqual(
            PROMPT_TEMPLATE_SHA256,
            hashlib.sha256(PROMPT_TEMPLATE.encode("utf-8")).hexdigest(),
        )
        expected = hashlib.sha256(
            (ANSWER_HASH_DOMAIN + "\0gsm8k_test_0001\0" + "3/4").encode(
                "utf-8"
            )
        ).hexdigest()
        self.assertEqual(
            expected_answer_sha256("gsm8k_test_0001", "3/4"), expected
        )

    def test_pinned_source_loader_authenticates_sha_bytes_blob_and_lines(self) -> None:
        payload = (
            '{"question":"q1","answer":"work\\n#### 1"}\n'
            '{"question":"q2","answer":"work\\n#### 2"}\n'
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.jsonl"
            path.write_bytes(payload)
            blob = hashlib.sha1(
                f"blob {len(payload)}\0".encode("ascii") + payload
            ).hexdigest()
            with mock.patch.multiple(
                gsm8k_import,
                GSM8K_TEST_SHA256=hashlib.sha256(payload).hexdigest(),
                GSM8K_TEST_GIT_BLOB_SHA1=blob,
                GSM8K_TEST_BYTES=len(payload),
                GSM8K_TEST_LINE_COUNT=2,
            ):
                records = load_gsm8k_test(path)
            self.assertEqual([row["line_index"] for row in records], [0, 1])
            path.write_bytes(payload + b"\n")
            with self.assertRaisesRegex(ValueError, "sha256 mismatch"):
                load_gsm8k_test(path)

    def test_selection_and_subset_hashes_are_input_order_independent(self) -> None:
        records = [_record(index) for index in range(12)]
        forward = select_items(records, 8)
        reverse = select_items(list(reversed(records)), 8)
        self.assertEqual(forward, reverse)
        self.assertEqual(
            selected_item_ids_sha256(forward), selected_item_ids_sha256(reverse)
        )
        self.assertEqual(
            canonical_subset_json_sha256(forward),
            canonical_subset_json_sha256(reverse),
        )

    def test_selection_refuses_duplicate_key_and_invalid_k(self) -> None:
        duplicate = [_record(0, "a" * 64), _record(1, "a" * 64)]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            select_items(duplicate, 1)
        for value in (True, 0, -1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    select_items([_record(0)], value)
        with self.assertRaisesRegex(ValueError, "exceeds"):
            select_items([_record(0)], 2)

    def test_gold_answer_uses_last_marker_and_canonical_rational(self) -> None:
        cases = (
            ("old #### 8\nnew #### 1,250", "1250"),
            ("work\n#### 0.75", "3/4"),
            ("work\n#### -2.5", "-5/2"),
        )
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(gold_answer({"answer": raw}), expected)
        with self.assertRaisesRegex(ValueError, "final '#### '"):
            gold_answer({"answer": "no marker"})

    def test_response_parser_requires_exact_final_marker_line(self) -> None:
        self.assertEqual(parse_response_answer("reason\n#### 0.75\n"), "3/4")
        self.assertEqual(parse_response_answer("reason\n#### 1,250"), "1250")
        for response in ("", "answer 3/4", "#### 3/4 trailing", "#### $3"):
            with self.subTest(response=response):
                self.assertIsNone(parse_response_answer(response))

    def test_scorer_pins_all_four_outcomes(self) -> None:
        annotation = _annotation()
        cases = (
            ("reason\n#### 0.75", "succeeded", OUTCOME_CORRECT),
            ("reason\n#### 2", "succeeded", OUTCOME_INCORRECT),
            ("unfinished", "capped", OUTCOME_TRUNCATED),
            ("not formatted", "succeeded", OUTCOME_MALFORMED),
        )
        for response, status, expected in cases:
            with self.subTest(expected=expected):
                result = score_gsm8k_response(
                    response, annotation, runtime_status=status
                )
                self.assertEqual(result.outcome, expected)
                self.assertEqual(result.correct, expected == OUTCOME_CORRECT)
        self.assertEqual(set(OUTCOME_CLASSES), {case[2] for case in cases})

    def test_capped_response_with_final_answer_is_scored_not_called_truncated(self) -> None:
        correct = score_gsm8k_response(
            "#### 3/4", _annotation(), runtime_status="capped"
        )
        wrong = score_gsm8k_response(
            "#### 2", _annotation(), runtime_status="capped"
        )
        self.assertEqual(correct.outcome, OUTCOME_CORRECT)
        self.assertEqual(wrong.outcome, OUTCOME_INCORRECT)

    def test_scorer_refuses_hash_scorer_and_status_drift(self) -> None:
        for mutation, expected in (
            ({"expected_answer_sha256": "0" * 64}, "answer hash mismatch"),
            ({"scorer_id": "other"}, "scorer mismatch"),
        ):
            with self.subTest(expected=expected):
                annotation = {**_annotation(), **mutation}
                with self.assertRaisesRegex(ValueError, expected):
                    score_gsm8k_response(
                        "#### 0.75", annotation, runtime_status="succeeded"
                    )
        with self.assertRaisesRegex(ValueError, "unsupported.*status"):
            score_gsm8k_response(
                "#### 0.75", _annotation(), runtime_status="below_floor"
            )

    def test_four_way_table_is_exact_set_level_output(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        sidecar = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
        rows = [
            {
                "item_id": annotation["item_id"],
                "response_text": f"#### {annotation['expected_answer']}",
                "status": "succeeded",
            }
            for annotation in sidecar["annotations"]
        ]
        table = score_gsm8k_outcome_table(rows, manifest, sidecar)
        self.assertEqual(table["item_count"], 8)
        self.assertEqual(table["correct_count"], 8)
        self.assertEqual(table["accuracy"], 1.0)
        self.assertIn("pinned set", table["quarantine"])

    def test_synthetic_producer_is_deterministic_and_self_validating(self) -> None:
        first_manifest, first_sidecar = _synthetic_product()
        second_manifest, second_sidecar = _synthetic_product()
        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_sidecar, second_sidecar)
        self.assertEqual(
            SuiteManifest.from_mapping(first_manifest).to_dict(), first_manifest
        )
        validate_gsm8k_annotations(first_manifest, first_sidecar)

    def test_producer_refuses_rendered_selection_order_drift(self) -> None:
        with _loaded_synthetic_records() as records:
            rendered = _rendered_records(records)
            rendered["items"].reverse()
            with self.assertRaisesRegex(ValueError, "selected GSM8K order"):
                build_gsm8k_scored_manifest(records, rendered)

    def test_annotation_validator_refuses_manifest_and_answer_tampering(self) -> None:
        manifest, sidecar = _synthetic_product()
        tampered_manifest = copy.deepcopy(sidecar)
        tampered_manifest["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "manifest_sha256"):
            validate_gsm8k_annotations(manifest, tampered_manifest)
        tampered_answer = copy.deepcopy(sidecar)
        tampered_answer["annotations"][0]["expected_answer"] = "999"
        with self.assertRaisesRegex(ValueError, "answer hash mismatch"):
            validate_gsm8k_annotations(manifest, tampered_answer)

    def test_committed_manifest_and_sidecar_have_pinned_canonical_hashes(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        sidecar = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(suite_manifest_sha256(manifest), PINNED_MANIFEST_SHA256)
        self.assertEqual(
            hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
            PINNED_MANIFEST_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(ANNOTATIONS_PATH.read_bytes()).hexdigest(),
            PINNED_ANNOTATIONS_FILE_SHA256,
        )
        validate_gsm8k_annotations(manifest, sidecar)

    def test_committed_subset_and_answer_hashes_recompute_from_quarantine_sidecar(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        sidecar = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
        annotations = {
            row["source_item_id"]: row for row in sidecar["annotations"]
        }
        subset = []
        question_prefix = PROMPT_TEMPLATE.split("{question}", 1)[0]
        for item in manifest["items"]:
            source_item_id = item["source"]["source_item_id"]
            annotation = annotations[source_item_id]
            rendered = item["source"]["prompt_text"]
            start = rendered.index(question_prefix) + len(question_prefix)
            end = rendered.index("<|im_end|>", start)
            question = rendered[start:end]
            source_record = {
                "question": question,
                "answer": annotation["source_answer"],
            }
            self.assertEqual(
                hashlib.sha256(
                    json.dumps(
                        source_record, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                ).hexdigest(),
                item["source"]["source_sha256"],
            )
            subset.append(
                {
                    "source_item_id": source_item_id,
                    "question": question,
                    "answer": annotation["source_answer"],
                }
            )
        benchmark = manifest["benchmark_import"]
        self.assertEqual(
            selected_item_ids_sha256(subset),
            benchmark["selected_item_ids_sha256"],
        )
        self.assertEqual(
            canonical_subset_json_sha256(subset),
            benchmark["canonical_subset_json_sha256"],
        )

    def test_local_qwen3_mirrors_match_committed_tokenizer_and_prompt_pins(self) -> None:
        if not all(path.is_dir() for path in MIRROR_DIRS):
            self.skipTest("local Qwen3 tokenizer mirrors are absent")
        try:
            from transformers import AutoTokenizer
        except ImportError:
            self.skipTest("transformers is absent")
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        benchmark = manifest["benchmark_import"]
        for mirror in MIRROR_DIRS:
            with self.subTest(mirror=mirror.name):
                config = json.loads(
                    (mirror / "tokenizer_config.json").read_text(encoding="utf-8")
                )
                self.assertEqual(
                    hashlib.sha256(config["chat_template"].encode()).hexdigest(),
                    benchmark["chat_template_sha256"],
                )
                self.assertEqual(
                    hashlib.sha256((mirror / "tokenizer.json").read_bytes()).hexdigest(),
                    benchmark["tokenizer_json_sha256"],
                )
                self.assertEqual(
                    tokenizer_id_for(
                        tokenizer_manifest=gsm8k_import._tokenizer_manifest(mirror)
                    ),
                    benchmark["tokenizer_id"],
                )
                tokenizer = AutoTokenizer.from_pretrained(
                    str(mirror), local_files_only=True
                )
                for item in manifest["items"]:
                    prompt_text = item["source"]["prompt_text"]
                    self.assertTrue(prompt_text.endswith(EMPTY_THINK_PREFIX))
                    self.assertEqual(
                        tokenizer.encode(prompt_text, add_special_tokens=True),
                        item["source"]["prompt_token_ids"],
                    )


if __name__ == "__main__":
    unittest.main()
