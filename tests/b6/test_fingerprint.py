import copy
import json
from pathlib import Path

from joulewise.b6 import fingerprint as f
from joulewise.hazards import clock
from joulewise.hazards.base import Context
from tests.hazards.fakes import Runner, FakeClocks, completed, BOOT_UUID
from tests.b6.support import DeskCase, fp, PACKS


class FingerprintTests(DeskCase):
    def test_14_digest_key_order_and_every_dependency(self):
        value = fp()
        self.assertEqual(f.digest(value), f.digest(dict(reversed(list(value.items())))))
        index = self.root / 'passes.jsonl'
        f.record_pass(value, self.root / 'smoke', index)
        self.assertEqual(f.smoke_required(value, index), (False, []))
        for field in value:
            changed = copy.deepcopy(value)
            changed[field] = {'pack_id': PACKS['alpha'], 'tree_id': 'changed'} if field == 'pack' else 'changed'
            self.assertEqual(f.smoke_required(changed, index), (True, [field]))

    def test_15_per_pack_last_line_null_and_malformed(self):
        index = self.root / 'passes.jsonl'
        alpha = fp()
        self.assertTrue(f.smoke_required(alpha, index)[0])
        f.record_pass(alpha, self.root, index)
        self.assertTrue(f.smoke_required(fp(PACKS['beta']), index)[0])
        changed = copy.deepcopy(alpha)
        changed['os_build'] = 'NEW'
        f.record_pass(changed, self.root, index)
        f.record_pass(fp(PACKS['beta']), self.root, index)
        self.assertEqual(f.smoke_required(changed, index), (False, []))
        self.assertEqual(f.smoke_required(alpha, index), (True, ['os_build']))
        null = copy.deepcopy(changed)
        null['runtime_versions']['python'] = None
        f.record_pass(null, self.root, index)
        self.assertEqual(f.smoke_required(null, index), (True, ['runtime_versions']))
        with index.open('a') as handle:
            handle.write('{torn\n')
        self.assertTrue(f.smoke_required(changed, index)[0])
        self.assertEqual(json.loads(index.read_text().splitlines()[0])['fingerprint_sha256'], f.digest(alpha))

    def test_16_meter_node_and_collection_without_hardware(self):
        text = '''+-o Wrong
          "idVendor" = 24521
          "idProduct" = 100
          "USB Serial Number" = "wrong"
+-o KM003C
          "idVendor" = 0x5FC9
          "idProduct" = 0x0063
          "USB Serial Number" = "SYNTHETIC"
          "bcdDevice" = 256
'''
        self.assertEqual(f.meter_device(text), {'serial': 'SYNTHETIC', 'bcdDevice': '256'})
        self.assertIsNone(f.meter_device(text.replace('0x0063', '0x0064')))
        runner = Runner({'git': lambda argv: completed(argv, b'\n' if 'status' in argv else b'a'*40),
                         '/usr/sbin/sysctl': lambda argv: completed(argv, (BOOT_UUID if argv == clock.BOOT_ARGV else 'TEST').encode()),
                         f.METER_ARGV: lambda argv: completed(argv, text.encode())}, real_python=False)
        value = f.collect(self.root, PACKS['alpha'], {}, {}, ctx=Context(run=runner, clocks=FakeClocks()),
                          read_bytes=lambda path: b'fake binary')
        self.assertFalse(value['code_dirty'])
        self.assertEqual(value['meter_device']['serial'], 'SYNTHETIC')
        self.assertEqual(len(value['powermetrics_version']), 64)
