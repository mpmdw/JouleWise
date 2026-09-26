# Operating runbook for the agent-free calibration derivation nights, lane ACCEPTANCE-EPOCH-25G83-01

STATUS: **DRAFT runbook, tracked at `docs/phase_2/derivation_night_runbook.md`;
authorises nothing; every arm still goes through NIGHT_HANDBACK
(email-then-arm) and Ed's NO overrides.** The lane's code is merged: every
script, gate and test this runbook operates is on `main` at
`8cbcaf08`. Sections marked `[UNVERIFIED: …]` are facts this runbook could not
establish from a primary source; they are open questions for the operator, not
instructions.

**Revision 9 — 2026-09-15, ARM-RETRY-CLASS-01 (A172 rulings R1–R3).**
§1.4a installs the adjudicated arm-abort procedure and its pure decision helper;
this grants no new experiment authority. The reviewed head used for an arm
must include both A172 and INSTALL-WINDOWS-MULTI-01. No merge or live arm is
claimed here.

**Revision 8 — 2026-09-15, INSTALL-WINDOWS-MULTI-01 (D-180 clause 1,
D-181 clause 1; adopted design record 06).** The live timing procedure below
targets the adjudicated implementation: `scripts/run_night.py` owns install
spans, the derived install close and the per-plan dead-man. The reviewed head
H used for an arm must include that implementation; the earlier merged-head
statement above describes the predecessor code. Sections §Terms, §0.4,
§1.2–§1.5, §2.1, §5, §7 and §8 carry the corresponding in-place updates.

**Historical revision notes follow, verbatim.** Their old clock limits and
open cutoff question describe those revisions; §1.3 is the current procedure.

**Changelog — revision 7 (2026-09-11), one line: the plan now names D-166,
the registration file required by the night gate, while the scientific
pre-registration is bound by the measurement head (the commit the plan pins) and the arm
record's SHA-256 digest (a fingerprint of the file's bytes).** What that forced:
§0.5, §1.1 and §1.4 name the gate's required file and the arm block checks its
path and digest; §1.5 gathers the five required arm-record items, including
the pre-registration's Git blob id (the identifier of its stored file bytes);
§2.5 binds the PASS continuation (extending the existing acceptance to the
new instrument configuration) to the recorded pre-registration digest;
§3 requires nights two and three to re-hash it at the desk and stop on any
change; and §5 explains which registration the gate actually checks.

