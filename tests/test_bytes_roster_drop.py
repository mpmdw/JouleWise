"""Registration §§2/10 alternative-roster regressions; synthetic desk work only."""
from __future__ import annotations

import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import bytes_analysis as ba
from scripts import bytes_twin as bt
from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]
DROP = "Qwen3-8B-8bit"


def design():
    # Desk manifests carry each model's public config_key (BY-REV F3: the Q1 census matches only on it).
    manifest = ba.read_json(ROOT / "tests/fixtures/bytes/campaign_design.json")
    for model in manifest["models"]:
        model.setdefault("config_key", "public-" + model["model"])
    return manifest


def manifest_without_drop():
    manifest = design()
    manifest["models"] = [m for m in manifest["models"] if m["model"] != DROP]
    return manifest


class RegisteredRosterTests(unittest.TestCase):
    def test_only_registered_alternative_and_full_roster_are_accepted(self):
        manifest = manifest_without_drop()
        self.assertIs(ba.validate_manifest(manifest), manifest)
        full = design()
        self.assertIs(ba.validate_manifest(full), full)
        wrong_nine = copy.deepcopy(full)
        wrong_nine["models"] = [m for m in wrong_nine["models"]
                                if m["model"] != "Llama-3.3-70B-Instruct-4bit"]
        eleven = copy.deepcopy(full)
        extra = copy.deepcopy(eleven["models"][0])
        extra["model"] = "unregistered-model"
        eleven["models"].append(extra)
        for invalid in (wrong_nine, eleven):
            with self.subTest(count=len(invalid["models"])):
                with self.assertRaises(ba.AnalysisError):
                    ba.validate_manifest(invalid)
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "manifest.json"
                    path.write_text(json.dumps(invalid))
                    with self.assertRaises(ValueError):
                        bt.analyse([], bt.read_manifest(path), [], stage="blinded")

    def test_frozen_families_follow_registered_roster(self):
        manifest = manifest_without_drop()
        frozen = ba.frozen_predictions([], manifest)
        self.assertEqual(frozen["H1_checks"], 18)
        self.assertEqual(frozen["H2_intervals"], {"rails": 8, "DC input": 8, "rest": 10})
        full = design()
        control = ba.frozen_predictions([], full)
        self.assertEqual(control["H1_checks"], 21)
        self.assertEqual(control["H2_intervals"], {"rails": 9, "DC input": 9, "rest": 11})


class RosterCLIChainTests(unittest.TestCase):
    def test_nine_model_registered_chain_and_twin_agreement(self):
        from tests import test_bytes_agreement as agreement

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, commands = build_campaign(root, drop=True)
            self.assertEqual(len(manifest["models"]), 9)
            self.assertNotIn(DROP, (root / "manifest.json").read_text())
            # The native registration and drawn key identities contain no dropped row.
            for path in (root / "private-keys").rglob("*.json"):
                self.assertNotIn(DROP, path.read_text())
            run_chain(root, manifest, commands, twin=True)
            frozen = ba.read_json(root / "out/a-fit/predictions.json")
            self.assertEqual(frozen["H1_checks"], 18)
            self.assertEqual(frozen["H2_intervals"], {"rails": 8, "DC input": 8, "rest": 10})
            for tag in ("a-fit/fit_pass_estimates", "a-held/heldout_pass_estimates"):
                for row in ba.read_json(root / "out" / (tag + ".json")):
                    if row["status"] == "computed":
                        # Same function and inputs: bit identity, with no new comparison bar.
                        self.assertEqual(row["h_j"], ba.student_t_quantile(
                            1 - .05 / 36, row["df"]) * math.sqrt(row["variance"]))
            primary = lambda r: r["basis"] == "gross primary" and r["selection"] == "primary"
            rows = [r for r in ba.read_json(root / "out/a-held/h2.json") if primary(r)]
            self.assertEqual({r["boundary"]: r["k"] for r in rows},
                             {"rails": 8, "DC input": 8, "rest": 10})
            for tag in ("t-blinded", "t-1", "t-2"):
                result = ba.read_json(root / "out" / (tag + ".json"))
                self.assertEqual(result["multiplicity"]["H1"]["family_size"], 18)
            for path in (root / "out").rglob("*.json"):
                self.assertNotIn(DROP, path.read_text(), str(path))
            recorder = agreement.compare_campaign(root)
            self.assertFalse(recorder.above(), [agreement.describe(r) for r in recorder.above()])
            print("NINE_MODEL_AGREEMENT", json.dumps(recorder.counts(), sort_keys=True))
            print("NINE_MODEL_COMMANDS", json.dumps(commands))


