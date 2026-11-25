"""The interim look's two-stage CLI on a synthetic custody copy (RL-166 Q8, Q15). Synthetic only: the custody
layout is written by scripts/cadence_look_synth.py, with energy files (power_trace.csv, meter streams, a level-E
file) planted beside everything stage 1 reads. Stage 1 must open none of them."""
from __future__ import annotations

import builtins
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import plistlib
import re
import shutil
import statistics
import struct
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

try:  # the fit needs numpy; the dependency-free core shards run without it (CI's look-fit job installs it)
    from joulewise.cadence_looks import fit_interim as F
    from tests.cadence import look_layout_fixture as LF
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as synth
    from joulewise.cadence_looks import manifest as M
except ModuleNotFoundError as _exc:  # pragma: no cover
    if _exc.name != "numpy":
        raise
    _NUMPY_MISSING = str(_exc)
else:
    _NUMPY_MISSING = None


def load_tests(loader, tests, pattern):
    """Without numpy the module loads and reports one skip, so shard discovery does not error."""
    if _NUMPY_MISSING is None:
        return tests

    class NumpyMissing(unittest.TestCase):
        @unittest.skip("numpy is not installed; this module runs in CI's look-fit job")
        def test_needs_numpy(self):
            pass
    return loader.loadTestsFromTestCase(NumpyMissing)


STEP3_CANDIDATES = [os.environ.get("JW_STEP3_MODULE"), "/Volumes/JW-EXT/scratch/step3/step3_energy_ratios.py"]


def step3_path():
    """The committed step 3 module if this branch has it, else a byte-identical copy named by the environment."""
    spec = importlib.util.find_spec("joulewise.cadence_looks.step3_energy_ratios")
    if spec is not None:
        return spec.origin
    for p in STEP3_CANDIDATES:
        if p and os.path.isfile(p) and R.sha256_file(p) == R.STEP3_SHA256:
            return p
    return None


def rj(p):
    with open(p) as f:
        return json.load(f)


def wb(p, data):
    with open(p, "wb" if isinstance(data, bytes) else "w") as f:
        f.write(data)


ENERGY_MARKERS = ("power_trace.csv", "segment_energy.json")


class AstraPreResponse(unittest.TestCase):
    def test_singular_onset_keeps_rank_refusal_before_responses(self):
        li, _, _ = synth.build("noisy", seed=3)
        for leg in li["legs"]:
            if leg["turn"]:
                for reading in leg["turn"]["journal"]:
                    if reading["tf08_c"] is not None:
                        reading["fan_rpm"] = 100 * reading["tf08_c"]
        with tempfile.TemporaryDirectory(prefix="singular-onset-cli-") as tmp:
            root = Path(tmp)
            ip, s1p, ep, op = [root / name for name in ("input.json", "stage1.json", "responses.json", "fit.json")]
            wb(ip, synth.dump(li))
            # Any attempt to decode this sentinel as level E fails; the audit hook
            # also proves it is never opened. Only generated predictors enter stage 1.
            wb(ep, "synthetic responses must remain unopened")
            rc, _, err = run_cli(["stage1", "--input", str(ip), "--out", str(s1p)])
            self.assertEqual(rc, 0, err)
            self.assertEqual(rj(s1p)["onset"]["status"], "not_estimable")
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", str(s1p), "--stage1-sha256", R.sha256_file(s1p),
                                      "--energy", str(ep), "--out", str(op)])
            self.assertEqual(rc, 2, err)
            self.assertIn("rank deficient", err)
            self.assertNotIn(str(ep), opened)
            self.assertFalse(op.exists())

    def test_receipt_epoch_overrules_the_roster_date_at_the_la_boundary(self):
        # 05:00 UTC on Nov 15 is still Nov 14 in Los Angeles.
        entry = {"span_id": "dev-01-s01", "block_id": "dev-01", "role": "fit"}
        receipt = {"started": {"epoch_s": 1_794_718_800}, "roster": [], "sensors": {}}
        with unittest.mock.patch.object(R, "_json", return_value=receipt), \
             unittest.mock.patch.object(R.TF, "file_sha256", return_value="0" * 64), \
             unittest.mock.patch.object(R, "span_meter", return_value=(None, None)), \
             unittest.mock.patch.object(R.I34, "keys", return_value=()), \
             unittest.mock.patch.object(R.I34, "judge_span", return_value=({}, None, None)), \
             unittest.mock.patch.object(R.M, "nonenergy_files", return_value={}), \
             unittest.mock.patch.object(R.M, "native_pm_files", return_value={}):
            for date in ("2026-11-20", "2026-11-99", "2026-11-15"):
                with self.subTest(date=date), self.assertRaisesRegex(F.LookInputError, "t0_local_date"):
                    R.read_span(Path("synthetic"), dict(entry, t0_local_date=date), {}, ())
            span, _ = R.read_span(Path("synthetic"), dict(entry, t0_local_date="2026-11-14"), {}, ())
            self.assertEqual(span["t0_local_date"], "2026-11-14")
            midnight = 1_794_729_600.0
            for epoch, date in ((math.nextafter(midnight, -math.inf), "2026-11-14"), (midnight, "2026-11-15")):
                receipt["started"]["epoch_s"] = epoch
                span, _ = R.read_span(Path("synthetic"), dict(entry, t0_local_date=date), {}, ())
                self.assertEqual(span["t0_local_date"], date)

    def test_dependent_full_design_refuses_before_opening_responses(self):
        li, _, _ = synth.build("noisy")
        for leg in li["legs"]:
            if leg["turn"]:
                for reading in leg["turn"]["journal"]:
                    if reading["tf08_c"] is not None:
                        reading["fan_rpm"] = 100 * reading["tf08_c"]
        stage1 = F.stage1(li, "0" * 64)
        self.assertFalse(any(t["trips"] for t in stage1["tripwires"].values() if isinstance(t, dict)))
        self.assertTrue(stage1["active_readings"]["fan_rpm"]["active"])
        self.assertTrue(stage1["active_readings"]["tf08_c"]["active"])
        self.assert_rank_refusal_before_responses(stage1, "full fit.*rank deficient")

    def test_dependent_fold_refuses_before_opening_responses(self):
        li, _, _ = synth.build("noisy")
        stage1 = F.stage1(li, "0" * 64)
        day = stage1["roster"]["fit_days"][0]
        # The full design retains independent readings on day one. Training without
        # that day makes the fan and temperature columns collinear.
        for leg in stage1["legs"]:
            if leg["in_energy_fit"] and leg["day"] != day:
                leg["start"]["z"][1] = 100 * leg["start"]["z"][0]
        self.assert_rank_refusal_before_responses(stage1, f"{day}.*rank deficient")

    def assert_rank_refusal_before_responses(self, stage1, reason):
        sha = hashlib.sha256(F.dump(stage1)).hexdigest()
        args = R.argparse.Namespace(stage1_sha256=sha, allow_draft=True, level_e=True, ledger_ref=None)

        class Layout:                       # the look's fixed files: stage1.json, and responses that must stay shut
            def read(self, key):
                if key != "stage1":
                    raise AssertionError("opened responses")
                return F.dump(stage1)
        # The frozen test copy has no Git history. Supply the draft commit at the same seam as the mocked ledger.
        with unittest.mock.patch.object(R, "_VERIFIED", [({}, None)]), \
             unittest.mock.patch.object(R, "layout_of", return_value=Layout()), \
             unittest.mock.patch.object(R, "_json", side_effect=[{}, AssertionError("opened responses")]) as read, \
             unittest.mock.patch.object(R.M, "_git", return_value=(0, b"0" * 40 + b"\n", b"")) as git, \
             unittest.mock.patch.object(R, "draft_ledger_check"), \
             unittest.mock.patch.object(R, "stage2_energy_preflight"):
            with self.assertRaisesRegex(F.LookInputError, reason):
                R.cmd_stage2(args)
            git.assert_called_once_with(R.ROOT, "rev-parse", "HEAD")
            read.assert_called_once()

