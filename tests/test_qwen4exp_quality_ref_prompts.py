"""Prompt builder for the bf16 quality reference (lead ruling L3).

Synthetic tokenizers only; the real tokenizer at the pinned revision is
fetched by the lead's command (docs/align/qwen4_exp_port/quant_quality.md).
"""
import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quality_ref_prompts", ROOT / "scripts" / "qwen4exp_quality_ref_prompts.py")
qref = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qref)
e2e = qref.e2e
HAS_JINJA = importlib.util.find_spec("jinja2") is not None
FIXTURE_TEMPLATE = ROOT / "tests" / "fixtures" / "qwen4exp_chat_template.jinja"
PIECES = r"\s*(?:\w+|[^\w\s])|\s+"  # BPE-like: leading whitespace joins the next piece


class FakeTokenizer:
    """Word/punctuation tokenizer; template control tokens map to their official ids."""
    def __init__(self):
        self.special = sorted(e2e.SPECIAL_TOKENS.items(), key=lambda kv: -len(kv[0]))
        self.vocab, self.inverse = {}, {}

    def _id(self, piece):
        if piece not in self.vocab:
            self.vocab[piece] = 1000 + int(hashlib.sha256(piece.encode()).hexdigest()[:8], 16) % 200_000
            self.inverse[self.vocab[piece]] = piece
        return self.vocab[piece]

    def encode(self, text, add_special_tokens=True):
        assert add_special_tokens is False
        ids, rest = [], text
        pattern = "(" + "|".join(re.escape(t) for t, _ in self.special) + ")"
        for chunk in re.split(pattern, rest):
            if chunk in e2e.SPECIAL_TOKENS:
                ids.append(e2e.SPECIAL_TOKENS[chunk])
            else:
                ids += [self._id(p) for p in re.findall(PIECES, chunk)]
        return ids

    def decode(self, ids):
        names = {v: k for k, v in e2e.SPECIAL_TOKENS.items()}
        return "".join(names.get(i, self.inverse.get(i, "")) for i in ids)


def nll_texts():
    return {e["id"]: e for e in e2e.load_items()["nll"]}


class ContinuationTableTests(unittest.TestCase):
    def test_table_covers_exactly_the_hosted_prompts_with_unique_pinned_anchors(self):
        spec = json.loads(qref.PROMPTS_PATH.read_text())
        self.assertEqual(sorted(p["id"] for p in spec["prompts"]), sorted(qref.CONTINUATIONS))
        texts = nll_texts()
        for prompt, (source, anchor) in qref.CONTINUATIONS.items():
            self.assertEqual(texts[source]["kind"], "natural", prompt)  # never the shuffled control
            self.assertEqual(texts[source]["text"].count(anchor), 1, prompt)

    def test_missing_or_ambiguous_anchor_refuses(self):
        with self.assertRaises(ValueError):
            qref.continuation_text({"x": "a b a"}, "x", "a")
        with self.assertRaises(ValueError):
            qref.continuation_text({"x": "a b"}, "x", "c")


