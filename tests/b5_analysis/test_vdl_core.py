"""D-188 VDL-CORE: the verified derivation store primitive (synthetic leaves only).

Every leaf here is a module-level function of this test module registered as a
synthetic LeafSpec for the duration of a test; the bytes are temporary trees.
"""
from __future__ import annotations

import ast
import contextlib
import contextvars
import hashlib
import io
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import analysis_verified_store as vdl
from joulewise import authentication_io as aio

ROOT = Path(__file__).resolve().parents[2]
MODULE = __name__
CALLS: dict[str, int] = {}
NONDETERMINISTIC = [0]
SIDE_FILE: list[Path] = []
_TEST_ROWS: contextvars.ContextVar[list | None] = contextvars.ContextVar("vdl_test_rows", default=None)


def _called(name: str) -> None:
    CALLS[name] = CALLS.get(name, 0) + 1


def _read(path: Path, grammar: str = "raw") -> bytes:
    """An authentication_io read that also feeds a test recorder (AUTH-IO's row shape)."""

    raw = aio.read_authentication_input(path, grammar=grammar, label=f"test input {path}")
    rows = _TEST_ROWS.get()
    if rows is not None:
        identity = str(Path(path).resolve(strict=False))
        rows.append(SimpleRow(api="read_authentication_input", identity=identity,
                              sha256=hashlib.sha256(raw).hexdigest(),
                              grammar=aio._forced_grammar(identity, grammar), caller_grammar=grammar,
                              label=f"test input {path}",
                              in_session=aio.active_v2_authentication_session() is not None,
                              relative=None))
    return raw


class SimpleRow:
    def __init__(self, **values):
        self.__dict__.update(values)


def digest_tree(path, factor):
    """Reads every file of the tree; returns a JSON-shaped value."""

    _called("digest_tree")
    total = hashlib.sha256()
    for item in sorted(Path(path).rglob("*")):
        if item.is_file():
            grammar = "json" if item.suffix == ".json" else "raw"
            total.update(_read(item, grammar))
    return {"digest": total.hexdigest(), "factor": factor, "nested": [1.5, (2, 3)]}


def firing_leaf(path, factor):
    _called("firing_leaf")
    arc.current().deadline.firings += 1
    return factor


def raising_leaf(path, factor):
    _called("raising_leaf")
    raise ValueError("leaf failure")


def clock_leaf(path, factor):
    _called("clock_leaf")
    vdl.note_clock()
    return factor


def writing_leaf(path, factor):
    _called("writing_leaf")
    with open(SIDE_FILE[0], "w") as handle:
        handle.write("x")
    return factor


def subprocess_leaf(path, factor):
    _called("subprocess_leaf")
    subprocess.run([sys.executable, "-c", "pass"], check=True)
    return factor


def thread_leaf(path, factor):
    _called("thread_leaf")
    worker = threading.Thread(target=lambda: None)
    worker.start()
    worker.join()
    return factor


def mutating_leaf(path, factor):
    _called("mutating_leaf")
    factor.append("mutated")
    return len(factor)


def toctou_leaf(path, factor):
    _called("toctou_leaf")
    (Path(path) / "late.txt").write_bytes(b"late")  # a write: also unstorable by the recorder
    return factor


def path_leaf(path, factor):
    _called("path_leaf")
    return f"problem in {Path(path).resolve()}"


def extra_leaf(path, factor):
    _called("extra_leaf")
    return hashlib.sha256(Path(factor).read_bytes()).hexdigest()


def listing_leaf(path, factor):
    _called("listing_leaf")
    return sorted(os.listdir(factor))


def nondeterministic_leaf(path, factor):
    _called("nondeterministic_leaf")
    NONDETERMINISTIC[0] += 1
    return NONDETERMINISTIC[0]


def physics_leaf(path, cache):
    """Uses the cached bound under 'cal', or 'refits' to 2.5 and inserts it."""

    _called("physics_leaf")
    bound = cache.get("cal")
    if bound is None:
        _called("refit")
        bound = 2.5
        cache["cal"] = bound
    return {"bound": bound}


def stray_physics_leaf(path, cache):
    _called("stray_physics_leaf")
    cache["other"] = 1.0
    return 0


def nested_outer(path, factor):
    _called("nested_outer")
    inner = vdl.call("T_digest", digest_tree, path, factor)
    return {"inner": inner["digest"], "outer": factor}


def nested_clock_outer(path, factor):
    _called("nested_clock_outer")
    return [vdl.call("T_digest", digest_tree, path, factor), clock_leaf(path, factor)]


def shadow_target(path, factor):
    _called("shadow_target")
    return NONDETERMINISTIC[0]


def _spec(leaf_id, fn, *, physics=False, path_free=False):
    if physics:
        params = (("path", vdl.TREE), ("cache", vdl.PHYSICS))
        probe = lambda arguments: [(arguments["cache"], "cal")]  # noqa: E731
    else:
        params = (("path", vdl.TREE), ("factor", vdl.SCALAR))
        probe = None
    return vdl.LeafSpec(leaf_id, (f"{MODULE}:{fn.__qualname__}",), params, path_free=path_free,
                        physics_probe=probe)