class PrefixPublication(unittest.TestCase):
    """Equal-day prefix arithmetic through the synthetic private writer."""

    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory(prefix="rl175-noisy-cli-")
        cls.addClassCleanup(tmp.cleanup)
        cls.root = Path(tmp.name)
        tokens = {}
        cls.li, energy, cls.truth = synth.build("noisy", tokens=tokens)
        cls.custody = cls.root / "custody"
        paths = synth.write_custody(cls.custody, cls.li, energy, tokens)
        from tests.cadence import look_minirepo as mr
        owner = unittest.TestCase()
        cls.addClassCleanup(owner.doCleanups)
        mini = mr.mini_repo(owner)
        roster_sha, verdicts_sha = (R.sha256_file(paths[name]) for name in ("roster.json", "rules_3_4.json"))
        mr.commit(mini, roster_sha256=roster_sha, verdicts_sha256=verdicts_sha)
        cls.s1p, cls.fitp, cls.cop = [cls.root / name for name in ("stage1.json", "fit.json", "freeze2.json")]
        commands = [
            ["stage1", "--roster", paths["roster.json"], "--custody", str(cls.custody),
             "--rules-3-4", paths["rules_3_4.json"], "--out", str(cls.s1p)],
            ["stage2", "--stage1", str(cls.s1p), "--stage1-sha256", "", "--custody", str(cls.custody),
             "--out", str(cls.fitp), "--coefficients-out", str(cls.cop)],
        ]
        for argv in commands:
            if argv[0] == "stage2":
                h = R.sha256_file(cls.s1p)
                argv[argv.index("--stage1-sha256") + 1] = h
                mr.commit(mini, stage1_sha256=h, roster_sha256=roster_sha, verdicts_sha256=verdicts_sha)
            rc, _, err = _cli_subprocess([*argv, "--manifest", mini / mr.MANIFEST], repo=mini)
            if rc:
                raise AssertionError(f"{argv[0]} failed: {err} {LAST_RUN.get('private_stderr')}")
        cls.s1, cls.fit, cls.co = (rj(p) for p in (cls.s1p, cls.fitp, cls.cop))
        cls.legs = {leg["leg_key"]: leg for leg in cls.li["legs"]}
        refs = {sp["span_id"]: sp["soak_reference_tv0h_c"] for sp in cls.li["spans"]}
        cls.predictions = {
            leg["leg_key"]: F.predict(cls.co, cls.legs[leg["leg_key"]], refs[leg["span_id"]], held_out_day=leg["day"])
            for leg in cls.s1["legs"] if leg["in_energy_fit"]}
        cls.energy, _ = R.read_segment_energy(cls.s1, LF.span_dirs(cls.custody, None))

    def test_unequal_day_bias_estimate_and_interval_from_cli_responses(self):
        for ch in F.CHANNELS:
            for label, plen in F.PREFIX.items():
                pairs = []
                for leg in self.s1["legs"]:
                    key = leg["leg_key"]
                    if key not in self.predictions or leg["decode_tokens"] <= plen:
                        continue
                    pred = self.predictions[key]["channels"][ch]
                    response = self.energy["legs"][key][ch]
                    short = sum(y for y, seg in zip(response["segments"], leg["segments"])
                                if seg["kind"] == "prefill" or seg["block"] < plen // F.BLOCK)
                    short += response["prefix_tails"][str(plen)]
                    pairs.append((leg["day"], sum(response["segments"]) - pred["total"],
                                  short - pred["prefix_tails"][str(plen)]))
                sd_l, sd_s = (statistics.stdev(p[j] for p in pairs) for j in (1, 2))
                by_day = {}
                for day, long, short in pairs:
                    by_day.setdefault(day, []).append(long / sd_l - short / sd_s)
                self.assertGreater(len({len(v) for v in by_day.values()}), 1)
                means = [statistics.mean(v) for v in by_day.values()]
                estimate = statistics.mean(means)
                half = F.t_quantile(0.95, len(means) - 1) * statistics.stdev(means) / math.sqrt(len(means))
                got = self.fit["channels"][ch]["prefix_bias"][label]
                # Same responses, independent sums: allow 4096 accumulated binary64
                # rounding units per pair (the generator's decode cap), scaled to
                # the standardized residuals. This is an arithmetic, not a noise bar.
                tol = 4096 * len(pairs) * math.ulp(max(1.0, *(abs(x) for v in by_day.values() for x in v)))
                self.assertAlmostEqual(got["estimate"], estimate, delta=tol)
                for actual, expected in zip(got["ci90"], (estimate - half, estimate + half)):
                    self.assertAlmostEqual(actual, expected, delta=tol)
                self.assertEqual((got["n_pairs"], got["n_days"]), (len(pairs), len(means)))


class Staging(unittest.TestCase):
    def pack(self, root, files=None, changed=False):
        import tarfile
        files = files or {"nested/opaque.bin": b"synthetic\x00\xff", "raw.jsonl": b"no fields decoded\n"}
        sid = "dev-01-s01"
        manifest = root / "SHA256SUMS"
        manifest.write_bytes("".join(f"{hashlib.sha256(data).hexdigest()}  ./{name}\n"
                                     for name, data in sorted(files.items())).encode())
        archive = root / "span.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            for i, (name, data) in enumerate(files.items()):
                if changed and i == 0:
                    data = bytes([data[0] ^ 1]) + data[1:]
                info = tarfile.TarInfo(sid + "/" + name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        marker = root / "marker.json"
        marker.write_text(json.dumps({"schema": "joulewise.span_offload_marker.v1", "span_name": sid,
                                     "provider_confirmed": True, "manifest_files": len(files),
                                     "manifest_sha256": R.sha256_file(manifest),
                                     "archive_sha256": R.sha256_file(archive)}))
        return sid, archive, manifest, marker

    @staticmethod
    def stage(args, staging_root, manifest_sha256=None):
        """Stage 1's launcher of the staging process, against the SHA256SUMS digest a pin list would carry."""
        return R.stage_archive(*args, staging_root, manifest_sha256=manifest_sha256 or R.sha256_file(args[2]))

    def test_verifies_every_file_and_records_hash_chain(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root)
            record = self.stage(args, root / "stage")
            self.assertEqual(record, {"span_id": args[0], "archive_sha256": R.sha256_file(args[1]),
                                     "manifest_sha256": R.sha256_file(args[2]),
                                     "marker_sha256": R.sha256_file(args[3]), "files_verified": 2})
            self.assertEqual((root / "stage" / args[0] / "nested/opaque.bin").read_bytes(), b"synthetic\x00\xff")
            with self.assertRaisesRegex(F.LookInputError, "already exists"):
                self.stage(args, root / "stage")

    def test_one_changed_byte_refuses_before_publishing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root, changed=True)  # archive hash is valid; a file differs by exactly one byte
            with self.assertRaisesRegex(F.LookInputError, "staged file sha256 differs"):
                self.stage(args, root / "stage")
            self.assertEqual(list((root / "stage").iterdir()), [])

    def test_manifest_and_archive_must_match_marker(self):
        for target in (1, 2):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                args = self.pack(root)
                path = args[target]
                path.write_bytes(path.read_bytes() + b"x")
                with self.assertRaisesRegex(F.LookInputError, "does not match"):
                    self.stage(args, root / "stage")
                self.assertFalse((root / "stage" / args[0]).exists())

    def test_unsafe_paths_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root, {"../escape": b"synthetic"})
            with self.assertRaisesRegex(F.LookInputError, "unsafe"):
                self.stage(args, root / "stage")
            self.assertFalse((root / "escape").exists())

    def test_a_sums_file_that_is_not_the_pinned_offload_manifest_refuses_before_anything_else_is_read(self):
        """Audit 1 on 2082c1a51: staging ran before the pin list was admitted. It now follows the pins: the
        SHA256SUMS must be the span's pinned offload manifest, and that is the first thing the staging process
        checks, before the marker, the archive or the staging root."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root)
            for label, pinned in (("another span's manifest", hashlib.sha256(b"another manifest").hexdigest()),
                                  ("one digit off", ("0" if R.sha256_file(args[2])[0] != "0" else "1")
                                   + R.sha256_file(args[2])[1:])):
                with self.subTest(label), self.assertRaisesRegex(F.LookInputError, "not the span's pinned offload manifest"):
                    self.stage(args, root / "stage", pinned)
                self.assertFalse((root / "stage").exists())               # not even the staging root was made
            os.chmod(args[1], 0)                      # and neither the archive nor the marker was needed to refuse
            args[3].unlink()
            try:
                with self.assertRaisesRegex(F.LookInputError, "not the span's pinned offload manifest"):
                    self.stage(args, root / "stage", "0" * 64)
            finally:
                os.chmod(args[1], 0o600)
            for bad in (None, "", "0" * 63, "g" * 64):
                with self.subTest(pinned=bad), self.assertRaisesRegex(F.LookInputError, "no pinned offload manifest digest"):
                    R.stage_archive(*args, root / "stage", manifest_sha256=bad)

    def test_the_stage_s_own_process_opens_no_archive_and_writes_no_member(self):
        """RL-179 F-12 as RL-194a keeps it: stage 1 opens and hashes no energy file. The archive holds the span's
        traces and meter streams, so the process that reads it is the staging process, never the stage."""
        import sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root, self.span_files())
            opened, recording = [], [True]

            def hook(event, hook_args):
                if recording[0] and event == "open" and hook_args and isinstance(hook_args[0], (str, bytes, os.PathLike)):
                    opened.append(os.path.realpath(os.fsdecode(hook_args[0])))
            sys.addaudithook(hook)
            try:
                record = self.stage(args, root / "stage")
            finally:
                recording[0] = False
            self.assertEqual(record["files_verified"], len(self.span_files()))
            staged = os.path.realpath(root / "stage")
            self.assertTrue(all((root / "stage" / args[0] / name).is_file() for name in self.span_files()))
            self.assertNotIn(os.path.realpath(args[1]), opened)                          # the archive
            self.assertFalse([path for path in opened if path == staged or path.startswith(staged + os.sep)])
            self.assertFalse([path for path in opened if Path(path).name in {Path(n).name for n in self.PROTECTED}])

    def test_the_staging_process_holds_no_decoder_and_imports_no_look_code(self):
        import ast
        source = (REPO / "scripts/cadence_look_stage_archive.py").read_text(encoding="utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").split(".")[0])
        self.assertEqual(imported, {"hashlib", "json", "os", "pathlib", "re", "sys", "tarfile", "tempfile"})

    def test_the_staging_process_creates_its_result_and_never_replaces_a_file(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root)
            taken = root / "PUBLIC.json"
            taken.write_bytes(b"kept\n")
            done = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_stage_archive.py"),
                                   "--span-id", args[0], "--archive", str(args[1]), "--manifest", str(args[2]),
                                   "--marker", str(args[3]), "--manifest-sha256", "0" * 64,
                                   "--staging-root", str(root / "stage"), "--out", str(taken)], capture_output=True)
            self.assertEqual((done.returncode, done.stdout, done.stderr), (2, b"", b""))
            self.assertEqual(taken.read_bytes(), b"kept\n")


    PROTECTED = ("legs/L001/runtime/run/power_trace.csv", "legs/L001/runtime/run/raw/powermetrics.plist",
                 "legs/L001/runtime/run/rich_telemetry.jsonl", "hazards/meter/stream-0001.jsonl")
    OPERATIONAL = ("runner_receipt.json", "soak/soak_reference.json", "legs/L001/leg_record.json",
                   "legs/L001/leg_summary.json", "legs/L001/runtime/run/config.json",
                   "legs/L001/runtime/run/events.jsonl", "legs/L001/runtime/run/outputs/align_turns.jsonl",
                   "legs/L001/runtime/run/outputs/align_thermal.jsonl")

    def span_files(self):
        return {**{name: b"{}\n" for name in self.OPERATIONAL},
                **{name: b"synthetic " + name.encode() for name in self.PROTECTED}, "notes/readme.txt": b"other\n"}

    def test_each_member_is_hashed_as_it_is_written_and_never_opened_again(self):
        """Audit 1 H1: staging re-opened every expanded trace, telemetry and meter file to hash it. The digest now
        comes from the bytes as they are written; RL-194 makes stage 1's pin check the first read of the copy."""
        import sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            args = self.pack(root, self.span_files())
            opened, recording = [], [True]

            def hook(event, hook_args):
                if recording[0] and event == "open" and hook_args and isinstance(hook_args[0], (str, bytes, os.PathLike)):
                    opened.append((os.fsdecode(hook_args[0]), hook_args[1]))
            from scripts import cadence_look_stage_archive as stager      # the staging process's own code, in-process
            sys.addaudithook(hook)
            try:
                record = stager.stage(*args, root / "stage", R.sha256_file(args[2]))
            finally:
                recording[0] = False
            self.assertEqual(record["files_verified"], len(self.span_files()))
            protected = {Path(n).name for n in self.PROTECTED}
            modes = [mode for path, mode in opened if Path(path).name in protected]
            self.assertEqual(len(modes), len(self.PROTECTED))            # each written once...
            self.assertTrue(all("x" in str(mode) for mode in modes), modes)   # ...and never opened to be read

    def test_the_operational_classification_names_the_look_s_operational_sources_only(self):
        """manifest.is_operational_path: the receipt, soak reference, leg records and summaries and bundle journals."""
        for name in self.OPERATIONAL:
            with self.subTest(name=name):
                self.assertTrue(M.is_operational_path(name))
        for name in (*self.PROTECTED, "notes/readme.txt", "legs/L001/runtime.rejected1/run/power_trace.csv",
                     "legs/L001/runtime/run/raw/powermetrics.plist", "hazards/meter/stream-0001.jsonl",
                     "legs/L001/runtime/run/outputs/power_trace.csv", "runner_receipt.json.bak"):
            with self.subTest(name=name):
                self.assertFalse(M.is_operational_path(name))

    def test_the_operational_classification_covers_what_the_manifest_reads_from_a_span(self):
        with tempfile.TemporaryDirectory() as td:
            sdir = Path(td)
            for name in self.OPERATIONAL:
                path = sdir / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}")
            (sdir / "runner_receipt.json").write_text(json.dumps({"roster": ["L001"]}))
            (sdir / "legs/L001/leg_record.json").write_text(json.dumps({"result": {"bundle": "run"}}))
            for rel in M.operational_paths(sdir):
                with self.subTest(rel=rel):
                    self.assertTrue(M.is_operational_path(rel), rel)


class _Custody:
    tmp = None

    @classmethod
    def get(cls):
        if cls.tmp is None or not os.path.isdir(cls.tmp):     # another module's teardown may have removed it
            cls._r = None
            cls.tmp = tempfile.mkdtemp(prefix="jw-look-run-")
            cls.tokens = {}
            cls.li, cls.en, cls.tr = synth.build("exact", tokens=cls.tokens)
            cls.paths = synth.write_custody(os.path.join(cls.tmp, "custody"), cls.li, cls.en, cls.tokens)
            cls.root = Path(cls.tmp) / "custody"
            # a level-E decoy beside the custody, as the twin comparison would have it
            with open(cls.root / "segment_energy.json", "wb") as f:
                f.write(synth.dump(cls.en))
        return cls

    @classmethod
    def read_r(cls):
        """Level R as stage 1 reads it from the custody copy (custody digests and trace clauses filled in)."""
        if getattr(cls, "_r", None) is None:
            cls._r = R.read_look_input(rj(cls.paths["roster.json"]), LF.span_dirs(cls.root, None),
                                       rj(cls.paths["rules_3_4.json"]))
        return copy.deepcopy(cls._r)

    @classmethod
    def s1_custody(cls):
        """Stage 1's output on the custody-read level R (every energy-fit leg carries its trace clauses)."""
        li = cls.read_r()
        return F.stage1(li, hashlib.sha256(synth.dump(li)).hexdigest())


def tearDownModule():
    """Remove the shared custody copy and the pin directory; the helpers recreate them on next use, so a module that
    imports these helpers (tests/cadence/test_time_fields.py) runs before or after this one."""
    if _Custody.tmp:
        shutil.rmtree(_Custody.tmp, ignore_errors=True)
    _Custody.tmp = None
    _DEFAULT_MANIFEST.clear()
    shutil.rmtree(_PIN_DIR, ignore_errors=True)


@contextlib.contextmanager
def spy_opens():
    opened = []
    real_open, real_io_open, real_os_open = builtins.open, io.open, os.open

    def rec(fn):
        def wrapper(file, *a, **k):
            if isinstance(file, (str, bytes, os.PathLike)):
                opened.append(os.fsdecode(file))
            return fn(file, *a, **k)
        return wrapper
    _SPIES.append(opened)
    try:
        with unittest.mock.patch.object(builtins, "open", rec(real_open)), \
                unittest.mock.patch.object(io, "open", rec(real_io_open)), \
                unittest.mock.patch.object(os, "open", rec(real_os_open)):
            yield opened
    finally:
        _SPIES.remove(opened)


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "docs/process/cadence/looks/lm-interim-01.json"
_PIN_DIR = os.path.realpath(tempfile.mkdtemp(prefix="jw-look-pins-"))      # no link on the way (audit 3, P1)


def _repin(node):
    """Every {path, sha256} pin re-pointed at the file's current hash (the mechanism under test is the check,
    not the manifest builder's pins, which follow this branch's head)."""
    if isinstance(node, dict):
        if isinstance(node.get("path"), str) and "sha256" in node and (REPO / node["path"]).is_file():
            node["sha256"] = R.sha256_file(REPO / node["path"])
        for v in node.values():
            _repin(v)
    elif isinstance(node, list):
        for v in node:
            _repin(v)
    return node


def pinned_manifest(mutate=None):
    _pin_dir()
    doc = _repin(rj(MANIFEST))
    if mutate:
        mutate(doc)
    path = os.path.join(_PIN_DIR, f"manifest-{len(os.listdir(_PIN_DIR))}.json")
    wb(path, json.dumps(doc))
    return path


def looks_file(stage1_sha256, status="stage1_committed", verdicts_sha256="3" * 64):
    _pin_dir()
    path = os.path.join(_PIN_DIR, f"looks-{len(os.listdir(_PIN_DIR))}.json")
    wb(path, json.dumps({"schema": "joulewise.cadence_look_ledger.v1", "looks": [
        {"look_id": "lm-interim-01", "manifest_path": "docs/process/cadence/looks/lm-interim-01.json",
         "sha256": "1" * 64, "status": status, "roster_sha256": "2" * 64, "stage1_sha256": stage1_sha256,
         "verdicts_sha256": verdicts_sha256}]}))
    return path


_DEFAULT_MANIFEST = []


def copy_bytecode_fixture(root):
    from tests.cadence import look_minirepo as mr

    for directory in ("joulewise", "scripts", "configs/align/v4", "docs/process/cadence/looks", "docs/research"):
        if (REPO / directory).is_dir():
            shutil.copytree(REPO / directory, root / directory, ignore=shutil.ignore_patterns("__pycache__"))
    mr.copy_missing_fixture_sources(root)


