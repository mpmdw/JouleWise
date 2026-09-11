# 13 — Arm runbook: `rehearsal-20260912` (REHEARSAL_STUB), t0 2026-09-12 00:30 PDT

DRAFT / NOT ARMED. Prepared 2026-09-11 by an Opus drafter for the magistrate,
in the linked worktree `/Users/edr/code/JouleWise-wt-bk-58a3bcfc` at
`c935a79d`. Nothing in this file was executed against `~/night-custody`,
`launchctl`, `~/Library/LaunchAgents` or the network while drafting; the only
commands run were read-only inspections of the repository and stdlib
arithmetic, listed in §Fact table.

**Authority.** Cold-gate ruling
[`06-coldgate-ruling-item6.md`](06-coldgate-ruling-item6.md) §4(c), reading R1,
conditions C-1…C-9 and §7; Opus refuter [`07`](07-opus-refuter-item6.md);
harvest record [`01`](01-rehearsal-20260911-harvest-record.md) and retirement
record [`02`](02-rehearsal-20260911-uninstall-and-retirement.md); the
interpreter-cure brief [`03`](03-brief-NIGHT-INTERPRETER-PIN-01.md); D-175
(eight REHEARSAL_STUB arming conditions) and D-180. The executed templates this
file is modelled on are runbook
[`67`](../2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md)
and arm record
[`123`](../2026-09-09-rehearsal-harvest/123-rehearsal-20260911-arm-record.md)
with its
[`123-arm-evidence/`](../2026-09-09-rehearsal-harvest/123-arm-evidence/), plus
the real-install shape of runbook
[`68`](../2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md)
§Block A / §Block B. **This document applies those decisions to this night; it
adds no standing rule.**

---

## Terms, glossed before first use

- **LaunchAgent** — a macOS `launchd` job file (a `.plist` in
  `~/Library/LaunchAgents`) that tells the operating system's scheduler which
  program to run, with which arguments, at which wall-clock time. This night
  installs two of them: `com.joulewise.night` (the driver, at t0) and
  `com.joulewise.night.deadman` (the recovery job, at 07:00).
- **Driver** — `scripts/run_night.py`, the program the `com.joulewise.night`
  LaunchAgent starts at t0.
- **REHEARSAL_STUB** — the plan class whose "measurement" is the driver's
  built-in two-line command `/bin/zsh -c 'sleep 2; echo REHEARSAL'`
  (`run_night.py:1575`). No pack, no model, no `powermetrics`, no `sudo`.
- **Preflight** (new, from the cure) — running the driver's own imports and
  plan parse under *the exact interpreter the LaunchAgent will name*, before
  the LaunchAgent is installed, so that an interpreter defect fails at the
  desk instead of at t0. It prints one JSON line and must not touch the
  custody root, the census, `launchctl` or the network (record 03 §3).
- **Census** — running `/usr/bin/pgrep -lf 'codex|claude|t3'` and looking at
  what comes back. Two different rules use it and they are NOT the same rule;
  §Preconditions P6 states both.
- **Custody root** — the directory holding this night's records
  (`night_plan.json`, `night.log`, `night/`).
- **Measurement root** — the checkout both LaunchAgents are installed FROM and
  whose `WorkingDirectory` they carry. For a stub it is disposable.
- **Frozen triple** — `(plan_id, measurement_root, measurement_head)`, carried
  in the magistrate relaunch prompt until the night is harvested and retired
  (`docs/process/MAGISTRATE_WATCHDOG.md:102`).
- **Plan span** — the interval during which the watchdog refuses to launch a
  magistrate agent session because a night is imminent or running
  (`scripts/magistrate_watchdog.py:plan_span_active`). §Preconditions P2 gives
  this night's numbers.
- **Fixed fence** — two *wall-clock* windows in which the watchdog also refuses
  to launch, independent of any plan: `[02:45:00, 03:30:00)` and
  `[07:00:00, 07:01:00)` local (`magistrate_watchdog.py:local_fixed_fence`).

---

## Pins

`H′` (written `H_PRIME` in every command below, because a shell variable cannot
carry a prime) is the **main commit that carries all four of**: PR #321
(`NIGHT-INTERPRETER-PIN-01`) merged; the B-1 cure PR (finding B-1 of refuter
07, packet [`10`](10-packet-c1-registration-seam-B1.md)) merged; PR #320
(`EPOCH-CONTINUATION-01`) merged; and the `docs/process/NIGHT_HANDBACK.md`
rewrite for THIS night (§Step 0b). It is not today's `origin/main`
(`1dddcfea` at 08:30 PDT 09-11) and not a bookkeeping head.

| Pin | Value | Where it comes from |
|---|---|---|
| Plan id / class | `rehearsal-20260912` / `REHEARSAL_STUB` | ruling 06 C-4 (fresh id, never `rehearsal-20260911`) |
| Schema | `joulewise.night_plan.v2` + integer `schema_version: 2` | NIGHT_HANDBACK §Standing rules; emitted by the writer |
| t0 | 2026-09-12 **00:30:00 PDT**, epoch **1789198200** | ruling 06 VERDICT window `[1789196400, 1789200000]`; verified §Fact table A1 |
| `window_max_s` | **900** | ruling 06 C-4 |
| Window close | `t0 + 900` = **1789199100** (00:45:00 PDT) | arithmetic A2 |
| Courier deadline (completion epoch) | `t0 + 900 + 300` = **1789199400** (00:50:00 PDT) | `run_night.py:958–959`, `COURIER_DEADLINE_S = 300` (`run_night.py:51`) |
| Plan span opens | `t0 − 25 min` = **1789196700** (00:05:00 PDT) | `PLAN_LEAD_S = 25*60` (`magistrate_watchdog.py:67`) |
| Stand-down request / TERM / KILL | `t0 − 25 min` = 1789196700 / `t0 − 16 min` = 1789197240 / `t0 − 15 min` = 1789197300 | `REQUEST_LEAD_S`/`TERM_LEAD_S`/`KILL_LEAD_S` (`magistrate_watchdog.py:68–70`), `standdown_phase` (822–829) |
| **Arming-activation exit boundary** | **00:05:00 PDT 09-12**, epoch **1789196700** | the stand-down request lands here; ruling 06 C-6 |
| First (and only possible) dead-man firing | 2026-09-12 07:00:00 PDT, epoch 1789221600 | `DEADMAN_HOUR = 7` (`run_night.py:54`); 07:00 on 09-11 has already passed at install time |
| Results branch | `night-results/20260912` | `_night_date` names it from t0's LOCAL date (`run_night.py:538`) |
| Measurement root (disposable) | `/private/tmp/joulewise-rehearsal-20260912-checkout` | ruling 06 C-4 "fresh disposable checkout path (61 N3)" |
| Custody root | `/Users/edr/night-custody/rehearsal-20260912` | ruling 06 C-4 |
| `chain_path` / `chain_sha256_path` | `<custody_root>/chain.zsh` / `.sha256` — **never written** | C5 skips the read for `REHEARSAL_STUB` (`night_gate.py:1043–1052`) |
| `registration_path` | `<<REGISTRATION_PATH per ruling 12>>` — see §Step 0c | packet 10 is in a second cold gate |
| Both heads | `repo_head = measurement_head = H′` | installer pin checks (`install_night_agent.sh:81–96`) |
| Install time | evening of **2026-09-11 local**, after 07:00 PDT | ruling 06 C-5 |
| Installer calendar flags | `--hour 0 --minute 30` | the installer refuses only `--hour 7` (`install_night_agent.sh:112–115`) |

