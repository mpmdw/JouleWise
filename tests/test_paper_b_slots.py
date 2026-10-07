"""Paper B slot manifest: every slot is empty and points at a field the code has.

A slot is a named empty place for one value that only measurement block 5 can
supply (``docs/paper/paper-b/slots.json``). Paper text refers to it by a slot
marker, the id wrapped as ``{{slot:<id>}}``. These checks protect three things:

1. No value. Every slot's ``value`` is null and no slot carries a number.
2. A real source. Every slot names an artifact (a schema id) and a field
   path. The schema id must be the value of the named module constant, and
   every key on the path must be in the key set (a module constant) or in the
   dict and set literals (a function) the manifest names for that object. The
   code is read with ``ast`` and never imported, so the check costs nothing
   and cannot run measurement code.
3. A clean outline. A slot marker in ``00-outline.md`` holds no digit and is
   the id of a slot, and the slot counts the outline states are the manifest's.

Checks against registered text (the analysis plan and the flag catalog) are
strict while those files are byte-identical to the sync point the manifest
records. Once they have moved (they are drafts that are about to be sealed),
drift is reported by a skip that names the re-sync, so that a paper document
never blocks the seal. Checks against code and against the frozen pack
configurations are always strict.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import unittest
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/paper/paper-b/slots.json"
OUTLINE = ROOT / "docs/paper/paper-b/00-outline.md"

SLOT_ID_RE = re.compile(r"[a-z]+(?:_[a-z]+)*(?:\.[a-z]+(?:_[a-z]+)*)+")
TOKEN_RE = re.compile(r"\{\{slot:([^{}]*)\}\}")
SLOT_KEYS = {"id", "family", "shape", "unit", "artifact", "field", "select", "issue", "basis", "value"}
OPTIONAL_SLOT_KEYS = {"rule", "site", "parts"}


class SlotBindingError(ValueError):
    """A slot's artifact or field does not exist in the code as the manifest says."""


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Reading the code without importing it
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _module(relative: str) -> ast.Module:
    path = ROOT / relative
    if not path.is_file():
        raise SlotBindingError(f"{relative}: no such file")
    return ast.parse(path.read_text(encoding="utf-8"), filename=relative)


def _assignments(relative: str) -> dict[str, ast.expr]:
    """Module-level ``NAME = <expression>`` assignments, last one wins."""
    found: dict[str, ast.expr] = {}
    for node in _module(relative).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            found[node.target.id] = node.value
    return found


def schema_constant(relative: str, name: str) -> str:
    value = _assignments(relative).get(name)
    if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
        raise SlotBindingError(f"{relative}: {name} is not a module-level string constant")
    return value.value


def _constant_strings(relative: str, name: str, seen: frozenset = frozenset()) -> set[str]:
    """Every string in a module constant, following names of other module constants.

    Key sets in the code are built as ``{"a", "b"} | _OTHER_KEYS`` or
    ``{"a", *_OTHER_KEYS}``; following the names gives the full set.
    """
    table = _assignments(relative)
    if name not in table:
        raise SlotBindingError(f"{relative}: no module-level constant {name}")
    strings: set[str] = set()
    for node in ast.walk(table[name]):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.add(node.value)
        elif isinstance(node, ast.Name) and node.id in table and node.id not in seen and node.id != name:
            strings |= _constant_strings(relative, node.id, seen | {name})
    return strings


def _function(relative: str, dotted: str) -> ast.AST:
    scope: list[ast.stmt] = _module(relative).body
    node: ast.AST | None = None
    for part in dotted.split("."):
        node = next((item for item in scope
                     if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                     and item.name == part), None)
        if node is None:
            raise SlotBindingError(f"{relative}: no function or class {dotted}")
        scope = node.body
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise SlotBindingError(f"{relative}: {dotted} is not a function")
    return node


def _function_keys(relative: str, dotted: str) -> set[str]:
    """Keys of every dict literal and members of every set literal inside one function."""
    keys: set[str] = set()
    for node in ast.walk(_function(relative, dotted)):
        if isinstance(node, ast.Dict):
            items = node.keys
        elif isinstance(node, ast.Set):
            items = node.elts
        else:
            continue
        for item in items:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                keys.add(item.value)
    return keys


