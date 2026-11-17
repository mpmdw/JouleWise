"""Collect the shared integration contract on main."""

from pathlib import Path
import unittest

from tests.contract.cluster import ClusterScenarios, _offload_sources


class TestClusterMain(ClusterScenarios, unittest.TestCase):
    # A member leaf owns collection of the activated cross-PR scenarios.
    select_main = any(Path(__file__).parent.glob("test_cluster_[0-9]*.py"))


class TestClusterInventory(unittest.TestCase):
    def test_at_most_one_offload_source(self):
        sources = _offload_sources()
        self.assertTrue(not sources or sources == ["joulewise/span_offload.py"], sources)
