"""D-188 LEAF-CLI: environment_admission's thermal scan, memo-first without reordering refusals.

``_window_thermal_pressure_refusals`` reads the idle plist, parses it, then
reads the measured plist; a failing idle parse refuses before that second
read (Sol #10). Inside an analysis run the idle parse is deferred past the
second read only when the run already parsed the same idle bytes under the
same anchor successfully. These tests compare every outcome (value, or
exception type and text), the read order and the V2 session records with the
store-free serial scan, on the committed synthetic S10 ALPHA member.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest import mock

from joulewise import analysis_run_cache as arc
from joulewise import authentication_io as aio
from joulewise import environment_admission as ea
from joulewise.adapters import powermetrics as pm
from joulewise.bundle_read import BundleReader
from tests.b5_analysis.test_shared_physics_cache import ARCHIVE, MEMBER
from tests.hazards import refusal_census


def outcome(fn, *args, **kwargs):
    try:
        return ("value", fn(*args, **kwargs))
    except Exception as exc:  # noqa: BLE001 - compared, never swallowed
        return ("raised", type(exc).__name__, str(exc))


def records(session):
    return {identity: (record.sha256, record.grammar, record.read_count)
            for identity, record in session.records.items()}


class MemoFirst(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="env-memo-first-"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, ignore_errors=True)
        with tarfile.open(ARCHIVE) as blob:
            blob.extractall(cls.tmp / "source",
                            members=[m for m in blob.getmembers() if m.name.startswith(MEMBER)], filter="data")
        cls.pristine = cls.tmp / "source" / MEMBER
        cls.metadata = json.loads((cls.pristine / "metadata.json").read_bytes())
        attempt = cls.metadata["environment_admission"]["attempts"][-1]["attempt"]
        cls.idle_name = "powermetrics_idle.plist" if attempt == 1 else f"powermetrics_idle_attempt_{attempt}.plist"
        window = BundleReader(cls.pristine).measured_window()
        cls.window = (window.start_s, window.end_s)

    def copy(self, label, *, bad_idle=False, no_raw=False, raw_suffix=b""):
        target = self.tmp / label / self.pristine.name
        shutil.copytree(self.pristine, target)
        self.addCleanup(shutil.rmtree, target.parent, ignore_errors=True)
        if bad_idle:
            (target / "raw" / self.idle_name).write_bytes(b"not a powermetrics plist stream\0")
        if no_raw:
            (target / "raw/powermetrics.plist").unlink()
        if raw_suffix:
            raw = target / "raw/powermetrics.plist"
            raw.write_bytes(raw.read_bytes() + raw_suffix)
        return target

    def scan(self, bundle):
        return ea._window_thermal_pressure_refusals(
            self.metadata, bundle_path=bundle,
            measured_window_start_s=self.window[0], measured_window_end_s=self.window[1])

    def traced(self):
        """Patch the two reads and the plist parse; return the event list."""

        events: list[str] = []
        read, parse = ea.read_authentication_input, pm.parse_powermetrics_records

        def traced_read(path, **kwargs):
            events.append("read:" + Path(path).name)
            return read(path, **kwargs)

        def traced_parse(data, **kwargs):
            events.append("parse:" + ("idle" if "timestamp_anchor_s" in kwargs else "raw"))
            return parse(data, **kwargs)

        self.addCleanup(mock.patch.stopall)
        mock.patch.object(ea, "read_authentication_input", traced_read).start()
        mock.patch.object(pm, "parse_powermetrics_records", traced_parse).start()
        return events

    def test_every_combination_has_the_serial_outcome(self):
        variants = {
            "good": {},
            "bad-idle": {"bad_idle": True},
            "no-raw": {"no_raw": True},
            "bad-idle-no-raw": {"bad_idle": True, "no_raw": True},
            "other-raw": {"raw_suffix": b"\0"},
        }
        bundles = {label: self.copy(label, **options) for label, options in variants.items()}
        serial = {label: outcome(self.scan, bundle) for label, bundle in bundles.items()}
        self.assertEqual(serial["good"], ("value", ()))
        self.assertEqual(serial["bad-idle"], ("value", ("environment_admission_missing",)))
        self.assertEqual(serial["no-raw"], ("value", ("environment_admission_missing",)))
        # Cold run, warm run (the good idle bytes known before every variant), and repeats.
        for warm in (False, True):
            with self.subTest(warm=warm), arc.analysis_run_caches({}):
                if warm:
                    self.assertEqual(outcome(self.scan, bundles["good"]), serial["good"])
                for label, bundle in bundles.items():
                    for repeat in range(2):
                        self.assertEqual(outcome(self.scan, bundle), serial[label], (label, repeat))
                idle_successes = arc.memo(ea._IDLE_PARSE_SUCCESS_MEMO)
                self.assertEqual(len(idle_successes), 1, "only the good idle bytes ever succeed")

    def test_bad_idle_never_reads_a_changed_registered_plist(self):
        """Sol #10: bad idle bytes refuse before the measured-plist read, in every run state."""

        bundle = self.copy("registered", bad_idle=True)
        raw = bundle / "raw/powermetrics.plist"

        def session_scan():
            with aio.V2AuthenticationReadSession() as session:
                aio.read_authentication_input(raw, grammar="raw", label="registered first")
                raw.write_bytes(original + b"\0")  # the first digest is now stale
                try:
                    return outcome(self.scan, bundle), records(session)
                finally:
                    raw.write_bytes(original)

        original = raw.read_bytes()
        serial = session_scan()
        self.assertEqual(serial[0], ("value", ("environment_admission_missing",)))
        good = self.copy("registered-good")
        with arc.analysis_run_caches({}):
            self.assertEqual(outcome(self.scan, good), ("value", ()))  # good idle known; this one is bad
            self.assertEqual(session_scan(), serial)
            self.assertEqual(session_scan(), serial)

    def test_known_good_idle_and_a_changed_registered_plist_raise_as_serially(self):
        bundle = self.copy("known-good")
        raw = bundle / "raw/powermetrics.plist"
        original = raw.read_bytes()

        def session_scan():
            with aio.V2AuthenticationReadSession() as session:
                aio.read_authentication_input(raw, grammar="raw", label="registered first")
                raw.write_bytes(original + b"\0")
                try:
                    return outcome(self.scan, bundle), records(session)
                finally:
                    raw.write_bytes(original)

        serial = session_scan()
        self.assertEqual(serial[0][:2], ("raised", "V2AuthenticationInputError"))
        with arc.analysis_run_caches({}):
            self.assertEqual(outcome(self.scan, bundle), ("value", ()))  # idle parse succeeded once
            self.assertEqual(session_scan(), serial)

    def test_read_and_parse_order(self):
        good, other = self.copy("order"), self.copy("order-other", raw_suffix=b"\0")
        serial_order = ["read:" + self.idle_name, "parse:idle", "read:powermetrics.plist", "parse:raw", "parse:raw"]
        events = self.traced()
        self.scan(good)
        self.assertEqual(events, serial_order)
        with arc.analysis_run_caches({}):
            events.clear()
            self.scan(good)
            self.assertEqual(events, serial_order, "a cold run parses in the serial order")
            events.clear()
            self.assertEqual(self.scan(good), ())
            self.assertEqual(events, ["read:" + self.idle_name, "read:powermetrics.plist"],
                             "a scan-memo hit after a known idle success parses nothing")
            events.clear()
            self.scan(other)
            self.assertEqual(events, ["read:" + self.idle_name, "read:powermetrics.plist",
                                      "parse:idle", "parse:raw", "parse:raw"],
                             "a scan-memo miss parses the known idle bytes after the second read")
        with arc.analysis_run_caches({}):
            bad = self.copy("order-bad", bad_idle=True)
            events.clear()
            self.assertEqual(self.scan(bad), ("environment_admission_missing",))
            self.assertEqual(events, ["read:" + self.idle_name, "parse:idle"],
                             "a failing idle parse refuses before the measured-plist read")
            self.assertEqual(arc.memo(ea._IDLE_PARSE_SUCCESS_MEMO), {})

    def test_outside_a_run_nothing_is_memoized(self):
        self.assertEqual(ea._idle_parse_success_key(b"x", 1.0), (None, None))

    def test_raise_sites_and_guards_unchanged(self):
        document = refusal_census.load_allowlist()
        listed = {(e["function"], e["kind"], e["detail"]): (e["count"], e["guard"]) for e in document["sites"]
                  if e["file"] == "joulewise/environment_admission.py"}
        sites = refusal_census.scan(["joulewise/environment_admission.py"])
        observed = refusal_census.site_counts(sites)
        guards = refusal_census.site_guards(sites)
        self.assertEqual({key[1:4]: (count, guards[key]) for key, count in observed.items()}, listed)
        thermal = {key: value for key, value in listed.items() if key[0] == "_window_thermal_pressure_refusals"}
        self.assertEqual({value[1][:8] for value in thermal.values()}, {"d51ac85e", "a72ee857", "465555e8"})


if __name__ == "__main__":
    unittest.main()
