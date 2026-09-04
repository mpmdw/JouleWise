# Counter-review — Opus seat, gate ledger row 6, contract lens — final head (2026-09-04)

Seat: Opus, counter-review, read-only except this file. Worktree
`/Users/edr/code/JouleWise-wt-watchdog-build`, branch
`feat/2026-09-03-magistrate-watchdog`, head `3f6b6282`, diff
`git diff origin/main...HEAD` (49 files, +9387/-69).

Read this session, in full: traces 12 (my own earlier consult, AD-1..AD-13), 13,
15, 16 (+ S-2b addendum), 18, 20; `origin/main:docs/process_traces/2026-09-02-hands-free-week/19-coldgate-fable-ruling-packet-17.md`;
`docs/process/MAGISTRATE_WATCHDOG.md` (all 350 lines);
`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` (all 23);
`scripts/install_magistrate_watchdog.sh` (all 217);
`configs/launchd/com.joulewise.magistrate.plist.template` (all 33);
`joulewise/night_plan_writer.py` (all 67); `scripts/magistrate_watchdog.py`
(:1-120, :399-530, :600-830, :970-995, :1095-1300, :1380-1720, :2018-2098);
`joulewise/night_gate.py` (:77, :175, :437, :660-680);
`tests/test_magistrate_watchdog.py` (:1178-1262).

Executed this session (only to confirm named claims):

