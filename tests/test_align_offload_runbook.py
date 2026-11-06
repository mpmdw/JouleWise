"""Operator contract and syntax checks; never execute documented commands."""
import ast
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / 'docs/align/mbp_offload_and_gold_setup.md').read_text()


class RunbookTests(unittest.TestCase):
    def test_current_reclaim_class_and_retention_are_unambiguous(self):
        step8 = TEXT.split('## 8.', 1)[1].split('## 9.', 1)[0]
        self.assertNotIn('--model-class public-weights', step8)
        self.assertIn('--remote "$JW_REMOTE"', step8)
        self.assertIn('No currently approved pilot deletion', step8)
        self.assertIn('"$JW_OP/delete_root.py" delete', step8)
        self.assertIn('80,000,000,000 bytes plus', TEXT)
        self.assertIn('Freed in this authoring session: 0 bytes', TEXT)

    def test_r0_patch_withdrawn_and_r0_is_report_only(self):
        # Lead ruling: R0's disk check is report-only and needs no offloads
        # (v4 ruling 6, origin/lane/2026-11-05-align-v4-wp4-r0).
        self.assertNotIn('r0_disk_gate_patch', TEXT)
        self.assertFalse((ROOT / 'docs/align/r0_disk_gate_patch.md').exists())
        self.assertIn('report-only', TEXT)
        self.assertIn('82cca4295', TEXT)
        self.assertNotIn('2*w1 + 30_000_000_000', TEXT)
        self.assertNotIn('pilot8-r0-inventory', TEXT)

    def test_keep_list_has_night_align_and_inode_rule(self):
        keep = TEXT.split('## 4.', 1)[1].split('## 5.', 1)[0]
        block = keep.split('```text\n', 1)[1].split('```', 1)[0].split()
        self.assertIn('/Users/edr/night-align', block)
        self.assertIn('by inode', keep)
        self.assertIn('NIGHT-ALIGN', keep)

    def test_step2_pins_all_scripts_and_records_absent_crontab(self):
        step2 = TEXT.split('## 2.', 1)[1].split('## 3.', 1)[0]
        for name in ('delete_root.py', 'disk_guard.py', 'align_offload_model_keep.py',
                     'external_volume_census.py'):
            self.assertIn(name, step2)
        self.assertNotIn('\ncrontab -l\n', step2)
        self.assertIn('crontab-absent.txt', step2)
        self.assertIn('no crontab for $(id -un)', step2)
        pause = step2.split('step2-pause.zsh', 1)[1]
        self.assertNotIn('test ! -e /Users/edr/night-custody/magistrate/STOP', pause)
        self.assertIn('already absent', pause)
        self.assertIn('cmp "$JW_OP/our-STOP.txt" "$jw_stop"', pause)

    def test_saturday_run_a_is_copy_only_and_ordered(self):
        sat = TEXT.split('## 15.', 1)[1]
        drivers = re.findall(r'```zsh\n(.*?)```', sat, re.S)
        a1 = next(d for d in drivers if 'step2b-bus-baseline.zsh"' in d)
        a2 = next(d for d in drivers if 'step13-ejected-census.zsh' in d)
        a3 = next(d for d in drivers if 'step13-unplugged-census.zsh"' in d and d is not a2)
        run_a = a1 + a2 + a3
        for forbidden in ('step3', 'step5', 'step7-cloud', 'step7b', 'step8', 'step9-budget',
                          'cloud-roundtrip', 'delete'):
            self.assertNotIn(forbidden, run_a)
        # 9a is NOT guarded (no tty inside the guard); copies are guarded.
        self.assertIn('zsh -f -euo pipefail "$JW_STEPS/step9a.zsh"', a2)
        self.assertNotIn('guarded "$JW_STEPS/step9a.zsh"', a2)
        self.assertIn('sudo -v', a2)
        order = [a2.index(x) for x in ('step9a.zsh', 'step6-tool', 'step6-item', 'step6-ssd',
                                       'step7-existing', 'step13-eject.zsh',
                                       'step13-ejected-census.zsh')]
        self.assertEqual(order, sorted(order))
        for pilot in ('pilot-v7-20261105T015948Z', 'pilot-v8-20261105T102850Z',
                      'pilot-v9-20261105T231016Z'):
            self.assertIn(pilot, a2)
        self.assertLess(a1.index('step2-pause'), a1.index('step2b-bus-baseline'))
        self.assertIn('physically unplug', sat)

    def test_ejected_census_requires_bus_layer_refusal_before_unplug(self):
        step13 = TEXT.split('## 13.', 1)[1].split('## 14.', 1)[0]
        self.assertLess(step13.index('diskutil eject'), step13.index('census-ejected-plugged'))
        self.assertLess(step13.index('census-ejected-plugged'), step13.index('Now physically unplug'))
        self.assertIn("assert r['extra_bus_devices']", step13)
        self.assertIn('census PASSED with the enclosure still plugged in', step13)
        calls = re.findall(r'python3\.13 -I -B "\$JW_OP/external_volume_census\.py"(?:[^\n]*\\\n)*[^\n]*', TEXT)
        self.assertGreaterEqual(len(calls), 6)
        for call in calls:
            if '--record-baseline' not in call:
                self.assertIn('--baseline', call)
        self.assertNotIn('$JW_CANON/scripts/external_volume_census.py', TEXT)

    def test_7a_is_digest_copy_with_evict_and_no_parser(self):
        s7a = TEXT.split('### 7a.', 1)[1].split('### 7b.', 1)[0]
        fence = s7a.split('```zsh\n', 1)[1].split('```', 1)[0]
        self.assertNotIn('jw_uploaded', fence)
        self.assertNotIn('VERIFY_FILE', fence)
        self.assertLess(fence.index('existing-$JW_ROW-original.sha256'), fence.index('cp -p'))
        self.assertLess(fence.index('cp -p'), fence.index('"$JW_ROW_DIR/original.sha256"\n'))
        self.assertLess(fence.index('shasum -a 256 -c "$JW_ROW_DIR/original.sha256"'),
                        fence.index('brctl evict'))
        self.assertIn('jw_wait_dataless "$JW_EXISTING_ARCHIVE" yes', fence)

    def test_9a_refuses_disk_image_via_pinned_volume_check(self):
        s9a = TEXT.split('### 9a.', 1)[1].split('### 9b.', 1)[0]
        self.assertIn('"$JW_OP/delete_root.py" volume-check', s9a)
        self.assertIn('--media "$JW_EXTERNAL_MEDIA"', s9a)
        self.assertIn('Disk Image', s9a)

    def test_termination_and_unpinned_upload_gates_are_explicit(self):
        self.assertIn('tmux plus caffeinate', TEXT)
        self.assertIn('Never close the Terminal', TEXT)
        self.assertIn('SIGKILL', TEXT)
        self.assertIn('unpinned and always refuses', TEXT)
        self.assertIn('fileprovider-evaluate-step5.txt', TEXT)
        self.assertIn('unknown keys/formats', ' '.join(TEXT.lower().split()))

    def test_saturday_targets_copy_order_and_measurement_gate(self):
        self.assertIn('WD_Black SN7100', TEXT)
        self.assertIn('OWC Express 1M2', TEXT)
        for root in ('pilot-v7-20261105T015948Z', 'pilot-v8-20261105T102850Z',
                     'pilot-v9-20261105T231016Z'):
            self.assertIn('/Users/edr/night-align/' + root, TEXT)
        ssd = TEXT.index('## 6. FIRST:')
        cloud = TEXT.index('## 7. THEN:')
        deletion = TEXT.index('## 8. LAST:')
        self.assertLess(ssd, cloud)
        self.assertLess(cloud, deletion)
        self.assertIn('second-copy --item', TEXT[ssd:cloud])
        self.assertIn('cloud-roundtrip --item', TEXT[cloud:deletion])
        self.assertIn('physically unplug', TEXT)
        self.assertIn('external_volume_census.py', TEXT.split('## 13.', 1)[1])

    def test_all_shell_fences_and_python_heredocs_parse_without_execution(self):
        fences = re.findall(r'```zsh\n(.*?)```', TEXT, re.S)
        self.assertGreater(len(fences), 10)
        python_count = 0
        for index, code in enumerate(fences):
            with self.subTest(fence=index):
                result = subprocess.run(['/bin/zsh', '-n'], input=code, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                for body in re.findall(r"<<'PY(?:[A-Z]*)'\n(.*?)\nPY[A-Z]*\n", code, re.S):
                    ast.parse(body)
                    python_count += 1
        self.assertGreater(python_count, 3)


if __name__ == '__main__':
    unittest.main()
