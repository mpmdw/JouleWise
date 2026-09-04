# Audit — the unattended night loop (D-127 / D-169), fresh read-only Fable seat

Bench: 2026-09-02 ~20:05 PDT, main `b81a2ac5`, read-only. Every fact marked
**[bench]** was executed this session; everything else is read from code or
rulings with a file:line cite. No repo file, worktree, custody file, or
launchctl state was written.

Files audited: `joulewise/night_gate.py`, `scripts/run_night.py`,
`scripts/launch_window.py`, `scripts/install_night_agent.sh`,
`configs/launchd/com.joulewise.night.plist.template`,
`docs/process/NIGHT_COURIER_PROMPT.md`, `docs/process/NIGHT_HANDBACK.md`,
`tests/test_run_night.py` (53 tests), `tests/test_night_gate.py` (43 tests),
`docs/decision_log.md` D-127/D-128/D-169,
`docs/process_traces/2026-09-01-unattended/{MAGISTRATE-RULING-UNATTENDED-STAGE1,coldgate-e10-fable,coldgate-d1-RULING}.md`,
`docs/process/state_kernel.json` rows NIGHT-REHEARSAL-01, UNATTENDED-LAUNCH-01,
T0-UNATTENDED-01, V5-* ladder, `docs/phase_2/window_runbook.md` E-10 (:1225-1262,
:1466-1500, :1724-1740), `SHAKEDOWN-G2-RUNSHEET.md` (:220-232, :524-532, :728-750),
the two installed plists, both custody roots under `/Users/edr/night-custody`.

---

## 1. Lifecycle of a night — what exists, where, and what does not

Legend: `[code]` implemented and tested; `[live]` proven by the 2026-09-02 02:56
launchd fire; `[GAP]` not implemented; `[RULING]` a decision, not code.

