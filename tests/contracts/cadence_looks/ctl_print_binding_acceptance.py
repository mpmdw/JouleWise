"""Worker authority regressions for episode bytes, admission, and U1."""

from dataclasses import fields, replace
from hashlib import sha256
from importlib import import_module
from inspect import signature
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
    assert (left.binding.leg_id, right.binding.leg_id) == ("L002", "L005")
    a, b = right.episode_bytes, left.episode_bytes
    if relabel:
        a, b = json.loads(a), json.loads(b)
        a["episode_id"], b["episode_id"] = b["episode_id"], a["episode_id"]
        a, b = fixtures.manifest.canonical(a), fixtures.manifest.canonical(b)
    positions[1] = replace(left, episode_bytes=a)
    positions[4] = replace(right, episode_bytes=b)


def _with_gpu_gap(positions):
    positions = list(positions)
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
    return positions


def _with_stale_admission(positions, identity):
    return [replace(leg, admitted=False) if identity(leg) in ("L002", "L009") else leg for leg in positions]


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
            if mode in ("swap", "swap_relabelled"):
                _with_swapped_episodes(positions, mode == "swap_relabelled")
            if mode == "stale_admission":
                positions = _with_stale_admission(positions, lambda leg: leg.binding.leg_id)
            if mode == "attempt":
                leg = positions[1]
                positions[1] = replace(leg, binding=replace(leg.binding, attempt=leg.binding.attempt + 1))
            if mode == "request_tampering":
                for i in (1, 8):
                    object.__setattr__(bindings[i], "admitted", False)
                    positions[i] = replace(positions[i], admitted=False)
            return tuple(positions)

        kwargs["first_read"] = read
        if mode == "gap_override":
            try:
                worker(**kwargs, gap_limits_ns={"gpu_rail": 10 * analysis.NS})
            except TypeError as error:
                if "unexpected keyword argument 'gap_limits_ns'" not in str(error):
                    raise
            else:
                raise AssertionError("worker accepted a caller U1 override")
        if mode == "freeze_inputs":
            kwargs["freeze_inputs"] = {**kwargs["freeze_inputs"], "current_revision": "9" * 40}
        elif mode == "stage1_bytes":
            kwargs[mode] += b" "
        elif mode == "blind":
            kwargs[mode] = {**kwargs[mode], "n_legs": kwargs[mode]["n_legs"] - 1}
        elif mode in ("execution_host", "local_host"):
            kwargs[mode] = "foreign-host"
        elif mode in ("restricted", "public"):
            path = directory / f"alternate-{mode}" / "lm-ctl-01" / kwargs[mode].name
            path.parent.mkdir(parents=True)
            kwargs[mode] = path
        worker(**kwargs)

    close_positions = None
    if mode in ("gap_bound", "gap_override"):
        close_positions = _with_gpu_gap
    elif mode == "committed_unadmitted":
        def close_positions(positions):
            return _with_stale_admission(positions, lambda leg: leg.leg_id)
    with (patch.object(release, "run_controls_worker", side_effect=run),
          patch.object(analysis, "print_controls", side_effect=observed_analysis)):
        fixtures.worker_fixture(directory, "ok", synthetic_path=True, close_positions=close_positions)


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
        return json.loads((root / "private" / "lm-ctl-01" / "synthetic-output" / "controls.json").read_bytes())

    def _assert_post_read_refusal(self, root, result):
        self.assertTrue((root / "first-read").exists())
        self.assertEqual((result.returncode, result.stdout), (1, b""), result.stderr)
        notice = result.stderr.splitlines()
        self.assertEqual(len(notice), 2, result.stderr)
        self.assertEqual(notice[0], b"stage2_error")
        self.assertFalse((root / "analysis-started").exists())
        self.assertFalse((root / "public" / "lm-ctl-01" / "PUBLIC.json").exists())

    def test_episode_swap_refuses_before_analysis(self):
        for mode in ("swap", "swap_relabelled", "attempt"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                if result.returncode == 0:
                    report = self._private(root)
                    leg = report["legs"][1]
                    hidden_j = leg["channels"]["gpu_rail"]["hidden"]["call_j"]
                    self.fail(f"{mode} reached the writer: L002={hidden_j!r} J, "
                              f"qualified={report['aligned_power']['qualified']!r}")
                self._assert_post_read_refusal(root, result)

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

    def test_reader_admission_flags_cannot_change_committed_fit(self):
        for mode, n_legs, fit_legs, slope in (("control", 12, 6, 1.0), ("committed_unadmitted", 10, 4, None)):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
                blind = json.loads((root / "public" / "lm-ctl-01" / "PUBLIC.json").read_bytes())
                self.assertEqual(blind["n_legs"], n_legs)
                fit = self._private(root)["dose_response"]["gpu_rail"]
                self.assertEqual((len(fit["legs"]), fit["slope"]), (fit_legs, slope))
        for mode in ("stale_admission", "request_tampering"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                self._assert_post_read_refusal(root, self._run(root, mode))

    def test_unbound_worker_inputs_cannot_change_printed_values(self):
        self.assertEqual(set(signature(release.run_controls_worker).parameters),
                         {"freeze_inputs", "stage1_bytes", "blind", "execution_host", "local_host",
                          "restricted", "public", "first_read"})
        for mode in ("freeze_inputs", "stage1_bytes", "blind", "execution_host", "local_host"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (2, b"", b"REFUSE controls look before read\n"))
                self.assertFalse((root / "first-read").exists())
                self.assertFalse((root / "analysis-started").exists())
                self.assertFalse((root / "private" / "lm-ctl-01" / "synthetic-output").exists())

        outputs = []
        for mode in ("control", "restricted", "public"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=fixtures.ROOT) as directory:
                root = Path(directory)
                result = self._run(root, mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
                private_dir = "alternate-restricted" if mode == "restricted" else "private"
                public_dir = "alternate-public" if mode == "public" else "public"
                outputs.append((
                    (root / private_dir / "lm-ctl-01" / "synthetic-output" / "controls.json").read_bytes(),
                    (root / public_dir / "lm-ctl-01" / "PUBLIC.json").read_bytes(),
                ))
        self.assertEqual(outputs, outputs[:1] * 3)

    def test_reader_fields_require_their_committed_values(self):
        with fixtures.frozen_kernel():
            v2 = import_module("tests.contracts.cadence_looks.frozen_v3.test_ctl01_print_v2")
            leg = v2.make_leg("L002")
            row = fixtures.vectors.example()[0]["legs"]["L002"]
            identity = fixtures.controls.LegBinding(*row["identity"], row["role"], row["reference"])
            episode = v2.rec.to_json(leg.episode).encode()
            expected = fixtures.manifest.Stage1Leg(
                identity, leg.kind, leg.admitted, leg.g0_released, leg.work_sha256,
                leg.episode.episode_id, sha256(episode).hexdigest(),
            )
            read = release.LegRead(identity, leg.kind, leg.admitted, leg.g0_released, episode, leg.work_bytes)
            self.assertEqual(release._bound_positions((expected,), (read,)), (leg,))
            substitutions = {
                "binding": (replace(identity, leg_id="L005"), replace(identity, attempt=2),
                            replace(identity, attempt=True), replace(identity, span=2)),
                "kind": ("plain",),
                "admitted": (False, 1),
                "g0_released": (False, 1),
                "episode_bytes": (None, episode + b" "),
                "work_bytes": (None, leg.work_bytes + b" "),
            }
            self.assertEqual(set(substitutions), {field.name for field in fields(release.LegRead)})
            for field, values in substitutions.items():
                for value in values:
                    with self.subTest(field=field), self.assertRaisesRegex(ValueError, "controls_member_"):
                        release._bound_positions((expected,), (replace(read, **{field: value}),))
            for new_rows in ((), (read, read)):
                with self.assertRaises(ValueError):
                    release._bound_positions((expected,), new_rows)

    def test_registered_u1_uses_exact_nominal_period(self):
        for period, expected in ((1_000_000_000, 5_000_000_000), (250_000_000, 1_250_000_000),
                                 (100_000_000, 1_000_000_000)):
            trace = type("CadenceFixture", (), {"nominal_interval_ns": period})()
            self.assertEqual(analysis.registered_u1_ns(trace, "gpu_rail"), expected)
            self.assertEqual(analysis.registered_u1_ns(trace, "dc_in"), 2_000_000_000)
