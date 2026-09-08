```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Replace argv classification with custody and campaign liveness markers; add process start identities and automatic campaign-root discovery.",
  "workspace": {
    "base_requested": "HEAD",
    "base_mode": "informational",
    "head_start": "b5786cea113f8aa08a75cbbd14cd89275b16d236",
    "head_end": "b5786cea113f8aa08a75cbbd14cd89275b16d236",
    "upstream_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "counts": {"blocker": 0, "should_fix": 3, "nit": 0},
    "findings": [
      {"id": "F1", "severity": "should_fix", "summary": "The status guard classifies mentions as execution and exempts real execution based on unrelated argument words."},
      {"id": "F2", "severity": "should_fix", "summary": "Existing chain and campaign markers record PIDs without process start identities."},
      {"id": "F3", "severity": "should_fix", "summary": "Campaign markers need automatic discovery across arbitrary runs directories; checking only repository-local runs is incomplete."}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --exit-code; git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["b5786cea113f8aa08a75cbbd14cd89275b16d236"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^b5786cea113f8aa08a75cbbd14cd89275b16d236$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only design inspection completed; no implementation, tests, publication, or live measurement was performed.",
      "needs": "Lead applies the seat brief and owns final verification."
    }
  ]
}
```

## Findings

**F1 — Retire the classifier.** `scripts/window_status.sh:69` exempts commands by words anywhere in their flattened arguments; `:74`–`:83` treats path mentions as execution. Another exemption or regex cannot repair this boundary.

**F2 — Add actual process identity.** Neither marker’s wall-clock creation timestamp is a process start token. Reuse the watchdog’s **identity comparison**, not its command classifier: `scripts/magistrate_watchdog.py:854`–`:864` requires the recorded PID and `start_time` to match the observed process.

**F3 — Make campaign markers discoverable.** `--runs-dir` is unrestricted and defaults to the invocation’s relative `runs` directory (`scripts/run_campaign.py:671`). Checking only the publication checkout misses standalone campaigns and measurement clones. Use an automatically published registry entry; do not require the operator to maintain a list of campaign directories.

### Inventory

All references describe the inspected HEAD.