def object_keys(artifact: dict, object_path: str) -> set[str]:
    objects = artifact["objects"]
    if object_path not in objects:
        raise SlotBindingError(
            f"{artifact['schema']}: the manifest does not say where the keys of "
            f"{object_path or 'the top-level object'!r} are defined")
    entry = objects[object_path]
    relative = entry.get("file", artifact["code"]["file"])
    if entry["kind"] == "constant":
        keys = _constant_strings(relative, entry["symbol"])
    elif entry["kind"] == "function":
        keys = _function_keys(relative, entry["symbol"])
    else:
        raise SlotBindingError(f"{artifact['schema']}: unknown kind {entry['kind']!r} for {object_path!r}")
    if not keys:
        raise SlotBindingError(f"{relative}: {entry['symbol']} names no key")
    return keys


def resolve(manifest: dict, artifact_name: str, field: str) -> None:
    """Raise SlotBindingError unless the artifact's schema id and every key on ``field`` exist in code."""
    artifact = manifest["artifacts"].get(artifact_name)
    if artifact is None:
        raise SlotBindingError(f"unknown artifact {artifact_name!r}")
    code = artifact["code"]
    found = schema_constant(code["file"], code["schema_constant"])
    if found != artifact["schema"]:
        raise SlotBindingError(
            f"{code['file']}: {code['schema_constant']} is {found!r}, the manifest says {artifact['schema']!r}")
    if not isinstance(field, str) or not field:
        raise SlotBindingError(f"{artifact_name}: empty field")
    object_path = ""
    segments = field.split(".")
    for index, segment in enumerate(segments):
        key = segment[:-2] if segment.endswith(("[]", "{}")) else segment
        if key not in object_keys(artifact, object_path):
            where = artifact["objects"][object_path]
            raise SlotBindingError(
                f"{artifact['schema']}: {key!r} (of {field!r}) is not a key in "
                f"{where.get('file', code['file'])} {where['symbol']}")
        if index + 1 < len(segments):
            object_path = f"{object_path}.{segment}" if object_path else segment


# ---------------------------------------------------------------------------
# Reading the registered text
# ---------------------------------------------------------------------------

def _sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def _at_sync_point(manifest: dict, name: str) -> bool:
    entry = manifest["synced_to"][name]
    return _sha256(entry["path"]) == entry["sha256"]


def _plan_text(manifest: dict) -> str:
    return (ROOT / manifest["synced_to"]["analysis_plan"]["path"]).read_text(encoding="utf-8")


def _section(text: str, heading_prefix: str) -> str:
    """The body of the level-two section whose heading starts with ``heading_prefix``."""
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(heading_prefix)), None)
    if start is None:
        return ""
    stop = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("## ")), len(lines))
    return "\n".join(lines[start + 1:stop])


def _backticked(text: str) -> set[str]:
    return set(re.findall(r"`([^`\n]+)`", text))


def _field_candidates(field: str) -> set[str]:
    """The sub-paths of a field that can count as 'the plan names it'.

    The leading collection (``cells``, ``contrasts``) alone never counts, so a
    plan sentence that merely mentions the collection names no field in it.
    """
    segments = [segment[:-2] if segment.endswith(("[]", "{}")) else segment for segment in field.split(".")]
    candidates = set()
    for start in range(len(segments)):
        for stop in range(start + 1, len(segments) + 1):
            if len(segments) == 1 or stop - 1 >= 1:
                candidates.add(".".join(segments[start:stop]))
    return candidates


def expected_basis(slot: dict, plan_tokens: set[str]) -> str:
    codes = slot["select"].get("codes")
    if codes:
        return "named" if all(code in plan_tokens for code in codes) else "inferred"
    return "named" if _field_candidates(slot["field"]) & plan_tokens else "inferred"