SPECS = (
    _spec("T_digest", digest_tree),
    _spec("T_digest_free", digest_tree, path_free=True),
    _spec("T_raise", raising_leaf),
    _spec("T_firing", firing_leaf),
    _spec("T_clock", clock_leaf),
    _spec("T_write", writing_leaf),
    _spec("T_subprocess", subprocess_leaf),
    _spec("T_thread", thread_leaf),
    _spec("T_mutate", mutating_leaf),
    _spec("T_toctou", toctou_leaf),
    _spec("T_path", path_leaf, path_free=True),
    _spec("T_extra", extra_leaf),
    _spec("T_listing", listing_leaf),
    _spec("T_nondet", nondeterministic_leaf),
    _spec("T_physics", physics_leaf, physics=True),
    _spec("T_stray", stray_physics_leaf, physics=True),
    _spec("T_outer", nested_outer),
    _spec("T_clock_outer", nested_clock_outer),
    _spec("T_shadow", shadow_target),
)


class FakeDeadline:
    def __init__(self):
        self.firings = 0


@contextlib.contextmanager
def run(mode=vdl.ON, *, deadline=True, physics=None):
    with arc.analysis_run_caches({} if physics is None else physics, vdl_mode=mode) as caches:
        caches.deadline = FakeDeadline() if deadline else None
        yield caches


def make_tree(parent: Path, name: str = "bundle", **files: bytes) -> Path:
    root = parent / name
    root.mkdir(parents=True)
    contents = files or {"metadata.json": b'{"a": 1}', "data.txt": b"payload", "sub/inner.json": b'{"b": 2}'}
    for relative, raw in contents.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return root


