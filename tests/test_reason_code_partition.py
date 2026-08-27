from __future__ import annotations

import ast
import unittest
from collections import defaultdict
from pathlib import Path

from joulewise.analysis_engine.claims import REASON_CODES
from joulewise.analysis_engine.reason_kinds import (
    CONTRACT_REASON_CODES,
    DATA_REASON_CODES,
    DEAD_REASON_CODES,
    LOCK_REASON_CODES,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (ROOT / "joulewise", ROOT / "scripts")


def _assignment_names(node: ast.Assign | ast.AnnAssign) -> set[str]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return {
        child.id
        for target in targets
        for child in ast.walk(target)
        if isinstance(child, ast.Name)
    }


def _declaration_only_nodes(path: Path, tree: ast.AST) -> set[ast.AST]:
    """Return frozen-vocabulary ASTs that are not reason emissions."""

    relative = path.relative_to(ROOT).as_posix()
    names_by_path = {
        "joulewise/analysis_engine/claims.py": {
            "REDUCER_REASON_CODES",
            "ENGINE_REASON_CODES",
            "REASON_CODES",
            "_NOT_ESTIMABLE",
            "_NOT_RESOLVABLE",
            "_UNRESOLVED",
            "_SENSITIVITY",
            "_REASON_PRECEDENCE",
        },
        "joulewise/calibration_ledger.py": {"REFUSAL_TAXONOMY"},
        "joulewise/whole_window.py": {
            "PROSPECTIVE_MEMBER_FAILURE_REASON_CODES",
            "_REDERIVATION_LEAF_REASONS",
            "_METRIC_LOCAL_PRECHECK_REASONS",
        },
        "joulewise/floor_extraction.py": {"CELL_REFUSAL_CODES"},
    }
    ignored: set[ast.AST] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and (
            _assignment_names(node) & names_by_path.get(relative, set())
        ):
            ignored.update(ast.walk(node))
        if (
            relative == "joulewise/calibration_exits.py"
            and isinstance(node, ast.ClassDef)
            and node.name == "RefusalCode"
        ):
            ignored.update(ast.walk(node))
    return ignored


def _is_executable_emission_literal(
    node: ast.Constant,
    parents: dict[ast.AST, ast.AST],
) -> bool:
    """Recognize a literal on an executable reason-producing path.

    For this structural grep proof, an emission is a reason literal inside a
    function body that is returned, stored, or passed to a producer call.
    Comparison/membership literals and mapping/subscript keys are consumers,
    not emitters.  Module-level frozen vocabularies are separately masked.
    """

    current: ast.AST = node
    in_function = False
    while current in parents:
        parent = parents[current]
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            in_function = True
            break
        if isinstance(parent, ast.Compare):
            return False
        if isinstance(parent, ast.Subscript) and parent.slice is current:
            return False
        if isinstance(parent, ast.Dict):
            for key in parent.keys:
                if key is current:
                    return False
        if isinstance(parent, ast.Call):
            function = parent.func
            if (
                isinstance(function, ast.Attribute)
                and function.attr in {"get", "startswith", "endswith"}
                and node in set(ast.walk(parent))
            ):
                return False
        current = parent
    return in_function


def emitted_reason_locations() -> dict[str, list[str]]:
    """Map registry spellings to executable source locations.

    The scan covers both ``joulewise/`` and ``scripts/``.  It deliberately
    excludes the claim registry/classification module and the adjacent frozen
    vocabularies called out by D-158; merely belonging to another enum or set
    is not evidence that a reason can be emitted.
    """

    locations: dict[str, list[str]] = defaultdict(list)
    for source_root in SOURCE_ROOTS:
        for path in sorted(source_root.rglob("*.py")):
            if path == ROOT / "joulewise/analysis_engine/reason_kinds.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            parents = {
                child: parent
                for parent in ast.walk(tree)
                for child in ast.iter_child_nodes(parent)
            }
            ignored = _declaration_only_nodes(path, tree)
            literal_aliases = {
                target.id: node.value.value
                for node in getattr(tree, "body", [])
                if isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
                and node.value.value in REASON_CODES
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and node.value in REASON_CODES
                    and node not in ignored
                    and _is_executable_emission_literal(node, parents)
                ):
                    locations[node.value].append(
                        f"{path.relative_to(ROOT).as_posix()}:{node.lineno}"
                    )
                if (
                    isinstance(node, ast.Name)
                    and isinstance(node.ctx, ast.Load)
                    and node.id in literal_aliases
                ):
                    current: ast.AST = node
                    while current in parents:
                        current = parents[current]
                        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            locations[literal_aliases[node.id]].append(
                                f"{path.relative_to(ROOT).as_posix()}:{node.lineno}"
                            )
                            break
    return locations


class ReasonCodePartitionTests(unittest.TestCase):
    def test_partition_is_total_and_pairwise_disjoint(self) -> None:
        partitions = {
            "DATA": DATA_REASON_CODES,
            "CONTRACT": CONTRACT_REASON_CODES,
            "DEAD": DEAD_REASON_CODES,
            "LOCK": LOCK_REASON_CODES,
        }
        membership = defaultdict(list)
        for name, values in partitions.items():
            for code in values:
                membership[code].append(name)
        unclassified = sorted(REASON_CODES - set(membership))
        multiply_classified = {
            code: names for code, names in sorted(membership.items()) if len(names) != 1
        }
        unexpected = sorted(set(membership) - REASON_CODES)
        self.assertFalse(
            unclassified or multiply_classified or unexpected,
            "reason partition drift: "
            f"unclassified={unclassified!r}, "
            f"multiply_classified={multiply_classified!r}, "
            f"not_registered={unexpected!r}",
        )
        self.assertEqual(set(membership), REASON_CODES)

    def test_every_data_or_contract_reason_has_an_executable_emitter(self) -> None:
        """A live code needs an executable literal, not vocabulary membership."""

        locations = emitted_reason_locations()
        missing = sorted(
            code
            for code in DATA_REASON_CODES | CONTRACT_REASON_CODES
            if not locations[code]
        )
        self.assertFalse(
            missing,
            "DATA/CONTRACT codes without an emitter in joulewise/ or scripts/: "
            f"{missing!r}",
        )

    def test_dead_vocabulary_has_no_executable_emitter(self) -> None:
        locations = emitted_reason_locations()
        newly_live = {
            code: locations[code]
            for code in sorted(DEAD_REASON_CODES)
            if locations[code]
        }
        self.assertFalse(
            newly_live,
            "DEAD reason vocabulary acquired an emitter and must be reclassified: "
            f"{newly_live!r}",
        )


if __name__ == "__main__":
    unittest.main()
