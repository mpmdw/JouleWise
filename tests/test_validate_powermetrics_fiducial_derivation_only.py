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
from tests.test_calibration_exits import _install_fake_writer_dependencies

REPO_ROOT = Path(__file__).resolve().parents[1]
_ACCEPTANCE_RELATIVE = (
    "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
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
        """Kills `main`'s empty-stale-field refusal.

        A matching epoch means the active acceptance DOES judge this machine,
        so an ordinary capture is possible and derivation-only would be a way
        to take a capture the level screen never sees.  The counterfactual
        input is an identity fixture equal to the artifact's own epoch; delete
        the `if not stale_fields` clause and this capture proceeds.
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
        """Kills `main`'s `if not bracket_mode` derivation refusal.

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

    # ---- private-repo acceptance custody ---------------------------------
    def _rekey_acceptance(self, *, maximum_s: str | None = None) -> dict:
        """Re-key the copied acceptance to THIS synthetic repo's bytes.

        The copied estimator sources are this checkout's, not the issued
        artifact's, so the artifact must re-authenticate against them or the
        writer refuses every capture.  `maximum_s` additionally rewrites the
        corpus maximum that the level screen is quantized from, which is how a
        test drives a real capture ABOVE the prior epoch's screen without
        touching the physical bound.  Test custody only: the re-keyed bytes
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
        if maximum_s is not None:
            derivation = acceptance["decimal_derivation"]
            derivation["source_statistics"]["maximum_s"] = maximum_s
            derivation["rounding"]["preflight_level_screen"]["value_s"] = maximum_s
            derivation["ratified_operatives"]["preflight_level_screen_s"] = maximum_s
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
            },
        )

    def _refusal(self, completed) -> dict:
        self.assertEqual(
            completed.returncode, 2, completed.stdout + completed.stderr
        )
        stream = completed.stderr.strip() or completed.stdout.strip()
        return json.loads(stream.splitlines()[-1])

    # ---- tests ------------------------------------------------------------
    def test_bracket_kind_session_refuses_a_derivation_only_capture(self) -> None:
        """Kills `main`'s `session_kind != SESSION_KIND_DERIVATION` clause.

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

    @unittest.skip(
        "UNCOVERED CLAUSE, seat S1: the TRUE branch of "
        "exceeds_prior_level_screen needs a capture whose bound exceeds r6's "
        "level screen 0.032898493715362. The fixture sampler's bound is "
        "~9.3e-05 s (it tracks sampling_interval_ms x --time-scale-for-test), "
        "so reaching the screen needs a time scale ~0.35, i.e. a ~17 min "
        "capture. Lowering the screen instead is blocked: "
        "_valid_acceptance_bound (calibration_bracketing.py:676-687) requires "
        "max(member values) to quantize to preflight_level_screen_s and "
        "range to equal bracket_screen_s, so the level screen cannot be "
        "rewritten without rewriting all 17 member values and both t-quantile "
        "predictions. Candidate cures, both outside this seat's WRITE_SCOPE: "
        "(a) a generated synthetic ISSUED acceptance fixture from seat S4's "
        "issuer, with a small corpus whose statistics are internally "
        "consistent; (b) a fixture-sampler knob that widens the trace "
        "interval without widening wall time. A test-only --acceptance-path "
        "override is REJECTED: it would let a caller pick an artifact of a "
        "different epoch and so bypass DERIVATION_ONLY_EPOCH_UNCHANGED."
    )
    def test_a_bound_above_the_prior_level_screen_is_recorded_but_still_valid(
        self,
    ) -> None:
        """Kills the DIAGNOSTIC-only reading of `exceeds_prior_level_screen`.

        V2: `systematic-invalid` means "exceeds the level screen of THIS
        epoch's acceptance", and none exists for 25G83.  The counterfactual is
        an acceptance whose corpus maximum -- and therefore whose level screen
        -- is below any real capture's bound.  Route the comparison back into
        the disposition and this row becomes `systematic-invalid`.
        """

        acceptance = self._rekey_acceptance(maximum_s="0.000000000000001")
        epoch, t1 = self._epoch("25G83")
        declared = derivation_session_slots(2)
        ledger, pin, session_id, custody = self._session(
            "derivation-exceeds",
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
        self.assertIs(evidence["exceeds_prior_level_screen"], True)
        self.assertIs(manifest["exceeds_prior_level_screen"], True)
        self.assertGreater(
            Decimal(str(evidence["b_fiducial_s"])),
            Decimal(
                acceptance["decimal_derivation"]["ratified_operatives"][
                    "preflight_level_screen_s"
                ]
            ),
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


if __name__ == "__main__":
    unittest.main()