class _Base(unittest.TestCase):
    def setUp(self):
        CALLS.clear()
        NONDETERMINISTIC[0] = 0
        self.tmp = Path(tempfile.mkdtemp(prefix="vdl-core-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        registration = vdl._registered(*SPECS)
        registration.__enter__()
        self.addCleanup(registration.__exit__, None, None, None)
        self.tree = make_tree(self.tmp)

    def counters(self, caches):
        return caches.vdl.restricted_counters()


class ModesAndCanonicalForm(unittest.TestCase):
    def test_modes(self):
        self.assertEqual(vdl.parse_mode("off"), vdl.OFF)
        self.assertEqual(vdl.parse_mode("on"), vdl.ON)
        self.assertEqual(vdl.parse_mode("shadow:1000"), vdl.Mode("shadow", 1000))
        for bad in ("shadow:1001", "shadow:-1", "shadow:x", "shadow:", "ON", "", "shadow:1e3"):
            with self.assertRaises(ValueError):
                vdl.parse_mode(bad)
        # Lead ruling: shadow on by default for synthetic runs, never on a real blind run.
        self.assertEqual(vdl.resolve_mode(None, synthetic=True), vdl.Mode("shadow", 1000))
        self.assertEqual(vdl.resolve_mode(None, synthetic=False), vdl.ON)
        self.assertEqual(vdl.resolve_mode("shadow:20", synthetic=False), vdl.ON)
        self.assertEqual(vdl.resolve_mode("garbage", synthetic=False), vdl.OFF)
        with self.assertRaises(ValueError):
            vdl.resolve_mode("garbage", synthetic=True)

    def test_canonical_form_is_injective_and_exact(self):
        cb = vdl.canonical_bytes
        self.assertNotEqual(cb(1.0), cb({"float": (1.0).hex()}))
        self.assertNotEqual(cb({"x": 1.0}), cb({"x": {"float": (1.0).hex()}}))
        self.assertNotEqual(cb(0.1 + 0.2), cb(0.3))
        self.assertEqual(cb(0.1 + 0.2), cb(0.30000000000000004))
        self.assertNotEqual(cb(1), cb(1.0))
        self.assertNotEqual(cb(True), cb(1))
        self.assertNotEqual(cb((1, 2)), cb([1, 2]))
        self.assertNotEqual(cb("1"), cb(1))
        self.assertNotEqual(cb(b"a"), cb("a"))
        self.assertNotEqual(cb(["ab", "c"]), cb(["a", "bc"]))
        self.assertEqual(cb({"a": 1, "b": 2}), cb({"b": 2, "a": 1}))
        self.assertEqual(cb(frozenset({3, 1})), cb(frozenset({1, 3})))
        self.assertNotEqual(cb(Path("/x")), cb("/x"))
        self.assertEqual(cb(vdl.reduce_bundle_dict), cb(vdl.reduce_bundle_dict))
        with self.assertRaises(TypeError):
            cb(object())
        with self.assertRaises(TypeError):
            cb(lambda: None)


class StoreRules(_Base):
    def test_inert_outside_a_run_and_when_off(self):
        self.assertEqual(vdl.call("T_digest", digest_tree, self.tree, 1)["factor"], 1)
        with run(vdl.OFF) as caches:
            self.assertIsNone(caches.vdl)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
        with arc.analysis_run_caches({}) as caches:
            self.assertIsNone(caches.vdl)
        self.assertEqual(CALLS["digest_tree"], 3)

    def test_fill_then_hit_returns_equal_fresh_copies(self):
        with run() as caches:
            first = vdl.call("T_digest", digest_tree, self.tree, 7)
            first["nested"].append("caller mutation after the fill")
            second = vdl.call("T_digest", digest_tree, self.tree, 7)
            second["nested"].append("caller mutation after a hit")
            third = vdl.call("T_digest", digest_tree, self.tree, 7)
            self.assertEqual(CALLS["digest_tree"], 1)
            self.assertEqual(third, {"digest": first["digest"], "factor": 7, "nested": [1.5, (2, 3)]})
            self.assertIsNot(second, third)
            self.assertEqual(self.counters(caches)["T_digest:hit"], 2)
            vdl.call("T_digest", digest_tree, self.tree, 8)  # another scalar: another key
            self.assertEqual(CALLS["digest_tree"], 2)

    def test_unregistered_or_wrapped_callables_bypass(self):
        with run() as caches:
            vdl.call("T_digest", lambda path, factor: digest_tree(path, factor), self.tree, 1)
            vdl.call("T_digest", lambda path, factor: digest_tree(path, factor), self.tree, 1)
            vdl.call("T_unknown", digest_tree, self.tree, 1)
            vdl.call("T_unknown", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 4)
            self.assertNotIn("T_digest:fill", self.counters(caches))

    def test_symlink_and_special_file_bypass(self):
        linked = make_tree(self.tmp, "linked")
        os.symlink(linked / "data.txt", linked / "alias.txt")
        special = make_tree(self.tmp, "special")
        os.mkfifo(special / "pipe")
        for tree in (linked, special):
            with self.subTest(tree=tree.name), run() as caches:
                CALLS.clear()
                if tree is special:
                    vdl.call("T_listing", listing_leaf, tree, str(self.tmp))
                    vdl.call("T_listing", listing_leaf, tree, str(self.tmp))
                    self.assertEqual(CALLS["listing_leaf"], 2)
                else:
                    vdl.call("T_digest", digest_tree, tree, 1)
                    vdl.call("T_digest", digest_tree, tree, 1)
                    self.assertEqual(CALLS["digest_tree"], 2)
                self.assertFalse(any(key.endswith(":fill") for key in self.counters(caches)))

    def test_tampered_byte_is_a_miss_and_the_leaf_decides(self):
        with run():
            before = vdl.call("T_digest", digest_tree, self.tree, 1)
            (self.tree / "data.txt").write_bytes(b"paYload")
            after = vdl.call("T_digest", digest_tree, self.tree, 1)
        self.assertEqual(CALLS["digest_tree"], 2)
        self.assertNotEqual(before["digest"], after["digest"])

    def test_same_size_rewrite_with_restored_mtime_is_caught_by_ctime(self):
        target = self.tree / "data.txt"
        with run(), vdl.enter_program_scope():
            before = vdl.call("T_digest", digest_tree, self.tree, 1)
            st = os.lstat(target)
            with open(target, "r+b") as handle:  # in place: same inode, same size
                handle.write(b"PAYLOAD")
            os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns))
            self.assertEqual(os.lstat(target).st_mtime_ns, st.st_mtime_ns)
            self.assertEqual(os.lstat(target).st_ino, st.st_ino)
            after = vdl.call("T_digest", digest_tree, self.tree, 1)
        self.assertEqual(CALLS["digest_tree"], 2)
        self.assertNotEqual(before["digest"], after["digest"])

    def test_scope_rehashes_after_an_inode_change(self):
        target = self.tree / "data.txt"
        hashed = []
        real = vdl.tree_digest

        def counting(root, *, content_only=False):
            hashed.append(root)
            return real(root, content_only=content_only)

        with mock.patch.object(vdl, "tree_digest", counting), run(), vdl.enter_program_scope():
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(len(hashed), 1)  # verified once in this program
            replacement = self.tree / "data.tmp"
            replacement.write_bytes(target.read_bytes())
            os.replace(replacement, target)  # same bytes, new inode
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(len(hashed), 2)
            self.assertEqual(CALLS["digest_tree"], 1)  # same content: still a hit

    def test_fresh_context_and_new_program_reverify(self):
        hashed = []
        real = vdl.tree_digest

        def counting(root, *, content_only=False):
            hashed.append(root)
            return real(root, content_only=content_only)

        with mock.patch.object(vdl, "tree_digest", counting), run():
            with vdl.enter_program_scope():
                vdl.call("T_digest", digest_tree, self.tree, 1)
                vdl.call("T_digest", digest_tree, self.tree, 1)
                self.assertEqual(len(hashed), 1)
                contextvars.Context().run(vdl.call, "T_digest", digest_tree, self.tree, 1)
                self.assertEqual(len(hashed), 2)
            with vdl.enter_program_scope():
                vdl.call("T_digest", digest_tree, self.tree, 1)
                self.assertEqual(len(hashed), 3)
            # Outside any program: a context-local scope, dropped when a program starts.
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(len(hashed), 4)
            with vdl.enter_program_scope():
                pass
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(len(hashed), 5)
        self.assertEqual(CALLS["digest_tree"], 1)

    def test_exceptions_are_never_stored(self):
        with run():
            for _ in range(2):
                with self.assertRaises(ValueError):
                    vdl.call("T_raise", raising_leaf, self.tree, 1)
        self.assertEqual(CALLS["raising_leaf"], 2)

    def test_deadline_firing_and_unavailable_observer_prevent_storing(self):
        with run() as caches:
            vdl.call("T_firing", firing_leaf, self.tree, 1)
            vdl.call("T_firing", firing_leaf, self.tree, 1)
            self.assertEqual(CALLS["firing_leaf"], 2)
            self.assertEqual(caches.deadline.firings, 2)
            self.assertNotIn("T_firing:fill", self.counters(caches))
        with run(deadline=False):
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 2)
        CALLS.clear()
        with run() as caches:
            caches.worker_observer_unavailable = True
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 2)

    def test_clock_write_subprocess_thread_mutation_toctou_prevent_storing(self):
        SIDE_FILE[:] = [self.tmp / "side.txt"]
        cases = [
            ("T_clock", clock_leaf, lambda: 1),
            ("T_write", writing_leaf, lambda: 1),
            ("T_subprocess", subprocess_leaf, lambda: 1),
            ("T_thread", thread_leaf, lambda: 1),
            ("T_mutate", mutating_leaf, lambda: ["a"]),
            ("T_toctou", toctou_leaf, lambda: 1),
        ]
        for leaf_id, fn, factor in cases:
            with self.subTest(leaf=leaf_id), run() as caches:
                CALLS.clear()
                tree = make_tree(self.tmp, f"t-{leaf_id}")
                vdl.call(leaf_id, fn, tree, factor())
                (tree / "late.txt").unlink(missing_ok=True)
                vdl.call(leaf_id, fn, tree, factor())
                self.assertEqual(CALLS[fn.__name__], 2)
                self.assertEqual(self.counters(caches).get(f"{leaf_id}:unstorable"), 2)

    def test_clock_inside_a_nested_leaf_makes_the_outer_fill_unstorable(self):
        with run() as caches:
            vdl.call("T_clock_outer", nested_clock_outer, self.tree, 1)
            vdl.call("T_clock_outer", nested_clock_outer, self.tree, 1)
            self.assertEqual(CALLS["nested_clock_outer"], 2)
            self.assertEqual(CALLS["digest_tree"], 1)  # the clock-free inner leaf is stored

    def test_nested_hit_forwards_its_manifest_to_the_outer_fill(self):
        with run():
            vdl.call("T_digest", digest_tree, self.tree, 1)  # inner entry
            vdl.call("T_outer", nested_outer, self.tree, 1)  # outer fill sees an inner hit
            vdl.call("T_outer", nested_outer, self.tree, 1)
            self.assertEqual(CALLS["nested_outer"], 1)
        other = make_tree(self.tmp, "other")
        with run():
            CALLS.clear()
            vdl.call("T_digest", digest_tree, other, 1)
            vdl.call("T_outer", nested_outer, other, 1)
            (other / "data.txt").write_bytes(b"changed")
            vdl.call("T_outer", nested_outer, other, 1)
            self.assertEqual(CALLS["nested_outer"], 2)

    def test_extra_reads_and_listings_are_verified_on_every_hit(self):
        extra = self.tmp / "policy.json"
        extra.write_bytes(b'{"p": 1}')
        listed = self.tmp / "listed"
        listed.mkdir()
        (listed / "one").write_bytes(b"")
        with run(), vdl.enter_program_scope():
            vdl.call("T_extra", extra_leaf, self.tree, str(extra))
            vdl.call("T_extra", extra_leaf, self.tree, str(extra))
            self.assertEqual(CALLS["extra_leaf"], 1)
            extra.write_bytes(b'{"p": 2}')
            vdl.call("T_extra", extra_leaf, self.tree, str(extra))
            self.assertEqual(CALLS["extra_leaf"], 2)
            vdl.call("T_listing", listing_leaf, self.tree, str(listed))
            vdl.call("T_listing", listing_leaf, self.tree, str(listed))
            self.assertEqual(CALLS["listing_leaf"], 1)
            (listed / "two").write_bytes(b"")
            self.assertEqual(vdl.call("T_listing", listing_leaf, self.tree, str(listed)), ["one", "two"])
            self.assertEqual(CALLS["listing_leaf"], 2)

    def test_extra_read_hashes_are_cached_per_scope(self):
        extra = self.tmp / "policy.json"
        extra.write_bytes(b'{"p": 1}')
        hashed = []
        real = vdl._hash_file_nofollow

        def counting(path):
            hashed.append(path)
            return real(path)

        with run(), vdl.enter_program_scope():
            vdl.call("T_extra", extra_leaf, self.tree, str(extra))
            with mock.patch.object(vdl, "_hash_file_nofollow", counting):
                for _ in range(5):
                    vdl.call("T_extra", extra_leaf, self.tree, str(extra))
        self.assertEqual([path for path in hashed if path.endswith("policy.json")], [])
        self.assertEqual(CALLS["extra_leaf"], 1)

    def test_poisoning_on_disagreement(self):
        with run() as driver:
            vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)  # value 1
            with run() as child:
                vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)  # value 2
                payload = child.vdl.export_entries(new_only=True)
            driver.vdl.merge_entries(payload)
            self.assertEqual(driver.vdl.restricted_counters().get("poison"), 1)
            self.assertFalse(driver.vdl.defect_pending())  # never served before the poison
            vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)
            vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)
            self.assertEqual(CALLS["nondeterministic_leaf"], 4)  # poisoned: always the leaf

    def test_poisoning_after_serving_is_a_defect(self):
        with run() as driver:
            vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)
            vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)  # served from the store
            with run() as child:
                vdl.call("T_nondet", nondeterministic_leaf, self.tree, 1)
                payload = child.vdl.export_entries()
            driver.vdl.merge_entries(payload)
            self.assertTrue(driver.vdl.defect_pending())
            with self.assertRaises(vdl.VerifiedStoreDefect):
                driver.vdl.check_defects()

    def test_merge_never_overwrites_and_exports_only_new(self):
        with run() as driver:
            vdl.call("T_digest", digest_tree, self.tree, 1)
            payload = driver.vdl.export_entries()
            with run() as child:
                child.vdl.merge_entries(payload)
                self.assertEqual(child.vdl.export_entries(new_only=True)["entries"], {})
                vdl.call("T_digest", digest_tree, self.tree, 1)
                self.assertEqual(CALLS["digest_tree"], 1)  # served from the shipped entry
        self.assertEqual(len(payload["entries"]), 1)
        with run() as other:
            other.vdl.merge_entries({"schema": "other", "entries": payload["entries"]})
            self.assertEqual(other.vdl.export_entries()["entries"], {})

    def test_physics_admission_v_absent_or_equal_to_p(self):
        with run():
            cache: dict = {}
            self.assertEqual(vdl.call("T_physics", physics_leaf, self.tree, cache), {"bound": 2.5})
            self.assertEqual(cache, {"cal": 2.5})
            fresh: dict = {}
            self.assertEqual(vdl.call("T_physics", physics_leaf, self.tree, fresh), {"bound": 2.5})
            self.assertEqual(fresh, {"cal": 2.5})  # P inserted where V was ABSENT
            self.assertEqual(CALLS["physics_leaf"], 1)
            same = {"cal": 2.5}
            vdl.call("T_physics", physics_leaf, self.tree, same)
            self.assertEqual(CALLS["physics_leaf"], 1)
            other = {"cal": 3.0}
            self.assertEqual(vdl.call("T_physics", physics_leaf, self.tree, other), {"bound": 3.0})
            self.assertEqual(CALLS["physics_leaf"], 2)  # V != P: a miss, the leaf decides
            self.assertEqual(CALLS["refit"], 1)

    def test_physics_insert_outside_the_probed_keys_is_unstorable(self):
        with run():
            vdl.call("T_stray", stray_physics_leaf, self.tree, {})
            vdl.call("T_stray", stray_physics_leaf, self.tree, {})
        self.assertEqual(CALLS["stray_physics_leaf"], 2)

    def test_path_free_hit_across_parents_and_path_in_value_refused(self):
        twin = make_tree(self.tmp / "elsewhere", "bundle")
        with run() as caches:
            first = vdl.call("T_digest_free", digest_tree, self.tree, 1)
            second = vdl.call("T_digest_free", digest_tree, twin, 1)
            self.assertEqual(first, second)
            self.assertEqual(CALLS["digest_tree"], 1)
            renamed = make_tree(self.tmp / "third", "renamed")
            vdl.call("T_digest_free", digest_tree, renamed, 1)
            self.assertEqual(CALLS["digest_tree"], 2)  # the relative name is in the key
            vdl.call("T_path", path_leaf, self.tree, 1)
            vdl.call("T_path", path_leaf, self.tree, 1)
            self.assertEqual(CALLS["path_leaf"], 2)

    def test_path_free_digest_ignores_mode_but_not_content(self):
        twin = make_tree(self.tmp / "elsewhere", "bundle")
        os.chmod(twin / "data.txt", 0o600)
        with run():
            vdl.call("T_digest_free", digest_tree, self.tree, 1)
            vdl.call("T_digest_free", digest_tree, twin, 1)
            self.assertEqual(CALLS["digest_tree"], 1)
        with run():
            CALLS.clear()
            vdl.call("T_digest", digest_tree, self.tree, 1)
            os.chmod(self.tree / "data.txt", 0o600)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 2)  # a full digest includes the mode

    def test_seeded_tree_is_not_rehashed(self):
        shas = {str(path.relative_to(self.tree).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.tree.rglob("*") if path.is_file()}
        hashed = []
        real = vdl.tree_digest
        with run(), vdl.enter_program_scope():
            self.assertTrue(vdl.seed_verified(self.tree, shas))
            self.assertFalse(vdl.seed_verified(self.tree, {**shas, "missing.txt": "0" * 64}))
            with mock.patch.object(vdl, "tree_digest",
                                   lambda root, *, content_only=False: hashed.append(root) or real(root, content_only=content_only)):
                vdl.call("T_digest", digest_tree, self.tree, 1)
        self.assertEqual(hashed, [])
        self.assertEqual(tree_digest_equal(self.tree, shas), True)

    def test_prefetch_verify_serves_the_scope(self):
        with run(), vdl.enter_program_scope() as scope:
            vdl.prefetch_verify([self.tree])
            key = (os.fspath(self.tree.resolve()), False)
            self.assertIn(key, scope.pending)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertIn(key, scope.trees)


def tree_digest_equal(root, shas):
    walked = vdl.tree_digest(root)
    return dict(walked.files) == shas


class SessionBridging(_Base):
    """Hits inside a V2 session: complete rows, consumer grammar verdicts, first-digest pre-check."""

    def serial_records(self, tree, factor=1):
        with aio.V2AuthenticationReadSession() as session:
            value = digest_tree(tree, factor)
        return value, dict(session.records)

    def test_sessionless_fill_without_capability_rows_never_serves_a_session(self):
        with run() as caches:
            vdl.call("T_digest", digest_tree, self.tree, 1)
            with aio.V2AuthenticationReadSession() as session:
                vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 2)
            self.assertTrue(session.records)
            self.assertIn("T_digest:verify_miss", self.counters(caches))

    def test_in_session_fill_serves_a_later_session_with_identical_records(self):
        expected_value, expected = self.serial_records(self.tree)
        CALLS.clear()
        with run():
            with aio.V2AuthenticationReadSession():
                vdl.call("T_digest", digest_tree, self.tree, 1)
            with aio.V2AuthenticationReadSession() as consumer:
                value = vdl.call("T_digest", digest_tree, self.tree, 1)
            # A session-less consumer may use an in-session fill as well.
            vdl.call("T_digest", digest_tree, self.tree, 1)
        self.assertEqual(CALLS["digest_tree"], 1)
        self.assertEqual(value, expected_value)
        self.assertEqual(dict(consumer.records), expected)
        self.assertEqual(list(consumer.records), list(expected))

    def test_path_free_rows_are_relocated_to_the_consumer_tree(self):
        twin = make_tree(self.tmp / "elsewhere", "bundle")
        _, expected = self.serial_records(twin)
        CALLS.clear()
        with run():
            with aio.V2AuthenticationReadSession():
                vdl.call("T_digest_free", digest_tree, self.tree, 1)
            with aio.V2AuthenticationReadSession() as consumer:
                vdl.call("T_digest_free", digest_tree, twin, 1)
        self.assertEqual(CALLS["digest_tree"], 1)
        self.assertEqual(dict(consumer.records), expected)
        self.assertTrue(all(identity.startswith(str(twin.resolve())) for identity in consumer.records))

    def test_first_digest_conflict_discards_the_hit_and_the_serial_read_refuses(self):
        target = str((self.tree / "sub" / "inner.json").resolve())  # read after two other files
        with aio.V2AuthenticationReadSession() as serial:
            serial._register(target, "0" * 64, "json", "earlier read")
            with self.assertRaises(aio.V2AuthenticationInputError):
                digest_tree(self.tree, 1)
        CALLS.clear()
        with run():
            with aio.V2AuthenticationReadSession():
                vdl.call("T_digest", digest_tree, self.tree, 1)
            with aio.V2AuthenticationReadSession() as consumer:
                consumer._register(target, "0" * 64, "json", "earlier read")
                with self.assertRaises(aio.V2AuthenticationInputError) as raised:
                    vdl.call("T_digest", digest_tree, self.tree, 1)
        self.assertEqual(raised.exception.reason, aio.V2_AUTHENTICATION_INPUT_CHANGED)
        self.assertEqual(CALLS["digest_tree"], 2)
        # Nothing of the discarded hit was registered: the session is the serial one.
        self.assertEqual(dict(consumer.records), dict(serial.records))

    def _capability_recorder(self):
        @contextlib.contextmanager
        def recording():
            rows: list = []
            token = _TEST_ROWS.set(rows)
            try:
                yield rows
            finally:
                _TEST_ROWS.reset(token)

        return [mock.patch.object(vdl._AUTH, "recording", recording),
                mock.patch.object(vdl._AUTH, "capability_complete", lambda: True)]

    def test_sessionless_rows_bridge_with_a_consumer_grammar_verdict(self):
        _, expected = self.serial_records(self.tree)
        CALLS.clear()
        with contextlib.ExitStack() as stack:
            for patch in self._capability_recorder():
                stack.enter_context(patch)
            with run():
                vdl.call("T_digest", digest_tree, self.tree, 1)
                with aio.V2AuthenticationReadSession() as consumer:
                    vdl.call("T_digest", digest_tree, self.tree, 1)
                memo = arc.memo(vdl.GRAMMAR_VERDICT_MEMO)
        self.assertEqual(CALLS["digest_tree"], 1)
        self.assertEqual(dict(consumer.records), expected)
        self.assertTrue(memo)

    def test_grammar_invalid_json_from_a_sessionless_fill_refuses_in_the_session(self):
        """Sol #3: a duplicate-key JSON that session-less parsing accepted must still refuse."""

        bad = make_tree(self.tmp, "bad", **{"metadata.json": b'{"a": 1, "a": 2}', "data.txt": b"x"})
        with self.assertRaises(aio.V2AuthenticationInputError):
            self.serial_records(bad)
        CALLS.clear()
        with contextlib.ExitStack() as stack:
            for patch in self._capability_recorder():
                stack.enter_context(patch)
            with run() as caches:
                vdl.call("T_digest", digest_tree, bad, 1)  # session-less: no parse, stored
                with aio.V2AuthenticationReadSession():
                    with self.assertRaises(aio.V2AuthenticationInputError):
                        vdl.call("T_digest", digest_tree, bad, 1)
        self.assertEqual(CALLS["digest_tree"], 2)
        self.assertEqual(caches.vdl.restricted_counters()["T_digest:hit_discarded"], 1)

    def test_probe_is_side_effect_free_until_apply(self):
        with run():
            with aio.V2AuthenticationReadSession():
                vdl.call("T_physics", physics_leaf, self.tree, {})
            with aio.V2AuthenticationReadSession() as consumer:
                cache: dict = {}
                hit = vdl.probe("T_physics", physics_leaf, self.tree, cache)
                self.assertIsNotNone(hit)
                self.assertEqual(cache, {})
                self.assertEqual(dict(consumer.records), {})
                self.assertEqual(hit.apply(), {"bound": 2.5})
                self.assertEqual(cache, {"cal": 2.5})
        self.assertEqual(CALLS["physics_leaf"], 1)

    def test_a_probed_hit_reverifies_at_its_serial_position(self):
        with run():
            vdl.call("T_physics", physics_leaf, self.tree, {})
            cache: dict = {}
            hit = vdl.probe("T_physics", physics_leaf, self.tree, cache)
            cache["cal"] = 9.0  # an earlier member inserted another value meanwhile
            with self.assertRaises(vdl._Bypass):
                hit.apply()
            other: dict = {}
            hit = vdl.probe("T_physics", physics_leaf, self.tree, other)
            (self.tree / "data.txt").write_bytes(b"changed after the probe")
            with self.assertRaises(vdl._Bypass):
                hit.apply()
            self.assertEqual(other, {})
        self.assertEqual(CALLS["physics_leaf"], 1)


