# Operating runbook for the agent-free calibration derivation nights, lane ACCEPTANCE-EPOCH-25G83-01

STATUS: **DRAFT runbook, tracked at `docs/phase_2/derivation_night_runbook.md`;
authorises nothing; every arm still goes through NIGHT_HANDBACK
(email-then-arm) and Ed's NO overrides.** The lane's code is merged: every
script, gate and test this runbook operates is on `main` at
`8cbcaf08`. Sections marked `[UNVERIFIED: …]` are facts this runbook could not
establish from a primary source; they are open questions for the operator, not
instructions.

**Changelog — revision 6 (2026-09-10), one line: the owner ruled, by directive
issue 316, that the first night is no longer the first of three blind
derivation nights but an EPOCH-EQUIVALENCE CHECK — one night, compared after
it closes against the thresholds the acceptance already in force carries,
under a rule fixed before the night runs.** What that forced:
§"What night one is for" is rewritten around the two routes and says which is
tried first; §2 becomes the harvest of an equivalence night — §2.1 gains the
retained values as things the magistrate MAY now read, §2.3 changes from a
blanket prohibition into a before/after boundary, and the new §2.5 states the
rule in full with its operative constants, its three outcomes (PASS, FAIL,
INCONCLUSIVE) and the exact next action for each; §3 and §4 are marked as the
FAIL route's continuation rather than the default; §6 items 4, 5, 7, 8 and 11
are restated so that the equivalence night licenses nothing by itself and a
PASS licenses nothing until the D-102 continuation addendum lands; §1 keeps
its arm procedure unchanged, with only its title and its one "three nights"
sentence corrected; §7 gains the ruling's own fact row; and §8 builds
`epoch-equivalence check`, `reference envelope`, `retained value` and
`continuation`. §2.5 names the committed desk tool that extracts the retained
values and applies the rule. One open item is RECORDED rather than answered:
the ruling fixes no night count for the case where an INCONCLUSIVE night is
followed by a failing one.

Revision 5 (same day) closed the operational defects a
contract review found, so the arm can be run from this file alone,
without the operator supplying values the file never defined. What that
forced: §0.2 now exports every variable a later runnable block interpolates —
`NIGHT_DATE`, `PLAN_ID`, `NIGHT_ROOT`, `STAGE`, `STAGED_PLAN`, `SESSION_ID`,
`EVIDENCE_ROOT_ID`, `CALIBRATION_PLAN`, `CALIBRATION_LEDGER` and
`LEDGER_HEAD_PIN` — each with a gloss and a rule for choosing it, and creates
the night root rather than telling the operator it must already exist; the
night plan is authored at a STAGING path and reaches its discoverable place
only at §1.4's atomic move, which removes the collision between §1.1b's
`--plan` INPUT and §1.4's "target must not pre-exist", and keeps §0.7's
discoverability precondition true; §1.4 carries the install commands
themselves instead of deferring to an unlocated runbook, and every citation of
that runbook is now a repository path; §1.5 states the frozen checkout triple's
exact contract fields and the new §2.0 derives from them every further value
the harvest needs; `fence` is split into its two senses and the watchdog sense
is stated as the contract states it, which is why a `t0` inside the
02:45–03:30 belt is correct rather than forbidden; `Session` is disambiguated
from the thing a fence blocks; `wrapper`, `night root` and `tracked chain` are
built in §Terms before §0 uses them, and §0.5 gives the tracked chain's path
and its `shasum` command at first use; and §0.8 always names which writer it
means.

Revision 4 (same day) revised against the MERGED
lane, and RESOLVED the §0.8 desk-input provenance with a tool that
exists. What that forced: the status banner no longer speaks of seat branches
or a red replay; §0.8's `[UNVERIFIED]` block is replaced by the desk-inputs writer
`scripts/write_derivation_night_inputs.py`, its flags, its refusals and the two
paste lines it prints; §0.3's `[UNVERIFIED]` on the live `check` strings is
replaced by the output recorded from a fresh clone at the desk (record 134);
the two desk inputs are named `identity-epoch.json` and `t1-bindings.json`
everywhere, which is the hyphenated spelling the code emits; §7 cites every
fact by SYMBOL and record number instead of by line number; §8 gains the desk
inputs writer, the paste line, the stale field and the `$PY` interpreter; and
`$PY` is now exported where it is first used rather than assumed.

Revision 3 (same day) revised against the lane's integration head, which moved
three things this runbook operates — the capture chain DISPATCHES on the
writer's exact status (a non-valid capture no longer ends the night), the
issuer enforces the pre-registration and the campaign's declared shape at
`prepare-candidate`, and the wrapper generator PARSES the two desk-produced
JSON inputs instead of only hashing them. Revision 2 closed the §1.1
`[UNVERIFIED]` on how the night driver supplies the chain's environment — it
does not, by design; a generated wrapper carries it.

Two `[UNVERIFIED]` blocks remain, unchanged in substance: the 06:05 last-start
cutoff's status (§1.3) and the complete night-gate refusal list with each
refusal's remedy (§5). Revision 5 edited one word inside the first — the
citation of the prior night's arm runbook now carries its repository path, like
every other citation of it.

Audience: the operator is the **next magistrate activation** — the session a
relaunch prompt starts, holding the frozen checkout triple (the plan id, measurement
clone path and head `H` of the night the previous activation armed, §1.5) and
the project's standing authorities. It is a desk operator: it prepares, notices, arms, exits, and
later harvests. It never observes a capture, because these nights are
agent-free by construction (§0.6).

---

## What night one is for, in one paragraph

Every calibration capture is judged against thresholds that live in one JSON
artifact called the **acceptance** — the issued file whose corpus statistics
set the numbers later captures are compared to. An acceptance binds an
**identity epoch**: the six-field vector `{os_build, hardware_model,
power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}`
describing the machine and estimator it was derived on. This machine's
`os_build` moved from `25F84` to `25G83`, so the live acceptance
`d079_calibration_acceptance_v2_n17_r6` binds an epoch that no longer exists
and refuses every ordinary capture (D-102 clause 2). Two routes lead out of
that refusal, and the owner's directive issue 316 of 2026-09-10 ruled which is
tried first. The LONG route DERIVES a replacement acceptance from a corpus of
captures taken on the new epoch — three agent-free nights of twelve
**derivation-only captures** each, a derivation-only capture being an
observation taken expressly to build a future acceptance, which licenses no
measurement of anything. The SHORT route, now the default, is an
**epoch-equivalence check**: ONE night of the same twelve derivation-only
captures, whose values are compared after the night closes against the
thresholds the existing acceptance already carries, under a rule fixed in
writing before the night runs. If every value sits inside that envelope, the
existing acceptance is CONTINUED onto the new epoch by a dated addendum and
nothing is derived; if any value does not, the three-night derivation proceeds
exactly as pre-registered, with this night counting as its first. This runbook
operates that one night; §2.5 is the rule that decides which route follows it,
and §3 and §4 run only if the check fails.

Sources for this paragraph: the pre-registration
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md`,
§"Why this registration exists" for the derivation route, and its revision 2
— which transcribes directive issue 316 — for the equivalence route, the
default ruling and the continuation.

## Terms, glossed here because every later section uses them

- **Slot** — one declared, ordered place for one capture inside a session,
  named `d01`…`d12`. Declared before the night runs; a slot the window cannot
  reach is recorded **unused**, never retried and never replaced.
- **Session** — a ledger capability that reserves several attempts under one
  open receipt while the repository-committed head pin stays put. A
  `derivation`-kind session is the only route these captures may take.
  Throughout this file, *session* unqualified always means this ledger object.
  The watchdog fences below speak of a different thing entirely — a magistrate
  **agent** session, a running Claude activation — and that sense is always
  written out in full.
- **Registration** — the set of ledger sessions that the pre-registration
  declares a derivation corpus is drawn from: three, one per night, on the
  FAIL route of §2.5, where the equivalence night counts as the first. A valid
  same-epoch observation captured OUTSIDE the registration refuses issuance
  rather than being quietly absorbed. An equivalence check that PASSES derives
  no corpus and issues nothing, so no registration closes.
- **Epoch** — the six-field identity vector above.
- **Stale field** — an identity field whose value on this machine differs from
  the active acceptance's identity epoch. A derivation night exists precisely
  because at least one field is stale; if none is, this is an ordinary night
  and the ordinary path applies.
- **Head pin** — the repository-committed file naming the ledger receipt count
  and last digest that consumers trust. *Head-equals-pin* means the physical
  ledger head matches that file exactly.
- **Screen** — a threshold a capture's value is compared against. Two matter
  here: the **level screen** (an acceptance's corpus maximum, the preflight
  bound a single capture is refused above) and the **bracket screen** (its
  corpus range, the drift below which a measurement window passes without
  spending error budget).
- **Ceiling** — the **budget ceiling**, the largest drift a generation will
  ever budget for. Issuance refuses when the bracket screen is not strictly
  below it.
- **Prior set** — an acceptance's list of every ledger observation through
  its cutoff receipt. **Corpus** — the subset of the prior set whose values
  the statistics are computed from; **retained n** is the corpus size.
- **Blind** — every rule that could otherwise be chosen after seeing values is
  fixed in writing BEFORE the data exists. That is the sense directive issue
  316 fixed for this campaign: blindness here means "every rule fixed before
  data", not "no one may look". Two consequences, differing by route. The
  equivalence night's rule is fixed at §2.5 before the night runs, so its
  retained values are read as soon as the night closes. On the FAIL route the
  derivation's rules are likewise fixed before capture, and the issuer
  additionally enforces in code that no corpus statistic is computed before
  the last registration session is terminal (§2.2, §4.1).
- **Dead-man** — the second LaunchAgent (a macOS launchd job file), installed
  alongside the night agent, which fires at a fixed local minute and stands the night down if the night's
  completion time has passed without completion.
- **Driver preflight** — the install-time check that loads the driver module
  and every project module it imports at module scope under the job's
  interpreter and PATH and parses the plan, without exercising functions'
  lazy imports inside `joulewise` or running the chain's input checks.
- **Tracked chain** — `scripts/night_chains/calibration_derivation_only.zsh`,
  the committed script that actually runs the twelve captures. *Tracked* means
  it is a repository file, byte-identical in every clone at `H`; contrast the
  wrapper, which is generated per night and committed nowhere.
- **Wrapper** — the generated `zsh` file, one per night, that the night driver
  actually launches. It carries the night's whole environment as literal
  `export` lines, re-checks its pinned inputs, and then `exec`s the tracked
  chain. The plan's `chain_path` names it. §1.1a builds the mechanism and the
  problem that forces it.
- **Night root** — `<NIGHT_ROOT>`, the single custody directory one night's
  evidence is filed under; the plan calls the same directory `custody_root`,
  and the wrapper exports it as `WINDOW_CUSTODY_ROOT`. The two desk inputs, the
  three generated files and everything the night writes live in it. Its path
  convention is `/Users/edr/night-custody/<PLAN_ID>` (§0.2).
- **Fence (watchdog sense)** — a period during which the relaunch watchdog
  refuses to LAUNCH OR ADOPT a magistrate **agent** session on this machine.
  Three things fence: a valid plan's span (opening at the closed boundary
  `t0 − 25 min`), the fixed local belt `[02:45:00, 03:30:00)`, and the fixed
  local dead-man minute `[07:00:00, 07:01:00)`; both fixed intervals are
  half-open (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Safety model and state
  machine" for the `FENCED` state, §"Fence and deadlines" for the intervals).
  **What a fence forbids is an agent being started, never a night being run.**
  The night's own two LaunchAgents are not magistrate sessions, and no fence
  touches them. That is why §1.2's worked `t0` of 02:56 local sits INSIDE the
  belt and is nonetheless correct: a capture night wants precisely the hour in
  which no agent can be launched or adopted. The rehearsal night of 2026-09-09
  fired at 02:56 local and ran to chain exit 0
  (`docs/process/NIGHT_HANDBACK.md`, §"Executed — rehearsal-20260909").
- **Blindness fence** — a different object under a confusingly similar name:
  the code-enforced refusal of `prepare-candidate` while any session named in
  the registration is not terminal, which stops a corpus statistic being
  computed early on the FAIL route (§2.3 item 3). It is not an interval, and
  no clock clears it; it does not govern the equivalence check of §2.5, whose
  rule is fixed before capture instead. Where this file writes "fence" with no
  qualifier it means the watchdog sense above.
- **Handback** — `docs/process/NIGHT_HANDBACK.md`, the file the night courier
  (the process that emails the night's result, §1.2) reads first; the magistrate rewrites its three night-specific sections before
  every armed night and commits that rewrite with the night's plan.
- **Email-then-arm** — the standing arming procedure: Ed is emailed the night
  notice, and the arm proceeds without waiting for a reply; **Ed's NO
  overrides** and stands the night down (`docs/process/MAGISTRATE_WATCHDOG.md`,
  §"Install handoff", closing paragraph: "Arming itself remains outside this
  watchdog's charter and always uses the email-then-arm handback; Ed's NO
  overrides").

A first-use table for every term of art in this file is at §8.

---

## 0. Preconditions and desk checks

Do all of §0 before authoring any plan. Each check is cheap; each failure is a
reason not to arm tonight, never a reason to work around it.

### 0.1 The lane's code is merged at a reviewed head H

`H` is the full 40-character SHA of the commit on `origin/main` that carries
BOTH the merged ACCEPTANCE-EPOCH-25G83-01 lane AND the night's handback rewrite
and production inventory row. There is exactly one H; the plan's `repo_head`,
the plan's `measurement_head`, the handback commit, and the clone's detached
HEAD are all H.

```zsh
set -euo pipefail
: "${BOOKKEEPING_ROOT:?the activation's authorized linked worktree}"
cd "$BOOKKEEPING_ROOT"
test "$PWD" != /Users/edr/code/JouleWise
git fetch origin main
export H="$(git rev-parse origin/main)"
git log --oneline -1 "$H"
```

Do not arm on a head whose whole-suite replay is not green. The lane's own
history is the standing example of why: five modules failed only under the
whole suite and never under any one worker's focused set (record 98), and the
replay did not come back clean until the head recorded in record 130. A
**record** cited by number in this file is the numbered write-up of that name
in this lane's process-trace directory,
`docs/process_traces/2026-09-10-activation-96bfeca7/`; each is a primary
artifact of the work it describes, and §7 lists which fact came from which.

### 0.2 A fresh clone at H is the measurement root

The **measurement root** is a fresh, independent GitHub clone detached at H,
from which BOTH night agents are installed. Its path is recorded in
`configs/production_custody_inventory.json` inside H itself, so the clone name
carries no SHA. Use the fresh-clone recipe rather than fast-forwarding or
renaming any provisional clone; renaming moves venv and editable-install
absolute paths (record 12, `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`, §"Fresh clone at H").

```zsh
set -euo pipefail
: "${H:?}"
export NIGHT_DATE=<YYYYMMDD>
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation"
remote_main="$(git ls-remote --exit-code "$REMOTE_URL" refs/heads/main)"
test "${remote_main%%$'\t'*}" = "$H"
test ! -e "$MEASUREMENT_ROOT"
test ! -L "$MEASUREMENT_ROOT"
git clone --no-hardlinks "$REMOTE_URL" "$MEASUREMENT_ROOT"
git -C "$MEASUREMENT_ROOT" checkout --detach "$H"
```

Build the clone's virtual environment from the lock, then export the one
interpreter every desk step in this runbook uses:

```zsh
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
test -x "$PY"
diff -u <(grep -Ev '^(#|[[:space:]]*$)' "$MEASUREMENT_ROOT/env/mac-measurement-lock.txt" | sort) \
  <("$PY" -m pip freeze --exclude-editable | sort)
```

The `diff` is the check that the environment is the reviewed one and not
merely present: empty output and rc 0 mean the clone's installed packages are
exactly the lock's. It is the same assertion the prior night's arm runbook runs
(`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`,
§"Block A", last command).

`$PY` is the **project venv interpreter** — the Python inside the measurement
clone's `.venv`, the only one with this project's dependencies installed. It is
not `/usr/bin/python3`. Two desk steps below fail in different ways under the
wrong interpreter, and §0.8's desk-inputs writer is the one that fails silently enough
to matter, so `$PY` is exported here, once, and used by name from now on. The
emitted wrapper sets the same value for the night itself, from
`<MEASUREMENT_ROOT>/.venv/bin/python`, and refuses if it is missing or not
executable (§1.1a step 1).

`<NIGHT_DATE>` is the eight-digit `YYYYMMDD` of the calendar date `t0` falls
on — the morning the captures happen, not the evening the agents are installed
(§1.3 installs on the day BEFORE `t0`). Every dated name below is built from
this one value so that the plan id, the night root and the clone cannot
disagree about which night they belong to.

The production ledger lives in this clone's own
`runs/calibration_observation_ledger.jsonl`, restored byte-exact from the
canonical ledger and then authenticated with `verify_custody=True`. Custody
locators are absolute iCloud paths; copy no custody directories and rewrite no
locator (record 05 / file 11 route).

#### Every other variable this runbook's commands interpolate

Assign them here, in the same shell, before anything below runs. **No command
later in this file assigns a variable**; a block that interpolates one it never
defined is how an operator ends up running `--out-dir ""` against an empty
string and writing the night's inputs into the current directory. Choose each
value by the rule in the table that follows, then run the block.

```zsh
set -euo pipefail
: "${H:?}" "${NIGHT_DATE:?}" "${MEASUREMENT_ROOT:?}"
export PLAN_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export SESSION_ID="d079-epoch-25g83-derivation-n1-$NIGHT_DATE"
export EVIDENCE_ROOT_ID=<the registered evidence root id, no derivable default>
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export STAGE="/Users/edr/night-plan-staging/$PLAN_ID"
export STAGED_PLAN="$STAGE/night_plan.json"
export CALIBRATION_PLAN="$NIGHT_ROOT/calibration_plan.json"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"

# No emitted literal may contain a census substring (§1.1b, §5).
if print -rl -- "$PLAN_ID" "$SESSION_ID" "$EVIDENCE_ROOT_ID" "$NIGHT_ROOT" \
     "$MEASUREMENT_ROOT" "$CALIBRATION_PLAN" | grep -iE 'codex|claude|t3'; then
  print -u2 'census substring in an emitted literal above; rename it'
  exit 1
fi

