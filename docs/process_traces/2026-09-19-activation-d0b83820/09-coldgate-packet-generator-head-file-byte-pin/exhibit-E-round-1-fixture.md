# Exhibit E — the round-1 fixture on the repair branch (verbatim `git diff 2f79e633..d3c8b3559a3c635e43de46e98918e0e468201919` for the two generator-running modules)

```diff
diff --git a/tests/test_campaign_generator_core.py b/tests/test_campaign_generator_core.py
index 9335d883..49efd533 100644
--- a/tests/test_campaign_generator_core.py
+++ b/tests/test_campaign_generator_core.py
@@ -2,6 +2,8 @@
 
 from __future__ import annotations
 
+from contextlib import nullcontext
+import hashlib
 import importlib.util
 import sys
 import tempfile
@@ -19,6 +21,18 @@ from scripts.check_campaign_generator_core_parity import (
 
 
 ROOT = Path(__file__).resolve().parents[1]
+# Generation-time bytes from a816036f4ea278fcc746b1220896b4b6bd084855:
+# git show a816036f:configs/calibration/calibration_ledger_head.json
+GENERATION_LEDGER_HEAD_BYTES = (
+    b'{\n'
+    b'  "sequence": 76,\n'
+    b'  "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",\n'
+    b'  "ledger_schema": "joulewise.calibration_observation_ledger.v1"\n'
+    b'}\n'
+)
+GENERATION_LEDGER_HEAD_SHA256 = (
+    "6bbe26258165bbd11ca996324a5862c2e6e34faae7999b6c06f5e12f27ac2902"
+)
 D117_GENERATORS = tuple(
     sorted((ROOT / "configs/campaigns").glob("d117_*/generate_configs.py"))
 )
@@ -101,9 +115,34 @@ class CampaignGeneratorCoreTests(unittest.TestCase):
                         lambda source=source: source
                     )
                 configure_generator(label, generator, pin)
+                head_fixture = nullcontext()
+                # GENERATOR-HEAD-FILE-BYTE-PIN-01 is registered for the cold
+                # gate: the production byte pin on an append-advancing file
+                # remains unchanged. Exercise the generator as a function of
+                # its declared inputs, for normal and mutated source alike.
+                if label in ("ALPHA", "BETA"):
+                    fixture_digest = hashlib.sha256(
+                        GENERATION_LEDGER_HEAD_BYTES
+                    ).hexdigest()
+                    self.assertEqual(fixture_digest, GENERATION_LEDGER_HEAD_SHA256)
+                    real_sha256_file = generator.sha256_file
+                    head_path = generator.REPO_ROOT / generator.LEDGER_HEAD_REL
+
+                    def fixture_sha256_file(
+                        path, *, head_path=head_path,
+                        real_sha256_file=real_sha256_file,
+                        fixture_digest=fixture_digest,
+                    ):
+                        if path == head_path:
+                            return fixture_digest
+                        return real_sha256_file(path)
+
+                    head_fixture = mock.patch.object(
+                        generator, "sha256_file", side_effect=fixture_sha256_file
+                    )
                 output_root = temporary / label.lower()
                 calls: list[tuple[Path, tuple[Path, ...]]] = []
-                with mock.patch.object(
+                with head_fixture as head_mock, mock.patch.object(
                     core,
                     "_generation_write_boundary_observer",
                     side_effect=lambda root, outputs: calls.append(
@@ -111,6 +150,13 @@ class CampaignGeneratorCoreTests(unittest.TestCase):
                     ),
                 ):
                     generate(generator, label, output_root)
+                if head_mock is not None:
+                    # The fixture must have been consulted for the head path,
+                    # or a future edit could route around it silently
+                    # (counter-review record 15 N1).
+                    self.assertIn(
+                        mock.call(head_path), head_mock.call_args_list
+                    )
 
                 final_calls = [
                     outputs
diff --git a/tests/test_d117_floor_qwen3_v5_generate.py b/tests/test_d117_floor_qwen3_v5_generate.py
index 59b3d7c4..bbd6e2a8 100644
--- a/tests/test_d117_floor_qwen3_v5_generate.py
+++ b/tests/test_d117_floor_qwen3_v5_generate.py
@@ -6,6 +6,7 @@ import ast
 import hashlib
 import importlib.util
 import json
+import shutil
 import subprocess
 import sys
 import tempfile
@@ -17,6 +18,10 @@ from joulewise.dominance_closeout import ABSOLUTE_COMMON_MODE_REASON
 from joulewise.provenance import prompt_token_ids_sha256
 from scripts import issue_g2a_prefill_prompt_pin as issuer
 from scripts import select_g2a_prefill_length as selector
+from tests.test_campaign_generator_core import (
+    GENERATION_LEDGER_HEAD_BYTES,
+    GENERATION_LEDGER_HEAD_SHA256,
+)
 
 
 ROOT = Path(__file__).resolve().parents[1]
@@ -46,8 +51,8 @@ MODEL_PANEL_ROWS = {
 }
 
 
-def load_generator(pack_id: str):
-    path = ROOT / "configs/campaigns" / pack_id / "generate_configs.py"
+def load_generator(pack_id: str, *, repository: Path = ROOT):
+    path = repository / "configs/campaigns" / pack_id / "generate_configs.py"
     spec = importlib.util.spec_from_file_location(f"{pack_id}_generator", path)
     assert spec is not None and spec.loader is not None
     module = importlib.util.module_from_spec(spec)
@@ -268,6 +273,29 @@ def family_marker(members: list[dict[str, object]]) -> dict[str, object]:
 class D117FloorQwen3V5PackTests(unittest.TestCase):
     maxDiff = None
 
+    def generation_repository(self, root: Path) -> Path:
+        """Give in-process and subprocess generation the same historical input."""
+        repository = root / "repository"
+        subprocess.run(
+            ("git", "clone", "-q", "--shared", str(ROOT), str(repository)),
+            check=True,
+            capture_output=True,
+        )
+        self.assertEqual(
+            hashlib.sha256(GENERATION_LEDGER_HEAD_BYTES).hexdigest(),
+            GENERATION_LEDGER_HEAD_SHA256,
+        )
+        (repository / "configs/calibration/calibration_ledger_head.json").write_bytes(
+            GENERATION_LEDGER_HEAD_BYTES
+        )
+        # The clone carries COMMITTED bytes; grade the working tree's generators
+        # (counter-review record 15 F1: an uncommitted generator edit must not
+        # be invisible to this test).
+        for _profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
+            relative = Path("configs/campaigns") / pack_id / "generate_configs.py"
+            shutil.copy2(ROOT / relative, repository / relative)
+        return repository
+
     def test_routing_constants_are_the_only_producer_routing_sources(self) -> None:
         observed = {}
         for profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
@@ -562,10 +590,11 @@ class D117FloorQwen3V5PackTests(unittest.TestCase):
     def test_generators_are_deterministic_closed_and_checkable(self) -> None:
         with tempfile.TemporaryDirectory(prefix="d117-floor-v5-") as temporary:
             root = Path(temporary)
+            repository = self.generation_repository(root)
             pin = fixture_prefill_pin(root)
             for profile, pack_id, _model_id, model_name, plan_id in FLOORS:
                 with self.subTest(pack_id=pack_id):
-                    module = load_generator(pack_id)
+                    module = load_generator(pack_id, repository=repository)
                     module.configure_prefill_pin(pin)
                     first = root / f"{pack_id}-first"
                     second = root / f"{pack_id}-second"
@@ -592,12 +621,15 @@ class D117FloorQwen3V5PackTests(unittest.TestCase):
                     checked = subprocess.run(
                         [
                             sys.executable,
-                            str(ROOT / "configs/campaigns" / pack_id / "generate_configs.py"),
+                            str(
+                                repository / "configs/campaigns" / pack_id
+                                / "generate_configs.py"
+                            ),
                             "--check",
                             "--output-root",
                             str(first),
                         ],
-                        cwd=ROOT,
+                        cwd=repository,
                         env={"PYTHONDONTWRITEBYTECODE": "1"},
                         check=False,
                         capture_output=True,
@@ -767,9 +799,10 @@ class D117FloorQwen3V5PackTests(unittest.TestCase):
     def test_contrast_references_resolve_to_matching_floor_plan_digests(self) -> None:
         with tempfile.TemporaryDirectory(prefix="d117-floor-link-") as temporary:
             output = Path(temporary)
+            repository = self.generation_repository(output)
             pin = fixture_prefill_pin(output)
             for _profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
-                module = load_generator(pack_id)
+                module = load_generator(pack_id, repository=repository)
                 module.configure_prefill_pin(pin)
                 module.generate(output)
 
@@ -814,6 +847,7 @@ class D117FloorQwen3V5PackTests(unittest.TestCase):
     def test_arm_registry_and_pack_record_accept_the_v5_floor_roster(self) -> None:
         with tempfile.TemporaryDirectory(prefix="d117-floor-roster-") as temporary:
             output = Path(temporary)
+            repository = self.generation_repository(output)
             pin = fixture_prefill_pin(output)
             registry, _raw = arm_readiness.load_registry(ROOT)
             installed = registry["freeze_evidence_lifecycle"]["successor_policy"][
@@ -829,7 +863,7 @@ class D117FloorQwen3V5PackTests(unittest.TestCase):
             )
             pack_roots: list[tuple[str, Path]] = []
             for profile, pack_id, _model_id, _model_name, _plan_id in FLOORS:
-                module = load_generator(pack_id)
+                module = load_generator(pack_id, repository=repository)
                 module.configure_prefill_pin(pin)
                 module.generate(output)
                 pack = output / "configs/campaigns" / pack_id
```
