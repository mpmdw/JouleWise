"""Offline unit-source acceptance and driver lifecycle with invented objects."""
import base64
import hashlib
import importlib.util
import sys
from collections import Counter
import json
import os
import shutil
import struct
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import contextmanager
from dataclasses import replace
from http.client import IncompleteRead
from pathlib import Path

from joulewise.align.qwen4_gold import stream, unit_source
from joulewise.align.qwen4_gold.core import IndexedCheckpoint, digest, file_stamp, sha256, write_json
from joulewise.align.qwen4_gold.stream_ple import BUFFER_SUFFIXES, SparseCheckpoint, extract_part, official_plan

FIXTURE = Path(__file__).parent / "fixtures/qwen4_gold/provider-fixture.json"
FIXTURE_SHA = "638ebee4772f0b07fb76e0b5a2d962bbe378419d8488acac084cde50c5ca3674"
FLOOR = 40_000_000_000
CAP = 262_144
REF_HASH = "e57b3617e71e81ecb7e5ae3b420c45b5aee80d76a07aa8c88b797c2642f1f5df"
RUNTIMES = {"reference": {"transformers": "5.22.1", "modeling_qwen4_exp.py_sha256": REF_HASH}, "mlx": {}}
TOY_LIMITS = unit_source.Limits(quota=20_000, selection_bytes=32_768, planner_sizes=(4096,)*5,
                                planner_dirs=2, unit_sizes=(4096,)*100, unit_dirs=80,
                                block=31, chunk=257, header=2048)
HAS_NUMPY = importlib.util.find_spec("numpy") is not None
HAS_READERS = HAS_NUMPY and importlib.util.find_spec("safetensors") is not None
HAS_OFFICIAL = HAS_READERS and all(importlib.util.find_spec(name) is not None
                                   for name in ("transformers", "torch"))
A, B = "A.safetensors", "B.safetensors"
PRE = "model.layers.1.ple.ple_embedding."
BUF = [PRE + s for s in BUFFER_SUFFIXES]
BASE = PRE + "ngram_embedding"
EMBED = "model.embed_tokens.weight"
W0,W1,W2 = [f"model.layers.{i}.scale" for i in range(3)]


def frozen():
    raw = FIXTURE.read_bytes()
    if len(raw) != 3208 or hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise AssertionError("frozen fixture bytes changed")
    data = json.loads(raw)
    return data, {f: base64.b64decode(v, validate=True) for f, v in data.pop("objects").items()}


def bound(inputs, limits):
    def small(data):
        raw = json.dumps(data, separators=(",", ":")).encode()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        return raw, len(raw), blob

    return dict(repo="invented/toy", revision=inputs["revision"], pins=inputs["pins"], limits=limits,
                small={"config.json": small(inputs["config"]),
                       "model.safetensors.index.json": small({"weight_map": inputs["weight_map"]})})


class Budget:
    """Independent synthetic allocation broker, including incomplete siblings."""
    def __init__(self, root, cap=CAP, free=None, quantum=4096):
        self.root, self.cap, self.q = root, cap, quantum
        self.free = FLOOR + cap if free is None else free
        self.events = []

    def rounded(self, n):
        return (n + self.q - 1) // self.q * self.q

    def admit(self, event, sizes=(), dirs=0):
        inodes = {}
        for path in [self.root, *self.root.rglob("*")] if self.root.exists() else ():
            st = path.lstat()
            if path.is_symlink():
                raise ValueError("unexpected allocation symlink")
            inodes[st.st_dev, st.st_ino] = max(st.st_blocks * 512,
                                              self.q if path.is_dir() else self.rounded(st.st_size))
        live = sum(inodes.values())
        need = live + dirs * self.q + sum(map(self.rounded, sizes))
        self.events.append((event, live, need))
        if need > self.cap:
            raise ValueError("allocation cap")
        if self.free - need < FLOOR:
            raise ValueError("free floor")
        return need


class Provider:
    """Adapt the frozen seat interface to the same provider the driver uses."""
    def __init__(self, root, inputs, open_object, budget, limits=TOY_LIMITS):
        self.impl = unit_source.Provider(root, bound(inputs, limits), open_object, budget)
        self.impl.start("seat", inputs["prompts"], REF_HASH)
        self.impl.recover()

    @property
    def state(self):
        plan = self.impl.state["plan"]
        objects = {tag: {**rec, "entries": {
            name: {**e, "sha256": rec["files"][e["file"]]["sha256"]} for name, e in rec["entries"].items()}}
                   for tag, rec in self.impl.records.items() if "entries" in rec}
        objects.update({tag: rec for tag, rec in self.impl.records.items() if rec["role"] == "catalogue"})
        return {**self.impl.state, "objects": objects, "plan": plan["response"] if plan else None}

    def file(self, tag, name):
        return self.impl._file(tag, name)

    def discover(self, obj):
        self.impl.discover(obj)

    def project(self, tag, obj, dense, last, sparse_last=None):
        self.impl.project(tag, obj, dense, last, sparse_last, role="planner" if last == "planner" else "regular")

    @contextmanager
    def checkpoint(self, tags, sparse_tags=()):
        with self.impl.checkpoint(tags, sparse_tags) as (ck, guards, store, checksum):
            yield SparseCheckpoint(ck.root, guards, store, checksum) if store else ck

    def plan(self, tags):
        with self.checkpoint(tags) as ck:
            response = official_plan({"prompts": self.impl.prompts}, ck)
        self.impl.install_plan(response, tags, self.impl.planner_bound(1024**3))

    def finish(self, consumer):
        self.impl.finish({consumer})