# Neither directory may be reused from an earlier night or an earlier attempt.
test ! -e "$NIGHT_ROOT"
test ! -L "$NIGHT_ROOT"
test ! -e "$STAGE"
test ! -L "$STAGE"
mkdir -p "$NIGHT_ROOT" "$STAGE"
test "$(stat -f %d "$NIGHT_ROOT")" = "$(stat -f %d "$STAGE")"
```

| Variable | One line, and the rule for choosing it |
|---|---|
| `NIGHT_DATE` | `YYYYMMDD` of the date `t0` falls on. Chosen first; everything dated is built from it. |
| `PLAN_ID` | The night plan's `plan_id` (§1.1). One per night, so nights 2 and 3 get `-n2-`/`-n3-`. It names the night root, so it is fixed BEFORE any directory exists. |
| `SESSION_ID` | The ledger session this night opens, passed to the generator as `--session-id` and baked into the wrapper. One per night; the three together are the registration (§3). It also prefixes every slot attempt id (`<SESSION_ID>-d01`…), so it is an emitted literal and must survive the census check. |
| `EVIDENCE_ROOT_ID` | The identifier of the evidence root the night's bundles are filed under. **It has no derivable default**: take the literal from the record that registers it and record both in the arm materials (§1.1b step 3). |
| `NIGHT_ROOT` | The night root (§Terms) — `/Users/edr/night-custody/<PLAN_ID>` by convention, and the value the plan's `custody_root` must carry. It is the directory the watchdog's discovery glob looks one level inside (§0.7). |
| `STAGE` | The staging directory the plan is AUTHORED in, deliberately outside the watchdog's discovery path, so that authoring a plan does not arm a night (§0.7, §1.1b step 2). |
| `STAGED_PLAN` | `$STAGE/night_plan.json` — the plan's path while it is being authored, generated from and verified against. §1.4 moves these bytes to `$NIGHT_ROOT/night_plan.json`, and that is the only moment the night becomes discoverable. |
| `CALIBRATION_PLAN` | The **frozen calibration plan**: the committed capture plan a night's captures are taken under, a `calibration_plan.json` from a frozen campaign pack in the clone (`docs/phase_2/window_runbook.md`, §the ALPHA `window.env` example, calls the same file `FROZEN_PLAN` and notes it is not a custody reservation plan). Copy those committed bytes to `$CALIBRATION_PLAN` before §1.1b step 3; the path must be absolute, and the wrapper re-checks the file's `plan_id` and SHA-256 at launch (§1.1a step 3), so a wrong copy fails before the settle rather than at `d01`. |
| `CALIBRATION_LEDGER` | The ledger the night opens its session against — **the clone's own**, never the canonical one. This is exactly the generator's `--ledger` default, written out so the harvest (§2.0) can rebuild it. |
| `LEDGER_HEAD_PIN` | The committed head pin the ledger is authenticated against — again the clone's, and exactly the generator's `--head-pin` default. |

Two notes on the block itself. `stat -f %d` prints a filesystem device number;
the night root and the staging directory must share one, because §1.4 publishes
the plan with `os.replace`, which cannot cross devices. And each precondition
is its own statement rather than a `&&` chain: under `set -e` a failing command
on the LEFT of `&&` does not end the shell, so `test ! -e X && test ! -L X`
would sail past an existing night root.

### 0.3 The epoch watch: `check` must exit 3, and that is the expected result

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check
echo "check rc=$?"
```

`check` is read-only. It authenticates the ACTIVE issued acceptance and the
ledger, then prints a four-row table comparing the epoch that acceptance binds
against the machine observed right now. The four watched fields are
`os_build` and `hardware_model` read from `/usr/sbin/sysctl`,
`powermetrics_sha256` hashed from `/usr/bin/powermetrics` (the binary is
hashed, never executed), and `mlx_version` from the **T1 bindings** of the
ledger's last row — T1 bindings being the toolchain-identity block a
finalization receipt records (among them the MLX version in force at that
capture). **With no `--session-ids` argument it returns 3 when any field
mismatches or any error was found, and 0 otherwise** (`check` and
`mismatched_fields` in `scripts/issue_calibration_acceptance_generation.py`).

Gloss, because the sign is inverted from the usual: **rc 3 is the expected,
correct result throughout this lane.** The whole reason the lane exists is that
`os_build` moved to `25G83` while the live acceptance still binds `25F84`. An
rc 0 here would mean the machine's identity now matches the old artifact —
i.e. the OS was rolled back, or the wrong acceptance file was read — and is a
**stop**, not a green light.

**The worked example, run at the desk from a fresh clone (record 134).** The
values below are what this machine printed, recorded field by field; the
column layout is the tool's, not reproduced here:

```
os_build             expected 25F84       observed 25G83       MISMATCH
hardware_model       expected …           observed …           match
powermetrics_sha256  expected d1dccad0…   observed b762e5bf…   MISMATCH
mlx_version          expected 0.31.2      observed 0.31.2      match
mismatched fields: os_build, powermetrics_sha256
rc 3
```

**Two mismatching fields is the expected shape here, not one.** The
`powermetrics_sha256` row compares the LEDGER'S LAST ROW's T1 sampler digest
(`d1dccad0…`, recorded when that capture ran) against the binary on this
machine now (`b762e5bf…`). The macOS update replaced the sampler binary along
with the build, so the last row's digest is simply older than the machine. That
is a second symptom of the same event, and it is exactly why a derivation
corpus is needed. Record the whole table verbatim in the arm materials, and
treat any field OTHER than `os_build` and `powermetrics_sha256` mismatching as
a stop until it is explained.

**Then run `check` a second time with `--preregistration`, and read the line it
appends.** The pre-registration names the `/usr/bin/powermetrics` SHA-256 the
campaign is registered under —
`b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5` — and says
in terms that a change to it voids the registration. The sampler binary is the
instrument: a different binary is a different measuring device, and a corpus
half-captured on each is two corpora. `check --preregistration` is the desk step
that reads that literal out of the registration text
(`preregistration_epoch_pins`) and compares it against the binary hashed on this
machine right now:

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md
echo "check --preregistration rc=$?"
```

Without the flag the watch output is byte-identical to the table above; with it,
exactly one line is APPENDED after the table, and nothing else changes. At the
desk run of record 134 that line read:

```
pre-registered powermetrics sha256 b762e5bf…: match
```

or, when they differ, `…: MISMATCH — the registration is void`.

**`match` here and `MISMATCH` on the table's `powermetrics_sha256` row are both
correct at the same time, and confusing them is the trap.** They compare
different pairs. The table asks *does the ledger's last recorded capture agree
with this machine?* — no, because the update moved the binary under it. The
appended line asks *is this machine the instrument the campaign registered?* —
yes, `b762e5bf…` is the observed value in the table AND the literal in the
registration. The first is the stale artifact; the second is the live
instrument, and the second is the one that must say `match` before any night is
armed.

**The return code cannot tell you which.** `check` returns 3 when any watched
field mismatches OR any error was recorded, and the mismatches above already
force 3 for this entire lane; a sampler mismatch only adds one more error to a
code that was 3 already. So the expected result here is still rc 3, and rc 3 is
not the check — the printed line is. Record that line verbatim in the arm
materials for every night. `MISMATCH` is a stop that voids the registration: no
night may be armed under it, and a mismatch discovered after captures exist is a
matter for Ed's written ruling, not a re-arm.

### 0.4 Ledger authenticated and head-equals-pin

The same `check` invocation loads the ledger snapshot with
`require_committed_pin=True, verify_custody=True, mode="read_replay"`. Any
refusal reason is printed on the `ledger: …` line. A `ledger:` line is a stop:
the night's first machine action opens a session at head-equals-pin, and a
ledger that will not authenticate at the desk will not authenticate at 03:00
either. Record the head pin's sequence and digest now — the pre-registration's
`[SEQ]` and `[DIGEST]` fields are filled from the pin in force at the FIRST
night's open, and are then frozen for every night of the campaign that
follows.

### 0.5 Pre-registration committed, with its bracket fields filled

`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` must be
committed inside H with `[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]` and
`[CHAIN_SHA256]` filled. Those five are facts that did not exist when the text
was written; filling them reopens no scientific rule. The plan's
`registration_path` points at this file (`NightPlan` in
`joulewise/night_gate.py`).

`[DD]` is the authoring day of the registration text itself — the registration's
own §"Fields filled at commit" glosses it exactly so — and the other four are
the facts named below.

`[CHAIN_SHA256]` takes the **tracked chain's** SHA-256 — the digest of
`scripts/night_chains/calibration_derivation_only.zsh` in the clone (§Terms) —
one value shared by all three nights, and NOT any night's wrapper digest:

```zsh
shasum -a 256 "$MEASUREMENT_ROOT/scripts/night_chains/calibration_derivation_only.zsh"
```

The registration reserves a
single blank for it, and every night produces its own wrapper (its own plan,
session ID and `t0`), so only the tracked chain's digest — the one value every
night shares — can fill it. That digest is also the literal each night's wrapper compares against
before it `exec`s (§1.1a step 4), which is what makes the registered value and
the value in force at capture the same number.

**Pin the pre-registration's own digest into the arm materials.** Once the file
is committed inside H with those five fields filled, hash the committed bytes
in the measurement clone and carry the value in every night's arm record:

```zsh
shasum -a 256 "$MEASUREMENT_ROOT/configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
```

The clean-tree check of §0.8 is what makes this the committed bytes rather than
a working-copy edit. The digest is not decoration: `prepare-candidate` takes it
as the required `--preregistration-sha256` and refuses —
`pre-registration sha256 <observed> does not match the pinned <given>; not
issued` — if the file's bytes moved between the arm and issuance (§4.2). A
pre-registration exists to fix the rules BEFORE the data; this pin is what makes
"before" checkable by someone reading the artifacts months later, because
without it the tool would derive against whatever the file says on the day it
runs, which is exactly the edit the document exists to forbid. Record it once,
at the first night's arm, and re-record the same value at every night that
follows — a change between nights is a stop, not a new pin.

**V3 is answered, and is no longer a precondition of this arm.** V3 is the
night count, the slots per night and the retained-corpus minimum — three
nights × 12 slots, retained n ≥ 19 — and the pre-registration required Ed's
affirmative written acknowledgment of it before the first capture's arm.
Directive issue 316 supplied the answer instead: NO as the default path, with
the equivalence night of §2.5 in its place, and V3 AFFIRMED only on that
check's FAIL route. Revision 2 of the pre-registration carries the ruling;
record its digest in the arm materials exactly as above, since revision 2 is
part of the committed file's bytes. The registration's other rules remain
proposed defaults adopted by cold gate 46 under an open Ed veto.

### 0.6 Census clean, and the night is agent-free

`[QUIET-MAC]` nights are agent-free. The magistrate exits before `t0 − 25
minutes`; that boundary is the closed start of the plan span, and the resident
supervisor's cooperative ladder enforces it: `standdown.request` at
`t0 − 25 min`, TERM no later than `t0 − 16 min`, KILL no later than
`t0 − 15 min` (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines", the boundary table).

Before the arm census, stop all own seats, delegated tasks and background jobs
using the activation's real task controls; record the task IDs and results and
invent none. Then inspect and classify by ancestry:

```zsh
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume'
```

A no-match `grep` exit 1 is the expected outcome, not a failure to be
suppressed. "Own" means this activation and its attached descendants: prior
activations, interactive sessions, foreign seats, daemons, spares, resumed
twins and PID-1 orphans are **not** own. Foreign or unclassifiable processes
abort the arm; do not signal them. Never run the chain, the driver, a full
preflight or a calibration capture from the live activation as a quietness
test.

### 0.7 Nothing else is armed or discoverable

No stand-down, no Ed NO, no unresolved owner-authored `directive` issue, no
discoverable prior plan root, no active or indeterminate measurement ownership.
Remove every `REHEARSAL_STUB` plan root before arming any real plan
(`docs/process/MAGISTRATE_WATCHDOG.md`, §"Install handoff").

**"Discoverable" is one exact glob, and that is what makes staging safe.** The
watchdog enumerates plans by globbing `*/night_plan.json` in the PARENT of its
own state directory — `glob_plans` in `scripts/magistrate_watchdog.py`, whose
state root is `/Users/edr/night-custody/magistrate`, so the enumerated set is
exactly `/Users/edr/night-custody/*/night_plan.json`: one level down, that
filename, nothing else. A plan authored at `$STAGED_PLAN` under
`/Users/edr/night-plan-staging/<PLAN_ID>/` is therefore invisible to it, which
is precisely why §1.1b authors and verifies there. The night becomes
discoverable at one instant and one only: §1.4's `os.replace` into
`$NIGHT_ROOT/night_plan.json`, after the email. The night's own driver never
discovers anything — launchd hands `scripts/run_night.py` the plan path as a
`--plan` argument (its `--plan` is `required=True`), so the driver reads the
file it was installed with and no other.

Check it, and expect no output:

```zsh
print -rl -- /Users/edr/night-custody/*/night_plan.json(N)
```

### 0.8 The clone's tree is clean, and the two desk inputs are written

**Clean tree** means: the measurement clone has no uncommitted change of any
kind — no modification, no staged file, no untracked file. Check it and record
the output verbatim in the night's arm materials:

```zsh
git -C "$MEASUREMENT_ROOT" status --porcelain
```

The expected output is **nothing at all**, zero bytes. Any line is a stop:
stand the night down and re-cut the clone (§0.2).

Why this is a precondition and not a nicety: the night gate binds the clone by
its committed `HEAD` only — it checks `git rev-parse HEAD` equals the plan's
`measurement_head` and nothing more (the clone-head condition in
`joulewise/night_gate.py`, read by the S7 contract refuter, record 105 §5.2).
Nothing anywhere excludes uncommitted edits. The wrapper of §1.1a closes this
for exactly one file, the capturing chain, by comparing its bytes against a
digest baked in at arm time; `recover_calibration_ledger.py`,
`reserve_calibration_window_bracket.py` and `validate_powermetrics_fiducial.py`
— the three programs that actually open the session, reserve the slots and
write the captures — remain bound by `HEAD` alone. So an edited working copy of
any of them would run all night with no signal. **This check is procedure, not
code**: no tool enforces it, which is precisely why it is written here and
recorded in the arm record.

#### The two desk inputs, and the desk-inputs writer that produces them

**Two different programs are called a writer in this lane, and this file always
says which.** The **desk-inputs writer** is
`scripts/write_derivation_night_inputs.py`, run once by the operator at the
desk. The **capture writer** is `scripts/validate_powermetrics_fiducial.py`,
run twelve times by the chain during the night. The bare word "writer" survives
below only inside a tool's own quoted message, where it always means the
capture writer.

The night root `$NIGHT_ROOT` (§Terms; exported and created at §0.2) must hold
two desk-produced JSON files before the wrapper can be generated:

| File | What it holds |
|---|---|
| `<NIGHT_ROOT>/identity-epoch.json` | The six-field identity vector, one JSON object. |
| `<NIGHT_ROOT>/t1-bindings.json` | The T1 bindings: the same six fields plus the four execution pins that fix the exact binaries and files a capture ran with — the `powermetrics` executable's digest, the clock-anchor method version, the MLX version, and the frozen protocol's digest. |

Those names are hyphenated, and the hyphens are not a style choice: they are the
constants `IDENTITY_EPOCH_NAME` and `T1_BINDINGS_NAME` in
`scripts/generate_g2a_probe_inputs.py`, which every tool in this chain imports.
An underscore spelling is a different file, and the wrapper would refuse at
launch with `identity epoch json is missing`.

The reservation copies the CONTENTS of both files verbatim into every slot
record (`scripts/reserve_calibration_window_bracket.py`, `main`, record 105 §2),
so their bytes are part of what every capture is bound to, and the generator
pins each one's SHA-256 into the wrapper as a literal.

**The producer is `scripts/write_derivation_night_inputs.py`** (seat S8, record
135). It exists because the producer used by G2-a — the measurement campaign
these thresholds exist to serve, and the one §6 clause 1 refuses to license
until a successor acceptance is issued — cannot serve a derivation night: that
tool authenticates the acceptance's epoch before writing anything, and a stale
epoch is exactly what a derivation night has (record 134). The desk-inputs writer takes
the same machine reads and skips that one authentication.

**It must be run with `$PY`** — the project venv interpreter of §0.2. The writer
reads the MLX version by importing `mlx.core`, and an interpreter without MLX
installed either fails the import outright (`refused: machine vector derivation
failed: ModuleNotFoundError: No module named 'mlx'`) or yields
`mlx_version None`, which its own completeness check refuses. A system
`python3` on this machine has no MLX, so this is the ordinary way to get it
wrong, and it is worth one line in the arm materials that `$PY` was used.

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/write_derivation_night_inputs.py --out-dir "$NIGHT_ROOT"
echo "write_derivation_night_inputs rc=$?"
```

Flags, all of which have workable defaults except `--out-dir`:

| Flag | Default | Meaning |
|---|---|---|
| `--out-dir` | required | The existing night root the two files are written into. It must already exist; the script never creates the custody directory the night's evidence is filed under. |
| `--power-policy` | `ac_high_power` | The value written into the epoch's `power_policy` field. The default is imported from the wrapper generator's own `CHAIN_POWER_POLICY`, so it cannot drift from the value that generator enforces. Do not pass another. |
| `--acceptance` | the active acceptance | The artifact this machine is compared against, to name the STALE FIELDS. Read for that diagnostic only: never written, never pinned into the night. |
| `--force` | off | Overwrite the two files if they already exist. |

**What it does, in order, so that nothing is written until everything passes.**
It reads this machine through the capture writer's own helpers rather than
through a second implementation — `_sysctl_identity` for `os_build` and
`hardware_model`, the module constants for the sampling interval, estimator
revision and protocol id, and `_planned_t1_bindings` for the four execution
pins, all from `scripts/validate_powermetrics_fiducial.py`. That is the point of
the design: the reserved slot's copy and the value the capture writer measures at 03:10
come from the same code, so they cannot disagree. It then refuses any vector
whose key set is not exactly the expected fields or whose values are not all
present, asks the live preflight which fields are stale, and only then writes
both files, with the canonical serialization (`indent=2`, sorted keys, trailing
newline) that every consumer's digest assumes.

**On success it exits 0 and prints three lines.** The last two are the **paste
lines** — lines formatted as shell assignments precisely so they can be pasted
into the arm materials and into the next command without retyping a path or a
digest:

```
stale identity fields vs /…/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json: os_build
IDENTITY_EPOCH_JSON=<NIGHT_ROOT>/identity-epoch.json sha256=<64 hex>
T1_BINDINGS_JSON=<NIGHT_ROOT>/t1-bindings.json sha256=<64 hex>
```

Record all three verbatim in the arm record. The two paths are what §1.1b step 3
hands to `gen_derivation_night.py` as `--identity-epoch-json` and
`--t1-bindings-json`; the two digests are what the generator bakes into the
wrapper and what the wrapper re-checks at launch, so the arm record's copy is
the operator's only way to tell, later, WHICH bytes the night was pinned to.

**Its refusals. Every one prints `refused: <reason>` on stderr, exits 2, and
writes nothing** — never one file of the pair:

| Refusal | Meaning | Operator action |
|---|---|---|
| `no identity field differs from the acceptance's epoch at <path>: … this is an ORDINARY night, not a derivation night` | Nothing is stale. | **Stop.** The premise of the lane is gone — re-run §0.3. A derivation night captured here would be refused by the capture writer at `d01` with the settle already spent. |
| `machine vector derivation failed: ModuleNotFoundError: No module named 'mlx'` | The wrong interpreter. | Re-run with `$PY` (§0.2). |
| `t1 bindings fields are empty on this machine: [...]` / `identity epoch fields are empty on this machine: [...]` | A machine read came back empty or `None` — an absent MLX or an unreadable sampler is the usual cause. | Fix the machine read. The night's reserve step refuses an empty binding, so this is a desk refusal standing in for a burned night. |
| `refusing to overwrite [...]; a night may already be pinned to those bytes` | The two files already exist. | Do not reach for `--force` reflexively: a wrapper generated from the old bytes pins their digests, so overwriting them invalidates it. Pass `--force` only when you intend that, and re-emit and re-`--verify` the wrapper afterwards. |
| `--out-dir <path> is not an existing directory` | The night root does not exist yet, or `$NIGHT_ROOT` was never exported and expanded to the empty string. | Re-run §0.2's export block, which both assigns `NIGHT_ROOT` and creates it. |
| `--power-policy is empty` | An empty value was passed. | Omit the flag. |
| `the acceptance at <path> could not be read as an issued artifact (…)` | The acceptance will not authenticate at all, so no stale field can be established. | Name a readable issued acceptance with `--acceptance`, or fix §0.3 first. |

**Re-derive both files whenever the machine may have moved.** Run the desk-inputs writer at
each night's arm, and re-run it if `os_build`, `powermetrics_sha256`,
`mlx_version`, `estimator_revision` or `protocol_sha256` changed since the
previous night: the capture writer compares its measured bindings against the
reserved slot's copy, so a drift between arm and `t0` refuses at slot `d01` and
costs the whole night. Both files live in the night root and travel with the
night's custody.

---

## 1. The equivalence night's arm (also night one of the FAIL route)

### 1.1 The plan is `joulewise.night_plan.v2`, class `DIAGNOSTIC_NO_PACK`

`DIAGNOSTIC_NO_PACK` is the receipt class for a night that runs no measurement
pack: it requires a registration path and marks only the pack-ARM condition
(C2) not-applicable. The transaction-authorization, quiet-census, boot/clock
and no-retry conditions all still have to pass.

The v2 plan's required keys are exactly `_PLAN_KEYS` in
`joulewise/night_gate.py`, and `NightPlan.from_mapping` refuses a plan with any
key missing or any key extra:

| Key | Value for night 1 |
|---|---|
| `schema` | `joulewise.night_plan.v2` |
| `schema_version` | integer `2` |
| `plan_id` | `<PLAN_ID>` — e.g. `d079-epoch-25g83-derivation-n1-<YYYYMMDD>` |
| `receipt_class` | `DIAGNOSTIC_NO_PACK` |
| `t0_epoch_s` | `<t0>` (integer Unix seconds) |
| `window_max_s` | `9000` (derived in §1.2) |
| `authored_epoch_s` | authoring time; must be within 36 h of both now and `t0` (`PLAN_MAX_AGE_S`) |
| `repo_head` | `<H>` |
| `measurement_root` | `<CLONE>` — the §0.2 clone path, absolute |
| `measurement_head` | `<H>` — equal to `repo_head` |
| `chain_path` | `<NIGHT_ROOT>/chain.zsh` — the **emitted wrapper** of §1.1a, NOT the tracked chain |
| `chain_sha256_path` | `<NIGHT_ROOT>/chain.zsh.sha256` — exactly `chain_path` plus `.sha256`; the generator refuses any other value |
| `custody_root` | `<NIGHT_ROOT>` — e.g. `/Users/edr/night-custody/<PLAN_ID>` |
| `registration_path` | the committed pre-registration of §0.5 |

The plan carries no pack block: `_PACK_NIGHT_KEYS` belongs to pack nights, and
this night has no pack.

### 1.1a The wrapper: what `chain_path` actually points at, and why

**The forcing problem.** The night driver launches the file the plan names in
`chain_path` with a fixed, four-variable environment and NO command-line
arguments: it sets `NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD` and
`PY` from the plan, and runs `/bin/zsh <chain_path>` with nothing after it
(`_run_chain_once` in `scripts/run_night.py`, pinned by a test in
`tests/test_run_night.py` that asserts the argv is exactly
`["/bin/zsh", <chain_path>]`; scout record 101 §0). The tracked derivation chain
`scripts/night_chains/calibration_derivation_only.zsh` needs far more than
that: **thirteen** further environment variables, each behind a
`: "${NAME:?required}"` guard, and **twenty-four** command-line arguments — one
`--slot-attempt-id` and one `--slot-custody-locator` per slot — which it
forwards verbatim to the session reservation as `"$@"`. There is no production
code that bridges the gap, and there never was: G2-a does not need one, because
its chain carries its own environment inside its own bytes (record 101 §2).

So a plan whose `chain_path` named the tracked chain directly would launch a
chain with ten of its thirteen variables unset. It would exit 1 on the first
`:?required` guard before spending any window time — safe, but a burned night
out of the three the corpus has.

**The mechanism.** A night is armed by pinning a **wrapper**: a generated zsh
file, one per night, written into the night root (the custody directory the
plan calls `custody_root`), which carries that night's whole environment as
literal `export` lines and then hands control to the tracked chain. The
generator is `scripts/gen_derivation_night.py`. In order, the wrapper:

1. **Refuses any night but its own.** It checks that `MEASUREMENT_ROOT` is
   present, absolute and free of control characters, that `MEASUREMENT_HEAD` is
   a 40-character lowercase hex SHA-1, and then that each of `NIGHT_PLAN_ID`,
   `MEASUREMENT_ROOT` and `MEASUREMENT_HEAD` equals the literal frozen into
   these bytes at arm time. It then reads the clone's actual
   `git rev-parse --verify HEAD` and requires it to equal `MEASUREMENT_HEAD`,
   and requires `<MEASUREMENT_ROOT>/.venv/bin/python` to exist and be
   executable.
2. **Exports the thirteen chain variables as literals** — `SESSION_ID`,
   `WINDOW_ID`, `PLAN_ID`, `PLAN_SHA256`, `PLAN`, `EVIDENCE_ROOT_ID`,
   `RUNS_ROOT`, `WINDOW_CUSTODY_ROOT`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN`,
   `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `WINDOW_END_EPOCH_S` — plus six
   more the chain would otherwise default from whatever shell armed the night:
   `SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `SLEEP`
   and `DATE`. The last six are pinned because the driver hands the child
   `os.environ.copy()`, so an inherited `SETTLE_S` from the arming operator's
   shell would silently retime the night. `WINDOW_END_EPOCH_S` is
   `int(t0_epoch_s + window_max_s)` — the same derivation §1.2 does by hand.
   `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON` are the two paths the desk
   writer printed in §0.8, hyphenated filenames and all.
3. **Authenticates the three desk-produced inputs before any window time is
   spent.** For the frozen calibration plan `PLAN`: it must exist, parse as
   JSON, carry a `plan_id` equal to the `PLAN_ID` literal, and hash to the
   `PLAN_SHA256` literal. For `IDENTITY_EPOCH_JSON` and `T1_BINDINGS_JSON`:
   each must exist and hash to its own baked-in SHA-256 literal — the digests
   the desk-inputs writer printed on its paste lines.
4. **Verifies the tracked chain's bytes** — `shasum -a 256` of
   `<CLONE>/scripts/night_chains/calibration_derivation_only.zsh` must equal a
   SHA-256 literal inside the wrapper. This is the link that makes the
   attestation transitive: the plan pins the wrapper's digest, the wrapper's
   own bytes contain the chain's digest, so the plan-pinned digest moves
   whenever the capturing bytes move.
5. **`exec`s the tracked chain** with the twenty-four per-slot bindings as
   argv: `--slot-attempt-id '<SESSION_ID>-dNN'` and
   `--slot-custody-locator '<RUNS_ROOT>/instrument_validation/<SESSION_ID>-dNN'`
   for `dNN` = `d01`…`d12`. `exec`, never `source`: the chain derives its
   repository root from its own `$0` with the line `cd "${0:A:h:h:h}"`, so it
   must run as `$0` at its in-clone path.

Every refusal above prints `FAIL <reason>` to stderr and exits 1. That stream
is the driver's `<NIGHT_ROOT>/night/chain.stderr.log`, and on an agent-free
night it is the only forensic record a 3 a.m. refusal leaves.

**The three emitted files.** One generator run writes exactly three files into
the night root. A **sidecar** here means a small companion file holding another
file's SHA-256 in `shasum` output form — the digest, two spaces, a name:

| File | Role |
|---|---|
| `<NIGHT_ROOT>/chain.zsh` | The wrapper. The plan's `chain_path` must be this exact path. |
| `<NIGHT_ROOT>/chain.zsh.sha256` | The wrapper's sidecar. The plan's `chain_sha256_path` must be this exact path; the driver refuses the night unless the wrapper's bytes still hash to it. |
| `<NIGHT_ROOT>/chain.zsh.chain-source.sha256` | **Advisory only** — the tracked chain's digest, named by its repository-relative path so an operator can run `shasum -a 256 -c` on it by hand from the clone. **Advisory** means nothing reads it at launch: the wrapper carries the same digest as a literal in its own bytes, so deleting or rewriting this file changes nothing about what the night will accept. |

**How the generator cites the chain, and why the operator should care.** Every
reference `gen_derivation_night.py` makes into the tracked chain is an **anchor
text** — one exact line of the chain, quoted in full and held in the
generator's `CHAIN_ANCHORS` table — and never a line number. Examples of the
anchors it holds: `cd "${0:A:h:h:h}"`, `SETTLE_S="${SETTLE_S:-600}"`,
`SLOT_CAPTURE_BUDGET_S="${SLOT_CAPTURE_BUDGET_S:-480}"`, and
`    if (( writer_rc == 0 )); then`. `tests/test_gen_derivation_night.py`
resolves every anchor against the chain's current bytes, so a chain edit that
moves or rewrites a cited line fails a test rather than shipping a false
citation into a night's artifact. Two of those anchors are the chain's
**writer-status dispatch** — its branch on the exact status number a capture
returns, built in full at §2.4 — because the wrapper's window arithmetic
assumes every declared slot is attempted. "A non-valid capture does not stop
the night" is therefore part of the contract the generator depends on, and is
pinned as such rather than left to a reader's assumption. When this runbook and
the code disagree, grep the quoted line: it is the citation that is guaranteed
to still exist.

### 1.1b Arm order: five steps, each depending on the one before

1. **Cut the clone at H** (§0.2), export `$PY`, and record
   `git -C "$MEASUREMENT_ROOT" status --porcelain`; it must be empty (§0.8).
   Then write the two desk inputs with the desk-inputs writer of §0.8 and record its three
   printed lines.
2. **Author the night plan at the STAGING path `$STAGED_PLAN`** (§1.1 table),
   with `chain_path` = `<NIGHT_ROOT>/chain.zsh` and `chain_sha256_path` = that
   path plus `.sha256`. The plan must exist FIRST: the generator reads
   `t0_epoch_s`, `window_max_s`, `custody_root`, `measurement_root`,
   `measurement_head`, `receipt_class`, `chain_path` and `chain_sha256_path`
   out of it, and refuses if `chain_path` is anything else.

   **The plan has two paths, in this order, and confusing them breaks the
   arm.** `--plan` is an INPUT: the generator opens that file and reads the
   eight fields above out of it, so the plan must already exist when step 3
   runs. But §1.4 publishes the night by `os.replace`-ing the staged bytes into
   `<NIGHT_ROOT>/night_plan.json`, and that target **must not pre-exist**. Both
   are true only if authoring, generation and `--verify` all happen at a
   different path from the published one:

   | Phase | Path | Who reads or writes it |
   |---|---|---|
   | author → generate → `--verify` (§1.1b steps 2–4) | `$STAGED_PLAN` = `/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json` | the operator, then `gen_derivation_night.py --plan` |
   | published, at the arm and for the whole night (§1.4) | `$NIGHT_ROOT/night_plan.json` | the watchdog's discovery glob, then the night driver via its `--plan` argument |

   **Nothing is lost by verifying before the move, because the wrapper's bytes
   depend on the plan's CONTENT and never on its path.** `gen_derivation_night.py`
   uses the `--plan` argument for exactly one thing — `json.loads` of the bytes
   at that path — and every value it renders into the wrapper comes from the
   decoded fields (`custody_root`, `measurement_root`, `measurement_head`,
   `t0_epoch_s`, `window_max_s`, `chain_path`, `chain_sha256_path`), not from
   where the file sat. So `--verify` against `$STAGED_PLAN` before the move and
   `--verify` against `$NIGHT_ROOT/night_plan.json` after it re-render the same
   bytes and both print the same digest. §1.4 re-runs `--verify` after the move
   for that reason: it is a free re-assertion, not a second, different check.

   And the staged path is why §0.7's "nothing else is discoverable" survives
   authoring: `/Users/edr/night-plan-staging/<PLAN_ID>/` is not one level below
   `/Users/edr/night-custody`, so the watchdog's `*/night_plan.json` glob never
   sees it, and the night is undiscoverable until §1.4 — after the email.
3. **Generate the wrapper**, run from the measurement clone. Six flags are
   required and there are no others to supply for an ordinary twelve-slot
   night:

   ```zsh
   cd "$MEASUREMENT_ROOT"
   "$PY" -B scripts/gen_derivation_night.py \
     --plan "$STAGED_PLAN" \
     --session-id "$SESSION_ID" \
     --evidence-root-id "$EVIDENCE_ROOT_ID" \
     --calibration-plan "$CALIBRATION_PLAN" \
     --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
     --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json"
   ```

   The last two paths are exactly the ones the desk-inputs writer printed on its paste
   lines in §0.8; paste them rather than retyping them.

   On success it prints `emitted <NIGHT_ROOT>/chain.zsh sha256=<64 hex>` and
   exits 0. Notes on the flags, because getting them wrong is a refusal:
   `--out` defaults to the plan's `chain_path` AND is refused if it is anything
   else, so do not pass it. `--window-id` defaults to the plan's `plan_id`;
   `--runs-root` to `<custody_root>/runs`; `--ledger` to
   `<measurement_root>/runs/calibration_observation_ledger.jsonl`; `--head-pin`
   to `<measurement_root>/configs/calibration/calibration_ledger_head.json` —
   pass any of these four only to override a default, and re-record the value
   if you do. `--slot-count` defaults to 12. There is **no `--repo-root`
   flag**: the generator digests the tracked chain from the clone the night
   will run, i.e. from `plan.measurement_root`, never from the checkout the
   generator happens to execute in. `--evidence-root-id` has no derivable
   default; state its literal value and the record that registers it in the arm
   record alongside `--session-id`.

   **The generator PARSES the two desk-produced JSON inputs; it does not only
   hash them.** Hashing pins WHICH file the night will use. Parsing is what
   tells the operator, at the desk and before any window exists, that the file
   can do its job at all. `identity-epoch.json` must be a JSON object whose keys
   are EXACTLY the six `IDENTITY_EPOCH_FIELDS`, with every value present and
   scalar — a non-empty string, or a number, because `sampling_interval_ms` is
   an integer in every issued acceptance — and whose `power_policy` is exactly
   `ac_high_power`. The three refusals name what is wrong: `identity epoch json
   keys are not exactly the six IDENTITY_EPOCH_FIELDS (missing=[…],
   extra=[…])`, `identity epoch json fields are empty or not scalar: […]`, and
   `identity epoch power_policy is '<x>', but the chain captures with
   --power-policy ac_high_power; the writer would refuse at d01 with the settle
   already spent`. `t1-bindings.json` must parse as a JSON object, and nothing
   more is asserted about its fields, because the ledger — not this tool — owns
   that block's shape.

   A file written by §0.8's desk-inputs writer passes all three by construction: its
   `--power-policy` default is imported from this generator's own
   `CHAIN_POWER_POLICY`, and it refuses an incomplete vector before writing.
   The generator's checks remain the ones that bind, because a hand-edited or
   hand-copied file reaches it by other routes.

   That last message states the forcing problem for all three. The chain
   hardcodes `--power-policy ac_high_power` on every capture, and the capture writer
   compares its measured bindings against the reserved slot's identity epoch,
   whose contents are copied verbatim from this very file. So an epoch naming a
   different policy used to fail at `d01`: after the driver's gate work, after
   the reservation, after 600 s of settle, with the session already open and
   eleven further slots that would fail the same way. The same JSON handed to
   the generator at the desk now costs a re-written file and no window time.
   **Learn it at the desk, not at d01** is the whole of the design.

   **The ledger's ceiling on declared slots.** A `--slot-count` above
   `MAX_DECLARED_SESSION_SLOTS` (99, in `joulewise/calibration_ledger.py`) is
   refused here — `slot count <n> exceeds the ledger's
   MAX_DECLARED_SESSION_SLOTS (99); the reservation would refuse it after the
   settle` — for the same reason: the reservation would otherwise refuse it
   INSIDE the window, after the settle, with the night spent. Twelve is the only
   value these nights use; the ceiling matters solely as the reason a large
   number fails at the desk instead of at 03:10.
4. **Re-derive and assert byte equality** — the arm-time **tripwire**, meaning
   a check that writes nothing and whose only job is to fail loudly if an input
   drifted between generation and arming. Same command as step 3 plus
   `--verify`:

   ```zsh
   "$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
     --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
     --calibration-plan "$CALIBRATION_PLAN" \
     --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
     --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" \
     --verify
   ```

   It renders the wrapper again from the same inputs and compares both the
   wrapper and its sidecar byte-for-byte with the files installed at the plan's
   `chain_path` and `chain_sha256_path` — that is, in the NIGHT ROOT. Only the
   plan is staged; the wrapper it describes is written where the night will run
   it. **rc 0**
   prints `VERIFIED <path> sha256=<64 hex>`. **rc 3** prints `FAIL wrapper
   bytes differ from re-derivation: re-derived sha256=… installed sha256=… at
   <path>`, with `<absent>` in place of the installed digest if the file is
   missing. Emission is deterministic, so a difference means an input drifted —
   the tracked chain, the frozen calibration plan, the identity-epoch or
   T1-bindings bytes, or the plan's own coordinates. Do not re-emit over the
   difference; find it. Re-running the §0.8 desk-inputs writer with `--force` between
   emission and arming is one way to cause exactly this, which is why that flag
   is not reflexive.
5. **Syntax-check the wrapper, then install the plan.**

   ```zsh
   /bin/zsh -n "$NIGHT_ROOT/chain.zsh"
   ```

   `zsh -n` parses the file and runs none of it; rc 0 is the only acceptable
   result. Then install the plan (§1.4). From here the plan pins the wrapper's
   digest and the wrapper pins the chain's, so the plan's attestation reaches
   the bytes that actually capture.

One wrapper per night, and one night per wrapper: any further night — the FAIL
route's nights two and three, or the m < 6 branch's second equivalence night
(§2.5) — means its own plan, its own session ID and its own wrapper, because
the generator refuses to reuse one wrapper across plans. How many nights
follow this one is decided by §2.5 after this night closes, and is not fixed
in advance.

### 1.2 WINDOW_MAX_S, with the arithmetic

The chain's programmed schedule uses its own defaults, read from
`scripts/night_chains/calibration_derivation_only.zsh`:
`SLOT_COUNT=12`, `SETTLE_S=600`, `SLOT_CADENCE_S=600`, `SLOT_CAPTURE_BUDGET_S=480`.

The night's shape is: one settle, then twelve captures at a **start-to-start**
cadence — meaning slot `d(k+1)` starts 600 s after slot `dk` STARTED, not after
it finished, and a long capture is never caught up by compressing a later slot.
So the programmed span from chain start to the end of the last capture's budget
is:

```
  settle                               600 s
