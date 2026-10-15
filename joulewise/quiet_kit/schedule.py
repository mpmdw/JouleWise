"""One segment plan shared by collection, estimates and the read-only plan."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestPlan:
    test_id: str
    segments: tuple[dict, ...]
    model_runs: tuple[str, ...] = ()
    captures: int = 0
    meter: bool = False
    planned_bytes: int = 0
    ruling_required: str | None = None

    @property
    def estimate_s(self) -> float:
        if self.ruling_required:
            return 0.
        return (sum(s.get('duration_s', 0) for s in self.segments) +
                sum(180 if w == 'B' else 150 for w in self.model_runs) +
                self.captures * 264 + 300)

    @property
    def basis(self) -> str:
        if self.ruling_required:
            return 'duration pending lead ruling: ' + self.ruling_required
        seconds = sum(s.get('duration_s', 0) for s in self.segments)
        return (f'{seconds:g} s segments + {len(self.model_runs)} model runs '
                '(150 s R/A; 180 s B, including ordinary baseline) + '
                f'{self.captures} captures x 264 s + 300 s nominal preflight')


def idle(seconds, **fields):
    return {'kind': 'idle', 'duration_s': seconds, **fields}


def load(kind, duty, seconds, **fields):
    return {'kind': kind, 'duty': duty, 'duration_s': seconds, **fields}


def schedule() -> tuple[TestPlan, ...]:
    m4 = [idle(60)]
    for priority in ('background', 'interactive'):
        for duty in (.05, .20, 1.0):
            m4 += [load('cpu', duty, 60, priority=priority), idle(60)]
    for repeat in range(2):
        for length in (.62, 2.0):
            for placement in (0., 2.5, 5., 7.5, 9.4):
                # Late bursts cross a tick. Two accounting intervals preserve
                # the second interval, followed by a whole quiet interval.
                intervals = 2 if placement + length > 10 else 1
                m4 += [dict(kind='burst', duty=1., priority='interactive',
                            duration_s=10 * intervals, burst_s=length,
                            placement_s=placement, repeat=repeat), idle(10)]
    m5 = [s for repeat in range(2) for s in (
        idle(75, repeat=repeat), load('cpu', 1., 75, repeat=repeat),
        idle(75, repeat=repeat), load('gpu', .05, 75, repeat=repeat),
        idle(75, repeat=repeat), load('gpu', .20, 75, repeat=repeat), idle(75, repeat=repeat))]
    # 10 quiet, 4 busy-core, 4 utility, interleaved rather than blocked.
    conditions = ('quiet', 'quiet', 'load', 'quiet', 'utility', 'quiet',
                  'load', 'quiet', 'utility', 'quiet', 'load', 'quiet',
                  'utility', 'quiet', 'load', 'quiet', 'utility', 'quiet')
    m1 = tuple({'kind': 'capture', 'condition': c} for c in conditions)
    m2 = tuple(s for q in range(5) for arm in ('N', 'L', 'L', 'N')
               for s in ([{'kind': 'long_wait', 'duration_s': 1200, 'quad': q, 'arm': arm}]
                         if arm == 'L' else []) +
               [{'kind': 'model', 'workload': 'R', 'quad': q, 'arm': arm}])
    m2b = tuple({'kind': 'model', 'workload': 'R', 'quad': q, 'arm': arm,
                 **({'sampling_idle_seconds': 50.0} if arm == 'S' else {})}
                for q in range(5) for arm in ('N', 'S', 'S', 'N'))
    m10 = tuple(s for repeat in range(2) for s in (
        idle(60, repeat=repeat), load('cpu', 1., 120, repeat=repeat),
        idle(60, repeat=repeat), load('gpu', 1., 120, repeat=repeat),
        idle(60, repeat=repeat), load('mixed', 1., 120, repeat=repeat),
        idle(60, repeat=repeat), load('mixed', 1., 120, repeat=repeat),
        idle(60, repeat=repeat), load('gpu', 1., 120, repeat=repeat),
        idle(60, repeat=repeat), load('cpu', 1., 120, repeat=repeat), idle(60, repeat=repeat)))
    m14 = tuple(s for r in range(2) for s in (
        idle(75), load('gpu', .05, 75), idle(75), load('gpu', .20, 75), idle(75),
        load('cpu', 1., 75), idle(75), load('cpu', .20, 75), idle(75)))
    block = tuple({'kind': 'model', 'workload': w, 'block': b}
                  for b in ('start', 'end') for w in ('R', 'A', 'B', 'B', 'A', 'R'))
    m15 = block[:6] + ({'kind': 'soak', 'duration_s': 5400, 'workloads': ['A', 'B']},) + block[6:]
    gib = 1024 ** 3
    return (
        TestPlan('m4-contention-watts', tuple(m4), planned_bytes=gib),
        TestPlan('m5-gpu-rail', tuple(m5), planned_bytes=gib),
        TestPlan('m1-capture-stop-line', m1, captures=18, planned_bytes=2*gib),
        TestPlan('m2-long-wait', m2, model_runs=('R',)*20, planned_bytes=8*gib),
        TestPlan('m2b-short-baseline', m2b, model_runs=('R',)*20, planned_bytes=8*gib),
        TestPlan('m3-clock-rate', (), planned_bytes=gib),
        TestPlan('m9-time-server', ({'kind': 'sntp', 'duration_s': 600, 'queries': 10},), planned_bytes=gib),
        TestPlan('m14-meter-idle-power', m14, meter=True, planned_bytes=gib),
        TestPlan('m13-meter-edges', tuple({'kind': 'capture', 'condition': 'quiet'} for _ in range(3)),
                 captures=3, meter=True, planned_bytes=gib),
        TestPlan('m10-rails-vs-wall', m10, meter=True, planned_bytes=gib),
        TestPlan('m15-drift-transfer', m15, model_runs=tuple('RABBAR'*2), planned_bytes=16*gib),
    )


PLANS = schedule()
BY_ID = {p.test_id: p for p in PLANS}
TOTAL_SECONDS = sum(p.estimate_s for p in PLANS)
