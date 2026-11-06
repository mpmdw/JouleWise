#!/usr/bin/env python3
"""Planning-only wall-clock calculator for ALIGN v4 episodes.

The policy numbers deliberately do not live in this module.  ``--budget`` is
an ALIGN source export (JSON), or a directory containing one.  This keeps the
calculator downstream of the v4 admission code and Window 1 plan instead of
creating a second, silently drifting policy table.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
from typing import Any

CONTEXT_RUNGS = (4096, 16384, 40960)  # measurement geometry, not ALIGN policy


def _object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON source {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top level must be an object")
    return value


def load_budget_source(source: Path) -> tuple[dict[str, Any], str]:
    """Load the machine-readable export produced beside the ALIGN v4 code.

    A directory lookup is intentionally exact rather than a recursive guess:
    assembled kits should write ``align-v4-feasibility.json``.  A direct path
    permits immutable exports with another name in tests and audit bundles.
    """
    if source.is_dir():
        candidates = [source / name for name in ("align-v4-feasibility.json", "align_v4_feasibility.py")
                      if (source / name).is_file()]
        if len(candidates) != 1:
            raise ValueError(f"{source}: expected exactly one ALIGN v4 feasibility source")
        path = candidates[0]
    else:
        path = source
    if path.suffix == ".py":
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
            matches = [ast.literal_eval(node.value) for node in tree.body
                       if isinstance(node, (ast.Assign, ast.AnnAssign))
                       and ((isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ALIGN_V4_FEASIBILITY"
                                                                   for t in node.targets))
                            or (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                                and node.target.id == "ALIGN_V4_FEASIBILITY"))]
        except (OSError, SyntaxError, ValueError) as exc:
            raise ValueError(f"cannot parse Python source {path}: {exc}") from exc
        if len(matches) != 1 or not isinstance(matches[0], dict):
            raise ValueError(f"{path}: expected one literal ALIGN_V4_FEASIBILITY mapping")
        data = matches[0]
    else:
        data = _object(path)
    required = {"schema", "limits", "efforts", "window"}
    if set(data) != required or data["schema"] != "align-v4-feasibility/v1":
        raise ValueError(f"{path}: expected exact align-v4-feasibility/v1 export")
    return data, str(path)


def load_performance(paths: list[Path]) -> dict[tuple[str, int], dict[str, float]]:
    """Medians from supervisor reports; the worker's rows live under ``results``."""
    cells: dict[tuple[str, int], dict[str, float]] = {}
    profiles = set()
    for path in paths:
        report = _object(path)
        if report.get("schema") != "qwen4exp-mbp-live/v1" or report.get("command") != "performance":
            raise ValueError(f"{path}: not a qwen4exp performance report")
        results = report.get("results")
        if (report.get("verdict") != "completed" or not isinstance(results, dict)
                or results.get("verdict") != "completed"):
            raise ValueError(f"{path}: performance report is not completed")
        medians = results.get("medians")
        if not isinstance(medians, list) or not medians:
            raise ValueError(f"{path}: performance report has no median rows")
        profiles.add(report.get("profile"))
        if len(profiles) > 1:
            raise ValueError(f"{path}: performance reports mix artifact profiles {sorted(map(str, profiles))}")
        for row in medians:
            try:
                key = (str(row["reasoning_effort"]), int(row["context"]))
                value = {"prefill_tps": float(row["prefill_tps"]),
                         "decode_tps": float(row["decode_tps"])}
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"{path}: malformed median row") from exc
            # Two chunk-size reports are alternatives, not samples to pool.
            # Assignment makes the later CLI argument (normally 2048) win.
            if min(value.values()) <= 0 or not all(math.isfinite(v) for v in value.values()):
                raise ValueError(f"{path}: median rates must be finite and positive")
            cells[key] = value
    return cells


