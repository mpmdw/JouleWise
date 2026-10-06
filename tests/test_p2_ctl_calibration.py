"""Gate-prune round 2, lane P2-CTL (PLAN2 section 3.1): calibration items.

- M1/M2: the member reads the window calibration verdict (J1).  On a full
  digest match it skips its own refit; on any miss it refits and flags
  ``calibration.refit_cache_miss``, never refuses.  Either way the child
  reduce is seeded with the verified bound instead of a second refit.
- t1-06: the calibration copy is clone-installed with a byte-copy fallback,
  and the installed copy is re-hashed.

Every faster path is paired with its legacy twin (unchanged) and its keeper
(a refit that does not reproduce the physics still refuses).
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise import calibration_bracketing, controller, powermetrics_fiducial
from joulewise.flags import core as flags_core
from joulewise.schemas import RunStatus
from tests.test_controller_hazard_flags import (
    WRITER,
    load_attachment,
    read_flags,
    run_window_member,
)
from tests.test_window_lineage import EVIDENCE, build_window


VERDICT_BASENAME = "window_calibration_verdict.json"
VERDICT_SCHEMA = "joulewise.window_calibration_verdict.v1"
_EFFECTIVE_BOUND: list[float] = []


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def effective_bound(capture: Path) -> float:
    """The real refit of the fixture capture, computed once per process."""

    if not _EFFECTIVE_BOUND:
        _EFFECTIVE_BOUND.append(powermetrics_fiducial.verify_stored_evidence_physics(
            EVIDENCE, (capture / "raw/powermetrics.plist").read_bytes(),
            (capture / "events.jsonl").read_bytes()))
    return _EFFECTIVE_BOUND[0]


def write_verdict(capture: Path, **overrides: Any) -> Path:
    """J1 as PLAN2 section 3.2 specifies it, for the fixture's pre-slot capture."""

    verdict = {
        "schema": VERDICT_SCHEMA,
        "evidence_sha256": sha256((capture / "instrument_evidence.json").read_bytes()),
        "manifest_sha256": sha256((capture / "manifest.json").read_bytes()),
        "raw_plist_sha256": sha256((capture / "raw/powermetrics.plist").read_bytes()),
        "events_sha256": sha256((capture / "events.jsonl").read_bytes()),
        "estimator_files_sha256": calibration_bracketing._current_estimator_code_sha256(),
        "effective_b_fiducial_s": effective_bound(capture),
        "flags": [],
    }
    verdict.update(overrides)
    path = capture.parent / VERDICT_BASENAME
    path.write_text(json.dumps(verdict, sort_keys=True))
    return path


class CountingRefit:
    """Count real refits (the estimator's raw-plist re-derivation)."""

    def __init__(self) -> None:
        self.calls = 0
        self._real = powermetrics_fiducial.rederive_detection_from_artifacts

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return self._real(*args, **kwargs)

    def patch(self):
        return patch.object(powermetrics_fiducial, "rederive_detection_from_artifacts", side_effect=self)


class StubVerify:
    """A stand-in for the 13 s refit where only the routing is under test."""

    def __init__(self, result: float | None = None, error: Exception | None = None) -> None:
        self.calls = 0
        self._result = result
        self._error = error

    def __call__(self, evidence: Any, *_args: Any) -> float:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._result if self._result is not None else float(evidence["b_fiducial_s"])

    def patch(self):
        return patch.object(powermetrics_fiducial, "verify_stored_evidence_physics", side_effect=self)


class _WindowCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.w = build_window(Path(tmp.name))
        self.custody = self.w.custody
        self.hazard = flags_core.hazard_flag_context(self.w.claim, writer=WRITER)
        self.assertIsNotNone(self.hazard)

    def flags(self, code: str) -> list[dict[str, Any]]:
        return [flag for flag in read_flags(self.custody) if flag["code"] == code]


# ---------------------------------------------------------------------------
# M1 / M2: the window calibration verdict (J1) and the reduce seed


