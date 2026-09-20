from __future__ import annotations

import copy
import hashlib
import inspect
import json
import re
import unittest
from pathlib import Path
from unittest import mock

from joulewise import night_gate
from joulewise.night_plan_writer import night_plan_mapping


HEAD = "a" * 40
BOOT_UUID = "12345678-1234-5678-9234-567812345678"
CHAIN_TEXT = "#!/bin/zsh\necho night\n"
REGISTRATION_TEXT = (Path(__file__).resolve().parents[1] / night_gate.D166_REGISTRATION_PATH).read_text()
RETIRED_V1 = Path(__file__).resolve().parent / "fixtures" / "night_plan_v1_retired.json"


def result(
    argv: tuple[str, ...],
    *,
    exit_code: int = 0,
    stdout: str = "",
    stderr: str = "",
    monotonic_ns: int = 10,
) -> night_gate.ProbeResult:
    return night_gate.ProbeResult(argv, exit_code, stdout, stderr, monotonic_ns)


def green_results() -> dict[tuple[str, ...], night_gate.ProbeResult]:
    return {
        night_gate.AGENT_CENSUS_ARGV: result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=1
        ),
        night_gate.HID_IDLE_ARGV: result(night_gate.HID_IDLE_ARGV, stdout="0\n"),
        night_gate.PMSET_BATT_ARGV: result(
            night_gate.PMSET_BATT_ARGV,
            stdout="Now drawing from 'AC Power'\n",
        ),
        night_gate.PMSET_GENERAL_ARGV: result(
            night_gate.PMSET_GENERAL_ARGV,
            stdout="System-wide power settings:\n displaysleep 0\n sleep 0\n",
        ),
        night_gate.LOAD_AVG_ARGV: result(
            night_gate.LOAD_AVG_ARGV, stdout="{ 0.75 0.63 0.58 }\n"
        ),
        night_gate.THERMAL_ARGV: result(
            night_gate.THERMAL_ARGV,
            stdout="Note: No thermal warning level has been recorded\n",
        ),
        night_gate.BOOT_SESSION_ARGV: result(
            night_gate.BOOT_SESSION_ARGV, stdout=BOOT_UUID + "\n"
        ),
    }


class FakeProbeSource:
    def __init__(
        self,
        *,
        results: dict[tuple[str, ...], night_gate.ProbeResult] | None = None,
        now_epoch_s: float = 1_005.0,
        checkout_head: str = HEAD,
        measurement_head: str = HEAD,
        chain_text: str = CHAIN_TEXT,
        chain_digest: str | None = None,
        registration_text: str = REGISTRATION_TEXT,
    ) -> None:
        self.results = green_results() if results is None else results
        self.now_value = now_epoch_s
        self.head_value = checkout_head
        self.measurement_head_value = measurement_head
        self.text = {
            "/custody/chain.zsh": chain_text,
            "/custody/chain.zsh.sha256": chain_digest
            if chain_digest is not None
            else hashlib.sha256(chain_text.encode("utf-8")).hexdigest() + "\n",
            "/custody/registration.json": registration_text,
        }
        self.run_calls: list[tuple[str, ...]] = []
        self.read_calls: list[str] = []
        self.now_calls = 0
        self.monotonic_calls = 0
        self.monotonic_error: Exception | None = None
        self.checkout_calls = 0
        self.measurement_calls: list[str] = []
        self.measurement_error: Exception | None = None
        self.raise_for: dict[tuple[str, ...], Exception] = {}

    def run(self, argv: tuple[str, ...]) -> night_gate.ProbeResult:
        self.run_calls.append(argv)
        if argv in self.raise_for:
            raise self.raise_for[argv]
        return self.results[argv]

    def now(self) -> float:
        self.now_calls += 1
        return self.now_value

    def monotonic(self) -> int:
        self.monotonic_calls += 1
        if self.monotonic_error is not None:
            raise self.monotonic_error
        return 99_000 + self.monotonic_calls

    def read_text(self, path: str) -> str:
        self.read_calls.append(path)
        return self.text[path]

    def checkout_head(self) -> str:
        self.checkout_calls += 1
        return self.head_value

    def measurement_head(self, root: str) -> str:
        self.measurement_calls.append(root)
        if self.measurement_error is not None:
            raise self.measurement_error
        return self.measurement_head_value

    def probes(self) -> night_gate.Probes:
        return night_gate.Probes(
            run=self.run,
            now_epoch_s=self.now,
            monotonic_ns=self.monotonic,
            read_text=self.read_text,
            checkout_head=self.checkout_head,
            measurement_head=self.measurement_head,
        )


class MissingChainProbeSource(FakeProbeSource):
    def __init__(self, plan: night_gate.NightPlan) -> None:
        super().__init__()
        self.missing_paths = {plan.chain_path, plan.chain_sha256_path}

    def read_text(self, path: str) -> str:
        if path in self.missing_paths:
            self.read_calls.append(path)
            raise FileNotFoundError(2, "No such file or directory", path)
        return super().read_text(path)


def make_plan(receipt_class: str = "DIAGNOSTIC_NO_PACK", **changes: object) -> night_gate.NightPlan:
    values: dict[str, object] = {
        "plan_id": "night-001",
        "receipt_class": receipt_class,
        "t0_epoch_s": 1_000.0,
        "window_max_s": 60,
        "authored_epoch_s": 900.0,
        "repo_head": HEAD,
        "measurement_root": "/measurement-checkout",
        "measurement_head": HEAD,
        "chain_path": "/custody/chain.zsh",
        "chain_sha256_path": "/custody/chain.zsh.sha256",
        "custody_root": "/custody",
        "registration_path": None
        if receipt_class == "TRANSACTION_PACK"
        else "/custody/registration.json",
    }
    values.update(changes)
    return night_gate.NightPlan(**values)  # type: ignore[arg-type]


def plan_mapping(receipt_class: str = "DIAGNOSTIC_NO_PACK") -> dict[str, object]:
    return night_plan_mapping(make_plan(receipt_class))


class PackPreArmIdentityTests(unittest.TestCase):
    def test_wrong_clone_refuses_without_writing_arm_for_every_pack_purpose(self):
        from dataclasses import replace
        from joulewise.night_plan_writer import write_night_plan
        from tests.test_run_night import PackNightProducerTests

        for purpose in ("T0_REHEARSAL", "G2B_SHAKEDOWN", "CAMPAIGN_TRANSACTION"):
            with self.subTest(purpose=purpose):
                fixture = PackNightProducerTests()
                try:
                    fixture.setUp()
                    other = fixture.root / "JouleWise-rehearsal-20260909-07681e95"
                    other.mkdir()
                    authorization = dict(fixture.authorization, purpose=purpose)
                    if purpose == "CAMPAIGN_TRANSACTION":
                        authorization["authority"] = "V5-TRANSACTION-GO-01"
                    auth_ref = fixture.write(fixture.custody / "authorization.json", authorization)
                    fixture.plan = replace(
                        fixture.plan, measurement_root=str(other),
                        pack_night={**fixture.plan.pack_night, "authorization_record": auth_ref},
                    )
                    write_night_plan(fixture.plan_path, fixture.plan)
                    code, launches = fixture.run_driver()
                    self.assertEqual(fixture.driver.EXIT_REFUSED, code)
                    refusal = json.loads((fixture.custody / "night/refusal.json").read_bytes())["refusal"]
                    self.assertEqual("launch_go_receipt_invalid", refusal["reason"])
                    self.assertEqual("measurement_root: launcher is not the planned clone", refusal["detail"])
                    fixture.author.author_arm_readiness_evidence_t0.assert_not_called()
                    fixture.readiness.generate_arm_receipt.assert_not_called()
                    self.assertFalse(fixture.arm_path.exists())
                    self.assertEqual([], list(fixture.custody.rglob("arm_readiness.receipts/*.json")))
                    self.assertFalse((fixture.custody / "night/go_receipt.json").exists())
                    self.assertEqual([], launches)
                finally:
                    fixture.doCleanups()


