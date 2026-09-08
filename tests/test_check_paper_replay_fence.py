"""Scratch-only backup discovery regressions."""
from tests import test_paper_excursion_decomposition as shared


class BackupProbeTests(shared.BackupProbeTests):
    script = shared.SCRIPT.with_name("check_paper_replay_fence.py")
