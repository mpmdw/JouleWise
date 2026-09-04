# Opus contract-lens refutation — magistrate relaunch watchdog cold gate (2026-09-02)

Seat: Opus 5, contract-lens refuter under `docs/process/coldgate_charter.md` §5.
Charge: attempt to FALSIFY the magistrate's proposal (exhibit 10) and the
designs' load-bearing claims, on the frozen packet and the same atomic
questions. **I am not the judge.** I did not see, and do not know, the cold
Fable instance's ruling.

---

## 0. Contamination disclosure (charter §5, opened as instructed)

1. **Loop context.** I am a background subagent of a running JouleWise session.
   My context window carries the project `CLAUDE.md`, the private
   `CLAUDE.local.md` orchestration doctrine (rules 1–11), and the user
   auto-memory index — including entries titled *"Ed remote approval for
   windows"*, *"Unattended loop FIRST"*, and *"Seven-day paper mandate"*. I am
   therefore **not cold**. The charter's cold-judge protections do not apply to
   me; they apply to the paired Fable instance. My priors run toward *accepting*
   hands-free automation as pre-authorized, which is exactly the disposition
   that would make me soft on Q7. I held that suspicion explicitly there and
   argued against my own prior.
2. **Doctrine not used as authority.** No conclusion below rests on
   `CLAUDE.local.md`, session memory, `RUN_STATE.md`, council logs, run
   reports, or any scratchpad. Every load-bearing claim is cited to code,
   tracked docs, the packet's exhibits, or a command I executed this session
   and pasted in §9.
3. **Reading order (Q8's request).** I read the packet (unavoidable — the
   charter makes it the primary read), then brief 02, then designs 04, 03, 09,
   and only then exhibit 10. **Isolation was nonetheless impossible:** packet
   §2/§3/§4 restate exhibit 10's proposal (the fence predicate, the install
   handoff, the fork choices) before any design is read. I had the magistrate's
   answers before I had the seats' arguments. See finding H-8.
4. **A side effect I caused.** Executing Q2 as written started a background
   Claude session. Disclosed in full at finding H-1 and §9(E). I flag it at the
   top because it contaminated the machine state this gate is about.

**Checkout / digest verification, recorded before the merits (charter §9):**

| item | expected (supplied outside the packet) | observed | method |
|---|---|---|---|
| worktree HEAD | `e57bb43e` | `e57bb43ebf00c088968c03f97de8b4f93286af47` | `git rev-parse HEAD` |
| charter sha256 | `099de884…c95d81` | `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81` | `shasum -a 256` |
| packet sha256 | `af2b9818…180975` | `af2b9818403e135778c90c8797b960ffb6123269728136f58868df6704180975` | `shasum -a 256` |

All three match. Validator receipt (`coldgate-validator-receipt/v2`) → **PASS**,
`judge_handoff_bound: false`, all 7 exhibit digests observed == expected.
Full receipt in §9(A). I proceeded to the merits.

---

## Q1 — May the stand-down DEADLINE and FORCE move to a launchd supervisor?

### Verdict: **STANDS** — I could not show R-9 bars it. Two load-bearing sub-claims are FALSIFIED.

