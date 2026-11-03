"""D-188 VDL-CORE: the key schema of every registered leaf.

For each LeafSpec: its parameters are exactly the parameters of every leaf
callable it names (so an added argument cannot silently leave the key), and
every key component - each scalar argument, each tree's bytes and identity,
the JOULEWISE_* environment, the commit and the code digest - changes the key
when mutated, while the physics view (admitted separately) does not.
Synthetic values only; no leaf is executed.
"""
from __future__ import annotations

import inspect
import math
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import authentication_io as aio


def _resolvable(reference: str):
    try:
        return vdl._resolve_reference(reference)
    except (ImportError, AttributeError):
        return None


class LeafSignatures(unittest.TestCase):
    def test_registry_is_closed_and_unique(self):
        self.assertIsInstance(vdl.LEAVES, tuple)
        ids = [spec.leaf_id for spec in vdl.LEAVES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sorted(ids), sorted([
            "L1_strict_validation", "L2_operative_summary", "L3_reduce_dict", "L4_calibration_bracket",
            "L5_environment_refusals", "L6_verify_instrument_calibration"]))

    def test_every_parameter_has_exactly_one_role(self):
        for spec in vdl.LEAVES:
            with self.subTest(leaf=spec.leaf_id):
                names = [name for name, _ in spec.params]
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue({role for _, role in spec.params} <= {vdl.TREE, vdl.TREES, vdl.SCALAR, vdl.PHYSICS})
                self.assertTrue(any(role in (vdl.TREE, vdl.TREES) for _, role in spec.params))
                resolved = [_resolvable(reference) for reference in spec.qualnames]
                self.assertTrue(any(resolved), "no registered callable exists")
                for reference, fn in zip(spec.qualnames, resolved):
                    if fn is None:
                        continue
                    self.assertEqual(set(inspect.signature(fn).parameters), set(names), reference)
                if spec.physics_probe is None:
                    self.assertNotIn(vdl.PHYSICS, {role for _, role in spec.params})


def _value(index: int):
    return {"scalar": index, "nested": [1.0, {"k": "v"}]}


