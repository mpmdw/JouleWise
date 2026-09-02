from __future__ import annotations

import copy
import hashlib
import inspect
import json
import unittest
from unittest import mock

from joulewise import night_gate


HEAD = "a" * 40
BOOT_UUID = "12345678-1234-5678-9234-567812345678"
CHAIN_TEXT = "#!/bin/zsh\necho night\n"
REGISTRATION_TEXT = '{"registered":true}\n'


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
        chain_text: str = CHAIN_TEXT,
        chain_digest: str | None = None,
        registration_text: str = REGISTRATION_TEXT,
    ) -> None:
        self.results = green_results() if results is None else results
        self.now_value = now_epoch_s
        self.head_value = checkout_head
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

    def probes(self) -> night_gate.Probes:
        return night_gate.Probes(
            run=self.run,
            now_epoch_s=self.now,
            monotonic_ns=self.monotonic,
            read_text=self.read_text,
            checkout_head=self.checkout_head,
        )


def make_plan(receipt_class: str = "DIAGNOSTIC_NO_PACK", **changes: object) -> night_gate.NightPlan:
    values: dict[str, object] = {
        "plan_id": "night-001",
        "receipt_class": receipt_class,
        "t0_epoch_s": 1_000.0,
        "window_max_s": 60,
        "authored_epoch_s": 900.0,
        "repo_head": HEAD,
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
    plan = make_plan(receipt_class)
    return {
        "schema": night_gate.PLAN_SCHEMA,
        "plan_id": plan.plan_id,
        "receipt_class": plan.receipt_class,
        "t0_epoch_s": plan.t0_epoch_s,
        "window_max_s": plan.window_max_s,
        "authored_epoch_s": plan.authored_epoch_s,
        "repo_head": plan.repo_head,
        "chain_path": plan.chain_path,
        "chain_sha256_path": plan.chain_sha256_path,
        "custody_root": plan.custody_root,
        "registration_path": plan.registration_path,
    }


class NightGateTests(unittest.TestCase):
    def evaluate(
        self, plan: night_gate.NightPlan, source: FakeProbeSource
    ) -> night_gate.Receipt:
        registration_hash = hashlib.sha256(REGISTRATION_TEXT.encode("utf-8")).hexdigest()
        with mock.patch.object(
            night_gate, "D166_REGISTRATION_SHA256", registration_hash
        ):
            return night_gate.evaluate_night(plan, source.probes())

    def test_production_argv_constants_match_the_t0_author_literals(self) -> None:
        self.assertEqual(
            ("/usr/bin/pgrep", "-lf", "codex|claude|t3"),
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

    def test_d166_registration_digest_is_the_ruled_literal(self) -> None:
        self.assertEqual(
            "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b",
            night_gate.D166_REGISTRATION_SHA256,
        )

    def test_an_exit_one_census_with_only_whitespace_is_clean(self) -> None:
        source = FakeProbeSource()
        source.results[night_gate.AGENT_CENSUS_ARGV] = result(
            night_gate.AGENT_CENSUS_ARGV, exit_code=1, stdout=" \n\t"
        )
        observed, refusal = night_gate.agent_census(source.probes())
        self.assertEqual(1, observed.exit_code)
        self.assertIsNone(refusal)

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
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

    def test_a_fully_green_rehearsal_can_never_yield_go(self) -> None:
        receipt = self.evaluate(make_plan("REHEARSAL_STUB"), FakeProbeSource())
        self.assertEqual("REHEARSAL_ONLY", receipt.verdict)
        self.assertTrue(all(row.status == "PASS" for row in receipt.conditions if row.condition_id != "C2"))
        self.assertEqual([], night_gate.validate_receipt(json.loads(receipt.to_json_bytes())))

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

    def test_wrong_checkout_head_is_stale_and_the_36_hour_boundary_is_current(self) -> None:
        wrong_head = FakeProbeSource(checkout_head="b" * 40)
        receipt = self.evaluate(make_plan(), wrong_head)
        self.assertEqual("night_plan_stale", receipt.refusal.reason)
        self.assertEqual([], wrong_head.run_calls)

        boundary = FakeProbeSource()
        receipt = self.evaluate(
            make_plan(authored_epoch_s=boundary.now_value - night_gate.PLAN_MAX_AGE_S),
            boundary,
        )
        self.assertEqual("GO", receipt.verdict)

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
            "night_refused_hid_idle",
            "night_refused_boot_clock",
            "night_refused_registration",
            "night_window_expired",
            "night_plan_stale",
            "night_plan_malformed",
            "night_chain_digest_mismatch",
            "night_refused_class_unbuilt",
            "night_receipt_class_invalid",
            "night_probe_error",
        }
        self.assertEqual(night_gate.NIGHT_GATE_REASON_CODES, expected)
        coverage = {
            "night_refused_agent_present": "test_a_census_that_finds_lines_refuses_and_preserves_them",
            "night_refused_not_quiet": "test_each_quiet_predicate_fails_closed_with_its_name_in_detail",
            "night_refused_hid_idle": "test_hid_idle_requires_the_exact_zero_value",
            "night_refused_boot_clock": "test_boot_clock_uses_a_canonical_uuid_and_never_invokes_sntp",
            "night_refused_registration": "test_a_wrong_registration_hash_refuses_after_every_machine_gate",
            "night_window_expired": "test_window_refusal_performs_no_command_or_file_or_head_probe",
            "night_plan_stale": "test_wrong_checkout_head_is_stale_and_the_36_hour_boundary_is_current",
            "night_plan_malformed": "test_a_direct_plan_with_missing_registration_is_refused_as_malformed",
            "night_chain_digest_mismatch": "test_chain_sidecar_refuses_case_name_and_token_count_defects",
            "night_refused_class_unbuilt": "test_a_transaction_plan_is_refused_until_stage_three_exists",
            "night_receipt_class_invalid": "test_c2_pass_or_an_unregistered_basis_is_a_class_invalid_defect",
            "night_probe_error": "test_any_probe_exception_refuses_before_later_commands_run",
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
                "night_aborted_agent_present",
                "night_chain_already_started",
                "night_chain_alive",
                "night_chain_launch_failed",
                "night_courier_running",
                "night_courier_unavailable",
                "night_plan_overruns_deadman",
                "night_record_exists",
            },
        )
        self.assertFalse(night_gate.NIGHT_DRIVER_REASON_CODES & night_gate.NIGHT_GATE_REASON_CODES)
        source = inspect.getsource(night_gate)
        body = source.split("NIGHT_DRIVER_REASON_CODES = frozenset(", 1)[1].split("\n)\n", 1)[1]
        for code in night_gate.NIGHT_DRIVER_REASON_CODES:
            self.assertNotIn(f'"{code}"', body, code)

    def test_every_reason_registry_member_has_the_night_prefix(self) -> None:
        for registry in (
            night_gate.NIGHT_GATE_REASON_CODES,
            night_gate.NIGHT_DRIVER_REASON_CODES,
        ):
            self.assertTrue(all(code.startswith("night_") for code in registry))


if __name__ == "__main__":
    unittest.main()