**Why t0 must be on or after 00:00 on 09-12, stated once.** `_night_date`
derives the results-branch name from t0's *local calendar date*. A t0 anywhere
on 09-11 would target `night-results/20260911`, which already exists on origin
at `37876416` (this morning's dead-man refusal — record 01). The driver's push
would be rejected non-fast-forward, `night.log` would carry
`durable record failed: …`, and the harvest could not tell that apart from a
real push defect. `night-results/20260912` does not exist; prove it, from the
worktree, with the `--exit-code` form (the bare form exits 0 even on no match):

```zsh
git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/night-results/20260912
# expected: no output, exit status 2  (0 with a line = the branch EXISTS: STOP)
```

---

## Preconditions (step 0) — each with the command that proves it

Set `DRIVER_SOURCE` first: it is **the arming activation's own authorized
linked bookkeeping worktree**, never the canonical checkout
`/Users/edr/code/JouleWise` (fenced: no Git operation there), and never the
disposable stub checkout. Every `git` command in this runbook that is not
inside the stub checkout runs with `-C "$DRIVER_SOURCE"`.

```zsh
: "${DRIVER_SOURCE:?the arming activation's authorized linked worktree}"
test "$DRIVER_SOURCE" != /Users/edr/code/JouleWise
git -C "$DRIVER_SOURCE" rev-parse --is-inside-work-tree
```

**P1 — the cure is merged and green at H′ (ruling 06 C-1).** PR #321 merged
into `main`; CI green; the defect-shaped tests of record 03 §5 (a)–(h) present
and passing on H′.

```zsh
git -C "$DRIVER_SOURCE" fetch origin main
git -C "$DRIVER_SOURCE" cat-file -e "$H_PRIME^{commit}"
test "$(git -C "$DRIVER_SOURCE" rev-parse "$H_PRIME^{commit}")" = "$H_PRIME"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H_PRIME" origin/main
# the cure is actually in H′, not merely adjacent to it:
git -C "$DRIVER_SOURCE" show "$H_PRIME:configs/launchd/com.joulewise.night.plist.template" | grep -Fq '@@PYTHON@@'
git -C "$DRIVER_SOURCE" show "$H_PRIME:configs/launchd/com.joulewise.night.plist.template" | grep -Fqv '/usr/bin/env'
git -C "$DRIVER_SOURCE" show "$H_PRIME:scripts/install_night_agent.sh" | grep -Fq -- '--python'
gh pr view 321 --json state,mergeCommit,statusCheckRollup
```

The unit run is executed once the stub checkout exists (§Block A step A4), from
that checkout, so the interpreter under test is the one the night will use:
`python3 -m unittest tests.test_install_night_agent tests.test_run_night` rc 0,
counts pasted into the arm record (ruling 06 C-1 requires the paste).

**P2 — the clock is right and we are outside every fence.** The install happens
on the evening of 09-11; the plan span for THIS plan does not open until
00:05 on 09-12, so publishing and installing tonight fences nothing.

```zsh
python3 -c '
from datetime import datetime
from zoneinfo import ZoneInfo
import time
Z = ZoneInfo("America/Los_Angeles")
now = time.time()
print("arm clock:", now, datetime.fromtimestamp(now, Z).isoformat())
assert datetime.fromtimestamp(1789198200).strftime("%Y-%m-%d %H:%M") == "2026-09-12 00:30", \
    "system local time differs from the pinned launchd time"
assert now > datetime(2026, 9, 11, 7, 0, tzinfo=Z).timestamp(), "install only after 07:00 PDT 09-11 (C-5)"
assert now < 1789196700, "at or beyond the 00:05 exit boundary"
local = datetime.fromtimestamp(now, Z)
sec = local.hour*3600 + local.minute*60 + local.second
assert not (2*3600+45*60 <= sec < 3*3600+30*60), "inside the 02:45-03:30 fixed fence"
assert not (7*3600 <= sec < 7*3600+60), "inside the 07:00 fixed fence"
'
```

**P3 — nothing is armed, no stand-down is requested, only the magistrate job is
loaded.** This is runbook 67's `preconditions.py`, reused verbatim below in
Block A; run as a precondition it must print
`launchctl list | grep joulewise: com.joulewise.magistrate` and
`foreign agent matches: []`.

**P4 — the retired night is fully gone (record 02 re-verified).**

```zsh
test ! -e /Users/edr/night-custody/rehearsal-20260911
test ! -e /private/tmp/joulewise-rehearsal-20260911-checkout
find /Users/edr/night-custody -maxdepth 2 -name night_plan.json    # expected: no output
launchctl list | grep -c 'com\.joulewise\.night'                   # expected: 0 (grep exits 1)
```

**P5 — the orphan daemon tree is gone (ruling 06 C-3, Ed-external).** Record 01
F2: pid 83102 `claude daemon run --origin transient`, children
83155/83180/83195/83220, plus `codex mcp-server` 83308/83319. This activation
may not signal it; Ed (or an interactive session) clears it.

```zsh
/bin/ps -axo pid=,ppid=,command= | /usr/bin/grep -E '^ *(83102|83155|83180|83195|83220|83308|83319) '
# expected: no output, grep exit 1.  Any output = STOP; do not arm; report to Ed.
```

**P6 — the census, and the exact rule that applies.** There are two rules and
they differ. State both in the arm record; do not conflate them.

1. **Arm-time census (this runbook).** Runbook 67 §Pins and preconditions,
   executed on 09-10 as record 123's Block A: the requirement is **no FOREIGN
   process**, where *own* means the arming activation's root PID (from
   `~/night-custody/magistrate/magistrate.lock`) and its currently attached
   descendants, proven by walking `ppid` chains; a prior activation, an
   interactive Claude/T3 session, another seat, a daemon, a spare, a pty host,
   a resumed twin, or an orphan reparented to PID 1 is **not** own. Record 123's
   Block A shows exactly this shape: census hits `18831`/`18848` (the
   activation's own `codex mcp-server` transport, ancestry `[.., 18817, 18814]`)
   with `foreign agent matches: []`. `pgrep` therefore exits **0**, not 1.
   *Ruling 06 C-3 is written as "`/usr/bin/pgrep -lf 'codex|claude|t3'` exits 1
   with empty stdout immediately before the install". Taken literally that is
   unsatisfiable by any live arming session — the session's own process matches
   the pattern. Its operative substance is D-175's eighth arming condition,
   "no OTHER agent session alive", and the ancestry form above is how "other"
   is decided in the only executed precedent. This runbook uses the ancestry
   form, adds P5's explicit orphan check, and records the substitution.*
   D-180 clause 3 ("idle interactive sessions are not foreign at the arm-time
   census of stub nights") is **ratified but not installed** — lane
   `ARM-CENSUS-IDLE-INTERACTIVE-01`, "decided ≠ done" — so tonight an idle
   *foreign* interactive session is still an abort, and D-180 clause 2's
   pre-authorized retry class is what covers retrying after it closes.
2. **Production census (the night itself).** `night_gate.agent_census`
   (`joulewise/night_gate.py:498–526`) runs
   `AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")` at t0 and
   every 30 s during acquisition, and passes **only** on
   `exit_code == 1 and stdout.strip() == ""`. There is no ancestry exemption in
   that code, and D-180 clause 3 explicitly leaves the plan span unchanged.
   **Consequence for tonight: any agent process alive at 00:30 on 09-12 refuses
   the night with `night_refused_agent_present`.** That is why the arming
   activation must exit by 00:05 with no own background work, and why no
   interactive session may be left open through t0.

**P7 — a ≥ 3.11 interpreter exists to build the stub venv from.**

```zsh
/opt/homebrew/bin/python3.13 --version        # observed at the desk 2026-09-11: Python 3.13.1
env -i PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/env python3 --version
# observed: Python 3.9.6 — this is the defect the cure closes; it is recorded, not used.
```

---

## Step 0a — what must be true about H′ before it is cut

H′ is a reviewed direct-to-`main` commit (or merge) carrying, in this order:

1. PR #321 `NIGHT-INTERPRETER-PIN-01` — the template's `@@PYTHON@@`
   placeholder, the installer's `--python ABS_PATH` with its default
   derivation, and `run_night.py preflight`.
2. The B-1 cure PR for the C1 registration seam (packet 10 / ruling 12).
3. PR #320 `EPOCH-CONTINUATION-01`.
4. The `docs/process/NIGHT_HANDBACK.md` rewrite of §Step 0b.

PR #320 is **not** required by ruling 06 for this stub — C-1 names only the
interpreter cure — but folding it into H′ costs nothing and keeps a single head
for tonight's stub and tomorrow morning's equivalence-night arm. If PR #320 is
not ready by the time the handback rewrite is committed, drop it from H′ and
record that; it changes nothing about this night.

## Step 0b — the NIGHT_HANDBACK rewrite, verbatim (R-9; ruling 06 MATERIAL finding)

`docs/process/NIGHT_HANDBACK.md` is what the night courier reads first. Its
§Purpose, §Where the results are and §Next lane still describe
`rehearsal-20260911`, which was harvested and retired this morning (records 01
and 02). R-9 requires the magistrate to rewrite those three sections before
every armed night, and to commit the rewrite with the night's plan — that
commit **is** H′, which is why the handback text below says "this commit"
rather than a hash.

Replace the existing `## Purpose of this night` section (currently lines 42–81)
with exactly:

```markdown
## Purpose of this night

Plan `rehearsal-20260912`, class `REHEARSAL_STUB`, is planned for
2026-09-12 at 00:30:00 PDT (`t0`, epoch 1789198200), with a 900-second
window. The courier deadline is `t0 + 900 + 300`, epoch 1789199400,
00:50:00 PDT that morning. The driver runs its built-in stub,
`sleep 2; echo REHEARSAL`: no pack, no model, no measurement, no sudo.
This notice describes the planned night; the arm record establishes
whether installation happened.

`rehearsal-20260911` is RETIRED: its night never ran. At 02:56 PDT on
2026-09-11 macOS's job scheduler started the driver with the Command Line
Tools Python 3.9, and the driver crashed on its first import before any
census, gate or stub ran; the 07:00 dead-man then refused on an orphaned
agent process. Harvest record
`docs/process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md`
and retirement record `02-…-uninstall-and-retirement.md` hold the evidence.
Acceptance item 5 is MET on that night; item 6 is NOT.

This third stub night exists for acceptance item 6 alone. Since PR #309 no
launchd-started driver has reached night-gate rows C1, C4 or the tail of C3:
the 09-09 night stopped at the C5 chain read and the 09-11 night never
started. This night runs those rows live, on a head carrying the interpreter
cure, and fires the cured job file's executable line under launchd for the
first time. Cold-gate ruling
`docs/process_traces/2026-09-11-activation-58a3bcfc/06-coldgate-ruling-item6.md`
§4(c) authorises the off-convention t0 and lists conditions C-1…C-9; its
fallback is a 02:56 stub on 09-13. Item 5 needs nothing from this night, so
the day-before 03:00–06:30 install span does not apply: the agents are
installed on the evening of 2026-09-11, after 07:00 PDT and after 00:30 has
passed that day, so the night agent's first firing IS t0. Both agents are
uninstalled at harvest, before 07:00 on 09-12, so the 07:00 dead-man never
fires; if uninstallation slips past 07:00 it takes the `courier already sent`
branch and is harmless.

`repo_head = measurement_head = H`, where H is **this commit**, the main
commit that rewrites this handback for this night. The disposable detached
checkout at H is `/private/tmp/joulewise-rehearsal-20260912-checkout`, and it
carries a `.venv` whose `bin/python` is Python 3.13 — the interpreter the two
LaunchAgents name by absolute path. Both night agents are installed from that
checkout. It is used only by this stub and is removed with the plan root after
harvest; it is never reused for a real plan.

The consolidated notice with these pins is sent after commit H and before the
plan is moved into place. Ed's NO on the notice thread stands the night down.
The arming activation exits after recording the arm. The watchdog's plan span
opens, and its stand-down request lands, at 00:05:00 PDT on 09-12
(epoch 1789196700, `t0 − 25 minutes`); TERM is `t0 − 16 minutes`
(1789197240) and KILL is `t0 − 15 minutes` (1789197300). The fixed
02:45–03:30 belt does not touch this night. Power source, powermode and the
timer probe are recorded at arm time. Powermode is recorded, not gated, for
this stub; a green stub says nothing about the capture-timeout seam.
```

Replace `## Where the results are` (currently lines 102–113) with exactly:

```markdown
## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260912`; records in
  `night/` — `result.json` (expected verdict `REHEARSAL_ONLY`,
  `chain_exit_code` 0), `receipt.json` or `refusal.json` as `result.json`
  directs, `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`,
  `courier.json`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260912/night.log`.
  At harvest, look for `night driver started` and a `night gate verdict=`
  line. There is no pre-night dead-man firing on this night, by design.
- Launchd streams: `night/launchd.night.out` and `night/launchd.night.err`.
  `launchd.night.err` must be EMPTY; the 2026-09-11 traceback signature in it
  is the defect this night exists to disprove.
- Results branch: `night-results/20260912` on `origin`, if the driver's push
  succeeded — verify, do not presume.
```

Replace `## Next lane for rehearsal-20260911` (currently lines 115–144) with
exactly:

```markdown
## Next lane for rehearsal-20260912

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260912` / `/private/tmp/joulewise-rehearsal-20260912-checkout`
/ this commit) harvests `result.json`, the receipt or refusal, the courier
message id and the results-branch evidence, and records them under
`NIGHT-REHEARSAL-01` item 6. Acceptance requires `receipt.json` verdict
`REHEARSAL_ONLY` with C1/C3/C4/C5 PASS and C2 `NOT_APPLICABLE`
(`no_pack_by_design`); C1 carrying a measured `registration_sha256`; C3
carrying measured `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`,
`load_average_raw` and `thermal_raw`; C4 carrying the boot-UUID and
epoch/monotonic pair; C5 recording `chain_stub: built_in_stub_by_design` with
null `chain_sha256` and `expected_chain_sha256`; `result.json`
`REHEARSAL_ONLY` with `chain_exit_code` 0; and `launchd.night.err` empty.
The stub's launchd exit status 3 is not a receipt-refusal signal.

A receipt refusing `night_refused_agent_present`, `night_refused_not_quiet`
or `night_refused_hid_idle` is a CORRECT refusal — the rows ran and refused —
and discharges nothing for item 6; the fallback route of ruling 06 §4(c) C-9
follows. Any `night_probe_error`, crash, non-empty `launchd.night.err`, or
refusal of any other kind is a finding to cure before any plan.

After preserving the evidence, and BEFORE the equivalence night's install
begins at 03:00 PDT on 09-12, the magistrate runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260912/night_plan.json --hour 0 --minute 30 --uninstall`
FROM the stub checkout, then removes the stub checkout
(`git worktree remove`) and the plan root. Never re-arm this plan, and never
reuse this stub root for a real plan.
For every v2 plan, run `scripts/install_night_agent.sh` FROM the checkout
named by the plan's `measurement_root`, with that checkout at the plan's
`measurement_head`; never install the two night agents from the development
checkout. Once authored, every armed plan's canonical
`(plan_id, measurement_root, measurement_head)` is included in the magistrate
relaunch prompt's frozen-checkout list until completion.
```

**One more handback edit the cure's doc clause must not leave wrong** (ruling
06 §9 MATERIAL). The G2-a routing paragraph currently reads "There is no v2
interpreter field: the driver, chain, and preflight always derive
`<measurement_root>/.venv/bin/python`" (lines 166–169). That sentence is true
of the **chain** and of the new **preflight**, and was *false of the driver*
until PR #321: before the cure the driver was whatever `python3` the
LaunchAgent's `PATH` resolved to. Ensure H′'s version of that paragraph says
which of the three was pinned when, and does not imply the driver was already
pinned. Verify after the rewrite:

