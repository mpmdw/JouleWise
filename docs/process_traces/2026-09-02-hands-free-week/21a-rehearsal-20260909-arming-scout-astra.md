```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "partial",
  "summary": "Read-only inspection complete; a nonexistent fake measurement checkout cannot pass the night installer, so an executable arming sequence requires a lead ruling.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "67cbf5fe66fc5b161684de4abc075182bb895356",
    "head_end": "67cbf5fe66fc5b161684de4abc075182bb895356",
    "upstream_end": "67cbf5fe66fc5b161684de4abc075182bb895356",
    "branch": "bookkeeping/2026-09-08-activation-evidence"
  },
  "pathspec": [],
  "unowned_dirty": [
    "/Users/edr/code/JouleWise-wt-fan-WATCHDOG-CENSUS-01/docs/process/MAGISTRATE_WATCHDOG.md",
    "/Users/edr/code/JouleWise-wt-fan-WATCHDOG-CENSUS-01/scripts/install_magistrate_watchdog.sh",
    "/Users/edr/code/JouleWise-wt-fan-WATCHDOG-CENSUS-01/scripts/magistrate_watchdog.py"
  ],
  "verdict": {
    "rows": [
      {"row": "Review proposed night", "action": "start_now"},
      {"row": "Choose installable rehearsal checkout", "action": "needs_ruling"},
      {"row": "Author and install night", "action": "wait_for"},
      {"row": "Use nonexistent fake root with current installer", "action": "do_not_start"},
      {"row": "Real measurement plan", "action": "wait_for"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD '@{upstream}'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "67cbf5fe66fc5b161684de4abc075182bb895356",
          "67cbf5fe66fc5b161684de4abc075182bb895356"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "67cbf5fe66fc5b161684de4abc075182bb895356"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## bookkeeping/2026-09-08-activation-evidence...origin/bookkeeping/2026-09-08-activation-evidence"]
      },
      "expected": {"exit_code": 0, "tail_regex": "^## bookkeeping/2026-09-08-activation-evidence"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: the documented fake-root bench plan is schema-valid but cannot pass install_night_agent.sh:88-90. NIGHT_HANDBACK also requires installation from measurement_root.",
      "needs": "Approve a disposable real Git checkout used only for REHEARSAL_STUB, or route a reviewed contract/implementation change. Do not invent an installer bypass."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "ps inspection of PIDs 71607 and 71666 was denied with operation not permitted. Their present liveness and identities remain unverified; custody and installed services were not inspected.",
      "needs": "Lead verifies PID plus start-time identities and installed watchdog provenance."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The separate watchdog-census checkout has three uncommitted files. Its watchdog diff changes handoff and dead-lock handling, not plan scanning or frozen-checkout rows.",
      "needs": "Reinspect the reviewed landed version and running watchdog provenance before arming."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "REHEARSAL_STUB can produce result verdict REHEARSAL_ONLY despite a refused gate receipt; both artifacts must be harvested.",
      "needs": "Accept only the specifically allowed agent-present receipt refusal; investigate every other receipt refusal."
    }
  ]
}
```

## Scheduling matrix

All commands below are **proposals for the magistrate**, not executed actions. Repository citations refer to the inspected `67cbf5f` checkout unless explicitly marked as the concurrent checkout.

| Row | action | wait_for | collision surface |
|---|---|---|---|
| Resolve rehearsal checkout | needs_ruling | Lead chooses an installable checkout | Fake-root documentation versus unconditional Git checks |
| Rewrite and commit handback | wait_for | Checkout ruling and final reviewed driver version | Moving HEAD after pinning |
| Email, author plan, install both agents | wait_for | Handback commit; email accepted; no Ed NO | Watchdog discovers the plan as soon as it exists |
| End magistrate session | wait_for | Arming finished, **before 02:31 PDT September 9** | Owned descendants and unrelated interactive seats |
| Launchd rehearsal, 02:56 | wait_for | Installed agents | Agent census and stale pins |
| Morning harvest and uninstall | wait_for | Driver/courier completion | Repeated daily jobs, incomplete reporting |
| Any real plan | do_not_start | Fresh post-watchdog rehearsal accepted; stub-root cleanup | Explicit kernel gate |

