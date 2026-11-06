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
        self.assertIn('80,000,000,000 bytes plus journal', TEXT)
        self.assertIn('two copies + 30 GB', TEXT)
        self.assertIn('r0_disk_gate_patch.md', TEXT)
        self.assertIn('Freed in this authoring session: 0 bytes', TEXT)

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
