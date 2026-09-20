"""Offline fixture: render and verify an evidence plan; never collect/install."""
import contextlib
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise import night_gate
from joulewise import quiet_predicate_campaign as campaign
from scripts import gen_evidence_night as generator
from tests.git_fixture import init_git_fixture
from tests.test_night_gate import make_plan

ROOT = Path(__file__).resolve().parents[1]


class EvidenceFixture:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qpe-fixture-", dir="/tmp")
        self.root = Path(self.temp.name)
        self.repo = self.root / "measurement"
        self.repo.mkdir()
        for directory in ("joulewise", "scripts"):
            shutil.copytree(ROOT / directory, self.repo / directory,
                            ignore=shutil.ignore_patterns("__pycache__"))
        for name in campaign.MANIFEST_PATHS:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        (self.repo / ".venv/bin").mkdir(parents=True)
        (self.repo / ".venv/bin/python").symlink_to(sys.executable)
        def git(*argv):
            return subprocess.check_output(["git", "-C", str(self.repo), *argv], stderr=subprocess.DEVNULL, text=True).strip()
        init_git_fixture(self.repo, "-q")
        git("add", *campaign.MANIFEST_PATHS)
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        self.head = git("rev-parse", "HEAD")
        self.custody = self.root / "custody"
        self.custody.mkdir()
        self.plan_path = self.custody / "night_plan.json"
        self.plan = replace(make_plan(), plan_id="qpe-fixture", repo_head=self.head,
            measurement_root=str(self.repo), measurement_head=self.head,
            custody_root=str(self.custody), chain_path=str(self.custody / "chain.zsh"),
            chain_sha256_path=str(self.custody / "chain.zsh.sha256"), window_max_s=9000,
            registration_path=campaign.PROTOCOL_PATH)
        self.write_plan()

    def write_plan(self):
        from joulewise.night_plan_writer import night_plan_json_bytes
        self.plan_path.write_bytes(night_plan_json_bytes(self.plan))

    @contextlib.contextmanager
    def installer_environment(self):
        from joulewise import night_agent_install as installer
        bin_dir = self.root / "bin"
        bin_dir.mkdir(exist_ok=True)
        courier = bin_dir / "claude"
        courier.write_text("#!/bin/sh\nexit 99\n")  # Render must never invoke it.
        courier.chmod(0o755)
        saved = {number: signal.getsignal(number) for number in installer.SIGNALS}
        try:
            with patch.dict(os.environ, {"PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", "")}):
                yield
        finally:
            for number, handler in saved.items():
                signal.signal(number, handler)

    def prepare_installer(self):
        head = subprocess.check_output(["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        now = time.time()
        self.plan = replace(self.plan, repo_head=head, authored_epoch_s=now,
                            t0_epoch_s=(int(now) // 60 + 24 * 60) * 60)
        self.write_plan()

    def close(self):
        self.temp.cleanup()


class EvidenceGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = EvidenceFixture()
        self.addCleanup(self.fixture.close)
        self.f = self.fixture

    def test_render_only_seals_tracked_inputs_and_both_chain_sidecars(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(generator.main(["--plan", str(self.f.plan_path), "--render-only"]), 0)
        wrapper = Path(self.f.plan.chain_path)
        manifest = json.loads(wrapper.with_name("evidence_manifest.json").read_text())
        self.assertEqual(manifest, campaign.manifest_for(self.f.plan))
        self.assertEqual(set(manifest["files"]), set(campaign.MANIFEST_PATHS))
        self.assertEqual(wrapper.read_text().count("export NIGHT_PAYLOAD_KIND="), 1)
        self.assertNotIn("CALIBRATION_LEDGER", wrapper.read_text())
        self.assertEqual(Path(self.f.plan.chain_sha256_path).read_text().split()[0], hashlib.sha256(wrapper.read_bytes()).hexdigest())
        if Path("/bin/zsh").is_file():
            subprocess.run(["/bin/zsh", "-n", str(wrapper)], check=True)
        self.assertFalse((self.f.custody / "night").exists())

    def test_relative_custody_root_refuses_at_the_desk(self):
        # Opus 90 S2: a relative custody root would seal a relative plan path.
        from scripts.gen_derivation_night import GenerationRefusal
        self.f.plan = replace(self.f.plan, custody_root=os.path.relpath(self.f.custody))
        self.f.write_plan()
        with self.assertRaisesRegex(GenerationRefusal, "night custody root must be an absolute path"):
            generator.generate(self.f.plan_path)
        self.assertFalse(Path(self.f.plan.chain_path).exists())

    def test_wrong_class_v4_and_frozen_window_refuse(self):
        from tests.test_quiet_admission import POLICY
        for change in ({"receipt_class": "REHEARSAL_STUB"}, {"window_max_s": 9001},
                       {"quiet_admission": dict(POLICY), "window_max_s": 9600}):
            with self.subTest(change=change):
                self.f.plan = replace(self.f.plan, **change)
                self.f.write_plan()
                with self.assertRaises((ValueError, generator.GenerationRefusal)):
                    generator.generate(self.f.plan_path)
                self.f.plan = replace(self.f.plan, receipt_class="DIAGNOSTIC_NO_PACK", window_max_s=9000, quiet_admission=None)

    def test_calibration_chain_and_override_options_refuse(self):
        for template in ("scripts/night_chains/calibration_derivation_only.zsh", "custom.zsh"):
            with self.assertRaisesRegex(generator.GenerationRefusal, "calibration/derivation"):
                generator.generate(self.f.plan_path, chain_template=template)
        for option in ("--settle-s", "--envelopes", "--duration-s", "--sample-interval-s"):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                generator.main(["--plan", str(self.f.plan_path), "--render-only", option, "1"])
            self.assertEqual(caught.exception.code, 2)
        Path(self.f.plan.chain_path).write_text("export CALIBRATION_LEDGER='/some/path'\n")
        with self.assertRaisesRegex(generator.GenerationRefusal, "calibration/derivation"):
            generator.generate(self.f.plan_path)

    def test_dirty_tracked_input_unruled_protocol_census_and_sidecar_refuse(self):
        source = self.f.repo / campaign.HARNESS_PATHS[0]
        data = source.read_bytes()
        source.write_bytes(data + b"\n# changed\n")
        with self.assertRaisesRegex(ValueError, "measurement_head"):
            generator.generate(self.f.plan_path)
        source.write_bytes(data)
        with patch.object(night_gate, "QPE01_PILOT_REGISTRATION_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "ruled"):
                generator.generate(self.f.plan_path)
        self.f.plan = replace(self.f.plan, plan_id="unsafe-claude-night")
        self.f.write_plan()
        with self.assertRaisesRegex(generator.GenerationRefusal, "census substring"):
            generator.generate(self.f.plan_path)
        self.f.plan = replace(self.f.plan, plan_id="qpe", chain_sha256_path="/tmp/wrong.sha256")
        self.f.write_plan()
        with self.assertRaisesRegex(generator.GenerationRefusal, "sidecar"):
            generator.generate(self.f.plan_path)

    def test_no_overwrite_of_authored_evidence(self):
        generator.generate(self.f.plan_path)
        with self.assertRaisesRegex(generator.GenerationRefusal, "exists"):
            generator.generate(self.f.plan_path)

    def test_staged_and_published_plan_render_identical_bytes(self):
        staged = self.f.root / "staging" / "night_plan.json"
        staged.parent.mkdir()
        os.replace(self.f.plan_path, staged)
        wrapper = generator.generate(staged)
        artifacts = (wrapper, Path(self.f.plan.chain_sha256_path),
                     wrapper.with_name("evidence_manifest.json"),
                     Path(str(wrapper) + ".chain-source.sha256"))
        staged_bytes = {path: path.read_bytes() for path in artifacts}
        self.assertEqual(night_gate.chain_literal(wrapper.read_text(), "EVIDENCE_PLAN_PATH"),
                         str(self.f.plan_path))
        self.assertFalse(self.f.plan_path.exists())
        os.replace(staged, self.f.plan_path)
        for path in artifacts:
            path.unlink()
        generator.generate(self.f.plan_path)
        self.assertEqual({path: path.read_bytes() for path in artifacts}, staged_bytes)

    def test_staged_installer_render_publication_probe_bindings_and_published_render(self):
        from joulewise import night_agent_install as installer
        import plistlib
        self.f.prepare_installer()
        staged = self.f.root / "staged.json"
        os.replace(self.f.plan_path, staged)
        generator.generate(staged)
        self.assertEqual(json.loads(staged.read_text())["schema"], "joulewise.night_plan.v2")
        self.assertFalse(self.f.plan_path.exists())
        with self.f.installer_environment():
            for phase, plan_path in (("staged", staged), ("published", self.f.plan_path)):
                if phase == "published":
                    os.replace(staged, self.f.plan_path)
                    bindings = installer.evidence_probe_bindings(self.f.plan, self.f.plan_path, sys.executable)
                    self.assertEqual(bindings["plan_sha256"], hashlib.sha256(plan_path.read_bytes()).hexdigest())
                rendered = self.f.root / phase
                output, errors = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    result = installer.main(["--plan", str(plan_path), "--python", sys.executable,
                                             "--render-only", str(rendered)])
                self.assertEqual(result, 0, errors.getvalue())
                self.assertIn('"payload_kind": "quiet_predicate_evidence"', output.getvalue())
                plists = list(rendered.glob("*.plist"))
                self.assertEqual(len(plists), 3)
                for path in plists:
                    argv = plistlib.loads(path.read_bytes())["ProgramArguments"]
                    expected = plan_path if "night-probe." in path.name else self.f.plan_path
                    self.assertEqual(argv[argv.index("--plan") + 1], str(expected.resolve()))
        self.assertEqual(list((self.f.custody / "night").iterdir()), [])

    def test_protocol_reread_mutation_refuses_before_execute(self):
        generator.generate(self.f.plan_path)
        from scripts import run_night
        night = self.f.custody / 'night'
        env = run_night._chain_environment(self.f.plan, night)
        env.update(EVIDENCE_PLAN_PATH=str(self.f.plan_path))
        manifest = campaign.manifest_for(self.f.plan)
        (self.f.repo / campaign.PROTOCOL_PATH).write_text('{}')
        with patch.dict(os.environ, env), \
                patch.object(campaign, 'verify_environment', return_value=(self.f.plan, manifest, 'a'*64)), \
                patch.object(campaign, 'execute') as execute:
            self.assertEqual(campaign.main(['run']), 2)
        execute.assert_not_called()
        refusal = json.loads((night / 'refusal.json').read_text())
        self.assertIn('protocol changed after manifest verification', refusal['refusal']['detail'])

    @unittest.skipUnless(Path('/bin/zsh').is_file(), 'zsh required for wrapper refusal fixture')
    def test_wrapper_source_mismatch_writes_typed_preexecute_refusal(self):
        generator.generate(self.f.plan_path)
        from scripts import run_night
        night = self.f.custody / 'night'
        (self.f.repo / campaign.CHAIN_PATH).write_text('# changed source\n')
        result = subprocess.run(['/bin/zsh', self.f.plan.chain_path],
            env=run_night._chain_environment(self.f.plan, night), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        refusal = json.loads((night / 'refusal.json').read_text())
        self.assertEqual(run_night.validate_refusal(refusal), [])
        self.assertIn('chain_source_sha256_mismatch', refusal['refusal']['detail'])
        self.assertFalse((night / 'evidence_processes.jsonl').exists())


if __name__ == "__main__":
    unittest.main()
