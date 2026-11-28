"""Failing-first R11 review witnesses; synthetic records and temporary Git only.

These tests deliberately fail on c3796bf49. Product fixes belong to the lead.
No hardware, model, measurement loader, network or external study path is used.
"""
from tests.git_fixture import init_git_fixture
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from joulewise.align.apple import v4_estimands as estimands
from joulewise.align.apple import v4_registration as registration


class RegistrationCandidateWitness(unittest.TestCase):
    def test_receipt_refuses_changed_live_cache_implementation(self):
        """A clean later commit can change executed cache code behind an old gate."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in registration.ARTIFACTS:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic registered artifact\n')
            cache = root / 'joulewise/align/apple/prompt_cache.py'
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text('def common_prefix_length(left, right):\n    return 0\n')
            gate_paths = {stage: f'docs/align/v4/review-witness-{stage}.md'
                          for stage in ('A', 'B')}
            for relative in gate_paths.values():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic admitted gate\n')

            def git(*arguments):
                return subprocess.run(
                    ['git', '-c', 'core.hooksPath=/dev/null', *arguments],
                    cwd=root, check=True, capture_output=True, text=True).stdout.strip()

            def commit(message):
                git('add', '.')
                git('-c', 'user.name=Synthetic', '-c', 'user.email=synthetic@example.invalid',
                    'commit', '-qm', message)
                return git('rev-parse', 'HEAD')

            def digest(relative):
                return hashlib.sha256((root / relative).read_bytes()).hexdigest()

            init_git_fixture(root, '-q')
            reviewed = commit('Synthetic reviewed candidate')
            receipt = {
                'schema': registration.RECEIPT_SCHEMA, 'status': 'registered',
                'commit': reviewed, 'lead_signature': 'lead: synthetic-review 2026-11-08',
                'rulings': {str(number): 'installed' for number in registration.RULINGS},
                'artifacts': {relative: digest(relative) for relative in registration.ARTIFACTS},
                'gates': {stage: {'verdict': 'ADMIT', 'path': relative,
                                  'sha256': digest(relative)}
                          for stage, relative in gate_paths.items()},
            }
            registration.validate_receipt(receipt, root)
            cache.write_text('def common_prefix_length(left, right):\n    return len(left)\n')
            self.assertNotEqual(commit('Synthetic unreviewed cache behavior'), reviewed)
            self.assertEqual(git('status', '--porcelain'), '')
            with self.assertRaises(ValueError, msg='executed runtime drift needs a new candidate gate'):
                registration.validate_receipt(receipt, root)


class ContrastIdentityWitness(unittest.TestCase):
    def test_zero_turn_x_retains_nonveto_failed_identity_receipt(self):
        """An X-G G0 timeout supplies zero native turns, not a D admission veto."""
        fixtures = {
            arm: {'turns': [{'turn': turn, 'prompt_token_ids': [turn + 1],
                             'output_token_ids': [turn + 2]} for turn in range(3)]}
            for arm in ('X', 'Y')
        }
        rendered = {arm: [turn['prompt_token_ids'] for turn in fixture['turns']]
                    for arm, fixture in fixtures.items()}
        receipt = registration.wp19_identity(
            fixtures, rendered, [], live_source_sha256=hashlib.sha256(b'').hexdigest())
        self.assertEqual(receipt['verdict'], 'fail')
        self.assertEqual(receipt['contrast_predeclared'], 'INCONCLUSIVE: identity broken')
        self.assertFalse(receipt['live_x_complete'])
        self.assertEqual(registration.validate_wp19(receipt), receipt)


class ExactDoseWitness(unittest.TestCase):
    def test_h_star_does_not_invent_an_integer_dose(self):
        with self.assertRaises(ValueError, msg='128.5 hidden tokens cannot become a 128-token crossing'):
            estimands.subturn_h_star([(128.5, 2.0)], 1.0)

    def test_h_star_missing_lower_grid_point_leaves_first_crossing_undefined(self):
        # 128 is below threshold and 384 is above. Without 256, the first
        # registered-grid crossing could be either 256 or 384.
        result = estimands.subturn_h_star([(128, 0.0), (384, 2.0)], 1.0)
        self.assertIsNone(result['h_star'])


if __name__ == '__main__':
    unittest.main()
