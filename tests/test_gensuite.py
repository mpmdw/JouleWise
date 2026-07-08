from __future__ import annotations

import hashlib
import importlib
import itertools
import json
import re
import tempfile
import unittest
from pathlib import Path

import joulewise.gensuite as gensuite
from joulewise.gensuite import (
    FAKE_TOKENIZER_MANIFEST,
    SENTINEL_CONDITIONS,
    Drbg,
    ShapeError,
    build_jw_mixed_manifest,
    build_jw_mixed_suite,
    build_sentinel_manifest,
    build_sentinel_suite,
    generate_chat,
    generate_code,
    generate_json,
    generate_multiling,
    generate_reason,
    generate_summ,
    item_seed,
    random_token_ids,
    realize_exact_prompt,
    repeated_seed_ids,
    sentinel_content,
    tokenizer_id_from_manifest,
)
from joulewise.provenance import prompt_token_ids_sha256
from joulewise.suite import SuiteManifest


class QuirkyFakeTokenizer:
    vocab_size = 4096
    bos_token_id = 1
    eos_token_id = 2
    pad_token_id = 0
    unk_token_id = 3
    special_token_ids = {0, 1, 2, 3}
    empty_decode_ids = {3901, 3902, 3903}
    tokenizer_manifest = (
        ("fake-tokenizer.json", "a" * 64),
        ("fake-merges.txt", "b" * 64),
    )

    def __init__(self) -> None:
        self.encode_inputs: list[tuple[str, bool]] = []

    def encode(self, text: str, add_special_tokens: bool) -> list[int]:
        self.encode_inputs.append((text, add_special_tokens))
        ids: list[int] = []
        i = 0
        merges = ["ab", "# ", " 0", " a", " e", "()", "{}", "->", "\n\n", "=="]
        while i < len(text):
            hit = next((merge for merge in merges if text.startswith(merge, i)), None)
            if hit is not None:
                ids.append(self._piece_id(hit))
                i += len(hit)
                continue
            ch = text[i]
            if ch.isspace():
                j = i + 1
                while j < len(text) and text[j].isspace() and text[j] != "\n":
                    j += 1
                ids.append(self._piece_id(text[i:j]))
                i = j
                continue
            if ch.isalnum() or ch == "_" or ord(ch) > 127:
                j = i + 1
                while j < len(text) and (text[j].isalnum() or text[j] == "_" or ord(text[j]) > 127):
                    j += 1
                run = text[i:j]
                step = 3 if any(ord(c) > 127 for c in run) else 4
                for k in range(0, len(run), step):
                    ids.append(self._piece_id(run[k : k + step]))
                i = j
                continue
            ids.append(self._piece_id(ch))
            i += 1
        if add_special_tokens:
            return [self.bos_token_id] + ids
        return ids

    def decode(self, ids: list[int]) -> str:
        if len(ids) == 1 and ids[0] in self.empty_decode_ids:
            return ""
        return "".join(f"<{token_id}>" for token_id in ids if token_id not in self.special_token_ids)

    def _piece_id(self, piece: str) -> int:
        digest = hashlib.sha256(piece.encode("utf-8")).digest()
        return 10 + int.from_bytes(digest[:4], "big") % (self.vocab_size - 20)


class ImpossibleBudgetTokenizer(QuirkyFakeTokenizer):
    def encode(self, text: str, add_special_tokens: bool) -> list[int]:
        count = len(text)
        ids = [10, 11] * count
        return [self.bos_token_id] + ids if add_special_tokens else ids


class ScriptedDrbg(Drbg):
    def __init__(self, values: list[int]) -> None:
        super().__init__(b"scripted")
        self.values = list(values)

    def u64(self) -> int:
        if not self.values:
            return 0
        return self.values.pop(0)