class RegistrationSeamTests(unittest.TestCase):
    RUNBOOK = Path(__file__).resolve().parents[1] / "docs/phase_2/derivation_night_runbook.md"

    def test_runbook_arm_block_checks_d166_registration(self) -> None:
        """T2: following the foreground arm block must not select the wrong file."""
        blocks = re.findall(r"^```[^\n]*\n(.*?)^```", self.RUNBOOK.read_text(), re.M | re.S)
        arm_blocks = [
            block for block in blocks
            if "assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'" in block
        ]
        self.assertEqual(len(arm_blocks), 1)
        self.assertIn(
            "assert plan.registration_path == night_gate.D166_REGISTRATION_PATH",
            arm_blocks[0],
        )
        self.assertNotIn("preregistration_d079_epoch_25g83_rev1.md", arm_blocks[0])

    def test_runbook_registration_path_references_name_d166(self) -> None:
        """T3: prose must not steer an operator back to the scientific pre-registration."""
        section = None
        references = []
        index_rows = []
        for number, line in enumerate(self.RUNBOOK.read_text().splitlines(), 1):
            if line.startswith("## "):
                section = line
            if "registration_path" not in line:
                continue
            if section == "## 7. Fact table — where each load-bearing fact came from" and line.startswith("| v2 plan required keys,"):
                index_rows.append(line)
                continue
            references.append((number, line))
        self.assertEqual(len(index_rows), 1)
        self.assertTrue(references)
        for number, line in references:
            with self.subTest(line=number):
                self.assertRegex(line, r"D-166|D166_REGISTRATION_PATH")

    def test_runbook_never_writes_unbraced_dollar_h_before_a_colon(self) -> None:
        # Opus counter-review 07 B1 (activation 3dab9c89): in zsh an unbraced
        # "$H:" is a history-style modifier; git then receives "<hash-1>path",
        # rev-parse exits 128 and "git show | shasum" prints the digest of
        # EMPTY input -- a false STOP on the PASS route. Require "${H}:".
        offenders = [
            f"{number}: {line.strip()}"
            for number, line in enumerate(self.RUNBOOK.read_text().splitlines(), 1)
            if re.search(r"\$H:", line)
        ]
        self.assertEqual([], offenders)

    def test_real_pre_registration_refuses_but_d166_passes_c1(self) -> None:
        """T4 documents the registration seam; it already passes on main.

        Only machine probes are fixtures: registration text and the gate's
        digest constant are real, with no constant mock or live capture.
        """
        root = Path(__file__).resolve().parents[1]
        pre_registration = "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
        for path, expected_status in (
            (pre_registration, "FAIL"),
            (night_gate.D166_REGISTRATION_PATH, "PASS"),
        ):
            with self.subTest(path=path):
                source = FakeProbeSource()
                registration_path = str(Path(make_plan().measurement_root) / path)
                source.text[registration_path] = (root / path).read_text(encoding="utf-8")
                receipt = night_gate.evaluate_night(
                    make_plan(registration_path=path), source.probes()
                )
                c1 = next(row for row in receipt.conditions if row.condition_id == "C1")
                self.assertEqual(c1.status, expected_status)
                self.assertIn(registration_path, source.read_calls)
                if expected_status == "FAIL":
                    self.assertEqual(receipt.refusal.reason, "night_refused_registration")
                else:
                    self.assertIsNone(receipt.refusal)
                    self.assertEqual(c1.measured["detail"], "D-166 registration hash passed")