class ValueComparison(unittest.TestCase):
    def test_strict_equality_ignores_pickle_layout_but_not_types_or_bits(self):
        shared = "x" * 50
        aliased = vdl.pickle.dumps([shared, shared])
        copied = vdl.pickle.dumps(["x" * 50, "".join(["x"] * 50)])
        self.assertNotEqual(aliased, copied)
        self.assertTrue(vdl._same_value(aliased, copied))
        self.assertFalse(vdl._same_value(vdl.pickle.dumps([1]), vdl.pickle.dumps([1.0])))
        self.assertFalse(vdl._same_value(vdl.pickle.dumps((1,)), vdl.pickle.dumps([1])))
        self.assertFalse(vdl._same_value(vdl.pickle.dumps({"a": 1, "b": 2}), vdl.pickle.dumps({"b": 2, "a": 1})))
        self.assertFalse(vdl._same_value(vdl.pickle.dumps(0.1 + 0.2), vdl.pickle.dumps(0.3)))
        self.assertTrue(vdl._same_value(vdl.pickle.dumps(float("nan")), vdl.pickle.dumps(float("nan"))))


SHADOW_SITE_REFUSAL = "decision-tier refusal"


def _refusing_site(fn):
    """The shape of every listed except site: any Exception becomes a study refusal."""

    try:
        return fn()
    except Exception:  # noqa: BLE001 - the site under test
        return SHADOW_SITE_REFUSAL


