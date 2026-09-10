"""Defect-shaped regressions for the derivation-night wrapper emitter.

Every test below names the defect it would catch.  The wrapper is the only
thing standing between a frozen v2 plan and a chain that needs thirteen
variables and twenty-four arguments the driver does not supply
(``scripts/run_night.py:430-444``), so a silent defect here is a burned night.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "gen_derivation_night.py"
CHAIN_RELPATH = "scripts/night_chains/calibration_derivation_only.zsh"
CHAIN_PATH = REPO_ROOT / CHAIN_RELPATH

# A night must never be exercised on a real epoch that is close to a real
# dead-man; 2026-09-12 02:56:00 PDT is the runbook's worked arithmetic example.
T0_EPOCH_S = 1789206960.0
WINDOW_MAX_S = 9000

# The six joulewise.calibration_ledger.IDENTITY_EPOCH_FIELDS, with the policy
# the chain captures under; `sampling_interval_ms` is an integer in every issued
# acceptance, so the fixture keeps it one.
IDENTITY_EPOCH = {
    "os_build": "25G83",
    "hardware_model": "Mac16,6",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "estimator_revision": "r6",
    "pulse_protocol_id": "p2",
}

FAKE_PYTHON = (
    "#!" + sys.executable + "\n"
    "import json, pathlib, sys\n"
    "calls = pathlib.Path(__file__).with_name('calls.jsonl')\n"
    "with calls.open('a') as stream:\n"
    "    stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
    "# Stop the chain immediately after the reservation, before its 600 s\n"
    "# settle, so this test never sleeps and never captures.\n"
    # argv[0] is this interpreter; argv[1] is the script the chain asked for.
    "sys.exit(3 if 'reserve_calibration_window_bracket.py' in sys.argv[1] else 0)\n"
)


def _load_generator():
    spec = importlib.util.spec_from_file_location("gen_derivation_night_test", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registering before exec keeps dataclass field resolution working.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


def _census_clean_temporary_directory() -> tempfile.TemporaryDirectory:
    """A temp directory whose whole path is free of `codex`, `claude`, `t3`.

    mkdtemp's random component hits one of those substrings every few hundred
    runs (`tmp4ew_t3eu` is a real example), and the generator then refuses to
    emit — correctly, since the night's own agent census would match the path.
    Retrying keeps that correct refusal from reading as a flaky test.
    """

    for _attempt in range(64):
        directory = tempfile.TemporaryDirectory()
        resolved = str(Path(directory.name).resolve()).lower()
        if not any(bad in resolved for bad in GEN.CENSUS_SUBSTRINGS):
            return directory
        directory.cleanup()
    raise AssertionError("no census-clean temporary directory available")


def _git(directory: Path, *arguments: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(directory), *arguments),
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"},
    )
    return result.stdout.strip()


class WrapperFixture:
    """A night root plus a real one-commit measurement clone of the chain."""

    def __init__(self, directory: Path, *, session_id: str = "derivation-20260912-epoch"):
        self.root = directory
        self.night_root = directory / "night-custody" / "derivation-20260912"
        self.night_root.mkdir(parents=True)
        self.measurement_root = directory / "measurement"
        (self.measurement_root / "scripts/night_chains").mkdir(parents=True)
        shutil.copy(CHAIN_PATH, self.measurement_root / CHAIN_RELPATH)
        (self.measurement_root / CHAIN_RELPATH).chmod(0o755)
        venv = self.measurement_root / ".venv/bin"
        venv.mkdir(parents=True)
        self.fake_python = venv / "python"
        self.fake_python.write_text(FAKE_PYTHON)
        self.fake_python.chmod(0o755)
        self.calls_path = venv / "calls.jsonl"
        _git(self.measurement_root, "init", "-q")
        _git(self.measurement_root, "add", "-A")
        _git(
            self.measurement_root,
            "-c", "user.email=seat@example.invalid", "-c", "user.name=seat",
            "commit", "-q", "-m", "fixture",
        )
        self.head = _git(self.measurement_root, "rev-parse", "HEAD")
        # The chain preflights these before spending any window time.
        for relative in (
            "runs/calibration_observation_ledger.jsonl",
            "configs/calibration/calibration_ledger_head.json",
        ):
            target = self.measurement_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n")
        self.frozen_plan = self.night_root / "calibration_plan.json"
        self.frozen_plan.write_text(json.dumps({"plan_id": "cal-derivation-20260912"}) + "\n")
        # A real-shaped identity epoch: the generator parses it now, not only
        # hashes it, and the six fields are the ledger's exact key set.
        (self.night_root / "identity_epoch.json").write_text(
            json.dumps(IDENTITY_EPOCH, indent=2, sort_keys=True) + "\n"
        )
        (self.night_root / "t1_bindings.json").write_text("{}\n")
        self.session_id = session_id
        self.out = self.night_root / "chain.zsh"
        self.plan_path = self.night_root / "night_plan.json"
        self.write_plan()

    def plan_mapping(self, **overrides) -> dict:
        mapping = {
            "schema": "joulewise.night_plan.v2",
            "schema_version": 2,
            "plan_id": "derivation-20260912",
            "receipt_class": "DIAGNOSTIC_NO_PACK",
            "t0_epoch_s": T0_EPOCH_S,
            "window_max_s": WINDOW_MAX_S,
            "authored_epoch_s": T0_EPOCH_S - 3600,
            "repo_head": "a" * 40,
            "measurement_root": str(self.measurement_root),
            "measurement_head": self.head,
            "chain_path": str(self.out),
            "chain_sha256_path": str(self.out) + ".sha256",
            "custody_root": str(self.night_root),
            "registration_path": (
                "configs/campaigns/d117_contrast_v5/"
                "d166_dominance_criterion_registration.json"
            ),
        }
        mapping.update(overrides)
        return mapping

    def write_plan(self, **overrides) -> None:
        self.plan_path.write_text(json.dumps(self.plan_mapping(**overrides), indent=2) + "\n")

    def clone_chain(self) -> Path:
        return self.measurement_root / CHAIN_RELPATH

    def emit(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable, "-B", str(SCRIPT_PATH),
                "--plan", str(self.plan_path),
                "--session-id", self.session_id,
                "--evidence-root-id", "EVR-derivation-20260912",
                "--calibration-plan", str(self.frozen_plan),
                "--identity-epoch-json", str(self.night_root / "identity_epoch.json"),
                "--t1-bindings-json", str(self.night_root / "t1_bindings.json"),
                *extra,
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def run_wrapper(self, **overrides: str | None) -> subprocess.CompletedProcess:
        """Launch exactly as ``run_night._run_chain_once`` would."""

        env = {
            "PATH": "/usr/bin:/bin",
            "NIGHT_PLAN_ID": "derivation-20260912",
            "MEASUREMENT_ROOT": str(self.measurement_root),
            "MEASUREMENT_HEAD": self.head,
            "PY": f"{self.measurement_root}/.venv/bin/python",
        }
        for key, value in overrides.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return subprocess.run(
            ["/bin/zsh", str(self.out)],
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def calls(self) -> list[list[str]]:
        if not self.calls_path.exists():
            return []
        return [json.loads(line) for line in self.calls_path.read_text().splitlines()]


def _exports(wrapper: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(r"^export ([A-Z0-9_]+)='([^']*)'$", wrapper, re.MULTILINE)
    }


def _exec_arguments(wrapper: str) -> list[str]:
    exec_line = wrapper[wrapper.index("\nexec /bin/zsh ") + 1 :]
    return shlex.split(exec_line.replace("\\\n", " "))


@unittest.skipUnless(shutil.which("git") and Path("/usr/bin/jq").exists(), "git and jq required")
class DerivationNightWrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = _census_clean_temporary_directory()
        self.addCleanup(self.directory.cleanup)
        self.fixture = WrapperFixture(Path(self.directory.name))

    # --- emission ---------------------------------------------------------

    def test_two_emissions_of_one_plan_are_byte_identical(self) -> None:
        """Arm-time re-derivation asserts byte equality (record 04 :672-694).

        A wrapper carrying a timestamp, a temporary path, or set iteration
        order would make that assertion fail at 03:00 with no way to tell drift
        from nondeterminism.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        first = self.fixture.out.read_bytes()
        first_sidecar = (self.fixture.out.with_suffix(".zsh.sha256")).read_bytes()
        self.assertEqual(self.fixture.emit().returncode, 0)
        self.assertEqual(self.fixture.out.read_bytes(), first)
        self.assertEqual((self.fixture.out.with_suffix(".zsh.sha256")).read_bytes(), first_sidecar)

    def test_every_required_chain_variable_is_exported_with_its_plan_value(self) -> None:
        """All thirteen `:?required` guards of the chain (:43-55) must be fed.

        Dropping any one export exits the chain 1 on its first guard: safe, but
        the whole night is spent.  The values are the plan's, not defaults.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        exports = _exports(self.fixture.out.read_text())
        required = re.findall(r'^: "\$\{([A-Z0-9_]+):\?required\}"$', CHAIN_PATH.read_text(), re.M)
        self.assertEqual(len(required), 13)
        self.assertEqual(sorted(set(required) - set(exports)), [])
        night = self.fixture.night_root
        measurement = self.fixture.measurement_root
        self.assertEqual(
            {name: exports[name] for name in required},
            {
                "SESSION_ID": self.fixture.session_id,
                "WINDOW_ID": "derivation-20260912",
                "PLAN_ID": "cal-derivation-20260912",
                "PLAN_SHA256": hashlib.sha256(
                    self.fixture.frozen_plan.read_bytes()
                ).hexdigest(),
                "PLAN": str(self.fixture.frozen_plan),
                "EVIDENCE_ROOT_ID": "EVR-derivation-20260912",
                "RUNS_ROOT": f"{night}/runs",
                "WINDOW_CUSTODY_ROOT": str(night),
                "CALIBRATION_LEDGER": f"{measurement}/runs/calibration_observation_ledger.jsonl",
                "LEDGER_HEAD_PIN": (
                    f"{measurement}/configs/calibration/calibration_ledger_head.json"
                ),
                "IDENTITY_EPOCH_JSON": f"{night}/identity_epoch.json",
                "T1_BINDINGS_JSON": f"{night}/t1_bindings.json",
                "WINDOW_END_EPOCH_S": str(int(T0_EPOCH_S + WINDOW_MAX_S)),
            },
        )

    def test_window_end_is_the_integer_sum_of_t0_and_window_max(self) -> None:
        """`WINDOW_END_EPOCH_S = int(t0 + window_max_s)` — an absolute epoch.

        A relative value, a float, or the courier/dead-man epoch instead would
        either be refused by the chain's `<->` guard (:69-75, exit 64) or run
        the night past its agent-free end.
        """

        # 8000 s is the shortest round window that still holds the programmed
        # span; the fractional t0 is what the integer cast has to survive.
        self.fixture.write_plan(t0_epoch_s=T0_EPOCH_S + 0.75, window_max_s=8000)
        self.assertEqual(self.fixture.emit().returncode, 0)
        exports = _exports(self.fixture.out.read_text())
        self.assertEqual(exports["WINDOW_END_EPOCH_S"], str(int(T0_EPOCH_S + 0.75 + 8000)))
        self.assertRegex(exports["WINDOW_END_EPOCH_S"], r"^[0-9]+$")

    def test_the_sidecar_is_the_strict_form_the_driver_accepts(self) -> None:
        """`run_night._sidecar_digest` (:97-105) refuses any other form.

        A `sha256sum --tag` or bare-digest sidecar refuses the night with
        chain_digest_mismatch after the plan is already frozen.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        sidecar = Path(str(self.fixture.out) + ".sha256").read_text()
        driver = _load_driver()
        self.assertEqual(
            driver._sidecar_digest(sidecar, self.fixture.out.name),
            hashlib.sha256(self.fixture.out.read_bytes()).hexdigest(),
        )

    def test_twenty_four_binding_flags_satisfy_the_real_reservation_parser(self) -> None:
        """The reservation refuses `declared_slot_flag_count_mismatch` (:167-186).

        This is the defect that cannot be caught by the chain's own tests: they
        drive it with empty argv.  Removing the bindings from the wrapper must
        make the production parser refuse, not default.
        """

        from scripts.reserve_calibration_window_bracket import (  # noqa: PLC0415
            _declared_slot_sources, _parser,
        )
        from joulewise.calibration_ledger import CalibrationLedgerError  # noqa: PLC0415

        self.assertEqual(self.fixture.emit().returncode, 0)
        arguments = _exec_arguments(self.fixture.out.read_text())
        bindings = arguments[3:]
        # Twenty-four repeated flags — twelve of each — i.e. 48 argv tokens.
        self.assertEqual(bindings.count("--slot-attempt-id"), 12)
        self.assertEqual(bindings.count("--slot-custody-locator"), 12)
        self.assertEqual(len(bindings), 48)
        common = [
            "--session-id", "s", "--window-id", "w", "--plan-id", "p",
            "--plan-sha256", "a" * 64, "--evidence-root-id", "e",
            "--runs-root", "/tmp/runs", "--identity-epoch-json", "/tmp/e.json",
            "--t1-bindings-json", "/tmp/t.json",
            "--session-kind", "derivation", "--slot-count", "12",
        ]
        declared, pairs = _declared_slot_sources(_parser().parse_args(common + bindings))
        self.assertEqual(len(declared), 12)
        self.assertEqual(
            pairs[0],
            (
                f"{self.fixture.session_id}-d01",
                f"{self.fixture.night_root}/runs/instrument_validation/"
                f"{self.fixture.session_id}-d01",
            ),
        )
        with self.assertRaises(CalibrationLedgerError) as caught:
            _declared_slot_sources(_parser().parse_args(common))
        self.assertEqual(caught.exception.context["reason"], "declared_slot_flag_count_mismatch")

    # --- refusals ---------------------------------------------------------

    def test_a_plan_missing_a_field_refuses_instead_of_emitting(self) -> None:
        """An inexact v2 plan is exactly what `NightPlan.from_mapping` refuses.

        Emitting from a partial plan would bake `None` into a literal export.
        """

        mapping = self.fixture.plan_mapping()
        del mapping["window_max_s"]
        self.fixture.plan_path.write_text(json.dumps(mapping))
        result = self.fixture.emit()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("not an exact v2 plan", result.stderr)
        self.assertFalse(self.fixture.out.exists())

    def test_a_plan_that_overruns_the_dead_man_refuses(self) -> None:
        """`t0 + window_max_s + 300` must be before the next local 07:00.

        The gate refuses such a plan at launch (run_night.py:1463-1474); the
        arm must learn it at the desk, not at 03:00 with the night burned.
        """

        deadman = GEN._next_deadman_epoch(T0_EPOCH_S)
        exact = int(deadman - T0_EPOCH_S - GEN.COURIER_DEADLINE_S)
        self.fixture.write_plan(window_max_s=exact)
        result = self.fixture.emit()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("overruns the dead-man", result.stderr)
        self.assertFalse(self.fixture.out.exists())
        # One second less is admissible: the comparison is strict, not fuzzy.
        self.fixture.write_plan(window_max_s=exact - 1)
        self.assertEqual(self.fixture.emit().returncode, 0)

    def test_a_census_substring_anywhere_in_the_night_refuses(self) -> None:
        """`pgrep -lf "codex|claude|t3"` aborts the night on its own argv.

        The census probe (joulewise/night_gate.py:42, :498-525) matches full
        command lines, so a session id or night root carrying one of those
        substrings would make the night kill itself mid-capture.
        """

        for field, session_id, plan_id in (
            ("session id", "derivation-20260912-claude", "derivation-20260912"),
            ("night custody root", "derivation-20260912-epoch", "derivation-20260912"),
        ):
            with self.subTest(field=field):
                fixture = self.fixture
                if field == "night custody root":
                    poisoned = fixture.night_root.parent / "t3-night"
                    poisoned.mkdir()
                    fixture.write_plan(custody_root=str(poisoned))
                else:
                    fixture.session_id = session_id
                result = fixture.emit()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("census substring", result.stderr)
                self.assertFalse(fixture.out.exists())
        self.fixture.session_id = "derivation-20260912-epoch"

    def test_a_slot_count_other_than_the_pre_registered_twelve_refuses(self) -> None:
        """Twelve slots are pre-registered (cold-gate ruling 46 §R-c).

        Silently emitting eleven bindings would reduce a pre-registered night.
        """

        result = self.fixture.emit("--slot-count", "8")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("not the pre-registered", result.stderr)
        self.assertEqual(
            self.fixture.emit(
                "--slot-count", "8", "--allow-slot-count",
                "--slot-count-ruling", "cold-gate-46-addendum-9",
            ).returncode,
            0,
        )
        self.assertEqual(len(_exec_arguments(self.fixture.out.read_text())[3:]), 32)

    def test_an_out_path_that_is_not_the_plans_chain_path_refuses(self) -> None:
        """The plan pins the wrapper by path AND digest; both must be this file."""

        result = self.fixture.emit("--out", str(self.fixture.night_root / "other.zsh"))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("chain_path", result.stderr)

    # --- the emitted wrapper, run the way the driver runs it --------------

    def test_the_wrapper_reaches_the_reservation_with_all_bindings(self) -> None:
        """End-to-end: four driver variables in, twenty-four bindings out.

        This is the test that fails if any single link is wrong — routing
        preamble, exports, plan re-derivation, chain digest, or `exec`.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        result = self.fixture.run_wrapper()
        calls = self.fixture.calls()
        self.assertEqual(len(calls), 2, result.stderr)
        readiness, reservation = calls
        self.assertIn("recover_calibration_ledger.py", readiness[0])
        self.assertIn("readiness", readiness)
        self.assertEqual(readiness[readiness.index("--phase") + 1], "pre-reserve")
        self.assertEqual(readiness[readiness.index("--session-id") + 1], self.fixture.session_id)
        self.assertIn("reserve_calibration_window_bracket.py", reservation[0])
        self.assertEqual(reservation[reservation.index("--slot-count") + 1], "12")
        self.assertEqual(reservation.count("--slot-attempt-id"), 12)
        self.assertEqual(reservation.count("--slot-custody-locator"), 12)
        self.assertEqual(reservation[-1], "--execute")
        # The fake interpreter stops the chain at the reservation, before the
        # 600 s settle: this test never sleeps and never captures.
        self.assertEqual(result.returncode, 3, result.stderr)

    def test_the_wrapper_refuses_when_the_tracked_chain_bytes_change(self) -> None:
        """The plan pins the wrapper, so only this check covers the chain.

        Without it, an edited (or reverted, or dirty-tree) capturing chain runs
        unattended with the plan's attestation still nominally satisfied.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        chain = self.fixture.measurement_root / CHAIN_RELPATH
        chain.write_text(chain.read_text() + "\n# an edit no reviewer saw\n")
        result = self.fixture.run_wrapper()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("tracked derivation chain bytes do not match", result.stderr)
        self.assertEqual(self.fixture.calls(), [])

    def test_the_wrapper_refuses_a_swapped_frozen_plan(self) -> None:
        """PLAN_SHA256 is a literal; the wrapper re-derives it from the file."""

        self.assertEqual(self.fixture.emit().returncode, 0)
        self.fixture.frozen_plan.write_text(
            json.dumps({"plan_id": "cal-derivation-20260912", "swapped": True}) + "\n"
        )
        result = self.fixture.run_wrapper()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("frozen plan bytes do not equal", result.stderr)
        self.assertEqual(self.fixture.calls(), [])

    def test_the_wrapper_refuses_a_different_plans_coordinates(self) -> None:
        """A wrapper pinned by one plan must never run under another."""

        self.assertEqual(self.fixture.emit().returncode, 0)
        result = subprocess.run(
            ["/bin/zsh", str(self.fixture.out)],
            env={
                "PATH": "/usr/bin:/bin",
                "NIGHT_PLAN_ID": "some-other-night",
                "MEASUREMENT_ROOT": str(self.fixture.measurement_root),
                "MEASUREMENT_HEAD": self.fixture.head,
                "PY": f"{self.fixture.measurement_root}/.venv/bin/python",
            },
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("night plan id does not match", result.stderr)

    def test_the_emitted_wrapper_parses_as_zsh(self) -> None:
        self.assertEqual(self.fixture.emit().returncode, 0)
        parsed = subprocess.run(
            ["/bin/zsh", "-n", str(self.fixture.out)], capture_output=True, text=True
        )
        self.assertEqual(parsed.returncode, 0, parsed.stderr)
        self.assertTrue(os.access(self.fixture.out, os.X_OK))

    # --- fix round 1 ------------------------------------------------------

    def test_the_chain_digest_is_a_literal_in_the_wrapper_bytes(self) -> None:
        """B-1/F1: the plan pins the wrapper, so the chain digest must be IN it.

        With the digest held in a separate sidecar file, editing the chain and
        rewriting that file left the wrapper byte-identical: the plan-pinned
        digest did not move, and the arm's re-emit-and-compare step was blind to
        a changed capturing chain (refuter 104 F1(a), reproduced).
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        first = self.fixture.out.read_text()
        chain = self.fixture.clone_chain()
        self.assertIn(hashlib.sha256(chain.read_bytes()).hexdigest(), first)
        # Change the chain, re-emit: the wrapper's own bytes must move.
        chain.write_text(chain.read_text() + "\n# an edit no reviewer saw\n")
        self.assertEqual(self.fixture.emit().returncode, 0)
        second = self.fixture.out.read_text()
        self.assertNotEqual(first, second)
        self.assertIn(hashlib.sha256(chain.read_bytes()).hexdigest(), second)

    def test_rewriting_the_advisory_sidecar_cannot_move_the_pin(self) -> None:
        """The refuter's exact attack: edit the chain, rewrite the sidecar, launch.

        Nothing the night reads may live outside the plan-pinned bytes.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        chain = self.fixture.clone_chain()
        chain.write_text(chain.read_text() + "\n# injected\n")
        sidecar = Path(str(self.fixture.out) + ".chain-source.sha256")
        sidecar.write_text(
            f"{hashlib.sha256(chain.read_bytes()).hexdigest()}  {CHAIN_RELPATH}\n"
        )
        result = self.fixture.run_wrapper()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("tracked derivation chain bytes do not match", result.stderr)
        self.assertEqual(self.fixture.calls(), [])
        # Deleting the advisory file entirely changes nothing: it is not trusted.
        sidecar.unlink()
        chain.write_text(chain.read_text().replace("\n# injected\n", ""))
        self.assertEqual(self.fixture.run_wrapper().returncode, 3)

    def test_the_chain_is_digested_from_the_measurement_clone(self) -> None:
        """F3: the generator's own checkout is not the checkout the night runs.

        Digesting the generator's copy bakes in bytes the night will never
        execute — the wrapper then refuses at t0 with the night burned.
        """

        chain = self.fixture.clone_chain()
        chain.write_text(chain.read_text() + "\n# only in the clone\n")
        self.assertEqual(self.fixture.emit().returncode, 0)
        wrapper = self.fixture.out.read_text()
        self.assertIn(hashlib.sha256(chain.read_bytes()).hexdigest(), wrapper)
        self.assertNotIn(hashlib.sha256(CHAIN_PATH.read_bytes()).hexdigest(), wrapper)
        # And the wrapper it emitted runs against that clone.
        self.assertEqual(self.fixture.run_wrapper().returncode, 3)

    def test_a_window_too_short_for_the_programmed_span_refuses(self) -> None:
        """B-2: settle + (N-1) x cadence + budget must fit, or the night aborts.

        A 3600 s window emitted a 12-slot night that would settle, run about
        five slots and hit window_exhausted — one of the campaign's three
        nights, partial (refuter 105 B-2, reproduced).
        """

        self.fixture.write_plan(window_max_s=3600)
        result = self.fixture.emit()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("window_max_s 3600 < required 7680 + 300 = 7980", result.stderr)
        self.assertFalse(self.fixture.out.exists())
        # The exact boundary, both sides.
        self.fixture.write_plan(window_max_s=7979)
        self.assertEqual(self.fixture.emit().returncode, 2)
        self.fixture.write_plan(window_max_s=7980)
        self.assertEqual(self.fixture.emit().returncode, 0)

    def test_the_span_constants_are_the_chains_own_defaults(self) -> None:
        """The refusal is only true if these numbers are the chain's numbers."""

        chain = CHAIN_PATH.read_text()
        for anchor, value in (
            ("settle_default", GEN.DEFAULT_SETTLE_S),
            ("cadence_default", GEN.DEFAULT_SLOT_CADENCE_S),
            ("budget_default", GEN.DEFAULT_SLOT_CAPTURE_BUDGET_S),
            ("slot_count_default", GEN.PRE_REGISTERED_SLOT_COUNT),
        ):
            with self.subTest(anchor=anchor):
                line = GEN.CHAIN_ANCHORS[anchor]
                self.assertIn(line, chain)
                self.assertIn(f":-{value}}}", line)
        self.assertEqual(GEN.programmed_span_s(12), 7680)

    def test_every_chain_citation_resolves_to_a_real_chain_line(self) -> None:
        """S-2: line-number citations rotted the moment the header was edited.

        Anchor texts cannot silently point at the wrong line; if one is edited
        away, this fails instead of shipping a false citation into a night.
        """

        lines = CHAIN_PATH.read_text().splitlines()
        for name, anchor in GEN.CHAIN_ANCHORS.items():
            with self.subTest(anchor=name):
                self.assertEqual(lines.count(anchor), 1, anchor)
        source = SCRIPT_PATH.read_text()
        self.assertNotIn("calibration_derivation_only.zsh:", source)
        # The two anchors quoted into every night's artifact really are quoted.
        self.assertEqual(self.fixture.emit().returncode, 0)
        wrapper = self.fixture.out.read_text()
        self.assertIn(GEN.CHAIN_ANCHORS["repo_from_argv0"], wrapper)
        self.assertIn(GEN.CHAIN_ANCHORS["forward_argv"].strip(), wrapper)

    def test_every_in_wrapper_refusal_prints_a_reason(self) -> None:
        """F4: three refusals exited 1 with an empty stderr.

        The driver redirects the chain's stderr to a file; an empty stream is
        the whole forensic record of why an unattended night refused.
        """

        for path, reason in (
            (self.fixture.frozen_plan, "frozen calibration plan is missing"),
            (self.fixture.night_root / "identity_epoch.json", "identity epoch json is missing"),
            (self.fixture.night_root / "t1_bindings.json", "t1 bindings json is missing"),
        ):
            with self.subTest(reason=reason):
                self.assertEqual(self.fixture.emit().returncode, 0)
                saved = path.read_bytes()
                path.unlink()
                result = self.fixture.run_wrapper()
                path.write_bytes(saved)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(result.stderr.strip(), f"FAIL {reason}")
                self.assertEqual(self.fixture.calls(), [])

    def test_modified_identity_or_t1_bytes_refuse(self) -> None:
        """S-1: their contents are copied verbatim into every slot record.

        (reserve_calibration_window_bracket.py reads both and writes their
        payloads into the declared slots, so a swapped file silently changes
        what every capture is bound to.)
        """

        for name, reason in (
            ("identity_epoch.json", "identity epoch bytes do not equal"),
            ("t1_bindings.json", "t1 bindings bytes do not equal"),
        ):
            with self.subTest(name=name):
                self.assertEqual(self.fixture.emit().returncode, 0)
                path = self.fixture.night_root / name
                saved = path.read_bytes()
                path.write_bytes(saved + b'{"swapped": true}\n')
                result = self.fixture.run_wrapper()
                path.write_bytes(saved)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn(reason, result.stderr)
                self.assertEqual(self.fixture.calls(), [])

    def test_a_non_diagnostic_receipt_class_refuses(self) -> None:
        """F5: the old pack-only guard was unreachable behind the schema check.

        It is now an allow-list on receipt_class, which a REHEARSAL_STUB plan
        reaches: such a night never runs its chain at all, so emitting a
        wrapper for it is silently pointless.
        """

        self.fixture.write_plan(receipt_class="REHEARSAL_STUB")
        result = self.fixture.emit()
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(
            "a derivation night is DIAGNOSTIC_NO_PACK; this plan is REHEARSAL_STUB",
            result.stderr,
        )
        self.assertFalse(self.fixture.out.exists())

    def test_departing_from_twelve_slots_requires_a_named_ruling(self) -> None:
        """F6: an unrecorded escape hatch off the pre-registration.

        The departure must be impossible to make quietly: a ruling reference is
        required, announced on stderr, and written into the wrapper's header.
        """

        refused = self.fixture.emit("--slot-count", "6", "--allow-slot-count")
        self.assertEqual(refused.returncode, 2, refused.stderr)
        self.assertIn("--slot-count-ruling", refused.stderr)
        self.assertFalse(self.fixture.out.exists())
        allowed = self.fixture.emit(
            "--slot-count", "6", "--allow-slot-count",
            "--slot-count-ruling", "cold-gate-46-addendum-9",
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertIn("DEPARTURE this night declares 6 slots", allowed.stderr)
        header = self.fixture.out.read_text().split("set -euo pipefail")[0]
        self.assertIn("DEPARTURE FROM THE PRE-REGISTRATION", header)
        self.assertIn("cold-gate-46-addendum-9", header)

    # --- fix round 2 ------------------------------------------------------

    def test_verify_mode_compares_the_installed_wrapper_without_writing(self) -> None:
        """D-1: arm step 4 has to be executable, and it is the tripwire step.

        The generator refuses any --out but the plan's chain_path, so "emit a
        second copy to a scratch path" could not be run at all; --verify
        re-derives in memory and compares.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        installed = self.fixture.out.read_bytes()
        good = self.fixture.emit("--verify")
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("VERIFIED", good.stdout)
        self.assertIn(hashlib.sha256(installed).hexdigest(), good.stdout)
        # It wrote nothing: the installed bytes and mtime are untouched.
        self.assertEqual(self.fixture.out.read_bytes(), installed)
        # An input drifted: the chain the night would run was edited.
        chain = self.fixture.clone_chain()
        chain.write_text(chain.read_text() + "\n# drift\n")
        drifted = self.fixture.emit("--verify")
        self.assertEqual(drifted.returncode, 3, drifted.stdout)
        self.assertIn("FAIL wrapper bytes differ from re-derivation", drifted.stderr)
        self.assertIn(hashlib.sha256(installed).hexdigest(), drifted.stderr)
        self.assertEqual(self.fixture.out.read_bytes(), installed)
        # Isolate the byte comparison: make the sidecar agree with the
        # RE-DERIVED digest, so only comparing the wrapper's own bytes can
        # still catch the drift.
        rederived = re.search(r"re-derived sha256=([0-9a-f]{64})", drifted.stderr)
        assert rederived is not None, drifted.stderr
        Path(str(self.fixture.out) + ".sha256").write_text(
            f"{rederived.group(1)}  {self.fixture.out.name}\n"
        )
        still = self.fixture.emit("--verify")
        self.assertEqual(still.returncode, 3, still.stdout)
        self.assertIn("FAIL wrapper bytes differ from re-derivation", still.stderr)

    def test_verify_mode_catches_a_tampered_sidecar(self) -> None:
        """The sidecar is what the driver checks the wrapper against."""

        self.assertEqual(self.fixture.emit().returncode, 0)
        sidecar = Path(str(self.fixture.out) + ".sha256")
        sidecar.write_text(f"{'0' * 64}  chain.zsh\n")
        result = self.fixture.emit("--verify")
        self.assertEqual(result.returncode, 3, result.stdout)
        self.assertIn("FAIL wrapper bytes differ from re-derivation", result.stderr)

    def test_a_frozen_plan_without_a_plan_id_refuses_with_a_reason(self) -> None:
        """D-2: the last unguarded refusal — rc 1 with an EMPTY stderr.

        Under `set -e` an unguarded command substitution kills the wrapper with
        no message, which is indistinguishable from a crash in the driver's log.
        """

        for payload, reason in (
            (b'{ not json\n', "frozen plan is not valid JSON"),
            (b'{"other": 1}\n', "frozen plan has no plan_id"),
        ):
            with self.subTest(reason=reason):
                self.assertEqual(self.fixture.emit().returncode, 0)
                self.fixture.frozen_plan.write_bytes(payload)
                result = self.fixture.run_wrapper()
                self.fixture.frozen_plan.write_text(
                    json.dumps({"plan_id": "cal-derivation-20260912"}) + "\n"
                )
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(result.stderr.strip(), f"FAIL {reason}")
                self.assertEqual(self.fixture.calls(), [])

    def test_a_ruling_reference_that_could_inject_code_refuses(self) -> None:
        """D-3: the ruling is interpolated into the header ABOVE all wrapper code.

        A newline ends the comment and starts a live line, and `zsh -n` — the
        documented arm check — accepts the result; a pasted multi-line reference
        does it by accident.
        """

        for ruling in (
            "ok\nexport SLOT_COUNT=99\n# rest",
            "ruling-$(touch /tmp/should-not-exist)",
            "ruling'; export SLOT_COUNT=99; '",
            "",
        ):
            with self.subTest(ruling=ruling):
                result = self.fixture.emit(
                    "--slot-count", "6", "--allow-slot-count",
                    "--slot-count-ruling", ruling,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("ruling", result.stderr)
                self.assertFalse(self.fixture.out.exists())

    def test_every_routing_refusal_names_its_reason(self) -> None:
        """Nit (a): ten refusal paths had no test asserting their reason.

        Each is a precondition an unattended night can actually hit, and the
        stderr line is the whole forensic record.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        clone = self.fixture.measurement_root
        cases = (
            ("measurement_root is required", {"MEASUREMENT_ROOT": None}, None),
            ("measurement_root must be an absolute path", {"MEASUREMENT_ROOT": "relative/path"}, None),
            ("measurement_root contains control characters", {"MEASUREMENT_ROOT": "/tmp/a\nb"}, None),
            ("measurement_head must be a full 40-character lowercase SHA-1", {"MEASUREMENT_HEAD": "abc"}, None),
            ("night plan id does not match the wrapper", {"NIGHT_PLAN_ID": "another-night"}, None),
            ("measurement_root does not match the wrapper", {"MEASUREMENT_ROOT": "/tmp"}, None),
            ("measurement_head does not match the wrapper", {"MEASUREMENT_HEAD": "b" * 40}, None),
            ("checkout HEAD cannot be read", {}, "unrepo"),
            ("checkout HEAD does not equal measurement_head", {}, "recommit"),
            ("measurement venv Python is missing or not executable", {}, "unvenv"),
            ("frozen plan id does not equal the arm-time literal", {}, "swap_plan_id"),
        )
        for reason, overrides, mutation in cases:
            with self.subTest(reason=reason):
                restore = None
                if mutation == "unrepo":
                    (clone / ".git").rename(clone / "git-aside")
                    restore = lambda: (clone / "git-aside").rename(clone / ".git")
                elif mutation == "recommit":
                    (clone / "later.txt").write_text("x\n")
                    _git(clone, "add", "-A")
                    _git(clone, "-c", "user.email=s@e.invalid", "-c", "user.name=s",
                         "commit", "-q", "-m", "later")
                    restore = lambda: _git(clone, "reset", "-q", "--hard", self.fixture.head)
                elif mutation == "unvenv":
                    self.fixture.fake_python.chmod(0o644)
                    restore = lambda: self.fixture.fake_python.chmod(0o755)
                elif mutation == "swap_plan_id":
                    self.fixture.frozen_plan.write_text(json.dumps({"plan_id": "other"}) + "\n")
                    restore = lambda: self.fixture.frozen_plan.write_text(
                        json.dumps({"plan_id": "cal-derivation-20260912"}) + "\n"
                    )
                try:
                    result = self.fixture.run_wrapper(**overrides)
                finally:
                    if restore is not None:
                        restore()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(result.stderr.strip(), f"FAIL {reason}")
                self.assertEqual(self.fixture.calls(), [])

    def test_the_wrapper_calls_every_external_command_by_absolute_path(self) -> None:
        """Nit (c): the driver hands the chain os.environ.copy(), PATH included."""

        self.assertEqual(self.fixture.emit().returncode, 0)
        code = "\n".join(
            line for line in self.fixture.out.read_text().splitlines()
            if not line.lstrip().startswith("#")
        )
        wrapper = self.fixture.out.read_text()
        for command in ("git", "jq", "shasum", "awk", "zsh"):
            with self.subTest(command=command):
                self.assertNotIn(f" {command} ", code)
        self.assertIn('/usr/bin/git -C "$MEASUREMENT_ROOT"', wrapper)

    # --- fix round 4 ------------------------------------------------------

    def test_a_slot_count_above_the_ledger_ceiling_refuses(self) -> None:
        """The ledger caps a declared-slot list, and refuses INSIDE the window.

        A 100-slot wrapper renders d100 bindings, settles for 600 s, and is then
        refused at the reservation with the night already spent.
        """

        from joulewise.calibration_ledger import (  # noqa: PLC0415
            MAX_DECLARED_SESSION_SLOTS,
        )

        over = MAX_DECLARED_SESSION_SLOTS + 1
        result = self.fixture.emit(
            "--slot-count", str(over), "--allow-slot-count",
            "--slot-count-ruling", "cold-gate-46-addendum-9",
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(
            f"slot count {over} exceeds the ledger's MAX_DECLARED_SESSION_SLOTS "
            f"({MAX_DECLARED_SESSION_SLOTS})",
            result.stderr,
        )
        self.assertFalse(self.fixture.out.exists())

    def test_the_identity_epoch_is_parsed_not_only_hashed(self) -> None:
        """Hashing pins WHICH file the night uses; parsing says it can do its job.

        Each rejected shape below would otherwise be discovered by the writer at
        d01, after the settle, with the window spent.
        """

        from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS  # noqa: PLC0415

        good = dict(IDENTITY_EPOCH)
        self.assertEqual(set(good), set(IDENTITY_EPOCH_FIELDS))
        epoch = self.fixture.night_root / "identity_epoch.json"
        epoch.write_text(json.dumps(good) + "\n")
        self.assertEqual(self.fixture.emit().returncode, 0)

        missing = {key: value for key, value in good.items() if key != "os_build"}
        extra = {**good, "surprise": "x"}
        empty = {**good, "estimator_revision": ""}
        wrong_policy = {**good, "power_policy": "ac_default"}
        for payload, fragment in (
            (b"{ not json\n", "not readable JSON"),
            (b'["a list"]\n', "must be a JSON object"),
            (json.dumps(missing).encode(), "not exactly the six"),
            (json.dumps(extra).encode(), "not exactly the six"),
            (json.dumps(empty).encode(), "empty or not scalar"),
            (json.dumps(wrong_policy).encode(), "--power-policy ac_high_power"),
        ):
            with self.subTest(fragment=fragment):
                epoch.write_bytes(payload)
                result = self.fixture.emit()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(fragment, result.stderr)
        epoch.write_text(json.dumps(good) + "\n")

    def test_the_t1_bindings_file_must_be_a_json_object(self) -> None:
        """Its contents are copied verbatim into every slot record."""

        bindings = self.fixture.night_root / "t1_bindings.json"
        for payload, fragment in (
            (b"not json at all\n", "not readable JSON"),
            (b"[1, 2, 3]\n", "must be a JSON object"),
        ):
            with self.subTest(fragment=fragment):
                bindings.write_bytes(payload)
                result = self.fixture.emit()
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("t1 bindings json", result.stderr)
                self.assertIn(fragment, result.stderr)
        bindings.write_text("{}\n")

    def test_the_binding_count_is_stated_in_words_that_match_the_argv(self) -> None:
        """"Twenty-four arguments" read as 24 argv words; there are 48.

        The wrapper's own header states both numbers, and they must equal what
        the exec line actually carries.
        """

        self.assertEqual(self.fixture.emit().returncode, 0)
        wrapper = self.fixture.out.read_text()
        arguments = _exec_arguments(wrapper)[3:]
        self.assertEqual(len(arguments), 48)
        self.assertIn("24 flag/value pairs, 48 argv words.", wrapper)
        self.assertNotIn("twenty-four per-slot binding arguments", wrapper)
        source = SCRIPT_PATH.read_text()
        self.assertNotIn("twenty-four per-slot binding arguments", source)


class GeneratedRegionTests(unittest.TestCase):
    def test_the_runsheet_region_matches_the_generator(self) -> None:
        """`--check` is the drift tripwire: editing the chain re-runs the emitter."""

        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT_PATH), "--check"],
            capture_output=True, text=True, cwd=REPO_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_region_carries_the_live_chain_digest(self) -> None:
        """A stale digest in the reviewed example is a stale wrapper recipe."""

        region = GEN.render_region(CHAIN_PATH.read_bytes())
        self.assertIn(hashlib.sha256(CHAIN_PATH.read_bytes()).hexdigest(), region)
        runsheet = GEN.RUNSHEET_PATH.read_text(encoding="utf-8")
        self.assertIn(region, runsheet)

    def test_the_region_documents_the_third_file_and_the_arm_order(self) -> None:
        """S-4: the emission has a custody side-effect and a required order.

        Without both, an operator cannot replicate the arm, and cannot tell
        whether the advisory sidecar in the night root is load-bearing.
        """

        region = GEN.render_region(CHAIN_PATH.read_bytes())
        for phrase in (
            "chain.zsh.chain-source.sha256",
            "ADVISORY ONLY",
            "### Arm order",
            "status --porcelain",
            "Re-derive and assert byte equality",
            "--verify",
            # The two 300 s budgets must be told apart before either is used.
            "The **pre-settle allowance** is the time the",
            "The **courier",
            "they are unrelated and",
            "digests the tracked chain **from the clone**",
            "```json",
            '"schema": "joulewise.night_plan.v2"',
            "24 per-slot binding flag/value pairs",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, region)

    def test_the_example_plan_is_one_the_driver_would_accept(self) -> None:
        """Arm-order step 2 has to be replicable, so its shape must be real.

        A plan whose key set is not exact is refused by the gate's own parser,
        and the example is the only shape the arm has to copy.
        """

        from joulewise.night_gate import NightPlan  # noqa: PLC0415

        spec = GEN.example_spec(CHAIN_PATH.read_bytes())
        plan = GEN.example_night_plan(spec)
        concrete = {
            **plan,
            "repo_head": "a" * 40,
            "measurement_head": "b" * 40,
            "registration_path": "configs/campaigns/example/registration.json",
        }
        parsed = NightPlan.from_mapping(concrete)
        self.assertEqual(parsed.receipt_class, "DIAGNOSTIC_NO_PACK")
        # chain_path is the WRAPPER, not the tracked chain, and the sidecar is
        # the one the generator writes beside it.
        self.assertEqual(parsed.chain_path, f"{spec.window_custody_root}/chain.zsh")
        self.assertEqual(parsed.chain_sha256_path, parsed.chain_path + ".sha256")
        self.assertEqual(parsed.custody_root, spec.window_custody_root)
        self.assertEqual(parsed.measurement_root, spec.measurement_root)
        # And the window it declares survives this generator's own fences.
        self.assertGreaterEqual(
            parsed.window_max_s,
            GEN.programmed_span_s(GEN.PRE_REGISTERED_SLOT_COUNT)
            + GEN.PRE_SETTLE_ALLOWANCE_S,
        )
        self.assertIn(json.dumps(plan, indent=2), GEN.render_region(CHAIN_PATH.read_bytes()))

    def test_the_g2a_emitter_still_passes_its_own_check(self) -> None:
        """The new region must not move the G2-a emitter's pinned fence lines."""

        result = subprocess.run(
            [sys.executable, "-B", str(REPO_ROOT / "scripts/gen_g2_phase_d.py"), "--check"],
            capture_output=True, text=True, cwd=REPO_ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def _load_driver():
    spec = importlib.util.spec_from_file_location(
        "run_night_for_sidecar_test", REPO_ROOT / "scripts/run_night.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Registering before exec keeps dataclass field resolution working.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