class NightGateTests(unittest.TestCase):
    def evaluate(
        self, plan: night_gate.NightPlan, source: FakeProbeSource
    ) -> night_gate.Receipt:
        registration_hash = hashlib.sha256(REGISTRATION_TEXT.encode("utf-8")).hexdigest()
        with mock.patch.object(
            night_gate, "D166_REGISTRATION_SHA256", registration_hash
        ):
            return night_gate.evaluate_night(plan, source.probes())

    def test_production_argv_constant_is_the_self_excluding_census_pattern(self) -> None:
        self.assertEqual(
            ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"),
            night_gate.AGENT_CENSUS_ARGV,
        )
        self.assertEqual(
            ("/usr/bin/defaults", "-currentHost", "read", "com.apple.screensaver", "idleTime"),
            night_gate.HID_IDLE_ARGV,
        )
        self.assertEqual(("/usr/bin/pmset", "-g", "batt"), night_gate.PMSET_BATT_ARGV)
        self.assertEqual(("/usr/bin/pmset", "-g"), night_gate.PMSET_GENERAL_ARGV)
        self.assertEqual(
            ("/usr/sbin/sysctl", "-n", "vm.loadavg"), night_gate.LOAD_AVG_ARGV
        )
        self.assertEqual(("/usr/bin/pmset", "-g", "therm"), night_gate.THERMAL_ARGV)
        self.assertEqual(
            ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),
            night_gate.BOOT_SESSION_ARGV,
        )

    def test_plan_schema_literal_is_v2(self) -> None:
        self.assertEqual("joulewise.night_plan.v2", night_gate.PLAN_SCHEMA)

    def test_d166_registration_digest_is_the_ruled_literal(self) -> None:
        self.assertEqual(
            "dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265",
            night_gate.D166_REGISTRATION_SHA256,
        )

    def test_d166_registration_file_hashes_to_the_ruled_literal(self) -> None:
        # The gate hashes the FILE at plan.registration_path the way the
        # driver reads it (utf-8 text re-encoded); the tracked registration
        # file must therefore carry exactly the canonical D-166 bytes.
        from pathlib import Path

        from configs.campaigns.d117_contrast_v5.generate_configs import (
            dominance_criterion_registration,
        )
        from joulewise.analysis_manifest_v3 import canonical_json_bytes

        path = Path(night_gate.__file__).resolve().parents[1] / night_gate.D166_REGISTRATION_PATH
        text = path.read_text(encoding="utf-8")
        self.assertEqual(
            canonical_json_bytes(dominance_criterion_registration()), text.encode("utf-8")
        )
        self.assertEqual(
            night_gate.D166_REGISTRATION_SHA256,
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
        )

    def test_an_exit_one_census_with_only_whitespace_is_clean(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=1, stdout=" \n\t"
        )
        observed, refusal = night_gate.agent_census(source.probes())
        self.assertEqual(1, observed.exit_code)
        self.assertIsNone(refusal)

    def test_census_does_not_match_peer_argv(self) -> None:
        """Old literal + sibling pgrep argv falsely refuses at agent_census."""
        peer = "79146 " + " ".join(night_gate.AGENT_CENSUS_ARGV)

        def census(processes):
            def run(argv):
                # Model pgrep -f over full command lines, using the requested
                # production regex rather than supplying a pre-filtered result.
                hits = [line for line in processes if re.search(argv[-1], line)]
                return result(argv, exit_code=0 if hits else 1,
                              stdout="".join(line + "\n" for line in hits))
            return night_gate.agent_census(mock.Mock(run=run, monotonic_ns=lambda: 10))

        observed, refusal = census([peer])
        self.assertIsNone(refusal)
        self.assertEqual("", observed.stdout)
        for command in ("/usr/bin/claude -p", "node codex mcp-server", "t3 code",
                        # Refuter 10 F1: a foreign agent whose argv also names pgrep
                        # must stay visible; a pgrep-line post-filter would hide it.
                        "/usr/bin/claude -p inspect /usr/bin/pgrep"):
            with self.subTest(command=command):
                observed, refusal = census([peer, "42 " + command])
                self.assertEqual("night_refused_agent_present", refusal.reason)
                self.assertEqual("42 " + command + "\n", observed.stdout)
        for outcome in (None, OSError("process list unavailable")):
            with self.subTest(probe=outcome):
                run = mock.Mock(side_effect=outcome) if isinstance(outcome, Exception) else mock.Mock(return_value=outcome)
                _, refusal = night_gate.agent_census(mock.Mock(run=run, monotonic_ns=lambda: 10))
                self.assertEqual("night_probe_error", refusal.reason)

    def test_a_census_that_finds_lines_refuses_and_preserves_them(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV,
            exit_code=0,
            stdout="42 claude\n43 codex\n",
        )
        _, refusal = night_gate.agent_census(source.probes())
        self.assertEqual("night_refused_agent_present", refusal.reason)
        self.assertIn("42 claude", refusal.detail)
        self.assertIn("43 codex", refusal.detail)

    def test_a_desktop_app_bundled_agent_server_refuses_the_census(self) -> None:
        # Ruling 2026-09-13 (NIGHT-CENSUS-CHATGPT-APP-01): the ChatGPT app's
        # bundled Codex CLI is an agent process; the pattern is not narrowed.
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV,
            exit_code=0,
            stdout=(
                "25658 /Applications/ChatGPT.app/Contents/Resources/codex "
                "-c features.code_mode_host=true app-server\n"
            ),
        )
        _, refusal = night_gate.agent_census(source.probes())
        self.assertEqual("night_refused_agent_present", refusal.reason)
        self.assertIn("25658 /Applications/ChatGPT.app", refusal.detail)
        self.assertEqual(("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3"), night_gate.AGENT_CENSUS_ARGV)

    def test_a_nonmatch_exit_with_output_still_refuses_the_census(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=1, stdout="42 t3\n"
        )
        _, refusal = night_gate.agent_census(source.probes())
        self.assertEqual("night_refused_agent_present", refusal.reason)
        self.assertIn("42 t3", refusal.detail)

    def test_census_refusal_detail_is_bounded_to_twenty_lines(self) -> None:
        source = FakeProbeSource()
        lines = [f"process {index}" for index in range(586)]
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV,
            exit_code=0,
            stdout="\n".join(lines) + "\n",
        )
        _, refusal = night_gate.agent_census(source.probes())
        self.assertEqual(21, len(refusal.detail.splitlines()))
        self.assertIn("process 19", refusal.detail)
        self.assertNotIn("process 20", refusal.detail)
        self.assertTrue(refusal.detail.endswith("… (+566 more)"))

    def test_an_error_exit_refuses_and_names_the_pgrep_status(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=2, stderr="usage"
        )
        _, refusal = night_gate.agent_census(source.probes())
        self.assertEqual("night_refused_agent_present", refusal.reason)
        self.assertIn("pgrep exit 2", refusal.detail)

    def test_a_census_timeout_fails_closed_as_a_probe_error(self) -> None:
        source = FakeProbeSource()
        source.raise_for[night_gate.AGENT_CENSUS_ARGV] = night_gate.ProbeError(
            "timed out"
        )
        observed, refusal = night_gate.agent_census(source.probes())
        self.assertEqual(-1, observed.exit_code)
        self.assertEqual("night_probe_error", refusal.reason)
        self.assertIn("timed out", refusal.detail)

    def test_a_plan_requires_an_exact_schema_and_key_set(self) -> None:
        good = plan_mapping()
        self.assertEqual(make_plan(), night_gate.NightPlan.from_mapping(good))
        for field, bad_value in (
            ("schema", "wrong"),
            ("repo_head", "A" * 40),
            ("window_max_s", True),
            ("registration_path", None),
        ):
            with self.subTest(field=field):
                bad = dict(good)
                bad[field] = bad_value
                with self.assertRaises(night_gate.PlanError) as raised:
                    night_gate.NightPlan.from_mapping(bad)
                self.assertEqual("night_plan_malformed", raised.exception.reason)
                self.assertIn(field, raised.exception.detail)
        extra = dict(good, surprise=True)
        with self.assertRaises(night_gate.PlanError) as raised:
            night_gate.NightPlan.from_mapping(extra)
        self.assertEqual("night_plan_malformed", raised.exception.reason)

        retired = json.loads(RETIRED_V1.read_text(encoding="utf-8"))
        with self.assertRaises(night_gate.PlanError) as retired_error:
            night_gate.NightPlan.from_mapping(retired)
        self.assertEqual("night_plan_malformed", retired_error.exception.reason)
        self.assertIn("joulewise.night_plan.v1 is retired", retired_error.exception.detail)
        self.assertIn(
            "re-authored under joulewise.night_plan.v2", retired_error.exception.detail
        )

        malformed_v2_cases: list[tuple[str, dict[str, object]]] = []
        for missing_field in ("measurement_head", "measurement_root"):
            missing = dict(good)
            del missing[missing_field]
            malformed_v2_cases.append((f"missing_{missing_field}", missing))
        relative_root = dict(good)
        relative_root["measurement_root"] = "relative/checkout"
        malformed_v2_cases.append(("relative_measurement_root", relative_root))
        bad_measurement_head = dict(good)
        bad_measurement_head["measurement_head"] = "A" * 40
        malformed_v2_cases.append(("bad_measurement_head", bad_measurement_head))
        for name, malformed in malformed_v2_cases:
            with self.subTest(malformed_v2_case=name):
                with self.assertRaises(night_gate.PlanError) as malformed_error:
                    night_gate.NightPlan.from_mapping(malformed)
                self.assertEqual(
                    "night_plan_malformed", malformed_error.exception.reason
                )
                self.assertNotIn(
                    "joulewise.night_plan.v1", malformed_error.exception.detail
                )

    def test_a_direct_plan_with_missing_registration_is_refused_as_malformed(self) -> None:
        source = FakeProbeSource()
        receipt = self.evaluate(make_plan(registration_path=None), source)
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("night_plan_malformed", receipt.refusal.reason)
        self.assertEqual([], source.run_calls)
        self.assertEqual([], source.read_calls)

    def test_the_class_table_matches_the_ruled_condition_matrix(self) -> None:
        expected = {
            "DIAGNOSTIC_NO_PACK": {
                "C1": ("PASS", None),
                "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
                "C3": ("PASS", None),
                "C4": ("PASS", None),
                "C5": ("PASS", None),
            },
            "REHEARSAL_STUB": {
                "C1": ("PASS", None),
                "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
                "C3": ("PASS", None),
                "C4": ("PASS", None),
                "C5": ("PASS", None),
            },
            "TRANSACTION_PACK": {
                condition_id: ("PASS", None)
                for condition_id in ("C1", "C2", "C3", "C4", "C5")
            },
        }
        self.assertEqual(expected, night_gate.class_table())

    def test_a_green_diagnostic_plan_yields_a_valid_go_receipt(self) -> None:
        source = FakeProbeSource()
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("GO", receipt.verdict)
        self.assertIsNone(receipt.refusal)
        self.assertEqual(
            ["PASS", "NOT_APPLICABLE", "PASS", "PASS", "PASS"],
            [row.status for row in receipt.conditions],
        )
        self.assertEqual("no_pack_by_design", receipt.conditions[1].basis)
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5")
        self.assertEqual(
            "window, plan freshness, measurement HEAD, and chain identity passed",
            c5.measured["detail"],
        )
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

    def test_a_fully_green_rehearsal_can_never_yield_go(self) -> None:
        receipt = self.evaluate(make_plan("REHEARSAL_STUB"), FakeProbeSource())
        self.assertEqual("REHEARSAL_ONLY", receipt.verdict)
        self.assertTrue(all(row.status == "PASS" for row in receipt.conditions if row.condition_id != "C2"))
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

    def test_rehearsal_stub_does_not_read_missing_chain_or_sidecar(self) -> None:
        plan = make_plan("REHEARSAL_STUB")
        source = MissingChainProbeSource(plan)
        receipt = self.evaluate(plan, source)
        self.assertEqual("REHEARSAL_ONLY", receipt.verdict, repr(receipt.refusal))
        self.assertIsNone(receipt.refusal)
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))
        self.assertNotIn(plan.chain_path, source.read_calls)
        self.assertNotIn(plan.chain_sha256_path, source.read_calls)
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5")
        self.assertEqual(plan.chain_path, c5.measured["chain_path"])
        self.assertEqual(plan.chain_sha256_path, c5.measured["chain_sha256_path"])
        self.assertIsNone(c5.measured["chain_sha256"])
        self.assertIsNone(c5.measured["expected_chain_sha256"])
        self.assertEqual("built_in_stub_by_design", c5.measured["chain_stub"])
        self.assertEqual(
            "window, plan freshness, and measurement HEAD passed; chain identity not evaluated "
            "(driver substitutes the built-in stub)",
            c5.measured["detail"],
        )
        self.assertEqual("PASS", c5.status)
        self.assertIsNone(c5.basis)

    def test_rehearsal_stub_does_not_read_present_mismatched_chain_or_sidecar(self) -> None:
        plan = make_plan("REHEARSAL_STUB")
        source = FakeProbeSource(chain_digest="0" * 64)
        receipt = self.evaluate(plan, source)
        self.assertEqual("REHEARSAL_ONLY", receipt.verdict, repr(receipt.refusal))
        self.assertIsNone(receipt.refusal)
        self.assertNotIn(plan.chain_path, source.read_calls)
        self.assertNotIn(plan.chain_sha256_path, source.read_calls)

    def test_diagnostic_still_refuses_missing_chain_or_sidecar(self) -> None:
        for missing in ("chain_path", "chain_sha256_path"):
            with self.subTest(missing=missing):
                plan = make_plan()
                source = MissingChainProbeSource(plan)
                source.missing_paths = {getattr(plan, missing)}
                receipt = self.evaluate(plan, source)
                self.assertEqual("REFUSED", receipt.verdict)
                self.assertEqual("night_probe_error", receipt.refusal.reason)
                self.assertIn("FileNotFoundError", receipt.refusal.detail)
                self.assertIn(getattr(plan, missing), source.read_calls)

    def test_a_transaction_plan_is_refused_until_stage_three_exists(self) -> None:
        source = FakeProbeSource()
        receipt = self.evaluate(make_plan("TRANSACTION_PACK"), source)
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("FAIL", receipt.conditions[0].status)
        self.assertEqual("stage 3 not implemented", receipt.conditions[0].measured["detail"])
        self.assertEqual("night_refused_class_unbuilt", receipt.refusal.reason)
        self.assertEqual(
            "stage 3 not implemented: TRANSACTION_PACK is pack-bound and stays under E-10 (ruling R-10)",
            receipt.refusal.detail,
        )
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))
        self.assertNotIn("/custody/registration.json", source.read_calls)

    def test_an_agent_present_outranks_the_unbuilt_transaction_class(self) -> None:
        # R-3 census-first: the zero-agent fence is checked before the class
        # table, so a TRANSACTION_PACK plan on a busy machine names the agent,
        # not the unbuilt stage (terra delta re-audit 125, S1 observation).
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="42 claude\n"
        )
        receipt = self.evaluate(make_plan("TRANSACTION_PACK"), source)
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("night_refused_agent_present", receipt.refusal.reason)
        self.assertIn("42 claude", receipt.refusal.detail)

    def test_every_class_round_trips_through_the_consumer_validator(self) -> None:
        for receipt_class in night_gate.RECEIPT_CLASSES:
            with self.subTest(receipt_class=receipt_class):
                receipt = self.evaluate(make_plan(receipt_class), FakeProbeSource())
                decoded = json.loads(receipt.to_json_bytes())
                self.assertEqual([], night_gate.validate_receipt(decoded))

    def test_canonical_receipt_bytes_are_sorted_indented_ascii_and_newline_terminated(self) -> None:
        receipt = self.evaluate(make_plan(), FakeProbeSource())
        encoded = receipt.to_json_bytes()
        self.assertTrue(encoded.endswith(b"\n"))
        self.assertIn(b'  "authored_monotonic_ns"', encoded)
        self.assertLess(encoded.index(b'"authored_monotonic_ns"'), encoded.index(b'"conditions"'))
        self.assertEqual(encoded, receipt.to_json_bytes())

        non_ascii_source = FakeProbeSource()
        non_ascii_source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="42 naïve-agent\n"
        )
        non_ascii_receipt = self.evaluate(make_plan(), non_ascii_source)
        non_ascii = non_ascii_receipt.to_json_bytes()
        self.assertIn(b"na\\u00efve-agent", non_ascii)
        self.assertEqual(non_ascii, non_ascii_receipt.to_json_bytes())

    def test_window_refusal_performs_no_command_or_file_or_head_probe(self) -> None:
        source = FakeProbeSource(now_epoch_s=2_000.0)
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("night_window_expired", receipt.refusal.reason)
        self.assertEqual([], source.run_calls)
        self.assertEqual([], source.read_calls)
        self.assertEqual(0, source.checkout_calls)
        self.assertEqual([], source.measurement_calls)

    def test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current(self) -> None:
        wrong_head = FakeProbeSource(measurement_head="b" * 40)
        receipt = self.evaluate(make_plan(), wrong_head)
        self.assertEqual("night_plan_stale", receipt.refusal.reason)
        self.assertIn("measurement_head", receipt.refusal.detail)
        self.assertEqual([], wrong_head.run_calls)

        boundary = FakeProbeSource()
        receipt = self.evaluate(
            make_plan(authored_epoch_s=boundary.now_value - night_gate.PLAN_MAX_AGE_S),
            boundary,
        )
        self.assertEqual("GO", receipt.verdict)

    def test_driver_checkout_head_movement_is_informational_and_census_still_runs(self) -> None:
        source = FakeProbeSource(checkout_head="b" * 40)
        receipt = self.evaluate(make_plan(), source)
        self.assertNotEqual(
            "night_plan_stale",
            None if receipt.refusal is None else receipt.refusal.reason,
        )
        self.assertIn(night_gate.AGENT_CENSUS_ARGV, source.run_calls)
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5")
        self.assertEqual("b" * 40, c5.measured["driver_checkout_head"])
        self.assertEqual(HEAD, c5.measured["plan_repo_head"])

    def test_measurement_checkout_probe_failure_uses_existing_probe_refusal(self) -> None:
        source = FakeProbeSource()
        source.measurement_error = RuntimeError("measurement path is not a git repo")
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("night_probe_error", receipt.refusal.reason)
        self.assertIn("measurement path is not a git repo", receipt.refusal.detail)
        self.assertEqual([], source.run_calls)

    def test_plan_age_refusals_precede_head_probes(self) -> None:
        cases = (
            (-200_000.0, "night_plan_stale"),
            (1_006.0, "night_plan_malformed"),
        )
        for authored_epoch_s, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                source = FakeProbeSource()
                source.measurement_error = RuntimeError("head probe must not run")
                receipt = self.evaluate(
                    make_plan(authored_epoch_s=authored_epoch_s), source
                )
                self.assertEqual(expected_reason, receipt.refusal.reason)
                self.assertEqual([], source.measurement_calls)
                self.assertEqual(0, source.checkout_calls)

    def test_a_future_dated_plan_is_malformed(self) -> None:
        source = FakeProbeSource()
        receipt = self.evaluate(make_plan(authored_epoch_s=source.now_value + 1.0), source)
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("night_plan_malformed", receipt.refusal.reason)
        self.assertIn("future", receipt.refusal.detail)

    def test_chain_sidecar_accepts_bare_hex_and_gnu_shasum_forms(self) -> None:
        digest = hashlib.sha256(CHAIN_TEXT.encode("utf-8")).hexdigest()
        for sidecar in (digest + "\n", f"{digest}  chain.zsh\n"):
            with self.subTest(sidecar=sidecar):
                receipt = self.evaluate(
                    make_plan(), FakeProbeSource(chain_digest=sidecar)
                )
                self.assertEqual("GO", receipt.verdict)

    def test_chain_sidecar_refuses_case_name_and_token_count_defects(self) -> None:
        digest = hashlib.sha256(CHAIN_TEXT.encode("utf-8")).hexdigest()
        cases = (
            (" \n", "token check"),
            (digest.upper() + "\n", "digest check"),
            (f"{digest}  wrong.zsh\n", "basename check"),
            (f"{digest}  a  b\n", "token check"),
        )
        for sidecar, detail in cases:
            with self.subTest(sidecar=sidecar):
                receipt = self.evaluate(
                    make_plan(), FakeProbeSource(chain_digest=sidecar)
                )
                self.assertEqual("night_chain_digest_mismatch", receipt.refusal.reason)
                self.assertIn(detail, receipt.refusal.detail)

    def test_first_refusal_order_advances_one_ruled_gate_at_a_time(self) -> None:
        def all_later_failures() -> FakeProbeSource:
            source = FakeProbeSource(chain_digest="0" * 64, registration_text="wrong")
            source.results[night_gate.AGENT_CENSUS_ARGV] = result(
                night_gate.AGENT_CENSUS_ARGV, exit_code=0, stdout="42 claude\n"
            )
            source.results[night_gate.HID_IDLE_ARGV] = result(
                night_gate.HID_IDLE_ARGV, stdout="1200\n"
            )
            source.results[night_gate.PMSET_BATT_ARGV] = result(
                night_gate.PMSET_BATT_ARGV, stdout="Now drawing from 'Battery Power'\n"
            )
            source.results[night_gate.BOOT_SESSION_ARGV] = result(
                night_gate.BOOT_SESSION_ARGV, stdout="not-a-uuid\n"
            )
            return source

        for index, expected_reason in enumerate(night_gate.ORDER):
            source = all_later_failures()
            plan = make_plan()
            if index == 0:
                source.now_value = 2_000.0
            else:
                source.now_value = 1_005.0
            if index == 1:
                plan = make_plan(authored_epoch_s=-200_000.0)
            elif index > 1:
                plan = make_plan()
            if index > 2:
                source.results[night_gate.AGENT_CENSUS_ARGV] = result(
                    night_gate.AGENT_CENSUS_ARGV, exit_code=1
                )
            if index > 3:
                source.text["/custody/chain.zsh.sha256"] = (
                    hashlib.sha256(CHAIN_TEXT.encode("utf-8")).hexdigest() + "\n"
                )
            if index == 4:
                plan = make_plan("TRANSACTION_PACK")
            if index > 5:
                source.results[night_gate.HID_IDLE_ARGV] = result(
                    night_gate.HID_IDLE_ARGV, stdout="0\n"
                )
            if index > 6:
                source.results[night_gate.PMSET_BATT_ARGV] = result(
                    night_gate.PMSET_BATT_ARGV, stdout="Now drawing from 'AC Power'\n"
                )
            if index > 7:
                source.results[night_gate.BOOT_SESSION_ARGV] = result(
                    night_gate.BOOT_SESSION_ARGV, stdout=BOOT_UUID + "\n"
                )
            with self.subTest(index=index, reason=expected_reason):
                receipt = self.evaluate(plan, source)
                self.assertEqual(expected_reason, receipt.refusal.reason)

    def test_quiet_predicates_run_fixed_commands_and_record_raw_stdout(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.PMSET_GENERAL_ARGV] = result(
            night_gate.PMSET_GENERAL_ARGV, stdout=" displaysleep 17\n"
        )
        source.results[night_gate.LOAD_AVG_ARGV] = result(
            night_gate.LOAD_AVG_ARGV, stdout="{ 2.0 1.0 0.5 }\n"
        )
        source.results[night_gate.THERMAL_ARGV] = result(
            night_gate.THERMAL_ARGV, stdout="CPU_Speed_Limit = 100\n"
        )
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("GO", receipt.verdict)
        self.assertEqual(
            [
                night_gate.AGENT_CENSUS_ARGV,
                night_gate.HID_IDLE_ARGV,
                night_gate.PMSET_BATT_ARGV,
                night_gate.PMSET_GENERAL_ARGV,
                night_gate.LOAD_AVG_ARGV,
                night_gate.THERMAL_ARGV,
                night_gate.BOOT_SESSION_ARGV,
            ],
            source.run_calls,
        )
        measured = receipt.conditions[2].measured
        self.assertEqual("17", measured["displaysleep"])
        self.assertEqual(2.0, measured["load_1m"])
        self.assertEqual("100", measured["cpu_speed_limit"])
        self.assertIn("AC Power", measured["ac_power_raw"])
        self.assertIn("displaysleep", measured["pmset_g_raw"])
        self.assertIn("2.0", measured["load_average_raw"])
        self.assertIn("CPU_Speed_Limit", measured["thermal_raw"])

    def test_load_average_requires_the_exact_sysctl_shape(self) -> None:
        malformed = FakeProbeSource()
        malformed.results[night_gate.LOAD_AVG_ARGV] = result(
            night_gate.LOAD_AVG_ARGV, stdout="warning 0.1\n"
        )
        receipt = self.evaluate(make_plan(), malformed)
        self.assertEqual("night_probe_error", receipt.refusal.reason)
        self.assertIn("warning 0.1", receipt.refusal.detail)

        exact = FakeProbeSource()
        exact.results[night_gate.LOAD_AVG_ARGV] = result(
            night_gate.LOAD_AVG_ARGV, stdout="{ 0.10 0.20 0.30 }\n"
        )
        receipt = self.evaluate(make_plan(), exact)
        self.assertEqual("GO", receipt.verdict)
        self.assertEqual(0.10, receipt.conditions[2].measured["load_1m"])

    def test_thermal_limit_prefix_with_trailing_text_is_a_probe_error(self) -> None:
        malformed = FakeProbeSource()
        malformed.results[night_gate.THERMAL_ARGV] = result(
            night_gate.THERMAL_ARGV, stdout="CPU_Speed_Limit = 80 trailing\n"
        )
        receipt = self.evaluate(make_plan(), malformed)
        self.assertEqual("night_probe_error", receipt.refusal.reason)
        self.assertIn("thermal output malformed", receipt.refusal.detail)

        no_limit_line = self.evaluate(make_plan(), FakeProbeSource())
        self.assertEqual("GO", no_limit_line.verdict)

    def test_list_form_probe_argv_is_accepted(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = night_gate.ProbeResult(
            list(night_gate.AGENT_CENSUS_ARGV), 1, "", "", 10  # type: ignore[arg-type]
        )
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("GO", receipt.verdict)

    def test_each_quiet_predicate_fails_closed_with_its_name_in_detail(self) -> None:
        cases = (
            (
                night_gate.PMSET_BATT_ARGV,
                result(night_gate.PMSET_BATT_ARGV, stdout="Battery Power\n"),
                "ac_power",
            ),
            (
                night_gate.PMSET_GENERAL_ARGV,
                result(night_gate.PMSET_GENERAL_ARGV, stdout="sleep 0\n"),
                "displaysleep",
            ),
            (
                night_gate.LOAD_AVG_ARGV,
                result(night_gate.LOAD_AVG_ARGV, stdout="{ 2.01 1.0 0.5 }\n"),
                "load_average",
            ),
            (
                night_gate.THERMAL_ARGV,
                result(night_gate.THERMAL_ARGV, stdout="CPU_Speed_Limit = 80\n"),
                "thermal",
            ),
        )
        for argv, replacement, name in cases:
            with self.subTest(predicate=name):
                source = FakeProbeSource()
                source.results[argv] = replacement
                receipt = self.evaluate(make_plan(), source)
                self.assertEqual("night_refused_not_quiet", receipt.refusal.reason)
                self.assertIn(name, receipt.refusal.detail)
                if name == "ac_power":
                    self.assertEqual("ac_power", receipt.refusal.detail)

    def test_hid_idle_requires_the_exact_zero_value(self) -> None:
        for stdout in ("1\n", "{ idleTime = 0; }\n", ""):
            with self.subTest(stdout=stdout):
                source = FakeProbeSource()
                source.results[night_gate.HID_IDLE_ARGV] = result(
                    night_gate.HID_IDLE_ARGV, stdout=stdout
                )
                receipt = self.evaluate(make_plan(), source)
                self.assertEqual("night_refused_hid_idle", receipt.refusal.reason)

    def test_boot_clock_uses_a_canonical_uuid_and_never_invokes_sntp(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.BOOT_SESSION_ARGV] = result(
            night_gate.BOOT_SESSION_ARGV, stdout=BOOT_UUID.upper() + "\n"
        )
        receipt = self.evaluate(make_plan(), source)
        measured = receipt.conditions[3].measured
        self.assertEqual(BOOT_UUID, measured["boot_session_uuid"])
        self.assertIsInstance(measured["clock_epoch_s"], float)
        self.assertIsInstance(measured["clock_monotonic_ns"], int)
        self.assertFalse(any("sntp" in " ".join(argv) for argv in source.run_calls))

    def test_any_probe_exception_refuses_before_later_commands_run(self) -> None:
        source = FakeProbeSource()
        source.raise_for[night_gate.PMSET_GENERAL_ARGV] = TimeoutError("ten seconds")
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("night_probe_error", receipt.refusal.reason)
        self.assertIn("TimeoutError", receipt.refusal.detail)
        self.assertNotIn(night_gate.LOAD_AVG_ARGV, source.run_calls)
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

    def test_monotonic_probe_failure_is_reported_as_a_probe_error(self) -> None:
        source = FakeProbeSource(now_epoch_s=2_000.0)
        source.monotonic_error = RuntimeError("clock unavailable")
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("night_probe_error", receipt.refusal.reason)
        self.assertIn("clock unavailable", receipt.refusal.detail)

    def test_malformed_probe_fields_and_unencodable_text_fail_closed(self) -> None:
        malformed = FakeProbeSource()
        malformed.results[night_gate.HID_IDLE_ARGV] = night_gate.ProbeResult(
            night_gate.HID_IDLE_ARGV, 0, None, "", 10  # type: ignore[arg-type]
        )
        receipt = self.evaluate(make_plan(), malformed)
        self.assertEqual("night_probe_error", receipt.refusal.reason)

        unencodable = FakeProbeSource()
        unencodable.text["/custody/chain.zsh"] = "\ud800"
        receipt = self.evaluate(make_plan(), unencodable)
        self.assertEqual("night_probe_error", receipt.refusal.reason)

    def test_a_wrong_registration_hash_refuses_after_every_machine_gate(self) -> None:
        source = FakeProbeSource(registration_text="altered")
        receipt = self.evaluate(make_plan(), source)
        self.assertEqual("night_refused_registration", receipt.refusal.reason)
        self.assertEqual(night_gate.BOOT_SESSION_ARGV, source.run_calls[-1])

    def test_c2_pass_or_an_unregistered_basis_is_a_class_invalid_defect(self) -> None:
        receipt = json.loads(self.evaluate(make_plan(), FakeProbeSource()).to_json_bytes())
        for field, value in (("status", "PASS"), ("basis", "some_other_basis")):
            with self.subTest(field=field):
                changed = copy.deepcopy(receipt)
                changed["conditions"][1][field] = value
                defects = night_gate.validate_receipt(changed)
                self.assertTrue(any("night_receipt_class_invalid" in item for item in defects))

    def test_receipt_rows_are_paired_with_class_rules_by_row_id(self) -> None:
        receipt = json.loads(self.evaluate(make_plan(), FakeProbeSource()).to_json_bytes())
        receipt["conditions"] = list(reversed(receipt["conditions"]))
        self.assertEqual([], night_gate.validate_receipt(receipt))

    def test_verdict_and_refusal_nullability_are_bidirectional(self) -> None:
        go_receipt = json.loads(
            self.evaluate(make_plan(), FakeProbeSource()).to_json_bytes()
        )
        go_receipt["refusal"] = {
            "reason": "night_probe_error",
            "detail": "injected",
            "evidence": [],
        }
        defects = night_gate.validate_receipt(go_receipt)
        self.assertTrue(any("GO verdict requires null" in item for item in defects))

        refused = json.loads(
            self.evaluate(make_plan("TRANSACTION_PACK"), FakeProbeSource()).to_json_bytes()
        )
        refused["refusal"] = None
        defects = night_gate.validate_receipt(refused)
        self.assertTrue(
            any("REFUSED verdict requires a refusal object" in item for item in defects)
        )

    def test_each_single_field_tamper_is_named_by_the_validator(self) -> None:
        original = json.loads(self.evaluate(make_plan(), FakeProbeSource()).to_json_bytes())

        def set_value(path: tuple[object, ...], value: object) -> dict[str, object]:
            changed = copy.deepcopy(original)
            target: object = changed
            for component in path[:-1]:
                target = target[component]  # type: ignore[index]
            target[path[-1]] = value  # type: ignore[index]
            return changed

        cases = (
            (("schema",), "wrong", "schema"),
            (("receipt_class",), "ALIEN", "receipt_class"),
            (("plan_id",), "", "plan_id"),
            (("verdict",), "REFUSED", "verdict"),
            (("authored_monotonic_ns",), True, "authored_monotonic_ns"),
            (("conditions", 0, "condition_id"), "C9", "condition_id"),
            (("conditions", 0, "status"), "NOT_APPLICABLE", "class_invalid"),
            (("conditions", 0, "basis"), "invented", "class_invalid"),
            (("conditions", 0, "evidence"), [7], "evidence"),
            (("conditions", 0, "measured"), [], "measured"),
            (("conditions", 1, "status"), "PASS", "class_invalid"),
            (("conditions", 1, "basis"), "wrong", "class_invalid"),
            (("refusal",), {}, "refusal"),
            (("verdict",), [], "verdict"),
        )
        for path, value, needle in cases:
            with self.subTest(path=path):
                defects = night_gate.validate_receipt(set_value(path, value))
                self.assertTrue(defects)
                if needle == "class_invalid":
                    self.assertTrue(
                        any("night_receipt_class_invalid" in defect for defect in defects),
                        defects,
                    )
                else:
                    self.assertTrue(any(needle in defect for defect in defects), defects)

        extra = copy.deepcopy(original)
        extra["extra"] = True
        self.assertTrue(any("receipt" in item for item in night_gate.validate_receipt(extra)))

        condition_extra = copy.deepcopy(original)
        condition_extra["conditions"][0]["extra"] = True
        self.assertTrue(
            any("conditions[0]" in item for item in night_gate.validate_receipt(condition_extra))
        )

    def test_nested_refusal_probe_tampers_are_rejected_by_exact_key_validation(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=2
        )
        original = json.loads(self.evaluate(make_plan(), source).to_json_bytes())
        self.assertEqual([], night_gate.validate_receipt(original))
        cases = (
            ("argv", [], "argv"),
            ("exit_code", True, "exit_code"),
            ("stdout", 4, "stdout"),
            ("stderr", None, "stderr"),
            ("monotonic_ns", -1, "monotonic_ns"),
        )
        for field, value, needle in cases:
            with self.subTest(field=field):
                changed = copy.deepcopy(original)
                changed["refusal"]["evidence"][0][field] = value
                defects = night_gate.validate_receipt(changed)
                self.assertTrue(any(needle in item for item in defects), defects)

    def test_reason_code_registry_is_exactly_the_ruled_set(self) -> None:
        expected = {
            "night_refused_agent_present",
            "night_refused_not_quiet",
            "night_refused_bind_expired",
            "night_refused_hid_idle",
            "night_refused_boot_clock",
            "night_refused_registration",
            "night_window_expired",
            "night_plan_stale",
            "night_plan_malformed",
            "night_chain_digest_mismatch",
            "night_refused_class_unbuilt",
            "launch_go_receipt_missing",
            "launch_go_receipt_invalid",
            "night_receipt_class_invalid",
            "night_probe_error",
        }
        self.assertEqual(night_gate.NIGHT_GATE_REASON_CODES, expected)
        coverage = {
            "night_refused_bind_expired": "test_bind_expiry_code_is_v3_only",
            "night_refused_agent_present": "test_a_census_that_finds_lines_refuses_and_preserves_them",
            "night_refused_not_quiet": "test_each_quiet_predicate_fails_closed_with_its_name_in_detail",
            "night_refused_hid_idle": "test_hid_idle_requires_the_exact_zero_value",
            "night_refused_boot_clock": "test_boot_clock_uses_a_canonical_uuid_and_never_invokes_sntp",
            "night_refused_registration": "test_a_wrong_registration_hash_refuses_after_every_machine_gate",
            "night_window_expired": "test_window_refusal_performs_no_command_or_file_or_head_probe",
            "night_plan_stale": "test_wrong_measurement_head_is_stale_and_the_36_hour_boundary_is_current",
            "night_plan_malformed": "test_a_direct_plan_with_missing_registration_is_refused_as_malformed",
            "night_chain_digest_mismatch": "test_chain_sidecar_refuses_case_name_and_token_count_defects",
            "night_refused_class_unbuilt": "test_a_transaction_plan_is_refused_until_stage_three_exists",
            "night_receipt_class_invalid": "test_c2_pass_or_an_unregistered_basis_is_a_class_invalid_defect",
            "night_probe_error": "test_any_probe_exception_refuses_before_later_commands_run",
            "launch_go_receipt_missing": "test_pack_refusal_codes_keep_standard_receipt_shape",
            "launch_go_receipt_invalid": "test_pack_refusal_codes_keep_standard_receipt_shape",
        }
        self.assertEqual(night_gate.NIGHT_GATE_REASON_CODES, set(coverage))
        methods = dir(type(self))
        for code, method_name in coverage.items():
            with self.subTest(code=code):
                self.assertIn(method_name, methods)

    def test_driver_codes_are_registered_here_but_never_emitted_by_the_gate(self) -> None:
        self.assertEqual(
            night_gate.NIGHT_DRIVER_REASON_CODES,
            {
                "night_calibration_refused",
                "night_refused_bind_expired",
                "night_aborted_agent_present",
                "night_chain_already_started",
                "night_chain_alive",
                "night_chain_launch_failed",
                "night_courier_running",
                "night_courier_unavailable",
                "night_plan_overruns_deadman",
                "night_record_exists",
                "night_window_exceeded",
            },
        )
        self.assertEqual(night_gate.NIGHT_DRIVER_REASON_CODES & night_gate.NIGHT_GATE_REASON_CODES, {"night_refused_bind_expired"})
        source = inspect.getsource(night_gate)
        body = source.split("NIGHT_DRIVER_REASON_CODES = frozenset(", 1)[1].split("\n)\n", 1)[1]
        for code in night_gate.NIGHT_DRIVER_REASON_CODES - {"night_refused_bind_expired"}:
            self.assertNotIn(f'"{code}"', body, code)

    def test_bind_expiry_code_is_v3_only(self):
        source = FakeProbeSource()
        receipt = json.loads(night_gate.evaluate_night(make_plan(), source.probes()).to_json_bytes())
        receipt['verdict'] = 'REFUSED'
        receipt['refusal'] = dict(reason='night_refused_bind_expired', detail='bind expired', evidence=[])
        self.assertIn('refusal.reason: is not registered', night_gate.validate_receipt(receipt))

    def test_valid_v3_pack_without_driver_arguments_lifts_unbuilt_fence(self):
        plan = make_plan("TRANSACTION_PACK", pack_night={
            "pack_id": "pack-test", "pack_root": "/fixture/pack-test",
            "pack_sha256": "a" * 64, "attempt_ordinal": 1,
            "authorization_record": {"path": "/custody/auth.json", "sha256": "b" * 64},
            "confirmation_record": {"path": "/custody/confirm.json", "sha256": "c" * 64},
        })
        parsed = night_gate.NightPlan.from_mapping(night_plan_mapping(plan))
        receipt = night_gate.evaluate_night(parsed, FakeProbeSource().probes())
        self.assertEqual("REFUSED", receipt.verdict)
        self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
        self.assertIn("custody_root", receipt.refusal.detail)
        self.assertEqual("FAIL", receipt.conditions[0].status)
        self.assertEqual("FAIL", receipt.conditions[1].status)

    def test_pack_import_failure_refuses_instead_of_crashing(self):
        plan = make_plan("TRANSACTION_PACK", pack_night={
            "pack_id": "pack-test", "pack_root": "/fixture/pack-test",
            "pack_sha256": "a" * 64, "attempt_ordinal": 1,
            "authorization_record": {"path": "/custody/auth.json", "sha256": "b" * 64},
            "confirmation_record": {"path": "/custody/confirm.json", "sha256": "c" * 64},
        })
        for error in (ImportError("dependency unavailable"), ModuleNotFoundError("dependency missing")):
            with self.subTest(error=type(error).__name__), mock.patch.object(
                    night_gate, "_evaluate_pack_conditions", side_effect=error):
                receipt = night_gate.evaluate_night(plan, FakeProbeSource().probes())
            self.assertEqual("REFUSED", receipt.verdict)
            self.assertEqual("launch_go_receipt_invalid", receipt.refusal.reason)
            self.assertIn(str(error), receipt.refusal.detail)
            self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

    def test_pack_refusal_codes_keep_standard_receipt_shape(self):
        from scripts.run_night import _pack_refused_receipt, PackNightRefusal
        from dataclasses import replace
        plan = make_plan("TRANSACTION_PACK")
        for missing in (False, True):
            error = PackNightRefusal("pack_root", missing=missing)
            receipt = _pack_refused_receipt(plan, error, FakeProbeSource().probes())
            self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))
            self.assertEqual(error.reason, receipt.refusal.reason)

    def test_every_reason_registry_member_has_the_night_prefix(self) -> None:
        for registry in (
            night_gate.NIGHT_GATE_REASON_CODES,
            night_gate.NIGHT_DRIVER_REASON_CODES,
        ):
            self.assertTrue(all(code.startswith("night_") or code in {"launch_go_receipt_missing", "launch_go_receipt_invalid"} for code in registry))


