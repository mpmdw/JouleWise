"""Failed-first episode provenance and U1 worker regressions for revision 4."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import controls_analysis as analysis, controls_release as release

from . import test_ctl_print as fixtures


PUBLIC_FIELDS = {"commit", "look_id", "manifest_sha256", "n_legs", "stage1_sha256"}


def _with_swapped_episodes(positions, relabel):
    left, right = positions[1], positions[4]
    assert (left.leg_id, right.leg_id) == ("L002", "L005")
    a, b = right.episode, left.episode
    if relabel:
        a = replace(a, episode_id=left.episode.episode_id)
        b = replace(b, episode_id=right.episode.episode_id)
    positions[1] = replace(left, episode=a)
    positions[4] = replace(right, episode=b)


def _with_gpu_gap(positions):
    leg = positions[1]
    assert leg.leg_id == "L002"
    traces = []
    for trace in leg.episode.power_traces:
        if trace.channel == "gpu_power":
            assert trace.nominal_interval_ns == analysis.NS
            kept = [i for i, t in enumerate(trace.t_ns) if not 100 <= t // analysis.NS < 105]
            trace = replace(trace, t_ns=tuple(trace.t_ns[i] for i in kept),
                            values=tuple(trace.values[i] for i in kept))
            assert (99 * analysis.NS, 105 * analysis.NS) in zip(trace.t_ns, trace.t_ns[1:])
        traces.append(trace)
    positions[1] = replace(leg, episode=replace(leg.episode, power_traces=tuple(traces)))


def run_binding_fixture(directory, mode):
    """Adapt only the invented reader result and caller arguments."""
    worker = release.run_controls_worker
    print_controls = analysis.print_controls

    def observed_analysis(*args, **kwargs):
        (directory / "analysis-started").touch(exist_ok=False)
        return print_controls(*args, **kwargs)

    def run(**kwargs):
        reader = kwargs["first_read"]

        def read(bindings):
            positions = list(reader(bindings))
            before = [(leg.work_bytes, leg.work_sha256) for leg in positions]
            if mode in ("swap", "swap_relabelled"):
                _with_swapped_episodes(positions, mode == "swap_relabelled")
            if mode in ("gap_bound", "gap_override"):
                _with_gpu_gap(positions)
            assert [(leg.work_bytes, leg.work_sha256) for leg in positions] == before
            return tuple(positions)

        kwargs["first_read"] = read
        if "gap_limits_ns" in kwargs:
            limits = dict.fromkeys(analysis.CHANNELS, 5 * analysis.NS)
            limits["dc_in"] = 2 * analysis.NS
            if mode == "gap_override":
                limits["gpu_rail"] = 10 * analysis.NS
            kwargs["gap_limits_ns"] = limits
        worker(**kwargs)

    with (patch.object(release, "run_controls_worker", side_effect=run),
          patch.object(analysis, "print_controls", side_effect=observed_analysis)):
        fixtures.worker_fixture(directory, "ok", synthetic_path=True)


class TestControlsBindingFreeze(unittest.TestCase):
    def _run(self, root, mode):
        for side in ("public", "private"):
            (root / side / "lm-ctl-01").mkdir(parents=True)
        launcher = ("import sys; from pathlib import Path; from tests.contracts.cadence_looks."
                    "ctl_print_binding_acceptance import run_binding_fixture; "
                    "run_binding_fixture(Path(sys.argv[1]), sys.argv[2])")
        return subprocess.run([sys.executable, "-B", "-c", launcher, str(root), mode],
                              cwd=fixtures.ROOT, capture_output=True)

    def _private(self, root):
        path = root / "private" / "lm-ctl-01" / "synthetic-output" / "controls.json"
        return json.loads(path.read_bytes())

    def test_episode_swap_refuses_before_analysis(self):
        for mode in ("swap", "swap_relabelled"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                self.assertTrue((root / "first-read").exists())
                public = root / "public" / "lm-ctl-01" / "PUBLIC.json"
                if result.returncode == 0:
                    report = self._private(root)
                    leg = report["legs"][1]
                    hidden_j = leg["channels"]["gpu_rail"]["hidden"]["call_j"]
                    self.fail(f"{mode} reached the writer: L002={hidden_j!r} J, "
                              f"qualified={report['aligned_power']['qualified']!r}")
                self.assertEqual((result.returncode, result.stdout), (1, b""), result.stderr)
                notice = result.stderr.splitlines()
                self.assertEqual(len(notice), 2, result.stderr)
                self.assertEqual(notice[0], b"stage2_error")
                self.assertFalse((root / "analysis-started").exists())
                self.assertFalse(public.exists())

    def test_caller_override_cannot_raise_registered_u1(self):
        public_bytes, observed = [], []
        for mode in ("gap_bound", "gap_override"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
                self.assertTrue((root / "first-read").exists())
                raw = (root / "public" / "lm-ctl-01" / "PUBLIC.json").read_bytes()
                self.assertEqual(set(json.loads(raw)), PUBLIC_FIELDS)
                public_bytes.append(raw)
                gpu = self._private(root)["legs"][1]["channels"]["gpu_rail"]
                hidden = gpu["hidden"]
                observed.append((gpu["baseline_w"], gpu["baseline_reason"], hidden["call_j"],
                                 hidden["floor"]["units"]))
        self.assertEqual(len(public_bytes), 2)
        self.assertEqual(public_bytes[0], public_bytes[1])
        self.assertEqual(observed, [(None, "gap_over_u1", None, None)] * 2)