**R-9 verbatim** (exhibit 11a lines 159–168, byte-identical to
`docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
at `e57bb43e`, sha256 `9f0e6be1beec32b0eb525886181e3704bf3d57343ac046bf84c8ec4322228611`):

> **R-9 — the night protocol for the running /loop (this session).** On an
> armed night the magistrate: (1) writes `night_plan.json` into the night's
> custody root and `docs/process/NIGHT_HANDBACK.md` (what the courier reads
> first: the night's purpose, the result paths, the next lane); (2) commits
> and pushes; (3) **ends the loop** (`ScheduleWakeup stop`) and the session.
> The standing turn-end live-work rule (`turn-end-wake-source-rule`) is
> suspended on armed nights: the LaunchAgent is the wake source. Ed's only
> behavioural item: close T3 Code and any interactive `claude` before the
> armed hour. If he does not, the night REFUSES (R-3), records why, pushes the
> record, and the courier emails the refusal; nothing hangs.

**Why I could not bar it.** I looked for four bars and found none:

1. *No exclusivity.* R-9 assigns acts to the magistrate. It contains no
   "only", no "no other actor may", and no reservation of session termination.
   A duty to do X is not a prohibition on a second mechanism that also
   achieves X when the duty-holder fails.
2. *No deadline exists in R-9 to move.* R-9 names no time. The only temporal
   words are "before the armed hour", and they govern **Ed's** behavioural
   item, not the magistrate's. There is no ruled deadline for a supervisor to
   usurp; the deadline is created fresh by D-171 item 7, not relocated.
3. *R-9 already seats a machine actor as the standing wake source*: "the
   LaunchAgent is the wake source." Extending a LaunchAgent from waking to
   also bounding is a change of degree within a shape R-9 itself installs.
4. *Charter §9 is not triggered.* "A prior governed verdict … must not be
   converted into its opposite by reinterpretation." R-9's operative
   requirement is that the session be gone before the timer fires. The
   proposal keeps the magistrate's cooperative exit as the preferred path and
   adds a fallback for the case R-9 handles by refusal. That strengthens
   R-9's outcome; it does not invert it.

I record one genuine tension and reject it as insufficient: R-9's last sentence
rules the consequence of a live agent at t0 — "the night REFUSES (R-3), records
why, pushes the record … nothing hangs." The proposal replaces *refuse-and-report*
with *kill-then-refuse-if-the-kill-failed*. That is an addition ahead of the
ruled path, not a replacement of it; the refusal machinery is untouched
(`joulewise/night_gate.py:388-415`). It does not rise to a bar.

**Sub-claim 1, FALSIFIED — the force as specified cannot achieve its purpose.**
Exhibit 10 §1 rules: "Kill only a process group the watchdog itself recorded;
an unowned census hit is a hold, never a kill." At the bench I mapped the
process groups of every census-matching process on this machine (§9(F)). Of the
magistrate session's own Codex subtree, `codex-code-mode-host` **pid 4822 sits
in its own process group 4822**, although its parent 4480 is inside the
session's group 4453. The same pattern repeats in the interactive session's
tree (pid 2972, pgid 2972, parent 1560 in group 1536). So:

- `killpg(recorded_pgid, SIGKILL)` — the exact primitive all three designs and
  exhibit 10 specify — **does not reach `codex-code-mode-host`**;
- that process's argv matches `pgrep -lf "codex|claude|t3"` (§9(F));
- by exhibit 10's own rule it is *unowned*, so the watchdog may not kill it;
- therefore a textbook-perfect forced stand-down still leaves the census
  non-empty and the night refuses `night_refused_agent_present`.

The force is being taken out of R-9's cooperative hands on the ground that a
machine can be relied on where a session cannot. Bench-proven, the machine
cannot be relied on either — not as specified.

**Sub-claim 2, FALSIFIED — the deadline.** See Q4. R-9 does not bar a
supervisor owning *a* deadline; the runbook bars *this* deadline.

**Compound-question defect.** Q1 demands one YES/NO over two separable objects
whose answers differ (deadline: constrained by the runbook; force: unbarred but
mechanically insufficient). Charter §6 names compound questions as a hygiene
defect. Recorded at H-4.

**Severity: MATERIAL** (sub-claim 1 is BLOCKER-grade for the build, and
recurs at Q2/Q3/Q4 — it is the same defect seen from four sides).

---

## Q2 — `claude --bg` versus `claude -p` as the base

### Verdict: **FALSIFIED.** The build must use `-p`. `--bg` is structurally incompatible with the zero-agent fence.

Exhibit 10 §2 proposes `--bg` as the base, on this ground: *"this magistrate
session itself runs as a background job with `/loop` + `ScheduleWakeup`
working, and `claude agents/attach/logs/stop/respawn` exist (Fable bench)."*

**(a) What the help text does NOT promise.** `--bg`'s entire documentation is
one flag entry (`claude --help`, verified §9(C)):

> `--bg, --background` — Start the session in the background and return
> immediately. Prints the id that `claude attach`, `logs`, `stop` and `rm`
> take; `claude agents` lists them. With `--resume <session-id>`, continues
> that session in the background under the same ID, or starts a copy and says
> so when the session is already running

It promises: backgrounding, immediate return, an id, and `--resume` semantics.
It does **not** promise, and nothing else in the help promises:

1. that a `--bg` session starts from launchd with **no TTY and no controlling
   terminal** (the launchd case is the only case that matters here);
2. that the session **survives its first turn** or persists idle awaiting work;
3. that **`ScheduleWakeup` or `/loop` fire** in a background session — the
   packet's Spawn row asserts this and cites no evidence;
4. **any permission-prompt policy.** `--permission-prompts` is documented as
   "Who answers permission prompts **with `--print`**", and its `none` value —
   "nobody: anything that would prompt is denied automatically" — is the *only*
   documented guarantee that a headless session cannot block on a human. That
   guarantee is scoped to `--print`;
5. **any machine-readable output.** `--output-format`, `--include-partial-messages`,
   `--max-budget-usd`, `--fallback-model` and `--no-session-persistence` are all
   marked "only works with `--print`". A `--bg` supervisor is blind except for
   `claude logs`.

**(b) The existence proof cited in exhibit 10 is, at this moment, exhibiting the
failure mode.** `claude agents --json --all` at 21:13 (§9(E)) returns for the
background session that spawned this refuter:

```
{ "pid": 4453, "id": "3c46c831", "cwd": "/Users/edr/code/JouleWise",
  "kind": "background", "name": "Paper experiment loop",
  "status": "waiting", "waitingFor": "permission prompt", "state": "blocked" }
```

That is the packet's own `--bg` witness, **blocked waiting for a permission
prompt**, in an *attended* context where a human can clear it. Under launchd,
at 02:30, with Ed a thousand miles away, nobody clears it — and the flag's
documentation offers no way to forbid it. Exhibit 10 cites this session's
existence and omits its state (hygiene finding H-3).

**(c) DECISIVE — `--bg` creates census-matching processes the watchdog is
forbidden to kill.** `--bg` runs through a daemon, not a bare fork. Bench
(§9(F)):

```
 4375  1536  4375  /Users/edr/.local/bin/claude daemon run --origin transient …
 4394  4375  4394  …/ClaudeCode.app/Contents/MacOS/claude --bg-pty-host …/pty/3c46c831.sock …
 4384  4375  4384  claude bg-pty-host  …/spare/6a8837f0.pty.sock …
 4389  4384  4389  claude bg-spare     …/spare/6a8837f0.claim.sock
95679  4375 95679  claude bg-pty-host  …/spare/421d5d1d.pty.sock …
95703 95679 95679  claude bg-spare     …/spare/421d5d1d.claim.sock
 4453  4394  4453  …/versions/2.1.259 --session-id 3c46c831-… (THE SESSION)
```

Every one of those rows matches `pgrep -lf "codex|claude|t3"` — I confirmed 4
of them appear in a live production-predicate census (§9(D)); the daemon and
pty host are absent from *my* census only because they are my own ancestors
(the `pgrep` ancestor exemption that design 03 §0 B-1 established), and a
launchd-started driver has no such exemption, so it would see all of them.
None of `4375, 4394, 4384, 4389, 95679, 95703` shares pgid `4453`. The daemon
**pre-warms a replacement spare after each launch** (spare `421d5d1d`'s sockets
are dated 21:13, coincident with my probe, while spare `6a8837f0` from 20:49 is
still alive at 21:15 — 24 minutes idle).

Consequence, stated as a contract result: under exhibit 10 §1's own rule
("kill only a recorded process group; an unowned census hit is a hold, never a
kill"), a `--bg`-based magistrate **can never present an empty census at t0**.
Every night refuses `night_refused_agent_present`. `--bg` does not merely lack
proof; it is incompatible with the fence the whole mechanism exists to satisfy.

**(d) `-p` is the base, and it is the proven one.** The night courier is a
launchd-originated `claude -p` that ran end-to-end on 2026-09-02 —
`_courier_argv` at `scripts/run_night.py:610-631`, allowlist at `:52-54` — with
`--permission-prompts none`'s documented deny-on-prompt behaviour available.

**(e) The bench proof that must precede install.** The packet's proposed
observable ("a `--bg` session started from a launchd job with no TTY that
survives its first turn and honours a scheduled wakeup") is **inadequate even
for `--bg`**, because it does not test the census. Required instead, for the
`-p` base:

```sh
# 1. launchd-origin headless launch (no TTY, no controlling terminal),
#    from a throwaway LaunchAgent label, into a tmp custody home:
/Users/edr/.local/bin/claude -p "<prompt>" --model fable --effort high \
  --output-format stream-json --permission-mode dontAsk \
  --permission-prompts none --allowedTools "<list>" \
  --session-id <uuid>   # stdout/stderr to files; start_new_session=True
# Observable 1: a `result` event in the stream-json file, exit 0, and the
#               session's first scripted act (the heartbeat file) present.
# Observable 2: NOTHING blocks — the run terminates without human input.

# 2. THE OBSERVABLE THE PACKET OMITS — post-kill census:
kill -TERM -<child_pgid>; sleep 120; kill -KILL -<child_pgid>
/usr/bin/pgrep -lf "codex|claude|t3"; echo "exit=$?"
# PASS requires exit 1 and empty stdout, after a session that spawned at least
# one Codex child (so `codex-code-mode-host` is in play). Anything else is the
# blocker of Q1 sub-claim 1 and MUST be cured before install, not after.
```

**Severity: BLOCKER** on the `--bg` base; **BLOCKER** on the omitted post-kill
census observable.

---

## Q3 — Narrowing the census to the fence: consistent with R-3 and D-161?

### Verdict: **FALSIFIED.** Not barred by R-3's text; barred by D-161's own carve-out and by a concrete race.

**On R-3.** R-3's operative words (exhibit 11a:72-82) fix the *predicate* and
the *moment* for the driver: "the census is the driver's first act and uses the
production predicate … `/usr/bin/pgrep -lf "codex|claude|t3"` with exit status
exactly 1 and empty stdout." R-3 governs the driver. It does not, by its terms,
say when a *watchdog* must consult the census. So the narrowing is not barred by
R-3, and the packet's framing of R-3 as "production-identical" is about the
predicate, which the proposal keeps. I decline to manufacture a bar here.

**On D-161 — the narrowing misapplies it.** Exhibit 10 §2 justifies the
narrowing as "D-161 shape". D-161 prunes refusals *whose only adversary is the
trusted operator*, and expressly keeps fail-closed **"for physics/evidence/
pre-registration"**. The zero-agent census is not an operator-adversary
refusal; it is the physics fence itself — the whole definition of a
quiet-machine window (exhibit 11a §0: "no agent process (`codex`, `claude`,
`t3`) … The **zero-agent fence** … is unchanged by anything below"). Invoking
D-161 to prune the physics fence's own precondition inverts the decision it
cites.

**The race case (asked for, and found).** The dead-man path:

- Proposal §3 fences (a) a plan span "until `courier.sent` exists or 35 min
  after `chain.exited`", and (b) "local time is in the 07:00 minute".
- The dead-man exists precisely for the case where `courier.sent` is **absent**
  at 07:00 (`scripts/run_night.py:1301-1322`); it launches a courier, which is
  a `claude -p` agent, with a deadline of `COURIER_DEADLINE_S = 300` plus
  backoff `60/180/600` — up to ~35 minutes of courier activity beginning at
  07:00.
- For last night's plan, `chain.exited` was written hours earlier (on 09-02:
  chain done by 02:57), so "35 min after `chain.exited`" elapsed before 04:00.
  Fence (a) is therefore **closed** at 07:01. Fence (b) closes at 07:01.
- At the 07:01 poll: no owned child, no lock, no stop branch, backoff expired,
  and — under the narrowing — **no census check**, because no plan span is
  open. The watchdog LAUNCHES a magistrate session while the dead-man's
  courier is live.
- Two agents now race over the same custody records, and one of them is the
  night's **only reporting channel to Ed** (R-7, exhibit 11a:125-145): the
  courier is the process that writes `courier.sent` and sends the email. Sol's
  design (09) additionally has the relaunched magistrate perform
  `RECOVER_COURIER` — i.e. both processes may try to send the same handback.
- Under the unnarrowed rule this is impossible: the courier is a live `claude`
  process, the census is non-empty, the watchdog holds.

A second, quieter case: the narrowing removes the only check that would stop the
watchdog **adding** a session while residue from a previous magistrate is still
alive. Combined with Q1's bench-proven `codex-code-mode-host` escape, residue
accumulates across launches with nothing in the loop that ever inspects it until
the gate does, at t0, when it is too late to act.

**Also falsified: the stated reason for deferring Sol's interlock.** Exhibit 10
§2 defers the shared `run_night`/watchdog launch lock because "v1 never launches
inside a fence, so the race window is the poll interval outside any plan span."
The dead-man case above *is* outside any plan span, and it races. The premise
that justifies the deferral is the premise this question falsifies.

**The rule I would install instead.** Keep the brief's original constraint —
**the production census must be empty for every launch, without exception** —
and cure the false-positive problem the narrowing was invented for by narrowing
the **predicate**, not the **scope**:

1. Launch requires `agent_census(make_probes())` clean (exit 1, empty stdout),
   always. This is the brief's "so the design cannot race the gate", and it is
   one `pgrep` per 300 s.
2. To stop benign matches (ChatGPT.app's Codex Framework helpers, per design 03
   §0 B-2; leftover snapshot shells; the `bg-spare` rows I found) from blocking
   every daytime relaunch, add a **recorded, bounded allowlist** consulted only
   by the *watchdog*, never by the gate: each allowlisted match is written into
   `watchdog.log` with its full argv, and the allowlist matches on absolute
   executable path (`/Applications/ChatGPT.app/…`), not on substring. The gate's
   predicate is untouched, so R-3 is untouched and the driver still refuses.
3. Make the allowlist's cost visible: if the watchdog launches over an
   allowlisted match, the next session's email says which ones — so a night that
   later refuses on that process is traceable to a decision, not a mystery.

This gives D-161 what it actually asks (stop refusing on the trusted operator's
own GUI app) without removing a physics check at the one moment it is load-bearing.

**Severity: BLOCKER** (the dead-man race can cost the night's only report to Ed
while he is away).

---

## Q4 — Stand-down timings: request t0−20, SIGTERM t0−5, SIGKILL t0−4

### Verdict: **FALSIFIED.** 5 minutes is insufficient, on the run-book's own physics rationale. Minimum I would accept: **forced kill complete by t0−15, request at t0−45.**

**The settle numbers, found in code and run-book as asked.**

| where | text | value |
|---|---|---|
| `scripts/capture_t0_step.py:349-352` | `if assignments["SETTLE_S"] != "180": … "SETTLE_S must be the frozen 180-second literal"` | **180 s, frozen** |
| `scripts/quiet_window_clock.sh:32` | `SETTLE_S="${SETTLE_S:-180}"` | 180 s |
| `scripts/gen_g2_phase_d.py:259-260` | `"# Runbook §5C/§6 settle: operator activity ends before the pre slot."` then `settle` | 180 s, chain-owned |
| `docs/phase_2/window_runbook.md:143` | `| Stage settle | 180 seconds |` | 180 s |
| `docs/phase_2/window_runbook.md:1666-1668` | "Final settle is chain-owned (D-117 §5C): operator activity ends at launch, and §1's post-activity settle happens here, before the pre-calibration." | after t0 |

**The fact the packet omits, and it decides the question**
(`docs/phase_2/window_runbook.md:425-432`, verbatim):

> - [ ] Let idle-triggered background daemons run **before** the window, not
>   inside it. macOS starts idle-only work — XProtect's scheduled malware scan
>   is the documented instance — in roughly the first 10 minutes after the
>   machine goes quiet. Leave the machine untouched and idle for at least 10
>   minutes **before** the §5C step-2 calibration-ledger pair. The frozen
>   `prewindow_check.sh --wait` invocation fulfills this idle and must have
>   exited with `READY` before the ledger commands begin. **This is in addition
>   to the chain-owned 180-second stage settle, not satisfied by it.**

And at `:641-652`: "The required quiet waits remain §5's completed ≥10-minute
untouched idle **and** the chain-owned 180-second settle after the operator's
launch." At `:438`: "Close every agent and browser-automation session" is a
pre-window checklist item, i.e. before the idle, not four minutes before t0.

**Why exhibit 10's supporting fact is true but irrelevant.** §2's parenthetical
— "the chain's own quiet prep settles 180 s after t0" — is accurate as to the
chain, and inapplicable to this question for two independent reasons:

1. **It is on the wrong side of the census.** The gate's census moment is t0.
   `evaluate_night` runs at driver fire time; the missed-fire guard requires
   `plan.t0_epoch_s <= now <= plan.t0_epoch_s + plan.window_max_s`
   (`joulewise/night_gate.py:551-571`), and the driver is a
   `StartCalendarInterval` job set to the t0 minute. `agent_census` is called at
   `joulewise/night_gate.py:611`. The chain's 180 s settle begins only after the
   gate has already passed and `chain.started` is claimed
   (`scripts/run_night.py:1198-1228`). **The settle cannot launder anything the
   census has already seen.** With SIGKILL at t0−4 and the census at t0, the
   design leaves ~4 minutes, then measures.
2. **The run-book expressly says it does not count.** "in addition to the
   chain-owned 180-second stage settle, **not satisfied by it**". The magistrate's
   §2 cell uses the 180 s settle for exactly the purpose the run-book forbids.

**The physical claim, stated plainly.** The run-book's reason for ≥10 minutes is
not ceremony: macOS starts idle-only work in roughly the first 10 minutes after
the machine goes quiet, and that work lands *inside* the measured window if the
machine went quiet less than 10 minutes before t0. A forced SIGKILL of a Claude
session at t0−4 is the opposite of a quiet machine: it triggers process teardown,
MCP-server exits, filesystem flushes, and — per Q1's bench evidence — leaves
escaped Codex hosts running. Four minutes is under half the run-book's floor,
and the activity at t0−4 is a burst, not a taper.

**On the number's provenance.** D-171 item 7 reads "Stand-down margin = 5
minutes before a window's t0 (30 was 'too much')". Exhibit 11b is byte-identical
to `docs/decision_log.md` lines 10586-10630 (verified, §9(H)), so the *entry* is
authority. But Ed's verbatim words, quoted in that same entry, are only: **"30
min before a window seems too much"**. Ed did not say five. "5" is the drafter's
interpolation of an upper-bound complaint into a point value, and the packet
presents it in §4's fork table as though it were Ed's ("Ed: '30 min seems too
much'"). Ed was not told, and could not have weighed, the run-book's 10-minute
idle rule — a measurement-validity constraint that D-161 expressly keeps
fail-closed ("physics/evidence/pre-registration").

**Three model families independently converged on the opposite answer**, and
exhibit 10 overrode all three: Opus 03 §8.4 request t0−45 / force t0−30; blind
Fable 04 cooperative t0−40 / TERM t0−30; Sol 09 drain t0−40 / TERM boundary−5 =
t0−35 / KILL t0−34. A 3/3 cross-family convergence overridden on a number no
seat proposed and Ed never uttered deserves its own line in the record.

**Minimum I would accept, and why each term:**

| term | value | reason |
|---|---|---|
| forced SIGKILL complete by | **t0 − 15 min** | ≥10 min verified quiet before t0 (run-book :425-432) + margin for the post-kill census and residue handling |
| SIGTERM at | **t0 − 17 min** | 120 s TERM→KILL grace, the grace all three designs specify |
| post-kill census verification | **mandatory, before t0 − 10** | the step exhibit 10 §3 omits; on residue, queue a notice and stop launching (design 03's `DEGRADED`) |
| cooperative request at | **t0 − 45 min** | a session must commit, push, email, and stop Codex children; design 03 §8.4's reasoning that a real capture is hours and work may be unpushed |

If Ed's 5 minutes must be honoured as ratified text, the minimum cure is a
one-line email telling him the run-book requires ≥10 minutes of untouched idle
and proposing t0−15/t0−45 — which still beats the 30 he called too much, and
therefore does not need a reply to be safe under his own stated preference.

**Severity: BLOCKER.** A window measured 4 minutes after a SIGKILL is not a
quiet-machine window, and its data would be claim-bearing.

---

## Q5 — Kill switch: branch probed by `git ls-remote --exit-code`

### Verdict: **STANDS** on the branch-versus-file choice. **Two MATERIAL defects in the probe as designed.**

**Probe executed (packet-directed), exit code pasted:**

```
$ git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/ops/stop-magistrate
EXIT=2                          # no output; branch absent
$ git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/main
e57bb43ebf00c088968c03f97de8b4f93286af47	refs/heads/main
EXIT=0
```

**The branch beats the file, and design 09's `MAGISTRATE_STOP`-on-`main` is the
one option that must not be adopted:** a root file on `main` moves the branch
head, and the gate refuses `night_plan_stale` when the canonical checkout's HEAD
differs from the plan's `repo_head` (`joulewise/night_gate.py:599-609`). Ed
pressing his own stop switch would stale the armed plan. Exhibit 10's reasoning
here is correct and I could not falsify it.

**Authentication: none needed today, and that is a fact with an expiry.**
Truly anonymous probe (credential helper disabled, terminal prompts off):

```
$ GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote --exit-code \
      https://github.com/mpmdw/JouleWise.git refs/heads/main
e57bb43e…	refs/heads/main          rc=0        # repo is public
```

**Rate: immaterial.** One unauthenticated `ls-remote` per 300 s = 288/day.

**Defect 1 (MATERIAL) — rc 128 conflates "network blip" with "switch is dead
forever", and the designs fail open on both.** Exit-code matrix, all four
executed (§9(G)):

| case | rc | stderr |
|---|---|---|
| ref exists | 0 | — |
| ref absent | 2 | (empty) |
| host unresolvable | **128** | `Could not resolve host` |
| repo private / renamed / auth revoked | **128** | `could not read Username for 'https://github.com'` |

Designs 03/04/09 all treat a failed probe as "unknown → not stopped" (fail
open), citing D-161. For a transient blip that is right. But rows 3 and 4 are
**indistinguishable**, and row 4 is permanent: if the repo's visibility changes,
or the URL is renamed, Ed's only remote control over an unattended week silently
stops working, and **nothing tells him**. He would push a stop branch and watch
nothing happen.

*Cure, cheap and bench-verified:* probe a **positive control** in the same poll —
`refs/heads/main`, which must exist. Control rc=0 ⇒ transport healthy ⇒ rc=2 on
the stop ref is a trustworthy "not stopped". Control rc=128 ⇒ the switch is
blind; count consecutive blind polls, and after N (I would use 6 = 30 min) stop
launching and put the fact in the next session's first email. This fails closed
on the *control*, not on the switch, so a blip costs nothing and a permanent
break cannot hide.

**Defect 2 (MATERIAL) — a typo in the branch name is silent and reads as
"not stopped".** `ops/stop-magistrate` is 20 characters typed on a phone. If Ed
creates `ops/stop_magistrate`, `stop-magistrate`, or `ops/stop-magistrate ` with
a trailing space, the exact-ref probe returns rc=2 — indistinguishable from "Ed
never pressed the switch" — while Ed believes the loop is stopped.

*Cure, bench-verified:* probe the **glob** with `--exit-code` and treat any match
as STOP. Semantics confirmed: `git ls-remote --exit-code <url> 'refs/heads/ops/*'`
→ rc=2 when empty, rc=0 with matches (§9(G)). Widen to two patterns
(`refs/heads/ops/*` and `refs/heads/*stop*`) and the whole class of near-misses
lands on STOP. Also **keep design 04's local `~/night-custody/magistrate/STOP`
file** as the second half — exhibit 10's fork table silently drops it, and it is
the only path that works when GitHub is unreachable.

**Two NITs.**
- *D/F namespace:* `refs/heads/ops` does not exist (`--exit-code` → rc=2), so
  `ops/stop-magistrate` is creatable today; creating it permanently blocks a
  future branch literally named `ops`. Design 04's flat `magistrate-stop` avoids
  the class. Not decisive.
- *Branch hygiene:* the remote carries 294 branches (`ls-remote --heads`,
  rc=0). Any bulk branch-pruning would delete the switch. Name it in the
  install email as a branch that must never be pruned.

**One structural limit to disclose to Ed, not to fix.** The switch is enforced
only by the watchdog polling it. A wedged watchdog cannot be stopped by it, and
there is deliberately no watchdog-for-the-watchdog (design 03 §8.7, D-161). That
is the right call, but the install notice must say in plain words what the stop
switch can and cannot do, so Ed's expectation matches the mechanism. Exhibit 10
§4 does not specify the notice's content at all.

---

## Q6 — Canonical cwd, and must the plan-pin change land BEFORE install?

### Verdict: **FALSIFIED.** "May follow" is not available. The plan-pin change must land **before** install — for the first real window, and for the rehearsal too.

**Bench state, right now (§9(I)):**

```
$ git -C /Users/edr/code/JouleWise rev-parse HEAD
33290b8bbe82b126037101edf8f15cdf96c920da
$ git -C /Users/edr/code/JouleWise status --porcelain=v2 --branch
# branch.oid 33290b8bbe82b126037101edf8f15cdf96c920da
# branch.head main
# branch.upstream origin/main
# branch.ab +0 -6                       ← SIX commits behind origin/main
$ plan rehearsal-20260903: repo_head = 33290b8b…, t0 = 2026-09-03 02:56,
                           authored = 2026-09-02 20:16:43, class REHEARSAL_STUB
```

The armed plan is valid **only because nobody has run `git pull` in the
canonical checkout since 20:16.** Six commits already sit on `origin/main` ahead
of it, and the sixth is `e57bb43e` — *the commit that landed this cold-gate
packet*. The magistrate's own working pattern, landing custody commits on main,
is the mechanism that stales the plan, and it has produced six of them in the
five hours since the last re-arm.

**This is the same signature, twice, going on three times.** The message of
33290b8b — the commit the plan is pinned to — records occurrence #1 in its own
words:

> `NIGHT_HANDBACK: rehearsal-20260903 RE-ARM (fresh audit: daytime pulls moved
> canonical HEAD past the pinned repo_head — gate would refuse night_plan_stale;
> plan re-pinned to this commit, plists re-rendered, courier pin refreshed)`

The six queued commits are occurrence #2, pending the next pull. The proposal's
cure for occurrence #3 is **a sentence in a prompt** ("a prompt-level ban on git
operations there while a plan is armed"). Charter §9: "Two consecutive rounds
failing with the same signature is a structural problem: the next spend is a
consult or redesign, not round three. If the packet shows this pattern,
licensing another same-shape round requires explicit justification." The packet
offers none — §2's cwd cell asserts the cure without acknowledging that the
previous instance of the same cure already failed today.

**The self-contradiction that closes the question.** Installing the watchdog
*requires* moving the canonical HEAD:

1. The plist's `ProgramArguments` must name a real file — design 04's template
   renders `@@REPO@@/scripts/magistrate_watchdog.py`, and exhibit 10 §2 puts the
   session's cwd at the canonical checkout.
2. For that path to exist, the canonical checkout must be on a commit that
   contains `scripts/magistrate_watchdog.py` — i.e. it must pull/merge.
3. Pulling moves HEAD off `33290b8b` ⇒ `checkout_head != plan.repo_head` ⇒
   `night_plan_stale` (`joulewise/night_gate.py:599-609`).
4. And `scripts/install_night_agent.sh:40-45` then refuses re-installation with
   exit 3 until the plan is re-armed: `[[ "$plan_head" == "$actual_head" ]] || {
   print "plan repo_head does not match checkout HEAD" >&2; exit 3; }`.

So exhibit 10 §4's sequence — install tonight, while a plan is armed, with "the
prompt's hard rule meanwhile" as the cure — **cannot be executed**, because the
prompt rule cannot govern the install itself. The install forces a third re-arm
tonight, at the hour before a rehearsal, by hand.

**Rehearsal-stub case — worse than it looks, and this is the part I would put
in front of the magistrate first.** The order of checks inside the gate is
decisive: `night_plan_stale` returns at `joulewise/night_gate.py:594-609`, and
`agent_census` is only reached at `:611`. **A stale plan short-circuits before
the census is ever taken.** So if the plan stales, tonight's rehearsal produces
**no census record at all** — and the empty 02:56 census (the first-ever C3
pass) is precisely the observable the rehearsal exists to produce (design 04
§6). A stale rehearsal is not a degraded rehearsal; it is a null one, and the
stand-down mechanism goes untested into a week of real windows.

*Answer for the rehearsal-stub case:* the pin change must land first, or the
plan must be re-armed after the install by a mechanism that is not a prompt —
and the re-arm must be the last write to the canonical checkout before 02:56.

**First real window case:** the pin change must land first, unconditionally. A
`REHEARSAL_STUB` can never carry `verdict: GO` (R-4, exhibit 11a:96-118), so a
stale rehearsal costs evidence; a stale *real* window costs the window, which is
the entire object of D-171.

**On the cwd choice itself — the magistrate's ground is true but not decisive.**
Bench: `CLAUDE.local.md` is untracked (`git ls-files --error-unmatch` → "did not
match any file(s) known to git") and exists only at
`/Users/edr/code/JouleWise/CLAUDE.local.md`; it is absent from this linked
worktree. So "a worktree loses the private doctrine" is **correct**, and I record
that in the magistrate's favour. It is not decisive, because the file is an
ordinary untracked file that can be copied or symlinked into a worktree, and
`--add-dir <directories...>` exists (`claude --help`, §9(C)) to grant tool access
to the canonical path from a worktree cwd. The fork table gives design 03's
worktree option two words and no rationale while giving the canonical choice a
full argument — hygiene finding H-6.

**If canonical cwd is kept, the prompt ban must be enumerated, not gestured at.**
"A ban on git operations" is over-broad and therefore fragile: `git fetch`,
`git log`, `git status`, `git show` do **not** move HEAD, and the session
*needs* them — design 04 §8.4 bench-established that `RUN_STATE.md`'s durable
pause pointer names a file that does not exist on main and lives only on an
unmerged branch, so a fetch is mandatory to resume at all. A ban the session
must break to do its job is a ban it will reinterpret. Enumerate the forbidden
set instead: `pull`, `merge`, `rebase`, `checkout`, `switch`, `reset`, `commit`,
`cherry-pick`, `stash pop` — in the canonical checkout, while a plan is armed.

**Severity: BLOCKER** on the ordering; **MATERIAL** on the ban's wording.

---

## Q7 — Does D-171 authorize install without waiting for a reply?

### Verdict: **The reading STANDS on the words. The §4 disposition is FALSIFIED — the conditions D-171 attaches are not met by the proposal.**

I tried hardest here, because my contaminated priors (§0) push toward "yes,
install". I could not falsify the no-reply reading. I could falsify the
inference the magistrate draws from it.

**The words, quoted** (exhibit 11b, byte-identical to `docs/decision_log.md`
lines 10586-10630 at `e57bb43e` — verified, §9(H)):

> 4. **Relaunch watchdog install AUTHORIZED** (user-level launchd, no sudo)
>    once it passes the gauntlet and a cold gate; it emails Ed at each launch
>    and stand-down and honours a stop file.

> 7. **Stand-down margin = 5 minutes before a window's t0** (30 was "too
>    much"); email at stand-down and at relaunch; **Ed reads, does not reply.**

And Ed's own words in the same entry:

> "2. i dont want to have to emial you anything back. im sure its fine, go
> ahead. 3. yes if i reply by email you can consider it a permission but the
> goal here is to not need me at all to run the expirement window - 4. yes,
> authorized."

**Why the no-reply reading survives.** Item 4's condition precedent is
"passes the gauntlet and a cold gate" — a reply is not among the conditions.
Item 7 says "Ed reads, does not reply." Item 3 makes a reply *sufficient* as
permission ("still counts as permission whenever one arrives"), which in the
ordinary reading of a permissive clause implies it is **not necessary**. Ed's
"i dont want to have to emial you anything back … go ahead" is as direct as
language gets. Reading item 4 to require a reply would make item 7's "does not
reply" and Ed's "not need me at all" inoperative. **The magistrate's reading of
"no reply needed" is correct.**

**What is falsified: the object authorized is not the object proposed.** Item 4
authorizes a specific artifact, described by three conjoined properties. Two are
not satisfied and one is silently redefined:

1. **"once it passes the gauntlet and a cold gate."** The gauntlet is a sequence
   over an *implementation*. No implementation exists — design 09's own
   verification status records "no proposed plist, script, prompt, state
   machine, or remote stop path exists until implementation and cold-gate
   approval." This gate adjudicates a **design**. The packet concedes the point
   itself: Q2 requires that a "bench proof must precede install." So install
   cannot follow *this* gate; item 4's own condition demands a further pass over
   the built artifact. Exhibit 10 §4's "after the gauntlet and this gate … this
   session … installs" elides the gap between a design gate and a build gate.
2. **"it emails Ed at each launch and stand-down."** Exhibit 10 §1 concedes the
   opposite: "Forced stand-downs and usage-exhaustion states are queued as
   `notice_pending` and reported by the next session's first email." That is
   defensible when a forced stand-down is the rare path. Under exhibit 10's own
   t0−5 SIGTERM / t0−4 SIGKILL timing it becomes the **ordinary** path — five
   minutes is not enough to commit, push, email, and stop Codex children, which
   is why every design seat put the cooperative window at 40–45 minutes. The
   proposal therefore delivers a watchdog that, in the normal case, does **not**
   email Ed at stand-down: not the artifact item 4 authorizes. Cure: adopt Q4's
   timings so the cooperative email is the normal path (my preference), or
   provision a non-Claude notification route (design 09 §8 item 2 — "Ed must
   separately authorize and provision a non-Claude mail/webhook credential"),
   or go back to Ed for the amendment.
3. **"honours a stop file."** D-171 says *file*. The proposal substitutes a
   *branch* and drops the local file entirely (design 04 carried both). The
   substitution is well-reasoned (a file on `main` moves HEAD — Q5), and I do
   not treat it as a bar; but the magistrate should not silently redefine a term
   in the text that authorizes it. Cure: implement both, and the authorizing
   text is satisfied literally.

**A context defect I must record even though fidelity checks out.** D-171 quotes
Ed's numbered answers 1–6 but **not the magistrate's checklist questions** they
answer. The mapping from "4. yes, authorized" to item 4, and the derivation of
item 7's "5 minutes" from "30 min before a window seems too much", cannot be
verified from the packet. The decision entry is ratified authority, so this does
not defeat item 4; but it means Q4's number rests on a drafter's interpolation
that no reader of the packet can check. Hygiene finding H-5.

**Severity: BLOCKER** on installing after this gate (condition 1);
**BLOCKER** on the stand-down email property (condition 2, and it is the same
defect as Q4); **NIT** on file-versus-branch.

---

## Q8 — Packet hygiene (charter §6)

The packet is **well-assembled by the standards I usually see**: atomic
questions, a mechanical exhibit manifest with digests that all verify, a
validator, and an explicit instruction to read the designs before the synthesis.
The defects below are real and several are material, but I want the record to
show they are defects in a serious packet, not a sloppy one.

**H-1 — BLOCKER, and self-inflicted by the packet.** Q2 instructs: "Execute
`claude --help` and `claude --bg --help` read-only; do not start a session",
and packet §5 forbids starting any `claude` session. **`claude --bg --help` does
not print help — it starts a background session.** Executing the packet as
written created session `6be6d134` in this worktree (§9(E)). Effect on this
gate: none on my reasoning, and it produced the strongest evidence in this
refutation. Effect on the machine: the session is now `state: done`, but two
`claude bg-*` processes (95679, 95703, spare `421d5d1d`, sockets dated 21:13,
coincident with the probe) are alive and match the production census. I did not
remove them — the charter forbids state-changing commands, and I had already
exceeded that boundary once by following the packet. **The magistrate should
decide whether to clear them before 02:56.** Minimum cure to the packet: replace
the instruction with `claude --help | grep -A6 -- '--bg'`, and never route a
`--help` through a mode-changing flag.

**H-2 — MATERIAL. Omitted contrary evidence on the decisive number (Q4).** The
packet directs me to "find the settle seconds" and offers the 180 s chain settle
as the supporting fact, while omitting `docs/phase_2/window_runbook.md:425-432`,
which sets a ≥10-minute untouched-idle requirement and states in terms that the
180-second settle **does not satisfy it**. That one paragraph decides Q4 against
the proposal. Effect: had I not gone looking, Q4 would have been adjudicated on
a fact set from which the answer could not be reached.

**H-3 — MATERIAL. Omitted contrary evidence on the `--bg` base (Q2).** Exhibit
10 §2's Spawn cell cites "this magistrate session itself runs as a background
job with `/loop` + `ScheduleWakeup` working" as the ground for `--bg`. At the
bench that same session reports `"status": "waiting", "waitingFor": "permission
prompt", "state": "blocked"`. The packet presents the existence half and omits
the state half. It also asserts "`/loop` + `ScheduleWakeup` working" with no
executed evidence, in a packet that elsewhere marks unexecuted claims carefully.

**H-4 — MATERIAL. Q1 is a compound question.** One YES/NO is demanded over the
deadline and the force, which have different answers (§Q1). Charter §6 names
this. Cure: split into Q1a (force) and Q1b (deadline).

**H-5 — MATERIAL. Exhibit 11b lacks the context needed to check it** (see Q7).
Ed's answers without the questions; item 7's "5 minutes" is nowhere in Ed's
quoted words. Charter §4 requires an admissible excerpt to carry "enough
contiguous context to be checked for selective quotation." Cure: add the
magistrate's leave-checklist questions as 11c.

**H-6 — MATERIAL. Asymmetric treatment in the fork table.** In the rows where
the magistrate departs from the seats — Stand-down, Session cwd, Kill switch,
Interlock — the "Proposed" cell carries a full argument while the rejected
positions are reduced to bare labels ("dedicated worktree", "as gate", "root
file `MAGISTRATE_STOP`"). In the Stand-down row this matters most: three
independent seats converged on force at t0−30/−35, and the table renders that
convergence as three separate cells rather than as the agreement it is.

**H-7 — MATERIAL. A load-bearing document is outside the packet.**
`docs/process_traces/2026-09-02-fresh-fable-audit/01-audit-night-loop.md` is
cited throughout designs 03/04 (F1–F11, B7–B10) and is the source of the
plan-pin cure that Q6 turns on ("audit item cited in exhibit 10 §1"). It is not
an exhibit, and it sits on an unmerged branch. The charter also bars me from
reading it as a narrative process document. Q6 was still decidable from code and
bench evidence, so I did not REFUSE — but a question should not depend on a
document the packet neither supplies nor permits.

**H-8 — NIT. Contamination by construction (answering Q8's direct question).**
I read 02 → 04 → 03 → 09 → 10, as asked. Isolation was still impossible: packet
§2 and §3 restate exhibit 10's fence predicate, install handoff and fork
choices, and the packet is the charter's mandated first read. I had the
magistrate's conclusions before the seats' arguments. Cure: put the proposal in
a sealed exhibit and keep the questions neutral of its content.

**H-9 — NIT, and I cured it myself.** Exhibits 11a/11b carry no charter §4
metadata block (source path, immutable revision, exact line range, the
proposition addressed, why non-narrative primary evidence is unavailable). Under
§4 that would normally force a REFUSE on the affected questions. I discharged it
mechanically instead of refusing, because the check is cheap and definitive:
both exhibits are **byte-identical to their tracked sources at `e57bb43e`** —
11a `cmp`-identical to `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`
(sha256 `9f0e6be1…228611`, both), and 11b's body byte-identical to
`docs/decision_log.md` lines 10586-10630 (§9(H)). No REFUSE is warranted on
fidelity grounds. The form defect should still be fixed in the next packet.

**No hygiene defect found in:** the exhibit manifest (7/7 digests verify), the
validator receipt, the charter pin, the §5 prohibitions, or the atomicity of
Q2–Q7.

---

## Summary of findings by severity

**BLOCKER**
1. `killpg(recorded_pgid)` does not reach `codex-code-mode-host`, which escapes
   into its own process group and matches the census. Forced stand-down cannot
   clear the census as specified. (Q1, Q2, Q3, Q4)
2. `--bg` as the base is incompatible with the zero-agent fence: the bg daemon,
   pty host and pre-warmed spares match the census, sit outside the session's
   process group, and are unowned by exhibit 10's own kill rule. (Q2)
3. The required post-kill census verification is absent from exhibit 10's
   proposal and from the packet's proposed bench proof. (Q2, Q4)
4. Narrowed census scope lets the watchdog launch a magistrate at 07:01 while
   the dead-man's courier — the night's only channel to Ed — is running. (Q3)
5. Stand-down at t0−5/t0−4 violates the run-book's ≥10-minute untouched-idle
   requirement, which the run-book says the 180 s chain settle does not
   satisfy. (Q4)
6. The plan-pin change must land before install; installing necessarily moves
   the canonical HEAD and stales the armed plan, and the stale check
   short-circuits before the census, nulling the rehearsal's only observable.
   (Q6)
7. Install cannot follow this gate: D-171 item 4 conditions authorization on a
   gauntlet over an implementation that does not exist, and on a watchdog that
   emails Ed at each stand-down — which the proposed timings make the
   exception rather than the rule. (Q7)

**MATERIAL**
8. Stop-switch probe cannot distinguish a network blip from a permanently dead
   switch (rc 128 both ways), and fails open on both, with no signal to Ed. (Q5)
9. Exact-ref stop probe makes a phone typo silent and indistinguishable from
   "not stopped"; the local STOP file was dropped without notice. (Q5)
10. The canonical-checkout git ban is worded over-broadly ("git operations"),
    banning the `fetch` the session needs to resume at all. (Q6)
11. Deferring Sol's shared launch interlock rests on the premise Q3 falsifies. (Q3)
12. Hygiene H-2, H-3, H-4, H-5, H-6, H-7.

**NIT**
13. `ops/` D-F namespace; 294-branch prune exposure. (Q5)
14. "stop file" silently redefined as "stop branch". (Q7)
15. Hygiene H-8, H-9.

## Where I disagree with the magistrate's labelled disposition (charter §8 — silence reads as concurrence)

I **agree** with: the branch-over-file kill switch; one user LaunchAgent with no
`KeepAlive`; spawning through the stable symlink; kill-only-what-you-own as a
principle; excluding night-arming from the watchdog's charter; and that D-171
does not require Ed to reply.

I **disagree** with, and would not let stand as written: `--bg` as the base
(Q2); the census-scope narrowing (Q3); the t0−20/−5/−4 timings (Q4); deferring
the interlock (Q3); installing after this gate rather than after a gate on the
built artifact (Q7); and treating the plan-pin change as a follow-up (Q6).

---

## 9. Executed evidence

Everything below was executed by me this session, read-only, in
`/Users/edr/code/JouleWise-wt-coldgate-wd` at `e57bb43e` unless noted. Nothing
was written under any checkout; no plist, launchctl, custody record, or
`~/Library/LaunchAgents` entry was touched. **One exception, disclosed at H-1:
`claude --bg --help` started a background session.**

**(A) Validator receipt** (`scripts/validate_gate_packet.py`), abridged to the
decisive fields; full JSON at `…/scratchpad/coldgate-wd/validator-receipt.txt`:

```
"result":"PASS", "schema":"coldgate-validator-receipt/v2",
"judge_handoff_bound":false, "reason":null,
"packet_sha256":"af2b9818403e135778c90c8797b960ffb6123269728136f58868df6704180975",
"charter_sha256":"099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81",
"exhibit_manifest_sha256":"a32af88f317f38840fa3e22daab066e947a427b77b677237ca23cfcbe0e275b3",
7 exhibits, observed_sha256 == expected_sha256 for all 7
```

**(B) Checkout identity.** `git rev-parse HEAD` → `e57bb43ebf00c088968c03f97de8b4f93286af47`;
`git status --porcelain` → clean. `shasum -a 256` on charter and packet reproduced
the two expected digests above.

**(C) `claude --help`** (version `2.1.259 (Claude Code)`), verbatim fragments
relied on: the `--bg, --background` entry quoted in full at Q2(a);
`--permission-prompts <target>` "Who answers permission prompts with --print:
'host' … or 'none' (nobody: anything that would prompt is denied automatically;
the permission mode still decides everything else)"; `--output-format` /
`--fallback-model` / `--max-budget-usd` / `--no-session-persistence` /
`--include-partial-messages` each "(only works with --print)";
`-p, --print` "Print response and exit"; `--add-dir <directories...>`
"Additional directories to allow tool access to"; `--permission-mode` choices
`acceptEdits|auto|bypassPermissions|manual|dontAsk|plan`. Commands present:
`agents`, `attach <id>`, `logs <id>`, `respawn [id]`, `rm <id>`, `stop|kill <id>`.

**(D) Production census predicate**, `/usr/bin/pgrep -lf "codex|claude|t3"` at
21:15:18 PDT → exit 0, 2144 lines. The background-infrastructure rows:

```
 4384 claude bg-pty-host --bg-pty-host /tmp/cc-daemon-501/14ebf21c/spare/6a8837f0.pty.sock 200 50 -- …/versions/2.1.259 --bg-spare …
 4389 claude bg-spare    --bg-spare    /tmp/cc-daemon-501/14ebf21c/spare/6a8837f0.claim.sock
95679 claude bg-pty-host --bg-pty-host /tmp/cc-daemon-501/14ebf21c/spare/421d5d1d.pty.sock 200 50 -- …/versions/2.1.259 --bg-spare …
95703 claude bg-spare    --bg-spare    /tmp/cc-daemon-501/14ebf21c/spare/421d5d1d.claim.sock
```

`AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")` at
`joulewise/night_gate.py:34`; the empty-census predicate (exit 1 **and** empty
stdout) and `night_refused_agent_present` at `joulewise/night_gate.py:405-415`.

**(E) The `--bg` side effect (H-1).**

```
$ claude --bg --help          # expected: help text.  actual: a session.
backgrounded · 6be6d134 (idle — send a prompt to start)
  claude agents             list sessions
  claude attach 6be6d134    open in this terminal
  claude logs 6be6d134      show recent output
  claude stop 6be6d134      stop this session
```

`claude agents --json --all` then returned, among others:

```
{"pid":4453,"id":"3c46c831","cwd":"/Users/edr/code/JouleWise","kind":"background",
 "name":"Paper experiment loop","status":"waiting",
 "waitingFor":"permission prompt","state":"blocked"}
{"id":"6be6d134","cwd":"/Users/edr/code/JouleWise-wt-coldgate-wd",
 "kind":"background","startedAt":1788408805349,"state":"done"}
```

Session `3c46c831` is this refuter's own parent session (my tool-result files are
written under `~/.claude/projects/-Users-edr-code-JouleWise/3c46c831-…/`), i.e.
the session exhibit 10 §2 cites as its `--bg` existence proof.

**(F) Process-group map** (`ps -o pid,ppid,pgid,command`), the evidence for the
kill-reach finding:

```
  PID  PPID  PGID COMMAND
 4375  1536  4375 /Users/edr/.local/bin/claude daemon run --origin transient --spawned-by {"label":"claude",…,"pid":1536}
 4394  4375  4394 …/ClaudeCode.app/Contents/MacOS/claude --bg-pty-host /tmp/cc-daemon-501/14ebf21c/pty/3c46c831.sock …
 4384  4375  4384 claude bg-pty-host …/spare/6a8837f0.pty.sock …
 4389  4384  4389 claude bg-spare    …/spare/6a8837f0.claim.sock
95679  4375 95679 claude bg-pty-host …/spare/421d5d1d.pty.sock …
95703 95679 95679 claude bg-spare    …/spare/421d5d1d.claim.sock
 4453  4394  4453 …/versions/2.1.259 --session-id 3c46c831-… --fork-session --resume …   ← THE SESSION
 4478  4453  4453 node …/codex mcp-server -c model="gpt-5.6-sol" …                        ← in group
 4480  4478  4453 …/codex-darwin-arm64/…/codex mcp-server …                               ← in group
 4822  4480  4822 …/codex-darwin-arm64/…/codex-code-mode-host                             ← ESCAPED (own pgid)
 1536  1282 1536 claude                                                                   (interactive)
 1560  1557 1536 …/codex mcp-server …
 2972  1560 2972 …/codex-code-mode-host                                                   ← ESCAPED (own pgid)
 4436  4389 4389 node …/codex mcp-server …                                                ← child of a SPARE
 4438  4436 4389 …/codex mcp-server …                                                     ← child of a SPARE
```

Two independent instances of `codex-code-mode-host` in its own process group
(4822 from parent 4480 in group 4453; 2972 from parent 1560 in group 1536).
Ancestry of the session: `4453 ← 4394 ← 4375 (daemon) ← 1536 (claude) ← 1282
(-zsh) ← 1278 (login) ← 1212 (Terminal.app)`. Daemon dir
`/tmp/cc-daemon-501/14ebf21c/` created 20:49; `spare/` mtime 21:13 with sockets
`421d5d1d.*` dated 21:13.

**(G) Stop-switch probes** (Q5). Packet-directed probe first, then the matrix:

```
$ git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/ops/stop-magistrate
rc=2      (no output)
$ git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/main
e57bb43ebf00c088968c03f97de8b4f93286af47	refs/heads/main          rc=0
$ git ls-remote --exit-code https://github.com/mpmdw/JouleWise.git refs/heads/ops
rc=2      (no branch named `ops`; no D/F conflict today)

# anonymous (credential helper disabled, terminal prompts off):
$ GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote --exit-code <url> refs/heads/main
e57bb43e…	refs/heads/main          rc=0        → repo is public, no auth needed
$ …                                       refs/heads/ops/stop-magistrate
rc=2                                                 stdout empty, stderr empty
$ …  https://nonexistent.invalid/x.git    refs/heads/ops/stop-magistrate
rc=128   fatal: unable to access …: Could not resolve host: nonexistent.invalid
$ …  https://github.com/mpmdw/JouleWise-does-not-exist.git  refs/heads/ops/stop-magistrate
rc=128   fatal: could not read Username for 'https://github.com': terminal prompts disabled

# glob semantics (the typo cure):
$ git ls-remote --exit-code <url> 'refs/heads/ops/*'         rc=2   (empty)
$ git ls-remote --exit-code --heads <url>                    rc=0   294 branches
```

**(H) Exhibit fidelity checks** (H-9):

```
$ cmp -s docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md \
         docs/process_traces/2026-09-02-hands-free-week/11a-exhibit-ruling-unattended-stage1.md
IDENTICAL
$ shasum -a 256 (both)
9f0e6be1beec32b0eb525886181e3704bf3d57343ac046bf84c8ec4322228611  (source)
9f0e6be1beec32b0eb525886181e3704bf3d57343ac046bf84c8ec4322228611  (exhibit 11a)
```

D-171: `docs/decision_log.md` heading at line 10586, block 10586–10630; the
exhibit 11b body from its `## D-171` heading is byte-identical to that block
(sha256 prefix `77d65fde4de02e2f` for both). Index row at
`docs/decision_log.md:217`.

**(I) Plan-pin state** (Q6):

```
$ git -C /Users/edr/code/JouleWise rev-parse HEAD
33290b8bbe82b126037101edf8f15cdf96c920da
$ git -C /Users/edr/code/JouleWise status --porcelain=v2 --branch
# branch.oid 33290b8bbe82b126037101edf8f15cdf96c920da
# branch.head main
# branch.upstream origin/main
# branch.ab +0 -6
$ python3 … /Users/edr/night-custody/rehearsal-20260903/night_plan.json
t0_epoch_s = 1788429360      → 2026-09-03 02:56:00 local
window_max_s = 900 ; authored_epoch_s = 1788405403 → 2026-09-02 20:16:43
repo_head = 33290b8bbe82b126037101edf8f15cdf96c920da
receipt_class = REHEARSAL_STUB
custody_root = /Users/edr/night-custody/rehearsal-20260903
(now = 2026-09-02 21:19:00 local)
$ git log --oneline 33290b8b..e57bb43e
e57bb43e hands-free week: watchdog design custody (09 Sol), magistrate synthesis (10), mechanical cold-gate packet (11) + exhibits 11a/11b
e3ed4fbf RUN_STATE T31 + hands-free-week durable state (00) …
56a3b9e4 hands-free week: custody the measurement-checkout catch-up …
b4cc8e50 test_docs_freshness: derive the counterfactual decision id from the index …
eeb4e133 D-171: index row
0f9b1be6 D-171: hands-free week — Ed's delegations for unattended windows …
```

Only two custody plan directories exist: `rehearsal-20260902`, `rehearsal-20260903`.

**(J) Code citations personally opened at this commit.**
`joulewise/night_gate.py`: `AGENT_CENSUS_ARGV` :34; `agent_census` :388-415 with
the empty predicate at :405-406 and `night_refused_agent_present` at :415;
missed-fire/window guard :551-571; `night_plan_stale` on age :591-597 and on
HEAD mismatch :599-609; **`agent_census` called at :611 — after the stale
return**. `scripts/run_night.py`: gate evaluation `probes = make_probes()` :1106 and
`receipt = evaluate_night(plan, probes)` :1107; `_claim_chain_start` and
`_run_chain_once` :1198-1228; dead-man :1301-1322.
`scripts/install_night_agent.sh`: KeepAlive refusal :35-38; `[[ "$plan_head" ==
"$actual_head" ]] || … exit 3` :40-45. `scripts/capture_t0_step.py:349-352`
(frozen `SETTLE_S` 180). `scripts/quiet_window_clock.sh:32,130-133`.
`scripts/gen_g2_phase_d.py:259-260`. `docs/phase_2/window_runbook.md`: :143,
:222, :425-432, :438, :641-652, :1325-1332, :1666-1668.
`CLAUDE.local.md`: untracked (`git ls-files --error-unmatch` → "did not match any
file(s) known to git"), present at `/Users/edr/code/JouleWise/CLAUDE.local.md`
(10574 bytes), absent from `/Users/edr/code/JouleWise-wt-coldgate-wd/`.

**Not executed / not read.** No `claude -p` or `codex` session was started (the
one `--bg` session at H-1 was the packet's instruction and ran no turn). I did
not read `RUN_STATE.md`, `council_log.md`, run reports, night run records,
`01-audit-night-loop.md`, or any scratchpad. I did not test whether a `--bg`
session survives under launchd, whether `ScheduleWakeup` fires in `-p` or `--bg`
mode, whether stopping a `--bg` session reaps the daemon and its spares, or
whether `killpg` would in fact leave `codex-code-mode-host` running — the last
is inferred from POSIX process-group semantics plus the observed pgid values,
and it is the single most important thing the pre-install bench must confirm
directly.