```zsh
git -C "$DRIVER_SOURCE" show "$H_PRIME:docs/process/NIGHT_HANDBACK.md" | grep -n 'rehearsal-20260911'
# expected: only the retirement sentence and the dated history section may name it.
git -C "$DRIVER_SOURCE" show "$H_PRIME:docs/process/NIGHT_HANDBACK.md" | grep -n 'rehearsal-20260912'
```

## Step 0c — the `registration_path` placeholder and the one-line rule for filling it

> **PLACEHOLDER — `<<REGISTRATION_PATH per ruling 12>>`.**
> A second cold gate (packet [`10`](10-packet-c1-registration-seam-B1.md),
> ruling 12) is deciding which document the *equivalence* night's row C1 must
> bind to: `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`
> (as on every night to date) or
> `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. Do not guess.

**The rule for filling it, in one line:** set `registration_path` to the file
in the stub checkout whose SHA-256 equals the `D166_REGISTRATION_SHA256`
constant compiled into **H′'s** `joulewise/night_gate.py`, because row C1 for
`receipt_class == "REHEARSAL_STUB"` hashes that file's UTF-8 bytes and refuses
`night_refused_registration` on any other digest (`night_gate.py:1300–1328`).

Fill and prove it mechanically, from the stub checkout, in Block A:

```zsh
cd "$STUB_CHECKOUT"
python3 -B - <<'PY'
import hashlib
from pathlib import Path
from joulewise.night_gate import D166_REGISTRATION_PATH, D166_REGISTRATION_SHA256
candidate = Path(D166_REGISTRATION_PATH)
digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
print('registration_path =', D166_REGISTRATION_PATH)
print('sha256            =', digest)
print('constant          =', D166_REGISTRATION_SHA256)
assert digest == D166_REGISTRATION_SHA256, 'C1 would refuse night_refused_registration'
PY
```

At the desk on 2026-09-11 that path is
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`
with digest
`dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` (packet 10
F1/F2). If ruling 12's cure changes C1's semantics in H′, the block above
follows the change automatically — it reads the constant, it does not hard-code
it. Pass the value **relative to the measurement root**, as runbook 67 did: the
gate reads it through the driver's probe adapter with `WorkingDirectory` set to
the measurement root.

---

## Block A — checkout, venv, staged authoring, render-only (steps 1–3)

Use foreground `zsh` tool calls. Tool-shell exports do not persist, so set
`H_PRIME` and `DRIVER_SOURCE` at the top of **each** block. Both
`/private/tmp` staging directories are deliberately outside the watchdog's
discovery glob `~/night-custody/*/night_plan.json`
(`MAGISTRATE_WATCHDOG.md:21`), so authoring the plan does not arm the night;
publication in Block B is the only moment it becomes discoverable.

### A1 — exports and preconditions

