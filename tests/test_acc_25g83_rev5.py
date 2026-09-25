"""The Revision 5 epoch and disposition boundary."""
from __future__ import annotations

from dataclasses import replace
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from scripts import issue_calibration_acceptance_generation as issuer
from scripts import sim_acc_25g83_rev5 as simulation
from joulewise import calibration_bracketing as bracketing
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from tests.fixtures.epoch_bootstrap.build import Slot, build_derivation_ledger

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
R7 = ROOT / "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json"
R6 = ROOT / "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json"
REGISTRY = ROOT / "configs/calibration/observation_dispositions.json"
DECISION_ID = "D-126-disposition-25G83-v3-2026-09-25"
LAUNCH_CONDITION = re.compile(
    r"template at commit \S+, rendered-plist digests \S+, \S+, and \S+\."
)


def registration_with_launch_pins(commit: str, night: str, deadman: str, probe: str) -> str:
    """Derive each seal fixture from the current registration's operating sentence."""
    text = PREREG.read_text()
    condition = (
        f"template at commit {commit}, rendered-plist digests "
        f"{night}, {deadman}, and {probe}."
    )
    result, count = LAUNCH_CONDITION.subn(condition, text)
    if count != 1:
        raise AssertionError(f"expected one launch condition, found {count}")
    return result


def sealed_registration() -> str:
    return registration_with_launch_pins("a" * 40, "b" * 64, "c" * 64, "d" * 64)
IDS_AND_VALUES = [
    ("08cf2f19ca7d2b1881e9ed426bbf2c4039e1b425e1ba999a5527bcee4e743cb6", "0.041133514338919874"),
    ("697ad07383e83bca6e031dd40708595d1f59227fece3c3eb8e6d04c8c2318dca", "0.04200278099548145"),
    ("e7e313e191bc844b49f4ddb18cbea5e17ca8367faa097f81aa699fc89a2d81a1", "0.172710636067422"),
    ("a1975da884533272159688d260aa034fe7f4ccfb30e4abaa67cde14977bc38fc", "0.03255031906139217"),
    ("7bce01d1490e10190958052c770f790a2ea2733c5091c605f2fdc86a09afb1c2", "0.04103035733376445"),
    ("ba83eb6f2b3dfb2e72e5cf37fe25df8d3387e70dafc6e8fe384b1f650003a236", "0.04337273381948624"),
    ("fc6e8fb3d3d69ef157407f0ecb565e6952e977e84f637c151c1edcfb402cf57f", "0.028250396657612444"),
    ("64fc21fb609d5baba98dc686dff12ab803b6294474639551f23fdb0a078257cd", "0.035576770468514644"),
    ("45731bb9943b9f29a3f3d6fc2175c7b66ad11987f88de1868fb79fb8f87d1cdb", "0.03487995875720681"),
    ("150e6e9b1c0b04a440a2b9b63f858fd92a8f0e4f858b512ab7d627ced71b82a3", "0.13333095801710004"),
    ("748018ce72e41600464dcb9f2fddcc466e2e3c0ebfcf6474828d908239c36b7b", "0.036897960254235855"),
]


