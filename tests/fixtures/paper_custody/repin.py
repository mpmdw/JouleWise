"""Compute the five synthetic, non-issuing paper-custody fixture roles.

The fixture roles used to live in the committed supply map, with receipt and
inventory digests that hash the validator source. Every edit to a validator
therefore broke ``tests/test_paper_custody.py`` until someone ran this script
by hand and committed new digests (lane L7, Ed's point c, 2026-10-05).

The fixture roles now leave the committed map. ``fixture_supply_map`` builds
them at test time from the current validator source, and the test writes the
result into its temporary Git anchor. Nothing here protects a number: the
inputs carry the marker ``synthetic-no-measurement-value`` and the roles run
in ``test_fixture_non_issuing`` mode, which can never issue a paper value.
Production roles stay hard-coded in the committed map and are not touched.

Run as a script, it rewrites the one committed fixture file the repository
base needs (``extraction_spec.json``) and reports whether the committed map
still carries fixture roles. ``--check`` writes nothing.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise import paper_custody as custody  # noqa: E402

MARKER = "synthetic-no-measurement-value"
FIXTURE_PREFIX = "fixture."
EXTRACTION_SPEC_PATH = "tests/fixtures/paper_custody/extraction_spec.json"
_JSONL_ROLES = frozenset({"campaign_log"})


def encoded(value: object) -> bytes:
    return custody._canonical_json_bytes(value)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fixture_families() -> tuple[str, ...]:
    return tuple(sorted(spec.family for spec in custody._FAMILY_SPECS.values()))


def _spec(family: str):
    for spec in custody._FAMILY_SPECS.values():
        if spec.family == family:
            return spec
    raise ValueError(f"unknown paper custody family: {family}")


def input_bytes(family: str, role: str) -> bytes:
    """Synthetic bytes of one fixture input; the test writes exactly these."""

    return encoded({"family": family, "marker": MARKER, "role": role,
                    "schema_version": custody._FIXTURE_SCHEMA})


def source_bytes(family: str) -> bytes:
    return encoded({"family": family, "marker": MARKER})


def _input_row(family: str, role: str) -> dict[str, str]:
    if family == "reported_energy_parents" and role == "extraction_spec":
        row = {"authority": "git_blob", "base": "repository", "path": EXTRACTION_SPEC_PATH}
    else:
        suffix = ".jsonl" if role in _JSONL_ROLES else ".json"
        row = {"authority": "generated", "base": "runs_root", "path": f"{family}/inputs/{role}{suffix}"}
    row.update(role=role, expected_sha256=digest(input_bytes(family, role)))
    return row


def fixture_role_entry(family: str) -> dict[str, object]:
    """One fixture role, with receipt and inventory digests from current source."""

    spec = _spec(family)
    inputs = [_input_row(family, role.value) for role in spec.roles_for("test_fixture_non_issuing")]
    census = [{"authority": "generated", "base": "runs_root", "path": f"{family}/sources/member.json",
               "expected_sha256": digest(source_bytes(family))}]
    validator = f"joulewise.paper_custody.{family}.v1"
    consumed = [*inputs, *[dict(row, role="authenticated_source") for row in census]]
    receipt_path = f"{family}/inputs/validator_receipt.json"
    receipt = {
        "family": family,
        "inputs": sorted([{"path": row["path"], "role": row["role"], "sha256": row["expected_sha256"]}
                          for row in consumed], key=lambda row: (row["role"], row["path"])),
        "replay_codes": [], "schema_version": custody._RECEIPT_SCHEMA, "status": "PASS",
        "validator": validator, "validator_source_sha256": custody._validator_source_sha256(family),
    }
    receipt_sha = digest(encoded(receipt))
    inventory = {
        "family": family,
        "files": sorted([{"authority": row["authority"], "path": row["path"], "role": row["role"],
                          "sha256": row["expected_sha256"]} for row in consumed]
                        + [{"authority": "generated", "path": receipt_path, "role": "validator_receipt",
                            "sha256": receipt_sha}], key=lambda row: (row["role"], row["path"])),
        "inventory_id": f"fixture-{family}", "mode": "test_fixture_non_issuing",
        "schema_version": custody._INVENTORY_SCHEMA,
    }
    return {
        "family": family,
        "inputs": inputs,
        "inventory": {"base": "runs_root", "expected_sha256": digest(encoded(inventory)),
                      "path": f"{family}/inventory.json"},
        "issuance_gate_id": None,
        "mode": "test_fixture_non_issuing",
        "receipt": {"base": "runs_root", "expected_sha256": receipt_sha, "path": receipt_path},
        "source_census": census,
        "subjects": [],
        "validator": validator,
    }


def committed_supply_map() -> dict[str, object]:
    return json.loads((ROOT / custody._SUPPLY_MAP_PATH).read_bytes())


def fixture_supply_map(base: dict[str, object] | None = None) -> dict[str, object]:
    """The committed map plus the five fixture roles computed from current source."""

    supply = copy.deepcopy(committed_supply_map() if base is None else base)
    roles = dict(supply.get("roles", {}))
    clash = sorted(role for role in roles if role.startswith(FIXTURE_PREFIX))
    if clash:
        raise ValueError(f"committed supply map still carries fixture roles: {clash}")
    for family in fixture_families():
        roles[f"{FIXTURE_PREFIX}{family}"] = fixture_role_entry(family)
    supply["roles"] = roles
    return supply


def supply_map_bytes(supply: dict[str, object]) -> bytes:
    return (json.dumps(supply, indent=2, sort_keys=True) + "\n").encode("utf-8")


def stale() -> list[str]:
    """Reasons the committed fixture state needs ``--write``; empty when fresh."""

    reasons = []
    roles = committed_supply_map().get("roles", {})
    fixture_roles = sorted(role for role in roles if role.startswith(FIXTURE_PREFIX))
    if fixture_roles:
        reasons.append(f"committed supply map carries computed fixture roles {fixture_roles}")
    path = ROOT / EXTRACTION_SPEC_PATH
    expected = input_bytes("reported_energy_parents", "extraction_spec")
    if not path.is_file() or path.read_bytes() != expected:
        reasons.append(f"{EXTRACTION_SPEC_PATH} differs from its generated bytes")
    return reasons


def repin() -> None:
    """Remove fixture roles from the committed map and refresh the spec fixture."""

    path = ROOT / custody._SUPPLY_MAP_PATH
    supply = committed_supply_map()
    roles = {role: entry for role, entry in supply.get("roles", {}).items()
             if not role.startswith(FIXTURE_PREFIX)}
    if roles != supply.get("roles"):
        supply["roles"] = roles
        path.write_bytes(supply_map_bytes(supply))
    (ROOT / EXTRACTION_SPEC_PATH).write_bytes(input_bytes("reported_energy_parents", "extraction_spec"))
    print("Fixture roles are computed at test time; committed map holds production and pending roles only.")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["--check"]:
        reasons = stale()
        for reason in reasons:
            print(f"STALE {reason}")
        return 1 if reasons else 0
    if args:
        print("usage: repin.py [--check]", file=sys.stderr)
        return 2
    repin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
