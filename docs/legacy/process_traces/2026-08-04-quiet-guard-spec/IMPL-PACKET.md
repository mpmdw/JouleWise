# QUIET-GUARD-01 implementation packet

Packet basis: exact implementation-intake baseline `e160c8972fa253ac5b6489a1532f275111565b4a`; the adopted design and Ed's four rulings are in `CONSULT-RECORD.md`; the full rollout is SHA-256 `83bd744b8ee3a0eed37df82410642cc440a3d993051d6d1be98b67a062353c62`. Q2, Q3, Q10, and Q13 are already ruled and are constraints below, not reopened questions. “Guard state” and “guard receipt” below always mean `/Library/Application Support/JouleWise/quiet-guard/**`; the runtime never writes bridge `.codex-bridge/**`, run bundles, manifests, `RUN_STATE.md`, `TASK_QUEUE.md`, decision logs, or any other scientific/audit artifact.

## Open-question resolutions

The packet-internal set is the rollout's 25 questions minus Ed-owned Q2, Q3, Q10, and Q13: **21 resolutions**.

1. **Q1 — Decision:** Use the adopted two-phase names exactly: the initiating T3 session may create only `handoff_pending`; only the detached watcher may enter `quiet_held`, after the session identity disappears and both the registry and independent census are zero.
   **Rationale:** This is the binding resolution of the arm-while-agent-alive contradiction and preserves fail-closed admission.

4. **Q4 — Decision:** Discover the T3 family anew for every request from the exact app bundle instance and initiating-session ancestry, record PID + process start time + executable + argv digest + ancestry, and treat an unlinked helper or `cloudflared` as an unknown survivor that is never killed and blocks promotion.
   **Rationale:** Version-pinned process names are brittle and could kill an unrelated shared helper, whereas exact observed identities can be revalidated immediately before action.

5. **Q5 — Decision:** Pin the current adapter to application `T3 Code (Alpha)`, bundle ID `com.t3tools.t3code`, and observed version `0.0.31`; quit by bundle ID through Apple Events, relaunch with `/usr/bin/open -b com.t3tools.t3code`, and declare readiness only after the app plus its observed family are stable and the app-death receipt proves history/checkpoint presence, cwd/worktree, provider, permission mode, and epoch continuity; do not automatically resume a turn.
   **Rationale:** The installed `Info.plist` supplies stable app identity and URL schemes, while a process appearing is weaker than the recurring app-death acceptance contract.

6. **Q6 — Decision:** Allow 120 seconds for the initiating session to self-exit and 30 seconds for graceful app quit; then TERM only still-matching manifest identities, wait 10 seconds, KILL only identities that still revalidate, wait 5 seconds, and refuse/recover if any identity remains or changes.
   **Rationale:** Bounded exact-identity escalation prevents an indefinite drain without reintroducing pattern kills or PID-reuse risk.

7. **Q7 — Decision:** Watcher supervision loss is never a custody-safe “finish” license: terminate the exact chain/process group when identity is still provable; otherwise enter `recovery_required`, retain the lease, and require the narrow recovery path to prove all chain/telemetry processes stopped.
   **Rationale:** Continuing after loss of the component that owns cleanup would turn an operational failure into unobserved evidence custody.

8. **Q8 — Decision: LEAD-RULING.** Before the later capture, Ed must state the numeric watcher negligibility threshold (the required 95% upper bound in joules and/or its maximum fraction of the operative floor); the frozen design is one A/B/B/A round with two watcher-absent and two watcher-present matched captures, and any additional round must be declared before seeing results.
   **Rationale:** The task explicitly makes the threshold Ed-predeclared, so choosing its number in this packet would be outcome-sensitive authority invention.

9. **Q9 — Decision:** A watcher that does not clear the predeclared bound is redesigned and recharacterized; if a negligible blocking-wait implementation cannot be shown, abandon the resident-watcher production shape, with no energy subtraction or post-hoc correction.
   **Rationale:** This follows the adopted “instrument infrastructure, no subtraction” rule and keeps correction methodology out of the first round.

11. **Q11 — Decision:** In operative `mechanical_commit` mode, the arm banner commit **and push** must succeed before the final measurement HEAD is frozen; a local-only arm commit refuses the window, while a close push failure after custody is safe yields `closed_degraded` and cannot alter the scientific verdict.
   **Rationale:** Ed ruled that the remote README stay current during windows, but post-measurement publication failure is presentation degradation rather than evidence failure.

12. **Q12 — Decision:** Treat the rollout's modified README as historical: at implementation intake the exact baseline is clean, so first land and human-review a sentinel-delimited guard block in an ordinary commit, then bind its exact digest as the mechanical projector's starting baseline.
   **Rationale:** A reviewed sentinel and digest remove ownership ambiguity without trying to reconcile obsolete uncommitted bytes from the consult session.