| # | Probe | Result |
|---|---|---|
|E1|`python3 -m unittest` the five permitted night modules|`Ran 169 tests in 26.242s` **OK** — the head is green|
|E2|Real CLI `tick --dry-run` against a temp custody root whose `state.json` carries a pre-reboot `next_eligible_monotonic=1500900`, with this process's `time.monotonic()=113955`|`decision=BACKOFF_USAGE reason=backoff has not expired` — **B-3 reproduced**|
|E3|`sysctl -n kern.boottime` vs `time.monotonic()`|wall-since-boot 113963 s, `time.monotonic()` 113972 s → monotonic **is** uptime-since-boot on this machine and **does** survive sleep (so B-3's reboot premise holds; a sleep-driven `CLOCK_UNCERTAIN` story does **not**, and I do not assert it)|
|E4|`grep -rn install_magistrate_watchdog tests/`|two hits, both `read_text` string assertions at `tests/test_magistrate_watchdog.py:1183,1256` — **no behavioral test of the installer exists**|
|E5|`grep -n "CANONICAL\|rev-parse\|git " scripts/install_magistrate_watchdog.sh`|`NONE` — the installer never identifies which checkout it is in|

No install, no `launchctl`, no signal to any live process, no `~/night-custody`
access, no session started, no `[QUIET-MAC]` work. Repository writes: this file
only.

---

## Verdict

**NOT LANDABLE** — three blockers (B-1, B-2, B-3), one of which (B-1) defeats
the single guarantee the whole mechanism exists to provide, and one of which
(B-3) silently disables the watchdog for days after any reboot.

Scope note, because the two halves of this branch have different risk: the
**night-plan pin** half (`joulewise/night_gate.py`, `night_plan_writer.py`,
`install_night_agent.sh`, `run_night.py`) is sound and I found nothing against
it. Every blocker below is in the **watchdog** half, and B-2/B-4/S-2/S-3/S-4 are
in the surfaces that seven Sol rounds never executed: the installer, the plist,
and the install/handoff checklist. The pattern the round-5 consult named — "one
author held code, fixture and oracle in one commit, so the round could not
fail" — was cured for `scripts/magistrate_watchdog.py` by the R-2 real-CLI gate
and was **not** cured for `scripts/install_magistrate_watchdog.sh`, which is the
artifact that actually runs tonight.

All five blockers/should-fixes are small, local fixes; none needs a redesign.

---

## Blockers

### B-1 — blocker — a durable plan hold preempts plan-deadline enforcement, and its unclamped 540+60 ladder can push the KILL past `t0`

This is the composition of round 6's S-2 and round 7's S-2b with an **active
plan span**, which no round tested.

`ResidentSupervisor.step()` evaluates in this fixed order
(`scripts/magistrate_watchdog.py:1597-1668`):

1. `:1607-1618` — if `clock_drain`, `return self._enforce_drain(...)`.
2. `:1630-1642` — if `resident_hold_drain` is a mapping,
   `return self._enforce_drain(...)`.
3. `:1644-1662` — if `snapshot.errors or conflicts`, latch
   `state["resident_hold_drain"]` and `return self._enforce_drain(...)`.
4. `:1666-1668` — **only now** `relevant_standdown_plan(...)` → `_enforce_plan`.

Limbs 1–3 `return` unconditionally, so once either latch is set the resident
**never again evaluates `standdown_phase`** (`:798-805`, the `t0-25 / t0-16 /
t0-15` ladder) for the remainder of the activation. `resident_hold_drain` is
cleared only in `_finish_child` (`:1394`).

`_enforce_drain` (`:1533-1596`) has no plan input and no plan clamp. It calls
`self._write_request(None, ...)` — note the literal `None`, so the request
carries no `term_epoch_s`/`kill_epoch_s` (contrast `:1441-1442`, where
`_enforce_plan` does write them) — and then keys TERM/KILL purely on
`elapsed = monotonic - requested_monotonic` against `STOP_COOPERATIVE_S = 540`
and `STOP_COOPERATIVE_S + STOP_TERM_GRACE_S = 600` (`:1566`, `:1576-1577`).
`KILL_LEAD_S` appears nowhere in the function.

`_write_request` returns early if `standdown.request` already exists
(`:1426-1430`), so the anchor is whichever path wrote first. That is the entire
safety of the current shape, and it holds only while the plan path ran first.

**Arithmetic.** Let `H` be the wall time at which the hold latches, `t0` the
window start. If no `standdown.request` exists at `H` (true whenever the hold
latches before the plan span opens the request at `t0-25`, or whenever the
supervisor was forked after `t0-25`), then:

- TERM at `H + 540`, KILL at `H + 600`.
- Guarantee requires KILL `<= t0 - 900`. That holds only for `H <= t0 - 1500`,
  i.e. only for a hold latched at or before `t0 - 25 min`.
- `H = t0 - 22 min` → KILL at **t0 - 12 min**.
- `H = t0 - 15 min` → KILL at **t0 - 5 min**.
- `H = t0 - 10 min` → KILL at **t0 + 0**.
- `H = t0 - 5 min` → KILL at **t0 + 5 min**, i.e. five minutes *inside* the
  protected window, with the full agent tree alive until then.

**Counterfactual (concrete, not hypothetical).** Tonight's plan is armed at
`~/night-custody/win-a11/` with `t0 = 03:00`; the magistrate is resident. At
02:44 a *second* sibling plan directory contains a plan that fails validation —
tomorrow's plan authored with `authored_epoch_s` a few seconds in the future
(`load_plans:663-667` raises `night_plan_malformed` on exactly this), or a plan
whose `measurement_head` was dropped, or any `night_plan.json` the operator is
mid-edit. The resident latches `resident_hold_drain` at 02:44, writes the
request at 02:44, sends TERM at 02:53 and KILL at 02:54 — **six minutes after
the ruled `t0-15` KILL**, and it never once evaluated tonight's plan. Change
the arrival to 02:55 and the KILL lands at 03:05, inside the window.

The same shape applies to `clock_drain` (limb 1), which is additionally
irreversible once latched.

**What this does and does not cost.** It does not corrupt physics: at `t0` the
night gate runs the production `agent_census` and refuses
(`joulewise/night_gate.py:666-674`, `night_aborted_agent_present` at `:77`), so
the outcome is a *refused window*, not contaminated evidence. But (a) the
watchdog's ruled contract, restated at `docs/process/MAGISTRATE_WATCHDOG.md:42-47`
and affirmed by the cold gate's Q6 ("request, TERM +9 min, KILL +10 min"
*outside* a plan; `t0-16`/`t0-15` *inside* one), is not delivered; and (b) with
Ed away, a refused window is a week-scale loss and the failure is announced only
in `events.jsonl`.

