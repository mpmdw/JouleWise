"""Acceptance contract for the fixture-only transfer-result renderer.

The values in ``tests/fixtures/results_fill_transfer`` are synthetic protocol
arithmetic.  They are not measurements and cannot issue a paper claim.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from joulewise.results_fill_transfer import (
    ESTIMATOR_REVISION,
    ESTIMATOR_SOURCE_SHA256,
    REASON_CODE_ORDER,
    RESULT_SCHEMA_VERSION,
    STOP_FILL,
    TRANSFER_FIDUCIAL_RESULT_SITES,
    TRANSFER_FIDUCIAL_RESULT_TOKEN,
    render_transfer_fiducial_result,
    validate_transfer_fiducial_result,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "results_fill_transfer"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILL_REGISTRY = PROJECT_ROOT / "docs" / "paper" / "results-fill-registry.md"
ESTIMATOR_SOURCE = PROJECT_ROOT / "joulewise" / "powermetrics_fiducial.py"

FIXTURE_SHA256 = {
    "supported.json": "46fc110986a43f68cb815d427c558c1b08b3c3e664bf560ded0b60206c7f037f",
    "not_supported.json": "586fd7b4c24bb5609bb71364a4af7555008d044ce8f7761348e70a657b609335",
    "not_evaluated.json": "c073dc0abb0af10f37a142206e1883be2ed01326cbbfc24c7939e79e52dc2edb",
}

_REGISTERED_SENTENCE_RE = re.compile(
    r"Render exactly: `supported` — `(?P<supported>Diagnostic only:[^`]+)`; "
    r"`not_supported` — `(?P<not_supported>Diagnostic only:[^`]+)`; "
    r"`not_evaluated` — `(?P<not_evaluated>Diagnostic only:[^`]+)` "
    r"One selected sentence"
)


def _registered_tr01_sentences() -> dict[str, str]:
    rows = [
        line
        for line in RESULTS_FILL_REGISTRY.read_text(encoding="utf-8").splitlines()
        if line.startswith("| TR-01 —")
    ]
    if len(rows) != 1:
        raise AssertionError("results-fill registry must contain exactly one TR-01 row")
    match = _REGISTERED_SENTENCE_RE.search(rows[0])
    if match is None:
        raise AssertionError("TR-01 row does not contain all three registered sentences")
    return match.groupdict()


def _registered_sentence(value: dict) -> str:
    template = _registered_tr01_sentences()[value["support_outcome"]]
    if value["support_outcome"] == "not_evaluated":
        return template.replace(
            "<semicolon-joined reason_codes>",
            ";".join(value["reason_codes"]),
        )
    return template.replace(
        "<R>",
        format(value["largest_composed_edge_residual_bound_s"], ".6f"),
    ).replace(
        "<B>",
        format(value["pulse_derived_timing_bound_s"], ".6f"),
    )


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
        self.assertEqual(
            REASON_CODE_ORDER,
            (
                "source_capture_refused",
                "run_census_incomplete",
                "edge_census_incomplete",
                "pulse_derived_timing_bound_unavailable",
            ),
        )
        self.assertEqual(
            hashlib.sha256(ESTIMATOR_SOURCE.read_bytes()).hexdigest(),
            ESTIMATOR_SOURCE_SHA256,
        )

        issued: dict[str, dict] = {}
        issued_raw: dict[str, bytes] = {}
        for fixture_name in FIXTURE_SHA256:
            raw = (FIXTURES / fixture_name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), FIXTURE_SHA256[fixture_name])
            value = json.loads(raw)
            issued[fixture_name] = value
            issued_raw[fixture_name] = raw
            self.assertEqual(value["schema_version"], RESULT_SCHEMA_VERSION)
            self.assertEqual(validate_transfer_fiducial_result(value), [])
            if value["source_capture"] is not None:
                self.assertEqual(
                    value["source_capture"]["estimator_revision"],
                    ESTIMATOR_REVISION,
                )
                self.assertEqual(
                    value["source_capture"]["estimator_source_sha256"],
                    ESTIMATOR_SOURCE_SHA256,
                )
                self.assertEqual(
                    len(value["edge_records"]),
                    value["census"]["observed_edge_count"],
                )

            rendered = render_transfer_fiducial_result(
                raw,
                expected_result_sha256=FIXTURE_SHA256[fixture_name],
            )
            self.assertEqual(tuple(rendered), TRANSFER_FIDUCIAL_RESULT_SITES)
            sentence = _registered_sentence(value)
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

        # A freshly content-addressed projection cannot change the registered
        # existing estimator revision or its source bytes.
        mutated = copy.deepcopy(supported)
        mutated["source_capture"]["estimator_revision"] = "arbitrary_changed_estimator.v99"
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["source_capture"]["estimator_source_sha256"] = "0" * 64
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        # The authenticated twenty-edge inventory, not the selected witness,
        # proves the unrounded global maximum and deterministic tie-break.
        mutated = copy.deepcopy(supported)
        mutated["edge_records"][-1]["fitted_residual_interval_s"] = {
            "lower": -0.498,
            "upper": 0.1,
        }
        mutated["edge_records"][-1]["composed_absolute_residual_bound_s"] = 0.5
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        # Interval ordering is exact even when distinct JSON integers alias as
        # binary floats above 2^53.
        mutated = copy.deepcopy(supported)
        mutated["edge_records"][-1].update(
            fitted_residual_interval_s={
                "lower": 9007199254740993,
                "upper": 9007199254740992,
            },
            effective_clock_anchor_bound_s=0,
            composed_absolute_residual_bound_s=9007199254740993,
        )
        mutated["largest_inserted_gap_edge"] = copy.deepcopy(
            mutated["edge_records"][-1]
        )
        mutated["largest_composed_edge_residual_bound_s"] = 9007199254740993
        mutated["support_outcome"] = "not_supported"
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["edge_records"][0]["composed_absolute_residual_bound_s"] = 0.013
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["largest_inserted_gap_edge"] = copy.deepcopy(mutated["edge_records"][-1])
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["edge_records"].pop()
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["edge_records"][-1] = copy.deepcopy(mutated["edge_records"][-2])
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        mutated = copy.deepcopy(supported)
        mutated["edge_records"][0], mutated["edge_records"][1] = (
            mutated["edge_records"][1],
            mutated["edge_records"][0],
        )
        self.assertTrue(_all_stop(_render(_reissue(mutated))))

        bundle_tie = copy.deepcopy(supported)
        bundle_tie["edge_records"][18].update(
            fitted_residual_interval_s={"lower": -0.02, "upper": 0.018},
            effective_clock_anchor_bound_s=0.002,
            composed_absolute_residual_bound_s=0.022,
        )
        self.assertFalse(_all_stop(_render(_reissue(bundle_tie))))
        bundle_tie["largest_inserted_gap_edge"] = copy.deepcopy(
            bundle_tie["edge_records"][18]
        )
        self.assertTrue(_all_stop(_render(_reissue(bundle_tie))))

        edge_tie = copy.deepcopy(supported)
        edge_tie["edge_records"][7].update(
            fitted_residual_interval_s={"lower": -0.02, "upper": 0.018},
            effective_clock_anchor_bound_s=0.002,
            composed_absolute_residual_bound_s=0.022,
        )
        self.assertFalse(_all_stop(_render(_reissue(edge_tie))))
        edge_tie["largest_inserted_gap_edge"] = copy.deepcopy(
            edge_tie["edge_records"][7]
        )
        self.assertTrue(_all_stop(_render(_reissue(edge_tie))))

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
        mutated["largest_inserted_gap_edge"]["composed_absolute_residual_bound_s"] = 0.021
        semantic_mutations.append(("selected composed bound", mutated))

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

        # Coverage refusals must agree with authenticated observed counts and
        # nullable global-comparison evidence.
        false_complete = copy.deepcopy(supported)
        false_complete.update(
            largest_composed_edge_residual_bound_s=None,
            largest_inserted_gap_edge=None,
            support_outcome="not_evaluated",
            reason_codes=["run_census_incomplete"],
        )
        self.assertTrue(_all_stop(_render(_reissue(false_complete))))

        truthful_run_incomplete = issued["not_evaluated.json"]
        self.assertEqual(
            truthful_run_incomplete["census"]["observed_run_count"], 9
        )
        self.assertEqual(
            truthful_run_incomplete["census"]["observed_edge_count"], 18
        )
        self.assertFalse(_all_stop(_render(issued_raw["not_evaluated.json"])))

        truthful_edge_incomplete = copy.deepcopy(supported)
        truthful_edge_incomplete["edge_records"].pop()
        truthful_edge_incomplete["census"]["observed_edge_count"] = 19
        truthful_edge_incomplete.update(
            largest_composed_edge_residual_bound_s=None,
            largest_inserted_gap_edge=None,
            support_outcome="not_evaluated",
            reason_codes=["edge_census_incomplete"],
        )
        self.assertEqual(
            validate_transfer_fiducial_result(
                json.loads(_reissue(truthful_edge_incomplete))
            ),
            [],
        )
        self.assertFalse(_all_stop(_render(_reissue(truthful_edge_incomplete))))

        two_shortfalls = copy.deepcopy(truthful_run_incomplete)
        two_shortfalls["edge_records"].pop()
        two_shortfalls["census"]["observed_edge_count"] = 17
        self.assertTrue(_all_stop(_render(_reissue(two_shortfalls))))
        two_shortfalls["reason_codes"] = [
            "run_census_incomplete",
            "edge_census_incomplete",
        ]
        self.assertFalse(_all_stop(_render(_reissue(two_shortfalls))))

        pulse_unavailable = copy.deepcopy(supported)
        pulse_unavailable.update(
            pulse_derived_timing_bound_s=None,
            support_outcome="not_evaluated",
            reason_codes=["pulse_derived_timing_bound_unavailable"],
        )
        self.assertFalse(_all_stop(_render(_reissue(pulse_unavailable))))

        source_refused = copy.deepcopy(supported)
        source_refused.update(
            source_capture=None,
            edge_records=[],
            largest_composed_edge_residual_bound_s=None,
            largest_inserted_gap_edge=None,
            pulse_derived_timing_bound_s=None,
            support_outcome="not_evaluated",
            reason_codes=["source_capture_refused"],
        )
        source_refused["census"]["observed_run_count"] = 0
        source_refused["census"]["observed_edge_count"] = 0
        self.assertFalse(_all_stop(_render(_reissue(source_refused))))

        # Equality belongs to supported (<=), never not_supported (>).
        equality = copy.deepcopy(supported)
        equality["pulse_derived_timing_bound_s"] = equality[
            "largest_composed_edge_residual_bound_s"
        ]
        equality_raw = _reissue(equality)
        self.assertEqual(
            set(_render(equality_raw).values()),
            {_registered_sentence(equality)},
        )
        equality["support_outcome"] = "not_supported"
        self.assertTrue(_all_stop(_render(_reissue(equality))))

        # A strict relation that disappears at the ruled six-decimal rendering
        # precision is refused rather than printed as an apparent equality.
        near_tie_not_supported = copy.deepcopy(issued["not_supported.json"])
        near_tie_not_supported["edge_records"][13].update(
            fitted_residual_interval_s={"lower": -0.0280682, "upper": 0.02},
            effective_clock_anchor_bound_s=0.002,
            composed_absolute_residual_bound_s=0.0300682,
        )
        near_tie_not_supported["largest_inserted_gap_edge"] = copy.deepcopy(
            near_tie_not_supported["edge_records"][13]
        )
        near_tie_not_supported["largest_composed_edge_residual_bound_s"] = 0.0300682
        near_tie_not_supported["pulse_derived_timing_bound_s"] = 0.0300679
        near_tie_not_supported_raw = _reissue(near_tie_not_supported)
        self.assertEqual(
            validate_transfer_fiducial_result(json.loads(near_tie_not_supported_raw)),
            [],
        )
        self.assertTrue(_all_stop(_render(near_tie_not_supported_raw)))

        near_tie_supported = copy.deepcopy(supported)
        near_tie_supported["pulse_derived_timing_bound_s"] = 0.0220002
        near_tie_supported_raw = _reissue(near_tie_supported)
        self.assertEqual(
            validate_transfer_fiducial_result(json.loads(near_tie_supported_raw)),
            [],
        )
        self.assertTrue(_all_stop(_render(near_tie_supported_raw)))

        # Missing, malformed, or unauthenticated inputs never expose a partial
        # site result.
        malformed = [b"", b"{}", b'{"x":NaN}', b'{"x":1,"x":2}']
        for raw in malformed:
            with self.subTest(malformed=raw):
                self.assertTrue(_all_stop(_render(raw)))


if __name__ == "__main__":
    unittest.main()