@unittest.skipUnless(HAS_JINJA, "jinja2 renders the pinned template")
class BuildPromptsTests(unittest.TestCase):
    def build(self, **kw):
        tokenizer = FakeTokenizer()
        encode = lambda s: tokenizer.encode(s, add_special_tokens=False)
        template = e2e.ChatTemplate(FIXTURE_TEMPLATE)
        spec = json.loads(qref.PROMPTS_PATH.read_text())
        rows, provenance = qref.build_prompts(encode, template, spec, e2e.load_items(), **kw)
        return rows, provenance, encode, template, spec

    def test_twelve_prompts_each_at_most_512_tokens_with_fixed_text_continuations(self):
        rows, provenance, encode, template, spec = self.build()
        self.assertEqual(len(rows), 12)
        texts = nll_texts()
        from joulewise.align.qwen4_gold.runner import load_prompts
        self.assertEqual(len(load_prompts_from(rows, load_prompts)), 12)  # gold stream accepts them
        for row, record, prompt in zip(rows, provenance, spec["prompts"]):
            self.assertLessEqual(len(row["input_ids"]), 512)
            self.assertEqual(row["name"], "hosted-" + prompt["id"])
            cut = row["continuation_from"]
            source, anchor = qref.CONTINUATIONS[prompt["id"]]
            text = texts[source]["text"]
            expected = encode(text[text.index(anchor):][:qref.SOURCE_CHARS])
            tail = row["input_ids"][cut:]
            self.assertGreaterEqual(len(tail), qref.MIN_CONTINUATION_TOKENS)
            self.assertLessEqual(len(tail), qref.CONTINUATION_TOKENS)
            self.assertEqual(tail, expected[:len(tail)])  # the pinned text, never model output
            self.assertEqual(record["continuation"]["source_sha256"], texts[source]["sha256"])
            if "context_from" not in prompt:
                rendered = template.render(prompt["messages"], prompt.get("tools"), add_generation_prompt=True,
                                           enable_thinking=False)
                self.assertEqual(row["input_ids"][:cut], encode(rendered))
                self.assertTrue(rendered.endswith("<think>\n\n</think>\n\n"))  # thinking off

    def test_long_context_is_cut_at_a_paragraph_boundary_to_fit(self):
        rows, provenance, *_ = self.build()
        record = next(p for p in provenance if p["name"] == "hosted-long_context_qsa")
        context = nll_texts()["pp_ch1_3_long"]["text"]
        self.assertTrue(record["context"]["context_truncated"])
        prefix = context[:record["context"]["context_chars"]]
        self.assertEqual(prefix, "\n\n".join(context.split("\n\n")[:record["context"]["context_paragraphs"]]))
        self.assertEqual(record["continuation_tokens"], qref.CONTINUATION_TOKENS)
        self.assertLessEqual(record["total_tokens"], 512)

    def test_deterministic_and_budget_enforced(self):
        first = self.build()[0]
        self.assertEqual(first, self.build()[0])
        small, records, *_ = self.build(max_tokens=400, continuation_tokens=64)
        self.assertTrue(all(len(r["input_ids"]) <= 400 for r in small))
        with self.assertRaises(ValueError):  # the tool prompt alone leaves no room
            self.build(max_tokens=300, continuation_tokens=40)


def load_prompts_from(rows, load_prompts):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "p.json"
        path.write_text(json.dumps(rows))
        return load_prompts(str(path), {"vocab_size": e2e.VOCAB_SIZE})


class FakeInfo(types.SimpleNamespace):
    pass