class DefectsNeverBecomeRefusals(_Base):
    """Critic item 2 / Sol #11: a VDL defect never surfaces as a study refusal."""

    def shadow_mismatch(self):
        """Fill, then change what the leaf computes, then call under shadow:1000."""

        vdl.call("T_shadow", shadow_target, self.tree, 1)
        NONDETERMINISTIC[0] += 1
        return vdl.call("T_shadow", shadow_target, self.tree, 1)

    def test_shadow_mismatch_returns_the_fresh_value_and_flags_the_run(self):
        with run(vdl.Mode("shadow", 1000)) as caches:
            outcome = _refusing_site(self.shadow_mismatch)
            self.assertEqual(outcome, 1)  # the leaf's fresh value, not the stored 0 and not a refusal
            self.assertTrue(caches.vdl.defect_pending())
            self.assertEqual(caches.vdl.restricted_counters()["T_shadow:shadow_mismatch"], 1)
            with self.assertRaises(vdl.VerifiedStoreDefect):
                _refusing_site(vdl.check_defects)  # BaseException: escapes `except Exception`

    def test_shadow_match_is_not_a_defect(self):
        with run(vdl.Mode("shadow", 1000)) as caches:
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            self.assertEqual(CALLS["digest_tree"], 2)
            self.assertFalse(caches.vdl.defect_pending())
            self.assertEqual(caches.vdl.restricted_counters()["T_digest:shadow"], 1)

    def test_defect_survives_a_base_exception_catch_and_ships_with_entries(self):
        with run() as driver:
            with run(vdl.Mode("shadow", 1000)) as worker:
                try:  # run_member / StepRunner catch BaseException
                    self.shadow_mismatch()
                    raise RuntimeError("the member failed afterwards")
                except BaseException:  # noqa: BLE001
                    pass
                payload = worker.vdl.export_entries(new_only=True)
            self.assertFalse(driver.vdl.defect_pending())
            driver.vdl.merge_entries(payload)
            self.assertTrue(driver.vdl.defect_pending())

    def test_hit_anomalies_fall_through_silently(self):
        with run() as caches:
            vdl.call("T_digest", digest_tree, self.tree, 1)
            with mock.patch.object(vdl.pickle, "loads", side_effect=RuntimeError("corrupt")):
                value = _refusing_site(lambda: vdl.call("T_digest", digest_tree, self.tree, 1))
            self.assertNotEqual(value, SHADOW_SITE_REFUSAL)
            self.assertEqual(CALLS["digest_tree"], 2)
            self.assertFalse(caches.vdl.defect_pending())
            with mock.patch.object(vdl.pickle, "dumps", side_effect=TypeError("unpicklable")):
                value = _refusing_site(lambda: vdl.call("T_digest", digest_tree, self.tree, 2))
            self.assertNotEqual(value, SHADOW_SITE_REFUSAL)
            with mock.patch.object(vdl, "code_digest", side_effect=OSError("unreadable")):
                value = _refusing_site(lambda: vdl.call("T_digest", digest_tree, self.tree, 3))
            self.assertNotEqual(value, SHADOW_SITE_REFUSAL)

    def test_whole_window_strict_validation_site(self):
        """whole_window._strict_validation_problems (critic: ':7731', 'strict validation raised')."""

        from joulewise import whole_window as ww

        with run(vdl.Mode("shadow", 1000)) as caches:
            vdl.call("T_shadow", shadow_target, self.tree, 1)
            NONDETERMINISTIC[0] += 1

            def validator(path, strict):
                return [] if vdl.call("T_shadow", shadow_target, self.tree, 1) == 1 else ["wrong"]

            self.assertEqual(ww._strict_validation_problems(self.tree, validator, None), [])
            self.assertTrue(caches.vdl.defect_pending())

            def defect(path, strict):
                vdl.check_defects()
                return []

            with self.assertRaises(vdl.VerifiedStoreDefect):
                ww._strict_validation_problems(self.tree, defect, None)


