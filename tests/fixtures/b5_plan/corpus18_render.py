"""Read-only production chain rendering with scratch bindings; no tools run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from joulewise.b5 import chain
from tests.fixtures.b5_plan.fake_window import PACKS

ROOT = Path(__file__).resolve().parents[3]


def render_pack(pack: str, scratch: Path) -> tuple[bytes, dict, list[str]]:
    pack_root = ROOT / 'configs/campaigns' / PACKS[pack]
    tree_raw = (pack_root / 'plan_tree.json').read_bytes()
    tree = json.loads(tree_raw)
    stages = chain.stage_plan(tree)
    bindings = {name: str(scratch / name) for name in (
        'ledger_path', 'claim_runs_root', 'bound_runs_root', 'operator_log_root',
        'pre_calibration_dir', 'post_calibration_dir', 'claim_backup_destination',
        'bound_backup_destination', 'identity_epoch_json', 't1_bindings_json')}
    bindings.update(repo_root=str(ROOT), bracket_session_id=f'corpus18-{pack}',
                    pre_attempt_id=f'corpus18-{pack}-pre', post_attempt_id=f'corpus18-{pack}-post')
    raw = chain.render_chain(tree=tree, tree_sha256=hashlib.sha256(tree_raw).hexdigest(),
                             stages=stages, bindings=bindings, measurement_root=ROOT,
                             pack_root=pack_root, plan_id=f'corpus18-{pack}-dry',
                             runbook_text=(ROOT / chain.RUNBOOK_RELATIVE).read_text())
    corpus = next(stage for stage in stages if stage.stage_id == f'{pack}-bound-collection')
    return raw, corpus.summary(), chain.stage_argv(corpus, bindings, tree, ROOT)