class Feed:
    """Forward-only, short reads. The byte meter lives outside provider restarts."""
    def __init__(self, objects):
        self.objects, self.visits, self.cut, self.at_read = objects, [], None, None

    @contextmanager
    def open(self, obj):
        raw = self.objects[obj]
        visit = [obj, 0]
        self.visits.append(visit)
        def read(n):
            assert 0 < n <= 31
            if self.at_read:
                self.at_read()
            pos = visit[1]
            if self.cut is not None and pos >= self.cut:
                raise OSError("injected cut")
            end = min(pos+n, pos+11, self.cut if self.cut is not None else len(raw))
            part = raw[pos:end]
            visit[1] += len(part)
            return part
        yield SimpleNamespace(read=read)


class Acceptance(unittest.TestCase):
    def setUp(self):
        w, self.raw = frozen()
        self.limits = TOY_LIMITS
        self.feed, self.inputs = Feed(self.raw), w
        tmp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)/"staging"
        self.root.mkdir()
        direct = self.root.parent/"direct"
        direct.mkdir()
        for name, value in self.raw.items():
            (direct/name).write_bytes(value)
        (direct/"config.json").write_text(json.dumps(w["config"]))
        (direct/"model.safetensors.index.json").write_text(json.dumps({"weight_map":w["weight_map"]}))
        self.direct = IndexedCheckpoint(direct)
        self.budget = Budget(self.root)
        self.start()

    def fresh(self, label):
        self.root = self.root.parent/label
        self.root.mkdir()
        self.budget = Budget(self.root)
        self.start()

    def start(self):
        self.p = Provider(self.root, self.inputs, self.feed.open, self.budget, self.limits)

    def discover(self):
        for obj in (A,B):
            self.p.discover(obj)

    def buffers(self):
        self.p.project("ba",A,[BUF[0]],"planner")
        self.p.project("bb",B,BUF[1:],"planner")

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_reference_parity_timeline_and_last_use(self):
        p = self.p
        phases, cursor = [], 0
        def record(label):
            nonlocal cursor
            events = self.budget.events[cursor:]
            phases.append((label,max(e[2] for e in events)))
            cursor = len(self.budget.events)
        self.discover()
        record("discovery")
        p.project("u0a",A,[EMBED,W0],"u0")
        with p.checkpoint(["u0a"]) as ck:
            self.assertEqual(ck.rows(EMBED,[3,1,3]).tobytes(),self.direct.rows(EMBED,[3,1,3]).tobytes())
        p.finish("u0")
        self.assertFalse((self.root/"u0a"/A).exists())
        record("u0")
        self.buffers()
        with self.assertRaises(FileNotFoundError):
            p.plan(["ba"])  # second original is necessary
        with self.assertRaisesRegex(ValueError,"plan"):
            p.project("early",A,[],"u1","u2")
        p.plan(["ba","bb"])
        record("buffers + planner")
        direct_plan = official_plan({"prompts":self.inputs["prompts"]},self.direct)
        self.assertEqual(p.state["plan"],direct_plan)
        ids = direct_plan["plans"][BASE]["ids"]
        self.assertEqual(ids,[2,3,5])
        self.assertFalse((self.root/"ba"/A).exists())
        # Replay BOTH table originals, folding all current regular tensors on those files.
        p.project("u1a",A,[BUF[0]],"u1","u2")
        p.project("u1b",B,[*BUF[1:],W1],"u1","u2")
        record("tables + folded dense")
        sparse = ["u1a","u1b"]
        for tag in sparse:
            record_obj = p.state["objects"][tag]
            obj = record_obj["obj"]
            for tensor,entry in record_obj["entries"].items():
                expected = extract_part(self.direct.root/obj,tensor,direct_plan["plans"][BASE],
                                        self.direct.root,self.inputs["pins"][obj][1])
                self.assertEqual(entry,expected)  # checks original BF16 words and NPY header
        gather = [ids[-1],ids[0],ids[-1],ids[1]]
        def parity(ck,key):
            left,right = self.direct.ngram_rows(BASE,gather),ck.ngram_rows(BASE,gather)
            self.assertEqual((right.dtype,right.shape,right.tobytes()),(left.dtype,left.shape,left.tobytes()))
            self.assertEqual((right/ck.read(key)).tobytes(),(left/self.direct.read(key)).tobytes())
            with self.assertRaisesRegex(ValueError,"outside sparse store"):
                ck.ngram_rows(BASE,[0])
        with p.checkpoint(sparse,sparse) as ck:
            parity(ck,W1)
        p.finish("u1")
        record("u1 workers + release")
        entries = [self.root/t/e["file"] for t in sparse for e in p.state["objects"][t]["entries"].values()]
        self.assertTrue(all(path.exists() for path in entries))
        self.assertFalse((self.root/"u1b"/B).exists())
        self.start()
        self.p.project("u2b",B,[W2],"u2")
        with self.p.checkpoint(["u2b"],sparse) as ck:
            parity(ck,W2)
        self.p.finish("u2")
        record("restart + u2 + release")
        self.assertTrue(all(not path.exists() for path in entries))
        self.assertEqual(self.feed.visits,[[f,len(self.raw[f])] for f in [A,B,A,A,B,A,B,B]])
        self.assertEqual(self.p.impl.bytes_charged, 4936)
        peak = max(n for _,_,n in self.budget.events)
        live = max(n for _,n,_ in self.budget.events)
        self.assertLessEqual(peak,self.budget.cap)
        self.assertGreaterEqual(self.budget.free-peak,FLOOR)
        print(f"toy visits {self.feed.visits}; traffic {sum(n for _,n in self.feed.visits)} B; "
              f"live {live} B; reserved peak {peak} B; minimum budgeted free {self.budget.free-peak} B")
        groups = {}
        for event,occupied,reserved in self.budget.events:
            groups[event] = max(groups.get(event,0),reserved)
        print("peak by operation",json.dumps(groups,sort_keys=True))
        print("phase reservations",phases)

    def test_missing_malformed_and_unbound_headers(self):
        with self.assertRaisesRegex(ValueError,"missing bound header"):
            self.p.project("absent",A,[W0],"u0")
        original = self.raw[A]
        for field,new in [(b'"BF16"',b'"I64" '),(b'"model.embed',b'"xodel.embed')]:
            with self.subTest(field=field):
                raw = original.replace(field,new,1)
                self.raw[A] = raw
                with self.assertRaisesRegex(ValueError,"ordinary object digest"):
                    self.p.discover(A)
                self.assertNotIn("h-"+A,self.p.state["objects"])
        for n, raw in enumerate((b"noheader", struct.pack("<Q",9999999)+b"{}",
                                 original.replace(b'"BF16"',b'"I64" ',1))):
            self.raw[A] = raw
            self.inputs["pins"][A] = [len(raw),hashlib.sha256(raw).hexdigest()]
            self.fresh("malformed-"+str(n))
            with self.assertRaisesRegex(ValueError,"header|shape/extent"):
                self.p.discover(A)
        self.assertNotIn("h-"+A,self.p.state["objects"])

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_out_of_range_official_ids(self):
        # Invent a different, fully hashed object whose official head offset is invalid.
        raw = bytearray(self.raw[B])
        n, = struct.unpack("<Q",raw[:8])
        lo = json.loads(raw[8:8+n])[BUF[2]]["data_offsets"][0]
        struct.pack_into("<q",raw,8+n+lo,7)
        self.raw[B] = bytes(raw)
        self.inputs["pins"][B] = [len(raw),hashlib.sha256(raw).hexdigest()]
        # Use a fresh invocation for the changed source pin.
        self.fresh("other-stage")
        self.discover()
        self.buffers()
        with self.assertRaisesRegex(ValueError,"outside table"):
            self.p.plan(["ba","bb"])
        self.assertIsNone(self.p.state["plan"])
        with self.assertRaisesRegex(ValueError,"plan"):
            self.p.project("rows",B,[],None,"u2")

    def test_interrupted_replay_and_wrong_discarded_byte(self):
        self.discover()
        self.p.project("first",A,[W0],"u0")
        self.feed.cut = len(self.raw[B])-25
        with self.assertRaisesRegex(OSError,"injected cut"):
            self.p.project("second",B,[W1],"u1")
        self.assertNotIn("second",self.p.state["objects"])
        self.assertGreater((self.root/".pending"/B).stat().st_size,0)
        self.assertEqual(self.feed.visits[-1],[B,self.feed.cut])
        self.start()
        self.assertFalse((self.root/".pending").exists())
        self.assertTrue(self.p.file("first",A).exists())
        self.feed.cut = None
        self.raw[B] = self.raw[B][:-1]+bytes([self.raw[B][-1]^1])
        with self.assertRaisesRegex(ValueError,"ordinary object digest"):
            self.p.project("second",B,[W1],"u1")
        self.assertNotIn("second",self.p.state["objects"])
        self.start()
        self.raw[B] = self.raw[B][:-1]+bytes([self.raw[B][-1]^1])
        self.p.project("second",B,[W1],"u1")
        self.assertEqual(self.feed.visits[-3:],[[B,620],[B,645],[B,645]])
        self.assertEqual(self.p.impl.bytes_charged, sum(n for _, n in self.feed.visits))

    def test_retry_requires_full_quota(self):
        self.limits = replace(TOY_LIMITS, quota=589+645+517+590)
        self.fresh("retry-quota")
        self.discover()
        self.feed.cut = 517
        with self.assertRaises(OSError):
            self.p.project("again", A, [W0], "u0")
        self.start()
        self.assertEqual(self.p.impl.bytes_charged, 589+645+517)
        self.feed.cut = None
        # Another authenticated visit can reserve 590 now, leaving only 1 B.
        self.p.project("again", A, [W0], "u0")
        self.assertEqual(self.p.impl.bytes_charged, self.limits.quota-1)
        count = len(self.feed.visits)
        with self.assertRaisesRegex(ValueError, "source quota"):
            self.p.project("needs-retry", A, [W0], "u0")
        self.assertEqual(len(self.feed.visits), count)
        self.assertEqual(self.feed.visits[-2:], [[A,517],[A,589]])

        self.limits = replace(self.limits, quota=self.limits.quota-1)
        self.fresh("retry-one-byte-short")
        self.discover()
        self.feed.cut = 517
        with self.assertRaises(OSError):
            self.p.project("again", A, [W0], "u0")
        self.start()
        self.feed.cut = None
        count = len(self.feed.visits)
        with self.assertRaisesRegex(ValueError, "source quota"):
            self.p.project("again", A, [W0], "u0")
        self.assertEqual(len(self.feed.visits), count)

    def test_changed_catalogue_or_replay_header(self):
        self.p.discover(A)
        header = self.p.file("h-"+A,"header")
        pristine = header.read_bytes()
        header.write_bytes(pristine.replace(b'"BF16"',b'"F16" ',1))
        count = len(self.feed.visits)
        with self.assertRaisesRegex(ValueError,"committed file"):
            self.p.project("bad",A,[W0],"u0")
        self.assertEqual(len(self.feed.visits),count)
        header.write_bytes(pristine)
        self.raw[A] = self.raw[A].replace(b'"BF16"',b'"F16" ',1)
        with self.assertRaisesRegex(ValueError,"replay header"):
            self.p.project("bad",A,[W0],"u0")
        self.assertNotIn("bad",self.p.state["objects"])


    def test_eof_and_atomic_publication(self):
        self.discover()
        old = self.raw[A]
        for raw,error in [(old[:-1],"short"),(old+b"!","trailing")]:
            self.raw[A] = raw
            with self.assertRaisesRegex(ValueError,error):
                self.p.project("late",A,[W0],"u0")
            self.assertNotIn("late",self.p.state["objects"])
            self.start()
        self.raw[A] = old
        private_sizes = []
        def observe():
            self.assertFalse((self.root/"late").exists())
            self.assertNotIn("late",self.p.state["objects"])
            private_sizes.append((self.root/".pending"/A).stat().st_size)
        self.feed.at_read = observe
        self.p.project("late",A,[W0],"u0")
        self.assertGreater(max(private_sizes),min(private_sizes))
        chunks = [hashlib.sha256(old[i:i+257]).digest() for i in range(0,len(old),257)]
        self.assertEqual(self.p.state["objects"]["late"]["canonical"],hashlib.sha256(b"".join(chunks)).hexdigest())

    def test_rename_before_receipt_requires_full_replay(self):
        self.discover()
        # Stop at the allocation boundary for the replacement journal, after object rename.
        admit = self.budget.admit
        def before_journal(event,*args,**kwargs):
            if event == "old + candidate journal":
                raise InterruptedError("before receipt")
            return admit(event,*args,**kwargs)
        self.budget.admit = before_journal
        with self.assertRaisesRegex(InterruptedError,"before receipt"):
            self.p.project("orphan",B,[W1],"u1")
        self.assertTrue((self.root/"orphan"/B).exists())
        self.assertNotIn("orphan",self.p.state["objects"])
        self.budget.admit = admit
        self.start()
        self.assertFalse((self.root/"orphan").exists())
        self.p.project("orphan",B,[W1],"u1")
        self.assertEqual(self.feed.visits[-2:],[[B,645],[B,645]])
        self.assertEqual(self.p.impl.bytes_charged, sum(n for _, n in self.feed.visits))

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_simultaneous_partials_and_floor(self):
        self.discover()
        self.buffers()
        self.p.plan(["ba","bb"])
        # A has one BF16 part and a dense tensor: two nonempty private files.
        current = self.budget.admit("before")
        self.budget.cap = current + 3*self.budget.q  # dir + owner + just one file
        count = len(self.feed.visits)
        with self.assertRaisesRegex(ValueError,"allocation cap"):
            self.p.project("double",A,[BUF[0]],"u1","u2")
        self.assertEqual(len(self.feed.visits),count)
        self.assertNotIn("double",self.p.state["objects"])
        self.budget.cap = 262144
        self.start()
        self.budget.free = FLOOR+current+4*self.budget.q-1
        with self.assertRaisesRegex(ValueError,"free floor"):
            self.p.project("double",A,[BUF[0]],"u1","u2")
        self.assertEqual(len(self.feed.visits),count)
        # Old incomplete sibling plus a new partial: different inodes, both charged.
        self.budget.free = FLOOR+self.budget.cap
        self.start()
        partial = self.root/"stale.tmp"
        partial.write_bytes(b"x")
        current = self.budget.admit("old partial live")
        self.budget.cap = current+self.budget.q-1
        with self.assertRaisesRegex(ValueError,"allocation cap"):
            self.budget.admit("old + next partial", [1])

    def test_canonical_single_chunk_boundary(self):
        self.limits = replace(self.limits, chunk=len(self.raw[A]))
        self.fresh("one-chunk")
        self.discover()
        self.assertEqual(self.p.state["objects"]["h-"+A]["canonical"], self.inputs["pins"][A][1])
        first, tail = self.raw[B][:589], self.raw[B][589:]
        composite = hashlib.sha256(hashlib.sha256(first).digest()+hashlib.sha256(tail).digest()).hexdigest()
        self.assertEqual(self.p.state["objects"]["h-"+B]["canonical"], composite)

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_empty_selected_part_matches_reader_format(self):
        self.inputs["prompts"] = [{"name": "one-part", "input_ids": [4]}]
        self.fresh("one-part")
        self.discover()
        self.buffers()
        self.p.plan(["ba", "bb"])
        plan = self.p.state["plan"]["plans"][BASE]
        self.assertEqual(plan["ids"], [5])
        for tag, obj in [("empty", A), ("nonempty", B)]:
            self.p.project(tag, obj, [], None, "consumer")
            part = next(iter(self.p.state["objects"][tag]["entries"]))
            expected = extract_part(self.direct.root / obj, part, plan,
                                    self.direct.root, self.inputs["pins"][obj][1])
            self.assertEqual(self.p.state["objects"][tag]["entries"][part], expected)
        with self.p.checkpoint([], ["empty", "nonempty"]) as ck:
            self.assertEqual(ck.ngram_rows(BASE, [5, 5]).tobytes(),
                             self.direct.ngram_rows(BASE, [5, 5]).tobytes())

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_budget_preflights_whole_batch_before_open(self):
        def setup(label):
            self.fresh(label)
            self.discover()
            self.buffers()
            self.p.plan(["ba", "bb"])

        def project():
            self.p.project("batch", A, [BUF[0]], "u1", "u2")

        setup("price")
        mark = len(self.budget.events)
        project()
        required = max(need for _, _, need in self.budget.events[mark:])
        for label in ("cap-short", "floor-short", "exact-fit"):
            with self.subTest(label=label):
                setup(label)
                visits = len(self.feed.visits)
                if label == "cap-short":
                    self.budget.cap = required - 1
                    with self.assertRaisesRegex(ValueError, "allocation cap"):
                        project()
                elif label == "floor-short":
                    self.budget.free = FLOOR + required - 1
                    with self.assertRaisesRegex(ValueError, "free floor"):
                        project()
                else:
                    self.budget.cap = required
                    self.budget.free = FLOOR + required
                    project()
                self.assertEqual(len(self.feed.visits), visits + (label == "exact-fit"))

    def test_unsettled_reservation_is_charged_on_reopen(self):
        self.discover()
        source = self.p.impl
        source._settle_traffic(source._reservation(A))
        self.start()
        self.assertEqual(self.p.impl.bytes_charged, 589+645+590)
        self.assertEqual(self.feed.visits, [[A, 589], [B, 645]])

    def test_incomplete_restore_preserves_spending_with_committed_catalogues(self):
        self.limits = replace(self.limits, quota=1235)
        self.fresh("restore-quota")
        self.discover()
        restored = self.root.parent / "incomplete-backup"
        shutil.copytree(self.root, restored, ignore=shutil.ignore_patterns("traffic.json"))
        reopened = Provider(restored, self.inputs, self.feed.open, Budget(restored), self.limits)
        reopened.discover(A)
        reopened.discover(B)
        self.assertEqual(reopened.impl.bytes_charged, 1234)
        with self.assertRaisesRegex(ValueError, "source quota"):
            reopened.project("needs-visit", A, [W0], "u0")
        self.assertEqual(self.feed.visits, [[A, 589], [B, 645]])

    def test_missing_or_reset_traffic_record_cannot_authorize_reuse(self):
        self.discover()
        journal = self.p.impl.journal
        state = json.loads(journal.read_bytes())
        for traffic, message in [(None, "invalid provider traffic ledger"),
                                 ({"spent": 0, "reserved": 0}, "predates committed receipts")]:
            with self.subTest(traffic=traffic):
                restored = {k: v for k, v in state.items() if k != "traffic"}
                if traffic is not None:
                    restored["traffic"] = traffic
                journal.write_bytes(unit_source.encode(restored))
                with self.assertRaisesRegex(ValueError, message):
                    self.start()
        self.assertEqual(self.feed.visits, [[A, 589], [B, 645]])

    def test_missing_authoritative_ledger_does_not_start_fresh(self):
        source = self.p.impl
        source._settle_traffic(source._reservation(A))
        source.journal.unlink()
        with self.assertRaisesRegex(ValueError, "provider journal"):
            self.start()
        self.assertEqual(self.feed.visits, [])

    def test_provider_recovers_interrupted_genesis(self):
        replace_file = Path.replace

        def interrupt(candidate, target):
            if target.name == "journal.json":
                raise InterruptedError("before genesis publication")
            return replace_file(candidate, target)

        with patch.object(Path, "replace", interrupt):
            with self.assertRaisesRegex(InterruptedError, "genesis publication"):
                self.fresh("torn-genesis")
        self.start()
        self.assertEqual(self.p.impl.bytes_charged, 0)
        self.assertEqual(self.feed.visits, [])
        self.p.discover(A)
        self.assertEqual(self.p.impl.bytes_charged, 589)

    def test_incomplete_read_exception_charges_partial_bytes(self):
        for phase, expected in (("first read", 7), ("EOF probe", 590)):
            with self.subTest(phase=phase):
                self.fresh(phase)
                delivered = bytearray()

                @contextmanager
                def source(name):
                    def read(n):
                        remaining = self.raw[name][len(delivered):]
                        if phase == "first read" or not remaining:
                            partial = remaining[:7] if remaining else b"!"
                            delivered.extend(partial)
                            raise IncompleteRead(partial)
                        block = remaining[:n]
                        delivered.extend(block)
                        return block
                    yield SimpleNamespace(read=read)

                interrupted = Provider(self.root, self.inputs, source, self.budget, self.limits)
                with self.assertRaises(IncompleteRead):
                    interrupted.discover(A)
                self.assertEqual(len(delivered), expected)
                self.assertEqual(interrupted.impl.bytes_charged, expected)
                self.start()
                self.assertEqual(self.p.impl.bytes_charged, expected)
                self.assertEqual(self.p.state["objects"], {})
                self.p.discover(A)
                self.assertEqual(self.p.impl.bytes_charged, expected + 589)

    def test_damaged_projection_requires_another_authenticated_visit(self):
        self.discover()
        self.p.project("keep", A, [W0], "u0")
        self.p.project("damaged", B, [W1], "u1")
        first = sha256(self.p.file("keep", A))
        self.p.file("damaged", B).write_bytes(b"broken")
        self.start()
        self.p.project("damaged", B, [W1], "u1")
        self.assertEqual(self.feed.visits[-2:], [[B, 645], [B, 645]])
        self.assertEqual(self.p.impl.bytes_charged, sum(n for _, n in self.feed.visits))
        self.assertEqual(sha256(self.p.file("keep", A)), first)


class DriverTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.work = self.base / "run"
        self.inputs, objects = frozen()
        # The provider seam's frozen objects omit driver endpoints. Add
        # tiny endpoint words to a copy and re-pin this separate inventory.
        original = objects[A]
        length = int.from_bytes(original[:8], "little")
        header = json.loads(original[8:8+length])
        payload = original[8+length:]
        self.endpoints = {"final": "model.hyper_connection_mixer.scale", "head": "lm_head.weight"}
        for name in self.endpoints.values():
            offset = len(payload)
            payload += struct.pack("<f", 1)
            header[name] = dict(dtype="F32", shape=[1], data_offsets=[offset, len(payload)])
            self.inputs["weight_map"][name] = A
        raw = json.dumps(header, separators=(",", ":")).encode()
        raw += b" " * (-len(raw) % 8)
        objects[A] = struct.pack("<Q", len(raw)) + raw + payload
        self.inputs["pins"][A] = [len(objects[A]), hashlib.sha256(objects[A]).hexdigest()]
        self.inputs["config"].update(hidden_size=2, hc_count=2)
        self.feed = Feed(objects)
        self.prompt_path = self.base / "prompts.json"
        self.prompt_path.write_text(json.dumps(self.inputs["prompts"]))
        self.adapter = self.base / "adapter.py"
        self.adapter.write_text("# synthetic harness\n")
        self.env = patch.dict(os.environ, {"HF_HUB_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def make_driver(self, resume=False, *, work=None, runtimes=RUNTIMES, budget=None, **updates):
        work = work or self.work
        work.mkdir(exist_ok=True)
        budget = budget if budget is not None else Budget(work, cap=2*1024**2)
        provider = unit_source.Provider(work / "unit-source", bound(self.inputs, TOY_LIMITS),
                                        self.feed.open, budget)
        args = dict(work=work, min_free_gb=25, max_staging_gb=12, max_gb=4, timeout=60,
                    resume=resume, keep_going=False, ref_python=sys.executable, mlx_python=sys.executable,
                    adapter_dependency=[], mlx_module=self.adapter, prompts_json=self.prompt_path,
                    seed=1, random_scale=1, convert_out=None, canonical_converter=None,
                    canonical_module=None, shared_shards="retain")
        args.update(updates)
        with patch.object(stream, "HubSource", side_effect=AssertionError("hub contacted")):
            return stream.StreamDriver(SimpleNamespace(**args), runtimes=runtimes, unit_source=provider)

    def test_driver_prices_large_provenance_before_writing(self):
        for i in range(129):
            name = f"scalar-{i:03}.safetensors"
            tensor = f"model.layers.0.scalar_{i:03}"
            header = json.dumps({tensor: dict(dtype="F32", shape=[], data_offsets=[0, 4])},
                                separators=(",", ":")).encode()
            header += b" " * (-len(header) % 8)
            raw = struct.pack("<Q", len(header)) + header + struct.pack("<f", 0)
            self.feed.objects[name] = raw
            self.inputs["pins"][name] = [len(raw), hashlib.sha256(raw).hexdigest()]
            self.inputs["weight_map"][tensor] = name

        work = self.work
        work.mkdir()
        broker = Budget(work, cap=36_864)
        with self.assertRaisesRegex(ValueError, "allocation cap"):
            self.make_driver(budget=broker)
        exact = next(need for event, _, need in broker.events if event == "fixture initialization files")
        for cap, free, error in ((exact-1, FLOOR+exact, "allocation cap"),
                                 (exact, FLOOR+exact-1, "free floor")):
            with self.subTest(error=error):
                broker = Budget(work, cap=cap, free=free)
                with self.assertRaisesRegex(ValueError, error):
                    self.make_driver(budget=broker)
                self.assertTrue(all(live <= cap for _, live, _ in broker.events))
                self.assertFalse((work / "parity").exists())
                self.assertFalse((work / "manifest.json").exists())
        broker = Budget(work, cap=exact)
        self.make_driver(budget=broker)
        self.assertEqual(max(need for _, _, need in broker.events), exact)
        self.assertLess(broker.admit("initialized fixture"), exact)
        self.assertEqual(self.feed.visits, [])

    def test_driver_recovers_interrupted_initialization_publications(self):
        replace_file = Path.replace
        for name in ("provenance.json", "manifest.json"):
            with self.subTest(name=name):
                work = self.base / name
                candidates = []

                def interrupt(candidate, target):
                    if target.name == name:
                        candidates.append(candidate)
                        raise InterruptedError("before initialization publication")
                    return replace_file(candidate, target)

                with patch.object(Path, "replace", interrupt):
                    with self.assertRaisesRegex(InterruptedError, "initialization publication"):
                        self.make_driver(work=work)
                self.assertEqual(len(candidates), 1)
                self.assertTrue(candidates[0].is_file())
                self.assertEqual(self.feed.visits, [])
                driver = self.make_driver(resume=True, work=work)
                self.assertTrue(driver.path.is_file())
                self.assertTrue((work / "parity/provenance.json").is_file())
                self.assertFalse(candidates[0].exists())
        self.assertEqual(self.feed.visits, [])

    def test_driver_refuses_missing_provider_after_uncommitted_source_attempt(self):
        driver = self.make_driver()
        self.feed.cut = 17
        with self.assertRaisesRegex(OSError, "injected cut"):
            driver.run()
        self.assertEqual(driver.unit_source.bytes_charged, 17)
        self.assertEqual(driver.state["units"], {})
        driver.unit_source.root.rename(self.base / "full-provider")
        driver.unit_source.root.mkdir()
        with patch.object(self.feed, "open", side_effect=AssertionError("unexpected source retry")):
            reopened = self.make_driver(resume=True)
            with self.assertRaisesRegex(ValueError, "missing provider journal"):
                reopened.run()
        self.assertFalse(reopened.unit_source.journal.exists())
        self.assertEqual(self.feed.visits, [[A, 17]])

    def test_driver_recovers_before_first_source_authorization(self):
        driver = self.make_driver()
        with patch.object(driver, "save", side_effect=InterruptedError("before source authorization")):
            with self.assertRaisesRegex(InterruptedError, "source authorization"):
                driver.run()
        self.assertEqual(driver.unit_source.bytes_charged, 0)
        self.assertFalse(json.loads(driver.path.read_bytes())["fixture_provider_started"])
        self.assertEqual(self.feed.visits, [])
        self.feed.cut = 17
        resumed = self.make_driver(resume=True)
        with self.assertRaisesRegex(OSError, "injected cut"):
            resumed.run()
        self.assertTrue(json.loads(resumed.path.read_bytes())["fixture_provider_started"])
        self.assertEqual(resumed.unit_source.bytes_charged, 17)

    def harness(self, driver, *, interrupt=False):
        import numpy as np

        seen = []
        sizes = {}
        weights = {"embed": EMBED, "0": W0, "1": W1, "2": W2, **self.endpoints}

        def case(unit, dtype, prompt, mode, hidden, **kwargs):
            ck = driver.harness.checkpoint
            args = driver.args.worker_extra
            guards = driver.harness.identity["stamps"]
            filename = self.inputs["weight_map"][weights[unit]]
            self.assertEqual(ck.shard_guards, guards)
            self.assertEqual(file_stamp(ck.root / filename), guards[filename])
            if unit == "embed":
                ck.rows(EMBED, [0])
            else:
                ck.read(weights[unit], selection=(slice(0, 1),))
            if unit == "1":
                self.assertEqual(set(guards), {A, B})
                for buf in BUF:
                    self.assertEqual(ck.info(buf)[1], "I64")
            if unit in ("1", "2", "final", "head"):
                worker = SparseCheckpoint(ck.root, guards, args["sparse_store"], args["sparse_digest"])
                self.assertEqual(worker.ngram_rows(BASE, [5, 3, 5]).shape, (3, 2))
            else:
                self.assertNotIn("sparse_store", args)
            if hidden is not None and mode == "real":
                index = driver.plan["units"].index(unit)
                np.testing.assert_array_equal(np.load(hidden), index)
                self.assertEqual(hidden.name, "output.npy" if "rerun-inputs" not in hidden.parts
                                 else f"{dtype}-{prompt['name']}.npy")
            seen.append((unit, mode, len(self.feed.visits), args["fixture_projection"]))
            if interrupt and unit == "1" and mode == "random":
                raise InterruptedError("worker interrupted")
            name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
            output = driver.harness.out / name / f"{prompt['name']}-{dtype}-{mode}" / "reference/output.npy"
            output.parent.mkdir(parents=True, exist_ok=True)
            np.save(output, np.full((1, len(prompt["input_ids"]), 2), driver.plan["units"].index(unit)+1, np.float32))
            sizes[unit] = sizes.get(unit, 0) + 1
            return output

        def publish(unit, finished=False):
            self.assertTrue(finished)
            self.assertEqual(sizes[unit], len(driver.prompts) * (4 if unit != "embed" else 2))
            name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
            result = {"status": "PASS", "cases": []}
            write_json(driver.harness.out / f"{name}.json", result)
            return result

        driver.harness.case, driver.harness.publish = case, publish
        return seen

    def stop_after_embed(self, driver):
        self.harness(driver)
        release = driver.release

        def interrupt():
            release()
            if "embed" in driver.state["units"]:
                raise InterruptedError("embed committed")

        with patch.object(driver, "release", interrupt):
            with self.assertRaisesRegex(InterruptedError, "embed committed"):
                driver.run()

    @unittest.skipUnless(HAS_READERS, "requires the pinned offline array readers")
    def test_driver_refuses_restore_missing_provider_after_unit_commit(self):
        driver = self.make_driver()
        provider = driver.unit_source
        start = provider.start
        snapshots = []

        def remember_genesis(*args, **kwargs):
            start(*args, **kwargs)
            snapshots.append(provider.journal.read_bytes())

        with patch.object(provider, "start", remember_genesis):
            self.stop_after_embed(driver)
        self.assertEqual(set(driver.state["units"]), {"embed"})
        self.assertEqual(driver.unit_source.bytes_charged, 2159)
        backup = self.base / "complete-fixture"
        self.work.rename(backup)
        shutil.copytree(backup, self.work, ignore=shutil.ignore_patterns("unit-source"))
        with patch.object(self.feed, "open", side_effect=AssertionError("unexpected source retry")):
            reopened = self.make_driver(resume=True)
            reopened.validate_done()
            with self.assertRaisesRegex(ValueError, "missing provider journal"):
                reopened.run()
        self.assertFalse(reopened.unit_source.root.exists())
        reopened.unit_source.root.mkdir()
        shutil.copyfile(backup / "unit-source/.owner", reopened.unit_source.root / ".owner")
        reopened.unit_source.journal.write_bytes(snapshots[0])
        with patch.object(self.feed, "open", side_effect=AssertionError("unexpected source retry")):
            reopened = self.make_driver(resume=True)
            with self.assertRaisesRegex(ValueError, "predates committed fixture spending"):
                reopened.run()
        self.assertEqual(self.feed.visits, [[A, 757], [B, 645], [A, 757]])

    @unittest.skipUnless(HAS_READERS, "requires the pinned offline array readers")
    def test_driver_recovers_interrupted_rerun_input_publication(self):
        original = self.make_driver()
        self.stop_after_embed(original)
        work = self.base / "selected"
        replace_file = Path.replace

        def interrupt(candidate, target):
            if target.suffix == ".npy":
                raise InterruptedError("before copied input publication")
            return replace_file(candidate, target)

        args = dict(work=work, rerun_from=self.work, units=["0"])
        before = len(self.feed.visits)
        with patch.object(Path, "replace", interrupt):
            with self.assertRaisesRegex(InterruptedError, "copied input publication"):
                self.make_driver(**args)
        resumed = self.make_driver(resume=True, **args)
        for row in resumed.state["rerun"]["inputs"]["embed"].values():
            self.assertEqual(sha256(row["path"]), row["sha256"])
        self.assertEqual(len(self.feed.visits), before)

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_driver_uses_guarded_views_and_commits_chain_before_release(self):
        driver = self.make_driver()
        interrupted = self.harness(driver, interrupt=True)
        original = stream.execute
        def execute(python, request, directory, max_gb, timeout):
            self.assertEqual(request["backend"], "ple_plan")
            self.assertEqual(request["prompts"], self.inputs["prompts"])
            self.assertEqual(request["config_digest"], digest(self.inputs["config"]))
            self.assertEqual(request["weight_map_digest"], digest(self.inputs["weight_map"]))
            self.assertEqual(set(request["shard_guards"]), {A, B})
            self.assertEqual(python, sys.executable)
            return original(python, request, directory, max_gb, timeout)
        with patch.object(stream, "execute", side_effect=execute) as planner:
            with self.assertRaisesRegex(InterruptedError, "worker interrupted"):
                driver.run()
        planner.assert_called_once()
        before = json.loads(driver.path.read_bytes())
        self.assertEqual(set(before["units"]), {"embed", "0"})
        self.assertNotIn("1", before["chain"])
        self.assertTrue((driver.unit_source.root / f"table-{B}" / B).exists())
        self.assertNotEqual(before["fixture_plan"], None)
        visited = len(self.feed.visits)
        self.assertEqual([f for f, _ in self.feed.visits], [A, B, A, A, A, B, A, B])
        resumed = self.make_driver(resume=True)
        seen = self.harness(resumed)
        with patch.object(stream, "execute", side_effect=AssertionError("planner re-executed")):
            result = resumed.run()
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["coverage"]["full_48_layer_gold"])
        self.assertEqual(result["fingerprint"], before["fingerprint"])
        self.assertEqual(result["fixture_source"]["plan"], before["fixture_plan"])
        self.assertEqual({n for unit, _, n, _ in seen if unit == "1"}, {visited})
        self.assertEqual({fp for unit, _, _, fp in seen if unit == "1"}, {interrupted[-1][3]})
        self.assertEqual(Counter(f for f, _ in self.feed.visits), Counter({A: 7, B: 4}))
        self.assertEqual(result["fixture_source"]["source_bytes"], sum(n for _, n in self.feed.visits))
        peak = max(need for budget in (driver.unit_source.budget, resumed.unit_source.budget)
                   for _, _, need in budget.events)
        print(f"synthetic driver visits {self.feed.visits}; traffic {result['fixture_source']['source_bytes']} B; "
              f"reserved peak {peak} B; floor margin {resumed.unit_source.budget.free-FLOOR-peak} B")
        self.assertTrue(resumed.unit_source.store.exists())
        self.assertFalse(any(resumed.unit_source.root.rglob("*.npy")))
        self.assertFalse(any(path.is_file() for path in resumed.unit_source.root.rglob("*.safetensors")))
        resumed.validate_done()

    @unittest.skipUnless(HAS_OFFICIAL, "requires the pinned offline planner runtime")
    def test_driver_resumes_after_unit_commit_before_unlink(self):
        driver = self.make_driver()
        self.harness(driver)
        release = driver.unit_source.release
        def crash_after_ack():
            if "1" in driver.unit_source.state["done"]:
                manifest = json.loads(driver.path.read_bytes())
                self.assertEqual(manifest["units"]["1"]["status"], "PASS")
                self.assertTrue(all(Path(f).is_file() for f in manifest["chain"]["1"].values()))
                self.assertTrue((driver.unit_source.root / f"table-{B}" / B).exists())
                raise InterruptedError("committed before unlink")
            return release()
        with patch.object(driver.unit_source, "release", side_effect=crash_after_ack):
            with self.assertRaisesRegex(InterruptedError, "committed before unlink"):
                driver.run()
        before = len(self.feed.visits)
        resumed = self.make_driver(resume=True)
        seen = self.harness(resumed)
        summary = resumed.run()
        self.assertEqual(summary["status"], "PASS")
        self.assertEqual(seen[0][:3], ("2", "real", before+1))
        self.assertFalse((resumed.unit_source.root / f"table-{B}" / B).exists())
        self.assertEqual(Counter(f for f, _ in self.feed.visits), Counter({A: 7, B: 4}))
        self.assertEqual(summary["fingerprint"], driver.state["fingerprint"])

        # A separate rerun rebuilds released sparse views and verifies the
        # original official predecessor, then performs only the selected unit.
        before = len(self.feed.visits)
        rerun = self.make_driver(work=self.base/"rerun", rerun_from=self.work, units=["2"])
        self.harness(rerun)
        selected = rerun.run()
        self.assertEqual(set(selected["units"]), {"2"})
        self.assertEqual([f for f, _ in self.feed.visits[before:]], [A, B, A, B, A, B, B])
        for key, metadata in rerun.state["rerun"]["inputs"]["1"].items():
            self.assertEqual(metadata["source"], resumed.state["chain"]["1"][key])
            self.assertEqual(sha256(metadata["path"]), metadata["sha256"])

    def test_driver_rejects_changed_invocation_before_source_open(self):
        driver = self.make_driver()
        with driver.driver_lock():
            with self.assertRaisesRegex(RuntimeError, "another streaming driver"):
                driver.run()
        with self.assertRaisesRegex(ValueError, "invocation changed"):
            self.make_driver(resume=True, seed=2)
        with self.assertRaisesRegex(ValueError, "convert_out"):
            self.make_driver(resume=True, convert_out=self.base / "export")
        with patch.object(stream, "HubSource", side_effect=AssertionError("hub contacted")):
            with self.assertRaisesRegex(ValueError, "changed source mode"):
                stream.StreamDriver(driver.args, runtimes=RUNTIMES)
        with self.assertRaisesRegex(ValueError, "bound metadata"):
            unit_source.Provider(driver.unit_source.root, {}, self.feed.open, driver.unit_source.budget)
        with self.assertRaisesRegex(ValueError, "object opener"):
            unit_source.Provider(driver.unit_source.root, bound(self.inputs, TOY_LIMITS), None,
                                 driver.unit_source.budget)
        self.assertEqual(self.feed.visits, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
