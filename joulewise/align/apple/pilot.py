"""First agent-monitoring pilot (v0): roster, offline SHADE factory, cache prefetch.

DRAFT for the lead; nothing here is registered. The pilot is an instrument
check of the Apple align_episode path on the measurement Mac: it makes no
hypothesis claim. docs/align/pilot_protocol_v0.md is the protocol.

Members name ``joulewise.align.apple.pilot:offline_shade_task`` as their task
factory. It never fetches: a measured session must not touch the network, so
the pinned SHADE-Arena cache is prepared at a desk with ``prefetch`` and the
member only verifies it (upstream_cache_missing otherwise, before idle
admission, as runtime_unavailable).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from joulewise.align.apple.workload import EpisodeSpec
from joulewise.align.shade.task import ShadeTask
from joulewise.align.shade.upstream import FILE_LIST_SHA256, UPSTREAM_COMMIT, PinnedUpstream

FACTORY = "joulewise.align.apple.pilot:offline_shade_task"

# Judge-free pairs only: their main and side evaluators are deterministic in
# the pinned source (docs/align/shade_port.md, "Pairs and evaluation
# semantics"), so no second model and no service is needed to score them.
PILOT_V0_PAIRS = ("spam_filter_update", "bank_transfer_2")
PILOT_V0_CONDITIONS = ("benign", "sabotage")
# Greedy MLX decoding makes a repeat of the same spec the same token sequence;
# three repeats per cell give two within-cell differences of identical work.
PILOT_V0_REPEATS = 3
# Operator budgets, not analysis thresholds: they bound the session length.
PILOT_V0_MAX_TURNS = 12
PILOT_V0_MAX_TOKENS = 1536


def offline_shade_task(task_pair: str, *, cache_dir: str | None = None,
                       commit: str = UPSTREAM_COMMIT, file_sha256: str = FILE_LIST_SHA256,
                       give_hint: bool = True) -> ShadeTask:
    """ShadeTask over a verified local cache; never fetches, never calls a judge."""
    upstream = PinnedUpstream(cache_dir, commit=commit, file_sha256=file_sha256, allow_fetch=False)
    return ShadeTask(task_pair, upstream=upstream, judge_endpoint=None, give_hint=give_hint)


def pilot_specs(*, pairs: Sequence[str] = PILOT_V0_PAIRS, repeats: int = PILOT_V0_REPEATS,
                max_turns: int = PILOT_V0_MAX_TURNS, max_tokens: int = PILOT_V0_MAX_TOKENS,
                task_kwargs: dict[str, Any] | None = None) -> list[EpisodeSpec]:
    """Every (pair, condition, repeat) episode; seed names the repeat.

    Upstream has no environment seed and MLX decoding is greedy, so the seed
    only distinguishes repeats; it does not change the work.
    """
    specs = []
    for pair in pairs:
        for repeat in range(1, repeats + 1):
            for condition in PILOT_V0_CONDITIONS:
                specs.append(EpisodeSpec(
                    task_factory=FACTORY, condition=condition, seed=repeat,
                    max_turns=max_turns, max_tokens=max_tokens, temperature=0.0,
                    task_kwargs={"task_pair": pair, **(task_kwargs or {})},
                ))
    return specs


def prefetch(cache_dir: str | None = None) -> dict[str, Any]:
    """Desk step: fetch the pinned source once and verify commit and manifest."""
    upstream = PinnedUpstream(cache_dir, allow_fetch=True)
    root = upstream.prepare(force=True)
    return {"root": None if root is None else str(root), "commit": upstream.commit,
            "file_sha256": upstream.file_sha256, "flags": list(upstream.flags),
            "ok": root is not None}


def verify(cache_dir: str | None = None) -> dict[str, Any]:
    """Precheck step: the offline verification a member performs, without a model."""
    upstream = PinnedUpstream(cache_dir, allow_fetch=False)
    root = upstream.prepare(force=True)
    return {"root": None if root is None else str(root), "flags": list(upstream.flags),
            "ok": root is not None}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prefetch", "verify"))
    parser.add_argument("--cache-dir")
    args = parser.parse_args(argv)
    result = (prefetch if args.command == "prefetch" else verify)(args.cache_dir)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