The irony is exact: the mechanism installed in rounds 6–7 to make holds
*fail-closed* created a *fail-late* path through the one deadline the system
exists to honour. Rounds 6 and 7 tested S-2/S-2b only with no plan span, and the
delta re-audits inherited that framing.

**Cure (small).** `_enforce_drain` takes the relevant plan (or its
`kill_epoch_s`) and clamps: TERM at `min(request + 540, t0 - TERM_LEAD_S)`, KILL
at `min(request + 600, t0 - KILL_LEAD_S)`. Regression: latch a
`resident_hold_drain` at `t0 - 10 min` with an active valid plan present; assert
SIGKILL is recorded at or before `t0 - 900`.

---

### B-2 — blocker — the installed plist points at whatever checkout the installer happened to run from; nothing pins it to the canonical repo

`scripts/install_magistrate_watchdog.sh:35-36`:

```zsh
script_dir="${0:A:h}"
repo="${script_dir:h}"
```

`$repo` is substituted into **both** `@@REPO@@` sites of the template — the
`ProgramArguments` script path
(`configs/launchd/com.joulewise.magistrate.plist.template:11`) and
`WorkingDirectory` (`:14`). The installer performs no check that `$repo` is
`/Users/edr/code/JouleWise` (E5: it contains no `git`, no `rev-parse`, no
canonical constant), even though `scripts/magistrate_watchdog.py:56` defines
`CANONICAL_REPO` and uses it for the child's cwd at `:1753` and for the prompt
fence at `:777`.

The install checklist compounds this. `docs/process/MAGISTRATE_WATCHDOG.md:118-121`
gives the command as a bare relative path with **no `cd`**:

```zsh
scripts/install_magistrate_watchdog.sh --install
```

and step 5 derives the reaper's import path the same way
(`:128`, `watchdog_checkout="$(/usr/bin/git rev-parse --show-toplevel)"`), also
from cwd. The doc pins cwd exactly once, for the unrelated no-TTY bench
(`:267`, "from the canonical checkout"). Meanwhile the surrounding text
instructs the magistrate to install *night* agents "FROM that plan's
`measurement_root`" (`:219`) and the relaunch prompt instructs the session to
"Work in linked worktrees" (`MAGISTRATE_RELAUNCH_PROMPT.md:7`) — so at the
moment step 4 runs, cwd is ambiguous between at least three trees, and the most
likely one is a worktree, because that is where the magistrate was told to work.

**Counterfactual.** The magistrate runs step 4 from
`/Users/edr/code/JouleWise-wt-watchdog-build` (this tree) or from any
`.claude/worktrees/*` tree. The plist is written with
`ProgramArguments = [/usr/bin/env, python3, <worktree>/scripts/magistrate_watchdog.py]`.
Everything verifies: `plutil -lint` passes, `bootstrap` succeeds, `launchctl
print` succeeds, the first tick runs, the handoff receipt says pass. Days later
the worktree is removed (`ExitWorktree`, `git worktree prune`, or an ordinary
cleanup). From then on every 300-second tick is `env: python3: can't open file
'<gone>/scripts/magistrate_watchdog.py'` into `launchd.err`, exit 2. There is no
resident supervisor to notice, no notice queued, no email — the notice channel
requires a *launched session*, and none launches. The doc states outright that
"there is intentionally no watchdog-for-the-watchdog"
(`MAGISTRATE_WATCHDOG.md:61`). Ed is away; the loop is dead for the remainder of
the week and the only symptom is silence.

**Cure.** Refuse `--install` unless `$repo -ef /Users/edr/code/JouleWise`
(matching `CANONICAL_REPO`), and add `cd /Users/edr/code/JouleWise` to doc steps
3–5. Regression: run `--install` from a copy of the tree at another path and
assert exit 3 with a named reason.

