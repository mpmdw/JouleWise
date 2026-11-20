"""RL-127 term 6 stage budgets (seconds) and the alarm factor.

A stage past ALARM_FACTOR x its budget raises an alarm and is profiled before
it is retried. "Noticed within" budgets (a refused or stranded session, an idle
MBP) are thresholds on detection itself, so their detectors fire at the budget,
not at 1.5x it. Code and path names say "night"; the rulings call an armed MBP
span a "session".
"""
from __future__ import annotations

ALARM_FACTOR = 1.5

BUDGETS_S = {
    "pr-ci": 30 * 60,              # PR CI run, any tree
    "test-unit": 10 * 60,          # one test unit (shard timeout 60 min)
    "test-shard": 60 * 60,         # shard timeout
    "quick": 5 * 60,               # `quick` tier, local or CI
    "state-only-ci": 5 * 60,       # state-only or docs-only commit, CI minutes
    "block-analysis": 60 * 60,     # real custody: copy, verify, inputs, reader
    "smoke": 75 * 60,              # smoke or Part A
    "rehearsal": 6000,             # RL-132: term 1 for Block 6 is 4 x 25 min = 100 min (floor 30 min, ceiling 4 h)
    "session-gap": 2 * 60 * 60,    # session close to next launch, no code change
    "session-gap-code": 4 * 60 * 60,  # session close to next launch, code or config change
    "notice": 30 * 60,             # refused or stranded session noticed
    "mbp-idle": 30 * 60,           # MBP unarmed with no job queued
    "seat-no-output": 30 * 60,     # existing seat rule
}

# Rehearsal bounds from RL-127 term 1, for callers that know the analysis time.
REHEARSAL_RATIO = 4
REHEARSAL_FLOOR_S = 30 * 60
REHEARSAL_CEILING_S = 4 * 60 * 60
DRY_RUN_FACTOR = 2


def rehearsal_budget_s(analysis_s: float) -> float:
    """Term 1: 4 x the analysis it rehearses, floor 30 min, ceiling 4 h."""
    return float(min(REHEARSAL_CEILING_S, max(REHEARSAL_FLOOR_S, REHEARSAL_RATIO * float(analysis_s))))


def dry_run_budget_s(predicted_s: float) -> float:
    """A dry-run stop is budgeted at 2 x its predicted wall."""
    return float(DRY_RUN_FACTOR * float(predicted_s))


def budget_for(stage: str, budget_s: float | None = None) -> float | None:
    """An explicit budget wins; otherwise the stage's RL-127 default; otherwise None."""
    if budget_s is not None:
        return float(budget_s)
    value = BUDGETS_S.get(stage)
    return None if value is None else float(value)


def alarm_after_s(budget_s: float | None) -> float | None:
    return None if budget_s is None else ALARM_FACTOR * float(budget_s)
