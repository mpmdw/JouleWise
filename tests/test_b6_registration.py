"""Pack-schema desk checks and disposable Git observations."""
import json
import importlib
import inspect
import subprocess
import tempfile
import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from joulewise.b6.pack_registration import Registration, load, open_packs, validate
from joulewise.flags.catalog import load_catalog
from tests.git_fixture import init_git_fixture
from joulewise.b6 import registration as acceptance_registration
from joulewise.b6 import plan_inputs

ROOT = Path(__file__).resolve().parents[1]
CATALOG = load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")


class AcceptanceDirectoryTests(unittest.TestCase):
    def test_copies_parse_and_are_exact_without_following_source_paths(self):
        target = ROOT / acceptance_registration.DEFAULT_DIR_RELATIVE
        for name, loader in (("identity_pins.json", acceptance_registration.load_identity_pins),
                             ("sizing_b5.json", acceptance_registration.load_sizing)):
            with self.subTest(name=name):
                original = ROOT / 'configs/campaigns/v5_claim_25g83' / name
                if name == 'sizing_b5.json':
                    # B6 adds pack-specific BYTES rows; the replication source
                    # and every original field/row must still be unchanged.
                    current, baseline = json.loads((target / name).read_text()), json.loads(original.read_text())
                    for key, value in baseline.items():
                        if key == 'packs':
                            self.assertEqual({k: current[key][k] for k in value}, value)
                        else:
                            self.assertEqual(current[key], value)
                else:
                    # B6 adds BYTES identity evidence (new units, bytes_* fields,
                    # bytes_c4); every block-5 field of every block-5 unit stays.
                    current, baseline = json.loads((target / name).read_text()), json.loads(original.read_text())
                    for key, value in baseline.items():
                        if key != 'units':
                            self.assertEqual(current[key], value, key)
                    for unit, fields in baseline['units'].items():
                        self.assertEqual({k: current['units'][unit][k] for k in fields}, fields, unit)
                        self.assertTrue(all(k.startswith('bytes') for k in set(current['units'][unit]) - set(fields)),
                                        unit)
                    self.assertTrue(all(k.startswith('bytes') for k in set(current) - set(baseline)))
                self.assertIsInstance(loader(target), dict)
        self.assertEqual(acceptance_registration.load_precheck_thresholds(target), {})
        loaded = acceptance_registration.load(target)
        self.assertEqual(acceptance_registration.SCHEMA, loaded["schema"])
        self.assertEqual([], loaded["defaults_used"], "the registered file states every value")

    def test_all_six_pass1_sizing_rows_reach_real_consumers(self):
        target = ROOT / acceptance_registration.DEFAULT_DIR_RELATIVE
        sized = acceptance_registration.load_sizing(target)
        for n in range(1, 7):
            pack = f'bytes-s{n}-p1'
            with self.subTest(pack=pack):
                self.assertIn(pack, sized['packs'], 'pass-1 sizing cannot be vacuously empty')
                row = sized['packs'][pack]
                self.assertEqual(row['pack_id'], pack)
                self.assertTrue(plan_inputs.valid_disk_terms(row.get('disk_derivation')))
                identities = {name: {'path': name, 'sha256': 'a' * 64}
                              for name in ('identity-epoch.json', 't1-bindings.json')}
                # build() consumes only the supplied identity locators; this
                # verifies the sizing seam without pretending to attest Mac identity.
                inputs = plan_inputs.build(ROOT, target, pack, 'sizing-desk-test', identities,
                    custody_root='/synthetic/custody', runs_parent='/synthetic/runs',
                    claim_backup='/synthetic/claim', bound_backup='/synthetic/bound', head='a' * 40)
                self.assertEqual(inputs['programmed_span_s']['seconds'], row['programmed_span_s'])
                self.assertEqual(inputs['T_stream_max_s']['seconds'], row['T_stream_max_s'])
                plan_inputs.encode_disk_budget(inputs, row['disk_derivation'])
                budget = inputs['disk_budget']
                self.assertEqual(budget['member_count'], 125 if n <= 4 else 75)
                self.assertGreater(budget['bytes_per_member'], 0)
                self.assertEqual(3 * budget['member_count'] * budget['bytes_per_member']
                                 + budget['headroom_bytes'], row['disk_derivation']['required_free_bytes'])

    def test_malformed_inputs_fail_the_loader_without_filling_measurements(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, loader, value in (
                ('identity_pins.json', acceptance_registration.load_identity_pins, {'schema': acceptance_registration.IDENTITY_SCHEMA}),
                ('sizing_b5.json', acceptance_registration.load_sizing, {'schema_version': acceptance_registration.SIZING_SCHEMA}),
                ('precheck_thresholds.json', acceptance_registration.load_precheck_thresholds, {'clock': {'typo': 1}}),
                ('acceptance.json', acceptance_registration.load, {'schema': acceptance_registration.SCHEMA,
                    'pack_id': 'test', 'registered_commit': 'a' * 40})):
                (root / name).write_text(json.dumps(value))
                with self.subTest(name=name), self.assertRaises(ValueError):
                    loader(root)


def registrations(*, target=3):
    regs = {}
    for p in ("alpha", "beta", "gamma"):
        data = deepcopy(load(ROOT / f"configs/b6/packs/{p}/registration.json").data)
        data.update(status="registered", target_sessions=target)
        data["estimators"] = [{"name": "desk", "library": "joulewise.test", "function": "desk", "version": "fixture"}]
        data.pop("draft_notes", None)
        # Synthetic registrations decide every previously unset effect.
        data["flag_effects"] = {code: effect if effect is not None else CATALOG.effect(code)
                                for code, effect in data["flag_effects"].items()}
        data["stopping"].update(count=target, end_t0_before="2026-11-01T00:00:00+00:00")
        regs[p] = Registration(data, commit_time=1)
    return regs


def modular(pack="beta", *, interleave="none"):
    reg = registrations()[pack]
    data = deepcopy(reg.data)
    tree = json.loads((ROOT / reg.plan_tree_ref).read_text())
    science = [s for s in tree["stage_graph"] if "science" in s["stage_id"]]
    modules = []
    for phase in ("decode", "prefill"):
        dirs = []
        for s in science:
            if ("prefill" in s["stage_id"]) == (phase == "prefill"):
                args = s["launch"]["commands"][0]["argv_template"]["arguments"]
                dirs.append(args[0]["value"])
        kind = "contrast" if pack == "gamma" else "floor"
        modules.append({"module_id": pack + "-" + phase, "kind": kind, "phase": phase,
                        "config_dirs": dirs, "est_minutes": 120, "run_count": 40 if kind == "contrast" else 50})
    data.update(session_shape="modular", plan_tree_ref=None, modules=modules,
                pack_unit=[m["module_id"] for m in modules], interleave=interleave)
    return replace(reg, data=data)


class RegistrationTests(unittest.TestCase):
    def test_registered_fixed_tree_exists_under_root_and_has_stage_graph(self):
        reg = registrations()["alpha"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "plan.json"
            reg = replace(reg, data={**reg.data, "plan_tree_ref": "plan.json"})
            self.assertEqual(validate(reg, CATALOG, root=root), ["plan_tree_ref"])
            for contents in ("broken", "{}", "[]", '{"stage_graph": null}'):
                path.write_text(contents)
                with self.subTest(contents=contents):
                    self.assertEqual(validate(reg, CATALOG, root=root), ["plan_tree_ref"])
            path.write_text('{"stage_graph": []}')
            self.assertEqual(validate(reg, CATALOG, root=root), [])
            escaped = replace(reg, data={**reg.data, "plan_tree_ref": "../plan.json"})
            self.assertEqual(validate(escaped, CATALOG, root=root), ["plan_tree_ref"])
            self.assertEqual(validate(replace(escaped, data={**escaped.data, "status": "draft"}), CATALOG, root=root), [])

    def test_registered_estimators_nonempty_but_empty_effects_valid(self):
        reg = registrations()["beta"]
        reg = replace(reg, data={**reg.data, "flag_effects": {}})
        self.assertEqual(validate(reg, CATALOG), [])
        reg = replace(reg, data={**reg.data, "estimators": []})
        self.assertEqual(validate(reg, CATALOG), ["estimators"])
        self.assertEqual(validate(replace(reg, data={**reg.data, "status": "draft"}), CATALOG), [])

    def test_template_and_registered_packs_validate(self):
        template = load(ROOT / "configs/b6/registration_template.json")
        self.assertEqual(validate(template, CATALOG), [])
        for p in ("alpha", "beta", "gamma"):
            reg = load(ROOT / f"configs/b6/packs/{p}/registration.json")
            self.assertEqual(validate(reg, CATALOG, root=ROOT), [])
            self.assertEqual(reg.status, "registered")
            self.assertEqual(len(reg.estimators), 4 if p == "gamma" else 3)
            for estimator in reg.estimators:
                module = importlib.import_module(estimator["library"])
                self.assertTrue(inspect.isfunction(getattr(module, estimator["function"])))
                self.assertEqual(estimator["version"], "6849cb7e3")
        with self.assertRaises(FrozenInstanceError):
            template.path = "changed"

    def test_every_required_field_named_when_missing_or_mistyped(self):
        reg = modular()
        # Optional fixed reference and defaultable pack_unit/interleave omitted.
        for field in set(reg.data) - {"plan_tree_ref", "pack_unit", "interleave"}:
            for mutation in ("missing", "mistyped"):
                d = deepcopy(reg.data)
                if mutation == "missing":
                    del d[field]
                else:
                    d[field] = 99 if field not in {"target_sessions", "minimum_sessions", "attempts_before_pause"} else "wrong"
                with self.subTest(field=field, mutation=mutation):
                    self.assertTrue(any(field in e for e in validate(Registration(d), CATALOG)))
        d = deepcopy(reg.data)
        d["minimum_sessions"] = 4
        self.assertIn("minimum_sessions", validate(Registration(d), CATALOG))

    def test_minimum_two_only_for_replications_and_never_above_target(self):
        for kind, minimum, target, valid in (
            ("replication", 1, 3, False), ("replication", 2, 3, True),
            ("new", 1, 1, True), ("new", 0, 3, False), ("new", 4, 3, False),
        ):
            d = deepcopy(registrations()["alpha"].data)
            d.update(kind=kind, minimum_sessions=minimum, target_sessions=target)
            d["stopping"]["count"] = target
            if kind == "new":
                d["corpus"]["stop_after_valid"] = 12
            with self.subTest(kind=kind, minimum=minimum, target=target):
                self.assertEqual(validate(Registration(d), CATALOG), [] if valid else ["minimum_sessions"])

    def test_registered_effects_match_catalog_and_have_no_draft_notes(self):
        for p in ("alpha", "beta", "gamma"):
            reg = load(ROOT / f"configs/b6/packs/{p}/registration.json")
            with self.subTest(pack=p):
                for code, effect in reg.flag_effects.items():
                    self.assertEqual(effect, CATALOG.effect(code), code)
                for code in ("code.executed_differs_from_sealed", "contention.request_overlap",
                             "diagnostic.s1_structural"):
                    self.assertEqual(reg.flag_effects[code], "DISCLOSE", code)
                self.assertEqual(reg.flag_effects["model.identity_mismatch"], "DISCLOSE")
                self.assertNotIn("draft_notes", reg.data)

    def test_draft_notes_ignored_for_drafts_and_refused_when_registered(self):
        d = deepcopy(registrations()["alpha"].data)
        d["draft_notes"] = ["Unresolved catalog code"]
        self.assertEqual(validate(Registration(d), CATALOG), ["draft_notes"])
        d["draft_notes"] = []
        self.assertEqual(validate(Registration(d), CATALOG), ["draft_notes"])
        d.update(status="draft", draft_notes={"ignored": True})
        self.assertEqual(validate(Registration(d), CATALOG), [])

    def test_unknown_code_count_date_and_draft_relaxations(self):
        reg = modular()
        for field, mutate, error in (
            ("flag_effects", lambda d: d["flag_effects"].update({"unknown.code": "DISCLOSE"}), "unknown.code"),
            ("modules", lambda d: d["modules"][0].update(run_count=48), "run_count"),
            ("stopping", lambda d: d["stopping"].update(end_t0_before="2026-11-01T00:00:00"), "end_t0_before"),
        ):
            d = deepcopy(reg.data)
            mutate(d)
            self.assertTrue(any(error in x for x in validate(Registration(d), CATALOG)))
        d = deepcopy(reg.data)
        d["flag_effects"]["disk.low"] = None
        d["estimators"] = [{"name": "test", "library": "joulewise.test", "function": "test", "version": None}]
        d["stopping"]["end_t0_before"] = None
        self.assertTrue(validate(Registration(d), CATALOG))
        d["status"] = "draft"
        self.assertEqual(validate(Registration(d), CATALOG), [])
        fixed = deepcopy(registrations()["alpha"].data)
        del fixed["plan_tree_ref"]
        self.assertIn("plan_tree_ref", validate(Registration(fixed), CATALOG))

    def test_module_fields_and_real_manifest_count_named(self):
        reg = modular()
        for field in ("module_id", "kind", "phase", "config_dirs", "est_minutes"):
            for value in (None, [], {}):
                d = deepcopy(reg.data)
                d["modules"][0][field] = value
                with self.subTest(field=field, value=value):
                    self.assertIn("modules[0]." + field, validate(Registration(d), CATALOG))
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            d = deepcopy(reg.data)
            d["modules"] = [d["modules"][0]]
            d["pack_unit"] = [d["modules"][0]["module_id"]]
            d["modules"][0].pop("run_count")
            d["modules"][0]["config_dirs"] = ["configs/synthetic"]
            manifest = repo / "configs/synthetic/order_manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"executed_order": [{}] * 48}))
            path = repo / "configs/b6/packs/test/registration.json"
            self.assertIn("modules[0].run_count", validate(Registration(d, str(path)), CATALOG))

    def test_clean_committed_open_dirty_untracked_and_draft_not_open(self):
        # Explicit brief exception: Git runs only in this disposable repo.
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            init_git_fixture(repo)

            def run(argv):
                self.assertEqual(argv[:3], ["git", "-C", str(repo)])
                return subprocess.run(argv, capture_output=True, text=True, check=False)

            run(["git", "-C", str(repo), "config", "--local", "user.name", "Fixture"])
            run(["git", "-C", str(repo), "config", "--local", "user.email", "fixture.invalid"])
            cat = repo / "catalog.json"
            cat.write_text(json.dumps({"schema_version": "joulewise.flag_catalog.v1", "codes": dict(CATALOG.codes)}))
            d = deepcopy(registrations()["alpha"].data)
            d["flag_catalog"] = "catalog.json"
            path = repo / "configs/b6/packs/alpha/registration.json"
            path.parent.mkdir(parents=True)
            tree = repo / d["plan_tree_ref"]
            tree.parent.mkdir(parents=True)
            tree.write_text('{"stage_graph": []}')
            path.write_text(json.dumps(d))
            rejected = []
            self.assertEqual(open_packs(repo, run=run, rejected=lambda *x: rejected.append(x)), [])
            self.assertIn("untracked_or_dirty", rejected[-1][1])
            run(["git", "-C", str(repo), "add", "."])
            committed = run(["git", "-C", str(repo), "commit", "-m", "fixture registration"])
            self.assertEqual(committed.returncode, 0, committed.stderr)
            opened = open_packs(repo, run=run)
            self.assertEqual([r.pack_id for r in opened], ["alpha"])
            self.assertGreater(opened[0].commit_time, 0)
            tree.unlink()
            self.assertEqual(open_packs(repo, run=run, rejected=lambda *x: rejected.append(x)), [])
            self.assertIn("plan_tree_ref", rejected[-1][1])
            tree.write_text('{"stage_graph": []}')
            path.write_text(json.dumps(d) + "\n")
            self.assertEqual(open_packs(repo, run=run), [])
            d["status"] = "draft"
            path.write_text(json.dumps(d))
            run(["git", "-C", str(repo), "add", "."])
            run(["git", "-C", str(repo), "commit", "-m", "fixture draft"])
            self.assertEqual(open_packs(repo, run=run), [])
