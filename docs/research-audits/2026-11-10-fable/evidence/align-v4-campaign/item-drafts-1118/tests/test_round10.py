"""Astra audit regressions against the rendered draft entry points."""
import datetime as dt
from pathlib import Path
import re
import os
import subprocess
import sys
import tempfile
import unittest
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parents[1]
STANDING = (HERE / 'STANDING-F0-r2.md').read_text()
TZ = ZoneInfo('America/Los_Angeles')


def epoch(value):
    return int(dt.datetime.fromisoformat(value).replace(tzinfo=TZ).timestamp())


class Round10(unittest.TestCase):
    def test_checklist_unset(self):
        for item in HERE.glob('ITEM-qual*.md'):
            with self.subTest(item=item.name):
                start = re.findall(r'```sh\n(.*?)```', item.read_text(), re.S)[0]
                self.assertLess(start.index('cadence_queue.py checklist'), start.index('all_gates || exit 1'))
                self.assertLess(start.index('CHECKLIST_OK=yes'), start.index('all_gates || exit 1'))

    def test_partial_block_recovery(self):
        status = (HERE / 'STATUS.md').read_text()
        for item in HERE.glob('ITEM-qual*.md'):
            with self.subTest(item=item.name):
                guide = item.read_text()
                self.assertIn('Untouched block', guide)
                self.assertIn('Partially run block', guide)
                self.assertIn('NEEDS_RULING was resolved in RL-175 C.3', guide)
                self.assertIn('lead can issue s02 by hand', guide)
        self.assertIn('NEEDS_RULING — partially run qualification block', status)

    def test_pair_bound(self):
        program = re.search(r'F0_NOW=.*?<<\'PY\'\n(.*?)\nPY', STANDING, re.S)[1]
        now = epoch('2026-11-22T19:00:00')
        midnight = epoch('2026-11-23T00:00:00')
        program = program.replace('now = time.time();', f'now = {now};')
        with tempfile.TemporaryDirectory(prefix='f0-round10-') as tmp:
            ledger = Path(tmp) / 'synthetic-ledger.tsv'
            ledger.write_text('# synthetic\n')
            first = f'{midnight-1}:{midnight}:{midnight}'
            for label, limit, allowed in (
                ('19:00 F0 strands second span', f'{first}/{first}/12262:300', False),
                ('item expiry at handoff', f'{midnight-1}:{now+13380}:{midnight}', False),
                ('queue expiry at handoff', f'{midnight-1}:{midnight}:{now+13380}', False),
                ('one whole second to spare', f'{midnight-1}:{now+13381}:{midnight}', True),
                ('pair fits exactly', f'{first}/{first}/{midnight-1-now-13380-300}:300', True),
            ):
                with self.subTest(case=label):
                    if 'COUNTED_LATEST' in STANDING:
                        # Replay the same staged spans using item 346's old
                        # window-end-only encoding.
                        limit = ' '.join(row.split(':')[0] for row in limit.split('/')[:2])
                    result = subprocess.run(
                        [sys.executable, '-I', '-B', '-', str(ledger), limit, 'none'],
                        input=program, text=True, capture_output=True,
                    )
                    self.assertEqual(result.returncode == 0, allowed, result.stderr)
                    if not allowed:
                        self.assertIn('rule 7', result.stderr)

    def test_child_t0_arguments(self):
        for item in HERE.glob('ITEM-qual*.md'):
            with self.subTest(item=item.name):
                run = re.findall(r'```sh\n(.*?)```', item.read_text(), re.S)[1]
                self.assertIn('--authorized-t0-date "$T0_DATE"', run)
                self.assertIn('--t0-before "$ARM_BEFORE_EPOCH"', run)

    def test_child_uses_same_stamp_before_work(self):
        sys.path.insert(0, str(HERE / 'tools'))
        from pinned import pinned
        with pinned() as source, tempfile.TemporaryDirectory(prefix='qual-child-t0-') as scratch:
            for n in range(1, 4):
                kit = HERE / 'kits' / f'cl-qual-{n:02d}.v1.1.json'
                with self.subTest(kit=kit.name):
                    result = subprocess.run(
                        [sys.executable, '-B', str(HERE / 'tests/check_child_t0.py'), str(source),
                         str(kit), str(Path(scratch) / kit.stem)],
                        text=True, capture_output=True, env={**os.environ, 'JW_B5_SYNTHETIC_ONLY': '1'},
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stdout.splitlines(), [
                        'PASS pinned child last authorized fractional second',
                        'PASS pinned child midnight during handoff',
                        'PASS pinned child different date before numeric cutoff',
                        'PASS pinned child item expires during handoff',
                    ])

    def test_maintenance_predicate(self):
        campaign = HERE.parent
        pattern = r"--predicate '(process IN \{[^']+\})'"
        expected = re.search(pattern, (HERE / 'ITEM-qual01-s01.md').read_text())[1]
        f2 = list((campaign / 'item-drafts-f2').glob('ITEM-*.md'))
        for kit in ('f2-inst-02', 'f2-inst-03'):
            f2.extend((campaign / 'item-drafts-f2-0203' / kit).glob('ITEM-*.md'))
        self.assertEqual(len(f2), 12)
        for path in [HERE / 'STANDING-F0-r2.md', *f2]:
            with self.subTest(item=path):
                self.assertEqual(re.findall(pattern, path.read_text()), [expected])

    def test_s01_limit(self):
        for item in HERE.glob('ITEM-qual*-s01.md'):
            with self.subTest(item=item.name):
                doc = item.read_text()
                self.assertRegex(doc, r'LIMIT 2026-11-\d\d 16:32:00 PST')
                start = re.findall(r'```sh\n(.*?)```', doc, re.S)[0]
                end = int(re.search(r'WINDOW_END=(\d+)', start)[1])
                self.assertEqual(dt.datetime.fromtimestamp(end, TZ).strftime('%H:%M:%S'), '16:32:00')

    def test_r0_missing_is_fatal(self):
        start = re.findall(r'```sh\n(.*?)```', STANDING, re.S)[0]
        mac_check = re.search(r'^R0=.*?\nPY\n', start, re.M | re.S)[0]
        for shell in ('bash', 'zsh'):
            with tempfile.TemporaryDirectory(prefix='f0-round10-') as tmp, self.subTest(shell=shell):
                missing = Path(tmp) / 'standing-f0' / 'r0-restore-ade002e9' / 'r0.json'
                # Replace the path even on old head so it can only open a synthetic path.
                safe = re.sub(r'^R0=.*$', f'R0="{missing}"', mac_check, count=1, flags=re.M)
                result = subprocess.run(
                    [shell], input=f'PY="{sys.executable}"\nREPO="{tmp}"\n{safe}echo REACHED_LAUNCH\n',
                    text=True, capture_output=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('REACHED_LAUNCH', result.stdout)
                missing.parent.mkdir(parents=True)
                missing.write_text('{}')
                bad = subprocess.run(
                    [shell], input=f'PY="{sys.executable}"\nREPO="{tmp}"\n{safe}echo REACHED_LAUNCH\n',
                    text=True, capture_output=True,
                )
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn('sha256', bad.stderr)
                self.assertNotIn('REACHED_LAUNCH', bad.stdout)
        self.assertIn('standing-f0/r0-restore-ade002e9/r0.json', mac_check)

    def test_renewal_ahead_and_ladder(self):
        gate = re.search(r'renewal_gate\(\) \{.*?\n\}', STANDING, re.S)[0]
        start = epoch('2026-11-22T11:51:24')
        issued = start - 3600
        for shell in ('bash', 'zsh'):
            for now, allowed in ((start-1, False), (start, True), (issued+604800, False)):
                with self.subTest(shell=shell, now=now):
                    script = (f'RENEWAL_START_EPOCH={start}\nEXPIRY_EPOCH={start+604800}\n'
                              f'RENEWAL_ISSUED_EPOCH={issued}\ndate() {{ echo {now}; }}\n'
                              f'{gate}\nrenewal_gate\n')
                    result = subprocess.run([shell], input=script, text=True, capture_output=True)
                    self.assertEqual(result.returncode == 0, allowed, result.stdout)
        self.assertIn('whose priority gate fails', STANDING)
        self.assertNotIn('RESTART_PENDING', STANDING)


if __name__ == '__main__':
    unittest.main()