```zsh
set -euo pipefail
: "${H_PRIME:?Set H_PRIME to the full committed handback hash from the notice}"
: "${DRIVER_SOURCE:?the arming activation's authorized linked worktree}"
export H_PRIME DRIVER_SOURCE
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260912
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
export PYTHONDONTWRITEBYTECODE=1
test "$DRIVER_SOURCE" != /Users/edr/code/JouleWise
for p in "$STAGE" "$SCRATCH" "$STUB_CHECKOUT" "$NIGHT_CUSTODY"; do
  test ! -e "$p"
  test ! -L "$p"
done
mkdir "$STAGE" "$SCRATCH"
# Capture foreground output, including failures; a missing final rc=0 is not success.
exec > >(tee "$STAGE/arm-blockA-output.txt") 2>&1
cat > "$STAGE/preconditions.py" <<'PY'
import json, os, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

zone = ZoneInfo("America/Los_Angeles")
now = time.time()
print("arm clock:", now, datetime.fromtimestamp(now, zone).isoformat(), flush=True)
# C-5: install on 2026-09-11 local, after 07:00 PDT, and after the chosen
# hour:minute (00:30) has already passed that day -- trivially true for hour 0.
assert now > datetime(2026, 9, 11, 7, 0, tzinfo=zone).timestamp(), "before 07:00 PDT 09-11"
assert now < 1789196700, "at or beyond the 00:05 PDT 09-12 exit boundary"
assert datetime.fromtimestamp(1789198200).strftime('%Y-%m-%d %H:%M') == '2026-09-12 00:30', 'system local time differs from the pinned launchd time'
local = datetime.fromtimestamp(now, zone)
second = local.hour * 3600 + local.minute * 60 + local.second
assert not (2*3600 + 45*60 <= second < 3*3600 + 30*60), "inside the 02:45-03:30 fixed fence"
assert not (7*3600 <= second < 7*3600 + 60), "inside the 07:00 fixed fence"
parent = Path('/Users/edr/night-custody')
stop = parent/'magistrate/standdown.request'
assert not stop.exists() and not stop.is_symlink(), "standdown requested"
assert not list(parent.glob('*/night_plan.json')), "existing plan"
services = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True)
matches = [line for line in services.stdout.splitlines() if 'joulewise' in line]
print('launchctl list | grep joulewise:', *matches, sep='\n', flush=True)
assert [line.split()[-1] for line in matches] == ['com.joulewise.magistrate']
# Own = the arming activation's root PID and its currently attached descendants.
# Default: the magistrate lock's PID. ARM_OWNER_PID overrides it ONLY when this
# session is not the lock's owner; the override and its reason go in the record.
override = os.environ.get('ARM_OWNER_PID')
me = int(override) if override else json.loads((parent/'magistrate/magistrate.lock').read_text())['pid']
print('own root pid:', me, '(override)' if override else '(magistrate.lock)', flush=True)
raw = subprocess.run(['ps', '-axo', 'pid=,ppid=,command='], capture_output=True, text=True, check=True).stdout
rows = {int(a): (int(b), c) for line in raw.splitlines() if line.strip()
        for a, b, c in [line.strip().split(None, 2)]}
def ancestors(pid):
    seen = set()
    while pid in rows and pid != 1 and pid not in seen:
        seen.add(pid)
        yield pid
        pid = rows[pid][0]
assert me in set(ancestors(os.getpid())), 'own root PID is not this census ancestor'
probe = subprocess.run(['/usr/bin/pgrep', '-lf', 'codex|claude|t3'], capture_output=True, text=True)
print('pgrep -lf "codex|claude|t3" rc=', probe.returncode, flush=True)
print(probe.stdout, end='', flush=True)
print(probe.stderr, end='', flush=True)
assert probe.returncode in (0, 1), 'census failed'
hits = [int(line.split(None, 1)[0]) for line in probe.stdout.splitlines() if line.strip()]
foreign = [pid for pid in hits if me not in set(ancestors(pid))]
for pid in hits:
    print('census ancestry:', pid, list(ancestors(pid)), rows.get(pid), flush=True)
print('foreign agent matches:', foreign, flush=True)
assert not foreign, 'foreign or unclassifiable process; preserve it and abort'
# Record 01 F2: the orphan tree must be gone before any arm (ruling 06 C-3).
orphans = [pid for pid in (83102, 83155, 83180, 83195, 83220, 83308, 83319) if pid in rows]
print('record-01 F2 orphan pids still present:', orphans, flush=True)
assert not orphans, 'the 83102 orphan tree is alive; Ed must clear it before arming'
PY
python3 -B "$STAGE/preconditions.py"
```

The census parser fails closed on any line it cannot parse — that is what
happened on 09-10 at 04:09:42 (record 123): a multi-line own keepalive Monitor
made `int(line.split()[0])` raise `ValueError`. **Do not weaken the parser or
filter a line to make the census pass.** Run §Step 3b's own-background stop
*before* this block, not only before Block B (record 123's FINDING for the
runbook owner; runbook 68 step 5 repeats it).

### A2 — H′ reachability and the handback read-back

```zsh
git -C "$DRIVER_SOURCE" fetch origin main
git -C "$DRIVER_SOURCE" cat-file -e "$H_PRIME^{commit}"
test "$(git -C "$DRIVER_SOURCE" rev-parse "$H_PRIME^{commit}")" = "$H_PRIME"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H_PRIME" "$remote_main_head"
git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/night-results/20260912 && {
  print 'ABORT: night-results/20260912 already exists' >&2; exit 1
} || true
git -C "$DRIVER_SOURCE" show "$H_PRIME:docs/process/NIGHT_HANDBACK.md"
# Inspect the displayed handback against the sent notice before continuing.
```

### A3 — cut the disposable checkout at H′

```zsh
git -C "$DRIVER_SOURCE" worktree add --detach "$STUB_CHECKOUT" "$H_PRIME"
test "$(git -C "$STUB_CHECKOUT" rev-parse HEAD)" = "$H_PRIME"
test -z "$(git -C "$STUB_CHECKOUT" status --short)"
```

*Route note.* Ruling 06 C-2 says "stub clone"; this uses a **linked worktree**,
which is the route runbook 67 specified, record 123 executed and record 02
retired with `git worktree remove`. The fresh-`git clone` recipe of runbook 68
§"Fresh clone at H" exists because a *measurement* root carries an editable
install whose absolute paths break on rename; a stub has no editable install
and needs none. The substitution is recorded here rather than made silently.

### A4 — the `.venv`, and the interpreter the LaunchAgents will name

The exact venv-creation commands are **not** in
`docs/phase_2/derivation_night_runbook.md` §0.2. §0.2 says "Build the clone's
virtual environment from the lock, then export the one interpreter every desk
step in this runbook uses", but its code block only *exports and checks*:

```zsh
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
test -x "$PY"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' "$MEASUREMENT_ROOT/env/mac-measurement-lock.txt" | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
```

and defers the creation to record 12 (runbook 68) §"Fresh clone at H", whose
exact commands are:

```zsh
python3.13 --version
# Expected reviewed interpreter: Python 3.13.1.
python3.13 -m venv .venv
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt -e ".[mac]"
.venv/bin/python -m pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3
```

**For this stub, run only the `venv` creation, not the two `pip install`
lines, and skip §0.2's lock `diff`.** The reason, stated so it can be checked
rather than trusted: every module the driver's `run`, `dead-man` and `rehearse`
paths import — `joulewise.night_gate`, `joulewise.arm_readiness`,
`joulewise.arm_readiness_evidence_t0`, `joulewise.t0_rehearsal` — imports only
the standard library at module scope (verified at the desk, §Fact table A6),
and `run_night.py:27–29` puts the repository root on `sys.path` itself, so the
project package needs no installation. The `mac` extra installs `mlx` and the
measurement stack, which a `sleep 2; echo REHEARSAL` stub never touches, and it
would take the arm outside its evening budget. §0.2's lock `diff` compares
`pip freeze` against the measurement lock and would therefore FAIL on this bare
venv by construction; it is **not applicable** to a stub and must not be run as
if it were. The real evidence that the venv is sufficient is the preflight in
A6, which fails closed with exit 2 if any driver import is missing.

```zsh
cd "$STUB_CHECKOUT"
/opt/homebrew/bin/python3.13 --version
/opt/homebrew/bin/python3.13 -m venv .venv
export PY="$STUB_CHECKOUT/.venv/bin/python"
test -x "$PY"
"$PY" -c 'import sys; print(sys.executable, sys.version); assert sys.version_info[:2] >= (3, 11)'
# .venv/ is gitignored (.gitignore:6), so the tree stays clean:
test -z "$(git -C "$STUB_CHECKOUT" status --short)"
python3 -m unittest tests.test_install_night_agent tests.test_run_night
```