| Artifact | Writer and contents | Exit/removal semantics; suitability |
|---|---|---|
| `<plan>/night/chain.started` | `scripts/run_night.py:358`–`:378`: `O_EXCL` claim, then JSON containing child `pid`, `pgid`, and write-time `epoch_s`. Child starts in a new session at `:424`–`:429`. | Retained as once-only custody. Launch failure fills null identities and an error (`:382`–`:398`). **Useful after adding a start token.** An empty-file interval exists between exclusive claim and completion. |
| `<plan>/night/chain.exited` | `_record_chain_exit`, `scripts/run_night.py:310`–`:326`: exit code, timestamps, optional reaper/failure fields. | Written after normal `wait()` (`:491`–`:492`), successful termination/reap (`:329`–`:355`), launch failure (`:432`–`:433`), or dead-man reconciliation (`:1380` onward). Retained. It proves the recorded child exited, not universally that every descendant exited. |
| `<plan>/night/chain.unkilled` | `scripts/run_night.py:463`–`:465`: PGID and timestamp when termination cannot be proven. | Retained diagnostic. Do not mistake its age for proof of quiescence. |
| `<plan>/night/censuses.jsonl` | Created even on malformed-plan handling (`scripts/run_night.py:1048`) and normal startup (`:1093`); appended by `:305`–`:307`, called during execution at `:452`–`:454`. | Historical agent-census evidence; no removal on exit. **Neither existence nor freshness establishes measurement liveness.** |
| `<plan>/night/courier.lock` | `scripts/run_night.py:743`–`:754`: `O_EXCL`; refreshed with courier-launcher PID and epoch at `:737`–`:740`. | Stale detection combines bounded age and PID liveness (`:720`–`:734`); stale file unlinked before retry (`:751`). Closed and unlinked in `finally` (`:852`–`:854`). Tracks handback, not capture. |
| `<plan>/night/courier.heartbeat`, `courier.sent` | The launched courier is instructed to write heartbeat first and sent after accepted email: `docs/process/NIGHT_COURIER_PROMPT.md:3`–`:5`, `:14`–`:17`. Driver launches that courier and observes the files (`scripts/run_night.py:795`–`:814`). | Heartbeat removed before retries (`:791`); sent retained and used to suppress dead-man retry (`:1351`–`:1355`). **No deterministic in-repo function writes `courier.sent`; its writer is the prompted courier.** Neither file should override a live measurement marker. |
| `<runs_dir>/campaign.lock` | Already exists—no leading dot. `scripts/run_campaign.py:3156`–`:3184`: `O_EXCL`, PID, random nonce, creation timestamp, flush/fsync. | Existing collision refuses and requests manual stale-lock removal (`:3169`–`:3177`); **no current PID-based stale reclamation**. Acquisition failure cleans up (`:3196`–`:3204`). Release preserves replacement files using ownership/inode checks (`:3300`–`:3333`). Production AXI acquires/releases at `:7272`/`:8016`; ordinary execution at `:8228`/`:8927`. Both release in `finally`; SIGKILL can leave stale files. |
| Launch consumption and lifecycle receipts | `scripts/launch_window.py` delegates to `joulewise/arm_readiness.py`: consumption exclusive write at `:9774`; lifecycle exclusive writes at `:10021`–`:10040`. | Durable lineage, not PID locks. Successful launcher `execve` replaces itself; there is no supervising wait/cleanup path. Receipts alone cannot establish present liveness. |
| `<custody-parent>/magistrate/magistrate.lock` | `scripts/magistrate_watchdog.py:2009`–`:2024`: exclusive STARTING record for supervisor; `:2039`–`:2051`: atomic ACTIVE replacement with child PID/start time. Installer can also seed it (`scripts/install_magistrate_watchdog.sh:269`–`:295`). | Spawn-failure removal `:2028`; child completion removal `:1638`; stale-owner reconciliation `:1386`–`:1407`. Installer rollback conditionally removes its unchanged seed (`scripts/install_magistrate_watchdog.sh:191`–`:193`). Tracks an agent, **not measurement**. |
| `magistrate/watchdog.lock`, `state.json` | Service lock opened and `flock`ed at `scripts/magistrate_watchdog.py:2224`–`:2237`; state atomically persisted, e.g. `:2056`, `:2276`. | Closing descriptor releases flock; lock pathname persists. State persists across ticks/exits. Neither pathname proves capture. |

### Census specification

**Identity interface**

Implement `observe_identity(pid) → LIVE(start_time) | DEAD | UNKNOWN`.

Use the watchdog’s PID/start-time comparison. A narrow production probe may request only a specific PID’s `lstart` and process state; it must never request or inspect command text. Normalize under a fixed locale. A missing process or zombie is DEAD; permission/probe failure is UNKNOWN. Tests inject this function and never execute `ps`.

The watchdog currently obtains `lstart` from its process table at `scripts/magistrate_watchdog.py:201`–`:225`. Reuse that token convention for new writers and readers. Keep `epoch_s` as diagnostic data only.

**Discovery**

1. Enumerate direct plan directories under `~/night-custody/`, inspecting `night/chain.started` and `night/chain.exited`. Support explicit additional custody parents through a JSON-array environment setting; paths are data, never shell fragments.
2. Use `~/night-custody/active-campaigns/` as a shared discovery registry for production campaign execution. Each production acquisition publishes an exclusive, uniquely named JSON entry containing:
   `schema`, `pid`, `start_time`, `runs_root`, and the existing campaign-lock `nonce`.
3. The registry entry is itself a liveness marker. A live entry refuses even if its referenced lock disappears. This avoids turning a missing pointer target into permission to publish.
4. Writers and reader share an overridable custody-parent setting. Tests always substitute a temporary parent. The status repository setting must not implicitly select measurement roots.