class TokenizerPinTests(unittest.TestCase):
    def fake_hub(self, files, tamper=None):
        infos = []
        for name, raw in files.items():
            lfs = types.SimpleNamespace(sha256=hashlib.sha256(raw).hexdigest()) if name == "tokenizer.json" else None
            infos.append(FakeInfo(path=name, size=len(raw), lfs=lfs, blob_id=qref.git_blob_sha1(raw)))
        calls = []

        class API:
            def get_paths_info(self, repo, paths, revision):
                calls.append(("info", repo, revision))
                return [i for i in infos if i.path in paths]

        def download(repo, name, revision, local_dir):
            calls.append(("download", repo, name, revision))
            path = Path(local_dir) / name
            path.write_bytes(files[name] + (b"x" if name == tamper else b""))
            return str(path)
        return API(), download, calls

    def files(self):
        return {"tokenizer.json": b'{"model": "fake"}', "tokenizer_config.json": b"{}",
                "chat_template.jinja": FIXTURE_TEMPLATE.read_bytes()}

    def test_fetch_pins_every_file_at_the_pinned_revision(self):
        with tempfile.TemporaryDirectory() as d:
            api, download, calls = self.fake_hub(self.files())
            pins = qref.fetch_tokenizer(Path(d) / "tok", api, download)
            self.assertEqual(sorted(pins["files"]), sorted(self.files()))
            self.assertTrue(all(c[-1] == qref.REVISION for c in calls))
            self.assertEqual(qref.REVISION, "de4b8e4d43b917e7706784d8bb445c9af86a3540")
            self.assertIn("lfs_sha256", pins["files"]["tokenizer.json"])
            self.assertIn("git_blob_id", pins["files"]["tokenizer_config.json"])
            qref.verify_tokenizer_dir(Path(d) / "tok")
            for tampered in ("tokenizer.json", "tokenizer_config.json"):
                api, download, _ = self.fake_hub(self.files(), tamper=tampered)
                with self.assertRaises(ValueError):
                    qref.fetch_tokenizer(Path(d) / ("bad-" + tampered), api, download)
            files = self.files(); del files["chat_template.jinja"]
            api, download, _ = self.fake_hub(files)
            with self.assertRaisesRegex(ValueError, "lacks"):
                qref.fetch_tokenizer(Path(d) / "missing", api, download)

    @unittest.skipUnless(HAS_JINJA, "jinja2 renders the pinned template")
    def test_build_writes_prompts_and_provenance_and_refuses_changed_files(self):
        with tempfile.TemporaryDirectory() as d:
            api, download, _ = self.fake_hub(self.files())
            tok = Path(d) / "tok"
            qref.fetch_tokenizer(tok, api, download)
            out = Path(d) / "run" / "prompts.json"
            self.assertEqual(qref.main(["build", "--tokenizer-dir", str(tok), "--out", str(out)],
                                       tokenizer=FakeTokenizer()), 0)
            rows = json.loads(out.read_text())
            record = json.loads((out.parent / "prompts.json.provenance.json").read_text())
            self.assertEqual(len(rows), 12)
            self.assertEqual(record["prompts_json_sha256"], hashlib.sha256(out.read_bytes()).hexdigest())
            self.assertEqual(record["tokenizer"]["revision"], qref.REVISION)
            self.assertTrue(record["tokenizer"]["preflight"]["ok"])
            self.assertEqual(record["template_sha256"], e2e.TEMPLATE_SHA256)
            self.assertEqual(record["total_tokens"], sum(len(r["input_ids"]) for r in rows))
            with self.assertRaisesRegex(ValueError, "512"):
                qref.main(["build", "--tokenizer-dir", str(tok), "--out", str(out), "--max-tokens", "600"],
                          tokenizer=FakeTokenizer())
            (tok / "tokenizer.json").write_bytes(b'{"model": "other"}')
            with self.assertRaisesRegex(ValueError, "changed since it was pinned"):
                qref.main(["build", "--tokenizer-dir", str(tok), "--out", str(out)], tokenizer=FakeTokenizer())
            shutil.rmtree(tok)
            with self.assertRaisesRegex(ValueError, "fetch-tokenizer"):
                qref.main(["build", "--tokenizer-dir", str(tok), "--out", str(out)], tokenizer=FakeTokenizer())

    @unittest.skipUnless(HAS_JINJA, "jinja2 renders the pinned template")
    def test_preflight_rejects_a_tokenizer_without_the_official_control_ids(self):
        class Plain(FakeTokenizer):
            def encode(self, text, add_special_tokens=True):
                return [self._id(p) for p in re.findall(PIECES, text)]
        with tempfile.TemporaryDirectory() as d:
            api, download, _ = self.fake_hub(self.files())
            tok = Path(d) / "tok"
            qref.fetch_tokenizer(tok, api, download)
            with self.assertRaisesRegex(ValueError, "preflight"):
                qref.main(["build", "--tokenizer-dir", str(tok), "--out", str(Path(d) / "p.json")], tokenizer=Plain())


if __name__ == "__main__":
    unittest.main()