def registered_text_problems(manifest: dict) -> list[str]:
    """Where the manifest and the registered text it was synced to disagree."""
    problems: list[str] = []
    plan = _plan_text(manifest)
    synced = manifest["synced_to"]["analysis_plan"]
    status = re.search(r"Status: \*\*(DRAFT, NOT SEALED|SEALED)[^*]*?Revision (\d+)", plan)
    if status is None:
        problems.append("analysis plan: status line not found")
    else:
        if int(status.group(2)) != synced["revision"]:
            problems.append(f"analysis plan is revision {status.group(2)}, manifest synced to {synced['revision']}")
        if (status.group(1) == "SEALED") != synced["sealed"]:
            problems.append("analysis plan sealed state differs from the manifest's")

    open_fills = _backticked(_section(plan, "## 13.").split("`REPORTED-ENERGY-REGISTRATION-DIGESTS`")[0])
    for family in manifest["families"]:
        for name in family["waits_on"]:
            if name not in open_fills:
                problems.append(f"family {family['family']}: {name} is not an open FILL of analysis plan section 13")

    printed = _section(plan, "## 9.")
    bound_schemas = {manifest["artifacts"][slot["artifact"]]["schema"] for slot in manifest["slots"]}
    for schema in sorted(token for token in _backticked(printed) if token.startswith("joulewise.")):
        if schema not in bound_schemas:
            problems.append(f"analysis plan section 9 prints from {schema}, which no slot reads")
    used: set[str] = set()
    for slot in manifest["slots"]:
        used |= _field_candidates(slot["field"])
    for row in printed.splitlines():
        cells = [cell.strip() for cell in row.split("|")]
        if len(cells) < 7 or cells[1] in ("Printed quantity", "") or set(cells[1]) <= {"-"}:
            continue
        for token in _backticked(cells[3]):
            if token not in used:
                problems.append(f"analysis plan section 9 names field {token} ({cells[1]}), which no slot reads")

    plan_tokens = _backticked(plan)
    for slot in manifest["slots"]:
        want = expected_basis(slot, plan_tokens)
        if slot["basis"] != want:
            problems.append(f"{slot['id']}: basis is {slot['basis']!r}, the plan text gives {want!r}")
    return problems