**Rule A — chain**

`chain.started` present, `chain.exited` absent, valid recorded identity still alive → **REFUSE**.

Add `start_time` to `_complete_chain_start`; record the **chain child**, not the driver. Refuse during the entire chain, including settle periods and inter-campaign gaps.

A valid exited marker closes this rule. Campaign entries remain independently evaluated; `courier.sent` never closes either rule.

**Rule B — campaign**

A campaign registry entry whose PID/start identity is alive → **REFUSE**.

Reuse existing `campaign.lock`; do not introduce a competing `<runs_dir>/.campaign.lock`. Add its process start token without changing nonce/inode ownership guarantees. Publish the registry entry at the two production execution acquisitions, before any measurement child is launched. Remove only that acquisition’s entry in `finally`, alongside lock release. Dry-run and maintenance-only acquisitions do not publish entries.

On normal exception/exit, cleanup runs. SIGKILL can leave markers: PID disappearance or start-token mismatch makes them **stale**, producing WARN without refusal.

Stale detection here is observational. **Do not silently add automatic reclamation to the existing campaign serialization lock**: that changes a separate concurrency contract. Its current explicit repair workflow remains.

**Uncertain evidence**

- Empty/malformed open chain marker, unreadable discovered marker, or UNKNOWN identity → **REFUSE: census indeterminate**, before status-file writes.
- Legacy PID-only marker: absent PID → stale WARN; present PID without a comparable token → indeterminate REFUSE. Never invent a start token from `epoch_s`.
- Missing default custody directory → empty census; unreadable directory → indeterminate REFUSE.
- A marker disappearing during inspection is reread/reconciled once; continuing instability is indeterminate.
- Do not delete or rewrite custody during census.

These refusals cover ordinary interrupted writes and incomplete observations, not hypothetical tampering.

**Rule C — argv**

Remove the process census and classifier entirely, including `JOULEWISE_STATUS_PS_COMMAND`. No argv diagnostic is needed. Editors, test names, prompts, spaced paths, `--`, and argument words cease to affect the result.

Preserve the existing freeze-sentinel behavior after a clear census.

### Miss analysis

| Process/situation | Coverage and significance |
|---|---|
| Driver-managed chain, arbitrary chain name | Rule A covers it. Filename and interpreter options are irrelevant. |
| Standalone production `run_campaign.py`, arbitrary runs directory | Rule B covers it through automatic registration. |
| Hand-run chain without driver | Covered while its production campaigns run; **not covered during preceding settle or inter-campaign gaps**. This matters if those periods belong to the protected quiet window. |
| Direct `python -m joulewise run`, custom collector, old uninstrumented checkout | Neither rule necessarily covers it. These are explicit coverage exclusions, not proof that publication is safe. |
| Dead driver, surviving chain | Covered because Rule A records the chain child. |
| Dead chain leader, surviving campaign parent | Rule B still covers the campaign. |
| Dead campaign parent, surviving measurement child | May be missed once the parent identity is dead. Parent liveness is not process-group quiescence. |
| Launch occurring after census passes | Snapshot race remains; census is not mutual exclusion between capture and publication. |

D-127 explicitly retains full agent exit during capture (`docs/decision_log.md:8245`). This helper prevents a particular accidental publication; it does not establish quiet-machine compliance by itself.

D-161’s operative distinction is **mistake versus deliberate action** (`docs/decision_log.md:10394` onward). Deliberately deleting markers or choosing an uninstrumented route does not justify a tamper-resistant guard. But an ordinary hand launch, crash orphan, or concurrent scheduled start cannot automatically be dismissed as an adversary.

For this bounded seat, document those exclusions and retain the prescribed driver-managed, sequential publication/launch workflow. If the lead requires supported hand-launch settle coverage or concurrent-start exclusion, that needs a chain-wide marker/shared exclusion mechanism as a separate extension—not renewed argv matching.

