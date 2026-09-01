```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Implemented the ruled G2-a authenticated receipt and hash-bound prefill-pin bundle chain.","workspace":{"base_requested":"main","base_mode":"informational","head_start":"82e7519d","head_end":"82e7519d","upstream_end":"82e7519d","branch":"feat/2026-09-01-g2a-probe"},"pathspec":["configs/campaigns/d117_contrast_v5/generate_configs.py","docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md","scripts/gen_g2_phase_d.py","scripts/generate_g2a_probe_inputs.py","scripts/issue_g2a_prefill_prompt_pin.py","scripts/summarize_g2a_prefill_probe.py","tests/fixtures/g2a/probes/short-prompt-corpus.txt","tests/test_d117_contrast_v5_pack.py","tests/test_generate_g2a_probe_inputs.py","tests/test_issue_g2a_prefill_prompt_pin.py","tests/test_summarize_g2a_prefill_probe.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_generate_g2a_probe_inputs tests.test_summarize_g2a_prefill_probe tests.test_issue_g2a_prefill_prompt_pin tests.test_d117_contrast_v5_pack tests.test_check_window_provenance && python3 scripts/gen_g2_phase_d.py --check && git diff --check && git diff --stat","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 89 tests in 15.773s","OK","PASS generated Phase D matches pinned runbook bytes"]},"expected":{"exit_code":0,"tail_regex":"Ran 89 tests.*OK.*PASS generated Phase D matches pinned runbook bytes"}},{"id":"V2","kind":"test","cmd":"Compute SHA-256 of frozen dominance_criterion_registration() bytes from HEAD and worktree.","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b","1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"]},"expected":{"exit_code":0,"tail_regex":"^1c0a4a.*\\n1c0a4a.*$"}}],"flags":[{"id":"F1","kind":"baseline_drift","level":"nonblocking","text":"Local main and the task branch are divergent; per the ruling, no rebase was run.","needs":""}]}
```

## Change

| Finding | Cure | Regression |
|---|---|---|
| B2, L-F1–F3 | Summarizer writes an authenticated receipt, validates recorded `config.json` bytes and realized prompt provenance, and emits below-floor rows for lost runs. | Run-ID/config-hash mutations and missing-small-run rows |
| B3, B6, S1 | Inventory binds MLX adapter hash and bind-time HEAD; check requires the exact policy; corpus option/fixture removed. | Adapter/policy drift tests |
| B4, D-3, B5 | Issuer emits closing sentence, trace pair, panel hash, ladder/selection references, and copies the bundle. | Receipt-linkage and issued-pin loader tests |
| L-F4, L-F5 | Loader hashes panel bytes, ladder, and selection record; compares the selected rung field-by-field without model/tokenizer reads. | Panel, token-ID, generation, repeat-count, selection path/hash mutations |
| S2, D-1, D-5 | Runsheet now defines the full receipt→selection→issuer→V5 desk chain, raw-rendering wording, and budget disclosure. | Generated-region check |

Guard table: inventory/adapter/policy → `test_generate_g2a_probe_inputs`; live-run receipt provenance → `test_summarize_g2a_prefill_probe`; issuer linkage → `test_issue_g2a_prefill_prompt_pin`; loader bundle/panel/rung checks → `test_d117_contrast_v5_pack`.

Registration hash: before = after = `1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b`.

`git diff --stat`: 11 files changed, 920 insertions, 143 deletions.

Full amended test diff:

