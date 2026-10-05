"""Ruling 76 B.2/B.3 regressions through the real author and ARM predicates."""
from decimal import Decimal
from fractions import Fraction
import unittest
from unittest import mock

from joulewise import arm_readiness as arm, arm_readiness_evidence_t0 as author
from joulewise import clock_reference, kernel_clock
from tests.test_kernel_clock import frequency_probe
from tests import test_v5_qualification_plan as sizing_fixture


class Block4ClockTests(unittest.TestCase):
    def derive(self, seconds, *, step_ns=0, word=-207749, author_word=None, stream_max=320):
        frequency = frequency_probe(word)
        end_frequency = frequency_probe(word if author_word is None else author_word)
        r0_raw = 1_000_000_000_000
        span = seconds * 10**9
        end_raw = r0_raw + span
        drift = round(Fraction(word * span, 65536 * 1_000_000))
        offset = 2_000_000_000_000_000_000
        r0 = {"anchor_realtime_ns": offset + r0_raw, "anchor_monotonic_raw_ns": r0_raw,
              "anchor_read_skew_ns": 1000, "batch_finished_monotonic_raw_ns": r0_raw + 10,
              "kernel_frequency": frequency, "t_stream_max_s": stream_max}
        agreement = author._ReferenceAgreement(3, Decimal(".01"), Decimal(".03"))
        fixture = sizing_fixture.PlanWriterTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        # Keep the clock cases' stream budget while replaying real sizing custody.
        fixture.input["sizing"]["streams"] = {
            name: fixture.allow(stream_max) for name in fixture.input["sizing"]["streams"]}
        fixture.write()
        context = author._Context(
            pack_root=fixture.pack, repository=fixture.repo,
            custody_root=fixture.custody, custody_pack_root=fixture.custody / fixture.pack.name,
            tree={}, pack_sha256=fixture.input["pack"]["sha256"],
            plan_sha256=arm.sha256_bytes(fixture.output.read_bytes()),
            head_commit=fixture.head, head_tree_oid="d" * 40, boot_session_id="boot",
            boot_probe=author._ProbeResult(("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"),
                str(fixture.repo), 0, "boot\n", ""),
            captures={"clock-reference": ({"finished_monotonic_ns": 10}, {})},
            clock=author._DerivationClock(lambda: end_raw, lambda: "1970-01-01T00:00:00Z",
                lambda: endpoint))
        disable = {"exit_code": 0, "argv": ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                   "-setusingnetworktime", "off"], "started_monotonic_ns": 20,
                   "finished_monotonic_ns": 30}
        endpoint = clock_reference.ClockAnchor(offset + end_raw + drift + step_ns, end_raw, 1000)
        with (mock.patch.object(author, "_captured_clock_reference", return_value=(r0, {}, agreement)),
              # The miniature writer pack has no registry; every real authoring
              # profile requires this gate, as the registry test below verifies.
              mock.patch.object(arm, "requires_t0_frequency_gate", return_value=True),
              mock.patch.object(author, "_capture", return_value=(disable, {})),
              mock.patch.object(author, "_fresh_clock_reference_batch", return_value=(
                  agreement, (), end_raw - 1000, endpoint, end_raw)),
              mock.patch.object(kernel_clock, "read_kernel_frequency", return_value=end_frequency)):
            row = author._derive_clock_attestation(context)
        receipt = {"boot_session_id": "boot", "valid_until_monotonic_ns": end_raw + 21_600_000_000_000}
        return row.value, receipt

    def test_steady_negative_drift_passes_author_and_arm_at_1600_and_3600_seconds(self):
        for seconds in (1600, 3600):
            with self.subTest(seconds=seconds):
                value, receipt = self.derive(seconds)
                self.assertGreater(value["anchor_delta_ns"], 5_000_000)
                self.assertLess(value["anchor_residual_ns"], 1)
                self.assertEqual(value["anchor_check_version"], kernel_clock.ANCHOR_CHECK_VERSION)
                self.assertTrue(arm._clock_probe_predicate_passes(
                    receipt, value, arm._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))
                live_span = 1200 * 10**9
                drift = round(Fraction(value["kernel_frequency"]["raw_word"] * live_span, 65536 * 10**6))
                live = {"boot_session_id": "boot", "read_skew_ns": 1000,
                        "realtime_ns": value["anchor_realtime_ns"] + live_span + drift,
                        "monotonic_raw_ns": value["anchor_monotonic_raw_ns"] + live_span,
                        "kernel_frequency": value["kernel_frequency"]}
                self.assertTrue(arm._clock_probe_predicate_passes(receipt, value, live))
                live["realtime_ns"] += 6_000_000
                self.assertFalse(arm._clock_probe_predicate_passes(receipt, value, live))

    def test_six_ms_step_at_1000_seconds_keeps_registered_anchor_refusal(self):
        with self.assertRaises(author.T0EvidenceAuthoringError) as caught:
            self.derive(1000, step_ns=6_000_000)
        self.assertEqual(caught.exception.reason_code, "evidence_author_t0_clock_attestation_underivable")
        self.assertEqual(str(caught.exception), "R0-to-author RAW anchor delta exceeds 5000000 ns")

    def test_slew_with_small_offset_has_distinct_frequency_refusal(self):
        with self.assertRaises(author.T0EvidenceAuthoringError) as caught:
            self.derive(1000, step_ns=1000, author_word=-207748)
        self.assertEqual(caught.exception.reason_code, "evidence_author_t0_kernel_frequency_changed")
        value, receipt = self.derive(1600)
        live = {"boot_session_id": "boot", "read_skew_ns": 1000,
                "realtime_ns": value["anchor_realtime_ns"],
                "monotonic_raw_ns": value["anchor_monotonic_raw_ns"],
                "kernel_frequency": frequency_probe(-207748)}
        self.assertFalse(arm._clock_probe_predicate_passes(receipt, value, live))

    def test_arm_recheck_preserves_its_author_origin_and_exact_boundary(self):
        value, receipt = self.derive(1600, step_ns=4_000_000)
        live = {"boot_session_id": "boot", "read_skew_ns": 1000,
                "realtime_ns": value["anchor_realtime_ns"] + 4_999_999,
                "monotonic_raw_ns": value["anchor_monotonic_raw_ns"],
                "kernel_frequency": value["kernel_frequency"]}
        self.assertTrue(arm._clock_probe_predicate_passes(receipt, value, live))
        live["realtime_ns"] += 2
        self.assertFalse(arm._clock_probe_predicate_passes(receipt, value, live))

    def test_twelve_ppm_fails_registered_stream_gate_at_author(self):
        with self.assertRaisesRegex(author.T0EvidenceAuthoringError, "stream clock budget"):
            self.derive(1000, word=12 * 65536)

    def test_twelve_ppm_fails_the_repository_sizing_input_in_both_directions(self):
        import json
        from pathlib import Path
        source = Path(__file__).resolve().parents[1] / "configs/campaigns/v5_qualification_25g83/sizing_allowances.json"
        sizing = json.loads(source.read_bytes())["sizing"]
        stream_max = max(item["seconds"] for item in sizing["streams"].values())
        for word in (-12 * 65536, 12 * 65536):
            with self.subTest(word=word):
                gate = kernel_clock.frequency_gate(frequency_probe(word), stream_max)
                self.assertFalse(gate["passes"])
                self.assertLess(gate["margin_ms"], 0)

    def test_idle_75_sizing_clears_current_frequency_and_checks_inclusive_limit(self):
        import json
        import math
        from pathlib import Path
        source = Path(__file__).resolve().parents[1] / "configs/campaigns/v5_qualification_25g83/sizing_allowances.json"
        adapter = json.loads(source.read_bytes())
        maximum = max(item["seconds"] for item in adapter["sizing"]["streams"].values())
        self.assertEqual(maximum, adapter["totals"]["T_stream_max"]["seconds"])
        self.assertEqual(maximum, 335)
        gate = kernel_clock.frequency_gate(frequency_probe(-207749), maximum)
        self.assertTrue(gate["passes"])
        self.assertAlmostEqual(gate["bound_ms"], 4.84570, places=5)
        self.assertFalse(kernel_clock.frequency_gate(frequency_probe(-207749), 613)["passes"])
        # The raw frequency word is quantized at 1/65536 ppm: last passing
        # word and its immediate successor exercise the actual gate boundary.
        last_word = math.floor((1300 / maximum - 0.25) * 65536)
        for sign in (-1, 1):
            self.assertTrue(kernel_clock.frequency_gate(frequency_probe(sign * last_word), maximum)["passes"])
            self.assertFalse(kernel_clock.frequency_gate(frequency_probe(sign * (last_word + 1)), maximum)["passes"])

    def test_frequency_requirement_follows_every_authoring_registry_profile(self):
        import json
        from pathlib import Path
        registry = json.loads((Path(__file__).resolve().parents[1] /
            "configs/arm_readiness/d117_row_registry_v2.json").read_bytes())
        for profile in registry["plan_profiles"]:
            rows = arm._profile_rows(registry, profile["profile_id"], phase="arm")
            expected = any("CLOCK_ATTESTATION" in row["required_evidence_kinds"] for row in rows)
            with self.subTest(profile=profile["profile_id"]), mock.patch.object(
                    arm, "_registry_reference", return_value=(registry, b"", {"plan_profile": profile["profile_id"]})):
                self.assertEqual(arm.requires_t0_frequency_gate(Path("renamed-pack")), expected)
                self.assertTrue(expected)

    def test_historical_fact_keeps_fixed_semantics_and_unknown_version_refuses(self):
        value, receipt = self.derive(1600)
        legacy = {key: val for key, val in value.items()
                  if key in arm._CLOCK_PROBE_VALUE_KEYS}
        self.assertFalse(arm._clock_probe_predicate_passes(receipt, legacy, arm._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))
        legacy["anchor_realtime_ns"] -= legacy["anchor_realtime_ns"] - legacy["anchor_monotonic_raw_ns"] - (
            legacy["r0_anchor_realtime_ns"] - legacy["r0_anchor_monotonic_raw_ns"])
        legacy["anchor_delta_ns"] = 0
        self.assertTrue(arm._clock_probe_predicate_passes(receipt, legacy, arm._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))
        value["anchor_check_version"] = "unknown"
        self.assertFalse(arm._clock_probe_predicate_passes(receipt, value, arm._PREDICATE_LIVE_ANCHOR_NOT_APPLICABLE))

    def test_historical_live_check_does_not_require_the_new_frequency_probe(self):
        value, receipt = self.derive(1000, word=0)
        legacy = {key: val for key, val in value.items() if key in arm._CLOCK_PROBE_VALUE_KEYS}
        endpoint = clock_reference.ClockAnchor(value["anchor_realtime_ns"],
            value["anchor_monotonic_raw_ns"], 1000)
        with (mock.patch.object(clock_reference, "sample_anchor", return_value=endpoint),
              mock.patch.object(arm, "_current_boot_session_id", return_value="boot"),
              mock.patch.object(kernel_clock, "read_kernel_frequency", side_effect=OSError("read unavailable"))):
            live = arm._sample_live_clock_anchor()
        self.assertEqual(set(live), arm._LIVE_ANCHOR_KEYS)
        self.assertTrue(arm._clock_probe_predicate_passes(receipt, legacy, live))
        self.assertFalse(arm._clock_probe_predicate_passes(receipt, value, live))


if __name__ == "__main__":
    unittest.main()