# The listed except sites (critic item 2): (file, a literal the handler maps to, or the
# handler's raised name). Each must catch only Exception subclasses, so that a
# VerifiedStoreDefect raised inside the try escapes, and the store itself never raises
# into them (tests above).
EXCEPT_SITES = (
    ("joulewise/whole_window.py", "whole_window_verdict_provenance_invalid", "Exception"),
    ("joulewise/whole_window.py", "reduction_unavailable", "Exception"),
    ("joulewise/whole_window.py", "strict validation raised", "Exception"),
    ("joulewise/whole_window.py", "instrument_calibration_invalid", None),
    ("joulewise/floor_extraction.py", "strict validation raised", "Exception"),
    ("joulewise/b5_analysis/bracket.py", "failed", "Exception"),
    ("joulewise/paper_custody.py", "_ClaimReplayRefused", "Exception"),
    ("joulewise/paper_reported_energy_issuer.py", "reported_energy_replay_refused", "Exception"),
)


def _handler_mentions(handler: ast.ExceptHandler, needle: str) -> bool:
    for node in ast.walk(ast.Module(body=handler.body, type_ignores=[])):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and needle in node.value:
            return True
        if isinstance(node, ast.Name) and node.id == needle:
            return True
    return False


class ListedExceptSites(unittest.TestCase):
    def test_no_listed_site_can_catch_a_store_defect(self):
        self.assertFalse(issubclass(vdl.VerifiedStoreDefect, Exception))
        for relative, needle, expected in EXCEPT_SITES:
            with self.subTest(site=f"{relative}:{needle}"):
                tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
                handlers = [handler for node in ast.walk(tree) if isinstance(node, ast.Try)
                            for handler in node.handlers if _handler_mentions(handler, needle)]
                self.assertTrue(handlers, "site not found; update EXCEPT_SITES with the code")
                if expected is not None:
                    self.assertTrue(any(isinstance(h.type, ast.Name) and h.type.id == expected
                                        for h in handlers))
                module = sys.modules.get(relative[:-3].replace("/", ".")) or __import__(
                    relative[:-3].replace("/", "."), fromlist=["_"])
                for handler in handlers:
                    self.assertIsNotNone(handler.type, "a bare except would catch a defect")
                    caught = eval(compile(ast.Expression(handler.type), relative, "eval"),  # noqa: S307
                                  vars(module), {})
                    caught = caught if isinstance(caught, tuple) else (caught,)
                    for kind in caught:
                        self.assertTrue(issubclass(kind, Exception), kind)
                        self.assertFalse(issubclass(vdl.VerifiedStoreDefect, kind), kind)