+ 11 cadence gaps (d01 → d12)   11 × 600 = 6600 s
+ the last capture's budget            480 s
------------------------------------------------
  programmed span                     7680 s  = 2 h 08 min
```

7680 s is the same 128 minutes the pre-registration states for a 12-slot night,
which is the cross-check that this arithmetic matches the registered design.

Margin on top of the programmed span covers three things the 7680 s does not:
the chain's pre-settle work (input preflight, the `--phase pre-reserve`
readiness check, and the session reservation, all of which run BEFORE the
settle so that an unusable declaration costs no window time), per-capture
overrun beyond 600 s pushing later slots later, and the driver's own work
before it starts the chain. Allocate **1320 s (22 min)**:

```
WINDOW_MAX_S = 7680 + 1320 = 9000 s   (2 h 30 min)
```

This is an operational allocation, not a measured completion guarantee. Do not
shorten the settle, the cadence, the slot count or the capture budget to fit a
window; shorten nothing and move `t0` earlier instead.

**The generator's floor under this allocation.** `gen_derivation_night.py`
refuses to emit a wrapper at all unless the window can hold the programmed
span plus a **pre-settle allowance** of 300 s. The pre-settle allowance is the
first of the three margin items above, isolated and made mandatory: the time
spent INSIDE the window but BEFORE the settle begins — the chain's input
preflight, its `--phase pre-reserve` readiness check and the session
reservation, plus the driver's own gate work before it starts the chain at all.
The refusal is arithmetic, and its message states both numbers:

```
required window = programmed span + pre-settle allowance
                = 7680 + 300
                = 7980 s          ← the generator's hard floor for 12 slots
```

`window_max_s 3600 < required 7680 + 300 = 7980 s: … lengthen the window rather
than shortening the schedule` is what a too-short window prints. **7980 is a
floor, not a recommendation: 9000 s remains the value to author**, because 7980
leaves nothing for the second margin item — per-capture overrun beyond 600 s,
which pushes every later slot later and is the realistic way a night loses its
last slot to `window_exhausted`. A `--allow-slot-count` departure recomputes
this floor from the new slot count rather than bypassing it.

Those are the registration's three durations, and it states all three together
precisely because confusing them is how a night opens a session it cannot
finish: **programmed span 7680 s (128 min)**, **generator minimum 7980 s
(133 min)**, **armed `window_max_s` 9000 s (150 min)**. A fourth number,
210 min, belongs to none of them — it is the install span 03:00–06:30 of §1.3,
an operator-facing block of the clock, and a 150 min window sits inside it with
an hour to spare. The two measure different things and neither is derived from
the other.

**The dead-man check.** The rule is `t0 + window_max_s + 300 < the next 07:00`,
where 300 s is the **courier allowance** and 07:00 is the dead-man minute. Two
different 300 s budgets appear in this section; they are unrelated and happen
to share a number. The pre-settle allowance above is spent INSIDE the window,
before the settle. The courier allowance is spent AFTER the window ends: it is
the time the driver reserves for the courier to send the night's result before
the dead-man fires. Neither is a substitute for the other, and widening the
window consumes dead-man slack while widening nothing else. Worked
with real numbers, using the coordinates the prior night's arm runbook (record 12, `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`) pinned
purely as an arithmetic example (`t0 = 2026-09-12 02:56:00 PDT`, epoch
`1789206960`; that morning's 07:00 is epoch `1789221600`):

```
t0                    = 1789206960   (02:56:00 PDT)
t0 + 9000             = 1789215960   (05:26:00 PDT)   ← acquisition allocation ends
t0 + 9000 + 300       = 1789216260   (05:31:00 PDT)   ← courier deadline
next 07:00            = 1789221600   (07:00:00 PDT)
1789216260 < 1789221600                               ✓ PASS, 89 minutes of slack

strict maximum window_max_s for this t0
  = 1789221600 - 1789206960 - 301 = 14339 s
9000 ≤ 14339                                          ✓
```

(The `-301` is `-300` for the courier and `-1` because the comparison is
strict. All four epoch↔local conversions above were verified with
`TZ=America/Los_Angeles date -r <epoch>` when this runbook was drafted.)

The chain's own end boundary follows: `WINDOW_END_EPOCH_S = t0 + WINDOW_MAX_S`
= `1789215960` in the example. Check that the last slot is admitted rather than
skipped — the chain refuses to START a slot whose 480 s budget would cross that
end.

**The schedule does not begin at `t0`, so name the gap before doing the
arithmetic.** Call it **Δ**: the elapsed time between the plan's `t0` and the
moment the chain's settle actually begins. Three things happen inside Δ, in
this order, and none is instantaneous:

1. **The driver's gate work.** The night gate evaluates its conditions,
   authenticates the plan and the registration, verifies the wrapper's bytes
   against its sidecar, and only then launches the wrapper.
2. **The chain preflight.** The wrapper's own checks (one `git rev-parse`, the
   three input digests, one `shasum` of the tracked chain — all sub-second on
   this hardware), then the chain's input preflight and its `--phase
   pre-reserve` readiness check.
3. **The session reservation.** The ledger call that opens the
   `derivation`-kind session and declares all twelve slots. The chain logs
   `chain_start` only after this returns; the settle begins immediately after.

Items 2 and 3 plus the driver's launch are exactly what the generator's 300 s
pre-settle allowance is a floor for; item 1 is the driver's own work. Every
time in the programmed schedule is therefore `t0 + Δ + <programmed offset>`:

```
d01 start      = t0 + Δ + 600
d12 start      = t0 + Δ + 600 + 11 × 600 = t0 + Δ + 7200
d12 budget end = t0 + Δ + 7680
```

and the admission test the chain actually runs — it refuses the slot when
`slot_start + 480 > WINDOW_END_EPOCH_S` — collapses to one inequality in Δ:

```
t0 + Δ + 7680  ≤  t0 + 9000
          Δ    ≤  1320 s   (22 min)
```

**That is what the 1320 s allocated above buys: 22 minutes of Δ before `d12` is
dropped.** The generator's mandatory 300 s covers only the part of Δ it can
reason about; the remaining 1020 s is the operator's headroom, and the second
margin item eats it from the other end — a capture that overruns 600 s pushes
every later slot later, which is arithmetically the same as a larger Δ.

Worked at Δ = 0 — the idealisation, labelled as one — and then at the largest Δ
that still admits `d12`, using the same example coordinates:

```
Δ = 0 s      d12 start      = t0 + 7200 = 1789214160  (04:56:00 PDT)
             d12 budget end = t0 + 7680 = 1789214640  (05:04:00 PDT)
             05:04:00 ≤ window end 05:26:00        ✓ admitted, 22 min unused

Δ = 1320 s   d12 budget end = t0 + 9000 = 1789215960  (05:26:00 PDT)
             05:26:00 ≤ window end 05:26:00        ✓ admitted, nothing left

Δ = 1321 s   d12 budget end = t0 + 9001 = 1789215961  (05:26:01 PDT)
             05:26:01 >  window end 05:26:00        ✗ d12 recorded unused
```

Δ cannot be measured at the desk — it is whatever the machine takes that night —
so the operator's rule is the one those three lines state: a night whose chain
starts more than 22 minutes after `t0` loses `d12`, and
`slot_unused slot=d12 reason=window_exhausted` in the chain log is the evidence
that it did. The realized Δ of a finished night is readable at the harvest: the
`chain_start` line's timestamp in `derivation-chain.log` minus `t0` (§2.1).

If your chosen `<t0>` fails either check, move `<t0>` earlier. Never raise
`window_max_s` past the strict maximum and never move the dead-man.

### 1.3 Install span and the exit boundary

Install BOTH agents on the calendar day BEFORE `t0`, between **03:00 and 06:30
local**. Never install in the 07:xx hour. The first 07:00 dead-man firing after
installation should stand down, because the night's completion time has not yet
arrived; that stand-down line in `night.log` is expected evidence, not a fault.

The activation's absolute exit boundary is `t0 − 25 minutes` (§0.6). Finish
recording and exit before it. Do not remain resident until `t0`.

`[UNVERIFIED: whether a 06:05 "Block B last start" cutoff should carry over to
these nights. Record 12 (`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`) §"Pins and preconditions" marks its own 06:05 rule
PROPOSED for that runbook and notes runbook 67 contains no such rule. Treat it
as the recommended operational cutoff, not a ratified gate: if the email-and-
install block cannot begin by 06:05, do not arm — author the next night's
notice instead.]`

### 1.4 Email, then arm

Order is fixed: **after H is committed and pushed, after any prior stub or plan
root is retired, and BEFORE the plan is moved into its discoverable place.**
There is no minimum notice interval beyond that ordering.

Send Ed the night notice with the activation's mail tool, under its standing
email authority, containing: plan ID; class `DIAGNOSTIC_NO_PACK`; the full H
twice; the handback commit (= H); measurement root, night custody root and runs
root; `t0` local and UTC; `window_max_s` = 9000; the emitted wrapper's digest
and its sidecar path (§1.1a), and the tracked chain's digest the wrapper pins;
the two desk inputs' paths and digests from §0.8's paste lines; the courier
deadline; the exit boundary; the planned install span; and the cancellation
instruction — **launch needs no action from Ed unless he replies NO**. Record
the actual send acceptance, time, message and thread IDs, and which NO relay is
available. A headless activation that cannot read the thread must say so; it
cannot certify that no reply went unseen. Write that evidence to
`$STAGE/notice-evidence.txt` before going on — the arm block below refuses to
publish without it, which is what keeps "email, THEN arm" from being a matter
of memory. Recheck owner-authored open `directive` issues immediately before
publication.

#### The arm itself, in one foreground block

These are the commands, adapted from the prior night's arm runbook, record 12,
`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`,
§"Block B" — the only executed template this project has for a real install.
Two things are changed from it and both are named here: the plan assertions are
this night's (`DIAGNOSTIC_NO_PACK`, `window_max_s = 9000`, no pack block, and a
`registration_path` equal to the committed pre-registration of §0.5), and the
chain re-check is this lane's wrapper `--verify` of §1.1b step 4 rather than
that runbook's G2-a runsheet render.

At 02:56 PDT on 2026-09-11, the driver crashed before any gate because
`python3` found through PATH selected macOS Python 3.9.6, which cannot import
`datetime.UTC`. Each LaunchAgent now names an absolute Python interpreter
(the executable running the driver). The installer flag `--python "$PY"`
pins that path to the project interpreter defined in §0.2. Install and
`--render-only` default to `<measurement_root>/.venv/bin/python` when
`--python` is omitted. Even a stub checkout needs that venv or an absolute
path to a Python whose version is at least `MIN_PYTHON` in `scripts/run_night.py`
(currently 3.11) and whose driver preflight exits 0 from the stub checkout.
The chain's interpreter remains `<measurement_root>/.venv/bin/python`,
independently of this driver pin.

Before installation, the **driver preflight** loads the driver module and
every project module it imports at module scope, under the job's interpreter
and PATH, and parses the plan. Its JSON `modules` list names the driver and
those direct module-scope project imports; keep that success line in the arm
record. It does not exercise functions' lazy imports inside `joulewise` or run
the night's gates or measurements. The installer refuses a missing interpreter,
a version below `MIN_PYTHON`, or a failed preflight.

Run it only after the notice is sent and its evidence is written. Everything
before the `os.replace` is reversible by doing nothing; everything after it is
an armed night.

```zsh
set -euo pipefail
: "${H:?}" "${PY:?}" "${MEASUREMENT_ROOT:?}" "${NIGHT_ROOT:?}" "${STAGE:?}" "${STAGED_PLAN:?}"
: "${SESSION_ID:?}" "${EVIDENCE_ROOT_ID:?}" "${CALIBRATION_PLAN:?}"
export NIGHT_HOUR=<t0's local hour, two digits or fewer, never the dead-man hour 7>
export NIGHT_MINUTE=<t0's local minute>
cd "$MEASUREMENT_ROOT"

# 1. The pins still hold, and the notice really went out.
test -s "$STAGE/notice-evidence.txt"
test "$(git rev-parse HEAD)" = "$H"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git fetch origin main
git merge-base --is-ancestor "$H" origin/main

# 2. The wrapper still re-derives to the installed bytes (§1.1b step 4).
"$PY" -B scripts/gen_derivation_night.py --plan "$STAGED_PLAN" \
  --session-id "$SESSION_ID" --evidence-root-id "$EVIDENCE_ROOT_ID" \
  --calibration-plan "$CALIBRATION_PLAN" \
  --identity-epoch-json "$NIGHT_ROOT/identity-epoch.json" \
  --t1-bindings-json "$NIGHT_ROOT/t1-bindings.json" \
  --verify

# 3. The staged plan says what this night is, and the move is possible.
cp "$STAGED_PLAN" "$STAGE/arm-night_plan.json"
"$PY" -B - <<'PY'
import json, os, time
from pathlib import Path
from joulewise.night_gate import NightPlan
plan = NightPlan.from_mapping(json.loads(Path(os.environ['STAGED_PLAN']).read_text()))
assert plan.repo_head == plan.measurement_head == os.environ['H']
assert plan.measurement_root == os.environ['MEASUREMENT_ROOT']
assert plan.custody_root == os.environ['NIGHT_ROOT']
assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'
assert plan.window_max_s == 9000
assert plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'
assert plan.chain_sha256_path == plan.chain_path + '.sha256'
assert plan.registration_path.endswith(
    'configs/calibration/preregistration_d079_epoch_25g83_rev1.md')
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600
assert 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
assert time.time() < plan.t0_epoch_s - 1500          # still before the exit boundary
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS')
PY

# 4. The final raw census, immediately before publication (§0.6).
ps -axo pid,ppid,command | grep -E 'claude (daemon run|bg-spare|bg-pty-host)|--resume' || true

# 5. Publication: the one irreversible instant.
"$PY" -B - <<'PY'
import os
from pathlib import Path
target = Path(os.environ['NIGHT_ROOT']) / 'night_plan.json'
assert not target.exists() and not target.is_symlink()
os.replace(os.environ['STAGED_PLAN'], target)
PY

# 6. Install both agents FROM the clone.
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" --python "$PY"

# 7. Inspect what was actually installed, and baseline the night directory.
launchctl list | grep joulewise
"$PY" -B - <<'PY'
import json, os, subprocess
from pathlib import Path
labels = {line.split()[-1] for line in
          subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps(
    [{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns}
     for p in entries], indent=2))
PY
plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist
plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist
cmp "$NIGHT_ROOT/night_plan.json" "$STAGE/arm-night_plan.json"
```

Read both `plutil` dumps against four things and record the answers: each
label's `StartCalendarInterval` (the night's `t0` hour and minute, and the
dead-man's fixed minute), `WorkingDirectory` (the clone), the exact driver,
plan and courier argv, and `RunAtLoad=false`. `install_night_agent.sh` refuses
`--hour 7` outright, printing `refusing --hour <h>: it is the dead-man hour`,
so the dead-man's own firing can never be the night's.

**If any step AFTER publication fails**, recover in this exact order and record
every return code — the same `--uninstall` / preserve / compare / unpublish
sequence record 12 §"Block B" uses:

```zsh
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" \
  --hour "$NIGHT_HOUR" --minute "$NIGHT_MINUTE" --uninstall
cp "$NIGHT_ROOT/night_plan.json" "$STAGE/failed-night_plan.json"
cmp "$STAGE/failed-night_plan.json" "$STAGE/arm-night_plan.json"
rm "$NIGHT_ROOT/night_plan.json"
```

The `cmp` before the `rm` is the point of keeping `arm-night_plan.json`: it
proves the bytes that were briefly discoverable are the bytes that were
reviewed, so the failed attempt is documentable rather than merely undone. If
recovery itself fails, record the surviving labels and the discoverable plan
and escalate; never claim nothing was armed.

### 1.5 Record and exit

Write the arm record and its evidence directory in the authorized linked
bookkeeping worktree, commit, push, and exit before `t0 − 25 min`. No own
background work may remain alive.

**The frozen checkout triple, exactly as the contract defines it.** It is three
fields and only three: `(plan_id, root, head)`. The relaunch prompt carries
them at line 9 — "Frozen checkout triples `(plan_id, root, head)` for this
activation: `@@FENCED_CHECKOUTS@@`" (`docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`) —
and the watchdog RENDERS that placeholder itself, at every launch, as a
deterministic JSON list of the canonical repository plus every authored,
not-completed v2 plan's measurement root and head
(`docs/process/MAGISTRATE_WATCHDOG.md`, §"Complete write inventory"). The
successor activation does not choose the list and this runbook cannot widen it:

| Field | This night's value |
|---|---|
| `plan_id` | `$PLAN_ID` — e.g. `d079-epoch-25g83-derivation-n1-<YYYYMMDD>` (§0.2) |
| `root` | `$MEASUREMENT_ROOT` — the fresh clone of §0.2, `/Users/edr/JouleWise-measurement-<NIGHT_DATE>-derivation` |
| `head` | `$H` — the 40-character reviewed head of §0.1 |

The triple's purpose is a fence, not a handover: the prompt forbids Git
operations in the canonical root and forbids MOVING any listed measurement
root, because a post-arm move invalidates the plan's pin and forces a re-arm
(same section). Everything the morning harvest additionally needs is
reconstructed from these three values plus the night root's own contents, and
§2.0 does exactly that. Still write all of it into the arm record as well: the
reconstruction is the successor's floor, not a licence to record less.

---

## 2. Morning harvest

The next activation harvests only after the plan span's closed completion
boundary has passed, the courier marker exists, and recorded process ownership
is clear. An early chain exit alone does not authorize early resumption, and
`courier.sent` alone clears neither chain nor campaign ownership.

### 2.0 Rebuild the night's coordinates from the frozen triple

The harvesting activation starts with three values (§1.5) and needs eight. Run
this first; every command in §2 interpolates what it exports. Four values are
derivations, and three are read back out of the wrapper the night actually ran
— which is stronger than copying them from the arm record, because the wrapper
is the file whose digest the plan pinned:

```zsh
set -euo pipefail
export PLAN_ID=<plan_id from the frozen triple>
export MEASUREMENT_ROOT=<root from the frozen triple>
export H=<head from the frozen triple>
export PY="$MEASUREMENT_ROOT/.venv/bin/python"
export NIGHT_ROOT="/Users/edr/night-custody/$PLAN_ID"
export WINDOW_CUSTODY_ROOT="$NIGHT_ROOT"
export CALIBRATION_LEDGER="$MEASUREMENT_ROOT/runs/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$MEASUREMENT_ROOT/configs/calibration/calibration_ledger_head.json"

