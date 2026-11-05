"""Byte contracts checked against every original helper before extraction.

Load only the named function AST, never a script's top-level code or data.
The same census exercises the replacement bindings after extraction.
"""
from __future__ import annotations

import ast
from collections.abc import Mapping
import copy
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import random
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = json.loads((ROOT / "tests/prune_s5_contracts.json").read_text())


def reject(value):
    raise ValueError(f"rejected {value!r}")


@lru_cache(maxsize=None)
def binding(location):
    path, name = location.split(":")
    tree = ast.parse((ROOT / path).read_text())
    namespace = dict(json=json, math=math, hashlib=hashlib, os=os,
                     tempfile=tempfile, Path=Path, PurePosixPath=PurePosixPath,
                     Mapping=Mapping, _reject_nonfinite_admission_number=reject,
                     _reject_nonfinite_json=reject, _nonfinite_number=reject,
                     _require=lambda ok, detail: None if ok else reject(detail))
    # Replacement imports plus the original function's signature/body. Strip
    # annotations so no unrelated application imports are needed for this check.
    nodes = [n for n in tree.body if isinstance(n, ast.ImportFrom)
             and n.module == "joulewise.strict_io"]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            node = copy.deepcopy(node)
            node.returns = None
            for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                arg.annotation = None
            nodes.append(node)
    exec(compile(ast.Module(nodes, type_ignores=[]), path, "exec"), namespace)
    return namespace[name]


def outcome(fn, *args, **kwargs):
    try:
        value = fn(*args, **kwargs)
        # repr preserves negative zero, NaN, numeric types and exact bytes.
        return type(value).__name__, repr(value)
    except (ValueError, TypeError, OverflowError, UnicodeError) as exc:
        return type(exc).__name__, str(exc)


def json_value(rng, depth=0):
    scalars = [None, True, False, 0, -0.0, 1e300, "é漢😀\n\x00", "\ud800"]
    if depth > 2 or rng.randrange(3) == 0:
        return rng.choice(scalars + [rng.randrange(-10**30, 10**30), rng.random()])
    if rng.randrange(2):
        return [json_value(rng, depth + 1) for _ in range(rng.randrange(5))]
    return {rng.choice(["z", "é", "a", "😀"]): json_value(rng, depth + 1)
            for _ in range(rng.randrange(5))}


