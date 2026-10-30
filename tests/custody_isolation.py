"""Keep test campaigns out of the operator's real night-custody registry.

``joulewise.measurement_liveness.custody_parent()`` defaults to
``~/night-custody`` when ``JOULEWISE_CUSTODY_PARENT`` is unset. That default is
production behaviour (the collection Mac relies on it), so tests must never
reach it: a campaign run by a test publishes ``active-campaigns`` entries there,
and the liveness census, the quiet guard and run_campaign's stale-lock reclaim
all read them.

Call :func:`isolate_custody_parent` from ``setUp`` (per test) or from
``setUpModule`` (per module) in every test module that can reach a custody
writer or reader. ``tests/test_custody_isolation_guard.py`` holds the list of
such modules and fails if one stops calling this helper.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

CUSTODY_PARENT_ENV = "JOULEWISE_CUSTODY_PARENT"
ADDITIONAL_PARENTS_ENV = "JOULEWISE_ADDITIONAL_CUSTODY_PARENTS"


def isolate_custody_parent(case: unittest.TestCase | None = None) -> Path:
    """Point the custody env vars at a fresh temporary parent until cleanup.

    With a test case the parent lives for that test (``addCleanup``); without
    one it lives for the module (``addModuleCleanup``), so call it from
    ``setUpModule``. The previous environment is restored exactly on cleanup,
    including the variables being unset. Returns the temporary custody parent.
    """
    add_cleanup = case.addCleanup if case is not None else unittest.addModuleCleanup
    temporary = tempfile.TemporaryDirectory(prefix="joulewise-custody-")
    add_cleanup(temporary.cleanup)
    parent = Path(temporary.name).resolve() / "custody-parent"
    env = patch.dict(os.environ, {
        CUSTODY_PARENT_ENV: str(parent),
        ADDITIONAL_PARENTS_ENV: "[]",
    })
    env.start()
    add_cleanup(env.stop)
    return parent
