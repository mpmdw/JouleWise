"""Defect-shaped regressions for the D1 derivation-only writer mode.

Ruling 46 (cold-gate Fable, 2026-09-10) A1/V1/V2 with addendum A-1/A-5: a
capture taken to BUILD the next acceptance for an identity epoch that no
issued acceptance binds.  Every test below names the exact production call
site in `scripts/validate_powermetrics_fiducial.py::main` that it kills.
"""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
from joulewise.calibration_bracketing import ACCEPTANCE_IDENTITY_FIELDS
from joulewise.calibration_exits import RefusalCode
from joulewise.calibration_ledger import (
    BRACKET_SESSION_SCHEMA,
    BRACKET_SESSION_FINALIZATION_EVENT,
    BRACKET_SESSION_SLOTS,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    SESSION_KIND_DERIVATION,
    T1_FIELDS,
    append_bracket_session_receipt,
    derivation_session_slots,
)
from tests.git_fixture import init_git_fixture
from tests.owned_process_runner import (
    OwnedPublicProcessRunner,
    assert_no_owned_process_group_survivors,
)
import scripts.validate_powermetrics_fiducial as validation_script
from tests.test_calibration_exits import _install_fake_writer_dependencies
from tests.fixtures.epoch_continuation.build import build_issued_continuation
from tests.test_validate_powermetrics_fiducial import documented_keys

REPO_ROOT = Path(__file__).resolve().parents[1]
_ACCEPTANCE_RELATIVE = (
    "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"
)
# The stall deadline the sampler-ack driver allows a freshly spawned fixture
# sampler child.  Liveness backstop only; no assertion depends on its value.
_SAMPLER_ACK_TIMEOUT_S = 30.0


def tearDownModule() -> None:
    assert_no_owned_process_group_survivors()


def _fresh_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _acceptance_epoch() -> dict:
    artifact = json.loads(
        (REPO_ROOT / _ACCEPTANCE_RELATIVE).read_text(encoding="utf-8")
    )
    return dict(artifact["identity_epoch"])