14. **Q14 — Decision:** Make at most three relaunch attempts total (the initial attempt plus two retries), with 5-second then 15-second delays and a full readiness check after each; the third same canonical cause stops automation.
   **Rationale:** Three total occurrences match the standing same-cause escalation rule without letting wording changes reset the counter.

15. **Q15 — Decision:** Never treat D-004 capability as stable by history: immediately before runway, execute the established noninteractive powermetrics capability probe and refuse if `sudo -n /usr/bin/powermetrics -n 1 -i 100` fails or prompts.
   **Rationale:** The repository records D-004 as installed and previously verified, but per-window reproving is cheaper and safer than caching a machine fact.

16. **Q16 — Decision:** The first-round guard only reads and records network-time state; Ed performs any disable/enable through the existing `scripts/quiet_window_clock.sh` operator path before handoff or after recovery, and an unknown or wrong state refuses arm rather than widening runtime sudo authority for `systemsetup`.
   **Rationale:** D-004 authorizes only powermetrics and the adopted §5A substrate is evidence-only until `SEC5A-REMOTE-01`.

17. **Q17 — Decision:** Remote attestation may confirm that a previously photographed/labeled charger, cable, port, and adapter identity are unchanged, but it may not establish first-use identity; missing prior physical identity evidence requires hands.
   **Rationale:** Programmatic wattage proves negotiation, not which physical cable and port produced it.

18. **Q18 — Decision:** Accept only Ed's logged-in console session with every display asleep, screensaver disengaged, no interactive input, and `loginwindow` below the existing CPU limit; an awake unlock screen, loginwindow-only boot state, different console user, or ambiguous probe refuses.
   **Rationale:** This is the narrow state that composes with the existing HID/display probes and avoids silently expanding the characterized environment.

19. **Q19 — Decision:** After chain exit, verdict, backup, cleanup, and lease release, perform the close README commit/push **before** T3 relaunch; no repository or network activity is allowed from chain launch through backup completion.
   **Rationale:** Publishing while T3 is still down makes `closed_degraded` remotely visible, and release-before-publication avoids keeping a quiet lease for presentation work.

20. **Q20 — Decision:** `recovery_required` blocks every agent-launch route, but permits a root-owned, non-agent `quiet_guard recover` command that can only inspect identities, append guard-local recovery evidence, and abandon after Ed/lead acknowledgment and zero-process proof.
   **Rationale:** Recovery must be possible without launching the very agent class whose absence is unproven.

21. **Q21 — Decision:** Do not add an out-of-band service in round one; if T3 is down and README close push fails, the durable local `status.json`, close receipt, and `closed_degraded` marker are authoritative and the next plain local/SSH session must acknowledge them before other work.
   **Rationale:** Q13 already makes phone push optional later, and inventing a new notifier would expand both infrastructure and credential surface.

22. **Q22 — Decision:** Run and retain the app-death receipt on every quiet-window close, and also run a non-measurement compatibility exercise after every T3 version change before that version may be used for live promotion.
   **Rationale:** Per-close evidence catches state-specific failures; version-change exercises catch adapter drift before a window depends on it.

23. **Q23 — Decision:** Require proof that the prior thread's history/checkpoint is visible and that no turn or external side effect was duplicated, but never automatically reopen or resume that turn; exact thread selection remains an operator action.
   **Rationale:** Availability proves recoverability, while automatic resumption risks duplicating work after an app death.

24. **Q24 — Decision:** If network time cannot be restored after custody is complete, release the quiet lease, set `closed_degraded`, publish that state if possible, relaunch T3, and block the next measurement arm until Ed restores time and acknowledges the marker; ordinary agent recovery remains available.
   **Rationale:** A time-cleanup failure must prevent a clean close and another window, but retaining the lease would also prevent remote repair.

25. **Q25 — Decision:** Use exact baseline `e160c8972fa253ac5b6489a1532f275111565b4a` for this packet and implementation intake; every live request must independently bind the then-reviewed implementation HEAD and the post-arm-banner measurement HEAD.
   **Rationale:** The rollout's `50229b9…`/`ac8a681…` mismatch is historical and cannot override the lead-supplied exact current baseline.

## Commit decomposition

The series is **build now, arm later**. Every commit keeps `live_promotion=false`; `quiet_guard arm` must refuse with `t3_char_pair_verdict_missing` until the lead installs a passing `T3-CHAR-PAIR-01` verdict reference. Production use also requires Ed's Q3 perimeter confirmation and a passing watcher-negligibility result under Q8. Neither activation nor a quiet capture is part of these commits. The one-time setup installs a root-owned, fixed-command helper and root-owned credential capability; normal guard calls are `sudo -n` only, and the helper drops to the invoking uid/gid before any agent child executes.

### Commit 1 — Root-owned lease engine and inactive installation

Purpose: land the fail-closed state machine, durable identity/event formats, atomic lock/write rules, recovery rules, and an explicit inactive installation that cannot arm.

Exact file map:

- Package: `joulewise/quiet_guard.py` (schemas, transition table, canonical failure signatures, atomic replace + directory fsync, registry/lease validation, host/boot binding); `joulewise/quiet_guard_process.py` (PID/start-time/executable/argv/ancestry identity and independent census primitives).
- Scripts: `scripts/quiet_guard.py` (unprivileged CLI/client); `scripts/quiet_guard_privileged.py` (installed root-owned fixed-command helper; agent children are privilege-dropped); `scripts/setup_quiet_guard.sh` (the only interactive-sudo artifact; creates the root-owned state/install/credential directories, validates and installs the helper and narrow `sudoers.d` command aliases, and writes `live_promotion=false`).
- Tests: `tests/test_quiet_guard.py`; `tests/test_quiet_guard_process.py`.
- Contract/docs: `docs/contracts/quiet_guard.md`; `docs/decision_log.md` (one decision entry interpreting Q2's setup authority and pinning the privilege-drop/capability boundary).

Independent boundary: the CLI can initialize only through a fake install root in tests, exercise every transition and stale-recovery rule, and prove real `arm` remains disabled; it does not modify a launcher or run a chain.

### Commit 2 — Atomic launcher perimeter for every evidenced local route

Purpose: put the same `control.lock` check-spawn-register interval around process-launching routes and a logical registration interval around reused app/server turns; inactive installations preserve current behavior, while an unhealthy enabled installation fails closed.

Exact file map:

- Package: `joulewise/quiet_guard.py`; `joulewise/quiet_guard_process.py`.
- Scripts/config: `scripts/codex-run`; `scripts/codex-bridge`; `scripts/codex-app-bridge.mjs`; `scripts/claude-bridge-mcp.mjs`; `scripts/check-codex-mcp.mjs`; `.mcp.json`; `scripts/setup_quiet_guard.sh` (after Ed confirms each resolved target, preserves it in root-owned libexec and installs a guarded entrypoint shim at the PATH location for direct `claude`, `codex`/`codex exec`, and `codex-run-v3`, without editing the target's bytes).
- Route documentation: `CLAUDE.md`; `.claude/skills/codex/SKILL.md`; `.claude/agents/codex.md`; `.claude/commands/codex.md`.
- Tests: `tests/test_quiet_guard_launchers.py`; `tests/test_codex_bridge_observer.py`; `tests/test_codex_app_bridge.py`; `tests/test_claude_bridge_mcp.py`.

Independent boundary: fixture launchers prove exactly one winner in spawn-versus-arm races, no child/turn is created on refusal, registration survives until the child/logical turn ends, and every existing bridge test remains green; no T3 quit or measurement command exists yet.

Deployment note: `~/.local/bin/codex-run-v3` is personal tooling outside Git and is **not** edited by a commit. During the separately Ed-run installation, its reviewed bytes are preserved as a root-owned target and the existing entrypoint is replaced atomically by the guarded shim only after Ed confirms that mapping and backup. T3-native creation, URL/remote triggers, and any route Ed adds to the Q3 enumeration must have an evidenced hook or remain a live-promotion blocker; the independent census is a bypass detector, not a substitute for hook coverage during measurement.

### Commit 3 — Two-phase T3 handoff, detached watcher, chain adapter, §5A evidence, and characterization instrument

Purpose: build the full fake-chain operational path from immutable request through exact-family drain, `quiet_held`, runway, chain wait, cleanup, and release, while preserving the existing campaign semantics and emitting only guard-local receipts.

Exact file map:

- Package: `joulewise/quiet_guard.py`; `joulewise/quiet_guard_process.py`; `joulewise/quiet_guard_t3.py` (request validation, dynamic family manifest, quit/relaunch primitives, inventories, app-death receipt); `joulewise/quiet_guard_characterization.py` (A/B/B/A plan validation and offline statistics, never subtraction).
- Scripts/config: `scripts/quiet_guard.py`; `scripts/quiet_guard_privileged.py`; `scripts/quiet_guard_chain.sh` (exact `caffeinate -is /bin/zsh <plan-root>/window-chain.zsh <plan-root>` adapter with off-repository stdout/stderr); `scripts/characterize_quiet_guard_watcher.py`; `configs/characterization/quiet_guard_watcher_abba.json`; `scripts/prewindow_check.sh`; `scripts/quiet_mac_prep.sh`.
- Reused without semantic alteration: `joulewise/environment.py` public snapshot probes and the existing `scripts/quiet_window_clock.sh` operator path; if implementation discovers that reuse requires a code change, that is a prospective scope request rather than an implicit file addition.
- Tests: `tests/test_quiet_guard_t3.py`; `tests/test_quiet_guard_characterization.py`; `tests/test_environment.py`; `tests/test_quiet_guard.py`; fixtures under `tests/fixtures/quiet_guard/`.
- Contract/docs: `docs/contracts/quiet_guard.md`; `docs/phase_2/window_runbook.md`.

Independent boundary: a fake T3 family and fake chain demonstrate session-exit-before-lease, four inventories, unrelated-process preservation, exact invocation, no watcher polling/output/file/network calls while blocked in `waitpid`, cleanup ordering, §5A `complete_but_not_authorizing`, and disabled live promotion. This commit builds the characterization command but runs no `[QUIET-MAC]` capture.

### Commit 4 — Mechanical README projection, degraded close, and relaunch completion

Purpose: finish arm/close signaling under Ed's Q10/Q13 rulings, using a dedicated identity and root-confined credential capability, then close the app-death/retry behavior and operator documentation.

Exact file map:

- Package: `joulewise/quiet_guard_projection.py` (sentinel/digest renderer, clean-tree and HEAD checks, fixed-path diff validator, commit metadata, push result); `joulewise/quiet_guard_t3.py`; `joulewise/quiet_guard.py`.
- Scripts: `scripts/quiet_guard.py`; `scripts/quiet_guard_privileged.py`; `scripts/setup_quiet_guard.sh` (root-owned dedicated banner checkout and credential, neither readable nor writable by agents; the exposed operation can modify only the README sentinel block).
- Presentation/docs: `README.md` (reviewed sentinel block); `WINDOW_STATUS.md` (one-time clarification that guard-local state is authoritative and README is its transient projection); `docs/contracts/quiet_guard.md`; `docs/phase_2/window_runbook.md`; `docs/decision_log.md`.
- Tests: `tests/test_quiet_guard_projection.py`; `tests/test_quiet_guard_t3.py`; `tests/test_quiet_guard.py`.

Independent boundary: temporary local bare remotes prove banner-only commits, dedicated author identity, arm commit+push before HEAD freeze, refusal on dirty/drift/non-fast-forward cases, no Git/network call in the chain interval, lease release before close projection and T3 relaunch, bounded retries, and durable `closed_degraded` acknowledgment. The final repository head is still non-armable until the later gates are installed.

The lead then runs the required full gauntlet over the complete series: independent contract/security/process-identity audit; severity-tiered refuters for races, stale recovery, family precision, privilege dropping, Git capability confinement, and remote lockout; fixes; and a delta re-audit of every fix round. Final diff/head, real T3 app-death exercise, installation, credential provisioning, launch-perimeter confirmation, and all live/hardware gates remain lead/Ed-owned.

## Launch-perimeter enumeration DRAFT (Q3)

This is the confirmation checklist, not a claim of complete host coverage. “Evidenced” means a repository file, installed path/config, or retained local record shows the route. “Suspected” means the route is plausible or the sandbox could not inspect its live registry. Ed should add, remove, or classify each row before `live_promotion` can become true.

| Route | Classification and evidence | Required guard point / confirmation |
|---|---|---|
| Direct Claude Code CLI (`claude`) | **EVIDENCED.** `$HOME/.local/bin/claude` is a symlink to `$HOME/.local/share/claude/versions/2.1.222`; `$HOME/.claude/settings.json` configures the CLI; `scripts/claude-bridge-mcp.mjs` also spawns `CLAUDE_BIN`/`claude`. | Install a guarded PATH shim and wrap the reverse bridge spawn; Ed confirms there are no absolute-path aliases or alternate installations in use. |
| Claude Code deep link / URL handler | **EVIDENCED.** `$HOME/Applications/Claude Code URL Handler.app/Contents/Info.plist` registers `claude-cli:` under bundle `com.anthropic.claude-code-url-handler`. | Treat a deep link as a Claude launch route; confirm whether the handler invokes the guarded PATH command or an absolute vendor binary. |
| T3-native Claude sessions | **EVIDENCED.** `/Applications/T3 Code (Alpha).app/Contents/Info.plist` identifies `com.t3tools.t3code` v0.0.31; `RUN_STATE.md`'s T3 cutover records native threads and the shared server/helper/cloudflared family; local Claude transcripts record `entrypoint: sdk-ts`. | A T3 pre-turn hook is not evidenced. Ed must confirm an available hook or accept app-down enforcement plus a prohibition on reopening T3 while held; without one of those, live promotion stays blocked. |
| T3 app launch and `t3code:` / `t3code-dev:` URLs | **EVIDENCED.** Both schemes are registered in the same T3 `Info.plist`. | Guard or administratively fence every app/deep-link launch while a lease is held; confirm phone/remote actions that can invoke these schemes. |
| T3-native Codex threads | **EVIDENCED.** `RUN_STATE.md` records an Ed-run native T3 Codex thread; retained rollouts distinguish `session_meta.originator: t3code_desktop`; `docs/process_traces/2026-08-03-t3-doctrine-gate/` pins the evidence. | Same T3-native hook/fence as above; the process census must include native Codex server/helpers as observed identities. |
| Direct Codex CLI and `codex exec` | **EVIDENCED.** Current shell resolution is `/opt/homebrew/bin/codex`; `.mcp.json` invokes `codex mcp-server`; `scripts/codex-run` and installed `codex-run-v3` invoke `codex exec`. `$HOME/.local/bin/codex` is presently a stale symlink to the absent `/Applications/Codex.app` and must not be assumed authoritative. | Install the guarded PATH shim for `codex`; Ed confirms whether `/Applications/ChatGPT.app/Contents/Resources/codex` or any absolute Homebrew path is invoked directly. |
| Project Codex MCP (`codex`, `codex-reply`) | **EVIDENCED.** `.mcp.json` starts `codex mcp-server`; `CLAUDE.md`, `.claude/agents/codex.md`, `.claude/commands/codex.md`, and `.claude/skills/codex/SKILL.md` expose the route. | Change `.mcp.json` to start through the guard and keep one logical registration for the whole server-created turn. |
| Legacy `scripts/codex-run` | **EVIDENCED.** The script directly executes `codex exec`/`codex exec resume` and is named by the adopted spec. | Wrap its child creation with `agent-exec`; retain existing observer/watchdog behavior. |
| Audited `scripts/codex-bridge` CLI fallback | **EVIDENCED.** The script executes the configured Codex binary and can select standalone CLI with `CODEX_APP_BRIDGE=off`. | Wrap the CLI child from check through exit; do not touch `.codex-bridge/**` from guard runtime. |
| `scripts/codex-bridge` app-owned turn | **EVIDENCED.** With `.codex-bridge/app-host-thread-id`, it calls `scripts/codex-app-bridge.mjs`, which starts a turn over the Codex desktop IPC socket. | Register the logical turn before the IPC start request and unregister after completion/interrupt; refuse before sending a start request. |
| Installed `codex-run-v3` | **EVIDENCED.** `$HOME/.local/bin/codex-run-v3` is an installed Bash script whose `launch_fresh`/`launch_resume` functions invoke `codex exec`; `CLAUDE.md` and `.claude/skills/codex/SKILL.md` call it the current orchestration wrapper. | Do not mutate the personal script from Git; setup installs a guarded shim after Ed confirms command precedence and any alternate copies. |
| Codex/ChatGPT desktop native threads | **EVIDENCED.** `/Applications/ChatGPT.app` is bundle `com.openai.codex` v26.727.51351; `$HOME/.codex/config.toml` holds desktop settings and trusted JouleWise projects; its embedded Codex binary exists. | Confirm whether the desktop app exposes a pre-turn hook. If not, it must be quit/fenced like T3 for a held lease and its helpers included in census. |
| Codex → Claude reverse consult | **EVIDENCED.** `.codex/config.toml` starts `scripts/claude-bridge-mcp.mjs`, which spawns the Claude CLI. | Wrap the spawned Claude child even though a correctly registered parent Codex turn should already make arm refuse. |
| Claude subagents / Agent tool / custom `codex` agent | **EVIDENCED.** `.claude/agents/codex.md` and retained local Claude session metadata enumerate Claude and Codex agent types. | Treat every subprocess child as part of the parent's identity tree and require the parent registry row to remain until all descendants exit. |
| Claude desktop / remote-control session | **EVIDENCED AS A CAPABILITY.** `/Applications/Claude.app` is installed as `com.anthropic.claudefordesktop`; local JouleWise transcripts include desktop/SDK entrypoints. | Ed confirms whether this surface can start a local Claude Code turn or only attach to one; if it can start, identify its pre-turn hook or fence the app. |
| Claude scheduled cloud agents/routines and remote triggers | **SUSPECTED/CONFIG-EVIDENCED CAPABILITY.** `$HOME/.claude.json` contains schedule/remote-control feature state, and local session tool listings expose cron/routine and remote-trigger tools; no active routine was enumerated in this sandbox. | Ed lists active routines and whether any can target this host/repo; every local materialization route needs a lease check, otherwise disable it for live promotion. |
| macOS `launchd` jobs | **EVIDENCED ABSENT IN INSPECTED FILES.** The four user LaunchAgents, six system LaunchAgents, and four LaunchDaemons under the standard plist directories contain no `claude`, `codex`, `t3code`, or JouleWise launcher reference. | Ed confirms no dynamically loaded/nonstandard plist exists; add any discovered label and executable to the hook/census table. |
| User `cron` / `at` jobs | **SUSPECTED, NOT INSPECTABLE HERE.** Sandbox policy denied `crontab -l` and `atq`. | Ed runs `crontab -l` and `atq` (and checks any scheduler UI) and records none or enumerates each command before promotion. |
| IDE extensions (VS Code, Cursor, Windsurf, JetBrains, Zed) | **NOT EVIDENCED.** No matching IDE application or Claude/Codex/OpenAI/Anthropic extension was found in the standard application and extension directories. | Ed confirms no alternate IDE/profile/remote extension host is used; any found extension is a separate logical launch route. |
| Shell aliases/functions/alternate PATH entries | **PARTLY EVIDENCED.** `$HOME/.zshrc` only prepends `$HOME/.local/bin`; `$HOME/.zprofile` adds Homebrew; no Claude/Codex alias was found, but absolute invocation remains possible. | Ed confirms other shells, terminal profiles, scripts outside the repo, and direct absolute binary use; guarded shims are cooperative coverage, not kernel-level exec control. |
| Browser/computer-use helpers and MCP servers inside an agent | **EVIDENCED DESCENDANTS, NOT INDEPENDENT MODEL ROUTES.** `$HOME/.codex/config.toml` configures browser/computer-use helper paths and MCP servers. | Census them as descendants/automation infrastructure and require them gone before `quiet_held`; they do not need their own launcher hook if their parent agent is correctly registered. |

Ed confirmation must turn this draft into an exact allowlist of routes, hooks, binaries/bundle IDs, and “not present” assertions. The guard may claim host-wide enforcement only over that confirmed perimeter; any later install, T3/Codex/Claude version change, new IDE, scheduler, remote trigger, or alternate binary invalidates the perimeter until re-enumerated.

## Test plan

No test in this section is a substitute for lead final-diff review, the full gauntlet, or live machine gates. All fixture roots are temporary and guard-owned; tests assert that audit/state/manifest/log and run-bundle paths are never opened for writing.

### Commit 1 test surface

- `python3 -m unittest tests.test_quiet_guard tests.test_quiet_guard_process`: every legal/illegal transition; `handoff_pending` versus `quiet_held`; canonical cause signatures; schema/host/boot mismatch; malformed/truncated JSON; lock unavailable; atomic replace plus directory fsync; monotonic epoch; no TTL release; stale registry/PID reuse; exact-identity abandonment; `recovery_required` acknowledgment; inactive `live_promotion` refusal; root-helper privilege drop and command allowlist.
- `python3 -m unittest discover -s tests`: canonical regression gate after the focused tests.

What it proves: the durable engine is fail-closed and installable without arming or granting an agent root execution.

### Commit 2 test surface

- `python3 -m unittest tests.test_quiet_guard_launchers`: repeated spawn-versus-arm race with exactly one winner; held/pending/recovery state refusal before child creation; registration lifetime; abnormal child exit cleanup; inactive-install pass-through; enabled-but-unhealthy fail-closed; direct CLI shim argument fidelity; no write to bridge/run/state artifacts.
- `python3 -m unittest tests.test_codex_bridge_observer tests.test_codex_app_bridge tests.test_claude_bridge_mcp`: existing bridge behavior plus refusal before `codex`, IPC `thread-follower-start-turn`, or Claude spawn; app logical registration lasts through interrupt/completion; observer/manifest bytes remain owned by their existing writers.
- `node scripts/check-codex-mcp.mjs`: project MCP smoke through the guarded command path with a fixture/inactive state root.
- `python3 -m unittest discover -s tests`: canonical regression gate.

What it proves: every repo-controlled route in the draft participates in the atomic interlock and cannot create an agent child/logical turn after quiet promotion wins.

### Commit 3 test surface

- `python3 -m unittest tests.test_quiet_guard_t3 tests.test_quiet_guard tests.test_quiet_guard_process`: immutable request digest; session must exit before promotion; 120/30/10/5-second timeout branches under a fake clock; dynamic process-family capture; four inventories; PID reuse/ancestry changes; unrelated same-name helper untouched; unknown `cloudflared` refusal; exact TERM/KILL only; zero registry plus independent census; existing arm predicates; frozen HEAD/plan/runs roots; exact `caffeinate` argv; signal/exit receipt; cleanup and recovery.
- `python3 -m unittest tests.test_environment tests.test_quiet_guard_t3`: adapter wattage including 70 W versus required 140 W; AC/display/screensaver/HID/login state; daemon CPU; Time Machine; `sudo -n` powermetrics refusal; network-time unknown; `remote_5a_evidence_status=complete_but_not_authorizing`; no `systemsetup` mutation from the runtime.
- `python3 -m unittest tests.test_quiet_guard_characterization`: exact A/B/B/A order; matched metadata; watcher absent/present identity; production watcher in blocking-wait state; mean/difference/95% upper-bound calculations; missing Ed threshold refuses verdict; custody roots cannot overlap claim/baseline/calibration/NEG-8 roots; output contains no subtraction field or corrected energy.
- A syscall/injected-spy test in `tests.test_quiet_guard_t3` proves that, from chain launch until wait return, the watcher performs no periodic census, file write, network/GUI call, terminal output, or repository access; only the blocking wait and signal interruption path are reachable.
- `python3 -m unittest discover -s tests`: canonical regression gate.

What it proves: the fake-chain end-to-end path implements the two-phase handoff and builds the watcher characterization instrument while remaining non-authorizing and non-measuring.

### Commit 4 test surface

- `python3 -m unittest tests.test_quiet_guard_projection`: temporary worktree/bare-remote tests for sentinel-only edit; expected digest; dedicated `JouleWise Quiet Guard` identity; exact clean HEAD; arm commit and successful push before freeze; dirty tracked file/missing sentinel/banner drift/concurrent HEAD/non-fast-forward refusal; credential unreadable to the agent-side client; root capability rejects every path except the README sentinel; deferred mode remains deterministic but is not operative.
- `python3 -m unittest tests.test_quiet_guard_t3 tests.test_quiet_guard`: chain → verdict → backup → cleanup → lease release → close commit/push → relaunch ordering; absolutely no Git/network operation during the chain interval; success and three-attempt relaunch schedule; app missing, readiness timeout, wrong provider/mode/worktree/history/epoch, duplicated-turn/side-effect failures; `closed_degraded` never re-locks; persistent marker acknowledgment; network-time cleanup failure blocks the next arm, not agent recovery.
- `python3 -m unittest discover -s tests`: canonical regression gate.

What it proves: the presentation and relaunch tail cannot contaminate measurement, broaden Git mutation, hide degradation, or retain a safe-to-release lease.

### Separate later `[QUIET-MAC]` queue item — watcher negligibility characterization

**Not run by this packet or by any implementation agent session.** After Commit 3 is gauntlet-clean, Ed/lead creates a quiet, zero-agent session and predeclares Q8's numeric threshold before inspecting outcomes. Run one matched **A/B/B/A** round where A is the watcher absent and B is the exact production watcher blocked in `waitpid`; T3 stays down. Each capture records raw powermetrics, whole-system power/energy, watcher user/system CPU time, maximum RSS, context switches, and wakeups where available. Report the watcher-present minus watcher-absent estimate and its 95% upper bound against Ed's threshold. Custody is permanently NON-CLAIM and disjoint from claim runs, baselines, calibration, and NEG-8. Passing licenses the characterized watcher version/runtime/OS/hardware tuple; failure means redesign/recharacterize or abandon, never subtract. Repeat after material watcher code/interpreter behavior, OS, or hardware changes.

This later item is distinct from `T3-CHAR-PAIR-01`. The code series is built with `live_promotion=false`; app-adjacent operation remains prohibited until the lead consumes a passing `T3-CHAR-PAIR-01` verdict. Enabling production use requires **both** that verdict and the watcher-negligibility acceptance, plus Ed-confirmed launcher coverage and the real non-measurement T3 app-death exercise.

## Risks/assumptions register

Every item labeled ASSUMPTION is a packet choice rather than a new binding project ruling. If an assumption fails, implementation stops at the named consequence; it never silently weakens the lease, custody, or live-promotion gate.

| ID | Assumption | Consequence if wrong |
|---|---|---|
| A1 | **ASSUMPTION (Q2 interpretation):** Ed's interactive one-time setup ruling authorizes installation of a root-owned fixed-command helper and narrowly enumerated `sudoers.d` entries for that helper; it does not authorize arbitrary root commands, a general privileged daemon, or `systemsetup`. | Root-owned state that agents cannot tamper with cannot also satisfy atomic check-spawn-register; stop before Commit 1 installation and obtain a narrower mechanism ruling. |
| A2 | **ASSUMPTION:** The helper can safely spawn a requested agent only after dropping to the invoking uid, primary gid, supplementary groups, cwd, and sanitized environment while its root parent retains the lock/registry lifecycle. | `agent-exec` would be a privilege-escalation surface; replace it with a reviewed local IPC service or another Ed-approved primitive before launcher integration. |
| A3 | **ASSUMPTION (Q4):** The T3 family can be derived from the exact app/session ancestry on each request; no helper or `cloudflared` needs a name-only/shared-service exception. | Unknown survivors refuse every arm until T3 exposes stronger ownership metadata or Ed identifies a separately safe shared process rule. |
| A4 | **ASSUMPTION (Q5):** Apple Events quit by bundle ID and `/usr/bin/open -b com.t3tools.t3code` are stable for installed T3 v0.0.31, and readiness can be proved without a private thread-restoration API. | The adapter remains fixture-only; live app-death exercise must identify a version-pinned supported quit/relaunch/readiness interface. |
| A5 | **ASSUMPTION (Q6):** 120/30/10/5 seconds are sufficient on this Mac for session exit, graceful app quit, TERM drain, and final KILL drain. | Timeouts would create false refusals or excessive hangs; amend constants prospectively from non-measurement observations and re-audit timeout tests. |
| A6 | **ASSUMPTION (Q7):** Immediate exact-chain termination is safer than allowing a chain to finish after watcher loss, and fail-closed stale recovery is operationally acceptable. | A custody-safe finish requirement would need a separately supervised design; do not weaken `recovery_required` in place. |
| A7 | **ASSUMPTION (Q8 shape):** One A/B/B/A round is the minimum planned characterization and dual absolute/floor-relative reporting is acceptable; the numeric threshold remains **LEAD-RULING**. | The capture plan cannot freeze until Ed supplies the number or chooses a different prospective replication design. |
| A8 | **ASSUMPTION (Q11):** “Remote README stays current during windows” means an arm push failure blocks launch, even if a local commit exists. | If Ed accepts local-only arming, the refusal policy may be relaxed only by an explicit ruling before tests are frozen. |
| A9 | **ASSUMPTION (Q12):** Baseline `e160c897…` supersedes the consult session's modified README and its current top block may be replaced once by a reviewed sentinel block. | Any unrepresented README owner/content must be reconciled by the lead before enabling the projector; digest mismatch continues to refuse. |
| A10 | **ASSUMPTION (Q14):** “Three same cause” means three total attempts, not three retries after the first, and 5/15-second backoff is adequate. | Change attempt accounting prospectively; never permit a fourth same-cause occurrence under ambiguous wording. |
| A11 | **ASSUMPTION (Q15):** D-004's prior installation evidence is informative but not durable, so a fresh noninteractive probe is required for every arm. | If the probe itself materially perturbs runway, move it before the untouched interval rather than deleting it. |
| A12 | **ASSUMPTION (Q16/Q24):** Network-time mutation may remain an Ed/operator action in round one without defeating the remote substrate acceptance, because §5A evidence is explicitly non-authorizing. | Full remote operation stays blocked on `SEC5A-REMOTE-01`; do not grant `systemsetup` sudo authority implicitly. |
| A13 | **ASSUMPTION (Q17):** A prior physical photo/label plus unchanged-identity attestation is sufficient future input for SEC5A's charger/cable/port question. | SEC5A must keep physical hands for every window or obtain an Ed ruling on a different seal/identity method. |
| A14 | **ASSUMPTION (Q18):** Logged-in owner + displays asleep + screensaver disengaged is the already characterized console state; loginwindow-only and awake lock UI are not equivalent. | Add a separate characterization before admitting another console state; unknown remains refusal. |
| A15 | **ASSUMPTION (Q19):** Close README publication after lease release but before T3 relaunch is acceptable post-measurement activity and supplies the best degraded-state visibility. | Reorder only the presentation/relaunch tail; never move Git/network activity before backup completion or reacquire the lease for it. |
| A16 | **ASSUMPTION (Q20):** A non-agent root-owned recovery CLI is sufficient for stale recovery and may run while all agent launchers are blocked. | If remote human shell access is unavailable, Ed must name a pre-existing non-agent recovery plane before live promotion. |
| A17 | **ASSUMPTION (Q21):** Persistent local receipts plus next-session acknowledgment are acceptable when both T3 and README publication fail; no guaranteed phone signal is required in round one. | Add a separately authorized notifier later; do not smuggle credentials/network calls into the measurement interval. |
| A18 | **ASSUMPTION (Q22/Q23):** Per-close app-death receipts and version-change exercises are enough, and recoverability means visible history/checkpoint rather than automatic exact-thread resumption. | A stronger continuity requirement needs a T3-supported, version-pinned API and new duplicate-side-effect tests. |
| A19 | **ASSUMPTION (Q25):** The future implementation series begins from `e160c897…` or a lead-reviewed descendant with no conflicting quiet-guard/README changes. | Rebase and re-audit the file map and banner digest at the actual head; do not reuse this packet's baseline mechanically. |
| A20 | **ASSUMPTION (launch coverage):** The repo/config enumeration plus Ed's amendment can form a closed cooperative perimeter; PATH shims, app fences/hooks, and an independent census cover every confirmed route. | Host-wide enforcement is not achieved; keep `live_promotion=false` until the missing route has a refusal hook, or adopt a separately ruled OS-level enforcement mechanism. |
| A21 | **ASSUMPTION (Git capability):** A repo-scoped Git credential stored root-only can be effectively narrowed to the README sentinel by exposing it solely through a root-owned helper that verifies clean HEAD, expected digest, exact one-path/one-block diff, author identity, and fast-forward destination. | If provider-enforced path scope is required, GitHub's ordinary credential scopes are insufficient; Ed must supply a GitHub App/workflow/branch-protection design before `mechanical_commit` is enabled. |
| A22 | **ASSUMPTION (runtime write boundary):** A dedicated root-owned banner checkout outside every agent workspace lets the guard touch only its own `/Library/...` state plus the README sentinel and Git metadata, never scientific custody or project process artifacts. | Mechanical projection must remain disabled until a checkout/capability boundary can prove no other path is writable. |
| A23 | **ASSUMPTION (live gate composition):** A passing `T3-CHAR-PAIR-01` verdict, passing watcher characterization, Ed-confirmed launch perimeter, and real app-death exercise are conjunctive activation inputs, while fixture tests only build the instrument. | Any attempt to arm before all four inputs exist is a gate defect and must refuse; no fixture or mock receipt can substitute. |