**Do not pass `--python` to the installer.** Rely on the cure's default
derivation. Reasons, in order: (1) with no `--python`, the installer extracts
`measurement_root` from the plan with `/usr/bin/plutil -extract` — no Python at
all — and derives `<measurement_root>/.venv/bin/python`, refusing with exit 2
and a message naming the missing path if it is absent or not executable
(`install_night_agent.sh:47–58` on the cure branch); that is exactly the path
the real equivalence night will take, so exercising it here is the point of the
night; (2) passing `--python` would take the explicit branch and leave the
derivation branch unexercised under launchd for the first time on the real
night; (3) `--python` combined with `--uninstall` is a usage error
(`(( uninstall && python_given )) && usage`), so the uninstall command in the
harvest stays flag-free either way.

### A5 — author the real plan at staging, and its validation twin at scratch

```zsh
cd "$STUB_CHECKOUT"
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import hashlib, os, time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH, D166_REGISTRATION_SHA256
from joulewise.night_plan_writer import write_night_plan

root = Path(os.environ['NIGHT_CUSTODY'])
stage = Path(os.environ['STAGE'])
scratch = Path(os.environ['SCRATCH'])
t0 = datetime(2026, 9, 12, 0, 30, tzinfo=ZoneInfo('America/Los_Angeles')).timestamp()
assert t0 == 1789198200
assert 1789196400 <= t0 <= 1789200000, 'outside cold-gate 06 C-4 window'
now = time.time()
assert now < t0 - 25 * 60, 'past the exit boundary'
assert 0 <= t0 - now <= 36 * 3600, 'authored_epoch_s must be within 36 h of t0'
# Step 0c: C1 hashes this file and refuses anything else.
registration = D166_REGISTRATION_PATH
digest = hashlib.sha256(Path(registration).read_bytes()).hexdigest()
assert digest == D166_REGISTRATION_SHA256, (registration, digest, D166_REGISTRATION_SHA256)
print('registration_path:', registration, digest)
plan = NightPlan(plan_id='rehearsal-20260912', receipt_class='REHEARSAL_STUB',
    t0_epoch_s=t0, window_max_s=900, authored_epoch_s=now,
    repo_head=os.environ['H_PRIME'], measurement_head=os.environ['H_PRIME'],
    measurement_root=os.environ['STUB_CHECKOUT'], custody_root=str(root),
    chain_path=str(root/'chain.zsh'), chain_sha256_path=str(root/'chain.zsh.sha256'),
    registration_path=registration)
twin_root = scratch/'custody'
twin = replace(plan, custody_root=str(twin_root), chain_path=str(twin_root/'chain.zsh'),
               chain_sha256_path=str(twin_root/'chain.zsh.sha256'))
print(write_night_plan(stage/'night_plan.json', plan))
print(write_night_plan(scratch/'night_plan.json', twin))
PY
```