## Residual risk

The proposed census detects registered live owners. It does not prove absence of every possible collector, surviving descendant, or future launch. Existing `lstart` tokens also have the watchdog’s timestamp precision; they are practical PID-reuse protection, not a cryptographic process identity.

Deployment must update the actual measurement checkout and use the same custody parent as the publication helper. Updating only this worktree does not instrument an older running campaign.

## SEAT BRIEF

**Objective:** Replace `window_status.sh` argv classification with the census specified above. Preserve publication and freeze behavior. No live captures, pushes, commits, watchdog installation, or changes to immutable custody.

**WRITE_SCOPE — exact paths:**

- `scripts/window_status.sh`
- `scripts/run_night.py`
- `scripts/run_campaign.py`
- `joulewise/measurement_liveness.py`
- `tests/test_window_status_guard.py`
- `tests/test_measurement_liveness.py`
- `tests/test_run_night.py`
- `tests/test_run_campaign.py`

**Deliverables:**

1. Shared identity, marker parsing, registry publication/cleanup, and census implementation in `joulewise/measurement_liveness.py`, with an injectable identity observer.
2. Chain-child `start_time` recording; preserve existing once-only and exit semantics.
3. Additive campaign start identity and production-only registry publication at ordinary and AXI execution acquisitions. Preserve existing campaign-lock ownership and stale-repair semantics.
4. Status shell invokes the marker census before any write; remove argv classification and its test hook.
5. Temporary-root fixtures for every changed test. No reads of host custody, no host process census, and no registry writes under the real home directory.
6. Return a clause map linking each behavior to its production site, biting assertion, and executed counterfactual. Lead owns bookkeeping and deployment.

**Deterministic regressions and counterfactuals:**

| Assertion | Counterfactual it must catch |
|---|---|
| Open chain with matching PID/start refuses before any status write or Git action | Ignore chain markers |
| Closed chain permits publication when no campaign is live | Ignore `chain.exited` |
| Same PID with different start token warns and permits | Compare PID alone |
| Dead PID with stale markers permits | Refuse on file existence alone |
| Legacy live-PID or malformed open marker refuses as indeterminate | Treat parse/identity uncertainty as empty census |
| `courier.sent` cannot suppress a live chain/campaign | Short-circuit on sent |
| Production campaign in an unrelated, spaced runs directory refuses | Inspect only `$REPO/runs` |
| Ordinary and AXI execution publish before mocked child launch | Remove either registration call |
| Exceptions release owned registry entries; replacement entries survive cleanup | Unconditionally unlink by pathname |
| Dead owner leaves harmless stale registry entry | Treat stale entry as live |
| Dry-run and maintenance-only acquisition publish no measurement entry | Register every lock acquisition |
| Mentions in editors, prompts, test names and paths do not affect output | Restore argv classifier |
| Live marker under a path containing `unittest` still refuses | Restore global word exemption |
| Freeze sentinel still permits local status write but prevents publication after a clear census | Move or remove freeze branch |
| Root/probe error refuses before status/Git mutation | Convert observation error to clear |

Test the shell with fake identity-probe executables and temporary custody. Mock measurement subprocesses in writer tests. Replace the old command-shape tests with marker-state assertions; install a failing `ps` stub to prove regression tests never consult host processes.

**Acceptance modules:**

```text
python3 -m unittest tests.test_measurement_liveness tests.test_window_status_guard
python3 -m unittest tests.test_run_night tests.test_run_campaign
python3 -m unittest tests.test_launch_window tests.test_magistrate_watchdog
python3 -m unittest discover -s tests
bash -n scripts/window_status.sh
git diff --check
```

Final handoff must report actual results, exact changed paths, clause-map counterfactual results, and the documented hand-launch/orphan/snapshot limitations. No fixture result may be described as live quiet-Mac validation.