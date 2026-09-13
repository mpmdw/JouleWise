# Exhibit E — tests/test_night_gate.py lines 330–410 at 27957b60 (existing agent-census tests)

```python

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
```