class GenSuiteTests(unittest.TestCase):
    def fake_tokenizer_id(self) -> str:
        return tokenizer_id_from_manifest(FAKE_TOKENIZER_MANIFEST)

    def test_drbg_determinism_and_rejection_edge(self) -> None:
        a = Drbg(b"seed")
        b = Drbg(b"seed")
        self.assertEqual([a.u64() for _ in range(5)], [b.u64() for _ in range(5)])
        n = 3
        lim = (1 << 64) - ((1 << 64) % n)
        edge = ScriptedDrbg([lim, lim + 1, 8])
        self.assertEqual(edge.below(n), 8 % n)

    def test_drbg_golden_vector(self) -> None:
        drbg = Drbg(b"seed")
        self.assertEqual(
            [drbg.u64() for _ in range(5)],
            [
                8279016544200635327,
                16810200532868329192,
                6109299868023459158,
                3433991522560598602,
                2625678594452531726,
            ],
        )

    def test_exact_shape_all_categories_multiple_seeds(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        funcs = [generate_chat, generate_code, generate_summ, generate_reason, generate_json]
        for func in funcs:
            for index in range(2):
                content = func(
                    item_seed("shape", func.__name__, index),
                    tokenizer,
                    tokenizer_id=self.fake_tokenizer_id(),
                )
                self.assertEqual(len(tokenizer.encode(content.prompt_text or "", True)), 512)
        for index in range(6):
            content = generate_multiling(
                item_seed("shape", "jw.multiling", index),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
                profile_index=index,
            )
            self.assertEqual(len(tokenizer.encode(content.prompt_text or "", True)), 512)
            self.assertLessEqual(content.annotations["ascii_tail_tokens"], 3)

    def test_exact_shape_fails_closed_when_unreachable(self) -> None:
        with self.assertRaises(ShapeError):
            realize_exact_prompt(
                ImpossibleBudgetTokenizer(),
                target_tokens=3,
                prologue="",
                unit_factory=lambda: "",
                atom_ladder=["x"],
                add_special_tokens=False,
                max_units=0,
            )

    def test_full_reencode_catches_cross_boundary_merge(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        prompt = realize_exact_prompt(
            tokenizer,
            target_tokens=2,
            prologue="a",
            unit_factory=lambda: "",
            atom_ladder=["b", " a"],
            add_special_tokens=False,
            max_units=0,
        )
        self.assertEqual(len(tokenizer.encode(prompt.text, False)), 2)
        self.assertEqual(prompt.text, "a a")
        self.assertIn(("ab", False), tokenizer.encode_inputs)

    def test_reasoning_trace_integer_divisibility_and_answer(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        saw_arithmetic = False
        saw_logic = False
        for index in range(20):
            content = generate_reason(
                item_seed("reason", "jw.reason", index),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
            )
            trace = content.annotations["reasoning_trace"]
            if trace["reason_type"] == "arithmetic":
                saw_arithmetic = True
                value = trace["initial"]
                for step in trace["steps"]:
                    if step["op"] == "int_div":
                        self.assertEqual(value % step["operand"], 0)
                    value = step["after"]
                    self.assertIsInstance(value, int)
                self.assertEqual(value, trace["verified_answer"])
                self.assertEqual(value, content.annotations["ground_truth"]["answer"])
                self.assertGreater(len(content.annotations["distractors"]), 0)
            else:
                saw_logic = True
                order = trace["solution_order"]
                self.assertEqual(trace["answer"], order[2])
                constraints = [tuple(pair) for pair in trace["constraints"]]
                valid = [
                    perm
                    for perm in itertools.permutations(order)
                    if all(perm.index(a) < perm.index(b) for a, b in constraints)
                ]
                self.assertEqual(valid, [tuple(order)])
            params = content.annotations["parameters"]
            self.assertEqual(params["answer_seed_range"]["value"], [10, 80])
            self.assertEqual(params["intermediate_cap"]["value"], 10000)
            self.assertNotIn("value_range", params)
        self.assertTrue(saw_arithmetic)
        self.assertTrue(saw_logic)

    def test_reasoning_prompt_text_independently_matches_trace(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        saw_arithmetic = False
        saw_logic = False
        for index in range(80):
            content = generate_reason(
                item_seed("reason-parse", "jw.reason", index),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
            )
            text = content.prompt_text or ""
            trace = content.annotations["reasoning_trace"]
            if trace["reason_type"] == "arithmetic":
                saw_arithmetic = True
                start = re.search(r"The starting count is ([0-9]+) crates\.", text)
                self.assertIsNotNone(start)
                value = int(start.group(1))  # type: ignore[union-attr]
                for sentence in re.findall(r"Then the clerk ([^.]+)\.", text):
                    match = re.fullmatch(
                        r"(adds|removes|multiplies the count by|packs the count evenly into groups of|raises the count by) ([0-9]+)( percent)?",
                        sentence,
                    )
                    if match is None:
                        continue
                    action, raw_operand, _ = match.groups()
                    operand = int(raw_operand)
                    if action == "adds":
                        value += operand
                    elif action == "removes":
                        value -= operand
                    elif action == "multiplies the count by":
                        value *= operand
                    elif action == "packs the count evenly into groups of":
                        self.assertEqual(value % operand, 0)
                        value //= operand
                    else:
                        value = value * (100 + operand) // 100
                self.assertEqual(value, trace["verified_answer"])
                self.assertEqual(value, content.annotations["ground_truth"]["answer"])
            else:
                saw_logic = True
                constraints = re.findall(r"([A-Z][a-z]+) arrived before ([A-Z][a-z]+)\.", text)
                names = sorted(set(itertools.chain.from_iterable(constraints)))
                valid = [
                    perm
                    for perm in itertools.permutations(names)
                    if all(perm.index(a) < perm.index(b) for a, b in constraints)
                ]
                self.assertEqual(len(valid), 1)
                self.assertEqual(valid[0][2], trace["answer"])
        self.assertTrue(saw_arithmetic)
        self.assertTrue(saw_logic)

    def test_per_category_determinism_prompt_text(self) -> None:
        funcs = [generate_chat, generate_code, generate_summ, generate_reason, generate_json, generate_multiling]
        for func in funcs:
            seed = item_seed("determinism", func.__name__, 0)
            kwargs = {"profile_index": 2} if func is generate_multiling else {}
            first = func(seed, QuirkyFakeTokenizer(), tokenizer_id=self.fake_tokenizer_id(), **kwargs)
            second = func(seed, QuirkyFakeTokenizer(), tokenizer_id=self.fake_tokenizer_id(), **kwargs)
            self.assertEqual(first.prompt_text, second.prompt_text)
            self.assertEqual(
                json.dumps(first.annotations, sort_keys=True),
                json.dumps(second.annotations, sort_keys=True),
            )

    def test_sentinel_ids_native_shape_and_sources(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        build = build_sentinel_suite(
            "sentinel-seed",
            tokenizer,
            tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
        )
        SuiteManifest.from_mapping(build.manifest)
        self.assertEqual(
            [item["grouping"]["condition_id"] for item in build.manifest["items"]],
            SENTINEL_CONDITIONS,
        )
        self.assertEqual(
            [item["grouping"]["condition_id"] for item in build.manifest["items"]],
            ["repeated_seed", "random_token", "natural_prose", "code_like", "multilingual"],
        )
        for item in build.manifest["items"]:
            ids = item["source"]["prompt_token_ids"]
            self.assertEqual(len(ids), 512)
            self.assertNotIn("prompt_text", item["source"])
            self.assertEqual(item["item_type"], "ids_prompt")
            self.assertEqual(item["shape"]["planned_prompt_tokens"], 512)
            self.assertNotEqual(ids[0], tokenizer.bos_token_id)
            ann = build.annotations["items"][item["item_id"]]
            self.assertFalse(ann["bos_present"])
            self.assertEqual(ann["prompt_source"], "token_ids")

    def test_repeated_seed_mirrors_mlx_recipe(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        seed = tokenizer.encode("JouleWise synthetic prompt token sequence.", add_special_tokens=False)
        expected = []
        while len(expected) < 512:
            expected.extend(seed)
        expected = expected[:512]
        self.assertEqual(repeated_seed_ids(tokenizer, 512), expected)
        content = sentinel_content(
            "repeated_seed",
            123,
            tokenizer,
            tokenizer_id=self.fake_tokenizer_id(),
        )
        self.assertEqual(content.prompt_token_ids, expected)

    def test_repeated_seed_mirrors_mlx_runtime_recipe(self) -> None:
        try:
            mlx_runtime = importlib.import_module("joulewise.adapters.mlx_runtime")
        except ImportError as exc:
            self.skipTest(f"mlx runtime not importable: {exc}")
        tokenizer = QuirkyFakeTokenizer()
        expected = []
        seed = tokenizer.encode("JouleWise synthetic prompt token sequence.", add_special_tokens=False)
        while len(expected) < 512:
            expected.extend(seed)
        expected = expected[:512]
        self.assertEqual(repeated_seed_ids(tokenizer, 512), expected)
        self.assertEqual(mlx_runtime._synthetic_prompt_tokens(tokenizer, 512), expected)

    def test_random_token_excludes_special_and_empty_decode_ids(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        ids = random_token_ids(tokenizer, 123, 512)
        forbidden = tokenizer.special_token_ids | tokenizer.empty_decode_ids
        self.assertFalse(any(token_id in forbidden for token_id in ids))

    def test_manifest_builders_validate_and_keep_blocks_contiguous(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        mixed = build_jw_mixed_suite(
            "manifest-seed",
            tokenizer,
            tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
            items_per_category=2,
        )
        sentinel = build_sentinel_suite(
            "manifest-seed",
            tokenizer,
            tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
        )
        for build in (mixed, sentinel):
            manifest = SuiteManifest.from_mapping(build.manifest)
            self.assertEqual(len(manifest.items), len(build.manifest["items"]))
            blocks = [item["grouping"]["block_id"] for item in build.manifest["items"]]
            for block in set(blocks):
                indices = [i for i, value in enumerate(blocks) if value == block]
                self.assertEqual(indices, list(range(min(indices), max(indices) + 1)))
            self.assertTrue(all(item["output_policy"] == "fixed_budget_exact" for item in build.manifest["items"]))
            self.assertTrue(all(item["status_policy"] == "none" for item in build.manifest["items"]))

    def test_manifest_builders_write_sidecars_without_manifest_annotations(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        with tempfile.TemporaryDirectory() as tmp:
            sidecar = Path(tmp) / "suite.annotations.json"
            manifest = build_jw_mixed_manifest(
                "sidecar-seed",
                tokenizer,
                tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
                sidecar_path=sidecar,
                items_per_category=1,
            )
            self.assertTrue(sidecar.exists())
            self.assertNotIn("annotations", manifest)
            SuiteManifest.from_mapping(manifest)
            sidecar_data = json.loads(sidecar.read_text(encoding="utf-8"))
            self.assertEqual(sidecar_data["tokenizer"]["files"], [
                {"filename": "fake-merges.txt", "sha256": "1" * 64},
                {"filename": "fake-tokenizer.json", "sha256": "0" * 64},
            ])
            self.assertEqual(
                manifest["source_manifest"]["source_id"],
                "jw_mixed_v1:" + sidecar_data["tokenizer"]["tokenizer_id"],
            )
            self.assertEqual(
                manifest["source_manifest"]["subset_sha256"],
                sidecar_data["source_manifest"]["subset_sha256"],
            )

            sent_sidecar = Path(tmp) / "sentinel.annotations.json"
            sent_manifest = build_sentinel_manifest(
                "sidecar-seed",
                tokenizer,
                tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
                sidecar_path=sent_sidecar,
            )
            self.assertTrue(sent_sidecar.exists())
            self.assertNotIn("annotations", sent_manifest)
            SuiteManifest.from_mapping(sent_manifest)

    def test_missing_tokenizer_manifest_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            build_jw_mixed_suite("missing-manifest", QuirkyFakeTokenizer(), items_per_category=1)

    def test_bank_hash_fails_closed_on_mutation(self) -> None:
        original = list(gensuite._BANKS["personas"])
        try:
            gensuite._BANKS["personas"].append("mutated persona")
            with self.assertRaises(AssertionError):
                gensuite._assert_bank_hash()
        finally:
            gensuite._BANKS["personas"] = original
            gensuite._assert_bank_hash()

    def test_per_generator_token_identity_and_hash(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        funcs = [generate_chat, generate_code, generate_summ, generate_reason, generate_json, generate_multiling]
        for func in funcs:
            kwargs = {"profile_index": 1} if func is generate_multiling else {}
            content = func(
                item_seed("token-identity", func.__name__, 0),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
                **kwargs,
            )
            self.assertEqual(
                content.prompt_token_ids,
                tokenizer.encode(content.prompt_text or "", add_special_tokens=True),
            )
            self.assertEqual(
                content.annotations["token_ids_sha256"],
                prompt_token_ids_sha256(content.prompt_token_ids),
            )

    def test_category_level_impossibly_small_budget_fails_closed(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        funcs = [generate_chat, generate_code, generate_summ, generate_reason, generate_json, generate_multiling]
        for func in funcs:
            kwargs = {"profile_index": 1} if func is generate_multiling else {}
            with self.assertRaises(ShapeError):
                func(
                    item_seed("tiny", func.__name__, 0),
                    tokenizer,
                    prompt_budget=3,
                    tokenizer_id=self.fake_tokenizer_id(),
                    **kwargs,
                )

    def test_needles_are_requested_realized_and_present(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        for index in range(10):
            content = generate_summ(
                item_seed("needles", "jw.summ", index),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
            )
            self.assertEqual(content.annotations["requested_needles"], content.annotations["realized_needles"])
            self.assertEqual(
                content.annotations["realized_needles"],
                len(content.annotations["needle_positions"]),
            )
            for needle in content.annotations["needle_positions"]:
                self.assertIn(needle["needle"], content.prompt_text or "")

    def test_multilingual_ascii_tail_is_final_and_bounded(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        for index in range(40):
            content = generate_multiling(
                item_seed("ascii-tail", "jw.multiling", index),
                tokenizer,
                tokenizer_id=self.fake_tokenizer_id(),
                profile_index=index,
            )
            tail_tokens = content.annotations["ascii_tail_tokens"]
            self.assertLessEqual(tail_tokens, 3)
            text = content.prompt_text or ""
            digit_positions = [i for i, ch in enumerate(text) if ch.isascii() and ch.isdigit()]
            if tail_tokens:
                self.assertTrue(digit_positions)
                suffix = text[min(digit_positions) :]
                self.assertTrue(all(ch.isascii() and (ch.isdigit() or ch.isspace()) for ch in suffix))
            else:
                self.assertFalse(digit_positions)

    def test_manifest_and_sidecar_bytes_are_deterministic(self) -> None:
        tokenizer = QuirkyFakeTokenizer()
        with tempfile.TemporaryDirectory() as tmp:
            builders = [
                (
                    "mixed",
                    lambda sidecar: build_jw_mixed_manifest(
                        "deterministic",
                        tokenizer,
                        tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
                        sidecar_path=sidecar,
                        items_per_category=1,
                    ),
                ),
                (
                    "sentinel",
                    lambda sidecar: build_sentinel_manifest(
                        "deterministic",
                        tokenizer,
                        tokenizer_manifest=FAKE_TOKENIZER_MANIFEST,
                        sidecar_path=sidecar,
                    ),
                ),
            ]
            for name, builder in builders:
                first_manifest = Path(tmp) / f"{name}.first.json"
                first_sidecar = Path(tmp) / f"{name}.first.annotations.json"
                second_manifest = Path(tmp) / f"{name}.second.json"
                second_sidecar = Path(tmp) / f"{name}.second.annotations.json"
                first = builder(first_sidecar)
                second = builder(second_sidecar)
                first_manifest.write_text(
                    json.dumps(first, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                second_manifest.write_text(
                    json.dumps(second, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                self.assertEqual(first_manifest.read_bytes(), second_manifest.read_bytes())
                self.assertEqual(first_sidecar.read_bytes(), second_sidecar.read_bytes())


if __name__ == "__main__":
    unittest.main()
