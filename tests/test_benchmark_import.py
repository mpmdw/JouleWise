import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from joulewise import benchmark_import
from joulewise.benchmark_import import (
    ANSWER_HASH_DOMAIN,
    EMPTY_THINK_PREFIX,
    OUTCOME_CLASSES,
    OUTCOME_CORRECT,
    OUTCOME_INCORRECT,
    OUTCOME_MALFORMED,
    OUTCOME_TRUNCATED,
    PROMPT_TEMPLATE,
    PROMPT_TEMPLATE_SHA256,
    PINNED_QWEN3_TOKENIZER_ID,
    SCORER_ID,
    build_gsm8k_scored_annotations,
    build_gsm8k_scored_manifest,
    canonical_subset_json_sha256,
    expected_answer_sha256,
    gold_answer,
    load_gsm8k_test,
    parse_response_answer,
    render_prompts,
    score_gsm8k_outcome_table,
    select_items,
    selected_item_ids_sha256,
    validate_gsm8k_annotations,
)
from joulewise.suite import SuiteManifest, suite_manifest_sha256
from scripts import gen_gsm8k_scored


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
MIRROR_DIRS = [
    Path("/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit"),
    Path("/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit"),
]
PINNED_MANIFEST_SHA256 = (
    "1ad902f8ec64c737ee80f76b9b2dc6989b9e2d49ca267d5cb685b6f4c645c7f5"
)
PINNED_ANNOTATIONS_FILE_SHA256 = (
    "9123780834539c9bf9bf3c1a7581034018fea5a9f5e4a26a65ed30c9ed36c7e2"
)


def _record(index: int, source_sha256: str) -> dict:
    return {
        "line_index": index,
        "question": f"question {index}",
        "answer": f"work\n#### {index + 1}",
        "source_item_id": f"gsm8k_test_{index:04d}",
        "source_sha256": source_sha256,
    }


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
            benchmark_import,
            GSM8K_TEST_SHA256=hashlib.sha256(payload).hexdigest(),
            GSM8K_TEST_GIT_BLOB_SHA1=blob_sha1,
            GSM8K_TEST_BYTES=len(payload),
            GSM8K_TEST_LINE_COUNT=count,
        ):
            yield load_gsm8k_test(source)


def _rendered_records(records):
    selected = select_items(records, 8)
    panel = json.loads(
        (ROOT / "configs/model_panels/qwen3_4bit.json").read_text(encoding="utf-8")
    )
    pinset = panel["rendering_pinsets"][0]
    return {
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
            }
            for index, record in enumerate(selected)
        ],
        "chat_template_sha256": pinset["chat_template_sha256"],
        "tokenizer_json_sha256": pinset["tokenizer_json_sha256"],
        "tokenizer_id": PINNED_QWEN3_TOKENIZER_ID,
        "rendered_with": {"library": "test", "version": "1"},
    }


def _synthetic_product() -> tuple[dict, dict]:
    with _loaded_synthetic_records() as records:
        manifest = build_gsm8k_scored_manifest(records, _rendered_records(records))
        return manifest, build_gsm8k_scored_annotations(manifest, records)


def _score_first_pinned_response(
    response_text: str,
    runtime_status: str,
    *,
    annotation_mutation: dict | None = None,
) -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sidecar = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
    if annotation_mutation is not None:
        sidecar["annotations"][0].update(annotation_mutation)
    rows = [
        {
            "item_id": annotation["item_id"],
            "response_text": f"#### {annotation['expected_answer']}",
            "status": "succeeded",
        }
        for annotation in sidecar["annotations"]
    ]
    rows[0]["response_text"] = response_text
    rows[0]["status"] = runtime_status
    return score_gsm8k_outcome_table(rows, manifest, sidecar)["items"][0]