The post-watchdog requirement is explicit at `docs/process/state_kernel.json:2965`; email-before-arm and Ed’s NO are at `:3020`. The inspected kernel still carries the watchdog dependency as pending at `:3004` and the rehearsal as blocked at `:3043`; the lead must reconcile this stale bookkeeping with the supplied activation evidence.

## Critical path

**Checkout ruling → final handback commit → arming notice → plan publication → installation → magistrate exit → launchd/courier evidence → harvest/uninstall → eligibility review for a real plan.**

### 1. Blocking ruling and exact proposed authoring sequence

**NEEDS_RULING:** May this night use a disposable **real Git checkout** under `/private/tmp`, exclusively as a rehearsal checkout?

Options considered:

- **Nonexistent fake root:** matches the watchdog bench example, but installation cannot succeed.
- **Disposable real checkout:** preserves isolation from actual measurement data and satisfies the existing installer and handback rules. **Recommended, subject to lead approval.**
- **Installer exception:** requires separately authorized, reviewed code/contract work; no bypass is proposed.

The fake example uses zero hashes and a nonexistent measurement path at `docs/process/MAGISTRATE_WATCHDOG.md:282`. It is a watchdog dry-run bench, not proof that night installation accepts those values (`:299`). The installer unconditionally executes `git -C "$measurement_root" rev-parse HEAD` and exits 3 on failure at `scripts/install_night_agent.sh:88`.

The following sequence is conditional on approving the disposable-real-checkout option. It deliberately stops before publication unless that ruling exists.

1. In the lead’s authorized worktree, rewrite the handback with the draft below and commit it through the required review workflow. Call the resulting commit **H**.
2. Send Ed the concrete arming notice: September 9, 02:56 PDT; `REHEARSAL_STUB`; built-in two-second shell stub; no real measurement; launches unless Ed replies NO. Record acceptance/message ID. An Ed NO stops the sequence.
3. Create the disposable checkout at **H**, then author the plan using the writer:

```zsh
# Run later, only after the lead approves this checkout choice.
# DRIVER_SOURCE must be the authorized worktree at the committed handback H.
export DRIVER_SOURCE=/Users/edr/code/JouleWise-wt-magistrate-1ef89702
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260909-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260909

export HAND_BACK_HEAD="$(git -C "$DRIVER_SOURCE" rev-parse HEAD)"
git -C "$DRIVER_SOURCE" show --stat "$HAND_BACK_HEAD" -- docs/process/NIGHT_HANDBACK.md

# Proceed only after verifying this is H, the intended handback commit.
test ! -e "$STUB_CHECKOUT"
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$HAND_BACK_HEAD"

cd "$STUB_CHECKOUT"
export NIGHT_REPO_HEAD="$(git rev-parse HEAD)"
export NIGHT_MEASUREMENT_HEAD="$(git -C "$STUB_CHECKOUT" rev-parse HEAD)"
test "$NIGHT_REPO_HEAD" = "$HAND_BACK_HEAD"
test "$NIGHT_MEASUREMENT_HEAD" = "$HAND_BACK_HEAD"

PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from joulewise.night_gate import NightPlan
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ["NIGHT_CUSTODY"])
target = root / "night_plan.json"
assert not root.exists(), "Use fresh custody; do not overwrite prior evidence"

t0 = datetime(
    2026, 9, 9, 2, 56, 0,
    tzinfo=ZoneInfo("America/Los_Angeles"),
).timestamp()
assert t0 == 1788947760
now = time.time()
assert now < t0 - 25 * 60, "Arming must finish before request deadline"
assert t0 + 900 - now <= 36 * 3600, "Keep full gate window within freshness"

plan = NightPlan(
    plan_id="rehearsal-20260909",
    receipt_class="REHEARSAL_STUB",
    t0_epoch_s=t0,
    window_max_s=900,
    authored_epoch_s=now,
    repo_head=os.environ["NIGHT_REPO_HEAD"],
    measurement_root=os.environ["STUB_CHECKOUT"],
    measurement_head=os.environ["NIGHT_MEASUREMENT_HEAD"],
    chain_path=str(root / "chain.sh"),
    chain_sha256_path=str(root / "chain.sh.sha256"),
    custody_root=str(root),
    registration_path=str(root / "registration.json"),
)
print(write_night_plan(target, plan))
PY
```

