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
                   "Evidence", "Family", "Role", "Required grant",
                   "Applicability", "Missing evidence", "Adoption")
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

# Closed safety vocabulary: changes require an explicit contract/test update.
SAFETY_VOCABULARY = {
    'Applicability': {
        'ruled omission (D-177); 24 admitted bundles / two brackets',
        'A only; never infer from a model verdict',
        'ALPHA 1p7b; BETA 8b; ordered strict members, basis, selection and prompt-pin agree',
        'ALPHA small / BETA large; selected L for prefill; floor acceptance required',
        'Actual affected ALPHA/BETA/GAMMA window',
        'All twelve ratios >=2 and publication acceptance PASS',
        'Comparison successor only',
        'Complete evaluable ratio census; B never means a failed model contrast',
        'ruled omission (D-177); DO_NOT_START; explicit inclusion and design gates required',
        'DO_NOT_START; historical pulse bound is not transfer validation',
        'ruled omission (D-177); DO_NOT_START; retired result remains retired',
        'DO_NOT_START; separate authorization, equipment, load/synchronization/range; not a comparison dependency',
        'DO_NOT_START; separate prospectively fixed design and explicit inclusion',
        'Every new machine must demonstrate admission; no inherited measured limits',
        'Every submission floor actually rechecked; binder existence and DC/CE parent acceptance do not grant publication prose',
        'ruled omission (D-177); Five disjoint A/B/B/A blocks per magnitude and earlier disjoint comparator; ALPHA/BETA nulls cannot double as test',
        'G2-a through final close; include failures, not merely admitted members',
        'GAMMA; authenticated floor acceptance; prefill contrast ctr-d117-prefill-pL-qwen3-1p7b-vs-qwen3-8b; L authenticated',
        'Illustrative datasets kept separate; never campaign evidence',
        'Independent GAMMA verdict; no inference from A/B; preserve valid Table 3 results on ratio refusal',
        'N/A by column/phase; not a missing measurement',
        'No measured annotations or numeric thresholds',
        'Only authenticated selected L; never assume a ladder rung',
        'Only if no governing before-comparison stop; retain separately valid model verdicts',
        'Prospective identity disclosure; no measured result',
        'Public release, not local custody paths',
        'ruled omission (D-177); separate Window C; forty admitted bundles / five lengths remain design requirements',
        'ruled omission (D-177); Six designated references, three held-out probes, three sustained-work/cooldown pairs',
        'Ten complete blocks per contrast; preserve collection order/membership; SYN-04 cannot supply',
        'Twelve evaluable ratios; four absolute common-mode ratios explicitly N/A',
        'Two distinct exhausted-ladder renderings require adoption; diagnostic failure is not production non-admission',
    },
    'Missing evidence': {
        'Keep synthetic label; omit unsupported illustration rather than infer empirical pass/refusal',
        'Remain excluded; no silent restoration',
        'Retain exclusion; historical Window C is no supplier',
        'Retain explicit N/A; never opportunistically fill',
        'Retain limitation',
        'Retain limitation; no result inferred from design',
        'Retain schematic label; empirical annotations need separate X6–X10 bindings',
        'STOP_FILL; methods/diagnostics fallback; no issued refusal inferred',
        'STOP_FILL; methods/diagnostics fallback; no issued refusal inferred; D-177 adjacent phase-energy limitation required',
        'STOP_FILL; preserve withdrawal/no-characterization prefix; D is not a fourth global outcome',
        'STOP_FILL; retain honest unissued-locators statement',
    },
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
        for column, vocabulary in SAFETY_VOCABULARY.items():
            if row[column] not in vocabulary:
                raise ValueError(f"{column}: outside closed safety vocabulary")
        family = {2: "d165_closeout",
                  3: "d165_closeout", 5: "reported_energy_parents",
                  6: "claim_evidence", 8: "claim_evidence",
                  9: "whole_window_verdict", 10: "d165_closeout"}.get(x, "UNRESOLVED")
        if x == 1:
            # X1 has no adopted text grant; do not freeze its candidate family.
            family = row["Family"]
            if family not in {"reported_energy_parents", "d165_closeout",
                              "whole_window_verdict", "claim_evidence",
                              "transfer_projection", "UNRESOLVED"}:
                raise ValueError("unknown candidate family")
            if not row["Required grant"].startswith("UNRESOLVED: candidate route;"):
                raise ValueError("X1 candidate grant treated as adopted")
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
        if x != 1 and family == "UNRESOLVED" and row["Required grant"] != "UNRESOLVED":
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

    def test_d177_phase_energy_adjacency_block_exists(self):
        self.assertIn(
            '**D-177 phase-energy limitation.** The D-123 mean cells—the average energies\n'
            'assigned to each phase—are phase-specific results. Every X5 placement below\n'
            'requires this adjacent note in the successor:\n'
            '\n'
            '> Phase attribution—assigning energy to prompt processing or token generation—is\n'
            '> reported without an instrument phase-accounting characterization, a measured\n'
            '> check of how those phase energies account for the enclosing request. The\n'
            '> phase-accounting check registered in P.2 was not run for this paper. Phase\n'
            '> energies are per-window accounting under the registered boundary rule—energy\n'
            '> assigned to each phase from its overlap with sampled power records—not\n'
            '> independently characterized attributions.',
            self.texts[0],
        )

    def test_all_three_tables_agree(self):
        check_agreement(*self.texts)

    def test_safety_columns_reject_permissive_wording_in_any_or_all_tables(self):
        for column in SAFETY_VOCABULARY:
            for key in EXPECTED_IDS:
                for tables in ((0,), (1,), (2,), (0, 1, 2)):
                    texts = list(self.texts)
                    for table in tables:
                        texts[table] = self.mutate(
                            table, key, column, "Fill from available evidence")[table]
                    with self.subTest(column=column, site=key, tables=tables):
                        with self.assertRaisesRegex(ValueError, "closed safety vocabulary"):
                            check_agreement(*texts)

    def test_safety_columns_with_known_but_different_wording_break_mirror(self):
        for column, value in (("Applicability", "Comparison successor only"),
                              ("Missing evidence", "Retain limitation")):
            for table in range(3):
                with self.subTest(column=column, table=table):
                    with self.assertRaisesRegex(ValueError, "agreement mismatch"):
                        check_agreement(*self.mutate(table, "CP-X01-identity", column, value))

    def test_x1_requires_unresolved_candidate_grant(self):
        for key in ("CP-X01-identity", "CP-X01-length"):
            texts = [self.mutate(i, key, "Required grant", "cell(subject=identity)")[i]
                     for i in range(3)]
            with self.subTest(site=key), self.assertRaisesRegex(ValueError, "candidate grant"):
                check_agreement(*texts)

    def test_x1_candidate_family_is_not_an_adoption_assertion(self):
        for key in ("CP-X01-identity", "CP-X01-length"):
            texts = [self.mutate(i, key, "Family", "claim_evidence")[i]
                     for i in range(3)]
            with self.subTest(site=key):
                check_agreement(*texts)

    def test_registry_proposal_has_no_scannable_fill_tokens(self):
        appendix = self.texts[1].split("<!-- BEGIN COMPARISON PROPOSALS -->", 1)[1]
        self.assertNotRegex(appendix, r"\[FILL:[^\]]+\]")
        for token in ("DS-32", "OB-01", "OR-01", "PG-08"):
            self.assertIn(f"&#91;FILL:{token}&#93;", appendix)

    def test_floor_sites_name_s6_reason_and_diagnostic_families(self):
        rows = parse_table(self.texts[0], "PROPOSALS", COLUMNS)
        for suffix in ("1p7b-prefill", "8b-prefill", "1p7b-decode", "8b-decode"):
            for family in ("TERMINAL_REFUSAL_REASON_*", "NO_EXACT_FLOOR_REASON_*",
                           "AVAILABLE_DIAGNOSTIC_CLAUSE_*", "POINT_DIAGNOSTIC_CLAUSE_*"):
                with self.subTest(site=suffix, family=family):
                    self.assertIn(family, rows[f"CP-X04-{suffix}"]["Site"])

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