class Blinding(_Base):
    def test_counters_never_reach_stdout_stderr_or_logs(self):
        out, err = io.StringIO(), io.StringIO()
        with self.assertNoLogs(level=logging.DEBUG), contextlib.redirect_stdout(out), \
                contextlib.redirect_stderr(err), run(vdl.Mode("shadow", 1000)) as caches:
            vdl.call("T_digest", digest_tree, self.tree, 1)
            vdl.call("T_digest", digest_tree, self.tree, 1)
            counters = caches.vdl.restricted_counters()
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")
        self.assertTrue(counters)
        self.assertNotIn("hit", repr(caches.vdl))

    def test_module_has_no_output_paths(self):
        source = (ROOT / "joulewise/analysis_verified_store.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        self.assertNotIn("print", names)
        self.assertNotIn("logging", names)
        self.assertFalse({"stdout", "stderr", "write_text", "write_bytes"} & attributes)


if __name__ == "__main__":
    unittest.main()


class RealStrictLeaf(unittest.TestCase):
    """L1 end to end on the committed synthetic S10 ALPHA member (no custody data).

    Session-less fill then hit; an in-session call cannot use the session-less
    entry (no capability rows on this AUTH-IO), computes in its session and
    upgrades the entry with that session's rows; a later session is served
    with exactly the serial session's records; a path-free copy under another
    parent hits; shadow:1000 recomputes a hit and finds no mismatch.
    """

    @classmethod
    def setUpClass(cls):
        import tarfile

        from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER

        cls.tmp = Path(tempfile.mkdtemp(prefix="vdl-real-"))
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(cls.tmp, members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)],
                            filter="data")
        cls.member = cls.tmp / MEMBER
        cls.copy = cls.tmp / "copies" / cls.member.name
        shutil.copytree(cls.member, cls.copy)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_strict_validation_leaf(self):
        from joulewise import cli

        strict = mock.patch.object(cli, "_strict_problems", wraps=cli._strict_problems)
        with run(vdl.Mode("shadow", 0)) as caches, strict as counted:
            expected = cli.validate_bundle(self.member, True)
            computed = counted.call_count
            first = vdl.call("L1_strict_validation", cli.validate_bundle, self.member, True)
            second = vdl.call("L1_strict_validation", cli.validate_bundle, self.member, True)
            self.assertEqual(first, expected)
            self.assertEqual(second, expected)
            self.assertEqual(counted.call_count, computed + 1)
            # The path-free copy (another parent, same relative name and bytes) hits.
            self.assertEqual(vdl.call("L1_strict_validation", cli.validate_bundle, self.copy, True), expected)
            self.assertEqual(counted.call_count, computed + 1)
            with aio.V2AuthenticationReadSession() as filler:
                self.assertEqual(vdl.call("L1_strict_validation", cli.validate_bundle, self.member, True),
                                 expected)
            self.assertEqual(counted.call_count, computed + 2)
            with aio.V2AuthenticationReadSession() as consumer:
                self.assertEqual(vdl.call("L1_strict_validation", cli.validate_bundle, self.member, True),
                                 expected)
            self.assertEqual(counted.call_count, computed + 2)
            self.assertEqual(dict(consumer.records), dict(filler.records))
            self.assertEqual(consumer.instrument_calibration_physics_cache,
                             filler.instrument_calibration_physics_cache)
            counters = caches.vdl.restricted_counters()
            self.assertEqual(counters["L1_strict_validation:hit"], 3)
            caches.vdl.mode = vdl.Mode("shadow", 1000)
            with aio.V2AuthenticationReadSession() as shadowed:
                self.assertEqual(vdl.call("L1_strict_validation", cli.validate_bundle, self.member, True),
                                 expected)
            self.assertEqual(counted.call_count, computed + 3)
            self.assertEqual(dict(shadowed.records), dict(filler.records))
            self.assertFalse(caches.vdl.defect_pending())
            self.assertEqual(caches.vdl.restricted_counters()["L1_strict_validation:shadow"], 1)
