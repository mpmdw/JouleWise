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
        (self.night_root / "identity_epoch.json").write_text("{}\n")
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

    def run_wrapper(self) -> subprocess.CompletedProcess:
        """Launch exactly as ``run_night._run_chain_once`` would."""

        return subprocess.run(
            ["/bin/zsh", str(self.out)],
            env={
                "PATH": "/usr/bin:/bin",
                "NIGHT_PLAN_ID": "derivation-20260912",
                "MEASUREMENT_ROOT": str(self.measurement_root),
                "MEASUREMENT_HEAD": self.head,
                "PY": f"{self.measurement_root}/.venv/bin/python",
            },
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
        self.directory = tempfile.TemporaryDirectory()
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

        self.fixture.write_plan(t0_epoch_s=T0_EPOCH_S + 0.75, window_max_s=600)
        self.assertEqual(self.fixture.emit().returncode, 0)
        exports = _exports(self.fixture.out.read_text())
        self.assertEqual(exports["WINDOW_END_EPOCH_S"], str(int(T0_EPOCH_S + 0.75 + 600)))
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
        self.assertEqual(self.fixture.emit("--slot-count", "8", "--allow-slot-count").returncode, 0)
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