if __name__ == "__main__":
    unittest.main()


class QuietGatePhaseTests(unittest.TestCase):
    def test_v4_failed_or_empty_boot_probe_is_probe_error(self):
        from dataclasses import replace
        from tests.test_quiet_admission import POLICY
        plan = replace(make_plan(), window_max_s=9600, quiet_admission=dict(POLICY))
        for code, stdout in ((2, ''), (2, BOOT_UUID), (0, ''), (0, '  \n')):
            with self.subTest(code=code, stdout=stdout):
                source = FakeProbeSource()
                with mock.patch.object(night_gate, 'D166_REGISTRATION_SHA256',
                                       hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()):
                    static = night_gate.evaluate_static(plan, source.probes())
                self.assertIsNone(static.refusal)
                source.results[night_gate.BOOT_SESSION_ARGV] = result(
                    night_gate.BOOT_SESSION_ARGV, exit_code=code, stdout=stdout, stderr='fixture probe failure')
                receipt = night_gate.evaluate_dynamic_hard(plan, source.probes(), static)
                self.assertEqual(receipt.refusal.reason, 'night_probe_error')

    def test_v2_receipt_bytes_and_validation_match_original_legacy_scenarios(self):
        """Compare the actual pre-v4 evaluator, including pack-class refusals."""
        import dataclasses
        import subprocess
        import sys
        import types
        baseline = types.ModuleType('night_gate_pre_v4_regression')
        baseline.__file__ = night_gate.__file__
        sys.modules[baseline.__name__] = baseline
        self.addCleanup(sys.modules.pop, baseline.__name__)
        raw = subprocess.check_output(['git', 'show', 'a90ab4e8:joulewise/night_gate.py'],
                                      cwd=Path(__file__).resolve().parents[1], text=True)
        exec(raw, baseline.__dict__)
        # CENSUS-SELF-MATCH-01 deliberately changes the probe argv. Compare
        # receipt/refusal semantics with that one input aligned in both engines.
        baseline.AGENT_CENSUS_ARGV = night_gate.AGENT_CENSUS_ARGV
        scenarios = [(None, None, 1005),
            (night_gate.LOAD_AVG_ARGV, '{ 3.70 1.00 1.00 }', 1005),
            (night_gate.PMSET_BATT_ARGV, "Now drawing from 'Battery Power'", 1005),
            (night_gate.HID_IDLE_ARGV, '10', 1005),
            (night_gate.THERMAL_ARGV, 'CPU_Speed_Limit = 80', 1005),
            (night_gate.BOOT_SESSION_ARGV, 'bad boot', 1005),
            (night_gate.AGENT_CENSUS_ARGV, '42 agent', 1005),
            (None, None, 1061)]
        for receipt_class in night_gate.RECEIPT_CLASSES:
            for argv, stdout, now in scenarios:
                with self.subTest(receipt_class=receipt_class, argv=argv, now=now):
                    receipts = []
                    for engine in (baseline, night_gate):
                        source = FakeProbeSource(now_epoch_s=now)
                        if argv:
                            source.results[argv] = result(argv, stdout=stdout)
                        source.results = {key: engine.ProbeResult(**dataclasses.asdict(value))
                                          for key, value in source.results.items()}
                        with mock.patch.object(engine, 'D166_REGISTRATION_SHA256',
                                               hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()):
                            receipt = engine.evaluate_night(make_plan(receipt_class), source.probes())
                        receipts.append(receipt.to_json_bytes())
                    # Record 46a R2: admission C1 gains only the ruled metadata.
                    current = json.loads(receipts[1])
                    for row in current["conditions"]:
                        if row["condition_id"] == "C1":
                            row["measured"].pop("registration_label", None)
                            row["measured"].pop("registration_ruling", None)
                    self.assertEqual(json.loads(receipts[0]), current)
                    value = json.loads(receipts[0])
                    self.assertEqual(baseline.validate_receipt(value), night_gate.validate_receipt(value))
                    self.assertEqual(set(value), baseline._RECEIPT_KEYS)

        for code, stdout in ((2, ''), (2, BOOT_UUID), (0, '')):
            receipts = []
            for engine in (baseline, night_gate):
                source = FakeProbeSource()
                source.results[night_gate.BOOT_SESSION_ARGV] = result(
                    night_gate.BOOT_SESSION_ARGV, exit_code=code, stdout=stdout)
                source.results = {key: engine.ProbeResult(**dataclasses.asdict(value))
                                  for key, value in source.results.items()}
                receipt = engine.evaluate_night(make_plan(), source.probes())
                self.assertEqual(receipt.refusal.reason, 'night_refused_boot_clock')
                receipts.append(receipt.to_json_bytes())
            self.assertEqual(*receipts)

    def test_static_and_dynamic_seams_cannot_authorize_v4_without_intervals(self):
        from dataclasses import replace
        from tests.test_quiet_admission import POLICY
        plan = replace(make_plan(), window_max_s=9600, quiet_admission=dict(POLICY))
        source = FakeProbeSource()
        with mock.patch.object(night_gate, 'D166_REGISTRATION_SHA256',
                               hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()):
            static = night_gate.evaluate_static(plan, source.probes())
            self.assertIsNone(static.refusal)
            self.assertNotEqual(static.verdict, 'GO')
            self.assertEqual(source.run_calls, [])
            hard = night_gate.evaluate_dynamic_hard(plan, source.probes(), static)
            self.assertIsNone(hard.refusal)
            self.assertNotIn(night_gate.LOAD_AVG_ARGV, source.run_calls)
            self.assertEqual(hard.verdict, 'PENDING')
            self.assertTrue(night_gate.validate_receipt(json.loads(hard.to_json_bytes())))
            with self.assertRaises(night_gate.PlanError):
                night_gate.evaluate_night(plan, source.probes())

    def test_v4_missing_block_never_falls_back_to_legacy(self):
        mapping = plan_mapping()
        mapping.update(schema=night_gate.QUIET_PLAN_SCHEMA, schema_version=4)
        with self.assertRaises(night_gate.PlanError):
            night_gate.NightPlan.from_mapping(mapping)