```
 DAY (agents present)
 ─────────────────────────────────────────────────────────────────────────────
 A. ARM   magistrate writes night_plan.json (t0, window_max_s, repo_head=HEAD,
          chain_path + .sha256 sidecar, custody_root, registration_path)
          + rewrites docs/process/NIGHT_HANDBACK.md, commits, pushes   [RULING R-9]
          chain bytes: scripts/gen_g2_phase_d.py --emit-chain (G2-a only)  [code :382]
          Ed is emailed the arming notice BEFORE arming (cold gate e10 (b))  [live 09-02]
       │
 B. INSTALL scripts/install_night_agent.sh --plan P --hour H --minute M   [code]
          checks plan.repo_head == HEAD, `command -v claude`, refuses --hour==7,
          refuses any existing write-once record; renders two plists from the
          template; launchctl bootstrap gui/501 both.                        [live]
          -> ~/Library/LaunchAgents/com.joulewise.night(.deadman).plist
             ProgramArguments: /usr/bin/env python3 run_night.py run|dead-man
             --plan P --courier-bin <resolved claude>; PATH = <claude dir>:/usr/bin:...
       │
 C. STAND-DOWN  "the magistrate ends the loop (ScheduleWakeup stop) and the
          session; Ed closes T3 Code and any interactive claude"          [RULING R-9]
          NO CODE does this.  Nothing kills agents; the gate only REFUSES.   [GAP by design]
       │
 ═══ 02:56 launchd fires com.joulewise.night (calendar, no KeepAlive) ═══
       │
 D. DRIVER PRE-GATE   scripts/run_night.py run_night()  :1032-1104
          write-once guard (_existing_record :904)  -> rerun refusal, exit 3
          resolve courier binary (:1055-1077)  -> night_courier_unavailable  [refuses BEFORE gate]
          overrun predicate t0+window_max_s+300 < 07:00 (:1079-1104)
       │
 E. GATE  joulewise/night_gate.py evaluate_night() :532-885, pure, injected probes
          ORDER (:90-100): window [t0,t0+max] -> plan age<=36h & repo_head==HEAD
          -> AGENT CENSUS /usr/bin/pgrep -lf "codex|claude|t3" (exit 1, empty)
          -> chain sha256 vs sidecar -> [TRANSACTION_PACK: night_refused_class_unbuilt :679-689]
          -> HID idleTime==0 -> AC power -> displaysleep present -> load1m<=2
          -> thermal 100 -> boot UUID + clocks -> D-166 registration hash (C1)
          receipt.json written O_EXCL (:1108).  REHEARSAL_STUB can never be GO (:482).
       │
 F. CAPTURE  _run_chain_once :392-480   Popen(["/bin/zsh", chain], start_new_session)
          census every 30 s; a hit -> killpg SIGTERM/SIGKILL -> night_aborted_agent_present
          REHEARSAL: command = "sleep 2; echo REHEARSAL", abort_on_census=False (:1158-1161, :1227)
          and the gate verdict is IGNORED (:1132 `and not rehearsal_effective`)
          NO runtime bound: the chain runs until it exits (window_max_s unused here) [bench] [GAP]
          The real G2-a chain (custody chain.zsh, 11.6 KB) calls
          validate_powermetrics_fiducial.py (:126) and run_campaign.py --arm-quiet-mode (:184-190)
          — never exercised by any rehearsal.
       │
 G. RECORD  result.json (:817-848) -> _durable_record: shallow clone of origin under
          custody_root/results-clone, branch night-results/<date>, push (:512-568)  [live]
       │
 H. COURIER RELAUNCH  run_courier :718-814   Popen([claude, "-p", PROMPT,
          "--output-format","text","--allowedTools", "Read,Glob,Grep,Bash,Edit,Write,
          mcp__claude_ai_Gmail__send_message"], cwd=REPO_ROOT, start_new_session)
          liveness: courier.heartbeat is the courier's FIRST act; driver waits <=300 s
          for courier.sent; 1 launch + 3 retries with 60/180/600 s backoff; courier.lock.
          On courier.sent the driver returns WITHOUT terminating the courier (:792-798)
          and unlinks the lock (:814): the courier lives on as an ORPHAN, unbounded,
          invisible to the dead-man.                                                  [live 09-02: ran >=6 min past driver exit]
          courier.json written; second results push; exit 0/3/4/5/6.
       │
 I. COURIER TURN (the "fresh headless session" of D-127 §1)   NIGHT_COURIER_PROMPT.md
          read NIGHT_HANDBACK.md, result.json, receipt/refusal; email Ed; write courier.sent;
          "Continue with the handback's next lane under the standing loop rules."
          It is ONE -p turn: no /loop, no ScheduleWakeup, no wake source after it ends.
          09-02's courier: harvested, committed to main, UNINSTALLED the agents,
          authored the next plan, emailed the arming notice, INSTALLED the next agents. [live]
       │
 ═══ 07:00 launchd fires com.joulewise.night.deadman ═══
 J. DEAD-MAN  dead_man() :1301-1406
          courier.sent exists -> skip (exit 0)  |  now < t0+max+300 -> "standing down" (exit 0) [live 09-02 07:00]
          fresh live courier.lock -> night_courier_running (exit 3)
          chain.started w/o chain.exited & pgid alive -> night_chain_alive, refusal.json, push, exit 3
          else census -> results push -> run the courier (4 attempts) -> push.
       │
 K. HARVEST / RE-ARM  handback "Next lane": magistrate harvests custody root,
          records under NIGHT-REHEARSAL-01, runs --uninstall AT THE ARMED COMMIT,
          then arms the next night.  Performed by whichever session is alive
          (09-02: the courier).  No mechanism guarantees a session exists.          [GAP]

 PACK-BOUND ONLY (stage 3 — none of this exists in the night path):
 L. generate_arm_readiness.py verify --pack-root  (runbook :1227-1234)          [not wired to night]
 M. E-10 launcher scripts/launch_window.py --pack-root --arm-receipt
    --launch-manifest --step6-confirmation-table --expected-confirmation-digest hC
    -> consumes the launch capability, execve's `/usr/bin/caffeinate -is /bin/zsh
    window-chain.zsh` (:264 region; runbook :1730-1734)                          [exists; Ed-invoked; no GO-receipt consumer]
 N. night gate class TRANSACTION_PACK: C1 = Ed's GO (V5-TRANSACTION-GO-01),
    C2 = arm verify PASS — no producer for either (night_gate.py :340-346, :435-437) [GAP]
```