# The wrapper is the pinned artifact; check its bytes before reading anything out of it.
test -x "$PY"
test "$(git -C "$MEASUREMENT_ROOT" rev-parse HEAD)" = "$H"
( cd "$NIGHT_ROOT" && shasum -a 256 -c chain.zsh.sha256 )

# Its export lines are single-quoted literals the generator emitted.
eval "$(grep -E '^export (SESSION_ID|EVIDENCE_ROOT_ID|PLAN|RUNS_ROOT)=' "$NIGHT_ROOT/chain.zsh")"
export SESSION_ID EVIDENCE_ROOT_ID PLAN RUNS_ROOT
print -rl -- "$NIGHT_ROOT" "$WINDOW_CUSTODY_ROOT" "$CALIBRATION_LEDGER" \
  "$LEDGER_HEAD_PIN" "$SESSION_ID" "$EVIDENCE_ROOT_ID" "$PLAN" "$RUNS_ROOT"
```

Why each is what it is, so the reconstruction can be checked rather than
trusted:

| Value | Where it comes from |
|---|---|
| `NIGHT_ROOT` | The `/Users/edr/night-custody/<PLAN_ID>` convention of §0.2. Confirm it against the night's own plan: `$NIGHT_ROOT/night_plan.json` must exist and its `custody_root` must equal `$NIGHT_ROOT`. |
| `WINDOW_CUSTODY_ROOT` | The night root itself. The generator sets the wrapper's `WINDOW_CUSTODY_ROOT` export from `plan.custody_root` and nothing else, so the two are the same directory under two names — §2.1's `<WINDOW_CUSTODY_ROOT>/operator_logs/derivation-chain.log` is inside the night root. |
| `CALIBRATION_LEDGER` | `<measurement_root>/runs/calibration_observation_ledger.jsonl` — the generator's `--ledger` default, and the value §0.2 exported at the arm. |
| `LEDGER_HEAD_PIN` | `<measurement_root>/configs/calibration/calibration_ledger_head.json` — the generator's `--head-pin` default. |
| `SESSION_ID`, `EVIDENCE_ROOT_ID`, `PLAN` | Not derivable from anything: they were the operator's literals at §0.2 and §1.1b step 3. The wrapper carries all three as `export` lines, which is why the block above verifies the wrapper against its sidecar first and only then reads them. `PLAN` is the frozen calibration plan `$CALIBRATION_PLAN`. |
| `RUNS_ROOT` | `<custody_root>/runs` unless the arm overrode `--runs-root`; taken from the wrapper for that reason, not assumed. |

If the sidecar check fails, stop: the bytes in the night root are not the bytes
the plan pinned, and nothing read out of them may be used. Recover the
coordinates from the arm record instead and treat the discrepancy as a finding.

### 2.1 What to read

| Artifact | What it establishes |
|---|---|
| `<NIGHT_ROOT>/night.log` | The driver's own log: the prior morning's dead-man stand-down line, then this night's gate verdict line. |
| `<NIGHT_ROOT>/night/result.json` | The verdict, the chain's exit code, and where the receipt or refusal is. Read this first; it directs the rest. |
| `<NIGHT_ROOT>/night/receipt.json` or `refusal.json` | The C1–C5 condition rows, or the refusal reason and detail. C2 is `NOT_APPLICABLE`/`no_pack_by_design` for this class. |
| `<WINDOW_CUSTODY_ROOT>/operator_logs/derivation-chain.log` | The chain's own lifecycle: `session_open kind=derivation slots=12`, `chain_start` (its timestamp minus `t0` is the night's realized Δ, §1.2), `settle_complete`, then twelve `slot_start` lines each answered by exactly one of `slot_end … disposition=valid`, `slot_end … disposition=non-valid` (a normal record, §2.4) or `slot_refused slot=dNN rc=<n>` (the night stopped here, session OPEN), and finally `derivation_night_complete slots=12` — or `slot_unused … reason=window_exhausted` followed by `session_abort`. |
| `<NIGHT_ROOT>/night/chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`, `chain.stderr.log` | Launchd lineage, actual chain termination, and the production census the driver takes at launch and every 30 s. |
| `<NIGHT_ROOT>/night/courier.sent`, `courier.json`, `courier.heartbeat` | Send time and message ID; verify the email separately in Ed's inbox. |
| launchd `.out`/`.err` for both labels | Present or absent, complete bytes, sizes, nanosecond mtimes — compare against the arm-time baseline. |
| `check --session-ids <SESSION_ID>` (§2.2) | The night's session kind, state, terminality, declared and filled slot counts, exclusion counts by mechanism. |
| The night's own ledger rows in `$CALIBRATION_LEDGER`, and each capture's `manifest.json` and `instrument_evidence.json` under `$RUNS_ROOT` | The twelve slot outcomes, and — for the captures that are `valid` and whose stored anchor record resolves — the **retained values** the equivalence rule compares (§2.5). Reading these AFTER this night has closed is what the check IS; §2.3 draws the line. |

Preserve the full custody root byte-exact outside watchdog discovery before any
removal, and keep a separate `lstat` inventory of the original with sizes and
`mtime_ns`; a backup's copied timestamps do not substitute for it.

### 2.2 The one mid-campaign query, and what it may not tell you

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --session-ids "$SESSION_ID"
echo "rc=$?"
```

With at least one non-empty `--session-ids`, `check` prints the epoch-watch
table byte-identically to §0.3 and then APPENDS a **registration dry run**
(`registration_dry_run`): for each named session its kind, its state and whether
that state is terminal, how many slots it declared and how many are filled, how
many captures are excluded under each named mechanism, then how many prior-set
prefix rows are pending or unresolved, and finally the line `registration
admissible for prepare-candidate: yes|no` with a `blocker:` line for each
obstacle. Every field is a count, a state name, or a mechanism name.

**Return code when a session is named: 0 = admissible, 5 = inadmissible**
(`DRY_RUN_INADMISSIBLE_EXIT = 5`; `check` returns the dry run's code,
deliberately, so that a drifted epoch does not mask the question actually
asked). The code answers ONE question — whether the named sessions are
admissible for `prepare-candidate` — and it is neither the equivalence check
nor an anticipation of it. On the FAIL route, where this night is registration
night one and two more follow, the expected code after nights one and two is
**5**, with the blocker naming the sessions that are not yet terminal; that is
the correct mid-campaign answer there. On the PASS route nothing is ever
prepared, and this code decides nothing.

### 2.3 When a value may be read, and when it may not

The boundary moved with directive issue 316, and it is a boundary in TIME, not
a prohibition on looking at all. Three rules, in force in this order:

1. **While the night is running, nothing is read.** No `b_fiducial_s`, no
   minimum, maximum, range, mean or SD, no screen, no statistic, no comparison
   against one — not from the bundles, not from the ledger rows, not "just to
   see if the night is working". The night is agent-free by construction
   (§0.6): no one is present to read anything, and no agent session may be
   launched to look.
2. **Once this night's ledger session is terminal, the retained values ARE
   read**, and §2.5 is what they are read for. Terminal means the session's
   last declared slot is final or the session was aborted. This is the change
   revision 6 carries, and it is licensed by the ruling rather than by the
   desk: the equivalence rule is fixed at §2.5, in writing, before the night
   runs, so reading afterwards selects nothing — nothing is left to choose.
3. **On the FAIL route only, the derivation's blindness fence resumes.**
   Nights two and three are captured and harvested with no corpus statistic
   computed, and that fence is installed in code rather than left to
   discipline: `prepare-candidate` refuses while any session named in the
   registration is not terminal, and names the session it found open. It is
   why the pre-registration fixes membership, exclusion mechanisms, stopping
   and analysis before the data exists — so that nothing can be chosen after
   seeing values.

Whether a capture's bound exceeded the level screen `0.032898493715362` IS
recorded in each capture's hashed evidence as a diagnostic. That recorded
boolean is NOT the equivalence check and never stands in for it: the check
compares every retained value against that screen AND the night's own range
against the bracket screen, computed from the values themselves (§2.5).

### 2.4 The writer-status dispatch: how a slot ends, and how a night ends early

Every capture hands the chain a status number, and the chain **dispatches** on
it — meaning it branches on the exact value rather than treating "non-zero" as
a single outcome. The three branches are not interchangeable, and the harvest
reads a different thing for each:

| Writer status | The ledger row | Chain log line | What the night does |
|---|---|---|---|
| `0` | finalized, disposition `valid` | `slot_end slot=dNN disposition=valid` | Continues to the next declared slot on the unchanged start-to-start cadence. |
| `1` | **finalized**, disposition not `valid` | `slot_end slot=dNN disposition=non-valid` | **Continues, identically.** This is a normal record, not a failure. |
| `≥ 2` | **not finalized** | `slot_refused slot=dNN rc=<status>` | **Stops the night, leaving the session OPEN.** The chain exits with the capture writer's own status. |

**Why a non-valid capture does not end the night.** The writer exits 1 when the
capture's disposition is not `valid` and 0 when it is, and the ledger row is
FINALIZED either way. An ordinary-invalid capture is a legitimate outcome the
pre-registration already handles, by named-mechanism exclusion at issuance —
and derivation slots are INDEPENDENT of one another: none is an endpoint that
another depends on, unlike a bracket session's two ends. So one non-valid
capture must never cost the captures after it. The chain runs the capture writer as an
`if` condition for exactly this reason, so that `set -e` cannot exit on status 1
before the dispatch is reached. **Expect `disposition=non-valid` lines in a
healthy night's log** — the pre-registration's own projection assumes a valid
rate near 30/38 — and record their count without reading a value.

**Why a refusal does end it.** Status 2 is the capture writer's refusal exit
(`emit_refusal`); anything above it is a crash. In both cases the row is NOT
finalized, so continuing would write later slots into a session whose declared
list has a hole nothing accounts for. The chain stops instead — and
deliberately does NOT call `abort-session`. It leaves the session OPEN so that
what this night amounts to is decided at the desk by a person reading the
refusal, rather than by the chain's own guess at 3 a.m.

**Operator action on `slot_refused` — desk recovery, never a retry.** *Desk
recovery* means the recovery tool run by the operator, at the desk, after the
night is over, against the measurement clone: never inside the window, and
never as a re-arm of the same night.

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/recover_calibration_ledger.py \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  abort-session --session-id "$SESSION_ID" --plan "$PLAN" \
  --reason "<the named reason this night actually stopped>"
```

Read the refusal in `chain.stderr.log` and name THAT as the reason. Do not
reach for `window_exhausted`: that is the window's reason and belongs to the
chain's own abort path below. Until the session is closed the ledger head does
not settle, so §3 item 4 bites — the next night cannot open at head-equals-pin,
and a refused night blocks its successor until the desk clears it.

**The other early end: `window_exhausted`.**

If the chain could not reach every slot it logs `slot_unused slot=dNN
reason=window_exhausted`, calls `recover_calibration_ledger.py … abort-session
--reason window_exhausted`, and exits 0. An aborted session IS terminal, and
its finalized observations remain in the prior set.

The correct response is: record the unused count, and **do nothing else**.
Every night runs all twelve declared slots regardless of interim values, and
no top-up, retry, early stop or outcome-driven extra night is permitted. A
night that lost slots to the window simply retained fewer captures. That
shortfall is not repaired; it is an INPUT to §2.5, whose `m < 6` branch is the
one place a further night can be required, and it is required by a rule fixed
before the night ran rather than chosen after it. On the FAIL route a
shortfall is resolved at §4, in the open, under Ed's written ruling. Do not
add a night to make the numbers work.

Everything else that can fail mid-night — a refused readiness check, a refused
reservation, a `slot_refused` dispatch — stops the chain with the session still
OPEN, either under `set -e` or by the dispatch's own `exit`. The answer is the
same in every case: desk recovery with the named reason, above. Never a retry
inside the window.

---

### 2.5 The epoch-equivalence check — the rule, its constants, and the one action each outcome takes

This section is the reason the night ran. The EPOCH-EQUIVALENCE CHECK is one
comparison: the night's retained values, captured on the new operating-system
build, are held against the envelope the acceptance in force already carries
from the old build; if they sit inside it, the build change did not move the
instrument. Its rule was fixed in writing before the night was armed, by the owner's directive issue 316 of 2026-09-10,
transcribed as revision 2 of
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` and as the dated
Ed addendum under D-102 in `docs/decision_log.md`. Nothing here is decided at
the desk; the desk applies it.

**The question the check asks.** Did the operating-system point release move
the clock-anchor bound outside the envelope this instrument was already
characterised against? It is an instrument question, not a derivation: the
check builds no corpus, computes no successor statistic, and issues nothing.

#### The three inputs

- **Retained value** — the `b_fiducial_s` (a capture's fiducial bound in
  seconds) of one capture of this night that BOTH carries ledger disposition
  `valid` AND resolves under anchor-v3 replay: its stored `clock_anchor`
  record was written by the anchor-v3 estimator and is not
  `affine_clock_fit_empty`. A capture that is `ordinary-invalid`, that was
  refused (`slot_refused`), or whose slot the window never reached
  (`window_exhausted`) is not retained and contributes no value. The value is
  the ledger row's `exact_bound_lexeme_s`, which the capture's authenticated
  `instrument_evidence.json` must carry identically — read both and refuse the
  night's numbers if they differ.
- **Retained m** — how many retained values this night produced. Issue 316's
  words: "Retained m = the night's valid, resolved captures (anchor-v3 replay
  resolved, not window_exhausted or slot_refused)."
- **Reference envelope** — the comparators the acceptance in force,
  `d079_calibration_acceptance_v2_n17_r6`, already carries, in the OPERATIVE
  form the validator uses. Issue 316 fixes that choice: "if the validator's
  operative screen differs from the raw range (the never-zero floor), the
  operative value is the one used."

#### The reference envelope, as constants, with their sources

Each comparator exists in two forms: the raw corpus statistic, and the
operative constant — the raw statistic rounded to the fixed decimal place the
artifact registers for it. The operative constant is the comparator in the
rule; the raw statistic is printed beside it so the difference is visible.

| Quantity | Operative constant the rule uses (s) | Raw corpus statistic (s) | Where each is read |
|---|---|---|---|
| Level screen (corpus maximum) | `0.032898493715362` | `0.03289849371536248` | Operative: `joulewise/calibration_bracketing.py`, `_D102_N17_DERIVATION["operatives"]["preflight_level_screen_s"]`, bound to this acceptance id through `_D102_GENERATION_DERIVATIONS`; same lexeme in the artifact at `decimal_derivation.ratified_operatives.preflight_level_screen_s` and at `decimal_derivation.rounding.preflight_level_screen`, whose `numeric_role` is `operative_comparator`. Raw: the artifact's `decimal_derivation.source_statistics.maximum_s`. |
| Bracket screen (corpus range) | `0.009724` | `0.00972358928879385` | Operative: the same validator row, `operatives["bracket_screen_s"]`; artifact `decimal_derivation.ratified_operatives.bracket_screen_s` and `decimal_derivation.rounding.operative_bracket_screen`, `numeric_role` `operative_comparator`. Raw: the artifact's `decimal_derivation.source_statistics.range_s`. |
| Budget ceiling (maximum budgetable drift) | `0.010164834757777545` | not a rounded statistic; the same value | Validator row `operatives["maximum_budgetable_drift_s"]`; artifact `decimal_derivation.ratified_operatives.maximum_budgetable_drift_s`. Carried for the record: the check itself compares against the two screens only. |
| Corpus size | `17` | `17` | Validator row `corpus_n`; artifact `derivation_corpus.n`. |

Three facts about those numbers, each of which changes what a comparison
means:

1. **The operative bracket screen is LARGER than the raw range**, by
   `0.009724 − 0.00972358928879385 = 4.1071120615e-7 s` — about 0.41 µs on a
   comparator of 9.7 ms. The artifact registers the quantum `0.000001` s under
   `ROUND_HALF_EVEN`, and the raw range rounds UP to it. Using the operative
   value is therefore marginally the more permissive choice.
2. **The operative level screen is SMALLER than the raw maximum**, by
   `0.03289849371536248 − 0.032898493715362 = 4.8e-16 s`; its registered
   quantum is `0.000000000000001` s and the raw maximum rounds DOWN to it.
   Marginally the stricter choice, at a margin that can only matter to a value
   tying the corpus maximum in its fifteenth decimal place.
3. **No floor is in force here.** The never-zero floor issue 316
   parenthesises — `0.010818` s, `D125_SCREEN_FLOOR_S` — belongs to the screen
   rule `floored_range_envelope_screen`, which the pre-registration registers
   for a FUTURE successor corpus. The acceptance in force registers the other
   rule, `range_equals_screen` — the quantized range IS the screen, with no
   floor (`_D102_N17_DERIVATION["screen_rule"]`, checked in
   `calibration_bracketing._valid_acceptance_bound`). The gap between the
   operative bracket screen and the raw range here is quantization alone.

#### The rule

Issue 316's operative text, quoted:

- "If m < 6 the check is INCONCLUSIVE: run one more equivalence night before
  deciding. No other action."
- "PASS = every retained b_fiducial_s <= the r6 level screen AND the night's
  range (max minus min of the retained values) <= the r6 operative bracket
  screen."
- "FAIL = anything else."

Against the table, the two PASS comparisons are: every retained value
≤ `0.032898493715362` s, and (largest retained value − smallest retained
value) ≤ `0.009724` s. Evaluate the `m < 6` branch FIRST: with fewer than six
retained values the check returns INCONCLUSIVE whatever those values are, and
no PASS or FAIL is recorded. A night retaining exactly one value has range
zero and would be decided on the level screen alone — which is precisely why
the sample-size branch is evaluated before the comparisons, and why it was
fixed before the night ran.

#### The three outcomes, and the exact next action for each

| Outcome | The exact next action, and nothing else |
|---|---|
| **INCONCLUSIVE** (`m < 6`) | Arm ONE more equivalence night: back to §1 with a fresh plan id, fresh `t0`, fresh night root, fresh desk inputs and a fresh session id, then harvest it through this same §2 and apply this same rule to it. No top-up of this night, no partial decision, no other action. |
| **PASS** | Write the dated continuation addendum under D-102 — "epoch continuation on evidence": an identity-field change followed by a same-envelope night CONTINUES the acceptance in force rather than voiding it. The addendum cites this night's session id, the twelve slot outcomes, the count m, and each of the m retained values as the ledger lexeme (issue 316: "the m values"), all verbatim from the desk tool's record, and moves no threshold. If the epoch-freshness refusal in the loader or the issuer blocks continuation, land the SMALLEST change that removes it through the ordinary pull-request gate and report its diff; never work around a refusal by hand. §3 and §4 do not run. |
| **FAIL** | The pre-registered three-night derivation proceeds exactly as revision 1 of the pre-registration writes it, with V3 AFFIRMED by the same issue (three nights, twelve slots, retained n ≥ 19, or exactly 17 under a written ruling). THIS night counts as registration night one, so §3 runs for nights two and three and §4 closes the registration. If the issuer's in-code blindness refusal blocks counting this night, report it and propose the minimal change — never run a fourth night to satisfy the guard. |