---

### B-3 — blocker — `next_eligible_monotonic` is persisted across reboots, wedging the watchdog in BACKOFF for the whole of the previous uptime

`apply_backoff` stores an absolute monotonic instant:
`state["next_eligible_monotonic"] = monotonic + delay`
(`scripts/magistrate_watchdog.py:1117`), and `_finish_child` does the same on a
*clean* exit (`:1412`, `monotonic() + 300`). `decide` gates on it at `:1197`:

```python
if monotonic < float(state.get("next_eligible_monotonic", 0.0)):
```

That value is written into `state.json` (`:1423`, `:1494`) and read back by
`load_state` (`:494-510`), which validates only schema and type. Nothing
anywhere compares it to the current monotonic epoch, and nothing records a boot
id. E3 confirms `time.monotonic()` on this machine is uptime-since-boot
(113 972 s vs 113 963 s wall-since-boot — it survives sleep, but not reboot).

**Counterfactual, executed (E2).** The machine has been up 17 days when a
session exits on a usage limit; `next_eligible_monotonic` is written as
≈1 500 900. The Mac reboots (software update, panic, power). At next login the
agent loads with `monotonic() ≈ 113 955`. The real CLI returns:

```
decision=BACKOFF_USAGE reason=backoff has not expired
```

and will keep returning it, every 300 s, until uptime again exceeds the
pre-reboot value — up to **the full previous uptime**, i.e. potentially the rest
of Ed's week. No notice is queued (the backoff notice was queued at the original
transition), no session launches, no email is sent. `clock_uncertain` masks it
for the first two ticks (`mono_delta < 0` at `:983`) and then clears
(`:988-995`), after which the tick reports a clean-looking BACKOFF forever.

**Cure.** On load, if `next_eligible_monotonic > monotonic + max(ladder)`, the
clock has restarted: reset it to `0.0` and record an event. Or store the
deadline as a wall epoch alongside the monotonic value and take the earlier of
the two. Regression: seed `state.json` as in E2 and assert the tick does not
report BACKOFF.

---

### B-4 — blocker — `install_magistrate_watchdog.sh` has no behavioral test at all; its only coverage is four `assertIn` string greps

E4: the entire test corpus references the installer twice, both as text:

- `tests/test_magistrate_watchdog.py:1183-1188` — `read_text` then
  `assertIn('"first_install_adoption": True', installer)`,
  `assertIn("os.O_EXCL", installer)`,
  `assertIn("must be run by the current magistrate session", installer)`.
- `tests/test_magistrate_watchdog.py:1250-1262` — `assertIn`/ordering over the
  doc's step strings.