class DerivationOnlyPreflightRefusalTests(unittest.TestCase):
    """Refusals that fire before any hardware, sampler, or ledger work."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.script = REPO_ROOT / "scripts" / "validate_powermetrics_fiducial.py"
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.epoch = _acceptance_epoch()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def _identity(self, name: str, **overrides) -> Path:
        path = self.root / f"{name}.json"
        payload = dict(self.epoch) | overrides
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return path

    def _writer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.script), *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=_fresh_env(),
            check=False,
        )

    def _refusal(self, completed: subprocess.CompletedProcess[str]) -> dict:
        self.assertEqual(
            completed.returncode, 2, completed.stdout + completed.stderr
        )
        stream = completed.stderr.strip() or completed.stdout.strip()
        return json.loads(stream.splitlines()[-1])

    def test_matching_identity_epoch_refuses_because_derivation_only_would_bypass_the_screen(
        self,
    ) -> None:
        """REFUSE: production call site validate_powermetrics_fiducial.main
        (the derivation-only branch's judged-epoch membership clause,
        `if planned_epoch in basis["judged_epochs"]`).

        A matching epoch means the active acceptance DOES judge this machine,
        so an ordinary capture is possible and derivation-only would be a way
        to take a capture the level screen never sees.  The counterfactual
        input is an identity fixture equal to the artifact's own epoch; delete
        the judged-epoch clause and this capture proceeds.
        """

        completed = self._writer(
            "--allow-live",
            "--power-policy",
            self.epoch["power_policy"],
            "--derivation-only",
            "--output-root",
            str(self.root / "matching" / "instrument_validation"),
            "--identity-epoch-json-for-test",
            str(self._identity("matching")),
        )
        payload = self._refusal(completed)
        self.assertEqual(
            payload["code"],
            RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED.value,
        )
        self.assertEqual(
            payload["context"]["acceptance_id"],
            json.loads(
                (REPO_ROOT / _ACCEPTANCE_RELATIVE).read_text(encoding="utf-8")
            )["acceptance_id"],
        )

    def test_standalone_derivation_only_refuses_without_a_declared_session_slot(
        self,
    ) -> None:
        """REFUSE: production call site validate_powermetrics_fiducial.main
        (the derivation-only branch's standalone clause, `if not bracket_mode`).

        A7 rules a derivation night to be ONE registered session; a standalone
        reservation cannot extend past the committed pin, so a standalone
        derivation capture is an ungoverned extension.  The counterfactual is
        a DIFFERING epoch (so the clause above cannot be the one refusing)
        with no `--session-id`.
        """

        completed = self._writer(
            "--allow-live",
            "--power-policy",
            self.epoch["power_policy"],
            "--derivation-only",
            "--output-root",
            str(self.root / "standalone" / "instrument_validation"),
            "--identity-epoch-json-for-test",
            str(self._identity("standalone", os_build="25G83")),
        )
        payload = self._refusal(completed)
        self.assertEqual(
            payload["code"],
            RefusalCode.DERIVATION_ONLY_SESSION_KIND_REQUIRED.value,
        )

    def test_derivation_only_without_allow_live_refuses_quiet_machine_authorization(
        self,
    ) -> None:
        """Clause (a): the mode is a LIVE capture parameter.

        This is composition, not a new gate: `main`'s existing `--allow-live`
        refusal precedes every derivation-only clause, so no ordering of the
        new code can let a derivation-only run reach capture unauthorized.
        """

        completed = self._writer(
            "--power-policy",
            self.epoch["power_policy"],
            "--derivation-only",
            "--output-root",
            str(self.root / "unauthorized" / "instrument_validation"),
            "--identity-epoch-json-for-test",
            str(self._identity("unauthorized", os_build="25G83")),
        )
        payload = self._refusal(completed)
        self.assertEqual(
            payload["code"], RefusalCode.QUIET_MAC_AUTH_REQUIRED.value
        )

    def test_rederive_from_with_derivation_only_refuses_before_any_replay(
        self,
    ) -> None:
        """Kills `main`'s derivation/rederive conflict clause.

        `--rederive-from` replays bytes that already exist and RETURNS 0 on its
        own, so the conflict refusal must precede that branch.  Delete the
        clause and this invocation exits 0 with a replay payload instead of
        refusing.
        """

        source = self.root / "rederive-source"
        source.mkdir(exist_ok=True)
        completed = self._writer(
            "--derivation-only",
            "--rederive-from",
            str(source),
            "--output",
            str(self.root / "rederived.json"),
        )
        payload = self._refusal(completed)
        self.assertEqual(
            payload["code"],
            RefusalCode.WRITER_BRACKET_REDERIVE_CONFLICT.value,
        )


class DerivationOnlyLiveCaptureTests(unittest.TestCase):
    """Ledger-bearing behaviour, driven by the fixture sampler only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name).resolve() / "repo"
        cls.runner = OwnedPublicProcessRunner(Path(cls.tmp.name))
        shutil.copytree(REPO_ROOT / "joulewise", cls.repo / "joulewise")
        (cls.repo / "scripts").mkdir()
        for name in (
            "recover_calibration_ledger.py",
            "reserve_calibration_window_bracket.py",
            "validate_powermetrics_fiducial.py",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, cls.repo / "scripts" / name)
        shutil.copytree(
            REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial",
            cls.repo / "configs" / "calibration" / "powermetrics_fiducial",
        )
        shutil.copy2(
            REPO_ROOT / _ACCEPTANCE_RELATIVE,
            cls.repo / _ACCEPTANCE_RELATIVE,
        )
        cls._pristine_acceptance = (cls.repo / _ACCEPTANCE_RELATIVE).read_bytes()
        cls._pristine_bracketing = (
            cls.repo / "joulewise" / "calibration_bracketing.py"
        ).read_bytes()
        cls.fake_sampler = _install_fake_writer_dependencies(cls.repo)
        init_git_fixture(cls.repo, "-q")
        for key, value in (
            ("user.email", "tests@joulewise.invalid"),
            ("user.name", "JouleWise tests"),
        ):
            subprocess.run(
                ["git", "config", key, value], cwd=cls.repo, check=True
            )
        subprocess.run(["git", "add", "."], cwd=cls.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "derivation-only runtime"],
            cwd=cls.repo,
            check=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_battery_brackets_are_authenticated_and_outside_anchor_spans(self) -> None:
        captures = []
        for duration in (0.0, 2.0):
            self._rekey_acceptance()
            epoch, t1 = self._epoch("25G83")
            token = f"battery-duration-{int(duration)}"
            declared = derivation_session_slots(2)
            ledger, pin, session_id, custody = self._session(
                token, slots=declared, session_kind=SESSION_KIND_DERIVATION,
                epoch=epoch, t1=t1,
            )
            completed = self._writer(
                ledger=ledger, pin=pin, session_id=session_id,
                slot=declared[0], custody=custody[declared[0]], epoch=epoch,
                battery_probe_duration_for_test=duration,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            root = custody[declared[0]]
            evidence = json.loads((root / "instrument_evidence.json").read_text())
            manifest = json.loads((root / "manifest.json").read_text())
            expected_artifacts = {"events.jsonl", "power_trace.csv",
                                  "instrument_evidence.json", "raw/powermetrics.plist"}
            self.assertEqual(set(manifest["artifacts"]), expected_artifacts)
            self.assertEqual(set(evidence["artifact_sha256"]), expected_artifacts - {"instrument_evidence.json"})
            self.assertEqual(set(evidence["battery_float"]), {"pre", "post"})
            stamps = evidence["clock_anchor"]["clock_stamps"]
            anchor_start = stamps["pre_spawn"]["monotonic_before_s"]
            anchor_end = stamps["post_parse"]["monotonic_after_s"]
            for phase in ("pre", "post"):
                observation = evidence["battery_float"][phase]
                raw = (root / observation["raw_path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), observation["raw_stdout_sha256"])
                self.assertTrue(observation["passed"])
                before = observation["monotonic_before_ns"] / 1e9
                after = observation["monotonic_after_ns"] / 1e9
                self.assertLessEqual(after, anchor_start) if phase == "pre" else self.assertGreaterEqual(before, anchor_end)
            self.assertEqual(evidence["battery_float"]["pre"]["monotonic_after_ns"]
                             - evidence["battery_float"]["pre"]["monotonic_before_ns"],
                             int(duration * 1e9))
            deltas = {name: (stamp["monotonic_before_s"] - anchor_start,
                             stamp["monotonic_after_s"] - anchor_start)
                      for name, stamp in stamps.items()}
            captures.append((deltas, evidence["b_fiducial_s"]))
        self.assertEqual(captures[0], captures[1])

    # ---- private-repo acceptance custody ---------------------------------
    def _rekey_acceptance(self) -> dict:
        """Re-key the copied acceptance to THIS synthetic repo's bytes.

        The copied estimator sources are this checkout's, not the issued
        artifact's, so the artifact must re-authenticate against them or the
        writer refuses every capture.  Test custody only: the re-keyed bytes
        never leave the temporary repository and are never issued.
        """

        path = self.repo / _ACCEPTANCE_RELATIVE
        bracketing = self.repo / "joulewise" / "calibration_bracketing.py"
        # Start from the pristine issued bytes every time, so no test's
        # re-key leaks into the next one through the shared repository.
        path.write_bytes(self._pristine_acceptance)
        bracketing.write_bytes(self._pristine_bracketing)
        acceptance = json.loads(path.read_text(encoding="utf-8"))
        acceptance["prospective_rederivation"]["estimator_code_sha256"] = {
            relative: hashlib.sha256((self.repo / relative).read_bytes()).hexdigest()
            for relative in acceptance["prospective_rederivation"][
                "estimator_code_sha256"
            ]
        }
        core = {
            key: value
            for key, value in acceptance.items()
            if key != "derivation_sha256"
        }
        acceptance["derivation_sha256"] = hashlib.sha256(
            json.dumps(
                core,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        old_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        path.write_text(
            json.dumps(acceptance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        source = bracketing.read_text(encoding="utf-8")
        if source.count(old_sha256) != 1:
            raise AssertionError("issued acceptance digest pin shape changed")
        bracketing.write_text(source.replace(old_sha256, new_sha256, 1))
        return acceptance

    # ---- session fixtures -------------------------------------------------
    def _epoch(self, os_build: str) -> tuple[dict, dict]:
        """The epoch and T1 vector the writer will itself compute.

        The reservation must record exactly what the writer plans, or the
        pre-capture slot authentication refuses before any of the derivation
        clauses under test can run.
        """

        epoch = _acceptance_epoch() | {"os_build": os_build}
        t1 = {field: f"value-{field}" for field in T1_FIELDS}
        t1.update(epoch)
        t1.update(
            {
                "powermetrics_sha256": hashlib.sha256(
                    self.fake_sampler.read_bytes()
                ).hexdigest(),
                "anchor_method_version": ACTIVE_CAPTURE_ANCHOR_METHOD,
                "mlx_version": "test-mlx-1",
                "protocol_sha256": hashlib.sha256(
                    (
                        self.repo
                        / "configs"
                        / "calibration"
                        / "powermetrics_fiducial"
                        / "protocol_v3.json"
                    ).read_bytes()
                ).hexdigest(),
            }
        )
        return epoch, t1

    def _session(
        self,
        token: str,
        *,
        slots: tuple[str, ...],
        session_kind: str | None,
        epoch: dict,
        t1: dict,
        continuation_root: Path | None = None,
    ):
        root = self.repo / "sessions" / token
        root.mkdir(parents=True)
        ledger = root / "ledger.jsonl"
        pin = root / "head.json"
        pin.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        if continuation_root is not None:
            # Preserve the real terminal derivation history in the capture's
            # ledger; preflight must cross-check it before opening a capture.
            shutil.copy2(continuation_root / "night/runs/calibration_observation_ledger.jsonl", ledger)
            shutil.copy2(continuation_root / "night/runs/calibration_ledger_head_pin.json", pin)
        subprocess.run(
            ["git", "add", str(pin.relative_to(self.repo))],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", f"pin {token}"], cwd=self.repo, check=True
        )
        session_id = f"session-{token}"
        runs_root = root / "runs"
        custody = {
            slot: runs_root / "instrument_validation" / f"{session_id}-{slot}"
            for slot in slots
        }
        kwargs = (
            {}
            if session_kind is None
            else {"session_kind": session_kind, "declared_slots": slots}
        )
        append_bracket_session_receipt(
            ledger,
            session_id=session_id,
            window_id=f"window-{token}",
            plan_id=f"plan-{token}",
            plan_sha256="a" * 64,
            evidence_root_id=f"evidence-{token}",
            runs_root=runs_root,
            slots={
                slot: {
                    "attempt_id": f"{session_id}-{slot}",
                    "custody_locator": str(custody[slot]),
                    "identity_epoch": epoch,
                    "t1_bindings": t1,
                }
                for slot in slots
            },
            head_pin_path=pin,
            require_committed_pin=False,
            repo_root=self.repo,
            **kwargs,
        )
        return ledger, pin, session_id, custody

    def _writer(
        self,
        *,
        ledger: Path,
        pin: Path,
        session_id: str,
        slot: str,
        custody: Path,
        epoch: dict,
        derivation_only: bool = True,
        extra_env: dict[str, str] | None = None,
        battery_probe_duration_for_test: float | None = None,
    ):
        identity = custody.parent / f"{session_id}-{slot}-identity.json"
        identity.parent.mkdir(parents=True, exist_ok=True)
        identity.write_text(json.dumps(epoch) + "\n", encoding="utf-8")
        command = [
            sys.executable,
            str(self.repo / "scripts" / "validate_powermetrics_fiducial.py"),
            "--allow-live",
            "--power-policy",
            epoch["power_policy"],
            "--ledger",
            str(ledger),
            "--head-pin",
            str(pin),
            "--session-id",
            session_id,
            "--slot",
            slot,
            "--attempt-id",
            f"{session_id}-{slot}",
            "--output-root",
            str(custody.parent),
            "--sampler-binary",
            str(self.fake_sampler),
            "--sampler-direct-for-test",
            "--time-scale-for-test",
            "0.001",
            "--sampler-ready-timeout-s",
            str(_SAMPLER_ACK_TIMEOUT_S),
            "--rollover-timeout-s",
            "1.0",
            "--identity-epoch-json-for-test",
            str(identity),
        ]
        if derivation_only:
            command.append("--derivation-only")
        if battery_probe_duration_for_test is not None:
            command.extend([
                "--battery-probe-fixture-for-test",
                str(REPO_ROOT / "tests/fixtures/battery_float/float.ioreg"),
                "--battery-probe-duration-for-test", str(battery_probe_duration_for_test),
            ])
        return self.runner.run(
            command,
            cwd=self.repo,
            env={
                **_fresh_env(),
                "JW_FAKE_SAMPLER_MODE": "normal",
                "JW_FAKE_HW_MODEL": epoch["hardware_model"],
                "JW_FAKE_OS_BUILD": epoch["os_build"],
                "JW_FAKE_SAMPLER_ELAPSED_NS": "200000",
                "JW_FAKE_TIME_SCALE": "0.001",
                "JW_FAKE_TIME_ORIGIN": str(time.time()),
                **(extra_env or {}),
            },
        )

    def _refusal(self, completed) -> dict:
        self.assertEqual(
            completed.returncode, 2, completed.stdout + completed.stderr
        )
        stream = completed.stderr.strip() or completed.stdout.strip()
        return json.loads(stream.splitlines()[-1])

    # ---- tests ------------------------------------------------------------
    def test_ordinary_continued_epoch_capture_requires_registered_continuation(self):
        """The real writer CLI reaches a fixture capture only with a valid pin."""
        acceptance = self._rekey_acceptance()
        epoch, t1 = self._epoch("25G83")
        continuation_root = Path(self.tmp.name) / "continuation"
        _, registry = build_issued_continuation(
            continuation_root, acceptance_path=self.repo / _ACCEPTANCE_RELATIVE,
        )
        ledger, pin, session_id, custody = self._session(
            "ordinary-continued", slots=BRACKET_SESSION_SLOTS,
            session_kind=None, epoch=epoch, t1=t1, continuation_root=continuation_root,
        )
        args = dict(ledger=ledger, pin=pin, session_id=session_id, slot="pre",
                    custody=custody["pre"], epoch=epoch, derivation_only=False)
        before_ledger = ledger.read_bytes()
        refusal = self._refusal(self._writer(**args))
        self.assertEqual(refusal["code"], RefusalCode.FROZEN_PROTOCOL_INVALID.value)
        self.assertEqual(refusal["context"]["reason"], "acceptance_artifact_epoch_mismatch")
        self.assertEqual(ledger.read_bytes(), before_ledger)
        self.assertFalse(custody["pre"].exists())

        # Install the test pin in the copied subprocess runtime only. The
        # production registry remains empty and all issued bytes stay frozen.
        source_path = self.repo / "joulewise/calibration_bracketing.py"
        pristine = source_path.read_bytes()
        serializable = {key: {**entry, "path": str(entry["path"])} for key, entry in registry.items()}
        addition = (
            f"\nEPOCH_CONTINUATION_REGISTRY.update({serializable!r})\n"
        ).encode()
        try:
            source_path.write_bytes(pristine + addition)
            completed = self._writer(**args)
        finally:
            source_path.write_bytes(pristine)
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).digest(), hashlib.sha256(pristine).digest())
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        for name in ("instrument_evidence.json", "manifest.json"):
            payload = json.loads((custody["pre"] / name).read_bytes())
            self.assertIn("acceptance_preflight", payload)
            record = payload["acceptance_preflight"]
            self.assertIn("judged_epochs", record)
            self.assertEqual(record["judged_epochs"], [acceptance["identity_epoch"], epoch])
            self.assertEqual(record["judged_epochs_basis"], "ledger_snapshot")
            self.assertEqual(record["continuation_refusals"], [])
            self.assertNotIn("derivation_only", payload)
        finalized = [json.loads(line) for line in ledger.read_text().splitlines()
                     if json.loads(line).get("event") == BRACKET_SESSION_FINALIZATION_EVENT
                     and json.loads(line).get("session_id") == session_id]
        self.assertEqual(len(finalized), 1)
        self.assertEqual(finalized[0]["disposition"], "valid")

    def test_bracket_kind_session_refuses_a_derivation_only_capture(self) -> None:
        """REFUSE: production call site validate_powermetrics_fiducial.main
        (the derivation-only branch's declared-kind clause,
        `declared_shape["session_kind"] != SESSION_KIND_DERIVATION`).

        The counterfactual is a session whose open receipt declares NO kind --
        the historical two-slot bracket shape, which reads back as kind
        `bracket`.  Its slots are measurement endpoints and are judged by the
        active acceptance's level screen; filling one derivation-only would
        write an unscreened endpoint.  Delete the clause and the capture runs.
        """

        self._rekey_acceptance()
        epoch, t1 = self._epoch("25G83")
        ledger, pin, session_id, custody = self._session(
            "bracket-kind",
            slots=BRACKET_SESSION_SLOTS,
            session_kind=None,
            epoch=epoch,
            t1=t1,
        )
        payload = self._refusal(
            self._writer(
                ledger=ledger,
                pin=pin,
                session_id=session_id,
                slot="pre",
                custody=custody["pre"],
                epoch=epoch,
            )
        )
        self.assertEqual(
            payload["code"],
            RefusalCode.DERIVATION_ONLY_SESSION_KIND_REQUIRED.value,
        )
        self.assertEqual(payload["context"]["session_kind"], "bracket")
        self.assertFalse(custody["pre"].exists())

    def test_derivation_slot_of_a_differing_epoch_appends_valid_with_provenance(
        self,
    ) -> None:
        """Kills the screen-basis and `preflight_systematic_screen_s = None`
        clauses together.

        A 25G83 capture judged by r6's 25F84 level screen is D-102 cl.2's
        "a threshold that judges itself" inverted: it fits the NEW screen to
        the OLD one.  This test asserts the disposition is `valid`, that the
        hashed evidence and manifest carry `derivation_only`, `screen_basis`
        and the DIAGNOSTIC `exceeds_prior_level_screen`, and that the ledger
        row's identity epoch is stale against r6 on exactly `os_build` -- so
        r6 still refuses the row for measurement use.
        """

        acceptance = self._rekey_acceptance()
        epoch, t1 = self._epoch("25G83")
        declared = derivation_session_slots(2)
        ledger, pin, session_id, custody = self._session(
            "derivation-valid",
            slots=declared,
            session_kind=SESSION_KIND_DERIVATION,
            epoch=epoch,
            t1=t1,
        )
        completed = self._writer(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot=declared[0],
            custody=custody[declared[0]],
            epoch=epoch,
        )
        self.assertEqual(
            completed.returncode, 0, completed.stdout + completed.stderr
        )
        out_dir = custody[declared[0]]
        evidence = json.loads(
            (out_dir / "instrument_evidence.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (out_dir / "manifest.json").read_text(encoding="utf-8")
        )
        for payload in (evidence, manifest):
            self.assertIs(payload["derivation_only"], True)
            self.assertEqual(set(payload["screen_basis"]), documented_keys("screen_basis"))
            self.assertEqual(
                payload["screen_basis"]["acceptance_id"],
                acceptance["acceptance_id"],
            )
            self.assertEqual(
                payload["screen_basis"]["artifact_sha256"],
                hashlib.sha256(
                    (self.repo / _ACCEPTANCE_RELATIVE).read_bytes()
                ).hexdigest(),
            )
            self.assertEqual(
                payload["screen_basis"]["preflight_level_screen_s"],
                acceptance["decimal_derivation"]["ratified_operatives"][
                    "preflight_level_screen_s"
                ],
            )
            self.assertEqual(
                payload["screen_basis"]["epoch"], acceptance["identity_epoch"]
            )
            self.assertEqual(payload["screen_basis"]["judged_epochs"], [acceptance["identity_epoch"]])
            self.assertEqual(payload["screen_basis"]["judged_epochs_basis"], "ledger_snapshot")
            self.assertIn("exceeds_prior_level_screen", payload)
        # The bound of a healthy fixture capture is far below r6's screen, so
        # the diagnostic is false here; the true case is the next test.
        self.assertIs(evidence["exceeds_prior_level_screen"], False)

        rows = [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
        ]
        finalization = next(
            row
            for row in rows
            if row.get("schema_version") == BRACKET_SESSION_SCHEMA
            and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
        )
        self.assertEqual(finalization["disposition"], "valid")
        self.assertEqual(finalization["slot"], declared[0])
        stale = [
            field
            for field in ACCEPTANCE_IDENTITY_FIELDS
            if finalization["identity_epoch"].get(field)
            != acceptance["identity_epoch"].get(field)
        ]
        self.assertEqual(stale, ["os_build"])

    def _healthy_derivation_capture(self, name, *, slot_count=1, extra_env=None):
        """Run `slot_count` real derivation slots to success, in order."""

        self._rekey_acceptance()
        epoch, t1 = self._epoch("25G83")
        declared = derivation_session_slots(2)
        ledger, pin, session_id, custody = self._session(
            name,
            slots=declared,
            session_kind=SESSION_KIND_DERIVATION,
            epoch=epoch,
            t1=t1,
        )
        runs = []
        for slot in declared[:slot_count]:
            completed = self._writer(
                ledger=ledger,
                pin=pin,
                session_id=session_id,
                slot=slot,
                custody=custody[slot],
                epoch=epoch,
                extra_env=extra_env,
            )
            self.assertEqual(
                completed.returncode, 0, completed.stdout + completed.stderr
            )
            runs.append(completed)
        return runs if slot_count > 1 else runs[0]

    def _assert_custody_timing_receipt(self, completed):
        """The success receipt must carry the healthy-night custody timing.

        `custody_elapsed_s` is the seconds the finalization operation's
        custody allowance had been running when the receipt was written, and
        `observations` is how many custody-bearing observation rows that pass
        covered.  Together they are the only record a SUCCESSFUL night leaves
        of how long its custody passes take -- the quantity the install-time
        headroom gate is sized against -- because the writer's custody
        deadline prints no telemetry and only an expiry carries the timing
        into a refusal document.

        The writer's standard-error contract is unchanged by the new fields.
        That contract has two parts, and a healthy capture is judged against
        both.  (1) Exactly one JSON line on a REFUSAL -- so a healthy capture,
        which does not refuse, writes no refusal line at all.  (2) No bounded-
        pass telemetry: the writer builds its custody deadline with
        `telemetry_stream=None`, so no `calibration_custody_progress` or
        `calibration_custody_complete` line may appear, because standard error
        is reserved for that single refusal line.  Operational writer events
        (`calibration_writer_arm_authorized`, the post-teardown census) are a
        third thing and are unchanged; they are still one JSON object per
        line, which is what lets a caller parse standard error line by line.
        Standard output stays exactly ONE JSON object: the receipt.

        `custody_passes` is the third field of the same record: how many of
        those whole-corpus sweeps actually opened and hashed the bytes.  A
        healthy slot makes exactly TWO -- the preflight snapshot taken before
        the writer lease exists, and one pass under the lease whose verified
        set the enforcing readiness gate and the slot validation then reuse
        (lane CUSTODY-PASS-MEMO-01).  Four, the count before the memo landed,
        is what made the install-time headroom gate demand a pass four times
        faster than the probe actually has to be.
        """

        receipt = json.loads(completed.stdout)
        elapsed = receipt["custody_elapsed_s"]
        self.assertNotIsInstance(elapsed, bool)
        self.assertIsInstance(elapsed, float)
        self.assertGreaterEqual(elapsed, 0.0)
        # A whole fixture capture runs in well under the 120 s night budget;
        # an implausible value means the field is not the deadline's clock.
        self.assertLess(elapsed, 120.0)
        observations = receipt["observations"]
        self.assertNotIsInstance(observations, bool)
        self.assertIsInstance(observations, int)
        self.assertGreaterEqual(observations, 0)
        passes = receipt["custody_passes"]
        self.assertNotIsInstance(passes, bool)
        self.assertIsInstance(passes, int)
        # Exactly two: not "at most", because a memo that never reused would
        # report four and a memo that reused across the lease boundary would
        # report one -- and one is unsound, not an improvement.
        self.assertEqual(
            2, passes,
            "a healthy slot must read the whole corpus exactly twice; "
            "WRITER_CUSTODY_PASSES in joulewise/night_agent_install.py "
            "bounds this count at the worst case of three",
        )
        stderr_events = [
            json.loads(line)
            for line in completed.stderr.splitlines()
            if line.strip()
        ]
        for event in stderr_events:
            self.assertNotIn(
                event.get("event"),
                {"calibration_custody_progress", "calibration_custody_complete"},
                completed.stderr,
            )
            self.assertNotEqual(
                event.get("schema"), "joulewise.calibration_refusal.v1",
                completed.stderr,
            )
        # One object, not a stream: json.loads over the WHOLE stream would
        # raise "Extra data" if the receipt ever gained a second line.
        self.assertEqual(json.loads(completed.stdout), receipt)
        return receipt

    def test_success_receipt_carries_the_healthy_custody_timing(self) -> None:
        """A night that SUCCEEDS must still report what its custody pass cost.

        Two slots, not one, because `observations` is legitimately 0 on the
        first: a session whose slots are all still unfinalized holds no
        custody-bearing observation for the pass to cover.  The second slot's
        preparation reads the row the first one finalized, so its count must
        RISE.  A hardcoded zero -- or a reading taken off the fresh
        finalization allowance, which counts nothing -- passes the first
        assertion and fails this one.
        """

        first, second = self._healthy_derivation_capture(
            "derivation-timing", slot_count=2,
        )
        first_receipt = self._assert_custody_timing_receipt(first)
        second_receipt = self._assert_custody_timing_receipt(second)
        self.assertEqual(first_receipt["observations"], 0)
        self.assertGreater(second_receipt["observations"], 0)
        # The new fields are additive: the terminal receipt a desk reader
        # already depends on is unchanged.
        for receipt in (first_receipt, second_receipt):
            self.assertEqual(receipt["status"], "valid")
            self.assertIn("ledger_head_pin_candidate", receipt)
            self.assertIs(receipt["claim_evaluation_blocked_until_pin_commit"], True)

    def test_capture_succeeds_with_the_night_budget_marker_inherited(self) -> None:
        """The chain's exported budget marker reaches the writer by inheritance.

        `JOULEWISE_NIGHT_CUSTODY_BUDGET_S` is exported once by the night chain,
        so every process the chain starts -- including this writer -- carries
        it.  Under the marker, any custody read that was handed no deadline of
        its own is REFUSED rather than run unbounded.  The writer threads its
        own deadline through every custody entry, so the marker must be inert
        here: a healthy capture still finalizes, and still reports its timing.
        No other test in this module runs the writer with the marker set --
        both this module and the custody-hang fixture scrub the environment
        down to PATH -- so without this test the inheritance path is unproven
        on the success side.
        """

        completed = self._healthy_derivation_capture(
            "derivation-marker",
            extra_env={"JOULEWISE_NIGHT_CUSTODY_BUDGET_S": "120"},
        )
        receipt = self._assert_custody_timing_receipt(completed)
        self.assertEqual(receipt["status"], "valid")

    def test_ordinary_mode_refuses_a_derivation_kind_slot_and_appends_nothing(
        self,
    ) -> None:
        """REFUSE: production call site
        validate_powermetrics_fiducial._CaptureLedgerLifecycle.begin
        (the derivation-kind guard, before the writer lease).

        The dangerous direction is not only "derivation-only fills a bracket
        slot"; it is also "the ORDINARY writer fills a derivation slot".  A
        derivation slot exists because no issued acceptance judges this
        machine, so the ordinary path would classify the capture against r6's
        level screen `0.032898493715362` -- D-102 cl.2 inverted, and the same
        defect addendum A-1 cured on the recovery finalization path.

        The epoch here deliberately MATCHES the acceptance, because that is the
        only state in which the ordinary writer clears its own epoch preflight
        and actually reaches the slot.  The counterfactual is this identical
        invocation with `--derivation-only` removed; delete the guard and the
        capture runs and is screened by r6.  The ledger must be byte-identical
        after the refusal: the guard sits before the writer lease.
        """

        self._rekey_acceptance()
        epoch, t1 = self._epoch(_acceptance_epoch()["os_build"])
        declared = derivation_session_slots(2)
        ledger, pin, session_id, custody = self._session(
            "ordinary-into-derivation",
            slots=declared,
            session_kind=SESSION_KIND_DERIVATION,
            epoch=epoch,
            t1=t1,
        )
        before = ledger.read_bytes()
        payload = self._refusal(
            self._writer(
                ledger=ledger,
                pin=pin,
                session_id=session_id,
                slot=declared[0],
                custody=custody[declared[0]],
                epoch=epoch,
                derivation_only=False,
            )
        )
        self.assertEqual(
            payload["code"],
            RefusalCode.DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY.value,
        )
        self.assertEqual(payload["context"]["session_kind"], "derivation")
        self.assertEqual(payload["context"]["slot"], declared[0])
        # Nothing appended, no custody, session untouched.
        self.assertEqual(ledger.read_bytes(), before)
        self.assertFalse(custody[declared[0]].exists())

    def test_ordinary_artifact_top_level_key_sets_require_deliberate_schema_changes(
        self,
    ) -> None:
        """The guard is kind-scoped, not a blanket ordinary-path refusal.

        Same ordinary invocation at a BRACKET-kind slot on the epoch the
        acceptance binds still captures and finalizes `valid`.  Widen the
        guard to every session and this goes red.
        """

        self._rekey_acceptance()
        epoch, t1 = self._epoch(_acceptance_epoch()["os_build"])
        ledger, pin, session_id, custody = self._session(
            "ordinary-into-bracket",
            slots=BRACKET_SESSION_SLOTS,
            session_kind=None,
            epoch=epoch,
            t1=t1,
        )
        completed = self._writer(
            ledger=ledger,
            pin=pin,
            session_id=session_id,
            slot="pre",
            custody=custody["pre"],
            epoch=epoch,
            derivation_only=False,
        )
        self.assertEqual(
            completed.returncode, 0, completed.stdout + completed.stderr
        )
        rows = [
            json.loads(line)
            for line in ledger.read_text(encoding="utf-8").splitlines()
        ]
        finalization = next(
            row
            for row in rows
            if row.get("schema_version") == BRACKET_SESSION_SCHEMA
            and row.get("event") == BRACKET_SESSION_FINALIZATION_EVENT
        )
        self.assertEqual(finalization["disposition"], "valid")
        evidence = json.loads(
            (custody["pre"] / "instrument_evidence.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertNotIn("derivation_only", evidence)
        self.assertNotIn("screen_basis", evidence)
        # Round-4's ordinary successful capture shape, pinned deliberately.
        # Additions/removals require an explicit artifact-contract decision.
        self.assertEqual(set(evidence), {
            "schema_version", "protocol_id", "validation_id", "status", "reasons",
            "anchor_method_version", "b_fiducial_s",
            "residual_median_s_diagnostic_only", "residual_p95_s_diagnostic_only",
            "residual_region_method", "residual_region_coverage_assumption",
            "residual_region_coverage_resolution_s", "baseline_w", "robust_sigma_w",
            "pulse_count", "all_pulses_detected", "spurious_plateau_count",
            "bindings", "binding_evidence", "artifact_sha256", "pulses",
            "capture_wall_time_s", "max_age_s", "clock_anchor",
            "clock_anchor_resolved", "acceptance_preflight",
        })
        manifest = json.loads((custody["pre"] / "manifest.json").read_bytes())
        self.assertEqual(set(manifest), {
            "schema_version", "validation_id", "protocol_id", "pulse_count",
            "artifacts", "acceptance_preflight",
        })
        for payload in (evidence, manifest):
            self.assertEqual(set(payload["acceptance_preflight"]), documented_keys("acceptance_preflight"))
        self.assertEqual(evidence["acceptance_preflight"], manifest["acceptance_preflight"])

class CaptureClassificationTests(unittest.TestCase):
    """`_classify_capture` at the function level, no capture, no CLI.

    Ruling 46 V2's "diagnostic, never a refusal" cannot be proven end to end:
    the fixture sampler's bound is ~9.3e-05 s (it tracks
    sampling_interval_ms x --time-scale-for-test), r6's level screen is
    0.032898493715362, and closing that factor of ~354 needs a ~17 minute
    capture.  Lowering the screen instead is blocked by the level-screen clause
    of `joulewise.calibration_bracketing._valid_acceptance_bound`, which
    requires max(member values) quantized to 1e-15 to equal
    `preflight_level_screen_s`.  The
    bound and the screen basis are therefore INJECTED here, into the smallest
    production function that computes both outputs, so the TRUE branch is a
    real assertion against real production code rather than a skipped test.
    """

    SCREEN_BASIS = {
        "acceptance_id": "d079_calibration_acceptance_v2_n17_r7",
        "artifact_sha256": "a" * 64,
        "preflight_level_screen_s": "0.032898493715362",
        "epoch": {"os_build": "25F84"},
    }

    def test_bound_above_the_prior_screen_is_diagnosed_but_stays_valid(
        self,
    ) -> None:
        """Kills the fold of the diagnostic into the disposition.

        This is the counterfactual the CLI cannot reach: a derivation-only
        capture whose bound EXCEEDS the prior epoch's level screen.  No
        acceptance judges this epoch, so `preflight_systematic_screen_s` is
        None and the disposition must stay `valid`; the excess is recorded and
        goes to the screen-challenge gate, which halts issuance for Ed rather
        than editing corpus membership.  Route the diagnostic back into the
        disposition and this row becomes `systematic-invalid`.
        """

        disposition, exceeds = validation_script._classify_capture(
            evidence_status="valid",
            bound_lexeme="0.040000000000000",
            preflight_systematic_screen_s=None,
            screen_basis=self.SCREEN_BASIS,
        )
        self.assertEqual(disposition, "valid")
        self.assertIs(exceeds, True)

    def test_bound_below_the_prior_screen_is_valid_and_not_diagnosed(
        self,
    ) -> None:
        """The FALSE branch, at the same seam as the TRUE one."""

        disposition, exceeds = validation_script._classify_capture(
            evidence_status="valid",
            bound_lexeme="0.000092981887817",
            preflight_systematic_screen_s=None,
            screen_basis=self.SCREEN_BASIS,
        )
        self.assertEqual(disposition, "valid")
        self.assertIs(exceeds, False)

    def test_an_invalid_derivation_capture_is_ordinary_invalid_never_systematic(
        self,
    ) -> None:
        """No `systematic-invalid` disposition exists for this epoch (V2)."""

        disposition, exceeds = validation_script._classify_capture(
            evidence_status="invalid",
            bound_lexeme="0.040000000000000",
            preflight_systematic_screen_s=None,
            screen_basis=self.SCREEN_BASIS,
        )
        self.assertEqual(disposition, "ordinary-invalid")
        self.assertIs(exceeds, True)

    def test_the_ordinary_path_still_screens_and_records_no_diagnostic(
        self,
    ) -> None:
        """The other side of the same seam: with an acceptance that DOES judge
        this epoch, the level screen still produces `systematic-invalid`, and
        no diagnostic is computed at all."""

        screen = Decimal(self.SCREEN_BASIS["preflight_level_screen_s"])
        over, exceeds_over = validation_script._classify_capture(
            evidence_status="valid",
            bound_lexeme="0.040000000000000",
            preflight_systematic_screen_s=screen,
            screen_basis=None,
        )
        self.assertEqual(over, "systematic-invalid")
        self.assertIsNone(exceeds_over)
        under, exceeds_under = validation_script._classify_capture(
            evidence_status="valid",
            bound_lexeme="0.000092981887817",
            preflight_systematic_screen_s=screen,
            screen_basis=None,
        )
        self.assertEqual(under, "valid")
        self.assertIsNone(exceeds_under)




class WriterCustodyDeadlineTests(unittest.TestCase):
    def _ordinary_abandon(self, pause_at=None):
        from unittest import mock
        from joulewise import calibration_ledger as ledger
        from tests import test_calibration_ledger as ledger_tests

        fixture = ledger_tests.CalibrationLedgerTests(methodName="runTest")
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        custody = fixture._custody("ordinary-abandon")
        (custody / "power_trace.csv").write_text("timestamp_s,power_w\n99.0,1.0\n")
        lifecycle = validation_script._CaptureLedgerLifecycle(
            ledger_path=fixture.ledger, head_pin_path=fixture.pin,
            attempt_id="ordinary-abandon", custody_locator=str(custody),
            identity_epoch=fixture.epoch, t1_bindings=fixture.t1,
            require_committed_pin=False, custody_deadline=ledger.CustodyDeadline(2),
        )
        self.addCleanup(lifecycle.writer_lease.release)
        lifecycle.begin()
        before = fixture.ledger.read_bytes(), fixture.pin.read_bytes()
        before_rows = [json.loads(line) for line in before[0].splitlines()]
        self.assertEqual(before_rows[-1]["event"], "reservation")
        self.assertEqual(before_rows[-1]["disposition"], "pending")
        real_hashes = validation_script.ledger_artifact_hashes
        real_finalize = validation_script.finalize_attempt_receipt
        hashes_seen = []

        def expire_after_hashing():
            lifecycle.custody_deadline.check()
            self.assertTrue(hashes_seen)
            time.sleep(lifecycle.custody_deadline.remaining() + 0.02)

        def hash_then_pause(*args, **kwargs):
            hashes = real_hashes(*args, **kwargs)
            self.assertEqual(set(hashes), set(ledger.GOVERNED_ARTIFACTS))
            hashes_seen.append(hashes)
            if pause_at == "hash_return":
                expire_after_hashing()
            return hashes

        def finalize_after_pause(*args, **kwargs):
            if pause_at == "finalizer_entry":
                expire_after_hashing()
            return real_finalize(*args, **kwargs)

        refusal = None
        with (
            mock.patch.object(validation_script, "ledger_artifact_hashes",
                              side_effect=hash_then_pause),
            mock.patch.object(validation_script, "finalize_attempt_receipt",
                              side_effect=finalize_after_pause),
        ):
            try:
                receipt = lifecycle.abandon("fixture interruption")
            except ledger.CalibrationLedgerError as exc:
                refusal = exc.code
        after = fixture.ledger.read_bytes(), fixture.pin.read_bytes()
        after_rows = [json.loads(line) for line in after[0].splitlines()]
        appended_events = [row["event"] for row in after_rows[len(before_rows):]]
        self.assertEqual(len(hashes_seen), 1)
        if pause_at:
            self.assertEqual(
                refusal, RefusalCode.LEDGER_CUSTODY_TIMEOUT,
                f"expired abandonment appended {appended_events}; ledger_changed={after != before}",
            )
            self.assertEqual(after, before)
            # The pending attempt already has its reservation intent; no new
            # append-intent or finalization may follow the expired custody pass.
            self.assertEqual(appended_events, [])
            self.assertFalse(lifecycle.closed)
        else:
            self.assertIsNone(refusal)
            self.assertEqual(receipt["disposition"], "abandoned")
            self.assertEqual(dict(receipt["artifact_sha256"]), hashes_seen[0])
            self.assertEqual(appended_events, ["append-intent", "finalization"])
            self.assertEqual(after[1], before[1])
            self.assertTrue(lifecycle.closed)
        with ledger.CalibrationWriterLease(fixture.ledger):
            pass

    def test_ordinary_abandon_refuses_expiry_after_hashing_without_append(self):
        self._ordinary_abandon("hash_return")

    def test_ordinary_abandon_forwards_deadline_to_finalizer_append_guard(self):
        self._ordinary_abandon("finalizer_entry")

    def test_ordinary_abandon_within_budget_appends_abandoned_receipt(self):
        self._ordinary_abandon()

    def _stall(self, after_reads, *, night_budget_marker=False):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, install_read_barrier
        with CustodyFixture() as fixture:
            w = fixture.witness
            state = w._state_real_writer("writer-custody-stall")
            marker = install_read_barrier(fixture, after_reads=after_reads)
            before = fixture.bytes()
            command = [sys.executable, str(w.writer_script),
                       *w._writer_capture_args(state)]
            if "--custody-budget-s" in w.writer_script.read_text():
                command += ["--custody-budget-s", "3"]
            env = w._writer_env(state, mode="normal") | fixture.env
            if night_budget_marker:
                # What the night chain exports, inherited by the writer it
                # starts. The writer threads its own deadline through every
                # custody entry, so the marker must change nothing here: the
                # blocked read is still cut by the writer's OWN allowance and
                # still refuses `calibration_ledger_custody_timeout`, not the
                # marker's `calibration_ledger_custody_invalid`.
                env = env | {"JOULEWISE_NIGHT_CUSTODY_BUDGET_S": "120"}
            completed, elapsed = fixture.run(command, env=env)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertLess(elapsed, 5)
            self.assertIn('"code": "calibration_ledger_custody_timeout"', completed.stderr)
            self.assertEqual(fixture.bytes(), before)
            self.assertFalse(Path(state["custody_locator"]).exists())
            reads = [json.loads(line) for line in marker.read_text().splitlines()]
            self.assertEqual(len(reads), after_reads + 1)
            refusal = json.loads(fixture.refusal.read_text())
            self.assertEqual(refusal["phase"], "writer_preflight" if after_reads == 0 else "under_lease")
            self.assertTrue(refusal["existing_session"])
            self.assertEqual(refusal["session_id"], state["session_id"])
            fixture.assert_lease_reacquirable()
            fixture.assert_workers_gone(completed)

    def test_writer_preflight_stall_refuses_without_starting_slot(self):
        self._stall(0)

    def test_writer_stall_under_the_inherited_night_marker_still_times_out(self):
        """The marker must not displace the writer's own custody timeout."""
        self._stall(0, night_budget_marker=True)
        self._stall(1, night_budget_marker=True)

    def test_writer_under_lease_stall_preserves_open_session(self):
        self._stall(1)

    def test_final_artifact_timeout_preserves_existing_session(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture, install_read_barrier
        with CustodyFixture() as fixture:
            w = fixture.witness
            state = w._state_real_writer("writer-final-custody-stall")
            custody = w._complete_custody(state["session_id"], "pre")
            install_read_barrier(fixture)
            fixture.env["JW_CUSTODY_BARRIER_TARGET"] = str(custody / "events.jsonl")
            before = fixture.bytes()
            # This calls the real finalization lifecycle under its real lease;
            # no sampler or hardware is involved in the fixture.
            code = (
                "from pathlib import Path; "
                "from scripts.validate_powermetrics_fiducial import _CaptureLedgerLifecycle; "
                "from joulewise.calibration_ledger import CustodyDeadline,CalibrationLedgerError; "
                f"l=_CaptureLedgerLifecycle(ledger_path=Path({str(fixture.ledger)!r}),"
                f"head_pin_path=Path({str(fixture.pin)!r}),attempt_id={state['attempt_id']!r},"
                f"custody_locator={str(custody)!r},identity_epoch={state['epoch']!r},"
                f"t1_bindings={state['t1']!r},session_id={state['session_id']!r},slot='pre',"
                "custody_deadline=CustodyDeadline(0.5)); "
                "l.writer_lease.acquire();l.begun=True\n"
                "try:\n l.finalize('valid')\nexcept CalibrationLedgerError as e:\n print(e.code.value)\n raise SystemExit(2)\n"
            )
            completed, _ = fixture.run([sys.executable, "-B", "-c", code])
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(completed.stdout.strip(), "calibration_ledger_custody_timeout")
            self.assertEqual(fixture.bytes(), before)
            fixture.assert_lease_reacquirable()
            fixture.assert_workers_gone(completed)

    def test_early_typed_writer_refusal_writes_document_and_preserves_collision(self):
        from tests.calibration_exits_fixtures.custody_hang import CustodyFixture
        with CustodyFixture() as fixture:
            fixture.refusal.write_bytes(b"prior\n")
            completed, _ = fixture.run([
                sys.executable, str(fixture.witness.writer_script),
                "--ledger", str(fixture.ledger), "--head-pin", str(fixture.pin),
            ])
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(fixture.refusal.read_bytes(), b"prior\n")
            documents = list(fixture.repo.glob("calibration-refusal.json.*.json"))
            self.assertEqual(len(documents), 1)
            refusal = json.loads(documents[0].read_text())
            self.assertEqual(refusal["code"], RefusalCode.QUIET_MAC_AUTH_REQUIRED.value)
            self.assertEqual(refusal["phase"], "writer_preflight")


if __name__ == "__main__":
    unittest.main()