def command(args, commands, *, cwd=ROOT):
    result = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                            env={**os.environ, "JW_B5_SYNTHETIC_ONLY": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    commands.append({"argv": [str(a) for a in args], "exit": result.returncode})
    if result.returncode:
        raise AssertionError(f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def build_campaign(root, *, drop):
    """Real reducer/export fixture in a child process, before native subset releases."""
    commands = []
    generate = '''
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("campaign", "tests/fixtures/bytes/campaign.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
root = Path(sys.argv[1])
manifest = fixture.archive_campaign(root, seed=1100, non_claim=False, release="none",
    subpack_sessions=True, drop_8b_8bit=sys.argv[2] == "drop")
(root / "manifest.json").write_text(json.dumps(manifest))
'''
    command([sys.executable, "-B", "-c", generate, root, "drop" if drop else "full"], commands)
    manifest = ba.read_json(root / "manifest.json")
    config_dirs = []
    for model in manifest["models"]:
        run_id = (model["model"] + "-0").lower().replace(".", "-")
        source = next(Path(s["archive"]) / "sources/claim-runs" / run_id / "config.json"
                      for s in manifest["sessions"] if (
                          Path(s["archive"]) / "sources/claim-runs" / run_id / "config.json").is_file())
        dest = root / "configs" / model["model"]
        dest.mkdir(parents=True)
        shutil.copyfile(source, dest / "run.json")
        config_dirs.append(str(dest.relative_to(root)))
    registration = root / "registrations/bytes/registration.json"
    registration.parent.mkdir(parents=True)
    registration.write_text(json.dumps({"pack_id": "bytes", "blinding_group": "bytes",
                                       "modules": [{"config_dirs": config_dirs}]}))
    return manifest, commands


def run_chain(root, manifest, commands, *, twin=False, code_root=ROOT, label="out"):
    out = root / label
    out.mkdir()
    analysis = [sys.executable, "-B", code_root / "scripts/bytes_analyze.py", "--export", root / "export",
                "--manifest", root / "manifest.json"]
    twin_args = [sys.executable, "-B", code_root / "scripts/bytes_twin.py", "--export-dir", root / "export",
                 "--manifest", root / "manifest.json"]
    for session in manifest["sessions"]:
        twin_args += ["--archive", session["archive"]]
    withheld = sorted((root / "private-keys/bytes/withheld").rglob("*.runs.csv"))

    def analyze(stage, tag, *extra):
        command([*analysis, "--stage", stage, "--out", out / tag, *extra], commands, cwd=code_root)
        (out / (tag + ".exit")).write_text("0\n")

    def run_twin(stage, tag, keys=None):
        args = [*twin_args, "--stage", stage, "--out", out / (tag + ".json")]
        if keys:
            args += ["--key-dir", root / keys]
        if stage == "2":
            for path in withheld:
                args += ["--export", path]
        command(args, commands, cwd=code_root)
        (out / (tag + ".exit")).write_text("0\n")

    def release(stage, keys, commit=None):
        args = [sys.executable, "-B", code_root / "scripts/b6_release_subset.py",
                "--pack-records-root", root / "private-keys", "--blinding-group", "bytes",
                "--registrations-root", root / "registrations", "--project-root", root,
                "--stage", stage, "--out", root / (label + "-" + stage + "-keys"), "--keys", *sorted(keys)]
        if commit:
            args += ["--stage1-commit", commit]
        command(args, commands, cwd=code_root)
        return label + "-" + stage + "-keys"

    analyze("blinded", "a-blinded")
    if twin:
        run_twin("blinded", "t-blinded")
    fit_keys = {"neg8_reference", *(m["config_key"] for m in manifest["models"] if m["role"] == "fit")}
    fit = release("fit", fit_keys)
    analyze("fit", "a-fit", "--key-dir", root / fit)
    if twin:
        run_twin("1", "t-1", fit)
    init_git_fixture(out / "a-fit", "-q")
    command(["git", "-C", out / "a-fit", "add", "."], commands)
    command(["git", "-C", out / "a-fit", "-c", "user.name=BYTES Synthetic", "-c", "user.email=fixture",
             "commit", "-qm", "Freeze synthetic predictions"], commands)
    commit = command(["git", "-C", out / "a-fit", "rev-parse", "HEAD"], commands).strip()
    analyze("blinded", "a-postcommit", "--stage1-commit", commit)
    all_keys = {"neg8_reference", *(m["config_key"] for m in manifest["models"])}
    held = release("heldout", all_keys, commit)
    analyze("heldout", "a-held", "--key-dir", root / held,
            "--predictions", out / "a-fit/predictions.json")
    if twin:
        run_twin("2", "t-2", held)
    return out


if __name__ == "__main__":
    unittest.main()