```diff
diff --git a/tests/test_d117_contrast_v5_pack.py b/tests/test_d117_contrast_v5_pack.py
index 5e8b8940..4051bcee 100644
--- a/tests/test_d117_contrast_v5_pack.py
+++ b/tests/test_d117_contrast_v5_pack.py
@@ -211,16 +211,58 @@ class D117ContrastV5PackTests(unittest.TestCase):
         self.generator = load_generator()
 
     def write_prefill_pin(self, root: Path, length: int = 512) -> Path:
-        token_ids = [7] * length
-        text = "TEST FIXTURE ONLY: post-G2 prompt-pin plumbing."
+        tokenizer_sha = (
+            "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
+        )
+        panel_sha = hashlib.sha256(PANEL.read_bytes()).hexdigest()
+        selection_path = root / "selection-record.json"
+        selection_path.write_text('{"fixture":"selection"}\n', encoding="utf-8")
+        selection_sha = hashlib.sha256(selection_path.read_bytes()).hexdigest()
+
+        def rung(token_count: int) -> dict[str, object]:
+            closing = f"Fixture closing sentence for {token_count}."
+            text = " ".join([self.generator.PROMPT_SENTENCE, closing])
+            token_ids = [token_count] * token_count
+            return {
+                "prefill_tokens": token_count,
+                "repeat_count": 1,
+                "closing_sentence": closing,
+                "prompt_text": text,
+                "prompt_text_utf8_sha256": hashlib.sha256(text.encode()).hexdigest(),
+                "prompt_token_ids": token_ids,
+                "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
+                "generation_method": (
+                    f"1 x '{self.generator.PROMPT_SENTENCE}' + '{closing}' under "
+                    f"tokenizer sha256:{tokenizer_sha}"
+                ),
+            }
+
+        target = rung(length)
+        companion = rung(1024 if length != 1024 else 512)
+        ladder_path = root / "prompt-ladder.json"
+        ladder_path.write_text(
+            json.dumps(
+                {
+                    "schema_version": "joulewise.g2a_prefill_prompt_ladder.v1",
+                    "prompt_sentence": self.generator.PROMPT_SENTENCE,
+                    "tokenizer_json_sha256": tokenizer_sha,
+                    "panel_thinking_policy": {
+                        "enable_thinking": "false",
+                        "panel_sha256": panel_sha,
+                    },
+                    "rungs": [target, companion],
+                }
+            ),
+            encoding="utf-8",
+        )
         value = {
             "schema_version": "joulewise.prefill_prompt_pin.v2",
             "selection_authority": {
                 "g2a_record": {
-                    "record_id": "test_fixture_only_not_production_evidence",
-                    "path": "test-fixtures/g2a-record.json",
+                    "record_id": f"sha256:{selection_sha}",
+                    "path": selection_path.name,
                 },
-                "ruling_trace_path": PREFILL_RULING_TRACE_PATH,
+                "ruling_trace_paths": list(self.generator.PREFILL_RULING_TRACE_PATHS),
             },
             "ladder_prompt_tokens": [512, 1024, 2048, 4096],
             "min_small_model_members_per_rung": 5,
@@ -228,19 +270,24 @@ class D117ContrastV5PackTests(unittest.TestCase):
             "min_phase_samples_pinned": 3,
             "sample_count_margin_floor": 2,
             "selection_expression": PREFILL_SELECTION_EXPRESSION,
-            "g2a_record_sha256": "b" * 64,
+            "g2a_record_sha256": selection_sha,
+            "selection_record": {"path": selection_path.name, "sha256": selection_sha},
+            "prompt_ladder": {
+                "path": ladder_path.name,
+                "sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
+            },
+            "panel_sha256": panel_sha,
             "exhausted_ladder_branch": copy.deepcopy(PREFILL_EXHAUSTED_LADDER_BRANCH),
             "prefill_length": length,
-            "tokenizer_json_sha256": (
-                "aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"
-            ),
-            "prompt_text": text,
-            "prompt_text_utf8_sha256": hashlib.sha256(text.encode()).hexdigest(),
-            "prompt_token_ids": token_ids,
-            "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
+            "tokenizer_json_sha256": tokenizer_sha,
+            "prompt_text": target["prompt_text"],
+            "prompt_text_utf8_sha256": target["prompt_text_utf8_sha256"],
+            "prompt_token_ids": target["prompt_token_ids"],
+            "prompt_token_ids_sha256": target["prompt_token_ids_sha256"],
             "prompt_tokens": length,
-            "repeat_count": 1,
-            "generation_method": "test_fixture_only",
+            "repeat_count": target["repeat_count"],
+            "closing_sentence": target["closing_sentence"],
+            "generation_method": target["generation_method"],
         }
@@ -375,6 +422,72 @@ class D117ContrastV5PackTests(unittest.TestCase):
             with self.assertRaisesRegex(ValueError, "prefill_g2a_record_hash_unresolved"):
                 self.configure(pin)
 
+    def test_prefill_prompt_pin_bundle_and_ladder_mutations_refuse(self) -> None:
+        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-bundle-") as temporary:
+            root = Path(temporary)
+            pin = self.write_prefill_pin(root)
+            value = json.loads(pin.read_text())
+            ladder_path = root / value["prompt_ladder"]["path"]
+
+            value["panel_sha256"] = "0" * 64
+            pin.write_text(json.dumps(value), encoding="utf-8")
+            with self.assertRaisesRegex(ValueError, "prefill_prompt_pin_panel_sha256_mismatch"):
+                self.configure(pin)
+
+        cases = {
+            "token_ids": (
+                lambda value: (
+                    value["prompt_token_ids"].__setitem__(0, 999),
+                    value.__setitem__(
+                        "prompt_token_ids_sha256",
+                        prompt_token_ids_sha256(value["prompt_token_ids"]),
+                    ),
+                ),
+                "prefill_prompt_pin_ladder_rung_mismatch: prompt_token_ids",
+            ),
+            "generation_method": (
+                lambda value: value.__setitem__("generation_method", "edited"),
+                "prefill_prompt_pin_ladder_rung_mismatch: generation_method",
+            ),
+            "repeat_count": (
+                lambda value: value.__setitem__("repeat_count", 2),
+                "prefill_prompt_pin_ladder_rung_mismatch: repeat_count",
+            ),
+            "selection_path": (
+                lambda value: value["selection_record"].__setitem__("path", "missing.json"),
+                "selection_record_missing",
+            ),
+            "selection_hash": (
+                lambda value: value["selection_record"].__setitem__("sha256", "0" * 64),
+                "selection_record_sha256_mismatch",
+            ),
+        }
+        for name, (mutate, reason) in cases.items():
+            with self.subTest(name=name), tempfile.TemporaryDirectory(
+                prefix="d117-v5-pin-bundle-"
+            ) as temporary:
+                pin = self.write_prefill_pin(Path(temporary))
+                value = json.loads(pin.read_text())
+                mutate(value)
+                pin.write_text(json.dumps(value), encoding="utf-8")
+                with self.assertRaisesRegex(ValueError, reason):
+                    self.configure(pin)
+
+        with tempfile.TemporaryDirectory(prefix="d117-v5-pin-bundle-") as temporary:
+            root = Path(temporary)
+            pin = self.write_prefill_pin(root)
+            value = json.loads(pin.read_text())
+            ladder_path = root / value["prompt_ladder"]["path"]
+            ladder = json.loads(ladder_path.read_text())
+            ladder["panel_thinking_policy"]["panel_sha256"] = "0" * 64
+            ladder_path.write_text(json.dumps(ladder), encoding="utf-8")
+            value["prompt_ladder"]["sha256"] = hashlib.sha256(
+                ladder_path.read_bytes()
+            ).hexdigest()
+            pin.write_text(json.dumps(value), encoding="utf-8")
+            with self.assertRaisesRegex(ValueError, "prefill_prompt_pin_panel_sha256_mismatch"):
+                self.configure(pin)
```

## Verification notes

The failing-looking refusal lines are intentional mutation regressions. The summary hashes the actual run bundle’s `config.json`, written by `joulewise/bundle.py:953`.

## Residual risk

`main` is divergent locally; no rebase was run per your ruling.