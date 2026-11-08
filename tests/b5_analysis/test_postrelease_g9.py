"""Exercise G9's output assertion with an in-memory driver result only."""
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise.b5_analysis import dry_run as d
from tests.b5_analysis import test_dry_run as fixture, test_sensitivity_guard as guard


class G9SidecarTests(unittest.TestCase):
    def invoke_g9(self, names):
        result = SimpleNamespace(code=2, record={'steps': [{
            'step': '4', 'status': 'tooling_refusal', 'refusal': guard.CODE,
            'outputs': [{'name': name, 'sha256': 'a'*64} for name in names]}]})
        case = mock.Mock()
        case.execute.return_value = result
        check = guard.DriverIntegrationGuardTests('test_G9_full_driver_refuses_wider_context_before_registered_writer')
        with mock.patch.object(fixture, 'DriverAcceptanceTests', return_value=case), \
                mock.patch.object(fixture.DriverDouble, 'calls', []):
            try:
                check.test_G9_full_driver_refuses_wider_context_before_registered_writer()
            finally:
                check.doCleanups()
        case.execute.assert_called_once()

    def test_registered_audit_sidecars_pass_g9(self):
        self.invoke_g9([d.STEP_CODES_NAME, d.vdl_mode_name('blind_on')])

    def test_prefix_lookalikes_and_writer_outputs_fail_g9(self):
        for name in (d.VDL_MODE_PREFIX+'invalid.json', d.VDL_MODE_PREFIX+'on.txt',
                     d.VDL_MODE_PREFIX+'shadow_10000.json', d.VDL_MODE_PREFIX+'on.json/extra',
                     'mint/extraction-alpha.json', d.STEP_CODES_NAME+'.extra'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.invoke_g9([d.STEP_CODES_NAME, name])