This is a **stub-only plan**. The chain and registration paths above are explicitly placeholders, following the bench shape; they do not constitute valid registration or real-chain evidence.

| Field | Value and reason |
|---|---|
| `plan_id` | `rehearsal-20260909`; requested unique night identity |
| `receipt_class` | `REHEARSAL_STUB`; selects the built-in stub and cannot establish GO |
| `t0_epoch_s` | `1788947760`, equivalent to `2026-09-09T02:56:00-07:00` |
| `window_max_s` | `900`; gate window ends 03:11 PDT |
| `authored_epoch_s` | Actual publication-time `time.time()`; future or older-than-36-hour plans refuse |
| `repo_head` | **H**, obtained at arm time using `git rev-parse HEAD` in the driver checkout |
| `measurement_root` | Proposed `/private/tmp/joulewise-rehearsal-20260909-checkout`; requires the ruling above because it is a real disposable checkout |
| `measurement_head` | **H**, obtained with `git -C "$STUB_CHECKOUT" rev-parse HEAD`; immutable through completion |
| `chain_path` | `/Users/edr/night-custody/rehearsal-20260909/chain.sh`; unused stub placeholder |
| `chain_sha256_path` | Same root, `chain.sh.sha256`; this is a **sidecar path**, not a digest-valued `chain_sha256` plan field |
| `custody_root` | `/Users/edr/night-custody/rehearsal-20260909` |
| `registration_path` | Same root, `registration.json`; required nonempty placeholder for this stub, not authenticated registration |

All twelve fields are defined at `joulewise/night_gate.py:184`; registration cannot be null for a stub (`:283`). The writer supplies both schema discriminators and validates the mapping at `joulewise/night_plan_writer.py:20`, then publishes atomically at `:38`.

**Important limitation:** the real gate attempts to read and authenticate registration if it reaches C1 (`joulewise/night_gate.py:908`). With this placeholder absent, a quiet-machine receipt can refuse for that reason. The driver still runs its built-in stub despite a refused receipt (`scripts/run_night.py:1169`). Therefore, this exact placeholder plan is suitable only with that limitation expressly understood; a non-agent refusal must be reported as a finding, not accepted as clean completion. A fully green gate requires the lead to supply the governed registration and other live gate prerequisites, not fabricated substitutes.

There is **no dead-man field** in `NightPlan`. Completion is `t0 + 900 + 300 = 03:16 PDT`; dead-man is September 9 at 07:00 (`scripts/run_night.py:45`, `:926`, `:938`). If installed before September 8’s 07:00 firing, that firing precedes completion and stands down; installation later cannot produce that earlier observable (`:1352`).

### 2. Installer: one invocation installs both agents

After the ruling, checkout preparation, email, and plan publication:

```zsh
cd /private/tmp/joulewise-rehearsal-20260909-checkout
scripts/install_night_agent.sh \
  --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json \
  --hour 2 --minute 56
```

This installs:

- `com.joulewise.night`: `run`, daily 02:56.
- `com.joulewise.night.deadman`: `dead-man`, daily 07:00.

Both labels and render calls are in `scripts/install_night_agent.sh:156` and `:187`; bootstrap and rollback are at `:194`.

Run the script **from the plan’s measurement checkout**, as required by `docs/process/NIGHT_HANDBACK.md:81`. More precisely, the installer derives its driver checkout from **the script’s own location**, not merely shell cwd (`scripts/install_night_agent.sh:31`).

Checks include:

- Valid v2 schema, no surrounding measurement-root whitespace, nonfuture author time, age ≤36 hours (`:44`).
- `repo_head == driver checkout HEAD` (`:80`).
- `measurement_head == measurement_root HEAD` (`:88`).
- Executable Claude courier, resolved and pinned (`:96`).
- Night hour differs from dead-man hour (`:108`).
- No prior write-once night records (`:177`).

**No invocation can install the supplied nonexistent-fake-root design successfully.** Running from a development checkout does not avoid `:88`; running from the nonexistent root is itself impossible. `--render-only` also performs the pin checks.

### 3. Draft replacement handback sections

Commit this text only after resolving the checkout and registration limitations. Replace prospective statements with observed arming evidence; do not assert an email was sent before it was accepted.