### The stub rehearsal proves steps B, D, E(partially), F(stub), G, H, I, J(stand-down) and nothing else

It does NOT exercise: a GO verdict; the census-abort kill path on a real
chain; the chain-digest refusal in the driver (:1163-1196, bypassed by the stub
branch); the real chain's `sudo -n powermetrics`, `pmset displaysleepnow`,
network-time toggle, model loading; the dead-man's courier path (courier.sent
exists, so it skips); and anything pack-bound.

---

## 2. Who exits, who relaunches, and the unresolved design conflict

**Who exits before the gate.** Nobody in code. R-9 assigns it to the
magistrate ("ends the loop and the session") and to Ed ("close T3 Code and any
interactive `claude`"). The driver only *refuses* on a census hit
(`night_refused_agent_present`) or *aborts* a running chain
(`night_aborted_agent_present`); it never terminates an agent. **[bench]**
Right now the census returns 9 lines: the standing-loop session `claude`
pid 73550 (running since Aug 29 12:36, PPID 815), its two `codex mcp-server`
children, my own parent session + its codex pair, and three `/bin/zsh -c
source /Users/edr/.claude/shell-snapshots/...` background loops. Two of those
loops (8858, 27838; children of 73550) are sleep-until-01:30 / poll-until-03:20
monitors — the standing session intends to be ALIVE at 02:56.

**Who relaunches afterward.** The courier (`run_courier`, :718-814) is the
only relaunch: one `claude -p` with six allowed tools, liveness-proved by
`courier.heartbeat`, deadline 300 s to `courier.sent`, 4 attempts, plus the
07:00 dead-man re-running the same courier step. That satisfies D-127 §4
literally (preflight, launch, liveness proof, bounded retries, launchd
fallback). It does not satisfy D-127 §1 / D-128 §1 ("drives the full loop
across multi-day stretches"), because:

1. A `-p` session is one turn. When it ends there is no wake source: the only
   timers are the next night's calendar entry (which the courier itself must
   arm) and the 07:00 dead-man (which stands down once `courier.sent` exists).
   The loop is a **daisy chain of couriers**, each of which must harvest,
   uninstall, re-author, email and re-install before it ends — exactly what
   09-02's courier did **[bench: launchd.night.out, plist mtimes 03:02, plan
   authored 03:02:27]**. Nothing in a ruling says the courier owns arming;
   R-9 says the *magistrate* does, and rule 11 lists "window commitments" and
   "anything irreversible" as decisions the lieutenant may not take alone.
   The courier is a lieutenant-class actor with Bash+Edit+Write+push and no
   gate over it.
2. The courier is unbounded and untracked after `courier.sent`: the driver
   returns without killing it and unlinks `courier.lock` (:812-814), so the
   dead-man cannot see it, and any background job it leaves behind is a
   census hit for the NEXT night (the census matches the substring `claude`
   in `~/.claude/shell-snapshots/...` argv **[bench: pids 8858, 27838 match
   on path alone]**).
3. Meanwhile the interactive standing loop (73550) has no reason in code to
   exit, and on a real night its mere existence refuses the night. The stub
   class hides this: for `REHEARSAL_STUB` the driver ignores the gate verdict
   (:1132) and never aborts on census (:1227).

**Is the stub rehearsal exercising the courier/relaunch path?** Yes for the
courier email + `courier.sent` + one-turn continuation (proven 09-02). No for
the *relaunch of a magistrate that keeps driving*: there is no such thing yet.