**A PASS licenses nothing by itself.** What licenses ordinary capture is the
D-102 continuation addendum, once it lands; until then the acceptance in force
still binds the old identity epoch and ordinary capture still refuses. The
first real G2-a measurement window is the next quiet slot AFTER the addendum
lands, under the ordinary window path and the standing gates — not under this
runbook. The pre-registration stays on file, un-withdrawn, as the fallback
route.

**The desk tool that applies this rule.** `scripts/epoch_equivalence_check.py`
reads the terminal session from the ledger, retains exactly the rows defined
above (it re-reads each retained capture's `instrument_evidence.json` and
refuses if its lexeme differs from the ledger row's), reads the operatives
from the validator registry and refuses if the artifact disagrees, and prints
the constants table, one line per declared slot, m, the two comparisons with
their operands, and the verdict line. It judges only against the r6 generation
named above; pointing it at any other acceptance refuses. It writes one JSON
record to `--out` (never under `configs/calibration/`) and nothing else:

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/epoch_equivalence_check.py \
  --session-id "$SESSION_ID" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --repo-root "$MEASUREMENT_ROOT" \
  --out "$NIGHT_ROOT/epoch-equivalence-record.json"
```

`--acceptance` is left at its default, which resolves against the checkout
the SCRIPT lives in (here the clone, because the `cd` and the relative script
path select the clone's copy; `$PY` only selects the interpreter); the tool
then refuses any generation other than r6 by id, so a second checkout at
the same head running its own copy judges against the same bytes.

Exit code 0 is PASS, 4 is FAIL, 5 is INCONCLUSIVE; 3 means the tool refused
to judge (the session is not terminal, is not derivation-kind, or the envelope
did not authenticate) and wrote nothing. Run it twice — once from the clone,
once from a second checkout at the same head, with a DIFFERENT `--out` for the
second run (for example `"$NIGHT_ROOT/epoch-equivalence-record-2.json"`; the
tool refuses to overwrite the first record without `--force`, and `--force`
would destroy the comparison) — and compare the two records
byte for byte before recording a verdict (the record carries the artifact's
repo-relative path and byte digest, never an absolute path, so two checkouts
at one head produce identical bytes); the record is a witness for the
continuation transaction, never its input.

[OPEN, and not decided by issue 316: if the check is INCONCLUSIVE and the
second equivalence night then FAILS, the issue fixes no answer to whether both
nights count as registration nights one and two or only one of them does.
Report that to Ed and get a written answer; do not choose it at the desk.]

---

## 3. Nights 2 and 3 — the FAIL route only

**This section runs only if §2.5 returned FAIL.** On PASS the derivation does
not happen at all, and on INCONCLUSIVE the next night is a second equivalence
night under §2.5, not night two of a registration. On FAIL the equivalence
night IS registration night one, and two further nights follow.

Identical to §1 and §2, with these differences and no others:

1. **The same registration.** Each night opens its OWN `derivation`-kind
   session with its own `<SESSION_ID>`, and all three session IDs together are
   the registration. Record every session ID in the arm record; §4 passes all
   three to the issuer.
2. **A new plan ID and new coordinates.** Fresh `<PLAN_ID>`, fresh `<t0>`,
   fresh `authored_epoch_s`, fresh night custody root, fresh desk inputs
   written into it (§0.8), and the §1.2 arithmetic recomputed for that night's
   dead-man. Never re-arm a published plan and never silently edit one.
3. **Distinct calendar days.** The registration requires three windows on
   distinct calendar days.
4. **The terminal pin candidate is reviewed and committed at the desk before
   the next night opens.** The night itself never commits Git. Each night opens
   at head-equals-pin, so an uncommitted terminal pin candidate blocks the next
   night's session open. The pre-registration's `[SEQ]`/`[DIGEST]` fields stay
   as the FIRST night's pin; they are the registration's baseline, not a
   per-night field.
5. **A `check` dry run precedes EVERY arm**, not just the first (§0.3 plus
   §2.2). This is the T38j lesson stated as a rule: the OS-build mismatch that
   voided the previous acceptance was found only because a dry run was run.
   Never skip it because last night's passed.
6. **Every arm goes through email-then-arm** (§1.4), every time. Ed's NO on any
   night's notice stands that night down.

Why three nights, stated before capture (pre-registration §"Why three nights of
twelve slots"): at the historical valid rate 30/38 and r6's replay-retention
ratio 17/19, two nights of 12 slots project
`24 × (30/38) × (17/19) = 16.95` retained observations — below the required 19.
Three nights project `36 × (30/38) × (17/19) = 25.4`. The margin is deliberate,
not generous.

---

## 4. After night 3 is terminal — the FAIL route only

**This section runs only if §2.5 returned FAIL** and §3's two further nights
have been captured. A PASS ends the lane at the D-102 continuation addendum;
nothing below is reached.

### 4.1 Confirm admissibility, still blind

`<S1>`, `<S2>` and `<S3>` below are the three nights' `SESSION_ID` values —
one per night, each recovered from that night's wrapper by §2.0 and
cross-checked against its arm record.

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --session-ids "<S1>" --session-ids "<S2>" --session-ids "<S3>"
echo "rc=$?"
```

Expect **rc 0** and `registration admissible for prepare-candidate: yes`. An
rc 5 prints its blockers: a non-terminal session, or pending/unresolved rows in
the prior-set prefix. Clear the named blocker at the desk — do not capture more
to make it go away.

Carry `--preregistration` here too, and read its appended line (§0.3): it must
still say `match` on the sampler digest. The dry run's return code is what the
command returns when sessions are named, so the sampler comparison is again
reported only in the printed line, never in the code.

### 4.2 Prepare the candidate

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py prepare-candidate \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "<the digest pinned at night 1's arm, §0.5>" \
  --registration-session-id "<S1>" \
  --registration-session-id "<S2>" \
  --registration-session-id "<S3>" \
  --d125-ruling "<the ruling reference that fixes the D-125 envelope rule>" \
  --out /Users/edr/night-custody/<PLAN_ID>/candidate_acceptance_25g83.json
echo "rc=$?"
```

That is the exact flag set for an ordinary campaign: nothing else is required,
and every remaining flag is an escape or an override discussed below.

**The four fences this command applies, and what each one refuses.** Each was a
promise the pre-registration made that no code read until the arm gate closed
it; they are the reason the flag set is what it is.

1. **The document itself.** `--preregistration-sha256` is argparse-required.
   The tool hashes the file it was handed and refuses `pre-registration sha256
   <observed> does not match the pinned <given>; not issued` on any difference,
   so a candidate can only ever attest to the text the campaign was armed under.
2. **The night count.** Exactly three `--registration-session-id` values
   (`PREREGISTERED_NIGHT_COUNT`), or the run refuses `registration names <n>
   sessions, not the pre-registered 3`.
3. **The slots per night.** Every named session must have DECLARED twelve
   slots (`PREREGISTERED_SLOTS_PER_NIGHT`) — declared, not filled, so a night
   that lost slots to the window still passes — or the run refuses `session
   <id> declared <n> slots, not the pre-registered 12`. Twelve declared × three
   nights is the n ≤ 36 ceiling the registration's admissible
   degrees-of-freedom range is derived from, which is why a differently-shaped
   corpus is a different experiment whatever its statistics say.
4. **The machine.** The `os_build` carried by the registration's rows must equal
   the one parsed out of the pre-registration text, and every member row's T1
   `powermetrics_sha256` must equal the sampler digest that text names
   (`preregistration_epoch_pins`); otherwise `the registration is void`. This is
   where the registration's "a change to either voids this registration" stops
   being decorative.

**The two written-ruling escapes.** A *written-ruling escape* is a flag that
permits departure from one pre-registered number, and only by naming the
written ruling that authorised it — the departure is then recorded in the
artifact rather than being invisible. Fences 2 and 3 have one each:
`--nights-ruling` for a session count other than three, `--slot-count-ruling`
for a session that declared other than twelve slots. Both take a reference to
Ed's or a cold gate's written ruling. **When they apply: only after that ruling
exists, and never to make a shortfall issue.** A campaign that came up short
does not acquire a fourth night and then name a ruling for it; the shortfall is
resolved in the open, under §2.4's no-top-up rule and this section's corpus
floor. The generator has the matching pair at the other end of the campaign
(`--allow-slot-count` with `--slot-count-ruling`, §1.1b), and the corpus floor
has its own (`--minimum-corpus-size 17` with `--ed-ruling`).

`--out` is **required and has no default**, deliberately: writing into
`configs/calibration/` is the D-138 transaction's act, never this tool's, so
the destination must be named and must be outside `configs/`. `--d125-ruling`
is deliberately NOT `required=True` in argparse, so that its absence produces
the ruled refusal with its reason rather than a usage error.
`--predecessor-acceptance` defaults to the ACTIVE issued acceptance and should
be left alone; it is the artifact the ceiling and the level screen are read
from (below).

The command writes exactly one file, marked `candidate_not_issued: true`,
which the production acceptance loader refuses to load. It licenses nothing.
It derives three OPERATIVES from the corpus: the **bracket screen S**, the
**budget ceiling C**, and the **level screen**. Under the D-125 envelope,
`S = max(new range quantized to 1e-6 s ROUND_HALF_EVEN, 0.010818)` and
`C = max(predecessor ceiling, new Q99)`, where Q99 is the two-draw prediction
at p = 0.995. Issuance refuses `successor_screen_exceeds_budget_ceiling` when
`S >= C`, and that refusal is never cured by lowering S.

Corpus size: `--minimum-corpus-size` defaults to 19
(`SUCCESSOR_MINIMUM_CORPUS_SIZE`); the only other permitted value is 17, and
only with `--ed-ruling` naming Ed's written ruling
(`RULED_ALTERNATIVE_CORPUS_SIZE`, imported from the validator so the floor has
one home). Nothing issues below 19 without it.

**Screen challenge.** If two or more retained members
(`SCREEN_CHALLENGE_MEMBER_LIMIT`) exceed r6's preflight level screen
`0.032898493715362`, the corpus is **not issued** and Ed rules in writing before
any further capture. That threshold is no longer a literal in the issuer: it is
read at run time from the authenticated predecessor acceptance, at
`decimal_derivation.ratified_operatives.preflight_level_screen_s` — the artifact
is the number's one home, so the issuer cannot drift from the generation it is
judging against.

A second diagnostic is recorded but edits no membership: whether the new maximum
exceeds r6's maximum plus r6's range, `0.04262208300415633` (the Decimal sum of
`0.03289849371536248` and `0.00972358928879385`). That one IS a ruled literal in
the issuer, because a ruling fixed its last digits — and it is checked at run
time against the predecessor's own `source_statistics`, refusing `predecessor
maximum plus range <x> does not equal the ruled diagnostic <y>` if the literal
ever stops describing the artifact it was derived from.

### 4.3 The cold science gate packet

The candidate goes to a **cold science gate** — a fresh adjudicating seat with
no campaign context, ruling on a mechanically assembled packet — because no one
who sat on the capture may sit on the exclusions. Assemble the packet from
primary artifacts only:

1. The committed pre-registration at its committed SHA, and the arm records for
   all three nights (including each night's desk-input paste lines, §0.8).
2. The candidate file written in §4.2, whole.
3. The three sessions' dry-run outputs and the chain logs, including every
   `slot_unused`/abort line.
4. The excluded-member list with, per member, its named mechanism, `member_id`,
   `manifest_sha256` and `instrument_evidence_sha256` — and the assertion, to be
   checked, that `affine_clock_fit_empty` is the ONLY registered exclusion
   mechanism, so that an unresolved anchor carrying any other reason must have
   refused issuance rather than quietly excluding a member.
5. The `quantile_proof` block: for each of p = 0.975 and p = 0.995, the
   quantile to 20 decimal places, the forward residual (bound: ≤ 1e-30), the
   agreement digit count between the two independent routes (bound: ≥ 30
   significant digits), both bounds, the closed-form method string, and the
   working precision. Those two bounds are the issuer's DECLARED bounds, not
   ratified constants.
6. The two screen-challenge diagnostics of §4.2 and the S-vs-C comparison.
7. The per-night distribution, order, exclusions and clock-residual margins —
   reported as diagnostics that authorize no trimming.
8. The pre-registration's own **known conditions** — recorded facts about the
   corpus that are not rules and edit no membership. One matters to a reader of
   the resulting acceptance: the night gate does not constrain the display's
   state at `t0` (it requires the screensaver's `idleTime` to read exactly `0`
   and merely records `pmset -g`'s `displaysleep` value), and the derivation
   chain omits the `--sleep-display-before-capture` flag the G2-a chain passes,
   because no operator is present to schedule a display action. These captures
   may therefore differ systematically in display state from the G2-a corpus
   the resulting acceptance will judge. It travels with the packet so the gate
   rules with it in view; it licenses no re-capture and moves no threshold.

### 4.4 The D-138 transaction — named, and out of scope here

Issuing the successor is the **D-138 atomic transaction**: the single reviewed
commit that swaps the live acceptance and every pin that names it. It is out of
scope for this runbook, has its own gate, and must not be started from the same
turn that prepared the candidate.

---

## 5. Failure table

The five groups below are in the order the night can reach them: the desk
writer refuses while writing the inputs (§0.8, its own table), the generator
refuses at the desk, the wrapper refuses at launch, the chain exits during the
night, and the capture writer and the issuer refuse inside a capture or at the desk after.

Generation-time refusals (`scripts/gen_derivation_night.py`, §1.1b step 3).
Every one prints `FAIL <reason>` on stderr and **exits 2**, and **nothing is
written** — no wrapper, no sidecar, no advisory sidecar. All of them are desk
failures with no window cost:

| Refusal (abridged text) | Meaning | Operator action |
|---|---|---|
| `emit mode requires --<flag> …` | One of the six required emit flags was omitted. | Supply it; see §1.1b step 3 for the full six. |
| `night plan is unreadable` / `night plan is not an exact v2 plan: …` | The plan file will not read, or its key set is not exactly the v2 key set. | Re-author the plan against the §1.1 table. The generator validates through the driver's own parser, so this is the same refusal the night would give. |
| `a derivation night is DIAGNOSTIC_NO_PACK; this plan is <class>` | The plan's `receipt_class` is something else. | A `TRANSACTION_PACK` plan launches a pack launcher instead of the plan's chain, and a `REHEARSAL_STUB` never runs its chain at all, so the wrapper would never execute. Fix the class or stop. |
| `window_max_s <n> < required 7680 + 300 = 7980 s …` | The window cannot hold the programmed span plus the pre-settle allowance (§1.2). | Lengthen the window or move `t0` earlier. Never shorten the settle, cadence, slot count or capture budget. |
| `plan overruns the dead-man: t0 + window_max_s + 300 = <n> is not before the next local 07:00 = <n>; move t0 earlier` | The §1.2 dead-man arithmetic fails. | Move `t0` earlier. Never raise `window_max_s` past the strict maximum and never move the dead-man. |
| `--out <path> is not the plan's chain_path '<path>'` | An output path other than the plan's `chain_path` was requested. | Do not pass `--out`. The refusal exists so the plan and the artifact cannot disagree. |
| `plan chain_sha256_path '<path>' is not '<chain_path>.sha256'` | The plan's sidecar path is not the wrapper's path plus `.sha256`. | Fix the plan; this is stricter than the driver, and it refuses rather than mis-writing. |
| `slot count <n> is not the pre-registered 12; pass --allow-slot-count with --slot-count-ruling <ref> to override` | A slot count other than twelve without the two-flag override. | Use twelve. A departure needs a named written ruling and is announced on stderr and in the wrapper's own header. |
| `--allow-slot-count requires --slot-count-ruling <ref>` / `slot-count ruling reference must be one line of [A-Za-z0-9._:/#@ -]` | The override was requested without an authority, or with one that is not a single line of ordinary reference characters. | Name the ruling in one plain line. The reference is interpolated into the wrapper's header, so a multi-line paste could open a comment and start a live line. |
| `<field> contains the census substring 'codex' \| 'claude' \| 't3': …` | Some emitted literal — a plan ID, session ID, window ID, evidence root ID, frozen plan ID, or any absolute path — contains one of the three substrings the night's own agent census matches (`AGENT_CENSUS_ARGV` in `joulewise/night_gate.py`). | Rename it. The census runs every 30 s against the process table and would match the wrapper's own command line and kill the night. |
| `<field> must be an absolute path: …` | A path literal is relative. | Use absolute paths everywhere; the wrapper runs with no useful working directory. |
| `frozen calibration plan is unreadable or carries no plan_id` / `a pinned input is unreadable: …` | The frozen calibration plan, the identity-epoch JSON, the T1-bindings JSON, or the tracked chain inside the clone could not be read. | Re-check §0.8 and the night root's contents — including that the two desk inputs carry the hyphenated names the desk-inputs writer gave them. The chain is read from the CLONE, so this also catches a mis-cut clone. |
| `identity epoch json keys are not exactly the six IDENTITY_EPOCH_FIELDS …` / `… fields are empty or not scalar …` / `identity epoch power_policy is '<x>' …` | The identity-epoch file cannot do its job (§1.1b step 3). | Re-run the §0.8 writer with `$PY` and `--force`; a hand-edited file is the usual cause. Then re-emit. |
| `slot count <n> exceeds the ledger's MAX_DECLARED_SESSION_SLOTS (99); the reservation would refuse it after the settle` | A slot count above the ledger's own ceiling. | Use twelve. |
| `--verify`: `FAIL wrapper bytes differ from re-derivation: …` (**rc 3**, not 2) | The installed wrapper or its sidecar is not what these inputs render (§1.1b step 4). | An input drifted. Find which — chain, frozen plan, identity epoch, T1 bindings, or the plan's coordinates. Do not re-emit over the difference. |

Launch-time refusals (the emitted wrapper, §1.1a). Every one prints
`FAIL <reason>` on stderr and **exits 1** before the session is opened, so no
window time and no ledger state is spent. On an agent-free night the only
record is `<NIGHT_ROOT>/night/chain.stderr.log` — read it first:

| `FAIL <reason>` | Meaning | Operator action |
|---|---|---|
| `measurement_root is required` / `must be an absolute path` / `contains control characters` / `measurement_head must be a full 40-character lowercase SHA-1` | The driver's four-variable environment was malformed. | Should be impossible from a valid plan; treat as a driver or plan defect and escalate before re-arming. |
| `night plan id does not match the wrapper` | `NIGHT_PLAN_ID` is not the plan this wrapper was frozen against. | The wrong wrapper was pinned, or a wrapper was reused across nights. Re-emit per night (§1.1b). |
| `measurement_root does not match the wrapper` / `measurement_head does not match the wrapper` | The plan's clone path or head is not the one baked in at arm time. | The plan was edited after emission, or the wrong clone was named. Re-cut, re-author, re-emit. |
| `checkout HEAD cannot be read` / `checkout HEAD does not equal measurement_head` | The clone is gone, is not a repository, or moved off H. | Stand down. Re-cut the clone at H (§0.2) and re-verify §0.8. |
| `measurement venv Python is missing or not executable` | `<CLONE>/.venv/bin/python` is absent. | The clone was renamed or its venv never built; renaming moves editable-install absolute paths (§0.2). |
| `frozen calibration plan is missing` / `identity epoch json is missing` / `t1 bindings json is missing` | A desk-produced input is not in the night root under the exact path the wrapper pinned. | Produce it before arming (§0.8). An underscore-spelled `identity_epoch.json` is a different file and reads as missing. |
| `frozen plan is not valid JSON` / `frozen plan has no plan_id` | The frozen calibration plan is corrupt. | Re-freeze at the desk; do not hand-edit. |
| `frozen plan id does not equal the arm-time literal` / `frozen plan bytes do not equal the arm-time digest` | The plan file in the night root is not the one the wrapper was generated from — a swapped or re-written file. | Stop and account for the change. Then re-emit and re-`--verify`; never edit the wrapper. |
| `identity epoch bytes do not equal the arm-time digest` / `t1 bindings bytes do not equal the arm-time digest` | One of the two files whose CONTENTS are copied into every slot record changed after emission — a `--force` re-run of the §0.8 writer is the ordinary cause. | Account for it, re-derive both (§0.8), re-emit, re-`--verify`. |
| `tracked derivation chain bytes do not match the arm-time digest` | The capturing chain inside the clone is not the reviewed bytes — an uncommitted edit, or a clone at the wrong head. | Stand down the night. This is the tripwire §0.8's clean-tree check exists to keep from ever firing at 03:00. |
| exit 1 with **no** `FAIL` line, on a `:?required` guard | The tracked chain ran without the wrapper's environment — i.e. the plan pinned the tracked chain directly instead of the emitted wrapper. | Re-author the plan per §1.1: `chain_path` is `<NIGHT_ROOT>/chain.zsh`. No window time was spent. |

Chain exits (`scripts/night_chains/calibration_derivation_only.zsh`):

| Signal | Meaning | Operator action |
|---|---|---|
| exit 64 | A knob (`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WINDOW_END_EPOCH_S`) was not a non-negative integer string, or failed the positivity check — which covers `SLOT_CAPTURE_BUDGET_S` as well as `SLOT_COUNT`, `SLOT_CADENCE_S` and `SETTLE_S`. Refused before the settle, the reservation and any operator-log write. | The environment or plan is malformed. No window time was spent and no partial night exists. Fix at the desk; author a fresh plan for a later night. **Why the budget is in the positivity guard:** at `SLOT_CAPTURE_BUDGET_S=0` the window test `slot_start + budget > WINDOW_END_EPOCH_S` becomes vacuous, so a slot could start one second before the agent-free window ends and capture straight past it. |
| exit 66 `derivation_chain_input_missing: <path>` | One of `PLAN`, `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` was absent. | The clone is incomplete or a path in the plan is wrong. Re-verify §0.2 and §0.4 before authoring the next night. |
| exit 1 | **Ambiguous — read `chain.stderr.log` to disambiguate.** With a `FAIL <reason>` line it is a wrapper refusal (table above). Without one it is the tracked chain's own `:?required` guard, meaning the chain ran without the wrapper's environment. | Both are pre-window failures costing no window time. Resolve per the matching row above before re-arming. |
| `readiness --phase pre-reserve` non-zero | The ledger was not ready; nothing was written and no window time was spent. It never authorizes ARM even when it passes. | Desk-repair the ledger; do not re-arm the same night on the same signature. |
| `slot_end slot=dNN disposition=non-valid`, night continues | **Not a failure.** The writer exited 1: the row is finalized with a disposition other than `valid`, and the next declared slot runs on the unchanged cadence (§2.4). | Record the count of such slots. Do nothing else, and read no value. Exclusion is decided at issuance, by named mechanism. |
| `slot_refused slot=dNN rc=2` + chain exits 2, session left OPEN | The writer REFUSED this capture (`emit_refusal` exits 2). The row is **not** finalized, so the chain stops rather than continuing over an unrecorded slot — and deliberately does not abort the session. | Read the refusal in `chain.stderr.log`, then **desk recovery**: `recover_calibration_ledger.py … abort-session --session-id <id> --plan <plan> --reason <the named reason>` (§2.4). Never a retry inside the window. Until the session is closed the next night cannot open at head-equals-pin. |
| `slot_refused slot=dNN rc=<n≥3>` + chain exits with that status, session left OPEN | The writer crashed rather than refusing. Same dispatch branch, same unfinalized row. | Same desk recovery, and account for the crash before any further night is armed: a crash is a defect, not an outcome. |
| `slot_unused … reason=window_exhausted` + `session_abort` + exit 0 | The window could not finish a slot's 480 s budget. Slots are recorded unused, never compressed or retried. Δ larger than 1320 s is the usual cause (§1.2). | Record the count. The session is terminal and §2.5 judges its finalized rows (an equivalence night with fewer than six retained values is INCONCLUSIVE). No top-up, no fourth night (§2.4). |
| Any other non-zero exit, with a `session_open` line already in the chain log | A ledger call failed under `set -e` after the session was opened. | Treat exactly as `slot_refused`: read the log, then desk recovery with a named reason. A `session_open` line with no `session_abort` and no terminal slot means the session is still open, whatever the exit code was. |

Capture-writer refusals (`scripts/validate_powermetrics_fiducial.py`, codes in
`joulewise/calibration_exits.py` as `RefusalCode.DERIVATION_*`):

| Refusal code | Meaning | Operator action |
|---|---|---|
| `calibration_derivation_only_epoch_unchanged` | `--derivation-only` was used while the live identity epoch still matches the active acceptance's. Derivation-only exists only when no acceptance binds the current epoch. | **Stop.** Either the OS reverted or the wrong acceptance was read. Re-run §0.3; do not force the flag. This is the same condition §0.8's desk-inputs writer refuses on at the desk. |
| `calibration_derivation_only_session_kind_required` | `--derivation-only` without a declared `derivation`-kind session slot. | The reservation did not open a derivation session, or the slot name is not in its declared list. Fix the reservation; never capture outside the registration. |
| `calibration_derivation_session_requires_derivation_only` | A `derivation`-kind session slot was captured WITHOUT `--derivation-only` — the mid-night flag-loss case the guard exists for. | The chain's writer invocation lost the flag. Stop the night's remaining slots at the desk; the session is recoverable, the mixed evidence is not. |
| `writer_bracket_arguments` | `--session-id`, `--slot` and `--attempt-id` are all-or-none; a partial triple refuses. | Fix the invocation; three values or none. |
| `quiet_mac_auth_required` / `power_policy_required` | `--allow-live` absent, or `--power-policy` not given. | The chain passes `--allow-live` and `ac_high_power`; a refusal here means the invocation was not the chain's. |

Issuer return codes (`scripts/issue_calibration_acceptance_generation.py`):

| Command | rc | Meaning | Operator action |
|---|---|---|---|
| `check` (no `--session-ids`) | 3 | Identity mismatch and/or an acceptance/ledger error. | **Expected throughout this lane** (§0.3). Read the table; confirm the mismatched fields are `os_build` and `powermetrics_sha256` and no others. |
| `check` (no `--session-ids`) | 0 | No mismatch, no error. | **Unexpected — stop.** The machine now matches the old epoch; the lane's premise is gone. Escalate before capturing. |
| `check --session-ids …` | 0 | Registration would be admissible. | Proceed to §4.2 — on the FAIL route, and expected only after night 3 is terminal. |
| `check --session-ids …` | 5 | Inadmissible; each blocker is printed. | Expected after nights 1 and 2. Clear the named blocker at the desk; never capture more to clear it. |
| `prepare-candidate` | 3 | `REFUSED: <reason>` and nothing written — a non-terminal session, absent `--d125-ruling`, corpus below the minimum, a pending/unresolved prior-set row, a valid same-epoch observation outside the registration, a member whose stored bytes disagree with its ledger row, a failed quantile proof, `S >= C`, or two or more retained members over the level screen. | Read the reason literally. Several of these are science stops requiring Ed's written ruling (§4.2), not defects to fix. |
| `prepare-candidate` | 3 | The arm-gate fences of §4.2, same `REFUSED:` shape: `pre-registration sha256 … does not match the pinned …; not issued`; `registration names <n> sessions, not the pre-registered 3`; `session <id> declared <n> slots, not the pre-registered 12`; `registration os_build … is not the pre-registered …; the registration is void`; `registration powermetrics sha256 … is not the pre-registered …; the registration is void`; `predecessor maximum plus range … does not equal the ruled diagnostic …`. | None of these is fixed by re-running with different flags. The first three are answered by naming the correct file and sessions, or by a written-ruling escape that already exists (§4.2) — never by inventing one. The two `void` refusals mean the campaign was captured on a machine the registration does not describe: stop, and take it to Ed in writing. |
| `prepare-candidate` | 0 | One candidate file written, `candidate_not_issued: true`. | It licenses nothing. Go to §4.3. |

Night-gate refusals to expect in `result.json`/`refusal.json` (names from
`NIGHT_GATE_REASON_CODES` and `NIGHT_DRIVER_REASON_CODES` in
`joulewise/night_gate.py`): `night_plan_malformed`,
`night_plan_overruns_deadman` (the §1.2 arithmetic was wrong),
`night_refused_agent_present` (§0.6 was violated), `night_refused_boot_clock`,
`night_refused_registration` (the `registration_path` did not authenticate).
`[UNVERIFIED: the full refusal list and each one's exact operator remedy; this
seat read the names and the two lines around them, not each refusal's
implementation.]`

---

## 6. What this runbook does NOT authorize

1. **No G2-a measurement window.** Nothing here licenses one. A G2-a window
   becomes possible only after the D-138 transaction issues the successor
   acceptance — that is the frozen constraint this lane exists to satisfy.
2. **No issuance.** `prepare-candidate` writes a candidate the production
   loader refuses. Issuing is D-138's single reviewed commit (§4.4).
3. **No writing into `configs/calibration/`.** Not by this runbook, not by the
   issuer, not by the desk-inputs writer, not "just to stage it".
4. **No look at any value while a night is running, and on the FAIL route no
   corpus statistic before night 3 is terminal** (§2.3). The equivalence
   night's retained values are read once its own session is terminal, and only
   to apply §2.5's fixed rule.
5. **No extra, replacement, top-up or retry night**, no early stop, and no
   outcome-driven schedule change (§2.4). The one further night this lane can
   require is §2.5's `m < 6` branch, which is fixed by rule BEFORE capture and
   is therefore not outcome-driven in the sense forbidden here.
6. **No amendment of the pre-registration** to accommodate what the data did.
   Its rules were fixed before capture precisely so they could not be.
7. **No arm that skips the email-then-arm handback, the standing gates, or the
   pre-arm `check` dry run.** V3's affirmative acknowledgment is no longer a
   precondition of THIS night: directive issue 316 answered V3 NO as the
   default path and authorized the equivalence night in its place. V3 becomes
   binding again only on the FAIL route, where the same issue affirms it.
8. **No agent present during any night this runbook operates**, and no use of
   the chain, driver or a live capture as a quietness test from a live
   session.
9. **No claim, floor, or paper number** may consume a derivation observation:
   derivation observations are corpus members and never bracket endpoints,
   before or after issuance, and no G2-a, floor or claim output is an input to
   this derivation.
10. **This runbook authorises nothing on its own.** The lane's code is merged
    and its whole-suite replay is green, but arming a night still takes a
    magistrate ruling that adopts this text, plus §1.4's email-then-arm — and
    Ed's NO overrides.
11. **No departure from twelve declared slots a night, and no night count
    chosen at the desk.** The twelve-slot shape is unchanged, and how many
    nights follow this one is decided by §2.5's rule, which was fixed before
    the night ran — never by what the night produced. Both tools still refuse
    a departure that is not accompanied by the written ruling they each
    require: the generator's `--allow-slot-count` with `--slot-count-ruling`
    at the arm (§1.1b), the issuer's `--nights-ruling` and
    `--slot-count-ruling` at issuance (§4.2). This runbook does not supply,
    imply or stand in for such a ruling; the flags exist so that a ruled
    departure is RECORDED in the artifact.
12. **No licence from a PASS.** A PASS authorizes exactly one thing: writing
    the D-102 continuation addendum. Ordinary capture, the first real G2-a
    window, and every claim-bearing use of the acceptance wait until that
    addendum has landed (§2.5).

---

## 7. Fact table — where each load-bearing fact came from

Every source is in the merged tree at `main`, read read-only with
`git show HEAD:<path>` unless another location is named. Citations are by
SYMBOL — a named constant, function, class, test name or document section — and
by trace record number (§0.1), never by line number: the lane's own finding S-2
was that line citations went stale within the session that wrote them, and the
generator's tests now resolve anchor TEXTS for the same reason. A **seat** named
below is one delegated worker session of this lane; what it produced is its
numbered record.

| Fact | Source |
|---|---|
| Chain order, `SLOT_COUNT=12`, `SETTLE_S=600`, `SLOT_CADENCE_S=600`, `SLOT_CAPTURE_BUDGET_S=480`, exits 64/66, `window_exhausted` abort, the thirteen required variables | `scripts/night_chains/calibration_derivation_only.zsh`: its knob defaults, its `:?required` guards, and its slot loop |
| The three-way writer-status dispatch (0 → `disposition=valid` continue; 1 → row finalized `disposition=non-valid`, continue; ≥ 2 → `slot_refused slot=dNN rc=<n>`, exit with the session OPEN and no abort), the capture writer run as an `if` condition so `set -e` cannot pre-empt it, and the positivity guard covering `SLOT_CAPTURE_BUDGET_S` | same file: the slot loop's `if (( writer_rc == 0 )); then` branch and the pre-settle guards |
| `chain_start` logged AFTER the reservation and immediately before the settle — the fact that makes Δ measurable at harvest | same file |
| Chain environment fixture (the exact thirteen required variables) | the chain-environment test in `tests/test_issue_calibration_acceptance_generation.py` |
| Writer flags `--allow-live --derivation-only --session-id --slot --attempt-id --power-policy`; all-or-none bracket triple | `scripts/validate_powermetrics_fiducial.py`, its argument parser and bracket-triple validation |
| The three derivation refusal codes | `joulewise/calibration_exits.py`, `RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED`, `DERIVATION_ONLY_SESSION_KIND_REQUIRED`, `DERIVATION_SESSION_REQUIRES_DERIVATION_ONLY`, raised in `scripts/validate_powermetrics_fiducial.py` |
| `check` semantics, rc 3, the watched fields, the dry-run fields, `DRY_RUN_INADMISSIBLE_EXIT = 5` | `scripts/issue_calibration_acceptance_generation.py`: `WATCH_FIELDS`, `observe_machine`, `mismatched_fields`, `registration_dry_run`, `check` |
| `prepare-candidate` flags, `--out` required and defaultless, `--d125-ruling` not argparse-required, rc 3 on refusal | same file, the `prepare-candidate` body and parser |
| `SUCCESSOR_MINIMUM_CORPUS_SIZE = 19`, `RULED_ALTERNATIVE_CORPUS_SIZE` imported from the validator (one home), `SCREEN_CHALLENGE_MEMBER_LIMIT = 2` | same file, those constants |
| `check --preregistration` (optional; parses the registered `powermetrics` digest, APPENDS one comparison line, adds an error rather than changing rc); `prepare-candidate --preregistration-sha256` required, `PREREGISTERED_NIGHT_COUNT = 3` and `PREREGISTERED_SLOTS_PER_NIGHT = 12` with `--nights-ruling` / `--slot-count-ruling` escapes; the `os_build` and sampler-digest void refusals; the level screen read from the authenticated predecessor's `ratified_operatives.preflight_level_screen_s`; the ruled maximum-plus-range diagnostic re-checked against the predecessor's `source_statistics` | same file: `preregistration_epoch_pins`, the authenticated-predecessor helper, and the `prepare-candidate` body and parser. These are the three arm-gate blockers record 109 recorded as unenforced, now enforced |
| Three nights × 12 slots, retained n ≥ 19, the 16.95/25.4 projections, the 128 min schedule, blindness, the screen challenge, the D-125 envelope, the halt on `S >= C`, `0.04262208300415633`, `0.010818`, the predecessor ceiling `0.010164834757777545` | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` |
| The three durations reconciled — programmed span 7680 s (128 min), generator minimum 7980 s (133 min), armed `window_max_s` 9000 s (150 min) — and the note that 210 min is the install span, not a window | same file, §"Why three nights of twelve slots" |
| Display state at `t0` is unconstrained by the night gate, recorded as a known condition and not a rule | same file, §"Known conditions (recorded, not rules)" |
| Fences `[02:45,03:30)` / `[07:00,07:01)`, plan span from `t0 − 25 min`, the stand-down ladder −25/−16/−15, the 15-minute watchdog liveness, email-then-arm with Ed's NO overriding, the `measurement_root`/`measurement_head` install rule | `docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines" (the intervals and the boundary table) and §"Install handoff" |
| The handback's role, the courier's reading order, the campaign/chain process checks | `docs/process/NIGHT_HANDBACK.md`, its opening sections |
| v2 plan required keys, `night_plan_overruns_deadman`, `registration_path`, the 36-hour authoring age | `joulewise/night_gate.py`: `_PLAN_KEYS`, `NightPlan.from_mapping`, `NIGHT_GATE_REASON_CODES`, `NIGHT_DRIVER_REASON_CODES`, `PLAN_MAX_AGE_S` |
| Generation-time parsing of the two JSON inputs (six exact `IDENTITY_EPOCH_FIELDS`, scalar non-empty values, `power_policy == ac_high_power`; T1 bindings parsed as an object only), `MAX_DECLARED_SESSION_SLOTS = 99` as a desk-time ceiling, and the `CHAIN_ANCHORS` anchor-text discipline | `scripts/gen_derivation_night.py`: `_validated_identity_epoch`, `_validated_json_object`, `CHAIN_POWER_POLICY`, `CHAIN_ANCHORS`, and the slot-count and window checks in `build_spec`; `MAX_DECLARED_SESSION_SLOTS` from `joulewise/calibration_ledger.py` |
| The wrapper mechanism, the thirteen + six exports, the three emitted files, the five-step arm order, the six required emit flags and their defaults, `--verify` rc 0 / rc 3, every generation-time refusal text, the 300 s pre-settle allowance, the 7680 s programmed span for twelve slots, the census substrings | `scripts/gen_derivation_night.py` (module docstring and the symbols `programmed_span_s`, `_census_clean`, `_validated_ruling`, `_next_deadman_epoch`, `build_spec`, `render_wrapper`, `emit`, `verify`, `build_parser`, `main`) and the `derivation-night-wrapper` generated region of `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` |
| The desk-inputs writer: its flags and defaults, its paste-line output format, every refusal in §0.8's table, the canonical hyphenated filenames, and the rule that it must run under the project venv interpreter | `scripts/write_derivation_night_inputs.py` (module docstring, `_derive_planned_vectors`, `_refuse_incomplete_vector`, `_stale_identity_fields`, `_resolved_out_dir`, `_refuse_overwrite`, `write_night_inputs`, `_build_parser`, `main`), whose names `IDENTITY_EPOCH_NAME` and `T1_BINDINGS_NAME` come from `scripts/generate_g2a_probe_inputs.py`; seat record 135, including its live desk smoke and its MLX finding |
| Why the G2-a producer cannot serve a derivation night (it authenticates the acceptance epoch that is stale), and that the desk-inputs writer is the answer | record 134 |
| The live `check` output in §0.3 — two mismatched fields, `mlx_version 0.31.2` matching, rc 3, and the appended `match` line on the pre-registered sampler digest | record 134, run from a fresh clone at the desk |
| Δ ≤ 1320 s for `d12` to be admitted at `window_max_s = 9000`; the three components of Δ | the chain's admission test read against the wrapper's pinned knobs; corroborated by the execution refuter's independent derivation (record 104 §7, "the night tolerates up to 1320 s of launch delay") and named as a runbook defect by the seam finding N-3 |
| The install commands of §1.4 — `scripts/install_night_agent.sh --plan --hour --minute --python "$PY"` installing BOTH labels in one call and `--uninstall` removing them, the `os.replace` publication with its non-pre-existing target and same-device requirement, the staged-copy `cmp` in recovery, the `launchctl list` and post-install `night/` baseline | record 12, `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`, §"Block A" (exports and staging) and §"Block B" (notice, census, move, install, inspect, rollback); the installer's own `--hour` dead-man refusal is in `scripts/install_night_agent.sh` |
| "Discoverable" = `/Users/edr/night-custody/*/night_plan.json`, one level, that filename — so the staging path arms nothing, and the driver discovers nothing because launchd hands it `--plan` | `glob_plans` in `scripts/magistrate_watchdog.py`; the `--plan` `required=True` argument of `scripts/run_night.py` |
| The plan is an INPUT to the generator, and the wrapper's bytes depend on the plan's CONTENT not its path | `scripts/gen_derivation_night.py`: `--plan`'s help text ("frozen v2 night plan JSON (emit mode)"), and `build_spec`, which renders every wrapper literal from the decoded plan fields |
| The wrapper's `WINDOW_CUSTODY_ROOT` is `plan.custody_root`, its `RUNS_ROOT` defaults to `<custody_root>/runs`, its `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` to the clone's ledger and head pin — the derivations §2.0 uses | `scripts/gen_derivation_night.py`: `WrapperSpec`, `build_spec`, and the `--runs-root` / `--ledger` / `--head-pin` defaults in `build_parser` |
| The frozen checkout triple is exactly `(plan_id, root, head)`, rendered by the watchdog into the relaunch prompt, and fences those checkouts against movement | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, the `@@FENCED_CHECKOUTS@@` line and the line after it; `docs/process/MAGISTRATE_WATCHDOG.md`, §"Complete write inventory" |
| A fence forbids LAUNCHING OR ADOPTING a magistrate agent session, not running a night — so a `t0` inside the belt is correct | `docs/process/MAGISTRATE_WATCHDOG.md`, §"Safety model and state machine" (the `FENCED` state) and §"Fence and deadlines"; corroborated by the rehearsal night that fired at 02:56 local and exited 0 (`docs/process/NIGHT_HANDBACK.md`, §"Executed — rehearsal-20260909") |
| The frozen calibration plan is a committed pack-relative `calibration_plan.json`, not a custody reservation plan | `docs/phase_2/window_runbook.md`, the ALPHA `window.env` example and its `FROZEN_PLAN` gloss |
| `[DD]` is the registration's authoring day | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, §"Fields filled at commit" |
| The clone's environment must equal `env/mac-measurement-lock.txt` | record 12, §"Block A", its closing `pip freeze` diff |
| Runbook shape, install span 03:00–06:30, never 07:xx, `t0+window_max_s+300 < 07:00`, the strict-maximum arithmetic, the Block A / Block B / record-and-exit structure | records 11 and 12 of this trace directory — `docs/process_traces/2026-09-10-activation-96bfeca7/11-night-handback-draft-g2a-20260912.md` and `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md` |
| The supersession banner shape and the "read the newest activation records" instruction | record 13 |
| Epoch↔local conversions and the four arithmetic results in §1.2 | computed with `TZ=America/Los_Angeles date -r <epoch>` and shell arithmetic when this runbook was drafted |
| Driver hands the chain four variables and no argv (`_run_chain_once` in `scripts/run_night.py`, pinned by the argv assertion in `tests/test_run_night.py`); the gate binds the clone by `HEAD` only (the clone-head condition in `joulewise/night_gate.py`); the reservation copies the identity-epoch and T1-bindings CONTENTS verbatim into every slot record (`main` in `scripts/reserve_calibration_window_bracket.py`) | scout record 101 §0–§2 and the contract-lens refuter record 105 §2, §5 |
| Clean tree and desk-input provenance as arm-checklist items, and "one wrapper per night" | seat record 103 §7.1–§7.4 and its fix-round items B-1, B-2, S-1, S-4; refuter record 105 §5 |
| Whole-suite replay green at the merged head, and the merge itself | records 130 and 133 |
| The epoch-equivalence rule itself — the `m < 6` INCONCLUSIVE branch, the PASS and FAIL definitions, the continuation route and its addendum contents, the FAIL route's affirmation of V3, and the blindness clarification | The owner's directive issue 316 of 2026-09-10, transcribed as revision 2 of `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` and as the dated Ed addendum under D-102 in `docs/decision_log.md` |
| The reference-envelope constants `0.032898493715362`, `0.009724`, `0.010164834757777545` and n = 17, their raw counterparts `0.03289849371536248` and `0.00972358928879385`, and the fact that this generation's screen rule carries no floor | `joulewise/calibration_bracketing.py`: `_D102_N17_DERIVATION` (its `operatives`, `corpus_n` and `screen_rule`), bound to the acceptance id by `_D102_GENERATION_DERIVATIONS` and checked in `_valid_acceptance_bound`; the same lexemes in `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` under `decimal_derivation.ratified_operatives`, `decimal_derivation.rounding` and `decimal_derivation.source_statistics` |

Still unverified, and flagged in place: the 06:05 last-start cutoff's status
(§1.3) and the complete night-gate refusal list with each refusal's remedy (§5).
**Closed since revision 1:** the driver's supply of the chain environment and of
the per-slot binding argv (§1.1, §1.1a) — there is no such driver code by
design, and the emitted wrapper supplies both. **Closed since revision 3:** the
live `check` strings (§0.3, record 134) and the producer of the two desk inputs
(§0.8, `scripts/write_derivation_night_inputs.py`). **Closed since revision
4:** the plan's two paths and the discoverability window between them (§1.1b
step 2, §0.7), the arm's actual install commands (§1.4), the frozen checkout
triple's exact fields and the harvest's reconstruction from them (§1.5, §2.0),
and the two senses of `fence` (§Terms). The wrapper generator's
tests live in `tests/test_gen_derivation_night.py`, the desk-inputs writer's in
`tests/test_write_derivation_night_inputs.py`, and the chain's own in
`tests/test_issue_calibration_acceptance_generation.py` under no
`test_night_chain_*` name.

