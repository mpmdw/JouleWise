# W-01 / W-02 — watchdog pre-arm reliability

Branch `ops/2026-11-10-watchdog-unknown-keys`, based on PR #707 head
`ops/2026-11-10-watchdog-v5-installed` at
`df531145602256ed0c3e95e1cc1c7d82143854af`. The head was fetched only from
the explicitly allowed local shared Git store's remote-tracking ref; there
was no network fetch and no production install.

Authority: owner's 2026-11-10 brief; measurement-system audit §3.3 W-01/W-02
and implicit-state-machines audit §4.3/4.4, read from
`origin/audit/2026-11-10-fable`. M0 and orchestration read. No active stop card.
Coordination state remains lead-owned and untouched. No agents delegated,
no external messages sent, no hardware measurements, no real custody reads.

## W-01

Commit `d8660fda5`.

Files: `scripts/magistrate_watchdog.py`, `tests/test_magistrate_watchdog.py`,
`tests/test_magistrate_watchdog_v5.py`, `tests/test_watchdog_reliability.py`,
`docs/process/MAGISTRATE_WATCHDOG.md`.

- Unsafe decisions distinguish unreadable/malformed plans, unreadable installed
  plists, conflicts, locks, unavailable process tables, and desk fences. An
  unclassified cause keeps the conservative HOLD_UNSAFE fallback.
- Any new unsafe reason immediately enters existing `notice_pending` and the
  typed event journal. Repeated identical observations do not flood the queue
  or reappear merely because the previous notice was acknowledged.
- After 900 seconds of continuous unsafe hold, the status becomes STRANDED
  and queues a separate escalation. Changing malformed bytes/reason/category
  does not restart the dwell. This is an operational state duration, not a
  measurement/analysis threshold.
- STRANDED still forbids launch. Strict plan parsing, all chain fences,
  PID/start-time ownership, and resident cooperative/TERM/KILL drainage remain
  in force. Unknown keys are never accepted to gain permission to launch.

## W-02

Commit `21fe4cec7`.

Files: `scripts/magistrate_watchdog.py`, `tests/test_magistrate_watchdog.py`,
`tests/test_watchdog_reliability.py`,
`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`,
`docs/process/MAGISTRATE_WATCHDOG.md`.

Both the tick's owned-process path and resident supervisor now read heartbeat.
The bounded wire is one plain line `PID ACTIVATION_ID EPOCH_SECONDS`. A valid
stamp must match the lock's PID/activation, be finite, originate within this
activation, and be at most five seconds ahead of the observation clock.
Missing/unreadable/malformed/mismatched/old/future stamps cannot keep a
session apparently healthy. After a 900-second activation-start grace or
stamp age, `magistrate_heartbeat_stale` is queued once per outage. Recovery
enables another notice for a later outage. `state.json` carries age, status,
identity and observation time. This is reporting only: a stale heartbeat
does not independently kill, spawn, release, or un-fence anything.

The prompt now specifies the wire, the lock PID rather than a tool shell PID,
and progress refresh at least once a minute and around long tool calls.
A background ticker that merely simulates progress is explicitly excluded.

## Bound-file impact and limits

`scripts/magistrate_watchdog.py` is in the W1 integration line's
`v4_registration.EXECUTED_CLOSURE` / `ARTIFACTS` and is STRICT. These patches
surface status/notices while preserving the unsafe no-launch direction and
existing process-action ladder. Integrating them changes bound bytes and
requires STRICT re-registration (new exact-candidate receipt, signature,
both gates) before W1, which is not registered yet. No registration text,
analysis engine, estimators, study thresholds, or seeds were edited.
The two changed process documents are not in that artifact set. Registration
code itself is unchanged. This second branch is not merged onto W1 here.

Residual risk: **notice_pending is a local durable queue, not an independent
mail/push transport.** The existing notice.ack/mail path needs a permitted
magistrate activation. While a plan remains unparseable, an Air-side observer
or operator must consume watchdog status/notices. These tests prove immediate
local notice and escalation, not that Ed receives mail during a permanent
hold. No external transport was exercised or installed. A watchdog that never
runs cannot observe or announce its own silence. State/event growth and the
existing whole-queue notice acknowledgement semantics are unchanged.

The dwell expires on the first observation at/after 900 seconds; ordinary
launchd ticks are 300 seconds apart. Stale heartbeat has the same observation
cadence unless a resident polls at its existing 10-second interval.

## Verification

One targeted module at a time; no full-suite execution:

- `python3.13 -B -m unittest tests.test_watchdog_reliability`: **9 passed**,
  0.038 s at the final code. Synthetic plans/plists/clocks/process table; real
  local state writes. Covers immediate unknown-key notice, unreadable plan vs
  plist, exact dwell boundary, no reset on changed bad keys, multi-day safe
  hold, open-chain fencing after schema repair, notice dedupe, heartbeat
  identity/age/error/grace/recovery, and resident heartbeat observation.
- `python3.13 -B -m unittest tests.test_magistrate_watchdog`: **155 passed**,
  3.289 s at the final code. Existing state assertions updated to the precise
  reason names; one long no-heartbeat stand-down now expects its stale notice
  alongside forced_standdown. Existing signal/ownership/fence assertions kept.
- `python3.13 -B -m unittest tests.test_magistrate_watchdog_v5`: **4 passed**,
  0.046 s after the heartbeat code. Unknown-key/schema/future-authorship cases
  still refuse launch and now assert HOLD_PLAN_MALFORMED.
- `python3.13 -B -m compileall -q joulewise tests`: passed.
- `git diff --check`: passed.

During development the old HOLD_UNSAFE assertions failed as expected after
the state split; they were changed to exact category assertions, not removed
or weakened. A test initially mocked the whole os module, suppressing its
own state writes; corrected to mock only fork. A resident fixture's asynchronous
stop probe raced its test assertion; the new fixture supplies an immediate
synthetic CLEAR stop observation. No production stop behavior was changed.

No MLX/Metal tests are relevant to these stdlib operational changes. Live
lead-owned checks still owed: native installed-watchdog dry run on the actual
W1 rendered plan, supervised stale-heartbeat/unknown-plan notice observation,
and the external observer/delivery path. Never install into an armed window.

## Other branch and blocked work

`ops/2026-11-10-w1-reliability` starts at W1 head `9abe6095f` and carries:

- `5bb152acc`: A-01 outcome/fault reporting, verdict preserved.
- `c80d4d638`: A-02 immediate results-ref delivery and honest courier.sent.
- `e787f6c24`: detailed W1 report,
  `docs/run_reports/2026-11-10-w1-reliability.md` on that branch.

That report lists the three changed STRICT production paths
(`scripts/run_night.py`, `joulewise/b5/driver.py`, `scripts/b6_courier.sh`),
9 passing new witnesses, 4 passing closure tests, the unresolved real-process
integration failure, native delivery risk, and the prospective bound-semantics
ruling question for **I-01, production HostLock preflight, and A-04/A-05**.
Those three work groups remain unimplemented under the brief's explicit
"STOP that item" rule. An asynchronous owner question was sent; no answer
has been assumed. W1 is not ready to arm solely from these patches.

Next exact step: owner/lead rules on those bound behavioral changes; review
both local branch diffs; integrate onto the current W1 line; complete the
blocked fixes if authorized; then STRICT re-registration and native PREQUAL /
W1 smoke at the final head. No branch was pushed or merged.