**The design conflict, stated plainly.** "Agent fully exits during capture"
(D-127 §2) is satisfied by making the supervisor a Python process. The
conflict is between D-128 (continuous operation, `/loop`, "never idle") and
the fact that the only automated post-capture agent is a one-shot with no
wake source and no ruling on what it may decide. Today it is resolved by
(a) keeping an interactive session alive through stub nights (acceptable only
because stubs ignore the gate) and (b) letting the courier arm nights alone.
Neither survives a real night: (a) refuses it; (b) is a rule-11 violation
without a cold gate.

**Second conflict, live tonight:** R-6 pins `repo_head` to the dev tree HEAD
at arm time, while D-128/rule 7 keep main moving. Tonight's plan pins
`c6335a30`; main is `b81a2ac5`, 115 commits later **[bench]**. Running the
real gate with the clock pinned to t0+1 **[bench]**: verdict `REFUSED`,
reason `night_plan_stale`, and C3 (the census) is "not evaluated after
refusal" because `night_plan_stale` precedes `night_refused_agent_present` in
ORDER (:90-100). The handback's own acceptance rule says "any OTHER refusal
reason [than agent_present] is a finding: cure the cause before re-arming".
Tonight is therefore a finding by construction, and the same mechanism kills
any real night whose day saw a merge.

---

## 3. Failure modes

| Scenario | What happens (code) | Who is told | Bench |
|---|---|---|---|
| Courier never heartbeats / never writes `courier.sent` | 4 attempts × ≤300 s + 60/180/600 s backoff (≈35 min worst case, :745-805); process group SIGTERM/SIGKILL per attempt; `courier.json sent=false`; exit 6. Results branch already pushed. Dead-man 07:00 tries 4 more. | Nobody by email. Ed must notice the *absence* of email; the results branch is the floor. The loop is dead until a human starts a session. | code |
| Courier heartbeats, emails, then crashes before arming the next night | `courier.sent` exists → dead-man skips forever; no next plan; agents left installed fire 07:00 daily doing nothing. | Ed got the night's email, not "the loop stopped". | code |
| Dead-man fires mid-window | Guard :1314-1321 stands down while now < t0+max+300 (proven 09-02 07:00 **[bench: night.log]**). The run path refuses plans whose completion ≥ 07:00 (:1079-1104), so a mid-window 07:00 only happens if the chain OVERRUNS. Then: `night_chain_alive`, `refusal.json`, push, exit 3 — the chain is not killed. Day 2: `_write_driver_refusal` hits O_EXCL on the existing `refusal.json` → uncaught `FileExistsError`, traceback, exit 1 **[bench: scratch simulation, courier/push patched]**. | Results branch only (day 1); nothing on day 2. | bench |
| Plan/chain overruns `window_max_s` | No runtime bound in `_run_chain_once` (:436-480; `window_max_s` absent **[bench grep]**). Chain runs until it exits; the driver waits forever; census continues every 30 s. `night_window_expired` is a start-time check only (:551-571). | Silence. | bench |
| powermetrics needs sudo | `sudo -n -l` **[bench]**: `(root) NOPASSWD: /usr/bin/powermetrics` and the two `systemsetup -setusingnetworktime on/off` commands; `/etc/sudoers.d/joulewise-{powermetrics,network-time}` present. Under launchd there is no TTY, so a non-NOPASSWD sudo fails immediately rather than hanging (`sudo -n` in `quiet_mac_prep.sh:47`, `rail-probe.sh:107`; plain `sudo` in `quiet_window_clock.sh:97,164` — fine only because NOPASSWD). Not exercised by any rehearsal. | n/a — not a blocker | bench |
| Machine sleeps | `pmset -g` **[bench]**: `sleep 0`, `displaysleep 0`, `powernap 1` → never sleeps on AC. Gate refuses `ac_power` at start only (:713-727); AC loss mid-window is unmonitored. launchd replays a missed calendar job after wake; the window guard refuses it. | Refusal email if at gate; silence if mid-window (chain dies or finishes late). | bench |
| `codex mcp-server` child lingers | Census regex `codex` hits → real night refused/aborted, stub night records it. No cleanup anywhere; nobody but a human can kill it before the gate. **[bench]** two pairs alive now (children of 73550 since Aug 29; of 8908) — they exit on parent EOF normally. | Refusal email. | bench |
| Background zsh loops from Claude Code | Any `run_in_background` shell carries `~/.claude/shell-snapshots/` in argv and matches `claude` **[bench: 8858, 27838, 10151]**; the `t3` substring is likewise loose (R-3 keeps it "fail-closed"). A real night with any leftover monitor refuses. | Refusal email. | bench |
| Courier binary pruned by auto-update | Plist pins `versions/2.1.252` (still present **[bench]**); `claude` symlink moved to 2.1.259 at 19:51 today. If the updater prunes 2.1.252, `_resolve_courier_bin` falls back to `shutil.which("claude")` under the plist PATH `.../claude/versions:/usr/bin:...`, which contains no file named `claude` → `None` **[bench]** → `night_courier_unavailable` (:1059-1077) BEFORE the gate: a pruned binary costs the whole night, not just the email. | Results branch only. | bench |
| HEAD moves between arm and fire | `night_plan_stale` before the census (:599-609, ORDER :90). Tonight: certain **[bench]**. | Refusal email (stub still runs and emails). | bench |
| Stale plan, agents left installed | Dead-man fires 07:00 every day; after `courier.sent` it is a no-op; uninstall is manual (handback) and needs the ARMED commit checked out (installer :38-44) — a second HEAD-pin trap. | — | code |
| Sidecar/chain tampered after arm | Gate C5 refuses `night_chain_digest_mismatch` (:622-677); driver re-checks (:1163-1196). Tonight's sidecar matches **[bench shasum]**. | Refusal email. | bench |