`chain.zsh` is never written: for `REHEARSAL_STUB` the gate's C5 row records
`chain_stub: built_in_stub_by_design` with null digests instead of reading the
file (`night_gate.py:1043–1052`, PR #309). The two path fields are still
required plan fields, so they are set and left non-existent.

`joulewise.night_plan_writer` exposes `write_night_plan` as a **function only**
— it has no CLI parser or `main`, so `python3 -m joulewise.night_plan_writer` is
not a plan-authoring command (runbook 67 §Block A).

### A6 — render-only against the TWIN, and the preflight paste lines

```zsh
cd "$STUB_CHECKOUT"
scripts/install_night_agent.sh --plan "$SCRATCH/night_plan.json" --hour 0 --minute 30 --render-only "$SCRATCH/render"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.plist"
/usr/bin/plutil -lint "$SCRATCH/render/com.joulewise.night.deadman.plist"
python3 -B - <<'PY'
import json, os, plistlib
from pathlib import Path
render = Path(os.environ['SCRATCH'])/'render'
py = os.environ['PY']
for label, mode, hour, minute in [('com.joulewise.night', 'run', 0, 30),
                                  ('com.joulewise.night.deadman', 'dead-man', 7, 0)]:
    data = plistlib.loads((render/(label+'.plist')).read_bytes())
    print(label, 'calendar=', data['StartCalendarInterval'],
          'ProgramArguments=', data['ProgramArguments'], flush=True)
    assert data['StartCalendarInterval'] == {'Hour': hour, 'Minute': minute}
    assert data['RunAtLoad'] is False
    argv = data['ProgramArguments']
    # Ruling 06 C-2: the cured shape.
    assert argv[0] == py, (argv[0], py)
    assert argv[0].startswith('/')
    assert '/usr/bin/env' not in argv and 'python3' not in argv
    assert argv[1] == str(Path(os.environ['STUB_CHECKOUT'])/'scripts/run_night.py')
    assert argv[2] == mode
PY
python3 -B - <<'PY'
import json, os
from pathlib import Path
real = json.loads((Path(os.environ['STAGE'])/'night_plan.json').read_bytes())
twin = json.loads((Path(os.environ['SCRATCH'])/'night_plan.json').read_bytes())
diff = {k for k in real.keys() | twin.keys() if real.get(k) != twin.get(k)}
print('plan differing fields:', sorted(diff))
assert diff == {'custody_root', 'chain_path', 'chain_sha256_path'}
assert real['schema'] == 'joulewise.night_plan.v2' and real['schema_version'] == 2
assert not Path(os.environ['NIGHT_CUSTODY']).exists()
PY
print 'block A rc=0'
```

`--plan` names the **staged validation twin**, not the real staged plan: even
`--render-only` executes `mkdir -p "$custody_root/night"`
(`install_night_agent.sh:123–125`), and the twin keeps that write inside
`$SCRATCH`. Its only differing fields must be the three printed custody paths.
The real plan is revalidated during the install itself.

**Two paste lines the arm record must carry (ruling 06 C-2).** Both appear in
`arm-blockA-output.txt`; copy them verbatim into the record:

1. The **preflight JSON line**, printed by the installer before rendering. The
   installer runs it as
   `/usr/bin/env -i PATH="$courier_path" HOME="$HOME" "$python" -B "$repo/scripts/run_night.py" preflight --plan "$plan"`
   — i.e. under the same stripped environment the LaunchAgent gets — and
   refuses the install with exit 2 if it is non-zero
   (`install_night_agent.sh:152–154` on the cure branch). Its shape is
   `{"preflight": "ok", "python": "…/.venv/bin/python", "version": "3.13.1", "modules": [...]}`
   (record 03 §3).
2. The rendered **`ProgramArguments`** of both plists, from the block above.

If the preflight fails here it has done its job: the bare venv is insufficient.
Escalation, in order: re-create the venv and run the two `pip install` lines of
runbook 68 quoted in A4; if that still fails, do not arm — record the failure
and take fallback (a).

---

## Step 3b — own background work stopped (between blocks)

Stop **all** own delegated seats, background jobs and keepalive work with the
session's own task controls, and record the actual task IDs and their results;
never invent a `TaskStop` id or a retired PID. Record 123's 04:09:42 entry is
the worked example of why this runs **before Block A as well**: a multi-line
own keepalive command broke the census parser and aborted the first attempt.

```zsh
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'
```

A no-match `grep` exit 1 is the expected result, not a failure to hide. Classify
any match by ancestry; a foreign, indeterminate or orphaned match aborts the
arm. **Do not signal foreign processes.** After 3b, complete Block B, the
record, the push and the exit in the same turn.

---

## Block B — notice, final census, publish, install, inspect (steps 4–7)

### B1 — re-establish pins and record arm-time readings

```zsh
set -euo pipefail
: "${H_PRIME:?Set the same full committed handback hash as Block A}"
: "${DRIVER_SOURCE:?the arming activation's authorized linked worktree}"
export H_PRIME DRIVER_SOURCE
export STUB_CHECKOUT=/private/tmp/joulewise-rehearsal-20260912-checkout
export NIGHT_CUSTODY=/Users/edr/night-custody/rehearsal-20260912
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
export PY="$STUB_CHECKOUT/.venv/bin/python"
export PYTHONDONTWRITEBYTECODE=1
test -f "$STAGE/night_plan.json"
exec > >(tee "$STAGE/arm-blockB-output.txt") 2>&1
grep -Fx 'block A rc=0' "$STAGE/arm-blockA-output.txt"
cd "$STUB_CHECKOUT"
test "$(git rev-parse HEAD)" = "$H_PRIME"
test -z "$(git status --short)"
test -x "$PY"
remote_main="$(git -C "$DRIVER_SOURCE" ls-remote --exit-code origin refs/heads/main)"
remote_main_head="${remote_main%%$'\t'*}"
git -C "$DRIVER_SOURCE" merge-base --is-ancestor "$H_PRIME" "$remote_main_head"
test ! -e "$NIGHT_CUSTODY"
test ! -L "$NIGHT_CUSTODY"
pmset -g batt
pmset -g custom
python3 -c "import time; t=time.perf_counter(); [time.sleep(0.05) for _ in range(20)]; print((time.perf_counter()-t)/20)"
print 'Powermode recorded, not gated for this stub. A green stub says nothing about the capture-timeout seam.'
test "$(stat -f %d "$STAGE")" = "$(stat -f %d /Users/edr/night-custody)"
date '+notice-preparation epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
```

The power and timer readings are arm-time observations, recorded and not gated
for a stub (runbook 67 §Block B; the timer argv is from
`44-coldgate-charge-replay-verdict.md:5`). The device-number equality is a
precondition for B4's atomic `os.replace`, which cannot cross filesystems.

### B2 — send Ed the NIGHT_HANDBACK notice, THEN arm (D-175 condition 1)

Send the consolidated notice now, under the activation's standing email
authority, after H′ exists and **before** the plan is moved into place. Include:
plan id and class; H′ twice (as `repo_head` and `measurement_head`); the
measurement root and custody root; t0 local and UTC with its epoch; 900 s;
the 00:50 PDT courier deadline; the 00:05 PDT exit boundary; the
`night-results/20260912` results branch; the planned install time; the fact
that the dead-man never fires because the agents are removed before 07:00; the
cold-gate authority (ruling 06 §4(c)) and ruling 06 §8's paragraph for Ed; and
explicit cancellation instructions — **launch needs no action from Ed unless he
replies NO.** Ruling 06 §7 additionally requires Ed's non-veto of reading R1 on
this thread.

Write the actual acceptance evidence — message id, thread id, accepted send
time — to `$STAGE/notice-evidence.txt` before continuing. A headless activation
cannot re-read the thread; say so rather than certifying that no unseen reply
exists (synthesis 65's limitation, recorded as such in record 123's NO-channel
row). Recheck owner-authored open `directive` issues and any relayed NO
immediately before publication.

```zsh
test -s "$STAGE/notice-evidence.txt"
cat "$STAGE/notice-evidence.txt"
```

### B3 — final census immediately before publication

```zsh
python3 -B "$STAGE/preconditions.py"
```

This is the same script Block A ran; running it again here is the point — it
re-asserts the clock, the exit boundary, the fixed fences, the absent
stand-down, the absent discoverable plan, the only-magistrate `launchctl` list,
the no-foreign-process census and the absent 83102 orphan tree, at the last
moment before the night becomes real.

### B4 — publish atomically, then install FROM the stub checkout

```zsh
cd "$STUB_CHECKOUT"
mkdir -p "$NIGHT_CUSTODY"
python3 -c 'import os,sys; os.replace(sys.argv[1], sys.argv[2]); print("moved", sys.argv[2])' "$STAGE/night_plan.json" "$NIGHT_CUSTODY/night_plan.json"
cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/arm-night_plan.json"
date '+install-start epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
if ! scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 0 --minute 30; then
  print 'ABORT: install failed after publication; preserve this transcript'
  scripts/install_night_agent.sh --plan "$NIGHT_CUSTODY/night_plan.json" --hour 0 --minute 30 --uninstall
  cp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/failed-night_plan.json"
  rm "$NIGHT_CUSTODY/night_plan.json"
  exit 1
fi
date '+install-end epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
```

Do not replace a failed cross-device move with a copy; B1's `stat -f %d` check
is what makes the rename possible. On success the installer prints
`validated pins: repo_head=… measurement_root=… measurement_head=…`; it
compares `repo_head` against the driver-checkout HEAD and `measurement_head`
against the HEAD of `measurement_root`, and its exact refusal strings are
`plan repo_head does not match driver checkout HEAD` and
`plan measurement_head does not match measurement checkout HEAD`
(`install_night_agent.sh:81–96`). Rendering and installing prove paths, pins,
schema, age, courier, calendar and — now — the interpreter; **none of it proves
the live night gate passes.**

### B5 — inspect the installed state and take the `night/` baseline

```zsh
launchctl list | grep joulewise
python3 -B - <<'PY'
import json, os, plistlib, subprocess, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
root = Path(os.environ['STUB_CHECKOUT'])
plan = str(Path(os.environ['NIGHT_CUSTODY'])/'night_plan.json')
py = os.environ['PY']
rows = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, check=True).stdout
labels = {line.split()[-1] for line in rows.splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
for label, mode, hour, minute, stem in [
        ('com.joulewise.night', 'run', 0, 30, 'launchd.night'),
        ('com.joulewise.night.deadman', 'dead-man', 7, 0, 'launchd.deadman')]:
    p = Path('/Users/edr/Library/LaunchAgents')/(label+'.plist')
    data = plistlib.loads(p.read_bytes())
    print(label, 'calendar=', data['StartCalendarInterval'], 'program=', data['ProgramArguments'],
          'cwd=', data['WorkingDirectory'], flush=True)
    assert data['StartCalendarInterval'] == {'Hour': hour, 'Minute': minute}
    assert data['WorkingDirectory'] == str(root)
    argv = data['ProgramArguments']
    assert argv[0] == py and argv[0].startswith('/')
    assert '/usr/bin/env' not in argv and 'python3' not in argv
    assert argv[1:5] == [str(root/'scripts/run_night.py'), mode, '--plan', plan]
    assert data['RunAtLoad'] is False
    assert data['StandardOutPath'] == str(Path(os.environ['NIGHT_CUSTODY'])/'night'/(stem+'.out'))
    assert data['StandardErrorPath'] == str(Path(os.environ['NIGHT_CUSTODY'])/'night'/(stem+'.err'))
now = time.time()
assert now < 1789196700, 'past the 00:05 PDT exit boundary'
print('install verified epoch=', now, datetime.fromtimestamp(now, ZoneInfo('America/Los_Angeles')).isoformat(), flush=True)
print('expected: night t0=1789198200 (2026-09-12 00:30 PDT); window close=1789199100; '
      'courier deadline=1789199400 (00:50 PDT); plan span opens=1789196700 (00:05 PDT); '
      'dead-man would be 1789221600 (09-12 07:00) but the agents are removed first', flush=True)
PY
cp /Users/edr/Library/LaunchAgents/com.joulewise.night.plist "$STAGE/arm-com.joulewise.night.plist"
cp /Users/edr/Library/LaunchAgents/com.joulewise.night.deadman.plist "$STAGE/arm-com.joulewise.night.deadman.plist"
cmp "$NIGHT_CUSTODY/night_plan.json" "$STAGE/arm-night_plan.json"
python3 -B - <<'PY'
import json, os
from pathlib import Path
root = Path(os.environ['NIGHT_CUSTODY'])/'night'
print('post-install night/ baseline:', json.dumps([
    {'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns}
    for p in sorted(root.iterdir())], indent=2))
PY
print 'block B rc=0'
```

The baseline must be `[]` — an empty `night/` (record 123's was). It is the
control the harvest compares every later entry against. If verification fails
*after* install, report the installed state and use the same
uninstall/unpublish recovery as the B4 failure branch before leaving a failed
arm. **Never remove an armed checkout while either agent is still loaded.**

---

## Record and exit (step 8)

Write a record shaped like
[`123`](../2026-09-09-rehearsal-harvest/123-rehearsal-20260911-arm-record.md)
in the activation's authorized linked bookkeeping worktree. It must carry, each
with an artifact pointer and never an expected value presented as an
observation:

- activation id and PID, record timestamp, install start/end epochs;
- H′ and the four things it carries (§Step 0a), with PR numbers;
- the **frozen triple** `(rehearsal-20260912, /private/tmp/joulewise-rehearsal-20260912-checkout, H′)`;
- the notice's message/thread ids, accepted send time, and the NO-channel
  limitation stated as a limitation;
- Block A and Block B outputs and return codes; the step-3b stop results with
  real task ids;
- **both censuses** raw, with ancestry and the P6 rule that was applied, plus
  the 83102-orphan check result;
- the C-1 unit-test output (rc and counts) and the CI state of PR #321;
- the **preflight JSON line** and the rendered + installed `ProgramArguments`
  (ruling 06 C-2);
- the `registration_path`, its measured sha256 and the constant it matched
  (§Step 0c);
- power source, both powermodes, the timer reading;
- the byte copy of the armed plan and the `night/` baseline;
- the sentence, explicitly: **a green stub says nothing about the
  capture-timeout seam.**

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?authorized linked worktree}"
: "${BOOKKEEPING_BRANCH:?authorized bookkeeping branch}"
: "${ARM_RECORD:?allocated repository-relative arm record path}"
: "${ARM_EVIDENCE:?allocated repository-relative artifact directory}"
export STAGE=/private/tmp/joulewise-rehearsal-20260912-staging
export SCRATCH=/private/tmp/joulewise-rehearsal-20260912-validate
cd "$BOOKKEEPING_ROOT"
test "$PWD" != /Users/edr/code/JouleWise
test "$(git branch --show-current)" = "$BOOKKEEPING_BRANCH"
test ! -e "$ARM_EVIDENCE"
mkdir -p "$ARM_EVIDENCE"
cp "$STAGE"/arm-* "$STAGE/preconditions.py" "$STAGE/notice-evidence.txt" "$ARM_EVIDENCE/"
cp -R "$SCRATCH/render" "$ARM_EVIDENCE/"
export DURABLE_POINTER=docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md
# Write ARM_RECORD with the fields above, and update DURABLE_POINTER with H',
# the frozen triple and the exact next action (harvest after 00:50).
test -f "$ARM_RECORD"
git diff --check
git diff -- "$ARM_RECORD" "$DURABLE_POINTER"
git status --short
test -z "$(git diff --cached --name-only)"
git add -- "$ARM_RECORD" "$ARM_EVIDENCE" "$DURABLE_POINTER"
git diff --cached --stat
# Review the index: only this arm's authorized record, artifacts and pointer.
git commit -m 'Record rehearsal-20260912 arm and harvest pointer'
git push origin "$BOOKKEEPING_BRANCH"
remote_branch="$(git ls-remote --exit-code origin "refs/heads/$BOOKKEEPING_BRANCH")"
test "${remote_branch%%$'\t'*}" = "$(git rev-parse HEAD)"
date '+arm-record-complete epoch=%s local=%Y-%m-%dT%H:%M:%S%z'
python3 -c 'import time; assert time.time() < 1789196700, "past the 00:05 PDT exit boundary"'
```

H′ stays the original handback commit as bookkeeping advances. Report a push
failure honestly and exit on time regardless. **End the activation with no own
background work, and absolutely before 00:05:00 PDT on 09-12** — the watchdog's
stand-down request lands then, TERM at 00:14, KILL at 00:15, and any agent
process alive at 00:30 refuses the night outright (P6 rule 2). Do not stay
resident until t0.

---

## Harvest pointer for the next activation

**Earliest safe harvest: after 00:50:00 PDT on 2026-09-12 (epoch 1789199400),
the courier deadline.** The watchdog will launch the next activation once
`plan_span_active` returns false, which happens when `courier.sent` exists in
`night/` (`magistrate_watchdog.py:734–735`). The fixed 02:45–03:30 belt does
not overlap the 00:50–02:30 harvest window.

1. **Harvest** by checklist
   [`13`](../2026-09-10-activation-96bfeca7/13-activation-checklist-2026-09-11.md)
   §2 (preserve first: `lstat` inventory of the original before any copy; a
   byte-exact archive of the whole custody root outside
   `~/night-custody/*/night_plan.json` discovery; repo copies with
   `SHA256SUMS`; `git ls-remote` the results branch and `cmp` its artifacts
   against custody; read the courier email back in the inbox).
2. **Accept or refuse item 6** against ruling 06 **C-7**, every clause of it:
   `night/receipt.json` verdict `REHEARSAL_ONLY`; C1 PASS with a measured
   `registration_sha256`; C2 `NOT_APPLICABLE` basis `no_pack_by_design`; C3
   PASS with measured `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`,
   `load_average_raw`, `thermal_raw` (and `cpu_speed_limit` when present); C4
   PASS with the boot-UUID/clock measured pair; C5 PASS with
   `chain_stub: built_in_stub_by_design`, `chain_sha256: null`,
   `expected_chain_sha256: null`; `night/result.json` verdict `REHEARSAL_ONLY`
   with `chain_exit_code` 0; `launchd.night.err` **empty**; `night.log`
   carrying `night driver started`, a `night gate verdict=` line that is not
   REFUSED, `durable record pushed branch=night-results/20260912`, and
   `courier attempt=1 … sent=True`; `courier.sent`'s message id read back in
   the inbox. Launchd last-exit 3 is the stub's unconditional status, **not** a
   refusal (ruling 61 Q4.3; `run_night.py:1672–1675`).
   Item 5 needs nothing from this night — it is already MET (record 01).
3. **Retire** by checklist 13 §4 and ruling 06 **C-8**, all of it **before
   02:30 PDT**: uninstall FROM the stub checkout with
   `scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260912/night_plan.json --hour 0 --minute 30 --uninstall`
   (no `--python`); verify the archive against the live root with `diff -qr`;
   `git worktree remove /private/tmp/joulewise-rehearsal-20260912-checkout`;
   `rm -r /Users/edr/night-custody/rehearsal-20260912`; then
   `launchctl list` free of `com.joulewise.night*` and
   `find ~/night-custody -maxdepth 2 -name night_plan.json` empty. Remove the
   frozen triple from the next relaunch prompt.
4. **Then the equivalence night**: `docs/phase_2/derivation_night_runbook.md`
   §0 through §1.5, with its install span 03:00–06:30 PDT on 2026-09-12 (§1.3)
   for t0 **2026-09-13 02:56:00 PDT, epoch 1789293360**. Note the launch
   fence: the watchdog will not START an activation inside
   `[02:45, 03:30)`, so the arming activation either is already resident before
   02:45 or is launched after 03:30 — plan the relaunch accordingly.

**The one way this schedule breaks, stated plainly.** `plan_span_active`
returns false after the completion epoch **only if `courier.sent` exists**;
otherwise it stays true until `_next_deadman_epoch(t0) + COURIER_LOCK_FRESH_S`
= 1789221600 + 900 = **1789222500, 07:15 PDT on 09-12**
(`magistrate_watchdog.py:732–736`; `COURIER_LOCK_FRESH_S = 900` from
`run_night.py:53`). So if the courier fails to send, no activation can be
launched to harvest before 07:15, C-8's "before 02:30" is missed, and fallback
(a) applies with no further gate. This is not a reason to weaken C-8; it is the
reason the harvest must confirm `courier.sent` first and report immediately if
it is absent.

---

## Fallback (a) — the trigger list (ruling 06 C-9)

Route (a) is: install 2026-09-12 03:00–06:30 PDT, stub t0 2026-09-13 02:56,
equivalence night earliest 2026-09-14 02:56. It applies **without any further
gate** if any of the following is true.

1. **Any of C-1…C-8 is not on disk by 02:30 PDT on 2026-09-12.** In particular:
   the cure not merged at a named head with its tests pasted (C-1); no rendered
   absolute-interpreter `ProgramArguments` and preflight JSON line in the arm
   record (C-2); the 83102 orphan tree still alive at the pre-install census
   (C-3); any plan coordinate outside C-4's bounds; an install outside C-5's
   bounds; an arming activation that does not exit by 00:05 (C-6); any C-7
   clause unmet; retirement incomplete (C-8).
2. **Ed vetoes reading R1** on the notice thread (a NO stands the night down
   outright; a veto of R1 specifically routes to (a)).
3. **The watchdog's fence for this t0 is not derived from the plan's
   `t0_epoch_s`** (C-6). Drafting verified the derivation in code —
   `plan_span_active` and `standdown_phase` both compute from
   `plan.t0_epoch_s`, and the only fixed fences are the wall-clock
   `[02:45, 03:30)` belt and the `[07:00, 07:01)` minute — so this trigger is
   expected NOT to fire; it is kept because the ruling's judge recorded it
   NOT EXECUTED.
4. **A CORRECT refusal on the (c) attempt**: a receipt refusing
   `night_refused_agent_present`, `night_refused_not_quiet` or
   `night_refused_hid_idle`. The rows ran live and refused; that is not a
   finding, but it discharges nothing for item 6, so (a) follows.
5. **The courier never sends**, so the harvest cannot be launched before 07:15
   PDT (see the paragraph above) and C-8 is missed.

Distinguish 4 from a **finding**: any `night_probe_error`, any crash, a
non-empty `launchd.night.err`, or a refusal of any other kind is a defect to
cure before any plan is armed, under (a) or (c) alike.

---

## Fact table — what was checked, and where

Line numbers refer to the drafting base `c935a79d` in
`/Users/edr/code/JouleWise-wt-bk-58a3bcfc`.

| Fact | Source, verified at the desk 2026-09-11 |
|---|---|
| A1. t0/window/deadline/span arithmetic | executed: `2026-09-12T00:30:00-07:00` → `1789198200`; `+900` → `1789199100`; `+300` → `1789199400` (`00:50:00-07:00`); `−1500` → `1789196700` (`00:05:00-07:00`); `−960` → `1789197240`; `−900` → `1789197300`; `2026-09-13T02:56:00-07:00` → `1789293360`; all round-tripped through `America/Los_Angeles` |
| A2. C-4's t0 window | ruling 06 §4(c) C-4 and VERDICT: `[1789196400, 1789200000]` = 00:00–01:00 PDT 09-12; `1789198200` is inside |
| A3. Watchdog leads and fences | `scripts/magistrate_watchdog.py:67–70` (`PLAN_LEAD_S`/`REQUEST_LEAD_S` `25*60`, `TERM_LEAD_S` `16*60`, `KILL_LEAD_S` `15*60`), `plan_span_active` 721–736, `standdown_phase` 822–829, `local_fixed_fence` 702–714, `plan_completion_epoch` 717–718 |
| A4. `COURIER_LOCK_FRESH_S = 900` | `scripts/run_night.py:51–53` (`COURIER_DEADLINE_S 300`, `COURIER_BACKOFF_S (60,180,600)`) |
| A5. `night-results/20260912` absent; `/20260911` present at `37876416` | executed `git ls-remote origin refs/heads/night-results/2026091[12]` from this worktree |
| A6. Driver-path modules import stdlib only at module scope | executed a grep of module-level imports in `joulewise/night_gate.py`, `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence_t0.py`, `joulewise/t0_rehearsal.py`, `scripts/run_night.py`; the only in-function project imports in `run_night.py` are at 1115, 1116, 1153, 1178, 1271, 1417 and name `arm_readiness`, `arm_readiness_evidence_t0`, `t0_rehearsal` |
| A7. `run_night.py` puts the repo root on `sys.path` | `scripts/run_night.py:27–29` |
| A8. Cure branch really implements the flags | executed `git show origin/fix/2026-09-11-night-interpreter-pin:…`: template `ProgramArguments[0]` is `@@PYTHON@@` with no `/usr/bin/env`; installer usage line carries `--python ABS_PATH`; `--python` with `--uninstall` is a usage error; default derivation at 47–58 via `/usr/bin/plutil -extract measurement_root`; preflight invocation at 152–154 under `env -i PATH=… HOME=…` |
| A9. Installer refuses only the dead-man hour | `scripts/install_night_agent.sh:112–115` (main) / the equivalent block on the cure branch; `--hour` accepts 0–23 at line 28 |
| A10. `--render-only` creates `custody_root/night` | `scripts/install_night_agent.sh:123–125` |
| A11. Row C1 for the stub class | `joulewise/night_gate.py:1300–1328`; constant `D166_REGISTRATION_SHA256` = `dfe55f8d…c265` at 32–41 |
| A12. Row C5 skips the chain read for the stub | `joulewise/night_gate.py:1043–1052` |
| A13. Production census argv and pass condition | `joulewise/night_gate.py:42` and `agent_census` 498–526: PASS only on `exit_code == 1` and empty stdout |
| A14. Arm-time own/foreign rule as executed | runbook 67 §Pins and preconditions; record 123 timeline 04:10:10 (`foreign agent matches: []` with own hits 18831/18848) |
| A15. D-180 clause 3 ratified, not installed; plan span unchanged | `docs/decision_log.md` D-180 §3 and its "decided ≠ done" preamble |
| A16. D-175's eight arming conditions | `docs/decision_log.md` D-175 §Decision |
| A17. `.venv/` is gitignored | `.gitignore:6` |
| A18. Interpreters on this host | executed: `/opt/homebrew/bin/python3.13 --version` → `Python 3.13.1`; `env -i PATH=/Users/edr/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin /usr/bin/env python3 --version` → `Python 3.9.6` |
| A19. Handback sections still describe the retired night | `docs/process/NIGHT_HANDBACK.md:42–81`, `102–113`, `115–144`; the driver/chain/preflight sentence at 166–169 |
| A20. PR state | executed `gh pr list`: #321 `NIGHT-INTERPRETER-PIN-01` OPEN/MERGEABLE; #320 `EPOCH-CONTINUATION-01` OPEN/MERGEABLE; `origin/main` `1dddcfea` |

---

## Flags for the lead

Facts in the dictated brief that did **not** match the primary file, and the
primary reading used instead:

1. **`plan_span_active`'s close condition.** Dictated: "closes at `courier.sent`
   or `t0 + 20 min`". Code (`magistrate_watchdog.py:732–736`): after the
   completion epoch the span closes **only** if `courier.sent` exists;
   otherwise it stays open until `_next_deadman_epoch(t0) + 900` =
   **1789222500 (07:15 PDT 09-12)**. Material: a failed courier blocks the
   harvest past C-8's 02:30 deadline. Written into §Harvest pointer and
   fallback trigger 5.
2. **"Census immediately before publication must be EMPTY (`pgrep` exit 1)".**
   That is ruling 06 C-3's literal text and it is unsatisfiable by any live
   arming session, whose own process matches `codex|claude|t3`. The executed
   rule (runbook 67 / record 123) is the ancestry-classified no-FOREIGN census,
   which exits 0 with own-only hits; D-175 condition 8's substance is "no OTHER
   agent session alive". §Preconditions P6 states both rules and the
   substitution. The EMPTY-census requirement *is* exact for the **production**
   census the driver runs at t0 — that part of the dictation is right, just
   about a different census.
3. **"verify with `git ls-remote origin refs/heads/night-results/20260912`".**
   The bare form exits **0** with no output when the ref is absent, so it
   asserts nothing. Must be `ls-remote --exit-code`, expecting status 2. The
   ref is confirmed absent today.
4. **"use the venv recipe of `derivation_night_runbook.md` §0.2 (quote its
   exact commands)".** §0.2 contains **no venv-creation commands** — it exports
   `PY`, tests `-x`, and diffs `pip freeze` against the measurement lock,
   deferring creation to runbook 68 §"Fresh clone at H". Both blocks are quoted
   in §Block A A4, with §0.2's lock `diff` explicitly marked NOT APPLICABLE to a
   bare stub venv (it would fail by construction).
5. **"pass `--python …` (or rely on the default derivation; say which and
   why)".** Answered: **rely on the default**, with three reasons in A4 —
   chiefly that the default branch is the one the real equivalence night takes,
   and passing `--python` would leave it unexercised.
6. **"a fresh disposable checkout"** — implemented as a `git worktree add
   --detach`, not a `git clone`, matching runbook 67 / record 123 / record 02's
   `git worktree remove`. Ruling 06 C-2's word is "clone"; the substitution is
   recorded in A3 with its reason.
7. **`registration_path` placeholder.** The placeholder is kept as instructed,
   but for a `REHEARSAL_STUB` the answer is forced by code, not by ruling 12:
   row C1 refuses anything whose digest is not `D166_REGISTRATION_SHA256`, so
   the value must be the file that constant names **in H′**. §Step 0c gives a
   block that reads the constant rather than hard-coding the path, so it
   follows ruling 12's cure automatically. Ruling 12's open question is about
   the *equivalence* night, not this stub.
8. **PR #320 in H′.** Ruling 06 C-1 requires only the interpreter cure. Folding
   #320 in is an ordering convenience; §Step 0a says so and says to drop it if
   it is not ready.
9. **"Dead-man stays at 07:00 … if it does, it takes the courier-already-sent
   branch."** Correct, and note the stronger fact: because installation happens
   on the evening of 09-11, the dead-man's *first* possible firing is 07:00 on
   09-12, after the harvest and uninstall — so on this night there is no
   pre-night dead-man observation at all. Item 5 does not need one (record 01).

### `[UNVERIFIED]`

- **U1.** H′ itself: it does not exist yet. `origin/main` is `1dddcfea`; PR
  #321, the B-1 cure PR and PR #320 are all unmerged as of 08:30 PDT 09-11.
  Every command taking `$H_PRIME` is unexecuted.
- **U2.** The notice's message/thread ids, Ed's non-veto of R1, and the
  clearing of the 83102 orphan tree — all future or Ed-external.
- **U3.** `~/night-custody/magistrate/magistrate.lock`'s current contents and
  whether the arming session will be its owner. The brief forbade touching
  `~/night-custody`, so `preconditions.py` carries an `ARM_OWNER_PID` override
  whose use must be recorded; the override path is unexecuted.
- **U4.** The preflight's exact JSON line under a **bare** venv. A6 establishes
  that every module the stub path imports is stdlib-only at module scope, but
  the cure's preflight may eagerly import more than those four modules; the
  installer fails closed with exit 2 if so, and A6's escalation covers it.
  Untested until the cure merges.
- **U5.** Whether the cure's `preflight` subcommand accepts a plan whose
  `chain_path` does not exist (true for every stub). It "parses the plan
  through the same `NightPlan` path the installer uses" (record 03 §3), and the
  installer already accepts such plans today, so this is expected to hold — but
  it is unexecuted, and it is the single most likely way Block A A6 fails.
- **U6.** Every live reading of this night: install/power/timer values, the
  rendered and installed plists, actual firing, receipt, courier, remote push,
  and the harvest. Script inspection and prior arm evidence establish command
  shapes, not this night's results.
- **U7.** The equivalence night's other gates (powermode, `sudo`, the ledger
  and pre-registration desk checks) are outside this runbook and remain owed.