**Purpose of this night**

> Plan `rehearsal-20260909`, class `REHEARSAL_STUB`, is the fresh post-watchdog rehearsal required by `NIGHT-REHEARSAL-01`. Scheduled launch: September 9, 2026 at 02:56 PDT, window 900 seconds, inside the 02:45–03:30 local belt. The installed night driver executes only its built-in `sleep 2; echo REHEARSAL` stub: no pack, model, measurement, or sudo.
>
> The arming notice precedes installation; Ed’s NO overrides the night. Record the accepted arming-email message ID in the arming evidence. Expected result verdict is `REHEARSAL_ONLY`, with chain exit code 0. A gate receipt refusing `night_refused_agent_present` is acceptable for this stub; every other refusal is a finding. Read the receipt even when the result says `REHEARSAL_ONLY`.
>
> Both plan HEAD pins identify the commit that rewrote this handback, as checked in the approved disposable rehearsal checkout. Preserve that checkout through completion. The magistrate ends its loop and exits before 02:31 PDT September 9.

**Where the results are**

> Results branch: `night-results/20260909` on `origin`, if the driver’s push succeeds.
>
> Primary custody: `/Users/edr/night-custody/rehearsal-20260909/night/`: `result.json`, `receipt.json`, any `refusal.json`, chain markers, census records, and courier records. Driver log: `/Users/edr/night-custody/rehearsal-20260909/night.log`.
>
> If installed before September 8 at 07:00, harvest that morning’s pre-night dead-man stand-down log line. Otherwise explicitly record that this night did not repeat that timing case. September 9’s dead-man is 07:00.

**Next lane**

> The magistrate harvests result, receipt, courier acceptance/message ID, results-branch push evidence, and applicable dead-man evidence. Record the fresh post-watchdog result under `NIGHT-REHEARSAL-01`; do not close the gate from the top-level result alone.
>
> Uninstall both night agents using the command below. Investigate any refusal other than `night_refused_agent_present`; never re-arm the same plan on the same signature twice. Before a real plan, preserve required evidence and remove the rehearsal plan roots as the watchdog runbook requires. The first diagnostic-plan email remains due before a `DIAGNOSTIC_NO_PACK` plan is armed.

The existing handback requires the rewrite/commit at `docs/process/NIGHT_HANDBACK.md:3` and identifies the pin as the rewrite commit at `:70`. **H is not today’s inspected `67cbf5f` unless that commit is actually replaced by the new rewrite commit before pin capture.** Author the external plan after H exists; do not attempt a self-referential commit containing its own SHA.

### 4. Frozen-checkout list and deadlines

For the recommended checkout option, with no other incomplete plans:

```json
[
  ["__canonical_repo__", "/Users/edr/code/JouleWise", null],
  ["rehearsal-20260909", "/private/tmp/joulewise-rehearsal-20260909-checkout", "<H: full 40-character commit>"]
]
```

The canonical row uses **null**, not the canonical checkout HEAD. Plan rows pin canonicalized `measurement_root` plus `measurement_head`, not `repo_head` (`scripts/magistrate_watchdog.py:797`).

With default custody, discovery scans:

```text
/Users/edr/night-custody/*/night_plan.json
```

It derives that glob from `storage.root.parent` (`scripts/magistrate_watchdog.py:258`). It **does not inspect launchctl to establish arming**: valid authored plans are treated as armed until courier completion/final bound, with an open chain extending ownership (`:739`). Thus publication alone affects the watchdog, even if subsequent installation fails.

All other authored, incomplete plans must also appear. Conflicting roots/heads or overlapping spans across different roots hold relaunch (`:765`). No custody scan was performed here, per the brief.

For this t0:

| PDT, September 9 | Enforcement |
|---|---|
| **02:31** | REQUEST boundary; magistrate must already be exiting |
| **02:40** | TERM owned descendants, then owned root |
| **02:41** | KILL surviving owned descendants/root |
| 02:45–03:30 | Fixed belt prevents launch |
| 03:16 | Nominal plan completion boundary |
| 07:15 | Dead-man-plus-lock-fresh bound absent courier completion; open chain can extend further |

