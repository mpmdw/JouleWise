# 2026-07-06: P1-002 Capture Verified + Slice 2H via Review/Counterreview Loop

Same-day continuation of `2026-07-06-autonomous-buildout.md`. The user
captured the privileged powermetrics sample (P1-002) and directed a
heavier multi-agent process: implementation by Codex (gpt-5.5), a
multi-lens adversarial review workflow on my side, and Codex
counterreviewing the findings as a peer.

## P1-002 capture verification

`sudo /usr/bin/powermetrics -i 1000 -n 5 --samplers
cpu_power,gpu_power,ane_power,thermal --format plist -o
tests/fixtures/powermetrics_sample.plist` (user-entered password; first
attempt failed only because `tests/fixtures/` didn't exist). Findings
recorded in the Phase 1 exit checklist instrumentation section:
NUL-separated plist framing (5 docs), rails in `processor` in mW,
`combined_power` = exact rail sum (D-018 manifest validated by the data),
`thermal_pressure` present, and the 1-second-resolution `timestamp` +
precise `elapsed_ns` subtlety.

## Slice 2H (commit `26dca41`)

First Codex implementation: adapter + registry + CI-safe fixture tests,
241 tests green both interpreters. My live check confirmed the one
acceptance criterion testable without sudoers: the mlx+powermetrics
config fails structurally with `permission_denied` naming the exact
D-004 sudoers line (all 3 experiment reps).

**Adversarial review workflow** (22 agents: contract / correctness /
test-adequacy lenses, every finding independently verified with a
refutation attempt): 10 confirmed, 2 refuted. Highlights:

- **Blocker:** `measure_idle` fabricated a 0.0 W `IdleBaseline` when the
  capability probe failed — the idle stage completed with fake data in
  events/metadata/summary, the run burned a full real warmup before
  failing at `start_sampling`, and the D-014 cooldown gate was poisoned
  (300 s busy-spin or instant false "recovered").
- Sample timestamps anchored to the 1 s-resolution plist date were
  systematically up to ~1 s early vs the SystemClock D-026 markers the
  reducer windows against (also spotted independently by me — good
  calibration for the workflow).
- Parser `KeyError`/`ExpatError` escaping the probe's `except ValueError`;
  idle count/timeout math crashing at high `power_hz`; unpinned D-002
  write-before-parse ordering; four dead failure branches; more.

**Codex counterreview:** agreed with all 10 (refuted none), and its F1
design was better than both options I posed — a structured
`AdapterFailure` exception (new, `interfaces.py`) that the controller
maps to the TRUE `FailureReason`, preserving `permission_denied` while
failing before warmup; the cooldown gate catches it and skips. F2 fix:
samples anchor to the injected clock at `start_sampling` + cumulative
`elapsed_ns`; the plist anchor is demoted to `plist_anchor_offset_s`
evidence (D-003 offset-bound pattern). Controller change justified and
accepted: minimal (one except arm + gate catch), contract-improving.

**Final live verification:** suites 251 green (both interpreters);
mlx+powermetrics run now stops at the `idle_baseline` stage,
`failure_reason=permission_denied`, `idle_baseline` absent from summary
AND metadata, warmup never starts (stage events end at
`stage_started idle_baseline`).

## 2H status

Implementation complete and fixture-verified. The real-machine smoke
(idle baseline + measured window from a live privileged run) — 2H's
final acceptance evidence — needs the D-004 sudoers line:
`edr ALL=(root) NOPASSWD: /usr/bin/powermetrics` (e.g. via
`sudo visudo -f /etc/sudoers.d/joulewise-powermetrics`). Once installed,
run `configs/examples/mac_mlx_local.json` → that is also Slice 2I's
one-command flagship (3 reps, real cooldown gate) — first real energy
numbers.

## Queue changes (user-directed re-prioritization)

P1-001 (supervisor scope) and P0-003 (real backup destination) moved to
meta/deferred rows at the user's direction ("ignore for the moment...
lower priority / meta"). P1-002 nearly complete (only the sudoers line
outstanding). New completed rows: 2H implementation.

## Delegation meta-observations (user-requested)

The review→counterreview loop worked notably well; details and the
distilled rules recorded in the global delegation guidance
(`~/.claude/CLAUDE.md`) per the user's request. Headline: Codex accepted
all confirmed findings AND improved on the suggested fix design when
asked for design judgment explicitly — treat it as a design peer, not
just an implementer; parent-side adversarial review + parent live
verification remain the two irreplaceable layers.