---

## 4. Findings table

Severity: BLOCKER = would lose or corrupt a real night; SHOULD-FIX = wrong
outcome in a reachable case; NIT = hygiene/doc.

| # | Sev | Where | Scenario / defect | Verified |
|---|---|---|---|---|
| F1 | BLOCKER (tonight) | `night_gate.py:599-609`, ORDER `:90-100`; plan `repo_head` c6335a30 vs HEAD b81a2ac5 | Tonight's gate refuses `night_plan_stale`; the census is never evaluated; by the handback's rule this is "a finding: cure before re-arming". Root cause: R-6 pins the DEV tree HEAD while D-128 keeps it moving (115 commits in 17 h). The chain already runs from `/Users/edr/JouleWise-measurement-20260813` (3c96b18f) — the plan pins the wrong tree. | bench (gate simulated with clock at t0+1) |
| F2 | BLOCKER (real night) | `run_night.py:436-480` | No runtime bound on the chain; a hung chain = driver alive forever, dead-man refusing daily, no kill, no email. `window_max_s` is only a start-time predicate. | bench (grep) |
| F3 | BLOCKER (design) | `run_night.py:792-798, 812-814`; `NIGHT_COURIER_PROMPT.md` last line; R-9 | The relaunched agent is a one-shot courier that arms the next night alone (rule 11: window commitments, irreversible) with no gate, no bound, no lock after `courier.sent`, and no wake source if it dies. No mechanism restarts a driving magistrate. | bench (09-02 courier output + plist mtimes) |
| F4 | SHOULD-FIX | `run_night.py:1362-1371` (also `:1328-1336`) | Second dead-man firing over a still-alive chain (or courier lock) raises uncaught `FileExistsError` on the write-once `refusal.json`; exit 1 with traceback; nothing logged. | bench (scratch sim) |
| F5 | SHOULD-FIX | `night_gate.py:34` (`AGENT_CENSUS_ARGV`), R-3 | Substring census over full argv: every Claude Code background shell (`~/.claude/shell-snapshots/`) and any `t3` substring is a hit. Real nights will be refused by the magistrate's own leftover monitors, not by agents. Changing it needs a ruling because R-3 keeps it identical to `arm_readiness_evidence_t0.py:1312`. | bench (3 zsh loops match on path) |
| F6 | SHOULD-FIX | `install_night_agent.sh` PATH render (`courier_path="${courier_bin:h}:..."`), `run_night.py:571-596` | The rendered PATH is the *versions* directory, which holds no file named `claude`; the `which` fallback can never succeed under launchd, so a pruned pinned version refuses the night before the gate (`night_courier_unavailable`). Pin the symlink dir (`~/.local/bin`) or search the versions dir. | bench (`shutil.which` → None) |
| F7 | SHOULD-FIX | `run_night.py:1131-1132, 1227` | `REHEARSAL_STUB` ignores the gate verdict and never aborts on census, so a rehearsal cannot detect a mis-ordered or broken gate; tonight's stale refusal will still produce `REHEARSAL_ONLY`, chain exit 0, and a "success" email. | code |
| F8 | SHOULD-FIX | `run_night.py:1338-1371` | Dead-man refuses on a live chain but never terminates it; combined with F2 the only exit from a hung night is a human. | code |
| F9 | SHOULD-FIX | `NIGHT_HANDBACK.md` "Next lane"; `install_night_agent.sh:38-44` | Uninstall requires HEAD == armed commit; after a day of merges the uninstall itself fails and the dead-man fires forever (09-02 needed a manual `~/.local/bin` PATH fix already). | code + kernel note |
| F10 | NIT | kernel fence NIGHT-REHEARSAL-01 ("census is the driver's first act") vs `run_night.py:1055-1104` | The driver's first acts are courier resolution and the overrun predicate; the gate's first acts are window/stale. Doc/code drift. | code |
| F11 | NIT | plist `EnvironmentVariables.PATH` | Courier session lacks `/opt/homebrew/bin`, `~/.local/bin`: no `gh`, `jq`, `codex` inside the courier; `.mcp.json` codex server cannot start (harmless, noisy). | plist read |
| F12 | NIT | chain `G2A_ROOT=/Users/edr/JouleWise-shakedown-g2/g2-a-20260902` | The real G2-a chain's arm-time input assertions reference a root that does not exist yet; the desk producer must run before G2-a can be armed. | bench (`ls`) |