def catalog_problems(manifest: dict) -> list[str]:
    catalog = json.loads((ROOT / manifest["synced_to"]["flag_catalog"]["path"]).read_text(encoding="utf-8"))
    codes = set(catalog["codes"])
    problems = []
    for slot in manifest["slots"]:
        for code in slot["select"].get("codes", []):
            if code not in codes:
                problems.append(f"{slot['id']}: flag code {code} is not in the flag catalog")
    return problems


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class SlotManifestShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()
        cls.slots = cls.manifest["slots"]
        cls.families = {family["family"]: family for family in cls.manifest["families"]}

    def test_every_value_is_null_and_no_slot_carries_a_number(self):
        def numbers(value):
            if isinstance(value, bool) or value is None or isinstance(value, str):
                return
            if isinstance(value, (int, float)):
                yield value
            elif isinstance(value, dict):
                for item in value.values():
                    yield from numbers(item)
            elif isinstance(value, list):
                for item in value:
                    yield from numbers(item)

        self.assertGreater(len(self.slots), 0)
        for slot in self.slots:
            with self.subTest(slot=slot.get("id")):
                self.assertIn("value", slot)
                self.assertIsNone(slot["value"])
                self.assertEqual(list(numbers(slot)), [])

    def test_ids_are_unique_digit_free_and_start_with_a_family_prefix(self):
        ids = [slot["id"] for slot in self.slots]
        self.assertEqual(len(ids), len(set(ids)))
        for slot in self.slots:
            with self.subTest(slot=slot["id"]):
                self.assertRegex(slot["id"], rf"\A{SLOT_ID_RE.pattern}\Z")
                self.assertIn(slot["family"], self.families)
                prefixes = self.families[slot["family"]]["prefixes"]
                self.assertTrue(any(slot["id"].startswith(prefix + ".") for prefix in prefixes))
        prefixes = [prefix for family in self.families.values() for prefix in family["prefixes"]]
        self.assertEqual(len(prefixes), len(set(prefixes)), "two families share an id prefix")

    def test_slots_use_only_the_declared_vocabulary(self):
        vocabulary = self.manifest["vocabulary"]
        for slot in self.slots:
            with self.subTest(slot=slot["id"]):
                self.assertTrue(SLOT_KEYS <= set(slot) <= SLOT_KEYS | OPTIONAL_SLOT_KEYS, sorted(slot))
                self.assertIn(slot["shape"], vocabulary["shapes"])
                self.assertIn(slot["issue"], vocabulary["issue"])
                self.assertIn(slot["basis"], vocabulary["basis"])
                self.assertIsInstance(slot["select"], dict)
                if slot["issue"] == "derive":
                    self.assertTrue(slot.get("rule"), "a derived slot names the plan's formula")
                if slot["shape"] == "line":
                    self.assertTrue(slot.get("parts"), "a line names the numbers it carries")
                pack = slot["select"].get("pack")
                if pack is not None and pack != "first clean":
                    self.assertIn(pack, vocabulary["packs"])
        for family in self.families.values():
            with self.subTest(family=family["family"]):
                self.assertIn(family["placement"]["state"], vocabulary["placement_states"])
                self.assertIn(family["available"], vocabulary["available"])
                self.assertIn(family["registered"], ("registered", "proposed"))
                self.assertTrue(any(slot["family"] == family["family"] for slot in self.slots))

    def test_family_sizes_follow_from_the_registered_design(self):
        # Registration section 0.9: four paper cells (two models, decode and the long prefill).
        # Analysis plan section 6: eight ratios (two models, two phases, two floor forms) and four
        # shared-sign ratios (comparative form only). Analysis plan section 7.1: two contrasts.
        vocabulary = self.manifest["vocabulary"]
        cells = len(vocabulary["models"]) * len(vocabulary["phases"])
        self.assertEqual(cells, 4)

        def records(family, field_prefix=""):
            return {json.dumps(slot["select"], sort_keys=True) for slot in self.slots
                    if slot["family"] == family and slot["field"].startswith(field_prefix)}

        self.assertEqual(len(records("reported")), cells)
        self.assertEqual(len(records("attribution_floor")), cells)
        self.assertEqual(len(records("floor")), cells)
        self.assertEqual(len(records("dominance", "independent_ratios[]")), 2 * cells)
        self.assertEqual(len(records("dominance", "comparative_common_mode_ratios[]")), cells)
        self.assertEqual(len(records("contrast")), 2)
        # Every record of one family carries the same set of fields.
        for family, prefix in (("reported", ""), ("floor", ""), ("contrast", ""),
                               ("dominance", "independent_ratios[]"),
                               ("dominance", "comparative_common_mode_ratios[]")):
            per_record: dict[str, set[str]] = {}
            for slot in self.slots:
                if slot["family"] == family and slot["field"].startswith(prefix):
                    per_record.setdefault(json.dumps(slot["select"], sort_keys=True), set()).add(slot["field"])
            self.assertEqual(len({frozenset(fields) for fields in per_record.values()}), 1, family)

    def test_unbound_lines_and_fixed_sentences_hold_no_value(self):
        for entry in self.manifest["unbound_lines"]:
            self.assertEqual(set(entry), {"key", "plan", "why"})
        for entry in self.manifest["fixed_sentences"]:
            self.assertEqual(set(entry), {"key", "plan", "conditional"})
        text = json.dumps([self.manifest["unbound_lines"], self.manifest["fixed_sentences"]])
        self.assertNotIn("{{slot:", text)


class SlotCodeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_every_slot_names_a_schema_and_field_that_exist_in_code(self):
        failures = []
        for slot in self.manifest["slots"]:
            try:
                resolve(self.manifest, slot["artifact"], slot["field"])
            except SlotBindingError as error:
                failures.append(f"{slot['id']}: {error}")
        self.assertEqual(failures, [])

    def test_every_declared_object_resolves(self):
        for name, artifact in self.manifest["artifacts"].items():
            code = artifact["code"]
            with self.subTest(artifact=name):
                self.assertEqual(schema_constant(code["file"], code["schema_constant"]), artifact["schema"])
                self.assertTrue(any(slot["artifact"] == name for slot in self.manifest["slots"]),
                                "an artifact no slot reads")
                for object_path in artifact["objects"]:
                    self.assertTrue(object_keys(artifact, object_path))

    def test_the_binding_check_rejects_what_is_not_in_code(self):
        def broken(change):
            manifest = copy.deepcopy(self.manifest)
            change(manifest)
            return manifest

        def rename_schema(manifest):
            manifest["artifacts"]["reported_energy"]["schema"] += "9"

        def rename_symbol(manifest):
            manifest["artifacts"]["claim_verdicts"]["objects"]["contrasts[].estimator"]["symbol"] = "_NO_SUCH_KEYS"

        def drop_object(manifest):
            del manifest["artifacts"]["reported_energy"]["objects"]["cells[].interval"]

        cases = [
            ("a field the code does not write", self.manifest, "reported_energy", "cells[].mean_joules"),
            ("a key under the wrong object", self.manifest, "claim_verdicts", "contrasts[].estimator.outcome"),
            ("an unknown artifact", self.manifest, "no_such_artifact", "cells[].mean_j"),
            ("a schema id the code does not hold", broken(rename_schema), "reported_energy", "cells[].mean_j"),
            ("a key set that does not exist", broken(rename_symbol), "claim_verdicts",
             "contrasts[].estimator.estimate"),
            ("an object the manifest does not locate", broken(drop_object), "reported_energy",
             "cells[].interval.n_r"),
        ]
        for label, manifest, artifact, field in cases:
            with self.subTest(case=label):
                with self.assertRaises(SlotBindingError):
                    resolve(manifest, artifact, field)
        # The same calls pass on the manifest as committed.
        resolve(self.manifest, "reported_energy", "cells[].mean_j")
        resolve(self.manifest, "claim_verdicts", "contrasts[].estimator.estimate")
        resolve(self.manifest, "reported_energy", "cells[].interval.n_r")

    def test_selectors_name_cells_and_contrasts_of_the_frozen_packs(self):
        frozen = self.manifest["frozen_identifiers"]
        packs = self.manifest["vocabulary"]["packs"]
        reported, families = set(), set()
        for name in ("alpha", "beta"):
            self.assertTrue((ROOT / "configs/campaigns" / packs[name]["pack_id"] / "plan_tree.json").is_file())
            spec = json.loads((ROOT / frozen["sources"][name]).read_text(encoding="utf-8"))
            reported |= {cell["cell_id"] for cell in spec["reported_energy_cells"]}
            families |= {cell["condition_family_id"] for cell in spec["cells"]}
        self.assertTrue((ROOT / "configs/campaigns" / packs["gamma"]["pack_id"] / "plan_tree.json").is_file())
        gamma = json.loads((ROOT / frozen["sources"]["gamma"]).read_text(encoding="utf-8"))
        contrasts = {contrast["contrast_id"] for contrast in gamma["contrasts"]}

        self.assertLessEqual(set(frozen["reported_cells"].values()), reported)
        self.assertLessEqual(set(frozen["floor_families"].values()), families)
        self.assertEqual(set(frozen["contrasts"].values()), contrasts)
        known = set(frozen["reported_cells"].values()) | set(frozen["floor_families"].values()) | contrasts
        models = {entry["model"] for entry in self.manifest["vocabulary"]["models"].values()}
        for slot in self.manifest["slots"]:
            select = slot["select"]
            with self.subTest(slot=slot["id"]):
                for key in ("cell_id", "condition_family_id", "contrast_id"):
                    if key in select:
                        self.assertIn(select[key], known)
                if "model" in select:
                    self.assertIn(select["model"], models)
                if "component" in select:
                    self.assertIn(select["component"], ("absolute", "comparative"))