---

## 8. First-use table

Every term of art in this file, where it is built, and in one line what it
means. A term is listed only if it does technical work.

| Term | Built at | One-line meaning |
|---|---|---|
| acceptance | §"What night one is for" | The issued artifact whose corpus statistics set the thresholds later captures are judged against. |
| epoch-equivalence check | §"What night one is for", applied §2.5 | One night's retained values compared against the thresholds the acceptance in force already carries, under a rule fixed in writing before the night runs. It derives nothing and issues nothing; it answers whether the OS point release moved the clock-anchor bound outside the existing envelope. |
| reference envelope | §2.5 | The comparators of the acceptance in force, in the OPERATIVE form the validator uses: level screen `0.032898493715362` s, bracket screen `0.009724` s, budget ceiling `0.010164834757777545` s, n = 17. Where an operative constant differs from the raw corpus statistic, the operative one is the comparator. |
| retained value / retained m | §2.5 | The `b_fiducial_s` of a capture that is both `valid` in the ledger and resolved under anchor-v3 replay; `m` is how many such values the night produced. A refused, unreached or invalid capture contributes none. |
| continuation ("epoch continuation on evidence") | §2.5 | Carrying the acceptance in force onto the new identity epoch by a dated D-102 addendum instead of voiding it and deriving a successor. It moves no threshold, and it is what licenses ordinary capture — a PASS by itself licenses nothing. |
| identity epoch / epoch | §"What night one is for" | The six-field vector `{os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}` an acceptance binds. |
| derivation-only capture | §"What night one is for" | A capture taken to BUILD a future acceptance; it licenses no measurement. The equivalence night's twelve captures are of this kind, whichever route follows. |
| slot | §Terms | One declared, ordered place for one capture inside a session (`d01`…`d12`). |
| session (ledger) | §Terms | A ledger capability reserving several attempts under one open receipt at a fixed head pin. Unqualified, *session* always means this; the watchdog's *agent session* is always written out in full. |
| registration | §Terms | The set of ledger sessions the pre-registration declares the corpus is drawn from. |
| stale field | §Terms, used §0.8 | An identity field whose value on this machine differs from the active acceptance's epoch; at least one must be stale for a derivation night to be the right night. |
| head pin / head-equals-pin | §Terms | The committed file naming the trusted receipt count and last digest; equality with the physical ledger head. |
| screen / level screen / bracket screen | §Terms, constants in §2.5, successor operatives in §4.2 | A threshold a value is compared against; corpus maximum; corpus range. |
| ceiling (budget ceiling) | §Terms, §4.2 | The largest drift a generation will ever budget for; the bracket screen must be strictly below it. |
| blind / blindness | §Terms, bounded §2.3 | Every rule that could be chosen after seeing values is fixed in writing BEFORE the data exists — "every rule fixed before data", not "no one may look". Nothing is read while a night runs; the equivalence night's retained values are read once its own session is terminal, and on the FAIL route no corpus statistic is computed before the last registration session is terminal. |
| driver preflight | §Terms, §1.4 | The install-time check of the driver module, its module-scope project imports and the plan under the job's interpreter and PATH; it does not exercise lazy imports inside project functions or the chain's input checks. |
| dead-man | §Terms | The second LaunchAgent that fires at a fixed local minute and stands the night down if completion has passed. |
| fence (watchdog sense) | §Terms | A period in which the watchdog refuses to LAUNCH OR ADOPT a magistrate agent session: a plan span, the half-open belt `[02:45:00, 03:30:00)`, or the half-open dead-man minute `[07:00:00, 07:01:00)`. It forbids an agent starting, never a night running — which is why a `t0` of 02:56 is inside the belt and correct. |
| blindness fence | §Terms, enforced §2.3 item 3 | The code-enforced refusal of `prepare-candidate` while any session named in the registration is not terminal — the FAIL route's fence on computing a corpus statistic early. Not an interval; no clock clears it, and it does not govern the equivalence check, whose rule is fixed before capture instead. |
| handback | §Terms | `docs/process/NIGHT_HANDBACK.md`, rewritten and committed with every armed night. |
| email-then-arm | §Terms, §1.4 | Email Ed the notice, arm without waiting for a reply; Ed's NO overrides. |
| `[QUIET-MAC]` | §0.6 | The agent-free machine discipline a capture night runs under. |
| measurement root / measurement head | §0.2, §1.1 | The fresh clone both night agents are installed from, and the commit it is detached at. |
| `$PY` / project venv interpreter | §0.2 | The Python inside the measurement clone's `.venv` — the only interpreter with this project's dependencies, and the one every desk step here uses. Not `/usr/bin/python3`. |
| T1 bindings | §0.3, §0.8 | The toolchain-identity block a finalization receipt records: the six epoch fields plus the four execution pins (sampler digest, clock-anchor method version, MLX version, frozen protocol digest). |
| desk-inputs writer | §0.8 | `scripts/write_derivation_night_inputs.py`: the tool that reads this machine through the capture writer's own helpers and writes `identity-epoch.json` and `t1-bindings.json` into the night root, refusing rather than writing a vector the night would reject. |
| paste line | §0.8 | One of the two lines the desk-inputs writer prints in `NAME=<path> sha256=<64 hex>` form, shaped as a shell assignment so the path and digest reach the arm record and the generator's flags without retyping. |
| clean tree | §0.8 | The measurement clone has no uncommitted change of any kind: `git status --porcelain` prints zero bytes. |
| `DIAGNOSTIC_NO_PACK` | §1.1 | The receipt class for a night with no measurement pack; only C2 is not-applicable. |
| wrapper | §Terms, built §1.1a | The generated zsh file, one per night, that carries the night's whole environment as literal `export` lines, authenticates its pinned inputs, and then `exec`s the tracked chain. The plan's `chain_path` names it. |
| night root | §Terms, exported §0.2 | `<NIGHT_ROOT>`, the custody directory the plan calls `custody_root`; the three emitted files and the night's two desk inputs live in it. |
| tracked chain | §Terms | `scripts/night_chains/calibration_derivation_only.zsh`, the committed script that runs the twelve captures — identical in every clone at `H`, unlike the per-night wrapper. |
| capture writer | §0.8 | `scripts/validate_powermetrics_fiducial.py`, run twelve times by the chain during the night. Distinguished from the desk-inputs writer everywhere in this file; a bare "writer" survives only inside a tool's own quoted message, where it means this one. |
| `<NIGHT_DATE>` | §0.2 | The eight-digit `YYYYMMDD` of the date `t0` falls on; every dated name in the arm is built from it. |
| staging path / `$STAGED_PLAN` | §0.2, §1.1b step 2 | `/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json`, where the plan is authored, generated from and `--verify`-ed. Outside the watchdog's discovery glob, so authoring a plan arms nothing. |
| published (plan) | §1.4 | The one instant a night becomes discoverable: `os.replace` of the staged bytes into `<NIGHT_ROOT>/night_plan.json`, a target that must not pre-exist. Everything before it is undone by doing nothing. |
| sidecar | §1.1a | A small companion file holding another file's SHA-256 in `shasum` output form — the digest, two spaces, a name. |
| advisory (of the third emitted file) | §1.1a | Written for a human's hand-check only; nothing reads it at launch, so deleting or rewriting it changes nothing about what the night will accept. |
| anchor text | §1.1a | One exact line of the chain, quoted in full as a citation instead of a line number, and resolved against the chain's current bytes by a test. |
| tripwire | §1.1b step 4 | A check that writes nothing and exists only to fail loudly if an input drifted — here, `--verify` re-deriving the wrapper and comparing it byte-for-byte. |
| `zsh -n` | §1.1b step 5 | A syntax check: zsh parses the file and runs none of it. |
| census substring | §1.1b, §5 | The three strings the night's own 30 s process census matches; the generator refuses to bake any of them into an emitted literal. |
| programmed span | §1.2 | Chain start to the end of the last slot's capture budget: settle + (slots − 1) × cadence + one budget = 7680 s for twelve slots. |
| pre-settle allowance | §1.2 | 300 s INSIDE the window and BEFORE the settle — the chain's input preflight, its pre-reserve readiness check and the session reservation, plus the driver's pre-launch work. The generator refuses a window below programmed span + this. |
| start-to-start cadence | §1.2 | Slot `d(k+1)` starts 600 s after `dk` STARTED; a long capture is never caught up by compressing a later slot. |
| window_max_s / `WINDOW_END_EPOCH_S` | §1.2 | The plan's window length in seconds, and the exclusive window end the chain enforces. |
| courier / courier deadline / courier allowance | §1.2, §2.1 | The process that emails the night's result; the 300 s the deadline arithmetic reserves for it AFTER the window ends. Distinct from the pre-settle allowance, which is spent inside the window; the two share a number by coincidence. |
| Δ (delta) | §1.2 | The elapsed time from the plan's `t0` to the moment the chain's settle begins: driver gate work + chain preflight + session reservation. `d12` is admitted only while Δ ≤ 1320 s. |
| plan span / exit boundary | §0.6, §1.3 | The interval from `t0 − 25 min` in which no agent may be resident; the activation's hard exit time. |
| census | §0.6 | The enumerated process inventory proving no foreign or own agent is live. |
| frozen checkout triple | §1.5 | Exactly `(plan_id, root, head)` — the three fields the watchdog renders into the relaunch prompt's `@@FENCED_CHECKOUTS@@` list. It fences those checkouts against movement; §2.0 reconstructs every further harvest coordinate from it. |
| terminal (session) | §2.2 | The session's last declared slot is final, or the session was aborted. |
| dispatch (writer-status) | §2.4 | The chain branching on the capture's EXACT status number rather than on "non-zero": 0 valid and 1 non-valid both finalize the row and continue the night; 2 or more is a refusal or crash that stops it with the session open. |
| desk recovery | §2.4 | Closing an open session with `recover_calibration_ledger.py … abort-session --reason <named>`, run by the operator at the desk after the night is over — never inside the window and never as a re-arm. |
| `window_exhausted` | §2.4 | The abort reason recorded when the window cannot finish a slot's capture budget. |
| prior set / corpus / retained n | §Terms | Every ledger observation through the cutoff; the subset whose values are computed from; the corpus size. |
| written-ruling escape | §4.2 | A flag that permits departure from one pre-registered number, and only by naming the written ruling that authorised it, so the departure is recorded in the artifact: `--nights-ruling`, `--slot-count-ruling`, `--allow-slot-count`, `--ed-ruling`. |
| Q99 / two-draw prediction | §4.2 | `t(0.995, n−1) × sample SD × √2`: how far apart two fresh draws fall at that confidence. |
| screen challenge | §4.2 | The pre-registered halt: two or more retained members over `0.032898493715362` means not issued, Ed rules in writing. |
| candidate / `candidate_not_issued` | §4.2 | The one file `prepare-candidate` writes, which the production loader refuses; it licenses nothing. |
| quantile proof | §4.3 | The recorded evidence that the Student-t quantile for the realized degrees of freedom was computed correctly two independent ways. |
| known condition | §4.3 | A recorded fact about how the corpus was captured that is deliberately not a rule — it edits no membership, moves no threshold, and licenses no re-capture. |
| cold science gate | §4.3 | A fresh adjudicating seat with no campaign context, ruling on a mechanically assembled packet. |
| D-138 transaction | §4.4 | The single reviewed commit that swaps the live acceptance and every pin naming it. |