---

## 5. What blocks the first pack-bound automated night (`_v5` transaction, and even G2-b)

| # | Blocker | Imposed by | Kind |
|---|---|---|---|
| B1 | `TRANSACTION_PACK` is refused by class (`night_refused_class_unbuilt`) and its C1/C2 rows have no producer ("stage 3 not implemented") | `night_gate.py:679-689, :340-346, :435-437`; STAGE1 ruling R-4/R-10 §3 | code (magistrate → Sol) |
| B2 | No GO-receipt consumer and no night-path integration of the launcher: `launch_window.py` needs `--arm-receipt`, `--launch-manifest`, the step-6 table and `hC`, and `execve`s the chain; `run_night` runs a zsh file. Kernel row UNATTENDED-LAUNCH-01 is `blocked`, hard-dependent on T0-UNATTENDED-01 (`partial`, PR pending). | `launch_window.py` (arg parser, `launch()`), kernel rows | code |
| B3 | E-10 amendment ("Ed personally invokes the sole reviewed launcher exactly once") must be Ed-ratified before any launch that consumes a frozen pack — G2-b included | `window_runbook.md:1243-1244`; kernel fence UNATTENDED-LAUNCH-01; cold gate e10 | Ed decision (one sentence; email suffices, no hands) |
| B4 | `hC` custody route is an open policy question: the chain's `--lifecycle-event start` needs the step-6 table + `hC`; the only channel into an `execve`'d chain is the environment; the runbook forbids storing `hC` in any env file and keeps it operator-pasted per use | `window_runbook.md:1472-1495`; rehearsal-operator-card §E-10 | magistrate ruling (cold gate) + Ed holds `hC` (custody transcript) — remote-supplyable in principle |
| B5 | The `_v5` ladder itself: V5-G2A-PREFILL-PROBE-01 (queued; first live night; F12 inputs absent) → V5-DECODE-IDENTITY-SET-01 (partial, fix round 4 owed) → V5-DESK-DAY-01 → V5-G2B-SHAKEDOWN-01 (pack-bound → E-10 → stage 3 or attended) → L10-A → V5-LAUNCH-REALIZATION-RECHECK-01 + D-170 → V5-TRANSACTION-GO-01 → V5-TRANSACTION-01 | `state_kernel.json` rows (dumped at bench) | magistrate work; one Ed GO (`V5-TRANSACTION-GO-01`, `ed_external`) |
| B6 | Stage-1 plan email to Ed naming the first armed date, sent before any `DIAGNOSTIC_NO_PACK` arming; Ed's NO overrides | `NIGHT_HANDBACK.md` next lane; cold gate e10 (b); NIGHT-REHEARSAL-01 fence | magistrate action; Ed silence/NO by email |
| B7 | HEAD-pin vs live loop (F1): a real night needs either a frozen main from arm to fire or a plan that pins the measurement checkout | `night_gate.py:599-609`, R-6 | magistrate design decision (ruling; reinterprets R-6 → cold gate) |
| B8 | Zero-agent at fire: the standing session, its codex children and background loops must be gone; nothing in code does it; T3 Code closed | R-3/R-9; census F5 | magistrate behaviour + Ed behavioural (T3 Code; remote-closable only via ssh) |
| B9 | Runtime bound + dead-man idempotence (F2, F4, F8) before any multi-hour capture | `run_night.py` | code |
| B10 | The relaunch/baton contract (F3): who arms night N+1, under which gate, and what wakes a driving session if the courier dies | R-9, rule 11 | magistrate ruling (process rule → Ed sees it) |
| — | **Not a blocker:** sudo. NOPASSWD slices for `powermetrics` and the network-time toggle are installed **[bench]**. No physical action is required for G2-a beyond AC power and an absent interactive session. | `sudo -n -l` | — |