This is verbatim the AD-13 defect class (`docs/process_traces/2026-09-03-watchdog-build/12-consult-opus-contract.md`,
AD-13: "doc tests assert string counts … it fails when someone adds a third
correct example and passes for a doc that is wrong in every other respect"),
which S-4 cured for the *documentation examples* in round 6 while leaving it in
place for the *installer*. It is also the exact structural condition R-2 was
written to abolish (trace 13 R-2, "the seat must show this test RED on the
current head, then GREEN"): the R-2 cure was applied to
`scripts/magistrate_watchdog.py` and not to the sibling script that runs on the
same night. The repo already owns the right pattern one module over —
`tests/test_install_night_agent.py` (228 lines) runs
`/bin/zsh scripts/install_night_agent.sh` as a real subprocess against a stub
`PATH`, a temp `HOME`, and a real temp git repo, with `--launchctl-bin` pointing
at a stub. That is precisely why the *night* installer's plan-pin defects were
caught in rounds 1–3 and why B-2, S-2 and S-5 below survived seven rounds here.

**Counterfactual.** Any of B-2 (unpinned `$repo`), S-2 (`O_EXCL` collision
after the plist is already written), S-5 (unpinned interpreter) is invisible to
every existing assertion, because none of them changes the installer's text.
Each would be a one-line failure in a `--render-only` + stub-`launchctl`
subprocess test.

**Cure.** A `tests/test_install_magistrate_watchdog.py` modelled on
`tests/test_install_night_agent.py:97-118`: temp `HOME`, stub `launchctl`,
`--render-only` and a full `--install` against the stub; assert the rendered
`ProgramArguments` path, the seeded lock's `first_install_adoption`, the
non-canonical-repo refusal, and the behaviour when `magistrate.lock` already
exists.

---

## Should-fix

### S-1 — should_fix — launchd's 300 s granularity puts the replacement-tick KILL as late as `t0 - 10 min`

`decide` returns `STANDDOWN_{phase}` with `adopt=True` when a plan span is
active and the owner is live (`scripts/magistrate_watchdog.py:1178-1187`), and
`tick` forks a fresh supervisor. Detection latency is one launchd
`StartInterval` (`configs/launchd/com.joulewise.magistrate.plist.template:24-25`,
300 s), and launchd does not guarantee punctuality under load or after wake.

Worst case: the resident dies at `t0 - 15:05`, immediately after a tick. The
next tick fires at `t0 - 10:05`; the newly forked supervisor's first `step()`
computes `phase == "KILL"` and signals — at **`t0 - 10 min`**, five minutes
later than ruled. If that tick instead lands in the first two post-wake samples,
`clock_uncertain` returns `True` (`:990-995` requires two sane samples) and
`decide` returns at `:1138-1139` **before reading the lock**, so no adoption
happens for another 300–600 s; the compound worst case reaches `t0` itself.

This is inherent to a 300 s poll and cannot be fully removed, but it is
undocumented: `docs/process/MAGISTRATE_WATCHDOG.md:42-47` presents `t0-16`/
`t0-15` as guarantees without stating that they hold only while the resident
supervisor is alive. State the bound explicitly ("a supervisor death inside the
span degrades the KILL to `t0 - 15 min + StartInterval`"), or reduce
`StartInterval` inside a plan span.

### S-2 — should_fix — the `O_EXCL` lock seed fails *after* the plist is on disk, and the doc has no recovery branch

Order in `scripts/install_magistrate_watchdog.sh`: render + write the plist
(`:146-163`), `plutil -lint` (`:164`), **then** seed `magistrate.lock` with
`os.O_CREAT | os.O_EXCL` (`:191`), then `bootstrap` (`:208`).

If `magistrate.lock` already exists — a previous aborted install, a bench
rehearsal that used the default custody root, a stale lock from any earlier
resident — the Python block dies with `FileExistsError`, `set -euo pipefail`
aborts, and the script exits **with `~/Library/LaunchAgents/com.joulewise.magistrate.plist`
already written and never bootstrapped**. Re-running `--install` fails
identically and forever. `docs/process/MAGISTRATE_WATCHDOG.md:118-123` gives no
failure branch, and this is step 4 of a checklist executed with no human
present.

The residue is not inert: a plist in `~/Library/LaunchAgents` is loaded at the
next GUI login. It would then run with **no seeded lock** while the interactive
twin is still alive, and `decide` (`:1194-1205`) would reach `LAUNCHING` and
spawn a **second** magistrate beside the twin — exactly the double-session state
the `first_install_adoption` seed exists to prevent.

Cure: seed the lock before writing the plist, or `rm -f "$plist"` on any failure
path after `:162`; and give the doc an explicit "if the lock already exists,
inspect it and remove it only after confirming no live owner" branch.

### S-3 — should_fix — a LaunchAgent does not survive an unattended reboot, and nothing tells Ed the watchdog is gone

`RunAtLoad`+`StartInterval` (`configs/launchd/com.joulewise.magistrate.plist.template:24-27`)
are correct, but a **user** LaunchAgent in `~/Library/LaunchAgents` loads at GUI
login, not at boot. If the Mac reboots while Ed is away — automatic update,
panic, power loss — nothing logs in, the agent never loads, and (per
`MAGISTRATE_WATCHDOG.md:61`) nothing watches the watchdog. Combined with B-3,
even a *successful* login after reboot yields days of silent BACKOFF.

The install checklist should (a) state the reboot exposure, (b) name the
mitigation the operator must take before the away week (disable automatic
restart-for-updates; confirm auto-login or accept the exposure), and (c) give Ed
a liveness threshold — the relaunch prompt makes an email the session's first
external act (`MAGISTRATE_RELAUNCH_PROMPT.md:2,5`), so "no email within N hours
means the watchdog is dead, ssh in and re-bootstrap" is the whole recovery
procedure and it is currently written nowhere.

### S-4 — should_fix — the documented rehearsal stubs share the real `measurement_root`, so arming the first real window while a stub is still armed is a permanent `plan_conflict`

Both documented stub plans use
`measurement_root="/Users/edr/JouleWise-measurement-20260813"` with
`measurement_head="0"*40` (`docs/process/MAGISTRATE_WATCHDOG.md:250` bench;
`:340` adoption rehearsal). `plan_is_armed`
(`scripts/magistrate_watchdog.py:715-724`) keeps an authored, non-completed plan
armed until `_next_deadman_epoch(t0) + COURIER_LOCK_FRESH_S` — up to about a
day — and a `REHEARSAL_STUB` never produces `night/courier.sent`, so it runs to
that full bound. `plan_conflicts` (`:741-750`) then fires on
`heads_by_root`, with **no span-overlap condition**:

```python
if len(heads) > 1:
    conflicts.add(f"one measurement_root has multiple heads: ...")
```

**Counterfactual.** The adoption rehearsal runs in the evening. Later the same
night the first real plan is armed for the same measurement checkout at its real
`measurement_head`. Both are armed; the roots match, the heads differ; every
tick returns `HOLD_UNSAFE plan_conflict` (`:1147-1149`), which via B-1's limb 3
drains and kills the resident magistrate and refuses every relaunch until the
stub's deadman bound passes. The conflict rule itself is correct and ruled
(R-6 / AD-11); the defect is that the checklist creates the collision and never
says to remove it. `MAGISTRATE_WATCHDOG.md:219` says only "Rehearsal stubs
may follow watchdog installation".

Cure: one sentence — "remove every `REHEARSAL_STUB` plan root before arming any
real plan" — plus, better, give the stubs a distinct throwaway
`measurement_root` so a forgotten stub cannot collide at all.

### S-5 — should_fix — the launchd interpreter is unpinned and is not the interpreter any test used

`ProgramArguments` is `/usr/bin/env python3` (template `:9-10`) resolved against
`PATH = $HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`
(`scripts/install_magistrate_watchdog.sh:47`). `~/.local/bin` is first, and it
is exactly the directory this project uses for personal tooling
(`~/.local/bin/claude`, `~/.local/bin/codex-run-v3`). Every test and every
recorded bench invokes the module through `sys.executable` or a bare `python3`
in an interactive shell, so the interpreter that will actually run this every
300 seconds for a week has never been exercised.

`joulewise/night_gate.py` is stdlib-only (the same reasoning AD-10 used to
accept system `python3` for the reaper), so there is no reason not to pin
`/usr/bin/python3` in `ProgramArguments`. Cure: replace `/usr/bin/env python3`
with `/usr/bin/python3` and assert the rendered value in the S-B4 installer
test.

### S-6 — should_fix — the Gmail path, on which the entire away-week contract rests, has never been exercised in `-p` mode

The relaunch prompt makes emailing Ed the session's defining external act
(`MAGISTRATE_RELAUNCH_PROMPT.md:5-6`, and `notice.ack` — consumed by the
supervisor — is written only *after* Gmail accepts). `mcp__claude_ai_Gmail__send_message`
is in `SESSION_ARGV_AFTER_PROMPT`'s `--allowedTools`
(`scripts/magistrate_watchdog.py:94-95`). But the one recorded headless bench
(`docs/process_traces/2026-09-03-watchdog-build/02-bench-headless-spawn.md`)
used the prompt *"Reply with exactly the single word OK and nothing else. **Do
not use any tool.**"* and `--effort low`. It proves the spawn, the argv, and
`end_turn`; it proves nothing about whether the Gmail MCP server loads and
authenticates in a launchd-spawned, no-TTY, `--permission-prompts none` session.

If it does not, the failure is silent in the worst way: prompt line 21 tells the
session to preserve the message under the custody root and continue, so the loop
runs all week and Ed hears nothing. One bounded bench — the same argv with a
prompt that sends one real email to Ed — closes it. This is the same shape as
cold-gate M-1 ("launchd `-p` unproven before twin kill"), one layer up.

---

## Nits

- **N-1** — `docs/process/MAGISTRATE_WATCHDOG.md:174,195`: the reaper's `"termed"`
  outcome is unreachable. The KILL pass calls `signal_matching` for **every**
  recorded pid (`:180-181`), which overwrites each outcome with `kill_sent` or
  `already_gone`, so the later `elif ... == "term_sent"` branch can never match.
  Cosmetic in the receipt, but the receipt is the handoff's only evidence.
- **N-2** — `MAGISTRATE_WATCHDOG.md:125` claims the reaper "waits the full
  `STOP_COOPERATIVE_S`", implying the cooperative grace AD-9 asked for. It does
  not: it sends SIGTERM first (`:176-177`) and *then* sleeps 540 s. No
  `standdown.request` is written, so the twin never gets the cooperative signal
  the relaunch prompt promises it (`MAGISTRATE_RELAUNCH_PROMPT.md:15-17`). The
  behaviour may be intended — say so, rather than describing it as a cooperative
  wait.
- **N-3** — `MAGISTRATE_RELAUNCH_PROMPT.md:10` fences the measurement roots only
  "while any plan is armed". Benign in practice (the pin is taken at authorship,
  so a pre-arm move cannot invalidate it), but the sentence reads as a general
  fence and would mislead a session that moved the checkout in the gap. Consider
  "never move any measurement checkout without a re-arm".
- **N-4** — `MAGISTRATE_WATCHDOG.md:217` expects "the next five-minute tick
  must create the first watchdog-owned one-turn `-p` magistrate". The reaper
  SIGKILLs the adopted twin without writing `standdown.request`, so
  `_finish_child` (`scripts/magistrate_watchdog.py:1389-1421`) takes the
  `classify_exit` branch, records a generic failure, applies the 120 s
  `GENERIC_BACKOFF_S[0]`, and queues a `launch_failure` notice. The launch still
  happens (120 s < 300 s), but the first launch email will carry a spurious
  failure notice. Say so, so the observer does not read it as a failed handoff.

---

## Install/handoff walk-through: steps whose failure is silent

Priority (1) asked for this explicitly. Walking
`docs/process/MAGISTRATE_WATCHDOG.md:99-217` against the code, as a magistrate
with no human present would execute it:

| Step | Failure mode | Silent? |
|---|---|---|
|1 (drain background tasks)|A missed Codex child stays alive; it is then an unclassified census hit at `t0`|**Yes** until the first `HOLD_CENSUS`|
|2 (`mv` retired-v1 trees)|`test -d` / `test ! -e` guard it; `set -e` aborts|No|
|3 (`handoff-inventory`)|Relative script path; requires cwd = a checkout. Wrong cwd → `zsh: no such file`|No (but see B-2)|
|3 (`--adopt-pid`)|Promoting a wrong pid puts a foreign process on the kill list|**Yes** — nothing re-checks provenance|
|4 (`--install`)|`$repo` unpinned → plist points at a worktree (**B-2**)|**Yes, permanently**|
|4 (`--install`)|`magistrate.lock` exists → abort with the plist already written (**S-2**)|Partly — the abort is loud, the residue is silent|
|5 (reaper `nohup`)|`git rev-parse` from the wrong cwd imports a different revision's `production_census`|**Yes**|
|5 (reaper)|Every recorded pid exits benignly between steps 3 and 5 → all `already_gone`, `verdict=pass` with nothing killed|**Yes** — indistinguishable from success|
|6 (observer reads the log)|Requires a human or a later session; the magistrate that started it is dead|N/A|
|6 (expect a tick to launch)|Generic-failure backoff delays it (**N-4**); B-3/B-2 prevent it entirely|**Yes**|

The recurring root is cwd: three of the four highest-consequence steps derive a
path from the current directory in a procedure that never sets one. Adding
`cd /Users/edr/code/JouleWise` to the top of the checklist and the canonical
refusal from B-2 removes most of this table.

## Priority (4): night plan writer vs installer vs gate

I checked for residual divergence across the four readers/writers and found
none that is load-bearing. `joulewise/night_plan_writer.py:15-27` builds the
mapping from `PLAN_SCHEMA`/`PLAN_SCHEMA_VERSION` + `dataclasses.asdict(plan)`
and then validates through `NightPlan.from_mapping` in the same function, so the
producer cannot emit a shape the consumer rejects — that is the right structure
and it closes AD-1/C-A. The three readers form a strict superset chain, as
documented at `MAGISTRATE_WATCHDOG.md:7`: watchdog (`from_mapping` + golden-shape
v1 identification + future-authorship) ⊇ installer (`from_mapping` + 36 h age +
future-authorship) ⊇ gate (`from_mapping` + 36 h + head probes + census). The
one asymmetry worth recording is not a divergence but a *duplication*: future
authorship is now checked in three places (`load_plans:663-667`,
`install_night_agent.sh`, and the gate) with three independently written error
strings. Since `night_plan_mapping` already exists as the one place producer and
consumer meet, the future-authorship limb belongs in `from_mapping` — a
should-fix-later, not a defect in this diff.

## Priority (6): usage-limit backoff during a window night

Behaviourally correct, with one exception which is B-3. `decide` reaches the
backoff gate at `:1197` only **after** the `active_plans` branch (`:1176-1188`)
and the fixed-fence branch (`:1193-1194`), so the doc's claim that "a new plan
fence always outranks backoff" (`MAGISTRATE_WATCHDOG.md:69`) is true by control
flow, not by comment. A 429 mid-window exits the session nonzero,
`classify_exit` matches `\bhttp\s+429\b` (`:105`) → `usage_exhausted` →
`USAGE_BACKOFF_S = (900, 1800, 3600, 7200, 7200)` plus activation-derived
jitter (`:1113-1114`). If that lands inside a plan span the tick returns
`FENCED`/`HOLD_CENSUS` rather than relaunching, which is right. The failure is
B-3: the *absolute monotonic* deadline this writes is the value that survives a
reboot and wedges the service.

---

## Same-signature statement

**NO** for the signature rounds 5 and 6 carried ("permitted tests green while a
production classification/control-flow path fails"): the five permitted modules
are green (E1) and the R-2 real-CLI gate does now cross `real_dependencies`.

**YES** for the *parent* signature the round-5 consult diagnosed — "the tests
are a restatement of the implementation rather than an independent statement of
the contract" — relocated one artifact over. B-2, S-2 and S-5 are all invisible
to `scripts/install_magistrate_watchdog.sh`'s only coverage, which is four
`assertIn` calls over its source text (B-4). The cure the consult specified for
the watchdog (a production-shaped subprocess test of the real entry point) was
never applied to the installer, and the installer is the artifact that executes
tonight. I record this for the cold gate alongside the Q-SIG carries from
rounds 5 and 6.

## Residual risk not covered by this review

I did not install, load, or bootstrap anything; I signalled no process, started
no session, and did not read or write `~/night-custody`. Every launchd claim
above is read from the template and the installer, not from a loaded service.
The live install, the first launchd-spawned `-p` session, the Gmail send, and
the twin kill remain unexercised by any seat.