These follow `docs/process/MAGISTRATE_WATCHDOG.md:40`, `scripts/magistrate_watchdog.py:717`, and `scripts/run_night.py:47`. **REQUEST does not immediately kill the magistrate.** Unrelated census matches are never kill authority (`docs/process/MAGISTRATE_WATCHDOG.md:49`).

### 5. Morning harvest and exact uninstall

The courier writes its heartbeat first, reads handback and authoritative result/receipt, emails Ed the verdict, chain exit code, refusal reason/detail, and results branch, then writes `courier.sent` after acceptance (`docs/process/NIGHT_COURIER_PROMPT.md:3`).

The email also includes watchdog state path, age, and last decision. Missing/unavailable age or age over 900 seconds must report watchdog death (`scripts/run_night.py:619`).

Harvest:

```text
/Users/edr/night-custody/rehearsal-20260909/night/result.json
/Users/edr/night-custody/rehearsal-20260909/night/receipt.json
/Users/edr/night-custody/rehearsal-20260909/night/courier.sent
/Users/edr/night-custody/rehearsal-20260909/night/courier.json
/Users/edr/night-custody/rehearsal-20260909/night.log
```

Receipt publication is at `scripts/run_night.py:1146`; result publication at `:867`. The driver uses a fresh shallow results clone and attempts to push `night-results/20260909`, copying artifacts under `docs/process_traces/night-results/20260909/` (`:532`). Push failure is logged, so branch existence must be verified rather than presumed (`:576`).

```zsh
cd /private/tmp/joulewise-rehearsal-20260909-checkout
scripts/install_night_agent.sh \
  --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json \
  --hour 2 --minute 56 --uninstall
```

This removes both agents/plists (`scripts/install_night_agent.sh:170`). Uninstall skips both HEAD checks and Claude resolution (`:43`), but still requires the plan file and script/template prerequisites (`:29`). Keep custody available until after uninstall.

### 6. Ranked machine-specific risks

1. **Blocking: nonexistent fake measurement root.** The watchdog bench fixture is not installable by the current night installer. Resolve the checkout choice before publication; otherwise even a failed install leaves a discoverable plan fence.

2. **Interactive Claude and Codex seats at 02:56.** The production census matches `codex|claude|t3` (`joulewise/night_gate.py:38`). However, the implementation nuance matters: a stub continues after a refused gate receipt, disables census-triggered chain abort, and can emit `REHEARSAL_ONLY` with driver base exit 3 (`scripts/run_night.py:1169`, `:1265`, `:1284`). Harvest the refusal from `receipt.json`; do not mistake result success for an agent-free night.

3. **Stale twin 71607 / daemon 71666.** Their identities and present liveness are supplied context, not independently verified: sandboxed `ps` was denied. A fresh PID-plus-start-time check is needed before any lead-owned retirement action. The watchdog must not kill unrelated census matches (`docs/process/MAGISTRATE_WATCHDOG.md:49`).

4. **Concurrent watchdog change is uncommitted and not proven active.** In `/Users/edr/code/JouleWise-wt-fan-WATCHDOG-CENSUS-01`, the inspected diff adds daemon/resumed-twin classification at `scripts/magistrate_watchdog.py:889`, handoff refusals at `:911`, and `HOLD_UNSAFE: dead_lock_resumed_twin` at `:1359`. Its handoff census explicitly must not replace the night census (`:932`). The diff does **not** change `glob_plans`, `load_plans`, `plan_is_armed`, or `fenced_checkout_rows`. Verify the final landed version and running supervisor provenance; an in-flight source edit does not establish running behavior.

5. **Placeholder registration can conceal another refusal beneath `REHEARSAL_ONLY`.** The gate authenticates registration at `joulewise/night_gate.py:908`; the stub result does not certify that it passed. This is a separate limitation from installer success.

6. **Daily firing and incomplete courier evidence.** Both jobs remain installed until explicitly removed. Existing records refuse a rerun (`scripts/run_night.py:1084`); absent courier completion can prolong the watchdog fence (`scripts/magistrate_watchdog.py:734`). Morning harvest and uninstall are required, not optional cleanup.

**Next exact step:** the lead rules on using a disposable real rehearsal checkout and resolves whether this night intentionally accepts placeholder-driven gate findings or supplies governed gate inputs. No files, plans, custody, agents, or processes were changed.