---

## 6. What I would change first (max 5)

1. **Pin the plan to the measurement checkout, not the dev tree.** Add
   `measurement_head` (HEAD of `/Users/edr/JouleWise-measurement-20260813`)
   and make R-6's stale check compare that; keep `repo_head` only for the
   installer/uninstaller, or drop the uninstall HEAD check. This is the one
   change that turns tonight from a finding into a pass and removes B7/F9.
   (Reinterprets R-6 → cold gate; small code.)
2. **Bound the capture.** In `_run_chain_once`, terminate the process group at
   `t0 + window_max_s` and record a registered driver code
   (`night_chain_overran`), and let the dead-man kill a proven-alive group
   after the completion epoch instead of only refusing. Make every dead-man
   write idempotent (dated `refusal-<epoch>.json` like `_write_rerun_refusal`).
3. **Make the courier a bounded baton with an explicit contract.** Keep the
   lock (or a `courier.pgid` record) until the courier exits; give it a
   total-life bound; write into the prompt exactly what it may do (email →
   harvest → uninstall → author next plan + handback → arming email →
   install → exit) and what it may not (merge, ratify, change cadence); and
   add a daytime `com.joulewise.magistrate` calendar entry that starts a fresh
   driving session only when `courier.sent` exists and the census is empty —
   D-127 §4's "independent launchd fallback" for the loop, not just the email.
4. **Tighten the census to process identity, not argv substring** (basename
   of argv[0] in {claude, codex, t3 code app names}), by ruling across both
   `night_gate.py:34` and `arm_readiness_evidence_t0.py:1312` so R-3's
   "production-identical" stays true; otherwise every leftover
   `run_in_background` shell refuses a real night.
