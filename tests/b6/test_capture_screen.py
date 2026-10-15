import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.fixtures.b5_plan import corpus18_render


class ChainScreenTests(unittest.TestCase):
    def test_sealed_plans_without_screen_are_byte_identical(self):
        hashes = {"alpha": "0400e2f0b7c74d957f9fb57216c30cc4fc7bb55d6f347fa9fd2958527194afe8",
                  "beta": "f95f4875f88c2bcb97f1ea7f9d2d43fa76b9506343c83d7a9a4a17297d4cc217",
                  "gamma": "7ed69d6068f29d36bc8c8690f9817aec734fc6e07e338a46ae440c65281d3c2e"}
        for pack, expected in hashes.items():
            raw, *_ = corpus18_render.render_pack(pack, Path('/private/tmp/b6-baseline') / pack)
            normalized = raw.replace(str(corpus18_render.ROOT).encode(), b'REPO_ROOT')
            self.assertEqual(hashlib.sha256(normalized).hexdigest(), expected)

    def test_rendered_screen_under_zsh_on_fake_captures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw, *_ = corpus18_render.render_pack("alpha", root, bindings_overrides={"capture_screen": {
                "alignment_reference_s": "0.036462861644980", "bracket_screen_s": "0.014531",
                "operative_bound_stop_s": "0.092"}})
            rendered = raw.decode()
            self.assertIn("screen_b6_calibration", rendered)
            self.assertNotIn("screen_pre_calibration()", rendered)
            source = rendered[rendered.index("B6_ALIGNMENT_REFERENCE_S="):rendered.index('cd "$REPO"')]
            for value, rc, flagged in ((.030, 0, False), (.040, 0, True), (.100, 12, True), (.077469, 0, True)):
                (root / "instrument_evidence.json").write_text(json.dumps({"b_fiducial_s": value}))
                shell = "CLAIM_RUNS_ROOT=fixture\nflag() { print -r -- \"flag $1\"; }\nstop_chain() { print -r -- \"chain.stop $1 $2\"; exit $2; }\n"
                script = root / "screen.zsh"
                script.write_text(shell + source + '\nscreen_b6_calibration "$1"\n')
                ran = subprocess.run(["/bin/zsh", "-f", str(script), str(root)], capture_output=True, text=True)
                self.assertEqual(ran.returncode, rc, ran.stderr)
                self.assertEqual("flag calibration.alignment_above_reference" in ran.stdout, flagged)
                if rc:
                    self.assertIn("chain.stop operative_bound_above_stop 12", ran.stdout)

    def test_null_screen_values_never_become_zero_thresholds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for calibration in (
                dict.fromkeys(("alignment_reference_s", "bracket_screen_s", "operative_bound_stop_s")),
                {"alignment_reference_s": None, "bracket_screen_s": "0.014531", "operative_bound_stop_s": None},
                {"alignment_reference_s": None, "bracket_screen_s": None, "operative_bound_stop_s": "0.092"},
            ):
                raw, *_ = corpus18_render.render_pack("alpha", root, bindings_overrides={
                    "capture_screen": calibration, "spare_retries": False})
                rendered = raw.decode()
                self.assertNotIn("Spare-slot retry", rendered)
                source = rendered[rendered.index("B6_ALIGNMENT_REFERENCE_S="):rendered.index('cd "$REPO"')]
                script = root / "screen.zsh"
                script.write_text('CLAIM_RUNS_ROOT=fixture\nflag() { print -r -- "flag $1"; }\n'
                                  'stop_chain() { exit $2; }\n' + source + '\nscreen_b6_calibration "$1"\n')
                for ms in (30.6, 36.5, 40.14, 48.01):
                    (root / "instrument_evidence.json").write_text(json.dumps({"b_fiducial_s": ms / 1000}))
                    ran = subprocess.run(["/bin/zsh", "-f", str(script), str(root)], capture_output=True, text=True)
                    self.assertEqual(ran.returncode, 0, ran.stderr)
                    self.assertNotIn("flag calibration.alignment_above_reference", ran.stdout)

    def test_missing_opening_bound_stops_via_existing_chain_caller(self):
        from joulewise.b6.capture_screen import SCREEN_SHELL
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shell = ('CLAIM_RUNS_ROOT=fixture\nflag() { print -r -- "flag $1"; }\n'
                     'stop_chain() { print -r -- "chain.stop $1 $2"; exit $2; }\n')
            script = root / "screen.zsh"
            script.write_text(shell + SCREEN_SHELL + '\nscreen_b6_calibration "$1" || stop_chain pre_calibration_screen_failed 12\nprint continued\n')
            for document in (None, '{"b_fiducial_s":null}'):
                if document:
                    (root / "instrument_evidence.json").write_text(document)
                ran = subprocess.run(["/bin/zsh", "-f", str(script), str(root)], capture_output=True, text=True)
                self.assertEqual(ran.returncode, 12)
                self.assertIn("flag calibration.bracket_incomplete", ran.stdout)
                self.assertIn("chain.stop pre_calibration_screen_failed 12", ran.stdout)
                self.assertNotIn("continued", ran.stdout)