def _positive_int(value: Any, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < (0 if allow_zero else 1):
        raise ValueError(f"{label} must be an integer >= {0 if allow_zero else 1}")
    return value


def _rung(tokens: int) -> int:
    for rung in CONTEXT_RUNGS:
        if tokens <= rung:
            return rung
    raise ValueError(f"prompt growth {tokens} exceeds measured 40,960-token context")


def _cell(rates, effort, rung):
    try:
        return rates[(effort, rung)]
    except KeyError as exc:
        raise ValueError(f"missing measured median for {effort} at context {rung}") from exc


def calculate(policy: dict[str, Any], rates: dict[tuple[str, int], dict[str, float]]) -> dict[str, Any]:
    limits, window = policy["limits"], policy["window"]
    if not isinstance(limits, dict) or not isinstance(window, dict) or not isinstance(policy["efforts"], dict):
        raise ValueError("limits, efforts, and window must be objects")
    episode_limit = _positive_int(limits.get("episode_time_limit_s"), "episode_time_limit_s")
    deadman = _positive_int(limits.get("deadman_limit_s"), "deadman_limit_s")
    window_s = _positive_int(window.get("length_s"), "window.length_s")
    episode_count = _positive_int(window.get("episode_count"), "window.episode_count")
    rows = []
    for effort, budget in policy["efforts"].items():
        if not isinstance(budget, dict) or set(budget) != {"initial_prompt_tokens", "turns"}:
            raise ValueError(f"efforts.{effort}: expected initial_prompt_tokens and turns")
        prompt = _positive_int(budget["initial_prompt_tokens"], f"{effort}.initial_prompt_tokens")
        turns = budget["turns"]
        if not isinstance(turns, list) or not turns:
            raise ValueError(f"efforts.{effort}.turns must be a non-empty list")
        prefill_s = decode_s = 0.0
        for number, turn in enumerate(turns, 1):
            if not isinstance(turn, dict) or set(turn) != {"reasoning_tokens", "answer_tokens"}:
                raise ValueError(f"{effort}.turns[{number}]: malformed token admission budget")
            reasoning = _positive_int(turn["reasoning_tokens"], "reasoning_tokens", allow_zero=True)
            answer = _positive_int(turn["answer_tokens"], "answer_tokens", allow_zero=True)
            decode = reasoning + answer
            # Prefill at the prompt's rung; decode at the rung of the context it
            # reaches (conservative), and never past the measured 40,960.
            prefill_cell = _cell(rates, effort, _rung(prompt))
            decode_cell = _cell(rates, effort, _rung(prompt + decode))
            prefill_s += prompt / prefill_cell["prefill_tps"]
            decode_s += decode / decode_cell["decode_tps"]
            prompt += decode
        wall = prefill_s + decode_s
        share = wall / deadman
        per_window = math.floor(window_s / wall)
        # The planned window must hold its planned episodes, not just one.
        verdict = ("INFEASIBLE" if wall > min(episode_limit, deadman) or per_window < episode_count
                   else ("MARGINAL" if share > .70 else "FEASIBLE"))
        rows.append({"effort": effort, "prefill_seconds": prefill_s, "decode_seconds": decode_s,
                     "episode_wall_seconds": wall, "episodes_per_window": per_window,
                     "planned_episodes": episode_count, "deadman_share": share, "verdict": verdict})
    return {"label": "PLANNING ESTIMATE — NOT ENERGY EVIDENCE", "rows": rows,
            "episode_time_limit_s": episode_limit, "deadman_limit_s": deadman,
            "window_length_s": window_s, "window_episode_count": episode_count}


def render(result: dict[str, Any], source: str) -> str:
    lines = [result["label"], f"ALIGN source: {source}",
             "effort  prefill_s  decode_s  episode_s  episodes/window  deadman_share  verdict"]
    for row in result["rows"]:
        lines.append(f"{row['effort']:<7} {row['prefill_seconds']:>9.1f} {row['decode_seconds']:>9.1f} "
                     f"{row['episode_wall_seconds']:>10.1f} {row['episodes_per_window']:>16} "
                     f"{row['deadman_share']:>13.1%}  {row['verdict']}")
    lines.append(f"Window plan: {result['window_episode_count']} episodes in {result['window_length_s']} s; "
                 f"episode limit {result['episode_time_limit_s']} s; deadman {result['deadman_limit_s']} s.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--performance", nargs="+", required=True, type=Path, metavar="JSON")
    parser.add_argument("--budget", required=True, type=Path, metavar="SOURCE")
    args = parser.parse_args(argv)
    try:
        policy, source = load_budget_source(args.budget)
        print(render(calculate(policy, load_performance(args.performance)), source))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
