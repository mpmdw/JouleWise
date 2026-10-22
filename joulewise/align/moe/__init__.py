"""MoE routing capture and Stage A separation analysis; optional models are lazy."""

from joulewise.align.records import RouterLog
from joulewise.align.moe.stats import (
    episode_stats, grouped_permutation_test, load_imbalance, mean_reuse_distance,
    reuse_fraction, routing_flags, usage_entropy,
)

__all__ = ["RouterLog", "episode_stats", "grouped_permutation_test", "load_imbalance",
           "mean_reuse_distance", "reuse_fraction", "routing_flags", "usage_entropy"]
