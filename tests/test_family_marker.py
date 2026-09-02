from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise import arm_readiness as readiness
from joulewise import scheduler_gates


ROOT = Path(__file__).resolve().parents[1]
REFRESH_SCRIPT = ROOT / "scripts/refresh_receipt_histsem_pinset.py"
SHA = "0" * 64
OID = "a" * 40
TREE = "b" * 40


def refresh_lane_module():
    spec = importlib.util.spec_from_file_location(
        "joulewise_refresh_receipt_histsem_pinset_family_test",
        REFRESH_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load refresh lane")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(label: str) -> str:
    """A distinct, stable, obviously-synthetic SHA-256 per fixture field.

    Every digest field in these fixtures used to be ``"0" * 64``.  That made
    the whole schema test class blind to cross-field comparison bugs: code that
    compared ``pack_sha256`` where it meant ``freeze_receipt.sha256`` compared
    equal either way.  Deriving each fixture digest from its field's own name
    means any such swap now shows up as a mismatch (gap G-9).
    """

    return hashlib.sha256(f"joulewise-fixture:{label}".encode()).hexdigest()


def member(profile: str, pack_id: str) -> dict[str, object]:
    def field(name: str) -> str:
        return digest(f"{profile}:{name}")

    return {
        "profile": profile,
        "pack_id": pack_id,
        "pack_path": f"configs/campaigns/{pack_id}",
        "pack_digest_algorithm": readiness.PACK_DIGEST_ALGORITHM,
        "pack_sha256": field("pack"),
        "plan_tree": {
            "path": "plan_tree.json",
            "sha256": field("plan_tree"),
            "sidecar_path": "plan_tree.sha256",
            "sidecar_sha256": field("plan_tree.sidecar"),
        },
        "frozen_plan": {
            "plan_id": "plan-v4",
            "window_id": f"window-{profile.lower()}",
            "path": "calibration_plan.json",
            "sha256": field("frozen_plan"),
        },
        "freeze_receipt": {
            "schema_version": readiness.FREEZE_RECEIPT_V2_SCHEMA,
            "receipt_id": "freeze-0004",
            "ordinal": 4,
            "path": "arm_readiness.freeze.receipts/freeze-0004.json",
            "sha256": field("freeze_receipt"),
            "sidecar_path": "arm_readiness.freeze.receipts/freeze-0004.json.sha256",
            "sidecar_sha256": field("freeze_receipt.sidecar"),
            "status": "PASS",
        },
    }


def marker() -> dict[str, object]:
    return {
        "schema_version": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
        "marker_kind": "FAMILY_PUBLICATION",
        "family_id": "d117-v5",
        "family_generation": 5,
        "publication_state": "PUBLISHED",
        "publication_git": {
            "head_commit": OID,
            "head_tree_oid": TREE,
            "local_main_commit": OID,
            "origin_main_commit": OID,
            "clean": True,
            "exact_match": True,
        },
        "common_evidence_git": {"head_commit": OID, "head_tree_oid": TREE},
        "lifecycle_registry": {
            "path": "configs/arm_readiness/d117_row_registry_v2.json",
            "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
            "registry_id": "d117-row-registry-v2",
            "sha256": digest("registry"),
            "lifecycle_registry_id": "d117-r1-lifecycle-v1",
            "family_publication_marker_schema": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
            "family_publication_refusal": {
                "role": "FAMILY_PUBLICATION",
                "code": "readiness_r1_family_publication",
                "type": "CUSTODY",
            },
        },
        "members": [
            member("ALPHA", "d117_floor_qwen3-1p7b_v5"),
            member("BETA", "d117_floor_qwen3-8b_v5"),
            member("GAMMA", "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"),
        ],
        "terminal_review": {
            "evidence_kind": "TERMINAL_REVIEW",
            "head_tree_oid": TREE,
        },
        "publication_authority": {
            "confirmation_schema": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        },
        "conditional_paths_deferred": {
            "gate": readiness.R1_DIGEST_CONDITIONAL_GATE_ID,
            "deferred_paths": sorted(readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS),
            "enforced_at_entry_points": list(
                readiness.R1_DIGEST_CONDITIONAL_ENTRY_POINTS
            ),
        },
        "authoring_context": {
            "transaction_id": f"d117-v5@{OID}",
            "source_commit_time_utc": "2026-08-22T00:00:00Z",
            "construction_phase": "POST_FREEZE_FAMILY_BOUNDARY",
            "custody_class": "TRANSACTION_EXTERNAL",
            "builder": {"path": "scripts/build_family_marker.py", "sha256": digest("builder")},
            "consumer": {"path": "scripts/verify_family_marker.py", "sha256": digest("consumer")},
        },
        "assurance": copy.deepcopy(readiness.ASSURANCE),
    }


def confirmation(marker_sha: str | None = None) -> dict[str, object]:
    marker_sha = digest("marker") if marker_sha is None else marker_sha
    source = marker()
    return {
        "schema_version": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
        "table_kind": "D117_STEP6_CONFIRMATION",
        "transaction_id": "d117-v5-publication",
        "family_id": "d117-v5",
        "git": {"head_commit": OID, "head_tree_oid": TREE},
        "registry": {
            "path": "configs/arm_readiness/d117_row_registry_v2.json",
            "schema_version": readiness.R1_ROW_REGISTRY_SCHEMA,
            "registry_id": "d117-row-registry-v2",
            "sha256": digest("registry"),
        },
        "family_publication": {
            "marker": {
                "path": readiness.FAMILY_PUBLICATION_MARKER_NAME,
                "schema_version": readiness.FAMILY_PUBLICATION_MARKER_SCHEMA,
                "sha256": marker_sha,
            },
            "members": [
                {
                    "profile": item["profile"],
                    "pack_id": item["pack_id"],
                    "pack_sha256": item["pack_sha256"],
                    "freeze_receipt_sha256": item["freeze_receipt"]["sha256"],
                }
                for item in source["members"]
            ],
        },
        "successor_pinset": {
            "path": "configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json",
            "schema_version": readiness.RECEIPT_HISTSEM_PINSET_SCHEMA,
            "sha256": digest("successor_pinset"),
            "pack_count": 3,
            "receipt_count": 33,
            "fact_count": 33,
        },
        "confirmation": {
            "authority": "ED",
            "decision": "YES",
            "statement": "I confirm these exact D-117 v5 step-6 bytes.",
        },
    }


class FamilyMarkerSchemaTests(unittest.TestCase):
    def test_golden_marker_and_confirmation_are_exact_canonical_schemas(self) -> None:
        value = marker()
        self.assertEqual(readiness.validate_family_publication_marker(value, first_generation=5), value)
        self.assertEqual(readiness.parse_json_bytes(readiness.render_json(value), require_canonical=True), value)
        table = confirmation()
        self.assertEqual(readiness.validate_step6_confirmation_table(table), table)

    def test_marker_schema_tamper_union_maps_to_closed_diagnostics(self) -> None:
        cases = []
        wrong_schema = marker(); wrong_schema["schema_version"] = "joulewise.d117_family_publication_marker.v2"
        cases.append((wrong_schema, "marker_schema_mismatch"))
        unknown = marker(); unknown["members"][0]["unknown"] = True
        cases.append((unknown, "marker_schema_mismatch"))
        incomplete = marker(); incomplete["members"].pop()
        cases.append((incomplete, "roster_incomplete"))
        wrong_family = marker(); wrong_family["members"][0]["pack_id"] = "d117_floor_qwen25_1p5b_v5"
        cases.append((wrong_family, "roster_mismatch"))
        wrong_ordinal = marker(); wrong_ordinal["members"][0]["freeze_receipt"]["ordinal"] = 5
        cases.append((wrong_ordinal, "freeze_binding_mismatch"))
        refused = marker(); refused["members"][0]["freeze_receipt"]["status"] = "REFUSE"
        cases.append((refused, "freeze_binding_mismatch"))
        wrong_tree = marker(); wrong_tree["terminal_review"]["head_tree_oid"] = "c" * 40
        cases.append((wrong_tree, "terminal_review_mismatch"))
        for value, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.validate_family_publication_marker(value, first_generation=5)
                self.assertEqual(caught.exception.check_id, expected)

    def test_confirmation_is_one_two_section_authenticator_without_cycle_fields(self) -> None:
        table = confirmation()
        readiness.validate_step6_confirmation_table(table)
        self.assertEqual(set(table) & {"family_publication", "successor_pinset"}, {"family_publication", "successor_pinset"})
        self.assertNotIn("sha256", table)
        self.assertNotIn("confirmed_at_utc", table["confirmation"])
        source = marker()
        authority = source["publication_authority"]
        self.assertEqual(authority, {
            "confirmation_schema": readiness.STEP6_CONFIRMATION_TABLE_SCHEMA,
            "required_decision": "YES",
        })

    def test_confirmation_missing_unknown_and_wrong_successor_refuse(self) -> None:
        """Each tamper must produce its SPECIFIC diagnostic.

        Asserting only that *some* registered code came back would pass against
        a validator that refuses for the wrong reason -- which is exactly what
        the previous ``assertIn(check_id, FAMILY_PUBLICATION_CHECK_IDS)``
        assertion did (gap G-9).
        """

        unknown = confirmation(); unknown["family_publication"]["extra"] = True
        wrong = confirmation(); wrong["successor_pinset"]["path"] = "configs/arm_readiness/not-enumerated.json"
        old_family = confirmation(); old_family["family_id"] = "d117-v4"
        old_marker = confirmation(); old_marker["family_publication"]["marker"]["path"] = "d117_family_publication_v4.json"
        old_pinset = confirmation(); old_pinset["successor_pinset"]["path"] = "configs/arm_readiness/legacy_receipt_histsem_pinset_v4_v1.json"
        no = confirmation(); no["confirmation"]["decision"] = "NO"
        absent_section = confirmation(); absent_section.pop("successor_pinset")
        wrong_packs = confirmation(); wrong_packs["successor_pinset"]["pack_count"] = 2
        wrong_receipts = confirmation(); wrong_receipts["successor_pinset"]["receipt_count"] = 32
        cases = (
            (unknown, "marker_schema_mismatch", "unknown key in a section"),
            (wrong, "confirmation_mismatch", "successor path off the chain"),
            (old_family, "confirmation_mismatch", "old family identity"),
            (old_marker, "confirmation_mismatch", "old marker path"),
            (old_pinset, "confirmation_mismatch", "old successor pinset path"),
            (no, "confirmation_mismatch", "decision is not the literal YES"),
            (absent_section, "marker_schema_mismatch", "successor section absent"),
            (wrong_packs, "confirmation_mismatch", "pack_count off contract"),
            (wrong_receipts, "confirmation_mismatch", "receipt_count off contract"),
        )
        for value, expected, label in cases:
            with self.subTest(case=label):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.validate_step6_confirmation_table(value)
                self.assertEqual(caught.exception.check_id, expected)

    def test_verification_receipt_lane_fields_gate_and_cannot_be_laundered(self) -> None:
        """Gap G-6: a candidate-lane receipt must not authorise anything.

        The S-0 clone forges ``origin/main``, so a candidate PASS proves only
        that the marker is internally coherent.  Consumers now inspect the
        receipt's own lane fields, and refuse both the honest candidate receipt
        (``lane_inadmissible``) and a doctored one whose fields contradict its
        phase (``lane_inconsistent``).
        """

        published = {
            "schema_version": readiness.FAMILY_PUBLICATION_VERIFICATION_SCHEMA,
            "receipt_kind": "family_publication_verification",
            "phase": "pre-arm",
            "lane": "published",
            "gate_admissible": True,
            "publication_authorized": True,
            "status": "PASS",
        }
        self.assertIs(
            readiness.require_gate_admissible_verification(published), published
        )

        candidate = dict(published, phase="candidate", lane="candidate",
                         gate_admissible=False, publication_authorized=False)
        with self.assertRaises(readiness.FamilyPublicationError) as caught:
            readiness.require_gate_admissible_verification(candidate)
        self.assertEqual(caught.exception.check_id, "lane_inadmissible")

        laundered = (
            ("candidate receipt relabelled published", dict(candidate, lane="published")),
            ("candidate receipt flagged admissible", dict(candidate, gate_admissible=True)),
            ("published receipt flagged candidate", dict(published, lane="candidate")),
            ("authorisation without admissibility",
             dict(published, publication_authorized=False)),
            ("foreign schema", dict(published, schema_version="joulewise.other.v1")),
            ("unknown phase", dict(published, phase="rehearsal")),
        )
        for label, receipt in laundered:
            with self.subTest(case=label):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.require_gate_admissible_verification(receipt)
                self.assertEqual(caught.exception.check_id, "lane_inconsistent")

        refused = dict(published, status="REFUSE")
        with self.assertRaises(readiness.FamilyPublicationError) as caught:
            readiness.require_gate_admissible_verification(refused)
        self.assertEqual(caught.exception.check_id, "lane_inadmissible")

    def test_diagnostic_check_ids_are_exact_closed_enumeration(self) -> None:
        """The set is exact, and every member is reachable.

        Pinning the set exactly is what keeps diagnostics from being invented
        at call sites -- but it also locks in any member that nothing raises.
        The finish round of 2026-08-22 (gap G-5) therefore RETIRED three
        members that had no raise site and could not honestly acquire one:
        ``history_shallow``, ``git_unavailable`` (neither is consulted on this
        path; an unavailable Git surfaces as ``head_unresolvable``), and
        ``internal_error`` (an unhandled fault must propagate, not be
        relabelled as a family-publication diagnosis).  The count went 32 -> 29.
        """

        expected = {
            "marker_absent", "marker_unreadable", "marker_noncanonical",
            "marker_schema_mismatch", "marker_self_digest_mismatch",
            "lane_inconsistent", "lane_inadmissible", "registry_mismatch",
            "registry_dormant", "roster_mismatch", "roster_incomplete",
            "pack_not_member", "family_incoherent", "head_mismatch",
            "head_unpublished", "head_unresolvable",
            "worktree_dirty", "pack_digest_mismatch",
            "plan_binding_mismatch", "evidence_set_mismatch",
            "freeze_binding_mismatch", "freeze_not_pass", "predecessor_mismatch",
            "terminal_review_mismatch", "confirmation_missing",
            "confirmation_mismatch", "tool_mismatch", "output_in_tree",
            "output_collision",
        }
        self.assertEqual(readiness.FAMILY_PUBLICATION_CHECK_IDS, frozenset(expected))
        self.assertEqual(len(readiness.FAMILY_PUBLICATION_CHECK_IDS), 29)
        with self.assertRaisesRegex(ValueError, "unregistered"):
            readiness.FamilyPublicationError("free_form", "no")
        for retired in ("history_shallow", "git_unavailable", "internal_error"):
            with self.subTest(retired=retired):
                with self.assertRaisesRegex(ValueError, "unregistered"):
                    readiness.FamilyPublicationError(retired, "retired in G-5")

    def test_every_check_id_has_a_raise_site(self) -> None:
        """The closure discipline's other half: no dead members.

        A member with no raise site is a diagnostic the code can never emit,
        and the exactness test above would preserve it indefinitely.  This
        counts raise sites mechanically across the library, the scheduler, and
        the two custody tools.
        """

        trees = [
            ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            for relative in (
                "joulewise/arm_readiness.py",
                "joulewise/scheduler_gates.py",
                "scripts/build_family_marker.py",
                "scripts/verify_family_marker.py",
            )
        ]
        raised: set[str] = set()
        for tree in trees:
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                callee = (
                    node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else node.func.id
                    if isinstance(node.func, ast.Name)
                    else None
                )
                if callee == "FamilyPublicationError" and node.args:
                    first = node.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        raised.add(first.value)
                if callee == "_read_external_canonical":
                    for keyword in node.keywords:
                        if (
                            keyword.arg
                            in {
                                "absent_check",
                                "invalid_check",
                                "noncanonical_check",
                                "digest_check",
                            }
                            and isinstance(keyword.value, ast.Constant)
                            and isinstance(keyword.value.value, str)
                        ):
                            raised.add(keyword.value.value)

            # The builder's reviewed-main split is deliberately dynamic, but
            # its two alternatives are still closed AST literals rather than a
            # free-form variable that could launder arbitrary check ids.
            assignments = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "diagnostic"
                    for target in node.targets
                )
            ]
            for assignment in assignments:
                if isinstance(assignment.value, ast.IfExp):
                    alternatives = (assignment.value.body, assignment.value.orelse)
                    if all(
                        isinstance(item, ast.Constant)
                        and isinstance(item.value, str)
                        for item in alternatives
                    ):
                        raised.update(item.value for item in alternatives)
        self.assertEqual(
            readiness.FAMILY_PUBLICATION_CHECK_IDS - raised,
            set(),
            "closed check-id set contains members nothing raises",
        )


