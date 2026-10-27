"""Conservative capabilities of the present harvest and analysis entry points."""
from joulewise.b6.lanes import HarvestCapabilities


class HarvestLane:
    def capabilities(self):
        # session.accept_archive explicitly computes pack_scoped=False.
        # export_runs applies stored hidden factors; no modular block-id
        # stratum evaluator is connected to this fixed-pack harvest path.
        return HarvestCapabilities(pack_scoped_flags=False, hidden_offsets=True, block_id_strata=False)


class AnalysisLane:
    def precision_reached(self, pack_id, reg, counting_ids):
        # No registered-estimator precision entry point exists in stage 1.
        return None