class WindowVerdictMemberTests(_WindowCase):
    def test_full_match_runs_no_refit_and_no_flag(self) -> None:
        write_verdict(self.w.capture)
        refit = CountingRefit()
        with refit.patch():
            bundle, summary = run_window_member(self.w)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(refit.calls, 0, "a matching window verdict replaces the member's refit")
        self.assertEqual(self.flags("calibration.refit_cache_miss"), [])
        metadata = json.loads((bundle / "metadata.json").read_bytes())
        self.assertEqual(metadata["instrument_calibration"]["verified_effective_b_fiducial_s"],
                         effective_bound(self.w.capture))

    def test_absent_verdict_refits_once_and_flags_the_member(self) -> None:
        refit = CountingRefit()
        with refit.patch():
            bundle, summary = run_window_member(self.w)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertEqual(refit.calls, 1)
        flags = self.flags("calibration.refit_cache_miss")
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["scope"]["level"], "member")
        self.assertEqual(flags[0]["scope"]["run_id"], bundle.name)
        value = flags[0]["observed"]
        value = value.get("value", value) if value.get("scope_unresolved") else value
        self.assertEqual(value, {"reason": "verdict_absent"})

    def test_reduce_is_seeded_with_the_verified_bound(self) -> None:
        write_verdict(self.w.capture)
        seen: list[dict[str, Any]] = []
        real_reduce = controller.reduce_module.reduce_bundle

        def recording(path, **kwargs):
            seen.append(dict(kwargs))
            return real_reduce(path, **kwargs)

        with patch.object(controller.reduce_module, "reduce_bundle", side_effect=recording):
            _bundle, summary = run_window_member(self.w)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        evidence_sha = sha256((self.w.capture / "instrument_evidence.json").read_bytes())
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].get("_instrument_calibration_physics_cache"),
                         {evidence_sha: effective_bound(self.w.capture)})

    def test_miss_with_unreproducible_physics_still_refuses(self) -> None:
        # Keeper: a cache miss falls back to the refit, and a failed refit refuses.
        write_verdict(self.w.capture, events_sha256="0" * 64)
        with StubVerify(error=ValueError("stored pulse residual does not contain the refit")).patch():
            with self.assertRaisesRegex(ValueError, "does not reproduce the raw physics"):
                run_window_member(self.w)
        self.assertFalse((self.w.claim / "hazard-member").exists())


class WindowVerdictRoutingTests(_WindowCase):
    """Which verdicts count as a hit; the refit is stubbed (routing only)."""

    def attach(self, *, hazard: Any) -> tuple[Any, StubVerify]:
        stub = StubVerify()
        with stub.patch():
            attachment = load_attachment(self.w, hazard=hazard)
        return attachment, stub

    def test_each_digest_field_mismatch_is_a_miss(self) -> None:
        for field in ("evidence_sha256", "manifest_sha256", "raw_plist_sha256", "events_sha256"):
            with self.subTest(field):
                write_verdict(self.w.capture, **{field: "f" * 64})
                attachment, stub = self.attach(hazard=self.hazard)
                self.assertEqual(stub.calls, 1)
                self.assertEqual(attachment.refit_cache_miss,
                                 {"reason": "digest_mismatch", "fields": [field]})

    def test_estimator_code_change_is_a_miss(self) -> None:
        estimator = dict(calibration_bracketing._current_estimator_code_sha256())
        estimator["joulewise/powermetrics_fiducial.py"] = "e" * 64
        write_verdict(self.w.capture, estimator_files_sha256=estimator)
        attachment, stub = self.attach(hazard=self.hazard)
        self.assertEqual(stub.calls, 1)
        self.assertEqual(attachment.refit_cache_miss["fields"], ["estimator_files_sha256"])

    def test_narrower_bound_schema_and_malformed_verdicts_are_misses(self) -> None:
        stored = float(EVIDENCE["b_fiducial_s"])
        cases = {
            "verdict_bound_invalid": {"effective_b_fiducial_s": stored - 1e-3},
            "verdict_schema_mismatch": {"schema": "joulewise.window_calibration_verdict.v0"},
            "verdict_malformed": {"flags": None},
        }
        for reason, overrides in cases.items():
            with self.subTest(reason):
                write_verdict(self.w.capture, **overrides)
                attachment, stub = self.attach(hazard=self.hazard)
                self.assertEqual(stub.calls, 1)
                self.assertEqual(attachment.refit_cache_miss["reason"], reason)
        (self.w.capture.parent / VERDICT_BASENAME).write_bytes(b"{not json")
        attachment, stub = self.attach(hazard=self.hazard)
        self.assertEqual((stub.calls, attachment.refit_cache_miss["reason"]), (1, "verdict_malformed"))

    def test_hit_uses_the_verdict_bound_and_seeds_it(self) -> None:
        write_verdict(self.w.capture)
        attachment, stub = self.attach(hazard=self.hazard)
        self.assertEqual(stub.calls, 0)
        self.assertIsNone(attachment.refit_cache_miss)
        bound = effective_bound(self.w.capture)
        self.assertEqual(attachment.metadata["verified_effective_b_fiducial_s"], bound)
        self.assertEqual(attachment.physics_seed,
                         {attachment.metadata["artifact_sha256"]: bound})

    def test_legacy_path_ignores_the_verdict(self) -> None:
        write_verdict(self.w.capture)
        attachment, stub = self.attach(hazard=None)
        self.assertEqual(stub.calls, 1, "the legacy path always refits")
        self.assertIsNone(getattr(attachment, "physics_seed", None))
        self.assertIsNone(getattr(attachment, "sources", None))


