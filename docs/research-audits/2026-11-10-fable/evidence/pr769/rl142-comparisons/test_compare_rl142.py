"""Synthetic tests for compare_rl142.py (RL-142 §2 item 5). No real run output is read.

    python3 -I -B -m unittest test_compare_rl142   (from /Volumes/JW-EXT/scratch, under AIR-QUIET.lock)
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
TOOL = HERE / "compare_rl142.py"
OLD = "90e22603593926e5654a8e72f095b6e600b5b85009a5a76d2e7f68431fb85759"
NEW = "4a9f594471652581737b6cd02bd2922592f2e7cf9d575a164adb10162a5211ea"
PROG = "scripts/independent_recompute_b6.py"
KA = "lines/whole_machine/qwen3-1p7b/decode/mean_j"
KB = "lines/whole_machine/qwen3-8b/prefill-p2048/mean_j"
OTHER = "reported/qwen3-1p7b/decode/per_token_j"
SESSIONS = ("r1-alpha", "r3-alpha", "r1-beta")
SECRETS = ("987654.321", "SECRET-VALUE-Q7", "secret_flag_code_zz", "SECRET-STDERR-TEXT", "SECRET-DETAIL-9",
           "4242.4242", "SECRET-UNOWNED-NEW")
TMP_ROOT = Path(os.environ.get("RL142_TEST_TMP", "/Volumes/JW-EXT/scratch/rl142-comparer-tmp"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(obj):
    return (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()


def restricted_doc(program, fixed, stopped, inputs_sha):
    pack_key = {"ALPHA": KA, "BETA": KB}
    values, inclusive, side, bq = {}, {}, {}, {}
    for pack, key in pack_key.items():
        n = 4 if fixed else 3
        mean = 987654.321 if fixed else 12.5
        row = {"n": n, "mean": mean, "sd": 1.5 if fixed else 1.25, "block5_included": fixed,
               "noncomputable_sessions": [], "sd_label": None}
        values[pack] = {"label": "between-session summary", "n_counting": 3,
                        "values": {key: row, OTHER: {"n": 3, "mean": 2.0, "sd": 0.5, "block5_included": True,
                                                     "noncomputable_sessions": [], "sd_label": None}}}
        inclusive[pack] = {"label": "including sessions that did not count", "added_sessions": [],
                           "values": {key: dict(row)}}
        side[pack] = {key: {"block5": 4242.4242 if fixed else None,
                            "block5_label": None if fixed else "block 5: not computed",
                            "sessions": {s: 12.0 for s in SESSIONS},
                            "delta": -1.0 if fixed else None,
                            "session_deltas": {s: 0.5 for s in SESSIONS} if fixed else {}}}
        for g in ("summary", "inclusive"):
            for stat in ("n", "mean", "sd"):
                bq[g + "/" + pack + "/" + key + "/" + stat] = row[stat]
        bq["side_by_side/" + pack + "/" + key + "/delta"] = side[pack][key]["delta"]
    failures = [] if fixed else ["section10:side_by_side/ALPHA/" + KA + "/delta", "comparator:side_by_side:__block__:x"]
    classes = {"side_by_side": {"compared": 4, "passed": 4 if fixed else 0, "failed": 0 if fixed else 4,
                                "unmatched": 0, "both_null": 0, "pass": fixed, "first_program_only": 0},
               "summary": {"compared": 12, "passed": 12, "failed": 0, "unmatched": 0, "both_null": 0, "pass": True,
                           "first_program_only": 0}}
    flags = [{"code": "neg8_reference_lost", "session": "r1-beta", "pack": "BETA", "scope": "session",
              "detail": {}, "stops_comparison": False}]
    if not fixed:
        flags += [{"code": "option_c_disagrees", "session": s, "pack": "ALPHA", "scope": "block",
                   "detail": list(failures) + ["SECRET-DETAIL-9"], "stops_comparison": True} for s in SESSIONS]
    flags += [{"code": "secret_flag_code_zz", "session": "r1-alpha", "pack": "ALPHA", "scope": "x",
               "detail": {"note": "SECRET-VALUE-Q7"}, "stops_comparison": False}]
    return {"schema": "joulewise.b6_recompute.v1", "mode": "BLOCK", "program_sha256": program,
            "b5_program_sha256": "d" * 64,
            "sessions": {s: {"pack": "ALPHA", "quantities": {KA: 12.0, OTHER: "SECRET-VALUE-Q7"}} for s in SESSIONS},
            "block": {"between_session": values, "flagged_inclusive": inclusive, "side_by_side": side,
                      "block6_only": {"ALPHA": {KA: {"n": 3, "mean": 12.5, "sd": 1.25}}},
                      "option_c": {"pass": fixed, "families": {"section10": 40}, "failures": failures,
                                   "first_program_only": [],
                                   "comparator": {"schema": "c", "pass": fixed, "recompute_stopped": False,
                                                  "classes": classes}}},
            "comparison_table": {"block": {"quantities": bq}},
            "flags": flags, "comparison_stopped": stopped, "closed": True, "block5_input": True,
            "inputs": {"host": "Air", "run_inputs_sha256": inputs_sha}}


def build(root, name, program, fixed, stopped, stem, inputs_name="run-inputs-block-2.json", b5_expected=44,
          checkout="/W/run", mutate=None):
    out = Path(root) / name
    out.mkdir(parents=True)
    inputs_sha = sha(inputs_name.encode())
    r = restricted_doc(program, fixed, stopped, inputs_sha)
    if mutate:
        mutate(r)
    rbytes = dump(r)
    rs = sha(rbytes)
    nflags = len(r["flags"])
    pub = {"schema": "p", "mode": "BLOCK", "comparison_stopped": stopped, "flag_count": nflags,
           "sessions": {s: {"flag_counts": {"neg8_reference_lost": 1 if s == "r1-beta" else 0},
                            "restricted_flag_count": sum(1 for f in r["flags"] if f["session"] == s
                                                         and f["code"] != "neg8_reference_lost")}
                        for s in SESSIONS},
           "restricted_sha256": rs}
    pbytes = dump(pub)
    included = 22 if fixed else 20
    struct = {"schema": "joulewise.b6_structure_probe.v1", "stage": "dry_run",
              "identity": {"comparison_stopped": stopped, "closed": True},
              "option_c": {"pass": fixed, "failure_count": len(r["block"]["option_c"]["failures"]),
                           "comparator": {"pass": fixed, "classes": copy.deepcopy(r["block"]["option_c"]["comparator"]["classes"])}},
              "term7": {"per_class": {c: {"compared": v["compared"], "both_null": v["both_null"],
                                          "passed": v["passed"], "listed": v["compared"]}
                                      for c, v in r["block"]["option_c"]["comparator"]["classes"].items()}},
              "names": {"failures": list(r["block"]["option_c"]["failures"]), "first_program_only": []},
              "flags": [{"code": f["code"], "session": f["session"], "pack": f["pack"], "scope": f["scope"],
                         "stops_comparison": f["stops_comparison"]} for f in r["flags"]],
              "block5_included": {"ALPHA": included, "BETA": included, "GAMMA": 4},
              "public": {"comparison_stopped": stopped},
              "checks": {"comparison_stopped": {"result": "departs" if stopped else "ok", "observed": stopped},
                         "option_c_pass": {"result": "ok" if fixed else "departs", "observed": fixed},
                         "failures_empty": {"result": "ok" if fixed else "departs",
                                            "count": len(r["block"]["option_c"]["failures"])},
                         "compared_classes_clean": {"result": "ok" if fixed else "departs",
                                                    "names_of_classes": [] if fixed else ["side_by_side"]},
                         "block5_included": {"result": "ok", "observed": 2 * included + 4, "expected": b5_expected,
                                             "by_pack": {"ALPHA": included, "BETA": included, "GAMMA": 4},
                                             "expected_by_pack": {"ALPHA": included, "BETA": included, "GAMMA": 4}}},
              "digests": {"program_sha256": program, "restricted_file": rs, "public_file": sha(pbytes),
                          "public_restricted_sha256": rs, "run_inputs_sha256": inputs_sha,
                          "inputs_file": inputs_sha}}
    stdout = ("recompute sessions=3 flags=" + str(nflags) + " comparison_stopped=" + json.dumps(stopped)
              + " restricted_sha256=" + rs + "\n").encode()
    stderr = ("warning SECRET-STDERR-TEXT " + stem + "\n").encode()
    argv = [sys.executable, "-B", checkout + "/" + PROG, "block", "--session", "/custody/r1-alpha/archive",
            "--block5", "/b5/recompute.json", "--closed", "--restricted-out", str(out / "restricted.json"),
            "--public-out", str(out / "public.json"), "--inputs", "/RUN/" + inputs_name, "--inputs-sha256",
            inputs_sha]
    closure = {PROG: program, "scripts/independent_recompute_b5.py": "b" * 64}
    record = {"schema": "joulewise.b6_real_run.v1", "stem": stem, "commit": "c" * 40 if program == OLD else "e" * 40,
              "checkout": checkout, "closure_before": closure, "closure_after": dict(closure),
              "closure_unchanged": True, "argv": argv, "argv_sha256": sha(json.dumps(argv).encode()),
              "timed_argv": ["/usr/bin/time", "-l", sys.executable, "-I", "-B", "/T/b6_real_run.py", "--exec-child",
                             str(out)],
              "start_time_ns": 1000 + len(stem), "end_time_ns": 9000 + len(stem), "wall_s": 322.5 + len(stem),
              "limit_s": 6400.0, "exit_code": 3 if stopped else 0, "time_wrapper_exit": 0,
              "peak_rss": 123456 + len(stem), "peak_rss_units": "bytes", "python": "3.13.0",
              "outputs_sha256": {"stdout": sha(stdout), "stderr": sha(stderr), "restricted": rs,
                                 "public": sha(pbytes)},
              "record_path": str(out / "record.json"), "status": "hold" if stopped else "complete",
              "class": None, "code": "comparison_stopped" if stopped else None, "frames": []}
    files = {"restricted.json": rbytes, "public.json": pbytes, "structure.json": dump(struct),
             "record.json": dump(record), "child-argv.json": dump({"schema": "s", "checkout": checkout, "argv": argv}),
             "stdout": stdout, "stderr": stderr, "time": ("real " + stem + " SECRET-STDERR-TEXT\n").encode(),
             "process.json": dump({"exit_code": 3 if stopped else 0, "peak_rss": len(stem), "user_s": 1.5}),
             "samples.jsonl": (json.dumps({"elapsed_s": 60.0 + len(stem)}) + "\n").encode()}
    for fname, data in files.items():
        (out / fname).write_bytes(data)
    return out


def edit_json(path, fn):
    doc = json.loads(path.read_bytes())
    fn(doc)
    path.write_bytes(dump(doc))


class Base(unittest.TestCase):
    def setUp(self):
        TMP_ROOT.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(dir=TMP_ROOT)
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_tool(self, mode, old, new, *extra, out_name="result.json"):
        out = self.root / out_name
        proc = subprocess.run([sys.executable, "-I", "-B", str(TOOL), "--mode", mode, "--old", str(old),
                               "--new", str(new), "--out", str(out), *extra], capture_output=True, text=True)
        result = json.loads(out.read_text()) if out.exists() else None
        return proc, result, (out.read_text() if out.exists() else "")

    def gate_pair(self):
        old = build(self.root, "gate-2", OLD, True, False, "gate-2", b5_expected=48)
        new = build(self.root, "gate-r2", NEW, True, False, "gate-r2", b5_expected=48)
        return old, new

    def dry_pair(self, mutate_new=None):
        old = build(self.root, "dry", OLD, False, True, "dry", b5_expected=44)
        new = build(self.root, "dry-r2", NEW, True, False, "dry-r2", b5_expected=48, mutate=mutate_new)
        return old, new

    def unowned(self, result):
        return [(r["file"], r["path"]) for r in result["paths"] if r["rule"] == "UNOWNED"]


class ModeA(Base):
    def test_a_clean(self):
        old, new = self.gate_pair()
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(self.unowned(result), [])
        for rule in ("R-PH-1", "R-PH-2", "R-DG-1", "R-B-1", "R-B-2", "R-B-3", "R-B-4", "B-FILE"):
            self.assertIn(rule, result["counts"]["by_rule"], rule)
        self.assertIn("verdict PASS", proc.stdout)
        self.assertEqual(result["comparer_sha256"], sha(TOOL.read_bytes()))

    def test_a_extra_difference_holds(self):
        old, new = self.gate_pair()
        edit_json(new / "restricted.json", lambda d: d["sessions"]["r1-alpha"]["quantities"].__setitem__(KA, 13.0))
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertIn(("restricted.json", "/sessions/r1-alpha/quantities/" + KA.replace("/", "~1")),
                      self.unowned(result))
        self.assertIn("verdict HOLD", proc.stdout)

    def test_a_does_not_allow_b_classes(self):
        old = build(self.root, "gate-2", OLD, False, True, "gate-2")
        new = build(self.root, "gate-r2", NEW, True, False, "gate-r2")
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertTrue(any(p == "/comparison_stopped" for f, p in self.unowned(result) if f == "restricted.json"))

    def test_a_program_hash_must_be_the_pair(self):
        old = build(self.root, "gate-2", "f" * 64, True, False, "gate-2")
        new = build(self.root, "gate-r2", NEW, True, False, "gate-r2")
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("restricted.json", "/program_sha256"), self.unowned(result))

    def test_a_unbound_digest_holds(self):
        old, new = self.gate_pair()
        edit_json(new / "public.json", lambda d: d.__setitem__("restricted_sha256", "0" * 64))
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("public.json", "/restricted_sha256"), self.unowned(result))

    def test_a_argv_beyond_out_dir_holds_and_inputs_rerun(self):
        old = build(self.root, "gate-2", OLD, True, False, "gate-2")
        new = build(self.root, "gate-r2", NEW, True, False, "gate-r2", inputs_name="run-inputs-gate-3.json")
        proc, result, _ = self.run_tool("a", old, new, out_name="r1.json")
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("child-argv.json", "/argv/14"), self.unowned(result))
        proc, result, _ = self.run_tool("a", old, new, "--inputs-rerun", out_name="r2.json")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("R-IN-1", result["counts"]["by_rule"])

    def test_a_missing_file_holds(self):
        old, new = self.gate_pair()
        (new / "samples.jsonl").unlink()
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("samples.jsonl", "/"), self.unowned(result))


class ModeB(Base):
    ALL_B = ("R-PH-1", "R-PH-2", "R-DG-1", "R-B-1", "R-B-3", "R-B-4", "R-B1-SUM", "R-B1-INC", "R-B1-SBS", "R-BQ",
             "R-CT-1", "R-CT-2", "R-CT-3", "R-FL", "R-OCP", "R-CS", "R-CS-X", "R-OCD", "R-OCD-N", "R-B5N", "B-FILE")

    def test_b_every_allowed_class(self):
        old, new = self.dry_pair()
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(self.unowned(result), [])
        for rule in self.ALL_B:
            self.assertIn(rule, result["counts"]["by_rule"], rule)

    def test_b_term7_side_by_side_passed_follows_comparator(self):
        old, new = self.dry_pair()
        proc, result, _ = self.run_tool("b", old, new)
        rows = [r for r in result["paths"] if r["rule"] == "R-CT-3"]
        self.assertEqual([(r["file"], r["path"]) for r in rows],
                         [("structure.json", "/term7/per_class/side_by_side/passed")])

    def test_b_term7_not_following_comparator_holds(self):
        old, new = self.dry_pair()
        edit_json(new / "structure.json",
                  lambda d: d["term7"]["per_class"]["side_by_side"].__setitem__("passed", 3))
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertEqual(self.unowned(result), [("structure.json", "/term7/per_class/side_by_side/passed")])

    def test_b_term7_other_field_or_class_holds(self):
        old, new = self.dry_pair()
        edit_json(new / "structure.json", lambda d: d["term7"]["per_class"]["summary"].__setitem__("passed", 11))
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("structure.json", "/term7/per_class/summary/passed"), self.unowned(result))

    def test_b_prefix_dir_substitutes_cleanly(self):
        # old dir "dry" is a path prefix of new dir "dry-r2" under one root (C1)
        old, new = self.dry_pair()
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        paths = {(r["file"], r["path"]): r["rule"] for r in result["paths"]}
        for key in (("record.json", "/record_path"), ("record.json", "/timed_argv/7"),
                    ("child-argv.json", "/argv/10"), ("child-argv.json", "/argv/12")):
            self.assertEqual(paths.get(key), "R-B-4", key)
        self.assertFalse([k for k in paths if k[0] in ("record.json", "child-argv.json")
                          and paths[k] == "UNOWNED"])

    def test_b_summary_class_tally_change_holds(self):
        def bump(r):
            r["block"]["option_c"]["comparator"]["classes"]["summary"]["passed"] = 11
        old, new = self.dry_pair(mutate_new=bump)
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertIn(("restricted.json", "/block/option_c/comparator/classes/summary/passed"),
                      self.unowned(result))
        self.assertIn(("structure.json", "/option_c/comparator/classes/summary/passed"), self.unowned(result))

    def test_b_one_unowned_path(self):
        old, new = self.dry_pair(mutate_new=lambda r: r["block"]["block6_only"]["ALPHA"][KA].__setitem__("n", 4))
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertEqual(self.unowned(result),
                         [("restricted.json", "/block/block6_only/ALPHA/" + KA.replace("/", "~1") + "/n")])

    def test_b_other_key_same_field_holds(self):
        old, new = self.dry_pair(mutate_new=lambda r: r["block"]["between_session"]["ALPHA"]["values"][OTHER]
                                 .__setitem__("n", 4))
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3)

    def test_b_flag_count_not_explained_holds(self):
        old, new = self.dry_pair()
        edit_json(new / "public.json", lambda d: d.__setitem__("flag_count", d["flag_count"] + 1))
        # keep the record's public digest bound so only the count is at issue
        edit_json(new / "record.json", lambda d: d["outputs_sha256"].__setitem__(
            "public", sha((new / "public.json").read_bytes())))
        proc, result, _ = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3)
        self.assertIn(("public.json", "/flag_count"), self.unowned(result))

    def test_secret_values_never_emitted(self):
        def plant(r):
            r["sessions"]["r1-alpha"]["quantities"][OTHER] = "SECRET-UNOWNED-NEW"
            # a difference under the restricted flag code, so its ordinal label is exercised
            for f in r["flags"]:
                if f["code"] == "secret_flag_code_zz":
                    f["scope"] = "SECRET-UNOWNED-NEW"
        old, new = self.dry_pair(mutate_new=plant)
        proc, result, text = self.run_tool("b", old, new)
        self.assertEqual(proc.returncode, 3)
        blob = proc.stdout + proc.stderr + text
        for secret in SECRETS:
            self.assertNotIn(secret, blob, secret)
        self.assertIn("<restricted-code-", blob)
        # the old files really held the secrets
        self.assertIn(b"987654.321", (new / "restricted.json").read_bytes())
        self.assertIn(b"secret_flag_code_zz", (old / "restricted.json").read_bytes())


class Usage(Base):
    def test_parse_error_and_out_exists(self):
        old, new = self.gate_pair()
        (new / "restricted.json").write_bytes(b"{not json SECRET-VALUE-Q7")
        proc, result, _ = self.run_tool("a", old, new)
        self.assertEqual(proc.returncode, 2)
        self.assertIsNone(result)
        self.assertNotIn("SECRET-VALUE-Q7", proc.stdout + proc.stderr)
        (self.root / "taken.json").write_text("{}")
        proc, _, _ = self.run_tool("a", old, old, out_name="taken.json")
        self.assertEqual(proc.returncode, 2)
        proc = subprocess.run([sys.executable, "-I", "-B", str(TOOL), "--mode", "c"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