class FamilyMarkerMechanismTests(unittest.TestCase):
    def _assert_custody_tool_sidecars_current(self, root: Path, lane: object) -> None:
        for name in lane.CUSTODY_TOOL_SIDECARS:
            tool = root / "scripts" / name
            sidecar = tool.with_name(f"{name}.sha256")
            self.assertTrue(sidecar.is_file(), f"missing sidecar for {name}")
            tool_bytes = tool.read_bytes()
            sidecar_bytes = sidecar.read_bytes()
            self.assertEqual(
                sidecar_bytes,
                readiness.gnu_sidecar(readiness.sha256_bytes(tool_bytes), name),
                f"{name}.sha256 differs from the independent GNU-sidecar oracle",
            )
            self.assertEqual(
                sidecar_bytes,
                lane.render_tool_sidecar(tool_bytes, name),
                f"{name}.sha256 differs from the refresh-lane binding",
            )

    def test_family_member_converts_lifecycle_escape_to_family_diagnostic(self) -> None:
        registry, _raw = readiness.load_registry(ROOT)
        lifecycle = registry["freeze_evidence_lifecycle"]
        escaped = readiness.EvidenceLifecycleError(
            lifecycle, "DEPENDENCY_CHANGED_SET", "corrupt confirmation custody"
        )
        with (
            mock.patch.object(readiness, "_plan_profile", return_value="ALPHA"),
            mock.patch.object(readiness, "_plan_tree", return_value=({}, b"{}\n")),
            mock.patch.object(
                readiness, "_load_freeze_reference", side_effect=escaped
            ),
        ):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._family_member(
                    ROOT,
                    ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5",
                    registry,
                    {},
                )
        self.assertEqual(caught.exception.check_id, "evidence_set_mismatch")

    def test_marker_deletion_cannot_disengage_registry_installed_family(self) -> None:
        registry = json.loads((ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes())
        with (
            mock.patch.object(readiness, "_repo_for_pack", return_value=ROOT),
            mock.patch.object(readiness, "load_registry", return_value=(registry, readiness.render_json(registry))),
        ):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._gate_family_publication(
                    Path("d117_floor_qwen3-1p7b_v5"),
                    marker_path=None,
                    confirmation_path=None,
                )
        self.assertEqual(caught.exception.check_id, "marker_absent")

    def test_generation_threshold_is_a_reviewed_registry_value_not_code(self) -> None:
        """Split S-2, behaviourally.

        The threshold must come from the tracked registry, so that advancing to
        a `_v5` family is a reviewed registry edit.  Proof: no code literal
        remains; the reader returns the registry's value; changing the registry
        value changes what the marker validator accepts; and a registry without
        the value refuses rather than defaulting.
        """

        self.assertFalse(hasattr(readiness, "FAMILY_PUBLICATION_FIRST_GENERATION"))
        registry = json.loads((ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes())
        policy = registry["freeze_evidence_lifecycle"]["successor_policy"]
        self.assertEqual(policy["family_publication_first_generation"], 5)
        self.assertEqual(readiness._family_first_generation(registry), 5)

        # The validator follows the registry, not a constant: the same marker
        # bytes are accepted at 5 and refused at 4.
        value = marker()
        self.assertEqual(
            readiness.validate_family_publication_marker(value, first_generation=5),
            value,
        )
        with self.assertRaises(readiness.FamilyPublicationError) as caught:
            readiness.validate_family_publication_marker(value, first_generation=4)
        self.assertEqual(caught.exception.check_id, "marker_schema_mismatch")

        # A registry that carries no reviewed threshold cannot engage at all.
        dormant = copy.deepcopy(registry)
        dormant["freeze_evidence_lifecycle"]["successor_policy"].pop(
            "family_publication_first_generation"
        )
        with self.assertRaisesRegex(
            readiness.ArmReadinessError, "generation threshold"
        ):
            readiness._family_first_generation(dormant)
        with self.assertRaises(readiness.ArmReadinessError) as invalid:
            readiness.validate_registry(dormant)
        self.assertEqual(
            invalid.exception.reason_code, "readiness_schema_invalid"
        )

    def test_freeze_gate_engages_only_on_the_predecessor_at_or_above_threshold(
        self,
    ) -> None:
        """Split S-2 + baseline item 5: freeze-time engagement is
        predecessor-only (the bootstrap cure) and threshold-driven.

        The pack being minted is never gated on its own unbuilt publication, so
        a generation-5 pack with no marker must still reach the chain gate; a generation-5
        PREDECESSOR without a marker must refuse.
        """

        registry = json.loads((ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes())
        calls: list[Path] = []

        def record(pack_root: Path, **kwargs: object) -> None:
            calls.append(Path(pack_root))
            raise readiness.FamilyPublicationError(
                "marker_absent", "registry-installed family has no marker"
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in (
                "d117_floor_qwen25_1p5b_v3",
                "d117_floor_qwen3-1p7b_v5",
                "d117_floor_qwen25_1p5b_v6",
            ):
                (root / name).mkdir()
            with (
                mock.patch.object(readiness, "_gate_family_publication", record),
                mock.patch.object(
                    readiness, "_gate_receipt_histsem", return_value=None
                ),
                mock.patch.object(readiness, "_plan_tree", return_value=({}, b"{}\n")),
                mock.patch.object(
                    readiness,
                    "_registry_reference",
                    return_value=(
                        registry,
                        readiness.render_json(registry),
                        {
                            "registry_id": registry["registry_id"],
                            "path": readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix(),
                            "sha256": digest("registry"),
                            "plan_profile": "ALPHA",
                        },
                    ),
                ),
                mock.patch.object(readiness, "_valid_plan_attachment", return_value=None),
                mock.patch.object(readiness, "_repo_for_pack", return_value=ROOT),
                mock.patch.object(
                    readiness,
                    "load_registry",
                    return_value=(registry, readiness.render_json(registry)),
                ),
            ):
                # No predecessor: the gate is not consulted at all -- the
                # bootstrap case. Execution stops at the patched _plan_tree.
                with self.assertRaises(readiness.ArmReadinessError):
                    readiness.generate_freeze_receipt(
                        root / "d117_floor_qwen3-1p7b_v5",
                        measurement_checkout=ROOT,
                    )
                self.assertEqual(calls, [])

                refusal = readiness.generate_freeze_receipt(
                    root / "d117_floor_qwen25_1p5b_v6",
                    measurement_checkout=ROOT,
                    predecessor_pack_root=root / "d117_floor_qwen3-1p7b_v5",
                )
                self.assertEqual(
                    refusal["reason_codes"], ["readiness_r1_family_publication"]
                )
                self.assertEqual(
                    calls, [(root / "d117_floor_qwen3-1p7b_v5").resolve()]
                )

        self.assertEqual(
            readiness._family_first_generation(registry), 5,
            "the threshold the gate compares against is the registry's",
        )

    def test_arm_library_boundary_refuses_with_the_governed_custody_code(self) -> None:
        """Split S-3, as far as it can honestly be proven at S-1.

        A direct arm invocation must refuse an unpublished family without the
        scheduler's help.  Three legs are proven here behaviourally:

        1. the gate ENGAGES from the tracked registry roster and refuses
           ``marker_absent`` when a roster pack has no marker (deleting the
           marker refuses; it does not disengage);
        2. the refusal record the arm and verification paths append is the
           registry's own FAMILY_PUBLICATION entry -- the typed CUSTODY code
           ``readiness_r1_family_publication``, not an improvised string; and
        3. both library entry points call the gate, and neither imports the
           scheduler.

        NOT proven here: the full end-to-end arm receipt carrying that code,
        which needs the three `_v5` packs (unbuilt until desk day).  Recorded as an
        open item in the S-1 manifest rather than papered over.
        """

        registry, _raw = readiness.load_registry(ROOT)
        self.assertEqual(
            readiness._family_refusal_entry(registry),
            {
                "role": "FAMILY_PUBLICATION",
                "code": "readiness_r1_family_publication",
                "type": "CUSTODY",
            },
        )
        self.assertEqual(
            readiness.REASON_TYPE_BY_CODE["readiness_r1_family_publication"],
            "CUSTODY",
        )
        registry_value = json.loads(
            (ROOT / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes()
        )
        with (
            mock.patch.object(readiness, "_repo_for_pack", return_value=ROOT),
            mock.patch.object(
                readiness,
                "load_registry",
                return_value=(
                    registry_value,
                    readiness.render_json(registry_value),
                ),
            ),
        ):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._gate_family_publication(
                    Path("d117_floor_qwen3-1p7b_v5"),
                    marker_path=None,
                    confirmation_path=None,
                )
        self.assertEqual(caught.exception.check_id, "marker_absent")

    def test_candidate_cli_refuses_absent_marker_without_traceback(self) -> None:
        help_result = subprocess.run(
            ("python3", "scripts/verify_family_marker.py", "--help"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("--expected-confirmation-digest", help_result.stdout)
        completed = subprocess.run(
            (
                "python3", "scripts/verify_family_marker.py", "--repository", ".",
                "--marker", "/definitely/absent/d117_family_publication_v5.json",
            ),
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertNotIn(b"Traceback", completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["lane"], "candidate")
        self.assertEqual(result["family_id"], "d117-v5")
        self.assertFalse(result["gate_admissible"])
        self.assertEqual(result["checks"], [{"check_id": "marker_absent", "status": "REFUSE"}])

    def test_candidate_cli_refusal_branches_report_v5(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "verify_family_marker_refusal_test",
            ROOT / "scripts/verify_family_marker.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        cases = (
            readiness.FamilyPublicationError("marker_absent", "absent marker"),
            readiness.ArmReadinessError(
                "readiness_row_registry_mismatch", "invalid registry"
            ),
        )
        for error in cases:
            with self.subTest(error=type(error).__name__):
                buffer = io.BytesIO()
                stdout = mock.Mock(buffer=buffer)
                with (
                    mock.patch.object(
                        module.readiness,
                        "verify_family_publication_marker",
                        side_effect=error,
                    ),
                    mock.patch.object(module.sys, "stdout", stdout),
                ):
                    code = module.main(
                        [
                            "--repository",
                            ".",
                            "--marker",
                            "/definitely/absent/marker.json",
                        ]
                    )
                self.assertEqual(code, 2)
                self.assertEqual(
                    json.loads(buffer.getvalue())["family_id"], "d117-v5"
                )

    def test_tool_hash_lane_is_phase_selected_and_neither_mode_is_bypassable(self) -> None:
        """Split S-5, behaviourally.

        Production mode must accept only the blob committed at the head under
        test, and candidate mode must accept only the bytes the reviewed $INPUT
        manifest recorded.  A modified tool must fail BOTH -- in particular it
        must not be able to authenticate itself by writing its own sidecar,
        which is what the previous implementation permitted.
        """

        relative = "scripts/verify_family_marker.py"
        head = subprocess.run(
            ("git", "-C", str(ROOT), "rev-parse", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        # Source the production expectation from the committed blob, not the
        # working tree: the two differ during any edit of this very tool.
        committed = subprocess.run(
            ("git", "-C", str(ROOT), "show", f"{head}:{relative}"),
            check=True,
            capture_output=True,
        ).stdout
        modified = committed + b"\n# tampered\n"
        with tempfile.TemporaryDirectory() as temporary:
            staging = Path(temporary)
            honest = staging / "verify_family_marker.py"
            honest.write_bytes(committed)
            tampered = staging / "tampered" / "verify_family_marker.py"
            tampered.parent.mkdir()
            tampered.write_bytes(modified)

            def manifest(directory: Path, digest: str) -> Path:
                path = directory / readiness.S0_CANDIDATE_MANIFEST_NAME
                path.write_text(
                    json.dumps({"custody_tools": {relative: digest}}),
                    encoding="utf-8",
                )
                return path

            reviewed = manifest(staging, readiness.sha256_bytes(committed))
            # A sidecar that agrees with the tampered bytes -- the exact
            # self-authentication the old implementation accepted.
            tampered.with_name(f"{tampered.name}.sha256").write_bytes(
                readiness.gnu_sidecar(readiness.sha256_bytes(modified), tampered.name)
            )
            forged = manifest(tampered.parent, readiness.sha256_bytes(modified))

            # Candidate mode: honest bytes PASS against the reviewed manifest.
            self.assertEqual(
                readiness._family_tool_reference(
                    ROOT, head, relative, honest,
                    phase="candidate", candidate_manifest=reviewed,
                ),
                {"path": relative, "sha256": readiness.sha256_bytes(committed)},
            )
            # Candidate mode: tampered bytes REFUSE against the reviewed
            # manifest, sidecar notwithstanding.
            for label, executing, table in (
                ("tampered tool vs reviewed manifest", tampered, reviewed),
                ("honest tool vs forged manifest", honest, forged),
            ):
                with self.subTest(case=label):
                    with self.assertRaises(readiness.FamilyPublicationError) as caught:
                        readiness._family_tool_reference(
                            ROOT, head, relative, executing,
                            phase="candidate", candidate_manifest=table,
                        )
                    self.assertEqual(caught.exception.check_id, "tool_mismatch")

            # Production mode: committed blob PASSES; tampered bytes REFUSE
            # even with a self-agreeing sidecar and a forged manifest beside it.
            for phase in ("publication", "pre-arm", "t0"):
                with self.subTest(phase=phase):
                    self.assertEqual(
                        readiness._family_tool_reference(
                            ROOT, head, relative, honest, phase=phase,
                        )["sha256"],
                        readiness.sha256_bytes(committed),
                    )
                    with self.assertRaises(readiness.FamilyPublicationError) as caught:
                        readiness._family_tool_reference(
                            ROOT, head, relative, tampered,
                            phase=phase, candidate_manifest=forged,
                        )
                    self.assertEqual(caught.exception.check_id, "tool_mismatch")
                    self.assertIn("committed at the reviewed head", str(caught.exception))

            # An unknown lane is refused rather than defaulted.
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._family_tool_reference(
                    ROOT, head, relative, honest, phase="production",
                )
            self.assertEqual(caught.exception.check_id, "lane_inadmissible")

        for path in (ROOT / "scripts/build_family_marker.py", ROOT / "scripts/verify_family_marker.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in ("--force", "--skip", "--allow", "--no-verify", "os.environ"):
                self.assertNotIn(forbidden, text)

    def test_builder_interface_is_runsheet_exact_and_output_is_external(self) -> None:
        completed = subprocess.run(
            ("python3", "scripts/build_family_marker.py", "--help"),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        for option in ("--repository", "--head", "--pack-root", "--output"):
            self.assertIn(option, completed.stdout)


    def test_custody_tool_sidecars_exist_and_are_current(self) -> None:
        """Gap G-1: the kernel row's named sidecar deliverables.

        A sidecar committed beside its tool is documentation, not a gate -- the
        S-5 lane is chosen by phase, and candidate mode authenticates against
        the reviewed $INPUT manifest, so nothing downstream reads these files.
        They exist because S-0 runsheet 1.3 runs `shasum -a 256 -c` on them.
        This test is what stops them going stale: the reviewed refresh lane,
        rather than a hand `shasum`, owns both the set and exact regeneration
        format.
        """

        lane = refresh_lane_module()
        ruled_names = {
            "build_family_marker.py",
            "verify_family_marker.py",
            "build_v4_histsem_pinset.py",
            "verify_receipt_histsem.py",
        }
        self.assertTrue(ruled_names.issubset(set(lane.CUSTODY_TOOL_SIDECARS)))
        self.assertEqual(
            len(lane.CUSTODY_TOOL_SIDECARS),
            len(set(lane.CUSTODY_TOOL_SIDECARS)),
        )
        self._assert_custody_tool_sidecars_current(ROOT, lane)

        # The lane's own sidecar uses the identical renderer but is not in the
        # CLI-owned set: self-rewriting plus the dirty-path refusal would need
        # two commits and could not be idempotent inside one reviewed change.
        name = REFRESH_SCRIPT.name
        self.assertNotIn(name, lane.CUSTODY_TOOL_SIDECARS)
        self.assertEqual(
            REFRESH_SCRIPT.with_name(f"{name}.sha256").read_bytes(),
            lane.render_tool_sidecar(REFRESH_SCRIPT.read_bytes(), name),
        )

    def test_custody_tool_sidecar_tripwire_has_an_independent_oracle(self) -> None:
        lane = refresh_lane_module()
        with tempfile.TemporaryDirectory() as temporary:
            scratch = Path(temporary)
            scripts = scratch / "scripts"
            scripts.mkdir()
            for name in lane.CUSTODY_TOOL_SIDECARS:
                (scripts / name).write_bytes((ROOT / "scripts" / name).read_bytes())
                (scripts / f"{name}.sha256").write_bytes(b"WRONG\n")
            with (
                mock.patch.object(lane, "render_tool_sidecar", return_value=b"WRONG\n"),
                self.assertRaises(AssertionError),
            ):
                self._assert_custody_tool_sidecars_current(scratch, lane)


class FamilyMarkerLiveFixtureTests(unittest.TestCase):
    """Gap G-7: exercise the verifier against a REAL repository.

    Every other test in this file hands the verifier dictionaries.  This class
    builds an actual Git repository with the tracked v2 registry committed,
    ``HEAD == refs/heads/main == refs/remotes/origin/main``, a clean tree, and
    a real marker file with a real GNU sidecar in custody OUTSIDE that
    repository -- then walks a tamper ladder through the verifier's own code.

    What it does NOT cover, honestly: the three `_v5` packs do not exist until
    desk day mints them, so the member-replay leg (``pack_digest_mismatch``,
    ``freeze_binding_mismatch``, ``evidence_set_mismatch``) is reached but its
    PASS direction cannot be observed here.  That first observation belongs to
    S-0 and must be transcribed there.
    """

    def fixture_repository(self, base: Path) -> tuple[Path, Path]:
        repository = base / "repository"
        custody = base / "custody"
        (repository / "configs/arm_readiness").mkdir(parents=True)
        custody.mkdir(exist_ok=True)
        registry_relative = readiness.ROW_REGISTRY_RELATIVE_PATH.as_posix()
        (repository / registry_relative).write_bytes(
            (ROOT / registry_relative).read_bytes()
        )
        for command in (
            ("init", "-q"),
            ("config", "user.email", "test@example.invalid"),
            ("config", "user.name", "S1 Finish Round"),
            ("checkout", "-q", "-B", "main"),
            ("add", "."),
            ("commit", "-qm", "install reviewed registry"),
        ):
            subprocess.run(
                ("git", "-C", str(repository), *command),
                check=True, capture_output=True,
            )
        head = subprocess.run(
            ("git", "-C", str(repository), "rev-parse", "HEAD"),
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        subprocess.run(
            ("git", "-C", str(repository), "update-ref",
             "refs/remotes/origin/main", head),
            check=True, capture_output=True,
        )
        return repository, custody

    def live_marker(self, repository: Path) -> dict[str, object]:
        live = readiness.reviewed_main(repository)
        self.assertIs(live["exact_match"], True, "fixture must be four-way exact")
        registry_raw = (
            repository / readiness.ROW_REGISTRY_RELATIVE_PATH
        ).read_bytes()
        value = marker()
        value["publication_git"] = dict(live)
        value["terminal_review"]["head_tree_oid"] = live["head_tree_oid"]
        value["authoring_context"]["transaction_id"] = f"d117-v5@{live['head_commit']}"
        value["lifecycle_registry"]["sha256"] = readiness.sha256_bytes(registry_raw)
        return value

    def write_marker(self, custody: Path, value: object, *, sidecar: bytes | None = None) -> Path:
        path = custody / readiness.FAMILY_PUBLICATION_MARKER_NAME
        raw = readiness.render_json(value) if not isinstance(value, bytes) else value
        path.write_bytes(raw)
        path.with_name(f"{path.name}.sha256").write_bytes(
            sidecar
            if sidecar is not None
            else readiness.gnu_sidecar(readiness.sha256_bytes(raw), path.name)
        )
        return path

    def published_artifacts(
        self, repository: Path, custody: Path
    ) -> tuple[dict[str, object], Path, Path, str, dict[str, object]]:
        value = self.live_marker(repository)
        live = readiness.reviewed_main(repository)
        value["common_evidence_git"] = {
            "head_commit": live["head_commit"],
            "head_tree_oid": live["head_tree_oid"],
        }
        marker_path = self.write_marker(custody, value)
        table = confirmation(readiness.sha256_bytes(marker_path.read_bytes()))
        table["git"] = {
            "head_commit": live["head_commit"],
            "head_tree_oid": live["head_tree_oid"],
        }
        table["registry"]["sha256"] = value["lifecycle_registry"]["sha256"]
        table["family_publication"]["members"] = [
            {
                "profile": item["profile"],
                "pack_id": item["pack_id"],
                "pack_sha256": item["pack_sha256"],
                "freeze_receipt_sha256": item["freeze_receipt"]["sha256"],
            }
            for item in value["members"]
        ]
        table_path = custody / readiness.STEP6_CONFIRMATION_TABLE_NAME
        table_raw = readiness.render_json(table)
        table_path.write_bytes(table_raw)
        table_path.with_name(f"{table_path.name}.sha256").write_bytes(
            readiness.gnu_sidecar(
                readiness.sha256_bytes(table_raw), table_path.name
            )
        )
        for item in value["members"]:
            (repository / str(item["pack_path"])).mkdir(parents=True, exist_ok=True)
        by_id = {str(item["pack_id"]): item for item in value["members"]}
        return (
            value,
            marker_path,
            table_path,
            readiness.sha256_bytes(table_raw),
            by_id,
        )

    def verify(self, repository: Path, marker_path: Path):
        return readiness.verify_family_publication_marker(
            repository, marker_path, phase="candidate"
        )

    def refusal(self, repository: Path, marker_path: Path) -> str:
        with self.assertRaises(readiness.FamilyPublicationError) as caught:
            self.verify(repository, marker_path)
        return caught.exception.check_id

    def test_published_verifier_requires_and_authenticates_out_of_band_digest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository, custody = self.fixture_repository(Path(temporary))
            value, marker_path, table_path, table_digest, by_id = (
                self.published_artifacts(repository, custody)
            )
            common_head = str(value["common_evidence_git"]["head_commit"])

            def replay(
                _repository,
                root,
                _registry,
                _reference,
                *,
                conditional_deferral=None,
                **_kwargs,
            ):
                # The stub stands in for a member evaluation on a repository
                # whose successor pinset HAS been minted, which is the state the
                # fixture marker's disclosure declares.  Honouring the ledger
                # here is also the assertion that the candidate lane hands the
                # replay a live deferral and every other lane hands it None.
                if conditional_deferral is not None:
                    for path in readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS:
                        conditional_deferral.record(path)
                return copy.deepcopy(by_id[root.name]), {common_head}

            with mock.patch.object(readiness, "_family_member", side_effect=replay):
                # Candidate lane remains independent of C and hC.
                candidate = readiness.verify_family_publication_marker(
                    repository, marker_path, phase="candidate"
                )
                self.assertFalse(candidate["gate_admissible"])

                for label, expected, check_id in (
                    (
                        "self-consistent ED/YES table without hC",
                        None,
                        "confirmation_missing",
                    ),
                    ("wrong hC", "0" * 64, "confirmation_mismatch"),
                ):
                    with self.subTest(case=label):
                        with self.assertRaises(
                            readiness.FamilyPublicationError
                        ) as caught:
                            readiness.verify_family_publication_marker(
                                repository,
                                marker_path,
                                phase="publication",
                                confirmation_path=table_path,
                                expected_confirmation_digest=expected,
                            )
                        self.assertEqual(caught.exception.check_id, check_id)

                verified = readiness.verify_family_publication_marker(
                    repository,
                    marker_path,
                    phase="publication",
                    confirmation_path=table_path,
                    expected_confirmation_digest=table_digest,
                )
                self.assertTrue(verified["gate_admissible"])
                self.assertEqual(
                    verified["confirmation"]["sha256"], table_digest
                )

                malformed = json.loads(table_path.read_bytes())
                malformed["transaction_id"] = []
                malformed_raw = readiness.render_json(malformed)
                table_path.write_bytes(malformed_raw)
                table_path.with_name(f"{table_path.name}.sha256").write_bytes(
                    readiness.gnu_sidecar(
                        readiness.sha256_bytes(malformed_raw), table_path.name
                    )
                )
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.verify_family_publication_marker(
                        repository,
                        marker_path,
                        phase="publication",
                        confirmation_path=table_path,
                        expected_confirmation_digest=readiness.sha256_bytes(
                            malformed_raw
                        ),
                    )
                self.assertEqual(
                    caught.exception.check_id, "confirmation_mismatch"
                )

    def test_library_gate_requires_and_authenticates_out_of_band_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository, custody = self.fixture_repository(Path(temporary))
            value, marker_path, table_path, table_digest, by_id = (
                self.published_artifacts(repository, custody)
            )
            common_head = str(value["common_evidence_git"]["head_commit"])
            target = repository / str(value["members"][0]["pack_path"])

            def replay(
                _repository,
                root,
                _registry,
                _reference,
                *,
                conditional_deferral=None,
                **_kwargs,
            ):
                # The stub stands in for a member evaluation on a repository
                # whose successor pinset HAS been minted, which is the state the
                # fixture marker's disclosure declares.  Honouring the ledger
                # here is also the assertion that the candidate lane hands the
                # replay a live deferral and every other lane hands it None.
                if conditional_deferral is not None:
                    for path in readiness.R1_DIGEST_CONDITIONAL_ALLOWLIST_PATHS:
                        conditional_deferral.record(path)
                return copy.deepcopy(by_id[root.name]), {common_head}

            with mock.patch.object(readiness, "_family_member", side_effect=replay):
                for label, expected, check_id in (
                    ("digest absent", None, "confirmation_missing"),
                    ("digest wrong", "0" * 64, "confirmation_mismatch"),
                ):
                    with self.subTest(case=label):
                        with self.assertRaises(
                            readiness.FamilyPublicationError
                        ) as caught:
                            readiness._gate_family_publication(
                                target,
                                marker_path=marker_path,
                                confirmation_path=table_path,
                                expected_confirmation_digest=expected,
                            )
                        self.assertEqual(caught.exception.check_id, check_id)

                self.assertIsNone(
                    readiness._gate_family_publication(
                        target,
                        marker_path=marker_path,
                        confirmation_path=table_path,
                        expected_confirmation_digest=table_digest,
                    )
                )

    def test_live_fixture_tamper_ladder_reaches_each_specific_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository, custody = self.fixture_repository(Path(temporary))
            value = self.live_marker(repository)
            marker_path = self.write_marker(custody, value)

            # The honest marker gets all the way to member replay, which is the
            # first check that needs the unbuilt _v5 packs.
            self.assertEqual(
                self.refusal(repository, marker_path), "plan_binding_mismatch"
            )

            # Marker absent from custody.
            absent = custody / "nowhere" / readiness.FAMILY_PUBLICATION_MARKER_NAME
            self.assertEqual(self.refusal(repository, absent), "marker_absent")

            # Marker inside the repository is refused before it is even read --
            # custody-externality is what keeps the changed set at 112.
            in_tree = repository / readiness.FAMILY_PUBLICATION_MARKER_NAME
            in_tree.write_bytes(marker_path.read_bytes())
            self.assertEqual(self.refusal(repository, in_tree), "marker_unreadable")
            in_tree.unlink()

            # Bytes disagreeing with their own sidecar now have their own
            # diagnostic instead of the vaguer marker_unreadable (gap G-5).
            self.write_marker(
                custody,
                value,
                sidecar=readiness.gnu_sidecar(
                    "0" * 64, readiness.FAMILY_PUBLICATION_MARKER_NAME
                ),
            )
            self.assertEqual(
                self.refusal(repository, marker_path), "marker_self_digest_mismatch"
            )

            # Noncanonical JSON.
            self.write_marker(custody, b'{ "schema_version": "x" }\n')
            self.assertEqual(
                self.refusal(repository, marker_path), "marker_noncanonical"
            )

            # Registry digest that is not the committed registry's.
            stale = copy.deepcopy(value)
            stale["lifecycle_registry"]["sha256"] = digest("stale-registry")
            self.write_marker(custody, stale)
            self.assertEqual(
                self.refusal(repository, marker_path), "registry_mismatch"
            )

            # Dirty tree.
            self.write_marker(custody, value)
            (repository / "scratch.txt").write_text("dirty\n")
            self.assertEqual(self.refusal(repository, marker_path), "worktree_dirty")
            (repository / "scratch.txt").unlink()
            self.assertEqual(
                self.refusal(repository, marker_path), "plan_binding_mismatch"
            )

    def test_builder_refuses_in_tree_output_and_collision_when_executed(self) -> None:
        """Gap G-8 item 7: execute the builder, do not grep it.

        Custody-externality and create-only are the two properties that keep
        the marker from touching the 112-path changed-set contract.  Both are
        asserted here against a real run of the CLI, and the repository is
        checked to be untouched afterwards -- the mechanical proof that
        building a marker cannot change the changed set.
        """

        with tempfile.TemporaryDirectory() as temporary:
            repository, _custody = self.fixture_repository(Path(temporary))
            before = subprocess.run(
                ("git", "-C", str(repository), "status", "--porcelain"),
                check=True, capture_output=True, text=True,
            ).stdout
            in_tree = repository / "marker.json"
            completed = subprocess.run(
                (
                    "python3", str(ROOT / "scripts/build_family_marker.py"),
                    "--repository", str(repository),
                    "--head", "0" * 40,
                    "--pack-root", "configs/campaigns/d117_floor_qwen3-1p7b_v5",
                    "--output", str(in_tree),
                ),
                check=False, capture_output=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertNotIn(b"Traceback", completed.stderr)
            self.assertEqual(
                json.loads(completed.stdout)["check_id"], "output_in_tree"
            )
            self.assertFalse(in_tree.exists())

            external = Path(temporary) / "custody" / "marker.json"
            external.parent.mkdir(parents=True, exist_ok=True)
            external.write_text("{}")
            collided = subprocess.run(
                (
                    "python3", str(ROOT / "scripts/build_family_marker.py"),
                    "--repository", str(repository),
                    "--head", "0" * 40,
                    "--pack-root", "configs/campaigns/d117_floor_qwen3-1p7b_v5",
                    "--output", str(external),
                ),
                check=False, capture_output=True,
            )
            self.assertEqual(collided.returncode, 2)
            self.assertEqual(
                json.loads(collided.stdout)["check_id"], "output_collision"
            )
            self.assertEqual(external.read_text(), "{}")

            after = subprocess.run(
                ("git", "-C", str(repository), "status", "--porcelain"),
                check=True, capture_output=True, text=True,
            ).stdout
            self.assertEqual(before, after, "a marker build must not touch the tree")

    def test_rollback_falsifier_old_published_head_is_refused(self) -> None:
        """Gap G-8 item 3 -- the refuter that DECIDED split S-1.

        A marker built at a genuinely published head stays valid forever under
        an ancestry rule: check out that old head after origin advances and it
        is trivially an ancestor of both HEAD and origin/main.  Strict four-way
        equality is what forbids it.  This is that scenario, executed.
        """

        with tempfile.TemporaryDirectory() as temporary:
            repository, custody = self.fixture_repository(Path(temporary))
            value = self.live_marker(repository)
            marker_path = self.write_marker(custody, value)
            old_head = value["publication_git"]["head_commit"]

            # The marker is valid at the head it was built at: it survives the
            # Git legs and refuses only at the unbuilt member replay.
            self.assertEqual(
                self.refusal(repository, marker_path), "plan_binding_mismatch"
            )

            # origin/main advances; the worktree is checked out at the OLD
            # published head, which remains an ancestor of the new origin/main.
            (repository / "later.txt").write_text("published later\n")
            for command in (
                ("add", "."),
                ("commit", "-qm", "advance origin"),
            ):
                subprocess.run(
                    ("git", "-C", str(repository), *command),
                    check=True, capture_output=True,
                )
            new_head = subprocess.run(
                ("git", "-C", str(repository), "rev-parse", "HEAD"),
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(
                ("git", "-C", str(repository), "update-ref",
                 "refs/remotes/origin/main", new_head),
                check=True, capture_output=True,
            )
            subprocess.run(
                ("git", "-C", str(repository), "reset", "-q", "--hard", old_head),
                check=True, capture_output=True,
            )
            # Ancestry would admit this: the old head IS an ancestor of the new
            # origin/main. Equality refuses it, with the rollback's own id.
            ancestry = subprocess.run(
                ("git", "-C", str(repository), "merge-base", "--is-ancestor",
                 old_head, new_head),
                check=False, capture_output=True,
            )
            self.assertEqual(
                ancestry.returncode, 0, "fixture must reproduce the ancestry trap"
            )
            self.assertEqual(
                self.refusal(repository, marker_path), "head_unpublished"
            )



class ConditionalDeferralDisclosureTests(unittest.TestCase):
    """S0-O2: the marker BUILD lane defers the C -> S condition and says so.

    Background, in the order a reader needs it.  The step-6 confirmation table
    ``C`` carries the marker's own digest ``hM``
    (``docs/contracts/d117_step6_confirmation_table.md``, "Acyclic digest
    graph"), so ``C`` cannot exist until after the marker bytes exist.  The R1
    changed-set gate the marker build replays nevertheless reaches the
    digest-conditional allowlist path -- the successor histsem pinset -- as soon
    as that pinset has been minted into the changed set, and that gate demands
    ``C``.  Marker BUILD therefore evaluated a condition it could not satisfy at
    any head, which is why estate 5 refused at runsheet r4 section 3.8 with
    ``evidence_set_mismatch`` / "no expected confirmation digest supplied".

    The cure is suppression WITH disclosure: build (both phases) and the
    candidate-lane replay treat the conditional path as discharged for that
    evaluation and record it in the marker's ``conditional_paths_deferred``
    field, naming the path and the four entry points that still enforce it.
    These tests hold each half in place -- the suppression works, and nothing
    that used to enforce stopped enforcing.
    """

    SUCCESSOR = readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix()

    def minted_successor_repository(self) -> tuple[Path, dict, dict, dict, str]:
        """A repository whose successor pinset IS in the R1 changed set.

        This is the state that made the build unsatisfiable: the evidence
        receipt derives from a commit before the mint, and the mint commit is
        the reviewed HEAD, so the conditional allowlist path is outstanding.
        """

        from tests.test_arm_readiness_evidence import (
            content_source_and_receipt,
            lifecycle_registry,
            plan_tree,
        )

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        repository = Path(temporary.name) / "repository"
        repository.mkdir()

        def git(*args: str) -> str:
            return subprocess.run(
                ("git", "-C", str(repository), *args),
                check=True, capture_output=True, text=True,
            ).stdout.strip()

        git("init", "-q")
        git("config", "user.email", "test@example.invalid")
        git("config", "user.name", "S0-O2 cure")
        (repository / "dependency.txt").write_text("stable\n")
        (repository / "pack").mkdir()
        (repository / "pack/plan_tree.json").write_bytes(plan_tree(frozen=False))
        git("add", ".")
        git("commit", "-qm", "derivation")
        derivation = git("rev-parse", "HEAD")
        source, receipt = content_source_and_receipt(repository, derivation)
        registry = lifecycle_registry(allowlist=(self.SUCCESSOR,))
        registry["successor_policy"]["family_publication_first_generation"] = 5
        successor = repository / self.SUCCESSOR
        successor.parent.mkdir(parents=True, exist_ok=True)
        successor.write_bytes(b'{"packs": []}\n')
        git("add", self.SUCCESSOR)
        git("commit", "-qm", "mint successor pinset")
        return repository, registry, source, receipt, git("rev-parse", "HEAD")

    def family_member_over_the_real_gate(
        self, repository: Path, registry, source, receipt, head: str, deferral
    ):
        """Run ``_family_member`` with the REAL R1 gate under its freeze replay.

        ``_family_member``'s two replay call sites are stubbed only far enough
        to reach the gate with the confirmation arguments they were handed, so
        what is exercised here is the actual supply line the estate hit.
        """

        def gate(**kwargs) -> None:
            readiness.validate_r1_evidence_lifecycle(
                repository,
                receipt,
                source,
                registry,
                current_head=head,
                expected_freshness_class="RE_DERIVABLE",
                plan_tree_path="pack/plan_tree.json",
                step6_confirmation_table=kwargs.get("step6_confirmation_table"),
                expected_confirmation_digest=kwargs.get(
                    "expected_confirmation_digest"
                ),
                conditional_deferral=kwargs.get("conditional_deferral"),
            )

        freeze = {
            "schema_version": readiness.FREEZE_RECEIPT_V2_SCHEMA,
            "receipt_id": "freeze-0004",
            "status": "PASS",
            "pack_identity": {"plan_path": "calibration_plan.json"},
        }

        def load_freeze_reference(*_args, **kwargs):
            gate(**kwargs)
            return freeze, {"path": "arm_readiness.freeze.receipts/freeze-0004.json"}

        def freeze_evidence_for_arm(*_args, **kwargs):
            gate(**kwargs)
            return [], {}

        with (
            mock.patch.object(readiness, "_plan_profile", return_value="ALPHA"),
            mock.patch.object(readiness, "_plan_tree", return_value=({}, b"{}\n")),
            mock.patch.object(
                readiness, "_load_freeze_reference", side_effect=load_freeze_reference
            ),
            mock.patch.object(
                readiness,
                "_freeze_evidence_for_arm",
                side_effect=freeze_evidence_for_arm,
            ),
        ):
            with self.assertRaises(readiness.FamilyPublicationError) as caught:
                readiness._family_member(
                    repository,
                    repository / "pack",
                    registry,
                    {"plan_profile": "ALPHA"},
                    conditional_deferral=deferral,
                )
        return caught.exception

    def test_uncured_family_member_reproduces_the_estate_five_refusal(self) -> None:
        """RED: the pre-cure supply line, exactly as the estate observed it.

        ``conditional_deferral=None`` is what ``build_family_publication_marker``
        used to pass unconditionally.  The refusal reproduced here -- check id
        ``evidence_set_mismatch``, detail naming the digest-conditional path and
        the absent expected digest -- is the estate-5 transcript 081 signature.
        """

        repository, registry, source, receipt, head = (
            self.minted_successor_repository()
        )
        exception = self.family_member_over_the_real_gate(
            repository, registry, source, receipt, head, None
        )
        self.assertEqual(exception.check_id, "evidence_set_mismatch")
        self.assertIn("digest-conditional allowlist path", str(exception))
        self.assertIn(self.SUCCESSOR, str(exception))
        self.assertIn("no expected confirmation digest supplied", str(exception))

    def test_cured_family_member_passes_the_gate_and_ledgers_the_path(self) -> None:
        """GREEN: with a deferral the same fixture clears the changed-set gate.

        The call still ends in a refusal, but a LATER one: ``plan_binding_``
        ``mismatch`` is the next check after the freeze replay, and it needs the
        real ``_v5`` pack files that only desk day mints.  What matters is that the
        changed-set refusal is gone and the ledger names the deferred path.
        """

        repository, registry, source, receipt, head = (
            self.minted_successor_repository()
        )
        deferral = readiness.R1ConditionalDeferral()
        exception = self.family_member_over_the_real_gate(
            repository, registry, source, receipt, head, deferral
        )
        self.assertEqual(exception.check_id, "plan_binding_mismatch")
        self.assertNotIn("digest-conditional", str(exception))
        self.assertEqual(deferral.deferred_paths, (self.SUCCESSOR,))

    def test_build_defers_in_both_phases_and_verify_only_in_candidate(self) -> None:
        """The lane rule, read off the two entry points' own call sites.

        Marker BUILD is not one of the contract's four enforcement entry points
        in EITHER phase, so both phases hand the member replay a live ledger.
        Marker REPLAY is one of them, so only its candidate lane -- which by
        construction has no table either -- gets a ledger; publication, pre-arm
        and t0 get ``None`` and enforce the condition for real.
        """

        recorded: list[object] = []

        def probe(*_args, conditional_deferral=None, **_kwargs):
            recorded.append(conditional_deferral)
            raise readiness.FamilyPublicationError("roster_mismatch", "probe")

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            live = FamilyMarkerLiveFixtureTests()
            repository, custody = live.fixture_repository(base)
            registry = json.loads(
                (repository / readiness.ROW_REGISTRY_RELATIVE_PATH).read_bytes()
            )
            roster = registry["freeze_evidence_lifecycle"]["successor_policy"][
                "successor_pack_ids"
            ]
            pack_roots = []
            for pack_id in roster.values():
                root = repository / "configs/campaigns" / pack_id
                root.mkdir(parents=True, exist_ok=True)
                pack_roots.append(root)
            head = readiness.reviewed_main(repository)["head_commit"]

            with (
                mock.patch.object(readiness, "_family_member", side_effect=probe),
                mock.patch.object(readiness, "_plan_profile", return_value="ALPHA"),
            ):
                for phase in ("candidate", "publication"):
                    with self.subTest(entry_point="build", phase=phase):
                        recorded.clear()
                        with self.assertRaises(readiness.FamilyPublicationError):
                            readiness.build_family_publication_marker(
                                repository,
                                head,
                                pack_roots,
                                base / "out" / f"{phase}.json",
                                builder_tool=ROOT / "scripts/build_family_marker.py",
                                consumer_tool=ROOT / "scripts/verify_family_marker.py",
                                phase=phase,
                            )
                        self.assertTrue(recorded)
                        self.assertIsInstance(
                            recorded[0], readiness.R1ConditionalDeferral
                        )

            value, marker_path, table_path, table_digest, _by_id = (
                live.published_artifacts(repository, custody)
            )
            with mock.patch.object(readiness, "_family_member", side_effect=probe):
                for phase, expects_ledger in (
                    ("candidate", True),
                    ("publication", False),
                    ("pre-arm", False),
                    ("t0", False),
                ):
                    with self.subTest(entry_point="replay", phase=phase):
                        recorded.clear()
                        with self.assertRaises(readiness.FamilyPublicationError):
                            readiness.verify_family_publication_marker(
                                repository,
                                marker_path,
                                phase=phase,
                                confirmation_path=(
                                    None if phase == "candidate" else table_path
                                ),
                                expected_confirmation_digest=(
                                    None if phase == "candidate" else table_digest
                                ),
                            )
                        self.assertTrue(recorded)
                        if expects_ledger:
                            self.assertIsInstance(
                                recorded[0], readiness.R1ConditionalDeferral
                            )
                        else:
                            self.assertIsNone(recorded[0])

    def test_disclosure_field_is_exact_and_cannot_launder_a_path(self) -> None:
        """The published field is governed, not free-form.

        A marker that named an arbitrary repository path here would be claiming
        the changed-set gate had been waived for it.  The validator accepts only
        the fixed gate id, the fixed entry-point list, and a sorted duplicate-free
        subset of the code-enumerated conditional class.
        """

        value = marker()
        self.assertEqual(
            readiness.validate_family_publication_marker(value, first_generation=5),
            value,
        )

        empty = marker()
        empty["conditional_paths_deferred"]["deferred_paths"] = []
        self.assertEqual(
            readiness.validate_family_publication_marker(empty, first_generation=5),
            empty,
        )

        laundered = marker()
        laundered["conditional_paths_deferred"]["deferred_paths"] = [
            "joulewise/arm_readiness.py"
        ]
        wrong_gate = marker()
        wrong_gate["conditional_paths_deferred"]["gate"] = "R1_ANYTHING"
        wrong_entry_points = marker()
        wrong_entry_points["conditional_paths_deferred"][
            "enforced_at_entry_points"
        ] = ["arm"]
        duplicated = marker()
        duplicated["conditional_paths_deferred"]["deferred_paths"] = [
            self.SUCCESSOR,
            self.SUCCESSOR,
        ]
        unknown_key = marker()
        unknown_key["conditional_paths_deferred"]["waived"] = True
        absent = marker()
        absent.pop("conditional_paths_deferred")
        for label, candidate in (
            ("path outside the conditional class", laundered),
            ("wrong gate id", wrong_gate),
            ("truncated entry-point list", wrong_entry_points),
            ("duplicated path", duplicated),
            ("unknown key", unknown_key),
            ("field absent entirely", absent),
        ):
            with self.subTest(case=label):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.validate_family_publication_marker(
                        candidate, first_generation=5
                    )
                self.assertEqual(caught.exception.check_id, "marker_schema_mismatch")

    def test_malformed_disclosure_elements_refuse_instead_of_raising_typeerror(
        self,
    ) -> None:
        """Refuter round F1: shape is proven before the list is ever ordered.

        ``sorted()`` and ``dict.fromkeys()`` raise ``TypeError`` on a
        heterogeneous or unhashable list -- ``[1, "a"]`` compares int to str,
        ``[[]]`` is unhashable.  ``TypeError`` is NOT one of the exception types
        ``scripts/verify_family_marker.py`` catches, so an ordering check placed
        before the element type check let a malformed marker escape the governed
        refusal boundary as a traceback.  Every element must therefore be proven
        to be a ``str`` first.

        The end-to-end half of this test is what actually matters: the CLI must
        emit a structured REFUSE document, because that is the artifact an
        operator reads and a transcript records.
        """

        for label, value in (
            ("mixed int and str", [1, "a"]),
            ("ints only", [2, 1]),
            ("unhashable element", [[]]),
            ("bool element", [True]),
            ("not a list at all", "configs/x.json"),
            ("mapping instead of list", {"a": 1}),
        ):
            with self.subTest(case=label):
                candidate = marker()
                candidate["conditional_paths_deferred"]["deferred_paths"] = value
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.validate_family_publication_marker(
                        candidate, first_generation=5
                    )
                self.assertEqual(caught.exception.check_id, "marker_schema_mismatch")

        # End to end through the consumer CLI: a REFUSE document on stdout and a
        # nonzero exit, never a traceback on stderr.
        with tempfile.TemporaryDirectory() as temporary:
            live = FamilyMarkerLiveFixtureTests()
            repository, custody = live.fixture_repository(Path(temporary))
            value = live.live_marker(repository)
            value["conditional_paths_deferred"]["deferred_paths"] = [1, "a"]
            marker_path = live.write_marker(custody, value)
            completed = subprocess.run(
                (
                    sys.executable,
                    str(ROOT / "scripts/verify_family_marker.py"),
                    "--repository", str(repository),
                    "--marker", str(marker_path),
                    "--phase", "candidate",
                ),
                capture_output=True, text=True,
            )
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertNotIn("TypeError", completed.stderr)
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["status"], "REFUSE")
        self.assertEqual(
            [check["check_id"] for check in receipt["checks"]],
            ["marker_schema_mismatch"],
        )

    def test_candidate_replay_refuses_a_disclosure_it_did_not_reproduce(self) -> None:
        """The candidate lane re-derives the ledger and compares it.

        Candidate replay runs the build's own evaluation, so its ledger must
        equal what the marker published.  A marker that overstates what it
        deferred is refused rather than believed.
        """

        with tempfile.TemporaryDirectory() as temporary:
            live = FamilyMarkerLiveFixtureTests()
            repository, custody = live.fixture_repository(Path(temporary))
            value = live.live_marker(repository)
            reviewed = readiness.reviewed_main(repository)
            value["common_evidence_git"] = {
                "head_commit": reviewed["head_commit"],
                "head_tree_oid": reviewed["head_tree_oid"],
            }
            for item in value["members"]:
                (repository / str(item["pack_path"])).mkdir(parents=True, exist_ok=True)
            by_id = {str(item["pack_id"]): item for item in value["members"]}
            marker_path = live.write_marker(custody, value)

            def replay(_repository, root, _registry, _reference, **_kwargs):
                # Deliberately does NOT record anything: this stands in for a
                # replay that found nothing to defer, against a marker claiming
                # the successor path was deferred.
                return copy.deepcopy(by_id[root.name]), {
                    str(reviewed["head_commit"])
                }

            with mock.patch.object(readiness, "_family_member", side_effect=replay):
                with self.assertRaises(readiness.FamilyPublicationError) as caught:
                    readiness.verify_family_publication_marker(
                        repository, marker_path, phase="candidate"
                    )
        self.assertEqual(caught.exception.check_id, "marker_schema_mismatch")
        self.assertIn("candidate replay ledger", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
