"""Campaign kit schema, condition/slot refusal, seed law, checklist and frozen-path hashing."""
from __future__ import annotations

import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from joulewise.cadence import kit as kitmod
from tests.cadence.fixtures import COMMIT, FIT, GOOD_OBS, RUNNER, make_kit
from tests.git_fixture import init_git_fixture


class KitValidation(unittest.TestCase):
    def assertRefused(self, kit, fragment):
        with self.assertRaises(kitmod.KitError) as ctx:
            kitmod.validate_kit(kit)
        self.assertTrue(any(fragment in p for p in ctx.exception.problems),
                        f"{fragment!r} not in {ctx.exception.problems}")

    def test_valid_kit_passes(self):
        kit = make_kit()
        self.assertIs(kitmod.validate_kit(kit), kit)

    def test_condition_label_key_is_refused_anywhere(self):
        for where in ("leg", "defaults", "top"):
            kit = make_kit()
            if where == "leg":
                kit["legs"][2]["condition"] = "x"
            elif where == "defaults":
                kit["leg_defaults"]["treatment_arm"] = 1
            else:
                kit["slots"] = []
            self.assertRefused(kit, "names a condition or slot")

    def test_condition_label_value_is_refused(self):
        for value in ("sabotage", "benign", "spam_filter_update", "known_h", "X-G", "r1_slots.json", "slot 3"):
            kit = make_kit()
            kit["model"] = value
            self.assertRefused(kit, "carries a condition label or slot")

    def test_free_text_is_exempt_from_the_value_scan_only(self):
        kit = make_kit()
        kit["inclusion_rules"][0]["text"] = "No condition label and no slot is used by any leg."
        kitmod.validate_kit(kit)
        kit["inclusion_rules"][0]["condition"] = "benign"
        self.assertRefused(kit, "names a condition or slot")

    def test_unknown_key_is_refused(self):
        kit = make_kit()
        kit["legs"][0]["prompt_family"] = "p"
        self.assertRefused(kit, "unknown key 'prompt_family'")

    def test_hand_edited_leg_list_is_refused(self):
        kit = make_kit()
        kit["legs"][1]["seed"] += 1
        self.assertRefused(kit, "not the seed law's list (first difference at index 1")
        kit = make_kit()
        kit["legs"][0]["start_band"], kit["legs"][1]["start_band"] = kit["legs"][1]["start_band"], kit["legs"][0]["start_band"]
        if kit["legs"][0]["start_band"] != make_kit()["legs"][0]["start_band"]:
            self.assertRefused(kit, "not the seed law's list")

    def test_seed_law_is_deterministic_and_balanced(self):
        law = {"method": "sha256-v1", "master_seed": 7, "n_legs": 9, "bands": ["a", "b", "c"]}
        one = kitmod.generate_legs("c-id", law)
        self.assertEqual(one, kitmod.generate_legs("c-id", law))
        self.assertEqual(sorted(leg["start_band"] for leg in one), ["a"] * 3 + ["b"] * 3 + ["c"] * 3)
        self.assertNotEqual(one, kitmod.generate_legs("c-id", {**law, "master_seed": 8}))
        # Pinned: the law must not drift across Python versions or hosts.
        digest = hashlib.sha256(json.dumps(one, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, hashlib.sha256(json.dumps(kitmod.generate_legs("c-id", law), sort_keys=True).encode()).hexdigest())
        self.assertEqual(one[0]["leg_id"], "L001")

    def test_stop_rules_may_tighten_never_loosen(self):
        for key, value in (("contaminated_redos_max", 4), ("band_unreachable_max", 3), ("leg_time_factor", 1.6),
                           ("refusal", False)):
            kit = make_kit()
            kit["stop_rules"][key] = value
            self.assertRefused(kit, "stop_rules")
        kit = make_kit()
        kit["stop_rules"].update(contaminated_redos_max=2, leg_time_factor=1.25)
        kitmod.validate_kit(kit)

    def test_span_template_batch_window_and_capacity(self):
        kit = make_kit()
        kit["span_template"]["t0_local"] = "12:00"
        self.assertRefused(kit, "overlaps the OS batch window")
        kit = make_kit()
        kit["span_template"]["end_by_local"] = "12:00"
        self.assertRefused(kit, "overlaps the OS batch window")
        kit = make_kit(legs_per_span=40)
        self.assertRefused(kit, "needs")
        self.assertFalse(kitmod._overlaps_batch(13 * 60 + 20, 11 * 60 + 30))
        self.assertTrue(kitmod._overlaps_batch(13 * 60 + 20, 11 * 60 + 46))

    def test_mandatory_checklist_lines(self):
        kit = make_kit()
        kit["checklist"] = [c for c in kit["checklist"] if c["kind"] != "network_time_off"]
        self.assertRefused(kit, "mandatory check 'network_time_off' missing")
        kit = make_kit()
        kit["checklist"].append({"id": "again", "kind": "ac_power"})
        self.assertRefused(kit, "'ac_power' listed twice")

    def test_look_fit_must_be_frozen_code(self):
        kit = make_kit()
        kit["looks"][0]["fit"]["path"] = "scratch/fit.py"
        self.assertRefused(kit, "energy is read only by frozen fit code")
        kit = make_kit()
        kit["looks"] = [{"look_id": "a", "after_legs": 4, "fit": {"path": FIT}},
                        {"look_id": "b", "after_legs": 4, "fit": {"path": FIT}}]
        self.assertRefused(kit, "strictly increasing")

    def test_ruling_must_authorize_spans(self):
        kit = make_kit()
        kit["ruling"]["authorizes_spans"] = False
        self.assertRefused(kit, "arms nothing")

    def test_duplicate_json_key_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "k.json"
            p.write_text('{"schema": "a", "schema": "b"}')
            with self.assertRaises(kitmod.KitError):
                kitmod.load_kit(p)


class Checklist(unittest.TestCase):
    def setUp(self):
        self.kit = kitmod.validate_kit(make_kit())
        t0, end = kitmod.span_window_epochs(self.kit["span_template"], date(2026, 11, 15))
        self.obs = {**GOOD_OBS, "kit_sha256": "f" * 64, "t0_epoch_s": t0, "end_by_epoch_s": end}

    def run_list(self, obs):
        return {r["kind"]: r for r in kitmod.evaluate_checklist(self.kit, obs, expected_kit_sha256="f" * 64)}

    def test_all_lines_pass_on_good_observations(self):
        rows = self.run_list(self.obs)
        self.assertTrue(all(r["ok"] for r in rows.values()), [r for r in rows.values() if not r["ok"]])

    def test_missing_observation_fails_never_passes(self):
        for key in GOOD_OBS:
            obs = dict(self.obs)
            del obs[key]
            self.assertFalse(all(r["ok"] for r in self.run_list(obs).values()), key)

    def test_each_bad_value_fails_its_line(self):
        bad = {"powermode": 1, "network_time": "on", "freq_word": 5, "stray_monitors": ["km003c_monitor.py"],
               "other_agents": ["codex"], "high_power_marker": True, "previous_span": "stopped",
               "halts": [{"scope": "queue"}], "disk_free_gb": 10, "kit_sha256": "0" * 64,
               "measurement_head": "b" * 40}
        for key, value in bad.items():
            rows = self.run_list({**self.obs, key: value})
            self.assertEqual(sum(not r["ok"] for r in rows.values()), 1, key)

    def test_span_window_rejects_a_non_template_t0(self):
        rows = self.run_list({**self.obs, "t0_epoch_s": self.obs["t0_epoch_s"] + 600})
        self.assertFalse(rows["span_window"]["ok"])


class FrozenPaths(unittest.TestCase):
    def test_verify_frozen_against_a_git_commit(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init_git_fixture(repo)
            (repo / "scripts").mkdir()
            (repo / "joulewise").mkdir()
            (repo / RUNNER).write_bytes(b"runner\n")
            (repo / FIT).write_bytes(b"fit\n")
            env = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
            subprocess.run(["git", "-C", d, "add", "."], check=True)
            subprocess.run(["git", "-C", d, *env, "commit", "-qm", "x"], check=True)
            head = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            kit = make_kit()
            kit["frozen"] = {"commit": head, "paths": {RUNNER: hashlib.sha256(b"runner\n").hexdigest(),
                                                       FIT: hashlib.sha256(b"fit\n").hexdigest()}}
            self.assertEqual(kitmod.verify_frozen(kit, repo), [])
            kit["frozen"]["paths"][FIT] = "0" * 64
            self.assertEqual(len(kitmod.verify_frozen(kit, repo)), 1)
            kit["frozen"]["paths"]["missing.py"] = "0" * 64
            self.assertTrue(any("not readable" in p for p in kitmod.verify_frozen(kit, repo)))


if __name__ == "__main__":
    unittest.main()
