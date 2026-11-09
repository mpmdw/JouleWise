"""Runtime calibration identity witnesses (lead ruling on r23j2-sol P2).

Every drift runs in its own subprocess, so the test process's modules stay
pristine. The first three are Sol's r23j2 probes, applied after the engine is
loaded, exactly as they would act at run time:
- an import-time side effect in another module;
- an importlib monkeypatch;
- a star import into the cadence namespace.
The rest are a monkeypatch of CAL_TARGET_PER_PAIR from a separate imported
module and further rebinding paths. Each must refuse with
calibration_identity_drift in both analyze() and io.load().
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest

from joulewise.align.v4_analysis import calibration_identity as ci

ROOT = Path(__file__).resolve().parents[2]
CADENCE = 'joulewise.align.apple.v4_cadence'
PROBE = textwrap.dedent('''
    import sys
    sys.path[:0] = [{helpers!r}, {root!r}]
    from joulewise.align.v4_analysis import analyze, engine
    from joulewise.align.v4_analysis.io import load
    from joulewise.align.v4_analysis.synthetic import series
    from joulewise.align.apple import v4_cadence
    import scripts.align_v4_kit as kit
    payload = series(turns=4)
    fill, _ = analyze(payload)                     # healthy before the drift
    assert fill['calibration']['decision'] == 'calibration_complete', fill['calibration']
    {drift}
    outcomes = []
    for call in (lambda: analyze(payload), lambda: load({path!r})):
        try:
            call()
            outcomes.append('ACCEPTED')
        except Exception as error:
            outcomes.append('REFUSED' if str(error).startswith('calibration_identity_drift')
                            else 'OTHER: '+type(error).__name__+': '+str(error)[:200])
    print('|'.join(outcomes))
''')
HELPERS = {
    'r23j2_effect.py': "import sys\nsys.modules['joulewise.align.apple.v4_cadence'].CAL_WINDOWS = 9\n",
    'r23j2_values.py': 'CAL_WINDOWS = 9\n',
    'r23j_target_patch.py': ("import joulewise.align.apple.v4_cadence as cadence\n"
                             "cadence.CAL_TARGET_PER_PAIR = 38\n"),
}
DRIFTS = {
    'sol: import-time side effect of another module': 'import r23j2_effect',
    'sol: importlib monkeypatch': "import importlib\nimportlib.import_module('joulewise.align.apple.v4_cadence').CAL_WINDOWS = 9",
    'sol: star import into the cadence namespace': "exec('from r23j2_values import *', v4_cadence.__dict__)",
    'CAL_TARGET_PER_PAIR monkeypatched by a separate module': 'import r23j_target_patch',
    'engine rebinding to a wrapper': ("_real = engine.calibration_stop\n"
                                      "engine.calibration_stop = lambda *a, **k: _real(*a, **k)"),
    'cadence function wrapped in place': ("import functools\n_real = v4_cadence.calibration_stop\n"
        "v4_cadence.calibration_stop = functools.wraps(_real)(lambda *a, **k: _real(*a, **k))"),
    'code object swapped': "v4_cadence.slot_of.__code__ = (lambda window_id: window_id).__code__",
    'default changed': "v4_cadence.calibration_stop.__defaults__ = ([],)",
    'kit constant patched': "kit.UNSIGNED = 'PENDING'",
    'kit function replaced': "kit.valid_lead_signature = lambda signature: True",
    'helper module alias swapped': "import json\nv4_cadence.re = json",
    'module replaced in sys.modules': ("import types\n_fake = types.ModuleType('joulewise.align.apple.v4_cadence')\n"
        "_fake.__dict__.update(v4_cadence.__dict__)\nsys.modules['joulewise.align.apple.v4_cadence'] = _fake"),
    'constant tuple replaced by an equal-looking list': "v4_cadence.STRUCTURAL_BARS = list(v4_cadence.STRUCTURAL_BARS)",
}


class RuntimeIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.helpers = Path(cls.tmp.name)
        for name, body in HELPERS.items():
            (cls.helpers/name).write_text(body)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_probe(self, drift):
        script = PROBE.format(helpers=str(self.helpers), root=str(ROOT), drift=drift,
                              path=str(self.helpers/'missing-input.json'))
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
        result = subprocess.run([sys.executable, '-B', '-c', script], capture_output=True, text=True,
                                cwd=self.helpers, env=env, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        return result.stdout.strip().splitlines()[-1]

    def test_every_drift_refuses_in_analyze_and_load(self):
        for label, drift in DRIFTS.items():
            with self.subTest(drift=label):
                self.assertEqual(self.run_probe(drift), 'REFUSED|REFUSED')

    def test_healthy_runtime_passes_and_load_reaches_its_own_checks(self):
        # Without drift, load proceeds past the identity check (to a missing file).
        out = self.run_probe('pass')
        self.assertEqual(out.split('|')[0], 'ACCEPTED')
        self.assertTrue(out.split('|')[1].startswith('OTHER'))


class IdentityPinTests(unittest.TestCase):
    def test_live_objects_equal_r11_pins_and_check_is_cheap(self):
        live = ci.check()
        self.assertEqual(live, ci.PINS)
        self.assertEqual(sorted(len(row) for row in ci.PINS.values()), [2, 15])
        started = time.perf_counter()
        for _ in range(20):
            ci.check()
        per_check = (time.perf_counter()-started)/20
        self.assertLess(per_check, .05)

    def test_digests_ignore_hash_seed(self):
        script = ("import json,sys; sys.path.insert(0, %r)\n"
                  "from joulewise.align.v4_analysis import calibration_identity as ci\n"
                  "print(json.dumps(ci.check(), sort_keys=True))") % str(ROOT)
        outs = {subprocess.run([sys.executable, '-B', '-c', script], capture_output=True, text=True,
                               env={**os.environ, 'PYTHONHASHSEED': seed}, timeout=300).stdout
                for seed in ('0', '1', '4242')}
        self.assertEqual(len(outs), 1)

    def test_interpreter_is_pinned(self):
        self.assertEqual(ci.INTERPRETER, tuple(sys.version_info[:2]))


if __name__ == '__main__':
    unittest.main()