class KeyMutations(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-key-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        caches = arc.analysis_run_caches({}, vdl_mode=vdl.ON)
        self.caches = caches.__enter__()
        self.addCleanup(caches.__exit__, None, None, None)
        self.store = self.caches.vdl

    def tree(self, parent: str, name: str = "bundle", payload: bytes = b"payload") -> Path:
        root = self.tmp / parent / name
        root.mkdir(parents=True, exist_ok=True)
        (root / "data.txt").write_bytes(payload)
        (root / "metadata.json").write_bytes(b'{"instrument_calibration": {"artifact_sha256": "cal"}}')
        return root

    def arguments(self, spec: vdl.LeafSpec, parent: str = "a") -> dict:
        arguments = {}
        for name, role in spec.params:
            if role == vdl.TREE:
                arguments[name] = self.tree(parent)
            elif role == vdl.TREES:
                arguments[name] = [self.tree(parent, "one"), self.tree(parent, "two")]
            elif role == vdl.PHYSICS:
                arguments[name] = None
            else:
                arguments[name] = _value(0)
        return arguments

    def key(self, spec: vdl.LeafSpec, arguments: dict) -> str:
        fn = next(fn for fn in map(_resolvable, spec.qualnames) if fn is not None)
        return self.store._prepare(spec, fn, (), dict(arguments)).key

    def test_each_scalar_mutation_is_a_different_key(self):
        for spec in vdl.LEAVES:
            base_arguments = self.arguments(spec)
            base = self.key(spec, base_arguments)
            self.assertEqual(base, self.key(spec, dict(base_arguments)))
            for name, role in spec.params:
                if role != vdl.SCALAR:
                    continue
                with self.subTest(leaf=spec.leaf_id, parameter=name):
                    for mutated in (_value(1), {"scalar": 0, "nested": [math.nextafter(1.0, 2.0), {"k": "v"}]},
                                    {"scalar": 0, "nested": [1, {"k": "v"}]},
                                    {"scalar": 0, "nested": ({"float": (1.0).hex()}, {"k": "v"})}, None):
                        changed = dict(base_arguments, **{name: mutated})
                        self.assertNotEqual(self.key(spec, changed), base)

    def test_tree_bytes_identity_and_name(self):
        for spec in vdl.LEAVES:
            with self.subTest(leaf=spec.leaf_id):
                arguments = self.arguments(spec)
                base = self.key(spec, arguments)
                tree_name = next(name for name, role in spec.params if role in (vdl.TREE, vdl.TREES))
                role = spec.roles()[tree_name]
                first = arguments[tree_name] if role == vdl.TREE else arguments[tree_name][0]
                (first / "data.txt").write_bytes(b"paYload")
                self.assertNotEqual(self.key(spec, arguments), base)
                (first / "data.txt").write_bytes(b"payload")
                self.assertEqual(self.key(spec, arguments), base)
                elsewhere = self.arguments(spec, parent="b")  # same names, same bytes, another parent
                self.assertEqual(self.key(spec, elsewhere) == base, spec.path_free)
                renamed = dict(arguments)
                other = self.tree("c", "renamed")
                renamed[tree_name] = other if role == vdl.TREE else [other, arguments[tree_name][1]]
                self.assertNotEqual(self.key(spec, renamed), base)
                if role == vdl.TREES:
                    swapped = dict(arguments, **{tree_name: list(reversed(arguments[tree_name]))})
                    self.assertNotEqual(self.key(spec, swapped), base)
                (first / "extra.txt").write_bytes(b"")
                self.assertNotEqual(self.key(spec, arguments), base)  # listings are in the digest
                (first / "extra.txt").unlink()

    def test_tree_argument_kind(self):
        spec = vdl._LEAVES_BY_ID["L5_environment_refusals"]
        arguments = self.arguments(spec)
        base = self.key(spec, arguments)
        self.assertEqual(self.key(spec, dict(arguments, bundle_path=str(arguments["bundle_path"]))), base)
        capability = aio.V2AuthenticationPath(arguments["bundle_path"])
        self.assertNotEqual(self.key(spec, dict(arguments, bundle_path=capability)), base)

    def test_physics_view_is_not_in_the_key(self):
        for spec in vdl.LEAVES:
            for name, role in spec.params:
                if role != vdl.PHYSICS:
                    continue
                with self.subTest(leaf=spec.leaf_id):
                    arguments = self.arguments(spec)
                    if spec.leaf_id == "L6_verify_instrument_calibration":
                        arguments["calibration"] = {"artifact_sha256": "cal"}
                    with_value = self.key(spec, dict(arguments, **{name: {"cal": 1.5}}))
                    self.assertEqual(self.key(spec, dict(arguments, **{name: {"cal": 2.5, "x": 1.0}})),
                                     with_value)
                    self.assertEqual(self.key(spec, dict(arguments, **{name: {}})), with_value)
                    # Whether a view is consulted at all is call context, and is keyed.
                    self.assertNotEqual(self.key(spec, arguments), with_value)

    def test_environment_commit_code_and_schema_components(self):
        spec = vdl._LEAVES_BY_ID["L1_strict_validation"]
        arguments = self.arguments(spec)
        base = self.key(spec, arguments)
        with mock.patch.dict(os.environ, {"JOULEWISE_VDL_KEY_TEST": "1"}):
            self.assertNotEqual(self.key(spec, arguments), base)
        with mock.patch.dict(os.environ, {"VDL_KEY_TEST_UNRELATED": "1"}):
            self.assertEqual(self.key(spec, arguments), base)
        self.store.commit = "0" * 40
        self.assertNotEqual(self.key(spec, arguments), base)
        self.store.commit = None
        with mock.patch.object(vdl, "code_digest", lambda: "f" * 64):
            self.assertNotEqual(self.key(spec, arguments), base)
        with mock.patch.object(vdl, "SCHEMA", "joulewise-vdl/other"):
            self.assertNotEqual(self.key(spec, arguments), base)
        other = vdl.LeafSpec("L1_other", spec.qualnames, spec.params, path_free=spec.path_free)
        self.assertNotEqual(self.key(other, arguments), base)

    def test_signature_drift_bypasses(self):
        spec = vdl._LEAVES_BY_ID["L5_environment_refusals"]
        drifted = vdl.LeafSpec(spec.leaf_id, spec.qualnames, spec.params[:-1])
        with self.assertRaises(vdl._Bypass):
            self.key(drifted, {name: value for name, value in self.arguments(spec).items()
                               if name != spec.params[-1][0]})


if __name__ == "__main__":
    unittest.main()