Revision 6 (2026-09-10): the owner ruled, by directive
issue 316, that the first night is no longer the first of three blind
derivation nights but an EPOCH-EQUIVALENCE CHECK — one night, compared after
it closes against the thresholds the acceptance already in force carries,
under a rule fixed before the night runs. What that forced:
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
  every identity epoch the active acceptance judges (its own, and any epoch an
  authenticated continuation has carried it onto). A derivation night exists
  precisely because at least one field is stale; if none is — including the
  case where a continuation already covers this machine — this is an ordinary
  night and the ordinary path applies.
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
  alongside the night agent. Its scheduled **epoch** here means seconds since
  1970-01-01 00:00 UTC (distinct from the machine's identity epoch). It is
  derived from **completion**: `t0 + window_max_s + 300 s`, where `t0` is the
  plan's start, `window_max_s` its window length, and 300 s (5 × 60 s) the
  allowance for the courier to email results. Add
  3600 s (60 × 60 s), rounded up to a minute (§1.2). Its first recovery time is that derived local hour and minute;
  the installed calendar repeats at that time until uninstalled. Before completion it logs a stand-down;
  after the courier delivery record `night/courier.sent` exists it skips;
  otherwise it uses the driver's existing recovery checks (§1.3).
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
  prevents a new magistrate **agent** session from launching on this machine.
  A valid plan's span fences, opening at the closed boundary `t0 − 8 min`
  and continuing through completion. After completion, the courier record
  and chain records determine when it closes; without delivery it extends
  through the derived dead-man plus the courier-lock allowance (§1.3).
  The watchdog discovers plans from sibling `*/night_plan.json` files or
  from the installed night job files' `--plan` arguments through
  `installed_agent_fence`. An unreadable installed job file or plan holds
  `HOLD_UNSAFE`, the state that forbids relaunch when safety cannot be proved.
  A discovered active span may adopt supervision of an already-owned session
  to drain it; an installed-only fence returns `FENCED` with `adopt=False`
  after stop checks clear. The night's two LaunchAgents can run during it. See
  `docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines".
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
export WINDOW_ID=<unique attempt identifier, e.g. n1-a>
export REMOTE_URL=https://github.com/mpmdw/JouleWise
export MEASUREMENT_ROOT="/Users/edr/JouleWise-measurement-$NIGHT_DATE-derivation-$WINDOW_ID"
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
on. Installation may be on that date or an earlier date, provided §1.3's
listed span, exclusive plan cutoff and existing gates all permit it.
`WINDOW_ID` identifies a newly planned measurement window; each successor gets
fresh plan, session and custody identifiers, even on the same day. An arm retry
before that window runs keeps this activation's approved bytes and identifiers;
only its attempt number and notice change. Resume at §1.4a without rerunning
§0.2 over existing paths. A changed t0, head, class, path or scientific input
requires ordinary fresh-plan authoring, never editing a failed candidate. Use letters,
digits and hyphens, and satisfy the census check below. Every name below uses
the same date and window identifier so the plan, session, custody and clone
stay together. The fresh-path checks remain mandatory for every attempt.

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
: "${H:?}" "${NIGHT_DATE:?}" "${WINDOW_ID:?}" "${MEASUREMENT_ROOT:?}"
export PLAN_ID="d079-epoch-25g83-derivation-$WINDOW_ID-$NIGHT_DATE"
export SESSION_ID="$PLAN_ID"
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
| `NIGHT_DATE` | `YYYYMMDD` of the real date `t0` falls on; never change the date to avoid a path collision. |
| `WINDOW_ID` | One explicit, unique attempt/window identifier on that date, such as `n1-a` or `n1-b`; shared by all derived names. |
| `PLAN_ID` | The night plan's `plan_id` (§1.1), derived from `WINDOW_ID` and `NIGHT_DATE`. It names the night root, so it is fixed BEFORE any directory exists. |
| `SESSION_ID` | The ledger session this attempt opens, equal to `PLAN_ID`, passed as `--session-id` and baked into the wrapper. The FAIL-route registration still follows §3. It also prefixes every slot attempt id (`<SESSION_ID>-d01`…), so it must survive the census check. |
| `EVIDENCE_ROOT_ID` | The identifier of the evidence root the night's bundles are filed under. **It has no derivable default**: take the literal from the record that registers it and record both in the arm materials (§1.1b step 3). |
| `NIGHT_ROOT` | The night root (§Terms) — `/Users/edr/night-custody/<PLAN_ID>` by convention, and the value the plan's `custody_root` must carry. It is the directory the watchdog's discovery glob looks one level inside (§0.7). |
| `STAGE` | The staging directory the plan is AUTHORED in, deliberately outside the watchdog's discovery path, so that authoring a plan does not arm a night (§0.7, §1.1b step 2). |
| `STAGED_PLAN` | `$STAGE/night_plan.json` — the plan's path while it is being authored, generated from and verified against. §1.4 moves these bytes to `$NIGHT_ROOT/night_plan.json`, and that is the only moment the night becomes discoverable. |
| `CALIBRATION_PLAN` | The **frozen calibration plan**: the committed capture plan a night's captures are taken under, a `calibration_plan.json` from a frozen campaign pack in the clone (`docs/phase_2/window_runbook.md`, §the ALPHA `window.env` example, calls the same file `FROZEN_PLAN` and notes it is not a custody reservation plan). Copy those committed bytes to `$CALIBRATION_PLAN` before §1.1b step 3; the path must be absolute, and the wrapper re-checks the file's `plan_id` and SHA-256 at launch (§1.1a step 3), so a wrong copy fails before the settle rather than at `d01`. |
| `CALIBRATION_LEDGER` | The ledger the night opens its session against — **the clone's own**, never the canonical one. This is exactly the generator's `--ledger` default, written out so the harvest (§2.0) can rebuild it. |
| `LEDGER_HEAD_PIN` | The committed head pin the ledger is authenticated against — again the clone's, and exactly the generator's `--head-pin` default. |

Two worked inputs for the same real date, `NIGHT_DATE=20260916`, produce
distinct names with the assignments above:

| Invocation input | `MEASUREMENT_ROOT` | `PLAN_ID` = `SESSION_ID` | `NIGHT_ROOT` / `STAGE` |
|---|---|---|---|
| `WINDOW_ID=n1-a` | `/Users/edr/JouleWise-measurement-20260916-derivation-n1-a` | `d079-epoch-25g83-derivation-n1-a-20260916` | `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-a-20260916` / `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-n1-a-20260916` |
| `WINDOW_ID=n1-b` | `/Users/edr/JouleWise-measurement-20260916-derivation-n1-b` | `d079-epoch-25g83-derivation-n1-b-20260916` | `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-b-20260916` / `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-n1-b-20260916` |

These are naming examples; a successor still requires harvest and uninstall,
all no-reuse checks, and the applicable registration constraints of §3.

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
ledger that will not authenticate at the desk will not authenticate at `t0`
either. Record the head pin's sequence and digest now — the pre-registration's
`[SEQ]` and `[DIGEST]` fields are filled from the pin in force at the FIRST
night's open, and are then frozen for every night of the campaign that
follows.

### 0.5 Pre-registration committed, with its bracket fields filled

`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` must be
committed inside H with `[DD]`, `[MLX_VERSION]`, `[SEQ]`, `[DIGEST]` and
`[CHAIN_SHA256]` filled. Those five are facts that did not exist when the text
was written; filling them reopens no scientific rule. The plan's
`registration_path` is `night_gate.D166_REGISTRATION_PATH`, the D-166 literal
in `joulewise/night_gate.py`: the fixed repository-relative path
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json`.
The file belongs to a different experiment. It records the comparison rule
that decision D-165 fixed for the D-117 contrast campaign
(`configs/campaigns/d117_contrast_v5`) before that campaign collected data;
the filename instead names D-166, the decision that set that campaign's
workload. What the rule says does not matter to this night, which never
evaluates it. The night gate requires this file for this night's receipt
class and checks exactly one thing, recorded as gate condition C1: it reads
the file as UTF-8 text and requires the SHA-256 of that text to equal the
literal `night_gate.D166_REGISTRATION_SHA256` in the same module. Nothing
else about the file is read. (Beware one word collision: the plan's
`registration_path` — the D-166 literal above — and C1's "registration" are
the gate's own names for THIS file, not §Terms' **Registration**, the set of
ledger sessions a derivation corpus is drawn from.) A receipt class is the
plan's category, and it selects which gate
checks apply; this night's is `DIAGNOSTIC_NO_PACK`, the class for a night
that launches no measurement pack — no campaign's committed bundle of runs,
pinned in a plan by id, root and digest — because this night takes only the
twelve calibration captures (§1.1 defines the class in full). The night's
own scientific pre-registration, the file named at the top of this section,
is bound to the night separately: by H, the measurement commit whose tree
contains it and which the plan pins, and by the digest recorded below and in
§1.5.

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

`[QUIET-MAC]` nights are agent-free. The magistrate exits before `t0 − 8
minutes`; that boundary is the closed start of the plan span, and the resident
supervisor's cooperative ladder enforces it: `standdown.request` at
`t0 − 8 min`, TERM no later than `t0 − 6 min`, KILL no later than
`t0 − 5 min` (`docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines", the boundary table).

Desktop apps that bundle an agent runtime — a shipped command-line agent
binary that the app runs as a local server — count as agents. The ChatGPT
desktop app runs the Codex CLI as `codex … app-server`, and both it and the
Claude desktop app run helper processes (the child processes an app starts
for its windows, network and services) whose argv (the command line a process
was started with) contains `codex` or `claude`; the census matches those
helpers (it does not match the apps' own top-level processes, which are named
`ChatGPT` and `Claude`). Quit both apps before the plan span and keep them
quit through t0. An app still running at t0 refuses the night — the gate
records a refusal and no measurement chain starts; that refusal is correct.

The coded census that the t0 gate and a pack night's arm both run
(`pgrep -lf codex|claude|t3`) matches those helper processes; that is the
ruled behaviour, and the pattern is not narrowed to exclude them.

**Step 3b — arm-time census (D-180 clause 3).** Terms are defined in the
first-use table (§8). Stop all own seats, delegated tasks and background jobs
using the activation's real task controls; record their task IDs and results
and invent none. After staging the plan, run the following from the reviewed
measurement checkout, with `PY` naming that checkout's interpreter;
repeat it immediately before publication in §1.4:

```zsh
"$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"
```

Preserve the command's output in the arm transcript, including its plan digest,
own PIDs, session descendants, workload categories and diagnostics. The parsed
plan's `receipt_class` alone selects the rule; a plan name or caller flag cannot
select it. For `REHEARSAL_STUB` only, an idle interactive Claude or Node/T3
session is not foreign: only the listed workload families make its tree busy.
Those families are unittest, pytest, `scripts/shard_tests.py`, powermetrics,
nvidia-smi, `scripts/run_night.py`, `scripts/run_campaign.py`,
`scripts/capture_t0_step.py`, `chain.zsh`, Python `-m joulewise*`, vLLM/MLX
serving or module runners, `codex exec`, and Claude `-p`/`--print*` children.
Inspect every descendant, including through shells and helpers; fixture paths
do not exempt a listed workload. Unknown commands and unreadable observations
read as idle, with observation diagnostics retained. The exact recognition
rules are in `joulewise/arm_census.py`; Node/T3 coverage is PROVISIONAL and
Electron roots are not claimed.

The caller's own PPID chain is exempt for every class. For a stub, its own
interactive or headless root receives the same idle-tree exemption: idle MCP
helpers, shells and other non-workload descendants are exempt, but workload
descendants still make the census busy. A sibling seat outside that subtree
remains foreign. For a stub, exit 3 stops publication on a busy tree or remaining foreign
agent; exit 0 permits the next step. For `DIAGNOSTIC_NO_PACK` and
`TRANSACTION_PACK`, the command exits 0 with diagnostics and grants no idle
exemption: the existing all-agents-closed arm precondition still applies,
without a new coded publication gate. Invalid plans exit 2 and must be repaired.
Exit 1 means the census did not run — preserve the transcript; not a busy verdict.
Do not signal foreign processes. Never run the chain, the driver, a full
preflight or a calibration capture from the live activation as a quietness test.

All sessions must still close before the plan span. At t0 the unfiltered night
gate still records `night_refused_agent_present` for any agent hit, so no real
measurement chain starts; the rehearsal driver retains its harmless-stub
continuation and records census hits without killing the stub. An arm-time
observation grants no plan-span exemption and predicts no future inactivity.

For `DIAGNOSTIC_NO_PACK` and `TRANSACTION_PACK`, an arm blocked ONLY by an otherwise idle
interactive session is the `arm_idle_interactive` retry cause under §1.4a once that session
closes; A172 never equates interactive with idle for those classes, and missing evidence
follows the existing refusal path. A173 alone owns classification and exemption changes.

### 0.7 Nothing else is armed, and every discoverable root is retained

No stand-down, no Ed NO, no unresolved owner-authored `directive` issue, no
discoverable prior plan root that is ACTIVE or UNKNOWN (a harvested, retained
root may remain discoverable), no active or indeterminate measurement ownership.
Remove every `REHEARSAL_STUB` plan root before arming any real plan
(`docs/process/MAGISTRATE_WATCHDOG.md`, §"Install handoff").

**Sibling discovery uses one exact glob; installed plists provide a second fence.**
The watchdog enumerates sibling plans by globbing `*/night_plan.json` in the
PARENT of its own state directory — `glob_plans` in `scripts/magistrate_watchdog.py`, whose
state root is `/Users/edr/night-custody/magistrate`, so the enumerated set is
exactly `/Users/edr/night-custody/*/night_plan.json`: one level down, that
filename, nothing else. A plan authored at `$STAGED_PLAN` under
`/Users/edr/night-plan-staging/<PLAN_ID>/` is therefore outside sibling
discovery, which is why §1.1b authors and verifies there. §1.4's `os.replace`
into `$NIGHT_ROOT/night_plan.json`, after the email, makes it discoverable.
Independently, the watchdog reads the `--plan` paths in both installed night
plists and fences their active spans, holding unsafe on unreadable or malformed
inputs. The installer requires the resolved plan path to be
`<custody_root>/night_plan.json`; staging is never an install destination.
The night's own driver never discovers anything — launchd hands
`scripts/run_night.py` the plan path as a
`--plan` argument (its `--plan` is `required=True`), so the driver reads the
file it was installed with and no other.

Check it. Prior roots may be discoverable; what stops an arm is any root whose
chain is open, whose span is active, whose night agents are installed, or whose
records show no terminal state. The executable form is
`python -m joulewise.evidence_night check --candidate STAGING`, whose
`night_agents` and `retained_roots` items must both pass with every inventoried
root classified `retained` (contract item 4: `ACTIVE` and `UNKNOWN` refuse).
For a manual read, run the same classifier the check binds, read-only, from the
root of the entry checkout:

```zsh
python3 -B -c 'import json; from joulewise import evidence_night as e; print(json.dumps(e.retained_roots({"roots_under": "/Users/edr"}), indent=1))'
```

It prints one row per `/Users/edr/night-custody/*/night_plan.json` with
`classification`, `reason` and the full paths of every marker found, then
`verdict`. Every row must read `retained`; an `ACTIVE` or `UNKNOWN` row, a
`Refused:` exit, or any installed night plist stops the arm. The classifier
raises `Refused` when a path it inspects, or any directory above that path, is
a symbolic link: the root's `night_plan.json`, its `night/` directory,
`night/courier.sent`, `night/result.json`, `night/chain.exited`,
`night/chain.started`, or any file in `night/` matched by the refusal names in
contract item 4. A symbolic link elsewhere under a root, such as `night/notes`
or `<root>/scratch`, is not inspected and does not refuse. Do not move or edit
a root to change its row. This is the same function `check` runs (contract item
4), evaluated at the current time with the entry checkout's timing constants,
so it sees the span rule.

Source: cold-gate ruling 2026-09-21 (packet 05 Q2, lane A230); the shell loop
that ruling illustrated was replaced by the direct call on the cold gate's
round-3 ruling (activation ce7c57a9, Q5) after it printed `retained` for a
symlinked `night/` directory that the classifier refuses.

### 0.8 The clone's tree is clean, and the two desk inputs are written

**Clean tree** means: the measurement clone has no uncommitted change of any
kind — no modification, no staged file, no untracked file. Check it and record
the output verbatim in the night's arm materials:

```zsh
git -C "$MEASUREMENT_ROOT" status --porcelain
```

The expected output is **nothing at all**, zero bytes. Any line is a stop:
stand the night down and re-cut the clone (§0.2).

Keep this arm-time check and its recorded output: it establishes the clone's
condition before the night is armed. At t0 the night gate checks the planned
measurement clone again, after confirming its committed `HEAD`. It runs Git
status with untracked files included and the fsmonitor hook disabled. A dirty
clone is refused as `night_plan_stale`; a clone whose status cannot be checked
is refused as `night_probe_error`. If either happens, find what wrote into the
clone and re-cut it (§0.2). Re-arming with a fresh plan does not repair the
clone.

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
| `this machine's identity epoch is one the acceptance at <path> already judges … this is an ORDINARY night, not a derivation night` | Nothing is stale: the machine matches the acceptance's own epoch, or an authenticated continuation already carries the acceptance onto this epoch (the PASS route completed). | **Stop.** The premise of the lane is gone — re-run §0.3; after a continuation, run the ordinary window path. A derivation night captured here would be refused by the capture writer at `d01` with the settle already spent. |
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
| `registration_path` | `night_gate.D166_REGISTRATION_PATH` — the fixed D-166 registration path required for this receipt class by the night gate (§0.5), `configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` |

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
the chain's pre-settle work (input preflight and the session reservation, both
of which run BEFORE the settle so that an unusable declaration costs no window
time — the reservation's `--pre-reserve-strict` enforcing readiness check is
one bounded custody pass inside the reservation itself, and the chain runs no
separate readiness command; `recover_calibration_ledger.py readiness --phase
pre-reserve` remains a DESK command, `docs/phase_2/window_runbook.md:466`),
per-capture overrun beyond 600 s pushing later slots later, and the driver's
own work before it starts the chain. Allocate **1320 s (22 min)**:

```
WINDOW_MAX_S = 7680 + 1320 = 9000 s   (2 h 30 min)
```

For an explicitly authored v4 plan, preserve this entire **9000 s post-bind
allocation** and add the sealed bind allocation before it. With `bind_max_s =
600`, author `window_max_s = 9600`: 600 s binding + 7680 s programmed span +
300 s minimum pre-settle allowance + 1020 s remaining margin. Binding means
observing interval CPU activity before reservation or a chain-start claim;
it does not consume the reservation's settle or change any slot constant.
Legacy v2 plans retain their one-shot load check and 9000 s allocation.
The CPU cutoff and admission parameters are provisional, pending cold-gate
proposition 4 and the evidence lane. No candidate cutoff is supplied. The JSON
must include a nonempty `cutoff_authority` naming the affirming ruling; no key
has a generator default. Validation fixtures use a non-admitting zero cutoff
and `TEST-ONLY-NOT-A-RULING`, never an activation policy.

To author a NEW v4 plan without changing the template or a sealed plan:

```sh
python3 scripts/gen_derivation_night.py \
  --quiet-admission-json "$STAGE/quiet-policy.json" \
  --plan-template "$STAGE/new-coordinates.json" \
  --new-plan "$STAGE/new-night-plan.json" \
  --new-plan-id "$NEW_PLAN_ID"
```

The template must already carry the new night's reviewed coordinates, fresh
timing and custody paths; the output id must differ from its template id.
The generator creates the plan and a `.runsheet.md` companion exclusively,
requires post-bind runway at least the computed 7980 s schedule minimum,
validates window_max_s ≥ bind_max_s + post_bind_budget_s, and states the bind
allocation. The 9000 s post-bind allocation above retains the existing margin.
Then generate/verify the wrapper using the existing `--plan` mode with the
new v4 plan. Without the explicit flag, `--check` and the reviewed v2 example
are byte-identical. See [the complete admission contract](../contracts/night_quiet_admission.md)
for sample accounting, receipts, deadline derivation and successor evidence.

This is an operational allocation, not a measured completion guarantee. Do not
shorten the settle, the cadence, the slot count or the capture budget to fit a
window; shorten nothing and move `t0` earlier instead.

**The generator's floor under this allocation.** `gen_derivation_night.py`
refuses to emit a wrapper at all unless the window can hold the programmed
span plus a **pre-settle allowance** of 300 s. The pre-settle allowance is the
first of the three margin items above, isolated and made mandatory: the time
spent INSIDE the window but BEFORE the settle begins — the chain's input
preflight, strict bounded readiness inside reservation and the session
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
(133 min)**, **armed `window_max_s` 9000 s (150 min)**. Install spans (§1.3)
are intervals in which the operator may install the jobs; they do not bound
or contain the acquisition window.

**The custody budget, and why one measured pass is not the whole bill.**
`CUSTODY_BUDGET_S` (120 s unless the chain's caller overrides it) is the
allowance for ONE preparation operation's custody work: checking that every
governed file the ledger names is present and hashes to the recorded value.
Call one sweep over all of those files a **custody pass**, and call its
wall-clock cost T. The reservation makes exactly ONE pass, and the arm-time
launchd access probe (§1.4) reports that one pass as the receipt field
`custody_elapsed_s`. So the probe measures T; it does not measure the night's
whole custody bill.

`custody_elapsed_s` is measured slightly WIDE of the pass itself, and
deliberately so. The clock it reports is the seconds since the operation's
allowance object (`CustodyDeadline`) was constructed, and that construction
happens before the ledger file is read and parsed. So `custody_elapsed_s`
covers ledger read + ledger parse + the custody pass, not the pass alone: it
is an over-report of T, never an under-report. Over-reporting is the safe
direction here, because the number is used to decide whether the writer's
passes fit inside one allowance — a gate that errs toward refusing a night,
not toward arming one that cannot finish. Same field, same meaning, in the
capture writer's own success receipt (below).

The capture writer sweeps the corpus four times per slot — its preflight
snapshot, its under-lease snapshot, its enforcing readiness check and its
slot validation — but on a healthy slot only TWO of those sweeps open and
hash the files. The other two are answered from a **custody memo**: the set
of (observation, governed file, expected hash) entries a sweep already
checked, kept on the one shared allowance object and reused by a later
sweep. The memo is armed only once the writer holds the ledger's **writer
lease** — the advisory lock every calibration writer takes before it
appends, so that while one writer holds it no other calibration writer can
change the ledger — and it is thrown away when the lease is released; so the
preflight sweep, which runs before the lease exists, never feeds a later
one. The lease does not lock the governed files themselves, and that has a
price: what the memo therefore stops seeing, and why the project accepts it,
is stated in `docs/contracts/calibration_ledger_append.md` under "The
under-lease custody memo". The memo is also keyed on the ledger's physical
head digest — the hash of its last receipt — so the pre-capture recovery
step that runs between the second and third sweeps invalidates it whenever
it actually appends anything, and the writer then pays a third honest sweep.

So: two reads on a healthy slot, three when recovery changed the ledger —
and three again when the corpus is CORRUPT. The preflight sweep seeds
nothing because it runs before the lease, and a sweep that REFUSES is never
memoized either, so the refusing under-lease sweep and the refusing re-read
after it both open the files: three reads again.

Three — the worst case, not the healthy count — is the constant
`WRITER_CUSTODY_PASSES` in `joulewise/night_agent_install.py`, and the
installer refuses to arm unless

```
custody_elapsed_s × WRITER_CUSTODY_PASSES × 1.5 ≤ custody_budget_s
```

The 1.5 is half a pass of margin (**headroom**) and nothing more: the corpus
grows with every finalized slot, and the passes are not identical in cost. It
is not a spare pass — the worst case is counted in `WRITER_CUSTODY_PASSES`
itself, because a slot whose corpus is corrupt must have room to reach its
typed `calibration_ledger_custody_invalid` rather than be cut off by a
`calibration_ledger_custody_timeout`, which would name the wrong cause. With
`WRITER_CUSTODY_PASSES = 3` and a 120 s budget, a probe is admissible only if
T ≤ 26.67 s (120 ÷ 4.5). Worked case: a probe reporting T = 90 s passes the
six-hour freshness check and every digest binding, yet the writer's three
passes would need 270 s of a 120 s allowance — a guaranteed
`calibration_ledger_custody_timeout` on slot `d01`. Such a night refuses at
the desk, at install time, naming `custody_elapsed_s`. A probe that verified
zero observations while the ledger already holds finalized ones is refused
too, naming `observations`: a pass over nothing certifies nothing.

The lever is the gate, not a larger budget: enlarging `CUSTODY_BUDGET_S`
spends window time the cadence arithmetic above has already allocated.

**Where a healthy night's T comes from.** The gate above is sized against T,
so T has to be observable on nights that WORK, not only on nights that refuse.
The capture writer's success receipt — the single JSON object it prints to
standard output, captured in `chain.stdout.log` — carries `custody_elapsed_s`,
`observations` and `custody_passes` for exactly that reason.
`custody_elapsed_s` is that slot's PREPARATION allowance — the one its
preflight snapshot, under-lease snapshot, readiness check and slot validation
shared — read at the end of preparation and measured the same wide way as the
probe's field (ledger read + parse + passes). `observations` is how many
custody-bearing observations that preparation counted; it is 0 for a
session's first slot, because none of its rows is finalized yet, and rises as
slots finalize. `custody_passes` is how many of that slot's sweeps actually
read the files rather than being answered from the memo: 2 on a healthy slot,
3 when the recovery step appended or a sweep refused. Read all three out of `chain.stdout.log`
after a night and you have the real per-slot series to check
`WRITER_CUSTODY_PASSES × 1.5 × T ≤ CUSTODY_BUDGET_S` against, instead of a
single arm-time sample — and `custody_passes` says whether the constant on
the left is still the truth.

**The inherited budget marker.** The chain exports
`JOULEWISE_NIGHT_CUSTODY_BUDGET_S` with the same seconds as
`CUSTODY_BUDGET_S`, and every process it starts inherits it: the reservation,
each capture writer, and the end-of-window session abort. A governed-file
read that was handed no budget object of its own is bounded by that inherited
value, and a read that cannot be bounded refuses
`calibration_ledger_custody_invalid` rather than blocking. It is a BUDGET — a
fresh allowance for each operation that starts under it — and not a clock
time, because the session abort runs when the window is already spent and
would otherwise refuse the one operation that closes the session.

*What the end-of-window abort costs in the worst case.* The abort
(`abort_window_exhausted` in the chain, which runs
`recover_calibration_ledger.py … abort-session --custody-budget-s`) needs ONE
custody value: the state of the session's **next slot**, the slot the window
ran out on. That is the value that decides whether the session can be closed
or whether complete capture custody must be finalized instead. So the abort
asks for that slot's state and no other, under one allowance:

```
1 × CUSTODY_BUDGET_S = 120 s   (plus seconds of lease and repair work)
```

`CUSTODY_BUDGET_S` (120 s) is set in the chain
`scripts/night_chains/calibration_derivation_only.zsh`, and the chain passes
it to the abort as a flag exactly as it passes it to the reservation and to
each capture writer. There is deliberately no `--custody-deadline-epoch-s`
here: the abort runs when the window is already spent, and an absolute
deadline would refuse the one operation that closes the session.

One pass is also the only figure the install-time headroom gate certifies.
That gate admits a night when `custody_elapsed_s × WRITER_CUSTODY_PASSES ×
1.5 ≤ custody_budget_s` — one measured pass of up to 26.67 s at three passes
and a 120 s budget. It never certified twelve passes, so an abort that read
all twelve declared slots under one shared allowance could time out on a
custody root the installer had legitimately admitted, and a timed-out abort
leaves the ledger session OPEN under a live writer lease, which is the state
desk recovery finds hardest to resolve (`LIVE_WRITER_CONTENTION`). Reading
only the slot whose state is consumed removes that failure entirely: the
pre-declared locators for the other slots are not opened, hashed, or given a
custody worker, and their entries report `not_inspected` rather than a state
nobody measured.

If that one pass exhausts its allowance, the abort command refuses with
`calibration_ledger_custody_timeout`, writes the
`joulewise.calibration_refusal.v1` document at
`JOULEWISE_CALIBRATION_REFUSAL_PATH` (the chain exports it into the night
directory) and exits 2; the driver reads that document and records verdict
`REFUSED` with `aborted_reason` `night_calibration_refused`, so the delivered
result says the night did not finish. A chain that exits 2 writing NO such
document is still recorded as verdict `GO` with `chain_exit_code` 2 — for
that case, read the chain exit code, not the verdict.

*And the driver no longer waits for any of it indefinitely.* 120 s of abort is
covered by the driver's own shutdown allowance, `WINDOW_SHUTDOWN_GRACE_S` =
300 s in `scripts/run_night.py`: **end-of-window abort is bounded by one
120 s custody budget for the abort's single custody read; the driver terminates the chain 300 s after
the exclusive window end.** Proving the chain's whole process group gone takes
at most 70 s after that (`TERMINATION_BOUND_S`: 30 s to reap the chain, 5 s of
group census, 30 s after the SIGKILL escalation, 5 s of census), and the
courier then has its own 300 s — 670 s in total against the 3900 s the
dead-man formula below leaves after the window end
(`COURIER_DEADLINE_S` 300 s + `DEADMAN_GRACE_S` 3600 s). The unbounded
alternative is what held the 2026-09-16 night for 11 h 07 m.

The 300 s grace covers the 120 s abort budget plus a writer overrun of up to
180 s beyond its capture budget (a nominal figure: lease acquisition, any
ledger repair and the closing write also consume the grace, so the real
headroom is somewhat less): the chain starts a slot only if
`next_start + 480 ≤ END`, and that 480 s budget is predictive (it never kills
the writer). A larger overrun can have its lawful closing abort interrupted
at +300 s, leaving an OPEN session that the next arm refuses and the desk
recovers. The writer lease is a kernel `flock` (an exclusive file lock the
operating system manages and releases when the holding process exits), so
this leaves no stuck lease.

**The dead-man check (updated 2026-09-15, INSTALL-WINDOWS-MULTI-01).**
`scripts/run_night.py` defines `COURIER_DEADLINE_S = 300` (5 × 60 s),
`DEADMAN_GRACE_S = 3600` (60 × 60 s), and `deadman_epoch(plan)`:

```
completion = t0 + window_max_s + COURIER_DEADLINE_S
D = deadman_epoch(plan) = 60 × ceil((completion + DEADMAN_GRACE_S) / 60)
required: completion < D
```

`ceil` means round upward to the next integer; if already integral, keep it.
The **courier** is the process that emails the night's result. Its 300 s
allowance is AFTER the window; the generator's separate 300 s pre-settle
allowance is INSIDE it. The courier can make four 300 s attempts with waits
of 60, 180 and 600 s: `4 × 300 + 60 + 180 + 600 = 2040 s`, below the
3600 s dead-man grace. Neither allowance enlarges the acquisition window.

Worked example, using the earlier plan's coordinates solely for arithmetic
under this design (`t0 = 2026-09-12 02:56:00 PDT`, epoch `1789206960`):

```
t0                    = 1789206960   (2026-09-12 02:56:00 PDT)
t0 + 9000             = 1789215960   (2026-09-12 05:26:00 PDT)  window end
completion            = 1789216260   (2026-09-12 05:31:00 PDT)  courier deadline
completion + 3600     = 1789219860   (2026-09-12 06:31:00 PDT)
D = 60 × ceil(1789219860 / 60) = 1789219860
1789216260 < 1789219860        PASS; 3600 s = 60 min of slack
```

The code checks `completion < deadman_epoch(plan)` directly; it does not
compute a separate maximum window against a fixed D. Changing the window
recomputes D. With sane constants completion is always at least 3600 s before
D, so the registered `night_plan_overruns_deadman` refusal remains in code but
is unreachable.

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
   this hardware), then the chain's input-presence checks.
3. **The session reservation.** Its `--pre-reserve-strict` enforcing check
   refuses before retry, recovery or append and uses one bounded custody pass.
   This consumes window time up to the custody budget. The ledger call then opens the
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

Keep `window_max_s = 9000` and the strict completion/dead-man check above. A derived
completion/dead-man check failure indicates inconsistent timing code or plan
inputs: stop and resolve it before arming. Never hand-edit the dead-man time.

### 1.3 Install span, install close and the exit boundary

**Updated 2026-09-15 — INSTALL-WINDOWS-MULTI-01, D-180 clause 1 and D-181
clause 1.** Install BOTH agents on any day after the notice email is sent,
before the plan's **install close** (the last allowed installation boundary),
and inside a listed **install span** (a recurring local-time interval).
Same-day successors are a machinery capability; for the three FAIL-route registration nights §3 item 3 still requires distinct calendar days.
The admissible interval opens with the notice send and closes exclusively at:

```
PLAN_LEAD_S = 480 s = 8 × 60 s
INSTALL_CLOSE_MARGIN_S = 120 s = 2 × 60 s
install_close_epoch(plan) = t0 - PLAN_LEAD_S - INSTALL_CLOSE_MARGIN_S
                         = t0 - 8 min - 2 min = t0 - 10 min
```

**LEAD-MARGIN-01:** the flat one-hour install pad introduced by `391a194b`
is now two minutes. It separates installation and handback from REQUEST,
allowing twelve nominal ten-second resident polls to discover the plan; it is
not a physical settling requirement. The exclusive cutoff and installer
rechecks still apply. Installation must finish strictly more than **ten
minutes** before t0 (eight-minute plan lead plus two-minute pad).

The resident ladder originated in `2b4476cb` and hands-free-week file 15 as a
cooperative handback, TERM grace and untouched-idle allowance. D-180 retained
that span; D-181 permits windows whenever the machine is quiet. The new
PLAN/REQUEST/TERM/KILL leads are **8/8/6/5 minutes**: fence launches and request
exit at t0−8, TERM at t0−6, then KILL at t0−5. The request asks for exit
within five minutes as a courtesy; TERM follows an on-time request by two
minutes and overrides that courtesy. Absolute TERM/KILL boundaries win even
after a late request. The arming activation still exits before the request boundary.

D-171(b) ratified the old 25-minute lead for a physical reason: idle-triggered
daemons (XProtect and kin) should run during **at least ten minutes of
untouched idle before the first capture**. With this derivation chain, KILL
at t0−5 plus `SETTLE_S = 600 s` before d01
(`scripts/night_chains/calibration_derivation_only.zsh:76`; §1.2's programmed
span and `t0 + Δ + 600` schedule) gives quiet-to-first-capture
**≥ 300 + 10 + 600 s ≈ 15.2 min ≥ 10 min**, using ten seconds of driver/start
delay in that timing budget. Even without crediting that delay,
`KILL_LEAD_S + SETTLE_S >= 600`. This meets the idle duration rule under the
new chain, but reduces the margin against a late-starting scan from roughly
25 to 15 minutes; load is not rechecked per capture (thermal only).
Ed **RATIFIED the conservative 8/8/6/5 chain on 2026-09-16 at 00:20 PDT**
("do whichever is safest first quick second"); see the D-171(b) addendum (A210).

The census needs the magistrate, supervisor and every Codex child gone.
With five-second samples and `e^(−5/60)` decay, one-minute load-average excess
falls to 0.674% after 300 s (KILL) and 0.248% after 360 s (TERM). Allowing ten
seconds of poll slack and about five seconds for signalling/exit leaves
285/345 effective seconds, retaining 0.865%/0.318% of excess. Under this
model, KILL-only teardown at t0−5 clears the **2.0** gate for excess load below
about **116–173**, at base load 1.0–0.5 (115.6 at base 1.0; 173.4 at base 0.5).
TERM at t0−6 provides the larger settling margin. KILL is the five-minute
floor, not a promise of passing t0; polling, descendant signalling, census
and supervisor-exit latency consume the budget.
The resident polls every
ten seconds: the 120/60-second phase gaps contain 12/6 polls and leave nominal
observation slack of 110/50 seconds. The launchd template's 300-second
`StartInterval` starts or recovers the resident and **cannot guarantee these
phases after supervisor failure**. Blocked I/O or scheduling may also delay
enforcement. The unchanged t0 gates refuse a surviving tree or excess load;
that is the fail-closed backstop. HID-idle, boot-clock and custody gates are
unchanged too.

`INSTALL_SPANS` in `scripts/run_night.py` is the one list of per-day local
`("HH:MM", "HH:MM")` spans. The shipped list is `(("00:00", "24:00"),)`:
midnight to the next midnight, open included and close excluded. Ed may narrow
that list. Entries must be ordered, disjoint, and close after open; `24:00`
is allowed only as a close. `install_spans_for_day(day)` resolves every entry
to epoch boundaries for that local date; `install_span_containing(now_epoch_s)`
returns the containing pair or `None`. This respects local daylight-saving
offsets; do not assume a local day always lasts 24 elapsed hours.

Print the plan's schedule from the measurement clone before sending notice:

```zsh
"$PY" -B scripts/run_night.py schedule --plan "$STAGED_PLAN"
```

The JSON prints `t0_epoch_s`, `install_close_epoch_s`, `deadman_epoch_s`,
both agents' calendar fields, and `install_spans_today`. To print every listed
span for the chosen install day and the plan boundaries with local offsets,
replace `<YYYY-MM-DD>` with that local date and run from the clone:

```zsh
"$PY" -B - "$STAGED_PLAN" "<YYYY-MM-DD>" <<'PY'
import json, sys
from datetime import date, datetime
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import (
    COURIER_DEADLINE_S, deadman_epoch,
    install_close_epoch, install_spans_for_day,
)
from scripts.magistrate_watchdog import PLAN_LEAD_S
plan = NightPlan.from_mapping(json.loads(Path(sys.argv[1]).read_text()))
def show(label, epoch):
    print(label, datetime.fromtimestamp(epoch).astimezone().isoformat(), epoch)
for i, (start, end) in enumerate(install_spans_for_day(date.fromisoformat(sys.argv[2])), 1):
    show(f"install span {i} open", start)
    show(f"install span {i} close (excluded)", end)
show("install close (excluded)", install_close_epoch(plan))
show("plan span / exit boundary", plan.t0_epoch_s - PLAN_LEAD_S)
show("t0", plan.t0_epoch_s)
show("completion / courier deadline", plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S)
show("dead-man", deadman_epoch(plan))
PY
```

Observed output from the two commands above, using a synthetic v2 plan at
`/tmp/install-windows-docs-synthetic/night_plan.json` with
`t0_epoch_s = 1789552560`, `window_max_s = 9000`, install date `2026-09-15`,
and the host's PDT timezone. This is a desk arithmetic check, not an arm.
The first command's `install_spans_today` always uses the execution date;
the second block uses the explicitly supplied date.

```text
{"deadman_calendar": {"Hour": 6, "Minute": 31}, "deadman_epoch_s": 1789565460.0, "install_close_epoch_s": 1789551960.0, "install_spans_today": [[1789455600.0, 1789542000.0]], "night_calendar": {"Day": 16, "Hour": 2, "Minute": 56, "Month": 9}, "t0_epoch_s": 1789552560.0}
```

```text
install span 1 open 2026-09-15T00:00:00-07:00 1789455600.0
install span 1 close (excluded) 2026-09-16T00:00:00-07:00 1789542000.0
install close (excluded) 2026-09-16T02:46:00-07:00 1789551960.0
plan span / exit boundary 2026-09-16T02:48:00-07:00 1789552080.0
t0 2026-09-16T02:56:00-07:00 1789552560.0
completion / courier deadline 2026-09-16T05:31:00-07:00 1789561860.0
dead-man 2026-09-16T06:31:00-07:00 1789565460.0
```

Print every listed span, not only the one intended for the arm. The notice and arm record
must give each boundary as local date/time with UTC offset plus epoch seconds
(seconds since 1970-01-01 00:00 UTC). Record the actual notice-send time as
open; installation must satisfy both `notice_sent <= now < install_close`
and membership in a listed span. Existing plan-age and census gates still apply.
Each retry sends a new notice and begins a new installer transaction. No
transaction may switch spans after selecting its first one.
The arm-time census in §0.6 changes neither install close nor the agent-free
plan span; its idle-session exception applies only to rehearsal stubs.

The installer checks these refusals before creating its output directories or
rendering plists. Timing/location diagnostics print `<reason>: <summary>; <detail>`;
the summary names `now_epoch_s`, `t0_epoch_s`, `install_close_epoch_s` and
`deadman_epoch_s`, each with a local ISO-8601 time. `install_outside_span`
also prints `install_spans_today`; `plan_outside_custody_root` prints `plan`
and `expected`. A job's **label** is its name in launchd. The installer reads
each label as **LOADED** (the query finds the job), **ABSENT** (the query
establishes that the job is not loaded), or **UNKNOWN** (the query cannot
establish either state). A query error alone does not establish absence.
UNKNOWN counts as loaded for safety: the installer refuses admission or
file removal. Admission refuses with
`night_agent_already_loaded … state=unknown rc=<n> stderr=<diagnostics>`
(exit 3), preserving the query's exit code (`rc`) and error output (`stderr`).
During retention cleanup or uninstall, each UNKNOWN query instead adds
`liveness_unknown: <label> rc=<n> stderr=<first line>` with the query's exit
code and first error-output line.
The loaded-job diagnostic names `label=com.joulewise.night`
or `label=com.joulewise.night.deadman` and identifies an unknown state when applicable.
Earlier interpreter, plan, pin, courier, preflight and existing-record checks
can refuse first.

| Refusal | Exit code | Condition / recovery |
|---|---|---|
| `install_span_closed` | 2 | `now >= install_close_epoch(plan)` or a later check reaches the initially selected span's close; do not install this plan late. Re-plan under the handback procedure. |
| `install_outside_span` | 2 | `now` is outside every listed `INSTALL_SPANS` entry; use an allowed span before the plan's close. |
| `plan_t0_in_the_past` | 2 | `t0 < now`; author a future plan. |
| `night_agent_already_loaded` | 3 | `launchctl print` succeeds for `gui/<uid>/com.joulewise.night` or `gui/<uid>/com.joulewise.night.deadman`, or either query is UNKNOWN; finish the prior harvest and documented uninstall before another arm. Resolve an UNKNOWN query with a human before proceeding. `--render-only` skips this loaded-job check. |
| `plan_outside_custody_root` | 2 | Real install only: resolved `--plan` is not the plan's `<custody_root>/night_plan.json`; publish through §1.4 before installing. `--render-only` accepts a staged plan and renders that future published path into both plists. |
| `night_plan_malformed` | 2 from `schedule`; 3 from the installer's earlier plan validation | Missing/malformed `t0_epoch_s`, `window_max_s` or `authored_epoch_s` (or another invalid plan field); the detail identifies the validation failure. |
| `plan_schedule_unrepresentable` | 2 | `schedule` cannot load the plan or represent derived arithmetic/calendar values, including `window_max_s=10**15` or `10**400`; detail preserves the underlying error. This is representability, with no maximum-window policy ceiling. |
| `install_spans_unresolvable_on_day` | 2 | A day's resolved spans have nonpositive duration, are out of order, or overlap after DST resolution; detail names the day and offending span/pair. No span is repaired, reordered or dropped. |
| `plan_t0_not_minute_aligned` | 2 | `t0_epoch_s` is not aligned to a whole minute; `schedule` and the installer refuse before rendering or bootstrapping. Author a minute-aligned plan. |
| `plan_t0_ambiguous_local_time` | 2 | The local wall-clock minute at `t0` maps to two distinct epochs during a DST fold; both occurrences are refused by `schedule` and the installer before rendering or bootstrapping. Choose an unambiguous minute. |
| `retained prior plist: <path>; re-run --uninstall` | 3 | A `.prior` sidecar holding the bytes an install replaced already exists. Nothing restores it automatically after the installer exits. Copy it by hand if you need the old plist back; `--uninstall` deletes both the plists and the sidecars. Complete the documented uninstall before trying another install. |
| `unsupported plist destination: <path>` | 2 | A plist or its `.prior` path is not a regular file, for example a directory or symbolic link. Resolve that destination before retrying. |
| `--render-only directory must differ from launch_dir` | 2 | The resolved render directory is the installation directory (`launch_dir`). Choose a separate directory for rendered files. |
| `probe receipt launch_context differs from install: <label>` | 2 | The installed night or dead-man job differs from the verified probe rendering; re-run the probe before installing. |

A plan's `t0` must fall on a whole minute that occurs exactly once in local time.

After both bootstraps (launchd's job-load operations) and verification, the
installer evaluates one **commit gate**, the check that authorizes success.
It reads the clock after the last launchd mutation and requires that time to
be strictly before both the plan cutoff and the initially selected span's
close; a later span cannot replace the selected one. One final evaluation
ensures earlier clock checks cannot authorize success after loading has
crossed a boundary. A failed install may already have loaded a job, so deleting
its job file (a **plist**) immediately would leave a loaded job without its
file. Before replacing or deleting files during failure cleanup, the installer
requires **proof of unloading**: queries must establish ABSENT for BOTH labels.
UNKNOWN is insufficient. **`.prior` sidecars** hold the bytes an install
replaced. Nothing restores them automatically after the installer exits: a
later install refuses while one is present, and `--uninstall` deletes both
the plists and the sidecars. Copy a sidecar by hand if you need the old plist
back.
SIGINT, SIGTERM and SIGHUP handlers are installed before argument parsing and
only record the first signal. Ordinary-code polls honor it before the next
mutation: response latency is bounded by one adapter call plus its timeout
(5 seconds for launchctl), or by the validation subprocess's runtime. Before
the handlers are installed, interpreter startup retains its usual signal
behavior. The commit gate evaluates the clock predicate, then takes its final
signal poll and assigns COMMITTED directly: a signal recorded during the clock
read rolls back with its signal code; one recorded after that latch is discarded
and exit 0 with the pins stands. A refusal already selected also keeps its code.
D6 teardown is **uninterruptible by construction (no raising handler exists)**:
it never polls, so signals during rollback are recorded and discarded. After
completion these three signals remain ignored until CLI process death;
in-process callers explicitly release the shield to restore their dispositions.
A stalled stdout pipe after COMMITTED can require SIGKILL to free it; handback
pipes must drain. SIGKILL/SIGQUIT skip teardown and can leave `.prior` sidecars
that make the next install refuse with exit 3; follow the sidecar recovery above.

These conditions give an install exactly one of five outcomes:

| Outcome (meaning) | Exit code | What remains on disk | Operator's next action |
|---|---|---|---|
| **committed** — both agents are loaded and verified | 0 | The installed plists remain; cleanup of prior plists' `.prior` sidecars is best-effort. A cleanup failure prints `warning: prior sidecars not removed: <detail>` and still exits 0. | Complete the arm record and exit by the boundary below. |
| **restored** — failure before or during loading leaves the pre-attempt files in place, or puts them back after both labels are established absent | Original failure code: 143 (SIGTERM), 130 (SIGINT), 129 (SIGHUP), 1, 2 or 3 | Any overwritten prior plist is restored byte-for-byte with its original modification time (`mtime`); newly created plists are removed. An admission refusal leaves existing files untouched. | Record the original failure and follow §1.4 recovery; do not report a successful arm. |
| **retained** — cleanup cannot establish that both labels are unloaded | 4 | Nothing is changed by file cleanup: the plists and their `.prior` sidecars are kept as they stand. Nothing restores the sidecars automatically after exit. | Stop. Treat the machine as still holding a loaded label, including when its state is UNKNOWN. Copy a sidecar by hand if you need the old plist back; successful `--uninstall` deletes both the plists and the sidecars. A human must resolve it; no retirement, unpublishing or successor arm may follow until `--uninstall` exits 0. |
| **failed teardown** — an unexpected teardown error leaves state RETAINED | 1 | Remaining plists and `.prior` sidecars are retained; teardown may have completed only some operations. The diagnostic is `teardown failed; retained: <type>: <message>`. | Stop and preserve the remaining files for human inspection. Do not assume both labels are unloaded or report a successful arm; no retirement, unpublishing or successor arm may follow until `--uninstall` exits 0. |
| **failed restoration** — labels are established absent, but restoring or removing files fails | 1 | Prior sidecars remain; some plists may already have been restored or removed. The diagnostic is `restore failed; retained prior sidecars: <error type>: <detail>`. | Stop and preserve the remaining sidecars for human inspection. Copy a sidecar by hand if you need the old plist back; nothing restores it automatically after exit. Do not report a successful arm or completed restoration. |

Retained cleanup prints
`teardown: <night> loaded=…; <deadman> loaded=…; retained plists: …`.
Exit 4 is a deliberate refusal to change files, not a crash or a partial install.
For example, if the selected span closes between the two bootstraps, the
installer finishes loading and verification, then the commit gate reports
`install_span_closed`: if cleanup
establishes both labels absent, it restores the prior files and exits 2; if a
label remains loaded or UNKNOWN, it keeps the plists and sidecars and exits 4.
If restoration itself fails after absence is established, it exits 1 with
the prior sidecars left by that failed restoration.
A bootstrap failure still reports `failed to bootstrap <label>` (for example,
`failed to bootstrap com.joulewise.night.deadman`), and a loaded-job verification
failure reports `launch agent verification failed`; their original exit code
is 3 when restoration succeeds, overridden by 4 when unloading cannot be
established, or by 1 when restoration fails.

The night job uses the local Month/Day/Hour/Minute from `t0`. The dead-man
uses only Hour/Minute from `deadman_epoch(plan)` (§1.2), so its calendar repeats at
that local minute until uninstalled. A firing before completion logs a
stand-down and writes no night record; after `night/courier.sent` it skips.
If delivery is missing after completion, existing chain-alive and courier
checks still govern recovery; the timer grants no authority to interrupt a
live chain. With no delivery record the watchdog span stays closed to agents
through `D + COURIER_LOCK_FRESH_S`, where the lock-fresh allowance is
`300 + max(60, 180, 600) = 900 s = 15 min`; a started but unexited chain
extends it without a clock limit.

The activation's absolute exit boundary is `t0 − 8 minutes` (§0.6),
two minutes after install close. Finish recording and exit before it.
Do not remain resident until `t0`.

### 1.4 Email, then arm

Order is fixed: **after H is committed and pushed, after any prior stub or plan
root is retired, and BEFORE the plan is moved into its discoverable place.**
There is no minimum notice interval beyond that ordering.

Every arm attempt, including the first, runs §1.4a steps 4–6 (`ARM_ATTEMPT=1`, `attempts.json` = `[]`).

Send one newly accepted notice for each actual arm attempt, including each retry of an unchanged plan. One notice never covers several attempts or several plans. Rechecking an uncleared cause is a waiting observation, not a new arm attempt, and needs no repeated email. A **refreshed notice** is a new accepted email describing the current approved candidate, its exact plan fingerprint, the attempt number and the earlier abort, with all existing plan, input and schedule fields filled again. Use the original plan's notice thread when available; a new thread does not cancel an earlier NO. A **fingerprint** here is the lowercase SHA-256 digest of the exact `night_plan.json` bytes that will be published. The full reviewed Git commit remains a separate field. No reply is needed; absence of a reply is not evidence that sending succeeded.
Send Ed the night notice with the activation's mail tool, under its standing
email authority, containing: plan ID; class `DIAGNOSTIC_NO_PACK`; the full H
twice; the handback commit (= H); measurement root, night custody root and runs
root; `t0` local and UTC; `window_max_s` = 9000; the emitted wrapper's digest
and its sidecar path (§1.1a), and the tracked chain's digest the wrapper pins;
the two desk inputs' paths and digests from §0.8's paste lines; the courier
deadline and derived dead-man; the exit boundary and completion; the notice-send
open and derived install close; every listed span for the install day, each
boundary as local date/time with UTC offset plus epoch seconds (§1.3); and the cancellation
instruction — **launch needs no action from Ed unless he replies NO**. Record
the actual send acceptance, time, message and thread IDs, and which NO relay is
available. A headless activation that cannot read the thread must say so; it
cannot certify that no reply went unseen. Write that evidence to
`$ATTEMPT_DIR/notice-evidence.txt` before going on, together with the parsed
`notice.json` below. The final publication check requires matching accepted
notice evidence; a nonempty text file alone is insufficient. Recheck owner-authored open `directive` issues immediately before
publication.

#### 1.4a Recover an eligible arm abort

The **magistrate** is the headless lead agent that prepares and installs a night. A **candidate** is a prepared plan file together with its fixed input files. **Publication** moves the plan to the location where the supervisor discovers it. A **scheduled job** is a task registered with launchd, macOS's task scheduler. An **arm attempt** is one attempt to publish an approved candidate and install its two scheduled jobs. A **retry** repeats that preparation and installation after a recorded arm abort; it never repeats a measurement that started. A **cold gate** is an independent adjudication by a fresh review session. D-180 clause 2 permits the four causes below to be retried without a new cold gate, after the cause has cleared and a fresh notice email has been accepted. The **plan class** is the plan's `receipt_class` value, which selects its measurement or rehearsal path; it stays the same. **Pre-registration** is the scientific protocol fixed before data collection. Ed's NO still overrides. Every physics, evidence and pre-registration requirement still applies.

The **watchdog** is the supervisor that starts and stops magistrate sessions around measurement windows. The **night gate** checks prerequisites before measurements; its **receipt** records the decision and observations. The **driver** is the program that runs that check, launches the measurement chain and arranges result delivery by the **courier**. A **ledger** is the capture-history record; **custody** means retaining the files that establish what ran and what it produced. A **measurement pack** is the fixed collection of experiment instructions and inputs required by a pack-class plan. A **reviewed head**, written H, is the full Git commit identifier of the reviewed code and instructions. A **fingerprint** is the lowercase SHA-256 digest of exact file bytes. A **binding** is a recorded equality tying a plan to its file bytes, head or other fixed input; a **pin** is the expected value in that equality. A **sidecar** is a companion file, such as a stored fingerprint or previous job-file bytes. An **API** is a programmatic service interface, such as the mail-send operation. A **committed installation** means both jobs were loaded, verified and accepted by the installer's final time check; this is separate from recording a Git commit. **Noncommit evidence** positively establishes that this installation did not reach that state. A missing response does not establish noncommit.

The **arm-time census** is the process inventory before publication. The **plan span** is the agent-free interval beginning eight minutes before `t0`, the plan's scheduled measurement start, and ending under the existing chain and courier completion rules. Permission to retry an arm abort does not excuse a process inside that span. `production_census` uses the night gate's raw process check. `handoff_census` checks departure of owned processes only, and `_is_interactive_claude` recognizes command shape only; neither proves the arm or plan-span census clean. A172 changes none of them.

A **zero-capture refusal** is a final night-gate refusal on machine state: one of the five refusal codes that describe the machine rather than the plan (an agent process present, not quiet because of load, power, thermal state, one busy process or a `corecaptured` respawn loop, bind window expired, screensaver guard, or boot clock). The driver's result and receipt must agree, and the result must have null chain fields. The watchdog also checks that no `*.consumed.json` marker exists under the custody root (or a calibration chain's absolute `RUNS_ROOT`), and that no capture file exists under that root's `instrument_validation` directory or, for an evidence night, under `night/evidence`, with `night/evidence_envelopes.jsonl` absent or empty. `courier.sent` records completed delivery, but the courier and driver may still be running. While such a refusal is delivered but not yet released, and only from eight minutes before `t0` until `t0` plus the plan's `window_max_s` plus the five-minute courier deadline, the watchdog checks the agent census and a separate `run_night.py` driver probe on each **tick** (one pass of its periodic check; launchd starts one every 300 seconds, the watchdog job's `StartInterval`). Both probes must be empty on the same tick before the watchdog latches an early release in `state.json`. The driver probe exists only for this early release; after the interval ends, or once the release is latched, no driver probe runs. The release is one-way: the magistrate the watchdog then starts is itself an agent-census match, so a later non-empty census does not restore the hold. The cost is then delivery, harvest (inspection and preservation of the night's records), cleanup and preparation of a fresh plan, not the unused window. For a calibration chain, the driver creates `chain.started` before launching the chain; the chain opens its ledger session during reservation, and no `*.consumed.json` marker is guaranteed to precede that append. The shared disk scan therefore also checks calibration-ledger rows bound to the predecessor plan. The **successor** is that fresh plan: it needs a new identity and **notice** (the email that announces a plan before it is armed), at least 60 seconds after the refusal's final write, installation before its own cutoff, and the usual **owner veto** (a NO reply on the notice email thread) and checks at its own scheduled start. The current next-start planner puts that start at least 40 minutes ahead of preparation, so the 20-minute recovery target is not a guarantee of a new measurement within 20 minutes. Registration and class refusals, or any night whose chain started, keep the full plan-span hold and cold-gate review.

A **listed install span** is a local-time interval from `run_night.INSTALL_SPANS`,
resolved for its local date; an **epoch second** counts from 1970-01-01 00:00 UTC.
`install_close_epoch(plan)` is the exclusive install cutoff, `t0 − ten minutes (the eight-minute REQUEST lead plus INSTALL_CLOSE_MARGIN_S = 2 × 60 s)`;
`PLAN_MAX_AGE_S` is the night gate's 36-hour plan-age limit. A **dead-man** is
the scheduled recovery job after planned completion. A **plist** is a launchd
job file; **UNKNOWN** means a query cannot establish whether a job is loaded.
A **stub** is a rehearsal chain without scientific acquisition. `$STAGE` is the
existing staging directory outside plan discovery. **Unpublication** removes
only this activation's plan from discovery after documented successful cleanup.

<!-- BEGIN ARM-RETRY-POLICY v1 -->

D-180 clause 2; A172 rulings R1–R3 and fix-round-1 R1–R4 (2026-09-15). Exact arm-event IDs are labels for recorded observations, not receipt codes.

| Retry cause | Meaning and required clearance |
|---|---|
| `arm_idle_interactive` | Only an otherwise idle interactive agent session blocked the arm-time census. Its complete descendant process tree must establish no test, measurement or capture work; unknown activity is not idle. Repeat the unchanged census after the session closes; never signal a foreign process. A173 alone owns any future stub exemption. |
| `arm_notice_mismatch` | The notice fingerprint or reviewed head differs from the approved candidate. Recheck preserved candidate bytes and all fixed inputs, then send a new notice. Changed science, custody or unexplained candidate bytes are evidence drift, not a notice-only fault. |
| `arm_watchdog_uncertain` | A watchdog tick (one supervisor evaluation) returned CLOCK_UNCERTAIN (wall and elapsed clocks disagree) or NETWORK_UNCERTAIN (the remote stop check is inconclusive). Let the watchdog clear its hold: two sane clock samples, or a successful network positive control with the stop reference absent. Never clear its state by hand. |
| `arm_transport` | A named mail/API/network/process-transport operation failed before publication, or installation transport failed with positive noncommit and completed cleanup evidence. A bare nonzero exit or lost response is insufficient. Restore transport and obtain accepted notice delivery; after publication require uninstall exit 0, preserved matching bytes and completed unpublication. Committed, retained, unknown or failed-restoration outcomes stop. |

**Gate and driver refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `night_refused_agent_present` | Production census refusal, including a receipt at t0; never an idle arm event. Zero-capture successor route per D-182. |
| `night_refused_not_quiet` | One-shot load refusal for v2, a terminal power/thermal predicate failure, or one named non-observer process at or above 0.5 busy cores over a single 30 s observation at t0 or at the arm check (registration v3; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). Also: more than two launchd spawns of corecaptured (the Wi-Fi log-capture helper) in the last 10 min at t0, detection only, or new spawns persisting 180 s after the arm check's one licensed Wi-Fi cycle (cold ruling 16 Q2, 2026-09-23). The detail names the process, its pid and its share, and the receipt's C3 row carries top_consumers_at_decision. For v4, load is diagnostic and the CPU cutoff is a sealed plan parameter with a named ruling. Zero-capture successor route per D-182. |
| `night_refused_battery_float` | Battery-float predicate failed on a successfully observed reading (ExternalConnected/IsCharging/|InstantAmperage| ≤ 200 mA, directive #421); never waived. Zero-capture successor route per D-182. |
| `night_refused_bind_expired` | Bind window expired with every sample recorded. Load is diagnostic; the CPU cutoff is a sealed plan parameter. Zero-capture successor route per D-182. |
| `night_refused_hid_idle` | Screensaver-configuration guard failed; this is not a live inactivity measurement. Zero-capture successor route per D-182. |
| `night_refused_boot_clock` | Measurement boot/clock guard failed; not a watchdog uncertainty tick. Zero-capture successor route per D-182. |
| `night_refused_registration` | The registration digest is not in the ruled table, or its bound chain-source digest differs from the measured source. |
| `night_window_expired` | Measurement window expired. |
| `night_plan_stale` | Plan age, pinned head, or a clean measurement clone failed; not a stale notice. |
| `measurement_root_outside_custody` | A plan authored at/after 1790340000 whose resolved measurement_root is not strictly inside /Users/edr/night-custody/measurement (acceptance ruling v2.1 R16). Re-author the plan; never a retry cause. |
| `night_plan_malformed` | Plan structure or fields failed their contract. |
| `night_chain_digest_mismatch` | Executable chain bytes differ from their fixed fingerprint. |
| `launch_go_receipt_missing` | Required measurement-pack launch authorization is absent. |
| `launch_go_receipt_invalid` | Required measurement-pack launch authorization is invalid. |
| `night_refused_class_unbuilt` | This gate cannot execute the requested plan class. |
| `night_receipt_class_invalid` | Receipt class/condition contract is invalid. |
| `night_probe_error` | An observation failed; missing evidence grants no permission. |
| `night_aborted_agent_present` | An agent appeared while the chain ran. |
| `night_chain_already_started` | The once-only chain-start record exists. |
| `night_chain_alive` | The existing chain has not been proved ended. |
| `night_chain_launch_failed` | Launch failed after the once-only start claim; not pre-arm transport. |
| `night_courier_running` | The result-delivery process is still running. |
| `night_courier_unavailable` | The driver's delivery executable is unavailable; not a failed notice send. |
| `night_plan_overruns_deadman` | Completion/dead-man schedule was refused; retained even if normally unreachable. |
| `night_record_exists` | A write-once night record proves invocation already occurred. |
| `night_calibration_refused` | The chain's calibration ledger refused (custody timeout, strict pre-reserve, or invalid custody); the document names the exact code; never an auto-retry cause. |
| `night_window_exceeded` | The chain ran past the exclusive window end and was terminated by the driver; reservation or capture intent may have been written and the session may need desk recovery; never an auto-retry cause. |
| `non_observer_process_busy` | Two CONSECUTIVE envelopes were excluded because one non-observer process held at least 30 busy-core-seconds inside each (registration v3's per-envelope integral; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). The chain ends about 31 minutes after t0 with a typed refusal naming the process, its pid and its core-seconds. This is a machine-state abort AFTER capture, so D-182's zero-capture route does not apply by itself; Ed's 2026-09-23 addendum to D-182 licenses ONE new-plan successor when fewer than minimum_retained envelopes were captured (installed by lane QPE01-ABORT-SUCCESSOR-01; until that lane lands the chain ends with no successor); the captured envelopes stay in the archive. One such envelope followed by a clean one never aborts; never an auto-retry cause. |

**Installer §1.3 refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `install_span_closed` | The selected transaction ended; never switch spans mid-install or bypass the plan cutoff. |
| `install_outside_span` | Wait for an allowed span before the cutoff; scheduling wait is not a fifth retry cause. |
| `plan_t0_in_the_past` | Author a future plan through ordinary planning. |
| `night_agent_already_loaded` | A loaded or UNKNOWN job blocks admission; follow harvest/uninstall and human resolution. |
| `plan_outside_custody_root` | Wrong published location; the existing installation rule still applies. |
| `night_plan_malformed` | Invalid plan fields; not a notice-only fault. |
| `plan_schedule_unrepresentable` | The schedule cannot be represented; no new duration ceiling is implied. |
| `install_spans_unresolvable_on_day` | Local-date spans fail resolution; never repair or drop them silently. |
| `plan_t0_not_minute_aligned` | t0 must name a whole minute. |
| `plan_t0_ambiguous_local_time` | t0's local minute occurs twice; choose an unambiguous minute. |
| `retained prior plist: <path>; re-run --uninstall` | A saved previous job file remains; follow the existing human-resolution/uninstall path. |
| `unsupported plist destination: <path>` | The job-file destination is not a regular file; resolve it under the existing path. |
| `--render-only directory must differ from launch_dir` | Use a separate directory for rendered job files. |
| `probe receipt launch_context differs from install: <label>` | The installed night or dead-man job differs from the verified probe rendering; re-run the probe before installing. |

**Other explicit refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `HOLD_CENSUS` | A supervisor census hold alone does not establish the narrowly evidenced idle arm cause. |
| `slot_refused` | A measurement slot refused; cure the finding before any further night. |

Unknown or mixed causes and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path; receipt refusals remain ineligible for same-plan retries. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.

R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.

D-182: binding observations inside the window are not retries. A zero-capture machine-state refusal may license ONE new-plan successor after courier delivery. A successor is a fresh plan with its own id and SHA-256 digest. The evidence-night successor check reads the predecessor (the refused plan), the shared disk facts (chain start, reservation markers, capture entries and envelope index), and the courier.sent delivery marker with message id. run_night.py creates chain.started before starting the chain (lines 536 and 3170); a calibration ledger session is appended only inside that chain, so absent chain.started also proves no ledger session. A bare C5 receipt row supplies none of these disk facts. The successor route also requires the driver's receipt shape with exactly one C5 row; early release keeps the receipt's veto-only role. The check requires the watchdog's early-release latch, at least 60 s since result.ended_epoch_s, and an unspent successor claim; a claim is the create-once file under night-custody/successor-claims that binds the predecessor to the successor id and digest. Real publish-install creates that claim immediately before publication; a rehearsal does not. The real launchctl must be spelled launchctl; any other spelling that resolves to it is refused, never treated as a rehearsal. A predecessor whose plan id cannot name a claim file fails the successor check. The claim binds only until the predecessor's completion time. Re-preparing with changed bytes after failed publication gives up the successor for the rest of that span. Removing released predecessor custody during its span is an operator action that forfeits the successor bound. The candidate still needs a fresh accepted notice, its own future install close, and no observed NO on any notice thread. Never re-arm the predecessor or treat this as a same-candidate retry. Direct install_night_agent.sh performs no successor check; a follow-up lane owns that route.

Every actual attempt sends a newly accepted notice and repeats the existing notice-to-publication lead: accepted email before publication, with no additional minimum interval. A notice is stale if its SHA-256 fingerprint (digest of the exact plan bytes) or reviewed head differs, a newer abort or NO exists, or it belongs to an earlier attempt. A new thread never clears an earlier NO. Waiting observations send no repeated email. Preserve each attempt in `$STAGE/arm-attempts/NNNNNN/` (a positive ordinal padded to at least six digits, without a count limit), created exclusively; never overwrite prior notice, candidate or failure evidence.

`prerequisites_clear` covers census, watchdog, science, custody, no invocation and authorized observable stop/directive checks; `veto_clear` covers directive issues (`gh issue list --label directive`), `standdown.request`/STOP and any NO relayed into a readable channel. Record an unreadable notice thread as a limitation in the attempt directory; it is not a stop and neither clearance boolean requires reading it. Preserve every observed NO; each stops publication.

<!-- END ARM-RETRY-POLICY v1 -->

**Two window codes, two different instants.** They sit next to each other in
the table above and mean opposite things.

- `night_window_expired` is a GATE refusal, decided BEFORE anything runs: at
  the moment the driver evaluated its conditions, the clock was already
  outside `[t0, t0 + window_max_s]`, so no chain was started and no ledger
  session was opened. Nothing was acquired and nothing needs recovery.
- `night_window_exceeded` is a DRIVER termination, decided AFTER the chain
  ran: the chain was still alive `WINDOW_SHUTDOWN_GRACE_S` (300 s) past the
  window end, so the driver terminated its whole process group. The
  reservation exists, capture intent may have been written, and the ledger
  session may still be open — this one can need desk recovery, which is why
  A172 keeps it on the cold-gate path with no auto-retry.

**Reading the two records a wall-clock termination leaves.** Both sit in the
night directory beside `result.json` and both are listed in the result's
artifact inventory.

- `chain.deadline` is always written when the deadline fires:
  `{"pgid", "deadline_epoch_s", "fired_epoch_s", "proven"}`. `pgid` is the
  chain's process-group identifier, `deadline_epoch_s` is the instant the
  driver computed once from its wall clock (`t0 + window_max_s + 300`),
  `fired_epoch_s` is when the termination sequence finished, and `proven` is
  the group proof: `true` means the chain was reaped AND a `pgrep -g` census
  of its group came back empty.
- `chain.unkilled` appears only when `proven` is false:
  `{"pgid", "epoch_s", "group_census"}`, where `group_census` is the lines the
  last census listed — the processes that were still in the group, or a
  `census_failed:` / `census_exit_N:` line if the census itself could not
  answer. In that state the night reports `night_chain_alive` with
  `evidence.trigger` = `night_window_exceeded`, the courier is suppressed, and
  the dead-man re-derives the same state at `t0 + window_max_s + 3900 s`.
  Treat surviving processes as a desk matter: identify them from
  `group_census` before arming anything else.

1. **Record and classify before retrying.** Preserve the command/tool, full
   result, stage reached, candidate digest and original attempt identity.
   Call `joulewise.arm_retry.classify_abort(cause)` on the exact recorded arm
   event after checking all refusal evidence. Only `retry` permits this path.
   A raw `HOLD_CENSUS` is insufficient; an idle-only cause needs its full-tree
   evidence. Any invocation, nonempty/malformed receipt, chain/capture activity
   or scientific refusal stops. An empty installer-created `night/` directory
   alone does not establish invocation. Never run a measurement or probe to
   classify an abort.
2. **Resolve publication first.** Before publication, verify the target is
   absent and no installer ran. After publication follow §1.4's uninstall →
   preserve → compare → unpublish order, requiring uninstall exit 0 and
   positive noncommit evidence. Installer exit 0 is committed even if its
   output was lost; a timeout is not noncommit evidence. Retained/UNKNOWN jobs,
   failed restoration or missing completion proof stop for human resolution.
   Restore only this activation's exact saved candidate to `$STAGED_PLAN`,
   exclusively if absent: `cp -n "$ATTEMPT_DIR/plan.json" "$STAGED_PLAN"`, then
   `cmp "$ATTEMPT_DIR/plan.json" "$STAGED_PLAN"` must exit 0. Never regenerate
   authoring timestamps, edit inputs or erase evidence to refresh a budget.
3. **Recheck the unchanged prerequisites.** Repeat §0.1's reviewed-head check,
   §0.3's epoch and pre-registration checks, §0.4's ledger authentication and
   head-equals-pin check, §0.5's committed pre-registration checks, §0.6's
   unchanged census, §0.7's directive/NO and ownership checks, and §0.8's
   clean-tree and fixed desk-input checks. Verify the wrapper under §1.1b
   step 4; do not rerun §0.2 or regenerate the desk inputs.
   The watchdog clears its own uncertain state. Wait
   only for the actual bound or uncleared condition; no new delay follows a
   successful harvest. A wait observation is not an attempt and sends no mail.
4. **Prepare each attempt before sending.** Set `ARM_ATTEMPT` to the next
   positive ordinal (1 initially), then exclusively create
   `$STAGE/arm-attempts/NNNNNN/` and export it as `ATTEMPT_DIR`. Preserve
   `$STAGED_PLAN` there as `plan.json` before sending, and save `notice-body.txt`.
   Include the exact SHA-256, full H, class, attempt number and earlier abort
   in the notice with all §1.4 fields. Send a new email; record actual accepted
   time and message/thread IDs, never intended or presumed acceptance. Check
   authorized observable channels: directive issues, `standdown.request`/STOP
   and any NO relayed into a readable channel, including earlier notices.
   Record an unreadable notice thread as a limitation in the attempt directory;
   it is not a stop. Preserve every observed NO; each stops publication.
5. **Retain observations for the executable check.** In the new directory
   write `attempts.json`, the chronological array of this candidate's prior
   abort records (empty for an initial arm). Each record has `attempt`,
   `attempt_epoch_s` (time the arm attempt began), `abort_epoch_s`, the exact
   `cause`, `receipt_class`, `plan_sha256`, `message_id` (empty if unsent), and
   `outcome`: `not_published` or `restored_unpublished`, the latter only after
   the cleanup proof in step 2. Keep the underlying outcomes in their original
   attempt directories; never overwrite them. This is an evidence snapshot,
   not a persistent retry-state file or cross-activation ownership grant.
   Write `notice.json` with `accepted: true` only after confirmed delivery,
   `message_id`, `thread_id`, `sent_epoch_s`, `attempt`, `plan_id`,
   `receipt_class`, `measurement_head` (= reviewed H), and `plan_sha256`.
   Immediately before publication refresh its observation fields from the
   retained actual directive/stop, census, watchdog and desk-check results:
   `prerequisites_clear` and `veto_clear` are literal booleans covering those
   authorized observable channels, not a requirement to read an inaccessible
   notice thread. `blocking_causes` lists all concurrent refusals,
   `latest_no_epoch_s` is null only if no observed standing NO exists, and
   `latest_abort_epoch_s` is copied byte-for-byte from
   `attempts[-1].abort_epoch_s`, never re-typed, rounded or truncated (null
   initially). Never fill clearance from the desired outcome. Preserve
   the original send evidence and the fresh observation outputs separately.
6. **Execute the final check below.** It rereads candidate bytes, the saved
   pre-notice snapshot and the current notice; derives bounds from the live
   schedule; then calls `retry_allowed`. Proceed only if `allowed` is true.
   A false result leaves the plan unpublished; clear only the named eligible
   cause, or use ordinary successor planning when the time budget is spent.
   A new plan never erases a scientific refusal. A successor activation uses
   R2's fresh same-class plan, leaving predecessor published directories alone.
7. **Record each outcome.** Preserve `outcome.json`, all failure/cleanup codes,
   actual attempt time, digest, accepted notice locator and evidence inventory
   in that attempt directory. `outcome.json` carries exactly the step-5 record fields for this attempt; attempt N+1's `attempts.json` is the unmodified concatenation of attempts 1..N `outcome.json`.
   The installer still checks its cutoff through
   commit. No measurement retry, new daemon or live validation is implied.

For the exclusive directory and snapshot step (before sending):

```zsh
set -euo pipefail
: "${ARM_ATTEMPT:?}" "${STAGE:?}" "${STAGED_PLAN:?}"
export ARM_ATTEMPT
ATTEMPT_DIR="$STAGE/arm-attempts/$(printf '%06d' "$ARM_ATTEMPT")"
export ATTEMPT_DIR
mkdir -p "$STAGE/arm-attempts"
mkdir "$ATTEMPT_DIR"                 # existing attempt evidence is a stop
cp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
```

#### The arm itself, in one foreground block

These are the commands, adapted from the prior night's arm runbook, record 12,
`docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`,
§"Block B" — the only executed template this project has for a real install.
Updated 2026-09-15 (INSTALL-WINDOWS-MULTI-01): calendar fields now come
from the plan schedule; the earlier adaptations also remain: the plan assertions are
this night's (`DIAGNOSTIC_NO_PACK`, `window_max_s = 9000`, no pack block, and a
`registration_path` equal to `night_gate.D166_REGISTRATION_PATH`, the fixed
D-166 registration path required by the night gate for this receipt class,
whose file must hash to `night_gate.D166_REGISTRATION_SHA256`, the gate's
expected SHA-256 fingerprint of those bytes), and the
chain re-check is this lane's wrapper `--verify` of §1.1b step 4 rather than
that runbook's G2-a runsheet render.

Before installation, exercise custody access through a temporary **LaunchAgent**
(a macOS launchd job file), using the published plan and the pinned checkout:

```zsh
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
# Only after exit 0, install through the ordinary arm sequence below.
```

A terminal inherits the owner's file-access consent; a launchd job does not
inherit the terminal's consent. The probe therefore runs the production
interpreter → chain → reservation path, using the real ledger and arguments.
Its **verify-only** mode performs enforcing custody checks and stops before
any session append, settle, or capture. It creates no `chain.started` record.
A **receipt** is its non-authorizing record at
`<plan_dir>/night_probe_receipt.json`. It binds the plan and wrapper bytes,
measurement commit, ledger head (the digest of the latest record), ledger
bytes, every reservation input file via `input_digests` (including the night
plan, calibration plan, identity epoch and T1 bindings), relevant code
fingerprints, and both interpreters' paths, versions and binary SHA-256
fingerprints. The input list comes from the chain's actual expanded reservation
arguments through the driver's production environment builder; for a
calibration plan, render-only prints these input fingerprints. For an evidence
plan (`NIGHT_PAYLOAD_KIND=quiet_predicate_evidence`), render-only never runs
the chain: it authenticates the wrapper statically (sidecar, sealed manifest,
chain-bound registration, the sealed published plan path) and prints one
advisory JSON line — the wrapper's SHA-256 and digests of the supplied plan
bytes and the sealed manifest — that nothing downstream consumes; the launchd
probe is the step that executes the chain verify-only. Installation recomputes the bindings and accepts
only an `ok` receipt whose finish time and file modification time are less
than six hours old; the finish time may be at most 60 s ahead of the clock.
It also refuses the install unless the receipt's single measured custody pass
leaves the capture writer room for its own passes —
`custody_elapsed_s × WRITER_CUSTODY_PASSES × 1.5 ≤ custody_budget_s`, which is
T ≤ 26.67 s at today's constant of 3 (§1.2) — and unless `observations` is
greater than zero whenever the ledger already holds finalized observations. The temporary job has a 600 s
limit (`--probe-timeout-s`) covering input binding reads and chain execution,
with the reached phase recorded on timeout. Its supervised process group
(the worker and its child processes) is terminated and checked for survivors;
then it is booted out (unloaded), and must pass a process
census (check for surviving processes) before the installer returns success.
A missing/failed/stale/mismatched receipt refuses installation with exit 2.
Rendering with `--render-only DIR` includes the probe job file; it starts no job.

The driver first writes `night_probe_receipt.pending.json`; the installer
publishes `night_probe_receipt.json` only after unloading and process cleanup
are proven. An interrupted or failed cleanup leaves no installable receipt.
Treat every Homebrew Python replacement as invalidating the successful launchd access probe; verify again.
A replacement changes the executable fingerprint bound by the receipt; this
is a conservative arm precondition, not a claim that every upgrade resets
macOS consent. After answering a consent dialog, rerun successfully without
further interaction before installation.

Worked example, 2026-09-16: the 09:45 reservation read 190 governed files,
3.33 GB under 38 iCloud custody locators, and waited 11 h 07 m until 20:52.
No captures or verdict resulted. The root-cause record supports consent as
the leading explanation, while cloud materialization (making remote file
bytes locally available) remains an alternative. The reservation and each
capture writer now share a whole-pass custody budget of 120 s, clipped ten
seconds before the exclusive window end. Exhaustion produces the typed
(machine-readable) `calibration_ledger_custody_timeout` refusal and preserves
the night. The courier reads `calibration-refusal.json`, every numbered
refusal listed by the result, and any later refusal siblings; it reports the
code, budget, elapsed time, and whether a session already existed. No retry
or ledger repair is authorized by this receipt or refusal.

At 02:56 PDT on 2026-09-11, the driver crashed before any gate because
`python3` found through PATH selected macOS Python 3.9.6, which cannot import
`datetime.UTC`. Each LaunchAgent now names an absolute Python interpreter
(the executable running the driver). The installer flag `--python "$PY"`
pins that path to the project interpreter defined in §0.2. Install and
`--render-only DIR` (render the two night job files and access-probe file into `DIR` without installing
anything) default to `<measurement_root>/.venv/bin/python` when
`--python` is omitted. Even a stub checkout needs that venv or an absolute
path to a Python whose version is at least `MIN_PYTHON` in `scripts/run_night.py`
(currently 3.11) and whose driver preflight exits 0 from the stub checkout.
The chain's interpreter remains `<measurement_root>/.venv/bin/python`,
independently of this driver pin.

`--render-only DIR --plan "$STAGED_PLAN"` validates the staged plan before
publication, including the same t0, install-close and install-span checks as
a real install. The night and dead-man plists name the future
`<custody_root>/night_plan.json`, so the validated agent arguments are the
ones that will run after publication (the third, probe plist is rendered from
the plan path as supplied — its `--plan` argument, pending-receipt path and
probe directory all derive from that path — so a staged render's probe file
differs from the published one in those derived fields). It never calls launchctl. This also
implements D-175's REHEARSAL_STUB procedure: stage outside the watchdog's
glob, validate with `--render-only` from the pinned checkout, then publish.
The atomic `os.replace` remains the single irreversible publication step;
a real install still requires the published custody path.

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
: "${ATTEMPT_DIR:?}" "${ARM_ATTEMPT:?}"
cd "$MEASUREMENT_ROOT"

# 1. The pins still hold, and the notice really went out.
test -s "$ATTEMPT_DIR/notice-evidence.txt"
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
cmp "$STAGED_PLAN" "$ATTEMPT_DIR/plan.json"
"$PY" -B - <<'PY'
import hashlib, json, os, time
from pathlib import Path
from joulewise import night_gate
from joulewise.night_gate import NightPlan
from scripts.run_night import install_close_epoch
plan = NightPlan.from_mapping(json.loads(Path(os.environ['STAGED_PLAN']).read_text()))
assert plan.repo_head == plan.measurement_head == os.environ['H']
assert plan.measurement_root == os.environ['MEASUREMENT_ROOT']
assert plan.custody_root == os.environ['NIGHT_ROOT']
assert plan.receipt_class == 'DIAGNOSTIC_NO_PACK'
assert plan.window_max_s == 9000
assert plan.chain_path == os.environ['NIGHT_ROOT'] + '/chain.zsh'
assert plan.chain_sha256_path == plan.chain_path + '.sha256'
assert plan.registration_path == night_gate.D166_REGISTRATION_PATH
assert hashlib.sha256(
    (Path(os.environ['MEASUREMENT_ROOT']) / night_gate.D166_REGISTRATION_PATH).read_bytes()
).hexdigest() == night_gate.D166_REGISTRATION_SHA256
assert 0 <= time.time() - plan.authored_epoch_s <= 36 * 3600
assert 0 <= plan.t0_epoch_s - plan.authored_epoch_s <= 36 * 3600
assert time.time() < install_close_epoch(plan)     # t0 - 480 - 120 seconds
assert Path(os.environ['STAGE']).stat().st_dev == Path(os.environ['NIGHT_ROOT']).stat().st_dev
print('staged plan checks PASS')
PY

# Validate both future agent plists while the plan is still staged.
scripts/install_night_agent.sh --render-only "$STAGE/rendered-agents" \
  --plan "$STAGED_PLAN" --python "$PY"

# 4. The final arm-time census, immediately before publication (§0.6 step 3b).
# Busy/foreign exit 3 is REHEARSAL_STUB-only; other valid classes are diagnostic.
if "$PY" -B -m joulewise.arm_census --plan "$STAGED_PLAN"; then
  :
else
  rc=$?
  print -u2 "arm census exit $rc; preserve the transcript and stop publication"
  exit "$rc"
fi

# 5. Publication: the one irreversible instant.
"$PY" -B - <<'PY'
import json, os, time
from pathlib import Path
from joulewise.arm_retry import retry_allowed
from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S
from scripts.run_night import install_close_epoch
attempt_dir = Path(os.environ['ATTEMPT_DIR'])
raw = Path(os.environ['STAGED_PLAN']).read_bytes()
plan = NightPlan.from_mapping(json.loads(raw))
attempts = json.loads((attempt_dir / 'attempts.json').read_text())
notice = json.loads((attempt_dir / 'notice.json').read_text())
now = time.time()
if notice['attempt'] != int(os.environ['ARM_ATTEMPT']):
    raise SystemExit('notice belongs to a different attempt')
context = dict(plan_bytes=raw, saved_plan_bytes=(attempt_dir / 'plan.json').read_bytes(),
               reviewed_head=os.environ['H'], install_close_epoch_s=install_close_epoch(plan),
               plan_max_age_s=PLAN_MAX_AGE_S)
decision = retry_allowed(now, context, attempts, notice)
if not decision.allowed:
    raise SystemExit('arm refused: ' + decision.reason)
target = Path(os.environ['NIGHT_ROOT']) / 'night_plan.json'
if target.exists() or target.is_symlink():
    raise SystemExit('publication target already exists')
os.replace(os.environ['STAGED_PLAN'], target)
PY

# 6. Install both agents FROM the clone.
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" \
  --python "$PY"

# 7. Inspect what was actually installed, and baseline the night directory.
launchctl list | grep joulewise
"$PY" -B - <<'PY'
import json, os, plistlib, subprocess
from pathlib import Path
from joulewise.night_gate import NightPlan
from scripts.run_night import schedule
labels = {line.split()[-1] for line in
          subprocess.check_output(['launchctl', 'list'], text=True).splitlines() if line.split()}
assert {'com.joulewise.night', 'com.joulewise.night.deadman'} <= labels
plan = NightPlan.from_mapping(json.loads(
    (Path(os.environ['NIGHT_ROOT']) / 'night_plan.json').read_text()))
expected = schedule(plan)
for label, key in (('com.joulewise.night', 'night_calendar'),
                   ('com.joulewise.night.deadman', 'deadman_calendar')):
    plist = plistlib.loads((Path.home() / 'Library' / 'LaunchAgents' / f'{label}.plist').read_bytes())
    assert plist['StartCalendarInterval'] == expected[key], (label, plist['StartCalendarInterval'])
print('installed calendars match plan: night Month/Day/Hour/Minute; dead-man Hour/Minute only')
night = Path(os.environ['NIGHT_ROOT']) / 'night'
entries = sorted(night.iterdir()) if night.is_dir() else []
print('post-install night/ baseline:', json.dumps(
    [{'name': p.name, 'size': p.lstat().st_size, 'mtime_ns': p.lstat().st_mtime_ns}
     for p in entries], indent=2))
PY
plutil -p ~/Library/LaunchAgents/com.joulewise.night.plist
plutil -p ~/Library/LaunchAgents/com.joulewise.night.deadman.plist
cmp "$NIGHT_ROOT/night_plan.json" "$ATTEMPT_DIR/plan.json"
```

Read both `plutil` dumps against four things and record the answers: each
label's `StartCalendarInterval` against `run_night.py schedule --plan`
(the night: Month/Day/Hour/Minute from `t0`; the daily dead-man: Hour/Minute
only from D), `WorkingDirectory` (the clone), the exact driver, plan and
courier argv, and `RunAtLoad=false`. Keep both dumps and the schedule JSON
in the arm record. The installer derives these fields; pass no `--hour` or
`--minute` inputs. Its parser accepts only `--plan`, `--python`, `--uninstall`,
`--render-only` and `--launchctl-bin`. An unknown flag, including `--help`,
prints usage to stderr and exits 2 before any installation work.

**If any step AFTER publication fails**, run `--uninstall` first and record
its return code. Continue with preserve / compare / unpublish **only if
uninstall exits 0**. Exit 4 means a label is still loaded or UNKNOWN and the
plists were deliberately kept; stop for human resolution. Any other nonzero
exit also stops recovery. The block below gates each command on the preceding
command's success; record every return code:

```zsh
scripts/install_night_agent.sh --plan "$NIGHT_ROOT/night_plan.json" \
  --uninstall &&
test ! -e "$ATTEMPT_DIR/failed-night_plan.json" &&
cp "$NIGHT_ROOT/night_plan.json" "$ATTEMPT_DIR/failed-night_plan.json" &&
cmp "$ATTEMPT_DIR/failed-night_plan.json" "$ATTEMPT_DIR/plan.json" &&
rm "$NIGHT_ROOT/night_plan.json"
```

The `cmp` before the `rm` is the point of keeping this attempt’s `plan.json`: it
proves the bytes that were briefly discoverable are the bytes that were
reviewed, so the failed attempt is documentable rather than merely undone. If
recovery itself fails, record the surviving labels and the discoverable plan
and escalate; never claim nothing was armed.

`--uninstall` verifies both labels after the two bootouts (requests to unload
the jobs). If either remains loaded or UNKNOWN, it exits 4, changes no files,
keeps both plists and any `.prior` sidecars, and prints
`uninstall: still loaded after bootout: <loaded labels>; retained plists: <night plist> <deadman plist>`.
Re-running `--uninstall` is safe and **idempotent**: repeating it does not
undo a successful uninstall, and files remain protected while either label
is loaded or UNKNOWN. Retry after human resolution; only exit 0 opens the
remaining recovery steps. Those steps do not restore old plist bytes:
successful `--uninstall` deletes both the plists and the sidecars. Copy a
sidecar by hand first if you need the old plist back.

### 1.5 Record and exit

Write the arm record and its evidence directory in the authorized linked
bookkeeping worktree, commit, push, and exit before `t0 − 8 min`. No own
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
| `plan_id` | `$PLAN_ID` — `d079-epoch-25g83-derivation-<WINDOW_ID>-<NIGHT_DATE>` (§0.2) |
| `root` | `$MEASUREMENT_ROOT` — the fresh clone of §0.2, `/Users/edr/JouleWise-measurement-<NIGHT_DATE>-derivation-<WINDOW_ID>` |
| `head` | `$H` — the 40-character reviewed head of §0.1 |

The triple's purpose is a fence, not a handover: the prompt forbids Git
operations in the canonical root and forbids MOVING any listed measurement
root, because a post-arm move invalidates the plan's pin and forces a re-arm
(same section). Everything the morning harvest additionally needs is
reconstructed from these three values plus the night root's own contents, and
§2.0 does exactly that. Still write all of it into the arm record as well: the
reconstruction is the successor's floor, not a licence to record less.

#### What the arm record must carry, every night

Also retain each arm-attempt directory, A172 rulings R1–R3, cause and clearance
records, exact plan digest, notice IDs/times, the install-close and plan-age checks actually applied,
and any noncommit/uninstall/byte-comparison
proof. These supplement every scientific/input item below.

**Timing evidence update — 2026-09-15, INSTALL-WINDOWS-MULTI-01.** Retain the
schedule JSON and both installed plist dumps with the actual notice-send open,
install close, every listed install-day span, `t0 − 8 min`, `t0`, completion
(the courier deadline) and D, all as local date/time plus epoch seconds.

The arm record is the committed account of the plan and fixed inputs before
capture; record these five items for the equivalence night and every night
on the FAIL route (the three-night derivation after §2.5 returns FAIL).
A SHA-256 digest is a fingerprint of file bytes; a Git blob id identifies
the stored bytes so they can be recovered without the working copy.

| Item | Required evidence |
|---|---|
| 1. Frozen plan and gate registration | `plan_id`, the night's identifier; the SHA-256 of the frozen calibration plan of §0.2 (`$CALIBRATION_PLAN`, the committed capture plan the captures run under, not this night's `night_plan.json`), equal to the wrapper's `PLAN_SHA256` literal; and the plan's `registration_path` verbatim, equal to `night_gate.D166_REGISTRATION_PATH` (the fixed D-166 registration path required by the gate), with that file's SHA-256 inside `$MEASUREMENT_ROOT` (the measurement clone): `dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265` expected. |
| 2. Scientific pre-registration | Repository-relative path `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`; the `shasum -a 256` result from the committed bytes inside `$MEASUREMENT_ROOT` after §0.5's fields are filled; measurement head H (the plan's pinned commit, 40 hexadecimal characters); and the Git blob id printed below. |
| 3. Rule and instructions | The commit id containing the D-102 evening addendum (the written rule the PASS route applies), and the commit id containing the runbook revision followed, with its revision number. |
| 4. Capture inputs | The wrapper chain's SHA-256 (the generated `chain.zsh` file the plan launches); the identity-epoch digest (the `identity-epoch.json` description of the instrument configuration); the T1-bindings digest (the `t1-bindings.json` fixed capture-input bindings); and `EVIDENCE_ROOT_ID` (the registered evidence-root identifier). These are the inputs already required in §0.2, §0.8 and §1.1b. |
| 5. FAIL-route nights 2/3 | Re-record item 2's digest with the words **equal to night 1**, or record **STOP** and do not arm (§3). |
| 6. Battery-float verdict lines (Revision 5 epochs, every window after W1) | Every earlier harvested window's `<session_id>: battery=<status> verdict_sha256=<64 hex> verdict_commit=<40 hex>` line, copied from its harvest notice (§2.2a; A-R5b-1). |

With `$H` set to the 40-hex measurement head, recover item 2's blob id with:

```zsh
git -C "$MEASUREMENT_ROOT" rev-parse "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
```

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
| `<NIGHT_ROOT>/night.log` | The driver's own log: a dead-man line dated before completion is expected evidence if that daily minute occurred after install; after `courier.sent` the dead-man skips. Read this plan's gate verdict line. |
| `<NIGHT_ROOT>/night/result.json` | The verdict, the chain's exit code, and where the receipt or refusal is. Read this first; it directs the rest. |
| `<NIGHT_ROOT>/night/receipt.json` or `refusal.json` | The C1–C5 condition rows, or the refusal reason and detail. C2 is `NOT_APPLICABLE`/`no_pack_by_design` for this class. |
| `<WINDOW_CUSTODY_ROOT>/operator_logs/derivation-chain.log` | The chain's own lifecycle: `session_open kind=derivation slots=12`, `chain_start` (its timestamp minus `t0` is the night's realized Δ, §1.2), `settle_complete`, then twelve `slot_start` lines each answered by exactly one of `slot_end … disposition=valid`, `slot_end … disposition=non-valid` (a normal record, §2.4) or `slot_refused slot=dNN rc=<n>` (the night stopped here, session OPEN), and finally `derivation_night_complete slots=12` — or `slot_unused … reason=window_exhausted` followed by `session_abort`. |
| `<NIGHT_ROOT>/night/chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`, `chain.stderr.log` | Launchd lineage, actual chain termination, and the production census the driver takes at launch and every 30 s. |
| `<NIGHT_ROOT>/night/courier.sent`, `courier.json`, `courier.heartbeat` | Send time and message ID; verify the email separately in Ed's inbox. |
| launchd `.out`/`.err` for both labels | Present or absent, complete bytes, sizes, nanosecond mtimes — compare against the arm-time baseline. |
| `night-results/<plan_id>` branch; `docs/process_traces/night-results/<plan_id>/` within it | The driver's best-effort published copies of night artifacts. Both destinations use the full plan ID, not the civil date; verify the push before relying on them. Local publication checkout: `<custody_root>/results-clone`. |
| `check --session-ids <SESSION_ID>` (§2.2) | The night's session kind, state, terminality, declared and filled slot counts, exclusion counts by mechanism. |
| `configs/calibration/battery_float_verdicts/<SESSION_ID>.json` in `$MEASUREMENT_ROOT` (§2.2a) | The window's battery-float verdict (`pass`, `battery_float_confounded` or `battery_float_evidence_missing`), written by `battery-verdict` and committed with the ledger head pin **before** any slot line, ledger row or evidence file below is read. This committed file is the window verdict. |
| The night's own ledger rows in `$CALIBRATION_LEDGER`, and each capture's `manifest.json` and `instrument_evidence.json` under `$RUNS_ROOT` | The twelve slot outcomes, and — for the captures that are `valid` and whose stored anchor record resolves — the **retained values** the equivalence rule compares (§2.5). Reading these AFTER this night has closed is what the check IS; §2.3 draws the line. |

Preserve the full custody root byte-exact outside watchdog discovery before any
removal, and keep a separate `lstat` inventory of the original with sizes and
`mtime_ns`; a backup's copied timestamps do not substitute for it.

### 2.2 The one mid-campaign query, and what it may not tell you

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --session-ids "$SESSION_ID" \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "$PREREGISTRATION_SHA256"
echo "rc=$?"
```

`$PREREGISTRATION_SHA256` is the registration digest the arm notice pinned
(§0.5). Both registration flags are required for any Revision 5 session (a
session with a finalized row in epoch 25G83/v3): the dry run authenticates each such
session's committed battery-float verdict against that exact registration
digest (§2.2a). Without them it prints the blocker `--preregistration and
--preregistration-sha256 are required` and returns 5; that rc 5 is the flag
blocker, not a fault in the window.

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
the correct mid-campaign answer there. After night two the same query names
only night two, so night one's valid rows are rows of the same epoch owned by
a session the query did not name, and the dry run also prints the addendum A-7
blocker `valid same-epoch observations outside this registration: <n> rows
owned by <session ids> (ruling 46 addendum A-7)`, exactly as `prepare-candidate`
would refuse on them; that too is the correct mid-campaign answer. On the PASS
route nothing is ever prepared, and this code decides nothing.

### 2.2a Record the battery-float verdict before reading any result (Revision 5 windows)

**Why this step exists.** Every Revision 5 capture brackets itself with two
readings of the battery (`raw/battery_float.pre.ioreg` and
`raw/battery_float.post.ioreg`). A window whose readings show the Mac drawing
charge current is excluded and replaced (registration amendment A-R5b). For
that exclusion to be unable to select on results, the verdict must be fixed
**before anyone reads a result**, and it must be impossible to change it
afterwards. So the verdict is computed once, at harvest, from the raw battery
bytes alone, written to one file, and committed in the same commit as the
ledger head pin (the committed file naming the ledger's row count and last row
digest, §2.0). That committed file is the window verdict (decision log
A-R5b-1). Every later tool (`check`, the cadence report and `prepare-candidate`,
through the one function `authenticate_committed_verdict`) recomputes the
verdict from the same raw bytes only to confirm the file, and refuses on any
disagreement. The continuation tool refuses a Revision 5 session outright.

**Custody failure.** When a capture finishes, the writer records a SHA-256
fingerprint of each battery reading's raw bytes inside
`instrument_evidence.json`, and the ledger row records the fingerprint of
`instrument_evidence.json` itself. If any of those fingerprinted files is later
missing or no longer matches its fingerprint, that is a *custody failure*: the
tools compute no verdict, write nothing and refuse, and the one cure is to
restore the bytes byte-exact from the preservation copy §2.1 requires. A
custody failure is never an exclusion: it cannot remove or replace a window.
A reading the writer itself recorded as failed (non-zero exit, timeout, stale
or unparseable bytes that still match their fingerprint) is a verdict,
`battery_float_evidence_missing`, because it is fixed instrument state.

**The order, one block.** Steps (i)–(v) complete before anything in step
(viii) is opened. `night.log`, `night/result.json`, the receipt or refusal and
the launchd files may be read before step (iii), because they hold no
measured value and no slot disposition.

```zsh
cd "$MEASUREMENT_ROOT"
# (i) §2.0 done: the ledger is rebuilt and authenticated at head-equals-pin.
# (ii) Any desk recovery the existing subcommands provide, so the session is
#      terminal. The custody root of an unissued epoch is never moved,
#      relocated or offloaded.
# (iii) Record the verdict. PREREGISTRATION_SHA256 is the digest the arm
#       notice pinned (§0.5).
"$PY" scripts/issue_calibration_acceptance_generation.py battery-verdict \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --repo-root "$MEASUREMENT_ROOT" --session-id "$SESSION_ID" \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "$PREREGISTRATION_SHA256"
echo "rc=$?"
#   rc=0 prints exactly one line: <SESSION_ID>: battery=<pass|confounded|evidence_missing>
#   rc=3 prints REFUSED: <reason>. On "REFUSED: custody failure", restore the
#   named bytes from the byte-exact preservation copy and re-run; do nothing
#   else until it exits 0.
# (iv) One commit: the ledger head pin and the verdict, together.
git add configs/calibration/calibration_ledger_head.json \
  "configs/calibration/battery_float_verdicts/$SESSION_ID.json"
git commit -m "Harvest $SESSION_ID: ledger head pin and battery-float verdict"
# (v) The harvest notice carries one line for this window and for every
#     earlier harvested window of the epoch (the next arm notice repeats them):
print -r -- "$SESSION_ID: battery=<pass|confounded|evidence_missing> verdict_sha256=$(shasum -a 256 "configs/calibration/battery_float_verdicts/$SESSION_ID.json" | cut -d' ' -f1) verdict_commit=$(git rev-parse HEAD)"
# (vi) The cadence report (refuses without the committed verdict).
"$PY" scripts/calibration_cadence_report.py \
  --window "W=$RUNS_ROOT/instrument_validation/$SESSION_ID-*" \
  --calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --session "W=$SESSION_ID" \
  --preregistration-sha256 "$PREREGISTRATION_SHA256"
# (vii) The count-only dry run of §2.2 (blocks without the committed verdict).
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --session-ids "$SESSION_ID" \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "$PREREGISTRATION_SHA256"
# (viii) Only now: the §2.1 reads of derivation-chain.log slot lines, the
#        night's ledger rows and the capture evidence files.
```

The verdict file counts only if exactly one commit in the checkout's history
touches its path and that commit added it: a file that is later edited,
deleted or deleted and re-added is treated as no verdict, and every consumer
refuses. The reading order above is procedure; the guarantee is the custody
rule, which makes every excluding verdict a function of bytes fingerprinted
before the slot was finalized.

### 2.3 When a value may be read, and when it may not

The boundary moved with directive issue 316, and it is a boundary in TIME, not
a prohibition on looking at all. On a Revision 5 window, the battery-float
verdict is recorded and committed (§2.2a) before any slot line, ledger row or
evidence file of the session is read. Three rules, in force in this order:

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

**Revision 5 route for epoch 25G83:** Registration Revision 5 takes no equivalence look for this epoch. `epoch_equivalence_check` and `issue_epoch_continuation` refuse its sessions. W1 and W2 follow Revision 5's derivation procedure instead. The equivalence-night PASS route in §2.4–§2.5 and its §4 continuation text below remain as the historical record.

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
--reason window_exhausted --custody-budget-s "$CUSTODY_BUDGET_S"`, and exits
0. That flag bounds the one custody read the abort makes — the next slot's
state — at 120 s (§1.2 "What the end-of-window abort costs in the worst
case"). An aborted session IS terminal, and its finalized observations remain
in the prior set.
`session-refusal` is the recovery tool's subcommand that reads an aborted
session and prints its abort as a **refusal code** — the machine-readable name
the tool prints in place of a prose reason, the kind §5's "Refusal code"
column carries. Which name it prints for a `window_exhausted` abort depends on
the copy of `scripts/recover_calibration_ledger.py` you run, and §2.4's
`cd "$MEASUREMENT_ROOT"` runs the measurement clone's copy at `H`, so ask that
copy by full path:
`grep -c window_exhausted "$MEASUREMENT_ROOT/scripts/recover_calibration_ledger.py"`.
A count of `0` — every head before the mapping landed, including the night
armed at `f90cb8c0` — prints `calibration_session_not_open`, which it
also prints for a session never aborted; read the reason from the
`slot_unused … reason=window_exhausted` line above instead. A count of `1` or
more whose matched line is the entry `"window_exhausted": RefusalCode.…`
prints `calibration_window_exhausted`. Either way the session is terminal.

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

Before applying the rule, the magistrate must re-hash the committed
pre-registration at H (the arm record's pinned measurement commit) with
`git -C "$MEASUREMENT_ROOT" show "${H}:configs/calibration/preregistration_d079_epoch_25g83_rev1.md" | shasum -a 256` (braced `${H}`: zsh reads an unbraced dollar-H followed by a colon as a history-style modifier and eats the colon, so git would hash nothing),
require equality with the arm record's SHA-256 digest (the fingerprint of
those committed bytes), and quote that digest in the D-102 continuation
addendum on PASS.

**The desk tool that applies this rule.** `scripts/epoch_equivalence_check.py`
reads the terminal session from the ledger, retains exactly the rows defined
above (it re-reads each retained capture's `instrument_evidence.json` and
refuses if its lexeme differs from the ledger row's), reads the operatives
from the validator registry and refuses if the artifact disagrees, and prints
the constants table, one line per declared slot, m, the two comparisons with
their operands, and the verdict line. It judges only against the r6 generation
named above; pointing it at any other acceptance refuses. It also refuses, with
exit 3 and nothing written, any session with a finalized row in epoch 25G83/v3:
registration Revision 5 says the equivalence look is not taken for that epoch,
so there is no legitimate run on such a session, and refusing before any
capture is read keeps a B value from being printed before its battery-float
verdict exists (cold ruling BFG-D-PARSER-ESC-01 §5.1). It writes one JSON
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
to judge (the session is not terminal, is not derivation-kind, is a Revision 5
session, or the envelope did not authenticate) and wrote nothing. Run it twice — once from the clone,
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
   Before arming night 2 or 3, re-hash the committed pre-registration at that
   night's H (the plan's measurement commit) at the desk using §0.5 and
   record its SHA-256 digest (the fingerprint of those bytes) as **equal to
   night 1** in §1.5's table; if it differs, STOP, do not arm, file the
   discrepancy for Ed's ruling, and never substitute a new pin (a replacement
   expected digest).
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
  --preregistration-sha256 "$PREREGISTRATION_SHA256" \
  --session-ids "<S1>" --session-ids "<S2>" --session-ids "<S3>"
echo "rc=$?"
```

Expect **rc 0** and `registration admissible for prepare-candidate: yes`. An
rc 5 prints its blockers: a ledger refusal (for example an uncommitted head
pin); a non-terminal session; pending/unresolved rows in the prior-set prefix;
a session's battery-float verdict missing or uncommitted (named or not: every
computed window of the epoch must carry an authentic committed verdict); a
battery-float verdict that cannot be re-established from the raw battery
bytes; an excluded window that is not declared, a declared window that is not
excluded, or more than one excluded window; or valid rows of the same epoch
owned by a session the command did not name (addendum A-7). Clear the named
blocker at the desk — do not capture more to make it go away.

**The replacement route.** Under amendment A-R5b a window whose committed
battery-float verdict is not `pass` (`battery_float_confounded`: the Mac drew
charge current; `battery_float_evidence_missing`: the readings cannot be
judged) is EXCLUDED from the corpus, and one later window replaces it. On that
route `<S1>` and `<S2>` are the windows the corpus is built from, and `<WX>` is
the excluded window's `SESSION_ID`, which the command must DECLARE with
`--battery-confounded-session-id` rather than name as a registration session:

```zsh
cd "$MEASUREMENT_ROOT"
"$PY" scripts/issue_calibration_acceptance_generation.py check \
  --preregistration configs/calibration/preregistration_d079_epoch_25g83_rev1.md \
  --preregistration-sha256 "$PREREGISTRATION_SHA256" \
  --session-ids "<S1>" --session-ids "<S2>" \
  --battery-confounded-session-id "<WX>"
echo "rc=$?"
```

The dry run then says "yes" exactly when `prepare-candidate` with the same
declaration issues; add the same `--battery-confounded-session-id "<WX>"` to
§4.2's command.

Carry `--preregistration` here too, and read its appended line (§0.3): it must
still say `match` on the sampler digest. `$PREREGISTRATION_SHA256` is the
digest pinned at night 1's arm (§0.5), the same value §4.2 passes. The dry run's return code is what the
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

**Updated 2026-09-15 — INSTALL-WINDOWS-MULTI-01:** installer refusals and
exit codes are in §1.3; the derived-dead-man generator refusal is below.

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
| `plan overruns the dead-man: t0 + window_max_s + 300 = <completion> is not before the derived deadman_epoch_s = <D>` | Completion is not before `deadman_epoch(plan)` (§1.2); unreachable with the adopted 3600 s grace. | Stop and check plan/code consistency. Keep the strict completion/dead-man check; never hand-edit D or raise the window to bypass a refusal. |
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
| `measurement_root is required` / `measurement_root must be an absolute path` / `measurement_root contains control characters` / `measurement_head must be a full 40-character lowercase SHA-1` | The driver-supplied environment was malformed. | Should be impossible from a valid plan; treat as a driver or plan defect and escalate before re-arming. |
| `night plan id does not match the wrapper` | `NIGHT_PLAN_ID` is not the plan this wrapper was frozen against. | The wrong wrapper was pinned, or a wrapper was reused across nights. Re-emit per night (§1.1b). |
| `measurement_root does not match the wrapper` / `measurement_head does not match the wrapper` | The plan's clone path or head is not the one baked in at arm time. | The plan was edited after emission, or the wrong clone was named. Re-cut, re-author, re-emit. |
| `checkout HEAD cannot be read` / `checkout HEAD does not equal measurement_head` | The clone is gone, is not a repository, or moved off H. | Stand down. Re-cut the clone at H (§0.2) and re-verify §0.8. |
| `measurement venv Python is missing or not executable` | `<CLONE>/.venv/bin/python` is absent. | The clone was renamed or its venv never built; renaming moves editable-install absolute paths (§0.2). |
| `frozen calibration plan is missing` / `identity epoch json is missing` / `t1 bindings json is missing` | A desk-produced input is not in the night root under the exact path the wrapper pinned. | Produce it before arming (§0.8). An underscore-spelled `identity_epoch.json` is a different file and reads as missing. |
| `frozen plan is not valid JSON` / `frozen plan has no plan_id` | The frozen calibration plan is corrupt. | Re-freeze at the desk; do not hand-edit. |
| `frozen plan id does not equal the arm-time literal` / `frozen plan bytes do not equal the arm-time digest` | The plan file in the night root is not the one the wrapper was generated from — a swapped or re-written file. | Stop and account for the change. Then re-emit and re-`--verify`; never edit the wrapper. |
| `identity epoch bytes do not equal the arm-time digest` / `t1 bindings bytes do not equal the arm-time digest` | One of the two files whose CONTENTS are copied into every slot record changed after emission — a `--force` re-run of the §0.8 writer is the ordinary cause. | Account for it, re-derive both (§0.8), re-emit, re-`--verify`. |
| `tracked derivation chain bytes do not match the arm-time digest` | The capturing chain inside the clone is not the reviewed bytes — an uncommitted edit, or a clone at the wrong head. | Stand down the night. This is the tripwire §0.8's clean-tree check exists to keep from ever firing at `t0`. |
| exit 1 with **no** `FAIL` line, on a `:?required` guard | The tracked chain ran without the wrapper's environment — i.e. the plan pinned the tracked chain directly instead of the emitted wrapper. | Re-author the plan per §1.1: `chain_path` is `<NIGHT_ROOT>/chain.zsh`. No window time was spent. |

Chain exits (`scripts/night_chains/calibration_derivation_only.zsh`):

| Signal | Meaning | Operator action |
|---|---|---|
| exit 64 | A knob (`SLOT_COUNT`, `SETTLE_S`, `SLOT_CADENCE_S`, `SLOT_CAPTURE_BUDGET_S`, `WINDOW_END_EPOCH_S`) was not a non-negative integer string, or failed the positivity check — which covers `SLOT_CAPTURE_BUDGET_S` as well as `SLOT_COUNT`, `SLOT_CADENCE_S` and `SETTLE_S`. Refused before the settle, the reservation and any operator-log write. | The environment or plan is malformed. No window time was spent and no partial night exists. Fix at the desk; author a fresh plan for a later night. **Why the budget is in the positivity guard:** at `SLOT_CAPTURE_BUDGET_S=0` the window test `slot_start + budget > WINDOW_END_EPOCH_S` becomes vacuous, so a slot could start one second before the agent-free window ends and capture straight past it. |
| exit 66 `derivation_chain_input_missing: <path>` | One of `PLAN`, `IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `CALIBRATION_LEDGER`, `LEDGER_HEAD_PIN` was absent. | The clone is incomplete or a path in the plan is wrong. Re-verify §0.2 and §0.4 before authoring the next night. |
| exit 1 | **Ambiguous — read `chain.stderr.log` to disambiguate.** With a `FAIL <reason>` line it is a wrapper refusal (table above). Without one it is the tracked chain's own `:?required` guard, meaning the chain ran without the wrapper's environment. | Both are pre-window failures costing no window time. Resolve per the matching row above before re-arming. |
| Reservation enforcing preflight exits 2 | **Enforcing** means the decision is made while the reservation holds the writer lease (exclusive permission to change ledger state). `--pre-reserve-strict` refuses before retry, recovery or append, including interrupted claims. The check consumes up to the custody budget of window time. Only enforcing under-lease predicates can produce `ready_to_arm`; success also emits a `pre_reserve_readiness` diagnostic line. | `calibration_ledger_custody_timeout` stops with `night_stopped_preserved`, leaving ledger/session state unchanged; report the budget and elapsed time. `calibration_ledger_recovery_required` requires desk recovery. Other readiness refusals preserve their named cause. Do not retry or repair inside the window. |
| Verify-only probe receipt | **Verify-only** performs access checks and stops before append, settle or capture. Its `outcome: ok` is non-authorizing arm-admission evidence; it is never a `ready_to_arm` result. | Install requires matching input and interpreter fingerprints and fresh receipt timestamps. A refused probe does not authorize capture, recovery or retry. |
| Evidence verify-only probe receipt | Verifies the sealed manifest, harness, tracked chain-source and ruled registration bindings. It never starts `collect`, `load` or power sampling. Its `outcome: ok` is non-authorizing; it is never `ready_to_arm`. | Install rechecks every digest at the pinned measurement commit, both interpreter identities, the single matching `VERIFY_ONLY_OK manifest=<sha>` line and the same fresh timestamps as the calibration probe. A calibration receipt cannot stand in for this evidence receipt. |
| `slot_end slot=dNN disposition=non-valid`, night continues | **Not a failure.** The writer exited 1: the row is finalized with a disposition other than `valid`, and the next declared slot runs on the unchanged cadence (§2.4). | Record the count of such slots. Do nothing else, and read no value. Exclusion is decided at issuance, by named mechanism. |
| `slot_refused slot=dNN rc=2` + chain exits 2, session left OPEN | The writer REFUSED this capture (`emit_refusal` exits 2). The row is **not** finalized, so the chain stops rather than continuing over an unrecorded slot — and deliberately does not abort the session. | Read the refusal in `chain.stderr.log`, then **desk recovery**: `recover_calibration_ledger.py … abort-session --session-id <id> --plan <plan> --reason <the named reason>` (§2.4). Never a retry inside the window. Until the session is closed the next night cannot open at head-equals-pin. |
| `slot_refused slot=dNN rc=<n≥3>` + chain exits with that status, session left OPEN | The writer crashed rather than refusing. Same dispatch branch, same unfinalized row. | Same desk recovery, and account for the crash before any further night is armed: a crash is a defect, not an outcome. |
| `slot_unused … reason=window_exhausted` + `session_abort` + exit 0 | The window could not finish a slot's 480 s budget. Slots are recorded unused, never compressed or retried. Δ larger than 1320 s is the usual cause (§1.2). | Record the count. The session is terminal and §2.5 judges its finalized rows (an equivalence night with fewer than six retained values is INCONCLUSIVE). No top-up, no fourth night (§2.4). |
| Any other non-zero exit, with a `session_open` line already in the chain log | A ledger call failed under `set -e` after the session was opened. | Treat exactly as `slot_refused`: read the log, then desk recovery with a named reason. A `session_open` line with no `session_abort` and no terminal slot means the session is still open, whatever the exit code was. |

Capture-writer refusals (`scripts/validate_powermetrics_fiducial.py`, codes in
`joulewise/calibration_exits.py` as `RefusalCode.DERIVATION_*`):

| Refusal code | Meaning | Operator action |
|---|---|---|
| `calibration_derivation_only_epoch_unchanged` | `--derivation-only` was used while the live identity epoch is one the active acceptance already judges (its own, or a continued epoch). Derivation-only exists only when no acceptance judges the current epoch. | **Stop.** Either the OS reverted, the wrong acceptance was read, or a continuation already covers this machine. Re-run §0.3; do not force the flag. This is the same condition §0.8's desk-inputs writer refuses on at the desk. |
| `calibration_derivation_only_session_kind_required` | `--derivation-only` without a declared `derivation`-kind session slot. | The reservation did not open a derivation session, or the slot name is not in its declared list. Fix the reservation; never capture outside the registration. |
| `calibration_derivation_session_requires_derivation_only` | A `derivation`-kind session slot was captured WITHOUT `--derivation-only` — the mid-night flag-loss case the guard exists for. | The chain's writer invocation lost the flag. Stop the night's remaining slots at the desk; the session is recoverable, the mixed evidence is not. |
| `writer_bracket_arguments` | `--session-id`, `--slot` and `--attempt-id` are all-or-none; a partial triple refuses. | Fix the invocation; three values or none. |
| `quiet_mac_auth_required` / `power_policy_required` | `--allow-live` absent, or `--power-policy` not given. | The chain passes `--allow-live` and `ac_high_power`; a refusal here means the invocation was not the chain's. |

Issuer return codes (`scripts/issue_calibration_acceptance_generation.py`):

| Command | rc | Meaning | Operator action |
|---|---|---|---|
| `check` (no `--session-ids`) | 3 | Identity mismatch and/or an acceptance/ledger error. | **Expected throughout this lane** (§0.3). Read the table; confirm the mismatched fields are `os_build` and `powermetrics_sha256` and no others. |
| `check` (no `--session-ids`) | 0 | No mismatch, no error. | **Unexpected — stop.** The machine now matches the old epoch; the lane's premise is gone. Escalate before capturing. |
| `check --session-ids …` | 0 | The registration passes every desk-mirrored issuer check (ledger, terminality, battery gate, confounded declaration and bound, A-7, prior-set rows). `prepare-candidate` may still refuse on the registration-shape and value rules it alone checks (§4.2 table). | Proceed to §4.2 — on the FAIL route, and expected only after night 3 is terminal. |
| `check --session-ids …` | 5 | Inadmissible; each blocker is printed. | Expected after nights 1 and 2. Clear the named blocker at the desk; never capture more to clear it. |
| `prepare-candidate` | 3 | `REFUSED: <reason>` and nothing written — a non-terminal session, absent `--d125-ruling`, corpus below the minimum, a pending/unresolved prior-set row, a valid same-epoch observation outside the registration, a member whose stored bytes disagree with its ledger row, a failed quantile proof, `S >= C`, or two or more retained members over the level screen. | Read the reason literally. Several of these are science stops requiring Ed's written ruling (§4.2), not defects to fix. |
| `prepare-candidate` | 3 | The arm-gate fences of §4.2, same `REFUSED:` shape: `pre-registration sha256 … does not match the pinned …; not issued`; `registration names <n> sessions, not the pre-registered 3`; `session <id> declared <n> slots, not the pre-registered 12`; `registration os_build … is not the pre-registered …; the registration is void`; `registration powermetrics sha256 … is not the pre-registered …; the registration is void`; `predecessor maximum plus range … does not equal the ruled diagnostic …`. | None of these is fixed by re-running with different flags. The first three are answered by naming the correct file and sessions, or by a written-ruling escape that already exists (§4.2) — never by inventing one. The two `void` refusals mean the campaign was captured on a machine the registration does not describe: stop, and take it to Ed in writing. |
| `prepare-candidate` | 0 | One candidate file written, `candidate_not_issued: true`. | It licenses nothing. Go to §4.3. |

The complete A172 routing partition for `NIGHT_GATE_REASON_CODES` and
`NIGHT_DRIVER_REASON_CODES` is rendered in §1.4a, together with the installer
refusals. Every receipt refusal stays cold; the table does not certify each
refusal's scientific remedy. `[UNVERIFIED: each refusal's exact operator remedy.]`

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

**Timing-source update — 2026-09-15, INSTALL-WINDOWS-MULTI-01.** The timing
rows cite the adopted design and the implementation that must be included in
the reviewed arm head; verify these symbols after code/docs integration.
Other sources are in the merged tree at `main`, read read-only with
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
| The three durations reconciled — programmed span 7680 s (128 min), generator minimum 7980 s (133 min), armed `window_max_s` 9000 s (150 min) | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, §"Why three nights of twelve slots"; its old install-span comparison is historical, superseded for installation by §1.3 |
| Display state at `t0` is unconstrained by the night gate, recorded as a known condition and not a rule | same file, §"Known conditions (recorded, not rules)" |
| Plan spans discovered from sibling plans or installed night plists, starting at `t0 − 8 min`; the stand-down ladder −8/−6/−5, 15-minute watchdog liveness, email-then-arm with Ed's NO overriding, and measurement-checkout install rule | `docs/process/MAGISTRATE_WATCHDOG.md`, §"Fence and deadlines" and §"Install handoff"; `installed_agent_fence` in `scripts/magistrate_watchdog.py` |
| The handback's role, the courier's reading order, the campaign/chain process checks | `docs/process/NIGHT_HANDBACK.md`, its opening sections |
| v2 plan required keys, `night_plan_overruns_deadman`, `registration_path`, the 36-hour authoring age | `joulewise/night_gate.py`: `_PLAN_KEYS`, `NightPlan.from_mapping`, `NIGHT_GATE_REASON_CODES`, `NIGHT_DRIVER_REASON_CODES`, `PLAN_MAX_AGE_S` |
| Generation-time parsing of the two JSON inputs (six exact `IDENTITY_EPOCH_FIELDS`, scalar non-empty values, `power_policy == ac_high_power`; T1 bindings parsed as an object only), `MAX_DECLARED_SESSION_SLOTS = 99` as a desk-time ceiling, and the `CHAIN_ANCHORS` anchor-text discipline | `scripts/gen_derivation_night.py`: `_validated_identity_epoch`, `_validated_json_object`, `CHAIN_POWER_POLICY`, `CHAIN_ANCHORS`, and the slot-count and window checks in `build_spec`; `MAX_DECLARED_SESSION_SLOTS` from `joulewise/calibration_ledger.py` |
| The wrapper mechanism, the thirteen + six exports, the three emitted files, the five-step arm order, the six required emit flags and their defaults, `--verify` rc 0 / rc 3, every generation-time refusal text, the 300 s pre-settle allowance, the 7680 s programmed span for twelve slots, the census substrings | `scripts/gen_derivation_night.py` (module docstring and the symbols `programmed_span_s`, `_census_clean`, `_validated_ruling`, `deadman_epoch` (imported from `scripts/run_night.py`), `build_spec`, `render_wrapper`, `emit`, `verify`, `build_parser`, `main`) and the `derivation-night-wrapper` generated region of `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` |
| The desk-inputs writer: its flags and defaults, its paste-line output format, every refusal in §0.8's table, the canonical hyphenated filenames, and the rule that it must run under the project venv interpreter | `scripts/write_derivation_night_inputs.py` (module docstring, `_derive_planned_vectors`, `_refuse_incomplete_vector`, `_stale_identity_fields`, `_resolved_out_dir`, `_refuse_overwrite`, `write_night_inputs`, `_build_parser`, `main`), whose names `IDENTITY_EPOCH_NAME` and `T1_BINDINGS_NAME` come from `scripts/generate_g2a_probe_inputs.py`; seat record 135, including its live desk smoke and its MLX finding |
| Why the G2-a producer cannot serve a derivation night (it authenticates the acceptance epoch that is stale), and that the desk-inputs writer is the answer | record 134 |
| The live `check` output in §0.3 — two mismatched fields, `mlx_version 0.31.2` matching, rc 3, and the appended `match` line on the pre-registered sampler digest | record 134, run from a fresh clone at the desk |
| Δ ≤ 1320 s for `d12` to be admitted at `window_max_s = 9000`; the three components of Δ | the chain's admission test read against the wrapper's pinned knobs; corroborated by the execution refuter's independent derivation (record 104 §7, "the night tolerates up to 1320 s of launch delay") and named as a runbook defect by the seam finding N-3 |
| The §1.4 installer uses `--plan --python "$PY"` for both labels, derives calendar fields from the plan, and removes jobs with `--uninstall`; publication and recovery retain the same `os.replace` / preserve / `cmp` sequence | `scripts/install_night_agent.sh`; `scripts/run_night.py` schedule command; record 12, `docs/process_traces/2026-09-10-activation-96bfeca7/12-arm-runbook-68-g2a-20260912.md`, for the historical publication/recovery sequence |
| Step 3b and §1.4 arm-time census: workload-positive idle-session exception and publication blocking for `REHEARSAL_STUB` only; other classes receive diagnostics; plan-span census unchanged | `joulewise/arm_census.py` (`classify_arm_census`, `main`); D-180 clause 3; `joulewise/night_gate.py` (`agent_census`) |
| Sibling discovery = `/Users/edr/night-custody/*/night_plan.json`, one level, that filename; installed plists independently fence their `--plan` references. The installer requires `<custody_root>/night_plan.json`; the driver reads only its required `--plan` path | `glob_plans` and `installed_agent_fence` in `scripts/magistrate_watchdog.py`; `check_schedule` in `scripts/install_night_agent.sh`; the `--plan` argument of `scripts/run_night.py` |
| The plan is an INPUT to the generator, and the wrapper's bytes depend on the plan's CONTENT not its path | `scripts/gen_derivation_night.py`: `--plan`'s help text ("frozen v2 night plan JSON (emit mode)"), and `build_spec`, which renders every wrapper literal from the decoded plan fields |
| The wrapper's `WINDOW_CUSTODY_ROOT` is `plan.custody_root`, its `RUNS_ROOT` defaults to `<custody_root>/runs`, its `CALIBRATION_LEDGER` and `LEDGER_HEAD_PIN` to the clone's ledger and head pin — the derivations §2.0 uses | `scripts/gen_derivation_night.py`: `WrapperSpec`, `build_spec`, and the `--runs-root` / `--ledger` / `--head-pin` defaults in `build_parser` |
| The frozen checkout triple is exactly `(plan_id, root, head)`, rendered by the watchdog into the relaunch prompt, and fences those checkouts against movement | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md`, the `@@FENCED_CHECKOUTS@@` line and the line after it; `docs/process/MAGISTRATE_WATCHDOG.md`, §"Complete write inventory" |
| A fence prevents new magistrate launches during a plan span; a discovered active span permits supervision adoption to DRAIN an owned session (`STANDDOWN_<phase>`, `adopt=True`). An installed-only fence has `adopt=False`; the night agents run during the span | `docs/process/MAGISTRATE_WATCHDOG.md`, §"Safety model and state machine" and §"Fence and deadlines" |
| The frozen calibration plan is a committed pack-relative `calibration_plan.json`, not a custody reservation plan | `docs/phase_2/window_runbook.md`, the ALPHA `window.env` example and its `FROZEN_PLAN` gloss |
| `[DD]` is the registration's authoring day | `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`, §"Fields filled at commit" |
| The clone's environment must equal `env/mac-measurement-lock.txt` | record 12, §"Block A", its closing `pip freeze` diff |
| Install close `t0 − 480 − 120`, whole-day shipped `INSTALL_SPANS`, and dead-man `60 × ceil((t0 + window_max_s + 300 + 3600) / 60)` | D-180 clause 1 and D-181 clause 1; INSTALL-WINDOWS-MULTI-01 adopted design record 06; `scripts/run_night.py`: `install_close_epoch`, `INSTALL_CLOSE_MARGIN_S`, `INSTALL_SPANS`, `deadman_epoch`, `DEADMAN_GRACE_S` |
| The supersession banner shape and the "read the newest activation records" instruction | record 13 |
| Epoch↔local conversions and strict maximum in §1.2 | §1.2 arithmetic, converted with `datetime.fromtimestamp(epoch, ZoneInfo("America/Los_Angeles"))`; the example applies the current design to earlier coordinates |
| Driver hands the chain seven variables and no argv — `NIGHT_PLAN_ID`, `JOULEWISE_NIGHT_PLAN_ID`, `NIGHT_DIR`, `MEASUREMENT_ROOT`, `MEASUREMENT_HEAD`, `PY`, `CUSTODY_BUDGET_S` (`_chain_environment` in `scripts/run_night.py`, pinned by the environment and argv assertions in `tests/test_run_night.py`); the gate binds the clone by `HEAD` only (the clone-head condition in `joulewise/night_gate.py`); the reservation copies the identity-epoch and T1-bindings CONTENTS verbatim into every slot record (`main` in `scripts/reserve_calibration_window_bracket.py`) | scout record 101 §0–§2 and the contract-lens refuter record 105 §2, §5 |
| Clean tree and desk-input provenance as arm-checklist items, and "one wrapper per night" | seat record 103 §7.1–§7.4 and its fix-round items B-1, B-2, S-1, S-4; refuter record 105 §5 |
| Whole-suite replay green at the merged head, and the merge itself | records 130 and 133 |
| The epoch-equivalence rule itself — the `m < 6` INCONCLUSIVE branch, the PASS and FAIL definitions, the continuation route and its addendum contents, the FAIL route's affirmation of V3, and the blindness clarification | The owner's directive issue 316 of 2026-09-10, transcribed as revision 2 of `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` and as the dated Ed addendum under D-102 in `docs/decision_log.md` |
| The reference-envelope constants `0.032898493715362`, `0.009724`, `0.010164834757777545` and n = 17, their raw counterparts `0.03289849371536248` and `0.00972358928879385`, and the fact that this generation's screen rule carries no floor | `joulewise/calibration_bracketing.py`: `_D102_N17_DERIVATION` (its `operatives`, `corpus_n` and `screen_rule`), bound to the acceptance id by `_D102_GENERATION_DERIVATIONS` and checked in `_valid_acceptance_bound`; the same lexemes in `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` under `decimal_derivation.ratified_operatives`, `decimal_derivation.rounding` and `decimal_derivation.source_statistics` |

**Updated 2026-09-15 — INSTALL-WINDOWS-MULTI-01:** §1.3 replaces the
unverified last-start cutoff with the derived install close. Still unverified
is each night-gate refusal's exact remedy (§5); §1.4a now enumerates routing.
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

**Timing rows updated 2026-09-15 — INSTALL-WINDOWS-MULTI-01.**

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
| stale field | §Terms, used §0.8 | An identity field whose value on this machine differs from every epoch the active acceptance judges (its own, and any an authenticated continuation carried it onto); at least one must be stale for a derivation night to be the right night. |
| head pin / head-equals-pin | §Terms | The committed file naming the trusted receipt count and last digest; equality with the physical ledger head. |
| screen / level screen / bracket screen | §Terms, constants in §2.5, successor operatives in §4.2 | A threshold a value is compared against; corpus maximum; corpus range. |
| ceiling (budget ceiling) | §Terms, §4.2 | The largest drift a generation will ever budget for; the bracket screen must be strictly below it. |
| blind / blindness | §Terms, bounded §2.3 | Every rule that could be chosen after seeing values is fixed in writing BEFORE the data exists — "every rule fixed before data", not "no one may look". Nothing is read while a night runs; the equivalence night's retained values are read once its own session is terminal, and on the FAIL route no corpus statistic is computed before the last registration session is terminal. |
| driver preflight | §Terms, §1.4 | The install-time check of the driver module, its module-scope project imports and the plan under the job's interpreter and PATH; it does not exercise lazy imports inside project functions or the chain's input checks. |
| dead-man | §Terms, §1.2–§1.3 | Daily job at the local hour/minute of completion plus 3600 s rounded up to a minute; pre-completion stand-down and post-`courier.sent` skip preserve existing recovery checks. |
| fence (watchdog sense) | §Terms, §1.3 | A discovered or installed plan's span prevents new magistrate launches. A discovered active span permits supervision adoption to DRAIN an owned session; an installed-only fence has `adopt=False`. Completion, courier delivery and chain records govern its end. |
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
| `DIAGNOSTIC_NO_PACK` | §0.6, §1.1 | The receipt class for a real night with no measurement pack; only C2 is not-applicable. |
| `REHEARSAL_STUB` | §0.6 | The receipt class running the driver's harmless built-in substitute chain, with no physics or evidence collection. |
| `TRANSACTION_PACK` | §0.6 | The receipt class for a real night bound to a measurement pack. |
| wrapper | §Terms, built §1.1a | The generated zsh file, one per night, that carries the night's whole environment as literal `export` lines, authenticates its pinned inputs, and then `exec`s the tracked chain. The plan's `chain_path` names it. |
| night root | §Terms, exported §0.2 | `<NIGHT_ROOT>`, the custody directory the plan calls `custody_root`; the three emitted files and the night's two desk inputs live in it. |
| tracked chain | §Terms | `scripts/night_chains/calibration_derivation_only.zsh`, the committed script that runs the twelve captures — identical in every clone at `H`, unlike the per-night wrapper. |
| capture writer | §0.8 | `scripts/validate_powermetrics_fiducial.py`, run twelve times by the chain during the night. Distinguished from the desk-inputs writer everywhere in this file; a bare "writer" survives only inside a tool's own quoted message, where it means this one. |
| `<NIGHT_DATE>` / `WINDOW_ID` | §0.2 | The real eight-digit `YYYYMMDD` date of `t0`, plus one unique attempt/window identifier; together they determine the clone, plan, session and custody names. |
| staging path / `$STAGED_PLAN` | §0.2, §1.1b step 2 | `/Users/edr/night-plan-staging/<PLAN_ID>/night_plan.json`, where the plan is authored, generated from and `--verify`-ed. Outside the watchdog's discovery glob, so authoring a plan arms nothing. |
| published (plan) | §1.4 | The one instant a night becomes discoverable: `os.replace` of the staged bytes into `<NIGHT_ROOT>/night_plan.json`, a target that must not pre-exist. Everything before it is undone by doing nothing. |
| sidecar | §1.1a | A small companion file holding another file's SHA-256 in `shasum` output form — the digest, two spaces, a name. |
| advisory (of the third emitted file) | §1.1a | Written for a human's hand-check only; nothing reads it at launch, so deleting or rewriting it changes nothing about what the night will accept. |
| anchor text | §1.1a | One exact line of the chain, quoted in full as a citation instead of a line number, and resolved against the chain's current bytes by a test. |
| tripwire | §1.1b step 4 | A check that writes nothing and exists only to fail loudly if an input drifted — here, `--verify` re-deriving the wrapper and comparing it byte-for-byte. |
| `zsh -n` | §1.1b step 5 | A syntax check: zsh parses the file and runs none of it. |
| census substring | §1.1b, §5 | The three strings the night's own 30 s process census matches; the generator refuses to bake any of them into an emitted literal. |
| programmed span | §1.2 | Chain start to the end of the last slot's capture budget: settle + (slots − 1) × cadence + one budget = 7680 s for twelve slots. |
| pre-settle allowance | §1.2 | 300 s INSIDE the window and BEFORE the settle — the chain's input preflight, strict bounded readiness inside reservation and the session reservation, plus the driver's pre-launch work. The generator refuses a window below programmed span + this. |
| start-to-start cadence | §1.2 | Slot `d(k+1)` starts 600 s after `dk` STARTED; a long capture is never caught up by compressing a later slot. |
| window_max_s / `WINDOW_END_EPOCH_S` | §1.2 | The plan's window length in seconds, and the exclusive window end the chain enforces. |
| courier / courier deadline / courier allowance | §1.2, §2.1 | The process that emails the night's result; the 300 s the deadline arithmetic reserves for it AFTER the window ends. Distinct from the pre-settle allowance, which is spent inside the window; the two share a number by coincidence. |
| install span / install close | §1.3 | Recurring local interval in `INSTALL_SPANS`; the separate per-plan exclusive cutoff `install_close_epoch(plan) = t0 − 10 min`. Installation also requires a sent notice. |
| completion / D | §Terms, §1.2 | Completion is `t0 + window_max_s + 300`; D is `deadman_epoch(plan)`, completion plus 3600 s rounded up to a minute. |
| Δ (delta) | §1.2 | The elapsed time from the plan's `t0` to the moment the chain's settle begins: driver gate work + chain preflight + session reservation. `d12` is admitted only while Δ ≤ 1320 s. |
| plan span / exit boundary | §0.6, §1.3 | The interval from `t0 − 8 min` in which no agent may be resident; the activation's hard exit time. |
| census | §0.6 | An inventory of running processes; the night gate uses the unfiltered `pgrep -lf codex\|claude\|t3` result. |
| arm / arm-time census | §0.6 | Publishing a plan and installing its night/report jobs; the separate process check immediately before that publication. |
| own / foreign | §0.6 | Own PIDs are the census caller and its ancestors reached through current PPID links; other processes are foreign unless the stub-only idle-session exception applies. No saved lock or guessed owner PID selects own. |
| PID / PPID / process tree | §0.6 | A process's numeric identifier / its parent's identifier / all children and later descendants reached through those parent links. |
| interactive session | §0.6 | A Claude executable named `claude` meeting the watchdog's interactive-role rules, or a Node process whose script operand ends in `/t3-code/dist/cli.js`. |
| idle / busy (arm only) | §0.6 | No descendant matches the ruled workload table / at least one does; unknown helpers and unreadable observations count as idle. Neither low CPU usage nor a fixture filename decides this classification. |
| exit code (arm census) | §0.6 | The command's integer result: 0 clear or diagnostic-only; 3 busy/foreign stub blocking publication; 2 invalid plan or invocation; 1 the census did not run — preserve the transcript; not a busy verdict. |
| plan digest | §0.6 | The SHA-256 identifying the exact plan bytes read by the command. |
| frozen checkout triple | §1.5 | Exactly `(plan_id, root, head)` — the three fields the watchdog renders into the relaunch prompt's `@@FENCED_CHECKOUTS@@` list. It fences those checkouts against movement; §2.0 reconstructs every further harvest coordinate from it. |
| terminal (session) | §2.2 | The session's last declared slot is final, or the session was aborted. |
| dispatch (writer-status) | §2.4 | The chain branching on the capture's EXACT status number rather than on "non-zero": 0 valid and 1 non-valid both finalize the row and continue the night; 2 or more is a refusal or crash that stops it with the session open. |
| desk recovery | §2.4 | Closing an open session with `recover_calibration_ledger.py … abort-session --reason <named>`, run by the operator at the desk after the night is over — never inside the window and never as a re-arm. |
| `window_exhausted` | §2.4 | The abort reason recorded when the window cannot finish a slot's capture budget. |
| refusal code / `session-refusal` | §2.4 | The machine-readable name (`RefusalCode`) a tool prints instead of a prose reason; `session-refusal` prints an aborted session's stored one. |
| prior set / corpus / retained n | §Terms | Every ledger observation through the cutoff; the subset whose values are computed from; the corpus size. |
| written-ruling escape | §4.2 | A flag that permits departure from one pre-registered number, and only by naming the written ruling that authorised it, so the departure is recorded in the artifact: `--nights-ruling`, `--slot-count-ruling`, `--allow-slot-count`, `--ed-ruling`. |
| Q99 / two-draw prediction | §4.2 | `t(0.995, n−1) × sample SD × √2`: how far apart two fresh draws fall at that confidence. |
| screen challenge | §4.2 | The pre-registered halt: two or more retained members over `0.032898493715362` means not issued, Ed rules in writing. |
| candidate / `candidate_not_issued` | §4.2 | The one file `prepare-candidate` writes, which the production loader refuses; it licenses nothing. |
| quantile proof | §4.3 | The recorded evidence that the Student-t quantile for the realized degrees of freedom was computed correctly two independent ways. |
| known condition | §4.3 | A recorded fact about how the corpus was captured that is deliberately not a rule — it edits no membership, moves no threshold, and licenses no re-capture. |
| cold science gate | §4.3 | A fresh adjudicating seat with no campaign context, ruling on a mechanically assembled packet. |
| D-138 transaction | §4.4 | The single reviewed commit that swaps the live acceptance and every pin naming it. |
