"""Fail-closed proposal agreement; these checks grant no paper fill authority."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/paper/results-fill-registry.md"
RETIRED = (tuple(f"DS-{n:02d}" for n in range(1, 34) if n != 8)
           + ("DS-08a", "PG-01", "PG-02", "PG-04", "PG-05", "PG-06",
              "PG-07", "PG-08", "OB-01", "OR-01"))


def check_retired_rows(text):
    for row_id in RETIRED:
        rows = [line for line in text.splitlines()
                if line.startswith(f"| {row_id} — ")]
        if len(rows) != 1:
            raise ValueError(f"{row_id}: missing or duplicate retirement row")
        cells = re.split(r"(?<!\\)\|", rows[0])[1:-1]
        if len(cells) != 7 or cells[4].strip() != "RETIRED_FALLBACK":
            raise ValueError(f"{row_id}: retired row treated as active")
        if not cells[5].strip().startswith("RETIRED_FALLBACK 2026-09-05 (D-174):"):
            raise ValueError(f"{row_id}: dated retirement lost")


class ComparisonPlacementFallbackTests(unittest.TestCase):
    def test_retired_successor_rows_remain_non_fillable(self):
        check_retired_rows(REGISTRY.read_text(encoding="utf-8"))

    def test_reactivation_counterfactual_rejected(self):
        text = REGISTRY.read_text(encoding="utf-8")
        for row_id in RETIRED:
            with self.subTest(row=row_id):
                row = next(line for line in text.splitlines()
                           if line.startswith(f"| {row_id} — "))
                changed = row.replace("| RETIRED_FALLBACK |", "| MEASURED |", 1)
                self.assertNotEqual(row, changed)
                with self.assertRaisesRegex(ValueError, "treated as active"):
                    check_retired_rows(text.replace(row, changed, 1))

    def test_missing_and_duplicate_retirement_rejected(self):
        text = REGISTRY.read_text(encoding="utf-8")
        for row_id in RETIRED:
            row = next(line for line in text.splitlines()
                       if line.startswith(f"| {row_id} — "))
            for changed in (text.replace(row, "", 1), text + "\n" + row):
                with self.subTest(row=row_id), self.assertRaisesRegex(
                        ValueError, "missing or duplicate"):
                    check_retired_rows(changed)


PLACEMENTS = ROOT / "docs/contracts/paper_comparison_placements.md"
CUSTODY = ROOT / "docs/contracts/paper_supply_custody.md"
COLUMNS = ("Obligation", "Placement", "Location", "Site", "Artifact field",
           "Supplier", "Evidence", "Family", "Role", "Required grant",
           "Applicability", "Missing evidence", "Adoption")
BINDING_COLUMNS = ("Obligation", "Placement", "Site", "Artifact field", "Supplier",
                   "Evidence", "Family", "Role", "Required grant", "Adoption")
# Independent site census: catches deletions even if made in every mirror.
SITE_KEYS = {
    1: "identity length", 2: "ratios abstract discussion conclusion headline",
    3: "section4 abstract discussion conclusion",
    4: "1p7b-prefill 8b-prefill 1p7b-decode 8b-decode composition na",
    5: "1p7b-prefill 8b-prefill 1p7b-decode 8b-decode", 6: "table",
    7: "table split",
    8: " ".join(f"{phase}-{branch}-{site}" for phase in ("decode", "prefill")
                for branch in ("a", "b")
                for site in ("abstract", "discussion", "conclusion")),
    9: "section4 abstract discussion conclusion",
    10: "section4 abstract discussion conclusion", 11: "archive", 12: "p1",
    13: "response", 14: "containment", 15: "phase drift",
    16: "challenge between-session", 17: "decode prefill", 18: "acceptance",
    19: "null slope floor holm geometry dependence", 20: "limitation result",
    21: "external", 22: "availability machine",
}
EXPECTED_IDS = {f"CP-X{x:02d}-{key}" for x, keys in SITE_KEYS.items()
                for key in keys.split()}
NON_EMPIRICAL = {
    "CP-X04-na": "LIMITATION", "CP-X12-p1": "SCHEMATIC",
    "CP-X16-between-session": "LIMITATION", "CP-X20-limitation": "LIMITATION",
    **{f"CP-X19-{key}": "SYNTHETIC" for key in SITE_KEYS[19].split()},
}


def parse_table(text, marker, columns):
    start, end = (f"<!-- {edge} COMPARISON {marker} -->"
                  for edge in ("BEGIN", "END"))
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError("missing or duplicate proposal section")
    body = text.split(start, 1)[1].split(end, 1)[0]
    lines = [line for line in body.splitlines() if line.strip()]
    cells = lambda line: [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
    if len(lines) < 3 or tuple(cells(lines[0])) != columns:
        raise ValueError("proposal table schema mismatch")
    if cells(lines[1]) != ["---"] * len(columns):
        raise ValueError("proposal separator mismatch")
    result = {}
    for line in lines[2:]:
        values = cells(line)
        if len(values) != len(columns) or any(not v for v in values):
            raise ValueError("malformed or empty placement")
        row = dict(zip(columns, values))
        key = row["Placement"]
        if key in result:
            raise ValueError("duplicate placement")
        result[key] = row
    if set(result) != EXPECTED_IDS:
        raise ValueError("missing or unexpected obligation/placement")
    for key, row in result.items():
        x = int(key.split("-")[1][1:])
        if row["Obligation"] != f"X{x}":
            raise ValueError("obligation identity mismatch")
        kind = NON_EMPIRICAL.get(key, "EMPIRICAL")
        if row["Evidence"] != kind:
            raise ValueError("empirical/synthetic disposition mismatch")
        family = {1: "reported_energy_parents", 2: "d165_closeout",
                  3: "d165_closeout", 5: "reported_energy_parents",
                  6: "claim_evidence", 8: "claim_evidence",
                  9: "whole_window_verdict", 10: "d165_closeout"}.get(x, "UNRESOLVED")
        if key == "CP-X07-table":
            family = "claim_evidence"
        if key == "CP-X20-result":
            family = "transfer_projection"
        if kind != "EMPIRICAL":
            family = "NONE"
        role = family if family in ("NONE", "UNRESOLVED") else "UNREGISTERED"
        if (row["Family"], row["Role"]) != (family, role):
            raise ValueError("family/role mismatch")
        if row["Adoption"] != "PROPOSED_STOP_FILL":
            raise ValueError("proposal treated as active")
        if kind == "EMPIRICAL" and row["Supplier"].startswith(
                ("synthetic_", "schematic_", "fixture.", "fixed_")):
            raise ValueError("empirical row has only a synthetic/non-empirical supplier")
        if family == "UNRESOLVED" and row["Required grant"] != "UNRESOLVED":
            raise ValueError("unresolved route assigned a grant")
        if kind != "EMPIRICAL" and row["Required grant"] != "NONE":
            raise ValueError("non-empirical row assigned a grant")
    return result


def check_agreement(placements, registry, custody):
    check_retired_rows(registry)
    tables = (parse_table(placements, "PROPOSALS", COLUMNS),
              parse_table(registry, "PROPOSALS", COLUMNS),
              parse_table(custody, "BINDINGS", BINDING_COLUMNS))
    if tables[0] != tables[1]:
        raise ValueError("placement/registry agreement mismatch")
    for key, binding in tables[2].items():
        if binding != {col: tables[0][key][col] for col in BINDING_COLUMNS}:
            raise ValueError("custody binding agreement mismatch")
    live = custody.split("## Custody-bound registry rows", 1)[1].split(
        "## Supply-map schema and lookup", 1)[0]
    lines = [line for line in live.splitlines() if line.startswith("|")]
    if lines != ["| Registry row | Family / supply role |", "|---|---|"]:
        raise ValueError("live census activated")


class ComparisonPlacementAgreementTests(unittest.TestCase):
    def setUp(self):
        self.texts = [p.read_text(encoding="utf-8")
                      for p in (PLACEMENTS, REGISTRY, CUSTODY)]

    def mutate(self, table, key, column, value):
        texts = list(self.texts)
        columns = BINDING_COLUMNS if table == 2 else COLUMNS
        row = next(line for line in texts[table].splitlines()
                   if f"| {key} |" in line)
        values = row.split("|")[1:-1]
        values[columns.index(column)] = f" {value} "
        texts[table] = texts[table].replace(row, "|" + "|".join(values) + "|", 1)
        return texts

    def test_all_three_tables_agree(self):
        check_agreement(*self.texts)

    def test_each_obligation_deleted_from_any_one_table_fails(self):
        for table in range(3):
            for x in range(1, 23):
                texts = list(self.texts)
                texts[table] = "\n".join(line for line in texts[table].splitlines()
                                         if not line.startswith(f"| X{x} |"))
                with self.subTest(table=table, obligation=x), self.assertRaisesRegex(
                        ValueError, "missing or unexpected"):
                    check_agreement(*texts)

    def test_each_supplier_changed_in_only_one_table_fails(self):
        for table in range(3):
            for key in EXPECTED_IDS:
                with self.subTest(table=table, site=key), self.assertRaisesRegex(
                        ValueError, "agreement mismatch"):
                    check_agreement(*self.mutate(table, key, "Supplier", "wrong_supplier"))

    def test_duplicate_placement_in_any_table_fails(self):
        for table in range(3):
            texts = list(self.texts)
            row = next(line for line in texts[table].splitlines()
                       if "| CP-X01-identity |" in line)
            texts[table] = texts[table].replace(row, row + "\n" + row, 1)
            with self.subTest(table=table), self.assertRaisesRegex(ValueError, "duplicate placement"):
                check_agreement(*texts)

    def test_family_role_and_adoption_mutations_fail(self):
        for table in range(3):
            for col, value, error in (("Family", "claim_evidence", "family/role"),
                                      ("Role", "fixture.reported_energy_parents", "family/role"),
                                      ("Adoption", "ACTIVE", "treated as active")):
                with self.subTest(table=table, column=col), self.assertRaisesRegex(ValueError, error):
                    check_agreement(*self.mutate(table, "CP-X05-1p7b-decode", col, value))

    def test_empirical_with_only_synthetic_supplier_fails(self):
        for table in range(3):
            for key in EXPECTED_IDS - NON_EMPIRICAL.keys():
                with self.subTest(table=table, site=key), self.assertRaisesRegex(
                        ValueError, "only a synthetic"):
                    check_agreement(*self.mutate(table, key, "Supplier", "synthetic_dependence"))

    def test_synchronized_empirical_reclassification_still_fails(self):
        texts = [self.mutate(i, "CP-X17-decode", "Evidence", "SYNTHETIC")[i]
                 for i in range(3)]
        with self.assertRaisesRegex(ValueError, "disposition mismatch"):
            check_agreement(*texts)

    def test_synchronized_obligation_deletion_still_fails(self):
        texts = ["\n".join(line for line in text.splitlines()
                           if not line.startswith("| X22 |")) for text in self.texts]
        with self.assertRaisesRegex(ValueError, "missing or unexpected"):
            check_agreement(*texts)

    def test_live_census_cannot_include_proposal(self):
        texts = list(self.texts)
        texts[2] = texts[2].replace("| Registry row | Family / supply role |\n|---|---|",
                                  "| Registry row | Family / supply role |\n|---|---|\n"
                                  "| CP-X05-1p7b-decode | reported_energy_parents/production.fake |", 1)
        with self.assertRaisesRegex(ValueError, "live census activated"):
            check_agreement(*texts)