class EvidenceRegistrationTests(unittest.TestCase):
    def test_ruled_registration_serialization_requires_dated_ruling_amendment(self):
        # 2026-09-19: record 61a S1/S4 + 56x R2 re-pin the frozen pilot.
        # 2026-09-19 (re-audit 64 R1): each entry now names its tracked records.
        # Any membership/metadata amendment needs its cold-gate ruling and a
        # dated update here.
        serialized = json.dumps(night_gate.RULED_REGISTRATIONS, sort_keys=True, separators=(',', ':'))
        self.assertEqual(hashlib.sha256(serialized.encode()).hexdigest(),
                         '81c6a189845394a089641d9582e7c278890b9f5afb39b4250addfdfdafb5e5e1')

    def test_every_ruled_registration_names_tracked_records_that_exist(self):
        # Ruling 61a S4: prose authority is not enough; each entry's records
        # must be tracked files, and a decision-log anchor must be a heading.
        root = Path(__file__).resolve().parents[1]
        for sha, entry in night_gate.RULED_REGISTRATIONS.items():
            with self.subTest(registration=entry['label']):
                self.assertEqual(set(entry), {'label', 'ruling', 'binds_chain', 'records'})
                self.assertTrue(entry['records'], 'an entry without records is prose-only authority')
                for ref in entry['records']:
                    path, _, anchor = ref.partition('#')
                    self.assertFalse(Path(path).is_absolute(), ref)
                    self.assertTrue((root / path).is_file(), ref)
                    if anchor:
                        headings = [line for line in (root / path).read_text().splitlines()
                                    if line.startswith('## ' + anchor + ':')]
                        self.assertTrue(headings, ref)

    def test_unavailable_chain_source_is_probe_error_not_digest_mismatch(self):
        source = self.source()
        argv = next(argv for argv in source.results if len(argv) > 4 and argv[0] == '/usr/bin/git' and argv[3] == 'show')
        source.results[argv] = result(argv, exit_code=1, stderr='fixture unavailable')
        receipt = night_gate.evaluate_night(make_plan(), source.probes())
        self.assertEqual(receipt.refusal.reason, 'night_probe_error')

    def source(self, registration=None, wrapper_extra=""):
        root = Path(__file__).resolve().parents[1]
        chain = (root / night_gate.EVIDENCE_CHAIN_PATH).read_text()
        sha = hashlib.sha256(chain.encode()).hexdigest()
        wrapper = "export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\nexport EVIDENCE_CHAIN_SOURCE_SHA256='" + sha + "'\n" + wrapper_extra
        source = FakeProbeSource(chain_text=wrapper, registration_text=registration or
            (root / night_gate.QPE01_PILOT_REGISTRATION_PATH).read_text())
        plan = make_plan()
        argv = ("/usr/bin/git", "-C", plan.measurement_root, "show", f"{plan.measurement_head}:{night_gate.EVIDENCE_CHAIN_PATH}")
        source.results[argv] = result(argv, stdout=chain)
        source.text[str(Path(plan.measurement_root) / night_gate.EVIDENCE_CHAIN_PATH)] = chain
        return source

    def test_evidence_registration_is_relative_to_measurement_root_from_tmp(self):
        import os
        import subprocess
        from dataclasses import replace
        from tests.test_gen_evidence_night import EvidenceFixture
        from scripts import gen_evidence_night
        fixture = EvidenceFixture()
        self.addCleanup(fixture.close)
        gen_evidence_night.generate(fixture.plan_path)
        source = FakeProbeSource(checkout_head=fixture.head, measurement_head=fixture.head)
        def run(argv):
            if argv[0] == "/usr/bin/git":
                completed = subprocess.run(argv, capture_output=True, text=True)
                return result(argv, exit_code=completed.returncode,
                              stdout=completed.stdout, stderr=completed.stderr)
            return source.run(argv)
        probes = replace(source.probes(), run=run, read_text=lambda path: Path(path).read_text())
        previous = os.getcwd()
        try:
            os.chdir("/tmp")
            receipt = night_gate.evaluate_night(fixture.plan, probes)
        finally:
            os.chdir(previous)
        self.assertEqual(receipt.verdict, "GO", receipt.refusal)

    def test_protocol_digest_and_source_are_the_ruled_files(self):
        source = self.source()
        self.assertEqual(hashlib.sha256(source.text['/custody/registration.json'].encode()).hexdigest(), night_gate.QPE01_PILOT_REGISTRATION_SHA256)
        self.assertIn(night_gate.QPE01_PILOT_REGISTRATION_SHA256, night_gate.RULED_REGISTRATIONS)
        receipt = night_gate.evaluate_night(make_plan(), source.probes())
        self.assertEqual(receipt.verdict, "GO")
        c1 = next(row for row in receipt.conditions if row.condition_id == "C1").measured
        c5 = next(row for row in receipt.conditions if row.condition_id == "C5").measured
        self.assertEqual(c1['registration_bound_chain_source_sha256'], c5['chain_source_sha256'])
        self.assertEqual(c1['registration_ruling'], 'cold gate 10 Q1/Q2 (2026-09-19); sizing ruling 46b')
        self.assertNotIn('D-166', c1['detail'])

    def test_chain_measurement_not_advisory_sidecar_is_binding(self):
        source = self.source()
        source.text[str(Path(make_plan().measurement_root) / night_gate.EVIDENCE_CHAIN_PATH)] += '# altered\n'
        receipt = night_gate.evaluate_night(make_plan(), source.probes())
        self.assertEqual(receipt.refusal.reason, 'night_chain_digest_mismatch')
        self.assertNotIn('/custody/registration.json', source.read_calls)

    def test_evidence_cannot_borrow_d166_and_calibration_cannot_borrow_pilot(self):
        source = self.source(registration=REGISTRATION_TEXT)
        receipt = night_gate.evaluate_night(make_plan(), source.probes())
        self.assertEqual(receipt.refusal.reason, 'night_refused_registration')
        source = FakeProbeSource(registration_text=self.source().text['/custody/registration.json'])
        receipt = night_gate.evaluate_night(make_plan(), source.probes())
        self.assertEqual(receipt.refusal.reason, 'night_refused_registration')

    def test_missing_malformed_or_wrong_chain_binding_refuses(self):
        for registration in ('{}', '[]', '{bad', '{"chain_source_sha256":"' + '0'*64 + '"}'):
            source = self.source(registration=registration)
            sha = hashlib.sha256(registration.encode()).hexdigest()
            entry = night_gate.RULED_REGISTRATIONS[night_gate.QPE01_PILOT_REGISTRATION_SHA256]
            with mock.patch.dict(night_gate.RULED_REGISTRATIONS, {sha: entry}):
                receipt = night_gate.evaluate_night(make_plan(), source.probes())
            self.assertEqual(receipt.refusal.reason, 'night_refused_registration')

    def test_payload_ambiguity_and_unknown_literal_refuse(self):
        for extra in ('export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n', "export CALIBRATION_LEDGER='/tmp/ledger'\n"):
            source = self.source(wrapper_extra=extra)
            receipt = night_gate.evaluate_night(make_plan(), source.probes())
            self.assertEqual(receipt.refusal.reason, 'night_chain_digest_mismatch')
            self.assertIn('probe payload kind ambiguous', receipt.refusal.detail)
        with self.assertRaisesRegex(ValueError, 'probe payload kind ambiguous'):
            night_gate.probe_payload_kind('export NIGHT_PAYLOAD_KIND=unknown\n')

    def test_cold_gate_document_clauses_and_evidence_probe_amendment_are_present(self):
        root = Path(__file__).resolve().parents[1]
        handback = ' '.join((root/'docs/process/NIGHT_HANDBACK.md').read_text().split())
        runbook = ' '.join((root/'docs/phase_2/derivation_night_runbook.md').read_text().split())
        courier = ' '.join((root/'docs/process/NIGHT_COURIER_PROMPT.md').read_text().split())
        for clause in ('The ruled-registration table in `night_gate.py` is amended only by cold-gate ruling; each entry names its ruling and the tracked records that hold it (`records`; a test asserts each exists).',
                       '`probe receipt kind does not match payload kind`', '`probe payload kind ambiguous`',
                       'sealed manifest, harness and registration digests',
                       '`joulewise.night_evidence_probe_receipt.v1`'):
            self.assertIn(clause, handback)
        self.assertIn('| Evidence verify-only probe receipt |', runbook)
        self.assertIn('It never starts `collect`, `load` or power sampling.', runbook)
        self.assertIn('You have no scientific decision authority', courier)
        self.assertIn('night/evidence_busy_cores.jsonl', courier)
