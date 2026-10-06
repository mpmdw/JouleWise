"""Flags written by protected-core code on the HAZARD_PACK path (gate-prune core lanes).

One mechanism: ``joulewise.flags.schema.make_flag`` plus ``joulewise.flags.sink.FlagSink``,
appending to ``<custody_root>/flags/<writer>.jsonl``.  The harvest folds every ``*.jsonl`` there
(``joulewise.b5.harvest._Harvest.arm_and_desk_records``).  A flag that cannot be written is printed
whole to stderr behind ``UNWRITTEN_MARKER``; stage stderr lands in ``<custody>/operator-logs/``, and
the harvest recovers those lines (DESIGN.md N8), so a failed write never silently drops an effect.

Dispatch: :func:`hazard_flag_context` returns a context only when the runs root carries the HAZARD
locator (``window_lineage.is_hazard_runs_root``), the same schema dispatch ``arm_readiness`` uses.
``None`` is the legacy path, whose behavior must not change.

Nothing here raises to its caller: a flag is a record, and a record never stops collection.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from joulewise.flags.schema import make_flag, make_scope, make_source, render_line

FLAGS_DIRNAME = "flags"
# joulewise.b5.plan.PLAN_BASENAME, read and never imported (keeps this module light).
WINDOW_PLAN_BASENAME = "night_plan.json"
WRITERS = ("core-controller", "core-run_campaign", "core-fiducial", "core-reservation")
UNWRITTEN_MARKER = "JOULEWISE_UNWRITTEN_FLAG "
# A code missing from the table below is still written, under this family and class; the catalog
# leaves it UNCLASSIFIED, which blocks release until a person looks.
UNKNOWN_CODE_CLASS = ("RECORDS", "REPRESENTATION")

# code -> (family, klass).  Effects live only in the sealed catalog (DESIGN.md section 5).
CORE_FLAG_CODES: Mapping[str, tuple[str, str]] = {
    "calibration.capture_battery_pair_unverified": ("CALIBRATION", "PHYSICS"),
    "records.pin_ledger": ("RECORDS", "REPRESENTATION"),
    "calibration.power_policy_unverified": ("CALIBRATION", "REPRESENTATION"),
    "instrument.binary_identity_unmeasured": ("INSTRUMENT", "NUMBER"),
    "env.member_quiet_state_violated": ("MEMBER_VALIDITY", "PHYSICS"),
    "env.member_guard_flagged": ("DIAGNOSTIC", "REPRESENTATION"),
    "member.idle_admission_telemetry_missing": ("MEMBER_VALIDITY", "PHYSICS"),
    "teardown.survivors": ("DIAGNOSTIC", "PHYSICS"),
    "cooldown.result_unknown": ("DIAGNOSTIC", "PHYSICS"),
    "env.stage_preflight_not_admitted": ("DIAGNOSTIC", "REPRESENTATION"),
    "campaign.runner_record_flagged": ("RECORDS", "REPRESENTATION"),
    "calibration.writer_record_flagged": ("CALIBRATION", "REPRESENTATION"),
    "code.executed_differs_from_sealed": ("CODE_IDENTITY", "NUMBER"),
}


@dataclasses.dataclass(frozen=True)
class HazardFlagContext:
    writer: str
    custody_root: Path | None
    plan_id: str | None
    attempt: str | int | None
    scope_resolved: bool
    stage: str = "window"

    @property
    def path(self) -> Path | None:
        if self.custody_root is None:
            return None
        return self.custody_root / FLAGS_DIRNAME / f"{self.writer}.jsonl"


def hazard_flag_context(
    runs_root: Path | str | None, *, writer: str, stage: str = "window"
) -> HazardFlagContext | None:
    """The HAZARD predicate plus where its flags go; ``None`` on the legacy path.  Never raises."""

    if runs_root is None:
        return None
    try:
        from joulewise import window_lineage

        if not window_lineage.is_hazard_runs_root(runs_root):
            return None
        locator = Path(runs_root) / window_lineage.LOCATOR_BASENAME
    except Exception:  # noqa: BLE001 - an unreadable root is "not hazard"
        return None
    custody: Path | None = None
    try:
        recorded = json.loads(locator.read_bytes())["launch_lineage"]["window_context"]["custody_root"]
        if isinstance(recorded, str) and Path(recorded).is_absolute():
            custody = Path(recorded)
    except Exception:  # noqa: BLE001 - flags then go to stderr behind UNWRITTEN_MARKER
        custody = None
    plan_id: str | None = None
    attempt: str | int | None = None
    resolved = False
    if custody is not None:
        try:
            plan = json.loads((custody / WINDOW_PLAN_BASENAME).read_bytes())
            window = plan.get("hazard_window")
            value = window.get("attempt") if isinstance(window, Mapping) else None
            if isinstance(plan.get("plan_id"), str) and isinstance(value, (str, int)) \
                    and not isinstance(value, bool):
                plan_id, attempt, resolved = plan["plan_id"], value, True
        except Exception:  # noqa: BLE001 - null bindings; the flag file is local to this custody
            pass
    return HazardFlagContext(writer=writer, custody_root=custody, plan_id=plan_id,
                             attempt=attempt, scope_resolved=resolved, stage=stage)


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value, allow_nan=False)
        return value
    except (TypeError, ValueError):
        return {"unserializable": repr(value)[:300]}


def emit(
    context: HazardFlagContext | None,
    code: str,
    *,
    level: str,
    run_id: str | None = None,
    observed: Any = None,
    expected: Any = None,
    detail: str = "",
    legacy_site: str | None = None,
    legacy_code: str | None = None,
    interval: Mapping[str, Any] | None = None,
) -> bool:
    """Record one flag; True once it is in the flag file.  Never raises, never drops the code."""

    if context is None:
        return False
    flag = None
    try:
        family, klass = CORE_FLAG_CODES.get(code, UNKNOWN_CODE_CLASS)
        observed = _json_safe(observed)
        if not context.scope_resolved:
            observed = {"value": observed, "scope_unresolved": True}
        if level == "member" and not run_id:
            # An unplaceable member fact is applied to every member (exclusions.compute): conservative.
            level, observed = "window", {"value": observed, "run_id_missing": True}
        flag = make_flag(
            code=code, family=family, klass=klass,
            scope=make_scope(level, plan_id=context.plan_id, attempt=context.attempt,
                             run_id=run_id, bundle_id=run_id),
            source=make_source(context.stage, f"core.{context.writer}",
                               legacy_site=legacy_site, legacy_code=legacy_code),
            observed=observed, expected=_json_safe(expected), detail=detail, interval=interval,
        )
        path = context.path
        if path is None:
            raise OSError("custody root unresolved from the HAZARD locator")
        from joulewise.flags.sink import FlagSink

        FlagSink(path).append(flag)
        return True
    except Exception as exc:  # noqa: BLE001 - a flag is a record; it never stops collection
        try:
            line = render_line(flag).decode("utf-8").rstrip("\n") if flag is not None else json.dumps(
                {"code": code, "level": level, "run_id": run_id, "unbuilt": f"{type(exc).__name__}: {exc}"[:300]},
                sort_keys=True)
            print(UNWRITTEN_MARKER + line, file=sys.stderr, flush=True)
        except Exception:  # noqa: BLE001
            pass
        return False