5. **Fix courier resolution under launchd**: render PATH with `~/.local/bin`
   first and pin `--courier-bin` to the symlink (or fall back to the newest
   file in the versions dir), so an auto-update prune cannot refuse the night
   before the gate.

---

## Executed evidence (this session, read-only)

- `git rev-parse HEAD` → `b81a2ac5…`; `git log --oneline c6335a30..HEAD | wc -l` → 115; `c6335a30` is an ancestor of HEAD.
- `/usr/bin/pgrep -lf "codex|claude|t3"` → 9 lines (pids 8858, 8929, 8931, 10151, 27838, 73550, 73570, 73572, and my parent 8908's pair); `ps -o pid,ppid,lstart -p 8858,27838,73550` → both loops are children of `claude` 73550 (started Aug 29 12:36:15, PPID 815).
- `sudo -n -l` → `(root) NOPASSWD: /usr/bin/powermetrics`, `(root) NOPASSWD: /usr/sbin/systemsetup -setusingnetworktime off|on`; `/etc/sudoers.d/joulewise-network-time`, `joulewise-powermetrics` present.
- `pmset -g` → `sleep 0 (sleep prevented by caffeinate, powerd)`, `displaysleep 0`; `pgrep -lf caffeinate` → `9912 caffeinate -i -t 300`; `defaults -currentHost read com.apple.screensaver idleTime` → 0.
- `ls ~/.local/share/claude/versions/` → 2.1.248, 2.1.251, 2.1.252, 2.1.259; `~/.local/bin/claude -> versions/2.1.259` (19:51 today); plists pin `versions/2.1.252`; `PATH=<versions dir>:/usr/bin:/bin:/usr/sbin:/sbin python3 -c 'shutil.which("claude")'` → `None`; `/usr/bin/python3` = 3.9.6 and imports `scripts.run_night` cleanly.
- `launchctl list | grep joulewise` → `com.joulewise.night`, `com.joulewise.night.deadman` loaded (exit 0). Plists: night 02:56, deadman 07:00, `RunAtLoad false`, no `KeepAlive`.
- `/Users/edr/night-custody/rehearsal-20260903/`: plan (t0 1788429360 = 2026-09-03 02:56 PDT, window 900 s, authored 03:02:27 on 09-02, `repo_head c6335a30`), `chain.zsh` sha256 `35d273eb…` == sidecar, `night/` holds only the empty deadman `.out/.err`; `night.log`: one line, `2026-09-02T07:00:01 dead-man fired before the night's completion epoch 1788430560; standing down`.
- `/Users/edr/night-custody/rehearsal-20260902/`: `night.log` 02:56:00 started → gate REFUSED → 02:56:02 REHEARSAL_ONLY → 02:56:16 push → 02:57:25 courier heartbeat=True sent=True → 02:57:27 push; `courier.sent` message_id 1a0618d143537010; `result.json` census_count 1, one hit of 1136 lines (a zsh PR-watcher matching on the snapshot path, two `claude` sessions, two codex pairs, a codex-run-v3 seat with its whole brief in argv); `launchd.night.out` (mtime 03:03) is the courier's own narrative of uninstalling, re-authoring, emailing and re-installing the 09-03 night; pid 14906 gone.
- Gate simulation (real probes, `now_epoch_s` pinned to t0+1): `REFUSED night_plan_stale`, C3 `not evaluated after refusal`; dead-man epoch 2026-09-03 07:00; completion 03:16:00; `window_max_s` not referenced inside `_run_chain_once`.
- Dead-man double-fire simulation in the scratchpad (`_durable_record`, `run_courier`, `_resolve_courier_bin` patched; live `/bin/sleep` process group as the chain): firing 1 → exit 3 + `dead-man refused while chain was alive`; firing 2 → uncaught `FileExistsError: …/night/refusal.json`.
- `/Users/edr/JouleWise-measurement-20260813` exists (HEAD 3c96b18f); `/Users/edr/JouleWise-shakedown-g2` does not exist.
