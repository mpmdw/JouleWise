"""Acceptance contract for the fixture-only transfer-result renderer.

The values in ``tests/fixtures/results_fill_transfer`` are synthetic protocol
arithmetic.  They are not measurements and cannot issue a paper claim.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from joulewise.results_fill_transfer import (
    RESULT_SCHEMA_VERSION,
    STOP_FILL,
    TRANSFER_FIDUCIAL_RESULT_SITES,
    TRANSFER_FIDUCIAL_RESULT_TOKEN,
    render_transfer_fiducial_result,
    validate_transfer_fiducial_result,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "results_fill_transfer"

FIXTURE_SHA256 = {
    "supported.json": "f528ab7932d7086b333d6d81e514c3a43b1bda48a57f67a08f4ee9b78f0fa8d5",
    "not_supported.json": "f47285a4fb63f3eccfab5fcbd1cd714cff5f4a67d8f50c768be47648f060b0d9",
    "not_evaluated.json": "7170183571e12600edb16799eedb209d0e2bc55400b746819bcf3c6d1c1cc999",
}

EXPECTED_SENTENCES = {
    "supported.json": (
        "Diagnostic only: the largest composed inserted-gap edge-residual bound "
        "was 0.022000 s, no greater than the session pulse-derived timing bound "
        "of 0.030068 s; this supports applying that timing bound to the studied "
        "inference boundary, but it does not mint a floor or license a claim."
    ),
    "not_supported.json": (
        "Diagnostic only: the largest composed inserted-gap edge-residual bound "
        "was 0.031000 s, exceeding the session pulse-derived timing bound of "
        "0.030068 s; this does not support applying that timing bound to the "
        "studied inference boundary and does not mint a floor or license a claim."
    ),
    "not_evaluated.json": (
        "Diagnostic only: the inserted-gap transfer comparison was not evaluated "
        "(issued reasons: source_capture_refused); applying the session "
        "pulse-derived timing bound to the studied inference boundary remains "
        "unestablished."
    ),
}


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _reissue(value: dict) -> bytes:
    """Independently rebuild a fixture-shaped content ID after a mutation."""

    value = copy.deepcopy(value)
    value["result_id"] = ""
    value["result_id"] = "tfr-" + hashlib.sha256(
        _canonical_json_bytes(value)
    ).hexdigest()
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def _render(raw: bytes) -> dict[str, str]:
    return render_transfer_fiducial_result(
        raw,
        expected_result_sha256=hashlib.sha256(raw).hexdigest(),
    )


def _all_stop(rendered: dict[str, str]) -> bool:
    return (
        tuple(rendered) == TRANSFER_FIDUCIAL_RESULT_SITES
        and set(rendered.values()) == {STOP_FILL}
    )


class TransferResultContractTests(unittest.TestCase):
    def test_transfer_result_contract_table(self) -> None:
        self.assertEqual(
            TRANSFER_FIDUCIAL_RESULT_TOKEN,
            "[TRANSFER_FIDUCIAL_RESULT]",
        )
        self.assertEqual(len(TRANSFER_FIDUCIAL_RESULT_SITES), 9)

        issued: dict[str, dict] = {}
        issued_raw: dict[str, bytes] = {}
        for fixture_name, sentence in EXPECTED_SENTENCES.items():
            raw = (FIXTURES / fixture_name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), FIXTURE_SHA256[fixture_name])
            value = json.loads(raw)
            issued[fixture_name] = value
            issued_raw[fixture_name] = raw
            self.assertEqual(value["schema_version"], RESULT_SCHEMA_VERSION)
            self.assertEqual(validate_transfer_fiducial_result(value), [])

            rendered = render_transfer_fiducial_result(
                raw,
                expected_result_sha256=FIXTURE_SHA256[fixture_name],
            )
            self.assertEqual(tuple(rendered), TRANSFER_FIDUCIAL_RESULT_SITES)
            self.assertEqual(list(rendered.values()), [sentence] * 9)
            self.assertEqual(len(set(rendered.values())), 1)

        supported = issued["supported.json"]

        # Raw-byte authentication is mandatory; an expected hash is never
        # inferred from the candidate artifact itself.
        self.assertTrue(
            _all_stop(
                render_transfer_fiducial_result(
                    issued_raw["supported.json"],
                    expected_result_sha256="f" * 64,
                )
            )
        )
        self.assertTrue(
            _all_stop(
                render_transfer_fiducial_result(
                    supported,
                    expected_result_sha256=FIXTURE_SHA256["supported.json"],
                )
            )
        )
        self.assertTrue(
            _all_stop(
                render_transfer_fiducial_result(
                    issued_raw["supported.json"],
                    expected_result_sha256="F" * 64,
                )
            )
        )

        # Every digest and commit binding is covered by the result content ID.
        digest_paths = [
            ("result_id",),
            ("source_capture", "file_sha256"),
            ("source_capture", "source_commit"),
            ("source_capture", "fit_source_commit"),
            ("source_capture", "plan_sha256"),
            ("source_capture", "pre_data_receipt_sha256"),
            ("source_capture", "estimator_source_sha256"),
            (
                "source_capture",
                "pulse_derived_timing_bound_source",
                "artifact_sha256",
            ),
        ]
        for path in digest_paths:
            with self.subTest(mutation="digest", path=path):
                mutated = copy.deepcopy(supported)
                target = mutated
                for key in path[:-1]:
                    target = target[key]
                width = len(target[path[-1]])
                replacement = "0" * width
                if target[path[-1]] == replacement:
                    replacement = "a" * width
                target[path[-1]] = replacement
                self.assertTrue(_all_stop(_render(_canonical_json_bytes(mutated))))

        for index in range(10):
            with self.subTest(mutation="bundle_digest", index=index):
                mutated = copy.deepcopy(supported)
                mutated["source_capture"]["bundle_sha256"][index]["sha256"] = "e" * 64
                self.assertTrue(_all_stop(_render(_canonical_json_bytes(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["source_capture"]["bundle_sha256"].pop()
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        # Census, public maximum, outcome, flags, witness arithmetic, and the
        # b_fiducial_s source binding all bite even after a fresh content ID.
        semantic_mutations = []
        for census_field in (
            "registered_run_count",
            "observed_run_count",
            "registered_edge_count",
            "observed_edge_count",
        ):
            mutated = copy.deepcopy(supported)
            mutated["census"][census_field] -= 1
            semantic_mutations.append((f"census.{census_field}", mutated))

        mutated = copy.deepcopy(supported)
        mutated["census"]["edges_per_run"].reverse()
        semantic_mutations.append(("census.edges_per_run", mutated))

        mutated = copy.deepcopy(supported)
        mutated["largest_composed_edge_residual_bound_s"] = 0.021
        semantic_mutations.append(("largest maximum", mutated))

        mutated = copy.deepcopy(supported)
        mutated["pulse_derived_timing_bound_s"] = -0.0
        semantic_mutations.append(("negative-zero timing bound", mutated))

        mutated = copy.deepcopy(supported)
        mutated["support_outcome"] = "not_supported"
        semantic_mutations.append(("outcome relation", mutated))

        mutated = copy.deepcopy(supported)
        mutated["support_outcome"] = "exceeds_bound"
        semantic_mutations.append(("outcome enum", mutated))

        mutated = copy.deepcopy(supported)
        mutated["diagnostic"] = False
        semantic_mutations.append(("diagnostic flag", mutated))

        mutated = copy.deepcopy(supported)
        mutated["claim_bearing"] = True
        semantic_mutations.append(("claim-bearing flag", mutated))

        mutated = copy.deepcopy(supported)
        mutated["source_capture"]["pulse_derived_timing_bound_source"]["field"] = "b_pulse_s"
        semantic_mutations.append(("b_fiducial_s binding", mutated))

        mutated = copy.deepcopy(supported)
        mutated["largest_inserted_gap_edge"]["fitted_residual_interval_s"]["lower"] = -0.019
        semantic_mutations.append(("raw interval witness", mutated))

        mutated = copy.deepcopy(supported)
        mutated["largest_inserted_gap_edge"]["effective_clock_anchor_bound_s"] = 0.001
        semantic_mutations.append(("anchor addend", mutated))

        mutated = copy.deepcopy(supported)
        mutated["reason_codes"] = ["unregistered_reason"]
        semantic_mutations.append(("reason enum", mutated))

        refusal = issued["not_evaluated.json"]
        mutated = copy.deepcopy(refusal)
        mutated["reason_codes"] = []
        semantic_mutations.append(("refusal reason absent", mutated))

        mutated = copy.deepcopy(refusal)
        mutated["reason_codes"] = [
            "edge_census_incomplete",
            "run_census_incomplete",
        ]
        semantic_mutations.append(("reason order", mutated))

        mutated = copy.deepcopy(refusal)
        mutated["reason_codes"] = [
            "source_capture_refused",
            "source_capture_refused",
        ]
        semantic_mutations.append(("reason uniqueness", mutated))

        mutated = copy.deepcopy(supported)
        mutated["unexpected"] = "not in the closed schema"
        semantic_mutations.append(("closed top-level keys", mutated))

        for label, mutated in semantic_mutations:
            with self.subTest(mutation=label):
                self.assertTrue(_all_stop(_render(_reissue(mutated))))

        # Equality belongs to supported (<=), never not_supported (>).
        equality = copy.deepcopy(supported)
        equality["pulse_derived_timing_bound_s"] = equality[
            "largest_composed_edge_residual_bound_s"
        ]
        equality_raw = _reissue(equality)
        self.assertEqual(
            set(_render(equality_raw).values()),
            {
                "Diagnostic only: the largest composed inserted-gap edge-residual "
                "bound was 0.022000 s, no greater than the session pulse-derived "
                "timing bound of 0.022000 s; this supports applying that timing "
                "bound to the studied inference boundary, but it does not mint a "
                "floor or license a claim."
            },
        )
        equality["support_outcome"] = "not_supported"
        self.assertTrue(_all_stop(_render(_reissue(equality))))

        # Missing, malformed, or unauthenticated inputs never expose a partial
        # site result.
        malformed = [b"", b"{}", b'{"x":NaN}', b'{"x":1,"x":2}']
        for raw in malformed:
            with self.subTest(malformed=raw):
                self.assertTrue(_all_stop(_render(raw)))


if __name__ == "__main__":
    unittest.main()