class RevisionFiveTests(unittest.TestCase):
    def test_registry_tracks_all_archived_valid_observations(self) -> None:
        rows = json.loads(REGISTRY.read_text())
        self.assertEqual({row["content_id"] for row in rows}, {item[0] for item in IDS_AND_VALUES})
        self.assertEqual({row["disposing_decision_id"] for row in rows}, {DECISION_ID})
        self.assertIn("# Revision 5 (", PREREG.read_text())

    def test_decision_log_binds_exact_registry_ids(self) -> None:
        text = (ROOT / "docs/decision_log.md").read_text()
        heading = f"## {DECISION_ID} — D-126 disposition, epoch 25G83 v3, 2026-09-25"
        self.assertEqual(text.splitlines().count(heading), 1)
        entry = text.split(heading, 1)[1].split("\n## ", 1)[0]
        table_ids = re.findall(r"`([0-9a-f]{64})`", entry)
        registry_ids = {row["content_id"] for row in json.loads(REGISTRY.read_text())
                        if row["disposing_decision_id"] == DECISION_ID}
        self.assertEqual(len(table_ids), 11)
        self.assertEqual(set(table_ids), registry_ids)

    def test_registry_rejects_unruled_or_duplicate_dispositions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            row = json.loads(REGISTRY.read_text())[0]
            path.write_text(json.dumps([row, row]))
            with self.assertRaisesRegex(issuer.PrepareRefusal, "invalid or duplicate"):
                issuer._registered_dispositions(path)
            row["disposing_decision_id"] = "unruled"
            path.write_text(json.dumps([row]))
            with self.assertRaisesRegex(issuer.PrepareRefusal, "invalid or duplicate"):
                issuer._registered_dispositions(path)

    def test_sealed_copy_clears_placeholder_refusal_but_malformed_seal_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = build_derivation_ledger(
                root / "fixture", [Slot("0.025") for _ in range(12)],
                second_session=("derivation-night-2", [Slot("0.026") for _ in range(12)]),
            )
            sealed = root / "sealed.md"
            sealed.write_text(sealed_registration())
            malformed = root / "malformed.md"
            malformed.write_text(registration_with_launch_pins(
                "not-a-commit", "b" * 64, "c" * 64, "d" * 64,
            ))

            def args(prereg: Path):
                return issuer.build_parser().parse_args([
                    "prepare-candidate", "--ledger", str(fixture["ledger"]),
                    "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
                    "--preregistration", str(prereg),
                    "--preregistration-sha256", hashlib.sha256(prereg.read_bytes()).hexdigest(),
                    "--predecessor-acceptance", str(R7),
                    "--registration-session-id", "derivation-night-1",
                    "--registration-session-id", "derivation-night-2",
                    "--d125-ruling", "D-125 25G83/v3 Revision 5",
                    "--out", str(root / "candidate.json"),
                ])

            with patch.object(issuer, "_registered_dispositions", return_value={}), patch.object(
                issuer, "_derivation_frame_cadence", return_value={"median_s": .132, "max_s": .144}
            ):
                with self.assertRaisesRegex(issuer.PrepareRefusal, "pins are malformed"):
                    issuer._prepare_candidate(args(malformed))
                candidate = issuer._prepare_candidate(args(sealed))
            self.assertEqual(candidate["registered_generation_row"]["registration_revision"], 5)

    def test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = build_derivation_ledger(
                root / "fixture", [Slot("0.025") for _ in range(12)],
                second_session=("derivation-night-2", [Slot("0.026") for _ in range(12)]),
            )
            snapshot = load_calibration_ledger_snapshot(
                fixture["ledger"], fixture["pin"], require_committed_pin=True,
                verify_custody=False, mode="read_replay", repo_root=fixture["root"],
            )
            foreign = tuple(replace(
                snapshot.observations[i], attempt_id=f"archived-{i}",
                bracket_session_id="archived-n1-n2", content_id=content_id,
                exact_bound_lexeme_s=value,
            ) for i, (content_id, value) in enumerate(IDS_AND_VALUES))
            augmented = replace(snapshot, observations=snapshot.observations + foreign)
            sealed = root / "sealed.md"
            sealed.write_text(sealed_registration())
            unsealed = root / "unsealed.md"
            unsealed.write_text(registration_with_launch_pins(
                "<PR-L-MERGE-SHA>", "<RENDERED-PLIST-SHA256:night>",
                "<RENDERED-PLIST-SHA256:deadman>", "<RENDERED-PLIST-SHA256:probe>",
            ))
            pre_revision = root / "pre_revision_5.md"
            pre_revision.write_text(PREREG.read_text().split("# Revision 5 (", 1)[0])
            malformed = root / "malformed.md"
            malformed.write_text(registration_with_launch_pins(
                "not-a-commit", "b" * 64, "c" * 64, "d" * 64,
            ))
            registry = root / "registry.json"
            out = root / "candidate.json"
            def args(prereg: Path):
                return issuer.build_parser().parse_args([
                    "prepare-candidate", "--ledger", str(fixture["ledger"]),
                    "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
                    "--preregistration", str(prereg),
                    "--preregistration-sha256", hashlib.sha256(prereg.read_bytes()).hexdigest(),
                    "--predecessor-acceptance", str(R7),
                    "--registration-session-id", "derivation-night-1",
                    "--registration-session-id", "derivation-night-2",
                    "--d125-ruling", "D-125 25G83/v3 Revision 5", "--out", str(out),
                ])
            with patch.object(issuer, "load_calibration_ledger_snapshot", return_value=augmented), patch.object(
                issuer, "_derivation_frame_cadence", return_value={"median_s": .132, "max_s": .144}
            ), patch.object(issuer, "DISPOSITION_REGISTRY", registry):
                with self.assertRaisesRegex(issuer.PrepareRefusal, "requires registration Revision 5"):
                    issuer._prepare_candidate(args(pre_revision))
                with self.assertRaisesRegex(issuer.PrepareRefusal, "unsealed placeholders"):
                    issuer._prepare_candidate(args(unsealed))
                with self.assertRaisesRegex(issuer.PrepareRefusal, "pins are malformed"):
                    issuer._prepare_candidate(args(malformed))
                wrong_predecessor = args(sealed)
                wrong_predecessor.predecessor_acceptance = R6
                with self.assertRaisesRegex(issuer.PrepareRefusal, "requires r7 predecessor"):
                    issuer._prepare_candidate(wrong_predecessor)
                registry.write_text("[]\n")
                with self.assertRaisesRegex(issuer.PrepareRefusal, "valid same-epoch observations outside"):
                    issuer._prepare_candidate(args(sealed))
                registry.write_bytes(REGISTRY.read_bytes())
                candidate = issuer._prepare_candidate(args(sealed))
            prior = candidate["prior_observation_set"]
            self.assertEqual({row["content_id"] for row in prior["observations"]} &
                             {content_id for content_id, _ in IDS_AND_VALUES},
                             {content_id for content_id, _ in IDS_AND_VALUES})
            self.assertEqual(prior["disposing_decision_ids"], [DECISION_ID])
            self.assertEqual(candidate["derivation_corpus"]["n"], 24)
            self.assertEqual(candidate["registered_generation_row"]["registration_revision"], 5)
            issued = copy.deepcopy(candidate)
            issued["artifact_role"] = "issued"
            issued["issuance"]["claim_eligible"] = True
            row = copy.deepcopy(issued["registered_generation_row"])
            row["epoch_catalog_ids"] = tuple(row["epoch_catalog_ids"])
            row["registration_session_ids"] = tuple(row["registration_session_ids"])
            cutoff = issued["ledger_cutoff"]
            baseline = replace(augmented, baseline_sequence=cutoff["sequence"],
                               baseline_digest=cutoff["head_digest"])
            bindings = {**dict(snapshot.observations[0].t1_bindings), **issued["identity_epoch"]}
            with patch.dict(bracketing._D102_GENERATION_DERIVATIONS,
                            {issued["acceptance_id"]: row}), patch.dict(
                bracketing.ISSUED_ACCEPTANCE_REGISTRY,
                {issued["acceptance_id"]: {"file_sha256": "e" * 64}},
            ), patch.object(
                bracketing, "load_calibration_acceptance_bound", return_value=issued
            ):
                bracket, _ = bracketing.evaluate_calibration_bracket(
                    [], window_start_s=100, window_end_s=110, bindings=bindings,
                    policy=bracketing.CalibrationBracketingPolicy(
                        require_bracket=True, calibration_bracket_max_drift_s=.010),
                    ledger_snapshot=baseline,
                )
            self.assertEqual(bracket["acceptance"]["freshness"]["status"], "fresh")

    def test_pinned_estimator_files_match_c034a56f(self) -> None:
        # SHA-256 of each blob's bytes at c034a56f, before Revision 5.
        expected = {
            "joulewise/powermetrics_fiducial.py": "386e825440e02bb0720e7b74f0f7503d785fb543a08c45386014eeb4216bab92",
            "joulewise/uncertainty_evidence.py": "b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8",
            "joulewise/adapters/powermetrics.py": "70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4",
            "joulewise/reduce.py": "7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc",
        }
        for path, digest in expected.items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_w1_futility_and_plateau_inset_refuse_by_mechanism(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sealed = root / "sealed.md"
            sealed.write_text(sealed_registration())
            for label, first, reason in (
                ("futility", [Slot("0.025") for _ in range(5)] +
                 [Slot("0.025", disposition="ordinary-invalid") for _ in range(7)],
                 "W1 futility procedure violation"),
                ("inset", [Slot("0.025") for _ in range(11)] + [Slot("0.251")],
                 "PLATEAU_INSET_S"),
            ):
                with self.subTest(label=label):
                    fixture = build_derivation_ledger(
                        root / label, first,
                        second_session=("derivation-night-2", [Slot("0.026") for _ in range(12)]),
                    )
                    args = issuer.build_parser().parse_args([
                        "prepare-candidate", "--ledger", str(fixture["ledger"]),
                        "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
                        "--preregistration", str(sealed),
                        "--preregistration-sha256", hashlib.sha256(sealed.read_bytes()).hexdigest(),
                        "--predecessor-acceptance", str(R7),
                        "--registration-session-id", "derivation-night-1",
                        "--registration-session-id", "derivation-night-2",
                        "--d125-ruling", "D-125 25G83/v3 Revision 5",
                        "--out", str(root / f"{label}.json"),
                    ])
                    with self.assertRaisesRegex(issuer.PrepareRefusal, reason):
                        issuer._prepare_candidate(args)

    def test_w3_refuses_when_w1_w2_valid_count_is_already_twelve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = build_derivation_ledger(
                root / "fixture", [Slot("0.025") for _ in range(12)],
                second_session=("derivation-night-2", [Slot("0.026") for _ in range(12)]),
            )
            snapshot = load_calibration_ledger_snapshot(
                fixture["ledger"], fixture["pin"], require_committed_pin=True,
                verify_custody=False, mode="read_replay", repo_root=fixture["root"],
            )
            second = snapshot.bracket_session_by_id["derivation-night-2"]
            third = replace(second, session_id="derivation-night-3",
                            capability_sequence=second.capability_sequence + 1000)
            extra = replace(snapshot.observations[0], attempt_id="third-invalid",
                            content_id="f" * 64, bracket_session_id="derivation-night-3",
                            disposition="ordinary-invalid")
            augmented = replace(snapshot, bracket_sessions=snapshot.bracket_sessions + (third,),
                                observations=snapshot.observations + (extra,))
            sealed = root / "sealed.md"
            sealed.write_text(sealed_registration())
            args = issuer.build_parser().parse_args([
                "prepare-candidate", "--ledger", str(fixture["ledger"]),
                "--head-pin", str(fixture["pin"]), "--repo-root", str(fixture["root"]),
                "--preregistration", str(sealed),
                "--preregistration-sha256", hashlib.sha256(sealed.read_bytes()).hexdigest(),
                "--predecessor-acceptance", str(R7),
                "--registration-session-id", "derivation-night-1",
                "--registration-session-id", "derivation-night-2",
                "--registration-session-id", "derivation-night-3",
                "--d125-ruling", "D-125 25G83/v3 Revision 5",
                "--out", str(root / "candidate.json"),
            ])
            with patch.object(issuer, "load_calibration_ledger_snapshot", return_value=augmented):
                with self.assertRaisesRegex(issuer.PrepareRefusal, "W3 was opened despite at least 12 valid"):
                    issuer._prepare_candidate(args)

    def test_simulation_runs_all_four_models_without_false_admission(self) -> None:
        rows = simulation.run(20, 20)
        self.assertEqual({row["model"] for row in rows}, set(simulation.MODELS))
        self.assertTrue(all(row["false_admission"] == 0 for row in rows))
        self.assertGreater(sum(row["w3_opened"] for row in simulation.run(20, 20, .5)), 0)
        self.assertLessEqual(1 - .05 ** (1 / 200), .015)
        self.assertEqual(simulation.exact_binomial_interval_95(0, 200)[0], 0.0)


if __name__ == "__main__":
    unittest.main()
