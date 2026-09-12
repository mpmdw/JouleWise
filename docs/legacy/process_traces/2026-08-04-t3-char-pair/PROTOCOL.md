# T3-CHAR-PAIR-01 — characterization protocol (defines "standard idle-capture conditions")

The kernel row's acceptance phrase "standard idle-capture conditions"
had no implementation behind it (found by a read-only scout,
2026-08-04). This document supplies it. NON-CLAIM throughout.

## Question

Does T3 Code, resident but dormant (app + server + helpers +
cloudflared), measurably raise the machine's idle power floor? The
answer decides whether app-adjacent windows are ever admissible, which
is the first physical blocker on the t3-drive chain.

## Mechanism (governed, ceremony-free by design)

`joulewise run <config> --runs-dir <fresh root>` — the single-bundle
verb. Chosen over `scripts/run_campaign.py` deliberately: with no
campaign policy bound, the controller skips environment admission
entirely (`joulewise/controller.py:929-1019`), writes no campaign-log
row, takes no `campaign.lock`, and emits no verdict — so nothing here
can be mistaken for claim licensing, and the custody fence is satisfied
structurally rather than by promise. The idle capture is lifecycle
stage 4; its artifact is `raw/powermetrics_idle.plist` (canonical name
pinned at `joulewise/adapters/powermetrics.py:51`), with the decoded
8-field sidecar `rich_telemetry_idle.jsonl`.

Configs: `configs/characterization/char-t3appup-r0{1,2,3}.json` (and a
matching `char-t3appdown-*` set for the second arm). `runtime_backend:
"mock"` so no model load perturbs the machine; `telemetry_backend:
"powermetrics"` so the instrument is real (the clock stays real unless
BOTH backends are mock, `joulewise/cli.py:236-240`).
`idle_seconds: 300` at `power_hz: 10` → ~3000 frames per capture.
Sudo: `sudo -n /usr/bin/powermetrics` — verified installed via
`joulewise doctor --json` (`sudo_noninteractive_policy: true`).

## Design: two arms with variance, not one-vs-one

The night plan's original fixed-order single pair (app-up then
app-down) was judged insufficient on its own to authorize app-up claim
windows — correctly, since a single capture per condition yields no
variance estimate and cannot separate a t3 effect from ordinary
drift. This protocol therefore collects **n = 3 per arm**, reporting
each arm's mean and spread and an upper bound on the app-up minus
app-down difference.

- **Arm A (app-UP), collected 2026-08-04 overnight, unattended:** t3
  resident, all threads dormant, no t3 activity.
- **Arm B (app-DOWN), collected with Ed present:** t3 quit, survivor
  inventory taken and survivors stopped by recorded PID + start-time +
  ancestry (never pattern-kill), then the same three captures.

Arm B is deliberately NOT collected unattended tonight: quitting t3
would kill Ed's own observation threads, and the app-death-recovery
acceptance gate wants Ed present for the quit/relaunch anyway. Splitting
the arms costs nothing scientifically and removes an irreversible
action on Ed's environment from an unattended window.

## Declared limitations (recorded before collection, not after)

1. **An operating agent session is present in both arms.** These
   captures run while a Claude Code session sits idle awaiting a
   background job (D-099: an idle agent session is 12-18% CPU of agent
   load). This is a confound the protocol controls by holding it
   constant across arms — the session must be in the same idle-waiting
   state, with zero tool calls and zero output streaming during every
   capture, in both arms. It is NOT eliminated. Eliminating it requires
   a detached zero-agent launcher, which is precisely what
   QUIET-GUARD-01 exists to build; until then this characterization can
   bound a t3 effect but cannot establish an absolute floor.
2. **Fixed order within each arm**, and the arms are separated in time
   (different nights/hours). Thermal and background-daemon state may
   differ between arms; the variance estimate is the only guard.
3. **Non-claim, permanently.** These roots share no baselines, no
   calibration, no NEG-8 evidence, and no custody path with any claim
   chain. No result here may be quoted as, or used to gate, a claim.
4. A negative result (no detectable t3 effect) does NOT by itself
   authorize app-up claim windows; it removes one objection. The
   authorization question belongs to a gate, with the quiet-guard
   machinery landed.

## Analysis (post-collection, desk work)

Per capture, from `rich_telemetry_idle.jsonl` and the raw plist: mean
and p95 package power, sample count, duration, and the same for the
CPU/GPU/ANE components. Report per arm: n, mean, sample SD, and the
between-arm difference with a confidence interval. Compare the observed
spread against the project's attribution limit (~1 J,
`joulewise-attribution-limit` doctrine) so the result is stated in
units the claim doctrine already recognizes.
