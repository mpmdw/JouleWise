"""Opt-in boundary for tests that read live hardware or host telemetry.

Check at execution time, before opening a reader or starting a monitor.
Synthetic-only runs take precedence over an explicit hardware opt-in.
"""
from __future__ import annotations

from functools import wraps
import os
import unittest


def require_live_hw():
    if os.environ.get("JW_B5_SYNTHETIC_ONLY") == "1":
        raise unittest.SkipTest("JW_B5_SYNTHETIC_ONLY=1 forbids live-hardware tests")
    if os.environ.get("JW_LIVE_HW") != "1":
        raise unittest.SkipTest("live-hardware tests require JW_LIVE_HW=1")


class LiveHardwareTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        require_live_hw()


def live_hw_only(test):
    """Guard one test in a class that otherwise uses fake readers."""
    @wraps(test)
    def guarded(*args, **kwargs):
        require_live_hw()
        return test(*args, **kwargs)
    return guarded
