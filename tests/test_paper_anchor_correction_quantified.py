"""Scratch-only backup discovery regressions."""
from tests import test_paper_excursion_decomposition as shared


class BackupProbeTests(shared.BackupProbeTests):
    script = shared.SCRIPT.with_name("paper_anchor_correction_quantified.py")

    def locate(self, root, digest):
        return self.module.locate_raw_powermetrics(root, self.member_id, digest)[0]
