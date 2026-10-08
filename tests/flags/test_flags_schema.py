"""The joulewise.flag.v1 record: identity, validation and canonical bytes."""

from __future__ import annotations

import copy
import json
import unittest

from joulewise.flags.schema import (
    FLAG_SCHEMA,
    FlagSchemaError,
    canonical_json_bytes,
    compute_flag_id,
    make_flag,
    make_interval,
    make_scope,
    make_source,
    now_stamp,
    render_line,
    validate_flag,
)

EMITTED = {"wall_s": 1791249981.5, "monotonic_ns": 123, "boot_session_uuid": "BOOT"}


def sample_flag(**overrides):
    arguments = dict(
        code="battery.member_span",
        family="PHYSICS_IN_SPAN",
        klass="PHYSICS",
        scope=make_scope("member", plan_id="plan-a", attempt=1, stage_id="s1", run_id="r01"),
        source=make_source("harvest", "joulewise.b5.harvest.battery_member_flags"),
        observed={"violations": [{"instant_amperage_ma": -447}]},
        expected={"abs_ma_max": 200},
        evidence=[{"path": "hazards/monitor/battery.jsonl", "sha256": "a" * 64}],
        detail="one in-force publication out of float",
        interval=make_interval(monotonic_ns=(10, 20)),
        emitted=EMITTED,
    )
    arguments.update(overrides)
    return make_flag(**arguments)


class FlagSchemaTests(unittest.TestCase):
    def test_make_flag_conforms_and_carries_every_field(self) -> None:
        flag = sample_flag()
        self.assertEqual(validate_flag(flag), [])
        self.assertEqual(flag["schema_version"], FLAG_SCHEMA)
        self.assertEqual(
            set(flag),
            {"schema_version", "flag_id", "code", "family", "klass", "scope", "interval", "source",
             "observed", "expected", "evidence", "detail", "emitted", "catalog_sha256", "blinding"},
        )
        self.assertEqual(flag["blinding"], "STRUCTURE")

    def test_flag_id_is_sha256_prefix_of_code_scope_observed_source(self) -> None:
        flag = sample_flag()
        payload = {"code": flag["code"], "scope": flag["scope"], "observed": flag["observed"],
                   "source": flag["source"], "interval": flag["interval"]}
        import hashlib

        expected = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()[:20]
        self.assertEqual(flag["flag_id"], expected)
        self.assertEqual(flag["flag_id"], compute_flag_id(flag["code"], flag["scope"], flag["observed"],
                                                          flag["source"], flag["interval"]))

    def test_same_fact_same_id_regardless_of_emission_time_or_detail(self) -> None:
        first = sample_flag()
        second = sample_flag(emitted=now_stamp(), detail="different words", evidence=[])
        self.assertEqual(first["flag_id"], second["flag_id"])
        third = sample_flag(observed={"violations": [{"instant_amperage_ma": -448}]})
        self.assertNotEqual(first["flag_id"], third["flag_id"])

    def test_tampered_flag_id_is_refused(self) -> None:
        flag = sample_flag()
        flag["observed"] = {"violations": []}
        self.assertIn("flag_id does not match canonical(code, scope, observed, source, interval)",
                      "; ".join(validate_flag(flag)))

    def test_malformed_records_are_reported_not_raised_by_validate(self) -> None:
        cases = {
            "code": "Battery Member",
            "family": "NOPE",
            "klass": "MAYBE",
            "blinding": "SECRET",
        }
        for field, value in cases.items():
            flag = sample_flag()
            flag[field] = value
            with self.subTest(field=field):
                self.assertTrue(validate_flag(flag))
        flag = sample_flag()
        flag["scope"] = dict(flag["scope"], level="member", run_id=None)
        self.assertTrue(any("run_id" in problem for problem in validate_flag(flag)))
        flag = sample_flag()
        flag["interval"] = dict(flag["interval"], monotonic_ns=[20, 10])
        self.assertTrue(any("ordered pair" in problem for problem in validate_flag(flag)))
        flag = sample_flag()
        flag["evidence"] = [{"path": "/abs/path", "sha256": "a" * 64}]
        self.assertTrue(any("evidence[0]" in problem for problem in validate_flag(flag)))
        flag = sample_flag()
        flag["extra"] = 1
        self.assertTrue(any("unknown fields" in problem for problem in validate_flag(flag)))
        self.assertEqual(validate_flag([]), ["flag must be a JSON object"])

    def test_make_flag_raises_on_nonfinite_observed(self) -> None:
        with self.assertRaises((FlagSchemaError, ValueError)):
            sample_flag(observed={"x": float("nan")})

    def test_restricted_blinding_is_allowed(self) -> None:
        flag = sample_flag(code="member.anchor_energy_envelope_exceeded", family="MEMBER_VALIDITY",
                           klass="NUMBER", blinding="RESTRICTED")
        self.assertEqual(validate_flag(flag), [])

    def test_detail_is_one_line(self) -> None:
        flag = sample_flag(detail="two\nlines")
        self.assertEqual(flag["detail"], "two lines")

    def test_render_line_is_canonical_and_newline_terminated(self) -> None:
        flag = sample_flag()
        line = render_line(flag)
        self.assertTrue(line.endswith(b"\n"))
        self.assertEqual(json.loads(line), flag)
        shuffled = dict(reversed(list(copy.deepcopy(flag).items())))
        self.assertEqual(render_line(shuffled), line)

    def test_emitted_stamp_has_three_fields(self) -> None:
        stamp = now_stamp()
        self.assertEqual(set(stamp), {"wall_s", "monotonic_ns", "boot_session_uuid"})
        self.assertIsInstance(stamp["monotonic_ns"], int)


if __name__ == "__main__":
    unittest.main()