# ---------------------------------------------------------------------------
# t1-06: clone-install with a byte-copy fallback and a re-hash


class CloneInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "source.bin"
        self.source.write_bytes(b"verified calibration bytes")

    def attachment(self, *, sources: dict[str, Path] | None) -> Any:
        return controller._InstrumentCalibrationAttachment(
            files={"raw/powermetrics.plist": self.source.read_bytes()}, metadata={},
            **({} if sources is None else {"sources": sources}))

    @unittest.skipUnless(sys.platform == "darwin", "clonefile(2) is an APFS call")
    def test_clone_file_clones_and_never_clobbers_or_follows_links(self) -> None:
        clone = self.root / "clone.bin"
        self.assertTrue(controller._clone_file(self.source, clone))
        self.assertEqual(clone.read_bytes(), self.source.read_bytes())
        self.assertFalse(clone.is_symlink())
        existing = self.root / "existing.bin"
        existing.write_bytes(b"other")
        self.assertFalse(controller._clone_file(self.source, existing))
        self.assertEqual(existing.read_bytes(), b"other")
        link = self.root / "link.bin"
        link.symlink_to(self.source)
        target = self.root / "from-link.bin"
        self.assertFalse(controller._clone_file(link, target))
        self.assertFalse(target.exists() or target.is_symlink())

    def test_hazard_install_clones_and_rehashes(self) -> None:
        calls: list[tuple[Path, Path]] = []
        real = controller._clone_file

        def recording(source: Path, destination: Path) -> bool:
            calls.append((source, destination))
            return real(source, destination)

        bundle = self.root / "bundle"
        with patch.object(controller, "_clone_file", side_effect=recording):
            self.attachment(sources={"raw/powermetrics.plist": self.source}).install(bundle)
        installed = bundle / "instrument_calibration/raw/powermetrics.plist"
        self.assertEqual(calls, [(self.source, installed)])
        self.assertEqual(installed.read_bytes(), self.source.read_bytes())

    def test_a_clone_that_does_not_match_is_replaced_by_the_verified_bytes(self) -> None:
        def wrong_clone(_source: Path, destination: Path) -> bool:
            destination.write_bytes(b"bytes that changed after verification")
            return True

        bundle = self.root / "bundle"
        with patch.object(controller, "_clone_file", side_effect=wrong_clone):
            self.attachment(sources={"raw/powermetrics.plist": self.source}).install(bundle)
        self.assertEqual((bundle / "instrument_calibration/raw/powermetrics.plist").read_bytes(),
                         b"verified calibration bytes")

    def test_a_byte_copy_that_does_not_rehash_refuses(self) -> None:
        # Keeper: the installed copy must be the verified bytes.
        bundle = self.root / "bundle"
        with patch.object(controller, "_clone_file", return_value=False), \
                patch.object(controller, "_installed_copy_sha256", return_value="0" * 64):
            with self.assertRaisesRegex(ValueError, "installed copy does not match"):
                self.attachment(sources={"raw/powermetrics.plist": self.source}).install(bundle)

    def test_legacy_install_writes_bytes_without_cloning(self) -> None:
        bundle = self.root / "bundle"
        with patch.object(controller, "_clone_file", side_effect=AssertionError("cloned")):
            self.attachment(sources=None).install(bundle)
        self.assertEqual((bundle / "instrument_calibration/raw/powermetrics.plist").read_bytes(),
                         b"verified calibration bytes")


class CloneInstallWindowTests(_WindowCase):
    def test_member_install_clones_every_attached_file(self) -> None:
        write_verdict(self.w.capture)
        calls: list[str] = []
        real = controller._clone_file

        def recording(source: Path, destination: Path) -> bool:
            calls.append(source.relative_to(self.w.capture.resolve()).as_posix())
            return real(source, destination)

        with patch.object(controller, "_clone_file", side_effect=recording):
            bundle, summary = run_window_member(self.w)
        self.assertEqual(summary.status, RunStatus.SUCCEEDED, summary.failure_message)
        self.assertIn("raw/powermetrics.plist", calls)
        self.assertIn("manifest.json", calls)
        for relative in calls:
            self.assertEqual((bundle / "instrument_calibration" / relative).read_bytes(),
                             (self.w.capture / relative).read_bytes())

if __name__ == "__main__":
    unittest.main()
