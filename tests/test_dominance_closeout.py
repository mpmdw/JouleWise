"""Producer-ownership regressions for D-165 close-out refusal codes."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest import mock

from joulewise.analysis_manifest_v3 import calculate_manifest_id
from joulewise import dominance_closeout as core
from scripts.build_d165_dominance_closeout import build_d165_dominance_closeout
from tests.test_d165_dominance_closeout import (
    _file_json_bytes,
    _reseal_test_sources,
    finalized_manifest,
    floor_artifact,
    replay_sidecar,
)


ROOT = Path(__file__).resolve().parents[1]


class D165CloseoutReasonOwnershipTests(unittest.TestCase):
    def test_real_builder_refusals_are_enumerated_and_registered(self) -> None:
        manifest = finalized_manifest()
        floor = floor_artifact()
        sidecar = replay_sidecar(floor)

        missing_cell_sidecar = copy.deepcopy(sidecar)
        missing_cell_sidecar["cells"].pop()
        missing_cell_sources = _reseal_test_sources(
            copy.deepcopy(manifest), copy.deepcopy(floor), missing_cell_sidecar
        )

        wrong_member_sidecar = copy.deepcopy(sidecar)
        wrong_member_sidecar["cells"][0]["comparative"]["common_mode_replay"][
            "inputs"
        ]["blocks"][0]["members"]["A1"] = "wrong-bundle"
        wrong_member_sources = _reseal_test_sources(
            copy.deepcopy(manifest), copy.deepcopy(floor), wrong_member_sidecar
        )

        unresolved_manifest = copy.deepcopy(manifest)
        unresolved_manifest["arms"][0]["floor_cell_id"] = None
        unresolved_sources = _reseal_test_sources(
            unresolved_manifest, copy.deepcopy(floor), copy.deepcopy(sidecar)
        )

        default_sidecar = copy.deepcopy(sidecar)
        default_comparative = default_sidecar["cells"][0]["comparative"]
        default_sidecar["cells"][0]["comparative"] = {
            "independent": default_comparative["independent"],
            "estimator": "default",
        }
        default_sources = _reseal_test_sources(
            copy.deepcopy(manifest), copy.deepcopy(floor), default_sidecar
        )

        zero_floor = copy.deepcopy(floor)
        zero_floor["cells"][0]["absolute"]["max_abs_residual_j"] = 0.0
        zero_floor["cells"][0]["absolute"]["prediction_component_j"] = 0.0
        zero_sources = _reseal_test_sources(
            copy.deepcopy(manifest), zero_floor, replay_sidecar(zero_floor)
        )

        bound_manifest = copy.deepcopy(manifest)
        bound_floor = copy.deepcopy(floor)
        bound_sidecar = copy.deepcopy(sidecar)
        bound_sources = _reseal_test_sources(
            bound_manifest, bound_floor, bound_sidecar
        )
        tampered_floor = copy.deepcopy(bound_floor)
        tampered_floor["cells"][0]["absolute"][
            "corner_widened_unguarded_floor_j"
        ] += 1.0
        floor_digest_sources = (
            bound_sources[0],
            _file_json_bytes(tampered_floor),
            bound_sources[2],
        )

        tampered_manifest = copy.deepcopy(bound_manifest)
        tampered_manifest["arms"][0]["model_tag"] = "tampered"
        manifest_id_sources = (
            _file_json_bytes(tampered_manifest),
            bound_sources[1],
            bound_sources[2],
        )

        missing_attachment = copy.deepcopy(bound_manifest)
        missing_attachment["evidence"].pop("dominance_replay_sidecar")
        missing_attachment["manifest_id"] = calculate_manifest_id(
            missing_attachment
        )
        missing_attachment_sources = (
            _file_json_bytes(missing_attachment),
            bound_sources[1],
            bound_sources[2],
        )

        wrong_digest = copy.deepcopy(bound_manifest)
        wrong_digest["evidence"]["dominance_replay_sidecar"]["sha256"] = "0" * 64
        wrong_digest["manifest_id"] = calculate_manifest_id(wrong_digest)
        replay_digest_sources = (
            _file_json_bytes(wrong_digest),
            bound_sources[1],
            bound_sources[2],
        )

        wrong_identity = copy.deepcopy(bound_manifest)
        wrong_identity["evidence"]["dominance_replay_sidecar"][
            "sidecar_id"
        ] = "wrong-sidecar"
        wrong_identity["manifest_id"] = calculate_manifest_id(wrong_identity)
        replay_identity_sources = (
            _file_json_bytes(wrong_identity),
            bound_sources[1],
            bound_sources[2],
        )

        closeouts = {
            "source cell census": build_d165_dominance_closeout(
                *missing_cell_sources
            ),
            "member census": build_d165_dominance_closeout(*wrong_member_sources),
            "unresolved floor": build_d165_dominance_closeout(*unresolved_sources),
            "default estimator": build_d165_dominance_closeout(*default_sources),
            "zero denominator": build_d165_dominance_closeout(*zero_sources),
            "floor digest": build_d165_dominance_closeout(*floor_digest_sources),
            "manifest identity": build_d165_dominance_closeout(*manifest_id_sources),
            "missing replay attachment": build_d165_dominance_closeout(
                *missing_attachment_sources
            ),
            "replay digest": build_d165_dominance_closeout(*replay_digest_sources),
            "replay identity": build_d165_dominance_closeout(
                *replay_identity_sources
            ),
        }
        registry_codes = set(core.D165_OR01_REASON_SENTENCES)
        enumeration = set(core.D165_CLOSEOUT_REFUSAL_CODES)
        self.assertEqual(
            len(core.D165_CLOSEOUT_REFUSAL_ENUMERATION), len(enumeration)
        )
        self.assertEqual(enumeration, registry_codes)
        for label, closeout in closeouts.items():
            with self.subTest(label=label):
                emitted = closeout["refusal_reason"]
                self.assertIn(emitted, enumeration)
                self.assertIn(emitted, registry_codes)

    def test_registry_and_enumeration_fail_on_addition_to_either_side(self) -> None:
        extra = "d165_paper_future_unmapped"
        with mock.patch.object(
            core,
            "D165_CLOSEOUT_REFUSAL_CODES",
            core.D165_CLOSEOUT_REFUSAL_CODES | {extra},
        ):
            self.assertNotEqual(
                set(core.D165_OR01_REASON_SENTENCES),
                core.D165_CLOSEOUT_REFUSAL_CODES,
            )
        with mock.patch.object(
            core,
            "D165_OR01_REASON_SENTENCES",
            {**core.D165_OR01_REASON_SENTENCES, extra: "future sentence"},
        ):
            self.assertNotEqual(
                set(core.D165_OR01_REASON_SENTENCES),
                core.D165_CLOSEOUT_REFUSAL_CODES,
            )

    def test_refusal_literals_have_one_enumeration_home(self) -> None:
        source = (ROOT / "joulewise/dominance_closeout.py").read_text(
            encoding="utf-8"
        )
        for code in core.D165_CLOSEOUT_REFUSAL_CODES:
            with self.subTest(code=code):
                occurrences = source.count(f'"{code}"') + source.count(
                    f"'{code}'"
                )
                self.assertEqual(occurrences, 1)

if __name__ == "__main__":
    unittest.main()