class StrictIOContracts(unittest.TestCase):
    def test_serialization(self):
        rng = random.Random(505)
        values = [{"é": "漢😀", "a": -0.0}, float("nan"), float("inf"),
                  -float("inf"), {1: "a", "b": 2}, b"bad", {"a": object()}]
        values += [json_value(rng) for _ in range(200)]
        for location, kind in CONTRACTS.items():
            if not kind.startswith("json_"):
                continue
            fn = binding(location)
            options = dict(sort_keys=True, ensure_ascii="ascii" in kind,
                           allow_nan=not kind.endswith("strict"))
            if "pretty" in kind:
                options["indent"] = 2
                if "insertion" in kind:
                    options.pop("sort_keys")
            else:
                options["separators"] = (",", ":")
            def expected(value):
                text = json.dumps(value, **options)
                if "pretty" in kind:
                    text += "\n"
                return text if kind.endswith("text") else text.encode("utf-8")
            for value in values:
                with self.subTest(location=location, kind=kind):
                    self.assertEqual(outcome(fn, value=value), outcome(expected, value))

    def test_digests(self):
        rng = random.Random(506)
        raw = [b"", bytes(range(256)), b"\x00\xff\n"]
        raw += [rng.randbytes(rng.randrange(4096)) for _ in range(100)]
        for location, kind in CONTRACTS.items():
            if kind not in ("sha256_raw", "sha256_data", "sha256_value", "sha256_text"):
                continue
            fn = binding(location)
            key = kind.removeprefix("sha256_")
            values = ["", "é漢😀", "\ud800", "\x00\n"] if key == "text" else raw
            for value in values:
                expected = lambda v: hashlib.sha256(v.encode("utf-8") if key == "text" else v).hexdigest()
                self.assertEqual(outcome(fn, **{key: value}), outcome(expected, value), location)

    def test_file_digests(self):
        rng = random.Random(507)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "é.bin"
            for size in (0, 1, 255, 2**20 - 1, 2**20, 2**20 + 1, 2**21 + 3):
                raw = rng.randbytes(size)
                path.write_bytes(raw)
                for location, kind in CONTRACTS.items():
                    if kind in ("sha256_file", "sha256_path_bytes"):
                        self.assertEqual(binding(location)(path=path), hashlib.sha256(raw).hexdigest(), location)
            path.unlink()
            for location, kind in CONTRACTS.items():
                if kind in ("sha256_file", "sha256_path_bytes"):
                    with self.assertRaises(FileNotFoundError, msg=location):
                        binding(location)(path)

    def test_guards(self):
        rng = random.Random(508)
        values = [None, True, False, "", [], {}, 0, -0.0, 1.5,
                  float("nan"), float("inf"), 10**400, "0" * 64, "A" * 64,
                  "0x" + "a" * 62, "a" * 63 + "\n", " " + "a" * 63]
        values += [rng.randrange(-10**40, 10**40) for _ in range(100)]
        values += ["".join(rng.choices("0123456789abcdefABCDEF_x \n", k=rng.randrange(63, 66))) for _ in range(100)]
        for location, kind in CONTRACTS.items():
            if kind not in ("is_lower_sha256", "is_sha256", "finite_or_none", "is_finite_float_projection", "require_finite"):
                continue
            fn = binding(location)
            def expected(value):
                if kind in ("is_lower_sha256", "is_sha256"):
                    chars = "0123456789abcdef" + ("ABCDEF" if kind == "is_sha256" else "")
                    return isinstance(value, str) and len(value) == 64 and all(c in chars for c in value)
                numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
                if kind == "require_finite":
                    if not numeric or not math.isfinite(float(value)):
                        raise ValueError("field must be a finite number")
                    return float(value)
                if kind == "finite_or_none":
                    return float(value) if numeric and math.isfinite(float(value)) else None
                return numeric and math.isfinite(float(value))
            for value in values:
                kw = {"name": "field"} if kind == "require_finite" else {}
                self.assertEqual(outcome(fn, value=value, **kw), outcome(expected, value), location)

    def test_strict_json_hooks(self):
        rng = random.Random(509)
        numbers = ["0", "-0", "-0.0", "1e309", "NaN", "Infinity", "bad", "9" * 400]
        numbers += [str(rng.randrange(-10**100, 10**100)) for _ in range(100)]
        for location, kind in CONTRACTS.items():
            fn = binding(location)
            if kind in ("parse_finite_float", "parse_finite_int"):
                def expected(value):
                    parsed = (float if kind.endswith("float") else int)(value)
                    try:
                        finite = math.isfinite(float(parsed))
                    except OverflowError:
                        finite = False
                    if not finite:
                        reject(value)
                    return parsed
                for value in numbers:
                    self.assertEqual(outcome(fn, value=value), outcome(expected, value), location)
            elif kind == "unique_json_pairs":
                cases = [[], [("é", 1)], [("a", 1), ("a", 2)], [("x", 1), ("y", 2), ("x", 3)]]
                cases += [[(rng.choice(["a", "é", "😀"]), rng.randrange(100))
                           for _ in range(rng.randrange(8))] for _ in range(100)]
                for pairs in cases:
                    if len(dict(pairs)) != len(pairs):
                        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                            fn(pairs=pairs)
                    else:
                        self.assertEqual(fn(pairs=pairs), dict(pairs))
                for raw in ('{"a":1,"a":2}', '{"o":{"é":1,"é":2}}'):
                    with self.assertRaises(ValueError):
                        json.loads(raw, object_pairs_hook=fn)

    def test_exact_keys_and_paths(self):
        rng = random.Random(510)
        for location, kind in CONTRACTS.items():
            fn = binding(location)
            if kind == "collect_exact_keys":
                for _ in range(100):
                    expected = set(rng.sample(["a", "b", "é"], rng.randrange(4)))
                    value = {k: 1 for k in rng.sample(["a", "b", "é"], rng.randrange(4))}
                    errors = ["prior"]
                    result = fn(value=value, expected=expected, where="field", errors=errors)
                    missing, extra = sorted(expected - set(value)), sorted(set(value) - expected)
                    wanted = ["prior"]
                    if missing:
                        wanted.append(f"field: missing key(s): {', '.join(missing)}")
                    if extra:
                        wanted.append(f"field: unrecognized key(s): {', '.join(extra)}")
                    self.assertEqual((result, errors), (not missing and not extra, wanted), location)
            elif kind == "relative_inside":
                # These legacy predicates deliberately allow normalization,
                # backslashes, drive-like names and NUL; do not tighten them.
                values = [None, "", "/a", "../a", "a/../b", ".", "a//b", "a/./b", "a\\b", "C:/a", "é/😀", "a\x00b"]
                values += ["/".join(rng.choices(["", ".", "..", "é", "a", "b\\c"], k=rng.randrange(5))) for _ in range(100)]
                for value in values:
                    valid = isinstance(value, str) and bool(value) and not PurePosixPath(value).is_absolute() and ".." not in PurePosixPath(value).parts
                    if valid:
                        self.assertEqual(fn(root=Path("root"), value=value, label="field"), Path("root") / value)
                    else:
                        with self.assertRaises(ValueError):
                            fn(Path("root"), value, "field")

    def test_fsync_and_atomic_write(self):
        for location, kind in CONTRACTS.items():
            if not (kind.startswith("fsync_") or kind == "atomic_write_bytes"):
                continue
            fn = binding(location)
            if kind.startswith("fsync_"):
                calls = []
                def effect(name, result=None):
                    return lambda *args: (calls.append((name, args)), result)[1]
                with patch.object(os, "open", side_effect=effect("open", 123)), patch.object(os, "fsync", side_effect=effect("fsync")), patch.object(os, "close", side_effect=effect("close")):
                    fn(Path("directory"))
                self.assertEqual([name for name, _ in calls], ["open", "fsync", "close"], location)
                for failed in ("open", "fsync", "close"):
                    with patch.object(os, "open", return_value=123), patch.object(os, "fsync"), patch.object(os, "close"):
                        with patch.object(os, failed, side_effect=OSError("injected")):
                            if "best_effort" in kind and failed != "close":
                                fn(Path("directory"))
                            else:
                                with self.assertRaises(OSError):
                                    fn(Path("directory"))
            else:
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "new" / "é.bin"
                    for raw in (b"", b"\x00\xff\n", random.Random(511).randbytes(65537)):
                        fn(path=path, raw=raw)
                        self.assertEqual(path.read_bytes(), raw)
                        self.assertEqual(list(path.parent.iterdir()), [path])
                    before = path.read_bytes()
                    for failed in ("fsync", "replace"):
                        with patch.object(os, failed, side_effect=OSError("injected")):
                            with self.assertRaises(OSError):
                                fn(path, b"replacement")
                        self.assertEqual(path.read_bytes(), before)
                        self.assertEqual(list(path.parent.iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
