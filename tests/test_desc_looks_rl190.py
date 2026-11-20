"""RL-190 §3 acceptance supplement. Run with the frozen v2.1.1 and v2.2.1 modules on PYTHONPATH.

The fixture translates public facts into the normalized Book/World input of v2.1.1.
All identifiers, references, epochs, hardware observations and Git objects created here
are invented. RecordVectors test the desk's documentary rules separately from the CLI.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_desc_looks_acceptance as frozen


INST, STAB1, STAB2 = frozen.IDS
UUID = "00112233-4455-4677-89ab-cdef01234567"
OTHER_UUID = "baadf00d-1111-4222-8abc-000000000002"
BOOT_UUID = "88888888-1111-4222-8abc-000000000003"
HOSTNAME = "invented-air.invalid"
# Independently computed test vector. No host identifier is read to construct it.
HOST = "hw1:" + hashlib.sha256(("joulewise.execution_host.v1:" + UUID.upper()).encode("utf-8")).hexdigest()
SHAPES = ((3, 2, 1, 2, 2, 2), (2,) * 6, (2,) * 6)
LOADED = "f2-inst-02/L005"
SOLO = "f2-inst-01/L006"
KEYS = tuple(f"f2-inst-{kit:02}/L{leg:03}" for kit in range(1, 4) for leg in range(1, 13))


def spans():
    groups = {}
    for kit, lengths in enumerate(SHAPES, 1):
        start = 1
        for number, length in enumerate(lengths, 1):
            name = f"invented-span-{kit}-{number}"
            groups[name] = tuple(f"f2-inst-{kit:02}/L{leg:03}" for leg in range(start, start + length))
            start += length
    return groups


GROUPS = spans()
LOCATION = {key: (span, index) for span, group in GROUPS.items() for index, key in enumerate(group)}
read, put, sha, wire = frozen.read, frozen.put, frozen.sha, frozen.wire


# Only device observations are replaced. Production hashes, Git ancestry, admission,
# CLI processes and reservation order execute normally. No real ioreg/sysctl is run.
HARDWARE = r'''
import json, os, re, shlex, socket, subprocess, sys
socket.gethostname = lambda: os.environ["R190_NODENAME"]
_delegate = subprocess.Popen
class _InventedDevice(_delegate):
    def __init__(self, args, *a, **kw):
        cmd = args if isinstance(args, (list, tuple)) else shlex.split(os.fsdecode(args))
        executable = os.path.basename(os.fsdecode(cmd[0]))
        if executable in ("sh", "zsh", "bash") and "-c" in cmd:
            # A composite shell probe is outside this fixture adapter.
            if re.search(r"\b(ioreg|sysctl|hostname)\b", os.fsdecode(cmd[cmd.index("-c")+1])):
                raise RuntimeError("unmodeled shell device query")
        if executable in ("ioreg", "sysctl", "hostname"):
            if executable == "ioreg":
                data = os.environ["R190_IOREG"]
            elif executable == "hostname":
                data = os.environ["R190_NODENAME"] + "\n"
            else:
                data = os.environ["R190_BOOT"] + "\n"
            if "log" in globals():
                log("device_query", executable)
            kw.pop("executable", None)
            kw["shell"] = False
            args = [sys.executable, "-S", "-c", "import sys; sys.stdout.write(sys.argv[1])", data]
        super().__init__(args, *a, **kw)
subprocess.Popen = _InventedDevice
def guard_device(event, args):
    if event in ("os.system", "os.exec", "os.posix_spawn", "subprocess.Popen"):
        command = os.fsdecode(args[0]) if isinstance(args[0], (bytes,str)) else ""
        if (event == "os.system" and re.search(r"\b(ioreg|sysctl|hostname)\b", command)) or os.path.basename(command) in ("ioreg", "sysctl", "hostname"):
            raise RuntimeError("direct live device query outside the fixture adapter")
sys.addaudithook(guard_device)
'''


def device_output(*uuids):
    return "".join(f'    | "IOPlatformUUID" = "{value}"\n' for value in uuids)


@contextmanager
def device(nodename=HOST, values=(UUID,), boundary=False):
    probe = frozen.PROBE + HARDWARE
    if boundary:
        probe += '''
def intercept(event, args):
    if event == "os.mkdir" and args[0] == os.environ["DESC_RESERVATION"]:
        log("reservation_attempt", args[0])
        raise PermissionError("end of synthetic preflight")
sys.addaudithook(intercept)
'''
    with patch.dict(os.environ, R190_NODENAME=nodename, R190_IOREG=device_output(*values),
                    R190_BOOT=BOOT_UUID), patch.object(frozen, "PROBE", probe):
        yield


def placeholders(folder, *unused, hand_table=False):
    # A frozen-copy inventory needs paths and hashes. Preflight must never open them.
    for name in ("support.json", "dc_points.csv", "power_trace.csv"):
        put(folder / name, b"invented unopened input\n")


def typed_item(key, reason, evidence, evidence_hash):
    item = dict(schema="joulewise.run_state_item.v1", owner="lead", number=900002,
                issued_epoch_s=1800000000, expires_epoch_s=None, status="ISSUED", sets=[], supersedes=[])
    return (f"900002. **Invented terminal declaration for {key}.**\n\n"
            + chr(96)*3 + "item\n" + wire(item).decode() + chr(96)*3 + "\n\n"
            + f"The lead declares {key} dropped:{reason}. No member exists or will exist. "
            + f"Evidence {evidence} sha256={evidence_hash}.\n").encode()


class AsRun(frozen.World):
    """Use frozen registration, pins and Git book. Group members BEFORE sealing the projection."""
    def __init__(self, base, scenario="ordinary", target=SOLO, defect=None, over=False,
                 look=INST, late=False):
        self.scenario, self.target, self.defect, self.over = scenario, target, defect, over
        self.late = late
        self.manifest_registration = None
        self.final_bytes = {}
        seal = frozen.Book.seal
        def snapshot(book, label):
            if late and label == "register public designs and identifiers before any close":
                self.final_bytes = {p: p.read_bytes() for p in (book.path / "manifests").glob("*.json")}
                for p in self.final_bytes:
                    p.unlink()
            if label == "close snapshot":
                delayed = {}
                if self.scenario == "drop" and self.defect == "late_queue":
                    # The final queue already establishes "unrun". Only the decision
                    # and its pointer arrive after the operational evidence snapshot.
                    for p in (book.path / "RUN_STATE.md", book.path / ("drops/" + self.target + ".json")):
                        delayed[p] = p.read_bytes()
                        p.unlink()
                projection = seal(book, label)
                if delayed:
                    for p, data in delayed.items():
                        put(p, data)
                    seal(book, "invented lead declares the unrun key after projection")
                if late:
                    for p, data in self.final_bytes.items():
                        put(p, data)
                    self.manifest_registration = seal(book, "invented final registration after projection")
                return projection
            return seal(book, label)

        layout = frozen.layout
        def populated(name):
            if name != INST:
                return layout(name)
            return [(kit, leg, 1, 12 * (kit - 1) + leg) for kit in range(1, 4) for leg in range(1, 13)]
        with patch.object(frozen, "layout", populated), patch.object(frozen, "traces", placeholders), \
                patch.object(frozen.Book, "seal", snapshot), patch.object(frozen.socket, "gethostname", return_value=HOST):
            super().__init__(base, look)

    def leg(self, kit, pos, v, day, ordinal, status):
        if self.inst:
            if status != "qualified":  # World appends two extra synthetic stability-style exclusions.
                return
            key = f"f2-inst-{kit:02}/L{pos:03}"
            if key == self.target and self.scenario in ("drop", "pending"):
                return
        return super().leg(kit, pos, v, day, ordinal, status)

    def declare_unrun_positions(self):
        # This family owns its grouped receipts and every deliberately missing or malformed drop.
        self.group_members()

    def named(self, name, path, doc):
        if name == "roster" and self.inst:
            if self.scenario == "missing":
                self.rows[:] = [r for r in self.rows if r["key"] != self.target]
            if self.scenario == "duplicate_masks_missing":
                self.rows[-1] = next(r.copy() for r in self.rows if r["key"] == self.target)
                assert len(self.rows) == len(KEYS)
            if self.scenario == "duplicate":
                self.rows.append(next(r.copy() for r in self.rows if r["key"] == self.target))
        if name == "cold":
            registration = self.manifest_registration or self.reg
            self.span_ledger = {}
            for span, close in getattr(self, "span_closes", {}).items():
                mark = read(self.repo / "checks" / (span + ".json"))["offload_manifest_sha256"]
                self.span_ledger[span] = dict(close_epoch_s=close, projection_commit=self.receipts,
                                              registration_commit=registration, offload_manifest_sha256=mark)
            doc = dict(doc, **self.cold_evidence())
        if name == "cold" and self.scenario == "early_cold":
            # The initial Book otherwise contains an effective freeze from the first commit.
            put(self.targets["freeze"], dict(self.freeze, twin_agrees="no"))
            super().named(name, path, doc)
            self.cold_commit = self.book.seal("invented cold signature while freeze ineffective")
            put(self.targets["freeze"], self.freeze)
            return
        if name == "freeze" and self.scenario == "early_cold":
            doc = dict(doc, twin_agrees="no")
        return super().named(name, path, doc)

    def cold_evidence(self):
        manifest = read(self.man)
        inventory = manifest["outputs"]
        pins = manifest["code_pins"]
        proof = {"manifest_sha256": sha(self.man.read_bytes()), "executor_revision": pins["reader"]["sha256"],
                 "schema_revisions": {role: val["sha256"] for role, val in pins.items() if "schema" in role},
                 "public_inventory": {k: v for k, v in inventory.items() if k != "custody_names"},
                 "restricted_inventory": inventory["custody_names"]}
        # Invented stand-ins for already-reviewed desk artifacts. The detached live
        # rehearsal and hand analysis are external to this fixture.
        for role, entry in {
            "synthetic_hand_tables": {"source": "invented hand table", "verdict": "agrees"},
            "row7": {"spans": sorted({r["receipt"] for r in self.rows if "receipt" in r}),
                     "hand_comparison": "agrees", "q1": True, "desk_final": True},
            "host_rehearsal": {"literal_directory": "RESTRICTED", "host": HOST,
                               "revision": rehearsal_revision(pins), "passed": True},
            "once_only": {"reservation_attempts_allowed": 1, "second_invocation_refused": True},
        }.items():
            location = f"authority/examples/{role}.json"
            put(self.repo / location, entry)
            proof[role] = {"path": location, "sha256": sha(wire(entry))}
        dropped = {}
        if self.inst and self.scenario in ("drop", "hide_member"):
            dropped[self.target] = ("ended_without_member" if self.defect in ("span", "no_item_span", "wrong_span")
                                    else "queue_retired")
        exclusions = {LOADED: "loaded"} if self.inst and LOADED in self.records else {}
        if self.inst and self.scenario == "wall" and self.defect != "none":
            exclusions[self.target] = {"quiet":"short_hold", "g0":"unreleased", "status":"incomplete",
                                       "tokens":"short", "cap":"cap_not_reached",
                                       "mode":"wrong_mode", "loaded":"loaded"}[self.defect]
        if not self.inst:
            # RL-192b: the cold record lists the reason for a loaded stability member.
            exclusions = {key: rec[-1].removeprefix("not_qualified:") for key, rec in self.records.items()
                          if rec[-1] != "qualified"}
        stanza = (f"RESTRICTED-READ ruling=RL-900002 look={self.look} "
                  f"manifest_sha256={proof['manifest_sha256']} reader=research_lead")
        ruling_path = "authority/examples/invented-ruling.md"
        payload = (f"RL-900002. Invented cold decision for {self.look}.\n"
                   + wire(dict(bindings=proof, dropped=dropped, not_qualified=exclusions)).decode()
                   + stanza + "\n").encode()
        put(self.repo / ruling_path, payload)
        return dict(ruling="RL-900002", ruling_path=ruling_path, ruling_sha256=sha(payload),
                    bindings=proof, dropped=dropped, not_qualified=exclusions)

    def save_row(self):
        if getattr(self, "span_ledger", {}):
            self.row["spans"] = self.span_ledger
        if self.manifest_registration:
            self.reg = self.row["registration_commit"] = self.manifest_registration
            for span in self.row.get("spans", {}).values():
                span["registration_commit"] = self.reg
        return super().save_row()

    def drop(self, key, row):
        if self.scenario == "pending":
            row.clear()
            row.update(key=key, disposition="pending")
            return
        source = "receipt" if self.defect in ("span", "no_item_span", "wrong_span") else "queue"
        reason = "ended_without_member" if source == "receipt" else "queue_retired"
        witness_path = f"ops/drop-evidence/{source}.json"
        span = LOCATION[key][0]
        witness = (dict(span_id=span, closed=True, kit_id=key.split("/")[0], member_legs=[],
                        unrun=[key], kit_sha256=sha((self.repo / "kits" / (key.split("/")[0]+".json")).read_bytes()))
                   if source == "receipt" else dict(queue_id="invented-Q", final=True, unrun=[key]))
        if self.defect in ("wrong_span", "wrong_queue"):
            witness["unrun"] = ["f2-inst-03/L001"]
        declaration = dict(key=key, status="dropped", reason=reason, authority="lead")
        if self.defect != "no_witness":
            put(self.repo / witness_path, witness)
            declaration[source] = witness_path
        if self.defect not in ("no_item_span", "no_item_queue"):
            item_key = "f2-inst-03/L001" if self.defect == "wrong_item" else key
            put(self.repo / "RUN_STATE.md", typed_item(item_key, reason, witness_path, sha(wire(witness))))
            declaration["typed_item_ref"] = {"path": "RUN_STATE.md", "number": 900002}
        path = "drops/" + key + ".json"
        put(self.repo / path, declaration)
        row.clear()
        row.update(key=key, drop=path)

    def group_members(self):
        by_key = {r["key"]: r for r in self.rows}
        self.span_closes = {}
        for span, group in GROUPS.items():
            members = [key for key in group if key in self.records]
            if not members:
                continue
            first = self.records[members[0]][1].copy()
            first.update(span_id=span, legs=[key.split("/")[1] for key in members],
                         close_epoch_s=1800000000 + 1000 * list(GROUPS).index(span))
            if self.scenario == "digest" and self.target in members:
                first["kit_sha256"] = sha(b"invented different kit")
            root = "ops/" + span + "/"
            self.span_closes[span] = first["close_epoch_s"]
            check_digest = sha(("invented offload manifest for " + span).encode())
            put(self.repo / "checks" / (span + ".json"),
                dict(span_id=span, offload_manifest_sha256=check_digest))
            put(self.repo / (root + "runner_receipt.json"), first)
            issue = {k: first[k] for k in ("kit_id", "kit_sha256", "span_id", "attempt", "runner_pin", "legs")}
            put(self.repo / (root + "issue.json"), issue)
            for role in ("hand_table", "q1", "desk_final"):
                put(self.repo / (root + role + ".json"), dict(span_id=span, attempt=1, record=role, passed=True))
            for index, key in enumerate(members):
                refs = by_key[key]
                op, _, plan, status = self.records[key]
                old = (self.repo / refs["issue"]).parent
                kit = read(self.repo / "kits" / (key.split("/")[0] + ".json"))
                budget = kit["span_template"]["leg_budget_s"]
                exceeds = self.over if self.scenario == "wall" and key == self.target else index == 0
                op.update(loaded_flag=key == LOADED, wall_s=budget + (1 if exceeds else -1),
                          leg_budget_s=budget, over_time_budget=exceeds,
                          reference_source_leg_id=members[0].split("/")[1])
                if self.scenario == "wall" and key == self.target:
                    if self.defect == "quiet": op["quiet_spans_ns"] = [[0, 599_999_999_999]]
                    if self.defect == "g0": op["g0_outcome"] = "timeout"
                    if self.defect == "status": op["leg_status"] = "incomplete"
                    if self.defect == "tokens": op["decode_tokens"] -= 1
                    if self.defect == "cap": op["decode_cap_reached"] = False
                    if self.defect == "loaded": op["loaded_flag"] = True
                    if self.defect == "mode":
                        first["power_mode"] = "High Power"
                        put(self.repo / (root + "runner_receipt.json"), first)
                self.records[key] = op, first, plan, status
                refs.update(issue=root+"issue.json", receipt=root+"runner_receipt.json",
                            leg_record=root+"legs/"+op["leg_id"]+"/leg_record.json")
                for role in ("hand_table", "q1", "desk_final"):
                    refs[role] = root + role + ".json"
                put(self.repo / refs["leg_record"], op)
                shutil.rmtree(old)  # Only the superseded invented singleton in this private test Book.
        if self.scenario in ("no_receipt", "no_leg_record"):
            role = "receipt" if self.scenario == "no_receipt" else "leg_record"
            (self.repo / by_key[self.target][role]).unlink()
        if self.scenario in ("pending", "drop", "hide_member"):
            self.drop(self.target, by_key[self.target])
            if self.scenario == "pending":
                # Remove the uncommitted placeholder for this still-open key.
                (self.repo / ("drops/" + self.target + ".json")).unlink()
        if self.scenario in ("second_bundle", "concealed_second_bundle"):
            refs = by_key[self.target]
            old = (self.repo / refs["issue"]).parent
            new = old.with_name(old.name + "-attempt2")
            shutil.copytree(old, new)
            for path in new.glob("*.json"):
                obj = read(path)
                obj["attempt"] = 2
                put(path, obj)
            second = {name: path.replace(old.name + "/", new.name + "/") if name != "key" else path
                      for name, path in refs.items()}
            if self.scenario == "second_bundle":
                self.rows.append(second)


def stage(test, world, *, allowed=True, nodename=HOST, values=(UUID,)):
    with device(nodename, values, boundary=True):
        code, stdout, error, events = frozen.invoke(world, "stage1")
    test.assertEqual((code, stdout), (0 if allowed else 2, b""), error)
    test.assertFalse([e for e in events if e[0] in ("open", "reservation_attempt")], events)
    test.assertEqual(world.stage.is_file(), allowed)
    test.assertFalse(world.private.exists() or world.public.exists())
    return read(world.stage) if allowed else None


def at_reservation(test, world, *, reached, nodename=HOST, values=(UUID,), check_probe=False):
    with device(nodename, values, boundary=True):
        code, stdout, error, events = frozen.invoke(world, "stage2")
    test.assertEqual((code, stdout), (2, b""), error)
    test.assertFalse(any(k == "open" for k, _ in events))
    test.assertFalse(world.private.exists() or world.public.exists())
    attempts = [i for i, (k, _) in enumerate(events) if k == "reservation_attempt"]
    test.assertEqual(len(attempts), int(reached), events)
    if check_probe:
        reads = [i for i, event in enumerate(events) if event == ["device_query", "ioreg"]]
        test.assertTrue(reads, "stage 2 never sampled the invented IOPlatformUUID")
        if attempts:
            test.assertLess(reads[0], attempts[0])


def literal_status(test, row, prefix):
    value = row["disposition"]
    if prefix.endswith(":"):
        test.assertTrue(isinstance(value, str) and value.startswith(prefix) and value[len(prefix):].strip(), value)
    else:
        test.assertEqual(value, prefix)


class RL190(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.serial = 0

    def world(self, **kwargs):
        self.serial += 1
        return AsRun(self.base / f"book-{self.serial}", **kwargs)


def member(test, kind):
    w = test.world()
    doc = stage(test, w)
    test.assertEqual(set(doc["positions"]), set(KEYS))
    if kind == "qualified":
        for key in KEYS:
            if key != LOADED:
                literal_status(test, doc["positions"][key], "qualified")
    elif kind == "loaded":
        row = doc["positions"][LOADED]
        literal_status(test, row, "not_qualified:loaded")
        test.assertEqual(row["receipt"], next(r["receipt"] for r in w.rows if r["key"] == LOADED))
    elif kind == "count":
        test.assertEqual(doc["counts"], {"n_legs": 35})
    else:
        check_span_ids(test, doc)


def pending_refuses(test, world):
    # SQ2 specifies effects only. The diagnostic may identify an operational key.
    before = subprocess.check_output(["git", "-C", world.repo, "rev-parse", "HEAD"])
    with device(boundary=True):
        rc, _, _, events = frozen.invoke(world, "stage1")
    test.assertEqual(rc, 2)
    test.assertFalse([event for event in events if event[0] in ("open", "reservation_attempt")])
    test.assertFalse(world.stage.exists() or world.private.exists() or world.public.exists())
    test.assertEqual(subprocess.check_output(["git", "-C", world.repo, "rev-parse", "HEAD"]), before)
    test.assertFalse(frozen.git_ok(world.repo, "cat-file", "-e", "HEAD:" + str(world.stage.relative_to(world.repo))))


def roster_case(test, scenario, target, defect=None):
    w = test.world(scenario=scenario, target=target, defect=defect)
    if defect == "late_queue":
        test.assertFalse(frozen.git_ok(w.repo, "cat-file", "-e", w.receipts+":RUN_STATE.md"))
        test.assertTrue(frozen.git_ok(w.repo, "cat-file", "-e", "HEAD:RUN_STATE.md"))
    allowed = scenario == "drop" and defect in ("queue", "span", "late_queue")
    if scenario == "pending":
        pending_refuses(test, w)
        return
    if not allowed:
        stage(test, w, allowed=False)
        return
    doc = stage(test, w)
    test.assertEqual(set(doc["positions"]), set(KEYS))
    literal_status(test, doc["positions"][target],
                   "dropped:" + ("queue_retired" if defect != "span" else "ended_without_member"))
    test.assertEqual(doc["counts"]["n_legs"], 34)


def check_span_ids(test, doc):
    def strings(obj, path=()):
        if isinstance(obj, dict):
            for name, value in obj.items():
                yield from strings(value, path + (name,))
        elif isinstance(obj, str):
            yield path, obj
    rows = {key:dict(strings(row)) for key,row in doc["positions"].items()}
    test.assertTrue(any(all(rows[key].get(path) == span for key,(span, _) in LOCATION.items())
                        for path in rows[KEYS[0]]), "no common field identifies each authenticated span")


def numeric_paths(obj, path=()):
    if isinstance(obj, dict):
        for name, value in obj.items():
            yield from numeric_paths(value, path + (name,))
    elif type(obj) is int:
        yield path, obj


def index_map(test, doc):
    # Find an actual per-leg integer that encodes receipt order across ALL spans.
    # Neither the spelling nor zero/one origin is specified. Kit position, attempt
    # and bool cannot satisfy this signature. Use the SAME field/base for every row.
    positions = doc["positions"]
    values = {key: dict(numeric_paths(row)) for key, row in positions.items()}
    for path, base in values[KEYS[0]].items():
        if all(values[key].get(path) == base + LOCATION[key][1] for key in KEYS):
            return {key: values[key][path] - base for key in KEYS}
    test.fail("no consistently encoded per-leg integer index follows the actual receipt order")


def indices(test):
    doc = stage(test, test.world())
    test.assertEqual(index_map(test, doc), {key: LOCATION[key][1] for key in KEYS})


def time_pair(test, predicate):
    rows = []
    for exceeds in (False, True):
        world = test.world(scenario="wall", target=SOLO, defect=predicate, over=exceeds)
        doc = stage(test, world)
        row = doc["positions"][SOLO]
        rows.append((doc["counts"], row["disposition"]))
        with test.subTest(over_time_budget=exceeds):
            test.assertIs(row.get("over_time_budget"), exceeds,
                          f"{SOLO} requires a literal boolean equal to the operational wall comparison")
            literal_status(test, row, "qualified" if predicate == "none" else
                           "not_qualified:loaded" if predicate == "loaded" else "not_qualified:")
    test.assertEqual(rows[0], rows[1])
    test.assertEqual(rows[0][0]["n_legs"], 35 if predicate == "none" else 34)


def single_exclusion(test, predicate):
    w = test.world(scenario="wall", target=SOLO, defect=predicate)
    doc = stage(test, w)
    literal_status(test, doc["positions"][SOLO],
                   "not_qualified:loaded" if predicate == "loaded" else "not_qualified:")
    test.assertEqual(doc["counts"]["n_legs"], 34)
    test.assertEqual(doc["positions"][SOLO]["receipt"], next(r["receipt"] for r in w.rows if r["key"] == SOLO))


def wall_independent(test, predicate):
    # Independent of the missing flag. A paired wall measurement must leave
    # every disposition and the full counts unchanged, even for excluded legs.
    outputs = []
    for exceeds in (False, True):
        doc = stage(test, test.world(scenario="wall", target=SOLO, defect=predicate, over=exceeds))
        outputs.append((doc["counts"], {k: r["disposition"] for k, r in doc["positions"].items()}))
    test.assertEqual(*outputs)


def chronology(test, mode):
    w = test.world(late=True)
    reg, projection = w.reg, w.receipts
    test.assertTrue(frozen.git_ok(w.repo, "merge-base", "--is-ancestor", projection, reg))
    test.assertFalse(frozen.git_ok(w.repo, "cat-file", "-e", projection+":"+str(w.man.relative_to(w.repo))))
    stage(test, w)
    if mode == "sibling":
        tip = w.book.head
        w.book.head = projection
        sibling = w.book.seal("invented alternate registration with identical manifest bytes")
        w.book.head = tip
        w.manifest_registration = sibling
        w.row["registration_commit"] = sibling
    if mode == "uncommitted":
        w.row.update(status="stage1_committed", stage1_path=str(w.stage.relative_to(w.repo)),
                     stage1_sha256=sha(w.stage.read_bytes()))
        w.save_row()
        subprocess.run(["git", "-C", str(w.repo), "add", "--", "LOOKS.json", w.row["stage1_path"]], check=True)
        at_reservation(test, w, reached=False)
    w.bind()
    if mode == "sibling":
        test.assertFalse(frozen.git_ok(w.repo, "merge-base", "--is-ancestor", sibling, w.stage1_commit))
        frozen.merge_fixture(w.book, w.stage1_commit, sibling)
        w.book.seal("invented main after both commits")
    else:
        test.assertTrue(frozen.git_ok(w.repo, "merge-base", "--is-ancestor", reg, w.stage1_commit))
    at_reservation(test, w, reached=mode != "sibling")


def freeze_case(test, when):
    w = test.world(scenario="early_cold")
    cold = str(w.targets["cold"].relative_to(w.repo))
    freeze = str(w.targets["freeze"].relative_to(w.repo))
    def at(name):
        return json.loads(subprocess.check_output(["git", "-C", str(w.repo), "show", w.cold_commit+":"+name]))
    test.assertTrue(at(cold)["passed"])
    test.assertEqual(at(freeze)["twin_agrees"], "no")
    if when == "signed_early":
        stage(test, w)
        w.bind()
        at_reservation(test, w, reached=True)
        return
    if when == "reservation":
        stage(test, w)
    put(w.targets["freeze"], dict(w.freeze, twin_agrees="no"))
    w.row["input_hashes"][freeze] = sha(w.targets["freeze"].read_bytes())
    if when == "stage1":
        w.save_row()
        w.book.seal("invented ineffective freeze")
        stage(test, w, allowed=False)
    else:
        # Bind a matching synthetic census digest so stale bytes are not the refusal.
        doc = read(w.stage)
        doc["source_snapshot"]["input_hashes_sha256"] = sha(wire(w.row["input_hashes"]))
        put(w.stage, doc)
        w.bind()
        at_reservation(test, w, reached=False)


def host_id(test, tokens, expected):
    # RL-184 names this CLI. No assumption about the Python helper's name or module.
    script = frozen.ROOT / "scripts/cadence_look_run.py"
    test.assertTrue(script.is_file(), "the specified host-id command is absent from this checkout")
    probe = test.base / "device"
    put(probe / "sitecustomize.py", HARDWARE.encode())
    with device(HOSTNAME, tokens):
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(probe), str(frozen.ROOT),
                                                          os.environ.get("PYTHONPATH", ""))))
        result = subprocess.run([sys.executable, "-B", str(script), "host-id"], cwd=test.base,
                                env=env, capture_output=True, check=False)
    if expected:
        test.assertEqual((result.returncode, result.stderr), (0, b""))
        test.assertIn(result.stdout, (HOST.encode(), (HOST+"\n").encode()))
    else:
        test.assertNotEqual(result.returncode, 0)
        test.assertNotRegex(result.stdout, rb"hw1:[0-9a-f]{64}")


def host_gate(test, look, mode):
    w = test.world(look=look)
    doc = stage(test, w)
    named = {"hostname": HOSTNAME, "boot_uuid": BOOT_UUID,
             "kit_commit": read(w.repo / "kits/f2-inst-01.json")["frozen"]["commit"]}.get(mode, HOST)
    if named != HOST:
        # Model a committed but malformed row. Keep the copy and stage digest
        # consistent so an unrelated hash/attestation failure cannot reject it.
        w.row["execution_host"] = named
        attestation = read(w.targets["copy"])
        attestation["execution_host"] = named
        put(w.targets["copy"], attestation)
        name = str(w.targets["copy"].relative_to(w.repo))
        w.row["input_hashes"][name] = sha(w.targets["copy"].read_bytes())
        doc["source_snapshot"]["input_hashes_sha256"] = sha(wire(w.row["input_hashes"]))
        put(w.stage, doc)
    w.bind()
    if mode in ("matching_board", "renamed"):
        at_reservation(test, w, reached=True, nodename=HOSTNAME if mode == "matching_board" else "new-name.invalid",
                       check_probe=True)
    elif mode == "different_board":
        # Legacy hostname equality would accept this even though the board changed.
        at_reservation(test, w, reached=False, values=(OTHER_UUID,), nodename=HOST, check_probe=True)
    else:
        # All three can be hostnames too. Equality with gethostname cannot be decisive.
        at_reservation(test, w, reached=False, nodename=named)


def stable_wall(test, over):
    original = AsRun.named
    observed = {}
    def insert(world, name, path, doc):
        if name == "host_chain":
            key = "f2-stab-15/L001"
            refs = next(r for r in world.rows if r["key"] == key)
            member_path = world.repo / refs["leg_record"]
            op = read(member_path)
            budget = read(world.repo / "kits/f2-stab-15.json")["span_template"]["leg_budget_s"]
            op.update(wall_s=budget + (1 if over else -1), loaded_flag=False,
                      leg_budget_s=budget, over_time_budget=over)
            put(member_path, op)
            observed["key"] = key
        return original(world, name, path, doc)
    with patch.object(AsRun, "named", insert):
        world = test.world(look=STAB2)
    row = stage(test, world)["positions"][observed["key"]]
    literal_status(test, row, "qualified")
    test.assertIs(row.get("over_time_budget"), over)


def own_reference(test, key=SOLO):
    # Use the candidate's own census detail and score path. Only one invented
    # member needs a numeric trace. Inspect the return in memory, before any writer.
    w = test.world()
    # Obtain detail and score inside the same isolated fake-device process as the CLI.
    program = r'''
from pathlib import Path
import sys
import test_desc_looks_acceptance as f
from joulewise.cadence_looks import description as d
root, look, key, folder, out = sys.argv[1:]
snap = d.Snapshot(Path(root), look, "stage1")
doc, qualified = d.census(snap)
paths = {name:Path(folder)/name for name in d.VALUE_FILES}
result = d.score(snap, {key:paths}, {key:qualified[key]}, lambda:None)
def references(obj):
    if isinstance(obj, dict):
        return {k: references(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [references(v) for v in obj]
    return obj if isinstance(obj, (str, bool, int)) else None
f.put(Path(out), references({name: rows[key] for name, rows in result.items() if key in rows}))
'''
    source = GROUPS[LOCATION[key][0]][0]  # Actual first member of this receipt.
    folder = test.base / "invented-trace"
    frozen.traces(folder, 1, 0)
    probe = test.base / "device"
    put(probe / "sitecustomize.py", HARDWARE.encode())
    output = test.base / "invented-print.json"
    with device():
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(probe), str(frozen.HERE), str(frozen.ROOT),
                                                          os.environ.get("PYTHONPATH", ""))))
        r = subprocess.run([sys.executable, "-B", "-c", program, str(w.repo), w.look, key,
                            str(folder), str(output)], env=env, cwd=test.base, capture_output=True)
    test.assertEqual(r.returncode, 0, r.stderr)
    def reference_facts(obj):
        if isinstance(obj, list):
            for item in obj:
                yield from reference_facts(item)
        if isinstance(obj, dict):
            for name, value in obj.items():
                word = name.lower()
                if "ref" in word or "g0" in word:
                    if type(value) is bool and ("own" in word or "captur" in word):
                        yield value == (source == key)
                    if isinstance(value, str):
                        if value in ("own", "self"):
                            yield source == key
                        elif value in ("shared", "inherited", "borrowed"):
                            yield source != key
                        elif value.startswith("L") or "/L" in value:
                            yield value in (source, source.split("/")[1])
                yield from reference_facts(value)
    facts = list(reference_facts(read(output)))
    test.assertTrue(facts, "per-leg prints omit the reference attribution")
    test.assertTrue(all(facts), f"{key} must carry the reference captured by {source}")



def schema_case(test, variation):
    from jsonschema.validators import validator_for
    dropped = variation == "drop"
    w = test.world(scenario="drop" if dropped else "ordinary", defect="queue" if dropped else None)
    doc = stage(test, w)
    schema = read(w.targets["pin_stage1_schema"])
    cls = validator_for(schema)
    cls.check_schema(schema)
    # Validate positions using the shipped schema; summaries have their own representation.
    schema_for_positions = dict(schema["properties"]["positions"])
    schema_for_positions["$defs"] = schema["$defs"]
    validator = cls(schema_for_positions)
    key = SOLO if dropped else LOADED if variation in ("loaded", "legacy_member") else KEYS[0]
    row = dict(doc["positions"][key])
    if dropped:
        row["disposition"] = "dropped:queue_retired"
    elif variation in ("loaded", "legacy_member"):
        row["disposition"] = "not_qualified:loaded"
    elif variation != "pending":
        row["over_time_budget"] = True
    errors = list(validator.iter_errors({key: row}))
    test.assertFalse(errors, errors[0].message if errors else "")
    if variation in ("flag", "loaded", "drop"):
        return
    if variation == "pending":
        row["disposition"] = "pending"
    elif variation == "missing_flag":
        row.pop("over_time_budget")
    elif variation == "legacy_member":
        row["disposition"] = "loaded"
    else:
        row["over_time_budget"] = {"integer": 1, "text": "false", "null": None}[variation]
    test.assertFalse(validator.is_valid({key: row}), f"schema admitted {variation} in committed output")


# These oracles consume normalized observations of a public record. No witness generated
# here is offered as an actual ruling, independent Check, or detached host rehearsal.
# Test desks can reuse them with their own public-evidence adapter.
def ledger_agrees(rows, expected):
    return set(rows) == set(expected) and all(
        all(rows[span].get(role) == value for role, value in witnesses.items())
        for span, witnesses in expected.items())


def ledger_vector(test, mode):
    w = test.world(late=True)
    expected = {}
    for span, group in GROUPS.items():
        path = next(r["receipt"] for r in w.rows if r["key"] == group[0])
        def projection_at(name):
            return json.loads(subprocess.check_output(["git", "-C", str(w.repo), "show", w.receipts+":"+name]))
        close = projection_at(path)["close_epoch_s"]
        mark = projection_at("checks/" + span + ".json")["offload_manifest_sha256"]
        expected[span] = dict(close_epoch_s=close, projection_commit=w.receipts,
                              registration_commit=w.reg, offload_manifest_sha256=mark)
    observations = read(w.ledger)["looks"][0]["spans"]
    other, span = tuple(GROUPS)[:2]
    row = observations[span]
    if mode == "missing_span":
        del observations[span]
    elif mode == "swapped_commits":
        row["registration_commit"], row["projection_commit"] = row["projection_commit"], row["registration_commit"]
    elif mode == "commit_time_as_close":
        row["close_epoch_s"] = int(subprocess.check_output(
            ["git", "-C", str(w.repo), "show", "-s", "--format=%ct", w.reg]))
        test.assertNotEqual(row["close_epoch_s"], expected[span]["close_epoch_s"])
    elif mode == "other_check":
        row["offload_manifest_sha256"] = expected[other]["offload_manifest_sha256"]
    elif mode != "complete":
        del row[mode]
    test.assertEqual(ledger_agrees(observations, expected), mode == "complete")


def multiple_projections(test, collapse):
    # The first and second span's blind projections land in different commits.
    # Either can be part of a later common snapshot without losing its own origin.
    book = frozen.Book(test.base / "span-ledger-book")
    expected = {}
    for number, span in enumerate(tuple(GROUPS)[:2], 1):
        close = 1799000000 + 1000 * number
        mark = sha(("independent invented Check " + span).encode())
        put(book.path / "checks" / span, {"offload_manifest_sha256": mark})
        put(book.path / "projection" / span, {"close_epoch_s": close})
        commit = book.seal("invented projection for " + span)
        expected[span] = dict(close_epoch_s=close, projection_commit=commit, offload_manifest_sha256=mark)
    put(book.path / "final-manifest.json", {"look_id": INST})
    registration = book.seal("invented final registration")
    first, second = expected
    for row in expected.values():
        row["registration_commit"] = registration
    rows = {k: v.copy() for k, v in expected.items()}
    if collapse:
        rows[first]["projection_commit"] = rows[second]["projection_commit"]
    test.assertNotEqual(expected[first]["projection_commit"], expected[second]["projection_commit"])
    put(book.path / "LOOKS.json", {"spans": rows})
    book.seal("invented span ledger")
    test.assertEqual(ledger_agrees(main_record(book, "LOOKS.json")["spans"], expected), not collapse)


COLD_BINDS = ("manifest_sha256", "executor_revision", "schema_revisions", "public_inventory",
              "restricted_inventory", "synthetic_hand_tables", "row7", "host_rehearsal", "once_only")


def cold_record_agrees(record, ruling_id, bindings, dropped, excluded):
    return (record.get("ruling") == ruling_id and record.get("bindings") == bindings
            and record.get("dropped") == dropped and record.get("not_qualified") == excluded)


def cold_vector(test, mode):
    w = test.world(scenario="drop", defect="queue")
    frozen_packet = read(w.targets["cold"])
    ruling = (w.repo / frozen_packet["ruling_path"]).read_bytes()
    test.assertEqual(sha(ruling), frozen_packet["ruling_sha256"])
    # Derive the expected witnesses independently from the public fixture sources.
    # A changed byte in a referenced artefact invalidates the otherwise complete record.
    manifest = read(w.man)
    inventory = manifest["outputs"]
    pins = manifest["code_pins"]
    evidence = dict(manifest_sha256=sha(w.man.read_bytes()),
                    executor_revision=sha((w.repo / pins["reader"]["path"]).read_bytes()),
                    schema_revisions={k: sha((w.repo / v["path"]).read_bytes()) for k, v in pins.items()
                                      if "schema" in k},
                    public_inventory={k: v for k, v in inventory.items() if k != "custody_names"},
                    restricted_inventory=inventory["custody_names"])
    for role in ("synthetic_hand_tables", "row7", "host_rehearsal", "once_only"):
        path = "authority/examples/" + role + ".json"
        evidence[role] = dict(path=path, sha256=sha((w.repo / path).read_bytes()))
    signed = json.loads(ruling.splitlines()[1])
    test.assertEqual(signed["bindings"], evidence)
    test.assertEqual(set(evidence), set(COLD_BINDS))
    if mode.startswith("omit_"):
        del frozen_packet["bindings"][mode[5:]]
    elif mode.startswith("stale_"):
        frozen_packet["bindings"][mode[6:]] = sha(b"other revision")
    elif mode == "unnamed":
        del frozen_packet["ruling"]
    elif mode == "collapsed_lists":
        frozen_packet["dropped"].update(frozen_packet.pop("not_qualified"))
    elif mode == "wrong_reason":
        frozen_packet["not_qualified"][LOADED] = "short"
    elif mode == "wrong_id":
        frozen_packet["dropped"] = {KEYS[-1]: "queue_retired"}
    accepted = cold_record_agrees(frozen_packet, "RL-900002", evidence, {SOLO: "queue_retired"},
                                  {LOADED: "loaded"})
    test.assertEqual(accepted, mode == "one_instrument_pass")


def stanza_authorizes(ruling_text, ruling_id, look, digest, on_main, effective):
    line = f"RESTRICTED-READ ruling={ruling_id} look={look} manifest_sha256={digest} reader=research_lead"
    return on_main and effective and line in ruling_text.splitlines()


def main_record(book, path):
    result = subprocess.run(["git", "-C", str(book.path), "show", "refs/remotes/origin/main:"+path],
                            capture_output=True, check=False)
    return json.loads(result.stdout) if result.returncode == 0 else None


def stanza_vector(test, mode):
    digest, ruling = sha(b"invented final manifest"), "RL-900002"
    line = f"RESTRICTED-READ ruling={ruling} look={INST} manifest_sha256={digest} reader=research_lead"
    signed = "Invented cold pass.\n" + line + "\nEnd.\n"
    other_document = ""
    if mode == "elsewhere":
        other_document, signed = signed, "Invented cold pass.\n"
    for token, replacement in (("prefix", ("RESTRICTED", "example RESTRICTED")),
                               ("suffix", ("research_lead", "research_lead extra")),
                               ("reader", ("research_lead", "ordinary_seat")),
                               ("look", (INST, STAB1)), ("hash", (digest, sha(b"other manifest"))),
                               ("ruling", (ruling, "RL-900003"))):
        if mode == token:
            signed = signed.replace(*replacement)
    if mode == "elsewhere":
        test.assertIn(line, other_document)
    # Exercise the difference between a file on disk, a commit on a sibling,
    # another look's success and a committed publication for this look.
    book = frozen.Book(test.base / "public-record-book")
    public = "publications/" + INST + "/PUBLIC.json"
    freeze = "authority/effective-freeze.json"
    put(book.path / freeze, {"effective": mode not in ("no_freeze", "neither")})
    initial = book.seal("invented public preconditions")
    if mode not in ("no_main", "neither"):
        path = public.replace(INST, STAB1) if mode == "peer_published" else public
        put(book.path / path, {"look_id": STAB1 if mode == "peer_published" else INST,
                               "manifest_sha256": digest})
        if mode != "working_only":
            book.seal("invented success publication")
            if mode == "sibling_only":
                side = book.head
                (book.path / path).unlink()
                book.head = initial
                put(book.path / "independent-main-change", b"fixture only\n")
                main = book.seal("invented independent main without publication")
                test.assertFalse(frozen.git_ok(book.path, "merge-base", "--is-ancestor", side, main))
                test.assertFalse(frozen.git_ok(book.path, "merge-base", "--is-ancestor", main, side))
    published = main_record(book, public)
    on_main = bool(published and published["look_id"] == INST and published["manifest_sha256"] == digest)
    result = stanza_authorizes(signed, ruling, INST, digest, on_main, main_record(book, freeze)["effective"])
    test.assertEqual(result, mode == "effective")


def rehearsal_revision(pins):
    # A comparison of path-to-content identities. The digest is a fixture representation.
    paths = {pin["path"]: pin["sha256"] for pin in pins.values() if pin["path"].endswith(".py")}
    if not paths:
        raise ValueError("no pinned executor code")
    return sha(wire(paths))


def rehearsal_covers(evidence, host, revision):
    return (evidence.get("host") == host and evidence.get("revision") == revision and
            evidence.get("passed") is True and evidence.get("literal_directory") == "RESTRICTED")


def rehearsal_vector(test, mode):
    # A documentary coverage relation. Which command, when and on which machine
    # the lead actually rehearsed remains outside an agent's synthetic suite.
    w = test.world()
    packet = read(w.targets["cold"])
    witness = packet["bindings"]["host_rehearsal"]
    actual = (w.repo / witness["path"]).read_bytes()
    test.assertEqual(sha(actual), witness["sha256"])
    manifest = read(w.man)
    paths = {p["path"] for p in manifest["code_pins"].values() if p["path"].endswith(".py")}
    revision = sha(wire({path:sha(subprocess.check_output(["git", "-C", w.repo, "show", w.reg+":"+path]))
                         for path in paths}))
    evidence = dict(json.loads(actual), originating_look=INST)
    requested = dict(host=HOST, revision=revision, look=STAB1)
    if mode == "other_host":
        requested["host"] = "hw1:" + sha(b"other invented host")
    elif mode == "other_revision":
        requested["revision"] = sha(b"other invented revision")
    elif mode == "surrogate_directory":
        evidence["literal_directory"] = "synthetic-alias"
    test.assertEqual(rehearsal_covers(evidence, requested["host"], requested["revision"]),
                     mode == "another_look")


def register(family, name, run, *args):
    method_name = f"test_{family}_{name}"
    if hasattr(RL190, method_name):
        raise ValueError(method_name)
    def case(self):
        run(self, *args)
    case.__name__ = method_name
    setattr(RL190, method_name, case)


for kind in ("qualified", "loaded", "count"):
    register("disposition", kind, member, kind)
for key in KEYS:
    register("disposition", "pending_" + key.replace("-", "_").replace("/", "_"),
             roster_case, "pending", key)
for evidence in ("queue", "span", "late_queue", "no_item_span", "no_item_queue", "no_witness",
                 "wrong_item", "wrong_queue", "wrong_span"):
    register("disposition", "drop_" + evidence, roster_case, "drop", SOLO, evidence)
for problem in ("missing", "duplicate", "duplicate_masks_missing", "hide_member", "second_bundle", "concealed_second_bundle", "no_receipt", "no_leg_record"):
    register("disposition", problem, roster_case, problem, SOLO)
register("layout", "as_run_ids_36", member, "spans")
register("layout", "as_run_indices_36", indices)
def all_flags(test):
    w = test.world()
    doc = stage(test, w)
    for key in KEYS:
        with test.subTest(key=key):
            test.assertIs(doc["positions"][key].get("over_time_budget"), LOCATION[key][1] == 0)
register("wall", "all_36", all_flags)
register("layout", "own_reference_L006", own_reference)
for predicate in ("none", "loaded", "status", "g0", "quiet", "tokens", "cap", "mode"):
    if predicate != "none":
        register("disposition", "single_gate_" + predicate, single_exclusion, predicate)
    register("wall", "flag_" + predicate, time_pair, predicate)
    register("wall", "invariance_" + predicate, wall_independent, predicate)
for over in (True, False):
    register("wall", "stab15_" + str(over).lower(), stable_wall, over)
for span, keys in GROUPS.items():
    register("ancestry", "kit_sha_" + span.replace("-", "_"), roster_case, "digest", keys[0])
for mode in ("after", "sibling", "uncommitted"):
    register("ancestry", mode, chronology, mode)
for mode in ("signed_early", "stage1", "reservation"):
    register("freeze", mode, freeze_case, mode)
for mode, values in (("lower", (UUID,)), ("mixed", (UUID.swapcase(),)), ("missing", ()),
                     ("malformed", ("not-a-uuid",)), ("two", (UUID, OTHER_UUID))):
    register("host", "cli_" + mode, host_id, values, mode in ("lower", "mixed"))
for look in frozen.IDS:
    modes = ("matching_board", "renamed", "different_board")
    if look == INST:
        modes += ("hostname", "boot_uuid", "kit_commit")
    for mode in modes:
        register("host", look.replace("-", "_") + "_" + mode, host_gate, look, mode)
for variation in ("loaded", "drop", "flag", "pending", "text", "integer", "null", "missing_flag", "legacy_member"):
    register("schema", variation, schema_case, variation)
for mode in ("complete", "missing_span", "swapped_commits", "commit_time_as_close", "other_check",
             "close_epoch_s", "projection_commit", "registration_commit", "offload_manifest_sha256"):
    register("ledgerRecord", mode, ledger_vector, mode)
register("ledgerRecord", "distinct_projection_commits", multiple_projections, False)
register("ledgerRecord", "global_projection_substitution", multiple_projections, True)
for mode in ("one_instrument_pass", "unnamed", "collapsed_lists", "wrong_reason", "wrong_id",
             *("omit_"+k for k in COLD_BINDS), *("stale_"+k for k in COLD_BINDS)):
    register("coldRecord", mode, cold_vector, mode)
for mode in ("effective", "elsewhere", "prefix", "suffix", "reader", "look", "hash", "ruling",
             "no_main", "no_freeze", "neither", "working_only", "sibling_only", "peer_published"):
    register("readRecord", mode, stanza_vector, mode)
for mode in ("another_look", "other_host", "other_revision", "surrogate_directory"):
    register("rehearsalRecord", mode, rehearsal_vector, mode)


if __name__ == "__main__":
    unittest.main()