class BenchmarkImportTests(unittest.TestCase):
    def test_module_import_does_not_load_transformers(self) -> None:
        self.assertFalse(
            any(
                name == "transformers" or name.startswith("transformers.")
                for name in sys.modules
            )
        )

    def test_prompt_template_hash_is_pinned(self) -> None:
        self.assertEqual(
            PROMPT_TEMPLATE_SHA256,
            hashlib.sha256(PROMPT_TEMPLATE.encode("utf-8")).hexdigest(),
        )

    def test_selection_is_independent_of_input_order(self) -> None:
        records = [
            _record(index, hashlib.sha256(f"source-{index}".encode()).hexdigest())
            for index in range(12)
        ]
        forward = select_items(records, 8)
        reverse = select_items(list(reversed(records)), 8)
        self.assertEqual(
            [record["source_item_id"] for record in forward],
            [record["source_item_id"] for record in reverse],
        )
        self.assertEqual(
            selected_item_ids_sha256(forward),
            selected_item_ids_sha256(reverse),
        )

    def test_load_refuses_non_pinned_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.jsonl"
            path.write_text('{"question":"q","answer":"#### 1"}\n')
            with self.assertRaisesRegex(ValueError, "sha256 mismatch"):
                load_gsm8k_test(path)

    def test_pinned_source_loader_authenticates_sha_bytes_blob_and_lines(self) -> None:
        payload = (
            '{"question":"q1","answer":"work\\n#### 1"}\n'
            '{"question":"q2","answer":"work\\n#### 2"}\n'
        ).encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "test.jsonl"
            path.write_bytes(payload)
            blob = hashlib.sha1(
                f"blob {len(payload)}\0".encode("ascii") + payload
            ).hexdigest()
            with mock.patch.multiple(
                benchmark_import,
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

    def test_gold_answer_uses_last_marker_and_canonical_fraction(self) -> None:
        cases = [
            ("steps\n#### 1,250", "1250"),
            ("steps\n#### 0.75", "3/4"),
            ("old #### 8\nnew #### 18", "18"),
        ]
        for raw, canonical in cases:
            with self.subTest(raw=raw):
                self.assertEqual(gold_answer({"answer": raw}), canonical)

    def test_selection_refuses_duplicate_key_and_invalid_k(self) -> None:
        duplicate = [_record(0, "a" * 64), _record(1, "a" * 64)]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            select_items(duplicate, 1)
        for value in (True, 0, -1):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    select_items([_record(0, "b" * 64)], value)
        with self.assertRaisesRegex(ValueError, "exceeds"):
            select_items([_record(0, "b" * 64)], 2)

    def test_gold_answer_refuses_unparsable_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "unparsable numeric answer"):
            gold_answer({"answer": "work\n#### twelve"})

    def test_expected_answer_hash_domain(self) -> None:
        expected = hashlib.sha256(
            (
                ANSWER_HASH_DOMAIN + "\0" + "gsm8k_test_0001" + "\0" + "3/4"
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(
            expected_answer_sha256("gsm8k_test_0001", "3/4"), expected
        )

    def test_committed_manifest_validates_and_round_trips(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        parsed = SuiteManifest.from_mapping(manifest)
        self.assertEqual(parsed.to_dict(), manifest)
        self.assertIsNotNone(parsed.benchmark_import)
        self.assertEqual(
            parsed.items[0].prompt_source_kind(), "prompt_token_ids"
        )
        self.assertEqual(suite_manifest_sha256(manifest), PINNED_MANIFEST_SHA256)
        self.assertEqual(
            hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
            PINNED_MANIFEST_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(ANNOTATIONS_PATH.read_bytes()).hexdigest(),
            PINNED_ANNOTATIONS_FILE_SHA256,
        )
        sidecar = json.loads(ANNOTATIONS_PATH.read_text())
        validate_gsm8k_annotations(manifest, sidecar)

    def test_committed_subset_hashes_recompute_from_manifest_and_annotations(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        sidecar = json.loads(ANNOTATIONS_PATH.read_text())
        benchmark_import = manifest["benchmark_import"]
        annotations_by_id = {
            row["source_item_id"]: row for row in sidecar["annotations"]
        }

        subset = []
        for item in manifest["items"]:
            source_item_id = item["source"]["source_item_id"]
            annotation = annotations_by_id[source_item_id]
            rendered_text = item["source"]["prompt_text"]
            question_prefix = PROMPT_TEMPLATE.split("{question}", 1)[0]
            question_start = rendered_text.index(question_prefix) + len(
                question_prefix
            )
            question_end = rendered_text.index("<|im_end|>", question_start)
            question = rendered_text[question_start:question_end]
            source_record = {
                "question": question,
                "answer": annotation["source_answer"],
            }
            self.assertEqual(
                _canonical_sha256(source_record), item["source"]["source_sha256"]
            )
            subset.append(
                {
                    "source_item_id": source_item_id,
                    "question": question,
                    "answer": annotation["source_answer"],
                }
            )
            self.assertEqual(
                annotation["expected_answer_sha256"],
                item["scoring"]["expected_answer_hash"],
            )

        selected_ids = [record["source_item_id"] for record in subset]
        self.assertEqual(
            _canonical_sha256(selected_ids),
            benchmark_import["selected_item_ids_sha256"],
        )
        self.assertEqual(
            _canonical_sha256(subset),
            benchmark_import["canonical_subset_json_sha256"],
        )
        self.assertEqual(
            canonical_subset_json_sha256(
                [
                    {
                        **record,
                        "line_index": annotations_by_id[record["source_item_id"]][
                            "line_index"
                        ],
                        "source_sha256": manifest["items"][index]["source"][
                            "source_sha256"
                        ],
                    }
                    for index, record in enumerate(subset)
                ]
            ),
            benchmark_import["canonical_subset_json_sha256"],
        )
        self.assertEqual(
            sidecar["manifest_sha256"], suite_manifest_sha256(manifest)
        )

    def test_response_parser_requires_exact_final_marker_line(self) -> None:
        self.assertEqual(parse_response_answer("reason\n#### 0.75\n"), "3/4")
        self.assertEqual(parse_response_answer("reason\n#### 1,250"), "1250")
        for response in ("", "answer 3/4", "#### 3/4 trailing", "#### $3"):
            with self.subTest(response=response):
                self.assertIsNone(parse_response_answer(response))

    def test_scorer_pins_all_four_outcomes_and_cap_semantics(self) -> None:
        sidecar = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
        expected_answer = sidecar["annotations"][0]["expected_answer"]
        cases = (
            (f"reason\n#### {expected_answer}", "succeeded", OUTCOME_CORRECT),
            ("reason\n#### 999999999999999999", "succeeded", OUTCOME_INCORRECT),
            ("unfinished", "capped", OUTCOME_TRUNCATED),
            ("not formatted", "succeeded", OUTCOME_MALFORMED),
            (f"#### {expected_answer}", "capped", OUTCOME_CORRECT),
            ("#### 999999999999999999", "capped", OUTCOME_INCORRECT),
        )
        for response, status, expected in cases:
            with self.subTest(expected=expected, status=status):
                result = _score_first_pinned_response(response, status)
                self.assertEqual(result["outcome"], expected)
                self.assertEqual(result["correct"], expected == OUTCOME_CORRECT)
        self.assertEqual(set(OUTCOME_CLASSES), set(case[2] for case in cases[:4]))

    def test_scorer_refuses_hash_scorer_and_status_drift(self) -> None:
        for mutation, expected in (
            ({"expected_answer_sha256": "0" * 64}, "answer hash mismatch"),
            ({"scorer_id": "other"}, "scorer_id mismatch"),
        ):
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(ValueError, expected):
                    _score_first_pinned_response(
                        "#### 0.75",
                        "succeeded",
                        annotation_mutation=mutation,
                    )
        with self.assertRaisesRegex(ValueError, "unsupported.*status"):
            _score_first_pinned_response("#### 0.75", "below_floor")

    def test_four_way_outcome_table_requires_the_exact_pinned_set(self) -> None:
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
        self.assertEqual(table["accuracy"], 1.0)
        self.assertIn("pinned set", table["quarantine"])

        cases = (
            ([], "gsm8k_pinned_set_empty"),
            (rows[:-1], "gsm8k_pinned_set_subset"),
            (rows + [{"item_id": "foreign"}], "gsm8k_pinned_set_superset"),
            ([{**rows[0], "item_id": "foreign"}] + rows[1:], "gsm8k_pinned_set_foreign"),
        )
        for candidate, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, reason):
                    score_gsm8k_outcome_table(candidate, manifest, sidecar)

        drifted = json.loads(json.dumps(manifest))
        drifted["benchmark_import"]["canonical_subset_json_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "gsm8k_pinned_subset_hash_mismatch"):
            score_gsm8k_outcome_table(rows, drifted, sidecar)

    def test_annotation_builder_self_validates(self) -> None:
        with _loaded_synthetic_records() as records:
            rendered = _rendered_records(records)
            manifest = build_gsm8k_scored_manifest(records, rendered)
            sidecar = build_gsm8k_scored_annotations(manifest, records)
        validate_gsm8k_annotations(manifest, sidecar)

    def test_canonical_generator_is_deterministic_and_self_validating(self) -> None:
        payload = "".join(
            json.dumps(
                {
                    "question": f"question {index}",
                    "answer": f"work\n#### {index + 1}",
                },
                separators=(",", ":"),
            )
            + "\n"
            for index in range(12)
        ).encode("utf-8")
        blob_sha1 = hashlib.sha1(
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "test.jsonl"
            source.write_bytes(payload)
            outputs: list[tuple[dict, dict]] = []
            with mock.patch.multiple(
                benchmark_import,
                GSM8K_TEST_SHA256=hashlib.sha256(payload).hexdigest(),
                GSM8K_TEST_GIT_BLOB_SHA1=blob_sha1,
                GSM8K_TEST_BYTES=len(payload),
                GSM8K_TEST_LINE_COUNT=12,
            ), mock.patch.object(
                gen_gsm8k_scored,
                "render_prompts",
                side_effect=lambda records, _directories: _rendered_records(records),
            ), mock.patch("sys.stdout", new=io.StringIO()):
                for run in range(2):
                    manifest_path = root / f"manifest-{run}.json"
                    annotations_path = root / f"annotations-{run}.json"
                    self.assertEqual(
                        gen_gsm8k_scored.main(
                            [
                                "--test-jsonl",
                                str(source),
                                "--tokenizer-dir",
                                str(root),
                                "--out-manifest",
                                str(manifest_path),
                                "--out-annotations",
                                str(annotations_path),
                            ]
                        ),
                        0,
                    )
                    outputs.append(
                        (
                            json.loads(manifest_path.read_text(encoding="utf-8")),
                            json.loads(annotations_path.read_text(encoding="utf-8")),
                        )
                    )
            self.assertEqual(outputs[0], outputs[1])
            validate_gsm8k_annotations(*outputs[0])
            self.assertEqual(
                SuiteManifest.from_mapping(outputs[0][0]).to_dict(), outputs[0][0]
            )

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

    def test_manifest_builder_refuses_unauthenticated_records(self) -> None:
        records = [
            _record(index, hashlib.sha256(f"source-{index}".encode()).hexdigest())
            for index in range(12)
        ]
        with self.assertRaisesRegex(ValueError, "gsm8k_source_authentication_required"):
            build_gsm8k_scored_manifest(records, _rendered_records(records))

    def test_annotation_builder_refuses_forged_line_index_records(self) -> None:
        with _loaded_synthetic_records() as records:
            manifest = build_gsm8k_scored_manifest(
                records, _rendered_records(records)
            )
            forged = [dict(record) for record in records]
            forged[0]["line_index"] = 999999
            with self.assertRaisesRegex(
                ValueError, "gsm8k_source_authentication_required"
            ):
                build_gsm8k_scored_annotations(manifest, forged)

    def test_public_scoring_surface_refuses_a_foreign_item(self) -> None:
        self.assertFalse(hasattr(benchmark_import, "score_gsm8k_response"))
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
        rows[0]["item_id"] = "gsm8k_test_foreign"
        with self.assertRaisesRegex(ValueError, "gsm8k_pinned_set_foreign"):
            score_gsm8k_outcome_table(rows, manifest, sidecar)

    def test_manifest_builder_refuses_drifted_reviewed_panel_copy(self) -> None:
        with _loaded_synthetic_records() as records:
            rendered = _rendered_records(records)
            panel = json.loads(
                (ROOT / "configs/model_panels/qwen3_4bit.json").read_text(
                    encoding="utf-8"
                )
            )
            for entry in panel["entries"]:
                entry["tokenizer_json_sha256"] = "0" * 64
            panel["rendering_pinsets"][0]["tokenizer_json_sha256"] = "0" * 64
            with tempfile.TemporaryDirectory() as temporary:
                drifted_panel = Path(temporary) / "qwen3_4bit.json"
                drifted_panel.write_text(json.dumps(panel), encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError, "gsm8k_reviewed_panel_pin_drift"
                ):
                    with mock.patch.object(
                        benchmark_import, "QWEN3_PANEL_PATH", drifted_panel
                    ):
                        build_gsm8k_scored_manifest(records, rendered)

    def test_render_prompts_asserts_two_mirror_equality_and_empty_think_tail(
        self,
    ) -> None:
        if not all(path.is_dir() for path in MIRROR_DIRS):
            self.skipTest("local Qwen3 tokenizer mirrors are absent")
        if importlib.util.find_spec("transformers") is None:
            self.skipTest("transformers is absent")

        imported_before = {
            name
            for name in sys.modules
            if name == "transformers" or name.startswith("transformers.")
        }
        code = """
import json
from pathlib import Path
from joulewise.benchmark_import import EMPTY_THINK_PREFIX, render_prompts

records = [
    {"source_item_id": f"item-{index}", "question": f"question {index}"}
    for index in range(2)
]
rendered = render_prompts(records, [Path(value) for value in __import__("sys").argv[1:]])
print(json.dumps({
    "count": len(rendered["items"]),
    "chat_hash_len": len(rendered["chat_template_sha256"]),
    "tokenizer_hash_len": len(rendered["tokenizer_json_sha256"]),
    "empty_think_tails": all(
        item["rendered_prompt_text"].endswith(EMPTY_THINK_PREFIX)
        for item in rendered["items"]
    ),
}, sort_keys=True))
"""
        completed = subprocess.run(
            [sys.executable, "-c", code, *(str(path) for path in MIRROR_DIRS)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout.splitlines()[-1])
        self.assertEqual(
            result,
            {
                "chat_hash_len": 64,
                "count": 2,
                "empty_think_tails": True,
                "tokenizer_hash_len": 64,
            },
        )
        imported_after = {
            name
            for name in sys.modules
            if name == "transformers" or name.startswith("transformers.")
        }
        self.assertEqual(imported_after, imported_before)

    def test_local_qwen3_mirrors_match_every_committed_prompt_token_id(self) -> None:
        if not all(path.is_dir() for path in MIRROR_DIRS):
            self.skipTest("local Qwen3 tokenizer mirrors are absent")
        if importlib.util.find_spec("transformers") is None:
            self.skipTest("transformers is absent")

        code = """
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer
from joulewise import benchmark_import
from joulewise.benchmark_import import EMPTY_THINK_PREFIX
from joulewise.gensuite import tokenizer_id_for

root = Path(__import__("sys").argv[1])
manifest = json.loads((root / "configs/suite_manifests/gsm8k_scored_v6_qwen3.json").read_text(encoding="utf-8"))
benchmark = manifest["benchmark_import"]
checked = 0
for raw_mirror in __import__("sys").argv[2:]:
    mirror = Path(raw_mirror)
    config = json.loads((mirror / "tokenizer_config.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(config["chat_template"].encode()).hexdigest() == benchmark["chat_template_sha256"]
    assert hashlib.sha256((mirror / "tokenizer.json").read_bytes()).hexdigest() == benchmark["tokenizer_json_sha256"]
    assert tokenizer_id_for(tokenizer_manifest=benchmark_import._tokenizer_manifest(mirror)) == benchmark["tokenizer_id"]
    tokenizer = AutoTokenizer.from_pretrained(str(mirror), local_files_only=True)
    for item in manifest["items"]:
        prompt_text = item["source"]["prompt_text"]
        assert prompt_text.endswith(EMPTY_THINK_PREFIX)
        assert tokenizer.encode(prompt_text, add_special_tokens=True) == item["source"]["prompt_token_ids"]
        checked += 1
print(json.dumps({"checked": checked}))
"""
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(ROOT),
                *(str(path) for path in MIRROR_DIRS),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout.splitlines()[-1]), {"checked": 16})


if __name__ == "__main__":
    unittest.main()
