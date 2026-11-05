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
        self.assertIn('--model-class public-weights', step8)
        self.assertNotIn('--remote ', step8)
        self.assertIn('Pilot roots and capture-bearing trees remain until after block-5 release', step8)
        self.assertNotIn('pilot 8 only if', TEXT)
        self.assertNotIn('pilot 8 only if eligible', TEXT)
        self.assertNotIn('R0 still needs at least 80 GB', TEXT)
        self.assertNotIn('free >= 80_000_000_000', TEXT)
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