def placed_manifest_bytes(argv):
    """The bytes of the manifest the harness names to the executor for ``argv`` (its root and pins set)."""
    from tests.cadence import look_layout_fixture as layout_fixture
    argv = list(argv)
    if "--manifest" not in argv:
        if not _DEFAULT_MANIFEST:
            _DEFAULT_MANIFEST.append(pinned_manifest())
        argv += ["--manifest", _DEFAULT_MANIFEST[0]]
    placed = layout_fixture.place(argv, repo=REPO)
    return (json.dumps(placed.manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def run_cli(argv, trap=False, mock_stage2=False, extra=None):
    """The CLI with a draft manifest whose pins match this tree, and, for stage 2, a LOOKS.json that names the
    stage-1 hash, unless the test passes its own."""
    argv = list(argv)
    if "--manifest" not in argv:
        if not _DEFAULT_MANIFEST:
            _DEFAULT_MANIFEST.append(pinned_manifest())
        argv += ["--manifest", _DEFAULT_MANIFEST[0], "--allow-draft"]
    if argv[0] == "stage2" and "--looks" not in argv:
        argv += ["--looks", looks_file(argv[argv.index("--stage1-sha256") + 1])]
    return _cli_subprocess(argv, trap=trap, mock_stage2=mock_stage2, extra=extra)


# The CLI runs in its own `python -I -B` process, from the repository root, so its unpinned-module guard sees only
# what the CLI itself loads (a test process has loaded other repository modules). The harness lives OUTSIDE the
# repository, so it is never a loaded repository file; it can install an open() audit hook, an energy-decode trap
# and a stage-2 stub for the tests that need them, then calls the CLI's main().
_HARNESS = os.path.join(_PIN_DIR, "cli_harness.py")
_HARNESS_SRC = r'''
import json, os, re, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
sys.pycache_prefix = tempfile.mkdtemp(prefix="jw-harness-pyc-")   # as the CLI does: no cached bytecode is read
opts = json.loads(sys.argv[1]); argv = sys.argv[2:]
sys.path.insert(0, opts["repo"])
opened = []
frames = []
reservation_attempts = twin_launches = 0
if opts.get("spy") or opts.get("twin_path"):
    def _hook(event, args):
        global reservation_attempts, twin_launches
        if opts.get("twin_path"):
            if event == "os.mkdir" and os.path.basename(os.fsdecode(args[0])) == "RESTRICTED":
                reservation_attempts += 1
            # the twin is launched through its pin-checking wrapper (RL-194 condition 4); either path counts
            if event == "subprocess.Popen" and isinstance(args[1], (list, tuple)) and (
                    opts["twin_path"] in args[1]
                    or any(str(word).endswith("scripts/cadence_interim_twin_pins.py") for word in args[1])):
                twin_launches += 1
        # RL-194: a roster file is read from disk once, by the pin check, and parsed from those bytes. What the
        # tests observe is what is parsed: a read served from the verified bytes counts as an open by its caller,
        # and the pin check's own read of every file does not.
        if event in ("open", "joulewise.custody_pins.read") and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = os.fsdecode(args[0])
            f, who, pin_check = sys._getframe(1), None, False   # the innermost repository frame that asked
            while f is not None:
                fn = f.f_code.co_filename
                if fn.startswith(opts["repo"] + os.sep):
                    who = os.path.relpath(fn, opts["repo"])
                    if who != "joulewise/cadence_looks/custody_pins.py":
                        break
                    pin_check, who = pin_check or event == "open", None
                f = f.f_back
            if not pin_check:
                opened.append(path)
                frames.append([path, who])
    sys.addaudithook(_hook)
if opts.get("trap"):
    import plistlib
    _real = json.loads
    def _loads(s, *a, **k):
        text = s.decode() if isinstance(s, (bytes, bytearray)) else s
        if re.search(r'"gpu_(energy|power)":\s*[-0-9]', text) or re.search(r'"p":\s*"[0-9a-f]', text) \
                or re.search(r'"k"\s*:\s*"[bhte]"', text):
            raise AssertionError("an energy-bearing line was parsed")     # no meter line, header and trailer included
        return _real(s, *a, **k)
    json.loads = _loads
    def _no_plist(*a, **k):
        raise AssertionError("plist parsed")
    plistlib.loads = plistlib.load = _no_plist
from scripts import cadence_look_run as R
if opts.get("manifest"):                     # the test's manifest stands in for the repository's fixed one
    R.manifest_path = lambda: Path(opts["manifest"])
if opts.get("run_state") is not None:          # the harness's fixture RUN_STATE (no CLI option takes one): a
    R.run_state_text = lambda allow_draft: opts["run_state"]       # run in the repository fetches nothing
    R.M.fetch_public = lambda repo: None
if opts.get("ledger"):
    R.ledger_path = lambda: Path(opts["ledger"])
if "host_probe" in opts:
    import subprocess
    real_run = subprocess.run
    def run(argv, *args, **kwargs):
        if argv[0] == "/usr/sbin/ioreg":
            assert argv == ["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]
            assert kwargs == {"capture_output": True, "check": True}
            return subprocess.CompletedProcess(argv, 0, opts["host_probe"].encode(), b"")
        return real_run(argv, *args, **kwargs)
    R.M.subprocess.run = run
else:
    R.M.execution_host = lambda: "hw1:" + "a" * 64
if opts.get("stage1_problems"):                  # a planted problem in the shared stage-1 check (Mythos r5 N7)
    R.M.stage1_problems = lambda *a, **k: list(opts["stage1_problems"])
if opts.get("trap"):
    # RL-173 E.1: the time reader converts only its whitelisted members, and no power_w of power_trace.csv
    TF = R.TF
    _member, _allowed = TF.member, set(TF.HEADER_KEYS) | set(TF.TRAILER_KEYS) | set(TF.POLL_KEYS)
    def _only_whitelisted(members, key):
        if key not in _allowed:
            raise AssertionError("the time reader converted a member outside its whitelist")
        return _member(members, key)
    TF.member = _only_whitelisted
    class _Poison(str):
        def __float__(self):
            raise AssertionError("a power_w was converted")
    class _Rows(TF.csv.DictReader):
        def __next__(self):
            row = super().__next__()
            if "power_w" in row:
                row["power_w"] = _Poison(row["power_w"])
            return row
    TF.csv = type(sys)("csv_trap")
    TF.csv.DictReader = _Rows
from pathlib import Path
import shutil
calls = []
private = None
if opts["exports"]:
    # Retained fit tests read generated private artifacts after the command exits.
    temp = Path(tempfile.mkdtemp(prefix="jw-look-fixture-"))
    private = temp / "synthetic-reservation"
    public = temp / "PUBLIC.json"
    R.release.destinations = lambda *a: (private, public)
    real_validate = R.validate_execution_row
    def validate(row, stage1, layout):
        holds = {flag: "RL-999" for flag in R.M.STAGE2_HOLD_FLAGS["interim"]
                 if stage1[flag.split(".")[0]].get(flag.split(".")[1]) is True}
        record = dict(row, execution_host="hw1:" + "a" * 64, custody_root=str(layout.root),
                      public_root=R.M.LOOK_PUBLIC_ROOT, holds_cleared=holds)
        return real_validate(record, stage1, layout)
    R.validate_execution_row = validate
    if not opts.get("real_twin"):
        R.require_twin_runner = lambda doc: None
        R.run_twin = lambda *args, **kwargs: {"agreement": "not_evaluable"}
    if not (R.ROOT / ".git").exists():
        git = R.M._git
        R.M._git = lambda repo, *args: ((0, b"f" * 40, "") if args == ("rev-parse", "HEAD") else git(repo, *args))
if opts.get("mock_stage2"):
    def _stage2(*a, **k):
        calls.append(1)
        return {}
    R.F.stage2 = _stage2
rc = None
try:
    if opts.get("entry") == "manifest":
        from scripts import cadence_look_manifest as manifest_cli
        rc = manifest_cli.main(argv)
    else:
        rc = R.main(argv)
finally:
    private_stderr = ""
    if private is not None:
        if rc == 0:
            for name, path in opts["exports"].items():
                shutil.copyfile(public if name == "PUBLIC.json" else private / name, path)
        if (private / "stderr").exists():
            private_stderr = (private / "stderr").read_text()
        shutil.rmtree(private.parent)
    if opts.get("report"):
        with open(opts["report"], "w") as f:
            served = [f"{sid}/{rel}" for custody in R.ADMITTED for sid, rel in custody.opened]
            json.dump({"opened": opened, "frames": frames, "stage2_calls": len(calls),
                       "private_stderr": private_stderr, "reservation_attempts": reservation_attempts,
                       "twin_launches": twin_launches, "served": served}, f)
sys.exit(rc)
'''


def _pin_dir():
    """The pin directory and the CLI harness in it, recreated if a module teardown removed them."""
    os.makedirs(_PIN_DIR, exist_ok=True)
    if not os.path.exists(_HARNESS):
        with open(_HARNESS, "w") as f:
            f.write(_HARNESS_SRC)


_pin_dir()

_SPIES = []           # active spy_opens lists: a subprocess's opens are appended to each
LAST_RUN = {}


def _cli_subprocess(argv, trap=False, mock_stage2=False, repo=None, extra=None):
    """Run the executor in its own ``python -I -B`` process through the harness. The executor takes no path
    (audit 2): a former command line is placed on the fixed layout first (``look_layout_fixture``), and its outputs
    are copied back to the names it asked for. In the repository the harness names this run's manifest (which
    registers the root and carries the pins) to the executor; a copy (``look_minirepo``) carries its own."""
    import subprocess
    import sys
    from tests.cadence import look_layout_fixture as layout_fixture, look_minirepo
    repo = Path(repo or REPO)
    _pin_dir()
    report = os.path.join(_PIN_DIR, f"report-{len(os.listdir(_PIN_DIR))}.json")
    argv = list(map(str, argv))
    extra = dict(extra or {})
    exports = {}
    if argv and argv[0] == "stage2":
        for flag, name in (("--out", "fit.json"), ("--coefficients-out", "coefficients.json")):
            if flag in argv:
                i = argv.index(flag)
                exports[name] = argv[i + 1]
                del argv[i:i + 2]
    pin = extra.pop("pin_custody", True)
    layout_opts = {}
    if repo != REPO:
        placed = look_minirepo.place_in(repo, argv, pin=pin)
        if placed.ledger:                   # a draft copy's scratch ledger, in place of the copy's LOOKS.json
            layout_opts = {"ledger": placed.ledger}
    else:
        placed = layout_fixture.place(argv, repo=REPO)
        if placed.placed:
            manifest = os.path.join(_PIN_DIR, f"placed-manifest-{len(os.listdir(_PIN_DIR))}.json")
            with io.FileIO(manifest, "w") as handle:
                handle.write((json.dumps(placed.manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
            layout_opts = {"manifest": manifest, "run_state": placed.run_state, "ledger": placed.ledger}
    opts = {"repo": str(repo), "spy": bool(_SPIES), "trap": trap, "mock_stage2": mock_stage2, "report": report,
            "exports": exports | extra.get("artifacts", {}), **layout_opts, **extra}
    r = subprocess.run([sys.executable, "-I", "-B", _HARNESS, json.dumps(opts), *placed.argv], cwd=repo,
                       capture_output=True, text=True, timeout=900)
    placed.collect()
    got = rj(report) if os.path.exists(report) else {"opened": [], "frames": [], "stage2_calls": 0}
    for spy in _SPIES:
        spy.extend(got["opened"])
    LAST_RUN.clear()
    LAST_RUN.update(got)
    return r.returncode, r.stdout, r.stderr


class Stage1Custody(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()

    def args(self, out):
        return ["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", out]

    def test_reader_rebuilds_level_r_exactly(self):
        """The custody reader rebuilds the generator's level R exactly, but for what only custody has: each span's
        custody digests and each development leg's trace clauses (RL-173 E.1; the generator writes null), which
        exclude no leg the generator did not plant as failing rule 3 or 4."""
        got = self.c.read_r()
        self.assertIs(got["synthetic"], True)
        spans = {s["span_id"]: s for s in self.c.li["spans"]}
        for sp in got["spans"]:
            cust = sp["custody"]
            files = set(cust["files_sha256"])
            self.assertIn("runner_receipt.json", files)
            self.assertIn("soak/soak_reference.json", files)
            self.assertTrue(any(p.endswith("/outputs/align_thermal.jsonl") for p in files))
            for path, sha in cust["files_sha256"].items():
                self.assertEqual(sha, R.sha256_file(self.c.root / sp["span_id"] / path))
            for leg in self.c.li["legs"]:
                if leg["span_id"] == sp["span_id"] and leg["leg_type"] == "T":
                    self.assertFalse(any(p.startswith(f"legs/{leg['leg_id']}/runtime/") for p in files))
            self.assertTrue(cust["native_pm_sha256"])
            self.assertRegex(cust["meter_time_sha256"], "^[0-9a-f]{64}$")
            self.assertIsNone(cust["meter_unreadable"])
            self.assertEqual([m["name"] for m in cust["meter_streams"]], ["stream-0001.jsonl"])
            self.assertEqual(cust["meter_streams"][0]["duplicates"], 0)
            sp["custody"] = None
            self.assertEqual(sp["soak_receipt"], spans[sp["span_id"]]["soak_receipt"])
        n_holes = 0
        for leg, want in zip(got["legs"], self.c.li["legs"]):
            th = leg["trace_holes"]
            span = spans[leg["span_id"]]
            if th is None:
                self.assertTrue(leg["turn"] is None or span["role"] == "describe", leg["leg_key"])
            else:
                n_holes += 1
                self.assertFalse(th["gpu_rail"]["excluded"], leg["leg_key"])           # the trace has every row
                self.assertLessEqual(th["gpu_rail"]["max_gap_s"], 2.0)
                # the planted rule-4 failure (polls removed for 3.5 s) is also a DC-in clause exclusion
                self.assertEqual(th["dc_in"]["excluded"], not want["inclusion"]["km003c_clean"], leg["leg_key"])
                self.assertTrue(th["dc_in"]["bracketed"])
            leg["trace_holes"] = None
        self.assertGreater(n_holes, 20)
        self.assertEqual(synth.dump(got), synth.dump(self.c.li))

    def test_stage1_opens_no_energy_file(self):
        """RL-173 E.1 item 1: stage 1 may open power_trace.csv and the meter streams for their time fields, and
        only through the one time reader (joulewise/cadence_looks/time_fields.py); no level-E file is opened."""
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "s1.json")
            with spy_opens() as opened:
                rc, _, err = run_cli(self.args(out))
            self.assertEqual(rc, 0, err)
        frames = LAST_RUN["frames"]
        self.assertTrue(any(p.endswith("events.jsonl") for p in opened))
        self.assertTrue(any(p.endswith("align_thermal.jsonl") for p in opened))
        self.assertFalse([p for p in opened if p.endswith("segment_energy.json")])
        energy = [(p, who) for p, who in frames if p.endswith("power_trace.csv") or "/hazards/meter/" in
                  p.replace(os.sep, "/")]
        self.assertTrue([p for p, _ in energy if p.endswith("power_trace.csv")])
        self.assertTrue([p for p, _ in energy if "/hazards/meter/stream-" in p.replace(os.sep, "/")])
        self.assertEqual({who for _, who in energy}, {"joulewise/cadence_looks/time_fields.py"})
        self.assertTrue(all("/hazards/meter/stream-" in p.replace(os.sep, "/") for p in opened if "/hazards/" in p))
        # the decoys exist, so the absence is meaningful
        self.assertTrue(list(self.c.root.glob("*/legs/*/runtime/runs/*/power_trace.csv")))
        self.assertTrue(list(self.c.root.glob("*/hazards/meter/stream-*.jsonl")))

    def test_stage1_decodes_no_power_value(self):
        """rich_telemetry and the plist are read by pattern for stamps and state only: no JSON line of them and no
        plist frame is parsed, so their gpu_energy and gpu_power never become values. RL-173 E.1: no meter line is
        JSON-decoded (header and trailer included), the time reader converts only whitelisted members, and no
        power_w of power_trace.csv is converted (the harness's traps raise on any of these)."""
        # the trap (in the CLI's process): any json.loads of an energy-bearing record, or any plist parse, raises
        with tempfile.TemporaryDirectory() as d:
            rc, _, err = run_cli(self.args(os.path.join(d, "s1.json")), trap=True)
        self.assertEqual(rc, 0, err)

    def test_r7_fan_null_when_a_key_is_missing(self):
        leg = next(leg for leg in self.c.li["legs"] if leg["turn"])
        sid, lid = leg["span_id"], leg["leg_id"]
        with tempfile.TemporaryDirectory() as d:
            bdir = Path(d) / "b"
            shutil.copytree(self.c.root / sid / "legs" / lid / "runtime" / "runs" / "cadence-leg", bdir,
                            ignore=shutil.ignore_patterns("power_trace.csv"))
            rows = [json.loads(x) for x in (bdir / "outputs/align_thermal.jsonl").read_text().splitlines() if x]
            for r in rows:
                if r.get("kind") == "reading":
                    del r["values"]["sensors"]["F1Ac"]
                    break
            with open(bdir / "outputs/align_thermal.jsonl", "w") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rows))
            j = R.journal_readings(bdir, -1e18, 1e18, R.FAN_KEYS)
        self.assertIsNone(j[0]["fan_rpm"])
        self.assertIsNotNone(j[1]["fan_rpm"])

    def test_missing_rules_3_4_verdict_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            v = rj(self.c.paths["rules_3_4.json"])
            v.pop(next(iter(v)))
            p = os.path.join(d, "v.json")
            wb(p, json.dumps(v))
            a = self.args(os.path.join(d, "s1.json"))
            a[a.index("--rules-3-4") + 1] = p
            rc, _, err = run_cli(a)
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", err)


class Stage2Custody(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.s3 = step3_path()

    def setUp(self):
        if self.s3 is None:
            self.skipTest("the committed step 3 module is not on this branch and no pinned copy is available")

    def s1(self):
        return F.stage1(self.c.li, hashlib.sha256(synth.dump(self.c.li)).hexdigest())

    def test_energy_reader_reproduces_level_e(self):
        s1 = self.s1()
        got, files = R.read_segment_energy(s1, LF.span_dirs(self.c.root, None), self.s3)
        self.assertEqual(set(got["legs"]), set(self.c.en["legs"]))
        # the custody record: every energy file opened, by path under the root and sha256 (no value)
        traces = {f["path"] for f in files if f["path"].endswith("/power_trace.csv")}
        self.assertEqual(len(traces), len(got["legs"]))
        self.assertEqual({f["path"].split("/")[0] for f in files if "/hazards/meter/" in f["path"]},
                         {k.split("/")[0] for k in got["legs"]})
        for f in files:
            self.assertEqual(f["sha256"], R.sha256_file(self.c.root / f["path"]))
        for k, e in got["legs"].items():
            want = self.c.en["legs"][k]
            for a, b in zip(e["gpu_rail"]["segments"], want["gpu_rail"]["segments"]):
                self.assertAlmostEqual(a / b, 1.0, delta=1e-12)
            for x in want["gpu_rail"]["prefix_tails"]:
                self.assertAlmostEqual(e["gpu_rail"]["prefix_tails"][x] / want["gpu_rail"]["prefix_tails"][x], 1.0,
                                       delta=1e-12)
            # DC-in: 2 samples/s against step changes at every boundary; the leg sum is within 0.2 %
            self.assertAlmostEqual(sum(e["dc_in"]["segments"]) / sum(want["dc_in"]["segments"]), 1.0, delta=2e-3)
            for a, b in zip(e["dc_in"]["segments"], want["dc_in"]["segments"]):
                self.assertAlmostEqual(a / b, 1.0, delta=0.03)

    def test_cli_both_stages_and_hash_gate(self):
        with tempfile.TemporaryDirectory() as d:
            s1p, fitp = os.path.join(d, "s1.json"), os.path.join(d, "fit.json")
            rc, out, err = run_cli(["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                                    "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", s1p])
            self.assertEqual(rc, 0, err)
            h = out.split("sha256=")[1].strip()
            self.assertEqual(h, R.sha256_file(s1p))
            rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", "0" * 64, "--custody",
                                  str(self.c.root), "--out", fitp])
            self.assertEqual(rc, 2)
            self.assertFalse(os.path.exists(fitp))
            rc, out, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--custody", str(self.c.root),
                                    "--out", fitp])
            self.assertEqual(rc, 0, err)
            fit = rj(fitp)
        self.assertEqual(fit["stage1_sha256"], h)
        for ch in F.CHANNELS:
            self.assertEqual(len(fit["channels"][ch]["coefficients"]), 9)

    def test_step3_module_must_be_the_pinned_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s3.py")
            shutil.copy(self.s3, p)
            with open(p, "a") as f:
                f.write("\n# edited\n")
            with self.assertRaises(F.LookInputError):
                R.load_step3(p)


class Meter(unittest.TestCase):

    def test_trapezoid_is_exact_on_a_linear_ramp_with_cuts(self):
        sample = struct.Struct("<HHiiHHHH")
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d)
            (sdir / "hazards/meter").mkdir(parents=True)
            raw0, off = 5 * 10**12, 1_790_000_000 * 10**9 - 5 * 10**12
            lines = [json.dumps({"k": "h", "status": "streaming", "rate_idx": 1, "start_raw_ns": raw0,
                                 "start_real_ns": raw0 + off})]
            for j in range(0, 600, 5):           # 10 samples/s for 60 s, 5 per poll
                raw = b""
                for i in range(j, j + 5):
                    w = 10.0 + 0.5 * (i * 0.1)                  # 10 W + 0.5 W/s
                    raw += sample.pack((i * 100) % 65536, 0, 20_000_000, int(round(w / 20 * 1e6)), 0, 0, 0, 0)
                rx = raw0 + (j + 4) * 100_000_000 + 200_000
                lines.append(json.dumps({"k": "b", "tx": rx - 1_000_000, "rx": rx, "rt": rx + off, "n": 5,
                                         "p": raw.hex(), "smc": {}}))
            lines.append(json.dumps({"k": "t", "polls": 120, "bad": 0, "usb_errors": 0}))
            (sdir / "hazards/meter/stream-0001.jsonl").write_text("\n".join(lines) + "\n")
            m = R.MeterSpan(sdir)
        t0 = m.t[0]
        a, b = t0 + 3.33, t0 + 41.07
        want = 10.0 * (b - a) + 0.25 * ((b - t0) ** 2 - (a - t0) ** 2)
        self.assertAlmostEqual(m.energy(a, b), want, delta=1e-3)
        with self.assertRaisesRegex(F.LookInputError, "bracketed"):    # no sample at or before the start
            m.energy(t0 - 1.0, t0 + 1.0)


class LevelR(unittest.TestCase):

    def test_cli_level_r_round_trip_and_canonical_gate(self):
        li, en, _ = synth.build("exact")
        with tempfile.TemporaryDirectory() as d:
            ip, ep = os.path.join(d, "li.json"), os.path.join(d, "en.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(en))
            s1p, fitp = os.path.join(d, "s1.json"), os.path.join(d, "fit.json")
            with spy_opens() as opened:
                rc, out, err = run_cli(["stage1", "--input", ip, "--out", s1p])
            self.assertEqual(rc, 0, err)
            self.assertFalse([p for p in opened if p.endswith("en.json")])
            h = out.split("sha256=")[1].strip()
            # a re-serialised stage-1 file with the right hash of its new bytes is still refused: not canonical
            s1 = rj(s1p)
            pretty = os.path.join(d, "pretty.json")
            wb(pretty, json.dumps(s1, indent=1))
            rc, _, err = run_cli(["stage2", "--stage1", pretty, "--stage1-sha256", R.sha256_file(pretty),
                                  "--energy", ep, "--out", fitp])
            self.assertEqual(rc, 2)
            rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--energy", ep, "--out", fitp])
            self.assertEqual(rc, 0, err)


if __name__ == "__main__":
    unittest.main()


class CliGate(unittest.TestCase):

    def test_cli_refuses_a_wrong_stage1_hash_before_stage2(self):
        li, en, _ = synth.build("exact")
        with tempfile.TemporaryDirectory() as d:
            ip, ep, s1p = os.path.join(d, "li.json"), os.path.join(d, "en.json"), os.path.join(d, "s1.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(en))
            self.assertEqual(run_cli(["stage1", "--input", ip, "--out", s1p])[0], 0)
            rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", "0" * 64, "--energy", ep,
                                  "--out", os.path.join(d, "fit.json")], mock_stage2=True)
            self.assertEqual(rc, 2)
            self.assertEqual(LAST_RUN["stage2_calls"], 0)


class VerifierCleanup(unittest.TestCase):
    @unittest.skipIf(_NUMPY_MISSING, "the look runner needs numpy")
    def test_sigterm_removes_the_verifiers_temporary_digests(self):
        driver = r'''
import os
from pathlib import Path
import signal
import subprocess
from unittest.mock import patch
from scripts import cadence_look_run as run

def interrupt(argv, **kwargs):
    pins = Path(argv[argv.index("--pins") + 1])
    assert pins.is_file()
    Path(argv[argv.index("--out") + 1]).write_text("invented verifier result")
    signal.raise_signal(signal.SIGTERM)
    raise AssertionError("SIGTERM did not unwind the verifier")

doc = run.M.load_json(run.manifest_path())
with patch.object(subprocess, "run", interrupt):
    run.run_verifier(doc, {"spans": []}, "0" * 64, [], None)
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(__file__).resolve().parents[2]
            result = subprocess.run([sys.executable, "-B", "-c", driver], cwd=root,
                                    env={**os.environ, "TMPDIR": tmp}, capture_output=True, timeout=30)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (143, b"", b""))
            self.assertEqual(list(Path(tmp).iterdir()), [])


class NoHpEnergy(unittest.TestCase):

    def test_stage2_opens_no_hp01_energy(self):
        c = _Custody.get()
        s3 = step3_path()
        if s3 is None:
            self.skipTest("no pinned step 3 module")
        s1 = F.stage1(c.li, hashlib.sha256(synth.dump(c.li)).hexdigest())
        with spy_opens() as opened:
            e, _ = R.read_segment_energy(s1, LF.span_dirs(c.root, None), s3)
        self.assertFalse([p for p in opened if "/hp-01-" in p.replace(os.sep, "/")])
        self.assertFalse([k for k in e["legs"] if k.startswith("hp-01")])


class Rules34Agree(unittest.TestCase):
    """The synthetic custody exercises inclusion_34.py: its verdicts equal the planted ones (type-T legs have no
    bundle in the synthetic custody and are not read at this look, so they are left out)."""

    def test_inclusion_34_verdicts_match_planted(self):
        try:
            from joulewise.cadence_looks import inclusion_34 as I
        except ImportError:
            self.skipTest("inclusion_34.py is not on this branch")
        c = _Custody.get()
        roster = rj(c.paths["roster.json"])
        sensors = rj(Path(R.ROOT) / "configs/align/v4/r1_runtime.json")["sensors"]
        verdicts, _ = I.judge_custody(roster, I.span_dirs(c.root), I.keys(sensors))
        planted = rj(c.paths["rules_3_4.json"])
        t_legs = {leg["leg_key"] for leg in c.li["legs"] if leg["leg_type"] == "T"}
        self.assertEqual({k: v for k, v in verdicts.items() if k not in t_legs},
                         {k: v for k, v in planted.items() if k not in t_legs})
        self.assertIn(False, [v["sidecar_coverage"] for v in planted.values()])
        self.assertIn(False, [v["km003c_clean"] for v in planted.values()])


class ColdSeatFixes(unittest.TestCase):
    """The Mythos and Sol cold seats on the combined look head (5ea1bdee9), in this package's files."""

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.roster = rj(cls.c.paths["roster.json"])
        cls.rules = rj(cls.c.paths["rules_3_4.json"])

    def span_copy(self, d, span_id):
        dst = Path(d) / span_id
        shutil.copytree(self.c.root / span_id, dst, ignore=shutil.ignore_patterns("power_trace.csv"))
        return dst

    def entry(self, span_id):
        return next(e for e in self.roster if e["span_id"] == span_id)

    def g0_timeout_leg(self):
        leg = next(x for x in self.c.li["legs"] if x["leg_type"] == "A" and x["turn"] is None)
        self.assertFalse(leg["inclusion"]["g0_released"])
        return leg

    def test_m1_g0_timeout_absent_turns_is_an_exclusion(self):
        leg = self.g0_timeout_leg()
        bundle = self.c.root / leg["span_id"] / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg"
        self.assertTrue((bundle / "events.jsonl").is_file())
        self.assertFalse((bundle / "outputs/align_turns.jsonl").exists())
        span, legs = R.read_span(self.c.root / leg["span_id"], self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        got = next(x for x in legs if x["leg_key"] == leg["leg_key"])
        self.assertIsNone(got["turn"])
        self.assertFalse(got["inclusion"]["g0_released"])

    def test_m1_g0_timeout_empty_turns_is_an_exclusion(self):
        leg = self.g0_timeout_leg()
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            (sdir / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg/outputs/align_turns.jsonl").write_text("")
            _, legs = R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        self.assertIsNone(next(x for x in legs if x["leg_key"] == leg["leg_key"])["turn"])

    def test_m1_included_leg_without_a_turn_refuses(self):
        leg = next(x for x in self.c.li["legs"] if x["turn"] and all(x["inclusion"].values()))
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            (sdir / "legs" / leg["leg_id"] / "runtime/runs/cadence-leg/outputs/align_turns.jsonl").unlink()
            with self.assertRaisesRegex(F.LookInputError, "included leg"):
                R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)

    def test_m7_capture_excluded_at_the_look_marks_the_span(self):
        span_id = next(s["span_id"] for s in self.c.li["spans"] if not s["marks"]
                       and any(x["g0_role"] == "consume" for x in self.c.li["legs"] if x["span_id"] == s["span_id"]))
        cap = next(x for x in self.c.li["legs"] if x["span_id"] == span_id and x["g0_role"] == "capture")
        span, _ = R.read_span(self.c.root / span_id, self.entry(span_id), self.rules, R.FAN_KEYS)
        self.assertEqual(span["marks"], [])
        rules = dict(self.rules)
        rules[cap["leg_key"]] = {"sidecar_coverage": True, "km003c_clean": False}      # rule 4 fails at the look
        span, _ = R.read_span(self.c.root / span_id, self.entry(span_id), rules, R.FAN_KEYS)
        self.assertEqual(span["marks"], ["reference from an excluded leg"])

    def test_m13_custody_carries_the_synthetic_flag(self):
        li = R.read_look_input(self.roster, LF.span_dirs(self.c.root, None), self.rules)
        self.assertTrue(li["synthetic"])
        with tempfile.TemporaryDirectory() as d:
            sid = self.roster[0]["span_id"]
            sdir = self.span_copy(d, sid)
            rec = rj(sdir / "runner_receipt.json")
            rec.pop("synthetic")
            wb(sdir / "runner_receipt.json", json.dumps(rec))
            # The generator's receipt without its flag is no pinned writer's receipt either, so admission refuses it;
            # a written span's `synthetic` False is the frozen admission matrix's path (test_interim_admission_closure).
            with self.assertRaisesRegex(F.LookInputError, "admission: .*runner_receipt.json"):
                R.read_look_input([self.roster[0]], LF.span_dirs(d, None), self.rules)

    def test_m14_unrun_leg_has_no_cell_and_cannot_be_included(self):
        with tempfile.TemporaryDirectory() as d:
            sid = self.roster[0]["span_id"]
            sdir = self.span_copy(d, sid)
            lid = rj(sdir / "runner_receipt.json")["roster"][-1]
            shutil.rmtree(sdir / "legs" / lid)
            _, legs = R.read_span(sdir, self.roster[0], self.rules, R.FAN_KEYS)
        leg = next(x for x in legs if x["leg_id"] == lid)
        self.assertEqual((leg["cell_prompt_tokens"], leg["turn"]), (None, None))
        self.assertFalse(any(leg["inclusion"].values()))
        li = copy.deepcopy(self.c.li)
        t = next(x for x in li["legs"] if x["turn"] and all(x["inclusion"].values()))
        t["turn"] = None
        with self.assertRaisesRegex(F.LookInputError, "R-21"):
            F.validate_input(li)

    def test_sol2_type_t_only_from_leg_type(self):
        leg = next(x for x in self.c.li["legs"] if x["turn"])
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, leg["span_id"])
            p = sdir / "legs" / leg["leg_id"] / "leg_record.json"
            rec = rj(p)
            rec["spec"]["type"] = "T"                    # the legacy key is ignored (R-21)
            wb(p, json.dumps(rec))
            _, legs = R.read_span(sdir, self.entry(leg["span_id"]), self.rules, R.FAN_KEYS)
        self.assertEqual(next(x for x in legs if x["leg_key"] == leg["leg_key"])["leg_type"], "A")

    def test_roster_is_one_shape(self):
        with self.assertRaises(F.LookInputError):
            R.read_look_input({"roster": self.roster}, LF.span_dirs(self.c.root, None), self.rules)

    def test_m4_meter_stream_without_samples_is_skipped(self):
        sid = self.roster[0]["span_id"]
        with tempfile.TemporaryDirectory() as d:
            sdir = self.span_copy(d, sid)
            hdr = (sdir / "hazards/meter/stream-0001.jsonl").read_text().splitlines()[0]
            (sdir / "hazards/meter/stream-0002.jsonl").write_text(hdr + "\n")
            m = R.MeterSpan(sdir)
            self.assertGreater(len(m.t), 100)
            (sdir / "hazards/meter/stream-0001.jsonl").unlink()
            with self.assertRaises(F.LookInputError):
                R.MeterSpan(sdir)

    def test_m4_stage1_preflight_refuses_a_missing_power_trace_before_stage_2(self):
        s1 = self.c.s1_custody()
        R.stage2_preflight(s1, LF.span_dirs(self.c.root, None))
        # RL-173 E.1: an energy-fit leg without both trace clauses (a level-R file the custody reader did not make)
        with self.assertRaisesRegex(F.LookInputError, "in the energy fit without both trace clauses"):
            R.stage2_preflight(F.stage1(self.c.li, "0" * 64), LF.span_dirs(self.c.root, None))
        L = next(x for x in s1["legs"] if x["in_energy_fit"])
        with tempfile.TemporaryDirectory() as d:
            self.span_copy(d, L["span_id"])               # the copy carries no power_trace.csv
            sdir_of = LF.span_dirs(self.c.root, [f"{L['span_id']}={d}/{L['span_id']}"])
            with self.assertRaisesRegex(F.LookInputError, "power_trace"):
                R.stage2_preflight(s1, sdir_of)

    def test_sol8_one_day_refuses_before_energy(self):
        li = copy.deepcopy(self.c.li)
        days = sorted({s["t0_local_date"] for s in li["spans"] if s["role"] == "fit"})
        keep = {s["span_id"] for s in li["spans"] if s["t0_local_date"] == days[-1] or s["role"] == "describe"}
        li["spans"] = [s for s in li["spans"] if s["span_id"] in keep]
        li["legs"] = [x for x in li["legs"] if x["span_id"] in keep]
        with tempfile.TemporaryDirectory() as d:
            ip, ep, s1p = os.path.join(d, "li.json"), os.path.join(d, "en.json"), os.path.join(d, "s1.json")
            wb(ip, synth.dump(li))
            wb(ep, synth.dump(self.c.en))
            rc, out, err = run_cli(["stage1", "--input", ip, "--out", s1p])
            self.assertEqual(rc, 0, err)
            h = out.split("sha256=")[1].strip()
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--energy", ep,
                                      "--out", os.path.join(d, "fit.json")])
        self.assertEqual(rc, 2)
        self.assertIn("two fit days", err)
        self.assertFalse([p for p in opened if p.endswith("en.json")])


class PinsAndCommit(unittest.TestCase):
    """verify_pins runs first in both stages; stage 2 requires LOOKS.json to name the stage-1 hash."""

    @classmethod
    def setUpClass(cls):
        li, cls.en, _ = synth.build("exact")
        cls.d = tempfile.mkdtemp(prefix="jw-look-pins-run-")
        cls.ip, cls.ep = os.path.join(cls.d, "li.json"), os.path.join(cls.d, "en.json")
        wb(cls.ip, synth.dump(li))
        wb(cls.ep, synth.dump(cls.en))
        cls.s1p = os.path.join(cls.d, "s1.json")
        rc, out, err = run_cli(["stage1", "--input", cls.ip, "--out", cls.s1p])
        assert rc == 0, err
        cls.h = out.split("sha256=")[1].strip()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def test_a_pin_mismatch_refuses_before_any_input_opens(self):
        def wrong(doc):
            for ref in doc["fit"]["code"]:
                if ref["path"] == "joulewise/cadence_looks/fit_interim.py":
                    ref["sha256"] = "0" * 64
        bad = pinned_manifest(wrong)
        with spy_opens() as opened:
            rc, _, err = run_cli(["stage1", "--input", self.ip, "--out", os.path.join(self.d, "x.json"),
                                  "--manifest", bad, "--allow-draft"])
        self.assertEqual(rc, 2)
        self.assertIn("differs from the pin", err)
        self.assertFalse([p for p in opened if p.endswith("li.json")])
        with spy_opens() as opened:
            rc, _, err = run_cli(["stage2", "--stage1", self.s1p, "--stage1-sha256", self.h, "--energy", self.ep,
                                  "--out", os.path.join(self.d, "y.json"), "--manifest", bad, "--allow-draft"])
        self.assertEqual(rc, 2)
        self.assertFalse([p for p in opened if p.endswith(("s1.json", "en.json"))])

    def test_a_draft_manifest_refuses_without_allow_draft(self):
        rc, _, err = run_cli(["stage1", "--input", self.ip, "--out", os.path.join(self.d, "x.json"),
                              "--manifest", pinned_manifest()])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", err)

    def test_stage2_needs_the_committed_stage1_hash_before_energy(self):
        for looks in (looks_file("9" * 64), looks_file(self.h, status="draft")):
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", self.s1p, "--stage1-sha256", self.h,
                                      "--energy", self.ep, "--out", os.path.join(self.d, "y.json"),
                                      "--looks", looks])
            self.assertEqual(rc, 2, err)
            self.assertFalse([p for p in opened if p.endswith("en.json")])
        rc, _, err = run_cli(["stage2", "--stage1", self.s1p, "--stage1-sha256", self.h, "--energy", self.ep,
                              "--out", os.path.join(self.d, "y.json"), "--looks", looks_file(self.h)])
        self.assertEqual(rc, 0, err)


def _meter_lines(t0, n, step=0.5, per_poll=2, watts=40.0, empty=lambda x: False, off=10**18,
                 resend=lambda x: False, nopayload=lambda x: False):
    """A KM003C stream as the monitor writes it (compact lines). Polls whose time is `empty` carry n:0, p:"".
    `resend`: the poll re-sends the previous poll's samples (same sequence numbers; the decoder drops them as
    duplicates). `nopayload`: the poll reports n samples and carries no payload."""
    sample = struct.Struct("<HHiiHHHH")
    raw0 = int(round(t0 * 1e9)) - off
    lines = [json.dumps({"k": "h", "status": "streaming", "rate_idx": 0, "poll_s": step * per_poll,
                         "sps": 1.0 / step, "start_raw_ns": raw0, "start_real_ns": raw0 + off},
                        separators=(",", ":"))]
    prev = None
    for j in range(0, n, per_poll):
        x = t0 + j * step
        rx = raw0 + int(round((j + per_poll - 1) * step * 1e9)) + 400_000
        if (resend(x) and prev is not None) or nopayload(x):
            lines.append(json.dumps({"k": "b", "tx": rx - 10**6, "rx": rx, "rt": rx + off, "n": per_poll,
                                     "p": prev.hex() if resend(x) else "", "smc": {}}, separators=(",", ":")))
            continue
        if empty(x):
            lines.append(json.dumps({"k": "b", "tx": rx - 10**6, "rx": rx, "rt": rx + off, "n": 0, "p": ""},
                                    separators=(",", ":")))
            continue
        raw = b"".join(sample.pack(int(round((j + i) * step * 1000)) % 65536, 0, 28_000_000,
                                   int(round(watts / 28 * 1e6)), 0, 0, 0, 0) for i in range(per_poll))
        prev = raw
        lines.append(json.dumps({"k": "b", "tx": rx - 10**6, "rx": rx, "rt": rx + off, "n": per_poll,
                                 "p": raw.hex(), "smc": {}}, separators=(",", ":")))
    lines.append(json.dumps({"k": "t", "polls": n // per_poll, "empties": 0, "bad": 0, "usb_errors": 0,
                             "stop_reason": "signal 15"}, separators=(",", ":")))
    return "\n".join(lines) + "\n"


class MeterSupport(unittest.TestCase):
    """Sol delta N5 (HIGH): no DC-in energy across an interval without aligned samples; coverage per interval."""

    def meter(self, d, streams):
        sdir = Path(d)
        (sdir / "hazards/meter").mkdir(parents=True, exist_ok=True)
        for i, text in enumerate(streams, 1):
            (sdir / f"hazards/meter/stream-{i:04d}.jsonl").write_text(text)
        return R.MeterSpan(sdir)

    def test_three_streams_middle_empty_refuses_inside_and_works_outside(self):
        t0 = 1_790_000_000.0
        with tempfile.TemporaryDirectory() as d:
            m = self.meter(d, [_meter_lines(t0, 400), _meter_lines(t0 + 200, 800, empty=lambda x: True),
                               _meter_lines(t0 + 600, 400)])
            self.assertAlmostEqual(m.energy(t0 + 10, t0 + 100), 40.0 * 90, delta=1e-2)       # before the hole
            self.assertAlmostEqual(m.energy(t0 + 650, t0 + 700), 40.0 * 50, delta=1e-2)      # after it
            for a, b in ((t0 + 250, t0 + 590),     # a whole turn inside the hole (Sol's case)
                         (t0 + 150, t0 + 250),     # hole at the interval's end
                         (t0 + 590, t0 + 650),     # hole at its start
                         (t0 + 150, t0 + 650)):    # partial overlap, hole inside
                with self.assertRaisesRegex(F.LookInputError, r"DC-in: \(leg\): a gap of [0-9.]+ s"):
                    m.energy(a, b)
            self.assertAlmostEqual(m.coverage(t0 + 10, t0 + 100), 1.0, delta=1e-6)
            self.assertLess(m.coverage(t0 + 150, t0 + 250), 0.6)

    def test_short_hole_is_bridged_and_shows_in_coverage(self):
        t0 = 1_790_000_000.0
        with tempfile.TemporaryDirectory() as d:
            m = self.meter(d, [_meter_lines(t0, 400, empty=lambda x: t0 + 50 <= x < t0 + 51)])
            e = m.energy(t0 + 40, t0 + 60)                      # a 1.5 s sample gap: within rule 4's 2 s
            self.assertAlmostEqual(e, 40.0 * 20, delta=1e-2)
            self.assertLess(m.coverage(t0 + 40, t0 + 60), 0.96)
            m2 = self.meter(tempfile.mkdtemp(dir=d), [_meter_lines(t0, 400, empty=lambda x: t0 + 50 <= x < t0 + 52)])
            with self.assertRaisesRegex(F.LookInputError, r"DC-in: \(leg\): a gap of 2\.500 s"):
                m2.energy(t0 + 40, t0 + 60)

    def test_interval_beyond_the_samples_refuses(self):
        t0 = 1_790_000_000.0
        with tempfile.TemporaryDirectory() as d:
            m = self.meter(d, [_meter_lines(t0, 100)])
            for a, b in ((t0 + 40, t0 + 60), (t0 - 5, t0 + 10)):
                with self.assertRaisesRegex(F.LookInputError, "a gap of|bracketed"):
                    m.energy(a, b)

    def test_sol_meter_gap_case_through_the_reader(self):
        """Sol's case on the synthetic custody: the meter split into three closed streams, the middle one empty
        across a whole fit turn. Stage 2's reader refuses instead of interpolating; the intact span reads."""
        c = _Custody.get()
        s1 = F.stage1(c.li, "0" * 64)
        L = next(x for x in s1["legs"] if x["in_energy_fit"] and x["span_id"] == "dev-01-s02")
        ts, tl = L["segments"][0]["wall_start_s"], L["segments"][-1]["wall_end_s"]
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / L["span_id"]
            shutil.copytree(c.root / L["span_id"], sdir)
            src = (sdir / "hazards/meter/stream-0001.jsonl").read_text().splitlines()
            head, polls, trailer = src[0], src[1:-1], src[-1]
            hdr = json.loads(head)
            off = hdr["start_real_ns"] - hdr["start_raw_ns"]

            def in_gap(line):
                rt = json.loads(line)["rt"] / 1e9
                return ts - 10 <= rt <= tl + 10
            a = [p for p in polls if json.loads(p)["rt"] / 1e9 < ts - 10]
            b = [p for p in polls if in_gap(p)]
            c_ = [p for p in polls if json.loads(p)["rt"] / 1e9 > tl + 10]
            empty = [json.dumps(dict(json.loads(p), n=0, p=""), separators=(",", ":")) for p in b]
            (sdir / "hazards/meter/stream-0001.jsonl").write_text("\n".join([head] + a + [trailer]) + "\n")
            (sdir / "hazards/meter/stream-0002.jsonl").write_text("\n".join([head] + empty + [trailer]) + "\n")
            (sdir / "hazards/meter/stream-0003.jsonl").write_text("\n".join([head] + c_ + [trailer]) + "\n")
            sdir_of = LF.span_dirs(c.root, [f"{L['span_id']}={sdir}"])
            with self.assertRaisesRegex(F.LookInputError, rf"DC-in: {L['leg_key']}: a gap of [0-9.]+ s between meter"):
                R.read_segment_energy(s1, sdir_of, step3_path())
            self.assertGreater(off, 0)


class RoundTwoCli(unittest.TestCase):
    """Mythos N2 and N7, Sol N1/N2 (this package's side) and Mythos N3, N9."""

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        li, cls.en, _ = synth.build("exact")
        cls.d = tempfile.mkdtemp(prefix="jw-look-r2-")
        cls.ip, cls.ep = os.path.join(cls.d, "li.json"), os.path.join(cls.d, "en.json")
        wb(cls.ip, synth.dump(li))
        wb(cls.ep, synth.dump(cls.en))
        real = copy.deepcopy(li)
        real["synthetic"] = False
        cls.rp = os.path.join(cls.d, "real.json")
        wb(cls.rp, synth.dump(real))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def s1(self, ip=None):
        p = os.path.join(self.d, f"s1-{len(os.listdir(self.d))}.json")
        rc, out, err = run_cli(["stage1", "--input", ip or self.ip, "--out", p])
        return rc, p, (out.split("sha256=")[1].strip() if rc == 0 else None), err

    def test_n2_allow_draft_needs_synthetic_input(self):
        rc, _, _, err = self.s1(self.rp)
        self.assertEqual(rc, 2)
        self.assertIn("synthetic input only", err)

    def test_n2_outputs_record_allow_draft_and_the_manifest(self):
        rc, p, h, err = self.s1()
        self.assertEqual(rc, 0, err)
        d = rj(p)
        self.assertIs(d["allow_draft"], True)
        self.assertIsNone(d["ledger_gate"])                 # no committed-ledger gate under --allow-draft
        # the manifest the executor was given: the default draft with the registered root and pins (audit 2)
        self.assertEqual(d["manifest_sha256"], hashlib.sha256(placed_manifest_bytes(["stage1", "--input", self.ip])).hexdigest())
        # code_sha256 = the repository files that stage loaded (M.loaded_repo_files): exactly manifest.STAGE1_CODE,
        # the time reader and the meter decoder's closure included whatever the input (RL-173 E.1), and no test module
        for k in ("joulewise/cadence_looks/fit_interim.py", "scripts/cadence_look_run.py",
                  "joulewise/cadence_looks/manifest.py", "joulewise/cadence_looks/time_fields.py",
                  "joulewise/external/km003c_parse.py"):
            self.assertIn(k, d["code_sha256"])
        self.assertFalse([k for k in d["code_sha256"] if k.startswith("tests/")])
        self.assertEqual({k for k in d["code_sha256"] if not k.startswith("input:")}, set(M.STAGE1_CODE))
        o = os.path.join(self.d, "o.json")
        rc, _, err = run_cli(["stage2", "--stage1", p, "--stage1-sha256", h, "--energy", self.ep, "--out", o])
        self.assertEqual(rc, 0, err)
        self.assertIs(rj(o)["allow_draft"], True)
        self.assertEqual(rj(o)["manifest_sha256"], d["manifest_sha256"])

    def test_n2_stage2_refuses_a_non_synthetic_stage1_under_allow_draft(self):
        rc, p, h, _ = self.s1()
        doc = rj(p)
        doc["synthetic"] = False
        q = os.path.join(self.d, "s1-real.json")
        wb(q, F.dump(doc))
        rc, _, err = run_cli(["stage2", "--stage1", q, "--stage1-sha256", R.sha256_file(q), "--energy", self.ep,
                              "--out", os.path.join(self.d, "x.json")])
        self.assertEqual(rc, 2)
        self.assertIn("synthetic input only", err)

    def test_n7_level_r_e_and_scratch_ledger_only_with_allow_draft(self):
        man = _DEFAULT_MANIFEST[0] if _DEFAULT_MANIFEST else pinned_manifest()
        rc, _, err = run_cli(["stage1", "--input", self.ip, "--out", os.path.join(self.d, "y.json"),
                              "--manifest", man])
        self.assertEqual(rc, 2)
        rc, p, h, _ = self.s1()
        # without --allow-draft a draft manifest already refuses; the guards below are checked in the stage itself
        # a committed look reads custody: level R and level E are synthetic only, and no command names another
        # ledger (audit 2: no option takes a path; CommandLine in test_look_layout)
        a = R.argparse.Namespace(stage1_sha256=h, level_e=True, ledger_ref=None, allow_draft=False)
        with self.assertRaisesRegex(F.LookInputError, "--level-e"):
            R.cmd_stage2(a)
        a = R.argparse.Namespace(level_r=True, allow_draft=False)
        with self.assertRaisesRegex(F.LookInputError, "--level-r"):
            R.cmd_stage1(a)

    def test_n3_own_shaped_supplier_excluded_marks_the_span(self):
        roster = rj(self.c.paths["roster.json"])
        rules = rj(self.c.paths["rules_3_4.json"])
        span_id = next(s["span_id"] for s in self.c.li["spans"] if not s["marks"]
                       and any(x["g0_role"] == "consume" for x in self.c.li["legs"] if x["span_id"] == s["span_id"]))
        entry = next(e for e in roster if e["span_id"] == span_id)
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / span_id
            shutil.copytree(self.c.root / span_id, sdir)       # power_trace.csv too: the GPU clause reads its stamps
            first = rj(sdir / "runner_receipt.json")["roster"][0]
            rec = rj(sdir / "legs" / first / "leg_record.json")
            rec["spec"].pop("g0_role", None)                   # own-shaped, as dev-03's first span is built
            wb(sdir / "legs" / first / "leg_record.json", json.dumps(rec))
            span, _ = R.read_span(sdir, entry, rules, R.FAN_KEYS)
            self.assertEqual(span["marks"], [])
            rules = dict(rules)
            rules[f"{span_id}/{first}"] = {"sidecar_coverage": True, "km003c_clean": False}
            span, legs = R.read_span(sdir, entry, rules, R.FAN_KEYS)
        self.assertIsNone(next(x for x in legs if x["leg_id"] == first)["g0_role"])
        self.assertEqual(span["marks"], ["reference from an excluded leg"])

    def test_n9_type_t_not_counted_under_the_rules(self):
        li = copy.deepcopy(self.c.li)
        t = next(x for x in li["legs"] if x["leg_type"] == "T")
        t["inclusion"].update(sidecar_coverage=False, km003c_clean=False)
        base = F.stage1(self.c.li, "0" * 64)["counts"]["excluded_by_rule"]
        got = F.stage1(li, "0" * 64)["counts"]["excluded_by_rule"]
        self.assertEqual(got, base)


class CommittedLedger(unittest.TestCase):
    """Stage 2 without --allow-draft reads the committed ledger (manifest.require_stage1_committed) on a pinned copy
    of the look's files (look_minirepo): it runs when LOOKS.json at HEAD names this stage-1 hash and roster, and
    refuses when it names another stage-1 hash."""

    def test_stage2_against_the_committed_ledger(self):
        from tests.cadence import look_minirepo as mr
        c = _Custody.get()
        mini = mr.mini_repo(self)
        roster_sha, verdicts_sha = R.sha256_file(c.paths["roster.json"]), R.sha256_file(c.paths["rules_3_4.json"])
        # the manifest committed, with the roster and verdict file stage 1 is given (Mythos r3 N8)
        mr.commit(mini, roster_sha256=roster_sha, verdicts_sha256=verdicts_sha)
        d = tempfile.mkdtemp(prefix="jw-look-committed-")
        self.addCleanup(lambda: shutil.rmtree(d, ignore_errors=True))
        man = mini / mr.MANIFEST
        s1p, op = os.path.join(d, "s1.json"), os.path.join(d, "o.json")
        r = mr.py(mini, "scripts/cadence_look_run.py", "stage1", "--roster", c.paths["roster.json"],
                  "--custody", c.root, "--rules-3-4", c.paths["rules_3_4.json"], "--out", s1p, "--manifest", man)
        self.assertEqual(r.returncode, 0, r.stderr)
        h = R.sha256_file(s1p)
        roster = rj(s1p)["code_sha256"]["input:roster_sha256"]
        self.assertEqual(roster, roster_sha)
        mr.commit(mini, stage1_sha256=h, roster_sha256=roster, verdicts_sha256=verdicts_sha)
        args = ["stage2", "--stage1", s1p, "--stage1-sha256", h, "--custody", c.root, "--out", op, "--manifest", man]
        rc, _, err = _cli_subprocess(args, repo=mini)
        self.assertEqual(rc, 0, err + LAST_RUN.get("private_stderr", ""))
        self.assertIs(rj(op)["allow_draft"], False)
        self.assertEqual(set(rj(op)["ledger_gate"]), {"commit", "ref", "ref_commit"})
        mr.commit(mini, stage1_sha256="9" * 64, roster_sha256=roster, verdicts_sha256=verdicts_sha)
        os.unlink(op)
        rc, _, err = _cli_subprocess(args, repo=mini)
        self.assertEqual(rc, 2)
        self.assertIn("stage-1 sha256", err)
        self.assertFalse(os.path.exists(op))


class MeterSampleSupport(unittest.TestCase):
    """Sol r4 NEW-1 and Mythos r4 N1: stage 2 judges support on the DECODED samples. Rule 4 passes on each stream
    below (its poll stamps are regular); stage 2 refuses the interval that crosses the hole in the samples."""

    T0 = 1_790_000_000.0

    def stream(self, d, **kw):
        sdir = Path(d)
        (sdir / "hazards/meter").mkdir(parents=True, exist_ok=True)
        path = sdir / "hazards/meter/stream-0001.jsonl"
        path.write_text(_meter_lines(self.T0, 400, **kw))         # 200 s at 2 samples/s, polls every 1 s
        return R.MeterSpan(sdir), path

    def rule4_passes(self, path, a, b):
        from joulewise.cadence_looks import inclusion_34 as I34
        r4 = I34.rule4((round(a * 1e9), round(b * 1e9)), [I34.read_meter_stream(path)])
        return r4["max_gap_s"] is not None and r4["max_gap_s"] <= 2.0

    def check_hole(self, mode, h0, h1, a, b):
        with tempfile.TemporaryDirectory() as d:
            m, path = self.stream(d, **{mode: lambda x: self.T0 + h0 <= x < self.T0 + h1})
            self.assertTrue(self.rule4_passes(path, self.T0 + a, self.T0 + b), mode)
            gaps = [y - x for x, y in zip(m.t, m.t[1:])]
            with self.assertRaisesRegex(F.LookInputError, r"DC-in: \(leg\): (a gap of [0-9.]+ s|.*not bracketed)"):
                m.energy(self.T0 + a, self.T0 + b)
            self.assertAlmostEqual(m.energy(self.T0 + 10, self.T0 + 30), 40.0 * 20, delta=1e-2)   # outside it
            return max(gaps)

    def test_sol_8_5_s_hole_of_resent_samples(self):
        self.assertAlmostEqual(self.check_hole("resend", 50, 58, 40, 70), 8.5, delta=0.05)

    def test_mythos_6_5_s_hole_of_resent_samples(self):
        self.assertAlmostEqual(self.check_hole("resend", 50, 56, 45, 65), 6.5, delta=0.05)

    def test_mythos_40_5_s_of_polls_without_payload(self):
        self.assertAlmostEqual(self.check_hole("nopayload", 60, 100, 70, 90), 40.5, delta=0.05)

    def test_mythos_15_s_flat_end_is_not_held(self):
        """The last 15 s of the stream carry no payload: an interval reaching into them is not bracketed by a
        decoded sample, and nothing is held at the last value."""
        with tempfile.TemporaryDirectory() as d:
            m, _ = self.stream(d, nopayload=lambda x: x >= self.T0 + 185)
            self.assertLess(m.t[-1], self.T0 + 185)
            with self.assertRaisesRegex(F.LookInputError, "bracketed|a gap of"):
                m.energy(self.T0 + 170, self.T0 + 195)

    def test_an_admitted_bracketed_leg_integrates(self):
        """RL-173 E.1: stage 1's DC-in clause and stage 2's support test are one definition (time_fields.support on
        the decoded samples). Over random legs on a stream with a 2.5 s sample gap: the clause admits a leg exactly
        when stage 2 integrates every cut of it, and refuses the legs that rule 4 alone admits across the gap."""
        from joulewise.cadence_looks import inclusion_34 as I34
        from joulewise.cadence_looks import time_fields as TF
        import random
        rng = random.Random(11)
        with tempfile.TemporaryDirectory() as d:
            m, path = self.stream(d, empty=lambda x: self.T0 + 120 <= x < self.T0 + 121.5)
            sm = TF.SpanMeter(d)
            self.assertEqual(sm.t, m.t)                       # the time reader's times are the decoder's
            st = I34.read_meter_stream(path)
            n_legs = n_refused_by_rule4 = n_clause = 0
            for _ in range(60):
                A = self.T0 + rng.uniform(-5, 150)
                B = A + rng.uniform(10, 60)
                iv = (round(A * 1e9), round(B * 1e9))
                r4 = I34.rule4(iv, [st])
                if not (r4["max_gap_s"] is not None and r4["max_gap_s"] <= 2.0):
                    n_refused_by_rule4 += 1
                    continue
                turn = {"segments": [{"wall_start_s": A, "wall_end_s": B}], "prefix_tails": []}
                dc = R.trace_holes(turn, Path(d) / "no-bundle", sm, None)["dc_in"]
                try:
                    m.energy(A, B)
                    stage2_ok = True
                except F.LookInputError:
                    stage2_ok = False
                self.assertEqual(not dc["excluded"], stage2_ok, (A - self.T0, B - self.T0, dc))
                if dc["excluded"]:
                    n_clause += 1
                    continue
                n_legs += 1
                cuts = sorted([A, B] + [rng.uniform(A, B) for _ in range(6)])
                for a, b in zip(cuts, cuts[1:]):
                    m.energy(a, b)                                     # must not refuse
            self.assertGreater(n_legs, 15)
            self.assertGreater(n_refused_by_rule4, 0)
            self.assertGreater(n_clause, 0)          # legs rule 4 admits whose start sits in the 2.5 s sample gap


ENERGY_FILES = ("power_trace.csv", "/hazards/meter/stream-", "en.json", "segment_energy.json")


def energy_opens(opened):
    return [p for p in opened if any(m in p.replace(os.sep, "/") for m in ENERGY_FILES)]


class RoundThree(unittest.TestCase):
    """Mythos round 3 (on 553e4cf00): N1, N2, N6 (above), N7, N10, N11 in this package's files."""

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.d = tempfile.mkdtemp(prefix="jw-look-r3-")
        cls.ep = os.path.join(cls.d, "en.json")
        wb(cls.ep, synth.dump(cls.c.en))
        cls.ip = os.path.join(cls.d, "li.json")
        wb(cls.ip, synth.dump(cls.c.li))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def stage1_custody(self, man=None):
        p = os.path.join(self.d, f"s1-{len(os.listdir(self.d))}.json")
        argv = ["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root), "--rules-3-4",
                self.c.paths["rules_3_4.json"], "--out", p]
        if man:
            argv += ["--manifest", man, "--allow-draft"]
        rc, out, err = run_cli(argv)
        self.assertEqual(rc, 0, err)
        return p, R.sha256_file(p)

    def test_n1_allow_draft_refuses_custody_whose_receipts_are_not_synthetic(self):
        p, h = self.stage1_custody()
        sid = self.c.li["spans"][0]["span_id"]
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / sid
            shutil.copytree(self.c.root / sid, sdir)
            rec = rj(sdir / "runner_receipt.json")
            rec.pop("synthetic")                          # as a real runner's receipt is
            wb(sdir / "runner_receipt.json", json.dumps(rec))
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", p, "--stage1-sha256", h, "--custody", str(self.c.root),
                                      "--span-dir", f"{sid}={sdir}", "--out", os.path.join(d, "o.json")])
            # RL-194: stage 2 runs under the pins stage 1 ran under, so the changed receipt is refused by its pin
            # first; behind the pins, the synthetic-only check still refuses it (Mythos r3 N1)
            self.assertEqual(rc, 2)
            self.assertIn("runner_receipt.json: its bytes are not its pin", err)
            self.assertEqual(energy_opens(opened), [])
            with self.assertRaisesRegex(F.LookInputError, "synthetic custody only"):
                R.synthetic_custody_only(rj(p), LF.span_dirs(self.c.root, [f"{sid}={sdir}"]))

    def test_n2_another_manifest_refuses_before_energy(self):
        p, h = self.stage1_custody()
        other = pinned_manifest(lambda doc: doc.update(title=doc["title"] + " (another draft)"))
        with spy_opens() as opened:
            rc, _, err = run_cli(["stage2", "--stage1", p, "--stage1-sha256", h, "--custody", str(self.c.root),
                                  "--out", os.path.join(self.d, "o2.json"), "--manifest", other, "--allow-draft"])
        self.assertEqual(rc, 2)
        self.assertIn("another manifest", err)
        self.assertEqual(energy_opens(opened), [])

    def test_n2_a_draft_stage1_file_refused_without_allow_draft_before_energy(self):
        p, h = self.stage1_custody()
        doc = rj(p)
        self.assertIs(doc["allow_draft"], True)
        a = R.argparse.Namespace(allow_draft=False, custody=str(self.c.root), span_dir=None)
        R._VERIFIED[:] = [(rj(_DEFAULT_MANIFEST[0]), _DEFAULT_MANIFEST[0])]
        with spy_opens() as opened:
            with self.assertRaisesRegex(F.LookInputError, "made under --allow-draft"):
                R.stage2_energy_preflight(doc, a)
        self.assertEqual(energy_opens(opened), [])

    def test_n2_a_missing_pin_refuses_before_energy(self):
        """A module the stages load that the manifest does not pin refuses before any energy file opens. Since RL-173
        E.1 stage 1 loads the meter decoder's closure too (the time reader runs its unwrap and clock fit), so a
        missing pin on it refuses stage 1 as well; stage 2, given a stage-1 file stamped with that manifest, refuses
        before energy."""
        p, h = self.stage1_custody()

        def drop_dependency(doc):              # a module of the meter decoder's closure
            doc["fit"]["dependencies"] = [x for x in doc["fit"]["dependencies"]
                                          if x["path"] != "joulewise/desk_restore.py"]
        man = pinned_manifest(drop_dependency)
        out = os.path.join(self.d, "s1-unpinned.json")
        rc, _, err = run_cli(["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                              "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", out, "--manifest", man,
                              "--allow-draft"])
        self.assertEqual(rc, 2)
        self.assertIn("joulewise/desk_restore.py (not pinned)", err)
        self.assertFalse(os.path.exists(out))
        doc = rj(p)
        # the stage-1 file stamped with the manifest the executor will be given (the harness sets its root and pins)
        doc["manifest_sha256"] = hashlib.sha256(placed_manifest_bytes(
            ["stage2", "--stage1", p, "--custody", str(self.c.root), "--manifest", man])).hexdigest()
        q = os.path.join(self.d, "s1-other-manifest.json")
        wb(q, F.dump(doc))
        with spy_opens() as opened:
            rc, _, err = run_cli(["stage2", "--stage1", q, "--stage1-sha256", R.sha256_file(q), "--custody",
                                  str(self.c.root), "--out", os.path.join(self.d, "o3.json"), "--manifest", man,
                                  "--allow-draft"])
        self.assertEqual(rc, 2)
        self.assertIn("desk_restore.py", err)
        self.assertEqual(energy_opens(opened), [])

    def test_n2_step3_module_flag_is_gone(self):
        rc, _, err = run_cli(["stage2", "--stage1", "x", "--stage1-sha256", "0" * 64, "--custody", "x",
                              "--step3-module", "x"])
        self.assertEqual(rc, 2)
        self.assertIn("unrecognized arguments", err)

    def test_n7_gpu_hole_switch(self):
        """Off by default (integrates the rows present); on, a segment with an uncovered stretch over max_gap_s
        refuses. The rule itself is the research lead's (Q-gpu-hole)."""
        self.assertIsNone(R.gpu_gap_rule({"fit": {}}))
        self.assertIsNone(R.gpu_gap_rule({"fit": {"gpu_trace_hole_refusal": {"enabled": False}}}))
        self.assertEqual(R.gpu_gap_rule({"fit": {"gpu_trace_hole_refusal": {"enabled": True, "max_gap_s": 2}}}), 2.0)
        s1 = F.stage1(self.c.li, "0" * 64)
        L = next(x for x in s1["legs"] if x["in_energy_fit"])
        a = L["segments"][3]["wall_start_s"]
        sdir = self.c.root / L["span_id"]
        rec = rj(sdir / "legs" / L["leg_id"] / "leg_record.json") if "leg_id" in L else \
            rj(sdir / "legs" / L["leg_key"].split("/")[1] / "leg_record.json")
        with tempfile.TemporaryDirectory() as d:
            copy_dir = Path(d) / L["span_id"]
            shutil.copytree(sdir, copy_dir)
            pt = copy_dir / "legs" / L["leg_key"].split("/")[1] / "runtime" / rec["result"]["bundle"] / "power_trace.csv"
            lines = pt.read_text().splitlines()
            keep = [lines[0]] + [r for r in lines[1:] if not (r.split(",")[3] == "gpu_power"
                                                             and a + 1 <= float(r.split(",")[4]) < a + 7)]
            pt.write_text("\n".join(keep) + "\n")
            only = {k: v for k, v in s1.items()}
            only["legs"] = [x if x["leg_key"] == L["leg_key"] else dict(x, in_energy_fit=False) for x in s1["legs"]]
            sdir_of = LF.span_dirs(self.c.root, [f"{L['span_id']}={copy_dir}"])
            R.read_segment_energy(only, sdir_of)                     # default: integrates
            R.read_segment_energy(only, sdir_of, gpu_max_gap_s=10.0)  # a 6 s hole under a 10 s bound: integrates
            with self.assertRaisesRegex(F.LookInputError, "GPU rail"):
                R.read_segment_energy(only, sdir_of, gpu_max_gap_s=2.0)

    def test_n10_stale_bytecode_beside_a_pinned_source_is_not_run(self):
        """A cached fit_interim built from a copy with QUALIFIED_THRESHOLD = 0.92, unchecked-hash (Python would run
        it whatever the source says), sits in __pycache__ of a copy of the tree. The copy's CLI runs and prints the
        pinned source's 0.02."""
        import importlib.util
        import py_compile
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            copy_bytecode_fixture(root)
            src = root / "joulewise/cadence_looks/fit_interim.py"
            bad = root / "bad_fit.py"
            bad.write_text(src.read_text().replace("QUALIFIED_THRESHOLD = 0.02", "QUALIFIED_THRESHOLD = 0.92"))
            cfile = importlib.util.cache_from_source(str(src))
            py_compile.compile(str(bad), cfile=cfile, dfile=str(src),
                               invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
            self.assertTrue(os.path.exists(cfile))
            man = pinned_manifest()
            s1p, op = root / "s1.json", root / "o.json"
            cli = str(root / "scripts/cadence_look_run.py")
            # the copy's own manifest registers the look's root; the level-R input is at its fixed place
            placed = LF.place(["stage1", "--input", self.ip, "--out", s1p, "--manifest", man, "--allow-draft"],
                              repo=root)
            (root / M.INTERIM_MANIFEST_PATH).write_text(json.dumps(placed.manifest, indent=2), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", "-B", cli, *placed.argv], capture_output=True, text=True, cwd=d)
            placed.collect()
            self.assertEqual(r.returncode, 0, r.stderr)
            h = R.sha256_file(s1p)
            rc, _, err = _cli_subprocess(["stage2", "--stage1", s1p, "--stage1-sha256", h, "--energy", self.ep,
                                             "--out", op, "--manifest", man, "--allow-draft",
                                             "--looks", looks_file(h)], repo=root)
            self.assertEqual(rc, 0, err + LAST_RUN.get("private_stderr", ""))
            self.assertEqual(rj(op)["qualified_interim_half"]["threshold"], 0.02)

    def test_n10_guard_refuses_a_module_with_a_cache_file(self):
        import types
        with tempfile.TemporaryDirectory() as d:
            fake = types.ModuleType("jw_fake_cached")
            fake.__file__ = str(R.ROOT / "joulewise" / "fake_cached.py")
            fake.__cached__ = os.path.join(d, "fake_cached.pyc")
            Path(fake.__cached__).write_bytes(b"")
            import sys
            sys.modules["jw_fake_cached"] = fake
            try:
                with self.assertRaisesRegex(F.LookInputError, "cached bytecode"):
                    R._check_sources()
            finally:
                del sys.modules["jw_fake_cached"]

    def test_n11_a_headerless_stream_is_not_decoded(self):
        sid = self.c.li["spans"][0]["span_id"]
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / sid
            shutil.copytree(self.c.root / sid, sdir, ignore=shutil.ignore_patterns("power_trace.csv"))
            p = sdir / "hazards/meter/stream-0001.jsonl"
            lines = p.read_text().splitlines()
            bad = '{"k":"b","tx":1,"rx":2,"rt":3,"n":2,"p":"zz-not-hex' + "\n"   # not even JSON
            p.write_text(bad + "\n".join(lines[2:]) + "\n")             # header gone; first line a sample line
            sm, why = R.span_meter(sdir)
            self.assertIsNone(why)
            header, end = R.meter_offsets(sm)
        self.assertIsNone(header)
        self.assertIsNotNone(end)                      # the poll lines still carry rx and rt
        self.assertFalse(any(t["present"] for t in sm.times))      # no header: no sample is decoded


class LegBracket(unittest.TestCase):
    """Mythos r3 N6 as RL-173 E.1 settles it: an energy-fit interval not bracketed by DECODED meter samples is
    excluded in stage 1 by rule 4's DC-in clause (named, with its reason), and stage 2's reader refuses it as the
    backstop, naming the leg. The stream here stops 1.2 s before the leg's last interval ends (rule 4 may admit it)."""

    def test_stream_ending_before_the_last_token(self):
        c = _Custody.get()
        s1 = c.s1_custody()
        sid = "dev-01-s02"
        L = [x for x in s1["legs"] if x["in_energy_fit"] and x["span_id"] == sid][-1]
        end = max(x["wall_end_s"] for x in L["segments"] + L["prefix_tails"])
        entry = next(e for e in rj(c.paths["roster.json"]) if e["span_id"] == sid)
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / sid
            shutil.copytree(c.root / sid, sdir)
            p = sdir / "hazards/meter/stream-0001.jsonl"
            lines = p.read_text().splitlines()
            keep = [lines[0]] + [x for x in lines[1:-1] if json.loads(x)["rt"] / 1e9 <= end - 1.2] + [lines[-1]]
            p.write_text("\n".join(keep) + "\n")
            _, legs = R.read_span(sdir, entry, rj(c.paths["rules_3_4.json"]), R.FAN_KEYS)
            got = next(x for x in legs if x["leg_key"] == L["leg_key"])
            dc = got["trace_holes"]["dc_in"]
            self.assertEqual((dc["excluded"], dc["bracketed"]), (True, False))
            self.assertEqual(dc["reason"], "an energy-fit interval not bracketed by decoded meter samples")
            self.assertFalse(got["inclusion"]["km003c_clean"])
            self.assertTrue(got["inclusion"]["sidecar_coverage"])
            sdir_of = LF.span_dirs(c.root, [f"{sid}={sdir}"])
            only = dict(s1, legs=[x if x["leg_key"] == L["leg_key"] else dict(x, in_energy_fit=False)
                                  for x in s1["legs"]])
            with self.assertRaisesRegex(F.LookInputError, f"DC-in: {L['leg_key']}: .*not bracketed"):
                R.read_segment_energy(only, sdir_of)
        R.stage2_preflight(s1, LF.span_dirs(c.root, None))      # the intact custody passes


class RoundFour(unittest.TestCase):
    """Sol r4 NEW-3 (the stage-1 file's schema and provenance, before energy) and Mythos r4 N7's survivors."""

    @classmethod
    def setUpClass(cls):
        cls.c = _Custody.get()
        cls.d = tempfile.mkdtemp(prefix="jw-look-r4-")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def stage1(self):
        p = os.path.join(self.d, f"s1-{len(os.listdir(self.d))}.json")
        rc, _, err = run_cli(["stage1", "--roster", self.c.paths["roster.json"], "--custody", str(self.c.root),
                              "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", p])
        self.assertEqual(rc, 0, err)
        return p

    def test_new3_defective_stage1_files_refuse_before_energy(self):
        p = self.stage1()
        good = rj(p)
        cases = {"omit": lambda d: d["code_sha256"].pop("joulewise/schemas.py"),
                 "zero": lambda d: d["code_sha256"].update({"joulewise/schemas.py": "0" * 64}),
                 "extra_file": lambda d: d["code_sha256"].update({"joulewise/suite.py": "0" * 64}),
                 "unknown_field": lambda d: d.update(per_leg_joules={"dev-01-s01/L001": 1.0})}
        for name, mutate in cases.items():
            doc = copy.deepcopy(good)
            mutate(doc)
            q = os.path.join(self.d, f"bad-{name}.json")
            wb(q, F.dump(doc))
            with spy_opens() as opened:
                rc, _, err = run_cli(["stage2", "--stage1", q, "--stage1-sha256", R.sha256_file(q), "--custody",
                                      str(self.c.root), "--out", os.path.join(self.d, f"o-{name}.json")])
            self.assertEqual(rc, 2, name)
            self.assertIn("stage-1 file", err, name)
            self.assertEqual(energy_opens(opened), [], name)
        # the unmodified file passes the same check
        rc, _, err = run_cli(["stage2", "--stage1", p, "--stage1-sha256", R.sha256_file(p), "--custody",
                              str(self.c.root), "--out", os.path.join(self.d, "o-good.json")])
        self.assertEqual(rc, 0, err)

    def test_n7_stage1_inputs_gate_refuses_an_unnamed_verdict_file(self):
        """Committed mode on look_minirepo: the ledger names the roster and one verdict file; stage 1 given another
        verdict file refuses before custody opens."""
        from tests.cadence import look_minirepo as mr
        mini = mr.mini_repo(self)
        roster_sha, verdicts_sha = R.sha256_file(self.c.paths["roster.json"]), R.sha256_file(self.c.paths["rules_3_4.json"])
        mr.commit(mini, roster_sha256=roster_sha, verdicts_sha256=verdicts_sha)
        other = os.path.join(self.d, "other-verdicts.json")
        v = rj(self.c.paths["rules_3_4.json"])
        first = next(iter(v))
        v[first] = {"sidecar_coverage": False, "km003c_clean": False}
        wb(other, json.dumps(v))
        out = os.path.join(self.d, "mini-s1.json")
        r = mr.py(mini, "scripts/cadence_look_run.py", "stage1", "--roster", self.c.paths["roster.json"],
                  "--custody", self.c.root, "--rules-3-4", other, "--out", out, "--manifest", mini / mr.MANIFEST)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("verdict", r.stderr)
        self.assertFalse(os.path.exists(out))
        r = mr.py(mini, "scripts/cadence_look_run.py", "stage1", "--roster", self.c.paths["roster.json"],
                  "--custody", self.c.root, "--rules-3-4", self.c.paths["rules_3_4.json"], "--out", out,
                  "--manifest", mini / mr.MANIFEST)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_n7_cached_bytecode_refused_through_the_cli(self):
        """A repository module that was loaded from a cache file before the CLI set its fresh prefix (here: a
        wrapper outside the repository imports fit_interim from a valid __pycache__ entry, then runs main) makes
        the stage refuse."""
        import py_compile
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "tree"
            copy_bytecode_fixture(root)
            py_compile.compile(str(root / "joulewise/cadence_looks/fit_interim.py"), doraise=True)
            ip = Path(d) / "li.json"
            wb(ip, synth.dump(self.c.li))
            wrapper = Path(d) / "wrap.py"
            wrapper.write_text("import sys\nsys.path.insert(0, %r)\n"
                               "import joulewise.cadence_looks.fit_interim\n"      # from __pycache__
                               "from scripts import cadence_look_run as R\n"
                               "sys.exit(R.main(sys.argv[1:]))\n" % str(root))
            # the copy's own manifest registers the look's root and the level-R input is at its fixed place
            placed = LF.place(["stage1", "--input", ip, "--out", Path(d) / "s1.json", "--manifest", pinned_manifest(),
                               "--allow-draft"], repo=root)
            (root / M.INTERIM_MANIFEST_PATH).write_text(json.dumps(placed.manifest, indent=2), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(wrapper), *placed.argv],
                               capture_output=True, text=True, cwd=d)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("cached bytecode", r.stderr)


class GpuSwitchOn(unittest.TestCase):
    """Mythos r4 N5 under RL-173 E.1: the manifest keeps fit.gpu_trace_hole_refusal on at 2 s (the backstop). A 6 s
    hole in one leg's power_trace.csv is now excluded in stage 1 by rule 3's GPU clause, so stage 2 runs (exit 0)
    without that leg; the backstop itself is exercised in tests/cadence/test_time_fields.py on a hand-built stage 1."""

    def test_stage2_with_the_switch_on(self):
        c = _Custody.get()
        self.assertEqual(R.gpu_gap_rule(rj(MANIFEST)), 2.0)                # on in the checked-in manifest
        s1 = c.s1_custody()
        L = next(x for x in s1["legs"] if x["in_energy_fit"])
        lid = L["leg_key"].split("/")[1]
        a = L["segments"][3]["wall_start_s"]
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / L["span_id"]
            shutil.copytree(c.root / L["span_id"], sdir)
            rec = rj(sdir / "legs" / lid / "leg_record.json")
            pt = sdir / "legs" / lid / "runtime" / rec["result"]["bundle"] / "power_trace.csv"
            lines = pt.read_text().splitlines()
            pt.write_text("\n".join([lines[0]] + [r for r in lines[1:] if not (
                r.split(",")[3] == "gpu_power" and a + 1 <= float(r.split(",")[4]) < a + 7)]) + "\n")
            p1 = os.path.join(d, "s1.json")
            rc, _, err = run_cli(["stage1", "--roster", c.paths["roster.json"], "--custody", str(c.root),
                                  "--rules-3-4", c.paths["rules_3_4.json"], "--span-dir", f"{L['span_id']}={sdir}",
                                  "--out", p1])
            self.assertEqual(rc, 0, err)
            got = next(x for x in rj(p1)["legs"] if x["leg_key"] == L["leg_key"])
            self.assertEqual((got["in_energy_fit"], got["inclusion"]["sidecar_coverage"]), (False, False))
            self.assertTrue(got["trace_holes"]["gpu_rail"]["excluded"])
            self.assertGreater(got["trace_holes"]["gpu_rail"]["max_gap_s"], 5.9)
            self.assertEqual(rj(p1)["counts"]["excluded_by_trace_clause"]["gpu_rail"], 1)
            o = os.path.join(d, "o.json")
            rc, _, err = run_cli(["stage2", "--stage1", p1, "--stage1-sha256", R.sha256_file(p1), "--custody",
                                  str(c.root), "--span-dir", f"{L['span_id']}={sdir}", "--out", o])
            self.assertEqual(rc, 0, err)
            self.assertTrue(os.path.exists(o))
