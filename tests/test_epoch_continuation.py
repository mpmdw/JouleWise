"""Mutation-shaped continuation tests; all ledgers and captures are synthetic."""

from __future__ import annotations

from contextlib import contextmanager, redirect_stdout, redirect_stderr
import copy
from dataclasses import replace
from decimal import Decimal, localcontext
import hashlib
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from joulewise import calibration_epoch_continuation as continuation
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.schemas import CalibrationBracketingPolicy
from scripts import issue_epoch_continuation as issuer
from tests.fixtures.epoch_bootstrap.build import (
    SESSION_ID, TARGET_EPOCH, T1_BINDINGS, Slot, build_derivation_ledger,
    tamper_member_bundle,
)
from tests.test_calibration_bracketing import _fixture_snapshot, _synthetic_issued_snapshot
from tests.fixtures.epoch_continuation.build import append_open_capture_session


def _seal(value):
    value["derivation_sha256"] = bracket._canonical_sha256(
        {key: item for key, item in value.items() if key != "derivation_sha256"}
    )
    return value


class EpochContinuationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / "candidate.json"
        self.artifact = bracket.load_calibration_acceptance_bound()
        self.rule = continuation.continuation_rule(self.artifact)
        self.level = Decimal(self.rule["level_screen_s"])
        self.screen = Decimal(self.rule["operative_bracket_screen_s"])
        self.fixture = None

    def build(self, slots=None, **kwargs):
        self.fixture = build_derivation_ledger(
            self.root / "fixture", slots or [Slot("0.025")] * 12, **kwargs,
        )
        return self.fixture

    def args(self, *extra):
        fixture = self.fixture
        return [
            "prepare-candidate", "--session-id", SESSION_ID,
            "--ledger", str(fixture["ledger"]), "--head-pin", str(fixture["pin"]),
            "--repo-root", str(fixture["root"]),
            "--acceptance", str(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH),
            "--d102-addendum-date", "2026-09-10", "--out", str(self.out), *extra,
        ]

    def run_cli(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            rc = issuer.main(args)
        return rc, stdout.getvalue(), stderr.getvalue()

    def prepare(self, *extra):
        if self.fixture is None:
            self.build()
        return self.run_cli(self.args(*extra))

    def snapshot(self):
        return load_calibration_ledger_snapshot(
            self.fixture["ledger"], self.fixture["pin"],
            require_committed_pin=True, verify_custody=False, mode="read_replay",
            repo_root=self.fixture["root"],
        )

    def candidate(self):
        rc, _, error = self.prepare()
        self.assertEqual((rc, error), (0, ""))
        return json.loads(self.out.read_bytes())

    @contextmanager
    def issued(self, payload=None):
        value = copy.deepcopy(payload if payload is not None else self.candidate())
        value.pop("candidate_not_issued", None)
        _seal(value)
        raw = (json.dumps(value, indent=2) + "\n").encode()
        path = self.root / "issued.json"
        path.write_bytes(raw)
        registry = {value["continuation_id"]: {
            "path": path, "relative_path": "tests/fixtures/epoch_continuation/issued.json",
            "file_sha256": hashlib.sha256(raw).hexdigest(),
        }}
        with patch.dict(bracket.EPOCH_CONTINUATION_REGISTRY, registry, clear=True):
            try:
                yield value, path
            finally:
                path.write_bytes(raw)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), registry[value["continuation_id"]]["file_sha256"])

    def load(self, snapshot=None):
        details = []
        loaded = continuation.load_epoch_continuations(
            self.artifact, self.snapshot() if snapshot is None else snapshot,
            refusal_details=details,
        )
        return loaded, details

    def evaluate(self, *, epoch=None, extra_values=(), extra_rows=(), night=None):
        """Combine a real fixture-night replay with an explicit synthetic prefix.

        Only the unit-evaluation snapshot is composed; no ledger or r6 byte is
        rewritten. The prefix retains every r6 prior-set content/disposition.
        """
        epoch = TARGET_EPOCH if epoch is None else epoch
        bindings = {**T1_BINDINGS, **epoch}
        bindings["protocol_sha256"] = bracket.protocol_sha256(bracket.PROTOCOL_ID)
        candidates = []
        for name, when, value in [("pre", 99, "0.025"), ("post", 111, "0.026"),
                                  *((f"extra-{i}", 200 + i, value) for i, value in enumerate(extra_values))]:
            candidates.append(bracket.CalibrationCandidate(
                relative_path=f"synthetic/{name}",
                manifest_sha256=hashlib.sha256(f"manifest-{name}".encode()).hexdigest(),
                evidence_sha256=hashlib.sha256(f"evidence-{name}".encode()).hexdigest(),
                protocol_id=bracket.PROTOCOL_ID, capture_wall_time_s=when,
                b_fiducial_s=value, bindings=bindings,
            ))
        ordinary, candidates = _fixture_snapshot(candidates)
        prior = _synthetic_issued_snapshot(self.artifact)
        night = self.snapshot() if night is None else night
        shifted = {row.attempt_id: replace(row, sequence=row.sequence + prior.head_sequence)
                   for row in night.observations}
        sessions = tuple(replace(session, finalized_slots={name: shifted.get(row.attempt_id, replace(row, sequence=row.sequence + prior.head_sequence))
                         for name, row in session.finalized_slots.items()})
                         for session in night.bracket_sessions)
        head = prior.head_sequence + night.head_sequence
        normal_rows = tuple(replace(row, sequence=head + row.sequence) for row in ordinary.observations)
        snapshot = replace(
            night, head_sequence=head + len(normal_rows) * 2 + len(extra_rows) * 2,
            baseline_sequence=prior.baseline_sequence, baseline_digest=prior.baseline_digest,
            observations=(*prior.observations, *shifted.values(), *normal_rows, *extra_rows),
            bracket_sessions=sessions,
        )
        return bracket.evaluate_calibration_bracket(
            candidates, window_start_s=100, window_end_s=110, bindings=bindings,
            policy=CalibrationBracketingPolicy(require_bracket=True, calibration_bracket_max_drift_s=0.010),
            acceptance_bound=self.artifact, ledger_snapshot=snapshot,
        )

    def test_open_capture_session_still_crosschecks_terminal_continuation(self):
        with self.issued():
            for kind in ("bracket", "derivation"):
                # The ledger uses the same open-state reason for both kinds.
                snapshot = self.snapshot()
                session = replace(snapshot.bracket_sessions[0], session_id="capture-in-flight",
                                  session_kind=kind, state="open", finalized_slots={})
                snapshot = replace(snapshot, bracket_sessions=(*snapshot.bracket_sessions, session),
                                   refusal_reasons=("calibration_ledger_bracket_session_open",))
                loaded, details = self.load(snapshot)
                self.assertEqual(details, [])
                self.assertEqual(len(loaded), 1)
                self.assertEqual(loaded[0].ledger_cross_check, "verified_terminal_derivation_session")
            snapshot = append_open_capture_session(self.fixture)
            self.assertTrue(snapshot.is_governed_open_bracket_extension)
            loaded, details = self.load(snapshot)
            self.assertEqual(details, [])
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].ledger_cross_check, "verified_terminal_derivation_session")

    def test_integrity_and_unknown_snapshot_refusals_remain_invalid(self):
        reasons = (
            "attempt_conflict", "baseline_missing", "bracket_session_conflict", "chain_conflict",
            "content_conflict", "custody_invalid", "head_mismatch", "head_uncommitted",
            "malformed", "missing", "operation_conflict", "pending", "recovery_required",
            "rollback", "ungoverned_business", "future_unknown_reason",
        )
        with self.issued():
            clean = self.snapshot()
            governed = append_open_capture_session(self.fixture)
            for reason in reasons:
                for base in (clean, governed):
                    with self.subTest(reason=reason, governed=base is governed):
                        # A head mismatch alone or without the governed pin proof
                        # is an integrity failure, even beside an open session.
                        snapshot = replace(base, refusal_reasons=tuple(sorted(set(
                            base.refusal_reasons + ("calibration_ledger_" + reason,)))),
                            committed_head_sequence=None if reason == "head_mismatch" else base.committed_head_sequence)
                        loaded, details = self.load(snapshot)
                        self.assertEqual(loaded, ())
                        self.assertEqual(details[0]["detail"], "ledger_snapshot_invalid")

    def test_continuations_own_open_session_still_refuses(self):
        with self.issued():
            snapshot = self.snapshot()
            session = replace(snapshot.bracket_sessions[0], state="open")
            snapshot = replace(snapshot, bracket_sessions=(session,),
                               refusal_reasons=("calibration_ledger_bracket_session_open",))
            loaded, details = self.load(snapshot)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "session_not_terminal_or_state_mismatch")

    def test_oserror_detail_uses_exception_class_and_relative_path(self):
        with self.issued() as (value, path):
            entry = bracket.EPOCH_CONTINUATION_REGISTRY[value["continuation_id"]]
            for relative in (entry["relative_path"], None, str(path)):
                for error in (FileNotFoundError(2, "missing", str(path)),
                              OSError(5, "failure", str(path), None, "/private/other-secret")):
                    with self.subTest(relative=relative, error=type(error).__name__):
                        expected_path = relative if relative and not Path(relative).is_absolute() else continuation.relpath(
                            path, Path(continuation.__file__).resolve().parents[1])
                        with patch.dict(entry, {"relative_path": relative}), patch.object(
                            continuation, "read_authentication_input", side_effect=error,
                        ):
                            loaded, details = self.load()
                        self.assertEqual(loaded, ())
                        self.assertEqual(details[0]["detail"], f"{type(error).__name__}: {expected_path}")
                        self.assertFalse(Path(details[0]["detail"].split(": ", 1)[1]).is_absolute())
                        self.assertNotIn("/private/other-secret", details[0]["detail"])
            path.unlink()
            loaded, details = self.load()
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"],
                             "FileNotFoundError: tests/fixtures/epoch_continuation/issued.json")

    def test_prepare_valid_null_bound_names_slot(self):
        self.build([Slot("0.025")] * 11 + [Slot(None, evidence_lexeme="null")])
        rc, out, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertEqual(out, "")
        self.assertIn("slots.d12.b_fiducial_s_required_for_valid_row", error)
        self.assertFalse(self.out.exists())

    def test_candidate_recipe_marker_pin_and_check(self):
        payload = self.candidate()
        self.assertTrue(payload["candidate_not_issued"])
        self.assertEqual(payload, _seal(copy.deepcopy(payload)))
        self.assertEqual(payload["evidence"]["m"], 12)
        self.assertEqual(len(payload["evidence"]["slots"]), 12)
        check = ["check", "--candidate", str(self.out)]
        self.assertIn("candidate_not_issued", self.run_cli(check)[2])
        with self.issued(payload) as (value, path):
            args = ["check", "--candidate", str(path)]
            rc, out, err = self.run_cli(args)
            self.assertEqual((rc, err), (0, ""))
            self.assertEqual(json.loads(out)["ledger_cross_check"], "skipped_no_ledger_snapshot")
            self.assertEqual(json.loads(out)["judged_epochs"], [self.artifact["identity_epoch"], TARGET_EPOCH])
            rc, out, err = self.run_cli(args + ["--ledger", str(self.fixture["ledger"]),
                "--head-pin", str(self.fixture["pin"]), "--repo-root", str(self.fixture["root"])])
            self.assertEqual((rc, err), (0, ""))
            self.assertEqual(json.loads(out)["ledger_cross_check"], "verified_terminal_derivation_session")
            with patch.dict(bracket.EPOCH_CONTINUATION_REGISTRY, {}, clear=True):
                rc, _, err = self.run_cli(args)
                self.assertEqual(rc, 3)
                self.assertIn("continuation_unregistered", err)

    def test_continued_freshness_and_screens_equal_original_path(self):
        with self.issued() as (value, _):
            result, reasons = self.evaluate()
            old, old_reasons = self.evaluate(epoch=self.artifact["identity_epoch"])
            self.assertEqual(reasons, ())
            self.assertEqual(old_reasons, ())
            self.assertEqual(result["status"], "passed")
            fresh = result["acceptance"]["freshness"]
            self.assertEqual(fresh["status"], "fresh")
            self.assertEqual(fresh["basis"], "epoch_continuation")
            self.assertEqual(fresh["stale_fields"], [])
            self.assertEqual(fresh["continuation_id"], value["continuation_id"])
            for field in ("preflight", "drift"):
                self.assertEqual(result["acceptance"][field], old["acceptance"][field])
            self.assertEqual(result["policy"], old["policy"])

    def test_check_requires_the_registry_path_to_load_the_continuation(self):
        with self.issued() as (value, path):
            entry = bracket.EPOCH_CONTINUATION_REGISTRY[value["continuation_id"]]
            entry["path"] = self.root / "missing-issued-file.json"
            rc, _, error = self.run_cli(["check", "--candidate", str(path)])
            self.assertEqual(rc, 3)
            self.assertIn("continuation_registry_path_unavailable_or_invalid", error)

    def test_without_continuation_new_epoch_is_stale(self):
        self.build()
        result, reasons = self.evaluate()
        self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
        self.assertEqual(result["acceptance"]["freshness"]["stale_fields"], ["os_build"])

    def test_rotated_byte_surfaces_invalid_and_stale(self):
        with self.issued() as (_, path):
            raw = path.read_bytes()
            # A harmless JSON whitespace rotation isolates byte authentication:
            # the schema, scientific values and canonical digest still agree.
            path.write_bytes(raw.replace(b"\n", b" ", 1))
            loaded, details = self.load()
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["reason"], continuation.CONTINUATION_INVALID)
            self.assertEqual(details[0]["detail"], "continuation_file_sha256")
            result, reasons = self.evaluate()
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertEqual(result["acceptance"]["freshness"]["reason"], continuation.CONTINUATION_INVALID)
            self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_other_acceptance_id_or_pin_refuses_even_with_valid_continuation_pin(self):
        payload = self.candidate()
        r5 = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R5_ACCEPTANCE_BOUND_PATH)
        cuts = {"acceptance_id": r5["acceptance_id"],
                "acceptance_file_sha256": bracket.ANCHOR_V3_R5_ACCEPTANCE_BOUND_SHA256,
                "acceptance_derivation_sha256": r5["derivation_sha256"]}
        for field, value in cuts.items():
            with self.subTest(field=field):
                changed = copy.deepcopy(payload)
                changed[field] = value
                with self.issued(changed):
                    loaded, details = self.load()
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], field)

    def test_machine_must_match_every_continued_identity_field(self):
        with self.issued():
            for field, value in TARGET_EPOCH.items():
                with self.subTest(field=field):
                    epoch = {**TARGET_EPOCH, field: value + 1 if isinstance(value, int) else value + "-other"}
                    result, reasons = self.evaluate(epoch=epoch)
                    self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
                    self.assertEqual(result["acceptance"]["freshness"]["status"], "stale")

    def test_fail_marker_and_derivation_hash_refuse(self):
        payload = self.candidate()
        for field, value in (("verdict", "fail"), ("candidate_not_issued", False), ("derivation_sha256", "0" * 64)):
            with self.subTest(field=field), self.issued(payload) as (issued, path):
                issued[field] = value
                if field != "derivation_sha256":
                    _seal(issued)
                raw = (json.dumps(issued) + "\n").encode()
                path.write_bytes(raw)
                entry = bracket.EPOCH_CONTINUATION_REGISTRY[issued["continuation_id"]]
                old_pin = entry["file_sha256"]
                entry["file_sha256"] = hashlib.sha256(raw).hexdigest()
                try:
                    loaded, details = self.load()
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], field)
                finally:
                    entry["file_sha256"] = old_pin

    def test_unchanged_epoch_and_forged_statistics_refuse(self):
        payload = self.candidate()
        cuts = (("continued_identity_epoch", self.artifact["identity_epoch"], "continued_identity_epoch_unchanged"),
                ("m", 11, "evidence.m"), ("retained_min_s", "0.024", "evidence.retained_min_s"),
                ("retained_max_s", "0.026", "evidence.retained_max_s"),
                ("retained_range_s", "0.001", "evidence.retained_range_s"))
        for field, value, reason in cuts:
            with self.subTest(field=field):
                changed = copy.deepcopy(payload)
                (changed if field == "continued_identity_epoch" else changed["evidence"])[field] = value
                with self.issued(changed):
                    loaded, details = self.load()
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], reason)

    def test_phantom_open_wrong_kind_and_missing_attempt_sessions_refuse(self):
        with self.issued():
            snapshot = self.snapshot()
            session = snapshot.bracket_sessions[0]
            cases = [
                (replace(snapshot, bracket_sessions=()), "session_absent"),
                (replace(snapshot, bracket_sessions=(replace(session, state="open"),)), "session_not_terminal"),
                (replace(snapshot, bracket_sessions=(replace(session, session_kind="bracket"),)), "session_not_derivation"),
                (replace(snapshot, bracket_sessions=(replace(session, finalized_slots={}),)), "ledger_finalized_slots_mismatch"),
                (replace(snapshot, observations=snapshot.observations[1:]), "acknowledged_attempt_missing"),
            ]
            for mutated, detail in cases:
                with self.subTest(detail=detail):
                    loaded, details = self.load(mutated)
                    self.assertEqual(loaded, ())
                    self.assertIn(detail, details[0]["detail"])
                    result, _ = self.evaluate(night=mutated)
                    self.assertEqual(result["acceptance"]["freshness"]["reason"], continuation.CONTINUATION_INVALID)

    def test_a_failing_night_prints_its_derived_record_and_exits_4_without_writing(self):
        """Delta 192 S2: the ruling's FAIL verdict reaches the desk with its numbers."""

        self.build([Slot(str(self.level + Decimal("0.001")))] * 3 + [Slot("0.025")] * 9)
        stream = io.StringIO()
        with redirect_stdout(stream):
            rc = issuer.main(self.args())
        self.assertEqual(rc, 4)
        self.assertFalse(self.out.exists())
        printed = json.loads(stream.getvalue())
        self.assertEqual(printed["verdict"], "fail")
        self.assertEqual(printed["evidence"]["m"], 12)

    def test_failed_nine_row_night_cannot_hide_three_finalized_rows_to_pass(self):
        self.build([Slot("0.025")] * 6 + [Slot(str(self.level + Decimal("0.001")))] * 3
                   + [Slot("0.025")] * 3, fill_slots=9, abort_reason="window_exhausted")
        forged, _, _ = issuer.derive_record(issuer.build_parser().parse_args(self.args()))
        self.assertFalse(self.out.exists())
        self.assertEqual(forged["verdict"], "fail")
        self.assertEqual(forged["evidence"]["m"], 9)
        snapshot = self.snapshot()
        self.assertEqual(len(snapshot.bracket_session_by_id[SESSION_ID].finalized_slots), 9)
        evidence = forged["evidence"]
        # Reproduce refuter 170: disclose the six low rows, relabel the three
        # over-screen rows as unused, then reseal and pin the forged PASS.
        for index in range(6, 9):
            evidence["slots"][index] = {
                **evidence["slots"][9], "slot": evidence["slots"][index]["slot"],
            }
        evidence.update({
            "acknowledged_attempt_ids": [slot["attempt_id"] for slot in evidence["slots"][:6]],
            "m": 6, "retained_min_s": "0.025", "retained_max_s": "0.025", "retained_range_s": "0.000",
        })
        forged.update(verdict="pass", continuation_id="forged-six-of-nine")
        with self.issued(forged):
            loaded, details = self.load(snapshot)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "hidden_finalized_row")

    def test_finalized_slots_must_match_ledger_attempt_ids(self):
        payload = self.candidate()
        payload["evidence"]["slots"][0]["attempt_id"] = "forged-attempt"
        payload["evidence"]["acknowledged_attempt_ids"][0] = "forged-attempt"
        with self.issued(payload):
            loaded, details = self.load()
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "ledger_finalized_slots_mismatch")

    def assert_unresolved_forgery_refuses(self, excluded_bound):
        self.build([Slot("0.025")] * 6 + [Slot(excluded_bound)] * 3
                   + [Slot("0.025")] * 3, fill_slots=9, abort_reason="window_exhausted")
        forged, _, _ = issuer.derive_record(issuer.build_parser().parse_args(self.args()))
        self.assertFalse(self.out.exists())
        self.assertEqual((forged["verdict"], forged["evidence"]["m"]), ("fail", 9))
        snapshot = self.snapshot()
        evidence = forged["evidence"]
        self.assertEqual(len(evidence["acknowledged_attempt_ids"]), 9)
        # Delta 179 forgery (a): keep every ledger-pinned field and all nine
        # acknowledgments, but invent an anchor failure for the three outliers.
        for slot in evidence["slots"][6:9]:
            slot.update(anchor_v3_resolved=False, anchor_v3_detail="made-up-anchor-failure")
        evidence.update(m=6, retained_min_s="0.025", retained_max_s="0.025", retained_range_s="0.000")
        forged.update(verdict="pass", continuation_id="forged-unresolved-three-of-nine")
        with self.issued(forged):
            for ledger in (snapshot, None):
                with self.subTest(ledger_present=ledger is not None):
                    details = []
                    loaded = continuation.load_epoch_continuations(
                        self.artifact, ledger, refusal_details=details,
                    )
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], "unresolved_valid_row_exceeds_envelope")

    def test_failed_nine_row_night_cannot_relabel_over_level_rows_unresolved(self):
        self.assert_unresolved_forgery_refuses(str(self.level + Decimal("0.001")))

    def test_failed_nine_row_night_cannot_relabel_range_extrema_unresolved(self):
        low = Decimal("0.025") - self.screen - Decimal("0.000000000000001")
        self.assertGreaterEqual(low, 0)
        self.assertLess(low, self.level)
        self.assert_unresolved_forgery_refuses(str(low))

    def test_every_slot_has_exact_documented_keys(self):
        self.build(fill_slots=6, abort_reason="window_exhausted")
        payload = self.candidate()
        fields = {"slot", "attempt_id", "content_id", "manifest_sha256",
                  "instrument_evidence_sha256", "disposition", "anchor_v3_resolved",
                  "anchor_v3_detail", "b_fiducial_s"}
        for index in range(12):
            for field in sorted(fields | {"misleading_annotation"}):
                with self.subTest(index=index, field=field):
                    changed = copy.deepcopy(payload)
                    slot = changed["evidence"]["slots"][index]
                    if field in fields:
                        del slot[field]
                    else:
                        slot[field] = "safe to ignore this capture"
                    with self.issued(changed):
                        loaded, details = self.load()
                        self.assertEqual(loaded, ())
                        self.assertEqual(details[0]["detail"], "slots.keys")

    def test_every_session_observation_must_be_disclosed(self):
        self.build(fill_slots=6, abort_reason="window_exhausted")
        with self.issued():
            snapshot = self.snapshot()
            session = snapshot.bracket_session_by_id[SESSION_ID]
            # A supplied snapshot must not hide a session observation simply
            # because its finalized_slots index omitted the row too.
            extra = replace(snapshot.observations[0], sequence=snapshot.head_sequence + 1,
                            attempt_id=SESSION_ID + "-d07", bracket_slot=session.declared_slots[6])
            snapshot = replace(snapshot, observations=(*snapshot.observations, extra))
            loaded, details = self.load(snapshot)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "hidden_finalized_row")

    def test_excluded_rows_still_crosscheck_disposition_and_exact_lexeme(self):
        self.build([Slot("0.025")] * 6 + [Slot("0.9", disposition="ordinary-invalid")] * 6)
        payload = self.candidate()
        for field, value in (("disposition", "systematic-invalid"), ("b_fiducial_s", "0.90")):
            with self.subTest(field=field):
                changed = copy.deepcopy(payload)
                changed["evidence"]["slots"][-1][field] = value
                with self.issued(changed):
                    loaded, details = self.load()
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], "acknowledged_row_disagrees")

    def test_acknowledged_content_id_must_match_snapshot(self):
        with self.issued():
            snapshot = self.snapshot()
            session = snapshot.bracket_sessions[0]
            name, row = next(iter(session.finalized_slots.items()))
            altered = replace(row, content_id="f" * 64)
            slots = dict(session.finalized_slots)
            slots[name] = altered
            snapshot = replace(snapshot,
                observations=tuple(altered if item.attempt_id == row.attempt_id else item for item in snapshot.observations),
                bracket_sessions=(replace(session, finalized_slots=slots),))
            loaded, details = self.load(snapshot)
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "acknowledged_content_id")

    def test_doubling_is_per_epoch_and_acknowledged_values_count(self):
        with self.issued():
            result, reasons = self.evaluate()
            self.assertEqual(reasons, ())  # prior 30 + new 14 must never pool.
            self.assertEqual(result["acceptance"]["prospective_rederivation"]["observed_triggers"], [])
            below, reasons = self.evaluate(extra_values=["0.025"] * 19)
            self.assertEqual(reasons, ())  # new epoch count 33.
            doubled, reasons = self.evaluate(extra_values=["0.025"] * 20)
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertEqual(doubled["acceptance"]["prospective_rederivation"]["observed_triggers"], ["corpus_doubles_from_17_to_34"])

    def test_low_acknowledged_value_exempt_but_ordinary_row_stales(self):
        self.build([Slot("0.020"), *[Slot("0.025")] * 11])
        with self.issued():
            result, reasons = self.evaluate()
            self.assertEqual(reasons, ())
            result, reasons = self.evaluate(extra_values=["0.020"])
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertEqual(result["acceptance"]["prospective_rederivation"]["observed_triggers"], ["new_valid_same_identity_capture_expands_observed_range"])

    def test_future_derivation_session_remains_in_range_trigger(self):
        self.build(second_session=("later-night", [Slot("0.020")] * 12))
        with self.issued():
            result, reasons = self.evaluate()
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertIn("new_valid_same_identity_capture_expands_observed_range", result["acceptance"]["prospective_rederivation"]["observed_triggers"])

    def test_systematic_row_in_the_equivalence_night_still_fires(self):
        payload = self.candidate()
        snapshot = self.snapshot()
        session = snapshot.bracket_session_by_id[SESSION_ID]
        name, original = next(iter(session.finalized_slots.items()))
        row = replace(original, disposition="systematic-invalid")
        # Model a previously issued continuation: today's preparer refuses
        # this night, but evaluation must still catch an issued failure row.
        payload["evidence"]["slots"][0]["disposition"] = "systematic-invalid"
        payload["evidence"]["m"] = 11
        night = replace(snapshot,
            observations=tuple(row if item.attempt_id == row.attempt_id else item for item in snapshot.observations),
            bracket_sessions=(replace(session, finalized_slots={**session.finalized_slots, name: row}),))
        with self.issued(payload):
            loaded, details = self.load(night)
            self.assertEqual(details, [])
            self.assertEqual(loaded[0].ledger_cross_check, "verified_terminal_derivation_session")
            self.assertIn(row.attempt_id, loaded[0].acknowledged_attempt_ids)
            result, reasons = self.evaluate(night=night)
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertEqual(result["acceptance"]["prospective_rederivation"]["observed_triggers"], ["new_systematic_failure_challenges_preflight_screen"])
        # An ordinary systematic failure independently fires, with a healthy
        # equivalence night so the first case cannot mask a broken trigger.
        payload["evidence"]["slots"][0]["disposition"] = "valid"
        payload["evidence"]["m"] = 12
        with self.issued(payload):
            hashes = {name: hashlib.sha256(f"ordinary-systematic-{name}".encode()).hexdigest()
                      for name in ("manifest.json", "instrument_evidence.json")}
            row = replace(
                row, sequence=999, attempt_id="ordinary-systematic",
                artifact_sha256=hashes, content_id=bracket.content_id_from_artifact_hashes(hashes),
                bracket_session_id=None, bracket_slot=None, bracket_window_id=None,
                bracket_plan_id=None, bracket_plan_sha256=None, bracket_evidence_root_id=None,
                bracket_runs_root=None,
            )
            result, reasons = self.evaluate(extra_rows=(row,))
            self.assertEqual(reasons, ("calibration_acceptance_bound_stale",))
            self.assertEqual(result["acceptance"]["prospective_rederivation"]["observed_triggers"], ["new_systematic_failure_challenges_preflight_screen"])

    def test_prepare_refuses_systematic_failure_night_without_writing(self):
        self.build([Slot("0.025")] * 11 + [Slot("0.025", disposition="systematic-invalid")])
        rc, out, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertEqual(out, "")
        self.assertIn("night_contains_systematic_failure: slots.d12", error)
        self.assertIn("stale on arrival", error)
        self.assertIn("the desk reports the failure to Ed under D-102's systematic-failure trigger", error)
        self.assertFalse(self.out.exists())

    def test_level_equality_passes(self):
        self.build([Slot(str(self.level))] * 12)
        self.assertEqual(self.prepare()[0], 0)

    def test_one_quantum_above_level_fails_without_writing(self):
        quantum = Decimal(1).scaleb(self.level.as_tuple().exponent)
        self.assertEqual(continuation.equivalence_statistics(
            [str(self.level + quantum)] + [str(self.level)] * 11, self.rule,
        )["verdict"], "fail")
        self.build([Slot(str(self.level + quantum)), *[Slot(str(self.level))] * 11])
        rc, out, error = self.prepare()
        self.assertEqual((rc, error), (4, ""))
        self.assertEqual(json.loads(out)["verdict"], "fail")
        self.assertFalse(self.out.exists())

    def test_range_equality_passes_with_distinct_min_and_max(self):
        low = self.level - self.screen
        self.build([Slot(str(low)), *[Slot(str(self.level))] * 11])
        payload = self.candidate()
        self.assertEqual(Decimal(payload["evidence"]["retained_range_s"]), self.screen)
        self.assertEqual(Decimal(payload["evidence"]["retained_min_s"]), low)
        self.assertEqual(Decimal(payload["evidence"]["retained_max_s"]), self.level)

    def test_range_above_screen_fails_even_when_every_value_meets_level(self):
        low = self.level - self.screen - Decimal("0.000000000000001")
        self.assertEqual(continuation.equivalence_statistics(
            [str(low)] + [str(self.level)] * 11, self.rule,
        )["verdict"], "fail")
        self.build([Slot(str(low)), *[Slot(str(self.level))] * 11])
        rc, out, error = self.prepare()
        self.assertEqual((rc, error), (4, ""))
        self.assertEqual(json.loads(out)["verdict"], "fail")
        self.assertFalse(self.out.exists())

    def test_full_precision_decimal_extrema_and_range_survive(self):
        lexemes = ["0.0250000000000000001", "0.0250000000000000009", "0.0250000000000000004"] * 4
        self.build([Slot(value) for value in lexemes])
        payload = self.candidate()
        self.assertEqual(payload["evidence"]["retained_min_s"], lexemes[0])
        self.assertEqual(payload["evidence"]["retained_max_s"], lexemes[1])
        self.assertEqual(Decimal(payload["evidence"]["retained_range_s"]), Decimal("0.0000000000000000008"))

    def test_five_retained_is_inconclusive_and_writes_nothing(self):
        self.build([Slot("0.025")] * 5 + [Slot("0.025", disposition="ordinary-invalid")] * 7)
        rc, out, error = self.prepare()
        self.assertEqual((rc, error), (5, ""))
        self.assertEqual(json.loads(out)["evidence"]["m"], 5)
        self.assertFalse(self.out.exists())

    def test_only_valid_resolved_values_are_retained_but_all_finalized_acknowledged(self):
        self.build([Slot("0.025")] * 6 + [Slot("0.9", disposition="ordinary-invalid")] * 3
                   + [Slot("0.026", unresolved_detail="affine_clock_fit_empty")] * 3)
        payload = self.candidate()
        self.assertEqual(payload["evidence"]["m"], 6)
        self.assertEqual(len(payload["evidence"]["acknowledged_attempt_ids"]), 12)
        with self.issued(payload):
            loaded, details = self.load()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(details, [])

    def test_unresolved_valid_row_requires_nonempty_anchor_detail(self):
        self.build([Slot("0.025")] * 6 + [Slot("0.026", unresolved_detail="affine_clock_fit_empty")] * 6)
        payload = self.candidate()
        with self.issued(payload):
            loaded, details = self.load()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(details, [])
        for detail in (None, ""):
            with self.subTest(detail=detail):
                changed = copy.deepcopy(payload)
                changed["evidence"]["slots"][-1]["anchor_v3_detail"] = detail
                with self.issued(changed):
                    loaded, details = self.load()
                    self.assertEqual(loaded, ())
                    self.assertEqual(details[0]["detail"], "slots.anchor_v3_detail_required")

    def test_one_unresolved_valid_row_inside_envelope_prepares_and_authenticates(self):
        low = str(self.level - self.screen)
        self.build([Slot(low)] * 11 + [Slot(str(self.level), unresolved_detail="affine_clock_fit_empty")])
        payload = self.candidate()
        evidence = payload["evidence"]
        self.assertEqual(evidence["m"], 11)
        self.assertEqual(evidence["retained_min_s"], low)
        self.assertEqual(evidence["retained_max_s"], low)
        self.assertEqual(Decimal(evidence["retained_range_s"]), 0)
        self.assertFalse(evidence["slots"][-1]["anchor_v3_resolved"])
        self.assertEqual(len(evidence["acknowledged_attempt_ids"]), 12)
        with self.issued(payload):
            loaded, details = self.load()
            self.assertEqual(details, [])
            self.assertEqual((loaded[0].m, loaded[0].verdict), (11, "pass"))
            self.assertEqual(loaded[0].ledger_cross_check, "verified_terminal_derivation_session")

    def assert_prepare_unresolved_envelope_refusal(self, slots, names):
        self.build(slots)
        rc, out, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertEqual(out, "")
        self.assertIn("unresolved_valid_row_exceeds_envelope", error)
        for name in names:
            self.assertIn(f"slots.{name}", error)
        self.assertIn("the desk reports it to Ed for a written ruling", error)
        self.assertFalse(self.out.exists())

    def test_prepare_refuses_unresolved_valid_row_above_level_without_writing(self):
        self.assert_prepare_unresolved_envelope_refusal(
            [Slot("0.025")] * 11
            + [Slot(str(self.level + Decimal("0.001")), unresolved_detail="affine_clock_fit_empty")],
            ["d12"],
        )

    def test_prepare_refuses_unresolved_valid_row_widening_range_without_writing(self):
        with localcontext() as context:
            context.prec = 120
            low = str(self.level - self.screen - Decimal("1e-100"))
        self.assert_prepare_unresolved_envelope_refusal(
            [Slot(str(self.level))] * 11 + [Slot(low, unresolved_detail="affine_clock_fit_empty")],
            ["d12"],
        )

    def test_prepare_checks_combined_unresolved_range(self):
        middle = self.level / 2
        offset = self.screen * Decimal("0.75")
        low, high = middle - offset, middle + offset
        self.assertGreaterEqual(low, 0)
        self.assertLessEqual(high, self.level)
        self.assertLess(offset, self.screen)  # Either alone would fit.
        self.assertGreater(high - low, self.screen)
        self.assert_prepare_unresolved_envelope_refusal(
            [Slot(str(middle))] * 10
            + [Slot(str(value), unresolved_detail="affine_clock_fit_empty") for value in (low, high)],
            ["d11", "d12"],
        )

    def test_unresolved_valid_rows_do_not_count_toward_minimum(self):
        self.build([Slot("0.025")] * 5 + [Slot("0.026", unresolved_detail="affine_clock_fit_empty")] * 7)
        rc, out, error = self.prepare()
        self.assertEqual((rc, error), (5, ""))
        record = json.loads(out)
        self.assertEqual((record["evidence"]["m"], record["verdict"]), (5, "inconclusive"))
        self.assertFalse(self.out.exists())

    def test_unresolved_over_screen_rows_below_minimum_stay_inconclusive_with_the_record(self):
        """Delta 192 S2: the envelope refusal guards only a PASS; an INCONCLUSIVE
        night reaches the desk with its record, unresolved bounds visible."""

        self.build([Slot("0.025")] * 5
                   + [Slot(str(self.level + Decimal("0.001")), unresolved_detail="affine_clock_fit_empty")] * 7)
        rc, out, error = self.prepare()
        self.assertEqual((rc, error), (5, ""))
        record = json.loads(out)
        self.assertEqual((record["evidence"]["m"], record["verdict"]), (5, "inconclusive"))
        unresolved = [s for s in record["evidence"]["slots"] if s["disposition"] == "valid" and not s["anchor_v3_resolved"]]
        self.assertEqual(len(unresolved), 7)
        self.assertFalse(self.out.exists())

    def test_all_valid_envelope_has_no_minimum_count(self):
        for lexemes in ([], [str(self.level)], [str(self.level - self.screen), str(self.level)]):
            with self.subTest(lexemes=lexemes):
                self.assertTrue(continuation.envelope_holds_over_all_valid(lexemes, self.rule))
        self.assertFalse(continuation.envelope_holds_over_all_valid(
            [str(self.level + Decimal("0.001"))], self.rule,
        ))

    def test_unresolved_valid_row_still_requires_a_decimal_bound(self):
        self.build([Slot("0.025")] * 11 + [Slot("0.026", unresolved_detail="affine_clock_fit_empty")])
        payload = self.candidate()
        payload["evidence"]["slots"][-1]["b_fiducial_s"] = None
        with self.issued(payload):
            loaded, details = self.load()
            self.assertEqual(loaded, ())
            self.assertEqual(details[0]["detail"], "slots.d12.b_fiducial_s_required_for_valid_row")

    def test_zero_retained_is_inconclusive(self):
        self.build([Slot("0.025", disposition="ordinary-invalid")] * 12)
        rc, out, _ = self.prepare()
        self.assertEqual(rc, 5)
        self.assertEqual(json.loads(out)["evidence"]["m"], 0)
        self.assertFalse(self.out.exists())

    def test_terminal_aborted_night_keeps_twelve_declared_slots(self):
        self.build(fill_slots=6, abort_reason="window_exhausted")
        payload = self.candidate()
        self.assertEqual(payload["evidence"]["m"], 6)
        self.assertEqual(payload["evidence"]["slots"][-1]["disposition"], "window_exhausted")
        with self.issued(payload):
            self.assertEqual(self.load()[1], [])

    def test_nonterminal_wrong_kind_and_wrong_slot_count_refuse(self):
        # Separate disposable roots avoid changing any registered ledger.
        cases = [(dict(fill_slots=6), 12, "session_not_terminal"),
                 (dict(session_kind="bracket"), 2, "session_not_derivation"),
                 ({}, 11, "session_requires_12_declared_slots")]
        for i, (kwargs, count, detail) in enumerate(cases):
            with self.subTest(detail=detail):
                self.fixture = build_derivation_ledger(self.root / f"case-{i}", [Slot("0.025")] * count, **kwargs)
                rc, _, error = self.prepare()
                self.assertEqual(rc, 3)
                self.assertIn(detail, error)
                self.assertFalse(self.out.exists())

    def test_same_epoch_refuses(self):
        self.build(session_epoch=self.artifact["identity_epoch"],
                   t1_bindings={**T1_BINDINGS, **self.artifact["identity_epoch"]})
        rc, _, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertIn("continued_identity_epoch_unchanged", error)

    def test_primary_bytes_and_exact_lexeme_refuse(self):
        self.build([Slot("0.025", evidence_lexeme="0.0250")] * 12)
        rc, _, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertIn("b_fiducial_s", error)
        self.assertFalse(self.out.exists())

    def test_primary_hash_tamper_refuses(self):
        self.build()
        tamper_member_bundle(self.fixture, SESSION_ID + "-d01", "instrument_evidence.json")
        rc, _, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertIn("instrument_evidence.json", error)
        self.assertFalse(self.out.exists())

    def test_retained_epochs_must_be_unanimous_and_content_ids_recomputed(self):
        self.build()
        snapshot = self.snapshot()
        session = snapshot.bracket_sessions[0]
        name, row = next(iter(session.finalized_slots.items()))
        for field, value, reason in (
            ("identity_epoch", {**TARGET_EPOCH, "hardware_model": "other-machine"}, "identity_epoch_not_unanimous"),
            ("content_id", "f" * 64, "content_id"),
        ):
            with self.subTest(field=field):
                altered = replace(row, **{field: value})
                slots = dict(session.finalized_slots)
                slots[name] = altered
                mutated = replace(snapshot,
                    observations=tuple(altered if item.attempt_id == row.attempt_id else item for item in snapshot.observations),
                    bracket_sessions=(replace(session, finalized_slots=slots),))
                with patch.object(issuer, "_load_snapshot", return_value=mutated):
                    rc, _, error = self.prepare()
                self.assertEqual(rc, 3)
                self.assertIn(reason, error)
                self.assertFalse(self.out.exists())

    def test_dirty_head_pin_refuses(self):
        self.build()
        pin = self.fixture["pin"]
        original = pin.read_bytes()
        try:
            pin.write_bytes(original + b" ")
            rc, _, error = self.prepare()
            self.assertEqual(rc, 3)
            self.assertIn("ledger", error)
            self.assertFalse(self.out.exists())
        finally:
            pin.write_bytes(original)
            self.assertEqual(hashlib.sha256(pin.read_bytes()).digest(), hashlib.sha256(original).digest())

    def test_force_cannot_overwrite_ledger_or_primary_evidence(self):
        self.build()
        for path, reason in (
            (self.fixture["ledger"], "out_overwrites_input"),
            (self.fixture["runs"] / "instrument_validation" / (SESSION_ID + "-d01") / "manifest.json",
             "out_overwrites_primary_evidence"),
        ):
            with self.subTest(reason=reason):
                self.out = path
                original = path.read_bytes()
                rc, _, error = self.prepare("--force")
                self.assertEqual(rc, 3)
                self.assertIn(reason, error)
                self.assertEqual(path.read_bytes(), original)

    def test_either_registry_operative_crosswire_refuses(self):
        self.build()
        for field in ("preflight_level_screen_s", "bracket_screen_s"):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.artifact)
                altered["decimal_derivation"]["ratified_operatives"][field] = "0.1"
                with patch.object(bracket, "load_calibration_acceptance_bound", return_value=altered):
                    rc, _, error = self.prepare()
                self.assertEqual(rc, 3)
                self.assertIn(field, error)
                self.assertFalse(self.out.exists())

    def test_output_configs_overwrite_force_and_determinism(self):
        self.build()
        self.out = self.root / "elsewhere" / "configs" / "calibration" / "forbidden.json"
        rc, _, error = self.prepare()
        self.assertEqual(rc, 3)
        self.assertIn("out_under_configs_calibration", error)
        self.assertFalse(self.out.exists())
        self.out = self.root / "candidate.json"
        self.assertEqual(self.prepare()[0], 0)
        raw = self.out.read_bytes()
        self.assertEqual(self.prepare()[0], 3)
        self.assertEqual(self.prepare("--force")[0], 0)
        self.assertEqual(self.out.read_bytes(), raw)

    def test_a_record_written_by_the_real_desk_tool_cross_checks_clean(self):
        """Fresh-eyes 196 B: the witness cross-check must accept the desk tool's
        own v1 record (its acceptance digest and screen rule are checked, not
        forgiven) and refuse it once the digest is altered."""

        from scripts import epoch_equivalence_check as desk
        self.build()
        witness = self.root / "desk-record.json"
        rc, out, _ = self.run_cli_of(desk.main, [
            "--session-id", SESSION_ID,
            "--ledger", str(self.fixture["ledger"]), "--head-pin", str(self.fixture["pin"]),
            "--acceptance", str(bracket.DEFAULT_ACCEPTANCE_BOUND_PATH),
            "--repo-root", str(self.fixture["root"]), "--out", str(witness),
        ])
        self.assertEqual(rc, 0, out)
        record = json.loads(witness.read_bytes())
        self.assertIn("acceptance_file_sha256", record["reference_envelope"])
        self.assertIn("screen_rule", record["reference_envelope"])
        rc, _, error = self.prepare("--equivalence-record", str(witness))
        self.assertEqual((rc, error), (0, ""))
        for field, value in (("acceptance_file_sha256", "0" * 64), ("screen_rule", "floored_range_envelope_screen")):
            with self.subTest(field=field):
                tampered = copy.deepcopy(record)
                tampered["reference_envelope"][field] = value
                witness.write_text(json.dumps(tampered), encoding="utf-8")
                rc, _, error = self.prepare("--force", "--equivalence-record", str(witness))
                self.assertEqual(rc, 3)
                self.assertIn(f"equivalence_record.reference_envelope.{field}", error)

    def run_cli_of(self, entry, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            rc = entry(args)
        return rc, stdout.getvalue(), stderr.getvalue()

    def test_s9_witness_agrees_then_m_or_lexeme_disagreement_names_field(self):
        self.build()
        fixture = Path(__file__).parent / "fixtures/epoch_continuation/s9-pass.json"
        witness = json.loads(fixture.read_bytes())
        path = self.root / "witness.json"
        for field in (None, "m", "b_fiducial_s", "level_screen_s", "range_s", "holds"):
            with self.subTest(field=field):
                value = copy.deepcopy(witness)
                if field == "m":
                    value["m"] = 11
                elif field == "b_fiducial_s":
                    value["retained"][0][field] = "0.0250"
                elif field == "level_screen_s":
                    value["reference_envelope"][field] = "0.1"
                elif field == "range_s":
                    value[field] = "0.001"
                elif field == "holds":
                    value["level_screen_comparison"][field] = False
                path.write_text(json.dumps(value))
                rc, _, error = self.prepare("--equivalence-record", str(path), "--force")
                self.assertEqual(rc, 0 if field is None else 3)
                if field is not None:
                    self.assertIn(field, error)

    def test_s9_level_fail_witness_preserves_false_comparison(self):
        quantum = Decimal(1).scaleb(self.level.as_tuple().exponent)
        self.assertEqual(continuation.equivalence_statistics(
            [str(self.level + quantum)] + [str(self.level)] * 11, self.rule,
        )["verdict"], "fail")
        self.build([Slot(str(self.level + quantum)), *[Slot(str(self.level))] * 11])
        witness = Path(__file__).parent / "fixtures/epoch_continuation/s9-fail-level.json"
        # A FAIL night derives its record (the envelope gate applies only to a
        # PASS over the retained values), so the S9 FAIL projection is live.
        record, artifact, session = issuer.derive_record(issuer.build_parser().parse_args(self.args()))
        projection = issuer._s9_projection(record, artifact, session)
        expected = json.loads(witness.read_bytes())
        for key in ("level_screen_comparison", "bracket_screen_comparison"):
            self.assertEqual(projection[key], expected[key])
        rc, out, error = self.prepare("--equivalence-record", str(witness))
        self.assertEqual((rc, error), (4, ""))
        self.assertEqual(json.loads(out)["verdict"], "fail")
        self.assertFalse(self.out.exists())

    def test_s9_bracket_fail_witness_preserves_false_comparison(self):
        low = self.level - self.screen - Decimal("0.000000000000001")
        self.assertEqual(continuation.equivalence_statistics(
            [str(low)] + [str(self.level)] * 11, self.rule,
        )["verdict"], "fail")
        self.build([Slot(str(low)), *[Slot(str(self.level))] * 11])
        witness = Path(__file__).parent / "fixtures/epoch_continuation/s9-fail-bracket.json"
        # A FAIL night derives its record (the envelope gate applies only to a
        # PASS over the retained values), so the S9 FAIL projection is live.
        record, artifact, session = issuer.derive_record(issuer.build_parser().parse_args(self.args()))
        projection = issuer._s9_projection(record, artifact, session)
        expected = json.loads(witness.read_bytes())
        for key in ("level_screen_comparison", "bracket_screen_comparison"):
            self.assertEqual(projection[key], expected[key])
        rc, out, error = self.prepare("--equivalence-record", str(witness))
        self.assertEqual((rc, error), (4, ""))
        self.assertEqual(json.loads(out)["verdict"], "fail")
        self.assertFalse(self.out.exists())

    def test_s9_extra_science_cannot_bypass_crosscheck(self):
        self.build()
        fixture = Path(__file__).parent / "fixtures/epoch_continuation/s9-pass.json"
        witness = json.loads(fixture.read_bytes())
        path = self.root / "witness.json"
        snapshot = self.snapshot()
        for key, value, detail in (
            ("ledger", {"ledger_schema": snapshot.ledger_schema,
                        "head_sequence": snapshot.head_sequence - 1,
                        "head_digest": snapshot.head_digest}, "ledger.head_sequence"),
            ("rc", 4, "rc"),
            ("unrecognized_science", 5, "unrecognized_science"),
        ):
            with self.subTest(key=key):
                path.write_text(json.dumps({**witness, key: value}))
                rc, _, error = self.prepare("--equivalence-record", str(path))
                self.assertEqual(rc, 3)
                self.assertIn(detail, error)
                self.assertFalse(self.out.exists())

    def test_malformed_self_pinned_json_refuses(self):
        with self.issued() as (value, path):
            raw = path.read_bytes()
            malformed = b'{"verdict":"pass",' + raw.lstrip()[1:]
            path.write_bytes(malformed)
            entry = bracket.EPOCH_CONTINUATION_REGISTRY[value["continuation_id"]]
            old_pin = entry["file_sha256"]
            entry["file_sha256"] = hashlib.sha256(malformed).hexdigest()
            try:
                loaded, details = self.load()
                self.assertEqual(loaded, ())
                self.assertIn("duplicate_key.verdict", details[0]["detail"])
            finally:
                entry["file_sha256"] = old_pin

    def test_all_acceptance_bytes_and_registry_remain_frozen(self):
        before = copy.deepcopy(bracket.ISSUED_ACCEPTANCE_REGISTRY)
        hashes = {key: hashlib.sha256(entry["path"].read_bytes()).hexdigest() for key, entry in before.items()}
        derivation = self.artifact["derivation_sha256"]
        with self.issued():
            self.assertEqual(self.evaluate()[1], ())
        self.assertEqual(bracket.ISSUED_ACCEPTANCE_REGISTRY, before)
        self.assertEqual({key: hashlib.sha256(entry["path"].read_bytes()).hexdigest() for key, entry in before.items()}, hashes)
        self.assertEqual(bracket.load_calibration_acceptance_bound()["derivation_sha256"], derivation)
        self.assertEqual(hashes[bracket.ACTIVE_ACCEPTANCE_ID], bracket.ANCHOR_V3_R6_ACCEPTANCE_BOUND_SHA256)


if __name__ == "__main__":
    unittest.main()
