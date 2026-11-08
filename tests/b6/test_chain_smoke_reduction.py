import copy
import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path

from joulewise.b5 import chain
from joulewise.b6 import smoke
from tests.b6.support import DeskCase, ROOT, PACKS, tree


class ChainSmokeReductionTests(DeskCase):
    def test_23_real_pack_render_bytes_equal_original_and_reduced_no_corpus(self):
        # Load the original renderer from HEAD without changing the worktree.
        source = subprocess.run(['git', '-C', str(ROOT), 'show', 'HEAD:joulewise/b5/chain.py'],
                                check=True, capture_output=True, text=True).stdout
        original = types.ModuleType('b6_original_chain')
        sys.modules[original.__name__] = original
        self.addCleanup(sys.modules.pop, original.__name__)
        exec(compile(source, 'original_chain.py', 'exec'), original.__dict__)
        bindings = {name: str(self.root / name) for name in (
            'ledger_path', 'claim_runs_root', 'bound_runs_root', 'operator_log_root',
            'pre_calibration_dir', 'post_calibration_dir', 'claim_backup_destination',
            'bound_backup_destination', 'identity_epoch_json', 't1_bindings_json')}
        bindings.update(repo_root=str(ROOT), bracket_session_id='synthetic', pre_attempt_id='synthetic-pre',
                        post_attempt_id='synthetic-post')
        keep_map = json.loads(smoke.KEEP_PATH.read_text())
        for pack in PACKS:
            t = tree(pack)
            args = dict(tree=t, tree_sha256=hashlib.sha256(json.dumps(t).encode()).hexdigest(),
                        bindings=bindings, measurement_root=ROOT, pack_root=ROOT / 'configs/campaigns' / PACKS[pack],
                        plan_id='synthetic', runbook_text=(ROOT / chain.RUNBOOK_RELATIVE).read_text())
            old = original.render_chain(stages=original.stage_plan(t), **args)
            current = chain.render_chain(stages=chain.stage_plan(t), **args)
            self.assertEqual(current, old, pack)
            reduced = smoke.reduce_tree(t, keep_map[PACKS[pack]])
            args['tree'] = reduced
            raw = chain.render_chain(stages=chain.stage_plan(reduced), **args).decode()
            self.assertFalse(any(' bound_derivation ' in line for line in raw.splitlines()
                                 if not line.startswith('#')))
            self.assertNotIn('neg8_corpus_retry decision=', raw)
            self.assertNotIn('Row 13: one retry', raw)
            self.assertNotIn(f'{pack}-bound-collection', raw)