class SlotRegisteredTextTests(unittest.TestCase):
    """Strict at the sync point; a named skip once the registered text has moved."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def _judge(self, problems, *documents):
        if not problems:
            return
        report = "; ".join(problems)
        if all(_at_sync_point(self.manifest, name) for name in documents):
            self.fail(report)
        self.skipTest(
            "the registered text has changed since slots.json was synced to it; re-sync the manifest "
            f"(synced_to, waits_on, basis, fields) to the current text. Differences: {report}")

    def test_manifest_agrees_with_the_analysis_plan(self):
        self._judge(registered_text_problems(self.manifest), "analysis_plan")

    def test_selected_flag_codes_are_in_the_flag_catalog(self):
        self._judge(catalog_problems(self.manifest), "flag_catalog")

    def test_registered_text_checks_reject_drift(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["families"][1]["waits_on"].append("NO-SUCH-FILL")
        manifest["slots"][0]["basis"] = "inferred" if manifest["slots"][0]["basis"] == "named" else "named"
        problems = registered_text_problems(manifest)
        if _at_sync_point(self.manifest, "analysis_plan"):
            self.assertEqual(len(problems), 2, problems)
        else:
            self.assertGreaterEqual(len(problems), 2, problems)
        manifest = copy.deepcopy(self.manifest)
        coded = next(slot for slot in manifest["slots"] if slot["select"].get("codes"))
        coded["select"]["codes"] = ["no.such_code"]
        self.assertEqual(len(catalog_problems(manifest)) - len(catalog_problems(self.manifest)), 1)


class OutlineSlotTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()
        cls.outline = OUTLINE.read_text(encoding="utf-8")
        cls.ids = {slot["id"] for slot in cls.manifest["slots"]}

    def test_slot_tokens_hold_no_digit_and_name_a_slot(self):
        tokens = TOKEN_RE.findall(self.outline)
        self.assertGreater(len(tokens), 0, "the outline shows no slot token")
        self.assertEqual(self.outline.count("{{slot:"), len(tokens), "a malformed slot token")
        for token in tokens:
            with self.subTest(token=token):
                self.assertNotRegex(token, r"[0-9]", "a digit inside a slot token")
                self.assertIn(token, self.ids)

    def test_token_check_rejects_a_value_and_an_unknown_id(self):
        for text in ("{{slot:reported.small.decode.mean=10.16}}", "{{slot:10.16}}"):
            token = TOKEN_RE.findall(text)[0]
            self.assertRegex(token, r"[0-9]")
        self.assertNotIn("reported.small.decode.average", self.ids)
        self.assertIn("reported.small.decode.mean", self.ids)

    def test_outline_names_every_slot_family(self):
        for family in self.manifest["families"]:
            for prefix in family["prefixes"]:
                with self.subTest(prefix=prefix):
                    self.assertIn(f"`{prefix}.", self.outline)

    def test_outline_slot_counts_match_the_manifest(self):
        slots = self.manifest["slots"]
        rows = [line for line in self.outline.splitlines() if line.startswith("|")]
        for family in self.manifest["families"]:
            count = sum(slot["family"] == family["family"] for slot in slots)
            marker = f"`{family['prefixes'][0]}."
            with self.subTest(family=family["family"]):
                matching = [row for row in rows if marker in row]
                self.assertEqual(len(matching), 1, "one table row per family")
                numbers = [cell.strip() for cell in matching[0].split("|") if cell.strip().isdigit()]
                self.assertEqual(numbers, [str(count)])
        results = ("reported", "attribution_floor", "floor", "dominance", "contrast", "descriptive")
        proper = sum(slot["family"] in results for slot in slots)
        self.assertIn(f"That is {len(slots)} slots.", self.outline)
        self.assertIn(f"{proper} of the {len(slots)}.", self.outline)
        self.assertIn(f"lists {len(self.manifest['fixed_sentences'])} of them", self.outline)
        self.assertIn(f"Another {len(self.manifest['unbound_lines'])} disclosure items", self.outline)

    def test_outline_states_no_energy_value(self):
        # A digit followed by an energy unit would be a stated result or a hint of one.
        self.assertIsNone(re.search(r"[0-9]\s*(?:J\b|J/token|joules?\b|mJ\b|kJ\b|W\b)", self.outline))


if __name__ == "__main__":
    unittest.main()
